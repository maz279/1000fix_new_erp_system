# A09 ERP audit fix program, builder B4 — M55 workspace pack / KPI tests.
#
#   UI-F2  leave_balances is an AS-AT pack on the Dhaka business day: a fiscal
#          window offered with a future end (July-June) never labels or counts
#          a future calendar year
#   UI-F3  every M55 pack honours the period the screen offers (two ranges ->
#          different rows), each on its own business date field
#   UI-F8  attendance day windows are the caller's Dhaka calendar days (a UTC
#          19:30 punch is the NEXT Dhaka day), days are distinct worked DAYS
#          (a split shift is one day) and the overtime pack's totals carry the
#          days column
#   UI-F9  roster_coverage is measured against PUNCHES (as the roster-vs-actual
#          report measures it); the served-but-unused `holidays` KPI is gone
#   M55-F12 the statutory_preflight pack reports "N of <floor> statutory
#          festival days typed for <year>"
from datetime import date, datetime, timedelta

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers.a09 import m55


@pytest.fixture
def emp(odoo_env):
    return odoo_env["hr.employee"].create({"name": "B4 Reports"})


def _record(env, emp, check_in, check_out=None):
    vals = {"employee_id": emp.id, "check_in": check_in, "source": "manual"}
    if check_out:
        vals["check_out"] = check_out
    return env["fix.attendance.record"].create(vals)


def _leave(env, emp, code, day_from, day_to, state="approved"):
    leave_type = env["fix.leave.type"].search([("code", "=", code)], limit=1)
    leave = env["fix.leave.request"].create(
        {
            "employee_id": emp.id,
            "leave_type_id": leave_type.id,
            "date_from": day_from,
            "date_to": day_to,
            "reason": "B4 fixture",
        }
    )
    leave.write({"state": state})
    return leave


# --- UI-F8: the Dhaka business day ---------------------------------------------------


def test_attendance_summary_uses_the_dhaka_day_window(odoo_env, emp):
    """A 19:30 UTC punch is 01:30 the NEXT Dhaka day: the same UTC date feeds
    two different Dhaka days, so a UTC-midnight window (the old bug) counts
    it on the wrong day. 2026-11-23 is the shared UTC date here."""
    _record(odoo_env, emp, datetime(2026, 11, 23, 10, 0), datetime(2026, 11, 23, 18, 0))
    _record(odoo_env, emp, datetime(2026, 11, 23, 19, 30), datetime(2026, 11, 24, 1, 30))
    on_23rd = m55.attendance_summary(odoo_env, "2026-11-23", "2026-11-23")
    on_24th = m55.attendance_summary(odoo_env, "2026-11-24", "2026-11-24")
    assert [r["hours"] for r in on_23rd["rows"]] == [8.0]  # only the 10:00 UTC punch
    assert [r["hours"] for r in on_24th["rows"]] == [6.0]  # the 19:30 UTC punch is Dhaka's 24th


def test_a_split_shift_is_one_worked_day(odoo_env, emp):
    _record(
        odoo_env, emp, datetime(2026, 11, 20, 3, 0), datetime(2026, 11, 20, 7, 0)
    )  # 09:00-13:00 Dhaka
    _record(
        odoo_env, emp, datetime(2026, 11, 20, 8, 0), datetime(2026, 11, 20, 13, 0)
    )  # 14:00-19:00 Dhaka
    pack = m55.attendance_summary(odoo_env, "2026-11-20", "2026-11-20")
    assert [(r["days"], r["hours"]) for r in pack["rows"]] == [(1, 9.0)]
    assert pack["totals"]["days"] == 1


def test_overtime_analysis_totals_carry_the_days_column(odoo_env, emp):
    _record(odoo_env, emp, datetime(2026, 11, 20, 3, 0), datetime(2026, 11, 20, 13, 0))  # 10h
    pack = m55.overtime_analysis(odoo_env, "2026-11-20", "2026-11-20")
    assert pack["totals"]["days"] == 1
    assert pack["totals"]["recorded_ot"] == 2.0


# --- UI-F3: each pack honours the offered period -------------------------------------


def test_attendance_summary_honours_the_period(odoo_env, emp):
    _record(odoo_env, emp, datetime(2026, 3, 10, 3, 0), datetime(2026, 3, 10, 13, 0))
    _record(odoo_env, emp, datetime(2026, 4, 10, 3, 0), datetime(2026, 4, 10, 11, 0))
    march = m55.attendance_summary(odoo_env, "2026-03-01", "2026-03-31")
    april = m55.attendance_summary(odoo_env, "2026-04-01", "2026-04-30")
    assert [(r["hours"], r["days"]) for r in march["rows"]] == [(10.0, 1)]
    assert [(r["hours"], r["days"]) for r in april["rows"]] == [(8.0, 1)]


