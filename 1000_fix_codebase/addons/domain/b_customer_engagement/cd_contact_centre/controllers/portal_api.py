# P10 agent-console portal API — the staff workspace behind :3005.
#
# The W4 contract in contact_api.py stays the partner/integration surface.
# This controller adds what the interactive console needs and the base
# contract does not expose: the queue with waiting/SLA/agent context, the
# disposition register, and the two write paths an agent actually uses —
# a reply turn and the mandatory wrap-up (disposition + substantive notes
# + FCR). Every route is auth="user" AND refuses non-staff users at the
# data layer; the console's proxy/bridge is not the only gate.

from datetime import datetime, time

from odoo import fields, http
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.http import request

ACTIVE_STATES = ("new", "with_ai", "with_agent")
CLOSED_STATES = ("resolved_ai", "resolved_agent", "abandoned")
MAX_REPLY = 4000


def _error(code, message):
    return {"error": {"code": code, "message": message}}


def _staff_only():
    """Staff consoles are for internal users only (P06/P10).

    Unbound request contexts (direct controller calls in tests/scripts) are
    not HTTP callers; the route's auth="user" already protects them.
    """
    try:
        user = request.env.user
    except (RuntimeError, AttributeError):
        return None
    if not user or not user._is_internal():
        return _error("staff_only", "This console is for 1000FiX staff")
    return None


def _to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _dt(value):
    return fields.Datetime.to_string(value) if value else ""


def _is_supervisor():
    try:
        return request.env.user.has_group("cd_contact_centre.group_cc_supervisor")
    except Exception:
        return False


