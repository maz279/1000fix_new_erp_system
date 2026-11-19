# ruff: noqa: F811 - `w` is the shared fixture, imported for pytest
"""M38 capture audit (19 Nov 2026): the records each sub-module page captures,
and the rule the spec puts on each, run as non-admin users in the
transaction (a plain clerk, operators, a merchandiser, a payment officer and
Storefront Managers).
"""

import types
from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

from .test_a04_c2_c13_storefront import (
    _consignment,
    _mk,
    _paid,
    _placed,
    w,  # noqa: F401 - the shared storefront world
)

REFUSED = (UserError, ValidationError, AccessError)
SF = "cd_storefront.group_fix_storefront_"


@pytest.fixture
def c(w):
    env = w.env
    x = types.SimpleNamespace(w=w, env=env)
    x.merch = _mk(env, "m38c_merch", SF + "merchandiser")
    x.manager = _mk(env, "m38c_manager", SF + "manager")
    x.manager2 = _mk(env, "m38c_manager2", SF + "manager")
    x.officer = _mk(env, "m38c_officer", SF + "payment_officer")
    x.category = env["product.category"].create({"name": "M38C Parts"})
    x.sub_category = env["product.category"].create(
        {"name": "M38C Chargers", "parent_id": x.category.id}
    )
    w.product.categ_id = x.sub_category
    x.stocked = env["product.template"].create(
        {
            "name": "M38C Battery",
            "list_price": 1500.0,
            "sale_ok": True,
            "type": "consu",
            "is_storable": True,
            "categ_id": x.sub_category.id,
        }
    )
    x.warehouse = env["stock.warehouse"].search([("company_id", "=", env.company.id)], limit=1)
    return x


def _device(env, w, serial):
    model = env["fix.device.model"].search([], limit=1)
    if not model:
        brand = env["fix.brand"].create({"name": "M38C Brand", "code": "M38CB"})
        model = env["fix.device.model"].create({"name": "M38C Phone", "brand_id": brand.id})
    return env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": w.customer.id, "serial_number": serial}
    )


def _cart(w, user=None, product=None, qty=1, **vals):
    u = user or w.clerk
    cart = w.env["fix.storefront.cart"].with_user(u).create({"customer_id": w.customer.id, **vals})
    w.env["fix.storefront.cart.line"].with_user(u).create(
        {"cart_id": cart.id, "product_id": (product or w.product).id, "quantity": qty}
    )
    return cart


# ============================================================ page 1: content
def test_content_is_published_bilingual_by_a_merchandiser_then_fixed(c):
    env, w = c.env, c.w
    Content = env["fix.storefront.content"]
    with pytest.raises(AccessError), env.cr.savepoint():
        Content.with_user(w.clerk).create({"name": "x", "code": "X"})
    page = Content.with_user(c.merch).create(
        {"name": "Return policy", "code": "M38C-RP", "content_type": "policy", "body_en": "7 days"}
    )
    with pytest.raises(UserError, match="Bengali title"), env.cr.savepoint():
        page.with_user(c.merch).action_publish()
    page.with_user(c.merch).write({"name_bn": "ফেরত নীতি"})
    with pytest.raises(UserError, match="both English and Bengali"), env.cr.savepoint():
        page.with_user(c.merch).action_publish()
    page.with_user(c.merch).write({"body_bn": "৭ দিন"})
    with pytest.raises(UserError, match="role"), env.cr.savepoint():
        page.with_user(w.operator).action_publish()
    page.with_user(c.merch).action_publish()
    assert (page.state, page.published_by_id) == ("published", c.merch)
    with pytest.raises(UserError, match="cannot be changed"), env.cr.savepoint():
        page.with_user(c.merch).write({"body_en": "30 days"})
    with pytest.raises(UserError, match="workflow"), env.cr.savepoint():
        page.with_user(c.merch).write({"state": "draft"})
    banner = Content.with_user(c.merch).create(
        {"name": "Eid", "name_bn": "ঈদ", "code": "M38C-EID", "content_type": "banner"}
    )
    with pytest.raises(UserError, match="image"), env.cr.savepoint():
        banner.with_user(c.merch).action_publish()


