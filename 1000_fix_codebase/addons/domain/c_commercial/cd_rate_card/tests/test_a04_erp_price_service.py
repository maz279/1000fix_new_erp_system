# A04 ERP audit (20 Nov 2026), stream B1: the M11 price service and the
# controls built on it (M11-F1..F20), on the live ORM (`odoo_env`, rolled
# back), as non-superusers where access or the gate matters.
#
# fix_real today: 0 rate cards, list_price 1.00 on every stocked item, M15
# cost on 8,008 parts. Each test reproduces what the audit probed there.
import itertools
import uuid
from datetime import timedelta

import pytest
from odoo import Command, fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
TAG = "B1PS-%s" % uuid.uuid4().hex[:6].upper()
_SEQ = itertools.count(1)
OFFICER = "cd_rate_card.group_pricing_officer"
RELEASER = "cd_rate_card.group_price_releaser"


def _user(env, tag, groups=()):
    n = next(_SEQ)
    vals = {
        "name": "%s %s %d" % (TAG, tag, n),
        "login": "%s.%s.%d@b1.test" % (TAG.lower(), tag, n),
        "group_ids": [(6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])],
    }
    if "operating_unit_ids" in env["res.users"]._fields:
        ou = env["operating.unit"].search([], limit=1)
        vals["operating_unit_ids"] = [(6, 0, ou.ids)]
        if "default_operating_unit_id" in env["res.users"]._fields:
            vals["default_operating_unit_id"] = ou.id
    return env["res.users"].with_context(no_reset_password=True).create(vals)


@pytest.fixture
def ppl(odoo_env):
    class P:
        clerk = _user(odoo_env, "clerk")
        officer = _user(odoo_env, "officer", [OFFICER])
        releaser = _user(odoo_env, "rel", [RELEASER])
        t2 = _user(odoo_env, "t2", ["cd_entity_config.group_dofa_tier_2"])
        t4 = _user(odoo_env, "t4", ["cd_entity_config.group_dofa_tier_4"])

    odoo_env["ir.config_parameter"].sudo().set_param("cd_rate_card.margin_floor_pct", "0")
    return P


def _today(env):
    return fields.Date.context_today(env["res.users"])


def _product(env, list_price=1.0, cost=None):
    """A real-shaped item: list_price the 1.00 placeholder, M15 cost if given."""
    code = "%s-%d" % (TAG, next(_SEQ))
    product = env["product.product"].create(
        {"name": "Item %s" % code, "default_code": code, "list_price": list_price}
    )
    if cost is not None:
        env["fix.spare.part"].sudo().create(
            {
                "name": "Part %s" % code,
                "part_number": code,
                "unit_cost": cost,
                "product_id": product.id,
            }
        )
    return product


def _card(env, user, product, price, **kw):
    vals = {"product_code": product.default_code, "unit_price": price, "line_type": "part"}
    vals.update(kw)
    card = env["fix.rate.card"].with_user(user).create(vals)
    card._guarded().write({"state": "released"})
    return env["fix.rate.card"].browse(card.ids)


def _price(env, product, **kw):
    return env["fix.rate.card"].price_for(product, **kw)


# ---- F1: no released price is no price ------------------------------------


def test_no_released_card_means_no_price_never_the_list_placeholder(odoo_env, ppl):
    product = _product(odoo_env, list_price=1.0)
    res = _price(odoo_env, product, channel="quotation")
    assert res["price"] is None and res["source"] == "none" and res["card_id"] is False
    assert "no released M11 price" in res["reason"]


def test_cost_margin_floor_refuses_the_placeholder_price(odoo_env, ppl):
    """p1/p2: 1.00 and 0.01 passed on an item that costs 548."""
    product = _product(odoo_env, cost=548.0)
    Card = odoo_env["fix.rate.card"].with_user(ppl.clerk)
    for price in (1.0, 0.01):
        with pytest.raises(UserError, match="floor is BDT 548.00"):
            Card.check_sale_price(product, price, "quotation")
    assert Card.check_sale_price(product, 548.0, "quotation")["floor"] == 548.0
    odoo_env["ir.config_parameter"].sudo().set_param("cd_rate_card.margin_floor_pct", "10")
    with pytest.raises(UserError, match="floor is BDT 602.80"):
        Card.check_sale_price(product, 600.0, "quotation")


