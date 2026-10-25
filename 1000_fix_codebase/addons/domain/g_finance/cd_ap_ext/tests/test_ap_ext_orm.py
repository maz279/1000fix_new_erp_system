# cd_ap_ext — live-ORM behaviour of M52 AP: TDS determination, the G3-06
# three-way match and the payment-request event seam. DoD-03 statutory set.
from __future__ import annotations

import json
from decimal import Decimal

import pytest
from odoo.exceptions import UserError

pytestmark = [pytest.mark.financial, pytest.mark.tax]

D = Decimal


def _money(value) -> Decimal:
    return D(str(value)).quantize(D("0.01"))


def _events(env, event_type, aggregate_id=None):
    domain = [("event_type", "=", event_type)]
    if aggregate_id is not None:
        domain.append(("aggregate_id", "=", aggregate_id))
    return [json.loads(e.payload) for e in env["fix.event.outbox"].search(domain, order="id")]


@pytest.fixture
def ap(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    vendor = env["res.partner"].create({"name": "Apex Spare Parts Ltd."})
    # a filer: valid proof of return on file, so the statutory rate applies
    # without the non-filer multiplier (see test_ap_a08_orm for the 1.5x path)
    env["fix.vendor.tax.profile"].create(
        {
            "partner_id": vendor.id,
            "taxpayer_type": "company",
            "psr_reference": "PSR-2026-APEX",
            "psr_valid_until": "2099-06-30",
        }
    )
    screen = env["product.product"].create({"name": "LCD screen 14in"})
    battery = env["product.product"].create({"name": "Laptop battery"})
    return {"env": env, "ou": ou, "vendor": vendor, "screen": screen, "battery": battery}


def _po(ap, lines):
    """lines: [(product, qty_ordered, qty_received, unit_price)]"""
    return ap["env"]["fix.purchase.order"].create(
        {
            "operating_unit_id": ap["ou"].id,
            "vendor_id": ap["vendor"].id,
            "line_ids": [
                (0, 0, {"product_id": p.id, "qty_ordered": o, "qty_received": r, "unit_price": u})
                for p, o, r, u in lines
            ],
        }
    )


def _invoice(ap, lines, po=None):
    """lines: [(product, description, qty, unit_price, extra_vals)]"""
    return ap["env"]["fix.vendor.invoice"].create(
        {
            "operating_unit_id": ap["ou"].id,
            "vendor_id": ap["vendor"].id,
            "invoice_ref": "APX-2026-0091",
            "requisition_id": po.id if po else False,
            "line_ids": [
                (0, 0, {"product_id": p.id, "description": d, "quantity": q, "unit_price": u, **x})
                for p, d, q, u, x in lines
            ],
        }
    )


class TestVendorInvoiceTotals:
    def test_tds_per_line_and_payable(self, ap):
        inv = _invoice(
            ap,
            [
                (ap["screen"], "Repair service", 2.0, 1500.0, {"tds_category": "service_general"}),
                (ap["battery"], "Batteries", 1.0, 999.99, {"tds_category": "supply_of_goods"}),
                (ap["battery"], "Exempt supply", 1.0, 500.0, {"tds_exempt": True}),
            ],
        )
        # 3,000.00 @10% = 300.00; 999.99 @5% = 49.9995 -> 50.00; exempt = 0.00
        assert [_money(v) for v in inv.line_ids.mapped("line_total")] == [
            D("3000.00"),
            D("999.99"),
            D("500.00"),
        ]
        assert _money(inv.subtotal) == D("4499.99")
        assert _money(inv.tds_amount) == D("350.00")
        assert _money(inv.total_payable) == D("4149.99")

    def test_missing_category_defaults_to_service_general(self, ap):
        inv = _invoice(ap, [(ap["screen"], "Service", 1.0, 1234.56, {"tds_category": False})])
        assert _money(inv.tds_amount) == D("123.46")  # 1,234.56 @10% = 123.456 -> 123.46
        assert _money(inv.total_payable) == D("1111.10")


class TestThreeWayMatch:
    def test_no_purchase_order_is_unmatched(self, ap):
        inv = _invoice(ap, [(ap["screen"], "Screen", 1.0, 100.0, {})])
        assert inv.match_state == "unmatched"
        assert inv.match_detail == "No purchase order linked"

    def test_po_receipt_and_price_reconciled(self, ap):
        po = _po(ap, [(ap["screen"], 3.0, 3.0, 4200.0)])
        inv = _invoice(ap, [(ap["screen"], "Screen", 3.0, 4200.01, {})], po)  # within 0.01
        assert inv.match_state == "matched"
        assert inv.match_detail == "PO / receipt / invoice reconciled"

    def test_every_variance_blocks(self, ap):
        po = _po(ap, [(ap["screen"], 3.0, 1.0, 4200.0)])
        inv = _invoice(
            ap,
            [
                (ap["screen"], "Screen", 2.0, 4200.02, {}),
                (ap["battery"], "Battery", 1.0, 900.0, {}),
            ],
            po,
        )
        assert inv.match_state == "blocked"
        assert inv.match_detail.split("\n") == [
            "Screen: received 1.00 < invoiced 2.00",
            "Screen: price above PO",
            "Battery: not on the PO",
        ]

    def test_editing_an_invoice_line_rematches(self, ap):
        """Regression: the match only depended on ('line_ids',
        'requisition_id'); raising a matched line's quantity kept it
        'matched' and payable without the goods having been received."""
        po = _po(ap, [(ap["screen"], 5.0, 2.0, 1000.0)])
        inv = _invoice(ap, [(ap["screen"], "Screen", 2.0, 1000.0, {})], po)
        assert inv.match_state == "matched"
        inv.line_ids.quantity = 4.0
        assert inv.match_state == "blocked"
        assert inv.match_detail == "Screen: received 2.00 < invoiced 4.00"
        with pytest.raises(UserError, match="G3-06"), ap["env"].cr.savepoint():
            inv.action_request_payment()

    def test_goods_receipt_unblocks(self, ap):
        po = _po(ap, [(ap["screen"], 2.0, 0.0, 1000.0)])
        inv = _invoice(ap, [(ap["screen"], "Screen", 2.0, 1000.0, {})], po)
        assert inv.match_state == "blocked"
        po.line_ids.qty_received = 2.0
        assert inv.match_state == "matched"


class TestPaymentRequest:
    def test_unmatched_invoice_cannot_be_paid(self, ap):
        inv = _invoice(ap, [(ap["screen"], "Screen", 1.0, 100.0, {})])
        with (
            pytest.raises(UserError, match=r"G3-06.*state: unmatched — No purchase order"),
            ap["env"].cr.savepoint(),
        ):
            inv.action_request_payment()
        assert _events(ap["env"], "payment.requested", inv.id) == []

    def test_matched_but_unapproved_invoice_cannot_be_paid(self, ap):
        po = _po(ap, [(ap["screen"], 1.0, 1.0, 5000.0)])
        inv = _invoice(ap, [(ap["screen"], "Screen", 1.0, 5000.0, {})], po)
        with pytest.raises(UserError, match="only approved bills"), ap["env"].cr.savepoint():
            inv.action_request_payment()
        assert _events(ap["env"], "payment.requested", inv.id) == []

    def test_matched_invoice_raises_payment_event(self, ap):
        po = _po(ap, [(ap["screen"], 1.0, 1.0, 5000.0)])
        inv = _invoice(ap, [(ap["screen"], "Screen", 1.0, 5000.0, {})], po)
        # the approval workflow itself is covered in test_ap_a08_orm
        inv.approval_state = "approved"
        inv.action_request_payment()
        assert _events(ap["env"], "payment.requested", inv.id) == [
            {
                "vendor_id": ap["vendor"].id,
                "amount": 4500.0,  # 5,000.00 - 10% TDS 500.00
                "currency": "BDT",
                "invoice_ref": "APX-2026-0091",
                "operating_unit_id": ap["ou"].id,
            }
        ]


class TestExpenseClaim:
    """Submission / approval basics; policy, SoD and GL posting are covered in
    test_ap_a08_orm (they need the GL roles configured)."""

    def _claim(self, ap, amount, **vals):
        env = ap["env"]
        employee = env["hr.employee"].create({"name": "Field Technician Rafiq"})
        return env["fix.expense.claim"].create(
            {
                "operating_unit_id": ap["ou"].id,
                "employee_id": employee.id,
                "description": "Travel to client site",
                "amount": amount,
                **vals,
            }
        )

    def test_submit_moves_to_submitted(self, ap):
        small = self._claim(ap, 25000.0)
        large = self._claim(ap, 25000.01)
        (small | large).action_submit()
        # above the threshold a finance MANAGER approves (checked on approval)
        assert (small.state, large.state) == ("submitted", "submitted")
        assert small.submitted_by == ap["env"].user

    def test_non_positive_claim_refused(self, ap):
        claim = self._claim(ap, 0.0)
        with pytest.raises(UserError, match="positive amount"), ap["env"].cr.savepoint():
            claim.action_submit()

    def test_only_submitted_claims_are_approved(self, ap):
        claim = self._claim(ap, 1800.5)
        with (
            pytest.raises(UserError, match=r"Only submitted claims .*\(draft\)"),
            ap["env"].cr.savepoint(),
        ):
            claim.action_approve()
        claim.action_submit()
        # Segregation of duties: the submitter cannot approve
        with pytest.raises(UserError, match="Segregation of duties"), ap["env"].cr.savepoint():
            claim.action_approve()
        assert claim.state == "submitted"
        assert _events(ap["env"], "payment.requested", claim.id) == []
