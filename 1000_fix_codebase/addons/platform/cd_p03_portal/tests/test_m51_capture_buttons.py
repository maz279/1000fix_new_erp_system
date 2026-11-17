# M51 Tax & Regulatory (BD): every sub-module page captures each record it
# covers (capture audit 2026-11-17).
#
# Before (HEAD 94bf9e99), evaluated with the engine's own fregCreate/fregPanels:
#   * pages 3 (Mushak Registers), 5 (VDS) and 8 (High-Value Register) had no
#     "+ New"; pages 5 and 8 captured nothing at all;
#   * page 4 (VAT Return 9.1) had no chip, and a filed return could not be
#     amended: no separately evidenced amendment (BRU-TAX-15 H);
#   * page 1 listed statutory parameters and page 9 audit packs with no chip,
#     although both forms existed; the SD & AT report sat on no page;
#   * no record of the declared marketplace VAT model (FR-TAX-045 P0,
#     BRU-TAX-16/17 H, decision D-03);
#   * no record of an NBR query, audit notice or assessment (AUT-TAX-22);
#   * VDS deducted by customers (FR-TAX-039) and vendor PSR / exemption status
#     (FR-TAX-007, BRU-TAX-08/26) were on no M51 page;
#   * the high-value cash NID threshold was a hard-coded 50,000 in M20, not
#     M51 master data (FR-TAX-044, BRU-TAX-01).
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
A08 = HERE.parent / "controllers" / "a08"
CONTROLLER = A08 / "m51.py"
WRITABLE_FILE = A08 / "writable.py"
TAX = HERE.parents[2] / "domain" / "g_finance" / "cd_tax_engine_bd"
BILLING = HERE.parents[2] / "domain" / "g_finance" / "cd_billing_engine"

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
const mod = P03_MODULES.M51;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M51', map);
  const panels = fregPanels('M51', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M51:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M51.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: own || null, forms,
    reports: panels.reports.map((r) => ({ r, route: P03_REPORT_ROUTES['M51:' + r] || null })) };
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
  foreign: Object.fromEntries(Object.values(P03_FORM_CHIPS).filter((id) => typeof id === 'string' && !id.startsWith('M51-') && P03_DATA_SCREENS[id]).map((id) => [id, screen(P03_DATA_SCREENS[id])])),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => id.startsWith('M51-')).map(([id, c]) => [id, screen(c)])) }));
"""


@pytest.fixture(scope="module")
def m51(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m51_capture")
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


def _surface_actions(path):
    """{model: {actions}} of one A08 controller's SURFACES (set literals and
    the module's MASTER_ACTIONS)."""
    master = set()
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "MASTER_ACTIONS"
        ):
            master = {ast.literal_eval(e) for e in node.value.elts}
    out = {}
    value = _assigned(path, "SURFACES")
    for key, conf in zip(value.keys, value.values, strict=True):
        acts = set()
        for k, v in zip(conf.keys, conf.values, strict=True):
            if ast.literal_eval(k) != "actions":
                continue
            if isinstance(v, ast.Set):
                acts = {ast.literal_eval(e) for e in v.elts}
            elif isinstance(v, ast.Call) and getattr(v.func, "id", "") == "set" and v.args:
                acts = set(master)
        out[ast.literal_eval(key)] = acts
    return out


def _surfaces():
    return _surface_actions(CONTROLLER)


def _all_a08_surfaces():
    out = {}
    for path in sorted(A08.glob("m*.py")):
        for model, acts in _surface_actions(path).items():
            out.setdefault(model, set()).update(acts)
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


MIXIN_FIELDS = {
    # fix.tax.effective.mixin / fix.tax.master.approval.mixin (fix_tax_master.py)
    "date_from",
    "date_to",
    "source_note",
    "state",
    "signoff_state",
    "adviser_reference",
    "adviser_reference_input",
    "cfo_signed_by_id",
    "verify_with_adviser",
}


def _model_classes():
    """{model: ({fields}, {methods})} defined or extended in cd_tax_engine_bd."""
    out = {}
    for path in (TAX / "models").glob("*.py"):
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
    "1": ["M51-form-treatment", "M51-form-rate", "M51-form-tparam", "M51-form-mktmodel"],
    "2": ["M51-form-inputcredit"],
    "3": ["M51-form-correction"],
    "4": ["M51-form-vatreturn", "M51-form-amendment"],
    "5": ["M20-form-vds", "M52-form-taxprofile"],
    "6": ["M51-form-tdsreturn", "M52-form-taxprofile"],
    "7": ["M51-form-challan"],
    "8": ["M51-form-tparam"],
    "9": ["M51-form-duerule", "M51-form-filing", "M51-form-audit", "M51-form-notice"],
}

NEW_MODELS = ("fix.marketplace.tax.model", "fix.vat.return.amendment", "fix.tax.notice")

