"""Event registry guard (AS-08 / FF-19): every event the code publishes is registered.

Regression for the R01 finding "158 event types are published by code but are not in
the event registry". The registry is generated from the publish() calls by
tooling/generators/generate_event_schemas.py; these tests fail the build as soon as a
publish() name (direct, through a wrapper helper, or via a literal variable) appears
without a registry entry + schema, and pin the generator's derivation behaviour on a
synthetic addon.
"""

from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]
for _p in (ROOT, ROOT / "tooling" / "generators", ROOT / "tooling" / "events"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import event_publishers
import generate_event_schemas
import verify_event_registry

EVENTS_DIR = ROOT / "contracts" / "events"
ADDONS_DIR = ROOT / "addons"
REGENERATE = "run `python tooling/generators/generate_event_schemas.py` and commit the result"
# Event types composed at run time cannot be registered (the registry fitness check needs
# the literal in the producer module). Known, reported to the module owner; a NEW one fails.
KNOWN_COMPOSED: set[str] = set()


def _no_brokers() -> dict:
    return {"kafka_brokers_reachable": 0, "kafka_brokers_declared": 3, "details": []}


@pytest.fixture(scope="module")
def scan() -> event_publishers.ScanResult:
    return event_publishers.scan_publishers(ADDONS_DIR, ROOT / "services")


@pytest.fixture(scope="module")
def registry() -> dict:
    return json.loads((EVENTS_DIR / "master-event-registry.json").read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- the real estate


def test_every_event_type_published_by_code_is_registered(scan, registry):
    registered = {e["event_type"] for e in registry["events"]}
    unregistered = sorted(set(scan.sites) - registered)
    assert not unregistered, f"published but unregistered: {unregistered} - {REGENERATE}"


def test_every_registered_event_is_still_published(scan, registry):
    stale = sorted({e["event_type"] for e in registry["events"]} - set(scan.sites))
    assert not stale, f"registered but no longer published: {stale} - {REGENERATE}"


def test_registry_fitness_audit_passes_every_measurable_check():
    result = verify_event_registry.audit_registry(probe=_no_brokers)
    failing = [c for c in result["checks"] if c["status"] == verify_event_registry.FAILED]
    assert not failing, failing
    assert result["published_but_unregistered"] == 0
    assert result["registered_but_unreferenced_by_producer"] == 0


def test_every_registered_event_has_a_conformant_schema(registry):
    for entry in registry["events"]:
        schema = json.loads((EVENTS_DIR / entry["filename"]).read_text(encoding="utf-8"))
        assert schema["title"] == entry["event_type"]
        payload = schema["properties"]["payload"]
        assert payload["type"] == "object"
        # closed payloads only: an open catch-all must be explained by the derivation
        if payload.get("additionalProperties") is not False:
            assert entry["schema_source"] == "curated" or "description" in payload, entry


def test_no_new_run_time_composed_event_types(scan):
    composed = {c.split(":", 1)[0] + ":" + c.split(":", 2)[2] for c in scan.composed}
    assert composed <= KNOWN_COMPOSED, (
        f"event types composed at run time cannot be registered: {composed - KNOWN_COMPOSED} - "
        "publish a literal event type instead"
    )
    assert not scan.unresolved, scan.unresolved


# --------------------------------------------------------------------------- guard behaviour


SYNTHETIC_MODEL = """
from odoo import fields, models

from libs.py.fix_events import publish


class Widget(models.Model):
    _name = "fix.widget"

    name = fields.Char(required=True)
    note = fields.Char()
    qty = fields.Integer()
    price = fields.Monetary()
    partner_id = fields.Many2one("res.partner")
    shelf_id = fields.Many2one("fix.shelf", required=True)

    def action_launch(self, reason: str):
        publish(
            self.env,
            "widget.launched",
            "fix.widget",
            self.id,
            {
                "name": self.name,
                "note": self.note,
                "qty": self.qty,
                "price": float(self.price),
                "partner": self.partner_id.name,
                "partner_id": self.partner_id.id,
                "shelf_code": self.shelf_id.code,
                "shelf_id": self.shelf_id.id,
                "reason": reason,
                "launched_at": fields.Datetime.now().isoformat(),
                "tags": [t.name for t in self.tag_ids],
                "bulk": self.qty > 10,
                "who": self.env.user.name,
            },
        )
        self._emit("widget.archived", self)
        kind = "widget.flagged" if self.qty else "widget.cleared"
        publish(self.env, kind, "fix.widget", self.id, {"qty": self.qty})
        publish(self.env, f"widget.{reason}", "fix.widget", self.id, {})

    def _emit(self, event_type, rec):
        publish(self.env, event_type, "fix.widget", rec.id, {"widget_id": rec.id})


class Shelf(models.Model):
    _name = "fix.shelf"

    code = fields.Char(required=True)
"""


@pytest.fixture
def synthetic_addons(tmp_path) -> Path:
    module = tmp_path / "addons" / "domain" / "z_test" / "cd_widget"
    (module / "models").mkdir(parents=True)
    (module / "__manifest__.py").write_text("{'name': 'Widget'}\n", encoding="utf-8")
    (module / "models" / "widget.py").write_text(textwrap.dedent(SYNTHETIC_MODEL), encoding="utf-8")
    tests = module / "tests"
    tests.mkdir()
    (tests / "test_widget.py").write_text(
        "publish(env, 'test.only_event', 'x', 1, {})\n", encoding="utf-8"
    )
    return tmp_path / "addons"


def test_guard_detects_a_new_unregistered_publish(synthetic_addons, registry):
    result = event_publishers.scan_publishers(synthetic_addons)
    found = set(result.sites)
    # direct, wrapper-forwarded and literal-variable names; tests/ are not product code
    assert found == {"widget.launched", "widget.archived", "widget.flagged", "widget.cleared"}
    registered = {e["event_type"] for e in registry["events"]}
    assert sorted(found - registered) == sorted(found)
    assert any("f'widget.{reason}'" in c for c in result.composed)

    audit = verify_event_registry.audit_registry(addons_dir=synthetic_addons, probe=_no_brokers)
    check = next(c for c in audit["checks"] if c["check"] == "published_event_types_registered")
    assert check["status"] == verify_event_registry.FAILED
    assert "widget.launched" in audit["published_but_unregistered_list"]


def test_generator_derives_closed_typed_payload_schemas(synthetic_addons, tmp_path):
    events_dir = tmp_path / "events"
    events_dir.mkdir()
    outputs, report = generate_event_schemas.build_contracts(synthetic_addons, events_dir)
    assert report["registered"] == 4
    launched = outputs[events_dir / "widget_launched.json"]
    payload = launched["properties"]["payload"]
    assert payload["additionalProperties"] is False
    assert payload["required"][:3] == ["name", "note", "qty"]
    props = payload["properties"]
    assert props["name"] == {"type": "string"}  # required Char
    assert props["note"] == {"type": ["string", "boolean"]}  # Odoo reads unset Char as False
    assert props["qty"] == {"type": "integer"}
    assert props["price"] == {"type": "number"}
    assert props["partner"] == {"type": ["string", "boolean"]}  # through an optional m2o
    assert props["partner_id"] == {"type": ["integer", "boolean"]}
    assert props["shelf_code"] == {"type": "string"}  # required m2o -> required Char
    assert props["shelf_id"] == {"type": "integer"}
    assert props["reason"] == {"type": "string"}  # from the parameter annotation
    assert props["launched_at"] == {"type": "string"}
    assert props["tags"] == {"type": "array"}
    assert props["bulk"] == {"type": "boolean"}
    assert props["who"] == {"type": ["string", "boolean"]}
    assert launched["x-owner-module"] == "cd_widget"
    assert launched["properties"]["event_type"]["const"] == "widget.launched"

    archived = outputs[events_dir / "widget_archived.json"]["properties"]["payload"]
    assert archived["properties"] == {"widget_id": {"type": "integer"}}

    reg = outputs[events_dir / "master-event-registry.json"]
    assert reg["total_registered_events"] == 4
    assert {e["kafka_topic"] for e in reg["events"]} == {"fix.events.widget"}
    assert all(e["schema_version"] == "1.0.0" for e in reg["events"])


def test_generator_corrects_a_curated_contract_that_contradicts_the_code(
    synthetic_addons, tmp_path
):
    events_dir = tmp_path / "events"
    events_dir.mkdir()
    curated = {
        "title": "widget.archived",
        "description": "Widget archived (curated).",
        "properties": {"payload": {"properties": {"widget_ref": {"type": "string"}}}},
    }
    (events_dir / "widget_archived.json").write_text(json.dumps(curated), encoding="utf-8")
    (events_dir / "master-event-registry.json").write_text(
        json.dumps({"events": [{"event_type": "widget.archived", "schema_version": "1.2.0"}]}),
        encoding="utf-8",
    )
    (events_dir / "ghost_event.json").write_text(json.dumps({"title": "ghost.event"}), "utf-8")

    outputs, report = generate_event_schemas.build_contracts(synthetic_addons, events_dir)
    assert report["curated_corrected"] == ["widget.archived"]
    assert report["planned"] == ["ghost_event.json"]  # no code publishes it
    fixed = outputs[events_dir / "widget_archived.json"]
    assert fixed["description"].startswith("Widget archived (curated).")
    assert fixed["x-curated-description"] == "Widget archived (curated)."
    entry = next(
        e
        for e in outputs[events_dir / "master-event-registry.json"]["events"]
        if e["event_type"] == "widget.archived"
    )
    assert entry["schema_version"] == "2.0.0"  # breaking correction


@pytest.mark.parametrize(
    ("old", "new", "expected"),
    [
        ({"properties": {"a": {"type": "string"}}, "required": ["a"]}, None, "1.4.2"),
        (
            {"properties": {"a": {"type": "string"}}, "required": ["a"]},
            {
                "properties": {"a": {"type": "string"}, "b": {"type": "integer"}},
                "required": ["a", "b"],
            },
            "1.5.0",
        ),
        (
            {"properties": {"a": {"type": "string"}, "b": {"type": "integer"}}, "required": ["a"]},
            {"properties": {"a": {"type": "string"}}, "required": ["a"]},
            "2.0.0",
        ),
        (
            {"properties": {"a": {"type": "string"}}, "required": ["a"]},
            {"properties": {"a": {"type": "integer"}}, "required": ["a"]},
            "2.0.0",
        ),
    ],
)
def test_schema_version_follows_semver_on_payload_change(old, new, expected):
    assert generate_event_schemas.bump_version("1.4.2", old, new or old) == expected
