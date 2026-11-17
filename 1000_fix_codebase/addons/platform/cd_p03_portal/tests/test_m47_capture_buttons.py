# M47 Facility & Branch Infrastructure: every sub-module page captures each
# record it covers (capture audit 2026-11-17).
#
# Before (HEAD ea2fdda1), evaluated with the engine's own fregCreate/fregPanels:
#   * pages 4 Utilities, 5 Infrastructure Assets, 6 Building PM and 9 Open /
#     Close Projects offered no chip at all;
#   * page 1 listed Occupancy & Condition and page 8 listed Security &
#     Incidents with no capture for either (their forms existed, unreachable);
#   * eight working lists sat on no page: operating-risk exceptions, rent
#     schedule, IFRS 16 extracts, lease remeasurement items, AP cost entries,
#     asset finance requests and hand-off problems;
#   * no P0 record existed for a licence renewal (FR-FAC-021), a lease's dated
#     obligations - rent review, break option, deposit return, landlord
#     obligation (FR-FAC-009/010), a utility account with its meter
#     (FR-FAC-038), an infrastructure outage (FR-FAC-027), the generator / UPS
#     test regime (FR-FAC-026, BRU-FAC-10) or the compliance set a site type
#     requires (FR-FAC-002/017, BRU-FAC-01);
#   * a licence held no issuing authority, fee or responsible person
#     (FR-FAC-016), an infrastructure asset no make, model, capacity or
#     expected life (FR-FAC-024), and a facility request no photograph
#     (FR-FAC-031/034).
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
CONTROLLER = HERE.parent / "controllers" / "a07" / "m47.py"
WRITABLE_FILE = HERE.parent / "controllers" / "a07" / "writable.py"
FACILITY = HERE.parents[2] / "domain" / "f_asset_facilities" / "cd_facility"
SPINE = HERE.parents[2] / "domain" / "f_asset_facilities" / "cd_asset_workorder_spine"

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
const mod = P03_MODULES.M47;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M47', map);
  const panels = fregPanels('M47', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M47:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M47.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: own || null, forms,
    reports: panels.reports.map((r) => ({ r, route: P03_REPORT_ROUTES['M47:' + r] || null })) };
});
console.log(JSON.stringify({ subs, forms: mod.forms, reports: mod.reports,
  labelled: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => id.startsWith('M47-')).map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create, report: c.report || null,
    tabs: (c.tabs || []).length,
    actions: (c.actions || []).map((a) => ({ m: a.m, kwargs: (a.asks || []).map((q) => q.kwarg).concat(a.kwarg ? [a.kwarg] : []) })),
    cols: c.cols || [],
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({
      name: f.name, readonly: !!f.readonly, required: !!f.required })) }])) }));
"""


@pytest.fixture(scope="module")
def m47(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m47_capture")
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


def _reports():
    value = _assigned(CONTROLLER, "REPORTS")
    return {ast.literal_eval(k) for k in value.keys}


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
    """{model: {method names}} defined in cd_facility's model files."""
    out = {}
    for path in (FACILITY / "models").glob("*.py"):
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
    "1": ["M47-form-site", "M47-form-condition", "M47-form-site-profile"],
    "2": ["M47-form-lease", "M47-form-lease-event"],
    "3": ["M47-form-licence", "M47-form-licence-renewal"],
    "4": ["M47-form-utility", "M47-form-utility-account"],
    "5": ["M47-form-asset", "M47-form-outage"],
    "6": ["M47-form-pm", "M47-form-power-test"],
    "7": ["M47-form-wo"],
    "8": ["M47-form-safety", "M47-form-incident"],
    "9": ["M47-form-project"],
}

# Page 10 is the work-order spine's queue: each demand is raised by its source
# module (an M45 calibration or PM, an M46 service, an M48 intervention, an M17
# device plan) and routed from here; a person fills the missing fact on the
# row's form and presses Route. A facility request a person raises is a work
# order (page 7, FR-FAC-031).
SYSTEM_QUEUES = {"10": "fix.maintenance.demand"}

RECORDS = {
    "1": "fix.site",
    "2": "fix.site.lease",
    "3": "fix.site.licence",
    "4": "fix.site.utility",
    "5": "fix.site.asset",
    "6": "fix.site.pm",
    "7": "fix.facility.work.order",
    "8": "fix.site.safety",
    "9": "fix.site.project",
    "10": "fix.maintenance.demand",
}

