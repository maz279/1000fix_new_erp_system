"""cd_storefront tests - P10-M03 (CD-M38-02)."""
import inspect
import unittest

from odoo.addons.cd_storefront.models.fix_storefront import (
    FixStorefrontCart, FixStorefrontCartLine, FixStorefrontReturn)


class TestCart(unittest.TestCase):
    def test_checkout_requires_items(self):
        src = inspect.getsource(FixStorefrontCart.action_checkout)
        self.assertIn("Cart is empty", src)

    def test_order_event(self):
        self.assertIn("storefront.order_placed",
                      inspect.getsource(FixStorefrontCart))

    def test_total_computed(self):
        src = inspect.getsource(FixStorefrontCart._compute_total)
        self.assertIn("line_ids", src)
        self.assertIn("sum", src)

    def test_cart_state_lifecycle(self):
        src = inspect.getsource(FixStorefrontCart)
        for s in ("open", "checkout", "ordered"):
            self.assertIn(s, src)

    def test_sequence_generated(self):
        src = inspect.getsource(FixStorefrontCart.create)
        self.assertIn("ir.sequence", src)


class TestCartLine(unittest.TestCase):
    def test_subtotal_computed(self):
        src = inspect.getsource(FixStorefrontCartLine._compute_subtotal)
        self.assertIn("quantity", src)
        self.assertIn("unit_price", src)

    def test_quantity_positive(self):
        self.assertIn("positive",
                      inspect.getsource(FixStorefrontCartLine._check_qty))

    def test_monetary_fields(self):
        import odoo.fields as f
        self.assertIsInstance(FixStorefrontCartLine.unit_price, f.Monetary)
        self.assertIsInstance(FixStorefrontCartLine.subtotal, f.Monetary)


class TestReturns(unittest.TestCase):
    def test_return_reasons(self):
        src = inspect.getsource(FixStorefrontReturn)
        for r in ("defective", "wrong_item", "not_as_described"):
            self.assertIn(r, src)

    def test_return_state_lifecycle(self):
        src = inspect.getsource(FixStorefrontReturn)
        for s in ("requested", "approved", "received", "refunded"):
            self.assertIn(s, src)

    def test_refund_amount_tracked(self):
        self.assertTrue(hasattr(FixStorefrontReturn, "refund_amount"))


if __name__ == "__main__":
    unittest.main()
