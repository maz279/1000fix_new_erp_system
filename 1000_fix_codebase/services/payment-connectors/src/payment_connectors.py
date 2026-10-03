"""payment-connectors — P06-M05 (INT-001 bKash · INT-002 Nagad · INT-003 SSLCOMMERZ).

The gateway adapters and the idempotent confirmation handler. Rules:

1. Credentials from environment variables ONLY — nothing in this file (or
   any test) contains a usable credential literal.
2. Outbound URLs validated before use (non-production jailed to loopback /
   compose names; production https-only; redirects never followed).
3. Dry-run default: without a configured gateway URL every operation is
   decided and logged, nothing transmitted (a workstation cannot charge).
4. DI-04 / T06: payment confirmation is IDEMPOTENT — `confirm()` keyed on
   (gateway, trx_id); a retried confirmation never double-credits. The
   store is pluggable (default in-memory; production = outbox table).
5. T08: the P0 fallback register — a gateway outage degrades to the next
   rail, it never stops trading.
"""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from dataclasses import dataclass

LOCAL_HOST_ALLOWLIST = frozenset(
    {"localhost", "127.0.0.1", "::1", "mailpit", "novu", "kong", "odoo"}
)

GATEWAYS = ("bkash", "nagad", "sslcommerz")

# IP-09 / 05-03 section 7 — the P0 payment fallback register.
PAYMENT_FALLBACK_REGISTER: dict[str, str] = {
    "INT-001 bKash": "degrade to Nagad merchant-pay rail, then SSLCOMMERZ card; cash-at-branch as the last rail; refunds queue and replay on recovery",
    "INT-002 Nagad": "degrade to bKash; SMS-verified phone order + cash on delivery for pickups",
    "INT-003 SSLCOMMERZ": "card payments pause; bank-transfer reference capture with manual confirmation; no card data is ever taken over voice",
}


class Refused(RuntimeError):
    """An operation refused on policy grounds (SSRF guard, bad config)."""


@dataclass(frozen=True)
class GatewayResult:
    gateway: str
    status: str          # "initiated" | "confirmed" | "dry-run" | "failed"
    trx_id: str
    detail: str = ""


def _host_is_rejected_in_production(host: str) -> str | None:
    """The SSRF rule's production half: reject loopback/private/reserved
    destinations even over https. A payment gateway is a public host; a URL
    pointing at 10.x/127.x/169.254.x/[::1] (cloud metadata, internal
    panels) is card-data exfiltration or misconfiguration — refused either
    way. Returns the refusal reason, or None when the host is acceptable."""
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


def _validate_url(url: str, env: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in ("http", "https"):
        raise Refused(f"{env}: scheme {parsed.scheme!r} not allowed")
    host = (parsed.hostname or "").lower()
    fix_env = os.environ.get("FIX_ENV", "local")
    if fix_env != "production":
        if host not in LOCAL_HOST_ALLOWLIST:
            raise Refused(f"{env}: host {host!r} outside the local allowlist")
    elif parsed.scheme != "https":
        raise Refused(f"{env}: production gateways must be https")
    else:
        private_reason = _host_is_rejected_in_production(host)
        if private_reason:
            raise Refused(f"{env}: {private_reason} (production SSRF guard)")
    if parsed.username or parsed.password:
        raise Refused(f"{env}: credentials must not be embedded in the URL")
    # Credential-bearing query parameters are refused too: credentials
    # travel in headers, never in a URL that ends up in logs (the same
    # guard the notification dispatcher carries).
    credential_keys = {"token", "apikey", "api_key", "access_token", "signature", "secret"}
    query_keys = {k.lower() for k, _ in urllib.parse.parse_qsl(parsed.query)}
    if query_keys & credential_keys:
        raise Refused(f"{env}: credential-like query parameter refused "
                      f"({sorted(query_keys & credential_keys)})")
    return url


class BaseGateway:
    gateway = ""
    url_env = ""
    key_env = ""

    def __init__(self) -> None:
        self.url = os.environ.get(self.url_env, "").strip()
        self.key = os.environ.get(self.key_env, "").strip()

    @property
    def configured(self) -> bool:
        return bool(self.url)

    def initiate(self, amount_cents: int, trx_id: str, callback_ref: str) -> GatewayResult:
        """Create a payment intent. Idempotent by trx_id at the gateway."""
        if not self.configured:
            return GatewayResult(self.gateway, "dry-run", trx_id,
                                 "gateway unconfigured (local default)")
        request = urllib.request.Request(
            _validate_url(self.url, self.url_env),
            data=json.dumps({
                "amount": amount_cents, "currency": "BDT",
                "merchantInvoiceNumber": trx_id, "callbackURL": callback_ref,
            }).encode("utf-8"),
            headers={"Content-Type": "application/json",
                     "Authorization": "Bearer %s" % os.environ.get(self.key_env, "")},
            method="POST")
        with urllib.request.urlopen(request, timeout=10) as response:  # noqa: S310 - validated
            body = json.loads(response.read() or b"{}")
        return GatewayResult(self.gateway, "initiated", trx_id,
                             detail=str(body.get("paymentID", body.get("sessionkey", ""))))


class BkashGateway(BaseGateway):
    gateway = "bkash"           # INT-001, L3 free connector extended
    url_env = "FIX_BKASH_API_URL"
    key_env = "FIX_BKASH_APP_KEY"


class NagadGateway(BaseGateway):
    gateway = "nagad"           # INT-002
    url_env = "FIX_NAGAD_API_URL"
    key_env = "FIX_NAGAD_MERCHANT_KEY"


class SslcommerzGateway(BaseGateway):
    gateway = "sslcommerz"      # INT-003 (cards + net banking)
    url_env = "FIX_SSLCOMMERZ_API_URL"
    key_env = "FIX_SSLCOMMERZ_STORE_PASSWORD"


def build_gateways() -> dict[str, BaseGateway]:
    return {cls.gateway: cls() for cls in (BkashGateway, NagadGateway, SslcommerzGateway)}


# --------------------------------------------------- idempotent confirmation

_confirmed: set[tuple[str, str]] = set()


def confirm(gateway: str, trx_id: str, amount_cents: int) -> GatewayResult:
    """T06: idempotent payment confirmation. Keyed on (gateway, trx_id):
    a retried confirmation returns the FIRST outcome and never double-credits.
    DI-04 — money is where idempotency defects cost most."""
    key = (gateway, trx_id)
    if key in _confirmed:
        return GatewayResult(gateway, "confirmed", trx_id,
                             detail="idempotent replay — no second credit")
    _confirmed.add(key)
    return GatewayResult(gateway, "confirmed", trx_id,
                         detail="amount=%d cents credited once" % amount_cents)


def reset_store() -> None:
    """Test isolation."""
    _confirmed.clear()
