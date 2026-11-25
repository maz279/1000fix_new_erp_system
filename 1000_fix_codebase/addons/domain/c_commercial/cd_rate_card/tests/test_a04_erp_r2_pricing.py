# A04 ERP audit round 2 (21 Nov 2026), stream R2-3: the deferred M11 / M37
# items (M11-F19, M11-F15, M37-F5/F7/F11) on the live ORM (`odoo_env`, rolled
# back), as non-superusers where a role or the guard decides.
import itertools
import uuid
from datetime import timedelta

import pytest
from odoo import Command, fields
from odoo.addons.cd_rate_card.controllers.indicative import allow
from odoo.addons.cd_rate_card.tests import contract_helpers
from odoo.addons.cd_service_order.models.fix_service_order import _dhaka_date
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
TAG = "R23-%s" % uuid.uuid4().hex[:6].upper()
_SEQ = itertools.count(1)
OFFICER = "cd_rate_card.group_pricing_officer"
RELEASER = "cd_rate_card.group_price_releaser"
SPREAD = "cd_rate_card.max_channel_spread_pct"


def _user(env, tag, groups=()):
    n = next(_SEQ)
    vals = {
        "name": "%s %s %d" % (TAG, tag, n),
        "login": "%s.%s.%d@r23.test" % (TAG.lower(), tag, n),
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
        releaser2 = _user(odoo_env, "rel2", [RELEASER])

    params = odoo_env["ir.config_parameter"].sudo()
    params.set_param("cd_rate_card.margin_floor_pct", "0")
    params.set_param(SPREAD, "")
    params.set_param("cd_rate_card.margin_target_pct", "")
    return P


def _today(env):
    return fields.Date.context_today(env["res.users"])


def _item(env, item_type="labour", state="approved", **vals):
    code = "%s-%d" % (TAG, next(_SEQ))
    tmpl = env["product.template"].create({"name": "Item %s" % code, "default_code": code})
    item = env["fix.catalogue.item"].create(
        dict({"product_tmpl_id": tmpl.id, "item_type": item_type}, **vals)
    )
    item._guarded().write({"state": state})
    return item


def _released(env, card):
    card._guarded().write({"state": "released"})
    return env["fix.rate.card"].browse(card.ids)


def _card(env, user, code, price, **kw):
    vals = {"product_code": code, "unit_price": price, "line_type": "part"}
    vals.update(kw)
    return _released(env, env["fix.rate.card"].with_user(user).create(vals))


def _labour(env, user, rate, level="l2", **kw):
    vals = {"rate_kind": "labour_hour", "unit_price": rate, "repair_level": level}
    vals.update(kw)
    return _released(env, env["fix.rate.card"].with_user(user).create(vals))


def _code(item):
    return item.product_tmpl_id.default_code


# ---- FR-PRC-012: labour rate x standard repair time ---------------------------


def test_a_labour_line_is_priced_at_the_labour_rate_times_its_srt(odoo_env, ppl):
    item = _item(odoo_env, repair_level="l2", standard_labour_time=1.5)
    Card = odoo_env["fix.rate.card"].with_user(ppl.clerk)
    assert Card.price_for(item, channel="service")["price"] is None
    rate = _labour(odoo_env, ppl.officer, 600.0)
    res = Card.price_for(item, channel="service")
    assert (res["price"], res["source"], res["card_id"]) == (900.0, "labour_rate", rate.id)
    assert (res["srt_minutes"], res["labour_rate"]) == (90.0, 600.0)
    # a fixed price for the service itself (FR-PRC-014) wins over the labour rate
    _card(odoo_env, ppl.officer, _code(item), 750.0, line_type="labour")
    res = Card.price_for(item, channel="service")
    assert (res["price"], res["source"]) == (750.0, "card")


def test_the_most_specific_labour_rate_wins_and_never_prices_as_an_item(odoo_env, ppl):
    brand = odoo_env["fix.brand"].create({"name": "%s brand" % TAG, "code": "R%s" % TAG[-5:]})
    other = odoo_env["fix.brand"].create({"name": "%s other" % TAG, "code": "Q%s" % TAG[-5:]})
    branded = _item(odoo_env, repair_level="l2", standard_labour_time=1.0, brand_id=brand.id)
    plain = _item(odoo_env, repair_level="l2", standard_labour_time=1.0, brand_id=other.id)
    generic = _labour(odoo_env, ppl.officer, 600.0)
    specific = _labour(odoo_env, ppl.officer, 800.0, brand_id=brand.id)
    Card = odoo_env["fix.rate.card"]
    assert Card.price_for(branded)["card_id"] == specific.id
    assert Card.price_for(branded)["price"] == 800.0
    assert Card.price_for(plain)["card_id"] == generic.id
    # an L3 operation finds no L2 rate
    assert (
        Card.price_for(_item(odoo_env, repair_level="l3", standard_labour_time=1.0))["price"]
        is None
    )
    # the labour rate is no unit price of an item named by its code
    assert not Card._resolve(generic.product_code)
    assert generic.product_code.startswith("LAB-L2")


def test_a_labour_rate_names_its_level_and_no_item(odoo_env, ppl):
    Card = odoo_env["fix.rate.card"].with_user(ppl.officer)
    with pytest.raises(REFUSED, match="repair level"), odoo_env.cr.savepoint():
        Card.create({"rate_kind": "labour_hour", "unit_price": 500.0})
    item = _item(odoo_env)
    with pytest.raises(REFUSED, match="names no single catalogue item"), odoo_env.cr.savepoint():
        Card.create(
            {
                "rate_kind": "labour_hour",
                "unit_price": 500.0,
                "repair_level": "l1",
                "catalogue_item_id": item.id,
            }
        )


# ---- AUT-PRC-09: a re-baselined SRT moves no labour price until accepted ------------


def _event(env, event_type, record):
    row = (
        env["fix.event.outbox"]
        .sudo()
        .search(
            [("event_type", "=", event_type), ("aggregate_id", "=", record.id)],
            order="id desc",
            limit=1,
        )
    )
    assert row, "no %s event for %s" % (event_type, record)
    return row._relay_event_dict()


def _rebaseline(env, item, minutes):
    base = env["fix.srt.baseline"].create(
        {
            "item_id": item.id,
            "repair_level": item.repair_level,
            "minutes": minutes,
            "reason": "time study",
        }
    )
    base.action_propose()
    base.action_approve()
    return base


def test_an_srt_rebaseline_holds_the_labour_price_until_a_releaser_accepts(odoo_env, ppl):
    item = _item(odoo_env, repair_level="l2", standard_labour_time=1.0)
    _labour(odoo_env, ppl.officer, 600.0)
    Card = odoo_env["fix.rate.card"]
    assert Card.price_for(item)["price"] == 600.0
    base = _rebaseline(odoo_env, item, 90.0)
    assert base.applied_at and base.price_effect == "held"
    assert item.standard_labour_time == 1.5  # the catalogue moved
    res = Card.price_for(item)
    assert (res["price"], res["srt_held"]) == (600.0, True)  # the price did not
    out = odoo_env["fix.m11.pricing.consumers"].consume_srt_rebaselined(
        _event(odoo_env, "catalogue.srt_rebaselined", base)
    )
    review = odoo_env["fix.price.review"].browse(out["id"])
    assert (review.kind, review.held_minutes, review.new_minutes) == ("srt", 60.0, 90.0)
    assert (review.current_price, review.proposed_price) == (600.0, 900.0)
    # replay is a no-op
    assert not odoo_env["fix.m11.pricing.consumers"].consume_srt_rebaselined(
        _event(odoo_env, "catalogue.srt_rebaselined", base)
    )["created"]
    with pytest.raises(REFUSED):
        review.with_user(ppl.officer).action_accept()
    review.with_user(ppl.releaser).action_accept()
    assert base.price_effect == "released" and review.state == "accepted"
    assert Card.price_for(item)["price"] == 900.0


# ---- FR-PRC-017: volume breaks ---------------------------------------------------


def test_volume_breaks_bracket_and_cumulative(odoo_env, ppl):
    item = _item(odoo_env, item_type="part")
    Card = odoo_env["fix.rate.card"].with_user(ppl.officer)
    card = Card.create({"product_code": _code(item), "unit_price": 100.0, "line_type": "part"})
    Break = odoo_env["fix.price.break"].with_user(ppl.officer)
    Break.create({"card_id": card.id, "threshold": 10.0, "unit_price": 90.0})
    Break.create({"card_id": card.id, "threshold": 50.0, "unit_price": 80.0})
    with pytest.raises(REFUSED, match="never raises"), odoo_env.cr.savepoint():
        Break.create({"card_id": card.id, "threshold": 5.0, "unit_price": 120.0})
    card = _released(odoo_env, card)
    price = odoo_env["fix.rate.card"].price_for
    assert price(item, qty=5)["price"] == 100.0
    assert price(item, qty=20)["price"] == 90.0  # bracket: every unit at 90
    assert price(item, qty=60)["price"] == 80.0
    card._guarded().write({"break_treatment": "cumulative"})
    # 10 at 100 + 10 at 90 = 1900 / 20
    assert price(item, qty=20)["price"] == 95.0
    with pytest.raises(REFUSED, match="part of the released price"):
        card.price_break_ids[:1].with_user(ppl.officer).write({"unit_price": 70.0})


# ---- FR-PRC-020 / BRU-PRC-14: channel differential within the max spread -----------


def test_channel_differential_is_released_only_inside_the_governed_spread(odoo_env, ppl):
    item = _item(odoo_env, item_type="part")
    _card(odoo_env, ppl.officer, _code(item), 100.0)
    Diff = odoo_env["fix.channel.differential"].with_user(ppl.officer)
    web = Diff.create(
        {"channel": "storefront", "product_code": _code(item), "adjustment_pct": 5.0, "reason": "x"}
    )
    with pytest.raises(UserError, match="no spread allowed"):
        web.with_user(ppl.releaser).action_release()
    odoo_env["ir.config_parameter"].sudo().set_param(SPREAD, "10")
    with pytest.raises(REFUSED):
        web.with_user(ppl.officer).action_release()  # not a releaser
    web.with_user(ppl.releaser).action_release()
    price = odoo_env["fix.rate.card"].price_for
    assert price(item, channel="storefront")["price"] == 105.0
    assert price(item, channel="quotation")["price"] == 100.0
    market = Diff.create(
        {
            "channel": "marketplace",
            "product_code": _code(item),
            "adjustment_pct": -8.0,
            "reason": "x",
        }
    )
    with pytest.raises(UserError, match="13.00% apart"):
        market.with_user(ppl.releaser).action_release()
    with pytest.raises(REFUSED):
        web.with_user(ppl.officer).write({"adjustment_pct": 9.0})


# ---- FR-PRC-032: the permanent override record ------------------------------------


@pytest.fixture
def est(odoo_env, ppl):
    env = odoo_env
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].search([("company_id", "=", env.company.id)], limit=1)
    if not entity:
        entity = env["fix.entity"].create(
            {"code": "R23E", "legal_name": "%s Entity" % TAG, "company_id": env.company.id}
        )
    branch = env["fix.branch"].create(
        {"name": TAG, "code": TAG[-6:], "entity_id": entity.id, "operating_unit_id": ou.id}
    )
    brand = env["fix.brand"].create({"name": "%s eb" % TAG, "code": "E%s" % TAG[-5:]})
    model = env["fix.device.model"].create({"name": "%s m" % TAG, "brand_id": brand.id})
    customer = env["res.partner"].create({"name": "%s cust" % TAG, "phone": "01711000222"})
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
    return order


