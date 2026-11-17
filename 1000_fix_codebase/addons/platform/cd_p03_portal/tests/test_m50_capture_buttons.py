# M50 Treasury & Banking: every sub-module page captures each record it
# covers (capture audit 2026-11-17).
#
# Before (HEAD 297241f9), evaluated with the engine's own fregCreate/fregPanels:
#   * page 2 (Statement & Recon): "+ New" opened a bank statement LINE, which
#     the model refuses to create (lines come only from an imported file);
#   * pages 3 (Cash Position) and 8 (FX) had no "+ New" at all, and page 8
#     had no capture of any kind;
#   * pages 4, 7 and 9 listed cheques, covenants, imprest funds and vouchers
#     with no chip, although their forms existed;
#   * the COD report and the cheque register sat on no page;
#   * no bank mandate (FR-TRE-002 P0, BRU-TRE-20 H): signatories were a
#     free-text note anyone could overwrite, with no approval or history;
#   * no matching rule (FR-TRE-008 P0, FR-TRE-010 P0): bank charges, interest
#     and tax on interest could only be booked one line at a time;
#   * the Settlement Exceptions list could not be acted on: no owner, no
#     provider case, no resolution (FR-TRE-027 P0, BRU-TRE-10 H);
#   * the 13-week forecast was never kept, so accuracy could not be measured
#     (FR-TRE-038, BRU-TRE-26 H);
#   * no FX conversion record (FR-TRE-042).
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
CONTROLLER = HERE.parent / "controllers" / "a08" / "m50.py"
WRITABLE_FILE = HERE.parent / "controllers" / "a08" / "writable.py"
TREASURY = HERE.parents[2] / "domain" / "g_finance" / "cd_cash_position"

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
const mod = P03_MODULES.M50;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M50', map);
  const panels = fregPanels('M50', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M50:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M50.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: own || null, forms,
    reports: panels.reports.map((r) => ({ r, route: P03_REPORT_ROUTES['M50:' + r] || null })) };
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
  foreign: Object.fromEntries(Object.values(P03_FORM_CHIPS).filter((id) => typeof id === 'string' && !id.startsWith('M50-') && P03_DATA_SCREENS[id]).map((id) => [id, screen(P03_DATA_SCREENS[id])])),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => id.startsWith('M50-')).map(([id, c]) => [id, screen(c)])) }));
