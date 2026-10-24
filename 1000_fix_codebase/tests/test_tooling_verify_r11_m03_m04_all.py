"""verify_r11_m03_all / verify_r11_m04_all: a sub-script's exit 2 (UNMEASURED
checks) is INCOMPLETE, not FAIL; the milestone verdict is FAIL > INCOMPLETE >
PASS and the exit code is derived from it."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = {
    "verify_r11_m03_all": (5, "r11-m03-summary-audit.json"),
    "verify_r11_m04_all": (4, "r11-m04-summary-audit.json"),
}


def _load(stem: str):
    spec = importlib.util.spec_from_file_location(
        f"{stem}_ut", REPO_ROOT / "tooling" / "scripts" / f"{stem}.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TestMilestoneVerdicts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, stem: str, exit_codes: list[int]) -> tuple[int, dict]:
        module = _load(stem)
        module.EVIDENCE_DIR = Path(self.tmp.name)
        codes = iter(exit_codes)
        module.subprocess.run = lambda *a, **kw: SimpleNamespace(
            returncode=next(codes), stdout="tail\n"
        )
        rc = module.main()
        summary = json.loads((Path(self.tmp.name) / SCRIPTS[stem][1]).read_text(encoding="utf-8"))
        return rc, summary

    def test_all_pass(self):
        for stem, (n, _) in SCRIPTS.items():
            with self.subTest(stem):
                rc, summary = self._run(stem, [0] * n)
                self.assertEqual((rc, summary["verdict"]), (0, "PASS"))

    def test_unmeasured_subscript_is_incomplete_not_fail(self):
        for stem, (n, _) in SCRIPTS.items():
            with self.subTest(stem):
                rc, summary = self._run(stem, [0, 2] + [0] * (n - 2))
                self.assertEqual((rc, summary["verdict"]), (2, "INCOMPLETE"))
                self.assertEqual(summary["incomplete_tasks"], 1)
                self.assertEqual(summary["failed_tasks"], 0)
                self.assertEqual(summary["tasks"][1]["status"], "INCOMPLETE")

    def test_fail_outranks_incomplete(self):
        for stem, (n, _) in SCRIPTS.items():
            with self.subTest(stem):
                rc, summary = self._run(stem, [2, 1] + [0] * (n - 2))
                self.assertEqual((rc, summary["verdict"]), (1, "FAIL"))

    def test_crash_exit_code_is_fail(self):
        for stem, (n, _) in SCRIPTS.items():
            with self.subTest(stem):
                rc, summary = self._run(stem, [3] + [0] * (n - 1))
                self.assertEqual(summary["tasks"][0]["status"], "FAIL")
                self.assertEqual(rc, 1)


if __name__ == "__main__":
    unittest.main()
