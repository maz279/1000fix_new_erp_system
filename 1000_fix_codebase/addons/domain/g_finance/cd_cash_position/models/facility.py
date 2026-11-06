# cd_cash_position — Facilities & Covenants (A08 · M50).
#
# Bank facilities (term loans, overdraft / cash credit, LC, guarantees):
# the sanctioned limit is master data; UTILISATION is read from the posted
# GL (the facility's liability account, or for an overdraft the bank
# journal's negative balance) — never typed in. Term loans carry a
# generated repayment schedule whose instalments post Dr loan / Dr interest
# / Cr bank. Covenants are tested against GL-derived ratios and every test
# is kept as evidence.
#
# A08 workflow audit (M50-12): the sanctioned terms and the generated
# schedule are frozen once the facility is active; a change of rate, tenor,
# limit or next due date is a fix.facility.amendment requested by one person
# and approved by a different Accounting Administrator, which re-schedules
# the unpaid instalments. Instalments are paid in schedule order, by an
# Accounting Administrator, at their scheduled amounts. A covenant's metric,
# operator and threshold are approved by an Accounting Administrator other
# than the one who set them and are frozen once approved; the test history
# is written only by the covenant test itself and never edited.
from __future__ import annotations

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .treasury_common import (
    GROUP_ACCOUNTANT,
    GROUP_ADMIN,
    bank_account_of,
    float_param,
    gl_balance,
    post_treasury_move,
    require_other_person,
    require_role,
    treasury_account,
    treasury_alert,
)

# BRU-TRE-24 / AUT-TRE-21: an LC or guarantee inside this many days of expiry
# alerts treasury daily until acknowledged. The spec says "the configured
# expiry window" without a value; default 30 days.
PARAM_EXPIRY_WINDOW = "cd_cash_position.lc_expiry_window_days"
DEFAULT_EXPIRY_WINDOW = 30
EXPIRY_ALERTED = ("lc", "bank_guarantee")

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
FACILITY_TERMS = (
    "lender_id",
    "facility_type",
    "currency_id",
    "limit_amount",
    "interest_rate",
    "principal",
    "start_date",
    "tenor_months",
    "repayment_frequency",
    "liability_account_id",
    "journal_id",
    "company_id",
)
REPAYMENT_TERMS = ("facility_id", "sequence", "due_date", "principal", "interest")


def annuity_lines(principal, rate_pa, periods, first_due, step_months, first_seq=1):
    """Equal-instalment (annuity) schedule rows."""
    rate = (rate_pa or 0.0) / 100.0 * step_months / 12.0
    periods = max(int(periods), 1)
    instalment = principal * rate / (1 - (1 + rate) ** (-periods)) if rate else principal / periods
    balance = principal
    rows = []
    for n in range(periods):
        interest = round(balance * rate, 2)
        part = round(instalment - interest, 2) if n < periods - 1 else round(balance, 2)
        balance = round(balance - part, 2)
        rows.append(
            {
                "sequence": first_seq + n,
                "due_date": first_due + relativedelta(months=step_months * n),
                "principal": part,
                "interest": interest,
            }
        )
    return rows


