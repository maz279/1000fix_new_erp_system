"""GV-009: verify_legacy_reference_lookup.py looks up and times every accepted legacy
reference on the database it is given; a missing / ambiguous / slow lookup or a missing
legacy_reference index is FAIL; service orders (no extract), production and an unreachable
database are UNMEASURED, so the verdict is never PASS on this tool's word alone. No network,
database or real evidence file is touched."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "scripts" / "verify_legacy_reference_lookup.py"


def _load():
    spec = importlib.util.spec_from_file_location("verify_legacy_reference_lookup_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


mod = _load()

EXTRACTS = {
    "devices_extract.json": [
        {"serial_number": "SN-1", "legacy_reference": "DEV:SN-1"},
        {"serial_number": "SN-2", "legacy_reference": "DEV:SN-2"},
        {"serial_number": "SN-1", "legacy_reference": "DEV:SN-1"},  # duplicate, quarantined
    ],
    "customers_extract.json": [
        {"legacy_reference": "CUST:1"},
        {"legacy_reference": "CUST:2"},  # quarantined
    ],
    "employees_extract.json": [{"legacy_reference": "EMP:1"}],
    "branches_extract.json": [{"legacy_reference": "BR:HQ"}],
}
LOADED = {
    "run": "RUN-1",
    "rejections": {
        "devices": [{"legacy_reference": "DEV:SN-1", "reason": "duplicate serial"}],
        "customers": [{"legacy_reference": "CUST:2", "reason": "duplicate phone"}],
    },
}


def good_tables():
    return {
        "fix_device": [(1, "DEV:SN-1"), (2, "DEV:SN-2")],
        "res_partner": [(10, "CUST:1")],
        "hr_employee": [(20, "EMP:1")],
        "fix_branch": [(30, "BR:HQ")],
        "fix_service_order": [],
    }


class FakeCursor:
    def __init__(self, db):
        self.db = db
        self.rows = []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql, params=None):
        if "pg_indexes" in sql:
            self.rows = [(1 if params[0] in self.db.indexed else 0,)]
            return
        table = sql.split(" FROM ")[1].split()[0]
        rows = self.db.tables.get(table, [])
        if "IS NOT NULL" in sql:
            self.rows = [(len(rows),)]
        else:
            self.rows = [(rid,) for rid, ref in rows if ref == params[0]]

    def fetchall(self):
        return self.rows

    def fetchone(self):
        return self.rows[0]


class FakeDb:
    def __init__(self, tables=None, indexed=None):
        self.tables = tables if tables is not None else good_tables()
        self.indexed = indexed if indexed is not None else set(self.tables)
        self.closed = False

    def cursor(self):
        return FakeCursor(self)

    def close(self):
        self.closed = True


def unreachable():
    raise RuntimeError("connection refused")


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        for name, rows in EXTRACTS.items():
            (self.dir / name).write_bytes(json.dumps(rows).encode())
        (self.dir / mod.LOADED_NAME).write_bytes(json.dumps(LOADED).encode())

    def run_with(self, db):
        return mod.build_evidence(self.dir, lambda: (db, "127.0.0.1:5433/fix_migration"))

    @staticmethod
    def domain(ev, name):
        return next(d for d in ev["domains"] if d["domain_model"] == name)


class TestLegacyLookup(Base):
    def test_all_lookups_resolve_but_verdict_incomplete(self):
        db = FakeDb()
        ev = self.run_with(db)
        self.assertEqual(ev["total_sample_lookups_tested"], 5)
        self.assertEqual(ev["total_successful_resolutions"], 5)
        self.assertEqual(ev["resolution_success_rate"], "100.0%")
        for name in ("fix.device", "res.partner", "hr.employee", "fix.branch"):
            self.assertEqual(self.domain(ev, name)["status"], "PASS", self.domain(ev, name))
        so = self.domain(ev, "fix.service.order")
        self.assertEqual(so["checks"]["coverage"]["status"], "UNMEASURED")
        self.assertEqual(ev["production_lookup_after_retirement"]["status"], "UNMEASURED")
        self.assertEqual(ev["verdict"], "INCOMPLETE")
        self.assertEqual(mod.exit_code_for(ev["verdict"]), 2)
        self.assertEqual(ev["performance_metrics"]["sla_conformance"], "PASS")
        self.assertTrue(
            all(lk["lookup_duration_ms"] is not None for lk in ev["sample_verifications"])
        )
        self.assertTrue(db.closed)

    def test_expected_refs_counts_quarantined_duplicates_per_occurrence(self):
        refs = mod.expected_refs(EXTRACTS["devices_extract.json"], LOADED["rejections"]["devices"])
        self.assertEqual(refs, ["DEV:SN-1", "DEV:SN-2"])
        refs = mod.expected_refs(
            EXTRACTS["customers_extract.json"], LOADED["rejections"]["customers"]
        )
        self.assertEqual(refs, ["CUST:1"])

    def test_missing_record_fails(self):
        tables = good_tables()
        tables["fix_device"] = [(1, "DEV:SN-1")]
        ev = self.run_with(FakeDb(tables))
        coverage = self.domain(ev, "fix.device")["checks"]["coverage"]
        self.assertEqual(coverage["status"], "FAIL")
        self.assertIn("DEV:SN-2 (LOOKUP_NOT_FOUND)", coverage["detail"])
        self.assertEqual(ev["resolution_success_rate"], "80.0%")
        self.assertEqual(ev["verdict"], "FAIL")
        self.assertEqual(mod.exit_code_for(ev["verdict"]), 1)

    def test_ambiguous_reference_fails(self):
        tables = good_tables()
        tables["hr_employee"] = [(20, "EMP:1"), (21, "EMP:1")]
        ev = self.run_with(FakeDb(tables))
        self.assertEqual(self.domain(ev, "hr.employee")["checks"]["coverage"]["status"], "FAIL")
        self.assertEqual(ev["verdict"], "FAIL")

    def test_missing_index_fails(self):
        db = FakeDb(indexed={"fix_device", "res_partner", "hr_employee", "fix_service_order"})
        ev = self.run_with(db)
        check = self.domain(ev, "fix.branch")["checks"]["legacy_reference_indexed"]
        self.assertEqual(check["status"], "FAIL")
        self.assertEqual(ev["verdict"], "FAIL")

    def test_slow_lookup_fails_sla(self):
        class SlowClock:
            def __init__(self):
                self.t = 0.0

            def perf_counter(self):
                self.t += 0.1  # 100 ms between start and stop
                return self.t

        original = mod.time
        mod.time = SlowClock()
        try:
            ev = self.run_with(FakeDb())
        finally:
            mod.time = original
        self.assertEqual(self.domain(ev, "fix.device")["checks"]["latency_sla"]["status"], "FAIL")
        self.assertEqual(ev["performance_metrics"]["sla_conformance"], "FAIL")
        self.assertEqual(ev["verdict"], "FAIL")

    def test_unreachable_database_is_unmeasured_never_pass(self):
        ev = mod.build_evidence(self.dir, unreachable)
        self.assertEqual(ev["total_sample_lookups_tested"], 0)
        self.assertIsNone(ev["resolution_success_rate"])
        self.assertIsNone(ev["performance_metrics"]["average_lookup_latency_ms"])
        for d in ev["domains"]:
            self.assertNotEqual(d["status"], "PASS")
            self.assertEqual(d["checks"]["legacy_reference_indexed"]["status"], "UNMEASURED")
        self.assertEqual(ev["verified_domains"], [])
        self.assertEqual(ev["verdict"], "INCOMPLETE")

    def test_missing_load_report_is_unmeasured(self):
        (self.dir / mod.LOADED_NAME).unlink()
        ev = self.run_with(FakeDb())
        self.assertEqual(
            self.domain(ev, "fix.device")["checks"]["coverage"]["status"], "UNMEASURED"
        )
        self.assertNotEqual(ev["verdict"], "PASS")


class TestOutputs(Base):
    def test_main_writes_only_temp_outputs(self):
        out = self.dir / "out"
        originals = (mod.EVIDENCE_DIR, mod.DOCS_DIR, mod.open_rehearsal_db)
        mod.EVIDENCE_DIR, mod.DOCS_DIR = out / "evidence", out / "docs"
        mod.open_rehearsal_db = lambda dsn=None: (FakeDb(), "fake")
        try:
            code = mod.main(["--extracts-dir", str(self.dir)])
        finally:
            mod.EVIDENCE_DIR, mod.DOCS_DIR, mod.open_rehearsal_db = originals
        self.assertEqual(code, 2)
        ev = json.loads((out / "evidence" / mod.EVIDENCE_NAME).read_text(encoding="utf-8"))
        self.assertEqual(ev["overall_status"], "INCOMPLETE")
        md = (out / "docs" / mod.MD_NAME).read_text(encoding="utf-8")
        self.assertIn("`INCOMPLETE`", md)
        self.assertNotIn("VERIFIED_PERMANENT_SURVIVAL", md)


if __name__ == "__main__":
    unittest.main()
