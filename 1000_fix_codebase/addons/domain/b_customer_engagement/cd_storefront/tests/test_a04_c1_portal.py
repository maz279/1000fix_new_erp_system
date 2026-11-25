"""A04 audit C1 (M38-3): a portal customer cannot price their own cart.

A portal user writing through JSON-RPC set a BDT 2,500 cart line to BDT 1 and
the order was placed at BDT 1; they could also rewrite another customer's
line, because the lines had no record rule. Every storefront flow runs
through the superuser controller, so the portal needs read access only, and
the order is always priced from the catalogue at checkout.
"""

import pytest
from odoo.exceptions import AccessError, UserError

from .test_a04_c2_c13_storefront import storefront_world

REFUSED = (AccessError, UserError)


@pytest.fixture
def shop(odoo_env):
    env = odoo_env
    product = env["product.template"].create({"name": "C1 Charger", "list_price": 2500.0})
    # A04 ERP M38-F1: the M11 storefront price (2,173.91 + 15% VAT = 2,500.00)
    storefront_world(env, product)

    def customer(n):
        partner = env["res.partner"].create({"name": "C1 Customer %d" % n})
        user = (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "C1 Portal %d" % n,
                    "login": "c1.portal.%d@a04.test" % n,
                    "partner_id": partner.id,
                    "group_ids": [(6, 0, [env.ref("base.group_portal").id])],
                }
            )
        )
        cart = env["fix.storefront.cart"].create({"customer_id": partner.id})
        line = env["fix.storefront.cart.line"].create(
            {"cart_id": cart.id, "product_id": product.id, "quantity": 1, "unit_price": 2500.0}
        )
        return user, cart, line

    return env, product, customer


def test_a_portal_customer_cannot_reprice_their_own_line(shop):
    env, _product, customer = shop
    user, _cart, line = customer(1)
    with pytest.raises(REFUSED):
        line.with_user(user).write({"unit_price": 1.0})
    assert line.unit_price == 2500.0


def test_a_portal_customer_cannot_see_or_touch_another_customers_line(shop):
    env, _product, customer = shop
    attacker, _c1, _l1 = customer(2)
    _victim, _c2, victim_line = customer(3)
    Lines = env["fix.storefront.cart.line"].with_user(attacker)
    assert victim_line.id not in Lines.search([]).ids
    with pytest.raises(REFUSED):
        victim_line.with_user(attacker).write({"unit_price": 1.0})


def test_a_portal_customer_cannot_create_lines_or_orders_directly(shop):
    env, product, customer = shop
    user, cart, _line = customer(4)
    with pytest.raises(REFUSED):
        env["fix.storefront.cart.line"].with_user(user).create(
            {"cart_id": cart.id, "product_id": product.id, "quantity": 1, "unit_price": 1.0}
        )
    with pytest.raises(REFUSED):
        env["fix.storefront.order"].with_user(user).create(
            {"customer_id": user.partner_id.id, "total_amount": 1.0}
        )


def test_an_internal_user_cannot_hand_price_a_line_either(shop, odoo_env):
    env, _product, customer = shop
    _user, _cart, line = customer(5)
    clerk = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "C1 Clerk",
                "login": "c1.clerk@a04.test",
                "group_ids": [(6, 0, [env.ref("base.group_user").id])],
            }
        )
    )
    with pytest.raises(REFUSED):
        line.with_user(clerk).write({"unit_price": 1.0})


def test_checkout_prices_every_line_from_the_catalogue(shop):
    env, _product, customer = shop
    _user, cart, line = customer(6)
    # a line priced before this fix (or by any other path) is re-priced
    line.sudo().write({"unit_price": 1.0})
    order = cart.action_place_order(shipping_address="House 1, Road 2, Dhaka")
    assert order.total_amount == 2500.0
    assert order.line_ids.unit_price == 2500.0
    assert line.unit_price == 2500.0


def test_a_line_takes_the_catalogue_price_whatever_is_sent(shop):
    env, product, customer = shop
    _user, cart, _line = customer(7)
    clerk = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "C1 Clerk 2",
                "login": "c1.clerk2@a04.test",
                # A04 ERP M38-F5: a cart line is captured by assisted sales
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
    new = (
        env["fix.storefront.cart.line"]
        .with_user(clerk)
        .create({"cart_id": cart.id, "product_id": product.id, "quantity": 2, "unit_price": 1.0})
    )
    assert new.unit_price == 2500.0 and new.subtotal == 5000.0
