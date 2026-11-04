# fix_attendance_approval — M55: routed decisions on attendance (A09 P0-b/P1/P2).
#
#   fix.attendance.regularisation  one routed decision on one pending record
#                                  (flagged clock-in, manual entry, changed hours)
#   fix.overtime.request           BRU-WFM-02/03: overtime approved BEFORE it is
#                                  paid; retrospective requests go to HR
#   fix.night.work.consent         BLA s.109: a woman's consent to night work
#
# Plus the leave hand-offs that need attendance: holidays are not charged as
# leave days, leave inside a locked attendance period is refused, approved
# leave sets the roster's on_leave, and the 'attendance' basis of the s.117
# accrual counts the days actually attended.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from .fix_attendance import (
    APPROVER_GROUP,
    SUPERVISOR_GROUP,
    _day_bounds,
    _locked_lock,
)

ATTENDANCE_ALL_READERS = (
    APPROVER_GROUP,
    "hr_attendance.group_hr_attendance_manager",
    SUPERVISOR_GROUP,
    "cd_attendance.group_attendance_lock_manager",
)
RETRO_GROUP = "hr.group_hr_manager"


class ResUsersAttendance(models.Model):
    _inherit = "res.users"

    def fix_reads_all_attendance(self):
        """True when this user reads every employee's attendance: the HR and
        payroll roles, and the attendance officers, supervisors and lock
        managers. Everyone else reads their own and their direct reports'."""
        self.ensure_one()
        if self.fix_reads_all_people():
            return True
        groups = [self.env.ref(x, raise_if_not_found=False) for x in ATTENDANCE_ALL_READERS]
        return any(g and g in self.sudo().all_group_ids for g in groups)


def _is_hr(env):
    return env.su or env.user.has_group("cd_hr_core.group_hr_officer")


