"""cd_facility tests - P10-M05 (CD-M47-01)."""
import inspect
import unittest

from odoo.addons.cd_facility.models.fix_facility import (
    FixFacilityWorkOrder, FixSite)


class TestFacility(unittest.TestCase):
    def test_site_types(self):
        src = inspect.getsource(FixSite)
        for st in ("branch", "warehouse", "office", "data_centre"):
            self.assertIn(st, src)

    def test_lease_tracked(self):
        self.assertTrue(hasattr(FixSite, "lease_start"))
        self.assertTrue(hasattr(FixSite, "lease_end"))
        self.assertTrue(hasattr(FixSite, "monthly_rent"))

    def test_floor_area_tracked(self):
        self.assertTrue(hasattr(FixSite, "floor_area_sqm"))

    def test_links_to_branch(self):
        self.assertTrue(hasattr(FixSite, "branch_id"))

    def test_assets_link_event(self):
        self.assertIn("site.assets_linked",
                      inspect.getsource(FixSite))


class TestFacilityWorkOrder(unittest.TestCase):
    def test_work_types(self):
        src = inspect.getsource(FixFacilityWorkOrder)
        for wt in ("maintenance", "repair", "upgrade", "inspection"):
            self.assertIn(wt, src)

    def test_links_to_site(self):
        self.assertTrue(hasattr(FixFacilityWorkOrder, "site_id"))

    def test_cost_tracked(self):
        self.assertTrue(hasattr(FixFacilityWorkOrder, "estimated_cost"))

    def test_state_lifecycle(self):
        src = inspect.getsource(FixFacilityWorkOrder)
        for s in ("draft", "scheduled", "in_progress", "completed"):
            self.assertIn(s, src)


if __name__ == "__main__":
    unittest.main()