def test_customer_channel_refuses_an_item_with_no_released_price(odoo_env, ppl):
    product = _product(odoo_env)
    with pytest.raises(UserError, match="customer channel sells only at a released price"):
        odoo_env["fix.rate.card"].with_user(ppl.clerk).check_sale_price(
            product, 100.0, "storefront"
        )
    _card(odoo_env, ppl.officer, product, 100.0)
    assert (
        odoo_env["fix.rate.card"]
        .with_user(ppl.clerk)
        .check_sale_price(product, 100.0, "storefront")
    )


# ---- F2/F3/F13/F14: precedence, context, company, currency -----------------


def test_precedence_customer_then_tier_then_standard(odoo_env, ppl):
    product = _product(odoo_env)
    _card(odoo_env, ppl.officer, product, 1000.0)
    _card(odoo_env, ppl.officer, product, 900.0, min_tier=2)
    walk_in = odoo_env["res.partner"].create({"name": "%s walk-in" % TAG})
    gold = odoo_env["res.partner"].create({"name": "%s gold" % TAG})
    gold.with_user(ppl.officer).write({"fix_price_tier": 3})
    key = odoo_env["res.partner"].create({"name": "%s key account" % TAG, "is_company": True})
    _card(odoo_env, ppl.officer, product, 850.0, partner_id=key.id)
    assert (_price(odoo_env, product, partner=walk_in)["price"], "card") == (1000.0, "card")
    res = _price(odoo_env, product, partner=gold)
    assert (res["price"], res["source"]) == (900.0, "tier")
    res = _price(odoo_env, product, partner=key)
    assert (res["price"], res["source"]) == (850.0, "customer")


def test_contract_lane_wins(odoo_env, ppl):
    from odoo.addons.cd_rate_card.tests import contract_helpers

    product = _product(odoo_env)
    _card(odoo_env, ppl.officer, product, 1000.0)
    contract = contract_helpers.contract(odoo_env)
    _card(odoo_env, ppl.officer, product, 800.0, min_tier=99, contract_id=contract.id)
    res = _price(odoo_env, product, contract=contract)
    assert (res["price"], res["source"]) == (800.0, "contract")


def test_customer_tier_is_set_only_by_a_pricing_officer(odoo_env, ppl):
    partner = odoo_env["res.partner"].create({"name": "%s c" % TAG})
    with pytest.raises(AccessError), odoo_env.cr.savepoint():
        partner.with_user(ppl.clerk).write({"fix_price_tier": 5})


def test_another_company_card_never_prices_this_company(odoo_env, ppl):
    """p1: a company-2 card priced a company-1 lookup."""
    other = odoo_env["res.company"].create({"name": "%s Co2" % TAG})
    product = _product(odoo_env)
    # recorded by that company's officer (here the superuser: the fence is the point)
    card = odoo_env["fix.rate.card"].create(
        {"product_code": product.default_code, "unit_price": 700.0, "company_id": other.id}
    )
    card._guarded().write({"state": "released"})
    assert _price(odoo_env, product, company=odoo_env.company)["price"] is None
    assert _price(odoo_env, product, company=other)["price"] == 700.0


def test_card_in_another_currency_does_not_price_bdt(odoo_env, ppl):
    usd = odoo_env.ref("base.USD")
    usd.sudo().active = True
    product = _product(odoo_env)
    _card(odoo_env, ppl.officer, product, 10.0, currency_id=usd.id)
    assert _price(odoo_env, product)["price"] is None
    assert _price(odoo_env, product, currency=usd)["price"] == 10.0


# ---- F4/F5: effective dating, versions ------------------------------------


