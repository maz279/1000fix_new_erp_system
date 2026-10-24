"""GV-009: execute_legacy_decommission.py is measure-only; every D-ladder state is derived
from checks (upstream T01 / T04 evidence counted only when exactly PASS); negative
connection tests, purge / rotation / review evidence, DPO countersigns and the estate shadow
scan are UNMEASURED, so no source reaches D7 and the verdict is never PASS on its word; an
upstream FAIL, a register disagreement or a live reference to a retired endpoint is FAIL.
Only temp files are touched."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "scripts" / "execute_legacy_decommission.py"


def _load():
    spec = importlib.util.spec_from_file_location("execute_legacy_decommission_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


mod = _load()


def t01_evidence(status="PASS", overrides=None):
    rows = []
    for src in mod.SOURCES_DATA:
        rows.append(
            {
                "source_id": src["id"],
                "source_name": src["name"],
                "approval_status": (overrides or {}).get(src["id"], status),
            }
        )
    return {"sources": rows}


def t04_evidence(status="PASS"):
    retirable = [s["id"] for s in mod.SOURCES_DATA if s["disp"] == "R"]
    return {
        "archive_classes": [
            {
                "archive_class_id": "ARCH-T",
                "covered_sources": retirable,
                "verification_status": status,
            }
        ]
    }


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        self.evidence = self.root / "evidence"
        self.evidence.mkdir()
        originals = (mod.EVIDENCE_DIR, mod.DOCS_DIR, mod.REPO_ROOT)
        mod.EVIDENCE_DIR, mod.DOCS_DIR, mod.REPO_ROOT = self.evidence, self.root / "docs", self.root
        self.addCleanup(self._restore, originals)
        cfg = self.root / "infra"
        cfg.mkdir()
        (cfg / "app.yaml").write_bytes(b"db_host: 127.0.0.1\n")

    @staticmethod
    def _restore(originals):
        mod.EVIDENCE_DIR, mod.DOCS_DIR, mod.REPO_ROOT = originals

    def write(self, name, data):
        (self.evidence / name).write_bytes(json.dumps(data).encode())

    @staticmethod
    def source(ev, sid):
        return next(s for s in ev["sources"] if s["source_id"] == sid)


class TestDecommissionRegister(Base):
    def test_upstream_pass_still_no_d7_and_verdict_incomplete(self):
        self.write(mod.T01_EVIDENCE, t01_evidence())
        self.write(mod.T04_EVIDENCE, t04_evidence())
        ev = mod.build_evidence()
        s01 = self.source(ev, "SRC-01")
        self.assertEqual(s01["checks"]["mig08_reconciliation_signoff"]["status"], "PASS")
        self.assertEqual(s01["checks"]["archive_restorable"]["status"], "PASS")
        self.assertEqual(s01["checks"]["negative_connection_test"]["status"], "UNMEASURED")
        self.assertEqual(s01["checks"]["dpo_countersign"]["status"], "UNMEASURED")
        self.assertEqual(s01["state"], "UNMEASURED")
        ds = ev["disposition_summary"]
        self.assertEqual(ds["retirable_sources_decommissioned_d7"], 0)
        self.assertEqual(ds["total_estate_accounted_for"], 48)
        self.assertFalse(ds["restated_gv001_closure_criteria_met"])
        self.assertEqual(ev["declared_dispositions"], {"K": 4, "N": 11, "P": 1, "R": 32})
        self.assertEqual(ev["financial_summary"]["total_annual_run_cost_released_bdt"], 0)
        self.assertEqual(ev["compliance_summary"]["negative_connection_tests_passed"], 0)
        self.assertIsNone(ev["compliance_summary"]["shadow_system_scan_findings"])
        checks = ev["estate_checks"]
        self.assertEqual(checks["register_complete"]["status"], "PASS")
        self.assertEqual(checks["register_agrees_with_t01"]["status"], "PASS")
        self.assertEqual(checks["codebase_legacy_endpoint_references"]["status"], "PASS")
        self.assertEqual(checks["shadow_system_scan"]["status"], "UNMEASURED")
        self.assertEqual(ev["verdict"], "INCOMPLETE")
        self.assertEqual(mod.exit_code_for(ev["verdict"]), 2)

    def test_upstream_fail_blocks_source_and_fails_verdict(self):
        self.write(mod.T01_EVIDENCE, t01_evidence(overrides={"SRC-05": "FAIL"}))
        self.write(mod.T04_EVIDENCE, t04_evidence())
        ev = mod.build_evidence()
        self.assertEqual(self.source(ev, "SRC-05")["state"], "BLOCKED")
        self.assertEqual(ev["disposition_summary"]["sources_blocked"], 1)
        self.assertEqual(ev["verdict"], "FAIL")
        self.assertEqual(mod.exit_code_for(ev["verdict"]), 1)

    def test_declared_upstream_strings_are_not_measurements(self):
        self.write(mod.T01_EVIDENCE, t01_evidence(status="APPROVED_FOR_DECOMMISSION"))
        self.write(mod.T04_EVIDENCE, t04_evidence(status="RESTORE_VERIFIED_PASS"))
        ev = mod.build_evidence()
        s01 = self.source(ev, "SRC-01")
        self.assertEqual(s01["checks"]["mig08_reconciliation_signoff"]["status"], "UNMEASURED")
        self.assertEqual(s01["checks"]["archive_restorable"]["status"], "UNMEASURED")

    def test_missing_upstream_evidence_is_unmeasured(self):
        ev = mod.build_evidence()
        s01 = self.source(ev, "SRC-01")
        self.assertIn("not found", s01["checks"]["mig08_reconciliation_signoff"]["detail"])
        self.assertEqual(s01["checks"]["archive_restorable"]["status"], "UNMEASURED")
        self.assertEqual(ev["estate_checks"]["register_agrees_with_t01"]["status"], "UNMEASURED")
        self.assertEqual(ev["verdict"], "INCOMPLETE")

    def test_uncovered_source_fails_archive_check(self):
        self.write(mod.T01_EVIDENCE, t01_evidence())
        self.write(
            mod.T04_EVIDENCE,
            {"archive_classes": [{"covered_sources": ["SRC-01"], "verification_status": "PASS"}]},
        )
        ev = mod.build_evidence()
        self.assertEqual(
            self.source(ev, "SRC-02")["checks"]["archive_restorable"]["status"], "FAIL"
        )
        self.assertEqual(ev["verdict"], "FAIL")

    def test_register_disagreement_with_t01_fails(self):
        data = t01_evidence()
        data["sources"][37]["source_name"] = "Something Else Entirely"
        self.write(mod.T01_EVIDENCE, data)
        self.write(mod.T04_EVIDENCE, t04_evidence())
        ev = mod.build_evidence()
        check = ev["estate_checks"]["register_agrees_with_t01"]
        self.assertEqual(check["status"], "FAIL")
        self.assertIn("SRC-38", check["detail"])
        self.assertEqual(ev["verdict"], "FAIL")

    def test_live_reference_to_retired_endpoint_fails(self):
        (self.root / "infra" / "legacy.conf").write_bytes(b"url = http://station.1000fix.com/\n")
        ev = mod.build_evidence()
        check = ev["estate_checks"]["codebase_legacy_endpoint_references"]
        self.assertEqual(check["status"], "FAIL")
        self.assertIn("infra/legacy.conf (SRC-01)", check["detail"])
        self.assertEqual(ev["compliance_summary"]["codebase_legacy_endpoint_references"], 1)
        self.assertEqual(ev["verdict"], "FAIL")

    def test_nothing_to_scan_is_unmeasured(self):
        check, findings = mod.scan_codebase(("no-such-dir",))
        self.assertEqual(check["status"], "UNMEASURED")
        self.assertEqual(findings, [])

    def test_incomplete_register_fails(self):
        original = mod.SOURCES_DATA
        mod.SOURCES_DATA = original[:-1]
        try:
            check = mod.register_completeness()
        finally:
            mod.SOURCES_DATA = original
        self.assertEqual(check["status"], "FAIL")
        self.assertIn("SRC-48", check["detail"])


class TestOutputs(Base):
    def test_main_writes_only_temp_outputs(self):
        self.assertEqual(mod.main([]), 2)
        ev = json.loads((self.evidence / mod.EVIDENCE_NAME).read_text(encoding="utf-8"))
        self.assertEqual(ev["overall_status"], "INCOMPLETE")
        self.assertTrue(ev["mode"].startswith("MEASURE_ONLY"))
        md = (self.root / "docs" / mod.MD_NAME).read_text(encoding="utf-8")
        self.assertNotIn("CERT-DCM", md)
        self.assertIn("No legacy source is certified decommissioned", md)


if __name__ == "__main__":
    unittest.main()
