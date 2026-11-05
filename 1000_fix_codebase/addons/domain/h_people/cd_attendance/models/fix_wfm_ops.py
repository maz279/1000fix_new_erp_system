# fix_wfm_ops — M55: holiday calendar (incl. moon-dependent) and on-call /
# standby records. Attendance, rosters, devices and locks live in fix_attendance.py.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError

APPROVER_GROUP = "hr_attendance.group_hr_attendance_user"


class FixHrHoliday(models.Model):
    """Public / religious / moon-dependent holidays for the working calendar."""

    _name = "fix.hr.holiday"
    _description = "Holiday (moon-dependent aware)"
    _order = "date"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    date = fields.Date(required=True, index=True)
    name_bn = fields.Char(string="Holiday (Bengali)", help="DE-17")
    holiday_type = fields.Selection(
        [
            ("public", "Public Holiday"),
            ("religious", "Religious"),
            ("moon", "Moon-Dependent (subject to sighting)"),
            # BLA s.118: the eleven festival holidays with wages are days of the
            # calendar the employer fixes, not leave a worker requests
            ("festival", "Festival Holiday (BLA s.118)"),
            ("company", "Company Day"),
        ],
        required=True,
        default="public",
    )
    tentative = fields.Boolean(
        string="Tentative (sighting-dependent)",
        help="Moon-dependent dates are announced after the sighting; tentative rows are "
        "confirmed by clearing this flag.",
    )
    notes = fields.Char()

    _date_name = models.Constraint(
        "UNIQUE (date, company_id)", "One holiday record per date per company"
    )

    # FR-WFM-037: the calendar is APPLIED - to the leave day count and to the
    # valuation of the attendance worked that day (M55-12, F17, H4)
    def _fix_apply_calendar(self, keys):
        Leave = self.env["fix.leave.request"].sudo()
        Record = self.env["fix.attendance.record"].sudo()
        days = set()
        for company_id, day in keys:
            if not day:
                continue
            days.add(day)
            leaves = Leave.search(
                [
                    ("company_id", "=", company_id),
                    ("state", "in", ("draft", "submitted")),
                    ("date_from", "<=", day),
                    ("date_to", ">=", day),
                ]
            )
            if leaves:
                self.env.add_to_compute(Leave._fields["days"], leaves)
                leaves.flush_recordset()
            start = fields.Datetime.to_datetime(day)
            recs = Record.search(
                [
                    ("company_id", "=", company_id),
                    ("check_in", ">=", start),
                    ("check_in", "<", start + timedelta(days=1)),
                ]
            )
            Record._fix_recompute_days([r._fix_day_key() for r in recs])

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        recs._fix_apply_calendar([(r.company_id.id, r.date) for r in recs])
        return recs

    def write(self, vals):
        before = [(r.company_id.id, r.date) for r in self]
        res = super().write(vals)
        if {"date", "company_id", "tentative"} & set(vals):
            self._fix_apply_calendar(before + [(r.company_id.id, r.date) for r in self])
        return res

    def unlink(self):
        keys = [(r.company_id.id, r.date) for r in self]
        res = super().unlink()
        self.env["fix.hr.holiday"]._fix_apply_calendar(keys)
        return res


