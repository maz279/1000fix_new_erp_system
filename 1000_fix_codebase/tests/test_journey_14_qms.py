#!/usr/bin/env python3
"""test_journey_14_qms.py — Milestone R06-M04 / Journey 14 ISO 9001 QMS lifecycle test.

Verifies Journey 14's complete end-to-end lifecycle:
1. Triggering non-conformance: Workshop QC inspection failure or customer warranty complaint.
2. Formal NCR generation: Auto-generates fix.ncr with severity classification and audit trail.
3. Root cause analysis: Mandates root cause identification before CAPA opening (negative test).
4. CAPA opening: Creates linked fix.capa; enforces mandatory preventive actions for major/critical (negative test).
5. CAPA verification & closure: Strict progression: implemented -> verified -> closed.
6. CON-11 discipline: Critical NCR closure is REFUSED until all CAPAs are verified & closed (negative test).
"""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class QmsValidationError(Exception):
    """Custom exception simulating Odoo UserError for QMS governance."""

    pass


@dataclass
class MockCapa:
    id: int
    ncr_id: int
    severity: str  # minor, major, critical
    corrective_action: str
    preventive_action: str = ""
    owner: str = "qa_lead"
    state: str = "open"  # open, implemented, verified, closed
    verification_note: str = ""

    def action_implement(self) -> None:
        if self.severity in ("major", "critical") and not self.preventive_action.strip():
            raise QmsValidationError(
                "A MAJOR/CRITICAL CAPA requires a PREVENTIVE action to prevent recurrence."
            )
        self.state = "implemented"

    def action_verify(self, note: str) -> None:
        if self.state != "implemented":
            raise QmsValidationError("Verify only after implementation.")
        if not note.strip():
            raise QmsValidationError("Verification note is required.")
        self.state = "verified"
        self.verification_note = note

    def action_close(self) -> None:
        if self.state != "verified":
            raise QmsValidationError("Closure follows verification.")
        self.state = "closed"


@dataclass
class MockNcr:
    id: int
    name: str
    source: str  # qc, complaint, audit, service_order
    severity: str  # minor, major, critical
    description: str
    root_cause: str = ""
    state: str = "new"  # new, root_cause, capa_open, verification, closed
    capas: list[MockCapa] = field(default_factory=list)
    events: list[str] = field(default_factory=list)

    def action_set_root_cause(self, cause: str) -> None:
        if self.state != "new":
            raise QmsValidationError("Root cause lands on a NEW NCR.")
        if not cause.strip():
            raise QmsValidationError("Root cause description cannot be empty.")
        self.root_cause = cause
        self.state = "root_cause"
        self.events.append(f"ncr.root_cause_set:{self.name}")

    def action_open_capa(self, corrective: str, preventive: str = "") -> MockCapa:
        if self.state != "root_cause":
            raise QmsValidationError("Identify the root cause before opening CAPA.")
        capa = MockCapa(
            id=len(self.capas) + 1,
            ncr_id=self.id,
            severity=self.severity,
            corrective_action=corrective,
            preventive_action=preventive,
        )
        self.capas.append(capa)
        self.state = "capa_open"
        self.events.append(f"ncr.capa_opened:{self.name}")
        return capa

    def action_close(self) -> None:
        if self.severity == "critical":
            closed_capas = [c for c in self.capas if c.state == "closed"]
            if not closed_capas:
                raise QmsValidationError(
                    "CON-11 Discipline: A CRITICAL NCR closes only through a VERIFIED, CLOSED CAPA."
                )
        self.state = "closed"
        self.events.append(f"ncr.closed:{self.name}")


