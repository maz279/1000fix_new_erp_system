# A09 · M55 Time, Attendance & Scheduling — surfaces, packs and KPIs over the
# attendance records, rosters, shift patterns, devices, leave requests, holiday
# calendar and on-call shifts.
import datetime

SURFACES = {
    "fix.attendance.record": {
        "order": "check_in desc",
        "limit": 400,
        "actions": {"action_approve", "action_reject", "action_checkout"},
    },
    "fix.biometric.device": {
        "order": "name",
        "limit": 100,
        "actions": {"action_ingest_punch"},
    },
    "fix.shift.template": {"order": "name", "limit": 100, "actions": set()},
    "fix.roster.slot": {
        "order": "date desc, employee_id",
        "limit": 500,
        "actions": set(),
    },
    "fix.leave.request": {
        "order": "date_from desc, id desc",
        "limit": 300,
        "actions": {"action_approve"},
    },
    "fix.leave.type": {"order": "name", "limit": 100, "actions": set()},
    "fix.hr.holiday": {"order": "date", "limit": 200, "actions": set()},
    "fix.hr.oncall": {
        "order": "date_from desc, id desc",
        "limit": 300,
        "actions": {"action_start", "action_complete", "action_cancel"},
    },
    "fix.attendance.lock": {
        "order": "period_start desc, id desc",
        "limit": 100,
        "actions": {"action_lock", "action_unlock", "action_export_form10_overtime_register"},
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
                "overtime": 0.0,
                "flagged": 0,
            },
        )
        row["days"] += 1
        row["hours"] += rec.worked_hours or 0.0
        row["overtime"] += rec.overtime_hours or 0.0
        if rec.approval_state in ("pending",):
            row["flagged"] += 1
    out = sorted(rows.values(), key=lambda r: -r["hours"])
    for r in out:
        r["hours"] = round(r["hours"], 2)
        r["overtime"] = round(r["overtime"], 2)
    return _pack(
        "Attendance Summary — %s to %s" % (start, end),
        ["employee", "days", "hours", "overtime", "flagged"],
        {
            "employee": "Employee",
            "days": "Days",
            "hours": "Worked Hours",
            "overtime": "Overtime Hours",
            "flagged": "Pending Flags",
        },
        out,
        [
            "Hours are the recorded check-in/out pairs; overtime is beyond the statutory "
            "8-hour day (BLA 2006 s.100/108)."
        ],
        totals={
            "employee": "Total",
            "days": sum(r["days"] for r in out),
            "hours": round(sum(r["hours"] for r in out), 2),
            "overtime": round(sum(r["overtime"] for r in out), 2),
        },
        empty="No attendance recorded in the period.",
    )


def overtime_analysis(env, date_from=None, date_to=None, **params):
    """Overtime analysis by employee for the period."""
    summary = attendance_summary(env, date_from, date_to)
    rows = [r for r in summary["rows"] if r["overtime"] > 0]
    rows.sort(key=lambda r: -r["overtime"])
    return _pack(
        "Overtime Analysis — %s" % summary["title"].split("— ")[-1],
        ["employee", "days", "hours", "overtime"],
        {
            "employee": "Employee",
            "days": "Days",
            "hours": "Worked Hours",
            "overtime": "Overtime Hours",
        },
        rows,
        [
            "Overtime is statutory-paid at twice the ordinary rate (BLA 2006 s.108); "
            "only employees with recorded overtime appear."
        ],
        totals={
            "employee": "Total",
            "hours": round(sum(r["hours"] for r in rows), 2),
            "overtime": round(sum(r["overtime"] for r in rows), 2),
        },
        empty="No overtime recorded in the period.",
    )


def leave_utilisation(env, date_from=None, date_to=None, **params):
    """Leave utilisation: requested vs approved days by leave type."""
    requests = env["fix.leave.request"].search([("state", "!=", "draft")])
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
        "Leave Utilisation — days by leave type",
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
        ["Utilisation is approved days over requested days for every non-draft request."],
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


REPORTS = {
    "attendance_summary": attendance_summary,
    "overtime_analysis": overtime_analysis,
    "leave_utilisation": leave_utilisation,
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
        "overtime_preapproved": len(
            env["fix.attendance.record"].search([("approval_state", "=", "approved")])
        ),
        "roster_coverage": round(
            (len(rosters) - len(rosters.filtered(lambda r: r.on_leave))) / len(rosters) * 100.0, 1
        )
        if rosters
        else 0.0,
        "leave_pending": len(leave),
        "geofence_clockins": geo,
        "holidays": len(public_holidays),
    }
