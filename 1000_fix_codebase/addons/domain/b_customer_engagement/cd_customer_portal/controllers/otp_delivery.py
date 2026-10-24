# OTP hand-off to the notification dispatcher's SMS channel (NT-007, INT-010).
#
# Integration choice (R01 follow-up, 2026-10-22): the code is POSTed straight
# to the dispatcher's ``/consume/once`` endpoint as one ``security.otp_requested``
# event. It is deliberately NOT published through ``libs/py/fix_events``: an
# outbox row is persisted in PostgreSQL and fanned out over Redis/Kafka (and
# every replay), so an OTP published there would sit in clear in the database,
# on the bus and in its archives. On the direct path the code exists only in
# this request and in the dispatcher's memory, which renders it into the SMS
# body, records "(redacted)" in its delivery tracking and excludes OTP events
# from its KPIs. Routing, the masking route (BD-01) and the gateway stay the
# dispatcher's decision ("one event, one decision"); without a configured SMS
# gateway the dispatcher runs dry-run (local/dev), with no packet leaving it.
#
# Nothing here logs or raises the code: error messages name the failure class
# only. The dispatcher URL comes from the environment (never the caller):
# ``FIX_NOTIFICATION_DISPATCHER_URL``, default the dispatcher's own loopback
# bind. Outside production it must be a loopback/compose host (DE-11).
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

DISPATCHER_URL_ENV = "FIX_NOTIFICATION_DISPATCHER_URL"
DEFAULT_DISPATCHER_URL = "http://127.0.0.1:8110"
CONSUME_PATH = "/consume/once"
OTP_EVENT = "security.otp_requested"
TIMEOUT_SECONDS = 5
LOCAL_DISPATCHER_HOSTS = frozenset({"localhost", "127.0.0.1", "::1", "notification-dispatcher"})
LANGUAGES = ("bn", "en")


class OtpDeliveryError(RuntimeError):
    """The code could not be handed to the dispatcher (message never holds the code)."""


class _RefuseRedirect(urllib.request.HTTPRedirectHandler):
    """A redirect from the dispatcher is refused, never followed with the code."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def dispatcher_endpoint():
    """The dispatcher's consume URL from the environment, validated (DE-11)."""
    url = (os.environ.get(DISPATCHER_URL_ENV) or DEFAULT_DISPATCHER_URL).strip().rstrip("/")
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise OtpDeliveryError(f"{DISPATCHER_URL_ENV} must be an http(s)://host URL")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise OtpDeliveryError(
            f"{DISPATCHER_URL_ENV} must not carry credentials, a query or a fragment"
        )
    fix_env = os.environ.get("FIX_ENV", "local")
    if fix_env != "production" and parsed.hostname.lower() not in LOCAL_DISPATCHER_HOSTS:
        raise OtpDeliveryError(
            f"DE-11: FIX_ENV={fix_env} only reaches a loopback/compose dispatcher host"
        )
    return url + CONSUME_PATH


def otp_event(phone, code, ttl_seconds, language="bn"):
    """The ``security.otp_requested`` event for one ``01XXXXXXXXX`` phone."""
    return {
        "event_type": OTP_EVENT,
        "payload": {
            # an OTP addresses the phone itself; no party is disclosed or needed
            "recipients": [
                {
                    "audience": "audience_any",
                    "party_id": 0,
                    "preferred_language": language if language in LANGUAGES else "bn",
                }
            ],
            "addresses": {"audience_any": "88" + phone},
            "variables": {"code": code, "valid_minutes": max(1, ttl_seconds // 60)},
            "event_time": time.time(),
        },
    }


def _post_json(url, payload):
    """One JSON POST without redirects; the decoded JSON answer."""
    opener = urllib.request.build_opener(_RefuseRedirect)
    req = urllib.request.Request(  # noqa: S310 - scheme/host validated by dispatcher_endpoint()
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with opener.open(req, timeout=TIMEOUT_SECONDS) as response:
        return json.loads(response.read() or b"{}")


def send_otp(phone, code, ttl_seconds, language="bn"):
    """Hand the code to the dispatcher; raise ``OtpDeliveryError`` unless it was
    accepted for delivery (sent, or dry-run where no gateway is configured)."""
    url = dispatcher_endpoint()
    try:
        answer = _post_json(url, otp_event(phone, code, ttl_seconds, language))
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        raise OtpDeliveryError(f"dispatcher unreachable ({type(exc).__name__})") from None
    decisions = answer.get("decisions") if isinstance(answer, dict) else None
    states = [d.get("state") for d in decisions or [] if isinstance(d, dict)]
    if "delivered" not in states:
        raise OtpDeliveryError(f"dispatcher did not deliver the code (states: {states})")
