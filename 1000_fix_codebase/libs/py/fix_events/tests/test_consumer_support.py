"""Consumer-side support: self-registering consumer groups and one event shape per bus."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from libs.py.fix_events import (
    CANONICAL_CONSUMER_GROUPS,
    ConsumerBusState,
    ConsumerGroupMigrationManager,
    DualWriteEventBus,
    normalize_bus_event,
)

# --------------------------------------------------------------------------- register_group


def test_a_new_consumer_group_registers_on_redis_and_consumes(kafka, redis):
    mgr = ConsumerGroupMigrationManager(kafka_client=kafka, redis_store=redis)
    assert "identity-lifecycle" not in CANONICAL_CONSUMER_GROUPS
    with pytest.raises(KeyError):
        mgr.get_group_state("identity-lifecycle")

    assert mgr.register_group("identity-lifecycle") == ConsumerBusState.BUS_REDIS
    DualWriteEventBus().publish_dual("employee.left", "hr.employee", 9, {"employee_id": 9})
    seen: list[dict] = []
    assert mgr.consume_event("identity-lifecycle", "fix.events.employee", seen.append) == 1
    assert json.loads(seen[0]["payload"]) == {"employee_id": 9}
    # the canonical cut-over plan is untouched
    assert len(CANONICAL_CONSUMER_GROUPS) == 6


def test_re_registering_never_resets_state_or_cursors(kafka, redis):
    mgr = ConsumerGroupMigrationManager(kafka_client=kafka, redis_store=redis)
    mgr.register_group("identity-lifecycle")
    DualWriteEventBus().publish_dual("employee.left", "hr.employee", 1, {})
    mgr.consume_event("identity-lifecycle", "fix.events.employee", lambda e: None)
    mgr.transition_group("identity-lifecycle", ConsumerBusState.BUS_DUAL, "cut-over")

    assert mgr.register_group("identity-lifecycle") == ConsumerBusState.BUS_DUAL
    group = mgr._groups["identity-lifecycle"]
    assert group["redis_cursors"] == {"fix:events:employee": 1}
    assert group["processed_count"] == 1
    assert mgr.register_group("notification-dispatcher") == ConsumerBusState.BUS_REDIS


# --------------------------------------------------------------------------- normalize_bus_event


def test_redis_and_kafka_copies_normalise_to_the_same_event(kafka, redis):
    meta = {"correlation_id": "corr-1", "causation_id": "evt-cause"}
    DualWriteEventBus().publish_dual("employee.left", "hr.employee", 42, {"a": 1}, meta)
    [msg] = redis.get_messages("fix:events:employee")
    [rec] = kafka.get_topic_records("fix.events.employee")

    from_redis = normalize_bus_event(msg["fields"])
    from_kafka = normalize_bus_event(rec.value)
    assert from_redis == from_kafka
    assert from_redis == {
        "event_id": rec.value["event_id"],
        "event_type": "employee.left",
        "aggregate": "hr.employee",
        "correlation_id": "corr-1",
        "causation_id": "evt-cause",
        "aggregate_id": 42,
        "payload": {"a": 1},
    }


@pytest.mark.parametrize(
    ("raw", "expected_payload", "expected_aggregate_id"),
    [
        ({"payload": "", "aggregate_id": ""}, {}, None),
        ({"payload": {"x": 1}}, {"x": 1}, None),
        ({"payload": "{}", "aggregate_id": "not-a-number"}, {}, None),
        ({"payload": "{}", "aggregate_id": ["7"]}, {}, None),
        ({"payload": "{}", "aggregate_id": 0}, {}, 0),
    ],
)
def test_normalisation_tolerates_absent_and_odd_fields(
    raw, expected_payload, expected_aggregate_id
):
    event = normalize_bus_event(raw)
    assert event["payload"] == expected_payload
    assert event["aggregate_id"] == expected_aggregate_id
    assert event["event_id"] is None and event["causation_id"] is None


@pytest.mark.parametrize(
    ("payload", "match"),
    [
        ("{not json", "not JSON"),
        ("[1, 2]", "JSON object"),
        (None, "JSON object"),
        (5, "JSON object"),
    ],
)
def test_normalisation_rejects_payloads_that_are_not_objects(payload, match):
    with pytest.raises(ValueError, match=match):
        normalize_bus_event({"payload": payload})
