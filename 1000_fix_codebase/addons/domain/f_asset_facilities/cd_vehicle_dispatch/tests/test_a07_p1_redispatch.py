"""A07 P1 wiring round 2 (2026-11-04): M46 vehicle.off_road / vehicle.available -> M02.

Live ORM, rolled back. The off-road record is opened and returned by M46's
own code; the events reach this bridge's subscriptions through the relay
(``cron_relay``) or its delivery step, and every consumer is delivered again
to prove redelivery changes nothing. Attacks run as the NON-ADMIN dispatcher
and technician of the P0 fixture.
"""

from datetime import datetime, time, timedelta

import pytest
from odoo.addons.cd_field_service.models.fix_field_order import DISPATCHER_GROUP
from odoo.addons.cd_vehicle_dispatch.tests import test_a07_p0_dispatch_bridge as _p0
from odoo.addons.cd_vehicle_dispatch.tests.test_a07_p0_dispatch_bridge import dispatch, refused
from odoo.exceptions import AccessError

# the P0 fixture (pytest finds it by this name)
w = _p0.w
MODULE = "cd_vehicle_dispatch"
WIRED = {
    "vehicle.off_road": "consume_vehicle_off_road",
    "vehicle.available": "consume_vehicle_available",
}


def _relay(w):
    w.env["fix.event.outbox"].cron_relay(limit=5000)


def _row(w, event_type, record):
    return w.env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate_id", "=", record.id)],
        order="id desc",
        limit=1,
    )


def _redeliver(w, event_type, record):
    """The relay's delivery step again, on the same outbox row."""
    row = _row(w, event_type, record)
    sub = w.env.ref("%s.consumer_%s" % (MODULE, event_type.replace(".", "_")))
    assert row and w.env["fix.event.outbox"]._relay_deliver(sub, row) == ""
    return row


def _delivered(w, event_type, record):
    row = _row(w, event_type, record)
    sub = w.env.ref("%s.consumer_%s" % (MODULE, event_type.replace(".", "_")))
    delivery = w.env["fix.event.consumer.delivery"].search(
        [("subscription_id", "=", sub.id), ("event_id", "=", row.id)]
    )
    assert delivery.state == "done", delivery.last_error


def _at(day, hour=6):
    """A UTC datetime on `day` (06:00 UTC is noon in Dhaka)."""
    return datetime.combine(day, time(hour, 0))


def _off(w, vehicle, cause="defect", reason="Brakes soft"):
    return w.env["fix.vehicle.offroad"].create(
        {"vehicle_id": vehicle.id, "reason": reason, "cause": cause}
    )


def _officer(w, login="a07rd_officer"):
    env = w.env
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id, env.ref("fleet.fleet_group_user").id])
                ],
                "company_id": env.company.id,
                "company_ids": [(6, 0, [env.company.id])],
                "operating_unit_ids": [(6, 0, w.ou.ids)],
                "default_operating_unit_id": w.ou.id,
            }
        )
    )
    return user


def _return(w, off, officer):
    """M46's own return: a passed re-check after the off-road, by an officer."""
    w.env["fix.vehicle.check"].create(
        {
            "vehicle_id": off.vehicle_id.id,
            "tyres_ok": True,
            "lights_ok": True,
            "fluids_ok": True,
            "brakes_ok": True,
        }
    )
    off.with_user(officer).action_return()
    assert off.state == "returned" and off.returned_by_id == officer


def test_both_events_have_an_active_subscription(w):
    for event_type, method in WIRED.items():
        sub = w.env["fix.event.consumer"].search(
            [("event_type", "=", event_type), ("module", "=", MODULE)]
        )
        assert len(sub) == 1 and sub.active
        assert (sub.model, sub.method) == ("fix.field.order", method)


def test_off_road_flags_open_orders_from_today_and_marks_the_assignment(w):
    live = w.fo(vehicle_id=w.good.id, vehicle_driver_id=w.driver.id)
    dispatch(w, live, w.ea)
    booking = live.vehicle_assignment_id
    later = w.fo(vehicle_id=w.good.id, scheduled_start=_at(w.today + timedelta(days=2)))
    past = w.fo(vehicle_id=w.good.id, scheduled_start=_at(w.today - timedelta(days=2)))
    closed = w.fo(vehicle_id=w.good.id)
    closed.write({"state": "cancelled"})  # setup: the superuser closes it
    elsewhere = w.fo(vehicle_id=w.vehicle("A07RD-OTHER").id)

    off = _off(w, w.good)
    _relay(w)
    _delivered(w, "vehicle.off_road", off)

    for rec in (live, later):
        assert rec.redispatch_required and rec.redispatch_offroad_id == off
        assert off.name in rec.redispatch_reason and rec.redispatch_flagged_at
        activity = rec.redispatch_activity_id
        assert activity and activity.res_id == rec.id
        assert activity.user_id.has_group(DISPATCHER_GROUP)
        assert not activity.user_id._is_superuser()
    for rec in (past, closed, elsewhere):
        assert not rec.redispatch_required and not rec.redispatch_offroad_id
    # never a state change
    assert (live.state, later.state) == ("dispatched", "pending_dispatch")
    assert live.vehicle_assignment_id == booking
    assert booking.offroad_conflict_id == off and off.name in booking.offroad_conflict_note

    # redelivery: one flag, one activity, one note
    first = live.redispatch_activity_id
    notes = len(live.message_ids)
    _redeliver(w, "vehicle.off_road", off)
    _redeliver(w, "vehicle.off_road", off)
    assert len(live.activity_ids) == 1 and len(live.message_ids) == notes
    assert live.redispatch_activity_id == first


