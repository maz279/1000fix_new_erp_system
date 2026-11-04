# fix_payroll_ops — M56: salary structures, festival bonus runs, tax
# certificates, quarterly withholding returns, off-cycle payments and WPPF.
# Periods, payslips and BEFTN batches live in fix_payroll.py.
#
# A09 workflow audit (2026-11-03), P0 A4: each document here was a set of
# plain-writable state flags. An officer created and approved his own
# BDT 5,000,000 off-cycle payment, then changed its amount and payee; wrote
# 'paid' directly; "trustee-approved" WPPF himself and rewrote the profit.
# Every document now carries fix.payroll.state.lock: state, the actor stamps
# and the computed amounts change only in a transition, and what was approved
# freezes.
#
# A09 P0-b / P1 / P2 (M56 build):
#   * off-cycle, festival bonus and WPPF approval is a routed M63 request
#     (C1): the preparer requests, a Payroll Manager who prepared nothing
#     decides from the inbox; the employee paid never decides their own;
#   * off-cycle and bonus payments are released by a Payroll Disbursement
#     Releaser (SOD-29), paid by a BEFTN file built from the payee and amount
#     pinned at approval, and posted to the GL (M56-7, M56-9);
#   * the festival bonus is computed per eligible employee: one year's
#     service, at most one month's basic, at most two a year (Labour Rules
#     2015 r.111(5)); it computed nothing before (probe B2);
#   * an awarded injury compensation (M59, hse.compensation.awarded) arrives
#     as a DRAFT off-cycle payment for its own approval (I5);
#   * the certificate counts the fiscal year's paid slips only; the return is
#     filed by a Payroll Manager with the challan and the NBR acknowledgement,
#     and a daily cron reminds payroll of returns falling due (M56-10).
from datetime import date, timedelta

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish
from libs.py.payroll_engine import beftn_settlement_date, completed_years

from .fix_payroll_disbursement import (
    PAYMENT_GL_ACCOUNTS,
    check_releaser,
    master_bank_details,
    payroll_gl_journal,
    post_two_line_entry,
)
from .fix_payroll_statutory import (
    FESTIVAL_BONUS_CAP_MONTHS,
    FESTIVAL_BONUS_SERVICE_YEARS,
    FESTIVAL_BONUSES_PER_YEAR,
    digest_rows,
    fiscal_year_bounds,
    q2,
)

PAYROLL_MANAGER = "cd_payroll_bd.group_payroll_manager"
PAYROLL_OFFICER = "cd_payroll_bd.group_payroll_officer"
# A paid run: what a certificate or a return reports (a calculated or approved
# run may still change or never be paid).
PAID_PERIOD_STATES = ("paid", "posted")


def routed_payroll_decision(records, what, makers):
    """The opening of every routed payroll approve method: from the inbox
    only, never by the requester, preparer or subject, and by a Payroll
    Manager who made none of it."""
    records._approval_assert_routed()
    records._people_assert_not_conflicted()
    if records.env.su:
        return
    decider = records._people_decider()
    if not decider.has_group(PAYROLL_MANAGER):
        raise AccessError("Only a Payroll Manager can approve %s." % what)
    for rec in records:
        if (rec._approval_acting_users() | decider) & makers(rec):
            raise UserError(
                "Maker-Checker SoD violation: %s %s was prepared or calculated by %s, who "
                "cannot also approve it." % (rec._description, rec.display_name, decider.name)
            )


def originating_account(company):
    """The company's originating account for off-cycle and bonus files."""
    return (company.payroll_beftn_account_no or "").strip(), (
        company.payroll_beftn_routing_no or ""
    ).strip()


def master_bank(employee):
    """(account, routing) registered on the employee master, read as payroll;
    no account when the master holds two conflicting ones."""
    account, routing, _bank, _problem = master_bank_details(employee)
    return account, routing


