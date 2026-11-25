# A09 ERP builder stream B2b — leave rules (M55-F15 year-boundary split,
# M55-F4 the unpaid leave type, M55-F21 the s.117 service-basis accrual).
import itertools
from datetime import date, timedelta

import pytest
from odoo import fields
from odoo.exceptions import UserError

LEAVE = "fix.leave.request"
_SEQ = itertools.count(1)


def _user(env, *groups):
    n = next(_SEQ)
    ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "B2b Leave User %d" % n,
                "login": "a09-b2b-leave-%d@test.local" % n,
                "group_ids": [(6, 0, ids)],
            }
        )
    )


@pytest.fixture
def x(odoo_env):
    env = odoo_env
    emp_u, mgr_u = (_user(env) for _ in range(2))
    e_mgr = env["hr.employee"].create({"name": "B2b Leave Manager", "user_id": mgr_u.id})
    e_emp = env["hr.employee"].create(
        {"name": "B2b Leave Employee", "user_id": emp_u.id, "parent_id": e_mgr.id}
    )
    lt = {t.code: t for t in env["fix.leave.type"].search([("company_id", "=", env.company.id)])}
    return type(
        "X",
        (),
        {
            "env": env,
            "emp_u": emp_u,
            "mgr_u": mgr_u,
            "e_emp": e_emp,
            "lt": lt,
            "today": fields.Date.today(),
        },
    )()


def _draft(x, code, d_from, d_to, **kw):
    return x.env[LEAVE].create(
        {
            "employee_id": x.e_emp.id,
            "leave_type_id": x.lt[code].id,
            "date_from": d_from,
            "date_to": d_to,
            **kw,
        }
    )


def _approved(x, code, d_from, d_to, **kw):
    lv = _draft(x, code, d_from, d_to, **kw)
    lv.action_submit()
    lv.with_user(x.mgr_u).action_inbox_approve()
    assert lv.state == "approved"
    return lv


# ---- M55-F15: a spanning leave charges each day to its own calendar year ------


def test_spanning_leave_charges_each_day_to_its_own_year(x):
    # paternity is not statutory (no floor), so the entitlement can be set
    # freely for the arithmetic
    x.lt["paternity"].write({"entitlement_days": 6})
    spanning = _approved(x, "paternity", date(2026, 12, 27), date(2027, 1, 3))
    assert spanning.days == 8
    assert spanning._fix_days_in_year(2026) == 5, "Dec 27-31 charged to 2026"
    assert spanning._fix_days_in_year(2027) == 3, "Jan 1-3 charged to 2027"
    probe = _draft(x, "paternity", date(2027, 2, 1), date(2027, 2, 2))
    assert probe._fix_year_taken("paternity", 2026) == 5
    assert probe._fix_year_taken("paternity", 2027) == 3


def test_a_spanning_leave_within_a_small_entitlement_is_not_charged_whole(x):
    # 8 days over the boundary, 5 + 3: both halves fit a 6-day entitlement,
    # so the spanning request passes where charging it whole to 2026 refused
    x.lt["paternity"].write({"entitlement_days": 6})
    spanning = _approved(x, "paternity", date(2026, 12, 27), date(2027, 1, 3))
    assert spanning.state == "approved"
    # 3 already charged to 2027: 4 more days there would be 7 > 6
    with pytest.raises(UserError, match="in 2027"), x.env.cr.savepoint():
        _approved(x, "paternity", date(2027, 3, 1), date(2027, 3, 4))


def test_holiday_inside_casual_leave_is_charged(x):
    # BLR 2015 r.106 once the type stops excluding holidays: a registered
    # festival day inside the span is a charged day
    x.lt["casual"].write({"excludes_holidays": False})
    x.env["fix.hr.holiday"].create(
        {
            "name": "B2b Test Festival",
            "company_id": x.env.company.id,
            "date": date(2027, 1, 5),  # a Tuesday
            "holiday_type": "festival",
        }
    )
    lv = _draft(x, "casual", date(2027, 1, 4), date(2027, 1, 6))
    assert lv._fix_days_in_year(2027) == 3, "the festival day inside is charged (r.106)"
    assert lv.days == 3  # cd_attendance computes with the same exclusion flag


# ---- M55-F4: the unpaid leave type ---------------------------------------------


def test_unpaid_type_is_seeded_and_marked(x):
    unpaid = x.lt.get("unpaid") or x.env.ref("cd_hr_core.leave_type_unpaid")
    assert unpaid._fix_is_unpaid()
    assert not unpaid.excludes_holidays, "holidays inside unpaid leave are charged"
    assert not unpaid.is_statutory


def test_unpaid_leave_has_no_per_year_cap_and_is_tracked_for_payroll(x):
    # no statutory entitlement figure exists: 20 days pass where a 10-day cap
    # would have refused, and the payroll helper counts exactly the days
    lv = _approved(x, "unpaid", date(2027, 2, 1), date(2027, 2, 20))
    assert (lv.state, lv.days) == ("approved", 20)
    Request = x.env[LEAVE]
    assert Request._fix_unpaid_days_between(x.e_emp, date(2027, 2, 1), date(2027, 2, 28)) == 20
    # clipped to the range asked for
    assert Request._fix_unpaid_days_between(x.e_emp, date(2027, 2, 10), date(2027, 2, 28)) == 11
    assert Request._fix_unpaid_days_between(x.e_emp, date(2027, 3, 1), date(2027, 3, 31)) == 0


