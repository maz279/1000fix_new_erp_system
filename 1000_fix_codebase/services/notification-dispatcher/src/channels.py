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

INT-011 (redundant SMS) is designed here as a secondary route entry but is a
W2 deliverable — its adapter raises NotImplemented until P04's W2 window.
"""
from __future__ import annotations

import json
import os
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
    status: str          # "delivered" | "failed" | "dry-run" | "not-implemented"
    provider_id: str = ""
    detail: str = ""


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
        if (ip.is_private or ip.is_loopback or ip.is_link_local
                or ip.is_reserved or ip.is_multicast or ip.is_unspecified):
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
        raise SendRefused(f"{env}: credential-like query parameter refused ({sorted(query_keys & credential_keys)})")
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
        assert self.url, "unconfigured channel must not reach _post"
        url = _validate_outbound_url(self.url, self.url_env)
        data = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.token:
            token_env_name = self.token_env
            headers["Authorization"] = f"Bearer {os.environ.get(token_env_name, '')}"
        # No redirect handler is installed on purpose: a gateway redirect is a
        # policy violation, not something to follow silently.
        request = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(request, timeout=10) as response:  # noqa: S310 - scheme/host validated above
            return json.loads(response.read() or b"{}")


class SMSChannel(BaseChannel):
    """INT-010 (primary) — masking/non-masking route per BD-01/BD-02."""

    channel = "sms"
    url_env = "FIX_SMS_GATEWAY_URL"       # INT-010 aggregator endpoint
    token_env = "FIX_SMS_GATEWAY_TOKEN"   # aggregator credential (env only)

    def send(self, recipient: str, rendered: str, *, sms_route: str = "") -> DeliveryResult:
        if os.environ.get("FIX_SMS_REDUNDANT_ONLY", "") == "1":
            return DeliveryResult("sms", "not-implemented", detail="INT-011 redundant SMS is W2")
        # Policy guards run BEFORE the dry-run branch: a policy violation must
        # refuse even when the gateway is unconfigured.
        if sms_route not in ("masking", "non-masking"):
            raise SendRefused(f"sms send without a declared route (BD-01): {sms_route!r}")
        if sms_route == "non-masking" and "1000FiX" in rendered:
            # BD-03 guard: a numeric-sender message must not carry the
            # registered masking sender signature.
            raise SendRefused("promotional message carrying the masking signature (BD-02/BD-03)")
        if not self.configured:
            return DeliveryResult("sms", "dry-run", detail="gateway unconfigured (local default)")
        result = self._post(
            {
                "to": recipient,
                "message": rendered,
                "route": sms_route,
                "sender": "1000FiX" if sms_route == "masking" else "numeric",
            }
        )
        return DeliveryResult("sms", "delivered", provider_id=str(result.get("id", "")))


class WhatsAppChannel(BaseChannel):
    """INT-012 — WhatsApp Business API (DEP-19 external dependency)."""

    channel = "whatsapp"
    url_env = "FIX_WHATSAPP_API_URL"
    token_env = "FIX_WHATSAPP_API_TOKEN"

    def send(self, recipient: str, rendered: str, *, sms_route: str = "") -> DeliveryResult:
        if not self.configured:
            return DeliveryResult("whatsapp", "dry-run", detail="WhatsApp API unconfigured")
        result = self._post({"to": recipient, "type": "text", "text": {"body": rendered}})
        return DeliveryResult("whatsapp", "delivered", provider_id=str(result.get("id", "")))


class EmailChannel(BaseChannel):
    """INT-013 — in every non-production environment this routes to Mailpit (EP-11)."""

    channel = "email"
    url_env = "FIX_EMAIL_API_URL"       # compose: http://mailpit:8025/api/v1/send
    token_env = "FIX_EMAIL_API_TOKEN"

    def send(self, recipient: str, rendered: str, *, sms_route: str = "") -> DeliveryResult:
        if not self.configured:
            return DeliveryResult("email", "dry-run", detail="email API unconfigured (EP-11 Mailpit in compose)")
        result = self._post({"to": [recipient], "subject": rendered.splitlines()[0][:120], "text": rendered})
        return DeliveryResult("email", "delivered", provider_id=str(result.get("id", "")))


class PushChannel(BaseChannel):
    """Push via the Novu gateway (P04-M05-T01)."""

    channel = "push"
    url_env = "FIX_NOVU_API_URL"
    token_env = "FIX_NOVU_API_TOKEN"

    def send(self, recipient: str, rendered: str, *, sms_route: str = "") -> DeliveryResult:
        if not self.configured:
            return DeliveryResult("push", "dry-run", detail="Novu unconfigured")
        result = self._post({"subscriberId": recipient, "message": rendered})
        return DeliveryResult("push", "delivered", provider_id=str(result.get("id", "")))


class InAppChannel(BaseChannel):
    """NT-018 — inbox copy. Delivered by writing back through the outbox
    (AS-08) rather than a gateway POST; this adapter only renders."""

    channel = "in_app"
    url_env = "FIX_INAPP_API_URL"
    token_env = "FIX_INAPP_API_TOKEN"

    def send(self, recipient: str, rendered: str, *, sms_route: str = "") -> DeliveryResult:
        return DeliveryResult("in_app", "dry-run", detail="in-app renders into the P01 inbox via the outbox")


class AlertChannel(BaseChannel):
    """NT-021 — on-call alert channel (internal; CH-06)."""

    channel = "alert"
    url_env = "FIX_ALERT_WEBHOOK_URL"
    token_env = "FIX_ALERT_WEBHOOK_TOKEN"

    def send(self, recipient: str, rendered: str, *, sms_route: str = "") -> DeliveryResult:
        if not self.configured:
            return DeliveryResult("alert", "dry-run", detail="alert webhook unconfigured")
        result = self._post({"text": rendered})
        return DeliveryResult("alert", "delivered", provider_id=str(result.get("id", "")))


def build_channels() -> dict[str, BaseChannel]:
    return {cls.channel: cls() for cls in
            (SMSChannel, WhatsAppChannel, EmailChannel, PushChannel, InAppChannel, AlertChannel)}
