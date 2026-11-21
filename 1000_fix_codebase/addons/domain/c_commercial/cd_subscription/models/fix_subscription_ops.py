# M39 subscription operations: usage metering, proration changes and autopay
# mandates on top of fix.subscription / fix.subscription.charge and the
# revenue-recognition schedules.
#
# A04 build (2026-11-04) C2-C10, for the M39 models other than
# fix.subscription (which A08 owns):
# - the cycle charge is frozen once invoiced, cannot be backdated or overlap
#   a billed cycle, and bills the period's usage overage (it billed the
#   recurring amount only, and the billing role rewrote 30,000 -> 1 after the
#   invoice was raised);
# - usage locks once billed (billed usage was rewritten 150 -> 0);
# - a proration is COMPUTED from the plan change and the billed cycle, and a
#   credit is approved under DOFA through M63 (a -50,000 credit was typed in,
#   born 'invoiced' and backdated 90 days);
# - an autopay mandate carries the customer's consent (OTP or a signed form
#   verified by someone else), a collection limit and validity, and its
#   collection runs with retries and failure handling (it was a data shell a
#   clerk created ACTIVE with a hand-typed reference).
from datetime import timedelta

from odoo import api, fields, models
from odoo.addons.cd_contract_core.models.fix_contract import require_role
from odoo.addons.cd_service_order.models import fix_otp_util
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

SUB_OFFICER = "cd_subscription.group_subscription_officer"
BILLING = "account.group_account_user"
FINANCE_MANAGER = "account.group_account_manager"

# A04 build (2026-11-04): BUSINESS DEFAULTS TO CONFIRM (§7 decision 6,
# subscription policy).
# - A charge may start at most one cycle (31 days) in the past unless an
#   Accounting Manager raises it; older catch-up billing is a Finance call.
CHARGE_BACKDATE_DAYS = 31
# - A proration credit is approved on the existing BDT 25,000 manager line
#   (rev_rec_engine's refund threshold), then the estate cost ladder.
PRORATION_CREDIT_DOFA_THRESHOLDS = [
    (25000.0, "tier_1"),
    (250000.0, "tier_2"),
    (1000000.0, "tier_3"),
    (float("inf"), "tier_4"),
]
# - A failed autopay collection is retried after 1, 3 and 7 days; a fourth
#   failure suspends the mandate and hands the debt to dunning.
AUTOPAY_RETRY_DAYS = (1, 3, 7)
# A04 ERP M39-F4: the M20 receipt method a mandate's collection lands as (the
# two-stage MFS / card clearing for wallets and cards, bank for a bank mandate).
METHOD_FOR_MANDATE = {
    "card": "card",
    "bkash": "bkash",
    "nagad": "nagad",
    "bank": "bank_transfer",
}
# Switch: the daily billing job generates due cycle charges. It creates draft
# AR invoices, so it ships OFF ("0") until Finance turns it on.
AUTO_BILLING_PARAM = "cd_subscription.auto_billing"


class FixApprovalMatrixSubscription(models.Model):
    """M39 decision domain on the DoA register (A04 build, 2026-11-04)."""

    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[("subscription_credit", "Subscription Plan Change / Credit")],
        ondelete={"subscription_credit": "cascade"},
    )


# ---------------------------------------------------------------------------
# Cycle charge controls
# ---------------------------------------------------------------------------
CHARGE_FROZEN_FIELDS = frozenset({"amount", "period_start", "period_end", "subscription_id"})


