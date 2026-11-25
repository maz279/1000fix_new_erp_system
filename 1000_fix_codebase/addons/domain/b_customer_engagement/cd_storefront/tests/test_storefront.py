"""cd_storefront tests - P10-M03 (CD-M38-02 / R08-M03).

A04 audit C13 (2026-11-04): these were source-text checks (the method's code
contains "storefront.order_placed", the class mentions "refunded"...), which
passed while every control they named could be bypassed by a write. They are
now behaviour checks run as a plain internal user; the lifecycle controls
themselves are proved in test_a04_c2_c13_storefront.py.
"""

import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

from .test_a04_c2_c13_storefront import storefront_world

REFUSED = (UserError, ValidationError, AccessError)


@pytest.fixture
def clerk_env(odoo_env):
    env = odoo_env
    clerk = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "SF Unit Clerk",
                "login": "sf.unit.clerk@a04.test",
                # A04 ERP M38-F5: carts are captured by assisted sales staff
                "group_ids": [
                    (
                        6,
                        0,
                        [
                            env.ref("base.group_user").id,
                            env.ref("cd_storefront.group_fix_storefront_assisted_sales").id,
                        ],
                    )
                ],
            }
        )
    )
    customer = env["res.partner"].create({"name": "SF Unit Customer", "city": "Dhaka"})
    product = env["product.template"].create(
        {"name": "SF Unit Cable", "list_price": 300.0, "sale_ok": True}
    )
    # A04 ERP M38-F1: the M11 card (260.87 + 15% VAT = BDT 300.00)
    storefront_world(env, product, price=260.87)
    return env, clerk, customer, product


def _cart(env, clerk, customer, product=None, qty=1):
    cart = env["fix.storefront.cart"].with_user(clerk).create({"customer_id": customer.id})
    if product:
        env["fix.storefront.cart.line"].with_user(clerk).create(
            {"cart_id": cart.id, "product_id": product.id, "quantity": qty}
        )
    return cart


def test_checkout_requires_items(clerk_env):
    env, clerk, customer, _product = clerk_env
    cart = _cart(env, clerk, customer)
    with pytest.raises(UserError, match="Cart is empty"):
        cart.action_checkout()
    assert cart.state == "open"


def test_cart_total_and_line_subtotals_are_computed(clerk_env):
    env, clerk, customer, product = clerk_env
    cart = _cart(env, clerk, customer, product, qty=3)
    assert cart.line_ids.subtotal == 900.0 and cart.total == 900.0
    with pytest.raises(UserError, match="Quantity must be positive"), env.cr.savepoint():
        cart.line_ids.with_user(clerk).write({"quantity": 0})


def test_placing_an_order_publishes_it(clerk_env):
    env, clerk, customer, product = clerk_env
    order = _cart(env, clerk, customer, product).action_place_order(shipping_address="Road 2")
    assert order.sudo().state == "pending_payment"
    assert order.sudo().name.startswith("SF/")
    assert env["fix.event.outbox"].search_count(
        [("event_type", "=", "storefront.order_placed"), ("aggregate_id", "=", order.id)]
    )


def test_a_plain_user_runs_no_order_or_return_step(clerk_env):
    env, clerk, customer, product = clerk_env
    order = _cart(env, clerk, customer, product).action_place_order(shipping_address="Road 2")
    for method in ("action_dispatch", "action_deliver", "action_cancel"):
        with pytest.raises(REFUSED), env.cr.savepoint():
            getattr(order.with_user(clerk), method)()
    with pytest.raises(REFUSED), env.cr.savepoint():
        order.with_user(clerk).action_confirm_payment(payment_ref="TYPED-1")
    with pytest.raises(REFUSED), env.cr.savepoint():
        env["fix.storefront.return"].with_user(clerk).create(
            {"order_id": order.id, "customer_id": customer.id, "refund_amount": 1.0}
        )
