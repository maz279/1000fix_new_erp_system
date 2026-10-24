"""GV-009: tooling/dr/test_clone_with_masking.py computes its NFR-086c evidence
from explicit checks of tooling/dr/clone_with_masking.py - a leaking masker
yields a FAIL verdict and exit 1, never a hard-coded PASS.

Evidence is written only into a temporary directory.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import shutil
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DR_DIR = REPO_ROOT / "tooling" / "dr"


def _load(stem: str):
    spec = importlib.util.spec_from_file_location(f"{stem}_ut", DR_DIR / f"{stem}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CloneWithMaskingTest(unittest.TestCase):
    def setUp(self) -> None:
        self.masker = _load("clone_with_masking")

    def test_bank_account_is_masked(self) -> None:
        masked = self.masker.mask_stream_chunk("acct 20501234567890 end")
        self.assertNotIn("20501234567890", masked)
        self.assertIn("BANK-ACC-", masked)

    def test_residual_pii_detects_unmasked_values(self) -> None:
        self.assertEqual(self.masker.residual_pii("call 01712345678"), ["MOBILE_BD"])
        self.assertEqual(self.masker.residual_pii("mail rahim@gmail.com"), ["EMAIL"])
        self.assertEqual(self.masker.residual_pii("anon-1a2b3c4d@masked.1000fix.internal"), [])

    def test_process_stream_enforcement_is_computed(self) -> None:
        out = StringIO()
        stats = self.masker.process_stream(StringIO("101\t8492018472\t01823456789\n"), out)
        self.assertTrue(stats["nfr_086c_enforced"])
        self.assertEqual(stats["residual_pii_lines"], 0)

        self.masker.mask_stream_chunk = lambda text: text  # a masker that masks nothing
        stats = self.masker.process_stream(StringIO("101\t8492018472\n"), StringIO())
        self.assertFalse(stats["nfr_086c_enforced"])
        self.assertEqual(stats["residual_pii_lines"], 1)


class TestCloneWithMaskingEvidenceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="clone_masking_ut_"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.module = _load("test_clone_with_masking")
        self.module.EVIDENCE_DIR = self.tmp

    def run_main(self) -> tuple[int, dict]:
        with contextlib.redirect_stdout(io.StringIO()):
            code = self.module.main()
        return code, json.loads((self.tmp / self.module.EVIDENCE_FILE).read_text("utf-8"))

    def test_working_masker_passes_with_computed_fields(self) -> None:
        code, evidence = self.run_main()
        self.assertEqual(code, 0)
        self.assertEqual(evidence["status"], "PASS")
        self.assertTrue(evidence["nfr_086c_compliant"])
        self.assertEqual(evidence["failed_checks"], [])
        self.assertIn("BANK_ACC", evidence["checked_types"])
        self.assertIn("NID_13", evidence["checked_types"])

    def test_leaking_masker_fails(self) -> None:
        self.module.mask_stream_chunk = lambda text: text
        real_process = self.module.process_stream

        def leaking_process(input_stream, output_stream):
            for line in input_stream:
                output_stream.write(line)
            stats = real_process(StringIO(""), StringIO())
            stats.update(lines_processed=8, lines_masked=0, residual_pii_lines=3)
            return stats

        self.module.process_stream = leaking_process
        code, evidence = self.run_main()
        self.assertEqual(code, 1)
        self.assertEqual(evidence["status"], "FAIL")
        self.assertFalse(evidence["nfr_086c_compliant"])
        self.assertFalse(evidence["sovereign_pii_zero_leakage"])
        self.assertIn("SQL_DUMP_STREAM", evidence["failed_checks"])
        self.assertIn("NID_10", evidence["failed_checks"])

    def test_pytest_style_functions_raise_on_leak(self) -> None:
        self.module.mask_stream_chunk = lambda text: text
        with self.assertRaises(AssertionError):
            self.module.test_individual_masking_rules()


if __name__ == "__main__":
    unittest.main()
