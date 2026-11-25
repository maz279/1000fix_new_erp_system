"""R01-AUDIT: seed-51-branches links every pilot alias branch to its real
register branch (operating unit, zone, legacy reference). Exercised against
an in-memory fake cursor - the seed is never run against a database here."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "scripts" / "seed-51-branches.py"


def _load():
    spec = importlib.util.spec_from_file_location("seed_51_branches_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FakeBranchCursor:
    """Just enough of fix_branch for link_pilot_aliases."""

    def __init__(self, rows: dict[str, dict]):
        self.rows = rows  # code -> {"id", "operating_unit_id", "zone_id", ...}
        self._result = None
        self.updates: list[tuple] = []

    def _by_code(self, code):
        return self.rows.get(code)

    def execute(self, sql, params):
        sql = " ".join(sql.split())
        if sql.startswith("SELECT id, operating_unit_id, zone_id FROM fix_branch WHERE code"):
            row = self._by_code(params[0])
            self._result = (row["id"], row["operating_unit_id"], row["zone_id"]) if row else None
        elif sql.startswith("SELECT id FROM fix_branch WHERE code"):
            row = self._by_code(params[0])
            self._result = (row["id"],) if row else None
        elif sql.startswith("UPDATE fix_branch"):
            assert re.search(r"operating_unit_id = %s, zone_id = %s, legacy_reference = %s", sql)
            ou_id, zone_id, legacy_ref, branch_id = params
            row = next(r for r in self.rows.values() if r["id"] == branch_id)
            row.update(
                operating_unit_id=ou_id, zone_id=zone_id, legacy_reference=legacy_ref, active=True
            )
            self.updates.append(params)
            self._result = None
        else:
            raise AssertionError(f"unexpected SQL: {sql}")

    def fetchone(self):
        return self._result


def _rows():
    return {
        "BR-0001": {"id": 1, "operating_unit_id": 101, "zone_id": 11},
        "BR-0002": {"id": 2, "operating_unit_id": 102, "zone_id": 11},
        "HQ": {"id": 50, "operating_unit_id": 999, "zone_id": None},
        "PC-01": {"id": 51, "operating_unit_id": 999, "zone_id": None},
    }


class TestPilotAliasLinking(unittest.TestCase):
    def setUp(self):
        self.seed = _load()

    def test_alias_takes_the_real_branch_operating_unit(self):
        cur = FakeBranchCursor(_rows())
        linked = self.seed.link_pilot_aliases(cur, {"HQ": "BR-0001", "PC-01": "BR-0002"})
        self.assertEqual([link["alias_code"] for link in linked], ["HQ", "PC-01"])
        self.assertEqual(cur.rows["HQ"]["operating_unit_id"], 101)
        self.assertEqual(cur.rows["PC-01"]["operating_unit_id"], 102)
        self.assertEqual(cur.rows["PC-01"]["zone_id"], 11)
        self.assertEqual(cur.rows["PC-01"]["legacy_reference"], "BR:PILOT_ALIAS:PC-01->BR-0002")
        # the real branches are untouched
        self.assertNotIn("legacy_reference", cur.rows["BR-0002"])

    def test_missing_real_branch_is_an_error(self):
        cur = FakeBranchCursor(_rows())
        with self.assertRaises(RuntimeError):
            self.seed.link_pilot_aliases(cur, {"HQ": "BR-9999"})
        self.assertEqual(cur.updates, [])

    def test_absent_alias_is_skipped_not_invented(self):
        cur = FakeBranchCursor(_rows())
        linked = self.seed.link_pilot_aliases(cur, {"PC-05": "BR-0001"})
        self.assertEqual(linked, [])
        self.assertEqual(cur.updates, [])

    def test_never_writes_under_migrations(self):
        extract = self.seed.MIGRATIONS_DIR / "extracts" / "branches_extract.json"
        with self.assertRaises(ValueError):
            self.seed.resolve_output_path(extract)
        with self.assertRaises(ValueError):
            self.seed.export_branch_register([], extract)
        self.assertFalse(hasattr(self.seed, "EXTRACTS_DIR"))

    def test_dry_run_touches_nothing(self):
        before = {
            p.name: p.stat().st_mtime_ns
            for p in (self.seed.MIGRATIONS_DIR / "extracts").glob("*")
            if p.is_file()
        }
        self.assertEqual(self.seed.main(["--dry-run"]), 0)
        after = {
            p.name: p.stat().st_mtime_ns
            for p in (self.seed.MIGRATIONS_DIR / "extracts").glob("*")
            if p.is_file()
        }
        self.assertEqual(before, after)

    def test_export_goes_to_the_requested_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "branches.json"
            row = {
                "code": "BR-0001",
                "sc": "SC-001",
                "name": "n",
                "name_bn": "ন",
                "division": "DHA",
                "district": "Dhaka",
                "latitude": 23.79,
                "longitude": 90.37,
                "phone": "1",
                "email": "e",
                "operating_unit_code": "OU-BR0001",
                "legacy_reference": "BR:SC:SC-001",
                "wave": 1,
                "pilot": True,
            }
            self.seed.export_branch_register([row], out)
            self.assertEqual(json.loads(out.read_text(encoding="utf-8"))[0]["code"], "BR-0001")
            self.assertNotIn(b"\r\n", out.read_bytes())

    def test_alias_to_non_pilot_centre_is_surfaced(self):
        questions = self.seed.alias_data_questions()
        # PC-01 (pilot Dhanmondi) -> BR-0002 (wave-2 Motijheel) is the open data question
        self.assertEqual(len(questions), 1)
        self.assertIn("PC-01 maps to BR-0002", questions[0])
        original = dict(self.seed.PILOT_ALIAS_MAPPING)
        try:
            self.seed.PILOT_ALIAS_MAPPING["PC-01"] = "BR-0004"  # a wave-1 pilot centre
            self.assertEqual(self.seed.alias_data_questions(), [])
        finally:
            self.seed.PILOT_ALIAS_MAPPING.clear()
            self.seed.PILOT_ALIAS_MAPPING.update(original)

    def test_every_mapped_real_code_is_in_the_register(self):
        register_codes = {b["code"] for b in self.seed.BRANCH_REGISTER}
        for alias, real in self.seed.PILOT_ALIAS_MAPPING.items():
            self.assertIn(real, register_codes, f"alias {alias} maps to unknown {real}")


if __name__ == "__main__":
    unittest.main()