def test_a_line_priced_off_its_released_price_leaves_a_permanent_record(odoo_env, ppl, est):
    item = _item(odoo_env, item_type="part")
    _card(odoo_env, ppl.officer, _code(item), 1000.0)
    product = item.product_tmpl_id.product_variant_id
    estimate = (
        odoo_env["fix.estimate"]
        .with_user(ppl.clerk)
        .create(
            {
                "order_id": est.id,
                "line_ids": [
                    Command.create(
                        {
                            "line_type": "part",
                            "product_id": product.id,
                            "description": product.name,
                            "quantity": 1.0,
                            "unit_price": 950.0,
                            "price_override_reason": "loyal customer",
                        }
                    )
                ],
            }
        )
    )
    line = estimate.line_ids
    Log = odoo_env["fix.price.override.log"]
    log = Log.search([("res_model", "=", "fix.estimate.line"), ("res_id", "=", line.id)])
    assert len(log) == 1
    assert (log.original_price, log.override_price, log.actor_id) == (1000.0, 950.0, ppl.clerk)
    assert log.reason == "loyal customer" and log.document == estimate.display_name
    with pytest.raises(UserError, match="permanent"):
        log.write({"override_price": 1.0})
    with pytest.raises(UserError, match="permanent"):
        log.unlink()
    # an unrelated write logs nothing new; a second change logs again
    line.write({"description": "renamed"})
    assert Log.search_count([("res_id", "=", line.id), ("res_model", "=", line._name)]) == 1
    line.write({"unit_price": 920.0})
    assert Log.search_count([("res_id", "=", line.id), ("res_model", "=", line._name)]) == 2


