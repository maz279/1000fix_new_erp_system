"""payment-connectors — gateway transport paths (INT-001..004) with HTTP mocked.

Covers the SSRF guard (production resolver mocked — no DNS), and the
initiate / query read-back / refund wire paths against a fake ``urlopen``.
Nothing here touches the network.
"""

from __future__ import annotations

import json
import logging
import socket
import sys
import urllib.error
import urllib.request
from pathlib import Path

import pytest

pytestmark = [pytest.mark.financial]

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import payment_connectors as pc

GATEWAY_ENVS = (
    "FIX_ENV",
    "FIX_PAYMENT_SANDBOX_MODE",
    "FIX_BKASH_API_URL",
    "FIX_BKASH_APP_KEY",
    "FIX_NAGAD_API_URL",
    "FIX_NAGAD_MERCHANT_KEY",
    "FIX_SSLCOMMERZ_API_URL",
    "FIX_SSLCOMMERZ_STORE_PASSWORD",
    "FIX_ROCKET_API_URL",
    "FIX_ROCKET_API_KEY",
)


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    for name in GATEWAY_ENVS:
        monkeypatch.delenv(name, raising=False)
    pc.reset_store()
    yield
    pc.reset_store()


class _FakeResponse:
    def __init__(self, body: bytes) -> None:
        self._body = body

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, *exc: object) -> bool:
        return False


def _fake_urlopen(monkeypatch, body: bytes = b"{}", exc: Exception | None = None) -> list:
    calls: list = []

    def fake(request, timeout):
        calls.append((request, timeout))
        if exc is not None:
            raise exc
        return _FakeResponse(body)

    monkeypatch.setattr(urllib.request, "urlopen", fake)
    return calls


def _wired_bkash(monkeypatch, url: str = "http://localhost:9/bkash") -> pc.BkashGateway:
    monkeypatch.setenv("FIX_BKASH_API_URL", url)
    monkeypatch.setenv("FIX_BKASH_APP_KEY", "unit-test-key")
    return pc.BkashGateway()


def _resolver(monkeypatch, addrs: list[str]) -> None:
    def fake_getaddrinfo(host, port):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (a, 0)) for a in addrs]

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)


# ------------------------------------------------------------------ SSRF guard


class TestUrlValidation:
    def test_non_http_scheme_refused(self):
        with pytest.raises(pc.Refused, match="scheme 'ftp' not allowed"):
            pc._validate_url("ftp://localhost/pay", "FIX_BKASH_API_URL")

    def test_embedded_credentials_refused(self):
        with pytest.raises(pc.Refused, match="credentials must not be embedded"):
            pc._validate_url("http://user:pw@localhost:9/pay", "FIX_BKASH_API_URL")

    def test_clean_local_url_returned_unchanged(self):
        url = "http://localhost:9/pay?merchant=1000fix"
        assert pc._validate_url(url, "FIX_BKASH_API_URL") == url

    def test_credential_query_parameter_names_the_keys(self):
        with pytest.raises(pc.Refused, match=r"\['api_key', 'signature'\]"):
            pc._validate_url("http://localhost:9/p?API_KEY=x&signature=y", "E")

    def test_production_requires_https(self, monkeypatch):
        monkeypatch.setenv("FIX_ENV", "production")
        with pytest.raises(pc.Refused, match="production gateways must be https"):
            pc._validate_url("http://checkout.pay.example.com/create", "E")

    def test_production_public_host_accepted(self, monkeypatch):
        monkeypatch.setenv("FIX_ENV", "production")
        _resolver(monkeypatch, ["8.8.8.8"])
        url = "https://checkout.pay.example.com/create"
        assert pc._validate_url(url, "E") == url

    def test_production_unresolvable_host_refused(self, monkeypatch):
        monkeypatch.setenv("FIX_ENV", "production")

        def boom(host, port):
            raise socket.gaierror("no such host")

        monkeypatch.setattr(socket, "getaddrinfo", boom)
        with pytest.raises(pc.Refused, match="does not resolve"):
            pc._validate_url("https://nowhere.invalid/create", "E")

    def test_unparseable_resolver_entries_are_skipped(self, monkeypatch):
        _resolver(monkeypatch, ["not-an-ip", "8.8.8.8"])
        assert pc._host_is_rejected_in_production("checkout.pay.example.com") is None

    def test_unparseable_then_private_entry_still_refused(self, monkeypatch):
        _resolver(monkeypatch, ["not-an-ip", "10.1.2.3"])
        reason = pc._host_is_rejected_in_production("internal.example.com")
        assert reason == "host 'internal.example.com' resolves to non-public address 10.1.2.3"

    def test_scoped_ipv6_link_local_refused(self, monkeypatch):
        _resolver(monkeypatch, ["fe80::1%eth0"])
        reason = pc._host_is_rejected_in_production("metadata.example.com")
        assert reason is not None and "fe80::1" in reason


