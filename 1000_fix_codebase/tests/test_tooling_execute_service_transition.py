"""GV-009: execute_service_transition.py no longer writes invented SLA actuals or
"COMPLIANT"/"TRANSFERRED"/"UNCONDITIONALLY_ACCEPTED" literals: SLA rows are
UNMEASURED, custody artefacts are checked on disk, and the exit code follows
the computed verdict."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "scripts" / "execute_service_transition.py"


def _load():
    spec = importlib.util.spec_from_file_location("execute_service_transition_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


M = _load()


class TestServiceTransition(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.manual = self.root / "SV-004.md"
        rows = [f"| **{d}** | {lead} (Ext. 1) | x | {hub} |" for d, lead, _, hub in M.ON_CALL_ROTA]
        self.manual.write_text("\n".join(rows) + "\n", encoding="utf-8")
        for _, _, rel, _ in M.CUSTODY_ASSETS:
            path = self.root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("x", encoding="utf-8")
        runbook = self.root / "addons" / "m1" / "runbook.md"
        runbook.parent.mkdir(parents=True)
        runbook.write_text("x", encoding="utf-8")
        index = {"modules": [{"runbook_path": "addons/m1/runbook.md"}]}
        (self.root / M.RUNBOOK_INDEX).write_text(json.dumps(index), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def _statuses(self, report: dict) -> dict[str, str]:
        return {c["id"]: c["status"] for c in report["checks"]}

    def test_complete_repository_is_still_incomplete_without_production_data(self):
        report = M.verify_service_transition(self.root, self.manual)
        statuses = self._statuses(report)
        self.assertEqual(statuses["SV004_ROTA_DOCUMENTED"], "PASS")
        self.assertEqual(statuses["CUSTODY_RUNBOOK_INDEX"], "PASS")
        self.assertTrue(all(r["status"] == "UNMEASURED" for r in report["sla_performance"]))
        self.assertTrue(all(r["measured_actual"] is None for r in report["sla_performance"]))
        self.assertEqual(statuses["HANDOVER_SIGNATURES"], "UNMEASURED")
        self.assertEqual(report["handover_verdict"], "INCOMPLETE")
        self.assertEqual(M.exit_code(report["handover_verdict"]), 2)
        text = json.dumps(report)
        for literal in ("COMPLIANT", "TRANSFERRED", "UNCONDITIONALLY_ACCEPTED", "99.98"):
            self.assertNotIn(literal, text)

    def test_missing_artefacts_fail(self):
        (self.root / "addons" / "m1" / "runbook.md").unlink()
        (self.root / "tooling" / "scripts" / "doctor.ps1").unlink()
        report = M.verify_service_transition(self.root, self.manual)
        statuses = self._statuses(report)
        self.assertEqual(statuses["CUSTODY_RUNBOOK_INDEX"], "FAIL")
        self.assertEqual(statuses["CUSTODY_DOCTOR"], "FAIL")
        self.assertEqual(report["handover_verdict"], "FAIL")
        self.assertEqual(M.exit_code(report["handover_verdict"]), 1)

    def test_rota_lead_not_in_manual_fails(self):
        self.manual.write_text("| **Dhaka Central** | Someone Else (Ext. 1) |\n", encoding="utf-8")
        report = M.verify_service_transition(self.root, self.manual)
        self.assertEqual(self._statuses(report)["SV004_ROTA_DOCUMENTED"], "FAIL")
        self.assertEqual(report["handover_verdict"], "FAIL")

    def test_main_writes_computed_markdown_and_exit_code(self):
        out_ev, out_md = self.root / "ev", self.root / "md"
        original = M.verify_service_transition
        M.verify_service_transition = lambda: original(self.root, self.manual)
        try:
            code = M.main(out_ev, out_md)
        finally:
            M.verify_service_transition = original
        self.assertEqual(code, 2)
        md = (out_md / "r11-m04-service-transition-handover.md").read_text(encoding="utf-8")
        self.assertIn("INCOMPLETE", md)
        self.assertNotIn("COMPLIANT", md)
        self.assertNotIn("FORMALLY EXECUTED & ACCEPTED", md)


if __name__ == "__main__":
    unittest.main()
