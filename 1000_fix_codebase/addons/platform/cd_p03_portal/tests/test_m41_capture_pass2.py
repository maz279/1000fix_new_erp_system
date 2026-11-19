# M41 capture pass 2 (2026-11-19): every page captures the spec record it
# names, and each form can hold that record's fields.
#
# Pass 1 (14 Nov) gave every page a "+ New". Read against FR-WMS-001..041 and
# §10.1, at HEAD e73400f6:
#   * page 1: the warehouse form had no execution switch, cut-offs or shift
#     pattern (FR-WMS-003); bins had no coordinate, pick face, weight or volume
#     (FR-WMS-002, T-09); a lifted block left no history (FR-WMS-034);
#   * page 3: the put-away bin was typed - no strategy, rejected bins,
#     override or approval (FR-WMS-013/014, BRU-WMS-06); no exception
#     (FR-WMS-015), dock door (FR-WMS-008), handling unit (FR-WMS-010),
#     cross-dock (FR-WMS-016), return receiving (FR-WMS-017) or inspection
#     capture (FR-WMS-011);
#   * page 4: no outbound demand queue (FR-WMS-018); templates had no purpose,
#     release rule, priority or destination (FR-WMS-019);
#   * page 6: no handling unit at packing (FR-WMS-025);
#   * page 9: no count plan (FR-WMS-031), time standard or productivity
#     (FR-WMS-040).
# The engine's own fregCreate / fregPanels decide what a page offers (the
# pass-1 fixture); the forms themselves are read from the module directly.
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
JS = HERE.parent / "static" / "src" / "a06" / "m41.js"
INVENTORY = HERE.parents[2] / "domain" / "e_supply_chain" / "cd_inventory"
STRUCTURE = HERE.parents[2] / "domain" / "e_supply_chain" / "cd_wms_structure"

_spec = importlib.util.spec_from_file_location("_m41_pass1", HERE / "test_m41_capture_buttons.py")
_p1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_p1)
m41 = _p1.m41  # the pass-1 fixture: pages as the engine evaluates them

# The spec records each page must now offer, besides pass 1's.
SPEC_CAPTURES = {
    "1": ["M41-form-bin", "M41-form-zone", "M41-form-warehouse"],
    "3": [
        "M41-form-putaway",
        "M41-form-putaway-exception",
        "M41-form-dock",
        "M41-form-dock-door",
        "M15-form-receipt",
        "M16-form-inspection",
        "M41-form-hu",
        "M41-form-crossdock",
        "M41-form-return",
    ],
    "4": ["M41-form-wave", "M41-form-demand", "M41-form-template"],
    "6": ["M41-form-carton", "M41-form-stage", "M41-form-hu", "M41-form-station"],
    "9": [
        "M41-form-operative",
        "M41-form-equipment",
        "M41-form-count-plan",
        "M41-form-floor-count",
        "M41-form-time-standard",
        "M41-form-productivity-run",
    ],
}

# Fields the spec names that each form must carry: (name, typed?)
SPEC_FIELDS = {
    "M41-form-warehouse": {"wms_enabled": True, "wave_cutoffs": True, "shift_pattern": True},
    "M41-form-zone": {"zone_type": True, "ownership_class": True, "sequence": True},
    "M41-form-bin": {
        "aisle": True,
        "bay": True,
        "level": True,
        "position": True,
        "is_pick_face": True,
        "max_weight_kg": True,
        "max_volume_m3": True,
        "length_cm": True,
        "width_cm": True,
        "height_cm": True,
        "pick_sequence": False,
    },
    "M41-form-putaway": {
        "directed_bin_id": False,
        "strategy_used": False,
        "rejected_bins": False,
        "override_reason": True,
        "override_note": True,
        "override_state": False,
        "override_approved_by_id": False,
    },
    "M41-form-dock": {"door_id": True, "arrived_at": False, "unload_started_at": False},
    "M41-form-wave": {"template_id": True, "cutoff_at": True, "priority": False},
    "M41-form-template": {
        "purpose": True,
        "release_rule": True,
        "priority": True,
        "dest_location_ids": True,
        "strategy": True,
    },
    "M41-form-floor-count": {"count_type": True, "plan_id": False},
    "M41-form-hu": {"hu_type": True, "parent_id": True, "current_bin_id": False},
    "M41-form-crossdock": {"receipt_line_id": True, "wave_line_id": True, "stage_lane": True},
    "M41-form-return": {"source_type": True, "returns_bin_id": True, "disposition": True},
    "M41-form-demand": {
        "source_type": True,
        "dest_location_id": True,
        "priority": True,
        "cutoff_at": True,
    },
    "M41-form-count-plan": {"scope": True, "zone_id": True, "velocity": True},
    "M41-form-time-standard": {"seconds_per_task": True, "seconds_per_unit": True},
}

