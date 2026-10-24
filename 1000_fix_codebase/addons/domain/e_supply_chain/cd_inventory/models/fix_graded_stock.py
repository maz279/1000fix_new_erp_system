# cd_inventory — Graded Stock & Refurbished Inventory Valuation (M15 / P09-M04-T08 / R07-M03-T03).
from __future__ import annotations

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish


class FixGradedStock(models.Model):
    """Refurbished and graded device stock in M15 inventory with grade-aware valuation.
    Valuation = Acquisition Cost (Trade-In offer) + Refurbishment Cost (Parts + Labour).
    A financial inventory path ensuring margin visibility per device."""

    _name = "fix.graded.stock"
    _description = "Graded & Refurbished Inventory"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc, id desc"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Operating Unit",
        index=True,
    )
    name = fields.Char(
        string="Stock Tag / Serial",
        required=True,
        copy=False,
        default="New",
        index=True,
    )
    device_id = fields.Many2one(
        "fix.device",
        string="Device Serial",
        required=True,
        index=True,
        ondelete="restrict",
    )
    tradein_id = fields.Integer(
        string="Originating Trade-In ID",
        index=True,
    )
    tradein_ref = fields.Char(
        string="Originating Trade-In Ref",
        index=True,
    )

    grade_id = fields.Many2one(
        "fix.refurb.grade",
        string="Refurbishment Grade",
        required=True,
        index=True,
        help="Grade A/B/C/D/E determining resale pricing and warranty",
    )
    location_id = fields.Many2one(
        "fix.stock.location",
        string="Warehouse Location",
        index=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        default=lambda self: self.env.ref("base.BDT"),
    )

    # Financial valuation fields (AS-10 Monetary)
    acquisition_cost = fields.Monetary(
        string="Acquisition Cost (Trade-In)",
        currency_field="currency_id",
        required=True,
        default=0.0,
        help="Price paid to customer during trade-in intake",
    )
    refurbishment_cost = fields.Monetary(
        string="Refurbishment Cost",
        currency_field="currency_id",
        default=0.0,
        help="Parts consumed and labour costs during workshop repair",
    )
    inventory_valuation = fields.Monetary(
        string="Inventory Valuation",
        currency_field="currency_id",
        compute="_compute_valuation",
        store=True,
        help="Total capitalized inventory cost: Acquisition + Refurbishment",
    )
    resale_price = fields.Monetary(
        string="Target Resale Price",
        currency_field="currency_id",
        required=True,
        default=0.0,
    )
    projected_margin = fields.Monetary(
        string="Projected Margin",
        currency_field="currency_id",
        compute="_compute_margin",
        store=True,
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_stock", "In Stock (Available)"),
            ("reserved", "Reserved"),
            ("sold", "Sold / Delivered"),
            ("scrapped", "Scrapped / E-Waste"),
        ],
        string="Inventory Status",
        default="in_stock",
        required=True,
        tracking=True,
    )

    @api.depends("acquisition_cost", "refurbishment_cost")
    def _compute_valuation(self):
        for rec in self:
            rec.inventory_valuation = (rec.acquisition_cost or 0.0) + (
                rec.refurbishment_cost or 0.0
            )

    @api.depends("resale_price", "inventory_valuation")
    def _compute_margin(self):
        for rec in self:
            rec.projected_margin = (rec.resale_price or 0.0) - (rec.inventory_valuation or 0.0)

    @api.constrains("acquisition_cost", "refurbishment_cost", "resale_price")
    def _check_financial_amounts(self):
        for rec in self:
            if rec.acquisition_cost < 0:
                raise ValidationError("Acquisition cost cannot be negative")
            if rec.refurbishment_cost < 0:
                raise ValidationError("Refurbishment cost cannot be negative")
            if rec.resale_price < 0:
                raise ValidationError("Resale price cannot be negative")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.graded.stock") or "STK/GRD/New"
                )
        return super().create(vals_list)

    def action_reserve(self):
        for rec in self:
            if rec.state != "in_stock":
                raise UserError("Only in-stock items can be reserved")
            rec.state = "reserved"

    def action_sell(self):
        for rec in self:
            if rec.state not in ("in_stock", "reserved"):
                raise UserError("Only in-stock or reserved items can be sold")
            rec.state = "sold"
            publish(
                self.env,
                "graded_stock.sold",
                "fix.graded.stock",
                rec.id,
                {
                    "device": rec.device_id.name if rec.device_id else "",
                    "grade": rec.grade_id.code if rec.grade_id else "",
                    "valuation": float(rec.inventory_valuation),
                    "resale_price": float(rec.resale_price),
                    "margin": float(rec.projected_margin),
                },
            )
