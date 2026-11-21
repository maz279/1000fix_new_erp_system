# M11 capture audit, pass 2 (18 Nov 2026): the records four sub-module pages
# could not capture, exercised as non-admin users on the live ORM (`odoo_env`,
# rolled back).
#
#   page 4  fix.parts.price.scheme  FR-PRC-013 markup / banded / grade / fixed
#   page 9  fix.price.adjustment    FR-PRC-018/019 premiums and surcharges
#   page 11 fix.price.mass.change   FR-PRC-024 / BRU-PRC-16 mass change
#   page 5  fix.rate.card.contract_id  FR-PRC-016 / AC-08 contract lane
#   pages 1/10 fix.price.simulation  inputs as fields, premiums on the trace
#   page 8  fix.promotion.catalogue_item_ids  FR-PRC-037 item scope
import itertools
import json
import uuid
from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox, inbox_task
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
TAG = "M11P2-%s" % uuid.uuid4().hex[:6].upper()
_SEQ = itertools.count(1)
OFFICER = "cd_rate_card.group_pricing_officer"
RELEASER = "cd_rate_card.group_price_releaser"
CCO = "cd_entity_config.group_dofa_tier_4"


def _user(env, tag, groups=()):
    n = next(_SEQ)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "%s %s %d" % (TAG, tag, n),
                "login": "%s.%s.%d@m11p2.test" % (TAG.lower(), tag, n),
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
            }
        )
    )


@pytest.fixture
def ppl(odoo_env):
    class P:
        clerk = _user(odoo_env, "clerk")
        officer = _user(odoo_env, "officer", [OFFICER])
        releaser = _user(odoo_env, "rel", [RELEASER])
        cco = _user(odoo_env, "cco", [RELEASER, CCO])

    return P


def _today(env):
    return fields.Date.context_today(env["res.users"])


def _release(record, ppl):
    record.with_user(ppl.officer).action_submit()
    approve_via_inbox(record, ppl.releaser, requester=ppl.officer)
    assert record.state == "active"
    return record


# --------------------------------------------------------------- page 4
def _scheme(env, user, **vals):
    base = {"name": "%s scheme" % TAG, "method": "markup", "markup_pct": 25.0}
    base.setdefault("valid_from", _today(env))
    base.update(vals)
    return env["fix.parts.price.scheme"].with_user(user).create(base)


def test_a_plain_user_does_not_record_a_parts_scheme(odoo_env, ppl):
    with pytest.raises(REFUSED), odoo_env.cr.savepoint():
        _scheme(odoo_env, ppl.clerk)


def test_markup_on_cost_with_whole_taka_rounding(odoo_env, ppl):
    scheme = _scheme(odoo_env, ppl.officer, markup_pct=25.0, rounding_step=5.0)
    assert scheme.price_for(1000.0) == 1250.0
    assert scheme.price_for(999.0) == 1250.0  # 1248.75 -> nearest 5
    with pytest.raises(UserError, match="positive cost"), odoo_env.cr.savepoint():
        scheme.price_for(0.0)


def test_banded_markup_by_cost_tier(odoo_env, ppl):
    scheme = _scheme(
        odoo_env,
        ppl.officer,
        method="banded",
        rounding_step=0.01,
        band_ids=[
            (0, 0, {"cost_from": 0.0, "cost_to": 500.0, "markup_pct": 40.0}),
            (0, 0, {"cost_from": 500.0, "cost_to": 2000.0, "markup_pct": 25.0}),
            (0, 0, {"cost_from": 2000.0, "markup_pct": 15.0}),
        ],
    )
    assert scheme.price_for(100.0) == 140.0
    assert scheme.price_for(1000.0) == 1250.0
    assert scheme.price_for(5000.0) == 5750.0


def test_a_band_ladder_with_a_gap_is_never_released(odoo_env, ppl):
    scheme = _scheme(
        odoo_env,
        ppl.officer,
        method="banded",
        band_ids=[
            (0, 0, {"cost_from": 0.0, "cost_to": 500.0, "markup_pct": 40.0}),
            (0, 0, {"cost_from": 800.0, "markup_pct": 20.0}),
        ],
    )
    with pytest.raises(UserError, match="without a gap"), odoo_env.cr.savepoint():
        scheme.with_user(ppl.officer).action_submit()


