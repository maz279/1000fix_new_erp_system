# fix_lease — M49 leases under IFRS 16 (branch rents).
#
# Commencement: lease liability = PV of the fixed monthly payments at the
# incremental borrowing rate (IFRS 16.26); right-of-use asset = liability +
# payments made at/before commencement + initial direct costs (16.24). The
# ROU asset is registered as a fix.fixed.asset (no tax class: rent is
# deducted as paid), so the monthly depreciation run charges it straight-line
# over the lease term. Each month: interest accretes on the liability
# (Dr interest / Cr liability) and the rent payment reduces it (Dr liability /
# Cr rent payable clearing — AP settles it with TDS/VDS). Short-term and
# low-value leases (16.5) are expensed through AP and get no ROU.
#
# A07 ERP audit (2026-11-20, owner decision D5): the liability is measured on
# the ESCALATED payment schedule and the contract's payment frequency (16.27),
# not a flat rent; every entry carries the lease's branch (never the first
# operating unit); a modification is remeasured (16.39-46: revised PV at the
# revised rate, ROU adjusted, remaining schedule rebuilt) and a termination
# derecognises the ROU asset and the liability with the gain or loss; due
# months post from a daily job on the Dhaka month end.
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_asset_common import (
    USER_GROUP,
    add_months,
    assert_period_open,
    dhaka_today,
    money,
    month_end,
    month_start,
    post_entry,
    require_accounts,
    require_group,
)

_logger = logging.getLogger(__name__)

PAYMENT_FREQUENCIES = [
    ("1", "Monthly"),
    ("3", "Quarterly"),
    ("6", "Half-Yearly"),
    ("12", "Yearly"),
]


def lease_present_value(payment: float, months: int, monthly_rate: float, advance: bool) -> float:
    """PV of `months` equal payments at `monthly_rate` (annuity; annuity-due
    when paid in advance)."""
    if months <= 0:
        raise ValueError("lease term must be positive months")
    if monthly_rate <= 0.0:
        return money(payment * months)
    annuity = payment * (1.0 - (1.0 + monthly_rate) ** -months) / monthly_rate
    if advance:
        annuity *= 1.0 + monthly_rate
    return money(annuity)


def lease_schedule(
    liability: float, payment: float, months: int, monthly_rate: float, advance: bool
):
    """Effective-interest schedule. Each row: opening, payment, interest,
    principal, closing. The last row absorbs rounding so the liability ends
    at exactly zero."""
    rows, opening = [], money(liability)
    for i in range(1, months + 1):
        base = opening - payment if advance else opening
        interest = money(base * monthly_rate)
        closing = money(opening + interest - payment)
        if i == months:
            interest = money(payment - opening)
            closing = 0.0
        rows.append(
            {
                "sequence": i,
                "opening": opening,
                "payment": money(payment),
                "interest": interest,
                "principal": money(payment - interest),
                "closing": closing,
            }
        )
        opening = closing
    return rows


