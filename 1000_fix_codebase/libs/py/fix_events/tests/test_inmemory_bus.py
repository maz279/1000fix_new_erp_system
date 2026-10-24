"""Behavioural tests for the in-memory transport (libs/py/fix_events/kafka_bus.py).

Covers topic mapping, partition logs (offsets, reads, timestamp index), keyed
partitioning / per-entity ordering, the FixEvent envelope, consumer-group offset
commits, DLQ routing and the at-least-once failure path. This is the in-process
InMemoryBus used by unit tests; the real Kafka transport has its own
integration-marked suite (test_kafka_backend_live.py).
"""

from __future__ import annotations

import hashlib
import logging

import pytest

from libs.py.fix_events import kafka_bus
from libs.py.fix_events.kafka_bus import (
    InMemoryBus,
    KafkaPartitionLog,
    KafkaRecord,
    get_kafka_client,
    map_topic_for_event,
)

# --------------------------------------------------------------------------- topics


@pytest.mark.parametrize(
    ("event_type", "topic"),
    [
        ("service_order.created", "fix.events.service_order"),
        ("vat.mushak_6_3.issued", "fix.events.vat"),
        ("party", "fix.events.party"),
    ],
)
def test_topic_is_derived_from_the_event_type_domain(event_type, topic):
    assert map_topic_for_event(event_type) == topic


# --------------------------------------------------------------------------- records


def test_record_to_dict_round_trips_every_field():
    rec = KafkaRecord("t", 2, 7, "k:1", {"a": 1}, {"h": "v"}, 12.5)
    assert rec.to_dict() == {
        "topic": "t",
        "partition": 2,
        "offset": 7,
        "key": "k:1",
        "value": {"a": 1},
        "headers": {"h": "v"},
        "timestamp": 12.5,
    }


# --------------------------------------------------------------------------- partition log


def test_partition_log_assigns_contiguous_offsets_and_keeps_explicit_timestamps():
    log = KafkaPartitionLog("fix.events.x", 1)
    first = log.append("a:1", {"n": 0}, {}, timestamp=100.0)
    second = log.append("a:1", {"n": 1}, {}, timestamp=50.0)
    assert (first.offset, second.offset) == (0, 1)
    assert (first.topic, first.partition) == ("fix.events.x", 1)
    assert [r.timestamp for r in log.records] == [100.0, 50.0]


def test_partition_log_defaults_the_timestamp_to_the_clock(clock):
    log = KafkaPartitionLog("t", 0)
    assert log.append("k", {}, {}).timestamp == clock.now


@pytest.mark.parametrize(
    ("offset", "limit", "expected"),
    [(0, 100, [0, 1, 2]), (1, 1, [1]), (2, 5, [2]), (3, 5, []), (99, 5, []), (-1, 5, [])],
)
def test_read_from_returns_the_requested_window_and_nothing_out_of_range(offset, limit, expected):
    log = KafkaPartitionLog("t", 0)
    for i in range(3):
        log.append("k", {"n": i}, {}, timestamp=float(i))
    assert [r.offset for r in log.read_from(offset, limit=limit)] == expected


def test_find_offset_by_timestamp_returns_earliest_record_at_or_after_target():
    log = KafkaPartitionLog("t", 0)
    for ts in (10.0, 20.0, 30.0):
        log.append("k", {}, {}, timestamp=ts)
    assert log.find_offset_by_timestamp(5.0) == 0
    assert log.find_offset_by_timestamp(20.0) == 1  # inclusive
    assert log.find_offset_by_timestamp(25.0) == 2
    # Nothing that late yet: the next offset to be written (log end).
    assert log.find_offset_by_timestamp(31.0) == 3


def test_find_offset_by_timestamp_on_an_empty_log_is_offset_zero():
    assert KafkaPartitionLog("t", 0).find_offset_by_timestamp(0.0) == 0


# --------------------------------------------------------------------------- client basics


