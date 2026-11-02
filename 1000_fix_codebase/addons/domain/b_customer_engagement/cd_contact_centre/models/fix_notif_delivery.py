# S1 — the Notification Delivery Service (A03 gap-plan Part IV, service S1).
#
# WHY this file exists. Every A03 module sent messages, and not one of them
# recorded that it had:
#   * M10 posted voucher and points-expiry notices with no record of the send;
#   * M34 dispatched CSAT surveys by publishing an event nothing logged;
#   * M35 launched campaigns that counted RECIPIENTS, never MESSAGES;
#   * M27's fix.cc.notif.template carried a consent_class that nothing read.
# So the estate could not answer three questions a service business must be
# able to answer: did this customer actually receive it, what did WhatsApp
# charge us this month, and what were we entitled to send them.
#
# This module is the one place a message leaves the estate. Every send is a
# row here BEFORE it is attempted, including a send that is refused — a
# suppression is the evidence that the rule worked, so it is logged, not
# dropped. Writing an adapter anywhere else is a review-blocking defect.
#
# Three things are deliberately NOT faked:
#   1. No carrier is invented. SMS and WhatsApp transports are seams; with no
#      provider configured a row stays `queued` and says why. CPaaS vendor
#      selection is a declared external dependency (CRM blueprint 3.9.3).
#   2. Delivery is never assumed from a successful send. `sent` and
#      `delivered` are different states, and only a provider callback moves a
#      row to `delivered`.
#   3. Cost is recorded per message from the provider's configured tariff,
#      and is zero (not estimated) until a provider is attached.
import logging
import sys
from datetime import timedelta
from pathlib import Path

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py import fix_btrc
from libs.py.fix_events import publish  # FF-28

_logger = logging.getLogger(__name__)

# The estate's channel adapters (INT-010/011 SMS, INT-012 WhatsApp, INT-013
# e-mail, Novu push, in-app). The folder is `notification-dispatcher`, which
# is not an importable package name, so the src directory goes on sys.path --
# the same pattern cd_rate_card and cd_cash_position already use to reach
# their services.
_DISPATCHER_SRC = (
    Path(__file__).resolve().parents[5] / "services" / "notification-dispatcher" / "src"
)


def _channel_adapters():
    """The adapter classes, or None when the service tree is unavailable.

    Imported lazily: a missing service directory must degrade to "nothing was
    transmitted, and here is why" rather than break the Odoo registry load.
    """
    try:
        if str(_DISPATCHER_SRC) not in sys.path:
            sys.path.insert(0, str(_DISPATCHER_SRC))
        import channels as dispatcher_channels
    except Exception as exc:
        _logger.warning("notification-dispatcher adapters unavailable: %s", exc)
        return None
    return dispatcher_channels


DELIVERY_CHANNELS = [
    ("sms", "SMS"),
    ("whatsapp", "WhatsApp"),
    ("email", "E-mail"),
    ("push", "Push"),
    ("voice", "Voice (outbound call)"),
]

# How a provider actually moves the message. Only `odoo_mail` is wired
# in-estate today; the rest are honest seams.
TRANSPORTS = [
    ("int_gateway", "Estate channel adapter (INT-010/011/012/013, Novu)"),
    ("odoo_mail", "Odoo mail server (e-mail)"),
    ("manual", "Manual — an operator sends it and marks it sent"),
]

# Which adapter class carries each channel.
ADAPTER_FOR_CHANNEL = {
    "sms": "SMSChannel",
    "whatsapp": "WhatsAppChannel",
    "email": "EmailChannel",
    "push": "PushChannel",
}

# BD-02: a marketing message never uses the registered masking sender. The
# route is DERIVED from the processing purpose rather than configured, because
# it is a regulatory consequence of the purpose and not a preference.
NON_MASKING_PURPOSES = frozenset({"marketing", "profiling"})

# BD-03: the masking signature must not appear on a numeric-sender message.
MASKING_SIGNATURE = "1000FiX"

# Retry backoff in minutes, applied by attempt number. A transient gateway
# failure resolves in minutes; a bad recipient never resolves, so the ladder
# is short and then gives up rather than retrying forever and paying for it.
RETRY_BACKOFF_MINUTES = (2, 10, 30, 120)