def lease_payment_vector(
    rent: float,
    months: int,
    advance: bool,
    frequency_months: int = 1,
    escalation_pct: float = 0.0,
    escalation_every: int = 12,
):
    """The contract's payments, one slot per lease month (0.0 in a month with
    no payment). `rent` is the monthly rent of the first lease year; it
    escalates by `escalation_pct` every `escalation_every` months (fixed or
    in-substance fixed escalations: IFRS 16.27). A payment covers
    `frequency_months` months: paid in the first month of its period in
    advance, in the last month in arrears (the final period may be short)."""
    if months <= 0:
        raise ValueError("lease term must be positive months")
    k = max(int(frequency_months or 1), 1)
    every = max(int(escalation_every or 12), 1)
    monthly = [
        money(rent * (1.0 + (escalation_pct or 0.0) / 100.0) ** ((i - 1) // every))
        for i in range(1, months + 1)
    ]
    payments = [0.0] * months
    for start in range(0, months, k):
        period = monthly[start : start + k]
        slot = start if advance else start + len(period) - 1
        payments[slot] = money(sum(period))
    return payments


def lease_present_value_vector(payments, monthly_rate: float, advance: bool) -> float:
    """PV of a payment vector: a month's payment is discounted from the start
    of its month (advance) or from its end (arrears)."""
    if not payments:
        raise ValueError("lease term must be positive months")
    if monthly_rate <= 0.0:
        return money(sum(payments))
    total = 0.0
    for i, pay in enumerate(payments, start=1):
        if pay:
            total += pay * (1.0 + monthly_rate) ** -((i - 1) if advance else i)
    return money(total)


def lease_schedule_vector(liability: float, payments, monthly_rate: float, advance: bool):
    """Effective-interest schedule over a payment vector. The row of the last
    payment absorbs rounding so the liability ends at exactly zero; a month
    after it carries nothing."""
    rows, opening = [], money(liability)
    last = max((i for i, pay in enumerate(payments, start=1) if pay), default=len(payments))
    for i, pay in enumerate(payments, start=1):
        pay = money(pay)
        if i > last:
            interest, closing = 0.0, 0.0
        else:
            base = opening - pay if advance else opening
            interest = money(base * monthly_rate)
            closing = money(opening + interest - pay)
            if i == last:
                interest = money(pay - opening)
                closing = 0.0
        rows.append(
            {
                "sequence": i,
                "opening": opening,
                "payment": pay,
                "interest": interest,
                "principal": money(pay - interest),
                "closing": closing,
            }
        )
        opening = closing
    return rows


class FixLease(models.Model):
    _name = "fix.lease"
    _description = "Lease Contract (IFRS 16)"
    _inherit = ["fix.guarded.mixin", "mail.thread", "mail.activity.mixin"]
    _order = "commencement_date desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Branch", tracking=True)
    reference = fields.Char(string="Reference", readonly=True, copy=False, default="/")
    name = fields.Char(string="Lease", required=True, tracking=True)
    partner_id = fields.Many2one("res.partner", string="Lessor", tracking=True)
    category_id = fields.Many2one(
        "fix.asset.category",
        string="Right-of-Use Category",
        tracking=True,
        help="Asset category of the right-of-use asset (its asset, accumulated "
        "depreciation and depreciation expense accounts and journal are used).",
    )
    commencement_date = fields.Date(string="Commencement Date", required=True, tracking=True)
    term_months = fields.Integer(string="Lease Term (Months)", required=True, tracking=True)
    end_date = fields.Date(string="End Date", compute="_compute_end_date", store=True)
    currency_id = fields.Many2one(related="company_id.currency_id")
    payment_amount = fields.Monetary(
        string="Monthly Rent (Gross)",
        required=True,
        tracking=True,
        help="Fixed monthly payment before TDS/VDS withholding (withholding is "
        "paid to NBR on the lessor's behalf, so it is part of the lease payment).",
    )
    payment_timing = fields.Selection(
        [("advance", "In Advance"), ("arrears", "In Arrears")],
        string="Payment Timing",
        default="advance",
        required=True,
    )
    payment_frequency = fields.Selection(
        PAYMENT_FREQUENCIES,
        string="Payment Frequency",
        default="1",
        required=True,
        tracking=True,
        help="How often the rent is paid; each payment covers that many months of rent.",
    )
    escalation_percent = fields.Float(
        string="Fixed Escalation % per Step",
        digits=(6, 3),
        tracking=True,
        help="Contractual (fixed) rent escalation, measured in the liability (IFRS 16.27). "
        "An index-linked (CPI) escalation is measured at the current rate (16.28): leave 0.",
    )
    escalation_interval_months = fields.Integer(
        string="Escalation Every (Months)", default=12, tracking=True
    )
    ibr_percent = fields.Float(
        string="Incremental Borrowing Rate % a Year", required=True, digits=(6, 3), tracking=True
    )
    prepaid_payments = fields.Monetary(
        string="Payments Before Commencement",
        help="Rent advance already paid that is NOT refundable (refundable security "
        "deposits are a receivable, not part of the ROU asset).",
    )
    initial_direct_costs = fields.Monetary(string="Initial Direct Costs")
    exemption = fields.Selection(
        [
            ("none", "None — On Balance Sheet"),
            ("short_term", "Short-Term (12 Months or Less)"),
            ("low_value", "Low-Value Asset"),
        ],
        string="IFRS 16 Exemption",
        default="none",
        required=True,
    )
    liability_account_id = fields.Many2one("account.account", string="Lease Liability Account")
    interest_account_id = fields.Many2one("account.account", string="Interest Expense Account")
    payment_account_id = fields.Many2one(
        "account.account",
        string="Rent Payable / Clearing Account",
        help="Credited with each rent payment (and with prepaid rent and direct "
        "costs at commencement); AP settles it with TDS/VDS.",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("ended", "Ended")],
        default="draft",
        required=True,
        tracking=True,
    )
    pv_preview = fields.Monetary(string="Present Value (Preview)", compute="_compute_preview")
    initial_liability = fields.Monetary(string="Initial Lease Liability", readonly=True, copy=False)
    rou_amount = fields.Monetary(string="Right-of-Use Asset", readonly=True, copy=False)
    asset_id = fields.Many2one("fix.fixed.asset", string="ROU Asset", readonly=True, copy=False)
    move_id = fields.Many2one("account.move", string="Recognition Entry", readonly=True, copy=False)
    schedule_line_ids = fields.One2many("fix.lease.schedule.line", "lease_id", string="Schedule")
    liability_balance = fields.Monetary(string="Liability Balance", compute="_compute_balances")
    interest_to_date = fields.Monetary(string="Interest to Date", compute="_compute_balances")
    terminated_on = fields.Date(string="Terminated On", readonly=True, copy=False)
    termination_move_id = fields.Many2one(
        "account.move", string="Derecognition Entry", readonly=True, copy=False
    )

    # A08 M49-4 (probe 62): rent and IBR were changed after recognition with no
    # remeasurement (IFRS 16.39). Once recognised, the terms are frozen; a
    # change goes through _fix_remeasure (A07 D5c), never an edit.
    _TERMS = frozenset(
        {
            "commencement_date",
            "term_months",
            "payment_amount",
            "payment_timing",
            "payment_frequency",
            "escalation_percent",
            "escalation_interval_months",
            "ibr_percent",
            "prepaid_payments",
            "initial_direct_costs",
            "exemption",
            "category_id",
            "liability_account_id",
            "interest_account_id",
            "payment_account_id",
            "company_id",
        }
    )

    def _fix_guarded_fields(self) -> set:
        # M49-1 (probe 60): 'active' was written with no liability, ROU or JE
        return super()._fix_guarded_fields() | {
            "state",
            "initial_liability",
            "rou_amount",
            "asset_id",
            "move_id",
            "terminated_on",
            "termination_move_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= set(self._TERMS)
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open() and set(vals) & self._TERMS:
            done = self.filtered(lambda r: r.state != "draft")
            if any(
                r._fix_guard_differs(n, vals[n], r[n])
                for r in done
                for n in set(vals) & self._TERMS
            ):
                raise UserError(
                    self.env._(
                        "%s is recognised: its terms are frozen (IFRS 16.39 — a change is a "
                        "remeasurement, not an edit).",
                        done[:1].name,
                    )
                )
        return super().write(vals)

    @api.depends("commencement_date", "term_months")
    def _compute_end_date(self):
        for rec in self:
            rec.end_date = (
                month_end(add_months(rec.commencement_date, rec.term_months - 1))
                if rec.commencement_date and rec.term_months > 0
                else False
            )

    @api.depends(
        "payment_amount",
        "term_months",
        "ibr_percent",
        "payment_timing",
        "payment_frequency",
        "escalation_percent",
        "escalation_interval_months",
    )
    def _compute_preview(self):
        for rec in self:
            try:
                rec.pv_preview = rec._fix_present_value(rec._fix_payment_vector(), rec.ibr_percent)
            except ValueError:
                rec.pv_preview = 0.0

    @api.depends("initial_liability", "schedule_line_ids.state")
    def _compute_balances(self):
        for rec in self:
            posted = rec.schedule_line_ids.filtered(lambda ln: ln.state == "posted")
            last = posted.sorted("sequence")[-1:] if posted else posted
            rec.liability_balance = last.closing if last else rec.initial_liability
            rec.interest_to_date = money(sum(posted.mapped("interest")))

    # ---- the payment schedule (A07 D5b) -------------------------------------
    def _fix_is_flat(self) -> bool:
        self.ensure_one()
        return (self.payment_frequency or "1") == "1" and not self.escalation_percent

    def _fix_payment_vector(self):
        """One payment slot per lease month under the contract's terms. The
        M47 bridge overrides it with the estate rent schedule when it has one."""
        self.ensure_one()
        return lease_payment_vector(
            self.payment_amount,
            self.term_months,
            self.payment_timing == "advance",
            int(self.payment_frequency or "1"),
            self.escalation_percent,
            self.escalation_interval_months or 12,
        )

    def _fix_present_value(self, payments, ibr_percent) -> float:
        self.ensure_one()
        rate = (ibr_percent or 0.0) / 100.0 / 12.0
        advance = self.payment_timing == "advance"
        if len(set(payments)) == 1:
            # flat monthly rent: the closed form, identical to the figures
            # recognised before the escalated schedule existed
            return lease_present_value(payments[0], len(payments), rate, advance)
        return lease_present_value_vector(payments, rate, advance)

    def _fix_schedule_rows(self, liability, payments, ibr_percent):
        self.ensure_one()
        rate = (ibr_percent or 0.0) / 100.0 / 12.0
        advance = self.payment_timing == "advance"
        if len(set(payments)) == 1:
            return lease_schedule(liability, payments[0], len(payments), rate, advance)
        return lease_schedule_vector(liability, payments, rate, advance)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("reference", "/") == "/":
                vals["reference"] = self.env["ir.sequence"].next_by_code("fix.lease") or "/"
        return super().create(vals_list)

    @api.constrains(
        "term_months", "payment_amount", "ibr_percent", "exemption", "escalation_interval_months"
    )
    def _check_terms(self):
        for rec in self:
            if rec.term_months <= 0:
                raise ValidationError(self.env._("The lease term must be at least one month."))
            if rec.payment_amount <= 0:
                raise ValidationError(self.env._("The monthly rent must be above zero."))
            if not 0.0 <= rec.ibr_percent < 100.0:
                raise ValidationError(self.env._("The borrowing rate must be from 0% to 99.99%."))
            if rec.exemption == "short_term" and rec.term_months > 12:
                raise ValidationError(
                    self.env._("A short-term lease runs 12 months or less (IFRS 16 Appendix A).")
                )
            if rec.escalation_interval_months < 0:
                raise ValidationError(self.env._("The escalation interval cannot be negative."))

    def action_activate(self):
        """Commencement: build the schedule, register the ROU asset and post
        Dr ROU / Cr lease liability (+ Cr clearing for prepaid rent and
        direct costs), on the lease's branch."""
        require_group(self.env, USER_GROUP, "Activating a lease")
        for rec in self:
            if rec.state != "draft":
                raise UserError(self.env._("Only draft leases can be activated."))
            if rec.exemption != "none":
                raise UserError(
                    self.env._(
                        "%s is exempt (IFRS 16.5): its rent is expensed through AP — no "
                        "right-of-use asset is recognised.",
                        rec.name,
                    )
                )
            if not rec.category_id:
                raise UserError(self.env._("Choose the right-of-use category of %s.", rec.name))
            if not rec.operating_unit_id:
                raise UserError(
                    self.env._(
                        "%s has no branch: an IFRS 16 lease is booked on its branch, never on "
                        "the company's first operating unit. Set the branch first.",
                        rec.name,
                    )
                )
            require_accounts(
                rec.category_id, ["journal_id", "asset_account_id"], "Lease recognition"
            )
            needed = ["liability_account_id", "interest_account_id", "payment_account_id"]
            require_accounts(rec, needed, "Lease recognition")
            payments = rec._fix_payment_vector()
            if len(payments) != rec.term_months or not any(payments):
                raise UserError(self.env._("%s has no payment to measure.", rec.name))
            liability = rec._fix_present_value(payments, rec.ibr_percent)
            upfront = money(rec.prepaid_payments + rec.initial_direct_costs)
            rou = money(liability + upfront)
            rows = rec._fix_schedule_rows(liability, payments, rec.ibr_percent)
            per_month = money(rou / rec.term_months)
            start = month_start(rec.commencement_date)
            vals = []
            for row in rows:
                dep = (
                    money(rou - per_month * (rec.term_months - 1))
                    if row["sequence"] == rec.term_months
                    else per_month
                )
                vals.append(
                    dict(
                        row,
                        lease_id=rec.id,
                        period_start=add_months(start, row["sequence"] - 1),
                        depreciation=dep,
                    )
                )
            assert_period_open(
                self.env, rec.company_id, rec.commencement_date, "IFRS 16 recognition"
            )
            self.env["fix.lease.schedule.line"].sudo().create(vals)
            lines = [
                (rec.category_id.asset_account_id, rou, 0.0, rec.name),
                (rec.liability_account_id, 0.0, liability, rec.name),
                (rec.payment_account_id, 0.0, upfront, rec.name),
            ]
            move = post_entry(
                self.env,
                rec.company_id,
                rec.category_id.journal_id,
                rec.commencement_date,
                "IFRS 16 recognition: %s" % rec.name,
                lines,
                rec.operating_unit_id,
            )
            asset = (
                self.env["fix.fixed.asset"]
                ._guarded()
                .create(
                    {
                        "company_id": rec.company_id.id,
                        "operating_unit_id": rec.operating_unit_id.id,
                        "name": "ROU — %s" % rec.name,
                        "category_id": rec.category_id.id,
                        "gross": rou,
                        "salvage": 0.0,
                        "life_months": rec.term_months,
                        "purchase_date": rec.commencement_date,
                        "lease_id": rec.id,
                    }
                )
            )
            asset._fix_activate_from_source(move)
            rec._guarded().write(
                {
                    "state": "active",
                    "initial_liability": liability,
                    "rou_amount": rou,
                    "asset_id": asset.id,
                    "move_id": move.id,
                }
            )
        return True

    def action_post_due(self):
        """Post every schedule month up to the current (Dhaka) month, in order."""
        today = month_start(dhaka_today(self.env))
        for rec in self:
            if rec.state != "active":
                raise UserError(self.env._("Only active leases post monthly entries."))
            due = rec.schedule_line_ids.filtered(
                lambda ln: ln.state == "draft" and ln.period_start <= today
            ).sorted("sequence")
            if not due:
                raise UserError(self.env._("%s has no unposted month due.", rec.name))
            due.action_post()
        return True

    @api.model
    def _cron_post_due_months(self):
        """A07 D5(g): post every active lease's months whose month end (Dhaka)
        has been reached, in order. A lease that cannot post (a closed period,
        an account missing) is skipped with the reason on its chatter; the
        others still post. Idempotent: a posted month is never posted again."""
        today = dhaka_today(self.env)
        posted = self.env["fix.lease.schedule.line"]
        for lease in self.sudo().search([("state", "=", "active")]):
            due = lease.schedule_line_ids.filtered(
                lambda ln: ln.state == "draft" and month_end(ln.period_start) <= today
            ).sorted("sequence")
            for line in due:
                try:
                    with self.env.cr.savepoint():
                        line.action_post()
                except UserError as exc:
                    text = "Monthly IFRS 16 job: month %s not posted: %s" % (line.sequence, exc)
                    _logger.warning("%s: %s", lease.name, text)
                    if text not in (lease.message_ids[:1].body or ""):
                        lease.message_post(body=text)
                    break
                posted |= line
        return posted

    # ---- remeasurement and termination (A07 D5c) ------------------------------
    def _fix_open_months(self, effective):
        """The posted months strictly before `effective` and the unposted ones
        from it: every earlier month is posted, no later one is."""
        self.ensure_one()
        lines = self.schedule_line_ids.sorted("sequence")
        before = lines.filtered(lambda ln: ln.period_start < effective)
        after = lines - before
        if before.filtered(lambda ln: ln.state != "posted"):
            raise UserError(
                self.env._("Post the months of %s before %s first.", self.name, effective)
            )
        if after.filtered(lambda ln: ln.state == "posted"):
            raise UserError(
                self.env._(
                    "%s is already posted on or after %s: a change takes effect from the "
                    "first unposted month.",
                    self.name,
                    effective,
                )
            )
        return before, after

    def _fix_carrying_liability(self, posted):
        self.ensure_one()
        if not posted:
            return money(self.initial_liability)
        return money(posted.sorted("sequence")[-1].closing)

    def _fix_remeasure(self, effective, terms, reason):
        """IFRS 16.39-46: remeasure the liability from `effective` (its month
        start) at the revised terms and rate; the difference adjusts the ROU
        asset (a decrease beyond its carrying amount goes to profit or loss),
        the remaining schedule is rebuilt and the ROU asset re-spread over the
        remaining term. Returns the adjustment entry (empty when the liability
        does not change)."""
        self.ensure_one()
        require_group(self.env, USER_GROUP, "Remeasuring a lease")
        if self.state != "active":
            raise UserError(self.env._("Only an active lease is remeasured."))
        allowed = {
            "payment_amount",
            "term_months",
            "ibr_percent",
            "escalation_percent",
            "escalation_interval_months",
            "payment_frequency",
        }
        unknown = set(terms) - allowed
        if unknown:
            raise UserError(self.env._("%s cannot be remeasured.", ", ".join(sorted(unknown))))
        effective = month_start(effective)
        posted, _rest = self._fix_open_months(effective)
        done = len(posted)
        carrying = self._fix_carrying_liability(posted)
        new_term = int(terms.get("term_months") or self.term_months)
        if new_term <= done:
            raise UserError(
                self.env._(
                    "The revised term (%s months) ends before the first unposted month: "
                    "terminate the lease instead.",
                    new_term,
                )
            )
        ibr = terms.get("ibr_percent") or self.ibr_percent
        if not ibr or ibr <= 0:
            raise UserError(self.env._("A remeasurement needs the revised borrowing rate."))
        self._guarded().write(dict(terms))
        payments = self._fix_payment_vector()[done:]
        new_liability = self._fix_present_value(payments, ibr)
        delta = money(new_liability - carrying)
        asset = self.asset_id
        cat = self.category_id
        label = "IFRS 16 remeasurement: %s (%s)" % (self.name, reason or "-")
        move = self.env["account.move"]
        gross_delta = delta
        if delta:
            if delta > 0:
                lines = [
                    (cat.asset_account_id, delta, 0.0, label),
                    (self.liability_account_id, 0.0, delta, label),
                ]
            else:
                nbv = money(asset.book_nbv) if asset else 0.0
                reduce = money(min(-delta, max(nbv, 0.0)))
                gross_delta = -reduce
                lines = [
                    (self.liability_account_id, -delta, 0.0, label),
                    (cat.asset_account_id, 0.0, reduce, label),
                ]
                if money(-delta - reduce):
                    require_accounts(cat, ["gain_account_id"], "Lease remeasurement")
                    lines.append((cat.gain_account_id, 0.0, money(-delta - reduce), label))
            move = post_entry(
                self.env,
                self.company_id,
                cat.journal_id,
                effective,
                label,
                lines,
                self.operating_unit_id,
            )
        rows = self._fix_schedule_rows(new_liability, payments, ibr)
        months_left = new_term - done
        rou_left = money((asset.book_nbv if asset else 0.0) + gross_delta)
        per_month = money(rou_left / months_left)
        self.schedule_line_ids.filtered(lambda ln: ln.state == "draft").sudo().unlink()
        vals = []
        for row in rows:
            seq = done + row["sequence"]
            dep = (
                money(rou_left - per_month * (months_left - 1))
                if row["sequence"] == months_left
                else per_month
            )
            vals.append(
                dict(
                    row,
                    sequence=seq,
                    lease_id=self.id,
                    period_start=add_months(month_start(self.commencement_date), seq - 1),
                    depreciation=dep,
                )
            )
        self.env["fix.lease.schedule.line"].sudo().create(vals)
        if asset:
            asset._guarded().write(
                {
                    "gross": money(asset.gross + gross_delta),
                    "life_months": asset.book_months_done + months_left,
                }
            )
        self.message_post(
            body=self.env._(
                "Remeasured from %(eff)s (%(why)s): liability %(old)s -> %(new)s, ROU "
                "adjusted by %(adj)s; %(n)s month(s) rebuilt.",
                eff=effective,
                why=reason or "-",
                old=carrying,
                new=new_liability,
                adj=gross_delta,
                n=months_left,
            )
        )
        return move

    def _fix_terminate(self, on_date, reason):
        """Early termination (IFRS 16.46(a), a full decrease in scope): the ROU
        asset and the liability are derecognised and the difference is a gain
        or a loss. Every month before the termination month is posted first;
        the remaining months are cancelled."""
        self.ensure_one()
        require_group(self.env, USER_GROUP, "Terminating a lease")
        if self.state != "active":
            raise UserError(self.env._("Only an active lease is terminated."))
        posted, _rest = self._fix_open_months(month_start(on_date))
        liability = self._fix_carrying_liability(posted)
        asset = self.asset_id
        cat = self.category_id
        live = asset and asset.state == "active"
        cost = money(asset.cost) if live else 0.0
        accumulated = (
            money(asset.accumulated_depreciation + asset.impairment_total) if live else 0.0
        )
        diff = money(liability + accumulated - cost)
        needed = ["journal_id", "asset_account_id"]
        if accumulated:
            needed.append("accumulated_account_id")
        if diff > 0:
            needed.append("gain_account_id")
        elif diff < 0:
            needed.append("loss_account_id")
        require_accounts(cat, needed, "Lease termination")
        label = "IFRS 16 termination: %s (%s)" % (self.name, reason or "-")
        lines = [
            (self.liability_account_id, liability, 0.0, label),
            (cat.accumulated_account_id, accumulated, 0.0, label),
            (cat.asset_account_id, 0.0, cost, label),
        ]
        if diff > 0:
            lines.append((cat.gain_account_id, 0.0, diff, label))
        elif diff < 0:
            lines.append((cat.loss_account_id, -diff, 0.0, label))
        lines = [ln for ln in lines if ln[0]]
        move = post_entry(
            self.env,
            self.company_id,
            cat.journal_id,
            on_date,
            label,
            lines,
            self.operating_unit_id,
        )
        self.schedule_line_ids.filtered(lambda ln: ln.state == "draft").sudo().unlink()
        if live:
            asset._mark_disposed(on_date, move)
        self._guarded().write(
            {"state": "ended", "terminated_on": on_date, "termination_move_id": move.id}
        )
        self.message_post(
            body=self.env._(
                "Terminated on %(d)s (%(why)s): liability %(l)s and ROU %(c)s derecognised, "
                "%(gl)s %(amt)s.",
                d=on_date,
                why=reason or "-",
                l=liability,
                c=money(cost - accumulated),
                gl="gain" if diff >= 0 else "loss",
                amt=abs(diff),
            )
        )
        return move


class FixLeaseScheduleLine(models.Model):
    _name = "fix.lease.schedule.line"
    _description = "Lease Schedule Line"
    _inherit = ["fix.guarded.mixin", "mail.thread", "mail.activity.mixin"]
    _order = "lease_id, sequence"

    lease_id = fields.Many2one(
        "fix.lease", string="Lease", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="lease_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="lease_id.operating_unit_id", store=True, string="Branch"
    )
    currency_id = fields.Many2one(related="lease_id.currency_id")
    sequence = fields.Integer(string="Month No.", required=True)
    period_start = fields.Date(string="Period (Month)", required=True)
    opening = fields.Monetary(string="Opening Liability")
    payment = fields.Monetary(string="Payment")
    interest = fields.Monetary(string="Interest")
    principal = fields.Monetary(string="Principal")
    closing = fields.Monetary(string="Closing Liability")
    depreciation = fields.Monetary(string="ROU Depreciation")
    state = fields.Selection(
        [("draft", "Draft"), ("posted", "Posted")], default="draft", required=True, tracking=True
    )
    move_id = fields.Many2one("account.move", string="Journal Entry", readonly=True, copy=False)

    _lease_sequence_uniq = models.Constraint(
        "UNIQUE (lease_id, sequence)", "One schedule line per lease month."
    )

    def _fix_guarded_fields(self) -> set:
        # the schedule is computed at recognition; its figures and posting
        # state move only by its actions
        return super()._fix_guarded_fields() | {
            n
            for n, f in self._fields.items()
            if f.store
            and n not in ("id", "create_uid", "create_date", "write_uid", "write_date")
            and not n.startswith(("message_", "activity_"))
            and f.type not in ("one2many", "many2many")
        }

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            raise UserError(self.env._("The lease schedule is built at commencement."))
        return super().create(vals_list)

    def action_post(self):
        """Post the month: interest accretion and the rent payment on the
        lease liability, then the ROU depreciation through the depreciation
        run (idempotent per asset and month). Months post in order, once."""
        require_group(self.env, USER_GROUP, "Posting a lease month")
        for line in self.sorted(lambda ln: (ln.lease_id.id, ln.sequence)):
            lease = line.lease_id
            if line.state != "draft":
                raise UserError(
                    self.env._("Month %s of %s is already posted.", line.sequence, lease.name)
                )
            if lease.state != "active":
                raise UserError(self.env._("%s is not active.", lease.name))
            earlier = lease.schedule_line_ids.filtered(
                lambda ln, s=line.sequence: ln.sequence < s and ln.state != "posted"
            )
            if earlier:
                raise UserError(self.env._("Post the earlier months of %s first.", lease.name))
            label = "%s — month %s" % (lease.name, line.sequence)
            move = self.env["account.move"]
            if money(line.interest) or money(line.payment):
                # A07 FIN-02: on the lease's own branch, never the first OU
                move = post_entry(
                    self.env,
                    lease.company_id,
                    lease.category_id.journal_id,
                    month_end(line.period_start),
                    label,
                    [
                        (lease.interest_account_id, line.interest, 0.0, label),
                        (lease.liability_account_id, line.principal, 0.0, label),
                        (lease.payment_account_id, 0.0, line.payment, label),
                    ],
                    lease.operating_unit_id,
                )
            line._guarded().write({"state": "posted", "move_id": move.id})
            asset = lease.asset_id
            if asset and asset.state == "active":
                charged = asset.depreciation_line_ids.filtered(
                    lambda ln, p=line.period_start: ln.book == "book" and ln.period_start == p
                )
                if not charged:
                    self.env["fix.asset.depreciation.run"]._depreciate(
                        asset, line.period_start, "book"
                    )
            if all(ln.state == "posted" for ln in lease.schedule_line_ids):
                lease._guarded().write({"state": "ended"})
        return True
