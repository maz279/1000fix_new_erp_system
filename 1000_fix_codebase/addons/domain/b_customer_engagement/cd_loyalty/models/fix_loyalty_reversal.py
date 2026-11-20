# Points earned on a service order are taken back when its invoice is
# credited or cancelled (A02 ERP pass 2, X5-09 / owner decision D25).
#
# FR-LOY-020 / BRU-LOY-05 / AUT-LOY-04: "points earned on a transaction are
# reversed automatically if that transaction is cancelled, refunded or charged
# back". A closed order earned through service_order.closed and nothing ever
# took the points back: M20 published credit_note.issued and invoice.cancelled
# and nobody consumed them, so a refunded repair kept its points.
#
# The reversal is a compensating ledger line (BRU-LOY-04: append-only), of its
# own type so it is neither a manual adjustment (it would need DOFA approval
# the relay cannot give) nor a redemption (it is not points the member
# spent). It takes back the earned points in the proportion of the invoice
# credited - cumulatively, so several partial credit notes never take back
# more than was earned - and all that is left on a cancellation. Points the
# member has already spent or that lapsed are not taken twice: the take-back
# stops at the wallet balance and the shortfall is recorded on the receipt.
from odoo import api, fields, models
from odoo.exceptions import ValidationError

from libs.py.fix_events import publish

CLAWBACK = "clawback"


class FixLoyaltyLedgerClawback(models.Model):
    _inherit = "fix.loyalty.ledger"

    transaction_type = fields.Selection(
        selection_add=[(CLAWBACK, "Earn Reversal (credit note / cancellation)")],
        ondelete={CLAWBACK: "cascade"},
    )

    @api.constrains("transaction_type", "points", "system_generated")
    def _check_clawback(self):
        for rec in self.filtered(lambda r: r.transaction_type == CLAWBACK):
            if rec.points > 0:
                raise ValidationError("An earn reversal removes points: its points are negative.")
            if not rec.system_generated:
                raise ValidationError(
                    "An earn reversal is raised by the credit note or cancellation itself, "
                    "not keyed in. Use a Customer Care Adjustment for a manual correction."
                )


