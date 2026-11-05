# M38 storefront operations: RMA requests and storefront/delivery slots.
# Carts, cart lines and graded refurb stock already live in cd_storefront.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_storefront_refund import GROUP_OPERATOR


class FixStorefrontRma(models.Model):
    """A04 workflow audit (2026-11-03) M38-13: this second RMA model was a
    duplicate of fix.storefront.return with none of its rules: no order, no
    cap, no sequence (every RMA was "New"), a free-text credit note and
    self-approval. It now shares the return's refund lifecycle
    (fix.storefront.refund.mixin): an order, the cap, the return window, the
    inspection, a routed DOFA refund approval and the M20 credit note."""

    _name = "fix.storefront.rma"
    _description = "Storefront RMA Request"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.storefront.refund.mixin"]
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
    requested_on = fields.Date(required=True, default=fields.Date.context_today)
    refund_amount = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    note = fields.Char()

    _credit_note_unique = models.UniqueIndex(
        "(credit_note_id) WHERE credit_note_id IS NOT NULL",
        "This credit note already pays another storefront RMA.",
    )

    def _sf_change_of_mind(self) -> bool:
        return self.reason == "change_of_mind"

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self[:1] and self[:1].state != "requested":
            locked |= {"requested_on"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.storefront.rma") or "New"
        return super().create(vals_list)

    def action_receive(self, condition=None):
        """The RMA's receive step is the shared receive-and-inspect: an item
        is received with its inspection result."""
        return self.action_receive_and_inspect(condition=condition)

    def action_refund(self, credit_note_ref=""):
        """The RMA completes on its M20 credit note, never on a typed
        reference (A04 audit M38-7): see action_record_credit_note."""
        return self.action_record_credit_note(credit_note=credit_note_ref)


class FixStorefrontSlot(models.Model):
    """A04 workflow audit (2026-11-03) M38-8: the slot was a standalone table
    whose `booked` count anyone typed (50 against a capacity of 10). Its
    bookings are now its orders, counted by the server and never above the
    capacity; the state follows from them, and closing a slot is an
    operator's action."""

    _name = "fix.storefront.slot"
    _description = "Storefront / Delivery Slot"
    _inherit = ["fix.guarded.mixin"]
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
    order_ids = fields.One2many("fix.storefront.order", "slot_id", string="Booked Orders")
    booked = fields.Integer(compute="_compute_booked", store=True, readonly=True)
    is_closed = fields.Boolean(string="Closed", readonly=True, copy=False)
    state = fields.Selection(
        [("open", "Open"), ("full", "Full"), ("closed", "Closed")],
        required=True,
        default="open",
        compute="_compute_booked",
        store=True,
        readonly=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"booked", "state", "is_closed"}

    @api.depends("order_ids.state", "capacity", "is_closed")
    def _compute_booked(self):
        for slot in self:
            slot.booked = len(slot.order_ids.filtered(lambda o: o.state != "cancelled"))
            if slot.is_closed:
                slot.state = "closed"
            elif slot.booked >= slot.capacity:
                slot.state = "full"
            else:
                slot.state = "open"

    @api.constrains("capacity", "start_hour", "end_hour", "booked")
    def _check_slot(self):
        for slot in self:
            if slot.capacity <= 0:
                raise ValidationError("A slot's capacity must be positive.")
            if not (0 <= slot.start_hour < slot.end_hour <= 24):
                raise ValidationError("A slot runs from its start hour to a later end hour.")
            if slot.booked > slot.capacity:
                raise ValidationError(
                    "Slot %s holds %d bookings: above its capacity of %d."
                    % (slot.name, slot.booked, slot.capacity)
                )

    def _sf_assert_bookable(self):
        for slot in self:
            if not slot.exists():
                raise UserError("That delivery slot does not exist.")
            if slot.state != "open":
                raise UserError(
                    "Slot %s is %s: it takes no more bookings." % (slot.name, slot.state)
                )
            if slot.slot_date and slot.slot_date < fields.Date.context_today(slot):
                raise UserError("Slot %s is in the past." % slot.name)

    def action_close(self):
        if not (self.env.su or self.env.user.has_group(GROUP_OPERATOR)):
            raise UserError("Closing a slot needs the Storefront Operator role.")
        self._guarded().write({"is_closed": True})
        return True

    def action_reopen(self):
        if not (self.env.su or self.env.user.has_group(GROUP_OPERATOR)):
            raise UserError("Reopening a slot needs the Storefront Operator role.")
        self._guarded().write({"is_closed": False})
        return True
