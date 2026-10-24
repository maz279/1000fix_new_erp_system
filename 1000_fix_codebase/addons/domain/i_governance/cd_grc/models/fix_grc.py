# fix_grc — M60: Governance, Risk, Compliance & Assurance (P09-M08 & R07-M05).
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish


class FixRiskRegister(models.Model):
    """M60: Enterprise Risk Register with likelihood/impact matrix and residual risk tracking."""

    _name = "fix.risk.register"
    _description = "Risk Register Entry"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "risk_score desc, name"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(string="Risk Description", required=True)
    category = fields.Selection(
        [
            ("strategic", "Strategic"),
            ("operational", "Operational (Service Delivery)"),
            ("financial", "Financial"),
            ("compliance", "Statutory & Regulatory Compliance"),
            ("cyber", "Cybersecurity & Data Protection (PDPA/ISO 27001)"),
            ("hse", "Health, Safety & Environment (BLA 2006)"),
        ],
        required=True,
        default="operational",
    )
    likelihood = fields.Selection(
        [
            ("1", "Rare (1)"),
            ("2", "Unlikely (2)"),
            ("3", "Possible (3)"),
            ("4", "Likely (4)"),
            ("5", "Almost Certain (5)"),
        ],
        default="3",
        required=True,
    )
    impact = fields.Selection(
        [
            ("1", "Insignificant (1)"),
            ("2", "Minor (2)"),
            ("3", "Moderate (3)"),
            ("4", "Major (4)"),
            ("5", "Severe / Catastrophic (5)"),
        ],
        default="3",
        required=True,
    )
    risk_score = fields.Integer(string="Inherent Risk Score", compute="_compute_score", store=True)
    mitigation = fields.Text(string="Mitigation & Treatment Strategy")
    control_ids = fields.One2many("fix.control", "risk_id", string="Mitigating Controls")
    owner_id = fields.Many2one("hr.employee", string="Risk Owner")
    review_date = fields.Date(string="Next Review Date")
    state = fields.Selection(
        [
            ("open", "Active / Open"),
            ("mitigating", "Mitigating / Under Treatment"),
            ("accepted", "Residual Accepted"),
            ("closed", "Closed / Retired"),
        ],
        default="open",
        required=True,
        tracking=True,
    )

    @api.depends("likelihood", "impact")
    def _compute_score(self):
        for rec in self:
            rec.risk_score = int(rec.likelihood or "3") * int(rec.impact or "3")


class FixControl(models.Model):
    """M60: Internal Control definition and effectiveness assessment."""

    _name = "fix.control"
    _description = "Internal Control"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(string="Control Title", required=True)
    control_code = fields.Char(string="Control Code (e.g. CTL-SEC-01)")
    control_type = fields.Selection(
        [("preventive", "Preventive"), ("detective", "Detective"), ("corrective", "Corrective")],
        required=True,
        default="preventive",
    )
    frequency = fields.Selection(
        [
            ("continuous", "Automated / Continuous"),
            ("daily", "Daily"),
            ("weekly", "Weekly"),
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("annual", "Annual"),
        ],
        default="continuous",
        required=True,
    )
    risk_id = fields.Many2one("fix.risk.register", string="Risk Addressed")
    obligation_ids = fields.Many2many("fix.compliance.obligation", string="Mapped Obligations")
    last_tested = fields.Date(string="Last Assessment Date")
    test_result = fields.Selection(
        [
            ("effective", "Effective"),
            ("partially", "Partially Effective"),
            ("ineffective", "Ineffective"),
        ],
        tracking=True,
    )
    evidence_doc_id = fields.Many2one(
        "fix.document",
        string="Control Evidence (M24)",
        help="Evidence artefact stored in M24 document store per ADR D-040",
    )
    state = fields.Selection(
        [("active", "Active"), ("inactive", "Inactive")],
        default="active",
        required=True,
        tracking=True,
    )


