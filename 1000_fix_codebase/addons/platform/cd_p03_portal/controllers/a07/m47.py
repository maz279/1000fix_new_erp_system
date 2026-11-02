# A07 · M47 Facility & Branch Infrastructure — surfaces, packs and KPIs over the
# site register, leases, licences, utilities, conditions, building PM, work
# orders, safety equipment, incidents and site projects.
import datetime

SURFACES = {
    "fix.site": {
        "order": "name",
        "limit": 200,
        "actions": {"action_close", "action_reopen"},
    },
    "fix.site.condition": {
        "order": "inspected_on desc, id desc",
        "limit": 300,
        "actions": set(),
    },
    "fix.site.asset": {
        "order": "site_id, asset_type, name",
        "limit": 400,
        "actions": {"action_maintenance", "action_restore", "action_retire"},
    },
    "fix.site.lease": {"order": "end_date desc, id desc", "limit": 200, "actions": set()},
    "fix.site.licence": {
        "order": "valid_to desc, id desc",
        "limit": 300,
        "actions": set(),
    },
    "fix.site.utility": {
        "order": "period desc, id desc",
        "limit": 400,
        "actions": {"action_flag"},
    },
    "fix.site.pm": {
        "order": "scheduled_on desc, id desc",
        "limit": 300,
        "actions": {"action_done"},
    },
    "fix.facility.work.order": {
        "order": "scheduled_date desc, id desc",
        "limit": 300,
        "actions": {"action_schedule", "action_start", "action_complete"},
    },
    "fix.site.safety": {
        "order": "next_check",
        "limit": 400,
        "actions": {"action_check"},
    },
    "fix.site.incident": {
        "order": "occurred_on desc, id desc",
        "limit": 200,
        "actions": {"action_close"},
    },
    "fix.site.project": {
        "order": "planned_on desc, id desc",
        "limit": 200,
        "actions": {"action_start", "action_done"},
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


def _sites(env):
    return env["fix.site"].sudo().search([])


def critical_dates(env, date_from=None, date_to=None, **params):
    today = datetime.date.today()
    horizon = today + datetime.timedelta(days=180)
    rows = []
    for lease in env["fix.site.lease"].sudo().search([("state", "=", "active")]):
        if lease.end_date and lease.end_date <= horizon:
            rows.append(
                {
                    "date": str(lease.end_date),
                    "kind": "Lease end",
                    "site": lease.site_id.name,
                    "reference": lease.name,
                    "days_left": (lease.end_date - today).days,
                }
            )
    for licence in env["fix.site.licence"].sudo().search([("state", "=", "valid")]):
        if licence.valid_to and licence.valid_to <= today + datetime.timedelta(days=90):
            rows.append(
                {
                    "date": str(licence.valid_to),
                    "kind": "Licence expiry (%s)" % licence.licence_type,
                    "site": licence.site_id.name,
                    "reference": licence.name,
                    "days_left": (licence.valid_to - today).days,
                }
            )
    for safety in env["fix.site.safety"].sudo().search([]):
        if safety.next_check and safety.next_check <= today + datetime.timedelta(days=30):
            rows.append(
                {
                    "date": str(safety.next_check),
                    "kind": "Safety check (%s)" % safety.equipment_type,
                    "site": safety.site_id.name,
                    "reference": safety.name,
                    "days_left": (safety.next_check - today).days,
                }
            )
    rows.sort(key=lambda r: r["date"])
    return _pack(
        "Critical-Date Control — leases (180d), licences (90d) and safety checks (30d)",
        ["date", "kind", "site", "reference", "days_left"],
        {
            "date": "Date",
            "kind": "Kind",
            "site": "Site",
            "reference": "Reference",
            "days_left": "Days Left",
        },
        rows,
        ["Negative days-left means the date has passed and the item is overdue."],
        empty="No critical date inside the horizons.",
    )


def branch_assets(env, date_from=None, date_to=None, **params):
    orders = env["fix.facility.work.order"].sudo().search([])
    rows = []
    for site in _sites(env):
        site_orders = orders.filtered(lambda o, sid=site.id: o.site_id.id == sid)
        rows.append(
            {
                "site": site.name,
                "type": dict(site._fields["site_type"].selection).get(site.site_type),
                "branch": site.branch_id.name if site.branch_id else "—",
                "area_sqm": round(site.floor_area_sqm or 0.0, 2),
                "assets": len(site.asset_ids),
                "asset_value": round(sum(site.asset_ids.mapped("value")), 2),
                "work_orders": len(site_orders),
                "spend": round(
                    sum((o.actual_cost or o.estimated_cost or 0.0) for o in site_orders),
                    2,
                ),
            }
        )
    rows.sort(key=lambda r: -r["spend"])
    return _pack(
        "Branch Asset Register — plant, equipment and work-order spend per site",
        ["site", "type", "branch", "area_sqm", "assets", "asset_value", "work_orders", "spend"],
        {
            "site": "Site",
            "type": "Type",
            "branch": "Branch",
            "area_sqm": "Area (sqm)",
            "assets": "Plant Assets",
            "asset_value": "Asset Value",
            "work_orders": "Work Orders",
            "spend": "WO Spend",
        },
        rows,
        [
            "Plant assets are the site infrastructure register (HVAC, lift, generator, "
            "fire pump, UPS, CCTV); spend is the actual cost, else the estimate."
        ],
        totals={
            "site": "Total",
            "assets": sum(r["assets"] for r in rows),
            "asset_value": round(sum(r["asset_value"] for r in rows), 2),
            "work_orders": sum(r["work_orders"] for r in rows),
            "spend": round(sum(r["spend"] for r in rows), 2),
        },
        empty="No sites registered yet.",
    )


def cost_per_site(env, date_from=None, date_to=None, **params):
    utilities = env["fix.site.utility"].sudo().search([])
    pms = env["fix.site.pm"].sudo().search([])
    orders = env["fix.facility.work.order"].sudo().search([])
    rows = []
    for site in _sites(env):
        utility = sum(
            utilities.filtered(lambda u, sid=site.id: u.site_id.id == sid).mapped("amount")
        )
        pm = sum(pms.filtered(lambda p, sid=site.id: p.site_id.id == sid).mapped("cost"))
        wo = sum(
            (o.actual_cost or o.estimated_cost or 0.0)
            for o in orders.filtered(lambda o, sid=site.id: o.site_id.id == sid)
        )
        rows.append(
            {
                "site": site.name,
                "rent": round(site.monthly_rent or 0.0, 2),
                "utilities": round(utility, 2),
                "pm": round(pm, 2),
                "work_orders": round(wo, 2),
                "total": round((site.monthly_rent or 0.0) + utility + pm + wo, 2),
            }
        )
    rows.sort(key=lambda r: -r["total"])
    return _pack(
        "Cost per Site / per Job — rent, utilities, PM and work orders",
        ["site", "rent", "utilities", "pm", "work_orders", "total"],
        {
            "site": "Site",
            "rent": "Monthly Rent",
            "utilities": "Utilities",
            "pm": "Building PM",
            "work_orders": "Work Orders",
            "total": "Total",
        },
        rows,
        [
            "The site's monthly rent comes from the site record; utilities, PM and "
            "work orders are the recorded records (no period filter applied here)."
        ],
        totals={
            "site": "Total",
            "rent": round(sum(r["rent"] for r in rows), 2),
            "utilities": round(sum(r["utilities"] for r in rows), 2),
            "pm": round(sum(r["pm"] for r in rows), 2),
            "work_orders": round(sum(r["work_orders"] for r in rows), 2),
            "total": round(sum(r["total"] for r in rows), 2),
        },
        empty="No sites registered yet.",
    )


def lease_expiry(env, date_from=None, date_to=None, **params):
    today = datetime.date.today()
    rows = []
    for lease in env["fix.site.lease"].sudo().search([]):
        rows.append(
            {
                "lease": lease.name,
                "site": lease.site_id.name,
                "lessor": lease.lessor_id.name,
                "start": str(lease.start_date),
                "end": str(lease.end_date),
                "rent": round(lease.monthly_rent, 2),
                "days_left": (lease.end_date - today).days if lease.end_date else "—",
                "state": dict(lease._fields["state"].selection).get(lease.state),
            }
        )
    rows.sort(key=lambda r: r["end"])
    return _pack(
        "Lease Expiry Register",
        ["lease", "site", "lessor", "start", "end", "rent", "days_left", "state"],
        {
            "lease": "Lease",
            "site": "Site",
            "lessor": "Lessor",
            "start": "Start",
            "end": "End",
            "rent": "Monthly Rent",
            "days_left": "Days Left",
            "state": "State",
        },
        rows,
        ["Days-left is computed from the lease end date."],
        empty="No leases recorded.",
    )


def licence_compliance(env, date_from=None, date_to=None, **params):
    rows = []
    for licence in env["fix.site.licence"].sudo().search([]):
        rows.append(
            {
                "licence": licence.name,
                "site": licence.site_id.name,
                "type": dict(licence._fields["licence_type"].selection).get(licence.licence_type),
                "number": licence.number or "—",
                "valid_to": str(licence.valid_to) if licence.valid_to else "—",
                "valid": licence.is_valid,
                "state": dict(licence._fields["state"].selection).get(licence.state),
            }
        )
    rows.sort(key=lambda r: (r["valid"], r["valid_to"]))
    return _pack(
        "Licence Compliance — statutory licences per site",
        ["licence", "site", "type", "number", "valid_to", "valid", "state"],
        {
            "licence": "Licence",
            "site": "Site",
            "type": "Type",
            "number": "Number",
            "valid_to": "Valid To",
            "valid": "Valid Today",
            "state": "State",
        },
        rows,
        ["Valid today = state valid AND the end date has not passed."],
        empty="No licences recorded.",
    )


def utilities_variance(env, date_from=None, date_to=None, **params):
    rows = []
    for utility in env["fix.site.utility"].sudo().search([]):
        rows.append(
            {
                "record": utility.name,
                "site": utility.site_id.name,
                "period": utility.period,
                "type": dict(utility._fields["utility_type"].selection).get(utility.utility_type),
                "amount": round(utility.amount, 2),
                "usage": round(utility.usage, 2),
                "unit": utility.unit or "—",
                "flagged": utility.flagged,
            }
        )
    rows.sort(key=lambda r: (r["site"], r["period"]))
    flagged = len([r for r in rows if r["flagged"]])
    return _pack(
        "Utilities Variance — recorded accounts and anomaly flags",
        ["record", "site", "period", "type", "amount", "usage", "unit", "flagged"],
        {
            "record": "Account",
            "site": "Site",
            "period": "Period",
            "type": "Type",
            "amount": "Amount",
            "usage": "Usage",
            "unit": "Unit",
            "flagged": "Flagged",
        },
        rows,
        [
            "%d account(s) flagged for review; the flag is a recorded judgement, not "
            "a statistical detector." % flagged
        ],
        totals={"record": "Total", "amount": round(sum(r["amount"] for r in rows), 2)},
        empty="No utility accounts recorded.",
    )


def work_order_performance(env, date_from=None, date_to=None, **params):
    orders = env["fix.facility.work.order"].sudo().search([])
    rows = []
    for order in orders:
        rows.append(
            {
                "order": order.name,
                "site": order.site_id.name,
                "type": dict(order._fields["work_type"].selection).get(order.work_type),
                "scheduled": str(order.scheduled_date) if order.scheduled_date else "—",
                "engineer": order.assigned_to.name if order.assigned_to else "—",
                "estimate": round(order.estimated_cost, 2),
                "actual": round(order.actual_cost, 2),
                "state": dict(order._fields["state"].selection).get(order.state),
            }
        )
    rows.sort(key=lambda r: str(r["scheduled"]), reverse=True)
    done = len([r for r in rows if r["state"] == "Completed"])
    return _pack(
        "Facility Work Order Performance",
        ["order", "site", "type", "scheduled", "engineer", "estimate", "actual", "state"],
        {
            "order": "Work Order",
            "site": "Site",
            "type": "Type",
            "scheduled": "Scheduled",
            "engineer": "Engineer",
            "estimate": "Estimate",
            "actual": "Actual",
            "state": "State",
        },
        rows,
        ["%d of %d work orders completed." % (done, len(rows))],
        totals={
            "order": "Total",
            "estimate": round(sum(r["estimate"] for r in rows), 2),
            "actual": round(sum(r["actual"] for r in rows), 2),
        },
        empty="No facility work orders recorded.",
    )


REPORTS = {
    "critical_dates": critical_dates,
    "branch_assets": branch_assets,
    "cost_per_site": cost_per_site,
    "lease_expiry": lease_expiry,
    "licence_compliance": licence_compliance,
    "utilities_variance": utilities_variance,
    "work_order_performance": work_order_performance,
}


def kpis(env):
    sites = _sites(env)
    today = datetime.date.today()
    horizon = today + datetime.timedelta(days=90)
    leases = env["fix.site.lease"].sudo().search([("state", "=", "active")])
    licences = env["fix.site.licence"].sudo().search([])
    utilities = env["fix.site.utility"].sudo().search([])
    orders = env["fix.facility.work.order"].sudo().search([])
    safety = env["fix.site.safety"].sudo().search([])
    total_sqft = sum(sites.mapped("floor_area_sqm")) * 10.7639
    return {
        "sites_active": len(sites.filtered(lambda s: s.state == "active")),
        "leases_expiring_90d": len(
            leases.filtered(lambda ln: ln.end_date and today <= ln.end_date <= horizon)
        ),
        "licences_expired": len(licences.filtered(lambda ln: not ln.is_valid)),
        "utilities_flagged": len(utilities.filtered(lambda u: u.flagged)),
        "utilities_cost_per_sqft": (
            round(sum(utilities.mapped("amount")) / total_sqft, 2) if total_sqft else 0.0
        ),
        "open_work_orders": len(
            orders.filtered(lambda o: o.state not in ("completed", "cancelled"))
        ),
        "safety_overdue": len(safety.filtered(lambda s: s.state == "overdue")),
        "safety_due": len(safety.filtered(lambda s: s.state in ("due", "overdue"))),
    }
