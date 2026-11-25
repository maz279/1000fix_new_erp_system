"""evat_client — INT-038 NBR e-VAT / IVAS Filing Interface Adapter (DEP-24).

Implements the statutory NBR VAT Online (Integrated VAT Administration System - IVAS)
Mushak 9.1 return filing protocol under the Bangladesh VAT & SD Act 2012:
1. Online-only filing requirement (manual paper abolished 1 July 2026).
2. IVAS Mushak 9.1 schema generation and cross-field arithmetic validation.
3. Secure API submission with statutory acknowledgement capture (ack token).
   GV-009 fail-closed: without a configured NBR endpoint the return is NOT
   accepted and no acknowledgement reference is ever minted locally.
4. Portal batch upload exporter (JSON/XML) with SHA-256 integrity digest for manual portal keying fallback.
5. Strict 13-digit BIN validation and mandatory nil return handling.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

logger = logging.getLogger(__name__)

BIN_REGEX = re.compile(r"^\d{13}$")
PERIOD_REGEX = re.compile(r"^\d{4}-(?:0[1-9]|1[0-2])$")


class EvatError(RuntimeError):
    """General NBR e-VAT communication or processing error."""


class EvatValidationError(ValueError):
    """Statutory validation failure against NBR IVAS schema."""


@dataclass
class IvasOutputLine:
    treatment: str
    taxable_value: float
    vat_amount: float
    sd_amount: float = 0.0


@dataclass
class IvasMushak91Payload:
    taxpayer_bin: str
    taxpayer_name: str
    tax_period: str  # YYYY-MM
    return_type: str  # "normal" | "amended" | "nil"
    submission_timestamp: str
    output_supplies: list[IvasOutputLine] = field(default_factory=list)
    total_taxable_value: float = 0.0
    total_output_vat: float = 0.0
    total_input_vat: float = 0.0
    total_sd_payable: float = 0.0
    increasing_adjustments: float = 0.0
    decreasing_adjustments: float = 0.0
    net_tax_payable: float = 0.0
    treasury_challan_no: str = ""
    treasury_challan_date: str = ""
    declarant_name: str = "Authorized Finance Officer"
    declarant_designation: str = "Tax Manager"
    declarant_nid: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


@dataclass(frozen=True)
class EvatSubmissionResult:
    status: str  # "ACCEPTED" | "REJECTED" | "SAVED_BATCH" | "NOT_SUBMITTED"
    ack_token: str
    taxpayer_bin: str
    tax_period: str
    net_tax_payable: float
    filed_at: str
    file_hash: str
    validation_messages: list[str] = field(default_factory=list)
    raw_response: dict[str, Any] = field(default_factory=dict)


def validate_ivas_payload(payload: IvasMushak91Payload) -> list[str]:
    """Validate payload against statutory NBR IVAS return rules."""
    errors: list[str] = []

    if not BIN_REGEX.match(payload.taxpayer_bin):
        errors.append(f"Taxpayer BIN {payload.taxpayer_bin!r} must be exactly 13 digits")

    if not PERIOD_REGEX.match(payload.tax_period):
        errors.append(f"Tax period {payload.tax_period!r} must be formatted as YYYY-MM")

    # Nil return invariants: a nil return declares NO tax activity at all —
    # adjustments and SD are tax activity too (they move the net payable).
    is_zero_activity = (
        payload.total_taxable_value == 0.0
        and payload.total_output_vat == 0.0
        and payload.total_input_vat == 0.0
        and payload.total_sd_payable == 0.0
        and payload.increasing_adjustments == 0.0
        and payload.decreasing_adjustments == 0.0
    )
    if is_zero_activity and payload.return_type != "nil":
        errors.append("Zero activity period must be filed with return_type='nil'")
    if not is_zero_activity and payload.return_type == "nil":
        errors.append(
            "Return with non-zero turnover, input VAT, SD or adjustments cannot be filed as nil"
        )

    # Arithmetic cross-check (within 1 paisa tolerance)
    computed_net = (
        payload.total_output_vat
        + payload.increasing_adjustments
        - payload.total_input_vat
        - payload.decreasing_adjustments
    )
    if abs(computed_net - payload.net_tax_payable) > 0.02:
        errors.append(
            f"Arithmetic mismatch: net_tax_payable ({payload.net_tax_payable}) != "
            f"output ({payload.total_output_vat}) + inc ({payload.increasing_adjustments}) - "
            f"input ({payload.total_input_vat}) - dec ({payload.decreasing_adjustments}) = {computed_net:.2f}"
        )

    # The declaration is signed by a real officer: no placeholder declarant
    # (the payload builder used to default to a made-up name and NID).
    if not (payload.declarant_name or "").strip():
        errors.append("Declarant name is required")
    if not (payload.declarant_designation or "").strip():
        errors.append("Declarant designation is required")
    nid = (payload.declarant_nid or "").strip()
    if not (nid.isdigit() and len(nid) in (10, 13, 17)):
        errors.append(f"Declarant NID {nid!r} must be 10, 13 or 17 digits")

    return errors


class Int038EvatClient:
    """INT-038: NBR e-VAT (IVAS) filing interface client."""

    def __init__(self, api_url: str | None = None, api_key: str | None = None) -> None:
        self.api_url = (api_url or os.environ.get("FIX_NBR_EVAT_API_URL", "")).strip()
        self.api_key = (api_key or os.environ.get("FIX_NBR_EVAT_API_KEY", "")).strip()
        self.sandbox_mode = not self.api_url or os.environ.get("FIX_ENV", "local") != "production"

    def build_payload(
        self,
        taxpayer_bin: str,
        taxpayer_name: str,
        tax_period: str,
        register_totals: dict[str, tuple[Decimal, Decimal]],
        input_vat: Decimal = Decimal("0.00"),
        increasing_adjustments: Decimal = Decimal("0.00"),
        decreasing_adjustments: Decimal = Decimal("0.00"),
        treasury_challan_no: str = "",
        treasury_challan_date: str = "",
        declarant_name: str = "",
        declarant_designation: str = "",
        declarant_nid: str = "",
    ) -> IvasMushak91Payload:
        """Construct a validated IVAS Mushak 9.1 payload from register totals."""
        supplies: list[IvasOutputLine] = []
        tot_taxable = Decimal("0.00")
        tot_output = Decimal("0.00")

        for treatment, (taxable, vat) in sorted(register_totals.items()):
            t_dec = Decimal(str(taxable))
            v_dec = Decimal(str(vat))
            tot_taxable += t_dec
            tot_output += v_dec
            supplies.append(
                IvasOutputLine(
                    treatment=treatment,
                    taxable_value=float(t_dec),
                    vat_amount=float(v_dec),
                )
            )

        net_tax = tot_output + increasing_adjustments - input_vat - decreasing_adjustments
        is_nil = (
            tot_taxable == 0
            and tot_output == 0
            and input_vat == 0
            and increasing_adjustments == 0
            and decreasing_adjustments == 0
        )
        ret_type = "nil" if is_nil else "normal"

        now_str = datetime.now(UTC).isoformat()
        return IvasMushak91Payload(
            taxpayer_bin=taxpayer_bin,
            taxpayer_name=taxpayer_name,
            tax_period=tax_period,
            return_type=ret_type,
            submission_timestamp=now_str,
            output_supplies=supplies,
            total_taxable_value=float(tot_taxable),
            total_output_vat=float(tot_output),
            total_input_vat=float(input_vat),
            total_sd_payable=0.0,
            increasing_adjustments=float(increasing_adjustments),
            decreasing_adjustments=float(decreasing_adjustments),
            net_tax_payable=float(net_tax),
            treasury_challan_no=treasury_challan_no,
            treasury_challan_date=treasury_challan_date,
            declarant_name=declarant_name,
            declarant_designation=declarant_designation,
            declarant_nid=declarant_nid,
        )

    def submit_return(self, payload: IvasMushak91Payload) -> EvatSubmissionResult:
        """Submit the Mushak 9.1 return to the configured NBR IVAS endpoint.

        GV-009 fail-closed: with no endpoint configured the return is NOT
        accepted — an acceptance reference is only ever the statutory
        acknowledgement captured from a real submission, never minted
        locally."""
        errors = validate_ivas_payload(payload)
        if errors:
            raise EvatValidationError(f"NBR IVAS validation failed: {'; '.join(errors)}")

        raw_json = payload.to_json()
        file_hash = hashlib.sha256(raw_json.encode("utf-8")).hexdigest()
        now_iso = datetime.now(UTC).isoformat()

        if not self.api_url:
            message = "NBR endpoint not configured - return submission NOT accepted"
            logger.error("NBR e-VAT return %s NOT submitted: %s", payload.tax_period, message)
            return EvatSubmissionResult(
                status="NOT_SUBMITTED",
                ack_token="",
                taxpayer_bin=payload.taxpayer_bin,
                tax_period=payload.tax_period,
                net_tax_payable=payload.net_tax_payable,
                filed_at=now_iso,
                file_hash=file_hash,
                validation_messages=[message],
                raw_response={},
            )

        # Production REST submission
        import urllib.error
        import urllib.request

        req = urllib.request.Request(  # noqa: S310 - config-provided NBR API URL
            f"{self.api_url}/api/v1/mushak-9-1/submit",
            data=raw_json.encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "X-Taxpayer-BIN": payload.taxpayer_bin,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
                res_data = json.loads(resp.read() or b"{}")
            token = str(res_data.get("acknowledgementToken") or "").strip()
            if not token:
                # No statutory acknowledgement = the return is NOT filed.
                # Never fabricate an ack token for an unacknowledged return.
                message = str(
                    res_data.get("statusMessage")
                    or "NBR IVAS response carried no acknowledgement token"
                )
                logger.error(
                    "NBR e-VAT return %s not acknowledged: %s", payload.tax_period, message
                )
                return EvatSubmissionResult(
                    status="REJECTED",
                    ack_token="",
                    taxpayer_bin=payload.taxpayer_bin,
                    tax_period=payload.tax_period,
                    net_tax_payable=payload.net_tax_payable,
                    filed_at=now_iso,
                    file_hash=file_hash,
                    validation_messages=[message],
                    raw_response=res_data,
                )
            return EvatSubmissionResult(
                status="ACCEPTED",
                ack_token=token,
                taxpayer_bin=payload.taxpayer_bin,
                tax_period=payload.tax_period,
                net_tax_payable=payload.net_tax_payable,
                filed_at=now_iso,
                file_hash=file_hash,
                raw_response=res_data,
            )
        except Exception as exc:
            logger.error("NBR e-VAT API submission failed: %s", exc)
            raise EvatError(f"Failed to submit return to NBR IVAS: {exc}") from exc

    def export_ivas_batch_file(self, payload: IvasMushak91Payload) -> tuple[str, str]:
        """Generate uploadable batch file content and SHA256 integrity hash for manual portal keying."""
        errors = validate_ivas_payload(payload)
        if errors:
            raise EvatValidationError(f"Cannot export invalid return: {'; '.join(errors)}")

        content = payload.to_json()
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        return content, digest

    export_batch_file = export_ivas_batch_file
