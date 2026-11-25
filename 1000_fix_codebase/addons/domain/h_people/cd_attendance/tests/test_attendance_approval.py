"""M55 AUT-WFM-02: approval of flagged mobile clock-ins on the live ORM
(``odoo_env``: fix_test, rolled back after every test).

These run as the SUPERUSER, who decides a record directly (data repair). Who
may decide as a person - the line manager, then the attendance officers, never
the requester or the employee - is tested as non-admin users in
test_a09_attendance_controls.py.

Working time is hand-computed against BLA 2006 (8h standard day, s.100)."""

import json
from contextlib import contextmanager
from datetime import date, datetime

import pytest
from odoo.exceptions import UserError


@contextmanager
def _refused(env, exc, match=None):
    """Expect ``exc``; the failed operation is rolled back (flushing savepoint)."""
    with pytest.raises(exc, match=match) as info, env.cr.savepoint():
        yield info
    env.invalidate_all()


@pytest.fixture
def emp(odoo_env):
    return odoo_env["hr.employee"].create({"name": "Flagged Tech"})


def _clock(env, emp, day, hours=10, state="pending", reason="position outside the geofence"):
    """A mobile clock-in of ``hours`` on ``day`` (09:00 start)."""
    return env["fix.attendance.record"].create(
        {
            "employee_id": emp.id,
            "check_in": datetime(day.year, day.month, day.day, 9, 0),
            "check_out": datetime(day.year, day.month, day.day, 9 + hours, 0),
            "source": "mobile",
            "geofence_result": "outside",
            "approval_state": state,
            "approval_reason": reason,
        }
    )


def _events(env, event_type, rec):
    rows = env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate_id", "=", rec.id)]
    )
    return [json.loads(r.payload) for r in rows]


def test_an_attendance_officer_approves_a_flagged_clock_in(odoo_env, emp):
    rec = _clock(odoo_env, emp, date(2026, 1, 12))
    # 10h: 10 worked, 2 recorded overtime beyond the 8h day; none payable
    # without an approved overtime request (BRU-WFM-02)
    assert (rec.worked_hours, rec.recorded_overtime_hours, rec.overtime_hours) == (10.0, 2.0, 0.0)
    rec.action_approve()
    assert (rec.approval_state, rec.approved_by, bool(rec.approved_at)) == (
        "approved",
        odoo_env.user,
        True,
    )
    assert (rec.worked_hours, rec.recorded_overtime_hours) == (10.0, 2.0)
    assert "Flagged clock-in approved" in rec.message_ids.mapped("body")[0]
    assert _events(odoo_env, "attendance.approved", rec) == [
        {"employee": "Flagged Tech", "reason": "position outside the geofence"}
    ]


def test_a_rejected_clock_in_is_kept_but_is_no_worked_time(odoo_env, emp):
    rec = _clock(odoo_env, emp, date(2026, 1, 13))
    rec.action_reject(reason="Not on site")
    assert rec.approval_state == "rejected"
    assert (rec.worked_hours, rec.overtime_hours) == (0.0, 0.0)
    assert "Flagged clock-in rejected: Not on site" in rec.message_ids.mapped("body")[0]
    assert _events(odoo_env, "attendance.rejected", rec)
    plain = _clock(odoo_env, emp, date(2026, 1, 14))
    plain.action_reject()
    assert "rejected: no reason given" in plain.message_ids.mapped("body")[0]


def test_decisions_are_tracked_in_the_chatter(odoo_env, emp):
    rec = _clock(odoo_env, emp, date(2026, 1, 15))
    odoo_env.cr.flush()  # tracking is finalised per flush
    rec.action_approve()
    odoo_env.cr.flush()
    tracked = rec.message_ids.tracking_value_ids.filtered(
        lambda t: t.field_id.name == "approval_state"
    )
    assert [(t.old_value_char, t.new_value_char) for t in tracked] == [
        ("Pending Approval", "Approved")
    ]


def test_only_pending_clock_ins_are_decided(odoo_env, emp):
    clean = _clock(odoo_env, emp, date(2026, 1, 16), state="not_required", reason=False)
    with _refused(odoo_env, UserError, "is not pending approval \\(it is not_required\\)"):
        clean.action_approve()
    done = _clock(odoo_env, emp, date(2026, 1, 17))
    done.action_approve()
    with _refused(odoo_env, UserError, "it is approved"):
        done.action_reject()


def test_a_person_decides_only_a_routed_record(odoo_env, emp):
    """Even an attendance officer does not decide a record directly: it is
    routed first, and then only the task's assignee decides."""
    rec = _clock(odoo_env, emp, date(2026, 1, 19))
    officer = (
        odoo_env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "Desk Officer",
                "login": "officer@attendance.test",
                "group_ids": [
                    (4, odoo_env.ref("base.group_user").id),
                    (4, odoo_env.ref("hr_attendance.group_hr_attendance_user").id),
                ],
            }
        )
    )
    with _refused(odoo_env, UserError, "has not been routed"):
        rec.with_user(officer).action_approve()
    assert rec.approval_state == "pending"
    rec.action_request_regularisation()
    task = (
        odoo_env["fix.workflow.task"]
        .search([("res_model", "=", "fix.attendance.regularisation"), ("state", "=", "pending")])
        .filtered(lambda t: t.assigned_user_id == officer)
    )
    assert task
    rec.with_user(officer).action_approve()
    assert (rec.approval_state, rec.approved_by) == ("approved", officer)


def test_pending_in_period_bounds_and_company(odoo_env, emp):
    first = _clock(odoo_env, emp, date(2026, 1, 1))
    last = _clock(odoo_env, emp, date(2026, 1, 31))  # the whole last day counts
    _clock(odoo_env, emp, date(2026, 2, 1))  # next period
    _clock(odoo_env, emp, date(2026, 1, 20), state="approved")
    model = odoo_env["fix.attendance.record"]
    jan = model.pending_in_period(date(2026, 1, 1), date(2026, 1, 31))
    assert jan == first | last
    other_company = odoo_env["res.company"].create({"name": "Attendance Sister Co"})
    assert not model.pending_in_period(date(2026, 1, 1), date(2026, 1, 31), other_company)
    assert model.pending_in_period(date(2026, 1, 1), date(2026, 1, 31), odoo_env.company) == jan


def test_a_period_with_pending_clock_ins_cannot_be_locked(odoo_env, emp):
    """BRU-WFM-01: only VERIFIED attendance is locked - a pending clock-in could
    never be decided afterwards (locked records are immutable)."""
    rec = _clock(odoo_env, emp, date(2026, 1, 21))
    lock = odoo_env["fix.attendance.lock"].create(
        {"name": "Jan 2026", "period_start": date(2026, 1, 1), "period_end": date(2026, 1, 31)}
    )
    with _refused(odoo_env, UserError) as err:
        lock.action_lock()
    assert str(err.value) == (
        "Attendance period Jan 2026 has 1 clock-in(s) pending approval - approve or reject "
        f"them before locking: {rec.display_label}"
    )
    assert lock.state == "draft"
    rec.action_reject(reason="Spoofed position")
    lock.action_lock()
    assert lock.state == "locked"
