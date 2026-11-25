"""stt tests — P11-M04 (Bengali STT WER scoring + PDPA gate + backend honesty)."""

import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import unittest

from stt import (
    STTBackendNotConfigured,
    classify_bn_accuracy,
    compute_wer,
    transcribe,
)


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
            transcribe(5.0, legal_basis=False, audio=b"RIFF")

    def test_transcription_without_backend_refuses_instead_of_echoing(self):
        """No STT_BACKEND configured: transcribe() must fail loudly. The old
        behaviour returned the caller's own string as the 'transcript'."""
        with self.assertRaises(STTBackendNotConfigured) as ctx:
            transcribe(5.0, legal_basis=True, audio=b"RIFF....")
        self.assertIn("no STT backend is configured", str(ctx.exception))
        self.assertIn("Refusing to fabricate", str(ctx.exception))


class TestWhisperServerSeam(unittest.TestCase):
    """The optional real backend seam: STT_BACKEND=whisper-server."""

    def setUp(self):
        self._saved = {
            k: __import__("os").environ.get(k) for k in ("STT_BACKEND", "STT_BACKEND_URL")
        }
        __import__("os").environ.update(
            STT_BACKEND="whisper-server", STT_BACKEND_URL="http://stt.test:9000"
        )

    def tearDown(self):
        import os

        for key, value in self._saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_transcribes_real_audio_through_the_server(self):
        import json

        captured = {}

        class FakeResponse:
            status = 200

            def read(self):
                return json.dumps({"text": "মাদারবোর্ড সার্কিট শর্ট", "confidence": 0.81}).encode()

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        def fake_urlopen(req, timeout=None):
            captured["url"] = req.full_url
            captured["data"] = req.data
            return FakeResponse()

        original = urllib.request.urlopen
        urllib.request.urlopen = fake_urlopen
        try:
            result = transcribe(12.5, legal_basis=True, audio=b"RIFF-audio-bytes")
        finally:
            urllib.request.urlopen = original

        self.assertEqual(result.text, "মাদারবোর্ড সার্কিট শর্ট")
        self.assertEqual(result.backend, "whisper-server")
        self.assertTrue(result.legal_basis_confirmed)
        self.assertAlmostEqual(result.confidence, 0.81)
        self.assertEqual(captured["url"], "http://stt.test:9000/v1/audio/transcriptions")
        self.assertEqual(captured["data"], b"RIFF-audio-bytes")

    def test_backend_without_url_refuses(self):
        import os

        os.environ.pop("STT_BACKEND_URL", None)
        with self.assertRaises(STTBackendNotConfigured):
            transcribe(5.0, legal_basis=True, audio=b"RIFF")

    def test_audio_is_required_even_with_backend(self):
        with self.assertRaises(ValueError):
            transcribe(5.0, legal_basis=True, audio=None)


class TestAccuracyClassification(unittest.TestCase):
    def test_production_ready(self):
        self.assertEqual(classify_bn_accuracy(0.10), "production-ready")

    def test_unusable(self):
        self.assertEqual(classify_bn_accuracy(0.60), "unusable")


if __name__ == "__main__":
    unittest.main()
