"""assistant_engine — Hybrid transactional and knowledge NLU engine for M32 Conversational AI.

Supports authored Bengali (বাংলা) and English NLU for 1000FiX contact centre
channels (Hotline 16743, WhatsApp, Web Chat, In-App).
Adheres to strict enterprise rules:
- Transactional & Knowledge: Integrates M61 technical library (closing Q-01 scope reduction; R07-M04-T04).
- Authored Bengali utterances: Never machine-translated (DE-17, T08).
- Honest resolution measurement: Grounded ERP answers count as resolved;
  low-confidence or complaint/escalation intents hand off with full context.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

# --- 1. Transactional Intent Definitions with Authored Bengali & English Corpora ---


@dataclass
class IntentDefinition:
    code: str
    name: str
    name_bn: str
    description: str
    sample_bn: list[str]
    sample_en: list[str]
    grounding_source: str
    resolvable_by_ai: bool = True
    auto_handoff: bool = False
    handoff_reason: str = ""
    # A transactional intent whose answer depends on the customer's live ERP
    # records. The pure engine cannot answer it: it routes the turn to the
    # Odoo-side grounding step (fix.conversation._ground_intent_response),
    # which answers from real records or hands off - never a canned outcome.
    requires_grounding: bool = False


INTENT_REGISTRY: dict[str, IntentDefinition] = {
    "order.status": IntentDefinition(
        code="order.status",
        name="Order Status Inquiry",
        name_bn="সার্ভিস অর্ডারের বর্তমান অবস্থা",
        description="Customer asking for current progress or tracking of a repair order",
        sample_bn=[
            "আমার সার্ভিস অর্ডারের বর্তমান অবস্থা কী?",
            "আমার ফোন মেরামতের কাজ কতদূর?",
            "অর্ডার স্ট্যাটাস জানতে চাই",
            "আমার ল্যাপটপ কি ঠিক হয়েছে?",
            "ডিভাইস ডেলিভারি কবে পাবো?",
            "সার্ভিসিং কি শেষ হয়েছে?",
            "অর্ডার ট্র্যাকিং করতে চাই",
            "আমার কাজের অগ্রগতি কি?",
        ],
        sample_en=[
            "What is the status of my service order?",
            "Is my phone repair completed?",
            "Track my repair order",
            "When will my laptop be ready for pickup?",
            "Current repair status please",
            "Check status for my TV service",
            "Can I get update on order progress?",
            "Is my tablet ready today?",
            "Status update on pending repair",
            "Has the technician inspected my device?",
            "Delivery date for serviced phone",
            "Want to know my order progress",
        ],
        grounding_source="fix.service.order.state",
        resolvable_by_ai=True,
        requires_grounding=True,
    ),
    "repair.price_estimate": IntentDefinition(
        code="repair.price_estimate",
        name="Repair Price & Fee Estimate",
        name_bn="মেরামতের আনুমানিক খরচ ও ফি",
        description="Customer asking standard service charge or parts replacement pricing",
        sample_bn=[
            "ডিসপ্লে পরিবর্তনের খরচ কত?",
            "ব্যাটারি চেঞ্জ করতে কত টাকা লাগবে?",
            "ল্যাপটপ মাদারবোর্ড রিপেয়ারের ফি কত?",
            "সার্ভিসিং চার্জ কত নিবেন?",
            "আইফোন স্ক্রিন লাগাতে কত টাকা?",
            "এসি মেরামতের খরচ কেমন পড়বে?",
            "পার্টসের দাম কত?",
            "ফ্রিজ মেরামতের চার্জ কত?",
        ],
        sample_en=[
            "How much does it cost to replace a screen?",
            "What is the battery replacement charge?",
            "Price estimate for motherboard repair",
            "What are your standard servicing fees?",
            "How much to fix iPhone display?",
            "Servicing cost for split AC",
            "Cost of replacing charging port",
            "What is the diagnostic fee?",
        ],
        grounding_source="fix.pricing.card",
        resolvable_by_ai=True,
        requires_grounding=True,
    ),
    "appointment.book": IntentDefinition(
        code="appointment.book",
        name="Technician Appointment Booking",
        name_bn="হোম সার্ভিস বা টেকনিশিয়ান অ্যাপয়েন্টমেন্ট বুকিং",
        description="Booking a home visit or workshop appointment",
        sample_bn=[
            "কাল সকাল ১০টায় একজন টেকনিশিয়ান পাঠাতে পারবেন?",
            "বাসায় এসে সার্ভিসিং করার বুকিং দিতে চাই",
            "হোম সার্ভিসের জন্য টেকনিশিয়ান লাগবে",
            "শুক্রবার টেকনিশিয়ান আসার সময় দেওয়া যাবে?",
            "টেকনিশিয়ান ভিজিটের শিডিউল করতে চাই",
        ],
        sample_en=[
            "Can you send a technician to my office tomorrow?",
            "Book a home service visit for my TV",
            "I want to schedule an on-site technician appointment",
            "Technician booking for laptop maintenance",
            "Schedule home repair for washing machine",
        ],
        grounding_source="fix.field.service.appointment",
        resolvable_by_ai=True,
        requires_grounding=True,
    ),
    "branch.locator": IntentDefinition(
        code="branch.locator",
        name="Branch Locator & Hours",
        name_bn="সার্ভিস সেন্টার লোকেশন ও সময়সূচী",
        description="Inquiries regarding service centers, addresses, and working hours",
        sample_bn=[
            "ধানমন্ডি সার্ভিস সেন্টার কোথায় এবং কখন খোলা?",
            "চট্টগ্রাম ব্রাঞ্চের ঠিকানা দিন",
            "উত্তরা শাখা কি আজ খোলা আছে?",
            "নিকটস্থ ১০০০ফিক্স সার্ভিস পয়েন্ট কোথায়?",
            "সার্ভিস সেন্টার কয়টা পর্যন্ত খোলা থাকে?",
            "মিরপুর ব্রাঞ্চের লোকেশন কোথায়?",
        ],
        sample_en=[
            "Where is your Dhanmondi service center and what are the hours?",
            "Address for Chittagong branch please",
            "Is the Uttara repair depot open on Saturday?",
            "Where is the nearest 1000FiX service outlet?",
            "Operating hours of Gulshan branch",
            "What time does Motijheel branch close?",
        ],
        grounding_source="res.branch.directory",
        resolvable_by_ai=True,
        requires_grounding=True,
    ),
    "invoice.download": IntentDefinition(
        code="invoice.download",
        name="Invoice & Receipt Request",
        name_bn="ইনভয়েস বা পেমেন্ট রশিদ ডাউনলোড",
        description="Customer requesting bill, money receipt or Mushak 6.3 copy",
        sample_bn=[
            "আমার আগের ইনভয়েস বা রশিদ দরকার",
            "পেমেন্ট বিল কপি পাঠানো যাবে?",
            "মুশক ৬.৩ চালান কপি চাই",
            "গত সার্ভিসের মানি রিসিট দেন",
            "ইনভয়েস ডাউনলোড কিভাবে করব?",
        ],
        sample_en=[
            "Send me the invoice for my last repair",
            "I need my payment receipt copy",
            "Download Mushak 6.3 tax invoice",
            "Can I get a copy of my billing statement?",
        ],
        grounding_source="account.move.customer_invoices",
        resolvable_by_ai=True,
        requires_grounding=True,
    ),
    "complaint.register": IntentDefinition(
        code="complaint.register",
        name="Complaint & Dispute Escalation",
        name_bn="অভিযোগ ও সমস্যা নিষ্পত্তি",
        description="Customer dissatisfaction, repeated defects, or technician delays",
        sample_bn=[
            "কাজ ঠিকমতো হয়নি, আমি কমপ্লেইন করতে চাই",
            "টেকনিশিয়ান এখনো আসেনি, খুব খারাপ সার্ভিস",
            "মেরামতের পর আবার একই সমস্যা হচ্ছে",
            "আমার অভিযোগ অফিসিয়ালি রেজিস্টার করুন",
            "আমি সুপারভাইজারের সাথে কথা বলব",
        ],
        sample_en=[
            "The repair was defective, I want to file an official complaint",
            "Technician did not show up, terrible experience",
            "Device is malfunctioning again after repair",
            "Escalate this complaint to a supervisor immediately",
            "I am extremely dissatisfied with the service delay",
        ],
        grounding_source="fix.complaint.ticket",
        resolvable_by_ai=False,
        auto_handoff=True,
        handoff_reason="complaint_escalation",
    ),
    "agent.request": IntentDefinition(
        code="agent.request",
        name="Explicit Agent Request",
        name_bn="এজেন্টের সাথে সরাসরি কথা বলার অনুরোধ",
        description="Explicit request to transfer to human customer care representative",
        sample_bn=[
            "মানুষের সাথে কথা বলতে চাই",
            "আমাকে একজন এজেন্টের কাছে দিন",
            "কাস্টমার কেয়ার প্রতিনিধির সাথে কথা বলব",
            "হিউম্যান এজেন্ট প্লিজ",
            "সরাসরি কারো সাথে কথা বলতে চাই",
            "এজেন্ট সাপোর্ট দরকার",
        ],
        sample_en=[
            "I want to speak with a human agent",
            "Connect me to customer care representative",
            "Talk to a human representative please",
            "Transfer to live agent",
            "Can I speak to someone real?",
            "Need human assistance immediately",
        ],
        grounding_source="fix.conversation.agent_transfer",
        resolvable_by_ai=False,
        auto_handoff=True,
        handoff_reason="customer_requested_agent",
    ),
    # --- M61 Knowledge Base Intents (R07-M04-T04 / Q-01 Scope Closure) ---
    "knowledge.troubleshooting": IntentDefinition(
        code="knowledge.troubleshooting",
        name="Device Troubleshooting & Diagnostics",
        name_bn="ডিভাইস ট্রাবলশুটিং ও প্রাথমিক সমাধান",
        description="Customer asking how to diagnose or solve common hardware and software device glitches",
        sample_bn=[
            "ল্যাপটপ অন হচ্ছে না কি করব?",
            "ফোন খুব গরম হয়ে যাচ্ছে করণীয় কি?",
            "ডিসপ্লেতে আলো আসছে না কিন্তু ভাইব্রেশন হয়",
            "ওয়াইফাই কানেক্ট হচ্ছে না কেন?",
            "ব্যাটারি খুব দ্রুত ড্রেন হচ্ছে কিভাবে সমাধান করব?",
            "ব্লু স্ক্রিন ইরর দেখাচ্ছে ল্যাপটপে",
            "চার্জ নিচ্ছে না ল্যাপটপ কি করা যায়?",
            "ক্যামেরা ওপেন হচ্ছে না মোবাইলে",
        ],
        sample_en=[
            "My laptop is not turning on what should I do?",
            "Phone is overheating rapidly troubleshooting steps",
            "No display on screen but phone vibrates",
            "WiFi not connecting to my device",
            "Battery draining very fast how to fix",
            "Laptop showing blue screen of death error",
            "Device is not charging troubleshooting guide",
            "Camera app crashing repeatedly on mobile",
        ],
        grounding_source="fix.knowledge.article[category='troubleshooting']",
        resolvable_by_ai=True,
    ),
    "knowledge.repair_guide": IntentDefinition(
        code="knowledge.repair_guide",
        name="Repair Procedure & Diagnostic Guide",
        name_bn="মেরামত পদ্ধতি ও ডায়াগনস্টিক নির্দেশিকা",
        description="Inquiries regarding repair steps, cleanroom diagnostics, and quality inspection workflows",
        sample_bn=[
            "মাদারবোর্ড রিপেয়ারের ধাপগুলো কি কি?",
            "স্ক্রিন পরিবর্তনের সময় কি কি চেক করা হয়?",
            "ওয়াটার ড্যামেজ ফোনের মেরামত কিভাবে করা হয়?",
            "রিপেয়ার প্রসেস কেমন হয়?",
            "১০০০ফিক্সে ল্যাপটপ সার্ভিসিং কিভাবে করা হয়?",
            "ওয়ার্কশপে ডিভাইস টেস্টিং কিভাবে করেন?",
        ],
        sample_en=[
            "What are the steps for motherboard repair?",
            "What is checked during screen replacement?",
            "How is water damaged phone repaired?",
            "Explain the repair process and diagnostic steps",
            "How is laptop servicing performed at 1000FiX?",
            "Quality inspection procedure during repair",
        ],
        grounding_source="fix.knowledge.article[category='repair_procedure']",
        resolvable_by_ai=True,
    ),
    "knowledge.warranty_policy": IntentDefinition(
        code="knowledge.warranty_policy",
        name="Warranty & ISO Standards Policy",
        name_bn="ওয়ারেন্টি নীতিমালা ও আইএসও মানদণ্ড",
        description="Warranty duration, claim coverage, and ISO 9001:2015 certified service guarantees",
        sample_bn=[
            "মেরামতের পর কি কোনো ওয়ারেন্টি আছে?",
            "স্পেয়ার পার্টসের ওয়ারেন্টি কতদিনের?",
            "১০০০ফিক্সের আইএসও সার্টিফিকেশন সম্পর্কে জানতে চাই",
            "ওয়ারেন্টি ক্লেইম করার নিয়ম কি?",
            "সার্ভিস ওয়ারেন্টির শর্তাবলী কি?",
            "রিপেয়ারের উপর কত মাস গ্যারান্টি দেন?",
        ],
        sample_en=[
            "Is there any warranty after repair?",
            "How long is the spare parts warranty?",
            "Tell me about 1000FiX ISO 9001:2015 certification",
            "How do I claim repair warranty?",
            "What are the terms of your service warranty?",
            "Official warranty period for replaced screens",
        ],
        grounding_source="fix.knowledge.article[category='policy']",
        resolvable_by_ai=True,
    ),
    "knowledge.maintenance_tips": IntentDefinition(
        code="knowledge.maintenance_tips",
        name="Preventative Maintenance Tips",
        name_bn="ডিভাইস সুরক্ষা ও প্রতিরোধমূলক রক্ষণাবেক্ষণ",
        description="Tips to extend device lifespan, heat dissipation, and battery health preservation",
        sample_bn=[
            "ল্যাপটপের ব্যাটারি লাইফ কিভাবে বাড়ানো যায়?",
            "এসি ভালো রাখার জন্য কিভাবে পরিষ্কার রাখব?",
            "স্মার্টফোনের স্টোরেজ ও পারফরম্যান্স ভালো রাখার টিপস",
            "বৃষ্টির দিনে গ্যাজেট সুরক্ষা কিভাবে করব?",
            "ডিভাইস রক্ষণাবেক্ষণের সঠিক নিয়ম কি?",
            "ল্যাপটপ গরম হওয়া কমানোর উপায় কি?",
        ],
        sample_en=[
            "How to increase laptop battery lifespan?",
            "Preventative maintenance tips for air conditioner",
            "Tips to keep smartphone fast and optimize storage",
            "How to protect electronics and gadgets from humidity",
            "What are best practices for device maintenance?",
            "How to prevent laptop from thermal overheating?",
        ],
        grounding_source="fix.knowledge.article[category='device_guide']",
        resolvable_by_ai=True,
    ),
}


# --- 2. Bengali & English Unicode Normalization & PII Scrubbing ---

BENGALI_PHONETIC_VARIANTS = [
    (r"\bবুজলাম\b", "বুঝলাম"),
    (r"\bবুজছি\b", "বুঝেছি"),
    (r"\bহবিনা\b", "হবে না"),
    (r"\bটাকা\b", "মূল্য"),
    (r"\bদাম\b", "মূল্য"),
    (r"\bখরচ\b", "মূল্য"),
    (r"\bকই\b", "কোথায়"),
    (r"\bকোথায়\b", "কোথায়"),
    (r"\bকবে\b", "কখন"),
    (r"\bকেমন\b", "অবস্থা"),
    (r"\bখবর\b", "অবস্থা"),
    (r"\bসারভিস\b", "সার্ভিস"),
    (r"\bঅরডার\b", "অর্ডার"),
    (r"\bওয়ারেন্টি\b", "ওয়ারেন্টি"),
]


def scrub_pii(text: str) -> str:
    """FLAW-32.2 / REQ-32.3: Masks bKash/Nagad/Rocket PINs, payment cards, and NIDs."""
    if not text:
        return ""
    # 1. Payment cards (13 to 16 digits)
    text = re.sub(r"\b(?:\d[ -]*?){13,16}\b", "****-****-****-****", text)
    # 2. bKash / Nagad / Rocket / generic PINs (e.g. পিন ১২৩৪৫, pin 1234, etc.)
    text = re.sub(
        r"(?i)(?:পিন|pin|password|পাছওয়ার্ড|পাসওয়ার্ড)\s*[:\s=]?\s*([0-9\u09e6-\u09ef]{4,6})",
        r"পিন *****",
        text,
    )
    # 3. National ID numbers (10 or 17 continuous digits)
    text = re.sub(r"\b(?:\d{10}|\d{17})\b", "NID-***MASKED***", text)
    return text


def normalize_text(text: str) -> str:
    """Normalizes Bengali and English text for robust intent classification.
    Strips zero-width joiners (ZWJ, ZWNJ), normalizes unicode NFKC, applies
    dialectical phonetic variants (FLAW-32.3), and removes punctuation.
    """
    if not text:
        return ""
    # Pre-scrub sensitive PII
    text = scrub_pii(text)
    # Unicode NFKC normalization
    text = unicodedata.normalize("NFKC", text)
    # Remove Zero-Width Non-Joiner (\u200C) and Zero-Width Joiner (\u200D)
    text = re.sub(r"[\u200B-\u200D\uFEFF]", "", text)
    # Lowercase English letters
    text = text.lower()
    # Apply Bengali phonetic/dialect normalizations
    for pattern, replacement in BENGALI_PHONETIC_VARIANTS:
        text = re.sub(pattern, replacement, text)
    # Replace punctuation with spaces
    text = re.sub(r"[?!.,;:\-—()\[\]{}'\"/।]+", " ", text)
    # Collapse multiple whitespaces
    return " ".join(text.split())


def tokenize(text: str) -> list[str]:
    """Tokenize normalized text into words and n-grams."""
    norm = normalize_text(text)
    return norm.split()


# --- 3. Intent Classification Core ---


@dataclass
class IntentMatchResult:
    matched_intent: str | None
    confidence: float
    utterance: str
    normalized_utterance: str
    grounding: str
    resolvable: bool
    requires_handoff: bool
    handoff_reason: str
    response_text_bn: str
    response_text_en: str
    requires_grounding: bool = False


# Customer-facing wording of each fix.service.order state (cd_service_order's
# SERVICE_ORDER_STATES). Authored bn/en (T08); used ONLY to describe the state
# actually read from the customer's order.
ORDER_STATE_TEXT: dict[str, tuple[str, str]] = {
    "draft": ("অর্ডারটি এখনো খসড়া অবস্থায় আছে", "the order is still in draft"),
    "intake": ("ডিভাইসটি গ্রহণ করা হয়েছে", "your device has been received at intake"),
    "diagnostic": ("ডিভাইসটির ডায়াগনস্টিক চলছে", "your device is being diagnosed"),
    "estimate_pending": ("খরচের এস্টিমেট প্রস্তুত করা হচ্ছে", "the cost estimate is being prepared"),
    "estimate_sent": ("খরচের এস্টিমেট আপনাকে পাঠানো হয়েছে", "the cost estimate has been sent to you"),
    "awaiting_approval": (
        "এস্টিমেটের জন্য আপনার অনুমোদনের অপেক্ষায় আছে",
        "it is awaiting your approval of the estimate",
    ),
    "approved": ("অনুমোদিত, মেরামতের জন্য সারিতে আছে", "approved and queued for repair"),
    "in_repair": ("মেরামতের কাজ চলছে", "it is currently being repaired"),
    "qc_pending": ("কোয়ালিটি পরীক্ষার অপেক্ষায় আছে", "it is waiting for quality inspection"),
    "qc_failed": (
        "কোয়ালিটি পরীক্ষায় উত্তীর্ণ হয়নি, পুনরায় মেরামত চলছে",
        "it did not pass quality inspection and is being reworked",
    ),
    "ready": ("সংগ্রহের জন্য প্রস্তুত", "it is ready for collection"),
    "delivered": ("ডেলিভারি সম্পন্ন হয়েছে", "it has been delivered"),
    "closed": ("অর্ডারটি বন্ধ করা হয়েছে", "the order is closed"),
    "cancelled": ("অর্ডারটি বাতিল করা হয়েছে", "the order was cancelled"),
}


class AssistantEngine:
    """Transactional NLU Classifier and Dialogue Manager."""

    def __init__(self, intents: dict[str, IntentDefinition] | None = None):
        self.intents = intents or INTENT_REGISTRY
        self._build_index()

    def _build_index(self):
        """Build normalized lexical lookup maps for fast matching.

        A sample that normalises to nothing (pure punctuation/whitespace) is
        skipped: as the empty string it is a substring of every utterance and
        would win the containment bonus for any input."""
        self.sample_map: list[tuple[str, str, str]] = []  # (intent_code, normalized_sample, lang)
        for code, defn in self.intents.items():
            for lang, samples in (("bn", defn.sample_bn), ("en", defn.sample_en)):
                for s in samples:
                    norm = normalize_text(s)
                    if norm:
                        self.sample_map.append((code, norm, lang))

    def classify_intent(self, utterance: str) -> IntentMatchResult:
        """Classify customer utterance against registered transactional intents."""
        norm_input = normalize_text(utterance)
        input_tokens = set(norm_input.split())

        if not norm_input:
            return IntentMatchResult(
                matched_intent=None,
                confidence=0.0,
                utterance=utterance,
                normalized_utterance=norm_input,
                grounding="",
                resolvable=False,
                requires_handoff=True,
                handoff_reason="empty_utterance",
                response_text_bn="দুঃখিত, আপনার বার্তাটি বুঝতে পারিনি। দয়া করে বিস্তারিত বলুন।",
                response_text_en="Sorry, could not understand your message. Please provide more details.",
            )

        best_intent = None
        best_score = 0.0

        for code, norm_sample, _ in self.sample_map:
            # Exact match
            if norm_input == norm_sample:
                best_score = 1.0
                best_intent = code
                break

            sample_tokens = set(norm_sample.split())
            intersection = input_tokens.intersection(sample_tokens)
            # norm_input is non-empty here, so input_tokens - and the union - never are
            union = input_tokens.union(sample_tokens)

            # Jaccard + Overlap coefficient (samples are never empty: see _build_index)
            jaccard = len(intersection) / len(union)
            overlap = len(intersection) / min(len(input_tokens), len(sample_tokens))
            combined = 0.4 * jaccard + 0.6 * overlap

            # Substring containment bonus
            if norm_sample in norm_input or norm_input in norm_sample:
                combined = max(combined, 0.85)

            if combined > best_score:
                best_score = combined
                best_intent = code

        # FLAW-32.1 / REQ-32.1: Three-tier confidence gating
        # Tier 1: High confidence (>= 0.75) -> Automated resolution / grounding
        # Tier 2: Disambiguation (0.50 <= confidence < 0.75) -> Disambiguation prompt
        # Tier 3: Low confidence (< 0.50) -> Immediate human agent handoff
        confidence = round(best_score, 4)
        if best_intent and confidence >= 0.75:
            defn = self.intents[best_intent]
            if defn.auto_handoff:
                return IntentMatchResult(
                    matched_intent=best_intent,
                    confidence=confidence,
                    utterance=utterance,
                    normalized_utterance=norm_input,
                    grounding=defn.grounding_source,
                    resolvable=False,
                    requires_handoff=True,
                    handoff_reason=defn.handoff_reason or "auto_handoff_intent",
                    response_text_bn="আপনার অনুরোধটি আমাদের প্রতিনিধির কাছে হস্তান্তর করা হচ্ছে। অনুগ্রহ করে লাইনে থাকুন।",
                    response_text_en="Transferring your request to a customer care representative. Please hold.",
                )
            elif defn.requires_grounding:
                # The engine has no ERP access: it never invents the answer.
                # Standalone it hands off; fix.conversation grounds it first.
                return IntentMatchResult(
                    matched_intent=best_intent,
                    confidence=confidence,
                    utterance=utterance,
                    normalized_utterance=norm_input,
                    grounding=defn.grounding_source,
                    resolvable=False,
                    requires_handoff=True,
                    handoff_reason="requires_erp_grounding",
                    response_text_bn="আপনার তথ্য যাচাই করতে একজন কাস্টমার কেয়ার প্রতিনিধির সাথে যুক্ত করছি।",
                    response_text_en="Connecting you with a customer care representative to check your records.",
                    requires_grounding=True,
                )
            else:
                authored = self._synthesize_grounded_response(best_intent)
                if authored is None:
                    # No authored answer: hand off rather than claim success.
                    return IntentMatchResult(
                        matched_intent=best_intent,
                        confidence=confidence,
                        utterance=utterance,
                        normalized_utterance=norm_input,
                        grounding=defn.grounding_source,
                        resolvable=False,
                        requires_handoff=True,
                        handoff_reason="no_authored_answer",
                        response_text_bn="আপনার প্রশ্নের নির্ভুল উত্তরের জন্য একজন কাস্টমার কেয়ার প্রতিনিধির সাথে যুক্ত করছি।",
                        response_text_en="Connecting you with a customer care specialist to assist you accurately.",
                    )
                resp_bn, resp_en = authored
                return IntentMatchResult(
                    matched_intent=best_intent,
                    confidence=confidence,
                    utterance=utterance,
                    normalized_utterance=norm_input,
                    grounding=defn.grounding_source,
                    resolvable=True,
                    requires_handoff=False,
                    handoff_reason="",
                    response_text_bn=resp_bn,
                    response_text_en=resp_en,
                )

        # Tier 2: Disambiguation (0.50 <= confidence < 0.75) (FLAW-32.1 / REQ-32.1)
        if best_intent and confidence >= 0.50:
            defn = self.intents[best_intent]
            return IntentMatchResult(
                matched_intent=best_intent,
                confidence=confidence,
                utterance=utterance,
                normalized_utterance=norm_input,
                grounding=defn.grounding_source,
                resolvable=False,
                requires_handoff=False,
                handoff_reason="disambiguation_required",
                response_text_bn="আপনি কি সার্ভিস সম্পর্কিত তথ্য জানতে চাচ্ছেন? স্পষ্ট করতে হ্যাঁ লিখুন অথবা বিস্তারিত বলুন।",
                response_text_en="Did you mean inquiry regarding service information? Please reply yes or clarify your request.",
            )

        # Tier 3: Low confidence (< 0.50) -> Immediate Human Agent Handoff (FLAW-32.1 / REQ-32.1)
        return IntentMatchResult(
            matched_intent=None,
            confidence=confidence,
            utterance=utterance,
            normalized_utterance=norm_input,
            grounding="",
            resolvable=False,
            requires_handoff=True,
            handoff_reason="low_intent_confidence",
            response_text_bn="আপনার প্রশ্নের নির্ভুল উত্তরের জন্য একজন কাস্টমার কেয়ার প্রতিনিধির সাথে যুক্ত করছি। অনুগ্রহ করে অপেক্ষা করুন।",
            response_text_en="Transferring your request to a live customer care representative for accurate assistance. Please hold.",
        )

    def _synthesize_grounded_response(self, intent_code: str) -> tuple[str, str] | None:
        """Authored general-guidance answers for the knowledge intents.

        Transactional intents (requires_grounding) never reach this: their
        answer depends on the customer's live records and is produced by
        fix.conversation._ground_intent_response or handed off."""
        responses: dict[str, tuple[str, str]] = {
            "knowledge.troubleshooting": (
                "প্রাথমিক ট্রাবলশুটিং: ডিভাইসটি ১০ সেকেন্ড পাওয়ার বাটন চেপে ধরে হার্ড রিবুট করুন। চার্জার কানেক্ট করে ১৫ মিনিট অপেক্ষা করুন। সমস্যা সমাধান না হলে আমাদের নিকটস্থ সেন্টারে ফ্রি ডায়াগনস্টিকের জন্য জমা দিন।",
                "Basic Troubleshooting: Perform a hard restart by holding the power button for 10 seconds. Connect an authentic charger for 15 minutes. If issue persists, bring it to any 1000FiX center for complimentary diagnostics.",
            ),
            "knowledge.repair_guide": (
                "১০০০ফিক্স রিপেয়ার প্রসেস: প্রথমে ISO 9001:2015 সার্টিফায়েড ল্যাবে সম্পূর্ণ ডায়াগনস্টিক, তারপর গ্রাহকের অনুমোদন সাপেক্ষে জেনুইন পার্টস প্রতিস্থাপন এবং মাল্টি-পয়েন্ট কোয়ালিটি চেক শেষে ডেলিভারি।",
                "1000FiX Repair Protocol: Complete diagnosis in an ISO 9001:2015 certified cleanroom lab, followed by customer cost approval, genuine OEM parts replacement, and multi-point QA inspection before delivery.",
            ),
            "knowledge.warranty_policy": (
                "ওয়ারেন্টি নীতিমালা: সকল অথেনটিক পার্টস ও রিপেয়ার সার্ভিসে ৯০ দিনের অফিসিয়াল ওয়ারেন্টি প্রদান করা হয়। ১০০০ফিক্স বাংলাদেশের একমাত্র ISO 9001:2015 সার্টিফায়েড আফটার-সেলস সার্ভিস প্রোভাইডার।",
                "Warranty Policy: All genuine replacement parts and repair work carry a 90-day official warranty. 1000FiX is Bangladesh's only ISO 9001:2015 certified after-sales service network.",
            ),
            "knowledge.maintenance_tips": (
                "রক্ষণাবেক্ষণ পরামর্শ: ডিভাইস ব্যাটারি ২০% এর নিচে ড্রেন হতে না দেওয়া, প্রতি ৬ মাসে ল্যাপটপের থার্মাল পেস্ট ও ফ্যান পরিষ্কার রাখা এবং আর্দ্রতা থেকে সুরক্ষিত রাখতে ড্রাই প্যাকেজিং ব্যবহার করুন।",
                "Preventative Maintenance: Maintain battery charge between 20%-80%, service laptop thermal paste and clean internal fans every 6 months, and keep devices away from excessive heat and humidity.",
            ),
        }
        # None = no authored answer: the caller hands off (never a generic
        # "request accepted" that claims an action nobody performed).
        return responses.get(intent_code)


# Global singleton engine
default_assistant_engine = AssistantEngine()
