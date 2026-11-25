"""GV-009: tooling/events/test_kafka_dlq_replay.py computes replay / DLQ results -
a leaky replay window or a failed remediation is a FAIL, the live cluster is
UNMEASURED, and no literal PASS is written."""

from __future__ import annotations

import importlib.util
import json
import socket
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "events" / "test_kafka_dlq_replay.py"


def _load():
    spec = importlib.util.spec_from_file_location("kafka_dlq_replay_tool_ut", SCRIPT)
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


def test_in_process_replay_and_dlq_measured_live_unmeasured(mod):
    res = mod.run_dlq_and_replay_tests(total_vat_events=60, pre_anchor_events=5)
    statuses = _statuses(res)
    assert statuses.pop("live_cluster_replay_and_dlq") == "UNMEASURED"
    assert set(statuses.values()) == {"PASS"}
    assert res["time_travel_replay"]["total_replayed"] == 60
    assert res["dead_letter_queue"]["dlq_record_count"] == 1
    assert res["verdict"] == "INCOMPLETE"


def test_replay_that_ignores_the_anchor_is_a_fail(mod, monkeypatch):
    class Leaky(mod.EventReplayEngine):
        def replay_from_timestamp(self, topic, timestamp, target_handler, max_records=10000):
            return super().replay_from_timestamp(topic, 0.0, target_handler, max_records)

    monkeypatch.setattr(mod, "EventReplayEngine", Leaky)
    res = mod.run_dlq_and_replay_tests(total_vat_events=60, pre_anchor_events=5)
    assert _statuses(res)["replay_from_anchor_exact_window"] == "FAIL"
    assert res["verdict"] == "FAIL"


def test_failed_remediation_is_a_fail(mod, monkeypatch):
    monkeypatch.setattr(mod, "remediator", lambda payload: dict(payload))  # still malformed
    res = mod.run_dlq_and_replay_tests(total_vat_events=20, pre_anchor_events=2)
    assert _statuses(res)["dlq_redrive_ingested_and_idempotent"] == "FAIL"
    assert res["verdict"] == "FAIL"
    assert mod.exit_code_for(res["verdict"]) == 1


def test_main_writes_the_computed_verdict(mod, tmp_path):
    assert mod.main() == 2
    evidence = json.loads((tmp_path / mod.EVIDENCE_FILE).read_text(encoding="utf-8"))
    assert evidence["verdict"] == evidence["results"]["verdict"] == "INCOMPLETE"