# What no form may type: the state, the evidence and what the engine decides.
NEVER_TYPED = {
    "fix.wms.putaway": {
        "state",
        "directed_bin_id",
        "strategy_used",
        "rejected_bins",
        "directed_at",
        "override_state",
        "override_by_id",
        "override_approved_by_id",
    },
    "fix.wms.handling.unit": {"state", "current_bin_id", "closed_by_id"},
    "fix.wms.crossdock": {"state", "staged_by_id", "dispatched_by_id", "load_ref", "wave_id"},
    "fix.wms.return.receipt": {"state", "received_by_id", "disposed_by_id", "putaway_id"},
    "fix.wms.outbound.demand": {"state", "wave_id"},
    "fix.wms.count.plan": {"state", "generated_by_id"},
    "fix.wms.productivity.run": {"state", "computed_by_id", "computed_at", "line_ids"},
    "fix.wms.dock": {"state", "arrived_at", "unload_started_at", "completed_at"},
    "fix.wms.wave.line": {"pick_sequence", "demand_id", "resourced_from_id"},
    "fix.wms.task": {"pick_sequence", "claimed_at"},
    "fix.wms.floor.count": {"plan_id"},
    "fix.wms.bin.block.log": {"event", "reason", "user_id"},
    "fix.wms.productivity": {"units", "tasks_completed"},
    "fix.wms.putaway.exception": {"cause"},
}

NEW_MODELS = (
    "fix.wms.bin.block.log",
    "fix.wms.dock.door",
    "fix.wms.putaway.exception",
    "fix.wms.handling.unit",
    "fix.wms.handling.unit.line",
    "fix.wms.crossdock",
    "fix.wms.return.receipt",
    "fix.wms.outbound.demand",
    "fix.wms.count.plan",
    "fix.wms.time.standard",
    "fix.wms.productivity.run",
    "fix.wms.productivity",
)


@pytest.fixture(scope="module")
def forms(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m41_pass2")
    (tmp / "m41.mjs").write_text(JS.read_text(encoding="utf-8"), "utf-8")
    probe = tmp / "probe.mjs"
    probe.write_text(
        "import * as M from './m41.mjs';\n"
        "const out = {};\n"
        "for (const [id, c] of Object.entries(M.SCREENS)) {\n"
        "  if (c.kind !== 'model_form') continue;\n"
        "  const fields = (c.sections || []).flatMap((s) => s.fields || []);\n"
        "  out[id] = { model: c.model, tabs: (c.tabs || []).map((t) => t.id),\n"
        "    sectionTabs: (c.sections || []).map((s) => s.tab || null),\n"
        "    fields: fields.map((f) => ({ name: f.name, readonly: !!f.readonly })),\n"
        "    lines: c.lines ? { field: c.lines.field, ro: !!c.lines.readonlyGrid,\n"
        "      fields: (c.lines.fields || []).map((f) => f.name) } : null,\n"
        "    save: c.saveAction ? c.saveAction : null };\n"
        "}\n"
        "console.log(JSON.stringify(out));\n",
        "utf-8",
    )
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our own probe file
        [node, str(probe)], capture_output=True, encoding="utf-8", check=True, timeout=60
    )
    return json.loads(out.stdout)


