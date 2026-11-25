# A09 · M55 Time, Attendance & Scheduling — surfaces, packs and KPIs over the
# attendance records, rosters, shift patterns, devices, leave requests, holiday
# calendar and on-call shifts.
#
# UI-F8 / M55-F8: every "today" and every period window in this file is the
# caller's Dhaka business day (fields.Date.context_today / the wall-clock to
# UTC conversion the estate's identity log uses), never datetime.date.today()
# on a UTC process — the attendance day window was 6 h off every evening.
import datetime

from odoo import fields

SURFACES = {
    "fix.attendance.record": {
        "order": "check_in desc",
        "limit": 400,
        # A09 M55-2: a pending record is decided from the approver's own task
        # (action_approve / action_reject decide the CALLER's task, never the
        # record directly); Request Approval routes it.
        "actions": {
            "action_request_regularisation",
            "action_approve",
            "action_reject",
            "action_checkout",
            "action_mark_rest_day",
            "action_clear_rest_day",
        },
    },
    # action_ingest_punch is the device integration's (the webhook
    # /hooks/v1/biometric/<device>); it is not a workspace button. The
    # supervisor rotates the webhook credential (A09 r2, M55-8).
    "fix.biometric.device": {
        "order": "name",
        "limit": 100,
        "actions": {"action_rotate_credential"},
    },
    "fix.biometric.punch.event": {"order": "id desc", "limit": 500, "actions": set()},
    # BRU-WFM-08: the employee gives and withdraws their own consent
    "fix.biometric.consent": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_give", "action_withdraw"},
    },
    "fix.shift.template": {"order": "name", "limit": 100, "actions": set()},
    "fix.roster.slot": {
        "order": "date desc, employee_id",
        "limit": 500,
        # FR-WFM-042/043: the rostered employee asks; a supervisor raises the change
        "actions": {"action_ask_change"},
    },
    # BRU-WFM-12: a roster is published once someone other than the planner
    # approves it; a published slot changes only through a change request
    "fix.roster.publication": {
        "order": "date_from desc, id desc",
        "limit": 200,
        "actions": {"action_submit", "action_inbox_approve", "action_reject", "action_cancel"},
    },
    "fix.roster.change.request": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_submit", "action_inbox_approve", "action_reject", "action_cancel"},
    },
    # T-07: versioned, effective-dated working-time rules
    "fix.working.time.rule": {
        "order": "company_id, date_from desc",
        "limit": 100,
        "actions": set(),
    },
    # FR-WFM-052 / I8: corrections carried into the next payroll
    "fix.attendance.adjustment": {
        "order": "date desc, id desc",
        "limit": 300,
        "actions": {"action_inbox_approve", "action_reject"},
    },
    "fix.leave.request": {
        "order": "date_from desc, id desc",
        "limit": 300,
        # M55-1: approve/reject decide the caller's routed task; the requester
        # submits and cancels (F15)
        "actions": {"action_submit", "action_inbox_approve", "action_reject", "action_cancel"},
    },
    "fix.leave.type": {"order": "name", "limit": 100, "actions": {"action_verify_citation"}},
    "fix.hr.holiday": {"order": "date", "limit": 200, "actions": set()},
    "fix.hr.oncall": {
        "order": "date_from desc, id desc",
        "limit": 300,
        # I9: the allowance is approved by someone other than the person on
        # call and the person who recorded it
        "actions": {
            "action_start",
            "action_complete",
            "action_cancel",
            "action_submit_allowance",
            "action_inbox_approve",
            "action_reject_allowance",
        },
    },
    "fix.attendance.lock": {
        "order": "period_start desc, id desc",
        "limit": 100,
        "actions": {"action_lock", "action_unlock", "action_export_form10_overtime_register"},
    },
    "fix.overtime.request": {
        "order": "date desc, id desc",
        "limit": 300,
        "actions": {"action_submit", "action_inbox_approve", "action_reject", "action_cancel"},
    },
    "fix.attendance.regularisation": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_inbox_approve", "action_inbox_reject"},
    },
    "fix.night.work.consent": {
        "order": "date_from desc",
        "limit": 200,
        "actions": {"action_confirm", "action_withdraw"},
    },
    "fix.leave.accrual": {"order": "employee_id, year_start desc", "limit": 500, "actions": set()},
    # Capture audit 2026-11-17. FR-WFM-044: a callout is verified by someone
    # other than the person on call and the recorder.
    "fix.oncall.callout": {
        "order": "called_at desc, id desc",
        "limit": 300,
        "actions": {"action_submit", "action_inbox_approve", "action_reject", "action_cancel"},
    },
    # FR-WFM-048/049: measured from the roster, published with a gap alert
    "fix.capacity.forecast": {
        "order": "date_from desc, id desc",
        "limit": 200,
        "actions": {"action_measure", "action_publish"},
    },
    # FR-WFM-050: time allocated from verified attendance, line-manager approved
    "fix.timesheet.line": {
        "order": "date desc, id desc",
        "limit": 400,
        "actions": {"action_submit", "action_inbox_approve", "action_reject", "action_cancel"},
    },
}


