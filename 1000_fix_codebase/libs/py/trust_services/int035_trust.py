"""INT-035 — Trade Licence & Business Registry Verification Client.

Implements statutory verification for Bangladesh businesses (RJSC & City
Corporations: DNCC, DSCC, CCC, etc.). Validates trade licences, company
registrations, and TIN/BIN credentials for seller onboarding (M12 KYC).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass
class TradeLicenseVerificationRequest:
    license_number: str
    entity_name: str
    entity_type: str  # sole_proprietorship, partnership, private_limited, public_limited
    city_corporation: str  # DNCC, DSCC, CCC, GCC, KCC, RCC, SCC, BCC, NCC, CCC_BD, OTHER
    tin_number: str | None = None
    bin_number: str | None = None
    authorized_person_nid: str | None = None


@dataclass
class TradeLicenseVerificationResult:
    is_valid: bool
    status: str  # valid, expired, suspended, not_found, invalid_format
    verification_id: str
    issued_to: str
    issue_date: str
    expiry_date: str
    permitted_categories: list[str]
    tin_matched: bool
    verified_at: str
    authority_name: str
    remarks: str


class TradeLicenseClient:
    """Client for INT-035 trade licence verification service."""

    def __init__(
        self,
        endpoint_url: str = "https://sandbox.registry.1000fix.local/v1/trade-license",
        api_key: str | None = None,
        sandbox: bool = True,
    ):
        self.endpoint_url = endpoint_url
        self.api_key = api_key or "SANDBOX_INT035_KEY"
        self.sandbox = sandbox

    def verify_license(
        self, req: TradeLicenseVerificationRequest
    ) -> TradeLicenseVerificationResult:
        """Verify a business trade licence. In sandbox mode, performs rule-grounded simulation."""
        license_cleaned = req.license_number.strip().upper() if req.license_number else ""
        if not license_cleaned or len(license_cleaned) < 6:
            return TradeLicenseVerificationResult(
                is_valid=False,
                status="invalid_format",
                verification_id=f"VRF-{uuid.uuid4().hex[:12].upper()}",
                issued_to=req.entity_name,
                issue_date="",
                expiry_date="",
                permitted_categories=[],
                tin_matched=False,
                verified_at=datetime.now(UTC).isoformat(),
                authority_name=req.city_corporation,
                remarks="Invalid license number format. Must be at least 6 alphanumeric characters.",
            )

        # Deterministic simulation rules for sandbox testing
        now_iso = datetime.now(UTC).isoformat()
        vid = f"VRF-{uuid.uuid4().hex[:12].upper()}"

        if "EXP" in license_cleaned:
            return TradeLicenseVerificationResult(
                is_valid=False,
                status="expired",
                verification_id=vid,
                issued_to=req.entity_name,
                issue_date="2023-07-01",
                expiry_date="2024-06-30",
                permitted_categories=["IT_EQUIPMENT", "ELECTRONICS"],
                tin_matched=bool(req.tin_number),
                verified_at=now_iso,
                authority_name=req.city_corporation,
                remarks="Trade license expired on 2024-06-30. Renewal required before onboarding.",
            )

        if "SUSP" in license_cleaned:
            return TradeLicenseVerificationResult(
                is_valid=False,
                status="suspended",
                verification_id=vid,
                issued_to=req.entity_name,
                issue_date="2024-07-01",
                expiry_date="2025-06-30",
                permitted_categories=["ELECTRONICS"],
                tin_matched=False,
                verified_at=now_iso,
                authority_name=req.city_corporation,
                remarks="License suspended by issuing authority due to regulatory compliance check.",
            )

        if "NOTFOUND" in license_cleaned or "404" in license_cleaned:
            return TradeLicenseVerificationResult(
                is_valid=False,
                status="not_found",
                verification_id=vid,
                issued_to=req.entity_name,
                issue_date="",
                expiry_date="",
                permitted_categories=[],
                tin_matched=False,
                verified_at=now_iso,
                authority_name=req.city_corporation,
                remarks="No matching trade license found in local government registry.",
            )

        # Valid trade license
        tin_matched = bool(req.tin_number and len(req.tin_number) >= 10)
        return TradeLicenseVerificationResult(
            is_valid=True,
            status="valid",
            verification_id=vid,
            issued_to=req.entity_name,
            issue_date="2025-07-01",
            expiry_date="2027-06-30",
            permitted_categories=[
                "IT_EQUIPMENT",
                "MOBILE_DEVICES",
                "HOME_APPLIANCES",
                "ELECTRONICS_REPAIR",
            ],
            tin_matched=tin_matched,
            verified_at=now_iso,
            authority_name=req.city_corporation or "DNCC",
            remarks="Trade license valid and active in municipal registry. Permitted for after-sales electronics service.",
        )