# ------------------------------------------------------------------ initiate


class TestInitiateOverHttp:
    def test_initiate_posts_intent_and_returns_payment_id(self, monkeypatch):
        calls = _fake_urlopen(monkeypatch, json.dumps({"paymentID": "PAY-77"}).encode())
        result = _wired_bkash(monkeypatch).initiate(115000, "TRX-1", "https://cb/1")
        assert (result.gateway, result.status, result.trx_id) == ("bkash", "initiated", "TRX-1")
        assert result.detail == "PAY-77"
        assert result.raw_payload == {"paymentID": "PAY-77"}
        request, timeout = calls[0]
        assert timeout == 10
        assert request.full_url == "http://localhost:9/bkash"
        assert request.get_method() == "POST"
        assert request.get_header("Authorization") == "Bearer unit-test-key"
        assert json.loads(request.data) == {
            "amount": 115000,
            "currency": "BDT",
            "merchantInvoiceNumber": "TRX-1",
            "callbackURL": "https://cb/1",
        }

    def test_sslcommerz_session_key_used_when_no_payment_id(self, monkeypatch):
        _fake_urlopen(monkeypatch, json.dumps({"sessionkey": "SK-9"}).encode())
        monkeypatch.setenv("FIX_SSLCOMMERZ_API_URL", "http://localhost:9/ssl")
        result = pc.SslcommerzGateway().initiate(5000, "TRX-2", "https://cb")
        assert result.status == "initiated"
        assert result.detail == "SK-9"

    def test_empty_body_is_an_empty_intent(self, monkeypatch):
        _fake_urlopen(monkeypatch, b"")
        result = _wired_bkash(monkeypatch).initiate(100, "TRX-3", "https://cb")
        assert result.status == "initiated"
        assert result.detail == ""
        assert result.raw_payload == {}

    def test_network_timeout_is_unknown_not_failed(self, monkeypatch, caplog):
        _fake_urlopen(monkeypatch, exc=urllib.error.URLError("timed out"))
        with caplog.at_level(logging.WARNING, logger=pc.logger.name):
            result = _wired_bkash(monkeypatch).initiate(100, "TRX-4", "https://cb")
        assert result.status == "unknown"
        assert result.detail == "network uncertainty: <urlopen error timed out>"
        assert "bkash initiate timed out/errored" in caplog.text

    def test_gateway_5xx_is_unknown(self, monkeypatch):
        err = urllib.error.HTTPError("http://localhost:9/bkash", 503, "Unavailable", {}, None)
        _fake_urlopen(monkeypatch, exc=err)
        result = _wired_bkash(monkeypatch).initiate(100, "TRX-5", "https://cb")
        assert result.status == "unknown"
        assert "503" in result.detail

    def test_sandbox_mode_without_url_refuses_to_simulate(self, monkeypatch):
        """GV-009: sandbox mode with no sandbox endpoint must not mint an
        "initiated" intent — it refuses outright."""
        monkeypatch.setenv("FIX_PAYMENT_SANDBOX_MODE", "YES")
        gateway = pc.NagadGateway()
        assert gateway.sandbox_mode is True and gateway.configured is True
        with pytest.raises(pc.GatewayError, match="refusing to simulate a gateway result"):
            gateway.initiate(2500, "TRX-6", "https://cb")

    def test_simulated_outage_raises(self):
        gateway = pc.RocketGateway(sandbox_mode=True)
        gateway.set_simulated_outage(True)
        with pytest.raises(pc.GatewayError, match="rocket is unavailable"):
            gateway.initiate(100, "TRX-7", "https://cb")


# ------------------------------------------------------------------ query read-back


