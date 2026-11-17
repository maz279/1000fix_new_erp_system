# M55 Time, Attendance & Workforce Scheduling: every sub-module page captures
# each record it covers (capture audit 2026-11-17).
#
# Before (HEAD c5feece6), evaluated with the engine's own fregCreate/fregPanels:
#   * page 2 (Working Time & OT) offered "+ New" ATTENDANCE RECORD, page 1's
#     record; the overtime request (BRU-WFM-02 pre-approval), night-work
#     consent and working-time rule lists sat on no page;
#   * page 7 (Availability Publication) offered "+ New" ROSTER SLOT, page 5's
#     record; the publication list sat on no page and there was no capacity
#     forecast (FR-WFM-048/049 P1);
#   * page 9 (Timesheets) offered "+ New" ATTENDANCE RECORD: there was no
#     timesheet line to allocate time to a project, contract or cost centre
#     (FR-WFM-050);
#   * page 6 (On-Call) had no chip and no callout record (FR-WFM-044 "with
#     allowance and callout recording");
#   * page 1 listed biometric devices with no chip, page 4 had no Holiday chip,
#     page 3 had no leave type (FR-WFM-026), and nine lists (consent, webhook
#     events, decisions, overtime, night work, rule versions, adjustments,
#     accrual, publications, roster changes) sat on no page.
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
CONTROLLER = HERE.parent / "controllers" / "a09" / "m55.py"
WRITABLE_FILE = HERE.parent / "controllers" / "a09" / "writable.py"
ATT = HERE.parents[2] / "domain" / "h_people" / "cd_attendance"

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
const mod = P03_MODULES.M55;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M55', map);
  const panels = fregPanels('M55', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M55:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M55.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: own || null, forms,
    reports: panels.reports.map((r) => ({ r, route: P03_REPORT_ROUTES['M55:' + r] || null })) };
});
const screen = (c) => ({
    kind: c.kind, model: c.model || null, create: c.create, report: c.report || null,
    tabs: (c.tabs || []).length,
    actions: (c.actions || []).map((a) => ({ m: a.m, kwargs: (a.asks || []).map((q) => q.kwarg).concat(a.kwarg ? [a.kwarg] : []) })),
    cols: c.cols || [],
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({
      name: f.name, readonly: !!f.readonly, required: !!f.required })) });
console.log(JSON.stringify({ subs, forms: mod.forms,
  formModels: Object.fromEntries(Object.entries(M.P03_FORM_MODELS || {}).filter(([k]) => k.startsWith('M55:'))),
  labelled: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => id.startsWith('M55-')).map(([id, c]) => [id, screen(c)])) }));
