# cd_ap_ext — Vendor Tax Profile and the bill approval matrix (CD-M52-01).
import re

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FixVendorTaxProfile(models.Model):
    """The vendor's tax identity: TIN, BIN and the proof of return
    submission (PSR) with its expiry. It drives TDS (payee type, the
    non-filer multiplier) and VDS (default service code)."""

    _name = "fix.vendor.tax.profile"
    _description = "Vendor Tax Profile"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "partner_id"
    _partner_company_unique = models.Constraint(
        "UNIQUE (partner_id, company_id)", "A vendor has one tax profile per company"
    )

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", help="Company-wide: leave empty")
    partner_id = fields.Many2one(
        "res.partner", string="Vendor", required=True, index=True, ondelete="cascade"
    )
    tin = fields.Char(string="TIN (e-TIN)", size=12, tracking=True)
    bin = fields.Char(string="BIN", size=13, tracking=True)
    taxpayer_type = fields.Selection(
        [("company", "Company"), ("individual", "Individual"), ("other", "Other / firm")],
        required=True,
        default="company",
        tracking=True,
    )
    psr_reference = fields.Char(
        string="Return-Filing Proof (PSR) Ref", tracking=True, help="Proof of submission of return"
    )
    psr_valid_until = fields.Date(string="PSR Valid Until", tracking=True)
    psr_attachment_ids = fields.Many2many("ir.attachment", string="PSR Evidence")
    psr_valid = fields.Boolean(
        string="PSR Valid Today", compute="_compute_psr_valid", search="_search_psr_valid"
    )
    turnover_enlisted = fields.Boolean(
        string="Turnover-Tax Enlisted",
        help="Enlisted, not VAT-registered: its invoices do not support input VAT credit",
    )
    default_tds_category = fields.Char(
        string="Default TDS Category", help="Tax Rate Master code, e.g. service_general"
    )
    default_vds_rate_id = fields.Many2one(
        "fix.tax.rate", string="Default VDS Service Code", domain=[("tax_kind", "=", "vds")]
    )
    vds_exempt = fields.Boolean(
        string="VDS Not Applicable",
        help="Supplies outside VDS (e.g. fuel, gas, WASA, electricity, telephone bills)",
    )
    note = fields.Text()

    @api.depends("psr_reference", "psr_valid_until")
    def _compute_psr_valid(self):
        today = fields.Date.context_today(self)
        for prof in self:
            prof.psr_valid = prof.is_filer_on(today)

    def _search_psr_valid(self, operator, value):
        today = fields.Date.context_today(self)
        valid = ["&", ("psr_reference", "!=", False), ("psr_valid_until", ">=", today)]
        positive = (operator == "=") == bool(value)
        return valid if positive else ["!", *valid]

    @api.constrains("tin", "bin")
    def _check_ids(self):
        for prof in self:
            if prof.tin and not re.fullmatch(r"\d{12}", prof.tin.strip()):
                raise ValidationError("A TIN (e-TIN) is 12 digits")
            if prof.bin and not re.fullmatch(r"\d{13}", prof.bin.strip()):
                raise ValidationError("A BIN is 13 digits")

    def is_filer_on(self, on_date):
        """True when a return-filing proof is recorded and valid on on_date."""
        self.ensure_one()
        return bool(self.psr_reference and self.psr_valid_until and self.psr_valid_until >= on_date)

    @api.model
    def for_partner(self, partner, company=None):
        company = company or self.env.company
        return self.sudo().search(
            [
                ("partner_id", "=", partner.commercial_partner_id.id),
                ("company_id", "=", company.id),
            ],
            limit=1,
        )


class FixApApprovalRule(models.Model):
    """The amount-based approval matrix for vendor bills: a bill needs every
    active level whose minimum it reaches, each approved by a member of the
    level's group who neither submitted the bill nor approved a lower level."""

    _name = "fix.ap.approval.rule"
    _description = "AP Approval Matrix Level"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "level, amount_min"
    _company_level_unique = models.Constraint(
        "UNIQUE (company_id, level)", "One matrix row per level and company"
    )

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", help="Company-wide: leave empty")
    name = fields.Char(required=True)
    level = fields.Integer(required=True, default=1)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount_min = fields.Monetary(
        string="Applies From (gross)", currency_field="currency_id", required=True, default=0.0
    )
    group_id = fields.Many2one("res.groups", string="Approver Group", required=True)
    active = fields.Boolean(default=True)

    @api.constrains("level", "amount_min")
    def _check_rule(self):
        for rule in self:
            if rule.level < 1 or rule.amount_min < 0:
                raise ValidationError("Levels start at 1 and minimums are not negative")

    @api.model
    def levels_for(self, amount, company):
        rules = self.sudo().search(
            [("company_id", "=", company.id), ("amount_min", "<=", amount)], order="level"
        )
        return self.browse(rules.ids)


class FixApApprovalLog(models.Model):
    """Immutable approver log of a vendor bill (or note)."""

    _name = "fix.ap.approval.log"
    _description = "AP Approval Log"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit")
    invoice_id = fields.Many2one("fix.vendor.invoice", index=True, ondelete="cascade")
    rule_id = fields.Many2one("fix.ap.approval.rule", string="Matrix Row", ondelete="set null")
    level = fields.Integer()
    user_id = fields.Many2one("res.users", required=True, default=lambda self: self.env.user)
    action = fields.Selection(
        [
            ("submit", "Submitted"),
            ("approve", "Approved"),
            ("reject", "Rejected"),
            ("reset", "Reset to Draft"),
        ],
        required=True,
    )
    amount = fields.Float(string="Bill Gross")
    note = fields.Char()
    logged_at = fields.Datetime(default=fields.Datetime.now, required=True)

    def write(self, vals):
        raise ValidationError("The approval log is append-only")

    def unlink(self):
        raise ValidationError("The approval log is append-only")
