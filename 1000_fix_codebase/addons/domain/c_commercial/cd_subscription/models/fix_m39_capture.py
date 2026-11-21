# ruff: noqa: I001
# cd_subscription: M39 sub-module capture audit (2026-11-19).
#
# The M39 workspace had a "+ New" on its first page only. Checked against the
# module spec (§3.1, §5 FR-SUB-001..044, §8, §9 BRU-SUB-01..20, §10.1, §11):
#
#   * Billing Schedules (FR-SUB-002/003/010, P0): the schedule was a fixed
#     30/91/365-day roll of next_invoice_date. No alignment (anniversary or
#     calendar), no timing (advance or arrears), no partial first period and
#     no projected periods. fix.subscription.schedule generates the periods,
#     a billing user who did not raise it activates it, and billing then
#     bills its periods in order.
#   * Charge Models (FR-SUB-004/006, FR-SUB-024, P0): a subscription had one
#     amount. fix.subscription.line holds recurring, one-time and usage
#     charge lines; a usage line is the rating tariff (included quantity and
#     a flat, tiered or volume rate), approved by a second person.
#   * Quantity & Proration (FR-SUB-005/012, P0): no quantity change; and an
#     APPROVED proration was never billed: nothing called _fix_mark_invoiced
#     and nothing consumed subscription.proration_approved. A quantity change
#     is now a proration on a charge line, and every approved proration is
#     netted into the next cycle charge (BRU-SUB-11: credit against future
#     charges by default).
#   * Usage Rating (FR-SUB-023/024/030, T-05, BRU-SUB-08, P0): the overage
#     rate was typed on every reading, there was no source key, and usage that
#     could not be rated had nowhere to go. A reading now rates against its
#     usage line, carries an idempotent source key, and a reading that cannot
#     be rated is kept as an exception until re-rated.
#   * Billing Runs (FR-SUB-031/032/033/038, BRU-SUB-17, T-02/T-10, P0): billing
#     was a per-subscription button or a switched-off cron. A billing run is
#     dry-run first, its exceptions dispositioned, reviewed by a Finance
#     Manager who did not run it, and committed unit by unit (resumable).
#   * Credits & Adjustments (FR-SUB-037, BRU-SUB-11/18, P0): a service
#     credit, dispute or correction had no record. fix.subscription.adjustment
#     is approved (a credit under DOFA through M63) and applied to the next
#     cycle charge.
#   * Suspend / Cancel / Renew (§8, FR-SUB-018/020/021/022, BRU-SUB-07/12/13):
#     the page captured nothing; pause, resume and renewal did not exist and
#     cancellation validated no notice. fix.subscription.lifecycle is the
#     request, with its notice evidence, approved by a second person.
#   * Metrics (FR-SUB-042, §10.1 fix.churn.record): churn had no reason or
#     competitor. fix.subscription.churn records them; MRR is normalised to a
#     month (BRU-SUB-15: a quarterly amount was counted as monthly).
from __future__ import annotations

from datetime import timedelta

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.addons.cd_contract_core.models.fix_contract import require_role
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from .fix_subscription import BILLABLE_STATES
from .fix_subscription_ops import (
    BILLING,
    FINANCE_MANAGER,
    PRORATION_CREDIT_DOFA_THRESHOLDS,
    SUB_OFFICER,
)

CYCLE_MONTHS = {"monthly": 1, "quarterly": 3, "annual": 12}
DEAD_STATES = ("cancelled", "churned")
# BRU-SUB-07: the agreed price-change notice; a contract states its own
# termination notice on its template (M08), this is the fallback.
PARAM_PRICE_NOTICE_DAYS = "cd_subscription.price_change_notice_days"
DEFAULT_PRICE_NOTICE_DAYS = 30
PARAM_CANCEL_NOTICE_DAYS = "cd_subscription.cancellation_notice_days"
DEFAULT_CANCEL_NOTICE_DAYS = 30


def _int_param(env, key, default):
    try:
        return int(env["ir.config_parameter"].sudo().get_param(key, default))
    except (TypeError, ValueError):
        return default


def _other_person(env, users, what):
    """Maker-checker: the acting user is none of `users` (service code acts
    for nobody)."""
    if env.su:
        return
    if env.user in users.filtered(lambda u: u):
        raise UserError("Segregation of duties: %s must be done by someone else." % what)


def _monthly(sub, amount):
    """BRU-SUB-15: a cycle amount as a monthly value."""
    return round((amount or 0.0) / CYCLE_MONTHS.get(sub.billing_cycle or "monthly", 1), 2)


# =============================================================================
# Charge lines and usage tariffs (page 3, FR-SUB-004/006/024)
# =============================================================================
LINE_TERMS = frozenset(
    {
        "subscription_id",
        "charge_type",
        "quantity",
        "unit_rate",
        "metric",
        "included_qty",
        "rating_model",
        "overage_rate",
        "tier_ids",
        "start_date",
        "end_date",
    }
)


class FixSubscriptionLine(models.Model):
    _name = "fix.subscription.line"
    _description = "Subscription Charge Line"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "subscription_id, id"

    subscription_id = fields.Many2one(
        "fix.subscription", required=True, index=True, ondelete="cascade"
    )
    company_id = fields.Many2one(
        related="subscription_id.company_id", store=True, index=True, string="Company"
    )
    operating_unit_id = fields.Many2one(
        related="subscription_id.operating_unit_id", store=True, string="Operating Unit"
    )
    currency_id = fields.Many2one(related="subscription_id.currency_id", string="Currency")
    customer_id = fields.Many2one(
        related="subscription_id.customer_id", store=True, string="Customer"
    )
    name = fields.Char(required=True, string="Description")
    charge_type = fields.Selection(
        [
            ("recurring", "Recurring (every cycle)"),
            ("one_time", "One-time"),
            ("usage", "Usage-based (rating tariff)"),
        ],
        required=True,
        default="recurring",
        tracking=True,
    )
    quantity = fields.Float(default=1.0, help="Devices, sites, seats, licences, GB.")
    unit_rate = fields.Monetary(
        currency_field="currency_id", help="Per unit per billing cycle (one-time: per unit)."
    )
    amount = fields.Monetary(
        currency_field="currency_id",
        compute="_compute_amount",
        store=True,
        string="Line Amount",
        help="Quantity x unit rate, billed every cycle (recurring) or once (one-time).",
    )
    metric = fields.Char(help="Usage lines: what is metered (remote hours, GB, prints...).")
    included_qty = fields.Float(string="Included Quantity", help="Usage within the plan.")
    rating_model = fields.Selection(
        [
            ("flat", "Flat overage rate"),
            ("tiered", "Tiered (each band at its own rate)"),
            ("volume", "Volume (all units at the reached band's rate)"),
        ],
        default="flat",
    )
    overage_rate = fields.Float(string="Overage Rate (BDT/unit)")
    tier_ids = fields.One2many("fix.subscription.line.tier", "line_id", string="Rate Bands")
    start_date = fields.Date(required=True, default=fields.Date.context_today)
    end_date = fields.Date()
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("ended", "Ended"), ("void", "Void")],
        default="draft",
        required=True,
        readonly=True,
        tracking=True,
    )
    approved_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    approved_at = fields.Datetime(readonly=True, copy=False)
    billed_charge_id = fields.Many2one(
        "fix.subscription.charge",
        string="Billed On (one-time)",
        readonly=True,
        copy=False,
        ondelete="set null",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "approved_by_id",
            "approved_at",
            "billed_charge_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if len(self) == 1 and self.state != "draft":
            locked |= LINE_TERMS
        return locked

    @api.depends("quantity", "unit_rate", "charge_type")
    def _compute_amount(self):
        for line in self:
            line.amount = (
                0.0
                if line.charge_type == "usage"
                else round((line.quantity or 0.0) * (line.unit_rate or 0.0), 2)
            )

    @api.constrains(
        "quantity", "unit_rate", "included_qty", "overage_rate", "start_date", "end_date"
    )
    def _check_line(self):
        for line in self:
            if min(line.quantity, line.unit_rate, line.included_qty, line.overage_rate) < 0:
                raise ValidationError("Quantities and rates on a charge line cannot be negative.")
            if line.end_date and line.end_date < line.start_date:
                raise ValidationError("A charge line cannot end before it starts.")
            if line.charge_type == "usage" and not (line.metric or "").strip():
                raise ValidationError("A usage line names the metric it rates.")

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, SUB_OFFICER, "Adding a charge line")
        lines = super().create(vals_list)
        for line in lines:
            if line.subscription_id.state in DEAD_STATES:
                raise UserError(
                    "Subscription %s is %s."
                    % (line.subscription_id.name, line.subscription_id.state)
                )
        return lines

    def write(self, vals):
        if self and not self._fix_guard_open():
            for line in self.filtered(lambda r: r.state != "draft"):
                if any(
                    n == "tier_ids" or line._fix_guard_differs(n, vals[n], line[n])
                    for n in set(vals) & LINE_TERMS
                ):
                    raise UserError(
                        "Charge line %s is %s: its terms are fixed. A quantity change is a "
                        "proration; a new rate is a new line." % (line.name, line.state)
                    )
        return super().write(vals)

    # ---- rating (FR-SUB-024) ---------------------------------------------------
    def _rate_usage(self, quantity):
        """(billable quantity, amount) of `quantity` against this tariff."""
        self.ensure_one()
        billable = max(0.0, (quantity or 0.0) - (self.included_qty or 0.0))
        if self.rating_model == "flat" or not self.tier_ids:
            return billable, round(billable * (self.overage_rate or 0.0), 2)
        tiers = self.tier_ids.sorted("from_qty")
        if self.rating_model == "volume":
            reached = tiers.filtered(lambda t: t.from_qty <= billable)[-1:]
            return billable, round(billable * (reached.rate if reached else 0.0), 2)
        amount = 0.0
        for i, tier in enumerate(tiers):
            upper = tiers[i + 1].from_qty if i + 1 < len(tiers) else None
            if billable <= tier.from_qty:
                break
            band = (min(billable, upper) if upper is not None else billable) - tier.from_qty
            amount += max(0.0, band) * tier.rate
        return billable, round(amount, 2)

    # ---- lifecycle -------------------------------------------------------------
    def action_approve(self):
        """A price term: a billing user who did not raise it."""
        require_role(self.env, BILLING, "Approving a charge line")
        for line in self:
            if line.state != "draft":
                raise UserError("Charge line %s is %s." % (line.name, line.state))
            _other_person(self.env, line.create_uid, "approving charge line %s" % line.name)
            if line.charge_type != "usage" and line.amount <= 0:
                raise UserError("Charge line %s has no amount." % line.name)
            if line.charge_type == "usage" and line.rating_model != "flat":
                tiers = line.tier_ids.sorted("from_qty")
                if not tiers or tiers[0].from_qty != 0:
                    raise UserError("A %s tariff starts with a band from 0." % line.rating_model)
            line._guarded().write(
                {
                    "state": "active",
                    "approved_by_id": self.env.uid,
                    "approved_at": fields.Datetime.now(),
                }
            )
            line.message_post(body="Approved by %s." % self.env.user.name)
        return True

    def action_end(self, end_date=None):
        require_role(self.env, SUB_OFFICER, "Ending a charge line")
        end = fields.Date.to_date(end_date) if end_date else fields.Date.context_today(self)
        if end < fields.Date.context_today(self) and not self.env.su:
            raise UserError("A charge line ends today or later (BRU-SUB-06: no backdated change).")
        for line in self:
            if line.state != "active":
                raise UserError("Only an active charge line is ended.")
            line._guarded().write({"end_date": end, "state": "ended"})
        return True

    def action_void(self):
        require_role(self.env, SUB_OFFICER, "Voiding a charge line")
        for line in self:
            if line.state != "draft":
                raise UserError("Only a draft charge line is voided; end an active one.")
            line._guarded().write({"state": "void"})
        return True

    def _bills_in(self, period_start, period_end):
        """Active (or ended within the period) and running in the period."""
        return self.filtered(
            lambda line: line.state in ("active", "ended")
            and line.start_date <= period_end
            and (not line.end_date or line.end_date >= period_start)
        )