# ============================================================ page 2: collections
def test_collections_merchandise_only_sellable_items(c):
    env, w = c.env, c.w
    Coll = env["fix.storefront.collection"]
    other = env["product.template"].create(
        {"name": "M38C Case", "list_price": 300.0, "sale_ok": True}
    )
    cross = Coll.with_user(c.merch).create(
        {
            "name": "Charger companions",
            "name_bn": "চার্জার সঙ্গী",
            "code": "M38C-X",
            "collection_type": "cross_sell",
            "product_ids": [(6, 0, [other.id])],
        }
    )
    with pytest.raises(UserError, match="alongside one item"), env.cr.savepoint():
        cross.with_user(c.merch).action_publish()
    with pytest.raises(ValidationError, match="alongside itself"), env.cr.savepoint():
        cross.with_user(c.merch).write({"anchor_product_id": other.id})
    cross.with_user(c.merch).write({"anchor_product_id": w.product.id})
    other.sale_ok = False
    with pytest.raises(UserError, match="not for sale"), env.cr.savepoint():
        cross.with_user(c.merch).action_publish()
    other.sale_ok = True
    cross.with_user(c.merch).action_publish()
    assert cross.state == "published"
    with pytest.raises(UserError, match="cannot be changed"), env.cr.savepoint():
        cross.with_user(c.merch).write({"product_ids": [(5, 0, 0)]})


# ============================================================ page 3: assisted cart
def test_an_assisted_cart_is_stamped_and_placed_through_checkout(c):
    w = c.w
    cart = _cart(w)
    assert (cart.channel, cart.assisted_by_id) == ("assisted", w.clerk)
    cart.with_user(w.clerk).write(
        {"delivery_address": "Road 9, Dhaka", "delivery_method": "express_courier"}
    )
    assert cart.with_user(w.clerk).action_place_assisted_order()
    order = cart.order_id.sudo()
    assert (order.shipping_address, order.shipping_method) == ("Road 9, Dhaka", "express_courier")
    assert order.total_amount == 2500.0
    with pytest.raises(UserError, match="cannot be changed|fixed"), w.env.cr.savepoint():
        cart.with_user(w.clerk).write({"delivery_address": "elsewhere"})
    with pytest.raises(UserError, match="fixed"), w.env.cr.savepoint():
        w.env["fix.storefront.cart.line"].with_user(w.clerk).create(
            {"cart_id": cart.id, "product_id": w.product.id}
        )


def test_the_workspace_grid_may_repost_the_servers_price(c):
    """The P03 grid posts every column: an unchanged price is not a hand-set one."""
    w = c.w
    cart = _cart(w)
    line = cart.line_ids
    line.with_user(w.clerk).write({"unit_price": line.unit_price, "quantity": 2})
    assert line.quantity == 2
    with pytest.raises(UserError, match="catalogue"), w.env.cr.savepoint():
        line.with_user(w.clerk).write({"unit_price": 1.0})


def test_a_refurbished_unit_needs_the_terms_accepted(c):
    env, w = c.env, c.w
    dev = _device(env, w, "M38C-SN-1")
    item = env["fix.graded.stock"].create(
        {
            "device_id": dev.id,
            "grade_id": env["fix.refurb.grade"].search([], limit=1).id,
            "acquisition_cost": 5000.0,
            "resale_price": 9000.0,
        }
    )
    cart = env["fix.storefront.cart"].with_user(w.clerk).create({"customer_id": w.customer.id})
    env["fix.storefront.cart.line"].with_user(w.clerk).create(
        {"cart_id": cart.id, "product_id": w.product.id, "graded_stock_id": item.id}
    )
    assert cart.has_refurbished
    with pytest.raises(UserError, match="terms"), env.cr.savepoint():
        cart.action_place_order(shipping_address="Road 7")
    cart.with_user(w.clerk).write({"terms_method": "otp"})
    with pytest.raises(UserError, match="reference"), env.cr.savepoint():
        cart.with_user(w.clerk).action_record_terms()
    cart.with_user(w.clerk).write({"terms_reference": "OTP-55121"})
    with pytest.raises(UserError, match="workflow"), env.cr.savepoint():
        cart.with_user(w.clerk).write({"terms_accepted_at": fields.Datetime.now()})
    cart.with_user(w.clerk).action_record_terms()
    order = cart.action_place_order(shipping_address="Road 7")
    assert order and item.state == "reserved"


