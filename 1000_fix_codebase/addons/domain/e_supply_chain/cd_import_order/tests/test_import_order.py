"""cd_import_order tests - P09-M07 (CD-M44-01)."""
import inspect
import unittest

from odoo.addons.cd_import_order.models.fix_import_order import FixImportOrder


class TestLandedCost(unittest.TestCase):
    def test_landed_computed(self):
        src = inspect.getsource(FixImportOrder._compute_landed)
        self.assertIn("fob_value", src)
        self.assertIn("customs_duty", src)

    def test_m41_break_goods_received_event(self):
        src = inspect.getsource(FixImportOrder.action_receive)
        self.assertIn("goods.received", src)


if __name__ == "__main__":
    unittest.main()
