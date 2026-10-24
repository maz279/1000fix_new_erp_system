"""test_fcr_measurement — engine routing battery behind First-Contact Resolution (G4-05).

Task R05-M03-T04 & Gate Item G4-05:
"Implement human handoff with full context transfer and measure >= 40%
first-contact resolution in production terms (G4-05) — rate report vs handoffs"

Tests 100 realistic customer interactions (50 Bengali, 50 English) across common
contact centre requests on Hotline 16743 and chat channels. The FCR rate
itself is measured on live conversations (resolution_rate()), counting only
answers grounded in real records.
"""

import sys
import unittest
from pathlib import Path

MODELS_DIR = Path(__file__).resolve().parents[1] / "models"
if str(MODELS_DIR) not in sys.path:
    sys.path.insert(0, str(MODELS_DIR))

from assistant_engine import AssistantEngine

BENCHMARK_INTERACTIONS = [
    # 1. Order Status (Bengali & English) - 20 interactions
    ("আমার সার্ভিস অর্ডারের বর্তমান অবস্থা কী?", "bn", True, "order.status"),
    ("আমার ফোন মেরামতের কাজ কতদূর?", "bn", True, "order.status"),
    ("অর্ডার স্ট্যাটাস জানতে চাই", "bn", True, "order.status"),
    ("আমার ল্যাপটপ কি ঠিক হয়েছে?", "bn", True, "order.status"),
    ("ডিভাইস ডেলিভারি কবে পাবো?", "bn", True, "order.status"),
    ("সার্ভিসিং কি শেষ হয়েছে?", "bn", True, "order.status"),
    ("অর্ডার ট্র্যাকিং করতে চাই", "bn", True, "order.status"),
    ("আমার কাজের অগ্রগতি কি?", "bn", True, "order.status"),
    ("What is the status of my service order?", "en", True, "order.status"),
    ("Is my phone repair completed?", "en", True, "order.status"),
    ("Track my repair order", "en", True, "order.status"),
    ("When will my laptop be ready for pickup?", "en", True, "order.status"),
    ("Current repair status please", "en", True, "order.status"),
    ("Check status for my TV service", "en", True, "order.status"),
    ("Can I get update on order progress?", "en", True, "order.status"),
    ("Is my tablet ready today?", "en", True, "order.status"),
    ("Status update on pending repair", "en", True, "order.status"),
    ("Has the technician inspected my device?", "en", True, "order.status"),
    ("Delivery date for serviced phone", "en", True, "order.status"),
    ("Want to know my order progress", "en", True, "order.status"),
    # 2. Repair Pricing (Bengali & English) - 16 interactions
    ("ডিসপ্লে পরিবর্তনের খরচ কত?", "bn", True, "repair.price_estimate"),
    ("ব্যাটারি চেঞ্জ করতে কত টাকা লাগবে?", "bn", True, "repair.price_estimate"),
    ("ল্যাপটপ মাদারবোর্ড রিপেয়ারের ফি কত?", "bn", True, "repair.price_estimate"),
    ("সার্ভিসিং চার্জ কত নিবেন?", "bn", True, "repair.price_estimate"),
    ("আইফোন স্ক্রিন লাগাতে কত টাকা?", "bn", True, "repair.price_estimate"),
    ("এসি মেরামতের খরচ কেমন পড়বে?", "bn", True, "repair.price_estimate"),
    ("পার্টসের দাম কত?", "bn", True, "repair.price_estimate"),
    ("ফ্রিজ মেরামতের চার্জ কত?", "bn", True, "repair.price_estimate"),
    ("How much does it cost to replace a screen?", "en", True, "repair.price_estimate"),
    ("What is the battery replacement charge?", "en", True, "repair.price_estimate"),
    ("Price estimate for motherboard repair", "en", True, "repair.price_estimate"),
    ("What are your standard servicing fees?", "en", True, "repair.price_estimate"),
    ("How much to fix iPhone display?", "en", True, "repair.price_estimate"),
    ("Servicing cost for split AC", "en", True, "repair.price_estimate"),
    ("Cost of replacing charging port", "en", True, "repair.price_estimate"),
    ("What is the diagnostic fee?", "en", True, "repair.price_estimate"),
    # 3. Branch Locator & Hours (Bengali & English) - 12 interactions
    ("ধানমন্ডি সার্ভিস সেন্টার কোথায় এবং কখন খোলা?", "bn", True, "branch.locator"),
    ("চট্টগ্রাম ব্রাঞ্চের ঠিকানা দিন", "bn", True, "branch.locator"),
    ("উত্তরা শাখা কি আজ খোলা আছে?", "bn", True, "branch.locator"),
    ("নিকটস্থ ১০০০ফিক্স সার্ভিস পয়েন্ট কোথায়?", "bn", True, "branch.locator"),
    ("সার্ভিস সেন্টার কয়টা পর্যন্ত খোলা থাকে?", "bn", True, "branch.locator"),
    ("মিরপুর ব্রাঞ্চের লোকেশন কোথায়?", "bn", True, "branch.locator"),
    (
        "Where is your Dhanmondi service center and what are the hours?",
        "en",
        True,
        "branch.locator",
    ),
    ("Address for Chittagong branch please", "en", True, "branch.locator"),
    ("Is the Uttara repair depot open on Saturday?", "en", True, "branch.locator"),
    ("Where is the nearest 1000FiX service outlet?", "en", True, "branch.locator"),
    ("Operating hours of Gulshan branch", "en", True, "branch.locator"),
    ("What time does Motijheel branch close?", "en", True, "branch.locator"),
    # 4. Appointment Booking (Bengali & English) - 10 interactions
    ("কাল সকাল ১০টায় একজন টেকনিশিয়ান পাঠাতে পারবেন?", "bn", True, "appointment.book"),
    ("বাসায় এসে সার্ভিসিং করার বুকিং দিতে চাই", "bn", True, "appointment.book"),
    ("হোম সার্ভিসের জন্য টেকনিশিয়ান লাগবে", "bn", True, "appointment.book"),
    ("শুক্রবার টেকনিশিয়ান আসার সময় দেওয়া যাবে?", "bn", True, "appointment.book"),
    ("টেকনিশিয়ান ভিজিটের শিডিউল করতে চাই", "bn", True, "appointment.book"),
    ("Can you send a technician to my office tomorrow?", "en", True, "appointment.book"),
    ("Book a home service visit for my TV", "en", True, "appointment.book"),
    ("I want to schedule an on-site technician appointment", "en", True, "appointment.book"),
    ("Technician booking for laptop maintenance", "en", True, "appointment.book"),
    ("Schedule home repair for washing machine", "en", True, "appointment.book"),
    # 5. Invoice & Receipt (Bengali & English) - 6 interactions
    ("আমার আগের ইনভয়েস বা রশিদ দরকার", "bn", True, "invoice.download"),
    ("পেমেন্ট বিল কপি পাঠানো যাবে?", "bn", True, "invoice.download"),
    ("মুশক ৬.৩ চালান কপি চাই", "bn", True, "invoice.download"),
    ("Send me the invoice for my last repair", "en", True, "invoice.download"),
    ("I need my payment receipt copy", "en", True, "invoice.download"),
    ("Download Mushak 6.3 tax invoice", "en", True, "invoice.download"),
    # --- Handoffs: Complaints, Explicit Agent Requests, Ambiguous / Out-of-Domain (36 interactions) ---
    # 6. Complaints (Auto-handoff) - 10 interactions
    ("কাজ ঠিকমতো হয়নি, আমি কমপ্লেইন করতে চাই", "bn", False, "complaint.register"),
    ("টেকনিশিয়ান এখনো আসেনি, খুব খারাপ সার্ভিস", "bn", False, "complaint.register"),
    ("মেরামতের পর আবার একই সমস্যা হচ্ছে", "bn", False, "complaint.register"),
    ("আমার অভিযোগ অফিসিয়ালি রেজিস্টার করুন", "bn", False, "complaint.register"),
    ("আমি সুপারভাইজারের সাথে কথা বলব", "bn", False, "complaint.register"),
    (
        "The repair was defective, I want to file an official complaint",
        "en",
        False,
        "complaint.register",
    ),
    ("Technician did not show up, terrible experience", "en", False, "complaint.register"),
    ("Device is malfunctioning again after repair", "en", False, "complaint.register"),
    ("Escalate this complaint to a supervisor immediately", "en", False, "complaint.register"),
    ("I am extremely dissatisfied with the service delay", "en", False, "complaint.register"),
    # 7. Explicit Agent Requests (Auto-handoff) - 12 interactions
    ("মানুষের সাথে কথা বলতে চাই", "bn", False, "agent.request"),
    ("আমাকে একজন এজেন্টের কাছে দিন", "bn", False, "agent.request"),
    ("কাস্টমার কেয়ার প্রতিনিধির সাথে কথা বলব", "bn", False, "agent.request"),
    ("হিউম্যান এজেন্ট প্লিজ", "bn", False, "agent.request"),
    ("সরাসরি কারো সাথে কথা বলতে চাই", "bn", False, "agent.request"),
    ("এজেন্ট সাপোর্ট দরকার", "bn", False, "agent.request"),
    ("I want to speak with a human agent", "en", False, "agent.request"),
    ("Connect me to customer care representative", "en", False, "agent.request"),
    ("Talk to a human representative please", "en", False, "agent.request"),
    ("Transfer to live agent", "en", False, "agent.request"),
    ("Can I speak to someone real?", "en", False, "agent.request"),
    ("Need human assistance immediately", "en", False, "agent.request"),
    # 8. Out of Domain / Low Confidence (Handoff fallback) - 14 interactions
    ("আজকে ঢাকায় আবহাওয়া কেমন থাকবে?", "bn", False, None),
    ("শেয়ার বাজারের খবর কি?", "bn", False, None),
    ("ক্রিকেট খেলার স্কোর কত?", "bn", False, None),
    ("কাছের রেস্টুরেন্ট কোনটি?", "bn", False, None),
    ("ট্রেনের টিকিট কাটার নিয়ম কি?", "bn", False, None),
    ("আপনার প্রিয় রং কি?", "bn", False, None),
    ("What is the capital of France?", "en", False, None),
    ("How is the traffic in Gulshan right now?", "en", False, None),
    ("Tell me a funny joke", "en", False, None),
    ("What are the stock prices today?", "en", False, None),
    ("Do you sell coffee makers?", "en", False, None),
    ("Can you help me with my math homework?", "en", False, None),
    ("Who won the football match yesterday?", "en", False, None),
    ("Recommend a good smartphone to buy", "en", False, None),
]


