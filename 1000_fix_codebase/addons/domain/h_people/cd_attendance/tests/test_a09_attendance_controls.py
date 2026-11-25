# A09 acceptance suite for M55 attendance (workflow audit P0-b B1-B6, P1 C5,
# P2 overtime; working/A09_evidence/module_findings/M55.md).
#
# Every attack runs as a freshly created NON-admin user and is refused; the
# proper path is then run by the right role. Writes go through call_kw with
# the client-controlled `tracking_disable` key, as the P0 suites do, and the
# workspace through the real /p03 controller with `request` patched.
import itertools
from datetime import date, datetime, timedelta
from types import SimpleNamespace
from unittest import mock

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_p03_portal.controllers.a09 import m55
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.service.model import call_kw

REFUSED = (AccessError, UserError, ValidationError)
REC = "fix.attendance.record"
JAN_S, JAN_E = date(2026, 1, 1), date(2026, 1, 31)
_SEQ = itertools.count(1)


def _user(env, *groups, ous=None):
    n = next(_SEQ)
    ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    vals = {
        "name": "A09 M55 User %d" % n,
        "login": "a09-m55-att-%d@test.local" % n,
        "group_ids": [(6, 0, ids)],
    }
    if ous is not None:
        vals["assigned_operating_unit_ids"] = [(6, 0, ous.ids)]
        vals["default_operating_unit_id"] = ous[:1].id
    return env["res.users"].with_context(no_reset_password=True).create(vals)


def dt(day, hour, minute=0):
    return datetime(day.year, day.month, day.day, hour, minute)


@pytest.fixture
def x(odoo_env):
    env = odoo_env
    c = SimpleNamespace(env=env)
    c.ou1 = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    c.ou2 = env["operating.unit"].create(
        {
            "name": "A09M55 OU2",
            "code": "A9M55B2",
            "company_id": env.company.id,
            "partner_id": env.company.partner_id.id,
        }
    )
    c.emp_u = _user(env, ous=c.ou1)
    c.col_u = _user(env, ous=c.ou1)
    # W4 (apply-as-approver): the M63 engine decides in the approver's
    # environment, so the routed line manager holds the attendance role
    # (write on fix.attendance.regularisation) like the officers below.
    c.mgr_u = _user(env, "hr_attendance.group_hr_attendance_user", ous=c.ou1)
    c.off_u = _user(env, "hr_attendance.group_hr_attendance_user", ous=c.ou1)
    c.off2_u = _user(env, "hr_attendance.group_hr_attendance_user", ous=c.ou1)
    c.sup_u = _user(env, "cd_attendance.group_attendance_supervisor", ous=c.ou1)
    c.sup2_u = _user(env, "cd_attendance.group_attendance_supervisor", ous=c.ou2)
    c.lockmgr_u = _user(env, "cd_attendance.group_attendance_lock_manager", ous=c.ou1)
    c.hrm_u = _user(env, "hr.group_hr_manager", ous=c.ou1)
    c.hro_u = _user(env, "cd_hr_core.group_hr_officer", ous=c.ou1)
    c.fem_u = _user(env, ous=c.ou1)
    E = env["hr.employee"]
    c.e_mgr = E.create({"name": "M55 Line Manager", "user_id": c.mgr_u.id})
    c.e_emp = E.create(
        {"name": "M55 Employee", "user_id": c.emp_u.id, "parent_id": c.e_mgr.id, "sex": "male"}
    )
    c.e_col = E.create({"name": "M55 Colleague", "user_id": c.col_u.id, "parent_id": c.e_mgr.id})
    c.e_off = E.create({"name": "M55 Officer Self", "user_id": c.off_u.id})
    c.e_fem = E.create({"name": "M55 Female Tech", "user_id": c.fem_u.id, "sex": "female"})
    c.dev = env["fix.biometric.device"].create({"device_id": "A9M55-DEV-1", "name": "Gate"})
    c.dev_off = env["fix.biometric.device"].create(
        {"device_id": "A9M55-DEV-OFF", "name": "Old gate", "active": False, "status": "offline"}
    )
    c.shift_day = env["fix.shift.template"].create(
        {"name": "A9M55 Day", "start_hour": 9.0, "end_hour": 17.0}
    )
    c.shift_night = env["fix.shift.template"].create(
        {"name": "A9M55 Night", "start_hour": 22.0, "end_hour": 6.0}
    )
    return c


