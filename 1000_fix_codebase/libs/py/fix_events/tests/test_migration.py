"""Behavioural tests for consumer-group migration (libs/py/fix_events/migration.py).

Covers the per-group state machine, rollback (and its blast-radius isolation),
state-routed consumption (Redis cursor, Kafka offsets, BUS_DUAL shadow compare),
lag-triggered auto-revert and the summary.
"""

from __future__ import annotations

import logging

import pytest

from libs.py.fix_events import migration
from libs.py.fix_events.dual_write import DualWriteEventBus
from libs.py.fix_events.migration import (
    CANONICAL_CONSUMER_GROUPS,
    ConsumerBusState,
    ConsumerGroupMigrationManager,
    get_migration_manager,
)

REDIS = ConsumerBusState.BUS_REDIS
DUAL = ConsumerBusState.BUS_DUAL
KAFKA = ConsumerBusState.BUS_KAFKA
GROUP = "audit-logger"
TOPIC = "fix.events.party"


@pytest.fixture
def mgr(kafka, redis) -> ConsumerGroupMigrationManager:
    return ConsumerGroupMigrationManager(kafka_client=kafka, redis_store=redis)


def _redis_events(redis, n, start=0):
    for i in range(start, start + n):
        redis.xadd("fix:events:party", {"seq": i})


# --------------------------------------------------------------------------- construction


def test_all_six_canonical_groups_start_on_redis_with_clean_counters(mgr, clock):
    assert len(CANONICAL_CONSUMER_GROUPS) == 6
    assert set(mgr._groups) == set(CANONICAL_CONSUMER_GROUPS)
    for group in CANONICAL_CONSUMER_GROUPS:
        assert mgr.get_group_state(group) is REDIS
        g = mgr._groups[group]
        assert g["rollback_count"] == g["processed_count"] == 0
        assert g["shadow_match_count"] == g["shadow_mismatch_count"] == 0
        assert g["history"] == []
        assert g["redis_cursors"] == {}
    assert mgr.max_lag_threshold == 500


def test_manager_defaults_to_the_process_wide_bus_clients(kafka, redis):
    default = ConsumerGroupMigrationManager(max_lag_threshold=10)
    assert default.kafka_client is kafka
    assert default.redis_store is redis
    assert default.max_lag_threshold == 10


@pytest.mark.parametrize(
    "call",
    [
        lambda m: m.get_group_state("ghost"),
        lambda m: m.transition_group("ghost", KAFKA),
        lambda m: m.rollback_group("ghost", "x"),
        lambda m: m.consume_event("ghost", TOPIC, print),
    ],
)
def test_unknown_groups_are_rejected(mgr, call):
    with pytest.raises(KeyError, match="Unknown consumer group: ghost"):
        call(mgr)


# --------------------------------------------------------------------------- transitions


def test_transition_records_history_and_logs(mgr, caplog, clock):
    with caplog.at_level(logging.INFO, logger=migration.logger.name):
        res = mgr.transition_group(GROUP, DUAL, reason="shadow start")
    assert res["group_id"] == GROUP
    assert (res["previous_state"], res["current_state"], res["status"]) == (
        "BUS_REDIS",
        "BUS_DUAL",
        "SUCCESS",
    )
    assert res["transition_time_ms"] >= 0
    [entry] = mgr._groups[GROUP]["history"]
    assert entry["reason"] == "shadow start"
    assert entry["timestamp_utc"] == mgr._groups[GROUP]["last_transition_utc"]
    assert f"Consumer group {GROUP} transitioned BUS_REDIS -> BUS_DUAL" in caplog.text


def test_transition_without_reason_gets_a_default_reason(mgr):
    mgr.transition_group(GROUP, KAFKA)
    assert mgr._groups[GROUP]["history"][-1]["reason"] == "Cutover to BUS_KAFKA"


