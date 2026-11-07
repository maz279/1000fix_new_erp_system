# iot_ingest - the one way a gateway delivers a reading: POST /iot/v1/ingest.
#
# A07 audit (2026-11-07) finding 5: fix.iot.stream.ingest had no entry point in
# the product, and it checked the adapter's auth mode but never a credential.
# The caller is a machine, so the route is public (auth="none") and the key is
# the whole of its authority: the key must be the one stored, as a hash, on the
# adapter of the stream it names. So a key reaches its own adapter's streams and
# nothing else, and an adapter whose key was never rotated cannot be reached at
# all. Consent, the adapter's state and every other gate are in ingest() itself.
#
#   POST /iot/v1/ingest
#   X-Adapter-Key: <the key shown when it was rotated>
#   {"stream": "STRM/0001", "value": 21.5, "timestamp": "2026-11-07T04:00:00Z"}
#
# A database with several tenants is chosen by Odoo's X-Odoo-Database header.
import json
import logging
import math
from datetime import UTC, datetime

import psycopg2
from odoo import SUPERUSER_ID, http
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.http import request

from ..models.fix_iot_ops import IngestRefused, adapter_key_hash, adapter_key_matches

_logger = logging.getLogger(__name__)

# One reading is under a hundred bytes; nothing legitimate comes near this.
MAX_BODY_BYTES = 4096
MAX_STREAM_NAME = 128

# What the gateway is told: a machine-readable code, and words that name nothing
# the key holder is not entitled to (a consent refusal in the model names the
# customer; the response must not).
_STATUS = {
    "adapter_disabled": (403, "The protocol adapter is disabled."),
    "adapter_unauthenticated": (403, "The protocol adapter accepts no authentication."),
    "adapter_no_key": (401, "The key is missing or wrong."),
    "consent_required": (403, "No valid telemetry consent covers this device."),
    "signal_not_disclosed": (403, "The telemetry consent does not disclose this signal."),
    "stream_not_active": (409, "The stream is not active."),
    "invalid_value": (400, "The value must be a finite number."),
}


def _refusal(status, code, message):
    return status, {"error": code, "message": message}


def _unauthorized():
    return _refusal(401, "unauthorized", "The key is missing or wrong.")


def _parse_timestamp(value):
    """The source's own time stamp as naive UTC, as Odoo stores it. A stamp with
    no zone is taken as UTC. Raises ValueError when it is not a date and time."""
    if not isinstance(value, str):
        raise ValueError("not text")
    moment = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    if moment.tzinfo:
        moment = moment.astimezone(UTC).replace(tzinfo=None)
    return moment.replace(microsecond=0)


def _parse_body(raw):
    """(stream name, value, timestamp) or a refusal."""
    try:
        body = json.loads(raw)
    except ValueError:
        return None, _refusal(400, "invalid_json", "The body must be JSON.")
    if not isinstance(body, dict):
        return None, _refusal(400, "invalid_json", "The body must be a JSON object.")
    stream = body.get("stream")
    if not isinstance(stream, str) or not stream.strip() or len(stream) > MAX_STREAM_NAME:
        return None, _refusal(400, "invalid_stream", "Name the stream.")
    value = body.get("value")
    if isinstance(value, bool) or not isinstance(value, int | float) or not math.isfinite(value):
        return None, _refusal(400, "invalid_value", _STATUS["invalid_value"][1])
    stamp = body.get("timestamp")
    if stamp is not None:
        try:
            stamp = _parse_timestamp(stamp)
        except ValueError:
            return None, _refusal(400, "invalid_timestamp", "The timestamp must be ISO 8601.")
    return (stream.strip(), float(value), stamp), None


def _find_stream(env, name, key):
    """The stream called `name` whose adapter's key this is. The comparison is
    constant-time whatever is found, so a wrong key and an unknown stream look
    alike from outside."""
    hashed = adapter_key_hash(key or "")
    streams = (
        env["fix.iot.stream"].sudo().search([("name", "=", name), ("adapter_id", "!=", False)])
    )
    found = env["fix.iot.stream"]
    for stream in streams:
        if adapter_key_matches(stream.adapter_id.sudo().api_key_hash, hashed):
            found = found or stream
    if not streams:
        adapter_key_matches("0" * 64, hashed)
    return found


def handle_ingest(env, key, raw):
    """Authenticate, then record one reading as the superuser. Returns (HTTP
    status, JSON payload); no refusal and no fault leaves a stack trace."""
    env = env(user=SUPERUSER_ID, su=True)
    if not key:
        return _unauthorized()
    # The key is checked against the adapter of the stream the body names, so a
    # body that names none cannot be authenticated: it is refused for what it is.
    parsed, refusal = _parse_body(raw)
    if refusal:
        return refusal
    name, value, stamp = parsed
    stream = _find_stream(env, name, key)
    if not stream:
        return _unauthorized()
    try:
        with env.cr.savepoint():
            reading, alerts = stream.ingest(value, timestamp=stamp)
            env.flush_all()
    except IngestRefused as exc:
        status, message = _STATUS.get(exc.code, (403, "The reading was refused."))
        if exc.code == "adapter_no_key":
            return _unauthorized()
        return _refusal(status, exc.code, message)
    except ValidationError as exc:
        # A replay of a reading already held, or one dated in the future.
        _logger.info("Reading refused on stream %s: %s", stream.name, exc)
        return _refusal(409, "reading_rejected", "The reading is a duplicate or dated ahead.")
    except (UserError, AccessError) as exc:
        _logger.info("Reading refused on stream %s: %s", stream.name, exc)
        return _refusal(403, "refused", "The reading was refused.")
    except psycopg2.errors.SerializationFailure:
        raise  # Odoo retries the request
    except Exception:
        _logger.exception("IoT ingest failed on stream %s", stream.name)
        return _refusal(500, "server_error", "The reading could not be recorded.")
    return 200, {"reading": reading.id, "alerts": len(alerts)}


def read_body(httprequest):
    """The request body, or None when it is over MAX_BODY_BYTES or does not
    declare its length (Odoo's request reads an undeclared body up to 128 MB).
    Nothing is read before the declared length has been checked."""
    declared = httprequest.content_length
    if declared is None or declared > MAX_BODY_BYTES:
        return None
    raw = httprequest.get_data(cache=False)
    return None if len(raw) > MAX_BODY_BYTES else raw


class IotIngestController(http.Controller):
    @http.route(
        "/iot/v1/ingest",
        type="http",
        auth="none",
        methods=["POST"],
        csrf=False,
        save_session=False,
    )
    def ingest(self, **_kw):
        raw = read_body(request.httprequest)
        if raw is None:
            status, payload = _refusal(
                413, "too_large", "The body must declare its length and be at most 4 KB."
            )
        else:
            status, payload = handle_ingest(
                request.env, request.httprequest.headers.get("X-Adapter-Key"), raw
            )
        return request.make_json_response(payload, status=status)