class FixSubscriptionLineTier(models.Model):
    _name = "fix.subscription.line.tier"
    _description = "Usage Rate Band"
    _order = "line_id, from_qty"

    line_id = fields.Many2one(
        "fix.subscription.line", required=True, ondelete="cascade", index=True
    )
    from_qty = fields.Float(string="From (billable units)", required=True, default=0.0)
    rate = fields.Float(string="Rate (BDT/unit)", required=True, default=0.0)

    @api.constrains("from_qty", "rate")
    def _check_tier(self):
        for tier in self:
            if tier.from_qty < 0 or tier.rate < 0:
                raise ValidationError("A rate band cannot be negative.")

    def _guard_line(self):
        for tier in self:
            if tier.line_id.state != "draft" and not self.env.su:
                raise UserError("The rate bands of an approved line are fixed.")

    @api.model_create_multi
    def create(self, vals_list):
        tiers = super().create(vals_list)
        tiers._guard_line()
        return tiers

    def write(self, vals):
        self._guard_line()
        return super().write(vals)

    def unlink(self):
        self._guard_line()
        return super().unlink()


class FixSubscriptionWithLines(models.Model):
    _inherit = "fix.subscription"

    line_ids = fields.One2many("fix.subscription.line", "subscription_id", string="Charge Lines")
    schedule_ids = fields.One2many(
        "fix.subscription.schedule", "subscription_id", string="Billing Schedules"
    )
    monthly_value = fields.Monetary(
        compute="_compute_monthly_value",
        currency_field="currency_id",
        string="MRR Contribution",
        help="BRU-SUB-15: the recurring amount and active recurring lines, normalised to a "
        "month; one-time charges excluded.",
    )

    @api.depends(
        "recurring_amount",
        "billing_cycle",
        "line_ids.amount",
        "line_ids.state",
        "line_ids.charge_type",
    )
    def _compute_monthly_value(self):
        for sub in self:
            recurring = sum(
                sub.line_ids.filtered(
                    lambda line: line.charge_type == "recurring" and line.state == "active"
                ).mapped("amount")
            )
            sub.monthly_value = _monthly(sub, (sub.recurring_amount or 0.0) + recurring)

    def _active_schedule(self):
        self.ensure_one()
        return self.schedule_ids.filtered(lambda s: s.state == "active")[:1]

    def action_generate_charge(self):
        """A subscription on an active billing schedule bills its next planned
        period (its own dates and partial-period amount); the others keep the
        fixed cycle roll.

        A04 ERP M39-F9 (BRU-SUB-17): a cycle is billed only by a billing run
        whose dry run a Finance Manager reviewed (the run's commit carries the
        guard token), or by system code; the only Accountant billed a cycle
        straight from the button. M39-F8: a scheduled period is priced at
        billing time (the price in force today x the period's fraction), not
        the amount frozen when the schedule was generated."""
        if not self.env.su and not self._fix_guard_has_token():
            raise UserError(
                "A subscription cycle is billed by a billing run: dry run it, have a Finance "
                "Manager who did not run it review it, then commit it (BRU-SUB-17)."
            )
        plain = self.browse()
        Charge = self.env["fix.subscription.charge"]
        for sub in self:
            schedule = sub._active_schedule() if sub.state in BILLABLE_STATES else False
            period = (
                schedule
                and schedule.period_ids.filtered(lambda p: p.state == "planned").sorted(
                    "period_start"
                )[:1]
            )
            if not period:
                plain |= sub
                continue
            amount = period._fix_price_now()
            if amount <= 0:
                raise UserError("Subscription %s has no recurring amount to charge" % sub.name)
            charge = Charge._guarded().create(
                {
                    "company_id": sub.company_id.id,
                    "operating_unit_id": sub.operating_unit_id.id,
                    "subscription_id": sub.id,
                    "period_start": period.period_start,
                    "period_end": period.period_end,
                    "amount": amount,
                }
            )
            charge = Charge.browse(charge.ids)
            charge._create_invoice()
            period.sudo().write({"state": "billed", "charge_id": charge.id})
            nxt = schedule.period_ids.filtered(lambda p: p.state == "planned").sorted(
                "period_start"
            )[:1]
            sub.sudo().write(
                {
                    "next_invoice_date": nxt.billing_date
                    if nxt
                    else period.period_end + timedelta(days=1)
                }
            )
            if not nxt:
                sub.message_post(body="Billing schedule exhausted: generate the next schedule.")
            publish(
                self.env,
                "subscription.charged",
                "fix.subscription",
                sub.id,
                {
                    "customer_id": sub.customer_id.id,
                    "amount": charge.amount,
                    "period_days": (period.period_end - period.period_start).days + 1,
                },
            )
        if plain:
            return super(FixSubscriptionWithLines, plain).action_generate_charge()
        return True


