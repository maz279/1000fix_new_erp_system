# fix_payroll — M56: period, payslips, BEFTN batch, GL posting (P08-M03).
#
# A09 workflow audit (2026-11-03), P0 A3/A4: every control of the payroll
# cycle lived in an action method, while the fields it protects were plain
# writable fields. A payroll officer wrote `state='approved'`, rewrote a
# colleague's payslip bank account after approval and had the BEFTN file pay
# his own account, edited an approved basic 30,000 -> 300,000, and added a
# ghost payslip to an approved period. Now:
#   * state, the actor stamps and every amount/payee field are guarded
#     (fix.guarded.mixin): only the transition methods set them;
#   * a payslip of an approved, paid or posted period cannot be created,
#     changed or deleted at all;
#   * approval stores a digest of (slip, employee, net, account, routing) and
#     the approved total, and the BEFTN file refuses a run that differs.
#
# A09 P0-b / P1 / P2 (M56 build):
#   * approval is a routed M63 request (fix.people.approval.mixin, domain
#     hr_payroll_release): the officer requests it, a Payroll Manager who did
#     not prepare or calculate the run decides it from the inbox (C1);
#   * a request is refused until pre-validation passes: no negative net, no
#     zero or sub-floor basic, no missing bank details, no slip without a
#     contract behind it (M56-14);
#   * the inputs come from fields that exist: tax category, tax location and
#     disabled child from hr.employee, overtime only for an eligible employee,
#     exactly one active contract per employee (C2, M56-6), and the attendance
#     lock is re-checked by calculate itself, in the period's company (M56-15);
#   * a leaver is paid only up to the left date, prorated; someone who left
#     before the period, or who has no active contract, is skipped and the run
#     says so (I3); approved M57 incentive lines are picked up once (I4);
#   * the BEFTN file is released by a Payroll Disbursement Releaser who neither
#     calculated nor approved the run (SOD-29), and settled only against a bank
#     confirmation (M56-4);
#   * a paid run's payslips are published: the employee then reads their own
#     slip, and only that one (M56-8, FR-PAY-050).
import hashlib
import json
from datetime import datetime, timedelta
from decimal import Decimal

from odoo import Command, api, fields, models
from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions
from odoo.exceptions import AccessError, UserError

from libs.py.fix_events import publish
from libs.py.payroll_engine import (
    OT_DIVISOR_HOURS,
    SALARY_EXEMPTION_CEILING,
    BeftnBatchHeader,
    BeftnEntry,
    PayslipInput,
    beftn_settlement_date,
    completed_years,
    compute_payslip,
    generate_beftn_batch_file,
    gratuity,
    resignation_compensation,
    validate_routing_number,
)

from .fix_payroll_disbursement import (
    RELEASER,
    check_releaser,
    master_bank_details,
    payroll_gl_journal,
)
from .fix_payroll_settlement import separation_contract, unused_leave_days
from .fix_payroll_statutory import (
    RETRENCHMENT_NOTICE_DAYS,
    SERVICE_COMPENSATION_DAYS,
    notice_served_days,
    q2,
    statutory_basis,
)

PAYROLL_OFFICER = "cd_payroll_bd.group_payroll_officer"
PAYROLL_MANAGER = "cd_payroll_bd.group_payroll_manager"

# Width of the beneficiary account field in a BEFTN entry-detail record
# (libs/py/payroll_engine/beftn.py: format_field(entry.account_number, 17)).
BEFTN_ACCOUNT_WIDTH = 17

# The period company's payroll GL accounts (res.company, configured by
# finance; the module never creates or guesses an account).
PAYROLL_GL_ACCOUNTS = [
    ("payroll_salary_expense_account_id", "Salary & Wage Expense"),
    ("payroll_pf_expense_account_id", "Employer PF Contribution Expense"),
    ("payroll_net_payable_account_id", "Net Salary Payable"),
    ("payroll_tax_payable_account_id", "Income Tax (TDS) Payable"),
    ("payroll_pf_payable_account_id", "Provident Fund Payable"),
]

PERIOD_FLOW = [
    ("draft", "Draft"),
    ("attendance_locked", "Attendance Locked"),
    ("calculated", "Calculated"),
    ("approved", "Approved"),
    ("paid", "Paid"),
    ("posted", "Posted"),
]

# A period in one of these states is committed: its payslips are frozen.
FROZEN_PERIOD_STATES = ("approved", "paid", "posted")

# Every payslip field that decides what is paid, to whom and into which
# account. Only action_calculate and the separation/retrenchment computations
# set them (through _guarded()); the stored computes follow from them.
PAYSLIP_GUARDED_FIELDS = frozenset(
    {
        "period_id",
        "employee_id",
        "company_id",
        "currency_id",
        "basic",
        "house_rent",
        "medical_allowance",
        "conveyance_allowance",
        "technical_allowance",
        "other_allowance",
        "dearness_allowance",
        "adhoc_allowance",
        "ot_hours",
        "incentive",
        "pf_employee_pct",
        "pf_employer_pct",
        "annual_taxable_other",
        "taxpayer_category",
        "has_disabled_child",
        "minimum_tax_location",
        "investment_allowance",
        "bank_account_no",
        "routing_no",
        "bank_name",
        "allowances_total",
        "annual_exemption",
        "gross",
        "overtime",
        "pf_employee",
        "pf_employer",
        "tax_withheld",
        "net",
        "completed_years",
        "gratuity_amount",
        "resignation_compensation_amount",
        "retrenchment_compensation",
        "notice_pay_amount",
        "unused_leave_days",
        "leave_encashment_amount",
        "contract_id",
        "oncall_allowance",
        "paid_days",
        "period_days",
        "ot_divisor_hours",
        "exemption_ceiling",
        "statutory_basis",
    }
)
# Set by action_publish_payslips on a paid run: the only payslip fields that
# change once the run is committed.
PAYSLIP_PUBLICATION_FIELDS = frozenset({"published", "published_on", "published_digest"})
PAYSLIP_GUARDED_FIELDS = PAYSLIP_GUARDED_FIELDS | PAYSLIP_PUBLICATION_FIELDS


def payslip_digest(slips) -> str:
    """SHA-256 over what a run pays: (slip, employee, net, account, routing),
    sorted so the digest does not depend on read order."""
    rows = sorted(
        (
            slip.id,
            slip.employee_id.id,
            "%.2f" % (slip.net or 0.0),
            (slip.bank_account_no or "").strip(),
            (slip.routing_no or "").strip(),
        )
        for slip in slips
    )
    return hashlib.sha256(json.dumps(rows).encode()).hexdigest()


class FixPayrollStateLock(models.AbstractModel):
    """fix.guarded.mixin plus the fields a payroll document freezes by state.

    The guarded fields (state, stamps, computed amounts) change only inside a
    transition. The state-locked fields are ordinary inputs while the document
    is a draft and freeze once it moves on: an approved off-cycle payment's
    amount and payee, a trustee-approved WPPF profit (A09 probes O4, W4)."""

    _name = "fix.payroll.state.lock"
    _description = "Payroll Document State Lock"
    _inherit = ["fix.guarded.mixin"]

    def _payroll_state_locked_fields(self) -> set:
        """Fields frozen by THIS record's state. Extend per model."""
        return set()

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        for rec in self:
            locked |= rec._payroll_state_locked_fields()
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                changed = [
                    name
                    for name in rec._payroll_state_locked_fields() & set(vals)
                    if rec._fix_guard_differs(name, vals[name], rec[name])
                ]
                if changed:
                    state = dict(rec._fields["state"].selection).get(rec.state, rec.state)
                    raise UserError(
                        "%s %s is %s: %s can no longer be changed."
                        % (
                            rec._description,
                            rec.display_name,
                            state,
                            ", ".join(sorted(rec._fields[n].string for n in changed)),
                        )
                    )
        return super().write(vals)


