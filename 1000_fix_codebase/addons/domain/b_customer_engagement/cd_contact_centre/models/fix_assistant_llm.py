# S7 — the AI Grounding Service, and real-time bn<->en translation.
#
# S7's charter from the gap plan: ONE API — ask(intent, context) -> grounded
# answer + citations + guardrail verdict — owned by M32 and consumed by M27
# agent assist, M07 seller copilot, M35 content drafts and the P01 chatbot.
# The point is to prevent per-module AI forks: four modules each calling a
# model directly is four sets of guardrails, four PII boundaries and four
# audit trails.
#
# WHAT IS REAL HERE AND WHAT IS A SEAM, stated plainly because this is the
# area where it is easiest to ship something that looks finished:
#
#   REAL: the service API, the guardrail evaluation, the citation
#   requirement, the dataset-release gate check, the refusal paths, the
#   per-ask audit record, and the ORM-grounded answers that M32's existing
#   rule-based engine already produces. Calling ask() today returns a real
#   grounded answer for the eleven authored intents.
#
#   A SEAM: the hosted generative model. No LLM endpoint is invented. A
#   provider record names where one would be and what it is allowed to do;
#   with none configured, ask() answers from the rule-based grounders and
#   SAYS SO in the response, rather than failing or pretending.
#
# The PDPA transfer constraint is why this matters more than usual: the
# module manifest already records that M32 runs on self-hosted Ollama because
# customer data must not leave the Company. So a provider record carries a
# residency declaration, and a provider that is not self-hosted cannot be
# used for a prompt containing customer context. That check is real and
# enforced below.
import json
import logging
import sys
from pathlib import Path

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

_logger = logging.getLogger(__name__)

# The self-hosted generation client. `conversational-ai` is not an importable
# package name, so its src goes on sys.path -- the pattern cd_rate_card and
# cd_cash_position already use to reach their services.
_AI_SRC = Path(__file__).resolve().parents[5] / "services" / "conversational-ai" / "src"


def _ollama():
    """The client module, or None when the service tree is unavailable.

    Lazy: a missing service directory must degrade to "nothing was generated,
    and here is why" rather than break the Odoo registry load.
    """
    try:
        if str(_AI_SRC) not in sys.path:
            sys.path.insert(0, str(_AI_SRC))
        import ollama_client
    except Exception as exc:
        _logger.warning("ollama client unavailable: %s", exc)
        return None
    return ollama_client


class FixAssistantLlmProvider(models.Model):
    """Where a generative model lives, and what it may be given."""

    _name = "fix.assistant.llm.provider"
    _description = "Assistant LLM Provider"
    _inherit = ["mail.thread"]
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    endpoint_config_key = fields.Char(
        string="Endpoint Config Key",
        help="ir.config_parameter holding the base URL. Credentials are "
        "NEVER stored on this record.",
    )
    model_name = fields.Char(help="The served model identifier, e.g. a local tag.")
    residency = fields.Selection(
        [
            ("self_hosted", "Self-hosted inside the Company"),
            ("in_country", "Third party, Bangladesh residency contracted"),
            ("offshore", "Offshore"),
        ],
        required=True,
        default="self_hosted",
        help="PDPA transfer restriction. The manifest records that M32 runs "
        "self-hosted because customer data must not leave the Company; this "
        "field is what enforces it rather than documenting it.",
    )
    may_receive_customer_context = fields.Boolean(
        string="May Receive Customer Context",
        default=False,
        help="Only ever true for a self-hosted or contractually in-country "
        "provider. The constraint below enforces that.",
    )
    max_tokens = fields.Integer(default=512)
    latency_profile = fields.Selection(
        [
            ("voice", "Voice IVR (sub-second budget)"),
            ("chat", "Agent assist / chat (2s budget)"),
            ("batch", "Offline: drafts, translation, mining"),
        ],
        required=True,
        default="chat",
        help="The recorded SLA budget this provider is held to. From "
        "benchmark_ollama_latency.py: voice <= 400ms, text chat <= 2000ms. A "
        "request that cannot answer inside its budget is useless to the "
        "caller, so it fails with a reason instead of arriving late.",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("disabled", "Disabled")],
        required=True,
        default="draft",
        tracking=True,
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )

    _code_unique = models.Constraint("UNIQUE (code)", "Each LLM provider code exists once.")

    @api.constrains("residency", "may_receive_customer_context")
    def _check_residency_permits_customer_data(self):
        for rec in self:
            if rec.may_receive_customer_context and rec.residency == "offshore":
                raise ValidationError(
                    "Provider '%s' is offshore and cannot be allowed to "
                    "receive customer context. PDPA transfer restrictions are "
                    "the reason M32 is self-hosted; a checkbox must not be "
                    "able to override them." % rec.name
                )

    @api.model
    def active_provider(self, needs_customer_context=True):
        """The provider to use, or empty when none may be used.

        Returning empty is a normal outcome, not an error: the grounding
        service falls back to its rule-based grounders and labels the answer.
        """
        domain = [("state", "=", "active"), ("active", "=", True)]
        if needs_customer_context:
            domain.append(("may_receive_customer_context", "=", True))
        return self.sudo().search(domain, order="sequence, id", limit=1)