class FixNotifProvider(models.Model):
    """A configured delivery provider for one channel.

    The tariff lives here so per-message cost is read from configuration
    rather than guessed. WhatsApp has charged per message since July 2025,
    which is the unit-economics question S1 exists to answer.
    """

    _name = "fix.notif.provider"
    _description = "Notification Provider"
    _order = "channel, sequence, id"

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True, help="Short key used in logs and dashboards.")
    channel = fields.Selection(DELIVERY_CHANNELS, required=True, default="sms")
    transport = fields.Selection(TRANSPORTS, required=True, default="int_gateway")
    endpoint_config_key = fields.Char(
        string="Endpoint Config Key",
        help="Only for a transport that reads Odoo configuration. The estate "
        "channel adapters read their endpoint and credential from the "
        "ENVIRONMENT (FIX_SMS_GATEWAY_URL, FIX_WHATSAPP_API_URL, "
        "FIX_EMAIL_API_URL, FIX_NOVU_API_URL), so a secret never reaches the "
        "database at all.",
    )
    sender_mask = fields.Char(
        string="Registered Sender Mask",
        help="BTRC-registered sender ID presented to the subscriber (REQ-35.4).",
    )
    cost_per_message = fields.Monetary(
        string="Tariff per Message",
        currency_field="currency_id",
        help="The contracted per-message price. 0 means no tariff is on file, "
        "and cost is then recorded as 0 rather than estimated.",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    max_attempts = fields.Integer(
        required=True, default=4, help="Attempts before a message is abandoned as failed."
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )

    _code_unique = models.Constraint(
        "UNIQUE (code)", "Each notification provider code exists once."
    )

    @api.constrains("max_attempts")
    def _check_max_attempts(self):
        for rec in self:
            if rec.max_attempts < 1:
                raise ValidationError("A provider must allow at least one attempt.")

    @api.model
    def provider_for(self, channel, company=None):
        """The provider that should carry a message on this channel, or None.

        Returning None is a legitimate, expected answer: it means no carrier
        has been contracted for that channel yet, and the delivery row will
        say exactly that instead of silently dropping the message.
        """
        company_id = getattr(company, "id", company) or self.env.company.id
        return (
            self.sudo().search(
                [
                    ("channel", "=", channel),
                    ("active", "=", True),
                    ("company_id", "in", [company_id, False]),
                ],
                order="sequence, id",
                limit=1,
            )
            or None
        )


class FixNotifDelivery(models.Model):
    """One outbound message: what we tried to send, to whom, under what
    lawful basis, through which provider, at what cost, and what happened.

    The row is created BEFORE the attempt, so a crash mid-send leaves
    evidence rather than silence.
    """

    _name = "fix.notif.delivery"
    _description = "Notification Delivery"
    _inherit = ["mail.thread"]
    _order = "queued_at desc, id desc"
    _rec_name = "to_address"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        index=True,
        help="The OU whose activity caused the send. Empty for estate-wide "
        "sends such as a national campaign.",
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Recipient Party",
        index=True,
        ondelete="set null",
        help="Empty when the recipient is not an identified party — which is "
        "itself a consent refusal, never a pass.",
    )
    to_address = fields.Char(
        required=True,
        index=True,
        help="The actual destination: MSISDN, WhatsApp JID or e-mail address.",
    )
    channel = fields.Selection(DELIVERY_CHANNELS, required=True, index=True)
    purpose = fields.Selection(
        [
            ("service_updates", "Service Updates"),
            ("marketing", "Marketing"),
            ("research", "Research & Analytics"),
            ("collections", "Debt Collection"),
            ("profiling", "Profiling"),
            ("call_recording", "Call Recording"),
        ],
        required=True,
        index=True,
        help="The PROCESSING purpose the consent decision was taken against.",
    )
    lawful_basis = fields.Selection(
        [
            ("consent", "Consent"),
            ("contract", "Performance of a contract"),
            ("legal_obligation", "Legal obligation"),
            ("vital_interest", "Vital interest"),
        ],
        required=True,
        default="consent",
        help="What this send relies on. Anything other than consent must be "
        "declared by the caller; it is recorded, never inferred.",
    )
    template_id = fields.Many2one("fix.cc.notif.template", string="Template")
    subject = fields.Char()
    body = fields.Text(required=True, help="The rendered message as sent.")
    language = fields.Selection(
        [("bn", "Bengali"), ("en", "English")],
        required=True,
        default="en",
        help="Which language version was actually sent (DE-17). Recorded "
        "because 'we have Bengali templates' and 'this customer received "
        "Bengali' are different claims, and only the second one matters.",
    )

    state = fields.Selection(
        [
            ("queued", "Queued"),
            ("sent", "Sent to provider"),
            ("delivered", "Delivered"),
            ("dry_run", "Dry run (gateway not configured)"),
            ("failed", "Failed"),
            ("suppressed", "Suppressed (not sent)"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="queued",
        index=True,
        tracking=True,
    )
    # --- consent evidence (S2) ---
    consent_decision = fields.Char(
        readonly=True,
        help="The S2 verdict: granted / withdrawn / absent / unidentified / " "basis_declared.",
    )
    consent_reason = fields.Text(readonly=True, help="The S2 verdict in words.")
    consent_id = fields.Many2one(
        "fix.consent", string="Decisive Consent Record", readonly=True, ondelete="set null"
    )
    consent_checked_at = fields.Datetime(readonly=True)
    # --- BTRC curfew evidence ---
    curfew_bound = fields.Boolean(
        readonly=True, help="Whether the BTRC 08:00-22:00 window binds this send."
    )
    curfew_hold_until = fields.Datetime(
        readonly=True, help="When a curfew-held message becomes sendable."
    )
    # --- provider and outcome ---
    provider_id = fields.Many2one("fix.notif.provider", string="Provider", ondelete="set null")
    provider_ref = fields.Char(
        index=True, help="The provider's own message id, for reconciliation."
    )
    attempts = fields.Integer(default=0, readonly=True)
    max_attempts = fields.Integer(default=4)
    last_error = fields.Text(readonly=True)
    next_attempt_at = fields.Datetime(index=True)
    cost = fields.Monetary(
        currency_field="currency_id",
        readonly=True,
        help="Charged per message from the provider tariff. 0 means no tariff "
        "is on file — never an estimate.",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    # --- provenance ---
    source_model = fields.Char(index=True, help="The model that asked for the send.")
    source_id = fields.Integer(index=True)
    source_event_id = fields.Char(index=True, help="Outbox event id, when event-driven.")
    dedup_key = fields.Char(
        index=True,
        help="Idempotency key. A second queue() with the same key returns the "
        "existing row instead of sending twice.",
    )
    queued_at = fields.Datetime(required=True, default=fields.Datetime.now, index=True)
    sent_at = fields.Datetime(readonly=True)
    delivered_at = fields.Datetime(readonly=True)
    failed_at = fields.Datetime(readonly=True)

    _dedup_unique = models.Constraint(
        "UNIQUE (dedup_key)",
        "A message with this idempotency key has already been queued.",
    )

    # ------------------------------------------------------------------
    # The single entry point
    # ------------------------------------------------------------------
    @api.model
    def queue(
        self,
        channel,
        purpose,
        to_address=None,
        partner=None,
        body=None,
        subject=None,
        template=None,
        template_values=None,
        lawful_basis="consent",
        source_model=None,
        source_id=None,
        source_event_id=None,
        dedup_key=None,
        operating_unit=None,
        company=None,
    ):
        """Queue one outbound message. THE way a message leaves the estate.

        Order of operations matters and is deliberate:
          1. resolve the recipient address (refuse if there is none);
          2. render the body (from a template, or take it as given);
          3. ask S2 for the consent verdict — a refusal is RECORDED as a
             suppressed row, because the suppression is the evidence;
          4. ask the BTRC clock whether the window permits it now;
          5. attach the provider and its tariff;
          6. leave the row queued for the dispatch cron.

        Returns the fix.notif.delivery record in every case, including
        refusal. Callers that want an exception on refusal should check
        `.state == 'suppressed'` or call fix.consent.consent_assert first.
        """
        if channel not in dict(DELIVERY_CHANNELS):
            raise ValidationError("Unknown delivery channel %r." % channel)
        partner_rec = (
            partner
            if hasattr(partner, "id")
            else (self.env["res.partner"].browse(partner) if partner else self.env["res.partner"])
        )
        partner_rec = partner_rec.exists() if partner_rec else self.env["res.partner"]

        # Idempotency first: never do work we are about to discard.
        if dedup_key:
            existing = self.sudo().search([("dedup_key", "=", dedup_key)], limit=1)
            if existing:
                return existing

        address = to_address or self._default_address(partner_rec, channel)
        if not address:
            raise ValidationError(
                "Cannot queue a %s message: no destination address was given and "
                "the party has none on file." % channel
            )

        template_rec = (
            template
            if hasattr(template, "id")
            else (self.env["fix.cc.notif.template"].browse(template) if template else None)
        )
        language = self._preferred_language(partner_rec)
        rendered_subject, rendered_body, sent_language = self._render(
            template_rec, subject, body, template_values or {}, language=language
        )
        if not (rendered_body or "").strip():
            raise ValidationError("Cannot queue an empty message body.")

        company_rec = company or self.env.company
        verdict = self.env["fix.consent"].consent_check(
            partner_rec, purpose, channel, basis=lawful_basis, company=company_rec
        )
        curfew = fix_btrc.curfew_verdict(purpose, channel)
        provider = self.env["fix.notif.provider"].provider_for(channel, company=company_rec)

        vals = {
            "company_id": company_rec.id,
            "operating_unit_id": getattr(operating_unit, "id", operating_unit) or False,
            "partner_id": partner_rec.id or False,
            "to_address": address,
            "channel": channel,
            "purpose": purpose,
            "lawful_basis": lawful_basis,
            "template_id": template_rec.id if template_rec else False,
            "subject": rendered_subject,
            "body": rendered_body,
            "language": sent_language,
            "consent_decision": verdict["decision"],
            "consent_reason": verdict["reason"],
            "consent_id": verdict["consent_id"] or False,
            "consent_checked_at": fields.Datetime.now(),
            "curfew_bound": curfew["bound"],
            "curfew_hold_until": curfew["hold_until"] or False,
            "provider_id": provider.id if provider else False,
            "max_attempts": provider.max_attempts if provider else 4,
            "source_model": source_model or False,
            "source_id": source_id or 0,
            "source_event_id": source_event_id or False,
            "dedup_key": dedup_key or False,
        }
        if not verdict["allowed"]:
            vals.update(state="suppressed", next_attempt_at=False)
        else:
            vals.update(
                state="queued",
                next_attempt_at=curfew["hold_until"] or fields.Datetime.now(),
            )
        record = self.sudo().create(vals)

        # Two literal publish calls rather than one with a computed event
        # type: the event-registry auditor reads publish() CALL SITES
        # statically, so an event name built by a conditional expression is
        # invisible to it and would never be checked against the registry.
        event_payload = {
            "channel": channel,
            "purpose": purpose,
            "partner_id": partner_rec.id or None,
            "decision": verdict["decision"],
            "reason": verdict["reason"],
            "curfew_bound": curfew["bound"],
            "provider": provider.code if provider else None,
        }
        if verdict["allowed"]:
            publish(
                self.env,
                "notification.queued",
                "fix.notif.delivery",
                record.id,
                event_payload,
            )
        else:
            publish(
                self.env,
                "notification.suppressed",
                "fix.notif.delivery",
                record.id,
                event_payload,
            )
        return record

    @api.model
    def _default_address(self, partner, channel):
        """The party's address for this channel, or '' when they have none."""
        if not partner:
            return ""
        if channel == "email":
            return partner.email or ""
        if channel in ("sms", "whatsapp", "voice"):
            # getattr: `mobile` is not present on res.partner in every Odoo
            # build, and a send must not crash on the ones without it.
            return getattr(partner, "mobile", False) or partner.phone or ""
        return ""

    @api.model
    def _preferred_language(self, partner):
        """Which language this recipient should be written to in.

        DELEGATES to M33's res.partner._get_notification_language(), which
        has existed all along and which nothing was calling at send time --
        so a customer who had stated a preference was served whatever the
        template author happened to write. Re-deriving the preference here
        would be exactly the duplication this whole programme of work is
        removing.

        With no identified party there is no stated preference, so the
        estate default (Bengali, PS-03) applies rather than English.
        """
        if not partner:
            return "bn"
        return partner._get_notification_language() or "bn"

    @api.model
    def _render(self, template, subject, body, values, language="en"):
        """Fill {{placeholders}} in a template, or pass an explicit body through.

        Deliberately a literal placeholder substitution and not an expression
        evaluator: a marketing template is authored by a marketer, and giving
        authored text the power to evaluate code against the ORM would be a
        remote-execution surface for the sake of a convenience nobody asked
        for. An unknown placeholder is left visible rather than blanked, so a
        mis-authored template is obvious in the log instead of silently
        sending a sentence with a hole in it.

        Language selection (DE-17): a Bengali-preferring recipient gets the
        Bengali body when the template HAS one. It falls back to English
        rather than sending nothing, and the fallback is visible in the
        delivery row's `language` field, so missing Bengali copy shows up as
        a measurable number instead of an assumption.
        """
        out_subject = subject or ""
        out_body = body or ""
        used_language = language
        if template:
            if language == "bn":
                bn_body = (getattr(template, "body_bn", "") or "").strip()
                bn_subject = (getattr(template, "subject_bn", "") or "").strip()
                if not out_body and bn_body:
                    out_body = bn_body
                elif not out_body:
                    out_body = template.body or ""
                    used_language = "en"
                if not out_subject:
                    out_subject = bn_subject or template.subject or ""
            else:
                out_body = out_body or template.body or ""
                out_subject = out_subject or template.subject or ""
        if not template and language == "bn":
            # An explicit body was passed by the caller; we cannot know which
            # language it is in, so we do not claim Bengali.
            used_language = "en" if body else language
        for key, value in (values or {}).items():
            token = "{{%s}}" % key
            out_subject = out_subject.replace(token, str(value))
            out_body = out_body.replace(token, str(value))
        return out_subject, out_body, used_language

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------
    def action_send(self):
        """Attempt delivery now. Records the outcome either way."""
        for rec in self:
            if rec.state in ("delivered", "suppressed", "cancelled", "dry_run"):
                raise UserError(
                    "This message is %s and cannot be sent."
                    % dict(rec._fields["state"].selection)[rec.state]
                )
            rec._attempt()
        return True

    def _attempt(self):
        """One delivery attempt, with the outcome written whatever happens."""
        self.ensure_one()
        # Re-check the curfew at SEND time, not only at queue time: a message
        # queued at 21:58 and dispatched at 22:03 is an out-of-window send,
        # and the regulator cares when it left, not when it was composed.
        curfew = fix_btrc.curfew_verdict(self.purpose, self.channel)
        if not curfew["allowed"]:
            self.write(
                {
                    "curfew_bound": True,
                    "curfew_hold_until": curfew["hold_until"],
                    "next_attempt_at": curfew["hold_until"],
                    "last_error": curfew["reason"],
                }
            )
            return False

        provider = self.provider_id
        if not provider:
            # The honest state: nothing was sent and nothing is pretended.
            self.write(
                {
                    "last_error": "No provider is configured for channel '%s'. The "
                    "message stays queued; CPaaS/WhatsApp vendor selection is a "
                    "declared external dependency." % self.channel,
                    "next_attempt_at": fields.Datetime.now() + timedelta(hours=1),
                }
            )
            return False

        self.attempts += 1
        try:
            result = self._dispatch_via_provider(provider)
        except Exception as exc:
            _logger.warning("notif delivery %s failed: %s", self.id, exc)
            result = {"ok": False, "error": str(exc), "provider_ref": ""}

        if result.get("ok"):
            self.write(
                {
                    "state": "sent",
                    "sent_at": fields.Datetime.now(),
                    "provider_ref": result.get("provider_ref") or "",
                    "cost": provider.cost_per_message or 0.0,
                    "last_error": False,
                    "next_attempt_at": False,
                }
            )
            publish(
                self.env,
                "notification.sent",
                "fix.notif.delivery",
                self.id,
                {
                    "channel": self.channel,
                    "purpose": self.purpose,
                    "provider": provider.code,
                    "provider_ref": self.provider_ref,
                    "cost": self.cost,
                    "attempts": self.attempts,
                },
            )
            return True

        error = result.get("error") or "provider reported failure without a reason"

        if result.get("dry_run"):
            # Its own state, deliberately. Recording a dry run as 'sent'
            # would be exactly the lie this log exists to prevent, and
            # leaving it 'queued' would have the cron retry it forever.
            self.write(
                {
                    "state": "dry_run",
                    "last_error": error,
                    "next_attempt_at": False,
                    "cost": 0.0,
                }
            )
            return False

        if result.get("permanent"):
            # A policy refusal or a misconfiguration retrying cannot fix.
            self.write(
                {
                    "state": "failed",
                    "failed_at": fields.Datetime.now(),
                    "last_error": error,
                    "next_attempt_at": False,
                }
            )
            publish(
                self.env,
                "notification.failed",
                "fix.notif.delivery",
                self.id,
                {
                    "channel": self.channel,
                    "purpose": self.purpose,
                    "attempts": self.attempts,
                    "error": error,
                },
            )
            return False

        if self.attempts >= (self.max_attempts or 4):
            self.write(
                {
                    "state": "failed",
                    "failed_at": fields.Datetime.now(),
                    "last_error": error,
                    "next_attempt_at": False,
                }
            )
            publish(
                self.env,
                "notification.failed",
                "fix.notif.delivery",
                self.id,
                {
                    "channel": self.channel,
                    "purpose": self.purpose,
                    "attempts": self.attempts,
                    "error": error,
                },
            )
            return False

        backoff = RETRY_BACKOFF_MINUTES[min(self.attempts - 1, len(RETRY_BACKOFF_MINUTES) - 1)]
        self.write(
            {
                "last_error": error,
                "next_attempt_at": fields.Datetime.now() + timedelta(minutes=backoff),
            }
        )
        return False

    def sms_route(self):
        """The BD-01 route this message must use, derived from its purpose.

        BD-02: a marketing message never uses the registered masking sender.
        This is a regulatory consequence of the processing purpose, so it is
        derived rather than configured — a checkbox must not be able to put
        promotional traffic on the masking route.
        """
        self.ensure_one()
        return "non-masking" if self.purpose in NON_MASKING_PURPOSES else "masking"

    def _dispatch_via_provider(self, provider):
        """Hand the message to the estate's channel adapter. Returns a verdict.

        `int_gateway` delegates to services/notification-dispatcher's
        adapters — the ones that already carry INT-010/011 SMS with its
        masking rules, INT-012 WhatsApp, INT-013 e-mail and Novu push, all
        SSRF-guarded and refusing redirects. Writing a second HTTP client
        here would duplicate the one piece of this estate that was already
        finished.

        `odoo_mail` sends through the mail server the estate runs, for
        e-mail only. `manual` never sends by itself — an operator marks it,
        which is the real workflow on a low-volume channel and is honest
        about who did the work.
        """
        self.ensure_one()
        if provider.transport == "odoo_mail":
            if self.channel != "email":
                return {
                    "ok": False,
                    "error": "The Odoo mail transport carries e-mail only, not %s." % self.channel,
                }
            mail = (
                self.env["mail.mail"]
                .sudo()
                .create(
                    {
                        "email_to": self.to_address,
                        "subject": self.subject or "1000FiX Services",
                        "body_html": "<pre>%s</pre>" % (self.body or ""),
                        "auto_delete": False,
                    }
                )
            )
            mail.send(raise_exception=True)
            return {"ok": True, "provider_ref": "mail.mail:%d" % mail.id}

        if provider.transport == "int_gateway":
            return self._dispatch_via_estate_adapter(provider)

        return {
            "ok": False,
            "error": "Provider '%s' is manual: an operator must send this message "
            "and mark it sent." % provider.code,
            "permanent": True,
        }

    def _dispatch_via_estate_adapter(self, provider):
        """One send through the dispatcher's channel adapter."""
        self.ensure_one()
        adapters = _channel_adapters()
        if adapters is None:
            return {
                "ok": False,
                "error": "The notification-dispatcher service tree is not "
                "available to this process, so nothing was transmitted.",
            }
        class_name = ADAPTER_FOR_CHANNEL.get(self.channel)
        if not class_name:
            return {
                "ok": False,
                "error": "No estate adapter carries channel '%s'." % self.channel,
                "permanent": True,
            }
        adapter = getattr(adapters, class_name)()

        kwargs = {}
        if self.channel == "sms":
            route = self.sms_route()
            kwargs["sms_route"] = route
            # BD-03, checked here as well as in the adapter so the refusal
            # names the template rather than surfacing as a bare exception:
            # a numeric-sender message must not carry the masking signature.
            if route == "non-masking" and MASKING_SIGNATURE in (self.body or ""):
                return {
                    "ok": False,
                    "permanent": True,
                    "error": "BD-02/BD-03: this is promotional traffic, so it must "
                    "go on the non-masking (numeric sender) route, and a "
                    "non-masking message may not carry the registered '%s' "
                    "masking signature. Remove the signature from the message "
                    "body or template." % MASKING_SIGNATURE,
                }

        try:
            result = adapter.send(self.to_address, self.body or "", **kwargs)
        except adapters.SendRefused as exc:
            # A policy refusal is permanent: retrying an unlawful send would
            # just break the rule again on a timer.
            return {"ok": False, "permanent": True, "error": "Refused by channel policy: %s" % exc}

        if result.status == "delivered":
            return {"ok": True, "provider_ref": result.provider_id or ""}
        if result.status == "dry-run":
            return {
                "ok": False,
                "dry_run": True,
                "error": "Adapter ran in dry-run: %s. Nothing was transmitted, "
                "and this is NOT recorded as a send."
                % (result.detail or "gateway endpoint unconfigured"),
            }
        return {"ok": False, "error": result.detail or "adapter reported failure"}

    def action_mark_sent_manually(self, provider_ref=""):
        """For manual-transport channels: an operator confirms they sent it."""
        for rec in self:
            if not rec.provider_id or rec.provider_id.transport != "manual":
                raise UserError("Only a manual-transport message may be marked sent by hand.")
            rec.write(
                {
                    "state": "sent",
                    "sent_at": fields.Datetime.now(),
                    "provider_ref": provider_ref or ("manual:%s" % self.env.user.login),
                    "cost": rec.provider_id.cost_per_message or 0.0,
                    "attempts": max(rec.attempts, 1),
                }
            )
        return True

    # ------------------------------------------------------------------
    # Provider callbacks
    # ------------------------------------------------------------------
    def mark_delivered(self, provider_ref=None, delivered_at=None):
        """A provider receipt confirms the handset/mailbox received it.

        Separate from `sent` on purpose: the estate must never claim delivery
        it was not told about.
        """
        for rec in self:
            if rec.state not in ("sent", "delivered"):
                raise UserError(
                    "Only a message already sent can be marked delivered (this "
                    "one is %s)." % rec.state
                )
            rec.write(
                {
                    "state": "delivered",
                    "delivered_at": delivered_at or fields.Datetime.now(),
                    "provider_ref": provider_ref or rec.provider_ref,
                }
            )
            publish(
                self.env,
                "notification.delivered",
                "fix.notif.delivery",
                rec.id,
                {
                    "channel": rec.channel,
                    "purpose": rec.purpose,
                    "provider_ref": rec.provider_ref,
                    "partner_id": rec.partner_id.id or None,
                },
            )
        return True

    def mark_failed(self, error, permanent=True):
        """A provider reports the message could not be delivered."""
        for rec in self:
            rec.write(
                {
                    "state": "failed" if permanent else rec.state,
                    "failed_at": fields.Datetime.now() if permanent else rec.failed_at,
                    "last_error": error or "provider reported a delivery failure",
                    "next_attempt_at": False
                    if permanent
                    else fields.Datetime.now() + timedelta(minutes=RETRY_BACKOFF_MINUTES[0]),
                }
            )
        return True

    def action_cancel(self, reason=""):
        for rec in self:
            if rec.state in ("sent", "delivered"):
                raise UserError("A message already sent cannot be cancelled.")
            rec.write(
                {
                    "state": "cancelled",
                    "last_error": reason or "cancelled by %s" % self.env.user.name,
                    "next_attempt_at": False,
                }
            )
        return True

    # ------------------------------------------------------------------
    # Crons
    # ------------------------------------------------------------------
    @api.model
    def cron_dispatch_queue(self, limit=200):
        """Send what is due. One pass; the backoff ladder spaces retries.

        A message bound to a MANUAL provider is the operator's to send, so the
        queue leaves it alone. Attempting it failed it permanently within a
        minute of being queued - before any operator could act - which made
        manual transport (the estate's state until a CPaaS is contracted)
        unusable.
        """
        due = self.sudo().search(
            [
                ("state", "=", "queued"),
                "|",
                ("provider_id", "=", False),
                ("provider_id.transport", "!=", "manual"),
                "|",
                ("next_attempt_at", "=", False),
                ("next_attempt_at", "<=", fields.Datetime.now()),
            ],
            order="queued_at",
            limit=limit,
        )
        sent = 0
        for rec in due:
            # Each message gets its own savepoint: one bad recipient must not
            # roll back the whole batch.
            try:
                with self.env.cr.savepoint():
                    if rec._attempt():
                        sent += 1
            except Exception:
                _logger.exception("notif delivery %s raised outside _attempt", rec.id)
        return {"considered": len(due), "sent": sent}

    @api.model
    def cron_expire_stale_queued(self, older_than_hours=72):
        """Abandon messages that have sat unsendable for too long.

        A promotional message that could not go out for three days is no
        longer the message anyone authored; sending it late is worse than not
        sending it. Transactional purposes are left alone — a late order
        update is still useful.
        """
        cutoff = fields.Datetime.now() - timedelta(hours=older_than_hours)
        stale = self.sudo().search(
            [
                ("state", "=", "queued"),
                ("purpose", "in", list(fix_btrc.CURFEWED_PURPOSES)),
                ("queued_at", "<=", cutoff),
            ]
        )
        for rec in stale:
            rec.write(
                {
                    "state": "cancelled",
                    "last_error": "Abandoned: queued %s and still unsendable after "
                    "%d hours." % (rec.queued_at, older_than_hours),
                    "next_attempt_at": False,
                }
            )
        return len(stale)

    # ------------------------------------------------------------------
    # Unit economics — the question S1 was built to answer
    # ------------------------------------------------------------------
    @api.model
    def delivery_cost_summary(self, date_from=None, date_to=None):
        """Per-channel message counts and charged cost over a window.

        Counts are of ROWS, which is the honest basis: a suppressed message
        costs nothing and is reported separately from one that was sent, and
        neither is mixed into a single "messages" figure.
        """
        domain = []
        if date_from:
            domain.append(("queued_at", ">=", date_from))
        if date_to:
            domain.append(("queued_at", "<=", date_to))
        # Every state in the field's own selection gets a column, derived
        # rather than listed. An earlier version listed five states by hand
        # and counted the rest nowhere, so adding the 'dry_run' state made a
        # row's cost count while its tally vanished and the columns stopped
        # summing to the row total. A report whose parts do not add up is
        # worse than no report.
        all_states = [key for key, _label in self._fields["state"].selection]
        rows = {}
        for rec in self.sudo().search(domain):
            bucket = rows.setdefault(
                rec.channel,
                dict(
                    {"channel": rec.channel, "messages": 0, "cost": 0.0},
                    **{state: 0 for state in all_states},
                ),
            )
            bucket["messages"] += 1
            # setdefault guards a row written before a state was retired.
            bucket.setdefault(rec.state, 0)
            bucket[rec.state] += 1
            bucket["cost"] += rec.cost or 0.0
        for bucket in rows.values():
            billable = bucket["sent"] + bucket["delivered"]
            bucket["cost_per_billable"] = round(bucket["cost"] / billable, 4) if billable else None
        return sorted(rows.values(), key=lambda r: r["channel"])

    @api.model
    def language_coverage(self, date_from=None, date_to=None):
        """How many Bengali-preferring recipients actually got Bengali.

        The DE-17 measurement the estate could not previously take. A row
        where the party prefers Bengali and `language` is 'en' is a template
        with no Bengali copy, named by channel and purpose so it can be
        fixed rather than discussed.
        """
        domain = [("state", "in", ("sent", "delivered"))]
        if date_from:
            domain.append(("queued_at", ">=", date_from))
        if date_to:
            domain.append(("queued_at", "<=", date_to))
        rows = {}
        for rec in self.sudo().search(domain):
            wanted = self._preferred_language(rec.partner_id)
            bucket = rows.setdefault(
                (rec.channel, rec.purpose),
                {
                    "channel": rec.channel,
                    "purpose": rec.purpose,
                    "messages": 0,
                    "bengali_wanted": 0,
                    "bengali_sent": 0,
                    "fell_back_to_english": 0,
                },
            )
            bucket["messages"] += 1
            if wanted == "bn":
                bucket["bengali_wanted"] += 1
                if rec.language == "bn":
                    bucket["bengali_sent"] += 1
                else:
                    bucket["fell_back_to_english"] += 1
        for bucket in rows.values():
            wanted = bucket["bengali_wanted"]
            bucket["bengali_coverage_pct"] = (
                round(100.0 * bucket["bengali_sent"] / wanted, 1) if wanted else None
            )
        return sorted(rows.values(), key=lambda r: (r["channel"], r["purpose"]))

    @api.model
    def suppression_reasons(self, date_from=None, date_to=None):
        """Why messages were NOT sent, grouped. The compliance evidence."""
        domain = [("state", "=", "suppressed")]
        if date_from:
            domain.append(("queued_at", ">=", date_from))
        if date_to:
            domain.append(("queued_at", "<=", date_to))
        counts = {}
        for rec in self.sudo().search(domain):
            key = (rec.channel, rec.purpose, rec.consent_decision or "unknown")
            counts[key] = counts.get(key, 0) + 1
        return [
            {"channel": c, "purpose": p, "decision": d, "messages": n}
            for (c, p, d), n in sorted(counts.items(), key=lambda kv: -kv[1])
        ]

    def write(self, vals):
        """A send that already happened is evidence and does not get rewritten.

        The body, recipient, purpose and lawful basis of a message that left
        the estate are what we told the subscriber and what we relied on to
        tell them. Editing them afterwards would make the log worthless as
        evidence, which is the only reason the log exists.
        """
        frozen = {"to_address", "body", "subject", "purpose", "lawful_basis", "partner_id"}
        touched = frozen & set(vals)
        if touched:
            for rec in self:
                if rec.state in ("sent", "delivered"):
                    raise UserError(
                        "Cannot change %s on a message already %s — the delivery "
                        "log is evidence of what was sent."
                        % (", ".join(sorted(touched)), rec.state)
                    )
        return super().write(vals)

    def unlink(self):
        for rec in self:
            if rec.state in ("sent", "delivered"):
                raise UserError(
                    "A message that was sent cannot be deleted from the delivery "
                    "log. Cancel or supersede it instead."
                )
        return super().unlink()
