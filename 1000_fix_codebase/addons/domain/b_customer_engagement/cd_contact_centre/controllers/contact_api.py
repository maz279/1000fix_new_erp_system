# P10 Contact Centre Console API — the W4 contract endpoints (PP5).
#
# The unified agent queue (30–80 agents), customer 360 and call control
# with the softphone integration SEAM: /contact/softphone returns the
# deployment's telephony endpoints from ir.config_parameter ONLY — no
# host literals in source, no credentials ever (they ride the agent's
# softphone client, not this API). G4-04/G4-05: the transcript IS the
# record; handoff keeps the full context.
from odoo import fields, http
from odoo.exceptions import UserError, ValidationError
from odoo.http import request

import json


def _error(code, message):
    return {"error": {"code": code, "message": message}}


class ContactApiController(http.Controller):
    """The P10 agent console API (W4 contract)."""

    @http.route("/contact/conversations", type="json", auth="user",
                readonly=True)
    def conversations(self, **kwargs):
        """The unified queue: live conversations across all channels,
        oldest first. The model has no agent-assignment column (agents
        claim via /contact/handoff), so the queue is the TEAM queue —
        `mine` narrowing ships with the assignment mapping (honest scope)."""
        domain = [("state", "in",
                   ("new", "with_ai", "with_agent"))]
        rows = request.env["fix.conversation"].search(
            domain, limit=100, order="started_at asc")
        result = [{
            "id": c.id,
            "channel": c.channel,
            "state": c.state,
            "intent": c.intent or "",
            "customer": c.customer_id.name or "",
            "contact_identity": c.contact_identity or "",
            "started_at": str(c.started_at or ""),
            "turns": len(c.turn_ids),
        } for c in rows]
        return {"conversations": result, "total": len(result)}

    @http.route("/contact/conversations/detail", type="json",
                auth="user", readonly=True)
    def conversation_detail(self, **kwargs):
        """Transcript + the customer-360 context (G4-04): open orders,
        registered devices, recent conversations. One query surface —
        the agent never hops screens to assemble context."""
        conversation_id = kwargs.get("conversation_id")
        if not conversation_id:
            return _error("missing_conversation",
                          "conversation_id is required")
        conv = request.env["fix.conversation"].browse(int(conversation_id))
        if not conv.exists():
            return _error("no_conversation", "Conversation not found")
        transcript = [{
            "seq": t.sequence,
            "speaker": t.speaker,
            "text": t.text,
            "lang": t.lang,
            "at": str(t.spoken_at or ""),
        } for t in conv.turn_ids.sorted(key=lambda t: t.sequence)]
        orders = []
        devices = []
        recent = []
        if conv.customer_id:
            orders = [{
                "ref": o.name, "state": o.state,
                "device": o.device_id.device_model_id.name or "",
            } for o in request.env["fix.service.order"].search(
                [("customer_id", "=", conv.customer_id.id)], limit=10)]
            devices = [{
                "model": d.device_model_id.name or "",
                "identifier": (d.imei_1 or d.serial_number or "")[:6] + "…",
                "warranty_status": d.warranty_status or "none",
            } for d in request.env["fix.device"].search(
                [("owner_id", "=", conv.customer_id.id)], limit=10)]
            recent = [{
                "id": c.id, "channel": c.channel, "state": c.state,
                "started_at": str(c.started_at or ""),
            } for c in request.env["fix.conversation"].search(
                [("customer_id", "=", conv.customer_id.id)], limit=10)]
        return {"conversation": {
            "id": conv.id,
            "channel": conv.channel,
            "state": conv.state,
            "intent": conv.intent or "",
            "customer": conv.customer_id.name or "",
            "transcript": transcript,
            "customer_360": {
                "open_orders": orders,
                "devices": devices,
                "recent_conversations": recent,
            },
        }}

    @http.route("/contact/handoff", type="json", auth="user",
                readonly=False)
    def handoff(self, **kwargs):
        """Call control (G4-05): claim (AI→agent), hand back with reason,
        or end the conversation. All transitions ride model writes that
        keep the transcript + handoff context."""
        conversation_id = kwargs.get("conversation_id")
        action = kwargs.get("action")
        if not conversation_id or action not in ("claim", "handoff", "end"):
            return _error("invalid_action",
                          "conversation_id + action "
                          "(claim|handoff|end) are required")
        conv = request.env["fix.conversation"].browse(int(conversation_id))
        if not conv.exists():
            return _error("no_conversation", "Conversation not found")
        try:
            if action == "claim":
                if conv.state not in ("new", "with_ai"):
                    return _error("not_claimable",
                                  "Only a new/AI conversation can be claimed")
                conv.write({"state": "with_agent"})
            elif action == "handoff":
                # back to the AI lane with a recorded reason
                conv.write({"state": "with_ai",
                            "handoff_reason": kwargs.get("reason", "")})
            else:  # end
                conv.write({"state": "resolved_agent",
                            "ended_at": fields.Datetime.now()})
        except (UserError, ValidationError) as exc:
            return _error("handoff_rejected", str(exc))
        return {"conversation": {"id": conv.id, "state": conv.state}}

    @http.route("/contact/softphone", type="json", auth="user",
                readonly=True)
    def softphone(self, **kwargs):
        """The softphone integration SEAM (PP5 special requirement):
        returns the deployment's telephony endpoints from system
        parameters ONLY. Unset keys surface as null — the console shows
        the click-to-copy fallback instead of inventing a host. No
        credentials ever cross this API."""
        params = request.env["ir.config_parameter"].sudo()
        return {"softphone": {
            "ws_url": params.get_param("fix_softphone_ws") or None,
            "sip_realm": params.get_param("fix_softphone_sip_realm") or None,
            "click_to_call_prefix": params.get_param(
                "fix_softphone_dial_prefix") or None,
            # integration hints for the console; the WebRTC handshake
            # itself lives in the softphone vendor's SDK
            "vendor": params.get_param("fix_softphone_vendor") or None,
        }}
