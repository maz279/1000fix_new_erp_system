"""GV-009: execute_financial_closure.py no longer writes an invented per-phase
effort/spend ledger or a "FAVOURABLE_VARIANCE_BUDGET_CLOSED_UNDER_CEILING"
verdict: planned effort is summed from cd-register.yaml and reconciled to
CO-003-AMD-01, actuals are UNMEASURED and the exit code follows the verdict."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "scripts" / "execute_financial_closure.py"


def _load():
    spec = importlib.util.spec_from_file_location("execute_financial_closure_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


M = _load()


class TestFinancialClosure(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.amendment = self.root / "amendment.md"
        self.amendment.write_text(
            "restated at 1,842 PW; register carries 1,850 PW across 331 units", encoding="utf-8"
        )
        self.register = self.root / "cd-register.yaml"

    def tearDown(self):
        self.tmp.cleanup()

    def _register(self, pws: list[int], count: int | None = None, pw_total: int | None = None):
        items = "".join(
            f"- id: CD-M01-{i:02d}\n  wave: W{1 + i % 2}\n  pw: {pw}\n" for i, pw in enumerate(pws)
        )
        header = (
            f"count: {len(pws) if count is None else count}\n"
            f"pw_total: {sum(pws) if pw_total is None else pw_total}\n"
        )
        self.register.write_text(header + "items:\n" + items, encoding="utf-8")

    def _run(self) -> dict:
        return M.compute_financial_closure(amendment_doc=self.amendment, cd_register=self.register)

    def _statuses(self, report: dict) -> dict[str, str]:
        return {c["id"]: c["status"] for c in report["checks"]}

    def test_reconciled_register_still_incomplete(self):
        pws = [5] * 331
        pws[0] += 1850 - sum(pws)
        self._register(pws)
        report = self._run()
        statuses = self._statuses(report)
        self.assertEqual(statuses["EFFORT_BASELINE_SOURCE"], M.PASS)
        self.assertEqual(statuses["CD_REGISTER_RECONCILIATION"], M.PASS)
        self.assertEqual(statuses["ACTUAL_SPEND_AND_VARIANCE"], M.UNMEASURED)
        self.assertEqual(report["summary"]["financial_verdict"], M.INCOMPLETE)
        self.assertEqual(M.exit_code(report["summary"]["financial_verdict"]), 2)
        self.assertEqual(report["planned_effort"]["register_planned_pw"], 1850)
        self.assertIsNone(report["actuals"]["actual_spend"])

    def test_register_drift_fails(self):
        pws = [5] * 332
        pws[0] += 1853 - sum(pws)
        self._register(pws)
        report = self._run()
        check = next(c for c in report["checks"] if c["id"] == "CD_REGISTER_RECONCILIATION")
        self.assertEqual(check["status"], M.FAIL)
        self.assertIn("+3 PW", check["detail"])
        self.assertEqual(report["summary"]["financial_verdict"], M.FAIL)
        self.assertEqual(M.exit_code(report["summary"]["financial_verdict"]), 1)

    def test_header_inconsistent_with_items_fails(self):
        pws = [5] * 331
        pws[0] += 1850 - sum(pws)
        self._register(pws, pw_total=1842)
        self.assertEqual(self._statuses(self._run())["CD_REGISTER_RECONCILIATION"], M.FAIL)

    def test_missing_sources_fail_without_crash(self):
        self.amendment.unlink()
        report = self._run()
        statuses = self._statuses(report)
        self.assertEqual(statuses["EFFORT_BASELINE_SOURCE"], M.FAIL)
        self.assertEqual(statuses["CD_REGISTER_RECONCILIATION"], M.FAIL)
        self.assertNotEqual(report["summary"]["financial_verdict"], M.PASS)

    def test_main_writes_computed_verdict(self):
        self._register([5, 6])
        evidence, trace = self.root / "evidence", self.root / "trace"
        saved = (M.EVIDENCE_DIR, M.TRACEABILITY_DIR)
        defaults = M.compute_financial_closure.__kwdefaults__
        M.EVIDENCE_DIR, M.TRACEABILITY_DIR = evidence, trace
        M.compute_financial_closure.__kwdefaults__ = {
            "amendment_doc": self.amendment,
            "cd_register": self.register,
        }
        try:
            code = M.main()
        finally:
            M.EVIDENCE_DIR, M.TRACEABILITY_DIR = saved
            M.compute_financial_closure.__kwdefaults__ = defaults
        self.assertEqual(code, 1)
        out = (evidence / "r11-m04-programme-financial-close.json").read_text(encoding="utf-8")
        self.assertEqual(json.loads(out)["summary"]["financial_verdict"], M.FAIL)
        md = (trace / "r11-m04-programme-financial-close.md").read_text(encoding="utf-8")
        self.assertNotIn("UNANIMOUSLY", md)
        self.assertIn("Financial verdict: FAIL", md)


if __name__ == "__main__":
    unittest.main()
