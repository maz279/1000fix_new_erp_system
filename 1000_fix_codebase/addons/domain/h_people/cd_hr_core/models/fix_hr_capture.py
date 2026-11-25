# cd_hr_core - the M21 records the sub-module pages had no way to capture
# (M21 capture audit 2026-11-17).
#
# - Org Structure: the departments (hr.department) and job profiles (hr.job)
#   every employee already belongs to were on no screen, so a new department
#   or job title could only be made in Odoo's back office. A job profile now
#   carries its job family and band (FR-HCM-022) and a position names its
#   job, department and whether it is frozen (FR-HCM-023).
# - ESS / MSS: no employment privacy-notice acknowledgement existed anywhere
#   (FR-HCM-044 P0, BRU-HCM-12 H, AUT-HCM-02). fix.hr.notice.ack records which
#   published notice version an employee acknowledged, when and how, and a
#   withdrawal is a stamped transition, never an edit.
# - Exit Process: no exit interview (FR-HCM-038): the reason for leaving was
#   free text, so attrition could not be analysed by reason (spec 14).
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_hr_controls_common import OFFICER

JOB_FAMILIES = [
    ("field_service", "Field Service & Repair"),
    ("workshop", "Workshop & Bench Repair"),
    ("customer_service", "Customer Service & Contact Centre"),
    ("logistics", "Logistics, RMA & Courier"),
    ("sales", "Sales & Business Development"),
    ("quality", "Quality Assurance"),
    ("finance", "Finance & Accounts"),
    ("people", "People Management & Administration"),
    ("technology", "Technology & IT"),
    ("management", "Management & Leadership"),
]


class HrJobArchitecture(models.Model):
    """A job profile in the job architecture catalogue (FR-HCM-022)."""

    _inherit = "hr.job"

    fix_code = fields.Char(string="Job Code", index=True, copy=False)
    name_bn = fields.Char(string="Job Title (Bengali)")
    fix_job_family = fields.Selection(JOB_FAMILIES, string="Job Family")
    fix_job_band = fields.Selection(
        lambda self: self.env["hr.employee"]._fields["job_band"].selection,
        string="Grade / Band",
        help="The band of the job; the employee's own band is set on the employee record.",
    )

    _fix_code_unique = models.Constraint(
        "UNIQUE (fix_code, company_id)", "A job code is used once per company."
    )


class HrDepartmentStructure(models.Model):
    """A department of the organisation structure (FR-HCM-020)."""

    _inherit = "hr.department"

    fix_code = fields.Char(string="Department Code", index=True, copy=False)
    name_bn = fields.Char(string="Department Name (Bengali)")

    _fix_code_unique = models.Constraint(
        "UNIQUE (fix_code, company_id)", "A department code is used once per company."
    )


class FixOrgPositionArchitecture(models.Model):
    """A position names its job profile and department, and may be frozen
    (FR-HCM-023: filled, vacant, frozen)."""

    _inherit = "fix.org.position"

    job_id = fields.Many2one("hr.job", string="Job Profile", index=True)
    department_id = fields.Many2one("hr.department", string="Department", index=True)
    frozen = fields.Boolean(
        string="Frozen",
        tracking=True,
        help="A frozen position is not a vacancy: its empty seats are not offered to recruitment.",
    )

    @api.constrains("job_id", "company_id")
    def _check_job_company(self):
        for position in self:
            job = position.job_id
            if (
                job
                and job.company_id
                and position.company_id
                and job.company_id != position.company_id
            ):
                raise ValidationError(
                    "Position %s belongs to %s but its job profile %s belongs to %s."
                    % (position.name, position.company_id.name, job.name, job.company_id.name)
                )


