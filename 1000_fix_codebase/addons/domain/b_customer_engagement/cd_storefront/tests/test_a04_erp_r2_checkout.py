# ruff: noqa: F811  (the storefront fixtures are imported and used as parameters)
"""A04 ERP audit, round 2 (21 Nov 2026) - M38 checkout and returns.

  M38-F14 the delivery fee and a checkout voucher are priced by the server at
          placement from M11 (price_for on the fee product; the promotion
          engine for the voucher, never below the floor), consumed once, and
          never taken from the caller; the voucher is not auto-applied
  M38-F20 an idempotency key makes a replay return the same order; the
          customer cancels their own order before dispatch only
  M38-F19 the API catalogue lists only M37-published items with a VAT class
          and filters by device compatibility
  M38-F8  a return names its lines; never more units than were sold, and the
          refund is what the customer paid for them

Every test runs as the storefront's users (assisted-sales clerk, operator,
a portal customer) against the ORM, and is built so only the new rule can
refuse it.
"""

import itertools
from contextlib import contextmanager
from datetime import timedelta
from unittest.mock import patch

import pytest
from odoo import Command, fields, http
from odoo.addons.cd_storefront.controllers import storefront_api
from odoo.addons.cd_storefront.controllers.storefront_api import StorefrontApiController
from odoo.exceptions import AccessError, UserError, ValidationError

from .test_a04_c2_c13_storefront import (  # noqa: F401  (fixtures)
    _consignment,
    _mk,
    _paid,
    published_item,
    refurb,
    released_card,
    w,
)

REFUSED = (UserError, ValidationError, AccessError)
FEE_PARAM = "cd_storefront.delivery_fee_code.%s"
_SEQ = itertools.count(1)


# ---------------------------------------------------------------- helpers
def _fee_product(w, price=100.0, method="standard_delivery"):
    n = next(_SEQ)
    fee = w.env["product.template"].create(
        {"name": "A4R2 Delivery %d" % n, "list_price": 999.0, "sale_ok": True}
    )
    fee.product_variant_id.default_code = "A4R2-DLV-%d" % n
    released_card(w.env, fee, price)
    w.env["ir.config_parameter"].sudo().set_param(
        FEE_PARAM % method, fee.product_variant_id.default_code
    )
    return fee


def _voucher(w, code=None, value=10.0, voucher=True, **vals):
    code = code or "A4R2V%d" % next(_SEQ)
    today = fields.Date.context_today(w.env["res.partner"])
    promo = (
        w.env["fix.promotion"]
        .sudo()
        .create(
            dict(
                {
                    "name": "R2 voucher %s" % code,
                    "code": code,
                    "discount_type": "percent",
                    "value": value,
                    "channel": "portal",
                    "valid_from": today - timedelta(days=1),
                    "valid_until": today + timedelta(days=10),
                    "storefront_voucher": voucher,
                    "company_id": w.env.company.id,
                },
                **vals,
            )
        )
    )
    promo._guarded().write({"state": "active"})
    return promo


def _cart(w, qty=2, product=None, user=None):
    u = user or w.clerk
    cart = w.env["fix.storefront.cart"].with_user(u).create({"customer_id": w.customer.id})
    w.env["fix.storefront.cart.line"].with_user(u).create(
        {"cart_id": cart.id, "product_id": (product or w.product).id, "quantity": qty}
    )
    return cart


def _place(cart, method="standard_delivery", rail="bkash", **kw):
    return cart.action_place_order(shipping_method=method, payment_rail=rail, **kw)


# ================================================================ M38-F14
def test_f14_delivery_fee_is_the_m11_price_of_the_fee_product(w):
    fee = _fee_product(w, 100.0)
    order = _place(_cart(w, qty=2)).sudo()
    line = order.line_ids.filtered(lambda ln: ln.line_type == "delivery")
    # 100.00 excl. VAT + 15% VAT, from the released card - never list_price
    assert (line.product_id, line.unit_price_excl, line.unit_price) == (fee, 100.0, 115.0)
    assert line.price_card_id and line.price_source == "card"
    assert (order.goods_amount, order.delivery_fee, order.total_amount) == (5000.0, 115.0, 5115.0)
    # a branch pickup names no fee product: no fee line
    pickup = _place(_cart(w, qty=1), method="branch_pickup").sudo()
    assert not pickup.line_ids.filtered(lambda ln: ln.line_type == "delivery")
    assert pickup.total_amount == 2500.0


