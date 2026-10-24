"""cd_partner tests - P10-M04 (CD-M40-01)."""

import inspect
import unittest

from odoo.addons.cd_partner.models.fix_partner import FixPartner, FixReferral


class TestPartnerIsPartyRole(unittest.TestCase):
    def test_links_to_party_master(self):
        self.assertTrue(hasattr(FixPartner, "partner_id"))

    def test_partner_types(self):
        src = inspect.getsource(FixPartner)
        for pt in ("referral", "reseller", "franchise", "alliance"):
            self.assertIn(pt, src)

    def test_commission_rate_tracked(self):
        self.assertTrue(hasattr(FixPartner, "commission_rate"))

    def test_territory_tracked(self):
        self.assertTrue(hasattr(FixPartner, "territory"))

    def test_contract_link(self):
        self.assertTrue(hasattr(FixPartner, "contract_id"))

    def test_onboard_event(self):
        self.assertIn("partner.onboarded", inspect.getsource(FixPartner))

    def test_state_lifecycle(self):
        src = inspect.getsource(FixPartner)
        for s in ("prospective", "onboarded", "suspended"):
            self.assertIn(s, src)


class TestReferral(unittest.TestCase):
    def test_commission_through_events(self):
        """M12<->M53 break: referral commissions publish events, never
        call the settlement engine directly."""
        src = inspect.getsource(FixReferral.action_earn_commission)
        self.assertIn("commission.earned", src)
        self.assertNotIn("fix.commission.ledger", src)

    def test_conversion_required(self):
        src = inspect.getsource(FixReferral.action_earn_commission)
        self.assertIn("Convert before", src)

    def test_conversion_event(self):
        self.assertIn("referral.converted", inspect.getsource(FixReferral))

    def test_referral_states(self):
        src = inspect.getsource(FixReferral)
        for s in ("submitted", "converted", "commissioned"):
            self.assertIn(s, src)

    def test_monetary_commission(self):
        import odoo.fields as f

        self.assertIsInstance(FixReferral.commission_amount, f.Monetary)


if __name__ == "__main__":
    unittest.main()
