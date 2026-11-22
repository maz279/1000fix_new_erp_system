# M20 dunning REMINDER DISPATCH (A08 M20-F5/F6 fix).
#
# The A08 audit found the ladder advanced, escalated and opened collection
# cases correctly but never sent a single reminder: no channel call, no M27
# handoff, no per-reminder evidence. This file closes that half of
# FR-ARB-032 / AUT-ARB-10 ("execute them automatically ... send the reminder
# on the level's channel ... log a suppressed or failed action"):
#
#   * fix.ar.dunning.action — the spec's per-reminder delivery evidence
#     entity (§10.1). One row per ladder step and channel; it records the
#     rendered subject/body, the amount and days overdue it stated, the
#     masked recipient, the transport reference and the outcome. It is
#     evidence: once it has reached a delivery state it is neither edited
#     nor deleted.
#   * Dispatch — the run's state transition (first reminder, or an advance
#     to the next level) renders the level's template and sends it through
#     the estate's ONE outbound exit, M27's fix.notif.delivery.queue()
#     (consent, BTRC curfew, DND, provider and cost all apply there). The
#     module is read through the registry: cd_contact_centre is a different
#     owner's module (M27) and a hard dependency is not needed to call a
#     service that the whole estate already calls this way.
#   * Retry — a failed send is retried by a cron or by a person, on the SAME
#     evidence row. A reminder that was sent is never sent again: the row's
#     state is the idempotency guard, backed by a unique (run, step,
#     channel) constraint.
#   * Call steps — a ladder level whose channel is a phone call raises the
#     M27 contact-centre handoff (routed through fix.routing.workstream when
#     a collections workstream is configured) and a local
#     fix.ar.dunning.handoff queue row with the explicit `m27_follow_up`
#     state. It never fabricates a "message" for a telephone call.
#
# Suppression is re-checked at send time, not only when the ladder advanced:
# a dispute, promise, payment plan or a payment that landed between the two
# is still honoured (BRU-ARB-15/16, FR-ARB-033/036).
from __future__ import annotations

import logging
import re

from odoo import api, fields, models
from odoo.exceptions import UserError

# Load order: the policy and the channel/tone computes live in fix_ar_capture,
# which itself imports fix_billing_engine (where fix.dunning is defined).
from . import fix_ar_capture  # noqa: F401 - load order
from .fix_ar_capture import LADDER_CHANNELS, TONES
from .fix_finance_approval import GROUP_ACCOUNTANT, require_role

_logger = logging.getLogger(__name__)

# The dunning steps and their level keys, as fix_ar_capture reads them from
# the policy (l1/l2/l3 channel/tone).
LEVEL_OF_STEP = {"reminder": "l1", "final": "l2", "escalate": "l3"}
STEP_OF_LEVEL = {v: k for k, v in LEVEL_OF_STEP.items()}

PARAM_DUNNING_RETRY_MAX = "cd_billing_engine.dunning_retry_max"
DEFAULT_DUNNING_RETRY_MAX = 3

# The ladder's templates are text, not template records: fix.ar.dunning.policy
# carries channel and tone per level, never a template id. The text below is
# the contract those tones render; it is interpolated with the invoice no,
# the amount due and the days overdue, and stamped on the evidence row with
# the ladder level, tone and version so a later wording change is visible.
DUNNING_TEMPLATES = {
    "friendly": {
        "subject": "Payment reminder — invoice {invoice} (1000 FiX Services)",
        "body": (
            "প্রিয় {customer}, ইনভয়েস {invoice} এর {amount} টাকা {days} দিন বকেয়া আছে। "
            "অনুগ্রহ করে দ্রুত পরিশোধ করুন অথবা 16743 নম্বরে কল করুন।\n"
            "Dear {customer}, invoice {invoice} for {amount} is {days} days overdue. "
            "Please pay at your earliest convenience or call 16743.\n"
            "1000 FiX Services Ltd."
        ),
    },
    "firm": {
        "subject": "Final reminder — invoice {invoice} (1000 FiX Services)",
        "body": (
            "প্রিয় {customer}, ইনভয়েস {invoice} এর {amount} টাকা {days} দিন বকেয়া। "
            "এটি চূড়ান্ত স্মারক; ৭ দিনের মধ্যে পরিশোধ না হলে হিসাব কালেকশন বিভাগে যাবে। "
            "হটলাইন 16743।\n"
            "Dear {customer}, this is a FINAL REMINDER: invoice {invoice} for {amount} is "
            "{days} days overdue. If it is not paid within 7 days the account will be "
            "escalated to collections. Hotline 16743.\n"
            "1000 FiX Services Ltd."
        ),
    },
    "final": {
        "subject": "Final notice — invoice {invoice} referred to collections",
        "body": (
            "প্রিয় {customer}, ইনভয়েস {invoice} এর {amount} টাকা {days} দিন বকেয়া এবং "
            "আপনার হিসাব কালেকশন বিভাগে হস্তান্তর করা হয়েছে। অনুগ্রহ করে 16743 নম্বরে "
            "যোগাযোগ করুন।\n"
            "Dear {customer}, invoice {invoice} for {amount} is {days} days overdue and "
            "has been escalated to our collections team. Please contact us on 16743.\n"
            "1000 FiX Services Ltd."
        ),
    },
}

