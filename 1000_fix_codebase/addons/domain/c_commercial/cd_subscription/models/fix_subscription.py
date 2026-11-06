# cd_subscription — M39 Subscription & recurring revenue + the M53 W4
# revenue slice (P07-M03, CD-M39-01).
#
# T02: consolidated B2B invoicing — ONE invoice per period for many jobs
# across many sites (a corporate client with 400 devices does not want 400
# invoices). T04: the W4 revenue-recognition slice (non-marketplace half);
# T06: commission CALCULATION (earning is an M12 event — pair 12; the
# computation lives in services/settlement-engine).
#
# A08 remediation (B4, 4 Nov 2026), M53-6/-9/-10/-13, F6, P1-6:
#   * fix.subscription is a finance record: plain users read it; its state,
#     dunning and refund fields change only through the actions, and a
#     held subscription is reinstated only once its overdue cycle invoices
#     are settled (M53-10);
#   * a refund is a DRAFT M20 credit note that runs the credit-note approval
#     (the requester never approves it); refund_requires_approval is computed
#     from that note's tier (M53-9);
#   * recognized_amount is the sum of the posted recognition lines — system
#     written, so a reset cannot post revenue twice (BRU-REV-26, M53-6);
#   * a manual schedule names its contract, a reason and evidence and needs a
#     routed CFO-level (DOFA Tier 4) approval before it recognises anything
#     (BRU-REV-01);
#   * the generator uses a valid obligation type and allocates the contract's
#     whole billed value, not one cycle (M53-13); allocated amounts are
#     guarded.
import math
import uuid
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.addons.cd_billing_engine.models.fix_billing_engine import m51_determine
from odoo.addons.cd_billing_engine.models.fix_finance_approval import (
    GROUP_ACCOUNTANT,
    require_role,
)
from odoo.addons.cd_tax_engine_bd.models import tax_logic
from odoo.exceptions import UserError

from libs.py.fix_events import publish  # FF-28

from . import rev_rec_engine

TWO = Decimal("0.01")

SUB_GUARDED = {
    "state",
    "dunning_step",
    "days_overdue",
    "last_refund_amount",
    "last_refund_earned",
    "refund_credit_note_id",
}
SUB_START_STATES = ("trial", "active")
# The price terms: set when the subscription is created, changed afterwards
# only through an approved price change (A04 M39 request, A08 B4).
SUB_PRICE_FIELDS = ("recurring_amount", "contract_value", "plan", "billing_cycle", "currency_id")
SUB_PRICE_GUARDED = {
    "pending_recurring_amount",
    "pending_plan",
    "price_change_requested_by_id",
    "price_change_requested_at",
    "price_change_reason",
    "cancelled_on",
    "source_quote_id",
    "source_quote_ref",
}
# Annualised price delta a second Accountant may approve; above it the
# Accounting Administrator (05-04 §7's finance-officer band, as for credit
# notes: a price cut is a revenue concession).
PARAM_PRICE_DIRECT = "cd_subscription.price_change_direct_limit"
DEFAULT_PRICE_DIRECT = 10000.0