# ---- AUT-PRC-08: a discontinued item's rates ------------------------------------------


def test_discontinued_item_tells_the_officer_then_retires_its_rates(odoo_env, ppl):
    item = _item(odoo_env, item_type="part", vat_class="standard_15")
    successor = _item(odoo_env, item_type="part", vat_class="standard_15")
    std = _card(odoo_env, ppl.officer, _code(item), 500.0)
    amc = contract_helpers.contract(odoo_env)
    contract = _card(odoo_env, ppl.officer, _code(item), 450.0, min_tier=99, contract_id=amc.id)
    item._guarded().write(
        {"state": "deprecated", "successor_id": successor.id, "discontinued_at": _today(odoo_env)}
    )
    event = {
        "event_id": "evt-%s" % TAG,
        "event_type": "catalogue.item_discontinued",
        "aggregate": "fix.catalogue.item",
        "aggregate_id": item.id,
        "payload": {"successor_id": successor.id, "end_of_support": None},
    }
    Consumers = odoo_env["fix.m11.pricing.consumers"]
    out = Consumers.consume_item_discontinued(event)
    assert out["retired"] == 1
    assert (std.state, std.active) == ("retired", False)
    assert contract.state == "released"  # BRU-CAT-10: the contract still services it
    reviews = odoo_env["fix.price.review"].search([("event_ref", "=", event["event_id"])])
    assert set(reviews.mapped("rate_card_id").ids) == {std.id, contract.id}
    assert reviews.mapped("successor_item_id") == successor
    assert reviews.filtered(lambda r: r.rate_card_id == std).card_retired
    # the officer was told
    assert reviews.activity_ids.filtered(lambda a: a.user_id == ppl.officer)
    assert not Consumers.consume_item_discontinued(event)["created"]  # idempotent
    # the price service offers the live successor
    assert odoo_env["fix.rate.card"].price_for(item)["successor_item_id"] == successor.id
    # an officer disposes; only the relay creates reviews
    review = reviews[:1].with_user(ppl.officer)
    with pytest.raises(UserError, match="State what was done"):
        review.action_dispose()
    review.action_dispose(note="successor rate raised")
    assert review.state == "done" and review.decided_by == ppl.officer
    with pytest.raises(REFUSED):
        odoo_env["fix.price.review"].with_user(ppl.officer).create(
            {"kind": "cost", "detail": "forged"}
        )
    with pytest.raises(REFUSED):
        review.write({"state": "open"})
    with pytest.raises(AccessError):
        Consumers.with_user(ppl.officer).consume_item_discontinued(event)


