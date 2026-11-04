"""A07 P1 wiring (builder S, 2026-11-04): the FF-48 events the spine now consumes.

Live ORM, rolled back. Each event is produced by the source module's own code
(an M45 hold, a failing calibration, a verification, the M48 liveness cron,
an M47 reopen, an M48 outcome) and handed to this module's subscription by
the relay's delivery step; every consumer is delivered twice to prove it is
idempotent on redelivery.
"""

from __future__ import annotations

import json
from datetime import timedelta

from odoo import fields
from odoo.addons.cd_asset_workorder_spine.tests import test_a07_p1_spine as _shared
from odoo.addons.cd_asset_workorder_spine.tests.test_a07_p1_spine import (
    DEMAND,
    WO,
    _deliver,
    _demands,
    _dispatch,
    _equipment,
    _m48,
    _refused,
    _run_wo,
    _vehicle,
    _vehicle_pm,
)

# the shared fixture of the module's own tests (pytest finds it by this name)
c = _shared.c

MODULE = "cd_asset_workorder_spine"
WIRED = {
    "equipment.out_of_service": (DEMAND, "consume_equipment_out_of_service"),
    "equipment.returned_to_service": (DEMAND, "consume_equipment_returned_to_service"),
    "telemetry.stream_silent": (DEMAND, "consume_telemetry_stream_silent"),
    "facility.work_order_reopened": (DEMAND, "consume_facility_work_order_reopened"),
    "equipment.impact_assessment_raised": (
        "fix.service.order.recheck",
        "consume_impact_assessment_raised",
    ),
    "equipment.impact_assessment_closed": (
        "fix.service.order.recheck",
        "consume_impact_assessment_closed",
    ),
    "iot.intervention_outcome_recorded": (
        "fix.ml.inference.run",
        "consume_iot_intervention_outcome",
    ),
}


def test_each_wired_event_has_one_active_subscription(c):
    for event_type, (model, method) in WIRED.items():
        sub = c.env["fix.event.consumer"].search(
            [("event_type", "=", event_type), ("module", "=", MODULE)]
        )
        assert len(sub) == 1 and sub.active, event_type
        assert (sub.model, sub.method) == (model, method)
        assert callable(getattr(c.env[model], method))


# ------------------------------------------------------------ M45 holds
def _cal(c, e, on, due, result="pass"):
    return c.env["fix.calibration"].create(
        {
            "equipment_id": e.id,
            "calibrated_on": on,
            "next_due": due,
            "standard_ref": "STD-A7W",
            "result": result,
            "certificate_ref": "CERT-A7W",
            "performed_by": "A7W Lab",
        }
    )


def test_a_fault_hold_raises_one_repair_work_order_left_alone_when_it_returns(c):
    e = _equipment(c, "A7WIR-EQ1")
    hold = c.env["fix.equipment.oos"].create({"equipment_id": e.id, "reason": "Display dead"})
    _deliver(c, "equipment.out_of_service", hold)
    _deliver(c, "equipment.out_of_service", hold)
    demand = _demands(c, hold)
    wo = demand.work_order_id
    assert len(demand) == 1 and demand.origin == "m45_repair" and demand.state == "routed"
    assert (wo.work_type, wo.equipment_id, wo.site_id, wo.state) == ("repair", e, c.site, "draft")
    assert (wo.spine_origin, wo.spine_asset_kind) == ("m45_repair", "equipment")
    assert (
        hold.name in wo.description
        and c.env[WO].search_count([("spine_demand_id", "=", demand.id)]) == 1
    )
    # back in service in M45 while the WO is open: the WO is left to its manager
    hold.action_resolve()
    _deliver(c, "equipment.returned_to_service", hold)
    _deliver(c, "equipment.returned_to_service", hold)
    assert demand.state == "routed" and wo.state == "draft"
    assert demand.source_log.count("[rts:%s]" % hold.id) == 1
    assert "stays as it is" in demand.source_log
    assert any("stays as it is" in (m.body or "") for m in wo.message_ids)


