"""test_assistant_nlu — Comprehensive unit tests for M32 Conversational AI Assistant Engine.

Validates:
- Bengali and English Unicode text normalization.
- 100% intent classification precision on authored benchmark utterances.
- Confidence scoring thresholding (>= 0.70 for AI resolve; < 0.70 for human handoff).
- Explicit human agent request escalation.
- Complaint dispute escalation.
- Transactional intents routed to live-record grounding (never canned answers).
"""

import sys
import unittest
from pathlib import Path

# Ensure cd_contact_centre/models is importable directly
MODELS_DIR = Path(__file__).resolve().parents[1] / "models"
if str(MODELS_DIR) not in sys.path:
    sys.path.insert(0, str(MODELS_DIR))

from assistant_engine import (
    INTENT_REGISTRY,
    AssistantEngine,
    normalize_text,
    tokenize,
)


class TestTextNormalization(unittest.TestCase):
    def test_bengali_unicode_normalization(self):
        # Text with Zero-Width Joiner (ZWJ \u200D) and Zero-Width Non-Joiner (ZWNJ \u200C)
        dirty_bn = "আমার\u200c সার্ভিস\u200d অর্ডারের অবস্থা কী??!!"
        clean_bn = normalize_text(dirty_bn)
        self.assertEqual(clean_bn, "আমার সার্ভিস অর্ডারের অবস্থা কী")

    def test_english_case_and_punctuation_normalization(self):
        dirty_en = "  Where is my LAPTOP REPAIR Order, please?!  "
        clean_en = normalize_text(dirty_en)
        self.assertEqual(clean_en, "where is my laptop repair order please")

    def test_tokenize(self):
        tokens = tokenize("ধানমন্ডি সার্ভিস সেন্টার কোথায়?")
        self.assertEqual(tokens, ["ধানমন্ডি", "সার্ভিস", "সেন্টার", "কোথায়"])