"""


@pytest.fixture(scope="module")
def m55(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m55_capture")
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


def _model_classes():
    """{model: ({fields}, {methods})} defined or extended in cd_attendance."""
    out = {}
    for path in (ATT / "models").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for cls in (n for n in tree.body if isinstance(n, ast.ClassDef)):
            names, flds = set(), set()
            for stmt in cls.body:
                if not (isinstance(stmt, ast.Assign) and isinstance(stmt.targets[0], ast.Name)):
                    continue
                target = stmt.targets[0].id
                if target in ("_name", "_inherit") and isinstance(stmt.value, ast.Constant):
                    names.add(stmt.value.value)
                elif (
                    isinstance(stmt.value, ast.Call)
                    and isinstance(stmt.value.func, ast.Attribute)
                    and getattr(stmt.value.func.value, "id", "") == "fields"
                ):
                    flds.add(target)
            methods = {f.name for f in cls.body if isinstance(f, ast.FunctionDef)}
            for name in names:
                entry = out.setdefault(name, (set(), set()))
                entry[0].update(flds)
                entry[1].update(methods)
    return out


# What each page lets a person capture: its own "+ New" first, then every
# other record the page covers, by form screen.
CAPTURES = {
    "1": ["M55-form-exception", "M55-form-bio", "M55-form-bio-consent"],
    "2": ["M55-form-ot", "M55-form-night", "M55-form-wt-rule"],
    "3": ["M55-form-leave", "M55-form-leave-type"],
    "4": ["M55-form-holiday"],
    "5": ["M55-form-roster", "M55-form-shift", "M55-form-roster-change"],
    "6": ["M55-form-oncall", "M55-form-callout"],
    "7": ["M55-form-publication", "M55-form-capacity", "M55-form-roster-change"],
    "8": ["M55-form-attendance-lock", "M55-form-exception"],
    "9": ["M55-form-timesheet", "M55-form-exception"],
}

# Lists that existed but sat on no page.
PLACED = {
    "1": ["M55-bio-consent", "M55-hook-events"],
    "2": ["M55-ot", "M55-night", "M55-wt-rules"],
    "3": ["M55-accrual", "M55-leave-types"],
    "5": ["M55-roster-changes"],
    "6": ["M55-callouts"],
    "7": ["M55-publications", "M55-capacity"],
    "8": ["M55-regs", "M55-adjustments"],
    "9": ["M55-timesheets"],
}

NEW_MODELS = ("fix.oncall.callout", "fix.capacity.forecast", "fix.timesheet.line")

# What a form must never let a person type: the state, every decision stamp
# and every measured figure.
NEVER_TYPED = {
    "fix.oncall.callout": {
        "name",
        "state",
        "employee_id",
        "company_id",
        "hours",
        "submitted_at",
        "verified_by_id",
        "verified_at",
        "rejection_reason",
    },
    "fix.capacity.forecast": {
        "name",
        "state",
        "rostered_hours",
        "leave_hours",
        "available_hours",
        "people_count",
        "gap_hours",
        "gap_pct",
        "gap_flag",
        "measured_at",
        "published_by_id",
        "published_at",
        "superseded_by_id",
    },
    "fix.timesheet.line": {
        "name",
        "state",
        "attended_hours",
        "submitted_at",
        "decided_by_id",
        "decided_at",
        "rejection_reason",
    },
}


def _sub(m55, no):
    return next(s for s in m55["subs"] if s["no"] == no)


def test_every_page_is_classified(m55):
    assert sorted(s["no"] for s in m55["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m55, no):
    sub = _sub(m55, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]} | {sub["create"]}
    missing = [form for form in [own, *others] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)


def test_no_page_offers_another_pages_record(m55):
    """Pages 2, 7 and 9 offered page 1's or page 5's record as their + New."""
    assert _sub(m55, "2")["create"] != "M55-form-exception"
    assert _sub(m55, "7")["create"] != "M55-form-roster"
    assert _sub(m55, "9")["create"] != "M55-form-exception"


@pytest.mark.parametrize("no", sorted(PLACED, key=int))
def test_orphan_lists_are_placed_on_their_page(m55, no):
    missing = [sid for sid in PLACED[no] if sid not in _sub(m55, no)["screens"]]
    assert not missing, "page %s does not list %s" % (no, missing)


def test_each_captured_record_is_listed_on_its_page(m55):
    for sub in m55["subs"]:
        listed = {m55["screens"][s]["model"] for s in sub["screens"] if s in m55["screens"]}
        listed.add(sub["model"])
        captures = list(sub["forms"])
        if sub["create"]:
            captures.append({"model": m55["screens"][sub["create"]]["model"]})
        for f in captures:
            assert f["model"] in listed, "page %s captures %s but lists none" % (
                sub["no"],
                f["model"],
            )


def test_every_creatable_list_on_a_page_has_its_capture(m55):
    for sub in m55["subs"]:
        captured = {f["model"] for f in sub["forms"] if f["opens"]}
        if sub["create"]:
            captured.add(m55["screens"][sub["create"]]["model"])
        for sid in sub["screens"]:
            cfg = m55["screens"].get(sid, {})
            if cfg.get("kind") == "model_list" and cfg.get("create") is not False:
                assert cfg["model"] in captured, "page %s lists %s (%s) with no capture" % (
                    sub["no"],
                    cfg["model"],
                    sid,
                )


def test_every_working_screen_sits_on_a_page(m55):
    placed = {sid for s in m55["subs"] for sid in s["screens"]}
    placed |= {r["route"] for s in m55["subs"] for r in s["reports"]}
    orphans = [
        sid
        for sid, cfg in m55["screens"].items()
        if cfg["kind"] in ("model_list", "table_report") and sid not in placed
    ]
    assert not orphans, orphans


def test_every_screen_on_a_page_has_a_navigation_label(m55):
    labelled = set(m55["labelled"])
    unlabelled = sorted(
        sid
        for sub in m55["subs"]
        for sid in sub["screens"]
        if sid in m55["screens"] and sid not in labelled
    )
    assert not unlabelled, unlabelled


def test_every_form_chip_has_a_form_model(m55):
    missing = [f for f in m55["forms"] if "M55:" + f not in m55["formModels"]]
    assert not missing, missing


def test_every_served_action_exists_on_its_model():
    classes = _model_classes()
    for model in NEW_MODELS:
        acts = _surfaces()[model]
        methods = classes.get(model, (set(), set()))[1]
        # the people inbox mixin supplies action_inbox_approve / _reject
        missing = acts - methods - {"action_inbox_approve", "action_inbox_reject"}
        assert not missing, "%s serves %s, which the model lacks" % (model, sorted(missing))


def test_every_list_action_is_served(m55):
    surfaces = _surfaces()
    for sid, cfg in m55["screens"].items():
        if cfg["kind"] != "model_list" or not cfg["actions"]:
            continue
        served = surfaces[cfg["model"]]
        for act in cfg["actions"]:
            assert act["m"] in served, "%s offers %s, not served" % (sid, act["m"])


def test_every_form_field_exists_on_its_model(m55):
    classes = _model_classes()
    for sid, cfg in m55["screens"].items():
        if cfg["kind"] != "model_form" or cfg["model"] not in NEW_MODELS:
            continue
        known = classes[cfg["model"]][0] | {"name", "state", "active"}
        unknown = [f["name"] for f in cfg["fields"] if f["name"] not in known]
        assert not unknown, "%s shows %s, not fields of %s" % (sid, unknown, cfg["model"])


@pytest.mark.parametrize("model", NEW_MODELS)
def test_new_registers_are_served_and_whitelisted(m55, model):
    assert model in _surfaces()
    forms = [
        c for c in m55["screens"].values() if c["kind"] == "model_form" and c["model"] == model
    ]
    assert forms, "%s has no workspace form" % model
    typed = {f["name"] for c in forms for f in c["fields"] if not f["readonly"]}
    assert _writable()[model] == typed


@pytest.mark.parametrize("model", sorted(NEVER_TYPED))
def test_stamps_and_measured_figures_are_never_typed(model):
    leaked = _writable().get(model, set()) & NEVER_TYPED[model]
    assert not leaked, (model, sorted(leaked))


def test_long_forms_are_tabbed(m55):
    """AGENTS.md: a form of more than 15 fields is split into tabs."""
    long_flat = [
        sid
        for sid, c in m55["screens"].items()
        if c["kind"] == "model_form" and len(c["fields"]) > 15 and not c["tabs"]
    ]
    assert not long_flat, long_flat


def test_decisions_ask_for_their_reason(m55):
    for sid, method in (
        ("M55-callouts", "action_reject"),
        ("M55-timesheets", "action_reject"),
    ):
        acts = {a["m"]: a for a in m55["screens"][sid]["actions"]}
        assert acts[method]["kwargs"] == ["reason"], sid


def test_new_models_are_secured():
    acl = (ATT / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    rules = (ATT / "security" / "fix_isolation_rules.xml").read_text(encoding="utf-8")
    own = (ATT / "security" / "fix_a09_attendance_rules.xml").read_text(encoding="utf-8")
    for model in NEW_MODELS:
        xmlid = "model_" + model.replace(".", "_")
        rows = [r.split(",") for r in acl.splitlines() if (",%s," % xmlid) in r]
        assert rows, model
        assert all(r[-1].strip() == "0" for r in rows), "%s: nobody deletes" % model
        sup = [r for r in rows if r[3] == "cd_attendance.group_attendance_supervisor"]
        assert sup and sup[0][4] == "1", "%s: supervisors need their own row" % model
        assert 'ref="%s"' % xmlid in rules, "%s has no company rule" % model
    for model in ("fix.oncall.callout", "fix.timesheet.line"):
        xmlid = "model_" + model.replace(".", "_")
        assert 'ref="%s"' % xmlid in own, "%s: no own-and-reports rule" % model


def test_the_new_file_loads_after_the_models_it_extends():
    init = (ATT / "models" / "__init__.py").read_text(encoding="utf-8")
    assert init.rstrip().endswith("from . import fix_wfm_capture"), init


def test_the_manifest_declares_what_the_new_records_reference():
    """FF-46: project (M67), contract (M05) and skill (M22) are referenced."""
    manifest = ast.literal_eval((ATT / "__manifest__.py").read_text(encoding="utf-8"))
    assert {"cd_ppm", "cd_msp_contract", "cd_competency"} <= set(manifest["depends"])