@pytest.mark.parametrize("no", sorted(SPEC_CAPTURES, key=int))
def test_each_page_offers_the_spec_records(m41, no):
    sub = _p1._sub(m41, no)
    chips = {f["id"] for f in sub["forms"] if f["opens"]}
    if sub["create"]:
        chips.add(sub["create"])
    missing = [f for f in SPEC_CAPTURES[no] if f not in chips]
    assert not missing, "page %s cannot capture %s" % (no, missing)


@pytest.mark.parametrize("sid", sorted(SPEC_FIELDS))
def test_each_form_holds_the_spec_fields(forms, sid):
    cfg = forms[sid]
    have = {f["name"]: not f["readonly"] for f in cfg["fields"]}
    for name, typed in SPEC_FIELDS[sid].items():
        assert name in have, "%s has no %s" % (sid, name)
        assert have[name] == typed, "%s: %s should be %s" % (
            sid,
            name,
            "typed" if typed else "read-only",
        )


def test_long_forms_are_tabbed(forms):
    """Workspace standard: a form of more than 15 fields is partitioned in tabs."""
    for sid, cfg in forms.items():
        if not sid.startswith("M41-") or len(cfg["fields"]) <= 15:
            continue
        assert cfg["tabs"], "%s has %d fields and no tabs" % (sid, len(cfg["fields"]))
        assert all(t in cfg["tabs"] for t in cfg["sectionTabs"]), sid


def test_the_handling_unit_shows_its_contents_and_the_run_its_rows(forms):
    hu, run = forms["M41-form-hu"], forms["M41-form-productivity-run"]
    assert hu["lines"] and hu["lines"]["field"] == "line_ids" and not hu["lines"]["ro"]
    assert {"part_id", "qty", "lot_id"} <= set(hu["lines"]["fields"])
    assert run["lines"] and run["lines"]["ro"], "productivity is measured, never typed"


def test_the_exception_form_runs_the_workflow(forms, m41):
    cfg = forms["M41-form-putaway-exception"]
    assert cfg["save"]["method"] == "action_report_exception"
    assert set(cfg["save"]["kwargs"]) == {"cause", "note"}
    assert "action_report_exception" in _p1._surfaces()["fix.wms.putaway"]
    typed = {f["name"] for f in m41["screens"]["M41-form-putaway-exception"]["fields"]}
    assert typed >= {"exception_cause_entry", "exception_note_entry"}


def test_the_state_and_evidence_are_never_typed():
    writable = _p1._writable()
    for model, fields in NEVER_TYPED.items():
        leaked = writable.get(model, set()) & fields
        assert not leaked, (model, sorted(leaked))


@pytest.mark.parametrize("model", NEW_MODELS)
def test_new_registers_are_served_and_secured(model):
    assert model in _p1._surfaces(), "%s is not served" % model
    acl = (INVENTORY / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    rules = (INVENTORY / "security" / "fix_wms_spec_rules.xml").read_text(encoding="utf-8")
    xmlid = "model_" + model.replace(".", "_")
    rows = [r.split(",") for r in acl.splitlines() if (",%s," % xmlid) in r]
    assert rows, model
    plain = [r for r in rows if r[3] == "base.group_user"]
    assert plain and plain[0][4:8] == ["1", "0", "0", "0"], model
    if model != "fix.wms.handling.unit.line":  # an open unit's content line may be removed
        assert all(r[-1].strip() == "0" for r in rows), "%s may be deleted" % model
    assert 'ref="%s"' % xmlid in rules, "%s has no company rule" % model


def test_load_order():
    init = (INVENTORY / "models" / "__init__.py").read_text(encoding="utf-8")
    assert init.index("fix_wms_ops_floor,") < init.index("fix_wms_ops_spec,")
    sinit = (STRUCTURE / "models" / "__init__.py").read_text(encoding="utf-8")
    assert sinit.index("import fix_wms_structure") < sinit.index("import fix_wms_layout")
    manifest = (INVENTORY / "__manifest__.py").read_text(encoding="utf-8")
    assert "security/fix_wms_spec_rules.xml" in manifest
    assert "data/fix_wms_spec_data.xml" in manifest
