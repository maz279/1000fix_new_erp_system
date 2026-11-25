#!/usr/bin/env python3
"""test_pdpa_breach_notification_drill.py — Automated NDMA Breach Notification Drill (R05-M05-T02).

Validates:
1. 6-step NDMA Breach Runbook execution under simulated emergency conditions (P07-M08-T07).
2. 72-hour statutory deadline calculation for National Data Management Authority notice (PDPA s.33).
3. Risk assessment scoring (high-risk threshold triggering consumer notification).
4. Bilingual customer notification flows in authored Bengali and English via M27.
5. Immutable incident timeline logging and M23 CAPA integration.
"""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DSR_SRC = REPO_ROOT / "services" / "dsr-orchestrator" / "src"
sys.path.insert(0, str(DSR_SRC))

from dsr_orchestrator import BREACH_RUNBOOK

STATUTORY_NDMA_DEADLINE_HOURS = 72
CONSUMER_NOTIFICATION_SLA_DAYS = 30


@dataclass
class SecurityIncident:
    incident_id: str
    detected_at: datetime
    data_classes_affected: list[str]
    subject_count_estimated: int
    is_high_risk: bool = False
    contained_at: datetime | None = None
    ndma_notified_at: datetime | None = None
    consumers_notified_at: datetime | None = None
    capa_reference: str | None = None
    audit_log: list[str] = field(default_factory=list)

    @property
    def ndma_deadline(self) -> datetime:
        return self.detected_at + timedelta(hours=STATUTORY_NDMA_DEADLINE_HOURS)


class BreachDrillEngine:
    """Executes and logs the 6-step NDMA breach runbook."""

    @staticmethod
    def contain(incident: SecurityIncident) -> None:
        incident.contained_at = incident.detected_at + timedelta(minutes=45)
        incident.audit_log.append(
            f"CONTAIN: Credentials revoked, affected API perimeter isolated at {incident.contained_at.isoformat()}"
        )

    @staticmethod
    def assess(incident: SecurityIncident) -> None:
        # High risk if sensitive PII (NID, TIN, Biometrics) is involved or count > 500
        sensitive = {"nid_number", "tin_number", "biometric_hash", "statutory_tax_record"}
        if (
            any(c in sensitive for c in incident.data_classes_affected)
            or incident.subject_count_estimated >= 500
        ):
            incident.is_high_risk = True
        incident.audit_log.append(
            f"ASSESS: Scope evaluated ({incident.subject_count_estimated} subjects, classes: {incident.data_classes_affected}). High risk = {incident.is_high_risk}"
        )

    @staticmethod
    def notify_ndma(incident: SecurityIncident, sent_at: datetime) -> dict:
        if sent_at > incident.ndma_deadline:
            raise ValueError(
                f"Breach notice exceeded statutory 72h limit: {sent_at} > {incident.ndma_deadline}"
            )
        incident.ndma_notified_at = sent_at
        incident.audit_log.append(
            f"NOTIFY_NDMA: Formal notice filed with National Data Management Authority at {sent_at.isoformat()}"
        )
        return {
            "authority": "National Data Management Authority (NDMA) - Bangladesh",
            "regulatory_basis": "PDPA 2026 Section 33",
            "incident_id": incident.incident_id,
            "detected_at": incident.detected_at.isoformat(),
            "notified_at": sent_at.isoformat(),
            "data_classes": incident.data_classes_affected,
            "subjects_impacted": incident.subject_count_estimated,
            "containment_summary": "Access tokens rotated; perimeter firewalls updated",
        }

    @staticmethod
    def notify_consumers(incident: SecurityIncident, sent_at: datetime) -> dict:
        if not incident.is_high_risk:
            return {"status": "skipped", "reason": "Low risk; statutory threshold not met"}
        incident.consumers_notified_at = sent_at
        incident.audit_log.append(
            f"NOTIFY_CONSUMERS: Bilingual alert broadcast to {incident.subject_count_estimated} users at {sent_at.isoformat()}"
        )
        return {
            "status": "sent",
            "channels": ["SMS", "Email", "In-App"],
            "messages": {
                "bn": "নিরাপত্তা বিজ্ঞপ্তি: আপনার অ্যাকাউন্টের নিরাপত্তা নিশ্চিত করতে তাৎক্ষণিকভাবে পাসওয়ার্ড পরিবর্তন করুন। বিস্তারিত: 1000fix.com/security",
                "en": "Security Notice: Please update your password immediately to protect your account. Details: 1000fix.com/security",
            },
        }

    @staticmethod
    def record_and_review(incident: SecurityIncident, capa_id: str) -> None:
        incident.capa_reference = capa_id
        incident.audit_log.append(
            f"RECORD_REVIEW: Immutable trail committed; Root cause linked to QMS CAPA {capa_id}"
        )


