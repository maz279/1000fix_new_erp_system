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
# M39-F15: a past-due subscription is still under contract and keeps billing;
# a held (suspended), paused or closed one does not.
BILLABLE_STATES = ("active", "past_due")
# rev_rec_engine's refund line: above it the refund needs a manager
REFUND_MANAGER_THRESHOLD = 25000.0
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
    "pending_contract_value",
    "contract_value_requested_by_id",
    "contract_value_reason",
}
# A04 ERP M39-F9 (20 Nov 2026): the billing terms. Set when the subscription
# is created; afterwards only the billing run, an approved lifecycle request
# (renewal, resume) or the billing schedule moves them (guarded writes). The
# only Accountant moved next_invoice_date a year ahead and grace to 999 days.
SUB_TERM_FIELDS = ("next_invoice_date", "grace_period_days", "contract_end_date")
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
    # ---- the IFRS 15 transaction price of an existing contract (M53-13): it is a
    # price term, so it is requested by one person and approved by another
    pending_contract_value = fields.Monetary(
        string="Requested Transaction Price",
        currency_field="currency_id",
        readonly=True,
        copy=False,
    )
    contract_value_requested_by_id = fields.Many2one(
        "res.users", string="Transaction Price Requested By", readonly=True, copy=False
    )
    contract_value_reason = fields.Char(string="Why This Price", readonly=True, copy=False)
    # the accepted M41 quotation a subscription was created from (A04 hand-off)
    source_quote_id = fields.Integer(
        string="Source Quotation ID", readonly=True, copy=False, index=True
    )
    source_quote_ref = fields.Char(string="Source Quotation", readonly=True, copy=False)

    _source_quote_unique = models.Constraint(
        "UNIQUE (source_quote_id)", "One subscription per accepted quotation"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | SUB_GUARDED | SUB_PRICE_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        # set on the form when the subscription is created; an empty recordset
        # is the new-record form (locked there, nothing could be created)
        return locked | set(SUB_PRICE_FIELDS) | set(SUB_TERM_FIELDS) if self else locked

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
            terms = sorted(
                {
                    f
                    for f in set(SUB_TERM_FIELDS) & set(vals)
                    for sub in self
                    if sub._fix_guard_differs(f, vals[f], sub[f])
                }
            )
            if terms:
                raise UserError(
                    "The billing terms of a subscription (%s) are set when it is created; "
                    "afterwards a reviewed billing run, an approved renewal / resume or an "
                    "activated billing schedule moves them (BRU-SUB-17)." % ", ".join(terms)
                )
        return super().write(vals)

    def action_request_contract_value(self, contract_value=None, reason=""):
        """Set or correct the transaction price of an existing contract: the
        form locks it once created, so Allocate Price had nothing to allocate
        on the contracts already live. A second person approves it."""
        require_role(self.env, GROUP_ACCOUNTANT, "Requesting a transaction price")
        try:
            value = float(contract_value or 0.0)
        except (TypeError, ValueError):
            raise UserError("The transaction price is a number.") from None
        if value <= 0:
            raise UserError("The transaction price is a positive amount.")
        if not (reason or "").strip():
            raise UserError("State where this transaction price comes from (the contract).")
        for sub in self:
            if sub.state in ("cancelled", "churned"):
                raise UserError("Subscription %s is %s." % (sub.name, sub.state))
            if sub.obligation_ids.filtered(lambda o: o.state in ("scheduled", "satisfied")):
                raise UserError(
                    "Obligations of %s are already scheduled: a price change is a contract "
                    "modification; cancel and re-create the affected obligations." % sub.name
                )
            sub._guarded().write(
                {
                    "pending_contract_value": value,
                    "contract_value_requested_by_id": self.env.uid,
                    "contract_value_reason": reason.strip()[:250],
                }
            )
            sub.message_post(
                body="Transaction price %.2f requested by %s: %s"
                % (value, self.env.user.name, reason.strip()[:250])
            )
        return True

    def action_approve_contract_value(self):
        """The second person: an Accountant up to the price-change band, the
        Accounting Administrator above it; never the requester or the creator."""
        from odoo.addons.cd_billing_engine.models.fix_finance_approval import (
            GROUP_ADMINISTRATOR,
            float_param,
        )

        for sub in self:
            if not sub.contract_value_requested_by_id:
                raise UserError("Subscription %s has no transaction price to approve." % sub.name)
            if not self.env.su:
                band = float_param(self.env, PARAM_PRICE_DIRECT, DEFAULT_PRICE_DIRECT)
                delta = abs((sub.pending_contract_value or 0.0) - (sub.contract_value or 0.0))
                require_role(
                    self.env,
                    GROUP_ACCOUNTANT if delta <= band else GROUP_ADMINISTRATOR,
                    "Approving this transaction price",
                )
                if self.env.user in (sub.contract_value_requested_by_id | sub.create_uid):
                    raise UserError(
                        "Segregation of duties: you requested or raised this subscription; "
                        "another person approves its transaction price."
                    )
            value = sub.pending_contract_value
            sub.sudo()._guarded().write(
                {
                    "contract_value": value,
                    "pending_contract_value": 0.0,
                    "contract_value_requested_by_id": False,
                    "contract_value_reason": False,
                }
            )
            sub.message_post(
                body="Transaction price %.2f approved by %s." % (value, self.env.user.name)
            )
        return True

    def _price_delta_annual(self, new_amount) -> float:
        self.ensure_one()
        cycles_a_year = {"monthly": 12, "quarterly": 4, "annual": 1}[self.billing_cycle]
        return abs((new_amount or 0.0) - (self.recurring_amount or 0.0)) * cycles_a_year

    def action_request_price_change(
        self, new_amount, plan=None, reason="", effective_date=None, customer_request_ref=None
    ):
        """A mid-term price (or plan) change: never applied by its requester.
        With A04's proration service the change is a draft proration routed
        through its DOFA approval (it applies the price); otherwise a second
        person approves it here (action_approve_price_change).

        A04 ERP round 2 M39-F16: an increase applies only after the customer's
        notice period (Send Price Notice on the plan change), unless the
        customer asked for it (customer_request_ref, the evidence)."""
        require_role(self.env, GROUP_ACCOUNTANT, "Requesting a subscription price change")
        if not (reason or "").strip():
            raise UserError("State why the price changes.")
        if new_amount is None or new_amount < 0:
            raise UserError("A recurring amount is zero or more.")
        Proration = self.env.get("fix.subscription.proration")
        out = []
        for sub in self:
            if sub.state in ("cancelled", "churned"):
                raise UserError("Subscription %s is %s." % (sub.name, sub.state))
            if Proration is not None and hasattr(Proration, "create_for_plan_change"):
                extra = {}
                if (customer_request_ref or "").strip():
                    extra = {
                        "notice_exemption": "customer_request",
                        "notice_exemption_ref": customer_request_ref.strip()[:250],
                    }
                proration = Proration.create_for_plan_change(
                    sub,
                    new_amount,
                    to_plan=plan,
                    effective_date=fields.Date.to_date(effective_date)
                    if effective_date
                    else fields.Date.context_today(sub),
                    **extra,
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
        # A04 ERP (B2): only the quotation's own event; the M01 estimate now
        # publishes estimate.quotation_accepted on another model
        if event.get("aggregate") != "fix.quotation":
            return {"skipped": "aggregate %s is not fix.quotation" % event.get("aggregate")}
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
        ou = ou or self.env["operating.unit"].sudo().search(
            [("company_id", "=", company.id)], limit=1
        )
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
        sub = (
            self.sudo()
            ._guarded()
            .create(
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
        Invoices (one bill, not N).

        A04 ERP M39-F5: a cycle is a calendar month / quarter / year from the
        cycle start (a fixed 30-day roll billed 13 charges in a 12-month
        term), and billing stops at the contract end: a last partial cycle is
        billed for its days, nothing is billed past the end.
        M39-F15: a past-due subscription is still under contract and is
        billed; only a held (suspended) one is not."""
        Charge = self.env["fix.subscription.charge"]
        for sub in self:
            if sub.state not in BILLABLE_STATES:
                continue
            if sub.recurring_amount <= 0:
                raise UserError("Subscription %s has no recurring amount to charge" % sub.name)
            period_start = sub.next_invoice_date
            period_end, amount = sub._fix_cycle_window(period_start)
            if not period_end:
                sub.message_post(
                    body="Not billed: the contract ended on %s; the cycle from %s is outside the "
                    "term (renew it to bill on)." % (sub.contract_end_date, period_start)
                )
                continue
            charge = Charge._guarded().create(
                {
                    "company_id": sub.company_id.id,
                    "operating_unit_id": sub.operating_unit_id.id,
                    "subscription_id": sub.id,
                    "period_start": period_start,
                    "period_end": period_end,
                    "amount": amount,
                }
            )
            charge = Charge.browse(charge.ids)
            charge._create_invoice()
            publish(
                self.env,
                "subscription.charged",
                "fix.subscription",
                sub.id,
                {
                    "customer_id": sub.customer_id.id,
                    "amount": charge.amount,
                    "period_days": (period_end - period_start).days + 1,
                },
            )
            sub._guarded().write({"next_invoice_date": period_end + timedelta(days=1)})

    def _fix_cycle_window(self, period_start):
        """(period_end, amount) of the cycle starting `period_start`: a full
        calendar cycle at the recurring amount, clipped to the contract end
        (the partial cycle billed for its days); (False, 0.0) when the cycle
        starts after the contract end."""
        self.ensure_one()
        # A cycle runs a calendar month / quarter / year from the billing date.
        # When the billing date falls on the start's anniversary, the cycle is
        # counted from the start, so a month-end start does not drift
        # (Jan 31 -> Feb 27, Feb 28 -> Mar 30).
        months = self._cycle_months()
        anchor = period_start
        if self.start_date and self.start_date <= period_start:
            k = 0
            while self.start_date + relativedelta(months=k * months) < period_start:
                k += 1
            if self.start_date + relativedelta(months=k * months) == period_start:
                anchor = self.start_date
        n = 1
        while anchor + relativedelta(months=n * months) <= period_start:
            n += 1
        cycle_start = anchor + relativedelta(months=(n - 1) * months)
        full_end = anchor + relativedelta(months=n * months) - timedelta(days=1)
        end = full_end
        if self.contract_end_date:
            if period_start > self.contract_end_date:
                return False, 0.0
            end = min(full_end, self.contract_end_date)
        amount = self.recurring_amount
        days = (end - period_start).days + 1
        full = (full_end - cycle_start).days + 1
        if days < full:  # a partial cycle (contract end, or resumed mid-cycle)
            amount = round(self.recurring_amount * days / full, 2)
        return end, amount

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
            sub._fix_refuse_second_basis()
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
                ob = (
                    Obligation._guarded()
                    .create(
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
                    )
                    .with_env(self.env)
                )
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

    def _fix_refuse_second_basis(self):
        """A04 ERP M39-F1: a subscription whose issued invoices already defer
        their own periods is not scheduled a second time over its whole
        contract value (November recognised 5,868.13 on 3,000 billed)."""
        for sub in self:
            if sub._fix_recognition_basis() == "invoice":
                raise UserError(
                    "%s already recognises revenue invoice by invoice (each issued cycle "
                    "invoice defers its own period). A contract-level schedule would recognise "
                    "the same revenue twice: one basis per subscription (M39-F1)." % sub.name
                )

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
        as_of = as_of or fields.Date.context_today(self)
        Charge = self.env["fix.subscription.charge"]
        overdue_basis = getattr(Charge, "_fix_overdue_unpaid", None)
        for sub in self:
            if sub.state in ("cancelled", "churned"):
                continue
            if overdue_basis is not None:
                # A04 M39-2: dunning keys off cycle invoices past due and
                # unpaid; the calendar is only the fallback when no invoice
                # basis exists. A subscription with nothing issued-and-overdue
                # is never dunned (a missed billing run is a Finance
                # omission, not customer non-payment).
                charges = overdue_basis(subscription=sub, as_of=as_of)
                dues = [c.invoice_due_date for c in charges if c.invoice_due_date]
                if not dues:
                    # paid up: leave Past Due, or billing stays stopped for ever
                    # (a held subscription is reinstated by a person)
                    if sub.state == "past_due":
                        sub._guarded().write(
                            {"state": "active", "dunning_step": "none", "days_overdue": 0}
                        )
                        sub.message_post(body="Nothing overdue any more: back to Active.")
                        publish(
                            self.env,
                            "subscription.reinstated",
                            "fix.subscription",
                            sub.id,
                            {"customer_id": sub.customer_id.id},
                        )
                    continue
                overdue = (as_of - min(dues)).days
            elif sub.next_invoice_date and as_of > sub.next_invoice_date:
                overdue = (as_of - sub.next_invoice_date).days
            else:
                continue
            sub._guarded().write({"days_overdue": overdue})
            grace = sub.grace_period_days or 15
            # A grace period shorter than the reminder band collapses the
            # band rather than delaying escalation past what was agreed.
            reminder_until = min(7, grace)
            if overdue < 3:
                continue
            step = (
                "reminder"
                if overdue <= reminder_until
                else "final"
                if overdue <= grace
                else "escalate"
            )
            if sub.dunning_step == step:
                # the daily job: the customer hears once per step, not once per day
                continue
            if overdue <= reminder_until:
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

    @api.model
    def _cron_run_dunning(self):
        """Daily (M53-15): the ladder over every live subscription. It reads
        issued cycle invoices past due and unpaid, and posts nothing."""
        subs = self.sudo().search([("state", "not in", ("cancelled", "churned"))])
        for sub in subs:
            try:
                with self.env.cr.savepoint():
                    sub.action_trigger_dunning()
            except UserError as exc:
                sub.message_post(body="Dunning run refused: %s" % exc)
        return len(subs)

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
                    % (
                        sub.name,
                        sum(unpaid.mapped("amount_residual")),
                        ", ".join(unpaid.mapped("name")),
                    )
                )
            # A04 ERP M39-F15 (BRU-SUB-12): the suspended months are not billed
            # on reinstatement; billing resumes from today
            today = fields.Date.context_today(sub)
            vals = {"state": "active", "dunning_step": "none", "days_overdue": 0}
            if sub.next_invoice_date and sub.next_invoice_date < today:
                vals["next_invoice_date"] = today
                sub.message_post(
                    body="Reinstated: the suspension from %s to %s is not billed."
                    % (sub.next_invoice_date, today)
                )
                if "schedule_ids" in sub._fields:
                    sub.schedule_ids.filtered(lambda s: s.state == "active").period_ids.filtered(
                        lambda p, day=today: p.state == "planned" and p.period_end < day
                    ).sudo().write({"state": "skipped"})
            sub._guarded().write(vals)
            publish(
                self.env,
                "subscription.reinstated",
                "fix.subscription",
                sub.id,
                {
                    "customer_id": sub.customer_id.id,
                },
            )

    def action_cancel(self, cancellation_date=None):
        """Cancel and settle (A04 ERP M39-F2): billing stops, every revenue
        schedule of the contract stops on the day, the unearned share of what
        was billed is credited, and what was delivered but not billed is billed
        (the final bill). Outstanding balances ride the M20 collections ladder."""
        require_role(self.env, GROUP_ACCOUNTANT, "Cancelling a subscription")
        on = fields.Date.to_date(cancellation_date) if cancellation_date else None
        for sub in self:
            if sub.state in ("cancelled", "churned"):
                raise UserError("Subscription %s is already %s" % (sub.name, sub.state))
            day = on or fields.Date.context_today(sub)
            sub._guarded().write({"state": "cancelled", "cancelled_on": day})
            res = sub._fix_settle_cancellation(day)
            sub._guarded().write(
                {
                    "last_refund_amount": float(res.net_refund_payable),
                    "last_refund_earned": float(res.earned_revenue),
                }
            )
            # T03: subscription dunning stops on cancellation — outstanding
            # balances ride the M20 collections ladder instead
            publish(self.env, "subscription.cancelled", "fix.subscription", sub.id, {})

    def action_request_refund(self, cancellation_date=None, fee_pct=0.0):
        """Prorated mid-cycle cancellation and credit note flow.
        Calculates earned vs unearned revenue and enforces BDT 25,000 approval threshold.

        A08 M53: the figures are kept on the subscription; each issued cycle
        invoice running past the cancellation gets a DRAFT credit note for its
        unearned share (gross of VAT pro rata) that runs M20's approval
        ladder; every revenue schedule recognises up to the cancellation date
        and stops.

        A04 ERP M39-F3 / F14: the unearned share is measured on the cycle the
        invoice actually billed (its own period and amount), not on
        next_invoice_date - 30 days, and the invoice-level deferral schedule
        stops too (it kept recognising the refunded share: 3,000 recognised
        for 1,000 earned and 200401 left 2,000 in debit)."""
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
        try:
            fee = float(fee_pct or 0.0)
        except (TypeError, ValueError):
            raise UserError("The cancellation fee is a percentage.") from None
        if not 0.0 <= fee <= 100.0:
            raise UserError("The cancellation fee is between 0 and 100%.")
        results = []
        for sub in self:
            if sub.state in ("cancelled", "churned"):
                raise UserError("Subscription %s is already %s" % (sub.name, sub.state))
            sub._guarded().write({"state": "cancelled", "cancelled_on": cancellation_date})
            res = sub._fix_settle_cancellation(cancellation_date, fee_pct=fee)
            sub._guarded().write(
                {
                    "last_refund_amount": float(res.net_refund_payable),
                    "last_refund_earned": float(res.earned_revenue),
                }
            )
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

    # ---- A04 ERP M39-F1/F2/F3/F14: one basis, and settling a cancellation ----
    def _fix_recognition_basis(self) -> str:
        """M39-F1: the ONE basis revenue is recognised on. 'contract': its
        performance obligations are scheduled (the whole transaction price
        over the term); 'invoice': each issued cycle invoice defers its own
        period; 'none' before either exists."""
        self.ensure_one()
        if self.obligation_ids.filtered(lambda o: o.state in ("scheduled", "satisfied")):
            return "contract"
        if (
            self.env["fix.revenue.schedule"]
            .sudo()
            .search_count(
                [
                    ("subscription_id", "=", self.id),
                    ("source_model", "=", "fix.ar.invoice"),
                    ("state", "!=", "cancelled"),
                ]
            )
        ):
            return "invoice"
        return "none"

    def _fix_billed_charges(self):
        """Cycle charges whose invoice is on the books (issued or later)."""
        self.ensure_one()
        return self.charge_ids.sudo().filtered(
            lambda c: c.invoice_id and c.invoice_id.state in ("issued", "paid", "credited")
        )

    def _fix_settle_cancellation(self, cancel_date, fee_pct=0.0):
        """Settle a cancellation dated `cancel_date`; returns the totals as a
        rev_rec_engine.CancellationRefundResult (VAT-exclusive)."""
        self.ensure_one()
        Schedule = self.env["fix.revenue.schedule"].sudo()
        earned_total = unearned_total = fee_total = net_total = billed_total = 0.0
        first_note = self.env["fix.credit.note"]
        contract_basis = self._fix_recognition_basis() == "contract"
        refunded_ex_vat = 0.0
        charges = self._fix_billed_charges().filtered(lambda c: c.period_end >= cancel_date)
        for charge in charges.sorted("period_start"):
            invoice = charge.invoice_id.sudo()
            deferred = invoice._fix_deferred_amount()
            if deferred <= 0.005:
                continue
            schedule = Schedule.search(
                [("source_model", "=", invoice._name), ("source_id", "=", invoice.id)], limit=1
            )
            if schedule and schedule.state == "active" and not contract_basis:
                if cancel_date > schedule.start_date and not schedule._recognition_refusal():
                    schedule.action_recognize_period(as_of=min(cancel_date, schedule.end_date))
                schedule.invalidate_recordset(["recognized_amount"])
                earned = round(min(schedule.recognized_amount, deferred), 2)
            else:
                term = max((charge.period_end - charge.period_start).days, 1)
                elapsed = min(max((cancel_date - charge.period_start).days, 0), term)
                earned = round(deferred * elapsed / term, 2)
            unearned = round(deferred - earned, 2)
            fee = round(unearned * (fee_pct or 0.0) / 100.0, 2)
            net = round(unearned - fee, 2)
            note = self._fix_refund_note(invoice, net, deferred)
            keep = 0.0
            if note:
                taxable_part, _vat = note._vat_split()
                keep = round(taxable_part, 2)
                first_note = first_note or note
            refunded_ex_vat += keep
            if schedule and not contract_basis:
                schedule._fix_stop_at(cancel_date, keep_deferred=keep)
            billed_total += deferred
            earned_total += earned
            unearned_total += unearned
            fee_total += fee
            net_total += net
        if first_note:
            self._guarded().write({"refund_credit_note_id": first_note.id})
        # every other schedule of the contract stops on the day
        self._stop_recognition(cancel_date)
        final = self._fix_final_charge(cancel_date)
        if contract_basis:
            self._fix_settle_contract_liability(cancel_date, refunded_ex_vat)
        if final:
            self.message_post(
                body="Final bill %s for %s to %s (delivered, not yet billed)."
                % (final.invoice_id.display_name, final.period_start, final.period_end)
            )
        return rev_rec_engine.CancellationRefundResult(
            cancellation_date=cancel_date,
            total_amount=Decimal(str(round(billed_total, 2))).quantize(TWO),
            earned_revenue=Decimal(str(round(earned_total, 2))).quantize(TWO),
            unearned_refund=Decimal(str(round(unearned_total, 2))).quantize(TWO),
            cancellation_fee=Decimal(str(round(fee_total, 2))).quantize(TWO),
            net_refund_payable=Decimal(str(round(net_total, 2))).quantize(TWO),
            requires_manager_approval=net_total > REFUND_MANAGER_THRESHOLD,
        )

    def _fix_refund_note(self, invoice, net_ex_vat, deferred):
        """A DRAFT credit note for `net_ex_vat` of `invoice` (grossed up by
        the invoice's own VAT ratio), on M20's credit-note ladder."""
        self.ensure_one()
        if net_ex_vat <= 0.005 or deferred <= 0.005:
            return self.env["fix.credit.note"]
        open_credit = invoice.total_payable - invoice.credited_amount
        amount = invoice.currency_id.round(
            min(invoice.total_payable * net_ex_vat / deferred, open_credit)
        )
        if amount <= 0:
            return self.env["fix.credit.note"]
        note = self.env["fix.credit.note"].create(
            {
                "company_id": invoice.company_id.id,
                "operating_unit_id": invoice.operating_unit_id.id,
                "invoice_id": invoice.id,
                "amount": amount,
                "reason_code": "subscription_refund",
            }
        )
        note.message_post(
            body="Refund of the unearned share of %s on cancellation: a draft credit note "
            "for finance to submit; it is approved by someone other than the requester "
            "(M20 credit-note ladder)." % self.name
        )
        return note

    def _fix_final_charge(self, cancel_date):
        """The final bill: service delivered up to the cancellation but not
        billed (billed in arrears, or the run had not reached it)."""
        self.ensure_one()
        billed = self.charge_ids.sudo()
        if not billed:
            # never billed through M39 (or billed elsewhere, e.g. the M08
            # contract walker): no final bill is guessed
            return self.env["fix.subscription.charge"]
        last_end = max(billed.mapped("period_end"))
        if cancel_date <= last_end + timedelta(days=1) or (self.recurring_amount or 0.0) <= 0:
            return self.env["fix.subscription.charge"]
        start = last_end + timedelta(days=1)
        end = cancel_date - timedelta(days=1)
        if self.contract_end_date:
            end = min(end, self.contract_end_date)
        if end < start:
            return self.env["fix.subscription.charge"]
        full_end = start + relativedelta(months=self._cycle_months()) - timedelta(days=1)
        days = (end - start).days + 1
        full = (full_end - start).days + 1
        amount = round(self.recurring_amount * days / full, 2)
        if amount <= 0.005:
            return self.env["fix.subscription.charge"]
        Charge = self.env["fix.subscription.charge"].sudo()
        charge = Charge._guarded().create(
            {
                "company_id": self.company_id.id,
                "operating_unit_id": self.operating_unit_id.id,
                "subscription_id": self.id,
                "period_start": start,
                "period_end": end,
                "amount": amount,
            }
        )
        charge = Charge.browse(charge.ids)
        charge._create_invoice()
        return charge

    def _fix_settle_contract_liability(self, cancel_date, refunded_ex_vat):
        """Contract basis: what was billed to the liability, less what the
        obligations recognised and the refunds, nets to zero. A remainder was
        earned (the customer forfeited it): it is recognised now. A shortfall
        is service recognised but never billed: it is billed (final bill)."""
        self.ensure_one()
        billed = sum(c.invoice_id.sudo()._fix_deferred_amount() for c in self._fix_billed_charges())
        schedules = self.obligation_ids.mapped("schedule_id").sudo()
        recognised = sum(schedules.mapped("recognized_amount"))
        balance = round(billed - recognised - refunded_ex_vat, 2)
        if balance > 0.005 and schedules:
            target = schedules.sorted("id")[-1:]
            target._fix_post_line(balance, cancel_date, "earned on cancellation (not refunded)")
        elif balance < -0.005:
            Charge = self.env["fix.subscription.charge"].sudo()
            ends = self.charge_ids.mapped("period_end")
            last = max(ends) if ends else cancel_date - timedelta(days=1)
            start = max(last + timedelta(days=1), cancel_date)
            charge = Charge._guarded().create(
                {
                    "company_id": self.company_id.id,
                    "operating_unit_id": self.operating_unit_id.id,
                    "subscription_id": self.id,
                    "period_start": start,
                    "period_end": start,
                    "amount": -balance,
                }
            )
            charge = Charge.browse(charge.ids)
            charge._create_invoice()
            self.message_post(
                body="Final bill of %.2f: service recognised under the contract but never billed."
                % -balance
            )

    def _stop_recognition(self, cancellation_date):
        """Recognise every obligation up to the cancellation, then stop it,
        and stop any other active schedule of the subscription."""
        self.ensure_one()
        for obligation in self.obligation_ids.filtered(lambda o: o.state != "cancelled"):
            schedule = obligation.schedule_id
            if schedule and schedule.state == "active":
                if not schedule._recognition_refusal() and cancellation_date > schedule.start_date:
                    schedule.action_recognize_period(as_of=cancellation_date)
                if schedule.state == "active":
                    schedule._guarded().write(
                        {"state": "cancelled", "cancelled_date": cancellation_date}
                    )
            obligation._guarded().write(
                {"state": "cancelled" if obligation.state != "satisfied" else "satisfied"}
            )
        others = (
            self.env["fix.revenue.schedule"]
            .sudo()
            .search([("subscription_id", "=", self.id), ("state", "in", ("active", "held"))])
        )
        for schedule in others:
            schedule._fix_stop_at(cancellation_date)

    def action_allocate_price(self):
        """IFRS 15 step 4: allocate the transaction price to the performance
        obligations by relative standalone selling price, at 2dp half-up; the
        rounding residue lands on the largest obligation so the allocation
        sums EXACTLY to the price. A contract whose obligations are already
        scheduled is a contract MODIFICATION and is refused here."""
        for sub in self:
            if sub.contract_value <= 0 and not sub.contract_end_date:
                raise UserError(
                    "Enter the transaction price of %s first (Request Transaction Price), or its "
                    "contract end so the price is what the term bills." % sub.name
                )
            sub._allocate_price(sub._transaction_price())

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
                obligation._guarded().write(
                    {"allocated_amount": float(share), "state": "allocated"}
                )

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

        # A04 ERP M39-F19: a Mushak 6.3 number is M51's, assigned when the
        # invoice is issued through M20; this preview never invents one (it
        # published year-customer-count as if it were the statutory number).
        mushak_no = False

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
    hold_reason = fields.Char(
        string="Why Held",
        readonly=True,
        copy=False,
        help="Why this schedule recognises nothing: it has no contract behind it, its amount "
        "is above the contract's value, or a manual schedule has no CFO approval (M53-6). "
        "A person cancels it or sends it to the CFO as a manual schedule.",
    )
    state = fields.Selection(
        [
            ("draft", "Awaiting CFO Approval (manual)"),
            ("active", "Active"),
            ("held", "Held: no contract or CFO approval"),
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

    SCHEDULE_GUARDED = {"state", "cancelled_date", "recognized_amount", "hold_reason"}
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
            if {"source_model", "source_id"} & set(vals):
                raise UserError("A schedule's source is set by the system, never edited.")
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
            if (
                not (schedule.manual_reason or "").strip()
                or not (schedule.evidence_ref or "").strip()
            ):
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
                # a held schedule has no contract behind it: nothing is deferred
                if schedule.state in ("cancelled", "held")
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
                # BRU-REV-01 / M53-6: naming any existing source at any total
                # used to give a schedule born active, past the CFO. A schedule
                # with a source is GENERATED from the contract's obligations;
                # anything typed is a manual schedule.
                raise UserError(
                    "A revenue schedule is generated from its contract (Generate Revenue "
                    "Schedule on the subscription), or raised without a source as a manual "
                    "schedule for the CFO's approval (BRU-REV-01): it is never typed against "
                    "a source document."
                )
        if not self._fix_guard_open() and manual:
            records = super(FixRevenueSchedule, self._guarded()).create(vals_list)
        else:
            records = super().create(vals_list)
        for rec in records.filtered(lambda r: r.source_model == "manual"):
            # the trace key of a manual schedule is its own id (unique by construction)
            super(FixRevenueSchedule, rec.sudo()).write({"source_id": -rec.id})
        # whatever created it, a schedule with nothing behind it never starts active
        records.filtered(lambda r: r.state == "active")._hold_unbased()
        return records.with_env(self.env)

    # ---- M53-6: what may post at all ------------------------------------------
    def _source_record(self):
        """The source document a generated schedule names, if it exists."""
        self.ensure_one()
        if self.source_model not in self.env or self.source_id <= 0:
            return None
        return self.env[self.source_model].sudo().browse(self.source_id).exists() or None

    @staticmethod
    def _fix_contract_ceiling(contract) -> float:
        days = max((contract.date_end - contract.date_start).days, 1)
        return round(contract.annual_value * math.ceil(days / 365.0), 2)

    def _recognition_refusal(self):
        """Why this schedule may not post revenue; None when it may.

        Revenue is recognised against a contract: the obligation it was
        generated from, a subscription with a real term or value, or a
        fix.contract; a manual schedule also needs the CFO's approval
        (BRU-REV-01). The total never exceeds that contract's value. A schedule
        with none of these (the two legacy schedules of BDT 1,200,000 on
        subscriptions billing 2,500 and 1,999) posts nothing, whoever runs it."""
        self.ensure_one()
        if self._is_manual():
            if not self.contract_id and not self.subscription_id:
                return "a manual schedule with no contract"
            if not self.dofa_approved:
                return "a manual schedule with no CFO approval"
            return None
        source = self._source_record()
        if self.source_model == "fix.ar.invoice":
            # A04 ERP M39-F6: a deferred invoice is its own basis - it billed
            # this period - so a subscription with no contract value or end
            # date still recognises what it billed (it was held for ever).
            # M39-F1: never beside the contract's obligation schedules.
            if not source:
                return "its invoice no longer exists"
            if source.state not in ("issued", "paid", "credited", "written_off"):
                return "invoice %s is %s, not issued" % (source.display_name, source.state)
            sub = self.subscription_id.sudo()
            if sub and sub._fix_recognition_basis() == "contract":
                return (
                    "%s recognises its revenue through its contract's performance obligations "
                    "(one basis per subscription)" % sub.display_name
                )
            ceiling = (
                source._fix_deferred_amount() if hasattr(source, "_fix_deferred_amount") else 0.0
            )
            if self.total_amount > ceiling + 0.005:
                return "total %.2f is above the %.2f invoice %s deferred" % (
                    self.total_amount,
                    ceiling,
                    source.display_name,
                )
            return None
        if self.source_model == "fix.performance.obligation":
            if not source:
                return "its performance obligation no longer exists"
            if source.schedule_id and source.schedule_id != self:
                return "its obligation is scheduled by %s" % source.schedule_id.display_name
            if self.total_amount > (source.allocated_amount or 0.0) + 0.005:
                return "total %.2f is above the obligation's allocated price %.2f" % (
                    self.total_amount,
                    source.allocated_amount or 0.0,
                )
            return None
        subscription = self.subscription_id.sudo() or (
            source if self.source_model == "fix.subscription" else None
        )
        contract = self.contract_id.sudo() or (
            source if self.source_model == "fix.contract" else None
        )
        if not subscription and not contract:
            return "no contract behind it (%s #%s)" % (self.source_model, self.source_id)
        ceiling = self._fix_contract_ceiling(contract) if contract else 0.0
        if subscription:
            if subscription.contract_value:
                ceiling = subscription.contract_value
            elif subscription.contract_end_date:
                ceiling = subscription._transaction_price()
            elif subscription.contract_id and not contract:
                ceiling = self._fix_contract_ceiling(subscription.contract_id.sudo())
        named = (subscription or contract).display_name
        if ceiling <= 0:
            return "no contract value or term on %s" % named
        if self.total_amount > ceiling + 0.005:
            return "total %.2f is above the contract value %.2f of %s" % (
                self.total_amount,
                ceiling,
                named,
            )
        return None

    def _hold_unbased(self):
        """Move active schedules with no basis to Held, for a person to decide.
        Posts nothing and is idempotent. Returns the schedules it held."""
        held = self.browse()
        for schedule in self.sudo().filtered(lambda s: s.state == "active"):
            refusal = schedule._recognition_refusal()
            if not refusal:
                continue
            schedule._guarded().write({"state": "held", "hold_reason": refusal[:250]})
            schedule.message_post(
                body="Held, nothing recognised: %s. Cancel it, or send it to the CFO as a "
                "manual schedule naming its contract." % refusal
            )
            held |= schedule
        return held

    @api.model
    def _hold_legacy_schedules(self):
        """Run at upgrade, so the list shows them before the first cron run."""
        return self.sudo().search([("state", "=", "active")])._hold_unbased()

    def action_cancel_held(self, reason=""):
        """A person's decision on a held schedule: there is no contract to
        recognise it against. What it recognised earlier stays posted."""
        require_role(self.env, GROUP_ACCOUNTANT, "Cancelling a held revenue schedule")
        if not (reason or "").strip():
            raise UserError("State why the held schedule is cancelled.")
        for schedule in self:
            if schedule.state != "held":
                raise UserError(
                    "Schedule %s is %s, not held." % (schedule.display_name, schedule.state)
                )
            schedule._guarded().write(
                {"state": "cancelled", "cancelled_date": fields.Date.context_today(schedule)}
            )
            schedule.message_post(
                body="Held schedule cancelled by %s: %s"
                % (self.env.user.name, reason.strip()[:250])
            )
        return True

    def action_reopen_as_manual(self):
        """A person's decision on a held schedule: it IS owed. It becomes a
        draft manual schedule (its contract, amount, reason and evidence are
        corrected on the form) that needs the CFO's approval to recognise."""
        require_role(self.env, GROUP_ACCOUNTANT, "Reopening a held revenue schedule")
        for schedule in self:
            if schedule.state != "held":
                raise UserError(
                    "Schedule %s is %s, not held." % (schedule.display_name, schedule.state)
                )
            if schedule.line_ids:
                raise UserError(
                    "Schedule %s has already recognised %.2f: raise a new manual schedule for "
                    "the remainder." % (schedule.display_name, schedule.recognized_amount)
                )
            origin = "%s #%s" % (schedule.source_model, schedule.source_id)
            vals = {
                "state": "draft",
                "hold_reason": False,
                "source_model": "manual",
                "source_id": -schedule.id,
            }
            source = schedule._source_record()
            if source and source._name == "fix.subscription" and not schedule.subscription_id:
                vals["subscription_id"] = source.id
            schedule._guarded().write(vals)
            schedule.message_post(
                body="Reopened as a manual schedule by %s (was %s): nothing is recognised before "
                "the CFO's approval (BRU-REV-01)." % (self.env.user.name, origin)
            )
        return True

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
        as_of = as_of or fields.Date.context_today(self)
        require_role(self.env, GROUP_ACCOUNTANT, "Recognising revenue")
        for schedule in self:
            if schedule.state == "draft":
                raise UserError(
                    "Manual schedule %s is not approved: nothing is recognised before the "
                    "CFO's approval (BRU-REV-01)." % schedule.display_name
                )
            if schedule.state == "held":
                raise UserError(
                    "Schedule %s is held (%s): nothing is recognised until a person cancels it "
                    "or the CFO approves it as a manual schedule."
                    % (schedule.display_name, schedule.hold_reason or "no basis")
                )
            if schedule.state != "active" or as_of < schedule.start_date:
                continue
            refusal = schedule._recognition_refusal()
            if refusal:
                raise UserError(
                    "Revenue recognition refused for %s: %s (BRU-REV-01)."
                    % (schedule.display_name, refusal)
                )
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
        revenue = self._fix_recognition_revenue_account() or _ar_account(
            self.env, company, "revenue"
        )
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

    def _fix_recognition_revenue_account(self):
        """A04 ERP (B2, M08-F5): a contract period billed in ADVANCE carries the
        contract family's revenue account (amc/managed 400107, rental 400108)
        on fix.contract.billing.period.revenue_account_id; its recognition
        credits that account, not the generic service revenue role."""
        self.ensure_one()
        if self.source_model != "fix.ar.invoice":
            return None
        invoice = self._source_record()
        if not invoice or invoice.source_model != "fix.contract.billing.period":
            return None
        Period = self.env.get("fix.contract.billing.period")
        if Period is None or "revenue_account_id" not in Period._fields:
            return None
        period = Period.sudo().browse(invoice.source_id).exists()
        return period.revenue_account_id or None

    def _fix_post_line(self, amount, on_date, why):
        """One recognition posting outside the straight line (a cancellation
        settles what is left): Dr contract liability / Cr revenue + its line."""
        self.ensure_one()
        amount = round(amount, 2)
        if amount <= 0.005:
            return self.env["fix.revenue.recognition.line"]
        move, deferred, revenue = self.sudo()._post_recognition(amount, on_date)
        line = (
            self.env["fix.revenue.recognition.line"]
            .sudo()
            .create({"schedule_id": self.id, "date": on_date, "amount": amount, "move_id": move.id})
        )
        self.invalidate_recordset(["recognized_amount", "line_ids"])
        self.message_post(body="Recognised %.2f on %s: %s." % (amount, on_date, why))
        publish(
            self.env,
            "revenue.recognized",
            "fix.revenue.schedule",
            self.id,
            {
                "amount": amount,
                "cumulative": self.recognized_amount,
                "source_model": self.source_model,
                "source_id": self.source_id,
                "gl_debit_account": deferred.code,
                "gl_credit_account": revenue.code,
                "reason": why,
            },
        )
        return line

    def _fix_stop_at(self, on_date, keep_deferred=0.0):
        """Stop the schedule at `on_date` (a cancellation): recognise the
        straight line up to that day, then what is left beyond the
        `keep_deferred` the refund credit note takes off the liability (it was
        earned: the service ended), and cancel. A held schedule (no basis) only
        stops. Leaves the liability for this schedule at keep_deferred, which
        the credit note's issue clears (A04 ERP M39-F2/F3, M09-F2)."""
        for schedule in self.sudo():
            if schedule.state not in ("active", "held"):
                continue
            if schedule.state == "active" and not schedule._recognition_refusal():
                # what is not refunded is earned, and never more: a refund
                # measured on a slightly different day count than the straight
                # line caps the recognition (the liability then nets to zero)
                final = round(max(schedule.total_amount - (keep_deferred or 0.0), 0.0), 2)
                term = (schedule.end_date - schedule.start_date).days or 1
                elapsed = min(max((on_date - schedule.start_date).days, 0), term)
                straight = round(schedule.total_amount * elapsed / term, 2)
                done = schedule.recognized_amount
                to_date = round(min(straight, final) - done, 2)
                if to_date > 0.005:
                    schedule._fix_post_line(to_date, on_date, "recognised to the cancellation")
                    done = round(done + to_date, 2)
                forfeit = round(final - done, 2)
                if forfeit > 0.005:
                    schedule._fix_post_line(
                        forfeit, on_date, "earned on cancellation (not refunded)"
                    )
                elif forfeit < -0.005:
                    schedule.message_post(
                        body="Recognised %.2f more than the %.2f the refund leaves earned: "
                        "finance reviews the over-recognition." % (-forfeit, final)
                    )
            if schedule.state != "cancelled":
                schedule._guarded().write({"state": "cancelled", "cancelled_date": on_date})
        return True

    @api.model
    def _cron_recognize(self):
        """Daily: recognise every active schedule with a contract behind it up
        to today (M53-15). A schedule with no basis is held for a person, not
        recognised (M53-6): the first run on the live copy would otherwise post
        BDT 854,795 from two legacy schedules."""
        done = 0
        active = self.sudo().search([("state", "=", "active")])
        active._hold_unbased()
        for schedule in active.filtered(lambda s: s.state == "active"):
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
            obligation.subscription_id._fix_refuse_second_basis()
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
                    "subscription_id": sub.id,
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