def test_f14_a_configured_fee_with_no_released_price_refuses_the_order(w):
    fee = _fee_product(w, 100.0)
    w.env["fix.rate.card"].sudo().search(
        [("product_code", "=", fee.product_variant_id.default_code)]
    )._guarded().write({"state": "retired"})
    with pytest.raises(UserError, match="delivery fee"), w.env.cr.savepoint():
        _place(_cart(w))


def test_f14_voucher_is_priced_by_the_promotion_engine_and_consumed(w):
    promo = _voucher(w, value=10.0, max_uses=5)
    order = _place(_cart(w, qty=2), method="branch_pickup", voucher_code=promo.code.lower())
    order = order.sudo()
    goods = order.line_ids.filtered(lambda ln: ln.line_type == "product")
    disc = order.line_ids.filtered(lambda ln: ln.line_type == "discount")
    # 10% of 2 x 2,173.91 excl. VAT = 434.78; with VAT 500.00 off the goods
    assert (disc.promotion_id, disc.subtotal, disc.unit_price_excl) == (promo, -500.0, -434.78)
    assert (goods.discount_amount, goods.net_subtotal) == (500.0, 4500.0)
    assert (order.discount_amount, order.voucher_code, order.total_amount) == (
        500.0,
        promo.code,
        4500.0,
    )
    # the total is still the sum of the lines; the voucher is spent once
    assert sum(order.line_ids.mapped("subtotal")) == order.total_amount
    assert (promo.use_count, promo.budget_used) == (1, 434.78)


def test_f14_a_voucher_is_never_applied_automatically(w):
    """price_for applies every active promotion by itself; a checkout
    voucher only when the customer names it."""
    _voucher(w, value=10.0)
    res = w.env["fix.rate.card"].sudo().price_for(w.product, channel="storefront")
    assert res["price"] == 2173.91 and res["promotion_discount"] == 0.0
    order = _place(_cart(w, qty=1), method="branch_pickup").sudo()
    assert order.total_amount == 2500.0 and not order.discount_amount


@pytest.mark.parametrize("case", ["unknown", "auto", "spent", "elsewhere"])
def test_f14_an_unusable_voucher_refuses_the_order(w, case):
    if case == "unknown":
        code = "NO-SUCH-VOUCHER"
    elif case == "auto":
        code = _voucher(w, voucher=False).code  # auto-applied promotion, not a voucher
    elif case == "spent":
        promo = _voucher(w, max_uses=1)
        promo._guarded().write({"use_count": 1})
        code = promo.code
    else:
        other = w.env["product.template"].create({"name": "R2 other item", "sale_ok": True})
        other.product_variant_id.default_code = "A4R2-OTH-%d" % next(_SEQ)
        item = published_item(w.env, other)
        code = _voucher(w, catalogue_item_ids=[Command.set(item.ids)]).code
    cart = _cart(w)
    with pytest.raises(UserError, match="oucher"), w.env.cr.savepoint():
        _place(cart, method="branch_pickup", voucher_code=code)
    assert cart.state != "ordered"


