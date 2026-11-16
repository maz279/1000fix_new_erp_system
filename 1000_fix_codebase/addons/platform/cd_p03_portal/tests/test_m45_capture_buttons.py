# M45 Enterprise Assets & Test Equipment: every sub-module page captures each
# record it covers (capture audit 2026-11-16).
#
# Before (HEAD 48184ca8), evaluated with the engine's own fregCreate/fregPanels:
#   * every page had a "+ New", but page 2 listed transfers with no transfer
#     capture and no way to hand an item back with its condition; page 4 listed
#     out-of-service holds with no way to raise one; calibration profiles,
#     impact assessments and alerts sat on NO page;
#   * the spec's class (FR-EAM-002/003), branch profile (FR-EAM-009),
#     reference standard (FR-EAM-028), recall (FR-EAM-029), PM plan
#     (FR-EAM-032), loss report (FR-EAM-040), blind count (FR-EAM-038) and
#     retirement (FR-EAM-042/043) had no record at all, and the equipment form
#     captured no identity (manufacturer, model, serial, tag, warranty);
#   * the fitness gate demanded a calibration of EVERY item, so a tool or a
#     laptop (registered on purpose, spec §4) could never be issued.
#
# Evaluated as the browser evaluates it: node runs the engine's own fregCreate
# and fregPanels over the real registry fragments.
from __future__ import annotations

import ast
import importlib.util
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "static" / "src"
CONTROLLER = HERE.parent / "controllers" / "a07" / "m45.py"
WRITABLE_FILE = HERE.parent / "controllers" / "a07" / "writable.py"
EQUIPMENT = HERE.parents[2] / "domain" / "f_asset_facilities" / "cd_equipment_register"

_spec = importlib.util.spec_from_file_location(
    "_estate_pages", HERE / "test_estate_module_pages.py"
)
_estate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_estate)

PROBE = """
import * as M from './meta.mjs';
const { P03_MODULES, P03_MODULE_CREATE, P03_FORM_CHIPS, P03_DATA_SCREENS, P03_REPORT_ROUTES } = M;
function %(create)s
function %(panels)s
const mod = P03_MODULES.M45;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M45', map);
  const panels = fregPanels('M45', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M45:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M45.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: own || null, forms,
    reports: panels.reports.map((r) => ({ r, route: P03_REPORT_ROUTES['M45:' + r] || null })) };
});
console.log(JSON.stringify({ subs, forms: mod.forms,
  labelled: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => id.startsWith('M45-')).map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create, report: c.report || null,
    tabs: (c.tabs || []).map((t) => t.id),
    sectionTabs: (c.sections || []).map((s) => s.tab || null),
    saveAction: c.saveAction || null,
    actions: (c.actions || []).map((a) => ({ m: a.m, kwargs: (a.asks || []).map((q) => q.kwarg).concat(a.kwarg ? [a.kwarg] : []) })),
    cols: c.cols || [],
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({
      name: f.name, readonly: !!f.readonly, required: !!f.required })) }])) }));
"""


@pytest.fixture(scope="module")
def m45(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m45_capture")
    for area in sorted(d for d in SRC.iterdir() if re.fullmatch(r"a\d\d", d.name)):
        (tmp / area.name).mkdir()
        for js in area.glob("*.js"):
            (tmp / area.name / (js.stem + ".mjs")).write_text(
                js.read_text(encoding="utf-8"), "utf-8"
            )
    meta = (SRC / "p03_modules_meta.js").read_text(encoding="utf-8")
    (tmp / "meta.mjs").write_text(_estate.IMPORT.sub(r'from "\1.mjs"', meta), "utf-8")
    engine = (SRC / "p03_workspace.js").read_text(encoding="utf-8").replace("\r\n", "\n")
    probe = tmp / "probe.mjs"
    probe.write_text(
        PROBE
        % {
            "create": _estate._method(engine, "fregCreate(mid, map)"),
            "panels": _estate._method(engine, "fregPanels(mid, mod, map)"),
        },
        "utf-8",
    )
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our own probe file
        [node, str(probe)], capture_output=True, encoding="utf-8", check=True, timeout=120
    )
    return json.loads(out.stdout)


def _assigned(path, name):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == name
        ):
            return node.value
    raise AssertionError("%s defines no %s" % (path.name, name))


def _surfaces():
    out = {}
    value = _assigned(CONTROLLER, "SURFACES")
    for key, conf in zip(value.keys, value.values, strict=True):
        acts = set()
        for k, v in zip(conf.keys, conf.values, strict=True):
            if ast.literal_eval(k) == "actions" and isinstance(v, ast.Set):
                acts = {ast.literal_eval(e) for e in v.elts}
        out[ast.literal_eval(key)] = acts
    return out


def _writable():
    out = {}
    value = _assigned(WRITABLE_FILE, "WRITABLE")
    for key, val in zip(value.keys, value.values, strict=True):
        names = set()
        if isinstance(val, ast.Call) and val.args:
            names = set(ast.literal_eval(val.args[0]))
        out[ast.literal_eval(key)] = names
    return out


