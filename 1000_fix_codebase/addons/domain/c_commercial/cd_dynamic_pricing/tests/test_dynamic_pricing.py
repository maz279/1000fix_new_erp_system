"""cd_dynamic_pricing tests - P10-M05 (CD-M11-01 / R08-M03).

A04 C13 (2026-11-04): these were `inspect.getsource` / hasattr checks. They
now exercise the rule as a non-admin Pricing Officer and a plain user.
"""

import json
import uuid

import pytest
from odoo.exceptions import UserError


@pytest.fixture
def users(odoo_env):
    def make(tag, extra=()):
        groups = [odoo_env.ref("base.group_user").id] + [odoo_env.ref(x).id for x in extra]
        return (
            odoo_env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "A04 C13 %s" % tag,
                    "login": "a04c13.dp.%s.%s@a04.test" % (tag, uuid.uuid4().hex[:6]),
                    "group_ids": [(6, 0, groups)],
                }
            )
        )

    return make("officer", ["cd_rate_card.group_pricing_officer"]), make("clerk")


def test_price_bounds_enforced(odoo_env, users):
    officer, _clerk = users
    Rule = odoo_env["fix.dynamic.price.rule"].with_user(officer)
    with pytest.raises(UserError, match="exceeds the maximum"), odoo_env.cr.savepoint():
        Rule.create({"name": "too high", "adjustment_pct": 20.0, "max_adjustment": 10.0})
    with pytest.raises(UserError, match="below the minimum"), odoo_env.cr.savepoint():
        Rule.create({"name": "too low", "adjustment_pct": -20.0, "min_adjustment": -10.0})


def test_apply_to_is_pure(odoo_env, users):
    officer, clerk = users
    rule = (
        odoo_env["fix.dynamic.price.rule"]
        .with_user(officer)
        .create({"name": "Pure", "adjustment_pct": 10.0, "surge_multiplier": 1.5})
    )
    before = odoo_env["fix.price.explanation"].search_count([])
    assert rule.with_user(clerk).apply_to(1000.0) == 1650.0
    assert odoo_env["fix.price.explanation"].search_count([]) == before


def test_calculate_and_explain_emits_event_and_trail(odoo_env, users):
    officer, clerk = users
    rule = (
        odoo_env["fix.dynamic.price.rule"]
        .with_user(officer)
        .create({"name": "Explained", "adjustment_pct": 10.0})
    )
    out = rule.with_user(clerk).calculate_and_explain(500.0)
    exp = odoo_env["fix.price.explanation"].browse(out["explanation_id"])
    assert (exp.rule_id, exp.final_price) == (rule, 550.0)
    event = odoo_env["fix.event.outbox"].search(
        [("event_type", "=", "pricing.calculated"), ("aggregate_id", "=", rule.id)]
    )
    assert json.loads(event.payload)["final_price"] == 550.0


@pytest.mark.parametrize(
    "rule_type", ["demand_surge", "off_peak", "inventory_clearance", "loyalty_tier"]
)
def test_rule_types(odoo_env, users, rule_type):
    officer, _clerk = users
    rule = (
        odoo_env["fix.dynamic.price.rule"]
        .with_user(officer)
        .create({"name": "Type %s" % rule_type, "rule_type": rule_type})
    )
    assert rule.rule_type == rule_type


def test_rate_card_link(odoo_env, users):
    officer, _clerk = users
    card = odoo_env["fix.rate.card"].create({"product_code": "A4C13-DP", "unit_price": 100.0})
    rule = (
        odoo_env["fix.dynamic.price.rule"]
        .with_user(officer)
        .create({"name": "Linked", "rate_card_id": card.id})
    )
    assert rule.rate_card_id == card
