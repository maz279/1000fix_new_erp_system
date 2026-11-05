# A09 acceptance suite for M55 leave (workflow audit M55-1, M55-7, B1-B6, C5,
# P2 leave; working/A09_evidence/module_findings/M55.md).
#
# Every attack runs as a freshly created NON-admin user and is refused; the
# proper path is then run by the right role. Writes go through call_kw with
# the client-controlled `tracking_disable` key, and the workspace through the
# real /p03 controller with `request` patched, as the P0 suites do.
#
# Replaces the leave tests of test_hr_core_orm.py / test_hr_core.py that
# asserted the defects (a DRAFT approved directly, reversed dates = 0 days, a
# second 'casual' type) or read the source.
import base64
import itertools
import json
from datetime import date, timedelta
from types import SimpleNamespace
from unittest import mock

import pytest
from dateutil.relativedelta import relativedelta
from odoo import fields
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.service.model import call_kw

LEAVE = "fix.leave.request"
_SEQ = itertools.count(1)
CERT = base64.b64encode(b"registered practitioner certificate")


def _user(env, *groups):
    n = next(_SEQ)
    ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A09 M55 Leave User %d" % n,
                "login": "a09-m55-leave-%d@test.local" % n,
                "group_ids": [(6, 0, ids)],
            }
        )
    )


def _contract(env, emp, joined):
    return env["fix.employment.contract"].create(
        {
            "employee_id": emp.id,
            "company_id": env.company.id,
            "contract_type": "permanent",
            "joining_date": joined,
            "basic_monthly": 30000.0,
            "state": "active",
        }
    )


@pytest.fixture
def x(odoo_env):
    env = odoo_env
    c = SimpleNamespace(env=env)
    c.emp_u, c.col_u, c.mgr_u, c.mgr2_u, c.fem_u = (_user(env) for _ in range(5))
    c.hro_u = _user(env, "cd_hr_core.group_hr_officer")
    E = env["hr.employee"]
    c.e_mgr = E.create({"name": "Leave Manager", "user_id": c.mgr_u.id})
    c.e_mgr2 = E.create({"name": "Other Manager", "user_id": c.mgr2_u.id})
    c.e_emp = E.create(
        {"name": "Leave Employee", "user_id": c.emp_u.id, "parent_id": c.e_mgr.id, "sex": "male"}
    )
    c.e_col = E.create({"name": "Leave Colleague", "user_id": c.col_u.id, "parent_id": c.e_mgr.id})
    c.e_fem = E.create(
        {"name": "Leave Mother", "user_id": c.fem_u.id, "parent_id": c.e_mgr.id, "sex": "female"}
    )
    c.today = fields.Date.today()
    _contract(env, c.e_emp, c.today - relativedelta(years=2, days=10))
    _contract(env, c.e_fem, c.today - relativedelta(years=1))
    c.lt = {
        t.code: t
        for t in env["fix.leave.type"].search(
            [
                ("company_id", "=", env.company.id),
                ("code", "in", ("casual", "sick", "annual", "maternity")),
            ]
        )
    }
    return c


def rpc(c, user, model, method, ids, *args):
    env = c.env(user=user.id, context={"tracking_disable": True})
    return call_kw(env[model], method, [ids, *args], {})


def draft(c, user, code, d_from, d_to, emp=None, **kw):
    return (
        c.env[LEAVE]
        .with_user(user)
        .create(
            {
                "employee_id": (emp or c.e_emp).id,
                "leave_type_id": c.lt[code].id,
                "date_from": d_from,
                "date_to": d_to,
                **kw,
            }
        )
    )


def submitted(c, code, d_from, d_to, user=None, emp=None, **kw):
    lv = draft(c, user or c.emp_u, code, d_from, d_to, emp=emp, **kw)
    lv.action_submit()
    return lv


def approved(c, code, d_from, d_to, **kw):
    lv = submitted(c, code, d_from, d_to, **kw)
    lv.with_user(c.mgr_u).action_inbox_approve()
    assert lv.state == "approved"
    return lv


