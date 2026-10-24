"""Behavioural tests for INT-035 trade-licence verification (sandbox rules)."""

from __future__ import annotations

import re
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[4]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import libs.py.trust_services as trust_services
from libs.py.trust_services.int035_trust import (
    TradeLicenseClient,
    TradeLicenseVerificationRequest,
    TradeLicenseVerificationResult,
)

VID = re.compile(r"^VRF-[0-9A-F]{12}$")


def _req(
    license_number: str | None, city: str = "DSCC", tin: str | None = None
) -> TradeLicenseVerificationRequest:
    return TradeLicenseVerificationRequest(
        license_number=license_number,  # type: ignore[arg-type] - None is a real-world input
        entity_name="Acme Repairs Ltd",
        entity_type="private_limited",
        city_corporation=city,
        tin_number=tin,
    )


def _assert_fresh_utc(stamp: str) -> None:
    parsed = datetime.fromisoformat(stamp)
    assert parsed.tzinfo is not None and parsed.utcoffset() == timedelta(0)
    assert abs(datetime.now(UTC) - parsed) < timedelta(minutes=1)


@pytest.fixture
def client() -> TradeLicenseClient:
    return TradeLicenseClient()


def test_package_exports_the_int035_api() -> None:
    assert trust_services.TradeLicenseClient is TradeLicenseClient
    assert trust_services.TradeLicenseVerificationRequest is TradeLicenseVerificationRequest
    assert trust_services.TradeLicenseVerificationResult is TradeLicenseVerificationResult
    assert "TradeLicenseClient" in trust_services.__all__


def test_client_defaults_to_sandbox_credentials() -> None:
    c = TradeLicenseClient()
    assert c.endpoint_url == "https://sandbox.registry.1000fix.local/v1/trade-license"
    assert c.api_key == "SANDBOX_INT035_KEY"
    assert c.sandbox is True


def test_client_accepts_explicit_configuration() -> None:
    c = TradeLicenseClient(endpoint_url="https://registry.example/v1", api_key="k-1", sandbox=False)
    assert (c.endpoint_url, c.api_key, c.sandbox) == ("https://registry.example/v1", "k-1", False)


def test_request_optional_fields_default_to_none() -> None:
    req = _req("TL-123456")
    assert (req.tin_number, req.bin_number, req.authorized_person_nid) == (None, None, None)


@pytest.mark.parametrize("license_number", [None, "", "      ", "ab12", " TL-1 "])
def test_missing_or_short_licence_is_invalid_format(
    client: TradeLicenseClient, license_number: str | None
) -> None:
    res = client.verify_license(_req(license_number, city="CCC", tin="1234567890"))
    assert res.is_valid is False
    assert res.status == "invalid_format"
    assert VID.match(res.verification_id)
    assert (res.issue_date, res.expiry_date, res.permitted_categories) == ("", "", [])
    assert res.tin_matched is False
    assert res.issued_to == "Acme Repairs Ltd"
    assert res.authority_name == "CCC"
    assert "at least 6" in res.remarks
    _assert_fresh_utc(res.verified_at)


def test_six_character_licence_is_long_enough(client: TradeLicenseClient) -> None:
    assert client.verify_license(_req("abc123")).status == "valid"


@pytest.mark.parametrize(("tin", "matched"), [("123", True), (None, False), ("", False)])
def test_expired_licence(client: TradeLicenseClient, tin: str | None, matched: bool) -> None:
    res = client.verify_license(_req("  tl-exp-2024 ", tin=tin))  # normalised: strip + upper
    assert (res.is_valid, res.status) == (False, "expired")
    assert (res.issue_date, res.expiry_date) == ("2023-07-01", "2024-06-30")
    assert res.permitted_categories == ["IT_EQUIPMENT", "ELECTRONICS"]
    assert res.tin_matched is matched
    assert res.authority_name == "DSCC"
    assert "expired on 2024-06-30" in res.remarks
    assert VID.match(res.verification_id)
    _assert_fresh_utc(res.verified_at)


def test_expired_rule_takes_precedence_over_suspended(client: TradeLicenseClient) -> None:
    assert client.verify_license(_req("EXP-SUSP-01")).status == "expired"


def test_suspended_licence(client: TradeLicenseClient) -> None:
    res = client.verify_license(_req("TL-SUSP-99", tin="1234567890"))
    assert (res.is_valid, res.status) == (False, "suspended")
    assert (res.issue_date, res.expiry_date) == ("2024-07-01", "2025-06-30")
    assert res.permitted_categories == ["ELECTRONICS"]
    assert res.tin_matched is False  # never matched while suspended
    assert "suspended" in res.remarks


@pytest.mark.parametrize("license_number", ["TL-NOTFOUND", "TL-404-000"])
def test_unknown_licence_is_not_found(client: TradeLicenseClient, license_number: str) -> None:
    res = client.verify_license(_req(license_number))
    assert (res.is_valid, res.status) == (False, "not_found")
    assert (res.issue_date, res.expiry_date, res.permitted_categories) == ("", "", [])
    assert res.tin_matched is False
    assert "No matching trade license" in res.remarks


@pytest.mark.parametrize(
    ("tin", "matched"),
    [("1234567890", True), ("12345678901234", True), ("123456789", False), (None, False)],
)
def test_valid_licence_and_tin_matching(
    client: TradeLicenseClient, tin: str | None, matched: bool
) -> None:
    res = client.verify_license(_req("DNCC-2025-123456", tin=tin))
    assert (res.is_valid, res.status) == (True, "valid")
    assert (res.issue_date, res.expiry_date) == ("2025-07-01", "2027-06-30")
    assert "ELECTRONICS_REPAIR" in res.permitted_categories
    assert len(res.permitted_categories) == 4
    assert res.tin_matched is matched
    assert res.authority_name == "DSCC"
    _assert_fresh_utc(res.verified_at)


def test_valid_licence_without_city_defaults_authority_to_dncc(
    client: TradeLicenseClient,
) -> None:
    assert client.verify_license(_req("TL-777777", city="")).authority_name == "DNCC"


def test_verification_ids_are_unique(client: TradeLicenseClient) -> None:
    ids = {client.verify_license(_req("TL-123456")).verification_id for _ in range(10)}
    assert len(ids) == 10
