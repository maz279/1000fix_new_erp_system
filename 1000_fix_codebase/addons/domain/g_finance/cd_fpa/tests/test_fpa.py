"""cd_fpa tests — P09 (CD-M54-01)."""
import unittest


class TestFpa(unittest.TestCase):
    def test_module_loads(self):
        """The module model classes are importable."""
        from odoo.addons.cd_fpa import models
        self.assertTrue(models)


if __name__ == "__main__":
    unittest.main()