# =============================================================================
# Billing schedule (page 2, FR-SUB-002/003/010)
# =============================================================================
class FixSubscriptionSchedule(models.Model):
    _name = "fix.subscription.schedule"
    _description = "Subscription Billing Schedule"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    subscription_id = fields.Many2one(
        "fix.subscription", required=True, index=True, ondelete="cascade"
    )
    company_id = fields.Many2one(
        related="subscription_id.company_id", store=True, index=True, string="Company"
    )
    operating_unit_id = fields.Many2one(
        related="subscription_id.operating_unit_id", store=True, string="Operating Unit"
    )
    currency_id = fields.Many2one(related="subscription_id.currency_id", string="Currency")
    customer_id = fields.Many2one(
        related="subscription_id.customer_id", store=True, string="Customer"
    )
    name = fields.Char(compute="_compute_name", store=True)
    billing_cycle = fields.Selection(related="subscription_id.billing_cycle", string="Frequency")
    alignment = fields.Selection(
        [
            ("anniversary", "Anniversary (from the start date)"),
            ("calendar", "Calendar (month / quarter / year)"),
        ],
        required=True,
        default="anniversary",
    )
    timing = fields.Selection(
        [("advance", "In advance (period start)"), ("arrears", "In arrears (after period end)")],
        required=True,
        default="advance",
    )
    first_period = fields.Selection(
        [
            ("prorate", "Prorate a partial first period by day"),
            ("full", "Bill a partial first period in full"),
        ],
        required=True,
        default="prorate",
    )
    anchor_date = fields.Date(
        string="First Period Starts", required=True, default=fields.Date.context_today
    )
    horizon = fields.Integer(string="Periods to Generate", default=12, required=True)
    period_ids = fields.One2many(
        "fix.subscription.schedule.period", "schedule_id", string="Periods"
    )
    planned_total = fields.Monetary(compute="_compute_totals", currency_field="currency_id")
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("superseded", "Superseded"), ("void", "Void")],
        default="draft",
        required=True,
        readonly=True,
        tracking=True,
    )
    activated_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    activated_at = fields.Datetime(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "activated_by_id", "activated_at"}

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if len(self) == 1 and self.state != "draft":
            locked |= {
                "subscription_id",
                "alignment",
                "timing",
                "first_period",
                "anchor_date",
                "horizon",
            }
        return locked

    @api.depends("subscription_id.name", "anchor_date")
    def _compute_name(self):
        for rec in self:
            rec.name = "%s from %s" % (rec.subscription_id.name or "", rec.anchor_date or "")

    @api.depends("period_ids.amount_planned")
    def _compute_totals(self):
        for rec in self:
            rec.planned_total = sum(rec.period_ids.mapped("amount_planned"))

    @api.constrains("horizon")
    def _check_horizon(self):
        for rec in self:
            if not 1 <= rec.horizon <= 36:
                raise ValidationError("A schedule generates 1 to 36 periods.")

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, SUB_OFFICER, "Setting up a billing schedule")
        records = super().create(vals_list)
        for rec in records:
            if rec.subscription_id.state in DEAD_STATES:
                raise UserError(
                    "Subscription %s is %s." % (rec.subscription_id.name, rec.subscription_id.state)
                )
        records._generate_periods()
        return records

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state != "draft"):
                touched = set(vals) & {
                    "subscription_id",
                    "alignment",
                    "timing",
                    "first_period",
                    "anchor_date",
                    "horizon",
                }
                if any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in touched):
                    raise UserError(
                        "Schedule %s is %s: generate a new schedule." % (rec.name, rec.state)
                    )
        result = super().write(vals)
        if set(vals) & {
            "alignment",
            "timing",
            "first_period",
            "anchor_date",
            "horizon",
            "subscription_id",
        }:
            self.filtered(lambda r: r.state == "draft")._generate_periods()
        return result

    def _calendar_cycle(self, start):
        """(first day, last day) of the calendar cycle containing `start`."""
        months = CYCLE_MONTHS[self.subscription_id.billing_cycle or "monthly"]
        first = start.replace(day=1)
        cycle_start = first - relativedelta(months=(first.month - 1) % months)
        return cycle_start, cycle_start + relativedelta(months=months) - timedelta(days=1)

    def _generate_periods(self):
        Period = self.env["fix.subscription.schedule.period"].sudo()
        for rec in self:
            rec.period_ids.sudo().unlink()
            sub = rec.subscription_id
            months = CYCLE_MONTHS[sub.billing_cycle or "monthly"]
            rows = []
            start = rec.anchor_date
            term_end = sub.contract_end_date
            for i in range(rec.horizon):
                # A04 ERP M39-F5: nothing is scheduled past the contract end
                if term_end and start > term_end:
                    break
                if rec.alignment == "calendar":
                    cycle_start, end = rec._calendar_cycle(start)
                    full_days = (end - cycle_start).days + 1
                else:
                    end = (
                        rec.anchor_date + relativedelta(months=months * (i + 1)) - timedelta(days=1)
                    )
                    full_days = (end - start).days + 1
                last = bool(term_end and end > term_end)
                if last:
                    end = term_end
                days = (end - start).days + 1
                fraction = 1.0
                partial = rec.alignment == "calendar" and i == 0 and days < full_days
                if partial and rec.first_period == "prorate":
                    fraction = days / full_days
                if last and days < full_days:
                    partial = True
                    fraction = days / full_days
                rows.append(
                    {
                        "schedule_id": rec.id,
                        "sequence": i + 1,
                        "period_start": start,
                        "period_end": end,
                        "billing_date": start
                        if rec.timing == "advance"
                        else end + timedelta(days=1),
                        "days": days,
                        "partial": partial,
                        "fraction": fraction,
                        "amount_planned": round((sub.recurring_amount or 0.0) * fraction, 2),
                        "explanation": (
                            "Partial period: %d of %d days x the price in force" % (days, full_days)
                            if fraction < 1.0
                            else "Full %s period" % (sub.billing_cycle or "monthly")
                        ),
                    }
                )
                start = end + timedelta(days=1)
            Period.create(rows)

    def action_regenerate(self):
        require_role(self.env, SUB_OFFICER, "Regenerating a billing schedule")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft schedule is regenerated.")
        self._generate_periods()
        return True

    def action_activate(self):
        """A billing user who did not set it up; it supersedes the active one
        and moves the next invoice date to its first period."""
        require_role(self.env, BILLING, "Activating a billing schedule")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Schedule %s is %s." % (rec.name, rec.state))
            _other_person(self.env, rec.create_uid, "activating billing schedule %s" % rec.name)
            sub = rec.subscription_id.sudo()
            billed_until = (
                max(sub.charge_ids.mapped("period_end") or [False]) if sub.charge_ids else False
            )
            if billed_until and rec.anchor_date <= billed_until:
                raise UserError(
                    "Subscription %s is billed until %s: the schedule starts after it."
                    % (sub.name, billed_until)
                )
            if not rec.period_ids:
                raise UserError("Schedule %s has no periods." % rec.name)
            sub.schedule_ids.filtered(lambda s: s.state == "active")._guarded().write(
                {"state": "superseded"}
            )
            rec._guarded().write(
                {
                    "state": "active",
                    "activated_by_id": self.env.uid,
                    "activated_at": fields.Datetime.now(),
                }
            )
            first = rec.period_ids.sorted("period_start")[:1]
            sub.write({"next_invoice_date": first.billing_date})
            sub.message_post(
                body="Billing schedule %s activated by %s." % (rec.name, self.env.user.name)
            )
        return True

    def action_void(self):
        require_role(self.env, SUB_OFFICER, "Voiding a billing schedule")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft schedule is voided.")
            rec._guarded().write({"state": "void"})
        return True


class FixSubscriptionSchedulePeriod(models.Model):
    _name = "fix.subscription.schedule.period"
    _description = "Billing Schedule Period"
    _order = "schedule_id, period_start"

    schedule_id = fields.Many2one(
        "fix.subscription.schedule", required=True, ondelete="cascade", index=True
    )
    subscription_id = fields.Many2one(related="schedule_id.subscription_id", store=True, index=True)
    company_id = fields.Many2one(related="schedule_id.company_id", store=True)
    currency_id = fields.Many2one(related="schedule_id.currency_id")
    sequence = fields.Integer(readonly=True)
    period_start = fields.Date(readonly=True)
    period_end = fields.Date(readonly=True)
    billing_date = fields.Date(readonly=True)
    days = fields.Integer(readonly=True)
    partial = fields.Boolean(readonly=True)
    amount_planned = fields.Monetary(
        currency_field="currency_id",
        readonly=True,
        help="The price in force when the schedule was generated (a projection): the period "
        "is billed at the price in force on its billing day (M39-F8).",
    )
    fraction = fields.Float(
        string="Share of a Full Cycle",
        readonly=True,
        default=1.0,
        help="A partial (first / last) period bills this share of the recurring amount.",
    )
    explanation = fields.Char(readonly=True)
    state = fields.Selection(
        [("planned", "Planned"), ("billed", "Billed"), ("skipped", "Skipped")],
        default="planned",
        readonly=True,
    )
    charge_id = fields.Many2one("fix.subscription.charge", readonly=True, ondelete="set null")

    def write(self, vals):
        if not self.env.su:
            raise UserError("Schedule periods are generated; regenerate the schedule instead.")
        return super().write(vals)

    def _fix_price_now(self):
        """M39-F8: the period at the price in force when it is billed."""
        self.ensure_one()
        sub = self.subscription_id.sudo()
        return round((sub.recurring_amount or 0.0) * (self.fraction or 1.0), 2)


