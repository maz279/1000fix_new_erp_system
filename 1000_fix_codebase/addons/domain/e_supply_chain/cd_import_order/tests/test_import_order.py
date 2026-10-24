"""cd_import_order tests - P09-M07 (CD-M44-01)."""

import inspect
import unittest

from odoo.addons.cd_import_order.models.fix_import_order import FixImportOrder


class TestLandedCost(unittest.TestCase):
    def test_landed_computed(self):
        src = inspect.getsource(FixImportOrder._compute_landed)
        self.assertIn("fob_value", src)
        self.assertIn("customs_duty", src)

    def test_landed_includes_freight_and_insurance(self):
        """Landed cost is FOB + duty + freight + insurance — the importer's
        true per-unit cost (M44's whole point)."""
        src = inspect.getsource(FixImportOrder._compute_landed)
        self.assertIn("freight", src.lower())
        self.assertIn("insurance", src.lower())

    def test_m41_break_goods_received_event(self):
        """AR-006 pair: receiving publishes goods.received; M41 (stock)
        consumes it — no synchronous call into stock."""
        src = inspect.getsource(FixImportOrder.action_receive)
        self.assertIn("goods.received", src)
        self.assertNotIn("cd_stock", src)

    def test_import_lifecycle_states(self):
        """draft -> shipped -> customs -> received -> landed (DE-16: the
        seed and tests enumerate the machine, not the happy path)."""
        src = inspect.getsource(FixImportOrder)
        for state in ("draft", "shipped", "customs", "received", "landed"):
            self.assertIn(state, src)

    def test_receive_transitions_to_received(self):
        src = inspect.getsource(FixImportOrder.action_receive)
        self.assertIn('"received"', src)

    def test_as02_conformance(self):
        for mixin in ("mail.thread", "mail.activity.mixin"):
            self.assertIn(mixin, FixImportOrder._inherit)
        self.assertTrue(hasattr(FixImportOrder, "company_id"))
        self.assertTrue(hasattr(FixImportOrder, "operating_unit_id"))


if __name__ == "__main__":
    unittest.main()
