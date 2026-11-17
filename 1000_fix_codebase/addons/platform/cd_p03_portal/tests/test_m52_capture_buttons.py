# M52 AP & Employee Expense: every sub-module page captures each record it
# covers (capture audit 2026-11-17).
#
# Before (HEAD 94bf9e99), evaluated with the engine's own fregCreate/fregPanels:
#   * pages 2 (Matching), 3 (Approval) and 9 (GRNI) captured nothing;
#   * page 5 listed payee bank changes, and page 7 expense policies, per-diem
#     and mileage rates, with no chip, although their forms existed; expense
#     categories and grades sat on no page; the take-on wizard sat on none;
#   * the match tolerance was hard-coded (exact quantity, 0.01 on price) with
#     no record to configure it (FR-APE-005 P0);
#   * a blocked bill had no exception case: no type, owner, responsible
#     party or due date (FR-APE-007 P0, BRU-APE-03 H);
#   * no vendor dispute (FR-APE-017), no vendor statement reconciliation
#     (FR-APE-016), no kept ageing snapshot (FR-APE-013 P0, BRU-APE-23 H);
#   * GRNI was only a live report: nothing kept for a period end, no
#     unrecorded-liability estimate (FR-APE-031 P0, BRU-APE-22 H);
#   * "Advances & Cards" had no card record (FR-APE-038) and no link to the
#     supplier advance M52 pays.
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
CONTROLLER = HERE.parent / "controllers" / "a08" / "m52.py"
WRITABLE_FILE = HERE.parent / "controllers" / "a08" / "writable.py"
AP = HERE.parents[2] / "domain" / "g_finance" / "cd_ap_ext"

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
const mod = P03_MODULES.M52;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M52', map);
  const panels = fregPanels('M52', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M52:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M52.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: own || null, forms,
    reports: panels.reports.map((r) => ({ r, route: P03_REPORT_ROUTES['M52:' + r] || null })) };
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
  foreign: Object.fromEntries(Object.values(P03_FORM_CHIPS).filter((id) => typeof id === 'string' && !id.startsWith('M52-') && P03_DATA_SCREENS[id]).map((id) => [id, screen(P03_DATA_SCREENS[id])])),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => id.startsWith('M52-')).map(([id, c]) => [id, screen(c)])) }));