def test_rollback_reverts_one_group_only_within_the_sla(mgr, caplog):
    for group in CANONICAL_CONSUMER_GROUPS:
        mgr.transition_group(group, KAFKA)
    with caplog.at_level(logging.WARNING, logger=migration.logger.name):
        res = mgr.rollback_group("inventory-syncer", "error spike")
    assert res["status"] == "ROLLED_BACK"
    assert (res["previous_state"], res["current_state"]) == ("BUS_KAFKA", "BUS_REDIS")
    assert res["sla_5s_met"] is True
    assert res["reason"] == "error spike"
    assert mgr._groups["inventory-syncer"]["rollback_count"] == 1
    assert mgr._groups["inventory-syncer"]["history"][-1]["reason"] == "ROLLBACK: error spike"
    assert "ROLLBACK triggered for consumer group inventory-syncer" in caplog.text
    # Blast radius: every other group is still on Kafka.
    others = [g for g in CANONICAL_CONSUMER_GROUPS if g != "inventory-syncer"]
    assert all(mgr.get_group_state(g) is KAFKA for g in others)


# --------------------------------------------------------------------------- BUS_REDIS


def test_regression_redis_consumption_resumes_from_a_per_group_cursor(mgr, redis):
    """Regression: BUS_REDIS used to process ``msgs[-limit:]`` on every poll.

    That re-processed the same tail each time and silently skipped every
    message older than the last ``limit`` ones.
    """
    _redis_events(redis, 5)
    seen = []
    assert mgr.consume_event(GROUP, TOPIC, lambda f: seen.append(f["seq"]), limit=3) == 3
    assert mgr.consume_event(GROUP, TOPIC, lambda f: seen.append(f["seq"]), limit=3) == 2
    assert mgr.consume_event(GROUP, TOPIC, lambda f: seen.append(f["seq"]), limit=3) == 0
    assert seen == [0, 1, 2, 3, 4]
    _redis_events(redis, 1, start=5)
    assert mgr.consume_event(GROUP, TOPIC, lambda f: seen.append(f["seq"])) == 1
    assert seen[-1] == 5
    assert mgr._groups[GROUP]["processed_count"] == 6
    assert mgr._groups[GROUP]["redis_cursors"] == {"fix:events:party": 6}


def test_redis_cursors_are_independent_per_group(mgr, redis):
    _redis_events(redis, 3)
    assert mgr.consume_event("audit-logger", TOPIC, lambda f: None) == 3
    assert mgr.consume_event("bi-streaming", TOPIC, lambda f: None) == 3


def test_redis_handler_failure_propagates_and_the_message_is_retried(mgr, redis):
    _redis_events(redis, 3)
    seen = []

    def flaky(fields):
        if fields["seq"] == 1:
            raise RuntimeError("handler down")
        seen.append(fields["seq"])

    with pytest.raises(RuntimeError, match="handler down"):
        mgr.consume_event(GROUP, TOPIC, flaky)
    assert mgr._groups[GROUP]["redis_cursors"]["fix:events:party"] == 1
    assert mgr._groups[GROUP]["processed_count"] == 1
    assert mgr.consume_event(GROUP, TOPIC, lambda f: seen.append(f["seq"])) == 2
    assert seen == [0, 1, 2]


# --------------------------------------------------------------------------- BUS_KAFKA


def test_kafka_state_consumes_with_committed_group_offsets(mgr, kafka):
    for i in range(4):
        kafka.produce("party.created", "res.partner", i, {"seq": i})
    mgr.transition_group(GROUP, KAFKA)
    seen = []
    assert mgr.consume_event(GROUP, TOPIC, lambda e: seen.append(e["payload"]["seq"])) == 4
    assert mgr.consume_event(GROUP, TOPIC, seen.append) == 0
    assert sorted(seen) == [0, 1, 2, 3]
    g = mgr._groups[GROUP]
    assert g["processed_count"] == 4
    assert g["shadow_match_count"] == g["shadow_mismatch_count"] == 0


def test_rollback_after_kafka_resumes_redis_from_the_groups_own_cursor(mgr, kafka, redis):
    bus = DualWriteEventBus()
    for i in range(3):
        bus.publish_dual("party.created", "res.partner", i, {"seq": i})
    mgr.transition_group(GROUP, KAFKA)
    assert mgr.consume_event(GROUP, TOPIC, lambda e: None) == 3
    mgr.rollback_group(GROUP, "lag")
    # At-least-once: Redis has its own cursor, so already-seen events are
    # redelivered (handlers are idempotent by contract, DI-05) - none is lost.
    assert mgr.consume_event(GROUP, TOPIC, lambda f: None) == 3


