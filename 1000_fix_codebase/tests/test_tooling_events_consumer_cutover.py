"""GV-009: tooling/events/run_consumer_cutover.py derives every status from a check
executed in the run - a broken rollback is a FAIL, the live drill is UNMEASURED,
and the verdict is never a hard-coded PASS."""

from __future__ import annotations

import importlib.util
import json
import socket
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "events" / "run_consumer_cutover.py"


def _load():
    spec = importlib.util.spec_from_file_location("run_consumer_cutover_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def mod(monkeypatch, tmp_path):
    def no_network(*args, **kwargs):
        raise OSError("network disabled in tests")

    monkeypatch.setattr(socket, "create_connection", no_network)
    module = _load()
    monkeypatch.setattr(module, "EVIDENCE_DIR", tmp_path)
    return module


def _statuses(res):
    return {c["check"]: c["status"] for c in res["checks"]}


def test_in_process_checks_pass_but_live_drill_is_unmeasured(mod):
    res = mod.run_consumer_cutover_drill()
    statuses = _statuses(res)
    assert statuses["live_rollback_sla_under_5s"] == "UNMEASURED"
    assert statuses["live_cluster_cutover_drill"] == "UNMEASURED"
    assert all(s == "PASS" for name, s in statuses.items() if not name.startswith("live_"))
    assert res["verdict"] == "INCOMPLETE"
    assert res["final_state_distribution"]["BUS_KAFKA"] == len(res["groups"])


def test_reachable_brokers_run_the_live_drill(mod, monkeypatch):
    """R01 re-audit 2026-10-23: reachable brokers now trigger the REAL live
    cutover drill. With a faked live drill the verdict follows its result;
    with a crashing live drill the live checks FAIL (never unmeasured)."""
    probe = {"kafka_brokers_reachable": 3, "kafka_brokers_declared": 3, "details": ["stub"]}

    monkeypatch.setattr(
        mod,
        "_live_cluster_cutover_drill",
        lambda: {
            "live_cluster_cutover_drill": (True, "stub live drill ok"),
            "live_rollback_sla_under_5s": (True, "stub rollback 0.5s"),
            "stats": {"events": 1},
        },
    )
    res = mod.run_consumer_cutover_drill(probe=lambda: probe)
    statuses = _statuses(res)
    assert statuses["live_cluster_cutover_drill"] == "PASS"
    assert statuses["live_rollback_sla_under_5s"] == "PASS"
    assert res["verdict"] == "PASS"

    monkeypatch.setattr(
        mod,
        "_live_cluster_cutover_drill",
        lambda: (_ for _ in ()).throw(OSError("brokers dropped")),
    )
    res2 = mod.run_consumer_cutover_drill(probe=lambda: probe)
    statuses2 = _statuses(res2)
    assert statuses2["live_cluster_cutover_drill"] == "FAIL"
    assert res2["verdict"] == "FAIL"


def test_broken_rollback_is_reported_as_fail(mod, monkeypatch):
    class NoRollback(mod.ConsumerGroupMigrationManager):
        def rollback_group(self, group_id, reason):  # claims success, changes nothing
            return {"group_id": group_id, "status": "ROLLED_BACK", "rollback_elapsed_ms": 0.0}

    monkeypatch.setattr(mod, "ConsumerGroupMigrationManager", NoRollback)
    res = mod.run_consumer_cutover_drill()
    statuses = _statuses(res)
    assert statuses["fault_injection_lag_breach_rolls_back_target"] == "FAIL"
    assert statuses["routing_after_rollback_reads_redis_stream"] == "FAIL"
    assert res["verdict"] == "FAIL"
    assert mod.exit_code_for(res["verdict"]) == 1


def test_a_raising_phase_is_a_fail_and_the_drill_continues(mod, monkeypatch):
    class Exploding(mod.ConsumerGroupMigrationManager):
        def transition_group(self, group_id, new_state, reason=""):
            raise RuntimeError("bus unavailable")

    monkeypatch.setattr(mod, "ConsumerGroupMigrationManager", Exploding)
    res = mod.run_consumer_cutover_drill()
    statuses = _statuses(res)
    assert statuses["transition_all_to_bus_dual"] == "FAIL"
    assert "live_cluster_cutover_drill" in statuses  # later checks still recorded
    assert res["verdict"] == "FAIL"


def test_main_writes_the_computed_verdict_and_exit_code(mod, tmp_path):
    assert mod.main() == 2
    evidence = json.loads((tmp_path / mod.EVIDENCE_FILE).read_text(encoding="utf-8"))
    assert evidence["verdict"] == evidence["results"]["verdict"] == "INCOMPLETE"