class FixLoyaltyAccountReversal(models.Model):
    _inherit = "fix.loyalty.account"

    # ------------------------------------------------------------------ helpers
    @api.model
    def _reversal_order(self, invoice):
        """The service order an M20 invoice billed, or None."""
        if not invoice or invoice.source_model != "fix.service.order" or not invoice.source_id:
            return None
        return self.env["fix.service.order"].sudo().browse(invoice.source_id).exists() or None

    def _earned_on_order(self, order):
        """(points still standing from this order's earn, points already taken
        back) for this account."""
        self.ensure_one()
        Ledger = self.env["fix.loyalty.ledger"].sudo()
        earned = Ledger.search(
            [
                ("account_id", "=", self.id),
                ("service_order_id", "=", order.id),
                ("transaction_type", "=", "accrual"),
                ("state", "=", "posted"),
                ("points", ">", 0),
                ("points_expired", "=", False),
            ]
        )
        taken = Ledger.search(
            [
                ("account_id", "=", self.id),
                ("service_order_id", "=", order.id),
                ("transaction_type", "=", CLAWBACK),
                ("state", "in", ("draft", "posted")),
            ]
        )
        return sum(earned.mapped("points")), -sum(taken.mapped("points"))

    def _claw_back(self, order, share, key, event, why):
        """Take back ``share`` (0..1, cumulative) of what this account earned on
        ``order``. Returns the points taken back."""
        self.ensure_one()
        Receipt = self.env["fix.loyalty.event.receipt"]
        if Receipt._seen(key):
            return 0
        earned, taken = self._earned_on_order(order)
        target = min(earned, int(round(earned * min(max(share, 0.0), 1.0))))
        due = target - taken
        if due <= 0:
            Receipt._record(key, event, "Nothing to take back (%s)." % why, self)
            return 0
        balance = self.points_balance
        points = min(due, max(balance, 0))
        if points <= 0:
            Receipt._record(
                key,
                event,
                "%d points due back (%s) but the wallet holds none: already spent or lapsed."
                % (due, why),
                self,
            )
            return 0
        line = (
            self.env["fix.loyalty.ledger"]
            .sudo()
            .create(
                {
                    "account_id": self.id,
                    "transaction_type": CLAWBACK,
                    "points": -points,
                    "service_order_id": order.id,
                    "company_id": self.company_id.id,
                    "operating_unit_id": (
                        order.operating_unit_id or order.branch_id.operating_unit_id
                    ).id,
                    "notes": "Earn on %s reversed: %s (FR-LOY-020, BRU-LOY-05)."
                    % (order.name, why),
                }
            )
        )
        short = due - points
        outcome = "Took back %d points (%s)." % (points, why)
        if short:
            outcome += " %d more were due but already spent or lapsed." % short
        if self.state != "active":
            Receipt._record(
                key,
                event,
                "Held as draft: the account is %s. %s" % (self.state, outcome),
                self,
                line,
            )
            return 0
        line.action_post()
        # action_post books a negative line as points the member REDEEMED; an
        # earn reversal is points never earned, so the accumulators say so.
        account = self.sudo()
        account._guarded().write(
            {
                "lifetime_points_redeemed": max(account.lifetime_points_redeemed - points, 0),
                "lifetime_points_earned": max(account.lifetime_points_earned - points, 0),
            }
        )
        Receipt._record(key, event, outcome, self, line)
        publish(
            self.env,
            "points.reversed",
            "fix.loyalty.ledger",
            line.id,
            {
                "account_no": self.name,
                "partner_id": self.partner_id.id,
                "points": points,
                "reason": why,
                "source": order.name,
            },
        )
        return points

    @api.model
    def _reverse_for_invoice(self, invoice, share, key_prefix, event, why):
        order = self._reversal_order(invoice)
        if not order:
            return {"reversed": 0, "reason": "the invoice is not a service order's"}
        accounts = self.sudo().search([("partner_id", "=", order.customer_id.id)])
        reversed_points = 0
        for account in accounts:
            reversed_points += account._claw_back(
                order, share, "%s:%d" % (key_prefix, account.id), event, why
            )
        return {"reversed": reversed_points, "order": order.name}

    # ---------------------------------------------------------------- consumers
    @api.model
    def consume_credit_note_issued(self, event: dict) -> dict:
        """R8 consumer of credit_note.issued: take back the credited share."""
        self._assert_system_consumer()
        note_id = event.get("aggregate_id")
        Note = self.env["fix.credit.note"].sudo()
        note = Note.browse(int(note_id or 0)).exists()
        if not note or note.state != "issued":
            return {"reversed": 0, "reason": "not an issued credit note"}
        invoice = note.invoice_id
        gross = invoice.total_payable or 0.0
        if gross <= 0.005:
            return {"reversed": 0, "reason": "the invoice has no value"}
        credited = sum(
            Note.search([("invoice_id", "=", invoice.id), ("state", "=", "issued")]).mapped(
                "amount"
            )
        )
        return self._reverse_for_invoice(
            invoice,
            credited / gross,
            "clawback:credit_note:%d" % note.id,
            event,
            "credit note %s on %s" % (note.display_name, invoice.name),
        )

    @api.model
    def consume_invoice_cancelled(self, event: dict) -> dict:
        """R8 consumer of invoice.cancelled: take back what is left."""
        self._assert_system_consumer()
        invoice = self.env["fix.ar.invoice"].sudo().browse(int(event.get("aggregate_id") or 0))
        invoice = invoice.exists()
        if not invoice or invoice.state != "cancelled":
            return {"reversed": 0, "reason": "not a cancelled invoice"}
        return self._reverse_for_invoice(
            invoice,
            1.0,
            "clawback:invoice_cancelled:%d" % invoice.id,
            event,
            "invoice %s cancelled" % invoice.name,
        )