class FixBankFacility(models.Model):
    _name = "fix.bank.facility"
    _description = "Bank Facility"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
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
    amendment_ids = fields.One2many("fix.facility.amendment", "facility_id", string="Amendments")
    expiry_ack_by_id = fields.Many2one(
        "res.users", string="Expiry Alert Acknowledged By", readonly=True, copy=False
    )
    expiry_ack_at = fields.Datetime(string="Expiry Alert Acknowledged", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "repayment_ids",
            "expiry_ack_by_id",
            "expiry_ack_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(f.state != "draft" for f in self):
            locked |= set(FACILITY_TERMS)
        return locked

    def write(self, vals):
        if self and not (self.env.su or self._fix_guard_has_token()):
            terms = set(FACILITY_TERMS) & set(vals)
            for fac in self.filtered(lambda f: f.state != "draft"):
                changed = [f for f in terms if fac._fix_guard_differs(f, vals[f], fac[f])]
                if changed:
                    raise UserError(
                        "%s is %s: its sanctioned terms (%s) change only through an approved "
                        "amendment." % (fac.name, fac.state, ", ".join(changed))
                    )
        return super().write(vals)

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

    @api.model
    def _cron_expiry_alerts(self):
        """AUT-TRE-21 (ir.cron, daily): an active LC or bank guarantee inside
        the expiry window alerts the Accounting Administrators every day until
        someone acknowledges it."""
        window = int(float_param(self.env, PARAM_EXPIRY_WINDOW, DEFAULT_EXPIRY_WINDOW))
        today = fields.Date.context_today(self)
        due = self.sudo().search(
            [
                ("state", "=", "active"),
                ("facility_type", "in", EXPIRY_ALERTED),
                ("expiry_date", "!=", False),
                ("expiry_date", "<=", today + relativedelta(days=window)),
                ("expiry_ack_at", "=", False),
            ]
        )
        for fac in due:
            left = (fac.expiry_date - today).days
            treasury_alert(
                fac,
                "LC / guarantee expiry",
                "%s (%s, limit %.2f) expires on %s — %s day(s) left."
                % (fac.name, fac.facility_type, fac.limit_amount, fac.expiry_date, left),
                deadline=fac.expiry_date,
            )
        return len(due)

    def action_acknowledge_expiry(self):
        """Stops the daily expiry alert (an Accounting Administrator)."""
        require_role(self.env, GROUP_ADMIN, "Acknowledging an LC / guarantee expiry")
        for fac in self:
            fac._guarded().write(
                {"expiry_ack_by_id": self.env.uid, "expiry_ack_at": fields.Datetime.now()}
            )
            fac.sudo().activity_ids.filtered(
                lambda a: a.summary == "LC / guarantee expiry"
            ).action_feedback(feedback="Acknowledged by %s" % self.env.user.name)
        return True

    def action_activate(self):
        require_role(self.env, GROUP_ADMIN, "Activating a bank facility")
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
            fac._guarded().write({"state": "active"})
        return True

    def action_close(self):
        require_role(self.env, GROUP_ADMIN, "Closing a bank facility")
        for fac in self:
            if fac.repayment_ids.filtered(lambda r: r.state == "planned"):
                raise UserError("%s still has unpaid instalments." % fac.name)
            fac._guarded().write({"state": "closed"})
        return True

    def action_generate_schedule(self):
        """Equal-instalment (annuity) schedule over the tenor at the
        facility's rate, on a DRAFT facility. Once active the schedule is
        frozen; an approved amendment re-schedules it."""
        require_role(self.env, GROUP_ADMIN, "Generating a facility schedule")
        for fac in self:
            if fac.facility_type not in AMORTISING:
                raise UserError("Only term / short-term loans carry an instalment schedule.")
            if fac.state != "draft":
                raise UserError(
                    "%s is %s: its schedule changes only through an approved amendment."
                    % (fac.name, fac.state)
                )
            if fac.repayment_ids.filtered(lambda r: r.state == "paid"):
                raise UserError("Instalments are already paid — the schedule is not regenerated.")
            if not (fac.principal > 0 and fac.tenor_months > 0 and fac.start_date):
                raise UserError("Set the principal, tenor and first instalment date first.")
            step = 3 if fac.repayment_frequency == "quarterly" else 1
            rows = annuity_lines(
                fac.principal, fac.interest_rate, fac.tenor_months // step, fac.start_date, step
            )
            fac._fix_replace_unpaid(rows)
        return True

    def _fix_replace_unpaid(self, rows):
        self.ensure_one()
        self.repayment_ids.filtered(lambda r: r.state == "planned").sudo()._guarded().unlink()
        self._guarded().write({"repayment_ids": [(0, 0, row) for row in rows]})


class FixFacilityRepayment(models.Model):
    _name = "fix.facility.repayment"
    _description = "Facility Repayment Instalment"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
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

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "paid_date", "move_id", *REPAYMENT_TERMS}

    @api.model_create_multi
    def create(self, vals_list):
        if not (self.env.su or self._fix_guard_has_token()):
            raise UserError(
                "Instalments come from the facility's schedule (or an approved amendment)."
            )
        return super().create(vals_list)

    def unlink(self):
        if not (self.env.su or self._fix_guard_has_token()):
            raise UserError("Scheduled instalments are not deleted; amend the facility instead.")
        return super().unlink()

    @api.depends("principal", "interest")
    def _compute_total(self):
        for r in self:
            r.total = r.principal + r.interest

    def _compute_overdue(self):
        today = fields.Date.context_today(self)
        for r in self:
            r.is_overdue = r.state == "planned" and r.due_date and r.due_date < today

    def action_pay(self):
        """Dr loan liability (principal) + Dr interest expense / Cr bank, at
        the scheduled amounts, in schedule order, by an Accounting
        Administrator."""
        require_role(self.env, GROUP_ADMIN, "Paying a loan instalment")
        for r in self:
            if r.state != "planned":
                raise UserError("This instalment is already paid.")
            fac = r.facility_id
            earlier = fac.repayment_ids.filtered(
                lambda x, r=r: (
                    x.state == "planned" and (x.due_date, x.sequence) < (r.due_date, r.sequence)
                )
            )
            if earlier:
                raise UserError(
                    "Instalment #%s is paid after #%s: instalments are paid in schedule order."
                    % (r.sequence, earlier.sorted("due_date")[:1].sequence)
                )
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
            r._guarded().write(
                {"state": "paid", "paid_date": fields.Date.context_today(self), "move_id": move.id}
            )
        return True


