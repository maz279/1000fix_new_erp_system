# M54 Costing, Budget & FP&A: every sub-module page captures each record it
# covers (capture audit 2026-11-17).
#
# Before (HEAD 94bf9e99), evaluated with the engine's own fregCreate/fregPanels:
#   * page 3 (Job & Contract Costing) and page 5 (Branch & Channel
#     Profitability) captured nothing: no "+ New", no chip;
#   * page 7 (Variance & Forecast) offered "+ New" BUDGET, which belongs to
#     page 6, and had no way to explain a variance or start a forecast;
#   * page 1 listed cost elements and page 4 business lines with no chip;
#   * no cost centre with an owner (FR-FPA-001 P0): the cost centre was free
#     text, so no variance could be put to an accountable owner;
#   * no approved planned activity rate (FR-FPA-012/013 P0, BRU-FPA-16 H):
#     job costing used whatever each technician's actual rate came to over
#     the window asked for;
#   * no top-down budget target (FR-FPA-029 P0, spec 8.2 "Target set");
#   * no variance explanation (FR-FPA-037 P0, BRU-FPA-12 H, AUT-FPA-08).
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
CONTROLLER = HERE.parent / "controllers" / "a08" / "m54.py"
WRITABLE_FILE = HERE.parent / "controllers" / "a08" / "writable.py"
FPA = HERE.parents[2] / "domain" / "g_finance" / "cd_fpa"

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
const mod = P03_MODULES.M54;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M54', map);
  const panels = fregPanels('M54', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M54:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M54.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: own || null, forms,
    reports: panels.reports.map((r) => ({ r, route: P03_REPORT_ROUTES['M54:' + r] || null })) };
});
const screen = (c) => ({
    kind: c.kind, model: c.model || null, create: c.create, report: c.report || null,
    tabs: (c.tabs || []).length,
    actions: (c.actions || []).map((a) => ({ m: a.m, kwargs: (a.asks || []).map((q) => q.kwarg).concat(a.kwarg ? [a.kwarg] : []) })),
    cols: c.cols || [],
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({
      name: f.name, readonly: !!f.readonly, required: !!f.required })) });
console.log(JSON.stringify({ subs, forms: mod.forms,
  labelled: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  foreign: Object.fromEntries(Object.values(P03_FORM_CHIPS).filter((id) => typeof id === 'string' && !id.startsWith('M54-') && P03_DATA_SCREENS[id]).map((id) => [id, screen(P03_DATA_SCREENS[id])])),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => id.startsWith('M54-')).map(([id, c]) => [id, screen(c)])) }));