def test_a_failed_calibration_hold_raises_a_calibration_demand_dismissed_on_return(c):
    e = _equipment(c, "A7WIR-EQ2", branch_id=c.br_bare.id)
    _cal(c, e, c.today - timedelta(days=200), c.today + timedelta(days=165))
    fail = _cal(c, e, c.today, c.today + timedelta(days=1), result="fail")
    hold = c.env["fix.equipment.oos"].search(
        [("equipment_id", "=", e.id), ("state", "=", "open"), ("hold_type", "=", "calibration")]
    )
    assert hold.calibration_id == fail
    _deliver(c, "equipment.out_of_service", hold)
    demand = _demands(c, hold)
    assert demand.origin == "m45_calibration" and demand.work_type == "inspection"
    assert demand.calibration_due == hold.started_on
    # no M47 site for the branch: pending with what it needs, nothing guessed
    assert demand.state == "pending" and "has no M47 site" in demand.blocker
    hold.action_resolve()
    _deliver(c, "equipment.returned_to_service", hold)
    _deliver(c, "equipment.returned_to_service", hold)
    assert demand.state == "dismissed" and hold.name in demand.dismiss_reason
    assert demand.source_log.count("[rts:") == 1 and not demand.work_order_id


# ------------------------------------------------------------ M48 silence
def _silent(c, device, metric):
    stream = c.env["fix.iot.stream"].create(
        {"device_id": device.id, "metric": metric, "sample_interval_sec": 60}
    )
    stream._guarded().write(
        {"state": "active", "activated_on": fields.Datetime.now() - timedelta(days=2)}
    )
    return stream


def test_a_silent_stream_raises_one_inspection_per_episode_and_device(c):
    e, _p = _m48(c)
    device = c.env["fix.iot.device"].search([("equipment_id", "=", e.id)])
    temp = _silent(c, device, "temperature")
    vib = _silent(c, device, "vibration")
    assert c.env["fix.iot.stream"].cron_liveness() >= 2
    gap_t = c.env["fix.iot.gap"].search([("stream_id", "=", temp.id)])
    gap_v = c.env["fix.iot.gap"].search([("stream_id", "=", vib.id)])
    _deliver(c, "telemetry.stream_silent", temp)
    _deliver(c, "telemetry.stream_silent", temp)
    _deliver(c, "telemetry.stream_silent", vib)
    _deliver(c, "telemetry.stream_silent", vib)
    demand = c.env[DEMAND].search(
        [("iot_device_id", "=", device.id), ("origin", "=", "m48_silent")]
    )
    assert len(demand) == 1 and demand.source_model == "fix.iot.gap"
    assert demand.source_res_id == gap_t.id
    wo = demand.work_order_id
    assert (wo.work_type, wo.site_id, wo.equipment_id, wo.iot_device_id) == (
        "inspection",
        c.site,
        e,
        device,
    )
    assert wo.spine_asset_kind == "iot" and gap_t.name in wo.description
    # the second stream's episode joined the open inspection, once
    assert demand.source_log.count("[gap:%s]" % gap_v.id) == 1
    assert demand.source_log.count("[gap:%s]" % gap_t.id) == 1


def test_a_silent_customer_device_waits_for_its_registered_m17_device(c):
    customer = c.env["res.partner"].create({"name": "A7WIR Clinic", "phone": "01711000881"})
    e, _p = _m48(c, partner=customer)
    device = c.env["fix.iot.device"].search([("equipment_id", "=", e.id)])
    stream = _silent(c, device, "temperature")
    c.env["fix.iot.stream"].cron_liveness()
    _deliver(c, "telemetry.stream_silent", stream)
    demand = c.env[DEMAND].search([("iot_device_id", "=", device.id)])
    assert demand.target == "service_order" and demand.partner_id == customer
    assert demand.state == "pending" and "registered device" in demand.blocker
    assert not demand.work_order_id and not demand.service_order_id


# ------------------------------------------------------------ M45 impact -> M01
def _service_order(c, serial):
    brand = c.env["fix.brand"].search([("code", "=", "A7WB")]) or c.env["fix.brand"].create(
        {"name": "A7WIRBrand", "code": "A7WB"}
    )
    model = c.env["fix.device.model"].create({"name": "A7WIR %s" % serial, "brand_id": brand.id})
    owner = c.env["res.partner"].create({"name": "A7WIR Owner %s" % serial})
    device = c.env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": owner.id, "serial_number": serial}
    )
    return c.env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": owner.id,
            "branch_id": c.br.id,
            "fault_description": "No charge",
            "technician_id": c.tech.id,
        }
    )


