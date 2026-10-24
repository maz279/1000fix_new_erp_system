"""stt fallbacks: accuracy classes, ml-gateway-less operation and the import
fallback chain (P11-M04 / M26 W8).

The ml_gateway dependency is replaced with in-memory fakes so the shared
model registry is never mutated by this module.

GV-009: no production WER has ever been measured. Without a gateway model
card carrying a measured ``metrics.wer``, the tracker reports
baseline_wer=None and status BASELINE_UNMEASURED - it never seeds itself
with an invented number (the old builtin baseline was a fabricated 0.118).
"""

from __future__ import annotations

import builtins
import importlib.util
import sys
import types
from pathlib import Path

import pytest

_SRC = Path(__file__).resolve().parents[1] / "src"
_STT_PATH = _SRC / "stt.py"
_ML_GW_SRC = str(Path(__file__).resolve().parents[2] / "ml-gateway" / "src")
sys.path.insert(0, str(_SRC))

import stt
from stt import STTProductionTracker, classify_bn_accuracy, compute_wer

# 4 of 5 words wrong -> average WER 0.8, far above any baseline.
_DEGRADED = [("এক দুই তিন চার পাঁচ", "এক ছয় সাত আট নয়")]


def _fake_gateway(info=None, drift=None, retrain=None):
    """A stand-in ml_gateway exposing only the attributes given."""
    calls = {"retrain": []}
    ns = types.SimpleNamespace(get_model_info=lambda name: info)
    if drift is not None:
        ns.detect_drift = lambda name, actual, predicted, threshold: drift
    if retrain is not None:

        def trigger_retraining(name, trigger_reason):
            calls["retrain"].append((name, trigger_reason))
            return retrain

        ns.trigger_retraining = trigger_retraining
    return ns, calls


@pytest.mark.parametrize(
    ("wer", "label"),
    [
        (0.0, "production-ready"),
        (0.15, "production-ready"),
        (0.2, "usable-with-review"),
        (0.30, "usable-with-review"),
        (0.4, "needs-improvement"),
        (0.50, "needs-improvement"),
        (0.51, "unusable"),
    ],
)
def test_accuracy_classes(wer, label):
    assert classify_bn_accuracy(wer) == label


def test_wer_with_empty_reference():
    assert compute_wer("", "").wer == 0.0
    assert compute_wer("", "কিছু").wer == 1.0


def test_empty_batch_is_not_recorded():
    tracker = STTProductionTracker()
    assert tracker.record_evaluation_batch("B-EMPTY", []) == {
        "batch_id": "B-EMPTY",
        "samples": 0,
        "average_wer": 0.0,
    }
    assert tracker.evaluation_history == []
    assert tracker.total_samples == 0
    assert tracker.active_batch_count == 0


class TestWithoutGateway:
    @pytest.fixture(autouse=True)
    def no_gateway(self, monkeypatch):
        monkeypatch.setattr(stt, "ml_gateway", None)

    def test_no_baseline_is_reported_as_unmeasured_not_healthy(self):
        result = STTProductionTracker().check_drift_and_retrain()
        assert result["baseline_wer"] is None
        assert result["current_wer"] is None
        assert result["drift_detected"] is None
        assert result["retraining_event"] is None
        assert result["status"] == "BASELINE_UNMEASURED"
        assert "no measured WER baseline" in result["reason"]

    def test_degraded_batch_without_baseline_still_cannot_drift_check(self):
        tracker = STTProductionTracker()
        tracker.record_evaluation_batch("B-BAD", _DEGRADED)
        result = tracker.check_drift_and_retrain(threshold=0.15)
        assert result["current_wer"] == 0.8  # the fixture batch IS measured
        assert result["baseline_wer"] is None  # but no baseline exists
        assert result["drift_detected"] is None
        assert result["retraining_event"] is None
        assert result["status"] == "BASELINE_UNMEASURED"
        assert tracker.last_drift_check is result

    def test_dashboard_uses_the_unregistered_card(self):
        tracker = STTProductionTracker()
        dash = tracker.get_dashboard_metrics()
        assert dash["active_version"] == "unregistered"
        assert dash["stage"] == "not-deployed"
        assert dash["model_architecture"] == "external-backend-required"
        assert dash["baseline_wer"] is None  # nothing invented
        assert dash["measured_wer"] is None  # nothing measured yet
        assert dash["accuracy_class"] == "unmeasured"
        assert dash["metrics_breakdown"]["character_error_rate"] is None
        assert dash["metrics_breakdown"]["real_time_factor_rtf"] is None
        assert dash["drift_monitoring"]["status"] == "BASELINE_UNMEASURED"
        assert dash["recent_batches"] == []

    def test_dashboard_reflects_measured_history(self):
        tracker = STTProductionTracker()
        tracker.record_evaluation_batch("B-BAD", _DEGRADED)
        dash = tracker.get_dashboard_metrics()
        assert dash["measured_wer"] == 0.8
        assert dash["accuracy_class"] == "unusable"
        assert dash["total_transcriptions_evaluated"] == 1
        assert dash["evaluation_batches_recorded"] == 1
        assert dash["baseline_wer"] is None  # measured run, invented baseline never


