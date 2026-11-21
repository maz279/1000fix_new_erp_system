"""Behavioural tests for the M38 storefront models and API journeys (live ORM).

``odoo_env`` (database fix_test, rolled back per test); the controller runs with
``odoo.http.request`` replaced by a stand-in carrying ``env`` + a real session.
Access control of the public routes lives in test_api_security.py.
"""

from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from odoo import Command, fields, http
from odoo.addons.cd_storefront.controllers import storefront_api
from odoo.addons.cd_storefront.controllers.storefront_api import StorefrontApiController
from odoo.exceptions import UserError

from .test_a04_c2_c13_storefront import published_item, released_card, storefront_world


class _Browser:
    def __init__(self, env, user):
        self.env = env(user=user.id)
        self.session = http.Session(http.get_default_session(), f"sid-{id(self)}", new=True)


@contextmanager
def _as(world, user):
    with patch.object(storefront_api, "request", _Browser(world.env, user)):
        yield StorefrontApiController()


@pytest.fixture
def world(odoo_env):
    env = odoo_env
    portal = env.ref("base.group_portal")
    users = env["res.users"].with_context(no_reset_password=True)
    alice = users.create(
        {"name": "Alice SF", "login": "alice@sf.test", "group_ids": [Command.set([portal.id])]}
    )
    staff = users.create({"name": "Staff SF", "login": "staff@sf.test"})
    charger = env["product.template"].create(
        {"name": "SF Fast Charger", "list_price": 1250.0, "sale_ok": True}
    )
    cable = env["product.template"].create(
        {"name": "SF USB-C Cable", "list_price": 300.0, "sale_ok": True}
    )
    # A04 ERP M38-F1/F12/F13: M11 prices (excl. VAT; 1,250.00 and 300.00 with
    # 15% VAT), live gateways with callback secrets, an approved COD rule
    storefront_world(env, charger, price=1086.96)
    released_card(env, cable, 260.87)
    published_item(env, cable)  # A04 ERP round 2 (M38-F19): on the M37 catalogue
    return SimpleNamespace(env=env, alice=alice, staff=staff, charger=charger, cable=cable)


def _cart(world, partner, lines=()):
    cart = world.env["fix.storefront.cart"].create({"customer_id": partner.id})
    for product, qty in lines:
        world.env["fix.storefront.cart.line"].create(
            {
                "cart_id": cart.id,
                "product_id": product.id,
                "quantity": qty,
                "unit_price": product.list_price,
            }
        )
    return cart


def _placed(world, state="pending_payment"):
    cart = _cart(world, world.alice.partner_id, [(world.charger, 2)])
    order = cart.action_place_order(shipping_address="Banani, Dhaka")
    if state != "pending_payment":
        order.state = state
    return order


# --- money formatting (BN-007) ------------------------------------------------------


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        (250, "250.00"),
        (1234567.5, "12,34,567.50"),
        (-98765.4, "-98,765.40"),
        (None, "0.00"),
        ("abc", "0.00"),
    ],
)
def test_amounts_are_south_asian_grouped(amount, expected):
    assert storefront_api._fmt_bdt(amount) == expected


# --- catalogue / cart ---------------------------------------------------------------


def test_catalogue_search_narrows_by_name(world):
    with _as(world, world.alice) as ctrl:
        res = ctrl.catalogue(search="SF Fast")
    assert [p["name"] for p in res["products"]] == ["SF Fast Charger"]
    assert res["products"][0]["price_bdt"] == "1,250.00"
    # stock is not a dependency: availability is unknown, so never asserted
    assert "in_stock" not in res["products"][0]


def test_adding_items_grows_one_cart(world):
    with _as(world, world.alice) as ctrl:
        first = ctrl.get_or_update_cart(product_id=world.charger.id)
        again = ctrl.get_or_update_cart(product_id=world.charger.id, quantity="2")
        mixed = ctrl.get_or_update_cart(product_id=world.cable.id, quantity=1)
        junk = ctrl.get_or_update_cart(product_id=world.cable.id, quantity="lots")
    assert first["cart_id"] == again["cart_id"] == mixed["cart_id"]
    charger_line = next(x for x in mixed["lines"] if x["product_id"] == world.charger.id)
    assert charger_line["quantity"] == 3.0
    assert charger_line["subtotal_bdt"] == "3,750.00"
    assert mixed["items_count"] == 2
    assert mixed["total_bdt"] == "4,050.00"
    assert junk["error"]["code"] == "INVALID_QUANTITY"


