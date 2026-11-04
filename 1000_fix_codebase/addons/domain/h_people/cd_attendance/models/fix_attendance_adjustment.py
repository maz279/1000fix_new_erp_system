# fix_attendance_adjustment — M55 FR-WFM-052 / BRU-WFM-10: forward adjustments,
# hand-off interface I8 with payroll (cd_payroll_bd consumes them).
#
# A09 audit M55-6 (C5): after a paid month was re-opened and edited, the
# payslip kept the old overtime while attendance showed the new one, and
# nothing carried the difference. Now a period payroll has PAID may be
# re-opened (by the Lock Manager, with a reason); at that moment what was paid
# is recorded per employee-day (fix.attendance.paid.baseline). Every change to
# that period's attendance afterwards keeps one draft adjustment per
# employee, day and kind equal to "now minus what was paid minus what earlier
# approved adjustments already carry", routed for approval. Payroll's next run
# consumes APPROVED adjustments through `_fix_consume(slip)`.
#
# I8 contract (fields payroll reads):
#   employee_id, company_id, date (the original day), period_month ('YYYY-MM'
#   of that day), kind (overtime_hours / absence_days / oncall_allowance),
#   quantity (signed: hours, days or 1 allowance), amount (signed money: the
#   s.108 value for overtime, the approved allowance for on-call, 0 for an
#   absence day, which payroll values), state (draft / approved / consumed /
#   cancelled), payslip_ref_id (Integer: the consuming fix.payslip id).
from datetime import timedelta
from decimal import Decimal

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

from .fix_attendance import PAYABLE_STATES, _day_bounds

ADJUSTMENT_APPROVER_GROUP = "hr.group_hr_manager"
PAYROLL_GROUPS = ("cd_payroll_bd.group_payroll_officer", "cd_payroll_bd.group_payroll_manager")
# payroll states after which a period takes nothing more (cd_payroll_bd)
PAYROLL_FROZEN_STATES = ("approved", "paid", "posted")