NEW_MODELS = (
    "fix.site.type.profile",
    "fix.site.lease.event",
    "fix.site.licence.renewal",
    "fix.site.utility.account",
    "fix.site.outage",
    "fix.site.power.test",
)

# What a form must never let a person type: the state, every decision stamp
# and every derived figure.
NEVER_TYPED = {
    "fix.site.lease.event": {
        "state",
        "site_id",
        "decision",
        "decided_by_id",
        "decided_on",
        "outcome_notes",
        "alert_horizon",
    },
    "fix.site.licence.renewal": {
        "state",
        "site_id",
        "licence_type",
        "submitted_on",
        "submitted_by_id",
        "completed_by_id",
        "completed_on",
        "total_cost",
        "cancel_reason",
    },
    "fix.site.utility.account": {"state", "closed_on", "closed_by_id"},
    "fix.site.outage": {
        "state",
        "ended_at",
        "ended_by_id",
        "operating_hours_lost",
        "recorded_by_id",
    },
    "fix.site.power.test": {"site_id", "tested_by_id", "work_order_id", "asset_type"},
    "fix.site.utility": {"flagged", "review_state", "anomaly_basis", "paid_on", "paid_amount"},
}

# a system-raised list: what the scheduled checks found (create: false)
NOT_A_PAGE = {"M47-alerts"}


def _sub(m47, no):
    return next(s for s in m47["subs"] if s["no"] == no)


def test_every_page_is_classified(m47):
    assert sorted(s["no"] for s in m47["subs"]) == sorted([*CAPTURES, *SYSTEM_QUEUES])


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m47, no):
    sub = _sub(m47, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]}
    missing = [form for form in [own, *others] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)


@pytest.mark.parametrize("no", sorted(SYSTEM_QUEUES))
def test_a_system_queue_offers_no_new_and_opens_its_rows(m47, no):
    sub = _sub(m47, no)
    assert sub["create"] is None
    form = next(
        c
        for c in m47["screens"].values()
        if c["kind"] == "model_form" and c["model"] == SYSTEM_QUEUES[no]
    )
    assert form.get("create") is False, "a demand is raised by its source module"
    assert any(not f["readonly"] for f in form["fields"]), "the missing fact is typed on the row"


@pytest.mark.parametrize("no", sorted(RECORDS, key=int))
def test_each_page_lists_its_own_record(m47, no):
    assert _sub(m47, no)["model"] == RECORDS[no]


def test_each_captured_record_is_listed_on_its_page(m47):
    for sub in m47["subs"]:
        listed = {m47["screens"][s]["model"] for s in sub["screens"] if s in m47["screens"]}
        for f in sub["forms"]:
            assert f["model"] in listed, "page %s captures %s but lists none" % (
                sub["no"],
                f["model"],
            )


def test_every_working_screen_sits_on_a_page(m47):
    placed = {sid for s in m47["subs"] for sid in s["screens"]}
    placed |= {r["route"] for s in m47["subs"] for r in s["reports"]}
    orphans = [
        sid
        for sid, cfg in m47["screens"].items()
        if cfg["kind"] in ("model_list", "table_report")
        and sid not in placed
        and sid not in NOT_A_PAGE
        and not sid.startswith("M47-rpt-")
    ]
    assert not orphans, orphans


def test_every_screen_on_a_page_has_a_navigation_label(m47):
    labelled = set(m47["labelled"])
    unlabelled = sorted(
        sid
        for sub in m47["subs"]
        for sid in sub["screens"]
        if sid in m47["screens"]
        and m47["screens"][sid]["kind"] == "model_list"
        and sid not in labelled
    )
    assert not unlabelled, unlabelled


def test_every_chip_name_is_a_module_form(m47):
    named = set(m47["forms"])
    for sub in m47["subs"]:
        for f in sub["forms"]:
            assert f["f"] in named, "page %s chip %r is not in the module's forms" % (
                sub["no"],
                f["f"],
            )
            assert f["id"], "page %s chip %r opens no screen" % (sub["no"], f["f"])


def test_every_page_report_has_a_route_and_a_pack(m47):
    packs = _reports()
    for sub in m47["subs"]:
        for r in sub["reports"]:
            assert r["route"], "page %s report %r has no route" % (sub["no"], r["r"])
            assert m47["screens"][r["route"]]["report"] in packs, r


