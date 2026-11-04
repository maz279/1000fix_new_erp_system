"""A07 P1 wiring round 2 (2026-11-04): M46 defect / telematics and M17 lost/stolen.

Live ORM, rolled back. Each event is produced by its source module's own code
(a failed pre-use check, the telematics silence job, the M17 lost/stolen
actions) and reaches this module through the relay (``cron_relay``); every
consumer is then delivered again to prove redelivery changes nothing.
Attacks run as NON-ADMIN users: the clerk who would forge or clear a hold,
the flagger who would clear his own flag.
"""

from __future__ import annotations

from datetime import timedelta

from odoo import fields
from odoo.addons.cd_asset_workorder_spine.tests import test_a07_p1_spine as _shared
from odoo.addons.cd_asset_workorder_spine.tests.test_a07_p1_spine import (
    DEMAND,
    WO,
    _deliver,
    _demands,
    _refused,
    _run_wo,
    _vehicle,
)

# the shared fixture of the module's own tests (pytest finds it by this name)
c = _shared.c

MODULE = "cd_asset_workorder_spine"
HOLD = "fix.service.order.device.hold"
BRANCH_MANAGER = "cd_device_registry.group_device_branch_manager"
WIRED = {
    "vehicle.defect_raised": (DEMAND, "consume_vehicle_defect_raised"),
    "vehicle.telematics_silent": (DEMAND, "consume_vehicle_telematics_silent"),
    "device.flagged": (HOLD, "consume_device_flagged"),
    "device.flag_cleared": (HOLD, "consume_device_flag_cleared"),
}
SILENCE = "cd_vehicle_ext.telematics_silence_minutes"


def _relay(c):
    c.env["fix.event.outbox"].cron_relay(limit=5000)


def _delivered(c, event_type, record):
    row = c.env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate_id", "=", record.id)],
        order="id desc",
        limit=1,
    )
    sub = c.env["fix.event.consumer"].search(
        [("event_type", "=", event_type), ("module", "=", MODULE)]
    )
    delivery = c.env["fix.event.consumer.delivery"].search(
        [("subscription_id", "=", sub.id), ("event_id", "=", row.id)]
    )
    assert row and delivery.state == "done", delivery.last_error


def test_each_round2_event_has_one_active_subscription(c):
    for event_type, (model, method) in WIRED.items():
        sub = c.env["fix.event.consumer"].search(
            [("event_type", "=", event_type), ("module", "=", MODULE)]
        )
        assert len(sub) == 1 and sub.active, event_type
        assert (sub.model, sub.method) == (model, method)
        assert callable(getattr(c.env[model], method))


# ------------------------------------------------------------ M46 defect
def _check(c, vehicle, ok=False, defects="Brake pedal soft"):
    return c.env["fix.vehicle.check"].create(
        {
            "vehicle_id": vehicle.id,
            "tyres_ok": True,
            "lights_ok": True,
            "fluids_ok": True,
            "brakes_ok": ok,
            "defects": False if ok else defects,
        }
    )


def test_a_failed_check_raises_one_repair_work_order_and_later_failures_join_it(c):
    vehicle = _vehicle(c, plate="A7R2-DEF")
    check = _check(c, vehicle)
    offroad = c.env["fix.vehicle.offroad"].search([("check_id", "=", check.id)])
    assert offroad.state == "offroad"
    _relay(c)
    _delivered(c, "vehicle.defect_raised", check)
    demand = _demands(c, check)
    wo = demand.work_order_id
    assert len(demand) == 1 and demand.origin == "m46_defect" and demand.state == "routed"
    assert (wo.work_type, wo.vehicle_id, wo.site_id, wo.state) == (
        "repair",
        vehicle,
        c.site,
        "draft",
    )
    assert (wo.spine_origin, wo.spine_asset_kind) == ("m46_defect", "vehicle")
    assert check.name in wo.description and offroad.name in wo.description
    assert "safety-critical" in wo.description
    # redelivery raises nothing new
    _deliver(c, "vehicle.defect_raised", check)
    _deliver(c, "vehicle.defect_raised", check)
    assert len(_demands(c, check)) == 1
    assert c.env[WO].search_count([("spine_demand_id", "=", demand.id)]) == 1
    # the van fails again before the repair: logged on the open demand
    again = _check(c, vehicle, defects="Brake light out")
    _relay(c)
    _deliver(c, "vehicle.defect_raised", again)
    assert not _demands(c, again)
    assert demand.source_log.count("[check:%s]" % again.id) == 1
    assert c.env[DEMAND].search_count([("vehicle_id", "=", vehicle.id)]) == 1
    # a passed check raises nothing
    passed = _check(c, vehicle, ok=True)
    assert not c.env["fix.event.outbox"].search_count(
        [("event_type", "=", "vehicle.defect_raised"), ("aggregate_id", "=", passed.id)]
    )