def test_internal_staff_without_a_customer_get_their_own_cart(world):
    with _as(world, world.staff) as ctrl:
        res = ctrl.get_or_update_cart(product_id=world.cable.id)
    cart = world.env["fix.storefront.cart"].browse(res["cart_id"])
    assert cart.customer_id == world.staff.partner_id


# --- checkout -----------------------------------------------------------------------


def test_customer_checkout_places_the_order(world):
    with _as(world, world.alice) as ctrl:
        ctrl.get_or_update_cart(product_id=world.charger.id, quantity=2)
        placed = ctrl.checkout(
            shipping_address="Gulshan 2", shipping_method="express_courier", payment_rail="nagad"
        )
        tracked = ctrl.track_order(order_name=placed["order_name"])
    order = world.env["fix.storefront.order"].browse(placed["order_id"])
    assert placed["total_bdt"] == "2,500.00"
    assert (placed["shipping_method"], placed["payment_rail"]) == ("express_courier", "nagad")
    assert order.cart_id.state == "ordered"
    assert order.customer_id == world.alice.partner_id
    assert [line["quantity"] for line in tracked["lines"]] == [2.0]
    assert tracked["carrier_consignment"] is None


def test_checkout_refuses_an_empty_cart(world):
    _cart(world, world.alice.partner_id)
    with _as(world, world.alice) as ctrl:
        res = ctrl.checkout()
    assert res["error"]["code"] == "CART_EMPTY"


def test_checkout_rejects_unknown_rails_and_methods_without_touching_the_cart(world):
    """Regression: an unknown shipping method/rail failed inside the order
    create AFTER the cart had moved to 'checkout' - the cart was stranded."""
    cart = _cart(world, world.alice.partner_id, [(world.cable, 1)])
    with _as(world, world.alice) as ctrl:
        method = ctrl.checkout(shipping_method="drone")
        rail = ctrl.checkout(payment_rail="barter")
    assert method["error"]["code"] == "INVALID_SHIPPING_METHOD"
    assert rail["error"]["code"] == "INVALID_PAYMENT_RAIL"
    with _as(world, world.alice) as ctrl:  # unhashable JSON values are just unknown
        assert ctrl.checkout(shipping_method={"x": 1})["error"]["code"] == "INVALID_SHIPPING_METHOD"
        assert ctrl.checkout(payment_rail=["bkash"])["error"]["code"] == "INVALID_PAYMENT_RAIL"
        order = _placed(world, state="delivered")
        bad_reason = ctrl.create_return(order_id=order.id, reason={"why": "x"})
    assert bad_reason["error"]["code"] == "INVALID_REASON"
    assert cart.state == "open"
    assert not cart.order_id


def test_a_failed_placement_rolls_the_cart_back(world, caplog):
    cart = _cart(world, world.alice.partner_id, [(world.cable, 1)])
    boom = RuntimeError("relation fix_storefront_order: deadlock detected")
    with (
        patch.object(type(cart), "action_place_order", side_effect=boom),
        _as(world, world.alice) as ctrl,
    ):
        res = ctrl.checkout()
    assert res["error"]["code"] == "CHECKOUT_FAILED"
    assert "deadlock" not in res["error"]["message"]  # internals stay in the log
    assert "Checkout failed" in caplog.text
    assert cart.state == "open"
    with _as(world, world.alice) as ctrl:
        no_address = ctrl.checkout()  # home delivery needs a real address
        retry = ctrl.checkout(shipping_address="Road 11, Banani")
    assert no_address["error"]["code"] == "CHECKOUT_FAILED"
    assert retry["state"] == "pending_payment"


def test_tracking_without_a_reference_finds_nothing(world):
    with _as(world, world.alice) as ctrl:
        res = ctrl.track_order()
    assert res["error"]["code"] == "ORDER_NOT_FOUND"


# --- models -------------------------------------------------------------------------


