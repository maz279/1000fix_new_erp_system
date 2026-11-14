# A03 · M32 Conversational AI (Bengali) — surfaces, report packs and KPIs over
# fix.assistant.intent / fix.conversation and the new assistant operations
# models. The playground and the agent-assist suggestions call the REAL
# classifier in assistant_engine.py — no canned demo replies.
import re

from odoo import http
from odoo.http import request

from ..p03_service_order_api import _require_internal

SURFACES = {
    "fix.assistant.intent": {
        "order": "code",
        "limit": 200,
        "actions": set(),
    },
    "fix.assistant.dialogue": {
        "order": "name",
        "limit": 100,
        "actions": set(),
    },
    "fix.assistant.rag.source": {
        "order": "name",
        "limit": 200,
        "actions": set(),
    },
    "fix.assistant.guardrail": {
        "order": "name",
        "limit": 200,
        "actions": set(),
    },
    # fix.conversation is served by M27's a03 surface (single declaration);
    # M32's screens read it through the merged registry.
    # --- added by the A03 gap-closure build -------------------
    # Each of these is bound by a workspace screen below; an
    # unservable surface is what test_a03_registry_coverage exists
    # to catch, and a surface no screen opens is dead weight it
    # also catches.
    "fix.assistant.llm.provider": {
        "order": "sequence, id",
        "limit": 100,
        "actions": set(),
    },
    "fix.assistant.ask": {
        "order": "asked_at desc, id desc",
        "limit": 300,
        # Review is four-eyes, and an answer that needs review is sent only
        # after it (A03 audit M32 G12).
        "actions": {"action_mark_reviewed", "action_send_to_customer"},
    },
    # The NLU release bundle (A03 audit M32 G4): digest, a measured
    # benchmark, then a four-eyes release routed through M63. There is no
    # Release button: the Tier-3 approver releases from their inbox.
    "fix.assistant.dataset": {
        "order": "create_date desc, id desc",
        "limit": 200,
        "actions": {
            "action_compute_digest",
            "action_run_benchmark",
            "action_request_approval",
            "action_recall_approval",
        },
    },
    "fix.assistant.intent.candidate": {
        "order": "frequency desc, id desc",
        "limit": 300,
        "actions": {"action_accept", "action_reject"},
    },
    # --- M32 capture audit (14 Nov 2026): the registers the Customer Service
    # Manager owns (spec 10.1 / 13). Read by every user, written by a
    # Contact Centre Supervisor (ACL); the hard rules live on the models.
    "fix.assistant.entity": {
        "order": "sequence, code",
        "limit": 200,
        "actions": set(),
    },
    "fix.assistant.action.authority": {
        "order": "action_type",
        "limit": 50,
        "actions": set(),
    },
    "fix.assistant.handoff.trigger": {
        "order": "category, signal",
        "limit": 50,
        "actions": set(),
    },
}

RESOLVED = ("resolved_ai", "resolved_agent")


def _pack(title, cols, labels, rows, notes, totals=None, empty=None):
    return {
        "title": title,
        "cols": cols,
        "labels": labels,
        "rows": rows,
        "totals": totals,
        "notes": notes,
        "empty": empty or "No data in this basis yet.",
    }


def _convs(env):
    return env["fix.conversation"].sudo().search([])


def _assistant_code(env):
    """Intent codes known to the DB side (the library the engine was seeded from)."""
    return set(env["fix.assistant.intent"].sudo().search([]).mapped("code"))


def _engine():
    from odoo.addons.cd_contact_centre.models.assistant_engine import AssistantEngine

    return AssistantEngine()


def _classify(text):
    try:
        res = _engine().classify_intent(text or "")
    except Exception:
        return None
    matched = getattr(res, "matched_intent", None)
    intent_code = matched.code if hasattr(matched, "code") else (matched or "")
    return {
        "intent": intent_code,
        "confidence": round(float(getattr(res, "confidence", 0.0)), 3),
        "grounding": getattr(res, "grounding", "") or "",
        "requires_handoff": bool(getattr(res, "requires_handoff", False)),
        "handoff_reason": getattr(res, "handoff_reason", "") or "",
        "response_bn": getattr(res, "response_text_bn", "") or "",
        "response_en": getattr(res, "response_text_en", "") or "",
    }


