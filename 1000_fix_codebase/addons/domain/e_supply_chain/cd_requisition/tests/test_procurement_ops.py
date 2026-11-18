"""cd_requisition procurement-ops behaviour (live ORM, rolled back): the M16
workspace documents — requisition conversion, RFQ/bid/award, blanket
consumption, expediting and inspection outcomes.

A06 audit (2026-11-03): these tests converted requisitions created already
'approved', awarded on a closed RFQ whose bids were typed in afterwards,
counted every PO of the vendor as blanket consumption and confirmed
inspections with a typed outcome and no receipt - the defects themselves.
They run as the system, so the approvals and supplier activation are seeded
the way their workflows leave them; the attacks are in test_a06_m16_controls.py.
"""

from __future__ import annotations

import uuid
from datetime import date

import pytest
from odoo.exceptions import UserError

TAG = uuid.uuid4().hex[:6].upper()


def _active(env, partner):
    sup = env["fix.supplier"].create(
        {"name": partner.name, "partner_id": partner.id, "status": "active"}
    )
    for doc_type in ("trade_licence", "tin", "vat"):
        env["fix.supplier.document"].create(
            {"supplier_id": sup.id, "doc_type": doc_type, "state": "valid"}
        )
    return sup


@pytest.fixture
def ctx(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    vendor, vendor2, vendor3 = env["res.partner"].create(
        [
            {"name": f"Ops Vendor {TAG}"},
            {"name": f"Ops Vendor B {TAG}"},
            {"name": f"Ops Vendor C {TAG}"},
        ]
    )
    for partner in (vendor, vendor2, vendor3):
        _active(env, partner)
    product = env["product.product"].create({"name": f"Ops Product {TAG}"})
    employee = env["hr.employee"].create({"name": f"Ops Buyer {TAG}"})
    return {
        "env": env,
        "ou": ou,
        "vendor": vendor,
        "vendor2": vendor2,
        "vendor3": vendor3,
        "product": product,
        "employee": employee,
    }


def _stamp(record):
    """What the M63 engine leaves on an approved record."""
    record._guarded().write(
        {
            "approval_state": "approved",
            "dofa_approved": True,
            "dofa_approved_tier": record._dofa_current_tier(),
            "dofa_approved_amount": record._dofa_amount(),
        }
    )
    return record


def _requisition(ctx, approved=True, **vals):
    defaults = {
        "description": f"Ops requisition {TAG}",
        "product_id": ctx["product"].id,
        "qty": 4,
        "vendor_id": ctx["vendor"].id,
        "estimate_amount": 20000,
        "cost_centre": "CC-OPS",
        "required_by": "2099-01-01",
        "urgency": "normal",
        "requested_by": ctx["employee"].id,
        "operating_unit_id": ctx["ou"].id,
    }
    defaults.update(vals)
    req = ctx["env"]["fix.requisition"].create(defaults)
    if approved:
        req._guarded().write({"state": "approved"})
        _stamp(req)
    return req


def _invite(ctx):
    """FR-PRO-011: the suppliers an RFQ asks to quote, and its deadline."""
    return {
        "invited_vendor_ids": [(6, 0, (ctx["vendor"] | ctx["vendor2"] | ctx["vendor3"]).ids)],
        "response_deadline": "2099-01-01",
    }


def _sent_po(ctx, price=1000.0, qty=2.0, **vals):
    env = ctx["env"]
    po = env["fix.purchase.order"].create(
        {
            "operating_unit_id": ctx["ou"].id,
            "vendor_id": ctx["vendor"].id,
            "line_ids": [
                (0, 0, {"product_id": ctx["product"].id, "qty_ordered": qty, "unit_price": price})
            ],
            **vals,
        }
    )
    po.action_record_requisition_exception(reason="ops test without requisition")
    _stamp(po)
    po.action_send()
    return po


def test_requisition_conversion_creates_po_with_link(ctx):
    env = ctx["env"]
    req = _requisition(ctx)
    req.action_convert_to_po()
    assert req.state == "converted"
    po = req.purchase_order_id
    assert po and po.vendor_id == ctx["vendor"]
    assert po.line_ids.product_id == ctx["product"]
    assert po.line_ids.unit_price == pytest.approx(5000.0)
    assert po.requisition_id == req and po.state == "draft" and po.approval_state == "none"
    # a converted requisition holds its PO: even if re-approved, converting
    # again would create a second PO for the same demand
    req._guarded().write({"state": "approved"})
    with pytest.raises(UserError, match="already converted"), env.cr.savepoint():
        req.action_convert_to_po()


def test_requisition_conversion_needs_approval_and_vendor(ctx):
    env = ctx["env"]
    draft = _requisition(ctx, approved=False, description=f"Draft {TAG}")
    with pytest.raises(UserError, match="approved"), env.cr.savepoint():
        draft.action_convert_to_po()
    no_vendor = _requisition(ctx, description=f"No vendor {TAG}", vendor_id=False)
    with pytest.raises(UserError, match="vendor"), env.cr.savepoint():
        no_vendor.action_convert_to_po()


def test_rfq_open_close_and_close_needs_bid(ctx):
    env = ctx["env"]
    rfq = env["fix.procurement.rfq"].create(
        {"description": f"RFQ {TAG}", "product_id": ctx["product"].id, "qty": 5, **_invite(ctx)}
    )
    assert rfq.name.startswith("RFQ/")
    rfq.action_open()
    with pytest.raises(UserError, match="at least one bid"), env.cr.savepoint():
        rfq.action_close()
    env["fix.procurement.bid"].create(
        {"rfq_id": rfq.id, "vendor_id": ctx["vendor"].id, "unit_price": 100}
    )
    rfq.action_close()
    assert rfq.state == "closed" and rfq.closed_at


def test_award_marks_winner_and_losers(ctx):
    env = ctx["env"]
    rfq = env["fix.procurement.rfq"].create(
        {"description": f"Award {TAG}", "product_id": ctx["product"].id, "qty": 2, **_invite(ctx)}
    )
    rfq.action_open()
    Bid = env["fix.procurement.bid"]
    first = Bid.create({"rfq_id": rfq.id, "vendor_id": ctx["vendor"].id, "unit_price": 120})
    second = Bid.create({"rfq_id": rfq.id, "vendor_id": ctx["vendor2"].id, "unit_price": 100})
    third = Bid.create({"rfq_id": rfq.id, "vendor_id": ctx["vendor3"].id, "unit_price": 130})
    rfq.action_close()
    award = env["fix.procurement.award"].create({"rfq_id": rfq.id, "bid_id": second.id})
    assert award.name.startswith("AWRD/")
    assert (award.state, award.is_lowest, award.compliant_bid_count) == ("decided", True, 3)
    assert second.state == "awarded"
    assert first.state == "lost" and third.state == "lost"
    assert rfq.state == "awarded"


def test_blanket_consumed_counts_linked_call_offs(ctx):
    env = ctx["env"]
    blanket = env["fix.procurement.blanket"].create(
        {
            "vendor_id": ctx["vendor"].id,
            "valid_from": date(2026, 1, 1),
            "valid_to": date(2026, 12, 31),
            "cap_amount": 10000,
        }
    )
    assert blanket.state == "draft"
    blanket.action_activate()
    unlinked = _sent_po(ctx, price=1000, qty=2)
    po = _sent_po(ctx, price=1000, qty=2, blanket_id=blanket.id)
    assert unlinked.amount_total == po.amount_total == pytest.approx(2000.0)
    blanket.invalidate_recordset()
    assert blanket.consumed_amount == pytest.approx(2000.0)
    assert blanket.remaining_amount == pytest.approx(8000.0)


def test_expedite_chase_then_resolve(ctx):
    env = ctx["env"]
    po = env["fix.purchase.order"].create(
        {"operating_unit_id": ctx["ou"].id, "vendor_id": ctx["vendor"].id}
    )
    case = env["fix.procurement.expedite"].create({"purchase_order_id": po.id, "reason": "late"})
    assert case.name.startswith("EXPD/")
    case.action_chase()
    assert case.state == "chased"
    assert case.follow_up_date
    case.action_resolve(note="vendor dispatched")
    assert case.state == "resolved"
    with pytest.raises(UserError, match="already resolved"), env.cr.savepoint():
        case.action_resolve(note="again")


def test_inspection_rejected_and_confirm(ctx):
    env = ctx["env"]
    po = _sent_po(ctx, price=1000, qty=5)
    po.action_record_receipt({po.line_ids.id: 5})
    line = po.receipt_ids.line_ids
    assert line.inspection_state == "pending" and line.qty_accepted == 0
    insp = env["fix.procurement.inspection"].create({"receipt_line_id": line.id, "qty_accepted": 4})
    assert insp.name.startswith("INSP/")
    assert (insp.product_id, insp.qty_received, insp.receipt_ref) == (
        ctx["product"],
        5.0,
        line.receipt_id.name,
    )
    assert insp.qty_rejected == pytest.approx(1.0) and insp.outcome == "partial"
    insp.action_confirm()
    assert insp.state == "done"
    assert (line.qty_accepted, line.inspection_state) == (4.0, "partial")
    assert po.line_ids.qty_accepted == 4.0
    with pytest.raises(UserError, match="draft"), env.cr.savepoint():
        insp.action_confirm()


def test_po_promised_and_received_dates(ctx):
    env = ctx["env"]
    po = env["fix.purchase.order"].create(
        {
            "operating_unit_id": ctx["ou"].id,
            "vendor_id": ctx["vendor"].id,
            "promised_date": date(2026, 10, 20),
            "received_on": date(2026, 10, 18),
        }
    )
    assert po.received_on <= po.promised_date


# ---- FR-PRO-006: cross-branch consolidation (M16 capture audit, 13 Nov 2026)
def _branches(ctx):
    env = ctx["env"]
    # one legal entity per company (M65 fix_entity_company_unique): reuse it
    entity = env["fix.entity"].search([("company_id", "=", env.company.id)], limit=1) or env[
        "fix.entity"
    ].create(
        {"code": f"CN{TAG}", "legal_name": f"Consolidation {TAG}", "company_id": env.company.id}
    )
    return env["fix.branch"].create(
        [
            {
                "name": f"Consol North {TAG}",
                "code": f"CN1{TAG}",
                "entity_id": entity.id,
                "operating_unit_id": ctx["ou"].id,
            },
            {
                "name": f"Consol South {TAG}",
                "code": f"CS1{TAG}",
                "entity_id": entity.id,
                "operating_unit_id": ctx["ou"].id,
            },
        ]
    )


def _consolidated_rfq(ctx, reqs, **vals):
    return ctx["env"]["fix.procurement.rfq"].create(
        {
            "description": f"Consolidated {TAG}",
            "product_id": ctx["product"].id,
            "requisition_ids": [(6, 0, reqs.ids)],
            **_invite(ctx),
            **vals,
        }
    )


def test_consolidated_rfq_buys_the_branches_total(ctx):
    north, south = _branches(ctx)
    a = _requisition(ctx, description=f"North {TAG}", branch_id=north.id, qty=4)
    b = _requisition(ctx, description=f"South {TAG}", branch_id=south.id, qty=6)
    rfq = _consolidated_rfq(ctx, a | b, qty=1)
    # the typed quantity gives way to the requisitions' total
    assert rfq.qty == pytest.approx(10.0)
    assert rfq.requisition_ids == a | b


def test_consolidated_award_raises_one_po_with_a_line_per_branch(ctx):
    env = ctx["env"]
    north, south = _branches(ctx)
    a = _requisition(ctx, description=f"North {TAG}", branch_id=north.id, qty=4)
    b = _requisition(ctx, description=f"South {TAG}", branch_id=south.id, qty=6)
    rfq = _consolidated_rfq(ctx, a | b)
    rfq.action_open()
    Bid = env["fix.procurement.bid"]
    win = Bid.create({"rfq_id": rfq.id, "vendor_id": ctx["vendor"].id, "unit_price": 90})
    Bid.create({"rfq_id": rfq.id, "vendor_id": ctx["vendor2"].id, "unit_price": 100})
    Bid.create({"rfq_id": rfq.id, "vendor_id": ctx["vendor3"].id, "unit_price": 110})
    rfq.action_close()
    award = env["fix.procurement.award"].create({"rfq_id": rfq.id, "bid_id": win.id})
    assert award.state == "decided"
    award.action_create_po()
    po = award.purchase_order_id
    assert a.state == b.state == "converted"
    assert a.purchase_order_id == b.purchase_order_id == po
    assert po.requisition_id in (a | b)
    assert not po.branch_id  # two branches: each keeps its own line
    assert sorted(po.line_ids.mapped("qty_ordered")) == [4.0, 6.0]
    assert set(po.line_ids.mapped("unit_price")) == {90.0}
    assert any(north.name in d for d in po.line_ids.mapped("description"))
    assert any(south.name in d for d in po.line_ids.mapped("description"))


def test_consolidation_refuses_what_it_cannot_buy(ctx):
    env = ctx["env"]
    north, south = _branches(ctx)
    draft = _requisition(ctx, approved=False, description=f"Draft {TAG}", branch_id=north.id)
    with pytest.raises(UserError, match="only approved"), env.cr.savepoint():
        _consolidated_rfq(ctx, draft)
    other_part = env["product.product"].create({"name": f"Other part {TAG}"})
    wrong = _requisition(ctx, description=f"Wrong part {TAG}", product_id=other_part.id)
    with pytest.raises(UserError, match="buys one part"), env.cr.savepoint():
        _consolidated_rfq(ctx, wrong)
    a = _requisition(ctx, description=f"North {TAG}", branch_id=north.id)
    b = _requisition(ctx, description=f"South {TAG}", branch_id=south.id)
    first = _consolidated_rfq(ctx, a | b)
    # out to tender once: neither a second RFQ nor a direct PO
    with pytest.raises(UserError, match="already sourcing"), env.cr.savepoint():
        _consolidated_rfq(ctx, b)
    with pytest.raises(UserError, match="being sourced"), env.cr.savepoint():
        a.action_convert_to_po()
    first.action_open()
    with pytest.raises(UserError, match="fixed once bids are invited"), env.cr.savepoint():
        first.write({"requisition_ids": [(6, 0, a.ids)]})
