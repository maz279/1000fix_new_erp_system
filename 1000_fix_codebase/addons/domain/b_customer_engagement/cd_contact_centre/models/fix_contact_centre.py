# cd_contact_centre — M27 Omnichannel Contact Centre + M32 Conversational AI
# (P07-M05, CD-M27-nn/CD-M32-nn). The notification half shipped in W1
# (ADR-022); this is the CONVERSATION half: unified channels, transcripts,
# the customer-360 view, and the M32 assistant's transactional intents with
# clean human handoff (G4-04/G4-05).
from odoo import api, fields, models
from odoo.exceptions import AccessError

from libs.py.fix_events import publish  # FF-28

from .assistant_engine import ORDER_STATE_TEXT, normalize_text

# Words that name the KIND of place, not WHICH branch: ignored when matching a
# branch the customer mentions ("Dhanmondi service centre" -> "dhanmondi").
_BRANCH_GENERIC_WORDS = {
    "1000fix",
    "branch",
    "centre",
    "center",
    "service",
    "services",
    "point",
    "outlet",
    "depot",
    "repair",
    "shop",
    "office",
    "শাখা",
    "সার্ভিস",
    "সেন্টার",
    "ব্রাঞ্চ",
    "পয়েন্ট",
    "১০০০ফিক্স",
}