def intent_coverage_fcr(env, date_from=None, date_to=None, **params):
    intents = env["fix.assistant.intent"].sudo().search([])
    convs = _convs(env)
    ai_convs = convs.filtered(lambda c: c.state == "resolved_ai" or c.ai_resolved)
    total = len(convs)
    rows = []
    for intent in intents:
        mine = convs.filtered(lambda c, code=intent.code: (c.intent or "") == code)
        rows.append(
            {
                "intent": intent.code,
                "name": intent.name,
                "sessions": len(mine),
                "ai_resolved": len([c for c in mine if c.state == "resolved_ai"]),
                "handoff": len([c for c in mine if c.state == "with_agent"]),
                "fcr_pct": round(
                    len([c for c in mine if c.state in RESOLVED]) / len(mine) * 100.0, 1
                )
                if mine
                else 0.0,
            }
        )
    rows.sort(key=lambda r: -r["sessions"])
    return _pack(
        "Intent Coverage & FCR",
        ["intent", "name", "sessions", "ai_resolved", "handoff", "fcr_pct"],
        {
            "intent": "Intent Code",
            "name": "Intent",
            "sessions": "Sessions",
            "ai_resolved": "AI-Resolved",
            "handoff": "Handed Off",
            "fcr_pct": "FCR %",
        },
        rows,
        [
            "Sessions are conversations whose recorded intent matches the library code; "
            "AI automation = %d of %d conversations resolved by the assistant."
            % (len(ai_convs), total)
            if total
            else "No conversations yet."
        ],
        totals={
            "intent": "Total",
            "sessions": sum(r["sessions"] for r in rows),
            "ai_resolved": sum(r["ai_resolved"] for r in rows),
            "handoff": sum(r["handoff"] for r in rows),
        }
        if rows
        else None,
        empty="No assistant intents registered yet.",
    )


def handoff_reasons(env, date_from=None, date_to=None, **params):
    """Handoffs by trigger category and reason (spec 14: emotional,
    operational, technical). The category is stamped at the handoff from the
    trigger table; rows that predate it are classified from their reason."""
    Trigger = env.get("fix.assistant.handoff.trigger")
    convs = _convs(env).filtered(lambda c: c.handoff_reason or c.state == "with_agent")
    by_key = {}
    for c in convs:
        reason = c.handoff_reason or "unspecified"
        category = getattr(c, "handoff_category", False)
        if not category and Trigger is not None:
            category = Trigger.resolve(reason)["category"]
        key = (category or "unclassified", reason)
        row = by_key.setdefault(
            key,
            {"category": key[0], "reason": reason, "conversations": 0, "urgent": 0},
        )
        row["conversations"] += 1
        if getattr(c, "handoff_priority", "") == "urgent":
            row["urgent"] += 1
    rows = sorted(by_key.values(), key=lambda r: (r["category"], -r["conversations"]))
    return _pack(
        "Handoff Reasons",
        ["category", "reason", "conversations", "urgent"],
        {
            "category": "Trigger Category",
            "reason": "Handoff Reason",
            "conversations": "Conversations",
            "urgent": "Urgent",
        },
        rows,
        [
            "Reasons are recorded by the assistant at the moment of handoff; the "
            "category and priority come from the handoff triggers. 'unspecified' means "
            "the row predates the reason capture."
        ],
        totals={
            "category": "Total",
            "conversations": sum(r["conversations"] for r in rows),
            "urgent": sum(r["urgent"] for r in rows),
        }
        if rows
        else None,
        empty="No handoffs recorded — the assistant has not escalated yet.",
    )


