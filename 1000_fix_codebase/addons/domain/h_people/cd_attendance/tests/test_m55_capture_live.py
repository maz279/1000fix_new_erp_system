# M55 capture audit 2026-11-17: the three records the workspace pages could not
# capture, exercised as freshly created NON-admin users on a real database.
#
#   fix.oncall.callout     FR-WFM-044 (recorded inside a started on-call window,
#                          verified by the line manager, never the person on call)
#   fix.capacity.forecast  FR-WFM-048/049 (measured from the roster, leave out,
#                          skill = valid certification, gap alert on publish)
#   fix.timesheet.line     FR-WFM-050 (never more than the day's verified
#                          attendance, line-manager approval, locked periods shut)
import itertools
from datetime import date, datetime, timedelta
from types import SimpleNamespace
from unittest import mock

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (AccessError, UserError, ValidationError)
_SEQ = itertools.count(1)


def _user(env, *groups, ous=None):
    n = next(_SEQ)
    ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    vals = {
        "name": "M55 Capture User %d" % n,
        "login": "m55-capture-%d@test.local" % n,
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
    c.ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    c.emp_u = _user(env, ous=c.ou)
    c.col_u = _user(env, ous=c.ou)
    c.mgr_u = _user(env, "hr_attendance.group_hr_attendance_user", ous=c.ou)
    c.off_u = _user(env, "hr_attendance.group_hr_attendance_user", ous=c.ou)
    c.sup_u = _user(env, "cd_attendance.group_attendance_supervisor", ous=c.ou)
    E = env["hr.employee"]
    c.e_mgr = E.create({"name": "M55C Line Manager", "user_id": c.mgr_u.id})
    c.e_emp = E.create({"name": "M55C Technician", "user_id": c.emp_u.id, "parent_id": c.e_mgr.id})
    c.e_col = E.create({"name": "M55C Colleague", "user_id": c.col_u.id, "parent_id": c.e_mgr.id})
    c.shift = env["fix.shift.template"].create(
        {"name": "M55C Day", "start_hour": 9.0, "end_hour": 17.0}
    )
    return c


@pytest.fixture
def p03(x):
    patchers = []

    def as_user(user):
        p = mock.patch.object(api, "request", SimpleNamespace(env=x.env(user=user.id)))
        p.start()
        patchers.append(p)
        ctl = api.P03GenericApiController()
        return SimpleNamespace(write=lambda **kw: ctl.model_write(**kw))

    yield as_user
    for p in patchers:
        p.stop()


def assignees(c, rec):
    return (
        c.env["fix.workflow.task"]
        .sudo()
        .search([("res_model", "=", rec._name), ("res_id", "=", rec.id), ("state", "=", "pending")])
        .mapped("assigned_user_id")
    )


# ======================================================================= callouts
def _oncall(c, day, start=True):
    oc = (
        c.env["fix.hr.oncall"]
        .with_user(c.sup_u)
        .create(
            {
                "employee_id": c.e_emp.id,
                "date_from": dt(day, 18),
                "date_to": dt(day + timedelta(days=1), 8),
            }
        )
    )
    if start:
        oc.action_start()
    return oc


def _callout(c, user, oc, h_from=20, h_to=23, **kw):
    day = oc.date_from.date()
    vals = {
        "oncall_id": oc.id,
        "called_at": dt(day, h_from),
        "finished_at": dt(day, h_to),
        "description": "Server room AC failure at the branch",
    }
    vals.update(kw)
    return c.env["fix.oncall.callout"].with_user(user).create(vals)


def test_callout_is_recorded_inside_a_started_window_and_verified_by_the_manager(x):
    day = fields.Date.today() + timedelta(days=5)
    planned = _oncall(x, day, start=False)
    with pytest.raises(UserError, match="was started"), x.env.cr.savepoint():
        _callout(x, x.emp_u, planned)
    oc = _oncall(x, day + timedelta(days=2))
    with pytest.raises(ValidationError, match="not on call"), x.env.cr.savepoint():
        _callout(x, x.emp_u, oc, h_from=10, h_to=12)
    with pytest.raises(AccessError), x.env.cr.savepoint():
        _callout(x, x.col_u, oc)  # a colleague records nothing on someone else's on-call
    co = _callout(x, x.emp_u, oc)
    assert (co.state, co.hours, co.employee_id) == ("draft", 3.0, x.e_emp)
    assert co.name.startswith("CALL/")
    with pytest.raises(ValidationError, match="overlaps"), x.env.cr.savepoint():
        _callout(x, x.emp_u, oc, h_from=22, h_to=23)
    with pytest.raises(UserError, match="changes only through its workflow"), x.env.cr.savepoint():
        co.with_user(x.emp_u).write({"state": "verified"})
    co.with_user(x.emp_u).action_submit()
    assert co.state == "submitted" and assignees(x, co) == x.mgr_u
    with pytest.raises(UserError), x.env.cr.savepoint():
        co.with_user(x.emp_u).action_inbox_approve()
    with pytest.raises(UserError), x.env.cr.savepoint():
        co.with_user(x.mgr_u).action_approve()  # direct, not from the routed task
    co.with_user(x.mgr_u).action_inbox_approve()
    assert (co.state, co.verified_by_id) == ("verified", x.mgr_u)
    with pytest.raises(UserError, match="only in draft"), x.env.cr.savepoint():
        co.with_user(x.emp_u).write({"description": "something else"})
    with pytest.raises(UserError, match="cannot be cancelled"), x.env.cr.savepoint():
        co.with_user(x.emp_u).action_cancel()


def test_callout_recorded_by_a_supervisor_is_never_verified_by_him_or_the_person_on_call(x):
    oc = _oncall(x, fields.Date.today() + timedelta(days=9))
    co = _callout(x, x.sup_u, oc)
    co.with_user(x.sup_u).action_submit()
    who = assignees(x, co)
    assert who and x.sup_u not in who and x.emp_u not in who
    with pytest.raises(UserError, match="State why"), x.env.cr.savepoint():
        co.with_user(x.mgr_u).action_reject(reason=" ")
    co.with_user(x.mgr_u).action_reject(reason="No ticket was raised for this call")
    assert (co.state, co.rejection_reason) == ("rejected", "No ticket was raised for this call")


# ======================================================================= capacity
def _branch(c):
    entity = c.env["fix.entity"].create(
        {"code": "M55CE", "legal_name": "M55C Entity", "company_id": c.env.company.id}
    )
    return c.env["fix.branch"].create(
        {
            "code": "M55CB",
            "name": "M55C Branch",
            "entity_id": entity.id,
            "operating_unit_id": c.ou.id,
        }
    )


def test_capacity_is_measured_from_the_roster_and_a_gap_alerts_supervisors(x):
    branch = _branch(x)
    d1 = fields.Date.today() + timedelta(days=20)
    d2 = d1 + timedelta(days=1)
    Slot = x.env["fix.roster.slot"]
    slots = Slot
    for emp in (x.e_emp, x.e_col):
        for d in (d1, d2):
            slots |= Slot.create(
                {"employee_id": emp.id, "date": d, "shift_id": x.shift.id, "branch_id": branch.id}
            )
    leave_slot = slots.filtered(lambda s: s.employee_id == x.e_col and s.date == d2)
    leave_slot._guarded().write({"on_leave": True})
    comp = x.env["fix.competency"].create({"code": "M55C-AC", "name": "M55C AC Repair"})
    x.env["fix.certification"].create(
        {
            "employee_id": x.e_emp.id,
            "competency_id": comp.id,
            "issued_on": d1 - timedelta(days=30),
            "expires_on": d2 + timedelta(days=300),
        }
    )
    vals = {
        "branch_id": branch.id,
        "date_from": d1,
        "date_to": d2,
        "demand_hours": 40.0,
        "demand_basis": "Eid campaign, last year's job volume plus 10%",
    }
    with pytest.raises(AccessError), x.env.cr.savepoint():
        x.env["fix.capacity.forecast"].with_user(x.emp_u).create(vals)
    F = x.env["fix.capacity.forecast"].with_user(x.sup_u)
    with pytest.raises(UserError, match="changes only through its workflow"), x.env.cr.savepoint():
        F.create(dict(vals, available_hours=999.0))
    fc = F.create(vals)
    fc.action_measure()
    assert (fc.rostered_hours, fc.leave_hours, fc.available_hours, fc.people_count) == (
        32.0,
        8.0,
        24.0,
        2,
    )
    assert (fc.gap_hours, fc.gap_flag) == (16.0, True)
    skilled = F.create(dict(vals, competency_id=comp.id))
    skilled.action_measure()
    assert (skilled.rostered_hours, skilled.available_hours, skilled.people_count) == (
        16.0,
        16.0,
        1,
    )
    fc.action_publish()
    assert fc.state == "published" and fc.published_by_id == x.sup_u
    todo = (
        x.env["mail.activity"]
        .sudo()
        .search(
            [("res_model", "=", fc._name), ("res_id", "=", fc.id), ("user_id", "=", x.sup_u.id)]
        )
    )
    assert todo and "Capacity gap" in todo[0].summary
    with pytest.raises(UserError, match="final"), x.env.cr.savepoint():
        fc.write({"demand_hours": 10.0})
    with pytest.raises(UserError, match="figures are what was published"), x.env.cr.savepoint():
        fc.action_measure()
    again = F.create(dict(vals, demand_hours=20.0))
    again.action_publish()
    assert (fc.state, fc.superseded_by_id, again.gap_flag) == ("superseded", again, False)
    with pytest.raises(ValidationError, match="at most"), x.env.cr.savepoint():
        F.create(dict(vals, date_to=d1 + timedelta(days=120)))


# ======================================================================= timesheets
def _attend(c, day, h_in, h_out, emp=None):
    return c.env["fix.attendance.record"].create(
        {
            "employee_id": (emp or c.e_emp).id,
            "check_in": dt(day, h_in),
            "check_out": dt(day, h_out),
            "source": "biometric",
        }
    )


def _line(c, user, day, hours, **kw):
    vals = {
        "employee_id": c.e_emp.id,
        "date": day,
        "hours": hours,
        "cost_centre": "CC-SVC",
        "description": "Preventive maintenance visit",
    }
    vals.update(kw)
    return c.env["fix.timesheet.line"].with_user(user).create(vals)


def test_timesheet_allocates_only_verified_attended_hours(x):
    day = fields.Date.today() - timedelta(days=1)
    _attend(x, day, 9, 17)
    with pytest.raises(ValidationError, match="Allocate the time"), x.env.cr.savepoint():
        _line(x, x.emp_u, day, 2, cost_centre=False)
    with pytest.raises(AccessError), x.env.cr.savepoint():
        _line(x, x.col_u, day, 2)  # a colleague does not book someone else's time
    a = _line(x, x.emp_u, day, 5)
    assert a.attended_hours == 8.0
    a.action_submit()
    b = _line(x, x.emp_u, day, 4)
    with pytest.raises(UserError, match="already allocated"), x.env.cr.savepoint():
        b.action_submit()
    b.write({"hours": 3})
    b.action_submit()
    none_day = day - timedelta(days=3)
    c_line = _line(x, x.emp_u, none_day, 1)
    with pytest.raises(UserError, match="no verified attendance"), x.env.cr.savepoint():
        c_line.action_submit()
    assert assignees(x, a) == x.mgr_u
    with pytest.raises(UserError), x.env.cr.savepoint():
        a.with_user(x.emp_u).action_inbox_approve()
    a.with_user(x.mgr_u).action_inbox_approve()
    assert (a.state, a.decided_by_id) == ("approved", x.mgr_u)
    with pytest.raises(UserError, match="only in draft"), x.env.cr.savepoint():
        a.with_user(x.emp_u).write({"hours": 1})
    with pytest.raises(UserError, match="changes only through its workflow"), x.env.cr.savepoint():
        b.with_user(x.emp_u).write({"state": "approved"})


def test_timesheet_defaults_the_cost_centre_and_respects_the_lock(x):
    x.e_emp.fix_cost_centre = "CC-EMP"
    day = date(2026, 1, 14)
    _attend(x, day, 9, 17)
    ln = _line(x, x.emp_u, day, 2, cost_centre=False)
    assert ln.cost_centre == "CC-EMP"
    lock = (
        x.env["fix.attendance.lock"]
        .with_user(x.sup_u)
        .create(
            {"name": "M55C Jan", "period_start": date(2026, 1, 1), "period_end": date(2026, 1, 31)}
        )
    )
    lock.action_lock()
    with pytest.raises(UserError, match="locked attendance period"), x.env.cr.savepoint():
        ln.action_submit()
    with pytest.raises(UserError, match="locked attendance period"), x.env.cr.savepoint():
        _line(x, x.emp_u, day, 1)


# ======================================================================= workspace
def test_the_workspace_forms_create_each_record_and_refuse_stamps(x, p03):
    oc = _oncall(x, fields.Date.today() + timedelta(days=30))
    day = oc.date_from.date() + timedelta(days=1)
    # the form posts the user's wall-clock time: 01:00-03:00 in Dhaka (UTC+6)
    # is 19:00-21:00 UTC of the evening the on-call started
    x.emp_u.tz = "Asia/Dhaka"
    res = p03(x.emp_u).write(
        model="fix.oncall.callout",
        record_id=False,
        values={
            "oncall_id": oc.id,
            "called_at": fields.Datetime.to_string(dt(day, 1)),
            "finished_at": fields.Datetime.to_string(dt(day, 3)),
            "description": "Router reset at the customer site",
        },
    )
    assert res.get("id") and not res.get("error"), res
    co = x.env["fix.oncall.callout"].browse(res["id"])
    res = p03(x.emp_u).write(
        model="fix.oncall.callout", record_id=co.id, values={"state": "verified"}
    )
    co.invalidate_recordset()
    assert co.state == "draft", res
    attended = fields.Date.today() - timedelta(days=2)
    _attend(x, attended, 9, 13)
    res = p03(x.emp_u).write(
        model="fix.timesheet.line",
        record_id=False,
        values={
            "employee_id": x.e_emp.id,
            "date": fields.Date.to_string(attended),
            "hours": 2,
            "cost_centre": "CC-SVC",
            "description": "Workshop bench repair",
        },
    )
    assert res.get("id") and not res.get("error"), res
    res = p03(x.emp_u).write(
        model="fix.capacity.forecast",
        record_id=False,
        values={"branch_id": False, "demand_hours": 1},
    )
    assert res.get("error"), res  # a plain user does not forecast capacity


def test_deployment_acl_rules_sequences_and_surfaces(x):
    from odoo.addons.cd_p03_portal.controllers.a09 import m55

    env = x.env
    Access = env["ir.model.access"]
    for model, perms in (
        ("fix.oncall.callout", (True, True, True)),
        ("fix.capacity.forecast", (True, False, False)),
        ("fix.timesheet.line", (True, True, True)),
    ):
        row = Access.search(
            [("model_id.model", "=", model), ("group_id", "=", env.ref("base.group_user").id)]
        )
        assert (row.perm_read, row.perm_write, row.perm_create) == perms, model
        assert not Access.search_count([("model_id.model", "=", model), ("perm_unlink", "=", True)])
    for xmlid in ("cd_attendance.rule_oncall_callout_own", "cd_attendance.rule_timesheet_line_own"):
        assert not env.ref(xmlid).groups  # global rules
    for code in ("fix.oncall.callout", "fix.capacity.forecast"):
        assert env["ir.sequence"].search_count([("code", "=", code)])
    assert {"action_measure", "action_publish"} == m55.SURFACES["fix.capacity.forecast"]["actions"]