def rpc(c, user, model, method, ids, *args, **kw):
    env = c.env(user=user.id, context={"tracking_disable": True})
    return call_kw(env[model], method, [ids, *args], kw)


def manual(c, user, day, h_in, h_out, emp=None, reason="forgot my card"):
    return (
        c.env[REC]
        .with_user(user)
        .create(
            {
                "employee_id": (emp or c.e_emp).id,
                "check_in": dt(day, h_in),
                "check_out": dt(day, h_out),
                "manual_reason": reason,
            }
        )
    )


def clean(c, day, h_in, h_out, emp=None):
    """setup: a clean device punch (superuser = the device integration)."""
    return c.env[REC].create(
        {
            "employee_id": (emp or c.e_emp).id,
            "check_in": dt(day, h_in),
            "check_out": dt(day, h_out),
            "source": "biometric",
        }
    )


def flagged(c, day, h_in=9, h_out=17, emp=None):
    """setup: a flagged mobile clock-in exactly as the technician API records it."""
    return c.env[REC].create(
        {
            "employee_id": (emp or c.e_emp).id,
            "check_in": dt(day, h_in),
            "check_out": dt(day, h_out),
            "source": "mobile",
            "geofence_result": "outside",
            "approval_state": "pending",
            "approval_reason": "position outside the geofence",
        }
    )


def tasks(c, rec):
    return (
        c.env["fix.workflow.task"]
        .sudo()
        .search([("res_model", "=", rec._name), ("res_id", "=", rec.id), ("state", "=", "pending")])
    )


def assignees(c, rec):
    return tasks(c, rec).mapped("assigned_user_id")


def lock(c, start=JAN_S, end=JAN_E, user=None):
    lk = (
        c.env["fix.attendance.lock"]
        .with_user(user or c.sup_u)
        .create({"name": "A9M55 %s" % start, "period_start": start, "period_end": end})
    )
    lk.action_lock()
    return lk


@pytest.fixture
def p03(x):
    patchers = []

    def as_user(user):
        p = mock.patch.object(api, "request", SimpleNamespace(env=x.env(user=user.id)))
        p.start()
        patchers.append(p)
        ctl = api.P03GenericApiController()
        return SimpleNamespace(
            write=lambda **kw: ctl.model_write(**kw),
            action=lambda **kw: ctl.model_action(**kw),
            report=lambda **kw: ctl.model_report(**kw),
        )

    yield as_user
    for p in patchers:
        p.stop()


# ======================================================================= capture (M55-3, M55-8)
def test_manual_entry_needs_a_reason_and_is_born_pending(x):
    with pytest.raises(UserError, match="states its reason"), x.env.cr.savepoint():
        manual(x, x.emp_u, date(2026, 2, 6), 9, 19, reason="")
    r = manual(x, x.emp_u, date(2026, 2, 6), 9, 19)
    assert r.approval_state == "pending"
    assert r.approval_reason.startswith("Manual entry by %s: forgot my card" % x.emp_u.name)
    assert r.source == "manual"


def test_employee_cannot_forge_a_biometric_or_mobile_row(x):
    for vals in (
        {"source": "biometric", "device_ref": "NO-SUCH-DEVICE"},
        {"source": "mobile", "geofence_result": "inside"},
        {"approval_state": "not_required"},
    ):
        with (
            pytest.raises(UserError, match="changes only through its workflow"),
            x.env.cr.savepoint(),
        ):
            manual(x, x.emp_u, date(2026, 2, 4), 9, 19).write(vals)
        if vals == {"approval_state": "not_required"}:
            continue  # the default: accepted, and the entry is still born pending
        with pytest.raises(UserError), x.env.cr.savepoint():
            x.env[REC].with_user(x.emp_u).create(
                {
                    "employee_id": x.e_emp.id,
                    "check_in": dt(date(2026, 2, 5), 9),
                    "manual_reason": "x",
                    **vals,
                }
            )


def test_employee_cannot_record_or_edit_a_colleagues_attendance(x):
    with pytest.raises(AccessError), x.env.cr.savepoint():
        manual(x, x.emp_u, date(2026, 2, 4), 9, 19, emp=x.e_col)
    col = clean(x, date(2026, 2, 20), 9, 17, emp=x.e_col)
    with pytest.raises(AccessError), x.env.cr.savepoint():
        rpc(x, x.emp_u, REC, "write", [col.id], {"check_out": dt(date(2026, 2, 20), 23)})
    # nor read the colleague's GPS position (B12)
    assert not x.env[REC].with_user(x.emp_u).search([("id", "=", col.id)])