def _pack(title, cols, labels, rows, notes, totals=None, empty=None):
    return {
        "title": title,
        "cols": cols,
        "labels": labels,
        "rows": rows,
        "totals": totals,
        "notes": notes,
        "empty": empty,
    }


def _today(env):
    """The business day in Asia/Dhaka (the estate's zone; a caller who set
    their own zone keeps it), never the UTC process clock's date (UI-F8)."""
    return fields.Date.context_today(
        env.user.with_context(tz=env.context.get("tz") or env.user.tz or "Asia/Dhaka")
    )


def _day_window(env, day_from, day_to):
    """(start, end) stored-UTC datetime bounds of the caller's CALENDAR days
    [day_from, day_to]: attendance datetimes are stored UTC while the packs'
    periods are the reader's (Dhaka) wall-clock days, so the window must be
    converted (UI-F8); end is exclusive."""
    from odoo.addons.cd_p03_portal.controllers.p03_generic_api import _datetime_to_utc

    start = _datetime_to_utc(env, "%s 00:00:00" % day_from)
    end = _datetime_to_utc(
        env, "%s 00:00:00" % (fields.Date.to_date(day_to) + datetime.timedelta(days=1))
    )
    return start, end


def _local_date(env, moment):
    """The stored (UTC) datetime's date on the reader's (Dhaka) wall clock."""
    from odoo.addons.cd_p03_portal.controllers.p03_generic_api import _datetime_to_local

    return _datetime_to_local(env, moment)[:10]


def attendance_summary(env, date_from=None, date_to=None, **params):
    """Attendance summary per employee for the period (the caller's calendar
    days; default this Dhaka month to today)."""
    today = _today(env)
    start = date_from or str(today.replace(day=1))
    end = date_to or str(today)
    win_start, win_end = _day_window(env, start, end)
    records = env["fix.attendance.record"].search(
        [("check_in", ">=", win_start), ("check_in", "<", win_end)]
    )
    rows = {}
    for rec in records:
        key = rec.employee_id.id
        row = rows.setdefault(
            key,
            {
                "employee": rec.employee_id.name,
                "days": set(),  # distinct worked DAYS: a split shift is one day (UI-F8)
                "hours": 0.0,
                "recorded_ot": 0.0,
                "overtime": 0.0,
                "flagged": 0,
            },
        )
        row["days"].add(_local_date(env, rec.check_in))
        row["hours"] += rec.worked_hours or 0.0
        row["recorded_ot"] += rec.recorded_overtime_hours or 0.0
        row["overtime"] += rec.overtime_hours or 0.0
        if rec.approval_state in ("pending",):
            row["flagged"] += 1
    out = []
    for row in rows.values():
        out.append(
            {
                "employee": row["employee"],
                "days": len(row["days"]),
                "hours": round(row["hours"], 2),
                "recorded_ot": round(row["recorded_ot"], 2),
                "overtime": round(row["overtime"], 2),
                "flagged": row["flagged"],
            }
        )
    out.sort(key=lambda r: -r["hours"])
    return _pack(
        "Attendance Summary — %s to %s" % (start, end),
        ["employee", "days", "hours", "recorded_ot", "overtime", "flagged"],
        {
            "employee": "Employee",
            "days": "Days",
            "hours": "Worked Hours",
            "recorded_ot": "Recorded Overtime",
            "overtime": "Payable Overtime",
            "flagged": "Pending Flags",
        },
        out,
        [
            "Days are distinct worked days per employee (a split shift is one day); "
            "hours are the recorded check-in/out pairs. Recorded overtime is beyond "
            "the statutory 8-hour day (BLA 2006 s.100); payable overtime is the part "
            "an approved overtime request covers, at most 2 h a day (BRU-WFM-02) and "
            "within the weekly ceiling of the working-time rule in force (s.102).",
            "The period is the reader's calendar days (Asia/Dhaka). You see your own "
            "attendance and your direct reports'; HR, payroll and the attendance "
            "roles see the company's.",
        ],
        totals={
            "employee": "Total",
            "days": sum(r["days"] for r in out),
            "hours": round(sum(r["hours"] for r in out), 2),
            "recorded_ot": round(sum(r["recorded_ot"] for r in out), 2),
            "overtime": round(sum(r["overtime"] for r in out), 2),
        },
        empty="No attendance recorded in the period.",
    )


