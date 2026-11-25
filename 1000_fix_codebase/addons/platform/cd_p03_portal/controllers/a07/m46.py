# A07 · M46 Fleet & Vehicles — surfaces, packs and KPIs over the fleet.vehicle
# register, dispatch assignments, drivers, documents, off-road records, checks,
# PM, fuel, telemetry and accidents.
import datetime
import itertools

from odoo import fields

from .writable import WRITABLE

SURFACES = {
    "fleet.vehicle": {
        "order": "name",
        "limit": 300,
        # A07 ERP audit M46-10: a vehicle leaves only through a CFO-approved
        # disposal (Vehicle Disposals); M46-25: a registered vehicle is
        # commissioned by a Fleet Officer.
        "actions": {"action_assert_dispatchable", "action_commission"},
        "pickers": {"branch_id": [], "fix_class_profile_id": []},
    },
    # A07 ERP audit M46-10 (BRU-FLT-20, D10): route, proceeds, buyer, CFO.
    "fix.vehicle.disposal": {
        "order": "id desc",
        "limit": 300,
        "actions": {
            "action_request_approval",
            "action_recall_approval",
            "action_complete",
            "action_cancel",
        },
        "pickers": {"vehicle_id": [("active", "=", True)]},
    },
    # A07 ERP audit M46-19: class profiles (documents, licence, tank, baseline).
    "fix.vehicle.class.profile": {
        "order": "name",
        "limit": 200,
        "actions": set(),
    },
    # The catalogue a vehicle's required model comes from.
    "fleet.vehicle.model": {
        "order": "name",
        "limit": 300,
        "actions": set(),
    },
    "fleet.vehicle.model.brand": {
        "order": "name",
        "limit": 300,
        "actions": set(),
    },
    "fix.vehicle.assignment": {
        "order": "date desc, id desc",
        "limit": 300,
        "actions": {"action_release", "action_reassign"},
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
        # the garage that did the work (FR-FLT-027)
        "pickers": {"provider_id": [("is_company", "=", True)], "paid_by_employee_id": []},
    },
    # A07 P0 recipe M46-9: a held fill is reviewed by someone other than
    # its recorder.
    "fix.vehicle.fuel": {
        "order": "filled_on desc, id desc",
        "limit": 400,
        "actions": {"action_clear_exception", "action_reject_fill", "action_correct_odometer"},
        # A07 ERP audit M46-02/03: the station billed, or the employee who paid
        "pickers": {"vendor_id": [("is_company", "=", True)], "paid_by_employee_id": []},
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
        "actions": {
            "action_claim",
            "action_request_approval",
            "action_recall_approval",
            "action_close",
            "action_close_no_claim",
            "action_add_insurer",
        },
        # An insurer is not every partner of 15,000.
        "pickers": {
            "insurer_id": [("is_insurer", "=", True)],
            "excess_vendor_id": [("is_company", "=", True)],
            "repair_pm_id": [],
        },
    },
    # Capture audit 2026-11-17: the four registers the sub-module pages had
    # no record for (models/fix_vehicle_capture.py in cd_vehicle_ext).
    "fix.vehicle.document.renewal": {
        "order": "initiated_on desc, id desc",
        "limit": 300,
        "actions": {"action_submit", "action_complete", "action_cancel"},
        # the renewed certificate is one already recorded with its scan
        "pickers": {
            "new_document_id": [("has_evidence", "=", True)],
            "vendor_id": [("is_company", "=", True)],
        },
    },
    "fix.vehicle.defect": {
        "order": "raised_on desc, id desc",
        "limit": 300,
        "actions": {"action_clear"},
    },
    "fix.telematics.device": {
        "order": "name",
        "limit": 300,
        "actions": {"action_remove", "action_retire"},
        "pickers": {"provider_id": [("is_company", "=", True)]},
    },
    "fix.vehicle.penalty": {
        "order": "issued_on desc, id desc",
        "limit": 300,
        # A07 ERP audit M46-14 (D11): above the LM limit the decision is
        # routed to the Operations Director / CFO (M63); a pending one can be
        # recalled.
        "actions": {"action_recover", "action_absorb", "action_recall_approval"},
        "pickers": {"vendor_id": [("is_company", "=", True)]},
    },
}


