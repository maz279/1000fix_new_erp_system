"""GV-009: execute-branch-rollout.py derives every readiness status from the
read-only branch register and the D-002 roster; site inspections, training
records, approvals and go-live are UNMEASURED, an unreachable database is
UNMEASURED (not a crash, not PASS), and missing staff is a FAIL."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "scripts" / "execute-branch-rollout.py"


def _load():
    spec = importlib.util.spec_from_file_location("execute_branch_rollout_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


M = _load()
ALL_CODES = sorted(c for codes in M.WAVE_PLAN.values() for c in codes)


def rows(employees: int = 3, ou: str | None = "OU1") -> list[tuple]:
    return [(c, c, c, True, f"BR:{c}", ou, ou, employees) for c in ALL_CODES]


class TestBranchRollout(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.saved = (M.FITNESS_EVIDENCE_DIR, M.DOCS_EVIDENCE_DIR, M.D002_ROSTER)
        M.FITNESS_EVIDENCE_DIR, M.DOCS_EVIDENCE_DIR = root / "fit", root / "docs"
        M.D002_ROSTER = root / "D-002.md"
        lines = [
            f"| **{name}** (`{lead_id}`) | {role} |"
            for cohort in M.SUPERUSER_COHORTS.values()
            for lead_id, name, role, _ in cohort["leads"]
        ]
        M.D002_ROSTER.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.saved_db = M.verify_branches_in_db

    def tearDown(self):
        M.FITNESS_EVIDENCE_DIR, M.DOCS_EVIDENCE_DIR, M.D002_ROSTER = self.saved
        M.verify_branches_in_db = self.saved_db
        self.tmp.cleanup()

    def _run(self, db):
        M.verify_branches_in_db = db
        return M.execute_rollout()

    def _all(self, evidence: dict) -> dict[str, str]:
        out = {c["id"]: c["status"] for c in evidence["checks"]}
        for wave in evidence["waves"].values():
            out.update(
                {f"W{wave['wave']}:{k}": v["status"] for k, v in wave["readiness_checks"].items()}
            )
        return out

    def test_unreachable_db_is_unmeasured(self):
        def down():
            raise OSError("connection refused")

        ev = self._run(down)
        statuses = self._all(ev)
        self.assertEqual(statuses["ROLLOUT_REGISTER_TARGET"], "UNMEASURED")
        self.assertEqual(statuses["W1:RB-04_staff_roster"], "UNMEASURED")
        self.assertEqual(statuses["D002_ROSTER"], "PASS")
        self.assertEqual(ev["verdict"], "INCOMPLETE")
        self.assertEqual(M.exit_code(ev["verdict"]), 2)
        self.assertIsNone(ev["total_service_centres_registered"])
        written = json.loads(
            (M.DOCS_EVIDENCE_DIR / "branch-rollout-evidence.json").read_text("utf-8")
        )
        self.assertEqual(written["verdict"], "INCOMPLETE")

    def test_unstaffed_centres_fail(self):
        ev = self._run(lambda: rows(employees=0))
        statuses = self._all(ev)
        self.assertEqual(statuses["ROLLOUT_REGISTER_TARGET"], "PASS")
        self.assertEqual(statuses["ROLLOUT_WAVE_PLAN"], "PASS")
        self.assertEqual(statuses["W2:RB-04_staff_roster"], "FAIL")
        self.assertEqual(ev["verdict"], "FAIL")
        self.assertIn("W2:RB-04_staff_roster", ev["rollout_blockers"])
        self.assertEqual(M.exit_code(ev["verdict"]), 1)

    def test_measured_ready_register_is_still_not_pass(self):
        ev = self._run(rows)
        statuses = self._all(ev)
        self.assertEqual(statuses["W1:RB-03_operating_unit"], "PASS")
        self.assertEqual(statuses["W1:RB-04_staff_roster"], "PASS")
        self.assertEqual(statuses["W1:GO_LIVE"], "UNMEASURED")
        self.assertEqual(statuses["W4:RB-12_director_approval"], "UNMEASURED")
        self.assertEqual(ev["verdict"], "INCOMPLETE")
        self.assertIsNone(ev["total_service_centres_live"])
        self.assertNotIn("score", json.dumps(ev))

    def test_short_register_fails_target_and_plan(self):
        ev = self._run(lambda: rows()[:40])
        statuses = self._all(ev)
        self.assertEqual(statuses["ROLLOUT_REGISTER_TARGET"], "FAIL")
        self.assertEqual(statuses["ROLLOUT_WAVE_PLAN"], "FAIL")
        self.assertEqual(ev["verdict"], "FAIL")

    def test_lead_missing_from_roster_fails(self):
        M.D002_ROSTER.write_text("| nobody |\n", encoding="utf-8")
        ev = self._run(rows)
        self.assertEqual(self._all(ev)["D002_ROSTER"], "FAIL")
        self.assertEqual(ev["verdict"], "FAIL")


if __name__ == "__main__":
    unittest.main()