def test_f14_a_voucher_stops_at_the_price_floor(w):
    """M15 cost 2,000 makes the floor 2,000: a 50% voucher may take only
    173.91 per unit off (as M11 stops a promotion at the floor)."""
    w.env["ir.config_parameter"].sudo().set_param("cd_rate_card.margin_floor_pct", "0")
    part = w.env["fix.spare.part"].create(
        {
            "name": "R2 floor part",
            "part_number": "R2FLOOR-%d" % next(_SEQ),
            "unit_cost": 2000.0,
            "product_id": w.product.product_variant_id.id,
        }
    )
    loc = w.env["fix.stock.location"].create(
        {
            "name": "R2 floor store",
            "code": "R2FS%d" % part.id,
            "location_type": "central",
            "operating_unit_id": w.ou.id,
        }
    )
    w.env["fix.stock.onhand"]._apply(part, loc, "owned", 5.0, 2000.0)
    promo = _voucher(w, value=50.0)
    order = _place(_cart(w, qty=1), method="branch_pickup", voucher_code=promo.code).sudo()
    disc = order.line_ids.filtered(lambda ln: ln.line_type == "discount")
    assert disc.unit_price_excl == -173.91
    assert order.total_amount == 2500.0 - 200.0  # 173.91 x 1.15 = 200.00


def test_f14_the_voucher_flag_is_fixed_once_released(w):
    promo = _voucher(w)
    with pytest.raises(UserError, match="no longer a draft"), w.env.cr.savepoint():
        officer = _mk(w.env, "a4r2_officer", "cd_rate_card.group_pricing_officer")
        promo.with_user(officer).write({"storefront_voucher": False})
    assert promo.storefront_voucher


def test_f14_the_checkout_promotions_screen_lists_online_promotions(w):
    """The screen's domain, run against the ORM, finds the storefront's
    promotions (it named channels fix.promotion does not have)."""
    import ast
    import re

    from odoo.addons.cd_p03_portal.controllers.form_fields import STATIC

    js = (STATIC / "a04" / "m38.js").read_text(encoding="utf-8")
    start = js.index("'M38-promos': {")
    domain = ast.literal_eval(re.search(r"domain:\s*(\[\[.*?\]\]\])", js[start:]).group(1))
    online, branch = _voucher(w), _voucher(w, voucher=False, channel="branch")
    found = w.env["fix.promotion"].sudo().search(domain)
    assert online in found and branch not in found


# ================================================================ M38-F20
def test_f20_a_replay_of_the_key_returns_the_same_order(w):
    cart = _cart(w)
    first = _place(cart, method="branch_pickup", idempotency_key="chk-001")
    again = _place(cart, method="branch_pickup", idempotency_key="chk-001")
    assert again == first
    assert w.env["fix.storefront.order"].sudo().search_count([("cart_id", "=", cart.id)]) == 1
    # without the key a second placement of the cart is still refused
    with pytest.raises(UserError, match="already been ordered"), w.env.cr.savepoint():
        _place(cart, method="branch_pickup")
    # the same key from another cart of the customer is the same request
    other_cart = _cart(w)
    assert _place(other_cart, method="branch_pickup", idempotency_key="chk-001") == first
    assert other_cart.state != "ordered"
    # and the database holds one key per customer whoever writes it
    other = _place(_cart(w), method="branch_pickup")
    with pytest.raises(Exception), w.env.cr.savepoint():  # noqa: B017 (unique index)
        other.sudo()._guarded().write({"idempotency_key": "chk-001"})
        w.env.flush_all()


def test_f20_the_replay_reserves_nothing_twice(w):
    variant = w.product.product_variant_id
    part = w.env["fix.spare.part"].create(
        {"name": "R2 res", "part_number": "R2RES-%d" % next(_SEQ), "product_id": variant.id}
    )
    loc = w.env["fix.stock.location"].create(
        {
            "name": "R2 store",
            "code": "R2ST%d" % part.id,
            "location_type": "central",
            "operating_unit_id": w.ou.id,
        }
    )
    w.env["fix.stock.onhand"]._apply(part, loc, "owned", 10.0, 1.0)
    if (
        "fix.storefront.order.line" in w.env
        and "reserved_qty" not in w.env["fix.storefront.order.line"]._fields
    ):
        pytest.skip("the books bridge (reservation) is not installed")
    cart = _cart(w, qty=2)
    _place(cart, method="branch_pickup", idempotency_key="res-1")
    _place(cart, method="branch_pickup", idempotency_key="res-1")
    w.env.invalidate_all()
    assert w.env["fix.stock.onhand"]._bucket(part, loc, "owned").reserved == 2.0


