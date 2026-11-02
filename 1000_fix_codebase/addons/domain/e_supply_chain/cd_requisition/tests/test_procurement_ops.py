"""cd_requisition procurement-ops behaviour (live ORM, rolled back): the M16
workspace documents — requisition conversion, RFQ/bid/award, blanket
consumption, expediting and inspection outcomes."""

from __future__ import annotations

import uuid
from datetime import date

import pytest
from odoo.exceptions import UserError

TAG = uuid.uuid4().hex[:6].upper()


@pytest.fixture
def ctx(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    vendor = env["res.partner"].create({"name": f"Ops Vendor {TAG}"})
    product = env["product.product"].create({"name": f"Ops Product {TAG}"})
    employee = env["hr.employee"].create({"name": f"Ops Buyer {TAG}"})
    return {"env": env, "ou": ou, "vendor": vendor, "product": product, "employee": employee}


def _requisition(ctx, **vals):
    defaults = {
        "description": f"Ops requisition {TAG}",
        "product_id": ctx["product"].id,
        "qty": 4,
        "vendor_id": ctx["vendor"].id,
        "estimate_amount": 20000,
        "urgency": "normal",
        "requested_by": ctx["employee"].id,
        "operating_unit_id": ctx["ou"].id,
        "state": "approved",
    }
    defaults.update(vals)
    return ctx["env"]["fix.requisition"].create(defaults)


def test_requisition_conversion_creates_po_with_link(ctx):
    env = ctx["env"]
    req = _requisition(ctx)
    req.action_convert_to_po()
    assert req.state == "converted"
    po = req.purchase_order_id
    assert po and po.vendor_id == ctx["vendor"]
    assert po.line_ids.product_id == ctx["product"]
    assert po.line_ids.unit_price == pytest.approx(5000.0)
    assert po.requisition_id == req
    # a converted requisition holds its PO: even if re-approved, converting
    # again would create a second PO for the same demand
    req.state = "approved"
    with pytest.raises(UserError, match="already converted"), env.cr.savepoint():
        req.action_convert_to_po()


def test_requisition_conversion_needs_approval_and_vendor(ctx):
    env = ctx["env"]
    draft = _requisition(ctx, description=f"Draft {TAG}", state="draft")
    with pytest.raises(UserError, match="approved"), env.cr.savepoint():
        draft.action_convert_to_po()
    no_vendor = _requisition(ctx, description=f"No vendor {TAG}")
    no_vendor.vendor_id = False
    with pytest.raises(UserError, match="vendor"), env.cr.savepoint():
        no_vendor.action_convert_to_po()


def test_rfq_open_close_and_close_needs_bid(ctx):
    env = ctx["env"]
    rfq = env["fix.procurement.rfq"].create(
        {"description": f"RFQ {TAG}", "product_id": ctx["product"].id, "qty": 5}
    )
    assert rfq.name.startswith("RFQ/")
    rfq.action_open()
    with pytest.raises(UserError, match="at least one bid"), env.cr.savepoint():
        rfq.action_close()
    env["fix.procurement.bid"].create(
        {"rfq_id": rfq.id, "vendor_id": ctx["vendor"].id, "unit_price": 100}
    )
    rfq.action_close()
    assert rfq.state == "closed"


def test_award_marks_winner_and_losers(ctx):
    env = ctx["env"]
    rfq = env["fix.procurement.rfq"].create(
        {
            "description": f"Award {TAG}",
            "product_id": ctx["product"].id,
            "qty": 2,
            "state": "closed",
        }
    )
    first = env["fix.procurement.bid"].create(
        {"rfq_id": rfq.id, "vendor_id": ctx["vendor"].id, "unit_price": 120}
    )
    second = env["fix.procurement.bid"].create(
        {"rfq_id": rfq.id, "vendor_id": ctx["vendor"].id, "unit_price": 100}
    )
    award = env["fix.procurement.award"].create(
        {"rfq_id": rfq.id, "bid_id": second.id, "rationale": "cheapest"}
    )
    assert award.name.startswith("AWRD/")
    assert second.state == "awarded"
    assert first.state == "lost"
    assert rfq.state == "awarded"


def test_blanket_consumed_uses_pos_in_window(ctx):
    env = ctx["env"]
    blanket = env["fix.procurement.blanket"].create(
        {
            "vendor_id": ctx["vendor"].id,
            "valid_from": date(2026, 1, 1),
            "valid_to": date(2026, 12, 31),
            "cap_amount": 10000,
        }
    )
    po = env["fix.purchase.order"].create(
        {
            "operating_unit_id": ctx["ou"].id,
            "vendor_id": ctx["vendor"].id,
            "date_order": "2026-06-01 10:00:00",
            "line_ids": [
                (0, 0, {"product_id": ctx["product"].id, "qty_ordered": 2, "unit_price": 1000})
            ],
        }
    )
    assert po.amount_total == pytest.approx(2000.0)
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
    case.action_resolve()
    assert case.state == "resolved"
    with pytest.raises(UserError, match="already resolved"), env.cr.savepoint():
        case.action_resolve()


def test_inspection_rejected_and_confirm(ctx):
    env = ctx["env"]
    insp = env["fix.procurement.inspection"].create(
        {
            "receipt_ref": f"GRN/{TAG}",
            "product_id": ctx["product"].id,
            "qty_received": 5,
            "qty_accepted": 4,
            "outcome": "partial",
        }
    )
    assert insp.name.startswith("INSP/")
    assert insp.qty_rejected == pytest.approx(1.0)
    insp.action_confirm()
    assert insp.state == "done"
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