# A surface added by the A07 ERP audit is served once writable.py (generated
# from the workspace forms) lists it; until it is regenerated the package
# would refuse to load (a07/__init__.py reads WRITABLE[model] for each).
for _new in ("fix.vehicle.disposal", "fix.vehicle.class.profile"):
    if _new not in WRITABLE:
        SURFACES.pop(_new)


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
# A07 ERP audit (2026-11-20) M46-17: the fence is the companies SELECTED in
# the session (env.companies), not every company the user may switch to, and
# the user's operating units (T-13: a branch sees its own fleet; a vehicle
# with no unit stays visible, as in the record rules). M46-16: a pack over a
# period includes the vehicles retired since, so a past period's figures do
# not change when a van is disposed of later.
def _ou_domain(env, field="operating_unit_id"):
    user = env.user
    # the superuser (crons, data checks) is not a branch user
    if env.su or "operating_unit_ids" not in user._fields:
        return []
    return ["|", (field, "=", False), (field, "in", user.operating_unit_ids.ids)]


def _vehicles(env, with_retired=False):
    domain = [
        "|",
        ("company_id", "=", False),
        ("company_id", "in", env.companies.ids),
        *_ou_domain(env),
    ]
    Vehicle = env["fleet.vehicle"].sudo()
    if with_retired:
        Vehicle = Vehicle.with_context(active_test=False)
    return Vehicle.search(domain)


def _scoped(env, model, vehicles, extra=None):
    return env[model].sudo().search([("vehicle_id", "in", vehicles.ids)] + (extra or []))


def _vehicle_name(vehicle):
    name = getattr(vehicle, "name", None) or vehicle.license_plate or "—"
    return name if vehicle.active else "%s (retired)" % name


def _drivers(env):
    ids = env.companies.ids
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


# A07 P1 M46-11 (BRU-FLT-18) [probe 56]: one typo odometer (999,999) published
# cost/km 0.01 as fact. A fill held by an exception rule is not an accepted
# reading: it is left out of the distance and the spend until reviewed, and
# the figure says it is provisional and why. A rejected fill never counts.
_HELD_WHY = {
    "odometer_back": "odometer goes backwards",
    "odometer_jump": "implausible distance",
    "over_capacity": "above tank capacity",
    "duplicate": "duplicate",
    "offroad": "vehicle off-road",
}


def _fill_to_fill(fills):
    """Distance and the fuel that drove it, measured fill to fill.

    A07 audit M46-11 (D5): km/l and cost/km divided by ALL litres and all
    fuel spend, including the first fill, whose fuel was burnt before the
    odometer range began (7.94 km/l reported vs 11.63 true). The first fill
    in the period only opens the range. Fewer than two fills, or an odometer
    that goes backwards between fills, has no measured distance: the figure
    is provisional (BRU-FLT-18), never 0.00 presented as fact."""
    fills = fills.filtered(lambda f: f.review_state != "rejected")
    held = fills.filtered(lambda f: f.review_state == "held")
    fills -= held
    out = _measure(fills)
    if held:
        why = sorted(
            {
                _HELD_WHY.get(code, code)
                for code in ",".join(held.mapped(lambda f: f.exception_flags or "")).split(",")
                if code
            }
        )
        out["basis"] = "provisional: %d fill(s) held for review left out (%s); %s" % (
            len(held),
            ", ".join(why) or "exception",
            out["basis"],
        )
    return out


def _measure(fills):
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
    date_from, date_to = _day(date_from), _day(date_to)
    vehicles = _vehicles(env, with_retired=True)
    checks = _scoped(env, "fix.vehicle.check", vehicles).filtered(
        lambda c: _in_period(c.checked_on, date_from, date_to)
    )
    accidents = _scoped(env, "fix.vehicle.accident", vehicles).filtered(
        lambda a: _in_period(a.occurred_on, date_from, date_to)
    )
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
            _period_note(date_from, date_to),
            "Recorded pre-use checks and recorded accidents only; no telematics scoring is "
            "claimed.",
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


