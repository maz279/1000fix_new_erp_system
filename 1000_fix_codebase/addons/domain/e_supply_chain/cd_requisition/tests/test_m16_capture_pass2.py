"""M16 second capture audit (19 Nov 2026): the records each sub-module page
captures carry what FR-PRO-001..038 asks of them.

Each test runs the user path (non-admin users made in the rolled-back
transaction, from the A06 control suite's fixture) and shows the refusal the
spec requires, then the proper path:

  A  requisition demand source, reference and budget (FR-PRO-001/002)
  B  approved-source list (FR-PRO-009)
  C  RFQ invitations and response deadline (FR-PRO-011/016)
  D  normalised bid terms and the quotation file (FR-PRO-012/013)
  E  PO payment terms and incoterm (FR-PRO-017)
  F  goods-receipt line condition and discrepancy (FR-PRO-026)
  G  service-entry confirmation (FR-PRO-037, BRU-PRO-19)
"""

from __future__ import annotations

import importlib.util
from datetime import date, timedelta
from pathlib import Path

import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

_spec = importlib.util.spec_from_file_location(
    "_m16_controls_for_pass2", Path(__file__).with_name("test_a06_m16_controls.py")
)
_ctl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ctl)

c = _ctl.c  # the A06 M16 fixture: users per role, active suppliers, products
GA, GB, GR = _ctl.GA, _ctl.GB, _ctl.GR
_user, _req, _rfq, _bid = _ctl._user, _ctl._req, _ctl._rfq, _ctl._bid
_approved_req, _sent_po, _bill = _ctl._approved_req, _ctl._sent_po, _ctl._bill

REFUSED = (UserError, ValidationError, AccessError)
SOON = date.today() + timedelta(days=7)


# ======================================================== A: demand source
def test_A01_requisition_records_where_its_demand_comes_from(c):
    req = _req(c)
    assert (req.demand_source, req.purchase_kind) == ("branch", "stock")
    job = _req(c, demand_source="job")
    with pytest.raises(UserError, match="source reference"):
        job.with_user(c.requester).action_submit()
    job.with_user(c.requester).write({"source_ref": "SO-2026-0042"})
    job.with_user(c.requester).action_submit()
    assert job.state == "submitted"


def test_A02_project_demand_names_its_budget(c):
    req = _req(c, demand_source="project", source_ref="PRJ-7")
    with pytest.raises(UserError, match="budget reference"):
        req.with_user(c.requester).action_submit()
    req.with_user(c.requester).write({"budget_ref": "CAPEX-2026-11"})
    req.with_user(c.requester).action_submit()
    assert req.state == "submitted"


def test_A03_converted_requisition_keeps_its_source(c):
    req = _approved_req(c)
    req.with_user(c.buyer).action_convert_to_po()
    with pytest.raises(UserError, match="part of the record"):
        req.with_user(c.requester).write({"demand_source": "it"})


# ========================================================= B: approved source
def _source(c, vendor=None, priority=1, user=None, **kw):
    vals = {
        "product_id": c.prod.id,
        "vendor_id": (vendor or c.vendor).id,
        "priority": priority,
        "agreed_price": 9500,
        "lead_time_days": 10,
    }
    vals.update(kw)
    return c.env["fix.procurement.approved.source"].with_user(user or c.buyer).create(vals)


def test_B01_only_a_buyer_proposes_a_source(c):
    with pytest.raises(REFUSED):
        _source(c, user=c.clerk2)
    src = _source(c)
    assert src.state == "draft" and src.name.startswith("APSRC/")


def test_B02_a_second_approver_approves_then_terms_are_fixed(c):
    src = _source(c)
    with pytest.raises(REFUSED):
        src.with_user(c.buyer).action_approve()
    both = _user(c.env, "a06m16p2_buyer_appr", [GB, GA])
    own = _source(c, vendor=c.vendor4, user=both)
    with pytest.raises(UserError, match="Segregation"):
        own.with_user(both).action_approve()
    src.with_user(c.papprover).action_approve()
    assert src.state == "approved" and src.approved_by_id == c.papprover
    with pytest.raises(UserError, match="fixed"):
        src.with_user(c.buyer).write({"agreed_price": 1})
    with pytest.raises(UserError, match="why"):
        src.with_user(c.buyer).action_withdraw(reason=" ")
    src.with_user(c.buyer).action_withdraw(reason="supplier exited the category")
    assert src.state == "withdrawn"


def test_B03_inactive_supplier_and_twin_source_refused(c):
    unreg = _source(c, vendor=c.vendor3)
    with pytest.raises(UserError, match="BRU-PRO-02"):
        unreg.with_user(c.papprover).action_approve()
    first = _source(c)
    first.with_user(c.papprover).action_approve()
    twin = _source(c, priority=2)
    with pytest.raises(UserError, match="already an approved source"):
        twin.with_user(c.papprover).action_approve()


