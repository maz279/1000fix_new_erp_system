# A06 S6 (A06 workflow audit 2026-11-03, findings M16-4/7/8): the three-way
# match on locked data, per receipt line.
#
# The match used to read the PO line's typed qty_received and live unit_price,
# per bill and per line: raising the PO price unblocked a bill, a typed receipt
# matched, two bills (staff or portal) and two lines billed 20 against 10
# received, and a 10/10 inspection rejection still matched. It now reads the
# accepted quantity of POSTED receipt lines, less what earlier live bills on
# the same PO already claimed, at the price the PO approval covered.
from __future__ import annotations

import pytest
from odoo.exceptions import UserError

pytestmark = [pytest.mark.financial]


@pytest.fixture
def m(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    vendor = env["res.partner"].create({"name": "A06 Match Vendor Ltd."})
    if "fix.supplier" in env:
        sup = env["fix.supplier"].create(
            {"name": vendor.name, "partner_id": vendor.id, "status": "active"}
        )
        for doc_type in ("trade_licence", "tin", "vat"):
            env["fix.supplier.document"].create(
                {"supplier_id": sup.id, "doc_type": doc_type, "state": "valid"}
            )
    screen, battery = env["product.product"].create(
        [{"name": "A06 Screen"}, {"name": "A06 Battery"}]
    )
    return {"env": env, "ou": ou, "vendor": vendor, "screen": screen, "battery": battery}


def _sent_po(m, lines):
    """lines: [(product, qty, unit_price)] — approved and sent, nothing received."""
    env = m["env"]
    po = env["fix.purchase.order"].create(
        {
            "operating_unit_id": m["ou"].id,
            "vendor_id": m["vendor"].id,
            "line_ids": [
                (0, 0, {"product_id": p.id, "qty_ordered": q, "unit_price": u}) for p, q, u in lines
            ],
        }
    )
    po.action_record_requisition_exception(reason="A06 match test PO")
    po._guarded().write(
        {
            "approval_state": "approved",
            "dofa_approved": True,
            "dofa_approved_tier": po._dofa_current_tier(),
            "dofa_approved_amount": po.amount_total,
        }
    )
    po.action_send()
    return po


def _receive(po, line, qty, accept=None):
    po.action_record_receipt({line.id: qty})
    rline = po.receipt_ids.sorted("id")[-1].line_ids
    if accept is not None:
        po.env["fix.procurement.inspection"].create(
            {"receipt_line_id": rline.id, "qty_accepted": accept}
        ).action_confirm()
    return rline


def _bill(m, po, lines, ref):
    return m["env"]["fix.vendor.invoice"].create(
        {
            "vendor_id": m["vendor"].id,
            "invoice_ref": ref,
            "requisition_id": po.id,
            "operating_unit_id": m["ou"].id,
            "line_ids": [
                (0, 0, {"product_id": p.id, "description": d, "quantity": q, "unit_price": u})
                for p, d, q, u in lines
            ],
        }
    )


def test_m16_posted_accepted_receipt_matches(m):
    po = _sent_po(m, [(m["screen"], 10, 1000)])
    _receive(po, po.line_ids, 10, accept=10)
    inv = _bill(m, po, [(m["screen"], "Screen", 10, 1000)], "A06-MATCH-1")
    assert (inv.match_state, inv.match_detail) == ("matched", "PO / receipt / invoice reconciled")


def test_m16_receipt_awaiting_inspection_is_not_matchable(m):
    po = _sent_po(m, [(m["screen"], 10, 1000)])
    _receive(po, po.line_ids, 10)
    inv = _bill(m, po, [(m["screen"], "Screen", 10, 1000)], "A06-MATCH-2")
    assert inv.match_state == "blocked"
    assert inv.match_detail == "Screen: received 0.00 < invoiced 10.00 (10.00 awaiting inspection)"
    po.receipt_ids.line_ids.inspection_ids.create(
        {"receipt_line_id": po.receipt_ids.line_ids.id, "qty_accepted": 10}
    ).action_confirm()
    assert inv.match_state == "matched"


def test_m16_inspection_not_required_is_configuration(m):
    m["env"]["ir.config_parameter"].set_param("cd_requisition.receipt_inspection_required", "0")
    po = _sent_po(m, [(m["screen"], 10, 1000)])
    rline = _receive(po, po.line_ids, 10)
    assert rline.inspection_state == "not_required" and rline.qty_accepted == 10
    assert _bill(m, po, [(m["screen"], "Screen", 10, 1000)], "A06-MATCH-3").match_state == "matched"


def test_m16_failed_inspection_blocks(m):
    po = _sent_po(m, [(m["screen"], 10, 1000)])
    _receive(po, po.line_ids, 10, accept=0)
    inv = _bill(m, po, [(m["screen"], "Screen", 10, 1000)], "A06-MATCH-4")
    assert inv.match_state == "blocked"
    assert (
        inv.match_detail == "Screen: received 0.00 < invoiced 10.00 (10.00 rejected at inspection)"
    )


def test_m16_partial_inspection_matches_only_accepted(m):
    po = _sent_po(m, [(m["screen"], 10, 1000)])
    _receive(po, po.line_ids, 10, accept=7)
    assert _bill(m, po, [(m["screen"], "Screen", 8, 1000)], "A06-MATCH-5").match_state == "blocked"
    ok = _bill(m, po, [(m["screen"], "Screen", 7, 1000)], "A06-MATCH-5b")
    assert ok.match_state == "blocked"  # the 8-unit bill came first and claims the receipt
    m["env"]["fix.vendor.invoice"].search([("invoice_ref", "=", "A06-MATCH-5")]).with_context(
        ap_internal=True
    ).write({"approval_state": "rejected"})
    ok.invalidate_recordset()
    assert ok.match_state == "matched"


def test_m16_receipt_line_is_invoiced_once(m):
    po = _sent_po(m, [(m["screen"], 10, 1000)])
    _receive(po, po.line_ids, 10, accept=10)
    first = _bill(m, po, [(m["screen"], "Screen", 10, 1000)], "A06-MATCH-6A")
    second = _bill(m, po, [(m["screen"], "Screen", 10, 1000)], "A06-MATCH-6B")
    assert first.match_state == "matched" and second.match_state == "blocked"
    assert second.match_detail == (
        "Screen: received 10.00, 10.00 already invoiced on other bills, invoiced 10.00"
    )
    with pytest.raises(UserError, match="G3-06"), m["env"].cr.savepoint():
        second.with_context(ap_internal=True).write({"approval_state": "approved"})
        second.action_request_payment()


def test_m16_two_partial_bills_share_the_receipt(m):
    po = _sent_po(m, [(m["screen"], 10, 1000)])
    _receive(po, po.line_ids, 10, accept=10)
    a = _bill(m, po, [(m["screen"], "Screen", 6, 1000)], "A06-MATCH-7A")
    b = _bill(m, po, [(m["screen"], "Screen", 4, 1000)], "A06-MATCH-7B")
    c = _bill(m, po, [(m["screen"], "Screen", 1, 1000)], "A06-MATCH-7C")
    assert (a.match_state, b.match_state, c.match_state) == ("matched", "matched", "blocked")


def test_m16_split_lines_are_summed(m):
    po = _sent_po(m, [(m["screen"], 10, 1000)])
    _receive(po, po.line_ids, 10, accept=10)
    inv = _bill(
        m,
        po,
        [(m["screen"], "Screen a", 10, 1000), (m["screen"], "Screen b", 10, 1000)],
        "A06-MATCH-8",
    )
    assert inv.match_state == "blocked"
    assert inv.match_detail == "Screen a: received 10.00 < invoiced 20.00"


def test_m16_price_comes_from_the_approved_po(m):
    po = _sent_po(m, [(m["screen"], 10, 1000)])
    _receive(po, po.line_ids, 10, accept=10)
    assert po.line_ids.approved_unit_price == 1000
    inv = _bill(m, po, [(m["screen"], "Screen", 10, 2000)], "A06-MATCH-9")
    assert inv.match_state == "blocked" and "price above PO" in inv.match_detail
    with pytest.raises(UserError, match="change order"), m["env"].cr.savepoint():
        po.line_ids.write({"unit_price": 2000})
    assert inv.match_state == "blocked"


def test_m16_unapproved_draft_po_is_not_matchable(m):
    po = m["env"]["fix.purchase.order"].create(
        {
            "operating_unit_id": m["ou"].id,
            "vendor_id": m["vendor"].id,
            "line_ids": [
                (0, 0, {"product_id": m["screen"].id, "qty_ordered": 1, "unit_price": 1000})
            ],
        }
    )
    inv = _bill(m, po, [(m["screen"], "Screen", 1, 1000)], "A06-MATCH-10")
    assert inv.match_state == "blocked"
    assert inv.match_detail == "Screen: received 0.00 < invoiced 1.00"


def test_m16_qty_variance_blocks_and_refuses_payment(m):
    """Replaces the MagicMock test of test_ap_ext.py: 10 invoiced, 4 received."""
    po = _sent_po(m, [(m["battery"], 10, 500)])
    _receive(po, po.line_ids, 4, accept=4)
    inv = _bill(m, po, [(m["battery"], "Spare Battery Pack", 10, 500)], "A06-MATCH-11")
    assert inv.match_state == "blocked"
    assert "received 4.00 < invoiced 10.00" in inv.match_detail
    with pytest.raises(UserError, match="G3-06: an unmatched vendor invoice cannot be paid"):
        inv.action_request_payment()


def test_m16_price_variance_blocks_and_refuses_payment(m):
    """Replaces the MagicMock test of test_ap_ext.py: 3,500 invoiced, PO 3,000."""
    po = _sent_po(m, [(m["screen"], 1, 3000)])
    _receive(po, po.line_ids, 1, accept=1)
    inv = _bill(m, po, [(m["screen"], "Display Panel", 1, 3500)], "A06-MATCH-12")
    assert inv.match_state == "blocked" and "price above PO" in inv.match_detail
    with pytest.raises(UserError, match="G3-06: an unmatched vendor invoice cannot be paid"):
        inv.action_request_payment()


def test_m16_not_on_po_and_multiple_products(m):
    po = _sent_po(m, [(m["screen"], 2, 1000)])
    _receive(po, po.line_ids, 2, accept=2)
    inv = _bill(
        m, po, [(m["screen"], "Screen", 2, 1000), (m["battery"], "Battery", 1, 50)], "A06-MATCH-13"
    )
    assert inv.match_detail == "Battery: not on the PO"