# =============================================================================
# Usage: tariff, source key and the exception queue (page 5)
# =============================================================================
class FixSubscriptionUsageRated(models.Model):
    _inherit = "fix.subscription.usage"

    line_id = fields.Many2one(
        "fix.subscription.line",
        string="Usage Tariff",
        domain="[('subscription_id', '=', subscription_id), ('charge_type', '=', 'usage'), ('state', '=', 'active')]",
        ondelete="restrict",
    )
    source_module = fields.Selection(
        [
            ("manual", "Manual reading"),
            ("m05", "M05 remote hours / incidents"),
            ("m06", "M06 storage volume"),
            ("m13", "M13 rental utilisation"),
            ("m08", "M08 entitlement overage"),
        ],
        default="manual",
        required=True,
    )
    source_key = fields.Char(
        help="The source record's key: a reading delivered twice is refused (T-05)."
    )
    state = fields.Selection(
        selection_add=[("exception", "Exception (not rated)")],
        ondelete={"exception": "set default"},
    )
    exception_cause = fields.Char(readonly=True, copy=False)

    _source_key_unique = models.Constraint(
        "UNIQUE (subscription_id, source_module, source_key)",
        "This source record is already metered on the subscription (T-05).",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"exception_cause"}

    @api.depends(
        "quantity",
        "committed",
        "overage_rate",
        "line_id",
        "line_id.included_qty",
        "line_id.overage_rate",
    )
    def _compute_overage(self):
        rated = self.filtered("line_id")
        for rec in rated:
            rec.overage_quantity, rec.overage_charge = rec.line_id._rate_usage(rec.quantity)
        return super(FixSubscriptionUsageRated, self - rated)._compute_overage()

    def _tariff_vals(self, vals):
        """A tariff line sets the metric, the commitment and the rate: they are
        never typed on a reading that has one."""
        line = self.env["fix.subscription.line"].sudo().browse(vals.get("line_id") or [])
        sub_id = vals.get("subscription_id")
        if not line and sub_id and vals.get("metric"):
            line = (
                self.env["fix.subscription.line"]
                .sudo()
                .search(
                    [
                        ("subscription_id", "=", sub_id),
                        ("charge_type", "=", "usage"),
                        ("state", "=", "active"),
                        ("metric", "=ilike", vals["metric"].strip()),
                    ],
                    limit=1,
                )
            )
        if line:
            if (
                line.subscription_id.id != (sub_id or line.subscription_id.id)
                or line.charge_type != "usage"
            ):
                raise UserError("The tariff is a usage line of the same subscription.")
            if line.state != "active":
                raise UserError("Tariff %s is not active." % line.name)
            vals.update(
                {
                    "line_id": line.id,
                    "metric": line.metric,
                    "committed": line.included_qty,
                    "overage_rate": line.overage_rate,
                }
            )
        return vals

    def _exception_cause(self):
        self.ensure_one()
        if self.subscription_id.state in DEAD_STATES:
            return "Subscription %s is %s: nothing to rate against." % (
                self.subscription_id.name,
                self.subscription_id.state,
            )
        if not self.line_id and self.quantity > self.committed and not self.overage_rate:
            return "No tariff: usage above the commitment has no rate."
        return False

    def _sort_exceptions(self):
        for rec in self:
            if rec.state == "billed":
                continue
            cause = rec._exception_cause()
            if cause:
                rec._guarded().write({"state": "exception", "exception_cause": cause})
            elif rec.state == "exception":
                rec._guarded().write({"state": "open", "exception_cause": False})

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = [self._tariff_vals(dict(v)) for v in vals_list]
        records = super().create(vals_list)
        records._sort_exceptions()
        return records

    def write(self, vals):
        if "line_id" in vals or "metric" in vals:
            for rec in self:
                merged = {
                    "subscription_id": rec.subscription_id.id,
                    "metric": vals.get("metric", rec.metric),
                }
                merged["line_id"] = vals.get("line_id", rec.line_id.id)
                vals = dict(
                    vals,
                    **{
                        k: v for k, v in self._tariff_vals(merged).items() if k != "subscription_id"
                    },
                )
        result = super().write(vals)
        if set(vals) & {
            "line_id",
            "metric",
            "quantity",
            "committed",
            "overage_rate",
            "subscription_id",
        }:
            self._sort_exceptions()
        return result

    def action_rerate(self):
        """Work the exception queue: after the reading was given a tariff (or
        the subscription was reinstated) it is rated again (BRU-SUB-08)."""
        require_role(self.env, SUB_OFFICER, "Re-rating usage")
        for rec in self:
            if rec.state != "exception":
                raise UserError("Only a usage exception is re-rated.")
        self._sort_exceptions()
        still = self.filtered(lambda r: r.state == "exception")
        if still:
            raise UserError("Still not rateable: %s" % "; ".join(still.mapped("exception_cause")))
        return True


# =============================================================================
# Proration: quantity change, and the approved proration billed (page 4)
# =============================================================================
class FixSubscriptionProrationQty(models.Model):
    _inherit = "fix.subscription.proration"

    change_type = fields.Selection(
        selection_add=[("quantity", "Quantity Change")],
        ondelete={"quantity": "set default"},
    )
    line_id = fields.Many2one(
        "fix.subscription.line",
        string="Charge Line",
        domain="[('subscription_id', '=', subscription_id), ('charge_type', '=', 'recurring'), ('state', '=', 'active')]",
    )
    old_quantity = fields.Float(readonly=True, copy=False)
    new_quantity = fields.Float()
    billed_charge_id = fields.Many2one(
        "fix.subscription.charge", string="Billed On Cycle", readonly=True, copy=False
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"old_quantity", "billed_charge_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if len(self) == 1 and self.state != "draft":
            locked |= {"line_id", "new_quantity"}
        return locked

    @api.constrains("change_type", "line_id", "new_quantity")
    def _check_quantity_change(self):
        for rec in self.filtered(lambda r: r.change_type == "quantity"):
            line = rec.line_id
            if (
                not line
                or line.subscription_id != rec.subscription_id
                or line.charge_type != "recurring"
            ):
                raise ValidationError(
                    "A quantity change names a recurring charge line of the subscription."
                )
            if rec.state == "draft" and line.state != "active":
                raise ValidationError("Charge line %s is not active." % line.name)
            if rec.new_quantity < 0:
                raise ValidationError("A quantity cannot be negative.")

    def _proration_values(self):
        vals = super()._proration_values()
        if self.change_type != "quantity" or not self.line_id:
            return vals
        line = self.line_id.sudo()
        old = line.amount
        new = round((self.new_quantity or 0.0) * (line.unit_rate or 0.0), 2)
        vals.update({"old_quantity": line.quantity, "old_amount": old})
        if self.new_amount != new:
            # written only on change: the base write refreshes on new_amount
            vals["new_amount"] = new
        if vals.get("cycle_days"):
            vals["amount"] = round((new - old) * vals["days_remaining"] / vals["cycle_days"], 2)
        return vals

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state != "draft"):
                touched = set(vals) & {"line_id", "new_quantity"}
                if any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in touched):
                    raise UserError(
                        "Proration %s is %s: its terms are fixed." % (rec.name, rec.state)
                    )
        result = super().write(vals)
        if self and set(vals) & {"line_id", "new_quantity"}:
            self.filtered(lambda r: r.state == "draft")._proration_refresh()
        return result

    def action_request_approval(self, justification=None):
        for rec in self.filtered(lambda r: r.change_type == "quantity"):
            rec._proration_refresh()
            if rec.new_quantity == rec.old_quantity:
                raise UserError("Proration %s changes nothing." % rec.name)
        return super().action_request_approval(justification=justification)

    def _proration_apply_to_subscription(self):
        qty = self.filtered(lambda r: r.change_type == "quantity")
        for rec in qty:
            line = rec.line_id.sudo()
            old = line.quantity
            line._guarded().write({"quantity": rec.new_quantity})
            line.message_post(
                body="Quantity %s -> %s by approved proration %s."
                % (old, rec.new_quantity, rec.name)
            )
            rec._guarded().write({"applied_to_subscription": True})
        return super(FixSubscriptionProrationQty, self - qty)._proration_apply_to_subscription()


# =============================================================================
# Credits and adjustments (page 7, FR-SUB-037, BRU-SUB-11/18)
# =============================================================================
ADJ_TERMS = frozenset(
    {"subscription_id", "charge_id", "adjustment_type", "direction", "amount", "name"}
)


