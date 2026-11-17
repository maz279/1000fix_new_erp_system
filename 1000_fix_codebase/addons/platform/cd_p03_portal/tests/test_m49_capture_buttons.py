# M49 Fixed Assets & Capex: every sub-module page captures each record it
# covers (capture audit 2026-11-17).
#
# Before (HEAD 3efdab37), evaluated with the engine's own fregCreate/fregPanels:
#   * every page had a "+ New" for its own record, but pages 1, 2, 3, 4 and 7
#     listed records they offered no chip for although their forms existed:
#     the Capital Budget (page 1), the Asset Categories (page 2), the CWIP
#     entries (page 3), the Depreciation Runs (page 4) and the Verification
#     Campaigns (page 7);
#   * the Lease Schedules and the Register-to-GL reconciliation sat on no page;
#   * page 3 is "Componentisation" but no component existed (FR-FXA-014): a
#     CWIP project capitalised into ONE asset with one life;
#   * no life / residual change or depreciation suspension (FR-FXA-023 P0,
#     FR-FXA-024, BRU-FXA-10): an asset's life was frozen in service with no
#     approved way to change it;
#   * no impairment assessment (FR-FXA-032, BRU-FXA-26 H): only a loss could
#     be recorded, never the annual assessment that found none;
#   * no verification variance investigation (FR-FXA-030 P0, BRU-FXA-15/16):
#     a missing or misplaced asset had no explanation, proposal or approval;
#   * no capital project or post-implementation review (FR-FXA-006/007,
#     BRU-FXA-24 H).
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
CONTROLLER = HERE.parent / "controllers" / "a08" / "m49.py"
WRITABLE_FILE = HERE.parent / "controllers" / "a08" / "writable.py"
ASSETS = HERE.parents[2] / "domain" / "g_finance" / "cd_fixed_asset_ext"

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
const mod = P03_MODULES.M49;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M49', map);
  const panels = fregPanels('M49', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M49:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M49.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: own || null, forms,
    reports: panels.reports.map((r) => ({ r, route: P03_REPORT_ROUTES['M49:' + r] || null })) };
});
console.log(JSON.stringify({ subs, forms: mod.forms,
  labelled: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => id.startsWith('M49-')).map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create, report: c.report || null,
    tabs: (c.tabs || []).length,
    actions: (c.actions || []).map((a) => ({ m: a.m, kwargs: (a.asks || []).map((q) => q.kwarg).concat(a.kwarg ? [a.kwarg] : []) })),
    cols: c.cols || [],
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({
      name: f.name, readonly: !!f.readonly, required: !!f.required })) }])) }));
"""


@pytest.fixture(scope="module")
def m49(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m49_capture")
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
    """{model: {method names}} defined in cd_fixed_asset_ext's model files."""
    out = {}
    for path in (ASSETS / "models").glob("*.py"):
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
    "1": ["M49-form-capex", "M49-form-budget", "M49-form-project"],
    "2": ["M49-form-asset", "M49-form-category", "M49-form-lease"],
    "3": ["M49-form-cwip", "M49-form-component"],
    "4": ["M49-form-deprun", "M49-form-depchange"],
    "5": ["M49-form-revaluation", "M49-form-impairment-test"],
    "6": ["M49-form-transfer"],
    "7": ["M49-form-verify", "M49-form-variance"],
    "8": ["M49-form-disposal"],
}

RECORDS = {
    "1": "fix.capex.request",
    "2": "fix.fixed.asset",
    "3": "fix.cwip.entry",
    "4": "fix.asset.depreciation.run",
    "5": "fix.asset.revaluation",
    "6": "fix.asset.transfer",
    "7": "fix.asset.verification.campaign",
    "8": "fix.asset.disposal",
}

NEW_MODELS = (
    "fix.capital.project",
    "fix.cwip.component",
    "fix.asset.depreciation.change",
    "fix.asset.impairment.assessment",
    "fix.asset.verification.variance",
)

# What a form must never let a person type: the state, every decision stamp
# and every derived figure.
NEVER_TYPED = {
    "fix.capital.project": {
        "state",
        "reference",
        "approved_by_id",
        "approved_on",
        "actual_completion",
        "committed_amount",
        "actual_cost",
        "review_required",
        "review_due_date",
        "review_actual_cost",
        "review_variance",
        "reviewed_by_id",
        "reviewed_on",
    },
    "fix.cwip.component": {"asset_id", "company_id", "cwip_state"},
    "fix.asset.depreciation.change": {
        "name",
        "state",
        "requested_by_id",
        "approved_by_id",
        "approved_on",
        "applied_from",
        "previous_life_months",
        "previous_salvage",
        "months_charged",
    },
    "fix.asset.impairment.assessment": {
        "name",
        "state",
        "assessed_by_id",
        "confirmed_by_id",
        "confirmed_on",
        "carrying_amount",
        "impairment_loss",
        "revaluation_id",
    },
    "fix.asset.verification.variance": {
        "name",
        "state",
        "variance_type",
        "proposed_by_id",
        "approved_by_id",
        "approved_on",
        "transfer_id",
        "disposal_id",
    },
    "fix.fixed.asset": {"depreciation_suspended", "cwip_component_id", "state"},
}


def _sub(m49, no):
    return next(s for s in m49["subs"] if s["no"] == no)


