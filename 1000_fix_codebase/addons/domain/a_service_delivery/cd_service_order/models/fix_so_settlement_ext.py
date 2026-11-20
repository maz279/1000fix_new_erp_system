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
# 4. A02 pass 2 (D1/D3): an on-site collection smaller than the amount due is
#    a PART PAYMENT (state 'partial'), never refused, so the technician's
#    drawer and the receipt move together; the balance is taken later (field,
#    counter, M20 receipt or cash on delivery). Cash on delivery ('cod') is
#    recorded unverified at proof of delivery.
from odoo import fields, models
from odoo.exceptions import UserError

from .fix_service_order import _SETTLEMENT_SOURCE_KEYS, GROUP_CASHIER, GROUP_SUPERVISOR

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
        if self.payment_settlement_state == "partial":
            return self._fix_record_balance(amount, reference, source)
        due = self._fix_amount_due()
        if source == "field_collection" and due > CENT and 0 < amount < due - CENT:
            # D3: part of the amount due, taken on site
            return self._fix_record_part_payment(amount, reference, source)
        if source == "cod":
            self._fix_assert_cod_amount(amount, self._fix_amount_outstanding())
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

    def _fix_paid_so_far(self) -> float:
        """What the order already holds in VERIFIED money (a settlement or
        part payments); a payment recorded now adds to it. For the drawer and
        the receipt hooks: the money a call took is what it adds to this."""
        self.ensure_one()
        if self.payment_settlement_state not in ("settled", "partial"):
            return 0.0
        if self.settlement_verified:
            # all of it (an order settled before amount_verified_bdt existed too)
            return round(self.amount_settled_bdt or 0.0, 2)
        return round(self.amount_verified_bdt or 0.0, 2)

    def _fix_recorded_so_far(self) -> float:
        """Every payment recorded on the order, verified or not (part
        payments, a settlement, cash on delivery)."""
        self.ensure_one()
        if self.payment_settlement_state not in ("settled", "partial"):
            return 0.0
        return round(self.amount_settled_bdt or 0.0, 2)

    def _fix_amount_outstanding(self) -> float:
        """Interface contract (S1/S2/S3, 20 Nov): what is still to collect -
        the amount due less every payment recorded on the order, verified or
        not. (_fix_amount_due() is the amount due before payments; advances
        such as the diagnostic fee are already netted from it.)"""
        self.ensure_one()
        return max(round(self._fix_amount_due() - self._fix_recorded_so_far(), 2), 0.0)

    def _fix_assert_settlement_input(self, amount, reference, source):
        if source not in _SETTLEMENT_SOURCE_KEYS:
            raise UserError(
                "Unknown settlement source '%s' (expected one of: %s)."
                % (source, ", ".join(sorted(_SETTLEMENT_SOURCE_KEYS)))
            )
        if self.state in ("closed", "cancelled"):
            raise UserError("Order %s is %s; it takes no settlement." % (self.name, self.state))
        reference = (reference or "").strip()
        if not reference:
            raise UserError(
                "A payment needs the receipt or transaction reference that proves it (M01-15)."
            )
        if amount <= CENT:
            raise UserError("Enter the amount received for order %s." % self.name)
        return reference

    def _fix_assert_cod_amount(self, amount, outstanding):
        """Contract: a cash-on-delivery collection is exactly what is still
        to collect - the rider collects that, no more, no less."""
        if abs(amount - outstanding) > CENT:
            raise UserError(
                "Cash on delivery of order %s is BDT %.2f (what is still to collect), not "
                "BDT %.2f." % (self.name, outstanding, amount)
            )

    def _fix_record_part_payment(self, amount, reference, source):
        """D3: an on-site payment smaller than what is still to collect is a
        part payment: recorded unverified, like any field collection, and the
        rest stays due. Never refused, so the technician's cash and the
        receipt move together. Verify Settlement verifies what is recorded."""
        self.ensure_one()
        reference = self._fix_assert_settlement_input(amount, reference, source)
        recorded = self._fix_recorded_so_far()
        verified_part = self._fix_paid_so_far()
        self._guarded().write(
            {
                "payment_settlement_state": "partial",
                "invoice_ref": reference,
                "amount_settled_bdt": round(recorded + amount, 2),
                "amount_verified_bdt": verified_part,
                "settlement_source": source,
                "settlement_recorded_by": self.env.user.id,
                "settlement_verified": False,
                "settlement_verified_by": False,
                "settlement_verified_at": False,
            }
        )
        due = self._fix_amount_due()
        self.message_post(
            body="Part payment recorded (%s): %s, BDT %.2f; BDT %.2f of BDT %.2f received, "
            "BDT %.2f still due. NOT YET VERIFIED."
            % (source, reference, amount, recorded + amount, due, self._fix_amount_outstanding())
        )
        return True

    def _fix_record_balance(self, amount, reference, source):
        """The balance of a part-paid order (D3): from the field (again a part
        payment when still short), the counter, an M20 receipt or cash on
        delivery. The order is settled once what is still to collect is
        covered; it is verified once every part is."""
        self.ensure_one()
        reference = self._fix_assert_settlement_input(amount, reference, source)
        due = self._fix_amount_due()
        recorded = self._fix_recorded_so_far()
        verified_part = self._fix_paid_so_far()
        short = self._fix_amount_outstanding()
        if short <= CENT:
            raise UserError(
                "Order %s owes nothing more: BDT %.2f was received against BDT %.2f due."
                % (self.name, recorded, due)
            )
        if source == "field_collection" and amount < short - CENT:
            return self._fix_record_part_payment(amount, reference, source)
        if source == "cod":
            self._fix_assert_cod_amount(amount, short)
        if amount > short + CENT:
            if source != "m20_receipt":
                raise UserError(
                    "BDT %.2f is more than the BDT %.2f balance of order %s."
                    % (amount, short, self.name)
                )
            amount = short
        if amount + CENT < short:
            raise UserError(
                "BDT %.2f does not cover the BDT %.2f balance of order %s."
                % (amount, short, self.name)
            )
        verified = False
        receipt = False
        if source == "m20_receipt":
            receipt = self._fix_find_m20_receipt(reference, short)
            if not receipt:
                raise UserError(
                    "No confirmed M20 receipt '%s' of at least BDT %.2f exists for %s."
                    % (reference, short, self.customer_id.display_name)
                )
            verified = True
        elif source == "counter":
            if not (self.env.su or self.env.user.has_group(GROUP_CASHIER)):
                raise UserError("Only a Service Order Cashier takes a counter payment.")
            verified = True
        total = round(recorded + amount, 2)
        verified_total = round(verified_part + (amount if verified else 0.0), 2)
        all_verified = verified_total + CENT >= total
        now = fields.Datetime.now()
        self._guarded().write(
            {
                "payment_settlement_state": "settled",
                "invoice_ref": reference,
                "amount_settled_bdt": total,
                "settlement_source": source,
                "settlement_recorded_by": self.env.user.id,
                "settlement_verified": all_verified,
                "settlement_verified_by": self.env.user.id if all_verified else False,
                "settlement_verified_at": now if all_verified else False,
                "amount_verified_bdt": verified_total,
            }
        )
        if receipt and hasattr(self, "_fix_link_m20_receipt"):
            self._fix_link_m20_receipt(receipt)
        self.message_post(
            body="Balance recorded (%s): %s, BDT %.2f; BDT %.2f now settled against BDT %.2f "
            "due%s."
            % (
                source,
                reference,
                amount,
                total,
                due,
                "" if all_verified else " - NOT ALL VERIFIED YET",
            )
        )
        return True

    def action_confirm_cod_remitted(self, reference=None):
        """D1: the rider settlement (M03) or the courier remittance confirms a
        cash-on-delivery collection: the system (the remittance's own
        posting), or a cashier who did not record it, verifies it."""
        user = self.env.user
        for order in self:
            if order.settlement_source != "cod" or order.payment_settlement_state != "settled":
                raise UserError("Order %s has no cash-on-delivery collection." % order.name)
            if order.settlement_verified:
                continue
            if reference and (reference or "").strip() != (order.invoice_ref or ""):
                raise UserError(
                    "Order %s was collected under %s, not %s."
                    % (order.name, order.invoice_ref, reference)
                )
            if not self.env.su:
                if not user.has_group(GROUP_CASHIER):
                    raise UserError("Only a Service Order Cashier confirms a rider's remittance.")
                if user == order.settlement_recorded_by:
                    raise UserError(
                        "Segregation of duties: the person who recorded the collection cannot "
                        "confirm it."
                    )
            order._guarded().write(
                {
                    "settlement_verified": True,
                    "settlement_verified_by": user.id,
                    "settlement_verified_at": fields.Datetime.now(),
                    "amount_verified_bdt": order.amount_settled_bdt,
                }
            )
            order.message_post(
                body="Cash on delivery %s (BDT %.2f) confirmed remitted."
                % (order.invoice_ref, order.amount_settled_bdt)
            )
        return True

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
                "amount_verified_bdt": round(paid + amount, 2),
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
            if order.payment_settlement_state not in ("settled", "partial"):
                continue
            if not order.settlement_verified:
                # a typed TrxID / field claim is not money: void it, refund
                # nothing for it. A part payment verified earlier stays.
                kept = round(order.amount_verified_bdt or 0.0, 2)
                claim = round((order.amount_settled_bdt or 0.0) - kept, 2)
                order._guarded().write(
                    {
                        "payment_settlement_state": "partial" if kept > CENT else "unpaid",
                        "amount_settled_bdt": kept,
                        "settlement_verified": kept > CENT,
                    }
                )
                order.message_post(
                    body="Unverified collection claim %s of BDT %.2f voided on cancellation: "
                    "nothing is refunded for money never verified. Cash a technician really "
                    "holds is accepted by a cashier and refunded by finance."
                    % (order.invoice_ref or "", claim)
                )
                if kept > CENT and not (self.env.su or self.env.user.has_group(GROUP_SUPERVISOR)):
                    raise UserError(
                        "Order %s holds a verified part payment (BDT %.2f): only a Service "
                        "Supervisor cancels it, which refunds the customer." % (order.name, kept)
                    )
            elif not (self.env.su or self.env.user.has_group(GROUP_SUPERVISOR)):
                raise UserError(
                    "Order %s is paid (BDT %.2f): only a Service Supervisor cancels a paid order, "
                    "which refunds the customer." % (order.name, order.amount_settled_bdt)
                )
        return super().action_cancel(reason_code=reason_code, note=note, reason=reason)
