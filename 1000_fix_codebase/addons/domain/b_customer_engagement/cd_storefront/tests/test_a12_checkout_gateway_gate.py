"""A12 audit P1-4 / D8 (M65 gateways -> M38 checkout).

The M65 payment-gateway master existed but checkout never read it: a
sandbox or suspended gateway could take a live order. Checkout now refuses
a rail whose gateway is configured but not LIVE (state=active AND
mode=live). A rail with no gateway master keeps today's behaviour so
tenants that never configured M65 are not locked out; cash on delivery
never touches a gateway at all.
"""

import pytest
from odoo.exceptions import UserError

from .test_a04_c2_c13_storefront import cod_rule, released_card


@pytest.fixture
def shop(odoo_env):
    env = odoo_env
    product = env["product.template"].create({"name": "A12 Router", "list_price": 1200.0})
    partner = env["res.partner"].create({"name": "A12 Checkout Customer"})
    # A04 ERP M38-F1/F12/F13: a released M11 price, the callback secrets and
    # an approved COD rule (configuration)
    released_card(env, product, 1043.48)
    cod_rule(env)
    for rail in ("bkash", "nagad"):
        env["ir.config_parameter"].sudo().set_param("cd_storefront.gateway_secret.%s" % rail, "s")

    def gateway(state="active", mode="live"):
        """Build a gateway through the SANCTIONED lifecycle (P1-4): every
        gateway is born draft in sandbox mode; activation is a guarded
        transition (draft->active, then sandbox->live), suspension needs a
        reason. Forging state/mode at create is refused by design."""
        rec = env["fix.payment.gateway"].create(
            {"provider": "bkash", "credential_ref": "vault://test/bkash"}
        )
        if state == "draft":
            pass  # born draft: no transition at all
        elif state == "suspended":
            rec.action_activate()  # draft -> active (sandbox is enough; the
            # refusal must come from the suspended state, not the mode)
            rec.action_suspend(reason="A12 gate fixture")
        elif mode == "live":
            rec.action_activate()  # draft -> active (still sandbox)
            rec.action_activate()  # active+sandbox -> active+live
        else:
            rec.action_activate()  # draft -> active, deliberately sandbox
        return rec

    def cart():
        cart = env["fix.storefront.cart"].create({"customer_id": partner.id})
        env["fix.storefront.cart.line"].create(
            {"cart_id": cart.id, "product_id": product.id, "quantity": 1, "unit_price": 1200.0}
        )
        return cart

    return env, cart, gateway


def test_a_live_gateway_takes_the_order(shop):
    _env, cart, gateway = shop
    gateway()
    order = cart().action_place_order(shipping_address="House 3, Dhaka", payment_rail="bkash")
    assert order.state == "pending_payment"
    assert order.payment_rail == "bkash"


def test_a_draft_gateway_refuses_checkout(shop):
    _env, cart, gateway = shop
    gateway(state="draft")
    with pytest.raises(UserError, match=r"checkout refused: gateway|not live for checkout"):
        cart().action_place_order(shipping_address="House 3, Dhaka", payment_rail="bkash")
    assert not cart().order_id, "no order may be created for a rail that is not live"


def test_a_sandbox_gateway_refuses_checkout(shop):
    _env, cart, gateway = shop
    gateway(mode="sandbox")
    with pytest.raises(UserError, match=r"checkout refused: gateway|not live for checkout"):
        cart().action_place_order(shipping_address="House 3, Dhaka", payment_rail="bkash")


def test_a_suspended_gateway_refuses_checkout(shop):
    _env, cart, gateway = shop
    gateway(state="suspended")
    with pytest.raises(UserError, match=r"checkout refused: gateway|not live for checkout"):
        cart().action_place_order(shipping_address="House 3, Dhaka", payment_rail="bkash")


def test_cash_on_delivery_never_touches_the_gateway(shop):
    _env, cart, gateway = shop
    gateway(state="suspended")
    order = cart().action_place_order(shipping_address="House 3, Dhaka", payment_rail="cod")
    assert order.state == "pending_payment"


def test_an_unconfigured_rail_takes_no_order(shop):
    # A04 ERP audit M38-F13 (supersedes the A12 "keeps today's behaviour"):
    # a rail with no gateway master took orders nobody could ever pay.
    env, cart, _gateway = shop
    env["fix.payment.gateway"].sudo().with_context(active_test=False).search(
        [("provider", "=ilike", "nagad")]
    ).unlink()
    with pytest.raises(UserError, match="not configured"):
        cart().action_place_order(shipping_address="House 3, Dhaka", payment_rail="nagad")
