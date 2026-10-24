"""GV-009: tooling/scripts/demonstrate-sla-engine.py derives its verdict from comparing what
SlaEngine returned with each case's expected state / tier / deadline - a misbehaving engine
yields FAIL (no literal verdict PASS, no assert-based verification)."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "scripts" / "demonstrate-sla-engine.py"


def _load():
    spec = importlib.util.spec_from_file_location("demonstrate_sla_engine_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class DemonstrateSlaEngineTest(unittest.TestCase):
    def setUp(self):
        self.m = _load()
        self.assertIsNone(self.m.SLA_IMPORT_ERROR)
        self.tmp = tempfile.TemporaryDirectory()
        self.m.EVIDENCE_FILE = Path(self.tmp.name) / "sla.json"

    def tearDown(self):
        self.tmp.cleanup()

    def _evidence(self) -> dict:
        return json.loads(self.m.EVIDENCE_FILE.read_text(encoding="utf-8"))

    def test_real_engine_matches_every_expectation(self):
        self.assertEqual(self.m.main(), 0)
        ev = self._evidence()
        self.assertEqual(ev["verdict"], "PASS")
        self.assertEqual(ev["checks_passed"], ev["checks_total"])
        self.assertTrue(all(c["status"] == "PASS" for c in ev["cases"]))

    def test_engine_that_never_escalates_fails(self):
        real = self.m.SlaEngine

        class FlatEngine(real):
            @classmethod
            def evaluate(cls, clock, current_time=None):
                res = real.evaluate(clock, current_time=current_time)
                res["state"] = "on_track"
                res["escalation_tier"] = "none"
                res["escalation_template"] = None
                return res

        self.m.SlaEngine = FlatEngine
        self.assertEqual(self.m.main(), 1)
        ev = self._evidence()
        self.assertEqual(ev["verdict"], "FAIL")
        statuses = {c["check"]: c["status"] for c in ev["checks"]}
        self.assertEqual(statuses["state_coverage"], "FAIL")
        self.assertEqual(statuses["escalation_tier_coverage"], "FAIL")
        self.assertEqual(statuses["case:CASE-01"], "PASS")
        self.assertEqual(statuses["case:CASE-03"], "FAIL")

    def test_engine_exception_is_recorded_as_fail(self):
        class BrokenEngine:
            @classmethod
            def evaluate(cls, clock, current_time=None):
                raise RuntimeError("boom")

        self.m.SlaEngine = BrokenEngine
        self.assertEqual(self.m.main(), 1)
        self.assertEqual(self._evidence()["verdict"], "FAIL")

    def test_import_failure_is_fail(self):
        self.m.SLA_IMPORT_ERROR = "ImportError: no sla_engine"
        self.assertEqual(self.m.main(), 1)
        ev = self._evidence()
        self.assertEqual(ev["verdict"], "FAIL")
        self.assertEqual(ev["checks"][0]["check"], "sla_engine_import")


if __name__ == "__main__":
    unittest.main()
