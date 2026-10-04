"""cd_tradein tests — P09 (CD-M14-01)."""
import unittest


class TestTradein(unittest.TestCase):
    def test_module_loads(self):
        """The module model classes are importable."""
        from odoo.addons.cd_tradein import models
        self.assertTrue(models)


if __name__ == "__main__":
    unittest.main()
