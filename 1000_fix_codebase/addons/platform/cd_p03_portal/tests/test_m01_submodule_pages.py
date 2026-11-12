# M01 - every one of the 13 Function Register sub-module pages describes and
# captures ITS OWN work.
#
# After the estimate page (test_submodule_create_button.py) the other twelve
# were walked in the live workspace on 2026-11-12. They shared its defects and
# added four of their own:
#
#   - twelve pages had empty "Reports Measuring It" / "Forms Capturing It"
#     panels although the module ships 7 reports and 6 forms;
#   - four pages that only work on EXISTING orders (dispatch hand-off, holds,
#     delivered jobs, the WIP board) offered "+ New Service Order";
#   - clicking a record on a page whose model has no form (fault codes,
#     diagnostic nodes, SLA policies) opened a record pane headed
#     "#undefined" with every value "-": the pane renders a row and was
#     given none;
#   - three forms opened BLANK for a record nobody types in from scratch -
#     the Hold / Release form (no customer, no device: Save could only
#     fail), the SLA KPI Instance form (every field read-only) and "Service
#     Order Record" (a twin of the New Service Order form);
#   - a boolean column printed the literal "true".
#
# The rules are JavaScript, so they are EXECUTED: node runs the engine's own
# method source over the real registry (same harness as
# test_a08_m19_registry.py). The record read is proved through the endpoint.
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from unittest import mock

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api

SRC = Path(__file__).resolve().parents[1] / "static" / "src"
IMPORT = re.compile(r'from\s+"(\./a\d\d/\w+)"')
FREG_CREATE = re.compile(r"^    (fregCreate\(mid, map\) \{\n.*?\n    \})\n", re.S | re.M)
FREG_RECORD = re.compile(r"^    async (openFregRecord\(row\) \{\n.*?\n    \})\n", re.S | re.M)
FREG_PANELS = re.compile(r"^    (fregPanels\(mid, mod, map\) \{\n.*?\n    \})\n", re.S | re.M)
FREG_REPORT = re.compile(
    r"^    async (loadFregReport\(mid, report\) \{\n.*?\n    \})\n", re.S | re.M
)

