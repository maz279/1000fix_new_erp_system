"""GV-009: tooling/upgrade/verify_fork_and_oca_matrix.py derives the fork audit from
FORKS.yaml, git status, versions.lock and vendored manifests, and reports upstream OCA v20
availability UNMEASURED - never a hard-coded per-repo v20 status or verdict PASS."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "upgrade" / "verify_fork_and_oca_matrix.py"
SHA = "0123456789abcdef0123456789abcdef01234567"
FULL_FORK = (
    "forks:\n"
    "  - repo: OCA/web\n"
    "    path: web_x\n"
    "    reason: r\n"
    "    upstream: u\n"
    "    exit_plan: e\n"
    "    approved_by: D-001\n"
    "    added_in_release: R1\n"
    "    review_by_release: R2\n"
)


def _load():
    spec = importlib.util.spec_from_file_location("verify_fork_and_oca_matrix_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class VerifyForkAndOcaMatrixTest(unittest.TestCase):
    def setUp(self):
        self.m = _load()
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        (root / "tooling").mkdir()
        (root / "FORKS.yaml").write_text("forks: []\n", encoding="utf-8")
        (root / "tooling" / "versions.lock").write_text(
            f"VENDOR_ODOO_BRANCH=19.0\nVENDOR_OCA_ORG=https://github.com/OCA\nVENDOR_OCA_WEB={SHA}\n",
            encoding="utf-8",
        )
        release = root / "vendor" / "odoo" / "odoo" / "release.py"
        release.parent.mkdir(parents=True)
        release.write_text("version_info = (19, 0, 0, FINAL, 0, '')\n", encoding="utf-8")
        self._module("web", "web_x", "19.0.1.0.0")
        self.m.REPO_ROOT = root
        self.m.EVIDENCE_DIR = root / "evidence"
        self.m.FORKS_FILE = root / "FORKS.yaml"
        self.m.VERSIONS_LOCK = root / "tooling" / "versions.lock"
        self.m.VENDOR_DIR = root / "vendor"
        self.m.VENDOR_OCA = root / "vendor" / "oca"
        self.m.ODOO_RELEASE = release
        self.m.git_status_vendor = lambda: ("code/", [])

    def tearDown(self):
        self.tmp.cleanup()

    def _module(self, repo: str, mod: str, version: str) -> None:
        d = Path(self.tmp.name) / "vendor" / "oca" / repo / mod
        d.mkdir(parents=True, exist_ok=True)
        (d / "__manifest__.py").write_text(f"{{'version': '{version}'}}", encoding="utf-8")

    def _run(self) -> tuple[int, dict]:
        code = self.m.main()
        ev = json.loads((self.m.EVIDENCE_DIR / self.m.EVIDENCE_NAME).read_text("utf-8"))
        return code, ev

    def _statuses(self, ev: dict) -> dict:
        return {c["check"]: c["status"] for c in ev["checks"]}

    def test_clean_tree_is_incomplete_because_v20_unmeasured(self):
        code, ev = self._run()
        self.assertEqual(code, 2)
        self.assertEqual(ev["verdict"], "INCOMPLETE")
        statuses = self._statuses(ev)
        self.assertEqual(statuses["oca_v20_availability"], "UNMEASURED")
        self.assertEqual(statuses["vendor_worktree_clean"], "PASS")
        self.assertIsNone(ev["oca_matrix"]["migrated_count"])
        self.assertTrue(
            all(r["v20_status"] == "UNMEASURED" for r in ev["oca_matrix"]["repositories"])
        )

    def test_git_unavailable_is_unmeasured(self):
        self.m.git_status_vendor = lambda: None
        code, ev = self._run()
        self.assertEqual(self._statuses(ev)["vendor_worktree_clean"], "UNMEASURED")
        self.assertNotEqual(ev["verdict"], "PASS")
        self.assertEqual(code, 2)

    def test_unauthorised_vendor_modification_fails(self):
        self.m.git_status_vendor = lambda: ("code/", [" M code/vendor/oca/web/web_x/x.py"])
        code, ev = self._run()
        self.assertEqual(code, 1)
        self.assertEqual(self._statuses(ev)["vendor_worktree_clean"], "FAIL")
        self.assertFalse(ev["fork_audit"]["vendor_clean"])

    def test_authorised_fork_passes_but_incomplete_entry_fails(self):
        self.m.git_status_vendor = lambda: ("code/", [" M code/vendor/oca/web/web_x/x.py"])
        self.m.FORKS_FILE.write_text(FULL_FORK, encoding="utf-8")
        _code, ev = self._run()
        statuses = self._statuses(ev)
        self.assertEqual(statuses["vendor_worktree_clean"], "PASS")
        self.assertEqual(statuses["fork_entries_complete"], "PASS")
        self.m.FORKS_FILE.write_text(FULL_FORK.replace("    exit_plan: e\n", ""), "utf-8")
        code, ev = self._run()
        self.assertEqual(self._statuses(ev)["fork_entries_complete"], "FAIL")
        self.assertEqual(code, 1)

    def test_unpinned_repo_and_off_series_module_fail(self):
        self._module("contract", "contract_x", "18.0.1.0.0")
        code, ev = self._run()
        statuses = self._statuses(ev)
        self.assertEqual(statuses["vendor_pins_match_tree"], "FAIL")
        self.assertEqual(statuses["vendored_series_consistent"], "FAIL")
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