def test_grade_differential(odoo_env, ppl):
    scheme = _scheme(
        odoo_env,
        ppl.officer,
        method="grade",
        markup_pct=30.0,
        genuine_adj_pct=5.0,
        aftermarket_adj_pct=-10.0,
        refurbished_adj_pct=-40.0,
        rounding_step=0.01,
    )
    assert scheme.price_for(1000.0, "genuine") == 1350.0
    assert scheme.price_for(1000.0, "aftermarket") == 1200.0
    assert scheme.price_for(1000.0, "oem") == 1300.0
    with pytest.raises(UserError, match="below its cost"), odoo_env.cr.savepoint():
        scheme.price_for(1000.0, "refurbished")


def test_a_scheme_prices_only_once_released_by_another_releaser(odoo_env, ppl):
    Scheme = odoo_env["fix.parts.price.scheme"]
    scheme = _scheme(odoo_env, ppl.officer)
    assert not Scheme.scheme_for()
    scheme.with_user(ppl.officer).action_submit()
    with pytest.raises(UserError, match="approver's inbox"), odoo_env.cr.savepoint():
        scheme.with_user(ppl.releaser).action_approve()
    approve_via_inbox(scheme, ppl.releaser, requester=ppl.officer)
    assert (scheme.state, scheme.version, scheme.approved_by) == ("active", 1, ppl.releaser)
    assert Scheme.scheme_for() == scheme


def test_the_most_specific_scheme_wins(odoo_env, ppl):
    Scheme = odoo_env["fix.parts.price.scheme"]
    category = odoo_env["product.category"].create({"name": "%s screens" % TAG})
    generic = _release(_scheme(odoo_env, ppl.officer, markup_pct=20.0), ppl)
    screens = _release(
        _scheme(odoo_env, ppl.officer, category_id=category.id, markup_pct=35.0), ppl
    )
    graded = _release(
        _scheme(
            odoo_env,
            ppl.officer,
            category_id=category.id,
            provenance_grade="genuine",
            markup_pct=45.0,
        ),
        ppl,
    )
    assert Scheme.scheme_for() == generic
    assert Scheme.scheme_for(category=category) == screens
    assert Scheme.scheme_for(category=category, grade="genuine") == graded
    assert Scheme.scheme_for(category=category, grade="oem") == screens


def test_a_released_scheme_and_its_bands_never_change(odoo_env, ppl):
    scheme = _scheme(
        odoo_env,
        ppl.officer,
        method="banded",
        band_ids=[(0, 0, {"cost_from": 0.0, "markup_pct": 30.0})],
    )
    _release(scheme, ppl)
    with pytest.raises(UserError, match="cannot change any more"), odoo_env.cr.savepoint():
        scheme.with_user(ppl.officer).write({"markup_pct": 99.0})
    with pytest.raises(UserError, match="cannot change"), odoo_env.cr.savepoint():
        scheme.band_ids.with_user(ppl.officer).write({"markup_pct": 99.0})
    with pytest.raises(UserError, match="cannot change"), odoo_env.cr.savepoint():
        odoo_env["fix.parts.price.band"].with_user(ppl.officer).create(
            {"scheme_id": scheme.id, "cost_from": 0.0, "markup_pct": 1.0}
        )


def test_a_new_version_supersedes_and_history_keeps_its_window(odoo_env, ppl):
    Scheme = odoo_env["fix.parts.price.scheme"]
    today = _today(odoo_env)
    old = _release(
        _scheme(odoo_env, ppl.officer, markup_pct=20.0, valid_from=today - timedelta(days=30)), ppl
    )
    new = _release(_scheme(odoo_env, ppl.officer, markup_pct=22.0, valid_from=today), ppl)
    assert (old.state, old.valid_to) == ("superseded", today - timedelta(days=1))
    assert new.version == 2
    assert Scheme.scheme_for(on_date=today - timedelta(days=5)) == old
    assert Scheme.scheme_for(on_date=today) == new
    backdated = _scheme(odoo_env, ppl.officer, valid_from=today - timedelta(days=10))
    with pytest.raises(UserError, match="already prices this scope"), odoo_env.cr.savepoint():
        backdated.with_user(ppl.officer).action_submit()


# --------------------------------------------------------------- page 9
def _premium(env, user, **vals):
    base = {
        "name": "%s premium" % TAG,
        "code": "%s-%d" % (TAG, next(_SEQ)),
        "adjustment_type": "express",
        "basis": "percent",
        "value": 20.0,
        "applies_to": "labour",
        "valid_from": _today(env),
    }
    base.update(vals)
    return env["fix.price.adjustment"].with_user(user).create(base)