"""


@pytest.fixture(scope="module")
def m54(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m54_capture")
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
    """{model: ({fields}, {methods})} defined or extended in cd_fpa."""
    out = {}
    for path in (FPA / "models").glob("*.py"):
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
    "1": ["M54-form-pool", "M54-form-element", "M54-form-centre"],
    "2": ["M54-form-allocation"],
    "3": ["M54-form-rate"],
    "4": ["M54-form-bline", "M54-form-variance-bl"],
    "5": ["M54-form-variance-branch"],
    "6": ["M54-form-budget", "M54-form-version", "M54-form-target"],
    "7": ["M54-form-variance", "M54-form-forecast", "M54-form-scenario"],
    "8": ["M54-form-boardpack"],
}

NEW_MODELS = (
    "fix.cost.centre",
    "fix.activity.rate",
    "fix.budget.target",
    "fix.variance.explanation",
)

# What a form must never let a person type: the state, every decision stamp
# and every measured figure.
NEVER_TYPED = {
    "fix.activity.rate": {
        "name",
        "state",
        "measured_rate",
        "measured_hours",
        "measured_at",
        "submitted_by",
        "submitted_at",
        "approved_by",
        "approved_at",
        "rejection_reason",
        "superseded_by_id",
    },
    "fix.budget.target": {
        "name",
        "state",
        "plan_amount",
        "departure",
        "departure_pct",
        "issued_by",
        "issued_at",
        "withdrawn_by",
        "withdraw_reason",
    },
    "fix.variance.explanation": {
        "name",
        "state",
        "version_id",
        "planned",
        "actual",
        "variance",
        "variance_pct",
        "threshold_amount",
        "threshold_pct",
        "breached",
        "measured_at",
        "due_date",
        "submitted_by",
        "submitted_at",
        "accepted_by",
        "accepted_at",
        "return_reason",
    },
}


def _sub(m54, no):
    return next(s for s in m54["subs"] if s["no"] == no)


def test_every_page_is_classified(m54):
    assert sorted(s["no"] for s in m54["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m54, no):
    sub = _sub(m54, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]} | {sub["create"]}
    missing = [form for form in [own, *others] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)


def test_the_variance_page_no_longer_offers_a_budget(m54):
    assert _sub(m54, "7")["create"] != "M54-form-budget"
    assert _sub(m54, "7")["model"] == "fix.variance.explanation"


def test_each_captured_record_is_listed_on_its_page(m54):
    for sub in m54["subs"]:
        listed = {m54["screens"][s]["model"] for s in sub["screens"] if s in m54["screens"]}
        listed.add(sub["model"])
        captures = list(sub["forms"])
        if sub["create"]:
            captures.append({"model": m54["screens"][sub["create"]]["model"]})
        for f in captures:
            assert f["model"] in listed, "page %s captures %s but lists none" % (
                sub["no"],
                f["model"],
            )


def test_every_creatable_list_on_a_page_has_its_capture(m54):
    for sub in m54["subs"]:
        captured = {f["model"] for f in sub["forms"] if f["opens"]}
        if sub["create"]:
            captured.add(m54["screens"][sub["create"]]["model"])
        for sid in sub["screens"]:
            cfg = m54["screens"].get(sid, {})
            if cfg.get("kind") == "model_list" and cfg.get("create") is not False:
                assert cfg["model"] in captured, "page %s lists %s (%s) with no capture" % (
                    sub["no"],
                    cfg["model"],
                    sid,
                )


def test_every_working_screen_sits_on_a_page(m54):
    placed = {sid for s in m54["subs"] for sid in s["screens"]}
    placed |= {r["route"] for s in m54["subs"] for r in s["reports"]}
    orphans = [
        sid
        for sid, cfg in m54["screens"].items()
        if cfg["kind"] in ("model_list", "table_report") and sid not in placed
    ]
    assert not orphans, orphans


def test_every_screen_on_a_page_has_a_navigation_label(m54):
    labelled = set(m54["labelled"])
    unlabelled = sorted(
        sid
        for sub in m54["subs"]
        for sid in sub["screens"]
        if sid in m54["screens"] and sid not in labelled
    )
    assert not unlabelled, unlabelled


def test_every_served_action_exists_on_its_model():
    classes = _model_classes()
    for model, acts in _surfaces().items():
        methods = classes.get(model, (set(), set()))[1]
        # the DOFA mixin (cd_workflow_engine) supplies the generic approval verbs
        missing = acts - methods
        assert not missing, "%s serves %s, which the model lacks" % (model, sorted(missing))


def test_every_list_action_is_served(m54):
    surfaces = _surfaces()
    for sid, cfg in m54["screens"].items():
        if cfg["kind"] != "model_list" or not cfg["actions"]:
            continue
        served = surfaces[cfg["model"]]
        for act in cfg["actions"]:
            assert act["m"] in served, "%s offers %s, not served" % (sid, act["m"])


def test_every_form_field_exists_on_its_model(m54):
    classes = _model_classes()
    for sid, cfg in m54["screens"].items():
        if cfg["kind"] != "model_form" or cfg["model"] not in NEW_MODELS:
            continue
        known = classes[cfg["model"]][0] | {"name", "state", "active"}
        unknown = [f["name"] for f in cfg["fields"] if f["name"] not in known]
        assert not unknown, "%s shows %s, not fields of %s" % (sid, unknown, cfg["model"])


@pytest.mark.parametrize("model", NEW_MODELS)
def test_new_registers_are_served_and_whitelisted(m54, model):
    assert model in _surfaces()
    forms = [
        c for c in m54["screens"].values() if c["kind"] == "model_form" and c["model"] == model
    ]
    assert forms, "%s has no workspace form" % model
    typed = {f["name"] for c in forms for f in c["fields"] if not f["readonly"]}
    assert _writable()[model] == typed


@pytest.mark.parametrize("model", sorted(NEVER_TYPED))
def test_stamps_and_measured_figures_are_never_typed(model):
    leaked = _writable().get(model, set()) & NEVER_TYPED[model]
    assert not leaked, (model, sorted(leaked))


def test_scoped_variance_forms_post_their_scope(m54):
    """The branch / business-line forms preset scope_type read-only: the
    field must still be writable, or the preset would never be posted and
    every branch explanation would save as a budget-line one."""
    assert "scope_type" in _writable()["fix.variance.explanation"]
    assert "version_type" in _writable()["fix.budget.version"]


def test_long_forms_are_tabbed(m54):
    """AGENTS.md: a form of more than 15 fields is split into tabs."""
    long_flat = [
        sid
        for sid, c in m54["screens"].items()
        if c["kind"] == "model_form" and len(c["fields"]) > 15 and not c["tabs"]
    ]
    assert not long_flat, long_flat


def test_decisions_ask_for_their_reason(m54):
    for sid, method in (
        ("M54-activity-rates", "action_reject"),
        ("M54-targets", "action_withdraw"),
        ("M54-variances", "action_return"),
    ):
        acts = {a["m"]: a for a in m54["screens"][sid]["actions"]}
        assert acts[method]["kwargs"] == ["reason"], sid


def test_new_models_are_secured():
    acl = (FPA / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    rules = (FPA / "security" / "fix_isolation_rules.xml").read_text(encoding="utf-8")
    for model in NEW_MODELS:
        xmlid = "model_" + model.replace(".", "_")
        rows = [r.split(",") for r in acl.splitlines() if (",%s," % xmlid) in r]
        assert rows, model
        ro = [r for r in rows if r[3] == "account.group_account_readonly"]
        assert ro and ro[0][4:8] == ["1", "0", "0", "0"], model
        mgr = [r for r in rows if r[3] == "account.group_account_manager"]
        assert mgr and mgr[0][4] == "1", "%s: administrators need their own row" % model
        assert 'ref="%s"' % xmlid in rules, "%s has no company rule" % model
    for model in ("fix_variance_explanation", "fix_cost_centre"):
        rows = [r.split(",") for r in acl.splitlines() if ",model_%s," % model in r]
        assert all(r[-1].strip() == "0" for r in rows), "%s: nobody deletes" % model


def test_the_new_file_loads_after_the_models_it_extends():
    """It extends fix.budget.version and fix.fpa.engine: an _inherit before
    its _name fails to load."""
    init = (FPA / "models" / "__init__.py").read_text(encoding="utf-8")
    assert init.rstrip().endswith("from . import fix_fpa_capture"), init
    assert "ruff: noqa: I001" in init