class FixAttendanceRegularisation(models.Model):
    """One routed decision on one pending attendance record (FR-WFM-013)."""

    _name = "fix.attendance.regularisation"
    _description = "Attendance Regularisation"
    _inherit = ["fix.people.approval.mixin", "fix.people.inbox.decide.mixin"]
    _order = "id desc"
    _rec_name = "name"

    _approval_domain = "hr_attendance"
    _approval_apply_method = "action_approve"
    _approval_group = APPROVER_GROUP
    _approval_manager_first = True

    name = fields.Char(compute="_compute_name", store=True)
    record_id = fields.Many2one(
        "fix.attendance.record", required=True, index=True, ondelete="cascade", readonly=True
    )
    employee_id = fields.Many2one("hr.employee", required=True, index=True, readonly=True)
    company_id = fields.Many2one("res.company", required=True, index=True, readonly=True)
    operating_unit_id = fields.Many2one("operating.unit", readonly=True)
    # B5: what the decider sees is what the decision covers
    check_in_snapshot = fields.Datetime(string="Check-In", readonly=True)
    check_out_snapshot = fields.Datetime(string="Check-Out", readonly=True)
    worked_hours_snapshot = fields.Float(string="Worked Hours", readonly=True)
    reason = fields.Text(readonly=True)
    state = fields.Selection(
        [
            ("open", "Awaiting Decision"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("voided", "Voided by a Change"),
        ],
        default="open",
        required=True,
        readonly=True,
        index=True,
    )
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True)
    decided_at = fields.Datetime(readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "decided_by_id",
            "decided_at",
            "record_id",
            "employee_id",
            "check_in_snapshot",
            "check_out_snapshot",
            "worked_hours_snapshot",
            "reason",
            "company_id",
            "operating_unit_id",
        }

    @api.depends("employee_id", "check_in_snapshot")
    def _compute_name(self):
        for rec in self:
            rec.name = "REG %s @ %s" % (rec.employee_id.name or "", rec.check_in_snapshot or "")

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            raise AccessError("A regularisation is raised from its attendance record.")
        for vals in vals_list:
            att = self.env["fix.attendance.record"].sudo().browse(vals["record_id"])
            vals.update(
                {
                    "employee_id": att.employee_id.id,
                    "company_id": att.company_id.id,
                    "operating_unit_id": att.operating_unit_id.id,
                    "check_in_snapshot": att.check_in,
                    "check_out_snapshot": att.check_out,
                    "worked_hours_snapshot": att.worked_hours,
                }
            )
        return super(FixAttendanceRegularisation, self._guarded()).create(vals_list)

    def _fix_void(self, reason):
        for reg in self.filtered(lambda r: r.state == "open"):
            reg._approval_void(reason)
            reg._guarded().write({"state": "voided"})

    def _fix_assert_still_covers(self):
        self.ensure_one()
        att = self.record_id.sudo()
        if att.approval_state != "pending":
            raise UserError("%s is no longer pending." % att.display_label)
        if (att.check_in, att.check_out) != (self.check_in_snapshot, self.check_out_snapshot):
            raise UserError(
                "%s changed after this decision was requested; it is requested again."
                % att.display_label
            )
        lock = _locked_lock(self.env, att.company_id, att.check_in.date())
        if lock:
            raise UserError("%s lies in locked period %s." % (att.display_label, lock.name))

    def action_approve(self):
        """Applied by the M63 engine in the approver's environment."""
        self._approval_assert_routed()
        self._people_assert_not_conflicted()
        decider = self._people_decider()
        for reg in self:
            if reg.state != "open":
                raise UserError("%s is %s." % (reg.name, reg.state))
            reg._fix_assert_still_covers()
            reg._guarded().write(
                {
                    "state": "approved",
                    "decided_by_id": decider.id,
                    "decided_at": fields.Datetime.now(),
                }
            )
            reg.record_id.sudo()._fix_apply_decision(
                "approved", decider, "Approved by %s (%s)" % (decider.name, reg.name)
            )
        return True

    def _approval_on_rejected(self, comment):
        for reg in self.filtered(lambda r: r.state == "open"):
            decider = reg._people_decider()
            reg._guarded().write(
                {
                    "state": "rejected",
                    "decided_by_id": decider.id,
                    "decided_at": fields.Datetime.now(),
                }
            )
            att = reg.record_id.sudo()
            if att.approval_state == "pending":
                att._fix_apply_decision(
                    "rejected", decider, "Rejected by %s: %s" % (decider.name, comment or "")
                )


