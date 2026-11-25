# inbound_webhook — M28 FR-IPF-037/038: POST /hooks/v1/inbound/<code>.
#
# M28 capture pass 2 (2026-11-19): nothing received a third-party webhook. A
# source an Integration Admin registered, and a second one took live, posts here
# signed the Standard Webhooks way, the same scheme the outbound dispatcher signs
# with (AP-004 s4.4):
#
#   POST /hooks/v1/inbound/bkash-payments
#   webhook-id: msg_2Kd8...                      (the sender's message id)
#   webhook-timestamp: 1763520000                (unix seconds)
#   webhook-signature: v1,<base64 HMAC-SHA256(secret, "<id>.<timestamp>.<raw body>")>
#   {"...": "..."}                               (a JSON object, not interpreted)
#
# Verified posts become ONE event, integration.webhook_received, carrying the
# source's owning module and route key; the owning module consumes it
# (FR-IPF-038: routed, never interpreted here). A message id is accepted once per
# source; a repeat is answered with the first result (IP-04 idempotent
# ingestion). Every refusal is recorded with its reason, except for an unknown
# code, which gets the same answer as a bad signature so that the endpoint does
# not reveal which sources exist.
import hashlib
import hmac
import json
import logging
from datetime import UTC, datetime

from odoo import SUPERUSER_ID, http
from odoo.http import request

from libs.py.fix_events import publish

from ..models.fix_integration_dispatch import _sign, _vault_secret

_logger = logging.getLogger(__name__)

MAX_BODY_BYTES = 256 * 1024


def _reply(http_status, **body):
    return request.make_json_response(body, status=http_status)


def _signature_ok(secret, message_id, timestamp, body, presented):
    expected = _sign(secret, message_id, timestamp, body)
    return any(
        hmac.compare_digest(expected, candidate)
        for candidate in (presented or "").split()
        if candidate.startswith("v1,")
    )


class InboundWebhook(http.Controller):
    @http.route(
        "/hooks/v1/inbound/<string:code>",
        type="http",
        auth="none",
        methods=["POST"],
        csrf=False,
        save_session=False,
    )
    def inbound(self, code, **kwargs):
        env = request.env(user=SUPERUSER_ID, su=True)
        return receive(env, code, request.httprequest.headers, request.httprequest.get_data())


def receive(env, code, headers, body):
    """The receiver itself, callable without HTTP (tests drive it directly)."""
    Receipt = env["fix.webhook.inbound.event"]
    source = env["fix.webhook.inbound.source"].search([("code", "=", code)], limit=1)
    message_id = (headers.get("webhook-id") or "").strip()[:200]
    stamp = (headers.get("webhook-timestamp") or "").strip()
    body = body or b""
    digest = hashlib.sha256(body).hexdigest()

    def refuse(http_status, reason, error):
        if source:
            Receipt.create(
                {
                    "source_id": source.id,
                    "message_id": message_id or "(none)",
                    "outcome": "rejected",
                    "reason": reason[:250],
                    "body_bytes": len(body),
                    "payload_sha256": digest,
                }
            )
        _logger.warning("inbound webhook %r refused: %s", code, reason)
        return _reply(http_status, error=error, message=reason)

    if not source:
        _logger.warning("inbound webhook: unknown code %r", code)
        return _reply(401, error="unauthorized", message="Unknown source or bad signature")
    if len(body) > MAX_BODY_BYTES:
        return refuse(413, "body over %d bytes" % MAX_BODY_BYTES, "too_large")
    if source.state != "active":
        return refuse(403, "source is %s" % source.state, "source_unavailable")
    secret = _vault_secret(source.secret_ref)
    if not secret:
        return refuse(503, "no secret value behind %s" % source.secret_ref, "not_configured")
    if not message_id or not stamp.isdigit():
        return refuse(400, "webhook-id and webhook-timestamp are required", "bad_request")
    signed_at = datetime.fromtimestamp(int(stamp), UTC).replace(tzinfo=None)
    skew = abs((datetime.now(UTC).replace(tzinfo=None) - signed_at).total_seconds())
    if skew > source.replay_window_seconds:
        return refuse(401, "signed %ds away from now" % skew, "stale")
    if not _signature_ok(secret, message_id, stamp, body, headers.get("webhook-signature")):
        return refuse(401, "signature does not verify", "unauthorized")

    first = Receipt.search(
        [
            ("source_id", "=", source.id),
            ("message_id", "=", message_id),
            ("outcome", "=", "accepted"),
        ],
        limit=1,
    )
    if first:
        Receipt.create(
            {
                "source_id": source.id,
                "message_id": message_id,
                "signed_at": signed_at,
                "outcome": "duplicate",
                "reason": "answered from receipt %d" % first.id,
                "body_bytes": len(body),
                "payload_sha256": digest,
            }
        )
        return _reply(
            200, status="duplicate", receipt=first.id, event_id=first.outbox_event_id.event_id
        )
    try:
        content = json.loads(body or b"null")
    except ValueError:
        content = None
    if not isinstance(content, dict):
        return refuse(400, "the body is not a JSON object", "bad_request")

    receipt = Receipt.create(
        {
            "source_id": source.id,
            "message_id": message_id,
            "signed_at": signed_at,
            "outcome": "accepted",
            "body_bytes": len(body),
            "payload_sha256": digest,
        }
    )
    event_id = publish(
        source.with_company(source.company_id).env,
        "integration.webhook_received",
        "fix.webhook.inbound.event",
        receipt.id,
        {
            "source": source.code,
            "owning_module": source.owning_module,
            "route_key": source.route_key,
            "message_id": message_id,
            "body": content,
        },
    )
    event = env["fix.event.outbox"].search([("event_id", "=", event_id)], limit=1)
    receipt.write({"outbox_event_id": event.id})
    return _reply(200, status="accepted", receipt=receipt.id, event_id=event_id)