# ============================================================ page 4: COD
def test_cod_is_offered_only_within_the_active_rule(c):
    env, w = c.env, c.w
    # no rule: today's behaviour
    assert _placed(w, rail="cod")
    rule = (
        env["fix.storefront.cod.rule"]
        .with_user(c.officer)
        .create({"name": "COD 2026", "max_order_value": 3000.0, "max_open_cod_orders": 2})
    )
    with pytest.raises(AccessError), env.cr.savepoint():
        env["fix.storefront.cod.rule"].with_user(w.clerk).create(
            {"name": "x", "max_order_value": 1.0}
        )
    with pytest.raises(UserError, match="role"), env.cr.savepoint():
        rule.with_user(c.officer).action_activate()
    rule.with_user(c.manager).action_activate()
    assert rule.state == "active"
    with pytest.raises(UserError, match="up to BDT 3000"), env.cr.savepoint():
        _placed(w, qty=2, rail="cod")
    assert _placed(w, rail="cod")  # the second open COD order
    with pytest.raises(UserError, match="open cash-on-delivery"), env.cr.savepoint():
        _placed(w, rail="cod")
    assert _placed(w, qty=2, rail="bkash")  # prepaid is unaffected
    with pytest.raises(UserError, match="cannot be changed"), env.cr.savepoint():
        rule.with_user(c.officer).write({"max_order_value": 99999.0})


def test_a_cod_rule_is_not_approved_by_its_author(c):
    env = c.env
    rule = (
        env["fix.storefront.cod.rule"]
        .with_user(c.manager)
        .create({"name": "COD self", "max_order_value": 3000.0})
    )
    with pytest.raises(UserError, match="recorded by you"), env.cr.savepoint():
        rule.with_user(c.manager).action_activate()
    rule.with_user(c.manager2).action_activate()
    newer = (
        env["fix.storefront.cod.rule"]
        .with_user(c.officer)
        .create(
            {
                "name": "COD history",
                "max_order_value": 50000.0,
                "history_value": 1000.0,
                "min_delivered_orders": 1,
            }
        )
    )
    newer.with_user(c.manager).action_activate()
    assert (rule.state, newer.state) == ("retired", "active")
    with pytest.raises(UserError, match="delivered orders"), env.cr.savepoint():
        _placed(c.w, rail="cod")


