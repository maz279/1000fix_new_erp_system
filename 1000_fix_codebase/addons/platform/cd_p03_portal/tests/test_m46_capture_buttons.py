# M46 Fleet & Vehicles: every sub-module page captures each record it covers
# (capture audit 2026-11-17).
#
# Before (HEAD 48184ca8), evaluated with the engine's own fregCreate/fregPanels:
#   * page 1 Vehicle Register offered "+ New Vehicle", whose Model is
#     required, but no way to add a Vehicle Model or Make (fix_real holds 0
#     models: the first vehicle could not be registered from the page);
#   * pages 2 Statutory Documents, 4 Assignment & Pool and 7 Telematics offered
#     no chip at all; page 2 listed off-road records with no capture;
#   * no document renewal (FR-FLT-013 P0 / FR-FLT-014), no defect classified
#     safety-critical or deferrable (FR-FLT-025 P0), no telematics device
#     register (FR-FLT-035 P0: page 7 recorded a free-text label on a
#     snapshot), no traffic fine (FR-FLT-043, BRU-FLT-16), no ownership basis
#     (FR-FLT-003 P0) and no service execution - garage, work, invoice, next
#     due (FR-FLT-026/027 P0) - existed.
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
CONTROLLER = HERE.parent / "controllers" / "a07" / "m46.py"
WRITABLE_FILE = HERE.parent / "controllers" / "a07" / "writable.py"
FLEET = HERE.parents[2] / "domain" / "f_asset_facilities" / "cd_vehicle_ext"
BRIDGE = HERE.parents[2] / "domain" / "f_asset_facilities" / "cd_asset_finance_hse_bridge"

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
const mod = P03_MODULES.M46;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M46', map);
  const panels = fregPanels('M46', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M46:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M46.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: own || null, forms,
    reports: panels.reports.map((r) => ({ r, route: P03_REPORT_ROUTES['M46:' + r] || null })) };
});
console.log(JSON.stringify({ subs, forms: mod.forms,
  labelled: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => id.startsWith('M46-')).map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create, report: c.report || null,
    tabs: (c.tabs || []).length,
    actions: (c.actions || []).map((a) => ({ m: a.m, kwargs: (a.asks || []).map((q) => q.kwarg).concat(a.kwarg ? [a.kwarg] : []) })),
    cols: c.cols || [],
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({
      name: f.name, readonly: !!f.readonly, required: !!f.required })) }])) }));
"""


@pytest.fixture(scope="module")
def m46(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m46_capture")
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
    """{model: {method names}} defined in cd_vehicle_ext's model files."""
    out = {}
    for path in (FLEET / "models").glob("*.py"):
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
    "1": ["M46-form-vehicle", "M46-form-model", "M46-form-brand"],
    "2": ["M46-form-document", "M46-form-renewal", "M46-form-offroad"],
    "3": ["M46-form-driver", "M46-form-penalty"],
    "4": ["M46-form-assignment"],
    "5": ["M46-form-check", "M46-form-defect", "M46-form-pm"],
    "6": ["M46-form-fuel"],
    "7": ["M46-form-device", "M46-form-telemetry"],
    "8": ["M46-form-accident", "M46-form-penalty"],
}

RECORDS = {
    "1": "fleet.vehicle",
    "2": "fix.vehicle.document",
    "3": "fix.driver",
    "4": "fix.vehicle.assignment",
    "5": "fix.vehicle.check",
    "6": "fix.vehicle.fuel",
    "7": "fix.telematics.device",
    "8": "fix.vehicle.accident",
}

NEW_MODELS = (
    "fix.vehicle.document.renewal",
    "fix.vehicle.defect",
    "fix.telematics.device",
    "fix.vehicle.penalty",
)

# What a form must never let a person type: the state, every decision stamp
# and every derived figure.
NEVER_TYPED = {
    "fix.vehicle.document.renewal": {
        "state",
        "submitted_on",
        "completed_by_id",
        "completed_on",
        "cancel_reason",
        "total_cost",
        "vehicle_id",
    },
    "fix.vehicle.defect": {
        "state",
        "raised_by_id",
        "offroad_id",
        "cleared_by_id",
        "cleared_on",
        "clear_note",
        "clear_check_id",
    },
    "fix.telematics.device": {"state", "removed_on", "retired", "health_state", "last_report_at"},
    "fix.vehicle.penalty": {
        "state",
        "recorded_by_id",
        "recovery_decision",
        "decision_reason",
        "decided_by_id",
        "decided_on",
    },
    "fix.vehicle.pm": {"state", "done_on", "done_by_id", "next_pm_id"},
}

# a system-raised list: what the scheduled checks found (create: false)
NOT_A_PAGE = {"M46-alerts"}


def _sub(m46, no):
    return next(s for s in m46["subs"] if s["no"] == no)


