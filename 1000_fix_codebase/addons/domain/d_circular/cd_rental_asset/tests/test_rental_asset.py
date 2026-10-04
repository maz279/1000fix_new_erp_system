"""cd_rental_asset tests — P09 (CD-M13-01)."""
import unittest


class TestRentalasset(unittest.TestCase):
    def test_module_loads(self):
        """The module model classes are importable."""
        from odoo.addons.cd_rental_asset import models
        self.assertTrue(models)


if __name__ == "__main__":
    unittest.main()