def test_f20_customer_cancels_before_dispatch_and_is_refunded(w):
    portal = w.portal
    order = _paid(w, _place(_cart(w, qty=1), method="branch_pickup"))
    order.with_user(portal).action_customer_cancel(reason="found it cheaper")
    s = order.sudo()
    assert (s.state, s.refund_due, s.cancelled_by_customer) == ("cancelled", 2500.0, True)
    assert s.cancelled_by_id == portal


def test_f20_no_self_cancel_once_dispatched_or_for_another_customer(w):
    order = _paid(w, _place(_cart(w, qty=1), method="standard_delivery"))
    stranger_partner = w.env["res.partner"].create({"name": "R2 stranger"})
    stranger = _mk(w.env, "a4r2_stranger", portal_partner=stranger_partner)
    with pytest.raises(UserError, match="own order"), w.env.cr.savepoint():
        order.with_user(stranger).action_customer_cancel()
    with pytest.raises(UserError, match="own order"), w.env.cr.savepoint():
        order.with_user(w.operator).action_customer_cancel()  # staff use action_cancel
    order.with_user(w.operator).action_dispatch(carrier_consignment_id=_consignment(w).id)
    with pytest.raises(UserError, match="before it is dispatched"), w.env.cr.savepoint():
        order.with_user(w.portal).action_customer_cancel()
    assert order.sudo().state == "dispatched"


# ================================================================ API (F19 / F20)
class _Browser:
    def __init__(self, env, user):
        self.env = env(user=user.id)
        self.session = http.Session(http.get_default_session(), "sid-%s" % id(self), new=True)


@contextmanager
def _in(browser):
    with patch.object(storefront_api, "request", browser):
        yield StorefrontApiController()


def test_f19_catalogue_lists_only_published_classified_items(w):
    unpublished = w.env["product.template"].create(
        {"name": "R2 Unpublished Cable", "sale_ok": True}
    )
    released_card(w.env, unpublished, 100.0)  # priced, but not on the M37 catalogue
    withdrawn = w.env["product.template"].create({"name": "R2 Withdrawn Item", "sale_ok": True})
    released_card(w.env, withdrawn, 100.0)
    item = published_item(w.env, withdrawn)
    item._guarded().write({"state": "approved", "is_published": False})  # unpublished
    with _in(_Browser(w.env, w.env.ref("base.public_user"))) as api:
        names = {p["name"] for p in api.catalogue(limit=200, search="R2 ")["products"]}
        names |= {p["name"] for p in api.catalogue(limit=200, search="A4 SF")["products"]}
        refused = api.get_or_update_cart(product_id=unpublished.id, quantity=1)
    assert "A4 SF Charger" in names
    assert not names & {"R2 Unpublished Cable", "R2 Withdrawn Item"}
    assert refused["error"]["code"] == "PRODUCT_NOT_FOUND"


def test_f19_catalogue_filters_by_device_compatibility(w):
    env = w.env
    brand = env["fix.brand"].create({"name": "R2 Brand", "code": "R2B%d" % next(_SEQ)})
    fits = env["fix.device.model"].create({"name": "R2 Fits", "brand_id": brand.id})
    other = env["fix.device.model"].create({"name": "R2 Other", "brand_id": brand.id})
    item = w.product.sudo().catalogue_item_id
    env["fix.model.compatibility"].sudo().create(
        {"item_id": item.id, "device_model_id": fits.id, "compatible": True}
    )
    env["fix.model.compatibility"].sudo().create(
        {"item_id": item.id, "device_model_id": other.id, "compatible": False, "note": "no fit"}
    )
    with _in(_Browser(env, env.ref("base.public_user"))) as api:
        yes = api.catalogue(search="A4 SF Charger", device_model_id=fits.id)["products"]
        no = api.catalogue(search="A4 SF Charger", device_model_id=other.id)["products"]
        bad = api.catalogue(device_model_id=999999999)
    assert [p["id"] for p in yes] == [w.product.id]
    assert no == []
    assert bad["error"]["code"] == "DEVICE_MODEL_NOT_FOUND"