class FixOvertimeRequest(models.Model):
    """BRU-WFM-02/03, SOD-27: overtime is approved before it is paid.

    Payable overtime on a day = min(recorded excess, the approved hours of
    that day's request, the s.100/108 daily cap); an employee who is not
    overtime-eligible (s.2(65), `overtime_eligible`) has none. A request made
    after the day is RETROSPECTIVE: it needs a reason and goes to HR, not to
    the line manager (a higher authority, BRU-WFM-03)."""

    _name = "fix.overtime.request"
    _description = "Overtime Request"
    _inherit = ["mail.thread", "fix.people.approval.mixin", "fix.people.inbox.decide.mixin"]
    _order = "date desc, id desc"

    _approval_domain = "hr_attendance"
    _approval_apply_method = "action_approve"
    _approval_group = APPROVER_GROUP
    _approval_manager_first = True

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    date = fields.Date(required=True, index=True)
    hours = fields.Float(string="Hours Requested", required=True)
    rest_day_work = fields.Boolean(
        string="Weekly Rest-Day Work", help="All hours worked on a rest day are overtime."
    )
    reason = fields.Text(required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        readonly=True,
        tracking=True,
        index=True,
    )
    retrospective = fields.Boolean(readonly=True)
    submitted_at = fields.Datetime(readonly=True)
    approved_hours = fields.Float(readonly=True)
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True)
    decided_at = fields.Datetime(readonly=True)
    rejection_reason = fields.Text(readonly=True)
    cancelled_by_id = fields.Many2one("res.users", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "retrospective",
            "submitted_at",
            "approved_hours",
            "decided_by_id",
            "decided_at",
            "rejection_reason",
            "cancelled_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= {"employee_id", "date", "hours", "rest_day_work", "company_id", "reason"}
        return locked

    @api.depends("employee_id", "date", "hours")
    def _compute_name(self):
        for rec in self:
            rec.name = "OT %s %s (%sh)" % (rec.employee_id.name or "", rec.date or "", rec.hours)

    # ---- routing: retrospective -> HR -----------------------------------------
    def _approval_line_managers(self):
        if any(self.mapped("retrospective")):
            return self.env["res.users"]
        return super()._approval_line_managers()

    def _approval_group_xmlid(self):
        if any(self.mapped("retrospective")):
            return RETRO_GROUP
        return super()._approval_group_xmlid()

    # ---- rules -------------------------------------------------------------------
    def _fix_cap(self):
        self.ensure_one()
        # T-07: the caps of the working-time rule version in force that day
        rule = self.env["fix.working.time.rule"]._fix_values_for(self.company_id, self.date)
        return rule["daily_max_hours"] if self.rest_day_work else rule["daily_ot_cap_hours"]

    @api.constrains("hours", "rest_day_work")
    def _check_hours(self):
        for rec in self:
            if rec.hours <= 0:
                raise ValidationError("Overtime hours must be positive.")
            if rec.hours > rec._fix_cap():
                raise ValidationError(
                    "At most %.0f h of overtime a %s (BLA s.100/108): %.2f h requested."
                    % (rec._fix_cap(), "rest day" if rec.rest_day_work else "day", rec.hours)
                )

    @api.constrains("employee_id", "date", "state")
    def _check_one_live_request(self):
        for rec in self.filtered(lambda r: r.state in ("submitted", "approved")):
            if self.sudo().search_count(
                [
                    ("id", "!=", rec.id),
                    ("employee_id", "=", rec.employee_id.id),
                    ("date", "=", rec.date),
                    ("state", "in", ("submitted", "approved")),
                ]
            ):
                raise ValidationError(
                    "%s already has an overtime request for %s." % (rec.employee_id.name, rec.date)
                )

    def _fix_check(self):
        for rec in self:
            emp = rec.employee_id.sudo()
            if "overtime_eligible" in emp._fields and not emp.overtime_eligible:
                raise UserError(
                    "%s is not overtime-eligible (BLA s.2(65)/s.108): no overtime is approved."
                    % emp.name
                )
            rec._check_hours()
            lock = _locked_lock(rec.env, rec.company_id, rec.date)
            if lock:
                raise UserError(
                    "%s lies in locked attendance period %s: a correction is carried into the "
                    "next period." % (rec.date, lock.name)
                )

    def write(self, vals):
        if self and not self._fix_guard_open():
            terms = {"employee_id", "date", "hours", "rest_day_work", "company_id"} & set(vals)
            if terms and self.filtered(lambda r: r.state != "draft"):
                raise UserError(
                    "An overtime request is changed only in draft: cancel it and request again."
                )
        return super().write(vals)

    def _fix_revalue(self):
        Record = self.env["fix.attendance.record"].sudo()
        keys = []
        for rec in self:
            start, end = _day_bounds(rec.date)
            for att in Record.search(
                [
                    ("employee_id", "=", rec.employee_id.id),
                    ("check_in", ">=", start),
                    ("check_in", "<", end),
                ]
            ):
                keys.append(att._fix_day_key())
        Record._fix_recompute_days(keys)

    # ---- transitions ----------------------------------------------------------------
    def action_submit(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft overtime request is submitted.")
            rec._fix_check()
            retro = rec.date < today
            if retro and len((rec.reason or "").strip()) < 10:
                raise UserError(
                    "A retrospective overtime request (BRU-WFM-03) states in full why it was "
                    "not approved before the work."
                )
            rec._guarded().write(
                {
                    "state": "submitted",
                    "retrospective": retro,
                    "submitted_at": fields.Datetime.now(),
                }
            )
            rec.action_request_approval()
        return True

    def action_approve(self):
        """Applied by the M63 engine in the approver's environment."""
        self._approval_assert_routed()
        self._people_assert_not_conflicted()
        decider = self._people_decider()
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Only a submitted overtime request is approved.")
            rec._fix_check()
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_hours": rec.hours,
                    "decided_by_id": decider.id,
                    "decided_at": fields.Datetime.now(),
                }
            )
        self._fix_revalue()
        return True

    def _approval_on_rejected(self, comment):
        for rec in self:
            rec._guarded().write(
                {
                    "state": "rejected",
                    "decided_by_id": rec._people_decider().id,
                    "decided_at": fields.Datetime.now(),
                    "rejection_reason": comment or False,
                }
            )

    def action_reject(self, reason=None):
        if not (reason or "").strip():
            raise UserError("State why this overtime is rejected.")
        return self.action_inbox_reject(reason=reason)

    def action_cancel(self):
        user = self.env.user
        for rec in self:
            if rec.state not in ("draft", "submitted", "approved"):
                raise UserError("%s is %s and cannot be cancelled." % (rec.name, rec.state))
            owner = rec.employee_id.sudo().user_id == user or rec.create_uid == user
            if not (owner or _is_hr(self.env)):
                raise UserError("Only the requester or HR cancels %s." % rec.name)
            if rec.state == "approved":
                lock = _locked_lock(rec.env, rec.company_id, rec.date)
                if lock:
                    raise UserError("%s lies in locked period %s." % (rec.date, lock.name))
            if rec.approval_state == "pending":
                rec.approval_request_id.sudo()._finish(
                    "recalled", "recalled", user, record_state="none"
                )
            rec._guarded().write({"state": "cancelled", "cancelled_by_id": user.id})
        self._fix_revalue()
        return True