def test_paid_leave_days_are_not_counted_as_unpaid(x):
    _approved(x, "casual", date(2027, 4, 1), date(2027, 4, 3))
    assert x.env[LEAVE]._fix_unpaid_days_between(x.e_emp, date(2027, 4, 1), date(2027, 4, 30)) == 0


# ---- M55-F21: the s.117 'service' basis counts only days of work performed -----


@pytest.fixture
def cal(x):
    """A Sun-Thu calendar (the estate's weekend is Friday-Saturday)."""
    calendar = x.env["resource.calendar"].create(
        {
            "name": "B2b Sun-Thu 8h",
            "company_id": x.env.company.id,
            "attendance_ids": [
                (0, 0, {"name": d, "dayofweek": str(dw), "hour_from": 8.0, "hour_to": 16.0})
                for d, dw in (
                    ("Sunday", 6),
                    ("Monday", 0),
                    ("Tuesday", 1),
                    ("Wednesday", 2),
                    ("Thursday", 3),
                )
            ],
        }
    )
    return calendar


def test_service_basis_excludes_festival_holidays_and_leave_days(odoo_env, x, cal):
    env = x.env
    mgr_u, onleave_u = _user(env), _user(env)
    e_mgr2 = env["hr.employee"].create({"name": "B2b Accrual Manager", "user_id": mgr_u.id})
    worked = env["hr.employee"].create({"name": "B2b Worked", "resource_calendar_id": cal.id})
    onleave = env["hr.employee"].create(
        {
            "name": "B2b On Leave",
            "user_id": onleave_u.id,
            "parent_id": e_mgr2.id,
            "resource_calendar_id": cal.id,
        }
    )
    for emp in (worked, onleave):
        env["fix.employment.contract"].create(
            {
                "employee_id": emp.id,
                "company_id": env.company.id,
                "contract_type": "permanent",
                "joining_date": date(2024, 1, 1),
                "basic_monthly": 30000.0,
                "state": "active",
            }
        )
    # a paid leave for the second employee: 1-10 Feb 2027
    lv = env[LEAVE].create(
        {
            "employee_id": onleave.id,
            "leave_type_id": x.lt["casual"].id,
            "date_from": date(2027, 2, 1),
            "date_to": date(2027, 2, 10),
        }
    )
    lv.action_submit()
    lv.with_user(mgr_u).action_inbox_approve()
    assert lv.state == "approved"

    span = (date(2027, 1, 1), date(2027, 12, 31))
    base = worked._fix_leave_days_worked(*span)
    leave_days = (date(2027, 2, 10) - date(2027, 2, 1)).days + 1
    fri_sat = sum(
        1 for i in range(leave_days) if (date(2027, 2, 1) + timedelta(days=i)).weekday() in (4, 5)
    )
    assert base == 365 - 365 // 7, "the weekly-holiday part is unchanged (s.103)"
    assert onleave._fix_leave_days_worked(*span) == base - (
        leave_days - fri_sat
    ), "s.117: a day of leave is not a day of work performed"
    # a registered festival holiday is not a day of work performed either
    env["fix.hr.holiday"].create(
        {
            "name": "B2b Festival Wednesday",
            "company_id": env.company.id,
            "date": date(2027, 6, 9),  # a Wednesday on the Sun-Thu calendar
            "holiday_type": "festival",
        }
    )
    assert worked._fix_leave_days_worked(*span) == base - 1


def test_unpaid_leave_days_also_reduce_the_accrual(odoo_env, x, cal):
    env = x.env
    mgr_u = _user(env)
    e_mgr2 = env["hr.employee"].create({"name": "B2b Accrual Manager 2", "user_id": mgr_u.id})
    worker = env["hr.employee"].create({"name": "B2b Worker", "resource_calendar_id": cal.id})
    idle = env["hr.employee"].create(
        {
            "name": "B2b Idle",
            "user_id": _user(env).id,
            "parent_id": e_mgr2.id,
            "resource_calendar_id": cal.id,
        }
    )
    lv = env[LEAVE].create(
        {
            "employee_id": idle.id,
            "leave_type_id": x.env.ref("cd_hr_core.leave_type_unpaid").id,
            "date_from": date(2027, 5, 3),
            "date_to": date(2027, 5, 14),
        }
    )
    lv.action_submit()
    lv.with_user(mgr_u).action_inbox_approve()
    assert lv.state == "approved"
    span = (date(2027, 1, 1), date(2027, 12, 31))
    assert idle._fix_leave_days_worked(*span) < worker._fix_leave_days_worked(*span), (
        "s.117 (lead-verified): a day of leave, paid or UNPAID, is not a day of " "work performed"
    )