class FixPayrollStructure(models.Model):
    """A salary grade. Only a Payroll Manager changes one, and every change
    is tracked (A09 probe M7: an officer rewrote a grade with no trace)."""

    _name = "fix.payroll.structure"
    _description = "Salary Structure"
    _inherit = ["mail.thread"]
    _order = "grade"

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    grade = fields.Char(string="Grade / Band", tracking=True)
    basic_pct = fields.Float(string="Basic % of Gross", default=60.0, tracking=True)
    house_rent_pct = fields.Float(string="House Rent %", default=30.0, tracking=True)
    transport_fixed = fields.Monetary(
        currency_field="currency_id", string="Transport (fixed)", tracking=True
    )
    medical_fixed = fields.Monetary(
        currency_field="currency_id", string="Medical (fixed)", tracking=True
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    pf_applicable = fields.Boolean(string="Provident Fund Applicable", default=True, tracking=True)
    gratuity_applicable = fields.Boolean(string="Gratuity Applicable", default=True, tracking=True)
    active = fields.Boolean(default=True, tracking=True)

    _basic_house_range = models.Constraint(
        "CHECK (basic_pct >= 0 AND basic_pct <= 100 AND house_rent_pct >= 0 AND house_rent_pct <= 100)",
        "Structure percentages are 0-100",
    )


# ---------------------------------------------------------------- festival bonus


class FixFestivalBonusLine(models.Model):
    """One eligible employee's festival bonus, computed by the run."""

    _name = "fix.payroll.bonus.line"
    _description = "Festival Bonus Line"
    _inherit = ["fix.guarded.mixin"]
    _order = "run_id, employee_id"

    run_id = fields.Many2one(
        "fix.payroll.bonus.run", required=True, ondelete="cascade", index=True, readonly=True
    )
    company_id = fields.Many2one(related="run_id.company_id", store=True)
    employee_id = fields.Many2one("hr.employee", required=True, index=True, readonly=True)
    contract_id = fields.Many2one("fix.employment.contract", readonly=True)
    completed_years = fields.Integer(readonly=True)
    basic = fields.Monetary(currency_field="currency_id", readonly=True)
    base_amount = fields.Monetary(
        currency_field="currency_id", string="Basis Amount", readonly=True
    )
    amount = fields.Monetary(currency_field="currency_id", readonly=True)
    capped = fields.Boolean(string="Capped at Basic (r.111(5))", readonly=True)
    bank_account_no = fields.Char(readonly=True)
    routing_no = fields.Char(readonly=True)
    currency_id = fields.Many2one(related="run_id.currency_id")

    def _fix_guarded_fields(self) -> set:
        # a line is written by the run's compute step only
        return super()._fix_guarded_fields() | {
            "run_id",
            "employee_id",
            "contract_id",
            "completed_years",
            "basic",
            "base_amount",
            "amount",
            "capped",
            "bank_account_no",
            "routing_no",
        }

    def unlink(self):
        if not (self.env.su or self._fix_guard_has_token()):
            raise UserError("A festival bonus line is removed only by recomputing its run.")
        return super().unlink()


class FixFestivalBonusRun(models.Model):
    _name = "fix.payroll.bonus.run"
    _description = "Festival Bonus Run"
    _inherit = ["mail.thread", "fix.people.approval.mixin", "fix.payroll.state.lock"]
    _order = "bonus_date desc, id desc"

    _approval_domain = "hr_bonus"
    _approval_apply_method = "action_approve"
    _approval_group = PAYROLL_MANAGER

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    festival = fields.Selection(
        [
            ("eid_ul_fitr", "Eid-ul-Fitr"),
            ("eid_ul_adha", "Eid-ul-Adha"),
            ("durga_puja", "Durga Puja"),
            ("other", "Other"),
        ],
        required=True,
        default="eid_ul_fitr",
    )
    bonus_date = fields.Date(required=True, default=fields.Date.context_today)
    basis = fields.Selection(
        [("basic", "Basic Salary"), ("gross", "Gross Salary")],
        required=True,
        default="basic",
    )
    multiplier = fields.Float(string="Multiplier (months)", default=1.0)
    line_ids = fields.One2many("fix.payroll.bonus.line", "run_id", string="Bonus Lines")
    employee_count = fields.Integer(readonly=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    total_amount = fields.Monetary(currency_field="currency_id", readonly=True)
    computation_note = fields.Text(readonly=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("computed", "Computed"),
            ("approved", "Approved"),
            ("paid", "Paid"),
            ("posted", "Posted"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="draft",
    )
    prepared_by_id = fields.Many2one(
        "res.users", string="Prepared By", readonly=True, default=lambda self: self.env.user
    )
    computed_by_id = fields.Many2one("res.users", string="Computed By", readonly=True)
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True)
    approved_on = fields.Datetime(string="Approved On", readonly=True)
    approved_digest = fields.Char(readonly=True)
    released_by_id = fields.Many2one("res.users", string="Released By", readonly=True)
    released_on = fields.Datetime(string="Released On", readonly=True)
    beftn_batch_id = fields.Many2one("fix.beftn.batch", string="BEFTN Batch", readonly=True)
    gl_move_id = fields.Many2one("account.move", string="GL Entry", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "prepared_by_id",
            "computed_by_id",
            "approved_by_id",
            "approved_on",
            "approved_digest",
            "released_by_id",
            "released_on",
            "beftn_batch_id",
            "gl_move_id",
            "employee_count",
            "total_amount",
            "computation_note",
            "line_ids",
        }

    def _payroll_state_locked_fields(self) -> set:
        locked = super()._payroll_state_locked_fields()
        if self.state != "draft":
            locked |= {"festival", "bonus_date", "basis", "multiplier", "company_id"}
            locked |= {"operating_unit_id", "currency_id"}
        return locked

    @api.constrains("multiplier")
    def _check_multiplier(self):
        for rec in self:
            if rec.multiplier <= 0:
                raise ValidationError("A festival bonus multiplier must be positive.")

    @api.constrains("bonus_date", "company_id", "state")
    def _check_two_a_year(self):
        """Labour Rules 2015 r.111(5): two festival bonuses a year (probe B4)."""
        for rec in self.filtered(lambda r: r.state != "cancelled" and r.bonus_date):
            year = rec.bonus_date.year
            count = self.sudo().search_count(
                [
                    ("company_id", "=", rec.company_id.id),
                    ("state", "!=", "cancelled"),
                    ("bonus_date", ">=", date(year, 1, 1)),
                    ("bonus_date", "<=", date(year, 12, 31)),
                ]
            )
            if count > FESTIVAL_BONUSES_PER_YEAR:
                raise ValidationError(
                    "%s already has %d festival bonus runs in %d: a worker receives at most two "
                    "festival bonuses a year (Labour Rules 2015 r.111(5))."
                    % (rec.company_id.name, FESTIVAL_BONUSES_PER_YEAR, year)
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.payroll.bonus.run") or "BON/New"
                )
        return super().create(vals_list)

    # ---- routed approval ------------------------------------------------------
    def _approval_amount(self) -> float:
        return float(self.total_amount or 0.0)

    def _approval_subject_employees(self):
        # a run pays many people; its preparers are excluded below
        return self.env["hr.employee"]

    def _approval_preparers(self):
        return (self.prepared_by_id | self.computed_by_id | self.create_uid).sudo()

    def _lines_digest(self):
        self.ensure_one()
        return digest_rows(
            [
                (
                    line.id,
                    line.employee_id.id,
                    "%.2f" % line.amount,
                    (line.bank_account_no or "").strip(),
                    (line.routing_no or "").strip(),
                )
                for line in self.line_ids
            ]
        )

    def _refuse_while_pending(self, what):
        for rec in self:
            if rec.approval_state == "pending":
                raise UserError(
                    "Bonus run %s is awaiting approval: recall the request before you %s."
                    % (rec.name, what)
                )

    def action_compute(self):
        """One line per eligible employee: an active contract, at least one
        completed year of service on the bonus date, fewer than two festival
        bonuses already this year; the amount at most one month's basic."""
        for rec in self:
            if rec.state not in ("draft", "computed"):
                raise UserError("Compute a draft bonus run.")
            rec._refuse_while_pending("recompute it")
            contracts = self.env["fix.employment.contract"].search(
                [("company_id", "=", rec.company_id.id), ("state", "=", "active")],
                order="employee_id, joining_date",
            )
            by_emp = {}
            for contract in contracts:
                by_emp.setdefault(contract.employee_id, []).append(contract)
            year = rec.bonus_date.year
            already = {}
            others = (
                self.env["fix.payroll.bonus.line"]
                .sudo()
                .search(
                    [
                        ("run_id", "!=", rec.id),
                        ("run_id.company_id", "=", rec.company_id.id),
                        ("run_id.state", "in", ("approved", "paid", "posted")),
                        ("run_id.bonus_date", ">=", date(year, 1, 1)),
                        ("run_id.bonus_date", "<=", date(year, 12, 31)),
                        ("amount", ">", 0),
                    ]
                )
            )
            for line in others:
                already[line.employee_id.id] = already.get(line.employee_id.id, 0) + 1
            rec.line_ids._guarded().unlink()
            vals_list, skipped = [], []
            multiplier = q2(rec.multiplier)
            for emp, own in by_emp.items():
                if len(own) > 1:
                    skipped.append("%s: more than one active contract" % emp.name)
                    continue
                contract = own[0]
                joining = fields.Date.to_date(contract.joining_date)
                if joining > rec.bonus_date:
                    skipped.append("%s: joins after the bonus date" % emp.name)
                    continue
                years = completed_years(joining, rec.bonus_date)
                if years < FESTIVAL_BONUS_SERVICE_YEARS:
                    skipped.append("%s: less than one year of service" % emp.name)
                    continue
                if already.get(emp.id, 0) >= FESTIVAL_BONUSES_PER_YEAR:
                    skipped.append(
                        "%s: already received two festival bonuses in %d" % (emp.name, year)
                    )
                    continue
                basic = q2(contract.basic_monthly)
                base = basic
                if rec.basis == "gross":
                    base = q2(
                        sum(
                            (contract[f] or 0.0)
                            for f in (
                                "basic_monthly",
                                "house_rent",
                                "medical_allowance",
                                "conveyance_allowance",
                                "technical_allowance",
                                "other_allowance",
                                "dearness_allowance",
                                "adhoc_allowance",
                            )
                        )
                    )
                wanted = q2(base * multiplier)
                cap = q2(basic * FESTIVAL_BONUS_CAP_MONTHS)
                account, routing = master_bank(emp)
                vals_list.append(
                    {
                        "run_id": rec.id,
                        "employee_id": emp.id,
                        "contract_id": contract.id,
                        "completed_years": years,
                        "basic": float(basic),
                        "base_amount": float(base),
                        "amount": float(min(wanted, cap)),
                        "capped": wanted > cap,
                        "bank_account_no": account,
                        "routing_no": routing,
                    }
                )
            lines = self.env["fix.payroll.bonus.line"]._guarded().create(vals_list)
            note = "Eligible: %d. %s" % (
                len(lines),
                " ".join("Skipped %s." % s for s in skipped),
            )
            rec._guarded().write(
                {
                    "state": "computed",
                    "computed_by_id": self.env.user.id,
                    "employee_count": len(lines),
                    "total_amount": sum(lines.mapped("amount")),
                    "computation_note": note.strip(),
                }
            )

    def action_request_approval(self, justification=None):
        for rec in self:
            if rec.state != "computed" or not rec.line_ids:
                raise UserError(
                    "Compute the bonus run (with at least one eligible employee) first."
                )
            missing = rec.line_ids.filtered(
                lambda line: not line.bank_account_no or not line.routing_no
            )
            if missing:
                raise UserError(
                    "Bank details are missing for: %s."
                    % ", ".join(missing.mapped("employee_id.name"))
                )
        return super().action_request_approval(justification=justification)

    def action_approve(self):
        routed_payroll_decision(self, "a festival bonus run", lambda rec: rec._approval_preparers())
        for rec in self:
            if rec.state != "computed":
                raise UserError("Approve a computed bonus run")
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": rec._people_decider().id,
                    "approved_on": fields.Datetime.now(),
                    "approved_digest": rec._lines_digest(),
                }
            )

    def _beftn_entries(self):
        from .fix_payroll import beftn_entry

        self.ensure_one()
        if self.state != "approved" or self._lines_digest() != self.approved_digest:
            raise UserError(
                "Bonus run %s does not match its approval - nothing is paid from a changed run."
                % self.name
            )
        return [
            beftn_entry(line.employee_id, line.bank_account_no, line.routing_no, line.amount)
            for line in self.line_ids
            if line.amount > 0
        ]

    def action_pay(self):
        check_releaser(
            self,
            "a festival bonus run",
            lambda rec: (
                rec._approval_preparers()
                | rec.approved_by_id
                | rec.approval_request_id.sudo().requested_by_id
            ),
        )
        for rec in self:
            if rec.state != "approved":
                raise UserError("Pay an approved bonus run")
            account, routing = originating_account(rec.company_id)
            submitted = fields.Datetime.now()
            batch = (
                self.env["fix.beftn.batch"]
                ._guarded()
                .create(
                    {
                        "bonus_run_id": rec.id,
                        "company_id": rec.company_id.id,
                        "submitted_at": submitted,
                        "settlement_date": beftn_settlement_date(submitted),
                        "employee_count": rec.employee_count,
                        "total_amount": rec.total_amount,
                        "company_account_no": account,
                        "company_routing_no": routing,
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
                "payroll.bonus_paid",
                "fix.payroll.bonus.run",
                rec.id,
                {"run": rec.name, "total": float(rec.total_amount), "batch_id": batch.id},
            )

    def action_post(self):
        for rec in self:
            if rec.state != "paid" or rec.gl_move_id:
                raise UserError("Post a paid bonus run once.")
            payroll_gl_journal(rec.company_id, PAYMENT_GL_ACCOUNTS, rec.name)
            move = post_two_line_entry(
                self.env,
                rec.company_id,
                "Festival Bonus - %s" % rec.name,
                rec.bonus_date,
                rec.total_amount,
                "Festival bonus %s" % rec.name,
                "payroll_salary_expense_account_id",
                "payroll_net_payable_account_id",
                ou=rec.operating_unit_id,
            )
            rec._guarded().write({"state": "posted", "gl_move_id": move.id})

    def action_cancel(self):
        for rec in self:
            if rec.state not in ("draft", "computed"):
                raise UserError("Only a bonus run not yet approved can be cancelled.")
            rec._refuse_while_pending("cancel it")
            rec._guarded().write({"state": "cancelled"})


# ---------------------------------------------------------------- certificates and returns


class FixPayrollCertificate(models.Model):
    _name = "fix.payroll.certificate"
    _description = "Tax / Salary Certificate"
    _inherit = ["fix.payroll.state.lock"]
    _order = "fiscal_year desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)
    certificate_type = fields.Selection(
        [
            ("salary", "Salary Certificate"),
            ("tax", "Tax Deduction Certificate"),
            ("employment", "Employment Certificate"),
        ],
        required=True,
        default="salary",
    )
    fiscal_year = fields.Char(required=True)
    # stamped by action_issue: a draft certificate has not been issued
    issued_on = fields.Date(readonly=True)
    issued_by_id = fields.Many2one("res.users", string="Issued By", readonly=True)
    amount = fields.Monetary(currency_field="currency_id", string="Annual Figure")
    total_gross = fields.Monetary(currency_field="currency_id", string="Total Gross Salary")
    total_basic = fields.Monetary(currency_field="currency_id", string="Total Basic Salary")
    total_allowances = fields.Monetary(currency_field="currency_id", string="Total Allowances")
    total_tax_withheld = fields.Monetary(
        currency_field="currency_id", string="Total Income Tax Withheld (TDS)"
    )
    total_pf_deducted = fields.Monetary(
        currency_field="currency_id", string="Total Provident Fund Contributed"
    )
    slip_count = fields.Integer(string="Payslips Counted", readonly=True)
    challan_refs = fields.Char(string="Treasury Challan References")
    state = fields.Selection(
        [("draft", "Draft"), ("issued", "Issued")],
        default="draft",
        required=True,
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    reference = fields.Char()

    def _fix_guarded_fields(self) -> set:
        # the figures come from the payslips, never typed (A09 probe T4: a
        # certificate was issued with a typed gross of 9,999,999)
        return super()._fix_guarded_fields() | {
            "state",
            "issued_on",
            "issued_by_id",
            "amount",
            "total_gross",
            "total_basic",
            "total_allowances",
            "total_tax_withheld",
            "total_pf_deducted",
            "slip_count",
        }

    def _payroll_state_locked_fields(self) -> set:
        locked = super()._payroll_state_locked_fields()
        if self.state == "issued":
            locked |= {"employee_id", "certificate_type", "fiscal_year", "company_id"}
            locked |= {"currency_id", "challan_refs", "reference"}
        return locked

    @api.constrains("fiscal_year")
    def _check_fiscal_year(self):
        for rec in self:
            fiscal_year_bounds(rec.fiscal_year)

    def action_compute_from_payslips(self):
        """The fiscal year's PAID payslips of the employee (ITA 2023 s.108/114
        certificate): 1 July to 30 June, never every slip ever (probe T1)."""
        for rec in self:
            if rec.state == "issued":
                raise UserError("Certificate %s is issued - its figures are final." % rec.name)
            start, end = fiscal_year_bounds(rec.fiscal_year)
            slips = self.env["fix.payslip"].search(
                [
                    ("employee_id", "=", rec.employee_id.id),
                    ("company_id", "=", rec.company_id.id),
                    ("period_id.state", "in", PAID_PERIOD_STATES),
                    ("period_id.period_start", ">=", start),
                    ("period_id.period_start", "<=", end),
                ]
            )
            gross = sum(slips.mapped("gross"))
            # the payslip's withheld tax (it read a non-existent `income_tax`
            # and crashed, A09 probe T1)
            tax = sum(slips.mapped("tax_withheld"))
            rec._guarded().write(
                {
                    "total_gross": gross,
                    "total_basic": sum(slips.mapped("basic")),
                    "total_allowances": sum(slips.mapped("allowances_total")),
                    "total_tax_withheld": tax,
                    "total_pf_deducted": sum(slips.mapped("pf_employee")),
                    "amount": tax if rec.certificate_type == "tax" else gross,
                    "slip_count": len(slips),
                }
            )

    def action_issue(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Issue a draft certificate")
            # always from the payslips at the moment of issue
            rec.action_compute_from_payslips()
            if rec.certificate_type in ("salary", "tax") and not rec.slip_count:
                raise UserError(
                    "Certificate %s covers no paid payslip of %s in fiscal year %s."
                    % (rec.name, rec.employee_id.name, rec.fiscal_year)
                )
            rec._guarded().write(
                {
                    "state": "issued",
                    "issued_on": fields.Date.context_today(self),
                    "issued_by_id": self.env.user.id,
                }
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.payroll.certificate") or "CERT/New"
                )
        return super().create(vals_list)


class FixWithholdingReturn(models.Model):
    _name = "fix.payroll.return"
    _description = "Quarterly Withholding Return"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.payroll.state.lock"]
    _order = "period desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    period = fields.Char(required=True, help="Quarter, e.g. Q1-2026")
    period_start = fields.Date(string="Period Start")
    period_end = fields.Date(string="Period End")
    due_date = fields.Date(
        string="Due Date",
        compute="_compute_due_date",
        store=True,
        help="The company's due day of the month after the period end (spec BRU-PAY-16).",
    )
    challan_number = fields.Char(string="Treasury Challan No")
    challan_date = fields.Date(string="Treasury Challan Date")
    tax_zone = fields.Char(string="NBR Tax Zone / Circle")
    employee_count = fields.Integer()
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    total_tax = fields.Monetary(currency_field="currency_id", string="Tax Withheld")
    filed_on = fields.Date(readonly=True)
    filed_by_id = fields.Many2one("res.users", string="Filed By", readonly=True)
    acknowledgement = fields.Char(string="NBR Acknowledgement")
    state = fields.Selection(
        [("draft", "Draft"), ("filed", "Filed")], required=True, default="draft"
    )

    def _fix_guarded_fields(self) -> set:
        # the totals come from the payslips (action_reconcile_payslips)
        return super()._fix_guarded_fields() | {
            "state",
            "filed_on",
            "filed_by_id",
            "employee_count",
            "total_tax",
        }

    def _payroll_state_locked_fields(self) -> set:
        locked = super()._payroll_state_locked_fields()
        if self.state == "filed":
            locked |= {"period", "period_start", "period_end", "challan_number"}
            locked |= {"challan_date", "tax_zone", "acknowledgement", "company_id"}
        return locked

    @api.depends("period_end", "company_id.payroll_return_due_day")
    def _compute_due_date(self):
        for rec in self:
            if not rec.period_end:
                rec.due_date = False
                continue
            nxt = fields.Date.to_date(rec.period_end) + relativedelta(months=1)
            day = min(max(rec.company_id.payroll_return_due_day or 25, 1), 28)
            rec.due_date = nxt.replace(day=day)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.payroll.return") or "PWR/New"
                )
        return super().create(vals_list)

    def action_reconcile_payslips(self):
        """The period's PAID payslip TDS (withholding return reconciliation)."""
        for rec in self:
            if rec.state == "filed":
                raise UserError("Return %s is filed - its totals are final." % rec.name)
            if not rec.period_start or not rec.period_end:
                raise UserError("Enter the return period's start and end before reconciling.")
            # `tax_withheld` is the payslip's field (`income_tax` crashed, A09 T2)
            slips = self.env["fix.payslip"].search(
                [
                    ("company_id", "=", rec.company_id.id),
                    ("tax_withheld", ">", 0),
                    ("period_id.state", "in", PAID_PERIOD_STATES),
                    ("period_id.period_start", ">=", rec.period_start),
                    ("period_id.period_end", "<=", rec.period_end),
                ]
            )
            rec._guarded().write(
                {
                    "employee_count": len(slips.mapped("employee_id")),
                    "total_tax": sum(slips.mapped("tax_withheld")),
                }
            )

    def action_file(self):
        """Filed by a Payroll Manager, with the treasury challan and the NBR
        acknowledgement, on totals reconciled at the moment of filing (probe
        T3 filed a typed 1 BDT with neither)."""
        if not (self.env.su or self.env.user.has_group(PAYROLL_MANAGER)):
            raise AccessError("Only a Payroll Manager files a withholding return.")
        for rec in self:
            if rec.state != "draft":
                raise UserError("File a draft return")
            missing = [
                label
                for field, label in (
                    ("challan_number", "treasury challan number"),
                    ("challan_date", "challan date"),
                    ("acknowledgement", "NBR acknowledgement"),
                )
                if not rec[field]
            ]
            if missing:
                raise UserError(
                    "Return %s cannot be filed without the %s." % (rec.name, ", ".join(missing))
                )
            rec.action_reconcile_payslips()
            rec._guarded().write(
                {
                    "state": "filed",
                    "filed_on": fields.Date.context_today(self),
                    "filed_by_id": self.env.user.id,
                }
            )

    @api.model
    def cron_return_due_alerts(self):
        """AUT-PAY-11: a to-do for payroll on every draft return due within
        14 days, again within 7; once per threshold (idempotent)."""
        today = fields.Date.context_today(self)
        returns = self.sudo().search(
            [
                ("state", "=", "draft"),
                ("due_date", "!=", False),
                ("due_date", "<=", today + timedelta(days=14)),
            ]
        )
        managers = (
            self.env.ref(PAYROLL_MANAGER)
            .sudo()
            .all_user_ids.filtered(lambda u: u.active and not u.share)
        )
        made = 0
        for rec in returns:
            window = 7 if rec.due_date <= today + timedelta(days=7) else 14
            summary = "Withholding return %s due %s (%d-day reminder)" % (
                rec.name,
                rec.due_date,
                window,
            )
            if rec.activity_ids.filtered(lambda a, s=summary: a.summary == s):
                continue
            user = managers.filtered(lambda u, r=rec: r.company_id in u.company_ids)[:1]
            rec.activity_schedule(
                "mail.mail_activity_data_todo",
                date_deadline=rec.due_date,
                summary=summary,
                user_id=(user or self.env.ref("base.user_admin")).id,
            )
            made += 1
        return made


# ---------------------------------------------------------------- off-cycle


class FixOffcyclePayment(models.Model):
    _name = "fix.payroll.offcycle"
    _description = "Off-Cycle Payment"
    _inherit = ["mail.thread", "fix.people.approval.mixin", "fix.payroll.state.lock"]
    _order = "payment_date desc, id desc"

    _approval_domain = "hr_offcycle"
    _approval_apply_method = "action_approve"
    _approval_group = PAYROLL_MANAGER

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)
    payment_type = fields.Selection(
        [
            ("advance", "Salary Advance"),
            ("arrear", "Arrear"),
            ("adjustment", "Adjustment"),
            ("settlement", "Final Settlement Part"),
            ("compensation", "Injury Compensation (BLA Ch. XII)"),
            ("recognition", "Recognition Prize (M57)"),
        ],
        required=True,
        default="arrear",
    )
    payment_date = fields.Date(required=True, default=fields.Date.context_today)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(currency_field="currency_id", required=True)
    reason = fields.Char()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("approved", "Approved"),
            ("paid", "Paid"),
            ("posted", "Posted"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="draft",
    )
    prepared_by_id = fields.Many2one(
        "res.users", string="Prepared By", readonly=True, default=lambda self: self.env.user
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True)
    approved_on = fields.Datetime(string="Approved On", readonly=True)
    # The payee's account, taken from the employee master when approval is
    # requested and pinned with the amount at approval (M56-7, probe O4).
    bank_account_no = fields.Char(string="Payee Account", readonly=True)
    routing_no = fields.Char(string="Payee Routing No", readonly=True)
    approved_digest = fields.Char(readonly=True)
    released_by_id = fields.Many2one("res.users", string="Released By", readonly=True)
    released_on = fields.Datetime(string="Released On", readonly=True)
    beftn_batch_id = fields.Many2one("fix.beftn.batch", string="BEFTN Batch", readonly=True)
    gl_move_id = fields.Many2one("account.move", string="GL Entry", readonly=True)
    # Where the payment came from, when it was not typed: a settled exit (I1),
    # an awarded injury compensation (I5) or an awarded recognition prize
    # (M57). Its amount and payee are then the source's, never the preparer's.
    exit_id = fields.Many2one("fix.hr.exit", string="Exit Settlement", readonly=True)
    source_event_id = fields.Char(string="Source Event", readonly=True, index=True, copy=False)
    hse_incident_ref = fields.Integer(string="HSE Incident ID", readonly=True)
    recognition_ref = fields.Integer(string="Recognition ID", readonly=True)

    _source_event_unique = models.Constraint(
        "UNIQUE (source_event_id)", "An event creates one off-cycle payment."
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "prepared_by_id",
            "approved_by_id",
            "approved_on",
            "bank_account_no",
            "routing_no",
            "approved_digest",
            "released_by_id",
            "released_on",
            "beftn_batch_id",
            "gl_move_id",
            "exit_id",
            "source_event_id",
            "hse_incident_ref",
            "recognition_ref",
        }

    def _payroll_state_locked_fields(self) -> set:
        # what was approved is what is paid: amount AND payee (A09 probe O4)
        locked = super()._payroll_state_locked_fields()
        if self.state != "draft":
            locked |= {"employee_id", "amount", "currency_id", "payment_type"}
            locked |= {"payment_date", "company_id"}
        if self.exit_id or self.source_event_id:
            locked |= {"employee_id", "amount", "currency_id", "payment_type", "company_id"}
        return locked

    @api.constrains("amount")
    def _check_amount(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError("An off-cycle payment is a positive amount.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.payroll.offcycle") or "OFC/New"
                )
        return super().create(vals_list)

    # ---- routed approval ------------------------------------------------------
    def _approval_amount(self) -> float:
        return float(self.amount or 0.0)

    def _approval_preparers(self):
        return (self.prepared_by_id | self.create_uid).sudo()

    def _payee_digest(self):
        self.ensure_one()
        return digest_rows(
            [
                (
                    self.id,
                    self.employee_id.id,
                    "%.2f" % self.amount,
                    (self.bank_account_no or "").strip(),
                    (self.routing_no or "").strip(),
                )
            ]
        )

    def _check_source_amount(self):
        """A settlement pays the exit's computed net (I1), nothing else."""
        for rec in self.filtered("exit_id"):
            net = rec.exit_id.sudo()._fix_settlement_breakdown()["net"]
            if rec.currency_id.compare_amounts(rec.amount, net) != 0:
                raise UserError(
                    "Settlement payment %s is %.2f but payroll computes %.2f for exit %s."
                    % (rec.name, rec.amount, net, rec.exit_id.display_name)
                )

    def action_request_approval(self, justification=None):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft off-cycle payment is sent for approval.")
            account, routing = master_bank(rec.employee_id)
            if not account or not routing:
                raise UserError(
                    "%s has no registered salary account and routing number: an off-cycle "
                    "payment is never sent to an assumed account." % rec.employee_id.name
                )
            rec._check_source_amount()
            rec._guarded().write({"bank_account_no": account, "routing_no": routing})
        return super().action_request_approval(justification=justification)

    def action_approve(self):
        routed_payroll_decision(self, "an off-cycle payment", lambda rec: rec._approval_preparers())
        for rec in self:
            if rec.state != "draft":
                raise UserError("Approve a draft off-cycle payment")
            # the payee the approver saw is still the payee on the master
            if master_bank(rec.employee_id) != (rec.bank_account_no, rec.routing_no):
                raise UserError(
                    "%s's bank details changed after approval was requested - request it again."
                    % rec.employee_id.name
                )
            rec._check_source_amount()
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": rec._people_decider().id,
                    "approved_on": fields.Datetime.now(),
                    "approved_digest": rec._payee_digest(),
                }
            )

    def _approval_on_rejected(self, comment):
        for rec in self:
            rec.message_post(body="Off-cycle payment rejected: %s" % (comment or ""))

    def _beftn_entries(self):
        from .fix_payroll import beftn_entry

        self.ensure_one()
        if self.state != "approved" or self._payee_digest() != self.approved_digest:
            raise UserError(
                "Off-cycle payment %s does not match its approval - nothing is paid from a "
                "changed payment." % self.name
            )
        return [beftn_entry(self.employee_id, self.bank_account_no, self.routing_no, self.amount)]

    def action_pay(self):
        """Released to the bank by a releaser who neither prepared nor
        approved it; the file pays the pinned payee the pinned amount."""
        check_releaser(
            self,
            "an off-cycle payment",
            lambda rec: (
                rec._approval_preparers()
                | rec.approved_by_id
                | rec.approval_request_id.sudo().requested_by_id
            ),
        )
        for rec in self:
            if rec.state != "approved":
                raise UserError("Pay an approved off-cycle payment")
            account, routing = originating_account(rec.company_id)
            submitted = fields.Datetime.now()
            batch = (
                self.env["fix.beftn.batch"]
                ._guarded()
                .create(
                    {
                        "offcycle_id": rec.id,
                        "company_id": rec.company_id.id,
                        "submitted_at": submitted,
                        "settlement_date": beftn_settlement_date(submitted),
                        "employee_count": 1,
                        "total_amount": rec.amount,
                        "company_account_no": account,
                        "company_routing_no": routing,
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
                "payroll.offcycle_paid",
                "fix.payroll.offcycle",
                rec.id,
                {
                    "employee_id": rec.employee_id.id,
                    "amount": float(rec.amount),
                    "payment_type": rec.payment_type,
                    "batch_id": batch.id,
                },
            )

    def action_post(self):
        for rec in self:
            if rec.state != "paid" or rec.gl_move_id:
                raise UserError("Post a paid off-cycle payment once.")
            payroll_gl_journal(rec.company_id, PAYMENT_GL_ACCOUNTS, rec.name)
            move = post_two_line_entry(
                self.env,
                rec.company_id,
                "Off-Cycle Payment - %s" % rec.name,
                rec.payment_date,
                rec.amount,
                "%s %s"
                % (dict(self._fields["payment_type"].selection)[rec.payment_type], rec.name),
                "payroll_salary_expense_account_id",
                "payroll_net_payable_account_id",
            )
            rec._guarded().write({"state": "posted", "gl_move_id": move.id})

    def action_cancel(self):
        for rec in self:
            if rec.state not in ("draft", "approved"):
                raise UserError("A paid off-cycle payment is not cancelled.")
            if rec.approval_state == "pending":
                raise UserError("Recall the approval request before cancelling %s." % rec.name)
            if rec.state == "approved" and not (
                self.env.su or self.env.user.has_group(PAYROLL_MANAGER)
            ):
                raise AccessError("Only a Payroll Manager cancels an approved payment.")
            rec._guarded().write({"state": "cancelled"})

    # ---- I5: injury compensation from M59 ------------------------------------
    @api.model
    def consume_compensation_awarded(self, event):
        """hse.compensation.awarded {employee_id, amount, incident_id, reason}
        -> one DRAFT off-cycle compensation payment (idempotent per event and
        per incident). Its own routed approval then decides it."""
        payload = event.get("payload") or {}
        employee = self.env["hr.employee"].browse(int(payload.get("employee_id") or 0)).exists()
        if not employee:
            raise UserError("hse.compensation.awarded names no existing employee: %s" % payload)
        amount = float(payload.get("amount") or 0.0)
        if amount <= 0:
            raise UserError("hse.compensation.awarded carries no positive amount: %s" % payload)
        source = event.get("event_id") or False
        incident = int(payload.get("incident_id") or 0)
        Offcycle = self.sudo().with_context(active_test=False)
        existing = Offcycle.search([("source_event_id", "=", source)], limit=1) if source else None
        if not existing and incident:
            existing = Offcycle.search(
                [
                    ("payment_type", "=", "compensation"),
                    ("hse_incident_ref", "=", incident),
                    ("employee_id", "=", employee.id),
                    ("state", "!=", "cancelled"),
                ],
                limit=1,
            )
        if existing:
            return existing
        return Offcycle._guarded().create(
            {
                "employee_id": employee.id,
                "company_id": employee.company_id.id,
                "payment_type": "compensation",
                "amount": amount,
                "reason": (payload.get("reason") or "Injury compensation (M59)")[:250],
                "source_event_id": source,
                "hse_incident_ref": incident,
            }
        )

    # ---- M57: a recognition prize --------------------------------------------
    @api.model
    def consume_recognition_awarded(self, event):
        """recognition.awarded {employee_id, amount, recognition_id, reason}
        -> one DRAFT off-cycle prize payment (idempotent per event and per
        recognition), so the prize is paid and taxed as salary income through
        payroll and decided by its own routed approval. An award without a
        prize pays nothing."""
        payload = event.get("payload") or {}
        amount = float(payload.get("amount") or 0.0)
        if amount <= 0:
            return False
        employee = self.env["hr.employee"].browse(int(payload.get("employee_id") or 0)).exists()
        if not employee:
            raise UserError("recognition.awarded names no existing employee: %s" % payload)
        source = event.get("event_id") or False
        recognition = int(payload.get("recognition_id") or 0)
        Offcycle = self.sudo().with_context(active_test=False)
        existing = Offcycle.search([("source_event_id", "=", source)], limit=1) if source else None
        if not existing and recognition:
            existing = Offcycle.search(
                [
                    ("payment_type", "=", "recognition"),
                    ("recognition_ref", "=", recognition),
                    ("state", "!=", "cancelled"),
                ],
                limit=1,
            )
        if existing:
            return existing
        return Offcycle._guarded().create(
            {
                "employee_id": employee.id,
                "company_id": employee.company_id.id,
                "payment_type": "recognition",
                "amount": amount,
                "reason": (payload.get("reason") or "Recognition prize (M57)")[:250],
                "source_event_id": source,
                "recognition_ref": recognition,
            }
        )


# ---------------------------------------------------------------- WPPF


class FixWppfAllocation(models.Model):
    """BLA 2006 Chapter XV (Sections 232-252): Workers' Profit Participation Fund (WPPF).

    Statutory 5% of net profit allocated 80:10:10 across:
    - 80% Participatory Fund (2/3 distributed equally, 1/3 invested per s.242)
    - 10% Welfare Fund
    - 10% Bangladesh Workers Welfare Foundation Fund (BWWF Act 2006)
    """

    _name = "fix.wppf.allocation"
    _description = "WPPF 5% Profit Participation Allocation (BLA Ch. XV)"
    _inherit = ["mail.thread", "fix.people.approval.mixin", "fix.payroll.state.lock"]
    _order = "fiscal_year desc, id desc"

    _approval_domain = "hr_wppf"
    _approval_apply_method = "action_approve"
    _approval_group = PAYROLL_MANAGER

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    fiscal_year = fields.Char(required=True, string="Fiscal Year", help="e.g. 2025-2026")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    net_profit = fields.Monetary(
        currency_field="currency_id", required=True, string="Audited Net Profit (BLA s.234)"
    )
    total_wppf_pool = fields.Monetary(
        currency_field="currency_id",
        compute="_compute_wppf_split",
        store=True,
        string="Total 5% WPPF Pool",
    )
    participatory_fund_amount = fields.Monetary(
        currency_field="currency_id",
        compute="_compute_wppf_split",
        store=True,
        string="Participatory Fund (80%)",
    )
    welfare_fund_amount = fields.Monetary(
        currency_field="currency_id",
        compute="_compute_wppf_split",
        store=True,
        string="Welfare Fund (10%)",
    )
    welfare_foundation_amount = fields.Monetary(
        currency_field="currency_id",
        compute="_compute_wppf_split",
        store=True,
        string="BWWF Government Foundation (10%)",
    )
    equal_distribution_pool = fields.Monetary(
        currency_field="currency_id",
        compute="_compute_wppf_split",
        store=True,
        string="2/3 Cash Distribution Pool (BLA s.242)",
    )
    investment_pool_share = fields.Monetary(
        currency_field="currency_id",
        compute="_compute_wppf_split",
        store=True,
        string="1/3 Investment Unit Pool (BLA s.242)",
    )
    eligible_workers_count = fields.Integer(
        string="Eligible Beneficiaries Count (BLA s.240)", default=0
    )
    per_worker_equal_share = fields.Monetary(
        currency_field="currency_id",
        compute="_compute_wppf_split",
        store=True,
        string="Equal Per-Worker Cash Share",
    )
    fiscal_year_end_date = fields.Date(string="Fiscal Year Close Date")
    distribution_due_date = fields.Date(
        string="Statutory Transfer Deadline (9 Months, s.234)",
        compute="_compute_wppf_split",
        store=True,
    )
    bwwf_challan_ref = fields.Char(string="BWWF 10% Deposit Challan Ref")
    trustee_board_resolution_ref = fields.Char(string="Board of Trustees Resolution Ref")
    # P8: the resolution is evidence, not a typed reference (probe W2)
    trustee_resolution_file = fields.Binary(string="Trustee Resolution (signed)", attachment=True)
    trustee_resolution_filename = fields.Char(string="Trustee Resolution File Name")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("calculated", "Calculated"),
            ("approved", "Trustee Approved"),
            ("posted", "Distributed & Posted"),
        ],
        default="draft",
        required=True,
    )
    prepared_by_id = fields.Many2one(
        "res.users", string="Prepared By", readonly=True, default=lambda self: self.env.user
    )
    calculated_by_id = fields.Many2one("res.users", string="Calculated By", readonly=True)
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True)
    approved_on = fields.Datetime(string="Approved On", readonly=True)
    gl_move_id = fields.Many2one("account.move", string="GL Entry", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "prepared_by_id",
            "calculated_by_id",
            "approved_by_id",
            "approved_on",
            "gl_move_id",
            "total_wppf_pool",
            "participatory_fund_amount",
            "welfare_fund_amount",
            "welfare_foundation_amount",
            "equal_distribution_pool",
            "investment_pool_share",
            "per_worker_equal_share",
            "distribution_due_date",
        }

    def _payroll_state_locked_fields(self) -> set:
        # the profit and headcount the pool was calculated from freeze with
        # the calculation (A09 probe W4); the trustee resolution with approval
        locked = super()._payroll_state_locked_fields()
        if self.state != "draft":
            locked |= {"net_profit", "eligible_workers_count", "fiscal_year"}
            locked |= {"fiscal_year_end_date", "company_id", "currency_id"}
        if self.state in ("approved", "posted"):
            locked |= {
                "trustee_board_resolution_ref",
                "trustee_resolution_file",
                "trustee_resolution_filename",
            }
        if self.state == "posted":
            locked |= {"bwwf_challan_ref"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.wppf.allocation")
                    or f"WPPF/{vals.get('fiscal_year') or 'New'}"
                )
        return super().create(vals_list)

    @api.depends("net_profit", "eligible_workers_count", "fiscal_year_end_date")
    def _compute_wppf_split(self):
        for rec in self:
            profit = max(float(rec.net_profit or 0.0), 0.0)
            pool = round(profit * 0.05, 2)
            part = round(pool * 0.80, 2)
            welfare = round(pool * 0.10, 2)
            foundation = round(pool - part - welfare, 2)
            cash_pool = round(part * (2.0 / 3.0), 2)
            inv_pool = round(part - cash_pool, 2)
            cnt = int(rec.eligible_workers_count or 0)
            per_worker = round(cash_pool / cnt, 2) if cnt > 0 else 0.0
            rec.total_wppf_pool = pool
            rec.participatory_fund_amount = part
            rec.welfare_fund_amount = welfare
            rec.welfare_foundation_amount = foundation
            rec.equal_distribution_pool = cash_pool
            rec.investment_pool_share = inv_pool
            rec.per_worker_equal_share = per_worker
            if rec.fiscal_year_end_date:
                rec.distribution_due_date = fields.Date.to_date(
                    rec.fiscal_year_end_date
                ) + timedelta(days=270)
            else:
                rec.distribution_due_date = False

    # ---- routed approval ------------------------------------------------------
    def _approval_amount(self) -> float:
        return float(self.total_wppf_pool or 0.0)

    def _approval_subject_employees(self):
        return self.env["hr.employee"]

    def _approval_preparers(self):
        return (self.prepared_by_id | self.calculated_by_id | self.create_uid).sudo()

    def action_calculate(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Calculate a draft WPPF allocation.")
            if rec.net_profit <= 0:
                raise UserError("Net profit must be positive to compute WPPF 5% allocation.")
            rec = rec._guarded()
            if not rec.eligible_workers_count:
                cnt = self.env["hr.employee"].search_count(
                    [("company_id", "=", rec.company_id.id), ("active", "=", True)]
                )
                rec.write({"eligible_workers_count": max(cnt, 1)})
            rec._compute_wppf_split()
            rec.write({"state": "calculated", "calculated_by_id": self.env.user.id})

    def action_request_approval(self, justification=None):
        for rec in self:
            if rec.state != "calculated":
                raise UserError("Calculate WPPF allocation before Trustee Board approval.")
            if not rec.trustee_board_resolution_ref or not rec.trustee_resolution_file:
                raise UserError(
                    "Attach the signed Board of Trustees resolution (reference and file) before "
                    "requesting WPPF approval."
                )
        return super().action_request_approval(justification=justification)

    def action_approve(self):
        routed_payroll_decision(self, "a WPPF allocation", lambda rec: rec._approval_preparers())
        for rec in self:
            if rec.state != "calculated":
                raise UserError("Calculate WPPF allocation before Trustee Board approval.")
            if not rec.trustee_board_resolution_ref or not rec.trustee_resolution_file:
                raise UserError(
                    "Board of Trustees resolution reference is required to approve WPPF allocation."
                )
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": rec._people_decider().id,
                    "approved_on": fields.Datetime.now(),
                }
            )

    def action_post(self):
        """Distribution posted: Dr WPPF expense / Cr WPPF payable for the 5%
        pool, on the company's WPPF accounts (probe W3: 'posted' made no entry)."""
        accounts = [
            ("payroll_wppf_expense_account_id", "WPPF Expense"),
            ("payroll_wppf_payable_account_id", "WPPF Payable"),
        ]
        for rec in self:
            if rec.state != "approved":
                raise UserError("Approve WPPF allocation before posting distribution.")
            if not rec.bwwf_challan_ref:
                raise UserError(
                    "BWWF 10% Government Welfare Foundation deposit challan reference is required before posting."
                )
            payroll_gl_journal(rec.company_id, accounts, rec.name)
            move = post_two_line_entry(
                self.env,
                rec.company_id,
                "WPPF Allocation - %s" % rec.name,
                rec.fiscal_year_end_date or fields.Date.context_today(self),
                rec.total_wppf_pool,
                "WPPF 5%% pool %s" % rec.fiscal_year,
                "payroll_wppf_expense_account_id",
                "payroll_wppf_payable_account_id",
            )
            rec._guarded().write({"state": "posted", "gl_move_id": move.id})
