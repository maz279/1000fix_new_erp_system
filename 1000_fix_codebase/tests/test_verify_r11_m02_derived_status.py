"""R01-AUDIT: verify_r11_m02_all derives every task status and the overall
status from explicit checks - a failing or missing evidence file is a FAIL,
never a hard-coded MILESTONE_R11_M02_CERTIFIED_PASS."""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "scripts" / "verify_r11_m02_all.py"
REAL_EVIDENCE = REPO_ROOT / "docs" / "traceability" / "evidence"
REAL_DOCS = REPO_ROOT / "docs" / "traceability"

EVIDENCE = [
    "r11-m02-legacy-48-reconciliations.json",
    "r11-m02-legacy-reference-verification.json",
    "r11-m02-decommission-register.json",
    "r11-m02-archive-register.json",
]
DOCS = [
    "r11-m02-reconciliation-signoffs.md",
    "r11-m02-legacy-lookup-proof.md",
    "r11-m02-decommission-records.md",
    "r11-m02-archive-integrity-proof.md",
]


def _load():
    spec = importlib.util.spec_from_file_location("verify_r11_m02_all_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _passing_t01() -> dict:
    source = {
        "source_id": "SRC-01",
        "reconciliation_status": "RECONCILED_100_PERCENT",
        "approval_status": "APPROVED_FOR_DECOMMISSION",
        "variance_percentage": 0.0,
    }
    return {
        "overall_status": "PASS",
        "milestone": "R11-M02",
        "task": "R11-M02-T01",
        "total_sources_evaluated": 48,
        "total_sources_approved": 48,
        "estate_variance_rate": "0.00%",
        "total_records_profiled_and_reconciled": 10,
        "sources": [dict(source, source_id=f"SRC-{i:02d}") for i in range(48)],
    }


class TestDerivedStatus(unittest.TestCase):
    def setUp(self):
        self.v = _load()
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.evidence = root / "evidence"
        self.evidence.mkdir()
        self.v.EVIDENCE_DIR = str(self.evidence)
        self.v.DOCS_DIR = str(root)
        for name in DOCS:
            (root / name).write_text("# doc\n", encoding="utf-8")
        self._write(EVIDENCE[0], _passing_t01())

    def tearDown(self):
        self.tmp.cleanup()

    def _write(self, name: str, data: dict) -> None:
        (self.evidence / name).write_text(json.dumps(data), encoding="utf-8")

    def test_passing_evidence_passes(self):
        self.assertEqual(self.v.audit_t01()["status"], "PASS")

    def test_variance_fails_the_task(self):
        data = _passing_t01()
        data["sources"][7]["variance_percentage"] = 0.4
        self._write(EVIDENCE[0], data)
        result = self.v.audit_t01()
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("SRC-07" in f for f in result["failed_checks"]))

    def test_missing_evidence_fails_without_aborting(self):
        results = [f() for f in (self.v.audit_t01, self.v.audit_t02, self.v.audit_t03)]
        self.assertEqual([r["status"] for r in results], ["PASS", "FAIL", "FAIL"])
        summary = self.v.summarise(results)
        self.assertEqual(summary["overall_status"], "MILESTONE_R11_M02_FAIL")
        self.assertEqual(summary["total_tasks_passed"], 1)

    def test_overall_pass_only_when_every_task_passes(self):
        passing = [{"status": "PASS"}] * 4
        self.assertEqual(
            self.v.summarise(passing)["overall_status"], "MILESTONE_R11_M02_CERTIFIED_PASS"
        )
        self.assertEqual(
            self.v.summarise([*passing[:3], {"status": "FAIL"}])["overall_status"],
            "MILESTONE_R11_M02_FAIL",
        )
        self.assertEqual(self.v.summarise([])["overall_status"], "MILESTONE_R11_M02_FAIL")

    def test_committed_evidence_is_evaluated(self):
        """The committed R11-M02 evidence set, copied (the summary is never rewritten)."""
        for name in EVIDENCE:
            if (REAL_EVIDENCE / name).is_file():
                shutil.copy(REAL_EVIDENCE / name, self.evidence / name)
        for name in DOCS:
            if (REAL_DOCS / name).is_file():
                shutil.copy(REAL_DOCS / name, Path(self.v.DOCS_DIR) / name)
        results = [
            f() for f in (self.v.audit_t01, self.v.audit_t02, self.v.audit_t03, self.v.audit_t04)
        ]
        for r in results:
            # a status is exactly "no failed check" - never declared
            clean = not r["failed_checks"] and not r["unmeasured_checks"]
            self.assertEqual(r["status"] == "PASS", clean, r["task_id"])

    def test_evidence_verdict_is_never_upgraded_by_field_matches(self):
        data = _passing_t01()
        data["overall_status"] = "INCOMPLETE"
        self._write(EVIDENCE[0], data)
        self.assertEqual(self.v.audit_t01()["status"], "INCOMPLETE")
        data["overall_status"] = "COMPLETED_UNCONDITIONAL_APPROVAL"  # not a computed verdict
        self._write(EVIDENCE[0], data)
        self.assertEqual(self.v.audit_t01()["status"], "FAIL")

    def test_incomplete_tasks_make_an_incomplete_milestone(self):
        tasks = [
            {"status": "PASS"},
            {"status": "INCOMPLETE"},
            {"status": "PASS"},
            {"status": "PASS"},
        ]
        self.assertEqual(self.v.summarise(tasks)["overall_status"], "MILESTONE_R11_M02_INCOMPLETE")


if __name__ == "__main__":
    unittest.main()
