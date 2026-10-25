# fix_asset_master — M49 master data: asset categories (posting accounts,
# useful life, tax class) and the effective-dated tax depreciation rates of
# the ITA 2023 Third Schedule (reducing balance). The seeded rates are NOT
# verified against the primary NBR text: each row carries "verify with the
# company's tax adviser" until someone ticks Verified.
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FixAssetCategory(models.Model):
    _name = "fix.asset.category"
    _description = "Asset Category"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code, name"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Restricted to Branch",
        help="Leave empty: the category is used by every branch of the company.",
    )
    name = fields.Char(string="Category", required=True, tracking=True)
    code = fields.Char(string="Code", required=True, tracking=True)
    active = fields.Boolean(default=True)
    useful_life_months = fields.Integer(
        string="Default Useful Life (Months)",
        required=True,
        default=60,
        tracking=True,
        help="Book (IAS 16) straight-line life: company accounting policy, editable.",
    )
    salvage_percent = fields.Float(
        string="Default Residual Value %", default=0.0, tracking=True, digits=(5, 2)
    )
    tax_rate_code = fields.Char(
        string="Tax Depreciation Class",
        tracking=True,
        help="Class code of the ITA 2023 Third Schedule rate table (Tax Depreciation "
        "Rates). Empty: no tax depreciation (for example right-of-use assets, whose "
        "rent is deducted as paid).",
    )
    journal_id = fields.Many2one(
        "account.journal",
        string="Asset Journal",
        domain="[('type', '=', 'general'), ('company_id', '=', company_id)]",
        tracking=True,
    )
    asset_account_id = fields.Many2one("account.account", string="Asset Account", tracking=True)
    accumulated_account_id = fields.Many2one(
        "account.account", string="Accumulated Depreciation & Impairment Account", tracking=True
    )
    expense_account_id = fields.Many2one(
        "account.account", string="Depreciation Expense Account", tracking=True
    )
    cwip_account_id = fields.Many2one("account.account", string="CWIP Account", tracking=True)
    revaluation_surplus_account_id = fields.Many2one(
        "account.account", string="Revaluation Surplus Account (OCI)", tracking=True
    )
    impairment_account_id = fields.Many2one(
        "account.account",
        string="Impairment / Revaluation Loss Account",
        tracking=True,
        help="Profit-or-loss account for impairment losses, revaluation decreases "
        "and their reversals (IAS 16.39-40, IAS 36.60/119).",
    )
    gain_account_id = fields.Many2one(
        "account.account", string="Gain on Disposal Account", tracking=True
    )
    loss_account_id = fields.Many2one(
        "account.account", string="Loss on Disposal Account", tracking=True
    )

    _code_company_uniq = models.Constraint(
        "UNIQUE (company_id, code)", "An asset category code is unique per company."
    )

    @api.constrains("useful_life_months", "salvage_percent")
    def _check_policy(self):
        for rec in self:
            if rec.useful_life_months <= 0:
                raise ValidationError(self.env._("The useful life must be at least one month."))
            if not 0.0 <= rec.salvage_percent < 100.0:
                raise ValidationError(self.env._("The residual value % must be from 0 to 99.99."))


class FixAssetTaxRate(models.Model):
    """Effective-dated tax depreciation rate (reducing balance, % a year)."""

    _name = "fix.asset.tax.rate"
    _description = "Tax Depreciation Rate (ITA 2023 Third Schedule)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code, date_from desc"

    company_id = fields.Many2one(
        "res.company",
        index=True,
        help="Leave empty: the statutory rate applies to every company.",
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Branch",
        help="Leave empty: statutory rates apply to every branch.",
    )
    code = fields.Char(string="Class Code", required=True, tracking=True)
    name = fields.Char(string="Asset Class", required=True, tracking=True)
    rate_percent = fields.Float(string="Rate % a Year", required=True, digits=(5, 2), tracking=True)
    date_from = fields.Date(string="Effective From", required=True, tracking=True)
    date_to = fields.Date(string="Effective To", tracking=True)
    legal_reference = fields.Char(string="Legal Reference", tracking=True)
    verified = fields.Boolean(
        string="Verified by Tax Adviser",
        tracking=True,
        help="Unticked: the rate was seeded from secondary sources and must be "
        "confirmed against the current ITA 2023 Third Schedule.",
    )
    note = fields.Text(string="Note")

    @api.constrains("rate_percent", "date_from", "date_to", "code", "company_id")
    def _check_rate(self):
        for rec in self:
            if not 0.0 < rec.rate_percent <= 100.0:
                raise ValidationError(
                    self.env._("A depreciation rate is above 0% and at most 100%.")
                )
            if rec.date_to and rec.date_to < rec.date_from:
                raise ValidationError(self.env._("Effective To is before Effective From."))
            overlap = self.search(
                [
                    ("id", "!=", rec.id),
                    ("code", "=", rec.code),
                    ("company_id", "=", rec.company_id.id),
                    "|",
                    ("date_to", "=", False),
                    ("date_to", ">=", rec.date_from),
                ]
            ).filtered(lambda o, r=rec: not r.date_to or o.date_from <= r.date_to)
            if overlap:
                raise ValidationError(
                    self.env._("Class %s already has a rate in force for these dates.", rec.code)
                )

    @api.model
    def rate_for(self, code, on_date, company):
        """The rate in force on `on_date` (company-specific first, then the
        statutory row with no company). None when nothing is in force."""
        base = [
            ("code", "=", code),
            ("date_from", "<=", on_date),
            "|",
            ("date_to", "=", False),
            ("date_to", ">=", on_date),
        ]
        rate = self.sudo().search([*base, ("company_id", "=", company.id)], limit=1)
        if not rate:
            rate = self.sudo().search([*base, ("company_id", "=", False)], limit=1)
        return rate or None