"""


@pytest.fixture(scope="module")
def m52(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m52_capture")
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
    """{model: ({fields}, {methods})} defined or extended in cd_ap_ext."""
    out = {}
    for path in (AP / "models").glob("*.py"):
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
    "1": ["M52-form-bill"],
    "2": ["M52-form-matchcase", "M52-form-tolerance"],
    "3": ["M52-form-matrix-change"],
    "4": [
        "M52-form-note",
        "M52-form-dispute",
        "M52-form-vstatement",
        "M52-form-snapshot",
        "M52-form-ap-takeon",
    ],
    "5": ["M52-form-aprun", "M52-form-bank-change"],
    "6": ["M52-form-taxprofile"],
    "7": [
        "M52-form-claim",
        "M52-form-policy",
        "M52-form-rate",
        "M52-form-expense-category",
        "M52-form-expense-grade",
    ],
    "8": ["M52-form-advance", "M16-form-advance", "M52-form-card", "M52-form-cardline"],
    "9": ["M52-form-grni"],
}

NEW_MODELS = (
    "fix.ap.match.tolerance",
    "fix.ap.match.exception",
    "fix.ap.dispute",
    "fix.ap.vendor.statement",
    "fix.ap.ageing.snapshot",
    "fix.ap.grni.accrual",
    "fix.expense.card",
    "fix.expense.card.transaction",
)
LINE_MODELS = ("fix.ap.ageing.snapshot.line", "fix.ap.grni.accrual.line")
# a draft (never decided) record may be deleted by its preparer
DRAFT_DELETABLE = {"fix.ap.vendor.statement", "fix.ap.grni.accrual", "fix.expense.card"}

# What a form must never let a person type: the state, every decision stamp
# and every derived figure.
NEVER_TYPED = {
    "fix.ap.match.tolerance": {
        "state",
        "supersedes_id",
        "requested_by_id",
        "requested_at",
        "approved_by_id",
        "approved_at",
        "name",
    },
    "fix.ap.match.exception": {
        "name",
        "state",
        "variance_detail",
        "opened_by_id",
        "resolved_by_id",
        "resolved_at",
        "vendor_id",
        "purchase_order_id",
        "bill_match_state",
        "age_days",
    },
    "fix.ap.dispute": {
        "name",
        "state",
        "raised_by_id",
        "raised_at",
        "resolved_by_id",
        "resolved_at",
        "bill_payable",
        "vendor_id",
    },
    "fix.ap.vendor.statement": {
        "name",
        "state",
        "ledger_balance",
        "open_bill_count",
        "difference",
        "prepared_by_id",
        "signed_by_id",
        "signed_at",
    },
    "fix.ap.ageing.snapshot": {
        "name",
        "taken_by_id",
        "taken_at",
        "current",
        "d1_30",
        "d31_60",
        "d61_90",
        "d90",
        "total",
        "vendor_count",
        "basis",
        "line_ids",
    },
    "fix.ap.grni.accrual": {
        "name",
        "state",
        "line_ids",
        "line_count",
        "grni_total",
        "clearing_balance",
        "clearing_note",
        "computed_by_id",
        "confirmed_by_id",
    },
    "fix.expense.card": {"unexplained_count", "name"},
    "fix.expense.card.transaction": {
        "state",
        "holder_id",
        "explained_by_id",
        "approved_by_id",
        "approved_at",
    },
    "fix.vendor.invoice": {"open_match_case_id", "open_dispute_id", "match_state", "match_detail"},
}


def _sub(m52, no):
    return next(s for s in m52["subs"] if s["no"] == no)


def _screen(m52, sid):
    return m52["screens"].get(sid) or m52["foreign"][sid]


def test_every_page_is_classified(m52):
    assert sorted(s["no"] for s in m52["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m52, no):
    sub = _sub(m52, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]} | {sub["create"]}
    missing = [form for form in [own, *others] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)


def test_no_page_offers_a_record_the_model_computes(m52):
    """Withholding lines, claim lines and take-on lines are never typed."""
    for sid in ("M52-tds", "M52-claim-lines", "M52-ap-takeon-lines", "M52-match", "M52-approval"):
        assert m52["screens"][sid]["create"] is False, sid
    for sub in m52["subs"]:
        assert sub["create"] not in ("M52-form-claim-line",), sub["no"]


def test_each_captured_record_is_listed_on_its_page(m52):
    for sub in m52["subs"]:
        listed = {m52["screens"][s]["model"] for s in sub["screens"] if s in m52["screens"]}
        listed.add(sub["model"])
        captures = list(sub["forms"])
        if sub["create"]:
            captures.append({"model": _screen(m52, sub["create"])["model"]})
        for f in captures:
            if f["model"] == "fix.purchase.advance":
                continue  # M16's supplier advance, listed on M16's own page
            assert f["model"] in listed, "page %s captures %s but lists none" % (
                sub["no"],
                f["model"],
            )


def test_every_creatable_list_on_a_page_has_its_capture(m52):
    for sub in m52["subs"]:
        captured = {f["model"] for f in sub["forms"] if f["opens"]}
        if sub["create"]:
            captured.add(_screen(m52, sub["create"])["model"])
        for sid in sub["screens"]:
            cfg = m52["screens"].get(sid, {})
            if cfg.get("kind") == "model_list" and cfg.get("create") is not False:
                assert cfg["model"] in captured, "page %s lists %s (%s) with no capture" % (
                    sub["no"],
                    cfg["model"],
                    sid,
                )


def test_every_working_screen_sits_on_a_page(m52):
    placed = {sid for s in m52["subs"] for sid in s["screens"]}
    placed |= {r["route"] for s in m52["subs"] for r in s["reports"]}
    orphans = [
        sid
        for sid, cfg in m52["screens"].items()
        if cfg["kind"] in ("model_list", "table_report") and sid not in placed
    ]
    assert not orphans, orphans


def test_every_screen_on_a_page_has_a_navigation_label(m52):
    labelled = set(m52["labelled"])
    unlabelled = sorted(
        sid
        for sub in m52["subs"]
        for sid in sub["screens"]
        if sid in m52["screens"]
        and m52["screens"][sid]["kind"] == "model_list"
        and sid not in labelled
    )
    assert not unlabelled, unlabelled


def test_every_served_action_exists_on_its_model():
    classes = _model_classes()
    for model, acts in _surfaces().items():
        if model not in classes:
            continue  # served models defined outside cd_ap_ext (take-on, cd_gl_ext)
        missing = acts - classes[model][1]
        assert not missing, "%s serves %s, which the model lacks" % (model, sorted(missing))


def test_every_list_action_is_served(m52):
    surfaces = _surfaces()
    for sid, cfg in m52["screens"].items():
        if cfg["kind"] != "model_list" or not cfg["actions"]:
            continue
        if cfg["model"] not in surfaces:
            continue  # served by another A08 module (the registry test checks those)
        served = surfaces[cfg["model"]]
        for act in cfg["actions"]:
            assert act["m"] in served, "%s offers %s, not served" % (sid, act["m"])


def test_every_form_field_exists_on_its_model(m52):
    classes = _model_classes()
    for sid, cfg in m52["screens"].items():
        if cfg["kind"] != "model_form" or cfg["model"] not in NEW_MODELS:
            continue
        known = classes[cfg["model"]][0] | {"name", "state", "active"}
        unknown = [f["name"] for f in cfg["fields"] if f["name"] not in known]
        assert not unknown, "%s shows %s, not fields of %s" % (sid, unknown, cfg["model"])


@pytest.mark.parametrize("model", NEW_MODELS)
def test_new_registers_are_served_and_whitelisted(m52, model):
    assert model in _surfaces()
    forms = [
        c for c in m52["screens"].values() if c["kind"] == "model_form" and c["model"] == model
    ]
    assert forms, "%s has no workspace form" % model
    typed = {f["name"] for c in forms for f in c["fields"] if not f["readonly"]}
    assert _writable()[model] == typed


@pytest.mark.parametrize("model", LINE_MODELS)
def test_computed_lines_are_never_written_through_the_workspace(model):
    assert _writable().get(model, set()) == set()


@pytest.mark.parametrize("model", sorted(NEVER_TYPED))
def test_stamps_and_derived_figures_are_never_typed(model):
    leaked = _writable().get(model, set()) & NEVER_TYPED[model]
    assert not leaked, (model, sorted(leaked))


def test_long_forms_are_tabbed(m52):
    """AGENTS.md: a form of more than 15 fields is split into tabs."""
    long_flat = [
        sid
        for sid, c in m52["screens"].items()
        if c["kind"] == "model_form" and len(c["fields"]) > 15 and not c["tabs"]
    ]
    assert not long_flat, long_flat


def test_match_exceptions_open_cases_and_cases_close_only_on_their_cause(m52):
    match = {a["m"] for a in m52["screens"]["M52-match"]["actions"]}
    assert "action_open_match_case" in match
    assert "open_match_case_id" in m52["screens"]["M52-match"]["cols"]
    cases = {a["m"] for a in m52["screens"]["M52-match-cases"]["actions"]}
    assert cases == {"action_resolve"}, "a case has no override or release action"


def test_the_grni_page_keeps_the_period_end_accrual(m52):
    sub = _sub(m52, "9")
    assert sub["model"] == "fix.ap.grni.accrual"
    acts = {a["m"] for a in m52["screens"]["M52-grni-accruals"]["actions"]}
    assert acts == {"action_compute", "action_confirm"}


def test_an_ageing_snapshot_has_no_action_that_changes_it(m52):
    assert not m52["screens"]["M52-ageing-snapshots"]["actions"]
    assert _surfaces()["fix.ap.ageing.snapshot"] == set()


def test_new_models_are_secured():
    acl = (AP / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    rules = (AP / "security" / "fix_isolation_rules.xml").read_text(encoding="utf-8")
    for model in (*NEW_MODELS, *LINE_MODELS):
        xmlid = "model_" + model.replace(".", "_")
        rows = [r.split(",") for r in acl.splitlines() if (",%s," % xmlid) in r]
        assert rows, model
        if model not in DRAFT_DELETABLE:
            assert all(r[-1].strip() == "0" for r in rows), "%s: nobody deletes" % model
        ro = [r for r in rows if r[3] == "account.group_account_readonly"]
        assert ro and ro[0][4:8] == ["1", "0", "0", "0"], model
        assert not [r for r in rows if r[3] == "base.group_user"], "%s: finance only" % model
        assert 'ref="%s"' % xmlid in rules, "%s has no company rule" % model


def test_the_new_file_loads_after_the_models_it_extends():
    """It extends the bill (fix_ap_ext) and the payment run
    (fix_ap_payment_run): it is imported after every other model file."""
    init = (AP / "models" / "__init__.py").read_text(encoding="utf-8")
    names = re.findall(r"^    (\w+),$", init, re.M)
    assert names[-1] == "fix_ap_capture", names
    assert "ruff: noqa: I001" in init
