# A07 · M46 Fleet & Vehicles — surfaces, packs and KPIs over the fleet.vehicle
# register, dispatch assignments, drivers, documents, off-road records, checks,
# PM, fuel, telemetry and accidents.
import datetime
import itertools

from odoo import fields

from ..p03_service_order_api import _company_domain

SURFACES = {
    "fleet.vehicle": {
        "order": "name",
        "limit": 300,
        "actions": {"action_assert_dispatchable"},
    },
    "fix.vehicle.assignment": {
        "order": "date desc, id desc",
        "limit": 300,
        "actions": set(),
    },
    # A07 P0 recipe M46-6: reinstatement is its own action (second person,
    # reason, licence in date); `state` is guarded.
    "fix.driver": {
        "order": "name",
        "limit": 200,
        "actions": {"action_suspend", "action_reinstate"},
    },
    "fix.vehicle.document": {
        "order": "valid_to desc, id desc",
        "limit": 300,
        "actions": {"action_expire"},
    },
    "fix.vehicle.offroad": {
        "order": "started_on desc, id desc",
        "limit": 200,
        "actions": {"action_return"},
    },
    "fix.vehicle.check": {
        "order": "checked_on desc, id desc",
        "limit": 300,
        "actions": set(),
    },
    "fix.vehicle.pm": {
        "order": "scheduled_on desc, id desc",
        "limit": 300,
        "actions": {"action_done"},
    },
    # A07 P0 recipe M46-9: a held fill is reviewed by someone other than
    # its recorder.
    "fix.vehicle.fuel": {
        "order": "filled_on desc, id desc",
        "limit": 400,
        "actions": {"action_clear_exception", "action_reject_fill"},
    },
    "fix.vehicle.telemetry": {
        "order": "last_ping desc, id desc",
        "limit": 200,
        "actions": set(),
    },
    "fix.vehicle.accident": {
        "order": "occurred_on desc, id desc",
        "limit": 200,
        # A07 P0 recipe M46-10: the settlement is DOFA-routed (M63 inbox).
        "actions": {"action_claim", "action_request_approval", "action_close"},
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


# A07 audit (2026-11-03) M46-12 (D6): every KPI and pack read sudo().search([])
# across all companies, so an officer's "Vehicles" counted vans they cannot
# read. sudo() stays (the packs aggregate over models a plain user may not
# list), and the company fence is re-applied: on fleet.vehicle directly, and
# on the M46 ops models (no company_id) through their vehicle.
def _vehicles(env):
    return env["fleet.vehicle"].sudo().search(_company_domain(env, "fleet.vehicle"))


def _scoped(env, model, vehicles, extra=None):
    return env[model].sudo().search([("vehicle_id", "in", vehicles.ids)] + (extra or []))


def _vehicle_name(vehicle):
    return getattr(vehicle, "name", None) or vehicle.license_plate or "—"


def _drivers(env):
    ids = env.user.company_ids.ids
    return (
        env["fix.driver"]
        .sudo()
        .search(
            ["|", ("employee_id.company_id", "=", False), ("employee_id.company_id", "in", ids)]
        )
    )


def _today(env):
    # the statutory and operating day is the Dhaka date (cd_vehicle_ext gate)
    return fields.Date.context_today(env["fix.vehicle.check"].with_context(tz="Asia/Dhaka"))


def _day(value):
    """A report period bound ("YYYY-MM-DD"), or None when not given."""
    try:
        return fields.Date.to_date(value) if value and value != "…" else None
    except (TypeError, ValueError):
        return None


def _in_period(day, date_from, date_to):
    return bool(day) and (not date_from or day >= date_from) and (not date_to or day <= date_to)


def _fill_to_fill(fills):
    """Distance and the fuel that drove it, measured fill to fill.

    A07 audit M46-11 (D5): km/l and cost/km divided by ALL litres and all
    fuel spend, including the first fill, whose fuel was burnt before the
    odometer range began (7.94 km/l reported vs 11.63 true). The first fill
    in the period only opens the range. Fewer than two fills, or an odometer
    that goes backwards between fills, has no measured distance: the figure
    is provisional (BRU-FLT-18), never 0.00 presented as fact."""
    ordered = fills.sorted(lambda f: (f.filled_on, f.odometer, f.id))
    out = {
        "fills": len(ordered),
        "litres": round(sum(ordered.mapped("litres")), 2),
        "spend": round(sum(ordered.mapped("amount")), 2),
        "km": None,
        "litres_in_range": None,
        "fuel_in_range": None,
        "basis": "provisional: %d fill(s), no measured distance" % len(ordered),
    }
    if len(ordered) < 2:
        return out
    if any(b.odometer < a.odometer for a, b in itertools.pairwise(ordered)):
        out["basis"] = "provisional: odometer goes backwards between fills"
        return out
    rest = ordered[1:]
    out.update(
        km=ordered[-1].odometer - ordered[0].odometer,
        litres_in_range=round(sum(rest.mapped("litres")), 2),
        fuel_in_range=round(sum(rest.mapped("amount")), 2),
        basis="measured: %d fills, fill to fill" % len(ordered),
    )
    if not out["km"]:
        out.update(km=None, basis="provisional: no distance between fills")
    return out


def driver_behaviour(env, date_from=None, date_to=None, **params):
    vehicles = _vehicles(env)
    checks = _scoped(env, "fix.vehicle.check", vehicles)
    accidents = _scoped(env, "fix.vehicle.accident", vehicles)
    rows = []
    for driver in _drivers(env):
        driver_checks = checks.filtered(lambda c, d=driver.id: c.driver_id.id == d)
        driver_accidents = accidents.filtered(lambda a, d=driver.id: a.driver_id.id == d)
        failed = len(driver_checks.filtered(lambda c: not c.passed))
        rows.append(
            {
                "driver": driver.name,
                "licence": driver.license_no,
                "state": dict(driver._fields["state"].selection).get(driver.state),
                "checks": len(driver_checks),
                "failed_checks": failed,
                "accidents": len(driver_accidents),
                "damage": round(sum(driver_accidents.mapped("damage_cost")), 2),
            }
        )
    rows.sort(key=lambda r: (-r["accidents"], -r["failed_checks"]))
    return _pack(
        "Driver Behaviour — checks, failures and accidents per driver",
        ["driver", "licence", "state", "checks", "failed_checks", "accidents", "damage"],
        {
            "driver": "Driver",
            "licence": "Licence",
            "state": "State",
            "checks": "Checks",
            "failed_checks": "Failed Checks",
            "accidents": "Accidents",
            "damage": "Damage Cost",
        },
        rows,
        [
            "Recorded pre-use checks and recorded accidents only; no telematics "
            "scoring is claimed."
        ],
        empty="No drivers registered yet.",
    )


def _period_fills(env, vehicles, date_from, date_to):
    fills = _scoped(env, "fix.vehicle.fuel", vehicles)
    return fills.filtered(lambda f: _in_period(f.filled_on, date_from, date_to))


def _period_note(date_from, date_to):
    if not (date_from or date_to):
        return "All recorded history (no period chosen)."
    return "Period %s → %s." % (date_from or "…", date_to or "…")


def cost_per_km(env, date_from=None, date_to=None, **params):
    date_from, date_to = _day(date_from), _day(date_to)
    vehicles = _vehicles(env)
    fuels = _period_fills(env, vehicles, date_from, date_to)
    # a PM job belongs to the day it was done, else the day it was scheduled
    pms = _scoped(env, "fix.vehicle.pm", vehicles).filtered(
        lambda p: _in_period(p.done_on or p.scheduled_on, date_from, date_to)
    )
    rows = []
    for vehicle in vehicles:
        f2f = _fill_to_fill(fuels.filtered(lambda f, vid=vehicle.id: f.vehicle_id.id == vid))
        pm_cost = round(
            sum(pms.filtered(lambda p, vid=vehicle.id: p.vehicle_id.id == vid).mapped("cost")), 2
        )
        km = f2f["km"]
        rows.append(
            {
                "vehicle": _vehicle_name(vehicle),
                "plate": vehicle.license_plate or "—",
                "fills": f2f["fills"],
                "km": km,
                "fuel_cost": f2f["spend"],
                "fuel_in_range": f2f["fuel_in_range"],
                "pm_cost": pm_cost,
                "total_cost": round(f2f["spend"] + pm_cost, 2),
                "cost_per_km": round((f2f["fuel_in_range"] + pm_cost) / km, 2) if km else None,
                "basis": f2f["basis"],
            }
        )
    rows.sort(key=lambda r: (r["cost_per_km"] is None, -(r["cost_per_km"] or 0)))
    measured = [r for r in rows if r["km"]]
    return _pack(
        "Cost per Kilometre — fuel + PM over the measured distance",
        [
            "vehicle", "plate", "fills", "km", "fuel_cost", "fuel_in_range",
            "pm_cost", "total_cost", "cost_per_km", "basis",
        ],
        {
            "vehicle": "Vehicle",
            "plate": "Plate",
            "fills": "Fills",
            "km": "Measured km",
            "fuel_cost": "Fuel Spend",
            "fuel_in_range": "Fuel in Range",
            "pm_cost": "PM Cost",
            "total_cost": "Total Spend",
            "cost_per_km": "Cost / km",
            "basis": "Basis",
        },
        rows,
        [
            _period_note(date_from, date_to),
            "Measured km = last − first fuel odometer in the period. Cost / km = "
            "(fuel of the fills after the first + PM cost) / measured km: the first "
            "fill's fuel was burnt before the range began.",
            "Provisional (no figure) where the period has fewer than two fills or the "
            "odometer goes backwards. Depreciation, insurance, document fees and "
            "downtime are not included.",
        ],
        totals={
            "vehicle": "Total",
            "km": sum(r["km"] for r in measured),
            "fuel_cost": round(sum(r["fuel_cost"] for r in rows), 2),
            "pm_cost": round(sum(r["pm_cost"] for r in rows), 2),
            "total_cost": round(sum(r["total_cost"] for r in rows), 2),
        },
        empty="No vehicles registered yet.",
    )  # fmt: skip


def _availability(env, vehicles):
    """Per vehicle id: the dispatch-gate blockers today (cd_vehicle_ext)."""
    return vehicles._fix_dispatch_blockers(day=_today(env))


def fleet_availability(env, date_from=None, date_to=None, **params):
    today = _today(env)
    vehicles = _vehicles(env)
    blockers = _availability(env, vehicles)
    offroad = set(
        _scoped(env, "fix.vehicle.offroad", vehicles, [("state", "=", "offroad")])
        .mapped("vehicle_id")
        .ids
    )
    assigned = set(
        _scoped(env, "fix.vehicle.assignment", vehicles, [("date", "=", today)])
        .mapped("vehicle_id")
        .ids
    )
    rows = []
    for vehicle in vehicles:
        reasons = blockers.get(vehicle.id, [])
        if vehicle.id in offroad:
            status = "off road"
        elif reasons:
            status = "not dispatchable"
        elif vehicle.id in assigned:
            status = "assigned today"
        else:
            status = "available"
        rows.append(
            {
                "vehicle": _vehicle_name(vehicle),
                "plate": vehicle.license_plate or "—",
                "driver": vehicle.fix_driver_id.name if vehicle.fix_driver_id else "—",
                "compliance_ok": vehicle.compliance_ok,
                "dispatchable": not reasons,
                "status": status,
                "blockers": "; ".join(reasons) or "—",
            }
        )
    rows.sort(key=lambda r: r["status"])
    passing = len([r for r in rows if r["dispatchable"]])
    busy = len([r for r in rows if r["status"] == "assigned today"])
    return _pack(
        "Fleet Availability — today's status per vehicle",
        ["vehicle", "plate", "driver", "compliance_ok", "dispatchable", "status", "blockers"],
        {
            "vehicle": "Vehicle",
            "plate": "Plate",
            "driver": "Driver",
            "compliance_ok": "Documents Valid",
            "dispatchable": "Passes Gate",
            "status": "Availability",
            "blockers": "Why Not",
        },
        rows,
        [
            "%d of %d vehicles pass the dispatch gate today (%d of them already "
            "assigned today). The gate reads the document register, open off-road "
            "records, open accidents, today's pre-use checks and the assigned "
            "driver; the header fitness/insurance dates are information only."
            % (passing, len(rows), busy)
        ],
        empty="No vehicles registered yet.",
    )


def fuel_efficiency(env, date_from=None, date_to=None, **params):
    date_from, date_to = _day(date_from), _day(date_to)
    vehicles = _vehicles(env)
    fuels = _period_fills(env, vehicles, date_from, date_to)
    rows = []
    for vehicle in vehicles:
        f2f = _fill_to_fill(fuels.filtered(lambda f, vid=vehicle.id: f.vehicle_id.id == vid))
        km, litres = f2f["km"], f2f["litres_in_range"]
        rows.append(
            {
                "vehicle": _vehicle_name(vehicle),
                "records": f2f["fills"],
                "litres": f2f["litres"],
                "km": km,
                "litres_in_range": litres,
                "km_per_litre": round(km / litres, 2) if km and litres else None,
                "spend": f2f["spend"],
                "basis": f2f["basis"],
            }
        )
    rows.sort(key=lambda r: (r["km_per_litre"] is None, -(r["km_per_litre"] or 0)))
    measured = [r for r in rows if r["km"]]
    return _pack(
        "Fuel Efficiency Trend — km per litre, fill to fill",
        ["vehicle", "records", "litres", "km", "litres_in_range", "km_per_litre", "spend", "basis"],
        {
            "vehicle": "Vehicle",
            "records": "Fills",
            "litres": "Litres",
            "km": "Measured km",
            "litres_in_range": "Litres in Range",
            "km_per_litre": "km/l",
            "spend": "Spend",
            "basis": "Basis",
        },
        rows,
        [
            _period_note(date_from, date_to),
            "km/l = (last − first fuel odometer) / litres of the fills after the "
            "first; provisional (no figure) with fewer than two fills or a backwards "
            "odometer. Fuel-card imports are M52's; these are recorded transactions.",
        ],
        totals={
            "vehicle": "Total",
            "litres": round(sum(r["litres"] for r in rows), 2),
            "km": sum(r["km"] for r in measured),
            "spend": round(sum(r["spend"] for r in rows), 2),
        },
        empty="No fuel transactions recorded yet.",
    )


def maintenance_cost(env, date_from=None, date_to=None, **params):
    vehicles = _vehicles(env)
    pms = _scoped(env, "fix.vehicle.pm", vehicles)
    rows = []
    for vehicle in vehicles:
        records = pms.filtered(lambda p, vid=vehicle.id: p.vehicle_id.id == vid)
        rows.append(
            {
                "vehicle": _vehicle_name(vehicle),
                "jobs": len(records),
                "done": len(records.filtered(lambda p: p.state == "done")),
                "cost": round(sum(records.mapped("cost")), 2),
                "last_service": str(max(records.mapped("scheduled_on"))) if records else "—",
            }
        )
    rows.sort(key=lambda r: -r["cost"])
    return _pack(
        "Maintenance Cost per Vehicle",
        ["vehicle", "jobs", "done", "cost", "last_service"],
        {
            "vehicle": "Vehicle",
            "jobs": "Jobs",
            "done": "Done",
            "cost": "Cost",
            "last_service": "Last Scheduled",
        },
        rows,
        ["Recorded PM/repair jobs only; parts drawn from M15 are not double-counted " "here."],
        totals={
            "vehicle": "Total",
            "jobs": sum(r["jobs"] for r in rows),
            "done": sum(r["done"] for r in rows),
            "cost": round(sum(r["cost"] for r in rows), 2),
        },
        empty="No vehicles registered yet.",
    )


def statutory_compliance(env, date_from=None, date_to=None, **params):
    today = _today(env)
    horizon = today + datetime.timedelta(days=90)
    vehicles = _vehicles(env)
    docs = _scoped(env, "fix.vehicle.document", vehicles)
    rows = []
    for vehicle in vehicles:
        vehicle_docs = docs.filtered(lambda d, vid=vehicle.id: d.vehicle_id.id == vid)
        expiring = vehicle_docs.filtered(lambda d: d.valid_to and today <= d.valid_to <= horizon)
        rows.append(
            {
                "vehicle": _vehicle_name(vehicle),
                "plate": vehicle.license_plate or "—",
                "fitness": str(vehicle.fitness_expiry) if vehicle.fitness_expiry else "—",
                "insurance": str(vehicle.insurance_expiry) if vehicle.insurance_expiry else "—",
                "compliant": vehicle.compliance_ok,
                "valid_docs": len(vehicle_docs.filtered(lambda d: d.is_valid)),
                "expiring_90d": len(expiring),
            }
        )
    rows.sort(key=lambda r: (r["compliant"], r["expiring_90d"]))
    return _pack(
        "Statutory Compliance Register — fitness, insurance and documents",
        ["vehicle", "plate", "fitness", "insurance", "compliant", "valid_docs", "expiring_90d"],
        {
            "vehicle": "Vehicle",
            "plate": "Plate",
            "fitness": "Fitness (header)",
            "insurance": "Insurance (header)",
            "compliant": "Compliant",
            "valid_docs": "Valid Docs",
            "expiring_90d": "Expiring (90d)",
        },
        rows,
        [
            "Compliant = every mandatory document type is in the register and valid "
            "today (the dispatch gate's own test). The header fitness and insurance "
            "dates are shown for information; they do not decide compliance."
        ],
        empty="No vehicles registered yet.",
    )


def incident_summary(env, date_from=None, date_to=None, **params):
    accidents = _scoped(env, "fix.vehicle.accident", _vehicles(env))
    rows = []
    for record in accidents:
        rows.append(
            {
                "accident": record.name,
                "vehicle": _vehicle_name(record.vehicle_id),
                "driver": record.driver_id.name if record.driver_id else "—",
                "occurred_on": str(record.occurred_on),
                "damage_cost": round(record.damage_cost, 2),
                "claim": record.claim_ref or "—",
                "state": dict(record._fields["state"].selection).get(record.state),
            }
        )
    rows.sort(key=lambda r: r["occurred_on"], reverse=True)
    return _pack(
        "Incident Summary — accidents and insurance claims",
        ["accident", "vehicle", "driver", "occurred_on", "damage_cost", "claim", "state"],
        {
            "accident": "Incident",
            "vehicle": "Vehicle",
            "driver": "Driver",
            "occurred_on": "Occurred",
            "damage_cost": "Damage Cost",
            "claim": "Claim Ref",
            "state": "State",
        },
        rows,
        ["Reported → claimed → closed; the claim reference is recorded when filed."],
        totals={"accident": "Total", "damage_cost": round(sum(r["damage_cost"] for r in rows), 2)},
        empty="No incidents recorded.",
    )


REPORTS = {
    "driver_behaviour": driver_behaviour,
    "cost_per_km": cost_per_km,
    "fleet_availability": fleet_availability,
    "fuel_efficiency": fuel_efficiency,
    "maintenance_cost": maintenance_cost,
    "statutory_compliance": statutory_compliance,
    "incident_summary": incident_summary,
}


def kpis(env):
    vehicles = _vehicles(env)
    today = _today(env)
    horizon = today + datetime.timedelta(days=90)
    offroad = _scoped(env, "fix.vehicle.offroad", vehicles, [("state", "=", "offroad")])
    docs = _scoped(env, "fix.vehicle.document", vehicles)
    expiring = docs.filtered(lambda d: d.valid_to and today <= d.valid_to <= horizon)
    month_start = today.replace(day=1)
    fuels = _scoped(env, "fix.vehicle.fuel", vehicles, [("filled_on", ">=", month_start)])
    accidents_open = len(
        _scoped(env, "fix.vehicle.accident", vehicles, [("state", "!=", "closed")])
    )
    # M46-12 (D6): "Available" was vehicles minus open off-road RECORDS (a van
    # with two records counted twice) and counted uninsured vans. It is now
    # the vehicles the dispatch gate passes today.
    blocked = _availability(env, vehicles)
    return {
        "vehicles": len(vehicles),
        "fleet_available": len(vehicles) - len(blocked),
        "docs_expiring_90d": len(expiring),
        "offroad": len(offroad.mapped("vehicle_id")),
        "fuel_mtd": round(sum(f.amount or 0.0 for f in fuels), 2),
        "accidents_open": accidents_open,
    }