def assignees(c, lv):
    return (
        c.env["fix.workflow.task"]
        .sudo()
        .search([("res_model", "=", LEAVE), ("res_id", "=", lv.id), ("state", "=", "pending")])
        .mapped("assigned_user_id")
    )


@pytest.fixture
def p03(x):
    patchers = []

    def as_user(user):
        p = mock.patch.object(api, "request", SimpleNamespace(env=x.env(user=user.id)))
        p.start()
        patchers.append(p)
        ctl = api.P03GenericApiController()
        return SimpleNamespace(
            write=lambda **kw: ctl.model_write(**kw), action=lambda **kw: ctl.model_action(**kw)
        )

    yield as_user
    for p in patchers:
        p.stop()


def jan(day, year=2027):
    return date(year, 1, day)


# ======================================================================= routing (M55-1, B3, B4)
def test_requester_cannot_approve_own_leave_any_way(x, p03):
    lv = submitted(x, "casual", jan(4), jan(6))
    with pytest.raises(UserError, match="changes only through its workflow"):
        rpc(x, x.emp_u, LEAVE, "write", [lv.id], {"state": "approved"})
    with (
        pytest.raises(UserError, match="approved from the approver's inbox"),
        x.env.cr.savepoint(),
    ):
        lv.with_user(x.emp_u).action_approve()
    with pytest.raises(UserError, match="not awaiting your decision"), x.env.cr.savepoint():
        lv.with_user(x.emp_u).action_inbox_approve()
    assert not p03(x.emp_u).action(model=LEAVE, ids=[lv.id], method="action_approve")["success"]
    assert not p03(x.emp_u).action(model=LEAVE, ids=[lv.id], method="action_inbox_approve")[
        "success"
    ]
    p03(x.emp_u).write(model=LEAVE, record_id=lv.id, values={"state": "approved"})
    lv.invalidate_recordset()
    assert lv.state == "submitted"


def test_born_submitted_or_approved_is_refused(x):
    for state in ("submitted", "approved"):
        with pytest.raises(UserError, match="changes only through its workflow"):
            draft(x, x.emp_u, "casual", jan(4), jan(6), state=state)


def test_routed_to_the_line_manager_only(x):
    lv = submitted(x, "casual", jan(4), jan(6))
    assert assignees(x, lv) == x.mgr_u
    for user in (x.col_u, x.mgr2_u, x.hro_u):
        with pytest.raises(UserError, match="not awaiting your decision"), x.env.cr.savepoint():
            lv.with_user(user).action_inbox_approve()
    lv.with_user(x.mgr_u).action_inbox_approve()
    assert (lv.state, lv.decided_by_id, lv.approved_days) == ("approved", x.mgr_u, 3)
    events = x.env["fix.event.outbox"].search(
        [("event_type", "=", "leave.approved"), ("aggregate_id", "=", lv.id)]
    )
    assert [json.loads(e.payload) for e in events] == [{"employee": "Leave Employee", "days": 3}]


def test_hr_decides_when_there_is_no_line_manager(x):
    x.e_col.parent_id = False
    lv = submitted(x, "casual", jan(4), jan(6), user=x.col_u, emp=x.e_col)
    who = assignees(x, lv)
    assert x.hro_u in who and x.col_u not in who and x.mgr_u not in who
    lv.with_user(x.hro_u).action_inbox_approve()
    assert lv.state == "approved"


def test_a_colleague_cannot_read_or_raise_my_leave(x):
    lv = draft(x, x.emp_u, "casual", jan(4), jan(6))
    assert not x.env[LEAVE].with_user(x.col_u).search([("id", "=", lv.id)])
    with pytest.raises(AccessError), x.env.cr.savepoint():
        draft(x, x.col_u, "casual", jan(11), jan(12), emp=x.e_emp)
    assert x.env[LEAVE].with_user(x.mgr_u).search([("id", "=", lv.id)])  # his report


def test_draft_is_never_approved_directly(x):
    lv = draft(x, x.emp_u, "casual", jan(4), jan(4))
    with pytest.raises(UserError, match="Only a submitted"), x.env.cr.savepoint():
        lv.sudo().action_approve()  # even the superuser applies only to a submitted request


