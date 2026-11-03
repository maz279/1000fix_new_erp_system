"""A03 audit W7: a template's consent class is a supervisor's decision.

A "transactional" template is sent on the contract basis, without the
marketing-consent and DND checks, and any agent could create one or turn a
marketing template transactional with one field. Tested as NON-ADMIN users,
both ways.
"""

import pytest
from odoo.exceptions import UserError

SUPERVISOR = "cd_contact_centre.group_cc_supervisor"


@pytest.fixture
def env(odoo_env):
    return odoo_env


@pytest.fixture
def make_user(env):
    seq = iter(range(1, 100))

    def _make(*xmlids):
        n = next(seq)
        groups = [env.ref("base.group_user").id] + [env.ref(x).id for x in xmlids]
        return (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "W7 user %d" % n,
                    "login": "w7.user.%d@a03.test" % n,
                    "group_ids": [(6, 0, groups)],
                }
            )
        )

    return _make


def _template(env, user, **vals):
    vals.setdefault("name", "W7 template")
    vals.setdefault("body", "Your device is ready, {{name}}.")
    return env["fix.cc.notif.template"].with_user(user).create(vals)


def test_an_agent_cannot_make_a_template_transactional(env, make_user):
    agent = make_user()
    with pytest.raises(UserError, match="Supervisor"), env.cr.savepoint():
        _template(env, agent, consent_class="transactional")
    tpl = _template(env, agent)
    assert (
        tpl.consent_class == "marketing"
    ), "an agent's template defaults to the consent-checked class"
    with pytest.raises(UserError, match="Supervisor"), env.cr.savepoint():
        tpl.with_user(agent).write({"consent_class": "transactional"})
    assert tpl.consent_class == "marketing"
    tpl.with_user(agent).write({"body": "Eid offer for {{name}}"})  # marketing stays editable


def test_an_agent_cannot_rewrite_a_transactional_template(env, make_user):
    agent, supervisor = make_user(), make_user(SUPERVISOR)
    tpl = _template(env, supervisor)
    assert tpl.consent_class == "transactional"
    assert {"body", "body_bn", "subject"} <= tpl.with_user(agent)._fix_form_locked_fields()
    assert not tpl.with_user(supervisor)._fix_form_locked_fields()
    with pytest.raises(UserError, match="transactional"), env.cr.savepoint():
        tpl.with_user(agent).write({"body": "50% off everything, {{name}}!"})
    assert tpl.body == "Your device is ready, {{name}}."
    tpl.with_user(agent).write({"name": "W7 renamed"})  # metadata stays open
    tpl.with_user(supervisor).write({"body": "Your device is ready for pickup, {{name}}."})
    # Down-classifying only adds checks, so anyone may do it, with the edit.
    tpl.with_user(agent).write({"consent_class": "marketing", "body": "Eid offer for {{name}}"})
    assert tpl.consent_class == "marketing"
