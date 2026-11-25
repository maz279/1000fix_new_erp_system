# M16 Procurement & Sourcing: every sub-module page offers the button that
# captures its record (audit 2026-11-13).
#
# Consolidation (3) and 3-Way Match (9) offered nothing. RFQ & Bidding (4) had
# no chip for the supplier bid or the award decision; Blanket Orders (6) and
# Expediting (7) no chip at all. GRN & Inspection (8) offered a "GRN" chip that
# created an M15 warehouse receipt with no purchase order (FR-PRO-026: the
# goods receipt is against a PO, which PO Goods Receipt does) and no chip for
# the inspection outcome; its RTV list refused "+ New" while its chip raised
# one. The Cross-Branch Consolidation report grouped requisitions BY branch,
# the opposite of FR-PRO-006, and no RFQ could buy for more than one.
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
CONTROLLER = ROOT / "controllers" / "a06" / "m16.py"
WRITABLE = ROOT / "controllers" / "a06" / "writable.py"

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
const mod = P03_MODULES.M16;
const S = P03_DATA_SCREENS;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M16', map);
  const forms = fregPanels('M16', mod, map).forms.map((f) => {
    const id = P03_FORM_CHIPS['M16:' + f];
    const cfg = S[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const lists = (map.screens || []).map((id) => ({ id, cfg: S[id] || {} }))
    .filter((x) => x.cfg.kind === 'model_list')
    .map((x) => ({ id: x.id, model: x.cfg.model, create: x.cfg.create !== false, empty: !!x.cfg.empty,
      domain: x.cfg.domain || [], actions: (x.cfg.actions || []).map((a) => a.m) }));
  return { no: s[0], model: map.model || null, domain: map.domain || [], create, forms, lists };
});
const cfgOf = (id) => S[id] || {};
const fields = (id) => (cfgOf(id).sections || []).flatMap((sec) => (sec.fields || []));
console.log(JSON.stringify({
  subs,
  moduleForms: mod.forms,
  consolForm: { model: cfgOf('M16-form-rfq-consol').model, fields: fields('M16-form-rfq-consol') },
  grnForm: { create: cfgOf('M16-form-grn').create, pick: !!cfgOf('M16-form-grn').pick },
  rowForms: P03_FORM_CHIPS['M16:__by_screen__'],
}));
"""

# How each page's record is captured: 'form' = a "+ New" or a chip that opens
# an in-workspace form; 'none' = a computed analysis, nothing is typed.
CAPTURE = {
    "1": "form",  # purchase requisition
    "2": "form",  # purchase requisition (approval is decided in the M63 inbox)
    "3": "form",  # consolidated RFQ over several branches' requisitions
    "4": "form",  # RFQ + supplier bid + award decision
    "5": "form",  # local / import PO, proforma, advance
    "6": "form",  # blanket agreement
    "7": "form",  # expediting case
    "8": "form",  # PO goods receipt + inspection outcome + RTV
    "9": "form",  # the vendor bill (M52's form): the match itself is computed
    "10": "none",  # spend and price history are computed from the orders
}


@pytest.fixture(scope="module")
def m16(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m16_capture")
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


def _sub(m16, no):
    return next(s for s in m16["subs"] if s["no"] == no)


def test_every_page_is_classified(m16):
    assert sorted(s["no"] for s in m16["subs"]) == sorted(CAPTURE)


@pytest.mark.parametrize("no", sorted(CAPTURE, key=int))
def test_each_page_offers_its_capture(m16, no):
    sub = _sub(m16, no)
    opening = [f for f in sub["forms"] if f["opens"]]
    if CAPTURE[no] == "none":
        assert sub["create"] is None and not opening
        return
    assert sub["create"] or opening, "page %s has no + New and no form chip" % no
    assert opening, "page %s has no form chip" % no
    for f in sub["forms"]:
        assert f["kind"] == "model_form", "chip %s opens %s" % (f["f"], f["kind"])


def test_consolidation_raises_one_rfq_over_several_requisitions(m16):
    sub = _sub(m16, "3")
    assert sub["create"]["screen"] == "M16-form-rfq-consol"
    assert ["state", "=", "approved"] in sub["domain"]
    assert ["purchase_order_id", "=", False] in sub["domain"]
    form = m16["consolForm"]
    assert form["model"] == "fix.procurement.rfq"
    by_name = {f["name"]: f for f in form["fields"]}
    assert not by_name["requisition_ids"].get("readonly")
    # the quantity is the requisitions' total, never typed
    assert by_name["qty"].get("readonly") is True
    assert "requisition_ids" in ast.literal_eval(_writable("fix.procurement.rfq"))


def test_rfq_page_records_bids_and_awards(m16):
    models = {f["model"] for f in _sub(m16, "4")["forms"]}
    assert {"fix.procurement.rfq", "fix.procurement.bid", "fix.procurement.award"} <= models


def test_goods_receipt_page_never_makes_a_po_less_warehouse_receipt(m16):
    sub = _sub(m16, "8")
    models = [f["model"] for f in sub["forms"]]
    assert "fix.stock.receipt" not in models
    assert {"fix.purchase.receipt", "fix.procurement.inspection", "fix.stock.rtv"} <= set(models)
    assert "GRN" not in m16["moduleForms"]
    grn_list = next(lst for lst in sub["lists"] if lst["id"] == "M16-grn")
    assert not grn_list["create"]
    assert m16["grnForm"] == {"create": False, "pick": True}


def test_rtv_list_and_chip_agree(m16):
    rtv = next(lst for lst in _sub(m16, "8")["lists"] if lst["id"] == "M16-rtv")
    assert rtv["create"] and rtv["empty"]
    assert {"action_submit", "action_mark_credited"} <= set(rtv["actions"])
    # approval and shipping are the warehouse controller's (M15)
    assert not {"action_approve", "action_ship"} & set(rtv["actions"])


def test_match_page_shows_the_bills_and_captures_the_bill(m16):
    sub = _sub(m16, "9")
    assert sub["create"]["screen"] == "M52-form-bill"
    assert sub["create"]["presets"] == {"bill_type": "po"}
    queue = next(lst for lst in sub["lists"] if lst["id"] == "M16-match-queue")
    assert queue["model"] == "fix.vendor.invoice"
    assert not queue["create"] and queue["empty"] and queue["actions"] == []
    assert m16["rowForms"]["M16-match-queue"] == "M52-form-bill"


def test_consolidation_report_groups_by_part_not_branch():
    tree = ast.parse(CONTROLLER.read_text(encoding="utf-8"))
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "consolidation")
    src = ast.get_source_segment(CONTROLLER.read_text(encoding="utf-8"), fn)
    assert "product_id" in src and '"approved"' in src and "purchase_order_id" in src


def _writable(model):
    tree = ast.parse(WRITABLE.read_text(encoding="utf-8"))
    table = next(
        n.value
        for n in tree.body
        if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "WRITABLE"
    )
    for key, value in zip(table.keys, table.values, strict=True):
        if ast.literal_eval(key) == model:
            return ast.unparse(value.args[0] if isinstance(value, ast.Call) else value)
    raise AssertionError("%s is not in the A06 write whitelist" % model)