class FixAttendanceAdjustment(models.Model):
    """One correction carried into the next payroll (I8)."""

    _name = "fix.attendance.adjustment"
    _description = "Attendance Forward Adjustment (FR-WFM-052)"
    _inherit = ["mail.thread", "fix.people.approval.mixin", "fix.people.inbox.decide.mixin"]
    _order = "date desc, id desc"

    _approval_domain = "hr_attendance"
    _approval_apply_method = "action_approve"
    _approval_group = ADJUSTMENT_APPROVER_GROUP

    name = fields.Char(compute="_compute_name", store=True)
    # ---- the I8 interface ---------------------------------------------------
    employee_id = fields.Many2one("hr.employee", required=True, index=True, readonly=True)
    company_id = fields.Many2one("res.company", required=True, index=True, readonly=True)
    date = fields.Date(string="Original Day", required=True, index=True, readonly=True)
    period_month = fields.Char(
        string="Original Month", compute="_compute_period_month", store=True, index=True
    )
    kind = fields.Selection(
        [
            ("overtime_hours", "Overtime Hours"),
            ("absence_days", "Absence Days"),
            ("oncall_allowance", "On-Call Allowance"),
        ],
        required=True,
        readonly=True,
        index=True,
    )
    quantity = fields.Float(readonly=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, readonly=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(currency_field="currency_id", readonly=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("approved", "Approved"),
            ("consumed", "Consumed by Payroll"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        readonly=True,
        tracking=True,
        index=True,
    )
    payslip_ref_id = fields.Integer(string="Payslip", readonly=True, index=True)
    # ---- provenance ---------------------------------------------------------
    lock_id = fields.Many2one("fix.attendance.lock", readonly=True, ondelete="set null")
    oncall_id = fields.Many2one(
        "fix.hr.oncall", string="On-Call", readonly=True, ondelete="set null"
    )
    raised_by_id = fields.Many2one("res.users", string="Change Made By", readonly=True)
    note = fields.Char(readonly=True)
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True)
    approved_at = fields.Datetime(readonly=True)
    consumed_at = fields.Datetime(readonly=True)
    cancel_reason = fields.Char(readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "employee_id",
            "company_id",
            "date",
            "kind",
            "quantity",
            "currency_id",
            "amount",
            "state",
            "payslip_ref_id",
            "lock_id",
            "oncall_id",
            "raised_by_id",
            "note",
            "approved_by_id",
            "approved_at",
            "consumed_at",
            "cancel_reason",
        }

    @api.depends("employee_id", "date", "kind", "quantity")
    def _compute_name(self):
        for rec in self:
            rec.name = "ADJ %s %s %s %+g" % (
                rec.employee_id.name or "",
                rec.date or "",
                rec.kind or "",
                rec.quantity,
            )

    @api.depends("date")
    def _compute_period_month(self):
        for rec in self:
            rec.period_month = rec.date.strftime("%Y-%m") if rec.date else False

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            raise AccessError("An adjustment is raised by the attendance change it carries.")
        return super(FixAttendanceAdjustment, self._guarded()).create(vals_list)

    def _approval_amount(self) -> float:
        return self.amount or 0.0

    def _approval_preparers(self):
        return self.sudo().mapped("raised_by_id")

    # ---- routing ------------------------------------------------------------------
    def _fix_route(self):
        """Route a draft adjustment; one nobody can decide yet stays draft and
        the routing cron tries again."""
        for rec in self.filtered(lambda r: r.state == "draft" and r.approval_state != "pending"):
            requester = rec.raised_by_id or self.env.user
            try:
                with self.env.cr.savepoint():
                    rec.with_user(requester).sudo().action_request_approval()
            except UserError:
                continue
        return True

    @api.model
    def cron_route_adjustments(self):
        """Hourly, idempotent: every draft adjustment reaches an approver's inbox."""
        drafts = self.sudo().search([("state", "=", "draft"), ("approval_state", "!=", "pending")])
        drafts._fix_route()
        return len(drafts)

    def action_approve(self):
        """Applied by the M63 engine in the approver's environment."""
        self._approval_assert_routed()
        self._people_assert_not_conflicted()
        decider = self._people_decider()
        for rec in self:
            if rec.state != "draft":
                raise UserError(
                    "Only a draft adjustment is approved (%s is %s)." % (rec.name, rec.state)
                )
            rec.sudo()._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": decider.id,
                    "approved_at": fields.Datetime.now(),
                }
            )
        return True

    def _approval_on_rejected(self, comment):
        for rec in self:
            rec.sudo()._guarded().write(
                {"state": "cancelled", "cancel_reason": ("Rejected: %s" % (comment or ""))[:250]}
            )

    def action_reject(self, reason=None):
        if not (reason or "").strip():
            raise UserError("State why this adjustment is rejected.")
        return self.action_inbox_reject(reason=reason)

    def _fix_cancel(self, reason):
        for rec in self.filtered(lambda r: r.state == "draft"):
            if rec.approval_state == "pending":
                rec.approval_request_id.sudo()._finish(
                    "voided", "voided", self.env.user, comment=reason, record_state="none"
                )
            rec.sudo()._guarded().write({"state": "cancelled", "cancel_reason": reason[:250]})

    # ---- I8: payroll consumes ----------------------------------------------------------
    def _fix_consume(self, slip):
        """Payroll takes an APPROVED adjustment onto `slip` (a fix.payslip of a
        later period, same employee and company). Guarded; refuses anything
        else. Only a DIFFERENT payslip that still exists blocks: an adjustment
        whose slip a recalculation deleted is taken again, and the same slip
        is idempotent (the I4 incentive-line rule)."""
        user = self.env.user
        if not (self.env.su or any(user.has_group(g) for g in PAYROLL_GROUPS)):
            raise AccessError("Adjustments are consumed by payroll only.")
        slip.ensure_one()
        if slip._name != "fix.payslip":
            raise UserError("An adjustment is consumed by a payslip only.")
        slip = slip.sudo()
        Slip = self.env["fix.payslip"].sudo()
        start = slip.period_id.period_start if "period_id" in slip._fields else False
        for rec in self:
            held = (
                rec.payslip_ref_id
                and rec.payslip_ref_id != slip.id
                and Slip.browse(rec.payslip_ref_id).exists()
            )
            if held:
                raise UserError("%s is already on payslip %s." % (rec.name, rec.payslip_ref_id))
            # past the check above, a consumed adjustment is on THIS slip or on
            # one a recalculation deleted: it is taken again
            if rec.state not in ("approved", "consumed"):
                raise UserError(
                    "%s is %s: payroll consumes only an approved adjustment."
                    % (rec.name, rec.state)
                )
            if slip.employee_id != rec.employee_id:
                raise UserError(
                    "%s belongs to %s, not to that payslip's employee."
                    % (rec.name, rec.employee_id.name)
                )
            if (
                "company_id" in slip._fields
                and slip.company_id
                and slip.company_id != rec.company_id
            ):
                raise UserError("%s belongs to another company." % rec.name)
            if start and start <= rec.date:
                raise UserError(
                    "%s corrects %s: it is carried into a LATER payroll period (FR-WFM-052)."
                    % (rec.name, rec.date)
                )
            rec.sudo()._guarded().write(
                {
                    "state": "consumed",
                    "payslip_ref_id": slip.id,
                    "consumed_at": fields.Datetime.now(),
                }
            )
        return True

    # ---- keeping the draft equal to what is owed ---------------------------------------
    @api.model
    def _fix_settle(
        self, employee, day, kind, target, amount, user, lock=None, oncall=None, note=None
    ):
        """Make the open adjustments of (employee, day, kind) carry `target`
        (the correction owed in total): drafts are updated, cancelled or
        created; approved and consumed ones are never touched."""
        Adj = self.sudo()
        rows = Adj.search(
            [
                ("employee_id", "=", employee.id),
                ("date", "=", day),
                ("kind", "=", kind),
                ("state", "!=", "cancelled"),
            ]
            + ([("oncall_id", "=", oncall.id)] if oncall else [])
        )
        settled = rows.filtered(lambda r: r.state in ("approved", "consumed"))
        draft = rows.filtered(lambda r: r.state == "draft")[:1]
        owed_qty = round(target[0] - sum(settled.mapped("quantity")), 2)
        owed_amt = round(amount - sum(settled.mapped("amount")), 2)
        if abs(owed_qty) < 0.005 and abs(owed_amt) < 0.005:
            if draft:
                draft._fix_cancel("the attendance is back to what was paid")
            return Adj.browse()
        if draft:
            if abs(draft.quantity - owed_qty) < 0.005 and abs(draft.amount - owed_amt) < 0.005:
                return draft
            if draft.approval_state == "pending":
                draft._approval_void("the correction changed to %+g" % owed_qty)
            draft._guarded().write(
                {"quantity": owed_qty, "amount": owed_amt, "raised_by_id": user.id}
            )
            draft._fix_route()
            return draft
        adj = (
            Adj.with_user(user)
            .sudo()
            .create(
                {
                    "employee_id": employee.id,
                    "company_id": employee.company_id.id,
                    "date": day,
                    "kind": kind,
                    "quantity": owed_qty,
                    "amount": owed_amt,
                    "lock_id": lock.id if lock else False,
                    "oncall_id": oncall.id if oncall else False,
                    "raised_by_id": user.id,
                    "note": (note or "")[:250] or False,
                }
            )
        )
        adj._fix_route()
        return adj


