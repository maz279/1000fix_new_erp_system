# A09 ERP audit fix program, builder B4 — M55 valuation-side tests.
#
#   M55-F23  the weekly payable-overtime ceiling: max(weekly_limit - 48, 0)
#            of the working-time rule version in force; no limit = no cap; the
#            excess stays recorded-not-payable
#   M55-F3   festival-typed holiday hours (fix.attendance.record.festival_hours)
#            and the payroll helpers B1a reads:
#              fix.attendance.record._fix_payroll_rest_day_hours
#              fix.attendance.record._fix_payroll_holiday_hours
#              fix.attendance.record._fix_payroll_festival_hours
#              fix.oncall.callout._fix_payroll_verified_callout_hours
#   M55-F4   fix.leave.request._fix_payroll_unpaid_leave_days (reads the
#            B2b is_unpaid flag defensively)
from datetime import date, datetime, timedelta

import pytest

WEEK = date(2026, 3, 2)  # a Monday


def _record(env, emp, day, hour_in, hour_out=None):
    vals = {"employee_id": emp.id, "check_in": datetime(day.year, day.month, day.day, hour_in)}
    if hour_out is not None:
        vals["check_out"] = datetime(day.year, day.month, day.day, hour_out)
    return env["fix.attendance.record"].create(vals)


def _approve_ot(env, emp, day, hours, rest_day=False):
    """An approved overtime request for the day (superuser fixture: the
    approval WORKFLOW is test_a09_attendance_controls.py's subject)."""
    req = env["fix.overtime.request"].create(
        {
            "employee_id": emp.id,
            "date": day,
            "hours": hours,
            "reason": "rush job",
            "rest_day_work": rest_day,
        }
    )
    req._guarded().write({"state": "approved", "approved_hours": req.hours})
    req._fix_revalue()
    return req


@pytest.fixture
def emp(odoo_env):
    return odoo_env["hr.employee"].create({"name": "B4 OT Week"})


# --- M55-F23: the weekly payable-overtime ceiling -----------------------------------


def test_a_week_of_two_hour_days_pays_only_the_weekly_ceiling(odoo_env, emp):
    """Seven 10 h days with an approved 2 h request each: 14 h recorded-and-
    approved would be 62 h paid — the s.102 ceiling (rule v1: 60 h) allows
    60 - 48 = 12 h payable; the rest stays recorded-not-payable."""
    recs = []
    for i in range(7):
        day = WEEK + timedelta(days=i)
        recs.append(_record(odoo_env, emp, day, 9, 19))
        _approve_ot(odoo_env, emp, day, 2)
    payable = [round(r.overtime_hours, 2) for r in recs]
    unapproved = [round(r.unapproved_overtime_hours, 2) for r in recs]
    # the week's budget is spent in check-in order: six days at 2 h, day 7 at 0
    assert payable == [2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 0.0]
    assert unapproved == [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0]
    assert round(sum(payable), 2) == 12.0  # max(60 - 48, 0)


def test_the_weekly_cap_redistributes_when_a_day_leaves_the_week(odoo_env, emp):
    """The ceiling is a WEEK budget: cancelling one day's approval must free
    its payable hours for the rest of the week (the whole ISO week is
    re-valued, so the split never goes stale)."""
    recs = []
    requests = []
    for i in range(7):
        day = WEEK + timedelta(days=i)
        recs.append(_record(odoo_env, emp, day, 9, 19))
        requests.append(_approve_ot(odoo_env, emp, day, 2))
    assert round(sum(r.overtime_hours for r in recs), 2) == 12.0
    # the first day's request is cancelled: its 2 h return to the week
    requests[0]._guarded().write({"state": "cancelled"})
    requests[0]._fix_revalue()
    for rec in recs:
        rec.invalidate_recordset()
    assert round(recs[0].overtime_hours, 2) == 0.0
    assert round(sum(r.overtime_hours for r in recs), 2) == 12.0
    # and day 7 now earns the freed hours (check-in order)
    assert round(recs[6].overtime_hours, 2) == 2.0


