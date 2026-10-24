"""GV-009: tooling/events/test_consumer_idempotency.py measures dedup counts and
drift instead of hard-coding them - a leaking dedup barrier is a FAIL, and the
production dedup store is reported UNMEASURED, so the verdict is never PASS."""

from __future__ import annotations

import importlib.util
import json
import socket
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "events" / "test_consumer_idempotency.py"


def _load():
    spec = importlib.util.spec_from_file_location("consumer_idempotency_tool_ut", SCRIPT)
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


def test_measured_dedup_and_unmeasured_production_store(mod):
    res = mod.run_idempotency_stress_test(total_unique=300, num_duplicates=100)
    statuses = _statuses(res)
    assert statuses.pop("production_dedup_store_at_scale") == "UNMEASURED"
    assert set(statuses.values()) == {"PASS"}
    assert res["duplicate_events_intercepted"] == 100
    assert res["duplicate_mutations_executed"] == 0
    assert res["business_state"]["balance_drift"] == 0
    assert res["verdict"] == "INCOMPLETE"


def test_leaking_dedup_barrier_is_a_fail(mod, monkeypatch):
    monkeypatch.setattr(mod.IdempotencyLedger, "check_and_set", lambda self, event_id: True)
    res = mod.run_idempotency_stress_test(total_unique=300, num_duplicates=100)
    statuses = _statuses(res)
    assert statuses["one_mutation_per_unique_event"] == "FAIL"
    assert statuses["duplicates_intercepted"] == "FAIL"
    assert statuses["zero_balance_drift"] == "FAIL"
    assert res["duplicate_mutations_executed"] == 100
    assert res["business_state"]["balance_drift"] == 100 * mod.AMOUNT_BDT
    assert res["verdict"] == "FAIL"
    assert mod.exit_code_for(res["verdict"]) == 1


def test_main_writes_the_computed_verdict(mod, tmp_path):
    assert mod.main() == 2
    evidence = json.loads((tmp_path / mod.EVIDENCE_FILE).read_text(encoding="utf-8"))
    assert evidence["verdict"] == evidence["results"]["verdict"] == "INCOMPLETE"
    assert "in_process_microbenchmark" in evidence["results"]
