# M43 Demand Planning: every sub-module page captures the record it names
# (capture audit 2026-11-16).
#
# Before (HEAD 19773ee8), evaluated with the engine's own fregCreate/fregPanels:
#   * 1 History & Cleansing, 4 Accuracy Tracking and 6 Lead-Time said
#     create: false - no "+ New" and no chip; nothing on them could be typed;
#   * 2 Segmentation, 7 Planned Orders and 9 What-If had a "+ New" but no chip;
#   * no outlier / censored-demand overlay (FR-DPL-003/004, T-01), no demand
#     driver (FR-DPL-013), no service-level target (FR-DPL-018), no lead-time
#     model per supplier with the quoted figure beside the actual (FR-DPL-019,
#     BRU-DPL-09), no new-part recommendation (FR-DPL-030), no end-of-life /
#     last-time-buy plan (FR-DPL-031, BRU-DPL-14), no van par recommendation
#     (FR-DPL-029, BRU-DPL-12) and no network stocking policy (FR-DPL-027)
#     existed - all spec §10.1 owned entities.
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
CONTROLLER = HERE.parent / "controllers" / "a06" / "m43.py"
WRITABLE_FILE = HERE.parent / "controllers" / "a06" / "writable.py"
DEMAND = HERE.parents[2] / "domain" / "e_supply_chain" / "cd_demand_plan"

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
const mod = P03_MODULES.M43;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M43', map);
  const panels = fregPanels('M43', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M43:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M43.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: own || null, forms,
    reports: panels.reports.map((r) => ({ r, route: P03_REPORT_ROUTES['M43:' + r] || null })) };
});
console.log(JSON.stringify({ subs, forms: mod.forms,
  labelled: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => id.startsWith('M43-')).map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create, report: c.report || null,
    actions: (c.actions || []).map((a) => ({ m: a.m, kwargs: (a.asks || []).map((q) => q.kwarg).concat(a.kwarg ? [a.kwarg] : []) })),
    cols: c.cols || [],
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({
      name: f.name, readonly: !!f.readonly, required: !!f.required })) }])) }));
"""

# What each page lets a person capture: its own "+ New" first, then every
# other record the page covers, by form screen.
CAPTURES = {
    "1": ["M43-form-adjustment"],
    "2": ["M43-form-segment"],
    "3": ["M43-form-forecast", "M43-form-driver", "M43-form-review"],
    "4": ["M43-form-review"],
    "5": ["M43-form-policy", "M43-form-target"],
    "6": ["M43-form-leadtime"],
    "7": ["M43-form-plan", "M43-form-npi", "M43-form-eol"],
    "8": ["M43-form-rebalance", "M43-form-vanpar", "M43-form-network"],
    "9": ["M43-form-scenario"],
}

RECORDS = {
    "1": "fix.demand.adjustment",
    "2": "fix.demand.segment",
    "3": "fix.demand.forecast",
    "4": "fix.demand.forecast",
    "5": "fix.demand.policy",
    "6": "fix.demand.lead.time",
    "7": "fix.demand.plan",
    "8": "fix.demand.rebalance",
    "9": "fix.demand.scenario",
}

NEW_MODELS = (
    "fix.demand.adjustment",
    "fix.demand.driver",
    "fix.demand.service.target",
    "fix.demand.lead.time",
    "fix.demand.npi",
    "fix.demand.eol",
    "fix.demand.van.par",
    "fix.demand.network.policy",
)

# What a form must never let a person type: the measured figure, the state and
# every approval stamp (T-01, BRU-DPL-09/12/14).
NEVER_TYPED = {
    "fix.demand.adjustment": {"state", "original_qty", "applied_by_id", "applied_on"},
    "fix.demand.driver": {"state", "prepared_by_id"},
    "fix.demand.service.target": {"state", "prepared_by_id", "approved_by_id"},
    "fix.demand.lead.time": {"sample_count", "mean_days", "std_dev_days", "p95_days"},
    "fix.demand.npi": {"state", "approved_by_id", "analogy_monthly_avg"},
    "fix.demand.eol": {"state", "last_time_buy_value", "approved_by_id", "cfo_approved_by_id"},
    "fix.demand.van.par": {
        "state",
        "suggested_min",
        "suggested_max",
        "avg_daily_demand",
        "approved_by_id",
        "published_rule_id",
    },
    "fix.demand.network.policy": {"state", "approved_by_id"},
}


@pytest.fixture(scope="module")
def m43(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m43_capture")
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
    """{model: {method names}} defined in cd_demand_plan's model files."""
    out = {}
    for path in (DEMAND / "models").glob("*.py"):
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