def test_next_years_card_is_a_new_version_and_dates_resolve(odoo_env, ppl):
    """p1: the (code, tier, contract) key refused next year's card."""
    today = _today(odoo_env)
    product = _product(odoo_env)
    _card(odoo_env, ppl.officer, product, 1000.0, valid_to=today + timedelta(days=9))
    _card(odoo_env, ppl.officer, product, 1100.0, valid_from=today + timedelta(days=10))
    assert _price(odoo_env, product, date=today)["price"] == 1000.0
    assert _price(odoo_env, product, date=today + timedelta(days=10))["price"] == 1100.0


def test_overlapping_released_cards_are_refused(odoo_env, ppl):
    product = _product(odoo_env)
    _card(odoo_env, ppl.officer, product, 1000.0)
    with pytest.raises(UserError, match="overlaps"), odoo_env.cr.savepoint():
        _card(odoo_env, ppl.officer, product, 1050.0, valid_from=_today(odoo_env))


def test_a_price_change_is_a_dated_new_version_not_an_overwrite(odoo_env, ppl):
    today = _today(odoo_env)
    product = _product(odoo_env)
    card = _card(odoo_env, ppl.officer, product, 1000.0, valid_from=today - timedelta(days=30))
    change = (
        odoo_env["fix.price.change"]
        .with_user(ppl.officer)
        .create(
            {
                "target_type": "rate_card",
                "change_type": "change",
                "rate_card_id": card.id,
                "proposed_value": 1200.0,
                "reason": "supplier price rise",
                "effective_from": today + timedelta(days=5),
            }
        )
    )
    change.with_user(ppl.officer).action_submit()
    approve_via_inbox(change, ppl.releaser, requester=ppl.officer)
    assert change.state == "applied" and change.new_rate_card_id
    assert card.unit_price == 1000.0 and card.valid_to == today + timedelta(days=4)
    assert _price(odoo_env, product, date=today)["price"] == 1000.0
    assert _price(odoo_env, product, date=today + timedelta(days=5))["price"] == 1200.0


def test_an_older_version_never_displaces_a_newer_one(odoo_env, ppl):
    """p2: approving an older-dated version superseded the newer one."""
    today = _today(odoo_env)
    Book, Version = odoo_env["fix.price.book"], odoo_env["fix.price.version"]
    book = Book.with_user(ppl.officer).create({"name": TAG, "code": TAG})
    newer = Version.with_user(ppl.officer).create(
        {"name": "new", "book_id": book.id, "version": "2", "effective_from": today}
    )
    newer.with_user(ppl.officer).action_submit()
    approve_via_inbox(newer, ppl.releaser, requester=ppl.officer)
    older = Version.with_user(ppl.officer).create(
        {
            "name": "old",
            "book_id": book.id,
            "version": "1",
            "effective_from": today - timedelta(days=10),
        }
    )
    older.with_user(ppl.officer).action_submit()
    approve_via_inbox(older, ppl.releaser, requester=ppl.officer)
    assert newer.state == "active"
    assert older.state == "superseded" and older.superseded_by_id == newer


def test_a_card_of_a_version_prices_only_while_the_version_is_in_force(odoo_env, ppl):
    today = _today(odoo_env)
    book = odoo_env["fix.price.book"].with_user(ppl.officer).create({"name": TAG, "code": TAG})
    version = (
        odoo_env["fix.price.version"]
        .with_user(ppl.officer)
        .create({"name": "v", "book_id": book.id, "version": "1", "effective_from": today})
    )
    product = _product(odoo_env)
    _card(odoo_env, ppl.officer, product, 500.0, version_id=version.id)
    assert _price(odoo_env, product)["price"] is None  # draft version prices nothing
    version.with_user(ppl.officer).action_submit()
    approve_via_inbox(version, ppl.releaser, requester=ppl.officer)
    assert _price(odoo_env, product)["price"] == 500.0


# ---- F8/F9/F20: floors on cards, releases --------------------------------


def _floor(env, user, product, price):
    return (
        env["fix.price.floor"]
        .with_user(user)
        .create(
            {"name": "%s floor" % TAG, "product_code": product.default_code, "floor_price": price}
        )
    )