# The ladder channels that M27's notification service can actually carry.
MESSAGE_CHANNELS = frozenset({"email", "sms", "whatsapp"})
# Channels with no outbound message: the portal presents the reminder; print
# is handed to the branch. Both are recorded, never claimed as sent.
MANUAL_CHANNELS = frozenset({"portal", "print"})
CALL_CHANNEL = "call"


def _mask(channel: str, address: str) -> str:
    """The recipient as the evidence may keep it: enough to recognise, never
    enough to reconstruct (a dunning notice names a debt)."""
    raw = (address or "").strip()
    if not raw:
        return ""
    if channel == "email" and "@" in raw:
        local, _, domain = raw.partition("@")
        return "%s***@%s" % (local[:1], domain)
    digits = re.sub(r"\D", "", raw)
    if len(digits) < 4:
        return "***"
    return "***%s" % digits[-4:]


def _money(value) -> str:
    return f"{float(value or 0.0):,.2f}"


def _address_for(partner, channel: str) -> str:
    """The customer's destination for a ladder channel, or ''."""
    if not partner:
        return ""
    if channel == "email":
        return partner.email or ""
    if channel in ("sms", "whatsapp", CALL_CHANNEL):
        return getattr(partner, "mobile", False) or partner.phone or ""
    return ""


