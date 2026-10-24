"""Behavioural security tests for the M38 storefront API (R01 re-audit 2026-10-22).

Runs against the live ORM (``odoo_env``: database fix_test, rolled back per test)
with ``odoo.http.request`` replaced by a minimal stand-in exposing ``env`` /
``session`` — the controller code itself runs unmodified. Each stand-in carries
its own session, i.e. one stand-in = one browser.
"""

from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from odoo import Command, http
from odoo.addons.cd_storefront.controllers import storefront_api
from odoo.addons.cd_storefront.controllers.storefront_api import StorefrontApiController


class _Browser:
    """One client: a user plus its own server-side session."""

    def __init__(self, env, user):
        self.env = env(user=user.id)
        self.session = http.Session(http.get_default_session(), f"sid-{id(self)}", new=True)


@contextmanager
def _in(browser):
    with patch.object(storefront_api, "request", browser):
        yield StorefrontApiController()


@pytest.fixture
def world(odoo_env):
    env = odoo_env
    portal = env.ref("base.group_portal")
    users = env["res.users"].with_context(no_reset_password=True)
    alice = users.create(
        {"name": "Alice", "login": "alice@sec.test", "group_ids": [Command.set([portal.id])]}
    )
    bob = users.create(
        {"name": "Bob", "login": "bob@sec.test", "group_ids": [Command.set([portal.id])]}
    )
    staff = users.create({"name": "Staff", "login": "staff@sec.test"})
    product = env["product.template"].create(
        {"name": "Sec Charger", "list_price": 100.0, "sale_ok": True}
    )
    hidden = env["product.template"].create(
        {"name": "Internal Jig", "list_price": 5.0, "sale_ok": False}
    )
    return SimpleNamespace(
        env=env,
        alice=alice,
        bob=bob,
        staff=staff,
        public=env.ref("base.public_user"),
        product=product,
        hidden=hidden,
    )


def _order(world, owner, state="paid", qty=2):
    """A placed order for ``owner`` (res.users) worth qty x 100."""
    return world.env["fix.storefront.order"].create(
        {
            "customer_id": owner.partner_id.id,
            "total_amount": 100.0 * qty,
            "shipping_address": "Dhanmondi, Dhaka",
            "state": state,
            "line_ids": [
                Command.create(
                    {
                        "product_id": world.product.id,
                        "quantity": qty,
                        "unit_price": 100.0,
                        "subtotal": 100.0 * qty,
                    }
                )
            ],
        }
    )


def _returns(world, order):
    return world.env["fix.storefront.return"].search([("order_id", "=", order.id)])


# --- route declaration ---------------------------------------------------------


def test_route_auth_levels():
    routes = StorefrontApiController
    assert routes.catalogue.original_routing["auth"] == "public"
    assert routes.get_or_update_cart.original_routing["auth"] == "public"
    assert routes.checkout.original_routing["auth"] == "public"
    assert routes.track_order.original_routing["auth"] == "public"
    assert routes.create_return.original_routing["auth"] == "user"


def test_catalogue_is_public_and_bounded(world):
    with _in(_Browser(world.env, world.public)) as ctrl:
        res = ctrl.catalogue(limit="999999")
        junk = ctrl.catalogue(limit="lots")
    names = [p["name"] for p in res["products"]]
    assert "Sec Charger" in names
    assert "Internal Jig" not in names
    assert res["count"] <= storefront_api.CATALOGUE_MAX_LIMIT
    assert junk["count"] >= 1


# --- cart / checkout ---------------------------------------------------------------


def test_guest_cart_is_bound_to_the_session(world):
    guest_1 = _Browser(world.env, world.public)
    guest_2 = _Browser(world.env, world.public)
    with _in(guest_1) as ctrl:
        mine = ctrl.get_or_update_cart(product_id=world.product.id, quantity=2)
        again = ctrl.get_or_update_cart()
    with _in(guest_2) as ctrl:
        other_view = ctrl.get_or_update_cart()
        stolen = ctrl.checkout(cart_id=mine["cart_id"])
        stolen_implicit = ctrl.checkout()
    assert mine["items_count"] == 1
    assert again["cart_id"] == mine["cart_id"]
    assert other_view["cart_id"] is None
    assert other_view["items_count"] == 0
    assert stolen["error"]["code"] == "CART_NOT_FOUND"
    assert stolen_implicit["error"]["code"] == "CART_NOT_FOUND"
    assert world.env["fix.storefront.cart"].browse(mine["cart_id"]).state == "open"


def test_portal_customer_cannot_reach_another_customers_cart(world):
    with _in(_Browser(world.env, world.bob)) as ctrl:
        bobs = ctrl.get_or_update_cart(product_id=world.product.id)
    with _in(_Browser(world.env, world.alice)) as ctrl:
        view = ctrl.get_or_update_cart(customer_id=world.bob.partner_id.id)
        checkout = ctrl.checkout(cart_id=bobs["cart_id"], customer_id=world.bob.partner_id.id)
    assert view["cart_id"] is None
    assert checkout["error"]["code"] == "CART_NOT_FOUND"
    assert world.env["fix.storefront.cart"].browse(bobs["cart_id"]).state == "open"


def test_internal_staff_may_act_for_a_customer(world):
    with _in(_Browser(world.env, world.bob)) as ctrl:
        bobs = ctrl.get_or_update_cart(product_id=world.product.id)
    with _in(_Browser(world.env, world.staff)) as ctrl:
        view = ctrl.get_or_update_cart(customer_id=world.bob.partner_id.id)
    assert view["cart_id"] == bobs["cart_id"]


