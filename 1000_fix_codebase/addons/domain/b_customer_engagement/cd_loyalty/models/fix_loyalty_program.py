# fix_loyalty_program — M10 Privilege Programme Configuration (CD-M10-01).
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FixLoyaltyProgram(models.Model):
    _name = "fix.loyalty.program"
    _description = "Loyalty & Privilege Programme"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    # AS-03: Multi-company & Operating Unit discipline
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

    name = fields.Char(string="Programme Name", required=True, tracking=True)
    name_bn = fields.Char(string="Programme Name (Bengali)", help="DE-17: Localised display name")
    code = fields.Char(string="Programme Code", required=True, index=True, copy=False)
    description = fields.Text(string="Description")
    active = fields.Boolean(default=True, tracking=True)

    # Earning & Redemption parameters
    points_per_bdt = fields.Float(
        string="Points Per BDT Spent",
        default=0.01,
        help="Rate of point accumulation. 0.01 means 1 point earned per 100 BDT spent.",
        tracking=True,
    )
    bdt_per_point = fields.Float(
        string="BDT Value Per Point",
        default=1.0,
        help="Monetary conversion value when redeeming points.",
        tracking=True,
    )
    min_points_to_redeem = fields.Integer(
        string="Minimum Points to Redeem",
        default=100,
        help="Threshold before a customer can apply points toward service invoices.",
    )
    expiry_months = fields.Integer(
        string="Points Expiration Window (Months)",
        default=12,
        help="Unused points expire after this many months from accrual date.",
    )

    # Relationships
    tier_ids = fields.One2many(
        "fix.loyalty.tier",
        "program_id",
        string="Membership Tiers",
    )
    account_ids = fields.One2many(
        "fix.loyalty.account",
        "program_id",
        string="Member Accounts",
    )
    account_count = fields.Integer(
        string="Total Members",
        compute="_compute_account_count",
    )

    _code_unique = models.Constraint(
        "UNIQUE (company_id, code)",
        "Programme code must be unique per company.",
    )

    @api.depends("account_ids")
    def _compute_account_count(self):
        for rec in self:
            rec.account_count = len(rec.account_ids)

    @api.constrains("points_per_bdt", "bdt_per_point")
    def _check_ratios(self):
        for rec in self:
            if rec.points_per_bdt < 0:
                raise ValidationError("Points per BDT cannot be negative.")
            if rec.bdt_per_point <= 0:
                raise ValidationError("BDT value per point must be strictly positive.")

    def calculate_points_earned(self, amount_bdt: float, tier=None) -> int:
        """Calculate loyalty points earned on a completed service order."""
        self.ensure_one()
        if amount_bdt <= 0 or not self.active:
            return 0
        base_points = amount_bdt * self.points_per_bdt
        multiplier = tier.points_multiplier if tier else 1.0
        return int(base_points * multiplier)