class FixSubscriptionChargeControls(models.Model):
    _name = "fix.subscription.charge"
    _inherit = ["fix.subscription.charge", "fix.guarded.mixin"]

    usage_ids = fields.One2many("fix.subscription.usage", "charge_id", string="Usage Billed")
    overage_amount = fields.Monetary(
        string="Usage Overage Billed", currency_field="currency_id", readonly=True, copy=False
    )
    invoice_due_date = fields.Date(compute="_compute_invoice_due", string="Invoice Due")
    days_past_due = fields.Integer(compute="_compute_invoice_due", string="Days Past Due")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"invoice_id", "overage_amount"}

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if len(self) == 1 and self.invoice_id:
            locked |= CHARGE_FROZEN_FIELDS
        return locked

    @api.constrains("amount")
    def _check_charge_amount(self):
        for charge in self:
            if (charge.amount or 0.0) <= 0:
                raise ValidationError("A cycle charge must be for a positive amount.")

    @api.constrains("period_start", "period_end", "subscription_id")
    def _check_no_overlap(self):
        for charge in self:
            if charge.period_end < charge.period_start:
                raise ValidationError("A charge period cannot end before it starts.")
            overlap = self.sudo().search_count(
                [
                    ("id", "!=", charge.id),
                    ("subscription_id", "=", charge.subscription_id.id),
                    ("period_start", "<=", charge.period_end),
                    ("period_end", ">=", charge.period_start),
                ]
            )
            if overlap:
                raise ValidationError(
                    "Subscription %s is already billed for part of %s to %s: a cycle is "
                    "billed once."
                    % (charge.subscription_id.name, charge.period_start, charge.period_end)
                )

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            # A04 ERP M39-F9: a typed 1.00 charge with no invoice marked a
            # cycle billed. A cycle charge is the billing run's output.
            raise UserError(
                "A cycle charge is generated by a reviewed billing run (BRU-SUB-17), never "
                "typed: it carries its invoice and its composition."
            )
        if not self.env.su and not self.env.user.has_group(FINANCE_MANAGER):
            floor = fields.Date.context_today(self) - timedelta(days=CHARGE_BACKDATE_DAYS)
            for vals in vals_list:
                start = fields.Date.to_date(vals.get("period_start"))
                if start and start < floor:
                    raise UserError(
                        "A cycle charge from %s is backdated more than %d days. Catch-up "
                        "billing of older cycles is raised by an Accounting Manager."
                        % (start, CHARGE_BACKDATE_DAYS)
                    )
        charges = super().create(vals_list)
        charges._fix_bill_usage()
        return charges

    def write(self, vals):
        if self and not self._fix_guard_open():
            frozen = set(vals) & CHARGE_FROZEN_FIELDS
            for charge in self.filtered("invoice_id"):
                if any(charge._fix_guard_differs(n, vals[n], charge[n]) for n in frozen):
                    raise UserError(
                        "Charge %s to %s is invoiced (%s): its amount and period are fixed. "
                        "Correct it with a credit note or a proration."
                        % (charge.period_start, charge.period_end, charge.invoice_id.display_name)
                    )
        return super().write(vals)

    def _create_invoice(self):
        # The invoice link is guarded; the cycle's own invoicing sets it.
        return super(FixSubscriptionChargeControls, self._guarded())._create_invoice()

    def _fix_bill_usage(self):
        """Add the overage of every unbilled usage reading up to the end of
        this cycle to the charge, and lock those readings."""
        Usage = self.env["fix.subscription.usage"].sudo()
        for charge in self:
            usage = Usage.search(
                [
                    ("subscription_id", "=", charge.subscription_id.id),
                    ("state", "=", "open"),
                    ("period_start", "<=", charge.period_end),
                ]
            )
            if not usage:
                continue
            overage = round(sum(usage.mapped("overage_charge")), 2)
            usage._guarded().write({"state": "billed", "charge_id": charge.id})
            if overage:
                charge.sudo()._guarded().write(
                    {"amount": round(charge.amount + overage, 2), "overage_amount": overage}
                )

    def _compute_invoice_due(self):
        today = fields.Date.context_today(self)
        for charge in self:
            inv = charge.invoice_id.sudo()
            due = False
            if inv and inv.invoice_date:
                due = inv.invoice_date + timedelta(days=inv._payment_terms_days())
            charge.invoice_due_date = due
            unpaid = bool(inv and inv.state == "issued" and (inv.amount_residual or 0.0) > 0.005)
            charge.days_past_due = max((today - due).days, 0) if (due and unpaid) else 0

    @api.model
    def _fix_overdue_unpaid(self, subscription=None, as_of=None):
        """The charges whose ISSUED invoice is past its due date with money
        still owed: the basis dunning should use (A08 owns the dunning on
        fix.subscription; it keys off next_invoice_date today, M39-2)."""
        as_of = as_of or fields.Date.context_today(self)
        domain = [("invoice_id.state", "=", "issued")]
        if subscription:
            domain.append(("subscription_id", "in", subscription.ids))
        charges = self.sudo().search(domain)
        return charges.filtered(
            lambda c: c.invoice_due_date
            and c.invoice_due_date < as_of
            and (c.invoice_id.amount_residual or 0.0) > 0.005
        )

    @api.model
    def cron_generate_due_charges(self):
        """Daily, off until Finance sets cd_subscription.auto_billing = 1.

        A04 ERP M39-F9 (BRU-SUB-17): the job no longer bills. It prepares one
        dry-run billing run per company with cycles due (unless one is already
        open), for a Finance Manager who did not run it to review and a billing
        user to commit. Returns the number of runs prepared."""
        param = self.env["ir.config_parameter"].sudo().get_param(AUTO_BILLING_PARAM, "0")
        if param != "1":
            return 0
        today = fields.Date.context_today(self)
        Sub = self.env["fix.subscription"].sudo()
        Run = self.env["fix.subscription.billing.run"].sudo()
        prepared = 0
        due = Sub.search(
            [("state", "in", ("active", "past_due")), ("next_invoice_date", "<=", today)]
        )
        for company in due.mapped("company_id"):
            if Run.search_count(
                [
                    ("company_id", "=", company.id),
                    ("state", "in", ("draft", "dry_run", "reviewed", "partial")),
                ]
            ):
                continue
            try:
                with self.env.cr.savepoint():
                    run = Run.create({"company_id": company.id, "as_of": today})
                    run.action_dry_run()
                    prepared += 1
            except (UserError, ValidationError):
                continue
        return prepared


# ---------------------------------------------------------------------------
# Usage metering
# ---------------------------------------------------------------------------
USAGE_INPUT_FIELDS = frozenset(
    {
        "subscription_id",
        "period_start",
        "period_end",
        "metric",
        "quantity",
        "committed",
        "overage_rate",
    }
)


class FixSubscriptionUsage(models.Model):
    _name = "fix.subscription.usage"
    _description = "Subscription Usage Meter"
    _inherit = ["fix.guarded.mixin"]
    _order = "period_start desc, id desc"

    subscription_id = fields.Many2one(
        "fix.subscription", required=True, ondelete="cascade", index=True
    )
    period_start = fields.Date(required=True)
    period_end = fields.Date(required=True)
    metric = fields.Char(required=True, help="What is metered (seats, GB, prints…).")
    quantity = fields.Float(required=True, default=0.0)
    committed = fields.Float(required=True, default=0.0)
    overage_quantity = fields.Float(compute="_compute_overage", string="Overage", store=True)
    overage_charge = fields.Monetary(
        currency_field="currency_id", compute="_compute_overage", store=True
    )
    overage_rate = fields.Float(default=0.0, help="BDT per overage unit.")
    currency_id = fields.Many2one(related="subscription_id.currency_id", store=True)
    state = fields.Selection(
        [("open", "Open"), ("billed", "Billed")],
        default="open",
        required=True,
        readonly=True,
        help="Billed: the reading went into a cycle charge and is locked.",
    )
    charge_id = fields.Many2one(
        "fix.subscription.charge",
        string="Billed On",
        readonly=True,
        copy=False,
        ondelete="restrict",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "charge_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if len(self) == 1 and self.state == "billed":
            locked |= USAGE_INPUT_FIELDS
        return locked

    @api.depends("quantity", "committed", "overage_rate")
    def _compute_overage(self):
        for rec in self:
            over = max(0.0, (rec.quantity or 0.0) - (rec.committed or 0.0))
            rec.overage_quantity = over
            rec.overage_charge = round(over * (rec.overage_rate or 0.0), 2)

    @api.constrains("period_start", "period_end", "quantity", "committed", "overage_rate")
    def _check_reading(self):
        for rec in self:
            if rec.period_end < rec.period_start:
                raise ValidationError("A usage period cannot end before it starts.")
            if min(rec.quantity, rec.committed, rec.overage_rate) < 0:
                raise ValidationError("Usage, commitment and overage rate cannot be negative.")

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, SUB_OFFICER, "Recording subscription usage")
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            require_role(self.env, SUB_OFFICER, "Editing subscription usage")
            frozen = set(vals) & USAGE_INPUT_FIELDS
            for rec in self.filtered(lambda r: r.state == "billed"):
                if any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in frozen):
                    raise UserError(
                        "Usage of %s to %s is billed on a cycle charge and locked."
                        % (rec.period_start, rec.period_end)
                    )
        return super().write(vals)

    def unlink(self):
        if not self._fix_guard_open() and self.filtered(lambda r: r.state == "billed"):
            raise UserError("A billed usage reading cannot be deleted.")
        return super().unlink()