def test_device_ingest_registered_active_and_replay_safe(x):
    with pytest.raises(AccessError), x.env.cr.savepoint():
        x.dev.with_user(x.emp_u).action_ingest_punch(x.e_col.id, dt(date(2026, 2, 3), 9))
    with pytest.raises(UserError, match="inactive or offline"), x.env.cr.savepoint():
        x.dev_off.with_user(x.sup_u).action_ingest_punch(x.e_emp.id, dt(date(2026, 2, 3), 9))
    d = x.dev.with_user(x.sup_u)
    # BRU-WFM-08: no punch without the employee's own biometric consent
    with pytest.raises(UserError, match="no recorded consent"), x.env.cr.savepoint():
        d.action_ingest_punch(x.e_emp.id, dt(date(2026, 2, 3), 9))
    consent = x.env["fix.biometric.consent"].with_user(x.hro_u).create({"employee_id": x.e_emp.id})
    consent.with_user(x.emp_u).action_give()
    first = d.action_ingest_punch(x.e_emp.id, dt(date(2026, 2, 3), 9))
    replay = d.action_ingest_punch(x.e_emp.id, dt(date(2026, 2, 3), 9))
    assert replay == first
    out = d.action_ingest_punch(x.e_emp.id, dt(date(2026, 2, 3), 18), "check_out")
    again = d.action_ingest_punch(x.e_emp.id, dt(date(2026, 2, 3), 18), "check_out")
    assert out == again == first
    recs = x.env[REC].search([("employee_id", "=", x.e_emp.id)])
    assert len(recs) == 1 and recs.check_out == dt(date(2026, 2, 3), 18)
    assert (recs.source, recs.device_id, recs.approval_state) == (
        "biometric",
        x.dev,
        "not_required",
    )


def test_overlapping_records_are_refused(x):
    clean(x, date(2026, 2, 5), 8, 18)
    for h_in, h_out in ((8, 18), (12, 20), (7, 9)):
        with pytest.raises(ValidationError, match="overlapping"), x.env.cr.savepoint():
            clean(x, date(2026, 2, 5), h_in, h_out)
    assert clean(x, date(2026, 2, 5), 18, 19)  # back to back is not an overlap


# ======================================================================= decisions (M55-2, M55-9)
def test_employee_cannot_approve_his_own_record(x, p03):
    r = flagged(x, date(2026, 2, 9), 9, 21)
    for vals in (
        {"approval_state": "approved", "approved_by": x.off_u.id},
        {"approved_at": fields.Datetime.now()},
        {"geofence_result": "inside", "approval_reason": False},
    ):
        with pytest.raises(UserError, match="changes only through its workflow"):
            rpc(x, x.emp_u, REC, "write", [r.id], vals)
    res = p03(x.emp_u).write(model=REC, record_id=r.id, values={"approval_state": "approved"})
    r.invalidate_recordset()
    assert r.approval_state == "pending", res
    with pytest.raises(UserError, match="has not been routed"), x.env.cr.savepoint():
        r.with_user(x.emp_u).action_approve()


def test_routed_to_the_line_manager_never_the_requester(x, p03):
    r = flagged(x, date(2026, 2, 12))
    r.with_user(x.emp_u).action_request_regularisation()
    reg = r.regularisation_ids
    assert assignees(x, reg) == x.mgr_u
    # the employee, a colleague and an unrelated officer cannot decide it
    for user in (x.emp_u, x.col_u, x.off_u):
        with pytest.raises(UserError, match="not awaiting your decision"), x.env.cr.savepoint():
            r.with_user(user).action_approve()
    res = p03(x.emp_u).action(model=REC, ids=[r.id], method="action_approve")
    assert not res["success"]
    res = p03(x.mgr_u).action(model=REC, ids=[r.id], method="action_approve")
    assert res["success"], res
    r.invalidate_recordset()
    assert (r.approval_state, r.approved_by, reg.state) == ("approved", x.mgr_u, "approved")


def test_officer_never_decides_his_own_clock_in(x):
    r = flagged(x, date(2026, 2, 11), emp=x.e_off)
    r.with_user(x.off_u).action_request_regularisation()
    reg = r.regularisation_ids
    assert x.off_u not in assignees(x, reg)
    assert x.off2_u in assignees(x, reg)
    with pytest.raises(UserError), x.env.cr.savepoint():
        r.with_user(x.off_u).action_approve()
    r.with_user(x.off2_u).action_approve()
    assert (r.approval_state, r.approved_by) == ("approved", x.off2_u)


