# M16 Procurement & Sourcing, capture audit pass 2 (19 Nov 2026).
#
# Pass 1 (13 Nov) gave every sub-module page a button. Read against the spec,
# several of those buttons captured records without what the requirement is
# about, and some records the spec names had no capture at all:
#   page 1/2  the requisition never said where its demand came from (FR-PRO-001)
#   page 4    no approved-source list (FR-PRO-009); an RFQ invited nobody and had
#             no deadline (FR-PRO-011); a bid was a price and a lead time only
#             (FR-PRO-012/013)
#   page 5    a PO had no payment terms or incoterm (FR-PRO-017)
#   page 6    an active blanket offered no call-off (FR-PRO-019)
#   page 8    a receipt line had no condition (FR-PRO-026); a service had no
#             service entry (FR-PRO-037, BRU-PRO-19)
#   page 9    no exception case or tolerance band (FR-PRO-030, BRU-PRO-09)
#
# Evaluated as the browser evaluates it (node runs the engine's own
# fregCreate / fregPanels over the real registry), plus the model check that
# every field a form offers exists and no form omits a required field.
from __future__ import annotations

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

_spec = importlib.util.spec_from_file_location(
    "_estate_pages_m16p2", HERE / "test_estate_module_pages.py"
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
  const forms = fregPanels('M16', mod, map).forms.map((f) => {
    const id = P03_FORM_CHIPS['M16:' + f];
    const cfg = S[id] || {};
    return { f, id: id || null, model: cfg.model || null, opens: cfg.kind === 'model_form' && cfg.create !== false };
  });
  return { no: s[0], screens: map.screens || [], create: fregCreate('M16', map), forms };
});
const screens = {};
for (const [id, cfg] of Object.entries(S)) {
  if (!id.startsWith('M16-') && !['M52-form-matchcase', 'M52-form-tolerance', 'M52-form-bill'].includes(id)) continue;
  screens[id] = {
    kind: cfg.kind, model: cfg.model || null, cols: cfg.cols || [], tabs: (cfg.tabs || []).map((t) => t.id),
    actions: (cfg.actions || []).map((a) => ({ m: a.m, form: a.form || null, prefill: a.prefill || null, carry: a.carry || null, states: a.states || null })),
    fields: (cfg.sections || []).flatMap((sec) => (sec.fields || []).map((f) => ({ ...f, tab: sec.tab || null }))),
    lines: cfg.lines ? { field: cfg.lines.field, fields: cfg.lines.fields.map((f) => f.name) } : null,
  };
}
const nav = mod.groups.flatMap((g) => g.screens.map((x) => x.id));
console.log(JSON.stringify({ subs, screens, nav, byScreen: P03_FORM_CHIPS['M16:__by_screen__'] }));
"""


@pytest.fixture(scope="module")
def reg(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m16_pass2")
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


def _sub(reg, no):
    return next(s for s in reg["subs"] if s["no"] == no)


def _fields(reg, screen):
    return {f["name"]: f for f in reg["screens"][screen]["fields"]}


def _chips(reg, no):
    return {f["f"]: f for f in _sub(reg, no)["forms"]}


# ------------------------------------------------------------- page by page
def test_p1_requisition_form_captures_the_demand_source_on_tabs(reg):
    fields = _fields(reg, "M16-form-requisition")
    for name in ("demand_source", "source_ref", "budget_ref", "purchase_kind"):
        assert name in fields, name
    assert fields["demand_source"]["required"] and fields["purchase_kind"]["required"]
    # >15 fields: the multi-tab form standard
    assert len(fields) > 15 and reg["screens"]["M16-form-requisition"]["tabs"]
    assert all(f["tab"] for f in fields.values())
    assert "demand_source" in reg["screens"]["M16-prs"]["cols"]


def test_p4_offers_the_approved_source_and_rfq_invitations(reg):
    chips = _chips(reg, "4")
    src = chips["Approved Source"]
    assert src["id"] == "M16-form-source" and src["opens"]
    assert src["model"] == "fix.procurement.approved.source"
    assert "M16-sources" in _sub(reg, "4")["screens"] and "M16-sources" in reg["nav"]
    assert reg["byScreen"]["M16-sources"] == "M16-form-source"
    actions = {a["m"] for a in reg["screens"]["M16-sources"]["actions"]}
    assert {"action_approve", "action_withdraw"} <= actions
    for form in ("M16-form-rfq", "M16-form-rfq-consol"):
        fields = _fields(reg, form)
        assert fields["invited_vendor_ids"]["required"], form
        assert fields["response_deadline"]["required"], form
    rfq_actions = {a["m"] for a in reg["screens"]["M16-rfqs"]["actions"]}
    assert "action_invite_approved_sources" in rfq_actions


def test_p4_bids_compare_on_more_than_price(reg):
    fields = _fields(reg, "M16-form-bid")
    for name in ("warranty_months", "moq", "payment_terms", "incoterm", "quote_file"):
        assert name in fields, name
    assert fields["quote_file"]["type"] == "binary"
    cols = reg["screens"]["M16-compare"]["cols"]
    for name in ("total_price", "warranty_months", "moq", "payment_terms", "incoterm"):
        assert name in cols, name


def test_p5_purchase_orders_carry_payment_terms_and_incoterm(reg):
    for form in ("M16-form-po", "M16-form-po-import"):
        fields = _fields(reg, form)
        assert {"payment_terms", "incoterm"} <= set(fields), form
    assert _fields(reg, "M16-form-po-import")["incoterm"]["required"]


def test_p6_an_active_blanket_raises_a_call_off(reg):
    call_off = next(a for a in reg["screens"]["M16-blanket"]["actions"] if a["m"] == "__call_off")
    assert call_off["form"] == "M16-form-po" and call_off["prefill"] == "blanket_id"
    assert call_off["carry"] == {"vendor_id": "vendor_id"} and call_off["states"] == ["active"]
    assert "vendor_id" in reg["screens"]["M16-blanket"]["cols"]
    assert "blanket_id" in _fields(reg, "M16-form-po")


def test_p8_receipt_condition_and_service_entry(reg):
    assert {"condition", "discrepancy_note"} <= set(
        reg["screens"]["M16-form-po-receipt"]["lines"]["fields"]
    )
    chip = _chips(reg, "8")["Service Entry"]
    assert chip["id"] == "M16-form-service-entry" and chip["opens"]
    assert chip["model"] == "fix.purchase.service.entry"
    assert "M16-service-entries" in _sub(reg, "8")["screens"]
    assert reg["byScreen"]["M16-service-entries"] == "M16-form-service-entry"
    fields = _fields(reg, "M16-form-service-entry")
    assert fields["evidence_file"]["type"] == "binary"
    assert {"purchase_order_id", "po_line_id", "qty_confirmed"} <= {
        n for n, f in fields.items() if f.get("required")
    }


def test_p9_exception_case_and_tolerance_are_captured_on_m52s_forms(reg):
    chips = _chips(reg, "9")
    assert chips["Match Exception Case"]["id"] == "M52-form-matchcase"
    assert chips["Match Tolerance"]["id"] == "M52-form-tolerance"
    assert all(
        chips[f]["opens"] for f in ("Match Exception Case", "Match Tolerance", "Vendor Bill")
    )
    assert "M16-match-cases" in _sub(reg, "9")["screens"]
    assert reg["byScreen"]["M16-match-cases"] == "M52-form-matchcase"


def test_every_page_but_spend_still_captures(reg):
    for sub in reg["subs"]:
        opens = [f for f in sub["forms"] if f["opens"]]
        if sub["no"] == "10":
            assert not opens and not sub["create"]
        else:
            assert opens, sub["no"]


def test_engine_carries_row_columns_onto_the_new_form():
    engine = (SRC / "p03_workspace.js").read_text(encoding="utf-8")
    body = engine[engine.index("async mlAction(method, label)") :][:2500]
    assert "cfg.carry" in body and "Object.keys(presets).length" in body


# --------------------------------------------------------- server agreement
def test_surfaces_and_writable_follow_the_forms():
    spec = importlib.util.spec_from_file_location(
        "_m16_ctl", ROOT / "controllers" / "a06" / "m16.py"
    )
    ctl = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ctl)
    s = ctl.SURFACES
    assert {"action_approve", "action_withdraw"} <= s["fix.procurement.approved.source"]["actions"]
    assert {"action_confirm", "action_cancel"} <= s["fix.purchase.service.entry"]["actions"]
    assert "action_invite_approved_sources" in s["fix.procurement.rfq"]["actions"]
    spec = importlib.util.spec_from_file_location(
        "_a06_w", ROOT / "controllers" / "a06" / "writable.py"
    )
    w = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(w)
    W = w.WRITABLE
    assert {"invited_vendor_ids", "response_deadline"} <= W["fix.procurement.rfq"]
    assert {"warranty_months", "moq", "payment_terms", "incoterm", "quote_file"} <= W[
        "fix.procurement.bid"
    ]
    assert {"payment_terms", "incoterm"} <= W["fix.purchase.order"]
    assert {"demand_source", "source_ref", "budget_ref", "purchase_kind"} <= W["fix.requisition"]
    assert "qty_confirmed" in W["fix.purchase.service.entry"]
    assert "agreed_price" in W["fix.procurement.approved.source"]


# required fields a form need not offer: create() derives them from another
# field the form does offer
DERIVED = {
    ("fix.procurement.inspection", "product_id"),  # from the receipt line
}
MAGIC = {"id", "create_uid", "create_date", "write_uid", "write_date"}


def test_every_m16_form_field_exists_and_required_fields_are_offered(reg, odoo_env):
    env = odoo_env
    gaps = []
    for sid, cfg in reg["screens"].items():
        if cfg["kind"] != "model_form" or not sid.startswith("M16-") or cfg["model"] not in env:
            continue
        model = env[cfg["model"]]
        offered = {f["name"] for f in cfg["fields"]}
        missing = offered - set(model._fields)
        if missing:
            gaps.append((sid, "unknown field", sorted(missing)))
        if sid == "M16-form-grn":
            continue  # read-only here: raised by posting a PO goods receipt
        defaults = model.default_get(list(model._fields))
        computed = {n for n, f in model._fields.items() if f.compute or f.related}
        skip = MAGIC | {"name"} | {n for m, n in DERIVED if m == cfg["model"]}
        if cfg["lines"]:
            skip.add(cfg["lines"]["field"])
        needed = {
            n
            for n, f in model._fields.items()
            if f.required and n not in defaults and n not in computed and n not in skip
        }
        if needed - offered:
            gaps.append((sid, "required not offered", sorted(needed - offered)))
    assert not gaps, gaps