class FixNightWorkConsent(models.Model):
    """BLA s.109: a woman is not allowed to work between 10 p.m. and 6 a.m.
    without her consent. The consent is hers: confirmed by her own user, or by
    HR against her signed consent; she withdraws it at any time."""

    _name = "fix.night.work.consent"
    _description = "Night-Work Consent (BLA s.109)"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "date_from desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    consent_file = fields.Binary(string="Signed Consent", attachment=True)
    consent_file_name = fields.Char()
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Given"), ("withdrawn", "Withdrawn")],
        default="draft",
        required=True,
        readonly=True,
        tracking=True,
    )
    confirmed_by_id = fields.Many2one("res.users", string="Recorded By", readonly=True)
    confirmed_at = fields.Datetime(readonly=True)
    withdrawn_at = fields.Datetime(readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "confirmed_by_id",
            "confirmed_at",
            "withdrawn_at",
        }

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for rec in self:
            if rec.date_to < rec.date_from:
                raise ValidationError("The consent cannot end before it starts.")

    def write(self, vals):
        if (
            self
            and not self._fix_guard_open()
            and {"employee_id", "date_from", "date_to", "consent_file"} & set(vals)
            and self.filtered(lambda r: r.state != "draft")
        ):
            raise UserError("A given consent is not edited: withdraw it and record a new one.")
        return super().write(vals)

    @api.model
    def _fix_covering(self, employee, day):
        return self.sudo().search(
            [
                ("employee_id", "=", employee.id),
                ("state", "=", "active"),
                ("date_from", "<=", day),
                ("date_to", ">=", day),
            ],
            limit=1,
        )

    def _fix_assert_hers_or_hr(self):
        for rec in self:
            if rec.employee_id.sudo().user_id == self.env.user:
                continue
            if _is_hr(self.env):
                continue
            raise AccessError(
                "Night-work consent is recorded by the employee herself, or by HR from her "
                "signed consent."
            )

    def action_confirm(self):
        self._fix_assert_hers_or_hr()
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft consent is confirmed.")
            if rec.employee_id.sudo().sex != "female":
                raise UserError("BLA s.109 consent is recorded for a woman employee.")
            if rec.employee_id.sudo().user_id != self.env.user and not rec.consent_file:
                raise UserError("HR records a consent only against her signed consent document.")
            rec._guarded().write(
                {
                    "state": "active",
                    "confirmed_by_id": self.env.user.id,
                    "confirmed_at": fields.Datetime.now(),
                }
            )
        return True

    def action_withdraw(self):
        self._fix_assert_hers_or_hr()
        for rec in self:
            if rec.state != "active":
                raise UserError("Only a given consent is withdrawn.")
            rec._guarded().write({"state": "withdrawn", "withdrawn_at": fields.Datetime.now()})
        return True


