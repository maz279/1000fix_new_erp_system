# ruff: noqa: F811  (the storefront fixture is imported and used as a parameter)
"""A04 ERP audit (20 Nov 2026), stream B4 - M38 storefront controls.

Each test drives the storefront as its users do (assisted-sales clerk,
storefront operator, the gateway callback / API as the superuser) against the
ORM, and is built so that only the new rule can refuse it:

  M38-F1  the price is M11's released storefront price, never list_price; no
          released price, no sale; only priced items are listed
  M38-F4  whole units only
  M38-F5  an assisted-sales role captures carts; the capturer never records
          the customer's terms or the client's approval
  M38-F7  a prepaid order past its payment timeout is cancelled by the job
  M38-F11 the exposure policy reads M15 stock (fix.stock.onhand)
  M38-F12 COD needs an approved COD rule; a guest order belongs to the
          customer of its mobile number
  M38-F13 a prepaid rail needs its live M65 gateway (and, online, a secret)
"""

from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_storefront.controllers import storefront_api
from odoo.exceptions import AccessError, UserError, ValidationError

from .test_a04_c2_c13_storefront import (  # noqa: F401  (fixture)
    STOREFRONT_EXCL_PRICE,
    _mk,
    _placed,
    released_card,
    w,
)

REFUSED = (UserError, ValidationError, AccessError)
SF = "cd_storefront.group_fix_storefront_"


def _cart(w, user=None, qty=1, product=None, **vals):
    cart = (
        w.env["fix.storefront.cart"]
        .with_user(user or w.clerk)
        .create(dict({"customer_id": w.customer.id}, **vals))
    )
    w.env["fix.storefront.cart.line"].with_user(user or w.clerk).create(
        {"cart_id": cart.id, "product_id": (product or w.product).id, "quantity": qty}
    )
    return cart


# ================================================================ M38-F1
def test_f1_line_price_is_m11_not_list_price(w):
    """The cart line takes the M11 card (VAT-exclusive 2,173.91, BDT 2,500.00
    with VAT) - list_price is moved to 1.00 to prove it is not read - and
    the order carries the price lock."""
    w.product.sudo().with_context(install_mode=True).write({"list_price": 1.0})
    order = _placed(w, qty=2)
    line = order.sudo().line_ids
    assert line.unit_price_excl == STOREFRONT_EXCL_PRICE
    assert line.unit_price == 2500.0
    assert line.price_card_id and line.price_source == "card"
    assert order.sudo().total_amount == 5000.0


def test_f1_no_released_price_no_sale(w):
    """fix_real has no M11 prices: the storefront sells nothing (fail closed),
    even with a list_price and even for the superuser API."""
    other = w.env["product.template"].create(
        {"name": "A4 SF Unpriced", "list_price": 1150.0, "sale_ok": True}
    )
    cart = w.env["fix.storefront.cart"].with_user(w.clerk).create({"customer_id": w.customer.id})
    for env in (
        w.env["fix.storefront.cart.line"].with_user(w.clerk),
        w.env["fix.storefront.cart.line"].sudo(),
    ):
        with pytest.raises(UserError, match="cannot be sold online"), w.env.cr.savepoint():
            env.create(
                {"cart_id": cart.id, "product_id": other.id, "quantity": 1, "unit_price": 1150}
            )


def test_f1_price_withdrawn_while_cart_waits_refuses_the_order(w):
    cart = _cart(w)
    w.env["fix.rate.card"].sudo().search(
        [("product_code", "=", w.product.product_variant_id.default_code)]
    )._guarded().write({"state": "retired"})
    with pytest.raises(UserError, match="cannot be sold online"), w.env.cr.savepoint():
        cart.action_place_order(shipping_method="branch_pickup", payment_rail="bkash")


def test_f1_a_typed_price_never_stands(w):
    cart = _cart(w)
    line = cart.line_ids
    with pytest.raises(UserError, match="comes from M11"), w.env.cr.savepoint():
        line.with_user(w.clerk).write({"unit_price": 1.0})
    # a tampered line is re-priced at placement
    line.sudo().write({"unit_price": 1.0, "unit_price_excl": 0.87})
    order = cart.action_place_order(shipping_method="branch_pickup", payment_rail="bkash")
    assert order.sudo().line_ids.unit_price == 2500.0


