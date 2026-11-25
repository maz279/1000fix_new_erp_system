"""Channel adapters — INT-010 SMS · INT-012 WhatsApp · INT-013 email · push · in-app.

P04-M05-T03…T05.

Hard rules baked into every adapter:

1. Credentials come from environment variables only. Nothing in this file (or
   any test) contains a usable credential literal.
2. Outbound URLs are validated before use: non-production traffic may only
   reach loopback or compose-internal hostnames; production gateway URLs must
   be https and come from the environment. Redirects are never followed.
3. Non-production email routes to Mailpit (EP-11) — the address is an env var
   too, defaulting to the compose name `mailpit` on the compose network.
4. Without explicit configuration every adapter runs in dry-run mode: the send
   is decided, logged and counted, but no packet leaves the process. A local
   developer workstation cannot reach a customer (DE-12/DE-15 companions).

INT-011 (redundant SMS) is implemented as automatic secondary gateway failover
on primary route failure (Wave-2 CD-M02-06 / Milestone R03-M03).
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

# Compose-internal service names + loopback are the only non-prod destinations.
LOCAL_HOST_ALLOWLIST = frozenset(
    {"localhost", "127.0.0.1", "::1", "mailpit", "novu", "kong", "odoo"}
)

CHANNELS = ("sms", "whatsapp", "email", "push", "in_app", "alert")


class SendRefused(RuntimeError):
    """A send the adapter refused on policy grounds (SSRF guard, bad config)."""


@dataclass(frozen=True)
class DeliveryResult:
    channel: str
    status: str  # "delivered" | "failed" | "dry-run" | "not-implemented"
    provider_id: str = ""
    detail: str = ""


class _NeverFollowRedirects(urllib.request.HTTPRedirectHandler):
    """Hard rule 2: a gateway redirect is a policy violation. Declining it
    surfaces the 3xx as an HTTPError (a failed send) instead of following it
    to a destination the SSRF guard never validated."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


# urllib.request.urlopen()'s default opener FOLLOWS redirects; every gateway
# call goes through this opener instead.
_OPENER = urllib.request.build_opener(_NeverFollowRedirects)


def _gateway_reply(raw: bytes) -> dict:
    """The provider fields of a 2xx gateway reply. The gateway has already
    accepted the message, so a body that is not a JSON object only means "no
    provider id" — it must not turn a completed send into an exception (a
    re-delivery of the event would double-send)."""
    try:
        reply = json.loads(raw or b"{}")
    except ValueError:  # JSONDecodeError and UnicodeDecodeError alike
        return {}
    return reply if isinstance(reply, dict) else {}


def _host_is_rejected_in_production(host: str) -> str | None:
    """The SSRF rule's production half: reject loopback/private/reserved
    destinations even over https. A production gateway is a public host; a
    URL pointing at 10.x/127.x/169.254.x/[::1] (metadata services,
    internal admin panels) is an attack or a misconfiguration — either way
    it must never receive a customer notification. Returns the refusal
    reason, or None when the host is acceptable."""
    import ipaddress
    import socket

    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return f"host {host!r} does not resolve"
    for info in infos:
        addr = info[4][0]
        try:
            ip = ipaddress.ip_address(addr.split("%")[0])
        except ValueError:
            continue
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        ):
            return f"host {host!r} resolves to non-public address {ip}"
    return None


def _validate_outbound_url(url: str, env: str) -> str:
    """SSRF guard — scheme, host and port policy for every outbound call.

    Mirrors the hardening in libs/py/fix_residency (FF-09's client): local
    environments are jailed to loopback/compose names; production must be
    https AND resolve to a public address (loopback/private/reserved are
    rejected even over https). Credentials never appear in the URL itself.
    """
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in ("http", "https"):
        raise SendRefused(f"{env}: scheme {parsed.scheme!r} not allowed")
    host = (parsed.hostname or "").lower()
    fix_env = os.environ.get("FIX_ENV", "local")
    if fix_env != "production":
        if host not in LOCAL_HOST_ALLOWLIST:
            raise SendRefused(
                f"{env}: host {host!r} outside the local allowlist (FIX_ENV={fix_env})"
            )
    else:
        if parsed.scheme != "https":
            raise SendRefused(f"{env}: production gateways must be https, got {parsed.scheme}")
        private_reason = _host_is_rejected_in_production(host)
        if private_reason:
            raise SendRefused(f"{env}: {private_reason} (production SSRF guard)")
    if parsed.username or parsed.password:
        raise SendRefused(f"{env}: credentials must not be embedded in the URL")
    # Credential-bearing query parameters are refused too: credentials travel
    # in the Authorization header, never in a URL that ends up in logs.
    credential_keys = {"token", "apikey", "api_key", "access_token", "signature", "secret"}
    query_keys = {k.lower() for k, _ in urllib.parse.parse_qsl(parsed.query)}
    if query_keys & credential_keys:
        raise SendRefused(
            f"{env}: credential-like query parameter refused ({sorted(query_keys & credential_keys)})"
        )
    return url


