# A09 · M59 Health, Safety & Wellbeing — surfaces, packs and KPIs over the
# hazard register, JSA, PPE, incidents/investigations, statutory clocks,
# lone-worker/road safety, drills, committee and occupational health.
import datetime

# A09 workflow audit (M59-F2..F12): every state on these surfaces moves only
# through the actions below; approvals (JSA, injury compensation) are
# requested here and decided from the M63 inbox, so their apply methods are
# not offered on the screens.
SURFACES = {
    "fix.hse.hazard": {
        "order": "risk_score desc, id desc",
        "limit": 300,
        "actions": {"action_control", "action_review", "action_close"},
    },
    "fix.hse.jsa": {
        "order": "job_type",
        "limit": 300,
        "actions": {
            "action_request_approval",
            "action_recall_approval",
            "action_revise",
            "action_retire",
        },
    },
    "fix.ppe.register": {"order": "name", "limit": 500, "actions": set()},
    "fix.ppe.issue": {"order": "issued_on desc", "limit": 500, "actions": {"action_acknowledge"}},
    "fix.safety.committee.member": {"order": "committee_id, side", "limit": 500, "actions": set()},
    "fix.safety.committee.meeting": {"order": "meeting_date desc", "limit": 300, "actions": set()},
    "fix.hse.incident": {
        "order": "reported_at desc, id desc",
        "limit": 400,
        "actions": {
            "action_investigate",
            "action_record_action_taken",
            "action_verify_capa",
            "action_close",
            "action_escalate",
            "action_notify_dife",
            "action_dispatch_dife_notice",
        },
    },
    "fix.statutory.accident.register": {
        "order": "accident_date desc",
        "limit": 300,
        "actions": {
            "action_notify_dife",
            "action_request_approval",
            "action_recall_approval",
            "action_close",
        },
    },
    "fix.hse.loneworker": {
        "order": "checkin_time desc, id desc",
        "limit": 400,
        "actions": {"action_checkout", "action_escalate"},
    },
    "fix.hse.roadcheck": {"order": "checked_on desc, id desc", "limit": 400, "actions": set()},
    "fix.hazardous.substance.register": {
        "order": "name",
        "limit": 200,
        "actions": {"action_quarantine", "action_release"},
    },
    "fix.hse.drill": {
        "order": "scheduled_on desc, id desc",
        "limit": 200,
        "actions": {"action_complete", "action_cancel"},
    },
    "fix.safety.committee": {
        "order": "formation_date desc",
        "limit": 100,
        "actions": {
            "action_activate",
            "action_record_meeting",
            "action_record_dife_registration",
            "action_dissolve",
        },
    },
    "fix.hse.health": {
        "order": "record_date desc, id desc",
        "limit": 300,
        "actions": {"action_close"},
    },
    "fix.safety.inspection": {"order": "id desc", "limit": 400, "actions": {"action_complete"}},
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


def incident_statistics(env, date_from=None, date_to=None, **params):
    """Incident statistics by type and severity."""
    incidents = env["fix.hse.incident"].search([])
    groups = {}
    for inc in incidents:
        key = dict(inc._fields["incident_type"].selection).get(inc.incident_type)
        g = groups.setdefault(key, {"total": 0, "low": 0, "medium": 0, "high": 0, "closed": 0})
        g["total"] += 1
        g[inc.severity] = g.get(inc.severity, 0) + 1
        if inc.state == "closed":
            g["closed"] += 1
    rows = [
        {
            "type": k,
            "total": v["total"],
            "low": v["low"],
            "medium": v["medium"],
            "high": v["high"],
            "closed": v["closed"],
        }
        for k, v in sorted(groups.items(), key=lambda kv: -kv[1]["total"])
    ]
    return _pack(
        "Incident Statistics — %d incidents" % len(incidents),
        ["type", "total", "low", "medium", "high", "closed"],
        {
            "type": "Incident Type",
            "total": "Total",
            "low": "Low",
            "medium": "Medium",
            "high": "High",
            "closed": "Closed",
        },
        rows,
        [
            "Severity follows the model's own bands; high means critical/hospitalisation/DIFE-reportable."
        ],
        totals={
            "type": "Total",
            "total": sum(r["total"] for r in rows),
            "low": sum(r["low"] for r in rows),
            "medium": sum(r["medium"] for r in rows),
            "high": sum(r["high"] for r in rows),
            "closed": sum(r["closed"] for r in rows),
        },
        empty="No incidents recorded.",
    )


def leading_indicators(env, date_from=None, date_to=None, **params):
    """Leading indicators: near-miss reports, inspections and hazards controlled."""
    today = datetime.date.today()
    month_start = today.replace(day=1)
    incidents = env["fix.hse.incident"].search([])
    near_miss = incidents.filtered(
        lambda i: (
            i.incident_type == "near_miss" and i.reported_at and i.reported_at.date() >= month_start
        )
    )
    inspections = env["fix.safety.inspection"].search([("inspected_on", ">=", str(month_start))])
    hazards = env["fix.hse.hazard"].search([])
    controlled = hazards.filtered(lambda h: h.state in ("controlled", "closed"))
    drills = env["fix.hse.drill"].search([("state", "=", "completed")])
    rows = [
        {"indicator": "Near-miss reports MTD", "value": len(near_miss)},
        {"indicator": "Safety inspections MTD", "value": len(inspections)},
        {"indicator": "Hazards controlled", "value": len(controlled)},
        {"indicator": "Hazards open", "value": len(hazards) - len(controlled)},
        {"indicator": "Drills completed", "value": len(drills)},
    ]
    return _pack(
        "Leading Indicators — the prevention side",
        ["indicator", "value"],
        {"indicator": "Indicator", "value": "Value"},
        rows,
        [
            "Leading indicators measure prevention activity (reports, inspections, controls, "
            "drills); they are counts, not rates."
        ],
        empty="No leading-indicator records.",
    )


def statutory_compliance(env, date_from=None, date_to=None, **params):
    """Statutory notification clock from the accident register: the deadline,
    whether it has passed, and whether the notice went late (BLA s.80)."""
    registers = env["fix.statutory.accident.register"].search([])
    now = datetime.datetime.now()
    rows = []
    for reg in registers:
        reported = reg.accident_date
        days = (datetime.date.today() - reported).days if reported else None
        overdue = bool(not reg.dife_notified and reg.notice_due and now > reg.notice_due)
        rows.append(
            {
                "record": reg.name,
                "employee": reg.employee_id.name if reg.employee_id else "—",
                "date": str(reported or "—"),
                "body_part": reg.affected_body_part or "—",
                "lost_days": reg.lost_work_days,
                "days_open": days if days is not None else "—",
                "notice_due": str(reg.notice_due or "—"),
                "overdue": "OVERDUE" if overdue else "No",
                "notified": "Yes" if reg.dife_notified else "No",
                "notice_date": str(reg.dife_notification_date or "—"),
                "late": "Late" if reg.notified_late else ("On time" if reg.dife_notified else "—"),
            }
        )
    rows.sort(key=lambda r: r["date"], reverse=True)
    pending = len([r for r in rows if r["notified"] == "No"])
    overdue = len([r for r in rows if r["overdue"] == "OVERDUE"])
    return _pack(
        "Statutory Compliance — %d awaiting DIFE notice, %d past the deadline" % (pending, overdue),
        [
            "record",
            "employee",
            "date",
            "body_part",
            "lost_days",
            "days_open",
            "notice_due",
            "overdue",
            "notified",
            "notice_date",
            "late",
        ],
        {
            "record": "Statutory Record",
            "employee": "Worker",
            "date": "Accident Date",
            "body_part": "Body Part",
            "lost_days": "Lost Days",
            "days_open": "Days Open",
            "notice_due": "Notice Deadline",
            "overdue": "Past Deadline",
            "notified": "DIFE Notified",
            "notice_date": "Notice Date",
            "late": "Notice Timeliness",
        },
        rows,
        [
            "Reads the statutory accident register (BLA 2006 s.80 / BLR 2015 r.70, Form 28 "
            "under r.73). The deadline is the incident's computed notice window; a plain "
            "employee sees only the entries that name them."
        ],
        totals={"record": "Total", "lost_days": sum(r["lost_days"] for r in rows)},
        empty="No statutory accident records.",
    )


def ppe_compliance(env, date_from=None, date_to=None, **params):
    """PPE register: item types with their regulatory standard, stock and the
    model's computed state (adequate / low stock)."""
    ppe = env["fix.ppe.register"].search([])
    rows = []
    for item in ppe:
        rows.append(
            {
                "item": item.name,
                "ppe_type": dict(item._fields["item_type"].selection).get(
                    item.item_type, item.item_type
                )
                if item.item_type
                else "—",
                "standard": item.regulatory_standard or "—",
                "stock": item.stock_quantity,
                "minimum": item.min_required_quantity,
                "state": dict(item._fields["state"].selection).get(item.state, item.state)
                if "state" in item._fields
                else "—",
            }
        )
    below = len([r for r in rows if r["stock"] < r["minimum"]])
    return _pack(
        "PPE Compliance — %d item type(s) below minimum" % below,
        ["item", "ppe_type", "standard", "stock", "minimum", "state"],
        {
            "item": "PPE Item",
            "ppe_type": "Type",
            "standard": "Regulatory Standard",
            "stock": "Stock",
            "minimum": "Minimum",
            "state": "State",
        },
        rows,
        [
            "Stock compliance: an item type is compliant when its stock is above its minimum. "
            "Issues to employees and their acknowledgements are kept on fix.ppe.issue."
        ],
        totals={"item": "Total", "stock": sum(r["stock"] for r in rows)},
        empty="No PPE items recorded.",
    )


def drill_coverage(env, date_from=None, date_to=None, **params):
    """Drill calendar coverage by drill type."""
    drills = env["fix.hse.drill"].search([])
    groups = {}
    for drill in drills:
        key = dict(drill._fields["drill_type"].selection).get(drill.drill_type)
        g = groups.setdefault(key, {"planned": 0, "completed": 0, "participants": 0})
        if drill.state == "completed":
            g["completed"] += 1
        else:
            g["planned"] += 1
        g["participants"] += drill.participants or 0
    rows = [
        {
            "drill_type": k,
            "planned": v["planned"],
            "completed": v["completed"],
            "participants": v["participants"],
        }
        for k, v in sorted(groups.items())
    ]
    return _pack(
        "Drill Calendar Coverage",
        ["drill_type", "planned", "completed", "participants"],
        {
            "drill_type": "Drill Type",
            "planned": "Planned/Open",
            "completed": "Completed",
            "participants": "Participants",
        },
        rows,
        ["Coverage counts drills by type; a type with no completed drill is visible as such."],
        totals={
            "drill_type": "Total",
            "planned": sum(r["planned"] for r in rows),
            "completed": sum(r["completed"] for r in rows),
            "participants": sum(r["participants"] for r in rows),
        },
        empty="No drills recorded.",
    )


REPORTS = {
    "incident_statistics": incident_statistics,
    "leading_indicators": leading_indicators,
    "statutory_compliance": statutory_compliance,
    "ppe_compliance": ppe_compliance,
    "drill_coverage": drill_coverage,
}


def kpis(env):
    today = datetime.date.today()
    year_start = today.replace(month=1, day=1)
    month_start = today.replace(day=1)
    incidents = env["fix.hse.incident"].search([])
    ytd = incidents.filtered(lambda i: i.reported_at and i.reported_at.date() >= year_start)
    lost_time = ytd.filtered(
        lambda i: i.severity in ("medium", "high") and i.incident_type == "injury"
    )
    near_miss = incidents.filtered(
        lambda i: (
            i.incident_type == "near_miss" and i.reported_at and i.reported_at.date() >= month_start
        )
    )
    registers = env["fix.statutory.accident.register"].search([])
    pending_dife = registers.filtered(lambda r: not r.dife_notified)
    ppe = env["fix.ppe.register"].search([])
    drills = env["fix.hse.drill"].search([("state", "=", "completed")])
    return {
        "recordable_incidents_ytd": len(ytd),
        "lost_time_injuries": len(lost_time),
        "near_miss_mtd": len(near_miss),
        "statutory_clock": len(pending_dife),
        # a rate: the share of PPE item types whose stock is above the minimum
        "ppe_compliance": round(
            len(ppe.filtered(lambda p: p.state == "compliant")) / len(ppe) * 100.0, 1
        )
        if ppe
        else 0.0,
        "drills_completed": len(drills),
    }