class FixSubscriptionAdjustment(models.Model):
    _name = "fix.subscription.adjustment"
    _description = "Subscription Credit / Adjustment"
    _inherit = ["mail.thread", "fix.dofa.mixin"]
    _order = "id desc"

    subscription_id = fields.Many2one(
        "fix.subscription", required=True, index=True, ondelete="cascade"
    )
    company_id = fields.Many2one(
        related="subscription_id.company_id", store=True, index=True, string="Company"
    )
    operating_unit_id = fields.Many2one(
        related="subscription_id.operating_unit_id", store=True, string="Operating Unit"
    )
    currency_id = fields.Many2one(related="subscription_id.currency_id", string="Currency")
    customer_id = fields.Many2one(
        related="subscription_id.customer_id", store=True, string="Customer"
    )
    _approval_domain = "subscription_credit"
    _approval_apply_method = "action_dofa_approve"
    _approval_group = BILLING
    _approval_routed = True

    name = fields.Char(required=True, string="Reference")
    charge_id = fields.Many2one(
        "fix.subscription.charge",
        string="Cycle Concerned",
        domain="[('subscription_id', '=', subscription_id)]",
    )
    adjustment_type = fields.Selection(
        [
            ("service_credit", "Service credit (SLA)"),
            ("dispute", "Dispute settlement"),
            ("goodwill", "Goodwill"),
            ("correction", "Billing correction / rerating"),
        ],
        required=True,
        default="service_credit",
    )
    direction = fields.Selection(
        [("credit", "Credit to the customer"), ("debit", "Charge to the customer")],
        required=True,
        default="credit",
    )
    amount = fields.Monetary(currency_field="currency_id", required=True)
    signed_amount = fields.Monetary(
        compute="_compute_signed", currency_field="currency_id", store=True
    )
    reason = fields.Text(required=True)
    evidence_ref = fields.Char(string="Evidence (ticket, SLA report, dispute ref)")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending", "Awaiting Approval"),
            ("approved", "Approved (next cycle)"),
            ("applied", "Applied"),
            ("void", "Void"),
        ],
        default="draft",
        required=True,
        readonly=True,
        tracking=True,
    )
    applied_charge_id = fields.Many2one(
        "fix.subscription.charge", string="Applied On", readonly=True, copy=False
    )
    invoice_id = fields.Many2one("fix.ar.invoice", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "applied_charge_id", "invoice_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if len(self) == 1 and self.state != "draft":
            locked |= ADJ_TERMS | {"reason", "evidence_ref"}
        return locked

    @api.depends("amount", "direction")
    def _compute_signed(self):
        for rec in self:
            rec.signed_amount = (
                -(rec.amount or 0.0) if rec.direction == "credit" else (rec.amount or 0.0)
            )

    @api.constrains("amount", "charge_id", "subscription_id")
    def _check_adjustment(self):
        for rec in self:
            if (rec.amount or 0.0) <= 0:
                raise ValidationError(
                    "An adjustment is for a positive amount; the direction says which way."
                )
            if rec.charge_id and rec.charge_id.subscription_id != rec.subscription_id:
                raise ValidationError("The cycle concerned belongs to another subscription.")

    # ---- DOFA: a credit is a concession -----------------------------------------
    def _dofa_amount(self) -> float:
        self.ensure_one()
        return self.amount if self.direction == "credit" else 0.0

    def _dofa_thresholds(self):
        return PRORATION_CREDIT_DOFA_THRESHOLDS

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "BDT %.2f (%s on %s)" % (
            self._dofa_amount(),
            self.adjustment_type,
            self.subscription_id.name,
        )

    @api.depends("amount", "direction")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def _approval_needed(self) -> bool:
        return True

    def _approval_tier(self):
        tier = self._dofa_current_tier()
        return tier if tier != "tier_0" else False

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, SUB_OFFICER, "Raising a subscription credit or adjustment")
        records = super().create(vals_list)
        for rec in records:
            if rec.subscription_id.state == "churned":
                raise UserError("Subscription %s is churned." % rec.subscription_id.name)
        return records

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state != "draft"):
                touched = set(vals) & (ADJ_TERMS | {"reason", "evidence_ref"})
                if any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in touched):
                    raise UserError(
                        "Adjustment %s is %s: its terms are fixed." % (rec.name, rec.state)
                    )
        return super().write(vals)

    def action_request_approval(self, justification=None):
        require_role(self.env, SUB_OFFICER, "Submitting an adjustment")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Adjustment %s is %s." % (rec.name, rec.state))
        result = super().action_request_approval(justification=justification)
        self._guarded().write({"state": "pending"})
        return result

    def action_dofa_approve(self):
        self._approval_assert_routed()
        for rec in self:
            if rec.state != "pending":
                raise UserError("Adjustment %s is %s." % (rec.name, rec.state))
            if rec._dofa_current_tier() == "tier_0":
                if not (self.env.su or self.env.user.has_group(BILLING)):
                    raise UserError("An adjustment is approved by a billing user.")
                if not self.env.su and rec.create_uid in rec._approval_acting_users():
                    raise UserError(
                        "Segregation of duties (BRU-SUB-18): you raised adjustment %s." % rec.name
                    )
            else:
                super(FixSubscriptionAdjustment, rec.sudo()).action_dofa_approve()
        for rec in self.sudo():
            rec._guarded().write({"state": "approved"})
            publish(
                self.env,
                "subscription.adjustment_approved",
                "fix.subscription.adjustment",
                rec.id,
                {
                    "subscription_id": rec.subscription_id.id,
                    "customer_id": rec.subscription_id.customer_id.id,
                    "type": rec.adjustment_type,
                    "amount": float(rec.signed_amount or 0.0),
                },
            )
        return True

    def _approval_on_rejected(self, comment):
        self.sudo().filtered(lambda r: r.state == "pending")._guarded().write({"state": "void"})
        return super()._approval_on_rejected(comment)

    def action_recall_approval(self):
        result = super().action_recall_approval()
        self.filtered(lambda r: r.state == "pending")._guarded().write({"state": "draft"})
        return result

    def action_void(self):
        require_role(self.env, SUB_OFFICER, "Voiding an adjustment")
        for rec in self:
            if rec.state not in ("draft", "pending"):
                raise UserError("Adjustment %s is %s." % (rec.name, rec.state))
            rec._approval_void("the adjustment was voided")
            rec.sudo()._guarded().write({"state": "void", "approval_state": "none"})
        return True


# =============================================================================
# The cycle charge: everything approved is billed on it (BRU-SUB-11/19)
# =============================================================================
class FixSubscriptionChargeComposed(models.Model):
    _inherit = "fix.subscription.charge"

    composition = fields.Text(readonly=True, copy=False, help="What this cycle charge is made of.")
    proration_ids = fields.One2many(
        "fix.subscription.proration", "billed_charge_id", string="Prorations Billed"
    )
    adjustment_ids = fields.One2many(
        "fix.subscription.adjustment", "applied_charge_id", string="Adjustments Applied"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"composition"}

    def _fix_components(self):
        """(items, one-time lines, prorations, adjustments) due on this cycle,
        each item (label, signed amount). Credits that would take the charge
        to zero or below wait for the next cycle."""
        self.ensure_one()
        sub = self.subscription_id.sudo()
        debits, credits = [], []
        lines = sub.line_ids._bills_in(self.period_start, self.period_end)
        one_time = self.env["fix.subscription.line"]
        for line in lines.filtered(lambda r: r.charge_type == "recurring" and r.amount):
            debits.append(
                (
                    "Recurring line %s: %s x %.2f" % (line.name, line.quantity, line.unit_rate),
                    line.amount,
                    line,
                )
            )
        for line in sub.line_ids.filtered(
            lambda r: r.charge_type == "one_time"
            and r.state in ("active", "ended")
            and not r.billed_charge_id
            and r.start_date <= self.period_end
        ):
            debits.append(
                (
                    "One-time %s: %s x %.2f" % (line.name, line.quantity, line.unit_rate),
                    line.amount,
                    line,
                )
            )
            one_time |= line
        prorations = (
            self.env["fix.subscription.proration"]
            .sudo()
            .search(
                [
                    ("subscription_id", "=", sub.id),
                    ("state", "=", "approved"),
                    ("billed_charge_id", "=", False),
                    ("effective_date", "<=", self.period_end),
                    # A04 ERP M39-F7: applied on its effective date first
                    ("applied_to_subscription", "=", True),
                ],
                order="effective_date, id",
            )
        )
        for p in prorations:
            label = "Proration %s (%s, %d of %d days)" % (
                p.name,
                p.change_type,
                p.days_remaining,
                p.cycle_days,
            )
            (debits if p.amount >= 0 else credits).append((label, p.amount, p))
        adjustments = (
            self.env["fix.subscription.adjustment"]
            .sudo()
            .search(
                [
                    ("subscription_id", "=", sub.id),
                    ("state", "=", "approved"),
                    ("applied_charge_id", "=", False),
                ],
                order="id",
            )
        )
        for a in adjustments:
            label = "%s %s" % (
                dict(a._fields["adjustment_type"].selection)[a.adjustment_type],
                a.name,
            )
            (debits if a.signed_amount >= 0 else credits).append((label, a.signed_amount, a))
        return debits, credits, one_time

    def _fix_bill_components(self):
        for charge in self:
            debits, credits, one_time = charge._fix_components()
            total = round(charge.amount + sum(d[1] for d in debits), 2)
            taken = list(debits)
            for item in credits:
                if round(total + item[1], 2) > 0:
                    total = round(total + item[1], 2)
                    taken.append(item)
            rows = ["Base: %.2f" % (charge.amount - (charge.overage_amount or 0.0))]
            if charge.overage_amount:
                rows.append("Usage overage: %.2f" % charge.overage_amount)
            rows += ["%s: %+.2f" % (label, amt) for label, amt, _rec in taken]
            waiting = [c for c in credits if c not in taken]
            if waiting:
                rows.append("Carried to the next cycle: %s" % ", ".join(c[0] for c in waiting))
            vals = {"composition": "\n".join(rows)}
            if taken:
                vals["amount"] = total
            charge.sudo()._guarded().write(vals)
            for _label, _amt, rec in taken:
                if rec._name == "fix.subscription.line":
                    if rec in one_time:
                        rec._guarded().write({"billed_charge_id": charge.id})
                elif rec._name == "fix.subscription.proration":
                    rec._guarded().write({"billed_charge_id": charge.id})
                else:
                    rec._guarded().write({"applied_charge_id": charge.id})

    @api.model_create_multi
    def create(self, vals_list):
        charges = super().create(vals_list)
        charges._fix_bill_components()
        return charges

    def _create_invoice(self):
        result = super()._create_invoice()
        for charge in self.sudo():
            if not charge.invoice_id:
                continue
            if charge.composition and charge.invoice_id.state == "draft":
                line = charge.invoice_id.line_ids[:1]
                if line:
                    line.write({"description": "%s\n%s" % (line.description, charge.composition)})
            charge.proration_ids.filtered(lambda p: p.state == "approved")._fix_mark_invoiced(
                invoice=charge.invoice_id
            )
            charge.adjustment_ids.filtered(lambda a: a.state == "approved")._guarded().write(
                {"state": "applied", "invoice_id": charge.invoice_id.id}
            )
        return result


