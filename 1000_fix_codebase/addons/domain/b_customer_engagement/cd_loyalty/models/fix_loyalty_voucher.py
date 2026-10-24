# fix_loyalty_voucher — M10 Customer Privilege Vouchers (CD-M10-01).
import secrets

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish


class FixLoyaltyVoucher(models.Model):
    _name = "fix.loyalty.voucher"
    _description = "Loyalty Privilege Voucher"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "valid_until asc, create_date desc"

    # AS-03: Multi-company and Operating Unit discipline
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
        string="Voucher Code",
        required=True,
        copy=False,
        index=True,
        default=lambda self: f"VCH-{secrets.token_hex(4).upper()}",
    )
    account_id = fields.Many2one(
        "fix.loyalty.account",
        string="Loyalty Account",
        ondelete="cascade",
        index=True,
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Customer Party",
        required=True,
        ondelete="restrict",
        index=True,
        tracking=True,
    )
    campaign_id = fields.Many2one(
        "fix.campaign",
        string="Originating Campaign",
        index=True,
    )

    discount_type = fields.Selection(
        [
            ("fixed_bdt", "Fixed BDT Discount"),
            ("percentage", "Percentage Discount (%)"),
        ],
        string="Discount Type",
        default="fixed_bdt",
        required=True,
        tracking=True,
    )
    discount_value = fields.Float(
        string="Discount Value",
        required=True,
        tracking=True,
        help="Amount in BDT (for fixed) or percentage (for percentage).",
    )
    min_spend_bdt = fields.Monetary(
        string="Minimum Order Spend (BDT)",
        currency_field="currency_id",
        default=0.0,
        help="Minimum service order amount before this voucher can be applied.",
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.ref("base.BDT", raise_if_not_found=False)
        or self.env.company.currency_id,
    )

    points_cost = fields.Integer(
        string="Points Burned to Issue",
        default=0,
        help="Loyalty points deducted from customer account upon voucher generation.",
    )
    valid_from = fields.Date(
        string="Valid From",
        default=fields.Date.context_today,
        required=True,
    )
    valid_until = fields.Date(
        string="Valid Until",
        required=True,
        tracking=True,
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active / Usable"),
            ("redeemed", "Redeemed"),
            ("expired", "Expired"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )

    service_order_id = fields.Many2one(
        "fix.service.order",
        string="Redeemed On Service Order",
        index=True,
        copy=False,
    )
    redeemed_at = fields.Datetime(string="Redemption Timestamp", readonly=True)

    _voucher_code_unique = models.Constraint(
        "UNIQUE (name)",
        "Voucher code must be globally unique.",
    )

    @api.constrains("discount_value", "discount_type", "valid_from", "valid_until")
    def _check_voucher_parameters(self):
        for rec in self:
            if rec.discount_value <= 0:
                raise ValidationError("Discount value must be greater than zero.")
            if rec.discount_type == "percentage" and rec.discount_value > 100.0:
                raise ValidationError("Percentage discount cannot exceed 100%.")
            if rec.valid_until < rec.valid_from:
                raise ValidationError(
                    "Voucher validity window is inverted: Valid Until is before Valid From."
                )

    def action_activate(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only draft vouchers can be activated.")
            rec.state = "active"

    def action_redeem(self, service_order):
        """Redeem voucher against a service order with strict validity checks."""
        self.ensure_one()
        if self.state != "active":
            raise UserError(f"Voucher {self.name} cannot be redeemed: status is '{self.state}'.")
        today = fields.Date.today()
        if today < self.valid_from or today > self.valid_until:
            # only a voucher PAST its window is expired; a not-yet-valid one stays
            # usable (it used to be marked expired by an early redemption attempt)
            if today > self.valid_until:
                self.state = "expired"
            raise UserError(
                f"Voucher {self.name} is outside its validity window ({self.valid_from} to {self.valid_until})."
            )

        self.write(
            {
                "state": "redeemed",
                "service_order_id": service_order.id,
                "redeemed_at": fields.Datetime.now(),
            }
        )

        publish(
            self.env,
            "loyalty.voucher_redeemed",
            "fix.loyalty.voucher",
            self.id,
            {
                "voucher_code": self.name,
                "partner_id": self.partner_id.id,
                "service_order_id": service_order.id,
                "discount_type": self.discount_type,
                "discount_value": self.discount_value,
            },
        )

    def action_cancel(self):
        for rec in self:
            if rec.state == "redeemed":
                raise UserError("Cannot cancel an already-redeemed voucher.")
            rec.state = "cancelled"
