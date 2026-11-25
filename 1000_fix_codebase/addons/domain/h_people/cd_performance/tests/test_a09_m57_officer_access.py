# M57-F14 (A09 ERP audit 2026-11-23): the HR Officer (spec R31: create, read,
# update, cycle administration) could create or change no M57 record - every
# set-up row sat on hr.group_hr_manager. The officer now sets the cycle, goals,
# reviews, PIPs and feedback up; the decisions stay on the deciding groups.
import itertools

import pytest
from odoo import fields
from odoo.exceptions import AccessError

_SEQ = itertools.count(1)


def _user(env, *groups):
    n = next(_SEQ)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A09 M57 Officer %d" % n,
                "login": "a09-m57-off-%d@a09.test" % n,
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
            }
        )
    )


def test_the_hr_officer_sets_up_the_cycle_and_decides_nothing(odoo_env):
    env = odoo_env
    officer = _user(env, "cd_hr_core.group_hr_officer")
    today = fields.Date.today()
    cycle = (
        env["fix.performance.review.cycle"]
        .with_user(officer)
        .create(
            {
                "name": "A09 Officer Cycle",
                "cycle_type": "annual",
                "period": str(today.year),
                "self_deadline": today,
                "manager_deadline": today,
                "calibration_deadline": today,
            }
        )
    )
    assert cycle.state == "draft" and cycle.create_uid == officer
    employee = env["hr.employee"].create({"name": "A09 M57 Officer Goal"})
    goal = (
        env["fix.performance.goal"]
        .with_user(officer)
        .create(
            {
                "name": "A09 Officer Goal",
                "employee_id": employee.id,
                "period": str(today.year),
            }
        )
    )
    # set-up is theirs; a decision is not (it stays on the workflow group)
    for model, record in (("fix.performance.review.cycle", cycle), ("fix.performance.goal", goal)):
        with pytest.raises(AccessError), env.cr.savepoint():
            record.with_user(officer).unlink()
        assert env[model].sudo().search_count([("id", "=", record.id)]) == 1
    # closing the cycle is the HR Manager's decision, not the officer's task
    with pytest.raises(AccessError), env.cr.savepoint():
        cycle.with_user(officer).action_close()
    # and a plain user can do neither
    plain = _user(env)
    with pytest.raises(AccessError), env.cr.savepoint():
        (
            env["fix.performance.review.cycle"]
            .with_user(plain)
            .create(
                {
                    "name": "A09 Plain Cycle",
                    "cycle_type": "annual",
                    "period": str(today.year),
                    "self_deadline": today,
                    "manager_deadline": today,
                    "calibration_deadline": today,
                }
            )
        )