PROBE = """
import * as M from './meta.mjs';
const { P03_MODULES, P03_MODULE_CREATE, P03_FORM_CHIPS, P03_DATA_SCREENS, P03_REPORT_ROUTES } = M;
function %(create)s
async function %(record)s
function %(panels)s
async function %(report)s

// loadFregReport against a stand-in: what the page's grid becomes
const feed = async (answer) => {
  const fr = { loading: true, reportTitle: '', gridData: { cols: [], rows: [] } };
  const asked = [];
  const self = { state: { activeFreg: fr }, t: (x) => x, render() {},
    async rpc(route, params) { asked.push([route, params.module, params.report]); return answer; } };
  await loadFregReport.call(self, 'M01', 'domain_events');
  return { asked, loading: fr.loading, title: fr.reportTitle, grid: fr.gridData };
};
const fed = {
  rows: await feed({ title: 'Domain Events Published (Outbox)', cols: ['event_type', 'total', 'last'],
    labels: { event_type: 'Event', total: 'Events', last: 'Latest Event' },
    rows: [{ event_type: 'service_order.intake', total: 3, last: null }] }),
  refused: await feed({ error: 'Report not available on this surface' }),
};

const mod = P03_MODULES.M01;
const subs = mod.freg.sub.map((s) => ({ no: s[0], title: s[1], map: s[3], create: fregCreate('M01', s[3]),
  panels: fregPanels('M01', mod, s[3]) }));

// the two panels of every sub-module page of every module, as the page builds them
const panels = [];
for (const [mid, m] of Object.entries(P03_MODULES)) {
  for (const s of (m.freg && m.freg.sub) || []) {
    const map = s[3] || null;
    const p = fregPanels(mid, m, map);
    const ids = (map && map.screens) || [];
    const models = [map && map.model, ...ids.map((id) => (P03_DATA_SCREENS[id] || {}).model)].filter(Boolean);
    panels.push({ mid, no: s[0], title: s[1], models, screens: ids,
      explicitReports: !!(map && map.reports), explicitForms: !!(map && map.forms),
      reports: p.reports.map((name) => ({ name, screen: P03_REPORT_ROUTES[mid + ':' + name] || null })),
      forms: p.forms.map((name) => {
        const screen = P03_FORM_CHIPS[mid + ':' + name] || null;
        const cfg = P03_DATA_SCREENS[screen] || {};
        return { name, screen, kind: cfg.kind || null, model: cfg.model || null };
      }) });
  }
}

const screens = {};
for (const [id, c] of Object.entries(P03_DATA_SCREENS)) {
  const fields = (c.sections || []).flatMap((s) => s.fields || []);
  screens[id] = { kind: c.kind, model: c.model || null, back: c.back || null, pick: c.pick || null,
    create: c.create === undefined ? null : c.create,
    newLabel: c.newLabel || null, pickRecord: c.pickRecord || null,
    saveAction: c.saveAction || null, empty: c.empty || null,
    fields: fields.map((f) => ({ name: f.name, readonly: !!f.readonly, required: !!f.required })),
    editable: c.kind === 'model_form'
      ? fields.filter((f) => !f.readonly).length + (c.lines && !c.lines.readonlyGrid ? 1 : 0) : null };
}

// the form "+ New" opens on every list that offers it
const news = [];
for (const [id, c] of Object.entries(P03_DATA_SCREENS)) {
  if (c.kind !== 'model_list' || c.create === false) continue;
  const mid = id.split('-')[0];
  const byScreen = P03_FORM_CHIPS[mid + ':__by_screen__'] || {};
  const byModel = P03_FORM_CHIPS[mid + ':__by_model__'] || {};
  const form = byScreen[id] || byModel[c.model] || null;
  if (form) news.push({ list: id, form });
}
const creates = Object.entries(P03_MODULE_CREATE).map(([mid, c]) => ({ mid, screen: c.screen || null }));
// an order list's own data-entry button (so_list `create`) and the row actions
// that open a form instead of typed prompts
const soCreates = Object.entries(P03_DATA_SCREENS)
  .filter(([, c]) => c.kind === 'so_list' && c.create)
  .map(([id, c]) => ({ list: id, screen: c.create.screen, label: c.create.label }));
const soForms = Object.entries(P03_DATA_SCREENS)
  .filter(([, c]) => c.kind === 'so_list')
  .flatMap(([id, c]) => (c.actions || []).filter((a) => a.form).map((a) => ({ list: id, action: a.id, m: a.m, form: a.form, states: a.states })));

// openFregRecord against a recording stand-in for the component
const run = async (index, recId, rpcRows) => {
  const map = mod.freg.sub[index][3];
  const calls = [];
  const self = {
    state: { activeFreg: { mid: 'M01', model: map.model || null, cols: map.cols || [], module: mod,
                           report: (!map.model && map.report) || null,
                           screens: map.screens.map((id) => ({ id })) },
             activeScreen: null, activeModule: mod, activeModuleId: 'M01', lang: 'en' },
    t: (x) => x,
    openScreen(id) { calls.push(['openScreen', id]); this.state.activeScreen = { id }; },
    openFormScreen(id, hit, cfg) { calls.push(['openFormScreen', id, cfg.recordId]); },
    openRecord(id) { calls.push(['openRecord', id]); },
    openModuleFormForModel(model, id) {
      const form = (P03_FORM_CHIPS['M01:__by_model__'] || {})[model];
      if (!form) return false;
      calls.push(['openModuleFormForModel', form, id]);
      return true;
    },
    async rpc(route, params) {
      calls.push(['rpc', route, params.model, params.cols, params.domain]);
      return { rows: rpcRows };
    },
    openRecordTab(desc) { calls.push(['openRecordTab', desc.id, desc.screenId, desc.row]); },
    showToast(message) { calls.push(['toast', message]); },
  };
  const row = ['LABEL'];
  Object.defineProperty(row, 'recId', { value: recId, enumerable: false });
  await openFregRecord.call(self, row);
  return calls;
};
const scenarios = {
  fault: await run(3, 7, [{ id: 7, code: 'AUD-01', active: true }]),
  fault_gone: await run(3, 7, []),
  sla_policy: await run(7, 61, [{ id: 61, code: 'M01-DEFAULT' }]),
  intake_order: await run(0, 12, []),
  held_order: await run(8, 12, []),
  estimate: await run(5, 4, []),
  event_total: await run(12, null, []),
};

console.log(JSON.stringify({ subs, screens, news, creates, soCreates, soForms, scenarios, panels, fed,
  reports: mod.reports, forms: mod.forms,
  nav: mod.groups.flatMap((g) => g.screens.map((s) => ({ id: s.id, t: s.t }))),
  chips: Object.fromEntries(Object.entries(P03_FORM_CHIPS).filter(([k]) => k.startsWith('M01:'))),
  routes: Object.fromEntries(Object.entries(P03_REPORT_ROUTES).filter(([k]) => k.startsWith('M01:'))) }));
"""


