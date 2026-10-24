"""Behavioural tests for time-travel replay and DLQ re-drive (libs/py/fix_events/replay.py).

Covers the replay window (epoch / ISO-8601 / naive-UTC), cross-partition
chronological ordering, the max_records ceiling, read-only repeatability, and
the DLQ re-drive contract: idempotent, aggregate-key and event_id preserving,
payload (not envelope) remediation, failure resumption.
"""

from __future__ import annotations

import datetime
import logging

import pytest

from libs.py.fix_events import replay
from libs.py.fix_events.kafka_bus import InMemoryBus
from libs.py.fix_events.replay import DLQ_REPLAY_GROUP, EventReplayEngine, get_replay_engine

TOPIC = "fix.events.vat"
DLQ = "fix.events.vat.dlq"
MIDNIGHT = datetime.datetime(2026, 10, 18, tzinfo=datetime.UTC).timestamp()


def _seed(client, stamps):
    """Append one record per (aggregate_id, timestamp) straight into its keyed partition."""
    client._ensure_topic(TOPIC)
    for agg_id, ts in stamps:
        key = f"fix.vat.register:{agg_id}"
        part = client._topics[TOPIC][client._select_partition(TOPIC, key)]
        part.append(key, {"agg": agg_id, "ts": ts}, {}, timestamp=ts)


@pytest.fixture
def seeded(kafka):
    # Two hours either side of 2026-10-18T00:00:00Z, spread over several keys.
    _seed(kafka, [(i, MIDNIGHT + (i - 4) * 1800) for i in range(9)])
    return kafka


def _collect(engine, ts, **kw):
    got = []
    res = engine.replay_from_timestamp(TOPIC, ts, got.append, **kw)
    return res, [e["ts"] for e in got]


# --------------------------------------------------------------------------- time travel


def test_replay_from_epoch_delivers_the_window_in_chronological_order(seeded, caplog):
    engine = EventReplayEngine(seeded)
    with caplog.at_level(logging.INFO, logger=replay.logger.name):
        res, stamps = _collect(engine, MIDNIGHT)
    assert stamps == [MIDNIGHT + k * 1800 for k in range(5)]
    assert res["replayed_count"] == 5
    assert res["status"] == "COMPLETED"
    assert (res["topic"], res["timestamp"]) == (TOPIC, MIDNIGHT)
    assert res["starting_offsets"] == seeded.seek_to_timestamp(TOPIC, MIDNIGHT)
    assert res["duration_ms"] >= 0
    assert f"Replayed 5 records from topic {TOPIC}" in caplog.text


@pytest.mark.parametrize("iso", ["2026-10-18T00:00:00Z", "2026-10-18T06:00:00+06:00"])
def test_replay_accepts_iso_8601_with_an_offset(seeded, iso):
    _, stamps = _collect(EventReplayEngine(seeded), iso)
    assert stamps[0] == MIDNIGHT
    assert len(stamps) == 5


def test_regression_naive_iso_timestamps_are_utc_not_host_local_time(seeded):
    """Regression: a naive ISO string was parsed as *local* time.

    On a UTC+6 (Dhaka) host the replay window silently started six hours early,
    re-delivering events from before the requested instant.
    """
    engine = EventReplayEngine(seeded)
    _, naive = _collect(engine, "2026-10-18T00:00:00")
    _, explicit = _collect(engine, "2026-10-18T00:00:00Z")
    assert naive == explicit
    assert min(naive) == MIDNIGHT


def test_integer_epoch_is_accepted(seeded):
    res, stamps = _collect(EventReplayEngine(seeded), int(MIDNIGHT) + 3600)
    assert res["replayed_count"] == 3
    assert stamps[0] == MIDNIGHT + 3600


def test_max_records_caps_to_the_earliest_events_across_partitions(seeded):
    res, stamps = _collect(EventReplayEngine(seeded), 0.0, max_records=3)
    assert res["replayed_count"] == 3
    assert stamps == [MIDNIGHT + k * 1800 for k in (-4, -3, -2)]


def test_replay_is_read_only_and_repeatable(seeded):
    engine = EventReplayEngine(seeded)
    first = _collect(engine, MIDNIGHT)[1]
    assert _collect(engine, MIDNIGHT)[1] == first
    assert seeded._consumer_offsets == {}  # no consumer group offsets touched


