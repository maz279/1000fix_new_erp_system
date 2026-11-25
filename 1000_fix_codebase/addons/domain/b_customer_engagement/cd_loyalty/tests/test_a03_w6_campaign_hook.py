"""A03 audit M10-8 (W6): a campaign reward hook moves only through its transitions.

The hook's state was an editable form field with no transitions, so a plain
user "activated" a hook - and started minting campaign points and vouchers -
by typing the state, on a campaign nobody had launched, and could re-price a
live hook. Tested as a NON-ADMIN user: the superuser is trusted by the guard
and would hide the gap. Each control is checked both ways.
"""

import pytest
from odoo.addons.cd_p03_portal.controllers.a03 import m10 as m10_api
from odoo.addons.cd_p03_portal.controllers.a03 import writable
from odoo.exceptions import AccessError, UserError

REFUSED = (AccessError, UserError)


@pytest.fixture
def env(odoo_env):
    return odoo_env


@pytest.fixture
def clerk(env):
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "W6 Loyalty Clerk",
                "login": "w6.clerk@a03.test",
                "group_ids": [(6, 0, [env.ref("base.group_user").id])],
            }
        )
    )


@pytest.fixture
def program(env):
    return env["fix.loyalty.program"].create({"name": "W6 Privilege", "code": "W6PRIV"})


def _hook(env, user, program, campaign_state="running", **vals):
    campaign = env["fix.campaign"].create({"name": "W6 Winter Care"})
    if campaign_state != "draft":
        campaign.write({"state": campaign_state})  # stands in for the DOFA-gated launch
    return (
        env["fix.loyalty.campaign.hook"]
        .with_user(user)
        .create({"name": "W6 hook", "campaign_id": campaign.id, "program_id": program.id, **vals})
    )


def test_state_cannot_be_typed(env, clerk, program):
    hook = _hook(env, clerk, program)
    with pytest.raises(REFUSED), env.cr.savepoint():
        hook.write({"state": "active"})
    with pytest.raises(REFUSED), env.cr.savepoint():
        _hook(env, clerk, program, state="active")
    assert hook.state == "draft"


def test_activation_needs_a_running_campaign_and_a_real_reward(env, clerk, program):
    for state in ("draft", "paused", "completed"):
        hook = _hook(env, clerk, program, campaign_state=state)
        with pytest.raises(UserError, match="not running"), env.cr.savepoint():
            hook.action_activate()
        assert hook.state == "draft"
    zero = _hook(env, clerk, program, bonus_points=0)
    with pytest.raises(UserError, match="positive bonus"), env.cr.savepoint():
        zero.action_activate()
    free = _hook(env, clerk, program, reward_type="voucher", voucher_discount_value=0.0)
    with pytest.raises(UserError, match="positive discount"), env.cr.savepoint():
        free.action_activate()


def test_lifecycle_and_frozen_terms(env, clerk, program):
    hook = _hook(env, clerk, program, bonus_points=150)
    hook.write({"bonus_points": 200})  # a draft is still editable
    hook.action_activate()
    assert hook.state == "active"
    assert {"bonus_points", "reward_type", "campaign_id"} <= hook._fix_form_locked_fields()
    with pytest.raises(UserError, match="reward terms are fixed"), env.cr.savepoint():
        hook.write({"bonus_points": 50000})
    hook.write({"name": "W6 hook renamed"})  # non-term fields stay editable
    with pytest.raises(UserError, match="Only a draft"), env.cr.savepoint():
        hook.action_activate()
    hook.action_complete()
    assert hook.state == "completed" and hook.bonus_points == 200
    with pytest.raises(UserError, match="Only an active"), env.cr.savepoint():
        hook.action_complete()
    with pytest.raises(UserError, match="Only active"), env.cr.savepoint():
        hook.action_execute_campaign_rewards(env["res.partner"].create({"name": "W6 late"}))


def test_the_workspace_offers_the_transitions_not_the_state():
    surface = m10_api.SURFACES["fix.loyalty.campaign.hook"]
    assert surface["actions"] == {"action_activate", "action_complete"}
    assert "state" not in writable.WRITABLE.get("fix.loyalty.campaign.hook", set())