# What a form must never let a person type: the state, every decision stamp
# and every derived figure.
NEVER_TYPED = {
    "fix.marketplace.tax.model": {
        "state",
        "basis_of_charge",
        "signoff_state",
        "verify_with_adviser",
        "proposed_by_id",
        "adviser_reference",
        "adviser_verified_by_id",
        "activated_by_id",
        "cfo_signed_by_id",
    },
    "fix.vat.return.amendment": {
        "name",
        "state",
        "amended_net",
        "previous_net",
        "difference",
        "nbr_acknowledgement",
        "prepared_by_id",
        "submitted_at",
        "approved_by_id",
        "approved_at",
        "filed_by_id",
        "filed_at",
        "reject_reason",
    },
    "fix.tax.notice": {
        "name",
        "state",
        "audit_pack_id",
        "responded_by_id",
        "responded_at",
        "closed_by_id",
        "closed_at",
        "days_to_due",
        "overdue",
    },
    "fix.tax.parameter": {"state", "signoff_state", "verify_with_adviser", "cfo_signed_by_id"},
}


def _sub(m51, no):
    return next(s for s in m51["subs"] if s["no"] == no)


def _screen(m51, sid):
    return m51["screens"].get(sid) or m51["foreign"][sid]


def test_every_page_is_classified(m51):
    assert sorted(s["no"] for s in m51["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m51, no):
    sub = _sub(m51, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]} | {sub["create"]}
    missing = [form for form in [own, *others] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)


def test_every_chip_opens_a_form(m51):
    for sub in m51["subs"]:
        dead = [f["f"] for f in sub["forms"] if not f["opens"]]
        assert not dead, "page %s offers %s, which open no form" % (sub["no"], dead)


def test_no_page_offers_a_record_the_engine_writes(m51):
    """Register rows, withholding lines and certificates are written by the
    engine from posted documents: none of them is typed."""
    for sid in (
        "M51-mushak62",
        "M51-mushak63",
        "M51-unclassified",
        "M51-mushak61",
        "M51-tds-lines",
        "M51-vds",
        "M51-certs",
    ):
        assert m51["screens"][sid]["create"] is False, sid
    engine_models = {"fix.mushak.register", "fix.withholding.line", "fix.withholding.certificate"}
    for sub in m51["subs"]:
        if sub["create"]:
            assert _screen(m51, sub["create"])["model"] not in engine_models, sub["no"]


def test_each_captured_record_is_listed_on_its_page(m51):
    for sub in m51["subs"]:
        listed = {_screen(m51, s)["model"] for s in sub["screens"] if s in m51["screens"]}
        listed.add(sub["model"])
        captures = list(sub["forms"])
        if sub["create"]:
            captures.append({"model": _screen(m51, sub["create"])["model"]})
        for f in captures:
            assert f["model"] in listed, "page %s captures %s but lists none" % (
                sub["no"],
                f["model"],
            )


def test_every_creatable_list_on_a_page_has_its_capture(m51):
    for sub in m51["subs"]:
        captured = {f["model"] for f in sub["forms"] if f["opens"]}
        if sub["create"]:
            captured.add(_screen(m51, sub["create"])["model"])
        for sid in sub["screens"]:
            cfg = m51["screens"].get(sid, {})
            if cfg.get("kind") == "model_list" and cfg.get("create") is not False:
                assert cfg["model"] in captured, "page %s lists %s (%s) with no capture" % (
                    sub["no"],
                    cfg["model"],
                    sid,
                )


def test_every_working_screen_sits_on_a_page(m51):
    placed = {sid for s in m51["subs"] for sid in s["screens"]}
    placed |= {r["route"] for s in m51["subs"] for r in s["reports"]}
    orphans = [
        sid
        for sid, cfg in m51["screens"].items()
        if cfg["kind"] in ("model_list", "table_report") and sid not in placed
    ]
    assert not orphans, orphans


def test_every_screen_on_a_page_has_a_navigation_label(m51):
    labelled = set(m51["labelled"])
    unlabelled = sorted(
        sid
        for sub in m51["subs"]
        for sid in sub["screens"]
        if sid in m51["screens"]
        and m51["screens"][sid]["kind"] == "model_list"
        and sid not in labelled
    )
    assert not unlabelled, unlabelled


def test_every_served_action_exists_on_its_model():
    classes = _model_classes()
    for model, acts in _surfaces().items():
        methods = set()
        for name, (_flds, meths) in classes.items():
            if name in (model, "fix.tax.master.approval.mixin", "fix.tax.effective.mixin"):
                methods |= meths
        missing = acts - methods
        assert not missing, "%s serves %s, which the model lacks" % (model, sorted(missing))


def test_every_list_action_is_served(m51):
    surfaces = _all_a08_surfaces()
    for sid, cfg in m51["screens"].items():
        if cfg["kind"] != "model_list" or not cfg["actions"]:
            continue
        served = surfaces.get(cfg["model"], set())
        for act in cfg["actions"]:
            assert act["m"] in served, "%s offers %s, not served" % (sid, act["m"])


def test_every_list_model_is_served(m51):
    surfaces = _all_a08_surfaces()
    for sid, cfg in m51["screens"].items():
        if cfg["kind"] in ("model_list", "model_form"):
            assert cfg["model"] in surfaces, "%s reads %s, which no A08 surface serves" % (
                sid,
                cfg["model"],
            )


def test_every_form_field_exists_on_its_tax_model(m51):
    classes = _model_classes()
    for sid, cfg in m51["screens"].items():
        if cfg["kind"] != "model_form" or cfg["model"] not in NEW_MODELS:
            continue
        known = classes[cfg["model"]][0] | MIXIN_FIELDS | {"name", "active"}
        unknown = [f["name"] for f in cfg["fields"] if f["name"] not in known]
        assert not unknown, "%s shows %s, not fields of %s" % (sid, unknown, cfg["model"])


@pytest.mark.parametrize("model", NEW_MODELS)
def test_new_registers_are_served_and_whitelisted(m51, model):
    assert model in _surfaces()
    forms = [
        c for c in m51["screens"].values() if c["kind"] == "model_form" and c["model"] == model
    ]
    assert forms, "%s has no workspace form" % model
    typed = {f["name"] for c in forms for f in c["fields"] if not f["readonly"]}
    assert _writable()[model] == typed


@pytest.mark.parametrize("model", sorted(NEVER_TYPED))
def test_stamps_and_derived_figures_are_never_typed(model):
    leaked = _writable().get(model, set()) & NEVER_TYPED[model]
    assert not leaked, (model, sorted(leaked))


def test_long_forms_are_tabbed(m51):
    """AGENTS.md: a form of more than 15 fields is split into tabs."""
    long_flat = [
        sid
        for sid, c in m51["screens"].items()
        if c["kind"] == "model_form" and len(c["fields"]) > 15 and not c["tabs"]
    ]
    assert not long_flat, long_flat


def test_amendment_and_notice_decisions_ask_for_their_reason(m51):
    acts = {a["m"]: a for a in m51["screens"]["M51-amendments"]["actions"]}
    assert acts["action_reject"]["kwargs"] == ["reason"]
    assert acts["action_mark_filed"]["kwargs"] == ["reference"]
    notice = {a["m"] for a in m51["screens"]["M51-notices"]["actions"]}
    assert notice == {"action_generate_pack", "action_record_response", "action_close"}


def test_the_marketplace_model_is_a_signed_off_master():
    from_signoff = _assigned(CONTROLLER, "SIGNOFF_MASTERS")
    models = {ast.literal_eval(e.elts[0]) for e in from_signoff.elts}
    assert "fix.marketplace.tax.model" in models
    data = (TAX / "data" / "fix_tax_capture_data.xml").read_text(encoding="utf-8")
    assert 'model="fix.marketplace.tax.model"' not in data, "D-03: absent, never seeded"


def test_the_nid_threshold_is_m51_master_data():
    master = (TAX / "models" / "fix_tax_master.py").read_text(encoding="utf-8")
    assert '("nid_cash_threshold",' in master
    data = (TAX / "data" / "fix_tax_capture_data.xml").read_text(encoding="utf-8")
    assert '<field name="key">nid_cash_threshold</field>' in data
    ar = (BILLING / "models" / "fix_ar_engine.py").read_text(encoding="utf-8")
    body = ar.split("def _nid_threshold", 1)[1].split("\n    def ", 1)[0]
    assert 'self.env["fix.tax.parameter"]' in body
    assert "NID_CASH_THRESHOLD_DEFAULT" not in ar, "no hard-coded threshold (BRU-TAX-01)"


def test_new_models_are_secured():
    acl = (TAX / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    rules = (TAX / "security" / "fix_isolation_rules.xml").read_text(encoding="utf-8")
    for model in NEW_MODELS:
        xmlid = "model_" + model.replace(".", "_")
        rows = [r.split(",") for r in acl.splitlines() if (",%s," % xmlid) in r]
        assert rows, model
        assert all(r[-1].strip() == "0" for r in rows), "%s: nobody deletes" % model
        ro = [r for r in rows if r[3] == "account.group_account_readonly"]
        assert ro and ro[0][4:8] == ["1", "0", "0", "0"], model
        assert 'ref="%s"' % xmlid in rules, "%s has no company rule" % model
    mkt = [r.split(",") for r in acl.splitlines() if ",model_fix_marketplace_tax_model," in r]
    user = [r for r in mkt if r[3] == "account.group_account_user"]
    assert user[0][4:8] == ["1", "0", "0", "0"], "an accountant does not declare D-03"


def test_the_new_file_loads_after_the_models_it_extends():
    """It extends fix.vat.return (fix_tax_returns, fix_tax_returns_a08)."""
    init = (TAX / "models" / "__init__.py").read_text(encoding="utf-8")
    order = re.findall(r"^from \. import (\w+)", init, re.M)
    assert order.index("fix_tax_capture") > order.index("fix_tax_returns_a08"), order