def test_obsolete_item_retires_its_contract_rates_too(odoo_env, ppl):
    item = _item(odoo_env, item_type="part", vat_class="standard_15")
    amc = contract_helpers.contract(odoo_env)
    contract = _card(odoo_env, ppl.officer, _code(item), 450.0, min_tier=99, contract_id=amc.id)
    item._guarded().write(
        {"state": "deprecated", "end_of_support_date": _today(odoo_env) - timedelta(days=1)}
    )
    odoo_env["fix.catalogue.item"].cron_obsolete_discontinued()
    assert item.state == "obsolete" and contract.state == "retired"


# ---- AUT-PRC-10: an M15 cost movement flags cards under the floor ----------------------


def test_a_cost_movement_flags_rates_now_under_the_cost_floor(odoo_env, ppl):
    item = _item(odoo_env, item_type="part")
    product = item.product_tmpl_id.product_variant_id
    card = _card(odoo_env, ppl.officer, _code(item), 500.0)
    part = (
        odoo_env["fix.spare.part"]
        .sudo()
        .create(
            {
                "name": "Part %s" % TAG,
                "part_number": _code(item),
                "unit_cost": 400.0,
                "product_id": product.id,
            }
        )
    )
    event = {
        "event_type": "stock.received",
        "aggregate": "fix.stock.receipt",
        "aggregate_id": 0,
        "payload": {"lines": [{"part_id": part.id, "accepted": 1, "unit_cost": 400.0}]},
    }
    Consumers = odoo_env["fix.m11.pricing.consumers"]
    assert not Consumers.consume_stock_received(event)["created"]
    part.write({"unit_cost": 620.0})
    part.invalidate_recordset()
    out = Consumers.consume_stock_received(event)
    review = odoo_env["fix.price.review"].browse(out["ids"])
    assert (review.kind, review.rate_card_id, review.floor_price) == ("cost", card, 620.0)
    assert not Consumers.consume_stock_adjusted(event)["created"]  # one open review per card
    # the owner's target margin flags a thin margin above the floor
    other = _item(odoo_env, item_type="part")
    card2 = _card(odoo_env, ppl.officer, _code(other), 1000.0)
    odoo_env["fix.spare.part"].sudo().create(
        {
            "name": "Part2 %s" % TAG,
            "part_number": _code(other),
            "unit_cost": 900.0,
            "product_id": other.product_tmpl_id.product_variant_id.id,
        }
    )
    Review = odoo_env["fix.price.review"]
    assert not Review._flag_cost(card2)
    odoo_env["ir.config_parameter"].sudo().set_param("cd_rate_card.margin_target_pct", "20")
    assert Review._flag_cost(card2).kind == "cost"