def test_every_served_action_exists_on_its_model():
    methods = _model_methods()
    for model in NEW_MODELS:
        acts = _surfaces().get(model, set())
        missing = acts - methods.get(model, set())
        assert not missing, "%s serves %s, which the model lacks" % (model, sorted(missing))


def test_every_list_action_is_served(m47):
    surfaces = _surfaces()
    for sid, cfg in m47["screens"].items():
        if cfg["kind"] != "model_list" or not cfg["actions"] or cfg["model"] not in surfaces:
            continue
        served = surfaces[cfg["model"]]
        for act in cfg["actions"]:
            assert act["m"] in served, "%s offers %s, not served" % (sid, act["m"])


@pytest.mark.parametrize("model", NEW_MODELS)
def test_new_registers_are_served_and_whitelisted(m47, model):
    assert model in _surfaces()
    forms = [
        c for c in m47["screens"].values() if c["kind"] == "model_form" and c["model"] == model
    ]
    assert forms, "%s has no workspace form" % model
    typed = {f["name"] for c in forms for f in c["fields"] if not f["readonly"]}
    assert _writable()[model] == typed


@pytest.mark.parametrize("model", sorted(NEVER_TYPED))
def test_stamps_and_derived_figures_are_never_typed(model):
    leaked = _writable().get(model, set()) & NEVER_TYPED[model]
    assert not leaked, (model, sorted(leaked))


def test_long_forms_are_tabbed(m47):
    """AGENTS.md: a form of more than 15 fields is split into tabs."""
    long_flat = [
        sid
        for sid, c in m47["screens"].items()
        if c["kind"] == "model_form" and len(c["fields"]) > 15 and not c["tabs"]
    ]
    assert not long_flat, long_flat


@pytest.mark.parametrize(
    "screen,model,want",
    [
        # FR-FAC-016: authority, cost and responsible role per licence
        ("M47-form-licence", "fix.site.licence", {"authority", "fee", "responsible_id"}),
        # FR-FAC-024: make, model, capacity and expected life
        (
            "M47-form-asset",
            "fix.site.asset",
            {"make", "model_name", "capacity", "expected_life_months"},
        ),
        # FR-FAC-031/034: the request's photograph and the completion evidence
        (
            "M47-form-wo",
            "fix.facility.work.order",
            {"request_photo", "completion_evidence_file"},
        ),
        # FR-FAC-038: a bill belongs to its utility account
        ("M47-form-utility", "fix.site.utility", {"account_id"}),
    ],
)
def test_existing_forms_capture_the_spec_attributes(m47, screen, model, want):
    names = {f["name"] for f in m47["screens"][screen]["fields"] if not f["readonly"]}
    assert want <= names, sorted(want - names)
    assert want <= _writable()[model]


def test_new_models_are_secured():
    acl = (FACILITY / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    rules = (FACILITY / "security" / "fix_facility_scope_rules.xml").read_text(encoding="utf-8")
    # an outage or a generator test is recorded by the branch (spec §13 R06/R08)
    branch_records = {"fix.site.outage", "fix.site.power.test"}
    for model in NEW_MODELS:
        xmlid = "model_" + model.replace(".", "_")
        rows = [r.split(",") for r in acl.splitlines() if (",%s," % xmlid) in r]
        assert rows, model
        assert all(r[-1].strip() == "0" for r in rows), "%s: nobody deletes" % model
        plain = [r for r in rows if r[3] == "base.group_user"]
        want = ["1", "1", "1", "0"] if model in branch_records else ["1", "0", "0", "0"]
        assert plain and plain[0][4:8] == want, model
        if model != "fix.site.type.profile":  # a profile is estate-wide
            assert 'ref="%s"' % xmlid in rules, "%s has no company rule" % model


def test_the_new_file_loads_after_the_models_it_extends():
    init = (FACILITY / "models" / "__init__.py").read_text(encoding="utf-8")
    assert init.index("fix_facility_ops") < init.index("fix_facility_capture")
    assert init.index("fix_facility_compliance") < init.index("fix_facility_capture")


def test_a_missed_generator_test_reaches_a_person():
    """BRU-FAC-10: a missed test escalates, so its event is routed to an alert."""
    alert = (SPINE / "models" / "fix_asset_alert.py").read_text(encoding="utf-8")
    consumers = (SPINE / "data" / "fix_asset_alert_consumers.xml").read_text(encoding="utf-8")
    assert '"site.power_test_overdue"' in alert
    assert ">site.power_test_overdue<" in consumers
