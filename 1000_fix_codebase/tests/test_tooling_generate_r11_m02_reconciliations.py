"""GV-009: generate_r11_m02_reconciliations.py never declares a legacy source reconciled or
approved (both UNMEASURED off-estate), measures the rehearsal reconciliation from the
extracts / manifest / load report / database it is given, and turns drift, count or
checksum mismatches into FAIL. No network, database or real evidence file is touched."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "scripts" / "generate_r11_m02_reconciliations.py"


def _load():
    spec = importlib.util.spec_from_file_location("generate_r11_m02_reconciliations_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


mod = _load()

BRANCHES = [
    {"code": "HQ", "legacy_reference": "BR:PILOT_2026:HQ"},
    {"code": "PC01", "legacy_reference": "BR:PILOT_2026:PC01"},
]
CUSTOMERS = [
    {"source_id": "WP-1", "legacy_reference": "CUST:WP_STORE:1"},
    {"source_id": "WP-2", "legacy_reference": "CUST:WP_STORE:2"},
    {"source_id": "WP-3", "legacy_reference": "CUST:WP_STORE:3"},
]


class FakeCursor:
    def __init__(self, present: dict[str, set[str]]):
        self.present = present
        self.result = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql, params=None):
        assert sql.startswith("SELECT"), sql
        table = sql.split(" FROM ")[1].split()[0]
        refs = set(params[0])
        self.result = (len(refs & self.present.get(table, set())),)

    def fetchone(self):
        return self.result


class FakeConn:
    def __init__(self, present):
        self.present = present
        self.closed = False

    def cursor(self):
        return FakeCursor(self.present)

    def close(self):
        self.closed = True


def good_db():
    return {
        "fix_branch": {"BR:PILOT_2026:HQ", "BR:PILOT_2026:PC01"},
        "res_partner": {"CUST:WP_STORE:1", "CUST:WP_STORE:2"},
    }


def connector_for(present):
    conn = FakeConn(present)
    return (lambda: (conn, "127.0.0.1:5433/fix_migration")), conn


def unreachable():
    raise RuntimeError("connection refused")


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        self.write_fixture()

    def write_fixture(self, *, control_override=None, rejection_reason="duplicate phone"):
        (self.dir / "branches_extract.json").write_bytes(json.dumps(BRANCHES).encode())
        (self.dir / "customers_extract.json").write_bytes(json.dumps(CUSTOMERS).encode())
        control = {"branches": 2, "customers": 3}
        control.update(control_override or {})
        manifest = {
            "run": "RUN-1",
            "control_totals": control,
            "checksums": {
                "branches": mod.compute_sha256(self.dir / "branches_extract.json"),
                "customers": mod.compute_sha256(self.dir / "customers_extract.json"),
            },
            "extract_files": {
                "branches": "branches_extract.json",
                "customers": "customers_extract.json",
            },
        }
        loaded = {
            "run": "RUN-1",
            "loaded_totals": {"branches": 2, "customers": 3},
            "accepted_records": {"branches": 2, "customers": 2},
            "quarantined_records": {"branches": 0, "customers": 1},
            "rejections": {
                "customers": [{"legacy_reference": "CUST:WP_STORE:3", "reason": rejection_reason}]
            },
        }
        (self.dir / mod.MANIFEST_NAME).write_bytes(json.dumps(manifest).encode())
        (self.dir / mod.LOADED_NAME).write_bytes(json.dumps(loaded).encode())

    def entity(self, ev, name):
        return next(e for e in ev["rehearsal_reconciliation"]["entities"] if e["entity"] == name)


class TestReconciliationRegister(Base):
    def test_sources_unmeasured_rehearsal_measured_verdict_incomplete(self):
        connector, conn = connector_for(good_db())
        ev = mod.build_evidence(self.dir, connector)
        self.assertEqual(len(ev["sources"]), 48)
        for s in ev["sources"]:
            self.assertEqual(s["reconciliation_status"], "UNMEASURED")
            self.assertEqual(s["approval_status"], "UNMEASURED")
            self.assertIsNone(s["legacy_record_count"])
            self.assertIsNone(s["variance_percentage"])
        self.assertEqual(ev["total_sources_approved"], 0)
        self.assertEqual(ev["total_sources_evaluated"], 0)
        self.assertIsNone(ev["estate_variance_rate"])
        branches = self.entity(ev, "branches")
        self.assertEqual(branches["status"], "PASS", branches["checks"])
        self.assertEqual(branches["live_accepted_records"], 2)
        customers = self.entity(ev, "customers")
        self.assertEqual(customers["checks"]["live_drift"]["status"], "PASS")
        self.assertEqual(customers["checks"]["quarantine_signoff"]["status"], "UNMEASURED")
        self.assertEqual(customers["quarantine_percentage"], 33.33)
        self.assertEqual(ev["rehearsal_reconciliation"]["unaccounted_variance_rate"], "0.00%")
        self.assertEqual(ev["verdict"], "INCOMPLETE")
        self.assertEqual(mod.exit_code_for(ev["verdict"]), 2)
        self.assertTrue(conn.closed)

    def test_checksum_drift_fails(self):
        (self.dir / "branches_extract.json").write_bytes(json.dumps(BRANCHES[::-1]).encode())
        ev = mod.build_evidence(self.dir, connector_for(good_db())[0])
        self.assertEqual(
            self.entity(ev, "branches")["checks"]["extract_checksum"]["status"], "FAIL"
        )
        self.assertEqual(ev["verdict"], "FAIL")
        self.assertEqual(mod.exit_code_for(ev["verdict"]), 1)

    def test_control_total_mismatch_fails(self):
        self.write_fixture(control_override={"branches": 5})
        ev = mod.build_evidence(self.dir, connector_for(good_db())[0])
        checks = self.entity(ev, "branches")["checks"]
        self.assertEqual(checks["extract_count"]["status"], "FAIL")
        self.assertEqual(checks["load_accounted"]["status"], "FAIL")
        self.assertEqual(ev["verdict"], "FAIL")

    def test_live_drift_fails(self):
        db = good_db()
        db["fix_branch"] = {"BR:PILOT_2026:HQ"}
        ev = mod.build_evidence(self.dir, connector_for(db)[0])
        drift = self.entity(ev, "branches")["checks"]["live_drift"]
        self.assertEqual(drift["status"], "FAIL")
        self.assertIn("DRIFT", drift["detail"])
        self.assertEqual(ev["verdict"], "FAIL")

    def test_unexplained_quarantine_fails(self):
        self.write_fixture(rejection_reason="")
        ev = mod.build_evidence(self.dir, connector_for(good_db())[0])
        checks = self.entity(ev, "customers")["checks"]
        self.assertEqual(checks["quarantine_explained"]["status"], "FAIL")
        self.assertEqual(ev["verdict"], "FAIL")

    def test_unreachable_database_is_unmeasured_never_pass(self):
        ev = mod.build_evidence(self.dir, unreachable)
        for name in ("branches", "customers"):
            drift = self.entity(ev, name)["checks"]["live_drift"]
            self.assertEqual(drift["status"], "UNMEASURED")
            self.assertIn("unreachable", drift["detail"])
        self.assertIsNone(ev["rehearsal_reconciliation"]["target_database"])
        self.assertEqual(ev["verdict"], "INCOMPLETE")

    def test_missing_manifest_is_unmeasured(self):
        (self.dir / mod.MANIFEST_NAME).unlink()
        ev = mod.build_evidence(self.dir, unreachable)
        self.assertEqual(ev["rehearsal_reconciliation"]["status"], "INCOMPLETE")
        self.assertNotEqual(ev["verdict"], "PASS")

    def test_derive_verdict(self):
        self.assertEqual(mod.derive_verdict([]), "INCOMPLETE")
        self.assertEqual(mod.derive_verdict(["PASS", "UNMEASURED"]), "INCOMPLETE")
        self.assertEqual(mod.derive_verdict(["PASS", "FAIL", "UNMEASURED"]), "FAIL")
        self.assertEqual(mod.derive_verdict(["PASS"]), "PASS")


class TestOutputs(Base):
    def test_main_writes_only_temp_outputs_with_computed_statuses(self):
        out = Path(self.tmp.name) / "out"
        originals = (mod.EVIDENCE_DIR, mod.DOCS_DIR, mod.open_rehearsal_db)
        mod.EVIDENCE_DIR, mod.DOCS_DIR = out / "evidence", out / "docs"
        mod.open_rehearsal_db = lambda dsn=None: unreachable()
        try:
            code = mod.main(["--extracts-dir", str(self.dir)])
        finally:
            mod.EVIDENCE_DIR, mod.DOCS_DIR, mod.open_rehearsal_db = originals
        self.assertEqual(code, 2)
        ev = json.loads((out / "evidence" / mod.EVIDENCE_NAME).read_text(encoding="utf-8"))
        self.assertEqual(ev["overall_status"], "INCOMPLETE")
        md = (out / "docs" / mod.MD_NAME).read_text(encoding="utf-8")
        self.assertIn("`UNMEASURED`", md)
        self.assertNotIn("**APPROVED**", md)
        self.assertNotIn("hereby certify", md)
        self.assertNotIn(b"\r\n", (out / "docs" / mod.MD_NAME).read_bytes())


if __name__ == "__main__":
    unittest.main()
