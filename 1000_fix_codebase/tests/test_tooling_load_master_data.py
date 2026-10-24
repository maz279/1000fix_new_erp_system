"""GV-009: tooling/scripts/load-master-data.py reads approval from each MD-* file's own
frontmatter - Draft datasets are NOT APPROVED, B-14 stays OPEN, the register carries no
fabricated sign-offs, and --dry-run never touches a database or migrations/."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "scripts" / "load-master-data.py"

MD_TEMPLATE = """---
id: {id}
title: Test dataset {id}
status: {status}
owner: MDM Lead
approver: {approver}
traces_to: [M64]
wave: W1
---

# {id}

## 9. Sample rows

```csv
code,name
A1,Alpha
B2,Beta
```
"""


def _load():
    spec = importlib.util.spec_from_file_location("load_master_data_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class LoadMasterDataTest(unittest.TestCase):
    def setUp(self):
        self.m = _load()
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.root = root
        self.md_root = root / "project_content" / "02_Master_Data_and_Configuration" / "02A"
        self.md_root.mkdir(parents=True)
        self.m.PROJECT_DIR = root
        self.m.MD_ROOT = self.md_root.parent
        self.m.OUTPUT_REGISTER = root / "docs" / "register.md"
        self.m.OUTPUT_JSON = root / "migrations" / "extracts" / "master-data-loaded.json"
        self.m.DRY_RUN_EVIDENCE = root / "docs" / "evidence" / "baseline.json"
        self.m.TIER_MAP = {0: ["MD-001"], 1: ["MD-002"]}

        def _no_db():
            raise AssertionError("get_db must not be called")

        self.m.get_db = _no_db

    def tearDown(self):
        self.tmp.cleanup()

    def _write(self, did: str, status: str, approver: str = "Chief Financial Officer"):
        text = MD_TEMPLATE.format(id=did, status=status, approver=approver)
        (self.md_root / f"{did}_Test.md").write_text(text, encoding="utf-8")

    def _evidence(self) -> dict:
        return json.loads(self.m.DRY_RUN_EVIDENCE.read_text(encoding="utf-8"))

    def test_draft_datasets_fail_approval_and_keep_b14_open(self):
        self._write("MD-001", "Draft")
        self._write("MD-002", "Draft")
        self.assertEqual(self.m.main(["--dry-run"]), 1)
        ev = self._evidence()
        self.assertEqual(ev["verdict"], "FAIL")
        self.assertTrue(ev["b14_resolution"].startswith("OPEN"))
        self.assertEqual(ev["approved_datasets"], 0)
        statuses = {c["check"]: c["status"] for c in ev["checks"]}
        self.assertEqual(statuses["approval"], "FAIL")
        self.assertEqual(statuses["database_load"], "UNMEASURED")
        for d in ev["datasets"]:
            self.assertTrue(d["approval_status"].startswith("NOT APPROVED"))
        register = self.m.OUTPUT_REGISTER.read_text(encoding="utf-8")
        self.assertNotIn("**SIGNED**", register)
        self.assertNotIn("RESOLVED / CLOSED", register)
        self.assertIn("PENDING", register)
        self.assertFalse(self.m.OUTPUT_JSON.exists(), "dry run must not write migrations/")

    def test_all_approved_dry_run_is_incomplete_not_pass(self):
        self._write("MD-001", "Approved")
        self._write("MD-002", "Baselined")
        self.assertEqual(self.m.main(["--dry-run"]), 2)
        ev = self._evidence()
        self.assertEqual(ev["verdict"], "INCOMPLETE")
        self.assertTrue(ev["b14_resolution"].startswith("OPEN"))
        self.assertEqual(ev["approved_datasets"], 2)

    def test_missing_dataset_fails_inventory(self):
        self._write("MD-001", "Approved")
        self.assertEqual(self.m.main(["--dry-run"]), 1)
        statuses = {c["check"]: c["status"] for c in self._evidence()["checks"]}
        self.assertEqual(statuses["inventory"], "FAIL")

    def test_unreachable_db_in_load_mode_is_unmeasured(self):
        self._write("MD-001", "Approved")
        self._write("MD-002", "Approved")

        def _refused():
            raise ConnectionError("connection refused")

        self.m.get_db = _refused
        self.assertEqual(self.m.main([]), 2)
        ev = json.loads(self.m.OUTPUT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(ev["verdict"], "INCOMPLETE")
        db = next(c for c in ev["checks"] if c["check"] == "database_load")
        self.assertEqual(db["status"], "UNMEASURED")

    def test_resolved_only_when_every_check_passes(self):
        self._write("MD-001", "Approved")
        self._write("MD-002", "Approved")
        parsed = self.m.parse_all(verbose=False)
        ok = self.m.evaluate_baseline(
            parsed, {"status": "PASS", "detail": "2/2 loaded", "loaded_datasets": 2}
        )
        self.assertEqual(ok["verdict"], "PASS")
        self.assertTrue(ok["b14_resolution"].startswith("RESOLVED"))
        parsed["MD-002"]["approved"] = False
        bad = self.m.evaluate_baseline(
            parsed, {"status": "PASS", "detail": "2/2 loaded", "loaded_datasets": 2}
        )
        self.assertEqual(bad["verdict"], "FAIL")


if __name__ == "__main__":
    unittest.main()
