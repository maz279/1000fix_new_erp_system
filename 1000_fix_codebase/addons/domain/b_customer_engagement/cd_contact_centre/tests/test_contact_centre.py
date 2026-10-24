# cd_contact_centre tests — M27 + M32 (P07-M05; G4-04/G4-05).
import unittest
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / "models" / "fix_contact_centre.py").read_text(
    encoding="utf-8"
)


class TestUnifiedChannels(unittest.TestCase):
    def test_all_five_channels(self):
        for channel in ("voice", "whatsapp", "chat", "email", "in_app"):
            self.assertIn('"%s"' % channel, SOURCE)

    def test_hotline_is_voice(self):
        self.assertIn("Hotline 16743", SOURCE)


class TestSystemOfRecord(unittest.TestCase):
    def test_transcript_is_the_record(self):
        """G4-04: hotline conversations captured — turns are stored, not
        just outcomes."""
        self.assertIn("turn_ids", SOURCE)
        self.assertIn("Transcript", SOURCE)

    def test_contact_identity_join_key(self):
        """Customer 360: unidentified callers join by identity, not guess."""
        self.assertIn("contact_identity", SOURCE)


class TestHandoff(unittest.TestCase):
    def test_full_context_transfer(self):
        """T07: the handoff carries channel, intent, reason and turn count."""
        body = SOURCE[
            SOURCE.index("def action_handoff_to_agent") : SOURCE.index("def action_resolve")
        ]
        for key in ("channel", "intent", "reason", "turns"):
            self.assertIn(key, body)

    def test_handoff_event_published(self):
        self.assertIn('"conversation.handed_off"', SOURCE)


class TestResolutionRate(unittest.TestCase):
    def test_measured_against_handoffs_not_sessions(self):
        """G4-05: AI resolutions / (AI resolutions + handoffs) — the honest
        denominator."""
        body = SOURCE[SOURCE.index("def resolution_rate") :]
        self.assertIn("ai + handoffs", body)
        self.assertNotIn("search_count([])", body)


class TestAssistantIntents(unittest.TestCase):
    def test_transactional_only(self):
        """T06: the knowledge base is W6 — the register carries no
        how-to/why intents (an already-ratified scope cut)."""
        self.assertIn("transactional", SOURCE)
        self.assertIn("knowledge base is W6", SOURCE)

    def test_bengali_utterances_authored(self):
        """T08: real Bengali utterances, never machine-translated."""
        self.assertIn("never machine-translated", SOURCE)
        self.assertIn("sample_bn", SOURCE)

    def test_grounding_declared(self):
        self.assertIn("grounding", SOURCE)

    def test_handoff_on_failure(self):
        self.assertIn("handoff_on_failure", SOURCE)


class TestTelephonyAndPIIMasking(unittest.TestCase):
    def test_call_sid_telephony_field(self):
        self.assertIn("call_sid", SOURCE)

    def test_pii_masked_pdpa_field(self):
        self.assertIn("pii_masked", SOURCE)

    def test_intake_hotline_call_method(self):
        self.assertIn("def intake_hotline_call", SOURCE)
        self.assertIn("conversation.hotline_captured", SOURCE)

    def test_intake_message_method(self):
        self.assertIn("def intake_message", SOURCE)

    def test_mask_pii_for_mining_method(self):
        self.assertIn("def mask_pii_for_mining", SOURCE)
        self.assertIn("[PHONE_MASKED]", SOURCE)
        self.assertIn("[EMAIL_MASKED]", SOURCE)


if __name__ == "__main__":
    unittest.main()
