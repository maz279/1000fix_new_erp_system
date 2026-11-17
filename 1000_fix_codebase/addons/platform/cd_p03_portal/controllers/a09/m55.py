# A09 · M55 Time, Attendance & Scheduling — surfaces, packs and KPIs over the
# attendance records, rosters, shift patterns, devices, leave requests, holiday
# calendar and on-call shifts.
import datetime

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


def attendance_summary(env, date_from=None, date_to=None, **params):
    """Attendance summary per employee for the period."""
    today = datetime.date.today()
    start = date_from or str(today.replace(day=1))
    end = date_to or str(today)
    records = env["fix.attendance.record"].search(
        [("check_in", ">=", start + " 00:00:00"), ("check_in", "<=", end + " 23:59:59")]
    )
    rows = {}
    for rec in records:
        key = rec.employee_id.id
        row = rows.setdefault(
            key,
            {
                "employee": rec.employee_id.name,
                "days": 0,
                "hours": 0.0,
                "recorded_ot": 0.0,
                "overtime": 0.0,
                "flagged": 0,
            },
        )
        row["days"] += 1
        row["hours"] += rec.worked_hours or 0.0
        row["recorded_ot"] += rec.recorded_overtime_hours or 0.0
        row["overtime"] += rec.overtime_hours or 0.0
        if rec.approval_state in ("pending",):
            row["flagged"] += 1
    out = sorted(rows.values(), key=lambda r: -r["hours"])
    for r in out:
        r["hours"] = round(r["hours"], 2)
        r["recorded_ot"] = round(r["recorded_ot"], 2)
        r["overtime"] = round(r["overtime"], 2)
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
            "Hours are the recorded check-in/out pairs, counted per employee and day. Recorded "
            "overtime is beyond the statutory 8-hour day (BLA 2006 s.100); payable overtime is "
            "the part an approved overtime request covers, at most 2 h a day (BRU-WFM-02).",
            "You see your own attendance and your direct reports'; HR, payroll and the "
            "attendance roles see the company's.",
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
            "overtime request was approved; the rest is recorded, not payable (BRU-WFM-02)."
        ],
        totals={
            "employee": "Total",
            "hours": round(sum(r["hours"] for r in rows), 2),
            "recorded_ot": round(sum(r["recorded_ot"] for r in rows), 2),
            "overtime": round(sum(r["overtime"] for r in rows), 2),
        },
        empty="No overtime recorded in the period.",
    )


def leave_utilisation(env, date_from=None, date_to=None, **params):
    """Leave utilisation: requested vs approved days by leave type, for leave
    starting in the period (default: this calendar year)."""
    today = datetime.date.today()
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
    today = datetime.date.today()
    start = date_from or str(today - datetime.timedelta(days=30))
    end = date_to or str(today)
    slots = env["fix.roster.slot"].search([("date", ">=", start), ("date", "<=", end)])
    records = env["fix.attendance.record"].search(
        [("check_in", ">=", start + " 00:00:00"), ("check_in", "<=", end + " 23:59:59")]
    )
    # Count punches per EMPLOYEE per day: a roster slot is one employee's day,
    # so a company-wide daily count would mark every slot uncovered.
    by_day = {}
    for rec in records:
        key = (rec.employee_id.id, rec.check_in.date())
        by_day[key] = by_day.get(key, 0) + 1
    rows = []
    for slot in slots:
        present = by_day.get((slot.employee_id.id, slot.date), 0)
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
    sick taken this calendar year, for the employees the caller may read."""
    today = datetime.date.today()
    as_of = datetime.date.fromisoformat(date_to) if date_to else today
    year = as_of.year
    leaves = env["fix.leave.request"].search(
        [
            ("state", "=", "approved"),
            ("date_from", ">=", datetime.date(year, 1, 1)),
            ("date_from", "<=", datetime.date(year, 12, 31)),
        ]
    )
    rows = []
    for emp in env["hr.employee"].search([]):
        mine = leaves.filtered(lambda r, e=emp: r.employee_id == e)

        def taken(code, mine=mine):
            return sum(mine.filtered(lambda r, c=code: r.leave_type_id.code == c).mapped("days"))

        rows.append(
            {
                "employee": emp.name,
                "annual_unused": round(emp._fix_unused_annual_leave_days(as_of), 1),
                "annual_taken": taken("annual"),
                "casual_taken": taken("casual"),
                "sick_taken": taken("sick"),
            }
        )
    rows.sort(key=lambda r: r["employee"] or "")
    return _pack(
        "Leave Balances — %s" % as_of,
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
            "Annual leave: 1 day per 18 days worked in each completed service year, after one "
            "year of service, carried forward up to the leave type limit (BLA s.117). The days "
            "worked are counted on the company's chosen basis.",
            "Casual (s.115) and sick (s.116) leave are per calendar year and not carried forward.",
        ],
        empty="No employees visible to you.",
    )


REPORTS = {
    "attendance_summary": attendance_summary,
    "overtime_analysis": overtime_analysis,
    "leave_utilisation": leave_utilisation,
    "leave_balances": leave_balances,
    "roster_vs_actual": roster_vs_actual,
    "coverage_gaps": coverage_gaps,
}


def kpis(env):
    today = datetime.date.today()
    records = env["fix.attendance.record"].search(
        [
            ("check_in", ">=", str(today) + " 00:00:00"),
            ("check_in", "<=", str(today) + " 23:59:59"),
        ]
    )
    flagged = env["fix.attendance.record"].search([("approval_state", "=", "pending")])
    rosters = env["fix.roster.slot"].search([("date", "=", str(today))])
    leave = env["fix.leave.request"].search([("state", "in", ("submitted",))])
    geo = len([r for r in records if r.source in ("mobile", "mobile_offline")])
    public_holidays = env["fix.hr.holiday"].search(
        [("date", ">=", str(today.replace(month=1, day=1)))]
    )
    return {
        "attendance_today": len(records),
        "exceptions_pending": len(flagged),
        # M55-11 / G2: approved overtime REQUESTS this month, not approved geofence flags
        "overtime_preapproved": env["fix.overtime.request"].search_count(
            [("state", "=", "approved"), ("date", ">=", str(today.replace(day=1)))]
        )
        if "fix.overtime.request" in env
        else 0,
        "roster_coverage": round(
            (len(rosters) - len(rosters.filtered(lambda r: r.on_leave))) / len(rosters) * 100.0, 1
        )
        if rosters
        else 0.0,
        "leave_pending": len(leave),
        "geofence_clockins": geo,
        "holidays": len(public_holidays),
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