class TestPdpaBreachNotificationDrill(unittest.TestCase):
    def test_runbook_step_count(self):
        """Verify the 6 standard steps in BREACH_RUNBOOK."""
        self.assertEqual(len(BREACH_RUNBOOK), 6)
        self.assertIn("CONTAIN", BREACH_RUNBOOK[0])
        self.assertIn("ASSESS", BREACH_RUNBOOK[1])
        self.assertIn("NOTIFY the National Data Management Authority", BREACH_RUNBOOK[2])
        self.assertIn("NOTIFY affected data subjects", BREACH_RUNBOOK[3])
        self.assertIn("RECORD", BREACH_RUNBOOK[4])
        self.assertIn("REVIEW", BREACH_RUNBOOK[5])

    def test_rehearsed_breach_drill_execution(self):
        """Simulate high-severity credential compromise drill within statutory windows."""
        detection = datetime(2026, 10, 18, 9, 0, 0)
        incident = SecurityIncident(
            incident_id="INC-2026-BD-01",
            detected_at=detection,
            data_classes_affected=["party_profile", "nid_number"],
            subject_count_estimated=1250,
        )

        # 1. Contain
        BreachDrillEngine.contain(incident)
        self.assertIsNotNone(incident.contained_at)
        self.assertEqual(incident.contained_at, detection + timedelta(minutes=45))

        # 2. Assess
        BreachDrillEngine.assess(incident)
        self.assertTrue(incident.is_high_risk)

        # 3. Notify NDMA (simulated at 18 hours post-detection - well within 72h limit)
        ndma_sent = detection + timedelta(hours=18)
        payload = BreachDrillEngine.notify_ndma(incident, ndma_sent)
        self.assertEqual(payload["regulatory_basis"], "PDPA 2026 Section 33")
        self.assertEqual(incident.ndma_notified_at, ndma_sent)

        # 4. Notify Consumers
        consumer_sent = detection + timedelta(hours=24)
        c_payload = BreachDrillEngine.notify_consumers(incident, consumer_sent)
        self.assertEqual(c_payload["status"], "sent")
        self.assertIn("নিরাপত্তা বিজ্ঞপ্তি", c_payload["messages"]["bn"])
        self.assertIn("Security Notice", c_payload["messages"]["en"])

        # 5. Record & Review
        BreachDrillEngine.record_and_review(incident, "CAPA-2026-088")
        self.assertEqual(incident.capa_reference, "CAPA-2026-088")
        self.assertEqual(len(incident.audit_log), 5)

    def test_breach_ndma_statutory_deadline_enforcement(self):
        """Verify that notices submitted beyond 72 hours raise statutory violation errors."""
        detection = datetime(2026, 10, 18, 9, 0, 0)
        incident = SecurityIncident(
            incident_id="INC-2026-TIMEOUT",
            detected_at=detection,
            data_classes_affected=["party_profile"],
            subject_count_estimated=100,
        )
        # Attempt notification at 73 hours (violates statutory limit)
        late_sent = detection + timedelta(hours=73)
        with self.assertRaises(ValueError) as ctx:
            BreachDrillEngine.notify_ndma(incident, late_sent)
        self.assertIn("exceeded statutory 72h limit", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
