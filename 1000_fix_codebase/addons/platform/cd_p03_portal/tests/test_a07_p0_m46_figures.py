"""A07 audit P0 (E5), M46-11/12: the fleet KPIs and packs tell the truth.

The audit found: "Available" = vehicles minus open off-road RECORDS (a van
with two records counted twice) and it counted uninsured vans; km/l and
cost/km divided by the first fill's fuel too (7.94 km/l vs 11.63), ignored
date_from/date_to, and showed 0.00 for a single-fill vehicle; every figure
read sudo().search([]) across companies. Run as a NON-ADMIN fleet officer
where scope matters; ``odoo_env`` rolls back after every test.
"""

from datetime import timedelta

import odoo.addons.cd_p03_portal.controllers.a07.m46 as m46
import pytest
from odoo.addons.cd_vehicle_ext.models.fix_vehicle_ops import dhaka_today


@pytest.fixture
def w(odoo_env):
    env = odoo_env

    class W:
        pass

    x = W()
    x.env = env
    x.today = dhaka_today(env["fix.vehicle.check"])
    brand = env["fleet.vehicle.model.brand"].create({"name": "A07P0K Brand"})
    x.model = env["fleet.vehicle.model"].create({"name": "A07P0K Van", "brand_id": brand.id})
    x.officer = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "a07p0k_fleet",
                "login": "a07p0k_fleet",
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id, env.ref("fleet.fleet_group_user").id])
                ],
            }
        )
    )

    def vehicle(plate, docs=("fitness", "insurance", "tax"), **kw):
        v = env["fleet.vehicle"].create({"model_id": x.model.id, "license_plate": plate, **kw})
        for doc_type in docs:
            env["fix.vehicle.document"].create(
                {"vehicle_id": v.id, "doc_type": doc_type, "valid_to": x.today + timedelta(days=90)}
            )
        return v

    def fill(v, odometer, litres, amount, days_ago=0):
        return env["fix.vehicle.fuel"].create(
            {
                "vehicle_id": v.id,
                "odometer": odometer,
                "litres": litres,
                "amount": amount,
                "filled_on": x.today - timedelta(days=days_ago),
            }
        )

    x.vehicle, x.fill = vehicle, fill
    return x


def _row(pack, plate):
    return next(r for r in pack["rows"] if r.get("plate") == plate or r["vehicle"].endswith(plate))


def test_available_counts_vehicles_that_pass_the_gate(w):
    before = m46.kpis(w.env)["fleet_available"]
    good = w.vehicle("A07P0K-GOOD")
    assert m46.kpis(w.env)["fleet_available"] == before + 1
    w.vehicle("A07P0K-UNINS", docs=("fitness", "tax"))  # no insurance on file
    assert m46.kpis(w.env)["fleet_available"] == before + 1
    off = w.env["fix.vehicle.offroad"]
    off.create({"vehicle_id": good.id, "reason": "a"})
    off.create({"vehicle_id": good.id, "reason": "b"})
    k = m46.kpis(w.env)
    assert k["fleet_available"] == before  # one van off road lowers it by one
    report = m46.fleet_availability(w.env)
    assert _row(report, "A07P0K-GOOD")["status"] == "off road"
    assert _row(report, "A07P0K-UNINS")["status"] == "not dispatchable"
    assert k["fleet_available"] == len([r for r in report["rows"] if r["dispatchable"]])


def test_figures_are_scoped_to_the_callers_companies(w):
    other = w.env["res.company"].create({"name": "A07P0K OtherCo"})
    w.vehicle("A07P0K-OTHERCO", company_id=other.id)
    officer_env = w.env(user=w.officer.id)
    readable = w.env["fleet.vehicle"].with_user(w.officer).search_count([])
    assert m46.kpis(officer_env)["vehicles"] == readable
    plates = {r["plate"] for r in m46.fleet_availability(officer_env)["rows"]}
    assert "A07P0K-OTHERCO" not in plates
    assert "A07P0K-OTHERCO" in {r["plate"] for r in m46.fleet_availability(w.env)["rows"]}


def test_km_per_litre_and_cost_per_km_are_fill_to_fill(w):
    v = w.vehicle("A07P0K-F2F")
    for odo, lit, amt in ((10000, 40, 4500), (10500, 42, 4700), (11000, 44, 4900)):
        w.fill(v, odo, lit, amt)
    w.env["fix.vehicle.pm"].create({"vehicle_id": v.id, "cost": 6500})
    eff = _row(m46.fuel_efficiency(w.env), v.name)
    assert eff["km"] == 1000 and eff["litres_in_range"] == 86
    assert eff["km_per_litre"] == round(1000 / 86, 2)  # 11.63, not 1000/126
    cpk = _row(m46.cost_per_km(w.env), "A07P0K-F2F")
    assert cpk["cost_per_km"] == 16.10  # (4700 + 4900 + 6500) / 1000
    assert cpk["fuel_cost"] == 14100 and cpk["fuel_in_range"] == 9600


def test_period_is_honoured(w):
    v = w.vehicle("A07P0K-PER")
    w.fill(v, 5000, 40, 4000, days_ago=400)  # outside the period
    w.fill(v, 10000, 40, 4500, days_ago=5)
    w.fill(v, 11000, 50, 5000)
    w.env["fix.vehicle.pm"].create(
        {"vehicle_id": v.id, "cost": 100000, "scheduled_on": w.today - timedelta(days=730)}
    )
    period = {"date_from": str(w.today - timedelta(days=30)), "date_to": str(w.today)}
    row = _row(m46.cost_per_km(w.env, **period), "A07P0K-PER")
    assert row["pm_cost"] == 0 and row["km"] == 1000 and row["cost_per_km"] == 5.0
    assert _row(m46.fuel_efficiency(w.env, **period), v.name)["km_per_litre"] == 20.0
    # without a period the history counts
    assert _row(m46.cost_per_km(w.env), "A07P0K-PER")["pm_cost"] == 100000


def test_single_fill_or_backwards_odometer_is_provisional_not_zero(w):
    one = w.vehicle("A07P0K-ONE")
    w.fill(one, 10000, 40, 13000)
    row = _row(m46.cost_per_km(w.env), "A07P0K-ONE")
    assert row["cost_per_km"] is None and row["km"] is None
    assert row["basis"].startswith("provisional") and row["fuel_cost"] == 13000
    assert _row(m46.fuel_efficiency(w.env), one.name)["km_per_litre"] is None
    back = w.vehicle("A07P0K-BACK")
    w.fill(back, 12000, 40, 4500, days_ago=2)
    w.fill(back, 9000, 40, 4500)
    row = _row(m46.cost_per_km(w.env), "A07P0K-BACK")
    assert row["cost_per_km"] is None and "backwards" in row["basis"]