class FixArDunningAction(models.Model):
    """One executed reminder — the spec's delivery evidence entity.

    Created BEFORE the send, so a crash mid-attempt still leaves evidence.
    The row is the ladder's audit trail: which level, on which channel, to
    which (masked) recipient, what it said, and what the transport answered.
    """

    _name = "fix.ar.dunning.action"
    _description = "Dunning Reminder (delivery evidence)"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "create_date desc, id desc"
    _rec_name = "name"

    # A08 M20-F5: idempotent per step+invoice+channel. The retry acts on this
    # row; it never creates a second one for a step that already has evidence.
    _step_unique = models.Constraint(
        "UNIQUE (dunning_id, step, channel)",
        "One reminder per dunning step and channel — the retry reuses its evidence row.",
    )

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", index=True)
    dunning_id = fields.Many2one(
        "fix.dunning", string="Dunning Run", required=True, ondelete="restrict", index=True
    )
    invoice_id = fields.Many2one(
        "fix.ar.invoice", string="Invoice", required=True, ondelete="restrict", index=True
    )
    customer_id = fields.Many2one(
        "res.partner", string="Customer", required=True, ondelete="restrict", index=True
    )
    policy_id = fields.Many2one(
        "fix.ar.dunning.policy", string="Ladder", ondelete="set null", index=True
    )
    name = fields.Char(compute="_compute_name", store=True, string="Reminder")
    currency_id = fields.Many2one(related="invoice_id.currency_id", string="Currency")
    level = fields.Selection(
        [("l1", "L1 Reminder"), ("l2", "L2 Final Notice"), ("l3", "L3 Escalation")],
        required=True,
        index=True,
    )
    step = fields.Selection(
        [
            ("reminder", "Reminder"),
            ("final", "Final Notice"),
            ("escalate", "Escalated to Collections"),
        ],
        required=True,
        index=True,
    )
    channel = fields.Selection(LADDER_CHANNELS, required=True, index=True)
    tone = fields.Selection(TONES, string="Tone")
    amount = fields.Monetary(
        string="Amount Due", currency_field="currency_id", help="The dunnable amount stated."
    )
    days_overdue = fields.Integer(string="Days Overdue")
    due_date = fields.Date(string="Due Date")
    recipient_masked = fields.Char(
        string="Recipient (masked)",
        readonly=True,
        help="MSISDN/e-mail with all but the last four digits or the domain removed.",
    )
    template_name = fields.Char(string="Rendered Template", readonly=True)
    subject = fields.Char(readonly=True)
    body = fields.Text(help="The rendered message as attempted.", readonly=True)
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("sent", "Sent to provider"),
            ("failed", "Failed"),
            ("suppressed", "Suppressed (not sent)"),
            ("handoff", "Handed off to M27"),
            ("manual", "Manual channel (portal / print)"),
        ],
        default="pending",
        required=True,
        tracking=True,
        index=True,
    )
    sent_at = fields.Datetime(readonly=True)
    provider_ref = fields.Char(string="Provider Message Id", readonly=True, index=True)
    notif_delivery_ref = fields.Char(
        string="Delivery Log Reference",
        readonly=True,
        help="fix.notif.delivery:<id> — the M27 row this reminder left through.",
    )
    handoff_id = fields.Many2one(
        "fix.ar.dunning.handoff", string="M27 Handoff", readonly=True, ondelete="restrict"
    )
    failure_reason = fields.Text(readonly=True)
    retry_count = fields.Integer(readonly=True, default=0, copy=False)
    note = fields.Text(readonly=True)

    # What makes a reminder what it is. Once the row has reached a terminal
    # state none of it may change — it is what the customer was told.
    _FROZEN_FIELDS = frozenset(
        {
            "dunning_id",
            "invoice_id",
            "customer_id",
            "policy_id",
            "level",
            "step",
            "channel",
            "tone",
            "amount",
            "days_overdue",
            "due_date",
            "recipient_masked",
            "template_name",
            "subject",
            "body",
            "company_id",
            "operating_unit_id",
        }
    )
    TERMINAL_STATES = ("sent", "handoff", "manual", "suppressed")

    def _fix_guarded_fields(self) -> set:
        return (
            super()._fix_guarded_fields()
            | self._FROZEN_FIELDS
            | {
                "state",
                "sent_at",
                "provider_ref",
                "notif_delivery_ref",
                "handoff_id",
                "failure_reason",
                "retry_count",
                "note",
            }
        )

    @api.depends("invoice_id.name", "step", "channel")
    def _compute_name(self):
        for rec in self:
            rec.name = "%s / %s / %s" % (
                rec.invoice_id.name or "Invoice #%s" % rec.invoice_id.id,
                rec.step,
                rec.channel,
            )

    def write(self, vals):
        # FR-ARB-032 / AUT-ARB-10: the delivery evidence is immutable once it
        # has reached a delivery state. State transitions still write through
        # _guarded(), but they never touch the frozen identity/content fields.
        touched = self._FROZEN_FIELDS & set(vals)
        if touched:
            for rec in self:
                if rec.state in self.TERMINAL_STATES:
                    raise UserError(
                        "Dunning reminder %s is evidence of what was sent (%s): %s "
                        "cannot be changed afterwards. Raise the next ladder step "
                        "instead (FR-ARB-032 / AUT-ARB-10)."
                        % (
                            rec.name or rec.id,
                            dict(rec._fields["state"].selection).get(rec.state, rec.state),
                            ", ".join(sorted(touched)),
                        )
                    )
        return super().write(vals)

    def unlink(self):
        # The estate refuses deletion of delivery evidence. A reminder that
        # went out (or was suppressed, or failed) is the proof that the rule
        # ran; deleting it is how a reminder disappears without a trace.
        raise UserError(
            "A dunning reminder is delivery evidence and cannot be deleted "
            "(FR-ARB-032 / AUT-ARB-10). Cancel or supersede the ladder instead."
        )

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------
    @api.model
    def _fix_render(self, run, as_of=None):
        """The values of the reminder for the run's CURRENT step."""
        invoice = run.invoice_id
        partner = invoice.customer_id
        today = fields.Date.to_date(as_of or fields.Date.today())
        terms = invoice._payment_terms_days()
        days = max((today - invoice.invoice_date).days - terms, 0)
        tone = run.tone or "friendly"
        # The level's TONE is the content contract (the ladder configures a
        # tone per level, not a template id); the step names the evidence.
        template = DUNNING_TEMPLATES.get(tone) or DUNNING_TEMPLATES["friendly"]
        values = {
            "customer": partner.name or "",
            "invoice": invoice.name or "",
            "amount": _money(run.overdue_amount or invoice.amount_residual),
            "days": days,
        }
        return {
            "company_id": invoice.company_id.id,
            "operating_unit_id": invoice.operating_unit_id.id,
            "dunning_id": run.id,
            "invoice_id": invoice.id,
            "customer_id": partner.id,
            "policy_id": run.policy_id.id or False,
            "level": LEVEL_OF_STEP.get(run.step, "l1"),
            "step": run.step,
            "tone": tone,
            "channel": run.channel,
            "amount": run.overdue_amount or invoice.amount_residual,
            "days_overdue": days,
            "due_date": fields.Date.add(invoice.invoice_date, days=terms),
            "template_name": "ar_dunning.%s.%s.v1" % (run.step, tone),
            "subject": template["subject"].format(**values),
            "body": template["body"].format(**values),
            "recipient_masked": _mask(run.channel, _address_for(partner, run.channel)),
            "state": "pending",
        }

    @api.model
    def _fix_create_for(self, run, as_of=None):
        values = self._fix_render(run, as_of=as_of)
        return self.sudo()._guarded().create(values)

    # ------------------------------------------------------------------
    # Delivery
    # ------------------------------------------------------------------
    def _fix_real_recipient(self):
        """The unmasked destination — used only to hand to M27, never stored
        on the evidence row."""
        self.ensure_one()
        return _address_for(self.customer_id, self.channel)

    def _fix_suppression_reason(self, as_of=None) -> str:
        """Why this reminder must NOT go out now, or ''.

        Re-checked at send time (the audit's requirement): the ladder's
        decision was made moments ago, but a dispute can be logged, a promise
        recorded or a payment allocated in the same run loop's window, and
        BRU-ARB-15/16 binds the SEND, not only the advance.
        """
        self.ensure_one()
        today = fields.Date.to_date(as_of or fields.Date.today())
        run = self.dunning_id
        invoice = self.invoice_id
        if invoice.state != "issued":
            return "Invoice %s is %s, not open." % (invoice.name, invoice.state)
        if invoice.amount_residual <= 0.005:
            return "Invoice %s is settled." % invoice.name
        if run.suppressed:
            return "Dunning is suppressed (%s)." % (run.suppression_reason or "recorded")
        if hasattr(run, "_manual_suppression_active") and run._manual_suppression_active(today):
            return "A recorded suppression holds this invoice until %s." % run.suppressed_until
        hold = self.env["fix.dunning"]._fix_holding_arrangement(invoice, today)
        if hold:
            return "A promise to pay or payment plan holds this invoice."
        disputed = sum(
            self.env["fix.ar.dispute"]
            .sudo()
            .search([("invoice_id", "=", invoice.id), ("state", "=", "open")])
            .mapped("amount_disputed")
        )
        if invoice.amount_residual - disputed <= 0.005:
            return "The open dispute covers the residual (FR-ARB-036)."
        return ""

    def _fix_finish(self, state, **values):
        self.ensure_one()
        values = dict(values, state=state)
        self.sudo()._guarded().write(values)
        label = dict(self._fields["state"].selection).get(state, state)
        self.sudo().message_post(
            body="Dunning reminder %s → %s (%s)." % (self.name or self.id, label, self.channel)
        )

    def _fix_delivery(self):
        """The M27 delivery row this reminder left through, when M27 is
        installed and the row still exists."""
        self.ensure_one()
        Notif = self.env.get("fix.notif.delivery")
        ref = self.notif_delivery_ref or ""
        if Notif is None or not ref.startswith("fix.notif.delivery:"):
            return None
        try:
            delivery_id = int(ref.split(":", 1)[1])
        except (TypeError, ValueError):
            return None
        return Notif.sudo().browse(delivery_id).exists()

    def _fix_dedup_key(self, attempt=0):
        key = "ar-dunning:%d:%s:%s" % (self.invoice_id.id, self.step, self.channel)
        return key if not attempt else "%s:retry:%d" % (key, attempt)

    def _fix_dispatch(self, as_of=None):
        """Route the reminder to its channel (idempotent on the step)."""
        self.ensure_one()
        if self.state != "pending":
            return self
        reason = self._fix_suppression_reason(as_of=as_of)
        if reason:
            self._fix_finish("suppressed", failure_reason=reason)
            return self
        if self.channel == CALL_CHANNEL:
            self._fix_handoff()
        elif self.channel in MANUAL_CHANNELS:
            self._fix_finish(
                "manual",
                note="%s channel: no outbound message is sent; the reminder is %s."
                % (
                    self.channel,
                    "presented in the customer portal" if self.channel == "portal" else "printed",
                ),
            )
        else:
            self._fix_send_message()
        return self

    def _fix_outcome_of(self, delivery):
        """The M27 row's outcome, with a suppression's reason kept as the
        evidence's failure_reason (a consent refusal is evidence)."""
        delivery.invalidate_recordset(
            ["state", "sent_at", "last_error", "provider_ref", "consent_reason"]
        )
        error = delivery.last_error or (
            delivery.consent_reason if delivery.state == "suppressed" else ""
        )
        return (
            delivery.state,
            error or "",
            delivery.provider_ref or "",
            delivery.sent_at,
            delivery.id,
        )

    def _fix_send_message(self):
        """Send through M27's single outbound exit and record the outcome."""
        self.ensure_one()
        Notif = self.env.get("fix.notif.delivery")
        if Notif is None:
            self._fix_finish(
                "failed",
                failure_reason="The M27 notification delivery service is not installed, "
                "so no reminder was transmitted.",
            )
            return False
        address = self._fix_real_recipient()
        if not address:
            self._fix_finish(
                "failed",
                failure_reason="No %s destination is on file for %s."
                % (self.channel, self.customer_id.display_name),
            )
            return False
        outcome = None
        try:
            with self.env.cr.savepoint():
                delivery = Notif.sudo().queue(
                    channel=self.channel,
                    purpose="collections",
                    partner=self.customer_id,
                    to_address=address,
                    subject=self.subject,
                    body=self.body,
                    lawful_basis="contract",
                    source_model=self._name,
                    source_id=self.id,
                    dedup_key=self._fix_dedup_key(),
                    operating_unit=self.operating_unit_id,
                    company=self.company_id,
                )
                if delivery.state == "queued":
                    delivery.action_send()
                outcome = self._fix_outcome_of(delivery)
        except Exception as exc:  # a bad address, a missing provider, a gateway fault
            _logger.warning("Dunning reminder %s was not sent: %s", self.id, exc)
            outcome = ("exception", str(exc), "", False, 0)
        return self._fix_apply_outcome(outcome)

    def _fix_apply_outcome(self, outcome, retry_count=None):
        state, error, provider_ref, sent_at, delivery_id = outcome
        ref = "fix.notif.delivery:%d" % delivery_id if delivery_id else False
        extra = {} if retry_count is None else {"retry_count": retry_count}
        if state in ("sent", "delivered"):
            self._fix_finish(
                "sent",
                sent_at=sent_at or fields.Datetime.now(),
                provider_ref=provider_ref or False,
                notif_delivery_ref=ref,
                failure_reason=False,
                **extra,
            )
            return True
        if state == "suppressed":
            self._fix_finish(
                "suppressed",
                failure_reason=error or "Suppressed by the consent / DND check.",
                notif_delivery_ref=ref,
                **extra,
            )
            return False
        self._fix_finish(
            "failed",
            failure_reason=error or "The provider did not accept the message (%s)." % state,
            notif_delivery_ref=ref or self.notif_delivery_ref or False,
            **extra,
        )
        return False

    def _fix_handoff(self):
        """A call step is a CONTACT-CENTRE task, never a fake message."""
        self.ensure_one()
        handoff = (
            self.env["fix.ar.dunning.handoff"]
            .sudo()
            ._guarded()
            .create(
                {
                    "company_id": self.company_id.id,
                    "operating_unit_id": self.operating_unit_id.id,
                    "action_id": self.id,
                    "invoice_id": self.invoice_id.id,
                    "customer_id": self.customer_id.id,
                    "phone": self._fix_real_recipient(),
                    "amount": self.amount,
                    "days_overdue": self.days_overdue,
                    "priority": 40 if self.level == "l3" else 30,
                    "note": "Dunning %s (%s) for invoice %s."
                    % (self.step, self.tone or "", self.invoice_id.name),
                }
            )
        )
        reference = handoff._fix_route_to_m27()
        if reference:
            handoff._guarded().write({"m27_reference": reference})
        self._fix_finish(
            "handoff",
            handoff_id=handoff.id,
            note="M27 follow-up %s raised%s."
            % (
                handoff.name,
                " and routed to %s" % reference if reference else "",
            ),
        )
        return handoff

    # ------------------------------------------------------------------
    # Retry
    # ------------------------------------------------------------------
    def action_retry(self):
        """Retry a FAILED reminder. A sent one is never sent twice."""
        require_role(self.env, GROUP_ACCOUNTANT, "Retrying a dunning reminder")
        for action in self:
            if action.state == "sent":
                # Idempotent: the evidence says it went out; a second message
                # would be a duplicate the customer must not receive.
                continue
            if action.state != "failed":
                raise UserError(
                    "Only a failed reminder is retried (this one is %s)."
                    % dict(action._fields["state"].selection).get(action.state, action.state)
                )
            action._fix_retry()
        return True

    def _fix_retry(self):
        self.ensure_one()
        reason = self._fix_suppression_reason()
        if reason:
            self._fix_finish("suppressed", failure_reason=reason)
            return False
        if self.dunning_id.step != self.step:
            # The ladder moved on while this send was failing. Retrying an
            # earlier level after a later one went out would tell the
            # customer two different things; the later step supersedes it.
            self._fix_finish(
                "suppressed",
                retry_count=(self.retry_count or 0) + 1,
                failure_reason="Superseded by the ladder's later step (%s)." % self.dunning_id.step,
            )
            return False
        if self.channel == CALL_CHANNEL:
            self._fix_handoff()
            return True
        if self.channel in MANUAL_CHANNELS:
            self._fix_finish("manual", note="%s channel: no outbound message." % self.channel)
            return False
        delivery = self._fix_delivery()
        attempt = (self.retry_count or 0) + 1
        if delivery is not None and delivery.state in ("sent", "delivered"):
            # Someone else's retry won the race: adopt its evidence.
            self._fix_finish(
                "sent",
                sent_at=delivery.sent_at or fields.Datetime.now(),
                provider_ref=delivery.provider_ref or False,
                notif_delivery_ref="fix.notif.delivery:%d" % delivery.id,
                failure_reason=False,
                retry_count=attempt,
            )
            return True
        Notif = self.env.get("fix.notif.delivery")
        if Notif is None:
            self._fix_finish(
                "failed",
                retry_count=attempt,
                failure_reason="The M27 notification delivery service is not installed.",
            )
            return False
        address = self._fix_real_recipient()
        if not address:
            self._fix_finish(
                "failed",
                retry_count=attempt,
                failure_reason="No %s destination is on file for %s."
                % (self.channel, self.customer_id.display_name),
            )
            return False
        outcome = None
        try:
            with self.env.cr.savepoint():
                if delivery is not None and delivery.state in ("queued", "failed"):
                    # Re-resolve a provider attached since the first attempt.
                    if not delivery.provider_id:
                        Provider = self.env.get("fix.notif.provider")
                        if Provider is not None:
                            provider = Provider.sudo().provider_for(
                                self.channel, company=self.company_id
                            )
                            if provider:
                                delivery.sudo().write({"provider_id": provider.id})
                    delivery.action_send()
                    outcome = self._fix_outcome_of(delivery)
                else:
                    # The previous transport row is terminal (dry run, manual
                    # provider, cancelled): a fresh attempt is a fresh row.
                    delivery = Notif.sudo().queue(
                        channel=self.channel,
                        purpose="collections",
                        partner=self.customer_id,
                        to_address=address,
                        subject=self.subject,
                        body=self.body,
                        lawful_basis="contract",
                        source_model=self._name,
                        source_id=self.id,
                        dedup_key=self._fix_dedup_key(attempt),
                        operating_unit=self.operating_unit_id,
                        company=self.company_id,
                    )
                    if delivery.state == "queued":
                        delivery.action_send()
                    outcome = self._fix_outcome_of(delivery)
        except Exception as exc:
            _logger.warning("Dunning reminder %s retry failed: %s", self.id, exc)
            outcome = ("exception", str(exc), "", False, 0)
        return self._fix_apply_outcome(outcome, retry_count=attempt)

    def action_retry_failed(self):
        """Manual button: retry these failed reminders now."""
        return self.action_retry()

    @api.model
    def _cron_retry_failed(self, limit=200):
        """AUT-ARB-10: a failed reminder is retried, not silently dropped."""
        max_retries = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(PARAM_DUNNING_RETRY_MAX, DEFAULT_DUNNING_RETRY_MAX)
            or DEFAULT_DUNNING_RETRY_MAX
        )
        failed = self.sudo().search(
            [
                ("state", "=", "failed"),
                ("channel", "in", list(MESSAGE_CHANNELS)),
                ("retry_count", "<", max_retries),
            ],
            limit=limit,
        )
        sent = 0
        for action in failed:
            try:
                action._fix_retry()
            except Exception:
                _logger.exception("Dunning reminder %s retry raised", action.id)
            sent += int(action.state == "sent")
        return {"failed": len(failed), "sent": sent}


