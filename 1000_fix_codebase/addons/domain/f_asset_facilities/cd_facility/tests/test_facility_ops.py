"""cd_facility ops behaviour (live ORM, rolled back): leases, licences,
occupancy, building PM, safety, incidents, site projects, plant assets,
work-order lifecycle, report packs and the KPI payload."""

from __future__ import annotations

import importlib
import uuid
from datetime import date, timedelta

import pytest
from odoo import fields as odoo_fields
from odoo.exceptions import UserError, ValidationError
from psycopg2 import IntegrityError

TAG = uuid.uuid4().hex[:6].upper()
m47 = importlib.import_module("odoo.addons.cd_p03_portal.controllers.a07.m47")


@pytest.fixture
def ctx(odoo_env):
    env = odoo_env
    site = env["fix.site"].create(
        # an operational site (A07 P1: new sites are born Planned)
        {"name": f"Site {TAG}", "site_type": "branch", "floor_area_sqm": 1000, "state": "active"}
    )
    lessor = env["res.partner"].create({"name": f"Lessor {TAG}", "is_company": True})
    return {"env": env, "site": site, "lessor": lessor}


def test_lease_sequence_and_date_rule(ctx):
    env, site, lessor = ctx["env"], ctx["site"], ctx["lessor"]
    today = date.today()
    lease = env["fix.site.lease"].create(
        {
            "site_id": site.id,
            "lessor_id": lessor.id,
            "start_date": today,
            "end_date": today + timedelta(days=30),
            "monthly_rent": 25000,
        }
    )
    assert lease.name.startswith("LEASE/")
    with pytest.raises(IntegrityError), env.cr.savepoint():
        env["fix.site.lease"].create(
            {
                "site_id": site.id,
                "lessor_id": lessor.id,
                "start_date": today,
                "end_date": today - timedelta(days=1),
            }
        )


def test_licence_validity_is_computed(ctx, monkeypatch):
    env, site = ctx["env"], ctx["site"]
    today = odoo_fields.Date.context_today(env.user)
    good = env["fix.site.licence"].create(
        {
            "site_id": site.id,
            "licence_type": "trade",
            "valid_to": today + timedelta(days=10),
        }
    )
    assert good.name.startswith("SLIC/")
    assert good.is_valid is True
    late = env["fix.site.licence"].create(
        {
            "site_id": site.id,
            "licence_type": "fire",
            "valid_to": today - timedelta(days=10),
        }
    )
    assert late.is_valid is False
    late.state = "suspended"
    assert late.is_valid is False
    # A07 audit (2026-11-03, M47-18): this test checked validity only at
    # create time, which certified the stale STORED compute. Validity must
    # follow the calendar: 11 days on, the good licence has lapsed too.
    monkeypatch.setattr(
        odoo_fields.Date, "context_today", staticmethod(lambda *a, **k: today + timedelta(days=11))
    )
    good.invalidate_recordset()
    assert good.is_valid is False
    monkeypatch.undo()
    # no end date is not "valid forever" (AC-21)
    undated = env["fix.site.licence"].create({"site_id": site.id, "licence_type": "health"})
    assert undated.is_valid is False
    found = env["fix.site.licence"].search([("site_id", "=", site.id), ("is_valid", "=", True)])
    assert found == good


def test_occupancy_is_a_percentage(ctx):
    env, site = ctx["env"], ctx["site"]
    row = env["fix.site.condition"].create(
        {"site_id": site.id, "inspected_on": date.today(), "occupancy_pct": 100}
    )
    assert row.name.startswith("SCND/")
    with pytest.raises(IntegrityError), env.cr.savepoint():
        env["fix.site.condition"].create(
            {"site_id": site.id, "inspected_on": date.today(), "occupancy_pct": 101}
        )


def test_building_pm_completion(ctx):
    env, site = ctx["env"], ctx["site"]
    job = env["fix.site.pm"].create({"site_id": site.id, "service_type": "hvac"})
    assert job.name.startswith("SPM/")
    job.action_done()
    assert job.state == "done"
    assert job.done_on
    with pytest.raises(UserError, match="open"), env.cr.savepoint():
        job.action_done()


def test_safety_check_clears_overdue(ctx):
    env, site = ctx["env"], ctx["site"]
    today = odoo_fields.Date.context_today(env.user)
    item = env["fix.site.safety"].create(
        {
            "site_id": site.id,
            "equipment_type": "extinguisher",
            "next_check": today - timedelta(days=5),
            "state": "ok",
        }
    )
    assert item.name.startswith("SSAF/")
    # A07 audit (2026-11-03, M47-18): the status is derived from next_check;
    # a typed "ok" on an item 5 days past due does not stick.
    assert item.state == "overdue"
    # the old test asserted "ok" after a check and never looked at next_check,
    # which stayed in the past. No inspection interval exists, so the check
    # must be given the next date, and it must move the date forward.
    with pytest.raises(UserError, match="next check date"), env.cr.savepoint():
        item.action_check()
    item.action_check(next_check=str(today + timedelta(days=180)))
    assert item.next_check == today + timedelta(days=180)
    assert item.state == "ok"
    # fix.site.safety.action_check stamps `fields.Date.context_today` - the
    # Bangladesh date (UTC+6). Asserting Python's `date.today()` asserted the
    # RUNNER's date instead, which disagrees for the first six hours of every
    # Dhaka day and, across a month boundary, by a month (A04 audit 2026-11-01).
    assert item.last_check == odoo_fields.Date.context_today(env.user)