class TestFCRMeasurement(unittest.TestCase):
    def setUp(self):
        self.engine = AssistantEngine()

    def test_run_100_session_fcr_battery(self):
        """Engine-level routing battery over 100 interactions.

        The pure engine has no ERP access, so it can no longer "resolve" a
        transactional query: every transactional row must be ROUTED to
        live-record grounding (fix.conversation._ground_intent_response), and
        every escalation / out-of-domain row must hand off. G4-05 FCR is
        measured on live conversations by fix.conversation.resolution_rate(),
        which counts only answers actually grounded in records - an engine
        benchmark that counted canned replies as resolutions overstated it."""
        total_interactions = len(BENCHMARK_INTERACTIONS)
        self.assertEqual(
            total_interactions, 100, "Benchmark suite must contain exactly 100 interactions"
        )

        routed_to_grounding = 0
        engine_resolved = 0
        handoff_count = 0

        for utterance, _lang, expected_resolvable, expected_intent in BENCHMARK_INTERACTIONS:
            result = self.engine.classify_intent(utterance)

            # The intent the engine acted on: a candidate below the 0.70
            # confidence threshold is a fallback handoff, not an intent match,
            # so out-of-domain rows (expected_intent None) must not clear it.
            confident_intent = result.matched_intent if result.confidence >= 0.70 else None
            self.assertEqual(
                confident_intent,
                expected_intent,
                f"Intent mismatch for '{utterance}': got {result.matched_intent!r} "
                f"at confidence {result.confidence}",
            )

            if result.requires_grounding:
                routed_to_grounding += 1
                self.assertTrue(expected_resolvable, f"Unexpected grounding for '{utterance}'")
                self.assertFalse(result.resolvable)
            elif result.resolvable and not result.requires_handoff:
                engine_resolved += 1
            else:
                handoff_count += 1
                self.assertFalse(
                    expected_resolvable, f"Unexpected handoff for resolvable query '{utterance}'"
                )
                self.assertTrue(result.requires_handoff)
                self.assertTrue(len(result.handoff_reason) > 0)

        self.assertEqual(routed_to_grounding + engine_resolved + handoff_count, 100)
        self.assertEqual(
            routed_to_grounding, 64, "Expected 64 transactional queries routed to grounding"
        )
        self.assertEqual(engine_resolved, 0, "The engine must not resolve transactional queries")
        self.assertEqual(handoff_count, 36, "Expected exactly 36 escalated handoffs")


if __name__ == "__main__":
    unittest.main()
