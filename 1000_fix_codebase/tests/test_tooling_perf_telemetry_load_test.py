"""GV-009: tooling/performance/run_telemetry_load_test.py no longer times a sleep as
"TimescaleDB flush" or hard-codes PASS - the throttle rule and the product
thresholds are checked, the load targets are UNMEASURED, and the status is
computed."""

from __future__ import annotations

import importlib.util
import json
import socket
import sys
import urllib.error
import urllib.request
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "performance" / "run_telemetry_load_test.py"
RULE_SOURCE = "        if elapsed < 30.0 and dist < 100.0:\n            is_throttled = True\n"


def _load():
    spec = importlib.util.spec_from_file_location("run_telemetry_load_test_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def mod(monkeypatch, tmp_path):
    def no_network(*args, **kwargs):
        raise OSError("network disabled in tests")

    def no_http(*args, **kwargs):
        raise urllib.error.URLError("network disabled in tests")

    monkeypatch.setattr(socket, "create_connection", no_network)
    monkeypatch.setattr(urllib.request, "urlopen", no_http)
    module = _load()
    monkeypatch.setattr(module, "EVIDENCE_DIR", tmp_path / "evidence")
    return module


@pytest.fixture
def model(tmp_path):
    path = tmp_path / "fix_technician_location.py"
    path.write_text(RULE_SOURCE, encoding="utf-8")
    return path


def _statuses(res):
    return {c["check"]: c["status"] for c in res["checks"]}


def test_load_targets_unmeasured_when_collector_unreachable(mod, model, tmp_path):
    res = mod.run_telemetry_benchmark(model_path=model)
    statuses = _statuses(res)
    assert statuses["nfr056_reference_rule_boundaries"] == "PASS"
    assert statuses["product_model_encodes_nfr056_thresholds"] == "PASS"
    assert statuses["sustained_50000_events_per_minute"] == "UNMEASURED"
    assert statuses["peak_1_5x_75000_events_per_minute"] == "UNMEASURED"
    assert res["collector_probe"]["reachable"] is False
    assert res["status"] == "INCOMPLETE"
    evidence = json.loads((tmp_path / "evidence" / mod.EVIDENCE_FILE).read_text(encoding="utf-8"))
    assert evidence["status"] == "INCOMPLETE"


def test_wrong_throttle_rule_is_a_fail(mod):
    assert mod.check_rule_boundaries(rule=lambda *args: True)["status"] == "FAIL"


def test_product_without_the_rule_is_a_fail_and_missing_model_unmeasured(mod, tmp_path):
    drifted = tmp_path / "drifted.py"
    drifted.write_text("if elapsed < 60.0 or dist < 100.0:\n    pass\n", encoding="utf-8")
    assert mod.check_product_thresholds(drifted)["status"] == "FAIL"
    assert mod.check_product_thresholds(tmp_path / "absent.py")["status"] == "UNMEASURED"
    res = mod.run_telemetry_benchmark(model_path=drifted, write_evidence=False)
    assert res["status"] == "FAIL"
    assert mod.exit_code_for(res["status"]) == 1


def test_reachable_collector_attempts_the_live_window(mod, model, monkeypatch):
    """R01 re-audit 2026-10-23: the tool now REALLY POSTs pings when the
    collector is reachable. With a faked live window the statuses reflect the
    window's verdict - never an unmeasured PASS-by-assumption."""
    monkeypatch.setattr(
        mod,
        "_live_load_window",
        lambda epm, seconds=20.0: {
            "events_sent": 100,
            "events_accepted": 100,
            "events_errored": 0,
            "p95_post_latency_ms": 30.0,
            "window_seconds": seconds,
        },
    )
    res = mod.run_telemetry_benchmark(
        probe=lambda: {"reachable": True, "detail": "stub 200"},
        model_path=model,
        write_evidence=False,
    )
    statuses = {c["check"]: c["status"] for c in res["checks"]}
    assert statuses["sustained_50000_events_per_minute"] == "PASS"
    assert res["status"] == "PASS"

    # And when the live window itself errors, the load checks fail loudly.
    monkeypatch.setattr(
        mod,
        "_live_load_window",
        lambda epm, seconds=20.0: (_ for _ in ()).throw(OSError("conn refused")),
    )
    res2 = mod.run_telemetry_benchmark(
        probe=lambda: {"reachable": True, "detail": "stub 200"},
        model_path=model,
        write_evidence=False,
    )
    statuses2 = {c["check"]: c["status"] for c in res2["checks"]}
    assert statuses2["sustained_50000_events_per_minute"] == "UNMEASURED"
