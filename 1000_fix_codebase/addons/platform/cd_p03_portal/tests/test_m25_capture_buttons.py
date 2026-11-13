# M25 Business Intelligence: every sub-module page offers the button that
# captures ITS record (audit 2026-11-13).
#
# Before: Standard Report Library and Lifecycle & Usage offered
# "+ New Dashboard" (neither page's record is a dashboard); Embedded Analytics
# offered nothing - its sync-connection list refused + New and had no form;
# the dashboard lifecycle (review, certification through M63, retirement) was
# served by the controller but declared on no screen, and the dashboard form
# had no Data Steward, so every review was refused; the spreadsheet-retirement
# register (FR-BID-034) had no model, so its KPI tile had no source; the
# schedule and alert forms asked for free-typed keys.
#
# Evaluated as the browser evaluates it: node runs the engine's own fregCreate
# and fregPanels over the real registry fragments (the M24/M37 fixture).
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
CONTROLLER = HERE.parent / "controllers" / "a11" / "m25.py"
ADDONS = HERE.parents[2]

_spec = importlib.util.spec_from_file_location(
    "_estate_pages", HERE / "test_estate_module_pages.py"
)
_estate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_estate)

PROBE = """
import * as M from './meta.mjs';
const { P03_MODULES, P03_MODULE_CREATE, P03_FORM_CHIPS, P03_DATA_SCREENS } = M;
function %(create)s
function %(panels)s
const mod = P03_MODULES.M25;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M25', map);
  const forms = fregPanels('M25', mod, map).forms.map((f) => {
    const id = P03_FORM_CHIPS['M25:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && cfg.create !== false };
  });
  return { no: s[0], title: s[1], model: map.model || null, report: map.report || null,
    create: create && (create.screen || (create.module ? 'module' : null)),
    label: create ? (create.label || null) : null, forms };
});
const S = P03_DATA_SCREENS;
console.log(JSON.stringify({ subs,
  module_create: P03_MODULE_CREATE.M25,
  kpis: mod.kpis,
  screens: Object.fromEntries(Object.entries(S).filter(([id]) => id.startsWith('M25-')).map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create, report: c.report || null,
    stateField: c.stateField || null, empty: !!c.empty, newLabel: c.newLabel || null,
    statusField: c.status ? c.status.field : null,
    actions: (c.actions || []).map((a) => ({ m: a.m, states: a.states || null, asks: (a.asks || []).map((x) => x.kwarg) })),
    cols: c.cols || [],
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({ name: f.name, type: f.type || null,
      choices: f.choices || null, readonly: !!f.readonly, required: !!f.required })) }])),
  by_screen: P03_FORM_CHIPS['M25:__by_screen__'] }));
"""

# What each page captures (the form its "+ New" opens).
CAPTURE = {
    "1": "module",  # a saved dashboard bound to a role cockpit
    "2": "M25-form-schedule",  # the library's packs are computed: a schedule sends one
    "3": "module",  # a saved (draft) dashboard - governed self-service
    "4": "M25-form-schedule",  # a distribution schedule (alert via its chip)
    "5": "M25-form-sync",  # an analytics dataset connection
    "6": "module",  # a dashboard (mobile renders the role cockpits)
    "7": "M25-form-pack",  # a manual pack on the spreadsheet-retirement register
}

# The chips each page must offer (a capture that page owns but its + New is not).
CHIPS = {
    "2": {"Distribution Schedule"},
    "4": {"Distribution Schedule", "Alert Subscription"},
    "5": {"Sync Connection"},
    "6": {"Dashboard", "Distribution Schedule"},
    "7": {"Manual Pack", "Dashboard"},
}


