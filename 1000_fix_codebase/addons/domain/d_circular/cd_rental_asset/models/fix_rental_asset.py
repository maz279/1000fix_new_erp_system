# fix_rental_asset — M13: rental reservation, damage, deposit (P09-M03).
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish


class FixRentalReservation(models.Model):
    """Journey 8: reserve -> deliver -> active -> return -> damage_assess
    -> closed. Availability checked against overlapping reservations."""
    _name = "fix.rental.reservation"
    _description = "Rental Reservation"
    # P03 workspace data-entry form (discovered by cd_p03_portal).
    _p03_capture = {
        "module": "M13",
        "form": "Reservation",
        "fields": ["customer_id", "date_from", "date_to", "contract_id", "device_id",
                   "fixed_asset_id", "deposit_collected", "daily_rate"],
    }
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_from desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, copy=False, readonly=True,
                       default=lambda self: "New")
    customer_id = fields.Many2one("res.partner", string="Customer",
                                  required=True, index=True)
    contract_id = fields.Many2one("fix.contract", string="Rental Contract",
                                  ondelete="set null",
                                  domain=[("family", "=", "rental")])
    device_id = fields.Many2one("fix.device", string="Rental Asset",
                                ondelete="restrict")
    fixed_asset_id = fields.Many2one("fix.fixed.asset",
                                     string="Fixed Asset (M49)",
                                     ondelete="set null")
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    deposit_collected = fields.Monetary(string="Deposit Collected",
                                        currency_field="currency_id")
    deposit_refunded = fields.Monetary(string="Deposit Refunded",
                                       currency_field="currency_id",
                                       readonly=True)
    daily_rate = fields.Monetary(string="Daily Rate",
                                 currency_field="currency_id")
    state = fields.Selection(
        [("draft", "Draft"), ("reserved", "Reserved"), ("delivered", "Delivered"),
         ("active", "Active"), ("returned", "Returned"),
         ("damage_assess", "Damage Assessment"), ("closed", "Closed"),
         ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True)
    damage_ids = fields.One2many("fix.rental.damage", "reservation_id",
                                 string="Damage Records")
    damage_total = fields.Monetary(compute="_compute_damage",
                                   string="Damage Total",
                                   currency_field="currency_id")

    @api.depends("damage_ids.cost")
    def _compute_damage(self):
        for rec in self:
            rec.damage_total = sum(rec.damage_ids.mapped("cost"))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "fix.rental.reservation") or "RENT/New"
        return super().create(vals_list)

    def action_reserve(self):
        """The availability check: overlapping ACTIVE reservations for the
        same device are refused (one asset, one customer at a time)."""
        for rec in self:
            if rec.date_to < rec.date_from:
                raise UserError("Rental window is inverted")
            overlaps = self.search_count([
                ("device_id", "=", rec.device_id.id),
                ("state", "in", ("reserved", "delivered", "active")),
                ("date_from", "<=", rec.date_to),
                ("date_to", ">=", rec.date_from),
                ("id", "!=", rec.id)])
            if overlaps:
                raise UserError(
                    "Rental asset %s is already reserved for the overlapping "
                    "period — availability is blocking, not advisory"
                    % rec.device_id.name)
            rec.state = "reserved"
            publish(self.env, "rental.reserved", "fix.rental.reservation",
                    rec.id, {"customer": rec.customer_id.name,
                             "from": str(rec.date_from),
                             "to": str(rec.date_to)})

    def action_deliver(self):
        for rec in self:
            if rec.state != "reserved":
                raise UserError("Deliver from reserved")
            rec.state = "delivered"
            publish(self.env, "rental.delivered", "fix.rental.reservation",
                    rec.id, {"customer": rec.customer_id.name})

    def action_activate(self):
        for rec in self:
            rec.state = "active"

    def action_return(self):
        for rec in self:
            if rec.state != "active":
                raise UserError("Return from active")
            rec.state = "returned"

    def action_assess_damage(self):
        """Journey 8's damage step: the deposit deduction is decided here."""
        for rec in self:
            if rec.state != "returned":
                raise UserError("Assess damage from returned")
            rec.state = "damage_assess"

    def action_close(self):
        """The deposit settlement: refund = collected - damage_total."""
        for rec in self:
            if rec.state != "damage_assess":
                raise UserError("Close from damage assessment")
            deduction = rec.damage_total
            refund = max(rec.deposit_collected - deduction, 0)
            rec.write({"state": "closed", "deposit_refunded": refund})
            publish(self.env, "rental.closed", "fix.rental.reservation",
                    rec.id, {"damage": float(deduction),
                             "refund": float(refund)})


class FixRentalDamage(models.Model):
    """Damage assessment line on a rental return."""
    _name = "fix.rental.damage"
    _description = "Rental Damage"
    # P03 workspace data-entry form (discovered by cd_p03_portal).
    _p03_capture = {
        "module": "M13",
        "form": "Damage Assessment",
        "fields": ["reservation_id", "category", "description", "cost"],
    }
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    reservation_id = fields.Many2one("fix.rental.reservation", required=True,
                                     ondelete="cascade", index=True)
    category = fields.Selection(
        [("cosmetic", "Cosmetic"), ("functional", "Functional"),
         ("lost", "Lost/Stolen"), ("accessory", "Accessory Missing")],
        required=True, default="cosmetic")
    description = fields.Text(required=True)
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    cost = fields.Monetary(string="Damage Cost", currency_field="currency_id",
                           required=True)

    @api.constrains("cost")
    def _check_cost(self):
        for rec in self:
            if rec.cost < 0:
                raise UserError("Damage cost cannot be negative")
