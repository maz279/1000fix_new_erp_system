"""cd_hse tests — P09 (CD-M59-01)."""
import unittest


class TestHse(unittest.TestCase):
    def test_module_loads(self):
        """The module model classes are importable."""
        from odoo.addons.cd_hse import models
        self.assertTrue(models)


if __name__ == "__main__":
    unittest.main()