@pytest.fixture(scope="module")
def m25(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m25_capture")
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


def _sub(m25, no):
    return next(s for s in m25["subs"] if s["no"] == no)


def _controller_literal(name):
    tree = ast.parse(CONTROLLER.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == name:
            return ast.literal_eval(node.value)
    raise AssertionError("m25.py no longer declares %s" % name)


def _served_actions():
    return {m: set(cfg.get("actions") or ()) for m, cfg in _controller_literal("SURFACES").items()}


def _report_keys():
    """Every key REPORTS ends up with: the literal plus the later assignments
    and .update({...}) calls in m25.py."""
    text = CONTROLLER.read_text(encoding="utf-8")
    keys = set()
    for node in ast.parse(text).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "REPORTS":
            keys |= {k.value for k in node.value.keys}
    keys |= set(re.findall(r'^REPORTS\["([a-z_]+)"\]\s*=', text, re.M))
    block = re.search(r"^REPORTS\.update\(\s*\{(.*?)\}\s*\)", text, re.M | re.S)
    if block:
        keys |= set(re.findall(r'"([a-z_]+)":', block.group(1)))
    return keys


def _metric_keys():
    text = CONTROLLER.read_text(encoding="utf-8")
    body = text[text.index("def _metrics(env):") :]
    body = body[: body.index("\ndef ", 1)]
    return set(re.findall(r'm\["([a-z0-9_]+)"\]\s*=', body))


def _model_source(model):
    for py in ADDONS.rglob("models/*.py"):
        text = py.read_text(encoding="utf-8", errors="ignore")
        if re.search(r'_name = ["\']%s["\']' % re.escape(model), text):
            return text
    raise AssertionError("no source declares %s" % model)


def _model_fields(model):
    text = _model_source(model)
    start = re.search(r'_name = ["\']%s["\']' % re.escape(model), text).start()
    nxt = re.search(r"^class ", text[start:], re.M)
    body = text[start : start + nxt.start()] if nxt else text[start:]
    return set(re.findall(r"^    ([a-z_0-9]+) = fields\.", body, re.M))


@pytest.mark.parametrize("no", sorted(CAPTURE, key=int))
def test_every_page_captures_its_own_record(m25, no):
    sub = _sub(m25, no)
    assert sub["create"] == CAPTURE[no], "M25 sub-module %s '%s' captures %r, expected %r" % (
        no,
        sub["title"],
        sub["create"],
        CAPTURE[no],
    )


def test_no_page_but_a_dashboard_page_offers_a_dashboard(m25):
    """The old defect: report library and lifecycle offered + New Dashboard."""
    for sub in m25["subs"]:
        if sub["create"] == "module":
            assert sub["model"] == "fix.bi.dashboard", sub


@pytest.mark.parametrize("no", sorted(CHIPS, key=int))
def test_each_page_shows_its_chips_and_they_open_a_form(m25, no):
    sub = _sub(m25, no)
    shown = {f["f"] for f in sub["forms"]}
    assert CHIPS[no] <= shown, "page %s chips %s miss %s" % (no, shown, CHIPS[no] - shown)
    for f in sub["forms"]:
        assert f["opens"], "chip %s on page %s opens no creatable form" % (f["f"], no)


def test_the_report_library_page_reads_the_library_pack(m25):
    sub = _sub(m25, "2")
    assert sub["report"] == "report_library" and not sub["model"]
    assert "report_library" in _report_keys()
    assert m25["screens"]["M25-library"]["report"] == "report_library"


def test_every_declared_action_is_served(m25):
    served = _served_actions()
    for sid, cfg in m25["screens"].items():
        for act in cfg["actions"]:
            assert act["m"] in served.get(cfg["model"], set()), (
                "%s declares %s on %s, which the controller does not serve"
                % (sid, act["m"], cfg["model"])
            )


def test_the_dashboard_lifecycle_is_on_the_builder(m25):
    acts = {a["m"]: a for a in m25["screens"]["M25-builder"]["actions"]}
    assert set(acts) == {"action_submit_review", "action_request_approval", "action_retire"}
    assert acts["action_submit_review"]["states"] == ["draft"]
    assert acts["action_retire"]["states"] == ["certified"]
    assert "justification" in acts["action_request_approval"]["asks"]
    assert m25["screens"]["M25-builder"]["stateField"] == "state"


def test_the_dashboard_form_names_its_steward_and_shows_its_state(m25):
    form = m25["screens"]["M25-form-dashboard"]
    names = {f["name"]: f for f in form["fields"]}
    assert "steward_id" in names and not names["steward_id"]["readonly"]
    assert form["statusField"] == "state"
    for system in ("owner_id", "certified_by", "certified_at"):
        assert names[system]["readonly"], system


def test_the_retirement_register_is_on_lifecycle_and_usage(m25):
    packs = m25["screens"]["M25-packs"]
    assert packs["model"] == "fix.bi.manual.pack" and packs.get("create") is not False
    assert m25["by_screen"]["M25-packs"] == "M25-form-pack"
    acts = {a["m"]: a for a in packs["actions"]}
    assert acts["action_start_parallel_run"]["states"] == ["registered", "investigated"]
    assert acts["action_reconcile_matched"]["states"] == ["parallel_run"]
    assert "note" in acts["action_reconcile_discrepancy"]["asks"]
    assert acts["action_retire"]["states"] == ["accepted"]
    assert m25["screens"]["M25-form-pack"]["newLabel"] == "Register a Manual Pack"


def test_the_sync_connection_is_creatable_and_runnable(m25):
    sync = m25["screens"]["M25-sync"]
    assert sync.get("create") is not False
    assert {a["m"] for a in sync["actions"]} == {"action_test_connection", "action_run_sync"}
    assert m25["by_screen"]["M25-sync"] == "M25-form-sync"


def test_schedule_sends_now_and_says_why_it_failed(m25):
    sched = m25["screens"]["M25-schedules"]
    assert [a["m"] for a in sched["actions"]] == ["action_send_now"]
    assert "last_note" in sched["cols"]


def test_schedule_report_choices_are_the_library(m25):
    for sid in ("M25-form-schedule", "M25-form-pack"):
        field = next(
            f
            for f in m25["screens"][sid]["fields"]
            if f["name"] in ("report_key", "replacement_report_key")
        )
        assert field["type"] == "selection" and field["choices"], sid
        keys = {k for k, _ in field["choices"]}
        missing = {k for k in keys if k.split(":", 1)[1] not in _report_keys()}
        assert not missing, "%s offers packs the library does not serve: %s" % (sid, missing)
        assert all(k.startswith("M25:") for k in keys)


def test_alert_metric_choices_are_exactly_the_metric_bank(m25):
    field = next(f for f in m25["screens"]["M25-form-alert"]["fields"] if f["name"] == "metric_key")
    assert field["type"] == "selection"
    assert {k for k, _ in field["choices"]} == _metric_keys()


def test_every_form_field_exists_on_its_model(m25):
    for sid, cfg in m25["screens"].items():
        if cfg["kind"] not in ("model_form", "model_list") or not cfg["model"]:
            continue
        fields = _model_fields(cfg["model"])
        for name in [f["name"] for f in cfg["fields"]] + cfg["cols"]:
            assert name in fields or name in ("display_name", "create_date"), (
                "%s shows %s.%s, which the model does not declare" % (sid, cfg["model"], name)
            )


def test_the_spreadsheets_retired_tile_has_a_source(m25):
    tile = next(k for k in m25["kpis"] if k["m"] == "spreadsheets_retired")
    assert tile.get("src") is not False
    text = CONTROLLER.read_text(encoding="utf-8")
    assert '"spreadsheets_retired": None' not in text
    assert "fix.bi.manual.pack" in _controller_literal("SURFACES")