class TestQueryReadBack:
    def test_unconfigured_query_is_dry_run(self):
        result = pc.BkashGateway(sandbox_mode=False).query("TRX-1")
        assert (result.status, result.detail) == ("dry-run", "gateway unconfigured")

    @pytest.mark.parametrize("provider_status", ["Completed", "Successful"])
    def test_completed_ledger_entry_confirms(self, monkeypatch, provider_status):
        body = {"transactionStatus": provider_status, "statusMessage": "Paid"}
        calls = _fake_urlopen(monkeypatch, json.dumps(body).encode())
        result = _wired_bkash(monkeypatch).query("TRX 1")
        assert (result.status, result.detail, result.raw_payload) == ("confirmed", "Paid", body)
        request, timeout = calls[0]
        assert request.full_url == "http://localhost:9/bkash/query?trx_id=TRX%201"
        assert request.get_method() == "GET"
        assert request.get_header("Authorization") == "Bearer unit-test-key"
        assert timeout == 10

    def test_other_ledger_status_is_failed(self, monkeypatch):
        _fake_urlopen(monkeypatch, json.dumps({"transactionStatus": "Cancelled"}).encode())
        result = _wired_bkash(monkeypatch).query("TRX-2")
        assert (result.status, result.detail) == ("failed", "")

    def test_empty_ledger_body_is_failed(self, monkeypatch):
        _fake_urlopen(monkeypatch, b"")
        assert _wired_bkash(monkeypatch).query("TRX-3").status == "failed"

    def test_query_transport_error_is_unknown(self, monkeypatch):
        _fake_urlopen(monkeypatch, exc=ConnectionResetError("reset by peer"))
        result = _wired_bkash(monkeypatch).query("TRX-4")
        assert result.status == "unknown"
        assert result.detail == "query error: reset by peer"

    def test_query_ssrf_refusal_is_not_swallowed(self, monkeypatch):
        gateway = _wired_bkash(monkeypatch, url="http://evil.example.com/bkash")
        with pytest.raises(pc.Refused):
            gateway.query("TRX-5")


# ------------------------------------------------------------------ refund


class TestRefund:
    def test_refund_during_outage_raises(self):
        gateway = pc.BkashGateway(sandbox_mode=True)
        gateway.set_simulated_outage(True)
        with pytest.raises(pc.GatewayError, match="bkash refund unavailable"):
            gateway.refund("TRX-1", 100)

    def test_unconfigured_refund_is_an_honest_dry_run(self):
        """GV-009: an unconfigured gateway never reports "refunded" — no money
        was reversed; the decision is labelled dry-run."""
        result = pc.NagadGateway(sandbox_mode=False).refund("TRX-2", 2500)
        assert result.status == "dry-run"
        assert result.detail == (
            "refund of 2500 cents decided only, nothing transmitted "
            "(gateway unconfigured, reason: customer cancellation)"
        )

    def test_unconfigured_refund_keeps_given_reason(self):
        result = pc.NagadGateway(sandbox_mode=False).refund("TRX-2B", 2500, "duplicate")
        assert result.status == "dry-run"
        assert result.detail.endswith("(gateway unconfigured, reason: duplicate)")

    def test_sandbox_refund_without_url_refuses(self):
        gateway = pc.RocketGateway(sandbox_mode=True)
        with pytest.raises(pc.GatewayError, match="refusing to simulate a gateway result"):
            gateway.refund("TRX-3", 10, "duplicate")

    def test_refund_over_http_posts_reversal(self, monkeypatch):
        calls = _fake_urlopen(monkeypatch, json.dumps({"refundTrxId": "RF-1"}).encode())
        result = _wired_bkash(monkeypatch).refund("TRX-4", 25000, "warranty")
        assert (result.status, result.detail) == ("refunded", "RF-1")
        assert result.raw_payload == {"refundTrxId": "RF-1"}
        request, _ = calls[0]
        assert request.full_url == "http://localhost:9/bkash/refund"
        assert request.get_method() == "POST"
        assert json.loads(request.data) == {
            "trx_id": "TRX-4",
            "amount": 25000,
            "reason": "warranty",
        }

    def test_refund_empty_body_has_blank_reference(self, monkeypatch):
        _fake_urlopen(monkeypatch, b"")
        assert _wired_bkash(monkeypatch).refund("TRX-5", 1).detail == ""