class FixPayrollPeriod(models.Model):
    """Journey 13's spine: lock -> calculate -> approve -> BEFTN -> payslips
    -> posting. Each transition is guarded; calculation REFUSED until the
    attendance lock exists (P08-M02-T05)."""

    _name = "fix.payroll.period"
    _description = "Payroll Period"
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
        "fix.people.approval.mixin",
        "fix.payroll.state.lock",
    ]
    _order = "period_start desc"

    # C1: payroll release is a routed M63 decision. Until the business rules a
    # DOFA ladder for payroll (report §7.2), the Payroll Manager group decides.
    _approval_domain = "hr_payroll_release"
    _approval_apply_method = "action_approve"
    _approval_group = PAYROLL_MANAGER

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    period_start = fields.Date(required=True)
    period_end = fields.Date(required=True)
    state = fields.Selection(PERIOD_FLOW, default="draft", required=True, tracking=True)
    calculator_id = fields.Many2one("res.users", string="Calculated By", readonly=True)
    payslip_ids = fields.One2many("fix.payslip", "period_id", string="Payslips")
    slip_count = fields.Integer(compute="_compute_counts", string="Slips")
    net_total = fields.Monetary(
        compute="_compute_counts", currency_field="currency_id", string="Net Total"
    )
    gross_total = fields.Monetary(
        compute="_compute_counts", currency_field="currency_id", string="Gross Total"
    )
    tax_total = fields.Monetary(
        compute="_compute_counts", currency_field="currency_id", string="Tax Withheld Total"
    )
    pf_total = fields.Monetary(
        compute="_compute_counts", currency_field="currency_id", string="PF Total (Emp + Empr)"
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    beftn_batch_id = fields.Many2one("fix.beftn.batch", string="BEFTN Batch", readonly=True)
    gl_move_id = fields.Many2one("account.move", string="GL Entry", readonly=True)
    # The company's real originating account for this run's BEFTN batch.
    # Entered by the payroll officer and carried onto the batch by action_pay
    # (R01 re-audit 2026-10-22): the batch fields have no defaults, so without
    # these the pay step could never produce a file.
    company_account_no = fields.Char(string="Company Originating Account")
    company_routing_no = fields.Char(string="Company Routing No (9 digits)")
    # The approval, pinned (A09 P0 A3): who approved, when, and what. The
    # BEFTN file is built only while the slips still hash to approved_digest
    # and add up to approved_net_total.
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True)
    approved_on = fields.Datetime(string="Approved On", readonly=True)
    approved_digest = fields.Char(string="Approved Payslip Digest", readonly=True)
    approved_net_total = fields.Monetary(
        currency_field="currency_id", string="Approved Net Total", readonly=True
    )
    # SOD-29: who sent the file to the bank (never the calculator or approver)
    released_by_id = fields.Many2one("res.users", string="Released By", readonly=True)
    released_on = fields.Datetime(string="Released On", readonly=True)
    # What calculate did and did not pay, and why (I3: a leaver or an employee
    # without an active contract is skipped, and the run says so).
    calculation_note = fields.Text(string="Calculation Notes", readonly=True)
    payslips_published_on = fields.Datetime(string="Payslips Published On", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "calculator_id",
            "approved_by_id",
            "approved_on",
            "approved_digest",
            "approved_net_total",
            "beftn_batch_id",
            "gl_move_id",
            "payslip_ids",
            "released_by_id",
            "released_on",
            "calculation_note",
            "payslips_published_on",
        }

    def _payroll_state_locked_fields(self) -> set:
        """Fields frozen by this period's state: the scope once calculated,
        the originating account once the run is approved (the approver
        approves a run that pays from a named account)."""
        locked = super()._payroll_state_locked_fields()
        if self.state not in ("draft", "attendance_locked"):
            locked |= {"period_start", "period_end", "company_id", "currency_id"}
            locked |= {"operating_unit_id"}
        if self.state in FROZEN_PERIOD_STATES:
            locked |= {"company_account_no", "company_routing_no"}
        return locked

    # ---- routed approval (C1) ------------------------------------------------
    def _approval_amount(self) -> float:
        return float(self.net_total or 0.0)

    def _approval_subject_employees(self):
        # A run pays everyone, its approver included: the subject exclusion
        # would leave no approver. The preparer and calculator are excluded.
        return self.env["hr.employee"]

    def _approval_preparers(self):
        return (self.calculator_id | self.create_uid).sudo()

    def action_request_approval(self, justification=None):
        """The officer's submit step: only a calculated run that passes
        pre-validation is routed to an approver."""
        for rec in self:
            if rec.state != "calculated":
                raise UserError(
                    "Payroll period %s is %s: only a calculated run is sent for approval."
                    % (rec.name, dict(PERIOD_FLOW)[rec.state])
                )
            rec._raise_prevalidation()
        return super().action_request_approval(justification=justification)

    def _approval_on_rejected(self, comment):
        """A rejected run goes back to the officer for recalculation."""
        for rec in self.filtered(lambda r: r.state == "calculated"):
            rec._guarded().write({"state": "attendance_locked"})
            rec.message_post(body="Payroll approval rejected: %s" % (comment or ""))

    def _refuse_while_pending(self, what):
        for rec in self:
            if rec.approval_state == "pending":
                raise UserError(
                    "Payroll period %s is awaiting approval: recall the request before you %s."
                    % (rec.name, what)
                )

    def _payroll_snapshot(self):
        """(digest, net total) of this period's payslips as they stand now."""
        self.ensure_one()
        slips = self.payslip_ids
        return payslip_digest(slips), self.currency_id.round(sum(slips.mapped("net")))

    def _check_approved_snapshot(self):
        """Refuse a period whose payslips no longer match what was approved."""
        for rec in self:
            digest, total = rec._payroll_snapshot()
            if not rec.approved_digest or digest != rec.approved_digest:
                raise UserError(
                    "Payroll period %s does not match its approval: a payslip's employee, "
                    "net pay or bank details differ from what was approved (or the period "
                    "was never approved through its approval action). Nothing is paid "
                    "from a changed run." % rec.name
                )
            if rec.currency_id.compare_amounts(total, rec.approved_net_total) != 0:
                raise UserError(
                    "Payroll period %s totals %.2f but %.2f was approved - nothing is paid "
                    "from a changed run." % (rec.name, total, rec.approved_net_total)
                )

    # ---- pre-validation (M56-14, BRU-PAY-05/13) -------------------------------
    def _payroll_prevalidation_issues(self) -> list:
        """Every reason this run may not be approved or paid as it stands."""
        self.ensure_one()
        issues = []
        company = self.company_id
        slips = self.payslip_ids
        if not slips:
            issues.append("the run has no payslip")
        account = (self.company_account_no or "").strip()
        routing = (self.company_routing_no or "").strip()
        if not account or not routing:
            issues.append("the company originating account and routing number are not entered")
        elif not validate_routing_number(routing):
            issues.append("the company routing number %r is not 9 digits" % routing)
        floor = company.payroll_minimum_basic_monthly or 0.0
        seen = set()
        for slip in slips.sudo():
            emp = slip.employee_id
            name = emp.name or "?"
            if emp.id in seen:
                issues.append("%s has more than one payslip in the run" % name)
            seen.add(emp.id)
            contract = slip.contract_id
            if (
                not contract
                or contract.employee_id != emp
                or contract.state not in ("active", "terminated")
            ):
                issues.append("%s's payslip has no active or terminated contract behind it" % name)
            if emp.company_id != company or slip.company_id != company:
                issues.append("%s's payslip belongs to another company" % name)
            if (slip.basic or 0.0) <= 0:
                issues.append("%s has a zero basic" % name)
            elif floor and (contract.basic_monthly or 0.0) < floor:
                issues.append(
                    "%s's monthly basic %.2f is below the minimum %.2f"
                    % (name, contract.basic_monthly, floor)
                )
            if (slip.net or 0.0) < 0:
                issues.append("%s has a negative net pay of %.2f" % (name, slip.net))
            if (slip.net or 0.0) > 0:
                acc = (slip.bank_account_no or "").strip()
                rt = (slip.routing_no or "").strip()
                if not acc or not rt:
                    issues.append("%s has no registered salary account and routing number" % name)
                elif not validate_routing_number(rt):
                    issues.append("%s's routing number %r is not 9 digits" % (name, rt))
                elif len(acc) > BEFTN_ACCOUNT_WIDTH:
                    issues.append(
                        "%s's account number is longer than the %d-character BEFTN field"
                        % (name, BEFTN_ACCOUNT_WIDTH)
                    )
        return issues

    def _raise_prevalidation(self):
        for rec in self:
            issues = rec._payroll_prevalidation_issues()
            if issues:
                raise UserError(
                    "Payroll period %s fails pre-validation and cannot be approved or paid: %s."
                    % (rec.name, "; ".join(issues))
                )

    def action_prevalidate(self):
        """The officer's check before requesting approval."""
        for rec in self:
            if rec.state != "calculated":
                raise UserError("Calculate the run before validating it.")
            rec._raise_prevalidation()
            rec.message_post(body="Pre-validation passed: %d payslip(s)." % rec.slip_count)
        return {"issues": []}

    @api.depends(
        "payslip_ids.net",
        "payslip_ids.gross",
        "payslip_ids.tax_withheld",
        "payslip_ids.pf_employee",
        "payslip_ids.pf_employer",
    )
    def _compute_counts(self):
        for rec in self:
            rec.slip_count = len(rec.payslip_ids)
            rec.net_total = sum(rec.payslip_ids.mapped("net"))
            rec.gross_total = sum(rec.payslip_ids.mapped("gross"))
            rec.tax_total = sum(rec.payslip_ids.mapped("tax_withheld"))
            rec.pf_total = sum(rec.payslip_ids.mapped("pf_employee")) + sum(
                rec.payslip_ids.mapped("pf_employer")
            )

    # ---- attendance gate (BRU-PAY-01, M56-15) ---------------------------------
    def _attendance_lock(self):
        """This period's attendance lock: same company, and the period's
        operating unit or a company-wide lock."""
        self.ensure_one()
        domain = [
            ("company_id", "=", self.company_id.id),
            ("period_start", "<=", self.period_start),
            ("period_end", ">=", self.period_end),
            ("state", "=", "locked"),
        ]
        if self.operating_unit_id:
            domain.append(("operating_unit_id", "in", [False, self.operating_unit_id.id]))
        else:
            domain.append(("operating_unit_id", "=", False))
        return self.env["fix.attendance.lock"].search(domain, limit=1)

    def _check_attendance_gate(self):
        """The gate itself, run by verify AND by calculate: attendance
        re-opened after verification stops the calculation (probe A8c)."""
        for rec in self:
            if not rec._attendance_lock():
                raise UserError(
                    "Journey 13: attendance for %s is not LOCKED — payroll "
                    "may not calculate on open attendance" % rec.name
                )
            # BRU-WFM-01 / BRU-PAY-01: VERIFIED and locked - a flagged clock-in still
            # pending approval is neither counted nor silently dropped
            pending = self.env["fix.attendance.record"].pending_in_period(
                rec.period_start, rec.period_end, rec.company_id
            )
            if pending:
                raise UserError(
                    "Journey 13: %d clock-in(s) of %s are still pending approval - payroll "
                    "may not calculate on unverified attendance: %s"
                    % (len(pending), rec.name, ", ".join(pending.mapped("display_label")))
                )

    def action_verify_attendance_locked(self):
        """T05: the gate — no calculation without the month's lock."""
        for rec in self:
            # A committed run is never re-opened for recalculation: that
            # silently voided the approval (A09 probe A7).
            if rec.state in FROZEN_PERIOD_STATES:
                raise UserError(
                    "Payroll period %s is %s - a committed run is not recalculated."
                    % (rec.name, dict(PERIOD_FLOW)[rec.state])
                )
            rec._refuse_while_pending("re-open it")
            rec._check_attendance_gate()
            rec._guarded().write({"state": "attendance_locked"})
            publish(
                self.env,
                "payroll.attendance_locked",
                "fix.payroll.period",
                rec.id,
                {"period": rec.name},
            )

    # ---- who is paid (C2, I3) -------------------------------------------------
    def _payroll_population(self):
        """([(employee, contract, paid_days)], [(employee, reason)], [employees
        with two active contracts]) for this period."""
        self.ensure_one()
        start, end = self.period_start, self.period_end
        employees = (
            self.env["hr.employee"]
            .with_context(active_test=False)
            .search([("company_id", "=", self.company_id.id)])
        )
        contracts = self.env["fix.employment.contract"].search(
            [("employee_id", "in", employees.ids), ("state", "in", ("active", "terminated"))],
            order="joining_date desc, id desc",
        )
        by_emp = {}
        for contract in contracts:
            by_emp.setdefault(contract.employee_id.id, []).append(contract)
        plan, skipped, conflicts = [], [], []
        period_days = (end - start).days + 1
        for emp in employees:
            own = by_emp.get(emp.id, [])
            active = [c for c in own if c.state == "active"]
            if len(active) > 1:
                conflicts.append(emp)
                continue
            left = emp.sudo().left_date
            if left and left < start:
                if own:
                    skipped.append((emp, "left on %s, before the period" % left))
                continue
            if left and left <= end:
                contract = (active or [c for c in own if c.joining_date <= left] or [None])[0]
                if not contract:
                    skipped.append((emp, "left on %s with no contract to pay from" % left))
                    continue
                paid_days = (left - max(start, contract.joining_date)).days + 1
            else:
                if not active:
                    if own:
                        skipped.append((emp, "no active contract"))
                    continue
                contract = active[0]
                if not emp.active:
                    skipped.append((emp, "archived employee with an active contract"))
                    continue
                paid_days = period_days
            if contract.joining_date > end:
                skipped.append((emp, "joins on %s, after the period" % contract.joining_date))
                continue
            plan.append((emp, contract, min(paid_days, period_days)))
        return plan, skipped, conflicts

    def _payable_overtime_hours(self, employee, until=None):
        """Overtime of the locked month an employee is paid for: none for an
        employee not eligible (BLA s.108 eligibility, M56-15), and only from
        clock-ins that are approved or need no approval."""
        self.ensure_one()
        if not employee.sudo().overtime_eligible:
            return Decimal("0")
        end = min(self.period_end, until) if until else self.period_end
        records = self.env["fix.attendance.record"].search(
            [
                ("employee_id", "=", employee.id),
                ("company_id", "=", self.company_id.id),
                ("approval_state", "in", ("approved", "not_required")),
                ("check_in", ">=", fields.Datetime.to_datetime(self.period_start)),
                ("check_in", "<", fields.Datetime.to_datetime(end + timedelta(days=1))),
            ]
        )
        return Decimal(str(sum(records.mapped("overtime_hours"))))

    def _oncall_allowance(self, employee):
        """(amount, records): the standby allowance of the employee's COMPLETED
        on-call shifts starting in the period (M55 fix.hr.oncall)."""
        self.ensure_one()
        if "fix.hr.oncall" not in self.env:
            return 0.0, None
        recs = (
            self.env["fix.hr.oncall"]
            .sudo()
            .search(
                [
                    ("employee_id", "=", employee.id),
                    ("company_id", "=", self.company_id.id),
                    ("state", "=", "completed"),
                    ("date_from", ">=", fields.Datetime.to_datetime(self.period_start)),
                    (
                        "date_from",
                        "<",
                        fields.Datetime.to_datetime(self.period_end + timedelta(days=1)),
                    ),
                ]
            )
        )
        return round(float(sum(recs.mapped("allowance"))), 2), recs

    def _incentive_lines(self, employee, released_slip_ids):
        """I4: the approved, unattached M57 incentive lines of this period.

        A line counts once: lines already attached to a slip that still
        exists elsewhere are left alone; lines attached to one of this run's
        own earlier slips (being replaced by the recalculation) are picked up
        again."""
        self.ensure_one()
        if "fix.incentive.line" not in self.env:
            return None
        Line = self.env["fix.incentive.line"].sudo()
        ym = self.period_start.strftime("%Y-%m")
        lines = Line.search(
            [
                ("employee_id", "=", employee.id),
                ("company_id", "=", self.company_id.id),
                ("run_id.state", "=", "approved"),
                ("run_id.period", "in", list({self.name, ym})),
            ]
        )
        attached_ids = {line.payslip_ref_id for line in lines if line.payslip_ref_id}
        live = set(self.env["fix.payslip"].sudo().browse(list(attached_ids)).exists().ids)
        return lines.filtered(
            lambda line: (
                not line.payslip_ref_id
                or line.payslip_ref_id in released_slip_ids
                or line.payslip_ref_id not in live
            )
        )

    def action_calculate(self):
        for rec in self:
            if rec.state != "attendance_locked":
                raise UserError("Lock attendance before calculating")
            rec._refuse_while_pending("recalculate it")
            # The gate is re-checked here: re-opening attendance after the
            # verify step stops the calculation (A09 probe A8c).
            rec._check_attendance_gate()
            plan, skipped, conflicts = rec._payroll_population()
            if conflicts:
                raise UserError(
                    "Payroll period %s cannot be calculated: %s each hold more than one active "
                    "employment contract. An employee is paid from exactly one active contract."
                    % (rec.name, ", ".join(emp.name for emp in conflicts))
                )
            rec._guarded().write({"calculator_id": self.env.user.id})
            # A recalculation replaces this run's earlier slips. The officer
            # holds no unlink ACL on payslips: only this transition removes them.
            released = set(rec.payslip_ids.ids)
            rec.payslip_ids.sudo().unlink()
            company = rec.company_id
            basis = statutory_basis(company)
            period_days = (rec.period_end - rec.period_start).days + 1
            divisor = Decimal(str(company.ot_divisor_hours or 0.0)) or OT_DIVISOR_HOURS
            ceiling = company.ita_exemption_ceiling or float(SALARY_EXEMPTION_CEILING)
            paid_notes = []
            for emp, contract, paid_days in plan:
                factor = Decimal(paid_days) / Decimal(period_days)

                def earned(amount, factor=factor):
                    return float(q2(Decimal(str(amount or 0.0)) * factor))

                # The employee master's sensitive fields (bank, routing, tax
                # profile) are HR-group fields a payroll officer does not read
                # directly: the run reads them with sudo.
                master = emp.sudo()
                left = master.left_date if paid_days < period_days else None
                ot_hours = rec._payable_overtime_hours(emp, until=left)
                # Only REAL bank details are carried onto the payslip: the
                # employee master's registered account and BEFTN routing code.
                # A missing or conflicting one stays empty and fails
                # pre-validation (R01 re-audit; A09 A3, M56-6).
                bank_acc, routing, bank_n, bank_problem = master_bank_details(emp)
                if bank_problem:
                    paid_notes.append(bank_problem)
                oncall, oncall_recs = rec._oncall_allowance(emp)
                if oncall_recs:
                    paid_notes.append(
                        "%s on-call allowance %.2f (%s)"
                        % (emp.name, oncall, ", ".join(oncall_recs.mapped("name")))
                    )

                inc_lines = rec._incentive_lines(emp, released)
                inc_amount = float(sum(inc_lines.mapped("amount"))) if inc_lines else 0.0

                slip = (
                    self.env["fix.payslip"]
                    ._guarded()
                    .create(
                        {
                            "period_id": rec.id,
                            "company_id": company.id,
                            "employee_id": emp.id,
                            "contract_id": contract.id,
                            "paid_days": paid_days,
                            "period_days": period_days,
                            "basic": earned(contract.basic_monthly),
                            "house_rent": earned(contract.house_rent),
                            "medical_allowance": earned(contract.medical_allowance),
                            "conveyance_allowance": earned(contract.conveyance_allowance),
                            "technical_allowance": earned(contract.technical_allowance),
                            "other_allowance": earned(contract.other_allowance) + oncall,
                            "oncall_allowance": oncall,
                            "dearness_allowance": earned(contract.dearness_allowance),
                            "adhoc_allowance": earned(contract.adhoc_allowance),
                            "ot_hours": float(ot_hours),
                            # A prorated basic keeps the full month's hourly
                            # rate: the divisor is prorated with it.
                            "ot_divisor_hours": float(divisor * factor),
                            "exemption_ceiling": ceiling,
                            "incentive": inc_amount,
                            # C2: the employee's own tax profile (the contract
                            # fields this read before do not exist)
                            "taxpayer_category": master.taxpayer_category or "general",
                            "minimum_tax_location": master.minimum_tax_location
                            or "dhaka_chattogram",
                            "has_disabled_child": bool(master.has_disabled_child),
                            # BRU-PAY-10: a rebate only on a validated
                            # declaration, and there is no declaration model
                            "investment_allowance": 0.0,
                            "bank_account_no": bank_acc,
                            "routing_no": routing,
                            "bank_name": bank_n,
                            "statutory_basis": basis,
                        }
                    )
                )
                for line in inc_lines or []:
                    line._fix_attach_payslip(slip)
                if paid_days < period_days:
                    paid_notes.append(
                        "%s paid %d of %d days (left %s)"
                        % (emp.name, paid_days, period_days, master.left_date)
                    )
            note_lines = ["Paid %d employee(s)." % len(plan)]
            note_lines += paid_notes
            note_lines += ["Skipped %s: %s." % (emp.name, why) for emp, why in skipped]
            note = "\n".join(note_lines)
            rec._guarded().write({"state": "calculated", "calculation_note": note})
            rec.message_post(body=note.replace("\n", "<br/>"))

    def action_approve(self):
        """The approver's decision, run from the M63 inbox task.

        SoD: the approver holds the Payroll Manager role and is neither the
        calculator nor the requester (DoD-04). There is no context bypass:
        the former ``bypass_payroll_sod`` key let any caller self-approve.

        Approval pins the run: the approver, the time, a digest of what each
        slip pays and to which account, and the net total."""
        self._approval_assert_routed()
        self._people_assert_not_conflicted()
        decider = self._people_decider()
        if not (self.env.su or decider.has_group(PAYROLL_MANAGER)):
            raise AccessError("Only a Payroll Manager can approve a payroll period.")
        for rec in self:
            if rec.state != "calculated":
                raise UserError("Calculate before approving")
            if rec.calculator_id and rec.calculator_id in rec._approval_acting_users():
                raise UserError(
                    "Maker-Checker SoD violation: Approver cannot be the same user (%s) who calculated the payroll period."
                    % rec.calculator_id.name
                )
            rec._raise_prevalidation()
            digest, total = rec._payroll_snapshot()
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": decider.id,
                    "approved_on": fields.Datetime.now(),
                    "approved_digest": digest,
                    "approved_net_total": total,
                }
            )
            publish(
                self.env,
                "payroll.approved",
                "fix.payroll.period",
                rec.id,
                {"period": rec.name, "net": float(rec.net_total)},
            )

    def _release_conflicts(self):
        self.ensure_one()
        return (
            self.calculator_id
            | self.approved_by_id
            | self.approval_request_id.sudo().requested_by_id
            | self.create_uid
        )

    def action_pay(self):
        """BEFTN disbursement — the batch window decides the settlement
        date (INT-005): modelled, never assumed instant. Released by a
        Payroll Disbursement Releaser who did not prepare, calculate or
        approve the run (SOD-29)."""
        check_releaser(self, "a payroll period", lambda rec: rec._release_conflicts())
        for rec in self:
            if rec.state != "approved":
                raise UserError("Approve before paying")
            rec._check_approved_snapshot()
            submitted = datetime.now()
            # The batch carries the APPROVED total, not a fresh sum: the file
            # must pay exactly what the approver saw.
            batch = (
                self.env["fix.beftn.batch"]
                ._guarded()
                .create(
                    {
                        "period_id": rec.id,
                        "company_id": rec.company_id.id,
                        "submitted_at": submitted,
                        "settlement_date": beftn_settlement_date(submitted),
                        "employee_count": rec.slip_count,
                        "total_amount": rec.approved_net_total,
                        "company_account_no": rec.company_account_no,
                        "company_routing_no": rec.company_routing_no,
                        "released_by_id": self.env.user.id,
                    }
                )
            )
            batch.action_generate_beftn_file()
            rec._guarded().write(
                {
                    "state": "paid",
                    "beftn_batch_id": batch.id,
                    "released_by_id": self.env.user.id,
                    "released_on": fields.Datetime.now(),
                }
            )
            publish(
                self.env,
                "payroll.beftn_submitted",
                "fix.payroll.period",
                rec.id,
                {
                    "period": rec.name,
                    "batch_id": batch.id,
                    "settlement": str(batch.settlement_date),
                },
            )

    def action_publish_payslips(self):
        """FR-PAY-050/051: a paid run's payslips are published once, with a
        content digest; the employee then reads their own slip."""
        if not (self.env.su or self.env.user.has_group(PAYROLL_OFFICER)):
            raise AccessError("Only payroll can publish payslips.")
        now = fields.Datetime.now()
        for rec in self:
            if rec.state not in ("paid", "posted"):
                raise UserError(
                    "Payroll period %s is %s: payslips are published once the run is paid."
                    % (rec.name, dict(PERIOD_FLOW)[rec.state])
                )
            slips = rec.payslip_ids.filtered(lambda s: not s.published)
            for slip in slips:
                slip._guarded().write(
                    {
                        "published": True,
                        "published_on": now,
                        "published_digest": slip._content_digest(),
                    }
                )
            rec._guarded().write({"payslips_published_on": now})
            publish(
                self.env,
                "payroll.payslips_published",
                "fix.payroll.period",
                rec.id,
                {"period": rec.name, "count": len(slips)},
            )
        return {"published": True}

    def action_post(self):
        """GL posting to M19 (P08-M03-T07): a balanced, POSTED journal entry
        from the payslip totals, on the accounts the period company configured
        (res.company payroll_* fields - never defaulted or invented here):

            Dr salary & wage expense   basic / overtime / incentive
            Dr employer PF expense     employer PF contribution
               Cr net salary payable   net pay
               Cr TDS payable          income tax withheld
               Cr PF payable           employee + employer PF

        Refused when the accounting is not configured, posted once only, and
        debits == credits is checked before the entry is posted. Emits
        payroll.posted for M54's W6 consumption."""
        for rec in self:
            if rec.gl_move_id:
                raise UserError(
                    "Payroll period %s is already posted to the GL (%s) - a period is "
                    "posted once." % (rec.name, rec.gl_move_id.name)
                )
            if rec.state != "paid":
                raise UserError("Pay before posting")
            company = rec.company_id
            currency = company.currency_id
            if rec.currency_id != currency:
                raise UserError(
                    "Payroll period %s is in %s but %s keeps its ledger in %s - no "
                    "exchange rate is assumed for a payroll posting."
                    % (rec.name, rec.currency_id.name, company.name, currency.name)
                )
            journal = payroll_gl_journal(company, PAYROLL_GL_ACCOUNTS, rec.name)

            slips = rec.payslip_ids
            gross = sum(slips.mapped("gross"))
            net = sum(slips.mapped("net"))
            pf_emp = sum(slips.mapped("pf_employee"))
            pf_empr = sum(slips.mapped("pf_employer"))
            tax = sum(slips.mapped("tax_withheld"))
            allowances_sum = (
                sum(slips.mapped("house_rent"))
                + sum(slips.mapped("medical_allowance"))
                + sum(slips.mapped("conveyance_allowance"))
                + sum(slips.mapped("technical_allowance"))
                + sum(slips.mapped("other_allowance"))
                + sum(slips.mapped("dearness_allowance"))
                + sum(slips.mapped("adhoc_allowance"))
            )
            components = [  # (account field, label, debit, credit)
                (
                    "payroll_salary_expense_account_id",
                    "Basic salary",
                    sum(slips.mapped("basic")),
                    0.0,
                ),
                (
                    "payroll_salary_expense_account_id",
                    "Allowances",
                    allowances_sum,
                    0.0,
                ),
                (
                    "payroll_salary_expense_account_id",
                    "Overtime",
                    sum(slips.mapped("overtime")),
                    0.0,
                ),
                (
                    "payroll_salary_expense_account_id",
                    "Incentive",
                    sum(slips.mapped("incentive")),
                    0.0,
                ),
                ("payroll_pf_expense_account_id", "Employer PF contribution", pf_empr, 0.0),
                ("payroll_net_payable_account_id", "Net salary payable", 0.0, net),
                ("payroll_tax_payable_account_id", "Income tax withheld (TDS)", 0.0, tax),
                ("payroll_pf_payable_account_id", "Provident fund payable", 0.0, pf_emp + pf_empr),
            ]
            lines = []
            for fname, label, debit, credit in components:
                debit, credit = currency.round(debit), currency.round(credit)
                if currency.is_zero(debit) and currency.is_zero(credit):
                    continue  # a component this period does not carry
                lines.append(
                    {
                        "account_id": company[fname].id,
                        "name": f"{label} - {rec.name}",
                        "debit": debit,
                        "credit": credit,
                    }
                )
            if not lines:
                raise UserError("Payroll period %s has nothing to post to the GL." % rec.name)
            total_debit = currency.round(sum(line["debit"] for line in lines))
            total_credit = currency.round(sum(line["credit"] for line in lines))
            if currency.compare_amounts(total_debit, total_credit) != 0:
                raise UserError(
                    "GL Unbalanced: Debits (%.2f) != Credits (%.2f) for period %s"
                    % (total_debit, total_credit, rec.name)
                )
            # cd_gl_ext's posting helper: posts the entry and attaches the
            # operating-unit dimension to every line (AS-03), in this transaction.
            move, _dimensions = post_with_dimensions(
                self.env,
                {
                    "move_type": "entry",
                    "ref": f"Payroll GL Posting - {rec.name}",
                    "journal_id": journal.id,
                    "date": rec.period_end,
                    "line_ids": [Command.create(line) for line in lines],
                },
                {idx: {"operating_unit_id": rec.operating_unit_id.id} for idx in range(len(lines))},
            )
            rec._guarded().write({"gl_move_id": move.id, "state": "posted"})
            publish(
                self.env,
                "payroll.posted",
                "fix.payroll.period",
                rec.id,
                {
                    "period": rec.name,
                    "gross": float(gross),
                    "net": float(net),
                    "tax": float(tax),
                    "pf": float(pf_emp + pf_empr),
                    "total_debit": total_debit,
                    "total_credit": total_credit,
                },
            )


