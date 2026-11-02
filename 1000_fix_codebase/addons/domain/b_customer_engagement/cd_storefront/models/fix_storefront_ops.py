# M38 storefront operations: RMA requests and storefront/delivery slots.
# Carts, cart lines and graded refurb stock already live in cd_storefront.
from odoo import fields, models
from odoo.exceptions import UserError


class FixStorefrontRma(models.Model):
    _name = "fix.storefront.rma"
    _description = "Storefront RMA Request"
    _order = "requested_on desc, id desc"

    name = fields.Char(required=True, copy=False, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    customer_id = fields.Many2one(
        "res.partner", string="Customer", required=True, ondelete="restrict"
    )
    order_id = fields.Many2one("fix.storefront.order", string="Storefront Order")
    reason = fields.Selection(
        [
            ("doa", "Dead on arrival"),
            ("not_as_described", "Not as described"),
            ("wrong_item", "Wrong item"),
            ("change_of_mind", "Change of mind"),
            ("warranty", "Warranty fault"),
        ],
        required=True,
        default="warranty",
    )
    requested_on = fields.Date(required=True)
    refund_amount = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    state = fields.Selection(
        [
            ("requested", "Requested"),
            ("approved", "Approved"),
            ("received", "Item received"),
            ("refunded", "Refunded"),
            ("rejected", "Rejected"),
        ],
        required=True,
        default="requested",
    )
    note = fields.Char()

    # RMA lifecycle (A04 zero-trust audit 2026-10-31, DISC-38.2): the model was
    # a passive duplicate. Governed transitions: approval requires a positive
    # refund amount; a refund completes only with a Mushak 6.7 credit-note
    # reference (issued by M20 billing) recorded on the note.
    def action_approve(self):
        for rec in self:
            if rec.state != "requested":
                raise UserError(
                    "RMA %s is %s — only a requested RMA can be approved" % (rec.name, rec.state)
                )
            if (rec.refund_amount or 0.0) <= 0.0:
                raise UserError(
                    "RMA %s: a positive refund amount is required before approval" % rec.name
                )
            rec.state = "approved"

    def action_receive(self):
        for rec in self:
            if rec.state != "approved":
                raise UserError("RMA %s: the item can only be received after approval" % rec.name)
            rec.state = "received"

    def action_refund(self, credit_note_ref=""):
        for rec in self:
            if rec.state != "received":
                raise UserError("RMA %s: refund executes after the item is received" % rec.name)
            if not (credit_note_ref or "").strip():
                raise UserError(
                    "RMA %s: Mushak 6.7 credit-note reference from M20 billing is "
                    "required to execute the refund (VAT Act 2012)" % rec.name
                )
            rec.write(
                {
                    "state": "refunded",
                    "note": ((rec.note or "") + " | Mushak 6.7: " + credit_note_ref).strip(" |"),
                }
            )

    def action_reject(self, reason=""):
        for rec in self:
            if rec.state in ("refunded", "rejected"):
                raise UserError("RMA %s is already closed (%s)" % (rec.name, rec.state))
            rec.write({"state": "rejected", "note": reason or rec.note})


class FixStorefrontSlot(models.Model):
    _name = "fix.storefront.slot"
    _description = "Storefront / Delivery Slot"
    _order = "slot_date, start_hour"

    name = fields.Char(required=True)
    slot_type = fields.Selection(
        [("storefront", "Storefront pickup slot"), ("delivery", "Delivery slot")],
        required=True,
        default="delivery",
    )
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    slot_date = fields.Date(required=True)
    start_hour = fields.Integer(required=True, default=10)
    end_hour = fields.Integer(required=True, default=13)
    capacity = fields.Integer(required=True, default=10)
    booked = fields.Integer(default=0)
    state = fields.Selection(
        [("open", "Open"), ("full", "Full"), ("closed", "Closed")],
        required=True,
        default="open",
    )
