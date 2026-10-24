"""GV-009: generate_dod15_remediation.py no longer writes invented remediation
actions or a literal-PASS markdown record: open findings come from the pentest
re-test evidence, SAST counts from the scan's summary, unmeasured vectors and
unowned medium/low items keep the record from PASS, and the exit code follows
the computed verdict."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "scripts" / "generate_dod15_remediation.py"


def _load():
    spec = importlib.util.spec_from_file_location("generate_dod15_remediation_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


M = _load()


def _pentest(high: int = 0, unmeasured: int = 0, low: int = 0) -> dict:
    findings = [{"code": f"A0{i}", "severity": "HIGH", "vector": "v"} for i in range(high)]
    return {
        "timestamp": "2026-10-22T00:00:00+00:00",
        "summary": {
            "total_tests": 10,
            "measured_tests": 10 - unmeasured,
            "unmeasured_tests": unmeasured,
            "critical_findings": 0,
            "high_findings": high,
            "medium_findings": 0,
            "low_informational": low,
        },
        "vector_results": {"A": [{"code": "U1", "outcome": "UNMEASURED"}] * unmeasured},
        "findings": findings,
    }


def _sast(high: int = 0, verdict: str = "PASS") -> dict:
    return {
        "timestamp": "2026-10-21T00:00:00+00:00",
        "verdict": verdict,
        "summary": {"critical": 0, "high": high, "medium": 0, "low": 0},
    }


class TestDod15Remediation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.pentest = self.root / "pentest.json"
        self.sast = self.root / "sast.json"

    def tearDown(self):
        self.tmp.cleanup()

    def _write(self, pentest: dict | None, sast: dict | None) -> dict:
        for path, data in ((self.pentest, pentest), (self.sast, sast)):
            if data is not None:
                path.write_text(json.dumps(data), encoding="utf-8")
        return M.build_record(self.pentest, self.sast)

    def _statuses(self, record: dict) -> dict[str, str]:
        return {c["id"]: c["status"] for c in record["checks"]}

    def test_clean_inputs_pass(self):
        record = self._write(_pentest(), _sast())
        self.assertEqual(record["summary"]["status"], M.PASS)
        self.assertTrue(record["summary"]["all_critical_high_remediated"])
        self.assertEqual(M.exit_code(record["summary"]["status"]), 0)

    def test_open_high_finding_fails(self):
        record = self._write(_pentest(high=2), _sast())
        self.assertEqual(self._statuses(record)["PENTEST_CRITICAL_HIGH"], M.FAIL)
        self.assertEqual(record["summary"]["status"], M.FAIL)
        self.assertFalse(record["summary"]["all_critical_high_remediated"])
        self.assertEqual([a["status"] for a in record["remediation_actions"]], ["OPEN", "OPEN"])
        self.assertEqual(M.exit_code(record["summary"]["status"]), 1)

    def test_sast_high_is_read_from_summary(self):
        record = self._write(_pentest(), _sast(high=1))
        self.assertEqual(self._statuses(record)["SAST_CRITICAL_HIGH"], M.FAIL)
        self.assertEqual(record["summary"]["high_findings_open"], 1)

    def test_unmeasured_vectors_and_unowned_lows_are_incomplete(self):
        record = self._write(_pentest(unmeasured=1, low=2), _sast())
        statuses = self._statuses(record)
        self.assertEqual(statuses["RETEST_COVERAGE"], M.UNMEASURED)
        self.assertEqual(statuses["MEDIUM_LOW_OWNERSHIP"], M.UNMEASURED)
        self.assertEqual(record["summary"]["status"], M.INCOMPLETE)
        self.assertEqual(M.exit_code(record["summary"]["status"]), 2)

    def test_missing_evidence_is_unmeasured_not_crash(self):
        record = self._write(None, None)
        self.assertEqual(set(self._statuses(record).values()), {M.UNMEASURED})
        self.assertIsNone(record["summary"]["all_critical_high_remediated"])
        self.assertEqual(record["summary"]["status"], M.INCOMPLETE)

    def test_main_writes_computed_status(self):
        self._write(_pentest(high=1), _sast())
        saved = (M.EVIDENCE_DIR, M.SECURITY_DOCS_DIR)
        defaults = M.build_record.__defaults__
        M.EVIDENCE_DIR, M.SECURITY_DOCS_DIR = self.root / "ev", self.root / "sec"
        M.build_record.__defaults__ = (self.pentest, self.sast)
        try:
            code = M.main()
        finally:
            M.EVIDENCE_DIR, M.SECURITY_DOCS_DIR = saved
            M.build_record.__defaults__ = defaults
        self.assertEqual(code, 1)
        out = json.loads(
            (self.root / "ev" / "r09-m05-security-remediation-evidence.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(out["summary"]["status"], M.FAIL)
        md = (self.root / "sec" / "DoD-15-security-remediation-record.md").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("Signed & Verified", md)
        self.assertIn("Overall status: FAIL", md)


if __name__ == "__main__":
    unittest.main()