# ---- AUT-PRC-11 / FR-PRC-045 ---------------------------------------------------------


def test_consistency_scan_flags_a_channel_spread_beyond_the_maximum(odoo_env, ppl):
    item = _item(odoo_env, item_type="part")
    _card(odoo_env, ppl.officer, _code(item), 100.0)
    params = odoo_env["ir.config_parameter"].sudo()
    params.set_param(SPREAD, "10")
    diff = (
        odoo_env["fix.channel.differential"]
        .with_user(ppl.officer)
        .create(
            {
                "channel": "storefront",
                "product_code": _code(item),
                "adjustment_pct": 8.0,
                "reason": "x",
            }
        )
    )
    diff.with_user(ppl.releaser).action_release()
    Review = odoo_env["fix.price.review"]
    Review.cron_consistency_scan()
    assert not Review.search([("kind", "=", "spread"), ("product_code", "=", _code(item))])
    params.set_param(SPREAD, "5")  # the owner tightens the spread after release
    Review.cron_consistency_scan()
    found = Review.search([("kind", "=", "spread"), ("product_code", "=", _code(item))])
    assert len(found) == 1 and "8.0% apart" in found.detail
    Review.cron_consistency_scan()
    assert Review.search_count([("kind", "=", "spread"), ("product_code", "=", _code(item))]) == 1


