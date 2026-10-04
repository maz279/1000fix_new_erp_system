"""cd_facility tests - P10-M05 (CD-M47-01)."""
import inspect
import unittest

from odoo.addons.cd_facility.models.fix_facility import FixSite


class TestFacility(unittest.TestCase):
    def test_site_types(self):
        src = inspect.getsource(FixSite)
        for st in ("branch", "warehouse", "office"):
            self.assertIn(st, src)

    def test_lease_tracked(self):
        self.assertTrue(hasattr(FixSite, "lease_start"))


if __name__ == "__main__":
    unittest.main()