class BaseChannel:
    """Common shape: config from env, dry-run default, one POST, no redirects."""

    channel = ""
    url_env = ""
    token_env = ""

    def __init__(self) -> None:
        self.url = os.environ.get(self.url_env, "").strip()
        self.token = os.environ.get(self.token_env, "").strip()

    @property
    def configured(self) -> bool:
        return bool(self.url)

    def render(self, body: str, variables: dict) -> str:
        out = body
        for key, value in variables.items():
            out = out.replace("{{" + key + "}}", str(value))
        return out

    def send(self, recipient: str, rendered: str, *, sms_route: str = "") -> DeliveryResult:
        raise NotImplementedError

    def _post(self, payload: dict) -> dict:
        if not self.url:
            raise RuntimeError("unconfigured channel must not reach _post")
        url = _validate_outbound_url(self.url, self.url_env)
        data = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.token:
            # The stripped value read in __init__ (the one checked above): a
            # trailing newline from a mounted secret must not reach the header.
            headers["Authorization"] = f"Bearer {self.token}"
        # _OPENER declines redirects: a gateway redirect is a policy
        # violation, not something to follow silently.
        request = urllib.request.Request(url, data=data, headers=headers, method="POST")  # noqa: S310 - URL checked by _validate_outbound_url()
        with _OPENER.open(request, timeout=10) as response:  # scheme/host validated above
            return _gateway_reply(response.read())

    def _deliver(self, payload: dict) -> DeliveryResult:
        """One gateway POST. A transport failure is a "failed" result so the
        dispatcher's retry-once + fallback ladder (NT-001 §4) runs, exactly as
        the SMS adapter does — never an exception that aborts the event."""
        try:
            result = self._post(payload)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            return DeliveryResult(self.channel, "failed", detail=f"gateway error: {exc}")
        return DeliveryResult(self.channel, "delivered", provider_id=str(result.get("id", "")))


class SMSChannel(BaseChannel):
    """INT-010 (primary) & INT-011 (redundant secondary) — masking/non-masking route per BD-01/BD-02."""

    channel = "sms"
    url_env = "FIX_SMS_GATEWAY_URL"  # INT-010 primary aggregator endpoint
    token_env = "FIX_SMS_GATEWAY_TOKEN"  # primary aggregator credential (env only)  # noqa: S105 - env-var NAME, not a secret value
    redundant_url_env = "FIX_SMS_REDUNDANT_GATEWAY_URL"  # INT-011 secondary aggregator endpoint
    redundant_token_env = "FIX_SMS_REDUNDANT_GATEWAY_TOKEN"  # secondary credential  # noqa: S105 - env-var NAME, not a secret value

    def __init__(self) -> None:
        super().__init__()
        self.redundant_url = os.environ.get(self.redundant_url_env, "").strip()
        self.redundant_token = os.environ.get(self.redundant_token_env, "").strip()

    @property
    def redundant_configured(self) -> bool:
        return bool(self.redundant_url)

    def _post_gateway(self, url: str, token: str, payload: dict) -> dict:
        validated_url = _validate_outbound_url(url, "SMS_REDUNDANT_GATEWAY")
        data = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        request = urllib.request.Request(validated_url, data=data, headers=headers, method="POST")  # noqa: S310 - URL checked by _validate_outbound_url()
        with _OPENER.open(request, timeout=10) as response:  # URL checked above, no redirects
            return _gateway_reply(response.read())

    def send(self, recipient: str, rendered: str, *, sms_route: str = "") -> DeliveryResult:
        # Policy guards run BEFORE the dry-run or send branches
        if sms_route not in ("masking", "non-masking"):
            raise SendRefused(f"sms send without a declared route (BD-01): {sms_route!r}")
        if sms_route == "non-masking" and "1000FiX" in rendered:
            # BD-03 guard: a numeric-sender message must not carry the
            # registered masking sender signature.
            raise SendRefused("promotional message carrying the masking signature (BD-02/BD-03)")

        payload = {
            "to": recipient,
            "message": rendered,
            "route": sms_route,
            "sender": "1000FiX" if sms_route == "masking" else "numeric",
        }

        # Dedicated INT-011 test mode: force redundant route
        if os.environ.get("FIX_SMS_REDUNDANT_ONLY", "") == "1":
            if not self.redundant_configured:
                return DeliveryResult(
                    "sms",
                    "dry-run",
                    detail="INT-011 redundant SMS dry-run (secondary gateway unconfigured)",
                )
            try:
                res = self._post_gateway(self.redundant_url, self.redundant_token, payload)
                return DeliveryResult(
                    "sms",
                    "delivered",
                    provider_id=str(res.get("id", "")),
                    detail="dispatched via INT-011 redundant secondary gateway",
                )
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                return DeliveryResult(
                    "sms", "failed", detail=f"INT-011 redundant gateway error: {e}"
                )

        # Normal route: attempt INT-010 primary first
        if self.configured:
            try:
                result = self._post(payload)
                return DeliveryResult("sms", "delivered", provider_id=str(result.get("id", "")))
            except (urllib.error.URLError, TimeoutError, OSError) as primary_err:
                # Primary failed: trigger INT-011 automatic failover if secondary configured
                if self.redundant_configured:
                    try:
                        res = self._post_gateway(self.redundant_url, self.redundant_token, payload)
                        return DeliveryResult(
                            "sms",
                            "delivered",
                            provider_id=str(res.get("id", "")),
                            detail="INT-011 failover after primary error",
                        )
                    except (urllib.error.URLError, TimeoutError, OSError) as sec_err:
                        return DeliveryResult(
                            "sms",
                            "failed",
                            detail=f"primary and redundant gateways failed: {sec_err}",
                        )
                return DeliveryResult(
                    "sms", "failed", detail=f"primary gateway failed: {primary_err}"
                )

        # If primary is unconfigured, check if redundant is configured
        if self.redundant_configured:
            try:
                res = self._post_gateway(self.redundant_url, self.redundant_token, payload)
                return DeliveryResult(
                    "sms",
                    "delivered",
                    provider_id=str(res.get("id", "")),
                    detail="INT-011 redundant secondary dispatch",
                )
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                return DeliveryResult("sms", "failed", detail=f"redundant gateway error: {e}")

        return DeliveryResult("sms", "dry-run", detail="gateway unconfigured (local default)")