def test_a_rule_version_without_a_weekly_limit_caps_the_day_only(odoo_env, emp):
    """A rule version with weekly_limit_hours = 0 (not checked) means NO
    weekly cap: the same week pays its full 14 h (the daily 2 h cap stands)."""
    for i in range(7):
        day = WEEK + timedelta(days=i)
        _record(odoo_env, emp, day, 9, 19)
        _approve_ot(odoo_env, emp, day, 2)
    recs = odoo_env["fix.attendance.record"].search(
        [
            ("employee_id", "=", emp.id),
            ("check_in", ">=", datetime(2026, 3, 2)),
            ("check_in", "<", datetime(2026, 3, 9)),
        ]
    )
    assert round(sum(r.overtime_hours for r in recs), 2) == 12.0  # rule v1: 60 h
    odoo_env["fix.working.time.rule"].create(
        {
            "company_id": odoo_env.company.id,
            "date_from": date(2026, 3, 2),
            "weekly_limit_hours": 0.0,
            "basis": "B4 test: weekly limit not checked for this span",
        }
    )
    recs.invalidate_recordset()
    assert round(sum(r.overtime_hours for r in recs), 2) == 14.0  # no weekly cap


def test_a_single_rest_day_keeps_its_ten_payable_hours(odoo_env, emp):
    """The rest-day 10 h payable cap (s.100/108) still applies on its own: one
    rest day in an otherwise empty week is under every weekly ceiling."""
    day = WEEK + timedelta(days=6)  # the Sunday of the test week
    rec = _record(odoo_env, emp, day, 9, 19)
    rec.action_mark_rest_day()
    _approve_ot(odoo_env, emp, day, 10, rest_day=True)
    rec.invalidate_recordset()
    assert (rec.rest_day_hours, round(rec.overtime_hours, 2)) == (10.0, 10.0)


# --- M55-F3: festival hours and the payroll helpers ----------------------------------


def test_festival_typed_holidays_carry_festival_hours(odoo_env, emp):
    Holiday = odoo_env["fix.hr.holiday"]
    day_f = date(2026, 3, 10)
    day_p = date(2026, 3, 11)
    Holiday.create({"name": "Festival Day", "date": day_f, "holiday_type": "festival"})
    Holiday.create({"name": "Plain Public Day", "date": day_p, "holiday_type": "public"})
    on_festival = _record(odoo_env, emp, day_f, 9, 17)
    on_public = _record(odoo_env, emp, day_p, 9, 17)
    assert (on_festival.holiday_hours, on_festival.festival_hours) == (8.0, 8.0)
    assert (on_public.holiday_hours, on_public.festival_hours) == (8.0, 0.0)
    # a tentative festival row is no confirmed holiday at all
    Holiday.create(
        {
            "name": "Moon Festival",
            "date": date(2026, 3, 12),
            "holiday_type": "festival",
            "tentative": True,
        }
    )
    on_tentative = _record(odoo_env, emp, date(2026, 3, 12), 9, 17)
    assert (on_tentative.holiday_hours, on_tentative.festival_hours) == (0.0, 0.0)


def test_payroll_helpers_read_decided_records_only(odoo_env, emp):
    Record = odoo_env["fix.attendance.record"]
    Holiday = odoo_env["fix.hr.holiday"]
    rest = date(2026, 3, 2)
    festival = date(2026, 3, 3)
    Holiday.create({"name": "Festival Day", "date": festival, "holiday_type": "festival"})
    r_rest = _record(odoo_env, emp, rest, 9, 19)
    r_rest.action_mark_rest_day()
    _record(odoo_env, emp, festival, 9, 17)  # the festival day itself
    # a PENDING festival record pays nothing (BRU-WFM-01: decided attendance only)
    r_pending = _record(odoo_env, emp, date(2026, 3, 4), 9, 17)
    Holiday.create({"name": "Festival 2", "date": date(2026, 3, 4), "holiday_type": "festival"})
    r_pending._guarded().write({"approval_state": "pending"})
    period = (date(2026, 3, 1), date(2026, 3, 31))
    assert Record._fix_payroll_rest_day_hours(emp, *period) == 10.0
    # the pending record's holiday hours are excluded (decided records only)
    assert Record._fix_payroll_holiday_hours(emp, *period) == 8.0
    assert Record._fix_payroll_festival_hours(emp, *period) == 8.0
    # a period outside the days reads zero
    assert Record._fix_payroll_rest_day_hours(emp, date(2026, 4, 1), date(2026, 4, 30)) == 0.0