class FixAssistantAsk(models.Model):
    """One call to the grounding service. The audit trail S7 needs.

    Every answer the estate gives through AI has a row here: what was asked,
    what grounded it, which guardrails ran, what came back and whether a
    human saw it. An AI answer with no record of its basis is not auditable,
    and REQ-32.5's whole posture is that it must be.
    """

    _name = "fix.assistant.ask"
    _description = "Assistant Grounded Answer"
    _order = "asked_at desc, id desc"
    _rec_name = "question"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    asked_at = fields.Datetime(required=True, default=fields.Datetime.now, index=True)
    asked_by = fields.Many2one("res.users", default=lambda self: self.env.user)
    consumer = fields.Selection(
        [
            ("m27_agent_assist", "M27 agent assist"),
            ("m27_bot", "M27 customer-facing bot"),
            ("m07_seller", "M07 seller copilot"),
            ("m35_content", "M35 content draft"),
            ("p01_chatbot", "P01 portal chatbot"),
            ("other", "Other"),
        ],
        required=True,
        default="other",
        help="Which caller asked. One service, many consumers — recording "
        "which is how a per-module fork would be noticed.",
    )
    conversation_id = fields.Many2one(
        "fix.conversation", string="Conversation", ondelete="set null", index=True
    )
    partner_id = fields.Many2one("res.partner", string="Customer", index=True)
    intent = fields.Char(index=True)
    question = fields.Text(required=True)
    language = fields.Selection(
        [("bn", "Bengali"), ("en", "English"), ("mixed", "Mixed")], default="bn"
    )
    answer_bn = fields.Text()
    answer_en = fields.Text()
    grounded = fields.Boolean(
        readonly=True,
        help="Whether the answer rests on a retrieved estate record. An "
        "ungrounded answer is never sent to a customer.",
    )
    citations = fields.Text(
        readonly=True,
        help="JSON list of the records the answer rests on. An answer that "
        "cites nothing is refused rather than shown.",
    )
    engine = fields.Selection(
        [
            ("rule_grounder", "Rule-based ORM grounder"),
            ("llm", "Generative model"),
            ("refused", "Refused"),
        ],
        required=True,
        default="rule_grounder",
        readonly=True,
        help="Never hidden. A rule-based answer presented as generative, or "
        "the reverse, misleads whoever is deciding how much to trust it.",
    )
    provider_id = fields.Many2one("fix.assistant.llm.provider", string="Provider", readonly=True)
    guardrail_verdict = fields.Selection(
        [("pass", "Passed"), ("blocked", "Blocked"), ("not_run", "Not run")],
        required=True,
        default="not_run",
        readonly=True,
    )
    guardrail_reason = fields.Char(readonly=True)

    @api.depends("question", "guardrail_reason", "asked_at")
    def _compute_display_name(self):
        """_rec_name = "question" renders a REFUSED ask as a blank label.

        ask() correctly refuses an empty question and still records the
        attempt — a refusal nobody can see is not an audit trail — so rows
        with a whitespace question exist by design. They were showing as an
        empty name in every list and many2one. Name the refusal instead of
        showing nothing; a long question is also truncated, because a Text
        field as a record label otherwise fills the tab strip.
        """
        for rec in self:
            q = (rec.question or "").strip()
            if q:
                rec.display_name = q[:60] + ("…" if len(q) > 60 else "")
            else:
                rec.display_name = "(%s)" % (rec.guardrail_reason or "empty question, refused")

    requires_human = fields.Boolean(
        readonly=True,
        help="HITL: true when the answer must be reviewed before it reaches a " "customer.",
    )
    human_reviewed_by = fields.Many2one("res.users", readonly=True)
    human_reviewed_at = fields.Datetime(readonly=True)
    latency_ms = fields.Integer(readonly=True)

    def action_mark_reviewed(self):
        for rec in self:
            rec.write(
                {
                    "human_reviewed_by": self.env.user.id,
                    "human_reviewed_at": fields.Datetime.now(),
                }
            )
        return True