class WhatsAppChannel(BaseChannel):
    """INT-012 — WhatsApp Business API (DEP-19 external dependency)."""

    channel = "whatsapp"
    url_env = "FIX_WHATSAPP_API_URL"
    token_env = "FIX_WHATSAPP_API_TOKEN"  # noqa: S105 - env-var NAME, not a secret value

    def send(self, recipient: str, rendered: str, *, sms_route: str = "") -> DeliveryResult:
        if not self.configured:
            return DeliveryResult("whatsapp", "dry-run", detail="WhatsApp API unconfigured")
        return self._deliver({"to": recipient, "type": "text", "text": {"body": rendered}})


class EmailChannel(BaseChannel):
    """INT-013 — in every non-production environment this routes to Mailpit (EP-11)."""

    channel = "email"
    url_env = "FIX_EMAIL_API_URL"  # compose: http://mailpit:8025/api/v1/send
    token_env = "FIX_EMAIL_API_TOKEN"  # noqa: S105 - env-var NAME, not a secret value

    def send(self, recipient: str, rendered: str, *, sms_route: str = "") -> DeliveryResult:
        if not self.configured:
            return DeliveryResult(
                "email", "dry-run", detail="email API unconfigured (EP-11 Mailpit in compose)"
            )
        return self._deliver(
            {
                "to": [recipient],
                "subject": (rendered.splitlines() or [""])[0][:120],
                "text": rendered,
            }
        )


class PushChannel(BaseChannel):
    """Push via the Novu gateway (P04-M05-T01)."""

    channel = "push"
    url_env = "FIX_NOVU_API_URL"
    token_env = "FIX_NOVU_API_TOKEN"  # noqa: S105 - env-var NAME, not a secret value

    def send(self, recipient: str, rendered: str, *, sms_route: str = "") -> DeliveryResult:
        if not self.configured:
            return DeliveryResult("push", "dry-run", detail="Novu unconfigured")
        return self._deliver({"subscriberId": recipient, "message": rendered})


class InAppChannel(BaseChannel):
    """NT-018 — inbox copy. Delivered by writing back through the outbox
    (AS-08) rather than a gateway POST; this adapter only renders."""

    channel = "in_app"
    url_env = "FIX_INAPP_API_URL"
    token_env = "FIX_INAPP_API_TOKEN"  # noqa: S105 - env-var NAME, not a secret value

    def send(self, recipient: str, rendered: str, *, sms_route: str = "") -> DeliveryResult:
        return DeliveryResult(
            "in_app", "dry-run", detail="in-app renders into the P01 inbox via the outbox"
        )


class AlertChannel(BaseChannel):
    """NT-021 — on-call alert channel (internal; CH-06)."""

    channel = "alert"
    url_env = "FIX_ALERT_WEBHOOK_URL"
    token_env = "FIX_ALERT_WEBHOOK_TOKEN"  # noqa: S105 - env-var NAME, not a secret value

    def send(self, recipient: str, rendered: str, *, sms_route: str = "") -> DeliveryResult:
        if not self.configured:
            return DeliveryResult("alert", "dry-run", detail="alert webhook unconfigured")
        return self._deliver({"text": rendered})


def build_channels() -> dict[str, BaseChannel]:
    return {
        cls.channel: cls()
        for cls in (
            SMSChannel,
            WhatsAppChannel,
            EmailChannel,
            PushChannel,
            InAppChannel,
            AlertChannel,
        )
    }
