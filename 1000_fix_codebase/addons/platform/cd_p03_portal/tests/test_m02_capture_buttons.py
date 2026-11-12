# M02 Field Service & Dispatch: every sub-module page offers the button that
# captures its record (audit 2026-11-12).
#
# Nine of the twelve M02 pages named no form. Van Stock, Field Safety and
# Territory had no button, though M15, M59 and M30 master forms for those
# records. Field Exceptions offered a "+ New" that the decline log refuses on
# save. "Crew Assignment" opened the field-order form, which has no crew. The
# Field Evidence Hub listed M31's bench-repair evidence. The safety screens said
# no safety store existed, though fix.hse.loneworker did. The KPI row showed
# 84.5 / 91.5 / 32.7 / 100 % "live" with no field order at all.
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
ROOT = HERE.parent
SRC = ROOT / "static" / "src"
CONTROLLER = ROOT / "controllers" / "a02" / "m02.py"

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
const mod = P03_MODULES.M02;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M02', map);
  const forms = fregPanels('M02', mod, map).forms.map((f) => {
    const id = P03_FORM_CHIPS['M02:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const lists = (map.screens || []).map((id) => ({ id, cfg: P03_DATA_SCREENS[id] || {} }))
    .filter((x) => x.cfg.kind === 'model_list')
    .map((x) => ({ id: x.id, model: x.cfg.model, create: x.cfg.create !== false, empty: !!x.cfg.empty,
      actions: (x.cfg.actions || []).map((a) => a.m) }));
  return { no: s[0], model: map.model || null, create, forms, lists };
});
const S = P03_DATA_SCREENS;
console.log(JSON.stringify({ subs, screens: Object.fromEntries(
  Object.entries(S).filter(([id]) => id.startsWith('M02-')).map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create, pick: c.pick || null,
    pickRecord: !!c.pickRecord, empty: !!c.empty, actions: (c.actions || []).map((a) => a.m),
    gated: (c.actions || []).map((a) => [a.m, a.states || null]),
    fields: (c.sections || []).flatMap((s) => (s.fields || []).map((f) => [f.name, !!f.readonly])),
    text: JSON.stringify([c.tabs || [], (c.sections || []).map((s) => [s.title, s.note || '', (s.fields || []).map((f) => f.label)])]) }])) }));
