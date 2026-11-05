# M12 chargebacks (A04 workflow audit 2026-11-03 P2 / M12-4; C2-C13 build
# 2026-11-04).
#
# A customer's card or MFS chargeback reverses money already credited to a
# marketplace sale. There was no model for it: the reversal was invisible to
# the seller's payout, and a lost chargeback was never recovered. A chargeback
# is now received -> contested (evidence sent to the gateway) -> won / lost,
# or accepted without contest. While it is open the seller's payout is held
# (BRU-BIL-03); a lost or accepted chargeback publishes
# marketplace.chargeback_lost so M53 recovers it from the seller (C7 bridge).
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from .fix_marketplace import OPERATOR_GROUP, _assert_role

CHARGEBACK_STATES = [
    ("received", "Received"),
    ("contested", "Contested (evidence sent)"),
    ("won", "Won"),
    ("lost", "Lost"),
    ("accepted", "Accepted"),
]
OPEN_CHARGEBACK_STATES = ("received", "contested")
# Card schemes and MFS gateways give about a week to answer; the business
# confirms the window per gateway (DEFAULT THE BUSINESS MUST CONFIRM).
RESPONSE_DAYS = 7


class FixMarketplaceChargeback(models.Model):
    _name = "fix.marketplace.chargeback"
    _description = "Marketplace Chargeback"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "received_on desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    name = fields.Char(
        string="Chargeback Reference", required=True, copy=False, readonly=True, default="CB/New"
    )
    order_id = fields.Many2one(
        "fix.marketplace.order", string="Marketplace Order", required=True, index=True
    )
    seller_id = fields.Many2one(
        "fix.marketplace.seller",
        string="Seller",
        compute="_compute_parties",
        store=True,
        index=True,
    )
    customer_id = fields.Many2one(
        "res.partner", string="Customer", compute="_compute_parties", store=True
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(currency_field="currency_id", required=True)
    reason = fields.Selection(
        [
            ("fraud", "Fraud / Unauthorised Payment"),
            ("not_received", "Service Not Received"),
            ("not_as_described", "Not as Described"),
            ("duplicate", "Duplicate Charge"),
            ("other", "Other"),
        ],
        required=True,
        default="other",
    )
    gateway_ref = fields.Char(string="Gateway Case Reference", required=True)
    received_on = fields.Date(required=True, default=fields.Date.context_today)
    respond_by = fields.Date(compute="_compute_respond_by", store=True)
    state = fields.Selection(
        CHARGEBACK_STATES, default="received", required=True, readonly=True, tracking=True
    )
    evidence_note = fields.Text(readonly=True)
    outcome_note = fields.Text(readonly=True)
    decided_by_id = fields.Many2one("res.users", string="Outcome Recorded By", readonly=True)
    decided_at = fields.Datetime(readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "evidence_note",
            "outcome_note",
            "decided_by_id",
            "decided_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id:
            locked |= {"order_id", "amount", "currency_id", "gateway_ref", "received_on"}
        return locked

    @api.depends("order_id.selected_quote_id.seller_id", "order_id.customer_id")
    def _compute_parties(self):
        for rec in self:
            rec.seller_id = rec.order_id.selected_quote_id.seller_id
            rec.customer_id = rec.order_id.customer_id

    @api.depends("received_on")
    def _compute_respond_by(self):
        for rec in self:
            rec.respond_by = (
                rec.received_on + timedelta(days=RESPONSE_DAYS) if rec.received_on else False
            )

    @api.constrains("amount", "order_id")
    def _check_amount(self):
        for rec in self:
            order = rec.order_id
            if rec.amount <= 0:
                raise ValidationError("A chargeback is a positive amount.")
            if not order.selected_quote_id:
                raise ValidationError(
                    "Order %s was never awarded: there is no sale to charge back." % order.name
                )
            ceiling = order.awarded_price or order.selected_quote_id.quoted_price
            if ceiling and rec.amount > ceiling + 0.005:
                raise ValidationError(
                    "A chargeback of %.2f exceeds what order %s was sold for (%.2f)."
                    % (rec.amount, order.name, ceiling)
                )

    @api.model_create_multi
    def create(self, vals_list):
        _assert_role(self.env, OPERATOR_GROUP, "Recording a chargeback")
        recs = super().create(vals_list)
        for rec in recs:
            rec._guarded().write({"name": "CB/%05d" % rec.id})
            rec.seller_id._recompute_payout_hold()
            publish(
                self.env,
                "marketplace.chargeback_received",
                "fix.marketplace.chargeback",
                rec.id,
                {
                    "chargeback": rec.name,
                    "order_id": rec.order_id.id,
                    "seller_id": rec.seller_id.id,
                    "amount": float(rec.amount),
                    "currency": rec.currency_id.name or "BDT",
                    "gateway_ref": rec.gateway_ref,
                    "respond_by": str(rec.respond_by or ""),
                },
            )
        return recs

    def write(self, vals):
        if self and not self._fix_guard_open():
            fixed = {"order_id", "amount", "currency_id", "gateway_ref", "received_on"}
            for rec in self:
                if any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in fixed & set(vals)):
                    raise UserError(
                        "A chargeback keeps the order, amount and gateway case it was received "
                        "with; record a new one."
                    )
                if rec.state not in OPEN_CHARGEBACK_STATES and set(vals) - {"reason"}:
                    raise UserError("Chargeback %s is decided and closed." % rec.name)
        return super().write(vals)

    def action_submit_evidence(self, note=None):
        """The seller's evidence (job record, delivery confirmation) goes to
        the gateway."""
        for rec in self:
            _assert_role(self.env, OPERATOR_GROUP, "Contesting a chargeback")
            if rec.state != "received":
                raise UserError("Only a received chargeback is contested.")
            if not (note or "").strip():
                raise UserError("Say what evidence was sent to the gateway.")
            rec._guarded().write({"state": "contested", "evidence_note": note})
        return True

    def _close(self, state, note):
        if not (note or "").strip():
            raise UserError("Record the gateway's outcome (case note or reference).")
        for rec in self:
            _assert_role(self.env, OPERATOR_GROUP, "Recording a chargeback outcome")
            allowed = ("contested",) if state in ("won", "lost") else OPEN_CHARGEBACK_STATES
            if rec.state not in allowed:
                raise UserError(
                    "Chargeback %s is %s: it cannot become %s." % (rec.name, rec.state, state)
                )
            rec._guarded().write(
                {
                    "state": state,
                    "outcome_note": note,
                    "decided_by_id": self.env.uid,
                    "decided_at": fields.Datetime.now(),
                }
            )
            rec.seller_id._recompute_payout_hold()
            if state in ("lost", "accepted"):
                publish(
                    self.env,
                    "marketplace.chargeback_lost",
                    "fix.marketplace.chargeback",
                    rec.id,
                    {
                        "chargeback": rec.name,
                        "order_id": rec.order_id.id,
                        "seller_id": rec.seller_id.id,
                        "seller_partner_id": rec.seller_id.partner_id.id,
                        "customer_id": rec.customer_id.id,
                        "amount": float(rec.amount),
                        "currency": rec.currency_id.name or "BDT",
                        "outcome": state,
                    },
                )
        return True

    def action_mark_won(self, note=None):
        return self._close("won", note)

    def action_mark_lost(self, note=None):
        return self._close("lost", note)

    def action_accept(self, note=None):
        """Accept liability without contesting."""
        return self._close("accepted", note)