def _sub(m43, no):
    return next(s for s in m43["subs"] if s["no"] == no)


def test_every_page_is_classified(m43):
    assert sorted(s["no"] for s in m43["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m43, no):
    sub = _sub(m43, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]}
    missing = [form for form in [own, *others] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)


@pytest.mark.parametrize("no", sorted(RECORDS, key=int))
def test_each_page_lists_its_own_record(m43, no):
    assert _sub(m43, no)["model"] == RECORDS[no]


def test_each_captured_record_is_listed_on_its_page(m43):
    for sub in m43["subs"]:
        listed = {m43["screens"][s]["model"] for s in sub["screens"] if s in m43["screens"]}
        for f in sub["forms"]:
            assert f["model"] in listed, "page %s captures %s but lists none" % (
                sub["no"],
                f["model"],
            )


def test_every_working_screen_sits_on_a_page(m43):
    placed = {sid for s in m43["subs"] for sid in s["screens"]}
    placed |= {r["route"] for s in m43["subs"] for r in s["reports"]}
    orphans = [
        sid
        for sid, cfg in m43["screens"].items()
        if cfg["kind"] in ("model_list", "table_report")
        and sid not in placed
        and not sid.startswith("M43-rpt-")
    ]
    assert not orphans, orphans


def test_every_screen_on_a_page_has_a_navigation_label(m43):
    """A list on a page but in no navigation group shows as its raw id."""
    labelled = set(m43["labelled"])
    unlabelled = sorted(
        sid
        for sub in m43["subs"]
        for sid in sub["screens"]
        if sid in m43["screens"]
        and m43["screens"][sid]["kind"] == "model_list"
        and sid not in labelled
    )
    assert not unlabelled, unlabelled


def test_every_served_action_exists_on_its_model():
    methods = _model_methods()
    for model, acts in _surfaces().items():
        missing = acts - methods.get(model, set())
        assert not missing, "%s serves %s, which the model lacks" % (model, sorted(missing))


def test_every_list_action_is_served(m43):
    surfaces = _surfaces()
    for sid, cfg in m43["screens"].items():
        if cfg["kind"] != "model_list" or not cfg["actions"]:
            continue
        served = surfaces.get(cfg["model"], set())
        for act in cfg["actions"]:
            assert act["m"] in served, "%s offers %s, not served" % (sid, act["m"])


@pytest.mark.parametrize("model", NEW_MODELS)
def test_new_registers_are_served_and_whitelisted(m43, model):
    assert model in _surfaces()
    forms = [
        c for c in m43["screens"].values() if c["kind"] == "model_form" and c["model"] == model
    ]
    assert forms, "%s has no workspace form" % model
    typed = {f["name"] for c in forms for f in c["fields"] if not f["readonly"]}
    assert _writable()[model] == typed


@pytest.mark.parametrize("model", sorted(NEVER_TYPED))
def test_measured_figures_and_stamps_are_never_typed(model):
    leaked = _writable().get(model, set()) & NEVER_TYPED[model]
    assert not leaked, (model, sorted(leaked))


def test_new_models_are_secured():
    acl = (DEMAND / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    rules = (DEMAND / "security" / "fix_isolation_rules.xml").read_text(encoding="utf-8")
    for model in NEW_MODELS:
        xmlid = "model_" + model.replace(".", "_")
        rows = [r.split(",") for r in acl.splitlines() if (",%s," % xmlid) in r]
        assert rows, model
        # nobody deletes; a plain employee only reads
        assert all(r[-1].strip() == "0" for r in rows), model
        plain = [r for r in rows if r[3] == "base.group_user"]
        assert plain and plain[0][4:8] == ["1", "0", "0", "0"], model
        assert 'ref="%s"' % xmlid in rules, "%s has no company rule" % model


def test_the_new_file_loads_after_the_models_it_extends():
    init = (DEMAND / "models" / "__init__.py").read_text(encoding="utf-8")
    assert init.index("fix_demand_ops") < init.index("fix_demand_capture")


def test_the_forecast_reads_the_history_overlay():
    """T-01: the overlay is applied when the forecast is computed - an applied
    adjustment that the moving average ignored would be a dead register."""
    ops = (DEMAND / "models" / "fix_demand_ops.py").read_text(encoding="utf-8")
    body = ops[ops.index("def action_compute_forecast") : ops.index("def action_approve")]
    assert '"fix.demand.adjustment"' in body and "_overlay(" in body
