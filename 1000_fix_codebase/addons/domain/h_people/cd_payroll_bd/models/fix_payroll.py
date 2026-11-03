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
    BeftnBatchHeader,
    BeftnEntry,
    PayslipInput,
    beftn_settlement_date,
    completed_years,
    compute_payslip,
    generate_beftn_batch_file,
    gratuity,
    resignation_compensation,
    retrenchment_compensation,
    validate_routing_number,
)

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
    }
)


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
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.payroll.state.lock"]
    _order = "period_start desc"

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
        }

    def _payroll_state_locked_fields(self) -> set:
        """Fields frozen by this period's state: the scope once calculated,
        the originating account once the bank file exists."""
        locked = super()._payroll_state_locked_fields()
        if self.state not in ("draft", "attendance_locked"):
            locked |= {"period_start", "period_end", "company_id", "currency_id"}
            locked |= {"operating_unit_id"}
        if self.state in ("paid", "posted"):
            locked |= {"company_account_no", "company_routing_no"}
        return locked

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
            lock = self.env["fix.attendance.lock"].search(
                [
                    ("period_start", "<=", rec.period_start),
                    ("period_end", ">=", rec.period_end),
                    ("state", "=", "locked"),
                ],
                limit=1,
            )
            if not lock:
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
            rec._guarded().write({"state": "attendance_locked"})
            publish(
                self.env,
                "payroll.attendance_locked",
                "fix.payroll.period",
                rec.id,
                {"period": rec.name},
            )

    def action_calculate(self):
        for rec in self:
            if rec.state != "attendance_locked":
                raise UserError("Lock attendance before calculating")
            rec._guarded().write({"calculator_id": self.env.user.id})
            # A recalculation replaces this run's earlier slips. The officer
            # holds no unlink ACL on payslips: only this transition removes them.
            rec.payslip_ids.sudo().unlink()
            # Only this period's company: a superuser/multi-company run must not
            # pay another company's staff out of this company's BEFTN batch.
            employees = self.env["hr.employee"].search([("company_id", "=", rec.company_id.id)])
            # The period END is a whole day: check-ins up to (not including)
            # the following midnight count. `<= period_end` (00:00) dropped
            # the last day's overtime from the payslip.
            ot_from = fields.Datetime.to_datetime(rec.period_start)
            ot_until = fields.Datetime.to_datetime(rec.period_end + timedelta(days=1))
            for emp in employees:
                contract = self.env["fix.employment.contract"].search(
                    [("employee_id", "=", emp.id), ("state", "=", "active")], limit=1
                )
                if not contract:
                    continue
                ot_hours = Decimal(
                    str(
                        sum(
                            self.env["fix.attendance.record"]
                            .search(
                                [
                                    ("employee_id", "=", emp.id),
                                    ("check_in", ">=", ot_from),
                                    ("check_in", "<", ot_until),
                                ]
                            )
                            .mapped("overtime_hours")
                        )
                    )
                )

                # TODO(A09 P1, needs a tax adviser): the tax inputs below are
                # still read from contract fields that do not exist, so every
                # slip is taxed general/Dhaka (A09 M56-6). Left as-is in P0.
                tax_cat = getattr(contract, "taxpayer_category", False) or "general"
                tax_loc = getattr(contract, "tax_location", False) or "dhaka_chattogram"
                has_child = getattr(contract, "has_disabled_child", False)
                inv_allow = float(getattr(contract, "investment_allowance", 0.0) or 0.0)
                # The employee master's sensitive fields (bank, routing,
                # allowances) are HR-group fields a payroll officer does not
                # read directly: the run reads them with sudo.
                master = emp.sudo()
                # Only REAL bank details are carried onto the payslip. A missing
                # account/routing number stays empty and blocks the BEFTN file
                # (R01 re-audit 2026-10-22: placeholders "1234567890123" /
                # "020260123" / "BRAC Bank PLC" used to be substituted, which
                # would have routed a salary to a fabricated account).
                # The account is the employee's registered bank account record
                # (Odoo 19 bank_account_ids / primary_bank_account_id), the
                # routing number the employee master's BEFTN routing code. They
                # used to be read from contract fields that do not exist
                # (bank_account_no / bank_routing_no), so routing was always
                # empty and officers typed bank details onto the slips (A09 A3).
                primary_bank = master.primary_bank_account_id
                bank_acc = (primary_bank.acc_number or "").strip() or False
                routing = (master.routing_number or "").strip() or False
                bank_n = primary_bank.bank_id.name or False

                house_rent = float(
                    getattr(contract, "house_rent", 0.0)
                    or getattr(master, "house_rent", 0.0)
                    or 0.0
                )
                med_allow = float(
                    getattr(contract, "medical_allowance", 0.0)
                    or getattr(master, "medical_allowance", 0.0)
                    or 0.0
                )
                conv_allow = float(
                    getattr(contract, "conveyance_allowance", 0.0)
                    or getattr(master, "conveyance_allowance", 0.0)
                    or 0.0
                )
                tech_allow = float(
                    getattr(contract, "technical_allowance", 0.0)
                    or getattr(master, "technical_allowance", 0.0)
                    or 0.0
                )
                other_allow = float(getattr(contract, "other_allowance", 0.0) or 0.0)
                da_allow = float(getattr(contract, "dearness_allowance", 0.0) or 0.0)
                adhoc_allow = float(getattr(contract, "adhoc_allowance", 0.0) or 0.0)

                inc_amount = 0.0
                inc_line = None
                if "fix.incentive.line" in self.env:
                    ym = rec.period_start.strftime("%Y-%m") if rec.period_start else ""
                    # M57's lines are own-record for plain users; the payroll
                    # run reads (and marks) the applied line of every employee.
                    inc_line = (
                        self.env["fix.incentive.line"]
                        .sudo()
                        .search(
                            [
                                ("employee_id", "=", emp.id),
                                ("run_id.state", "=", "applied"),
                                "|",
                                ("run_id.period", "=", rec.name),
                                ("run_id.period", "=", ym),
                            ],
                            order="id desc",
                            limit=1,
                        )
                    )
                    if inc_line:
                        inc_amount = float(inc_line.amount or 0.0)

                slip = (
                    self.env["fix.payslip"]
                    ._guarded()
                    .create(
                        {
                            "period_id": rec.id,
                            "company_id": rec.company_id.id,
                            "employee_id": emp.id,
                            "basic": float(contract.basic_monthly),
                            "house_rent": house_rent,
                            "medical_allowance": med_allow,
                            "conveyance_allowance": conv_allow,
                            "technical_allowance": tech_allow,
                            "other_allowance": other_allow,
                            "dearness_allowance": da_allow,
                            "adhoc_allowance": adhoc_allow,
                            "ot_hours": float(ot_hours),
                            "incentive": inc_amount,
                            "taxpayer_category": tax_cat,
                            "minimum_tax_location": tax_loc,
                            "has_disabled_child": has_child,
                            "investment_allowance": inv_allow,
                            "bank_account_no": bank_acc,
                            "routing_no": routing,
                            "bank_name": bank_n,
                        }
                    )
                )
                if inc_line:
                    inc_line.write({"payslip_ref_id": slip.id, "applied_to_payslip": True})
            rec._guarded().write({"state": "calculated"})

    def action_approve(self):
        """SoD: approver must differ from the calculator (DoD-04) and hold
        the Payroll Manager role. There is no context bypass: the former
        ``bypass_payroll_sod`` context key let any caller (RPC included)
        self-approve. calculator_id and state are guarded, so neither can be
        rewritten to get past this check.

        Approval pins the run: the approver, the time, a digest of what each
        slip pays and to which account, and the net total."""
        if not self.env.user.has_group("cd_payroll_bd.group_payroll_manager"):
            raise AccessError("Only a Payroll Manager can approve a payroll period.")
        for rec in self:
            if rec.state != "calculated":
                raise UserError("Calculate before approving")
            if rec.calculator_id and rec.calculator_id == self.env.user:
                raise UserError(
                    "Maker-Checker SoD violation: Approver cannot be the same user (%s) who calculated the payroll period."
                    % rec.calculator_id.name
                )
            digest, total = rec._payroll_snapshot()
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.user.id,
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

    def action_pay(self):
        """BEFTN disbursement — the batch window decides the settlement
        date (INT-005): modelled, never assumed instant."""
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
                        "submitted_at": submitted,
                        "settlement_date": beftn_settlement_date(submitted),
                        "employee_count": rec.slip_count,
                        "total_amount": rec.approved_net_total,
                        "company_account_no": rec.company_account_no,
                        "company_routing_no": rec.company_routing_no,
                    }
                )
            )
            batch.action_generate_beftn_file()
            rec._guarded().write({"state": "paid", "beftn_batch_id": batch.id})
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
            journal = company.payroll_journal_id
            missing = [label for fname, label in PAYROLL_GL_ACCOUNTS if not company[fname]]
            if not journal:
                missing.insert(0, "Payroll Journal")
            if missing:
                raise UserError(
                    "Configure the payroll accounting of %s before posting %s: %s."
                    % (company.name, rec.name, ", ".join(missing))
                )
            foreign = [
                label
                for fname, label in PAYROLL_GL_ACCOUNTS
                if company not in company[fname].company_ids
            ]
            if journal.company_id != company:
                foreign.insert(0, "Payroll Journal")
            if foreign:
                raise UserError(
                    "These payroll accounts of %s do not belong to the company: %s."
                    % (company.name, ", ".join(foreign))
                )

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
        self._check_period_open(periods)
        return super().write(vals)

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
    basic = fields.Monetary(string="Basic (Monthly)", currency_field="currency_id", required=True)
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
    )
    notice_pay_amount = fields.Monetary(
        string="Notice Pay in Lieu (BLA s.26)",
        currency_field="currency_id",
        readonly=True,
        help="The 120-day statutory notice less the notice actually served.",
    )
    unused_leave_days = fields.Float(
        string="Unused Earned Leave (days)",
        default=0.0,
        help="Earned leave carried to separation; drives the encashment below.",
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
        # Not company_id.ot_divisor_hours / ita_exemption_ceiling: the slip
        # takes the company configuration when it is calculated and keeps it.
        # As a dependency, an administrator's later change recomputed the net
        # of slips already approved, paid and posted (A09 probe M8).
    )
    def _compute_slip(self):
        for rec in self:
            divisor_val = getattr(rec.company_id, "ot_divisor_hours", 0.0) or float(
                OT_DIVISOR_HOURS
            )
            ceiling_val = getattr(rec.company_id, "ita_exemption_ceiling", 0.0)
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

    def action_compute_separation(self, separation_date):
        """Gratuity + resignation compensation per the Labour (Amendment)
        Act 2026 — P08-M03-T04's statutory core."""
        self.ensure_one()
        contract = self.env["fix.employment.contract"].search(
            [("employee_id", "=", self.employee_id.id), ("state", "in", ("active", "terminated"))],
            order="joining_date asc",
            limit=1,
        )
        if not contract:
            raise UserError("No contract found for separation pay")
        grat = gratuity(
            Decimal(str(self.basic)), fields.Date.to_date(contract.joining_date), separation_date
        )
        comp = resignation_compensation(
            Decimal(str(self.basic)), fields.Date.to_date(contract.joining_date), separation_date
        )
        # Record the settlement on the slip: it is the payable document, and the
        # figures must survive the call that produced them.
        self._guarded().write(
            {
                "completed_years": completed_years(
                    fields.Date.to_date(contract.joining_date), separation_date
                ),
                "gratuity_amount": float(grat),
                "resignation_compensation_amount": float(comp),
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

    def action_compute_retrenchment(self, termination_date, notice_given_days=0):
        """Retrenchment compensation per Bangladesh Labour Act 2006, Section 20 & 26.

        `notice_given_days` is the written notice actually served (0-120);
        the shortfall against the statutory 120 days is paid in lieu. (It was
        forwarded as `notice_given=`, a keyword the engine does not accept, so
        every call raised TypeError.)"""
        self.ensure_one()
        contract = self.env["fix.employment.contract"].search(
            [("employee_id", "=", self.employee_id.id), ("state", "in", ("active", "terminated"))],
            order="joining_date asc",
            limit=1,
        )
        if not contract:
            raise UserError("No contract found for retrenchment pay")
        comp = retrenchment_compensation(
            Decimal(str(self.basic)),
            fields.Date.to_date(contract.joining_date),
            termination_date,
            notice_given_days=notice_given_days,
        )
        # s.26 pays the unserved part of the 120-day statutory notice; the
        # engine returns service compensation and notice pay as one figure, so
        # split it here to show the operator what each part is.
        daily = Decimal(str(self.basic)) / Decimal(30)
        notice_pay = daily * Decimal(max(120 - notice_given_days, 0))
        self._guarded().write(
            {
                "completed_years": completed_years(
                    fields.Date.to_date(contract.joining_date), termination_date
                ),
                "retrenchment_compensation": float(comp),
                "notice_pay_amount": float(round(notice_pay, 2)),
            }
        )
        return float(comp)


class FixBeftnBatch(models.Model):
    """INT-005: batch settlement with the cut-off calendar and 128-byte file generation."""

    _name = "fix.beftn.batch"
    _description = "BEFTN Batch"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "submitted_at desc"

    def _fix_guarded_fields(self) -> set:
        # The batch is built by action_pay and its file by
        # action_generate_beftn_file; nothing on it is typed (A09 probe A11b:
        # a manager rewrote file_content and total_amount by write()).
        return super()._fix_guarded_fields() | {
            "state",
            "period_id",
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
        }

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    period_id = fields.Many2one("fix.payroll.period", string="Payroll Period", ondelete="set null")
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
    state = fields.Selection(
        [("submitted", "Submitted"), ("settled", "Settled")], default="submitted", required=True
    )

    def action_generate_beftn_file(self):
        """Generate standard Bangladesh Bank 128-byte fixed-width ASCII BEFTN batch."""
        self.ensure_one()
        if not self.period_id:
            raise UserError("No payroll period linked to this BEFTN batch.")
        # A file once generated has been submitted to the bank: it is never
        # rebuilt (A09 probe A11 regenerated a paid batch from a changed slip).
        if self.file_content:
            raise UserError(
                "BEFTN batch %s already holds its submitted file - a submitted file is "
                "never regenerated." % (self.file_name or self.id)
            )
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
        payable = self.period_id.payslip_ids.filtered(lambda slip: slip.net > 0)
        if not payable:
            raise UserError(
                "Payroll period %s has no payable payslip - there is nothing to send "
                "over BEFTN." % self.period_id.name
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
        entries = []
        for slip in payable:
            routing = slip.routing_no.strip()
            if not validate_routing_number(routing):
                raise UserError(
                    "Invalid bank routing number for employee %s: %r is not 9 digits."
                    % (slip.employee_id.name, routing)
                )
            acc_no = slip.bank_account_no.strip()
            if len(acc_no) > BEFTN_ACCOUNT_WIDTH:
                # The fixed-width entry record would silently cut the number
                # to 17 characters - i.e. credit a different account.
                raise UserError(
                    "Bank account number for employee %s is longer than the %d-character "
                    "BEFTN account field and would be truncated."
                    % (slip.employee_id.name, BEFTN_ACCOUNT_WIDTH)
                )
            emp_name = (slip.employee_id.name or "Employee").strip()
            entries.append(
                BeftnEntry(
                    employee_id=f"EMP{slip.employee_id.id:05d}",
                    employee_name=emp_name,
                    routing_number=routing,
                    account_number=acc_no,
                    amount_bdt=Decimal(str(round(slip.net, 2))),
                )
            )
        # Control total: the credits in the file are the approved total. A
        # slip with a negative net was silently left out of the file, so the
        # employee went unpaid while the run "balanced" (A09 probe M6).
        credits = float(sum(entry.amount_bdt for entry in entries))
        if currency.compare_amounts(credits, self.total_amount) != 0:
            raise UserError(
                "The BEFTN credits for %s total %.2f but the approved run totals %.2f - "
                "a payslip with a negative net pay cannot be left out silently."
                % (period.name, credits, self.total_amount)
            )

        batch_header = BeftnBatchHeader(
            company_name="1000FIX SERVICES LTD",
            company_id=company_account,
            originating_routing=company_routing,
            batch_number=self.id or 1,
            settlement_date=self.settlement_date or fields.Date.today(),
            description="SALARY " + (self.period_id.name or ""),
        )

        content = generate_beftn_batch_file(batch_header, entries)
        self._guarded().write(
            {
                "file_content": content,
                "file_name": f"BEFTN_{self.period_id.name or 'BATCH'}_{self.id}.txt",
            }
        )
        return content

    def action_settle(self):
        for rec in self:
            if fields.Date.today() < rec.settlement_date:
                raise UserError(
                    "BEFTN settles %s — before the settlement date the batch "
                    "cannot be marked settled" % rec.settlement_date
                )
            rec._guarded().write({"state": "settled"})
            publish(
                self.env,
                "payroll.beftn_settled",
                "fix.beftn.batch",
                rec.id,
                {"settlement": str(rec.settlement_date)},
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