def _model_methods():
    """{model: {method names}} defined in cd_equipment_register's model files."""
    out = {}
    for path in (EQUIPMENT / "models").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for cls in (n for n in tree.body if isinstance(n, ast.ClassDef)):
            names = set()
            for stmt in cls.body:
                if (
                    isinstance(stmt, ast.Assign)
                    and isinstance(stmt.targets[0], ast.Name)
                    and stmt.targets[0].id in ("_name", "_inherit")
                    and isinstance(stmt.value, ast.Constant)
                ):
                    names.add(stmt.value.value)
            methods = {f.name for f in cls.body if isinstance(f, ast.FunctionDef)}
            for name in names:
                out.setdefault(name, set()).update(methods)
    return out


# What each page lets a person capture: its own "+ New" first, then every
# other record the page covers, by form screen.
CAPTURES = {
    "1": [
        "M45-form-equipment",
        "M45-form-category",
        "M45-form-branch-profile",
        "M45-form-writeoff",
    ],
    "2": ["M45-form-issue", "M45-form-return", "M45-form-transfer"],
    "3": ["M45-form-kit"],
    "4": [
        "M45-form-calibration",
        "M45-form-profile",
        "M45-form-standard",
        "M45-form-recall",
        "M45-form-oos",
    ],
    "5": ["M45-form-pm", "M45-form-pm-plan", "M45-form-oos"],
    "6": ["M45-form-usage"],
    "7": [
        "M45-form-audit",
        "M45-form-verification",
        "M45-form-loss",
        "M45-form-writeoff",
        "M45-form-retirement",
    ],
}

RECORDS = {
    "1": "fix.equipment",
    "2": "fix.equipment.issue",
    "3": "fix.equipment.kit",
    "4": "fix.calibration",
    "5": "fix.equipment.pm",
    "6": "fix.equipment.usage",
    "7": "fix.equipment.audit",
}

# lists a page must show although nobody captures them there
LISTED = {
    "4": {"M45-impacts", "M45-alerts", "M45-calibration"},
    "6": {"M45-impacts", "M45-retro"},
    "2": {"M45-alerts"},
}

NEW_MODELS = (
    "fix.equipment.category",
    "fix.branch.equipment.profile",
    "fix.equipment.pm.plan",
    "fix.equipment.loss",
    "fix.equipment.audit",
    "fix.equipment.retirement",
)

# What a form must never let a person type: states, stamps and derived figures.
NEVER_TYPED = {
    "fix.equipment": {
        "operational_status",
        "measurement_critical",
        "classification",
        "calibration_state",
        "calibration_recall_note",
        "retired_on",
        "retired_by_id",
        "warranty_active",
    },
    "fix.equipment.loss": {
        "state",
        "reported_by_id",
        "reported_on",
        "custodian_at_loss_id",
        "value_impact",
        "decided_by_id",
        "decided_on",
        "decision_note",
        "repair_job_id",
    },
    "fix.equipment.audit": {
        "state",
        "expected_count",
        "found_count",
        "missing_count",
        "unexpected_count",
        "variance_value",
        "completed_by_id",
        "completed_on",
    },
    "fix.equipment.retirement": {"state", "requested_by_id", "disposed_by_id", "disposed_on"},
    "fix.equipment.pm.plan": {"next_due", "open_jobs"},
    "fix.equipment.pm": {"plan_id", "state", "done_on"},
    "fix.branch.equipment.profile": {
        "held_count",
        "fit_count",
        "shortfall",
        "capability_exception",
    },
}


def _sub(m45, no):
    return next(s for s in m45["subs"] if s["no"] == no)


