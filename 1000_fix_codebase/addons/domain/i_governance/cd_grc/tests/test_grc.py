"""cd_grc tests — P09 (CD-M60-01)."""
import unittest


class TestGrc(unittest.TestCase):
    def test_module_loads(self):
        """The module model classes are importable."""
        from odoo.addons.cd_grc import models
        self.assertTrue(models)


if __name__ == "__main__":
    unittest.main()