def test_a_card_is_never_created_below_its_floor(odoo_env, ppl):
    """p1: a card was created at 400 under a 950 floor."""
    product = _product(odoo_env)
    _floor(odoo_env, ppl.officer, product, 950.0)
    with pytest.raises(UserError, match="below the floor"), odoo_env.cr.savepoint():
        odoo_env["fix.rate.card"].with_user(ppl.officer).create(
            {"product_code": product.default_code, "unit_price": 400.0}
        )


def test_a_rate_change_below_the_floor_is_refused_at_submission(odoo_env, ppl):
    """p1: 1000 -> 500 under a 950 floor was accepted."""
    product = _product(odoo_env)
    card = _card(odoo_env, ppl.officer, product, 1000.0)
    _floor(odoo_env, ppl.officer, product, 950.0)
    change = (
        odoo_env["fix.price.change"]
        .with_user(ppl.officer)
        .create(
            {
                "target_type": "rate_card",
                "change_type": "change",
                "rate_card_id": card.id,
                "proposed_value": 500.0,
                "reason": "clearance",
            }
        )
    )
    with pytest.raises(UserError, match="below the floor"), odoo_env.cr.savepoint():
        change.with_user(ppl.officer).action_submit()


def test_a_card_is_never_released_below_m15_cost(odoo_env, ppl):
    product = _product(odoo_env, cost=600.0)
    with pytest.raises(UserError, match="M15 cost"), odoo_env.cr.savepoint():
        odoo_env["fix.rate.card"].with_user(ppl.officer).create(
            {"product_code": product.default_code, "unit_price": 500.0}
        )


def test_a_card_is_released_only_for_a_real_code(odoo_env, ppl):
    """q4: a card was released for a code that does not exist."""
    card = (
        odoo_env["fix.rate.card"]
        .with_user(ppl.officer)
        .create({"product_code": "%s-NOSUCH" % TAG, "unit_price": 100.0})
    )
    with pytest.raises(UserError, match="No item or charge code"), odoo_env.cr.savepoint():
        card.with_user(ppl.officer).action_request_release()


def test_the_dynamic_rule_uses_the_item_floor_and_cost(odoo_env, ppl):
    """F9: _floor_for matched floors by code only and ignored cost."""
    product = _product(odoo_env, cost=800.0)
    rule = (
        odoo_env["fix.dynamic.price.rule"]
        .with_user(ppl.officer)
        .create({"name": TAG, "rule_type": "off_peak", "adjustment_pct": -30.0})
    )
    assert rule._floor_for(product.default_code) == 800.0


def test_dynamic_rule_type_constrains_the_sign(odoo_env, ppl):
    with pytest.raises(ValidationError, match="never raises"), odoo_env.cr.savepoint():
        odoo_env["fix.dynamic.price.rule"].with_user(ppl.officer).create(
            {"name": TAG, "rule_type": "off_peak", "adjustment_pct": 20.0}
        )
    with pytest.raises(ValidationError, match="never lowers"), odoo_env.cr.savepoint():
        odoo_env["fix.dynamic.price.rule"].with_user(ppl.officer).create(
            {"name": TAG, "rule_type": "demand_surge", "adjustment_pct": -20.0}
        )


# ---- F10: promotions, parts schemes, brand rates chained in ------------------


def _promotion(env, ppl, value, **kw):
    today = _today(env)
    promo = (
        env["fix.promotion"]
        .with_user(ppl.officer)
        .create(
            dict(
                {
                    "name": TAG,
                    "code": "%s-P%d" % (TAG, next(_SEQ)),
                    "value": value,
                    "valid_from": today,
                    "valid_until": today + timedelta(days=5),
                },
                **kw,
            )
        )
    )
    promo._guarded().write({"state": "active"})
    return promo


def test_an_active_promotion_reaches_the_price(odoo_env, ppl):
    """p1: a 20% promotion left the M36 price unchanged."""
    product = _product(odoo_env)
    _card(odoo_env, ppl.officer, product, 1000.0)
    _promotion(odoo_env, ppl, 20.0)
    res = _price(odoo_env, product, channel="quotation")
    assert (res["price"], res["list_price"], res["promotion_discount"]) == (800.0, 1000.0, 200.0)


