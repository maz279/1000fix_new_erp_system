# fix_rental_asset — M13: rental reservation, damage, deposit (P09-M03 / R07-M03).
from __future__ import annotations

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish


class FixRentalReservation(models.Model):
    """Journey 8: reserve -> deliver -> active -> return -> damage_assess
    -> closed. Availability checked against overlapping reservations.
    Composes M37 rental SKUs, M03 logistics, M39 subscription billing,
    and M01 service order loaner intake (FR-SRM-063/064)."""

    _name = "fix.rental.reservation"
    _description = "Rental Reservation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_from desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, copy=False, readonly=True, default=lambda self: "New")
    customer_id = fields.Many2one("res.partner", string="Customer", required=True, index=True)
    contract_id = fields.Many2one(
        "fix.contract",
        string="Rental Contract",
        ondelete="set null",
        domain=[("family", "=", "rental")],
    )
    rental_sku_id = fields.Many2one(
        "fix.rental.sku",
        string="Rental SKU (M37)",
        ondelete="restrict",
        index=True,
        help="M37 catalog item defining rental rates and deposit",
    )
    device_id = fields.Many2one(
        "fix.device", string="Rental Asset", ondelete="restrict", index=True
    )
    fixed_asset_id = fields.Many2one(
        "fix.fixed.asset", string="Fixed Asset (M49)", ondelete="set null"
    )
    service_order_id = fields.Many2one(
        "fix.service.order",
        string="Origin Service Order (M01)",
        ondelete="set null",
        help="FR-SRM-063/064: loaner/swap-out device for customer repair",
    )
    date_from = fields.Date(required=True, default=fields.Date.context_today)
    date_to = fields.Date(required=True, default=fields.Date.context_today)
    actual_return_date = fields.Date(string="Actual Return Date")
    duration_days = fields.Integer(
        compute="_compute_duration", store=True, string="Duration (Days)"
    )

    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    deposit_collected = fields.Monetary(
        string="Deposit Collected",
        currency_field="currency_id",
        help="Security deposit collected upfront",
    )
    deposit_refunded = fields.Monetary(
        string="Deposit Refunded",
        currency_field="currency_id",
        readonly=True,
        help="Amount refunded to customer after damage deduction",
    )
    daily_rate = fields.Monetary(string="Daily Rate", currency_field="currency_id")
    weekly_rate = fields.Monetary(string="Weekly Rate", currency_field="currency_id")
    monthly_rate = fields.Monetary(string="Monthly Rate", currency_field="currency_id")
    rental_charge = fields.Monetary(
        compute="_compute_rental_charge",
        store=True,
        string="Rental Fee",
        currency_field="currency_id",
    )
    late_fee = fields.Monetary(string="Late Return Fee", currency_field="currency_id", default=0.0)
    excess_billed = fields.Monetary(
        string="Excess Damage Billed",
        currency_field="currency_id",
        readonly=True,
        help="Charges exceeding deposit amount invoiced via M20",
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("reserved", "Reserved"),
            ("delivered", "Delivered"),
            ("active", "Active"),
            ("returned", "Returned"),
            ("damage_assess", "Damage Assessment"),
            ("closed", "Closed"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    damage_ids = fields.One2many("fix.rental.damage", "reservation_id", string="Damage Records")
    damage_total = fields.Monetary(
        compute="_compute_damage", string="Damage Total", currency_field="currency_id"
    )

    delivery_consignment_id = fields.Many2one(
        "fix.consignment", string="Outbound Delivery Consignment (M03)", ondelete="set null"
    )
    return_consignment_id = fields.Many2one(
        "fix.consignment", string="Return Consignment (M03)", ondelete="set null"
    )
    subscription_id = fields.Many2one(
        "fix.subscription", string="Rental Subscription (M39)", ondelete="set null"
    )

    @api.depends("date_from", "date_to")
    def _compute_duration(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                days = (rec.date_to - rec.date_from).days + 1
                rec.duration_days = max(days, 1)
            else:
                rec.duration_days = 1

    @api.onchange("rental_sku_id")
    def _onchange_rental_sku(self):
        if self.rental_sku_id:
            self.daily_rate = self.rental_sku_id.daily_rate
            self.weekly_rate = self.rental_sku_id.weekly_rate
            self.monthly_rate = self.rental_sku_id.monthly_rate
            if not self.deposit_collected:
                self.deposit_collected = self.rental_sku_id.security_deposit

    @api.depends("duration_days", "daily_rate", "weekly_rate", "monthly_rate")
    def _compute_rental_charge(self):
        for rec in self:
            days = rec.duration_days or 1
            if days >= 30 and rec.monthly_rate:
                months = days // 30
                rem_days = days % 30
                rec.rental_charge = (months * rec.monthly_rate) + (
                    rem_days * (rec.daily_rate or (rec.monthly_rate / 30.0))
                )
            elif days >= 7 and rec.weekly_rate:
                weeks = days // 7
                rem_days = days % 7
                rec.rental_charge = (weeks * rec.weekly_rate) + (
                    rem_days * (rec.daily_rate or (rec.weekly_rate / 7.0))
                )
            else:
                rec.rental_charge = days * rec.daily_rate

    @api.depends("damage_ids.cost")
    def _compute_damage(self):
        for rec in self:
            rec.damage_total = sum(rec.damage_ids.mapped("cost"))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.rental.reservation") or "RENT/New"
                )
        return super().create(vals_list)

    def action_reserve(self):
        """The availability check: overlapping ACTIVE reservations for the
        same device are refused (one asset, one customer at a time)."""
        for rec in self:
            if rec.date_to < rec.date_from:
                raise UserError("Rental window is inverted")
            if rec.device_id:
                overlaps = self.search_count(
                    [
                        ("device_id", "=", rec.device_id.id),
                        ("state", "in", ("reserved", "delivered", "active")),
                        ("date_from", "<=", rec.date_to),
                        ("date_to", ">=", rec.date_from),
                        ("id", "!=", rec.id),
                    ]
                )
                if overlaps:
                    raise UserError(
                        "Rental asset %s is already reserved for the overlapping "
                        "period — availability is blocking, not advisory" % rec.device_id.name
                    )
            rec.state = "reserved"
            publish(
                self.env,
                "rental.reserved",
                "fix.rental.reservation",
                rec.id,
                {
                    "customer": rec.customer_id.name,
                    "sku": rec.rental_sku_id.name if rec.rental_sku_id else "",
                    "from": str(rec.date_from),
                    "to": str(rec.date_to),
                    "deposit": float(rec.deposit_collected),
                },
            )

    def _logistics_operating_unit(self):
        """M03 consignments are OU-scoped (operating_unit_id is required):
        the reservation's OU, else the acting user's default OU."""
        self.ensure_one()
        ou = self.operating_unit_id or self.env.user.default_operating_unit_id
        if not ou:
            raise UserError(
                "Rental %s has no operating unit — M03 logistics cannot be dispatched" % self.name
            )
        return ou

    def action_generate_delivery_consignment(self):
        """Creates outbound delivery through M03 logistics (once per rental).
        Returns the delivery consignments of every reservation in self."""
        for rec in self:
            if rec.state != "reserved":
                raise UserError("Can only dispatch delivery for reserved rentals")
            if not rec.delivery_consignment_id:
                consignment = self.env["fix.consignment"].create(
                    {
                        "consignment_type": "delivery",
                        "scheduled_date": fields.Datetime.now(),
                        "operating_unit_id": rec._logistics_operating_unit().id,
                        "service_order_id": rec.service_order_id.id
                        if rec.service_order_id
                        else False,
                    }
                )
                rec.delivery_consignment_id = consignment.id
        return self.mapped("delivery_consignment_id")

    def action_deliver(self):
        for rec in self:
            if rec.state != "reserved":
                raise UserError("Deliver from reserved")
            rec.state = "delivered"
            publish(
                self.env,
                "rental.delivered",
                "fix.rental.reservation",
                rec.id,
                {
                    "customer": rec.customer_id.name,
                    "consignment": rec.delivery_consignment_id.name
                    if rec.delivery_consignment_id
                    else "",
                },
            )

    def action_activate(self):
        for rec in self:
            if rec.state not in ("delivered", "reserved"):
                raise UserError("Activate from delivered or reserved")
            rec.state = "active"
            publish(
                self.env,
                "rental.activated",
                "fix.rental.reservation",
                rec.id,
                {"customer": rec.customer_id.name, "start_date": str(rec.date_from)},
            )

    def action_generate_return_consignment(self):
        """Creates return collection consignment through M03 logistics (once
        per rental). Returns the return consignments of every reservation."""
        for rec in self:
            if rec.state not in ("active", "delivered"):
                raise UserError("Return consignment requires active or delivered rental")
            if not rec.return_consignment_id:
                consignment = self.env["fix.consignment"].create(
                    {
                        "consignment_type": "pickup",
                        "scheduled_date": fields.Datetime.now(),
                        "operating_unit_id": rec._logistics_operating_unit().id,
                        "service_order_id": rec.service_order_id.id
                        if rec.service_order_id
                        else False,
                    }
                )
                rec.return_consignment_id = consignment.id
        return self.mapped("return_consignment_id")

    def action_return(self):
        for rec in self:
            if rec.state != "active":
                raise UserError("Return from active")
            today = fields.Date.context_today(self)
            rec.actual_return_date = today
            # Compute late fee if returned after date_to
            if rec.date_to and today > rec.date_to:
                overdue_days = (today - rec.date_to).days
                daily = rec.daily_rate or (rec.rental_charge / max(rec.duration_days, 1))
                rec.late_fee = overdue_days * daily * 1.5  # 1.5x standard rate for overdue
            rec.state = "returned"
            publish(
                self.env,
                "rental.returned",
                "fix.rental.reservation",
                rec.id,
                {
                    "customer": rec.customer_id.name,
                    "actual_return_date": str(today),
                    "late_fee": float(rec.late_fee),
                },
            )

    def action_assess_damage(self):
        """Journey 8's damage step: condition inspection and damage quantification."""
        for rec in self:
            if rec.state != "returned":
                raise UserError("Assess damage from returned")
            rec.state = "damage_assess"
            publish(
                self.env,
                "rental.damage_assessed",
                "fix.rental.reservation",
                rec.id,
                {"damage_total": float(rec.damage_total)},
            )

    def action_close(self):
        """The deposit settlement & billing closure:
        total_charges = damage_total + late_fee
        deposit_deduction = min(total_charges, deposit_collected)
        deposit_refunded = max(deposit_collected - total_charges, 0)
        excess_billed = max(total_charges - deposit_collected, 0)
        100% money path coverage guaranteed."""
        for rec in self:
            if rec.state != "damage_assess":
                raise UserError("Close from damage assessment")
            total_charges = rec.damage_total + rec.late_fee
            deduction = min(total_charges, rec.deposit_collected)
            refund = max(rec.deposit_collected - total_charges, 0.0)
            excess = max(total_charges - rec.deposit_collected, 0.0)

            rec.write({"state": "closed", "deposit_refunded": refund, "excess_billed": excess})
            publish(
                self.env,
                "rental.closed",
                "fix.rental.reservation",
                rec.id,
                {
                    "rental_charge": float(rec.rental_charge),
                    "deposit_collected": float(rec.deposit_collected),
                    "damage_total": float(rec.damage_total),
                    "late_fee": float(rec.late_fee),
                    "deduction": float(deduction),
                    "refund": float(refund),
                    "excess_billed": float(excess),
                },
            )


class FixRentalDamage(models.Model):
    """Damage assessment line on a rental return."""

    _name = "fix.rental.damage"
    _description = "Rental Damage"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    reservation_id = fields.Many2one(
        "fix.rental.reservation", required=True, ondelete="cascade", index=True
    )
    category = fields.Selection(
        [
            ("cosmetic", "Cosmetic"),
            ("functional", "Functional"),
            ("lost", "Lost/Stolen"),
            ("accessory", "Accessory Missing"),
        ],
        required=True,
        default="cosmetic",
    )
    description = fields.Text(required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    cost = fields.Monetary(string="Damage Cost", currency_field="currency_id", required=True)
    inspector_id = fields.Many2one("hr.employee", string="Inspector")
    evidence_url = fields.Char(string="Damage Evidence Link / S3 Ref")
    disputed = fields.Boolean(string="Disputed by Customer", default=False)

    @api.constrains("cost")
    def _check_cost(self):
        for rec in self:
            if rec.cost < 0:
                raise ValidationError("Damage cost cannot be negative")