class FixLeaveRequestAttendance(models.Model):
    """The leave hand-offs that need attendance (M55-6, M55-10, F11, F17)."""

    _inherit = "fix.leave.request"

    @api.depends("date_from", "date_to", "leave_type_id", "company_id")
    def _compute_days(self):
        Holiday = self.env["fix.hr.holiday"].sudo()
        for rec in self:
            if not (rec.date_from and rec.date_to and rec.date_to >= rec.date_from):
                rec.days = 0
                continue
            span = (rec.date_to - rec.date_from).days + 1
            if rec.leave_type_id.excludes_holidays:
                span -= Holiday.search_count(
                    [
                        ("company_id", "=", rec.company_id.id or self.env.company.id),
                        ("tentative", "=", False),
                        ("date", ">=", rec.date_from),
                        ("date", "<=", rec.date_to),
                    ]
                )
            rec.days = max(span, 0)

    def _fix_leave_check_period_open(self):
        super()._fix_leave_check_period_open()
        Lock = self.env["fix.attendance.lock"].sudo()
        for rec in self:
            lock = Lock.search(
                [
                    ("state", "=", "locked"),
                    ("company_id", "=", rec.company_id.id),
                    ("period_start", "<=", rec.date_to),
                    ("period_end", ">=", rec.date_from),
                ],
                limit=1,
            )
            if lock:
                raise UserError(
                    "%s falls in locked attendance period %s: a leave in a closed (and paid) "
                    "month is a correction carried into the next period."
                    % (rec.display_name, lock.name)
                )
        return True

    def _fix_leave_check_rules(self):
        super()._fix_leave_check_rules()
        Record = self.env["fix.attendance.record"].sudo()
        for rec in self:
            start, _e = _day_bounds(rec.date_from)
            _s, end = _day_bounds(rec.date_to)
            worked = Record.search(
                [
                    ("employee_id", "=", rec.employee_id.id),
                    ("approval_state", "!=", "rejected"),
                    ("worked_hours", ">", 0),
                    ("check_in", ">=", start),
                    ("check_in", "<", end),
                ]
            )
            if worked:
                days = sorted({str(r.check_in.date()) for r in worked})
                raise UserError(
                    "%s has attendance on %s: a day is either worked or on leave."
                    % (rec.employee_id.name, ", ".join(days))
                )

    def _fix_leave_after_decision(self):
        super()._fix_leave_after_decision()
        Slot = self.env["fix.roster.slot"].sudo()
        for rec in self:
            Slot.search(
                [
                    ("employee_id", "=", rec.employee_id.id),
                    ("date", ">=", rec.date_from),
                    ("date", "<=", rec.date_to),
                ]
            )._fix_sync_on_leave()
        return True


class HrEmployeeAttendanceDays(models.Model):
    _inherit = "hr.employee"

    def _fix_leave_days_worked(self, date_from, date_to):
        """The 'attendance' basis of the s.117 accrual: days with attendance."""
        self.ensure_one()
        if self.sudo().company_id.fix_annual_leave_basis != "attendance":
            return super()._fix_leave_days_worked(date_from, date_to)
        if date_to < date_from:
            return 0
        recs = (
            self.env["fix.attendance.record"]
            .sudo()
            .search(
                [
                    ("employee_id", "=", self.id),
                    ("approval_state", "in", ("not_required", "approved")),
                    ("worked_hours", ">", 0),
                    ("check_in", ">=", fields.Datetime.to_datetime(date_from)),
                    ("check_in", "<", fields.Datetime.to_datetime(date_to + timedelta(days=1))),
                ]
            )
        )
        return len({r.check_in.date() for r in recs})