class FixPayslip(models.Model):
    """One employee-month. ALL arithmetic delegates to the payroll engine
    (libs/py/payroll_engine) — the DoD-03 100%-covered authority."""

    _name = "fix.payslip"
    _description = "Payslip"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | PAYSLIP_GUARDED_FIELDS

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(slip.period_id.state in FROZEN_PERIOD_STATES for slip in self):
            locked |= set(self._fields)  # a frozen slip offers no input at all
        return locked

    def _check_period_open(self, periods):
        """No payslip of a committed period is created, changed or deleted -
        not even through a transition (a ghost slip rode an approved run's
        BEFTN file, A09 probe A6). Superuser code (data repair, seeds) is
        trusted, as everywhere the guard applies."""
        if self.env.su:
            return
        frozen = periods.filtered(lambda p: p.state in FROZEN_PERIOD_STATES)
        if frozen:
            raise UserError(
                "Payroll period %s is %s: its payslips are frozen. A change to an "
                "approved run goes through a correction run, never an edit."
                % (
                    ", ".join(frozen.mapped("name")),
                    dict(PERIOD_FLOW)[frozen[0].state],
                )
            )

    @api.model_create_multi
    def create(self, vals_list):
        period_ids = {vals["period_id"] for vals in vals_list if vals.get("period_id")}
        self._check_period_open(self.env["fix.payroll.period"].browse(period_ids))
        return super().create(vals_list)

    def write(self, vals):
        periods = self.period_id
        if vals.get("period_id"):
            periods |= self.env["fix.payroll.period"].browse(vals["period_id"])
        # Publication is the one change a committed slip takes, and only from
        # the period's publish transition.
        publishing = set(vals) <= PAYSLIP_PUBLICATION_FIELDS and self._fix_guard_has_token()
        if not publishing:
            self._check_period_open(periods)
        return super().write(vals)

    # ---- employee self-service (FR-PAY-051, M56-8) ---------------------------
    def _fix_own_published(self):
        """This user's own PUBLISHED payslips (read as payroll)."""
        return self.sudo().search(
            [("employee_id.user_id", "=", self.env.uid), ("published", "=", True)],
            order="id desc",
        )

    @api.model
    def fix_my_payslips(self):
        """The caller's own published payslips, as rows. A plain employee holds
        no payslip ACL: this is the only window, and it shows only their own."""
        return [
            {
                "id": slip.id,
                "period": slip.period_id.name,
                "basic": round(slip.basic or 0.0, 2),
                "gross": round(slip.gross or 0.0, 2),
                "tax": round(slip.tax_withheld or 0.0, 2),
                "pf": round(slip.pf_employee or 0.0, 2),
                "net": round(slip.net or 0.0, 2),
                "published_on": str(slip.published_on or "")[:16],
                "digest": slip.published_digest,
            }
            for slip in self._fix_own_published()
        ]

    @api.model
    def fix_my_payslip_html(self, slip_id):
        """The Bengali payslip (cd_payroll_bd.report_payslip_bn) of one of the
        caller's own published slips; any other slip is refused."""
        slip = self._fix_own_published().filtered(lambda s: s.id == int(slip_id or 0))
        if not slip:
            raise AccessError("You can print only your own published payslip.")
        html, _kind = (
            self.env["ir.actions.report"]
            .sudo()
            ._render_qweb_html("cd_payroll_bd.action_report_payslip_bn", slip.ids)
        )
        return html.decode() if isinstance(html, bytes) else html

    def _content_digest(self) -> str:
        """SHA-256 of what the published slip says (FR-PAY-050 hash)."""
        self.ensure_one()
        return hashlib.sha256(
            json.dumps(
                [
                    self.id,
                    self.period_id.name,
                    self.employee_id.id,
                    "%.2f" % self.basic,
                    "%.2f" % self.gross,
                    "%.2f" % self.pf_employee,
                    "%.2f" % self.tax_withheld,
                    "%.2f" % self.net,
                    (self.bank_account_no or "").strip(),
                    (self.routing_no or "").strip(),
                ]
            ).encode()
        ).hexdigest()

    def unlink(self):
        self._check_period_open(self.period_id)
        return super().unlink()

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    period_id = fields.Many2one("fix.payroll.period", required=True, ondelete="cascade", index=True)
    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    # The contract the run paid from (C2: exactly one active contract), and
    # how much of the month it paid (I3: a leaver is prorated to the left date).
    contract_id = fields.Many2one(
        "fix.employment.contract", string="Contract", readonly=True, ondelete="restrict"
    )
    paid_days = fields.Integer(string="Paid Days", readonly=True)
    oncall_allowance = fields.Monetary(
        string="On-Call Allowance (in Other Allowance)",
        currency_field="currency_id",
        readonly=True,
        help="Completed M55 on-call shifts of the period, included in Other Allowance.",
    )
    period_days = fields.Integer(string="Days in Period", readonly=True)
    # The company configuration the slip was calculated with, pinned on the
    # slip (BRU-PAY-07): a later settings change never recomputes it.
    ot_divisor_hours = fields.Float(
        string="Overtime Divisor (h)",
        readonly=True,
        help="The company divisor at calculation, prorated with the basic for a part month "
        "so the hourly rate stays the full month's.",
    )
    exemption_ceiling = fields.Float(string="Para 27 Exemption Ceiling", readonly=True)
    statutory_basis = fields.Char(
        string="Statutory Basis",
        readonly=True,
        help="The tax table, separation bands and minimum-wage floor this slip was computed "
        "under (company decision flags, A09 report section 7.3/7.4).",
    )
    # FR-PAY-050: publication, once, with the content digest
    published = fields.Boolean(string="Published to Employee", readonly=True, default=False)
    published_on = fields.Datetime(string="Published On", readonly=True)
    published_digest = fields.Char(string="Published Content Digest", readonly=True)
    basic = fields.Monetary(string="Basic", currency_field="currency_id", required=True)
    house_rent = fields.Monetary(
        string="House Rent Allowance", currency_field="currency_id", default=0.0
    )
    medical_allowance = fields.Monetary(
        string="Medical Allowance", currency_field="currency_id", default=0.0
    )
    conveyance_allowance = fields.Monetary(
        string="Conveyance Allowance", currency_field="currency_id", default=0.0
    )
    technical_allowance = fields.Monetary(
        string="Technical Skill / OEM Allowance", currency_field="currency_id", default=0.0
    )
    other_allowance = fields.Monetary(
        string="Other Allowance", currency_field="currency_id", default=0.0
    )
    dearness_allowance = fields.Monetary(
        string="Dearness Allowance", currency_field="currency_id", default=0.0
    )
    adhoc_allowance = fields.Monetary(
        string="Ad-hoc / Interim Allowance", currency_field="currency_id", default=0.0
    )
    ot_hours = fields.Float(string="Overtime Hours")
    incentive = fields.Monetary(
        string="Incentive (M57)",
        currency_field="currency_id",
        help="Applied by the M57 incentive engine before approval",
    )
    pf_employee_pct = fields.Float(string="PF Employee %", default=10.0)
    pf_employer_pct = fields.Float(string="PF Employer %", default=10.0)
    annual_taxable_other = fields.Monetary(
        string="YTD Taxable Outside This Slip",
        currency_field="currency_id",
        help="P08-M03-T08: migrated YTD statutory balances land here",
    )
    taxpayer_category = fields.Selection(
        [
            ("general", "General"),
            ("female_senior", "Female / Senior 65+"),
            ("disabled_third_gender", "Disabled / Third Gender"),
            ("freedom_fighter", "Gazetted Freedom Fighter"),
        ],
        string="Taxpayer Category",
        default="general",
    )
    has_disabled_child = fields.Boolean(string="Has Disabled Child", default=False)
    minimum_tax_location = fields.Selection(
        [
            ("dhaka_chattogram", "Dhaka/Chattogram City Corp"),
            ("other_city_corporation", "Other City Corporation"),
            ("non_city_corporation", "Non-City / Rural"),
        ],
        string="Tax Location",
        default="dhaka_chattogram",
    )
    investment_allowance = fields.Monetary(
        string="Annual Investment Allowance", currency_field="currency_id", default=0.0
    )
    bank_account_no = fields.Char(string="Bank Account No")
    routing_no = fields.Char(string="Routing No (9 digits)")
    bank_name = fields.Char(string="Bank Name")

    allowances_total = fields.Monetary(
        string="Allowances Total", currency_field="currency_id", compute="_compute_slip", store=True
    )
    annual_exemption = fields.Monetary(
        string="ITA 2023 Para 27 Annual Exemption",
        currency_field="currency_id",
        compute="_compute_slip",
        store=True,
    )
    # --- Final settlement (BLA 2006 s.20/s.26/s.27 + Labour (Amendment) Act 2026)
    # action_compute_separation / action_compute_retrenchment computed these and
    # returned them to the caller without ever writing them down, so the payslip
    # form's settlement fields had nothing to bind to and the operator's
    # "Compute Separation" click left no record on the slip.
    completed_years = fields.Integer(string="Completed Years of Service", readonly=True)
    gratuity_amount = fields.Monetary(
        string="Gratuity (BLA s.27)", currency_field="currency_id", readonly=True
    )
    resignation_compensation_amount = fields.Monetary(
        string="Resignation Compensation (BLA s.27)",
        currency_field="currency_id",
        readonly=True,
    )
    retrenchment_compensation = fields.Monetary(
        string="Retrenchment Compensation (BLA s.20)",
        currency_field="currency_id",
        readonly=True,
        help="30 days' wages per completed year, or gratuity if higher (s.20(2)(c)).",
    )
    notice_pay_amount = fields.Monetary(
        string="Notice Pay in Lieu (BLA s.20)",
        currency_field="currency_id",
        readonly=True,
        help="One month's notice (s.20(1)(a)) less the notice actually served.",
    )
    unused_leave_days = fields.Float(
        string="Unused Earned Leave (days)",
        default=0.0,
        readonly=True,
        help="From the leave controls at separation (I2); drives the encashment below.",
    )
    leave_encashment_amount = fields.Monetary(
        string="Leave Encashment",
        currency_field="currency_id",
        compute="_compute_leave_encashment",
        store=True,
        help="Daily wage (basic / 30) x unused earned leave days.",
    )

    @api.depends("basic", "unused_leave_days")
    def _compute_leave_encashment(self):
        for rec in self:
            daily = (rec.basic or 0.0) / 30.0
            rec.leave_encashment_amount = round(daily * (rec.unused_leave_days or 0.0), 2)

    gross = fields.Monetary(
        string="Gross", currency_field="currency_id", compute="_compute_slip", store=True
    )
    overtime = fields.Monetary(
        string="Overtime Pay", currency_field="currency_id", compute="_compute_slip", store=True
    )
    pf_employee = fields.Monetary(
        string="PF Employee", currency_field="currency_id", compute="_compute_slip", store=True
    )
    pf_employer = fields.Monetary(
        string="PF Employer", currency_field="currency_id", compute="_compute_slip", store=True
    )
    tax_withheld = fields.Monetary(
        string="Income Tax Withheld",
        currency_field="currency_id",
        compute="_compute_slip",
        store=True,
    )
    net = fields.Monetary(
        string="Net Pay", currency_field="currency_id", compute="_compute_slip", store=True
    )

    @api.depends(
        "basic",
        "house_rent",
        "medical_allowance",
        "conveyance_allowance",
        "technical_allowance",
        "other_allowance",
        "dearness_allowance",
        "adhoc_allowance",
        "ot_hours",
        "incentive",
        "pf_employee_pct",
        "pf_employer_pct",
        "annual_taxable_other",
        "taxpayer_category",
        "has_disabled_child",
        "minimum_tax_location",
        "investment_allowance",
        "ot_divisor_hours",
        "exemption_ceiling",
        # Not company_id.ot_divisor_hours / ita_exemption_ceiling: the slip
        # takes the company configuration when it is calculated and keeps it.
        # As a dependency, an administrator's later change recomputed the net
        # of slips already approved, paid and posted (A09 probe M8).
    )
    def _compute_slip(self):
        for rec in self:
            divisor_val = (
                rec.ot_divisor_hours
                or getattr(rec.company_id, "ot_divisor_hours", 0.0)
                or float(OT_DIVISOR_HOURS)
            )
            ceiling_val = rec.exemption_ceiling or getattr(
                rec.company_id, "ita_exemption_ceiling", 0.0
            )
            explicit_ceiling = Decimal(str(ceiling_val)) if ceiling_val > 0 else None
            result = compute_payslip(
                PayslipInput(
                    employee_ref=rec.employee_id.name or "",
                    basic_monthly=Decimal(str(rec.basic or 0.0)),
                    house_rent=Decimal(str(rec.house_rent or 0.0)),
                    medical_allowance=Decimal(str(rec.medical_allowance or 0.0)),
                    conveyance_allowance=Decimal(str(rec.conveyance_allowance or 0.0)),
                    technical_allowance=Decimal(str(rec.technical_allowance or 0.0)),
                    other_allowance=Decimal(str(rec.other_allowance or 0.0)),
                    dearness_allowance=Decimal(str(rec.dearness_allowance or 0.0)),
                    adhoc_allowance=Decimal(str(rec.adhoc_allowance or 0.0)),
                    ot_hours=Decimal(str(rec.ot_hours or 0.0)),
                    incentive=Decimal(str(rec.incentive or 0.0)),
                    pf_employee_pct=Decimal(str(rec.pf_employee_pct or 0.0)),
                    pf_employer_pct=Decimal(str(rec.pf_employer_pct or 0.0)),
                    annual_taxable_other=Decimal(str(rec.annual_taxable_other or 0.0)),
                    taxpayer_category=rec.taxpayer_category or "general",
                    disabled_dependents=1 if rec.has_disabled_child else 0,
                    tax_location=rec.minimum_tax_location or "dhaka_chattogram",
                    allowable_investment=Decimal(str(rec.investment_allowance or 0.0)),
                    ot_divisor_hours=Decimal(str(divisor_val)),
                    exemption_ceiling=explicit_ceiling,
                )
            )

            rec.allowances_total = float(result.allowances_total)
            rec.annual_exemption = float(result.annual_exemption)
            rec.gross = float(result.gross)
            rec.overtime = float(result.overtime)
            rec.pf_employee = float(result.pf_employee)
            rec.pf_employer = float(result.pf_employer)
            rec.tax_withheld = float(result.tax_month)
            rec.net = float(result.net)

    def _separation_inputs(self, separation_date=None):
        """(separation date, exit or None) for this slip's employee: the date
        given, else the employee's latest exit's last working day, else the
        employee's left date. The workspace button sends no date (probe M10)."""
        self.ensure_one()
        exit_rec = None
        if "fix.hr.exit" in self.env:
            exit_rec = (
                self.env["fix.hr.exit"]
                .sudo()
                .search(
                    [("employee_id", "=", self.employee_id.id), ("state", "!=", "cancelled")],
                    order="last_working_day desc, id desc",
                    limit=1,
                )
            ) or None
        if separation_date:
            day = fields.Date.to_date(separation_date)
        elif exit_rec:
            day = fields.Date.to_date(exit_rec.last_working_day)
        elif self.employee_id.sudo().left_date:
            day = self.employee_id.sudo().left_date
        else:
            raise UserError(
                "%s has no exit record and no left date: there is no separation date to "
                "compute from." % self.employee_id.display_name
            )
        return day, exit_rec

    def action_compute_separation(self, separation_date=None):
        """Gratuity + resignation compensation (engine bands, company decision
        flag) and the unused earned leave (I2), recorded on the slip.

        These are the settlement's figures for reference on the slip; the
        settlement itself is paid from the exit (I1) as an off-cycle payment."""
        self.ensure_one()
        self._check_period_open(self.period_id)
        day, _exit = self._separation_inputs(separation_date)
        basic, joining = separation_contract(self.env, self.employee_id, day)
        basic = Decimal(str(basic))
        grat = gratuity(basic, joining, day)
        comp = resignation_compensation(basic, joining, day)
        self._guarded().write(
            {
                "completed_years": completed_years(joining, day),
                "gratuity_amount": float(grat),
                "resignation_compensation_amount": float(comp),
                "unused_leave_days": unused_leave_days(self.employee_id, day),
            }
        )
        publish(
            self.env,
            "payroll.separation_computed",
            "fix.payslip",
            self.id,
            {
                "employee": self.employee_id.name,
                "gratuity": float(grat),
                "resignation_compensation": float(comp),
            },
        )
        return {"gratuity": float(grat), "resignation": float(comp)}

    def action_compute_retrenchment(self, termination_date=None, notice_given_days=None):
        """Retrenchment per Bangladesh Labour Act 2006 s.20: one month's notice
        or wages in lieu (s.20(1)(a)), plus 30 days' wages per completed year
        or gratuity, whichever is higher (s.20(2)(c)).

        It paid the s.26 termination notice of 120 days instead: 3 years at
        30,000 came to 210,000 rather than 120,000 (A09 probe M9).
        `notice_given_days` defaults to the notice the exit record shows."""
        self.ensure_one()
        self._check_period_open(self.period_id)
        day, exit_rec = self._separation_inputs(termination_date)
        if notice_given_days is None:
            notice_given_days = notice_served_days(exit_rec.notice_date, day) if exit_rec else 0
        if notice_given_days < 0:
            raise UserError("Notice given cannot be negative.")
        basic, joining = separation_contract(self.env, self.employee_id, day)
        basic = Decimal(str(basic))
        years = completed_years(joining, day)
        daily = basic / Decimal(30)
        notice_pay = q2(daily * max(RETRENCHMENT_NOTICE_DAYS - int(notice_given_days), 0))
        service = max(
            q2(daily * SERVICE_COMPENSATION_DAYS * years), q2(gratuity(basic, joining, day))
        )
        self._guarded().write(
            {
                "completed_years": years,
                "retrenchment_compensation": float(service),
                "notice_pay_amount": float(notice_pay),
                "unused_leave_days": unused_leave_days(self.employee_id, day),
            }
        )
        return float(service + notice_pay)