def test_reject_needs_a_reason_and_a_rejected_record_stays_rejected(x):
    r = flagged(x, date(2026, 2, 18), 9, 21)
    r.with_user(x.emp_u).action_request_regularisation()
    with pytest.raises(UserError, match="State why"), x.env.cr.savepoint():
        r.with_user(x.mgr_u).action_reject()
    r.with_user(x.mgr_u).action_reject(reason="not on site")
    assert (r.approval_state, r.worked_hours) == ("rejected", 0.0)
    with pytest.raises(UserError, match="changes only through its workflow"):
        rpc(x, x.emp_u, REC, "write", [r.id], {"approval_state": "not_required"})
    with pytest.raises(UserError, match="not re-opened by editing"), x.env.cr.savepoint():
        rpc(x, x.emp_u, REC, "write", [r.id], {"check_out": dt(date(2026, 2, 18), 22)})


def test_changing_the_hours_of_a_decided_record_reopens_it(x):
    r = flagged(x, date(2026, 2, 16), 9, 17)
    r.with_user(x.emp_u).action_request_regularisation()
    r.with_user(x.mgr_u).action_approve()
    assert r.approval_state == "approved"
    rpc(x, x.emp_u, REC, "write", [r.id], {"check_out": dt(date(2026, 2, 16), 23)})
    r.invalidate_recordset()
    assert (r.approval_state, r.approved_by.id) == ("pending", False)
    assert "hours changed by" in r.approval_reason
    # a pending request voids when the hours move under it
    r.with_user(x.emp_u).action_request_regularisation()
    open_reg = r.regularisation_ids.filtered(lambda g: g.state == "open")
    rpc(x, x.emp_u, REC, "write", [r.id], {"check_out": dt(date(2026, 2, 16), 20)})
    assert open_reg.state == "voided"


def test_cron_routes_every_pending_record_idempotently(x):
    a = flagged(x, date(2026, 2, 23))
    b = manual(x, x.emp_u, date(2026, 2, 24), 9, 17)
    Record = x.env[REC]
    Record.cron_route_pending_attendance()
    assert len(a.regularisation_ids) == len(b.regularisation_ids) == 1
    Record.cron_route_pending_attendance()
    assert len(a.regularisation_ids) == len(b.regularisation_ids) == 1
    assert assignees(x, a.regularisation_ids) == x.mgr_u


# ======================================================================= valuation & overtime (M55-4)
def test_split_shift_keeps_its_overtime(x):
    a = clean(x, date(2026, 2, 26), 6, 12)
    b = clean(x, date(2026, 2, 26), 13, 19)
    assert (a.recorded_overtime_hours, b.recorded_overtime_hours) == (0.0, 4.0)
    assert a.overtime_hours + b.overtime_hours == 0.0  # none approved
    assert b.compliance_status == "daily_limit_exceeded"  # 12h that day


def test_overtime_is_payable_only_when_approved_and_capped(x):
    day = fields.Date.today() + timedelta(days=3)
    r = clean(x, day, 8, 22)  # 14h: 6h recorded overtime
    assert (r.recorded_overtime_hours, r.overtime_hours) == (6.0, 0.0)
    OT = x.env["fix.overtime.request"].with_user(x.emp_u)
    with pytest.raises(ValidationError, match="At most 2 h"), x.env.cr.savepoint():
        OT.create({"employee_id": x.e_emp.id, "date": day, "hours": 6, "reason": "rush"})
    req = OT.create({"employee_id": x.e_emp.id, "date": day, "hours": 2, "reason": "rush job"})
    with pytest.raises(UserError, match="changes only through its workflow"):
        rpc(x, x.emp_u, "fix.overtime.request", "write", [req.id], {"state": "approved"})
    req.action_submit()
    assert (req.state, req.retrospective, assignees(x, req)) == ("submitted", False, x.mgr_u)
    with pytest.raises(UserError, match="not awaiting your decision"), x.env.cr.savepoint():
        req.with_user(x.emp_u).action_inbox_approve()
    with pytest.raises(UserError), x.env.cr.savepoint():
        req.with_user(x.mgr_u).action_approve()  # direct, not from the task
    req.with_user(x.mgr_u).action_inbox_approve()
    r.invalidate_recordset()
    assert (req.state, req.approved_hours, req.decided_by_id) == ("approved", 2.0, x.mgr_u)
    assert (r.recorded_overtime_hours, r.overtime_hours, r.unapproved_overtime_hours) == (
        6.0,
        2.0,
        4.0,
    )
    with pytest.raises(UserError, match="changed only in draft"):
        rpc(x, x.emp_u, "fix.overtime.request", "write", [req.id], {"hours": 1.5})
    req.with_user(x.emp_u).action_cancel()
    r.invalidate_recordset()
    assert r.overtime_hours == 0.0


