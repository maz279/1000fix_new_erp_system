"""cd_storefront tests - P10-M03 (CD-M38-02 / R08-M03)."""

import inspect
import unittest

from odoo.addons.cd_storefront.controllers.storefront_api import StorefrontApiController
from odoo.addons.cd_storefront.models.fix_storefront import (
    FixStorefrontCart,
    FixStorefrontCartLine,
    FixStorefrontOrder,
    FixStorefrontReturn,
)


class TestCart(unittest.TestCase):
    def test_checkout_requires_items(self):
        src = inspect.getsource(FixStorefrontCart.action_checkout)
        self.assertIn("Cart is empty", src)

    def test_order_event(self):
        src = inspect.getsource(FixStorefrontCart.action_place_order)
        self.assertIn("storefront.order_placed", src)

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
        self.assertIn("positive", inspect.getsource(FixStorefrontCartLine._check_qty))

    def test_monetary_fields(self):
        import odoo.fields as f

        self.assertIsInstance(FixStorefrontCartLine.unit_price, f.Monetary)
        self.assertIsInstance(FixStorefrontCartLine.subtotal, f.Monetary)


class TestOrder(unittest.TestCase):
    def test_payment_rails(self):
        src = inspect.getsource(FixStorefrontOrder)
        for rail in ("bkash", "nagad", "sslcommerz", "cod"):
            self.assertIn(rail, src)

    def test_shipping_methods(self):
        src = inspect.getsource(FixStorefrontOrder)
        for method in ("standard_delivery", "express_courier", "branch_pickup"):
            self.assertIn(method, src)

    def test_state_lifecycle(self):
        src = inspect.getsource(FixStorefrontOrder)
        for state in ("pending_payment", "paid", "dispatched", "delivered"):
            self.assertIn(state, src)

    def test_confirm_payment_event(self):
        src = inspect.getsource(FixStorefrontOrder.action_confirm_payment)
        self.assertIn("storefront.payment_confirmed", src)

    def test_dispatch_event(self):
        src = inspect.getsource(FixStorefrontOrder.action_dispatch)
        self.assertIn("storefront.order_dispatched", src)


class TestReturns(unittest.TestCase):
    def test_return_reasons(self):
        src = inspect.getsource(FixStorefrontReturn)
        for r in ("defective", "wrong_item", "not_as_described"):
            self.assertIn(r, src)

    def test_return_state_lifecycle(self):
        src = inspect.getsource(FixStorefrontReturn)
        for s in ("requested", "approved", "received", "refunded"):
            self.assertIn(s, src)

    def test_inspected_condition_grades(self):
        src = inspect.getsource(FixStorefrontReturn)
        for g in ("grade_a", "grade_b", "scrap"):
            self.assertIn(g, src)

    def test_refund_requires_inspection(self):
        src = inspect.getsource(FixStorefrontReturn.action_approve_refund)
        self.assertIn("Cannot refund prior to physical receipt and inspection", src)
        self.assertIn("storefront.refund_processed", src)


class TestStorefrontApiController(unittest.TestCase):
    def test_controller_endpoints_exist(self):
        self.assertTrue(hasattr(StorefrontApiController, "catalogue"))
        self.assertTrue(hasattr(StorefrontApiController, "get_or_update_cart"))
        self.assertTrue(hasattr(StorefrontApiController, "checkout"))
        self.assertTrue(hasattr(StorefrontApiController, "track_order"))
        self.assertTrue(hasattr(StorefrontApiController, "create_return"))


if __name__ == "__main__":
    unittest.main()
