# Field cash never enters a drawer without a receipt (A02 pass 2, D3 / M02-01).
#
# M02-01 (P0): a technician's on-site cash that M01 refused to record as the
# order's settlement (a part payment: less than the amount due) was still
# accepted into the branch drawer: the drawer total rose, nothing reached AR
# or the GL, and the M50 deposit then credited the drawer account for cash
# never debited to it.
#
# The drawer's own field-cash posting (fix.cash.shift._post_field_cash) now
# guarantees the receipt, whoever calls it:
#   - the order holds a recorded field settlement (cash): its settlement
#     receipt is raised now for the cash moving (Dr drawer / Cr AR), so the
#     cashier's verification right after finds it booked;
#   - no settlement was recorded (owner decision D3, a part payment): the
#     cash is booked as an ADVANCE receipt on the order (Dr drawer / Cr AR,
#     unapplied); the order's amount due is the estimate less its advances,
#     and its invoice applies the advance. The order stays unpaid for the rest.
# A posting with no service order behind it is refused: field cash is always
# some order's money.
import re

from odoo import models
from odoo.exceptions import UserError

from .fix_counter_sale_posting import resolve_account
from .fix_order_cash_receipt import assert_receipt_posted, dhaka_today

# cd_field_service's acceptance reference: "Field cash <field order> / <service order>"
_FIELD_CASH_REF = re.compile(r"/\s*(?P<order>[^/]+?)\s*$")


class FixCashShiftFieldCashReceipt(models.Model):
    _inherit = "fix.cash.shift"

    def _post_field_cash(self, amount, reference=None, order=None):
        order = order or self._fdf_field_cash_order(reference)
        if not order:
            raise UserError(
                "Field cash of BDT %.2f (%s) names no service order: field cash enters a drawer "
                "only with the receipt of the order it was collected for."
                % (amount or 0.0, reference or "no reference")
            )
        result = super()._post_field_cash(amount, reference=reference, order=order)
        order.sudo()._fdf_book_field_cash(amount, reference)
        return result

    def _fdf_field_cash_order(self, reference):
        """The service order named at the end of the acceptance reference."""
        match = _FIELD_CASH_REF.search(reference or "")
        if not match:
            return self.env["fix.service.order"]
        company = self[:1].company_id or self.env.company
        return (
            self.env["fix.service.order"]
            .sudo()
            .search([("name", "=", match.group("order")), ("company_id", "=", company.id)], limit=1)
        )


class FixServiceOrderFieldCashReceipt(models.Model):
    _inherit = "fix.service.order"

    def _fdf_book_field_cash(self, amount, reference):
        """D3: the receipt behind field cash entering the drawer. Returns it."""
        self.ensure_one()
        amount = round(amount or 0.0, 2)
        if amount <= 0:
            return self.env["fix.ar.receipt"]
        recorded = self.payment_settlement_state in ("settled", "partial") and (
            # a full settlement or (interface contract, D3) a part payment
            (
                self.settlement_source == "field_collection"
                and (self.settlement_tender or "cash") == "cash"
            )
            # A02 pass 2 review (N3): the part paid on site, then the balance
            # as cash on delivery before the cashier counted the field cash:
            # the order still holds the field part, recorded and not yet in
            # the books. Booked as an advance, it was counted twice.
            or self.settlement_source == "cod"
        )
        if not recorded:
            return self._fdf_raise_field_advance(amount, reference)
        missing = round((self.amount_settled_bdt or 0.0) - self._fdf_settled_in_books(), 2)
        take = round(min(amount, max(missing, 0.0)), 2)
        receipt = self.env["fix.ar.receipt"]
        if take > 0.005:
            receipt = self._fdf_raise_settlement_receipt(take, tender="cash")
        # A02 pass 2 review (D20): the technician handed in more than the
        # order still takes (it was paid or its price fell meanwhile). The
        # drawer has the cash: the rest is the customer's credit on the order
        # (an advance receipt, refunded or applied later), never off the books.
        excess = round(amount - take, 2)
        if excess > 0.005:
            receipt |= self._fdf_raise_field_advance(excess, reference)
        return receipt

    def _fdf_raise_field_advance(self, amount, reference):
        """A part payment taken on site: an advance receipt on the order."""
        self.ensure_one()
        company = self.company_id or self.env.company
        account, why = resolve_account(self.env, company, "drawer_cash")
        if not account:
            raise UserError("Field cash for %s refused: %s" % (self.name, why))
        unit = self.operating_unit_id or self.branch_id.operating_unit_id
        check = self.env["fix.cash.id.check"].sudo().search([("order_id", "=", self.id)], limit=1)
        receipt = (
            self.env["fix.ar.receipt"]
            .sudo()
            .with_company(company)
            .create(
                {
                    "company_id": company.id,
                    "operating_unit_id": unit.id or False,
                    "branch_id": self.branch_id.id,
                    "customer_id": self.customer_id.id,
                    "amount": amount,
                    "method": "cash",
                    "reference": (reference or "").strip() or "FIELD/%s" % self.name,
                    "receipt_date": dhaka_today(),
                    "source_order_id": self.id,
                    "is_order_advance": True,
                    "cash_id_check_id": check.id or False,
                }
            )
        )
        receipt.action_confirm()
        assert_receipt_posted(receipt, "Field cash for %s" % self.name)
        self.message_post(
            body="Part payment of BDT %.2f taken on site and handed in: booked as advance "
            "receipt %s on this order (D3). The order stays unpaid for the rest."
            % (amount, receipt.name)
        )
        return receipt
