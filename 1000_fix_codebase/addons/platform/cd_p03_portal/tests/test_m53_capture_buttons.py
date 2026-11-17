# M53 Revenue Recognition & Settlement: every sub-module page captures the
# record it is about (capture audit 2026-11-17).
#
# Before (HEAD 94bf9e99), evaluated with the engine's own fregCreate/fregPanels:
#   * page 2 (Allocation & SSP): "+ New" opened a Performance Obligation; no
#     stand-alone selling price existed (FR-REV-006 P0, AUT-REV-03), so the
#     SSP of every obligation was typed on its contract with nothing to check;
#   * page 4 (Modifications & Reversals): "+ New" opened a Subscription; no
#     contract modification existed (FR-REV-008, BRU-REV-04 H) and the system
#     told users to cancel and re-create obligations, losing the history;
#   * page 5 (Principal vs Agent): no capture at all; no declared position
#     (FR-REV-007 P0, BRU-REV-08/09 H) although marketplace commission was
#     booked as an agent with nothing declared;
#   * page 7 (Seller Settlement): "+ New" opened a typed Seller Statement,
#     which the model can never issue (a statement is issued by its paid
#     payout run); no payout hold (FR-REV-035 P0, BRU-REV-16 H) and no
#     settlement dispute holding only the disputed lines (FR-REV-039,
#     BRU-REV-17 H);
#   * page 8 (Partner Payouts): no capture at all;
#   * page 6 (Commission Ledger): no "+ New";
#   * the warranty provision and policy lists, the held schedules and the
#     unsourced commissions sat on no page.
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
CONTROLLER = HERE.parent / "controllers" / "a08" / "m53.py"
WRITABLE_FILE = HERE.parent / "controllers" / "a08" / "writable.py"
DOMAIN = HERE.parents[2] / "domain"
SETTLEMENT = DOMAIN / "g_finance" / "cd_settlement_ext"
SUBSCRIPTION = DOMAIN / "c_commercial" / "cd_subscription"
PARTNER = DOMAIN / "b_customer_engagement" / "cd_partner"

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
const mod = P03_MODULES.M53;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M53', map);
  const panels = fregPanels('M53', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M53:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M53.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: own || null, forms,
    reports: panels.reports.map((r) => ({ r, route: P03_REPORT_ROUTES['M53:' + r] || null })) };
});
const screen = (c) => ({
    kind: c.kind, model: c.model || null, create: c.create, report: c.report || null,
    tabs: (c.tabs || []).length,
    actions: (c.actions || []).map((a) => ({ m: a.m, kw: a.kw || null,
      kwargs: (a.asks || []).map((q) => q.kwarg).concat(a.kwarg ? [a.kwarg] : []) })),
    cols: c.cols || [],
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({
      name: f.name, readonly: !!f.readonly, required: !!f.required })) });
console.log(JSON.stringify({ subs, forms: mod.forms,
  labelled: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => id.startsWith('M53-')).map(([id, c]) => [id, screen(c)])) }));