# ============================================================ page 5: order changes
def test_an_order_change_is_applied_by_another_operator_before_dispatch(c):
    env, w = c.env, c.w
    order = _placed(w)
    Change = env["fix.storefront.order.change"]
    change = Change.with_user(w.clerk).create(
        {
            "order_id": order.id,
            "change_type": "address",
            "new_address": "Flat 4B, Chattogram",
            "reason": "moved",
        }
    )
    assert change.name.startswith("SFC/")
    with pytest.raises(UserError, match="role"), env.cr.savepoint():
        change.with_user(w.clerk).action_apply()
    own = Change.with_user(w.operator).create(
        {
            "order_id": order.id,
            "change_type": "method",
            "new_method": "branch_pickup",
            "reason": "x",
        }
    )
    with pytest.raises(UserError, match="recorded by you"), env.cr.savepoint():
        own.with_user(w.operator).action_apply()
    change.with_user(w.operator).action_apply()
    assert order.sudo().shipping_address == "Flat 4B, Chattogram"
    assert (change.state, change.decided_by_id) == ("applied", w.operator)
    with pytest.raises(ValidationError, match="names the new"), env.cr.savepoint():
        Change.with_user(w.clerk).create(
            {"order_id": order.id, "change_type": "slot", "reason": "x"}
        )
    # paid: the delivery mode is fixed; dispatched: nothing changes here
    _paid(w, order)
    with pytest.raises(UserError, match="paid"), env.cr.savepoint():
        Change.with_user(w.clerk).create(
            {
                "order_id": order.id,
                "change_type": "method",
                "new_method": "express_courier",
                "reason": "x",
            }
        )
    order.with_user(w.operator).action_dispatch(carrier_consignment_id=_consignment(w).id)
    with pytest.raises(UserError, match="dispatched"), env.cr.savepoint():
        Change.with_user(w.clerk).create(
            {"order_id": order.id, "change_type": "address", "new_address": "y", "reason": "x"}
        )


def test_a_slot_change_books_the_new_slot(c):
    env, w = c.env, c.w
    today = fields.Date.context_today(env.user)
    Slot = env["fix.storefront.slot"].with_user(w.operator)
    full = Slot.create({"name": "M38C full", "slot_date": today, "capacity": 1})
    free = Slot.create({"name": "M38C free", "slot_date": today, "capacity": 1})
    order = _placed(w, slot_id=full.id)
    _placed(w)  # another order, no slot
    blocked = _placed(w)
    change = (
        env["fix.storefront.order.change"]
        .with_user(w.clerk)
        .create(
            {"order_id": blocked.id, "change_type": "slot", "new_slot_id": full.id, "reason": "x"}
        )
    )
    with pytest.raises(UserError, match="full"), env.cr.savepoint():
        change.with_user(w.operator2).action_apply()
    move = (
        env["fix.storefront.order.change"]
        .with_user(w.clerk)
        .create(
            {"order_id": order.id, "change_type": "slot", "new_slot_id": free.id, "reason": "later"}
        )
    )
    move.with_user(w.operator2).action_apply()
    assert order.sudo().slot_id == free
    assert (full.booked, free.booked) == (0, 1)


# ============================================================ page 6: exposure
def _stock(c, product, qty):
    variant = product.product_variant_id
    c.env["stock.quant"].sudo()._update_available_quantity(variant, c.warehouse.lot_stock_id, qty)


def _policy(c, author=None, **vals):
    rec = (
        c.env["fix.stock.exposure.policy"]
        .with_user(author or c.w.operator)
        .create({"name": "M38C exposure", **vals})
    )
    rec.with_user(c.manager).action_activate()
    return rec


def test_only_exposed_stock_is_sold_online(c):
    env, w = c.env, c.w
    _stock(c, c.stocked, 10)
    # no policy: today's behaviour
    assert _cart(w, product=c.stocked, qty=10)
    policy = _policy(c, category_id=c.category.id, buffer_qty=2, buffer_pct=30.0)
    assert policy._sf_exposable_qty(c.stocked) == 7  # 10 less max(2, 3)
    with pytest.raises(UserError, match="Only 7"), env.cr.savepoint():
        _cart(w, product=c.stocked, qty=8)
    cart = _cart(w, product=c.stocked, qty=7)
    with pytest.raises(UserError, match="Only 7"), env.cr.savepoint():
        cart.line_ids.with_user(w.clerk).write({"quantity": 9})
    # an item's own policy wins over its category's: withdrawn from sale
    _policy(c, product_id=c.stocked.id, enabled=False)
    with pytest.raises(UserError, match="withdrawn"), env.cr.savepoint():
        _cart(w, product=c.stocked)
    # ... and is re-checked at placement (T-05)
    with pytest.raises(UserError, match="withdrawn"), env.cr.savepoint():
        cart.action_place_order(shipping_address="Road 7")