def test_every_page_is_classified(m46):
    assert sorted(s["no"] for s in m46["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m46, no):
    sub = _sub(m46, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]}
    missing = [form for form in [own, *others] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)


@pytest.mark.parametrize("no", sorted(RECORDS, key=int))
def test_each_page_lists_its_own_record(m46, no):
    assert _sub(m46, no)["model"] == RECORDS[no]


def test_each_captured_record_is_listed_on_its_page(m46):
    for sub in m46["subs"]:
        listed = {m46["screens"][s]["model"] for s in sub["screens"] if s in m46["screens"]}
        for f in sub["forms"]:
            assert f["model"] in listed, "page %s captures %s but lists none" % (
                sub["no"],
                f["model"],
            )


def test_every_working_screen_sits_on_a_page(m46):
    placed = {sid for s in m46["subs"] for sid in s["screens"]}
    placed |= {r["route"] for s in m46["subs"] for r in s["reports"]}
    orphans = [
        sid
        for sid, cfg in m46["screens"].items()
        if cfg["kind"] in ("model_list", "table_report")
        and sid not in placed
        and sid not in NOT_A_PAGE
        and not sid.startswith("M46-rpt-")
    ]
    assert not orphans, orphans


def test_every_screen_on_a_page_has_a_navigation_label(m46):
    labelled = set(m46["labelled"])
    unlabelled = sorted(
        sid
        for sub in m46["subs"]
        for sid in sub["screens"]
        if sid in m46["screens"]
        and m46["screens"][sid]["kind"] == "model_list"
        and sid not in labelled
    )
    assert not unlabelled, unlabelled


def test_every_served_action_exists_on_its_model():
    methods = _model_methods()
    for model, acts in _surfaces().items():
        if model not in (*NEW_MODELS, "fix.vehicle.pm", "fix.vehicle.telemetry"):
            continue
        missing = acts - methods.get(model, set())
        assert not missing, "%s serves %s, which the model lacks" % (model, sorted(missing))


def test_every_list_action_is_served(m46):
    surfaces = _surfaces()
    for sid, cfg in m46["screens"].items():
        # fix.asset.alert (M46-alerts) is served by the A07 asset spine
        if cfg["kind"] != "model_list" or not cfg["actions"] or cfg["model"] not in surfaces:
            continue
        served = surfaces[cfg["model"]]
        for act in cfg["actions"]:
            assert act["m"] in served, "%s offers %s, not served" % (sid, act["m"])


@pytest.mark.parametrize("model", NEW_MODELS)
def test_new_registers_are_served_and_whitelisted(m46, model):
    assert model in _surfaces()
    forms = [
        c for c in m46["screens"].values() if c["kind"] == "model_form" and c["model"] == model
    ]
    assert forms, "%s has no workspace form" % model
    typed = {f["name"] for c in forms for f in c["fields"] if not f["readonly"]}
    assert _writable()[model] == typed


@pytest.mark.parametrize("model", sorted(NEVER_TYPED))
def test_stamps_and_derived_figures_are_never_typed(model):
    leaked = _writable().get(model, set()) & NEVER_TYPED[model]
    assert not leaked, (model, sorted(leaked))


def test_long_forms_are_tabbed(m46):
    """AGENTS.md: a form of more than 15 fields is split into tabs."""
    long_flat = [
        sid
        for sid, c in m46["screens"].items()
        if c["kind"] == "model_form" and len(c["fields"]) > 15 and not c["tabs"]
    ]
    assert not long_flat, long_flat


def test_the_vehicle_form_records_its_ownership_basis(m46):
    names = {f["name"] for f in m46["screens"]["M46-form-vehicle"]["fields"]}
    want = {"fix_ownership_basis", "fix_contract_ref", "fix_contract_end"}
    assert want <= names
    assert want <= _writable()["fleet.vehicle"]


def test_the_service_form_records_its_execution(m46):
    names = {f["name"] for f in m46["screens"]["M46-form-pm"]["fields"]}
    want = {"provider_id", "work_performed", "invoice_ref", "next_due_date", "next_due_odometer"}
    assert want <= names
    assert want <= _writable()["fix.vehicle.pm"]


def test_a_snapshot_names_its_registered_device(m46):
    names = {f["name"] for f in m46["screens"]["M46-form-telemetry"]["fields"]}
    assert "device_id" in names and "device_id" in _writable()["fix.vehicle.telemetry"]


def test_new_models_are_secured():
    acl = (FLEET / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    rules = (FLEET / "security" / "fix_vehicle_ops_rules.xml").read_text(encoding="utf-8")
    for model in NEW_MODELS:
        xmlid = "model_" + model.replace(".", "_")
        rows = [r.split(",") for r in acl.splitlines() if (",%s," % xmlid) in r]
        assert rows, model
        assert all(r[-1].strip() == "0" for r in rows), "%s: nobody deletes" % model
        plain = [r for r in rows if r[3] == "base.group_user"]
        # any employee reports a defect (spec §13 R10-R12/R16); the rest is
        # the Fleet Officer's, and a plain employee only reads it
        want = ["1", "1", "1", "0"] if model == "fix.vehicle.defect" else ["1", "0", "0", "0"]
        assert plain and plain[0][4:8] == want, model
        assert 'ref="%s"' % xmlid in rules, "%s has no company rule" % model


def test_the_new_file_loads_after_the_models_it_extends():
    init = (FLEET / "models" / "__init__.py").read_text(encoding="utf-8")
    assert init.index("fix_vehicle_ops") < init.index("fix_vehicle_capture")


def test_a_vehicle_not_owned_is_not_capitalised():
    src = (BRIDGE / "models" / "m49_asset_request.py").read_text(encoding="utf-8")
    assert "fix_ownership_basis" in src
