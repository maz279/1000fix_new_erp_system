# cd_ap_ext — Vendor Tax Profile and the bill approval matrix (CD-M52-01).
import re

from odoo import api, fields, models
from odoo.addons.cd_fixed_asset_ext.models.fix_asset_common import (
    attach_upload,
    attachment_names,
)
from odoo.exceptions import UserError, ValidationError

_MATRIX_KEY = "fix_ap_matrix_change"
_MATRIX_TOKEN = object()
# A matrix level is decided by accounting: its group must be (or imply) one
# of these (A08 M52-12: level 2 was re-pointed to base.group_user).
MATRIX_GROUPS = ("account.group_account_user", "account.group_account_manager")


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
    psr_attachment_ids = fields.Many2many(
        "ir.attachment",
        string="PSR Evidence",
        help="A08 M52-10: the PSR counts only with the proof attached (and a TIN on file).",
    )
    psr_evidence_file = fields.Binary(
        string="Upload PSR Proof",
        compute="_compute_upload_files",
        inverse="_inverse_psr_evidence_file",
        attachment=False,
    )
    psr_evidence_filename = fields.Char(string="PSR File Name", copy=False)
    psr_evidence_names = fields.Char(string="PSR Proof Attached", compute="_compute_upload_names")
    # A08 M52-10: a TDS exemption is evidence, not a tick on the bill line.
    tds_exempt_certificate_ref = fields.Char(string="TDS Exemption Certificate No", tracking=True)
    tds_exempt_valid_until = fields.Date(string="Exemption Valid Until", tracking=True)
    tds_exempt_attachment_ids = fields.Many2many(
        "ir.attachment",
        "fix_vendor_tax_profile_tds_exempt_att_rel",
        "profile_id",
        "attachment_id",
        string="Exemption Certificate",
    )
    tds_exempt_file = fields.Binary(
        string="Upload Exemption Certificate",
        compute="_compute_upload_files",
        inverse="_inverse_tds_exempt_file",
        attachment=False,
    )
    tds_exempt_filename = fields.Char(string="Certificate File Name", copy=False)
    tds_exempt_names = fields.Char(string="Certificate Attached", compute="_compute_upload_names")
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

    @api.depends("psr_reference", "psr_valid_until", "psr_attachment_ids", "tin")
    def _compute_psr_valid(self):
        today = fields.Date.context_today(self)
        for prof in self:
            prof.psr_valid = prof.is_filer_on(today)

    def _search_psr_valid(self, operator, value):
        today = fields.Date.context_today(self)
        valid = [
            "&",
            "&",
            "&",
            ("tin", "!=", False),
            ("psr_reference", "!=", False),
            ("psr_attachment_ids", "!=", False),
            ("psr_valid_until", ">=", today),
        ]
        positive = (operator == "=") == bool(value)
        return valid if positive else ["!", *valid]

    def _compute_upload_files(self):
        for prof in self:
            prof.psr_evidence_file = False
            prof.tds_exempt_file = False

    def _inverse_psr_evidence_file(self):
        for prof in self:
            attach_upload(
                prof,
                "psr_attachment_ids",
                prof.psr_evidence_file,
                prof.psr_evidence_filename,
                "PSR %s" % (prof.psr_reference or prof.partner_id.display_name),
            )

    def _inverse_tds_exempt_file(self):
        for prof in self:
            attach_upload(
                prof,
                "tds_exempt_attachment_ids",
                prof.tds_exempt_file,
                prof.tds_exempt_filename,
                "TDS exemption %s"
                % (prof.tds_exempt_certificate_ref or prof.partner_id.display_name),
            )

    @api.depends("psr_attachment_ids", "tds_exempt_attachment_ids")
    def _compute_upload_names(self):
        for prof in self:
            prof.psr_evidence_names = attachment_names(prof.psr_attachment_ids)
            prof.tds_exempt_names = attachment_names(prof.tds_exempt_attachment_ids)

    @api.constrains("default_vds_rate_id")
    def _check_default_vds(self):
        # the form's list is every tax rate: the domain binds only Odoo's own form
        for prof in self:
            rate = prof.default_vds_rate_id.sudo()
            if rate and rate.tax_kind != "vds":
                raise ValidationError("%s is not a VDS service code." % rate.display_name)

    @api.constrains("tin", "bin")
    def _check_ids(self):
        for prof in self:
            if prof.tin and not re.fullmatch(r"\d{12}", prof.tin.strip()):
                raise ValidationError("A TIN (e-TIN) is 12 digits")
            if prof.bin and not re.fullmatch(r"\d{13}", prof.bin.strip()):
                raise ValidationError("A BIN is 13 digits")

    def is_filer_on(self, on_date):
        """True when a return-filing proof is recorded, EVIDENCED (attachment)
        and valid on on_date, for a payee with a TIN. A08 M52-10: a typed
        reference 'x' to 2099 used to clear the non-filer uplift."""
        self.ensure_one()
        return bool(
            (self.tin or "").strip()
            and (self.psr_reference or "").strip()
            and self.psr_valid_until
            and self.psr_valid_until >= on_date
            and self.psr_attachment_ids
        )

    def is_tds_exempt_on(self, on_date):
        """An exemption certificate with its number, file and expiry, valid on on_date."""
        self.ensure_one()
        return bool(
            (self.tds_exempt_certificate_ref or "").strip()
            and self.tds_exempt_valid_until
            and self.tds_exempt_valid_until >= on_date
            and self.tds_exempt_attachment_ids
        )

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
    def _fix_assert_matrix_group(self, group):
        allowed = self.env["res.groups"]
        for xmlid in MATRIX_GROUPS:
            allowed |= self.env.ref(xmlid, raise_if_not_found=False) or self.env["res.groups"]
        group = group.sudo()
        if not (group & allowed or group.all_implied_ids & allowed):
            raise ValidationError(
                "A matrix level is decided by an accounting group (Accountant or Accounting "
                "Administrator, or a group that implies one): %s is not." % group.display_name
            )

    @api.constrains("group_id")
    def _check_group(self):
        for rule in self:
            self._fix_assert_matrix_group(rule.group_id)

    # ---- dual control (A08 M52-12) ------------------------------------------
    def _fix_matrix_writing(self):
        return self.with_context(**{_MATRIX_KEY: _MATRIX_TOKEN})

    def _fix_matrix_open(self):
        return self.env.su or self.env.context.get(_MATRIX_KEY) is _MATRIX_TOKEN

    def _fix_matrix_refuse(self):
        raise UserError(
            "The AP approval matrix changes through a matrix change request, proposed by one "
            "accounting manager and confirmed by another (A08 M52-12)."
        )

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_matrix_open():
            self._fix_matrix_refuse()
        return super().create(vals_list)

    def write(self, vals):
        tracked = {"name", "level", "amount_min", "group_id", "active", "company_id", "currency_id"}
        if tracked & set(vals) and not self._fix_matrix_open():
            self._fix_matrix_refuse()
        return super().write(vals)

    def unlink(self):
        if not self._fix_matrix_open():
            self._fix_matrix_refuse()
        return super().unlink()

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
