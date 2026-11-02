# fix_grc_ops — M60: control testing, SoD rules, delegated authority, licence
# register, policy governance, legal matters, PDPA requests and whistleblowing.
# Risk register, controls, compliance frameworks/obligations and audit
# findings live in fix_grc.py.
from odoo import api, fields, models


class FixGrcControlTest(models.Model):
    _name = "fix.grc.control.test"
    _description = "Control Test"
    _order = "tested_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    control_id = fields.Many2one("fix.control", required=True, ondelete="cascade", index=True)
    tested_on = fields.Date(required=True, default=fields.Date.context_today)
    tester_id = fields.Many2one("hr.employee", string="Tester")
    sample_size = fields.Integer(string="Sample Size")
    exceptions = fields.Integer(string="Exceptions Found")
    result = fields.Selection(
        [
            ("effective", "Effective"),
            ("partially_effective", "Partially Effective"),
            ("ineffective", "Ineffective"),
        ],
        required=True,
        default="effective",
    )
    notes = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.grc.control.test") or "CTST/New"
                )
        return super().create(vals_list)


class FixGrcSodRule(models.Model):
    _name = "fix.grc.sod.rule"
    _description = "Segregation of Duties Rule"
    _order = "name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    role_a = fields.Char(string="First Role", required=True)
    role_b = fields.Char(string="Incompatible Role", required=True)
    conflict_area = fields.Char(string="Process Area")
    severity = fields.Selection(
        [("high", "High"), ("medium", "Medium"), ("low", "Low")],
        required=True,
        default="high",
    )
    compensating_control = fields.Char(string="Compensating Control")
    state = fields.Selection(
        [("active", "Active"), ("waived", "Waived")], required=True, default="active"
    )

    def action_waive(self):
        for rec in self:
            rec.state = "waived"


class FixGrcAuthority(models.Model):
    _name = "fix.grc.authority"
    _description = "Delegated Authority Level"
    _order = "amount_limit desc"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    role_title = fields.Char(string="Role / Position", required=True)
    amount_limit = fields.Monetary(currency_field="currency_id", string="Authority Limit")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    authority_scope = fields.Char(string="Scope")
    delegate_to = fields.Char(string="May Delegate To")
    effective_from = fields.Date(required=True, default=fields.Date.context_today)


class FixGrcLicence(models.Model):
    _name = "fix.grc.licence"
    _description = "Corporate Licence Register"
    _order = "valid_to"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    licence_type = fields.Selection(
        [
            ("trade", "Trade Licence"),
            ("bin", "BIN / VAT Registration"),
            ("tin", "TIN"),
            ("fire", "Fire Safety"),
            ("environment", "Environment"),
            ("other", "Other"),
        ],
        required=True,
        default="trade",
    )
    number = fields.Char(string="Licence Number")
    authority = fields.Char(string="Issuing Authority")
    issued_on = fields.Date()
    valid_to = fields.Date()
    responsible_id = fields.Many2one("hr.employee", string="Responsible")
    state = fields.Selection(
        [
            ("valid", "Valid"),
            ("expiring", "Expiring Soon"),
            ("expired", "Expired"),
            ("suspended", "Suspended"),
        ],
        required=True,
        default="valid",
    )


class FixGrcPolicy(models.Model):
    _name = "fix.grc.policy"
    _description = "Corporate Policy"
    _order = "code"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    policy_type = fields.Selection(
        [
            ("hr", "HR"),
            ("quality", "Quality"),
            ("security", "Information Security"),
            ("finance", "Finance"),
            ("hse", "HSE"),
            ("other", "Other"),
        ],
        required=True,
        default="quality",
    )
    version = fields.Char(default="1.0")
    owner_id = fields.Many2one("hr.employee", string="Policy Owner")
    approved_on = fields.Date()
    review_due = fields.Date()
    attestation_required = fields.Boolean(string="Attestation Required", default=True)
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("retired", "Retired")],
        required=True,
        default="draft",
    )

    _code_unique = models.Constraint(
        "UNIQUE (code, company_id)", "A policy code is unique per company"
    )

    def action_approve(self):
        for rec in self:
            rec.state = "approved"
            rec.approved_on = fields.Date.context_today(self)