def guardrail_status(env, date_from=None, date_to=None, **params):
    """Each rule with how often it fired, counted from the grounded-answer log
    (fix.assistant.ask records every guardrail verdict with the rule's name)."""
    rules = env["fix.assistant.guardrail"].sudo().with_context(active_test=False).search([])
    Ask = env.get("fix.assistant.ask")
    blocked_asks = (
        Ask.sudo().search([("guardrail_verdict", "=", "blocked")]) if Ask is not None else []
    )
    flagged_asks = (
        Ask.sudo().search([("guardrail_reason", "ilike", "Flagged by guardrail")])
        if Ask is not None
        else []
    )
    rows = []
    for rule in rules:
        prefix = "Guardrail '%s'" % rule.name
        blocked = sum(1 for a in blocked_asks if (a.guardrail_reason or "").startswith(prefix))
        flags = sum(1 for a in flagged_asks if rule.name in (a.guardrail_reason or ""))
        rows.append(
            {
                "name": rule.name,
                "rule": rule.rule,
                "action": rule.action,
                "active": "✓" if rule.active else "✗",
                "blocked": blocked,
                "flagged": flags,
            }
        )
    return _pack(
        "Guard-Rail Intervention Log",
        ["name", "rule", "action", "active", "blocked", "flagged"],
        {
            "name": "Guard Rail",
            "rule": "Condition",
            "action": "Action",
            "active": "Active",
            "blocked": "Blocked / Handed Off",
            "flagged": "Flagged",
        },
        rows,
        [
            "Counts come from the grounded-answer log, which records the verdict and "
            "the rule that fired on every assistant answer. These are input guard rails; "
            "the output filter (FR-CAI-032) is not a configurable rule yet."
        ],
        totals={
            "name": "Total",
            "blocked": sum(r["blocked"] for r in rows),
            "flagged": sum(r["flagged"] for r in rows),
        }
        if rows
        else None,
        empty="No guard-rail rules configured yet.",
    )


def bengali_vs_english(env, date_from=None, date_to=None, **params):
    turns = env["fix.conversation.turn"].sudo().search([])
    convs = _convs(env)
    by_lang = {}
    for turn in turns:
        row = by_lang.setdefault(
            turn.lang or "unknown", {"lang": turn.lang or "unknown", "turns": 0}
        )
        row["turns"] += 1
    rows = [by_lang[k] for k in sorted(by_lang, key=lambda k: -by_lang[k]["turns"])]
    ai = len(convs.filtered(lambda c: c.state == "resolved_ai"))
    total = len(convs)
    return _pack(
        "Bengali vs English Performance",
        ["lang", "turns"],
        {"lang": "Turn Language", "turns": "Turns"},
        rows,
        [
            "Language mix is measured from every transcript turn. Session-level "
            "resolution: %d of %d conversations resolved by the assistant." % (ai, total)
            if total
            else "No conversations yet."
        ],
        totals={"lang": "Total", "turns": sum(r["turns"] for r in rows)} if rows else None,
        empty="No transcript turns recorded yet.",
    )


def assistant_csat(env, date_from=None, date_to=None, **params):
    convs = _convs(env)
    ai = convs.filtered(lambda c: c.state == "resolved_ai" or c.ai_resolved)
    surveys = env["fix.survey"].sudo().search([("state", "=", "responded")])
    rows = [
        {"metric": "Assistant sessions", "value": len(convs), "basis": "fix.conversation"},
        {
            "metric": "Resolved by the assistant",
            "value": len(ai),
            "basis": "state=resolved_ai / ai_resolved",
        },
        {
            "metric": "Survey responses (all channels)",
            "value": len(surveys),
            "basis": "fix.survey responded",
        },
    ]
    return _pack(
        "Assistant CSAT",
        ["metric", "value", "basis"],
        {"metric": "Measure", "value": "Value", "basis": "Basis"},
        rows,
        [
            "CSAT cannot yet be attributed to the assistant: the CX survey links to the "
            "service order, not to the conversation. The declared gap is a survey↔"
            "conversation key; this pack does not invent one."
        ],
    )


_BUILTIN_ENTITIES = {
    "Order / invoice reference": re.compile(r"\b(?:SO|INV|AR)[/-]?\d{3,}\b", re.IGNORECASE),
    "Phone number": re.compile(r"(?:\+?880|0)1\d{9}\b"),
    "Amount (BDT)": re.compile(r"(?:৳|BDT|Tk\.?)\s?\d[\d,]*", re.IGNORECASE),
}