class FixAssistantGroundingService(models.Model):
    """S7 itself: one ask() every consumer calls."""

    _inherit = "fix.assistant.intent"

    @api.model
    def ask(
        self,
        question,
        intent=None,
        conversation=None,
        partner=None,
        consumer="other",
        language="bn",
        allow_generative=True,
    ):
        """THE grounded-answer API.

        Order of operations, and why:
          1. GUARDRAILS FIRST, on the question. A question that trips a
             guardrail must not reach a grounder or a model at all — running
             them afterwards would mean the prohibited content was already
             processed.
          2. GROUND. The rule-based grounders answer from live ORM records
             and return citations. This is what the estate has today and it
             is real.
          3. GENERATE, only if a usable provider exists AND the answer needs
             it AND residency permits the context. Otherwise the grounded
             answer stands, labelled rule_grounder.
          4. REFUSE rather than invent. No citation means no answer.
          5. RECORD. Always, including refusals.

        Returns a dict with the answer, its basis, its citations and the ask
        record id.
        """
        started = fields.Datetime.now()
        Ask = self.env["fix.assistant.ask"]
        conversation_rec = conversation if hasattr(conversation, "id") else None
        partner_rec = partner if hasattr(partner, "id") else None
        if partner_rec is None and conversation_rec is not None:
            partner_rec = conversation_rec.customer_id

        base_vals = {
            "consumer": consumer,
            "conversation_id": conversation_rec.id if conversation_rec else False,
            "partner_id": partner_rec.id if partner_rec else False,
            "intent": intent or "",
            "question": question or "",
            "language": language,
        }

        if not (question or "").strip():
            record = Ask.sudo().create(
                dict(
                    base_vals,
                    engine="refused",
                    guardrail_verdict="not_run",
                    guardrail_reason="Empty question.",
                )
            )
            return {
                "ok": False,
                "ask_id": record.id,
                "reason": "No question was asked.",
                "engine": "refused",
            }

        # 1. guardrails on the INPUT
        verdict = self._evaluate_guardrails(question)
        if verdict["blocked"]:
            record = Ask.sudo().create(
                dict(
                    base_vals,
                    engine="refused",
                    guardrail_verdict="blocked",
                    guardrail_reason=verdict["reason"],
                    requires_human=True,
                )
            )
            publish(
                self.env,
                "assistant.guardrail_blocked",
                "fix.assistant.ask",
                record.id,
                {
                    "consumer": consumer,
                    "intent": intent or None,
                    "reason": verdict["reason"],
                },
            )
            return {
                "ok": False,
                "ask_id": record.id,
                "reason": verdict["reason"],
                "engine": "refused",
                "requires_human": True,
            }

        # 2. ground against live records
        grounded = self._ground(question, intent, conversation_rec)

        # 3. generation, only where it is permitted and useful
        engine = "rule_grounder"
        provider = self.env["fix.assistant.llm.provider"]
        generative_note = ""
        if allow_generative and not grounded["grounded"]:
            provider = self.env["fix.assistant.llm.provider"].active_provider(
                needs_customer_context=bool(partner_rec)
            )
            if provider:
                generated = self._generate(provider, question, grounded, language)
                if generated["ok"]:
                    grounded = generated["answer"]
                    engine = "llm"
                else:
                    generative_note = generated["reason"]
            else:
                generative_note = (
                    "No LLM provider is configured that may receive this "
                    "context, so the rule-based grounders answered. Hosted-model "
                    "selection is a declared external dependency."
                )

        # 4. refuse rather than invent
        if not grounded["grounded"]:
            record = Ask.sudo().create(
                dict(
                    base_vals,
                    engine="refused",
                    guardrail_verdict="pass",
                    guardrail_reason=generative_note or "No grounding record found.",
                    requires_human=True,
                    answer_bn=grounded.get("bn") or "",
                    answer_en=grounded.get("en") or "",
                    latency_ms=int((fields.Datetime.now() - started).total_seconds() * 1000),
                )
            )
            return {
                "ok": False,
                "ask_id": record.id,
                "reason": grounded.get("reason")
                or "Nothing in the estate grounds an answer to this, so no "
                "answer was produced. %s"
                % generative_note,
                "engine": "refused",
                "requires_human": True,
                "bn": grounded.get("bn"),
                "en": grounded.get("en"),
            }

        # 5. record
        record = Ask.sudo().create(
            dict(
                base_vals,
                engine=engine,
                provider_id=provider.id if provider else False,
                guardrail_verdict="pass",
                guardrail_reason=generative_note,
                grounded=True,
                citations=json.dumps(grounded.get("citations") or [], ensure_ascii=False),
                answer_bn=grounded.get("bn") or "",
                answer_en=grounded.get("en") or "",
                # A generated answer always needs a human before it reaches a
                # customer; a rule-based grounded one does not, because its
                # text was authored.
                requires_human=(engine == "llm"),
                latency_ms=int((fields.Datetime.now() - started).total_seconds() * 1000),
            )
        )
        return {
            "ok": True,
            "ask_id": record.id,
            "engine": engine,
            "bn": grounded.get("bn"),
            "en": grounded.get("en"),
            "citations": grounded.get("citations") or [],
            "requires_human": engine == "llm",
            "note": generative_note,
        }

    @api.model
    def _evaluate_guardrails(self, text):
        """Run the configured guardrails over a question."""
        Guardrail = self.env.get("fix.assistant.guardrail")
        if Guardrail is None:
            return {"blocked": False, "reason": ""}
        lowered = (text or "").lower()
        flagged = []
        for guardrail in Guardrail.sudo().search([("active", "=", True)]):
            # fix.assistant.guardrail stores the condition in `rule` as
            # authored prose. Matching is a containment test over its
            # significant words rather than the whole sentence, because a
            # rule reading "advice on legal liability" must fire on "is
            # 1000FiX legally liable" -- an exact-phrase test would never
            # match anything a customer actually types.
            condition = (guardrail.rule or "").strip().lower()
            if not condition:
                continue
            terms = [t for t in condition.split() if len(t) > 3]
            if not terms:
                continue
            hits = sum(1 for t in terms if t in lowered)
            # Two significant terms, or every term for a short rule. One
            # incidental word is not a match.
            needed = 2 if len(terms) > 2 else len(terms)
            if hits < needed:
                continue
            if guardrail.action in ("block", "handoff"):
                return {
                    "blocked": True,
                    "reason": "Guardrail '%s' matched (%d of %d terms) and its "
                    "action is %s." % (guardrail.name, hits, len(terms), guardrail.action),
                }
            flagged.append(guardrail.name)
        # A 'flag' guardrail does not block; it is reported so the ask record
        # carries it and a reviewer can see why the answer was marked.
        return {
            "blocked": False,
            "reason": ("Flagged by guardrail(s): %s." % ", ".join(flagged)) if flagged else "",
        }

    @api.model
    def _ground(self, question, intent, conversation):
        """Answer from live ORM records via M32's existing grounders.

        Reuses fix.conversation._ground_intent_response, which already
        resolves order status, price estimates, branch locations and the rest
        against real records and refuses unknowns. Re-implementing grounding
        here would be the per-module fork S7 exists to prevent.
        """
        Conversation = self.env["fix.conversation"]
        host = conversation or Conversation.sudo().new(
            {"channel": "chat", "operating_unit_id": False}
        )
        resolved_intent = intent
        if not resolved_intent:
            resolved_intent = getattr(host, "intent", "") or ""
        try:
            answer = host._ground_intent_response(resolved_intent, question)
        except Exception as exc:
            return {
                "grounded": False,
                "bn": "",
                "en": "",
                "reason": "The grounder for intent %r failed: %s" % (resolved_intent, exc),
                "citations": [],
            }
        citations = []
        if answer.get("grounded"):
            citations.append(
                {
                    "basis": "orm_grounder",
                    "intent": resolved_intent,
                    "note": answer.get("reason") or "",
                }
            )
        return {
            "grounded": bool(answer.get("grounded")),
            "bn": answer.get("bn") or "",
            "en": answer.get("en") or "",
            "reason": answer.get("reason") or "",
            "citations": citations,
        }

    # The system prompt. Deliberately narrow: this model serves transactional
    # intents for a repair business, and a model told it may answer anything
    # will answer anything.
    _ASSIST_SYSTEM_PROMPT = (
        "You are the assistant for 1000FiX Services Ltd, an electronics and "
        "appliance repair company in Bangladesh (hotline 16743). Answer ONLY "
        "from the grounding facts given to you. If the facts do not contain "
        "the answer, say that you do not know and that a human agent will "
        "help -- never guess an order status, a price, an address or a date. "
        "Keep the reply under four sentences. Reply in the language the "
        "customer used."
    )

    @api.model
    def _generate(self, provider, question, grounded, language):
        """Generate through the self-hosted runtime.

        The runtime is Ollama, which this estate chose and recorded: the
        module manifest states M32 runs self-hosted under PDPA transfer
        restrictions, and benchmark_ollama_latency.py pins its image digest
        and the latency SLAs. The client is in
        services/conversational-ai/src/ollama_client.py, SSRF-guarded to
        self-hosted hosts only -- a model endpoint that could be pointed
        anywhere would be an exfiltration channel for exactly the customer
        data that mandate protects.

        Returns {ok, answer|reason, text}. A transport failure is a REASON,
        never an exception: the caller's refusal path and human handoff are
        better outcomes than a 500 in the middle of a conversation.
        """
        client = _ollama()
        if client is None:
            return {
                "ok": False,
                "reason": "The conversational-ai service tree is not available "
                "to this process, so nothing was generated.",
            }
        if not client.configured():
            return {
                "ok": False,
                "reason": "No self-hosted model runtime is configured (%s / %s "
                "are unset), so the rule-based grounders answered instead."
                % (client.URL_ENV, client.MODEL_ENV),
            }

        facts = grounded.get("en") or grounded.get("bn") or ""
        prompt = (
            "Grounding facts from the ERP (the ONLY facts you may use):\n"
            "%s\n\nCustomer question: %s" % (facts or "(none found)", question)
        )
        result = client.generate(
            prompt,
            system=self._ASSIST_SYSTEM_PROMPT,
            profile=provider.latency_profile or "chat",
            max_tokens=provider.max_tokens or 512,
        )
        if not result.ok:
            return {"ok": False, "reason": result.detail}

        # A generated answer still has to pass the output guardrails. The
        # input was checked before grounding; this is the second half, and
        # without it a guardrail only ever policed the customer's words and
        # never the model's.
        verdict = self._evaluate_guardrails(result.text)
        if verdict["blocked"]:
            return {
                "ok": False,
                "reason": "Generated answer blocked on output: %s" % verdict["reason"],
            }

        answer = {
            "grounded": True,
            "bn": result.text if language == "bn" else "",
            "en": result.text if language != "bn" else "",
            "reason": "generated by %s in %dms" % (result.model, result.latency_ms),
            "citations": [
                *list(grounded.get("citations") or []),
                {
                    "basis": "generated",
                    "model": result.model,
                    "latency_ms": result.latency_ms,
                    "completion_tokens": result.completion_tokens,
                    "note": "Generated from the grounding facts above. Requires "
                    "human review before it reaches a customer.",
                },
            ],
        }
        return {"ok": True, "answer": answer, "text": result.text}