# ---------------------------------------------------------------------------
# Plan-change proration
# ---------------------------------------------------------------------------
PRORATION_INPUT_FIELDS = frozenset(
    {"subscription_id", "change_type", "to_plan", "new_amount", "effective_date", "name"}
)


class FixSubscriptionProration(models.Model):
    _name = "fix.subscription.proration"
    _description = "Subscription Proration"
    _inherit = ["mail.thread", "fix.dofa.mixin"]
    _order = "effective_date desc, id desc"

    # A credit is a manual concession: DOFA on its size, routed through M63.
    # A charge to the customer (an upgrade) is decided by a billing user who
    # did not raise it.
    _approval_domain = "subscription_credit"
    _approval_apply_method = "action_dofa_approve"
    _approval_group = BILLING
    _approval_routed = True

    name = fields.Char(required=True)
    subscription_id = fields.Many2one(
        "fix.subscription", required=True, ondelete="cascade", index=True
    )
    change_type = fields.Selection(
        [("upgrade", "Upgrade"), ("downgrade", "Downgrade"), ("cancel", "Cancellation")],
        required=True,
        default="upgrade",
    )
    from_plan = fields.Char(readonly=True, help="The plan in force, read from the subscription.")
    to_plan = fields.Char()
    old_amount = fields.Monetary(
        currency_field="currency_id",
        readonly=True,
        help="The recurring amount in force, read from the subscription.",
    )
    new_amount = fields.Monetary(currency_field="currency_id", string="New Recurring Amount")
    charge_id = fields.Many2one(
        "fix.subscription.charge", string="Billed Cycle", readonly=True, copy=False
    )
    cycle_days = fields.Integer(readonly=True, copy=False)
    days_remaining = fields.Integer(readonly=True, copy=False)
    amount = fields.Monetary(
        currency_field="currency_id",
        readonly=True,
        help="Computed: (new - old) x unused days / cycle days of the billed cycle. "
        "Negative is a credit to the customer.",
    )
    currency_id = fields.Many2one(related="subscription_id.currency_id", store=True)
    effective_date = fields.Date(required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending", "Awaiting Approval"),
            ("approved", "Approved"),
            ("invoiced", "Invoiced"),
            ("void", "Void"),
        ],
        required=True,
        default="draft",
        readonly=True,
        tracking=True,
    )
    invoice_id = fields.Many2one("fix.ar.invoice", readonly=True, copy=False)
    credit_note_id = fields.Many2one("fix.credit.note", readonly=True, copy=False)
    applied_to_subscription = fields.Boolean(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "amount",
            "from_plan",
            "old_amount",
            "charge_id",
            "cycle_days",
            "days_remaining",
            "invoice_id",
            "credit_note_id",
            "applied_to_subscription",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if len(self) == 1 and self.state != "draft":
            locked |= PRORATION_INPUT_FIELDS
        return locked

    # ---- DOFA: only a credit is a concession ------------------------------------
    def _dofa_amount(self) -> float:
        self.ensure_one()
        return abs(self.amount) if (self.amount or 0.0) < 0 else 0.0

    def _dofa_thresholds(self):
        return PRORATION_CREDIT_DOFA_THRESHOLDS

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "BDT %.2f (proration credit on %s)" % (
            self._dofa_amount(),
            self.subscription_id.name,
        )

    @api.depends("amount")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def _approval_needed(self) -> bool:
        return True

    def _approval_tier(self):
        tier = self._dofa_current_tier()
        return tier if tier != "tier_0" else False

    # ---- the computation -----------------------------------------------------------
    def _proration_values(self):
        """What the subscription and its billed cycle say: the plan and price
        in force, the cycle covering the effective date, and the amount."""
        self.ensure_one()
        sub = self.subscription_id.sudo()
        old = sub.recurring_amount or 0.0
        charge = sub.charge_ids.filtered(
            lambda c: c.period_start <= self.effective_date <= c.period_end
        ).sorted("period_start")[-1:]
        vals = {
            "from_plan": sub.plan,
            "old_amount": old,
            "charge_id": charge.id or False,
            "cycle_days": 0,
            "days_remaining": 0,
            "amount": 0.0,
        }
        if charge:
            cycle = (charge.period_end - charge.period_start).days + 1
            left = (charge.period_end - self.effective_date).days + 1
            new = 0.0 if self.change_type == "cancel" else (self.new_amount or 0.0)
            vals.update(
                {
                    "cycle_days": cycle,
                    "days_remaining": left,
                    "amount": round((new - old) * left / cycle, 2) if cycle else 0.0,
                }
            )
        return vals

    def _proration_refresh(self):
        for rec in self:
            rec.sudo()._guarded().write(rec._proration_values())

    @api.constrains("new_amount")
    def _check_new_amount(self):
        for rec in self:
            if (rec.new_amount or 0.0) < 0:
                raise ValidationError("A recurring amount cannot be negative.")

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, SUB_OFFICER, "Raising a plan change")
        today = fields.Date.context_today(self)
        for vals in vals_list:
            eff = fields.Date.to_date(vals.get("effective_date"))
            if not self.env.su and eff and eff < today:
                raise UserError(
                    "A plan change takes effect from today or later (%s is backdated)." % eff
                )
        records = super().create(vals_list)
        records._proration_refresh()
        return records

    def write(self, vals):
        if self and not self._fix_guard_open():
            frozen = set(vals) & PRORATION_INPUT_FIELDS
            for rec in self.filtered(lambda r: r.state != "draft"):
                if any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in frozen):
                    raise UserError(
                        "Proration %s is %s: its terms are fixed. Void it and raise a new one."
                        % (rec.name, rec.state)
                    )
            eff = vals.get("effective_date")
            if eff and fields.Date.to_date(eff) < fields.Date.context_today(self):
                raise UserError("A plan change takes effect from today or later.")
        result = super().write(vals)
        if self and set(vals) & {"new_amount", "effective_date", "change_type", "subscription_id"}:
            self.filtered(lambda r: r.state == "draft")._proration_refresh()
        return result

    @api.model
    def create_for_plan_change(self, subscription, new_amount, to_plan=None, effective_date=None):
        """The service A08's plan / price change should call: a DRAFT
        proration computed from the billed cycle, to submit for approval.
        On approval the new plan and price are applied to the subscription."""
        old = subscription.recurring_amount or 0.0
        change = "cancel" if not new_amount else ("upgrade" if new_amount > old else "downgrade")
        return self.create(
            {
                "name": "%s: %s -> %s" % (subscription.name, old, new_amount),
                "subscription_id": subscription.id,
                "change_type": change,
                "to_plan": to_plan or subscription.plan,
                "new_amount": new_amount,
                "effective_date": effective_date or fields.Date.context_today(self),
            }
        )

    # ---- lifecycle -------------------------------------------------------------------
    def _proration_require_state(self, allowed, what):
        for rec in self:
            if rec.state not in allowed:
                raise UserError("Proration %s cannot %s: it is %s." % (rec.name, what, rec.state))

    def action_request_approval(self, justification=None):
        require_role(self.env, SUB_OFFICER, "Submitting a plan change")
        self._proration_require_state(("draft",), "be submitted")
        self._proration_refresh()
        for rec in self:
            if rec.change_type != "cancel" and rec.new_amount == rec.old_amount and not rec.to_plan:
                raise UserError("Proration %s changes nothing." % rec.name)
        result = super().action_request_approval(justification=justification)
        self._guarded().write({"state": "pending"})
        return result

    def action_dofa_approve(self):
        self._approval_assert_routed()
        self._proration_require_state(("pending",), "be approved")
        for rec in self:
            if rec._dofa_current_tier() == "tier_0":
                if not (self.env.su or self.env.user.has_group(BILLING)):
                    raise UserError("A plan change is approved by a billing user.")
                if not self.env.su and rec.create_uid in rec._approval_acting_users():
                    raise UserError(
                        "Segregation of duties: you raised proration %s, so someone else "
                        "must approve it." % rec.name
                    )
            else:
                super(FixSubscriptionProration, rec.sudo()).action_dofa_approve()
        today = fields.Date.context_today(self)
        for rec in self.sudo():
            rec._guarded().write({"state": "approved"})
            # A04 ERP M39-F7: a change dated ahead applies on its date (the
            # daily cron), priced on the cycle billed then; it applied at
            # once with 0 proration
            if rec.effective_date <= today:
                rec._proration_refresh_approved()
                rec._proration_apply_to_subscription()
            publish(
                self.env,
                "subscription.proration_approved",
                "fix.subscription.proration",
                rec.id,
                {
                    "subscription_id": rec.subscription_id.id,
                    "customer_id": rec.subscription_id.customer_id.id,
                    "change_type": rec.change_type,
                    "amount": float(rec.amount or 0.0),
                    "old_amount": float(rec.old_amount or 0.0),
                    "new_amount": float(rec.new_amount or 0.0),
                    "effective_date": str(rec.effective_date),
                    "charge_id": rec.charge_id.id or None,
                },
            )
        return True

    def _proration_refresh_approved(self):
        """Re-read the billed cycle covering the effective date (an approved
        change dated ahead had no cycle to prorate when it was approved)."""
        for rec in self:
            rec.sudo()._guarded().write(rec._proration_values())

    @api.model
    def cron_apply_due_prorations(self):
        """Daily: approved changes whose effective date has come are priced on
        the cycle that covers it and applied to the subscription; the next
        cycle charge then bills (or credits) the proration."""
        today = fields.Date.context_today(self)
        due = self.sudo().search(
            [
                ("state", "=", "approved"),
                ("applied_to_subscription", "=", False),
                ("effective_date", "<=", today),
            ],
            order="effective_date, id",
        )
        for rec in due:
            try:
                with self.env.cr.savepoint():
                    rec._proration_refresh_approved()
                    rec._proration_apply_to_subscription()
            except (UserError, ValidationError) as exc:
                rec.message_post(body="Could not apply on its date: %s" % exc)
        return len(due)

    def _proration_apply_to_subscription(self):
        """The approved change becomes the subscription's plan and price for
        the next cycle (service write, under the approval)."""
        for rec in self:
            sub = rec.subscription_id.sudo()
            # A02 ERP pass 2 (M05-S05): a change computed from an amount the
            # subscription no longer has would overwrite the change applied in
            # between (two MSP uplifts approved one after the other kept only
            # the second). It is refused; void it and raise it again.
            if (
                rec.change_type != "cancel"
                and abs((sub.recurring_amount or 0.0) - (rec.old_amount or 0.0)) > 0.005
            ):
                raise UserError(
                    "Plan change %s was computed from a recurring amount of %.2f, but %s now "
                    "bills %.2f (another change was applied since). Void it and raise it again "
                    "from the current amount."
                    % (rec.name, rec.old_amount, sub.name, sub.recurring_amount)
                )
            vals = {}
            if rec.change_type != "cancel":
                vals["recurring_amount"] = rec.new_amount
                plans = dict(sub._fields["plan"].selection)
                if rec.to_plan and rec.to_plan in plans:
                    vals["plan"] = rec.to_plan
            if vals:
                sub.write(vals)
            rec._guarded().write({"applied_to_subscription": True})
            sub.message_post(
                body="Plan change %s approved: %s"
                % (rec.name, ", ".join("%s=%s" % kv for kv in vals.items()))
            )
            # the MSP terms amendments this change billed (M05-S05)
            Amendment = self.env.get("fix.msp.terms.amendment")
            if Amendment is not None:
                Amendment.sudo()._guarded().search(
                    [("billing_ref", "=", "fix.subscription.proration,%s" % rec.id)]
                ).write({"billing_state": "billed"})

    def _approval_on_rejected(self, comment):
        self.sudo().filtered(lambda r: r.state == "pending")._guarded().write({"state": "void"})
        return super()._approval_on_rejected(comment)

    def action_recall_approval(self):
        result = super().action_recall_approval()
        self.filtered(lambda r: r.state == "pending")._guarded().write({"state": "draft"})
        return result

    def action_void(self):
        require_role(self.env, SUB_OFFICER, "Voiding a plan change")
        self._proration_require_state(("draft", "pending"), "be voided")
        for rec in self:
            rec._approval_void("the proration was voided")
            rec.sudo()._guarded().write({"state": "void", "approval_state": "none"})
        return True

    def _fix_mark_invoiced(self, invoice=None, credit_note=None):
        """The finance bridge (C7) calls this, as a service, once it has
        raised the M20 invoice (amount > 0) or credit note (amount < 0)."""
        if not self.env.su:
            raise UserError("A proration is marked invoiced by the billing hand-off only.")
        for rec in self:
            rec._proration_require_state(("approved",), "be invoiced")
            rec._guarded().write(
                {
                    "state": "invoiced",
                    "invoice_id": invoice.id if invoice else False,
                    "credit_note_id": credit_note.id if credit_note else False,
                }
            )
        return True


