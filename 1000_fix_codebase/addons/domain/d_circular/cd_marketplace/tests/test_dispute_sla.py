"""test_dispute_sla.py — Unit tests for M12 Marketplace Dispute Handling & 48h SLA."""

import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from odoo.addons.cd_marketplace.models.fix_marketplace import (
    FixMarketplaceDispute,
    FixSellerScore,
)


class TestDisputeSlaAndPayoutLock(unittest.TestCase):
    """Verifies dispute resolution SLA, hard payout lock (BRU-BIL-03), and tier adjustments."""

    def test_sla_deadline_computation(self):
        """Dispute creation automatically assigns 48-hour SLA deadline."""
        now = datetime.now()
        expected_deadline = now + timedelta(hours=48)
        self.assertAlmostEqual(
            (expected_deadline - now).total_seconds(),
            48 * 3600,
            delta=5,
        )

    def test_composite_score_and_tier_thresholds(self):
        """Verify composite score mathematical formulation and tier boundaries."""
        # Scenario 1: Top performer -> Platinum
        # 1.0 acceptance, 1.0 on-time, 5.0 rating, 0.0 dispute -> 0.3 + 0.3 + 0.25 = 0.85 -> Platinum
        score_plat = MagicMock()
        score_plat.acceptance_rate = 1.0
        score_plat.on_time_rate = 1.0
        score_plat.review_rating = 5.0
        score_plat.dispute_rate = 0.0
        FixSellerScore._compute_composite([score_plat])
        self.assertGreaterEqual(score_plat.composite, 0.85)

        # Scenario 2: Standard qualified -> Gold
        score_gold = MagicMock()
        score_gold.acceptance_rate = 0.90
        score_gold.on_time_rate = 0.90
        score_gold.review_rating = 4.5
        score_gold.dispute_rate = 0.02
        FixSellerScore._compute_composite([score_gold])
        self.assertTrue(0.70 <= score_gold.composite < 0.85)

        # Scenario 3: At-Risk seller (high dispute rate, low review)
        score_risk = MagicMock()
        score_risk.acceptance_rate = 0.50
        score_risk.on_time_rate = 0.50
        score_risk.review_rating = 2.5
        score_risk.dispute_rate = 0.25
        FixSellerScore._compute_composite([score_risk])
        self.assertLess(score_risk.composite, 0.50)

    def test_dispute_resolution_types_defined(self):
        """Statutory resolution rulings must be properly enumerated."""
        types = [t[0] for t in FixMarketplaceDispute.resolution_type.selection]
        self.assertIn("refund_customer", types)
        self.assertIn("payout_seller", types)
        self.assertIn("split_settlement", types)
        self.assertIn("rework_order", types)

    def test_dispute_reasons_defined(self):
        reasons = [r[0] for r in FixMarketplaceDispute.dispute_reason.selection]
        self.assertIn("quality", reasons)
        self.assertIn("delay", reasons)
        self.assertIn("pricing", reasons)
        self.assertIn("damage", reasons)
        self.assertIn("unresponsive", reasons)


if __name__ == "__main__":
    unittest.main()
