"""R01-AUDIT: verify_r10_m04_all derives every task status and detail from the
producing tools' evidence; a FAIL/INCOMPLETE/missing input is never PASS and a
producer's non-zero exit never aborts the audit."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "scripts" / "verify_r10_m04_all.py"


def _load():
    spec = importlib.util.spec_from_file_location("verify_r10_m04_all_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PASSING = {
    "r10-m04-environment-data-rules-audit.json": {
        "total_environments": 12,
        "passed": True,
        "violations": [],
    },
    "r10-m04-clone-masking-evidence.json": {
        "status": "PASS",
        "nfr_086c_compliant": True,
        "lines_processed": 8,
        "residual_pii_lines": 0,
    },
    "r10-m04-dr-rehearsal-evidence.json": {
        "status": "PASS",
        "actual_rpo_seconds": 3,
        "actual_rto_seconds": 600,
        "rpo_compliant": True,
        "rto_compliant": True,
    },
    "r10-m04-gp12-drill-evidence.json": {
        "status": "PASS",
        "gp_12_discharged": True,
        "immutable_digest": "sha256:abc",
        "promotion_ladder": [1, 2, 3, 4],
    },
    "r10-m04-handover-signoff.json": {"all_approved": True, "signoffs": [{"role": "CTO"}]},
    "r10-m04-ha-kill-node-evidence.json": {"status": "PASS", "drills": [{"status": "PASS"}]},
    "r10-m04-secret-scan-evidence.json": {
        "status": "PASS",
        "violations_found": 0,
        "files_scanned": 10,
    },
}


class TestR10M04Derived(unittest.TestCase):
    def setUp(self):
        self.v = _load()
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.v.REPO_ROOT = root
        self.v.EVIDENCE_DIR = root / "docs" / "traceability" / "evidence"
        self.v.EVIDENCE_DIR.mkdir(parents=True)
        for rel in (
            "docs/runbooks/RB-52-dr-disaster-recovery-and-cutover.md",
            "docs/operator/OPERATOR_MANUAL.md",
            "docs/traceability/r10-m04-operator-handover.md",
            "docs/decisions/D-042-three-release-expand-contract-migration-protocol.md",
        ):
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text("x", encoding="utf-8")
        self.producer_calls: list[list[str]] = []
        # self.v.subprocess IS the global subprocess module: restore run() on
        # teardown, or the stub leaks into every later test in the process
        # (11 migrations/tests failed in full-suite runs, R01 re-audit).
        self.addCleanup(setattr, self.v.subprocess, "run", self.v.subprocess.run)
        self.v.subprocess.run = lambda cmd, **kw: self.producer_calls.append(cmd)
        for name, data in PASSING.items():
            self._write(name, data)

    def tearDown(self):
        self.tmp.cleanup()

    def _write(self, name: str, data: dict) -> None:
        (self.v.EVIDENCE_DIR / name).write_text(json.dumps(data), encoding="utf-8")

    def test_all_passing_evidence_is_incomplete_only_for_human_signoffs(self):
        summary = self.v.run_milestone_audit()
        statuses = [t["status"] for t in summary["tasks"]]
        # T05's recorded sign-offs are human attestations: UNMEASURED, never PASS
        self.assertEqual(statuses, ["PASS", "PASS", "PASS", "PASS", "INCOMPLETE", "PASS"])
        self.assertEqual(summary["status"], "INCOMPLETE")
        self.assertEqual(self.producer_calls, [])

    def test_unapproved_handover_fails(self):
        self._write("r10-m04-handover-signoff.json", {"all_approved": False, "signoffs": []})
        self.assertEqual(self.v.run_milestone_audit()["tasks"][4]["status"], "FAIL")

    def test_failing_drill_fails_the_milestone(self):
        self._write(
            "r10-m04-dr-rehearsal-evidence.json",
            {"status": "FAIL", "rpo_compliant": None, "rto_compliant": None},
        )
        summary = self.v.run_milestone_audit()
        t03 = summary["tasks"][2]
        self.assertEqual(t03["status"], "FAIL")
        self.assertIn("RPO unmeasured", t03["details"])
        self.assertEqual(summary["status"], "FAIL")

    def test_incomplete_drill_is_incomplete_not_pass(self):
        self._write(
            "r10-m04-gp12-drill-evidence.json",
            {"status": "INCOMPLETE", "gp_12_discharged": False, "immutable_digest": None},
        )
        summary = self.v.run_milestone_audit()
        self.assertEqual(summary["tasks"][3]["status"], "INCOMPLETE")
        self.assertEqual(summary["status"], "INCOMPLETE")

    def test_missing_evidence_runs_producer_without_aborting_and_fails(self):
        (self.v.EVIDENCE_DIR / "r10-m04-ha-kill-node-evidence.json").unlink()
        summary = self.v.run_milestone_audit()
        self.assertEqual(len(self.producer_calls), 1)
        self.assertEqual(summary["tasks"][5]["status"], "FAIL")
        self.assertEqual(summary["status"], "FAIL")

    def test_unmeasured_rpo_on_passing_evidence_is_incomplete(self):
        self._write(
            "r10-m04-dr-rehearsal-evidence.json",
            {"status": "PASS", "rpo_compliant": None, "rto_compliant": True},
        )
        self.assertEqual(self.v.run_milestone_audit()["tasks"][2]["status"], "INCOMPLETE")


if __name__ == "__main__":
    unittest.main()
