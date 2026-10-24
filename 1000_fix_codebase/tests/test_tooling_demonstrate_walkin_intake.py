"""GV-009: tooling/scripts/demonstrate-walkin-intake.py measures intake durations from
recorded timestamps (read-only) - no random durations, no INSERTs, no hard-coded PASS /
100% compliance; an unreachable DB is UNMEASURED and the staff demonstration needs a human."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "scripts" / "demonstrate-walkin-intake.py"
START = datetime(2026, 10, 20, 9, 0, 0)


def _load():
    spec = importlib.util.spec_from_file_location("demonstrate_walkin_intake_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _row(i: int, seconds: int, *, stored=None, statement="walk-in", fault="Cracked screen"):
    start = START + timedelta(minutes=10 * i)
    return {
        "id": 100 + i,
        "intake_start": start,
        "handover_complete": start + timedelta(seconds=seconds),
        "intake_duration_seconds": seconds if stored is None else stored,
        "handover_acknowledged": True,
        "handover_method": "otp",
        "fault_description": fault,
        "customer_statement": statement,
        "state": "completed",
    }


class DemonstrateWalkinIntakeTest(unittest.TestCase):
    def setUp(self):
        self.m = _load()
        self.tmp = tempfile.TemporaryDirectory()
        self.m.EVIDENCE_FILE = Path(self.tmp.name) / "walkin.json"

    def tearDown(self):
        self.tmp.cleanup()

    def _statuses(self, ev: dict) -> dict:
        return {c["check"]: c["status"] for c in ev["checks"]}

    def test_unreachable_db_is_unmeasured(self):
        def refused():
            raise ConnectionError("connection refused")

        ev = self.m.run_measurement(fetch=refused)
        self.assertEqual(self._statuses(ev)["application_recorded_intake_timings"], "UNMEASURED")
        self.assertEqual(ev["verdict"], "INCOMPLETE")
        self.assertEqual(ev["runs"], [])

    def test_slow_intake_fails(self):
        rows = [_row(i, 120) for i in range(9)] + [_row(9, 200)]
        ev = self.m.run_measurement(fetch=lambda: rows)
        self.assertEqual(self._statuses(ev)["application_recorded_intake_timings"], "FAIL")
        self.assertEqual(ev["verdict"], "FAIL")
        self.assertEqual(ev["max_duration_seconds"], 200)
        self.assertEqual(ev["compliance_pct"], 90.0)

    def test_stored_duration_mismatch_fails(self):
        rows = [_row(i, 120) for i in range(10)]
        rows[3] = _row(3, 120, stored=60)
        ev = self.m.run_measurement(fetch=lambda: rows)
        self.assertEqual(ev["verdict"], "FAIL")

    def test_fast_intakes_still_not_pass_without_staff_demonstration(self):
        rows = [_row(i, 100 + i) for i in range(10)]
        ev = self.m.run_measurement(fetch=lambda: rows)
        statuses = self._statuses(ev)
        self.assertEqual(statuses["application_recorded_intake_timings"], "PASS")
        self.assertEqual(statuses["branch_staff_demonstration"], "UNMEASURED")
        self.assertEqual(ev["verdict"], "INCOMPLETE")
        self.assertEqual(ev["mean_duration_seconds"], 104.5)

    def test_rows_synthesised_by_old_script_are_excluded(self):
        fault = self.m.COMMON_FAULTS[0]
        rows = [_row(i, 120, statement=f"Customer stated: {fault}", fault=fault) for i in range(10)]
        ev = self.m.run_measurement(fetch=lambda: rows)
        self.assertEqual(ev["excluded_synthesised_records"], 10)
        self.assertEqual(ev["qualifying_intakes"], 0)
        self.assertEqual(self._statuses(ev)["application_recorded_intake_timings"], "UNMEASURED")

    def test_main_exit_code_and_evidence_are_derived(self):
        def refused():
            raise ConnectionError("connection refused")

        self.m.fetch_completed_intakes = refused
        self.assertEqual(self.m.main(), 2)
        ev = json.loads(self.m.EVIDENCE_FILE.read_text(encoding="utf-8"))
        self.assertEqual(ev["verdict"], "INCOMPLETE")
        self.assertNotIn("demonstrated_by", ev)


if __name__ == "__main__":
    unittest.main()
