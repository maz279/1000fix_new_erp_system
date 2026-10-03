"""ocr harness tests — P06-M08-T08."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ocr_harness import EvaluationCase, evaluate  # noqa: E402


class TestHarness(unittest.TestCase):
    def test_exact_match_scoring(self):
        cases = [EvaluationCase("c1", "a.png", {"nid": "123", "name_bn": "রহিম"})]
        result = evaluate(cases, lambda p: {"nid": "123", "name_bn": "রহিম "})
        self.assertEqual(result.field_accuracy, 100.0)

    def test_near_miss_scores_zero(self):
        """Fuzzy credit flatters OCR accuracy into uselessness."""
        cases = [EvaluationCase("c1", "a.png", {"nid": "1234567890"})]
        result = evaluate(cases, lambda p: {"nid": "123456789"})
        self.assertEqual(result.field_accuracy, 0.0)

    def test_missing_field_scores_zero(self):
        cases = [EvaluationCase("c1", "a.png", {"nid": "1", "name": "x"})]
        result = evaluate(cases, lambda p: {"nid": "1"})
        self.assertEqual(result.field_accuracy, 50.0)

    def test_dry_run_recogniser_recognises_nothing(self):
        from ocr_harness import dry_run_recogniser
        self.assertEqual(dry_run_recogniser("x.png"), {})


if __name__ == "__main__":
    unittest.main()
