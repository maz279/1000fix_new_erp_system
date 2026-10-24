# fix_payroll — M56: period, payslips, BEFTN batch, GL posting (P08-M03).
from datetime import datetime, timedelta
from decimal import Decimal

from odoo import Command, api, fields, models
from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions
from odoo.exceptions import AccessError, UserError

from libs.py.fix_events import publish
from libs.py.payroll_engine import (
    BeftnBatchHeader,
    BeftnEntry,
    PayslipInput,
    beftn_settlement_date,
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


class FixPayrollPeriod(models.Model):
    """Journey 13's spine: lock -> calculate -> approve -> BEFTN -> payslips
    -> posting. Each transition is guarded; calculation REFUSED until the
    attendance lock exists (P08-M02-T05)."""

    _name = "fix.payroll.period"
    _description = "Payroll Period"
    _inherit = ["mail.thread", "mail.activity.mixin"]
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
            rec.state = "attendance_locked"
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
            rec.calculator_id = self.env.user
            rec.payslip_ids.unlink()
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

                tax_cat = getattr(contract, "taxpayer_category", False) or "general"
                tax_loc = getattr(contract, "tax_location", False) or "dhaka_chattogram"
                has_child = getattr(contract, "has_disabled_child", False)
                inv_allow = float(getattr(contract, "investment_allowance", 0.0) or 0.0)
                # Only REAL bank details are carried onto the payslip. A missing
                # account/routing number stays empty and blocks the BEFTN file
                # (R01 re-audit 2026-10-22: placeholders "1234567890123" /
                # "020260123" / "BRAC Bank PLC" used to be substituted, which
                # would have routed a salary to a fabricated account).
                # Odoo 19 replaced hr.employee.bank_account_id with
                # bank_account_ids / primary_bank_account_id (an HR-group
                # field, read with sudo for the payroll run): the old name
                # silently dropped every employee's registered salary account.
                primary_bank = emp.sudo().primary_bank_account_id
                bank_acc = getattr(contract, "bank_account_no", False) or primary_bank.acc_number
                routing = getattr(contract, "bank_routing_no", False)
                bank_n = getattr(contract, "bank_name", False) or primary_bank.bank_id.name

                self.env["fix.payslip"].create(
                    {
                        "period_id": rec.id,
                        "company_id": rec.company_id.id,
                        "employee_id": emp.id,
                        "basic": float(contract.basic_monthly),
                        "ot_hours": float(ot_hours),
                        "taxpayer_category": tax_cat,
                        "minimum_tax_location": tax_loc,
                        "has_disabled_child": has_child,
                        "investment_allowance": inv_allow,
                        "bank_account_no": bank_acc,
                        "routing_no": routing,
                        "bank_name": bank_n,
                    }
                )
            rec.state = "calculated"

    def action_approve(self):
        """SoD: approver must differ from the calculator (DoD-04) and hold
        the Payroll Manager role. There is no context bypass: the former
        ``bypass_payroll_sod`` context key let any caller (RPC included)
        self-approve."""
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
            rec.state = "approved"
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
            submitted = datetime.now()
            batch = self.env["fix.beftn.batch"].create(
                {
                    "period_id": rec.id,
                    "submitted_at": submitted,
                    "settlement_date": beftn_settlement_date(submitted),
                    "employee_count": rec.slip_count,
                    "total_amount": rec.net_total,
                    "company_account_no": rec.company_account_no,
                    "company_routing_no": rec.company_routing_no,
                }
            )
            batch.action_generate_beftn_file()
            rec.write({"state": "paid", "beftn_batch_id": batch.id})
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
            components = [  # (account field, label, debit, credit)
                (
                    "payroll_salary_expense_account_id",
                    "Basic salary",
                    sum(slips.mapped("basic")),
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
            rec.write({"gl_move_id": move.id, "state": "posted"})
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
    _inherit = ["mail.thread", "mail.activity.mixin"]

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
    ot_hours = fields.Float(string="Overtime Hours")
    incentive = fields.Monetary(
        string="Incentive (M57)",
        currency_field="currency_id",
        help="Applied by the M57 incentive engine " "before approval",
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
        "ot_hours",
        "incentive",
        "pf_employee_pct",
        "pf_employer_pct",
        "annual_taxable_other",
        "taxpayer_category",
        "has_disabled_child",
        "minimum_tax_location",
        "investment_allowance",
    )
    def _compute_slip(self):
        for rec in self:
            result = compute_payslip(
                PayslipInput(
                    employee_ref=rec.employee_id.name or "",
                    basic_monthly=Decimal(str(rec.basic)),
                    ot_hours=Decimal(str(rec.ot_hours)),
                    incentive=Decimal(str(rec.incentive)),
                    pf_employee_pct=Decimal(str(rec.pf_employee_pct)),
                    pf_employer_pct=Decimal(str(rec.pf_employer_pct)),
                    annual_taxable_other=Decimal(str(rec.annual_taxable_other)),
                    taxpayer_category=rec.taxpayer_category or "general",
                    disabled_dependents=1 if rec.has_disabled_child else 0,
                    tax_location=rec.minimum_tax_location or "dhaka_chattogram",
                    allowable_investment=Decimal(str(rec.investment_allowance or 0.0)),
                )
            )

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
        return float(comp)


class FixBeftnBatch(models.Model):
    """INT-005: batch settlement with the cut-off calendar and 128-byte file generation."""

    _name = "fix.beftn.batch"
    _description = "BEFTN Batch"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "submitted_at desc"

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
            lambda slip: not (slip.routing_no or "").strip()
            or not (slip.bank_account_no or "").strip()
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

        batch_header = BeftnBatchHeader(
            company_name="1000FIX SERVICES LTD",
            company_id=company_account,
            originating_routing=company_routing,
            batch_number=self.id or 1,
            settlement_date=self.settlement_date or fields.Date.today(),
            description="SALARY " + (self.period_id.name or ""),
        )

        content = generate_beftn_batch_file(batch_header, entries)
        self.write(
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
            rec.state = "settled"
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