class FixHrNoticeAck(models.Model):
    """An employee's acknowledgement of the employment privacy notice
    (FR-HCM-044, BRU-HCM-12, AUT-HCM-02).

    Captured once against a PUBLISHED notice version: what the employee saw is
    the notice's fixed wording (M33 refuses to edit a version with consents
    against it). A withdrawal of consent-based processing is a stamped
    transition; the acknowledgement row itself is never rewritten."""

    _name = "fix.hr.notice.ack"
    _description = "Employee Privacy Notice Acknowledgement"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "acknowledged_on desc, id desc"

    # what was acknowledged, by whom and how: history once captured
    _DECISION_FIELDS = ("employee_id", "notice_id", "acknowledged_on", "method")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "recorded_by_id",
            "withdrawn_on",
            "withdrawn_by_id",
            "withdrawal_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        return locked | set(self._DECISION_FIELDS) if self else locked

    name = fields.Char(compute="_compute_name", store=True, string="Reference")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company, index=True
    )
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, index=True, ondelete="restrict"
    )
    notice_id = fields.Many2one(
        "fix.transparency.notice",
        string="Notice Version",
        required=True,
        ondelete="restrict",
        domain=[("active", "=", True)],
        help="The published employment privacy notice the employee was shown.",
    )
    purposes = fields.Char(related="notice_id.purpose_set", string="Purposes Covered")
    acknowledged_on = fields.Date(
        string="Acknowledged On", required=True, default=fields.Date.context_today
    )
    method = fields.Selection(
        [
            ("signed_paper", "Signed Paper Copy"),
            ("self_service", "Employee Self-Service"),
            ("email", "Email Reply"),
            ("kiosk", "Branch Kiosk"),
        ],
        string="How It Was Acknowledged",
        required=True,
        default="signed_paper",
    )
    evidence_file = fields.Binary(string="Signed Copy / Evidence", attachment=True)
    evidence_filename = fields.Char(string="Evidence Filename")
    recorded_by_id = fields.Many2one("res.users", string="Recorded By", readonly=True)
    state = fields.Selection(
        [("acknowledged", "Acknowledged"), ("withdrawn", "Consent Withdrawn")],
        default="acknowledged",
        required=True,
        tracking=True,
    )
    withdrawn_on = fields.Date(string="Withdrawn On", readonly=True)
    withdrawn_by_id = fields.Many2one("res.users", string="Withdrawal Recorded By", readonly=True)
    withdrawal_reason = fields.Char(string="Withdrawal (what the employee withdrew)", readonly=True)

    @api.depends("employee_id", "notice_id")
    def _compute_name(self):
        for ack in self:
            ack.name = "PNA/%s/v%s" % (
                ack.employee_id.employee_code or ack.employee_id.id or "?",
                ack.notice_id.version or "?",
            )

    @api.constrains("acknowledged_on")
    def _check_not_future(self):
        today = fields.Date.context_today(self)
        for ack in self:
            if ack.acknowledged_on and ack.acknowledged_on > today:
                raise ValidationError("An acknowledgement cannot be dated in the future.")

    @api.constrains("employee_id", "notice_id", "state")
    def _check_one_live(self):
        for ack in self.filtered(lambda a: a.state == "acknowledged"):
            twin = self.search_count(
                [
                    ("id", "!=", ack.id),
                    ("employee_id", "=", ack.employee_id.id),
                    ("notice_id", "=", ack.notice_id.id),
                    ("state", "=", "acknowledged"),
                ]
            )
            if twin:
                raise ValidationError(
                    "%s has already acknowledged notice v%s."
                    % (ack.employee_id.name, ack.notice_id.version)
                )

    @api.model_create_multi
    def create(self, vals_list):
        notices = self.env["fix.transparency.notice"]
        for vals in vals_list:
            notice = notices.browse(vals.get("notice_id")).exists()
            # a retired or unpublished version is not what the employee is shown
            if notice and not notice.active:
                raise UserError(
                    "Notice v%s is not a published, current version. Record the "
                    "acknowledgement against the version in force." % notice.version
                )
            if vals.get("method") == "signed_paper" and not vals.get("evidence_file"):
                raise UserError("A signed paper acknowledgement needs the signed copy attached.")
        records = super().create(vals_list)
        records._guarded().write({"recorded_by_id": self.env.uid})
        return records

    def write(self, vals):
        if not self._fix_guard_open():
            changed = {
                name
                for ack in self
                for name in set(self._DECISION_FIELDS) & set(vals)
                if ack._fix_guard_differs(name, vals[name], ack[name])
            }
            if changed:
                raise UserError(
                    "An acknowledgement cannot be edited once recorded (%s). Record a new "
                    "acknowledgement against the current notice instead."
                    % ", ".join(sorted(changed))
                )
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError(
                "An acknowledgement is evidence and is kept. Record a withdrawal instead."
            )
        return super().unlink()

    def action_withdraw(self, reason=None):
        """The employee withdraws consent-based processing (FR-HCM-044). The
        statutory processing of employment data continues regardless."""
        if not self.env.user.has_group(OFFICER):
            raise UserError("Only HR records a withdrawal.")
        reason = (reason or "").strip()
        if not reason:
            raise UserError("State what the employee withdrew.")
        for ack in self:
            if ack.state != "acknowledged":
                raise UserError("%s is already withdrawn." % ack.name)
            ack._guarded().write(
                {
                    "state": "withdrawn",
                    "withdrawn_on": fields.Date.context_today(self),
                    "withdrawn_by_id": self.env.uid,
                    "withdrawal_reason": reason,
                }
            )
            ack.message_post(body="Consent-based processing withdrawn: %s" % reason)
        return True


class HrEmployeeNoticeAck(models.Model):
    _inherit = "hr.employee"

    notice_ack_ids = fields.One2many("fix.hr.notice.ack", "employee_id", string="Privacy Notices")

    def fix_privacy_notice_acknowledged(self):
        """The employees (of self) holding a live acknowledgement of a notice
        version that is still in force."""
        acks = self.env["fix.hr.notice.ack"].search(
            [
                ("employee_id", "in", self.ids),
                ("state", "=", "acknowledged"),
                ("notice_id.active", "=", True),
            ]
        )
        return acks.mapped("employee_id")