def test_a_verified_defect_repair_leaves_the_return_to_service_to_m46(c):
    vehicle = _vehicle(c, plate="A7R2-VER")
    check = _check(c, vehicle)
    _relay(c)
    wo = _demands(c, check).work_order_id
    # M47's lifecycle: the clerk cannot verify, the work order is the FM's
    _run_wo(c, wo)
    _refused(c.env, wo.with_user(c.clerk).action_verify, match="Facility Manager")
    wo.with_user(c.fm2).action_verify(notes="Brake master cylinder replaced")
    assert wo.state == "verified" and _demands(c, check).state == "done"
    offroad = c.env["fix.vehicle.offroad"].search([("check_id", "=", check.id)])
    assert offroad.state == "offroad"  # still the Fleet Officer's, on a re-check
    assert any(offroad.name in (m.body or "") for m in wo.message_ids)
    # a new failure after the repair is closed is a new demand
    later = _check(c, vehicle, defects="Brakes again")
    _relay(c)
    assert _demands(c, later).state == "routed"


def test_a_defect_on_a_vehicle_with_no_site_waits_and_cannot_be_forged(c):
    vehicle = _vehicle(c, plate="A7R2-BARE", branch_id=c.br_bare.id)
    check = _check(c, vehicle)
    _relay(c)
    demand = _demands(c, check)
    assert demand.state == "pending" and "has no M47 site" in demand.blocker
    # the clerk neither dismisses it nor points it elsewhere
    _refused(c.env, demand.with_user(c.clerk).action_dismiss, reason="not needed")
    _refused(
        c.env,
        demand.with_user(c.clerk).write,
        {"vehicle_id": _vehicle(c, plate="A7R2-X").id},
        match="cannot be set directly",
    )
    _refused(
        c.env,
        c.env[DEMAND].with_user(c.fm).create,
        {
            "name": "x",
            "origin": "m46_defect",
            "target": "work_order",
            "source_model": "fix.vehicle.check",
            "source_res_id": check.id,
            "description": "x",
        },
    )


# ------------------------------------------------------------ M46 telematics
def _snapshot(c, vehicle, device, minutes_ago):
    """A snapshot that was online when it was recorded."""
    Param = c.env["ir.config_parameter"].sudo()
    Param.set_param(SILENCE, "100000")
    snap = c.env["fix.vehicle.telemetry"].create(
        {
            "vehicle_id": vehicle.id,
            "device_ref": device,
            "last_ping": fields.Datetime.now() - timedelta(minutes=minutes_ago),
        }
    )
    Param.set_param(SILENCE, "60")
    assert snap.state == "online"
    return snap


def _silence(c):
    c.env["fix.vehicle.telemetry"].cron_telemetry_silence()


def test_a_silent_telematics_device_raises_one_inspection_per_episode(c):
    vehicle = _vehicle(c, plate="A7R2-TEL")
    snap = _snapshot(c, vehicle, "TRK-A7R2", minutes_ago=180)
    _silence(c)
    assert snap.state == "stale"
    _relay(c)
    _delivered(c, "vehicle.telematics_silent", snap)
    demand = c.env[DEMAND].search(
        [("source_model", "=", snap._name), ("source_res_id", "=", snap.id)]
    )
    wo = demand.work_order_id
    assert demand.origin == "m46_telematics" and demand.source_key == "TRK-A7R2"
    assert (demand.state, wo.work_type, wo.vehicle_id, wo.site_id) == (
        "routed",
        "inspection",
        vehicle,
        c.site,
    )
    assert "TRK-A7R2" in wo.description
    _deliver(c, "vehicle.telematics_silent", snap)
    _deliver(c, "vehicle.telematics_silent", snap)
    assert c.env[DEMAND].search_count([("vehicle_id", "=", vehicle.id)]) == 1
    # the device reports once and falls silent again while the inspection is
    # open: the new episode is logged on it, no second work order
    again = _snapshot(c, vehicle, "TRK-A7R2", minutes_ago=90)
    _silence(c)
    _relay(c)
    assert demand.source_log.count("[telemetry:%s]" % again.id) == 1
    assert c.env[WO].search_count([("vehicle_id", "=", vehicle.id)]) == 1
    # another device on the same van is its own inspection
    other = _snapshot(c, vehicle, "CAM-A7R2", minutes_ago=120)
    _silence(c)
    _relay(c)
    assert (
        c.env[DEMAND].search_count(
            [("vehicle_id", "=", vehicle.id), ("source_key", "=", "CAM-A7R2")]
        )
        == 1
    )
    assert other.state == "stale"


def test_a_device_that_reported_before_the_relay_raises_nothing(c):
    vehicle = _vehicle(c, plate="A7R2-BACK")
    snap = _snapshot(c, vehicle, "TRK-BACK", minutes_ago=180)
    _silence(c)
    _snapshot(c, vehicle, "TRK-BACK", minutes_ago=0)  # it is back
    _relay(c)
    _delivered(c, "vehicle.telematics_silent", snap)
    assert not c.env[DEMAND].search_count([("vehicle_id", "=", vehicle.id)])


# ------------------------------------------------------------ M17 lost/stolen
def _user(c, login, *groups):
    env = c.env
    ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [(6, 0, ids)],
                "company_ids": [(6, 0, c.co.ids)],
                "company_id": c.co.id,
                "assigned_operating_unit_ids": [(6, 0, c.ou.ids)],
                "default_operating_unit_id": c.ou.id,
            }
        )
    )