# ---------------------------------------------------------------------------
# Autopay mandate
# ---------------------------------------------------------------------------
MANDATE_TERM_FIELDS = frozenset(
    {
        "subscription_id",
        "method",
        "mandate_ref",
        "max_amount",
        "valid_from",
        "valid_until",
        "consent_channel",
        "consent_phone",
        "consent_signatory",
        "consent_document_id",
    }
)
MANDATE_GUARDED = frozenset(
    {
        "state",
        "consent_at",
        "consent_evidence",
        "consent_recorded_by",
        "consent_verified_by",
        "otp_digest",
        "otp_expires_at",
        "otp_attempts",
        "gateway_token",
        "last_attempt_at",
        "last_result",
        "failure_count",
        "next_retry_on",
        "last_failure_reason",
    }
)


class FixSubscriptionAutopay(models.Model):
    _name = "fix.subscription.autopay"
    _description = "Subscription Autopay Mandate"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    subscription_id = fields.Many2one(
        "fix.subscription", required=True, ondelete="cascade", index=True
    )
    method = fields.Selection(
        [("card", "Card"), ("bkash", "bKash"), ("nagad", "Nagad"), ("bank", "Bank mandate")],
        required=True,
        default="card",
    )
    mandate_ref = fields.Char(help="Gateway mandate / token reference.")
    state = fields.Selection(
        [
            ("draft", "Awaiting Consent"),
            ("active", "Active"),
            ("suspended", "Suspended (collection failed)"),
            ("revoked", "Revoked"),
            ("expired", "Expired"),
        ],
        required=True,
        default="draft",
        readonly=True,
        tracking=True,
    )
    currency_id = fields.Many2one(related="subscription_id.currency_id")
    max_amount = fields.Monetary(
        string="Collection Limit",
        currency_field="currency_id",
        help="The most a single collection may take, as the customer consented.",
    )
    valid_from = fields.Date(default=fields.Date.context_today)
    valid_until = fields.Date()
    # --- consent evidence ---------------------------------------------------
    consent_channel = fields.Selection(
        [("otp", "Customer OTP"), ("signed_form", "Signed Mandate Form")],
        string="Consent Channel",
        default="otp",
        required=True,
    )
    consent_phone = fields.Char(
        string="Consenting Phone", help="The account holder's mobile; the customer's when empty."
    )
    consent_signatory = fields.Char(string="Account Holder")
    consent_document_id = fields.Many2one(
        "fix.document", string="Signed Mandate Form", ondelete="restrict"
    )
    consent_at = fields.Datetime(readonly=True, copy=False)
    consent_evidence = fields.Char(readonly=True, copy=False)
    consent_recorded_by = fields.Many2one("res.users", readonly=True, copy=False)
    consent_verified_by = fields.Many2one("res.users", readonly=True, copy=False)
    otp_digest = fields.Char(readonly=True, copy=False, groups="base.group_system")
    otp_expires_at = fields.Datetime(readonly=True, copy=False)
    otp_attempts = fields.Integer(readonly=True, copy=False)
    gateway_token = fields.Char(readonly=True, copy=False, groups="base.group_system")
    # --- collection ---------------------------------------------------------
    last_attempt_at = fields.Datetime(readonly=True)
    last_result = fields.Selection(
        [("none", "Never charged"), ("success", "Success"), ("failed", "Failed")],
        required=True,
        default="none",
        readonly=True,
    )
    failure_count = fields.Integer(readonly=True, copy=False)
    next_retry_on = fields.Date(readonly=True, copy=False)
    last_failure_reason = fields.Char(readonly=True, copy=False)
    attempt_ids = fields.One2many(
        "fix.subscription.autopay.attempt", "mandate_id", string="Collection Attempts"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | MANDATE_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if len(self) == 1 and (self.state != "draft" or self.consent_at):
            locked |= MANDATE_TERM_FIELDS
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, SUB_OFFICER, "Capturing an autopay mandate")
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            require_role(self.env, SUB_OFFICER, "Editing an autopay mandate")
            frozen = set(vals) & MANDATE_TERM_FIELDS
            for rec in self.filtered(lambda r: r.state != "draft" or r.consent_at):
                if any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in frozen):
                    raise UserError(
                        "The customer consented to these mandate terms; they cannot be "
                        "changed. Revoke the mandate and capture a new one."
                    )
        return super().write(vals)

    def _mandate_require_state(self, allowed, what):
        for rec in self:
            if rec.state not in allowed:
                raise UserError("The mandate cannot %s: it is %s." % (what, rec.state))

    def _mandate_phone(self):
        self.ensure_one()
        if self.consent_phone:
            partner = self.env["res.partner"].new({"phone": self.consent_phone})
            return fix_otp_util.bd_mobile(partner)
        return fix_otp_util.bd_mobile(self.subscription_id.customer_id)

    # ---- consent ----------------------------------------------------------------------
    def action_send_consent_otp(self):
        """Send the account holder a one-time code to consent to the mandate."""
        require_role(self.env, SUB_OFFICER, "Requesting mandate consent")
        self._mandate_require_state(("draft",), "collect consent")
        for rec in self:
            if rec.consent_channel != "otp":
                raise UserError("This mandate's consent is a signed form, not an OTP.")
            if (rec.max_amount or 0.0) <= 0:
                raise UserError("Set the collection limit the customer is consenting to first.")
            phone = rec._mandate_phone()
            if not phone:
                raise UserError("There is no valid Bangladesh mobile number for the consent code.")
            code = fix_otp_util.issue_code()
            fix_otp_util.dispatch_otp(phone, code, fix_otp_util.OTP_TTL_SECONDS)
            rec.sudo()._guarded().write(
                {
                    "otp_digest": fix_otp_util.digest(self.env, "autopay_consent", rec.id, code),
                    "otp_expires_at": fields.Datetime.now()
                    + timedelta(seconds=fix_otp_util.OTP_TTL_SECONDS),
                    "otp_attempts": 0,
                }
            )
            rec.message_post(body="Consent code sent to %s." % fix_otp_util.mask(phone))
        return True

    def action_verify_consent_otp(self, otp=None, code=None):
        """Record the customer's consent from the code they read back. A
        wrong code is counted, not raised; five misses burn it."""
        require_role(self.env, SUB_OFFICER, "Recording mandate consent")
        code = (otp or code or "").strip()
        result = {"verified": True}
        for rec in self:
            stored = rec.sudo().otp_digest
            if rec.state != "draft" or not stored or not rec.otp_expires_at:
                raise UserError("Send the customer a consent code first.")
            if fields.Datetime.now() > rec.otp_expires_at:
                raise UserError("The consent code has expired. Send a new one.")
            if not fix_otp_util.matches(self.env, "autopay_consent", rec.id, code, stored):
                attempts = rec.otp_attempts + 1
                burnt = attempts >= fix_otp_util.OTP_MAX_ATTEMPTS
                rec.sudo()._guarded().write(
                    {"otp_attempts": attempts, "otp_digest": False if burnt else stored}
                )
                result = {
                    "verified": False,
                    "error": "That consent code is not correct."
                    + (" Too many attempts: send a new code." if burnt else ""),
                }
                continue
            now = fields.Datetime.now()
            rec.sudo()._guarded().write(
                {
                    "otp_digest": False,
                    "consent_at": now,
                    "consent_evidence": "OTP %s %s (limit %.2f)"
                    % (fix_otp_util.mask(rec._mandate_phone()), now, rec.max_amount),
                    "consent_recorded_by": self.env.user.id,
                }
            )
            rec.message_post(body="Customer consent verified by code.")
        return result

    def action_verify_signed_form(self):
        """A signed mandate form, verified by an officer who did not capture
        the mandate (segregation of duties)."""
        require_role(self.env, SUB_OFFICER, "Verifying a signed mandate form")
        self._mandate_require_state(("draft",), "be verified")
        for rec in self:
            if rec.consent_channel != "signed_form":
                raise UserError("This mandate's consent is by OTP.")
            if not rec.consent_document_id or not rec.consent_document_id.sudo().attachment_id:
                raise UserError("Attach the signed mandate form first.")
            if not (rec.consent_signatory or "").strip() or (rec.max_amount or 0.0) <= 0:
                raise UserError("The form needs the account holder and the collection limit.")
            if not self.env.su and rec.create_uid == self.env.user:
                raise UserError(
                    "Segregation of duties: you captured this mandate, so another "
                    "Subscription Officer must verify the signed form."
                )
            now = fields.Datetime.now()
            rec.sudo()._guarded().write(
                {
                    "consent_at": now,
                    "consent_evidence": "Signed form %s by %s (limit %.2f)"
                    % (rec.consent_document_id.display_name, rec.consent_signatory, rec.max_amount),
                    "consent_recorded_by": rec.create_uid.id,
                    "consent_verified_by": self.env.user.id,
                }
            )
        return True

    def action_activate(self):
        require_role(self.env, SUB_OFFICER, "Activating an autopay mandate")
        self._mandate_require_state(("draft",), "be activated")
        today = fields.Date.context_today(self)
        for rec in self:
            if not rec.consent_at:
                raise UserError("A mandate activates only on the customer's recorded consent.")
            if (rec.max_amount or 0.0) <= 0:
                raise UserError("The mandate has no collection limit.")
            if rec.valid_until and rec.valid_until < today:
                raise UserError("The mandate's validity has already ended.")
            if rec.subscription_id.state in ("cancelled", "churned"):
                raise UserError("The subscription is closed.")
            other = self.sudo().search_count(
                [
                    ("subscription_id", "=", rec.subscription_id.id),
                    ("state", "=", "active"),
                    ("id", "!=", rec.id),
                ]
            )
            if other:
                raise UserError("The subscription already has an active mandate; revoke it first.")
            rec.sudo()._guarded().write({"state": "active"})
        return True

    def action_revoke(self, reason=None):
        require_role(self.env, SUB_OFFICER, "Revoking an autopay mandate")
        self._mandate_require_state(("draft", "active", "suspended"), "be revoked")
        for rec in self:
            rec.sudo()._guarded().write({"state": "revoked"})
            rec.message_post(body="Mandate revoked by %s. %s" % (self.env.user.name, reason or ""))
        return True

    def register_gateway_token(self, token, mandate_ref=None):
        """The payment-gateway integration (a service) records the provider's
        token for a mandate the customer consented to."""
        if not self.env.su:
            raise UserError(
                "The gateway token is recorded by the payment-gateway integration only."
            )
        vals = {"gateway_token": token}
        if mandate_ref:
            vals["mandate_ref"] = mandate_ref
        self._guarded().write(vals)
        return True

    # ---- collection -------------------------------------------------------------------
    def _mandate_due_charges(self):
        """Issued, unpaid charges of the subscription with no collection open."""
        self.ensure_one()
        Attempt = self.env["fix.subscription.autopay.attempt"].sudo()
        today = fields.Date.context_today(self)
        charges = self.subscription_id.sudo().charge_ids.filtered(
            lambda c: c.invoice_id
            and c.invoice_id.state == "issued"
            and (c.invoice_id.amount_residual or 0.0) > 0.005
            and c.invoice_id.invoice_date
            and c.invoice_id.invoice_date <= today
        )
        open_ = Attempt.search(
            [("charge_id", "in", charges.ids), ("state", "=", "requested")]
        ).mapped("charge_id")
        return charges - open_

    @api.model
    def cron_autopay_collect(self):
        """Daily, idempotent: request a collection for every issued, unpaid
        charge of a consented, active mandate (a retry waits for its day).
        The gateway's answer comes back through the attempt's
        action_record_result. Returns the number of requests."""
        today = fields.Date.context_today(self)
        mandates = self.sudo().search([("state", "=", "active"), ("consent_at", "!=", False)])
        Attempt = self.env["fix.subscription.autopay.attempt"].sudo()
        requested = 0
        for mandate in mandates:
            if mandate.valid_until and mandate.valid_until < today:
                mandate._guarded().write({"state": "expired"})
                continue
            if mandate.next_retry_on and mandate.next_retry_on > today:
                continue
            for charge in mandate._mandate_due_charges():
                amount = round(charge.invoice_id.amount_residual, 2)
                if amount > (mandate.max_amount or 0.0) + 0.005:
                    Attempt.create(
                        {
                            "mandate_id": mandate.id,
                            "charge_id": charge.id,
                            "amount": amount,
                            "state": "over_limit",
                            "reason": "BDT %.2f exceeds the consented limit %.2f"
                            % (amount, mandate.max_amount),
                        }
                    )
                    continue
                attempt = Attempt.create(
                    {"mandate_id": mandate.id, "charge_id": charge.id, "amount": amount}
                )
                mandate._guarded().write({"last_attempt_at": fields.Datetime.now()})
                publish(
                    self.env,
                    "subscription.autopay_collection_requested",
                    "fix.subscription.autopay",
                    mandate.id,
                    {
                        "attempt_id": attempt.id,
                        "subscription_id": mandate.subscription_id.id,
                        "charge_id": charge.id,
                        "invoice_id": charge.invoice_id.id,
                        "amount": amount,
                        "method": mandate.method,
                        "mandate_ref": mandate.mandate_ref or "",
                    },
                )
                requested += 1
        return requested


