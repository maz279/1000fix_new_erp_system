"""M20 second capture pass (19 Nov 2026): the records the spec says a
person captures on a sub-module page and that had no model.

- p4  fix.ar.invoice.delivery  FR-ARB-013/014 (P0): one record per invoice
      and channel; re-delivery is a retry on it, never a second record or a
      second payment link (T-12).
- p4  fix.ar.statement         FR-ARB-017 (P0): a statement of account
      generated on demand, frozen once generated, then marked delivered.
- p5  fix.ar.deposit           FR-ARB-028 (P1): deposit / retention /
      advance money held apart from trade receivables, applied to an
      invoice or released as a refund.
- p8  fix.ar.dunning.policy    FR-ARB-032 (P0): the reminder ladder per
      segment or named account. The dunning run reads it; the NT-006
      constants are the fallback only.
- p8  fix.ar.promise           FR-ARB-035 (P1): holds dunning until the date,
      kept or broken by the daily check; a broken promise resumes dunning
      and escalates the collection case (AUT-ARB-12).
- p8  fix.ar.payment.plan      FR-ARB-037 (P2): instalments agreed by a
      second person; dunning held while it runs; a missed instalment
      defaults it and resumes dunning.
- p8  fix.ar.collection.case   FR-ARB-034 (P1): the prioritised worklist
      item, opened by an escalated dunning run, a broken promise, a
      defaulted plan or a collector.
- p9  fix.ar.refund            FR-ARB-040 (P0): refund of on-account money
      (an unapplied receipt or a released deposit), authorised by another
      person, cash above the threshold refused, executed by M50.
- p10 fix.ar.unbilled.exception FR-ARB-043 (P0), BRU-ARB-24: delivered but
      not invoiced, raised daily from the reconciliation (or reported by
      hand for streams it does not read), escalated by age, resolved with a
      reason; "not billable" needs a second person (BRU-ARB-01).
"""

from __future__ import annotations

import logging
import re

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

# The models extended below (fix.dunning, fix.ar.receipt, fix.ar.allocation)
# must be defined first, whatever order the package __init__ is sorted in.
from . import fix_billing_engine  # noqa: F401 - load order
from .fix_ar_engine import _ar_account, compute_customer_statement, compute_leakage
from .fix_finance_approval import (
    GROUP_ACCOUNTANT,
    GROUP_ADMINISTRATOR,
    float_param,
    has_role,
    require_role,
)

_logger = logging.getLogger(__name__)

CHANNELS = [
    ("portal", "Customer Portal"),
    ("email", "Email"),
    ("whatsapp", "WhatsApp"),
    ("sms", "SMS"),
    ("print", "Print"),
]
LADDER_CHANNELS = [*CHANNELS, ("call", "Collector Call")]
TONES = [("friendly", "Friendly reminder"), ("firm", "Firm"), ("final", "Final notice")]
SEGMENTS = [
    ("all", "All customers (default ladder)"),
    ("retail", "Retail / walk-in (individuals)"),
    ("corporate", "Corporate accounts (companies)"),
]
ESCALATION_ROLES = [
    ("collector", "Collector"),
    ("finance_manager", "Finance Manager"),
    ("cfo", "Chief Financial Officer"),
]
CASE_OUTCOMES = [
    ("paid", "Paid in full"),
    ("promise", "Promise to pay recorded"),
    ("payment_plan", "Payment plan agreed"),
    ("written_off", "Written off"),
    ("legal", "Referred to legal"),
    ("uncollectible", "Uncollectible"),
]
REFUND_METHODS = [
    ("bank_transfer", "Bank transfer (BEFTN / RTGS)"),
    ("bkash", "bKash"),
    ("nagad", "Nagad"),
    ("rocket", "Rocket"),
    ("cheque", "Cheque"),
    ("cash", "Cash"),
]
UNBILLED_SOURCES = [
    ("service_order", "Service order (M01)"),
    ("contract", "Contract cycle (M08)"),
    ("rental", "Rental period (M13)"),
    ("marketplace", "Marketplace / e-commerce order (M12/M38)"),
    ("subscription", "Subscription cycle (M39)"),
    ("managed_service", "Managed / data service (M05/M06)"),
    ("warranty_claim", "Warranty claim (M09)"),
    ("other", "Other delivered work"),
]
UNBILLED_RESOLUTIONS = [
    ("invoiced", "Invoiced"),
    ("not_billable", "Not billable (approved)"),
    ("duplicate", "Duplicate of another item"),
]

PARAM_PROMISE_MAX_DAYS = "cd_billing_engine.promise_max_days"
PARAM_PLAN_MAX_MISSED = "cd_billing_engine.payment_plan_max_missed"
PARAM_DELIVERY_MAX_RETRIES = "cd_billing_engine.delivery_max_retries"
PARAM_REFUND_CASH_MAX = "cd_billing_engine.refund_cash_max"
PARAM_REFUND_DIRECT_MAX = "cd_billing_engine.refund_direct_max"
PARAM_UNBILLED_DAYS = "cd_billing_engine.unbilled_escalation_days"  # "1,3,7"
EPS = 0.005


def _seq(env, code, prefix, rec):
    return env["ir.sequence"].sudo().next_by_code(code) or "%s/%05d" % (prefix, rec.id)


def _stamp_create(model, vals_list, stamps_for):
    """Create with system stamps on guarded fields: the user's own values for
    them are refused first (the mixin rule), then the stamps are written in
    the same create under the guard token."""
    if not model._fix_guard_open():
        guarded = model._fix_guarded_fields()
        for vals in vals_list:
            touched = [k for k, v in vals.items() if k in guarded and v not in (False, None, "")]
            if touched:
                model._fix_guard_refuse(touched)
    for vals in vals_list:
        vals.update(stamps_for(vals))
    return model._guarded()


GROUP_BILLING = "account.group_account_invoice"


def _require_billing(env, what):
    """Billing work: the billing clerk, an Accountant or the Accounting
    Administrator (Odoo 19's finance groups do not imply each other)."""
    if not (has_role(env, GROUP_BILLING) or has_role(env, GROUP_ACCOUNTANT)):
        raise AccessError("%s needs a billing or accounting role, which you do not hold." % what)


def _customer_segment(partner) -> str:
    return "corporate" if partner.commercial_partner_id.is_company else "retail"