def test_exposure_strict_mode_and_policy_rules(c):
    env, w = c.env, c.w
    with (
        pytest.raises(ValidationError, match="either one item or one category"),
        env.cr.savepoint(),
    ):
        env["fix.stock.exposure.policy"].with_user(w.operator).create({"name": "both"})
    with pytest.raises(AccessError), env.cr.savepoint():
        env["fix.stock.exposure.policy"].with_user(w.clerk).create(
            {"name": "x", "product_id": c.stocked.id}
        )
    own = (
        env["fix.stock.exposure.policy"]
        .with_user(c.manager)
        .create({"name": "self", "product_id": c.stocked.id})
    )
    with pytest.raises(UserError, match="recorded by you"), env.cr.savepoint():
        own.with_user(c.manager).action_activate()
    env["ir.config_parameter"].sudo().set_param("cd_storefront.exposure_policy_required", "1")
    with pytest.raises(UserError, match="not covered"), env.cr.savepoint():
        _cart(w)


# ============================================================ page 7: return policy
def test_the_return_window_and_fee_follow_the_category_policy(c):
    env, w = c.env, c.w
    order = _paid(w, _placed(w))
    default = order.sudo()._sf_window_days()
    policy = (
        env["fix.storefront.return.policy"]
        .with_user(w.operator)
        .create(
            {
                "name": "Chargers 15 days",
                "category_id": c.category.id,
                "window_days": 15,
                "restocking_fee_pct": 10.0,
            }
        )
    )
    assert order.sudo()._sf_window_days() == default  # a draft changes nothing
    policy.with_user(c.manager).action_activate()
    assert order.sudo()._sf_window_days() == 15  # the parent category's policy
    assert order.sudo()._sf_restocking_pct() == 10.0
    start = fields.Datetime.context_timestamp(order, order.sudo().payment_date).date()
    assert order.sudo().return_deadline == start + timedelta(days=15)
    ret = (
        env["fix.storefront.return"]
        .with_user(w.operator)
        .create(
            {
                "order_id": order.id,
                "customer_id": w.customer.id,
                "reason": "changed_mind",
                "refund_amount": 2500.0,
            }
        )
    )
    assert ret._sf_refund_after_inspection("grade_b") == 2250.0
    with pytest.raises(ValidationError, match="at least one day"), env.cr.savepoint():
        env["fix.storefront.return.policy"].with_user(w.operator).create(
            {"name": "zero", "window_days": 0}
        )


# ============================================================ page 8: corporate
@pytest.fixture
def corp(c):
    env = c.env
    company = env["res.partner"].create({"name": "M38C Bank Ltd", "is_company": True})
    buyer = env["res.partner"].create({"name": "M38C Buyer", "parent_id": company.id})
    boss = env["res.partner"].create({"name": "M38C Boss", "parent_id": company.id})
    acct = (
        env["fix.storefront.corporate.account"]
        .with_user(c.w.operator)
        .create(
            {
                "partner_id": company.id,
                "approver_ids": [(6, 0, [boss.id])],
                "approval_threshold": 1000.0,
                "category_ids": [(6, 0, [c.category.id])],
            }
        )
    )
    acct.with_user(c.manager).action_activate()
    return types.SimpleNamespace(company=company, buyer=buyer, boss=boss, acct=acct)


