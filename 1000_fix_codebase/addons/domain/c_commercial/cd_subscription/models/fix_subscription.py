# cd_subscription — M39 Subscription & recurring revenue + the M53 W4
# revenue slice (P07-M03, CD-M39-01).
#
# T02: consolidated B2B invoicing — ONE invoice per period for many jobs
# across many sites (a corporate client with 400 devices does not want 400
# invoices). T04: the W4 revenue-recognition slice (non-marketplace half);
# T06: commission CALCULATION (earning is an M12 event — pair 12; the
# computation lives in services/settlement-engine).
from odoo import api, fields, models
from odoo.exceptions import UserError

from datetime import date, timedelta

from decimal import Decimal

from libs.py.fix_events import publish  # FF-28


class FixSubscription(models.Model):
    """A recurring subscription on OCA contract's pattern, billing through
    M20's AR engine."""

    _name = "fix.subscription"
    _description = "Subscription"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "next_invoice_date, id desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    name = fields.Char(required=True)
    customer_id = fields.Many2one("res.partner", string="Customer", required=True,
                                  index=True, ondelete="restrict")
    contract_id = fields.Many2one("fix.contract", string="Contract",
                                  index=True, ondelete="set null")
    plan = fields.Selection(
        [("basic", "Basic"), ("standard", "Standard"), ("premium", "Premium")],
        required=True, default="standard")
    billing_cycle = fields.Selection(
        [("monthly", "Monthly"), ("quarterly", "Quarterly"), ("annual", "Annual")],
        required=True, default="monthly")
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    recurring_amount = fields.Monetary(string="Recurring Amount",
                                       currency_field="currency_id", required=True)
    state = fields.Selection(
        [("trial", "Trial"), ("active", "Active"), ("past_due", "Past Due"),
         ("paused", "Paused"), ("cancelled", "Cancelled"), ("churned", "Churned")],
        default="active", required=True, tracking=True)
    start_date = fields.Date(default=fields.Date.today, required=True)
    next_invoice_date = fields.Date(required=True, default=fields.Date.today)
    consolidated = fields.Boolean(
        default=True,
        help="T02: roll this subscription's period charges into the customer's "
             "ONE consolidated invoice (with jobs and other subscriptions)")

    @api.constrains("recurring_amount")
    def _check_amount(self):
        for sub in self:
            if sub.recurring_amount < 0:
                raise UserError("The recurring amount cannot be negative")

    def _cycle_days(self) -> int:
        return {"monthly": 30, "quarterly": 91, "annual": 365}[self.billing_cycle]

    def action_generate_charge(self):
        """AUT-025: the cycle charge — creates the AR invoice line group and
        advances the next date. Consolidated invoicing aggregates these per
        customer per period (one invoice, not N)."""
        Invoice = self.env["fix.ar.invoice"]
        for sub in self:
            if sub.state != "active":
                continue
            # In the consolidated flow the charge is recorded against the
            # customer's period invoice group; the standalone fallback opens
            # a draft AR invoice for this subscription alone.
            if not sub.consolidated:
                Invoice.create({
                    "customer_id": sub.customer_id.id,
                    "operating_unit_id": sub.operating_unit_id.id,
                    "source_model": "fix.subscription",
                    "source_id": sub.id,
                })
            publish(self.env, "subscription.charged", "fix.subscription", sub.id, {
                "customer_id": sub.customer_id.id,
                "amount": sub.recurring_amount,
                "period_days": sub._cycle_days(),
            })
            sub.next_invoice_date = sub.next_invoice_date + timedelta(
                days=sub._cycle_days())

    def action_cancel(self):
        for sub in self:
            sub.state = "cancelled"
            # T03: subscription dunning stops on cancellation — outstanding
            # balances ride the M20 collections ladder instead
            publish(self.env, "subscription.cancelled", "fix.subscription", sub.id, {})


class FixRevenueSchedule(models.Model):
    """M53's W4 slice (T04): revenue RECOGNITION for the non-marketplace
    half — subscriptions, contracts and protection plans recognized over
    their term. AUT-025's monthly split; the ledger posts from here.

    BRU-LOY-12's shape applied to contracts: fee revenue is recognized over
    the period, never at the point of sale."""

    _name = "fix.revenue.schedule"
    _description = "Revenue Recognition Schedule"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "recognize_date, id"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    source_model = fields.Char(string="Source Model", required=True, index=True)
    source_id = fields.Integer(string="Source ID", required=True, index=True)
    description = fields.Char(required=True)
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    total_amount = fields.Monetary(string="Deferred Amount", currency_field="currency_id",
                                   required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    recognized_amount = fields.Monetary(string="Recognized", currency_field="currency_id",
                                        default=0.0, copy=False)
    state = fields.Selection(
        [("active", "Active"), ("complete", "Complete"), ("cancelled", "Cancelled")],
        default="active", required=True, tracking=True)
    _sql_constraints = [
        ("source_schedule_unique", "unique(source_model, source_id)",
         "One recognition schedule per source document"),
    ]

    @api.constrains("start_date", "end_date", "total_amount")
    def _check_schedule(self):
        for schedule in self:
            if schedule.end_date <= schedule.start_date:
                raise UserError("The recognition term must be positive")
            if schedule.total_amount <= 0:
                raise UserError("The deferred amount must be positive")

    @api.model
    def create_from_deferral(self, source_model: str, source_id: int,
                             description: str, total: float,
                             start: date, end: date) -> "FixRevenueSchedule":
        """Straight-line over the term: each period recognizes
        total * period_days / term_days. The monthly split runs from
        AUT-025's Airflow workflow; this is the schedule it draws down."""
        return self.create({
            "source_model": source_model, "source_id": source_id,
            "description": description, "total_amount": total,
            "start_date": start, "end_date": end,
        })

    def action_recognize_period(self, as_of: date | None = None):
        """Recognize up to `as_of` (default today), straight-line, and
        publish for the GL posting. Idempotent per call — recognition is
        cumulative (recognized_amount only grows)."""
        as_of = as_of or date.today()
        for schedule in self:
            if schedule.state != "active" or as_of < schedule.start_date:
                continue
            effective_end = min(as_of, schedule.end_date)
            term_days = (schedule.end_date - schedule.start_date).days or 1
            elapsed = (effective_end - schedule.start_date).days
            target = round(schedule.total_amount * elapsed / term_days, 2)
            delta = round(target - schedule.recognized_amount, 2)
            if delta <= 0:
                continue
            schedule.recognized_amount = target
            if target >= schedule.total_amount - 0.01:
                schedule.state = "complete"
            publish(self.env, "revenue.recognized", "fix.revenue.schedule",
                    schedule.id, {
                        "amount": delta,
                        "cumulative": schedule.recognized_amount,
                        "source_model": schedule.source_model,
                        "source_id": schedule.source_id,
                    })