# ======================================================================= reject / cancel (F15)
def test_reject_records_the_reason(x, p03):
    lv = submitted(x, "casual", jan(4), jan(6))
    with pytest.raises(UserError, match="State why"), x.env.cr.savepoint():
        lv.with_user(x.mgr_u).action_reject()
    res = p03(x.mgr_u).action(
        model=LEAVE, ids=[lv.id], method="action_reject", kwargs={"reason": "audit week"}
    )
    assert res["success"], res
    lv.invalidate_recordset()
    assert (lv.state, lv.rejection_reason, lv.decided_by_id) == ("rejected", "audit week", x.mgr_u)


def test_cancel_withdraws_and_restores_the_balance(x):
    pending = submitted(x, "casual", jan(4), jan(6))
    pending.with_user(x.emp_u).action_cancel()
    assert (pending.state, pending.approval_state) == ("cancelled", "none")
    assert pending.approval_request_id.state == "recalled"
    ten = approved(x, "casual", jan(11), jan(20))
    with pytest.raises(UserError, match="Entitlement exhausted"), x.env.cr.savepoint():
        submitted(x, "casual", date(2027, 2, 1), date(2027, 2, 1))
    with pytest.raises(UserError, match="Say why"), x.env.cr.savepoint():
        ten.with_user(x.emp_u).action_cancel()
    with pytest.raises(UserError), x.env.cr.savepoint():  # not his: he cannot even read it
        ten.with_user(x.col_u).action_cancel(reason="x")
    with pytest.raises(UserError, match="requester or HR"), x.env.cr.savepoint():
        ten.with_user(x.mgr_u).action_cancel(reason="x")
    ten.with_user(x.emp_u).action_cancel(reason="trip cancelled")
    assert ten.state == "cancelled"
    assert submitted(x, "casual", date(2027, 2, 1), date(2027, 2, 10)).state == "submitted"


def test_approved_and_submitted_terms_are_frozen(x):
    lv = approved(x, "casual", jan(4), jan(5))
    with pytest.raises(UserError, match="cannot change"):
        rpc(x, x.emp_u, LEAVE, "write", [lv.id], {"date_to": date(2027, 2, 12)})
    assert (lv.days, lv.approved_date_to) == (2, jan(5))
    sub = submitted(x, "casual", jan(18), jan(18))
    with pytest.raises(UserError, match="awaiting approval"):
        rpc(x, x.emp_u, LEAVE, "write", [sub.id], {"date_to": jan(28)})
    for field, value in (("approved_days", 40), ("decided_by_id", x.emp_u.id)):
        with pytest.raises(UserError, match="changes only through its workflow"):
            rpc(x, x.emp_u, LEAVE, "write", [lv.id], {field: value})


# ======================================================================= rules (M55-7)
def test_reversed_dates_and_overlaps_are_refused(x):
    with pytest.raises(ValidationError, match="cannot end"), x.env.cr.savepoint():
        draft(x, x.emp_u, "casual", date(2027, 7, 31), date(2027, 7, 1))
    approved(x, "casual", date(2027, 6, 1), date(2027, 6, 3))
    with pytest.raises(UserError, match="already has"), x.env.cr.savepoint():
        submitted(x, "sick", date(2027, 6, 2), date(2027, 6, 4), medical_certificate=CERT)


def test_one_leave_type_per_code(x):
    with pytest.raises(ValidationError, match="already exists"), x.env.cr.savepoint():
        x.env["fix.leave.type"].with_user(x.hro_u).create(
            {"code": "casual", "name": "Casual Leave (dup)", "entitlement_days": 10}
        )