@pytest.mark.parametrize(
    "vals",
    [
        {"value": 0.0},
        {"value": -5.0},
        {"basis": "percent", "value": 150.0},
        {"adjustment_type": "distance", "distance_from_km": 10.0, "distance_to_km": 5.0},
        {"adjustment_type": "after_hours", "hour_from": 20.0, "hour_to": 20.0},
    ],
)
def test_a_premium_is_bounded(odoo_env, ppl, vals):
    with pytest.raises(REFUSED), odoo_env.cr.savepoint():
        _premium(odoo_env, ppl.officer, **vals)


def test_a_zone_premium_names_its_branches(odoo_env, ppl):
    premium = _premium(odoo_env, ppl.officer, adjustment_type="zone")
    with pytest.raises(UserError, match="names the branches"), odoo_env.cr.savepoint():
        premium.with_user(ppl.officer).action_submit()


def test_premiums_apply_only_once_released_and_only_where_they_match(odoo_env, ppl):
    Premium = odoo_env["fix.price.adjustment"]
    express = _premium(odoo_env, ppl.officer, value=20.0)
    assert Premium.premiums_for(["express"], 1000.0, line_type="labour") == []
    _release(express, ppl)
    night = _release(
        _premium(
            odoo_env,
            ppl.officer,
            adjustment_type="after_hours",
            basis="fixed",
            value=300.0,
            hour_from=20.0,
            hour_to=8.0,
        ),
        ppl,
    )
    far = _release(
        _premium(
            odoo_env,
            ppl.officer,
            adjustment_type="distance",
            basis="fixed",
            value=500.0,
            applies_to="transport",
            distance_from_km=10.0,
            distance_to_km=25.0,
        ),
        ppl,
    )
    assert Premium.premiums_for(["express"], 1000.0, line_type="labour") == [(express, 200.0)]
    assert Premium.premiums_for(["express"], 1000.0, line_type="part") == []
    assert Premium.premiums_for(["after_hours"], 1000.0, hour=23.0) == [(night, 300.0)]
    assert Premium.premiums_for(["after_hours"], 1000.0, hour=2.0) == [(night, 300.0)]
    assert Premium.premiums_for(["after_hours"], 1000.0, hour=12.0) == []
    assert Premium.premiums_for(["distance"], 0.0, line_type="transport", distance_km=12.0) == [
        (far, 500.0)
    ]
    assert Premium.premiums_for(["distance"], 0.0, line_type="transport", distance_km=30.0) == []


# --------------------------------------------------------------- page 11
def _card(env, code, price, **vals):
    card = (
        env["fix.rate.card"]
        .sudo()
        .create({"product_code": code, "unit_price": price, "line_type": "labour", **vals})
    )
    card._guarded().write({"state": "released"})
    return card


@pytest.fixture
def cards(odoo_env):
    prefix = "%s-SRV" % TAG
    return {
        "a": _card(odoo_env, prefix + "-A", 1000.0),
        "b": _card(odoo_env, prefix + "-B", 2000.0),
        "part": _card(odoo_env, prefix + "-P", 500.0, line_type="part"),
        "prefix": prefix,
    }


def _mass(env, user, prefix, **vals):
    base = {
        "line_type": "labour",
        "product_code_prefix": prefix,
        "change_kind": "percent",
        "value": 10.0,
        "effective_date": _today(env) + timedelta(days=7),
        "reason": "Annual labour review",
    }
    base.update(vals)
    return env["fix.price.mass.change"].with_user(user).create(base)


def test_the_preview_lists_every_matching_released_rate(odoo_env, ppl, cards):
    draft = (
        odoo_env["fix.rate.card"]
        .sudo()
        .create({"product_code": cards["prefix"] + "-D", "unit_price": 700.0})
    )
    change = _mass(odoo_env, ppl.officer, cards["prefix"])
    change.with_user(ppl.officer).action_preview()
    got = {line.rate_card_id: (line.current_price, line.new_price) for line in change.line_ids}
    assert got == {cards["a"]: (1000.0, 1100.0), cards["b"]: (2000.0, 2200.0)}
    assert draft not in got and cards["part"] not in got


def test_a_rate_pushed_below_its_floor_blocks_submission(odoo_env, ppl, cards):
    odoo_env["fix.price.floor"].sudo().create(
        {"name": "floor", "product_code": cards["a"].product_code, "floor_price": 950.0}
    )
    change = _mass(odoo_env, ppl.officer, cards["prefix"], value=-10.0)
    with pytest.raises(UserError, match="below their floor"), odoo_env.cr.savepoint():
        change.with_user(ppl.officer).action_submit()
    assert change.state == "draft"