def test_every_page_is_classified(m45):
    assert sorted(s["no"] for s in m45["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m45, no):
    sub = _sub(m45, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]}
    missing = [form for form in [own, *others] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)


@pytest.mark.parametrize("no", sorted(RECORDS, key=int))
def test_each_page_lists_its_own_record(m45, no):
    assert _sub(m45, no)["model"] == RECORDS[no]


@pytest.mark.parametrize("no", sorted(LISTED, key=int))
def test_system_raised_lists_sit_on_their_page(m45, no):
    assert LISTED[no] <= set(_sub(m45, no)["screens"])


def test_each_captured_record_is_listed_on_its_page(m45):
    for sub in m45["subs"]:
        listed = {m45["screens"][s]["model"] for s in sub["screens"] if s in m45["screens"]}
        for f in sub["forms"]:
            assert f["model"] in listed, "page %s captures %s but lists none" % (
                sub["no"],
                f["model"],
            )


def test_every_working_screen_sits_on_a_page(m45):
    placed = {sid for s in m45["subs"] for sid in s["screens"]}
    placed |= {r["route"] for s in m45["subs"] for r in s["reports"]}
    orphans = [
        sid
        for sid, cfg in m45["screens"].items()
        if cfg["kind"] in ("model_list", "table_report")
        and sid not in placed
        and not sid.startswith("M45-rpt-")
    ]
    assert not orphans, orphans


def test_every_report_chip_routes(m45):
    for sub in m45["subs"]:
        for r in sub["reports"]:
            assert r["route"] in m45["screens"], (sub["no"], r)


def test_every_screen_on_a_page_has_a_navigation_label(m45):
    """A list on a page but in no navigation group shows as its raw id."""
    labelled = set(m45["labelled"])
    unlabelled = sorted(
        sid
        for sub in m45["subs"]
        for sid in sub["screens"]
        if sid in m45["screens"]
        and m45["screens"][sid]["kind"] == "model_list"
        and sid not in labelled
    )
    assert not unlabelled, unlabelled


def test_every_served_action_exists_on_its_model():
    methods = _model_methods()
    for model, acts in _surfaces().items():
        missing = acts - methods.get(model, set())
        # the approval actions come from cd_workflow_engine's mixin
        missing -= {"action_request_approval", "action_recall_approval"}
        assert not missing, "%s serves %s, which the model lacks" % (model, sorted(missing))


def test_every_list_action_is_served(m45):
    surfaces = _surfaces()
    for sid, cfg in m45["screens"].items():
        if cfg["kind"] != "model_list" or not cfg["actions"]:
            continue
        if cfg["model"] not in surfaces:
            continue  # served by its owner's controller (fix.asset.alert: the spine)
        served = surfaces[cfg["model"]]
        for act in cfg["actions"]:
            assert act["m"] in served, "%s offers %s, not served" % (sid, act["m"])


def test_every_save_action_is_served(m45):
    surfaces = _surfaces()
    for sid, cfg in m45["screens"].items():
        act = cfg["saveAction"]
        if act:
            assert act["method"] in surfaces.get(cfg["model"], set()), (sid, act["method"])


@pytest.mark.parametrize("model", NEW_MODELS)
def test_new_registers_are_served_and_whitelisted(m45, model):
    assert model in _surfaces()
    forms = [
        c for c in m45["screens"].values() if c["kind"] == "model_form" and c["model"] == model
    ]
    assert forms, "%s has no workspace form" % model
    typed = {f["name"] for c in forms for f in c["fields"] if not f["readonly"]}
    # a form's lines grid is written through its one2many
    assert _writable()[model] - {"line_ids"} == typed


@pytest.mark.parametrize("model", sorted(NEVER_TYPED))
def test_stamps_and_derived_figures_are_never_typed(model):
    leaked = _writable().get(model, set()) & NEVER_TYPED[model]
    assert not leaked, (model, sorted(leaked))


def test_the_equipment_form_captures_identity_and_class(m45):
    form = m45["screens"]["M45-form-equipment"]
    names = {f["name"] for f in form["fields"]}
    wanted = {
        "category_id",
        "asset_tag",
        "manufacturer",
        "model_name",
        "serial_no",
        "supplier_id",
        "warranty_until",
        "acquisition_ref",
        "expected_life_months",
    }
    assert wanted <= names
    assert wanted <= _writable()["fix.equipment"]


@pytest.mark.parametrize("sid", ["M45-form-equipment", "M45-form-calibration", "M45-form-loss"])
def test_long_forms_are_tabbed(m45, sid):
    """Project standard: a form over 15 fields is partitioned into tabs."""
    form = m45["screens"][sid]
    assert len(form["fields"]) > 15
    assert form["tabs"] and all(t in form["tabs"] for t in form["sectionTabs"])


def test_calibration_names_its_reference_standard(m45):
    names = {f["name"] for f in m45["screens"]["M45-form-calibration"]["fields"]}
    assert {"standard_equipment_id", "provider_id", "accreditation_ref"} <= names


def test_return_and_recall_pick_an_existing_record(m45):
    ret = m45["screens"]["M45-form-return"]["saveAction"]
    assert ret["method"] == "action_return"
    assert ret["kwargs"] == {"condition": "return_condition", "detail": "condition_in"}
    rec = m45["screens"]["M45-form-recall"]["saveAction"]
    assert rec["method"] == "action_recall_calibration"


def test_new_models_are_secured():
    acl = (EQUIPMENT / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    rules = (EQUIPMENT / "security" / "fix_m45_ops_rules.xml").read_text(encoding="utf-8")
    for model in (*NEW_MODELS, "fix.equipment.audit.line"):
        xmlid = "model_" + model.replace(".", "_")
        rows = [r.split(",") for r in acl.splitlines() if (",%s," % xmlid) in r]
        assert rows, model
        assert 'ref="%s"' % xmlid in rules, "%s has no company rule" % model
        if model != "fix.equipment.audit.line":
            # nobody deletes a register row
            assert all(r[-1].strip() == "0" for r in rows), model


def test_the_new_file_loads_after_the_models_it_extends():
    init = (EQUIPMENT / "models" / "__init__.py").read_text(encoding="utf-8")
    for base in ("fix_equipment,", "fix_equipment_ops"):
        assert init.index(base) < init.index("fix_equipment_capture"), base