LEAVING_REASONS = [
    ("compensation", "Pay & Benefits"),
    ("career_growth", "Career Growth"),
    ("manager", "Relationship with Manager"),
    ("workload", "Workload & Hours"),
    ("work_environment", "Work Environment & Safety"),
    ("relocation", "Relocation"),
    ("higher_studies", "Higher Studies"),
    ("health", "Health"),
    ("family", "Family Reasons"),
    ("contract_end", "End of Contract"),
    ("retirement", "Retirement"),
    ("other", "Other"),
]
RATING = [
    ("1", "1 - Very Poor"),
    ("2", "2 - Poor"),
    ("3", "3 - Fair"),
    ("4", "4 - Good"),
    ("5", "5 - Very Good"),
]


class FixHrExitInterview(models.Model):
    """The structured exit interview of one exit (FR-HCM-038): the reason for
    leaving and the leaver's ratings, for attrition analysis by reason."""

    _name = "fix.hr.exit.interview"
    _description = "Exit Interview"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "interview_date desc, id desc"

    _ANSWER_FIELDS = (
        "exit_id",
        "interview_date",
        "interviewer_id",
        "primary_reason",
        "secondary_reason",
        "rating_manager",
        "rating_pay",
        "rating_workload",
        "rating_growth",
        "rating_environment",
        "would_rejoin",
        "would_recommend",
        "comments",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "recorded_on"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state == "recorded":
            locked |= set(self._ANSWER_FIELDS)
        return locked

    name = fields.Char(compute="_compute_name", store=True, string="Reference")
    company_id = fields.Many2one(related="exit_id.company_id", store=True, index=True)
    exit_id = fields.Many2one(
        "fix.hr.exit", string="Exit", required=True, ondelete="cascade", index=True
    )
    employee_id = fields.Many2one(
        related="exit_id.employee_id", store=True, string="Employee", index=True
    )
    exit_type = fields.Selection(related="exit_id.exit_type", string="Exit Type")
    interview_date = fields.Date(
        string="Interview Date", required=True, default=fields.Date.context_today
    )
    interviewer_id = fields.Many2one(
        "res.users", string="Interviewer", required=True, default=lambda self: self.env.user
    )
    primary_reason = fields.Selection(
        LEAVING_REASONS, string="Main Reason for Leaving", required=True
    )
    secondary_reason = fields.Selection(LEAVING_REASONS, string="Second Reason")
    rating_manager = fields.Selection(RATING, string="Line Manager")
    rating_pay = fields.Selection(RATING, string="Pay & Benefits")
    rating_workload = fields.Selection(RATING, string="Workload & Hours")
    rating_growth = fields.Selection(RATING, string="Growth & Training")
    rating_environment = fields.Selection(RATING, string="Work Environment & Safety")
    would_rejoin = fields.Boolean(string="Would Rejoin 1000FiX")
    would_recommend = fields.Boolean(string="Would Recommend 1000FiX as an Employer")
    comments = fields.Text(string="Leaver's Comments")
    state = fields.Selection(
        [("draft", "Draft"), ("recorded", "Recorded")],
        default="draft",
        required=True,
        tracking=True,
    )
    recorded_on = fields.Datetime(string="Recorded On", readonly=True)

    _exit_unique = models.Constraint("UNIQUE (exit_id)", "An exit has one exit interview.")

    @api.depends("exit_id")
    def _compute_name(self):
        for rec in self:
            rec.name = "EXI/%s" % (rec.exit_id.name or "?")

    @api.constrains("exit_id", "interviewer_id", "secondary_reason", "primary_reason")
    def _check_interview(self):
        for rec in self:
            if rec.exit_id.state == "cancelled":
                raise ValidationError(
                    "Exit %s is cancelled: there is no leaver to interview." % rec.exit_id.name
                )
            leaver_user = rec.exit_id.employee_id.user_id
            if leaver_user and rec.interviewer_id == leaver_user:
                raise ValidationError("The leaver cannot interview themselves.")
            if rec.secondary_reason and rec.secondary_reason == rec.primary_reason:
                raise ValidationError("The second reason repeats the main reason.")

    def write(self, vals):
        if not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state == "recorded"):
                changed = {
                    name
                    for name in set(self._ANSWER_FIELDS) & set(vals)
                    if rec._fix_guard_differs(name, vals[name], rec[name])
                }
                if changed:
                    raise UserError(
                        "Exit interview %s is recorded and cannot be edited." % rec.name
                    )
        return super().write(vals)

    def action_record(self):
        if not self.env.user.has_group(OFFICER):
            raise UserError("Only HR records an exit interview.")
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is already recorded." % rec.name)
            rec._guarded().write({"state": "recorded", "recorded_on": fields.Datetime.now()})
        return True
