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
import re
from datetime import date, timedelta
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from odoo import Command, api, fields, models
from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish
from libs.py.payroll_engine import beftn_settlement_date, completed_years

from .fix_payroll_disbursement import (
    PAYMENT_GL_ACCOUNTS,
    check_releaser,
    master_bank_details,
    master_payment_channel,
    payroll_gl_journal,
    post_two_line_entry,
)
from .fix_payroll_statutory import (
    FESTIVAL_BONUS_CAP_MONTHS,
    FESTIVAL_BONUS_SERVICE_YEARS,
    FESTIVAL_BONUSES_PER_YEAR,
    digest_rows,
    fiscal_year_bounds,
    marginal_rate,
    q2,
)

PAYROLL_MANAGER = "cd_payroll_bd.group_payroll_manager"
PAYROLL_OFFICER = "cd_payroll_bd.group_payroll_officer"
# Off-cycle types an overpayment recovery never reduces: a final settlement
# (incl. a death-in-service nominee's share) and an injury compensation are
# fixed by law or by an award.
RECOVERY_EXEMPT_TYPES = ("settlement", "compensation")
# An 11-digit Bangladesh mobile wallet (cd_hr_core's MFS format).
MFS_WALLET_RE = re.compile(r"^01[3-9]\d{8}$")
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
    # A09 round 2 (bonus TDS decision): withheld at the employee's payslip
    # marginal rate once the company turns it on; nothing withheld today
    marginal_rate = fields.Float(string="Marginal Tax Rate", readonly=True, digits=(4, 2))
    tax_withheld = fields.Monetary(currency_field="currency_id", readonly=True)
    net_amount = fields.Monetary(currency_field="currency_id", string="Net Paid", readonly=True)
    # an approved overpayment recovery taken from the bonus (company setting
    # payroll_recovery_source = any_payment); net_amount is after it
    recovery_deduction = fields.Monetary(
        currency_field="currency_id", string="Overpayment Recovery", readonly=True
    )
    # A09 round 2: how it is paid - the bank, or (an employee with no bank
    # account) the MFS wallet on the master, exactly as the monthly run
    payment_channel = fields.Selection(
        [("bank", "Bank (BEFTN)"), ("mfs", "MFS Wallet")], default="bank", readonly=True
    )
    mfs_provider = fields.Selection(
        lambda self: self.env["hr.employee"]._fields["mfs_provider"].selection, readonly=True
    )
    mfs_wallet = fields.Char(readonly=True)
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
            "marginal_rate",
            "tax_withheld",
            "net_amount",
            "recovery_deduction",
            "payment_channel",
            "mfs_provider",
            "mfs_wallet",
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
    total_tax = fields.Monetary(currency_field="currency_id", readonly=True, string="Tax Withheld")
    total_net = fields.Monetary(currency_field="currency_id", readonly=True, string="Net Paid")
    total_recovery = fields.Monetary(
        currency_field="currency_id", readonly=True, string="Overpayments Recovered"
    )
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
            "total_tax",
            "total_net",
            "total_recovery",
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

    def _rate_slip(self, employee):
        """The employee's latest committed payslip of this company, whose
        marginal rate a festival bonus is withheld at."""
        return (
            self.env["fix.payslip"]
            .sudo()
            .search(
                [
                    ("employee_id", "=", employee.id),
                    ("company_id", "=", self.company_id.id),
                    ("period_id.state", "in", ("approved", "paid", "posted")),
                    ("period_id.period_start", "<=", self.bonus_date),
                ],
                order="id desc",
                limit=1,
            )
        )

    def _lines_digest(self):
        self.ensure_one()
        return digest_rows(
            [
                (
                    line.id,
                    line.employee_id.id,
                    "%.2f" % line.amount,
                    "%.2f" % line.net_amount,
                    (line.bank_account_no or "").strip(),
                    (line.routing_no or "").strip(),
                    line.payment_channel or "bank",
                    (line.mfs_wallet or "").strip(),
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
            # release the recoveries the replaced lines took (through the ORM,
            # so each recovery's balance is recomputed)
            self.env["fix.payroll.recovery.line"].sudo().search(
                [("bonus_line_id", "in", rec.line_ids.ids)]
            )._guarded().unlink()
            rec.line_ids._guarded().unlink()
            vals_list, skipped, unrated = [], [], []
            multiplier = q2(rec.multiplier)
            withhold = rec.company_id.payroll_bonus_tds == "marginal"
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
                amount = min(wanted, cap)
                rate = Decimal("0")
                if withhold:
                    slip = rec._rate_slip(emp)
                    if not slip:
                        unrated.append(emp.name)
                        continue
                    rate = marginal_rate(
                        slip.annual_taxable,
                        slip.taxpayer_category,
                        1 if slip.has_disabled_child else 0,
                    )
                tax = q2(amount * rate)
                account, routing = master_bank(emp)
                channel, provider, wallet = master_payment_channel(emp)
                if channel == "mfs":
                    account = routing = False
                vals_list.append(
                    {
                        "run_id": rec.id,
                        "employee_id": emp.id,
                        "contract_id": contract.id,
                        "completed_years": years,
                        "basic": float(basic),
                        "base_amount": float(base),
                        "amount": float(amount),
                        "capped": wanted > cap,
                        "marginal_rate": float(rate * 100),
                        "tax_withheld": float(tax),
                        "net_amount": float(amount - tax),
                        "payment_channel": channel,
                        "mfs_provider": provider,
                        "mfs_wallet": wallet,
                        "bank_account_no": account,
                        "routing_no": routing,
                    }
                )
            if unrated:
                raise UserError(
                    "Festival bonus TDS is withheld at the payslip marginal rate, and %s have no "
                    "committed payslip to take the rate from." % ", ".join(sorted(unrated))
                )
            lines = self.env["fix.payroll.bonus.line"]._guarded().create(vals_list)
            if rec.company_id.payroll_recovery_source == "any_payment":
                Recovery = self.env["fix.payroll.recovery"]
                month = rec.bonus_date.strftime("%Y-%m")
                for line in lines:
                    due = Recovery._due(line.employee_id, rec.company_id, month, line.net_amount)
                    taken = Recovery._record(due, month, bonus_line_id=line.id)
                    if taken:
                        line._guarded().write(
                            {
                                "recovery_deduction": taken,
                                "net_amount": round(line.net_amount - taken, 2),
                            }
                        )
                        skipped.append(
                            "%s: overpayment recovery %.2f deducted"
                            % (line.employee_id.name, taken)
                        )
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
                    "total_tax": sum(lines.mapped("tax_withheld")),
                    "total_net": sum(lines.mapped("net_amount")),
                    "total_recovery": sum(lines.mapped("recovery_deduction")),
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
                lambda line: (
                    not (line.mfs_provider and line.mfs_wallet)
                    if line.payment_channel == "mfs"
                    else not line.bank_account_no or not line.routing_no
                )
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
        # the employee receives the bonus net of any withholding
        return [
            beftn_entry(line.employee_id, line.bank_account_no, line.routing_no, line.net_amount)
            for line in self.line_ids
            if line.net_amount > 0 and line.payment_channel != "mfs"
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
            if rec._lines_digest() != rec.approved_digest:
                raise UserError(
                    "Bonus run %s does not match its approval - nothing is paid from a changed "
                    "run." % rec.name
                )
            account, routing = originating_account(rec.company_id)
            submitted = fields.Datetime.now()
            wallets = rec.line_ids.filtered(
                lambda ln: ln.payment_channel == "mfs" and ln.net_amount > 0
            )
            cur = rec.company_id.currency_id
            bank_total = cur.round(rec.total_net - sum(wallets.mapped("net_amount")))
            batch = self.env["fix.beftn.batch"]
            if cur.compare_amounts(bank_total, 0.0) > 0 or not wallets:
                batch = (
                    self.env["fix.beftn.batch"]
                    ._guarded()
                    .create(
                        {
                            "bonus_run_id": rec.id,
                            "company_id": rec.company_id.id,
                            "submitted_at": submitted,
                            "settlement_date": beftn_settlement_date(submitted),
                            "employee_count": rec.employee_count - len(wallets),
                            "total_amount": bank_total,
                            "company_account_no": account,
                            "company_routing_no": routing,
                            "released_by_id": self.env.user.id,
                        }
                    )
                )
                batch.action_generate_beftn_file()
            if wallets:
                # the same rule and file as the monthly run
                self.env["fix.mfs.disbursement"]._create_rows(
                    {"bonus_run_id": rec.id},
                    [
                        (ln.employee_id, ln.mfs_provider, ln.mfs_wallet, ln.net_amount)
                        for ln in wallets
                    ],
                    submitted,
                    rec.company_id,
                    "BONUS %s" % rec.name,
                )
            rec._guarded().write(
                {
                    "state": "paid",
                    "beftn_batch_id": batch.id or False,
                    "released_by_id": self.env.user.id,
                    "released_on": fields.Datetime.now(),
                }
            )
            publish(
                self.env,
                "payroll.bonus_paid",
                "fix.payroll.bonus.run",
                rec.id,
                {"run": rec.name, "total": float(rec.total_amount), "batch_id": batch.id or False},
            )

    def action_post(self):
        for rec in self:
            if rec.state != "paid" or rec.gl_move_id:
                raise UserError("Post a paid bonus run once.")
            cur = rec.company_id.currency_id
            if cur.is_zero(rec.total_tax or 0.0) and cur.is_zero(rec.total_recovery or 0.0):
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
            else:
                move = rec._post_with_tds()
            rec._guarded().write({"state": "posted", "gl_move_id": move.id})
            publish(
                self.env,
                "payroll.bonus_posted",
                "fix.payroll.bonus.run",
                rec.id,
                rec._bonus_posted_payload(move),
            )

    def _bonus_posted_payload(self, move):
        """payroll.bonus_posted for M19/M50/M51: the bonus and its TDS per
        operating unit (the employee's unit, else the contract's, else the
        run's - the monthly run's cost rule); the per-unit tax sums to the
        run's tax_total."""
        self.ensure_one()
        by_ou = {}
        for line in self.sudo().line_ids:
            emp = line.employee_id.sudo()
            ou = (
                emp.operating_unit_id
                or line.contract_id.operating_unit_id
                or self.operating_unit_id
            )
            row = by_ou.setdefault(ou.id or False, [0.0, 0.0])
            row[0] += line.amount
            row[1] += line.tax_withheld
        cur = self.company_id.currency_id
        return {
            "company_id": self.company_id.id,
            "bonus_run_id": self.id,
            "move_id": move.id,
            "period_end": str(self.bonus_date),
            "tax_total": float(cur.round(self.total_tax or 0.0)),
            "by_operating_unit": [
                {
                    "operating_unit_id": ou_id,
                    "gross": float(cur.round(gross)),
                    "tax": float(cur.round(tax)),
                }
                for ou_id, (gross, tax) in sorted(by_ou.items(), key=lambda kv: kv[0] or 0)
            ],
        }

    def _post_with_tds(self):
        """Dr salary expense (the bonus) / Cr net payable (paid) / Cr TDS
        payable / Cr overpayment recovery (each only when carried)."""
        self.ensure_one()
        company = self.company_id
        cur = company.currency_id
        accounts = list(PAYMENT_GL_ACCOUNTS)
        if not cur.is_zero(self.total_tax or 0.0):
            accounts.append(("payroll_tax_payable_account_id", "Income Tax (TDS) Payable"))
        if not cur.is_zero(self.total_recovery or 0.0):
            accounts.append(("payroll_recovery_account_id", "Overpayment Recovery Account"))
        journal = payroll_gl_journal(company, accounts, self.name)
        rows = [
            ("payroll_salary_expense_account_id", "Festival bonus", self.total_amount, 0.0),
            ("payroll_net_payable_account_id", "Festival bonus paid", 0.0, self.total_net),
            ("payroll_tax_payable_account_id", "Festival bonus TDS", 0.0, self.total_tax),
            (
                "payroll_recovery_account_id",
                "Overpayment recovered from festival bonus",
                0.0,
                self.total_recovery,
            ),
        ]
        rows = [r for r in rows if not (cur.is_zero(r[2] or 0.0) and cur.is_zero(r[3] or 0.0))]
        lines = [
            {
                "account_id": company[fname].id,
                "name": "%s %s" % (label, self.name),
                "debit": cur.round(debit),
                "credit": cur.round(credit),
            }
            for fname, label, debit, credit in rows
        ]
        debits = sum(line["debit"] for line in lines)
        credits = sum(line["credit"] for line in lines)
        if cur.compare_amounts(debits, credits):
            raise UserError(
                "Festival bonus %s does not balance: amount != net + TDS + recovery." % self.name
            )
        move, _dims = post_with_dimensions(
            self.env,
            {
                "move_type": "entry",
                "ref": "Festival Bonus - %s" % self.name,
                "journal_id": journal.id,
                "date": self.bonus_date,
                "line_ids": [Command.create(line) for line in lines],
            },
            {
                idx: {"operating_unit_id": self.operating_unit_id.id or False}
                for idx in range(len(lines))
            },
            source="payroll_subledger",
        )
        return move

    def action_cancel(self):
        for rec in self:
            if rec.state not in ("draft", "computed"):
                raise UserError("Only a bonus run not yet approved can be cancelled.")
            rec._refuse_while_pending("cancel it")
            self.env["fix.payroll.recovery.line"].sudo().search(
                [("bonus_line_id", "in", rec.line_ids.ids)]
            )._guarded().unlink()
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
            ("correction", "Post-Payment Correction"),
        ],
        required=True,
        default="arrear",
    )
    # BRU-PAY-04 / T-07 (A09 round 2): a paid payslip is never edited; what
    # it should have paid on top is an off-cycle correction linked to it
    correction_slip_id = fields.Many2one(
        "fix.payslip",
        string="Corrects Payslip",
        index=True,
        ondelete="restrict",
        help="The paid payslip this correction tops up. The slip itself stays as paid.",
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
    # BLA s.19 death in service: the settlement is paid to each NOMINEE, with
    # the share M21 pinned; the nominee's account is a verified payroll record
    nominee_dependant_id = fields.Many2one(
        "fix.hr.dependant", string="Nominee", readonly=True, ondelete="restrict"
    )
    nominee_name = fields.Char(string="Nominee (payee)", readonly=True)
    nominee_share_pct = fields.Float(string="Nominee Share %", readonly=True)
    nominee_account_id = fields.Many2one(
        "fix.payroll.nominee.account", string="Nominee Account", readonly=True
    )
    # an approved overpayment recovery taken at the approval request (company
    # setting payroll_recovery_source = any_payment), pinned in the digest
    recovery_deduction = fields.Monetary(
        currency_field="currency_id", string="Overpayment Recovery", readonly=True, default=0.0
    )
    net_amount = fields.Monetary(
        currency_field="currency_id",
        string="Net Paid",
        compute="_compute_net_amount",
        store=True,
    )
    # A09 round 2: how it is paid - the bank, or (an employee with no bank
    # account) the MFS wallet on the master, exactly as the monthly run
    payment_channel = fields.Selection(
        [("bank", "Bank (BEFTN)"), ("mfs", "MFS Wallet")], default="bank", readonly=True
    )
    mfs_provider = fields.Selection(
        lambda self: self.env["hr.employee"]._fields["mfs_provider"].selection, readonly=True
    )
    mfs_wallet = fields.Char(readonly=True)

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
            "nominee_dependant_id",
            "nominee_name",
            "nominee_share_pct",
            "nominee_account_id",
            "recovery_deduction",
            "payment_channel",
            "mfs_provider",
            "mfs_wallet",
        }

    def _payroll_state_locked_fields(self) -> set:
        # what was approved is what is paid: amount AND payee (A09 probe O4)
        locked = super()._payroll_state_locked_fields()
        if self.state != "draft":
            locked |= {"employee_id", "amount", "currency_id", "payment_type"}
            locked |= {"payment_date", "company_id"}
        if self.exit_id or self.source_event_id:
            locked |= {"employee_id", "amount", "currency_id", "payment_type", "company_id"}
        if self.state != "draft":
            locked |= {"correction_slip_id", "reason"}
        return locked

    @api.constrains("payment_type", "correction_slip_id", "employee_id", "company_id", "reason")
    def _check_correction(self):
        for rec in self:
            slip = rec.correction_slip_id.sudo()
            if rec.payment_type != "correction":
                if slip:
                    raise ValidationError(
                        "Only a post-payment correction names the payslip it corrects."
                    )
                continue
            if not slip:
                raise ValidationError(
                    "A post-payment correction names the paid payslip it corrects."
                )
            if slip.period_id.state not in PAID_PERIOD_STATES:
                raise ValidationError(
                    "Payslip %s is in a %s run: only a PAID payslip is corrected off-cycle; an "
                    "unpaid run is recalculated." % (slip.display_name, slip.period_id.state)
                )
            if slip.employee_id != rec.employee_id or slip.company_id != rec.company_id:
                raise ValidationError(
                    "A correction pays the employee and company of the payslip it corrects."
                )
            if not (rec.reason or "").strip():
                raise ValidationError("State what the correction puts right.")

    @api.constrains("amount")
    def _check_amount(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError("An off-cycle payment is a positive amount.")

    @api.depends("amount", "recovery_deduction")
    def _compute_net_amount(self):
        for rec in self:
            rec.net_amount = round((rec.amount or 0.0) - (rec.recovery_deduction or 0.0), 2)

    # payments a recovery never reduces: what the law or an award fixes
    def _recovery_exempt(self):
        self.ensure_one()
        return (
            self.payment_type in RECOVERY_EXEMPT_TYPES
            or bool(self.exit_id)
            or bool(self.nominee_name)
        )

    def _release_recovery(self):
        lines = (
            self.env["fix.payroll.recovery.line"].sudo().search([("offcycle_id", "in", self.ids)])
        )
        lines._guarded().unlink()
        self.filtered("recovery_deduction")._guarded().write({"recovery_deduction": 0.0})

    def _take_recovery(self):
        """At the approval request: what an approved recovery takes from this
        payment, within the monthly cap across every payment of the month."""
        self.ensure_one()
        self._release_recovery()
        if self.company_id.payroll_recovery_source != "any_payment" or self._recovery_exempt():
            return 0.0
        Recovery = self.env["fix.payroll.recovery"]
        month = self.payment_date.strftime("%Y-%m")
        # never the whole payment: something is paid on every approved payment
        due = Recovery._due(self.employee_id, self.company_id, month, self.amount - 0.01)
        taken = Recovery._record(due, month, offcycle_id=self.id)
        if taken:
            self._guarded().write({"recovery_deduction": taken})
        return taken

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("correction_slip_id"):
                slip = self.env["fix.payslip"].sudo().browse(vals["correction_slip_id"])
                vals.setdefault("employee_id", slip.employee_id.id)
                vals.setdefault("company_id", slip.company_id.id)
                vals.setdefault("payment_type", "correction")
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
            + (
                [(self.id, self.employee_id.id, "recovery", "%.2f" % self.recovery_deduction, "")]
                if self.recovery_deduction
                else []
            )
            + (
                [
                    (
                        self.id,
                        self.employee_id.id,
                        "mfs",
                        self.mfs_provider or "",
                        self.mfs_wallet or "",
                    )
                ]
                if self.payment_channel == "mfs"
                else []
            )
            + (
                [
                    (
                        self.id,
                        self.employee_id.id,
                        "nominee",
                        self.nominee_name,
                        "%.4f" % self.nominee_share_pct,
                    )
                ]
                if self.nominee_name
                else []
            )
        )

    def _check_source_amount(self):
        """A settlement pays the exit's computed net (I1), nothing else; a
        nominee's payment pays exactly that nominee's pinned share of it."""
        for rec in self.filtered("exit_id"):
            exit_rec = rec.exit_id.sudo()
            net = exit_rec._fix_settlement_breakdown()["net"]
            if rec.nominee_name:
                payees = exit_rec._fix_nominee_payees()
                total = sum(float(p.get("amount") or 0.0) for p in payees)
                mine = [
                    p
                    for p in payees
                    if (p.get("dependant_id") or False) == (rec.nominee_dependant_id.id or False)
                    and (p.get("name") or "") == rec.nominee_name
                ]
                if rec.currency_id.compare_amounts(total, net) != 0 or not mine:
                    raise UserError(
                        "Exit %s's nominee split no longer matches the settlement payroll "
                        "computes (%.2f)." % (exit_rec.display_name, net)
                    )
                net = float(mine[0].get("amount") or 0.0)
            if rec.currency_id.compare_amounts(rec.amount, net) != 0:
                raise UserError(
                    "Settlement payment %s is %.2f but payroll computes %.2f for exit %s."
                    % (rec.name, rec.amount, net, rec.exit_id.display_name)
                )

    def _payee_channel(self):
        """('bank' | 'mfs', provider, wallet): a nominee is paid by bank; the
        employee by the master's channel (the monthly run's rule)."""
        self.ensure_one()
        if self.nominee_name:
            return "bank", False, False
        return master_payment_channel(self.employee_id)

    def _payee_bank(self):
        """(account, routing, nominee account record) of who this pays: the
        employee's registered salary account, or for a death settlement the
        nominee's VERIFIED account (fix.payroll.nominee.account)."""
        self.ensure_one()
        if not self.nominee_name:
            if self._payee_channel()[0] == "mfs":
                return False, False, self.env["fix.payroll.nominee.account"]
            account, routing = master_bank(self.employee_id)
            return account, routing, self.env["fix.payroll.nominee.account"]
        acc = self.env["fix.payroll.nominee.account"]._verified_for(
            self.employee_id, self.nominee_dependant_id, self.nominee_name
        )
        return (acc.bank_account_no or False), (acc.routing_no or False), acc

    def action_request_approval(self, justification=None):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft off-cycle payment is sent for approval.")
            account, routing, nominee_acc = rec._payee_bank()
            if rec.nominee_name and not nominee_acc:
                raise UserError(
                    "Nominee %s has no registered account: record the nominee's bank account "
                    "and have a second payroll user verify it (Nominee Accounts) before this "
                    "death-in-service payment is requested." % rec.nominee_name
                )
            channel, provider, wallet = rec._payee_channel()
            if channel == "mfs":
                if not provider or not MFS_WALLET_RE.match(wallet or ""):
                    raise UserError(
                        "%s is paid by MFS but has no provider or no valid 11-digit wallet."
                        % rec.employee_id.name
                    )
            elif not account or not routing:
                raise UserError(
                    "%s has no registered salary account and routing number: an off-cycle "
                    "payment is never sent to an assumed account." % rec.employee_id.name
                )
            rec._check_source_amount()
            rec._guarded().write(
                {
                    "bank_account_no": account,
                    "routing_no": routing,
                    "nominee_account_id": nominee_acc.id or False,
                    "payment_channel": channel,
                    "mfs_provider": provider,
                    "mfs_wallet": wallet,
                }
            )
            rec._take_recovery()
        return super().action_request_approval(justification=justification)

    def action_approve(self):
        routed_payroll_decision(self, "an off-cycle payment", lambda rec: rec._approval_preparers())
        for rec in self:
            if rec.state != "draft":
                raise UserError("Approve a draft off-cycle payment")
            # the payee the approver saw is still the payee on record
            account, routing, _acc = rec._payee_bank()
            channel, _provider, wallet = rec._payee_channel()
            if (account, routing, channel, wallet or False) != (
                rec.bank_account_no,
                rec.routing_no,
                rec.payment_channel,
                rec.mfs_wallet or False,
            ):
                raise UserError(
                    "%s's bank details changed after approval was requested - request it again."
                    % (rec.nominee_name or rec.employee_id.name)
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
        self._release_recovery()
        for rec in self:
            rec.message_post(body="Off-cycle payment rejected: %s" % (comment or ""))

    def action_recall_approval(self):
        result = super().action_recall_approval()
        self._release_recovery()
        return result

    def _beftn_entries(self):
        from .fix_payroll import beftn_entry

        self.ensure_one()
        if self.state != "approved" or self._payee_digest() != self.approved_digest:
            raise UserError(
                "Off-cycle payment %s does not match its approval - nothing is paid from a "
                "changed payment." % self.name
            )
        entry = beftn_entry(
            self.employee_id, self.bank_account_no, self.routing_no, self.net_amount
        )
        if self.nominee_name:
            entry.employee_name = self.nominee_name.strip()  # the nominee is the beneficiary
        return [entry]

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
            submitted = fields.Datetime.now()
            if rec.payment_channel == "mfs":
                if rec._payee_digest() != rec.approved_digest:
                    raise UserError(
                        "Off-cycle payment %s does not match its approval - nothing is paid "
                        "from a changed payment." % rec.name
                    )
                disb = self.env["fix.mfs.disbursement"]._create_rows(
                    {"offcycle_id": rec.id},
                    [(rec.employee_id, rec.mfs_provider, rec.mfs_wallet, rec.net_amount)],
                    submitted,
                    rec.company_id,
                    "OFFCYCLE %s" % rec.name,
                )
                rec._guarded().write(
                    {
                        "state": "paid",
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
                        "batch_id": False,
                        "mfs_disbursement_id": disb.id,
                    },
                )
                continue
            account, routing = originating_account(rec.company_id)
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
                        "total_amount": rec.net_amount,
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
            label = "%s %s" % (
                dict(self._fields["payment_type"].selection)[rec.payment_type],
                rec.name,
            )
            cur = rec.company_id.currency_id
            if cur.is_zero(rec.recovery_deduction or 0.0):
                payroll_gl_journal(rec.company_id, PAYMENT_GL_ACCOUNTS, rec.name)
                move = post_two_line_entry(
                    self.env,
                    rec.company_id,
                    "Off-Cycle Payment - %s" % rec.name,
                    rec.payment_date,
                    rec.amount,
                    label,
                    "payroll_salary_expense_account_id",
                    "payroll_net_payable_account_id",
                )
            else:
                move = rec._post_with_recovery(label)
            rec._guarded().write({"state": "posted", "gl_move_id": move.id})

    def _post_with_recovery(self, label):
        """Dr salary expense (the payment) / Cr net payable (what was paid) /
        Cr overpayment recovery (what it recovered)."""
        self.ensure_one()
        company = self.company_id
        cur = company.currency_id
        journal = payroll_gl_journal(
            company,
            [
                *PAYMENT_GL_ACCOUNTS,
                ("payroll_recovery_account_id", "Overpayment Recovery Account"),
            ],
            self.name,
        )
        rows = [
            ("payroll_salary_expense_account_id", label, self.amount, 0.0),
            ("payroll_net_payable_account_id", "%s paid" % label, 0.0, self.net_amount),
            (
                "payroll_recovery_account_id",
                "Overpayment recovered from %s" % self.name,
                0.0,
                self.recovery_deduction,
            ),
        ]
        lines = [
            {
                "account_id": company[f].id,
                "name": n,
                "debit": cur.round(d),
                "credit": cur.round(c),
            }
            for f, n, d, c in rows
        ]
        if cur.compare_amounts(sum(ln["debit"] for ln in lines), sum(ln["credit"] for ln in lines)):
            raise UserError("Off-cycle payment %s does not balance." % self.name)
        move, _dims = post_with_dimensions(
            self.env,
            {
                "move_type": "entry",
                "ref": "Off-Cycle Payment - %s" % self.name,
                "journal_id": journal.id,
                "date": self.payment_date,
                "line_ids": [Command.create(line) for line in lines],
            },
            {idx: {"operating_unit_id": False} for idx in range(len(lines))},
            source="payroll_subledger",
        )
        return move

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
            rec._release_recovery()
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
    # ---- A09 round 2 (M56-13) ---------------------------------------------------
    # The profit is the AUDITED figure. M19 holds no audited-profit record (its
    # fix.financial.report.bridge P&L is computed from the ledger, not signed
    # by an auditor), so the figure is typed WITH the audited statements and
    # the auditor's report reference as evidence; a linked M19 P&L shows the
    # ledger figure beside it for the trustees.
    audited_statement_file = fields.Binary(string="Audited Financial Statements", attachment=True)
    audited_statement_filename = fields.Char()
    audit_report_ref = fields.Char(string="Auditor's Report Reference")
    ledger_report_id = fields.Many2one(
        "fix.financial.report.bridge",
        string="M19 Profit & Loss (ledger)",
        domain="[('report_type', '=', 'pnl'), ('company_id', '=', company_id)]",
    )
    ledger_net_profit = fields.Monetary(
        currency_field="currency_id",
        string="Ledger Net Profit (M19, at calculation)",
        readonly=True,
    )
    beneficiary_ids = fields.One2many(
        "fix.wppf.beneficiary", "allocation_id", string="Beneficiaries"
    )
    approved_digest = fields.Char(readonly=True)
    # the 10% Bangladesh Workers' Welfare Foundation share, paid by challan
    bwwf_challan_date = fields.Date(string="BWWF Challan Date")
    bwwf_challan_file = fields.Binary(string="BWWF Deposit Challan", attachment=True)
    bwwf_challan_filename = fields.Char()
    bwwf_paid_by_id = fields.Many2one("res.users", string="BWWF Paid By", readonly=True)
    bwwf_paid_on = fields.Datetime(string="BWWF Paid On", readonly=True)
    bwwf_move_id = fields.Many2one("account.move", string="BWWF GL Entry", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "prepared_by_id",
            "calculated_by_id",
            "approved_by_id",
            "approved_on",
            "gl_move_id",
            "ledger_net_profit",
            "beneficiary_ids",
            # counted from the beneficiary lines, never typed (M56-13)
            "eligible_workers_count",
            "approved_digest",
            "bwwf_paid_by_id",
            "bwwf_paid_on",
            "bwwf_move_id",
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
        if self.state != "draft":
            locked |= {
                "audited_statement_file",
                "audited_statement_filename",
                "audit_report_ref",
                "ledger_report_id",
            }
        if self.bwwf_paid_on:
            locked |= {
                "bwwf_challan_ref",
                "bwwf_challan_date",
                "bwwf_challan_file",
                "bwwf_challan_filename",
            }
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
            if not rec.audited_statement_file or not (rec.audit_report_ref or "").strip():
                raise UserError(
                    "The WPPF profit is the audited net profit (BLA s.234): attach the audited "
                    "financial statements and the auditor's report reference first."
                )
            ledger = 0.0
            if rec.ledger_report_id:
                report = rec.ledger_report_id.sudo()
                if report.company_id != rec.company_id or report.report_type != "pnl":
                    raise UserError("Link a profit & loss statement of the same company.")
                if not report.generated_at:
                    raise UserError("Generate the linked M19 profit & loss statement first.")
                ledger = report.headline_amount
            rec = rec._guarded()
            count = rec._wppf_build_beneficiaries()
            if not count:
                raise UserError(
                    "No employee of %s is an eligible WPPF beneficiary." % rec.company_id.name
                )
            rec.write({"eligible_workers_count": count, "ledger_net_profit": ledger})
            rec._compute_wppf_split()
            rec.write({"state": "calculated", "calculated_by_id": self.env.user.id})

    def _wppf_build_beneficiaries(self):
        """One line per active employee of the company under an active
        contract: eligible unless short of the company's minimum service or
        marked by payroll as not a worker (BLA s.2(65): managerial and
        administrative staff are not workers). Returns the eligible count."""
        self.ensure_one()
        Line = self.env["fix.wppf.beneficiary"].sudo()._guarded()
        Line.search([("allocation_id", "=", self.id)]).unlink()
        as_of = self.fiscal_year_end_date or fields.Date.context_today(self)
        minimum = self.company_id.payroll_wppf_min_service_months or 0
        contracts = (
            self.env["fix.employment.contract"]
            .sudo()
            .search(
                [
                    ("company_id", "=", self.company_id.id),
                    ("state", "=", "active"),
                    ("employee_id.active", "=", True),
                ],
                order="employee_id, joining_date",
            )
        )
        vals_list, seen = [], set()
        for contract in contracts:
            emp = contract.employee_id
            if emp.id in seen:
                continue
            seen.add(emp.id)
            joining = fields.Date.to_date(contract.joining_date)
            delta = relativedelta(as_of, joining) if joining <= as_of else relativedelta()
            months = delta.years * 12 + delta.months if joining <= as_of else 0
            short = bool(minimum) and months < minimum
            vals_list.append(
                {
                    "allocation_id": self.id,
                    "employee_id": emp.id,
                    "contract_id": contract.id,
                    "joining_date": joining,
                    "service_months": months,
                    "auto_excluded": short,
                    "auto_reason": (
                        "%d month(s) of service, under the %d-month minimum" % (months, minimum)
                    )
                    if short
                    else False,
                }
            )
        lines = Line.create(vals_list)
        return len(lines.filtered("eligible"))

    def _wppf_recount(self):
        for rec in self:
            count = len(rec.beneficiary_ids.filtered("eligible"))
            if not count:
                raise UserError("A WPPF allocation keeps at least one eligible beneficiary.")
            rec._guarded().write({"eligible_workers_count": count})

    def _beneficiary_digest(self):
        self.ensure_one()
        return digest_rows(
            [
                ("emp-%d" % ln.employee_id.id, str(bool(ln.eligible)), "%.2f" % ln.share_amount)
                for ln in self.sudo().beneficiary_ids
            ]
            + [("pool", "%.2f" % self.total_wppf_pool, str(self.eligible_workers_count))]
        )

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
                    "approved_digest": rec._beneficiary_digest(),
                }
            )

    def _check_approved_beneficiaries(self):
        for rec in self:
            if rec.approved_digest and rec.approved_digest != rec._beneficiary_digest():
                raise UserError(
                    "WPPF allocation %s no longer matches what the trustees approved." % rec.name
                )

    def action_pay_bwwf(self):
        """The 10% Bangladesh Workers' Welfare Foundation share (BLA s.240,
        BWWF Act 2006): paid by treasury challan, recorded by a Payroll
        Disbursement Releaser who neither prepared nor approved the
        allocation, with the challan as evidence, and posted Dr WPPF payable /
        Cr the company's WPPF paying bank account."""
        check_releaser(
            self,
            "a WPPF BWWF payment",
            lambda rec: rec._approval_preparers() | rec.approved_by_id,
        )
        accounts = [
            ("payroll_wppf_payable_account_id", "WPPF Payable"),
            ("payroll_wppf_bank_account_id", "WPPF / BWWF Paying Bank Account"),
        ]
        for rec in self:
            if rec.state not in ("approved", "posted"):
                raise UserError("The BWWF share is paid from an approved WPPF allocation.")
            if rec.bwwf_paid_on:
                raise UserError("The BWWF share of %s is already paid." % rec.name)
            rec._check_approved_beneficiaries()
            if not (
                (rec.bwwf_challan_ref or "").strip()
                and rec.bwwf_challan_date
                and rec.bwwf_challan_file
            ):
                raise UserError(
                    "Record the BWWF deposit challan (reference, date and the challan itself) "
                    "before marking the BWWF share paid."
                )
            payroll_gl_journal(rec.company_id, accounts, rec.name)
            move = post_two_line_entry(
                self.env,
                rec.company_id,
                "WPPF BWWF Payment - %s" % rec.name,
                rec.bwwf_challan_date,
                rec.welfare_foundation_amount,
                "BWWF 10%% share %s (challan %s)" % (rec.fiscal_year, rec.bwwf_challan_ref),
                "payroll_wppf_payable_account_id",
                "payroll_wppf_bank_account_id",
            )
            rec._guarded().write(
                {
                    "bwwf_paid_by_id": self.env.user.id,
                    "bwwf_paid_on": fields.Datetime.now(),
                    "bwwf_move_id": move.id,
                }
            )
        return True

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
            rec._check_approved_beneficiaries()
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


# WPPF payments to participants: ITA 2023 s.88, 10% at payment (benchmark
# "Bangladesh statutory" table, verified [48]).
WPPF_PAYMENT_TDS_RATE = Decimal("0.10")


class FixWppfBeneficiary(models.Model):
    """One employee's place in a WPPF allocation (BLA s.240-242): eligibility,
    the equal share of the cash pool, and the s.88 withholding on it."""

    _name = "fix.wppf.beneficiary"
    _description = "WPPF Beneficiary"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "allocation_id, employee_id"

    allocation_id = fields.Many2one(
        "fix.wppf.allocation", required=True, ondelete="cascade", index=True, readonly=True
    )
    company_id = fields.Many2one(related="allocation_id.company_id", store=True)
    operating_unit_id = fields.Many2one("operating.unit", readonly=True)
    currency_id = fields.Many2one(related="allocation_id.currency_id")
    employee_id = fields.Many2one("hr.employee", required=True, index=True, readonly=True)
    contract_id = fields.Many2one("fix.employment.contract", readonly=True)
    joining_date = fields.Date(readonly=True)
    service_months = fields.Integer(readonly=True)
    auto_excluded = fields.Boolean(string="Excluded by Rule", readonly=True)
    auto_reason = fields.Char(string="Rule", readonly=True)
    worker_status = fields.Selection(
        [
            ("worker", "Worker (BLA s.2(65))"),
            ("excluded", "Not a worker (managerial / administrative)"),
        ],
        required=True,
        default="worker",
    )
    exclusion_reason = fields.Char(string="Why Not a Worker")
    eligible = fields.Boolean(compute="_compute_share", store=True)
    share_amount = fields.Monetary(
        currency_field="currency_id", compute="_compute_share", store=True
    )
    tds_amount = fields.Monetary(
        currency_field="currency_id", compute="_compute_share", store=True, string="TDS (s.88)"
    )
    net_share = fields.Monetary(currency_field="currency_id", compute="_compute_share", store=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "allocation_id",
            "operating_unit_id",
            "employee_id",
            "contract_id",
            "joining_date",
            "service_months",
            "auto_excluded",
            "auto_reason",
        }

    @api.depends("auto_excluded", "worker_status", "allocation_id.per_worker_equal_share")
    def _compute_share(self):
        for rec in self:
            rec.eligible = not rec.auto_excluded and rec.worker_status == "worker"
            share = Decimal(str(rec.allocation_id.per_worker_equal_share or 0.0))
            share = share if rec.eligible else Decimal(0)
            tds = q2(share * WPPF_PAYMENT_TDS_RATE)
            rec.share_amount = float(share)
            rec.tds_amount = float(tds)
            rec.net_share = float(share - tds)

    def write(self, vals):
        if not self._fix_guard_open() and {"worker_status", "exclusion_reason"} & set(vals):
            for rec in self:
                alloc = rec.allocation_id
                if alloc.state != "calculated" or alloc.approval_state == "pending":
                    raise UserError(
                        "A WPPF beneficiary is classified on a calculated allocation, before "
                        "the trustees are asked to approve it."
                    )
            if vals.get("worker_status") == "excluded" and not (
                vals.get("exclusion_reason") or all(r.exclusion_reason for r in self)
            ):
                raise UserError("State why the employee is not a worker (BLA s.2(65)).")
        result = super().write(vals)
        if {"worker_status"} & set(vals):
            self.mapped("allocation_id")._wppf_recount()
        return result