def test_a_corporate_order_needs_its_po_and_the_clients_approval(c, corp):
    env, w = c.env, c.w
    stranger = env["res.partner"].create({"name": "M38C Stranger"})
    with pytest.raises(ValidationError, match="do not work for"), env.cr.savepoint():
        corp.acct.sudo().write({"approver_ids": [(4, stranger.id)]})
    cart = (
        env["fix.storefront.cart"]
        .with_user(w.clerk)
        .create({"customer_id": corp.buyer.id, "corporate_account_id": corp.acct.id})
    )
    assert cart.channel == "corporate"
    env["fix.storefront.cart.line"].with_user(w.clerk).create(
        {"cart_id": cart.id, "product_id": w.product.id}
    )
    with pytest.raises(UserError, match="purchase-order"), env.cr.savepoint():
        cart.action_place_order(shipping_address="Gulshan")
    cart.with_user(w.clerk).write({"po_reference": "PO-7781"})
    with pytest.raises(UserError, match="approval"), env.cr.savepoint():
        cart.action_place_order(shipping_address="Gulshan")
    cart.with_user(w.clerk).write(
        {"client_approver_id": corp.buyer.id, "client_approval_ref": "mail 12"}
    )
    with pytest.raises(UserError, match="own approvers"), env.cr.savepoint():
        cart.with_user(w.clerk).action_record_client_approval()
    cart.with_user(w.clerk).write({"client_approver_id": corp.boss.id})
    cart.with_user(w.clerk).action_record_client_approval()
    with pytest.raises(UserError, match="fixed"), env.cr.savepoint():
        cart.line_ids.with_user(w.clerk).write({"quantity": 5})
    with pytest.raises(UserError, match="cannot be changed"), env.cr.savepoint():
        cart.with_user(w.clerk).write({"po_reference": "PO-other"})
    order = cart.action_place_order(shipping_address="Gulshan")
    assert order.sudo().po_reference == "PO-7781"


def test_a_corporate_order_stays_in_the_agreed_catalogue(c, corp):
    env, w = c.env, c.w
    outside = env["product.template"].create(
        {"name": "M38C Sofa", "list_price": 100.0, "sale_ok": True}
    )
    cart = (
        env["fix.storefront.cart"]
        .with_user(w.clerk)
        .create(
            {
                "customer_id": corp.buyer.id,
                "corporate_account_id": corp.acct.id,
                "po_reference": "PO-1",
            }
        )
    )
    env["fix.storefront.cart.line"].with_user(w.clerk).create(
        {"cart_id": cart.id, "product_id": outside.id}
    )
    with pytest.raises(UserError, match="agreed catalogue"), env.cr.savepoint():
        cart.action_place_order(shipping_address="Gulshan")
    other = (
        env["fix.storefront.cart"]
        .with_user(w.clerk)
        .create(
            {
                "customer_id": w.customer.id,
                "corporate_account_id": corp.acct.id,
                "po_reference": "PO-2",
            }
        )
    )
    env["fix.storefront.cart.line"].with_user(w.clerk).create(
        {"cart_id": other.id, "product_id": w.product.id}
    )
    with pytest.raises(UserError, match="not a buyer"), env.cr.savepoint():
        other.action_place_order(shipping_address="Gulshan")


# ============================================================ page 9: recovery
def test_recovery_contacts_are_a_log_and_count_conversions(c):
    env, w = c.env, c.w
    cart = _cart(w)
    Attempt = env["fix.storefront.recovery.attempt"]
    contact = Attempt.with_user(w.clerk).create(
        {"cart_id": cart.id, "channel": "whatsapp", "outcome": "reminded"}
    )
    assert (contact.contacted_by_id, contact.customer_id) == (w.clerk, w.customer)
    assert not contact.converted
    contact.with_user(w.clerk).write({"outcome": "reminded", "note": "sent link"})  # a re-post
    with pytest.raises(UserError, match="log entry"), env.cr.savepoint():
        contact.with_user(w.clerk).write({"outcome": "will_resume"})
    with pytest.raises(UserError, match="log entry"), env.cr.savepoint():
        contact.with_user(w.clerk).unlink()
    cart.action_place_order(shipping_address="Road 1")
    contact.invalidate_recordset(["converted"])
    assert contact.converted
    with pytest.raises(UserError, match="unordered"), env.cr.savepoint():
        Attempt.with_user(w.clerk).create({"cart_id": cart.id, "outcome": "no_answer"})
    from odoo.addons.cd_p03_portal.controllers.a04 import m38

    pack = m38.abandonment_recovery(env)
    row = next(r for r in pack["rows"] if r["cart"] == cart.name)
    assert (row["contacts"], row["recovered"]) == (1, "✓")


