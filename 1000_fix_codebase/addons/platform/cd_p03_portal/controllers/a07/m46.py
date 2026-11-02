# A07 · M46 Fleet & Vehicles — surfaces, packs and KPIs over the fleet.vehicle
# register, dispatch assignments, drivers, documents, off-road records, checks,
# PM, fuel, telemetry and accidents.
import datetime

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
    "fix.driver": {"order": "name", "limit": 200, "actions": {"action_suspend"}},
    "fix.vehicle.document": {
        "order": "valid_to desc, id desc",
        "limit": 300,
        "actions": set(),
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
    "fix.vehicle.fuel": {
        "order": "filled_on desc, id desc",
        "limit": 400,
        "actions": set(),
    },
    "fix.vehicle.telemetry": {
        "order": "last_ping desc, id desc",
        "limit": 200,
        "actions": set(),
    },
    "fix.vehicle.accident": {
        "order": "occurred_on desc, id desc",
        "limit": 200,
        "actions": {"action_claim", "action_close"},
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


def _vehicles(env):
    return env["fleet.vehicle"].sudo().search([])


def _vehicle_name(vehicle):
    return getattr(vehicle, "name", None) or vehicle.license_plate or "—"


def driver_behaviour(env, date_from=None, date_to=None, **params):
    checks = env["fix.vehicle.check"].sudo().search([])
    accidents = env["fix.vehicle.accident"].sudo().search([])
    rows = []
    for driver in env["fix.driver"].sudo().search([]):
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


def cost_per_km(env, date_from=None, date_to=None, **params):
    fuels = env["fix.vehicle.fuel"].sudo().search([])
    pms = env["fix.vehicle.pm"].sudo().search([])
    rows = []
    for vehicle in _vehicles(env):
        vehicle_fuel = fuels.filtered(lambda f, vid=vehicle.id: f.vehicle_id.id == vid)
        vehicle_pm = pms.filtered(lambda p, vid=vehicle.id: p.vehicle_id.id == vid)
        odos = vehicle_fuel.mapped("odometer")
        km = (max(odos) - min(odos)) if len(odos) > 1 else 0
        fuel_cost = sum(vehicle_fuel.mapped("amount"))
        pm_cost = sum(vehicle_pm.mapped("cost"))
        total = fuel_cost + pm_cost
        rows.append(
            {
                "vehicle": _vehicle_name(vehicle),
                "plate": vehicle.license_plate or "—",
                "km": km,
                "fuel_cost": round(fuel_cost, 2),
                "pm_cost": round(pm_cost, 2),
                "total_cost": round(total, 2),
                "cost_per_km": round(total / km, 2) if km else 0.0,
            }
        )
    rows.sort(key=lambda r: -r["cost_per_km"])
    return _pack(
        "Cost per Kilometre — fuel + PM over the recorded odometer range",
        ["vehicle", "plate", "km", "fuel_cost", "pm_cost", "total_cost", "cost_per_km"],
        {
            "vehicle": "Vehicle",
            "plate": "Plate",
            "km": "Recorded km",
            "fuel_cost": "Fuel Cost",
            "pm_cost": "PM Cost",
            "total_cost": "Total",
            "cost_per_km": "Cost / km",
        },
        rows,
        [
            "km = highest − lowest fuel odometer for the vehicle; a vehicle with one "
            "fuel record has no range and shows 0."
        ],
        totals={
            "vehicle": "Total",
            "km": sum(r["km"] for r in rows),
            "total_cost": round(sum(r["total_cost"] for r in rows), 2),
        },
        empty="No vehicles registered yet.",
    )


def fleet_availability(env, date_from=None, date_to=None, **params):
    today = datetime.date.today()
    offroad = env["fix.vehicle.offroad"].sudo().search([("state", "=", "offroad")])
    assignments = env["fix.vehicle.assignment"].sudo().search([("date", "=", today)])
    rows = []
    for vehicle in _vehicles(env):
        row_offroad = offroad.filtered(lambda o, vid=vehicle.id: o.vehicle_id.id == vid)
        row_assigned = assignments.filtered(lambda a, vid=vehicle.id: a.vehicle_id.id == vid)
        if row_offroad:
            status = "off road"
        elif row_assigned:
            status = "assigned today"
        elif not vehicle.compliance_ok:
            status = "not compliant"
        else:
            status = "available"
        rows.append(
            {
                "vehicle": _vehicle_name(vehicle),
                "plate": vehicle.license_plate or "—",
                "driver": vehicle.fix_driver_id.name if vehicle.fix_driver_id else "—",
                "compliance_ok": vehicle.compliance_ok,
                "status": status,
            }
        )
    rows.sort(key=lambda r: r["status"])
    available = len([r for r in rows if r["status"] == "available"])
    return _pack(
        "Fleet Availability — today's status per vehicle",
        ["vehicle", "plate", "driver", "compliance_ok", "status"],
        {
            "vehicle": "Vehicle",
            "plate": "Plate",
            "driver": "Driver",
            "compliance_ok": "Compliant",
            "status": "Availability",
        },
        rows,
        [
            "%d of %d vehicles available today; off-road and today's assignments "
            "are read from their records." % (available, len(rows))
        ],
        empty="No vehicles registered yet.",
    )


def fuel_efficiency(env, date_from=None, date_to=None, **params):
    fuels = env["fix.vehicle.fuel"].sudo().search([])
    rows = []
    for vehicle in _vehicles(env):
        records = fuels.filtered(lambda f, vid=vehicle.id: f.vehicle_id.id == vid)
        odos = records.mapped("odometer")
        km = (max(odos) - min(odos)) if len(odos) > 1 else 0
        litres = sum(records.mapped("litres"))
        rows.append(
            {
                "vehicle": _vehicle_name(vehicle),
                "records": len(records),
                "litres": round(litres, 2),
                "km": km,
                "km_per_litre": round(km / litres, 2) if litres else 0.0,
                "spend": round(sum(records.mapped("amount")), 2),
            }
        )
    rows.sort(key=lambda r: -r["km_per_litre"])
    return _pack(
        "Fuel Efficiency Trend — km per litre over recorded fills",
        ["vehicle", "records", "litres", "km", "km_per_litre", "spend"],
        {
            "vehicle": "Vehicle",
            "records": "Fills",
            "litres": "Litres",
            "km": "Recorded km",
            "km_per_litre": "km/l",
            "spend": "Spend",
        },
        rows,
        [
            "Efficiency uses the odometer range across fills; a single fill shows 0. "
            "Fuel-card imports are M52's; these are recorded transactions."
        ],
        totals={
            "vehicle": "Total",
            "litres": round(sum(r["litres"] for r in rows), 2),
            "km": sum(r["km"] for r in rows),
            "spend": round(sum(r["spend"] for r in rows), 2),
        },
        empty="No fuel transactions recorded yet.",
    )


def maintenance_cost(env, date_from=None, date_to=None, **params):
    pms = env["fix.vehicle.pm"].sudo().search([])
    rows = []
    for vehicle in _vehicles(env):
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
    today = datetime.date.today()
    horizon = today + datetime.timedelta(days=90)
    docs = env["fix.vehicle.document"].sudo().search([])
    rows = []
    for vehicle in _vehicles(env):
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
            "fitness": "Fitness Expiry",
            "insurance": "Insurance Expiry",
            "compliant": "Compliant",
            "valid_docs": "Valid Docs",
            "expiring_90d": "Expiring (90d)",
        },
        rows,
        [
            "Compliant = the vehicle's fitness and insurance are both present and "
            "not past; the document register adds the supporting papers."
        ],
        empty="No vehicles registered yet.",
    )


def incident_summary(env, date_from=None, date_to=None, **params):
    accidents = env["fix.vehicle.accident"].sudo().search([])
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
    today = datetime.date.today()
    horizon = today + datetime.timedelta(days=90)
    offroad = env["fix.vehicle.offroad"].sudo().search([("state", "=", "offroad")])
    docs = env["fix.vehicle.document"].sudo().search([])
    expiring = docs.filtered(lambda d: d.valid_to and today <= d.valid_to <= horizon)
    fuels = env["fix.vehicle.fuel"].sudo().search([])
    month_start = today.replace(day=1)
    fuel_mtd = sum(f.amount or 0.0 for f in fuels if f.filled_on and f.filled_on >= month_start)
    accidents_open = env["fix.vehicle.accident"].sudo().search_count([("state", "!=", "closed")])
    available = len(vehicles) - len(offroad)
    return {
        "vehicles": len(vehicles),
        "fleet_available": max(available, 0),
        "docs_expiring_90d": len(expiring),
        "offroad": len(offroad),
        "fuel_mtd": round(fuel_mtd, 2),
        "accidents_open": accidents_open,
    }