def test_f1_catalogue_lists_only_priced_items(w):
    unpriced = w.env["product.template"].create(
        {"name": "A4 SF Catalogue Unpriced", "list_price": 999.0, "sale_ok": True}
    )
    # the catalogue lists a product only when this pricing answers
    Line = w.env["fix.storefront.cart.line"]
    assert Line._sf_m11_price(w.product)["incl"] == 2500.0
    with pytest.raises(UserError, match="cannot be sold online"):
        Line._sf_m11_price(unpriced)
    # and the collection publish uses it too: an unpriced item is not merchandised
    coll = (
        w.env["fix.storefront.collection"]
        .sudo()
        .create(
            {
                "name": "B4 set",
                "name_bn": "B4",
                "code": "B4SET%s" % unpriced.id,
                "product_ids": [(6, 0, unpriced.ids)],
            }
        )
    )
    with pytest.raises(UserError, match="cannot be sold online"):
        coll.action_publish()


# ================================================================ M38-F4
def test_f4_fractional_quantity_refused(w):
    cart = w.env["fix.storefront.cart"].with_user(w.clerk).create({"customer_id": w.customer.id})
    with pytest.raises(ValidationError, match="whole units"), w.env.cr.savepoint():
        w.env["fix.storefront.cart.line"].with_user(w.clerk).create(
            {"cart_id": cart.id, "product_id": w.product.id, "quantity": 0.01}
        )
    line = (
        w.env["fix.storefront.cart.line"]
        .with_user(w.clerk)
        .create({"cart_id": cart.id, "product_id": w.product.id, "quantity": 1})
    )
    with pytest.raises(ValidationError, match="whole units"), w.env.cr.savepoint():
        line.with_user(w.clerk).write({"quantity": 1.5})


# ================================================================ M38-F5
def test_f5_a_plain_internal_user_cannot_capture_a_cart(w):
    plain = _mk(w.env, "a4b4_plain")
    with pytest.raises(AccessError), w.env.cr.savepoint():
        w.env(user=plain)["fix.storefront.cart"].create({"customer_id": w.customer.id})


def test_f5_terms_and_client_approval_need_a_role_and_another_person(w):
    cart = _cart(w)
    cart.sudo().write({"terms_method": "checkbox"})
    plain = _mk(w.env, "a4b4_plain2")
    with pytest.raises(UserError, match="role"), w.env.cr.savepoint():
        cart.with_user(plain).action_record_terms()
    with pytest.raises(UserError, match="captured cart"), w.env.cr.savepoint():
        cart.with_user(w.clerk).action_record_terms()
    cart.with_user(w.operator).action_record_terms()
    assert cart.sudo().terms_accepted_by_id == w.operator
    # the client's approval: an operator, never the capturing clerk
    client = w.env["res.partner"].create({"name": "A4 B4 Corp", "is_company": True})
    approver = w.env["res.partner"].create({"name": "A4 B4 Approver", "parent_id": client.id})
    acct = (
        w.env["fix.storefront.corporate.account"]
        .sudo()
        .create({"partner_id": client.id, "approver_ids": [(6, 0, approver.ids)]})
    )
    acct._guarded().write({"state": "active"})
    corp = (
        w.env["fix.storefront.cart"]
        .with_user(w.clerk)
        .create({"customer_id": client.id, "corporate_account_id": acct.id, "po_reference": "PO-1"})
    )
    w.env["fix.storefront.cart.line"].with_user(w.clerk).create(
        {"cart_id": corp.id, "product_id": w.product.id, "quantity": 1}
    )
    corp.sudo().write({"client_approver_id": approver.id, "client_approval_ref": "mail-7"})
    with pytest.raises(UserError, match="Storefront Operator"), w.env.cr.savepoint():
        corp.with_user(w.clerk).action_record_client_approval()
    corp.with_user(w.operator).action_record_client_approval()
    assert corp.sudo().client_approval_recorded_by_id == w.operator


# ================================================================ M38-F7
def test_f7_unpaid_prepaid_order_expires(w):
    order = _placed(w, rail="bkash", method="branch_pickup")
    assert order.sudo().payment_expires_at
    cod = _placed(w, rail="cod", method="branch_pickup")
    assert not cod.sudo().payment_expires_at
    w.env.cr.execute(
        "UPDATE fix_storefront_order SET payment_expires_at = %s WHERE id IN %s",
        (fields.Datetime.now() - timedelta(minutes=1), (order.id, cod.id)),
    )
    w.env.invalidate_all()
    w.env["fix.storefront.order"].cron_expire_unpaid_orders()
    order.invalidate_recordset()
    cod.invalidate_recordset()
    assert order.sudo().state == "cancelled"
    assert cod.sudo().state == "pending_payment"  # COD never expires


