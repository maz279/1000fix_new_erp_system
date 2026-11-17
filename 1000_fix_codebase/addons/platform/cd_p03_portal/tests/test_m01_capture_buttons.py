# M01 Service Requests & Orders: every sub-module page that is about a record
# a person records offers a relevant capture (capture audit 2026-11-17).
#
# Before (HEAD c5feece6), evaluated with the engine's own fregCreate/fregPanels:
#   * page 3 (Entitlement Evaluation & SLA Clock): nothing. Entitlement is
#     evaluated against the warranty register, which M09 owns and has a form for;
#   * page 4 (Complaint & Fault Taxonomy Coding): nothing. The taxonomy is
#     defined in M37 (spec §3.3), whose Fault Code form was not reachable;
#   * page 5 (Diagnostic Templates & Benchmarks): nothing, and no form for a
#     diagnostic tree node existed anywhere (FR-SRM-021 P0);
#   * page 7 (Assignment & Field Dispatch Handoff): nothing; the hand-off was a
#     row action on the order book only (FR-SRM-031 P0);
#   * page 8 (SLA Policy, Clock & Escalations): only an SLA item. No form for a
#     policy existed anywhere (FR-SRM-047 P0), and "Escalation Rules" listed
#     the policies - no escalation rule record existed (FR-SRM-049 P0);
#   * page 11 (Service Reports & Repair Warranty): nothing; issuing the repair
#     warranty was a row button on one list (FR-SRM-045 P0).
# Pages 12 (boards and WIP analysis) and 13 (domain events) are read-only by
# design: an analysis and an event log are not typed in.
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
CONTROLLER = HERE.parent / "controllers" / "a02" / "m01.py"
WRITABLE_FILE = HERE.parent / "controllers" / "a02" / "writable.py"
DOMAIN = HERE.parents[2] / "domain"
SERVICE_ORDER = DOMAIN / "a_service_delivery" / "cd_service_order"
FIELD_SERVICE = DOMAIN / "a_service_delivery" / "cd_field_service"
WORKSHOP = DOMAIN / "a_service_delivery" / "cd_workshop"

_spec = importlib.util.spec_from_file_location(
    "_estate_pages", HERE / "test_estate_module_pages.py"
)
_estate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_estate)

PROBE = """
import * as M from './meta.mjs';
const { P03_MODULES, P03_MODULE_CREATE, P03_FORM_CHIPS, P03_FORM_MODELS, P03_DATA_SCREENS, P03_REPORT_ROUTES } = M;
function %(create)s
function %(panels)s
const mod = P03_MODULES.M01;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M01', map);
  const panels = fregPanels('M01', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M01:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      formModel: (P03_FORM_MODELS || {})['M01:' + f] || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M01.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: own || null, label: create ? (create.label || null) : null, forms };
});
const screen = (c) => ({
    kind: c.kind, model: c.model || null,
    create: c.create === undefined ? null : c.create,
    pick: c.pickRecord ? { domain: c.pickRecord.domain || [], cols: c.pickRecord.cols || [] } : null,
    save: c.saveAction ? c.saveAction.method : null,
    tabs: (c.tabs || []).length,
    lines: c.lines ? { field: c.lines.field, fields: (c.lines.fields || []).map((f) => f.name) } : null,
    actions: (c.actions || []).map((a) => ({ m: a.m, kwargs: (a.asks || []).map((q) => q.kwarg).concat(a.kwarg ? [a.kwarg] : []) })),
    cols: c.cols || [],
    empty: !!c.empty,
    fields: (c.sections || []).flatMap((s) => (s.fields || []).map((f) => ({
      name: f.name, readonly: !!f.readonly, required: !!f.required, tab: s.tab || null }))),
    tabIds: (c.tabs || []).map((t) => t.id) });
console.log(JSON.stringify({ subs, forms: mod.forms,
  labelled: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  byModel: P03_FORM_CHIPS['M01:__by_model__'] || {},
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS)
    .filter(([id]) => /^(M01|M09|M37|M02|M31)-/.test(id)).map(([id, c]) => [id, screen(c)])) }));
"""