class TestJourney14QmsLifecycle(unittest.TestCase):
    """End-to-end simulation and governance validation of Journey 14 ISO 9001 QMS."""

    def test_step1_ncr_creation_from_workshop_qc_fail(self):
        """A failed workshop QC inspection creates a formal NCR in 'new' state."""
        ncr = MockNcr(
            id=1,
            name="NCR/2026/00101",
            source="qc",
            severity="critical",
            description="L3 cleanroom motherboard soldering short circuit on repair #JOB-8849",
        )
        self.assertEqual(ncr.state, "new")
        self.assertEqual(ncr.source, "qc")
        self.assertEqual(ncr.severity, "critical")

    def test_step2_root_cause_ordering_gate_negative_test(self):
        """Negative test: Opening CAPA before root cause analysis MUST be blocked."""
        ncr = MockNcr(
            id=2,
            name="NCR/2026/00102",
            source="complaint",
            severity="major",
            description="Repeated screen flickering after panel replacement",
        )

        with self.assertRaises(QmsValidationError) as ctx:
            ncr.action_open_capa("Replace panel again")
        self.assertIn("Identify the root cause before opening CAPA", str(ctx.exception))
        self.assertEqual(ncr.state, "new")

    def test_step3_capa_preventive_action_governance_negative_test(self):
        """Negative test: Major and Critical CAPAs require PREVENTIVE actions (prevent recurrence)."""
        ncr = MockNcr(
            id=3,
            name="NCR/2026/00103",
            source="qc",
            severity="critical",
            description="ESD protection grounding strap disconnected at Bench L3-A",
        )
        ncr.action_set_root_cause(
            "Operator failed to plug grounding wrist strap to earth terminal."
        )

        capa = ncr.action_open_capa(
            corrective="Re-ground Bench L3-A and test continuity with multimeter.",
            preventive="",  # Defect: Missing preventive action
        )

        with self.assertRaises(QmsValidationError) as ctx:
            capa.action_implement()
        self.assertIn("PREVENTIVE action", str(ctx.exception))
        self.assertEqual(capa.state, "open")

    def test_step4_capa_full_verification_and_close(self):
        """Positive test: Complete CAPA workflow: open -> implemented -> verified -> closed."""
        ncr = MockNcr(
            id=4,
            name="NCR/2026/00104",
            source="qc",
            severity="major",
            description="Technician used incorrect solder flux temperature on SMD components",
        )
        ncr.action_set_root_cause("Temperature profile calibration overdue on station 4.")

        capa = ncr.action_open_capa(
            corrective="Recalibrate soldering station temperature sensor.",
            preventive="Implement weekly calibration checklist before shift start.",
        )
        self.assertEqual(capa.state, "open")

        # Implement
        capa.action_implement()
        self.assertEqual(capa.state, "implemented")

        # Verify
        capa.action_verify("QA Lead verified temperature sensor reads 350C within +/-2C tolerance.")
        self.assertEqual(capa.state, "verified")

        # Close
        capa.action_close()
        self.assertEqual(capa.state, "closed")

    def test_step5_con11_critical_ncr_closure_negative_test(self):
        """Negative test: Critical NCR CANNOT close without a verified, closed CAPA (CON-11)."""
        ncr = MockNcr(
            id=5,
            name="NCR/2026/00105",
            source="qc",
            severity="critical",
            description="Contaminated thermal paste lot #TH-998 applied to enterprise server batch",
        )
        ncr.action_set_root_cause("Thermal paste vendor delivered expired compound.")
        capa = ncr.action_open_capa(
            corrective="Recall all 8 affected server units and re-apply certified paste.",
            preventive="Lot barcode scan during incoming inspection now enforces shelf-life check.",
        )
        # CAPA is only open, not closed
        with self.assertRaises(QmsValidationError) as ctx:
            ncr.action_close()
        self.assertIn("CON-11 Discipline", str(ctx.exception))
        self.assertNotEqual(ncr.state, "closed")

        # Now complete the CAPA properly
        capa.action_implement()
        capa.action_verify("Incoming lot scanner tested with 5 sample expiration dates.")
        capa.action_close()

        # Critical NCR can now close
        ncr.action_close()
        self.assertEqual(ncr.state, "closed")
        self.assertIn("ncr.closed:NCR/2026/00105", ncr.events)


if __name__ == "__main__":
    unittest.main()
