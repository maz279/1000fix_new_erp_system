"""GV-009: execute_cutover_weekend.py no longer logs a production cutover that did
not happen as PASS - every production step is UNMEASURED, the preconditions are
measured, and the record is never PASS / "100_PERCENT_PASS" / certified."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "scripts" / "execute_cutover_weekend.py"

RUNBOOK = """# RB-53-PRODUCTION-CUTOVER-MASTER
Freeze legacy sources. Hard Rollback Triggers apply.
### 4. Automated Smoke Gates
| ID | Journey | Assertion |
|---|---|---|
| `J01` | Customer Online Booking | ok |
| `J02` | Walk-in Intake | ok |
"""


def _load():
    spec = importlib.util.spec_from_file_location("execute_cutover_weekend_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


M = _load()


class TestCutoverRecord(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.evidence = root / "evidence"
        self.trace = root / "trace"
        self.runbook = root / "RB-53.md"
        self.runbook.write_text(RUNBOOK, encoding="utf-8")
        self.evidence.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def _rehearsal(self, status: str) -> None:
        path = self.evidence / M.REHEARSAL_EVIDENCE_NAME
        path.write_text(json.dumps({"status": status}), encoding="utf-8")

    def _run(self):
        return M.execute_cutover(self.evidence, self.trace, self.runbook)

    def _steps(self, evidence: dict) -> dict[str, str]:
        return {s["step"]: s["verdict"] for s in evidence["steps_executed"]}

    def test_unobservable_production_steps_are_unmeasured(self):
        self._rehearsal("PASS")
        evidence, log_path = self._run()
        steps = self._steps(evidence)
        self.assertEqual(steps["PRE-01-RUNBOOK"], "PASS")
        self.assertEqual(steps["PRE-02-REHEARSAL"], "PASS")
        for step_id, _, _ in M.CUTOVER_STEPS:
            self.assertEqual(steps[step_id], "UNMEASURED")
        self.assertEqual(evidence["status"], "INCOMPLETE")
        self.assertEqual(M.exit_code(evidence["status"]), 2)
        self.assertEqual(evidence["smoke_gate"]["total_journeys"], 2)
        self.assertIsNone(evidence["smoke_gate"]["passed_journeys"])
        self.assertNotEqual(evidence["live_traffic_status"], "ACTIVE_UNFROZEN")
        log = Path(log_path).read_text(encoding="utf-8")
        self.assertNotIn("PASS — 100% SUCCESSFUL", log)
        self.assertNotIn("[CERTIFIED]", log)
        self.assertNotIn("100_PERCENT_PASS", json.dumps(evidence))

    def test_failed_rehearsal_fails_the_record(self):
        self._rehearsal("FAIL")
        evidence, _ = self._run()
        self.assertEqual(self._steps(evidence)["PRE-02-REHEARSAL"], "FAIL")
        self.assertEqual(evidence["status"], "FAIL")
        self.assertEqual(M.exit_code(evidence["status"]), 1)

    def test_missing_runbook_and_rehearsal(self):
        self.runbook.unlink()
        evidence, _ = self._run()
        steps = self._steps(evidence)
        self.assertEqual(steps["PRE-01-RUNBOOK"], "FAIL")
        self.assertEqual(steps["PRE-02-REHEARSAL"], "UNMEASURED")
        self.assertEqual(evidence["status"], "FAIL")
        written = json.loads((self.evidence / M.EVIDENCE_NAME).read_text(encoding="utf-8"))
        self.assertEqual(written["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