def entity_catalog(env, date_from=None, date_to=None, **params):
    """Entity extraction over the customer turns, with the definitions the
    Customer Service Manager registered (fix.assistant.entity). With none
    registered, the three built-in patterns run and the pack says so."""
    turns = env["fix.conversation.turn"].sudo().search([("speaker", "=", "customer")])
    Entity = env.get("fix.assistant.entity")
    definitions = Entity.sudo().search([]) if Entity is not None else []
    rows = []
    if definitions:
        for definition in definitions:
            hits = sum(1 for turn in turns if turn.text and definition.extract(turn.text))
            rows.append(
                {
                    "entity": definition.name,
                    "turns_with_match": hits,
                    "basis": "%s · %s" % (definition.code, definition.validation),
                }
            )
        basis_note = (
            "Extraction uses the %d registered entity definitions: each pattern is "
            "proved against its examples when saved, Bengali digits count as digits, "
            "and its validation (e.g. the IMEI check digit) must pass." % len(definitions)
        )
    else:
        for label, rx in _BUILTIN_ENTITIES.items():
            hits = 0
            for turn in turns:
                text = turn.text or ""
                if Entity is not None:
                    text = Entity._normalise(text)
                if text and rx.search(text):
                    hits += 1
            rows.append({"entity": label, "turns_with_match": hits, "basis": "built-in pattern"})
        basis_note = (
            "No entity definition is registered yet, so the three built-in patterns ran. "
            "Register definitions on this page to extract IMEI, serials, dates and the rest."
        )
    rows.append(
        {
            "entity": "Customer turns scanned",
            "turns_with_match": len(turns),
            "basis": "fix.conversation.turn speaker=customer",
        }
    )
    return _pack(
        "Entity Extraction — matches in the transcripts",
        ["entity", "turns_with_match", "basis"],
        {"entity": "Entity", "turns_with_match": "Turns With a Match", "basis": "Basis"},
        rows,
        [
            basis_note,
            "Extraction is deterministic pattern matching over the recorded text; a "
            "trained entity model is not claimed.",
        ],
    )


def handoff_packages(env, date_from=None, date_to=None, **params):
    convs = _convs(env).filtered(lambda c: c.state == "with_agent")
    rows = []
    for c in convs:
        rows.append(
            {
                "conversation": c.id,
                "customer": c.customer_id.name or c.contact_identity or "Anonymous",
                "intent": c.intent or "—",
                "reason": c.handoff_reason or "—",
                "category": getattr(c, "handoff_category", False) or "—",
                "priority": getattr(c, "handoff_priority", False) or "—",
                "turns": len(c.turn_ids),
                "started": c.started_at.strftime("%Y-%m-%d %H:%M") if c.started_at else "—",
            }
        )
    return _pack(
        "Handoff Packages — full context transferred to the agent",
        [
            "conversation",
            "customer",
            "intent",
            "reason",
            "category",
            "priority",
            "turns",
            "started",
        ],
        {
            "conversation": "Conversation",
            "customer": "Customer",
            "intent": "Intent",
            "reason": "Reason",
            "category": "Trigger Category",
            "priority": "Queue Priority",
            "turns": "Transcript Turns",
            "started": "Started",
        },
        rows,
        [
            "A handoff package is the conversation record itself: the agent sees the "
            "whole transcript, the intent and the customer 360 (T07)."
        ],
        empty="No active handoffs — every assistant session is self-service.",
    )


def suggested_replies(env, date_from=None, date_to=None, **params):
    """Agent-assist NBAs: classify the latest customer turn of every open
    conversation with the REAL engine and propose the grounded reply."""
    convs = _convs(env).filtered(lambda c: c.state in ("with_ai", "with_agent"))
    rows = []
    for c in convs[:20]:
        last_customer = c.turn_ids.filtered(lambda t: t.speaker == "customer")
        text = last_customer[-1].text if last_customer else ""
        result = _classify(text)
        if not result:
            continue
        rows.append(
            {
                "conversation": c.id,
                "customer": c.customer_id.name or c.contact_identity or "Anonymous",
                "utterance": (text or "")[:80],
                "intent": result["intent"] or "—",
                "confidence": result["confidence"],
                "suggested": (result["response_bn"] or result["response_en"])[:120],
                "handoff": "handoff" if result["requires_handoff"] else "",
            }
        )
    return _pack(
        "Suggested Replies / NBA — real classifier output",
        ["conversation", "customer", "utterance", "intent", "confidence", "suggested", "handoff"],
        {
            "conversation": "Conversation",
            "customer": "Customer",
            "utterance": "Last Customer Turn",
            "intent": "Detected Intent",
            "confidence": "Confidence",
            "suggested": "Suggested Reply (bn/en)",
            "handoff": "Handoff Flag",
        },
        rows,
        [
            "Suggestions come from the same classifier the assistant runs; a low "
            "confidence or a guard-rail hit is flagged for handoff."
        ],
        empty="No open conversations needing a suggestion.",
    )


