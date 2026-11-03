# fix_loyalty_program — M10 Privilege Programme Configuration (CD-M10-01).
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


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

    # --- settings that change what the programme costs (A03 audit M10) ---
    # Each defaults to today's behaviour. Setting them is a business ruling,
    # so only DOFA Tier 3 may change them (see write()).
    expected_breakage_pct = fields.Float(
        string="Expected Breakage % (IFRS 15)",
        default=0.0,
        tracking=True,
        help="The share of outstanding points Finance expects never to be "
        "redeemed. The IFRS 15 liability report carries outstanding points "
        "net of this rate. 0 (the default) reports the full gross liability, "
        "which is what the report did before the rate existed. Setting it is "
        "a Finance decision.",
    )
    referral_referrer_points = fields.Integer(
        string="Referral Award: Referrer (points)",
        default=0,
        tracking=True,
        help="Points posted to the referrer when a referral converts. 0 awards "
        "nothing, as before this setting existed.",
    )
    referral_referee_points = fields.Integer(
        string="Referral Award: New Customer (points)",
        default=0,
        tracking=True,
        help="Points posted to the referred customer on conversion, when they "
        "hold an account in this programme. 0 awards nothing.",
    )

    _COST_SETTINGS = (
        "expected_breakage_pct",
        "referral_referrer_points",
        "referral_referee_points",
    )
    _COST_SETTINGS_GROUP = "cd_entity_config.group_dofa_tier_3"

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

    @api.constrains(*_COST_SETTINGS)
    def _check_cost_settings(self):
        for rec in self:
            if not 0.0 <= rec.expected_breakage_pct <= 100.0:
                raise ValidationError("Expected breakage must be between 0% and 100%.")
            if rec.referral_referrer_points < 0 or rec.referral_referee_points < 0:
                raise ValidationError("A referral award cannot be negative.")

    def _cost_settings_changed(self, vals) -> list:
        changed = []
        for name in set(vals) & set(self._COST_SETTINGS):
            for rec in self:
                if abs((vals[name] or 0) - (rec[name] or 0)) > 1e-6:
                    changed.append(self._fields[name].string)
                    break
        return changed

    def _cost_settings_refuse(self, changed):
        raise UserError(
            "%s can only be changed by a DOFA Tier 3 (Director) holder: the "
            "setting changes what the programme costs." % ", ".join(sorted(changed))
        )

    def _cost_settings_authorised(self) -> bool:
        return self.env.su or self.env.user.has_group(self._COST_SETTINGS_GROUP)

    @api.model_create_multi
    def create(self, vals_list):
        if not self._cost_settings_authorised():
            changed = {
                self._fields[name].string
                for vals in vals_list
                for name in self._COST_SETTINGS
                if vals.get(name)
            }
            if changed:
                self._cost_settings_refuse(changed)
        return super().create(vals_list)

    def write(self, vals):
        # A referral award mints points on every conversion and the breakage
        # rate moves the IFRS 15 liability, so neither is an everyday edit.
        # The P03 form re-posts unchanged values on save; only a change counts.
        if not self._cost_settings_authorised():
            changed = self._cost_settings_changed(vals)
            if changed:
                self._cost_settings_refuse(changed)
        return super().write(vals)

    def breakage_rate(self) -> float:
        """Expected breakage as a fraction (0.0 to 1.0) for the IFRS 15 report."""
        self.ensure_one()
        return max(0.0, min(100.0, self.expected_breakage_pct or 0.0)) / 100.0

    def calculate_points_earned(self, amount_bdt: float, tier=None) -> int:
        """Calculate loyalty points earned on a completed service order."""
        self.ensure_one()
        if amount_bdt <= 0 or not self.active:
            return 0
        base_points = amount_bdt * self.points_per_bdt
        multiplier = tier.points_multiplier if tier else 1.0
        return int(base_points * multiplier)