class FixArDunningHandoff(models.Model):
    """The contact-centre follow-up a CALL ladder step raises.

    M27's own queue entry (fix.routing.workitem, via a collections workstream)
    is used when one is configured; this row is the always-present, explicit
    `m27_follow_up` queue record, so a call step can never be mistaken for a
    message that was "sent".
    """

    _name = "fix.ar.dunning.handoff"
    _description = "Dunning Call Handoff (M27 contact-centre follow-up)"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "priority desc, create_date, id"
    _rec_name = "name"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", index=True)
    action_id = fields.Many2one(
        "fix.ar.dunning.action",
        string="Reminder Evidence",
        required=True,
        ondelete="restrict",
        index=True,
    )
    invoice_id = fields.Many2one(
        "fix.ar.invoice", string="Invoice", required=True, ondelete="restrict", index=True
    )
    customer_id = fields.Many2one(
        "res.partner", string="Customer", required=True, ondelete="restrict", index=True
    )
    name = fields.Char(compute="_compute_name", store=True)
    currency_id = fields.Many2one(related="invoice_id.currency_id", string="Currency")
    phone = fields.Char(string="Number To Call")
    amount = fields.Monetary(string="Amount Due", currency_field="currency_id")
    days_overdue = fields.Integer(string="Days Overdue")
    priority = fields.Integer(default=30, help="Higher is worked first.")
    state = fields.Selection(
        [
            ("m27_follow_up", "M27 follow-up (awaiting contact centre)"),
            ("picked_up", "Picked up by an agent"),
            ("done", "Contacted"),
            ("cancelled", "Cancelled"),
        ],
        default="m27_follow_up",
        required=True,
        tracking=True,
        index=True,
    )
    m27_reference = fields.Char(
        string="M27 Work Item",
        readonly=True,
        help="fix.routing.workitem:<id> when a contact-centre workstream routed it.",
    )
    note = fields.Text(readonly=True)
    picked_up_by_id = fields.Many2one("res.users", string="Picked Up By", readonly=True)
    picked_up_at = fields.Datetime(readonly=True)
    closed_at = fields.Datetime(readonly=True)
    closed_by_id = fields.Many2one("res.users", string="Closed By", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "m27_reference",
            "picked_up_by_id",
            "picked_up_at",
            "closed_at",
            "closed_by_id",
        }

    @api.depends("invoice_id.name", "customer_id.name")
    def _compute_name(self):
        for rec in self:
            rec.name = "Call %s / %s" % (
                rec.invoice_id.name or "Invoice #%s" % rec.invoice_id.id,
                rec.customer_id.name or "customer",
            )

    def _fix_route_to_m27(self) -> str:
        """Route the call to a configured M27 collections workstream.

        Nothing is created on a guess: with no workstream, the local
        `m27_follow_up` row is the handoff and the pack says so.
        """
        self.ensure_one()
        Workstream = self.env.get("fix.routing.workstream")
        if Workstream is None:
            return ""
        workstream = Workstream.sudo().search(
            [
                ("active", "=", True),
                ("company_id", "in", [self.company_id.id, False]),
                (
                    "source_model",
                    "in",
                    ("fix.ar.dunning.action", "fix.ar.invoice", "fix.dunning"),
                ),
            ],
            limit=1,
        )
        if not workstream:
            return ""
        try:
            with self.env.cr.savepoint():
                item = workstream.intake(
                    self.action_id._name, self.action_id.id, partner=self.customer_id
                )
            return "fix.routing.workitem:%d" % item.id
        except Exception as exc:
            _logger.info("Dunning call handoff not routed to M27: %s", exc)
            return ""

    def action_pick_up(self):
        require_role(self.env, GROUP_ACCOUNTANT, "Picking up a dunning call")
        for rec in self:
            if rec.state != "m27_follow_up":
                raise UserError("Only a queued M27 follow-up is picked up.")
            rec._guarded().write(
                {
                    "state": "picked_up",
                    "picked_up_by_id": self.env.uid,
                    "picked_up_at": fields.Datetime.now(),
                }
            )
            rec.message_post(body="Dunning call picked up by %s." % self.env.user.name)
        return True

    def action_done(self, note=""):
        require_role(self.env, GROUP_ACCOUNTANT, "Closing a dunning call")
        if not (note or "").strip():
            raise UserError("Say what the call established before closing it.")
        for rec in self:
            if rec.state not in ("m27_follow_up", "picked_up"):
                raise UserError("Only an open dunning call is closed.")
            rec._guarded().write(
                {
                    "state": "done",
                    "note": (note or "").strip()[:500],
                    "closed_at": fields.Datetime.now(),
                    "closed_by_id": self.env.uid,
                }
            )
            rec.message_post(body="Dunning call closed: %s" % note)
        return True

    def action_cancel(self, reason=""):
        require_role(self.env, GROUP_ACCOUNTANT, "Cancelling a dunning call")
        if not (reason or "").strip():
            raise UserError("Say why the dunning call is cancelled.")
        for rec in self:
            if rec.state in ("done", "cancelled"):
                raise UserError("A closed dunning call is not cancelled again.")
            rec._guarded().write(
                {
                    "state": "cancelled",
                    "note": (reason or "").strip()[:500],
                    "closed_at": fields.Datetime.now(),
                    "closed_by_id": self.env.uid,
                }
            )
            rec.message_post(body="Dunning call cancelled: %s" % reason)
        return True