@pytest.fixture(scope="module")
def m01(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_registry_m01_pages")
    for area in sorted(d for d in SRC.iterdir() if re.fullmatch(r"a\d\d", d.name)):
        (tmp / area.name).mkdir()
        for js in area.glob("*.js"):
            (tmp / area.name / (js.stem + ".mjs")).write_text(
                js.read_text(encoding="utf-8"), "utf-8"
            )
    meta = (SRC / "p03_modules_meta.js").read_text(encoding="utf-8")
    (tmp / "meta.mjs").write_text(IMPORT.sub(r'from "\1.mjs"', meta), "utf-8")
    engine = (SRC / "p03_workspace.js").read_text(encoding="utf-8").replace("\r\n", "\n")
    create, record = FREG_CREATE.search(engine), FREG_RECORD.search(engine)
    panels, report = FREG_PANELS.search(engine), FREG_REPORT.search(engine)
    assert report, "p03_workspace.js no longer defines async loadFregReport(mid, report)"
    assert create, "p03_workspace.js no longer defines fregCreate(mid, map)"
    assert record, "p03_workspace.js no longer defines async openFregRecord(row)"
    assert panels, "p03_workspace.js no longer defines fregPanels(mid, mod, map)"
    probe = tmp / "probe.mjs"
    probe.write_text(
        PROBE
        % {
            "create": create.group(1),
            "record": record.group(1),
            "panels": panels.group(1),
            "report": report.group(1),
        },
        "utf-8",
    )
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our own probe file
        [node, str(probe)],
        capture_output=True,
        encoding="utf-8",  # Bengali labels: never the Windows ANSI codepage
        check=True,
        timeout=60,
    )
    return json.loads(out.stdout)


def _sub(m01, no):
    return next(s for s in m01["subs"] if s["no"] == no)


# --- the button on each of the 13 pages --------------------------------------

MODULE = {"module": True}
EXPECTED_BUTTON = {
    "1": MODULE,  # intake IS where an order is made
    "2": MODULE,
    "3": None,  # warranties are registered against the device, not here
    "4": None,  # fault codes: M01-fault refuses "+ New"
    "5": None,  # diagnostic tree: M01-templates refuses "+ New"
    "6": {"screen": "M01-form-estimate", "label": "Diagnostic Estimate Request"},
    "7": None,  # hands an EXISTING on-site order to dispatch
    "8": None,  # SLA policies are not made in M01; its items are, on their own list
    # the hold form first asks which order, then runs action_defer_order
    "9": {"screen": "M01-form-hold", "label": "Place Order on Hold", "verbatim": True},
    "10": {"screen": "M01-form-qc", "label": "QC Checklist Inspection"},
    "11": None,  # ready / delivered / closed orders
    "12": None,  # the WIP board and its analysis
    "13": None,  # events are counted, not created: the page is fed by a report
}


def test_every_m01_page_offers_its_own_capture_or_none(m01):
    assert [s["no"] for s in m01["subs"]] == [str(n) for n in range(1, 14)]
    got = {s["no"]: s["create"] for s in m01["subs"]}
    assert got == EXPECTED_BUTTON


def test_a_page_that_works_on_existing_orders_says_so(m01):
    """The order slices name what they capture - nothing (`create: false`), or
    the form that acts on an existing order - so they never carry the module's
    "+ New Service Order" again."""
    for no in ("7", "11", "12"):
        sub = _sub(m01, no)
        assert sub["map"]["model"] == "fix.service.order"
        assert sub["map"].get("domain"), "sub-module %s is no longer a slice" % no
        assert sub["map"].get("create") is False, "sub-module %s" % no
    holds = _sub(m01, "9")
    assert holds["map"]["domain"] == [["is_deferred_block", "=", True]]
    assert holds["map"]["create"] == "M01-form-hold"


# --- the two panels ----------------------------------------------------------