class TestIntentClassification(unittest.TestCase):
    def setUp(self):
        self.engine = AssistantEngine()

    def assert_routed_to_grounding(self, res, intent):
        """A transactional intent is never answered by the pure engine: it
        is routed to live-record grounding and, standalone, hands off."""
        self.assertEqual(res.matched_intent, intent)
        self.assertGreaterEqual(res.confidence, 0.70)
        self.assertTrue(res.requires_grounding)
        self.assertFalse(res.resolvable)
        self.assertTrue(res.requires_handoff)
        self.assertEqual(res.handoff_reason, "requires_erp_grounding")

    def test_order_status_bengali(self):
        utterances = [
            "আমার সার্ভিস অর্ডারের বর্তমান অবস্থা কী?",
            "আমার ফোন মেরামতের কাজ কতদূর?",
            "অর্ডার স্ট্যাটাস জানতে চাই",
            "আমার ল্যাপটপ কি ঠিক হয়েছে?",
        ]
        for u in utterances:
            res = self.engine.classify_intent(u)
            self.assert_routed_to_grounding(res, "order.status")
            # Regression: the engine used to tell EVERY customer their repair
            # was completed and in QC, whatever the order's real state.
            self.assertNotIn("কোয়ালিটি টেস্টিং", res.response_text_bn)

    def test_order_status_english(self):
        utterances = [
            "What is the status of my service order?",
            "Is my phone repair completed?",
            "Track my repair order",
        ]
        for u in utterances:
            res = self.engine.classify_intent(u)
            self.assert_routed_to_grounding(res, "order.status")
            self.assertNotIn("Quality Inspection", res.response_text_en)

    def test_price_estimate_bengali(self):
        res = self.engine.classify_intent("ডিসপ্লে পরিবর্তনের খরচ কত?")
        self.assert_routed_to_grounding(res, "repair.price_estimate")
        self.assertNotIn("৫০০ টাকা", res.response_text_bn)

    def test_appointment_booking_bengali(self):
        res = self.engine.classify_intent("কাল সকাল ১০টায় একজন টেকনিশিয়ান পাঠাতে পারবেন?")
        self.assert_routed_to_grounding(res, "appointment.book")
        self.assertNotIn("নথিভুক্ত হয়েছে", res.response_text_bn)

    def test_branch_locator_bengali(self):
        res = self.engine.classify_intent("ধানমন্ডি সার্ভিস সেন্টার কোথায় এবং কখন খোলা?")
        self.assert_routed_to_grounding(res, "branch.locator")
        self.assertNotIn("হাউজ ৪২", res.response_text_bn)

    def test_invoice_download_bengali(self):
        res = self.engine.classify_intent("আমার আগের ইনভয়েস বা রশিদ দরকার")
        self.assert_routed_to_grounding(res, "invoice.download")
        self.assertNotIn("পাঠিয়ে দেওয়া হয়েছে", res.response_text_bn)

    def test_complaint_escalation_requires_handoff(self):
        res = self.engine.classify_intent("কাজ ঠিকমতো হয়নি, আমি কমপ্লেইন করতে চাই")
        self.assertEqual(res.matched_intent, "complaint.register")
        self.assertFalse(res.resolvable)
        self.assertTrue(res.requires_handoff)
        self.assertEqual(res.handoff_reason, "complaint_escalation")

    def test_explicit_agent_request_triggers_handoff(self):
        res = self.engine.classify_intent("মানুষের সাথে কথা বলতে চাই")
        self.assertEqual(res.matched_intent, "agent.request")
        self.assertFalse(res.resolvable)
        self.assertTrue(res.requires_handoff)
        self.assertEqual(res.handoff_reason, "customer_requested_agent")

    def test_unrecognized_query_falls_back_to_agent_handoff(self):
        res = self.engine.classify_intent("আজকে আবহাওয়া কেমন হবে?")
        self.assertFalse(res.resolvable)
        self.assertTrue(res.requires_handoff)
        self.assertEqual(res.handoff_reason, "low_intent_confidence")

    def test_empty_query_handling(self):
        res = self.engine.classify_intent("")
        self.assertFalse(res.resolvable)
        self.assertTrue(res.requires_handoff)

    # --- M61 Knowledge Base Intent Tests (R07-M04-T04 / Q-01 Closure) ---
    def test_knowledge_troubleshooting_bengali(self):
        res = self.engine.classify_intent("ল্যাপটপ অন হচ্ছে না কি করব?")
        self.assertEqual(res.matched_intent, "knowledge.troubleshooting")
        self.assertGreaterEqual(res.confidence, 0.70)
        self.assertTrue(res.resolvable)
        self.assertFalse(res.requires_handoff)
        self.assertIn("হার্ড রিবুট", res.response_text_bn)

    def test_knowledge_troubleshooting_english(self):
        res = self.engine.classify_intent("My laptop is not turning on what should I do?")
        self.assertEqual(res.matched_intent, "knowledge.troubleshooting")
        self.assertGreaterEqual(res.confidence, 0.70)
        self.assertTrue(res.resolvable)
        self.assertIn("hard restart", res.response_text_en)

    def test_knowledge_repair_guide_bengali(self):
        res = self.engine.classify_intent("মাদারবোর্ড রিপেয়ারের ধাপগুলো কি কি?")
        self.assertEqual(res.matched_intent, "knowledge.repair_guide")
        self.assertGreaterEqual(res.confidence, 0.70)
        self.assertTrue(res.resolvable)
        self.assertIn("ISO 9001:2015", res.response_text_bn)

    def test_knowledge_repair_guide_english(self):
        res = self.engine.classify_intent("What are the steps for motherboard repair?")
        self.assertEqual(res.matched_intent, "knowledge.repair_guide")
        self.assertGreaterEqual(res.confidence, 0.70)
        self.assertTrue(res.resolvable)
        self.assertIn("ISO 9001:2015", res.response_text_en)

    def test_knowledge_warranty_policy_bengali(self):
        res = self.engine.classify_intent("মেরামতের পর কি কোনো ওয়ারেন্টি আছে?")
        self.assertEqual(res.matched_intent, "knowledge.warranty_policy")
        self.assertGreaterEqual(res.confidence, 0.70)
        self.assertTrue(res.resolvable)
        self.assertIn("৯০ দিনের", res.response_text_bn)

    def test_knowledge_warranty_policy_english(self):
        res = self.engine.classify_intent("Is there any warranty after repair?")
        self.assertEqual(res.matched_intent, "knowledge.warranty_policy")
        self.assertGreaterEqual(res.confidence, 0.70)
        self.assertTrue(res.resolvable)
        self.assertIn("90-day", res.response_text_en)

    def test_knowledge_maintenance_tips_bengali(self):
        res = self.engine.classify_intent("ল্যাপটপের ব্যাটারি লাইফ কিভাবে বাড়ানো যায়?")
        self.assertEqual(res.matched_intent, "knowledge.maintenance_tips")
        self.assertGreaterEqual(res.confidence, 0.70)
        self.assertTrue(res.resolvable)
        self.assertIn("২০% এর নিচে", res.response_text_bn)

    def test_knowledge_maintenance_tips_english(self):
        res = self.engine.classify_intent("How to increase laptop battery lifespan?")
        self.assertEqual(res.matched_intent, "knowledge.maintenance_tips")
        self.assertGreaterEqual(res.confidence, 0.70)
        self.assertTrue(res.resolvable)
        self.assertIn("20%-80%", res.response_text_en)


class TestIntentRegistryQuality(unittest.TestCase):
    def test_all_intents_have_authored_bengali(self):
        for code, defn in INTENT_REGISTRY.items():
            self.assertTrue(
                len(defn.sample_bn) >= 4, f"Intent {code} lacks sufficient Bengali samples"
            )
            for sample in defn.sample_bn:
                # Assert sample is genuine Bengali Unicode characters (\u0980-\u09FF)
                has_bengali = any(0x0980 <= ord(c) <= 0x09FF for c in sample)
                self.assertTrue(
                    has_bengali, f"Sample '{sample}' does not contain Bengali characters"
                )


if __name__ == "__main__":
    unittest.main()