class ContactPortalApiController(http.Controller):
    """Session-authenticated agent workspace routes (:3005)."""

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------
    @http.route("/contact/portal/queue", type="jsonrpc", auth="user", readonly=True)
    def portal_queue(self, **kwargs):
        """Active conversations with waiting time, SLA and routing context."""
        denied = _staff_only()
        if denied:
            return denied
        now = fields.Datetime.now()
        domain = [("state", "in", ACTIVE_STATES)]
        channel = kwargs.get("channel")
        if channel in ("voice", "whatsapp", "chat", "email", "in_app"):
            domain.append(("channel", "=", channel))
        rows = request.env["fix.conversation"].search(
            domain, limit=200, order="queued_at asc, started_at asc, id asc"
        )
        result = []
        for conv in rows:
            entered = conv.queued_at or conv.started_at
            waiting = max(0, int((now - entered).total_seconds() // 60)) if entered else 0
            item = conv.work_item_id
            result.append(
                {
                    "id": conv.id,
                    "channel": conv.channel,
                    "state": conv.state,
                    "intent": conv.intent or "",
                    "customer": conv.customer_id.name or "",
                    "contact_identity": conv.contact_identity or "",
                    "started_at": _dt(conv.started_at),
                    "waiting_minutes": waiting,
                    "turns": len(conv.turn_ids),
                    "agent": conv.agent_id.name or "",
                    "agent_id": conv.agent_id.id or None,
                    "queued_at": _dt(conv.queued_at),
                    "answered_at": _dt(conv.answered_at),
                    "sla_due_at": _dt(conv.sla_answer_due_at),
                    "sla_breached": bool(
                        conv.sla_answer_due_at
                        and not conv.answered_at
                        and now > conv.sla_answer_due_at
                    ),
                    "priority": item.priority if item else 0,
                    "work_state": item.state if item else "",
                    "entitlement": item.entitlement_note if item else "",
                    "handoff_reason": conv.handoff_reason or "",
                }
            )
        return {"conversations": result, "total": len(result)}

    @http.route("/contact/portal/summary", type="jsonrpc", auth="user", readonly=True)
    def portal_summary(self, **kwargs):
        """Queue posture for the console header — counts, oldest wait, breaches."""
        denied = _staff_only()
        if denied:
            return denied
        now = fields.Datetime.now()
        convs = request.env["fix.conversation"].search([("state", "in", ACTIVE_STATES)])
        by_state = {}
        by_channel = {}
        oldest = 0
        breached = 0
        waiting = 0
        for conv in convs:
            by_state[conv.state] = by_state.get(conv.state, 0) + 1
            by_channel[conv.channel] = by_channel.get(conv.channel, 0) + 1
            entered = conv.queued_at or conv.started_at
            if entered:
                oldest = max(oldest, int((now - entered).total_seconds() // 60))
            if conv.state == "with_agent":
                continue
            waiting += 1
            if conv.sla_answer_due_at and not conv.answered_at and now > conv.sla_answer_due_at:
                breached += 1
        today = datetime.combine(fields.Date.context_today(request.env.user), time.min)
        resolved_today = request.env["fix.conversation"].search_count(
            [
                ("state", "in", ("resolved_ai", "resolved_agent")),
                ("ended_at", ">=", today),
            ]
        )
        return {
            "active": len(convs),
            "waiting_for_agent": waiting,
            "oldest_waiting_minutes": oldest,
            "sla_breached": breached,
            "resolved_today": resolved_today,
            "by_state": by_state,
            "by_channel": by_channel,
            "generated_at": _dt(now),
        }

    @http.route("/contact/portal/dispositions", type="jsonrpc", auth="user", readonly=True)
    def portal_dispositions(self, **kwargs):
        """The active disposition register for the mandatory wrap-up."""
        denied = _staff_only()
        if denied:
            return denied
        rows = request.env["fix.cc.disposition"].search([("active", "=", True)], order="code")
        return {
            "dispositions": [
                {
                    "id": d.id,
                    "code": d.code,
                    "name": d.name,
                    "category": d.category,
                    "is_resolved": d.is_resolved,
                }
                for d in rows
            ]
        }

    @http.route("/contact/portal/conversation", type="jsonrpc", auth="user", readonly=True)
    def portal_conversation(self, **kwargs):
        """Transcript + customer 360 + the wrap-up state of one conversation."""
        denied = _staff_only()
        if denied:
            return denied
        conversation_id = _to_int(kwargs.get("conversation_id"))
        if not conversation_id:
            return _error("missing_conversation", "conversation_id is required")
        conv = request.env["fix.conversation"].browse(conversation_id)
        if not conv.exists():
            return _error("no_conversation", "Conversation not found")
        transcript = [
            {
                "seq": t.sequence,
                "speaker": t.speaker,
                "text": t.text,
                "lang": t.lang,
                "at": _dt(t.spoken_at),
            }
            for t in conv.turn_ids.sorted(key=lambda t: (t.sequence, t.id))
        ]
        orders, devices, recent = [], [], []
        if conv.customer_id:
            orders = [
                {
                    "ref": o.name,
                    "state": o.state,
                    "device": o.device_id.device_model_id.name or "",
                }
                for o in request.env["fix.service.order"].search(
                    [("customer_id", "=", conv.customer_id.id)], limit=10
                )
            ]
            devices = [
                {
                    "model": d.device_model_id.name or "",
                    "identifier": (d.imei_1 or d.serial_number or "")[:6] + "…",
                    "warranty_status": d.warranty_status or "none",
                }
                for d in request.env["fix.device"].search(
                    [("owner_id", "=", conv.customer_id.id)], limit=10
                )
            ]
            recent = [
                {
                    "id": c.id,
                    "channel": c.channel,
                    "state": c.state,
                    "started_at": _dt(c.started_at),
                }
                for c in request.env["fix.conversation"].search(
                    [("customer_id", "=", conv.customer_id.id), ("id", "!=", conv.id)],
                    limit=10,
                    order="started_at desc",
                )
            ]
        item = conv.work_item_id
        return {
            "conversation": {
                "id": conv.id,
                "channel": conv.channel,
                "state": conv.state,
                "intent": conv.intent or "",
                "customer": conv.customer_id.name or "",
                "contact_identity": conv.contact_identity or "",
                "agent": conv.agent_id.name or "",
                "agent_id": conv.agent_id.id or None,
                "queued_at": _dt(conv.queued_at),
                "started_at": _dt(conv.started_at),
                "answered_at": _dt(conv.answered_at),
                "ended_at": _dt(conv.ended_at),
                "sla_due_at": _dt(conv.sla_answer_due_at),
                "handoff_reason": conv.handoff_reason or "",
                "ai_resolved": bool(conv.ai_resolved),
                "disposition": {
                    "id": conv.disposition_id.id,
                    "code": conv.disposition_id.code,
                    "name": conv.disposition_id.name,
                }
                if conv.disposition_id
                else None,
                "wrapup_notes": conv.wrapup_notes or "",
                "fcr": bool(conv.fcr),
                "priority": item.priority if item else 0,
                "entitlement": item.entitlement_note if item else "",
                "transcript": transcript,
                "customer_360": {
                    "open_orders": orders,
                    "devices": devices,
                    "recent_conversations": recent,
                },
            }
        }

    # ------------------------------------------------------------------
    # Writes
    # ------------------------------------------------------------------
    @http.route("/contact/portal/reply", type="jsonrpc", auth="user", readonly=False)
    def portal_reply(self, **kwargs):
        """Record an agent reply as a transcript turn (the system of record).

        Channel delivery is the adapter's job; this route never pretends a
        message left the estate. It refuses when the conversation is not an
        agent-handled one, or when another agent owns it.
        """
        denied = _staff_only()
        if denied:
            return denied
        conversation_id = _to_int(kwargs.get("conversation_id"))
        text = (kwargs.get("text") or "").strip()
        lang = kwargs.get("lang") if kwargs.get("lang") in ("bn", "en") else "bn"
        if not conversation_id:
            return _error("missing_conversation", "conversation_id is required")
        if not text:
            return _error("empty_reply", "Reply text is required")
        if len(text) > MAX_REPLY:
            return _error("reply_too_long", "Reply text is limited to %d characters" % MAX_REPLY)
        conv = request.env["fix.conversation"].browse(conversation_id)
        if not conv.exists():
            return _error("no_conversation", "Conversation not found")
        if conv.state != "with_agent":
            return _error(
                "not_with_agent",
                "Claim the conversation before replying (current state: %s)" % conv.state,
            )
        if conv.agent_id and conv.agent_id != request.env.user and not _is_supervisor():
            return _error(
                "not_your_conversation",
                "This conversation is handled by %s" % conv.agent_id.name,
            )
        try:
            conv.intake_message(text, speaker="agent", lang=lang)
        except (UserError, ValidationError, AccessError) as exc:
            return _error("reply_rejected", str(exc))
        turn = conv.turn_ids.sorted(key=lambda t: (t.sequence, t.id))[-1]
        return {
            "turn": {
                "seq": turn.sequence,
                "speaker": turn.speaker,
                "text": turn.text,
                "lang": turn.lang,
                "at": _dt(turn.spoken_at),
            },
            "conversation": {"id": conv.id, "state": conv.state},
        }

    @http.route("/contact/portal/wrapup", type="jsonrpc", auth="user", readonly=False)
    def portal_wrapup(self, **kwargs):
        """Close an agent conversation through the mandatory wrap-up gate.

        The model decides: disposition + >=20-character substantive notes +
        FCR, and for voice calls the BTRC recording-digest rule. Nothing is
        re-implemented or bypassed here.
        """
        denied = _staff_only()
        if denied:
            return denied
        conversation_id = _to_int(kwargs.get("conversation_id"))
        disposition_id = _to_int(kwargs.get("disposition_id"))
        notes = (kwargs.get("wrapup_notes") or "").strip()
        fcr = bool(kwargs.get("fcr"))
        if not conversation_id:
            return _error("missing_conversation", "conversation_id is required")
        if not disposition_id:
            return _error("missing_disposition", "Choose a disposition before closing")
        if len(notes) < 20:
            return _error(
                "wrapup_too_short",
                "Wrap-up notes must be at least 20 characters (%d given)" % len(notes),
            )
        conv = request.env["fix.conversation"].browse(conversation_id)
        if not conv.exists():
            return _error("no_conversation", "Conversation not found")
        try:
            conv.action_wrap_up(disposition_id=disposition_id, wrapup_notes=notes, fcr=fcr)
        except (UserError, ValidationError, AccessError) as exc:
            return _error("wrapup_rejected", str(exc))
        return {
            "conversation": {
                "id": conv.id,
                "state": conv.state,
                "disposition": conv.disposition_id.name or "",
                "fcr": bool(conv.fcr),
            }
        }