def test_B04_requisition_without_vendor_buys_from_first_source(c):
    second = _source(c, vendor=c.vendor4, priority=2)
    first = _source(c, vendor=c.vendor5, priority=1)
    (second | first).with_user(c.papprover).action_approve()
    req = _approved_req(c, vendor_id=False)
    # filled in at submission, so the approver decided it with its vendor
    assert req.vendor_id == c.vendor5
    req.with_user(c.buyer).action_convert_to_po()
    assert req.purchase_order_id.vendor_id == c.vendor5


# ============================================================ C: RFQ invitations
def test_C01_rfq_opens_only_with_invitations_and_a_deadline(c):
    bare = _rfq(c, open_=False, invited_vendor_ids=[], response_deadline=False)
    with pytest.raises(UserError, match="invites no supplier"):
        bare.with_user(c.buyer).action_open()
    bare.with_user(c.buyer).write({"invited_vendor_ids": [(4, c.vendor.id)]})
    with pytest.raises(UserError, match="deadline"):
        bare.with_user(c.buyer).action_open()
    bare.with_user(c.buyer).write({"response_deadline": date.today() - timedelta(days=1)})
    with pytest.raises(UserError, match="passed"):
        bare.with_user(c.buyer).action_open()
    bare.with_user(c.buyer).write({"response_deadline": SOON})
    bare.with_user(c.buyer).action_open()
    assert bare.state == "open"


def test_C02_only_an_invited_supplier_bids(c):
    r = _rfq(c, invited_vendor_ids=[(6, 0, c.vendor.ids)])
    with pytest.raises(UserError, match="not invited"):
        c.env["fix.procurement.bid"].with_user(c.buyer).create(
            {"rfq_id": r.id, "vendor_id": c.vendor4.id, "unit_price": 900}
        )
    r.with_user(c.buyer).write({"invited_vendor_ids": [(4, c.vendor4.id)]})
    bid = (
        c.env["fix.procurement.bid"]
        .with_user(c.buyer)
        .create({"rfq_id": r.id, "vendor_id": c.vendor4.id, "unit_price": 900})
    )
    assert bid.state == "received"


def test_C03_invitations_never_withdrawn_deadline_only_extended(c):
    r = _rfq(c)
    with pytest.raises(UserError, match="cannot be withdrawn"):
        r.with_user(c.buyer).write({"invited_vendor_ids": [(3, c.vendor4.id)]})
    with pytest.raises(UserError, match="extended"):
        r.with_user(c.buyer).write({"response_deadline": date.today()})
    with pytest.raises(UserError, match="extended"):
        r.with_user(c.buyer).write({"response_deadline": False})
    r.with_user(c.buyer).write({"response_deadline": SOON + timedelta(days=7)})
    _bid(c, r, c.vendor, 1000)
    r.with_user(c.buyer).action_close()
    with pytest.raises(UserError, match="event record"):
        r.with_user(c.buyer).write({"invited_vendor_ids": [(4, c.vendor3.id)]})


def test_C04_no_bid_after_the_deadline(c):
    r = _rfq(c)
    r.sudo()._guarded().write({"response_deadline": date.today() - timedelta(days=1)})
    with pytest.raises(UserError, match="deadline"):
        c.env["fix.procurement.bid"].with_user(c.buyer).create(
            {"rfq_id": r.id, "vendor_id": c.vendor.id, "unit_price": 900}
        )


def test_C05_invite_approved_sources(c):
    r = _rfq(c, open_=False, invited_vendor_ids=[])
    with pytest.raises(UserError, match="no approved source"):
        r.with_user(c.buyer).action_invite_approved_sources()
    src = _source(c, vendor=c.vendor4)
    src.with_user(c.papprover).action_approve()
    r.with_user(c.buyer).action_invite_approved_sources()
    assert r.invited_vendor_ids == c.vendor4
    r.with_user(c.buyer).action_open()
    assert r.state == "open"


# ================================================================ D: bid terms
def test_D01_bid_terms_compare_and_are_sealed_with_the_price(c):
    r = _rfq(c, qty=10)
    bid = _bid(
        c,
        r,
        c.vendor,
        1000,
        warranty_months=12,
        moq=5,
        payment_terms="30 days after delivery",
        incoterm="dap",
    )
    assert bid.total_price == pytest.approx(10000)
    _bid(c, r, c.vendor4, 1100)
    r.with_user(c.buyer).action_close()
    for vals in ({"warranty_months": 24}, {"incoterm": "exw"}, {"payment_terms": "advance"}):
        with pytest.raises(UserError, match="sealed"):
            bid.with_user(c.buyer).write(vals)


