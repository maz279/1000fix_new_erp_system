"""cd_storefront tests - P10-M03 (CD-M38-02)."""
import inspect
import unittest

from odoo.addons.cd_storefront.models.fix_storefront import (
    FixStorefrontCart, FixStorefrontCartLine)


class TestCart(unittest.TestCase):
    def test_checkout_requires_items(self):
        src = inspect.getsource(FixStorefrontCart.action_checkout)
        self.assertIn("Cart is empty", src)

    def test_order_event(self):
        self.assertIn("storefront.order_placed",
                      inspect.getsource(FixStorefrontCart))


class TestCartLine(unittest.TestCase):
    def test_subtotal_computed(self):
        src = inspect.getsource(FixStorefrontCartLine._compute_subtotal)
        self.assertIn("quantity", src)

    def test_quantity_positive(self):
        self.assertIn("positive",
                      inspect.getsource(FixStorefrontCartLine._check_qty))


if __name__ == "__main__":
    unittest.main()