class FixSubscription(models.Model):
    """A recurring subscription on OCA contract's pattern, billing through
    M20's AR engine."""

    _name = "fix.subscription"
    _description = "Subscription"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "next_invoice_date, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    name = fields.Char(required=True)
    customer_id = fields.Many2one(
        "res.partner", string="Customer", required=True, index=True, ondelete="restrict"
    )
    contract_id = fields.Many2one(
        "fix.contract", string="Contract", index=True, ondelete="set null"
    )
    plan = fields.Selection(
        [("basic", "Basic"), ("standard", "Standard"), ("premium", "Premium")],
        required=True,
        default="standard",
    )
    billing_cycle = fields.Selection(
        [("monthly", "Monthly"), ("quarterly", "Quarterly"), ("annual", "Annual")],
        required=True,
        default="monthly",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    recurring_amount = fields.Monetary(
        string="Recurring Amount", currency_field="currency_id", required=True
    )
    state = fields.Selection(
        [
            ("trial", "Trial"),
            ("active", "Active"),
            ("past_due", "Past Due"),
            ("hold", "Service Hold"),
            ("paused", "Paused"),
            ("cancelled", "Cancelled"),
            ("churned", "Churned"),
        ],
        default="active",
        required=True,
        tracking=True,
    )
    dunning_step = fields.Selection(
        [
            ("none", "None"),
            ("reminder", "Reminder (L1)"),
            ("final", "Final Notice (L2)"),
            ("escalate", "Service Suspended (L3)"),
        ],
        default="none",
        required=True,
        tracking=True,
    )
    grace_period_days = fields.Integer(default=15, help="Days before hold escalation")
    days_overdue = fields.Integer(default=0)
    start_date = fields.Date(default=fields.Date.today, required=True)
    next_invoice_date = fields.Date(required=True, default=fields.Date.today)
    consolidated = fields.Boolean(
        default=True,
        help="T02: roll this subscription's period charges into the customer's "
        "ONE consolidated invoice (with jobs and other subscriptions)",
    )
    # --- IFRS 15 contract (A08 M53) -----------------------------------
    contract_value = fields.Monetary(
        string="Transaction Price",
        currency_field="currency_id",
        tracking=True,
        help="IFRS 15 transaction price for the contract term (VAT excluded), allocated "
        "to the performance obligations by relative standalone selling price",
    )
    contract_end_date = fields.Date(string="Contract End", tracking=True)
    obligation_ids = fields.One2many(
        "fix.performance.obligation", "subscription_id", string="Performance Obligations"
    )
    charge_ids = fields.One2many("fix.subscription.charge", "subscription_id", string="Charges")
    last_refund_amount = fields.Monetary(
        string="Last Refund (net)", currency_field="currency_id", readonly=True, copy=False
    )
    last_refund_earned = fields.Monetary(
        string="Earned at Cancellation", currency_field="currency_id", readonly=True, copy=False
    )
    refund_requires_approval = fields.Boolean(
        string="Refund Needs Manager Approval",
        compute="_compute_refund_requires_approval",
        help="Computed from the refund credit note: True when its amount sits above "
        "the credit-note direct band, so the Accounting Administrator approves it.",
    )
    refund_credit_note_id = fields.Many2one(
        "fix.credit.note", string="Refund Credit Note", readonly=True, copy=False
    )

    # ---- price change (two-person; A04's proration when installed) --------
    pending_recurring_amount = fields.Monetary(
        string="Requested Recurring Amount", currency_field="currency_id", readonly=True, copy=False
    )
    pending_plan = fields.Char(string="Requested Plan", readonly=True, copy=False)
    price_change_requested_by_id = fields.Many2one(
        "res.users", string="Price Change Requested By", readonly=True, copy=False
    )
    price_change_requested_at = fields.Datetime(readonly=True, copy=False)
    price_change_reason = fields.Char(readonly=True, copy=False)
    cancelled_on = fields.Date(string="Cancelled On", readonly=True, copy=False)
    # the accepted M41 quotation a subscription was created from (A04 hand-off)
    source_quote_id = fields.Integer(string="Source Quotation ID", readonly=True, copy=False, index=True)
    source_quote_ref = fields.Char(string="Source Quotation", readonly=True, copy=False)

    _source_quote_unique = models.Constraint(
        "UNIQUE (source_quote_id)", "One subscription per accepted quotation"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | SUB_GUARDED | SUB_PRICE_GUARDED

    def _fix_form_locked_fields(self) -> set:
        return super()._fix_form_locked_fields() | set(SUB_PRICE_FIELDS)

    def write(self, vals):
        if not self._fix_guard_open():
            touched = [
                f
                for f in set(SUB_PRICE_FIELDS) & set(vals)
                for sub in self
                if sub._fix_guard_differs(f, vals[f], sub[f])
            ]
            if touched:
                raise UserError(
                    "The price of a subscription (%s) changes only through Request Price "
                    "Change, approved by a second person." % ", ".join(sorted(set(touched)))
                )
        return super().write(vals)

    def _price_delta_annual(self, new_amount) -> float:
        self.ensure_one()
        cycles_a_year = {"monthly": 12, "quarterly": 4, "annual": 1}[self.billing_cycle]
        return abs((new_amount or 0.0) - (self.recurring_amount or 0.0)) * cycles_a_year

    def action_request_price_change(self, new_amount, plan=None, reason=""):
        """A mid-term price (or plan) change: never applied by its requester.
        With A04's proration service the change is a draft proration routed
        through its DOFA approval (it applies the price); otherwise a second
        person approves it here (action_approve_price_change)."""
        require_role(self.env, GROUP_ACCOUNTANT, "Requesting a subscription price change")
        if not (reason or "").strip():
            raise UserError("State why the price changes.")
        if new_amount is None or new_amount < 0:
            raise UserError("A recurring amount is zero or more.")
        Proration = (
            self.env["fix.subscription.proration"]
            if "fix.subscription.proration" in self.env
            else None
        )
        out = []
        for sub in self:
            if sub.state in ("cancelled", "churned"):
                raise UserError("Subscription %s is %s." % (sub.name, sub.state))
            if Proration is not None and hasattr(Proration, "create_for_plan_change"):
                proration = Proration.create_for_plan_change(
                    sub, new_amount, to_plan=plan, effective_date=fields.Date.context_today(sub)
                )
                if hasattr(proration, "action_request_approval"):
                    proration.action_request_approval(justification=reason)
                out.append(proration)
                continue
            sub._guarded().write(
                {
                    "pending_recurring_amount": new_amount,
                    "pending_plan": plan or False,
                    "price_change_requested_by_id": self.env.uid,
                    "price_change_requested_at": fields.Datetime.now(),
                    "price_change_reason": reason.strip()[:250],
                }
            )
            sub.message_post(
                body="Price change requested by %s: %.2f -> %.2f (%s)."
                % (self.env.user.name, sub.recurring_amount, new_amount, reason)
            )
            out.append(sub)
        return out

    def action_approve_price_change(self):
        """The second person: an Accountant within the band (annualised delta),
        the Accounting Administrator above it; never the requester."""
        from odoo.addons.cd_billing_engine.models.fix_finance_approval import (
            GROUP_ADMINISTRATOR,
            float_param,
        )

        for sub in self:
            if not sub.price_change_requested_by_id:
                raise UserError("Subscription %s has no price change awaiting approval." % sub.name)
            if not self.env.su:
                band = float_param(self.env, PARAM_PRICE_DIRECT, DEFAULT_PRICE_DIRECT)
                group = (
                    GROUP_ACCOUNTANT
                    if sub._price_delta_annual(sub.pending_recurring_amount) <= band
                    else GROUP_ADMINISTRATOR
                )
                require_role(self.env, group, "Approving this price change")
                if self.env.user in (sub.price_change_requested_by_id | sub.create_uid):
                    raise UserError(
                        "Segregation of duties: you requested or raised this subscription; "
                        "another person approves its price change."
                    )
            vals = {"recurring_amount": sub.pending_recurring_amount}
            if sub.pending_plan:
                vals["plan"] = sub.pending_plan
            old = sub.recurring_amount
            sub.sudo()._guarded().write(
                dict(
                    vals,
                    pending_recurring_amount=0.0,
                    pending_plan=False,
                    price_change_requested_by_id=False,
                    price_change_requested_at=False,
                    price_change_reason=False,
                )
            )
            sub.message_post(
                body="Price change %.2f -> %.2f approved by %s."
                % (old, sub.recurring_amount, self.env.user.name)
            )
        return True

    # ---- the A04 hand-off: an accepted subscription quotation ----------------
    @api.model
    def consume_quotation_accepted(self, event: dict) -> dict:
        """R8 consumer of quotation.accepted: a SUBSCRIPTION quotation becomes
        its subscription, once (keyed on the quotation). The payload is a
        claim: the quotation is re-read and must be accepted."""
        from odoo.exceptions import AccessError

        if not self.env.su:
            raise AccessError("The quotation consumer runs only from the event relay.")
        payload = event.get("payload") or {}
        if "fix.quotation" not in self.env:
            return {"skipped": "no quotation module"}
        try:
            quote_id = int(event.get("aggregate_id") or 0)
        except (TypeError, ValueError):
            quote_id = 0
        quote = self.env["fix.quotation"].sudo().browse(quote_id).exists() if quote_id else None
        if not quote:
            raise UserError("Quotation hand-back refused: there is no quotation #%s." % quote_id)
        quote_type = quote["quote_type"] if "quote_type" in quote._fields else None
        if quote_type != "subscription":
            return {"skipped": "quote type %s" % (quote_type or payload.get("quote_type"))}
        existing = self.sudo().search([("source_quote_id", "=", quote.id)], limit=1)
        if existing:
            return {"model": self._name, "id": existing.id, "created": False}
        if quote.state != "accepted":
            raise UserError(
                "Quotation hand-back refused: %s is %s, not accepted." % (quote.name, quote.state)
            )
        company = quote.company_id if "company_id" in quote._fields else self.env.company
        ou = quote["operating_unit_id"] if "operating_unit_id" in quote._fields else False
        ou = ou or self.env["operating.unit"].sudo().search([("company_id", "=", company.id)], limit=1)
        if not ou:
            raise UserError("Quotation hand-back refused: %s has no operating unit." % company.name)
        months = (quote["contract_months"] if "contract_months" in quote._fields else 0) or 12
        start = (
            quote["contract_start"] if "contract_start" in quote._fields else False
        ) or fields.Date.context_today(self)
        value = quote["accepted_value"] if "accepted_value" in quote._fields else 0.0
        value = value or quote.value or 0.0
        if value <= 0:
            raise UserError("Quotation hand-back refused: %s carries no value." % quote.name)
        sub = self.sudo()._guarded().create(
            {
                "name": "%s — %s" % (quote.name, quote.customer_id.name),
                "company_id": company.id,
                "operating_unit_id": ou.id,
                "customer_id": quote.customer_id.id,
                "currency_id": quote.currency_id.id,
                "billing_cycle": "monthly",
                "recurring_amount": round(value / months, 2),
                "contract_value": value,
                "start_date": start,
                "next_invoice_date": start,
                "contract_end_date": start + relativedelta(months=months) - timedelta(days=1),
                "state": "active",
                "source_quote_id": quote.id,
                "source_quote_ref": quote.name,
            }
        )
        sub.message_post(body="Created from accepted quotation %s." % quote.name)
        return {"model": self._name, "id": sub.id, "created": True}

    @api.depends("refund_credit_note_id.amount", "refund_credit_note_id.state")
    def _compute_refund_requires_approval(self):
        for sub in self:
            note = sub.refund_credit_note_id.sudo()
            sub.refund_requires_approval = bool(note) and note._dofa_current_tier() != "tier_0"

    @api.model_create_multi
    def create(self, vals_list):
        if self._fix_guard_open():
            return super().create(vals_list)
        for vals in vals_list:
            if vals.get("state", "active") not in SUB_START_STATES:
                raise UserError("A subscription starts on trial or active.")
            forged = (SUB_GUARDED - {"state"}) & {k for k, v in vals.items() if v}
            if forged:
                self._fix_guard_refuse(forged)
        records = super(FixSubscription, self._guarded()).create(vals_list)
        return records.with_env(self.env)

    @api.constrains("recurring_amount")
    def _check_amount(self):
        for sub in self:
            if sub.recurring_amount < 0:
                raise UserError("The recurring amount cannot be negative")

    def _cycle_days(self) -> int:
        return {"monthly": 30, "quarterly": 91, "annual": 365}[self.billing_cycle]

    def action_generate_charge(self):
        """AUT-025: the cycle charge. Every cycle is a fix.subscription.charge
        with its own draft AR invoice (one line, VAT determined by M51) in
        the SUBSCRIPTION's company, so a charge is billed exactly once and
        the contract's billed amount is real. Finance issues the invoice
        (Mushak 6.3 + number); its issue credits the contract liability, not
        revenue (IFRS 15 — recognition runs from the performance
        obligations). A consolidated subscription's invoices are rolled into
        the customer's ONE period bill by M20's Consolidated Corporate
        Invoices (one bill, not N)."""
        Charge = self.env["fix.subscription.charge"]
        for sub in self:
            if sub.state != "active":
                continue
            if sub.recurring_amount <= 0:
                raise UserError("Subscription %s has no recurring amount to charge" % sub.name)
            period_start = sub.next_invoice_date
            period_end = period_start + timedelta(days=sub._cycle_days() - 1)
            charge = Charge.create(
                {
                    "company_id": sub.company_id.id,
                    "operating_unit_id": sub.operating_unit_id.id,
                    "subscription_id": sub.id,
                    "period_start": period_start,
                    "period_end": period_end,
                    "amount": sub.recurring_amount,
                }
            )
            charge._create_invoice()
            publish(
                self.env,
                "subscription.charged",
                "fix.subscription",
                sub.id,
                {
                    "customer_id": sub.customer_id.id,
                    "amount": sub.recurring_amount,
                    "period_days": sub._cycle_days(),
                },
            )
            sub.next_invoice_date = sub.next_invoice_date + timedelta(days=sub._cycle_days())

    def _cycle_months(self) -> int:
        return {"monthly": 1, "quarterly": 3, "annual": 12}[self.billing_cycle]

    def _billed_cycles(self) -> int:
        """The billing cycles in the contract term (a partial cycle bills in
        full), or 1 without a contract end."""
        self.ensure_one()
        if not self.contract_end_date or self.contract_end_date <= self.start_date:
            return 1
        delta = relativedelta(self.contract_end_date, self.start_date)
        months = delta.years * 12 + delta.months + (1 if delta.days > 0 else 0)
        return max(1, math.ceil(months / self._cycle_months()))

    def _transaction_price(self) -> float:
        """IFRS 15 transaction price: the contract value, else what the
        contract bills over its term (recurring amount x billed cycles)."""
        self.ensure_one()
        if self.contract_value:
            return self.contract_value
        return round((self.recurring_amount or 0.0) * self._billed_cycles(), 2)

    def action_generate_revrec_schedule(self):
        """IFRS 15 Revenue Schedule Generation (FLAW-39.1).
        Ratably distributes the contract's transaction price over the
        performance period (A08 M53-13: the obligation type was invalid, so
        this crashed for every contract without obligations, and it
        scheduled one cycle of a twelve-cycle contract)."""
        require_role(self.env, GROUP_ACCOUNTANT, "Generating a revenue schedule")
        Obligation = self.env["fix.performance.obligation"]
        created_schedules = self.env["fix.revenue.schedule"]
        for sub in self:
            val = sub._transaction_price()
            if val <= 0:
                raise UserError(
                    "Subscription %s requires contract value or recurring amount for revenue recognition."
                    % sub.name
                )
            if not sub.obligation_ids:
                end_date = sub.contract_end_date or (
                    sub.start_date + timedelta(days=sub._cycle_days())
                )
                ob = Obligation._guarded().create(
                    {
                        "subscription_id": sub.id,
                        "name": f"Subscription Service Delivery ({sub.name})",
                        "obligation_type": "amc_service",
                        "standalone_price": val,
                        "allocated_amount": val,
                        "satisfaction": "over_time",
                        "start_date": sub.start_date,
                        "end_date": end_date,
                        "state": "allocated",
                    }
                ).with_env(self.env)
                ob.action_create_schedule()
                if ob.schedule_id:
                    created_schedules |= ob.schedule_id
            else:
                if sub.obligation_ids.filtered(lambda o: o.state == "draft"):
                    sub._allocate_price(val)
                for ob in sub.obligation_ids:
                    if ob.state == "allocated" and not ob.schedule_id:
                        ob.action_create_schedule()
                        if ob.schedule_id:
                            created_schedules |= ob.schedule_id
            publish(
                self.env,
                "subscription.revrec_scheduled",
                "fix.subscription",
                sub.id,
                {"subscription": sub.name, "amount": float(val)},
            )
        return created_schedules

    def action_trigger_dunning(self, as_of=None):
        """Automated 3-stage dunning workflow (FLAW-39.2).

        Stage 1 (day 3 to day 7): reminder notice + SMS.
        Stage 2 (day 8 to grace expiry): final notice + formal email.
        Stage 3 (past grace): service-order lock and entitlement suspension.

        `grace_period_days` is the escalation boundary and is configurable per
        subscription. The first implementation of this ladder hard-coded the
        docstring's "Day 14" as `min(grace_period_days, 13)`, which overrode
        the customer's agreed grace period and moved every stage a day early:
        a 7-day-overdue account was already at Final and a 15-day one was
        suspended (A04 audit, 2026-10-31).
        """
        as_of = as_of or fields.Date.today()
        Charge = self.env["fix.subscription.charge"]
        overdue_basis = getattr(Charge, "_fix_overdue_unpaid", None)
        for sub in self:
            if sub.state in ("cancelled", "churned"):
                continue
            if overdue_basis is not None:
                # A04 M39-2: dunning keys off cycle invoices past due and unpaid
                charges = overdue_basis(subscription=sub, as_of=as_of)
                dues = [c.invoice_due_date for c in charges if c.invoice_due_date]
                if not dues:
                    continue
                overdue = (as_of - min(dues)).days
                sub._guarded().write({"days_overdue": overdue})
            elif sub.next_invoice_date and as_of > sub.next_invoice_date:
                overdue = (as_of - sub.next_invoice_date).days
                sub._guarded().write({"days_overdue": overdue})
                grace = sub.grace_period_days or 15
                # A grace period shorter than the reminder band collapses the
                # band rather than delaying escalation past what was agreed.
                reminder_until = min(7, grace)
                if overdue < 3:
                    continue
                elif overdue <= reminder_until:
                    sub._guarded().write({"state": "past_due", "dunning_step": "reminder"})
                    publish(
                        self.env,
                        "subscription.dunning_reminder_sms",
                        "fix.subscription",
                        sub.id,
                        {
                            "customer_id": sub.customer_id.id,
                            "days_overdue": overdue,
                            "step": "reminder",
                        },
                    )
                elif overdue <= grace:
                    sub._guarded().write({"state": "past_due", "dunning_step": "final"})
                    publish(
                        self.env,
                        "subscription.dunning_final_email",
                        "fix.subscription",
                        sub.id,
                        {
                            "customer_id": sub.customer_id.id,
                            "days_overdue": overdue,
                            "step": "final",
                        },
                    )
                else:
                    # Past the agreed grace period: service-order lock and
                    # entitlement suspension.
                    sub._guarded().write({"state": "hold", "dunning_step": "escalate"})
                    publish(
                        self.env,
                        "subscription.service_order_locked",
                        "fix.subscription",
                        sub.id,
                        {
                            "customer_id": sub.customer_id.id,
                            "days_overdue": overdue,
                            "step": "service_lock",
                        },
                    )
                publish(
                    self.env,
                    "subscription.dunning_escalated",
                    "fix.subscription",
                    sub.id,
                    {
                        "customer_id": sub.customer_id.id,
                        "dunning_step": sub.dunning_step,
                        "days_overdue": overdue,
                        "state": sub.state,
                    },
                )

    def _overdue_unpaid_invoices(self):
        """Cycle invoices past their due date with money still owed."""
        self.ensure_one()
        today = fields.Date.context_today(self)
        Charge = self.env["fix.subscription.charge"]
        if hasattr(Charge, "_fix_overdue_unpaid"):
            return Charge._fix_overdue_unpaid(subscription=self, as_of=today).mapped("invoice_id")
        invoices = self.charge_ids.mapped("invoice_id").sudo()
        return invoices.filtered(
            lambda i: i.state == "issued"
            and i.amount_residual > 0.005
            and i.invoice_date + timedelta(days=i._payment_terms_days()) < today
        )

    def action_reinstate(self):
        """Reinstate subscription after payment receipt (A08 M53-10: only
        finance reinstates, and only once the overdue cycle invoices are
        settled — a plain user lifted a service hold with nothing paid)."""
        require_role(self.env, GROUP_ACCOUNTANT, "Reinstating a subscription")
        for sub in self:
            if sub.state != "hold":
                raise UserError(
                    "Subscription %s is %s: only a suspended (service hold) subscription is "
                    "reinstated." % (sub.name, sub.state)
                )
            unpaid = sub._overdue_unpaid_invoices()
            if unpaid:
                raise UserError(
                    "Subscription %s still owes %.2f on overdue invoice(s) %s: it is reinstated "
                    "once they are paid."
                    % (sub.name, sum(unpaid.mapped("amount_residual")), ", ".join(unpaid.mapped("name")))
                )
            sub._guarded().write(
                {
                    "state": "active",
                    "dunning_step": "none",
                    "days_overdue": 0,
                }
            )
            publish(
                self.env,
                "subscription.reinstated",
                "fix.subscription",
                sub.id,
                {
                    "customer_id": sub.customer_id.id,
                },
            )

    def action_cancel(self):
        require_role(self.env, GROUP_ACCOUNTANT, "Cancelling a subscription")
        for sub in self:
            sub._guarded().write(
                {"state": "cancelled", "cancelled_on": fields.Date.context_today(sub)}
            )
            # T03: subscription dunning stops on cancellation — outstanding
            # balances ride the M20 collections ladder instead
            publish(self.env, "subscription.cancelled", "fix.subscription", sub.id, {})

    def action_request_refund(self, cancellation_date=None, fee_pct=0.0):
        """Prorated mid-cycle cancellation and credit note flow.
        Calculates earned vs unearned revenue and enforces BDT 25,000 approval threshold.

        A08 M53: the figures are kept on the subscription; the cycle's issued
        invoice gets a DRAFT credit note for the unearned share (gross of VAT
        pro rata) that runs M20's approval ladder; the performance
        obligations recognise up to the cancellation date and stop."""
        require_role(self.env, GROUP_ACCOUNTANT, "Requesting a subscription refund")
        today = fields.Date.context_today(self)
        cancellation_date = fields.Date.to_date(cancellation_date) if cancellation_date else today
        if cancellation_date != today and not self.env.su:
            # A04 M39: a cancellation is dated the day it is recorded — a
            # backdated one would refund service already delivered
            raise UserError(
                "A cancellation is dated today (%s), not %s: it is never backdated."
                % (today, cancellation_date)
            )
        results = []
        for sub in self:
            if sub.state in ("cancelled", "churned"):
                raise UserError("Subscription %s is already %s" % (sub.name, sub.state))
            # Term calculation based on last cycle start to next invoice date
            cycle_days = sub._cycle_days()
            start = sub.next_invoice_date - timedelta(days=cycle_days)
            end = sub.next_invoice_date
            res = rev_rec_engine.compute_cancellation_refund(
                total_amount=sub.recurring_amount,
                start_date=start,
                end_date=end,
                cancellation_date=cancellation_date,
                cancellation_fee_pct=fee_pct,
            )
            sub._guarded().write(
                {
                    "state": "cancelled",
                    "cancelled_on": cancellation_date,
                    "last_refund_amount": float(res.net_refund_payable),
                    "last_refund_earned": float(res.earned_revenue),
                }
            )
            sub._refund_credit_note(res, start)
            sub._stop_recognition(cancellation_date)
            publish(
                self.env,
                "subscription.refund_requested",
                "fix.subscription",
                sub.id,
                {
                    "customer_id": sub.customer_id.id,
                    "net_refund": float(res.net_refund_payable),
                    "earned_revenue": float(res.earned_revenue),
                    "unearned_refund": float(res.unearned_refund),
                    "requires_manager_approval": sub.refund_requires_approval,
                },
            )
            results.append(res)
        return results

    def _refund_credit_note(self, res, cycle_start):
        """A draft credit note for the unearned share of the cycle invoice."""
        self.ensure_one()
        net = float(res.net_refund_payable)
        if net <= 0 or not self.recurring_amount:
            return
        charge = self.charge_ids.filtered(
            lambda c: (
                c.period_start == cycle_start
                and c.invoice_id.state in ("issued", "paid", "credited")
            )
        )[:1]
        invoice = charge.invoice_id
        if not invoice:
            self.message_post(
                body="Refund of %s computed; no issued invoice for the cycle starting %s — "
                "raise the credit note in M20 once the cycle invoice is issued."
                % (round(net, 2), cycle_start)
            )
            return
        open_credit = invoice.total_payable - invoice.credited_amount
        amount = invoice.currency_id.round(
            min(invoice.total_payable * net / self.recurring_amount, open_credit)
        )
        if amount <= 0:
            return
        note = self.env["fix.credit.note"].create(
            {
                "company_id": invoice.company_id.id,
                "operating_unit_id": invoice.operating_unit_id.id,
                "invoice_id": invoice.id,
                "amount": amount,
                "reason_code": "subscription_refund",
            }
        )
        self._guarded().write({"refund_credit_note_id": note.id})
        note.message_post(
            body="Refund of the unearned share of %s on cancellation: a draft credit note "
            "for finance to submit; it is approved by someone other than the requester "
            "(M20 credit-note ladder)." % self.name
        )

    def _stop_recognition(self, cancellation_date):
        """Recognise every obligation up to the cancellation, then stop it."""
        self.ensure_one()
        for obligation in self.obligation_ids.filtered(lambda o: o.state != "cancelled"):
            schedule = obligation.schedule_id
            if schedule and schedule.state == "active":
                schedule.action_recognize_period(as_of=cancellation_date)
                if schedule.state == "active":
                    schedule._guarded().write(
                        {"state": "cancelled", "cancelled_date": cancellation_date}
                    )
            obligation._guarded().write(
                {"state": "cancelled" if obligation.state != "satisfied" else "satisfied"}
            )

    def action_allocate_price(self):
        """IFRS 15 step 4: allocate the transaction price to the performance
        obligations by relative standalone selling price, at 2dp half-up; the
        rounding residue lands on the largest obligation so the allocation
        sums EXACTLY to the price. A contract whose obligations are already
        scheduled is a contract MODIFICATION and is refused here."""
        for sub in self:
            if sub.contract_value <= 0:
                raise UserError("Enter the transaction price of %s first" % sub.name)
            sub._allocate_price(sub.contract_value)

    def _allocate_price(self, contract_value):
        for sub in self:
            obligations = sub.obligation_ids.filtered(lambda o: o.state != "cancelled")
            if not obligations:
                raise UserError(
                    "Add the performance obligations of %s (AMC service, workmanship "
                    "warranty, parts) before allocating the price" % sub.name
                )
            if obligations.filtered(lambda o: o.state in ("scheduled", "satisfied")):
                raise UserError(
                    "Obligations of %s are already scheduled — a price change is a contract "
                    "modification; cancel and re-create the affected obligations" % sub.name
                )
            total_ssp = sum(obligations.mapped("standalone_price"))
            if total_ssp <= 0:
                raise UserError("The obligations of %s carry no standalone price" % sub.name)
            price = Decimal(str(contract_value)).quantize(TWO, ROUND_HALF_UP)
            ssp = [Decimal(str(o.standalone_price)) for o in obligations]
            shares = [
                (price * p / Decimal(str(total_ssp))).quantize(TWO, ROUND_HALF_UP) for p in ssp
            ]
            largest = max(range(len(ssp)), key=lambda i: ssp[i])
            shares[largest] += price - sum(shares, Decimal("0"))
            for obligation, share in zip(obligations, shares, strict=True):
                obligation._guarded().write({"allocated_amount": float(share), "state": "allocated"})

    @api.model
    def generate_consolidated_b2b_invoice(
        self,
        customer_id: int,
        period_start: date,
        period_end: date,
        device_lines: list[dict] | None = None,
    ):
        """T02 / R05-M02-T01: Consolidated B2B Invoicing demonstration & engine.
        ONE master invoice per period for an enterprise customer across 400+ devices
        and multiple branch sites (with itemized asset-level lines and Mushak 6.3)."""
        customer = self.env["res.partner"].browse(customer_id)
        # The master invoice is issued by the ACTIVE company, and its
        # operating unit must belong to that same company (a cross-company
        # OU would post the Mushak row against the wrong legal entity).
        company = self.env.company
        operating_unit = self.env["operating.unit"].search(
            [("company_id", "=", company.id)], limit=1
        )

        # 400 devices demonstration support
        device_lines = device_lines or []
        lines_data = []
        total_taxable = Decimal("0.00")
        total_vat = Decimal("0.00")
        vat_rate = Decimal("0.15")  # standard statutory 15% VAT

        for line in device_lines:
            taxable = Decimal(str(line.get("amount", 250.00))).quantize(
                Decimal("0.01"), ROUND_HALF_UP
            )
            vat = (taxable * vat_rate).quantize(Decimal("0.01"), ROUND_HALF_UP)
            total_taxable += taxable
            total_vat += vat
            lines_data.append(
                {
                    "description": line.get("description", "Device Maintenance & Support"),
                    "device_id": line.get("device_id"),
                    "serial_number": line.get("serial_number", ""),
                    "branch_name": line.get("branch_name", "Head Office"),
                    "taxable_amount": float(taxable),
                    "vat_amount": float(vat),
                    "line_total": float(taxable + vat),
                }
            )

        invoice_vals = {
            "company_id": company.id,
            "customer_id": customer.id,
            # False when the company has no operating unit: the required
            # field then fails loudly at create, never lands on a magic id
            "operating_unit_id": operating_unit.id,
            "source_model": "fix.subscription.consolidated",
            "source_id": customer.id,
            "invoice_date": period_end,
            "taxable_amount": float(total_taxable),
            "vat_amount": float(total_vat),
            "total_payable": float(total_taxable + total_vat),
            "state": "issued",
        }

        # Mushak 6.3 Register row creation
        year = period_end.year
        mushak_no = f"{year}-C{customer.id:04d}-{len(device_lines):04d}"
        invoice_vals["mushak_ref"] = mushak_no

        publish(
            self.env,
            "invoice.consolidated_b2b_created",
            "fix.ar.invoice",
            customer.id,
            {
                "customer_id": customer.id,
                "customer_name": customer.name or "Corporate Client",
                "period_start": str(period_start),
                "period_end": str(period_end),
                "total_payable": float(total_taxable + total_vat),
                "taxable_amount": float(total_taxable),
                "vat_amount": float(total_vat),
                "device_count": len(device_lines),
                "mushak_no": mushak_no,
            },
        )

        return {
            "invoice": invoice_vals,
            "line_count": len(lines_data),
            "device_count": len(device_lines),
            "mushak_no": mushak_no,
            "total_taxable": float(total_taxable),
            "total_vat": float(total_vat),
            "total_payable": float(total_taxable + total_vat),
            "lines": lines_data,
        }


class FixRevenueSchedule(models.Model):
    """M53's W4 slice (T04): revenue RECOGNITION for the non-marketplace
    half — subscriptions, contracts and protection plans recognized over
    their term. AUT-025's monthly split; the ledger posts from here.

    BRU-LOY-12's shape applied to contracts: fee revenue is recognized over
    the period, never at the point of sale."""

    _name = "fix.revenue.schedule"
    _description = "Revenue Recognition Schedule"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.dofa.mixin"]
    _order = "start_date, id"
    # BRU-REV-01: a manual schedule is approved at CFO level (DOFA Tier 4),
    # routed through M63; generated schedules need no approval.
    _approval_domain = "revenue_manual_schedule"
    _approval_apply_method = "action_dofa_approve"
    _approval_routed = True

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    source_model = fields.Char(string="Source Model", required=True, index=True)
    source_id = fields.Integer(string="Source ID", required=True, index=True)
    description = fields.Char(required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    total_amount = fields.Monetary(
        string="Deferred Amount", currency_field="currency_id", required=True
    )
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    recognized_amount = fields.Monetary(
        string="Recognized",
        currency_field="currency_id",
        compute="_compute_recognized",
        store=True,
        copy=False,
        help="The sum of the posted recognition lines: system written, never typed "
        "(BRU-REV-26 — a reset re-posted revenue).",
    )
    contract_id = fields.Many2one(
        "fix.contract",
        string="Contract",
        index=True,
        help="A manual schedule's contract (BRU-REV-01): required for a manual schedule.",
    )
    subscription_id = fields.Many2one(
        "fix.subscription",
        string="Subscription Contract",
        index=True,
        help="A manual schedule may name the subscription contract instead.",
    )
    manual_reason = fields.Text(string="Manual Schedule Reason")
    evidence_ref = fields.Char(string="Evidence Reference")
    deferred_balance = fields.Monetary(
        string="Deferred Balance",
        currency_field="currency_id",
        compute="_compute_deferred_balance",
        store=True,
        help="Contract liability still to recognise (total - recognised)",
    )
    line_ids = fields.One2many(
        "fix.revenue.recognition.line", "schedule_id", string="Recognition Postings"
    )
    cancelled_date = fields.Date(string="Cancelled On", readonly=True, copy=False)
    state = fields.Selection(
        [
            ("draft", "Awaiting CFO Approval (manual)"),
            ("active", "Active"),
            ("complete", "Complete"),
            ("cancelled", "Cancelled"),
        ],
        default="active",
        required=True,
        tracking=True,
    )
    _source_schedule_unique = models.Constraint(
        "UNIQUE (source_model, source_id)", "One recognition schedule per source document"
    )

    SCHEDULE_GUARDED = {"state", "cancelled_date", "recognized_amount"}
    SCHEDULE_LOCKED = (
        "total_amount",
        "start_date",
        "end_date",
        "source_model",
        "source_id",
        "company_id",
        "contract_id",
        "subscription_id",
        "manual_reason",
        "evidence_ref",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self.SCHEDULE_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" or r.approval_state == "pending" for r in self):
            locked |= set(self.SCHEDULE_LOCKED)
        return locked

    def write(self, vals):
        if not self._fix_guard_open():
            touched = set(self.SCHEDULE_LOCKED) & set(vals)
            if touched and self.filtered(lambda r: r.state != "draft" or r.line_ids):
                raise UserError(
                    "A released schedule is never edited (BRU-REV-04): a modification is a new "
                    "schedule. %s cannot change." % ", ".join(sorted(touched))
                )
        return super().write(vals)

    @api.depends("line_ids.amount")
    def _compute_recognized(self):
        for schedule in self:
            schedule.recognized_amount = round(sum(schedule.line_ids.mapped("amount")), 2)

    # ---- BRU-REV-01: the manual schedule's CFO approval ----------------------
    def _is_manual(self) -> bool:
        self.ensure_one()
        return (self.source_model or "manual") == "manual"

    def _dofa_amount(self) -> float:
        self.ensure_one()
        return self.total_amount if self._is_manual() else 0.0

    def _dofa_thresholds(self):
        # every manual schedule, whatever its value, is a CFO decision
        return [(0.0, "tier_0"), (float("inf"), "tier_4")]

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "BDT %.2f (manual revenue schedule)" % self._dofa_amount()

    @api.depends("total_amount", "source_model")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def _contract_value(self) -> float:
        self.ensure_one()
        if self.subscription_id:
            return self.subscription_id._transaction_price()
        if self.contract_id:
            contract = self.contract_id
            days = max((contract.date_end - contract.date_start).days, 1)
            return round(contract.annual_value * math.ceil(days / 365.0), 2)
        return 0.0

    def _check_manual_basis(self):
        for schedule in self.filtered(lambda s: s._is_manual()):
            contract = schedule.contract_id or schedule.subscription_id
            if not contract:
                raise UserError(
                    "A manual revenue schedule names the contract it recognises (BRU-REV-01)."
                )
            if contract.company_id != schedule.company_id:
                raise UserError("The contract belongs to another company.")
            if not (schedule.manual_reason or "").strip() or not (
                schedule.evidence_ref or ""
            ).strip():
                raise UserError(
                    "A manual revenue schedule carries a reason and evidence (BRU-REV-01)."
                )
            ceiling = schedule._contract_value()
            if schedule.total_amount > ceiling + 0.005:
                raise UserError(
                    "Manual schedule of %.2f exceeds the value of %s (%.2f)."
                    % (schedule.total_amount, contract.display_name, ceiling)
                )

    def action_request_cfo_approval(self):
        """Route a manual schedule to the CFO (DOFA Tier 4) through M63."""
        require_role(self.env, GROUP_ACCOUNTANT, "Requesting approval of a manual schedule")
        for schedule in self:
            if not schedule._is_manual() or schedule.state != "draft":
                raise UserError("Only a manual schedule awaiting approval is routed")
            schedule._check_manual_basis()
            schedule.action_request_approval(justification=schedule.manual_reason)
        return True

    def action_dofa_approve(self):
        """The CFO's decision (from the M63 inbox): the DOFA checks (Tier 4
        group, approver is not the creator), then the schedule goes live."""
        self._approval_assert_routed()
        for schedule in self:
            if schedule.state != "draft":
                raise UserError("Schedule %s is not awaiting approval" % schedule.display_name)
            if not self.env.su:
                task = schedule._approval_task()
                conflicted = (
                    schedule.create_uid
                    | schedule.approval_request_id.requested_by_id
                    | schedule.approval_amount_changed_by_id
                )
                if (self.env.user | task.on_behalf_of_id) & conflicted:
                    raise UserError(
                        "Segregation of duties: a manual revenue release is never self-approved."
                    )
            schedule._check_manual_basis()
        # stamped as the system after the checks (the CFO need not hold the
        # accountant's write rights); the stamp names the approver
        result = super(FixRevenueSchedule, self.sudo()).action_dofa_approve()
        for schedule in self:
            schedule._dofa_assert_approved("The manual revenue schedule")
            schedule.sudo()._guarded().write({"state": "active"})
            publish(
                self.env,
                "revenue.manual_release",
                "fix.revenue.schedule",
                schedule.id,
                {
                    "amount": schedule.total_amount,
                    "reason": schedule.manual_reason or "",
                    "approver": self.env.uid,
                },
            )
        return result

    def _approval_excluded(self):
        self.ensure_one()
        return (
            super()._approval_excluded() | self.create_uid | self.approval_amount_changed_by_id
        ).sudo()

    @api.depends("total_amount", "recognized_amount", "state")
    def _compute_deferred_balance(self):
        for schedule in self:
            schedule.deferred_balance = (
                0.0
                if schedule.state == "cancelled"
                else max(schedule.total_amount - schedule.recognized_amount, 0.0)
            )

    @api.constrains("start_date", "end_date", "total_amount")
    def _check_schedule(self):
        for schedule in self:
            if schedule.end_date <= schedule.start_date:
                raise UserError("The recognition term must be positive")
            if schedule.total_amount <= 0:
                raise UserError("The deferred amount must be positive")

    @api.model_create_multi
    def create(self, vals_list):
        manual = []
        for vals in vals_list:
            if not vals.get("source_model") or vals.get("source_model") == "manual":
                # A manually entered schedule (the workspace form) has no
                # source document; give it a unique trace key so the
                # required source pair stays satisfied and distinct. It is
                # born awaiting the CFO's approval (BRU-REV-01).
                vals["source_model"] = "manual"
                # a unique placeholder; the schedule's own id replaces it below
                vals["source_id"] = -(uuid.uuid4().int % 1000000000) - 1
                manual.append(vals)
                if vals.get("state", "draft") != "draft" and not self.env.su:
                    raise UserError(
                        "A manual revenue schedule starts awaiting CFO approval (BRU-REV-01)."
                    )
                vals["state"] = "draft"
            elif not self.env.su and not self._fix_guard_has_token():
                model = vals["source_model"]
                if model not in self.env or not (
                    self.env[model].sudo().browse(vals.get("source_id") or 0).exists()
                ):
                    raise UserError("A generated schedule names its existing source document.")
        if not self._fix_guard_open() and manual:
            records = super(FixRevenueSchedule, self._guarded()).create(vals_list)
        else:
            records = super().create(vals_list)
        for rec in records.filtered(lambda r: r.source_model == "manual"):
            # the trace key of a manual schedule is its own id (unique by construction)
            super(FixRevenueSchedule, rec.sudo()).write({"source_id": -rec.id})
        return records.with_env(self.env)

    @api.model
    def create_from_deferral(
        self,
        source_model: str,
        source_id: int,
        description: str,
        total: float,
        start: date,
        end: date,
        operating_unit_id: int | None = None,
    ) -> "FixRevenueSchedule":
        """Straight-line over the term: each period recognizes
        total * period_days / term_days. The monthly split runs from
        AUT-025's Airflow workflow; this is the schedule it draws down.

        The schedule lands in the SOURCE document's company and operating
        unit (both required here; every deferral source - subscription,
        contract, protection plan - carries them) unless a unit is given."""
        source = self.env[source_model].browse(source_id)
        return self.create(
            {
                "company_id": source.company_id.id,
                "operating_unit_id": operating_unit_id or source.operating_unit_id.id,
                "source_model": source_model,
                "source_id": source_id,
                "description": description,
                "total_amount": total,
                "start_date": start,
                "end_date": end,
            }
        )

    def action_recognize_period(self, as_of: date | None = None):
        """Recognize up to `as_of` (default today), straight-line, post it to
        the GL and publish. Idempotent per call — recognition is cumulative
        (recognized_amount only grows), so re-running a period recognizes
        nothing new.

        A08 M53: each delta is a fix.revenue.recognition.line with its GL
        move — Dr contract liability (deferred revenue) / Cr revenue — on the
        company's configured accounts (cd_billing_engine.account_code.
        deferred_revenue / .revenue). A missing account or journal REFUSES
        the whole run: revenue is never recognised without its posting."""
        as_of = as_of or date.today()
        require_role(self.env, GROUP_ACCOUNTANT, "Recognising revenue")
        for schedule in self:
            if schedule.state == "draft":
                raise UserError(
                    "Manual schedule %s is not approved: nothing is recognised before the "
                    "CFO's approval (BRU-REV-01)." % schedule.display_name
                )
            if schedule.state != "active" or as_of < schedule.start_date:
                continue
            effective_end = min(as_of, schedule.end_date)
            term_days = (schedule.end_date - schedule.start_date).days or 1
            elapsed = (effective_end - schedule.start_date).days
            target = round(schedule.total_amount * elapsed / term_days, 2)
            delta = round(target - schedule.recognized_amount, 2)
            if delta <= 0:
                continue
            move, deferred, revenue = schedule._post_recognition(delta, effective_end)
            self.env["fix.revenue.recognition.line"].sudo().create(
                {
                    "schedule_id": schedule.id,
                    "date": effective_end,
                    "amount": delta,
                    "move_id": move.id,
                }
            )
            schedule.invalidate_recordset(["recognized_amount", "line_ids"])
            if schedule.recognized_amount >= schedule.total_amount - 0.01:
                schedule._guarded().write({"state": "complete"})
            publish(
                self.env,
                "revenue.recognized",
                "fix.revenue.schedule",
                schedule.id,
                {
                    "amount": delta,
                    "cumulative": schedule.recognized_amount,
                    "source_model": schedule.source_model,
                    "source_id": schedule.source_id,
                    "gl_debit_account": deferred.code,
                    "gl_credit_account": revenue.code,
                },
            )

    def _post_recognition(self, amount, entry_date):
        """Dr contract liability / Cr revenue through M19's engine."""
        from odoo.addons.cd_billing_engine.models.fix_ar_engine import (
            _ar_account,
            _ar_journal,
            _post_ar_move,
        )

        self.ensure_one()
        company = self.company_id
        deferred = _ar_account(self.env, company, "deferred_revenue")
        revenue = _ar_account(self.env, company, "revenue")
        missing = [
            role for role, acc in (("deferred_revenue", deferred), ("revenue", revenue)) if not acc
        ]
        if missing:
            raise UserError(
                "Revenue recognition refused for %s: GL account role(s) %s not configured in "
                "company %s (system parameter cd_billing_engine.account_code.<role>)"
                % (self.description, ", ".join(missing), company.name)
            )
        if not _ar_journal(self.env, company):
            raise UserError(
                "Revenue recognition refused: company %s has no general journal" % company.name
            )
        dims = self.env["fix.ar.invoice"]._ar_posting_dims()
        move, note = _post_ar_move(
            self.env,
            company,
            entry_date,
            "REV-REC %s — %s" % (self.description, entry_date),
            [
                (deferred.id, "Contract liability released", amount, 0.0, False),
                (revenue.id, "Revenue recognised (IFRS 15)", 0.0, amount, False),
            ],
            {0: dims, 1: dims},
            source="ar",
        )
        if not move:
            raise UserError("Revenue recognition refused: %s" % (note or "posting failed"))
        return move, deferred, revenue

    @api.model
    def _cron_recognize(self):
        """Daily: recognise every active schedule up to today (M53-15)."""
        done = 0
        for schedule in self.sudo().search([("state", "=", "active")]):
            try:
                with self.env.cr.savepoint():
                    schedule.action_recognize_period()
                    done += 1
            except UserError as exc:
                schedule.message_post(body="Recognition run refused: %s" % exc)
        return done


class FixRevenueRecognitionLine(models.Model):
    """One recognition posting of a schedule (the as-of history the
    contract-balance and deferred-revenue reports read)."""

    _name = "fix.revenue.recognition.line"
    _description = "Revenue Recognition Posting"
    _order = "date desc, id desc"

    schedule_id = fields.Many2one(
        "fix.revenue.schedule", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(
        related="schedule_id.company_id", store=True, index=True, string="Company"
    )
    operating_unit_id = fields.Many2one(
        related="schedule_id.operating_unit_id", store=True, string="Operating Unit"
    )
    currency_id = fields.Many2one(related="schedule_id.currency_id")
    date = fields.Date(required=True, index=True)
    amount = fields.Monetary(currency_field="currency_id", required=True)
    move_id = fields.Many2one("account.move", string="GL Move", readonly=True)


class FixSubscriptionCharge(models.Model):
    """One billing cycle of a subscription / AMC contract and its invoice."""

    _name = "fix.subscription.charge"
    _description = "Subscription Cycle Charge"
    _order = "period_start desc, id desc"

    _cycle_unique = models.Constraint(
        "UNIQUE (subscription_id, period_start)", "One charge per subscription cycle"
    )

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    subscription_id = fields.Many2one(
        "fix.subscription", required=True, index=True, ondelete="restrict"
    )
    customer_id = fields.Many2one(related="subscription_id.customer_id", store=True)
    currency_id = fields.Many2one(related="subscription_id.currency_id")
    period_start = fields.Date(required=True)
    period_end = fields.Date(required=True)
    amount = fields.Monetary(string="Charge (VAT excl.)", currency_field="currency_id")
    invoice_id = fields.Many2one("fix.ar.invoice", string="Invoice", readonly=True, copy=False)
    invoice_state = fields.Selection(related="invoice_id.state", string="Invoice State")

    def _create_invoice(self):
        """The cycle's draft AR invoice: one line, VAT by M51's synchronous
        determination (standard 15% unless the tariff says otherwise)."""
        Invoice = self.env["fix.ar.invoice"]
        for charge in self:
            sub = charge.subscription_id
            determination = m51_determine(
                self.env,
                [
                    tax_logic.TaxLine(
                        product_code="SVC",
                        qty=Decimal("1"),
                        unit_price=Decimal(str(charge.amount)).quantize(TWO, ROUND_HALF_UP),
                    )
                ],
                on_date=charge.period_start,
                company=charge.company_id,
            )
            det = determination.lines[0]
            invoice = Invoice.create(
                {
                    "company_id": charge.company_id.id,
                    "customer_id": sub.customer_id.id,
                    "operating_unit_id": charge.operating_unit_id.id,
                    "source_model": "fix.subscription.charge",
                    "source_id": charge.id,
                    "invoice_date": charge.period_start,
                    "manual_reason": "Subscription cycle charge %s (%s to %s)"
                    % (sub.name, charge.period_start, charge.period_end),
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "description": "%s — %s to %s"
                                % (sub.name, charge.period_start, charge.period_end),
                                "taxable_amount": float(det.taxable_amount),
                                "vat_amount": float(det.vat_amount),
                                "line_total": float(det.line_total),
                            },
                        )
                    ],
                }
            )
            charge.sudo().write({"invoice_id": invoice.id})


OBLIGATION_TYPES = [
    ("amc_service", "AMC Service (stand-ready)"),
    ("workmanship_warranty", "Workmanship Warranty (service-type)"),
    ("parts", "Parts Included"),
    ("other", "Other Distinct Service"),
]


class FixPerformanceObligation(models.Model):
    """IFRS 15 performance obligation of a subscription / AMC contract:
    its standalone selling price, the allocated share of the transaction
    price and the revenue schedule that recognises it."""

    _name = "fix.performance.obligation"
    _description = "Performance Obligation (IFRS 15)"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "subscription_id, id"

    def _fix_guarded_fields(self) -> set:
        # A08 M53-6: the allocation is the price split's output, never typed
        return super()._fix_guarded_fields() | {"allocated_amount", "state", "schedule_id"}

    subscription_id = fields.Many2one(
        "fix.subscription", string="Contract", required=True, index=True, ondelete="cascade"
    )
    company_id = fields.Many2one(
        related="subscription_id.company_id", store=True, index=True, string="Company"
    )
    operating_unit_id = fields.Many2one(
        related="subscription_id.operating_unit_id", store=True, string="Operating Unit"
    )
    customer_id = fields.Many2one(related="subscription_id.customer_id", store=True)
    currency_id = fields.Many2one(related="subscription_id.currency_id")
    name = fields.Char(required=True)
    obligation_type = fields.Selection(
        OBLIGATION_TYPES, required=True, default="amc_service", tracking=True
    )
    satisfaction = fields.Selection(
        [("over_time", "Over Time (ratable)"), ("point_in_time", "Point in Time")],
        required=True,
        default="over_time",
        tracking=True,
    )
    standalone_price = fields.Monetary(
        string="Standalone Selling Price", currency_field="currency_id", required=True
    )
    allocated_amount = fields.Monetary(
        string="Allocated Price", currency_field="currency_id", readonly=True, copy=False
    )
    start_date = fields.Date(string="Satisfaction Start")
    end_date = fields.Date(string="Satisfaction End / Date")
    schedule_id = fields.Many2one(
        "fix.revenue.schedule", string="Revenue Schedule", readonly=True, copy=False
    )
    recognized_amount = fields.Monetary(
        related="schedule_id.recognized_amount", string="Recognised"
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("allocated", "Price Allocated"),
            ("scheduled", "Scheduled"),
            ("satisfied", "Satisfied"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )

    @api.constrains("standalone_price", "start_date", "end_date", "satisfaction")
    def _check_obligation(self):
        for obligation in self:
            if obligation.standalone_price < 0:
                raise UserError("A standalone selling price cannot be negative")
            if (
                obligation.satisfaction == "over_time"
                and obligation.start_date
                and obligation.end_date
                and obligation.end_date <= obligation.start_date
            ):
                raise UserError("The satisfaction period must be positive")

    @api.onchange("obligation_type")
    def _onchange_obligation_type(self):
        if self.obligation_type == "parts":
            self.satisfaction = "point_in_time"

    def action_create_schedule(self):
        """Hand the allocated price to a revenue schedule: ratable over the
        satisfaction period for over-time obligations; for a point-in-time
        obligation a one-day schedule ending on the satisfaction date (it is
        recognised in full when that date is reached)."""
        Schedule = self.env["fix.revenue.schedule"]
        for obligation in self:
            if obligation.state != "allocated":
                raise UserError("Allocate the transaction price before scheduling")
            if obligation.allocated_amount <= 0:
                raise UserError("Obligation %s has no allocated price" % obligation.name)
            sub = obligation.subscription_id
            allocated = sum(
                sub.obligation_ids.filtered(lambda o: o.state != "cancelled").mapped(
                    "allocated_amount"
                )
            )
            if allocated > sub._transaction_price() + 0.01:
                raise UserError(
                    "Obligations of %s are allocated %.2f, above the transaction price %.2f."
                    % (sub.name, allocated, sub._transaction_price())
                )
            if obligation.satisfaction == "over_time":
                start = obligation.start_date or sub.start_date
                end = obligation.end_date or sub.contract_end_date
                if not end:
                    raise UserError(
                        "Set the satisfaction end (or the contract end) of %s" % obligation.name
                    )
            else:
                end = obligation.end_date
                if not end:
                    raise UserError(
                        "Set the satisfaction date of the point-in-time obligation %s"
                        % obligation.name
                    )
                start = end - timedelta(days=1)
            schedule = Schedule.sudo().create(
                {
                    "company_id": obligation.company_id.id,
                    "operating_unit_id": obligation.operating_unit_id.id,
                    "source_model": "fix.performance.obligation",
                    "source_id": obligation.id,
                    "description": "%s — %s" % (sub.name, obligation.name),
                    "total_amount": obligation.allocated_amount,
                    "start_date": start,
                    "end_date": end,
                }
            )
            obligation._guarded().write({"schedule_id": schedule.id, "state": "scheduled"})

    def action_recognize(self):
        """Recognise the obligation's schedule up to today."""
        for obligation in self:
            if not obligation.schedule_id:
                raise UserError("Obligation %s has no revenue schedule yet" % obligation.name)
            obligation.schedule_id.action_recognize_period()
            if obligation.schedule_id.state == "complete":
                obligation._guarded().write({"state": "satisfied"})