def test_a_scheduled_change_waits_for_its_date_then_applies_and_rolls_back(odoo_env, ppl, cards):
    Mass = odoo_env["fix.price.mass.change"]
    change = _mass(odoo_env, ppl.officer, cards["prefix"])
    change.with_user(ppl.officer).action_submit()
    # the author cannot approve; a plain releaser can (future date)
    assert not inbox_task(change, ppl.officer)
    approve_via_inbox(change, ppl.releaser, requester=ppl.officer)
    assert change.state == "approved"
    assert cards["a"].unit_price == 1000.0
    Mass.cron_apply_due()
    assert change.state == "approved"  # not yet its date
    change._guarded().write({"effective_date": _today(odoo_env)})
    Mass.cron_apply_due()
    assert change.state == "applied"
    # A04 ERP audit M11-F4: the new price is a dated version from the
    # effective date; the rate in force keeps its history
    Card = odoo_env["fix.rate.card"]
    assert (cards["a"].unit_price, cards["b"].unit_price) == (1000.0, 2000.0)
    assert (
        Card._resolve(cards["a"].product_code).unit_price,
        Card._resolve(cards["b"].product_code).unit_price,
    ) == (1100.0, 2200.0)
    with pytest.raises(REFUSED), odoo_env.cr.savepoint():
        change.with_user(ppl.officer).action_rollback(reason="wrong")
    change.with_user(ppl.releaser).action_rollback(reason="Board reversed the review")
    assert change.state == "rolled_back"
    assert (
        Card._resolve(cards["a"].product_code).unit_price,
        Card._resolve(cards["b"].product_code).unit_price,
    ) == (1000.0, 2000.0)


def test_rollback_refuses_when_a_rate_moved_since(odoo_env, ppl, cards):
    change = _mass(odoo_env, ppl.officer, cards["prefix"], effective_date=_today(odoo_env))
    change.with_user(ppl.officer).action_submit()
    approve_via_inbox(change, ppl.cco, requester=ppl.officer)
    assert change.state == "applied"
    version = change.line_ids.filtered(lambda r: r.rate_card_id == cards["a"]).new_rate_card_id
    version._guarded().write({"unit_price": 1500.0})
    with pytest.raises(UserError, match="changed again"), odoo_env.cr.savepoint():
        change.with_user(ppl.releaser).action_rollback(reason="undo")


def test_an_immediate_change_is_the_ccos_decision(odoo_env, ppl, cards):
    change = _mass(odoo_env, ppl.officer, cards["prefix"], effective_date=_today(odoo_env))
    change.with_user(ppl.officer).action_submit()
    # routed to the CCO tier, not to a plain releaser
    assert not inbox_task(change, ppl.releaser)
    approve_via_inbox(change, ppl.cco, requester=ppl.officer)
    assert change.state == "applied"
    assert odoo_env["fix.rate.card"]._resolve(cards["a"].product_code).unit_price == 1100.0


def test_approved_terms_are_pinned(odoo_env, ppl, cards):
    change = _mass(odoo_env, ppl.officer, cards["prefix"])
    change.with_user(ppl.officer).action_submit()
    with pytest.raises(UserError, match="pinned"), odoo_env.cr.savepoint():
        change.with_user(ppl.officer).write({"value": 50.0})


# --------------------------------------------------------------- page 5
def _contract(env, code, state="active", start=None, end=None):
    today = _today(env)
    ou = env["operating.unit"].sudo().search([], limit=1)
    customer = env["res.partner"].sudo().create({"name": "%s customer" % TAG, "is_company": True})
    contract = (
        env["fix.contract"]
        .sudo()
        .create(
            {
                "code": code,
                "name": "%s AMC" % TAG,
                "family": "amc",
                "customer_id": customer.id,
                "operating_unit_id": ou.id,
                "date_start": start or today - timedelta(days=10),
                "date_end": end or today + timedelta(days=355),
                "annual_value": 120000.0,
                "stamp_duty_cert_no": "SD-%s" % code,
                "stamp_duty_amount": 300.0,
            }
        )
    )
    contract._guarded().write({"state": state})
    return contract


def test_a_contract_rate_names_a_real_contract(odoo_env, ppl):
    Card = odoo_env["fix.rate.card"].with_user(ppl.officer)
    with pytest.raises(UserError, match="names its M08 contract"), odoo_env.cr.savepoint():
        Card.create(
            {"product_code": TAG, "unit_price": 400.0, "min_tier": 99, "contract_no": "NOPE-1"}
        )
    contract = _contract(odoo_env, "%s-K1" % TAG)
    card = Card.create({"product_code": TAG, "unit_price": 400.0, "contract_id": contract.id})
    assert (card.min_tier, card.contract_no) == (99, contract.code)
    assert (card.valid_from, card.valid_to) == (contract.date_start, contract.date_end)


