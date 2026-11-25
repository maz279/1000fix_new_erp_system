"""Behavioural tests for the dual-write coordinator (libs/py/fix_events/dual_write.py).

Covers the payload digest, the Redis stream stand-in, dual publishing (stream /
topic routing, hash propagation, stats and latency averages), failure
propagation, and the parity audit (count, multiset and per-key FIFO checks).
"""

from __future__ import annotations

import datetime
import hashlib
import json

import pytest

from libs.py.fix_events import dual_write
from libs.py.fix_events.dual_write import (
    DualWriteEventBus,
    MockRedisStreamStore,
    get_dual_bus,
    get_redis_store,
    payload_digest,
)

# --------------------------------------------------------------------------- digest


def test_payload_digest_is_sha256_of_canonical_json():
    payload = {"b": 2, "a": 1}
    expected = hashlib.sha256(b'{"a": 1, "b": 2}').hexdigest()
    assert payload_digest(payload) == expected
    assert payload_digest({"a": 1, "b": 2}) == expected  # key order irrelevant


def test_payload_digest_stringifies_non_json_values():
    when = datetime.date(2026, 10, 18)
    assert payload_digest({"d": when}) == payload_digest({"d": "2026-10-18"})


# --------------------------------------------------------------------------- redis store


def test_xadd_creates_the_stream_and_assigns_unique_ordered_ids(clock):
    store = MockRedisStreamStore()
    fields = {"k": "v"}
    first = store.xadd("fix:events:party", fields)
    second = store.xadd("fix:events:party", {"k": "w"})
    ms = int(clock.now * 1000)
    assert (first, second) == (f"{ms}-0", f"{ms}-1")
    fields["k"] = "mutated"  # stored fields are a copy
    msgs = store.get_messages("fix:events:party")
    assert [m["fields"]["k"] for m in msgs] == ["v", "w"]
    assert [m["id"] for m in msgs] == [first, second]
    assert msgs[0]["timestamp"] == clock.now


def test_streams_are_independent_and_unknown_streams_are_empty():
    store = MockRedisStreamStore()
    store.xadd("fix:events:a", {})
    assert store.xadd("fix:events:b", {}).endswith("-0")
    assert store.get_messages("fix:events:missing") == []


def test_get_redis_store_returns_the_process_wide_store(redis):
    assert get_redis_store() is redis


# --------------------------------------------------------------------------- publish_dual


def test_bus_binds_the_global_kafka_client_and_redis_store(kafka, redis):
    bus = DualWriteEventBus()
    assert bus.kafka_client is kafka
    assert bus.redis_store is redis
    assert bus.stats == {
        "dual_write_total": 0,
        "redis_success": 0,
        "kafka_success": 0,
        "parity_mismatches": 0,
        "avg_redis_latency_ms": 0.0,
        "avg_kafka_latency_ms": 0.0,
    }


def test_publish_dual_writes_the_same_event_to_redis_and_kafka(kafka, redis, clock):
    bus = DualWriteEventBus()
    meta = {"correlation_id": "corr-9", "causation_id": "c-1"}
    payload = {"order": "SO-1", "amount": 1500}

    res = bus.publish_dual("service_order.created", "fix.service.order", 7, payload, meta)

    digest = payload_digest(payload)
    [msg] = redis.get_messages("fix:events:service_order")
    event_id = msg["fields"]["event_id"]
    assert event_id.startswith("evt-")
    assert msg["fields"] == {
        "event_id": event_id,
        "event_type": "service_order.created",
        "aggregate": "fix.service.order",
        "aggregate_id": "7",
        "payload": json.dumps(payload, sort_keys=True),
        "payload_sha256": digest,
        "correlation_id": "corr-9",
        "causation_id": "c-1",
        "emitted_at": "2026-10-14T17:46:40Z",  # the frozen clock, in UTC
    }
    [rec] = kafka.get_topic_records("fix.events.service_order")
    assert rec.key == "fix.service.order:7"
    assert rec.value["payload"] == payload
    assert rec.headers["redis_msg_id"] == msg["id"]
    assert rec.headers["payload_sha256"] == digest
    assert rec.headers["causation_id"] == "c-1"
    # Regression (DI-05): both copies carry ONE event_id, the consumers' dedup key.
    assert rec.value["event_id"] == event_id
    assert res == {
        "event_id": event_id,
        "event_type": "service_order.created",
        "redis_stream": "fix:events:service_order",
        "redis_msg_id": msg["id"],
        "kafka_topic": "fix.events.service_order",
        "kafka_partition": rec.partition,
        "kafka_offset": rec.offset,
        "payload_sha256": digest,
    }
    # Caller metadata is not mutated by the Kafka header enrichment.
    assert meta == {"correlation_id": "corr-9", "causation_id": "c-1"}


def test_publish_dual_without_metadata_leaves_the_causal_ids_empty(kafka, redis):
    DualWriteEventBus().publish_dual("party.created", "res.partner", 1, {})
    fields = redis.get_messages("fix:events:party")[0]["fields"]
    assert (fields["correlation_id"], fields["causation_id"]) == ("", "")