def test_every_m01_report_and_form_is_on_a_submodule(m01):
    """The module shipped 7 reports and 6 forms and showed them on one page
    (the eighth report, Domain Events Published, came with sub-module 13). The
    SLA KPI Instance is no longer one of them: a clock is not typed in."""
    on_pages_r = {r for s in m01["subs"] for r in s["map"].get("reports", [])}
    on_pages_f = {f for s in m01["subs"] for f in s["map"].get("forms", [])}
    assert len(m01["reports"]) == 8 and len(m01["forms"]) == 5
    assert "SLA KPI Instance" not in m01["forms"]
    assert set(m01["reports"]) == on_pages_r
    assert set(m01["forms"]) == on_pages_f


def test_every_panel_chip_opens_a_declared_screen(m01):
    bad = []
    for sub in m01["subs"]:
        for report in sub["map"].get("reports", []):
            target = m01["routes"].get("M01:" + report)
            if target not in m01["screens"]:
                bad.append("%s report '%s' -> %s" % (sub["no"], report, target))
        for form in sub["map"].get("forms", []):
            target = m01["chips"].get("M01:" + form)
            if m01["screens"].get(target, {}).get("kind") != "model_form":
                bad.append("%s form '%s' -> %s" % (sub["no"], form, target))
    assert not bad, "\n  ".join(bad)


def test_a_screen_link_is_badged_with_what_it_is(m01):
    """The letter beside a screen link is its type: a computed report read
    'g' (grid) and an order list read 'r' (report)."""
    wrong = []
    for entry in m01["nav"]:
        kind = m01["screens"].get(entry["id"], {}).get("kind")
        if kind == "table_report" and entry["t"] != "r":
            wrong.append("%s is a report, badged '%s'" % (entry["id"], entry["t"]))
        if kind in ("so_list", "model_list") and entry["t"] != "g":
            wrong.append("%s is a list, badged '%s'" % (entry["id"], entry["t"]))
        if kind == "model_form" and entry["t"] != "f":
            wrong.append("%s is a form, badged '%s'" % (entry["id"], entry["t"]))
    assert not wrong, "\n  ".join(wrong)


# --- forms of a record nobody types in from scratch --------------------------


def test_m01_forms_that_need_a_record_do_not_open_blank(m01):
    for form in ("M01-order", "M01-form-sla-instance"):
        assert m01["screens"][form]["create"] is False, form
    # the hold form opens on a chooser of holdable orders, never on a blank order
    assert m01["screens"]["M01-form-hold"]["pickRecord"]
    # why: every field of an SLA clock is read-only
    assert m01["screens"]["M01-form-sla-instance"]["editable"] == 0
    # and the forms that DO create stay creatable
    for form in ("M01-form-order", "M01-form-estimate", "M01-form-qc", "M01-form-sla-item"):
        assert m01["screens"][form]["create"] is None, form


def test_an_existing_only_form_leads_to_the_list_its_record_is_picked_from(m01):
    """Estate-wide: opened with no record such a form goes to `back`, which
    must be a declared list (not another form) - and it says what to do."""
    forms = {
        fid: cfg
        for fid, cfg in m01["screens"].items()
        if cfg["kind"] == "model_form" and cfg["create"] is False
    }
    assert {"M01-order", "M01-form-sla-instance"} <= set(forms)
    bad = []
    for fid, cfg in forms.items():
        back = m01["screens"].get(cfg["back"] or "")
        if not back or back["kind"] == "model_form":
            bad.append("%s: back=%s is not a list" % (fid, cfg["back"]))
        if not cfg["pick"]:
            bad.append("%s: no `pick` instruction" % fid)
    assert not bad, "\n  ".join(bad)


def test_no_new_button_opens_an_existing_only_form(m01):
    """Estate-wide: "+ New" on a list, and a module's own create, must reach a
    form that can create - an existing-only one would bounce back to the list."""
    existing_only = {
        fid
        for fid, cfg in m01["screens"].items()
        if cfg["kind"] == "model_form" and cfg["create"] is False
    }
    assert len(m01["news"]) > 500, "only %d lists resolve a New form" % len(m01["news"])
    bad = ["%s -> %s" % (n["list"], n["form"]) for n in m01["news"] if n["form"] in existing_only]
    bad += [
        "%s create -> %s" % (c["mid"], c["screen"])
        for c in m01["creates"]
        if c["screen"] in existing_only
    ]
    assert not bad, "\n  ".join(bad)


