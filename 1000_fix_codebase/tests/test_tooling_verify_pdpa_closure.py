"""GV-009: verify_pdpa_closure.py derives every status from the drills it runs;
the production drill, regulatory filing, CII covenants and the DP Forum
attestation are UNMEASURED (so the verdict is never PASS on its word), and a
broken saga / runbook / drill test is FAIL."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "scripts" / "verify_pdpa_closure.py"


def _load():
    spec = importlib.util.spec_from_file_location("verify_pdpa_closure_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


mod = _load()


def green(_target):
    return {"status": "PASS", "exit_code": 0}


class TestPdpaClosure(unittest.TestCase):
    def test_measured_drills_pass_but_verdict_is_incomplete(self):
        ev = mod.build_evidence(pytest_fn=green)
        for key in ("dsr_erasure_drill", "dsr_compensation_drill", "dsr_statutory_clocks"):
            self.assertEqual(ev["checks"][key]["status"], "PASS", ev["checks"][key])
        for key in ("production_dsr_drill", "regulatory_breach_filing", "cii_flow_down"):
            self.assertEqual(ev["checks"][key]["status"], "UNMEASURED")
        self.assertEqual(ev["checks"]["dp_forum_attestation"]["status"], "UNMEASURED")
        self.assertEqual(ev["verdict"], "INCOMPLETE")
        self.assertEqual(mod.exit_code_for(ev["verdict"]), 2)
        self.assertEqual(
            ev["checks"]["dsr_erasure_drill"]["steps_executed"], len(list(mod.SagaStep))
        )

    def test_red_breach_drill_test_fails_verdict(self):
        ev = mod.build_evidence(pytest_fn=lambda _t: {"status": "FAIL", "exit_code": 1})
        self.assertEqual(ev["verdict"], "FAIL")
        self.assertEqual(mod.exit_code_for(ev["verdict"]), 1)

    def test_broken_saga_fails_the_drill(self):
        original = mod.run_erasure_saga

        def skips_a_step(state, executors, residency=None):
            for step in list(mod.SagaStep)[:-1]:
                executors[step](state.party_ref)
                state.completed.append(step)
            return state

        mod.run_erasure_saga = skips_a_step
        try:
            res = mod.execute_dsr_erasure_drill()
        finally:
            mod.run_erasure_saga = original
        self.assertEqual(res["status"], "FAIL")
        self.assertTrue(res["problems"])

    def test_runbook_without_notify_or_72h_fails(self):
        res = mod.check_breach_runbook(["1. CONTAIN the systems", "2. RECORD everything"])
        self.assertEqual(res["status"], "FAIL")
        self.assertIn("NOTIFY", res["phases_missing"])
        self.assertFalse(res["states_72_hour_window"])

    def test_cii_fields_found_still_unmeasured(self):
        with tempfile.TemporaryDirectory() as tmp:
            model = Path(tmp) / "fix_msp.py"
            model.write_text(
                "from odoo import fields, models\n\n\n"
                "class FixMspContract(models.Model):\n"
                '    _name = "fix.msp.contract"\n'
                "    cii_designated = fields.Boolean()\n",
                encoding="utf-8",
            )
            res = mod.check_cii_flow_down(model)
        self.assertEqual(res["status"], "UNMEASURED")
        self.assertEqual(res["contract_model_fields"], ["cii_designated"])

    def test_main_writes_computed_markdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            saved = (mod.EVIDENCE_DIR, mod.DOCS_DIR, mod.build_evidence)
            orig_build = mod.build_evidence
            mod.EVIDENCE_DIR, mod.DOCS_DIR = out, out
            mod.build_evidence = lambda: orig_build(pytest_fn=green)
            try:
                code = mod.main()
            finally:
                mod.EVIDENCE_DIR, mod.DOCS_DIR, mod.build_evidence = saved
            data = json.loads((out / "r11-m03-pdpa-compliance-attestation.json").read_text("utf-8"))
            md = (out / "r11-m03-pdpa-closure-record.md").read_text(encoding="utf-8")
        self.assertEqual(code, 2)
        self.assertEqual(data["verdict"], "INCOMPLETE")
        self.assertIn("**`INCOMPLETE`**", md)
        self.assertNotIn("ATTESTED", md)


if __name__ == "__main__":
    unittest.main()