def test_publish_dual_tracks_counts_and_running_latency_averages(kafka, redis, clock):
    bus = DualWriteEventBus()
    # perf_counter() is read 4x per publish: redis start/end, kafka start/end.
    clock.script_perf_counter([0.0, 0.002, 0.002, 0.006, 1.0, 1.004, 1.004, 1.010])
    bus.publish_dual("party.created", "res.partner", 1, {"n": 1})
    assert bus.stats["avg_redis_latency_ms"] == pytest.approx(2.0)
    assert bus.stats["avg_kafka_latency_ms"] == pytest.approx(4.0)
    bus.publish_dual("party.created", "res.partner", 1, {"n": 2})
    assert bus.stats["dual_write_total"] == 2
    assert bus.stats["redis_success"] == 2
    assert bus.stats["kafka_success"] == 2
    assert bus.stats["avg_redis_latency_ms"] == pytest.approx(3.0)
    assert bus.stats["avg_kafka_latency_ms"] == pytest.approx(5.0)


def test_kafka_failure_propagates_and_the_parity_audit_exposes_it(kafka, redis, monkeypatch):
    bus = DualWriteEventBus()

    def broker_down(**_kwargs):
        raise ConnectionError("kafka unavailable")

    monkeypatch.setattr(kafka, "produce", broker_down)
    with pytest.raises(ConnectionError, match="kafka unavailable"):
        bus.publish_dual("party.created", "res.partner", 1, {"n": 1})

    # Not swallowed, not counted as a success; the Redis leg already landed.
    assert bus.stats["dual_write_total"] == 0
    assert bus.stats["kafka_success"] == 0
    assert len(redis.get_messages("fix:events:party")) == 1
    report = bus.verify_parity("party.created")
    assert report["parity_match"] is False
    assert report["discrepancies"] == 1


# --------------------------------------------------------------------------- verify_parity


def test_parity_holds_for_dual_written_events_across_many_keys(kafka, redis, clock):
    bus = DualWriteEventBus()
    for i in range(12):
        clock.advance(0.001)
        bus.publish_dual("stock.consumed", "fix.stock", i % 4, {"seq": i})
    assert bus.verify_parity("stock.anything") == {
        "stream_key": "fix:events:stock",
        "kafka_topic": "fix.events.stock",
        "redis_count": 12,
        "kafka_count": 12,
        "parity_match": True,
        "key_ordering_match": True,
        "discrepancies": 0,
    }


def test_parity_of_an_empty_family_is_trivially_true(kafka, redis):
    report = DualWriteEventBus().verify_parity("ncr.raised")
    assert (report["redis_count"], report["kafka_count"], report["parity_match"]) == (0, 0, True)


def test_parity_counts_events_missing_from_one_side(kafka, redis):
    bus = DualWriteEventBus()
    bus.publish_dual("party.created", "res.partner", 1, {"n": 1})
    kafka.produce("party.created", "res.partner", 2, {"n": 2}, {"payload_sha256": "x"})
    kafka.produce("party.created", "res.partner", 3, {"n": 3}, {"payload_sha256": "y"})
    report = bus.verify_parity("party.created")
    assert report["parity_match"] is False
    assert report["key_ordering_match"] is True  # every Redis key matches in Kafka
    assert report["discrepancies"] == 2


def _redis_event(store, aggregate, aggregate_id, digest):
    store.xadd(
        "fix:events:payment",
        {"aggregate": aggregate, "aggregate_id": str(aggregate_id), "payload_sha256": digest},
    )


def test_parity_flags_payload_hash_divergence_with_equal_counts(kafka, redis):
    bus = DualWriteEventBus()
    _redis_event(redis, "fix.settlement", 1, "h-redis")
    kafka.produce("payment.settled", "fix.settlement", 1, {}, {"payload_sha256": "h-kafka"})
    report = bus.verify_parity("payment.settled")
    assert (report["redis_count"], report["kafka_count"]) == (1, 1)
    assert report["parity_match"] is False
    assert report["key_ordering_match"] is False
    assert report["discrepancies"] == 1


def test_parity_flags_per_key_reordering_even_when_the_multisets_match(kafka, redis, clock):
    bus = DualWriteEventBus()
    _redis_event(redis, "fix.settlement", 1, "h1")
    _redis_event(redis, "fix.settlement", 1, "h2")
    kafka.produce("payment.settled", "fix.settlement", 1, {}, {"payload_sha256": "h2"})
    clock.advance(1)
    kafka.produce("payment.settled", "fix.settlement", 1, {}, {"payload_sha256": "h1"})
    report = bus.verify_parity("payment.settled")
    assert report["parity_match"] is False
    assert report["key_ordering_match"] is False
    assert report["discrepancies"] == 1


# --------------------------------------------------------------------------- singleton


def test_get_dual_bus_builds_once_and_then_reuses(no_singletons, kafka, redis):
    bus = get_dual_bus()
    assert isinstance(bus, DualWriteEventBus)
    assert get_dual_bus() is bus
    assert bus.kafka_client is kafka
    assert dual_write._global_dual_bus is bus


def test_publish_dual_keeps_a_caller_supplied_event_id_on_both_buses(kafka, redis):
    """Regression: the Redis copy had no event_id, so Redis-path consumers could not dedup."""
    res = DualWriteEventBus().publish_dual(
        "employee.left", "hr.employee", 4, {"employee_id": 4}, {"event_id": "evt-fixed"}
    )
    [msg] = redis.get_messages("fix:events:employee")
    [rec] = kafka.get_topic_records("fix.events.employee")
    assert res["event_id"] == msg["fields"]["event_id"] == rec.value["event_id"] == "evt-fixed"