# ================================================================ E: PO terms
def test_E01_award_po_carries_the_bid_terms_and_they_are_pinned(c):
    r = _rfq(c)
    vendors = [c.vendor, c.vendor4, c.vendor5]
    bids = [
        _bid(c, r, v, p, payment_terms="45 days", incoterm="ddp")
        for v, p in zip(vendors, [1000, 1100, 1200], strict=True)
    ]
    r.with_user(c.buyer).action_close()
    award = (
        c.env["fix.procurement.award"]
        .with_user(c.buyer)
        .create({"rfq_id": r.id, "bid_id": bids[0].id})
    )
    award.with_user(c.buyer).action_create_po()
    po = award.purchase_order_id
    assert (po.payment_terms, po.incoterm) == ("45 days", "ddp")


def test_E02_sent_po_terms_fixed_and_carried_to_change_order(c):
    po = _sent_po(c)
    with pytest.raises(UserError, match="change order"):
        po.with_user(c.buyer).write({"payment_terms": "advance"})
    po.sudo()._guarded().write({"payment_terms": "30 days", "incoterm": "dap"})
    result = po.with_user(c.buyer).action_create_change_order()
    new = c.env["fix.purchase.order"].browse(result["change_order_ids"])
    assert (new.payment_terms, new.incoterm) == ("30 days", "dap")


# ======================================================== F: receipt condition
def test_F01_a_damaged_line_needs_its_discrepancy(c):
    po = _sent_po(c)
    receipt = (
        c.env["fix.purchase.receipt"].with_user(c.receiver).create({"purchase_order_id": po.id})
    )
    line = receipt.line_ids[:1]
    assert line.condition == "good"
    line.with_user(c.receiver).write({"condition": "damaged"})
    with pytest.raises(UserError, match="discrepancy"):
        receipt.with_user(c.receiver).action_post()
    line.with_user(c.receiver).write({"discrepancy_note": "carton crushed, 1 unit dented"})
    receipt.with_user(c.receiver).action_post()
    assert receipt.state == "posted"


# ========================================================== G: service entry
@pytest.fixture
def svc(c):
    product = c.env["product.product"].create(
        {"name": "A06M16P2 AC duct cleaning", "type": "service"}
    )
    po = _sent_po(c, product_id=product.id, purchase_kind="service")
    return product, po


def _entry(c, po, qty=2, user=None, **kw):
    vals = {
        "purchase_order_id": po.id,
        "po_line_id": po.line_ids[:1].id,
        "qty_confirmed": qty,
        "service_period": "Nov 2026",
        "description": "Ducts of 2 branches cleaned, job sheets signed",
    }
    vals.update(kw)
    return c.env["fix.purchase.service.entry"].with_user(user or c.requester).create(vals)


def test_G01_a_service_has_no_goods_receipt(c, svc):
    _product, po = svc
    line = po.line_ids[:1]
    with pytest.raises(UserError, match="BRU-PRO-19"):
        po.with_user(c.receiver).action_record_receipt({line.id: 2})


def test_G02_the_requester_confirms_never_the_buyer_and_the_bill_matches(c, svc):
    product, po = svc
    entry = _entry(c, po)
    assert entry.name.startswith("SRVE/")
    with pytest.raises(UserError, match="SOD-02"):
        entry.with_user(c.buyer).action_confirm()
    with pytest.raises(UserError, match="requester"):
        entry.with_user(c.clerk2).action_confirm()
    entry.with_user(c.requester).action_confirm()
    assert entry.state == "confirmed" and entry.receipt_id.state == "posted"
    assert entry.receipt_id.receiver_id == c.requester
    line = po.line_ids[:1]
    assert (line.qty_received, line.qty_accepted) == (2, 2)
    assert po.state == "received"
    inv = _bill(c, po, 2, 10000, "A06M16P2-G02", product=product)
    assert inv.match_state == "matched", inv.match_detail
    with pytest.raises(UserError, match="final"):
        entry.with_user(c.requester).write({"qty_confirmed": 1})


def test_G03_stock_goods_are_not_confirmed_by_a_service_entry(c):
    po = _sent_po(c)
    with pytest.raises(ValidationError, match="stock goods"):
        _entry(c, po)


def test_G04_over_confirmation_and_missing_evidence_refused(c, svc):
    _product, po = svc
    over = _entry(c, po, qty=5)
    with pytest.raises(UserError, match="already confirmed"):
        over.with_user(c.requester).action_confirm()
    bare = _entry(c, po, description=False)
    with pytest.raises(UserError, match="evidence"):
        bare.with_user(c.requester).action_confirm()
