"""cd_import_order tests — P09 (CD-M44-01)."""
import unittest


class TestImportorder(unittest.TestCase):
    def test_module_loads(self):
        """The module model classes are importable."""
        from odoo.addons.cd_import_order import models
        self.assertTrue(models)


if __name__ == "__main__":
    unittest.main()