class FixGrcLegal(models.Model):
    _name = "fix.grc.legal"
    _description = "Legal Matter"
    _order = "opened_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    matter_type = fields.Selection(
        [
            ("litigation", "Litigation"),
            ("contract", "Contract Dispute"),
            ("labour", "Labour / Employment"),
            ("ip", "IP / Trademark"),
            ("regulatory", "Regulatory Notice"),
            ("other", "Other"),
        ],
        required=True,
        default="litigation",
    )
    counterparty = fields.Char()
    opened_on = fields.Date(required=True, default=fields.Date.context_today)
    counsel = fields.Char(string="External Counsel")
    exposure = fields.Monetary(currency_field="currency_id", string="Exposure")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    state = fields.Selection(
        [
            ("open", "Open"),
            ("negotiation", "Negotiation"),
            ("closed", "Closed"),
            ("judgment", "Judgment"),
        ],
        required=True,
        default="open",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.grc.legal") or "LEG/New"
        return super().create(vals_list)

    def action_close(self):
        for rec in self:
            rec.state = "closed"


class FixGrcPdpa(models.Model):
    _name = "fix.grc.pdpa"
    _description = "PDPA Data Subject Request"
    _order = "received_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    request_type = fields.Selection(
        [
            ("access", "Access"),
            ("erasure", "Erasure"),
            ("correction", "Correction"),
            ("portability", "Portability"),
            ("objection", "Objection"),
        ],
        required=True,
        default="access",
    )
    subject_name = fields.Char(string="Data Subject", required=True)
    received_on = fields.Date(required=True, default=fields.Date.context_today)
    due_on = fields.Date(string="SLA Due")
    handled_by_id = fields.Many2one("hr.employee", string="Handled By")
    outcome = fields.Selection(
        [
            ("pending", "Pending"),
            ("fulfilled", "Fulfilled"),
            ("refused", "Refused"),
            ("partially", "Partially Fulfilled"),
        ],
        required=True,
        default="pending",
    )
    notes = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.grc.pdpa") or "DSR/New"
        return super().create(vals_list)

    def action_fulfil(self):
        for rec in self:
            rec.outcome = "fulfilled"


class FixGrcWhistle(models.Model):
    _name = "fix.grc.whistle"
    _description = "Whistleblowing Report"
    _order = "reported_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    channel = fields.Selection(
        [
            ("hotline", "Hotline"),
            ("email", "Email"),
            ("web", "Web Form"),
            ("letter", "Letter"),
            ("in_person", "In Person"),
        ],
        required=True,
        default="hotline",
    )
    category = fields.Selection(
        [
            ("fraud", "Fraud / Bribery"),
            ("harassment", "Harassment"),
            ("safety", "Safety Breach"),
            ("data", "Data Privacy"),
            ("other", "Other"),
        ],
        required=True,
        default="fraud",
    )
    reported_on = fields.Date(required=True, default=fields.Date.context_today)
    anonymous = fields.Boolean(string="Anonymous", default=True)
    summary = fields.Text(required=True)
    investigator_id = fields.Many2one("hr.employee", string="Investigator")
    state = fields.Selection(
        [
            ("received", "Received"),
            ("investigating", "Investigating"),
            ("substantiated", "Substantiated"),
            ("unsubstantiated", "Unsubstantiated"),
            ("closed", "Closed"),
        ],
        required=True,
        default="received",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.grc.whistle") or "WBL/New"
        return super().create(vals_list)

    def action_investigate(self):
        for rec in self:
            rec.state = "investigating"


REPORTS = {}