# --- a record clicked on a sub-module page -----------------------------------


def test_a_record_without_a_form_opens_with_its_row(m01):
    """The pane renders the ROW. It is read by id, with the columns of the
    sub-module's own list, and handed to the pane with that list as context."""
    calls = m01["scenarios"]["fault"]
    assert calls[0] == ["openScreen", "M01-fault"]
    route, model, cols, domain = calls[1][1:]
    assert (route, model, domain) == ("/p03/model/records", "fix.fault.code", [["id", "=", 7]])
    assert cols == ["code", "name", "category", "default_severity", "active"]
    assert calls[2] == [
        "openRecordTab",
        7,
        "M01-fault",
        {"id": 7, "code": "AUD-01", "active": True},
    ]
    assert len(calls) == 3


def test_the_record_is_read_with_the_columns_of_its_own_list(m01):
    """SLA policies: the page's first screen is M01-sla and its columns differ
    from the page's grid - the pane labels come from the screen, so must the row."""
    calls = m01["scenarios"]["sla_policy"]
    assert calls[0] == ["openScreen", "M01-sla"]
    assert calls[1][3] == [
        "code",
        "service_type",
        "priority",
        "response_hours",
        "resolution_hours",
        "active",
    ]
    assert calls[2][:3] == ["openRecordTab", 61, "M01-sla"]


def test_a_record_that_cannot_be_read_says_so(m01):
    calls = m01["scenarios"]["fault_gone"]
    assert [c[0] for c in calls] == ["openScreen", "rpc", "toast"]
    assert not any(c[0] == "openRecordTab" for c in calls)


def test_an_order_opens_as_the_order_record(m01):
    """As from every order list - not a second copy of the intake form. The
    page's first screen is the intake console; it has no rows to open."""
    assert m01["scenarios"]["intake_order"] == [["openScreen", "M01-intake"], ["openRecord", 12]]


def test_a_held_order_opens_in_the_hold_release_form(m01):
    assert m01["chips"]["M01:__by_screen__"] == {"M01-holds": "M01-form-hold"}
    assert m01["scenarios"]["held_order"] == [
        ["openScreen", "M01-holds"],
        ["openFormScreen", "M01-form-hold", 12],
    ]


def test_a_record_with_a_form_still_opens_its_form(m01):
    assert m01["scenarios"]["estimate"] == [
        ["openScreen", "M01-estimates"],
        ["openModuleFormForModel", "M01-form-estimate", 4],
    ]


class FakeRequest:
    def __init__(self, env):
        self.env = env


def test_the_endpoint_reads_one_record_by_id(odoo_env):
    """What the pane is given: the list's columns for exactly that record, a
    boolean as a boolean (the grid shows its verdict, never the word)."""
    env = odoo_env
    fault = env["fix.fault.code"].search([], limit=1)
    if not fault:
        pytest.skip("the test database has no fault code")
    cols = ["code", "name", "category", "default_severity", "active"]
    with mock.patch.object(api, "request", FakeRequest(env)):
        res = api.P03GenericApiController().model_records(
            model="fix.fault.code", cols=cols, domain=[["id", "=", fault.id]]
        )
    assert "error" not in res, res
    assert len(res["rows"]) == 1
    row = res["rows"][0]
    assert row["id"] == fault.id and row["code"] == fault.code
    assert row["active"] is True


def test_the_page_grid_shows_a_boolean_as_a_verdict():
    """Wiring guard: the sub-module grid printed the literal "true" (and "-"
    for a real False, as if nobody had recorded it)."""
    engine = (SRC / "p03_workspace.js").read_text(encoding="utf-8")
    loader = engine[
        engine.index("async loadFregRecords(map)") : engine.index(
            "openScreen(screenId, customGroupEn)"
        )
    ]
    assert 'typeof v === "boolean") return v ? "✓" : "✗"' in loader
    assert "v === false" not in loader


# --- sub-module 13: events are counted, not listed ---------------------------


def test_m01_names_both_panels_on_every_page(m01):
    """M01 is curated: every mapping states its reports AND its forms, an
    empty list included, so the engine derives nothing for this module."""
    loose = [s["no"] for s in m01["subs"] if "reports" not in s["map"] or "forms" not in s["map"]]
    assert not loose, "sub-modules that leave a panel to be derived: %s" % loose
    for sub in m01["subs"]:
        assert sub["panels"]["reports"] == sub["map"]["reports"]
        assert sub["panels"]["forms"] == sub["map"]["forms"]