def test_retrospective_overtime_goes_to_hr_not_the_line_manager(x):
    day = fields.Date.today() - timedelta(days=2)
    req = (
        x.env["fix.overtime.request"]
        .with_user(x.emp_u)
        .create({"employee_id": x.e_emp.id, "date": day, "hours": 2, "reason": "late"})
    )
    with pytest.raises(UserError, match="retrospective"), x.env.cr.savepoint():
        req.action_submit()
    req.write({"reason": "Generator failure kept the branch open until 22:00"})
    req.action_submit()
    who = assignees(x, req)
    assert req.retrospective and x.mgr_u not in who and x.hrm_u in who


def test_overtime_ineligible_employee_gets_none(x):
    x.e_emp.overtime_eligible = False
    req = (
        x.env["fix.overtime.request"]
        .with_user(x.emp_u)
        .create({"employee_id": x.e_emp.id, "date": fields.Date.today(), "hours": 2, "reason": "x"})
    )
    with pytest.raises(UserError, match="not overtime-eligible"), x.env.cr.savepoint():
        req.action_submit()


def test_rest_day_is_marked_by_the_supervisor_not_the_employee(x):
    r = manual(x, x.emp_u, date(2026, 2, 25), 9, 17)
    with pytest.raises(UserError, match="changes only through its workflow"):
        rpc(x, x.emp_u, REC, "write", [r.id], {"is_rest_day": True})
    with pytest.raises(AccessError), x.env.cr.savepoint():
        r.with_user(x.emp_u).action_mark_rest_day()
    r.with_user(x.sup_u).action_mark_rest_day()
    assert (r.is_rest_day, r.recorded_overtime_hours, r.overtime_hours) == (True, 8.0, 0.0)


def test_public_holiday_hours_are_valued_as_such(x):
    x.env["fix.hr.holiday"].create(
        {"name": "A9M55 Shaheed Dibosh", "date": date(2031, 2, 21), "holiday_type": "public"}
    )
    r = clean(x, date(2031, 2, 21), 9, 17)
    assert r.holiday_hours == 8.0


# ======================================================================= the lock (M55-5, M55-6)
def test_lock_cannot_be_born_locked_or_written_locked(x, p03):
    t = fields.Date.today()
    with pytest.raises(UserError, match="changes only through its workflow"):
        x.env["fix.attendance.lock"].with_user(x.sup_u).create(
            {
                "name": "born",
                "period_start": t.replace(day=1),
                "period_end": t + timedelta(days=27),
                "state": "locked",
            }
        )
    res = p03(x.sup_u).write(
        model="fix.attendance.lock",
        values={
            "name": "p03 born",
            "period_start": str(t.replace(day=1)),
            "period_end": str(t + timedelta(days=27)),
            "state": "locked",
        },
    )
    made = x.env["fix.attendance.lock"].browse(res.get("id") or 0).exists()
    assert not (made and made.state == "locked"), res
    # even a trusted (superuser) load never locks over a pending clock-in
    flagged(x, JAN_S + timedelta(days=4))
    with pytest.raises(UserError, match="pending approval"), x.env.cr.savepoint():
        x.env["fix.attendance.lock"].create(
            {"name": "legacy", "period_start": JAN_S, "period_end": JAN_E, "state": "locked"}
        )


def test_pending_check_sees_every_operating_unit(x):
    p = flagged(x, date(2026, 1, 21))
    p.write({"operating_unit_id": x.ou1.id})
    with pytest.raises(UserError, match="pending approval"), x.env.cr.savepoint():
        lock(x, user=x.sup2_u)


def test_one_lock_per_period(x):
    lock(x)
    with pytest.raises(ValidationError, match="one lock per period"), x.env.cr.savepoint():
        x.env["fix.attendance.lock"].with_user(x.sup_u).create(
            {"name": "dup", "period_start": date(2026, 1, 15), "period_end": date(2026, 2, 15)}
        )