def test_replay_of_an_unknown_topic_is_empty(kafka):
    res = EventReplayEngine(kafka).replay_from_timestamp("fix.events.none", 0, print)
    assert res["replayed_count"] == 0
    assert res["starting_offsets"] == {0: 0, 1: 0, 2: 0}


class _NoAutoCreateClient(InMemoryBus):
    """A client whose seek, like a real broker, does not auto-create topics."""

    def seek_to_timestamp(self, topic, timestamp_s):
        if topic not in self._topics:
            return {}
        return super().seek_to_timestamp(topic, timestamp_s)


def test_replay_tolerates_clients_that_do_not_auto_create_topics():
    client = _NoAutoCreateClient()
    res = EventReplayEngine(client).replay_from_timestamp("fix.events.none", 0, print)
    assert (res["replayed_count"], res["starting_offsets"]) == (0, {})
    assert "fix.events.none" not in client._topics


def test_replay_handler_errors_propagate(seeded):
    def boom(_event):
        raise RuntimeError("rebuild failed")

    with pytest.raises(RuntimeError, match="rebuild failed"):
        EventReplayEngine(seeded).replay_from_timestamp(TOPIC, MIDNIGHT, boom)


# --------------------------------------------------------------------------- DLQ re-drive


def _poison(client, n=1, aggregate_id=42):
    """Produce n events and dead-letter all of them through a failing consumer."""
    recs = [
        client.produce(
            "vat.mushak_6_3.issued",
            "fix.vat.register",
            aggregate_id,
            {"m51_id": f"VAT-{i}", "malformed": True},
            {"trace": f"t{i}"},
        )
        for i in range(n)
    ]

    def reject(event):
        if event["payload"].get("malformed"):
            raise ValueError("schema rejected")

    client.consume("evat-reporter", TOPIC, reject)
    return recs


def _redriven(client):
    return [r for r in client.get_topic_records(TOPIC) if r.headers.get("reprocessed_from_dlq")]


def test_replay_dlq_without_a_dlq_topic_is_a_no_op(kafka):
    res = EventReplayEngine(kafka).replay_dlq(DLQ, TOPIC)
    assert (res["reprocessed_count"], res["status"]) == (0, "RECOVERED")
    assert (res["dlq_topic"], res["target_topic"]) == (DLQ, TOPIC)
    assert res["duration_ms"] >= 0


def test_regression_redriven_event_keeps_aggregate_key_event_id_and_payload_shape(kafka):
    """Regression: the re-drive lost the event's identity and shape.

    aggregate/aggregate_id were read from the headers (never set there), so every
    re-driven event was keyed ``fix.generic:1`` - one partition, wrong entity,
    broken per-entity ordering; the whole old envelope was nested as the new
    payload; and a fresh event_id defeated consumer dedup for groups that had
    already processed the original.
    """
    [original] = _poison(kafka)
    res = EventReplayEngine(kafka).replay_dlq(DLQ, TOPIC)
    assert res["reprocessed_count"] == 1

    [rec] = _redriven(kafka)
    assert rec.key == "fix.vat.register:42" == original.key
    assert rec.partition == original.partition
    assert rec.value["aggregate"] == "fix.vat.register"
    assert rec.value["aggregate_id"] == 42
    assert rec.value["payload"] == {"m51_id": "VAT-0", "malformed": True}
    assert rec.value["event_id"] == original.value["event_id"]
    assert rec.value["event_type"] == "vat.replayed"
    assert rec.headers["original_event_type"] == "vat.mushak_6_3.issued"
    assert rec.headers["original_dlq_offset"] == "0"
    assert rec.headers["dlq_reason"] == "schema rejected"
    assert rec.headers["trace"] == "t0"


def test_regression_replay_dlq_is_idempotent(kafka):
    """Regression: every call re-drove the whole DLQ from offset 0 (duplicates)."""
    engine = EventReplayEngine(kafka)

    def fix(payload):
        return {**payload, "malformed": False}

    _poison(kafka, n=2)
    assert engine.replay_dlq(DLQ, TOPIC, remediator=fix)["reprocessed_count"] == 2
    assert engine.replay_dlq(DLQ, TOPIC, remediator=fix)["reprocessed_count"] == 0
    assert len(_redriven(kafka)) == 2
    # Only records dead-lettered since the last re-drive go out next time (the
    # consumer accepts the two remediated re-drives and rejects one new poison).
    _poison(kafka, n=1, aggregate_id=7)
    assert engine.replay_dlq(DLQ, TOPIC, remediator=fix)["reprocessed_count"] == 1
    assert kafka._consumer_offsets[DLQ_REPLAY_GROUP][DLQ] == {0: 3}


