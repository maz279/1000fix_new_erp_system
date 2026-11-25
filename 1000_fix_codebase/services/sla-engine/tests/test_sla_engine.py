"""
Unit tests for SLA Engine (services/sla-engine)
Tests:
  - Policy initialization and validation constraints
  - Deadline calculation
  - On-track state
  - Near-breach warning at >= 80% threshold and Tier 1 escalation
  - Breach detection and Tier 2 / Tier 3 escalation firing
  - Clock pause and resume functionality
  - Resolved order state
"""

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sla_engine import (
    EscalationTier,
    SlaClock,
    SlaEngine,
    SlaPolicy,
    SlaPriority,
    SlaState,
)


@pytest.fixture
def standard_policy():
    return SlaPolicy(
        code="SLA-NORM",
        name="Standard Repair Policy",
        service_type="walk_in",
        priority=SlaPriority.NORMAL,
        response_hours=2.0,
        resolution_hours=24.0,
        escalation_template="NT-020",
    )


@pytest.fixture
def urgent_policy():
    return SlaPolicy(
        code="SLA-URG",
        name="Urgent Repair Policy",
        service_type="walk_in",
        priority=SlaPriority.URGENT,
        response_hours=0.5,
        resolution_hours=4.0,
        escalation_template="NT-020",
    )


def test_policy_validation():
    """Verify constraint checks on policy targets."""
    with pytest.raises(ValueError, match="positive business hours"):
        SlaPolicy(
            code="ERR",
            name="Err",
            service_type="walk_in",
            priority=SlaPriority.NORMAL,
            response_hours=0,
            resolution_hours=5,
        )

    with pytest.raises(ValueError, match="Response target cannot exceed resolution target"):
        SlaPolicy(
            code="ERR2",
            name="Err2",
            service_type="walk_in",
            priority=SlaPriority.NORMAL,
            response_hours=10,
            resolution_hours=5,
        )


def test_on_track_evaluation(standard_policy):
    """Verify clock is ON_TRACK when time consumed is low (< 80%)."""
    start = datetime(2026, 10, 16, 9, 0, tzinfo=UTC)
    clock = SlaClock(service_order_ref="SO-001", policy=standard_policy, created_at=start)

    # 4 hours elapsed out of 24h (16.7%)
    current = start + timedelta(hours=4)
    res = SlaEngine.evaluate(clock, current_time=current)

    assert res["state"] == SlaState.ON_TRACK.value
    assert res["is_breached"] is False
    assert res["escalation_tier"] == EscalationTier.NONE.value
    assert res["consumed_pct"] == 16.7


def test_near_breach_threshold(standard_policy):
    """Verify NEAR_BREACH state and Tier 1 warning when >= 80% consumed."""
    start = datetime(2026, 10, 16, 9, 0, tzinfo=UTC)
    clock = SlaClock(service_order_ref="SO-002", policy=standard_policy, created_at=start)

    # 20 hours elapsed out of 24h (83.3%)
    current = start + timedelta(hours=20)
    res = SlaEngine.evaluate(clock, current_time=current)

    assert res["state"] == SlaState.NEAR_BREACH.value
    assert res["is_breached"] is False
    assert res["escalation_tier"] == EscalationTier.TIER_1_WARNING.value
    assert res["escalation_template"] == "NT-020"
    assert res["consumed_pct"] == 83.3


def test_breach_detection_and_escalation(urgent_policy):
    """Verify BREACHED state and escalation tier firing (Tier 2 and Tier 3)."""
    start = datetime(2026, 10, 16, 9, 0, tzinfo=UTC)
    clock = SlaClock(service_order_ref="SO-003", policy=urgent_policy, created_at=start)

    # 4.5 hours elapsed out of 4h (30 mins overdue -> Tier 2 Supervisor alert)
    current = start + timedelta(hours=4.5)
    res1 = SlaEngine.evaluate(clock, current_time=current)
    assert res1["state"] == SlaState.BREACHED.value
    assert res1["is_breached"] is True
    assert res1["escalation_tier"] == EscalationTier.TIER_2_SUPERVISOR.value

    # 7.0 hours elapsed out of 4h (3 hours overdue -> Tier 3 Operations escalation)
    current_late = start + timedelta(hours=7.0)
    res2 = SlaEngine.evaluate(clock, current_time=current_late)
    assert res2["state"] == SlaState.BREACHED.value
    assert res2["is_breached"] is True
    assert res2["escalation_tier"] == EscalationTier.TIER_3_OPERATIONS.value


def test_clock_pause_behavior(standard_policy):
    """Verify pausing the clock stops time consumption."""
    start = datetime(2026, 10, 16, 9, 0, tzinfo=UTC)
    clock = SlaClock(service_order_ref="SO-004", policy=standard_policy, created_at=start)

    # Pause after 2 hours
    clock.pause(when=start + timedelta(hours=2))
    assert clock.is_paused is True

    # Check state while paused
    res = SlaEngine.evaluate(clock, current_time=start + timedelta(hours=10))
    assert res["state"] == SlaState.PAUSED.value
    assert res["is_breached"] is False

    # Resume at hour 6 (paused for 4 hours)
    clock.resume(when=start + timedelta(hours=6))
    assert clock.total_paused_seconds == 4 * 3600.0

    # At hour 10, actual elapsed is 10 - 4 = 6 hours (25% consumed)
    res2 = SlaEngine.evaluate(clock, current_time=start + timedelta(hours=10))
    assert res2["state"] == SlaState.ON_TRACK.value
    assert res2["consumed_pct"] == 25.0


def test_resolved_order(standard_policy):
    """Verify resolved orders transition to RESOLVED state."""
    start = datetime(2026, 10, 16, 9, 0, tzinfo=UTC)
    clock = SlaClock(service_order_ref="SO-005", policy=standard_policy, created_at=start)
    clock.record_resolution(when=start + timedelta(hours=12))

    res = SlaEngine.evaluate(clock, current_time=start + timedelta(hours=30))
    assert res["state"] == SlaState.RESOLVED.value
    assert res["is_breached"] is False
    assert res["escalation_tier"] == EscalationTier.NONE.value
