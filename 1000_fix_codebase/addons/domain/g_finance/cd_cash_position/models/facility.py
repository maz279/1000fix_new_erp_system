# cd_cash_position — Facilities & Covenants (A08 · M50).
#
# Bank facilities (term loans, overdraft / cash credit, LC, guarantees):
# the sanctioned limit is master data; UTILISATION is read from the posted
# GL (the facility's liability account, or for an overdraft the bank
# journal's negative balance) — never typed in. Term loans carry a
# generated repayment schedule whose instalments post Dr loan / Dr interest
# / Cr bank. Covenants are tested against GL-derived ratios and every test
# is kept as evidence.
from __future__ import annotations

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .treasury_common import bank_account_of, gl_balance, post_treasury_move, treasury_account

FACILITY_TYPES = [
    ("term_loan", "Term Loan"),
    ("short_term_loan", "Short-Term Loan"),
    ("overdraft", "Overdraft"),
    ("cash_credit", "Cash Credit"),
    ("lc", "Letter of Credit"),
    ("bank_guarantee", "Bank Guarantee"),
]
AMORTISING = ("term_loan", "short_term_loan")
REVOLVING = ("overdraft", "cash_credit")


class FixBankFacility(models.Model):
    _name = "fix.bank.facility"
    _description = "Bank Facility"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)
    lender_id = fields.Many2one("res.partner", string="Lender", required=True)
    facility_type = fields.Selection(FACILITY_TYPES, required=True, default="term_loan")
    sanction_ref = fields.Char(string="Sanction Letter Ref")
    sanction_date = fields.Date()
    expiry_date = fields.Date(string="Expiry / Maturity")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    limit_amount = fields.Monetary(
        string="Sanctioned Limit", currency_field="currency_id", required=True, tracking=True
    )
    interest_rate = fields.Float(string="Interest Rate (% p.a.)", digits=(6, 3), tracking=True)
    principal = fields.Monetary(
        string="Disbursed Principal", currency_field="currency_id", help="Term loans: amount drawn"
    )
    start_date = fields.Date(string="First Instalment Date")
    tenor_months = fields.Integer(string="Tenor (Months)")
    repayment_frequency = fields.Selection(
        [("monthly", "Monthly"), ("quarterly", "Quarterly")], default="monthly"
    )
    liability_account_id = fields.Many2one(
        "account.account",
        string="Liability Account",
        help="GL account the facility's outstanding is booked on (loans, LC acceptances)",
    )
    journal_id = fields.Many2one(
        "account.journal",
        string="Bank Account",
        domain="[('type', '=', 'bank'), ('company_id', '=', company_id)]",
        help="Overdraft / cash credit: the account whose debit balance is the utilisation. "
        "Loans: the account instalments are paid from.",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("closed", "Closed")],
        default="draft",
        required=True,
        tracking=True,
    )
    utilised = fields.Monetary(currency_field="currency_id", compute="_compute_utilisation")
    available = fields.Monetary(currency_field="currency_id", compute="_compute_utilisation")
    utilisation_pct = fields.Float(
        string="Utilisation %", compute="_compute_utilisation", digits=(6, 1)
    )
    next_due_date = fields.Date(compute="_compute_next_due")
    next_due_amount = fields.Monetary(currency_field="currency_id", compute="_compute_next_due")
    repayment_ids = fields.One2many(
        "fix.facility.repayment", "facility_id", string="Repayment Schedule"
    )
    covenant_ids = fields.One2many("fix.facility.covenant", "facility_id", string="Covenants")

    @api.constrains("limit_amount", "interest_rate", "tenor_months", "principal")
    def _check_terms(self):
        for fac in self:
            if fac.limit_amount <= 0:
                raise ValidationError("The sanctioned limit must be positive.")
            if fac.interest_rate < 0 or fac.tenor_months < 0:
                raise ValidationError("Interest rate and tenor cannot be negative.")
            if fac.principal > fac.limit_amount + 0.005:
                raise ValidationError("The disbursed principal cannot exceed the sanctioned limit.")

    def _compute_utilisation(self):
        for fac in self:
            if fac.facility_type in REVOLVING and fac.journal_id.default_account_id:
                used = max(
                    -gl_balance(self.env, fac.journal_id.default_account_id, fac.company_id), 0.0
                )
            elif fac.liability_account_id:
                used = max(-gl_balance(self.env, fac.liability_account_id, fac.company_id), 0.0)
            else:
                used = 0.0
            fac.utilised = used
            fac.available = fac.limit_amount - used
            fac.utilisation_pct = (
                round(used / fac.limit_amount * 100.0, 1) if fac.limit_amount else 0.0
            )

    def _compute_next_due(self):
        for fac in self:
            nxt = fac.repayment_ids.filtered(lambda r: r.state == "planned").sorted("due_date")[:1]
            fac.next_due_date = nxt.due_date if nxt else False
            fac.next_due_amount = nxt.total if nxt else 0.0

    def action_activate(self):
        for fac in self:
            if fac.state != "draft":
                raise UserError("Only a draft facility is activated.")
            if not (
                fac.liability_account_id or (fac.facility_type in REVOLVING and fac.journal_id)
            ):
                raise UserError(
                    "Set the liability account (or, for an overdraft, the bank account) so "
                    "utilisation can be read from the GL."
                )
            fac.state = "active"
        return True

    def action_close(self):
        for fac in self:
            if fac.repayment_ids.filtered(lambda r: r.state == "planned"):
                raise UserError("%s still has unpaid instalments." % fac.name)
            fac.state = "closed"
        return True

    def action_generate_schedule(self):
        """Equal-instalment (annuity) schedule over the tenor at the
        facility's rate; replaces only the unpaid lines of a fresh schedule."""
        for fac in self:
            if fac.facility_type not in AMORTISING:
                raise UserError("Only term / short-term loans carry an instalment schedule.")
            if fac.repayment_ids.filtered(lambda r: r.state == "paid"):
                raise UserError("Instalments are already paid — the schedule is not regenerated.")
            if not (fac.principal > 0 and fac.tenor_months > 0 and fac.start_date):
                raise UserError("Set the principal, tenor and first instalment date first.")
            step = 3 if fac.repayment_frequency == "quarterly" else 1
            periods = max(fac.tenor_months // step, 1)
            rate = (fac.interest_rate or 0.0) / 100.0 * step / 12.0
            if rate:
                instalment = fac.principal * rate / (1 - (1 + rate) ** -periods)
            else:
                instalment = fac.principal / periods
            balance = fac.principal
            lines = []
            for n in range(periods):
                interest = round(balance * rate, 2)
                principal = (
                    round(instalment - interest, 2) if n < periods - 1 else round(balance, 2)
                )
                balance = round(balance - principal, 2)
                lines.append(
                    (
                        0,
                        0,
                        {
                            "sequence": n + 1,
                            "due_date": fac.start_date + relativedelta(months=step * n),
                            "principal": principal,
                            "interest": interest,
                        },
                    )
                )
            fac.repayment_ids.unlink()
            fac.write({"repayment_ids": lines})
        return True


class FixFacilityRepayment(models.Model):
    _name = "fix.facility.repayment"
    _description = "Facility Repayment Instalment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "facility_id, due_date, sequence"

    facility_id = fields.Many2one(
        "fix.bank.facility", required=True, index=True, ondelete="cascade"
    )
    company_id = fields.Many2one(related="facility_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="facility_id.operating_unit_id", store=True, index=True
    )
    currency_id = fields.Many2one(related="facility_id.currency_id")
    sequence = fields.Integer(string="No.")
    due_date = fields.Date(required=True, index=True)
    principal = fields.Monetary(currency_field="currency_id")
    interest = fields.Monetary(currency_field="currency_id")
    total = fields.Monetary(currency_field="currency_id", compute="_compute_total", store=True)
    state = fields.Selection(
        [("planned", "Planned"), ("paid", "Paid")], default="planned", required=True, tracking=True
    )
    is_overdue = fields.Boolean(compute="_compute_overdue", string="Overdue")
    paid_date = fields.Date(readonly=True, copy=False)
    move_id = fields.Many2one("account.move", readonly=True, copy=False)

    @api.depends("principal", "interest")
    def _compute_total(self):
        for r in self:
            r.total = r.principal + r.interest

    def _compute_overdue(self):
        today = fields.Date.context_today(self)
        for r in self:
            r.is_overdue = r.state == "planned" and r.due_date and r.due_date < today

    def action_pay(self):
        """Dr loan liability (principal) + Dr interest expense / Cr bank."""
        for r in self:
            if r.state != "planned":
                raise UserError("This instalment is already paid.")
            fac = r.facility_id
            if fac.state != "active":
                raise UserError("%s is not active." % fac.name)
            if not fac.liability_account_id:
                raise UserError("%s has no liability account." % fac.name)
            bank = bank_account_of(fac.journal_id)
            lines = [
                (
                    fac.liability_account_id,
                    "Principal #%s" % r.sequence,
                    r.principal,
                    0.0,
                    fac.lender_id,
                )
            ]
            if r.interest:
                interest = treasury_account(self.env, fac.company_id, "interest_expense")
                lines.append(
                    (interest, "Interest #%s" % r.sequence, r.interest, 0.0, fac.lender_id)
                )
            lines.append(
                (bank, "%s instalment #%s" % (fac.name, r.sequence), 0.0, r.total, fac.lender_id)
            )
            move = post_treasury_move(
                self.env,
                fac.company_id,
                fields.Date.context_today(self),
                "LOAN %s #%s" % (fac.name, r.sequence),
                lines,
                source="treasury",
            )
            r.write(
                {"state": "paid", "paid_date": fields.Date.context_today(self), "move_id": move.id}
            )
        return True


COVENANT_METRICS = [
    ("current_ratio", "Current Ratio"),
    ("debt_to_equity", "Debt to Equity"),
    ("dscr", "Debt Service Coverage (trailing 12 months)"),
    ("min_liquidity", "Minimum Cash & Bank Balance"),
    ("utilisation_pct", "Facility Utilisation %"),
]

ASSET_CURRENT = ("asset_receivable", "asset_cash", "asset_current", "asset_prepayments")
LIAB_CURRENT = ("liability_payable", "liability_credit_card", "liability_current")


def _balance_by_types(env, company, types, date_from=None, date_to=None):
    domain = [
        ("company_id", "=", company.id),
        ("parent_state", "=", "posted"),
        ("account_id.account_type", "in", list(types)),
    ]
    if date_from:
        domain.append(("date", ">=", date_from))
    if date_to:
        domain.append(("date", "<=", date_to))
    groups = env["account.move.line"]._read_group(domain, [], ["balance:sum"])
    return (groups[0][0] or 0.0) if groups else 0.0


def covenant_metric(env, facility, metric, on_date):
    """GL-derived covenant metric, or None when it cannot be computed (the
    test then reads "not computable" instead of passing). Lender definitions
    vary — these are the plain GL ratios; agree them with the lender."""
    company = facility.company_id
    if metric == "utilisation_pct":
        return facility.utilisation_pct
    if metric == "min_liquidity":
        return round(_balance_by_types(env, company, ("asset_cash",), date_to=on_date), 2)
    if metric == "current_ratio":
        assets = _balance_by_types(env, company, ASSET_CURRENT, date_to=on_date)
        liabilities = -_balance_by_types(env, company, LIAB_CURRENT, date_to=on_date)
        return round(assets / liabilities, 3) if liabilities > 0.005 else None
    if metric == "debt_to_equity":
        asset_types = (*ASSET_CURRENT, "asset_non_current", "asset_fixed")
        liab_types = (*LIAB_CURRENT, "liability_non_current")
        assets = _balance_by_types(env, company, asset_types, date_to=on_date)
        liabilities = -_balance_by_types(env, company, liab_types, date_to=on_date)
        equity = assets - liabilities
        debt = sum(
            env["fix.bank.facility"]
            .search([("company_id", "=", company.id), ("state", "=", "active")])
            .mapped("utilised")
        )
        return round(debt / equity, 3) if equity > 0.005 else None
    if metric == "dscr":
        start = on_date - relativedelta(months=12)
        income = -_balance_by_types(env, company, ("income", "income_other"), start, on_date)
        expense = _balance_by_types(
            env, company, ("expense", "expense_direct_cost"), start, on_date
        )
        service = sum(
            env["fix.facility.repayment"]
            .search(
                [
                    ("company_id", "=", company.id),
                    ("due_date", ">", on_date),
                    ("due_date", "<=", on_date + relativedelta(months=12)),
                ]
            )
            .mapped("total")
        )
        return round((income - expense) / service, 3) if service > 0.005 else None
    return None


class FixFacilityCovenant(models.Model):
    _name = "fix.facility.covenant"
    _description = "Facility Covenant"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "facility_id, id"

    facility_id = fields.Many2one(
        "fix.bank.facility", required=True, index=True, ondelete="cascade"
    )
    company_id = fields.Many2one(related="facility_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="facility_id.operating_unit_id", store=True, index=True
    )
    name = fields.Char(required=True)
    metric = fields.Selection(COVENANT_METRICS, required=True)
    operator = fields.Selection(
        [("ge", "At Least (≥)"), ("le", "At Most (≤)")], required=True, default="ge"
    )
    threshold = fields.Float(required=True, digits=(16, 3))
    last_value = fields.Float(readonly=True, digits=(16, 3))
    last_result = fields.Selection(
        [("pass", "Pass"), ("breach", "Breach"), ("na", "Not Computable")], readonly=True
    )
    last_tested = fields.Date(readonly=True)
    test_ids = fields.One2many("fix.covenant.test", "covenant_id", string="Test History")

    def action_test(self):
        today = fields.Date.context_today(self)
        for cov in self:
            value = covenant_metric(self.env, cov.facility_id, cov.metric, today)
            if value is None:
                result = "na"
            elif cov.operator == "ge":
                result = "pass" if value >= cov.threshold else "breach"
            else:
                result = "pass" if value <= cov.threshold else "breach"
            self.env["fix.covenant.test"].create(
                {
                    "covenant_id": cov.id,
                    "tested_on": today,
                    "value": value or 0.0,
                    "threshold": cov.threshold,
                    "result": result,
                }
            )
            cov.write({"last_value": value or 0.0, "last_result": result, "last_tested": today})
            if result == "breach":
                cov.message_post(
                    body="Covenant breached: %s = %s (limit %s)" % (cov.name, value, cov.threshold)
                )
        return True


class FixCovenantTest(models.Model):
    _name = "fix.covenant.test"
    _description = "Covenant Test Result"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "tested_on desc, id desc"

    covenant_id = fields.Many2one(
        "fix.facility.covenant", required=True, index=True, ondelete="cascade"
    )
    company_id = fields.Many2one(related="covenant_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="covenant_id.operating_unit_id", store=True, index=True
    )
    tested_on = fields.Date(required=True)
    value = fields.Float(digits=(16, 3))
    threshold = fields.Float(digits=(16, 3))
    result = fields.Selection(
        [("pass", "Pass"), ("breach", "Breach"), ("na", "Not Computable")], required=True
    )


class FixCashForecastItem(models.Model):
    """A recurring cash item the 13-week forecast cannot read from a
    document (rent, payroll, utilities, statutory deposits, ...)."""

    _name = "fix.cash.forecast.item"
    _description = "Recurring Cash-Flow Item"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "direction, name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)
    direction = fields.Selection(
        [("inflow", "Inflow"), ("outflow", "Outflow")], required=True, default="outflow"
    )
    category = fields.Selection(
        [
            ("payroll", "Payroll"),
            ("rent", "Rent"),
            ("utilities", "Utilities"),
            ("tax", "Tax / VAT Deposit"),
            ("other", "Other"),
        ],
        required=True,
        default="other",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(currency_field="currency_id", required=True)
    frequency = fields.Selection(
        [
            ("once", "Once"),
            ("weekly", "Weekly"),
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
        ],
        required=True,
        default="monthly",
    )
    start_date = fields.Date(required=True, default=fields.Date.context_today)
    end_date = fields.Date()
    active = fields.Boolean(default=True)

    @api.constrains("amount")
    def _check_amount(self):
        for item in self:
            if item.amount <= 0:
                raise ValidationError("A forecast item amount must be positive.")

    def occurrences(self, date_from, date_to):
        """Dates this item falls due within [date_from, date_to]."""
        self.ensure_one()
        step = {
            "weekly": relativedelta(weeks=1),
            "monthly": relativedelta(months=1),
            "quarterly": relativedelta(months=3),
        }.get(self.frequency)
        out = []
        current = self.start_date
        n = 0
        while current and current <= date_to and n < 1000:
            if current >= date_from and (not self.end_date or current <= self.end_date):
                out.append(current)
            if not step:
                break
            n += 1
            current = self.start_date + step * n
        return out
