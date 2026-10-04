"""cd_data_case tests — P09 (CD-M06-01)."""
import unittest


class TestDatacase(unittest.TestCase):
    def test_module_loads(self):
        """The module model classes are importable."""
        from odoo.addons.cd_data_case import models
        self.assertTrue(models)


if __name__ == "__main__":
    unittest.main()
