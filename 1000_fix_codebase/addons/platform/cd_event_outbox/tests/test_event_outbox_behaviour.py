# Behavioural tests for fix.event.outbox (AS-08 transactional outbox) on the
# live ORM (`odoo_env`, rolled back after every test).
import contextlib
import hashlib
import json
import uuid

import pytest
from odoo.exceptions import ValidationError


@contextlib.contextmanager
def _rejects(env, exc, match):
    """pytest.raises inside a savepoint: an expected failure never leaves a
    half-applied write in the shared test transaction."""
    with pytest.raises(exc, match=match) as info, env.cr.savepoint():
        yield info


AGG = "test.outbox.aggregate"


def _emit(env, event_type="outbox.tested", payload=None, metadata=None, aggregate_id=7):
    return env["fix.event.outbox"].emit(
        event_type, AGG, aggregate_id, payload if payload is not None else {"k": 1}, metadata
    )


@pytest.mark.parametrize("bad_type", ["", None, "nodots"])
def test_emit_rejects_non_dot_notation_event_types(odoo_env, bad_type):
    with _rejects(odoo_env, ValidationError, match="dot-notation"):
        _emit(odoo_env, event_type=bad_type)


def test_emit_writes_pending_row_with_sorted_payload_and_hash(odoo_env):
    rec = _emit(odoo_env, payload={"b": 2, "a": 1}, aggregate_id=42)

    expected_payload = json.dumps({"a": 1, "b": 2}, sort_keys=True)
    assert rec.status == "pending"
    assert rec.bus_target == "dual"
    assert rec.aggregate == AGG and rec.aggregate_id == 42
    assert rec.payload == expected_payload
    assert rec.payload_sha256 == hashlib.sha256(expected_payload.encode()).hexdigest()
    uuid.UUID(rec.event_id)  # a real UUID - the idempotency key (DI-05)


def test_emit_metadata_carries_supplied_correlation_and_causation(odoo_env):
    rec = _emit(odoo_env, metadata={"correlation_id": "corr-1", "causation_id": "cause-9"})
    meta = json.loads(rec.metadata_json)
    assert meta["correlation_id"] == "corr-1"
    assert meta["causation_id"] == "cause-9"
    assert meta["source"] == "odoo"
    assert meta["emitted_at"]


def test_emit_generates_correlation_when_metadata_absent_or_partial(odoo_env):
    no_meta = json.loads(_emit(odoo_env).metadata_json)
    uuid.UUID(no_meta["correlation_id"])
    assert no_meta["causation_id"] is None

    partial = json.loads(_emit(odoo_env, metadata={"causation_id": "c-2"}).metadata_json)
    uuid.UUID(partial["correlation_id"])
    assert partial["causation_id"] == "c-2"


def test_drain_pending_returns_only_pending_events_decoded(odoo_env):
    Outbox = odoo_env["fix.event.outbox"]
    first = _emit(odoo_env, payload={"n": 1}, metadata={"correlation_id": "c-first"})
    second = _emit(odoo_env, payload={"n": 2})
    published = _emit(odoo_env, payload={"n": 3})
    published.mark_published()
    # a row written without metadata (legacy) decodes to an empty dict
    bare = Outbox.create(
        {
            "event_type": "outbox.bare",
            "aggregate": AGG,
            "aggregate_id": 1,
            "payload": json.dumps({"n": 4}),
        }
    )

    drained = {d["id"]: d for d in Outbox.drain_pending(limit=100000) if d["aggregate"] == AGG}

    assert set(drained) == {first.id, second.id, bare.id}
    assert drained[first.id]["payload"] == {"n": 1}
    assert drained[first.id]["metadata"]["correlation_id"] == "c-first"
    assert drained[first.id]["event_id"] == first.event_id
    assert drained[first.id]["payload_sha256"] == first.payload_sha256
    assert drained[bare.id]["metadata"] == {}
    assert drained[bare.id]["bus_target"] == "dual"


def test_drain_pending_honours_limit(odoo_env):
    for n in range(3):
        _emit(odoo_env, payload={"n": n})
    assert len(odoo_env["fix.event.outbox"].drain_pending(limit=2)) == 2


def test_mark_published_without_kafka_coordinates(odoo_env):
    rec = _emit(odoo_env)
    rec.mark_published()
    assert rec.status == "published"
    assert rec.published_at
    assert not rec.kafka_published_at
    assert rec.kafka_partition == 0 and rec.kafka_offset == 0


def test_mark_published_records_kafka_partition_and_offset(odoo_env):
    recs = _emit(odoo_env) | _emit(odoo_env)
    recs.mark_published(kafka_partition=3, kafka_offset=1234)
    for rec in recs:
        assert rec.status == "published"
        assert rec.kafka_partition == 3
        assert rec.kafka_offset == 1234
        assert rec.kafka_published_at


def test_mark_published_partition_zero_is_still_recorded(odoo_env):
    rec = _emit(odoo_env)
    rec.mark_published(kafka_partition=0)
    # partition 0 is a real partition (not "absent"): the Kafka timestamp is set
    assert rec.kafka_published_at
    assert rec.kafka_offset == 0


def test_mark_failed_increments_attempts_and_truncates_error(odoo_env):
    rec = _emit(odoo_env)
    rec.mark_failed("x" * 5000)
    assert rec.status == "failed"
    assert rec.publish_attempts == 1
    assert len(rec.last_error) == 2000
    rec.mark_failed("broker down")
    assert rec.publish_attempts == 2
    assert rec.last_error == "broker down"
