"""GV-009: verify_iso9001_surveillance.py no longer writes invented audits,
NCRs, CAPAs or a "MAINTAINED" certificate: the M23 code controls are checked by
AST, production QMS records and the certificate are UNMEASURED, and the exit
code follows the computed verdict."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "scripts" / "verify_iso9001_surveillance.py"


def _load():
    spec = importlib.util.spec_from_file_location("verify_iso9001_surveillance_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


M = _load()

GOOD_MODELS = """
class Ncr:
    _name = "fix.ncr"

class Audit:
    _name = "fix.internal.audit"

class Capa:
    _name = "fix.capa"

    def action_close(self):
        for rec in self:
            if rec.state != "verified":
                raise ValueError("Closure follows verification")
            rec.state = "closed"
"""

UNGUARDED_CAPA = GOOD_MODELS.replace(
    '            if rec.state != "verified":\n                raise ValueError("Closure follows verification")\n',
    "",
)


class TestIso9001Surveillance(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.models = Path(self.tmp.name) / "models"
        self.models.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def _statuses(self, evidence: dict) -> dict[str, str]:
        return {c["id"]: c["status"] for c in evidence["checks"]}

    def test_code_controls_pass_but_records_unmeasured(self):
        (self.models / "qms.py").write_text(GOOD_MODELS, encoding="utf-8")
        evidence = M.audit_qms_estate(self.models)
        statuses = self._statuses(evidence)
        self.assertEqual(statuses["M23_QMS_MODELS_PRESENT"], M.PASS)
        self.assertEqual(statuses["CAPA_CLOSE_REQUIRES_VERIFICATION"], M.PASS)
        self.assertEqual(statuses["CON11_ZERO_MAJOR_SYSTEM_NCRS"], M.UNMEASURED)
        self.assertEqual(statuses["SURVEILLANCE_CERTIFICATE"], M.UNMEASURED)
        self.assertEqual(evidence["surveillance_certificate"]["status"], M.UNMEASURED)
        self.assertEqual(evidence["verdict"], M.INCOMPLETE)
        self.assertEqual(M.exit_code(evidence["verdict"]), 2)

    def test_unguarded_capa_close_fails(self):
        (self.models / "qms.py").write_text(UNGUARDED_CAPA, encoding="utf-8")
        evidence = M.audit_qms_estate(self.models)
        self.assertEqual(self._statuses(evidence)["CAPA_CLOSE_REQUIRES_VERIFICATION"], M.FAIL)
        self.assertEqual(evidence["verdict"], M.FAIL)
        self.assertEqual(M.exit_code(evidence["verdict"]), 1)

    def test_missing_models_dir_fails(self):
        evidence = M.audit_qms_estate(self.models / "absent")
        statuses = self._statuses(evidence)
        self.assertEqual(statuses["M23_QMS_MODELS_PRESENT"], M.FAIL)
        self.assertEqual(statuses["CAPA_CLOSE_REQUIRES_VERIFICATION"], M.FAIL)
        self.assertEqual(evidence["verdict"], M.FAIL)

    def test_real_addon_is_scanned(self):
        evidence = M.audit_qms_estate()
        self.assertEqual(self._statuses(evidence)["M23_QMS_MODELS_PRESENT"], M.PASS)
        self.assertNotEqual(evidence["verdict"], M.PASS)

    def test_main_writes_computed_verdict_without_pass_literals(self):
        (self.models / "qms.py").write_text(GOOD_MODELS, encoding="utf-8")
        evidence_dir, docs = Path(self.tmp.name) / "evidence", Path(self.tmp.name) / "docs"
        saved = (M.EVIDENCE_DIR, M.DOCS_DIR)
        defaults = M.audit_qms_estate.__defaults__
        M.EVIDENCE_DIR, M.DOCS_DIR = evidence_dir, docs
        M.audit_qms_estate.__defaults__ = (self.models,)
        try:
            code = M.main()
        finally:
            M.EVIDENCE_DIR, M.DOCS_DIR = saved
            M.audit_qms_estate.__defaults__ = defaults
        self.assertEqual(code, 2)
        out = (evidence_dir / "r11-m03-iso9001-surveillance-result.json").read_text(
            encoding="utf-8"
        )
        self.assertEqual(json.loads(out)["verdict"], M.INCOMPLETE)
        self.assertNotIn("MAINTAINED", out)
        md = (docs / "r11-m03-iso9001-surveillance-report.md").read_text(encoding="utf-8")
        self.assertNotIn("**PASS**", md)
        self.assertNotIn("UNCONDITIONALLY", md)


if __name__ == "__main__":
    unittest.main()
