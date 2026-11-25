"""R01-AUDIT: verify_r11_m01_all derives each task from the producing tools'
computed verdicts; a success headline in a log, or post-go-live claims with no
evidenced cutover, can never PASS."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "scripts" / "verify_r11_m01_all.py"


def _load():
    spec = importlib.util.spec_from_file_location("verify_r11_m01_all_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TestR11M01Derived(unittest.TestCase):
    def setUp(self):
        self.v = _load()
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.v.CODEBASE_ROOT = self.root
        self.v.EVIDENCE_DIR = self.root / "docs" / "traceability" / "evidence"
        self.v.EVIDENCE_DIR.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def _evidence(self, name: str, data: dict) -> None:
        (self.v.EVIDENCE_DIR / name).write_text(json.dumps(data), encoding="utf-8")

    def _doc(self, rel: str, text: str = "x") -> None:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def test_success_headline_in_log_does_not_pass_incomplete_execution(self):
        self._doc("docs/traceability/r11-m01-cutover-execution-log.md", "PASS — 100% SUCCESSFUL")
        self._evidence("r11-m01-cutover-execution-evidence.json", {"status": "INCOMPLETE"})
        self.assertEqual(self.v.verify_t03_cutover_weekend_execution()["status"], "INCOMPLETE")

    def test_failed_rehearsal_fails(self):
        self._evidence("r11-m01-final-volume-rehearsal.json", {"status": "FAIL"})
        self._evidence("r11-m01-reconciliation-presignature.json", {"status": "UNMEASURED"})
        self.assertEqual(self.v.verify_t02_rehearsal_presignature()["status"], "FAIL")

    def test_missing_evidence_fails(self):
        self.assertEqual(self.v.verify_t03_cutover_weekend_execution()["status"], "FAIL")

    def test_post_go_live_claims_fail_without_cutover(self):
        self._doc("docs/operations/SV-004-hypercare-operating-manual.md")
        self._evidence(
            "r11-m01-hypercare-day1-stability-report.json",
            {"status": "PASS", "system_telemetry": {"uptime_percentage": 100.0}},
        )
        self.assertEqual(self.v.verify_t04_hypercare_operations("INCOMPLETE")["status"], "FAIL")
        # even after a PASSing cutover, production telemetry is not observable here
        self.assertEqual(self.v.verify_t04_hypercare_operations("PASS")["status"], "INCOMPLETE")

    def test_runbook_sections_and_walkthrough(self):
        self._doc(
            "docs/runbooks/RB-53-production-cutover-master-runbook.md",
            "\n".join(self.v.RB53_SECTIONS),
        )
        self._doc(
            "docs/traceability/r11-m01-cutover-runbook.md", "DRY-WALKTHROUGH CERTIFIED COMPLETE"
        )
        # a certified walkthrough is a human attestation: INCOMPLETE, never PASS
        self.assertEqual(self.v.verify_t01_cutover_runbook()["status"], "INCOMPLETE")
        self._doc("docs/runbooks/RB-53-production-cutover-master-runbook.md", "Smoke Gates")
        self.assertEqual(self.v.verify_t01_cutover_runbook()["status"], "FAIL")

    def test_summary_is_derived(self):
        tasks = [{"task_id": f"T{i}", "status": "PASS"} for i in range(5)]
        self.assertEqual(self.v.summarise(tasks)["overall_status"], "PASS")
        tasks[0]["status"] = "INCOMPLETE"
        self.assertEqual(self.v.summarise(tasks)["overall_status"], "INCOMPLETE")
        tasks[4]["status"] = "FAIL"
        self.assertEqual(self.v.summarise(tasks)["overall_status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