# ===========================================================================
# p8 — dunning policy (FR-ARB-032)
# ===========================================================================
class FixArDunningPolicy(models.Model):
    _name = "fix.ar.dunning.policy"
    _description = "AR Dunning Policy (reminder ladder)"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "state, segment, name"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    name = fields.Char(required=True, tracking=True)
    segment = fields.Selection(SEGMENTS, required=True, default="all", tracking=True)
    customer_ids = fields.Many2many(
        "res.partner",
        "fix_ar_dunning_policy_partner_rel",
        "policy_id",
        "partner_id",
        string="Named Accounts",
        help="Customers this ladder applies to whatever their segment (a strategic account, "
        "a brand partner). A named policy wins over a segment policy.",
    )
    first_offset_days = fields.Integer(string="L1 After (days past due)", default=1, required=True)
    l1_channel = fields.Selection(
        LADDER_CHANNELS, string="L1 Channel", default="email", required=True
    )
    l1_tone = fields.Selection(TONES, string="L1 Tone", default="friendly", required=True)
    l2_days = fields.Integer(string="L2 After (days at L1)", default=7, required=True)
    l2_channel = fields.Selection(
        LADDER_CHANNELS, string="L2 Channel", default="whatsapp", required=True
    )
    l2_tone = fields.Selection(TONES, string="L2 Tone", default="firm", required=True)
    l3_days = fields.Integer(string="L3 After (days at L2)", default=14, required=True)
    l3_channel = fields.Selection(
        LADDER_CHANNELS, string="L3 Channel", default="call", required=True
    )
    l3_tone = fields.Selection(TONES, string="L3 Tone", default="final", required=True)
    escalation_role = fields.Selection(
        ESCALATION_ROLES, string="L3 Escalates To", default="collector", required=True
    )
    note = fields.Text(string="Why this ladder")
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("retired", "Retired")],
        default="draft",
        required=True,
        tracking=True,
    )
    activated_by_id = fields.Many2one("res.users", string="Activated By", readonly=True, copy=False)
    activated_at = fields.Datetime(string="Activated On", readonly=True, copy=False)
    retired_reason = fields.Char(readonly=True, copy=False)

    LADDER_FIELDS = (
        "segment",
        "customer_ids",
        "first_offset_days",
        "l1_channel",
        "l1_tone",
        "l2_days",
        "l2_channel",
        "l2_tone",
        "l3_days",
        "l3_channel",
        "l3_tone",
        "escalation_role",
        "company_id",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "activated_by_id",
            "activated_at",
            "retired_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= set(self.LADDER_FIELDS)
        return locked

    @api.constrains("first_offset_days", "l2_days", "l3_days")
    def _check_days(self):
        for rec in self:
            if rec.first_offset_days < 0:
                raise ValidationError("The first reminder goes out on or after the due date.")
            if rec.l2_days < 1 or rec.l3_days < 1:
                raise ValidationError("Each ladder level waits at least one day before the next.")

    def write(self, vals):
        if (not self._fix_guard_open() and set(self.LADDER_FIELDS) & set(vals)) and (
            self.filtered(lambda r: r.state != "draft")
        ):
            raise UserError(
                "An active or retired ladder is not edited: retire it and activate a new one, "
                "so the reminders already sent stay explained by the ladder that sent them."
            )
        return super().write(vals)

    def action_activate(self):
        """An Accounting Administrator other than the author puts the ladder
        in force. One active segment ladder per company and segment."""
        require_role(self.env, GROUP_ADMINISTRATOR, "Activating a dunning ladder")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft ladder is activated.")
            if not self.env.su and rec.create_uid == self.env.user:
                raise UserError(
                    "Segregation of duties: you wrote ladder %s; another Accounting "
                    "Administrator activates it." % rec.name
                )
            if not rec.customer_ids:
                clash = self.search(
                    [
                        ("id", "!=", rec.id),
                        ("company_id", "=", rec.company_id.id),
                        ("segment", "=", rec.segment),
                        ("state", "=", "active"),
                        ("customer_ids", "=", False),
                    ],
                    limit=1,
                )
                if clash:
                    raise UserError(
                        "Ladder %s is already in force for this segment: retire it first."
                        % clash.name
                    )
            rec._guarded().write(
                {
                    "state": "active",
                    "activated_by_id": self.env.uid,
                    "activated_at": fields.Datetime.now(),
                }
            )

    def action_retire(self, reason=""):
        require_role(self.env, GROUP_ADMINISTRATOR, "Retiring a dunning ladder")
        if not (reason or "").strip():
            raise UserError("Say why the ladder is retired.")
        for rec in self:
            if rec.state != "active":
                raise UserError("Only an active ladder is retired.")
            rec._guarded().write({"state": "retired", "retired_reason": reason.strip()[:250]})

    @api.model
    def _fix_policy_for(self, invoice):
        """The ladder in force for an invoice: a named-account ladder, else
        the customer's segment, else the company default ('all')."""
        if not invoice:
            return self.browse()
        partner = invoice.customer_id.commercial_partner_id
        active = self.sudo().search(
            [("state", "=", "active"), ("company_id", "=", invoice.company_id.id)]
        )
        named = active.filtered(
            lambda p: partner in p.customer_ids or invoice.customer_id in p.customer_ids
        )
        if named:
            return named[:1]
        unnamed = active.filtered(lambda p: not p.customer_ids)
        for segment in (_customer_segment(invoice.customer_id), "all"):
            hit = unnamed.filtered(lambda p, s=segment: p.segment == s)
            if hit:
                return hit[:1]
        return self.browse()


# ===========================================================================
# the dunning run reads the ladder, the promises and the plans
# ===========================================================================
class FixDunningCapture(models.Model):
    _inherit = "fix.dunning"

    suppression_reason = fields.Selection(
        selection_add=[("promise", "Promise to Pay")], ondelete={"promise": "set null"}
    )
    policy_id = fields.Many2one("fix.ar.dunning.policy", compute="_compute_policy", string="Ladder")
    channel = fields.Selection(LADDER_CHANNELS, compute="_compute_policy", string="Channel")
    tone = fields.Selection(TONES, compute="_compute_policy", string="Tone")

    STEP_LEVEL = {"reminder": "l1", "final": "l2", "escalate": "l3"}
    DEFAULT_CHANNEL = {
        "reminder": ("email", "friendly"),
        "final": ("whatsapp", "firm"),
        "escalate": ("call", "final"),
    }

    @api.depends("invoice_id", "step")
    def _compute_policy(self):
        Policy = self.env["fix.ar.dunning.policy"]
        for run in self:
            policy = Policy._fix_policy_for(run.invoice_id)
            run.policy_id = policy
            level = self.STEP_LEVEL.get(run.step, "l1")
            if policy:
                run.channel = policy["%s_channel" % level]
                run.tone = policy["%s_tone" % level]
            else:
                run.channel, run.tone = self.DEFAULT_CHANNEL.get(run.step, ("email", "friendly"))

    def _fix_ladder(self):
        self.ensure_one()
        policy = self.env["fix.ar.dunning.policy"]._fix_policy_for(self.invoice_id)
        if not policy:
            return super()._fix_ladder()
        return {"reminder": ("final", policy.l2_days), "final": ("escalate", policy.l3_days)}

    @api.model
    def _fix_first_offset(self, invoice):
        policy = self.env["fix.ar.dunning.policy"]._fix_policy_for(invoice)
        return max(policy.first_offset_days, 1) if policy else super()._fix_first_offset(invoice)

    @api.model
    def _fix_hold_new(self, invoice, today):
        return bool(self._fix_holding_arrangement(invoice, today)) or super()._fix_hold_new(
            invoice, today
        )

    @api.model
    def _fix_holding_arrangement(self, invoice, today):
        """An open promise not yet due, or a running payment plan, holds the
        dunning of this invoice (BRU-ARB-15, FR-ARB-035)."""
        promise = (
            self.env["fix.ar.promise"]
            .sudo()
            .search(
                [
                    ("invoice_id", "=", invoice.id),
                    ("state", "=", "open"),
                    ("promised_date", ">=", today),
                ],
                limit=1,
            )
        )
        if promise:
            return promise
        return (
            self.env["fix.ar.payment.plan"]
            .sudo()
            .search([("invoice_ids", "in", invoice.ids), ("state", "=", "active")], limit=1)
        )

    def _manual_suppression_active(self, today) -> bool:
        if super()._manual_suppression_active(today):
            return True
        return bool(
            self.suppressed
            and self.suppression_reason in ("promise", "payment_plan")
            and self._fix_holding_arrangement(self.invoice_id, today)
        )

    @api.model
    def action_run_dunning(self, as_of=None):
        result = super().action_run_dunning(as_of=as_of)
        escalated = self.search([("step", "=", "escalate"), ("suppressed", "=", False)])
        Case = self.env["fix.ar.collection.case"].sudo()
        opened = 0
        for run in escalated:
            invoice = run.invoice_id
            if invoice.state != "issued":
                continue
            _case, created = Case._fix_open_for(
                invoice.customer_id, invoice.company_id, "dunning_escalation", invoice
            )
            opened += int(created)
        result["cases_opened"] = opened
        return result

    def _fix_hold_for(self, invoices, reason, until, note, user):
        """Record the suppression an arrangement imposes (BRU-ARB-16: who,
        why, until when) on the invoices' existing runs."""
        runs = self.sudo().search([("invoice_id", "in", invoices.ids)])
        for run in runs:
            run._guarded().write(
                {
                    "suppressed": True,
                    "suppression_reason": reason,
                    "suppressed_by_id": user.id,
                    "suppressed_at": fields.Datetime.now(),
                    "suppressed_until": until or False,
                    "suppression_note": (note or "")[:250] or False,
                }
            )
            run.message_post(body="Dunning held (%s) until %s: %s" % (reason, until, note))

    def _fix_release_for(self, invoices, reason, note):
        runs = self.sudo().search(
            [("invoice_id", "in", invoices.ids), ("suppression_reason", "=", reason)]
        )
        for run in runs:
            run._guarded().write(
                {
                    "suppressed": False,
                    "suppression_reason": False,
                    "suppressed_until": False,
                    "suppression_note": (note or "")[:250] or False,
                }
            )
            run.message_post(body="Dunning resumed: %s" % note)


# ===========================================================================
# p8 — collection case (FR-ARB-034)
# ===========================================================================
class FixArCollectionCase(models.Model):
    _name = "fix.ar.collection.case"
    _description = "AR Collection Case (worklist item)"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "state, priority_score desc, id"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)
    name = fields.Char(default="New", readonly=True, copy=False, index=True)
    customer_id = fields.Many2one("res.partner", string="Customer", required=True, index=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    origin = fields.Selection(
        [
            ("manual", "Opened by a collector"),
            ("dunning_escalation", "Dunning escalated (L3)"),
            ("broken_promise", "Promise broken"),
            ("plan_default", "Payment plan defaulted"),
        ],
        default="manual",
        required=True,
    )
    assigned_to = fields.Many2one(
        "res.users", string="Collector", default=lambda self: self.env.user, tracking=True
    )
    state = fields.Selection(
        [("open", "Open"), ("in_progress", "Being worked"), ("closed", "Closed")],
        default="open",
        required=True,
        tracking=True,
    )
    total_overdue = fields.Monetary(currency_field="currency_id", readonly=True)
    oldest_age = fields.Integer(string="Oldest Overdue (days)", readonly=True)
    overdue_count = fields.Integer(string="Overdue Invoices", readonly=True)
    broken_promises = fields.Integer(readonly=True)
    priority_score = fields.Integer(
        readonly=True,
        help="Value (BDT thousands overdue) + oldest age in days + 50 per broken promise.",
    )
    next_action_at = fields.Date(string="Next Action On", tracking=True)
    last_contact_at = fields.Datetime(string="Last Contact", readonly=True)
    last_contact_note = fields.Char(readonly=True)
    note = fields.Text(string="Why the case is opened")
    outcome = fields.Selection(CASE_OUTCOMES, readonly=True, copy=False)
    outcome_note = fields.Char(readonly=True, copy=False)
    closed_by = fields.Many2one("res.users", readonly=True, copy=False)
    closed_at = fields.Datetime(readonly=True, copy=False)
    promise_ids = fields.One2many("fix.ar.promise", "case_id", string="Promises")

    MEASURED = (
        "total_overdue",
        "oldest_age",
        "overdue_count",
        "broken_promises",
        "priority_score",
    )

    def _fix_guarded_fields(self) -> set:
        return (
            super()._fix_guarded_fields()
            | set(self.MEASURED)
            | {
                "state",
                "outcome",
                "outcome_note",
                "closed_by",
                "closed_at",
                "last_contact_at",
                "last_contact_note",
                "origin",
                "name",
            }
        )

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= {"customer_id"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("customer_id"):
                raise UserError("A collection case is about one customer.")
            company = vals.get("company_id") or self.env.company.id
            if self.sudo().search_count(
                [
                    ("customer_id", "=", vals["customer_id"]),
                    ("company_id", "=", company),
                    ("state", "!=", "closed"),
                ]
            ):
                raise UserError("This customer already has an open collection case: work that one.")
        cases = super().create(vals_list)
        for case in cases:
            case._guarded().write({"name": _seq(self.env, "fix.ar.collection.case", "COL", case)})
        cases._fix_refresh()
        return cases

    def write(self, vals):
        if (not self._fix_guard_open() and self.filtered(lambda r: r.state == "closed")) and (
            set(vals) - {"message_follower_ids"}
        ):
            raise UserError("A closed collection case is evidence and is not edited.")
        return super().write(vals)

    def _fix_overdue_invoices(self):
        self.ensure_one()
        today = fields.Date.today()
        invoices = (
            self.env["fix.ar.invoice"]
            .sudo()
            .search(
                [
                    ("customer_id", "=", self.customer_id.id),
                    ("company_id", "=", self.company_id.id),
                    ("state", "=", "issued"),
                ]
            )
        )
        return invoices.filtered(
            lambda i: i.amount_residual > EPS
            and (today - i.invoice_date).days > i._payment_terms_days()
        )

    def _fix_refresh(self):
        today = fields.Date.today()
        for case in self:
            overdue = case._fix_overdue_invoices()
            total = sum(overdue.mapped("amount_residual"))
            oldest = max(
                [(today - i.invoice_date).days - i._payment_terms_days() for i in overdue] or [0]
            )
            broken = (
                self.env["fix.ar.promise"]
                .sudo()
                .search_count([("customer_id", "=", case.customer_id.id), ("state", "=", "broken")])
            )
            vals = {
                "total_overdue": round(total, 2),
                "oldest_age": oldest,
                "overdue_count": len(overdue),
                "broken_promises": broken,
                "priority_score": int(total / 1000.0) + oldest + 50 * broken,
            }
            if not case.operating_unit_id and overdue:
                vals["operating_unit_id"] = overdue[:1].operating_unit_id.id
            case._guarded().write(vals)

    def action_refresh(self):
        self._fix_refresh()

    @api.model
    def _fix_open_for(self, customer, company, origin, invoice=None):
        """The open case of a customer, or a new one. Returns (case, created)."""
        case = self.sudo().search(
            [
                ("customer_id", "=", customer.id),
                ("company_id", "=", company.id),
                ("state", "!=", "closed"),
            ],
            limit=1,
        )
        if case:
            case._fix_refresh()
            return case, False
        case = (
            self.sudo()
            ._guarded()
            .create(
                {
                    "customer_id": customer.id,
                    "company_id": company.id,
                    "operating_unit_id": invoice.operating_unit_id.id if invoice else False,
                    "origin": origin,
                    "assigned_to": False,
                    "note": "Opened automatically: %s"
                    % dict(self._fields["origin"].selection).get(origin, origin),
                }
            )
        )
        return case, True

    def action_log_contact(self, note="", next_action=""):
        """A contact with the customer: what was said and when to act next."""
        require_role(self.env, GROUP_ACCOUNTANT, "Logging a collection contact")
        if not (note or "").strip():
            raise UserError("Record what the customer said.")
        try:
            nxt = fields.Date.to_date(next_action) if next_action else False
        except ValueError:
            raise UserError("The next action date is written YYYY-MM-DD.") from None
        for case in self:
            if case.state == "closed":
                raise UserError("Case %s is closed." % case.name)
            vals = {
                "state": "in_progress",
                "last_contact_at": fields.Datetime.now(),
                "last_contact_note": note.strip()[:250],
            }
            case._guarded().write(vals)
            if nxt:
                case.write({"next_action_at": nxt})
            case.message_post(body="Contact logged by %s: %s" % (self.env.user.name, note))
            case._fix_refresh()

    def action_take(self):
        require_role(self.env, GROUP_ACCOUNTANT, "Taking a collection case")
        self.write({"assigned_to": self.env.uid})

    def action_close(self, note="", outcome=None):
        require_role(self.env, GROUP_ACCOUNTANT, "Closing a collection case")
        if outcome not in dict(CASE_OUTCOMES):
            raise UserError("A case closes with an outcome.")
        if not (note or "").strip():
            raise UserError("Record how the case ended.")
        for case in self:
            if case.state == "closed":
                continue
            case._fix_refresh()
            if outcome == "paid" and case.total_overdue > EPS:
                raise UserError(
                    "Case %s still has %.2f overdue: it is not paid in full."
                    % (case.name, case.total_overdue)
                )
            if outcome == "promise" and not case.promise_ids.filtered(lambda p: p.state == "open"):
                raise UserError("Record the promise on this case before closing it as a promise.")
            if outcome == "payment_plan" and not self.env[
                "fix.ar.payment.plan"
            ].sudo().search_count(
                [("customer_id", "=", case.customer_id.id), ("state", "=", "active")]
            ):
                raise UserError("No active payment plan for this customer.")
            case._guarded().write(
                {
                    "state": "closed",
                    "outcome": outcome,
                    "outcome_note": note.strip()[:250],
                    "closed_by": self.env.uid,
                    "closed_at": fields.Datetime.now(),
                }
            )

    def action_close_paid(self, note=""):
        return self.action_close(note, "paid")

    def action_close_promise(self, note=""):
        return self.action_close(note, "promise")

    def action_close_plan(self, note=""):
        return self.action_close(note, "payment_plan")

    def action_close_legal(self, note=""):
        return self.action_close(note, "legal")

    def action_close_uncollectible(self, note=""):
        return self.action_close(note, "uncollectible")

    def _cron_refresh(self):
        self.search([("state", "!=", "closed")])._fix_refresh()


# ===========================================================================
# p8 — promise to pay (FR-ARB-035)
# ===========================================================================
class FixArPromise(models.Model):
    _name = "fix.ar.promise"
    _description = "AR Promise to Pay"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "state, promised_date, id"

    company_id = fields.Many2one("res.company", required=True, index=True, readonly=True)
    operating_unit_id = fields.Many2one("operating.unit", index=True, readonly=True)
    name = fields.Char(default="New", readonly=True, copy=False, index=True)
    invoice_id = fields.Many2one(
        "fix.ar.invoice", string="Invoice", required=True, index=True, ondelete="restrict"
    )
    customer_id = fields.Many2one(
        related="invoice_id.customer_id", store=True, string="Customer", index=True
    )
    currency_id = fields.Many2one(related="invoice_id.currency_id")
    case_id = fields.Many2one("fix.ar.collection.case", string="Collection Case", index=True)
    amount = fields.Monetary(currency_field="currency_id", required=True)
    promised_date = fields.Date(required=True)
    made_by = fields.Char(string="Promised By (customer side)", required=True)
    contact_channel = fields.Selection(
        [
            ("call", "Phone call"),
            ("visit", "Visit"),
            ("email", "Email"),
            ("whatsapp", "WhatsApp"),
            ("portal", "Portal"),
        ],
        string="How it was made",
        default="call",
        required=True,
    )
    note = fields.Char()
    recorded_by = fields.Many2one("res.users", readonly=True, copy=False)
    residual_at_promise = fields.Monetary(currency_field="currency_id", readonly=True, copy=False)
    state = fields.Selection(
        [("open", "Open"), ("kept", "Kept"), ("broken", "Broken"), ("cancelled", "Cancelled")],
        default="open",
        required=True,
        tracking=True,
    )
    kept_at = fields.Datetime(readonly=True, copy=False)
    broken_at = fields.Datetime(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "kept_at",
            "broken_at",
            "recorded_by",
            "residual_at_promise",
            "company_id",
            "operating_unit_id",
            "name",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= {"invoice_id", "amount", "promised_date", "made_by"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, GROUP_ACCOUNTANT, "Recording a promise to pay")
        today = fields.Date.today()
        max_days = int(float_param(self.env, PARAM_PROMISE_MAX_DAYS, 30))
        for vals in vals_list:
            invoice = self.env["fix.ar.invoice"].browse(vals.get("invoice_id"))
            if invoice.state != "issued" or invoice.amount_residual <= EPS:
                raise UserError("A promise to pay is recorded against an open issued invoice.")
            amount = vals.get("amount") or 0.0
            if amount <= 0 or amount > invoice.amount_residual + EPS:
                raise UserError(
                    "The promised amount is positive and at most the open %.2f."
                    % invoice.amount_residual
                )
            when = fields.Date.to_date(vals.get("promised_date"))
            if not when or when < today:
                raise UserError("A promise is for today or a later date.")
            if (when - today).days > max_days:
                raise UserError(
                    "A promise beyond %s days is a payment plan, not a promise." % max_days
                )
            if self.sudo().search_count([("invoice_id", "=", invoice.id), ("state", "=", "open")]):
                raise UserError("Invoice %s already has an open promise." % invoice.name)
        model = _stamp_create(
            self,
            vals_list,
            lambda v: {
                "company_id": self.env["fix.ar.invoice"].browse(v["invoice_id"]).company_id.id,
                "operating_unit_id": self.env["fix.ar.invoice"]
                .browse(v["invoice_id"])
                .operating_unit_id.id,
                "recorded_by": self.env.uid,
                "residual_at_promise": self.env["fix.ar.invoice"]
                .browse(v["invoice_id"])
                .amount_residual,
            },
        )
        promises = super(FixArPromise, model).create(vals_list)
        for promise in promises:
            promise._guarded().write({"name": _seq(self.env, "fix.ar.promise", "PTP", promise)})
            self.env["fix.dunning"]._fix_hold_for(
                promise.invoice_id,
                "promise",
                promise.promised_date,
                "%s: %.2f promised by %s" % (promise.name, promise.amount, promise.made_by),
                self.env.user,
            )
        # the guard token stays inside create: the caller gets plain records
        return promises.with_env(self.env)

    def write(self, vals):
        if not self._fix_guard_open():
            locked = {"invoice_id", "amount", "promised_date", "made_by"} & set(vals)
            if locked and self:
                raise UserError(
                    "A recorded promise is not re-written: cancel it and record a new one."
                )
        return super().write(vals)

    def _fix_is_kept(self) -> bool:
        self.ensure_one()
        inv = self.invoice_id
        return (
            inv.state == "paid"
            or inv.amount_residual <= self.residual_at_promise - self.amount + EPS
        )

    def _cron_check_promises(self, as_of=None):
        """AUT-ARB-12: kept when the promised money arrived; broken once the
        date passes without it — dunning resumes and the case escalates."""
        today = as_of or fields.Date.today()
        kept = broken = 0
        for promise in self.sudo().search([("state", "=", "open")]):
            if promise._fix_is_kept():
                promise._guarded().write({"state": "kept", "kept_at": fields.Datetime.now()})
                self.env["fix.dunning"]._fix_release_for(
                    promise.invoice_id, "promise", "%s kept" % promise.name
                )
                kept += 1
            elif promise.promised_date < today:
                promise._guarded().write({"state": "broken", "broken_at": fields.Datetime.now()})
                self.env["fix.dunning"]._fix_release_for(
                    promise.invoice_id, "promise", "%s broken on %s" % (promise.name, today)
                )
                case, _created = self.env["fix.ar.collection.case"]._fix_open_for(
                    promise.customer_id, promise.company_id, "broken_promise", promise.invoice_id
                )
                if not promise.case_id:
                    promise._guarded().write({"case_id": case.id})
                case._fix_refresh()
                case.message_post(body="Promise %s broken: dunning resumed." % promise.name)
                broken += 1
        return {"kept": kept, "broken": broken}

    def action_cancel(self, reason=""):
        require_role(self.env, GROUP_ACCOUNTANT, "Cancelling a promise")
        if not (reason or "").strip():
            raise UserError("Say why the promise is cancelled.")
        for promise in self:
            if promise.state != "open":
                raise UserError("Only an open promise is cancelled.")
            promise._guarded().write({"state": "cancelled"})
            promise.message_post(body="Cancelled: %s" % reason)
            self.env["fix.dunning"]._fix_release_for(
                promise.invoice_id, "promise", "%s cancelled" % promise.name
            )


# ===========================================================================
# p8 — payment plan (FR-ARB-037)
# ===========================================================================
class FixArPaymentPlan(models.Model):
    _name = "fix.ar.payment.plan"
    _description = "AR Payment Plan"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "state, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", index=True)
    name = fields.Char(default="New", readonly=True, copy=False, index=True)
    customer_id = fields.Many2one("res.partner", string="Customer", required=True, index=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    invoice_ids = fields.Many2many(
        "fix.ar.invoice",
        "fix_ar_payment_plan_invoice_rel",
        "plan_id",
        "invoice_id",
        string="Invoices in the Plan",
    )
    line_ids = fields.One2many("fix.ar.payment.plan.line", "plan_id", string="Instalments")
    reason = fields.Char(string="Why a plan", required=True)
    total_amount = fields.Monetary(
        currency_field="currency_id",
        readonly=True,
        help="The open amount the plan settles, at agreement.",
    )
    scheduled_amount = fields.Monetary(
        currency_field="currency_id", compute="_compute_progress", string="Instalments Total"
    )
    paid_to_date = fields.Monetary(currency_field="currency_id", compute="_compute_progress")
    missed_count = fields.Integer(readonly=True, copy=False)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("completed", "Completed"),
            ("defaulted", "Defaulted"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    approved_by_id = fields.Many2one("res.users", string="Agreed By", readonly=True, copy=False)
    approved_at = fields.Datetime(string="Agreed On", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "total_amount",
            "missed_count",
            "approved_by_id",
            "approved_at",
            "name",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= {"customer_id", "invoice_ids", "line_ids", "reason"}
        return locked

    @api.depends("line_ids.amount", "invoice_ids.amount_residual", "total_amount")
    def _compute_progress(self):
        for plan in self:
            plan.scheduled_amount = sum(plan.line_ids.mapped("amount"))
            if plan.state in ("draft", "cancelled") or not plan.total_amount:
                plan.paid_to_date = 0.0
            else:
                open_now = sum(plan.invoice_ids.mapped("amount_residual"))
                plan.paid_to_date = max(round(plan.total_amount - open_now, 2), 0.0)

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, GROUP_ACCOUNTANT, "Proposing a payment plan")
        plans = super().create(vals_list)
        for plan in plans:
            plan._guarded().write({"name": _seq(self.env, "fix.ar.payment.plan", "PPL", plan)})
        return plans

    def write(self, vals):
        if not self._fix_guard_open():
            frozen = {"customer_id", "invoice_ids", "line_ids", "reason", "company_id"} & set(vals)
            if frozen and self.filtered(lambda r: r.state != "draft"):
                raise UserError("An agreed plan is not re-written: cancel it and agree a new one.")
        return super().write(vals)

    def action_activate(self):
        """Agreed by an Accountant other than the one who proposed it; the
        instalments add up to what is open on the plan's invoices."""
        require_role(self.env, GROUP_ACCOUNTANT, "Agreeing a payment plan")
        today = fields.Date.today()
        for plan in self:
            if plan.state != "draft":
                raise UserError("Only a draft plan is agreed.")
            if not self.env.su and plan.create_uid == self.env.user:
                raise UserError(
                    "Segregation of duties: you proposed plan %s; another Accountant agrees it."
                    % plan.name
                )
            invoices = plan.invoice_ids
            if not invoices:
                raise UserError("A plan settles at least one open invoice.")
            if invoices.filtered(
                lambda i, plan=plan: i.state != "issued"
                or i.amount_residual <= EPS
                or i.customer_id.commercial_partner_id != plan.customer_id.commercial_partner_id
                or i.company_id != plan.company_id
            ):
                raise UserError(
                    "Every invoice in the plan is an open issued invoice of this customer."
                )
            if not plan.line_ids:
                raise UserError("Schedule the instalments.")
            if plan.line_ids.filtered(lambda ln: ln.amount <= 0 or not ln.due_date):
                raise UserError("Every instalment has a positive amount and a due date.")
            if min(plan.line_ids.mapped("due_date")) < today:
                raise UserError("Instalments fall due today or later.")
            total = round(sum(invoices.mapped("amount_residual")), 2)
            scheduled = round(sum(plan.line_ids.mapped("amount")), 2)
            if abs(total - scheduled) > 0.01:
                raise UserError(
                    "The instalments add up to %.2f but %.2f is open on the plan's invoices."
                    % (scheduled, total)
                )
            clash = self.sudo().search(
                [
                    ("id", "!=", plan.id),
                    ("state", "=", "active"),
                    ("invoice_ids", "in", invoices.ids),
                ],
                limit=1,
            )
            if clash:
                raise UserError("Plan %s already covers one of these invoices." % clash.name)
            plan._guarded().write(
                {
                    "state": "active",
                    "total_amount": total,
                    "approved_by_id": self.env.uid,
                    "approved_at": fields.Datetime.now(),
                    "operating_unit_id": plan.operating_unit_id.id
                    or invoices[:1].operating_unit_id.id,
                }
            )
            self.env["fix.dunning"]._fix_hold_for(
                invoices,
                "payment_plan",
                max(plan.line_ids.mapped("due_date")),
                "%s agreed (%.2f in %s instalments)" % (plan.name, total, len(plan.line_ids)),
                self.env.user,
            )

    def action_cancel(self, reason=""):
        require_role(self.env, GROUP_ACCOUNTANT, "Cancelling a payment plan")
        if not (reason or "").strip():
            raise UserError("Say why the plan is cancelled.")
        for plan in self:
            if plan.state not in ("draft", "active"):
                raise UserError("Only a draft or active plan is cancelled.")
            was_active = plan.state == "active"
            plan._guarded().write({"state": "cancelled"})
            plan.message_post(body="Cancelled: %s" % reason)
            if was_active:
                self.env["fix.dunning"]._fix_release_for(
                    plan.invoice_ids, "payment_plan", "%s cancelled" % plan.name
                )

    def _fix_missed(self, today):
        """Instalments due before today that the money paid so far does not cover."""
        self.ensure_one()
        paid = self.paid_to_date
        cumulative = 0.0
        missed = 0
        for line in self.line_ids.sorted(lambda ln: (ln.due_date, ln.id)):
            cumulative += line.amount
            if line.due_date < today and paid + EPS < cumulative:
                missed += 1
        return missed

    def _cron_check_plans(self, as_of=None):
        """FR-ARB-037: a completed plan closes; a missed instalment (beyond
        the tolerated count, default none) defaults it, resumes dunning and
        escalates the customer's collection case."""
        today = as_of or fields.Date.today()
        tolerated = int(float_param(self.env, PARAM_PLAN_MAX_MISSED, 0))
        done = defaulted = 0
        for plan in self.sudo().search([("state", "=", "active")]):
            plan.invalidate_recordset(["paid_to_date"])
            if plan.paid_to_date >= plan.total_amount - EPS:
                plan._guarded().write({"state": "completed"})
                done += 1
                continue
            missed = plan._fix_missed(today)
            if missed != plan.missed_count:
                plan._guarded().write({"missed_count": missed})
            if missed > tolerated:
                plan._guarded().write({"state": "defaulted"})
                self.env["fix.dunning"]._fix_release_for(
                    plan.invoice_ids, "payment_plan", "%s defaulted on %s" % (plan.name, today)
                )
                case, _created = self.env["fix.ar.collection.case"]._fix_open_for(
                    plan.customer_id, plan.company_id, "plan_default", plan.invoice_ids[:1]
                )
                case.message_post(body="Payment plan %s defaulted." % plan.name)
                defaulted += 1
        return {"completed": done, "defaulted": defaulted}


class FixArPaymentPlanLine(models.Model):
    _name = "fix.ar.payment.plan.line"
    _description = "AR Payment Plan Instalment"
    _order = "plan_id, due_date, id"

    plan_id = fields.Many2one("fix.ar.payment.plan", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="plan_id.company_id", store=True, index=True)
    currency_id = fields.Many2one(related="plan_id.currency_id")
    due_date = fields.Date(required=True)
    amount = fields.Monetary(currency_field="currency_id", required=True)
    note = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            plan = self.env["fix.ar.payment.plan"].browse(vals.get("plan_id"))
            if plan.state != "draft" and not self.env.su:
                raise UserError("An agreed plan's instalments are not changed.")
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.su and self.filtered(lambda ln: ln.plan_id.state != "draft"):
            raise UserError("An agreed plan's instalments are not changed.")
        return super().write(vals)

    def unlink(self):
        if not self.env.su and self.filtered(lambda ln: ln.plan_id.state != "draft"):
            raise UserError("An agreed plan's instalments are not removed.")
        return super().unlink()


# ===========================================================================
# p4 — invoice delivery (FR-ARB-013/014)
# ===========================================================================
class FixArInvoiceDelivery(models.Model):
    _name = "fix.ar.invoice.delivery"
    _description = "AR Invoice Delivery"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    company_id = fields.Many2one("res.company", required=True, index=True, readonly=True)
    operating_unit_id = fields.Many2one("operating.unit", index=True, readonly=True)
    name = fields.Char(default="New", readonly=True, copy=False, index=True)
    invoice_id = fields.Many2one(
        "fix.ar.invoice", string="Invoice", required=True, index=True, ondelete="restrict"
    )
    customer_id = fields.Many2one(
        related="invoice_id.customer_id", store=True, string="Customer", index=True
    )
    channel = fields.Selection(CHANNELS, required=True, default="email")
    recipient = fields.Char(help="Email address, mobile number or portal login it goes to.")
    status = fields.Selection(
        [
            ("queued", "Queued"),
            ("sent", "Sent"),
            ("delivered", "Delivered"),
            ("opened", "Opened"),
            ("failed", "Failed"),
        ],
        default="queued",
        required=True,
        tracking=True,
    )
    sent_at = fields.Datetime(readonly=True, copy=False)
    delivered_at = fields.Datetime(readonly=True, copy=False)
    opened_at = fields.Datetime(readonly=True, copy=False)
    failure_reason = fields.Char(readonly=True, copy=False)
    retry_count = fields.Integer(readonly=True, copy=False)
    payment_link_id = fields.Many2one("fix.ar.payment.link", readonly=True, copy=False)

    _invoice_channel_unique = models.Constraint(
        "UNIQUE (invoice_id, channel)",
        "An invoice has one delivery record per channel: re-deliver it with Retry.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "status",
            "sent_at",
            "delivered_at",
            "opened_at",
            "failure_reason",
            "retry_count",
            "payment_link_id",
            "company_id",
            "operating_unit_id",
            "name",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= {"invoice_id", "channel"}
        return locked

    @staticmethod
    def _fix_check_recipient(channel, recipient):
        recipient = (recipient or "").strip()
        if channel == "email" and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", recipient):
            raise UserError("An email delivery goes to an email address.")
        if channel in ("whatsapp", "sms") and len(re.sub(r"\D", "", recipient)) < 10:
            raise UserError("A WhatsApp or SMS delivery goes to a mobile number.")
        return recipient

    @api.model_create_multi
    def create(self, vals_list):
        _require_billing(self.env, "Delivering an invoice")
        Link = self.env["fix.ar.payment.link"].sudo()
        for vals in vals_list:
            invoice = self.env["fix.ar.invoice"].browse(vals.get("invoice_id"))
            if invoice.state not in ("issued", "paid"):
                raise UserError("Only an issued invoice is delivered (a draft has no number).")
            channel = vals.get("channel") or "email"
            if self.sudo().search_count(
                [("invoice_id", "=", invoice.id), ("channel", "=", channel)]
            ):
                raise UserError(
                    "Invoice %s already has a %s delivery: re-deliver it with Retry (T-12)."
                    % (invoice.name, channel)
                )
            partner = invoice.customer_id
            if not vals.get("recipient"):
                vals["recipient"] = {
                    "email": partner.email,
                    "portal": partner.email,
                    "whatsapp": partner.phone,
                    "sms": partner.phone,
                }.get(channel) or ""
            vals["recipient"] = self._fix_check_recipient(channel, vals["recipient"])
        model = _stamp_create(
            self,
            vals_list,
            lambda v: {
                "company_id": self.env["fix.ar.invoice"].browse(v["invoice_id"]).company_id.id,
                "operating_unit_id": self.env["fix.ar.invoice"]
                .browse(v["invoice_id"])
                .operating_unit_id.id,
                # T-12: the invoice's existing link travels with every
                # delivery; delivering never mints a second one
                "payment_link_id": Link.search(
                    [("invoice_id", "=", v["invoice_id"]), ("state", "=", "new")], limit=1
                ).id,
            },
        )
        records = super(FixArInvoiceDelivery, model).create(vals_list)
        for rec in records:
            rec._guarded().write({"name": _seq(self.env, "fix.ar.invoice.delivery", "DLV", rec)})
        return records.with_env(self.env)

    def write(self, vals):
        if not self._fix_guard_open() and self and {"invoice_id", "channel"} & set(vals):
            raise UserError("A delivery's invoice and channel are fixed: record another channel.")
        if not self._fix_guard_open() and "recipient" in vals:
            for rec in self:
                vals["recipient"] = self._fix_check_recipient(rec.channel, vals["recipient"])
        return super().write(vals)

    def _fix_move(self, allowed_from, vals, what):
        _require_billing(self.env, what)
        for rec in self:
            if rec.status not in allowed_from:
                raise UserError(
                    "%s: delivery %s is %s."
                    % (what, rec.name, dict(self._fields["status"].selection)[rec.status])
                )
            rec._guarded().write(vals)

    def action_mark_sent(self):
        self._fix_move(
            ("queued",), {"status": "sent", "sent_at": fields.Datetime.now()}, "Marking sent"
        )

    def action_mark_delivered(self):
        self._fix_move(
            ("sent",),
            {"status": "delivered", "delivered_at": fields.Datetime.now()},
            "Confirming delivery",
        )

    def action_mark_opened(self):
        self._fix_move(
            ("sent", "delivered"),
            {"status": "opened", "opened_at": fields.Datetime.now()},
            "Recording it opened",
        )

    def action_mark_failed(self, reason=""):
        if not (reason or "").strip():
            raise UserError("Record why the delivery failed (bounced, wrong number…).")
        self._fix_move(
            ("queued", "sent"),
            {"status": "failed", "failure_reason": reason.strip()[:250]},
            "Recording a failure",
        )

    def action_retry(self):
        """AUT-ARB-02: retry on the same record; past the configured retries
        the channel is given up and another one is recorded instead."""
        limit = int(float_param(self.env, PARAM_DELIVERY_MAX_RETRIES, 3))
        for rec in self:
            if rec.status != "failed":
                raise UserError("Only a failed delivery is retried.")
            if rec.retry_count >= limit:
                raise UserError(
                    "Delivery %s failed %s times on %s: deliver on another channel."
                    % (rec.name, rec.retry_count + 1, rec.channel)
                )
            rec._fix_move(
                ("failed",),
                {
                    "status": "sent",
                    "sent_at": fields.Datetime.now(),
                    "retry_count": rec.retry_count + 1,
                    "failure_reason": False,
                },
                "Retrying a delivery",
            )


# ===========================================================================
# p4 — customer statement (FR-ARB-017)
# ===========================================================================
class FixArStatement(models.Model):
    _name = "fix.ar.statement"
    _description = "AR Customer Statement of Account"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    name = fields.Char(default="New", readonly=True, copy=False, index=True)
    customer_id = fields.Many2one("res.partner", string="Customer", required=True, index=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    period_from = fields.Date(required=True)
    period_to = fields.Date(required=True)
    opening_balance = fields.Monetary(currency_field="currency_id", readonly=True)
    total_charges = fields.Monetary(currency_field="currency_id", readonly=True)
    total_credits = fields.Monetary(currency_field="currency_id", readonly=True)
    closing_balance = fields.Monetary(currency_field="currency_id", readonly=True)
    line_count = fields.Integer(readonly=True)
    lines_text = fields.Text(string="Transactions", readonly=True)
    generated_at = fields.Datetime(readonly=True, copy=False)
    generated_by = fields.Many2one("res.users", readonly=True, copy=False)
    delivery_channel = fields.Selection(CHANNELS, readonly=True, copy=False)
    delivered_at = fields.Datetime(readonly=True, copy=False)
    state = fields.Selection(
        [("draft", "Draft"), ("generated", "Generated"), ("delivered", "Delivered")],
        default="draft",
        required=True,
        tracking=True,
    )

    FROZEN = (
        "opening_balance",
        "total_charges",
        "total_credits",
        "closing_balance",
        "line_count",
        "lines_text",
        "generated_at",
        "generated_by",
        "delivery_channel",
        "delivered_at",
        "state",
        "name",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | set(self.FROZEN)

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= {"customer_id", "period_from", "period_to", "company_id"}
        return locked

    @api.constrains("period_from", "period_to")
    def _check_period(self):
        for rec in self:
            if rec.period_from and rec.period_to and rec.period_from > rec.period_to:
                raise ValidationError("The period starts before it ends.")

    @api.model_create_multi
    def create(self, vals_list):
        _require_billing(self.env, "Requesting a statement")
        records = super().create(vals_list)
        for rec in records:
            rec._guarded().write({"name": _seq(self.env, "fix.ar.statement", "STM", rec)})
        return records

    def write(self, vals):
        if (not self._fix_guard_open() and self.filtered(lambda r: r.state != "draft")) and (
            {"customer_id", "period_from", "period_to", "company_id"} & set(vals)
        ):
            raise UserError("A generated statement is a snapshot: request a new one.")
        return super().write(vals)

    def action_generate(self):
        """The statement as the ledger stood: opening balance, every invoice,
        credit note and receipt in the period, closing balance. Frozen once
        generated, so what the customer received is reproducible."""
        _require_billing(self.env, "Generating a statement")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Statement %s is already generated." % rec.name)
            data = compute_customer_statement(
                self.env, rec.customer_id.id, rec.period_from, rec.period_to
            )
            rows = data.get("rows") or []
            charges = sum(r["charge"] for r in rows if r["charge"] > 0)
            credits = -sum(r["charge"] for r in rows if r["charge"] < 0)
            text = "\n".join(
                "%s  %-8s  %-18s  %-20s  %12.2f"
                % (
                    r["date"],
                    r["kind"],
                    (r.get("ref") or "")[:18],
                    (r.get("detail") or "")[:20],
                    r["charge"],
                )
                for r in rows
            )
            rec._guarded().write(
                {
                    "opening_balance": data["opening"],
                    "closing_balance": data["closing"],
                    "total_charges": round(charges, 2),
                    "total_credits": round(credits, 2),
                    "line_count": len(rows),
                    "lines_text": text or "No transaction in the period.",
                    "generated_at": fields.Datetime.now(),
                    "generated_by": self.env.uid,
                    "state": "generated",
                }
            )

    def action_mark_delivered(self, channel=""):
        _require_billing(self.env, "Recording a statement delivered")
        channel = (channel or "").strip().lower()
        if channel not in dict(CHANNELS):
            raise UserError("Deliver on one of: %s." % ", ".join(dict(CHANNELS)))
        for rec in self:
            if rec.state != "generated":
                raise UserError("Generate statement %s before delivering it." % rec.name)
            rec._guarded().write(
                {
                    "state": "delivered",
                    "delivery_channel": channel,
                    "delivered_at": fields.Datetime.now(),
                }
            )


# ===========================================================================
# p5 — deposits and retention (FR-ARB-028); receipts net them out
# ===========================================================================
class FixArDeposit(models.Model):
    _name = "fix.ar.deposit"
    _description = "AR Customer Deposit / Retention"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "state, release_due_at, id desc"

    company_id = fields.Many2one("res.company", required=True, index=True, readonly=True)
    operating_unit_id = fields.Many2one("operating.unit", index=True, readonly=True)
    name = fields.Char(default="New", readonly=True, copy=False, index=True)
    deposit_type = fields.Selection(
        [
            ("deposit", "Customer deposit"),
            ("retention", "Contract retention money"),
            ("advance", "Advance against a future invoice"),
        ],
        string="Type",
        required=True,
        default="deposit",
    )
    receipt_id = fields.Many2one(
        "fix.ar.receipt",
        string="Receipt Holding the Money",
        required=True,
        index=True,
        ondelete="restrict",
    )
    customer_id = fields.Many2one(
        related="receipt_id.customer_id", store=True, string="Customer", index=True
    )
    currency_id = fields.Many2one(related="receipt_id.currency_id")
    amount = fields.Monetary(currency_field="currency_id", required=True)
    contract_id = fields.Many2one("fix.contract", string="Contract", index=True)
    reference = fields.Char(string="Agreement Reference")
    received_at = fields.Date(related="receipt_id.receipt_date", string="Received On")
    release_due_at = fields.Date(string="Release / Apply By")
    state = fields.Selection(
        [
            ("held", "Held"),
            ("applied", "Applied to an invoice"),
            ("released", "Released (refund requested)"),
        ],
        default="held",
        required=True,
        tracking=True,
    )
    applied_to_invoice_id = fields.Many2one("fix.ar.invoice", readonly=True, copy=False)
    allocation_id = fields.Many2one("fix.ar.allocation", readonly=True, copy=False)
    applied_at = fields.Datetime(readonly=True, copy=False)
    refund_id = fields.Many2one("fix.ar.refund", readonly=True, copy=False)
    released_at = fields.Datetime(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "applied_to_invoice_id",
            "allocation_id",
            "applied_at",
            "refund_id",
            "released_at",
            "company_id",
            "operating_unit_id",
            "name",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= {"receipt_id", "amount", "deposit_type"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, GROUP_ACCOUNTANT, "Recording a deposit")
        for vals in vals_list:
            receipt = self.env["fix.ar.receipt"].browse(vals.get("receipt_id"))
            if receipt.state != "confirmed":
                raise UserError("A deposit is money already received: pick a confirmed receipt.")
            amount = vals.get("amount") or 0.0
            if amount <= 0 or amount > receipt.unapplied_amount + EPS:
                raise UserError(
                    "Receipt %s has %.2f unapplied: a deposit is positive and at most that."
                    % (receipt.name, receipt.unapplied_amount)
                )
        model = _stamp_create(
            self,
            vals_list,
            lambda v: {
                "company_id": self.env["fix.ar.receipt"].browse(v["receipt_id"]).company_id.id,
                "operating_unit_id": self.env["fix.ar.receipt"]
                .browse(v["receipt_id"])
                .operating_unit_id.id,
            },
        )
        records = super(FixArDeposit, model).create(vals_list)
        for rec in records:
            rec._guarded().write({"name": _seq(self.env, "fix.ar.deposit", "DEP", rec)})
        records.receipt_id._fix_check_net()
        return records.with_env(self.env)

    def write(self, vals):
        if (
            not self._fix_guard_open()
            and self
            and {"receipt_id", "amount", "deposit_type"} & set(vals)
        ):
            raise UserError("A recorded deposit is not re-written.")
        return super().write(vals)

    def action_apply(self, invoice=""):
        """Apply the held money to an invoice of the same customer (an advance
        against its final invoice, retention against the closing bill)."""
        require_role(self.env, GROUP_ACCOUNTANT, "Applying a deposit")
        ref = (invoice or "").strip()
        if not ref:
            raise UserError("Name the invoice (its number) the deposit is applied to.")
        for dep in self:
            if dep.state != "held":
                raise UserError("Only a held deposit is applied.")
            target = self.env["fix.ar.invoice"].search(
                [("name", "=", ref), ("company_id", "=", dep.company_id.id)], limit=1
            )
            if not target:
                raise UserError("No invoice numbered %s." % ref)
            amount = min(dep.amount, target.amount_residual)
            if amount <= EPS:
                raise UserError("Invoice %s has nothing open." % target.name)
            dep._guarded().write(
                {
                    "state": "applied",
                    "applied_to_invoice_id": target.id,
                    "applied_at": fields.Datetime.now(),
                }
            )
            dep.receipt_id.invalidate_recordset(["unapplied_amount", "allocated_amount"])
            allocation = self.env["fix.ar.allocation"].create(
                {"receipt_id": dep.receipt_id.id, "invoice_id": target.id, "amount": amount}
            )
            dep._guarded().write({"allocation_id": allocation.id})
            if amount < dep.amount - EPS:
                dep.message_post(
                    body="%.2f applied to %s; the remaining %.2f returns to the receipt as unapplied."
                    % (amount, target.name, dep.amount - amount)
                )

    def action_release(self, reason=""):
        """Return the held money: raises a refund for another person to authorise."""
        require_role(self.env, GROUP_ACCOUNTANT, "Releasing a deposit")
        if not (reason or "").strip():
            raise UserError("Say why the deposit is released.")
        for dep in self:
            if dep.state != "held":
                raise UserError("Only a held deposit is released.")
            dep._guarded().write({"state": "released", "released_at": fields.Datetime.now()})
            dep.receipt_id.invalidate_recordset(["unapplied_amount"])
            refund = (
                self.env["fix.ar.refund"]
                .with_context(fix_deposit_release=True)
                .create(
                    {
                        "receipt_id": dep.receipt_id.id,
                        "deposit_id": dep.id,
                        "amount": dep.amount,
                        "method": "bank_transfer",
                        "reason": reason.strip()[:250],
                    }
                )
            )
            dep._guarded().write({"refund_id": refund.id})


class FixArReceiptCapture(models.Model):
    _inherit = "fix.ar.receipt"

    deposit_ids = fields.One2many("fix.ar.deposit", "receipt_id", string="Deposits Held")
    refund_ids = fields.One2many("fix.ar.refund", "receipt_id", string="Refunds")
    deposit_held_amount = fields.Monetary(compute="_compute_allocation", store=True)
    refunded_amount = fields.Monetary(compute="_compute_allocation", store=True)

    @api.depends(
        "amount",
        "allocation_ids.amount",
        "state",
        "deposit_ids.amount",
        "deposit_ids.state",
        "refund_ids.amount",
        "refund_ids.state",
    )
    def _compute_allocation(self):
        """Unapplied = received - allocated - held as a deposit - refunded:
        a deposit is tracked apart from trade receivables (FR-ARB-028) and
        never escalates as unapplied; refunded money has left."""
        super()._compute_allocation()
        for rec in self:
            held = sum(rec.deposit_ids.filtered(lambda d: d.state == "held").mapped("amount"))
            refunded = sum(
                rec.refund_ids.filtered(lambda r: r.state not in ("rejected",)).mapped("amount")
            )
            rec.deposit_held_amount = held
            rec.refunded_amount = refunded
            if rec.state != "reversed":
                rec.unapplied_amount = rec.amount - rec.allocated_amount - held - refunded

    def _fix_check_net(self):
        for rec in self:
            rec.invalidate_recordset(["unapplied_amount"])
            if rec.unapplied_amount < -EPS:
                raise UserError(
                    "Receipt %s would be over-committed by %.2f (allocations, deposits and "
                    "refunds never exceed what was received)." % (rec.name, -rec.unapplied_amount)
                )


class FixArAllocationCapture(models.Model):
    _inherit = "fix.ar.allocation"

    @api.model
    def _fix_check_totals(self, receipts, invoices):
        super()._fix_check_totals(receipts, invoices)
        receipts._fix_check_net()


# ===========================================================================
# p9 — refund of on-account money (FR-ARB-040)
# ===========================================================================
class FixArRefund(models.Model):
    _name = "fix.ar.refund"
    _description = "AR Refund (on-account money)"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "id desc"

    company_id = fields.Many2one("res.company", required=True, index=True, readonly=True)
    operating_unit_id = fields.Many2one("operating.unit", index=True, readonly=True)
    name = fields.Char(default="New", readonly=True, copy=False, index=True)
    receipt_id = fields.Many2one(
        "fix.ar.receipt",
        string="Receipt Being Refunded",
        required=True,
        index=True,
        ondelete="restrict",
    )
    deposit_id = fields.Many2one("fix.ar.deposit", readonly=True, copy=False)
    customer_id = fields.Many2one(
        related="receipt_id.customer_id", store=True, string="Customer", index=True
    )
    currency_id = fields.Many2one(related="receipt_id.currency_id")
    amount = fields.Monetary(currency_field="currency_id", required=True)
    method = fields.Selection(REFUND_METHODS, required=True, default="bank_transfer")
    payee_account = fields.Char(string="Pay To (wallet / account no.)")
    reason = fields.Char(required=True)
    requested_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    authorised_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    authorised_at = fields.Datetime(readonly=True, copy=False)
    payment_instruction = fields.Char(string="M50 Instruction", readonly=True, copy=False)
    rejected_reason = fields.Char(readonly=True, copy=False)
    state = fields.Selection(
        [
            ("requested", "Requested"),
            ("authorised", "Authorised (with treasury)"),
            ("rejected", "Rejected"),
        ],
        default="requested",
        required=True,
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "requested_by_id",
            "authorised_by_id",
            "authorised_at",
            "payment_instruction",
            "rejected_reason",
            "deposit_id",
            "company_id",
            "operating_unit_id",
            "name",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= {"receipt_id", "amount", "method", "payee_account", "reason"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, GROUP_ACCOUNTANT, "Requesting a refund")
        cash_max = float_param(self.env, PARAM_REFUND_CASH_MAX, 10000.0)
        for vals in vals_list:
            receipt = self.env["fix.ar.receipt"].browse(vals.get("receipt_id"))
            if receipt.state != "confirmed":
                raise UserError("Only money from a confirmed receipt is refunded.")
            amount = vals.get("amount") or 0.0
            available = receipt.unapplied_amount
            deposit = self.env["fix.ar.deposit"].browse(vals.get("deposit_id"))
            if amount <= 0 or amount > available + EPS:
                raise UserError(
                    "Receipt %s has %.2f on account: a refund is positive and at most that. "
                    "Money allocated to an invoice is returned by a credit note."
                    % (receipt.name, available)
                )
            if vals.get("method") == "cash" and amount > cash_max + EPS:
                raise UserError(
                    "A cash refund above BDT %.2f is refused (BRU-ARB-11): refund to an account."
                    % cash_max
                )
            if deposit and deposit.receipt_id != receipt:
                raise UserError("The deposit belongs to another receipt.")
        if not self._fix_guard_open():
            guarded = self._fix_guarded_fields() - {"deposit_id"}
            for vals in vals_list:
                touched = [
                    k for k, v in vals.items() if k in guarded and v not in (False, None, "")
                ]
                if touched:
                    self._fix_guard_refuse(touched)
                if vals.get("deposit_id") and not self.env.context.get("fix_deposit_release"):
                    raise UserError("A deposit is refunded by releasing it.")
        stamped = []
        for vals in vals_list:
            receipt = self.env["fix.ar.receipt"].browse(vals["receipt_id"])
            stamped.append(
                dict(
                    vals,
                    company_id=receipt.company_id.id,
                    operating_unit_id=receipt.operating_unit_id.id,
                    requested_by_id=self.env.uid,
                )
            )
        model = self._guarded()
        records = super(FixArRefund, model).create(stamped)
        for rec in records:
            rec._guarded().write({"name": _seq(self.env, "fix.ar.refund", "RFD", rec)})
        records.receipt_id._fix_check_net()
        return records.with_env(self.env)

    def write(self, vals):
        if (not self._fix_guard_open() and self) and (
            {"receipt_id", "amount", "method", "payee_account", "reason"} & set(vals)
        ):
            raise UserError("A requested refund is not re-written: reject it and request again.")
        return super().write(vals)

    def action_authorise(self):
        """Authorised by someone other than the requester: an Accountant up to
        the direct band, the Accounting Administrator above it. Treasury (M50)
        executes it from a pending instruction (Dr receivable / Cr bank)."""
        require_role(self.env, GROUP_ACCOUNTANT, "Authorising a refund")
        direct_max = float_param(self.env, PARAM_REFUND_DIRECT_MAX, 10000.0)
        for rec in self:
            if rec.state != "requested":
                raise UserError("Refund %s is not awaiting authorisation." % rec.name)
            if not self.env.su and rec.requested_by_id == self.env.user:
                raise UserError(
                    "Segregation of duties: you requested refund %s; another person authorises it."
                    % rec.name
                )
            if rec.amount > direct_max + EPS:
                require_role(
                    self.env,
                    GROUP_ADMINISTRATOR,
                    "Authorising a refund above BDT %.2f" % direct_max,
                )
            if "fix.payment.execution" not in self.env:
                raise UserError("Refunds are executed by treasury (M50), which is not installed.")
            customer = rec.customer_id.commercial_partner_id.sudo()
            options = {
                "company_id": rec.company_id.id,
                "operating_unit_id": rec.operating_unit_id.id,
                "method": rec.method
                if rec.method in ("bank_transfer", "cheque", "cash")
                else "mobile_fs",
                "payee": customer.display_name,
            }
            ar = _ar_account(self.env, rec.company_id, "ar")
            if ar:
                options["debit_account_id"] = ar.id
            try:
                pay = self.env["fix.payment.execution"]._fix_request_payment(
                    "fix.ar.refund",
                    rec.id,
                    customer,
                    customer.bank_ids[:1],
                    rec.amount,
                    rec.currency_id,
                    "Refund %s of on-account money (receipt %s)" % (rec.name, rec.receipt_id.name),
                    self.env.user,
                    **options,
                )
            except TypeError:
                options.pop("method", None)
                pay = self.env["fix.payment.execution"]._fix_request_payment(
                    "fix.ar.refund",
                    rec.id,
                    customer,
                    customer.bank_ids[:1],
                    rec.amount,
                    rec.currency_id,
                    "Refund %s of on-account money (receipt %s)" % (rec.name, rec.receipt_id.name),
                    self.env.user,
                    **options,
                )
            rec._guarded().write(
                {
                    "state": "authorised",
                    "authorised_by_id": self.env.uid,
                    "authorised_at": fields.Datetime.now(),
                    "payment_instruction": pay.name,
                }
            )
            rec.message_post(body="Authorised; treasury instruction %s is pending." % pay.name)

    def action_reject(self, reason=""):
        require_role(self.env, GROUP_ACCOUNTANT, "Rejecting a refund")
        if not (reason or "").strip():
            raise UserError("Say why the refund is rejected.")
        for rec in self:
            if rec.state != "requested":
                raise UserError("Refund %s is not awaiting authorisation." % rec.name)
            rec._guarded().write({"state": "rejected", "rejected_reason": reason.strip()[:250]})
            if rec.deposit_id and rec.deposit_id.state == "released":
                rec.deposit_id._guarded().write({"state": "held", "released_at": False})
                rec.deposit_id.message_post(body="Release refused (%s): held again." % reason)


# ===========================================================================
# p10 — delivered but not invoiced (FR-ARB-043, BRU-ARB-24)
# ===========================================================================
class FixArUnbilledException(models.Model):
    _name = "fix.ar.unbilled.exception"
    _description = "AR Delivered-but-Unbilled Exception"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "state, age_days desc, id"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)
    name = fields.Char(default="New", readonly=True, copy=False, index=True)
    source_module = fields.Selection(UNBILLED_SOURCES, required=True, default="other")
    source_model = fields.Char(readonly=True, copy=False)
    source_id = fields.Integer(readonly=True, copy=False, index=True)
    source_ref = fields.Char(string="Source Document", required=True)
    customer_id = fields.Many2one("res.partner", string="Customer", required=True, index=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    delivered_at = fields.Date(string="Delivered On", required=True)
    estimated_value = fields.Monetary(currency_field="currency_id")
    age_days = fields.Integer(readonly=True, copy=False)
    detected_by = fields.Selection(
        [("reconciliation", "Daily reconciliation"), ("manual", "Reported by hand")],
        default="manual",
        readonly=True,
        copy=False,
    )
    reported_by = fields.Many2one("res.users", readonly=True, copy=False)
    escalated_to = fields.Selection(
        [
            ("branch_manager", "Branch Manager"),
            ("finance_manager", "Finance Manager"),
            ("cfo", "CFO"),
        ],
        readonly=True,
        copy=False,
    )
    escalated_at = fields.Datetime(readonly=True, copy=False)
    state = fields.Selection(
        [("open", "Open"), ("escalated", "Escalated"), ("resolved", "Resolved")],
        default="open",
        required=True,
        tracking=True,
    )
    resolution = fields.Selection(UNBILLED_RESOLUTIONS, readonly=True, copy=False)
    resolution_note = fields.Char(readonly=True, copy=False)
    invoice_id = fields.Many2one("fix.ar.invoice", readonly=True, copy=False)
    resolved_by = fields.Many2one("res.users", readonly=True, copy=False)
    resolved_at = fields.Datetime(readonly=True, copy=False)
    note = fields.Text()

    _source_unique = models.Constraint(
        "UNIQUE (source_model, source_id, company_id)",
        "This delivered item already has an exception.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "resolution",
            "resolution_note",
            "invoice_id",
            "resolved_by",
            "resolved_at",
            "escalated_to",
            "escalated_at",
            "age_days",
            "detected_by",
            "reported_by",
            "source_model",
            "source_id",
            "name",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state == "resolved" or r.detected_by == "reconciliation" for r in self):
            locked |= {
                "source_module",
                "source_ref",
                "customer_id",
                "delivered_at",
                "estimated_value",
            }
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            _require_billing(self.env, "Reporting unbilled work")
        today = fields.Date.today()
        for vals in vals_list:
            when = fields.Date.to_date(vals.get("delivered_at"))
            if when and when > today:
                raise UserError("Work is reported unbilled once delivered, not before.")
            if (vals.get("estimated_value") or 0.0) < 0:
                raise UserError("The estimated value is not negative.")
        model = _stamp_create(
            self,
            vals_list,
            lambda v: {} if self.env.su else {"reported_by": self.env.uid, "detected_by": "manual"},
        )
        records = super(FixArUnbilledException, model).create(vals_list)
        for rec in records:
            rec._guarded().write({"name": _seq(self.env, "fix.ar.unbilled.exception", "UBX", rec)})
        records._fix_age()
        return records.with_env(self.env)

    def write(self, vals):
        if (not self._fix_guard_open() and self.filtered(lambda r: r.state == "resolved")) and (
            set(vals) - {"note", "message_follower_ids"}
        ):
            raise UserError("A resolved exception is evidence and is not edited.")
        return super().write(vals)

    def _fix_thresholds(self):
        raw = self.env["ir.config_parameter"].sudo().get_param(PARAM_UNBILLED_DAYS) or "1,3,7"
        try:
            days = [int(x) for x in str(raw).split(",")][:3]
        except ValueError:
            days = [1, 3, 7]
        while len(days) < 3:
            days.append(days[-1] if days else 7)
        return days

    def _fix_age(self):
        """BRU-ARB-24 / AUT-ARB-18: escalation by age, unconditionally —
        branch manager, then Finance Manager, then CFO."""
        today = fields.Date.today()
        bm, fm, cfo = self._fix_thresholds()
        for rec in self.filtered(lambda r: r.state != "resolved"):
            age = (today - rec.delivered_at).days if rec.delivered_at else 0
            level = (
                "cfo"
                if age >= cfo
                else "finance_manager"
                if age >= fm
                else "branch_manager"
                if age >= bm
                else False
            )
            vals = {"age_days": age}
            raised = bool(level) and level != rec.escalated_to
            if raised:
                vals.update(
                    {
                        "escalated_to": level,
                        "escalated_at": fields.Datetime.now(),
                        "state": "escalated",
                    }
                )
            rec._guarded().write(vals)
            if raised:
                rec.message_post(body="Unbilled for %s days: escalated to %s." % (age, level))

    @api.model
    def _fix_invoice_for_exception(self, rec):
        """The invoice that bills this exception's source, across the
        streams the reconciliation now covers (A08 M20-F4)."""
        Invoice = self.env["fix.ar.invoice"].sudo()
        if rec.source_model == "fix.contract":
            periods = (
                self.env["fix.contract.billing.period"]
                .sudo()
                .search([("contract_id", "=", rec.source_id)])
            )
            if periods:
                return Invoice.search(
                    [
                        ("source_model", "=", periods._name),
                        ("source_id", "in", periods.ids),
                        ("state", "!=", "cancelled"),
                    ],
                    limit=1,
                )
            return Invoice
        if rec.source_model == "fix.subscription":
            charges = (
                self.env["fix.subscription.charge"]
                .sudo()
                .search([("subscription_id", "=", rec.source_id)])
            )
            if charges:
                return Invoice.search(
                    [
                        ("source_model", "=", charges._name),
                        ("source_id", "in", charges.ids),
                        ("state", "!=", "cancelled"),
                    ],
                    limit=1,
                )
            return Invoice
        if rec.source_model == "fix.warranty.claim":
            claim = self.env["fix.warranty.claim"].sudo().browse(rec.source_id).exists()
            if not claim:
                return Invoice
            invoices = self.env["fix.a04.claim.consumers"].sudo()._claim_invoices(claim)
            return invoices[:1]
        return Invoice.search(
            [
                ("source_model", "=", rec.source_model),
                ("source_id", "=", rec.source_id),
                ("state", "!=", "cancelled"),
            ],
            limit=1,
        )

    @api.model
    def _fix_raise_stream_exceptions(self, data):
        """Create the delivered-but-unbilled exceptions for the new streams:
        one per contract / subscription / claim still unbilled (the unique
        (source_model, source_id, company_id) key makes a re-run a no-op)."""
        created = 0
        for row in data.get("unbilled_periods") or []:
            company = self.env["res.company"].browse(row["company_id"])
            if self.sudo().search_count(
                [
                    ("source_model", "=", row["source_model"]),
                    ("source_id", "=", row["source_id"]),
                    ("company_id", "=", company.id),
                ]
            ):
                continue
            self.sudo()._guarded().create(
                {
                    "company_id": company.id,
                    "operating_unit_id": row["operating_unit_id"],
                    "source_module": "contract"
                    if row["stream"] == "contract_period"
                    else "subscription",
                    "source_model": row["source_model"],
                    "source_id": row["source_id"],
                    "source_ref": "%s (%s to %s)"
                    % (row["reference"], row["period_start"], row["period_end"]),
                    "customer_id": row["customer_id"] or False,
                    "delivered_at": fields.Date.to_date(row["period_start"]) or fields.Date.today(),
                    "estimated_value": row["amount"],
                    "detected_by": "reconciliation",
                }
            )
            created += 1
        for row in data.get("unbilled_claims") or []:
            if not row["customer_id"]:
                continue  # a brand with no billing partner: nothing to bill yet
            company = self.env["res.company"].browse(row["company_id"])
            if self.sudo().search_count(
                [
                    ("source_model", "=", "fix.warranty.claim"),
                    ("source_id", "=", row["claim_id"]),
                    ("company_id", "=", company.id),
                ]
            ):
                continue
            self.sudo()._guarded().create(
                {
                    "company_id": company.id,
                    "operating_unit_id": row["operating_unit_id"],
                    "source_module": "warranty_claim",
                    "source_model": "fix.warranty.claim",
                    "source_id": row["claim_id"],
                    "source_ref": row["claim"],
                    "customer_id": row["customer_id"],
                    "delivered_at": fields.Date.to_date(row["decided_on"]) or fields.Date.today(),
                    "estimated_value": row["amount"],
                    "detected_by": "reconciliation",
                }
            )
            created += 1
        return created

    @api.model
    def _cron_reconcile(self):
        """AUT-ARB-17: delivered-but-unbilled work becomes an exception —
        closed service orders, due subscription/contract periods and
        recoverable claims (A08 M20-F4); an exception whose source got
        invoiced resolves itself; every open one ages and escalates."""
        data = compute_leakage(self.env)
        Order = self.env["fix.service.order"].sudo()
        created = 0
        for row in data.get("unbilled_closed_orders") or []:
            order = Order.browse(row["order_id"])
            company = order.company_id or self.env.company
            if self.sudo().search_count(
                [
                    ("source_model", "=", "fix.service.order"),
                    ("source_id", "=", order.id),
                    ("company_id", "=", company.id),
                ]
            ):
                continue
            marker = getattr(order, "closed_date", None) or order.write_date
            delivered = marker.date() if hasattr(marker, "date") else marker
            self.sudo()._guarded().create(
                {
                    "company_id": company.id,
                    "operating_unit_id": order.operating_unit_id.id,
                    "source_module": "service_order",
                    "source_model": "fix.service.order",
                    "source_id": order.id,
                    "source_ref": order.name,
                    "customer_id": order.customer_id.id,
                    "delivered_at": delivered or fields.Date.today(),
                    "detected_by": "reconciliation",
                }
            )
            created += 1
        created += self._fix_raise_stream_exceptions(data)
        # A contract/subscription/claim exception only resolves when the
        # stream's own scan no longer calls it unbilled (a partly billed
        # contract has an invoice but an unbilled period too).
        still_unbilled = {
            (row["source_model"], row["source_id"]) for row in (data.get("unbilled_periods") or [])
        } | {("fix.warranty.claim", row["claim_id"]) for row in (data.get("unbilled_claims") or [])}
        auto = 0
        for rec in self.sudo().search(
            [("state", "!=", "resolved"), ("source_model", "!=", False), ("source_id", "!=", 0)]
        ):
            if (rec.source_model, rec.source_id) in still_unbilled:
                continue
            hit = self._fix_invoice_for_exception(rec)
            if hit:
                rec._guarded().write(
                    {
                        "state": "resolved",
                        "resolution": "invoiced",
                        "invoice_id": hit.id,
                        "resolution_note": "Invoice %s found by the daily reconciliation"
                        % hit.name,
                        "resolved_at": fields.Datetime.now(),
                    }
                )
                auto += 1
        self.sudo().search([("state", "!=", "resolved")])._fix_age()
        return {"created": created, "auto_resolved": auto}

    def _fix_resolve(self, resolution, note, invoice=None):
        if not (note or "").strip():
            raise UserError("Record how the exception was resolved.")
        for rec in self:
            if rec.state == "resolved":
                raise UserError("%s is already resolved." % rec.name)
            rec._guarded().write(
                {
                    "state": "resolved",
                    "resolution": resolution,
                    "resolution_note": note.strip()[:250],
                    "invoice_id": invoice.id if invoice else False,
                    "resolved_by": self.env.uid,
                    "resolved_at": fields.Datetime.now(),
                }
            )

    def action_resolve_invoiced(self, invoice=""):
        """Resolved by the invoice that now bills it (its number)."""
        _require_billing(self.env, "Resolving an unbilled exception")
        ref = (invoice or "").strip()
        target = self.env["fix.ar.invoice"].search([("name", "=", ref)], limit=1) if ref else None
        if not target or target.state not in ("issued", "paid"):
            raise UserError("Name the ISSUED invoice that bills this work (its number).")
        for rec in self:
            if target.customer_id.commercial_partner_id != rec.customer_id.commercial_partner_id:
                raise UserError("Invoice %s is another customer's." % target.name)
        self._fix_resolve("invoiced", "Billed on %s" % target.name, target)

    def action_resolve_not_billable(self, note=""):
        """BRU-ARB-01: an explicitly approved suppression — an Accounting
        Administrator who did not report it."""
        require_role(self.env, GROUP_ADMINISTRATOR, "Approving work as not billable")
        for rec in self:
            if not self.env.su and rec.reported_by == self.env.user:
                raise UserError(
                    "Segregation of duties: you reported %s; another person approves it as not "
                    "billable." % rec.name
                )
        self._fix_resolve("not_billable", note)

    def action_resolve_duplicate(self, note=""):
        _require_billing(self.env, "Resolving an unbilled exception")
        self._fix_resolve("duplicate", note)
