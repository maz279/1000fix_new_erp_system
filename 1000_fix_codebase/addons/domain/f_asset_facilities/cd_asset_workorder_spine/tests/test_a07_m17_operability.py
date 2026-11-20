"""A07 M17, the parts that reach M01: the lost/stolen hold at the hand-over and
on its own screen, a maintenance plan rolling when its order closes, and the
causing job and stock lot of a fitted component. Driven through the workspace
endpoints as NON-ADMIN users; the order walks its real path to Ready.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import types
from datetime import timedelta
from pathlib import Path

import odoo.addons.cd_p03_portal as portal
import odoo.addons.cd_p03_portal.controllers.p03_generic_api as api
import pytest
from odoo import fields
from odoo.addons.cd_asset_workorder_spine.tests.test_a07_p1_spine import DEMAND
from odoo.addons.cd_service_order.tests.test_a02_p0_m01 import (
    handover_evidence,
    order,
    to_ready,
    w,  # noqa: F401 - the fixture
)
from odoo.exceptions import UserError

HOLD = "fix.service.order.device.hold"
BM = "cd_device_registry.group_device_branch_manager"
MODULE = "cd_asset_workorder_spine"
SRC = Path(portal.__file__).parent / "static" / "src" / "a07"


@pytest.fixture
def ui(w):  # noqa: F811
    cls = api.P03GenericApiController
    ctl = cls()
    old = getattr(api, "request", None)

    def call(name, user, **kw):
        api.request = types.SimpleNamespace(env=w.env(user=user.id))
        fn = getattr(cls, name)
        return getattr(fn, "original_endpoint", fn)(ctl, **kw)

    try:
        yield types.SimpleNamespace(
            records=lambda user, **kw: call("model_records", user, **kw),
            form=lambda user, **kw: call("model_form", user, **kw),
            write=lambda user, **kw: call("model_write", user, **kw),
            action=lambda user, **kw: call("model_action", user, **kw),
        )
    finally:
        api.request = old


@pytest.fixture(scope="module")
def js(tmp_path_factory):
    node = shutil.which("node")
    assert node, "node evaluates the registry: without it these tests prove nothing"
    tmp = tmp_path_factory.mktemp("m17spine")
    (tmp / "m17.mjs").write_text((SRC / "m17.js").read_text(encoding="utf-8"), "utf-8")
    (tmp / "run.mjs").write_text(
        "import * as A from './m17.mjs';\n"
        "console.log(JSON.stringify({module: A.MODULE, screens: A.SCREENS, chips: A.FORM_CHIPS}));\n",
        "utf-8",
    )
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our probe file
        [node, str(tmp / "run.mjs")],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=60,
    )
    return json.loads(out.stdout)


def _relay_to_hold(w, event_type, device, method):  # noqa: F811
    row = w.env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate_id", "=", device.id)],
        order="id desc",
        limit=1,
    )
    assert row
    sub = w.env["fix.event.consumer"].search(
        [("event_type", "=", event_type), ("module", "=", MODULE)]
    )
    assert w.env["fix.event.outbox"]._relay_deliver(sub, row) == ""
    assert callable(getattr(w.env[HOLD], method))


def _ready_to_hand_over(w):  # noqa: F811
    o = to_ready(w, order(w), 10000)
    handover_evidence(w, o)
    o.with_user(w.cashier).action_mark_settled("POS-M17", 11500.0, tender="cash")
    return o


def _branch_manager(w, login="m17_spine_bm"):  # noqa: F811
    return (
        w.env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [(6, 0, [w.env.ref("base.group_user").id, w.env.ref(BM).id])],
            }
        )
    )


# ------------------------------------------------------------ 9 hold at the hand-over
def test_9_a_held_order_is_not_handed_over_until_the_flag_is_cleared(w, ui):  # noqa: F811
    o = _ready_to_hand_over(w)
    device = o.device_id
    device.with_user(w.clerk).action_mark_lost(reason="Owner reported theft GD-9")
    _relay_to_hold(w, "device.flagged", device, "consume_device_flagged")
    hold = w.env[HOLD].search([("order_id", "=", o.id)])
    assert hold.state == "open" and o.device_flag_hold
    out = ui.action(w.clerk, model="fix.service.order", ids=[o.id], method="action_deliver")
    assert not out["success"] and "lost" in out["error"].lower()
    assert o.state == "ready"
    bm = _branch_manager(w)
    device.with_user(bm).action_clear_lost(reason="Recovered by the owner")
    _relay_to_hold(w, "device.flag_cleared", device, "consume_device_flag_cleared")
    assert hold.state == "cleared" and not o.device_flag_hold
    out = ui.action(w.clerk, model="fix.service.order", ids=[o.id], method="action_deliver")
    assert out["success"], out
    assert o.state == "delivered"


def test_9_a_flag_not_yet_relayed_still_stops_the_hand_over(w):  # noqa: F811
    """The relay runs on a schedule: between the flag and the hold there is a
    window, and an order opened after the flag gets no hold at all. The device's
    own state decides too."""
    o = _ready_to_hand_over(w)
    o.device_id.with_user(w.clerk).action_mark_lost(reason="Reported at the counter")
    assert not o.device_flag_hold
    with pytest.raises(UserError, match="lost"), w.env.cr.savepoint():
        o.with_user(w.clerk).action_deliver()
    assert o.state == "ready"


def test_9_superuser_service_code_is_held_too(w):  # noqa: F811
    o = _ready_to_hand_over(w)
    o.device_id.with_user(w.clerk).action_mark_lost(reason="Reported at the counter")
    with pytest.raises(UserError, match="lost"), w.env.cr.savepoint():
        o.sudo().action_deliver()


def test_9_the_holds_have_a_screen_that_nobody_types_on(w, ui, js):  # noqa: F811
    screen = js["screens"]["M17-holds"]
    assert screen["model"] == HOLD and screen["create"] is False
    assert js["chips"]["M17:__by_screen__"]["M17-holds"] == "M17-form-hold"
    form = js["screens"]["M17-form-hold"]
    assert all(f.get("readonly") for s in form["sections"] for f in s["fields"])
    assert "M17-holds" in {s["id"] for g in js["module"]["groups"] for s in g["screens"]}
    assert api.SURFACES[HOLD]["writable"] == frozenset()
    o = order(w)
    o.sudo().write({"operating_unit_id": w.branch.operating_unit_id.id})
    o.device_id.with_user(w.clerk).action_mark_lost(reason="Stolen, GD-12")
    _relay_to_hold(w, "device.flagged", o.device_id, "consume_device_flagged")
    hold = w.env[HOLD].search([("order_id", "=", o.id)])
    out = ui.records(w.clerk, model=HOLD, cols=screen["cols"], domain=[("id", "=", hold.id)])
    assert "error" not in out and len(out["rows"]) == 1
    # every declared column exists: an unknown one is dropped silently
    assert set(screen["cols"]) <= set(out["rows"][0])
    assert "reason" in screen["cols"] and "GD-12" in out["rows"][0]["reason"]
    # read as the caller: a user of another unit does not list it
    other_ou = w.env["operating.unit"].search(
        [("id", "!=", o.operating_unit_id.id)], limit=1
    ) or w.env["operating.unit"].create(
        {
            "name": "M17 Spine OU2",
            "code": "M17S2",
            "partner_id": w.env.company.partner_id.id,
            "company_id": w.env.company.id,
        }
    )
    stranger = (
        w.env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "m17_spine_other",
                "login": "m17_spine_other",
                "group_ids": [(6, 0, w.env.ref("base.group_user").ids)],
                "assigned_operating_unit_ids": [(6, 0, other_ou.ids)],
                "default_operating_unit_id": other_ou.id,
            }
        )
    )
    assert o.operating_unit_id, "the order must sit in a unit for this to prove anything"
    out = ui.records(stranger, model=HOLD, cols=["name"], domain=[("id", "=", hold.id)])
    assert not out["rows"]


# ------------------------------------------------------------ PM plan roll
def _plan_with_order(w):  # noqa: F811
    device = order(w).device_id
    plan = w.env["fix.device.pm"].create(
        {
            "device_id": device.id,
            "plan_type": "annual",
            "next_due": fields.Date.context_today(w.env["fix.device"]) - timedelta(days=1),
        }
    )
    w.env["fix.device.pm"].cron_pm_due()
    w.env[DEMAND].consume_device_maintenance_due(
        {"payload": {"plan_id": plan.id, "due_date": str(plan.next_due)}}
    )
    demand = w.env[DEMAND].search([("device_pm_id", "=", plan.id)])
    if not demand.service_order_id:
        # the customer is the demand's; the branch comes from the fixture
        demand.sudo().write({"branch_id": w.branch.id})
        demand.sudo().action_route()
    assert demand.state == "routed" and demand.service_order_id
    return plan, demand, demand.service_order_id


def test_a_plan_rolls_when_its_order_closes_and_the_demand_is_done(w):  # noqa: F811
    plan, demand, so = _plan_with_order(w)
    due = plan.next_due
    today = fields.Date.context_today(plan)
    assert plan.state == "active" and not plan.last_done
    w.env.flush_all()
    w.env.cr.execute("UPDATE fix_service_order SET state = 'delivered' WHERE id = %s", (so.id,))
    w.env.invalidate_all()
    assert plan.next_due == due  # delivered is not closed
    so.sudo().action_close()
    plan.invalidate_recordset()
    demand.invalidate_recordset()
    assert so.state == "closed"
    assert plan.last_done == today and plan.next_due > today
    assert demand.state == "done"
    # closing again (redelivery, a repeated write) does not roll it twice
    rolled = plan.next_due
    so.sudo()._guarded().write({"state": "closed"})
    plan.invalidate_recordset()
    assert plan.next_due == rolled


def test_a_cancelled_order_does_not_roll_the_plan(w):  # noqa: F811
    plan, demand, so = _plan_with_order(w)
    due = plan.next_due
    so.sudo()._guarded().write({"state": "intake"})
    so.sudo()._guarded().write({"state": "cancelled"})
    plan.invalidate_recordset()
    assert plan.next_due == due and not plan.last_done and demand.state == "routed"


def test_a_paused_plan_is_not_rolled_and_the_close_still_stands(w):  # noqa: F811
    plan, demand, so = _plan_with_order(w)
    due = plan.next_due
    plan.action_pause()
    w.env.flush_all()
    w.env.cr.execute("UPDATE fix_service_order SET state = 'delivered' WHERE id = %s", (so.id,))
    w.env.invalidate_all()
    so.sudo().action_close()
    plan.invalidate_recordset()
    demand.invalidate_recordset()
    assert so.state == "closed" and plan.next_due == due and demand.state == "done"


# ------------------------------------------------------------ 14 the job and the lot
def test_14_the_component_form_picks_the_job_and_the_lot(w, ui, js):  # noqa: F811
    offered = {
        f["name"] for s in js["screens"]["M17-form-component"]["sections"] for f in s["fields"]
    }
    assert {"causing_order_id", "stock_lot_ref_id"} <= offered
    o = order(w)
    product = w.env["product.product"].create({"name": "M17 Panel", "tracking": "lot"})
    lot = w.env["stock.lot"].create({"name": "M17-LOT-1", "product_id": product.id})
    out = ui.form(
        w.clerk,
        model="fix.device.component",
        fields=[{"name": "causing_order_id"}, {"name": "stock_lot_ref_id"}],
    )
    assert {f["name"]: f["type"] for f in out["fields"]} == {
        "causing_order_id": "many2one",
        "stock_lot_ref_id": "many2one",
    }
    res = ui.write(
        w.clerk,
        model="fix.device.component",
        values={
            "device_id": o.device_id.id,
            "part_name": "Panel",
            "causing_order_id": o.id,
            "stock_lot_ref_id": lot.id,
        },
    )
    assert "error" not in res, res
    part = w.env["fix.device.component"].browse(res["id"])
    # the reference the genealogy and its events read
    assert (part.service_order_id, part.lot_id) == (o.id, lot.id)
    assert (part.causing_order_id, part.stock_lot_ref_id) == (o, lot)
    read = ui.form(
        w.clerk,
        model="fix.device.component",
        fields=[{"name": "causing_order_id"}],
        record_id=part.id,
    )
    assert read["record"]["causing_order_id"]["id"] == o.id
    # a removed part's history is not rewritten through them
    part.with_user(w.clerk).action_remove()
    res = ui.write(
        w.clerk,
        model="fix.device.component",
        record_id=part.id,
        values={"causing_order_id": False},
    )
    assert "error" in res
    part.invalidate_recordset()
    assert part.service_order_id == o.id