# ================================================================ M38-F11
def test_f11_exposure_reads_m15_stock(w):
    env = w.env
    w.product.is_storable = True  # a stocked item
    variant = w.product.product_variant_id
    part = env["fix.spare.part"].create(
        {
            "name": "B4 exp",
            "part_number": "B4EXP-%s" % w.product.id,
            "unit_cost": 10.0,
            "product_id": variant.id,
        }
    )
    loc = env["fix.stock.location"].create(
        {
            "name": "B4 store",
            "code": "B4ST%s" % w.product.id,
            "location_type": "central",
            "operating_unit_id": w.ou.id,
        }
    )
    env["fix.stock.onhand"]._apply(part, loc, "owned", 5.0, 10.0)
    policy = (
        env["fix.stock.exposure.policy"]
        .sudo()
        .create({"name": "B4 exposure", "product_id": w.product.id, "buffer_qty": 2})
    )
    policy._guarded().write({"state": "active"})
    Exposure = env["fix.stock.exposure.policy"]
    Exposure._sf_check_exposure(w.product, 3, env.company)  # 5 on hand - 2 buffer
    with pytest.raises(UserError, match="Only 3"):
        Exposure._sf_check_exposure(w.product, 4, env.company)


# ================================================================ M38-F12
def test_f12_cod_needs_an_approved_rule(w):
    w.env["fix.storefront.cod.rule"].sudo().search([])._guarded().write({"state": "retired"})
    with pytest.raises(UserError, match="no approved COD rule"), w.env.cr.savepoint():
        _placed(w, rail="cod", method="branch_pickup")


def test_f12_guest_partner_is_per_mobile_number(w):
    env = w.env(su=True)
    a = storefront_api.guest_customer_for_phone(env, "+880 1711-000111")
    b = storefront_api.guest_customer_for_phone(env, "01711000111")
    c = storefront_api.guest_customer_for_phone(env, "01811000222")
    assert a == b and a != c and a.phone == "01711000111"
    assert not storefront_api.guest_customer_for_phone(env, "12345")


# ================================================================ M38-F13
def test_f13_a_rail_with_no_gateway_takes_no_order(w):
    w.env["fix.payment.gateway"].sudo().with_context(active_test=False).search(
        [("provider", "=ilike", "nagad")]
    ).unlink()
    with pytest.raises(UserError, match="not configured"), w.env.cr.savepoint():
        _placed(w, rail="nagad", method="branch_pickup")


def test_f13_an_online_checkout_needs_the_callback_secret(w):
    w.env["ir.config_parameter"].sudo().set_param("cd_storefront.gateway_secret.bkash", "")
    cart = w.env["fix.storefront.cart"].sudo().create({"customer_id": w.customer.id})
    w.env["fix.storefront.cart.line"].sudo().create(
        {"cart_id": cart.id, "product_id": w.product.id, "quantity": 1}
    )
    assert cart.channel == "web"
    with pytest.raises(UserError, match="callback secret"), w.env.cr.savepoint():
        cart.action_place_order(shipping_method="branch_pickup", payment_rail="bkash")


# ================================================================ wiring
class TestDeployment:
    def test_wiring(self, odoo_env):
        env = odoo_env
        cron = env.ref("cd_storefront.ir_cron_storefront_expire_unpaid")
        assert cron.active and "cron_expire_unpaid_orders" in cron.code
        assisted = env.ref("cd_storefront.group_fix_storefront_assisted_sales")
        # the post-migrate script: every Storefront Manager holds assisted sales
        manager = env.ref("cd_storefront.group_fix_storefront_manager")
        assert assisted in manager.implied_ids
        assert manager.all_user_ids <= assisted.all_user_ids
        acl = (
            env["ir.model.access"]
            .sudo()
            .search(
                [
                    ("model_id.model", "=", "fix.storefront.cart"),
                    ("group_id", "=", env.ref("base.group_user").id),
                ]
            )
        )
        assert acl and not any(acl.mapped("perm_create")) and not any(acl.mapped("perm_write"))
        from odoo.addons.cd_p03_portal.controllers.a04 import m38

        acts = m38.SURFACES["fix.storefront.order"]["actions"]
        assert {"action_retry_posting", "action_record_customer_nid"} <= acts
        assert released_card  # helper import kept for the books tests