def test_f20_api_checkout_replay_and_self_cancel(w):
    browser = _Browser(w.env, w.portal)
    _fee_product(w, 100.0)
    with _in(browser) as api:
        api.get_or_update_cart(product_id=w.product.id, quantity=1)
        first = api.checkout(
            shipping_method="standard_delivery", payment_rail="bkash", idempotency_key="api-key-1"
        )
        again = api.checkout(
            shipping_method="standard_delivery", payment_rail="bkash", idempotency_key="api-key-1"
        )
        assert "error" not in first, first
        assert again["order_id"] == first["order_id"]
        assert (first["delivery_fee_bdt"], first["total_bdt"]) == ("115.00", "2,615.00")
        out = api.cancel_order(order_id=first["order_id"], reason="changed my mind")
    assert out["state"] == "cancelled"
    other = _Browser(
        w.env,
        _mk(
            w.env, "a4r2_other_portal", portal_partner=w.env["res.partner"].create({"name": "R2 X"})
        ),
    )
    order2 = _place(_cart(w, qty=1), method="branch_pickup")
    with _in(other) as api:
        assert api.cancel_order(order_id=order2.id)["error"]["code"] == "ORDER_NOT_FOUND"


def test_f14_api_quote_and_voucher_error(w):
    promo = _voucher(w, value=10.0)
    with _in(_Browser(w.env, w.portal)) as api:
        api.get_or_update_cart(product_id=w.product.id, quantity=2)
        quote = api.checkout_quote(shipping_method="branch_pickup", voucher_code=promo.code)
        bad = api.checkout(shipping_method="branch_pickup", voucher_code="NOPE-R2")
    assert (quote["discount_bdt"], quote["total_bdt"]) == ("500.00", "4,500.00")
    assert bad["error"]["code"] == "VOUCHER_NOT_APPLICABLE"


# ================================================================ M38-F8
def _delivered(w, qty=3):
    order = _paid(w, _place(_cart(w, qty=qty), method="branch_pickup"))
    order.with_user(w.operator).action_dispatch()
    order.with_user(w.operator).action_deliver()
    return order


def _line_return(w, order, qty, user=None, **vals):
    line = order.sudo().line_ids.filtered(lambda ln: ln.line_type == "product")[:1]
    return (
        w.env["fix.storefront.return"]
        .with_user(user or w.operator)
        .create(
            dict(
                {
                    "order_id": order.id,
                    "customer_id": order.customer_id.id,
                    "reason": "defective",
                    "line_ids": [Command.create({"order_line_id": line.id, "quantity": qty})],
                },
                **vals,
            )
        )
    )


def test_f8_a_return_names_its_lines_and_refunds_what_they_cost(w):
    order = _delivered(w, qty=3)
    ret = _line_return(w, order, 1)
    rl = ret.sudo().line_ids
    assert (rl.quantity, rl.unit_refund, rl.amount) == (1.0, 2500.0, 2500.0)
    assert ret.sudo().refund_amount == 2500.0  # defaults to what the lines cost
    # the refund cannot exceed what the named lines cost
    with pytest.raises(ValidationError, match="lines returned"), w.env.cr.savepoint():
        ret.with_user(w.operator).write({"refund_amount": 2600.0})
    # the server, never the caller, sets what a line cost
    with pytest.raises(UserError), w.env.cr.savepoint():
        rl.with_user(w.operator).write({"unit_refund": 9999.0})


def test_f8_never_more_units_than_were_sold(w):
    order = _delivered(w, qty=3)
    with pytest.raises(ValidationError, match="sold 3"), w.env.cr.savepoint():
        _line_return(w, order, 4)
    _line_return(w, order, 2)
    with pytest.raises(ValidationError, match="sold 3"), w.env.cr.savepoint():
        _line_return(w, order, 2)
    third = _line_return(w, order, 1)  # 2 + 1 = 3: the last unit
    assert third.sudo().line_ids.quantity == 1.0