def overtime_analysis(env, date_from=None, date_to=None, **params):
    """Overtime analysis by employee for the period."""
    summary = attendance_summary(env, date_from, date_to)
    rows = [r for r in summary["rows"] if r["recorded_ot"] > 0]
    rows.sort(key=lambda r: -r["overtime"])
    return _pack(
        "Overtime Analysis — %s" % summary["title"].split("— ")[-1],
        ["employee", "days", "hours", "recorded_ot", "overtime"],
        {
            "employee": "Employee",
            "days": "Days",
            "hours": "Worked Hours",
            "recorded_ot": "Recorded Overtime",
            "overtime": "Payable Overtime",
        },
        rows,
        [
            "Overtime is paid at twice the ordinary rate (BLA 2006 s.108) only where an "
            "overtime request was approved; the rest is recorded, not payable "
            "(BRU-WFM-02). Payable overtime is also capped per employee-week at the "
            "weekly limit less 48 h of the rule version in force (M55-F23, s.102)."
        ],
        totals={
            "employee": "Total",
            "days": sum(r["days"] for r in rows),
            "hours": round(sum(r["hours"] for r in rows), 2),
            "recorded_ot": round(sum(r["recorded_ot"] for r in rows), 2),
            "overtime": round(sum(r["overtime"] for r in rows), 2),
        },
        empty="No overtime recorded in the period.",
    )


def leave_utilisation(env, date_from=None, date_to=None, **params):
    """Leave utilisation: requested vs approved days by leave type, for leave
    starting in the period (default: this calendar year)."""
    today = _today(env)
    start = date_from or str(today.replace(month=1, day=1))
    end = date_to or str(today.replace(month=12, day=31))
    requests = env["fix.leave.request"].search(
        [
            ("state", "not in", ("draft", "cancelled")),
            ("date_from", ">=", start),
            ("date_from", "<=", end),
        ]
    )
    groups = {}
    for req in requests:
        key = req.leave_type_id.name
        g = groups.setdefault(key, {"requested": 0, "approved": 0, "rejected": 0, "pending": 0})
        g["requested"] += req.days or 0
        if req.state == "approved":
            g["approved"] += req.days or 0
        elif req.state == "rejected":
            g["rejected"] += req.days or 0
        else:
            g["pending"] += req.days or 0
    rows = [
        {
            "leave_type": k,
            **v,
            "utilisation": round(v["approved"] / v["requested"] * 100.0, 1)
            if v["requested"]
            else 0.0,
        }
        for k, v in sorted(groups.items())
    ]
    return _pack(
        "Leave Utilisation — %s to %s" % (start, end),
        ["leave_type", "requested", "approved", "pending", "rejected", "utilisation"],
        {
            "leave_type": "Leave Type",
            "requested": "Requested Days",
            "approved": "Approved",
            "pending": "Pending",
            "rejected": "Rejected",
            "utilisation": "% Approved",
        },
        rows,
        [
            "Utilisation is approved days over requested days for every submitted, decided or "
            "pending request starting in the period."
        ],
        totals={
            "leave_type": "Total",
            "requested": sum(r["requested"] for r in rows),
            "approved": sum(r["approved"] for r in rows),
            "pending": sum(r["pending"] for r in rows),
            "rejected": sum(r["rejected"] for r in rows),
        },
        empty="No leave requests recorded.",
    )


