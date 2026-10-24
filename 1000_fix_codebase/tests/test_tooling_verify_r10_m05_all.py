"""R01-AUDIT: verify_r10_m05_all derives MG-005 / GV-003 verdicts from the
current evidence - a document that merely names the invented
PROD_REHEARSAL_MG005_20261021 run can never make the milestone PASS."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "scripts" / "verify_r10_m05_all.py"
INVENTED = "PROD_REHEARSAL_MG005_20261021"


def _load():
    spec = importlib.util.spec_from_file_location("verify_r10_m05_all_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TestR10M05Derived(unittest.TestCase):
    def setUp(self):
        self.v = _load()
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.v.CODEBASE_ROOT = self.root
        self.v.EVIDENCE_DIR = self.root / "docs" / "traceability" / "evidence"
        self.v.QUARANTINE_DIR = self.root / "docs" / "traceability" / "quarantine-invented"
        self.v.FITNESS_EVIDENCE_DIR = self.root / "tooling" / "fitness" / "evidence"
        for d in (self.v.EVIDENCE_DIR, self.v.QUARANTINE_DIR, self.v.FITNESS_EVIDENCE_DIR):
            d.mkdir(parents=True)
        (self.v.QUARANTINE_DIR / f"{INVENTED}-control-totals.json").write_text("{}", "utf-8")
        # a REHEARSAL.md that still carries the old claim text must not matter
        (self.root / "migrations").mkdir()
        (self.root / "migrations" / "REHEARSAL.md").write_text(
            f"{INVENTED}\nGate GP-11 Discharge\n", encoding="utf-8"
        )

    def tearDown(self):
        self.tmp.cleanup()

    def _evidence(self, name: str, data: dict) -> None:
        (self.v.EVIDENCE_DIR / name).write_text(json.dumps(data), encoding="utf-8")

    def _rehearsal(self, status: str, discharged: bool, run_id: str = "R-REAL-1") -> None:
        self._evidence(
            "r10-m05-migration-rehearsal-evidence.json",
            {"status": status, "gp_11_discharged": discharged, "run_id": run_id},
        )
        self._evidence("r10-m05-mg004-business-signoff.json", {"verdict": "PASS"})

    def test_mg005_not_run_fails_despite_rehearsal_text(self):
        self._rehearsal("INCOMPLETE", discharged=False)
        result = self.v.verify_t02_migration_rehearsal()
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["mg005"], "NOT RUN")

    def test_measured_rehearsal_passes(self):
        self._rehearsal("PASS", discharged=True)
        result = self.v.verify_t02_migration_rehearsal()
        self.assertEqual(result["status"], "PASS", result["checks"])
        self.assertEqual(result["mg005"], "RUN")

    def test_quarantined_run_id_fails(self):
        self._rehearsal("PASS", discharged=True, run_id=INVENTED)
        self.assertEqual(self.v.verify_t02_migration_rehearsal()["status"], "FAIL")

    def test_invented_artefact_back_in_extracts_fails(self):
        self._rehearsal("PASS", discharged=True)
        extracts = self.root / "migrations" / "extracts"
        extracts.mkdir()
        (extracts / f"{INVENTED}-loaded-counts.json").write_text("{}", encoding="utf-8")
        result = self.v.verify_t02_migration_rehearsal()
        self.assertEqual(result["status"], "FAIL")

    def test_missing_evidence_fails(self):
        self.assertEqual(self.v.verify_t02_migration_rehearsal()["status"], "FAIL")

    def test_go_decision_citing_invented_run_fails(self):
        gov = self.root / "docs" / "governance"
        gov.mkdir(parents=True)
        (gov / "GV-003-production-readiness-go-decision.md").write_text(
            f"Rehearsal ({INVENTED}) reconciled 100%", encoding="utf-8"
        )
        self._evidence(
            "r10-m05-go-nogo-decision.json",
            {"determination": "GO", "votes": {"go_votes": 7, "total_board_members": 7}},
        )
        for name in ("r10-m04-dr-rehearsal-evidence.json", "r10-m04-ha-kill-node-evidence.json"):
            self._evidence(name, {"status": "PASS"})
        result = self.v.verify_t04_review_board_go({"T01": "PASS"})
        self.assertEqual(result["status"], "FAIL")
        (gov / "GV-003-production-readiness-go-decision.md").write_text("clean", encoding="utf-8")
        # votes are human attestations: at best INCOMPLETE, never PASS
        self.assertEqual(self.v.verify_t04_review_board_go({"T01": "PASS"})["status"], "INCOMPLETE")

    def test_training_certifications_are_never_pass(self):
        (self.root / "docs" / "training").mkdir(parents=True)
        (self.root / "docs" / "training" / "CH-002-training-closure-record.md").write_text(
            "x", "utf-8"
        )
        self._evidence(
            "r10-m05-training-closure-evidence.json",
            {"status": "PASS", "targets": {"certified_super_users": 85}},
        )
        self.assertEqual(self.v.verify_t03_training_closure()["status"], "INCOMPLETE")

    def test_summary_is_derived(self):
        tasks = [{"task_id": f"T{i}", "status": "PASS"} for i in range(4)]
        self.assertEqual(self.v.summarise(tasks)["overall_status"], "PASS")
        tasks[1]["status"] = "INCOMPLETE"
        self.assertEqual(self.v.summarise(tasks)["overall_status"], "INCOMPLETE")
        tasks[2]["status"] = "FAIL"
        self.assertEqual(self.v.summarise(tasks)["overall_status"], "FAIL")


class TestNoInventedProductionTotals(unittest.TestCase):
    def test_no_tooling_script_writes_production_shaped_rehearsal_artefacts(self):
        offenders = [
            p.relative_to(REPO_ROOT).as_posix()
            for p in (REPO_ROOT / "tooling").rglob("*.py")
            if "REAL_PRODUCTION_SHAPED" in p.read_text(encoding="utf-8", errors="ignore")
        ]
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
