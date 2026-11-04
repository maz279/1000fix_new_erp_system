# cd_hr_core — M55 leave controls (A09 workflow audit P0-b, P1, P2).
#
# The leave models are defined in fix_hr_core.py; their approval, state guard,
# statutory rules and hand-offs are extended here so that the M21 and M55 work
# can change cd_hr_core without touching the same file.
#
# What the audit found (M55-1, M55-7, M55-10): the requester approved their own
# leave (ORM, the Approve button and /p03/model/write); a DRAFT was approved;
# an approved 2-day leave was stretched to 40 days; there was no reject or
# cancel; maternity was approved for a man and after 10 days' service; annual
# leave was a flat 20 days from day one; a second 'casual' type doubled the
# casual entitlement; overlapping and reversed-date leave passed; sick leave
# needed no certificate.
#
# The lifecycle now is:
#   draft --action_submit--> submitted (routed: line manager first, then HR)
#     --task approve--> approved (dates pinned) --action_cancel--> cancelled
#     --task reject-->  rejected (reason recorded)
#   draft/submitted --action_cancel--> cancelled
# Every rule is checked when the request is submitted AND again inside the
# approve transition, so a balance used up in between is caught.
from datetime import date, timedelta

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

# BLA 2006 s.46(1): a woman is entitled to maternity benefit only if she has
# worked for the employer for at least six months immediately preceding the
# day of her delivery (2013 text, Verified in the A09 benchmark).
MATERNITY_MIN_SERVICE_MONTHS = 6
# BLA 2006 s.46(2): no maternity benefit for a woman who has two or more
# surviving children at the time of confinement (2013 text).
MATERNITY_MAX_SURVIVING_CHILDREN = 1
# BLA 2006 s.117(1): one day of annual leave for every 18 days of work
# performed during the previous twelve months, after one year's service.
ANNUAL_LEAVE_DAYS_PER_EARNED_DAY = 18
ANNUAL_LEAVE_SERVICE_YEARS = 1

LIVE_STATES = ("submitted", "approved")
# Fields that change what was asked for; frozen once the request leaves draft.
REQUEST_TERMS = ("employee_id", "leave_type_id", "date_from", "date_to", "company_id")


class ResCompanyLeaveSettings(models.Model):
    _inherit = "res.company"

    # A09 decision (report §7): the BLA counts "days of work performed"; how
    # they are counted where attendance is not captured for everyone is a
    # company ruling. 'service' credits every day of service less one weekly
    # holiday in seven (s.103); 'attendance' counts the days with attendance.
    fix_annual_leave_basis = fields.Selection(
        [
            ("service", "Days of service, less one weekly holiday in seven"),
            ("attendance", "Days with recorded attendance"),
        ],
        string="Annual Leave: Days Worked Basis",
        default="service",
        required=True,
        help="BLA 2006 s.117(1): 1 day of annual leave per 18 days of work performed. "
        "Choose how the days of work are counted (A09 decision).",
    )