def roster_vs_actual(env, date_from=None, date_to=None, **params):
    """Roster vs actual: rostered slots compared with attendance recorded that day."""
    today = _today(env)
    start = date_from or str(today - datetime.timedelta(days=30))
    end = date_to or str(today)
    slots = env["fix.roster.slot"].search([("date", ">=", start), ("date", "<=", end)])
    win_start, win_end = _day_window(env, start, end)
    records = env["fix.attendance.record"].search(
        [("check_in", ">=", win_start), ("check_in", "<", win_end)]
    )
    # Count punches per EMPLOYEE per LOCAL day: a roster slot is one employee's
    # day, and the reader's calendar day is the Dhaka one (UI-F8).
    by_day = {}
    for rec in records:
        key = (rec.employee_id.id, _local_date(env, rec.check_in))
        by_day[key] = by_day.get(key, 0) + 1
    rows = []
    for slot in slots:
        present = by_day.get((slot.employee_id.id, str(slot.date)), 0)
        rows.append(
            {
                "date": str(slot.date),
                "employee": slot.employee_id.name,
                "shift": slot.shift_id.name,
                "on_leave": "Yes" if slot.on_leave else "No",
                "actual_punches": present,
                "status": "Covered" if present else ("Leave" if slot.on_leave else "Gap"),
            }
        )
    rows.sort(key=lambda r: r["date"], reverse=True)
    gaps = len([r for r in rows if r["status"] == "Gap"])
    return _pack(
        "Roster vs Actual — %s to %s (%d gaps)" % (start, end, gaps),
        ["date", "employee", "shift", "on_leave", "actual_punches", "status"],
        {
            "date": "Date",
            "employee": "Employee",
            "shift": "Shift",
            "on_leave": "On Leave",
            "actual_punches": "Employee Punches",
            "status": "Status",
        },
        rows,
        [
            "A slot is Covered when that EMPLOYEE has at least one punch that day; a Gap is "
            "a rostered slot with no punch and no approved leave."
        ],
        empty="No rostered slots in the period.",
    )


def coverage_gaps(env, date_from=None, date_to=None, **params):
    """Coverage gaps: rostered slots with no leave and no punch."""
    report = roster_vs_actual(env, date_from, date_to)
    rows = [r for r in report["rows"] if r["status"] == "Gap"]
    return _pack(
        "Coverage Gaps — rostered but neither present nor on leave",
        ["date", "employee", "shift", "on_leave", "actual_punches", "status"],
        {
            "date": "Date",
            "employee": "Employee",
            "shift": "Shift",
            "on_leave": "On Leave",
            "actual_punches": "Punches (day)",
            "status": "Status",
        },
        rows,
        ["Zero-punch rostered days with no approved leave are the real coverage gaps."],
        empty="No coverage gaps in the period.",
    )


def leave_balances(env, date_from=None, date_to=None, **params):
    """Leave balances: annual leave earned (BLA s.117) and used, casual and
    sick taken, for the employees the caller may read.

    An AS-AT snapshot (UI-F2): the figures are as at the as-of date — the
    Dhaka business day, or the offered period's end when that is EARLIER —
    and the calendar year it counts is that as-of date's year, so a fiscal
    July–June window offered with a future end never labels or counts a
    future year. The year's leaves are read once for every employee (F17:
    batched, no per-employee searches) and only leave that has STARTED by the
    as-of date counts as taken."""
    today = _today(env)
    as_of = min(fields.Date.to_date(date_to), today) if date_to else today
    year = as_of.year
    leaves = env["fix.leave.request"].search(
        [
            ("state", "=", "approved"),
            ("date_from", ">=", datetime.date(year, 1, 1)),
            ("date_from", "<=", as_of),
        ]
    )
    taken = {}
    for leave in leaves:
        per_emp = taken.setdefault(leave.employee_id.id, {})
        code = leave.leave_type_id.code
        per_emp[code] = per_emp.get(code, 0) + (leave.days or 0)
    # F17: the s.117 ledger in one batch read, inside the caller's companies
    employees = env["hr.employee"].search([("company_id", "in", env.companies.ids)])
    unused = employees._fix_unused_annual_leave_days_batch(as_of)
    rows = [
        {
            "employee": emp.name,
            "annual_unused": round(unused.get(emp.id, 0.0), 1),
            "annual_taken": taken.get(emp.id, {}).get("annual", 0),
            "casual_taken": taken.get(emp.id, {}).get("casual", 0),
            "sick_taken": taken.get(emp.id, {}).get("sick", 0),
        }
        for emp in employees
    ]
    rows.sort(key=lambda r: r["employee"] or "")
    return _pack(
        "Leave Balances — as at %s" % as_of,
        ["employee", "annual_unused", "annual_taken", "casual_taken", "sick_taken"],
        {
            "employee": "Employee",
            "annual_unused": "Annual Unused (s.117)",
            "annual_taken": "Annual Taken %d" % year,
            "casual_taken": "Casual Taken %d (of 10)" % year,
            "sick_taken": "Sick Taken %d (of 14)" % year,
        },
        rows,
        [
            "As-at snapshot: figures are as at %s; a calendar-year pack counts the "
            "calendar year of the as-of date, and only leave that has started by then "
            "counts as taken." % as_of,
            "Annual leave: 1 day per 18 days worked in each completed service year, after one "
            "year of service, carried forward up to the leave type limit (BLA s.117). The days "
            "worked are counted on the company's chosen basis.",
            "Casual (s.115) and sick (s.116) leave are per calendar year and not carried forward.",
        ],
        empty="No employees visible to you.",
    )


