# fix_qms_ops — M23: policy/objectives, process register, checklist templates,
# quality gates, certification surveillance, management review and CoPQ.
# NCRs, CAPAs and internal audits live in fix_qms.py.
from odoo import api, fields, models
from odoo.exceptions import UserError


class FixQmsPolicy(models.Model):
    _name = "fix.qms.policy"
    _description = "Quality Policy & Objective"
    _order = "year desc, id desc"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    year = fields.Char(required=True)
    policy_text = fields.Text()
    objective = fields.Char(string="Quality Objective")
    target = fields.Float(string="Target")
    actual = fields.Float(string="Actual")
    unit = fields.Char()
    owner_id = fields.Many2one("hr.employee", string="Owner")
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("reviewed", "Reviewed")],
        required=True,
        default="draft",
    )

    def action_approve(self):
        for rec in self:
            rec.state = "approved"


class FixQmsProcess(models.Model):
    _name = "fix.qms.process"
    _description = "QMS Process Register"
    _order = "code"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    process_owner_id = fields.Many2one("hr.employee", string="Process Owner")
    iso_clause = fields.Char(string="ISO 9001 Clause")
    process_type = fields.Selection(
        [("core", "Core / Value Stream"), ("support", "Support"), ("management", "Management")],
        required=True,
        default="core",
    )
    inputs = fields.Char()
    outputs = fields.Char()
    kpi_definition = fields.Char(string="Process KPI")
    state = fields.Selection(
        [("active", "Active"), ("retired", "Retired")], required=True, default="active"
    )

    _code_unique = models.Constraint(
        "UNIQUE (code, company_id)", "A process code is unique per company"
    )


class FixQmsChecklist(models.Model):
    _name = "fix.qms.checklist"
    _description = "Quality Checklist Template"
    _order = "name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    checklist_type = fields.Selection(
        [
            ("qc", "QC Bench Check"),
            ("audit", "Audit Checklist"),
            ("handover", "Handover"),
            ("safety", "Safety Walk"),
        ],
        required=True,
        default="qc",
    )
    iso_clause = fields.Char(string="ISO Clause")
    item_count = fields.Integer(string="Items")
    version = fields.Char(default="1.0")
    state = fields.Selection(
        [("draft", "Draft"), ("published", "Published"), ("retired", "Retired")],
        required=True,
        default="draft",
    )

    def action_publish(self):
        for rec in self:
            rec.state = "published"


class FixQmsGate(models.Model):
    _name = "fix.qms.gate"
    _description = "Quality Gate"
    _order = "sequence, id"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    sequence = fields.Integer(default=10)
    stage = fields.Char(string="Process Stage")
    mandatory_checklist_id = fields.Many2one("fix.qms.checklist", string="Mandatory Checklist")
    blocking = fields.Boolean(string="Blocks Progression", default=True)
    state = fields.Selection(
        [("active", "Active"), ("retired", "Retired")], required=True, default="active"
    )


class FixQmsCertification(models.Model):
    _name = "fix.qms.certification"
    _description = "Certification & Surveillance Audit"
    _order = "audit_date desc, id desc"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    standard = fields.Char(required=True, default="ISO 9001:2015")
    body = fields.Char(string="Certification Body")
    certificate_no = fields.Char()
    audit_type = fields.Selection(
        [
            ("stage_1", "Stage 1"),
            ("stage_2", "Stage 2"),
            ("surveillance", "Surveillance"),
            ("recertification", "Recertification"),
        ],
        required=True,
        default="surveillance",
    )
    audit_date = fields.Date(required=True, default=fields.Date.context_today)
    valid_until = fields.Date()
    result = fields.Selection(
        [
            ("pending", "Pending"),
            ("passed", "Passed"),
            ("minor_ncs", "Passed with Minor NCs"),
            ("major_ncs", "Major NCs"),
            ("failed", "Failed"),
        ],
        required=True,
        default="pending",
    )
    notes = fields.Char()

    def action_pass(self):
        for rec in self:
            rec.result = "passed"


class FixQmsReview(models.Model):
    _name = "fix.qms.review"
    _description = "Management Review"
    _order = "review_date desc, id desc"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    review_date = fields.Date(required=True, default=fields.Date.context_today)
    chairperson_id = fields.Many2one("hr.employee", string="Chairperson")
    attendees = fields.Char()
    agenda = fields.Text()
    decisions = fields.Text()
    open_actions = fields.Integer(string="Open Actions")
    state = fields.Selection(
        [("scheduled", "Scheduled"), ("held", "Held"), ("closed", "Closed")],
        required=True,
        default="scheduled",
    )

    def action_hold(self):
        for rec in self:
            rec.state = "held"

    def action_close(self):
        for rec in self:
            if rec.state != "held":
                raise UserError("Close a review that has been held")
            rec.state = "closed"


class FixQmsCopq(models.Model):
    _name = "fix.qms.copq"
    _description = "Cost of Poor Quality"
    _order = "period desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    period = fields.Char(required=True, help="YYYY-MM")
    category = fields.Selection(
        [
            ("rework", "Rework"),
            ("scrap", "Scrap"),
            ("warranty", "Warranty"),
            ("complaint", "Complaint Handling"),
            ("inspection", "Inspection"),
            ("downtime", "Downtime"),
        ],
        required=True,
        default="rework",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(currency_field="currency_id", required=True)
    source_ref = fields.Char()
    notes = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.qms.copq") or "COPQ/New"
        return super().create(vals_list)
