"""GV-009: run_final_cutover_rehearsal.py computes the R11-M01-T02 verdict from
measured extract checksums / control totals; financial parity, full-volume
staging and the business pre-signature are UNMEASURED, so it is never PASS and
never writes an "UNCONDITIONAL AUTHORIZATION"."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "scripts" / "run_final_cutover_rehearsal.py"


def _load():
    spec = importlib.util.spec_from_file_location("run_final_cutover_rehearsal_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


M = _load()
RECORDS = [{"legacy_reference": f"BR:PILOT_2026:PC{i}"} for i in range(3)]


def build_extracts(root: Path) -> Path:
    extracts = root / "extracts"
    extracts.mkdir()
    (extracts / "branches_extract.json").write_bytes(json.dumps(RECORDS).encode("utf-8"))
    manifest = {
        "run": "UT_FINAL",
        "control_totals": {"branches": 3},
        "checksums": {"branches": M.rehearsal.compute_sha256(extracts / "branches_extract.json")},
        "extract_files": {"branches": "branches_extract.json"},
    }
    (extracts / "control-totals.json").write_text(json.dumps(manifest), encoding="utf-8")
    loaded = {
        "run": "UT_FINAL",
        "loaded_totals": {"branches": 3},
        "accepted_records": {"branches": 3},
        "quarantined_records": {"branches": 0},
    }
    (extracts / "loaded-counts.json").write_text(json.dumps(loaded), encoding="utf-8")
    return extracts


def unreachable():
    raise OSError("connection refused")


class TestFinalRehearsalVerdict(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.evidence = self.root / "evidence"

    def tearDown(self):
        self.tmp.cleanup()

    def _statuses(self, record: dict) -> dict[str, str]:
        return {c["id"]: c["status"] for c in record["checks"]}

    def test_unreachable_infra_is_incomplete_and_unauthorised(self):
        extracts = build_extracts(self.root)
        record, presign = M.run(extracts, self.evidence, unreachable)
        statuses = self._statuses(record)
        self.assertEqual(record["status"], "INCOMPLETE")
        self.assertEqual(M.rehearsal.exit_code(record["status"]), 2)
        self.assertEqual(statuses["MIG02_EXTRACT_BRANCHES"], "PASS")
        self.assertEqual(statuses["MIG02_LIVE_COUNTS"], "UNMEASURED")
        self.assertEqual(statuses["FIN_OPENING_BALANCE_PARITY"], "UNMEASURED")
        self.assertEqual(statuses["BUSINESS_PRESIGNATURE"], "UNMEASURED")
        self.assertIsNone(record["financial_balance_parity"]["balance_variance_bdt"])
        self.assertEqual(
            record["stream_checksums"]["branches"],
            M.rehearsal.compute_sha256(extracts / "branches_extract.json"),
        )
        self.assertEqual(record["mig02_control_totals"]["stream_counts"], {"branches": 3})
        self.assertEqual(presign["signatories"], [])
        self.assertNotIn("UNCONDITIONAL AUTHORIZATION", presign["authorization"])
        on_disk = json.loads((self.evidence / M.PRESIGN_NAME).read_text(encoding="utf-8"))
        self.assertEqual(on_disk["status"], "UNMEASURED")

    def test_checksum_drift_fails(self):
        extracts = build_extracts(self.root)
        (extracts / "branches_extract.json").write_bytes(json.dumps(RECORDS[::-1]).encode("utf-8"))
        record, _ = M.run(extracts, self.evidence, unreachable)
        self.assertEqual(self._statuses(record)["MIG02_EXTRACT_BRANCHES"], "FAIL")
        self.assertEqual(record["status"], "FAIL")

    def test_extract_without_control_total_is_unmeasured(self):
        extracts = build_extracts(self.root)
        (extracts / "inventory_parts_extract.json").write_bytes(b"[{}, {}]")
        record, _ = M.run(extracts, self.evidence, unreachable)
        check = next(c for c in record["checks"] if c["id"] == "MIG02_UNMANIFESTED_EXTRACTS")
        self.assertEqual(check["status"], "UNMEASURED")
        self.assertEqual(check["extracts"]["inventory_parts_extract.json"]["record_count"], 2)
        self.assertNotEqual(record["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