def test_a_promotion_stops_at_the_floor(odoo_env, ppl):
    product = _product(odoo_env, cost=900.0)
    _card(odoo_env, ppl.officer, product, 1000.0)
    _promotion(odoo_env, ppl, 50.0)
    res = _price(odoo_env, product)
    assert res["price"] == 900.0 and res.get("floor_clamped")


def test_a_released_parts_scheme_prices_a_part_with_no_card(odoo_env, ppl):
    product = _product(odoo_env, cost=1000.0)
    item = odoo_env["fix.catalogue.item"].create(
        {"product_tmpl_id": product.product_tmpl_id.id, "item_type": "part"}
    )
    assert item
    scheme = (
        odoo_env["fix.parts.price.scheme"]
        .with_user(ppl.officer)
        .create(
            {
                "name": TAG,
                "method": "markup",
                "markup_pct": 25.0,
                "valid_from": _today(odoo_env),
            }
        )
    )
    assert _price(odoo_env, product)["price"] is None  # draft scheme prices nothing
    scheme._guarded().write({"state": "active"})
    res = _price(odoo_env, product)
    assert (res["price"], res["source"]) == (1250.0, "parts_scheme")


def test_m09_reads_the_brand_rate_through_the_service(odoo_env, ppl):
    brand = odoo_env["fix.brand"].create({"name": "%s brand" % TAG, "code": TAG[-6:]})
    Card = odoo_env["fix.rate.card"]
    assert Card.reimbursement_for(brand, "l1", 100.0)["amount"] is None
    rate = (
        odoo_env["fix.brand.reimbursement.rate"]
        .with_user(ppl.officer)
        .create(
            {
                "brand_id": brand.id,
                "repair_level": "l1",
                "labour_rate": 500.0,
                "parts_markup_pct": 10.0,
                "valid_from": _today(odoo_env),
            }
        )
    )
    rate._guarded().write({"state": "active"})
    res = Card.reimbursement_for(brand, "l1", 100.0)
    assert res["amount"] == 610.0 and res["rate_id"] == rate.id


# ---- F7: the override is bound to one line, single use, dated ------------------


@pytest.fixture
def est(odoo_env, ppl):
    env = odoo_env
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].search([("company_id", "=", env.company.id)], limit=1)
    if not entity:  # the clean template has none; reuse it when it exists
        entity = env["fix.entity"].create(
            {"code": "B1E", "legal_name": "%s Entity" % TAG, "company_id": env.company.id}
        )
    branch = env["fix.branch"].create(
        {"name": TAG, "code": TAG[-6:], "entity_id": entity.id, "operating_unit_id": ou.id}
    )
    brand = env["fix.brand"].create({"name": "%s b" % TAG, "code": "B%s" % TAG[-5:]})
    model = env["fix.device.model"].create({"name": "%s m" % TAG, "brand_id": brand.id})
    customer = env["res.partner"].create({"name": "%s cust" % TAG, "phone": "01711000111"})
    device = env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": customer.id, "serial_number": "SN-" + TAG}
    )
    order = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "fault_description": "No display",
        }
    )

    def make(product, price=None, user=None, reason=None):
        vals = {
            "line_type": "part",
            "product_id": product.id,
            "description": product.name,
            "quantity": 1.0,
        }
        if price is not None:
            vals["unit_price"] = price
        if reason:
            vals["price_override_reason"] = reason
        estimate = (
            env["fix.estimate"]
            .with_user(user or ppl.clerk)
            .create({"order_id": order.id, "line_ids": [Command.create(vals)]})
        )
        return env["fix.estimate"].browse(estimate.ids)

    return make


def _override(env, ppl, line, price, days=3):
    return (
        env["fix.price.override"]
        .with_user(ppl.clerk)
        .create(
            {
                "estimate_line_id": line.id,
                "product_id": line.product_id.id,
                "requested_price": price,
                "valid_until": _today(env) + timedelta(days=days),
                "dofa_justification": "price match",
            }
        )
    )


