"""GV-009: tooling/performance/run_g5_profile.py, run_g6_profile.py and
run_g7_profile.py time only real requests - failed requests are errors (FAIL),
an unreachable Odoo is UNMEASURED, the 1.5x-peak load is UNMEASURED (no load is
generated), and the written status is the computed one, never a literal PASS."""

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
PERF = REPO_ROOT / "tooling" / "performance"
# script stem -> evidence status key
SCRIPTS = {
    "run_g5_profile": "status",
    "run_g6_profile": "overall_status",
    "run_g7_profile": "overall_status",
}


def _load(stem: str):
    spec = importlib.util.spec_from_file_location(f"{stem}_ut", PERF / f"{stem}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(params=sorted(SCRIPTS))
def mod(request, monkeypatch, tmp_path):
    def no_network(*args, **kwargs):
        raise OSError("network disabled in tests")

    def no_http(*args, **kwargs):
        raise urllib.error.URLError("network disabled in tests")

    monkeypatch.setattr(socket, "create_connection", no_network)
    monkeypatch.setattr(urllib.request, "urlopen", no_http)
    module = _load(request.param)
    monkeypatch.setattr(module, "EVIDENCE_DIR", tmp_path)
    module.status_key = SCRIPTS[request.param]
    return module


def _statuses(res):
    return {c["check"]: c["status"] for c in res["checks"]}


def _up(host, port):
    return True, "stub reachable"


def test_unreachable_odoo_is_unmeasured(mod):
    res = mod.run_profile(reach=lambda h, p: (False, "stub unreachable"))
    assert set(_statuses(res).values()) == {"UNMEASURED"}
    assert res["unloaded_probe"] is None
    assert res["status"] == "INCOMPLETE"


def test_failed_requests_are_errors_not_timed_successes(mod):
    def refused():
        raise ConnectionRefusedError("refused")

    res = mod.run_profile(reach=_up, fetch=refused)
    assert _statuses(res)["odoo_jsonrpc_probe_error_free"] == "FAIL"
    assert res["unloaded_probe"]["successes"] == 0
    assert res["unloaded_probe"]["latency_ms"]["p95"] is None
    assert res["status"] == "FAIL"
    assert mod.exit_code_for(res["status"]) == 1


def test_probe_over_budget_is_a_fail(mod, monkeypatch):
    monkeypatch.setattr(mod, "P95_BUDGET_MS", -1.0)
    res = mod.run_profile(reach=_up, fetch=lambda: None)
    assert _statuses(res)["odoo_jsonrpc_unloaded_p95_within_budget"] == "FAIL"
    assert res["status"] == "FAIL"


def test_healthy_probe_is_still_not_pass_without_load(mod):
    res = mod.run_profile(reach=_up, fetch=lambda: None)
    statuses = _statuses(res)
    assert statuses["odoo_jsonrpc_probe_error_free"] == "PASS"
    peak = [s for name, s in statuses.items() if name.startswith("pe004_1_5x_peak::")]
    assert peak and set(peak) == {"UNMEASURED"}
    assert res["status"] == "INCOMPLETE"


def test_main_writes_the_computed_status(mod, tmp_path):
    exit_code = mod.main()
    evidence = json.loads((tmp_path / mod.EVIDENCE_FILE).read_text(encoding="utf-8"))
    assert evidence[mod.status_key] == evidence["measurement"]["status"] == "INCOMPLETE"
    assert exit_code == 2
