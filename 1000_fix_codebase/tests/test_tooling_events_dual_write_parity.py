"""GV-009: tooling/events/verify_dual_write_parity.py checks parity record by
record - a divergent payload or a dropped causation_id is a FAIL, live Redis /
Kafka is UNMEASURED, and the evidence verdict is the computed one."""

from __future__ import annotations

import importlib.util
import json
import socket
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "events" / "verify_dual_write_parity.py"


def _load():
    spec = importlib.util.spec_from_file_location("verify_dual_write_parity_ut", SCRIPT)
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


def _bus(mod, cls):
    bus = cls()
    bus.kafka_client = mod.InMemoryBus()
    bus.redis_store = mod.MockRedisStreamStore()
    return bus


def test_full_fidelity_bus_is_incomplete_not_pass(mod):
    class FullFidelity(mod.DualWriteEventBus):
        def publish_dual(self, event_type, aggregate, aggregate_id, payload, metadata=None):
            res = super().publish_dual(event_type, aggregate, aggregate_id, payload, metadata)
            fields = self.redis_store.get_messages(res["redis_stream"])[-1]["fields"]
            fields["causation_id"] = (metadata or {}).get("causation_id")
            return res

    res = mod.run_dual_write_parity_verification(50, bus=_bus(mod, FullFidelity))
    statuses = _statuses(res)
    assert statuses.pop("live_redis_and_kafka_dual_write") == "UNMEASURED"
    assert set(statuses.values()) == {"PASS"}
    assert res["verdict"] == "INCOMPLETE"


def test_divergent_payload_on_one_bus_is_a_fail(mod):
    class Corrupting(mod.DualWriteEventBus):
        def publish_dual(self, event_type, aggregate, aggregate_id, payload, metadata=None):
            res = super().publish_dual(event_type, aggregate, aggregate_id, payload, metadata)
            if payload["seq"] == 7:
                rec = self.kafka_client._topics[res["kafka_topic"]][res["kafka_partition"]]
                rec.records[res["kafka_offset"]].value["payload"] = {"seq": 7, "tampered": True}
            return res

    res = mod.run_dual_write_parity_verification(50, bus=_bus(mod, Corrupting))
    assert _statuses(res)["payload_sha256_parity"] == "FAIL"
    assert res["mismatch_counts"]["payload_digest"] == 1
    assert res["verdict"] == "FAIL"
    assert mod.exit_code_for(res["verdict"]) == 1


def test_library_bus_never_reports_pass_and_main_writes_computed_verdict(mod, tmp_path):
    exit_code = mod.main()
    evidence = json.loads((tmp_path / mod.EVIDENCE_FILE).read_text(encoding="utf-8"))
    assert evidence["verdict"] == evidence["results"]["verdict"]
    assert evidence["verdict"] in {"FAIL", "INCOMPLETE"}
    assert exit_code == mod.exit_code_for(evidence["verdict"])
