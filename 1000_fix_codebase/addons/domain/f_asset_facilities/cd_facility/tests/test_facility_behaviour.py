"""cd_facility behaviour (live ORM, rolled back): sites and facility
maintenance work orders."""

from __future__ import annotations

import json
import re
from datetime import date

from odoo import fields


def _events(env, event_type, aggregate, res_id):
    rows = env["fix.event.outbox"].search(
        [
            ("event_type", "=", event_type),
            ("aggregate", "=", aggregate),
            ("aggregate_id", "=", res_id),
        ],
        order="id",
    )
    return [json.loads(r.payload) for r in rows]


def _site(env, **vals):
    vals.setdefault("name", "Dhanmondi Service Branch")
    return env["fix.site"].create(vals)


def _work_order(env, site=None, **vals):
    vals.setdefault("description", "Replace UPS battery bank")
    vals["site_id"] = (site or _site(env)).id
    return env["fix.facility.work.order"].create(vals)


def test_site_defaults(odoo_env):
    site = _site(odoo_env)
    assert site.site_type == "branch"
    assert site.state == "active"


def test_link_assets_publishes_asset_count(odoo_env):
    eqs = odoo_env["fix.equipment"].create(
        [{"code": "EQ-S1", "name": "Scope"}, {"code": "EQ-S2", "name": "Programmer"}]
    )
    linked = _site(odoo_env, name="Tejgaon Depot", equipment_ids=[(6, 0, eqs.ids)])
    empty = _site(odoo_env, name="Empty Kiosk")
    (linked | empty).action_link_assets()
    assert _events(odoo_env, "site.assets_linked", "fix.site", linked.id) == [
        {"site": "Tejgaon Depot", "assets_count": 2}
    ]
    assert _events(odoo_env, "site.assets_linked", "fix.site", empty.id) == [
        {"site": "Empty Kiosk", "assets_count": 0}
    ]


def test_site_close_and_reopen(odoo_env):
    sites = _site(odoo_env, name="A") | _site(odoo_env, name="B")
    sites.action_close()
    assert set(sites.mapped("state")) == {"closed"}
    sites.action_reopen()
    assert set(sites.mapped("state")) == {"active"}


def test_work_order_name_falls_back_to_timestamp(odoo_env):
    # The module ships `seq_fix_facility_work_order`, so the timestamp branch is
    # only reachable with no active sequence for the code. The test used to
    # assert the fallback without deactivating it, and so only passed on a
    # database where this module's own data had never loaded (re-audit
    # 2026-10-31); it now removes the sequence inside the rolled-back
    # transaction, which is what the fallback is actually for.
    odoo_env["ir.sequence"].search([("code", "=", "fix.facility.work.order")]).write(
        {"active": False}
    )

    wo = _work_order(odoo_env)
    assert re.fullmatch(r"FWO/\d{14}", wo.name)
    assert wo.state == "draft"
    assert wo.scheduled_date == fields.Date.context_today(wo)
    assert wo.currency_id == odoo_env.ref("base.BDT")


def test_work_order_name_from_sequence(odoo_env):
    odoo_env["ir.sequence"].create(
        {"name": "FWO test", "code": "fix.facility.work.order", "prefix": "FWO/T/"}
    )
    assert _work_order(odoo_env).name.startswith("FWO/T/")


def test_work_order_explicit_name_is_kept(odoo_env):
    assert _work_order(odoo_env, name="FWO/MANUAL/7").name == "FWO/MANUAL/7"


def test_schedule_with_and_without_date(odoo_env):
    keep = _work_order(odoo_env, scheduled_date=date(2026, 11, 1))
    keep.action_schedule()
    assert keep.state == "scheduled"
    assert keep.scheduled_date == date(2026, 11, 1)

    moved = _work_order(odoo_env)
    moved.action_schedule(date=date(2026, 12, 24))
    assert moved.state == "scheduled"
    assert moved.scheduled_date == date(2026, 12, 24)


def test_start_and_cancel(odoo_env):
    wo = _work_order(odoo_env)
    wo.action_start()
    assert wo.state == "in_progress"
    wo.action_cancel()
    assert wo.state == "cancelled"


def test_complete_publishes_actual_then_estimated_then_zero_cost(odoo_env):
    site = _site(odoo_env, name="CTG Warehouse")
    actual = _work_order(odoo_env, site, work_type="repair", estimated_cost=900, actual_cost=1250)
    estimated = _work_order(odoo_env, site, estimated_cost=900)
    free = _work_order(odoo_env, site, work_type="inspection")
    (actual | estimated | free).action_complete()
    assert {actual.state, estimated.state, free.state} == {"completed"}
    wo_model = "fix.facility.work.order"
    assert _events(odoo_env, "facility.work_order_completed", wo_model, actual.id) == [
        {"order": actual.name, "site": "CTG Warehouse", "work_type": "repair", "cost": 1250.0}
    ]
    assert (
        _events(odoo_env, "facility.work_order_completed", wo_model, estimated.id)[0]["cost"]
        == 900.0
    )
    assert _events(odoo_env, "facility.work_order_completed", wo_model, free.id)[0] == {
        "order": free.name,
        "site": "CTG Warehouse",
        "work_type": "inspection",
        "cost": 0.0,
    }


def test_work_orders_cascade_with_site(odoo_env):
    site = _site(odoo_env)
    wo = _work_order(odoo_env, site)
    assert site.work_order_ids == wo
    site.unlink()
    assert not wo.exists()