"""


@pytest.fixture(scope="module")
def m53(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m53_capture")
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
    """{model: ({fields}, {methods})} defined or extended in the M53 modules."""
    out = {}
    paths = [
        *(SETTLEMENT / "models").glob("*.py"),
        *(SUBSCRIPTION / "models").glob("*.py"),
        *(PARTNER / "models").glob("*.py"),
    ]
    for path in paths:
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
    "1": ["M53-form-obligation", "M53-form-provision", "M53-form-policy"],
    "2": ["M53-form-ssp", "M53-form-obligation"],
    "3": ["M53-form-schedule"],
    "4": ["M53-form-modification", "M53-form-subscription"],
    "5": ["M53-form-presentation"],
    "6": ["M53-form-scheme"],
    "7": ["M53-form-payoutrun", "M53-form-hold", "M53-form-recon"],
    "8": ["M53-form-payoutrun", "M53-form-hold"],
    "9": ["M53-form-clawback"],
}

NEW_MODELS = (
    "fix.ssp",
    "fix.contract.modification",
    "fix.revenue.presentation",
    "fix.payout.hold",
)

# What a form must never let a person type: the state, every decision stamp
# and every derived figure.
NEVER_TYPED = {
    "fix.ssp": {
        "state",
        "requested_by_id",
        "requested_at",
        "approved_by_id",
        "approved_at",
        "reject_reason",
        "effective_to",
        "superseded_by_id",
        "company_id",
    },
    "fix.contract.modification": {
        "name",
        "state",
        "requested_by_id",
        "approved_by_id",
        "approved_at",
        "reject_reason",
        "catchup_amount",
        "catchup_schedule_id",
        "current_price",
        "line_ids",
    },
    "fix.contract.modification.line": {
        "new_allocation",
        "remaining_amount",
        "catchup_amount",
        "new_schedule_id",
    },
    "fix.revenue.presentation": {
        "state",
        "requested_by_id",
        "approved_by_id",
        "approved_at",
        "reject_reason",
        "effective_to",
    },
    "fix.payout.hold": {
        "name",
        "state",
        "scope",
        "held_amount",
        "raised_by_id",
        "raised_at",
        "released_by_id",
        "released_at",
        "release_reason",
        "outcome",
        "adjustment_id",
    },
    "fix.seller.statement": {
        "seller_partner_id",
        "period",
        "gross_gmv",
        "commission_amount",
        "tds_withheld",
        "platform_fee",
        "clawback_amount",
        "net_payable",
        "state",
    },
    "fix.performance.obligation": {"ssp_id", "ssp_basis", "allocated_amount", "state"},
}


def _sub(m53, no):
    return next(s for s in m53["subs"] if s["no"] == no)


def test_every_page_is_classified(m53):
    assert sorted(s["no"] for s in m53["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m53, no):
    sub = _sub(m53, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]} | {sub["create"]}
    missing = [form for form in [own, *others] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)


def test_the_page_new_is_the_page_s_own_record(m53):
    """Page 2 is about SSPs, 4 about modifications, 5 about the position."""
    for no, model in (
        ("2", "fix.ssp"),
        ("4", "fix.contract.modification"),
        ("5", "fix.revenue.presentation"),
    ):
        sub = _sub(m53, no)
        assert sub["model"] == model
        assert m53["screens"][sub["create"]]["model"] == model


def test_seller_statements_are_never_typed(m53):
    """A statement is issued by its paid payout run (BRU-REV-21)."""
    assert m53["screens"]["M53-sellers"]["create"] is False
    form = m53["screens"]["M53-form-statement"]
    assert form["create"] is False
    assert not [f["name"] for f in form["fields"] if not f["readonly"]]
    assert _writable()["fix.seller.statement"] == set()
    for sub in m53["subs"]:
        assert sub["create"] != "M53-form-statement", sub["no"]


def test_each_captured_record_is_listed_on_its_page(m53):
    for sub in m53["subs"]:
        listed = {m53["screens"][s]["model"] for s in sub["screens"] if s in m53["screens"]}
        listed.add(sub["model"])
        captures = list(sub["forms"])
        if sub["create"]:
            captures.append({"model": m53["screens"][sub["create"]]["model"]})
        for f in captures:
            assert f["model"] in listed, "page %s captures %s but lists none" % (
                sub["no"],
                f["model"],
            )


def test_every_creatable_list_on_a_page_has_its_capture(m53):
    for sub in m53["subs"]:
        captured = {f["model"] for f in sub["forms"] if f["opens"]}
        if sub["create"]:
            captured.add(m53["screens"][sub["create"]]["model"])
        for sid in sub["screens"]:
            cfg = m53["screens"].get(sid, {})
            if cfg.get("kind") == "model_list" and cfg.get("create") is not False:
                assert cfg["model"] in captured, "page %s lists %s (%s) with no capture" % (
                    sub["no"],
                    cfg["model"],
                    sid,
                )


def test_every_working_screen_sits_on_a_page(m53):
    placed = {sid for s in m53["subs"] for sid in s["screens"]}
    placed |= {r["route"] for s in m53["subs"] for r in s["reports"]}
    orphans = [
        sid
        for sid, cfg in m53["screens"].items()
        if cfg["kind"] in ("model_list", "table_report") and sid not in placed
    ]
    assert not orphans, orphans


def test_every_screen_on_a_page_has_a_navigation_label(m53):
    labelled = set(m53["labelled"])
    unlabelled = sorted(
        sid
        for sub in m53["subs"]
        for sid in sub["screens"]
        if sid in m53["screens"]
        and m53["screens"][sid]["kind"] == "model_list"
        and sid not in labelled
    )
    assert not unlabelled, unlabelled


def test_every_served_action_exists_on_its_model():
    classes = _model_classes()
    for model, acts in _surfaces().items():
        methods = classes.get(model, (set(), set()))[1]
        missing = acts - methods
        # the DOFA mixins (cd_workflow_engine / cd_billing_engine) supply these
        missing -= {"action_recall_approval", "action_dofa_approve"}
        assert not missing, "%s serves %s, which the model lacks" % (model, sorted(missing))


def test_every_list_action_is_served(m53):
    surfaces = _surfaces()
    for sid, cfg in m53["screens"].items():
        if cfg["kind"] != "model_list" or not cfg["actions"]:
            continue
        served = surfaces[cfg["model"]]
        for act in cfg["actions"]:
            assert act["m"] in served, "%s offers %s, not served" % (sid, act["m"])


def test_every_new_form_field_exists_on_its_model(m53):
    classes = _model_classes()
    for sid, cfg in m53["screens"].items():
        if cfg["kind"] != "model_form" or cfg["model"] not in NEW_MODELS:
            continue
        known = classes[cfg["model"]][0] | {"name", "state", "active"}
        unknown = [f["name"] for f in cfg["fields"] if f["name"] not in known]
        assert not unknown, "%s shows %s, not fields of %s" % (sid, unknown, cfg["model"])


@pytest.mark.parametrize("model", NEW_MODELS)
def test_new_registers_are_served_and_whitelisted(m53, model):
    assert model in _surfaces()
    forms = [
        c for c in m53["screens"].values() if c["kind"] == "model_form" and c["model"] == model
    ]
    assert forms, "%s has no workspace form" % model
    typed = {f["name"] for c in forms for f in c["fields"] if not f["readonly"]}
    assert _writable()[model] == typed


@pytest.mark.parametrize("model", sorted(NEVER_TYPED))
def test_stamps_and_derived_figures_are_never_typed(model):
    leaked = _writable().get(model, set()) & NEVER_TYPED[model]
    assert not leaked, (model, sorted(leaked))


def test_long_forms_are_tabbed(m53):
    """AGENTS.md: a form of more than 15 fields is split into tabs."""
    long_flat = [
        sid
        for sid, c in m53["screens"].items()
        if c["kind"] == "model_form" and len(c["fields"]) > 15 and not c["tabs"]
    ]
    assert not long_flat, long_flat


def test_a_dispute_is_closed_with_its_coded_outcome(m53):
    acts = [a for a in m53["screens"]["M53-holds"]["actions"] if a["m"] == "action_release"]
    outcomes = {a["kw"]["outcome"] for a in acts}
    assert outcomes == {"resolved", "upheld", "partly_upheld", "rejected"}
    assert all(a["kwargs"] == ["reason"] for a in acts)


def test_rejections_ask_for_their_reason(m53):
    for sid in ("M53-ssp", "M53-modifications", "M53-presentation"):
        acts = {a["m"]: a for a in m53["screens"][sid]["actions"]}
        assert acts["action_reject"]["kwargs"] == ["reason"], sid


def test_new_models_are_secured():
    for module, models in (
        (SUBSCRIPTION, ("fix.ssp", "fix.contract.modification", "fix.contract.modification.line")),
        (SETTLEMENT, ("fix.revenue.presentation", "fix.payout.hold")),
    ):
        acl = (module / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
        rules = (module / "security" / "fix_isolation_rules.xml").read_text(encoding="utf-8")
        for model in models:
            xmlid = "model_" + model.replace(".", "_")
            rows = [r.split(",") for r in acl.splitlines() if (",%s," % xmlid) in r]
            assert rows, model
            assert all(r[-1].strip() == "0" for r in rows), "%s: nobody deletes" % model
            ro = [r for r in rows if r[3] == "account.group_account_readonly"]
            assert ro and ro[0][4:8] == ["1", "0", "0", "0"], model
            assert 'ref="%s"' % xmlid in rules, "%s has no company rule" % model
    acl = (SUBSCRIPTION / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    lines = [
        r.split(",") for r in acl.splitlines() if ",model_fix_contract_modification_line," in r
    ]
    assert all(r[5:8] == ["0", "0", "0"] for r in lines), "lines are written by the model only"


def test_the_capture_file_loads_after_the_models_it_extends():
    """It extends the commission ledger and the payout run (fix_settlement_ext):
    an _inherit before its _name fails to load."""
    init = (SETTLEMENT / "models" / "__init__.py").read_text(encoding="utf-8")
    names = re.findall(r"^    (\w+),$", init, re.M)
    assert names[-1] == "fix_settlement_capture", names
    assert "ruff: noqa: I001" in init
    # the subscription file imports fix_subscription itself before extending it
    src = (SUBSCRIPTION / "models" / "fix_revenue_capture.py").read_text(encoding="utf-8")
    assert "from .fix_subscription import" in src