def test_flags_and_conflicts_cannot_be_typed(w):
    rec = w.fo(vehicle_id=w.good.id)
    dispatch(w, rec, w.ea)
    other = w.fo(vehicle_id=w.vehicle("A07RD-SPARE").id)
    off = _off(w, w.good)
    _relay(w)
    assert rec.redispatch_required and not other.redispatch_required
    booking = rec.vehicle_assignment_id
    # the dispatcher clears the flag by hand, the technician forges one
    assert "cannot be set directly" in refused(
        w.env, lambda: rec.with_user(w.ud).write({"redispatch_required": False})
    )
    assert "cannot be set directly" in refused(
        w.env,
        lambda: other.with_user(w.ud).write(
            {"redispatch_required": True, "redispatch_offroad_id": off.id}
        ),
    )
    assert "cannot be set directly" in refused(
        w.env, lambda: rec.with_user(w.ua).write({"redispatch_cleared_by_id": w.ua.id})
    )
    # any internal user may write an assignment: not its conflict
    assert "cannot be set directly" in refused(
        w.env, lambda: booking.with_user(w.ua).write({"offroad_conflict_id": False})
    )
    # nor can a user publish the event that would clear it
    with pytest.raises(AccessError), w.env.cr.savepoint():
        w.env["fix.event.outbox"].with_user(w.ud).create(
            {"event_type": "vehicle.available", "aggregate_id": off.id}
        )
    assert rec.redispatch_required and booking.offroad_conflict_id == off


def test_available_clears_the_flags_with_who_and_when(w):
    rec = w.fo(vehicle_id=w.good.id, vehicle_driver_id=w.driver.id)
    dispatch(w, rec, w.ea)
    booking = rec.vehicle_assignment_id
    off = _off(w, w.good)
    _relay(w)
    activity = rec.redispatch_activity_id
    assert rec.redispatch_required and activity
    officer = _officer(w)
    _return(w, off, officer)
    _relay(w)
    _delivered(w, "vehicle.available", off)
    assert not rec.redispatch_required and rec.redispatch_offroad_id == off
    assert rec.redispatch_cleared_by_id == officer and rec.redispatch_cleared_at
    assert "returned to service" in rec.redispatch_clear_note
    # the dispatcher's activity is marked done (kept, archived) with the reason
    assert not activity.active and activity.date_done
    assert rec.state == "dispatched"
    assert not booking.offroad_conflict_id
    assert booking.offroad_conflict_cleared_by_id == officer
    stamp = rec.redispatch_cleared_at
    _redeliver(w, "vehicle.available", off)
    assert rec.redispatch_cleared_at == stamp and not rec.redispatch_required


def test_a_second_off_road_record_keeps_the_flag(w):
    rec = w.fo(vehicle_id=w.good.id)
    dispatch(w, rec, w.ea)
    first = _off(w, w.good)
    _relay(w)
    second = _off(w, w.good, cause="accident", reason="Rear-ended")
    _relay(w)
    assert rec.redispatch_offroad_id == first  # one flag, not two
    assert len(rec.activity_ids) == 1
    _return(w, first, _officer(w))
    _relay(w)
    assert rec.redispatch_required and rec.redispatch_offroad_id == second
    assert second.name in rec.redispatch_reason
    assert rec.vehicle_assignment_id.offroad_conflict_id == second


def test_re_dispatch_with_another_van_resolves_the_flag(w):
    rec = w.fo(vehicle_id=w.good.id)
    dispatch(w, rec, w.ea)
    _off(w, w.good)
    _relay(w)
    activity = rec.redispatch_activity_id
    spare = w.vehicle("A07RD-SWAP")
    # re-dispatch: the dispatcher moves the order to another van
    rec.with_user(w.ud).write({"vehicle_id": spare.id})
    assert not rec.redispatch_required and rec.redispatch_cleared_by_id == w.ud
    assert "Re-dispatched by" in rec.redispatch_clear_note and not activity.active
    booking = rec.vehicle_assignment_id
    assert booking.vehicle_id == spare and not booking.offroad_conflict_id
    assert booking.offroad_conflict_cleared_by_id == w.ud