def test_verified_callout_hours_reach_payroll(odoo_env, emp):
    Oncall = odoo_env["fix.hr.oncall"]
    Callout = odoo_env["fix.oncall.callout"]
    shift = odoo_env["fix.shift.template"].create(
        {"name": "B4 Night", "start_hour": 22.0, "end_hour": 6.0}
    )
    oncall = Oncall.create(
        {
            "employee_id": emp.id,
            "shift_id": shift.id,
            "date_from": datetime(2026, 3, 6, 18, 0),
            "date_to": datetime(2026, 3, 7, 6, 0),
        }
    )
    # B4-ops rule: a callout is recorded only on an on-call that has started
    oncall.action_start()
    verified = Callout.create(
        {
            "oncall_id": oncall.id,
            "called_at": datetime(2026, 3, 6, 20, 0),
            "arrived_at": datetime(2026, 3, 6, 21, 0),
            "finished_at": datetime(2026, 3, 6, 23, 0),
            "description": "Data centre power failure",
        }
    )
    draft = Callout.create(
        {
            "oncall_id": oncall.id,
            "called_at": datetime(2026, 3, 6, 23, 30),
            "finished_at": datetime(2026, 3, 7, 1, 0),
            "description": "Follow-up visit",
        }
    )
    verified._guarded().write({"state": "verified"})  # the routed verification is B4-ops'
    assert (verified.state, draft.state) == ("verified", "draft")
    helper = Callout._fix_payroll_verified_callout_hours
    assert helper(emp, date(2026, 3, 1), date(2026, 3, 31)) == 3.0  # called->finished
    assert helper(emp, date(2026, 4, 1), date(2026, 4, 30)) == 0.0


def test_unpaid_leave_days_helper_reads_the_flag_defensively(odoo_env, emp):
    Leave = odoo_env["fix.leave.request"]
    unpaid = odoo_env.ref("cd_hr_core.leave_type_unpaid")  # B2b's seeded LWP type
    paid = odoo_env.ref("cd_hr_core.leave_type_casual")
    Leave.create(
        {
            "employee_id": emp.id,
            "leave_type_id": unpaid.id,
            "date_from": date(2026, 3, 30),
            "date_to": date(2026, 4, 3),
        }
    ).write({"state": "approved"})
    Leave.create(
        {
            "employee_id": emp.id,
            "leave_type_id": paid.id,
            "date_from": date(2026, 3, 10),
            "date_to": date(2026, 3, 11),
        }
    ).write({"state": "approved"})
    helper = Leave._fix_payroll_unpaid_leave_days
    # a leave spanning the period boundary is split at it: 2 of its 5 days
    assert helper(emp, date(2026, 3, 1), date(2026, 3, 31)) == 2
    assert helper(emp, date(2026, 4, 1), date(2026, 4, 30)) == 3
    assert helper(emp, date(2026, 5, 1), date(2026, 5, 31)) == 0
    # a not-yet-approved unpaid leave counts nothing
    Leave.create(
        {
            "employee_id": emp.id,
            "leave_type_id": unpaid.id,
            "date_from": date(2026, 3, 20),
            "date_to": date(2026, 3, 21),
        }
    )
    assert helper(emp, date(2026, 3, 1), date(2026, 3, 31)) == 2
