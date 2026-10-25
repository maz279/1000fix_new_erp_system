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
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_asset_common import (
    USER_GROUP,
    add_months,
    money,
    month_end,
    month_start,
    post_entry,
    require_accounts,
    require_group,
)


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


class FixLease(models.Model):
    _name = "fix.lease"
    _description = "Lease Contract (IFRS 16)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
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

    @api.depends("commencement_date", "term_months")
    def _compute_end_date(self):
        for rec in self:
            rec.end_date = (
                month_end(add_months(rec.commencement_date, rec.term_months - 1))
                if rec.commencement_date and rec.term_months > 0
                else False
            )

    @api.depends("payment_amount", "term_months", "ibr_percent", "payment_timing")
    def _compute_preview(self):
        for rec in self:
            try:
                rec.pv_preview = lease_present_value(
                    rec.payment_amount,
                    rec.term_months,
                    rec.ibr_percent / 100.0 / 12.0,
                    rec.payment_timing == "advance",
                )
            except ValueError:
                rec.pv_preview = 0.0

    @api.depends("initial_liability", "schedule_line_ids.state")
    def _compute_balances(self):
        for rec in self:
            posted = rec.schedule_line_ids.filtered(lambda ln: ln.state == "posted")
            last = posted.sorted("sequence")[-1:] if posted else posted
            rec.liability_balance = last.closing if last else rec.initial_liability
            rec.interest_to_date = money(sum(posted.mapped("interest")))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("reference", "/") == "/":
                vals["reference"] = self.env["ir.sequence"].next_by_code("fix.lease") or "/"
        return super().create(vals_list)

    @api.constrains("term_months", "payment_amount", "ibr_percent", "exemption")
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

    def action_activate(self):
        """Commencement: build the schedule, register the ROU asset and post
        Dr ROU / Cr lease liability (+ Cr clearing for prepaid rent and
        direct costs)."""
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
            require_accounts(
                rec.category_id, ["journal_id", "asset_account_id"], "Lease recognition"
            )
            needed = ["liability_account_id", "interest_account_id", "payment_account_id"]
            require_accounts(rec, needed, "Lease recognition")
            rate = rec.ibr_percent / 100.0 / 12.0
            advance = rec.payment_timing == "advance"
            liability = lease_present_value(rec.payment_amount, rec.term_months, rate, advance)
            upfront = money(rec.prepaid_payments + rec.initial_direct_costs)
            rou = money(liability + upfront)
            rows = lease_schedule(liability, rec.payment_amount, rec.term_months, rate, advance)
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
            self.env["fix.lease.schedule.line"].create(vals)
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
            )
            asset = self.env["fix.fixed.asset"].create(
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
                    "state": "active",
                }
            )
            rec.write(
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
        """Post every schedule month up to the current month, in order."""
        today = month_start(fields.Date.context_today(self))
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


class FixLeaseScheduleLine(models.Model):
    _name = "fix.lease.schedule.line"
    _description = "Lease Schedule Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
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
            )
            line.write({"state": "posted", "move_id": move.id})
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
                lease.state = "ended"
        return True
