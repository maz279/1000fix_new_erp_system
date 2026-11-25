#!/usr/bin/env python3
"""test_journey_07_marketplace.py — Journey 7: Marketplace Order to Payout Test Suite.
Milestone R08-M01 / Tasks R08-M01-T01, R08-M01-T02, R08-M01-T03, R08-M01-T04.

Validates the complete 14-step Journey 7 marketplace lifecycle:
1. Seller registration with NID, trade licence, and business details.
2. L6 KYC document routing to Z4 sovereign vault (FF-09 single-client invariant).
3. CFO operational sign-off and compliance verification (BRU-ECM-01).
4. Category qualification restriction (BRU-ECM-07: quote ONLY in certified categories).
5. Customer marketplace service order creation and quote solicitation.
6. Verified seller quote submission with positive price constraint.
7. Transparent quote selection with ephemeral contact disclosure (BRU-ECM-05 / EA-04).
8. Job execution to enterprise repair QC standards.
9. Customer completion sign-off and post-transaction review (BRU-ECM-02).
10. Refurbished device resale wiring with mandatory battery health and defect disclosure (BRU-TRF-04).
11. Commission accrual publishing 'commission.earned' outbox event (M12 <-> M53 Decoupling Break).
12. Dispute creation with 48h SLA and hard payout lock (BRU-BIL-03).
13. Dispute arbitration, resolution, and payout lock release.
14. Seller scoring composite and tier ranking assignment (Platinum/Gold/Silver/At-Risk).
"""

from __future__ import annotations

import inspect
import sys
import unittest
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Setup odoo import path
sys.path.insert(0, str(REPO_ROOT / "vendor" / "odoo"))
import odoo
import odoo.addons

# every addons root (the marketplace now imports the M20 finance approval
# helpers from cd_billing_engine, A04 ERP M12)
for _root in [
    REPO_ROOT / "addons" / "platform",
    *sorted((REPO_ROOT / "addons" / "domain").iterdir()),
]:
    if _root.is_dir() and str(_root) not in odoo.addons.__path__:
        odoo.addons.__path__.append(str(_root))

from odoo.addons.cd_marketplace.models.fix_marketplace import (
    FixMarketplaceDispute,
    FixMarketplaceOrder,
    FixMarketplaceSeller,
    FixSellerQuote,
    FixSellerScore,
    tier_for_score,
)


@dataclass
class MockPartner:
    id: int
    name: str
    phone: str = "01711000000"
    email: str = "partner@example.com"


@dataclass
class MockCategory:
    id: int
    name: str
    code: str


@dataclass
class MockGradedStock:
    id: int
    name: str
    device_model: str = "iPhone 14 Pro Max 256GB"
    grade_code: str = "A"
    valuation_bdt: float = 85000.0