class FixBeftnBatch(models.Model):
    """INT-005: batch settlement with the cut-off calendar and 128-byte file
    generation. A batch pays exactly one approved document: a payroll period,
    an off-cycle payment or a festival bonus run."""

    _name = "fix.beftn.batch"
    _description = "BEFTN Batch"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.payroll.state.lock"]
    _order = "submitted_at desc"

    def _fix_guarded_fields(self) -> set:
        # The batch is built by a release step and its file by
        # action_generate_beftn_file; nothing on it is typed (A09 probe A11b:
        # a manager rewrote file_content and total_amount by write()).
        return super()._fix_guarded_fields() | {
            "state",
            "period_id",
            "offcycle_id",
            "bonus_run_id",
            "company_id",
            "currency_id",
            "submitted_at",
            "settlement_date",
            "employee_count",
            "total_amount",
            "company_account_no",
            "company_routing_no",
            "file_content",
            "file_name",
            "file_digest",
            "released_by_id",
            "settled_by_id",
            "settled_on",
        }

    def _payroll_state_locked_fields(self) -> set:
        # the bank's confirmation is evidence once the batch is settled
        locked = super()._payroll_state_locked_fields()
        if self.state == "settled":
            locked |= {
                "bank_confirmation_ref",
                "bank_confirmation_file",
                "bank_confirmation_filename",
            }
        return locked

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    period_id = fields.Many2one("fix.payroll.period", string="Payroll Period", ondelete="set null")
    offcycle_id = fields.Many2one(
        "fix.payroll.offcycle", string="Off-Cycle Payment", ondelete="set null", readonly=True
    )
    bonus_run_id = fields.Many2one(
        "fix.payroll.bonus.run", string="Festival Bonus Run", ondelete="set null", readonly=True
    )
    submitted_at = fields.Datetime(required=True, readonly=True)
    settlement_date = fields.Date(
        required=True,
        readonly=True,
        help="Engine-computed: after the 16:00 "
        "cut-off, or Fri/Sat/holiday, the next "
        "working day (Sun-Thu week)",
    )
    employee_count = fields.Integer()
    total_amount = fields.Monetary(string="Total Amount", currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    # No defaults: the originating account and routing number are the
    # company's real banking details and must be entered, never assumed.
    company_account_no = fields.Char(string="Company Originating Account")
    company_routing_no = fields.Char(string="Company Routing No")
    file_content = fields.Text(string="BEFTN 128-byte File", readonly=True)
    file_name = fields.Char(string="File Name", readonly=True)
    file_digest = fields.Char(string="File SHA-256", readonly=True)
    released_by_id = fields.Many2one("res.users", string="Released By", readonly=True)
    # FR-PAY-048: settled only against the bank's confirmation (M56-4)
    bank_confirmation_ref = fields.Char(string="Bank Confirmation Reference")
    bank_confirmation_file = fields.Binary(
        string="Bank Confirmation / Return File", attachment=True
    )
    bank_confirmation_filename = fields.Char(string="Bank Confirmation File Name")
    settled_by_id = fields.Many2one("res.users", string="Settled By", readonly=True)
    settled_on = fields.Datetime(string="Settled On", readonly=True)
    state = fields.Selection(
        [("submitted", "Submitted"), ("settled", "Settled")], default="submitted", required=True
    )

    def _source(self):
        """(document, description, [BeftnEntry]) for this batch, refused when
        the document is not approved or no longer matches its approval."""
        self.ensure_one()
        if self.period_id:
            return self._period_source()
        if self.offcycle_id:
            doc = self.offcycle_id
            return doc, "OFFCYCLE " + (doc.name or ""), doc._beftn_entries()
        if self.bonus_run_id:
            doc = self.bonus_run_id
            return doc, "BONUS " + (doc.name or ""), doc._beftn_entries()
        raise UserError("No payroll period linked to this BEFTN batch.")

    def _period_source(self):
        period = self.period_id
        if period.state != "approved":
            raise UserError(
                "A BEFTN file is built only for an APPROVED payroll period; %s is %s."
                % (period.name, dict(PERIOD_FLOW)[period.state])
            )
        # the slips still pay exactly what was approved, to the same accounts
        period._check_approved_snapshot()
        currency = period.currency_id
        if currency.compare_amounts(self.total_amount, period.approved_net_total) != 0:
            raise UserError(
                "BEFTN batch total %.2f differs from the %.2f approved for %s."
                % (self.total_amount, period.approved_net_total, period.name)
            )
        payable = period.payslip_ids.filtered(lambda slip: slip.net > 0)
        if not payable:
            raise UserError(
                "Payroll period %s has no payable payslip - there is nothing to send "
                "over BEFTN." % period.name
            )
        missing = payable.filtered(
            lambda slip: (
                not (slip.routing_no or "").strip() or not (slip.bank_account_no or "").strip()
            )
        )
        if missing:
            raise UserError(
                "Bank details are missing for: %s. A salary is never sent to an "
                "assumed account - complete the employee contract bank fields first."
                % ", ".join(missing.mapped("employee_id.name"))
            )
        entries = [
            beftn_entry(slip.employee_id, slip.bank_account_no, slip.routing_no, slip.net)
            for slip in payable
        ]
        return period, "SALARY " + (period.name or ""), entries

    def action_generate_beftn_file(self):
        """Generate standard Bangladesh Bank 128-byte fixed-width ASCII BEFTN batch."""
        self.ensure_one()
        if not (self.period_id or self.offcycle_id or self.bonus_run_id):
            raise UserError("No payroll period linked to this BEFTN batch.")
        # A file once generated has been submitted to the bank: it is never
        # rebuilt (A09 probe A11 regenerated a paid batch from a changed slip).
        if self.file_content:
            raise UserError(
                "BEFTN batch %s already holds its submitted file - a submitted file is "
                "never regenerated." % (self.file_name or self.id)
            )
        currency = self.currency_id
        company_account = (self.company_account_no or "").strip()
        company_routing = (self.company_routing_no or "").strip()
        if not company_account or not company_routing:
            raise UserError(
                "Enter the company originating account and routing number before "
                "generating a BEFTN file."
            )
        # validate_routing_number() RETURNS a bool (it never raises): the
        # previous try/except could not fire, so a malformed routing number
        # surfaced as a raw engine ValueError instead of a named UserError.
        if not validate_routing_number(company_routing):
            raise UserError(
                "Invalid company routing number %r: a BEFTN routing number is 9 digits."
                % company_routing
            )
        _doc, description, entries = self._source()
        # Control total: the credits in the file are the approved total. A
        # slip with a negative net was silently left out of the file, so the
        # employee went unpaid while the run "balanced" (A09 probe M6).
        credits = float(sum(entry.amount_bdt for entry in entries))
        if currency.compare_amounts(credits, self.total_amount) != 0:
            raise UserError(
                "The BEFTN credits for %s total %.2f but the approved run totals %.2f - "
                "a payslip with a negative net pay cannot be left out silently."
                % (description, credits, self.total_amount)
            )

        batch_header = BeftnBatchHeader(
            company_name="1000FIX SERVICES LTD",
            company_id=company_account,
            originating_routing=company_routing,
            batch_number=self.id or 1,
            settlement_date=self.settlement_date or fields.Date.today(),
            description=description,
        )

        content = generate_beftn_batch_file(batch_header, entries)
        label = (description.split(" ", 1)[-1] or "BATCH").replace("/", "-")
        self._guarded().write(
            {
                "file_content": content,
                "file_name": f"BEFTN_{label}_{self.id}.txt",
                "file_digest": hashlib.sha256(content.encode()).hexdigest(),
            }
        )
        return content

    def action_settle(self):
        """FR-PAY-048: the batch is settled from the bank's confirmation - a
        reference AND the bank's confirmation / return file - by a releaser,
        never on the date alone (A09 probe A10)."""
        if not (self.env.su or self.env.user.has_group(RELEASER)):
            raise AccessError(
                "Only a Payroll Disbursement Releaser (Finance) records the bank's settlement."
            )
        for rec in self:
            if rec.state != "submitted":
                raise UserError("BEFTN batch %s is already settled." % (rec.file_name or rec.id))
            if fields.Date.today() < rec.settlement_date:
                raise UserError(
                    "BEFTN settles %s — before the settlement date the batch "
                    "cannot be marked settled" % rec.settlement_date
                )
            if not (rec.bank_confirmation_ref or "").strip() or not rec.bank_confirmation_file:
                raise UserError(
                    "Attach the bank's confirmation (reference and confirmation / return file) "
                    "before marking BEFTN batch %s settled." % (rec.file_name or rec.id)
                )
            rec._guarded().write(
                {
                    "state": "settled",
                    "settled_by_id": self.env.user.id,
                    "settled_on": fields.Datetime.now(),
                }
            )
            publish(
                self.env,
                "payroll.beftn_settled",
                "fix.beftn.batch",
                rec.id,
                {"settlement": str(rec.settlement_date)},
            )


def beftn_entry(employee, account, routing, amount):
    """One validated BEFTN credit: a 9-digit routing number and an account
    that fits the 17-character field (it is never truncated)."""
    routing = (routing or "").strip()
    acc_no = (account or "").strip()
    if not routing or not acc_no:
        raise UserError(
            "Bank details are missing for: %s. A payment is never sent to an assumed account."
            % employee.name
        )
    if not validate_routing_number(routing):
        raise UserError(
            "Invalid bank routing number for employee %s: %r is not 9 digits."
            % (employee.name, routing)
        )
    if len(acc_no) > BEFTN_ACCOUNT_WIDTH:
        # The fixed-width entry record would silently cut the number
        # to 17 characters - i.e. credit a different account.
        raise UserError(
            "Bank account number for employee %s is longer than the %d-character "
            "BEFTN account field and would be truncated." % (employee.name, BEFTN_ACCOUNT_WIDTH)
        )
    return BeftnEntry(
        employee_id=f"EMP{employee.id:05d}",
        employee_name=(employee.name or "Employee").strip(),
        routing_number=routing,
        account_number=acc_no,
        amount_bdt=Decimal(str(round(amount, 2))),
    )


class ResCompanyPayrollAccounting(models.Model):
    """The payroll GL configuration of a company (M56 -> M19). Finance
    enters these; payroll posting refuses until every one is set."""

    _inherit = "res.company"

    payroll_journal_id = fields.Many2one(
        "account.journal",
        string="Payroll Journal",
        domain="[('type', '=', 'general'), ('company_id', '=', id)]",
    )
    payroll_salary_expense_account_id = fields.Many2one(
        "account.account", string="Salary & Wage Expense Account"
    )
    payroll_pf_expense_account_id = fields.Many2one(
        "account.account", string="Employer PF Contribution Expense Account"
    )
    payroll_net_payable_account_id = fields.Many2one(
        "account.account", string="Net Salary Payable Account"
    )
    payroll_tax_payable_account_id = fields.Many2one(
        "account.account", string="Income Tax (TDS) Payable Account"
    )
    payroll_pf_payable_account_id = fields.Many2one(
        "account.account", string="Provident Fund Payable Account"
    )
    ot_divisor_hours = fields.Float(
        string="Statutory Overtime Divisor Hours",
        default=float(OT_DIVISOR_HOURS),
        help="BLR 2015 formula: 208 hours/month (48h x 52 / 12)",
    )
    ita_exemption_ceiling = fields.Float(
        string="ITA 2023 Para 27 Exemption Ceiling (BDT)",
        default=0.0,
        help="Optional company override for ITA 2023 Sixth Schedule Part 1 Para 27 ceiling (default BDT 450,000)",
    )