class FixAttendancePaidBaseline(models.Model):
    """What payroll paid for one employee-day of a re-opened paid period."""

    _name = "fix.attendance.paid.baseline"
    _description = "Paid Attendance Baseline"
    _order = "date, employee_id"

    lock_id = fields.Many2one("fix.attendance.lock", required=True, index=True, ondelete="cascade")
    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    date = fields.Date(required=True, index=True)
    overtime_hours = fields.Float()
    worked = fields.Boolean()

    _lock_employee_day = models.Constraint(
        "UNIQUE (lock_id, employee_id, date)", "One paid baseline per employee-day of a lock"
    )

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            raise AccessError("The paid baseline is recorded by the re-opening only.")
        return super().create(vals_list)

    def write(self, vals):
        raise UserError("The paid baseline is never changed.")


def _day_figures(env, employee, day):
    """(payable overtime, worked?) of an employee-day as payroll would read it."""
    start, end = _day_bounds(day)
    recs = (
        env["fix.attendance.record"]
        .sudo()
        .search(
            [("employee_id", "=", employee.id), ("check_in", ">=", start), ("check_in", "<", end)]
        )
    )
    ot = round(sum(recs.mapped("overtime_hours")), 2)
    worked = any(r.worked_hours > 0 and r.approval_state in PAYABLE_STATES for r in recs)
    return ot, worked