"""

# How each page's record is captured. 'form': a "+ New" or a chip that opens
# an in-workspace form. 'actions': buttons on one of its lists write it.
# 'system': written by the technician app or a workflow - typing it in would
# fabricate evidence, so the page offers nothing and says where it comes from.
CAPTURE = {
    "1": "form",  # a new field order enters the assignment queue
    "2": "form",  # Emergency Reschedule (pick the order first)
    "3": "form",  # Route Plan
    "4": "form",  # Zone Geofence + Dispatch Zone (M30)
    "5": "form",  # Field Work Order + Crew Assignment
    "6": "form",  # Technician Work Order
    "7": "system",  # offline command journal
    "8": "system",  # GPS pings
    "9": "system",  # signature / photos from the technician app
    "10": "form",  # Van Stock Reconciliation (M15)
    "11": "actions",  # Record Collection / Hand Over Cash
    "12": "form",  # Lone-Worker Check-In (M59)
}


@pytest.fixture(scope="module")
def m02(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m02_capture")
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


def test_every_page_is_classified(m02):
    assert sorted(s["no"] for s in m02["subs"]) == sorted(CAPTURE)


@pytest.mark.parametrize("no", sorted(CAPTURE, key=int))
def test_each_page_offers_its_capture(m02, no):
    sub = next(s for s in m02["subs"] if s["no"] == no)
    opening = [f for f in sub["forms"] if f["opens"]]
    kind = CAPTURE[no]
    if kind == "form":
        assert sub["create"] or opening, "page %s has no + New and no form chip" % no
        for f in sub["forms"]:
            assert f["kind"] == "model_form", "chip %s opens %s" % (f["f"], f["kind"])
    elif kind == "actions":
        assert any(lst["actions"] for lst in sub["lists"]), "page %s: no list writes it" % no
    else:
        assert not sub["create"] and not opening, "page %s would let a person type in %s" % (
            no,
            sub["model"],
        )
        assert all(lst["empty"] for lst in sub["lists"]), (
            "page %s: say where records come from" % no
        )


def test_a_list_whose_model_refuses_create_offers_no_new(m02):
    # fix.field.decline.log.create raises unless Decline writes it
    exc = m02["screens"]["M02-exceptions"]
    assert exc["create"] is False and exc["empty"]
    form = m02["screens"]["M02-form-exception"]
    assert form["create"] is False and form["pick"]


def test_crew_assignment_adds_a_technician_work_order(m02):
    sub = next(s for s in m02["subs"] if s["no"] == "5")
    crew = next(f for f in sub["forms"] if f["f"] == "Crew Assignment")
    assert crew["model"] == "fix.work.order"


def test_reschedule_never_creates_a_field_order(m02):
    form = m02["screens"]["M02-form-reschedule"]
    assert form["pickRecord"], "a reschedule acts on an existing order"


def test_field_evidence_is_field_order_evidence(m02):
    assert m02["screens"]["M02-evidence"]["model"] == "fix.field.order"
    assert next(s for s in m02["subs"] if s["no"] == "9")["model"] == "fix.field.order"


def test_safety_screens_read_the_real_stores(m02):
    assert m02["screens"]["M02-loneworker"]["model"] == "fix.hse.loneworker"
    assert m02["screens"]["M02-panic"]["model"] == "fix.offline.idempotency.ledger"


def test_collection_buttons_are_whitelisted():
    tree = ast.parse(CONTROLLER.read_text(encoding="utf-8"))
    surfaces = next(
        n.value
        for n in tree.body
        if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "SURFACES"
    )
    surfaces = ast.literal_eval(surfaces)
    allowed = surfaces["fix.field.order"]["actions"]
    assert {"action_record_collection", "action_handover_field_cash"} <= allowed


def test_kpis_report_nothing_measured_as_none():
    """No invented fallback: `x if measured else 84.5` printed 84.5 % as live."""
    tree = ast.parse(CONTROLLER.read_text(encoding="utf-8"))
    kpis = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "kpis")
    invented = [
        ast.unparse(n)
        for n in ast.walk(kpis)
        if isinstance(n, ast.IfExp)
        and isinstance(n.orelse, ast.Constant)
        and isinstance(n.orelse.value, float)
        and n.orelse.value != 0.0
    ]
    assert not invented, invented


# --- bidirectional audit (2026-11-13): the screen agrees with the backend ----


def test_every_list_button_names_the_states_the_server_accepts(m02):
    """A button without `states` showed as available in every state, and the
    server then refused most presses (Decline outside 'dispatched', ...)."""
    ungated = [
        "%s:%s" % (sid, m)
        for sid, s in m02["screens"].items()
        if s["kind"] == "model_list"
        for m, states in s["gated"]
        if not states
    ]
    assert not ungated, ungated


def test_a_route_plan_can_be_built_and_run(m02):
    routes = m02["screens"]["M02-routes"]
    assert {"action_optimize_route", "action_start_route", "action_complete_route"} <= set(
        routes["actions"]
    )
    fields = dict(m02["screens"]["M02-form-route"]["fields"])
    # optimise needs two stops: the stops are on the form
    assert fields.get("field_order_ids") is False
    # the reference is numbered on save (read-only on the model)
    assert fields.get("name") is True


def test_a_work_order_slot_can_get_its_technician(m02):
    assert "action_assign" in m02["screens"]["M02-wo"]["actions"]


def test_nobody_types_a_safety_heartbeat(m02):
    assert dict(m02["screens"]["M02-form-wo"]["fields"])["lone_worker_checkin_at"] is True


def test_the_geofence_form_asks_for_the_shape_the_model_checks(m02):
    text = m02["screens"]["M02-form-zone"]["text"]
    assert "GeoJSON" not in text
    assert "radius_m" in text and "points" in text
