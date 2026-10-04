"""stt tests — P11-M04 (Bengali STT accuracy + PDPA gate)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import unittest

from stt import classify_bn_accuracy, compute_wer, transcribe


class TestWER(unittest.TestCase):
    def test_perfect_transcription(self):
        score = compute_wer("আমি ভাত খাই", "আমি ভাত খাই")
        self.assertEqual(score.wer, 0.0)

    def test_one_substitution(self):
        score = compute_wer("আমি ভাত খাই", "আমি মাছ খাই")
        self.assertEqual(score.substitutions, 1)
        self.assertAlmostEqual(score.wer, 1 / 3, places=3)

    def test_one_insertion(self):
        score = compute_wer("আমি খাই", "আমি ভাত খাই")
        self.assertEqual(score.insertions, 1)

    def test_one_deletion(self):
        score = compute_wer("আমি ভাত খাই", "আমি খাই")
        self.assertEqual(score.deletions, 1)

    def test_empty_reference(self):
        score = compute_wer("", "কিছু")
        self.assertEqual(score.wer, 1.0)

    def test_both_empty(self):
        score = compute_wer("", "")
        self.assertEqual(score.wer, 0.0)


class TestPDPA(unittest.TestCase):
    def test_transcription_requires_legal_basis(self):
        with self.assertRaises(ValueError):
            transcribe(5.0, legal_basis=False)

    def test_transcription_with_legal_basis(self):
        result = transcribe(5.0, legal_basis=True, text="হ্যালো")
        self.assertTrue(result.legal_basis_confirmed)


class TestAccuracyClassification(unittest.TestCase):
    def test_production_ready(self):
        self.assertEqual(classify_bn_accuracy(0.10), "production-ready")

    def test_unusable(self):
        self.assertEqual(classify_bn_accuracy(0.60), "unusable")


if __name__ == "__main__":
    unittest.main()