def statutory_preflight(env, date_from=None, date_to=None, **params):
    """M55-F12 (code side): read-only readiness rows before a leave year runs.
    Today's row: how many of the statutory festival days (BLA s.118) the
    holiday calendar has TYPED 'festival' — the days that count against the
    festival entitlement and are paid as festival work (s.118 as amended).
    The holiday list itself is the business's (OWNER): nothing is seeded or
    invented here."""
    from odoo.addons.cd_hr_core.models.fix_hr_core import STATUTORY_LEAVE

    floor = STATUTORY_LEAVE.get("festival", 0)
    holidays = env["fix.hr.holiday"].search([])
    years = sorted({h.date.year for h in holidays if h.date} | {_today(env).year})
    rows = []
    for year in years:
        of_year = holidays.filtered(
            lambda h, y=year: h.date and h.date.year == y and not h.tentative
        )
        typed = len(of_year.filtered(lambda h: h.holiday_type == "festival"))
        rows.append(
            {
                "check": "Statutory festival days typed (BLA s.118)",
                "year": year,
                "detail": "%d of %d statutory festival days typed for %d" % (typed, floor, year),
                "status": "ACTION" if typed < floor else "READY",
            }
        )
    return _pack(
        "M55 Statutory Preflight — holiday calendar readiness",
        ["check", "year", "detail", "status"],
        {
            "check": "Check",
            "year": "Year",
            "detail": "Finding",
            "status": "Status",
        },
        rows,
        [
            "Festival-typed confirmed holidays count against the statutory festival "
            "entitlement and are the days whose worked hours payroll reads as festival "
            "work (fix.attendance.record.festival_hours). A year with fewer typed days "
            "than the statutory floor needs the business's holiday list (OWNER)."
        ],
        empty="No holiday calendar rows visible to you.",
    )


REPORTS = {
    "attendance_summary": attendance_summary,
    "overtime_analysis": overtime_analysis,
    "leave_utilisation": leave_utilisation,
    "leave_balances": leave_balances,
    "roster_vs_actual": roster_vs_actual,
    "coverage_gaps": coverage_gaps,
    "statutory_preflight": statutory_preflight,
}


def kpis(env):
    today = _today(env)
    win_start, win_end = _day_window(env, today, today)
    records = env["fix.attendance.record"].search(
        [("check_in", ">=", win_start), ("check_in", "<", win_end)]
    )
    flagged = env["fix.attendance.record"].search([("approval_state", "=", "pending")])
    rosters = env["fix.roster.slot"].search([("date", "=", str(today))])
    leave = env["fix.leave.request"].search([("state", "in", ("submitted",))])
    geo = len([r for r in records if r.source in ("mobile", "mobile_offline")])
    # UI-F9: coverage measured against PUNCHES, as the roster-vs-actual report
    # measures it — the share of today's rostered slots whose employee has at
    # least one punch that (Dhaka) day. A slot covered by nobody's punch is
    # not covered, whatever the leave flag says.
    punched = {rec.employee_id.id for rec in records}
    covered = len([s for s in rosters if s.employee_id.id in punched])
    return {
        "attendance_today": len(records),
        "exceptions_pending": len(flagged),
        # M55-11 / G2: approved overtime REQUESTS this month, not approved geofence flags
        "overtime_preapproved": env["fix.overtime.request"].search_count(
            [("state", "=", "approved"), ("date", ">=", str(today.replace(day=1)))]
        )
        if "fix.overtime.request" in env
        else 0,
        "roster_coverage": round(covered / len(rosters) * 100.0, 1) if rosters else 0.0,
        "leave_pending": len(leave),
        "geofence_clockins": geo,
        # UI-F9: the `holidays` key was served to no tile — dropped; the
        # statutory holiday readiness lives in the statutory_preflight pack.
        # A09 r2: rosters awaiting publication and corrections awaiting approval
        "rosters_awaiting": env["fix.roster.publication"].search_count(
            [("state", "=", "submitted")]
        )
        if "fix.roster.publication" in env
        else 0,
        "adjustments_open": env["fix.attendance.adjustment"].search_count([("state", "=", "draft")])
        if "fix.attendance.adjustment" in env
        else 0,
    }