def test_estimate_takes_the_released_price_when_none_is_typed(odoo_env, ppl, est):
    product = _product(odoo_env, cost=400.0)
    _card(odoo_env, ppl.officer, product, 1000.0)
    line = est(product).line_ids
    assert (line.unit_price, line.card_price, line.price_source) == (1000.0, 1000.0, "rate_card")
    assert line.line_total == line.quantity * line.unit_price  # A02: qty x unit price


def test_estimate_with_no_card_keeps_working_above_cost(odoo_env, ppl, est):
    """fix_real has 0 cards: a typed price stands, checked against M15 cost."""
    product = _product(odoo_env, cost=400.0)
    line = est(product, 450.0).line_ids
    assert (line.unit_price, line.price_source) == (450.0, "entered")
    with pytest.raises(UserError, match="floor is BDT 400.00"), odoo_env.cr.savepoint():
        est(product, 1.0)


def test_a_different_typed_price_needs_a_reason_and_is_recorded(odoo_env, ppl, est):
    product = _product(odoo_env, cost=400.0)
    _card(odoo_env, ppl.officer, product, 1000.0)
    with pytest.raises(UserError, match="state why"), odoo_env.cr.savepoint():
        est(product, 900.0)
    line = est(product, 900.0, reason="loyal customer").line_ids
    assert (line.card_price, line.unit_price, line.price_source) == (1000.0, 900.0, "changed")


def test_a_typed_line_discount_reaches_the_dofa_ladder(odoo_env, ppl, est):
    """F6: estimate DOFA read only the header discount; 25% typed off the
    released price was Tier 0."""
    product = _product(odoo_env, cost=100.0)
    _card(odoo_env, ppl.officer, product, 1000.0)
    estimate = est(product, 750.0, reason="competitor match")
    assert estimate.discount_pct == 0.0
    assert estimate._dofa_amount() == 25.0
    assert estimate._dofa_current_tier() == "tier_3"


def test_override_is_bound_to_its_line_used_once_and_lapses(odoo_env, ppl, est):
    """p3: one floor approval let 600 (storefront), 650 (another user) and 600
    (quotation) through, forever."""
    product = _product(odoo_env, cost=1000.0)
    line = est(product, 1000.0).line_ids
    other = est(product, 1000.0).line_ids
    override = _override(odoo_env, ppl, line, 900.0)  # 10% below: Tier 2
    assert override.floor_price == 1000.0 and override.dofa_tier_required == "tier_2"
    with pytest.raises(UserError, match="floor is BDT 1000.00"), odoo_env.cr.savepoint():
        line.with_user(ppl.clerk).write({"unit_price": 900.0})  # not approved yet
    approve_via_inbox(override, ppl.t2, requester=ppl.clerk)
    assert override.state == "approved"
    # another line, the same item and price: not covered
    with pytest.raises(UserError, match="floor is BDT 1000.00"), odoo_env.cr.savepoint():
        other.with_user(ppl.clerk).write({"unit_price": 900.0})
    # deeper than approved: not covered
    with pytest.raises(UserError, match="below the BDT 900.00"), odoo_env.cr.savepoint():
        line.with_user(ppl.clerk).write({"unit_price": 800.0})
    line.with_user(ppl.clerk).write({"unit_price": 900.0})
    assert override.state == "consumed" and override.consumed_by == ppl.clerk
    # the line keeps its price on a re-check; the quotation never sees it
    assert (
        odoo_env["fix.rate.card"]
        .with_user(ppl.clerk)
        .check_sale_price(product, 900.0, "estimate", line=line)
    )
    with pytest.raises(UserError, match="floor is BDT 1000.00"):
        odoo_env["fix.rate.card"].with_user(ppl.clerk).check_sale_price(product, 900.0, "quotation")


