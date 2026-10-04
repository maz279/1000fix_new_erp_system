"""cd_itsm tests — P09 (CD-M66-01)."""
import unittest


class TestItsm(unittest.TestCase):
    def test_module_loads(self):
        """The module model classes are importable."""
        from odoo.addons.cd_itsm import models
        self.assertTrue(models)


if __name__ == "__main__":
    unittest.main()
