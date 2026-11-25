# M63 Process Automation: every sub-module page captures the record it holds
# (capture audit 2026-11-18).
#
# Before (HEAD 32e24dc9), evaluated with the engine's own fregCreate/fregPanels:
#   * page 2 (Approval Chains) captured nothing: no "+ New" and no chip,
#     although its Substitution / OOO list is creatable and its form existed;
#     approval requests and history sat on no page;
#   * page 3 (DoA Matrix) offered the routing row only: the value ladder that
#     sets the approval tier (FR-BPA-009 "to what value") was out of reach;
#   * page 4 (Business Rules): "Rule Simulation" was the automation-rate
#     report; no simulation could be run or recorded (FR-BPA-007,
#     BRU-BPA-04 H, entity fix.rule.simulation);
#   * page 5 (Scheduled & Event Jobs) showed scheduled workflows only: event
#     automations were on no page, and no business job could be registered
#     against the scheduled action that runs it;
#   * page 6 (Task Inbox) listed the inbox only (the all-tasks list sat on no
#     page); it rightly captures nothing: the engine raises tasks;
#   * page 7 (Audit & Performance) typed a workflow instance by hand (nothing
#     in the code starts one, and the KPIs counted it); there was no
#     routine-work register (the 85% target's denominator, AUT-BPA-21,
#     AC-25) and no recorded manual intervention (FR-BPA-008, BRU-BPA-23).
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
CONTROLLER = HERE.parent / "controllers" / "a11" / "m63.py"
ENGINE = HERE.parents[2] / "domain" / "i_governance" / "cd_workflow_engine"

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
const mod = P03_MODULES.M63;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M63', map);
  const panels = fregPanels('M63', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M63:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M63.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: own || null, presets: (create && create.presets) || null, forms,
    reports: panels.reports.map((r) => ({ r, route: P03_REPORT_ROUTES['M63:' + r] || null })) };
});
const screen = (c) => ({
    kind: c.kind, model: c.model || null, create: c.create, report: c.report || null,
    presets: c.presets || null, tabs: (c.tabs || []).length,
    actions: (c.actions || []).map((a) => ({ m: a.m, kwargs: (a.asks || []).map((q) => q.kwarg).concat(a.kwarg ? [a.kwarg] : []) })),
    cols: c.cols || [],
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({
      name: f.name, readonly: !!f.readonly, required: !!f.required })) });
console.log(JSON.stringify({ subs, forms: mod.forms, kpis: mod.kpis.map((k) => k.m),
  labelled: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => id.startsWith('M63-')).map(([id, c]) => [id, screen(c)])) }));