def test_cart_rejects_unsaleable_products_and_bad_quantities(world):
    with _in(_Browser(world.env, world.alice)) as ctrl:
        hidden = ctrl.get_or_update_cart(product_id=world.hidden.id)
        unknown = ctrl.get_or_update_cart(product_id="x")
        negative = ctrl.get_or_update_cart(product_id=world.product.id, quantity=-5)
        nan = ctrl.get_or_update_cart(product_id=world.product.id, quantity="nan")
    assert hidden["error"]["code"] == "PRODUCT_NOT_FOUND"
    assert unknown["error"]["code"] == "PRODUCT_NOT_FOUND"
    assert negative["error"]["code"] == "INVALID_QUANTITY"
    assert nan["error"]["code"] == "INVALID_QUANTITY"
    assert not world.env["fix.storefront.cart"].search(
        [("customer_id", "=", world.alice.partner_id.id)]
    )


def test_guest_checkout_and_tracking_stay_in_the_placing_session(world):
    guest = _Browser(world.env, world.public)
    snoop = _Browser(world.env, world.public)
    with _in(guest) as ctrl:
        cart = ctrl.get_or_update_cart(product_id=world.product.id, quantity=1)
        placed = ctrl.checkout(cart_id=cart["cart_id"], shipping_address="Mirpur")
        tracked = ctrl.track_order(order_id=placed["order_id"])
        empty_again = ctrl.checkout()
    with _in(snoop) as ctrl:
        by_id = ctrl.track_order(order_id=placed["order_id"])
        by_name = ctrl.track_order(order_name=placed["order_name"])
    assert placed["state"] == "pending_payment"
    assert tracked["order_name"] == placed["order_name"]
    assert empty_again["error"]["code"] == "CART_NOT_FOUND"
    assert by_id["error"]["code"] == "ORDER_NOT_FOUND"
    assert by_name["error"]["code"] == "ORDER_NOT_FOUND"


# --- tracking ----------------------------------------------------------------------


def test_tracking_requires_ownership(world):
    order = _order(world, world.alice)
    with _in(_Browser(world.env, world.alice)) as ctrl:
        own = ctrl.track_order(order_id=order.id)
        own_by_name = ctrl.track_order(order_name=order.name)
    with _in(_Browser(world.env, world.bob)) as ctrl:
        foreign = ctrl.track_order(order_id=order.id)
        foreign_by_name = ctrl.track_order(order_name=order.name)
        missing = ctrl.track_order(order_id=order.id + 1000)
    with _in(_Browser(world.env, world.public)) as ctrl:
        anonymous = ctrl.track_order(order_id=order.id)
    with _in(_Browser(world.env, world.staff)) as ctrl:
        staff = ctrl.track_order(order_id=order.id)
    assert own["order_id"] == order.id
    assert own_by_name["order_id"] == order.id
    assert staff["order_id"] == order.id
    for res in (foreign, foreign_by_name, anonymous):
        assert res == missing  # indistinguishable from a non-existent order
    assert missing["error"]["code"] == "ORDER_NOT_FOUND"


# --- returns -----------------------------------------------------------------------


def test_returns_require_ownership(world):
    order = _order(world, world.alice)
    with _in(_Browser(world.env, world.bob)) as ctrl:
        foreign = ctrl.create_return(order_id=order.id, refund_amount=200)
    with _in(_Browser(world.env, world.public)) as ctrl:
        anonymous = ctrl.create_return(order_id=order.id)
    with _in(_Browser(world.env, world.staff)) as ctrl:
        staff = ctrl.create_return(order_id=order.id)
    for res in (foreign, anonymous, staff):
        assert res["error"]["code"] == "ORDER_NOT_FOUND"
    assert not _returns(world, order)


def test_return_refund_is_computed_and_capped_by_the_server(world):
    order = _order(world, world.alice, qty=2)  # 200.00 of lines
    with _in(_Browser(world.env, world.alice)) as ctrl:
        inflated = ctrl.create_return(order_id=order.id, refund_amount=999999)
        negative = ctrl.create_return(order_id=order.id, refund_amount=-1)
        garbage = ctrl.create_return(order_id=order.id, refund_amount="all of it")
        bad_reason = ctrl.create_return(order_id=order.id, reason="because")
        partial = ctrl.create_return(order_id=order.id, refund_amount=50)
        over_rest = ctrl.create_return(order_id=order.id, refund_amount=151)
        rest = ctrl.create_return(order_id=order.id, reason="wrong_item")
        exhausted = ctrl.create_return(order_id=order.id)
    assert inflated["error"]["code"] == "REFUND_EXCEEDS_ORDER"
    assert negative["error"]["code"] == "INVALID_REFUND_AMOUNT"
    assert garbage["error"]["code"] == "INVALID_REFUND_AMOUNT"
    assert bad_reason["error"]["code"] == "INVALID_REASON"
    assert partial["refund_bdt"] == "50.00"
    assert over_rest["error"]["code"] == "REFUND_EXCEEDS_ORDER"
    assert rest["refund_bdt"] == "150.00"
    assert exhausted["error"]["code"] == "RETURN_NOT_ALLOWED"
    assert sorted(_returns(world, order).mapped("refund_amount")) == [50.0, 150.0]


def test_unpaid_order_cannot_be_returned(world):
    order = _order(world, world.alice, state="pending_payment")
    with _in(_Browser(world.env, world.alice)) as ctrl:
        res = ctrl.create_return(order_id=order.id)
    assert res["error"]["code"] == "RETURN_NOT_ALLOWED"
    assert not _returns(world, order)
