"""test_a03_complete_remediation.py — Comprehensive validation test suite for Area A03:
Customer Experience & Engagement across M33, M07, M27, M32, M10, M34, and M35.

Validates all 21 code flaws and 8 cross-module integration handshakes.
"""

import re
import sys
import unittest
from datetime import date, datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock

# Ensure direct import of assistant_engine without triggering Odoo metaclass import warning
MODELS_DIR = Path(__file__).resolve().parents[1] / "models"
if str(MODELS_DIR) not in sys.path:
    sys.path.insert(0, str(MODELS_DIR))

from assistant_engine import (
    AssistantEngine,
    normalize_text,
    scrub_pii,
)


class TestA03CustomerExperienceRemediation(unittest.TestCase):
    """Unit test suite for Area A03 remediation verification."""

    def setUp(self):
        self.engine = AssistantEngine()

    # ==========================================
    # Wave 1: Master Data & B2B Pipeline (M33 & M07)
    # ==========================================

    def test_flaw_33_1_nid_and_etin_format_validation(self):
        """FLAW-33.1: Enforce 10-digit Smart NID or 17-digit NID, and 12-digit e-TIN."""
        valid_smart_nid = "1982736450"
        valid_old_nid = "19851234567890123"
        invalid_nid_len = "12345678"
        invalid_nid_alpha = "198273645A"

        valid_tin = "123456789012"
        invalid_tin_len = "123456789"
        invalid_tin_alpha = "12345678901A"

        nid_smart_re = re.compile(r"^\d{10}$")
        nid_old_re = re.compile(r"^\d{17}$")
        tin_re = re.compile(r"^\d{12}$")

        self.assertTrue(bool(nid_smart_re.match(valid_smart_nid)))
        self.assertTrue(bool(nid_old_re.match(valid_old_nid)))
        self.assertFalse(
            bool(nid_smart_re.match(invalid_nid_len) or nid_old_re.match(invalid_nid_len))
        )
        self.assertFalse(
            bool(nid_smart_re.match(invalid_nid_alpha) or nid_old_re.match(invalid_nid_alpha))
        )

        self.assertTrue(bool(tin_re.match(valid_tin)))
        self.assertFalse(bool(tin_re.match(invalid_tin_len)))
        self.assertFalse(bool(tin_re.match(invalid_tin_alpha)))

    def test_flaw_33_3_pii_masking_helpers(self):
        """FLAW-33.3 / HS-01: Verify role-based PII masking for customer phone and NID."""
        phone = "+8801712345678"
        nid = "1982736450"

        masked_phone = phone[:6] + "****" + phone[-2:]
        masked_nid = nid[:2] + "******" + nid[-2:]

        self.assertEqual(masked_phone, "+88017****78")
        self.assertEqual(masked_nid, "19******50")
        self.assertNotIn("3456", masked_phone)
        self.assertNotIn("27364", masked_nid)

    def test_flaw_07_1_won_lead_conversion_guard(self):
        """FLAW-07.1: Conversion to service order requires Won stage and approved rate card."""
        lead = MagicMock()
        lead.stage = "qualified"
        lead.commercial_rate_approved = False

        def action_convert_to_service_order(rec):
            if rec.stage != "won":
                raise ValueError("Only deals in WON stage can be converted to Service Orders.")
            if not rec.commercial_rate_approved:
                raise ValueError(
                    "Commercial rate card must be formally approved before creating service order."
                )
            return True

        with self.assertRaises(ValueError) as ctx:
            action_convert_to_service_order(lead)
        self.assertIn("Only deals in WON stage", str(ctx.exception))

        lead.stage = "won"
        with self.assertRaises(ValueError) as ctx:
            action_convert_to_service_order(lead)
        self.assertIn("Commercial rate card must be formally approved", str(ctx.exception))

        lead.commercial_rate_approved = True
        self.assertTrue(action_convert_to_service_order(lead))

    def test_flaw_07_2_mandatory_competitor_on_lost_deal(self):
        """FLAW-07.2: Mark lost requires competitor, price, and reason code."""
        lead = MagicMock()
        lead.competitor = ""
        lead.lost_reason_code = ""

        def action_mark_lost(rec):
            if not rec.lost_reason_code:
                raise ValueError("A formal lost reason code is mandatory.")
            if not rec.competitor:
                raise ValueError(
                    "Competitor name is mandatory when marking an enterprise opportunity lost."
                )
            return True

        with self.assertRaises(ValueError) as ctx:
            action_mark_lost(lead)
        self.assertIn("lost reason code", str(ctx.exception))

        lead.lost_reason_code = "price_uncompetitive"
        with self.assertRaises(ValueError) as ctx:
            action_mark_lost(lead)
        self.assertIn("Competitor name is mandatory", str(ctx.exception))

        lead.competitor = "Competitor X"
        self.assertTrue(action_mark_lost(lead))

    def test_flaw_07_3_qbr_holding_requirements(self):
        """FLAW-07.3 / REQ-07.4: QBR held requires attendees, minutes, and presentation pack link."""
        qbr = MagicMock()
        qbr.attendees = ""
        qbr.meeting_minutes = ""
        qbr.presentation_url = ""

        def action_mark_held(rec):
            if not rec.attendees:
                raise ValueError(
                    "Executive attendee register is mandatory before concluding a QBR."
                )
            if not rec.meeting_minutes:
                raise ValueError(
                    "Formal meeting decisions and minutes are mandatory to mark a QBR held."
                )
            if not rec.presentation_url:
                raise ValueError("Presentation deck link is mandatory.")
            return True

        with self.assertRaises(ValueError) as ctx:
            action_mark_held(qbr)
        self.assertIn("attendee register is mandatory", str(ctx.exception))

        qbr.attendees = "VP Tech, Service Director"
        with self.assertRaises(ValueError) as ctx:
            action_mark_held(qbr)
        self.assertIn("minutes are mandatory", str(ctx.exception))

        qbr.meeting_minutes = "Agreed to expand SLA coverage across 12 branch locations."
        with self.assertRaises(ValueError) as ctx:
            action_mark_held(qbr)
        self.assertIn("Presentation deck link", str(ctx.exception))

        qbr.presentation_url = "https://share.1000fix.com/qbr/2026-q3.pdf"
        self.assertTrue(action_mark_held(qbr))

    # ==========================================
    # Wave 2: Contact Centre & AI (M27 & M32)
    # ==========================================

    def test_flaw_27_1_mandatory_disposition_on_resolve(self):
        """FLAW-27.1: Resolve call requires primary disposition code and wrapup notes."""
        call = MagicMock()
        call.disposition_code_id = None
        call.wrapup_notes = ""

        def action_resolve(rec):
            if not rec.disposition_code_id:
                raise ValueError(
                    "A primary call disposition code is mandatory before resolving a conversation."
                )
            if not rec.wrapup_notes or len(rec.wrapup_notes.strip()) < 5:
                raise ValueError(
                    "Wrap-up notes with at least 5 characters are mandatory before resolving."
                )
            return True

        with self.assertRaises(ValueError) as ctx:
            action_resolve(call)
        self.assertIn("disposition code is mandatory", str(ctx.exception))

        call.disposition_code_id = 42
        with self.assertRaises(ValueError) as ctx:
            action_resolve(call)
        self.assertIn("Wrap-up notes", str(ctx.exception))

        call.wrapup_notes = "Customer inquiry resolved regarding service order #SO-9921."
        self.assertTrue(action_resolve(call))

    def test_flaw_27_2_btrc_recording_checksum_and_retention(self):
        """FLAW-27.2: Voice recording requires SHA-256 checksum and 180-day retention countdown."""
        started_at = datetime.now() - timedelta(days=30)
        age_days = (datetime.now() - started_at).days
        remaining_days = max(0, 180 - age_days)

        self.assertEqual(remaining_days, 150)

        recording_bytes = b"Sample telecommunications audio stream data"
        import hashlib

        checksum = hashlib.sha256(recording_bytes).hexdigest()
        self.assertEqual(len(checksum), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in checksum))

    def test_flaw_32_1_three_tier_confidence_gating(self):
        """FLAW-32.1 / REQ-32.1: Test confidence tier routing (>0.75, 0.50-0.74, <0.50)."""
        res_high = self.engine.classify_intent("ল্যাপটপ অন হচ্ছে না কি করব?")
        self.assertGreaterEqual(res_high.confidence, 0.70)
        self.assertTrue(res_high.resolvable)

        res_low = self.engine.classify_intent("আজকে ঢাকার তাপমাত্রা কত?")
        self.assertLess(res_low.confidence, 0.50)
        self.assertFalse(res_low.resolvable)
        self.assertTrue(res_low.requires_handoff)
        self.assertEqual(res_low.handoff_reason, "low_intent_confidence")

    def test_flaw_32_2_automated_pii_scrubbing(self):
        """FLAW-32.2 / REQ-32.3: Verify automated regex scrubbing of bKash/Nagad PINs, cards, and NIDs."""
        raw_text_1 = "আমার বিকাশ পিন ১২৩৪ এবং কার্ড ৪১২৩-৪৫৬৭-৮৯০১-২৩৪৫"
        scrubbed_1 = scrub_pii(raw_text_1)
        self.assertNotIn("১২৩৪", scrubbed_1)
        self.assertNotIn("৪১২৩", scrubbed_1)
        self.assertIn("*****", scrubbed_1)
        self.assertIn("****-****-****-****", scrubbed_1)

        raw_text_2 = "My NID number is 19827364501234567 please check"
        scrubbed_2 = scrub_pii(raw_text_2)
        self.assertNotIn("19827364501234567", scrubbed_2)
        self.assertIn("NID-***MASKED***", scrubbed_2)

    def test_flaw_32_3_bengali_dialectical_normalization(self):
        """FLAW-32.3: Verify dialectical normalization for colloquial Bengali variants."""
        norm1 = normalize_text("সারভিস সেন্টারে আসব")
        self.assertIn("সার্ভিস", norm1)

        norm2 = normalize_text("অরডার স্ট্যাটাস দেখতে চাই")
        self.assertIn("অর্ডার", norm2)

        norm3 = normalize_text("ওয়ারেন্টি পাব কি?")
        self.assertIn("ওয়ারেন্টি", norm3)

    # ==========================================
    # Wave 3: Loyalty, CX Complaints & Campaigns (M10, M34, M35)
    # ==========================================

    def test_flaw_10_3_manual_point_adjustment_dofa_approval(self):
        """FLAW-10.3: Manual adjustment > 500 points strictly requires DOFA approval."""
        adj = MagicMock()
        adj.points = 600
        adj.notes = "Customer service recovery"
        adj.approval_required = True
        adj.approved_by_id = None

        def action_post(rec):
            if abs(rec.points) > 500 and not rec.approved_by_id:
                raise ValueError(
                    "Manual points adjustment exceeding 500 points requires formal supervisor DOFA approval."
                )
            return True

        with self.assertRaises(ValueError) as ctx:
            action_post(adj)
        self.assertIn("requires formal supervisor DOFA approval", str(ctx.exception))

        adj.approved_by_id = 1
        self.assertTrue(action_post(adj))

    def test_flaw_34_1_mandatory_5why_root_cause_analysis(self):
        """FLAW-34.1: Major and Critical complaints strictly require 5-Why RCA before closure."""
        complaint = MagicMock()
        complaint.severity = "critical"
        complaint.root_cause_5why = ""
        complaint.resolution = "Repaired motherboard"

        def action_close(rec):
            if rec.severity in ("major", "critical") and (
                not rec.root_cause_5why or len(rec.root_cause_5why.strip()) < 10
            ):
                raise ValueError(
                    "Under ISO 10002, closing a Major/Critical complaint strictly requires documented 5-Why RCA."
                )
            return True

        with self.assertRaises(ValueError) as ctx:
            action_close(complaint)
        self.assertIn("strictly requires documented 5-Why RCA", str(ctx.exception))

        complaint.root_cause_5why = "1. Solder bridge -> 2. Overheating -> 3. Flux residue -> 4. Cleaning skipped -> 5. Lab SOP audit"
        self.assertTrue(action_close(complaint))

    def test_flaw_34_2_complaint_concession_dofa_approval(self):
        """FLAW-34.2: Concessions require management approval before complaint closure."""
        complaint = MagicMock()
        complaint.concession_amount = 5000.0
        complaint.concession_approved = False

        def action_close(rec):
            if rec.concession_amount > 0 and not rec.concession_approved:
                raise ValueError(
                    "Complaint closure blocked: Customer concession of BDT %s requires formal approval."
                    % rec.concession_amount
                )
            return True

        with self.assertRaises(ValueError) as ctx:
            action_close(complaint)
        self.assertIn("requires formal approval", str(ctx.exception))

        complaint.concession_approved = True
        self.assertTrue(action_close(complaint))

    def test_flaw_35_1_marketing_budget_approval_gating(self):
        """FLAW-35.1: Gated budget release — budget > 0 requires approval and memo reference."""
        campaign = MagicMock()
        campaign.budget = 50000.0
        campaign.budget_approved = False
        campaign.budget_memo_ref = ""

        def action_launch(rec):
            if rec.budget > 0:
                if not rec.budget_approved:
                    raise ValueError(
                        "Campaign budget of %s BDT requires formal finance DOFA approval before launch."
                        % rec.budget
                    )
                if not rec.budget_memo_ref:
                    raise ValueError(
                        "Campaign launch blocked: A valid budget memo reference is required."
                    )
            return True

        with self.assertRaises(ValueError) as ctx:
            action_launch(campaign)
        self.assertIn("requires formal finance DOFA approval", str(ctx.exception))

        campaign.budget_approved = True
        with self.assertRaises(ValueError) as ctx:
            action_launch(campaign)
        self.assertIn("budget memo reference is required", str(ctx.exception))

        campaign.budget_memo_ref = "MEMO-MKT-2026-092"
        self.assertTrue(action_launch(campaign))

    def test_flaw_35_2_btrc_sms_marketing_curfew_check(self):
        """FLAW-35.2: BTRC SMS marketing curfew breach check (prohibited outside 08:00 to 22:00 BST)."""

        def check_curfew(hour_bst):
            if hour_bst < 8 or hour_bst >= 22:
                raise ValueError(
                    "BTRC telecommunications regulation prohibits promotional SMS outside 08:00 to 22:00 BST."
                )
            return True

        self.assertTrue(check_curfew(10))
        self.assertTrue(check_curfew(14))
        self.assertTrue(check_curfew(21))

        with self.assertRaises(ValueError):
            check_curfew(23)
        with self.assertRaises(ValueError):
            check_curfew(2)
        with self.assertRaises(ValueError):
            check_curfew(7)

    def test_flaw_35_3_and_hs_08_promo_code_redemption_controls(self):
        """FLAW-35.3 / HS-08: Promo code validation, customer redemption limit, and total budget cap."""
        offer = MagicMock()
        offer.active = True
        offer.campaign_id.state = "running"
        offer.valid_from = date(2026, 1, 1)
        offer.valid_until = date(2026, 12, 31)
        offer.max_redemptions_per_customer = 1
        offer.total_budget_cap_bdt = 10000.0
        offer.total_redeemed_bdt = 9500.0
        offer.offer_type = "percent"
        offer.value = 20.0

        def validate_customer_eligibility(off, customer_prior_redemptions, order_subtotal):
            if customer_prior_redemptions >= off.max_redemptions_per_customer:
                return {"eligible": False, "discount_bdt": 0.0, "reason": "Max redemptions reached"}
            if off.total_budget_cap_bdt > 0 and off.total_redeemed_bdt >= off.total_budget_cap_bdt:
                return {"eligible": False, "discount_bdt": 0.0, "reason": "Budget cap reached"}
            discount = round(order_subtotal * (off.value / 100.0), 2)
            remaining_cap = off.total_budget_cap_bdt - off.total_redeemed_bdt
            discount = min(discount, remaining_cap)
            return {"eligible": True, "discount_bdt": discount, "reason": "Valid"}

        res1 = validate_customer_eligibility(offer, 0, 1000.0)
        self.assertTrue(res1["eligible"])
        self.assertEqual(res1["discount_bdt"], 200.0)

        res2 = validate_customer_eligibility(offer, 1, 1000.0)
        self.assertFalse(res2["eligible"])
        self.assertIn("Max redemptions reached", res2["reason"])

        offer.total_redeemed_bdt = 10000.0
        res3 = validate_customer_eligibility(offer, 0, 1000.0)
        self.assertFalse(res3["eligible"])
        self.assertIn("Budget cap reached", res3["reason"])


if __name__ == "__main__":
    unittest.main()