class FixLeaveTypeControls(models.Model):
    _name = "fix.leave.type"
    _inherit = ["fix.leave.type", "fix.guarded.mixin"]

    # A09 P8: the citation "verified on" date defaulted to today, so every new
    # type claimed a verification nobody made. It is now set only by
    # action_verify_citation, which records who verified it.
    verified_on = fields.Date(default=False)
    verified_by_id = fields.Many2one("res.users", string="Citation Verified By", readonly=True)
    excludes_holidays = fields.Boolean(
        string="Holidays Not Charged",
        default=True,
        help="Registered public holidays inside the leave are not counted as leave days "
        "(FR-WFM-037). Off for maternity, which runs in continuous weeks.",
    )
    requires_certificate = fields.Boolean(
        string="Medical Certificate Required",
        help="Approval needs a medical certificate attached (BLA s.116 for sick leave).",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"verified_on", "verified_by_id"}

    @api.constrains("code", "company_id")
    def _check_one_type_per_code(self):
        # M55-7 / F13: entitlement was counted per type ROW, so a second
        # 'casual' row gave 20 casual days.
        for rec in self:
            dup = self.sudo().search_count(
                [
                    ("id", "!=", rec.id),
                    ("code", "=", rec.code),
                    ("company_id", "=", rec.company_id.id),
                ]
            )
            if dup:
                raise ValidationError(
                    "A leave type with code '%s' already exists in %s: one type per code, "
                    "or its entitlement would be counted twice." % (rec.code, rec.company_id.name)
                )

    @api.model
    def _fix_seed_leave_rules(self):
        """Data hook (idempotent): sick needs a certificate; maternity counts
        every calendar day."""
        Type = self.sudo()
        Type.search([("code", "=", "sick"), ("requires_certificate", "=", False)]).write(
            {"requires_certificate": True}
        )
        Type.search(["|", ("code", "=", "maternity"), ("maternity", "=", True)]).filtered(
            "excludes_holidays"
        ).write({"excludes_holidays": False})
        return True

    def _fix_is_certificate_type(self):
        self.ensure_one()
        return self.requires_certificate or self.code == "sick"

    def action_verify_citation(self):
        """HR records that the statutory citation was checked today."""
        user = self.env.user
        if not (self.env.su or user.has_group("cd_hr_core.group_hr_officer")):
            raise UserError("Only an HR Officer verifies a leave type's statutory citation.")
        for rec in self:
            if not (rec.legal_citation and rec.labour_act_section):
                raise UserError(
                    "%s has no statutory section and citation to verify." % rec.display_name
                )
            rec._guarded().write(
                {"verified_on": fields.Date.context_today(rec), "verified_by_id": user.id}
            )
        return True

    def write(self, vals):
        # a changed citation is no longer the one that was verified
        if self and {"legal_citation", "labour_act_section"} & set(vals):
            res = super().write(vals)
            self.filtered("verified_on")._guarded().write(
                {"verified_on": False, "verified_by_id": False}
            )
            return res
        return super().write(vals)


class FixPeopleInboxDecide(models.AbstractModel):
    """Decide a routed record from its own screen: the caller's open inbox
    task for the record is approved or rejected. Nothing is decided that the
    engine did not route to the caller."""

    _name = "fix.people.inbox.decide.mixin"
    _description = "Decide a routed people record from its screen"

    def _fix_my_task(self):
        self.ensure_one()
        req = self.sudo().approval_request_id
        task = req.task_ids.filtered(
            lambda t: (
                t.state == "pending"
                and (t.assigned_user_id or t.assigned_to_id.user_id) == self.env.user
            )
        )[:1]
        if not task or req.state != "pending":
            approvers = ", ".join(
                (t.assigned_user_id or t.assigned_to_id.user_id).name or "?"
                for t in req.task_ids.filtered(lambda t: t.state == "pending")
            )
            raise UserError(
                "%s is not awaiting your decision%s."
                % (
                    self.display_name,
                    " (it is routed to %s)" % approvers if approvers else "",
                )
            )
        return self.env["fix.workflow.task"].browse(task.id)

    def action_inbox_approve(self):
        for rec in self:
            rec._fix_my_task().action_approve()
        return True

    def action_inbox_reject(self, reason=None):
        for rec in self:
            rec._fix_my_task().action_reject(comment=reason)
        return True


