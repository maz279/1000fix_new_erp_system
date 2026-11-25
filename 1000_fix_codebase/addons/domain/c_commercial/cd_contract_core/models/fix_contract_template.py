# cd_contract_core — Contract Template Master Model (DEFECT-M37-PHANTOM Remediation)
from odoo import api, fields, models
from odoo.exceptions import UserError

LEGAL = "cd_contract_core.group_contract_legal"
TERMS_FIELDS = ("standard_terms", "terms_bn")


class FixContractTemplate(models.Model):
    """Statutory Contract Template Master for Commercial Contracts and SLA Packages."""

    _name = "fix.contract.template"
    _description = "Contract Template"
    # A04 build (2026-11-04) M08-15: the author signed off his own one-letter
    # template "as Legal". The sign-off is now a Legal reviewer's, never the
    # author's or the last editor's, and editing signed wording withdraws it.
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "name"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(string="Template Name", required=True, tracking=True)
    code = fields.Char(string="Template Code", required=True, index=True, copy=False)
    contract_type = fields.Selection(
        [
            ("amc", "Annual Maintenance Contract (AMC)"),
            ("ramc", "Repair & Maintenance Contract (RAMC)"),
            ("managed", "Managed Services Agreement"),
            ("rental", "Equipment Rental Agreement"),
            ("marketplace", "Marketplace Seller Agreement"),
            ("sla", "Service Level Agreement (SLA Only)"),
        ],
        string="Contract Type",
        required=True,
        default="amc",
        tracking=True,
    )
    generation_type = fields.Selection(
        [
            ("auto", "Automated Generation (System)"),
            ("manual", "Manual Drafting"),
        ],
        string="Generation Type",
        required=True,
        default="auto",
    )
    date_start = fields.Date(string="Default Start Date", default=fields.Date.today)
    date_end = fields.Date(string="Default End Date")
    standard_terms = fields.Text(string="Standard Contract Terms & Conditions")
    terms_bn = fields.Text(string="Contract Terms (Bengali)")
    duration_months = fields.Integer(string="Standard Term (Months)", default=12)
    notice_period_days = fields.Integer(string="Termination Notice Period (Days)", default=30)
    active = fields.Boolean(default=True, tracking=True)

    # A template with no wording is a shell. The six seeded templates ship
    # structurally complete and deliberately empty of terms, because contract
    # wording is Legal's to author — so the system has to say out loud which
    # templates are not yet usable, rather than let one be used blank
    # (A04 audit, 2026-11-01).
    is_publishable = fields.Boolean(
        string="Ready to Issue",
        compute="_compute_is_publishable",
        store=True,
        help="A template may only generate a contract once both the English "
        "and Bengali standard terms are authored.",
    )
    publish_blocker = fields.Char(
        string="Why Not Ready", compute="_compute_is_publishable", store=True
    )

    # Wording alone is not sign-off. Draft terms were seeded so Legal edits
    # rather than starts from a blank page, and a draft that became issuable
    # merely by being non-empty would be worse than an empty template: an
    # unreviewed contract could reach a customer. Legal signs, by name
    # (A04 audit, 2026-11-01).
    legal_reviewed_by = fields.Many2one(
        "res.users", string="Legal Sign-Off", readonly=True, tracking=True
    )
    legal_reviewed_on = fields.Datetime(readonly=True, tracking=True)
    terms_are_draft = fields.Boolean(
        string="Terms Are Draft",
        default=True,
        tracking=True,
        readonly=True,
        help="Seeded wording is a starting point for Legal, not approved "
        "terms. Cleared automatically when Legal signs off.",
    )
    terms_last_edited_by = fields.Many2one(
        "res.users",
        string="Wording Last Edited By",
        readonly=True,
        copy=False,
        help="Whoever last changed the wording cannot be the Legal reviewer who signs it.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "legal_reviewed_by",
            "legal_reviewed_on",
            "terms_are_draft",
            "terms_last_edited_by",
        }

    def write(self, vals):
        edited = set(vals) & set(TERMS_FIELDS)
        moved = (
            self.filtered(lambda r: any(r._fix_guard_differs(n, vals[n], r[n]) for n in edited))
            if edited and not self._fix_guard_open()
            else self.browse()
        )
        result = super().write(vals)
        if moved:
            signed = moved.filtered("legal_reviewed_by")
            moved._guarded().write(
                {
                    "terms_last_edited_by": self.env.uid,
                    "legal_reviewed_by": False,
                    "legal_reviewed_on": False,
                    "terms_are_draft": True,
                }
            )
            for rec in signed:
                rec.message_post(body="Wording changed after sign-off: Legal sign-off withdrawn.")
        return result

    @api.depends("standard_terms", "terms_bn", "legal_reviewed_by")
    def _compute_is_publishable(self):
        for rec in self:
            missing = []
            if not (rec.standard_terms or "").strip():
                missing.append("English standard terms")
            if not (rec.terms_bn or "").strip():
                missing.append("Bengali terms (DE-17 bilingual requirement)")
            if not rec.legal_reviewed_by:
                missing.append("Legal sign-off")
            rec.is_publishable = not missing
            rec.publish_blocker = ("Awaiting: " + ", ".join(missing)) if missing else False

    def _require_legal(self, what):
        if not (self.env.su or self.env.user.has_group(LEGAL)):
            raise UserError("%s is for a Contract Legal Reviewer." % what)

    def action_legal_signoff(self):
        """Legal accepts this wording. Attributable, and reversible."""
        self._require_legal("Signing off contract wording")
        for rec in self:
            if not (rec.standard_terms or "").strip() or not (rec.terms_bn or "").strip():
                raise UserError(
                    "Both the English and Bengali terms must be authored "
                    "before Legal can sign off template '%s'." % rec.name
                )
            if not self.env.su and self.env.user in (rec.create_uid | rec.terms_last_edited_by):
                raise UserError(
                    "Segregation of duties: you authored or last edited the wording of "
                    "template '%s', so another Legal reviewer must sign it off." % rec.name
                )
            rec.sudo()._guarded().write(
                {
                    "legal_reviewed_by": self.env.user.id,
                    "legal_reviewed_on": fields.Datetime.now(),
                    "terms_are_draft": False,
                }
            )
            rec.message_post(body="Contract wording signed off by %s." % self.env.user.name)
        return True

    def action_withdraw_signoff(self):
        """Pull a template out of use - it stops being issuable at once."""
        self._require_legal("Withdrawing a contract sign-off")
        for rec in self:
            rec.sudo()._guarded().write(
                {"legal_reviewed_by": False, "legal_reviewed_on": False, "terms_are_draft": True}
            )
            rec.message_post(body="Legal sign-off withdrawn by %s." % self.env.user.name)
        return True

    def assert_publishable(self):
        """Raise unless this template may be issued to a customer."""
        for rec in self:
            if not rec.is_publishable:
                raise UserError(
                    "Contract template '%s' is not ready to issue. %s"
                    % (rec.name, rec.publish_blocker)
                )
        return True

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("code"):
                vals["code"] = (
                    self.env["ir.sequence"].next_by_code("fix.contract.template")
                    or f"CTPL/{fields.Date.today().year}/{self.search_count([]) + 1}"
                )
        return super().create(vals_list)
