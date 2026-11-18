# M15 Spare Parts & Inventory: every sub-module page offers the button that
# captures its record, and only where a person may type that record
# (audit 2026-11-13).
#
# Before: Location Hierarchy (FR-INV-002) listed locations with no way to add
# one. Ownership Segregation had no capture, and the approved class-change
# document (FR-INV-018, BRU-INV-06) sat on no page at all. Van Stock could not
# set a van's par levels (FR-INV-029) and Transfers & RTV could not raise a
# return to vendor (FR-INV-052), although both forms existed. Serial & Lot
# Trace offered "+ New Serial / Lot", a form whose every required field the
# server refuses: lots are created by goods receipts only. The suspense
# integrity check was on no page.
#
# Evaluated as the browser evaluates it: node runs the engine's own fregCreate
# and fregPanels over the real registry fragments (the M10 guard's fixture).
from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "static" / "src"

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
const mod = P03_MODULES.M15;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M15', map);
  const forms = fregPanels('M15', mod, map).forms.map((f) => {
    const id = P03_FORM_CHIPS['M15:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const lists = (map.screens || []).map((id) => ({ id, cfg: P03_DATA_SCREENS[id] || {} }))
    .filter((x) => x.cfg.kind === 'model_list')
    .map((x) => ({ id: x.id, model: x.cfg.model, create: x.cfg.create !== false, empty: !!x.cfg.empty }));
  return { no: s[0], model: map.model || null, screens: map.screens || [],
    create: create && (create.screen || (create.module ? 'module' : null)), forms, lists };
});
const S = P03_DATA_SCREENS;
console.log(JSON.stringify({ subs,
  nav: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  byModel: P03_FORM_CHIPS['M15:__by_model__'] || {},
  screens: Object.fromEntries(Object.entries(S).filter(([id]) => /^M(15|41)-/.test(id)).map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create, pick: !!c.pick, back: c.back || null,
    empty: !!c.empty }])) }));
