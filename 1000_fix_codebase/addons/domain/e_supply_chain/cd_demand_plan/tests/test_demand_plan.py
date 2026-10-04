"""cd_demand_plan tests — P09 (CD-M43-01)."""
import unittest


class TestDemandplan(unittest.TestCase):
    def test_module_loads(self):
        """The module model classes are importable."""
        from odoo.addons.cd_demand_plan import models
        self.assertTrue(models)


if __name__ == "__main__":
    unittest.main()
