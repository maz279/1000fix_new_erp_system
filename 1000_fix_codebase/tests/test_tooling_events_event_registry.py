"""GV-009: tooling/events/verify_event_registry.py reads the registry instead of
generating a catalogue - schema diffs, envelope defects and unregistered
publishers are FAILs, the 988-event claim is UNMEASURED, and nothing is a
hard-coded PASS."""

from __future__ import annotations

import importlib.util
import json
import socket
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "events" / "verify_event_registry.py"

EVENTS = [("rental.reserved", "cd_rental"), ("rental.closed", "cd_rental")]


def _load():
    spec = importlib.util.spec_from_file_location("verify_event_registry_ut", SCRIPT)
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
    monkeypatch.setattr(module, "EVIDENCE_DIR", tmp_path / "evidence")
    return module


def _schema(event_type):
    return {
        "title": event_type,
        "type": "object",
        "required": ["event_id", "event_type", "timestamp", "producer", "payload"],
        "properties": {
            "event_id": {"type": "string"},
            "event_type": {"type": "string", "const": event_type},
            "timestamp": {"type": "string"},
            "producer": {"type": "string"},
            "payload": {"type": "object"},
        },
    }


def _fixture_repo(root: Path, published: list[str]) -> tuple[Path, Path]:
    events_dir = root / "contracts" / "events"
    events_dir.mkdir(parents=True)
    entries = []
    for event_type, producer in EVENTS:
        fname = event_type.replace(".", "_") + ".json"
        (events_dir / fname).write_text(json.dumps(_schema(event_type)), encoding="utf-8")
        entries.append(
            {
                "event_type": event_type,
                "producer": producer,
                "filename": fname,
                "kafka_topic": "fix.events.rental",
                "schema_version": "1.0.0",
            }
        )
    registry = {
        "total_registered_events": len(entries),
        "kafka_topics": ["fix.events.rental"],
        "events": entries,
    }
    (events_dir / "master-event-registry.json").write_text(json.dumps(registry), encoding="utf-8")
    module_dir = root / "addons" / "domain" / "d_circular" / "cd_rental"
    (module_dir / "models").mkdir(parents=True)
    (module_dir / "__manifest__.py").write_text("{'name': 'cd_rental'}\n", encoding="utf-8")
    calls = "".join(f"    publish(env, {t!r}, 'fix.rental', 1, {{}})\n" for t in published)
    (module_dir / "models" / "rental.py").write_text(f"def emit(env):\n{calls}", encoding="utf-8")
    return events_dir, root / "addons"


def _statuses(res):
    return {c["check"]: c["status"] for c in res["checks"]}


def test_conforming_registry_is_incomplete_because_988_claim_is_unmeasured(mod, tmp_path):
    events_dir, addons_dir = _fixture_repo(tmp_path, ["rental.reserved", "rental.closed"])
    res = mod.audit_registry(events_dir, addons_dir)
    statuses = _statuses(res)
    assert statuses.pop("in003_988_event_catalogue_coverage") == "UNMEASURED"
    assert statuses.pop("broker_topic_provisioning_partitions_retention") == "UNMEASURED"
    assert set(statuses.values()) == {"PASS"}
    assert res["registered_events"] == 2
    assert res["verdict"] == "INCOMPLETE"


def test_registry_defects_are_fails(mod, tmp_path):
    events_dir, addons_dir = _fixture_repo(tmp_path, ["rental.reserved", "rental.lost"])
    (events_dir / "orphan_event.json").write_text(
        json.dumps(_schema("orphan.event")), encoding="utf-8"
    )
    broken = _schema("rental.closed")
    broken["properties"]["event_type"]["const"] = "rental.ended"
    broken["required"].remove("timestamp")
    (events_dir / "rental_closed.json").write_text(json.dumps(broken), encoding="utf-8")

    res = mod.audit_registry(events_dir, addons_dir)
    statuses = _statuses(res)
    assert statuses["registry_schema_file_diff_zero"] == "FAIL"
    assert statuses["schema_envelope_conformance"] == "FAIL"
    assert statuses["registered_events_referenced_by_producer"] == "FAIL"  # rental.closed
    assert statuses["published_event_types_registered"] == "FAIL"  # rental.lost
    assert res["published_but_unregistered_list"] == ["rental.lost"]
    assert res["verdict"] == "FAIL"
    assert mod.exit_code_for(res["verdict"]) == 1


def test_main_writes_the_computed_verdict(mod, tmp_path, monkeypatch):
    events_dir, addons_dir = _fixture_repo(tmp_path, ["rental.reserved", "rental.closed"])
    monkeypatch.setattr(mod, "EVENTS_DIR", events_dir)
    monkeypatch.setattr(mod, "ADDONS_DIR", addons_dir)
    assert mod.main() == 2
    evidence = json.loads((tmp_path / "evidence" / mod.EVIDENCE_FILE).read_text(encoding="utf-8"))
    assert evidence["verdict"] == evidence["results"]["verdict"] == "INCOMPLETE"