# =============================================================================
# Billing run: dry run, review, commit (page 6, FR-SUB-031..038, BRU-SUB-17)
# =============================================================================
class FixSubscriptionBillingRun(models.Model):
    _name = "fix.subscription.billing.run"
    _description = "Subscription Billing Run"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit (optional)")
    billing_cycle = fields.Selection(
        [("monthly", "Monthly"), ("quarterly", "Quarterly"), ("annual", "Annual")],
        string="Cycle (optional)",
    )
    customer_id = fields.Many2one("res.partner", string="Customer (optional)")
    as_of = fields.Date(
        string="Bill Cycles Due By", required=True, default=fields.Date.context_today
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("dry_run", "Dry Run Done"),
            ("reviewed", "Reviewed"),
            ("partial", "Partly Committed (resume)"),
            ("committed", "Committed"),
            ("void", "Void"),
        ],
        default="draft",
        required=True,
        readonly=True,
        tracking=True,
    )
    unit_ids = fields.One2many("fix.subscription.billing.run.unit", "run_id", string="Units")
    unit_count = fields.Integer(compute="_compute_totals")
    exception_count = fields.Integer(compute="_compute_totals")
    total_amount = fields.Float(compute="_compute_totals", string="Run Total (BDT)")
    dry_run_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    dry_run_at = fields.Datetime(readonly=True, copy=False)
    reviewed_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    reviewed_at = fields.Datetime(readonly=True, copy=False)
    committed_at = fields.Datetime(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "dry_run_by_id",
            "dry_run_at",
            "reviewed_by_id",
            "reviewed_at",
            "committed_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if len(self) == 1 and self.state not in ("draft", "dry_run"):
            locked |= {"company_id", "operating_unit_id", "billing_cycle", "customer_id", "as_of"}
        return locked

    @api.depends("unit_ids.state", "unit_ids.amount")
    def _compute_totals(self):
        for run in self:
            run.unit_count = len(run.unit_ids)
            run.exception_count = len(run.unit_ids.filtered(lambda u: u.state == "exception"))
            run.total_amount = round(
                sum(run.unit_ids.filtered(lambda u: u.state != "skipped").mapped("amount")), 2
            )

    @api.constrains("as_of")
    def _check_as_of(self):
        for run in self:
            if run.as_of > fields.Date.context_today(run):
                raise ValidationError(
                    "A billing run bills cycles already due (as of today or earlier)."
                )

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, BILLING, "Starting a billing run")
        runs = super().create(vals_list)
        for run in runs:
            run.sudo().write({"name": "BR/%s/%05d" % (run.as_of, run.id)})
        return runs

    def write(self, vals):
        if self and not self._fix_guard_open():
            for run in self.filtered(lambda r: r.state not in ("draft", "dry_run")):
                touched = set(vals) & {
                    "company_id",
                    "operating_unit_id",
                    "billing_cycle",
                    "customer_id",
                    "as_of",
                }
                if any(run._fix_guard_differs(n, vals[n], run[n]) for n in touched):
                    raise UserError(
                        "Billing run %s is %s: its scope is fixed." % (run.name, run.state)
                    )
            if set(vals) & {
                "company_id",
                "operating_unit_id",
                "billing_cycle",
                "customer_id",
                "as_of",
            }:
                self.filtered(lambda r: r.state == "dry_run")._guarded().write({"state": "draft"})
        return super().write(vals)

    def _scope(self):
        self.ensure_one()
        domain = [
            ("state", "in", list(BILLABLE_STATES)),
            ("next_invoice_date", "<=", self.as_of),
            ("company_id", "=", self.company_id.id),
        ]
        if self.operating_unit_id:
            domain.append(("operating_unit_id", "=", self.operating_unit_id.id))
        if self.billing_cycle:
            domain.append(("billing_cycle", "=", self.billing_cycle))
        if self.customer_id:
            domain.append(("customer_id", "=", self.customer_id.id))
        return self.env["fix.subscription"].sudo().search(domain, order="next_invoice_date, id")

    @staticmethod
    def _unit_exception(sub):
        if (sub.recurring_amount or 0.0) <= 0 and not sub.line_ids.filtered(
            lambda line: line.state == "active"
        ):
            return "no_amount", "No recurring amount and no active charge line."
        if not sub.contract_id:
            return "no_contract", "Not bound to an M08 contract (BRU-SUB-01)."
        if not sub.customer_id:
            return "no_customer", "No customer to bill."
        if sub.charge_ids.filtered(lambda c: c.period_start == sub.next_invoice_date):
            return "already_billed", "The cycle from %s is already billed." % sub.next_invoice_date
        if (
            sub.contract_end_date
            and sub.next_invoice_date > sub.contract_end_date
            and not sub._active_schedule()
        ):
            return "term_ended", "The contract ended on %s (renew it to bill on)." % (
                sub.contract_end_date
            )
        exceptions = (
            sub.env["fix.subscription.usage"]
            .sudo()
            .search_count([("subscription_id", "=", sub.id), ("state", "=", "exception")])
        )
        if exceptions:
            return "unrated_usage", "%d usage reading(s) are not rated." % exceptions
        return False, False

    @api.model
    def _fix_preview_amount(self, sub, period):
        """A04 ERP M39-F12: what the commit will bill for `sub`, computed the
        way the charge composes it (base or scheduled period at today's price,
        usage overage, recurring and one-time lines, approved prorations and
        adjustments), without writing anything. The dry run counted the base
        and recurring lines only: 3,000 previewed, 8,700 committed."""
        if period:
            start, end = period.period_start, period.period_end
            base = period._fix_price_now()
        else:
            start = sub.next_invoice_date
            end, base = sub._fix_cycle_window(start)
            if not end:
                return 0.0
        overage = sum(
            sub.env["fix.subscription.usage"]
            .sudo()
            .search(
                [
                    ("subscription_id", "=", sub.id),
                    ("state", "=", "open"),
                    ("period_start", "<=", end),
                ]
            )
            .mapped("overage_charge")
        )
        draft = sub.env["fix.subscription.charge"].new(
            {
                "subscription_id": sub.id,
                "period_start": start,
                "period_end": end,
                "amount": base + overage,
            }
        )
        debits, credits, _one_time = draft._fix_components()
        total = round(base + overage + sum(d[1] for d in debits), 2)
        for item in credits:
            if round(total + item[1], 2) > 0:
                total = round(total + item[1], 2)
        return total

    def action_dry_run(self):
        """T-10: the units the commit will bill, with the same scope rules; the
        run writes nothing else."""
        require_role(self.env, BILLING, "Running a billing dry run")
        Unit = self.env["fix.subscription.billing.run.unit"].sudo()
        for run in self:
            if run.state not in ("draft", "dry_run"):
                raise UserError("Billing run %s is %s." % (run.name, run.state))
            run.unit_ids.sudo().unlink()
            rows = []
            for sub in run._scope():
                cause, detail = self._unit_exception(sub)
                schedule = sub._active_schedule()
                period = (
                    schedule
                    and schedule.period_ids.filtered(lambda p: p.state == "planned").sorted(
                        "period_start"
                    )[:1]
                )
                rows.append(
                    {
                        "run_id": run.id,
                        "subscription_id": sub.id,
                        "period_start": period.period_start if period else sub.next_invoice_date,
                        "amount": self._fix_preview_amount(sub, period),
                        "state": "exception" if cause else "ready",
                        "cause": cause or False,
                        "detail": detail or False,
                    }
                )
            Unit.create(rows)
            run._guarded().write(
                {
                    "state": "dry_run",
                    "dry_run_by_id": self.env.uid,
                    "dry_run_at": fields.Datetime.now(),
                }
            )
            run.message_post(
                body="Dry run: %d units, %d exceptions." % (run.unit_count, run.exception_count)
            )
        return True

    def action_review(self):
        """BRU-SUB-17: a Finance Manager who did not run it, once every
        exception carries a disposition."""
        require_role(self.env, FINANCE_MANAGER, "Reviewing a billing run")
        for run in self:
            if run.state != "dry_run":
                raise UserError("Billing run %s has no fresh dry run to review." % run.name)
            _other_person(
                self.env, run.dry_run_by_id | run.create_uid, "reviewing billing run %s" % run.name
            )
            open_ = run.unit_ids.filtered(lambda u: u.state == "exception" and not u.disposition)
            if open_:
                raise UserError(
                    "Disposition every exception first: %s"
                    % ", ".join(open_.mapped("subscription_id.name"))
                )
            run._guarded().write(
                {
                    "state": "reviewed",
                    "reviewed_by_id": self.env.uid,
                    "reviewed_at": fields.Datetime.now(),
                }
            )
        return True

    def action_commit(self):
        """T-02 / FR-SUB-038: unit by unit, each in its own savepoint; a
        committed unit is never billed again, so a failed run resumes."""
        require_role(self.env, BILLING, "Committing a billing run")
        for run in self:
            if run.state not in ("reviewed", "partial"):
                raise UserError(
                    "Billing run %s is committed only after its dry run is reviewed." % run.name
                )
            for unit in run.unit_ids.sorted("id"):
                if unit.state in ("committed", "skipped"):
                    continue
                if unit.state == "exception" and unit.disposition == "skip":
                    unit.sudo().write({"state": "skipped"})
                    continue
                sub = unit.subscription_id
                if sub.state not in BILLABLE_STATES or (
                    sub.next_invoice_date != unit.period_start and not sub._active_schedule()
                ):
                    unit.sudo().write(
                        {"state": "failed", "detail": "The subscription changed after the dry run."}
                    )
                    continue
                try:
                    with self.env.cr.savepoint():
                        before = sub.charge_ids
                        # the reviewed run is the authority to bill (BRU-SUB-17)
                        sub._guarded().action_generate_charge()
                        charge = (sub.charge_ids - before)[:1]
                        unit.sudo().write(
                            {"state": "committed", "charge_id": charge.id, "amount": charge.amount}
                        )
                except (UserError, ValidationError) as exc:
                    unit.sudo().write({"state": "failed", "detail": str(exc)[:250]})
            done = all(u.state in ("committed", "skipped") for u in run.unit_ids)
            run._guarded().write(
                {"state": "committed" if done else "partial", "committed_at": fields.Datetime.now()}
            )
        return True

    def action_void(self):
        require_role(self.env, BILLING, "Voiding a billing run")
        for run in self:
            if run.state not in ("draft", "dry_run", "reviewed"):
                raise UserError("A committed billing run is not voided.")
            run._guarded().write({"state": "void"})
        return True