def test_an_impact_assessment_flags_the_orders_behind_its_uses_and_records_the_disposition(c):
    e = _equipment(c, "A7WIR-EQ3")
    _cal(c, e, c.today - timedelta(days=200), c.today + timedelta(days=165))
    so1, so2 = _service_order(c, "A7WIR-S1"), _service_order(c, "A7WIR-S2")
    Usage = c.env["fix.equipment.usage"]
    Usage.m45_record_qc_use(e, "QC-%s" % so1.name, "pass", source=so1, service_order_ref=so1.name)
    Usage.create({"equipment_id": e.id, "job_ref": so2.name})
    Usage.create({"equipment_id": e.id, "job_ref": "A7WIR-NOWHERE"})
    states = (so1.state, so2.state)
    fail = _cal(c, e, c.today, c.today + timedelta(days=1), result="fail")
    impact = fail.impact_id
    assert len(impact.usage_ids) == 3
    _deliver(c, "equipment.impact_assessment_raised", impact)
    _deliver(c, "equipment.impact_assessment_raised", impact)
    Recheck = c.env["fix.service.order.recheck"]
    lines = Recheck.search([("impact_id", "=", impact.id)])
    assert lines.order_id == so1 | so2 and len(lines) == 2
    assert so1.quality_recheck_required and so2.quality_recheck_required
    assert (so1.state, so2.state) == states  # never a state change
    acts = so1.activity_ids.filtered(lambda a: impact.name in (a.summary or ""))
    assert len(acts) == 1 and acts.user_id == c.clerk
    assert any("A7WIR-NOWHERE" in (m.body or "") for m in impact.message_ids)
    # the flags are the bridge's
    line = lines.filtered(lambda r: r.order_id == so1)
    _refused(c.env, line.with_user(c.clerk).write, {"state": "decided"})
    _refused(c.env, so1.with_user(c.clerk).write, {"quality_recheck_required": False})
    # the Quality Manager's disposition lands on the flags; the activity is completed
    impact.write({"disposition": "retested", "disposition_note": "Re-tested both units, OK"})
    impact.action_close_impact()
    _deliver(c, "equipment.impact_assessment_closed", impact)
    _deliver(c, "equipment.impact_assessment_closed", impact)
    assert set(lines.mapped("state")) == {"decided"}
    assert set(lines.mapped("disposition")) == {"retested"}
    # done: removed, or archived where the activity type keeps done activities
    assert not so1.quality_recheck_required and not acts.exists().filtered("active")
    assert (so1.state, so2.state) == states


# ------------------------------------------------------------ M47 reopen
def test_a_reopened_spine_work_order_reopens_its_demand_and_names_a_completed_source(c):
    vehicle = _vehicle(c, plate="A7WIR-1")
    pm = _vehicle_pm(c, vehicle)
    c.env["fix.vehicle.pm"].cron_pm_due()
    _deliver(c, "vehicle.service_due", pm)
    demand = _demands(c, pm)
    wo = demand.work_order_id
    _run_wo(c, wo)
    wo.with_user(c.fm).action_reopen(reason="oil leak found")
    _deliver(c, "facility.work_order_reopened", wo)
    _deliver(c, "facility.work_order_reopened", wo)
    assert demand.state == "routed" and demand.source_log.count("reopened: oil leak") == 1
    assert "not un-completed" not in demand.source_log
    # the fleet office closed the service by hand; then the WO is reopened again
    pm.with_user(c.officer).write({"odometer": 51000})
    pm.action_done()
    wo.with_user(c.fm).action_complete(notes="Leak fixed")
    demand._guarded().write({"state": "done"})  # as a verification would leave it
    wo.with_user(c.fm).action_reopen(reason="leak again")
    _deliver(c, "facility.work_order_reopened", wo)
    assert demand.state == "routed" and pm.state == "done"
    assert "routed again" in demand.source_log and "not un-completed" in demand.source_log
    assert demand.source_log.count("[reopen:") == 2


# ------------------------------------------------------------ M48 -> M26
def test_an_intervention_outcome_becomes_one_m26_ground_truth_row(c):
    _e, p = _m48(c)
    a = _dispatch(c, p)
    a.write({"outcome_evidence_ref": "JC-A7WIR-1"})
    a.action_done(outcome="not_confirmed", note="Bearing within limits")
    _deliver(c, "iot.intervention_outcome_recorded", a)
    _deliver(c, "iot.intervention_outcome_recorded", a)
    Run = c.env["fix.ml.inference.run"]
    run = Run.search([("iot_action_id", "=", a.id)])
    assert len(run) == 1 and run.model_id.code == "m26.predictive.maintenance"
    assert (run.suggested_value, run.final_value, run.overridden) == (
        "failure_predicted",
        "false_alarm",
        True,
    )
    assert "Bearing" in run.override_reason and run.state == "computed"
    assert json.loads(run.output_json)["evidence_ref"] == "JC-A7WIR-1"
    assert json.loads(run.input_text)["prediction"] == p.name
    _refused(c.env, run.with_user(c.clerk).write, {"iot_action_id": False})