def _answer(bn: str, en: str, grounded: bool, reason: str = "") -> dict:
    return {"bn": bn, "en": en, "grounded": grounded, "reason": reason}


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

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    channel = fields.Selection(CHANNELS, required=True, default="voice", tracking=True)
    customer_id = fields.Many2one("res.partner", string="Customer", index=True, ondelete="set null")
    contact_identity = fields.Char(
        string="Contact Identity",
        help="The caller's number / WhatsApp JID / email — the join key when "
        "the party is not yet identified",
    )
    state = fields.Selection(
        [
            ("new", "New"),
            ("with_ai", "With AI Assistant"),
            ("with_agent", "With Agent"),
            ("resolved_ai", "Resolved by AI"),
            ("resolved_agent", "Resolved by Agent"),
            ("abandoned", "Abandoned"),
        ],
        default="new",
        required=True,
        tracking=True,
    )
    started_at = fields.Datetime(default=fields.Datetime.now, required=True)
    ended_at = fields.Datetime(readonly=True)
    turn_ids = fields.One2many("fix.conversation.turn", "conversation_id", string="Transcript")
    # M32 assistant fields
    ai_resolved = fields.Boolean(
        readonly=True, copy=False, help="G4-05: resolved by the assistant without an agent"
    )
    handoff_reason = fields.Char(readonly=True)
    intent = fields.Char(index=True, help="The classified transactional intent (bn/en)")
    call_sid = fields.Char(
        string="Call SID", index=True, help="Telephony session identifier from CPaaS (INT-015)"
    )
    pii_masked = fields.Boolean(
        string="PII Masked", default=False, help="SC-003: transcript masked for offline mining"
    )

    def action_handoff_to_agent(self, reason: str = ""):
        """T07: the human-handoff path with FULL context transfer — the
        agent sees the entire transcript, the intent and the customer 360."""
        for conversation in self:
            conversation.write({"state": "with_agent", "handoff_reason": reason})
            publish(
                self.env,
                "conversation.handed_off",
                "fix.conversation",
                conversation.id,
                {
                    "channel": conversation.channel,
                    "intent": conversation.intent,
                    "reason": reason,
                    "turns": len(conversation.turn_ids),
                },
            )

    def action_resolve(self, by_ai: bool):
        for conversation in self:
            conversation.write(
                {
                    "state": "resolved_ai" if by_ai else "resolved_agent",
                    "ai_resolved": by_ai,
                    "ended_at": fields.Datetime.now(),
                }
            )
            publish(
                self.env,
                "conversation.resolved",
                "fix.conversation",
                conversation.id,
                {"by_ai": by_ai, "intent": conversation.intent},
            )

    @api.model
    def resolution_rate(self) -> float:
        """G4-05 measured the honest way: AI resolutions against FIRST
        CONTACTS with handoffs (not against total sessions)."""
        ai = self.search_count([("ai_resolved", "=", True)])
        handoffs = self.search_count([("handoff_reason", "!=", False)])
        total = ai + handoffs
        return round(100.0 * ai / total, 2) if total else 0.0

    @api.model
    def intake_hotline_call(
        self, caller_phone: str, call_sid: str = "", initial_utterance: str = "", lang: str = "bn"
    ):
        """INT-015: Inbound call on Hotline 16743 creates conversation in record (G4-04)."""
        partner = self.env["res.partner"].search([("phone", "=", caller_phone)], limit=1)
        ou = self.env["operating.unit"].search([], limit=1)
        conv = self.create(
            {
                "channel": "voice",
                "contact_identity": caller_phone,
                "call_sid": call_sid,
                "customer_id": partner.id if partner else False,
                "operating_unit_id": ou.id if ou else False,
                "state": "with_ai",
                "started_at": fields.Datetime.now(),
            }
        )
        greeting_bn = "১০০০ফিক্স কাস্টমার কেয়ারে আপনাকে স্বাগতম। আপনি কিভাবে সাহায্য চান?"
        greeting_en = "Welcome to 1000FiX Customer Care. How can we assist you today?"
        self.env["fix.conversation.turn"].create(
            {
                "conversation_id": conv.id,
                "sequence": 10,
                "speaker": "ai",
                "text": greeting_bn if lang == "bn" else greeting_en,
                "lang": lang,
            }
        )
        publish(
            self.env,
            "conversation.hotline_captured",
            "fix.conversation",
            conv.id,
            {
                "channel": "voice",
                "caller": caller_phone,
                "call_sid": call_sid,
            },
        )
        if initial_utterance:
            conv.intake_message(initial_utterance, speaker="customer", lang=lang)
        return conv

    def intake_message(self, text: str, speaker: str = "customer", lang: str = "bn"):
        """Records a transcript turn and triggers transactional AI dialogue management."""
        for conv in self:
            seq = (max(conv.turn_ids.mapped("sequence"), default=0) + 10) if conv.turn_ids else 10
            self.env["fix.conversation.turn"].create(
                {
                    "conversation_id": conv.id,
                    "sequence": seq,
                    "speaker": speaker,
                    "text": text,
                    "lang": lang,
                }
            )
            if speaker == "customer" and conv.state in ("new", "with_ai"):
                from .assistant_engine import default_assistant_engine

                res = default_assistant_engine.classify_intent(text)
                conv.write({"intent": res.matched_intent or ""})
                resolvable = res.resolvable
                handoff_reason = res.handoff_reason
                reply = res.response_text_bn if lang == "bn" else res.response_text_en
                if getattr(res, "requires_grounding", False):
                    # Transactional intent: answer ONLY from the customer's
                    # live records; anything not grounded hands off (G4-05:
                    # only a grounded answer counts as an AI resolution).
                    answer = conv._ground_intent_response(res.matched_intent, text)
                    resolvable = answer["grounded"]
                    handoff_reason = answer["reason"]
                    reply = answer["bn"] if lang == "bn" else answer["en"]
                self.env["fix.conversation.turn"].create(
                    {
                        "conversation_id": conv.id,
                        "sequence": seq + 10,
                        "speaker": "ai",
                        "text": reply,
                        "lang": lang,
                    }
                )
                if resolvable:
                    conv.action_resolve(by_ai=True)
                else:
                    # T07: an unresolved turn always hands off - never a dead end
                    conv.action_handoff_to_agent(reason=handoff_reason or "escalation")

    # --- M32 grounding: transactional answers from live ERP records -----------------

    def _ground_intent_response(self, intent: str, text: str) -> dict:
        """Answer a transactional intent from the customer's real records.

        Returns {"bn", "en", "grounded", "reason"}. ``grounded`` is True only
        when the reply states facts read from records; otherwise the reply is
        guidance and ``reason`` is the handoff reason. Nothing here claims an
        action (booking, invoice dispatch) that was not performed."""
        self.ensure_one()
        handlers = {
            "order.status": self._ground_order_status,
            "repair.price_estimate": self._ground_price_estimate,
            "branch.locator": self._ground_branch_locator,
            "appointment.book": self._ground_appointment_book,
            "invoice.download": self._ground_invoice_download,
        }
        handler = handlers.get(intent)
        if not handler:
            return _answer(
                "আপনার প্রশ্নের নির্ভুল উত্তরের জন্য একজন কাস্টমার কেয়ার প্রতিনিধির সাথে যুক্ত করছি।",
                "Connecting you with a customer care specialist to assist you accurately.",
                False,
                "no_grounding_source",
            )
        try:
            return handler(text)
        except AccessError:
            return _answer(
                "আপনার তথ্য যাচাই করতে একজন কাস্টমার কেয়ার প্রতিনিধির সাথে যুক্ত করছি।",
                "Connecting you with a customer care representative to check your records.",
                False,
                "grounding_access_denied",
            )

    def _ground_order_status(self, text: str) -> dict:
        if "fix.service.order" not in self.env:
            return _answer(
                "অর্ডারের অবস্থা জানাতে একজন প্রতিনিধির সাথে যুক্ত করছি।",
                "Connecting you with a representative to check your order status.",
                False,
                "order_source_unavailable",
            )
        if not self.customer_id:
            # An unidentified contact never gets anyone's order status: the
            # agent verifies identity against the order reference.
            return _answer(
                "আপনার পরিচয় যাচাই করা যায়নি। অনুগ্রহ করে আপনার সার্ভিস অর্ডার নম্বরটি প্রস্তুত রাখুন, "
                "একজন প্রতিনিধি আপনার সাথে যুক্ত হচ্ছেন।",
                "We could not identify your account. Please keep your service order reference "
                "ready; connecting you with a representative.",
                False,
                "order_reference_required",
            )
        orders = self.env["fix.service.order"].search(
            [("customer_id", "=", self.customer_id.id)], order="create_date desc, id desc"
        )
        if not orders:
            return _answer(
                "আপনার নামে কোনো সার্ভিস অর্ডার পাওয়া যায়নি। একজন প্রতিনিধির সাথে যুক্ত করছি।",
                "We found no service order under your account. Connecting you with a "
                "representative.",
                False,
                "no_order_found",
            )
        lowered = (text or "").lower()
        # The order the customer names (by reference), else their latest one.
        order = next((o for o in orders if o.name and o.name.lower() in lowered), orders[0])
        state_bn, state_en = ORDER_STATE_TEXT.get(
            order.state, (order.state or "অজানা", order.state or "unknown")
        )
        device = order.device_id.display_name or ""
        suffix = " (%s)" % device if device else ""
        return _answer(
            "আপনার সার্ভিস অর্ডার %s%s: %s।" % (order.name, suffix, state_bn),
            "Your service order %s%s: %s." % (order.name, suffix, state_en),
            True,
        )

    def _ground_price_estimate(self, text: str) -> dict:
        """Quote a standard (tier-0, non-contract, in-validity) rate-card line
        only when the utterance names exactly one priced catalogue product;
        otherwise an agent confirms the price."""
        agent_confirms = _answer(
            "সঠিক খরচ ডিভাইস ও সমস্যার উপর নির্ভর করে — একজন প্রতিনিধি আপনাকে খরচ নিশ্চিত করবেন।",
            "The exact cost depends on the device and fault — a representative will confirm "
            "the price for you.",
            False,
            "price_requires_agent",
        )
        if "fix.rate.card" not in self.env or "product.product" not in self.env:
            return agent_confirms
        today = fields.Date.context_today(self)
        cards = self.env["fix.rate.card"].search(
            [
                ("min_tier", "=", 0),
                ("contract_no", "=", False),
                "|",
                ("valid_from", "=", False),
                ("valid_from", "<=", today),
                "|",
                ("valid_to", "=", False),
                ("valid_to", ">=", today),
            ]
        )
        if not cards:
            return agent_confirms
        products = self.env["product.product"].search(
            [("default_code", "in", cards.mapped("product_code"))]
        )
        has_bn = "name_bn" in products._fields
        norm = normalize_text(text)
        matches = products.browse()
        for product in products:
            names = [product.name, product.name_bn if has_bn else ""]
            if any(normalize_text(n or "") and normalize_text(n) in norm for n in names):
                matches |= product
        if len(matches) != 1:
            return agent_confirms
        card = cards.filtered(lambda c: c.product_code == matches.default_code)[:1]
        name_bn = (matches.name_bn if has_bn else "") or matches.name
        return _answer(
            "%s এর স্ট্যান্ডার্ড রেট: %.2f টাকা (ভ্যাট ব্যতীত)। চূড়ান্ত খরচ ডায়াগনস্টিকের পর নিশ্চিত করা হবে।"
            % (name_bn, card.unit_price),
            "Standard rate for %s: BDT %.2f (VAT-exclusive). The final cost is confirmed "
            "after diagnosis." % (matches.name, card.unit_price),
            True,
        )

    def _ground_branch_locator(self, text: str) -> dict:
        """Answer from the fix.branch record the customer names (branch name or
        its upazila); several or no matches go to an agent."""
        ask_agent = _answer(
            "কোন এলাকার শাখা জানতে চান তা নিশ্চিত করতে একজন প্রতিনিধির সাথে যুক্ত করছি।",
            "Connecting you with a representative to confirm which branch you are looking for.",
            False,
            "branch_not_identified",
        )
        if "fix.branch" not in self.env:
            return ask_agent
        tokens = set(normalize_text(text).split())
        matched = self.env["fix.branch"]
        for branch in self.env["fix.branch"].search([]):
            keys = set()
            for label in (
                branch.name,
                branch.name_bn,
                branch.address_id.upazila,
                branch.address_id.upazila_bn,
            ):
                keys |= set(normalize_text(label or "").split())
            keys -= _BRANCH_GENERIC_WORDS
            if any(len(k) >= 3 and k in tokens for k in keys):
                matched |= branch
        if len(matched) != 1:
            return ask_agent
        addr = matched.address_id
        addr_en = ", ".join(
            p for p in (addr.house, addr.street, addr.upazila, addr.district, addr.postcode) if p
        )
        addr_bn = addr.display_name if addr else ""
        if not (addr_en or matched.phone):
            return ask_agent
        phone_bn = " ফোন: %s।" % matched.phone if matched.phone else ""
        phone_en = " Phone: %s." % matched.phone if matched.phone else ""
        return _answer(
            "%s: %s।%s" % (matched.name_bn or matched.name, addr_bn or "ঠিকানা নথিভুক্ত নেই", phone_bn),
            "%s: %s.%s" % (matched.name, addr_en or "address not on record", phone_en),
            True,
        )

    def _ground_appointment_book(self, text: str) -> dict:
        # The assistant performs no booking: it must not say one was made.
        return _answer(
            "টেকনিশিয়ান ভিজিটের সময় নির্ধারণ করতে একজন প্রতিনিধির সাথে যুক্ত করছি। "
            "বুকিং নিশ্চিত হলে আপনাকে জানানো হবে।",
            "Connecting you with a representative to schedule the technician visit. "
            "You will be told once the booking is confirmed.",
            False,
            "appointment_requires_agent",
        )

    def _ground_invoice_download(self, text: str) -> dict:
        # Nothing is sent from here: guidance plus an agent, never "dispatched".
        return _answer(
            "আপনার ইনভয়েস ও মুশক ৬.৩ চালান কাস্টমার পোর্টালের ইনভয়েস অংশ থেকে ডাউনলোড করা যায়। "
            "কপি পাঠাতে একজন প্রতিনিধির সাথে যুক্ত করছি।",
            "Your invoices and Mushak 6.3 copies can be downloaded from the Invoices section "
            "of the customer portal. Connecting you with a representative to send a copy.",
            False,
            "invoice_requires_agent",
        )

    def mask_pii_for_mining(self) -> bool:
        """SC-003 DPIA requirement: Masks customer PII prior to offline mining."""
        import re

        for conv in self:
            for turn in conv.turn_ids:
                masked = re.sub(r"(\+?880?|0)1[3-9]\d{8}", "[PHONE_MASKED]", turn.text)
                masked = re.sub(
                    r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[EMAIL_MASKED]", masked
                )
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

    conversation_id = fields.Many2one(
        "fix.conversation", required=True, ondelete="cascade", index=True
    )
    sequence = fields.Integer(default=10)
    speaker = fields.Selection(
        [("customer", "Customer"), ("ai", "AI Assistant"), ("agent", "Agent")], required=True
    )
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
    _code_unique = models.Constraint("UNIQUE (code)", "Intent code must be unique")

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    code = fields.Char(
        required=True, size=32, help="e.g. order.status, invoice.download, appointment.book"
    )
    name = fields.Char(required=True)
    name_bn = fields.Char(
        string="Name (Bengali)",
        required=True,
        help="DE-17 + T08: authored Bengali, never machine-translated",
    )
    description = fields.Text()
    sample_bn = fields.Text(
        string="Bengali Utterances",
        required=True,
        help="Real Bengali utterances, one per line — the NLU test corpus (T08)",
    )
    sample_en = fields.Text(string="English Utterances")
    grounding = fields.Char(
        string="Grounding (live ERP data)",
        help="CD-M32-03: the live source this intent answers from — e.g. "
        "fix.service.order.tracking_ref via the party",
    )
    handoff_on_failure = fields.Boolean(
        default=True,
        help="T07: an intent the assistant cannot resolve hands off with full "
        "context rather than dead-ending",
    )
    active = fields.Boolean(default=True)