class FixSubscriptionAutopayAttempt(models.Model):
    """One collection request against a mandate, and the gateway's answer."""

    _name = "fix.subscription.autopay.attempt"
    _description = "Autopay Collection Attempt"
    _order = "id desc"

    mandate_id = fields.Many2one(
        "fix.subscription.autopay", required=True, ondelete="cascade", index=True
    )
    charge_id = fields.Many2one("fix.subscription.charge", required=True, ondelete="restrict")
    invoice_id = fields.Many2one(related="charge_id.invoice_id", store=True)
    currency_id = fields.Many2one(related="mandate_id.currency_id")
    amount = fields.Monetary(currency_field="currency_id", required=True)
    state = fields.Selection(
        [
            ("requested", "Requested"),
            ("success", "Collected"),
            ("failed", "Failed"),
            ("over_limit", "Over the Consented Limit"),
        ],
        default="requested",
        required=True,
    )
    provider_ref = fields.Char()
    reason = fields.Char()
    requested_at = fields.Datetime(default=fields.Datetime.now, required=True)
    decided_at = fields.Datetime()
    receipt_id = fields.Many2one(
        "fix.ar.receipt",
        string="M20 Receipt",
        readonly=True,
        copy=False,
        help="A04 ERP M39-F4: the receipt a successful collection became, allocated to the "
        "cycle invoice (one per attempt).",
    )

    _receipt_unique = models.Constraint("UNIQUE (receipt_id)", "One receipt per collection attempt")

    @api.model
    def consume_autopay_succeeded(self, event: dict) -> dict:
        """subscription.autopay_succeeded -> a confirmed M20 receipt on the
        customer, allocated to the cycle invoice up to its residual; the rest
        stays unapplied on the receipt. Idempotent per attempt. Relay only;
        the attempt is re-read, the payload is a claim."""
        if not self.env.su:
            raise AccessError("The autopay receipt consumer runs only from the event relay.")
        payload = event.get("payload") or {}
        try:
            attempt_id = int(payload.get("attempt_id") or 0)
        except (TypeError, ValueError):
            attempt_id = 0
        attempt = self.sudo().browse(attempt_id).exists() if attempt_id else None
        if not attempt:
            raise UserError(
                "Autopay receipt refused: there is no collection attempt #%s." % attempt_id
            )
        if attempt.mandate_id.id != int(event.get("aggregate_id") or 0):
            raise UserError("Autopay receipt refused: the attempt belongs to another mandate.")
        if attempt.state != "success":
            raise UserError(
                "Autopay receipt refused: attempt #%s is %s, not collected."
                % (attempt.id, attempt.state)
            )
        claimed = payload.get("amount")
        if claimed is not None and abs(float(claimed) - attempt.amount) > 0.005:
            raise UserError(
                "Autopay receipt refused: the event says %.2f, the attempt %.2f."
                % (float(claimed), attempt.amount)
            )
        if attempt.receipt_id:
            return {"model": "fix.ar.receipt", "id": attempt.receipt_id.id, "created": False}
        return attempt._fix_book_receipt()

    def _fix_book_receipt(self):
        self.ensure_one()
        invoice = self.invoice_id.sudo()
        if not invoice:
            raise UserError("Autopay receipt refused: attempt #%s has no invoice." % self.id)
        method = METHOD_FOR_MANDATE.get(self.mandate_id.method, "bank_transfer")
        Receipt = self.env["fix.ar.receipt"].sudo().with_company(invoice.company_id)
        receipt = Receipt.create(
            {
                "company_id": invoice.company_id.id,
                "operating_unit_id": invoice.operating_unit_id.id or False,
                "branch_id": invoice.branch_id.id or False,
                "customer_id": invoice.customer_id.id,
                "amount": round(self.amount, 2),
                "method": method,
                "reference": (self.provider_ref or "AUTOPAY-%s" % self.id)[:64],
                "receipt_date": fields.Date.context_today(self),
            }
        )
        receipt.action_confirm()
        self.write({"receipt_id": receipt.id})
        invoice.invalidate_recordset(["amount_residual"])
        applied = round(min(receipt.amount, invoice.amount_residual or 0.0), 2)
        if invoice.state == "issued" and applied > 0.005:
            self.env["fix.ar.allocation"].sudo().create(
                {"receipt_id": receipt.id, "invoice_id": invoice.id, "amount": applied}
            )
        self.mandate_id.message_post(
            body="Collection %s booked as receipt %s; BDT %.2f applied to %s."
            % (self.provider_ref or self.id, receipt.name, max(applied, 0.0), invoice.name)
        )
        return {"model": "fix.ar.receipt", "id": receipt.id, "created": True}

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            raise UserError("Collection attempts are raised by the autopay job only.")
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.su:
            raise UserError("A collection attempt is recorded by the payment gateway only.")
        return super().write(vals)

    def action_record_result(self, result, provider_ref=None, reason=None):
        """The payment-gateway integration (a service) records the answer.
        Success hands the money to M20 (subscription.autopay_succeeded, for
        the receipt); a failure schedules the retry, and the last failure
        suspends the mandate and hands the debt to dunning."""
        if not self.env.su:
            raise UserError("A collection result is recorded by the payment gateway only.")
        if result not in ("success", "failed"):
            raise UserError("A collection result is 'success' or 'failed'.")
        today = fields.Date.context_today(self)
        for attempt in self:
            if attempt.state != "requested":
                raise UserError("This collection attempt is already decided.")
            mandate = attempt.mandate_id
            attempt.write(
                {
                    "state": result,
                    "provider_ref": provider_ref or False,
                    "reason": reason or False,
                    "decided_at": fields.Datetime.now(),
                }
            )
            if result == "success":
                mandate._guarded().write(
                    {
                        "last_result": "success",
                        "failure_count": 0,
                        "next_retry_on": False,
                        "last_failure_reason": False,
                    }
                )
                publish(
                    self.env,
                    "subscription.autopay_succeeded",
                    "fix.subscription.autopay",
                    mandate.id,
                    {
                        "attempt_id": attempt.id,
                        "subscription_id": mandate.subscription_id.id,
                        "charge_id": attempt.charge_id.id,
                        "invoice_id": attempt.invoice_id.id,
                        "amount": float(attempt.amount),
                        "provider_ref": provider_ref or "",
                    },
                )
                continue
            failures = mandate.failure_count + 1
            vals = {
                "last_result": "failed",
                "failure_count": failures,
                "last_failure_reason": reason or False,
            }
            if failures <= len(AUTOPAY_RETRY_DAYS):
                vals["next_retry_on"] = today + timedelta(days=AUTOPAY_RETRY_DAYS[failures - 1])
            else:
                vals.update({"state": "suspended", "next_retry_on": False})
                publish(
                    self.env,
                    "subscription.autopay_failed",
                    "fix.subscription.autopay",
                    mandate.id,
                    {
                        "subscription_id": mandate.subscription_id.id,
                        "charge_id": attempt.charge_id.id,
                        "invoice_id": attempt.invoice_id.id,
                        "failures": failures,
                        "reason": reason or "",
                    },
                )
            mandate._guarded().write(vals)
        return True
