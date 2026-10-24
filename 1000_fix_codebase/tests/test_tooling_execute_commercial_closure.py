"""GV-009: execute_commercial_closure.py no longer writes fourteen invented
"APPROVED_AND_MERGED" change requests or a "UNANIMOUSLY_APPROVED" verdict: CR
dispositions are parsed from the CR documents, the scope baseline is read from
the requirements-baseline evidence, and the exit code follows the verdict."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "scripts" / "execute_commercial_closure.py"


def _load():
    spec = importlib.util.spec_from_file_location("execute_commercial_closure_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


M = _load()

APPROVED_CR = "# CR-X-01 — thing\n\n| | |\n|---|---|\n| **CR ID** | `CR-X-01` |\n| **Status** | **APPROVED & RATIFIED** |\n"
PENDING_CR = "# CR — other\n\n| Field | Value |\n|---|---|\n| CR id | CR-X-02 |\n| Decides | Change Board |\n"


class TestCommercialClosure(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.docs = self.root / "docs"
        (self.docs / "a").mkdir(parents=True)
        self.amendment = self.docs / "amendment.md"
        self.amendment.write_text("baseline 3,389 requirements and 122 NFRs", encoding="utf-8")
        self.baseline_dir = self.root / "baseline"
        self.baseline_dir.mkdir()
        self._baseline(3389, 122)
        self.rtm = self.root / "rtm.csv"
        self._rtm(["accepted"] * 3389)

    def tearDown(self):
        self.tmp.cleanup()

    def _baseline(self, population: int, nfrs: int) -> None:
        data = {"denominator": {"population": population}, "nfr": {"unique": nfrs}}
        path = self.baseline_dir / "requirements-baseline-2026-10-01.json"
        path.write_text(json.dumps(data), encoding="utf-8")

    def _rtm(self, statuses: list[str]) -> None:
        rows = ["requirement,status"] + [f"FR-{i},{s}" for i, s in enumerate(statuses)]
        self.rtm.write_text("\n".join(rows) + "\n", encoding="utf-8")

    def _run(self) -> dict:
        return M.audit_commercial_closure(
            root=self.root,
            docs_dir=self.docs,
            amendment_doc=self.amendment,
            baseline_dir=self.baseline_dir,
            rtm_csv=self.rtm,
        )

    def _statuses(self, report: dict) -> dict[str, str]:
        return {c["id"]: c["status"] for c in report["checks"]}

    def test_all_repo_checks_pass_but_human_items_keep_it_incomplete(self):
        (self.docs / "a" / "CR-one.md").write_text(APPROVED_CR, encoding="utf-8")
        report = self._run()
        statuses = self._statuses(report)
        for check in ("AMENDMENT_ON_DISK", "SCOPE_BASELINE_MATCHES", "REQUIREMENTS_ACCEPTANCE"):
            self.assertEqual(statuses[check], M.PASS, check)
        self.assertEqual(statuses["CHANGE_REQUEST_DISPOSITION"], M.PASS)
        self.assertEqual(statuses["VENDOR_SETTLEMENTS"], M.UNMEASURED)
        self.assertEqual(statuses["CONTRACT_SIGNATURES"], M.UNMEASURED)
        self.assertEqual(report["commercial_verdict"], M.INCOMPLETE)
        self.assertEqual(M.exit_code(report["commercial_verdict"]), 2)
        self.assertEqual(report["change_requests"]["items"][0]["cr_id"], "CR-X-01")

    def test_undispositioned_cr_fails(self):
        (self.docs / "a" / "CR-one.md").write_text(APPROVED_CR, encoding="utf-8")
        (self.docs / "a" / "CR-two.md").write_text(PENDING_CR, encoding="utf-8")
        report = self._run()
        self.assertEqual(self._statuses(report)["CHANGE_REQUEST_DISPOSITION"], M.FAIL)
        pending = [i for i in report["change_requests"]["items"] if i["cr_id"] == "CR-X-02"]
        self.assertEqual(pending[0]["disposition"], "NO_RECORDED_DISPOSITION")
        self.assertEqual(report["commercial_verdict"], M.FAIL)
        self.assertEqual(M.exit_code(report["commercial_verdict"]), 1)

    def test_status_classification(self):
        self.assertEqual(M.classify_cr_status("APPROVED & RATIFIED"), "DISPOSITIONED")
        self.assertEqual(M.classify_cr_status("Proposed"), "OPEN")
        self.assertEqual(M.classify_cr_status("approved, pending signature"), "OPEN")
        self.assertEqual(M.classify_cr_status(None), "NO_RECORDED_DISPOSITION")

    def test_seeded_rtm_and_baseline_drift_fail(self):
        (self.docs / "a" / "CR-one.md").write_text(APPROVED_CR, encoding="utf-8")
        self._rtm(["seeded"] * 10)
        self._baseline(3347, 122)
        statuses = self._statuses(self._run())
        self.assertEqual(statuses["REQUIREMENTS_ACCEPTANCE"], M.FAIL)
        self.assertEqual(statuses["SCOPE_BASELINE_MATCHES"], M.FAIL)

    def test_missing_inputs_are_unmeasured_or_fail_never_pass(self):
        self.amendment.unlink()
        for path in self.baseline_dir.iterdir():
            path.unlink()
        self.rtm.unlink()
        report = self._run()
        statuses = self._statuses(report)
        self.assertEqual(statuses["AMENDMENT_ON_DISK"], M.FAIL)
        self.assertEqual(statuses["SCOPE_BASELINE_MATCHES"], M.UNMEASURED)
        self.assertEqual(statuses["REQUIREMENTS_ACCEPTANCE"], M.UNMEASURED)
        self.assertEqual(statuses["CHANGE_REQUEST_DISPOSITION"], M.UNMEASURED)
        self.assertNotEqual(report["commercial_verdict"], M.PASS)

    def test_main_writes_computed_verdict(self):
        evidence, trace = self.root / "evidence", self.root / "trace"
        saved = (M.EVIDENCE_DIR, M.TRACEABILITY_DIR)
        defaults = M.audit_commercial_closure.__kwdefaults__
        M.EVIDENCE_DIR, M.TRACEABILITY_DIR = evidence, trace
        M.audit_commercial_closure.__kwdefaults__ = {
            "root": self.root,
            "docs_dir": self.docs,
            "amendment_doc": self.amendment,
            "baseline_dir": self.baseline_dir,
            "rtm_csv": self.rtm,
        }
        (self.docs / "a" / "CR-two.md").write_text(PENDING_CR, encoding="utf-8")
        try:
            code = M.main()
        finally:
            M.EVIDENCE_DIR, M.TRACEABILITY_DIR = saved
            M.audit_commercial_closure.__kwdefaults__ = defaults
        self.assertEqual(code, 1)
        out = (evidence / "r11-m04-commercial-closure-statement.json").read_text(encoding="utf-8")
        self.assertEqual(json.loads(out)["commercial_verdict"], M.FAIL)
        self.assertNotIn("APPROVED_AND_MERGED", out)
        md = (trace / "r11-m04-commercial-closure-statement.md").read_text(encoding="utf-8")
        self.assertIn("Commercial verdict: FAIL", md)


if __name__ == "__main__":
    unittest.main()
