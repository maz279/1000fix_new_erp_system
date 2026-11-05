# A09 round 2, M55 leave (package r2e): BRU-WFM-04 team coverage on leave
# approval, and BLA s.118 festival holidays as calendar days, not leave.
#
# Every attack runs as a freshly created NON-admin user; the threshold and
# mode are company settings (0 = off) because no source states the figure.
import base64
import itertools
from datetime import date
from types import SimpleNamespace

import pytest
from odoo.exceptions import UserError
from odoo.service.model import call_kw

LEAVE = "fix.leave.request"
CERT = base64.b64encode(b"registered practitioner certificate")
_SEQ = itertools.count(1)


def _user(env, *groups):
    n = next(_SEQ)
    ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A09 R2E Leave User %d" % n,
                "login": "a09-r2e-leave-%d@test.local" % n,
                "group_ids": [(6, 0, ids)],
            }
        )
    )


@pytest.fixture
def t(odoo_env):
    env = odoo_env
    c = SimpleNamespace(env=env)
    c.mgr_u = _user(env)
    c.users = [_user(env) for _ in range(3)]
    E = env["hr.employee"]
    c.dept = env["hr.department"].create({"name": "R2E Field Team"})
    c.e_mgr = E.create({"name": "R2E Team Lead", "user_id": c.mgr_u.id})
    c.team = [
        E.create(
            {
                "name": "R2E Tech %d" % i,
                "user_id": u.id,
                "parent_id": c.e_mgr.id,
                "department_id": c.dept.id,
                "sex": "male",
            }
        )
        for i, u in enumerate(c.users)
    ]
    c.lt = {
        lt.code: lt
        for lt in env["fix.leave.type"].search(
            [("company_id", "=", env.company.id), ("code", "in", ("casual", "sick", "festival"))]
        )
    }
    return c


def leave(c, i, code, d_from, d_to, **kw):
    lv = (
        c.env[LEAVE]
        .with_user(c.users[i])
        .create(
            {
                "employee_id": c.team[i].id,
                "leave_type_id": c.lt[code].id,
                "date_from": d_from,
                "date_to": d_to,
                **kw,
            }
        )
    )
    lv.action_submit()
    return lv


def approve(c, lv):
    lv.with_user(c.mgr_u).action_inbox_approve()
    return lv


D1, D2 = date(2031, 6, 10), date(2031, 6, 11)


def test_coverage_check_is_off_at_zero(t):
    approve(t, leave(t, 0, "casual", D1, D1))
    second = approve(t, leave(t, 1, "casual", D1, D1))
    assert second.state == "approved" and not second.coverage_flag


def test_coverage_flag_mode_records_the_shortfall_and_lets_the_approver_decide(t):
    t.env.company.fix_leave_coverage_max_pct = 50.0
    first = approve(t, leave(t, 0, "casual", D1, D1))
    assert first.state == "approved" and not first.coverage_flag  # 1 of 3 away
    second = leave(t, 1, "casual", D1, D2)
    assert second.coverage_flag and "2 of 3" in second.coverage_note  # seen at submission
    approve(t, second)
    assert second.state == "approved" and second.coverage_flag
    # the flag is the workflow's, never typed
    env = t.env(user=t.users[1].id, context={"tracking_disable": True})
    with pytest.raises(UserError, match="changes only through its workflow"):
        call_kw(env[LEAVE], "write", [[second.id], {"coverage_flag": False}], {})


def test_coverage_block_mode_refuses_the_approval_but_not_certified_sick_leave(t):
    t.env.company.write({"fix_leave_coverage_max_pct": 50.0, "fix_leave_coverage_mode": "block"})
    approve(t, leave(t, 0, "casual", D1, D1))
    casual = leave(t, 1, "casual", D1, D1)
    with pytest.raises(UserError, match="BRU-WFM-04"), t.env.cr.savepoint():
        approve(t, casual)
    assert casual.state == "submitted"
    # a statutory sick leave on a certificate is a right: flagged, never refused
    sick = leave(t, 2, "sick", D1, D1, medical_certificate=CERT, medical_certificate_name="c.pdf")
    approve(t, sick)
    assert sick.state == "approved" and sick.coverage_flag
    # another day has cover: approved
    assert approve(t, leave(t, 1, "casual", D2, D2)).state == "approved"


def test_festival_holidays_are_not_requested_as_leave(t):
    assert "festival" in t.lt  # the statutory catalogue still carries the type
    lv = (
        t.env[LEAVE]
        .with_user(t.users[0])
        .create(
            {
                "employee_id": t.team[0].id,
                "leave_type_id": t.lt["festival"].id,
                "date_from": D1,
                "date_to": D1,
            }
        )
    )
    with pytest.raises(UserError, match="holiday calendar"):
        lv.action_submit()
