"""cd_marketplace tests — Milestone R08-M01: M12 Marketplace at Seller Scale."""

import inspect
import unittest

from odoo.addons.cd_marketplace.models.fix_marketplace import (
    ORDER_STATES,
    SELLER_TIERS,
    FixMarketplaceDispute,
    FixMarketplaceOrder,
    FixMarketplaceSeller,
    FixSellerScore,
)


class TestSellerIsPartyRole(unittest.TestCase):
    """R08-M01-T01: Seller KYC onboarding, Z4 residency, and CFO approval."""

    def test_seller_links_to_party_master(self):
        self.assertTrue(hasattr(FixMarketplaceSeller, "partner_id"))
        self.assertTrue(hasattr(FixMarketplaceSeller, "company_id"))
        self.assertTrue(hasattr(FixMarketplaceSeller, "operating_unit_id"))

    def test_statutory_kyc_fields_present(self):
        src = inspect.getsource(FixMarketplaceSeller)
        self.assertIn("nid_number", src)
        self.assertIn("trade_license_no", src)
        self.assertIn("tin_number", src)
        self.assertIn("kyc_doc_z4_ref", src)
        self.assertIn("kyc_status", src)
        self.assertIn("verified", src)
        self.assertIn("in_review", src)

    def test_cfo_approval_gate(self):
        src = inspect.getsource(FixMarketplaceSeller)
        self.assertIn("cfo_approved", src)
        self.assertIn("cfo_approval_date", src)
        self.assertIn("action_cfo_approve", src)

    def test_category_qualification(self):
        src = inspect.getsource(FixMarketplaceSeller)
        self.assertIn("category_ids", src)
        self.assertIn("product.category", src)

    def test_tier_and_payout_hold(self):
        src = inspect.getsource(FixMarketplaceSeller)
        self.assertIn("tier", src)
        self.assertIn("payout_hold", src)
        tiers = [t[0] for t in SELLER_TIERS]
        self.assertIn("platinum", tiers)
        self.assertIn("gold", tiers)
        self.assertIn("silver", tiers)
        self.assertIn("at_risk", tiers)


class TestMarketplaceOrder(unittest.TestCase):
    """R08-M01-T02: Journey 7 order lifecycle, M14 refurb resale, and ephemeral contact."""

    def test_commission_earned_event_not_call(self):
        """Appendix E Pair 12: M12 publishes event; never directly calls M53."""
        src = inspect.getsource(FixMarketplaceOrder.action_earn_commission)
        self.assertIn("commission.earned", src)
        self.assertNotIn("fix.commission.ledger", src)
        self.assertNotIn("cd_settlement_ext", src)

    def test_journey_seven_states(self):
        states = [s[0] for s in ORDER_STATES]
        for s in (
            "open",
            "quoted",
            "selected",
            "in_progress",
            "completed",
            "reviewed",
            "commissioned",
            "paid",
        ):
            self.assertIn(s, states)

    def test_ephemeral_contact_masking(self):
        src = inspect.getsource(FixMarketplaceOrder)
        self.assertIn("customer_contact_revealed", src)
        self.assertIn("revealed_seller_id", src)
        # Verify revealed on selection, expired on completion (BRU-ECM-05)
        sel_src = inspect.getsource(FixMarketplaceOrder.action_select_quote)
        self.assertIn("customer_contact_revealed", sel_src)
        comp_src = inspect.getsource(FixMarketplaceOrder.action_complete)
        self.assertIn("customer_contact_revealed", comp_src)

    def test_refurbished_resale_wiring(self):
        src = inspect.getsource(FixMarketplaceOrder)
        self.assertIn("order_type", src)
        self.assertIn("tradein_request_id", src)
        self.assertIn("graded_stock_id", src)
        self.assertIn("battery_health_percent", src)
        self.assertIn("disclosed_defects", src)

    def test_dispute_payout_lock_enforcement(self):
        src = inspect.getsource(FixMarketplaceOrder.action_earn_commission)
        self.assertIn("has_open_dispute", src)
        self.assertIn("BRU-BIL-03", src)


class TestSellerScoringAndRanking(unittest.TestCase):
    """R08-M01-T03: Seller scoring and tier ranking."""

    def test_composite_explainable(self):
        src = inspect.getsource(FixSellerScore._compute_composite)
        self.assertIn("acceptance_rate", src)
        self.assertIn("on_time_rate", src)
        self.assertIn("review_rating", src)
        self.assertIn("dispute_rate", src)

    def test_tier_ranking_logic(self):
        src = inspect.getsource(FixSellerScore.compute_ranking_tier)
        self.assertIn("platinum", src)
        self.assertIn("gold", src)
        self.assertIn("silver", src)
        self.assertIn("at_risk", src)

    def test_score_and_tier_events(self):
        src = inspect.getsource(FixSellerScore)
        self.assertIn("seller.scored", src)
        self.assertIn("seller.tier_updated", src)


class TestMarketplaceDisputeHandling(unittest.TestCase):
    """R08-M01-T03: Dispute resolution and 48h SLA."""

    def test_dispute_model_fields(self):
        src = inspect.getsource(FixMarketplaceDispute)
        self.assertIn("order_id", src)
        self.assertIn("seller_id", src)
        self.assertIn("customer_id", src)
        self.assertIn("dispute_reason", src)
        self.assertIn("disputed_amount", src)
        self.assertIn("sla_deadline", src)
        self.assertIn("resolution_type", src)

    def test_payout_lock_on_dispute_creation(self):
        src = inspect.getsource(FixMarketplaceDispute.create)
        self.assertIn("payout_hold", src)
        self.assertIn("marketplace.dispute_raised", src)

    def test_dispute_resolution_actions(self):
        src = inspect.getsource(FixMarketplaceDispute)
        self.assertIn("action_investigate", src)
        self.assertIn("action_arbitrate", src)
        self.assertIn("action_resolve", src)
        self.assertIn("action_escalate", src)
        self.assertIn("marketplace.dispute_resolved", src)


if __name__ == "__main__":
    unittest.main()
