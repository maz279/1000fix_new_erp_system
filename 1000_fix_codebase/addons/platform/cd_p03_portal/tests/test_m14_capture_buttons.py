# M14 Trade-In & Refurbishment: every sub-module page offers the button that
# captures its record (audit 2026-11-13).
#
# Destruction Gate and Resale named no form, so neither page had a button,
# and Bulk Buy-Back offered the single-unit intake (no lot, no declared asset
# list). The trade-in pickers offered every trade-in although each record is
# refused outside one stage (a grade or QA outside refurbishment, a harvest
# of anything but a graded grade-E unit, a valuation after acceptance).
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
CONTROLLER = ROOT / "controllers" / "a05" / "m14.py"

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
const mod = P03_MODULES.M14;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M14', map);
  const forms = fregPanels('M14', mod, map).forms.map((f) => {
    const id = P03_FORM_CHIPS['M14:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  return { no: s[0], model: map.model || null, create, forms, screens: map.screens || [] };
});
const fields = (id) => Object.fromEntries((P03_DATA_SCREENS[id].sections || [])
  .flatMap((s) => s.fields).map((f) => [f.name, { domain: f.domain || null, readonly: !!f.readonly }]));
const S = P03_DATA_SCREENS;
console.log(JSON.stringify({ subs, screens: Object.fromEntries(
  Object.entries(S).filter(([id]) => id.startsWith('M14-')).map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create, domain: c.domain || null,
    pickRecord: c.pickRecord || null, empty: !!c.empty, back: c.back || null,
    lines: c.lines ? c.lines.field : null,
    actions: (c.actions || []).map((a) => a.m),
    fields: c.kind === 'model_form' ? fields(id) : null }])) }));
"""

# How each page's record is captured: every M14 page has a form that a person
# fills in (a new record, or a pick-then-fill step on an existing trade-in).
CAPTURE = {
    "1": "M14-form-request",
    "2": "M14-form-valuation",
    "3": "M14-form-provenance",
    "4": "M14-form-settlement",
    "5": "M14-form-bulk",
    "6": "M14-form-wipe",
    "7": "M14-form-refurb",
    "8": "M14-form-grade",
    "9": "M14-form-resale",
    "10": "M14-form-harvest",
}


@pytest.fixture(scope="module")
def m14(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m14_capture")
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


def _surfaces():
    tree = ast.parse(CONTROLLER.read_text(encoding="utf-8"))
    node = next(
        n.value
        for n in tree.body
        if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "SURFACES"
    )
    return ast.literal_eval(node)


def test_every_page_is_classified(m14):
    assert sorted(s["no"] for s in m14["subs"]) == sorted(CAPTURE, key=str)


@pytest.mark.parametrize("no", sorted(CAPTURE, key=int))
def test_each_page_offers_its_capture(m14, no):
    sub = next(s for s in m14["subs"] if s["no"] == no)
    assert sub["create"], "page %s has no + New button" % no
    screen = sub["create"].get("screen") or "M14-form-request"  # module: the intake
    assert screen == CAPTURE[no], "page %s's button opens %s" % (no, screen)
    assert any(f["opens"] and f["id"] == CAPTURE[no] for f in sub["forms"]), (
        "page %s does not show its form chip" % no
    )
    for f in sub["forms"]:
        assert f["kind"] == "model_form", "chip %s opens %s" % (f["f"], f["kind"])


def test_m14_never_offers_to_issue_a_destruction_certificate(m14):
    """Spec §13 SoD: the gate is operated by M06, never by the module it gates."""
    offered = {f["model"] for s in m14["subs"] for f in s["forms"]}
    assert "fix.data.wipe.certificate" not in offered
    wipe = m14["screens"]["M14-form-wipe"]
    assert wipe["pickRecord"]["domain"] == [["state", "=", "collected"]]
    assert wipe["fields"]["wipe_certificate_id"] == {
        "domain": [["sanitization_status", "=", "verified"]],
        "readonly": False,
    }


def test_gate_and_resale_pages_list_the_units_waiting_with_their_buttons(m14):
    gate = m14["screens"]["M14-gate"]
    assert gate["model"] == "fix.tradein.request" and gate["create"] is False and gate["empty"]
    assert gate["actions"] == ["action_wipe", "action_refurbish"]
    prep = m14["screens"]["M14-resale-prep"]
    assert prep["domain"] == [["state", "=", "graded"]] and prep["create"] is False
    assert prep["actions"] == ["action_resale_ready"]
    resale = m14["screens"]["M14-form-resale"]
    assert ["grade", "!=", "e"] in resale["pickRecord"]["domain"]
    editable = {n for n, f in resale["fields"].items() if not f["readonly"]}
    assert editable == {
        "resale_channel",
        "resale_value",
        "marketplace_seller_id",
        "resale_listed_on",
    }


def test_bulk_buy_back_is_a_lot_with_its_declared_assets(m14):
    sub = next(s for s in m14["subs"] if s["no"] == "5")
    assert sub["model"] == "fix.bulk.buyback"
    form = m14["screens"]["M14-form-bulk"]
    assert form["lines"] == "asset_ids"
    lst = m14["screens"]["M14-bulk"]
    assert lst["actions"] == ["action_open_intakes", "action_close"]


# Each record is refused by its model outside one stage of the trade-in: the
# picker offers only the trade-ins at that stage.
PICKERS = {
    "M14-form-valuation": [["state", "in", ["draft", "offered"]]],
    "M14-form-provenance": [["state", "not in", ["closed", "rejected"]]],
    "M14-form-refurb": [["state", "=", "refurbished"]],
    "M14-form-qa": [["state", "=", "refurbished"]],
    "M14-form-grade": [["state", "=", "refurbished"]],
    "M14-form-harvest": [["state", "in", ["graded", "closed"]], ["grade", "=", "e"]],
}


@pytest.mark.parametrize("form", sorted(PICKERS))
def test_trade_in_pickers_offer_only_the_stage_the_record_needs(m14, form):
    assert m14["screens"][form]["fields"]["tradein_id"]["domain"] == PICKERS[form]


def test_every_capture_button_is_whitelisted():
    surfaces = _surfaces()
    assert {"action_wipe", "action_refurbish", "action_resale_ready"} <= surfaces[
        "fix.tradein.request"
    ]["actions"]
    assert surfaces["fix.bulk.buyback"]["actions"] == {"action_open_intakes", "action_close"}
