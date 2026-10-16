"""
services/sla-engine - Milestone R02-M05 Task T01 (G1-04):
Pure-computation SLA Clock Engine and Escalation Dispatcher.
Calculates response deadlines, resolution deadlines, clock pauses,
near-breach warnings (80% threshold), and breach escalation tiers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional, List, Dict, Any


class SlaPriority(str, Enum):
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    EMERGENCY = "emergency"


class SlaState(str, Enum):
    ON_TRACK = "on_track"
    NEAR_BREACH = "near_breach"
    BREACHED = "breached"
    PAUSED = "paused"
    RESOLVED = "resolved"


class EscalationTier(str, Enum):
    NONE = "none"
    TIER_1_WARNING = "tier_1_warning"       # 80% threshold reached -> assigned tech alert
    TIER_2_SUPERVISOR = "tier_2_supervisor" # 100% breach -> branch supervisor alert
    TIER_3_OPERATIONS = "tier_3_operations" # > 2h breach -> operations manager escalation


@dataclass(frozen=True)
class SlaPolicy:
    code: str
    name: str
    service_type: str
    priority: SlaPriority
    response_hours: float
    resolution_hours: float
    escalation_template: str = "NT-020"
    active: bool = True

    def __post_init__(self):
        if self.response_hours <= 0 or self.resolution_hours <= 0:
            raise ValueError("SLA targets must be positive business hours")
        if self.response_hours > self.resolution_hours:
            raise ValueError("Response target cannot exceed resolution target")


@dataclass
class SlaClock:
    service_order_ref: str
    policy: SlaPolicy
    created_at: datetime
    response_at: Optional[datetime] = None
    resolution_at: Optional[datetime] = None
    is_paused: bool = False
    paused_at: Optional[datetime] = None
    total_paused_seconds: float = 0.0

    def pause(self, when: Optional[datetime] = None) -> None:
        if not self.is_paused:
            self.is_paused = True
            self.paused_at = when or datetime.now(timezone.utc)

    def resume(self, when: Optional[datetime] = None) -> None:
        if self.is_paused:
            now = when or datetime.now(timezone.utc)
            if self.paused_at:
                delta = (now - self.paused_at).total_seconds()
                self.total_paused_seconds += max(0.0, delta)
            self.is_paused = False
            self.paused_at = None

    def record_response(self, when: Optional[datetime] = None) -> None:
        if not self.response_at:
            self.response_at = when or datetime.now(timezone.utc)

    def record_resolution(self, when: Optional[datetime] = None) -> None:
        if not self.resolution_at:
            self.resolution_at = when or datetime.now(timezone.utc)


class SlaEngine:
    """Calculates SLA deadlines and monitors breach status."""

    NEAR_BREACH_THRESHOLD = 0.80  # 80% of SLA time elapsed

    @staticmethod
    def calculate_deadline(start_time: datetime, target_hours: float, paused_seconds: float = 0.0) -> datetime:
        """Calculate deadline adding business hours + paused seconds."""
        # Simple continuous clock with paused seconds offset
        target_seconds = target_hours * 3600.0
        return start_time + timedelta(seconds=target_seconds + paused_seconds)

    @classmethod
    def evaluate(cls, clock: SlaClock, current_time: Optional[datetime] = None) -> Dict[str, Any]:
        now = current_time or datetime.now(timezone.utc)

        # Ensure created_at has timezone
        created_at = clock.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        # Effective paused seconds
        effective_paused = clock.total_paused_seconds
        if clock.is_paused and clock.paused_at:
            paused_at = clock.paused_at
            if paused_at.tzinfo is None:
                paused_at = paused_at.replace(tzinfo=timezone.utc)
            effective_paused += max(0.0, (now - paused_at).total_seconds())

        # Response SLA
        response_deadline = cls.calculate_deadline(created_at, clock.policy.response_hours, effective_paused)
        response_time = clock.response_at or now
        if response_time.tzinfo is None:
            response_time = response_time.replace(tzinfo=timezone.utc)

        # Resolution SLA
        resolution_deadline = cls.calculate_deadline(created_at, clock.policy.resolution_hours, effective_paused)
        resolution_time = clock.resolution_at or now
        if resolution_time.tzinfo is None:
            resolution_time = resolution_time.replace(tzinfo=timezone.utc)

        # Resolution evaluation
        target_resolution_secs = clock.policy.resolution_hours * 3600.0
        elapsed_resolution_secs = max(0.0, (resolution_time - created_at).total_seconds() - effective_paused)
        consumed_ratio = min(5.0, elapsed_resolution_secs / target_resolution_secs) if target_resolution_secs > 0 else 1.0

        # Determine state and escalation tier
        if clock.resolution_at is not None:
            state = SlaState.RESOLVED
            escalation = EscalationTier.NONE
            is_breached = resolution_time > resolution_deadline
        elif clock.is_paused:
            state = SlaState.PAUSED
            escalation = EscalationTier.NONE
            is_breached = False
        elif now > resolution_deadline:
            state = SlaState.BREACHED
            is_breached = True
            overdue_secs = (now - resolution_deadline).total_seconds()
            if overdue_secs > 7200.0:  # > 2 hours overdue
                escalation = EscalationTier.TIER_3_OPERATIONS
            else:
                escalation = EscalationTier.TIER_2_SUPERVISOR
        elif consumed_ratio >= cls.NEAR_BREACH_THRESHOLD:
            state = SlaState.NEAR_BREACH
            escalation = EscalationTier.TIER_1_WARNING
            is_breached = False
        else:
            state = SlaState.ON_TRACK
            escalation = EscalationTier.NONE
            is_breached = False

        return {
            "service_order_ref": clock.service_order_ref,
            "policy_code": clock.policy.code,
            "priority": clock.policy.priority.value,
            "state": state.value,
            "is_breached": is_breached,
            "is_paused": clock.is_paused,
            "consumed_pct": round(consumed_ratio * 100.0, 1),
            "response_deadline": response_deadline.isoformat(),
            "resolution_deadline": resolution_deadline.isoformat(),
            "response_at": clock.response_at.isoformat() if clock.response_at else None,
            "resolution_at": clock.resolution_at.isoformat() if clock.resolution_at else None,
            "escalation_tier": escalation.value,
            "escalation_template": clock.policy.escalation_template if escalation != EscalationTier.NONE else None,
            "evaluation_time": now.isoformat()
        }