def conversation_analytics(env, date_from=None, date_to=None, **params):
    convs = _convs(env)
    total = len(convs)
    ai = len(convs.filtered(lambda c: c.state == "resolved_ai"))
    handoff = len(convs.filtered(lambda c: c.state == "with_agent"))
    turns = sum(len(c.turn_ids) for c in convs)
    rows = [
        {"metric": "Conversations", "value": total, "basis": "fix.conversation"},
        {"metric": "Resolved by assistant", "value": ai, "basis": "state=resolved_ai"},
        {"metric": "Active handoffs", "value": handoff, "basis": "state=with_agent"},
        {
            "metric": "Avg turns per conversation",
            "value": round(turns / total, 1) if total else 0.0,
            "basis": "transcript turns",
        },
        {
            "metric": "AI share",
            "value": round(ai / total * 100.0, 1) if total else 0.0,
            "basis": "% of conversations",
        },
    ]
    return _pack(
        "Conversation Analytics",
        ["metric", "value", "basis"],
        {"metric": "Measure", "value": "Value", "basis": "Basis"},
        rows,
        ["Measured from the conversation and transcript records only."],
    )


REPORTS = {
    "intent_coverage_fcr": intent_coverage_fcr,
    "handoff_reasons": handoff_reasons,
    "guardrail_status": guardrail_status,
    "bengali_vs_english": bengali_vs_english,
    "assistant_csat": assistant_csat,
    "entity_catalog": entity_catalog,
    "handoff_packages": handoff_packages,
    "suggested_replies": suggested_replies,
    "conversation_analytics": conversation_analytics,
}


def _guardrail_blocks(env):
    """How many AI answers a guardrail stopped, or None without the log."""
    Ask = env.get("fix.assistant.ask")
    if Ask is None:
        return None
    return Ask.sudo().search_count([("guardrail_verdict", "=", "blocked")])


def kpis(env):
    convs = _convs(env)
    total = len(convs)
    ai = len(convs.filtered(lambda c: c.state == "resolved_ai" or c.ai_resolved))
    turns = env["fix.conversation.turn"].sudo().search([])
    bn_turns = len(turns.filtered(lambda t: t.lang == "bn"))
    return {
        "faq_automation": round(ai / total * 100.0, 1) if total else None,
        "ai_fcr": round(ai / total * 100.0, 1) if total else None,
        "handoff_precision": None,  # needs a labelled "should-have-handled" ground truth
        "bengali_sessions": round(bn_turns / len(turns) * 100.0, 1) if turns else None,
        # Closed: fix.assistant.ask (S7) records a guardrail verdict on
        # every call, so blocks are counted rather than declared missing.
        "guardrail_blocks": _guardrail_blocks(env),
        "avg_turns": round(sum(len(c.turn_ids) for c in convs) / total, 1) if total else None,
    }


class P03AssistantApi(http.Controller):
    @http.route("/p03/assistant/kpis", type="jsonrpc", auth="user", readonly=True)
    def assistant_kpis(self, module=None, **kw):
        _require_internal(request.env)
        return {"M32": kpis(request.env)}

    @http.route("/p03/assistant/classify", type="jsonrpc", auth="user", readonly=True)
    def assistant_classify(self, text=None, **kw):
        """The playground: classify a typed utterance with the REAL engine."""
        _require_internal(request.env)
        result = _classify(text)
        if result is None:
            return {"error": "The assistant engine could not be loaded."}
        return result