def _device_with_orders(c):
    env = c.env
    c.bm = _user(c, "a07r2_bm", BRANCH_MANAGER)
    c.bm2 = _user(c, "a07r2_bm2", BRANCH_MANAGER)
    c.br.sudo().write({"manager_id": c.bm.id})
    brand = env["fix.brand"].create({"name": "A7R2Brand", "code": "A7R2"})
    model = env["fix.device.model"].create({"name": "A7R2 Phone", "brand_id": brand.id})
    owner = env["res.partner"].create({"name": "A7R2 Owner", "phone": "01711000881"})
    device = env["fix.device"].create(
        {
            "device_model_id": model.id,
            "owner_id": owner.id,
            "serial_number": "A7R2-SN-1",
            "imei_1": "356938035643809",
            "branch_id": c.br.id,
        }
    )

    def order(note):
        return env["fix.service.order"].create(
            {
                "device_id": device.id,
                "customer_id": owner.id,
                "branch_id": c.br.id,
                "fault_description": "A07 round 2 %s" % note,
                "operating_unit_id": c.ou.id,
            }
        )

    first, second, gone = order("open 1"), order("open 2"), order("cancelled")
    gone._guarded().write({"state": "intake"})
    gone._guarded().write({"state": "cancelled"})
    return device, first, second, gone


def _holds(c, order):
    return c.env[HOLD].search([("order_id", "=", order.id)])


def test_a_lost_flag_holds_every_open_order_and_its_clearance_is_recorded(c):
    device, first, second, gone = _device_with_orders(c)
    states = (first.state, second.state)
    device.with_user(c.clerk).action_mark_lost(reason="Owner reported theft, GD-881")
    _relay(c)
    _delivered(c, "device.flagged", device)
    for order in (first, second):
        hold = _holds(c, order)
        assert len(hold) == 1 and hold.state == "open" and order.device_flag_hold
        assert (hold.device_id, hold.flagged_by_id) == (device, c.clerk)
        assert "GD-881" in hold.reason
        activity = hold.activity_id
        assert activity.user_id == c.bm and activity.res_id == order.id
        assert "Do not hand it back" in activity.note
    assert not _holds(c, gone) and not gone.device_flag_hold
    assert (first.state, second.state) == states  # never a state change
    # redelivery: one hold and one activity per order
    _deliver(c, "device.flagged", device)
    _deliver(c, "device.flagged", device)
    assert len(_holds(c, first)) == 1 and len(first.activity_ids) == 1

    # the flagger cannot clear his own flag, nor can anyone without the role
    _refused(c.env, device.with_user(c.clerk).action_clear_lost, reason="found it")
    assert first.device_flag_hold

    device.with_user(c.bm2).action_clear_lost(reason="Recovered by police, GD-881 closed")
    _relay(c)
    _delivered(c, "device.flag_cleared", device)
    for order in (first, second):
        hold = _holds(c, order)
        assert hold.state == "cleared" and not order.device_flag_hold
        assert hold.cleared_by_id == c.bm2 and hold.cleared_at
        assert "Recovered by police" in hold.clear_reason
        assert not hold.activity_id.active and hold.activity_id.date_done
    stamp = _holds(c, first).cleared_at
    _deliver(c, "device.flag_cleared", device)
    assert _holds(c, first).cleared_at == stamp

    # flagged again: a new hold, the cleared one stays as it was
    device.with_user(c.clerk).action_mark_lost(reason="Stolen again")
    _relay(c)
    holds = _holds(c, first)
    assert len(holds) == 2 and holds.mapped("state").count("open") == 1
    assert first.device_flag_hold


def test_a_hold_cannot_be_forged_cleared_or_deleted_by_hand(c):
    device, first, _second, _gone = _device_with_orders(c)
    device.action_mark_lost(reason="Reported lost at the counter")
    _relay(c)
    hold = _holds(c, first)
    assert hold.state == "open"
    for user in (c.clerk, c.bm):
        _refused(
            c.env, hold.with_user(user).write, {"state": "cleared"}, match="cannot be set directly"
        )
        _refused(
            c.env,
            first.with_user(user).write,
            {"device_flag_hold": False},
            match="cannot be set directly",
        )
        _refused(c.env, hold.with_user(user).unlink)
        _refused(
            c.env,
            c.env[HOLD].with_user(user).create,
            {
                "name": "x",
                "order_id": _second.id,
                "device_id": device.id,
                "flag_event_id": "forged",
            },
        )
    assert hold.state == "open" and first.device_flag_hold
    assert not _holds(c, _gone)


def test_a_flag_cleared_before_the_relay_raises_no_hold(c):
    device, first, _second, _gone = _device_with_orders(c)
    device.action_mark_lost(reason="Mistaken report")
    device.with_user(c.bm2).action_clear_lost(reason="Customer had it all along")
    _relay(c)
    _delivered(c, "device.flagged", device)
    assert not _holds(c, first) and not first.device_flag_hold