"""

# How each page's record is captured. 'form': a "+ New" or a chip opening an
# in-workspace form. 'system': moved only by a workflow (receipts, issues,
# transfers, counts, wave release) or calculated, so the page offers nothing
# and every list on it says where its rows come from.
CAPTURE = {
    "1": "system",  # on-hand: the ledger position (FR-INV-001/005)
    "2": "form",  # stock location (FR-INV-002, FR-INV-028 vans)
    "3": "form",  # ownership-class change (FR-INV-018)
    "4": "form",  # a reservation held for a job (FR-INV-019..021, 027; pass 2)
    "5": "form",  # stock issue (FR-INV-022), backorder (FR-INV-025)
    "6": "form",  # van reconciliation + reorder rule (FR-INV-029..031)
    "7": "form",  # a recall (FR-INV-040; pass 2) - serials still come from receipts
    "8": "system",  # valuation: weighted average from the movements
    "9": "form",  # goods receipt (the module's button)
    "10": "form",  # cycle / full count
    "11": "system",  # ageing and ABC are calculated
    "12": "form",  # transfer request, scrap order, return to vendor
    "13": "form",  # item master
}


@pytest.fixture(scope="module")
def m15(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m15_capture")
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


def _sub(m15, no):
    return next(s for s in m15["subs"] if s["no"] == no)


def _opening(sub):
    return {f["f"]: f for f in sub["forms"] if f["opens"]}


def test_every_page_is_classified(m15):
    assert sorted(s["no"] for s in m15["subs"]) == sorted(CAPTURE)


@pytest.mark.parametrize("no", sorted(CAPTURE, key=int))
def test_each_page_offers_its_capture(m15, no):
    sub = _sub(m15, no)
    if CAPTURE[no] == "form":
        assert sub["create"] or _opening(sub), "page %s has no + New and no form chip" % no
        for f in sub["forms"]:
            assert f["kind"] == "model_form", "chip %s opens %s" % (f["f"], f["kind"])
    else:
        assert not sub["create"] and not _opening(sub), "page %s lets a person type in %s" % (
            no,
            sub["model"],
        )
        assert all(lst["empty"] for lst in sub["lists"]), "page %s: say where rows come from" % no


def test_every_working_screen_sits_on_a_page(m15):
    """A list or report on no page cannot be reached from the register."""
    placed = {sid for s in m15["subs"] for sid in s["screens"]}
    orphans = [
        sid
        for sid in m15["nav"]
        if m15["screens"].get(sid, {}).get("kind") != "model_form" and sid not in placed
    ]
    assert not orphans, orphans


def test_location_hierarchy_adds_a_location(m15):
    sub = _sub(m15, "2")
    assert sub["create"] == "M41-form-stock-location"
    assert _opening(sub)["Stock Location"]["model"] == "fix.stock.location"
    assert "M15-locations" in sub["screens"], "the page must list the locations it adds"
    assert m15["byModel"]["fix.stock.location"] == "M41-form-stock-location"


def test_ownership_segregation_changes_class_only_by_the_approved_document(m15):
    sub = _sub(m15, "3")
    assert sub["create"] == "M15-form-classchange"
    assert "M15-classchange" in sub["screens"], "the class change must be reachable to approve"
    assert _opening(sub)["Ownership-Class Change"]["model"] == "fix.stock.class.change"


def test_van_stock_sets_par_levels(m15):
    sub = _sub(m15, "6")
    assert sub["create"] == "M15-form-recon"
    assert _opening(sub)["Reorder Rule"]["model"] == "fix.reorder.rule"


def test_transfers_page_raises_a_return_to_vendor(m15):
    sub = _sub(m15, "12")
    forms = _opening(sub)
    assert forms["Return to Vendor"]["model"] == "fix.stock.rtv"
    assert forms["Scrap Order"]["model"] == "fix.stock.quarantine"
    assert forms["Transfer Request"]["model"] == "fix.stock.transfer"


def test_a_serial_is_never_typed_in(m15):
    """Name, part, location, quantity and status of a lot are guarded and a
    storekeeper holds no create right: a blank lot form could never save."""
    lots = m15["screens"]["M15-serials"]
    assert lots["create"] is False and lots["empty"]
    form = m15["screens"]["M15-form-lot"]
    assert form["create"] is False and form["pick"]
    # page 7's "+ New" is the recall, never a blank lot (pass 2)
    assert _sub(m15, "7")["create"] == "M15-form-recall"


def test_suspense_check_sits_with_valuation(m15):
    assert "M15-suspense" in _sub(m15, "8")["screens"]


# ------------------------------------------------ capture pass 2 (2026-11-19)
# Every page had a button after 13 Nov; these pages still could not record
# what the spec says a person records there.


def test_reservations_page_holds_stock_for_a_job(m15):
    """Page 4 offered nothing: a reservation was a number M41 wrote."""
    sub = _sub(m15, "4")
    assert sub["model"] == "fix.stock.reservation"
    assert sub["create"] == "M15-form-reservation"
    assert _opening(sub)["Stock Reservation"]["model"] == "fix.stock.reservation"
    assert "M15-reservations" in sub["screens"]
    assert m15["byModel"]["fix.stock.reservation"] == "M15-form-reservation"


def test_issue_page_raises_a_backorder(m15):
    sub = _sub(m15, "5")
    assert _opening(sub)["Backorder"]["model"] == "fix.stock.backorder"
    assert "M15-backorders" in sub["screens"]


def test_serial_page_declares_a_recall(m15):
    sub = _sub(m15, "7")
    assert _opening(sub)["Stock Recall"]["model"] == "fix.stock.recall"
    assert "M15-recalls" in sub["screens"]


def test_ownership_page_reconciles_a_brand_consignment(m15):
    sub = _sub(m15, "3")
    assert _opening(sub)["Consignment Statement"]["model"] == "fix.consignment.reconciliation"
    assert "M15-consignment" in sub["screens"]


def test_van_page_moves_stock_van_to_van(m15):
    """FR-INV-033: a transfer request between two vans."""
    assert _opening(_sub(m15, "6"))["Transfer Request"]["model"] == "fix.stock.transfer"


def test_issue_form_draws_the_jobs_reservation():
    js = (SRC / "a06" / "m15.js").read_text(encoding="utf-8")
    issue = js[js.index("'M15-form-issue'") : js.index("'M15-form-transfer'")]
    assert "reservation_id" in issue