def test_incident_close_guard(ctx):
    env, site = ctx["env"], ctx["site"]
    incident = env["fix.site.incident"].create(
        {"site_id": site.id, "incident_type": "theft", "description": "test"}
    )
    assert incident.name.startswith("SINC/")
    # A07 P0 recipe (M47-10): closing records a resolution
    with pytest.raises(UserError, match="resolution"), env.cr.savepoint():
        incident.action_close()
    incident.action_close(resolution="Lock replaced; police GD 123")
    assert incident.state == "closed"
    assert incident.resolution == "Lock replaced; police GD 123"
    with pytest.raises(UserError, match="open"), env.cr.savepoint():
        incident.action_close(resolution="again")


def test_site_project_lifecycle(ctx):
    env, site = ctx["env"], ctx["site"]
    project = env["fix.site.project"].create({"site_id": site.id, "project_type": "open"})
    assert project.name.startswith("SPRJ/")
    project.action_start()
    assert project.state == "in_progress"
    project.action_done()
    assert project.state == "done"
    assert project.done_on
    with pytest.raises(UserError, match="in-progress"), env.cr.savepoint():
        project.action_done()


def test_plant_asset_lifecycle_and_report(ctx):
    env, site = ctx["env"], ctx["site"]
    asset = env["fix.site.asset"].create(
        {"site_id": site.id, "asset_type": "generator", "value": 500000}
    )
    assert asset.name.startswith("SASET/")
    asset.action_maintenance()
    assert asset.state == "maintenance"
    with pytest.raises(UserError, match="operational"), env.cr.savepoint():
        asset.action_maintenance()
    asset.action_restore()
    assert asset.state == "operational"
    # A07 P0 recipe (M47-11): retiring BDT 500,000 of plant needs a DOFA
    # approval; the routed path is tested in test_a07_p0_recipe_lifecycles.py
    with pytest.raises(ValidationError, match="sign-off"), env.cr.savepoint():
        asset.action_retire()
    asset.write(
        {"dofa_approved": True, "dofa_approved_tier": "tier_5", "dofa_approved_amount": 500000}
    )
    asset.action_retire(reason="Replaced by new plant")
    assert asset.state == "retired"

    pack = m47.branch_assets(env)
    row = next(r for r in pack["rows"] if r["site"] == site.name)
    assert row["assets"] == 1
    assert row["asset_value"] == 500000


def test_work_order_lifecycle_and_sequence(ctx):
    env, site = ctx["env"], ctx["site"]
    order = env["fix.facility.work.order"].create(
        {"site_id": site.id, "work_type": "repair", "description": "test repair"}
    )
    assert order.name.startswith("FWO/")
    order.action_schedule()
    assert order.state == "scheduled"
    order.action_start()
    assert order.state == "in_progress"
    order.action_complete(notes="Fan motor replaced")
    assert order.state == "completed"
    assert order.completion_notes == "Fan motor replaced"


def test_kpis_count_only_open_work_orders(ctx):
    env, site = ctx["env"], ctx["site"]
    env["fix.facility.work.order"].create(
        {"site_id": site.id, "work_type": "repair", "description": "open one"}
    )
    done = env["fix.facility.work.order"].create(
        {"site_id": site.id, "work_type": "repair", "description": "done one"}
    )
    # A07 P0 recipe: the lifecycle is walked, not jumped
    done.action_schedule()
    done.action_start()
    done.action_complete(notes="done")
    payload = m47.kpis(env)
    assert payload["sites_active"] >= 1
    assert payload["open_work_orders"] >= 1
    assert payload["utilities_cost_per_sqft"] >= 0
    assert payload["safety_due"] >= payload["safety_overdue"]


def test_report_packs_are_wired(ctx):
    env, site, lessor = ctx["env"], ctx["site"], ctx["lessor"]
    today = date.today()
    env["fix.site.lease"].create(
        {
            "site_id": site.id,
            "lessor_id": lessor.id,
            "start_date": today,
            "end_date": today + timedelta(days=45),
            "monthly_rent": 10000,
        }
    )
    env["fix.site.licence"].create(
        {
            "site_id": site.id,
            "licence_type": "trade",
            "valid_to": today - timedelta(days=1),
        }
    )
    env["fix.site.safety"].create(
        {
            "site_id": site.id,
            "equipment_type": "alarm",
            "next_check": today - timedelta(days=1),
            "state": "overdue",
        }
    )
    env["fix.site.utility"].create(
        {"site_id": site.id, "period": "2026-10", "utility_type": "power", "amount": 1600}
    )

    dates = m47.critical_dates(env)
    assert any(r["site"] == site.name and r["days_left"] < 0 for r in dates["rows"])
    licences = m47.licence_compliance(env)
    assert any(r["site"] == site.name and r["valid"] is False for r in licences["rows"])
    utilities = m47.utilities_variance(env)
    assert utilities["rows"]
    costs = m47.cost_per_site(env)
    row = next(r for r in costs["rows"] if r["site"] == site.name)
    assert row["total"] == row["rent"] + row["utilities"] + row["pm"] + row["work_orders"]