def test_the_event_page_is_fed_by_its_own_report(m01):
    """It showed the device-history list (Service Reports, sub-module 11's
    screen): M01 had nothing of its own for the events it publishes."""
    sub = _sub(m01, "13")
    assert "model" not in sub["map"]
    assert sub["map"]["report"] == "domain_events"
    assert sub["map"]["screens"] == ["M01-events"]
    assert m01["screens"]["M01-events"]["kind"] == "table_report"
    assert m01["routes"]["M01:Domain Events Published"] == "M01-events"
    assert {"id": "M01-events", "t": "r"} in m01["nav"]
    assert "M01-reports" not in sub["map"]["screens"]
    # a row of the page is a total: it leads to the report, it opens no record
    assert m01["scenarios"]["event_total"] == [["openScreen", "M01-events"]]


def test_the_event_page_grid_shows_the_report_rows(m01):
    """The page's grid is the report: its labelled columns, a blank as a
    dash, the report's title on the chip - and the server's own words when
    the report is not served."""
    fed = m01["fed"]["rows"]
    assert fed["asked"] == [["/p03/model/report", "M01", "domain_events"]]
    assert fed["loading"] is False
    assert fed["title"] == "Domain Events Published (Outbox)"
    assert fed["grid"]["cols"] == ["Event", "Events", "Latest Event"]
    assert fed["grid"]["rows"] == [["service_order.intake", 3, "\u2014"]]
    assert fed["grid"]["total"] == 1
    refused = m01["fed"]["refused"]
    assert refused["loading"] is False
    assert refused["grid"] == {
        "cols": [],
        "rows": [],
        "error": "Report not available on this surface",
    }


def test_the_domain_events_report_answers_on_any_database(odoo_env):
    """Read-only, so it can be pointed at a copy of the live estate
    (FIX_TEST_DB): the report runs on whatever the outbox holds and never
    lists an event of another module's record."""
    with mock.patch.object(api, "request", FakeRequest(odoo_env)):
        res = api.P03GenericApiController().model_report(module="M01", report="domain_events")
    assert "error" not in res, res
    assert res["title"] == "Domain Events Published (Outbox)"
    assert res["cols"] == [
        "event_type",
        "aggregate",
        "total",
        "published",
        "pending",
        "failed",
        "last",
    ]
    allowed = {"fix.service.order", "fix.estimate", "fix.sla.kpi.instance"}
    assert {r["aggregate"] for r in res["rows"]} <= allowed
    assert all(r["total"] == r["published"] + r["pending"] + r["failed"] for r in res["rows"])


def test_the_domain_events_report_counts_what_m01_published(odoo_env):
    """Through the endpoint the page calls. Counts per event and status for
    M01's aggregates only - and never a payload."""
    env = odoo_env
    Outbox = env["fix.event.outbox"]
    base = {"aggregate": "fix.service.order", "aggregate_id": 1, "payload": '{"secret": "x"}'}
    Outbox.create({**base, "event_type": "service_order.probe_m01_13", "status": "pending"})
    Outbox.create({**base, "event_type": "service_order.probe_m01_13", "status": "published"})
    Outbox.create({**base, "event_type": "service_order.probe_m01_13", "status": "published"})
    Outbox.create({**base, "aggregate": "res.partner", "event_type": "party.probe_m01_13"})
    with mock.patch.object(api, "request", FakeRequest(env)):
        res = api.P03GenericApiController().model_report(module="M01", report="domain_events")
    assert "error" not in res, res
    assert res["cols"] == [
        "event_type",
        "aggregate",
        "total",
        "published",
        "pending",
        "failed",
        "last",
    ]
    row = next(r for r in res["rows"] if r["event_type"] == "service_order.probe_m01_13")
    assert (row["total"], row["published"], row["pending"], row["failed"]) == (3, 2, 1, 0)
    assert row["aggregate"] == "fix.service.order" and row["last"]
    assert not any(r["event_type"] == "party.probe_m01_13" for r in res["rows"])
    assert all(
        set(r) == set(res["cols"]) for r in res["rows"]
    ), "a row carries more than its columns"
    assert "secret" not in json.dumps(res)