class FixSubscriptionBillingRunUnit(models.Model):
    _name = "fix.subscription.billing.run.unit"
    _description = "Billing Run Unit"
    _order = "run_id, id"

    run_id = fields.Many2one(
        "fix.subscription.billing.run", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="run_id.company_id", store=True)
    subscription_id = fields.Many2one(
        "fix.subscription", required=True, readonly=True, ondelete="cascade"
    )
    customer_id = fields.Many2one(related="subscription_id.customer_id")
    period_start = fields.Date(readonly=True)
    amount = fields.Float(string="Amount (BDT)", readonly=True)
    state = fields.Selection(
        [
            ("ready", "Ready"),
            ("exception", "Exception"),
            ("committed", "Billed"),
            ("skipped", "Skipped"),
            ("failed", "Failed (resume)"),
        ],
        default="ready",
        readonly=True,
    )
    cause = fields.Selection(
        [
            ("no_amount", "No amount"),
            ("no_contract", "No contract"),
            ("no_customer", "No customer"),
            ("already_billed", "Already billed"),
            ("unrated_usage", "Unrated usage"),
            ("term_ended", "Contract term ended"),
        ],
        readonly=True,
    )
    detail = fields.Char(readonly=True)
    disposition = fields.Selection(
        [("skip", "Skip this cycle"), ("bill", "Bill anyway")],
        help="Exceptions only: what the reviewer decided.",
    )
    disposition_note = fields.Char()
    charge_id = fields.Many2one("fix.subscription.charge", readonly=True, ondelete="set null")

    def write(self, vals):
        if not self.env.su:
            if set(vals) - {"disposition", "disposition_note"}:
                raise UserError("A billing run unit is computed by the dry run.")
            for unit in self:
                if unit.run_id.state != "dry_run" or unit.state != "exception":
                    raise UserError(
                        "Only an exception of a dry run awaiting review takes a disposition."
                    )
                if vals.get("disposition") == "bill" and unit.cause in (
                    "already_billed",
                    "no_amount",
                    "no_customer",
                    "term_ended",
                ):
                    raise UserError("%s cannot be billed anyway." % unit.detail)
        return super().write(vals)


# =============================================================================
# Pause / resume / cancel / renew (page 8, §8, FR-SUB-018/020/021/022)
# =============================================================================
LIFE_TERMS = frozenset(
    {
        "subscription_id",
        "action_type",
        "effective_date",
        "pause_until",
        "notice_received_on",
        "renewal_end_date",
        "escalation_pct",
        "notice_sent_on",
        "notice_channel",
        "notice_evidence",
        "reason",
    }
)


