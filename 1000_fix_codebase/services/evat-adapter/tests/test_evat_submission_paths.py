"""INT-038 NBR e-VAT (IVAS) — nil-return invariants, the production REST
submission path (NBR IVAS HTTP mocked, no network), batch export, and the
package entry point (src/__init__.py, loaded under a unique name)."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import logging
import sys
import urllib.error
import urllib.request
from decimal import Decimal
from pathlib import Path

import pytest

pytestmark = [pytest.mark.tax, pytest.mark.financial]

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

import evat_client as ec

D = Decimal
BIN = "1234567890123"
API = "https://ivas.nbr.example/gateway"


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    for name in ("FIX_ENV", "FIX_NBR_EVAT_API_URL", "FIX_NBR_EVAT_API_KEY"):
        monkeypatch.delenv(name, raising=False)


# Synthetic test declarant (the builder no longer defaults one).
DECLARANT = {
    "declarant_name": "Test Declarant",
    "declarant_designation": "Test Tax Manager",
    "declarant_nid": "1234567890",
}


def _payload(client: ec.Int038EvatClient, **overrides) -> ec.IvasMushak91Payload:
    kwargs = {
        "taxpayer_bin": BIN,
        "taxpayer_name": "1000 FiX Services Ltd.",
        "tax_period": "2026-09",
        "register_totals": {"standard_15": (D("100000.00"), D("15000.00"))},
        "input_vat": D("4000.00"),
        **DECLARANT,
    }
    kwargs.update(overrides)
    return client.build_payload(**kwargs)


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


@pytest.fixture
def live_client(monkeypatch) -> ec.Int038EvatClient:
    monkeypatch.setenv("FIX_ENV", "production")
    client = ec.Int038EvatClient(api_url=API, api_key="unit-test-key")
    assert client.sandbox_mode is False
    return client


# ------------------------------------------------------------------ nil-return rules


class TestNilReturnInvariants:
    def test_zero_activity_filed_as_normal_is_rejected(self):
        payload = _payload(ec.Int038EvatClient(), register_totals={}, input_vat=D("0"))
        payload.return_type = "normal"
        assert ec.validate_ivas_payload(payload) == [
            "Zero activity period must be filed with return_type='nil'"
        ]

    def test_trading_period_filed_as_nil_is_rejected(self):
        payload = _payload(ec.Int038EvatClient())
        payload.return_type = "nil"
        assert ec.validate_ivas_payload(payload) == [
            "Return with non-zero turnover, input VAT, SD or adjustments cannot be filed as nil"
        ]

    def test_regression_adjustment_only_period_is_not_a_nil_return(self):
        """Regression: with no sales/purchases but a 500.00 increasing
        adjustment, build_payload marked the return "nil" while declaring
        net_tax_payable=500.00 — and validation accepted it. A nil return
        declares no tax; this one under-declared a liability."""
        payload = _payload(
            ec.Int038EvatClient(),
            register_totals={},
            input_vat=D("0.00"),
            increasing_adjustments=D("500.00"),
        )
        assert payload.return_type == "normal"
        assert payload.net_tax_payable == 500.00
        assert ec.validate_ivas_payload(payload) == []

    def test_regression_hand_built_nil_with_decreasing_adjustment_is_rejected(self):
        payload = _payload(
            ec.Int038EvatClient(),
            register_totals={},
            input_vat=D("0.00"),
            decreasing_adjustments=D("250.00"),
        )
        payload.return_type = "nil"
        assert ec.validate_ivas_payload(payload) == [
            "Return with non-zero turnover, input VAT, SD or adjustments cannot be filed as nil"
        ]

    def test_build_payload_lines_and_totals(self):
        payload = _payload(
            ec.Int038EvatClient(),
            register_totals={
                "zero_rated": (D("5000.00"), D("0.00")),
                "standard_15": (D("100000.00"), D("15000.00")),
            },
            treasury_challan_no="TR-1",
            declarant_nid="1234567890",
        )
        assert [line.treatment for line in payload.output_supplies] == [
            "standard_15",
            "zero_rated",
        ]
        assert payload.total_taxable_value == 105000.00
        assert payload.total_output_vat == 15000.00
        assert payload.net_tax_payable == 11000.00
        assert payload.total_sd_payable == 0.0
        assert payload.to_dict()["treasury_challan_no"] == "TR-1"
        assert json.loads(payload.to_json())["declarant_nid"] == "1234567890"


# ------------------------------------------------------------------ submission


class TestClientConfiguration:
    def test_explicit_url_outside_production_stays_in_sandbox(self):
        assert ec.Int038EvatClient(api_url=API).sandbox_mode is True

    def test_production_reads_url_and_key_from_environment(self, monkeypatch):
        monkeypatch.setenv("FIX_ENV", "production")
        monkeypatch.setenv("FIX_NBR_EVAT_API_URL", f"  {API}  ")
        monkeypatch.setenv("FIX_NBR_EVAT_API_KEY", "env-key")
        client = ec.Int038EvatClient()
        assert (client.api_url, client.api_key, client.sandbox_mode) == (API, "env-key", False)

    def test_production_without_url_is_sandbox(self, monkeypatch):
        monkeypatch.setenv("FIX_ENV", "production")
        assert ec.Int038EvatClient().sandbox_mode is True


class TestSandboxSubmission:
    """GV-009: the old client minted "NBR-IVAS-<period>-M91-<digest>"
    acceptance tokens offline. Unconfigured must now mean NOT accepted — the
    only acknowledgement is one captured from a real submission."""

    def test_unconfigured_client_never_mints_an_acceptance_token(self):
        client = ec.Int038EvatClient()
        payload = _payload(client)
        result = client.submit_return(payload)
        digest = hashlib.sha256(payload.to_json().encode("utf-8")).hexdigest()
        assert result.file_hash == digest  # the return itself is still hashed
        assert result.status == "NOT_SUBMITTED"
        assert result.ack_token == ""
        assert result.validation_messages == [
            "NBR endpoint not configured - return submission NOT accepted"
        ]
        assert result.raw_response == {}

    def test_configured_url_submits_over_the_wire_even_outside_production(self, monkeypatch):
        """A URL outside production is a sandbox ENDPOINT: the submission
        goes over HTTP and the acknowledgement comes from that endpoint."""
        calls = _fake_urlopen(
            monkeypatch, json.dumps({"acknowledgementToken": "SBX-ACK-1"}).encode()
        )
        client = ec.Int038EvatClient(api_url=API, api_key="unit-test-key")
        assert client.sandbox_mode is True
        result = client.submit_return(_payload(client))
        assert (result.status, result.ack_token) == ("ACCEPTED", "SBX-ACK-1")
        request, _timeout = calls[0]
        assert request.full_url == f"{API}/api/v1/mushak-9-1/submit"
        assert request.get_method() == "POST"


class TestProductionSubmission:
    def test_acknowledged_return_is_accepted(self, monkeypatch, live_client):
        calls = _fake_urlopen(
            monkeypatch, json.dumps({"acknowledgementToken": "NBR-ACK-0001"}).encode()
        )
        payload = _payload(live_client)
        result = live_client.submit_return(payload)
        assert (result.status, result.ack_token) == ("ACCEPTED", "NBR-ACK-0001")
        assert result.net_tax_payable == 11000.00
        assert result.raw_response == {"acknowledgementToken": "NBR-ACK-0001"}
        request, timeout = calls[0]
        assert timeout == 30
        assert request.full_url == f"{API}/api/v1/mushak-9-1/submit"
        assert request.get_method() == "POST"
        assert request.get_header("Authorization") == "Bearer unit-test-key"
        assert request.get_header("X-taxpayer-bin") == BIN
        assert request.data == payload.to_json().encode("utf-8")
        assert result.file_hash == hashlib.sha256(request.data).hexdigest()

    def test_regression_unacknowledged_return_is_never_reported_filed(
        self, monkeypatch, live_client, caplog
    ):
        """Regression: when NBR answered WITHOUT an acknowledgementToken
        (e.g. a rejection body), the client invented "NBR-<timestamp>" and
        reported status ACCEPTED — an unfiled statutory return looked filed."""
        body = {"statusCode": "422", "statusMessage": "BIN not registered for IVAS"}
        _fake_urlopen(monkeypatch, json.dumps(body).encode())
        with caplog.at_level(logging.ERROR, logger=ec.logger.name):
            result = live_client.submit_return(_payload(live_client))
        assert (result.status, result.ack_token) == ("REJECTED", "")
        assert result.validation_messages == ["BIN not registered for IVAS"]
        assert result.raw_response == body
        assert "2026-09 not acknowledged" in caplog.text

    def test_regression_empty_response_is_rejected(self, monkeypatch, live_client):
        _fake_urlopen(monkeypatch, b"")
        result = live_client.submit_return(_payload(live_client))
        assert (result.status, result.ack_token) == ("REJECTED", "")
        assert result.validation_messages == ["NBR IVAS response carried no acknowledgement token"]

    def test_transport_failure_raises_evat_error(self, monkeypatch, live_client, caplog):
        _fake_urlopen(monkeypatch, exc=urllib.error.URLError("connection refused"))
        with (
            caplog.at_level(logging.ERROR, logger=ec.logger.name),
            pytest.raises(ec.EvatError, match="Failed to submit return to NBR IVAS") as info,
        ):
            live_client.submit_return(_payload(live_client))
        assert isinstance(info.value.__cause__, urllib.error.URLError)
        assert "NBR e-VAT API submission failed" in caplog.text

    def test_invalid_return_is_never_transmitted(self, monkeypatch, live_client):
        calls = _fake_urlopen(monkeypatch)
        with pytest.raises(ec.EvatValidationError, match="13 digits"):
            live_client.submit_return(_payload(live_client, taxpayer_bin="BIN-1"))
        assert calls == []


# ------------------------------------------------------------------ batch export


class TestBatchExport:
    def test_invalid_return_cannot_be_exported(self):
        client = ec.Int038EvatClient()
        with pytest.raises(ec.EvatValidationError, match="Cannot export invalid return"):
            client.export_ivas_batch_file(_payload(client, tax_period="2026-9"))

    def test_export_digest_matches_content(self):
        client = ec.Int038EvatClient()
        content, digest = client.export_ivas_batch_file(_payload(client))
        assert digest == hashlib.sha256(content.encode("utf-8")).hexdigest()
        assert json.loads(content)["net_tax_payable"] == 11000.00


# ------------------------------------------------------------------ package entry point


def test_package_entry_point_reexports_the_client():
    name = "evat_adapter_pkg"
    module = sys.modules.get(name)
    if module is None:
        spec = importlib.util.spec_from_file_location(
            name, SRC / "__init__.py", submodule_search_locations=[str(SRC)]
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    assert sorted(module.__all__) == sorted(
        [
            "EvatError",
            "EvatSubmissionResult",
            "EvatValidationError",
            "Int038EvatClient",
            "IvasMushak91Payload",
            "IvasOutputLine",
            "validate_ivas_payload",
        ]
    )
    client = module.Int038EvatClient()
    payload = _payload(client)
    assert module.validate_ivas_payload(payload) == []
    assert issubclass(module.EvatValidationError, ValueError)
    assert module.IvasOutputLine("x", 1.0, 0.15).sd_amount == 0.0
