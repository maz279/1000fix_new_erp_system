# M57-F15 (A09 ERP audit 2026-11-23): payroll and HR generalists read every
# rating, review, PIP and 360 feedback ("who said what"). Spec §13 / R41: the
# Payroll Officer sees the incentive money; ratings are S2. HR and the M57
# deciders still read everything; payroll reads the money records only.
import itertools

from odoo import fields

_SEQ = itertools.count(1)


def _user(env, *groups):
    n = next(_SEQ)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A09 M57 Privacy %d" % n,
                "login": "a09-m57-priv-%d@a09.test" % n,
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
            }
        )
    )


def test_payroll_reads_the_money_but_not_the_ratings(odoo_env):
    env = odoo_env
    payroll = _user(env, "cd_payroll_bd.group_payroll_officer")
    hr = _user(env, "cd_hr_core.group_hr_officer")
    employee = env["hr.employee"].create({"name": "A09 M57 Privacy Subject"})
    period = str(fields.Date.today().year)
    review = (
        env["fix.performance.review"]
        .sudo()
        .create(
            {
                "employee_id": employee.id,
                "period": period,
                "self_rating": 4.0,
                "manager_rating": 3.0,
            }
        )
    )
    # the helper is the contract the rules read
    assert payroll.fix_reads_all_performance() is False
    assert payroll.fix_reads_all_payroll_money() is True
    assert hr.fix_reads_all_performance() is True
    # behaviourally: the review is invisible to payroll, visible to HR
    assert review not in env["fix.performance.review"].with_user(payroll).search([])
    assert review in env["fix.performance.review"].with_user(hr).search([])
    # the employee still reads their own review
    employee.user_id = _user(env, "base.group_user").id
    assert review in env["fix.performance.review"].with_user(employee.user_id).search([])
