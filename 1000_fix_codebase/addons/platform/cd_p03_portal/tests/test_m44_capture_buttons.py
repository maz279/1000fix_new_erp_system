# M44 Import, Trade Compliance & Landed Cost: every sub-module page captures
# each record it covers (capture audit 2026-11-16).
#
# Before (HEAD a94fb665), evaluated with the engine's own fregCreate/fregPanels:
#   * every page had a "+ New", but eight working lists - LC amendments, LC
#     payments, advance payments, the HS tariff master, restricted goods,
#     import permits, C&F agents and cargo insurance - sat on NO page, so
#     their records could be captured from no sub-module;
#   * pages 4 Eligibility & IRC, 5 Shipping & Insurance and 8 Landed Cost
#     offered no chip; page 1 listed proformas with no proforma capture;
#   * no cost document (FR-ITC-018/030/031, BRU-ITC-16 - the order's close
#     said "BRU-ITC-16 has no document model"), no LC discrepancy
#     (FR-ITC-016) and no customs query/examination (FR-ITC-028) existed, and
#     the shipment named no freight forwarder (FR-ITC-021, BRU-ITC-12).
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
CONTROLLER = HERE.parent / "controllers" / "a06" / "m44.py"
WRITABLE_FILE = HERE.parent / "controllers" / "a06" / "writable.py"
IMPORT = HERE.parents[2] / "domain" / "e_supply_chain" / "cd_import_order"

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
const mod = P03_MODULES.M44;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M44', map);
  const panels = fregPanels('M44', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M44:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M44.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: own || null, forms,
    reports: panels.reports.map((r) => ({ r, route: P03_REPORT_ROUTES['M44:' + r] || null })) };
});
console.log(JSON.stringify({ subs, forms: mod.forms,
  labelled: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => id.startsWith('M44-')).map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create, report: c.report || null,
    actions: (c.actions || []).map((a) => ({ m: a.m, kwargs: (a.asks || []).map((q) => q.kwarg).concat(a.kwarg ? [a.kwarg] : []) })),
    cols: c.cols || [],
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({
      name: f.name, readonly: !!f.readonly, required: !!f.required })) }])) }));
"""


@pytest.fixture(scope="module")
def m44(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m44_capture")
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
    """{model: {method names}} defined in cd_import_order's model files."""
    out = {}
    for path in (IMPORT / "models").glob("*.py"):
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
    "1": ["M44-form-order", "M44-form-proforma"],
    "2": [
        "M44-form-lc",
        "M44-form-lca",
        "M44-form-lc-amend",
        "M44-form-discrepancy",
        "M44-form-lc-pay",
        "M44-form-advance",
        "M44-form-cost",
    ],
    "3": ["M44-form-hs", "M44-form-tariff"],
    "4": ["M44-form-irc", "M44-form-restriction", "M44-form-permit", "M44-form-lca"],
    "5": ["M44-form-shipdoc", "M44-form-arrival", "M44-form-insurance"],
    "6": [
        "M44-form-arrival",
        "M44-form-boe",
        "M44-form-query",
        "M44-form-agent",
        "M44-form-cost",
    ],
    "7": ["M44-form-boe", "M44-form-tariff"],
    "8": ["M44-form-landed", "M44-form-cost"],
}

RECORDS = {
    "1": "fix.import.order",
    "2": "fix.import.lc",
    "3": "fix.import.hs",
    "4": "fix.import.irc",
    "5": "fix.import.shipdoc",
    "6": "fix.import.arrival",
    "7": "fix.import.boe",
    "8": "fix.import.landed",
}

NEW_MODELS = ("fix.import.cost", "fix.import.lc.discrepancy", "fix.import.customs.query")

# What a form must never let a person type: the state, every decision stamp
# and every derived figure (BRU-ITC-14/16, FR-ITC-016/028).
NEVER_TYPED = {
    "fix.import.cost": {
        "state",
        "amount_bdt",
        "variance",
        "variance_pct",
        "recorded_by_id",
        "reconciled_by_id",
        "reconciled_on",
        "rejection_reason",
    },
    "fix.import.lc.discrepancy": {"state", "decided_by_id", "decided_on", "decision_reason"},
    "fix.import.customs.query": {
        "state",
        "response",
        "responded_on",
        "outcome",
        "resolved_on",
        "answered_by_id",
        "resolved_by_id",
    },
}