class FixLeaveRequestRouted(models.Model):
    """Leave is decided from the approver's inbox, never by the requester."""

    _name = "fix.leave.request"
    _inherit = ["fix.leave.request", "fix.people.approval.mixin", "fix.people.inbox.decide.mixin"]

    _approval_domain = "hr_leave"
    _approval_apply_method = "action_approve"
    _approval_group = "cd_hr_core.group_hr_officer"
    _approval_manager_first = True

    state = fields.Selection(
        selection_add=[("cancelled", "Cancelled")], ondelete={"cancelled": "set default"}
    )
    submitted_at = fields.Datetime(readonly=True, copy=False)
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True, copy=False)
    decided_at = fields.Datetime(string="Decided At", readonly=True, copy=False)
    rejection_reason = fields.Text(readonly=True, copy=False)
    cancelled_by_id = fields.Many2one("res.users", string="Cancelled By", readonly=True, copy=False)
    cancelled_at = fields.Datetime(readonly=True, copy=False)
    cancel_reason = fields.Text(readonly=True, copy=False)
    # B5: what the approval covered
    approved_date_from = fields.Date(readonly=True, copy=False)
    approved_date_to = fields.Date(readonly=True, copy=False)
    approved_days = fields.Integer(readonly=True, copy=False)
    # s.116: sick leave on a registered medical practitioner's certificate
    medical_certificate = fields.Binary(attachment=True, copy=False)
    medical_certificate_name = fields.Char(copy=False)
    # s.46-47: maternity is 8 weeks before and 8 weeks after the confinement
    expected_confinement_date = fields.Date(
        string="Expected Confinement Date", help="Maternity: the expected day of delivery."
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "submitted_at",
            "decided_by_id",
            "decided_at",
            "rejection_reason",
            "cancelled_by_id",
            "cancelled_at",
            "cancel_reason",
            "approved_date_from",
            "approved_date_to",
            "approved_days",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= set(REQUEST_TERMS) | {"expected_confinement_date"}
        return locked

    # ---- data rules that hold in every state ---------------------------------
    @api.constrains("date_from", "date_to")
    def _check_date_order(self):
        # F8: a reversed range gave 0 days, which passed every balance
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_to < rec.date_from:
                raise ValidationError(
                    "Leave cannot end (%s) before it starts (%s)." % (rec.date_to, rec.date_from)
                )

    def _fix_overlapping(self):
        self.ensure_one()
        return self.sudo().search(
            [
                ("id", "!=", self.id),
                ("employee_id", "=", self.employee_id.id),
                ("state", "in", LIVE_STATES),
                ("date_from", "<=", self.date_to),
                ("date_to", ">=", self.date_from),
            ],
            limit=1,
        )

    @api.constrains("date_from", "date_to", "employee_id", "state")
    def _check_no_overlap(self):
        # F7: two live leaves over the same days
        for rec in self.filtered(lambda r: r.state in LIVE_STATES):
            rec._fix_assert_no_overlap()

    def _fix_assert_no_overlap(self):
        for rec in self:
            other = rec._fix_overlapping()
            if other:
                raise ValidationError(
                    "%s already has %s (%s to %s, %s) over these dates."
                    % (
                        rec.employee_id.name,
                        other.leave_type_id.name,
                        other.date_from,
                        other.date_to,
                        other.state,
                    )
                )

    # ---- writes: terms frozen once submitted ---------------------------------
    def write(self, vals):
        if self and not self._fix_guard_open():
            terms = set(REQUEST_TERMS) & set(vals)
            if terms:
                for rec in self:
                    changed = [n for n in terms if rec._fix_guard_differs(n, vals[n], rec[n])]
                    if not changed or rec.state == "draft":
                        continue
                    if rec.state == "submitted":
                        raise UserError(
                            "%s is awaiting approval: recall it (Cancel) and submit a new "
                            "request to change its dates or type." % rec.display_name
                        )
                    raise UserError(
                        "%s is %s: its dates and type are what was decided and cannot change. "
                        "Cancel it and apply again." % (rec.display_name, rec.state)
                    )
        return super().write(vals)

    # ---- the rules -----------------------------------------------------------
    def _fix_leave_check_period_open(self):
        """Hook: refuse when the leave falls in a closed attendance period
        (cd_attendance overrides; core HR has no attendance lock)."""
        return True

    def _fix_leave_after_decision(self):
        """Hook: availability follow-up after approval or cancellation
        (cd_attendance overrides: roster on_leave)."""
        return True

    def _fix_year_taken(self, code, year):
        self.ensure_one()
        return sum(
            self.sudo()
            .search(
                [
                    ("id", "!=", self.id),
                    ("employee_id", "=", self.employee_id.id),
                    ("leave_type_id.code", "=", code),
                    ("company_id", "=", self.company_id.id),
                    ("state", "=", "approved"),
                    ("date_from", ">=", date(year, 1, 1)),
                    ("date_from", "<=", date(year, 12, 31)),
                ]
            )
            .mapped("days")
        )

    def _fix_check_maternity(self):
        self.ensure_one()
        emp = self.employee_id.sudo()
        if emp.sex != "female":
            raise UserError(
                "Maternity benefit is for a woman (BLA s.45-46): %s is recorded as %s."
                % (emp.name, emp.sex or "no sex recorded")
            )
        conf = self.expected_confinement_date
        if not conf:
            raise UserError("Maternity leave needs the expected confinement date (s.47).")
        start = emp._fix_service_start()
        if not start or start + relativedelta(months=MATERNITY_MIN_SERVICE_MONTHS) > conf:
            raise UserError(
                "Maternity benefit needs %d months' service before the delivery (BLA s.46(1)): "
                "%s joined %s, confinement %s."
                % (MATERNITY_MIN_SERVICE_MONTHS, emp.name, start or "on no recorded date", conf)
            )
        if (emp.children or 0) > MATERNITY_MAX_SURVIVING_CHILDREN:
            raise UserError(
                "No maternity benefit when the woman has two or more surviving children "
                "(BLA s.46(2)): %s has %d recorded." % (emp.name, emp.children)
            )
        half = (self.leave_type_id.entitlement_days or 0) // 2
        before = (conf - self.date_from).days
        after = (self.date_to - conf).days + 1
        if before > half or after > half:
            raise UserError(
                "Maternity is %d days before and %d days after the confinement (s.47): this "
                "request has %d before and %d from the confinement day."
                % (half, half, max(before, 0), max(after, 0))
            )

    def _fix_leave_check_rules(self):
        """Every rule a leave must meet to be submitted or approved."""
        for rec in self:
            ltype = rec.leave_type_id.sudo()
            ltype.action_validate_statutory()
            if ltype.company_id != rec.company_id:
                raise UserError("%s is not a leave type of %s." % (ltype.name, rec.company_id.name))
            if rec.date_to < rec.date_from:
                raise UserError("Leave cannot end before it starts.")
            if rec.days <= 0:
                raise UserError("%s charges no leave days." % rec.display_name)
            rec._fix_assert_no_overlap()
            rec._fix_leave_check_period_open()
            if ltype.maternity or ltype.code == "maternity":
                rec._fix_check_maternity()
                total = rec.days
                if total > ltype.entitlement_days:
                    raise UserError(
                        "Maternity is at most %d days: %d requested."
                        % (ltype.entitlement_days, total)
                    )
            elif ltype.code == "annual":
                available = rec.employee_id.sudo()._fix_annual_leave_available(
                    rec.date_from, exclude=rec
                )
                if rec.days > available:
                    raise UserError(
                        "Annual leave balance exhausted (BLA s.117: 1 day per %d days worked "
                        "after %d year's service): %d requested, %g earned and unused on %s."
                        % (
                            ANNUAL_LEAVE_DAYS_PER_EARNED_DAY,
                            ANNUAL_LEAVE_SERVICE_YEARS,
                            rec.days,
                            available,
                            rec.date_from,
                        )
                    )
            else:
                year = rec.date_from.year
                taken = rec._fix_year_taken(ltype.code, year)
                if taken + rec.days > ltype.entitlement_days:
                    raise UserError(
                        "Entitlement exhausted: %d approved + %d requested > %d days in %d"
                        % (taken, rec.days, ltype.entitlement_days, year)
                    )
            if ltype._fix_is_certificate_type() and not rec.medical_certificate:
                raise UserError(
                    "%s needs a registered medical practitioner's certificate attached "
                    "(BLA s.116)." % ltype.name
                )

    # ---- transitions ---------------------------------------------------------
    def action_submit(self):
        """The requester submits; the request is routed for approval."""
        for rec in self:
            if rec.state != "draft":
                raise UserError(
                    "Only a draft leave request is submitted (%s is %s)."
                    % (rec.display_name, rec.state)
                )
            rec._fix_leave_check_rules()
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
                raise UserError(
                    "Only a submitted leave request is approved (%s is %s)."
                    % (rec.display_name, rec.state)
                )
            rec._fix_leave_check_rules()
            rec._guarded().write(
                {
                    "state": "approved",
                    "decided_by_id": decider.id,
                    "decided_at": fields.Datetime.now(),
                    "approved_date_from": rec.date_from,
                    "approved_date_to": rec.date_to,
                    "approved_days": rec.days,
                }
            )
            publish(
                rec.env,
                "leave.approved",
                "fix.leave.request",
                rec.id,
                {"employee": rec.employee_id.name, "days": rec.days},
            )
        self._fix_leave_after_decision()
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

    def action_cancel(self, reason=None):
        """The requester withdraws, or HR recalls, a leave. An approved leave
        that has started is recalled by HR only; the days return to the
        balance because only approved leave is ever counted."""
        user = self.env.user
        is_hr = self.env.su or user.has_group("cd_hr_core.group_hr_officer")
        for rec in self:
            if rec.state not in ("draft", "submitted", "approved"):
                raise UserError("%s is %s and cannot be cancelled." % (rec.display_name, rec.state))
            owner = rec.employee_id.sudo().user_id == user or rec.create_uid == user
            if not (owner or is_hr):
                raise UserError("Only the requester or HR cancels %s." % rec.display_name)
            if rec.state == "approved":
                if not (reason or "").strip():
                    raise UserError("Say why an approved leave is cancelled.")
                if not is_hr and rec.date_from <= fields.Date.context_today(rec):
                    raise UserError(
                        "%s has started: HR recalls a leave that is under way." % rec.display_name
                    )
                rec._fix_leave_check_period_open()
            if rec.approval_state == "pending":
                req = rec.approval_request_id.sudo()
                req._finish("recalled", "recalled", user, comment=reason, record_state="none")
            was_approved = rec.state == "approved"
            rec._guarded().write(
                {
                    "state": "cancelled",
                    "cancelled_by_id": user.id,
                    "cancelled_at": fields.Datetime.now(),
                    "cancel_reason": reason or False,
                }
            )
            if was_approved:
                publish(
                    rec.env,
                    "leave.cancelled",
                    "fix.leave.request",
                    rec.id,
                    {"employee": rec.employee_id.name, "days": rec.days},
                )
        self._fix_leave_after_decision()
        return True

    def action_reject(self, reason=None):
        """The workspace Reject button: decides the caller's own inbox task."""
        if not (reason or "").strip():
            raise UserError("State why this leave is rejected.")
        return self.action_inbox_reject(reason=reason)


class HrEmployeeLeaveAccrual(models.Model):
    """I2: annual leave by the BLA s.117 accrual."""

    _inherit = "hr.employee"

    def _fix_service_start(self):
        """The first day of service: the earliest recorded joining date."""
        self.ensure_one()
        emp = self.sudo()
        dates = [emp[f] for f in ("joining_date", "joined_date") if f in emp._fields and emp[f]]
        if "fix.employment.contract" in self.env:
            contracts = (
                self.env["fix.employment.contract"]
                .sudo()
                .search([("employee_id", "=", emp.id), ("state", "!=", "draft")])
            )
            dates += [d for d in contracts.mapped("joining_date") if d]
        return min(dates) if dates else False

    def _fix_leave_days_worked(self, date_from, date_to):
        """Days of work performed in [date_from, date_to] for the s.117 accrual.

        The 'service' basis is here; cd_attendance adds the 'attendance' basis."""
        self.ensure_one()
        if date_to < date_from:
            return 0
        if self.sudo().company_id.fix_annual_leave_basis != "service":
            return 0
        days = (date_to - date_from).days + 1
        return days - days // 7

    def _fix_annual_leave_years(self, as_of):
        """[(year_start, year_end)] of the service years completed by `as_of`."""
        self.ensure_one()
        start = self._fix_service_start()
        out = []
        if not start:
            return out
        left = self.sudo().left_date if "left_date" in self._fields else False
        k = 0
        while True:
            y_start = start + relativedelta(years=k)
            y_end = start + relativedelta(years=k + 1) - timedelta(days=1)
            if y_end >= as_of:
                break
            if left and y_start > left:
                break
            out.append((y_start, min(y_end, left) if left else y_end))
            k += 1
        return out

    def _fix_annual_leave_ledger(self, as_of):
        """[(service_year_start, service_year_end, days_worked, days_earned)]."""
        self.ensure_one()
        rows = []
        for y_start, y_end in self._fix_annual_leave_years(as_of):
            worked = self._fix_leave_days_worked(y_start, y_end)
            rows.append((y_start, y_end, worked, worked // ANNUAL_LEAVE_DAYS_PER_EARNED_DAY))
        return rows

    def _fix_annual_leave_balance(self, as_of, exclude=None, until=None):
        """Earned annual leave less the approved annual leave started by `until`
        (default `as_of`), accumulating up to the type's carry-forward cap plus
        any refused annual leave (s.117(7))."""
        self.ensure_one()
        annual = (
            self.env["fix.leave.type"]
            .sudo()
            .search([("code", "=", "annual"), ("company_id", "=", self.company_id.id)], limit=1)
        )
        if not annual:
            return 0.0
        until = until or as_of
        Leave = self.env["fix.leave.request"].sudo()
        base = [("employee_id", "=", self.id), ("leave_type_id.code", "=", "annual")]
        if exclude:
            base.append(("id", "not in", exclude.ids))
        taken = Leave.search([*base, ("state", "=", "approved"), ("date_from", "<=", until)])
        refused = Leave.search([*base, ("state", "=", "rejected"), ("date_from", "<=", as_of)])
        events = []
        for _ys, y_end, _worked, earned in self._fix_annual_leave_ledger(as_of):
            events.append((y_end + timedelta(days=1), 0, float(earned)))
        for lv in taken:
            events.append((lv.date_from, 1, -float(lv.days)))
        cap = annual.carry_forward_limit or 0
        extra = 0.0
        balance = 0.0
        for when, _kind, n in sorted(events):
            if n > 0:
                extra = float(
                    sum(refused.filtered(lambda r, w=when: r.date_from < w).mapped("days"))
                )
                balance += n
                if cap:
                    balance = min(balance, cap + extra)
            else:
                balance += n
        return max(balance, 0.0)

    def _fix_unused_annual_leave_days(self, as_of=None):
        """I2: annual (earned) leave days still unused at `as_of` (default today).

        BLA s.117: after one year's continuous service, 1 day per 18 days of
        work performed in each completed service year, carried forward up to
        the annual type's carry-forward limit. Leave earned in the service
        year still running becomes available at its anniversary. Read by
        payroll (unused_leave_days, encashment) and the M21 exit settlement."""
        self.ensure_one()
        as_of = fields.Date.to_date(as_of) if as_of else fields.Date.context_today(self)
        return self._fix_annual_leave_balance(as_of)

    def _fix_annual_leave_available(self, on_date, exclude=None):
        """What a new annual leave starting `on_date` may use: the balance on
        that day less approved annual leave that starts later."""
        self.ensure_one()
        far = on_date + relativedelta(years=50)
        return self._fix_annual_leave_balance(on_date, exclude=exclude, until=far)


class FixLeaveAccrual(models.Model):
    """The s.117 accrual register: one row per employee and completed service
    year (BLA r.24 Form-9 basis), written by the accrual cron."""

    _name = "fix.leave.accrual"
    _description = "Annual Leave Accrual (BLA s.117)"
    _order = "employee_id, year_start desc"

    company_id = fields.Many2one("res.company", required=True, index=True, readonly=True)
    employee_id = fields.Many2one("hr.employee", required=True, index=True, readonly=True)
    year_start = fields.Date(required=True, readonly=True)
    year_end = fields.Date(required=True, readonly=True)
    days_worked = fields.Integer(readonly=True)
    days_earned = fields.Integer(readonly=True)
    basis = fields.Char(readonly=True)
    computed_at = fields.Datetime(readonly=True)

    _employee_year = models.Constraint(
        "UNIQUE (employee_id, year_start)", "One accrual row per employee and service year"
    )

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            raise UserError("The accrual register is written by the accrual run only.")
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.su:
            raise UserError("The accrual register is written by the accrual run only.")
        return super().write(vals)

    @api.model
    def cron_accrue_annual_leave(self):
        """Idempotent: (re)writes the row of every completed service year."""
        self = self.sudo()
        today = fields.Date.context_today(self)
        Employee = self.env["hr.employee"].sudo()
        count = 0
        for emp in Employee.search([]):
            for y_start, y_end, worked, earned in emp._fix_annual_leave_ledger(today):
                vals = {
                    "company_id": emp.company_id.id,
                    "employee_id": emp.id,
                    "year_start": y_start,
                    "year_end": y_end,
                    "days_worked": worked,
                    "days_earned": earned,
                    "basis": emp.company_id.fix_annual_leave_basis,
                    "computed_at": fields.Datetime.now(),
                }
                row = self.search([("employee_id", "=", emp.id), ("year_start", "=", y_start)])
                if row:
                    if (row.days_worked, row.days_earned, row.year_end) != (worked, earned, y_end):
                        row.write(vals)
                else:
                    self.create(vals)
                count += 1
        return count
