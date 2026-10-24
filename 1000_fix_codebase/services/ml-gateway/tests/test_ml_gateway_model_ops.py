"""ml-gateway model-ops edges: retraining, lineage and rollback (R07-M04)."""

from __future__ import annotations

import copy
import datetime as _datetime
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import ml_gateway
from ml_gateway import (
    DispatchFeatures,
    detect_drift,
    get_model_lineage,
    rollback_model,
    score_dispatch,
    trigger_retraining,
)

FIXED_TODAY = _datetime.date(2026, 10, 22)


class _FixedDate(_datetime.date):
    @classmethod
    def today(cls):
        return FIXED_TODAY


@pytest.fixture(autouse=True)
def isolated_registry(monkeypatch):
    """The registry and the retraining log are module globals: snapshot and
    restore them so these tests never leak state into other suites."""
    registry = copy.deepcopy(ml_gateway.MODEL_REGISTRY)
    log = copy.deepcopy(ml_gateway.RETRAINING_LOG)
    monkeypatch.setattr(_datetime, "date", _FixedDate)
    yield
    ml_gateway.MODEL_REGISTRY.clear()
    ml_gateway.MODEL_REGISTRY.update(registry)
    ml_gateway.RETRAINING_LOG[:] = log


def test_urgent_priority_adds_urgency_factor():
    normal = score_dispatch(DispatchFeatures("T1"))
    urgent = score_dispatch(
        DispatchFeatures("T1", priority="urgent", historical_ftf=0.8, historical_sla=0.5)
    )
    assert normal.factors["urgency"] == 0.0
    assert urgent.factors["urgency"] == 1.0
    assert urgent.factors["first_time_fix"] == 2.0
    assert urgent.factors["sla_hit"] == 0.75
    assert urgent.score == round(3.0 + 2.0 + 0.75 + 0.0 + 1.0, 4)


def test_uncertified_is_blocked_by_large_penalty():
    result = score_dispatch(DispatchFeatures("T9", certification_active=False, workload_today=2))
    assert result.factors["certification"] == -100.0
    assert result.factors["workload"] == -0.6


def test_drift_with_zero_actual_is_never_drift():
    assert detect_drift("m", actual=0, predicted=50) is False


def test_drift_uses_relative_error_against_negative_actual():
    assert detect_drift("m", actual=-100, predicted=-130) is True


def test_retraining_unknown_model_refused():
    with pytest.raises(ValueError, match="Unknown model: nope"):
        trigger_retraining("nope", "drift")


def test_retraining_demand_forecast_logs_event_and_invents_no_metrics():
    old = copy.deepcopy(ml_gateway.MODEL_REGISTRY["demand-forecast"])
    event = trigger_retraining("demand-forecast", "scheduled")
    model = ml_gateway.MODEL_REGISTRY["demand-forecast"]

    assert event == {
        "model_name": "demand-forecast",
        "from_version": old["version"],
        "to_version": f"{old['version'].split('.')[0]}.{int(old['version'].split('.')[1]) + 1}.0",
        "reason": "scheduled",
        "triggered_at": "2026-10-22",
        "status": "recorded",  # bookkeeping only - no training pipeline ran
        "note": "no training backend is deployed; metrics remain unmeasured",
    }
    # No fabricated post-retraining accuracy: metrics stay empty/unmeasured.
    assert model["metrics"] == {}
    assert model["trained_at"] is None
    assert model["stage"] == "retrain-requested"
    assert model["history"][-1] == {
        "version": old["version"],
        "stage": "archived",
        "prior_stage": old["stage"],
        "trained_at": old["trained_at"],
        "metrics": old["metrics"],
    }
    assert ml_gateway.RETRAINING_LOG[-1] is event
    assert event in get_model_lineage("demand-forecast")["retraining_events"]


def test_retraining_bengali_stt_never_invents_a_wer():
    trigger_retraining("bengali-stt", "WER drift")
    model = ml_gateway.MODEL_REGISTRY["bengali-stt"]
    assert model["metrics"] == {}  # no production WER has ever been measured
    assert model["stage"] == "not-deployed"  # retraining request cannot deploy a backend


def test_retraining_unlisted_model_keeps_metrics_and_creates_history(monkeypatch):
    monkeypatch.setitem(
        ml_gateway.MODEL_REGISTRY,
        "warranty-fraud",
        {"version": "2.3.1", "stage": "staging", "trained_at": "2026-01-01"},
    )
    event = trigger_retraining("warranty-fraud", "manual")
    model = ml_gateway.MODEL_REGISTRY["warranty-fraud"]
    assert (event["from_version"], event["to_version"]) == ("2.3.1", "2.4.0")
    assert model["stage"] == "retrain-requested"
    assert "metrics" in model and model["metrics"] == {}  # none invented
    assert model["history"] == [
        {
            "version": "2.3.1",
            "stage": "archived",
            "prior_stage": "staging",
            "trained_at": "2026-01-01",
            "metrics": {},
        }
    ]

    lineage = get_model_lineage("warranty-fraud")
    assert lineage["lineage"] == {}
    assert lineage["metrics"] == {}
    assert lineage["retraining_events"] == [event]


def test_lineage_unknown_model_refused():
    with pytest.raises(ValueError, match="Unknown model: ghost"):
        get_model_lineage("ghost")


def test_rollback_unknown_model_refused():
    with pytest.raises(ValueError, match="Unknown model: ghost"):
        rollback_model("ghost", "1.0.0")


def test_rollback_to_version_absent_from_history_refused():
    before = copy.deepcopy(ml_gateway.MODEL_REGISTRY["dispatch-scoring"])
    with pytest.raises(ValueError, match=r"Version 7\.7\.7 not found"):
        rollback_model("dispatch-scoring", "7.7.7")
    assert ml_gateway.MODEL_REGISTRY["dispatch-scoring"] == before


def test_rollback_without_any_history_refused(monkeypatch):
    monkeypatch.setitem(
        ml_gateway.MODEL_REGISTRY, "bare", {"version": "1.0.0", "stage": "production"}
    )
    with pytest.raises(ValueError, match="not found in model history"):
        rollback_model("bare", "0.9.0")


def test_rollback_restores_archived_state():
    # No shipped history exists (nothing was ever trained): create one via a
    # retraining event, then roll back to it.
    trigger_retraining("demand-forecast", "scheduled")
    archived = ml_gateway.MODEL_REGISTRY["demand-forecast"]["history"][0]
    current = ml_gateway.MODEL_REGISTRY["demand-forecast"]["version"]
    res = rollback_model("demand-forecast", archived["version"])
    model = ml_gateway.MODEL_REGISTRY["demand-forecast"]
    assert res == {
        "model_name": "demand-forecast",
        "rolled_back_from": current,
        "active_version": archived["version"],
        "status": "rolled_back",
    }
    assert model["metrics"] == archived["metrics"]
    assert model["metrics"] is not archived["metrics"]  # copied, not aliased
    assert model["trained_at"] == archived["trained_at"]
    assert model["stage"] == archived["prior_stage"]  # real prior stage restored
