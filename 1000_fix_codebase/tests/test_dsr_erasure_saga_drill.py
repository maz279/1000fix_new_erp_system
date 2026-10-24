#!/usr/bin/env python3
"""test_dsr_erasure_saga_drill.py — Automated Rehearsal Drill for DSR Erasure SAGA (R05-M05-T01).

Simulates and verifies:
1. Portable machine-readable export assembling regional OLTP data and Z4 resident data through ResidencyClientProtocol.
2. Full 7-step Erasure SAGA execution across primary, resident store (Z4), replicas, warehouse, object store, search index, and backups.
3. Catastrophic failure injection with automated compensation rollback in reverse order over completed steps only.
4. Statutory 5-year processing record retention surviving through erasure (NFR-095).
5. Controller 30-day notification timeline (NFR-093).
"""

from __future__ import annotations

import json
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
    DsrError,
    DsrRequest,
    DsrType,
    ResidencyClientProtocol,
    SagaState,
    SagaStep,
    assemble_export,
    erasure_preserves_record,
    run_erasure_saga,
)


class MockResidencyService(ResidencyClientProtocol):
    """Simulated Z4 Split-Residency Data Vault service (DEP-31 / D-013)."""

    def __init__(self):
        self.vault: dict[str, dict] = {
            "party:corp_01": {"nid_number": "19901234567890123", "tin_number": "123456789012"},
            "party:cust_99": {"nid_number": "19859876543210123", "biometric_hash": "a1b2c3d4e5f6"},
        }
        self.tombstone_log: list[tuple[str, str]] = []

    def fetch_resident(self, party_ref: str) -> dict:
        return self.vault.get(party_ref, {})

    def tombstone(self, party_ref: str, key: str) -> None:
        if party_ref in self.vault:
            self.tombstone_log.append((party_ref, key))
            if key == "all":
                self.vault[party_ref] = {
                    "_tombstoned": True,
                    "_timestamp": date.today().isoformat(),
                }
            else:
                self.vault[party_ref].pop(key, None)


class TestDsrErasureSagaDrill(unittest.TestCase):
    def setUp(self):
        self.residency = MockResidencyService()
        self.drill_trace: list[str] = []

    def _make_drill_executors(self, fail_at_step: SagaStep | None = None):
        """Creates executors for all 7 saga steps that record operational traces."""
        executors = {}
        for step in SagaStep:

            def make_executor(s: SagaStep, should_fail: bool):
                def execute(party_ref: str):
                    if should_fail:
                        self.drill_trace.append(f"FAILED:{s.value}")
                        raise RuntimeError(f"Simulated storage failure during {s.value}")
                    self.drill_trace.append(f"EXEC:{s.value}")

                return execute

            executors[step] = make_executor(step, step == fail_at_step)
        return executors

    def test_portable_export_assembly(self):
        """T01: Assemble machine-readable export through residency client."""

        def load_regional_data(party_ref: str):
            return {
                "orders_count": 14,
                "customer_tier": "enterprise_platinum",
                "registered_branch": "DHK-MOT-01",
            }

        bundle = assemble_export("party:cust_99", load_regional_data, self.residency)
        portable = bundle.to_portable()

        self.assertEqual(portable["party_ref"], "party:cust_99")
        self.assertIn("orders_count", portable["regional"])
        self.assertIn("nid_number", portable["resident"])
        # Validate machine-readable serialization
        serialized = json.dumps(portable)
        self.assertIn("19859876543210123", serialized)

    def test_erasure_saga_successful_drill(self):
        """T01: Full 7-step erasure saga rehearsal completing with 100% success."""
        party = "party:corp_01"
        saga = SagaState(request_id="DSR-2026-DRILL-01", party_ref=party)
        executors = self._make_drill_executors(fail_at_step=None)

        result = run_erasure_saga(saga, executors, self.residency)

        self.assertEqual(result.status, "completed")
        self.assertEqual(len(result.completed), 7)
        self.assertEqual(len(result.compensations_run), 0)

        # Confirm Z4 tombstone occurred
        self.assertIn((party, "all"), self.residency.tombstone_log)
        self.assertTrue(self.residency.vault[party]["_tombstoned"])

        # Confirm all 7 steps executed in exact forward order
        expected_steps = [
            "EXEC:anonymize_regional",
            "EXEC:tombstone_resident",
            "EXEC:purge_read_replicas",
            "EXEC:purge_warehouse_rows",
            "EXEC:purge_object_store",
            "EXEC:purge_search_index",
            "EXEC:mark_backups_out_of_scope_next_cycle",
        ]
        self.assertEqual(self.drill_trace, expected_steps)

    def test_erasure_saga_catastrophic_failure_reverse_compensation_drill(self):
        """T01: Failure at step 4 (warehouse) triggers reverse compensation rollback of steps 3, 2, 1."""
        party = "party:cust_99"
        saga = SagaState(request_id="DSR-2026-DRILL-FAIL-02", party_ref=party)
        # Fail at warehouse purge (step 4)
        executors = self._make_drill_executors(fail_at_step=SagaStep.PURGE_WAREHOUSE)

        with self.assertRaises(DsrError) as ctx:
            run_erasure_saga(saga, executors, self.residency)

        self.assertIn("erasure saga failed at purge_warehouse_rows", str(ctx.exception))
        self.assertEqual(saga.failed_at, SagaStep.PURGE_WAREHOUSE)
        self.assertEqual(saga.status, "rolled_back")

        # Confirm exact reverse compensation order: replica -> resident -> regional
        expected_compensations = [
            "restore_purge_read_replicas",
            "restore_tombstone_resident",
            "restore_anonymize_regional",
        ]
        self.assertEqual(saga.compensations_run, expected_compensations)
        # Completed list reset to empty post-rollback
        self.assertEqual(len(saga.completed), 0)

    def test_5_year_processing_record_preservation(self):
        """T01 / NFR-095: Processing record retained 5 years past erasure."""
        erasure_date = date(2026, 10, 18)
        retention_end = erasure_preserves_record(erasure_date)
        # Exactly 5 years * 365 days
        self.assertEqual((retention_end - erasure_date).days, 365 * 5)
        self.assertEqual(PROCESSING_RECORD_YEARS, 5)

    def test_controller_30_day_notification_clock(self):
        """T01 / NFR-093: Controller notification within 30 days."""
        req = DsrRequest(
            request_id="REQ-001",
            dsr_type=DsrType.ERASURE,
            party_ref="party:cust_99",
            received_on=date(2026, 10, 18),
        )
        self.assertEqual(req.due_on, date(2026, 10, 18) + timedelta(days=30))
        self.assertEqual(NOTIFICATION_DAYS, 30)


if __name__ == "__main__":
    unittest.main()
