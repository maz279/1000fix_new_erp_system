"""GV-009: tooling/performance/run_journey_hardening_pass.py no longer reports
GET /web/login timings as journey p95 - every journey is UNMEASURED, a failing
baseline probe is a FAIL, and the status is computed."""

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
SCRIPT = REPO_ROOT / "tooling" / "performance" / "run_journey_hardening_pass.py"


def _load():
    spec = importlib.util.spec_from_file_location("run_journey_hardening_pass_ut", SCRIPT)
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
    monkeypatch.setattr(module, "EVIDENCE_DIR", tmp_path)
    return module


def _statuses(res):
    return {c["check"]: c["status"] for c in res["checks"]}


def test_unreachable_odoo_and_all_journeys_unmeasured(mod, tmp_path):
    res = mod.run_hardening_pass()
    assert set(_statuses(res).values()) == {"UNMEASURED"}
    assert res["journeys_declared"] == len(mod.JOURNEY_SPECIFICATIONS)
    assert res["journeys_measured"] == 0
    assert res["status"] == "INCOMPLETE"
    evidence = json.loads((tmp_path / mod.EVIDENCE_FILE).read_text(encoding="utf-8"))
    assert evidence["status"] == "INCOMPLETE"
    assert mod.exit_code_for(evidence["status"]) == 2


def test_failing_baseline_probe_is_a_fail(mod):
    def broken():
        raise RuntimeError("JSON-RPC error")

    res = mod.run_hardening_pass(
        reach=lambda h, p: (True, "stub"), fetch=broken, write_evidence=False
    )
    assert _statuses(res)["odoo_baseline_probe_error_free"] == "FAIL"
    assert res["status"] == "FAIL"
    assert mod.exit_code_for(res["status"]) == 1


def test_healthy_baseline_does_not_make_journeys_pass(mod):
    res = mod.run_hardening_pass(
        reach=lambda h, p: (True, "stub"), fetch=lambda: None, write_evidence=False
    )
    statuses = _statuses(res)
    assert statuses.pop("odoo_baseline_probe_error_free") == "PASS"
    assert set(statuses.values()) == {"UNMEASURED"}
    assert res["status"] == "INCOMPLETE"
