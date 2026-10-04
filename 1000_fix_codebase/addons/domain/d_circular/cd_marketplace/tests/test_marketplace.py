"""cd_marketplace tests - P10-M01 (CD-M12-01)."""
import inspect
import unittest

from odoo.addons.cd_marketplace.models.fix_marketplace import (
    FixMarketplaceOrder, FixMarketplaceSeller, FixSellerQuote, FixSellerScore)


class TestSellerIsPartyRole(unittest.TestCase):
    def test_seller_links_to_party_master(self):
        self.assertTrue(hasattr(FixMarketplaceSeller, "partner_id"))

    def test_kyc_status_tracked(self):
        src = inspect.getsource(FixMarketplaceSeller)
        self.assertIn("kyc_status", src)
        self.assertIn("verified", src)


class TestMarketplaceOrder(unittest.TestCase):
    def test_commission_earned_event_not_call(self):
        src = inspect.getsource(FixMarketplaceOrder.action_earn_commission)
        self.assertIn("commission.earned", src)
        self.assertNotIn("fix.commission.ledger", src)

    def test_selection_requires_quoted_state(self):
        src = inspect.getsource(FixMarketplaceOrder.action_select_quote)
        self.assertIn("Quotes Received", src)

    def test_journey_seven_states(self):
        from odoo.addons.cd_marketplace.models.fix_marketplace import ORDER_STATES
        states = [s[0] for s in ORDER_STATES]
        for s in ("open", "quoted", "selected", "completed", "reviewed",
                  "commissioned", "paid"):
            self.assertIn(s, states)


class TestSellerScoring(unittest.TestCase):
    def test_composite_explainable(self):
        src = inspect.getsource(FixSellerScore._compute_composite)
        self.assertIn("acceptance_rate", src)
        self.assertIn("on_time_rate", src)
        self.assertIn("dispute_rate", src)

    def test_score_event(self):
        self.assertIn("seller.scored", inspect.getsource(FixSellerScore))


if __name__ == "__main__":
    unittest.main()