def test_a_record_is_not_moved_into_a_locked_period(x):
    lock(x)
    r = clean(x, date(2026, 2, 2), 9, 17)
    with (
        pytest.raises(UserError, match="Cannot move attendance in locked period"),
        x.env.cr.savepoint(),
    ):
        r.write({"check_in": dt(date(2026, 1, 15), 9), "check_out": dt(date(2026, 1, 15), 17)})


def test_unlock_needs_its_own_role_a_reason_and_an_untaken_period(x):
    clean(x, date(2026, 1, 12), 9, 17)
    lk = lock(x)
    with pytest.raises(AccessError, match="Lock Manager"), x.env.cr.savepoint():
        lk.with_user(x.sup_u).action_unlock(reason="fix")
    with pytest.raises(UserError, match="State why"), x.env.cr.savepoint():
        lk.with_user(x.lockmgr_u).action_unlock()
    lk.with_user(x.lockmgr_u).action_unlock(reason="late upload from the Uttara terminal")
    assert (lk.state, lk.unlocked_by_id, lk.unlock_count) == ("unlocked", x.lockmgr_u, 1)
    late = clean(x, date(2026, 1, 13), 9, 17)
    assert late.retro_change
    lk.with_user(x.sup_u).action_lock()
    assert (lk.state, lk.retro_flag) == ("locked", True)
    # payroll takes the period: it is never re-opened again
    P = x.env["fix.payroll.period"].create(
        {"name": "A9M55-2026-01", "period_start": JAN_S, "period_end": JAN_E}
    )
    P.action_verify_attendance_locked()
    with pytest.raises(UserError, match=r"payroll .* has already taken it"), x.env.cr.savepoint():
        lk.with_user(x.lockmgr_u).action_unlock(reason="one more fix")


def test_payroll_pays_only_approved_overtime(x):
    x.env["fix.employment.contract"].create(
        {
            "employee_id": x.e_emp.id,
            "company_id": x.env.company.id,
            "contract_type": "permanent",
            "joining_date": date(2020, 1, 1),
            "basic_monthly": 20800.0,
            "state": "active",
        }
    )
    for d in (5, 6, 7):
        clean(x, date(2026, 1, d), 8, 22)  # 14h days, 6h recorded each
    # one day had 2h approved before it was worked (superuser = data setup)
    req = x.env["fix.overtime.request"].create(
        {"employee_id": x.e_emp.id, "date": date(2026, 1, 6), "hours": 2, "reason": "rush"}
    )
    req.write({"state": "submitted"})
    req.action_approve()
    lk = lock(x)
    rows = lk.with_user(x.sup_u).action_export_form10_overtime_register()
    row = next(r for r in rows if r["employee_id"] == x.e_emp.id)
    assert (row["overtime_hours"], row["overtime_pay"]) == (2.0, 400.0)
    P = x.env["fix.payroll.period"].create(
        {"name": "A9M55-PAY", "period_start": JAN_S, "period_end": JAN_E}
    )
    P.action_verify_attendance_locked()
    P.action_calculate()
    slip = P.payslip_ids.filtered(lambda s: s.employee_id == x.e_emp)
    assert slip.ot_hours == 2.0


# ======================================================================= roster (M55-10, s.109)
def test_double_rostering_and_women_night_work(x):
    S = x.env["fix.roster.slot"].with_user(x.sup_u)
    S.create({"employee_id": x.e_emp.id, "date": date(2026, 3, 10), "shift_id": x.shift_day.id})
    with pytest.raises(ValidationError, match="at most 10 h a day"), x.env.cr.savepoint():
        S.create(
            {"employee_id": x.e_emp.id, "date": date(2026, 3, 10), "shift_id": x.shift_night.id}
        )
    with pytest.raises(ValidationError, match=r"s\.109"), x.env.cr.savepoint():
        S.create(
            {"employee_id": x.e_fem.id, "date": date(2026, 3, 9), "shift_id": x.shift_night.id}
        )
    Consent = x.env["fix.night.work.consent"]
    consent = Consent.with_user(x.fem_u).create(
        {"employee_id": x.e_fem.id, "date_from": date(2026, 3, 1), "date_to": date(2026, 3, 31)}
    )
    # the supervisor who rosters her does not give her consent for her
    with pytest.raises(AccessError), x.env.cr.savepoint():
        consent.with_user(x.sup_u).action_confirm()
    with pytest.raises(UserError, match="changes only through its workflow"):
        rpc(x, x.fem_u, "fix.night.work.consent", "write", [consent.id], {"state": "active"})
    consent.with_user(x.fem_u).action_confirm()
    slot = S.create(
        {"employee_id": x.e_fem.id, "date": date(2026, 3, 9), "shift_id": x.shift_night.id}
    )
    assert slot and consent.confirmed_by_id == x.fem_u


