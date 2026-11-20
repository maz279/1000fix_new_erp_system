# fix_competency — M22: certification register + FR-LMS-039 (P08-M05).
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish

EXPIRING_WINDOW_DAYS = 30


class FixCompetency(models.Model):
    _name = "fix.competency"
    _description = "Competency"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    code = fields.Char(required=True)
    name = fields.Char(required=True)
    name_bn = fields.Char(string="Competency (Bengali)", help="DE-17")
    device_type = fields.Char(
        string="Device Type Scope",
        help="e.g. smartphone, laptop, home_appliance — the dispatch "
             "eligibility match key (FR-LMS-039)")
    required_for_dispatch = fields.Boolean(
        default=True,
        help="Unchecked for developmental competencies that do not gate "
             "assignment")


    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
class FixCertification(models.Model):
    """The certification register with expiry tracking (P08-M05-T02)."""
    _name = "fix.certification"
    _description = "Certification"
    # P03 workspace data-entry form (discovered by cd_p03_portal).
    _p03_capture = {
        "module": "M22",
        "form": "Certification",
        "fields": ["employee_id", "competency_id", "issued_on", "expires_on", "evidence_ref"],
    }
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "employee_id, expires_on"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    competency_id = fields.Many2one("fix.competency", required=True,
                                     ondelete="restrict")
    issued_on = fields.Date(required=True, default=fields.Date.today)
    expires_on = fields.Date(
        help="Empty means non-expiring (e.g. internal licences)")
    evidence_ref = fields.Char(
        string="Evidence Reference",
        help="Pointer into M24 documents — the certificate artefact")
    status = fields.Selection(
        [("active", "Active"), ("expiring", "Expiring Soon"),
         ("expired", "Expired")],
        compute="_compute_status", store=True)

    @api.depends("expires_on")
    def _compute_status(self):
        today = fields.Date.today()
        for rec in self:
            if not rec.expires_on:
                rec.status = "active"
            elif rec.expires_on < today:
                rec.status = "expired"
            elif (rec.expires_on - today).days <= EXPIRING_WINDOW_DAYS:
                rec.status = "expiring"
            else:
                rec.status = "active"

    def action_grant(self):
        for rec in self:
            publish(self.env, "certification.granted", "fix.certification",
                    rec.id, {"employee": rec.employee_id.name,
                             "competency": rec.competency_id.code})

    def action_mark_expired(self):
        """Manual sweep for certifications whose expiry passed in place."""
        for rec in self:
            if rec.status == "expired":
                publish(self.env, "certification.expired",
                        "fix.certification", rec.id,
                        {"employee": rec.employee_id.name,
                         "competency": rec.competency_id.code})

    @api.model
    def dispatch_eligibility(self, employee, device_type=None):
        """FR-LMS-039 — the dispatch eligibility check.

        Returns (eligible: bool, reason: str). A technician is eligible for
        a device type when they hold an ACTIVE certification in a dispatch-
        gating competency whose scope matches. This is the check the W2
        seam stubbed to 'eligible' — the stub is CLOSED.
        """
        if not employee:
            return False, "no technician assigned"
        certs = self.search([("employee_id", "=", employee.id),
                             ("status", "=", "active")])
        gating = self.env["fix.competency"].search(
            [("required_for_dispatch", "=", True)])
        gating_by_id = {c.id: c for c in gating}
        held = {certs.competency_id.id}
        if device_type:
            scoped = [c for c in gating
                      if c.device_type and device_type in c.device_type]
            if scoped:
                for comp in scoped:
                    if comp.id in held:
                        return True, "certified for %s" % device_type
                return False, (
                    "FR-LMS-039: %s holds no ACTIVE certification for %s"
                    % (employee.name, device_type))
        # No device scope demanded: at least one gating competency held
        if held & set(gating_by_id):
            return True, "holds dispatch-gating certification"
        return False, (
            "FR-LMS-039: %s holds no dispatch-gating certification"
            % employee.name)


    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
class FixTrainingCourse(models.Model):
    _name = "fix.training.course"
    _description = "Training Course"
    # P03 workspace data-entry form (discovered by cd_p03_portal).
    _p03_capture = {
        "module": "M22",
        "form": "Course",
        "fields": ["code", "name", "name_bn", "content_ref", "competency_id"],
    }
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    code = fields.Char(required=True)
    name = fields.Char(required=True)
    name_bn = fields.Char(string="Course (Bengali)", help="DE-17")
    content_ref = fields.Char(
        string="Content Pack",
        help="project_content 08 pack (the 24 TR-* files) — loaded content "
             "pointer; authoring degrades without M61 (accepted)")
    competency_id = fields.Many2one("fix.competency",
                                    string="Certifies Towards")
    enrollment_ids = fields.One2many("fix.training.enrollment", "course_id",
                                     string="Enrollments")

    def action_enroll(self, employees):
        for rec in self:
            for emp in employees:
                self.env["fix.training.enrollment"].create({
                    "course_id": rec.id, "employee_id": emp.id})


    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
class FixTrainingEnrollment(models.Model):
    _name = "fix.training.enrollment"
    _description = "Training Enrollment"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    course_id = fields.Many2one("fix.training.course", required=True,
                                ondelete="cascade")
    employee_id = fields.Many2one("hr.employee", required=True)
    state = fields.Selection([("enrolled", "Enrolled"), ("passed", "Passed"),
                              ("failed", "Failed")],
                             default="enrolled", required=True)
    completed_on = fields.Date()

    def action_pass(self):
        for rec in self:
            rec.state = "passed"
            rec.completed_on = fields.Date.today()
            if rec.course_id.competency_id:
                self.env["fix.certification"].create({
                    "employee_id": rec.employee_id.id,
                    "competency_id": rec.course_id.competency_id.id,
                    "issued_on": fields.Date.today(),
                }).action_grant()
            publish(self.env, "training.passed", "fix.training.enrollment",
                    rec.id, {"employee": rec.employee_id.name,
                             "course": rec.course_id.code})


    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
class FixWorkOrderEligibilityExt(models.Model):
    """P08-M05-T04/T05: the M02 -> M22 AND M31 -> M22 stubs CLOSED —
    certification eligibility is now a BLOCKING check on the live
    assignment path (both field service and workshop share
    fix.work.order)."""
    _inherit = "fix.work.order"

    def action_check_certification(self):
        for rec in self:
            if not rec.technician_id:
                return True
            device_type = (
                rec.order_id.device_id.device_type if rec.order_id else None)
            eligible, reason = self.env[
                "fix.certification"].dispatch_eligibility(
                    rec.technician_id, device_type=device_type)
            if not eligible:
                raise UserError(
                    "M22 eligibility: assignment blocked — %s" % reason)
            return True

    def write(self, vals):
        result = super().write(vals)
        if vals.get("technician_id"):
            for rec in self:
                rec.action_check_certification()
        return result

    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")