class FixComplianceFramework(models.Model):
    """M60: Authoritative compliance frameworks (ISO 9001, ISO 27001, PDPA, Labour Act)."""

    _name = "fix.compliance.framework"
    _description = "Compliance Standard & Framework Matrix"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code, name"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(string="Framework Name", required=True)
    code = fields.Selection(
        [
            ("iso_9001", "ISO 9001:2015 Quality Management"),
            ("iso_27001", "ISO/IEC 27001:2022 Information Security"),
            ("pdpa_2023", "Bangladesh PDPA 2023 / 2026"),
            ("bla_2006", "Bangladesh Labour Act 2006 & Rules 2015"),
            ("iso_14001", "ISO 14001:2015 Environmental Management"),
        ],
        string="Framework Identifier",
        required=True,
        default="iso_9001",
    )
    standard_edition = fields.Char(string="Edition / Revision", default="Current")
    certifying_body = fields.Char(
        string="Certification Body / Regulator", default="DNV / DIFE / DoE"
    )
    obligation_ids = fields.One2many(
        "fix.compliance.obligation", "framework_id", string="Obligations"
    )
    finding_ids = fields.One2many("fix.audit.finding", "framework_id", string="Audit Findings")
    clause_count = fields.Integer(
        string="Total Mapped Clauses", compute="_compute_clause_stats", store=True
    )
    compliance_score = fields.Float(
        string="Compliance Rate (%)", compute="_compute_clause_stats", store=True
    )
    last_audit_date = fields.Date(string="Last External/Internal Audit")
    next_audit_date = fields.Date(string="Next Surveillance Audit")
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [("draft", "Draft Mapping"), ("active", "Enforced & Audited"), ("archived", "Archived")],
        default="active",
        required=True,
        tracking=True,
    )

    @api.depends("obligation_ids.compliance_status")
    def _compute_clause_stats(self):
        for rec in self:
            rec.clause_count = len(rec.obligation_ids)
            # "Not Applicable" clauses are out of scope: counting them in the
            # denominator scored an excluded clause as a failure.
            applicable = rec.obligation_ids.filtered(
                lambda o: o.compliance_status != "not_applicable"
            )
            if applicable:
                compliant = len(applicable.filtered(lambda o: o.compliance_status == "compliant"))
                partial = len(
                    applicable.filtered(lambda o: o.compliance_status == "partially_compliant")
                )
                rec.compliance_score = round(
                    ((compliant + (0.5 * partial)) / len(applicable)) * 100.0, 1
                )
            else:
                rec.compliance_score = 100.0


class FixComplianceObligation(models.Model):
    """M60: Specific clause or statutory requirement under a compliance framework."""

    _name = "fix.compliance.obligation"
    _description = "Compliance Obligation & Clause"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "clause_reference, name"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    framework_id = fields.Many2one(
        "fix.compliance.framework", string="Compliance Framework", required=True
    )
    name = fields.Char(string="Requirement Title", required=True)
    clause_reference = fields.Char(string="Clause / Section Reference", required=True)
    mandatory = fields.Boolean(string="Mandatory Statutory Requirement", default=True)
    control_ids = fields.Many2many("fix.control", string="Enforcing Controls")
    evidence_doc_id = fields.Many2one(
        "fix.document",
        string="Compliance Evidence (M24 Document)",
        help="Evidentiary record registered in M24 kernel per ADR D-040",
    )
    compliance_status = fields.Selection(
        [
            ("compliant", "Fully Compliant"),
            ("partially_compliant", "Partially Compliant"),
            ("non_compliant", "Non-Compliant"),
            ("not_applicable", "Not Applicable"),
        ],
        default="compliant",
        required=True,
        tracking=True,
    )
    notes = fields.Text(string="Audit & Assessment Notes")


class FixAuditFinding(models.Model):
    """M60: Internal & External Audit Non-Conformances and Corrective Actions (CAPA)."""

    _name = "fix.audit.finding"
    _description = "Audit Finding & CAPA"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "audit_date desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(string="Finding Summary", required=True)
    finding_code = fields.Char(string="Finding Reference (e.g. AUD-2026-001)")
    framework_id = fields.Many2one(
        "fix.compliance.framework", string="Audited Framework", required=True
    )
    obligation_id = fields.Many2one(
        "fix.compliance.obligation", string="Breached Obligation / Clause"
    )
    finding_type = fields.Selection(
        [
            ("major_nc", "Major Non-Conformance"),
            ("minor_nc", "Minor Non-Conformance"),
            ("ofi", "Opportunity for Improvement (OFI)"),
        ],
        default="minor_nc",
        required=True,
        tracking=True,
    )
    auditor_id = fields.Many2one("hr.employee", string="Lead Auditor", required=True)
    audit_date = fields.Date(string="Audit Date", default=fields.Date.today, required=True)
    target_closure_date = fields.Date(string="CAPA Target Closure Date", required=True)
    description = fields.Text(string="Condition & Objective Evidence", required=True)
    root_cause_analysis = fields.Text(string="Root Cause Analysis (5-Why / Fishbone)")
    remediation_plan = fields.Text(string="Corrective Action Plan (CAPA)")
    closure_evidence_doc_id = fields.Many2one(
        "fix.document",
        string="Closure Evidence Document (M24)",
        help="Signed verification artefact in M24 volume store per ADR D-040",
    )
    capa_status = fields.Selection(
        [
            ("open", "Open Non-Conformance"),
            ("capa_submitted", "CAPA Submitted"),
            ("verified", "Effectiveness Verified"),
            ("closed", "Closed & Certified"),
        ],
        default="open",
        required=True,
        tracking=True,
    )

    def action_submit_capa(self, plan_text=""):
        for rec in self:
            if plan_text:
                rec.remediation_plan = plan_text
            rec.capa_status = "capa_submitted"

    def action_verify_closure(self):
        for rec in self:
            if not rec.remediation_plan:
                raise UserError("A remediation plan must be documented before verifying closure.")
            rec.capa_status = "closed"
            publish(
                self.env,
                "grc.capa_closed",
                "fix.audit.finding",
                rec.id,
                {"code": rec.finding_code or rec.name, "framework": rec.framework_id.name},
            )