def _overtime_value(env, employee, hours):
    """BLA s.108 value of `hours` (signed) at the employee's active contract."""
    from libs.py.payroll_engine import OT_DIVISOR_HOURS, overtime_amount

    if not hours:
        return 0.0
    contract = (
        env["fix.employment.contract"]
        .sudo()
        .search([("employee_id", "=", employee.id), ("state", "=", "active")], limit=1)
        if "fix.employment.contract" in env
        else None
    )
    basic = Decimal(
        str((contract.basic_monthly if contract else employee.sudo().basic_wage) or 0.0)
    )
    da = Decimal(str((contract.dearness_allowance if contract else 0.0) or 0.0))
    adhoc = Decimal(str((contract.adhoc_allowance if contract else 0.0) or 0.0))
    value = overtime_amount(
        basic,
        Decimal(str(abs(hours))),
        dearness_monthly=da,
        adhoc_monthly=adhoc,
        divisor_hours=OT_DIVISOR_HOURS,
    )
    return float(value) if hours > 0 else -float(value)


class FixAttendanceLockBaseline(models.Model):
    _inherit = "fix.attendance.lock"

    adjustment_ids = fields.One2many("fix.attendance.adjustment", "lock_id", readonly=True)

    def _fix_after_reopen(self):
        """At the first re-opening after payment: record what was paid."""
        super()._fix_after_reopen()
        Baseline = self.env["fix.attendance.paid.baseline"].sudo()
        Record = self.env["fix.attendance.record"].sudo()
        for lock in self.sudo().filtered(lambda r: not r.baseline_taken):
            records = Record.search(
                [
                    ("company_id", "=", lock.company_id.id),
                    ("check_in", ">=", fields.Datetime.to_datetime(lock.period_start)),
                    (
                        "check_in",
                        "<",
                        fields.Datetime.to_datetime(lock.period_end + timedelta(days=1)),
                    ),
                ]
            )
            rows = []
            for emp, day in {(r.employee_id, r.check_in.date()) for r in records}:
                ot, worked = _day_figures(self.env, emp, day)
                rows.append(
                    {
                        "lock_id": lock.id,
                        "employee_id": emp.id,
                        "date": day,
                        "overtime_hours": ot,
                        "worked": worked,
                    }
                )
            Baseline.create(rows)
            lock._guarded().write({"baseline_taken": True})
        return True

    @api.model
    def _fix_paid_reopened(self, company, day):
        """The re-opened lock of `company` over `day` that payroll had paid."""
        if not (company and day):
            return self.browse()
        return self.sudo().search(
            [
                ("state", "=", "unlocked"),
                ("baseline_taken", "=", True),
                ("company_id", "=", company.id),
                ("period_start", "<=", day),
                ("period_end", ">=", day),
            ],
            limit=1,
        )


