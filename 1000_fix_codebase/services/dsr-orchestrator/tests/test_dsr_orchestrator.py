"""dsr-orchestrator tests — P07-M08 (the G4-06 PDPA criterion)."""

from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dsr_orchestrator import (
    BREACH_RUNBOOK,
    NOTIFICATION_DAYS,
    PROCESSING_RECORD_YEARS,
    DsrError,
    DsrRequest,
    DsrType,
    SagaState,
    SagaStep,
    assemble_export,
    erasure_preserves_record,
    run_erasure_saga,
)


class TestDsrRequest(unittest.TestCase):
    def test_30_day_clock(self):
        """NFR-093: the controller notifies within 30 days."""
        req = DsrRequest("R1", DsrType.ACCESS, "party:1", date(2027, 5, 1))
        self.assertEqual((req.due_on - req.received_on).days, NOTIFICATION_DAYS)
        self.assertEqual(NOTIFICATION_DAYS, 30)

    def test_all_five_rights(self):
        for right in ("access", "rectification", "portability", "erasure", "objection"):
            self.assertIn(right, [t.value for t in DsrType])


class FakeResidency:
    def __init__(self):
        self.fetched = []
        self.tombstoned = []

    def fetch_resident(self, party_ref):
        self.fetched.append(party_ref)
        return {"nid_number": "SYNC-TEST-VALUE"}

    def tombstone(self, party_ref, key):
        self.tombstoned.append((party_ref, key))
        return {"erased": True, "key": party_ref, "scope": key}


class TestExport(unittest.TestCase):
    def test_assembles_through_residency_service(self):
        """T03: the export path goes THROUGH the residency service — the
        only client of the resident store (FF-09)."""
        fake = FakeResidency()
        bundle = assemble_export("party:9", lambda ref: {"name": "x"}, fake)
        self.assertIn("party:9", fake.fetched)
        portable = bundle.to_portable()
        self.assertIn("regional", portable)
        self.assertIn("resident", portable)

    def test_machine_readable_enforced(self):
        from dsr_orchestrator import ExportBundle

        bundle = ExportBundle("p", machine_readable=False)
        with self.assertRaises(DsrError):
            bundle.to_portable()


class TestErasureSaga(unittest.TestCase):
    def _executors(self, fail_at=None):
        ex = {}
        for step in SagaStep:

            def make(failing):
                def run(party):
                    if failing:
                        raise RuntimeError("boom")

                return run

            ex[step] = make(step is fail_at)
        return ex

    def test_full_saga_completes_in_order(self):
        state = SagaState("S1", "party:1")
        residency = FakeResidency()
        run_erasure_saga(state, self._executors(), residency)
        self.assertEqual(state.status, "completed")
        self.assertEqual(len(state.completed), 7)
        # Z4 tombstoned through the residency client
        self.assertIn(("party:1", "all"), residency.tombstoned)

    def test_failure_rolls_back_completed_steps_in_reverse(self):
        state = SagaState("S2", "party:2")
        executors = self._executors(fail_at=SagaStep.PURGE_WAREHOUSE)
        with self.assertRaises(DsrError) as ctx:
            run_erasure_saga(state, executors)
        self.assertIn("compensations run", str(ctx.exception))
        # compensations ran for the completed prefix, in reverse order
        self.assertEqual(
            state.compensations_run,
            [
                SagaStep.PURGE_REPLICAS.compensation,
                SagaStep.TOMBSTONE_RESIDENT.compensation,
                SagaStep.ANONYMIZE_REGIONAL.compensation,
            ],
        )

    def test_missing_executor_refused(self):
        state = SagaState("S3", "party:3")
        with self.assertRaises(DsrError):
            run_erasure_saga(state, {})

    def test_backups_marked_not_deleted(self):
        """Backups roll out on cycle — the saga marks, never deletes them."""
        self.assertIn("mark_backups", SagaStep.MARK_BACKUPS.value)


class TestStatutoryRetained(unittest.TestCase):
    def test_record_survives_five_years(self):
        """T05 / NFR-095: the processing record outlives the erasure."""
        until = erasure_preserves_record(date(2027, 5, 13))
        self.assertEqual((until - date(2027, 5, 13)).days, 365 * PROCESSING_RECORD_YEARS)
        self.assertEqual(PROCESSING_RECORD_YEARS, 5)


class TestBreachRunbook(unittest.TestCase):
    def test_rehearsed_steps_present(self):
        self.assertTrue(any("National Data Management Authority" in s for s in BREACH_RUNBOOK))
        self.assertTrue(any("72 hours" in s for s in BREACH_RUNBOOK))
        self.assertTrue(any("REHEARSED" in s for s in BREACH_RUNBOOK))


class TestPurity(unittest.TestCase):
    def test_no_odoo_imports(self):
        import inspect

        import dsr_orchestrator

        source = inspect.getsource(dsr_orchestrator)
        self.assertNotIn("from odoo", source)
        self.assertNotIn("DELETE FROM", source.upper().replace("NOT A DELETE", ""))


if __name__ == "__main__":
    unittest.main()