def test_f8_a_rejected_return_frees_its_units(w):
    order = _delivered(w, qty=2)
    first = _line_return(w, order, 2)
    first.with_user(w.operator).action_reject(reason="not received")
    again = _line_return(w, order, 2)
    assert again.sudo().line_ids.quantity == 2.0


def test_f8_voucher_share_reduces_the_line_refund(w):
    promo = _voucher(w, value=10.0)
    order = _paid(w, _place(_cart(w, qty=2), method="branch_pickup", voucher_code=promo.code))
    order.with_user(w.operator).action_dispatch()
    order.with_user(w.operator).action_deliver()
    ret = _line_return(w, order, 1)
    # the customer paid 4,500.00 for 2: one unit refunds 2,250.00, not 2,500.00
    assert ret.sudo().line_ids.unit_refund == 2250.0 and ret.sudo().refund_amount == 2250.0


def test_f8_lines_frozen_once_authorised_and_no_mixing(w):
    order = _delivered(w, qty=3)
    ret = _line_return(w, order, 1)
    ret.with_user(w.operator).action_approve()
    with pytest.raises(UserError, match="authorised"), w.env.cr.savepoint():
        ret.sudo().line_ids.write({"quantity": 2.0})
    # one order is returned line by line or as a whole, never both
    with pytest.raises(ValidationError, match="line by line"), w.env.cr.savepoint():
        w.env["fix.storefront.return"].with_user(w.operator).create(
            {
                "order_id": order.id,
                "customer_id": order.customer_id.id,
                "reason": "defective",
                "refund_amount": 100.0,
            }
        )


def test_f8_a_line_return_restocks_only_the_returned_refurb_device(w, refurb):
    """A05's refurbished return path brings back every device of the order
    on a whole-order return; a line return brings back only its own."""
    item = refurb("A4R2-SN-%d" % next(_SEQ))
    cart = w.env["fix.storefront.cart"].with_user(w.clerk).create({"customer_id": w.customer.id})
    Line = w.env["fix.storefront.cart.line"].with_user(w.clerk)
    Line.create({"cart_id": cart.id, "product_id": w.product.id, "graded_stock_id": item.id})
    Line.create({"cart_id": cart.id, "product_id": w.product.id, "quantity": 1})
    cart.write({"terms_method": "checkbox"})
    cart.with_user(w.operator).action_record_terms()
    order = _paid(w, _place(cart, method="branch_pickup"))
    order.with_user(w.operator).action_dispatch()
    order.with_user(w.operator).action_deliver()
    assert item.state == "sold"
    plain = order.sudo().line_ids.filtered(
        lambda ln: ln.line_type == "product" and not ln.graded_stock_id
    )
    ret = (
        w.env["fix.storefront.return"]
        .with_user(w.operator)
        .create(
            {
                "order_id": order.id,
                "customer_id": order.customer_id.id,
                "reason": "defective",
                "line_ids": [Command.create({"order_line_id": plain.id, "quantity": 1})],
            }
        )
    )
    ret.with_user(w.operator).action_approve()
    ret.with_user(w.operator2).action_receive_and_inspect(condition="grade_a")
    assert item.state == "sold"  # the device was not returned


# ================================================================ wiring
class TestDeployment:
    def test_wiring(self, odoo_env):
        env = odoo_env
        acl = (
            env["ir.model.access"]
            .sudo()
            .search([("model_id.model", "=", "fix.storefront.return.line")])
        )
        assert acl.filtered(lambda a: a.group_id == env.ref("base.group_user") and a.perm_read)
        assert not acl.filtered(
            lambda a: a.group_id == env.ref("base.group_portal") and a.perm_write
        )
        assert env.ref("cd_storefront.rule_fix_storefront_return_line_company")
        from odoo.addons.cd_p03_portal.controllers.a04 import m38

        assert "fix.storefront.return.line" in m38.SURFACES
        assert StorefrontApiController.cancel_order.original_routing["auth"] == "public"
        assert StorefrontApiController.checkout_quote.original_routing["auth"] == "public"
        assert "storefront_voucher" in env["fix.promotion"]._fields