class FixAttendanceRecordAdjustments(models.Model):
    _inherit = "fix.attendance.record"

    def _fix_recompute_days(self, keys):
        super()._fix_recompute_days(keys)
        self._fix_sync_adjustments(keys)

    def _fix_sync_adjustments(self, keys):
        """FR-WFM-052: each employee-day of a re-opened PAID period carries
        the difference to what was paid as a draft adjustment."""
        Lock = self.env["fix.attendance.lock"]
        Baseline = self.env["fix.attendance.paid.baseline"].sudo()
        Adj = self.env["fix.attendance.adjustment"]
        Employee = self.env["hr.employee"].sudo()
        user = self.env.user
        for key in {k for k in keys if k}:
            emp = Employee.browse(key[0]).exists()
            if not emp:
                continue
            lock = Lock._fix_paid_reopened(emp.company_id, key[1])
            if not lock:
                continue
            base = Baseline.search(
                [("lock_id", "=", lock.id), ("employee_id", "=", emp.id), ("date", "=", key[1])],
                limit=1,
            )
            ot, worked = _day_figures(self.env, emp, key[1])
            d_ot = round(ot - (base.overtime_hours if base else 0.0), 2)
            Adj._fix_settle(
                emp,
                key[1],
                "overtime_hours",
                (d_ot,),
                _overtime_value(self.env, emp, d_ot),
                user,
                lock=lock,
                note="Overtime changed after payment (%s)" % lock.name,
            )
            d_abs = int(bool(base and base.worked)) - int(worked)
            Adj._fix_settle(
                emp,
                key[1],
                "absence_days",
                (float(d_abs),),
                0.0,
                user,
                lock=lock,
                note="Worked day changed after payment (%s)" % lock.name,
            )


class FixHrOncallAdjustment(models.Model):
    _inherit = "fix.hr.oncall"

    def _fix_after_allowance_approved(self):
        """I9: an allowance approved after payroll froze its period is carried
        forward (the approval itself was routed; the adjustment is born approved)."""
        Period = self.env["fix.payroll.period"].sudo() if "fix.payroll.period" in self.env else None
        for rec in self:
            if Period is None or not rec.approved_allowance:
                continue
            day = rec.date_from.date()
            domain = [
                ("period_start", "<=", day),
                ("period_end", ">=", day),
                ("state", "in", PAYROLL_FROZEN_STATES),
            ]
            if "company_id" in Period._fields:
                domain.append(("company_id", "=", rec.company_id.id))
            if not Period.search_count(domain):
                continue
            adj = self.env["fix.attendance.adjustment"]._fix_settle(
                rec.employee_id,
                day,
                "oncall_allowance",
                (1.0,),
                rec.approved_allowance,
                rec.allowance_approved_by_id or self.env.user,
                oncall=rec,
                note="On-call %s approved after payroll froze %s"
                % (rec.name, day.strftime("%Y-%m")),
            )
            if adj and adj.state == "draft":
                if adj.approval_state == "pending":
                    adj._approval_void("approved with the on-call allowance")
                adj._guarded().write(
                    {
                        "state": "approved",
                        "approved_by_id": rec.allowance_approved_by_id.id,
                        "approved_at": fields.Datetime.now(),
                    }
                )
        return True


class HrEmployeeLeaverRoster(models.Model):
    _inherit = "hr.employee"

    @api.model
    def consume_employee_left_roster(self, event):
        """AUT-WFM-16 relay consumer of employee.left: the leaver's roster slots
        and planned on-call shifts after the last working day are closed, so
        dispatch never counts on a leaver. Idempotent; relay (superuser) only."""
        if not self.env.su:
            raise AccessError("The leaver roster consumer runs from the event relay only.")
        payload = event.get("payload") or {}
        emp = (
            self.with_context(active_test=False)
            .browse(int(payload.get("employee_id") or event.get("aggregate_id") or 0))
            .exists()
        )
        if not emp or not emp.left_date:
            return False
        slots = (
            self.env["fix.roster.slot"]
            .sudo()
            .search([("employee_id", "=", emp.id), ("date", ">", emp.left_date)])
        )
        for slot in slots:
            if slot.publication_id and slot.publication_id.state == "submitted":
                slot.publication_id._fix_void("a rostered employee left")
        removed = len(slots)
        slots._guarded().unlink()
        oncall = (
            self.env["fix.hr.oncall"]
            .sudo()
            .search(
                [
                    ("employee_id", "=", emp.id),
                    ("state", "=", "planned"),
                    (
                        "date_from",
                        ">",
                        fields.Datetime.to_datetime(emp.left_date + timedelta(days=1)),
                    ),
                ]
            )
        )
        for rec in oncall:
            rec._guarded().write({"state": "cancelled"})
        return {"slots_removed": removed, "oncall_cancelled": len(oncall)}
