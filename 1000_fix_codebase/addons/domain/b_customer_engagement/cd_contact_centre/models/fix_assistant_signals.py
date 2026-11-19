# M32 capture audit, pass 3 (19 Nov 2026): the two gaps pass 2 reported as
# open that are capture work, not new engines.
#
#   7 Handoff Decision  fix.assistant.signal.phrase: what a customer says that
#                       means distress or a safety risk, abuse, an explicit
#                       request for a human, or frustration (FR-CAI-004/034,
#                       FR-CAI-036 emotional signals, BRU-CAI-06/07,
#                       AUT-CAI-04/05). Pass 1 made the emotional triggers
#                       tunable, but nothing ever raised them. The live bot
#                       now checks every customer message against this register
#                       BEFORE classification and hands off at once through
#                       the trigger table (distress: Urgent, supervisors
#                       alerted).
#   9 Analytics         AUT-CAI-08 "session ends without resolution: log to the
#                       unresolved queue". A conversation the customer
#                       abandons after the assistant spoke is logged too.
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from libs.py.fix_events import publish  # FF-28

from .assistant_engine import TRANSFER_REPLY, normalize_text

_logger = logging.getLogger(__name__)

PHRASE_SIGNALS = [
    ("distress", "Distress, vulnerability or a safety risk"),
    ("abusive", "Abusive or unsafe content"),
    ("explicit_request", "Explicit request for a human"),
    ("frustration", "Frustration"),
]
# When one message matches several, the most serious wins.
PRECEDENCE = ("distress", "abusive", "explicit_request", "frustration")
# BRU-CAI-06/07: phrases for these signals are never removed by their author
# alone (the SOD-20 pattern the guard rails follow).
PROTECTED = frozenset({"distress", "explicit_request"})
MIN_PHRASE = 3
# The handoff reason the conversation records. An explicit request keeps the
# reason M27 and its reports already use (the agent.request intent writes it);
# the trigger table maps it to the explicit_request signal.
HANDOFF_REASON = {"explicit_request": "customer_requested_agent"}


class FixAssistantSignalPhrase(models.Model):
    """A phrase that, said by a customer, hands the conversation to a person."""

    _name = "fix.assistant.signal.phrase"
    _description = "Assistant Handoff Signal Phrase"
    _inherit = ["mail.thread"]
    _order = "signal, phrase"
    _rec_name = "phrase"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    signal = fields.Selection(PHRASE_SIGNALS, required=True, tracking=True)
    phrase = fields.Char(
        required=True,
        tracking=True,
        help="Matched as whole words after the assistant's own normalisation "
        "(case, punctuation and Bengali spelling variants). Bengali phrases are "
        "authored by a native speaker (T08).",
    )
    normalised = fields.Char(compute="_compute_normalised", store=True, index=True)
    language = fields.Selection(
        [("any", "Any"), ("bn", "Bengali"), ("en", "English")], required=True, default="any"
    )
    note = fields.Char(string="Why / Owner Note")
    active = fields.Boolean(default=True, tracking=True)

    _phrase_unique = models.Constraint(
        "UNIQUE (company_id, signal, normalised)", "This phrase is already registered."
    )

    @api.depends("phrase")
    def _compute_normalised(self):
        for rec in self:
            rec.normalised = normalize_text(rec.phrase or "")

    @api.constrains("phrase")
    def _check_phrase(self):
        for rec in self:
            norm = rec.normalised or ""
            if len(norm) < MIN_PHRASE or not any(ch.isalpha() for ch in norm):
                raise ValidationError(
                    _(
                        "A signal phrase needs at least %d letters: a shorter one would hand "
                        "off ordinary messages."
                    )
                    % MIN_PHRASE
                )

    # --- SOD-20 pattern: a protected phrase leaves only by another supervisor
    def _check_removal_by_another(self):
        if self.env.su:
            return
        mine = self.filtered(lambda r: r.signal in PROTECTED and r.create_uid == self.env.user)
        if mine:
            raise ValidationError(
                _(
                    "BRU-CAI-06/07: you added the %(sig)s phrase '%(p)s', so another "
                    "supervisor must remove it."
                )
                % {"sig": dict(PHRASE_SIGNALS)[mine[0].signal], "p": mine[0].phrase}
            )

    def write(self, vals):
        if ("active" in vals and not vals["active"]) or (
            "signal" in vals and vals["signal"] not in PROTECTED
        ):
            self.filtered("active")._check_removal_by_another()
        return super().write(vals)

    def unlink(self):
        self._check_removal_by_another()
        return super().unlink()

    @api.model
    def detect(self, text):
        """The most serious signal a message carries, or None.

        Returns {"signal", "phrase_id"}."""
        norm = " %s " % normalize_text(text or "")
        if not norm.strip():
            return None
        rows = self.sudo().search([("company_id", "in", self.env.companies.ids)])
        hits = {}
        for row in rows:
            if row.normalised and (" %s " % row.normalised) in norm:
                hits.setdefault(row.signal, row)
        for signal in PRECEDENCE:
            if signal in hits:
                return {"signal": signal, "phrase_id": hits[signal].id}
        return None


class FixConversationSignals(models.Model):
    _inherit = "fix.conversation"

    def intake_message(self, text: str, speaker: str = "customer", lang: str = "bn"):
        """AUT-CAI-04/05: a distress, abuse, explicit-request or frustration
        phrase hands off on the same turn, before any classification or
        generation, through the handoff trigger table."""
        hit = None
        if speaker == "customer":
            hit = self.env["fix.assistant.signal.phrase"].detect(text)
        if not hit:
            return super().intake_message(text, speaker=speaker, lang=lang)
        Turn = self.env["fix.conversation.turn"]
        for conv in self:
            if conv.state not in ("new", "with_ai"):
                # already with a person: record the turn as usual
                super(FixConversationSignals, conv).intake_message(text, speaker=speaker, lang=lang)
                continue
            conv._route_contact()
            seq = max(conv.turn_ids.mapped("sequence"), default=0) + 10
            Turn.create(
                {
                    "conversation_id": conv.id,
                    "sequence": seq,
                    "speaker": "customer",
                    "text": text,
                    "lang": lang,
                }
            )
            Turn.create(
                {
                    "conversation_id": conv.id,
                    "sequence": seq + 10,
                    "speaker": "ai",
                    "text": TRANSFER_REPLY["bn" if lang == "bn" else "en"],
                    "lang": lang,
                }
            )
            publish(
                self.env,
                "sentiment.detected",
                "fix.conversation",
                conv.id,
                {
                    "signal": hit["signal"],
                    "phrase_id": hit["phrase_id"],
                    "party": conv.customer_id.id or None,
                },
            )
            conv.action_handoff_to_agent(reason=HANDOFF_REASON.get(hit["signal"], hit["signal"]))
        return None

    def _mark_abandoned(self):
        """AUT-CAI-08: a session the assistant took part in that ends without
        resolution goes to the unresolved queue for review."""
        engaged = self.filtered(
            lambda c: c.state not in self._CLOSED_STATES
            and any(t.speaker == "customer" for t in c.turn_ids)
            and any(t.speaker == "ai" for t in c.turn_ids)
        )
        res = super()._mark_abandoned()
        for conv in engaged:
            try:
                conv._log_unresolved("session_abandoned", signal="abandoned")
            except Exception:  # abandoning the call must never fail on the log
                _logger.exception("Could not log abandoned conversation %s", conv.id)
        return res
