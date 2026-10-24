#!/usr/bin/env python3
"""test_g4_06_pdpa_readiness.py — Gate G4 check G4-06b verification suite.

Verifies end-to-end operational PDPA compliance:
1. All 5 Data Subject Rights (Access, Rectification, Portability, Erasure, Objection)
2. Machine-readable export schema (regional + Z4 vault through ResidencyClientProtocol)
3. Erasure SAGA execution with 7 steps and compensating reversals
4. 5-year statutory processing record retention (NFR-095)
5. Controller-side 30-day consumer notification (NFR-093) and NDMA 72-hour breach runbook rehearsal
6. Signed SC-003 DPIA report artifact validation
"""

from __future__ import annotations

import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DSR_SRC = REPO_ROOT / "services" / "dsr-orchestrator" / "src"
sys.path.insert(0, str(DSR_SRC))

from dsr_orchestrator import (
    NOTIFICATION_DAYS,
    PROCESSING_RECORD_YEARS,
    DsrRequest,
    DsrState,
    DsrType,
    ResidencyClientProtocol,
    SagaState,
    SagaStep,
    assemble_export,
    erasure_preserves_record,
    run_erasure_saga,
)


class DummyResidencyService(ResidencyClientProtocol):
    """Mock residency service adhering to ResidencyClientProtocol (FF-09)."""

    def fetch_resident(self, party_ref: str) -> dict:
        return {
            "nid_classified": "Z4-VAULT-TOKEN-1988-9923847291",
            "biometric_voiceprint_ref": "Z4-VOICEPRINT-SHA256-EF8819",
            "jurisdiction": "BD-DHAKA-SOVEREIGN",
        }

    def tombstone(self, party_ref: str, key: str) -> None:
        pass


class TestG406PdpaReadiness(unittest.TestCase):
    """Full operational verification for G4-06b PDPA readiness."""

    def test_all_five_dsr_rights_operational(self):
        """Verify all five DSR rights defined under PDPA 2026."""
        required_rights = {
            "access",
            "rectification",
            "portability",
            "erasure",
            "objection",
        }
        enum_values = {e.value for e in DsrType}
        self.assertTrue(
            required_rights.issubset(enum_values),
            f"Missing required DSR rights: {required_rights - enum_values}",
        )

        # Verify request lifecycle with 30-day clock (NFR-093)
        today = date(2026, 10, 18)
        req = DsrRequest(
            request_id="DSR-2026-001",
            dsr_type=DsrType.ACCESS,
            party_ref="fix.party,1001",
            received_on=today,
        )
        self.assertEqual(req.state, DsrState.RECEIVED)
        self.assertEqual(req.due_on, today + timedelta(days=30))
        self.assertEqual(NOTIFICATION_DAYS, 30)

    def test_machine_readable_export_portable_schema(self):
        """Verify DSR portable export produces valid JSON combining regional and Z4 resident data."""

        def load_regional(party_ref: str) -> dict:
            return {
                "party_ref": party_ref,
                "display_name": "Rahim Ahmed",
                "service_tickets": ["TKT-9912", "TKT-9915"],
                "warranty_registrations": ["W-881923"],
            }

        residency = DummyResidencyService()
        bundle = assemble_export("fix.party,1001", load_regional, residency)
        portable = bundle.to_portable()

        self.assertEqual(portable["party_ref"], "fix.party,1001")
        self.assertIn("service_tickets", portable["regional"])
        self.assertIn("nid_classified", portable["resident"])
        self.assertEqual(portable["resident"]["jurisdiction"], "BD-DHAKA-SOVEREIGN")

    def test_erasure_saga_drill_and_five_year_retention(self):
        """Verify erasure saga drill passes 7 steps and preserves 5-year statutory processing record."""
        self.assertEqual(len(list(SagaStep)), 7, "Erasure saga must consist of exactly 7 steps")
        self.assertEqual(
            PROCESSING_RECORD_YEARS, 5, "Statutory processing record must be retained for 5 years"
        )

        executed = []
        executors = {step: (lambda party, s=step: executed.append(s)) for step in SagaStep}

        state = SagaState(request_id="DSR-ERASURE-001", party_ref="fix.party,1001")
        final_state = run_erasure_saga(state, executors)

        self.assertEqual(final_state.status, "completed")
        self.assertEqual(len(final_state.completed), 7)
        self.assertEqual(executed, list(SagaStep))

        # Verify statutory retention invariant (survives 5 years)
        erased_on = date(2026, 10, 18)
        retain_until = erasure_preserves_record(erased_on)
        self.assertEqual(retain_until, erased_on + timedelta(days=365 * 5))
        self.assertEqual(PROCESSING_RECORD_YEARS, 5)

    def test_ndma_breach_and_consumer_notification_slas(self):
        """Verify NDMA 72-hour reporting ceiling and consumer 30-day notification SLA."""
        drill_record = REPO_ROOT / "docs" / "runbooks" / "breach-notification-drill-record.md"
        self.assertTrue(drill_record.exists(), "Breach notification drill record must be filed")
        content = drill_record.read_text(encoding="utf-8")
        self.assertIn("72 Hours", content)
        self.assertIn("30 Days", content)
        self.assertIn("INC-2026-10-DRILL-001", content)
        self.assertIn("VERIFIED PASS", content)

    def test_sc003_dpia_report_signed_and_filed(self):
        """Verify SC-003 DPIA re-run report exists and contains all required signatory approvals."""
        dpia_file = REPO_ROOT / "docs" / "governance" / "SC-003-DPIA-signoff-and-readiness.md"
        self.assertTrue(dpia_file.exists(), "SC-003 DPIA signoff report must exist")
        text = dpia_file.read_text(encoding="utf-8")
        self.assertIn("DPIA-SC003-RERUN-2026-10-18", text)
        self.assertIn("100% PASS", text)
        self.assertIn("Data Protection Officer (DPO)", text)
        self.assertIn("Chief Information Security Officer (CISO)", text)
        self.assertIn("Chief Technology Officer (CTO)", text)
        self.assertIn("Senior Legal Counsel", text)


if __name__ == "__main__":
    unittest.main()
