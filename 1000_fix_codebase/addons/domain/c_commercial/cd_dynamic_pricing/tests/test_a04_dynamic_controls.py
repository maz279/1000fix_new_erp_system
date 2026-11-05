# A04 C2-C13 (2026-11-04): M11 dynamic-pricing controls, as non-admin users
# on the live ORM (`odoo_env`, rolled back). Replays dr_01 / dr_02 of
# working/A04_evidence/probes/m11_m36_m37/probe_m11.py.
import itertools
import uuid

import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
TAG = "A4CDP-%s" % uuid.uuid4().hex[:6]
_SEQ = itertools.count(1)
OFFICER = "cd_rate_card.group_pricing_officer"
RELEASER = "cd_rate_card.group_price_releaser"


def _user(env, tag, groups=()):
    n = next(_SEQ)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "%s %s %d" % (TAG, tag, n),
                "login": "%s.%s.%d@a04.test" % (TAG.lower(), tag, n),
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

    return P


def _rule(env, user, **kw):
    vals = {"name": "%s rule %d" % (TAG, next(_SEQ)), "adjustment_pct": 10.0}
    vals.update(kw)
    return env["fix.dynamic.price.rule"].with_user(user).create(vals)


def test_plain_user_does_not_author_a_rule(odoo_env, ppl):
    with pytest.raises(REFUSED), odoo_env.cr.savepoint():
        _rule(odoo_env, ppl.clerk)


def test_rule_cannot_declare_its_own_corridor_or_price_to_zero(odoo_env, ppl):
    """dr_01: a -100% rule with a self-declared corridor priced BDT 0."""
    with pytest.raises(ValidationError, match="BRU-PRC-09"), odoo_env.cr.savepoint():
        _rule(odoo_env, ppl.officer, adjustment_pct=-100.0, min_adjustment=-100.0)
    with pytest.raises(ValidationError, match="BRU-PRC-09"), odoo_env.cr.savepoint():
        _rule(odoo_env, ppl.officer, adjustment_pct=150.0, max_adjustment=500.0)
    rule = _rule(odoo_env, ppl.officer, adjustment_pct=-50.0, surge_multiplier=0.01)
    assert rule.apply_to(1000.0) == 5.0  # bounded, never free


def test_corridor_is_the_policy_parameter(odoo_env, ppl):
    odoo_env["ir.config_parameter"].sudo().set_param("cd_dynamic_pricing.corridor_min_pct", "-20")
    with pytest.raises(ValidationError, match="-20.0%"), odoo_env.cr.savepoint():
        _rule(odoo_env, ppl.officer, adjustment_pct=-10.0, min_adjustment=-30.0)
    assert _rule(odoo_env, ppl.officer, adjustment_pct=-10.0, min_adjustment=-20.0)


def test_dynamic_price_never_goes_below_the_floor(odoo_env, ppl):
    code = "%s-SKU" % TAG
    odoo_env["fix.price.floor"].create(
        {"name": "%s floor" % TAG, "product_code": code, "floor_price": 900.0}
    )
    rule = _rule(odoo_env, ppl.officer, adjustment_pct=-30.0, min_adjustment=-30.0)
    out = rule.with_user(ppl.clerk).calculate_and_explain(1000.0, product_code=code)
    assert out["final_price"] == 1000.0 and "Guardrail" in out["text"]
    out = rule.with_user(ppl.clerk).calculate_and_explain(1000.0)
    assert out["final_price"] == 700.0


def test_explanation_is_append_only(odoo_env, ppl):
    """dr_02: the trail was rewritten by a clerk."""
    rule = _rule(odoo_env, ppl.officer)
    out = rule.with_user(ppl.clerk).calculate_and_explain(1000.0)
    exp = odoo_env["fix.price.explanation"].browse(out["explanation_id"])
    for user in (ppl.clerk, ppl.officer, ppl.releaser):
        with pytest.raises(REFUSED), odoo_env.cr.savepoint():
            exp.with_user(user).write({"final_price": 1.0, "rules_applied": "nothing"})
        with pytest.raises(REFUSED), odoo_env.cr.savepoint():
            exp.with_user(user).unlink()
    with pytest.raises(REFUSED), odoo_env.cr.savepoint():
        odoo_env["fix.price.explanation"].with_user(ppl.officer).create({"name": "forged"})
    action = exp.with_user(ppl.clerk).action_reconstruct()
    assert action["params"]["type"] == "success"


def test_disable_is_a_guardrail_enable_is_someone_elses_decision(odoo_env, ppl):
    rule = _rule(odoo_env, ppl.releaser)
    with pytest.raises(UserError, match="cannot be set directly"), odoo_env.cr.savepoint():
        rule.with_user(ppl.officer).write({"active": False})
    rule.with_user(ppl.officer).action_disable(reason="complaints spike")
    assert not rule.active and rule.disabled_by == ppl.officer
    with pytest.raises(UserError, match="Segregation of duties"), odoo_env.cr.savepoint():
        rule.with_user(ppl.releaser).action_enable()  # its author
    other = _user(odoo_env, "rel2", [RELEASER])
    rule.with_user(other).action_enable()
    assert rule.active
