"""A07 ERP audit (2026-11-20) M46-06 / M46-07: the van is gated again when the
job moves, not only at dispatch.

- BRU-FLT-07 / AUT-FLT-07: a job dispatched the evening before for today was
  never asked for today's pre-use check; travel now does not start without it
  (with cd_vehicle_ext.require_passed_preuse_check on);
- BRU-FLT-02 / AUT-FLT-02: a van taken off the road after dispatch kept its
  orders, and the technician accepted and started travel in it.

Live ORM (``odoo_env`` rolls back), as the NON-ADMIN technician of the P0
fixture.
"""

from datetime import datetime, time, timedelta

import pytest
from odoo.addons.cd_vehicle_dispatch.tests import test_a07_p0_dispatch_bridge as _p0
from odoo.addons.cd_vehicle_dispatch.tests.test_a07_p0_dispatch_bridge import dispatch, refused

w = _p0.w  # the P0 fixture
PREUSE = "cd_vehicle_ext.require_passed_preuse_check"


def _at(day, hour=6):
    return datetime.combine(day, time(hour, 0))


def _check(w, vehicle, ok=True):
    vals = {"vehicle_id": vehicle.id}
    vals.update({k: ok for k in ("tyres_ok", "lights_ok", "fluids_ok", "brakes_ok")})
    return w.env["fix.vehicle.check"].create(vals)


@pytest.mark.relay_backlog  # no relay here: skip the seed-backlog sweep
def test_m46_06_a_job_dispatched_the_day_before_needs_todays_check_to_start(w):
    # dispatched yesterday evening for today: the dispatch gate read
    # yesterday's day, so no check of today was asked for (the switch stands
    # for that here). The job's own steps on the day ask for it.
    rec = w.fo(vehicle_id=w.good.id, vehicle_driver_id=w.driver.id, scheduled_start=_at(w.today))
    dispatch(w, rec, w.ea)
    w.env["ir.config_parameter"].sudo().set_param(PREUSE, "True")
    msg = refused(w.env, lambda: rec.with_user(w.ua).action_accept())
    assert msg and "no passed pre-use check today" in msg
    assert rec.state == "dispatched"
    check = _check(w, w.good)
    rec.with_user(w.ua).action_accept()
    # a later failed check of the day stops the van leaving
    _check(w, w.good, ok=False)
    msg = refused(w.env, lambda: rec.with_user(w.ua).action_start_travel())
    assert msg and "failed today" in msg
    assert rec.state == "accepted" and check.passed


@pytest.mark.relay_backlog  # no relay here: skip the seed-backlog sweep
def test_m46_06_accepting_tomorrows_job_tonight_reads_tomorrows_gate(w):
    w.env["ir.config_parameter"].sudo().set_param(PREUSE, "True")
    tomorrow = w.today + timedelta(days=1)
    rec = w.fo(vehicle_id=w.good.id, vehicle_driver_id=w.driver.id, scheduled_start=_at(tomorrow))
    dispatch(w, rec, w.ea)
    rec.with_user(w.ua).action_accept()  # tomorrow's check cannot exist tonight
    assert rec.state == "accepted"


def test_m46_07_a_van_taken_off_the_road_after_dispatch_stops_the_job(w):
    rec = w.fo(vehicle_id=w.good.id, vehicle_driver_id=w.driver.id)
    dispatch(w, rec, w.ea)
    off = w.env["fix.vehicle.offroad"].create(
        {"vehicle_id": w.good.id, "reason": "Brakes failed at 08:00"}
    )
    w.env["fix.event.outbox"].cron_relay(limit=5000)
    assert rec.redispatch_required and rec.redispatch_offroad_id == off
    msg = refused(w.env, lambda: rec.with_user(w.ua).action_accept())
    assert msg and "taken off the road" in msg and off.name in msg
    assert rec.state == "dispatched"
    # the dispatcher re-dispatches it with another van: the job moves again
    other = w.vehicle("A07ERP-SPARE")
    rec.with_user(w.ud).write({"vehicle_id": other.id})
    assert not rec.redispatch_required
    rec.with_user(w.ua).action_accept()
    assert rec.state == "accepted"


@pytest.mark.relay_backlog  # no relay here: skip the seed-backlog sweep
def test_m46_07_an_off_road_van_stops_travel_even_before_the_flag_arrives(w):
    rec = w.fo(vehicle_id=w.good.id, vehicle_driver_id=w.driver.id)
    dispatch(w, rec, w.ea)
    rec.with_user(w.ua).action_accept()
    # the event has not been relayed yet: the gate itself refuses
    w.env["fix.vehicle.offroad"].create({"vehicle_id": w.good.id, "reason": "Tyre burst"})
    msg = refused(w.env, lambda: rec.with_user(w.ua).action_start_travel())
    assert msg and "off-road" in msg


@pytest.mark.relay_backlog  # no relay here: skip the seed-backlog sweep
def test_a_job_with_no_vehicle_is_not_gated(w):
    rec = w.fo()
    dispatch(w, rec, w.ea)
    rec.with_user(w.ua).action_accept()
    rec.with_user(w.ua).action_start_travel()
    assert rec.state == "en_route"
