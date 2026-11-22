# fix_wfm_capture - M55 capture audit (2026-11-17): the three records the
# workspace pages had no capture for.
#
#   fix.oncall.callout     FR-WFM-044 "on-call rota with allowance and callout
#                          recording": a callout inside an active or finished
#                          on-call window, recorded by the person on call (or a
#                          supervisor) and verified by the line manager or an
#                          attendance officer - never by the person on call or
#                          the recorder.
#   fix.capacity.forecast  FR-WFM-048/049: available capacity by branch and
#                          skill for a period, MEASURED from the roster (leave
#                          days out; with a skill, only people holding a valid
#                          certification of it on the day) against the demand
#                          forecast; publishing it alerts the attendance
#                          supervisors when demand exceeds capacity.
#   fix.timesheet.line     FR-WFM-050: time allocated to a project (M67), a
#                          contract (M05), a work order or a cost centre, never
#                          more than the verified attendance of that day,
#                          approved by the line manager.
#
# A locked attendance period is closed to all three (BRU-WFM-10).
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_attendance import (
    APPROVER_GROUP,
    PAYABLE_STATES,
    SUPERVISOR_GROUP,
    _day_bounds,
    _locked_lock,
)

# a forecast covers a planning period, not a year of roster rows
MAX_FORECAST_DAYS = 93


def _refuse_locked(env, company, day, what):
    lock = _locked_lock(env, company, day)
    if lock:
        raise UserError(
            "%s falls in locked attendance period %s: a correction is carried into the next "
            "period (BRU-WFM-10)." % (what, lock.name)
        )


def _changes_after_draft(records, vals, terms):
    """True when a caller outside a transition changes `terms` on a record
    that has left draft."""
    return bool(
        records
        and set(terms) & set(vals)
        and not records._fix_guard_open()
        and records.filtered(lambda r: r.state != "draft")
    )


def _attendance_role(env):
    """Supervisors, attendance officers and HR record for other people."""
    user = env.user
    return env.su or user.fix_reads_all_attendance()


