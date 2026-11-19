# Settlement rules a real order-to-cash needs (A02 ERP audit, 19 Nov 2026).
#
# Imported LAST in this package: it overrides methods of fix_service_order.
#
# 1. Over-settlement (X-05): any amount at or above the amount due was taken,
#    so a technician's unverified TrxID claim of BDT 50,000 on a BDT 500 job
#    became the refund ceiling when the order was cancelled. Counter and field
#    money is now the amount due; an M20 receipt that is larger settles the
#    amount due and keeps the rest as the customer's credit on that receipt.
# 2. Top-up (X-07 / M01-F5): an approved estimate revised upwards after the
#    order was paid left it unreleasable (delivery: "owes more"; settlement:
#    "already settled"). The difference can now be taken as a top-up, by the
#    counter or against an M20 receipt; the amounts add up on the order.
# 3. Refunds are of real money only (M01-F10): cancelling an order whose
#    collection was never verified (a typed TrxID) voids the claim instead of
#    raising a refund for it; cancelling a VERIFIED paid order is a
#    supervisor's decision.
from odoo import models
from odoo.exceptions import UserError

from .fix_service_order import GROUP_CASHIER, GROUP_SUPERVISOR

CENT = 0.005


class FixServiceOrderSettlementRules(models.Model):
    _inherit = "fix.service.order"

    def _fix_record_settlement(self, amount_bdt, reference, source):
        self.ensure_one()
        try:
            amount = float(amount_bdt)
        except (TypeError, ValueError):
            raise UserError("Enter the amount received for order %s." % self.name) from None
        if self.payment_settlement_state == "settled" and self.settlement_verified:
            return self._fix_record_topup(amount, reference, source)
        due = self._fix_amount_due()
        if due <= CENT and self._fix_governing_estimate():
            # advances already received (the diagnostic fee) cover the
            # estimate: the device is released without new money, and taking
            # some anyway would only leave it unapplied on the customer
            raise UserError(
                "Order %s owes nothing more: what was already received covers its estimate. "
                "Deliver it without a new payment." % self.name
            )
        if due > CENT and amount > due + CENT:
            if source == "m20_receipt":
                # the receipt may carry more (the customer paid ahead); the
                # order takes what it owes and the rest stays on the receipt
                amount = round(due, 2)
            else:
                raise UserError(
                    "BDT %.2f is more than the BDT %.2f due on order %s: record the amount due "
                    "(give the customer change, or take the surplus as a separate receipt)."
                    % (amount, due, self.name)
                )
        result = super()._fix_record_settlement(amount, reference, source)
        if source == "m20_receipt" and hasattr(self, "_fix_link_m20_receipt"):
            self._fix_link_m20_receipt(self._fix_m20_receipt_of(reference))
        return result

    def _fix_m20_receipt_of(self, reference):
        """The receipt this order now holds under ``reference`` (after the
        settlement, _fix_find_m20_receipt no longer offers it to this order's
        siblings; this order may still read it)."""
        if "fix.ar.receipt" not in self.env:
            return False
        partner = self.customer_id.commercial_partner_id
        return (
            self.env["fix.ar.receipt"]
            .sudo()
            .search(
                [
                    ("state", "=", "confirmed"),
                    "|",
                    ("name", "=", reference),
                    ("reference", "=", reference),
                ]
            )
            .filtered(lambda r: r.customer_id.commercial_partner_id == partner)[:1]
        )

    def _fix_record_topup(self, amount, reference, source):
        """The order was paid and its price then went up: take the difference."""
        self.ensure_one()
        due = self._fix_amount_due()
        paid = self.amount_settled_bdt or 0.0
        short = round(due - paid, 2)
        if short <= CENT:
            raise UserError("Order %s is already settled and verified." % self.name)
        if self.state in ("closed", "cancelled"):
            raise UserError("Order %s is %s; it takes no settlement." % (self.name, self.state))
        reference = (reference or "").strip()
        if not reference:
            raise UserError("A top-up needs the receipt or transaction reference.")
        if amount + CENT < short:
            raise UserError(
                "BDT %.2f does not cover the BDT %.2f still due on order %s."
                % (amount, short, self.name)
            )
        if source == "m20_receipt":
            receipt = self._fix_find_m20_receipt(reference, short)
            if not receipt:
                raise UserError(
                    "No confirmed M20 receipt '%s' of at least BDT %.2f exists for %s."
                    % (reference, short, self.customer_id.display_name)
                )
            amount = short
        elif source == "counter":
            if not (self.env.su or self.env.user.has_group(GROUP_CASHIER)):
                raise UserError("Only a Service Order Cashier takes a counter top-up.")
            if amount > short + CENT:
                raise UserError(
                    "BDT %.2f is more than the BDT %.2f still due on order %s."
                    % (amount, short, self.name)
                )
            receipt = False
        else:
            raise UserError(
                "A top-up is taken at the counter or against an M20 receipt, not as a field "
                "collection."
            )
        self._guarded().write(
            {
                "amount_settled_bdt": round(paid + amount, 2),
                "settlement_recorded_by": self.env.user.id,
            }
        )
        if receipt and hasattr(self, "_fix_link_m20_receipt"):
            self._fix_link_m20_receipt(receipt)
        self.message_post(
            body="Settlement top-up (%s): %s, BDT %.2f; BDT %.2f now settled against BDT %.2f due."
            % (source, reference, amount, paid + amount, due)
        )
        return True

    # ------------------------------------------------------------ cancel
    def action_cancel(self, reason_code=None, note=None, reason=None):
        for order in self:
            if order.payment_settlement_state != "settled":
                continue
            if not order.settlement_verified:
                # a typed TrxID / field claim is not money: void it, refund nothing
                claim = order.amount_settled_bdt or 0.0
                order._guarded().write(
                    {
                        "payment_settlement_state": "unpaid",
                        "amount_settled_bdt": 0.0,
                    }
                )
                order.message_post(
                    body="Unverified collection claim %s of BDT %.2f voided on cancellation: "
                    "nothing is refunded for money never verified. Cash a technician really "
                    "holds is accepted by a cashier and refunded by finance."
                    % (order.invoice_ref or "", claim)
                )
            elif not (self.env.su or self.env.user.has_group(GROUP_SUPERVISOR)):
                raise UserError(
                    "Order %s is paid (BDT %.2f): only a Service Supervisor cancels a paid order, "
                    "which refunds the customer." % (order.name, order.amount_settled_bdt)
                )
        return super().action_cancel(reason_code=reason_code, note=note, reason=reason)