def test_an_unused_override_lapses_at_its_use_by_date(odoo_env, ppl, est):
    product = _product(odoo_env, cost=1000.0)
    line = est(product, 1000.0).line_ids
    override = _override(odoo_env, ppl, line, 950.0)
    approve_via_inbox(override, ppl.t2, requester=ppl.clerk)
    override._guarded().write({"valid_until": _today(odoo_env) - timedelta(days=1)})
    assert odoo_env["fix.price.override"].cron_expire_overrides() == 1
    with pytest.raises(UserError, match="floor is BDT 1000.00"), odoo_env.cr.savepoint():
        line.with_user(ppl.clerk).write({"unit_price": 950.0})


def test_the_requester_never_approves_the_override(odoo_env, ppl, est):
    product = _product(odoo_env, cost=1000.0)
    line = est(product, 1000.0, user=ppl.t2).line_ids
    override = (
        odoo_env["fix.price.override"]
        .with_user(ppl.t2)
        .create(
            {
                "estimate_line_id": line.id,
                "product_id": product.id,
                "requested_price": 900.0,
                "valid_until": _today(odoo_env) + timedelta(days=2),
                "dofa_justification": "x",
            }
        )
    )
    override.with_user(ppl.t2).action_submit()
    assert ppl.t2 not in override.approval_request_id.task_ids.mapped("assigned_user_id")


def test_an_override_is_not_needed_above_the_floor(odoo_env, ppl, est):
    product = _product(odoo_env, cost=100.0)
    line = est(product, 200.0).line_ids
    with pytest.raises(UserError, match="no override is needed"), odoo_env.cr.savepoint():
        _override(odoo_env, ppl, line, 150.0)


# ---- F11: list_price is guarded ---------------------------------------------


def test_list_price_changes_only_by_a_pricing_officer_with_a_trail(odoo_env, ppl):
    product = _product(odoo_env)
    tmpl = product.product_tmpl_id
    clerk_mgr = _user(odoo_env, "prodmgr", ["product.group_product_manager"])
    with pytest.raises(UserError, match="Pricing Officer"), odoo_env.cr.savepoint():
        tmpl.with_user(clerk_mgr).write({"list_price": 5000.0})
    with pytest.raises(UserError, match="Pricing Officer"), odoo_env.cr.savepoint():
        tmpl.with_user(clerk_mgr).sudo().write({"list_price": 5000.0})
    tmpl.with_user(ppl.officer).sudo().write({"list_price": 5000.0})
    assert "List price changed from 1.00 to 5000.00" in tmpl.message_ids[:1].body


# ---- F16: one rounding --------------------------------------------------------


def test_one_half_up_rounding_everywhere(odoo_env, ppl):
    from odoo.addons.cd_rate_card.models.pricing_money import money

    assert money(1.545) == 1.55 and money(2.675) == 2.68
    rule = (
        odoo_env["fix.dynamic.price.rule"]
        .with_user(ppl.officer)
        .create({"name": TAG, "rule_type": "demand_surge", "adjustment_pct": 0.5})
    )
    # 307.7 x 1.005 = 309.2385 -> 309.24 (HALF_EVEN gave the same; 1.545 case:)
    assert rule.apply_to(1.5373134328) == money(1.5373134328 * 1.005)


# ---- deployment wiring ----------------------------------------------------------


class TestDeployment:
    def test_wiring(self, odoo_env):
        env = odoo_env
        cron = env.ref("cd_rate_card.ir_cron_m11_expire_overrides")
        assert cron.active and "cron_expire_overrides" in cron.code
        assert env.ref("cd_rate_card.rule_fix_rate_card_company")
        assert env.ref("cd_rate_card.rule_fix_price_override_company")
        assert env.ref("cd_rate_card.rule_fix_price_floor_company")
        assert env.ref("cd_rate_card.rule_fix_price_version_company")
        acl = env["ir.model.access"].search([("model_id.model", "=", "fix.price.override")])
        assert acl.filtered(lambda a: a.group_id == env.ref("base.group_user") and a.perm_create)
        from odoo.addons.cd_p03_portal.controllers.a04 import m11 as surface
        from odoo.addons.cd_p03_portal.controllers.a04.writable import WRITABLE

        assert "fix.price.override" in surface.SURFACES
        assert {"requested_price", "valid_until", "estimate_line_id"} <= WRITABLE[
            "fix.price.override"
        ]
        assert hasattr(env["fix.rate.card"], "price_for")
        assert hasattr(env["fix.rate.card"], "check_sale_price")