"""


@pytest.fixture(scope="module")
def m50(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m50_capture")
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
    """{model: ({fields}, {methods})} defined or extended in cd_cash_position."""
    out = {}
    for path in (TREASURY / "models").glob("*.py"):
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
    "1": ["M50-form-journal", "M50-form-mandate"],
    "2": ["M50-form-import", "M50-form-recon", "M50-form-rule"],
    "3": ["M50-form-deposit"],
    "4": ["M50-form-instruction", "M50-form-cheque", "M50-form-chequebook"],
    "5": ["M50-form-gateway", "M50-form-sxcase", "M50-form-cod", "M50-form-courier"],
    "6": ["M50-form-forecast", "M50-form-fcversion"],
    "7": ["M50-form-facility", "M50-form-amendment", "M50-form-covenant"],
    "8": ["M50-form-fxconv", "M19-form-fx"],
    "9": ["M50-form-count", "M50-form-fund", "M50-form-voucher", "M50-form-topup"],
}

NEW_MODELS = (
    "fix.bank.mandate",
    "fix.bank.matching.rule",
    "fix.settlement.exception",
    "fix.cash.forecast.version",
    "fix.fx.conversion",
)

# What a form must never let a person type: the state, every decision stamp
# and every derived figure.
NEVER_TYPED = {
    "fix.bank.mandate": {
        "state",
        "requested_by_id",
        "requested_at",
        "approved_by_id",
        "approved_at",
        "ended_by_id",
        "ended_at",
        "end_reason",
        "company_id",
        "currency_id",
    },
    "fix.bank.matching.rule": {
        "state",
        "version",
        "previous_id",
        "requested_by_id",
        "approved_by_id",
        "approved_at",
        "last_test",
        "line_count",
    },
    "fix.settlement.exception": {
        "name",
        "state",
        "exception_type",
        "amount",
        "opened_on",
        "resolution",
        "resolution_note",
        "proposed_by_id",
        "resolved_by_id",
        "resolved_on",
    },
    "fix.cash.forecast.version": {
        "name",
        "generated_at",
        "generated_by_id",
        "week_start",
        "opening_balance",
        "measured_weeks",
        "mean_accuracy_pct",
    },
    "fix.cash.forecast.version.line": {"actual_net", "variance", "accuracy_pct", "measured"},
    "fix.fx.conversion": {
        "name",
        "state",
        "book_rate",
        "realised_difference",
        "rate_achieved",
        "prepared_by_id",
        "approved_by_id",
        "move_id",
    },
    "fix.bank.statement.line": {"external_class", "matching_rule_id", "external_move_id"},
    "account.journal": {"fix_signatories", "fix_active_signatories"},
}


def _sub(m50, no):
    return next(s for s in m50["subs"] if s["no"] == no)


def _screen(m50, sid):
    return m50["screens"].get(sid) or m50["foreign"][sid]


def test_every_page_is_classified(m50):
    assert sorted(s["no"] for s in m50["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m50, no):
    sub = _sub(m50, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]} | {sub["create"]}
    missing = [form for form in [own, *others] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)


def test_no_page_offers_a_record_the_model_refuses_to_create(m50):
    """Statement lines and settlement lines come only from imported files."""
    for sub in m50["subs"]:
        assert sub["create"] != "M50-form-stmtline", sub["no"]
    assert m50["screens"]["M50-form-stmtline"]["create"] is False
    assert m50["screens"]["M50-recon"]["create"] is False


def test_each_captured_record_is_listed_on_its_page(m50):
    for sub in m50["subs"]:
        listed = {m50["screens"][s]["model"] for s in sub["screens"] if s in m50["screens"]}
        listed.add(sub["model"])
        captures = list(sub["forms"])
        if sub["create"]:
            captures.append({"model": _screen(m50, sub["create"])["model"]})
        for f in captures:
            if f["model"] == "fix.fx.revaluation":
                continue  # M19's revaluation, summarised by the FX Holdings report
            assert f["model"] in listed, "page %s captures %s but lists none" % (
                sub["no"],
                f["model"],
            )


def test_every_creatable_list_on_a_page_has_its_capture(m50):
    for sub in m50["subs"]:
        captured = {f["model"] for f in sub["forms"] if f["opens"]}
        if sub["create"]:
            captured.add(_screen(m50, sub["create"])["model"])
        for sid in sub["screens"]:
            cfg = m50["screens"].get(sid, {})
            if cfg.get("kind") == "model_list" and cfg.get("create") is not False:
                assert cfg["model"] in captured, "page %s lists %s (%s) with no capture" % (
                    sub["no"],
                    cfg["model"],
                    sid,
                )


def test_every_working_screen_sits_on_a_page(m50):
    placed = {sid for s in m50["subs"] for sid in s["screens"]}
    placed |= {r["route"] for s in m50["subs"] for r in s["reports"]}
    orphans = [
        sid
        for sid, cfg in m50["screens"].items()
        if cfg["kind"] in ("model_list", "table_report") and sid not in placed
    ]
    assert not orphans, orphans


def test_every_screen_on_a_page_has_a_navigation_label(m50):
    labelled = set(m50["labelled"])
    unlabelled = sorted(
        sid
        for sub in m50["subs"]
        for sid in sub["screens"]
        if sid in m50["screens"]
        and m50["screens"][sid]["kind"] == "model_list"
        and sid not in labelled
    )
    assert not unlabelled, unlabelled


def test_every_served_action_exists_on_its_model():
    classes = _model_classes()
    for model, acts in _surfaces().items():
        methods = classes.get(model, (set(), set()))[1]
        missing = acts - methods
        # the DOFA mixin (cd_workflow_engine) supplies the payment recall
        missing -= {"action_recall_approval"}
        assert not missing, "%s serves %s, which the model lacks" % (model, sorted(missing))


def test_every_list_action_is_served(m50):
    surfaces = _surfaces()
    for sid, cfg in m50["screens"].items():
        if cfg["kind"] != "model_list" or not cfg["actions"]:
            continue
        served = surfaces[cfg["model"]]
        for act in cfg["actions"]:
            assert act["m"] in served, "%s offers %s, not served" % (sid, act["m"])


def test_every_form_field_exists_on_its_treasury_model(m50):
    classes = _model_classes()
    for sid, cfg in m50["screens"].items():
        # the new records and the statement line this audit extended (other
        # forms also show fields of Odoo's models and of the DOFA mixin)
        if cfg["kind"] != "model_form" or cfg["model"] not in (
            *NEW_MODELS,
            "fix.bank.statement.line",
        ):
            continue
        known = classes[cfg["model"]][0] | {"name", "state", "active"}
        unknown = [f["name"] for f in cfg["fields"] if f["name"] not in known]
        assert not unknown, "%s shows %s, not fields of %s" % (sid, unknown, cfg["model"])


@pytest.mark.parametrize("model", NEW_MODELS)
def test_new_registers_are_served_and_whitelisted(m50, model):
    assert model in _surfaces()
    forms = [
        c for c in m50["screens"].values() if c["kind"] == "model_form" and c["model"] == model
    ]
    assert forms, "%s has no workspace form" % model
    typed = {f["name"] for c in forms for f in c["fields"] if not f["readonly"]}
    assert _writable()[model] == typed


@pytest.mark.parametrize("model", sorted(NEVER_TYPED))
def test_stamps_and_derived_figures_are_never_typed(model):
    leaked = _writable().get(model, set()) & NEVER_TYPED[model]
    assert not leaked, (model, sorted(leaked))


def test_long_forms_are_tabbed(m50):
    """AGENTS.md: a form of more than 15 fields is split into tabs."""
    long_flat = [
        sid
        for sid, c in m50["screens"].items()
        if c["kind"] == "model_form" and len(c["fields"]) > 15 and not c["tabs"]
    ]
    assert not long_flat, long_flat


def test_auto_match_offers_the_rules_and_exceptions_open_cases(m50):
    recon = {a["m"] for a in m50["screens"]["M50-recon"]["actions"]}
    assert "action_apply_rules" in recon
    lines = {a["m"] for a in m50["screens"]["M50-gateway-lines"]["actions"]}
    assert "action_open_case" in lines


def test_a_resolution_is_proposed_with_its_evidence(m50):
    acts = {a["m"]: a for a in m50["screens"]["M50-settlement-cases"]["actions"]}
    assert set(acts["action_propose"]["kwargs"]) == {"resolution", "note"}
    for model_action in ("action_reject", "action_revoke"):
        mandate = {a["m"]: a for a in m50["screens"]["M50-mandates"]["actions"]}
        assert mandate[model_action]["kwargs"] == ["reason"]


def test_new_models_are_secured():
    acl = (TREASURY / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    rules = (TREASURY / "security" / "fix_isolation_rules.xml").read_text(encoding="utf-8")
    for model in (*NEW_MODELS, "fix.cash.forecast.version.line"):
        xmlid = "model_" + model.replace(".", "_")
        rows = [r.split(",") for r in acl.splitlines() if (",%s," % xmlid) in r]
        assert rows, model
        assert all(r[-1].strip() == "0" for r in rows), "%s: nobody deletes" % model
        ro = [r for r in rows if r[3] == "account.group_account_readonly"]
        assert ro and ro[0][4:8] == ["1", "0", "0", "0"], model
        assert 'ref="%s"' % xmlid in rules, "%s has no company rule" % model
    weeks = [
        r.split(",") for r in acl.splitlines() if ",model_fix_cash_forecast_version_line," in r
    ]
    assert all(
        r[5:8] == ["0", "0", "0"] for r in weeks
    ), "forecast weeks are written by the model only"


def test_the_new_file_loads_after_the_models_it_extends():
    """It extends the statement line (fix_cash_position) and the settlement
    line (gateway_settlement): an _inherit before its _name fails to load."""
    init = (TREASURY / "models" / "__init__.py").read_text(encoding="utf-8")
    names = re.findall(r"^    (\w+),$", init, re.M)
    assert names[-1] == "fix_treasury_capture", names
    assert "ruff: noqa: I001" in init