@pytest.fixture(scope="module")
def m01(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m01_capture")
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


def _sub(m01, no):
    return next(s for s in m01["subs"] if s["no"] == no)


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
    """{model: ({fields}, {methods})} over the modules M01's forms bind."""
    out = {}
    paths = [
        *(SERVICE_ORDER / "models").glob("*.py"),
        *(FIELD_SERVICE / "models").glob("*.py"),
        *(WORKSHOP / "models").glob("*.py"),
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


# What each page offers: its own button, then the form chips it shows.
CAPTURES = {
    "1": ("M01-form-order", ["M01-form-order"]),
    "2": ("M01-form-order", ["M01-form-order"]),
    "3": ("M09-form-warranty", ["M09-form-warranty"]),
    "4": ("M37-form-fault", ["M37-form-fault"]),
    "5": ("M01-form-diag-node", ["M01-form-diag-node"]),
    "6": ("M01-form-estimate", ["M01-form-estimate"]),
    "7": ("M01-form-dispatch", ["M01-form-dispatch", "M31-form-receive", "M02-form-workorder"]),
    "8": ("M01-form-sla-policy", ["M01-form-sla-policy", "M01-form-sla-item", "M01-form-esc-rule"]),
    "9": ("M01-form-hold", ["M01-form-hold"]),
    "10": ("M01-form-qc", ["M01-form-qc"]),
    "11": ("M01-form-rwty", ["M01-form-rwty"]),
    "12": (None, []),
    "13": (None, []),
}

NEW_FORMS = (
    "M01-form-diag-node",
    "M01-form-sla-policy",
    "M01-form-esc-rule",
    "M01-form-dispatch",
    "M01-form-rwty",
)


def test_every_page_is_classified(m01):
    assert sorted(CAPTURES, key=int) == [s["no"] for s in m01["subs"]]


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_offers_its_capture(m01, no):
    sub = _sub(m01, no)
    own, chips = CAPTURES[no]
    assert sub["create"] == own, "page %s '%s' button" % (no, sub["title"])
    assert [f["id"] for f in sub["forms"]] == chips, "page %s chips" % no
    for form in sub["forms"]:
        assert form["opens"], "page %s chip %s opens nothing" % (no, form["f"])
        # FORM_MODELS names the model the chip's form edits
        assert form["formModel"] == form["model"], form


def test_only_the_analysis_and_event_pages_capture_nothing(m01):
    bare = [s["no"] for s in m01["subs"] if not s["create"]]
    assert bare == ["12", "13"]


def test_an_owner_module_record_opens_the_owner_s_form(m01):
    """M01 applies the warranty (M09), the fault taxonomy (M37), the workshop
    book-in (M31) and the technician slot (M02): it opens their forms and
    masters no copy of them."""
    owned = {
        "M09-form-warranty": "M09",
        "M37-form-fault": "M37",
        "M31-form-receive": "M31",
        "M02-form-workorder": "M02",
    }
    for sub in m01["subs"]:
        for form in sub["forms"]:
            if form["id"] in owned:
                assert not any(
                    sid.startswith("M01-form")
                    and m01["screens"][sid]["model"] == form["model"]
                    and m01["screens"][sid]["save"] is None
                    and form["model"] != "fix.service.order"
                    for sid in m01["screens"]
                ), "M01 has its own form for %s" % form["model"]


def test_every_m01_list_on_a_capturing_page_opens_its_form(m01):
    for no in ("4", "5", "8"):
        for sid in _sub(m01, no)["screens"]:
            cfg = m01["screens"][sid]
            if cfg["kind"] != "model_list":
                continue
            if cfg["model"] in ("fix.escalation.event",):
                assert cfg["create"] is False and cfg["empty"], sid
                continue
            assert cfg["create"], "%s refuses + New" % sid
            assert m01["byModel"].get(cfg["model"]) or cfg["create"].get("screen"), sid


def test_escalation_rules_list_rules_not_policies(m01):
    esc = m01["screens"]["M01-esc"]
    assert esc["model"] == "fix.escalation.rule"
    assert {"policy_id", "threshold_pct", "group_id"} <= set(esc["cols"])
    raised = m01["screens"]["M01-esc-raised"]
    assert [a["m"] for a in raised["actions"]] == ["action_acknowledge"]
    assert raised["actions"][0]["kwargs"] == ["note"]
    assert "M01-esc-raised" in m01["labelled"]


def test_the_hand_off_and_the_warranty_pick_an_existing_order(m01):
    """Both act on an order that exists: the form asks which, then runs the
    order's own action - the server keeps its checks (zone, second live field
    order, delivered-only, issued once)."""
    disp = m01["screens"]["M01-form-dispatch"]
    assert disp["save"] == "action_create_field_order"
    assert ["service_type", "=", "onsite"] in disp["pick"]["domain"]
    assert ["field_order_ids", "=", False] in disp["pick"]["domain"]
    rwty = m01["screens"]["M01-form-rwty"]
    assert rwty["save"] == "action_issue_repair_warranty"
    assert ["service_warranty_until", "=", False] in rwty["pick"]["domain"]
    for cfg in (disp, rwty):
        # nothing is typed: the action derives everything from the order
        assert all(f["readonly"] for f in cfg["fields"]), cfg


def test_save_actions_and_list_actions_are_served_and_exist(m01):
    served = _surfaces()
    classes = _model_classes()
    for sid in (*NEW_FORMS, "M01-esc-raised"):
        cfg = m01["screens"][sid]
        methods = ([cfg["save"]] if cfg["save"] else []) + [a["m"] for a in cfg["actions"]]
        for method in methods:
            assert method in served[cfg["model"]], "%s.%s not served" % (cfg["model"], method)
            assert method in classes[cfg["model"]][1], "%s.%s missing" % (cfg["model"], method)


def test_every_new_form_field_exists_on_its_model(m01):
    classes = _model_classes()
    builtin = {"display_name", "id", "create_date", "write_date"}
    for sid in (*NEW_FORMS, "M01-esc", "M01-esc-raised", "M01-sla", "M01-templates"):
        cfg = m01["screens"][sid]
        known = classes[cfg["model"]][0] | builtin
        names = [f["name"] for f in cfg["fields"]] + cfg["cols"]
        if cfg["pick"]:
            names += cfg["pick"]["cols"] + [c[0] for c in cfg["pick"]["domain"]]
        missing = sorted(set(names) - known)
        assert not missing, "%s: %s" % (sid, missing)
        if cfg["lines"]:
            comodel = {"children_ids": "fix.diagnostic.node", "item_ids": "fix.sla.item"}[
                cfg["lines"]["field"]
            ]
            assert set(cfg["lines"]["fields"]) <= classes[comodel][0], sid


def test_every_form_section_sits_on_a_declared_tab(m01):
    for sid in NEW_FORMS:
        cfg = m01["screens"][sid]
        tabs = set(cfg["tabIds"])
        for field in cfg["fields"]:
            assert (field["tab"] is None and not tabs) or field["tab"] in tabs, (sid, field)


@pytest.mark.parametrize("model", ["fix.escalation.rule", "fix.escalation.event"])
def test_new_registers_are_served_and_whitelisted(model):
    assert model in _surfaces()
    assert model in _writable()


def test_an_escalation_is_never_typed():
    assert _writable()["fix.escalation.event"] == set()


def test_new_models_are_secured():
    acl = (SERVICE_ORDER / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    rows = [r.split(",") for r in acl.splitlines()[1:] if r.strip()]
    by_model = {}
    for r in rows:
        by_model.setdefault(r[2], []).append(r)
    rule = by_model["model_fix_escalation_rule"]
    # read for everyone, the rule book kept by Service Supervisors
    assert any(r[3] == "base.group_user" and r[4:8] == ["1", "0", "0", "0"] for r in rule)
    assert any(
        r[3] == "cd_service_order.group_so_supervisor" and r[4:8] == ["1", "1", "1", "1"]
        for r in rule
    )
    event = by_model["model_fix_escalation_event"]
    # nobody creates or deletes one: the cron raises it as superuser
    assert all(r[6] == "0" and r[7] == "0" for r in event)


def test_the_capture_file_loads_after_the_models_it_extends():
    init = (SERVICE_ORDER / "models" / "__init__.py").read_text(encoding="utf-8")
    pos = init.index("from . import fix_sla_escalation")
    for dep in ("fix_sla_policy", "fix_sla_instance", "fix_service_order_handback"):
        assert init.index(dep) < pos, dep