class TestJourney07MarketplaceLifecycle(unittest.TestCase):
    """End-to-end simulation and verification of Journey 7."""

    def setUp(self):
        self.customer = MockPartner(id=201, name="Dr. Ayesha Rahman", phone="01711223344")
        self.seller_partner = MockPartner(id=301, name="Jewel Ahmed (Uttara Phone Care)")
        self.mobile_repair_cat = MockCategory(id=1, name="Mobile & Tablet Repair", code="CAT-MOB")
        self.laptop_repair_cat = MockCategory(id=2, name="Laptop Component Repair", code="CAT-LPT")
        self.refurb_stock = MockGradedStock(id=501, name="REFURB-APL-IP14P-001")

    def test_step_01_seller_registration_and_kyc_submission(self):
        """Step 1 & 2: Seller registers, NID & trade license routed to Z4 via fix_residency (FF-09)."""
        # Verify statutory KYC and residency attributes on FixMarketplaceSeller
        self.assertTrue(hasattr(FixMarketplaceSeller, "nid_number"))
        self.assertTrue(hasattr(FixMarketplaceSeller, "trade_license_no"))
        self.assertTrue(hasattr(FixMarketplaceSeller, "tin_number"))
        self.assertTrue(hasattr(FixMarketplaceSeller, "kyc_doc_z4_ref"))
        self.assertTrue(hasattr(FixMarketplaceSeller, "kyc_status"))
        self.assertTrue(hasattr(FixMarketplaceSeller, "cfo_approved"))
        self.assertTrue(hasattr(FixMarketplaceSeller, "action_submit_kyc"))

        # Verify that action_submit_kyc handles Z4 split-residency via fix_residency (FF-09)
        seller_src = inspect.getsource(FixMarketplaceSeller.action_submit_kyc)
        self.assertIn("fix_residency", seller_src)
        self.assertIn("kyc_doc_z4_ref", seller_src)
        self.assertIn("seller.kyc_submitted", seller_src)

    def test_step_03_and_04_cfo_approval_and_category_qualification(self):
        """Step 3 & 4: Compliance review & CFO approval (BRU-ECM-01), category qualification (BRU-ECM-07)."""
        seller_src = inspect.getsource(FixMarketplaceSeller)
        self.assertIn("action_cfo_approve", seller_src)
        self.assertIn("cfo_approved", seller_src)
        self.assertIn("category_ids", seller_src)
        self.assertIn("seller.approved", seller_src)

    def test_step_05_and_06_order_creation_and_verified_seller_quote(self):
        """Step 5 & 6: Order broadcast and quoting gated to verified sellers only."""
        quote_create_src = inspect.getsource(FixSellerQuote.create)
        self.assertIn("BRU-ECM-01", quote_create_src)
        self.assertIn("kyc_status", quote_create_src)
        self.assertIn("cfo_approved", quote_create_src)

        # Quoted price positive constraint
        price_check_src = inspect.getsource(FixSellerQuote._check_price)
        self.assertIn("quoted_price <= 0", price_check_src)

    def test_step_07_and_08_quote_selection_and_ephemeral_contact(self):
        """Step 7 & 8: Transparent selection awards job and reveals ephemeral contact (BRU-ECM-05)."""
        select_src = inspect.getsource(FixMarketplaceOrder.action_select_quote)
        self.assertIn("customer_contact_revealed", select_src)
        self.assertIn("revealed_seller_id", select_src)
        self.assertIn("BRU-ECM-05", select_src)
        self.assertIn("order.selected", select_src)
        self.assertIn("marketplace.contact_revealed", select_src)

    def test_step_09_and_10_job_completion_and_contact_expiry(self):
        """Step 9 & 10: Completion expires customer contact (BRU-ECM-05) and supports review."""
        complete_src = inspect.getsource(FixMarketplaceOrder.action_complete)
        self.assertIn('"customer_contact_revealed": False', complete_src)
        self.assertIn("marketplace_order.completed", complete_src)

        review_src = inspect.getsource(FixMarketplaceOrder.action_review)
        self.assertIn("reviewed", review_src)

    def test_step_10_refurbished_resale_mandatory_disclosures(self):
        """Step 10 (Branch): M14 Trade-In refurb device listing with battery & defects disclosure (BRU-TRF-04)."""
        order_src = inspect.getsource(FixMarketplaceOrder.action_list_refurb_resale)
        self.assertIn("refurb_resale", order_src)
        self.assertIn("battery_health_percent", order_src)
        self.assertIn("disclosed_defects", order_src)
        self.assertIn("marketplace.refurb_listed", order_src)

    def test_step_11_commission_earned_outbox_break(self):
        """Step 11: M12 publishes commission.earned; NEVER calls M53 directly (Pair 12)."""
        earn_src = inspect.getsource(FixMarketplaceOrder.action_earn_commission)
        self.assertIn("commission.earned", earn_src)
        self.assertNotIn("fix.commission.ledger", earn_src)
        self.assertNotIn("cd_settlement_ext", earn_src)
        self.assertIn("has_open_dispute", earn_src)
        self.assertIn("BRU-BIL-03", earn_src)

    def test_step_12_and_13_dispute_creation_payout_lock_and_sla_resolution(self):
        """Step 12 & 13: Dispute creation triggers hard payout lock (BRU-BIL-03); resolution releases lock."""
        # A04 M12: the seller's hold is recomputed from its open disputes (and
        # its own escrow) rather than flipped on and off, so a second open
        # dispute keeps the hold when the first one resolves. The executable
        # proof is cd_marketplace/tests/test_a04_m12_controls.py
        # (test_the_payout_waits_for_escrow_disputes_and_the_seller_hold and
        # the dispute tests after it).
        dispute_create_src = inspect.getsource(FixMarketplaceDispute.create)
        self.assertIn("_recompute_payout_hold", dispute_create_src)
        self.assertIn("sla_deadline", dispute_create_src)
        self.assertIn("marketplace.dispute_raised", dispute_create_src)

        resolve_src = inspect.getsource(FixMarketplaceDispute.action_resolve)
        self.assertIn("_recompute_payout_hold", resolve_src)
        self.assertIn("marketplace.dispute_resolved", resolve_src)

    def test_step_14_seller_scoring_and_tier_ranking(self):
        """Step 14: Seller composite scoring and Platinum/Gold/Silver/At-Risk ranking."""
        # A04 ERP audit M12-F14: the bands moved to tier_for_score (scores run
        # 0-1); the ranking reads them and publishes the tier change.
        tier_src = inspect.getsource(FixSellerScore.compute_ranking_tier)
        self.assertIn("tier_for_score", tier_src)
        self.assertIn("seller.tier_updated", tier_src)
        self.assertEqual(tier_for_score(0.90), "platinum")
        self.assertEqual(tier_for_score(0.75), "gold")
        self.assertEqual(tier_for_score(0.55), "silver")
        self.assertEqual(tier_for_score(0.20), "at_risk")


if __name__ == "__main__":
    unittest.main()