# ---- M11-F15: the VAT basis of the item's class -------------------------------------


def test_price_carries_the_vat_of_the_items_class(odoo_env, ppl):
    standard = _item(odoo_env, item_type="part", vat_class="standard_15")
    exempt = _item(odoo_env, item_type="part", vat_class="exempt")
    reduced = _item(odoo_env, item_type="part", vat_class="reduced")
    for item in (standard, exempt, reduced):
        _card(odoo_env, ppl.officer, _code(item), 100.0)
    Card = odoo_env["fix.rate.card"]
    res = Card.price_for(standard)
    rate = Card._vat_rate(odoo_env.company, _today(odoo_env))
    assert res["vat_rate"] == rate
    if rate is not None:
        assert res["price_incl"] == round(100.0 * (1 + rate / 100.0), 2)
    res = Card.price_for(exempt)
    assert (res["vat_rate"], res["price_incl"]) == (0.0, 100.0)
    res = Card.price_for(reduced)
    assert (res["vat_rate"], res["price_incl"]) == (None, None)  # M51 decides on the invoice


# ---- M37-F5: a subscription from a plan definition -----------------------------------


def test_plan_definition_gives_the_subscription_its_price_and_cycle(odoo_env, ppl):
    item = _item(odoo_env, item_type="subscription", vat_class="standard_15")
    plan = odoo_env["fix.subscription.plan.def"].create(
        {"item_id": item.id, "billing_frequency": "quarterly", "commitment_months": 12}
    )
    with pytest.raises(UserError, match="no released M11 price"):
        plan._fix_subscription_vals()
    card = _card(odoo_env, ppl.officer, _code(item), 2400.0, line_type="labour")
    vals = plan.with_user(ppl.clerk)._fix_subscription_vals()
    assert (vals["billing_cycle"], vals["recurring_amount"], vals["rate_card_id"]) == (
        "quarterly",
        2400.0,
        card.id,
    )
    assert vals["plan_def_id"] == plan.id and vals["commitment_months"] == 12
    plan.write({"billing_frequency": "half_yearly"})
    with pytest.raises(UserError, match="M39 bills"):
        plan._fix_subscription_vals()
    assert odoo_env["fix.subscription.plan.def"]._fix_for_item(item) == plan


# ---- FR-CAT-046: the impact preview gates the lifecycle -------------------------------


def test_discontinue_needs_a_fresh_impact_preview_when_rates_reference_the_item(odoo_env, ppl):
    item = _item(odoo_env, item_type="part", vat_class="standard_15")
    card = _card(odoo_env, ppl.officer, _code(item), 500.0)
    impact = item._fix_impact_preview()
    assert impact["total"] >= 1
    assert any(card.display_name in g["records"] for g in impact["groups"])
    with pytest.raises(UserError, match="Preview the impact first"):
        item.action_discontinue(reason="end of life")
    item.action_preview_impact()
    assert "Rate cards: 1" in item.impact_summary
    _card(odoo_env, ppl.officer, _code(item), 400.0, min_tier=2)  # the impact changed
    with pytest.raises(UserError, match="changed since the impact was previewed"):
        item.action_discontinue(reason="end of life")
    item.action_preview_impact()
    item.action_discontinue(reason="end of life")
    assert item.state == "deprecated" and not item.impact_hash
    # nothing references it: no preview needed
    lone = _item(odoo_env, item_type="part", vat_class="standard_15")
    lone.action_restrict(reason="recall")
    assert lone.state == "restricted"


# ---- M37-F5: the repair warranty of the catalogue service reaches M01 --------------------


def test_the_catalogue_repair_warranty_reaches_the_m01_warranty(odoo_env, ppl, est):
    item = _item(odoo_env, item_type="service", vat_class="standard_15", repair_warranty_days=180)
    est.write({"catalog_item_id": item.id})
    est._guarded().write({"delivered_at": fields.Datetime.now()})
    policy = est.service_warranty_days
    est._fix_issue_repair_warranty()
    assert est.service_warranty_days == max(policy, 180)
    assert est.service_warranty_until == _dhaka_date(est.delivered_at) + timedelta(
        days=max(policy, 180)
    )