def test_entitlement_is_per_code_per_calendar_year_and_rechecked_at_approval(x):
    a = submitted(x, "casual", jan(4), jan(9))  # 6 days
    b = submitted(x, "casual", jan(18), jan(23))  # 6 more: 12 > 10 once a is approved
    a.with_user(x.mgr_u).action_inbox_approve()
    with (
        pytest.raises(UserError, match=r"6 approved \+ 6 requested > 10 days in 2027"),
        x.env.cr.savepoint(),
    ):
        b.with_user(x.mgr_u).action_inbox_approve()
    b.invalidate_recordset()
    assert b.state == "submitted"
    # a new calendar year restores it (s.115: 10 days IN A CALENDAR YEAR)
    nxt = approved(x, "casual", date(2028, 1, 3), date(2028, 1, 12))
    assert nxt.days == 10


def test_the_statutory_floor_is_rechecked(x):
    x.lt["sick"].with_user(x.hro_u).write({"entitlement_days": 7})
    with pytest.raises(ValidationError, match="statutory floor"), x.env.cr.savepoint():
        submitted(x, "sick", jan(4), jan(5), medical_certificate=CERT)


def test_sick_leave_needs_a_certificate(x):
    with pytest.raises(UserError, match="certificate"), x.env.cr.savepoint():
        submitted(x, "sick", jan(4), jan(17))
    lv = submitted(x, "sick", jan(4), jan(17), medical_certificate=CERT)
    assert lv.state == "submitted"


def test_maternity_eligibility(x):
    conf = x.today + timedelta(days=90)
    start, end = conf - timedelta(days=56), conf + timedelta(days=55)
    with pytest.raises(UserError, match="for a woman"), x.env.cr.savepoint():
        submitted(x, "maternity", start, end, expected_confinement_date=conf)
    with pytest.raises(UserError, match="confinement date"), x.env.cr.savepoint():
        submitted(x, "maternity", start, end, user=x.fem_u, emp=x.e_fem)
    early = start - timedelta(days=14)
    with pytest.raises(UserError, match="days before"), x.env.cr.savepoint():
        submitted(
            x, "maternity", early, end, user=x.fem_u, emp=x.e_fem, expected_confinement_date=conf
        )
    x.e_fem.children = 2
    with pytest.raises(UserError, match="two or more surviving children"), x.env.cr.savepoint():
        submitted(
            x, "maternity", start, end, user=x.fem_u, emp=x.e_fem, expected_confinement_date=conf
        )
    x.e_fem.children = 1
    lv = submitted(
        x, "maternity", start, end, user=x.fem_u, emp=x.e_fem, expected_confinement_date=conf
    )
    lv.with_user(x.mgr_u).action_inbox_approve()
    assert (lv.state, lv.days) == ("approved", 112)


def test_maternity_needs_six_months_service(x):
    new = x.env["hr.employee"].create(
        {"name": "Leave New Joiner", "sex": "female", "parent_id": x.e_mgr.id}
    )
    _contract(x.env, new, x.today - timedelta(days=10))
    conf = x.today + timedelta(days=56)
    with pytest.raises(UserError, match=r"6 months' service"), x.env.cr.savepoint():
        submitted(
            x,
            "maternity",
            x.today + timedelta(days=1),
            conf + timedelta(days=55),
            user=x.mgr_u,
            emp=new,
            expected_confinement_date=conf,
        )


# ======================================================================= annual leave, I2 (s.117)
def test_annual_leave_accrues_one_day_per_eighteen_worked(x):
    # two completed service years, 'service' basis: 365 - 52 weekly holidays
    # = 313 days worked a year -> 313 // 18 = 17 days a year
    assert x.e_emp._fix_unused_annual_leave_days() == 34.0
    new = x.env["hr.employee"].create({"name": "Leave Joiner", "parent_id": x.e_mgr.id})
    _contract(x.env, new, x.today - timedelta(days=30))
    assert new._fix_unused_annual_leave_days() == 0.0  # nothing before a year's service
    d0 = x.today + timedelta(days=7)
    with pytest.raises(UserError, match="Annual leave balance exhausted"), x.env.cr.savepoint():
        submitted(x, "annual", d0, d0 + timedelta(days=19), user=x.mgr_u, emp=new)
    lv = approved(x, "annual", d0, d0 + timedelta(days=9))
    assert lv.days == 10
    assert x.e_emp._fix_unused_annual_leave_days(as_of=d0 + timedelta(days=1)) == 24.0
    # the remaining balance is rechecked against approved FUTURE leave too
    later = d0 + timedelta(days=30)
    with pytest.raises(UserError, match="Annual leave balance exhausted"), x.env.cr.savepoint():
        submitted(x, "annual", later, later + timedelta(days=24))


