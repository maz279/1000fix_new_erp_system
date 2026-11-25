"""Unit and sandbox pact compliance tests for INT-035 and INT-037."""

import unittest

from libs.py.trust_services.int035_trust import (
    TradeLicenseClient,
    TradeLicenseVerificationRequest,
)
from libs.py.trust_services.int037_ads import (
    AdDeliveryEngine,
)


class TestTradeLicenseClientINT035(unittest.TestCase):
    def setUp(self):
        self.client = TradeLicenseClient(sandbox=True)

    def test_valid_trade_license_verification(self):
        req = TradeLicenseVerificationRequest(
            license_number="TRAD/DNCC/2026/049182",
            entity_name="Apex Electronics Ltd",
            entity_type="private_limited",
            city_corporation="DNCC",
            tin_number="489201948192",
            bin_number="001294819201",
        )
        res = self.client.verify_license(req)
        self.assertTrue(res.is_valid)
        self.assertEqual(res.status, "valid")
        self.assertEqual(res.issued_to, "Apex Electronics Ltd")
        self.assertIn("IT_EQUIPMENT", res.permitted_categories)
        self.assertTrue(res.tin_matched)
        self.assertTrue(res.verification_id.startswith("VRF-"))

    def test_expired_trade_license(self):
        req = TradeLicenseVerificationRequest(
            license_number="TRAD/EXP/2023/00192",
            entity_name="Lapsed Merchant Co",
            entity_type="sole_proprietorship",
            city_corporation="DSCC",
        )
        res = self.client.verify_license(req)
        self.assertFalse(res.is_valid)
        self.assertEqual(res.status, "expired")
        self.assertIn("expired", res.remarks.lower())

    def test_suspended_trade_license(self):
        req = TradeLicenseVerificationRequest(
            license_number="TRAD/SUSP/2024/991",
            entity_name="Suspended Retail Ltd",
            entity_type="partnership",
            city_corporation="CCC",
        )
        res = self.client.verify_license(req)
        self.assertFalse(res.is_valid)
        self.assertEqual(res.status, "suspended")

    def test_not_found_trade_license(self):
        req = TradeLicenseVerificationRequest(
            license_number="TRAD/NOTFOUND/000",
            entity_name="Ghost Co",
            entity_type="sole_proprietorship",
            city_corporation="DNCC",
        )
        res = self.client.verify_license(req)
        self.assertFalse(res.is_valid)
        self.assertEqual(res.status, "not_found")

    def test_invalid_format(self):
        req = TradeLicenseVerificationRequest(
            license_number="123",
            entity_name="Short",
            entity_type="sole_proprietorship",
            city_corporation="DNCC",
        )
        res = self.client.verify_license(req)
        self.assertFalse(res.is_valid)
        self.assertEqual(res.status, "invalid_format")


class TestAdDeliveryEngineINT037(unittest.TestCase):
    def setUp(self):
        self.engine = AdDeliveryEngine()

    def test_create_and_serve_campaign(self):
        camp = self.engine.create_campaign(
            seller_id=42,
            title="Specialist Laptop Motherboard Repair 20% Off",
            target_categories=["IT_EQUIPMENT", "LAPTOPS"],
            placement="home_hero_banner",
            budget_bdt=1000.0,
            cpc_rate_bdt=10.0,
            cpm_rate_bdt=50.0,
            campaign_id="CMP-TEST-001",
        )
        self.assertEqual(camp.state, "active")
        self.assertEqual(camp.remaining_budget, 1000.0)

        # Serve ads
        ads = self.engine.serve_ads("home_hero_banner", category="IT_EQUIPMENT")
        self.assertEqual(len(ads), 1)
        self.assertEqual(ads[0]["campaign_id"], "CMP-TEST-001")

        # Wrong category should not match
        no_ads = self.engine.serve_ads("home_hero_banner", category="FURNITURE")
        self.assertEqual(len(no_ads), 0)

    def test_impression_and_click_tracking(self):
        camp = self.engine.create_campaign(
            seller_id=10,
            title="Phone Screen Replacement",
            target_categories=["MOBILE_DEVICES"],
            placement="search_sponsored",
            budget_bdt=100.0,
            cpc_rate_bdt=5.0,
            cpm_rate_bdt=50.0,
            campaign_id="CMP-TEST-002",
        )
        # Record 10 impressions
        for _ in range(10):
            res = self.engine.record_impression("CMP-TEST-002")
            self.assertEqual(res["status"], "recorded")

        self.assertEqual(camp.impressions, 10)
        self.assertGreater(camp.spent_bdt, 0.0)

        # Record 2 clicks
        res = self.engine.record_click("CMP-TEST-002")
        self.assertEqual(res["clicks"], 1)
        res = self.engine.record_click("CMP-TEST-002")
        self.assertEqual(res["clicks"], 2)
        self.assertEqual(camp.clicks, 2)
        self.assertEqual(camp.ctr, 20.0)  # 2 clicks / 10 impressions = 20%

        # Record 1 conversion
        res = self.engine.record_conversion("CMP-TEST-002")
        self.assertEqual(res["conversions"], 1)

        # Get analytics
        analytics = self.engine.get_analytics("CMP-TEST-002")
        self.assertEqual(analytics["impressions"], 10)
        self.assertEqual(analytics["clicks"], 2)
        self.assertEqual(analytics["conversions"], 1)
        self.assertEqual(analytics["state"], "active")

    def test_budget_exhaustion(self):
        camp = self.engine.create_campaign(
            seller_id=10,
            title="Small Budget Boost",
            target_categories=["ALL"],
            placement="product_detail_boost",
            budget_bdt=10.0,
            cpc_rate_bdt=10.0,
            cpm_rate_bdt=50.0,
            campaign_id="CMP-TEST-EXHAUST",
        )
        # 1 click consumes full 10 BDT
        res = self.engine.record_click("CMP-TEST-EXHAUST")
        self.assertEqual(res["state"], "exhausted")
        self.assertEqual(camp.remaining_budget, 0.0)

        # Further clicks should report not active
        res2 = self.engine.record_click("CMP-TEST-EXHAUST")
        self.assertEqual(res2["error"], "campaign_not_active")


if __name__ == "__main__":
    unittest.main()