def test_a_contract_rate_stays_within_the_term(odoo_env, ppl):
    contract = _contract(odoo_env, "%s-K2" % TAG)
    with pytest.raises(UserError, match="within the contract's term"), odoo_env.cr.savepoint():
        odoo_env["fix.rate.card"].with_user(ppl.officer).create(
            {
                "product_code": TAG,
                "unit_price": 400.0,
                "contract_id": contract.id,
                "valid_to": contract.date_end + timedelta(days=30),
            }
        )


def test_the_contract_lane_lapses_with_the_contract(odoo_env, ppl):
    Card = odoo_env["fix.rate.card"]
    contract = _contract(odoo_env, "%s-K3" % TAG)
    tier = _card(odoo_env, TAG + "-L", 500.0)
    lane = Card.sudo().create(
        {"product_code": TAG + "-L", "unit_price": 400.0, "contract_id": contract.id}
    )
    lane._guarded().write({"state": "released"})
    assert Card._resolve(TAG + "-L", contract_no=contract.code) == lane
    contract._guarded().write({"state": "expired"})
    assert Card._resolve(TAG + "-L", contract_no=contract.code) == tier


# --------------------------------------------------------------- pages 1/10
def test_the_simulation_takes_fields_and_names_the_premiums(odoo_env, ppl):
    card = _card(odoo_env, TAG + "-SIM", 1000.0)
    _release(_premium(odoo_env, ppl.officer, adjustment_type="weekend", value=10.0), ppl)
    sim = (
        odoo_env["fix.price.simulation"]
        .with_user(ppl.clerk)
        .create(
            {
                "name": "%s sim" % TAG,
                "rate_card_id": card.id,
                "quantity": 3.0,
                "premium_kinds": "weekend",
            }
        )
    )
    sim.with_user(ppl.clerk).action_compute()
    out = json.loads(sim.result_json)
    assert out["quantity"] == 3.0
    assert [p["amount"] for p in out["premiums"]] == [100.0]
    net = round(1000.0 - out["promotion_discount_per_unit"] + 100.0, 2)
    assert out["net_unit_price"] == net
    assert out["net_total"] == round(net * 3.0, 2)


# --------------------------------------------------------------- page 8
def test_a_promotion_for_named_items_discounts_only_them(odoo_env, ppl):
    Promo = odoo_env["fix.promotion"]
    tmpl = (
        odoo_env["product.template"]
        .sudo()
        .create({"name": "%s item" % TAG, "default_code": TAG + "-ITEM"})
    )
    item = odoo_env["fix.catalogue.item"].sudo().search(
        [("product_tmpl_id", "=", tmpl.id)], limit=1
    ) or odoo_env["fix.catalogue.item"].sudo().create(
        {"name": "%s item" % TAG, "product_tmpl_id": tmpl.id, "item_type": "part"}
    )
    promo = Promo.with_user(ppl.officer).create(
        {
            "name": "%s promo" % TAG,
            "code": TAG,
            "value": 10.0,
            "valid_from": _today(odoo_env),
            "valid_until": _today(odoo_env) + timedelta(days=5),
            "catalogue_item_ids": [(6, 0, item.ids)],
        }
    )
    promo._guarded().write({"state": "active"})
    assert promo.covers(TAG + "-ITEM")
    assert not promo.covers("OTHER")
    assert not promo.covers(None)
    assert Promo.best_combination(promo, 1000.0, product_code=TAG + "-ITEM")[1] == 100.0
    assert Promo.best_combination(promo, 1000.0, product_code="OTHER")[1] == 0.0
    promo._guarded().write({"state": "in_review"})
    with pytest.raises(UserError, match="items it applies to"), odoo_env.cr.savepoint():
        promo.with_user(ppl.officer).write({"catalogue_item_ids": [(5, 0, 0)]})


def test_an_author_who_is_also_a_releaser_never_releases_their_own(odoo_env, ppl):
    """BRU-PRC-07 / SOD-14: holding both roles does not let the author decide."""
    both = _user(odoo_env, "both", [OFFICER, RELEASER])
    scheme = _scheme(odoo_env, both)
    scheme.with_user(both).action_submit()
    assert not inbox_task(scheme, both)
    with pytest.raises(UserError), odoo_env.cr.savepoint():
        scheme.with_user(both).action_approve()
    approve_via_inbox(scheme, ppl.releaser, requester=both)
    assert scheme.state == "active"
