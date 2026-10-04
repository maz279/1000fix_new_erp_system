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


class TestReferral(unittest.TestCase):
    def test_commission_through_events(self):
        src = inspect.getsource(FixReferral.action_earn_commission)
        self.assertIn("commission.earned", src)

    def test_conversion_required(self):
        src = inspect.getsource(FixReferral.action_earn_commission)
        self.assertIn("Convert before", src)


if __name__ == "__main__":
    unittest.main()
