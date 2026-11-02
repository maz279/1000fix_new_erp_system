# A07 · M45 Enterprise Assets & Test Equipment — surfaces, packs and KPIs over
# the equipment register/calibration plus kits, issue/return, transfers,
# verification, out-of-service, PM and usage.
import datetime

SURFACES = {
    "fix.equipment": {"order": "code", "limit": 400, "actions": {"action_assert_usable"}},
    "fix.calibration": {"order": "calibrated_on desc, id desc", "limit": 400, "actions": set()},
    "fix.equipment.kit": {"order": "code", "limit": 200, "actions": set()},
    "fix.equipment.issue": {
        "order": "issued_on desc, id desc",
        "limit": 300,
        "actions": {"action_return"},
    },
    "fix.equipment.transfer": {
        "order": "transfer_date desc, id desc",
        "limit": 300,
        "actions": set(),
    },
    "fix.equipment.verification": {
        "order": "verified_on desc, id desc",
        "limit": 300,
        "actions": set(),
    },
    "fix.equipment.oos": {
        "order": "started_on desc, id desc",
        "limit": 300,
        "actions": {"action_resolve"},
    },
    "fix.equipment.pm": {
        "order": "scheduled_on desc, id desc",
        "limit": 300,
        "actions": {"action_done"},
    },
    "fix.equipment.usage": {"order": "used_on desc, id desc", "limit": 400, "actions": set()},
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


def _equipment(env):
    return env["fix.equipment"].sudo().search([])


def classification(env, date_from=None, date_to=None, **params):
    buckets = {}
    for equipment in _equipment(env):
        key = (
            equipment.category or "Uncategorised",
            equipment.custodian_id.name if equipment.custodian_id else "No custodian",
        )
        row = buckets.setdefault(
            key,
            {
                "category": key[0],
                "custodian": key[1],
                "items": 0,
                "calibrated": 0,
                "overdue": 0,
            },
        )
        row["items"] += 1
        if equipment.last_calibration:
            row["calibrated"] += 1
        if equipment.calibration_overdue:
            row["overdue"] += 1
    rows = sorted(buckets.values(), key=lambda r: -r["items"])
    return _pack(
        "Classification — equipment by category and custodian",
        ["category", "custodian", "items", "calibrated", "overdue"],
        {
            "category": "Category",
            "custodian": "Custodian",
            "items": "Items",
            "calibrated": "Calibrated",
            "overdue": "Overdue",
        },
        rows,
        [
            "Calibrated = has at least one calibration record; overdue = the computed "
            "flag on the equipment."
        ],
        totals={
            "category": "Total",
            "items": sum(r["items"] for r in rows),
            "calibrated": sum(r["calibrated"] for r in rows),
            "overdue": sum(r["overdue"] for r in rows),
        },
        empty="No equipment registered yet.",
    )


def calibration_schedule(env, date_from=None, date_to=None, **params):
    today = datetime.date.today()
    rows = []
    for equipment in _equipment(env):
        days = (equipment.next_calibration - today).days if equipment.next_calibration else None
        rows.append(
            {
                "code": equipment.code,
                "name": equipment.name,
                "category": equipment.category or "—",
                "last_calibration": str(equipment.last_calibration)
                if equipment.last_calibration
                else "—",
                "next_calibration": str(equipment.next_calibration)
                if equipment.next_calibration
                else "—",
                "days_left": days if days is not None else "—",
                "overdue": equipment.calibration_overdue,
                "status": equipment.operational_status,
            }
        )
    rows.sort(key=lambda r: (r["next_calibration"] == "—", r["next_calibration"]))
    return _pack(
        "Calibration Schedule — next due per equipment",
        [
            "code",
            "name",
            "category",
            "last_calibration",
            "next_calibration",
            "days_left",
            "overdue",
            "status",
        ],
        {
            "code": "Code",
            "name": "Equipment",
            "category": "Category",
            "last_calibration": "Last",
            "next_calibration": "Next Due",
            "days_left": "Days Left",
            "overdue": "Overdue",
            "status": "Status",
        },
        rows,
        [
            "Days-left is negative when overdue; an equipment without a calibration "
            "shows '—' rather than a fabricated date."
        ],
        empty="No equipment registered yet.",
    )


def retrospective_impact(env, date_from=None, date_to=None, **params):
    usages = env["fix.equipment.usage"].sudo().search([])
    calibrations = env["fix.calibration"].sudo().search([])
    rows = []
    for equipment in _equipment(env).filtered(
        lambda e: e.calibration_overdue
        or calibrations.filtered(
            lambda c, eid=e.id: c.equipment_id.id == eid and c.result == "fail"
        )
    ):
        failed = calibrations.filtered(
            lambda c, eid=equipment.id: c.equipment_id.id == eid and c.result == "fail"
        )
        last_fail = max(failed.mapped("calibrated_on")) if failed else None
        affected = usages.filtered(
            lambda u, eid=equipment.id, since=last_fail: u.equipment_id.id == eid
            and (not since or u.used_on >= since)
        )
        rows.append(
            {
                "code": equipment.code,
                "name": equipment.name,
                "next_calibration": str(equipment.next_calibration)
                if equipment.next_calibration
                else "—",
                "overdue": equipment.calibration_overdue,
                "failed_calibrations": len(failed),
                "affected_uses": len(affected),
                "last_failure": str(last_fail) if last_fail else "—",
            }
        )
    rows.sort(key=lambda r: -r["affected_uses"])
    return _pack(
        "Retrospective Impact — uses since the last failed/overdue calibration",
        [
            "code",
            "name",
            "next_calibration",
            "overdue",
            "failed_calibrations",
            "affected_uses",
            "last_failure",
        ],
        {
            "code": "Code",
            "name": "Equipment",
            "next_calibration": "Next Due",
            "overdue": "Overdue",
            "failed_calibrations": "Failed Cals",
            "affected_uses": "Uses Since Failure",
            "last_failure": "Last Failure",
        },
        rows,
        [
            "Affected uses are recorded usage rows on or after the last failed "
            "calibration; overdue equipment with no failure lists uses against the "
            "current window."
        ],
        empty="No equipment is overdue or has a failed calibration.",
    )


def calibration_compliance(env, date_from=None, date_to=None, **params):
    today = datetime.date.today()
    horizon = today + datetime.timedelta(days=30)
    rows = []
    for equipment in _equipment(env):
        if equipment.calibration_overdue:
            status = "overdue"
        elif equipment.next_calibration and equipment.next_calibration <= horizon:
            status = "due within 30 days"
        elif equipment.next_calibration:
            status = "current"
        else:
            status = "never calibrated"
        rows.append(
            {
                "code": equipment.code,
                "name": equipment.name,
                "category": equipment.category or "—",
                "next_calibration": str(equipment.next_calibration)
                if equipment.next_calibration
                else "—",
                "status": status,
                "operational": equipment.operational_status,
            }
        )
    rows.sort(key=lambda r: r["status"])
    counts = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    return _pack(
        "Calibration Compliance Report",
        ["code", "name", "category", "next_calibration", "status", "operational"],
        {
            "code": "Code",
            "name": "Equipment",
            "category": "Category",
            "next_calibration": "Next Due",
            "status": "Calibration Status",
            "operational": "Operational",
        },
        rows,
        ["Status counts: " + ", ".join("%s %d" % (k, v) for k, v in sorted(counts.items()))],
        empty="No equipment registered yet.",
    )


def utilisation(env, date_from=None, date_to=None, **params):
    usages = env["fix.equipment.usage"].sudo().search([])
    rows = []
    for equipment in _equipment(env):
        uses = usages.filtered(lambda u, eid=equipment.id: u.equipment_id.id == eid)
        rows.append(
            {
                "code": equipment.code,
                "name": equipment.name,
                "uses": len(uses),
                "total_uses": sum(uses.mapped("uses")),
                "qc_uses": len(uses.filtered(lambda u: u.qc_result != "na")),
                "last_used": str(max(uses.mapped("used_on"))) if uses else "—",
                "status": equipment.operational_status,
            }
        )
    rows.sort(key=lambda r: -r["total_uses"])
    return _pack(
        "Equipment Utilisation — recorded uses per item",
        ["code", "name", "uses", "total_uses", "qc_uses", "last_used", "status"],
        {
            "code": "Code",
            "name": "Equipment",
            "uses": "Usage Rows",
            "total_uses": "Total Uses",
            "qc_uses": "QC Uses",
            "last_used": "Last Used",
            "status": "Status",
        },
        rows,
        [
            "Counts recorded usage rows only; an item with no usage rows shows 0 — "
            "absence of data is not evidence of no use."
        ],
        totals={
            "code": "Total",
            "uses": sum(r["uses"] for r in rows),
            "total_uses": sum(r["total_uses"] for r in rows),
        },
        empty="No equipment registered yet.",
    )


def loss_writeoff(env, date_from=None, date_to=None, **params):
    verifications = env["fix.equipment.verification"].sudo().search([("state", "=", "missing")])
    rows = []
    for record in verifications:
        rows.append(
            {
                "code": record.equipment_id.code,
                "name": record.equipment_id.name,
                "campaign": record.campaign_ref,
                "verified_on": str(record.verified_on),
                "location": record.location or "—",
                "verifier": record.verifier_id.name if record.verifier_id else "—",
                "status": dict(record.equipment_id._fields["operational_status"].selection).get(
                    record.equipment_id.operational_status
                ),
            }
        )
    rows.sort(key=lambda r: r["verified_on"], reverse=True)
    return _pack(
        "Tool Loss & Write-Off — equipment missing at verification",
        ["code", "name", "campaign", "verified_on", "location", "verifier", "status"],
        {
            "code": "Code",
            "name": "Equipment",
            "campaign": "Campaign",
            "verified_on": "Verified",
            "location": "Last Location",
            "verifier": "Verifier",
            "status": "Operational",
        },
        rows,
        [
            "A missing verification is the recorded loss; retirement/write-off is the "
            "equipment's operational status, not inferred here."
        ],
        totals={"code": "Total"},
        empty="No equipment was missing at verification.",
    )


def cost_of_ownership(env, date_from=None, date_to=None, **params):
    pms = env["fix.equipment.pm"].sudo().search([])
    calibrations = env["fix.calibration"].sudo().search([])
    rows = []
    for equipment in _equipment(env):
        equipment_pm = pms.filtered(lambda p, eid=equipment.id: p.equipment_id.id == eid)
        rows.append(
            {
                "code": equipment.code,
                "name": equipment.name,
                "pm_jobs": len(equipment_pm),
                "pm_cost": round(sum(equipment_pm.mapped("cost")), 2),
                "calibrations": len(
                    calibrations.filtered(lambda c, eid=equipment.id: c.equipment_id.id == eid)
                ),
                "status": equipment.operational_status,
            }
        )
    rows.sort(key=lambda r: -r["pm_cost"])
    return _pack(
        "Cost of Ownership — recorded PM cost and calibration count",
        ["code", "name", "pm_jobs", "pm_cost", "calibrations", "status"],
        {
            "code": "Code",
            "name": "Equipment",
            "pm_jobs": "PM Jobs",
            "pm_cost": "PM Cost",
            "calibrations": "Calibrations",
            "status": "Status",
        },
        rows,
        [
            "Only recorded PM cost is summed; the equipment register carries no "
            "acquisition cost, so total cost of ownership is not claimed."
        ],
        totals={
            "code": "Total",
            "pm_jobs": sum(r["pm_jobs"] for r in rows),
            "pm_cost": round(sum(r["pm_cost"] for r in rows), 2),
            "calibrations": sum(r["calibrations"] for r in rows),
        },
        empty="No equipment registered yet.",
    )


REPORTS = {
    "classification": classification,
    "calibration_schedule": calibration_schedule,
    "retrospective_impact": retrospective_impact,
    "calibration_compliance": calibration_compliance,
    "utilisation": utilisation,
    "loss_writeoff": loss_writeoff,
    "cost_of_ownership": cost_of_ownership,
}


def kpis(env):
    equipment = _equipment(env)
    issues = env["fix.equipment.issue"].sudo().search([("state", "=", "issued")])
    return {
        "equipment_total": len(equipment),
        "calibration_overdue": len(equipment.filtered(lambda e: e.calibration_overdue)),
        "oos_open": env["fix.equipment.oos"].sudo().search_count([("state", "=", "open")]),
        "issued_out": len(issues),
        "kits": env["fix.equipment.kit"].sudo().search_count([("active", "=", True)]),
        "pm_open": env["fix.equipment.pm"].sudo().search_count([("state", "=", "open")]),
    }
