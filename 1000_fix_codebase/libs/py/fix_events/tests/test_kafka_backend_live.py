"""Integration tests for the REAL Kafka transport (libs/py/fix_events/kafka_backend.py).

Marked ``integration`` (ci.yml nightly profile): these exercise a live
3-broker cluster — the asset-ml compose profile bound to
127.0.0.1:9092/9094/9095 or ``KAFKA_BOOTSTRAP_SERVERS``. Each run uses a
unique topic/domain and consumer group so repeated runs never clash.

A skip is honest and self-describing: it means the real transport was NOT
verified against a live cluster in this run (brokers unreachable), never that
the behaviour was assumed.
"""

from __future__ import annotations

import uuid

import pytest

from libs.py.fix_events.kafka_backend import KafkaBackend, bootstrap_servers_env
from libs.py.fix_events.kafka_bus import map_topic_for_event
from libs.py.fix_events.replay import DLQ_REPLAY_GROUP, EventReplayEngine

pytestmark = pytest.mark.integration

BOOTSTRAP = bootstrap_servers_env()


def _brokers_reachable(servers: list[str], timeout: float = 1.5) -> tuple[bool, str]:
    import socket

    for server in servers:
        host, _, port = server.partition(":")
        try:
            with socket.create_connection((host, int(port)), timeout=timeout):
                continue
        except OSError as exc:
            return False, f"{server} ({type(exc).__name__})"
    return True, ""


_REACHABLE, _FIRST_FAILURE = _brokers_reachable(BOOTSTRAP)
requires_live_brokers = pytest.mark.skipif(
    not _REACHABLE,
    reason=(
        f"live Kafka brokers unreachable at {BOOTSTRAP} "
        f"(first failure: {_FIRST_FAILURE or 'n/a'}) — the real fix_events "
        "transport was NOT verified in this run; start the asset-ml compose "
        "profile to measure it"
    ),
)


@pytest.fixture
def backend():
    bus = KafkaBackend(bootstrap_servers=BOOTSTRAP, consume_deadline_s=25.0)
    try:
        yield bus
    finally:
        bus.close()  # leave the group / release sockets: no zombie members


@pytest.fixture
def run() -> str:
    return uuid.uuid4().hex[:10]


# --------------------------------------------------------------------- roundtrip


@requires_live_brokers
def test_produce_consume_roundtrip_with_keyed_partitions(backend, run):
    domain = f"it{run}"
    topic = map_topic_for_event(f"{domain}.created")
    produced = [
        backend.produce(
            f"{domain}.created", "it.partner", i % 4, {"seq": i}, {"correlation_id": f"c-{run}"}
        )
        for i in range(12)
    ]

    assert {r.topic for r in produced} == {topic}
    # Same key -> same partition (broker murmur2), FIFO offsets within the key.
    by_key: dict[str, list[int]] = {}
    for rec in produced:
        by_key.setdefault(rec.key, []).append(rec.offset)
    assert len(by_key) == 4
    assert all(len(offsets) == 3 for offsets in by_key.values())
    assert all(offsets == sorted(offsets) for offsets in by_key.values())
    # Envelope semantics are the shared kafka_bus ones.
    first = produced[0].value
    assert first["event_type"] == f"{domain}.created"
    assert first["aggregate"] == "it.partner"
    assert first["payload"] == {"seq": 0}
    assert first["event_id"].startswith("evt-")
    assert first["correlation_id"] == f"c-{run}"
    assert produced[0].headers["source"] == "odoo"

    group = f"it-{run}-roundtrip"
    seen: list[dict] = []
    assert backend.consume(group, topic, seen.append, limit=50) == 12
    assert sorted(e["payload"]["seq"] for e in seen) == list(range(12))
    # Committed: nothing redelivered, only new records flow.
    assert backend.consume(group, topic, seen.append, limit=50) == 0
    backend.produce(f"{domain}.created", "it.partner", 1, {"seq": 99})
    assert backend.consume(group, topic, seen.append, limit=50) == 1
    assert seen[-1]["payload"]["seq"] == 99

    # Replay index: offsets-for-times at 0 maps every partition into the log.
    starts = backend.seek_to_timestamp(topic, 0.0)
    assert starts and all(off >= 0 for off in starts.values())
    scanned = backend.read_topic_from(topic, starts)
    assert [r.value["payload"]["seq"] for r in scanned] == sorted(
        r.value["payload"]["seq"] for r in scanned
    )
    backend.close()


@requires_live_brokers
def test_poison_message_is_dead_lettered_and_redriven_over_live_brokers(backend, run):
    domain = f"dlq{run}"
    topic = map_topic_for_event(f"{domain}.raised")
    dlq = f"{topic}.dlq"
    group = f"it-{run}-dlq"
    for i in range(3):
        backend.produce(f"{domain}.raised", "it.ncr", 7, {"seq": i, "bad": i == 1})

    ok: list[int] = []

    def handler(event: dict) -> None:
        if event["payload"]["bad"]:
            raise ValueError("schema rejected")
        ok.append(event["payload"]["seq"])

    assert backend.consume(group, topic, handler, limit=10) == 3
    assert ok == [0, 2]

    dead = backend.get_topic_records(dlq)
    assert len(dead) == 1
    assert dead[0].headers["dlq_reason"] == "schema rejected"
    assert dead[0].headers["original_topic"] == topic

    # Idempotent DLQ re-drive through the transport-agnostic replay engine.
    engine = EventReplayEngine(backend)
    first = engine.replay_dlq(dlq, topic, remediator=lambda p: {**p, "bad": False})
    assert first["reprocessed_count"] == 1
    assert engine.replay_dlq(dlq, topic)["reprocessed_count"] == 0  # cursor committed
    assert backend.committed_offsets(DLQ_REPLAY_GROUP, dlq) == {
        dead[0].partition: dead[0].offset + 1
    }
    redriven = [
        r for r in backend.get_topic_records(topic) if r.headers.get("reprocessed_from_dlq")
    ]
    assert len(redriven) == 1
    assert redriven[0].value["payload"] == {"seq": 1, "bad": False}
    backend.close()
