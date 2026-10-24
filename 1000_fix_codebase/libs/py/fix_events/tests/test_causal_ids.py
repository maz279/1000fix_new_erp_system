"""Regression: correlation_id / causation_id survive every bus mode (AS-08 traceability).

Before the fix the Kafka envelope - the only thing a handler sees in BUS_KAFKA,
BUS_DUAL (shadow), time-travel replay and DLQ re-drive - carried neither id
(they lived only in record headers), and the Redis stream entry written by the
dual-write path dropped causation_id, so BUS_REDIS handlers lost it.
"""

from __future__ import annotations

import pytest

from libs.py.fix_events.dual_write import DualWriteEventBus
from libs.py.fix_events.migration import ConsumerBusState, ConsumerGroupMigrationManager
from libs.py.fix_events.replay import EventReplayEngine

CORR = "corr-req-77"
CAUSE = "evt-parent-01"
IDS = {"correlation_id": CORR, "causation_id": CAUSE}
TOPIC = "fix.events.party"
GROUP = "audit-logger"


def _ids(mapping):
    return {k: mapping.get(k) for k in IDS}


@pytest.fixture
def dual(kafka, redis):
    bus = DualWriteEventBus()
    bus.publish_dual("party.created", "res.partner", 5, {"name": "A"}, dict(IDS))
    return bus


@pytest.fixture
def mgr(kafka, redis):
    return ConsumerGroupMigrationManager(kafka_client=kafka, redis_store=redis)


def test_dual_write_carries_both_ids_on_redis_kafka_headers_and_envelope(dual, kafka, redis):
    [msg] = redis.get_messages("fix:events:party")
    [rec] = kafka.get_topic_records(TOPIC)
    assert _ids(msg["fields"]) == IDS
    assert _ids(rec.headers) == IDS
    assert _ids(rec.value) == IDS


def test_kafka_produce_puts_both_ids_in_the_handler_visible_envelope(kafka):
    rec = kafka.produce("party.created", "res.partner", 1, {}, dict(IDS))
    assert _ids(rec.value) == IDS
    bare = kafka.produce("party.created", "res.partner", 1, {})
    assert _ids(bare.value) == {"correlation_id": None, "causation_id": None}


@pytest.mark.parametrize(
    "state",
    [ConsumerBusState.BUS_REDIS, ConsumerBusState.BUS_DUAL, ConsumerBusState.BUS_KAFKA],
)
def test_migration_handlers_see_both_ids_in_every_bus_state(dual, mgr, state):
    if state is not ConsumerBusState.BUS_REDIS:
        mgr.transition_group(GROUP, state)
    seen = []
    assert mgr.consume_event(GROUP, TOPIC, seen.append) == 1
    assert _ids(seen[0]) == IDS
    if state is ConsumerBusState.BUS_DUAL:  # the shadow compare still matches
        assert mgr._groups[GROUP]["shadow_match_count"] == 1


def test_time_travel_replay_delivers_both_ids(dual, kafka):
    seen = []
    EventReplayEngine(kafka).replay_from_timestamp(TOPIC, 0.0, seen.append)
    assert [_ids(e) for e in seen] == [IDS]


def test_dlq_and_redrive_keep_the_original_ids_for_the_same_event(dual, kafka):
    [original] = kafka.get_topic_records(TOPIC)

    def reject(_event):
        raise ValueError("poison")

    kafka.consume("evat-reporter", TOPIC, reject)
    [dead] = kafka._topics[f"{TOPIC}.dlq"][0].records
    assert _ids(dead.headers) == IDS
    assert _ids(dead.value) == IDS

    EventReplayEngine(kafka).replay_dlq(f"{TOPIC}.dlq", TOPIC)
    [redriven] = [
        r for r in kafka.get_topic_records(TOPIC) if r.headers.get("reprocessed_from_dlq")
    ]
    # Same event (event_id kept for consumer dedup) => its causal ids are unchanged.
    assert redriven.value["event_id"] == original.value["event_id"]
    assert _ids(redriven.headers) == IDS
    assert _ids(redriven.value) == IDS
    seen = []
    kafka.consume("bi-streaming", TOPIC, seen.append)
    assert [_ids(e) for e in seen] == [IDS, IDS]