class FixFacilityAmendment(models.Model):
    """A change to an active facility's terms: requested by one person,
    approved by a different Accounting Administrator, then applied (the
    unpaid instalments re-scheduled on the outstanding principal)."""

    _name = "fix.facility.amendment"
    _description = "Facility Amendment"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "id desc"

    facility_id = fields.Many2one(
        "fix.bank.facility", required=True, index=True, ondelete="cascade"
    )
    company_id = fields.Many2one(related="facility_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="facility_id.operating_unit_id", store=True, index=True
    )
    currency_id = fields.Many2one(related="facility_id.currency_id")
    reason = fields.Char(required=True, help="Lender letter / board approval reference")
    new_limit_amount = fields.Monetary(
        currency_field="currency_id", help="Empty: the sanctioned limit is unchanged"
    )
    new_interest_rate = fields.Float(digits=(6, 3), help="Empty: unchanged")
    new_instalments = fields.Integer(
        string="Remaining Instalments", help="Empty: as many as are still unpaid"
    )
    new_next_due_date = fields.Date(help="Empty: the next unpaid instalment's date")
    state = fields.Selection(
        [("draft", "Requested"), ("approved", "Approved & Applied"), ("rejected", "Rejected")],
        default="draft",
        required=True,
        tracking=True,
    )
    requested_by_id = fields.Many2one(
        "res.users", default=lambda self: self.env.user, readonly=True, copy=False
    )
    approved_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    approved_at = fields.Datetime(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "requested_by_id",
            "approved_by_id",
            "approved_at",
        }

    def write(self, vals):
        decided = any(a.state != "draft" for a in self)
        trusted = self.env.su or self._fix_guard_has_token()
        if decided and not trusted and set(vals) - {"message_main_attachment_id"}:
            raise UserError("A decided amendment is a record of what was approved.")
        return super().write(vals)

    def action_approve(self):
        require_role(self.env, GROUP_ADMIN, "Approving a facility amendment")
        for am in self:
            if am.state != "draft":
                raise UserError("Only a requested amendment is approved.")
            require_other_person(
                self.env,
                am.requested_by_id | am.create_uid,
                "Approving amendment of %s" % (am.facility_id.name),
            )
            am._fix_apply()
            am._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.uid,
                    "approved_at": fields.Datetime.now(),
                }
            )
        return True

    def action_reject(self):
        require_role(self.env, GROUP_ADMIN, "Rejecting a facility amendment")
        self.filtered(lambda a: a.state == "draft")._guarded().write({"state": "rejected"})
        return True

    def _fix_apply(self):
        self.ensure_one()
        fac = self.facility_id.sudo()
        vals = {}
        if self.new_limit_amount:
            vals["limit_amount"] = self.new_limit_amount
        if self.new_interest_rate:
            vals["interest_rate"] = self.new_interest_rate
        if vals:
            fac._guarded().write(vals)
        if fac.facility_type in AMORTISING and (
            self.new_interest_rate or self.new_instalments or self.new_next_due_date
        ):
            unpaid = fac.repayment_ids.filtered(lambda r: r.state == "planned").sorted("due_date")
            outstanding = round(sum(unpaid.mapped("principal")), 2)
            if outstanding <= 0.005:
                raise UserError("%s has no unpaid principal to re-schedule." % fac.name)
            step = 3 if fac.repayment_frequency == "quarterly" else 1
            paid = fac.repayment_ids - unpaid
            rows = annuity_lines(
                outstanding,
                fac.interest_rate,
                self.new_instalments or len(unpaid),
                self.new_next_due_date or unpaid[:1].due_date,
                step,
                first_seq=(max(paid.mapped("sequence")) if paid else 0) + 1,
            )
            fac._fix_replace_unpaid(rows)
        fac.message_post(body="Amendment applied: %s." % self.reason)


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
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
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
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved")],
        default="draft",
        required=True,
        tracking=True,
    )
    approved_by_id = fields.Many2one("res.users", readonly=True, copy=False)

    _COVENANT_TERMS = ("facility_id", "metric", "operator", "threshold")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "approved_by_id",
            "last_value",
            "last_result",
            "last_tested",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(c.state != "draft" for c in self):
            locked |= set(self._COVENANT_TERMS)
        return locked

    def write(self, vals):
        if self and not (self.env.su or self._fix_guard_has_token()):
            terms = set(self._COVENANT_TERMS) & set(vals)
            for cov in self.filtered(lambda c: c.state != "draft"):
                changed = [f for f in terms if cov._fix_guard_differs(f, vals[f], cov[f])]
                if changed:
                    raise UserError(
                        "Covenant %s was approved: %s cannot change. Record the lender's new "
                        "covenant as a new one." % (cov.name, ", ".join(changed))
                    )
        return super().write(vals)

    def action_approve(self):
        """An Accounting Administrator other than the one who set it agrees the
        covenant with the sanction letter."""
        require_role(self.env, GROUP_ADMIN, "Approving a covenant")
        for cov in self:
            if cov.state != "draft":
                raise UserError("Covenant %s is already approved." % cov.name)
            require_other_person(
                self.env, cov.create_uid | cov.write_uid, "Approving %s" % cov.name
            )
            cov._guarded().write({"state": "approved", "approved_by_id": self.env.uid})
        return True

    @api.model
    def _cron_test_covenants(self):
        """Scheduled covenant tests (ir.cron): every approved covenant of an
        active facility."""
        covenants = self.sudo().search(
            [("state", "=", "approved"), ("facility_id.state", "=", "active")]
        )
        covenants.action_test()
        return len(covenants)

    def action_test(self):
        require_role(self.env, GROUP_ACCOUNTANT, "Testing a covenant")
        today = fields.Date.context_today(self)
        for cov in self:
            if cov.state != "approved":
                raise UserError("Covenant %s is not approved: it is not tested." % cov.name)
            value = covenant_metric(self.env, cov.facility_id, cov.metric, today)
            if value is None:
                result = "na"
            elif cov.operator == "ge":
                result = "pass" if value >= cov.threshold else "breach"
            else:
                result = "pass" if value <= cov.threshold else "breach"
            self.env["fix.covenant.test"].sudo()._guarded().create(
                {
                    "covenant_id": cov.id,
                    "tested_on": today,
                    "value": value or 0.0,
                    "threshold": cov.threshold,
                    "result": result,
                }
            )
            cov.sudo()._guarded().write(
                {"last_value": value or 0.0, "last_result": result, "last_tested": today}
            )
            if result == "breach":
                cov.sudo().message_post(
                    body="Covenant breached: %s = %s (limit %s)" % (cov.name, value, cov.threshold)
                )
        return True


class FixCovenantTest(models.Model):
    _name = "fix.covenant.test"
    _description = "Covenant Test Result"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
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

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_has_token():
            raise UserError("Covenant test results are written by the covenant test only.")
        return super().create(vals_list)

    def write(self, vals):
        if set(vals) - {"message_main_attachment_id"} and not self._fix_guard_has_token():
            raise UserError("A covenant test result is evidence and is never edited.")
        return super().write(vals)

    def unlink(self):
        raise UserError("A covenant test result is evidence and is never deleted.")


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