"""


@pytest.fixture(scope="module")
def m63(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m63_capture")
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
    value = _assigned(CONTROLLER, "WRITABLE")
    for key, val in zip(value.keys, value.values, strict=True):
        names = set()
        if isinstance(val, ast.Call) and val.args:
            names = set(ast.literal_eval(val.args[0]))
        out[ast.literal_eval(key)] = names
    return out


def _model_classes():
    """{model: ({fields}, {methods})} defined or extended in cd_workflow_engine."""
    out = {}
    for path in (ENGINE / "models").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for cls in (n for n in tree.body if isinstance(n, ast.ClassDef)):
            names, flds = set(), set()
            for stmt in cls.body:
                if not (isinstance(stmt, ast.Assign) and isinstance(stmt.targets[0], ast.Name)):
                    continue
                target = stmt.targets[0].id
                if target in ("_name", "_inherit") and isinstance(stmt.value, ast.Constant):
                    names.add(stmt.value.value)
                elif target == "_inherit" and isinstance(stmt.value, ast.List):
                    names.update(
                        e.value
                        for e in stmt.value.elts
                        if isinstance(e, ast.Constant) and e.value.startswith("fix.")
                    )
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
# other record the page covers, by form screen. Page 6 captures nothing.
CAPTURES = {
    "1": ["M63-form-automation"],
    "2": ["M63-form-substitution", "M63-form-doa"],
    "3": ["M63-form-doa", "M30-form-dofa-ladder", "M30-form-dofa-band"],
    "4": ["M63-form-rule", "M63-form-simulation"],
    "5": ["M63-form-scheduled", "M63-form-event", "M63-form-job-registration"],
    "7": ["M63-form-intervention", "M63-form-register"],
}
NO_CAPTURE = {"6"}

NEW_MODELS = ("fix.rule.simulation", "fix.automation.register", "fix.workflow.intervention")

# What a form must never let a person type: results, stamps and outcomes.
NEVER_TYPED = {
    "fix.rule.simulation": {
        "name",
        "rule_snapshot",
        "target_models",
        "run_by_id",
        "run_at",
        "evaluated_count",
        "matched_count",
        "changed_count",
        "unreached_count",
        "truncated",
        "summary",
        "sample_differences",
    },
    "fix.automation.register": {"automated_volume", "last_reviewed_on", "reviewed_by_id"},
    "fix.workflow.intervention": {"name", "operator_id", "at", "state_before", "state_after"},
    "fix.workflow.instance": {
        "automation_id",
        "res_model",
        "res_id",
        "state",
        "started_at",
        "finished_at",
        "escalated",
    },
}


def _sub(m63, no):
    return next(s for s in m63["subs"] if s["no"] == no)


def test_every_page_is_classified(m63):
    assert sorted(s["no"] for s in m63["subs"]) == sorted({*CAPTURES, *NO_CAPTURE})


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m63, no):
    sub = _sub(m63, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]} | {sub["create"]}
    missing = [form for form in [own, *others] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)


def test_the_task_inbox_page_captures_nothing(m63):
    """A task is raised by the approval engine and is never typed in."""
    sub = _sub(m63, "6")
    assert sub["create"] is None and not sub["forms"]
    assert m63["screens"]["M63-form-task"]["create"] is False


def test_the_audit_page_no_longer_types_a_workflow_instance(m63):
    sub = _sub(m63, "7")
    assert sub["create"] != "M63-form-instance"
    form = m63["screens"]["M63-form-instance"]
    assert form["create"] is False
    assert all(f["readonly"] for f in form["fields"]), form["fields"]


def test_rule_simulation_is_a_record_not_the_automation_report(m63):
    cfg = m63["screens"]["M63-simulation"]
    assert cfg["kind"] == "model_list" and cfg["model"] == "fix.rule.simulation", cfg


def test_page_five_fills_in_the_engine_of_what_it_creates(m63):
    sub = _sub(m63, "5")
    assert sub["presets"] == {"engine": "odoo_cron"}
    assert m63["screens"]["M63-form-scheduled"]["presets"] == {"engine": "odoo_cron"}
    assert m63["screens"]["M63-form-event"]["presets"] == {"engine": "event_consumer"}
    assert m63["screens"]["M63-events"]["model"] == "fix.automation"
    # A11 pass 1, D-L13: the page serves the REAL ir.cron estate, not phantom DAG rows
    assert m63["screens"]["M63-jobs"]["kind"] == "table_report"
    assert m63["screens"]["M63-jobs"]["report"] == "scheduled_jobs"


def test_each_chip_opens_the_model_its_name_says(m63):
    from_meta = {
        "Substitution / OOO": "fix.approval.substitution",
        "Approval Chain": "fix.approval.matrix",
        "Authority Ladder": "fix.dofa.ladder",
        "Ladder Band": "fix.dofa.threshold",
        "Rule Simulation": "fix.rule.simulation",
        "Scheduled Job Registration": "fix.automation",
        "Manual Intervention": "fix.workflow.intervention",
        "Automation Register Entry": "fix.automation.register",
    }
    for sub in m63["subs"]:
        for chip in sub["forms"]:
            if chip["f"] in from_meta:
                assert chip["model"] == from_meta[chip["f"]], chip


def test_each_captured_record_is_listed_on_its_page(m63):
    """A captured record of M63's own is visible where it was made. The
    M30 ladder, band and job registry are listed on M30's own pages."""
    m30 = {"fix.dofa.ladder", "fix.dofa.threshold", "fix.scheduled.job"}
    for sub in m63["subs"]:
        listed = {m63["screens"][s]["model"] for s in sub["screens"] if s in m63["screens"]}
        listed.add(sub["model"])
        captures = list(sub["forms"])
        if sub["create"]:
            captures.append({"model": m63["screens"][sub["create"]]["model"]})
        for f in captures:
            if f["model"] in m30:
                continue
            if sub["no"] == "2" and f["model"] == "fix.approval.matrix":
                continue  # the chain's rule is listed on page 3, the DoA matrix
            assert f["model"] in listed, "page %s captures %s but lists none" % (
                sub["no"],
                f["model"],
            )


def test_every_creatable_list_on_a_page_has_its_capture(m63):
    for sub in m63["subs"]:
        captured = {f["model"] for f in sub["forms"] if f["opens"]}
        if sub["create"]:
            captured.add(m63["screens"][sub["create"]]["model"])
        for sid in sub["screens"]:
            cfg = m63["screens"].get(sid, {})
            if cfg.get("kind") != "model_list" or cfg.get("create") is False:
                continue
            if cfg["model"] in ("fix.workflow.instance", "fix.workflow.task"):
                continue  # engine-raised: the monitor acts on them, never creates
            assert cfg["model"] in captured, "page %s lists %s (%s) with no capture" % (
                sub["no"],
                cfg["model"],
                sid,
            )