def test_overtime_analysis_honours_the_period(odoo_env, emp):
    _record(odoo_env, emp, datetime(2026, 3, 10, 3, 0), datetime(2026, 3, 10, 13, 0))  # 2h OT
    _record(odoo_env, emp, datetime(2026, 4, 10, 3, 0), datetime(2026, 4, 10, 11, 0))  # none
    march = m55.overtime_analysis(odoo_env, "2026-03-01", "2026-03-31")
    april = m55.overtime_analysis(odoo_env, "2026-04-01", "2026-04-30")
    assert [(r["recorded_ot"]) for r in march["rows"]] == [2.0]
    assert april["rows"] == []


def test_leave_utilisation_honours_the_period(odoo_env, emp):
    _leave(odoo_env, emp, "casual", date(2026, 1, 12), date(2026, 1, 13))
    _leave(odoo_env, emp, "casual", date(2026, 2, 9), date(2026, 2, 10))
    january = m55.leave_utilisation(odoo_env, "2026-01-01", "2026-01-31")
    february = m55.leave_utilisation(odoo_env, "2026-02-01", "2026-02-28")
    assert january["rows"][0]["approved"] == 2
    assert february["rows"][0]["approved"] == 2
    assert january["totals"]["approved"] == 2  # a range never shows the other month's leave


def test_roster_vs_actual_honours_the_period(odoo_env, emp):
    shift = odoo_env["fix.shift.template"].create(
        {"name": "B4 Day", "start_hour": 9.0, "end_hour": 17.0}
    )
    Slot = odoo_env["fix.roster.slot"]
    Slot.create({"employee_id": emp.id, "date": date(2026, 3, 10), "shift_id": shift.id})
    Slot.create({"employee_id": emp.id, "date": date(2026, 4, 10), "shift_id": shift.id})
    march = m55.roster_vs_actual(odoo_env, "2026-03-01", "2026-03-31")
    april = m55.roster_vs_actual(odoo_env, "2026-04-01", "2026-04-30")
    assert [r["date"] for r in march["rows"]] == ["2026-03-10"]
    assert [r["date"] for r in april["rows"]] == ["2026-04-10"]
    # the punches are grouped on the DHAKA day: this 19:30 UTC punch on the
    # 10th belongs to the rostered 11th... of MARCH, so the March 10 slot stays a Gap
    _record(odoo_env, emp, datetime(2026, 3, 10, 19, 30), datetime(2026, 3, 10, 21, 30))
    march = m55.roster_vs_actual(odoo_env, "2026-03-01", "2026-03-31")
    assert march["rows"][0]["status"] == "Gap"
    # a punch inside the slot's own Dhaka day covers it
    _record(odoo_env, emp, datetime(2026, 3, 10, 4, 0), datetime(2026, 3, 10, 12, 0))
    march = m55.roster_vs_actual(odoo_env, "2026-03-01", "2026-03-31")
    assert march["rows"][0]["status"] == "Covered"


def test_coverage_gaps_honours_the_period(odoo_env, emp):
    shift = odoo_env["fix.shift.template"].create(
        {"name": "B4 Day", "start_hour": 9.0, "end_hour": 17.0}
    )
    Slot = odoo_env["fix.roster.slot"]
    Slot.create({"employee_id": emp.id, "date": date(2026, 3, 10), "shift_id": shift.id})
    Slot.create({"employee_id": emp.id, "date": date(2026, 4, 10), "shift_id": shift.id})
    _record(odoo_env, emp, datetime(2026, 4, 10, 4, 0), datetime(2026, 4, 10, 12, 0))
    march = m55.coverage_gaps(odoo_env, "2026-03-01", "2026-03-31")
    april = m55.coverage_gaps(odoo_env, "2026-04-01", "2026-04-30")
    assert [r["date"] for r in march["rows"]] == ["2026-03-10"]  # no punch: the gap
    assert april["rows"] == []


def test_leave_balances_honours_the_period(odoo_env, emp):
    _leave(odoo_env, emp, "annual", date(2025, 6, 2), date(2025, 6, 3))
    _leave(odoo_env, emp, "annual", date(2026, 6, 2), date(2026, 6, 3))
    y2025 = m55.leave_balances(odoo_env, "2025-01-01", "2025-12-31")
    y2026 = m55.leave_balances(odoo_env, "2026-01-01", "2026-12-31")
    row_2025 = next(r for r in y2025["rows"] if r["employee"] == emp.name)
    row_2026 = next(r for r in y2026["rows"] if r["employee"] == emp.name)
    assert row_2025["annual_taken"] == 2
    assert row_2026["annual_taken"] == 2  # each range counts ITS calendar year only
    assert y2025["labels"]["annual_taken"] == "Annual Taken 2025"
    assert y2026["labels"]["annual_taken"] == "Annual Taken 2026"