# ---- M36: the quotation prices through the service, never from list 1.00 ----


def test_quotation_line_never_falls_back_to_the_list_placeholder(odoo_env, ppl):
    QLine = odoo_env["fix.quotation.line"].with_user(ppl.clerk)
    product = _product(odoo_env, list_price=1.0)
    with pytest.raises(UserError, match="no released M11 price"):
        QLine._priced_vals({"unit_price": None}, product)
    typed = QLine._priced_vals({"unit_price": 450.0}, product)
    assert (typed["price_source"], typed["list_price"]) == ("manual", 450.0)


def test_quotation_line_takes_the_released_price_and_measures_off_list(odoo_env, ppl):
    QLine = odoo_env["fix.quotation.line"].with_user(ppl.clerk)
    product = _product(odoo_env)
    _card(odoo_env, ppl.officer, product, 1000.0)
    vals = QLine._priced_vals({"unit_price": None}, product)
    assert (vals["unit_price"], vals["price_source"], vals["list_price"]) == (
        1000.0,
        "rate_card",
        1000.0,
    )
    _promotion(odoo_env, ppl, 10.0)
    vals = QLine._priced_vals({"unit_price": None}, product)
    # the promotion is in the price and counts as discount off the released price
    assert (vals["unit_price"], vals["list_price"]) == (900.0, 1000.0)
    typed = QLine._priced_vals({"unit_price": 700.0}, product)
    assert (typed["price_source"], typed["list_price"]) == ("manual", 1000.0)


# ---- M37-F4: M01 intake checks the catalogue lifecycle ----------------------


def test_service_order_refuses_a_discontinued_catalogue_item(odoo_env, ppl, est):
    product = _product(odoo_env)
    item = odoo_env["fix.catalogue.item"].create(
        {"product_tmpl_id": product.product_tmpl_id.id, "item_type": "service"}
    )
    item._guarded().write({"state": "deprecated"})
    order = odoo_env["fix.service.order"].search(
        [("fault_description", "=", "No display")], order="id desc", limit=1
    )
    with pytest.raises(UserError, match="no longer sold"), odoo_env.cr.savepoint():
        order.write({"catalog_item_id": item.id})
    item._guarded().write({"state": "approved"})
    order.write({"catalog_item_id": item.id})
    assert order.catalog_item_id == item


def test_a_mass_change_creates_dated_versions_and_rolls_back(odoo_env, ppl):
    """F4 (fix_m11_capture _apply): a mass change overwrote unit_price in place."""
    today = _today(odoo_env)
    product = _product(odoo_env)
    card = _card(odoo_env, ppl.officer, product, 1000.0, valid_from=today - timedelta(days=30))
    mass = (
        odoo_env["fix.price.mass.change"]
        .with_user(ppl.officer)
        .create(
            {
                "product_code_prefix": product.default_code,
                "change_kind": "percent",
                "value": 10.0,
                "effective_date": today + timedelta(days=3),
                "reason": "inflation",
            }
        )
    )
    mass.with_user(ppl.officer).action_submit()
    approve_via_inbox(mass, ppl.releaser, requester=ppl.officer)
    assert mass.state == "approved"
    mass._apply()
    line = mass.line_ids
    assert line.new_rate_card_id and card.unit_price == 1000.0
    assert _price(odoo_env, product, date=today)["price"] == 1000.0
    assert _price(odoo_env, product, date=today + timedelta(days=3))["price"] == 1100.0
    mass.with_user(ppl.releaser).action_rollback(reason="wrong index")
    assert not line.new_rate_card_id.active and not card.valid_to
    assert _price(odoo_env, product, date=today + timedelta(days=3))["price"] == 1000.0