def _sub(m44, no):
    return next(s for s in m44["subs"] if s["no"] == no)


def test_every_page_is_classified(m44):
    assert sorted(s["no"] for s in m44["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m44, no):
    sub = _sub(m44, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]}
    missing = [form for form in [own, *others] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)


@pytest.mark.parametrize("no", sorted(RECORDS, key=int))
def test_each_page_lists_its_own_record(m44, no):
    assert _sub(m44, no)["model"] == RECORDS[no]


def test_each_captured_record_is_listed_on_its_page(m44):
    for sub in m44["subs"]:
        listed = {m44["screens"][s]["model"] for s in sub["screens"] if s in m44["screens"]}
        for f in sub["forms"]:
            assert f["model"] in listed, "page %s captures %s but lists none" % (
                sub["no"],
                f["model"],
            )


def test_every_working_screen_sits_on_a_page(m44):
    placed = {sid for s in m44["subs"] for sid in s["screens"]}
    placed |= {r["route"] for s in m44["subs"] for r in s["reports"]}
    orphans = [
        sid
        for sid, cfg in m44["screens"].items()
        if cfg["kind"] in ("model_list", "table_report")
        and sid not in placed
        and not sid.startswith("M44-rpt-")
    ]
    assert not orphans, orphans


def test_every_screen_on_a_page_has_a_navigation_label(m44):
    """A list on a page but in no navigation group shows as its raw id."""
    labelled = set(m44["labelled"])
    unlabelled = sorted(
        sid
        for sub in m44["subs"]
        for sid in sub["screens"]
        if sid in m44["screens"]
        and m44["screens"][sid]["kind"] == "model_list"
        and sid not in labelled
    )
    assert not unlabelled, unlabelled


# the models this audit built or changed; the LC approval actions of older
# surfaces come from cd_workflow_engine's mixin, outside this module
TOUCHED = (*NEW_MODELS, "fix.import.landed", "fix.import.arrival")


def test_every_served_action_exists_on_its_model():
    methods = _model_methods()
    for model, acts in _surfaces().items():
        if model not in TOUCHED:
            continue
        missing = acts - methods.get(model, set())
        assert not missing, "%s serves %s, which the model lacks" % (model, sorted(missing))


def test_every_list_action_is_served(m44):
    surfaces = _surfaces()
    for sid, cfg in m44["screens"].items():
        if cfg["kind"] != "model_list" or not cfg["actions"]:
            continue
        served = surfaces.get(cfg["model"], set())
        for act in cfg["actions"]:
            if act["m"].startswith("__"):  # an engine action that opens a form
                continue
            assert act["m"] in served, "%s offers %s, not served" % (sid, act["m"])


@pytest.mark.parametrize("model", NEW_MODELS)
def test_new_registers_are_served_and_whitelisted(m44, model):
    assert model in _surfaces()
    forms = [
        c for c in m44["screens"].values() if c["kind"] == "model_form" and c["model"] == model
    ]
    assert forms, "%s has no workspace form" % model
    typed = {f["name"] for c in forms for f in c["fields"] if not f["readonly"]}
    assert _writable()[model] == typed


@pytest.mark.parametrize("model", sorted(NEVER_TYPED))
def test_stamps_and_derived_figures_are_never_typed(model):
    leaked = _writable().get(model, set()) & NEVER_TYPED[model]
    assert not leaked, (model, sorted(leaked))


def test_the_shipment_form_books_a_forwarder(m44):
    fields = {f["name"] for f in m44["screens"]["M44-form-arrival"]["fields"]}
    assert {"forwarder_id", "carrier", "booking_ref"} <= fields
    assert {"forwarder_id", "carrier", "booking_ref"} <= _writable()["fix.import.arrival"]


def test_new_models_are_secured():
    acl = (IMPORT / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    rules = (IMPORT / "security" / "fix_import_child_rules.xml").read_text(encoding="utf-8")
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
    init = (IMPORT / "models" / "__init__.py").read_text(encoding="utf-8")
    for base in ("fix_import_order", "fix_import_ops", "fix_import_compliance"):
        assert init.index(base) < init.index("fix_import_capture"), base


def test_close_no_longer_claims_cost_documents_are_unmodelled():
    order = (IMPORT / "models" / "fix_import_order.py").read_text(encoding="utf-8")
    assert "has no document model" not in order
