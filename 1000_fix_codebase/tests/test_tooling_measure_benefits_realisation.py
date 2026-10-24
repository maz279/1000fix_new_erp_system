"""GV-009: measure_benefits_realisation.py no longer writes invented KPI actuals,
"EXCEEDED"/"PROMISE_FULFILLED" literals or a "SUBSTANTIATED_AND_VERIFIED" verdict:
baselines come from the KPI register, production actuals are UNMEASURED and the
exit code follows the computed verdict."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "scripts" / "measure_benefits_realisation.py"


def _load():
    spec = importlib.util.spec_from_file_location("measure_benefits_realisation_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


M = _load()


def _register(rows: list[dict], total: int | None = None) -> dict:
    n = len(rows) if total is None else total
    return {
        "total_registered": n,
        "reconciliation_bm002": {"registered_count": n},
        "register": rows,
    }


ROWS = [
    {"kpi": "KPI-001", "name": "Service order automation rate", "baseline": "20%"},
    {"kpi": "KPI-002", "name": "Average TAT", "baseline": "unmeasured"},
    {"kpi": "KPI-095", "name": "Overall automation of routine work", "baseline": "20%"},
]


class TestBenefitsRealisation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.register = self.root / "kpi-register.json"

    def tearDown(self):
        self.tmp.cleanup()

    def _write(self, data: dict) -> None:
        self.register.write_text(json.dumps(data), encoding="utf-8")

    def _statuses(self, report: dict) -> dict[str, str]:
        return {c["id"]: c["status"] for c in report["checks"]}

    def test_consistent_register_still_unmeasured_not_pass(self):
        self._write(_register(ROWS))
        report = M.measure_benefits(self.register)
        statuses = self._statuses(report)
        self.assertEqual(statuses["BM002_REGISTER_INTEGRITY"], M.PASS)
        self.assertEqual(statuses["PROMISE_AUTOMATION_70"], M.UNMEASURED)
        self.assertEqual(statuses["PROMISE_REVENUE_GROWTH_87"], M.UNMEASURED)
        self.assertEqual(statuses["KPI_PRODUCTION_ACTUALS"], M.UNMEASURED)
        self.assertEqual(report["executive_verdict"], M.INCOMPLETE)
        self.assertEqual(M.exit_code(report["executive_verdict"]), 2)
        self.assertEqual(report["summary"]["kpis_with_measured_actual"], 0)
        self.assertEqual(report["summary"]["kpis_with_recorded_baseline"], 2)
        self.assertTrue(all(m["measured_production_actual"] is None for m in report["metrics"]))
        auto = next(c for c in report["checks"] if c["id"] == "PROMISE_AUTOMATION_70")
        self.assertEqual(auto["register_kpi"], "KPI-095")

    def test_register_count_mismatch_fails(self):
        self._write(_register(ROWS, total=95))
        report = M.measure_benefits(self.register)
        self.assertEqual(self._statuses(report)["BM002_REGISTER_INTEGRITY"], M.FAIL)
        self.assertEqual(report["executive_verdict"], M.FAIL)
        self.assertEqual(M.exit_code(report["executive_verdict"]), 1)

    def test_missing_register_fails_without_crash(self):
        report = M.measure_benefits(self.root / "absent.json")
        self.assertEqual(report["executive_verdict"], M.FAIL)
        self.assertEqual(report["metrics"], [])

    def test_no_automation_kpi_fails_the_promise(self):
        self._write(_register([ROWS[1]]))
        report = M.measure_benefits(self.register)
        self.assertEqual(self._statuses(report)["PROMISE_AUTOMATION_70"], M.FAIL)

    def test_main_writes_computed_verdict_and_no_fabricated_literals(self):
        self._write(_register(ROWS))
        evidence, docs = self.root / "evidence", self.root / "docs"
        saved = (M.EVIDENCE_DIR, M.TRACEABILITY_DIR, M.KPI_REGISTER)
        original_defaults = M.measure_benefits.__defaults__
        M.EVIDENCE_DIR, M.TRACEABILITY_DIR, M.KPI_REGISTER = evidence, docs, self.register
        M.measure_benefits.__defaults__ = (self.register,)
        try:
            code = M.main()
        finally:
            M.EVIDENCE_DIR, M.TRACEABILITY_DIR, M.KPI_REGISTER = saved
            M.measure_benefits.__defaults__ = original_defaults
        self.assertEqual(code, 2)
        out = (evidence / "r11-m04-benefits-realisation-report.json").read_text(encoding="utf-8")
        self.assertEqual(json.loads(out)["executive_verdict"], M.INCOMPLETE)
        md = (docs / "r11-m04-benefits-realisation-report.md").read_text(encoding="utf-8")
        for literal in ("EXCEEDED", "PROMISE_FULFILLED", "SUBSTANTIATED", "APPROVED"):
            self.assertNotIn(literal, out)
            self.assertNotIn(literal, md)


if __name__ == "__main__":
    unittest.main()