# FIN-20 (R2a, 2026-11-21): what the ledger knows about a vehicle beyond its
# fuel, PM and renewals (vehicle._fix_tco, cd_asset_finance_hse_bridge): M49
# book depreciation, insurance premium and excess, fines absorbed, lease rent,
# repairs through a facility work order not tied to a PM, less insurer
# settlements. Fuel / PM / renewals stay read from their source records (their
# posted cost entries are the same money), so nothing is counted twice.
TCO_EXTRA = {
    "depreciation": ("depreciation",),
    "insurance": ("vehicle_insurance", "vehicle_insurance_excess"),
    "fines": ("vehicle_fine",),
    "lease_rent": ("vehicle_lease_rent",),
    "repairs": ("facility_work_order",),
    "insurance_recovered": ("insurance_recovered",),
}


def _vehicle_tco(vehicle, date_from, date_to):
    """The ledger costs of TCO_EXTRA for the period (zeros without the bridge)."""
    out = dict.fromkeys(TCO_EXTRA, 0.0)
    out["provisional"] = 0.0
    tco = getattr(vehicle, "_fix_tco", None)
    if not tco:
        return out
    start = date_from or datetime.date(2000, 1, 1)
    end = date_to or fields.Date.context_today(vehicle.with_context(tz="Asia/Dhaka"))
    figures = tco(start, end)
    for column, keys in TCO_EXTRA.items():
        out[column] = round(sum(figures.get(k, 0.0) for k in keys), 2)
    out["provisional"] = figures.get("provisional", 0.0)
    return out