def test_remediator_fixes_a_copy_of_the_payload(kafka):
    _poison(kafka)
    dlq_value_before = dict(kafka._topics[DLQ][0].records[0].value)
    received = []

    def remediate(payload):
        received.append(dict(payload))
        payload["malformed"] = False
        return payload

    EventReplayEngine(kafka).replay_dlq(DLQ, TOPIC, remediator=remediate)
    assert received == [{"m51_id": "VAT-0", "malformed": True}]
    assert _redriven(kafka)[0].value["payload"] == {"m51_id": "VAT-0", "malformed": False}
    assert kafka._topics[DLQ][0].records[0].value == dlq_value_before


def test_replay_dlq_respects_limit_and_resumes(kafka):
    engine = EventReplayEngine(kafka)
    _poison(kafka, n=3)
    assert engine.replay_dlq(DLQ, TOPIC, limit=2)["reprocessed_count"] == 2
    assert engine.replay_dlq(DLQ, TOPIC, limit=2)["reprocessed_count"] == 1
    assert sorted(r.headers["original_dlq_offset"] for r in _redriven(kafka)) == ["0", "1", "2"]


def test_failing_remediator_propagates_and_the_redrive_resumes_there(kafka):
    engine = EventReplayEngine(kafka)
    _poison(kafka, n=3)

    def strict(payload):
        if payload["m51_id"] == "VAT-1":
            raise ValueError("cannot remediate")
        return payload

    with pytest.raises(ValueError, match="cannot remediate"):
        engine.replay_dlq(DLQ, TOPIC, remediator=strict)
    assert kafka._consumer_offsets[DLQ_REPLAY_GROUP][DLQ] == {0: 1}
    assert engine.replay_dlq(DLQ, TOPIC)["reprocessed_count"] == 2
    assert sorted(r.headers["original_dlq_offset"] for r in _redriven(kafka)) == ["0", "1", "2"]


def test_non_envelope_dlq_records_are_redriven_as_their_own_payload(kafka):
    raw = InMemoryBus().produce("vat.x", "a", 1, {})
    raw.value = {"raw": True}  # e.g. a record dead-lettered by a foreign producer
    raw.headers = {}
    kafka.route_to_dlq(DLQ, raw, "unparseable")
    EventReplayEngine(kafka).replay_dlq(DLQ, TOPIC)
    [rec] = _redriven(kafka)
    assert rec.key == "fix.generic:1"
    assert rec.value["payload"] == {"raw": True}
    assert rec.headers["original_event_type"] == ""
    assert rec.value["event_id"].startswith("evt-")


def test_end_to_end_poison_pill_recovery_with_consumer_dedup(kafka):
    """A remediated re-drive is consumed by the failing group, deduped by others."""
    [original] = _poison(kafka)
    seen_by_audit: set[str] = set()
    audit_effects = []

    def audit(event):  # idempotent consumer (DI-05): dedup by event_id
        if event["event_id"] in seen_by_audit:
            return
        seen_by_audit.add(event["event_id"])
        audit_effects.append(event["payload"]["m51_id"])

    assert kafka.consume("audit-logger", TOPIC, audit) == 1

    def remediate(payload):
        return {**payload, "malformed": False}

    EventReplayEngine(kafka).replay_dlq(DLQ, TOPIC, remediator=remediate)

    vat_effects = []
    assert kafka.consume("evat-reporter", TOPIC, lambda e: vat_effects.append(e)) == 1
    assert vat_effects[0]["payload"]["malformed"] is False
    assert vat_effects[0]["event_id"] == original.value["event_id"]
    assert kafka.consume("audit-logger", TOPIC, audit) == 1
    assert audit_effects == ["VAT-0"]  # the re-drive produced no second effect


# --------------------------------------------------------------------------- singleton


def test_get_replay_engine_builds_once_and_then_reuses(no_singletons, kafka):
    engine = get_replay_engine()
    assert isinstance(engine, EventReplayEngine)
    assert get_replay_engine() is engine
    assert engine.kafka_client is kafka