def test_every_page_is_classified(m49):
    assert sorted(s["no"] for s in m49["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m49, no):
    sub = _sub(m49, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]}
    missing = [form for form in [own, *others] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)


@pytest.mark.parametrize("no", sorted(RECORDS, key=int))
def test_each_page_lists_its_own_record(m49, no):
    assert _sub(m49, no)["model"] == RECORDS[no]


def test_each_captured_record_is_listed_on_its_page(m49):
    for sub in m49["subs"]:
        listed = {m49["screens"][s]["model"] for s in sub["screens"] if s in m49["screens"]}
        for f in sub["forms"]:
            assert f["model"] in listed, "page %s captures %s but lists none" % (
                sub["no"],
                f["model"],
            )


def test_every_creatable_list_on_a_page_has_its_capture(m49):
    """A list a person can add to (create not false) offers its form as a
    chip on the page that shows it."""
    for sub in m49["subs"]:
        captured = {f["model"] for f in sub["forms"] if f["opens"]}
        for sid in sub["screens"]:
            cfg = m49["screens"].get(sid, {})
            if cfg.get("kind") == "model_list" and cfg.get("create") is not False:
                assert cfg["model"] in captured, "page %s lists %s (%s) with no capture" % (
                    sub["no"],
                    cfg["model"],
                    sid,
                )


def test_every_working_screen_sits_on_a_page(m49):
    placed = {sid for s in m49["subs"] for sid in s["screens"]}
    placed |= {r["route"] for s in m49["subs"] for r in s["reports"]}
    orphans = [
        sid
        for sid, cfg in m49["screens"].items()
        if cfg["kind"] in ("model_list", "table_report") and sid not in placed
    ]
    assert not orphans, orphans


def test_every_screen_on_a_page_has_a_navigation_label(m49):
    labelled = set(m49["labelled"])
    unlabelled = sorted(
        sid
        for sub in m49["subs"]
        for sid in sub["screens"]
        if sid in m49["screens"]
        and m49["screens"][sid]["kind"] == "model_list"
        and sid not in labelled
    )
    assert not unlabelled, unlabelled


def test_every_served_action_exists_on_its_model():
    methods = _model_methods()
    for model, acts in _surfaces().items():
        missing = acts - methods.get(model, set())
        # the routed-approval mixin (cd_workflow_engine) supplies these
        missing -= {"action_recall_approval", "action_approve"}
        assert not missing, "%s serves %s, which the model lacks" % (model, sorted(missing))


def test_every_list_action_is_served(m49):
    surfaces = _surfaces()
    for sid, cfg in m49["screens"].items():
        if cfg["kind"] != "model_list" or not cfg["actions"]:
            continue
        served = surfaces[cfg["model"]]
        for act in cfg["actions"]:
            assert act["m"] in served, "%s offers %s, not served" % (sid, act["m"])


@pytest.mark.parametrize("model", NEW_MODELS)
def test_new_registers_are_served_and_whitelisted(m49, model):
    assert model in _surfaces()
    forms = [
        c for c in m49["screens"].values() if c["kind"] == "model_form" and c["model"] == model
    ]
    assert forms, "%s has no workspace form" % model
    typed = {f["name"] for c in forms for f in c["fields"] if not f["readonly"]}
    assert _writable()[model] == typed


@pytest.mark.parametrize("model", sorted(NEVER_TYPED))
def test_stamps_and_derived_figures_are_never_typed(model):
    leaked = _writable().get(model, set()) & NEVER_TYPED[model]
    assert not leaked, (model, sorted(leaked))


def test_long_forms_are_tabbed(m49):
    """AGENTS.md: a form of more than 15 fields is split into tabs."""
    long_flat = [
        sid
        for sid, c in m49["screens"].items()
        if c["kind"] == "model_form" and len(c["fields"]) > 15 and not c["tabs"]
    ]
    assert not long_flat, long_flat


def test_a_category_says_whether_it_must_be_componentised(m49):
    names = {f["name"] for f in m49["screens"]["M49-form-category"]["fields"]}
    assert "componentisation_required" in names
    assert "componentisation_required" in _writable()["fix.asset.category"]


def test_a_verification_campaign_is_scoped_to_a_branch(m49):
    names = {f["name"] for f in m49["screens"]["M49-form-verify"]["fields"]}
    assert "operating_unit_id" in names
    assert "operating_unit_id" in _writable()["fix.asset.verification.campaign"]


def test_a_capex_request_names_its_capital_project(m49):
    names = {f["name"] for f in m49["screens"]["M49-form-capex"]["fields"]}
    assert "project_id" in names and "project_id" in _writable()["fix.capex.request"]


def test_new_models_are_secured():
    acl = (ASSETS / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    rules = (ASSETS / "security" / "fix_isolation_rules.xml").read_text(encoding="utf-8")
    for model in NEW_MODELS:
        xmlid = "model_" + model.replace(".", "_")
        rows = [r.split(",") for r in acl.splitlines() if (",%s," % xmlid) in r]
        assert rows, model
        # documents are never deleted; a component line is removed only while
        # its CWIP project is open (the model refuses otherwise)
        if model != "fix.cwip.component":
            assert all(r[-1].strip() == "0" for r in rows), "%s: nobody deletes" % model
        ro = [r for r in rows if r[3] == "account.group_account_readonly"]
        assert ro and ro[0][4:8] == ["1", "0", "0", "0"], model
        assert 'ref="%s"' % xmlid in rules, "%s has no company rule" % model


def test_the_new_file_loads_after_the_models_it_extends():
    init = (ASSETS / "models" / "__init__.py").read_text(encoding="utf-8")
    assert init.index("fix_fixed_asset") < init.index("fix_asset_capture")
    assert init.index("fix_capex,") < init.index("fix_asset_capture")
