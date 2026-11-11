# A09 · M21 - the headcount and org-distribution packs label their branch
# column with operating-unit names (2026-11-10 screens sweep).
#
# The caller may read only their own operating units (record rule "Allowed
# operating units") while the employees they are entitled to count sit in
# branch units. Reading `emp.operating_unit_id.name` as the caller raised an
# AccessError that took the whole aggregate down - intermittently, because a
# warm cache serves the name without the access check. The label is read
# sudo (name only); which employees are counted stays the caller's own search.
from __future__ import annotations

import uuid

import pytest
from odoo.addons.cd_p03_portal.controllers.a09 import m21
from odoo.exceptions import AccessError

TAG = uuid.uuid4().hex[:6]


@pytest.fixture()
def world(odoo_env):
    env = odoo_env
    if "operating.unit" not in env or "hr.employee" not in env:
        pytest.skip("operating_unit / hr not installed")
    company = env.company
    unit = env["operating.unit"].create(
        {
            "name": "M21 Label Branch %s" % TAG,
            "code": "ML%s" % TAG,
            "company_id": company.id,
            "partner_id": company.partner_id.id,
        }
    )
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "M21 label reader %s" % TAG,
                "login": "m21_label_%s@example.test" % TAG,
                "group_ids": [(6, 0, [env.ref("base.group_user").id])],
            }
        )
    )
    # the creator of a unit is added to it by the OU module: take it away again
    user.sudo().write({"operating_unit_ids": [(3, unit.id)]})
    env.flush_all()
    env.invalidate_all()
    return env, unit, user


def test_the_label_is_served_for_a_unit_the_caller_may_not_read(world):
    env, unit, user = world
    as_caller = unit.with_user(user)
    assert unit not in user.operating_unit_ids
    env.invalidate_all()  # a warm cache hides the access check (the intermittency)
    try:
        _ = as_caller.name  # the read IS the probe
    except AccessError:
        pass
    else:
        pytest.skip("this build lets every internal user read every operating unit")
    env.invalidate_all()
    assert m21._unit_name(as_caller) == "M21 Label Branch %s" % TAG
    assert m21._unit_name(env["operating.unit"].with_user(user)) == "Unassigned"


def test_the_packs_no_longer_read_the_unit_name_as_the_caller():
    """The two packs (and the transfer count) go through the one helper."""
    import inspect

    for pack in (m21.headcount_movement, m21.org_distribution, m21.attrition_analysis):
        source = inspect.getsource(pack)
        assert "operating_unit_id.name" not in source, pack.__name__
    assert "_unit_name(" in inspect.getsource(m21.headcount_movement)
    assert "_unit_name(" in inspect.getsource(m21.org_distribution)


def test_org_distribution_runs_for_a_caller_outside_the_branch(world):
    """End to end: an HR reader who is not a member of the branch unit gets
    the pack, with the branch named, instead of an AccessError."""
    env, unit, user = world
    hr_group = env.ref("hr.group_hr_user", raise_if_not_found=False)
    if not hr_group:
        pytest.skip("hr.group_hr_user missing")
    user.sudo().write({"group_ids": [(4, hr_group.id)]})
    employee = env["hr.employee"].create(
        {"name": "M21 Label Emp %s" % TAG, "operating_unit_id": unit.id}
    )
    env.flush_all()
    env.invalidate_all()
    caller_env = env(user=user)
    visible = caller_env["hr.employee"].search([("id", "=", employee.id)])
    pack = m21.org_distribution(caller_env)
    moved = m21.headcount_movement(caller_env)
    assert pack["cols"] == ["branch", "position", "headcount"] and moved["rows"] is not None
    if visible:
        # the caller counts this employee: the branch it sits in must be named
        assert any(r["branch"] == unit.name for r in pack["rows"]), pack["rows"][:5]
        assert any(r["branch"] == unit.name for r in moved["rows"]), moved["rows"][:5]
    else:
        # the caller's own rules hide the employee: the label fix widened nothing
        assert all(r["branch"] != unit.name for r in pack["rows"])