class FixSubscriptionLifecycle(models.Model):
    _name = "fix.subscription.lifecycle"
    _description = "Subscription Pause / Resume / Cancel / Renew"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    subscription_id = fields.Many2one(
        "fix.subscription", required=True, index=True, ondelete="cascade"
    )
    company_id = fields.Many2one(
        related="subscription_id.company_id", store=True, index=True, string="Company"
    )
    operating_unit_id = fields.Many2one(
        related="subscription_id.operating_unit_id", store=True, string="Operating Unit"
    )
    currency_id = fields.Many2one(related="subscription_id.currency_id", string="Currency")
    customer_id = fields.Many2one(
        related="subscription_id.customer_id", store=True, string="Customer"
    )
    name = fields.Char(compute="_compute_name", store=True)
    action_type = fields.Selection(
        [("pause", "Pause"), ("resume", "Resume"), ("cancel", "Cancel"), ("renew", "Renew")],
        required=True,
        default="pause",
    )
    reason = fields.Text(required=True)
    effective_date = fields.Date(required=True, default=fields.Date.context_today)
    pause_until = fields.Date(string="Paused Until")
    notice_received_on = fields.Date(
        string="Customer Notice Received", default=fields.Date.context_today
    )
    notice_required_days = fields.Integer(
        compute="_compute_notice", string="Notice Required (days)"
    )
    notice_ok = fields.Boolean(compute="_compute_notice", string="Notice Satisfied")
    renewal_end_date = fields.Date(string="New Term End")
    escalation_pct = fields.Float(string="Price Escalation %")
    notice_sent_on = fields.Date(string="Price Notice Sent On")
    notice_channel = fields.Selection(
        [("email", "Email"), ("sms", "SMS"), ("letter", "Letter"), ("portal", "Customer portal")]
    )
    notice_evidence = fields.Char(string="Notice Evidence (ref / document)")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending", "Awaiting Approval"),
            ("scheduled", "Approved (takes effect on date)"),
            ("applied", "Applied"),
            ("rejected", "Rejected"),
            ("void", "Void"),
        ],
        default="draft",
        required=True,
        readonly=True,
        tracking=True,
    )
    approved_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    escalation_proration_id = fields.Many2one(
        "fix.subscription.proration", readonly=True, copy=False
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "approved_by_id",
            "escalation_proration_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if len(self) == 1 and self.state != "draft":
            locked |= LIFE_TERMS
        return locked

    @api.depends("subscription_id.name", "action_type", "effective_date")
    def _compute_name(self):
        for rec in self:
            rec.name = "%s %s %s" % (
                rec.action_type or "",
                rec.subscription_id.name or "",
                rec.effective_date or "",
            )

    @api.depends(
        "action_type",
        "notice_received_on",
        "effective_date",
        "escalation_pct",
        "notice_sent_on",
        "subscription_id",
    )
    def _compute_notice(self):
        for rec in self:
            if rec.action_type == "cancel":
                tpl = rec.subscription_id.contract_id.sudo().template_id
                days = (tpl.notice_period_days if tpl else 0) or _int_param(
                    rec.env, PARAM_CANCEL_NOTICE_DAYS, DEFAULT_CANCEL_NOTICE_DAYS
                )
                rec.notice_required_days = days
                rec.notice_ok = bool(
                    rec.notice_received_on
                    and rec.effective_date
                    and (rec.effective_date - rec.notice_received_on).days >= days
                )
            elif rec.action_type == "renew" and rec.escalation_pct:
                days = _int_param(rec.env, PARAM_PRICE_NOTICE_DAYS, DEFAULT_PRICE_NOTICE_DAYS)
                rec.notice_required_days = days
                rec.notice_ok = bool(
                    rec.notice_sent_on
                    and rec.effective_date
                    and (rec.effective_date - rec.notice_sent_on).days >= days
                    and rec.notice_channel
                    and (rec.notice_evidence or "").strip()
                )
            else:
                rec.notice_required_days = 0
                rec.notice_ok = True

    @api.model_create_multi
    def create(self, vals_list):
        require_role(
            self.env, SUB_OFFICER, "Requesting a subscription pause, cancellation or renewal"
        )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state != "draft"):
                if any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in set(vals) & LIFE_TERMS):
                    raise UserError(
                        "Request %s is %s: its terms are fixed." % (rec.name, rec.state)
                    )
        return super().write(vals)

    def _validate(self):
        self.ensure_one()
        sub = self.subscription_id
        today = fields.Date.context_today(self)
        if self.effective_date < today and not self.env.su:
            raise UserError("A lifecycle change takes effect today or later (BRU-SUB-06).")
        if self.action_type == "pause":
            if sub.state != "active":
                raise UserError("Only an active subscription is paused (it is %s)." % sub.state)
            if self.pause_until and self.pause_until <= self.effective_date:
                raise UserError("A pause ends after it starts.")
        elif self.action_type == "resume":
            if sub.state != "paused":
                raise UserError("Only a paused subscription is resumed.")
        elif self.action_type == "cancel":
            if sub.state in DEAD_STATES:
                raise UserError("Subscription %s is already %s." % (sub.name, sub.state))
            if not self.notice_ok:
                raise UserError(
                    "BRU-SUB-13: cancellation needs %d days' notice; notice was received on %s for %s."
                    % (self.notice_required_days, self.notice_received_on, self.effective_date)
                )
        elif self.action_type == "renew":
            if sub.state in DEAD_STATES:
                raise UserError("Subscription %s is %s." % (sub.name, sub.state))
            if not self.renewal_end_date or (
                sub.contract_end_date and self.renewal_end_date <= sub.contract_end_date
            ):
                raise UserError("A renewal sets a new term end after the current one.")
            if self.escalation_pct < 0:
                raise UserError("An escalation is zero or more; a price cut is a plan change.")
            if self.escalation_pct and not self.notice_ok:
                raise UserError(
                    "BRU-SUB-07: a price change needs the customer told %d days ahead, with the channel "
                    "and evidence recorded." % self.notice_required_days
                )

    def action_submit(self):
        require_role(self.env, SUB_OFFICER, "Submitting a lifecycle request")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Request %s is %s." % (rec.name, rec.state))
            rec._validate()
            rec._guarded().write({"state": "pending"})
        return True

    def action_approve(self):
        """§8 guards: a pause by a Finance Manager, the others by a billing
        user; never the requester."""
        for rec in self:
            if rec.state != "pending":
                raise UserError("Request %s is %s." % (rec.name, rec.state))
            require_role(
                self.env,
                FINANCE_MANAGER if rec.action_type == "pause" else BILLING,
                "Approving a subscription %s" % rec.action_type,
            )
            _other_person(self.env, rec.create_uid, "approving %s" % rec.name)
            rec._validate()
            rec._guarded().write({"state": "scheduled", "approved_by_id": self.env.uid})
            if rec.effective_date <= fields.Date.context_today(rec):
                rec._apply()
        return True

    def action_reject(self, reason=None):
        require_role(self.env, BILLING, "Rejecting a lifecycle request")
        for rec in self:
            if rec.state != "pending":
                raise UserError("Request %s is %s." % (rec.name, rec.state))
            _other_person(self.env, rec.create_uid, "rejecting %s" % rec.name)
            rec._guarded().write({"state": "rejected"})
            rec.message_post(body="Rejected: %s" % (reason or ""))
        return True

    def action_void(self):
        require_role(self.env, SUB_OFFICER, "Voiding a lifecycle request")
        for rec in self:
            if rec.state not in ("draft", "pending", "scheduled"):
                raise UserError("Request %s is %s." % (rec.name, rec.state))
            rec._guarded().write({"state": "void"})
        return True

    def _apply(self):
        for rec in self.sudo():
            sub = rec.subscription_id
            if rec.action_type == "pause":
                sub._guarded().write({"state": "paused"})
            elif rec.action_type == "resume":
                sub._guarded().write({"state": "active"})
                if sub.next_invoice_date and sub.next_invoice_date < rec.effective_date:
                    sub.write({"next_invoice_date": rec.effective_date})
            elif rec.action_type == "cancel":
                # A04 ERP M39-F2: the cancellation settles (refund, final bill,
                # recognition stopped) on the date it takes effect
                sub.action_cancel(cancellation_date=rec.effective_date)
            elif rec.action_type == "renew":
                sub.write({"contract_end_date": rec.renewal_end_date})
                if rec.escalation_pct:
                    new = round((sub.recurring_amount or 0.0) * (1 + rec.escalation_pct / 100.0), 2)
                    proration = (
                        self.env["fix.subscription.proration"]
                        .sudo()
                        .create_for_plan_change(sub, new, effective_date=rec.effective_date)
                    )
                    proration.with_user(rec.create_uid).action_request_approval(
                        justification="Renewal escalation %.2f%% (%s)"
                        % (rec.escalation_pct, rec.name)
                    )
                    rec._guarded().write({"escalation_proration_id": proration.id})
            rec._guarded().write({"state": "applied"})
            sub.message_post(body="%s applied (%s)." % (rec.action_type.capitalize(), rec.name))
            publish(
                self.env,
                "subscription.%s"
                % {
                    "pause": "paused",
                    "resume": "resumed",
                    "cancel": "cancel_applied",
                    "renew": "renewed",
                }[rec.action_type],
                "fix.subscription",
                sub.id,
                {
                    "customer_id": sub.customer_id.id,
                    "request_id": rec.id,
                    "effective_date": str(rec.effective_date),
                },
            )

    @api.model
    def cron_apply_due(self):
        """Daily: approved requests whose date has come, and pauses whose end
        has come (FR-SUB-018 resume with schedule realignment)."""
        today = fields.Date.context_today(self)
        due = self.sudo().search([("state", "=", "scheduled"), ("effective_date", "<=", today)])
        for rec in due:
            try:
                with self.env.cr.savepoint():
                    rec._apply()
            except (UserError, ValidationError) as exc:
                rec.message_post(body="Could not apply: %s" % exc)
        ended = self.sudo().search(
            [("action_type", "=", "pause"), ("state", "=", "applied"), ("pause_until", "<=", today)]
        )
        for rec in ended:
            sub = rec.subscription_id
            if sub.state == "paused":
                sub._guarded().write({"state": "active"})
                if sub.next_invoice_date and sub.next_invoice_date < rec.pause_until:
                    sub.write({"next_invoice_date": rec.pause_until})
                sub.message_post(body="Pause %s ended: resumed." % rec.name)
        return len(due)


# =============================================================================
# Churn reasons (page 10, FR-SUB-042, §10.1 fix.churn.record)
# =============================================================================
class FixSubscriptionChurn(models.Model):
    _name = "fix.subscription.churn"
    _description = "Subscription Churn Record"
    _inherit = ["fix.guarded.mixin"]
    _order = "churn_date desc, id desc"

    subscription_id = fields.Many2one(
        "fix.subscription", required=True, index=True, ondelete="cascade"
    )
    company_id = fields.Many2one(
        related="subscription_id.company_id", store=True, index=True, string="Company"
    )
    operating_unit_id = fields.Many2one(
        related="subscription_id.operating_unit_id", store=True, string="Operating Unit"
    )
    currency_id = fields.Many2one(related="subscription_id.currency_id", string="Currency")
    customer_id = fields.Many2one(
        related="subscription_id.customer_id", store=True, string="Customer"
    )
    churn_date = fields.Date(required=True, default=fields.Date.context_today)
    churn_type = fields.Selection(
        [("logo", "Logo churn (customer lost)"), ("revenue", "Revenue churn (contraction)")],
        required=True,
        default="logo",
    )
    lost_mrr = fields.Monetary(
        currency_field="currency_id",
        readonly=True,
        string="Lost MRR",
        help="Stamped from the subscription's monthly value when recorded.",
    )
    reason_code = fields.Selection(
        [
            ("price", "Price"),
            ("service_quality", "Service quality"),
            ("competitor", "Moved to a competitor"),
            ("business_closed", "Business closed / relocated"),
            ("non_payment", "Non-payment"),
            ("consolidation", "Consolidated with another contract"),
            ("other", "Other"),
        ],
        required=True,
    )
    competitor = fields.Char()
    cohort = fields.Char(compute="_compute_cohort", store=True, string="Start Cohort")
    notes = fields.Text()

    @api.constrains("subscription_id", "churn_type")
    def _check_one_logo_churn(self):
        for rec in self.filtered(lambda r: r.churn_type == "logo"):
            if self.search_count(
                [
                    ("subscription_id", "=", rec.subscription_id.id),
                    ("churn_type", "=", "logo"),
                    ("id", "!=", rec.id),
                ]
            ):
                raise ValidationError(
                    "Logo churn is already recorded for %s." % rec.subscription_id.name
                )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"lost_mrr"}

    @api.depends("subscription_id.start_date")
    def _compute_cohort(self):
        for rec in self:
            start = rec.subscription_id.start_date
            rec.cohort = start.strftime("%Y-%m") if start else False

    @api.constrains("reason_code", "competitor")
    def _check_competitor(self):
        for rec in self:
            if rec.reason_code == "competitor" and not (rec.competitor or "").strip():
                raise ValidationError("Name the competitor the customer moved to.")

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, SUB_OFFICER, "Recording churn")
        records = super().create(vals_list)
        for rec in records:
            sub = rec.subscription_id
            if rec.churn_type == "logo" and sub.state not in DEAD_STATES:
                raise UserError(
                    "Subscription %s is %s: logo churn is recorded once it is cancelled."
                    % (sub.name, sub.state)
                )
            rec._guarded().write({"lost_mrr": sub.monthly_value})
        return records
