# cd_dynamic_pricing live-ORM tests — M11 W7 dynamic pricing + explanations.
import json

import pytest
from odoo.exceptions import UserError


def _events(env, rule):
    rows = env["fix.event.outbox"].search(
        [
            ("event_type", "=", "pricing.calculated"),
            ("aggregate", "=", "fix.dynamic.price.rule"),
            ("aggregate_id", "=", rule.id),
        ],
        order="id",
    )
    return [json.loads(row.payload) for row in rows]


def _rule(env, **overrides):
    vals = {"name": "Eid Surge", "adjustment_pct": 10.0, "surge_multiplier": 1.5}
    vals.update(overrides)
    # A04 ERP audit M11-F17: the rule type follows the direction it moves
    mult = vals["surge_multiplier"] if vals["surge_multiplier"] > 0 else 1.0
    if "rule_type" not in vals and (1 + vals["adjustment_pct"] / 100.0) * mult < 1.0:
        vals["rule_type"] = "off_peak"
    return env["fix.dynamic.price.rule"].create(vals)


def test_defaults(odoo_env):
    rule = odoo_env["fix.dynamic.price.rule"].create({"name": "Plain"})
    assert (rule.rule_type, rule.channel, rule.active) == ("demand_surge", "both", True)
    assert (rule.min_adjustment, rule.max_adjustment, rule.surge_multiplier) == (-50.0, 100.0, 1.0)


def test_adjustment_above_the_maximum_is_refused(odoo_env):
    with (
        pytest.raises(UserError, match=r"Adjustment 150.0 exceeds the maximum 100.0"),
        odoo_env.cr.savepoint(),
    ):
        _rule(odoo_env, adjustment_pct=150.0)


def test_adjustment_below_the_minimum_is_refused(odoo_env):
    with (
        pytest.raises(UserError, match=r"Adjustment -60.0 below the minimum -50.0"),
        odoo_env.cr.savepoint(),
    ):
        _rule(odoo_env, adjustment_pct=-60.0)


def test_bounds_are_inclusive(odoo_env):
    assert _rule(odoo_env, adjustment_pct=100.0).adjustment_pct == 100.0
    assert _rule(odoo_env, adjustment_pct=-50.0).adjustment_pct == -50.0


def test_apply_to_combines_adjustment_and_surge(odoo_env):
    # 1000 * 1.10 * 1.5 = 1650.00
    assert _rule(odoo_env).apply_to(1000.0) == 1650.0
    # off-peak 20% discount, no surge: 1234.56 * 0.80 = 987.648 -> 987.65
    assert _rule(odoo_env, adjustment_pct=-20.0, surge_multiplier=1.0).apply_to(1234.56) == 987.65


@pytest.mark.parametrize("multiplier", [0.0, -2.0])
def test_non_positive_surge_multiplier_is_neutral(odoo_env, multiplier):
    # a 0/negative multiplier must never zero or flip a price: 1000 * 1.10
    assert _rule(odoo_env, surge_multiplier=multiplier).apply_to(1000.0) == 1100.0


def test_negative_base_price_is_refused(odoo_env):
    with pytest.raises(UserError, match="Base price cannot be negative"), odoo_env.cr.savepoint():
        _rule(odoo_env).apply_to(-1.0)


def test_calculate_and_explain_persists_the_audit_trail(odoo_env):
    ou = odoo_env["operating.unit"].search([("company_id", "=", odoo_env.company.id)], limit=1)
    rule = _rule(odoo_env, operating_unit_id=ou.id)
    out = rule.calculate_and_explain(1000.0, "Eid-ul-Fitr demand peak")
    text = (
        "Rule 'Eid Surge' (demand_surge): adjustment 10.0%, surge mult 1.5. "
        "Base: 1000.00 -> Final: 1650.00. Context: Eid-ul-Fitr demand peak"
    )
    assert (out["final_price"], out["text"]) == (1650.0, text)
    explanation = odoo_env["fix.price.explanation"].browse(out["explanation_id"])
    assert explanation.name.startswith("EXP/Eid Surge/")
    assert (explanation.base_price, explanation.final_price) == (1000.0, 1650.0)
    assert explanation.rules_applied == text
    assert explanation.model_driven is True  # demand_surge is the ML-driven type
    assert (explanation.rule_id, explanation.operating_unit_id) == (rule, ou)
    assert explanation.company_id == odoo_env.company
    assert _events(odoo_env, rule) == [
        {"rule_name": "Eid Surge", "base_price": 1000.0, "final_price": 1650.0}
    ]


def test_explanation_without_unit_or_context(odoo_env):
    # M11-F17: an off-peak rule lowers the price, so it carries no surge
    rule = _rule(
        odoo_env, name="Night", rule_type="off_peak", adjustment_pct=-10.0, surge_multiplier=1.0
    )
    out = rule.calculate_and_explain(500.0)
    explanation = odoo_env["fix.price.explanation"].browse(out["explanation_id"])
    # 500 * 0.90 = 450.00
    assert out["final_price"] == 450.0
    assert out["text"].endswith("Context: Standard dispatch request")
    assert explanation.model_driven is False
    assert not explanation.operating_unit_id
