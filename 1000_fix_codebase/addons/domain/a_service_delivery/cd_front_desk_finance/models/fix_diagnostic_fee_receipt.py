# The walk-in diagnostic fee reaches the books (A02 ERP audit, 19 Nov 2026).
#
# A cash diagnostic fee went into the drawer (cash_payments) and nowhere else,
# and a wallet / card fee went nowhere at all: no GL, no AR. The M50 deposit
# then credited the drawer account for cash never debited to it, and the fee
# was charged a second time in the repair settlement (the order's amount due
# was the full estimate).
#
# At the hand-over that creates the service order, a paid fee now raises a
# confirmed M20 receipt marked as an ADVANCE on that order:
#   cash            Dr drawer cash / Cr the customer's AR
#   wallet / card   Dr the channel clearing / Cr the customer's AR
# The order's amount due is the estimate less its advances (cd_billing_engine
# fix_order_settlement), and the order's invoice applies the advance with the
# settlement. A declined repair keeps the advance as the customer's credit,
# which finance invoices as the fee or refunds (unapplied-cash queue).
from odoo import fields, models
from odoo.exceptions import UserError

from .fix_counter_sale_posting import resolve_account

FEE_CHANNEL_METHOD = {"cash": "cash", "bkash": "bkash", "nagad": "nagad", "card": "card"}


class FixWalkinIntakeFeeReceipt(models.Model):
    _inherit = "fix.walkin.intake"

    diagnostic_fee_receipt_id = fields.Many2one(
        "fix.ar.receipt",
        string="Diagnostic Fee Receipt (M20)",
        readonly=True,
        copy=False,
        index=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"diagnostic_fee_receipt_id"}

    def action_complete_handover(self):
        result = super().action_complete_handover()
        for rec in self:
            rec._fdf_raise_fee_receipt()
        return result

    def _fdf_raise_fee_receipt(self):
        self.ensure_one()
        fee = round(self.diagnostic_fee_bdt or 0.0, 2)
        method = FEE_CHANNEL_METHOD.get(self.payment_channel or "")
        if fee <= 0 or not method or self.diagnostic_fee_receipt_id:
            return self.env["fix.ar.receipt"]
        if method == "cash" and not self.diagnostic_fee_shift_id:
            return self.env["fix.ar.receipt"]  # taken outside any drawer (branch switch off)
        order = self.service_order_id
        company = self.company_id or self.env.company
        if method == "cash":
            account, why = resolve_account(self.env, company, "drawer_cash")
            if not account:
                raise UserError("Diagnostic fee of %s refused: %s" % (self.display_name, why))
        unit = (order.operating_unit_id if order else False) or self.branch_id.operating_unit_id
        receipt = (
            self.env["fix.ar.receipt"]
            .sudo()
            .with_company(company)
            .create(
                {
                    "company_id": company.id,
                    "operating_unit_id": unit.id if unit else False,
                    "branch_id": self.branch_id.id,
                    "customer_id": self.customer_id.id,
                    "amount": fee,
                    "method": method,
                    "reference": (self.payment_trx_ref or "").strip()
                    or "DIAG/%s" % (self.display_name or self.id),
                    "receipt_date": fields.Date.context_today(self),
                    "source_order_id": order.id if order else False,
                    "is_order_advance": True,
                }
            )
        )
        receipt.action_confirm()
        self._guarded().write({"diagnostic_fee_receipt_id": receipt.id})
        self.message_post(
            body="Diagnostic fee BDT %.2f posted to the books as receipt %s%s."
            % (fee, receipt.name, " (an advance on %s)" % order.name if order else "")
        )
        return receipt