class TestWithPartialGateway:
    def test_missing_model_card_keeps_baseline_unmeasured(self, monkeypatch):
        gw, _ = _fake_gateway(info=None)  # no detect_drift / trigger_retraining
        monkeypatch.setattr(stt, "ml_gateway", gw)
        result = STTProductionTracker().check_drift_and_retrain()
        assert result["baseline_wer"] is None
        assert result["status"] == "BASELINE_UNMEASURED"

    def test_model_card_without_measured_wer_stays_unmeasured(self, monkeypatch):
        gw, _ = _fake_gateway(info={"metrics": {"cer": 0.04}}, drift=False)
        monkeypatch.setattr(stt, "ml_gateway", gw)
        assert STTProductionTracker().check_drift_and_retrain()["baseline_wer"] is None

    def test_measured_baseline_and_no_drift_is_healthy(self, monkeypatch):
        gw, _ = _fake_gateway(info={"metrics": {"wer": 0.118}}, drift=False)
        monkeypatch.setattr(stt, "ml_gateway", gw)
        result = STTProductionTracker().check_drift_and_retrain()
        assert result["baseline_wer"] == 0.118
        assert result["current_wer"] == 0.118
        assert result["status"] == "HEALTHY"

    def test_gateway_drift_without_retraining_hook(self, monkeypatch):
        gw, _ = _fake_gateway(info={"metrics": {"wer": 0.2}}, drift=True)
        monkeypatch.setattr(stt, "ml_gateway", gw)
        result = STTProductionTracker().check_drift_and_retrain()
        assert result["baseline_wer"] == 0.2
        assert result["drift_detected"] is True
        assert result["retraining_event"] is None
        assert result["status"] == "DRIFT_DETECTED"

    def test_gateway_reports_no_drift_so_no_retraining(self, monkeypatch):
        gw, calls = _fake_gateway(info={"metrics": {"wer": 0.1}}, drift=False, retrain={"x": 1})
        monkeypatch.setattr(stt, "ml_gateway", gw)
        result = STTProductionTracker().check_drift_and_retrain()
        assert result["status"] == "HEALTHY"
        assert calls["retrain"] == []

    def test_gateway_drift_triggers_retraining(self, monkeypatch):
        event = {"model_name": "bengali-stt", "to_version": "0.1.0"}
        gw, calls = _fake_gateway(info={"metrics": {"wer": 0.1}}, drift=True, retrain=event)
        monkeypatch.setattr(stt, "ml_gateway", gw)
        tracker = STTProductionTracker()
        tracker.record_evaluation_batch("B-BAD", _DEGRADED)
        result = tracker.check_drift_and_retrain(threshold=0.2)
        assert result["status"] == "RETRAINED"
        assert result["retraining_event"] is event
        assert calls["retrain"] == [
            ("bengali-stt", "WER drifted from 0.100 to 0.800 (threshold=0.2)")
        ]

    def test_module_dashboard_uses_default_tracker(self, monkeypatch):
        gw, _ = _fake_gateway(
            info={
                "version": "9.9.9",
                "stage": "evaluated",
                "model_backend": "whisper-v3",
                "metrics": {"wer": 0.1, "cer": 0.01},
            }
        )
        monkeypatch.setattr(stt, "ml_gateway", gw)
        monkeypatch.setattr(stt, "_DEFAULT_TRACKER", STTProductionTracker())
        dash = stt.get_stt_dashboard_metrics()
        assert dash["active_version"] == "9.9.9"
        assert dash["stage"] == "evaluated"
        assert dash["baseline_wer"] == 0.1
        assert dash["metrics_breakdown"]["character_error_rate"] == 0.01
        assert dash["metrics_breakdown"]["real_time_factor_rtf"] is None  # not measured


# ---------------------------------------------------------------- import chain


def _load_stt_copy(monkeypatch, name):
    spec = importlib.util.spec_from_file_location(name, _STT_PATH)
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, name, module)
    spec.loader.exec_module(module)
    return module


def _fail_first_ml_gateway_import(monkeypatch):
    real_import = builtins.__import__
    attempts = []

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "ml_gateway":
            attempts.append(name)
            if len(attempts) == 1:
                raise ImportError("simulated: ml_gateway not on sys.path")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    return attempts


def test_import_fallback_adds_sibling_ml_gateway_to_path(monkeypatch):
    monkeypatch.setattr(sys, "path", [p for p in sys.path if p != _ML_GW_SRC])
    attempts = _fail_first_ml_gateway_import(monkeypatch)
    module = _load_stt_copy(monkeypatch, "stt_fallback_path_insert")
    assert attempts == ["ml_gateway", "ml_gateway"]
    assert sys.path[0] == _ML_GW_SRC
    assert module.ml_gateway is not None
    assert module.ml_gateway.get_model_info("bengali-stt") is not None


def test_import_fallback_does_not_duplicate_existing_path(monkeypatch):
    monkeypatch.setattr(sys, "path", [_ML_GW_SRC, *[p for p in sys.path if p != _ML_GW_SRC]])
    attempts = _fail_first_ml_gateway_import(monkeypatch)
    module = _load_stt_copy(monkeypatch, "stt_fallback_path_present")
    assert attempts == ["ml_gateway", "ml_gateway"]
    assert sys.path.count(_ML_GW_SRC) == 1
    assert module.ml_gateway is not None


def test_import_fallback_degrades_to_no_gateway(monkeypatch):
    # A None entry makes every `import ml_gateway` raise ImportError.
    monkeypatch.setitem(sys.modules, "ml_gateway", None)
    module = _load_stt_copy(monkeypatch, "stt_fallback_no_gateway")
    assert module.ml_gateway is None
    result = module.STTProductionTracker().check_drift_and_retrain()
    assert result["status"] == "BASELINE_UNMEASURED"  # honest, not "HEALTHY"
    assert module.get_stt_dashboard_metrics()["active_version"] == "unregistered"
