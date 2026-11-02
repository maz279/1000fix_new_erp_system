# fix_competency_ops — M22: assessments, learning paths, OJT mentoring records
# and ISO/brand audit evidence. Competencies, certifications and training
# courses/enrolments live in fix_competency.py.
from odoo import api, fields, models
from odoo.exceptions import UserError


class FixCompetencyAssessment(models.Model):
    _name = "fix.competency.assessment"
    _description = "Competency Assessment"
    _order = "assessed_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)
    competency_id = fields.Many2one("fix.competency", required=True, ondelete="restrict")
    assessed_on = fields.Date(required=True, default=fields.Date.context_today)
    assessor_id = fields.Many2one("hr.employee", string="Assessor")
    level = fields.Selection(
        [
            ("l1", "L1 - Aware"),
            ("l2", "L2 - Assisted"),
            ("l3", "L3 - Independent"),
            ("l4", "L4 - Expert / Trainer"),
        ],
        required=True,
        default="l2",
    )
    score = fields.Float(string="Score %")
    passed = fields.Boolean(string="Passed")
    notes = fields.Char()

    _score_range = models.Constraint(
        "CHECK (score >= 0 AND score <= 100)", "Assessment score is a 0-100 percentage"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.competency.assessment") or "ASMT/New"
                )
        return super().create(vals_list)


class FixLearningPath(models.Model):
    _name = "fix.learning.path"
    _description = "Learning Path"
    _order = "name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    target_role = fields.Char(string="Target Role")
    competency_ids = fields.Many2many("fix.competency", string="Target Competencies")
    course_ids = fields.Many2many("fix.training.course", string="Courses in Path")
    min_level = fields.Selection(
        [
            ("l1", "L1 - Aware"),
            ("l2", "L2 - Assisted"),
            ("l3", "L3 - Independent"),
            ("l4", "L4 - Expert / Trainer"),
        ],
        required=True,
        default="l3",
    )
    active = fields.Boolean(default=True)


class FixOjtRecord(models.Model):
    _name = "fix.ojt.record"
    _description = "OJT / Mentoring Record"
    _order = "date_from desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)
    mentor_id = fields.Many2one("hr.employee", string="Mentor")
    competency_id = fields.Many2one("fix.competency", string="Focus Competency")
    date_from = fields.Date(required=True, default=fields.Date.context_today)
    date_to = fields.Date()
    hours = fields.Float(string="Hours")
    outcome = fields.Selection(
        [
            ("ongoing", "Ongoing"),
            ("competent", "Declared Competent"),
            ("extended", "Extended"),
            ("discontinued", "Discontinued"),
        ],
        required=True,
        default="ongoing",
    )
    notes = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.ojt.record") or "OJT/New"
        return super().create(vals_list)


class FixAuditEvidence(models.Model):
    _name = "fix.audit.evidence"
    _description = "ISO / Brand Audit Evidence"
    _order = "collected_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    evidence_type = fields.Selection(
        [
            ("iso_9001", "ISO 9001:2015"),
            ("brand_audit", "Brand Audit"),
            ("internal_audit", "Internal Audit"),
            ("skills_audit", "Skills Audit"),
        ],
        required=True,
        default="brand_audit",
    )
    standard_ref = fields.Char(string="Standard Clause / Brand Requirement")
    collected_on = fields.Date(required=True, default=fields.Date.context_today)
    reference = fields.Char(string="Evidence Reference")
    attachment_note = fields.Char(string="Attachment / Location")
    employee_id = fields.Many2one("hr.employee", string="Audited Technician / Staff")
    brand_id = fields.Many2one("fix.brand", string="Audited OEM Brand")
    dossier_summary = fields.Text(string="Compiled ISO 9001 Cl. 7.2 Dossier")
    evidence_file = fields.Binary(string="Audit Evidence Scan", attachment=True)
    evidence_filename = fields.Char(string="Evidence Filename")
    notes = fields.Text(string="Auditor Notes")
    valid_until = fields.Date()
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"), ("accepted", "Accepted")],
        required=True,
        default="draft",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.audit.evidence") or "AUD/New"
                )
        return super().create(vals_list)

    def action_submit(self):
        for rec in self:
            rec.state = "submitted"

    def action_accept(self):
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Accept a submitted evidence record")
            rec.state = "accepted"

    def action_compile_iso_dossier(self):
        """ISO 9001:2015 Clause 7.2 Competence Dossier Compiler (RAP-M22-06)."""
        self.ensure_one()
        emp_domain = [("employee_id", "=", self.employee_id.id)] if self.employee_id else []
        certs = self.env["fix.certification"].search(emp_domain)
        trainings = self.env["fix.training.enrollment"].search(
            [*emp_domain, ("state", "=", "passed")]
        )
        assessments = self.env["fix.competency.assessment"].search(emp_domain)
        ojts = self.env["fix.ojt.record"].search(emp_domain)

        lines = [
            f"ISO 9001:2015 CLAUSE 7.2 COMPETENCE DOSSIER — {self.name}",
            f"Standard / Clause: {self.standard_ref or 'ISO 9001:2015 Cl. 7.2'}",
            f"Technician: {self.employee_id.name if self.employee_id else 'All Certified Staff'}",
            f"Active Certifications: {len(certs.filtered(lambda c: c.status != 'expired'))}",
            f"Passed Training Courses: {len(trainings)}",
            f"Competency Assessments: {len(assessments)}",
            f"OJT Mentoring Hours: {sum(ojts.mapped('hours')):.1f}h",
        ]
        summary = "\n".join(lines)
        self.write({"dossier_summary": summary})
        return {
            "evidence_id": self.id,
            "certifications": len(certs),
            "passed_trainings": len(trainings),
            "assessments": len(assessments),
            "ojt_hours": sum(ojts.mapped("hours")),
            "summary": summary,
        }