# ---- FR-PRC-010 / BRU-PRC-17: the anonymous indicative band ---------------------------


def test_indicative_band_shows_a_published_price_band_and_nothing_else(odoo_env, ppl):
    item = _item(odoo_env, item_type="part", vat_class="exempt")
    _card(odoo_env, ppl.officer, _code(item), 1000.0)
    Card = odoo_env["fix.rate.card"]
    assert Card.indicative_band(_code(item)) is None  # not published
    item._guarded().write({"state": "published", "is_published": True, "name_bn": "পণ্য"})
    gold = odoo_env["res.partner"].create({"name": "%s gold" % TAG})
    _card(odoo_env, ppl.officer, _code(item), 800.0, partner_id=gold.id)
    band = Card.indicative_band(_code(item))
    assert (band["low"], band["high"], band["vat"]) == (1000.0, 1000.0, "inclusive")
    assert set(band) == {"item", "item_bn", "code", "currency", "low", "high", "vat", "indicative"}
    # the limiter
    key = "test-%s" % TAG
    assert all(allow(key, 3, now=100.0 + i) for i in range(3))
    assert not allow(key, 3, now=103.0)
    assert allow(key, 3, now=161.0)


# ---- wiring ------------------------------------------------------------------------


class TestDeployment:
    def test_consumers_crons_acl_and_surfaces_exist(self, odoo_env):
        env = odoo_env
        Consumer = env["fix.event.consumer"].sudo()
        for event, method in (
            ("catalogue.item_discontinued", "consume_item_discontinued"),
            ("catalogue.srt_rebaselined", "consume_srt_rebaselined"),
            ("stock.received", "consume_stock_received"),
            ("stock.adjusted", "consume_stock_adjusted"),
        ):
            row = Consumer.search(
                [("event_type", "=", event), ("method", "=", method), ("active", "=", True)]
            )
            assert row.model == "fix.m11.pricing.consumers", event
            assert hasattr(env[row.model], method)
        for xmlid, code in (
            ("cd_rate_card.ir_cron_m11_cost_scan", "model.cron_cost_scan()"),
            ("cd_rate_card.ir_cron_m11_consistency_scan", "model.cron_consistency_scan()"),
            ("cd_rate_card.ir_cron_m11_leakage_scan", "model.cron_leakage_scan()"),
        ):
            cron = env.ref(xmlid)
            assert cron.active and cron.code == code
        for model in (
            "fix.price.break",
            "fix.channel.differential",
            "fix.price.override.log",
            "fix.price.review",
            "fix.catalogue.numbering",
        ):
            acl = env["ir.model.access"].sudo().search([("model_id.model", "=", model)])
            assert acl, model
            assert env["ir.rule"].sudo().search([("model_id.model", "=", model)]), model
        from odoo.addons.cd_p03_portal.controllers.a04 import m11, m37

        assert m11.SURFACES["fix.price.review"]["actions"] == {
            "action_dispose",
            "action_accept",
            "action_reject",
        }
        assert {"action_release", "action_retire"} == m11.SURFACES["fix.channel.differential"][
            "actions"
        ]
        assert {"price_exceptions", "price_consistency"} <= set(m11.REPORTS)
        assert {"action_preview_impact", "action_assign_code"} <= m37.SURFACES[
            "fix.catalogue.item"
        ]["actions"]
        assert "fix.catalogue.numbering" in m37.SURFACES

    def test_report_packs_run_for_a_plain_user(self, odoo_env):
        from odoo.addons.cd_p03_portal.controllers.a04 import m11

        user = _user(odoo_env, "viewer")
        env = odoo_env(user=user)
        for name in ("price_exceptions", "price_consistency"):
            pack = m11.REPORTS[name](env)
            assert pack["title"] and isinstance(pack["rows"], list)
