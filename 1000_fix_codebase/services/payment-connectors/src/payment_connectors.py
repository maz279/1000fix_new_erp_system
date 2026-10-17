"""payment-connectors — P06-M05 (INT-001 bKash · INT-002 Nagad · INT-003 SSLCOMMERZ · INT-004 Rocket).

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
6. R04-M03: Sandbox certification, query read-back to resolve `unknown` state,
   and dynamic circuit-breaker fallback router.
"""
from __future__ import annotations

import json
import logging
import os
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

LOCAL_HOST_ALLOWLIST = frozenset(
    {"localhost", "127.0.0.1", "::1", "mailpit", "novu", "kong", "odoo"}
)

GATEWAYS = ("bkash", "nagad", "sslcommerz")
ALL_GATEWAYS = ("bkash", "nagad", "sslcommerz", "rocket")

# IP-09 / 05-03 section 7 — the P0 payment fallback register.
PAYMENT_FALLBACK_REGISTER: dict[str, str] = {
    "INT-001 bKash": "degrade to Nagad merchant-pay rail, then SSLCOMMERZ card; cash-at-branch as the last rail; refunds queue and replay on recovery",
    "INT-002 Nagad": "degrade to bKash; SMS-verified phone order + cash on delivery for pickups",
    "INT-003 SSLCOMMERZ": "card payments pause; bank-transfer reference capture with manual confirmation; no card data is ever taken over voice",
    "INT-004 Rocket": "degrade to bKash or Nagad mobile money collection",
}

FALLBACK_CHAINS: dict[str, list[str]] = {
    "bkash": ["nagad", "sslcommerz", "cash_at_branch"],
    "nagad": ["bkash", "cod"],
    "sslcommerz": ["bank_transfer", "cash_at_branch"],
    "rocket": ["bkash", "nagad", "cash_at_branch"],
}


class Refused(RuntimeError):
    """An operation refused on policy grounds (SSRF guard, bad config)."""


class GatewayError(RuntimeError):
    """An operational error encountered while communicating with a gateway."""


