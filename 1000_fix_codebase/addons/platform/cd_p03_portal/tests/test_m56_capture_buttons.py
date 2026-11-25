# M56 Payroll & Statutory: every sub-module page captures each record it
# covers (capture audit 2026-11-17).
#
# Before (HEAD c5feece6), evaluated with the engine's own fregCreate/fregPanels:
#   * pages 2 (BD Income Tax), 3 (Provident Fund), 4 (Gratuity) and
#     8 (BEFTN & Payslips) captured nothing: no "+ New", no chip;
#   * page 1 offered no "+ New"; pages 5, 7 and 9 listed WPPF allocations,
#     off-cycle payments and certificates with no chip;
#   * 15 working lists (statutory packs, recoveries, bank and MFS returns,
#     nominee accounts, variance review, gratuity provision...) sat on no page;
#   * no investment declaration (FR-PAY-013/014, BRU-PAY-10 H): the payslip
#     sent an investment of 0, so nobody ever received the rebate;
#   * no provident fund membership (FR-PAY-020): 10% + 10% for everyone;
#   * no opening gratuity provision (FR-PAY-022, Q-05): the first accrual
#     posted the whole history as one month's expense;
#   * a salary advance was paid and never recovered (FR-PAY-031/032).
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
CONTROLLER = HERE.parent / "controllers" / "a09" / "m56.py"
WRITABLE_FILE = HERE.parent / "controllers" / "a09" / "writable.py"
PAYROLL = HERE.parents[2] / "domain" / "h_people" / "cd_payroll_bd"

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
const mod = P03_MODULES.M56;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M56', map);
  const panels = fregPanels('M56', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M56:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M56.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: own || null, presets: (create && create.presets) || null, forms,
    reports: panels.reports.map((r) => ({ r, route: P03_REPORT_ROUTES['M56:' + r] || null })) };
});
const screen = (c) => ({
    kind: c.kind, model: c.model || null, create: c.create, report: c.report || null,
    tabs: (c.tabs || []).length, presets: c.presets || null, domain: c.domain || null,
    actions: (c.actions || []).map((a) => ({ m: a.m, kwargs: (a.asks || []).map((q) => q.kwarg).concat(a.kwarg ? [a.kwarg] : []) })),
    cols: c.cols || [],
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({
      name: f.name, readonly: !!f.readonly, required: !!f.required })) });
console.log(JSON.stringify({ subs, forms: mod.forms,
  labelled: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => id.startsWith('M56-')).map(([id, c]) => [id, screen(c)])) }));