def test_client_defaults_to_the_three_broker_ha_cluster():
    client = InMemoryBus()
    assert client.bootstrap_servers == ["127.0.0.1:9092", "127.0.0.1:9094", "127.0.0.1:9095"]
    assert client.num_partitions == 3


def test_client_keeps_explicit_bootstrap_servers_and_partition_count():
    client = InMemoryBus(["broker:1"], num_partitions=5)
    assert client.bootstrap_servers == ["broker:1"]
    client._ensure_topic("fix.events.x")
    assert sorted(client._topics["fix.events.x"]) == [0, 1, 2, 3, 4]


def test_ensure_topic_is_idempotent_and_never_truncates_an_existing_topic(kafka):
    rec = kafka.produce("party.created", "res.partner", 1, {})
    kafka._ensure_topic("fix.events.party")
    assert kafka.get_topic_records("fix.events.party") == [rec]


def test_partition_selection_is_a_stable_md5_hash_of_the_key(kafka):
    key = "res.partner:42"
    expected = int(hashlib.md5(key.encode(), usedforsecurity=False).hexdigest(), 16) % 3
    assert kafka._select_partition("any", key) == expected
    assert {kafka._select_partition("other", key) for _ in range(5)} == {expected}


# --------------------------------------------------------------------------- produce


def test_produce_writes_a_fixevent_envelope_to_the_keyed_partition(kafka, clock):
    meta = {"correlation_id": "corr-1", "event_id": "evt-given"}
    rec = kafka.produce("party.created", "res.partner", 42, {"name": "A"}, meta)

    assert rec.topic == "fix.events.party"
    assert rec.key == "res.partner:42"
    assert rec.partition == kafka._select_partition(rec.topic, rec.key)
    assert rec.offset == 0
    assert rec.timestamp == clock.now
    assert rec.value == {
        "event_id": "evt-given",
        "correlation_id": "corr-1",
        "causation_id": None,  # none supplied
        "event_type": "party.created",
        "aggregate": "res.partner",
        "aggregate_id": 42,
        "timestamp": rec.headers["emitted_at"],
        "producer": "1000fix_erp",
        "payload": {"name": "A"},
    }
    assert rec.headers["source"] == "odoo"
    assert rec.headers["producer"] == "fix_events"
    assert rec.headers["content_type"] == "application/json"
    assert rec.headers["correlation_id"] == "corr-1"
    # The caller's metadata dict is copied, never mutated.
    assert meta == {"correlation_id": "corr-1", "event_id": "evt-given"}


def test_produce_lets_caller_metadata_override_default_headers(kafka):
    rec = kafka.produce(
        "party.created", "res.partner", 1, {}, {"source": "portal", "emitted_at": "T0"}
    )
    assert rec.headers["source"] == "portal"
    assert rec.value["timestamp"] == "T0"


def test_produce_keeps_per_entity_order_in_a_single_partition(kafka):
    recs = [kafka.produce("stock.moved", "fix.stock", 7, {"seq": i}) for i in range(5)]
    assert {r.partition for r in recs} == {recs[0].partition}
    assert [r.offset for r in recs] == [0, 1, 2, 3, 4]


def test_regression_event_id_is_unique_even_with_shared_correlation_id(kafka):
    """Regression: event_id used to fall back to the request-wide correlation_id.

    Two different events raised in one request shared an event_id, so the
    consumers' event_id dedup (DI-05) silently dropped the second one.
    """
    a = kafka.produce("party.created", "res.partner", 1, {}, {"correlation_id": "req-1"})
    b = kafka.produce("stock.consumed", "fix.stock", 2, {}, {"correlation_id": "req-1"})
    assert a.value["event_id"] != b.value["event_id"]
    assert "req-1" not in (a.value["event_id"], b.value["event_id"])