# --- the two panels on every sub-module page of every module -----------------


def test_no_panel_chip_points_nowhere(m01):
    """Explicit or derived: a report chip opens a declared screen and a form
    chip a form. A chip that resolves to nothing answers with a toast."""
    pages = m01["panels"]
    assert len({p["mid"] for p in pages}) == 67 and len(pages) >= 590
    bad = []
    for page in pages:
        tag = "%s/%s '%s'" % (page["mid"], page["no"], page["title"])
        bad += [
            "%s report '%s' -> %s" % (tag, r["name"], r["screen"])
            for r in page["reports"]
            if r["screen"] not in m01["screens"]
        ]
        bad += [
            "%s form '%s' -> %s (%s)" % (tag, f["name"], f["screen"], f["kind"])
            for f in page["forms"]
            if f["kind"] != "model_form"
        ]
    assert not bad, "\n  ".join(bad)


def test_a_derived_chip_provably_belongs_to_its_page(m01):
    """A mapping that names no reports / forms gets the module's own chips
    that are bound to it - a report whose screen is one of the page's
    screens, a form on the page's record or on the record of one of its
    lists. Nothing is matched by name."""
    bad, derived_forms, derived_reports = [], 0, 0
    for page in m01["panels"]:
        tag = "%s/%s '%s'" % (page["mid"], page["no"], page["title"])
        if not page["explicitReports"]:
            derived_reports += bool(page["reports"])
            bad += [
                "%s report '%s' (%s) is not one of its screens" % (tag, r["name"], r["screen"])
                for r in page["reports"]
                if r["screen"] not in page["screens"]
            ]
        if not page["explicitForms"]:
            derived_forms += bool(page["forms"])
            bad += [
                "%s form '%s' is on %s, not on its records %s"
                % (tag, f["name"], f["model"], page["models"])
                for f in page["forms"]
                if f["model"] not in page["models"]
            ]
    assert not bad, "\n  ".join(bad)
    # the point of the rule: these pages showed two empty panels
    assert derived_forms >= 300, "only %d pages derive a form" % derived_forms
    assert derived_reports >= 100, "only %d pages derive a report" % derived_reports


# --- Hold Management: the list where a hold is placed (2026-11-12) -----------
# It listed holds and offered nothing to enter: no button, and the only way in
# was a row action that asked for the reason as a CODE in a browser prompt and
# could not take a resume date.


def test_hold_management_offers_to_place_a_hold(m01):
    assert {"list": "M01-holds", "screen": "M01-form-hold", "label": "Place Order on Hold"} in m01[
        "soCreates"
    ]
    # and the order book offers a new order, which a hold needs first
    assert {"list": "M01-all", "screen": "M01-form-order", "label": "New Service Order"} in m01[
        "soCreates"
    ]
    for entry in m01["soCreates"]:
        assert m01["screens"][entry["screen"]]["kind"] == "model_form", entry


def test_the_defer_row_action_opens_the_hold_form(m01):
    """Every order list's "Defer / Hold" opens the form for that order, and only
    in states the server accepts a hold in (it refuses ready and finished)."""
    defers = [a for a in m01["soForms"] if a["action"] == "defer"]
    assert {a["list"] for a in defers} >= {"M01-all", "M01-holds", "M01-wip", "M01-rework"}
    for a in defers:
        assert a["form"] == "M01-form-hold" and a["m"] == "action_defer_order"
        assert not {"ready", "delivered", "closed", "cancelled"} & set(a["states"]), a


def test_the_hold_form_picks_an_order_then_runs_the_hold(m01, odoo_env):
    form = m01["screens"]["M01-form-hold"]
    assert form["newLabel"] == "Place Order on Hold"
    pick = form["pickRecord"]
    assert pick["domain"] == [
        ["is_deferred_block", "=", False],
        ["state", "not in", ["ready", "delivered", "closed", "cancelled"]],
    ]
    order_fields = odoo_env["fix.service.order"]._fields
    assert [c for c in pick["cols"] if c not in order_fields] == []
    act = form["saveAction"]
    assert act["method"] == "action_defer_order"
    assert act["method"] in api.SURFACES["fix.service.order"]["actions"]
    # each argument is a field the form shows, under the name the method takes
    shown = {f["name"]: f for f in form["fields"]}
    assert act["kwargs"] == {
        "reason": "deferred_reason",
        "resume_date": "deferred_until",
        "notes": "deferred_notes",
    }
    assert set(act["kwargs"].values()) <= set(shown)
    assert shown["deferred_reason"]["required"]
    # the reason is guarded on the model: readonly for the generic write, an
    # input on this form only because the action carries it
    assert order_fields["deferred_reason"].readonly
    engine = (SRC / "p03_workspace.js").read_text(encoding="utf-8")
    assert "for (const name of Object.values(act.kwargs || {}))" in engine