def cost_per_km(env, date_from=None, date_to=None, **params):
    date_from, date_to = _day(date_from), _day(date_to)
    vehicles = _vehicles(env, with_retired=True)
    fuels = _period_fills(env, vehicles, date_from, date_to)
    # a PM job belongs to the day it was done, else the day it was scheduled;
    # an open job's cost is an estimate, not a cost
    pms = _scoped(env, "fix.vehicle.pm", vehicles, [("state", "=", "done")]).filtered(
        lambda p: _in_period(p.done_on or p.scheduled_on, date_from, date_to)
    )
    # FR-FLT-014: a completed renewal's government fee, agent fee and penalty
    # are running cost, on the day it completed (capture audit 2026-11-17)
    renewals = _scoped(
        env, "fix.vehicle.document.renewal", vehicles, [("state", "=", "completed")]
    ).filtered(lambda r: _in_period(r.completed_on, date_from, date_to))
    rows = []
    for vehicle in vehicles:
        f2f = _fill_to_fill(fuels.filtered(lambda f, vid=vehicle.id: f.vehicle_id.id == vid))
        pm_cost = round(
            sum(pms.filtered(lambda p, vid=vehicle.id: p.vehicle_id.id == vid).mapped("cost")), 2
        )
        doc_cost = round(
            sum(
                renewals.filtered(lambda r, vid=vehicle.id: r.vehicle_id.id == vid).mapped(
                    "total_cost"
                )
            ),
            2,
        )
        tco = _vehicle_tco(vehicle, date_from, date_to)
        ledger = round(sum(tco[k] for k in TCO_EXTRA), 2)
        pm_cost_only = pm_cost
        pm_cost = round(pm_cost + doc_cost + ledger, 2)  # the running cost beside fuel
        km = f2f["km"]
        rows.append(
            {
                "vehicle": _vehicle_name(vehicle),
                "plate": vehicle.license_plate or "—",
                "fills": f2f["fills"],
                "km": km,
                "fuel_cost": f2f["spend"],
                "fuel_in_range": f2f["fuel_in_range"],
                "pm_cost": pm_cost_only,
                "document_cost": doc_cost,
                **{k: tco[k] for k in TCO_EXTRA},
                "total_cost": round(f2f["spend"] + pm_cost, 2),
                "cost_per_km": round((f2f["fuel_in_range"] + pm_cost) / km, 2) if km else None,
                "unposted": tco["provisional"],
                "basis": f2f["basis"],
            }
        )
    rows.sort(key=lambda r: (r["cost_per_km"] is None, -(r["cost_per_km"] or 0)))
    measured = [r for r in rows if r["km"]]
    return _pack(
        "Cost per Kilometre — fuel, PM, renewals and the ledger's vehicle costs over the "
        "measured distance",
        [
            "vehicle", "plate", "fills", "km", "fuel_cost", "fuel_in_range",
            "pm_cost", "document_cost", "depreciation", "insurance", "fines",
            "lease_rent", "repairs", "insurance_recovered", "total_cost",
            "cost_per_km", "unposted", "basis",
        ],
        {
            "vehicle": "Vehicle",
            "plate": "Plate",
            "fills": "Fills",
            "km": "Measured km",
            "fuel_cost": "Fuel Spend",
            "fuel_in_range": "Fuel in Range",
            "pm_cost": "PM Cost",
            "document_cost": "Document Renewals",
            "depreciation": "Depreciation",
            "insurance": "Insurance",
            "fines": "Fines Absorbed",
            "lease_rent": "Lease Rent",
            "repairs": "Other Repairs",
            "insurance_recovered": "Insurer Recovered",
            "total_cost": "Total Spend",
            "cost_per_km": "Cost / km",
            "unposted": "Not Yet Posted",
            "basis": "Basis",
        },
        rows,
        [
            _period_note(date_from, date_to),
            "Measured km = last − first fuel odometer in the period. Cost / km = "
            "(fuel of the fills after the first + PM cost + document renewals + the ledger's "
            "vehicle costs) / measured km: the first fill's fuel was burnt before the range "
            "began. PM cost counts completed services only; document renewals count the "
            "government fee, agent fee and penalty of renewals completed in the period.",
            "Ledger vehicle costs (FIN-20) are POSTED amounts: M49 book depreciation of the "
            "vehicle's fixed asset, insurance premium and excess, traffic fines the company "
            "absorbed, lease rent, repairs through a work order not tied to a PM, less "
            "insurer settlements. Cost entries not yet posted are shown apart (Not Yet "
            "Posted) and left out of the figure.",
            "Provisional (no figure) where the period has fewer than two fills or the "
            "odometer goes backwards. A fill held by a fuel exception rule is left out "
            "until the Logistics Manager reviews it, and the row is provisional. "
            "Downtime is not included.",
        ],
        totals={
            "vehicle": "Total",
            "km": sum(r["km"] for r in measured),
            "fuel_cost": round(sum(r["fuel_cost"] for r in rows), 2),
            "pm_cost": round(sum(r["pm_cost"] for r in rows), 2),
            "document_cost": round(sum(r["document_cost"] for r in rows), 2),
            **{k: round(sum(r[k] for r in rows), 2) for k in TCO_EXTRA},
            "total_cost": round(sum(r["total_cost"] for r in rows), 2),
            "unposted": round(sum(r["unposted"] for r in rows), 2),
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


def _efficiency_flag(km_per_litre, baseline, pct):
    """A07 ERP audit M46-19 (FR-FLT-033): measured km/l this far below the
    vehicle's baseline is deterioration. No baseline or no threshold: no flag
    (nothing is invented)."""
    if km_per_litre is None or not baseline:
        return "—"
    if not pct:
        return "no threshold set"
    floor = baseline * (1 - pct / 100.0)
    return "DETERIORATED" if km_per_litre < floor else "ok"


def fuel_efficiency(env, date_from=None, date_to=None, **params):
    date_from, date_to = _day(date_from), _day(date_to)
    vehicles = _vehicles(env, with_retired=True)
    fuels = _period_fills(env, vehicles, date_from, date_to)
    rows = []
    for vehicle in vehicles:
        f2f = _fill_to_fill(fuels.filtered(lambda f, vid=vehicle.id: f.vehicle_id.id == vid))
        km, litres = f2f["km"], f2f["litres_in_range"]
        kml = round(km / litres, 2) if km and litres else None
        baseline, pct = vehicle._fix_fuel_baseline()
        rows.append(
            {
                "vehicle": _vehicle_name(vehicle),
                "records": f2f["fills"],
                "litres": f2f["litres"],
                "km": km,
                "litres_in_range": litres,
                "km_per_litre": kml,
                "baseline": round(baseline, 2) if baseline else None,
                "flag": _efficiency_flag(kml, baseline, pct),
                "spend": f2f["spend"],
                "basis": f2f["basis"],
            }
        )
    rows.sort(key=lambda r: (r["km_per_litre"] is None, -(r["km_per_litre"] or 0)))
    measured = [r for r in rows if r["km"]]
    return _pack(
        "Fuel Efficiency Trend — km per litre, fill to fill",
        [
            "vehicle",
            "records",
            "litres",
            "km",
            "litres_in_range",
            "km_per_litre",
            "baseline",
            "flag",
            "spend",
            "basis",
        ],
        {
            "vehicle": "Vehicle",
            "records": "Fills",
            "litres": "Litres",
            "km": "Measured km",
            "litres_in_range": "Litres in Range",
            "km_per_litre": "km/l",
            "baseline": "Baseline km/l",
            "flag": "Deterioration",
            "spend": "Spend",
            "basis": "Basis",
        },
        rows,
        [
            _period_note(date_from, date_to),
            "km/l = (last − first fuel odometer) / litres of the fills after the "
            "first; provisional (no figure) with fewer than two fills or a backwards "
            "odometer. Fills held for review are left out until reviewed. Fuel-card "
            "imports are M52's; these are recorded transactions.",
            "Baseline = the vehicle's own baseline km/l, else its class profile's. "
            "DETERIORATED = km/l below the baseline by more than the class profile's "
            "threshold (%).",
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
    date_from, date_to = _day(date_from), _day(date_to)
    vehicles = _vehicles(env, with_retired=True)
    # a job belongs to the day it was done, else the day it was scheduled
    pms = _scoped(env, "fix.vehicle.pm", vehicles).filtered(
        lambda p: _in_period(p.done_on or p.scheduled_on, date_from, date_to)
    )
    rows = []
    for vehicle in vehicles:
        records = pms.filtered(lambda p, vid=vehicle.id: p.vehicle_id.id == vid)
        rows.append(
            {
                "vehicle": _vehicle_name(vehicle),
                "jobs": len(records),
                "done": len(records.filtered(lambda p: p.state == "done")),
                # an open job's figure is an estimate: it is a cost once done
                "cost": round(sum(records.filtered(lambda p: p.state == "done").mapped("cost")), 2),
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
        [
            _period_note(date_from, date_to),
            "Recorded PM/repair jobs only; parts drawn from M15 are not double-counted here. "
            "Cost counts completed jobs: the figure on an open job is an estimate.",
        ],
        totals={
            "vehicle": "Total",
            "jobs": sum(r["jobs"] for r in rows),
            "done": sum(r["done"] for r in rows),
            "cost": round(sum(r["cost"] for r in rows), 2),
        },
        empty="No vehicles registered yet.",
    )


def _expiring(docs, today, horizon):
    """Documents that will really lapse: the current one of its type, not marked
    expired. A superseded certificate's end date warns of nothing."""
    return docs.filtered(
        lambda d: d.is_current
        and d.state == "valid"
        and d.valid_to
        and today <= d.valid_to <= horizon
    )


def statutory_compliance(env, date_from=None, date_to=None, **params):
    today = _today(env)
    horizon = today + datetime.timedelta(days=90)
    vehicles = _vehicles(env)
    docs = _scoped(env, "fix.vehicle.document", vehicles)
    rows = []
    for vehicle in vehicles:
        vehicle_docs = docs.filtered(lambda d, vid=vehicle.id: d.vehicle_id.id == vid)
        expiring = _expiring(vehicle_docs, today, horizon)
        problems = vehicle._fix_document_problems(today, today).get(vehicle.id, [])
        rows.append(
            {
                "vehicle": _vehicle_name(vehicle),
                "plate": vehicle.license_plate or "—",
                "fitness": str(vehicle.fitness_expiry) if vehicle.fitness_expiry else "—",
                "insurance": str(vehicle.insurance_expiry) if vehicle.insurance_expiry else "—",
                "compliant": vehicle.compliance_ok,
                "valid_docs": len(vehicle_docs.filtered(lambda d: d.is_valid)),
                "awaiting_scan": len(
                    vehicle_docs.filtered(lambda d: d.evidence_status != "attached")
                ),
                "expiring_90d": len(expiring),
                "why_not": "; ".join(problems) or "—",
            }
        )
    rows.sort(key=lambda r: (r["compliant"], r["expiring_90d"]))
    return _pack(
        "Statutory Compliance Register — fitness, insurance and documents",
        [
            "vehicle",
            "plate",
            "fitness",
            "insurance",
            "compliant",
            "valid_docs",
            "awaiting_scan",
            "expiring_90d",
            "why_not",
        ],
        {
            "vehicle": "Vehicle",
            "plate": "Plate",
            "fitness": "Fitness (register)",
            "insurance": "Insurance (register)",
            "compliant": "Compliant",
            "valid_docs": "Valid Docs",
            "awaiting_scan": "Awaiting Scan",
            "expiring_90d": "Expiring (90d)",
            "why_not": "Why Not",
        },
        rows,
        [
            "Compliant = each mandatory document type's current document (the latest "
            "recorded one in force) is valid today and carries its evidence scan: the "
            "dispatch gate's own test. The fitness and insurance dates are read from "
            "the register. Awaiting Scan counts documents with no scan attached "
            "(legacy rows recorded before evidence was required count as valid until "
            "cd_vehicle_ext.legacy_documents_count_valid is switched off)."
        ],
        empty="No vehicles registered yet.",
    )


def incident_summary(env, date_from=None, date_to=None, **params):
    date_from, date_to = _day(date_from), _day(date_to)
    accidents = _scoped(env, "fix.vehicle.accident", _vehicles(env, with_retired=True)).filtered(
        lambda a: _in_period(a.occurred_on, date_from, date_to)
    )
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
        [
            _period_note(date_from, date_to),
            "Reported → claimed → closed; the claim reference is recorded when filed.",
        ],
        totals={"accident": "Total", "damage_cost": round(sum(r["damage_cost"] for r in rows), 2)},
        empty="No incidents recorded.",
    )


def insurers(env, date_from=None, date_to=None, **params):
    """Who the accident form offers as an insurer, and their claims."""
    ids = env.companies.ids
    partners = (
        env["res.partner"]
        .sudo()
        .search(
            [("is_insurer", "=", True), "|", ("company_id", "=", False), ("company_id", "in", ids)],
            order="name",
        )
    )
    accidents = _scoped(env, "fix.vehicle.accident", _vehicles(env))
    rows = []
    for partner in partners:
        claims = accidents.filtered(lambda a, p=partner.id: a.insurer_id.id == p)
        rows.append(
            {
                "insurer": partner.name,
                "phone": partner.phone or "—",
                "email": partner.email or "—",
                "open": len(claims.filtered(lambda a: a.state != "closed")),
                "closed": len(claims.filtered(lambda a: a.state == "closed")),
            }
        )
    return _pack(
        "Insurers — the companies an accident claim can name",
        ["insurer", "phone", "email", "open", "closed"],
        {
            "insurer": "Insurer",
            "phone": "Phone",
            "email": "Email",
            "open": "Open Accidents",
            "closed": "Closed Accidents",
        },
        rows,
        [
            "A Fleet Officer adds an insurer from Accidents & Insurance: select the "
            "accident and press Add Insurer."
        ],
        empty="No insurer yet. A Fleet Officer adds one from Accidents & Insurance: select the "
        "accident and press Add Insurer.",
    )


# ------------------------------------------------------------------ documents
# A07 ERP audit (2026-11-20) M46-22 / D18: the printable fleet documents. Each
# is a pack with its own filter; the report bar's PDF is the company document
# (letterhead, meta, notes), so the screen and the print never differ.
def _pick(options, chosen):
    return chosen if chosen in options else None


def vehicle_logbook(env, date_from=None, date_to=None, vehicle=None, **params):
    """The vehicle's history card: every recorded event, oldest first."""
    date_from, date_to = _day(date_from), _day(date_to)
    vehicles = _vehicles(env, with_retired=True)
    options = sorted(v.license_plate for v in vehicles if v.license_plate)
    filters = [{"key": "vehicle", "label": "Vehicle (plate)", "options": options[:500]}]
    plate = _pick(options, vehicle)
    cols = ["day", "kind", "ref", "detail", "odometer", "amount", "by"]
    labels = {
        "day": "Date",
        "kind": "Event",
        "ref": "Record",
        "detail": "Detail",
        "odometer": "Odometer (km)",
        "amount": "Amount (BDT)",
        "by": "Recorded / Decided By",
    }
    if not plate:
        out = _pack(
            "Vehicle Logbook",
            cols,
            labels,
            [],
            ["Choose the vehicle in the filter above."],
            empty="Pick a vehicle in the filter above.",
        )
        out["filters"] = filters
        return out
    v = vehicles.filtered(lambda x: x.license_plate == plate)[:1]
    rows = []

    def add(day, kind, rec, detail, odometer=None, amount=None, by=None):
        if _in_period(day, date_from, date_to) or (not date_from and not date_to and day):
            rows.append(
                {
                    "day": str(day),
                    "kind": kind,
                    "ref": rec.display_name,
                    "detail": detail,
                    "odometer": odometer or None,
                    "amount": round(amount, 2) if amount else None,
                    "by": by or "—",
                }
            )

    for d in _scoped(env, "fix.vehicle.document", v):
        add(
            d.valid_from or d.create_date.date(),
            "Document",
            d,
            "%s %s valid to %s (%s)"
            % (d.doc_type, d.number or "-", d.valid_to or "-", d.evidence_status),
        )
    for c in _scoped(env, "fix.vehicle.check", v):
        add(
            c.checked_on,
            "Pre-use check",
            c,
            "passed" if c.passed else "FAILED: %s" % (c.defects or "-"),
            c.odometer,
            by=c.create_uid.name,
        )
    for f in _scoped(env, "fix.vehicle.fuel", v):
        add(
            f.filled_on,
            "Fuel",
            f,
            "%s L at %s (%s)" % (f.litres, f.station or "-", f.review_state),
            f.odometer,
            f.amount,
            f.create_uid.name,
        )
    for p in _scoped(env, "fix.vehicle.pm", v, [("state", "=", "done")]):
        add(
            p.done_on,
            "Service",
            p,
            "%s at %s" % (p.pm_type, p.provider_id.name or "-"),
            p.odometer,
            p.cost,
            p.done_by_id.name,
        )
    for o in _scoped(env, "fix.vehicle.offroad", v):
        add(o.started_on, "Off road", o, o.reason or "-", by=o.raised_by_id.name)
        if o.ended_on:
            add(o.ended_on, "Returned to service", o, o.name, by=o.returned_by_id.name)
    for a in _scoped(env, "fix.vehicle.accident", v):
        add(
            a.occurred_on,
            "Accident",
            a,
            "%s (%s)" % ((a.description or "")[:80], a.state),
            amount=a.damage_cost,
            by=a.create_uid.name,
        )
    for r in _scoped(env, "fix.vehicle.document.renewal", v, [("state", "=", "completed")]):
        add(
            r.completed_on,
            "Document renewal",
            r,
            r.doc_type,
            amount=r.total_cost,
            by=r.completed_by_id.name,
        )
    for p in _scoped(env, "fix.vehicle.penalty", v):
        add(
            p.issued_on,
            "Traffic fine",
            p,
            "%s (%s)" % (p.offence, p.recovery_decision or p.state),
            amount=p.amount,
            by=p.decided_by_id.name or p.recorded_by_id.name,
        )
    for d in _scoped(env, "fix.vehicle.disposal", v, [("state", "=", "done")]):
        add(
            d.done_on,
            "Disposal",
            d,
            "%s to %s" % (d.route, d.buyer_id.name or "-"),
            amount=d.proceeds,
            by=d.done_by_id.name,
        )
    rows.sort(key=lambda r: (r["day"], r["kind"]))
    out = _pack(
        "Vehicle Logbook — %s" % _vehicle_name(v),
        cols,
        labels,
        rows,
        [
            _period_note(date_from, date_to),
            "Branch: %s. Ownership: %s. Every event recorded in M46 for this vehicle."
            % (v.branch_id.display_name or "—", v.fix_ownership_basis),
        ],
        empty="Nothing recorded for this vehicle in the period.",
    )
    out["filters"] = filters
    return out


def disposal_gate_pass(env, date_from=None, date_to=None, disposal=None, **params):
    """The gate pass a disposed vehicle leaves the premises on (BRU-FLT-20)."""
    vehicles = _vehicles(env, with_retired=True)
    done = _scoped(env, "fix.vehicle.disposal", vehicles, [("state", "=", "done")])
    options = sorted(done.mapped("name"))
    filters = [{"key": "disposal", "label": "Disposal", "options": options[:500]}]
    name = _pick(options, disposal)
    cols = ["field", "value"]
    labels = {"field": "", "value": ""}
    if not name:
        out = _pack(
            "Vehicle Disposal Gate Pass",
            cols,
            labels,
            [],
            ["Choose a completed disposal in the filter above."],
            empty="Pick a completed disposal in the filter above.",
        )
        out["filters"] = filters
        return out
    d = done.filtered(lambda x: x.name == name)[:1]
    routes = dict(d._fields["route"].selection)
    rows = [
        {"field": f, "value": val}
        for f, val in (
            ("Disposal", d.name),
            ("Vehicle", _vehicle_name(d.vehicle_id)),
            ("Licence plate", d.vehicle_id.license_plate or "—"),
            ("Route", routes.get(d.route, d.route)),
            ("Buyer / receiver", d.buyer_id.name or "—"),
            ("Proceeds (BDT)", "%.2f" % (d.proceeds or 0.0)),
            ("Disposal date", str(d.disposal_date)),
            ("Approved by (CFO)", d.dofa_approved_by.name or "—"),
            ("Completed by", d.done_by_id.name or "—"),
            ("Reason", d.reason or "—"),
        )
    ]
    out = _pack(
        "Vehicle Disposal Gate Pass — %s" % d.name,
        cols,
        labels,
        rows,
        ["The vehicle may leave the premises on this pass, signed at the gate."],
    )
    out["filters"] = filters
    return out


def fine_notice(env, date_from=None, date_to=None, penalty=None, **params):
    """The fine slip / recovery notice of a decided traffic fine (FR-FLT-043)."""
    fines = _scoped(
        env, "fix.vehicle.penalty", _vehicles(env, with_retired=True), [("state", "=", "decided")]
    )
    options = sorted(fines.mapped("name"))
    filters = [{"key": "penalty", "label": "Traffic fine", "options": options[:500]}]
    name = _pick(options, penalty)
    cols = ["field", "value"]
    labels = {"field": "", "value": ""}
    if not name:
        out = _pack(
            "Traffic Fine Notice",
            cols,
            labels,
            [],
            ["Choose a decided fine in the filter above."],
            empty="Pick a decided fine in the filter above.",
        )
        out["filters"] = filters
        return out
    p = fines.filtered(lambda x: x.name == name)[:1]
    recover = p.recovery_decision == "recover"
    rows = [
        {"field": f, "value": val}
        for f, val in (
            ("Fine", p.name),
            ("Vehicle", _vehicle_name(p.vehicle_id)),
            ("Driver on duty", p.driver_id.name or "—"),
            ("Issued on", str(p.issued_on)),
            ("Authority / case", "%s / %s" % (p.authority or "—", p.case_ref or "—")),
            ("Offence", p.offence),
            ("Amount (BDT)", "%.2f" % p.amount),
            ("Decision", "Recovered from the driver" if recover else "Absorbed by the company"),
            ("Reason", p.decision_reason or "—"),
            ("Decided by", p.decided_by_id.name or "—"),
            ("Approved by", p.dofa_approved_by.name or "within the Logistics Manager limit"),
            ("Paid on / ref", "%s / %s" % (p.paid_on or "not yet", p.payment_ref or "—")),
        )
    ]
    notes = (
        [
            "Recovery notice: the amount is recovered through payroll (M56) within the "
            "statutory deduction limit, once HR approves the recovery."
        ]
        if recover
        else ["The fine is a company cost, paid through AP or petty cash."]
    )
    out = _pack("Traffic Fine Notice — %s" % p.name, cols, labels, rows, notes)
    out["filters"] = filters
    return out


REPORTS = {
    "insurers": insurers,
    "driver_behaviour": driver_behaviour,
    "cost_per_km": cost_per_km,
    "fleet_availability": fleet_availability,
    "fuel_efficiency": fuel_efficiency,
    "maintenance_cost": maintenance_cost,
    "statutory_compliance": statutory_compliance,
    "incident_summary": incident_summary,
    # A07 ERP audit M46-22: the printable fleet documents
    "vehicle_logbook": vehicle_logbook,
    "disposal_gate_pass": disposal_gate_pass,
    "fine_notice": fine_notice,
}


def kpis(env):
    vehicles = _vehicles(env)
    today = _today(env)
    horizon = today + datetime.timedelta(days=90)
    offroad = _scoped(env, "fix.vehicle.offroad", vehicles, [("state", "=", "offroad")])
    docs = _scoped(env, "fix.vehicle.document", vehicles)
    expiring = _expiring(docs, today, horizon)
    month_start = today.replace(day=1)
    # accepted spend only: a held fill is not yet a cost, a rejected one never is
    fuels = _scoped(
        env,
        "fix.vehicle.fuel",
        vehicles,
        [("filled_on", ">=", month_start), ("review_state", "in", ("none", "cleared"))],
    )
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