def test_explicit_references_are_kept_and_defaults_generated(world):
    env = world.env
    named = env["fix.storefront.cart"].create(
        {"name": "CART/MANUAL/1", "customer_id": world.alice.partner_id.id}
    )
    generated = _cart(world, world.alice.partner_id)
    order = env["fix.storefront.order"].create(
        {
            "name": "SO/MANUAL/1",
            "customer_id": world.alice.partner_id.id,
            "total_amount": 10.0,
            "shipping_address": "Mirpur",
        }
    )
    # A04 audit M38-9: a return names the paid order it returns
    paid = _placed(world, state="paid")
    rma = env["fix.storefront.return"].create(
        {"name": "RMA/MANUAL/1", "customer_id": world.alice.partner_id.id, "order_id": paid.id}
    )
    assert (named.name, order.name, rma.name) == ("CART/MANUAL/1", "SO/MANUAL/1", "RMA/MANUAL/1")
    assert generated.name.startswith("CART/")


def test_generated_references_are_unique_within_one_second(world):
    """Regression: with no ir.sequence the models fell back to a second-resolution
    timestamp, so back-to-back orders shared one reference."""
    first, second = _placed(world), _placed(world)
    paid = _placed(world, state="paid")
    vals = {"customer_id": world.alice.partner_id.id, "order_id": paid.id}
    rmas = world.env["fix.storefront.return"].create([dict(vals), dict(vals)])
    assert first.name != second.name
    assert first.name.startswith("SF/")
    assert len(set(rmas.mapped("name"))) == 2
    assert all(name.startswith("RMA/") for name in rmas.mapped("name"))


def test_cart_guards(world):
    empty = _cart(world, world.alice.partner_id)
    full = _cart(world, world.alice.partner_id, [(world.cable, 1)])
    with pytest.raises(UserError, match="Cart is empty"), world.env.cr.savepoint():
        empty.action_checkout()
    with pytest.raises(UserError, match="Cart is empty"), world.env.cr.savepoint():
        empty.action_place_order()
    # one cart, one order - never a silent partial
    with pytest.raises(ValueError), world.env.cr.savepoint():
        (empty | full).action_place_order()
    with pytest.raises(UserError, match="Quantity must be positive"), world.env.cr.savepoint():
        full.line_ids.quantity = 0
    assert full.state == "open"


def test_placed_order_carries_the_cart_lines_and_customer_address(world):
    world.alice.partner_id.write({"street": "House 7, Road 3", "city": "Dhaka"})
    cart = _cart(world, world.alice.partner_id, [(world.charger, 1), (world.cable, 2)])
    order = cart.action_place_order()
    assert order.total_amount == 1850.0
    assert "House 7, Road 3" in order.shipping_address
    assert sorted(order.line_ids.mapped("subtotal")) == [600.0, 1250.0]
    assert (cart.state, cart.order_id) == ("ordered", order)


def test_payment_dispatch_and_delivery_lifecycle(world):
    order = _placed(world)
    order.action_confirm_payment(payment_ref="BKX-1", rail="bkash")
    paid_at = order.payment_date
    order.action_confirm_payment(payment_ref="BKX-2")  # already paid: a no-op
    assert (order.state, order.payment_ref, order.payment_date) == ("paid", "BKX-1", paid_at)
    consignment = world.env["fix.consignment"].create(
        {
            "operating_unit_id": world.env["operating.unit"].search([], limit=1).id,
            "scheduled_date": fields.Datetime.now(),
        }
    )
    order.action_dispatch(carrier_consignment_id=consignment.id)
    assert (order.state, order.carrier_consignment_id) == ("dispatched", consignment)
    # A04 audit M38-11: delivered on the consignment's proof of delivery
    with pytest.raises(UserError, match="proof of delivery"), world.env.cr.savepoint():
        order.action_deliver()
    consignment.write({"state": "delivered"})  # the M03 POD (its own suite)
    order.action_deliver()
    assert order.state == "delivered"
    with pytest.raises(UserError, match="paid before dispatch"), world.env.cr.savepoint():
        order.action_dispatch()


def test_payment_needs_a_real_gateway_reference(world):
    order = _placed(world)
    with pytest.raises(UserError, match="gateway transaction reference"), world.env.cr.savepoint():
        order.action_confirm_payment()
    with pytest.raises(UserError, match="gateway transaction reference"), world.env.cr.savepoint():
        order.action_confirm_payment(payment_ref="   ")
    assert (order.state, order.payment_ref, order.payment_date) == ("pending_payment", False, False)
    order.payment_ref = "8N7A6B5C4D"  # entered from the bKash statement
    order.action_confirm_payment()
    assert (order.state, order.payment_ref, order.payment_rail) == ("paid", "8N7A6B5C4D", "bkash")
    cancelled = _placed(world, state="cancelled")
    with pytest.raises(UserError, match="only an unpaid order"), world.env.cr.savepoint():
        cancelled.action_confirm_payment(payment_ref="LATE-1")