# ============================================================ page 10: service booking
def _branch(env):
    branch = env["fix.branch"].search([], limit=1)
    if branch:
        return branch
    unit = env["operating.unit"].search([], limit=1) or env["operating.unit"].create(
        {"name": "M38C Unit", "code": "M38CU"}
    )
    entity = env["fix.entity"].search([], limit=1) or env["fix.entity"].create(
        {
            "legal_name": "1000FiX Group Ltd",
            "code": "M38CGRP",
            "company_id": env.company.id,
            "operating_unit_id": unit.id,
        }
    )
    return env["fix.branch"].create(
        {
            "name": "M38C Hub",
            "code": "M38C-HUB",
            "entity_id": entity.id,
            "operating_unit_id": unit.id,
        }
    )


@pytest.fixture
def svc(c):
    env, w = c.env, c.w
    branch = _branch(env)
    device = _device(env, w, "M38C-SVC-1")
    slot = (
        env["fix.storefront.slot"]
        .with_user(w.operator)
        .create(
            {
                "name": "M38C repair 10-13",
                "slot_type": "service",
                "slot_date": fields.Date.context_today(env.user) + timedelta(days=1),
                "capacity": 1,
                "branch_id": branch.id,
            }
        )
    )
    return types.SimpleNamespace(branch=branch, device=device, slot=slot)


def _booking(c, svc, **vals):
    return (
        c.env["fix.storefront.service.booking"]
        .with_user(c.w.clerk)
        .create(
            {
                "customer_id": c.w.customer.id,
                "device_id": svc.device.id,
                "branch_id": svc.branch.id,
                "slot_id": svc.slot.id,
                "fault_description": "Screen flickers",
                **vals,
            }
        )
    )


def test_a_service_booking_becomes_the_m01_service_order(c, svc):
    env, w = c.env, c.w
    booking = _booking(c, svc)
    assert booking.name.startswith("SFB/")
    assert (svc.slot.booked, svc.slot.state) == (1, "full")
    with pytest.raises(UserError, match="full"), env.cr.savepoint():
        _booking(c, svc)
    with pytest.raises(UserError, match="role"), env.cr.savepoint():
        booking.with_user(w.clerk).action_confirm()
    booking.with_user(w.operator).action_confirm()
    order = booking.service_order_id.sudo()
    assert order and (order.customer_id, order.device_id, order.branch_id) == (
        w.customer,
        svc.device,
        svc.branch,
    )
    assert order.service_type == "hotline" and order.fault_description == "Screen flickers"
    with pytest.raises(UserError, match="confirmed"), env.cr.savepoint():
        booking.with_user(w.operator).action_confirm()
    with pytest.raises(UserError, match="M01 service order"), env.cr.savepoint():
        booking.with_user(w.operator).action_cancel(reason="x")
    with pytest.raises(UserError, match="workflow"), env.cr.savepoint():
        booking.with_user(w.operator).write({"state": "requested"})


def test_a_booking_is_for_the_customers_own_device_in_a_service_slot(c, svc):
    env, w = c.env, c.w
    with pytest.raises(ValidationError, match="not registered"), env.cr.savepoint():
        _booking(c, svc, customer_id=w.other.id)
    delivery = (
        env["fix.storefront.slot"]
        .with_user(w.operator)
        .create(
            {
                "name": "M38C delivery",
                "slot_date": fields.Date.context_today(env.user),
                "capacity": 5,
            }
        )
    )
    with pytest.raises(ValidationError, match="not a service"), env.cr.savepoint():
        _booking(c, svc, slot_id=delivery.id)
    booking = _booking(c, svc)
    with pytest.raises(UserError, match="reason"), env.cr.savepoint():
        booking.with_user(w.clerk).action_cancel()
    booking.with_user(w.clerk).action_cancel(reason="customer travelled")
    assert booking.state == "cancelled" and svc.slot.booked == 0
