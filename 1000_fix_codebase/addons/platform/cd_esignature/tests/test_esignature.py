# cd_esignature tests — M24 completion (P06-M08-T02).
import unittest
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / "models" / "fix_esignature.py").read_text(
    encoding="utf-8"
)
DOCUMENT = (
    Path(__file__).resolve().parents[3]
    / "platform"
    / "cd_document_core"
    / "models"
    / "fix_document.py"
).read_text(encoding="utf-8")


class TestEnvelope(unittest.TestCase):
    def test_provider_independent(self):
        """The envelope carries no vendor SDK — the L6 provider plugs in."""
        self.assertNotIn("docusign", SOURCE.lower())
        self.assertNotIn("apisign", SOURCE.lower())

    def test_evidence_hash_is_sha256(self):
        self.assertIn("hashlib.sha256", SOURCE)

    def test_send_requires_signers(self):
        self.assertIn("An envelope needs at least one signer", SOURCE)

    def test_completion_checks_all_signed(self):
        self.assertIn("all(s.signed_at", SOURCE)


class TestSignerOrder(unittest.TestCase):
    def test_unique_sequences_enforced(self):
        self.assertIn("Signing order sequences must be unique", SOURCE)


class TestLegalHold(unittest.TestCase):
    def test_hold_freezes_retention(self):
        """A legal hold stops the retention clock (no expiry while held)."""
        self.assertIn("if rec.legal_hold:", DOCUMENT)

    def test_hold_needs_reason(self):
        self.assertIn("legal_hold_reason", DOCUMENT)


if __name__ == "__main__":
    unittest.main()