def test_annual_leave_carry_forward_cap_and_refused_leave(x):
    vet = x.env["hr.employee"].create({"name": "Leave Veteran", "parent_id": x.e_mgr.id})
    _contract(x.env, vet, x.today - relativedelta(years=5, days=10))
    assert vet._fix_unused_annual_leave_days() == 40.0  # 5 x 17 = 85, capped at 40
    # s.117(7): leave applied for and refused is added beyond the cap
    refused_on = x.today - timedelta(days=400)
    x.env[LEAVE].create(
        {
            "employee_id": vet.id,
            "leave_type_id": x.lt["annual"].id,
            "date_from": refused_on,
            "date_to": refused_on + timedelta(days=9),
            "state": "rejected",
        }
    )
    assert vet._fix_unused_annual_leave_days() == 50.0


def test_accrual_cron_writes_the_register_idempotently(x):
    Accrual = x.env["fix.leave.accrual"]
    Accrual.cron_accrue_annual_leave()
    rows = Accrual.search([("employee_id", "=", x.e_emp.id)])
    assert len(rows) == 2 and set(rows.mapped("days_earned")) == {17}
    Accrual.cron_accrue_annual_leave()
    assert Accrual.search_count([("employee_id", "=", x.e_emp.id)]) == 2
    with pytest.raises(UserError, match="accrual run only"), x.env.cr.savepoint():
        rpc(x, x.hro_u, "fix.leave.accrual", "write", rows.ids, {"days_earned": 99})
    mine = x.env["fix.leave.accrual"].with_user(x.emp_u).search([])
    assert mine and set(mine.mapped("employee_id")) == {x.e_emp}
    assert (
        not x.env["fix.leave.accrual"].with_user(x.col_u).search([("employee_id", "=", x.e_emp.id)])
    )


# ======================================================================= citation (P8)
def test_citation_verification_is_an_action_not_a_default(x):
    t = (
        x.env["fix.leave.type"]
        .with_user(x.hro_u)
        .create(
            {
                "code": "a9study",
                "name": "Study",
                "entitlement_days": 5,
                "is_statutory": False,
                "labour_act_section": "Policy",
                "legal_citation": "HR policy handbook 2026",
            }
        )
    )
    assert not t.verified_on
    with pytest.raises(UserError, match="changes only through its workflow"):
        rpc(x, x.hro_u, "fix.leave.type", "write", [t.id], {"verified_on": str(x.today)})
    with pytest.raises(UserError, match="HR Officer"), x.env.cr.savepoint():
        t.with_user(x.emp_u).action_verify_citation()
    t.with_user(x.hro_u).action_verify_citation()
    hr_today = fields.Date.context_today(t.with_user(x.hro_u))
    assert (t.verified_on, t.verified_by_id) == (hr_today, x.hro_u)
    t.with_user(x.hro_u).write({"legal_citation": "HR policy handbook 2027"})
    assert not t.verified_on


# ======================================================================= deployment
def test_deployment_cron_rules_and_acl(x):
    env = x.env
    cron = env.ref("cd_hr_core.cron_accrue_annual_leave")
    assert cron.active and cron.model_id.model == "fix.leave.accrual"
    assert cron.code.strip() == "model.cron_accrue_annual_leave()"
    for xmlid in ("cd_hr_core.rule_leave_request_own", "cd_hr_core.rule_leave_accrual_own"):
        assert not env.ref(xmlid).groups
    row = env.ref("cd_hr_core.access_fix_leave_accrual_user")
    assert (row.perm_read, row.perm_write, row.perm_create, row.perm_unlink) == (
        True,
        False,
        False,
        False,
    )
    assert env.ref("cd_hr_core.leave_type_sick").requires_certificate
    assert not env.ref("cd_hr_core.leave_type_maternity").excludes_holidays
