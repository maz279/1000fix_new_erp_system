# fix_loyalty_tier — M10 Privilege Membership Tiers (CD-M10-01).
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FixLoyaltyTier(models.Model):
    _name = "fix.loyalty.tier"
    _description = "Loyalty Membership Tier"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence asc, min_points_threshold asc"

    # AS-03: Company and Operating Unit scoping
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

    program_id = fields.Many2one(
        "fix.loyalty.program",
        string="Loyalty Programme",
        required=True,
        ondelete="cascade",
        index=True,
    )
    name = fields.Char(string="Tier Name", required=True, tracking=True)
    name_bn = fields.Char(string="Tier Name (Bengali)", help="DE-17: Localised display name")
    code = fields.Char(string="Tier Code", required=True, index=True)
    sequence = fields.Integer(default=10, help="Evaluation and display order")
    active = fields.Boolean(default=True, tracking=True)

    # Qualification criteria
    min_points_threshold = fields.Integer(
        string="Minimum Points Required",
        default=0,
        help="Lifetime points required to achieve or maintain this tier.",
        tracking=True,
    )
    min_spend_bdt = fields.Monetary(
        string="Minimum Spend (BDT)",
        currency_field="currency_id",
        default=0.0,
        help="Alternative spend-based threshold for tier qualification.",
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.ref("base.BDT", raise_if_not_found=False) or self.env.company.currency_id,
    )

    # Benefits
    points_multiplier = fields.Float(
        string="Points Multiplier",
        default=1.0,
        help="Bonus multiplier on base points earned (e.g., 1.5x for Gold).",
        tracking=True,
    )
    labour_discount_pct = fields.Float(
        string="Labour Discount (%)",
        default=0.0,
        help="Discount percentage applied to repair labour estimates.",
        tracking=True,
    )
    parts_discount_pct = fields.Float(
        string="Parts Discount (%)",
        default=0.0,
        help="Discount percentage applied to spare parts prices.",
        tracking=True,
    )
    priority_diagnostic = fields.Boolean(
        string="Priority Diagnostics",
        default=False,
        help="Queue diagnostic jobs with expedited priority.",
    )
    dedicated_support = fields.Boolean(
        string="Dedicated Support Line",
        default=False,
        help="Direct VIP queue routing at contact centre.",
    )

    _tier_code_unique = models.Constraint(
        "UNIQUE (program_id, code)",
        "Tier code must be unique within a loyalty programme.",
    )

    @api.constrains("points_multiplier", "labour_discount_pct", "parts_discount_pct")
    def _check_benefits(self):
        for rec in self:
            if rec.points_multiplier < 1.0:
                raise ValidationError("Points multiplier must be at least 1.0x.")
            if not (0.0 <= rec.labour_discount_pct <= 100.0):
                raise ValidationError("Labour discount must be between 0% and 100%.")
            if not (0.0 <= rec.parts_discount_pct <= 100.0):
                raise ValidationError("Parts discount must be between 0% and 100%.")
