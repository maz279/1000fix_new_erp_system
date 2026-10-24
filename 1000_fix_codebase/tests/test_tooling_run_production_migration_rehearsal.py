"""GV-009: run_production_migration_rehearsal.py measures the MG-005 rehearsal
(extract counts + sha256 vs the manifest, control totals vs the load report,
read-only live counts, plaintext-residency scan) and never reports PASS while
production volume, MG-007 rollback or the MG-004 signature are unmeasured."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "scripts" / "run_production_migration_rehearsal.py"


def _load():
    spec = importlib.util.spec_from_file_location("run_prod_mig_rehearsal_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


M = _load()

CUSTOMERS = [
    {"legacy_reference": f"CUST:WP_STORE:{i}", "nid": f"19900000000{i:02d}"} for i in range(3)
]
BRANCHES = [{"legacy_reference": f"BR:PILOT_2026:PC{i}"} for i in range(2)]


def build_extracts(root: Path, loaded_customers: int = 3) -> Path:
    """A consistent Wave-1-shaped extract set: manifest, two extracts, load report."""
    extracts = root / "extracts"
    extracts.mkdir()
    files = {"customers": "customers_extract.json", "branches": "branches_extract.json"}
    for name, records in (("customers", CUSTOMERS), ("branches", BRANCHES)):
        (extracts / files[name]).write_bytes(json.dumps(records).encode("utf-8"))
    manifest = {
        "run": "UT_RUN",
        "control_totals": {"customers": 3, "branches": 2},
        "checksums": {k: M.compute_sha256(extracts / v) for k, v in files.items()},
        "extract_files": files,
    }
    (extracts / M.MANIFEST_NAME).write_text(json.dumps(manifest), encoding="utf-8")
    loaded = {
        "run": "UT_RUN",
        "loaded_totals": {"customers": loaded_customers, "branches": 2},
        "accepted_records": {"customers": loaded_customers - 1, "branches": 2},
        "quarantined_records": {"customers": 1, "branches": 0},
    }
    (extracts / M.LOADED_NAME).write_text(json.dumps(loaded), encoding="utf-8")
    return extracts


class FakeCursor:
    def __init__(self, live: dict[str, int], leak_hits: int):
        self.live = live
        self.leak_hits = leak_hits
        self.result: tuple | list = ()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, query, params=None):
        text = query if isinstance(query, str) else ""
        if "information_schema.columns" in text:
            self.result = [("res_partner", "name"), ("res_partner", "comment")]
        elif "CUST:WP_STORE:" in text:
            self.result = (self.live.get("customers", 0),)
        elif "BR:PILOT_2026:" in text:
            self.result = (self.live.get("branches", 0),)
        else:  # the composed plaintext-scan query
            self.result = (self.leak_hits,)

    def fetchone(self):
        return self.result

    def fetchall(self):
        return self.result


class FakeConn:
    def __init__(self, live: dict[str, int], leak_hits: int = 0):
        self.live = live
        self.leak_hits = leak_hits

    def cursor(self):
        return FakeCursor(self.live, self.leak_hits)

    def close(self):
        pass


def unreachable():
    raise OSError("connection refused")


def fake_db(live: dict[str, int], leak_hits: int = 0):
    return lambda: (FakeConn(live, leak_hits), "fake:5433/fix_migration")


class TestRehearsalVerdict(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.evidence = self.root / "evidence"

    def tearDown(self):
        self.tmp.cleanup()

    def _checks(self, evidence: dict) -> dict[str, str]:
        return {c["id"]: c["status"] for c in evidence["checks"]}

    def test_unreachable_db_is_unmeasured_never_pass(self):
        ev = M.run(build_extracts(self.root), self.evidence, unreachable)
        checks = self._checks(ev)
        self.assertEqual(ev["status"], "INCOMPLETE")
        self.assertFalse(ev["gp_11_discharged"])
        self.assertEqual(M.exit_code(ev["status"]), 2)
        self.assertEqual(checks["MIG02_LIVE_COUNTS"], "UNMEASURED")
        self.assertEqual(checks["MIG06_RESIDENCY"], "UNMEASURED")
        self.assertEqual(checks["MIG02_EXTRACT_CUSTOMERS"], "PASS")
        self.assertEqual(checks["MIG02_CONTROL_TOTALS"], "PASS")
        written = json.loads((self.evidence / M.EVIDENCE_NAME).read_text(encoding="utf-8"))
        self.assertEqual(written["status"], "INCOMPLETE")
        signoff = json.loads((self.evidence / M.SIGNOFF_NAME).read_text(encoding="utf-8"))
        self.assertEqual(signoff["verdict"], "UNMEASURED")
        self.assertIsNone(signoff["signatory"])
        self.assertNotIn("SIGN-OFF", json.dumps(signoff))

    def test_consistent_db_still_not_pass_without_production_and_signoff(self):
        ev = M.run(
            build_extracts(self.root), self.evidence, fake_db({"customers": 2, "branches": 2})
        )
        checks = self._checks(ev)
        self.assertEqual(checks["MIG02_LIVE_COUNTS"], "PASS")
        self.assertEqual(checks["MIG06_RESIDENCY"], "PASS")
        for unobservable in ("MG005_PRODUCTION_VOLUME", "MG007_ROLLBACK", "MG004_BUSINESS_SIGNOFF"):
            self.assertEqual(checks[unobservable], "UNMEASURED")
        self.assertEqual(ev["status"], "INCOMPLETE")

    def test_tampered_extract_fails(self):
        extracts = build_extracts(self.root)
        (extracts / "customers_extract.json").write_bytes(json.dumps(CUSTOMERS[:2]).encode())
        ev = M.run(extracts, self.evidence, unreachable)
        self.assertEqual(self._checks(ev)["MIG02_EXTRACT_CUSTOMERS"], "FAIL")
        self.assertEqual(ev["status"], "FAIL")
        self.assertEqual(M.exit_code(ev["status"]), 1)

    def test_control_total_mismatch_fails(self):
        ev = M.run(build_extracts(self.root, loaded_customers=4), self.evidence, unreachable)
        self.assertEqual(self._checks(ev)["MIG02_CONTROL_TOTALS"], "FAIL")
        self.assertEqual(ev["status"], "FAIL")

    def test_live_count_drift_fails(self):
        ev = M.run(
            build_extracts(self.root), self.evidence, fake_db({"customers": 1, "branches": 2})
        )
        self.assertEqual(self._checks(ev)["MIG02_LIVE_COUNTS"], "FAIL")
        self.assertEqual(ev["status"], "FAIL")

    def test_plaintext_classified_value_fails_residency(self):
        live = {"customers": 2, "branches": 2}
        ev = M.run(build_extracts(self.root), self.evidence, fake_db(live, leak_hits=1))
        residency = next(c for c in ev["checks"] if c["id"] == "MIG06_RESIDENCY")
        self.assertEqual(residency["status"], "FAIL")
        self.assertEqual(
            residency["plaintext_leaks"], {"res_partner.name": 1, "res_partner.comment": 1}
        )
        self.assertEqual(ev["status"], "FAIL")

    def test_missing_manifest_fails(self):
        extracts = build_extracts(self.root)
        (extracts / M.MANIFEST_NAME).unlink()
        ev = M.run(extracts, self.evidence, unreachable)
        self.assertEqual(self._checks(ev)["MIG02_MANIFEST"], "FAIL")
        self.assertEqual(ev["status"], "FAIL")

    def test_overall_verdict_rules(self):
        def c(status):
            return {"status": status}

        self.assertEqual(M.overall_verdict([c("PASS"), c("PASS")]), "PASS")
        self.assertEqual(M.overall_verdict([c("PASS"), c("UNMEASURED")]), "INCOMPLETE")
        self.assertEqual(M.overall_verdict([c("UNMEASURED"), c("FAIL")]), "FAIL")
        self.assertEqual(M.overall_verdict([]), "UNMEASURED")


if __name__ == "__main__":
    unittest.main()
