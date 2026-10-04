"""cd_talent tests — P09 (CD-M58-01)."""
import unittest


class TestTalent(unittest.TestCase):
    def test_module_loads(self):
        """The module model classes are importable."""
        from odoo.addons.cd_talent import models
        self.assertTrue(models)


if __name__ == "__main__":
    unittest.main()