class FixHrOncall(models.Model):
    """On-call / standby shift with its allowance.

    I9 (A09 r2): the allowance is approved through the M63 engine by someone
    other than the person on call and the person who recorded it (line manager
    first, then the attendance officers); `approved_allowance` is pinned at
    approval and is what payroll pays. An allowance approved after payroll has
    frozen its month is carried forward as an attendance adjustment."""

    _name = "fix.hr.oncall"
    _description = "On-Call / Standby Shift"
    _inherit = ["fix.people.approval.mixin", "fix.people.inbox.decide.mixin"]
    _order = "date_from desc, id desc"

    _approval_domain = "hr_attendance"
    _approval_apply_method = "action_approve_allowance"
    _approval_group = APPROVER_GROUP
    _approval_manager_first = True

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)
    shift_id = fields.Many2one("fix.shift.template", string="Shift")
    date_from = fields.Datetime(required=True)
    date_to = fields.Datetime(required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    allowance = fields.Monetary(currency_field="currency_id", string="Standby Allowance")
    approved_allowance = fields.Monetary(
        currency_field="currency_id",
        string="Approved Allowance",
        readonly=True,
        copy=False,
        help="Pinned when the allowance is approved; payroll pays this figure (I9).",
    )
    allowance_approved_by_id = fields.Many2one(
        "res.users", string="Allowance Approved By", readonly=True, copy=False
    )
    allowance_approved_at = fields.Datetime(readonly=True, copy=False)
    phone = fields.Char(string="Contact Number")
    state = fields.Selection(
        [
            ("planned", "Planned"),
            ("active", "Active"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="planned",
        readonly=True,
    )

    _dates_ordered = models.Constraint(
        "CHECK (date_to >= date_from)", "On-call end cannot precede its start"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.hr.oncall") or "ONC/New"
        return super().create(vals_list)

    def _fix_guarded_fields(self) -> set:
        # A09 P3: the on-call state is the lifecycle, not a typed field
        return super()._fix_guarded_fields() | {
            "state",
            "approved_allowance",
            "allowance_approved_by_id",
            "allowance_approved_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and (self.state in ("completed", "cancelled") or self.approval_state == "approved"):
            locked |= {"employee_id", "date_from", "date_to", "allowance", "currency_id"}
        return locked

    def _approval_amount(self) -> float:
        return self.allowance or 0.0

    def write(self, vals):
        frozen = {"employee_id", "date_from", "date_to", "allowance", "currency_id"} & set(vals)
        if frozen and not self.env.su:
            done = self.filtered(lambda r: r.state in ("completed", "cancelled"))
            if done:
                raise UserError(
                    "On-call %s is %s: its employee, window and allowance are final."
                    % (done[0].name, done[0].state)
                )
            approved = self.filtered(lambda r: r.approval_state == "approved")
            if approved:
                raise UserError(
                    "The allowance of %s is approved: its employee, window and allowance are "
                    "what was approved." % approved[0].name
                )
        return super().write(vals)

    # ---- I9: the allowance decision -------------------------------------------------
    def action_submit_allowance(self):
        """Route the allowance for approval (never to the person on call or the
        person who recorded it)."""
        for rec in self:
            if rec.state == "cancelled":
                raise UserError("%s is cancelled: no allowance is approved." % rec.name)
            if (rec.allowance or 0.0) <= 0:
                raise UserError("%s has no allowance to approve." % rec.name)
            if rec.approval_state == "approved":
                raise UserError("The allowance of %s is already approved." % rec.name)
            rec.action_request_approval()
        return True

    def action_approve_allowance(self):
        """Applied by the M63 engine in the approver's environment."""
        self._approval_assert_routed()
        self._people_assert_not_conflicted()
        decider = self._people_decider()
        for rec in self:
            if rec.state == "cancelled":
                raise UserError("%s is cancelled." % rec.name)
            # the approver (a line manager) holds no write on on-call: the
            # transition writes as superuser after the routed checks above
            rec.sudo()._guarded().write(
                {
                    "approved_allowance": rec.allowance,
                    "allowance_approved_by_id": decider.id,
                    "allowance_approved_at": fields.Datetime.now(),
                }
            )
        self._fix_after_allowance_approved()
        return True

    def _fix_after_allowance_approved(self):
        """Hook (fix_attendance_adjustment): a late approval is carried forward."""
        return True

    def action_reject_allowance(self, reason=None):
        if not (reason or "").strip():
            raise UserError("State why this allowance is rejected.")
        return self.action_inbox_reject(reason=reason)

    def action_start(self):
        for rec in self:
            if rec.state != "planned":
                raise UserError("Start a planned on-call shift")
            rec._guarded().write({"state": "active"})

    def action_complete(self):
        for rec in self:
            if rec.state != "active":
                raise UserError("Complete an active on-call shift")
            rec._guarded().write({"state": "completed"})

    def action_cancel(self):
        # H2: a COMPLETED shift (allowance earned) is not cancelled away
        for rec in self:
            if rec.state not in ("planned", "active"):
                raise UserError(
                    "Only a planned or active on-call shift is cancelled (%s is %s)."
                    % (rec.name, rec.state)
                )
            rec._guarded().write({"state": "cancelled"})