def test_on_leave_is_never_typed(x):
    slot = (
        x.env["fix.roster.slot"]
        .with_user(x.sup_u)
        .create({"employee_id": x.e_emp.id, "date": date(2026, 3, 11), "shift_id": x.shift_day.id})
    )
    with pytest.raises(UserError, match="changes only through its workflow"):
        rpc(x, x.sup_u, "fix.roster.slot", "write", [slot.id], {"on_leave": True})


def _approved_leave(x, day, emp=None):
    casual = x.env["fix.leave.type"].search(
        [("code", "=", "casual"), ("company_id", "=", x.env.company.id)], limit=1
    )
    lv = (
        x.env["fix.leave.request"]
        .with_user(x.emp_u)
        .create(
            {
                "employee_id": (emp or x.e_emp).id,
                "leave_type_id": casual.id,
                "date_from": day,
                "date_to": day,
            }
        )
    )
    lv.action_submit()
    lv.with_user(x.mgr_u).action_inbox_approve()
    return lv


def test_approved_leave_marks_the_roster_and_blocks_dispatch(x):
    t = fields.Date.today() + timedelta(days=3)
    slot = (
        x.env["fix.roster.slot"]
        .with_user(x.sup_u)
        .create({"employee_id": x.e_emp.id, "date": t, "shift_id": x.shift_day.id})
    )
    lv = _approved_leave(x, t)
    slot.invalidate_recordset()
    assert lv.state == "approved" and slot.on_leave
    lv.with_user(x.emp_u).action_cancel(reason="plans changed")
    slot.invalidate_recordset()
    assert lv.state == "cancelled" and not slot.on_leave


def test_leave_days_skip_public_holidays_and_locked_months_are_closed(x):
    x.env["fix.hr.holiday"].create(
        {"name": "A9M55 holiday", "date": date(2031, 2, 21), "holiday_type": "public"}
    )
    casual = x.env["fix.leave.type"].search(
        [("code", "=", "casual"), ("company_id", "=", x.env.company.id)], limit=1
    )
    lv = (
        x.env["fix.leave.request"]
        .with_user(x.emp_u)
        .create(
            {
                "employee_id": x.e_emp.id,
                "leave_type_id": casual.id,
                "date_from": date(2031, 2, 20),
                "date_to": date(2031, 2, 22),
            }
        )
    )
    assert lv.days == 2
    # F11: a back-dated leave inside a locked (and paid) month is refused
    clean(x, date(2026, 1, 12), 8, 18)
    lock(x)
    back = (
        x.env["fix.leave.request"]
        .with_user(x.emp_u)
        .create(
            {
                "employee_id": x.e_emp.id,
                "leave_type_id": casual.id,
                "date_from": date(2026, 1, 12),
                "date_to": date(2026, 1, 13),
            }
        )
    )
    with pytest.raises(UserError, match="locked attendance period"), x.env.cr.savepoint():
        back.action_submit()


def test_a_worked_day_is_not_also_a_leave_day(x):
    clean(x, date(2026, 3, 3), 9, 17)
    casual = x.env["fix.leave.type"].search(
        [("code", "=", "casual"), ("company_id", "=", x.env.company.id)], limit=1
    )
    lv = (
        x.env["fix.leave.request"]
        .with_user(x.emp_u)
        .create(
            {
                "employee_id": x.e_emp.id,
                "leave_type_id": casual.id,
                "date_from": date(2026, 3, 3),
                "date_to": date(2026, 3, 4),
            }
        )
    )
    with pytest.raises(UserError, match="either worked or on leave"), x.env.cr.savepoint():
        lv.action_submit()