class FixDunningDispatch(models.Model):
    """The ladder's send half: on a step transition, deliver the reminder."""

    _inherit = "fix.dunning"

    reminder_ids = fields.One2many("fix.ar.dunning.action", "dunning_id", string="Reminders Sent")
    reminder_count = fields.Integer(compute="_compute_reminder_count")

    def _compute_reminder_count(self):
        for run in self:
            run.reminder_count = len(run.reminder_ids)

    def _fix_dispatch_reminder(self, as_of=None):
        """One evidence row per step+channel; returns it in every case."""
        self.ensure_one()
        Action = self.env["fix.ar.dunning.action"].sudo()
        existing = Action.search(
            [
                ("dunning_id", "=", self.id),
                ("step", "=", self.step),
                ("channel", "=", self.channel),
            ],
            limit=1,
        )
        if existing:
            return existing
        try:
            # The row is created before the send, so a crash mid-attempt
            # leaves evidence. A savepoint keeps a unique-constraint race
            # from poisoning the whole ladder run: the winner's row is used.
            with self.env.cr.savepoint():
                action = Action._fix_create_for(self, as_of=as_of)
        except Exception:
            existing = Action.search(
                [
                    ("dunning_id", "=", self.id),
                    ("step", "=", self.step),
                    ("channel", "=", self.channel),
                ],
                limit=1,
            )
            if existing:
                return existing
            raise
        try:
            return action._fix_dispatch(as_of=as_of)
        except Exception as exc:
            # The evidence row already exists; leave it in a state the retry
            # cron will pick up rather than an orphaned `pending`.
            try:
                action._fix_finish("failed", failure_reason="Dispatch error: %s" % exc)
            except Exception:
                _logger.exception("Could not mark dunning reminder %s failed", action.id)
            raise

    def action_send_reminder(self):
        """Manual send of the current step (idempotent)."""
        require_role(self.env, GROUP_ACCOUNTANT, "Sending a dunning reminder")
        for run in self:
            if run.suppressed:
                raise UserError(
                    "Dunning is suppressed for %s; lift it first." % run.invoice_id.name
                )
            run._fix_dispatch_reminder()
        return True

    @api.model
    def action_run_dunning(self, as_of=None):
        result = super().action_run_dunning(as_of=as_of)
        runs = self.sudo().browse(result.get("transitioned_ids") or []).exists()
        counts = {"sent": 0, "failed": 0, "suppressed": 0, "handoff": 0, "manual": 0}
        for run in runs:
            try:
                action = run._fix_dispatch_reminder(as_of=as_of)
            except Exception:  # a broken reminder must not sink the whole ladder
                _logger.exception("Dunning reminder dispatch failed for %s", run.invoice_id.name)
                continue
            counts[action.state] = counts.get(action.state, 0) + 1
        result["reminders_dispatched"] = counts
        return result