class _SupervisorRequest:
    def __init__(self, env):
        self.env = env


def test_a_hold_is_placed_through_the_endpoint_the_form_calls(odoo_env):
    """As the form sends it: action_defer_order with the three values - and a
    user without the Service Supervisor role is refused, as before."""
    env = odoo_env
    company = env.company
    entity = env["fix.entity"].create(
        {"code": "HOLDF", "legal_name": "Hold Form Ltd", "company_id": company.id}
    )
    ou = env["operating.unit"].search([("company_id", "=", company.id)], limit=1)
    branch = env["fix.branch"].create(
        {
            "code": "HLDF",
            "name": "Hold Form Centre",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    customer = env["res.partner"].create({"name": "Hold Form Customer", "phone": "01710000099"})
    brand = env["fix.brand"].create({"name": "Holdworks", "code": "HLDW"})
    model = env["fix.device.model"].create(
        {"brand_id": brand.id, "name": "HW-1", "device_type": "laptop"}
    )
    device = env["fix.device"].create(
        {"serial_number": "SN-HOLD-FORM-1", "device_model_id": model.id, "owner_id": customer.id}
    )
    order = env["fix.service.order"].create(
        {
            "customer_id": customer.id,
            "branch_id": branch.id,
            "device_id": device.id,
            "fault_description": "No power",
            "state": "intake",
        }
    )
    assert not order.is_deferred_block
    kwargs = {"reason": "customer_travel", "resume_date": "2026-12-01", "notes": "Customer abroad"}

    clerk = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "Hold Form Clerk",
                "login": "hold.form.clerk@m01.test",
                "group_ids": [(6, 0, [env.ref("base.group_user").id])],
            }
        )
    )
    with mock.patch.object(api, "request", _SupervisorRequest(env(user=clerk.id))):
        refused = api.P03GenericApiController().model_action(
            model="fix.service.order", ids=[order.id], method="action_defer_order", kwargs=kwargs
        )
    assert refused["success"] is False and "Supervisor" in refused["error"], refused
    order.invalidate_recordset()
    assert not order.is_deferred_block

    with mock.patch.object(api, "request", _SupervisorRequest(env)):
        placed = api.P03GenericApiController().model_action(
            model="fix.service.order", ids=[order.id], method="action_defer_order", kwargs=kwargs
        )
    assert placed["success"] is True, placed
    order.invalidate_recordset()
    assert order.is_deferred_block
    assert order.deferred_reason == "customer_travel"
    assert str(order.deferred_until) == "2026-12-01"
    assert order.deferred_notes == "Customer abroad"


# --- Live SLA Clocks: evidence, not data entry (2026-11-12) ------------------


def test_the_sla_clock_is_not_offered_as_a_data_entry_form(m01):
    """Every field of a clock is guarded; it starts by itself. It was offered
    as a form chip ("Forms Capturing It", the module chips, the nav) over a list
    that had - correctly - no "+ New", which read as a broken form."""
    assert "SLA KPI Instance" not in m01["forms"]
    assert "M01:SLA KPI Instance" not in m01["chips"]
    assert not any(e["id"] == "M01-form-sla-instance" for e in m01["nav"])
    assert _sub(m01, "3")["map"]["forms"] == []
    # a clock row still opens its read-only record form
    assert m01["chips"]["M01:__by_model__"]["fix.sla.kpi.instance"] == "M01-form-sla-instance"


def test_the_clock_list_says_how_a_clock_starts(m01):
    clocks = m01["screens"]["M01-sla-instances"]
    assert clocks["create"] is False
    assert "starts by itself" in clocks["empty"] and "cannot be typed in" in clocks["empty"]
    xml = (SRC / "p03_workspace.xml").read_text(encoding="utf-8")
    assert "state.gl.modelCfg.empty ? t(state.gl.modelCfg.empty)" in xml