# ======================================================================= on-call (H2)
def test_on_call_state_is_guarded_and_completed_shifts_stay_completed(x):
    oc = (
        x.env["fix.hr.oncall"]
        .with_user(x.sup_u)
        .create(
            {
                "employee_id": x.e_emp.id,
                "date_from": dt(date(2026, 3, 1), 18),
                "date_to": dt(date(2026, 3, 2), 8),
                "allowance": 1500,
            }
        )
    )
    with pytest.raises(UserError, match="changes only through its workflow"):
        rpc(x, x.sup_u, "fix.hr.oncall", "write", [oc.id], {"state": "completed"})
    with pytest.raises(AccessError), x.env.cr.savepoint():
        oc.with_user(x.emp_u).action_start()
    oc.action_start()
    oc.action_complete()
    with pytest.raises(UserError, match="planned or active"), x.env.cr.savepoint():
        oc.action_cancel()
    with pytest.raises(UserError, match="final"), x.env.cr.savepoint():
        rpc(x, x.sup_u, "fix.hr.oncall", "write", [oc.id], {"allowance": 9000})


# ======================================================================= reports & KPIs (M55-11)
def test_attendance_summary_shows_only_what_the_caller_may_read(x, p03):
    co_b = x.env["res.company"].create({"name": "A9M55 Co B"})
    eb = x.env["hr.employee"].create({"name": "A9M55 Company-B Worker", "company_id": co_b.id})
    x.env[REC].create(
        {
            "employee_id": eb.id,
            "company_id": co_b.id,
            "check_in": dt(date(2026, 2, 3), 8),
            "check_out": dt(date(2026, 2, 3), 20),
            "source": "manual",
        }
    )
    clean(x, date(2026, 2, 3), 9, 17, emp=x.e_col)
    clean(x, date(2026, 2, 4), 9, 17)
    out = p03(x.emp_u).report(
        module="M55",
        report="attendance_summary",
        params={"date_from": "2026-02-01", "date_to": "2026-02-28"},
    )
    names = [r["employee"] for r in out.get("rows", [])]
    assert names == [x.e_emp.name], out
    # the manager sees his reports
    out = p03(x.mgr_u).report(
        module="M55",
        report="attendance_summary",
        params={"date_from": "2026-02-01", "date_to": "2026-02-28"},
    )
    assert {r["employee"] for r in out["rows"]} == {x.e_emp.name, x.e_col.name}


def test_overtime_kpi_counts_overtime_approvals_not_geofence_flags(x):
    before = m55.kpis(x.env(user=x.off_u.id))["overtime_preapproved"]
    r = flagged(x, fields.Date.today(), 9, 16)
    r.action_request_regularisation()
    r.with_user(x.mgr_u).action_approve()
    assert m55.kpis(x.env(user=x.off_u.id))["overtime_preapproved"] == before
    req = x.env["fix.overtime.request"].create(
        {"employee_id": x.e_emp.id, "date": fields.Date.today(), "hours": 1, "reason": "x"}
    )
    req.write({"state": "submitted"})
    req.action_approve()
    assert m55.kpis(x.env(user=x.off_u.id))["overtime_preapproved"] == before + 1


# ======================================================================= deployment
def test_deployment_crons_groups_acl_and_surfaces(x):
    env = x.env
    cron = env.ref("cd_attendance.cron_route_pending_attendance")
    assert cron.active and cron.model_id.model == REC
    assert cron.code.strip() == "model.cron_route_pending_attendance()"
    assert env.ref("cd_attendance.group_attendance_lock_manager")
    Access = env["ir.model.access"]
    for model, perms in (
        ("fix.attendance.regularisation", (True, False, False)),
        ("fix.overtime.request", (True, True, True)),
        ("fix.night.work.consent", (True, True, True)),
    ):
        row = Access.search(
            [("model_id.model", "=", model), ("group_id", "=", env.ref("base.group_user").id)]
        )
        assert (row.perm_read, row.perm_write, row.perm_create) == perms, model
        assert not row.perm_unlink
    for xmlid in (
        "cd_attendance.rule_attendance_record_own",
        "cd_attendance.rule_attendance_regularisation_own",
        "cd_attendance.rule_overtime_request_own",
        "cd_attendance.rule_night_work_consent_own",
    ):
        assert not env.ref(xmlid).groups  # global rules
    surf = m55.SURFACES
    assert {"action_request_regularisation", "action_approve", "action_reject"} <= surf[REC][
        "actions"
    ]
    assert {"action_submit", "action_inbox_approve", "action_reject", "action_cancel"} <= surf[
        "fix.leave.request"
    ]["actions"]
    assert "action_ingest_punch" not in surf["fix.biometric.device"]["actions"]
    assert "action_approve" not in surf["fix.leave.request"]["actions"]