def test_regression_event_id_is_unique_within_the_same_millisecond(kafka, clock):
    """Regression: the fallback event_id was ``evt-<epoch ms>`` and collided."""
    ids = {kafka.produce("party.created", "res.partner", i, {}).value["event_id"] for i in range(3)}
    assert len(ids) == 3
    assert all(i.startswith("evt-") for i in ids)


# --------------------------------------------------------------------------- consume


def _fill(client, n):
    """Produce n VAT events spread over 10 aggregates (so over every partition)."""
    return [client.produce("vat.issued", "fix.vat.register", i % 10, {"seq": i}) for i in range(n)]


def test_consume_delivers_every_record_once_and_commits_offsets(kafka):
    _fill(kafka, 12)
    seen = []
    assert kafka.consume("evat-reporter", "fix.events.vat", lambda e: seen.append(e)) == 12
    assert sorted(e["payload"]["seq"] for e in seen) == list(range(12))
    # Committed: a second poll redelivers nothing...
    assert kafka.consume("evat-reporter", "fix.events.vat", seen.append) == 0
    # ...and only new records are delivered afterwards.
    kafka.produce("vat.issued", "fix.vat.register", 1, {"seq": 12})
    assert kafka.consume("evat-reporter", "fix.events.vat", seen.append) == 1
    assert seen[-1]["payload"]["seq"] == 12


def test_consumer_groups_track_offsets_independently(kafka):
    _fill(kafka, 4)
    assert kafka.consume("audit-logger", "fix.events.vat", lambda e: None) == 4
    assert kafka.consume("bi-streaming", "fix.events.vat", lambda e: None) == 4
    offsets = kafka._consumer_offsets
    assert offsets["audit-logger"]["fix.events.vat"] == offsets["bi-streaming"]["fix.events.vat"]


def test_consume_limit_applies_per_partition_and_resumes(kafka):
    client = InMemoryBus(num_partitions=1)
    _fill(client, 5)
    seen = []
    assert client.consume("g", "fix.events.vat", seen.append, limit=2) == 2
    assert client.consume("g", "fix.events.vat", seen.append, limit=2) == 2
    assert client.consume("g", "fix.events.vat", seen.append, limit=2) == 1
    assert [e["payload"]["seq"] for e in seen] == [0, 1, 2, 3, 4]


def test_consume_on_an_unknown_topic_creates_it_and_processes_nothing(kafka):
    assert kafka.consume("g", "fix.events.nothing", lambda e: None) == 0
    assert "fix.events.nothing" in kafka._topics


def test_poison_message_is_dead_lettered_and_does_not_block_the_partition(kafka, caplog):
    client = InMemoryBus(num_partitions=1)
    for i in range(3):
        client.produce("vat.issued", "fix.vat.register", 1, {"seq": i, "bad": i == 1})
    ok = []

    def handler(event):
        if event["payload"]["bad"]:
            raise ValueError("schema rejected")
        ok.append(event["payload"]["seq"])

    with caplog.at_level(logging.ERROR, logger=kafka_bus.logger.name):
        processed = client.consume("evat-reporter", "fix.events.vat", handler)

    assert processed == 3  # the dead-lettered message counts as handled
    assert ok == [0, 2]
    assert client._consumer_offsets["evat-reporter"]["fix.events.vat"] == {0: 3}
    dlq = client._topics["fix.events.vat.dlq"][0].records
    assert len(dlq) == 1
    assert dlq[0].value["payload"]["seq"] == 1
    assert dlq[0].headers["dlq_reason"] == "schema rejected"
    assert dlq[0].headers["original_topic"] == "fix.events.vat"
    assert dlq[0].headers["original_offset"] == "1"
    assert "failed_at_utc" in dlq[0].headers
    assert "consumer error on fix.events.vat[0]:1" in caplog.text


