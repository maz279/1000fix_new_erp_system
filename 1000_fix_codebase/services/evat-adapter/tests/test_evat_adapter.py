"""services/evat-adapter tests — INT-038 NBR e-VAT / IVAS filing adapter tests."""

from __future__ import annotations

import sys
import unittest
from decimal import Decimal
from pathlib import Path

import pytest

pytestmark = [pytest.mark.tax, pytest.mark.financial]

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from evat_client import (
    EvatSubmissionResult,
    EvatValidationError,
    Int038EvatClient,
    validate_ivas_payload,
)

D = Decimal


class TestEvatPayloadValidation(unittest.TestCase):
    def setUp(self):
        client = Int038EvatClient()
        build = client.build_payload

        def build_with_declarant(**kwargs):
            # synthetic test declarant (the builder no longer defaults one)
            kwargs.setdefault("declarant_name", "Test Declarant")
            kwargs.setdefault("declarant_designation", "Test Tax Manager")
            kwargs.setdefault("declarant_nid", "1234567890")
            return build(**kwargs)

        client.build_payload = build_with_declarant
        self.client = client

    def test_valid_payload_passes_validation(self):
        payload = self.client.build_payload(
            taxpayer_bin="1234567890123",
            taxpayer_name="1000 FiX Services Ltd.",
            tax_period="2026-09",
            register_totals={
                "standard_15": (D("100000.00"), D("15000.00")),
                "zero_rated": (D("10000.00"), D("0.00")),
            },
            input_vat=D("3500.00"),
            increasing_adjustments=D("500.00"),
            decreasing_adjustments=D("200.00"),
        )
        errors = validate_ivas_payload(payload)
        self.assertEqual(errors, [])
        self.assertEqual(payload.net_tax_payable, 15000.00 + 500.00 - 3500.00 - 200.00)

    def test_invalid_bin_rejected(self):
        payload = self.client.build_payload(
            taxpayer_bin="12345",  # Too short
            taxpayer_name="1000 FiX Services Ltd.",
            tax_period="2026-09",
            register_totals={"standard_15": (D("1000.00"), D("150.00"))},
        )
        errors = validate_ivas_payload(payload)
        self.assertTrue(any("13 digits" in e for e in errors))

    def test_invalid_period_rejected(self):
        payload = self.client.build_payload(
            taxpayer_bin="1234567890123",
            taxpayer_name="1000 FiX Services Ltd.",
            tax_period="2026-13",  # Month 13 invalid
            register_totals={"standard_15": (D("1000.00"), D("150.00"))},
        )
        errors = validate_ivas_payload(payload)
        self.assertTrue(any("YYYY-MM" in e for e in errors))

    def test_arithmetic_mismatch_rejected(self):
        payload = self.client.build_payload(
            taxpayer_bin="1234567890123",
            taxpayer_name="1000 FiX Services Ltd.",
            tax_period="2026-09",
            register_totals={"standard_15": (D("1000.00"), D("150.00"))},
        )
        # Corrupt net tax payable manually
        payload.net_tax_payable = 999.00
        errors = validate_ivas_payload(payload)
        self.assertTrue(any("Arithmetic mismatch" in e for e in errors))

    def test_nil_return_enforced_when_zero_activity(self):
        payload = self.client.build_payload(
            taxpayer_bin="1234567890123",
            taxpayer_name="1000 FiX Services Ltd.",
            tax_period="2026-09",
            register_totals={},
            input_vat=D("0.00"),
        )
        self.assertEqual(payload.return_type, "nil")
        errors = validate_ivas_payload(payload)
        self.assertEqual(errors, [])


class TestInt038EvatClientSubmission(unittest.TestCase):
    def setUp(self):
        client = Int038EvatClient()
        build = client.build_payload

        def build_with_declarant(**kwargs):
            # synthetic test declarant (the builder no longer defaults one)
            kwargs.setdefault("declarant_name", "Test Declarant")
            kwargs.setdefault("declarant_designation", "Test Tax Manager")
            kwargs.setdefault("declarant_nid", "1234567890")
            return build(**kwargs)

        client.build_payload = build_with_declarant
        self.client = client

    def test_submit_return_unconfigured_is_not_accepted(self):
        """GV-009: with no NBR endpoint configured the client must NOT mint a
        local NBR-IVAS-...-M91 acceptance token — the return is explicitly
        NOT accepted."""
        payload = self.client.build_payload(
            taxpayer_bin="1234567890123",
            taxpayer_name="1000 FiX Services Ltd.",
            tax_period="2026-09",
            register_totals={"standard_15": (D("500000.00"), D("75000.00"))},
            input_vat=D("15000.00"),
            increasing_adjustments=D("1000.00"),
            treasury_challan_no="TR-CH-202609-00123",
            treasury_challan_date="2026-10-14",
        )
        res = self.client.submit_return(payload)
        self.assertIsInstance(res, EvatSubmissionResult)
        self.assertEqual(res.status, "NOT_SUBMITTED")
        self.assertEqual(res.ack_token, "")
        self.assertEqual(res.taxpayer_bin, "1234567890123")
        self.assertEqual(res.net_tax_payable, 61000.00)
        self.assertTrue(len(res.file_hash) == 64)
        self.assertEqual(
            res.validation_messages,
            ["NBR endpoint not configured - return submission NOT accepted"],
        )
        self.assertEqual(res.raw_response, {})

    def test_export_batch_file_integrity(self):
        payload = self.client.build_payload(
            taxpayer_bin="1234567890123",
            taxpayer_name="1000 FiX Services Ltd.",
            tax_period="2026-09",
            register_totals={"standard_15": (D("200000.00"), D("30000.00"))},
            input_vat=D("5000.00"),
        )
        content, digest = self.client.export_batch_file(payload)
        self.assertIn("1000 FiX Services Ltd.", content)
        self.assertIn("2026-09", content)
        self.assertTrue(len(digest) == 64)

    def test_invalid_submission_raises_validation_error(self):
        payload = self.client.build_payload(
            taxpayer_bin="INVALID_BIN",
            taxpayer_name="1000 FiX Services Ltd.",
            tax_period="2026-09",
            register_totals={},
        )
        with self.assertRaises(EvatValidationError):
            self.client.submit_return(payload)


if __name__ == "__main__":
    unittest.main()


class TestDeclarantRequired(unittest.TestCase):
    def test_payload_without_a_declarant_is_rejected(self):
        payload = Int038EvatClient().build_payload(
            taxpayer_bin="1234567890123",
            taxpayer_name="1000 FiX Services Ltd.",
            tax_period="2026-09",
            register_totals={"standard_15": (D("100.00"), D("15.00"))},
        )
        errors = validate_ivas_payload(payload)
        self.assertIn("Declarant name is required", errors)
        self.assertTrue(any("Declarant NID" in e for e in errors))
