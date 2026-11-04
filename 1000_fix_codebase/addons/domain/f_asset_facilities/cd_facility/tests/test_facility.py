"""cd_facility tests - P10-M05 (CD-M47-01 / R08-M03).

A07 P3 (2026-11-04): this file grepped the source text (`inspect.getsource`)
for state names and event types, so it passed whatever the code did. It now
exercises the same facts on the live ORM (rolled back).
"""

import json

import pytest
from odoo.exceptions import UserError

SITE_TYPES = ("branch", "warehouse", "office", "data_centre")
WORK_TYPES = ("maintenance", "repair", "upgrade", "inspection")


def _site(env, **vals):
    vals.setdefault("name", "A07P3 Site")
    vals.setdefault("state", "active")
    return env["fix.site"].create(vals)


def test_every_site_type_is_recorded(odoo_env):
    sites = odoo_env["fix.site"].create(
        [{"name": "A07P3 %s" % t, "site_type": t} for t in SITE_TYPES]
    )
    assert tuple(sites.mapped("site_type")) == SITE_TYPES


def test_lease_area_and_branch_are_stored_on_the_site(odoo_env):
    branch = odoo_env["fix.branch"].search([], limit=1)
    site = _site(
        odoo_env,
        lease_start="2026-01-01",
        lease_end="2028-12-31",
        monthly_rent=55000.0,
        floor_area_sqm=120.5,
        branch_id=branch.id,
    )
    site.invalidate_recordset()
    assert (str(site.lease_start), str(site.lease_end)) == ("2026-01-01", "2028-12-31")
    assert (site.monthly_rent, site.floor_area_sqm) == (55000.0, 120.5)
    assert site.branch_id == branch


def test_linked_assets_event_counts_the_equipment(odoo_env):
    eqs = odoo_env["fix.equipment"].create(
        [{"code": "A07P3-EQ1", "name": "Scope"}, {"code": "A07P3-EQ2", "name": "Meter"}]
    )
    site = _site(odoo_env, equipment_ids=[(6, 0, eqs.ids)])
    site.action_link_assets()
    row = odoo_env["fix.event.outbox"].search(
        [("event_type", "=", "site.assets_linked"), ("aggregate_id", "=", site.id)]
    )
    assert json.loads(row.payload) == {"site": site.name, "assets_count": 2}


def test_work_order_types_costs_and_links(odoo_env):
    site = _site(odoo_env)
    eq = odoo_env["fix.equipment"].create({"code": "A07P3-EQ3", "name": "UPS"})
    orders = odoo_env["fix.facility.work.order"].create(
        [
            {
                "site_id": site.id,
                "equipment_id": eq.id,
                "work_type": t,
                "description": "A07P3 %s" % t,
                "estimated_cost": 0.0,
            }
            for t in WORK_TYPES
        ]
    )
    assert tuple(orders.mapped("work_type")) == WORK_TYPES
    assert set(orders.mapped("site_id")) == {site} and set(orders.mapped("equipment_id")) == {eq}
    assert set(orders.mapped("state")) == {"draft"}


def test_work_order_lifecycle_runs_in_order_and_publishes_the_actual_cost(odoo_env):
    site = _site(odoo_env)
    wo = odoo_env["fix.facility.work.order"].create(
        {"site_id": site.id, "description": "A07P3 lifecycle"}
    )
    with pytest.raises(UserError), odoo_env.cr.savepoint():
        wo.action_complete(notes="skipped ahead")
    wo.action_schedule()
    wo.action_start()
    wo.action_complete(notes="Replaced the breaker, photo IMG-3")
    assert wo.state == "completed"
    row = odoo_env["fix.event.outbox"].search(
        [("event_type", "=", "facility.work_order_completed"), ("aggregate_id", "=", wo.id)]
    )
    payload = json.loads(row.payload)
    assert (payload["order"], payload["cost"]) == (wo.name, 0.0)
