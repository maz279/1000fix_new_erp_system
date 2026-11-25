"""SLA clock edge cases: idempotent transitions, naive timestamps, package API (G1-04)."""

from __future__ import annotations

import importlib.util
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

_SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(_SRC))

from sla_engine import SlaClock, SlaEngine, SlaPolicy, SlaPriority, SlaState

START = datetime(2026, 10, 16, 9, 0, tzinfo=UTC)
NAIVE_START = START.replace(tzinfo=None)


@pytest.fixture
def policy():
    return SlaPolicy(
        code="SLA-HIGH",
        name="High",
        service_type="onsite",
        priority=SlaPriority.HIGH,
        response_hours=1.0,
        resolution_hours=10.0,
    )


@pytest.fixture
def sla_pkg(monkeypatch):
    """Load services/sla-engine/src as a package under a unique name."""
    name = "sla_engine_src_pkg"
    spec = importlib.util.spec_from_file_location(
        name, _SRC / "__init__.py", submodule_search_locations=[str(_SRC)]
    )
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, name, module)
    spec.loader.exec_module(module)
    yield module
    sys.modules.pop(f"{name}.sla_engine", None)


def test_package_reexports_public_api(sla_pkg, policy):
    assert sorted(sla_pkg.__all__) == [
        "EscalationTier",
        "SlaClock",
        "SlaEngine",
        "SlaPolicy",
        "SlaPriority",
        "SlaState",
    ]
    pkg_policy = sla_pkg.SlaPolicy("P", "P", "walk_in", sla_pkg.SlaPriority.NORMAL, 1.0, 2.0)
    clock = sla_pkg.SlaClock("SO-PKG", pkg_policy, START)
    res = sla_pkg.SlaEngine.evaluate(clock, current_time=START + timedelta(hours=1))
    assert res["state"] == sla_pkg.SlaState.ON_TRACK.value
    assert res["consumed_pct"] == 50.0


def test_policy_rejects_non_positive_resolution():
    with pytest.raises(ValueError, match="positive business hours"):
        SlaPolicy("E", "E", "walk_in", SlaPriority.NORMAL, response_hours=1, resolution_hours=-1)


def test_pause_is_idempotent(policy):
    clock = SlaClock("SO-1", policy, START)
    first = START + timedelta(hours=1)
    clock.pause(when=first)
    clock.pause(when=first + timedelta(hours=3))
    assert clock.paused_at == first


def test_pause_defaults_to_now(policy):
    clock = SlaClock("SO-1", policy, START)
    before = datetime.now(UTC)
    clock.pause()
    assert clock.is_paused is True
    assert before <= clock.paused_at <= datetime.now(UTC)


def test_resume_when_not_paused_is_noop(policy):
    clock = SlaClock("SO-2", policy, START, total_paused_seconds=60.0)
    clock.resume(when=START + timedelta(hours=5))
    assert clock.is_paused is False
    assert clock.total_paused_seconds == 60.0


def test_resume_without_pause_timestamp_adds_nothing(policy):
    clock = SlaClock("SO-3", policy, START, is_paused=True, paused_at=None)
    clock.resume(when=START + timedelta(hours=5))
    assert clock.is_paused is False
    assert clock.paused_at is None
    assert clock.total_paused_seconds == 0.0


def test_resume_before_pause_never_subtracts(policy):
    clock = SlaClock("SO-3b", policy, START)
    clock.pause(when=START + timedelta(hours=2))
    clock.resume(when=START + timedelta(hours=1))  # clock skew
    assert clock.total_paused_seconds == 0.0


def test_record_response_is_first_write_wins(policy):
    clock = SlaClock("SO-4", policy, START)
    first = START + timedelta(minutes=30)
    clock.record_response(when=first)
    clock.record_response(when=first + timedelta(hours=2))
    assert clock.response_at == first
    res = SlaEngine.evaluate(clock, current_time=START + timedelta(hours=1))
    assert res["response_at"] == first.isoformat()
    assert res["response_deadline"] == (START + timedelta(hours=1)).isoformat()


def test_record_response_defaults_to_now(policy):
    clock = SlaClock("SO-4b", policy, START)
    clock.record_response()
    assert clock.response_at is not None
    assert clock.response_at.tzinfo is UTC


def test_record_resolution_is_first_write_wins(policy):
    clock = SlaClock("SO-5", policy, START)
    first = START + timedelta(hours=3)
    clock.record_resolution(when=first)
    clock.record_resolution(when=first + timedelta(hours=30))
    assert clock.resolution_at == first


def test_naive_timestamps_are_treated_as_utc(policy):
    clock = SlaClock(
        "SO-6",
        policy,
        NAIVE_START,
        response_at=NAIVE_START + timedelta(minutes=20),
        resolution_at=NAIVE_START + timedelta(hours=12),
    )
    res = SlaEngine.evaluate(clock, current_time=NAIVE_START + timedelta(hours=13))
    assert res["state"] == SlaState.RESOLVED.value
    assert res["is_breached"] is True  # resolved 2h after the 10h deadline
    assert res["escalation_template"] is None
    assert res["resolution_deadline"] == (START + timedelta(hours=10)).isoformat()
    assert res["evaluation_time"] == (START + timedelta(hours=13)).isoformat()
    assert res["consumed_pct"] == 120.0


def test_naive_pause_extends_deadline_while_paused(policy):
    clock = SlaClock("SO-7", policy, NAIVE_START)
    clock.pause(when=NAIVE_START + timedelta(hours=2))
    res = SlaEngine.evaluate(clock, current_time=NAIVE_START + timedelta(hours=5))
    assert res["state"] == SlaState.PAUSED.value
    assert res["is_paused"] is True
    # 3h paused so far pushes the 10h resolution deadline to 13h
    assert res["resolution_deadline"] == (START + timedelta(hours=13)).isoformat()
    assert res["consumed_pct"] == 20.0


def test_paused_flag_without_timestamp_uses_recorded_pause_only(policy):
    clock = SlaClock("SO-8", policy, START, is_paused=True, paused_at=None)
    res = SlaEngine.evaluate(clock, current_time=START + timedelta(hours=4))
    assert res["state"] == SlaState.PAUSED.value
    assert res["resolution_deadline"] == (START + timedelta(hours=10)).isoformat()


def test_evaluate_defaults_to_now(policy):
    clock = SlaClock("SO-9", policy, datetime.now(UTC))
    res = SlaEngine.evaluate(clock)
    assert res["state"] == SlaState.ON_TRACK.value
    assert res["escalation_template"] is None


def test_consumed_ratio_is_capped_at_five(policy):
    clock = SlaClock("SO-10", policy, START)
    res = SlaEngine.evaluate(clock, current_time=START + timedelta(hours=100))
    assert res["consumed_pct"] == 500.0
    assert res["state"] == SlaState.BREACHED.value
    assert res["escalation_template"] == "NT-020"