class FixOncallCallout(models.Model):
    """One callout during an on-call / standby window (FR-WFM-044)."""

    _name = "fix.oncall.callout"
    _description = "On-Call Callout"
    _inherit = ["mail.thread", "fix.people.approval.mixin", "fix.people.inbox.decide.mixin"]
    _order = "called_at desc, id desc"

    _approval_domain = "hr_attendance"
    _approval_apply_method = "action_approve"
    _approval_group = APPROVER_GROUP
    _approval_manager_first = True

    name = fields.Char(default="New", readonly=True, copy=False)
    oncall_id = fields.Many2one(
        "fix.hr.oncall",
        string="On-Call / Standby",
        required=True,
        index=True,
        ondelete="restrict",
    )
    company_id = fields.Many2one(
        "res.company",
        related="oncall_id.company_id",
        store=True,
        index=True,
        string="Company",
    )
    operating_unit_id = fields.Many2one(
        "operating.unit", related="oncall_id.operating_unit_id", store=True, string="Operating Unit"
    )
    employee_id = fields.Many2one(
        "hr.employee",
        related="oncall_id.employee_id",
        store=True,
        index=True,
        string="Called Out",
    )
    called_at = fields.Datetime(string="Called At", required=True)
    caller = fields.Char(string="Raised By (caller or channel)")
    work_order_id = fields.Many2one("fix.work.order", string="Work Order", ondelete="set null")
    description = fields.Text(string="What Was Done", required=True)
    arrived_at = fields.Datetime(string="Arrived On Site At")
    finished_at = fields.Datetime(string="Finished At", required=True)
    hours = fields.Float(string="Callout Hours", compute="_compute_hours", store=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Awaiting Verification"),
            ("verified", "Verified"),
            ("rejected", "Rejected"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        readonly=True,
        tracking=True,
        index=True,
    )
    submitted_at = fields.Datetime(readonly=True, copy=False)
    verified_by_id = fields.Many2one("res.users", string="Verified By", readonly=True, copy=False)
    verified_at = fields.Datetime(string="Verified At", readonly=True, copy=False)
    rejection_reason = fields.Text(readonly=True, copy=False)

    _TERMS = frozenset(
        {"oncall_id", "called_at", "finished_at", "arrived_at", "work_order_id", "description"}
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "state",
            "submitted_at",
            "verified_by_id",
            "verified_at",
            "rejection_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= set(self._TERMS) | {"caller"}
        return locked

    @api.depends("called_at", "finished_at")
    def _compute_hours(self):
        for rec in self:
            if rec.called_at and rec.finished_at and rec.finished_at > rec.called_at:
                rec.hours = round((rec.finished_at - rec.called_at).total_seconds() / 3600.0, 2)
            else:
                rec.hours = 0.0

    @api.constrains("oncall_id", "called_at", "arrived_at", "finished_at")
    def _check_window(self):
        for rec in self:
            oc = rec.oncall_id.sudo()
            if rec.finished_at <= rec.called_at:
                raise ValidationError("A callout finishes after it was called.")
            if rec.arrived_at and not (rec.called_at <= rec.arrived_at <= rec.finished_at):
                raise ValidationError("The arrival lies between the call and the finish.")
            if not (oc.date_from <= rec.called_at <= oc.date_to):
                raise ValidationError(
                    "%s was not on call at %s: the window of %s is %s to %s."
                    % (oc.employee_id.name, rec.called_at, oc.name, oc.date_from, oc.date_to)
                )

    @api.constrains("oncall_id", "called_at", "finished_at", "state")
    def _check_no_overlap(self):
        for rec in self.filtered(lambda r: r.state not in ("rejected", "cancelled")):
            if self.sudo().search_count(
                [
                    ("id", "!=", rec.id),
                    ("oncall_id", "=", rec.oncall_id.id),
                    ("state", "not in", ("rejected", "cancelled")),
                    ("called_at", "<", rec.finished_at),
                    ("finished_at", ">", rec.called_at),
                ]
            ):
                raise ValidationError("%s overlaps another callout of the same on-call." % rec.name)

    def _fix_check_open(self):
        for rec in self:
            oc = rec.oncall_id.sudo()
            if oc.state not in ("active", "completed"):
                raise UserError(
                    "%s is %s: a callout is recorded on an on-call that was started."
                    % (oc.name, oc.state)
                )
            _refuse_locked(rec.env, rec.company_id, rec.called_at.date(), "This callout")

    @api.model_create_multi
    def create(self, vals_list):
        # who may record (the person on call, their manager, an attendance
        # role) is the global rule rule_oncall_callout_own, checked on create
        recs = super().create(vals_list)
        recs._fix_check_open()
        for rec in recs:
            rec._guarded().write(
                {"name": self.env["ir.sequence"].next_by_code("fix.oncall.callout") or "CALL/New"}
            )
        return recs

    def write(self, vals):
        if _changes_after_draft(self, vals, set(self._TERMS) | {"caller"}):
            raise UserError("A callout is changed only in draft: cancel it and record it again.")
        res = super().write(vals)
        if {"oncall_id", "called_at"} & set(vals):
            self._fix_check_open()
        return res

    # ---- transitions -------------------------------------------------------------
    def action_submit(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft callout is submitted.")
            rec._fix_check_open()
            rec._guarded().write({"state": "submitted", "submitted_at": fields.Datetime.now()})
            rec.action_request_approval()
        return True

    def action_approve(self):
        """Applied by the M63 engine in the verifier's environment."""
        self._approval_assert_routed()
        self._people_assert_not_conflicted()
        decider = self._people_decider()
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Only a submitted callout is verified.")
            rec._fix_check_open()
            rec.sudo()._guarded().write(
                {
                    "state": "verified",
                    "verified_by_id": decider.id,
                    "verified_at": fields.Datetime.now(),
                }
            )
        return True

    def _approval_on_rejected(self, comment):
        for rec in self:
            rec.sudo()._guarded().write(
                {
                    "state": "rejected",
                    "verified_by_id": rec._people_decider().id,
                    "verified_at": fields.Datetime.now(),
                    "rejection_reason": comment or False,
                }
            )

    def action_reject(self, reason=None):
        if not (reason or "").strip():
            raise UserError("State why this callout is rejected.")
        return self.action_inbox_reject(reason=reason)

    def action_cancel(self):
        user = self.env.user
        for rec in self:
            if rec.state not in ("draft", "submitted"):
                raise UserError("%s is %s and cannot be cancelled." % (rec.name, rec.state))
            if not (rec.create_uid == user or _attendance_role(self.env)):
                raise UserError(
                    "Only the recorder or an attendance supervisor cancels %s." % rec.name
                )
            if rec.approval_state == "pending":
                rec.approval_request_id.sudo()._finish(
                    "recalled", "recalled", user, record_state="none"
                )
            rec._guarded().write({"state": "cancelled"})
        return True

    # --- M55-F3 (attendance side): the verified callout hours payroll reads -------
    @api.model
    def _fix_payroll_verified_callout_hours(self, employee, date_from, date_to):
        """VERIFIED callout hours of `employee` for callouts CALLED inside
        [date_from, date_to] (FR-WFM-044: verified by someone other than the
        person on call and the recorder — the standby allowance itself reaches
        payroll through fix.hr.oncall.approved_allowance). Superuser read:
        payroll must see every operating unit."""
        end = fields.Date.to_date(date_to) + timedelta(days=1)
        callouts = self.sudo().search(
            [
                ("employee_id", "=", employee.id),
                ("state", "=", "verified"),
                ("called_at", ">=", fields.Datetime.to_datetime(date_from)),
                ("called_at", "<", fields.Datetime.to_datetime(end)),
            ]
        )
        return round(sum(callouts.mapped("hours")), 2)


class FixCapacityForecast(models.Model):
    """Forecast capacity by branch and skill against forecast demand (FR-WFM-048/049)."""

    _name = "fix.capacity.forecast"
    _description = "Capacity Forecast"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "date_from desc, id desc"

    name = fields.Char(default="New", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    branch_id = fields.Many2one("fix.branch", string="Branch", required=True, index=True)
    competency_id = fields.Many2one(
        "fix.competency",
        string="Skill",
        ondelete="restrict",
        help="Empty: every rostered person. Set: only people holding a valid certification "
        "of this competency on the day (FR-WFM-047).",
    )
    date_from = fields.Date(string="Period From", required=True)
    date_to = fields.Date(string="Period To", required=True)
    demand_hours = fields.Float(string="Forecast Demand (hours)", required=True)
    demand_basis = fields.Text(
        string="Demand Basis",
        required=True,
        help="Where the demand figure comes from: job history, a campaign (M35), contract volumes.",
    )
    rostered_hours = fields.Float(string="Rostered Hours", readonly=True, copy=False)
    leave_hours = fields.Float(string="On Approved Leave (hours)", readonly=True, copy=False)
    available_hours = fields.Float(string="Available Hours", readonly=True, copy=False)
    people_count = fields.Integer(string="People Rostered", readonly=True, copy=False)
    gap_hours = fields.Float(
        string="Gap (demand - available)",
        readonly=True,
        copy=False,
        help="Positive: demand the roster cannot meet.",
    )
    gap_pct = fields.Float(string="Gap %", readonly=True, copy=False)
    gap_flag = fields.Boolean(string="Demand Exceeds Capacity", readonly=True, copy=False)
    measured_at = fields.Datetime(readonly=True, copy=False)
    state = fields.Selection(
        [("draft", "Draft"), ("published", "Published"), ("superseded", "Superseded")],
        default="draft",
        required=True,
        readonly=True,
        tracking=True,
        index=True,
    )
    published_by_id = fields.Many2one("res.users", string="Published By", readonly=True, copy=False)
    published_at = fields.Datetime(readonly=True, copy=False)
    superseded_by_id = fields.Many2one(
        "fix.capacity.forecast", string="Superseded By", readonly=True, copy=False
    )

    _MEASURES = frozenset(
        {
            "rostered_hours",
            "leave_hours",
            "available_hours",
            "people_count",
            "gap_hours",
            "gap_pct",
            "gap_flag",
            "measured_at",
        }
    )
    _SCOPE = frozenset(
        {
            "company_id",
            "operating_unit_id",
            "branch_id",
            "competency_id",
            "date_from",
            "date_to",
            "demand_hours",
            "demand_basis",
        }
    )

    def _fix_guarded_fields(self) -> set:
        return (
            super()._fix_guarded_fields()
            | set(self._MEASURES)
            | {"name", "state", "published_by_id", "published_at", "superseded_by_id"}
        )

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= set(self._SCOPE)
        return locked

    @api.constrains("date_from", "date_to", "demand_hours")
    def _check_period(self):
        for rec in self:
            if rec.date_to < rec.date_from:
                raise ValidationError("The period ends on or after it starts.")
            if (rec.date_to - rec.date_from).days + 1 > MAX_FORECAST_DAYS:
                raise ValidationError(
                    "A capacity forecast covers at most %d days." % MAX_FORECAST_DAYS
                )
            if rec.demand_hours < 0:
                raise ValidationError("Forecast demand is not negative.")

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        for rec in recs:
            rec._guarded().write(
                {"name": self.env["ir.sequence"].next_by_code("fix.capacity.forecast") or "CAP/New"}
            )
        return recs

    def write(self, vals):
        if _changes_after_draft(self, vals, self._SCOPE):
            raise UserError("A published forecast is final: start a new one for the same scope.")
        return super().write(vals)

    # ---- measurement ---------------------------------------------------------------
    def _fix_skilled(self, employees, day):
        """The employees holding a valid certification of the skill on `day`."""
        self.ensure_one()
        if not self.competency_id:
            return employees
        certs = (
            self.env["fix.certification"]
            .sudo()
            .search(
                [
                    ("employee_id", "in", employees.ids),
                    ("competency_id", "=", self.competency_id.id),
                    ("state", "=", "valid"),
                    ("issued_on", "<=", day),
                    "|",
                    ("expires_on", "=", False),
                    ("expires_on", ">=", day),
                ]
            )
        )
        return certs.mapped("employee_id")

    def _fix_measure_values(self):
        self.ensure_one()
        slots = (
            self.env["fix.roster.slot"]
            .sudo()
            .search(
                [
                    ("company_id", "=", self.company_id.id),
                    ("branch_id", "=", self.branch_id.id),
                    ("date", ">=", self.date_from),
                    ("date", "<=", self.date_to),
                ]
            )
        )
        rostered = leave = 0.0
        people = set()
        by_day = {}
        for slot in slots:
            by_day.setdefault(slot.date, self.env["fix.roster.slot"].sudo())
            by_day[slot.date] |= slot
        for day, day_slots in by_day.items():
            skilled = self._fix_skilled(day_slots.mapped("employee_id"), day)
            for slot in day_slots.filtered(lambda s, sk=skilled: s.employee_id in sk):
                hours = slot.shift_id._fix_duration()
                rostered += hours
                people.add(slot.employee_id.id)
                if slot.on_leave:
                    leave += hours
        available = rostered - leave
        gap = self.demand_hours - available
        return {
            "rostered_hours": round(rostered, 2),
            "leave_hours": round(leave, 2),
            "available_hours": round(available, 2),
            "people_count": len(people),
            "gap_hours": round(gap, 2),
            "gap_pct": round(100.0 * gap / self.demand_hours, 1) if self.demand_hours else 0.0,
            "gap_flag": gap > 0,
            "measured_at": fields.Datetime.now(),
        }

    def action_measure(self):
        """Read the roster for the period (draft forecasts only)."""
        for rec in self:
            if rec.state != "draft":
                raise UserError(
                    "%s is %s: its figures are what was published." % (rec.name, rec.state)
                )
            rec._guarded().write(rec._fix_measure_values())
        return True

    def action_publish(self):
        """Measure, freeze, supersede the previous published forecast of the
        same scope, and alert the supervisors when demand exceeds capacity."""
        user = self.env.user
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft forecast is published.")
            rec._guarded().write(rec._fix_measure_values())
            older = self.sudo().search(
                [
                    ("id", "!=", rec.id),
                    ("state", "=", "published"),
                    ("company_id", "=", rec.company_id.id),
                    ("branch_id", "=", rec.branch_id.id),
                    ("competency_id", "=", rec.competency_id.id),
                    ("date_from", "<=", rec.date_to),
                    ("date_to", ">=", rec.date_from),
                ]
            )
            older._guarded().write({"state": "superseded", "superseded_by_id": rec.id})
            rec._guarded().write(
                {
                    "state": "published",
                    "published_by_id": user.id,
                    "published_at": fields.Datetime.now(),
                }
            )
            if rec.gap_flag:
                rec._fix_alert_gap()
        return True

    def _fix_alert_gap(self):
        """FR-WFM-049: a to-do for every attendance supervisor of the company."""
        self.ensure_one()
        group = self.env.ref(SUPERVISOR_GROUP, raise_if_not_found=False)
        users = (group.sudo().user_ids if group else self.env["res.users"]).filtered(
            lambda u: u.active and not u.share and self.company_id in u.company_ids
        )
        summary = "Capacity gap: %s%s %s to %s" % (
            self.branch_id.name,
            " (%s)" % self.competency_id.name if self.competency_id else "",
            self.date_from,
            self.date_to,
        )
        note = "Forecast demand %.1f h, available %.1f h: %.1f h short (%.1f%%)." % (
            self.demand_hours,
            self.available_hours,
            self.gap_hours,
            self.gap_pct,
        )
        self.sudo().message_post(body="%s. %s" % (summary, note))
        for user in users:
            self.sudo().activity_schedule(
                "mail.mail_activity_data_todo", summary=summary, note=note, user_id=user.id
            )


class FixTimesheetLine(models.Model):
    """Time allocated to a project, contract, work order or cost centre (FR-WFM-050)."""

    _name = "fix.timesheet.line"
    _description = "Timesheet Line"
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
    employee_id = fields.Many2one(
        "hr.employee",
        required=True,
        index=True,
        default=lambda self: self.env.user.employee_id,
    )
    date = fields.Date(required=True, index=True, default=fields.Date.context_today)
    hours = fields.Float(required=True)
    project_id = fields.Many2one("fix.project", string="Project (M67)", ondelete="restrict")
    contract_id = fields.Many2one(
        "fix.msp.contract", string="Managed-Service Contract (M05)", ondelete="restrict"
    )
    work_order_id = fields.Many2one("fix.work.order", string="Work Order", ondelete="restrict")
    cost_centre = fields.Char(
        string="Cost Centre",
        help="GL cost centre code. Empty: the employee's own cost centre, filled on save.",
    )
    description = fields.Text(string="Work Done", required=True)
    attended_hours = fields.Float(
        string="Attended That Day",
        compute="_compute_attended",
        help="Verified attendance hours of the day (manual entries count once approved).",
    )
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
    submitted_at = fields.Datetime(readonly=True, copy=False)
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True, copy=False)
    decided_at = fields.Datetime(readonly=True, copy=False)
    rejection_reason = fields.Text(readonly=True, copy=False)

    _TERMS = frozenset(
        {
            "employee_id",
            "date",
            "hours",
            "project_id",
            "contract_id",
            "work_order_id",
            "cost_centre",
            "description",
            "company_id",
        }
    )
    _LIVE = ("submitted", "approved")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "submitted_at",
            "decided_by_id",
            "decided_at",
            "rejection_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= set(self._TERMS)
        return locked

    @api.depends("employee_id", "date", "hours")
    def _compute_name(self):
        for rec in self:
            rec.name = "TS %s %s (%sh)" % (rec.employee_id.name or "", rec.date or "", rec.hours)

    def _fix_attended(self):
        self.ensure_one()
        start, end = _day_bounds(self.date)
        recs = (
            self.env["fix.attendance.record"]
            .sudo()
            .search(
                [
                    ("employee_id", "=", self.employee_id.id),
                    ("check_in", ">=", start),
                    ("check_in", "<", end),
                    ("approval_state", "in", PAYABLE_STATES),
                ]
            )
        )
        return round(sum(recs.mapped("worked_hours")), 2)

    @api.depends("employee_id", "date")
    def _compute_attended(self):
        for rec in self:
            rec.attended_hours = rec._fix_attended() if rec.employee_id and rec.date else 0.0

    @api.constrains("hours", "project_id", "contract_id", "work_order_id", "cost_centre")
    def _check_allocation(self):
        for rec in self:
            if rec.hours <= 0 or rec.hours > 24:
                raise ValidationError("Timesheet hours are more than 0 and at most 24.")
            if not (rec.project_id or rec.contract_id or rec.work_order_id or rec.cost_centre):
                raise ValidationError(
                    "Allocate the time to a project, a contract, a work order or a cost centre."
                )

    def _fix_check(self):
        for rec in self:
            _refuse_locked(rec.env, rec.company_id, rec.date, "%s" % rec.date)
            attended = rec._fix_attended()
            if not attended:
                raise UserError(
                    "%s has no verified attendance on %s: time is allocated from hours attended."
                    % (rec.employee_id.name, rec.date)
                )
            allocated = sum(
                self.sudo()
                .search(
                    [
                        ("id", "!=", rec.id),
                        ("employee_id", "=", rec.employee_id.id),
                        ("date", "=", rec.date),
                        ("state", "in", rec._LIVE),
                    ]
                )
                .mapped("hours")
            )
            if allocated + rec.hours > attended + 1e-6:
                raise UserError(
                    "%s attended %.2f h on %s; %.2f h are already allocated, so %.2f h more "
                    "cannot be." % (rec.employee_id.name, attended, rec.date, allocated, rec.hours)
                )

    def _fix_default_cost_centre(self, vals_list):
        Employee = self.env["hr.employee"].sudo()
        for vals in vals_list:
            if not vals.get("cost_centre") and vals.get("employee_id"):
                emp = Employee.browse(vals["employee_id"])
                if hasattr(emp, "_fix_effective_cost_centre"):
                    centre = emp._fix_effective_cost_centre()
                    if centre and not (
                        vals.get("project_id")
                        or vals.get("contract_id")
                        or vals.get("work_order_id")
                    ):
                        vals["cost_centre"] = centre

    @api.model_create_multi
    def create(self, vals_list):
        self._fix_default_cost_centre(vals_list)
        # who may record (the employee, their manager, an attendance role) is
        # the global rule rule_timesheet_line_own, checked on create
        recs = super().create(vals_list)
        for rec in recs:
            _refuse_locked(rec.env, rec.company_id, rec.date, "%s" % rec.date)
        return recs

    def write(self, vals):
        if _changes_after_draft(self, vals, self._TERMS):
            raise UserError(
                "A timesheet line is changed only in draft: cancel it and record it again."
            )
        return super().write(vals)

    # ---- transitions -------------------------------------------------------------
    def action_submit(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft timesheet line is submitted.")
            rec._fix_check()
            rec._guarded().write({"state": "submitted", "submitted_at": fields.Datetime.now()})
            rec.action_request_approval()
        return True

    def action_approve(self):
        """Applied by the M63 engine in the approver's environment."""
        self._approval_assert_routed()
        self._people_assert_not_conflicted()
        decider = self._people_decider()
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Only a submitted timesheet line is approved.")
            _refuse_locked(rec.env, rec.company_id, rec.date, "%s" % rec.date)
            rec.sudo()._guarded().write(
                {
                    "state": "approved",
                    "decided_by_id": decider.id,
                    "decided_at": fields.Datetime.now(),
                }
            )
        return True

    def _approval_on_rejected(self, comment):
        for rec in self:
            rec.sudo()._guarded().write(
                {
                    "state": "rejected",
                    "decided_by_id": rec._people_decider().id,
                    "decided_at": fields.Datetime.now(),
                    "rejection_reason": comment or False,
                }
            )

    def action_reject(self, reason=None):
        if not (reason or "").strip():
            raise UserError("State why this timesheet line is rejected.")
        return self.action_inbox_reject(reason=reason)

    def action_cancel(self):
        user = self.env.user
        for rec in self:
            if rec.state not in ("draft", "submitted", "approved"):
                raise UserError("%s is %s and cannot be cancelled." % (rec.name, rec.state))
            owner = rec.employee_id.sudo().user_id == user or rec.create_uid == user
            if not (owner or _attendance_role(self.env)):
                raise UserError(
                    "Only the employee, the recorder or a supervisor cancels %s." % rec.name
                )
            if rec.state == "approved":
                _refuse_locked(rec.env, rec.company_id, rec.date, "%s" % rec.date)
            if rec.approval_state == "pending":
                rec.approval_request_id.sudo()._finish(
                    "recalled", "recalled", user, record_state="none"
                )
            rec._guarded().write({"state": "cancelled"})
        return True
