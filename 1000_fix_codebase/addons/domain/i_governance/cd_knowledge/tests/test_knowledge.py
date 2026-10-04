"""cd_knowledge tests — P09 (CD-M61-01)."""
import unittest


class TestKnowledge(unittest.TestCase):
    def test_module_loads(self):
        """The module model classes are importable."""
        from odoo.addons.cd_knowledge import models
        self.assertTrue(models)


if __name__ == "__main__":
    unittest.main()