def test_without_dlq_a_failure_propagates_and_the_message_is_redelivered(kafka):
    client = InMemoryBus(num_partitions=1)
    for i in range(3):
        client.produce("vat.issued", "fix.vat.register", 1, {"seq": i})
    seen = []

    def flaky(event):
        if event["payload"]["seq"] == 1:
            raise RuntimeError("downstream unavailable")
        seen.append(event["payload"]["seq"])

    with pytest.raises(RuntimeError, match="downstream unavailable"):
        client.consume("g", "fix.events.vat", flaky, dlq_on_failure=False)
    # Offset committed up to (not past) the failed record; nothing dead-lettered.
    assert client._consumer_offsets["g"]["fix.events.vat"] == {0: 1}
    assert "fix.events.vat.dlq" not in client._topics
    # Retry resumes at the failed record: no loss, no duplicate of seq 0.
    assert client.consume("g", "fix.events.vat", lambda e: seen.append(e["payload"]["seq"])) == 2
    assert seen == [0, 1, 2]


def test_route_to_dlq_truncates_the_reason_and_keeps_the_original_record_intact(kafka):
    rec = kafka.produce("vat.issued", "fix.vat.register", 9, {"x": 1}, {"trace": "t1"})
    original_headers = dict(rec.headers)
    dlq_rec = kafka.route_to_dlq("fix.events.vat.dlq", rec, "E" * 900)
    assert len(dlq_rec.headers["dlq_reason"]) == 500
    assert dlq_rec.headers["trace"] == "t1"
    assert (dlq_rec.key, dlq_rec.value, dlq_rec.partition) == (rec.key, rec.value, 0)
    assert rec.headers == original_headers


# --------------------------------------------------------------------------- seek / read


def test_seek_to_timestamp_maps_every_partition_to_its_first_offset_at_or_after(kafka, clock):
    early = _fill(kafka, 6)
    cut = clock.now + 10
    clock.advance(10)
    late = _fill(kafka, 6)
    offsets = kafka.seek_to_timestamp("fix.events.vat", cut)
    assert sorted(offsets) == [0, 1, 2]
    for p, offset in offsets.items():
        # Every early record of the partition is skipped; the seek lands on the
        # partition's first late record (or its log end if it got none).
        assert offset == len([r for r in early if r.partition == p])
        first_late = [r.offset for r in late if r.partition == p][:1]
        assert first_late in ([offset], [])


def test_seek_past_the_newest_record_returns_log_end_offsets(kafka, clock):
    _fill(kafka, 6)
    ends = {p: len(log.records) for p, log in kafka._topics["fix.events.vat"].items()}
    assert kafka.seek_to_timestamp("fix.events.vat", clock.now + 1) == ends


def test_get_topic_records_merges_partitions_chronologically(kafka, clock):
    produced = []
    for i in range(6):
        clock.advance(1)
        produced.append(kafka.produce("vat.issued", "fix.vat.register", i, {"seq": i}))
    merged = kafka.get_topic_records("fix.events.vat")
    assert [r.value["payload"]["seq"] for r in merged] == list(range(6))
    assert len({r.partition for r in merged}) > 1
    assert kafka.get_topic_records("fix.events.empty") == []


# --------------------------------------------------------------------------- singleton


def test_get_kafka_client_builds_once_and_then_reuses(monkeypatch):
    monkeypatch.setenv(kafka_bus.TRANSPORT_ENV, kafka_bus.TRANSPORT_MEMORY)
    monkeypatch.setattr(kafka_bus, "_global_kafka_client", None)
    first = get_kafka_client()
    assert isinstance(first, InMemoryBus)
    assert get_kafka_client() is first


def test_get_kafka_client_defaults_to_the_real_backend_without_connecting(monkeypatch):
    """Default transport is the real Kafka backend; building it does no I/O."""
    from libs.py.fix_events.kafka_backend import KafkaBackend

    monkeypatch.delenv(kafka_bus.TRANSPORT_ENV, raising=False)
    monkeypatch.setattr(kafka_bus, "_global_kafka_client", None)
    client = get_kafka_client()
    assert isinstance(client, KafkaBackend)
    assert client._producer is None  # lazily connected: nothing was opened