def test_every_working_screen_sits_on_a_page(m63):
    placed = {sid for s in m63["subs"] for sid in s["screens"]}
    placed |= {r["route"] for s in m63["subs"] for r in s["reports"]}
    orphans = [
        sid
        for sid, cfg in m63["screens"].items()
        if cfg["kind"] == "model_list" and sid not in placed
    ]
    assert not orphans, orphans


def test_every_screen_on_a_page_has_a_navigation_label(m63):
    labelled = set(m63["labelled"])
    unlabelled = sorted(
        sid
        for sub in m63["subs"]
        for sid in sub["screens"]
        if sid in m63["screens"] and sid not in labelled
    )
    assert not unlabelled, unlabelled


def test_every_served_action_exists_on_its_model():
    classes = _model_classes()
    for model, acts in _surfaces().items():
        methods = classes.get(model, (set(), set()))[1]
        missing = acts - methods
        assert not missing, "%s serves %s, which the model lacks" % (model, sorted(missing))


def test_every_list_action_is_served(m63):
    surfaces = _surfaces()
    for sid, cfg in m63["screens"].items():
        if cfg["kind"] != "model_list" or not cfg["actions"]:
            continue
        served = surfaces[cfg["model"]]
        for act in cfg["actions"]:
            assert act["m"] in served, "%s offers %s, not served" % (sid, act["m"])


def test_every_monitor_action_asks_why(m63):
    acts = {a["m"]: a["kwargs"] for a in m63["screens"]["M63-monitor"]["actions"]}
    assert set(acts) == {"action_complete", "action_fail", "action_escalate", "action_terminate"}
    assert all(kwargs == ["reason"] for kwargs in acts.values()), acts


def test_every_list_column_exists_on_its_model(m63):
    """A column the model lacks is dropped silently by the endpoint."""
    classes = _model_classes()
    for sid, cfg in m63["screens"].items():
        if cfg["kind"] != "model_list" or cfg["model"] not in classes:
            continue
        known = classes[cfg["model"]][0] | {"name", "state", "display_name"}
        unknown = [c for c in cfg["cols"] if c not in known]
        assert not unknown, "%s lists %s, not fields of %s" % (sid, unknown, cfg["model"])


def test_every_form_field_exists_on_its_model(m63):
    classes = _model_classes()
    for sid, cfg in m63["screens"].items():
        if cfg["kind"] != "model_form" or cfg["model"] not in classes:
            continue
        known = classes[cfg["model"]][0] | {"name", "state", "active"}
        unknown = [f["name"] for f in cfg["fields"] if f["name"] not in known]
        assert not unknown, "%s shows %s, not fields of %s" % (sid, unknown, cfg["model"])


@pytest.mark.parametrize("model", NEW_MODELS)
def test_new_registers_are_served_and_whitelisted(m63, model):
    assert model in _surfaces()
    forms = [
        c for c in m63["screens"].values() if c["kind"] == "model_form" and c["model"] == model
    ]
    assert forms, "%s has no workspace form" % model
    typed = {f["name"] for c in forms for f in c["fields"] if not f["readonly"]}
    assert _writable()[model] == typed


@pytest.mark.parametrize("model", sorted(NEVER_TYPED))
def test_results_stamps_and_outcomes_are_never_typed(model):
    leaked = _writable().get(model, set()) & NEVER_TYPED[model]
    assert not leaked, (model, sorted(leaked))


def test_new_kpis_are_offered(m63):
    assert {"rules_unsimulated", "interventions_mtd", "automation_rate"} <= set(m63["kpis"])


def test_new_models_are_secured():
    acl = (ENGINE / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    rules = (ENGINE / "security" / "fix_isolation_rules.xml").read_text(encoding="utf-8")
    for model in NEW_MODELS:
        xmlid = "model_" + model.replace(".", "_")
        rows = [r.split(",") for r in acl.splitlines() if (",%s," % xmlid) in r]
        assert rows, model
        assert 'ref="%s"' % xmlid in rules, "%s has no company rule" % model
        # nobody deletes one; a plain user only reads
        assert all(r[-1].strip() == "0" for r in rows), "%s: nobody deletes" % model
        plain = [r for r in rows if r[3] == "base.group_user"]
        assert plain and all(r[5:8] == ["0", "0", "0"] for r in plain), plain
    # a simulation and an intervention are evidence: nobody writes one
    for model in ("fix_rule_simulation", "fix_workflow_intervention"):
        rows = [r.split(",") for r in acl.splitlines() if ",model_%s," % model in r]
        assert all(r[5] == "0" for r in rows), model


def test_the_new_file_loads_after_the_models_it_extends():
    init = (ENGINE / "models" / "__init__.py").read_text(encoding="utf-8")
    assert init.rstrip().endswith("from . import fix_m63_capture"), init
    assert init.index("fix_m63_capture") > init.index("fix_approval_engine")