def test_dispatch_deliver_and_cancel_guards(world):
    unpaid = _placed(world)
    with pytest.raises(UserError, match="paid before dispatch"), world.env.cr.savepoint():
        unpaid.action_dispatch()
    with pytest.raises(UserError, match="Only a dispatched order"), world.env.cr.savepoint():
        unpaid.action_deliver()
    assert unpaid.state == "pending_payment"
    cod = _placed(world)
    cod.payment_rail = "cod"
    with pytest.raises(UserError, match="consignment"), world.env.cr.savepoint():
        cod.action_dispatch()  # A04 audit M38-11: it leaves on its consignment
    consignment = world.env["fix.consignment"].create(
        {
            "operating_unit_id": world.env["operating.unit"].search([], limit=1).id,
            "scheduled_date": fields.Datetime.now(),
        }
    )
    cod.action_dispatch(carrier_consignment_id=consignment.id)  # cash at the door
    assert cod.state == "dispatched"
    with pytest.raises(UserError, match="no longer be cancelled"), world.env.cr.savepoint():
        cod.action_cancel()
    consignment.write({"state": "delivered"})
    cod.action_deliver()
    with pytest.raises(UserError, match="no longer be cancelled"), world.env.cr.savepoint():
        cod.action_cancel()
    unpaid.action_cancel()
    assert unpaid.state == "cancelled"
    with pytest.raises(UserError, match="paid before dispatch"), world.env.cr.savepoint():
        unpaid.action_dispatch()


def test_home_delivery_needs_a_real_address(world):
    partner = world.env["res.partner"].create({"name": "SF No Address"})
    world.env.invalidate_all()
    cart = _cart(world, partner, [(world.cable, 1)])
    if (partner.contact_address or "").strip():
        pytest.skip("contact_address renders the name for an address-less partner")
    with pytest.raises(UserError, match="shipping address is required"), world.env.cr.savepoint():
        cart.action_place_order()
    assert "Dhaka, Bangladesh" not in (cart.order_id.shipping_address or "")
    pickup = cart.action_place_order(shipping_method="branch_pickup")
    assert pickup.shipping_address == "Branch walk-in pickup"


def test_return_refund_requires_receipt_and_inspection(world):
    """The return lifecycle up to the refund approval. A04 audit M38-5: the
    refund is then approved from the M63 inbox by a refund approver holding
    the DOFA tier (test_a04_c2_c13_storefront.py), never by the superuser
    pressing a button: action_dofa_approve checks the tier of whoever acts."""
    order = _placed(world, state="delivered")
    rma = world.env["fix.storefront.return"].create(
        {
            "order_id": order.id,
            "customer_id": world.alice.partner_id.id,
            "refund_amount": 1250.0,
        }
    )
    with pytest.raises(UserError, match="approved return"), world.env.cr.savepoint():
        rma.action_receive_and_inspect(condition="grade_a")
    rma.action_approve()
    assert rma.state == "approved"
    with pytest.raises(UserError, match="requested return"), world.env.cr.savepoint():
        rma.action_approve()
    with pytest.raises(UserError, match="prior to physical receipt"), world.env.cr.savepoint():
        rma.action_approve_refund()
    with pytest.raises(UserError, match="inspection result"), world.env.cr.savepoint():
        rma.action_receive_and_inspect()  # never a default grade
    rma.action_receive_and_inspect(condition="grade_b")
    assert (rma.state, rma.inspected_condition) == ("received", "grade_b")
    assert rma.refund_amount == 1250.0  # a defect is refunded at any grade
    assert rma.dofa_tier_required == "tier_2"  # BDT 1,250: above the Tier-1 band
    events = world.env["fix.event.outbox"].search(
        [("event_type", "=", "storefront.refund_processed"), ("aggregate_id", "=", rma.id)]
    )
    assert not events  # nothing is "refunded" before the approval and the credit note