class FixConversationTurnTranslation(models.Model):
    """Real-time bn<->en translation on the transcript.

    A sharper fit here than in most D365 tenants, as the gap plan notes: A03
    is bilingual by mandate and turns already carry `lang`, so translating a
    Bengali customer turn for an English-reading specialist is a real daily
    need rather than a demo.
    """

    _inherit = "fix.conversation.turn"

    text_translated = fields.Text(
        string="Translated Text",
        readonly=True,
        help="The turn rendered in the other language. Empty means no "
        "translation exists — never a silent copy of the original.",
    )
    translated_to = fields.Selection([("bn", "Bengali"), ("en", "English")], readonly=True)
    translation_engine = fields.Selection(
        [
            ("none", "Not translated"),
            ("llm", "Generative model"),
            ("human", "Human agent"),
        ],
        default="none",
        readonly=True,
        help="T08 forbids machine-translated AUTHORED content (intent "
        "utterances, templates). A live transcript is different: it is "
        "working text for an agent, not published copy. The engine is "
        "recorded so the two never get confused.",
    )
    translated_at = fields.Datetime(readonly=True)

    def action_translate(self, target_language=None):
        """Translate this turn for the handling agent.

        Returns a per-turn result. With no generative provider available the
        turn is left untranslated and says so, because a transcript that
        silently shows the original as a translation would mislead an agent
        into thinking they had understood it.
        """
        results = []
        Provider = self.env["fix.assistant.llm.provider"]
        for turn in self:
            source = (turn.lang or "bn").lower()
            target = target_language or ("en" if source.startswith("bn") else "bn")
            if turn.text_translated and turn.translated_to == target:
                results.append({"turn_id": turn.id, "ok": True, "cached": True})
                continue
            provider = Provider.active_provider(needs_customer_context=True)
            if not provider:
                results.append(
                    {
                        "turn_id": turn.id,
                        "ok": False,
                        "reason": "No self-hosted or in-country model is "
                        "configured, and a customer transcript may not be sent "
                        "to an offshore one (PDPA). The turn is left in its "
                        "original language rather than shown as translated.",
                    }
                )
                continue
            client = _ollama()
            if client is None or not client.configured():
                results.append(
                    {
                        "turn_id": turn.id,
                        "ok": False,
                        "reason": "No self-hosted model runtime is configured, so "
                        "the turn is left in its original language rather than "
                        "shown as translated.",
                    }
                )
                continue
            translated = client.translate(turn.text or "", target)
            if not translated.ok:
                results.append({"turn_id": turn.id, "ok": False, "reason": translated.detail})
                continue
            turn.write(
                {
                    "text_translated": translated.text,
                    "translated_to": target,
                    "translation_engine": "llm",
                    "translated_at": fields.Datetime.now(),
                }
            )
            results.append({"turn_id": turn.id, "ok": True, "latency_ms": translated.latency_ms})
        return results

    def action_record_human_translation(self, text, target_language):
        """An agent types the translation. Always available, always honest."""
        if not (text or "").strip():
            raise UserError("A human translation cannot be empty.")
        for turn in self:
            turn.write(
                {
                    "text_translated": text,
                    "translated_to": target_language,
                    "translation_engine": "human",
                    "translated_at": fields.Datetime.now(),
                }
            )
        return True