# --------------------------------------------------------------------------- BUS_DUAL


def test_dual_state_shadow_matches_dual_written_events(mgr, kafka, redis):
    bus = DualWriteEventBus()
    for i in range(4):
        bus.publish_dual("party.created", "res.partner", i, {"seq": i})
    mgr.transition_group(GROUP, DUAL)
    seen = []
    assert mgr.consume_event(GROUP, TOPIC, lambda e: seen.append(e["payload"]["seq"])) == 4
    g = mgr._groups[GROUP]
    assert sorted(seen) == [0, 1, 2, 3]
    assert (g["processed_count"], g["shadow_match_count"], g["shadow_mismatch_count"]) == (4, 4, 0)


def test_regression_dual_state_reports_events_missing_from_redis(mgr, kafka, redis):
    """Regression: BUS_DUAL counted every processed event as a shadow match.

    No comparison with Redis was made, so a Kafka-only (or divergent) event was
    reported as a match and the cutover gate could never see a mismatch.
    """
    DualWriteEventBus().publish_dual("party.created", "res.partner", 1, {"seq": 1})
    kafka.produce("party.created", "res.partner", 2, {"seq": 2})  # Kafka only
    mgr.transition_group(GROUP, DUAL)
    assert mgr.consume_event(GROUP, TOPIC, lambda e: None) == 2
    g = mgr._groups[GROUP]
    assert (g["shadow_match_count"], g["shadow_mismatch_count"]) == (1, 1)


def test_dual_state_dead_letters_failures_without_shadow_counting_them(mgr, kafka, redis):
    DualWriteEventBus().publish_dual("party.created", "res.partner", 1, {"seq": 1})
    mgr.transition_group(GROUP, DUAL)

    def reject(_event):
        raise ValueError("poison")

    assert mgr.consume_event(GROUP, TOPIC, reject) == 1
    g = mgr._groups[GROUP]
    assert g["processed_count"] == 1
    assert g["shadow_match_count"] == g["shadow_mismatch_count"] == 0
    assert len(kafka._topics["fix.events.party.dlq"][0].records) == 1


# --------------------------------------------------------------------------- health / summary


def test_lag_within_threshold_is_healthy_and_recorded(mgr):
    mgr.transition_group(GROUP, KAFKA)
    assert mgr.check_health_and_auto_revert(GROUP, 500) == {
        "group_id": GROUP,
        "lag": 500,
        "status": "HEALTHY",
    }
    assert mgr._groups[GROUP]["simulated_lag"] == 500
    assert mgr.get_group_state(GROUP) is KAFKA


def test_lag_breach_auto_reverts_a_migrated_group(mgr):
    mgr.transition_group(GROUP, DUAL)
    res = mgr.check_health_and_auto_revert(GROUP, 750)
    assert res["status"] == "ROLLED_BACK"
    assert "Consumer lag (750 msgs) exceeded threshold (500 msgs)" in res["reason"]
    assert mgr.get_group_state(GROUP) is REDIS


def test_lag_breach_on_a_group_already_on_redis_does_not_roll_back_again(mgr):
    res = mgr.check_health_and_auto_revert(GROUP, 10_000)
    assert res["status"] == "HEALTHY"
    assert mgr._groups[GROUP]["rollback_count"] == 0


def test_summary_reports_the_state_distribution(mgr):
    mgr.transition_group("audit-logger", KAFKA)
    mgr.transition_group("bi-streaming", DUAL)
    summary = mgr.get_summary()
    assert summary["total_groups"] == 6
    assert summary["state_distribution"] == {"BUS_REDIS": 4, "BUS_DUAL": 1, "BUS_KAFKA": 1}
    assert summary["groups"]["audit-logger"]["state"] == "BUS_KAFKA"


def test_get_migration_manager_builds_once_and_then_reuses(no_singletons, kafka, redis):
    mgr = get_migration_manager()
    assert isinstance(mgr, ConsumerGroupMigrationManager)
    assert get_migration_manager() is mgr
    assert (mgr.kafka_client, mgr.redis_store) == (kafka, redis)
