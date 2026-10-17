# cd_contact_centre — M27 Omnichannel Contact Centre + M32 Conversational AI
# (P07-M05, CD-M27-nn/CD-M32-nn). The notification half shipped in W1
# (ADR-022); this is the CONVERSATION half: unified channels, transcripts,
# the customer-360 view, and the M32 assistant's transactional intents with
# clean human handoff (G4-04/G4-05).
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish  # FF-28

CHANNELS = [
    ("voice", "Voice (Hotline 16743)"),
    ("whatsapp", "WhatsApp"),
    ("chat", "Web Chat"),
    ("email", "Email"),
    ("in_app", "In-App"),
]


class FixConversation(models.Model):
    """One conversation on any channel, with its transcript. G4-04: hotline
    conversations captured in the system of record — the transcript IS the
    record. SC-003: transcripts exist for SERVICE; mining them for training
    needs a confirmed legal basis first (the flag enforces the pause)."""

    _name = "fix.conversation"
    _description = "Conversation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "started_at desc, id desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    channel = fields.Selection(CHANNELS, required=True, default="voice",
                               tracking=True)
    customer_id = fields.Many2one("res.partner", string="Customer", index=True,
                                  ondelete="set null")
    contact_identity = fields.Char(
        string="Contact Identity",
        help="The caller's number / WhatsApp JID / email — the join key when "
             "the party is not yet identified")
    state = fields.Selection(
        [("new", "New"), ("with_ai", "With AI Assistant"), ("with_agent", "With Agent"),
         ("resolved_ai", "Resolved by AI"), ("resolved_agent", "Resolved by Agent"),
         ("abandoned", "Abandoned")],
        default="new", required=True, tracking=True)
    started_at = fields.Datetime(default=fields.Datetime.now, required=True)
    ended_at = fields.Datetime(readonly=True)
    turn_ids = fields.One2many("fix.conversation.turn", "conversation_id",
                               string="Transcript")
    # M32 assistant fields
    ai_resolved = fields.Boolean(readonly=True, copy=False,
                                 help="G4-05: resolved by the assistant without an agent")
    handoff_reason = fields.Char(readonly=True)
    intent = fields.Char(index=True,
                         help="The classified transactional intent (bn/en)")
    call_sid = fields.Char(string="Call SID", index=True,
                           help="Telephony session identifier from CPaaS (INT-015)")
    pii_masked = fields.Boolean(string="PII Masked", default=False,
                                help="SC-003: transcript masked for offline mining")

    def action_handoff_to_agent(self, reason: str = ""):
        """T07: the human-handoff path with FULL context transfer — the
        agent sees the entire transcript, the intent and the customer 360."""
        for conversation in self:
            conversation.write({"state": "with_agent", "handoff_reason": reason})
            publish(self.env, "conversation.handed_off", "fix.conversation",
                    conversation.id, {
                        "channel": conversation.channel,
                        "intent": conversation.intent,
                        "reason": reason,
                        "turns": len(conversation.turn_ids),
                    })

    def action_resolve(self, by_ai: bool):
        for conversation in self:
            conversation.write({
                "state": "resolved_ai" if by_ai else "resolved_agent",
                "ai_resolved": by_ai,
                "ended_at": fields.Datetime.now(),
            })
            publish(self.env, "conversation.resolved", "fix.conversation",
                    conversation.id, {"by_ai": by_ai, "intent": conversation.intent})

    @api.model
    def resolution_rate(self) -> float:
        """G4-05 measured the honest way: AI resolutions against FIRST
        CONTACTS with handoffs (not against total sessions)."""
        ai = self.search_count([("ai_resolved", "=", True)])
        handoffs = self.search_count([("handoff_reason", "!=", False)])
        total = ai + handoffs
        return round(100.0 * ai / total, 2) if total else 0.0

    @api.model
    def intake_hotline_call(self, caller_phone: str, call_sid: str = "",
                            initial_utterance: str = "", lang: str = "bn"):
        """INT-015: Inbound call on Hotline 16743 creates conversation in record (G4-04)."""
        partner = self.env["res.partner"].search([("phone", "=", caller_phone)], limit=1)
        ou = self.env["operating.unit"].search([], limit=1)
        conv = self.create({
            "channel": "voice",
            "contact_identity": caller_phone,
            "call_sid": call_sid,
            "customer_id": partner.id if partner else False,
            "operating_unit_id": ou.id if ou else False,
            "state": "with_ai",
            "started_at": fields.Datetime.now(),
        })
        greeting_bn = "১০০০ফিক্স কাস্টমার কেয়ারে আপনাকে স্বাগতম। আপনি কিভাবে সাহায্য চান?"
        greeting_en = "Welcome to 1000FiX Customer Care. How can we assist you today?"
        self.env["fix.conversation.turn"].create({
            "conversation_id": conv.id,
            "sequence": 10,
            "speaker": "ai",
            "text": greeting_bn if lang == "bn" else greeting_en,
            "lang": lang,
        })
        publish(self.env, "conversation.hotline_captured", "fix.conversation",
                conv.id, {
                    "channel": "voice",
                    "caller": caller_phone,
                    "call_sid": call_sid,
                })
        if initial_utterance:
            conv.intake_message(initial_utterance, speaker="customer", lang=lang)
        return conv

    def intake_message(self, text: str, speaker: str = "customer", lang: str = "bn"):
        """Records a transcript turn and triggers transactional AI dialogue management."""
        for conv in self:
            seq = (max(conv.turn_ids.mapped("sequence"), default=0) + 10) if conv.turn_ids else 10
            self.env["fix.conversation.turn"].create({
                "conversation_id": conv.id,
                "sequence": seq,
                "speaker": speaker,
                "text": text,
                "lang": lang,
            })
            if speaker == "customer" and conv.state in ("new", "with_ai"):
                from .assistant_engine import default_assistant_engine
                res = default_assistant_engine.classify_intent(text)
                conv.write({"intent": res.matched_intent or ""})
                reply = res.response_text_bn if lang == "bn" else res.response_text_en
                self.env["fix.conversation.turn"].create({
                    "conversation_id": conv.id,
                    "sequence": seq + 10,
                    "speaker": "ai",
                    "text": reply,
                    "lang": lang,
                })
                if res.resolvable:
                    conv.action_resolve(by_ai=True)
                elif res.requires_handoff:
                    conv.action_handoff_to_agent(reason=res.handoff_reason or "escalation")

    def mask_pii_for_mining(self) -> bool:
        """SC-003 DPIA requirement: Masks customer PII prior to offline mining."""
        import re
        for conv in self:
            for turn in conv.turn_ids:
                masked = re.sub(r"(\+?880?|0)1[3-9]\d{8}", "[PHONE_MASKED]", turn.text)
                masked = re.sub(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[EMAIL_MASKED]", masked)
                masked = re.sub(r"\b\d{10}\b|\b\d{17}\b", "[NID_MASKED]", masked)
                turn.write({"text": masked})
            conv.write({"pii_masked": True})
        return True


class FixConversationTurn(models.Model):
    """One turn in the transcript — who spoke, what was said, in which
    language. Transcript storage is the system of record (T04)."""

    _name = "fix.conversation.turn"
    _description = "Conversation Turn"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "conversation_id, sequence, id"

    conversation_id = fields.Many2one("fix.conversation", required=True,
                                      ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    speaker = fields.Selection(
        [("customer", "Customer"), ("ai", "AI Assistant"), ("agent", "Agent")],
        required=True)
    text = fields.Text(required=True)
    lang = fields.Selection([("bn", "বাংলা"), ("en", "English")], default="bn")
    spoken_at = fields.Datetime(default=fields.Datetime.now, readonly=True)


class FixAssistantIntent(models.Model):
    """CD-M32-02: the TRANSACTIONAL intent register (T06: transactional
    only — the M61 knowledge base is W6, an already-ratified scope cut).
    T08: Bengali utterances are authored, never machine-translated."""

    _name = "fix.assistant.intent"
    _description = "Assistant Intent (transactional)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _code_unique = models.Constraint('UNIQUE (code)', 'Intent code must be unique')

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    code = fields.Char(required=True, size=32,
                       help="e.g. order.status, invoice.download, appointment.book")
    name = fields.Char(required=True)
    name_bn = fields.Char(string="Name (Bengali)", required=True,
                          help="DE-17 + T08: authored Bengali, never machine-translated")
    description = fields.Text()
    sample_bn = fields.Text(string="Bengali Utterances", required=True,
                            help="Real Bengali utterances, one per line — the "
                                 "NLU test corpus (T08)")
    sample_en = fields.Text(string="English Utterances")
    grounding = fields.Char(
        string="Grounding (live ERP data)",
        help="CD-M32-03: the live source this intent answers from — e.g. "
             "fix.service.order.tracking_ref via the party")
    handoff_on_failure = fields.Boolean(
        default=True,
        help="T07: an intent the assistant cannot resolve hands off with full "
             "context rather than dead-ending")
    active = fields.Boolean(default=True)