# --- UI-F2: an as-at pack never counts a future year ----------------------------------


def test_a_future_range_end_never_labels_a_future_year(odoo_env, emp):
    """The workspace sends the July-June fiscal window (today 2026-07-01 to
    2027-06-30): the pack must say 'as at' the Dhaka business day and label
    the calendar year it really counts (2026), never 'Taken 2027'."""
    _leave(odoo_env, emp, "casual", date(2026, 11, 2), date(2026, 11, 3))
    today = fields.Date.context_today(
        odoo_env.user.with_context(tz=odoo_env.context.get("tz") or "Asia/Dhaka")
    )
    pack = m55.leave_balances(odoo_env, "2026-07-01", "2027-06-30")
    assert pack["title"] == "Leave Balances — as at %s" % today
    assert pack["labels"]["annual_taken"] == "Annual Taken %d" % today.year
    assert pack["labels"]["casual_taken"] == "Casual Taken %d (of 10)" % today.year
    row = next(r for r in pack["rows"] if r["employee"] == emp.name)
    if today >= date(2026, 11, 3):
        assert row["casual_taken"] == 2  # the leave started by the as-of day
    # an as-of BEFORE the leave counts it not taken
    earlier = m55.leave_balances(odoo_env, "2026-01-01", "2026-11-01")
    row = next(r for r in earlier["rows"] if r["employee"] == emp.name)
    assert row["casual_taken"] == 0


def test_leave_balances_stay_inside_the_callers_companies(odoo_env, emp):
    other = odoo_env["res.company"].create({"name": "B4 Other Co"})
    odoo_env["hr.employee"].create({"name": "B4 Other Co Worker", "company_id": other.id})
    # the caller's allowed companies: the fixture's administrator is allowed
    # every company, so the scope is pinned here to the test's own company
    scoped = odoo_env(context={**odoo_env.context, "allowed_company_ids": [odoo_env.company.id]})
    pack = m55.leave_balances(scoped)
    names = {r["employee"] for r in pack["rows"]}
    assert "B4 Reports" in names
    assert "B4 Other Co Worker" not in names


# --- UI-F9: KPI honesty ----------------------------------------------------------------


def test_roster_coverage_is_measured_against_punches(odoo_env, emp):
    other = odoo_env["hr.employee"].create({"name": "B4 Second"})
    shift = odoo_env["fix.shift.template"].create(
        {"name": "B4 Day", "start_hour": 9.0, "end_hour": 17.0}
    )
    Slot = odoo_env["fix.roster.slot"]
    today = fields.Date.context_today(
        odoo_env.user.with_context(tz=odoo_env.context.get("tz") or "Asia/Dhaka")
    )
    # emp punches now (always inside today's Dhaka window); `other` only has a
    # roster slot with no punch: 1 of 2 slots punched = 50%
    _record(odoo_env, emp, fields.Datetime.now() - timedelta(hours=1), fields.Datetime.now())
    Slot.create({"employee_id": emp.id, "date": today, "shift_id": shift.id})
    Slot.create({"employee_id": other.id, "date": today, "shift_id": shift.id})
    kpis = m55.kpis(odoo_env)
    assert kpis["roster_coverage"] == 50.0
    assert kpis["attendance_today"] == 1
    # the dead `holidays` payload is gone from the controller
    assert "holidays" not in kpis


# --- M55-F12: the statutory preflight row ----------------------------------------------


def test_statutory_preflight_reports_festival_day_typing(odoo_env):
    from odoo.addons.cd_hr_core.models.fix_hr_core import STATUTORY_LEAVE

    floor = STATUTORY_LEAVE.get("festival", 0)
    year = fields.Date.context_today(
        odoo_env.user.with_context(tz=odoo_env.context.get("tz") or "Asia/Dhaka")
    ).year
    Holiday = odoo_env["fix.hr.holiday"]
    Holiday.create({"name": "B4 Shab-e-Barat", "date": date(year, 3, 1), "holiday_type": "public"})
    pack = m55.statutory_preflight(odoo_env)
    row = next(r for r in pack["rows"] if r["year"] == year)
    assert row["detail"] == "0 of %d statutory festival days typed for %d" % (floor, year)
    assert row["status"] == "ACTION"
    for i in range(max(floor, 1)):
        Holiday.create(
            {"name": "B4 Festival %d" % i, "date": date(year, 4, 1 + i), "holiday_type": "festival"}
        )
    pack = m55.statutory_preflight(odoo_env)
    row = next(r for r in pack["rows"] if r["year"] == year)
    assert row["detail"] == "%d of %d statutory festival days typed for %d" % (
        max(floor, 1),
        floor,
        year,
    )
    assert row["status"] == "READY"