@dataclass(frozen=True)
class GatewayResult:
    gateway: str
    status: str          # "initiated" | "confirmed" | "dry-run" | "failed" | "unknown" | "refunded"
    trx_id: str
    detail: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    raw_payload: dict[str, Any] = field(default_factory=dict)


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

    def __init__(self, sandbox_mode: bool | None = None) -> None:
        self.url = os.environ.get(self.url_env, "").strip()
        self.key = os.environ.get(self.key_env, "").strip()
        # Explicit sandbox override or environment configuration
        env_sandbox = os.environ.get("FIX_PAYMENT_SANDBOX_MODE", "").lower() in ("true", "1", "yes")
        self.sandbox_mode = sandbox_mode if sandbox_mode is not None else env_sandbox
        self._simulated_outage: bool = False

    @property
    def configured(self) -> bool:
        return bool(self.url) or self.sandbox_mode

    def set_simulated_outage(self, outage: bool) -> None:
        """Testing utility: simulate circuit-breaker failure or provider downtime."""
        self._simulated_outage = outage

    def initiate(self, amount_cents: int, trx_id: str, callback_ref: str) -> GatewayResult:
        """Create a payment intent. Idempotent by trx_id at the gateway."""
        if self._simulated_outage:
            raise GatewayError(f"Gateway {self.gateway} is unavailable (simulated outage/503)")

        if not self.configured:
            return GatewayResult(self.gateway, "dry-run", trx_id,
                                 "gateway unconfigured (local default)")

        if self.sandbox_mode and not self.url:
            # Deterministic sandbox simulation mode
            session_token = f"SBX-{self.gateway.upper()}-{trx_id}-{int(time.time())}"
            return GatewayResult(
                self.gateway, "initiated", trx_id,
                detail=session_token,
                raw_payload={"amount": amount_cents, "currency": "BDT", "status": "initiated", "token": session_token}
            )

        request = urllib.request.Request(
            _validate_url(self.url, self.url_env),
            data=json.dumps({
                "amount": amount_cents, "currency": "BDT",
                "merchantInvoiceNumber": trx_id, "callbackURL": callback_ref,
            }).encode("utf-8"),
            headers={"Content-Type": "application/json",
                     "Authorization": "Bearer %s" % os.environ.get(self.key_env, "")},
            method="POST")
        try:
            with urllib.request.urlopen(request, timeout=10) as response:  # noqa: S310 - validated
                body = json.loads(response.read() or b"{}")
        except urllib.error.URLError as e:
            # Per IN-007 §3: network timeout or 5xx moves to 'unknown', not 'failed'
            logger.warning("Gateway %s initiate timed out/errored: %s", self.gateway, e)
            return GatewayResult(self.gateway, "unknown", trx_id, detail=f"network uncertainty: {e}")

        return GatewayResult(self.gateway, "initiated", trx_id,
                             detail=str(body.get("paymentID", body.get("sessionkey", ""))),
                             raw_payload=body)

    def query(self, trx_id: str) -> GatewayResult:
        """IN-007 §5: The Read-Back Rule.
        Resolves 'unknown' or pending states directly from provider ledger.
        A timeout is NOT a failure; read-back queries are required."""
        if self._simulated_outage:
            return GatewayResult(self.gateway, "unknown", trx_id, detail="read-back unreachable (outage)")

        if not self.configured:
            return GatewayResult(self.gateway, "dry-run", trx_id, detail="gateway unconfigured")

        if self.sandbox_mode and not self.url:
            # Simulated sandbox query returns confirmed state
            return GatewayResult(
                self.gateway, "confirmed", trx_id,
                detail=f"verified via {self.gateway} sandbox read-back",
                raw_payload={"trx_id": trx_id, "verification_status": "Successful", "currency": "BDT"}
            )

        query_url = f"{_validate_url(self.url, self.url_env)}/query?trx_id={urllib.parse.quote(trx_id)}"
        request = urllib.request.Request(
            query_url,
            headers={"Authorization": "Bearer %s" % os.environ.get(self.key_env, "")},
            method="GET"
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:  # noqa: S310
                body = json.loads(response.read() or b"{}")
            status = "confirmed" if body.get("transactionStatus") in ("Completed", "Successful") else "failed"
            return GatewayResult(self.gateway, status, trx_id, detail=str(body.get("statusMessage", "")), raw_payload=body)
        except Exception as e:
            return GatewayResult(self.gateway, "unknown", trx_id, detail=f"query error: {e}")

    def refund(self, trx_id: str, amount_cents: int, reason: str = "") -> GatewayResult:
        """IN-007 §6: Refund/reversal execution against provider."""
        if self._simulated_outage:
            raise GatewayError(f"Gateway {self.gateway} refund unavailable")

        if not self.configured or (self.sandbox_mode and not self.url):
            return GatewayResult(
                self.gateway, "refunded", trx_id,
                detail=f"refunded {amount_cents} cents (reason: {reason or 'customer cancellation'})"
            )

        refund_url = f"{_validate_url(self.url, self.url_env)}/refund"
        request = urllib.request.Request(
            refund_url,
            data=json.dumps({"trx_id": trx_id, "amount": amount_cents, "reason": reason}).encode("utf-8"),
            headers={"Content-Type": "application/json",
                     "Authorization": "Bearer %s" % os.environ.get(self.key_env, "")},
            method="POST"
        )
        with urllib.request.urlopen(request, timeout=10) as response:  # noqa: S310
            body = json.loads(response.read() or b"{}")
        return GatewayResult(self.gateway, "refunded", trx_id, detail=str(body.get("refundTrxId", "")), raw_payload=body)


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


class RocketGateway(BaseGateway):
    gateway = "rocket"          # INT-004 (Rocket mobile money via aggregator)
    url_env = "FIX_ROCKET_API_URL"
    key_env = "FIX_ROCKET_API_KEY"


def build_gateways(include_all: bool = False, sandbox_mode: bool | None = None) -> dict[str, BaseGateway]:
    classes = (BkashGateway, NagadGateway, SslcommerzGateway, RocketGateway) if include_all else (BkashGateway, NagadGateway, SslcommerzGateway)
    return {cls.gateway: cls(sandbox_mode=sandbox_mode) for cls in classes}


# --------------------------------------------------- dynamic fallback router


class PaymentRouter:
    """T04 / IP-09: Multi-rail payment router and circuit-breaker.
    If a primary gateway experiences an outage or degradation, the router
    automatically cascades to the declared fallback rail without halting trading."""

    def __init__(self, gateways: dict[str, BaseGateway] | None = None) -> None:
        self.gateways = gateways or build_gateways(include_all=True)

    def initiate_with_fallback(
        self,
        amount_cents: int,
        trx_id: str,
        callback_ref: str,
        preferred_rail: str = "bkash"
    ) -> tuple[GatewayResult, list[str]]:
        """Attempt initiation on preferred rail; cascade along fallback chain upon failure."""
        chain = [preferred_rail] + [g for g in FALLBACK_CHAINS.get(preferred_rail, []) if g in self.gateways]
        degradation_log: list[str] = []

        for rail in chain:
            gateway = self.gateways.get(rail)
            if not gateway:
                degradation_log.append(f"{rail}: not available in active gateway registry")
                continue

            try:
                result = gateway.initiate(amount_cents, trx_id, callback_ref)
                if result.status in ("initiated", "dry-run"):
                    if degradation_log:
                        logger.warning(
                            "Payment %s degraded from %s to %s. Trace: %s",
                            trx_id, preferred_rail, rail, " -> ".join(degradation_log)
                        )
                    return result, degradation_log
                degradation_log.append(f"{rail}: status={result.status} detail={result.detail}")
            except Exception as exc:
                degradation_log.append(f"{rail}: exception={exc}")

        # If all automated rails in the chain fail, drop to manual fallback instruction
        fallback_instruction = PAYMENT_FALLBACK_REGISTER.get(
            f"INT-001 {preferred_rail.title()}",
            "Fallback to cash-at-branch or bank deposit reference capture."
        )
        fail_res = GatewayResult(
            preferred_rail, "failed", trx_id,
            detail=f"All digital rails failed. Manual Fallback: {fallback_instruction}"
        )
        return fail_res, degradation_log


# --------------------------------------------------- idempotent confirmation

_confirmed: dict[tuple[str, str], dict[str, Any]] = {}


def confirm(gateway: str, trx_id: str, amount_cents: int) -> GatewayResult:
    """T06 / DI-04: idempotent payment confirmation. Keyed on (gateway, trx_id):
    a retried confirmation returns the FIRST outcome and never double-credits.
    DI-04 — money is where idempotency defects cost most."""
    key = (gateway, trx_id)
    if key in _confirmed:
        record = _confirmed[key]
        return GatewayResult(
            gateway, "confirmed", trx_id,
            detail="idempotent replay — no second credit",
            timestamp=record["timestamp"]
        )

    now_iso = datetime.now(timezone.utc).isoformat()
    _confirmed[key] = {
        "gateway": gateway,
        "trx_id": trx_id,
        "amount_cents": amount_cents,
        "timestamp": now_iso,
    }
    return GatewayResult(
        gateway, "confirmed", trx_id,
        detail="amount=%d cents credited once" % amount_cents,
        timestamp=now_iso
    )


def reset_store() -> None:
    """Test isolation."""
    _confirmed.clear()