"""


@pytest.fixture(scope="module")
def m56(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m56_capture")
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
    """{model: ({fields}, {methods})} defined or extended in cd_payroll_bd."""
    out = {}
    for path in (PAYROLL / "models").glob("*.py"):
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
    "1": ["M56-form-structure"],
    "2": ["M56-form-declaration", "M56-form-pack"],
    "3": ["M56-form-pf-member"],
    "4": ["M56-form-gratuity-opening"],
    "5": ["M56-form-bonus", "M56-form-wppf"],
    "6": ["M56-form-advance", "M56-form-advance-recovery"],
    "7": ["M56-form-run", "M56-form-offcycle", "M56-form-recovery"],
    "8": ["M56-form-bank-return", "M56-form-mfs-return"],
    "9": ["M56-form-return", "M56-form-certificate"],
    "10": ["M56-form-settlement", "M56-form-nominee-account"],
}

NEW_MODELS = ("fix.investment.declaration", "fix.pf.member", "fix.payroll.gratuity.opening")

# What a form must never let a person type: the state and every decision stamp.
NEVER_TYPED = {
    "fix.investment.declaration": {
        "name",
        "state",
        "eligible_amount",
        "recorded_by_id",
        "validated_by_id",
        "validated_on",
        "rejection_reason",
    },
    "fix.pf.member": {
        "name",
        "state",
        "recorded_by_id",
        "approved_by_id",
        "approved_on",
        "left_on",
        "leave_reason",
    },
    "fix.payroll.gratuity.opening": {
        "name",
        "state",
        "recorded_by_id",
        "approved_by_id",
        "approved_on",
    },
    "fix.payroll.recovery": {
        "name",
        "state",
        "employee_id",
        "approved_by_id",
        "approved_on",
        "approved_digest",
        "recovered_amount",
        "remaining_amount",
    },
}


def _sub(m56, no):
    return next(s for s in m56["subs"] if s["no"] == no)


def test_every_page_is_classified(m56):
    assert sorted(s["no"] for s in m56["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m56, no):
    sub = _sub(m56, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]} | {sub["create"]}
    missing = [form for form in [own, *others] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)


def test_a_record_made_on_a_sliced_page_lands_on_it(m56):
    """An advance made on Loans & Advances is an advance; a settlement part
    made on Final Settlement is a settlement - the chip forms preset it too."""
    assert _sub(m56, "6")["presets"] == {"payment_type": "advance"}
    assert _sub(m56, "10")["presets"] == {"payment_type": "settlement"}
    sc = m56["screens"]
    assert sc["M56-form-advance"]["presets"] == {"payment_type": "advance"}
    assert sc["M56-form-settlement"]["presets"] == {"payment_type": "settlement"}
    assert sc["M56-form-advance-recovery"]["presets"] == {"recovery_type": "advance"}
    for form, field in (
        ("fix.payroll.offcycle", "payment_type"),
        ("fix.payroll.recovery", "recovery_type"),
    ):
        assert field in _writable()[form], "%s.%s preset is never posted" % (form, field)


def test_sliced_lists_show_only_their_slice(m56):
    sc = m56["screens"]
    assert sc["M56-advances"]["domain"] == [["payment_type", "=", "advance"]]
    assert sc["M56-settlement"]["domain"] == [["payment_type", "=", "settlement"]]
    assert sc["M56-advance-recoveries"]["domain"] == [["recovery_type", "=", "advance"]]
    assert sc["M56-recoveries"]["domain"] == [["recovery_type", "=", "overpayment"]]


def test_each_captured_record_is_listed_on_its_page(m56):
    for sub in m56["subs"]:
        listed = {m56["screens"][s]["model"] for s in sub["screens"] if s in m56["screens"]}
        listed.add(sub["model"])
        captures = list(sub["forms"])
        if sub["create"]:
            captures.append({"model": m56["screens"][sub["create"]]["model"]})
        for f in captures:
            assert f["model"] in listed, "page %s captures %s but lists none" % (
                sub["no"],
                f["model"],
            )


def test_every_creatable_list_on_a_page_has_its_capture(m56):
    for sub in m56["subs"]:
        captured = {f["model"] for f in sub["forms"] if f["opens"]}
        if sub["create"]:
            captured.add(m56["screens"][sub["create"]]["model"])
        for sid in sub["screens"]:
            cfg = m56["screens"].get(sid, {})
            if cfg.get("kind") == "model_list" and cfg.get("create") is not False:
                assert cfg["model"] in captured, "page %s lists %s (%s) with no capture" % (
                    sub["no"],
                    cfg["model"],
                    sid,
                )


def test_every_working_screen_sits_on_a_page(m56):
    placed = {sid for s in m56["subs"] for sid in s["screens"]}
    placed |= {r["route"] for s in m56["subs"] for r in s["reports"]}
    orphans = [
        sid
        for sid, cfg in m56["screens"].items()
        if cfg["kind"] in ("model_list", "table_report")
        and sid not in placed
        and not sid.startswith("M56-rpt-")
    ]
    assert not orphans, orphans


def test_every_screen_on_a_page_has_a_navigation_label(m56):
    labelled = set(m56["labelled"])
    unlabelled = sorted(
        sid
        for sub in m56["subs"]
        for sid in sub["screens"]
        if sid in m56["screens"] and sid not in labelled
    )
    assert not unlabelled, unlabelled


def test_every_served_action_exists_on_its_model():
    classes = _model_classes()
    # the approval mixin (cd_hr_core / cd_workflow_engine) supplies the routed verbs
    generic = {"action_request_approval", "action_recall_approval"}
    for model, acts in _surfaces().items():
        methods = classes.get(model, (set(), set()))[1]
        missing = acts - methods - generic
        assert not missing, "%s serves %s, which the model lacks" % (model, sorted(missing))


def test_every_list_action_is_served(m56):
    surfaces = _surfaces()
    for sid, cfg in m56["screens"].items():
        if cfg["kind"] != "model_list" or not cfg["actions"]:
            continue
        served = surfaces[cfg["model"]]
        for act in cfg["actions"]:
            assert act["m"] in served, "%s offers %s, not served" % (sid, act["m"])


def test_every_form_field_exists_on_its_model(m56):
    classes = _model_classes()
    for sid, cfg in m56["screens"].items():
        if cfg["kind"] != "model_form" or cfg["model"] not in classes:
            continue
        known = classes[cfg["model"]][0] | {"name", "state", "active", "approval_state"}
        known |= {"create_uid", "create_date", "write_date"}
        unknown = [f["name"] for f in cfg["fields"] if f["name"] not in known]
        assert not unknown, "%s shows %s, not fields of %s" % (sid, unknown, cfg["model"])


@pytest.mark.parametrize("model", NEW_MODELS)
def test_new_registers_are_served_and_whitelisted(m56, model):
    assert model in _surfaces()
    forms = [
        c for c in m56["screens"].values() if c["kind"] == "model_form" and c["model"] == model
    ]
    assert forms, "%s has no workspace form" % model
    typed = {f["name"] for c in forms for f in c["fields"] if not f["readonly"]}
    assert _writable()[model] == typed


@pytest.mark.parametrize("model", sorted(NEVER_TYPED))
def test_stamps_are_never_typed(model):
    leaked = _writable().get(model, set()) & NEVER_TYPED[model]
    assert not leaked, (model, sorted(leaked))


def test_long_forms_are_tabbed(m56):
    """AGENTS.md: a form of more than 15 fields is split into tabs."""
    long_flat = [
        sid
        for sid, c in m56["screens"].items()
        if c["kind"] == "model_form" and len(c["fields"]) > 15 and not c["tabs"]
    ]
    assert not long_flat, long_flat


def test_decisions_ask_for_their_reason(m56):
    for sid, method in (
        ("M56-declarations", "action_reject"),
        ("M56-pf-members", "action_leave"),
    ):
        acts = {a["m"]: a for a in m56["screens"][sid]["actions"]}
        assert acts[method]["kwargs"] == ["reason"], sid
    acts = {a["m"]: a for a in m56["screens"]["M56-declarations"]["actions"]}
    assert acts["action_validate"]["kwargs"] == ["eligible_amount"]


def test_new_models_are_secured():
    acl = (PAYROLL / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    rules = (PAYROLL / "security" / "fix_isolation_rules.xml").read_text(encoding="utf-8")
    for model in NEW_MODELS:
        xmlid = "model_" + model.replace(".", "_")
        rows = [r.split(",") for r in acl.splitlines() if (",%s," % xmlid) in r]
        assert rows, model
        assert all(r[3].endswith("group_payroll_officer") for r in rows), model
        assert all(r[-1].strip() == "0" for r in rows), "%s: nobody deletes" % model
        assert 'ref="%s"' % xmlid in rules, "%s has no company rule" % model


def test_the_payslip_sends_the_validated_investment():
    """BRU-PAY-10: the calculation no longer sends a typed-in 0."""
    src = (PAYROLL / "models" / "fix_payroll.py").read_text(encoding="utf-8")
    assert '"investment_allowance": 0.0' not in src
    assert 'fix.investment.declaration"]._allowance_for' in src
    assert 'fix.pf.member"]._slip_rates' in src


def test_the_new_file_loads_after_the_models_it_extends():
    """It extends fix.payroll.offcycle: an _inherit before its _name fails to load."""
    init = (PAYROLL / "models" / "__init__.py").read_text(encoding="utf-8")
    body = init[init.index("from . import (") :]
    assert body.rstrip().endswith("fix_payroll_capture,\n)"), body
    assert "ruff: noqa: I001" in init
