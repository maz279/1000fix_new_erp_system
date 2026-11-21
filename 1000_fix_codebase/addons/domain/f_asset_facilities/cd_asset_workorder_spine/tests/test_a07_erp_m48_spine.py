"""A07 ERP audit (2026-11-20) - M48 on the work-order spine (builder stream S5).

Live ORM, rolled back. Events are delivered through the relay's own path."""

from __future__ import annotations

import uuid
from datetime import date

import pytest
from odoo import fields
from odoo.addons.cd_asset_workorder_spine.tests.test_a07_p1_spine import (
    DEMAND,
    MODULE,
    REFUSED,
    WO,
    _director,
    _equipment,
    _vehicle,
    c,  # noqa: F401 - the fixture
)
from odoo.addons.cd_stream_registry.models.fix_iot_ops import IngestRefused

TAG = uuid.uuid4().hex[:5].upper()
MODEL = "m26.predictive.maintenance"


def _deliver_one(c, event_type, record, method):  # noqa: F811
    row = c.env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate_id", "=", record.id)],
        order="id desc",
        limit=1,
    )
    assert row, "%s published no %s" % (record.display_name, event_type)
    sub = c.env["fix.event.consumer"].search(
        [("event_type", "=", event_type), ("module", "=", MODULE), ("method", "=", method)]
    )
    assert len(sub) == 1 and sub.active, (event_type, method)
    assert c.env["fix.event.outbox"]._relay_deliver(sub, row) == ""
    return row


def _govern(env):
    model = env["fix.ml.model"].search([("code", "=", MODEL)], limit=1)
    env["fix.ml.evaluation.gate"].create(
        {"version_id": model._serving_version().id, "gate": "accuracy", "result": "passed"}
    )


def _device(c, owner=None):  # noqa: F811
    brand = c.env["fix.brand"].create({"name": "E48B%s" % TAG, "code": "E%s" % TAG[:3]})
    model = c.env["fix.device.model"].create({"name": "E48 Chiller", "brand_id": brand.id})
    owner = owner or c.env["res.partner"].create({"name": "E48 Owner %s" % TAG})
    return c.env["fix.device"].create(
        {
            "device_model_id": model.id,
            "owner_id": owner.id,
            "serial_number": "E48-%s" % TAG,
            "branch_id": c.br.id,
        }
    )


def _customer_prediction(c, device):  # noqa: F811
    c.env["fix.iot.device"].create(
        {"name": "E48 sensor", "device_id": "E48S-%s" % TAG, "customer_device_id": device.id}
    )
    return c.env["fix.predictive.maintenance"].create(
        {
            "name": "E48-CUST",
            "customer_device_id": device.id,
            "prediction": "failure_predicted",
            "confidence": 0.9,
            "estimated_days_to_failure": 6,
            "model_name": MODEL,
        }
    )


def _approved_request(c, p):  # noqa: F811
    _director(c)
    p.action_create_preventive_wo("needed", scheduled_on="2026-12-03")
    action = p.preventive_action_id
    action.sudo().action_approve()  # superuser: the M63 routing is proven in M48's suite
    return action


# ================================================================== M48-04
def test_m48_04_no_contract_no_order_but_an_opportunity(c):  # noqa: F811
    _govern(c.env)
    device = _device(c)
    p = _customer_prediction(c, device)
    _approved_request(c, p)
    _deliver_one(c, "predictive_maintenance.wo_created", p, "consume_predictive_wo_created")
    demand = c.env[DEMAND].search([("prediction_id", "=", p.id)])
    assert demand.target == "service_order" and demand.device_id == device
    assert (demand.entitlement_state, demand.commercial_route) == ("no_contract", "opportunity")
    assert demand.state == "pending" and not demand.service_order_id
    assert "opportunity" in demand.blocker
    # the cron retries pending demands: still no order
    c.env[DEMAND].cron_maintenance_due()
    assert not demand.service_order_id
    _deliver_one(c, "iot.proactive_opportunity", demand, "consume_iot_proactive_opportunity")
    lead = c.env["crm.lead"].search([("description", "ilike", "[M48 demand %s]" % demand.id)])
    assert len(lead) == 1 and lead.partner_id == device.owner_id


def test_m48_04_entitled_and_consented_work_is_raised_under_the_contract(c):  # noqa: F811
    env = c.env
    _govern(env)
    device = _device(c)
    contract = env["fix.contract"].create(
        {
            "operating_unit_id": c.ou.id,
            "name": "E48 AMC",
            "family": "amc",
            "customer_id": device.owner_id.id,
            "date_start": date(2026, 1, 1),
            "date_end": date(2027, 12, 31),
            "annual_value": 1000.0,
            "covered_device_ids": [(6, 0, device.ids)],
            "stamp_duty_cert_no": "SD-E48-%s" % TAG,
            "stamp_duty_amount": 300.0,
            "has_signed_contract_doc": True,
        }
    )
    contract._guarded().write({"state": "active"})
    p = _customer_prediction(c, device)
    state, found, _why = env[DEMAND]._spine_entitlement(device)
    assert state == "no_consent" and found == contract
    env["fix.iot.consent"].create(
        {
            "subject_type": "customer",
            "partner_id": device.owner_id.id,
            "purpose": "service",
            "proactive_service": True,
            "evidence_ref": "form",
            "granted_by": "owner",
            "signal_groups_permitted": "vibration",
        }
    )
    _approved_request(c, p)
    _deliver_one(c, "predictive_maintenance.wo_created", p, "consume_predictive_wo_created")
    demand = env[DEMAND].search([("prediction_id", "=", p.id)])
    assert demand.entitlement_state == "entitled" and demand.commercial_route == "contract"
    order = demand.service_order_id
    assert order and order.order_category == "amc" and order.contract_id == contract
    # D17(c): the approved date
    assert demand.scheduled_date == fields.Date.to_date("2026-12-03")


# ================================================================== M48-05
def test_m48_05_a_vehicle_prediction_goes_to_the_vehicle_work_order(c):  # noqa: F811
    env = c.env
    _govern(env)
    vehicle = _vehicle(c, plate="E48-%s" % TAG)
    p = env["fix.predictive.maintenance"].create(
        {
            "name": "E48-VEH",
            "vehicle_id": vehicle.id,
            "prediction": "failure_predicted",
            "confidence": 0.9,
            "model_name": MODEL,
        }
    )
    with pytest.raises(REFUSED), env.cr.savepoint():
        env["fix.predictive.maintenance"].create(
            {"name": "two", "vehicle_id": vehicle.id, "equipment_id": _equipment(c, "E48X").id}
        )
    _approved_request(c, p)
    _deliver_one(c, "predictive_maintenance.wo_created", p, "consume_predictive_wo_created")
    wo = env[WO].search([("prediction_id", "=", p.id)])
    assert len(wo) == 1 and wo.vehicle_id == vehicle and wo.spine_asset_kind == "vehicle"


# ================================================================== M48-06
def test_m48_06_vehicle_telematics_feeds_m48_through_the_consent_gate(c):  # noqa: F811
    env = c.env
    vehicle = _vehicle(c, plate="E48T-%s" % TAG)
    tracker = env["fix.iot.device"].create(
        {
            "name": "E48 tracker",
            "device_id": "E48TRK-%s" % TAG,
            "device_type": "tracker",
            "vehicle_id": vehicle.id,
        }
    )
    stream = env["fix.iot.stream"].create({"device_id": tracker.id, "metric": "odometer_km"})
    stream.action_activate()
    snapshot = {"vehicle_id": vehicle.id, "odometer": 12000, "last_ping": fields.Datetime.now()}
    # a tracker needs a consent: the snapshot is refused with the reading
    with pytest.raises(IngestRefused), env.cr.savepoint():
        env["fix.vehicle.telemetry"].create(dict(snapshot))
    env["fix.iot.consent"].create(
        {
            "subject_type": "device",
            "device_id": tracker.id,
            "evidence_ref": "driver notice",
            "granted_by": "driver",
            "signal_groups_permitted": "odometer_km",
        }
    )
    env["fix.vehicle.telemetry"].create(dict(snapshot))
    readings = env["fix.iot.telemetry"].search([("device_id", "=", tracker.id)])
    assert readings.mapped("value") == [12000.0]


# ================================================================== M48-08
def test_m48_08_dispatch_raises_the_order_at_once_and_done_waits_for_it(c):  # noqa: F811
    env = c.env
    _govern(env)
    e = _equipment(c, "E48-EQ8")
    env["fix.iot.device"].create(
        {
            "name": "E48 s8",
            "device_id": "E48-8-%s" % TAG,
            "equipment_id": e.id,
            "site_id": c.site.id,
        }
    )
    p = env["fix.predictive.maintenance"].create(
        {
            "name": "E48-8",
            "equipment_id": e.id,
            "prediction": "failure_predicted",
            "model_name": MODEL,
        }
    )
    a = env["fix.iot.action"].create(
        {"prediction_id": p.id, "action_type": "replace", "technician_id": c.tech.id}
    )
    a._guarded().write({"state": "approved"})
    a.action_dispatch()
    demand = env[DEMAND].search([("iot_action_id", "=", a.id)])
    assert demand and demand.work_order_id, "raised in the dispatch, not by the relay"
    a._guarded().write({"outcome_evidence_ref": "JC-8"})
    with pytest.raises(REFUSED, match="still open"), env.cr.savepoint():
        a.action_done("confirmed", "found worn")
    # no demand at all also blocks completion
    demand.work_order_id.sudo()._guarded().write({"spine_demand_id": False, "iot_action_id": False})
    demand.sudo().unlink()
    assert "no work order" in "; ".join(a._fix_completion_blockers())


# ================================================================== M48-09
def test_m48_09_a_direct_outcome_reaches_m26(c):  # noqa: F811
    env = c.env
    e = _equipment(c, "E48-EQ9")
    p = env["fix.predictive.maintenance"].create(
        {
            "name": "E48-9",
            "equipment_id": e.id,
            "prediction": "failure_predicted",
            "model_name": MODEL,
        }
    )
    p.sudo().action_record_outcome("confirmed", "failed on site", "SO-9")
    _deliver_one(c, "intervention.outcome_recorded", p, "consume_iot_direct_outcome")
    run = env["fix.ml.inference.run"].search([("iot_prediction_id", "=", p.id)])
    # confirmed: the field bore the suggestion out (final = suggested, not overridden)
    assert len(run) == 1 and run.final_value == "failure_predicted" and not run.overridden
    _deliver_one(c, "intervention.outcome_recorded", p, "consume_iot_direct_outcome")
    assert env["fix.ml.inference.run"].search_count([("iot_prediction_id", "=", p.id)]) == 1


# ================================================================== M48-15 / 18
def test_m48_15_a_major_rule_alert_reaches_the_owner_and_raises_an_inspection(c):  # noqa: F811
    env = c.env
    device = env["fix.iot.device"].create(
        {"name": "E48 gen", "device_id": "E48G-%s" % TAG, "site_id": c.site.id}
    )
    stream = env["fix.iot.stream"].create({"device_id": device.id, "metric": "temperature"})
    stream.action_activate()
    env["fix.iot.rule"].create(
        {"stream_id": stream.id, "operator": "gt", "threshold": 90, "severity": "major"}
    )
    _reading, alerts = stream.ingest(120.0)
    assert alerts.routed_to_module == "M47"
    _deliver_one(c, "iot.rule_alert_raised", alerts, "consume_asset_alert")
    row = env["fix.asset.alert"].search(
        [("event_type", "=", "iot.rule_alert_raised"), ("res_id", "=", alerts.id)]
    )
    assert row.module == "M47" and row.notified_groups == "cd_facility.group_facility_manager"
    _deliver_one(c, "iot.rule_alert_raised", alerts, "consume_iot_rule_alert_inspection")
    demand = env[DEMAND].search(
        [("source_model", "=", "fix.iot.alert"), ("source_res_id", "=", alerts.id)]
    )
    assert demand.origin == "m48_alert" and demand.work_type == "inspection"
    assert demand.work_order_id.site_id == c.site
    _deliver_one(c, "iot.rule_alert_raised", alerts, "consume_iot_rule_alert_inspection")
    assert (
        env[DEMAND].search_count(
            [("source_model", "=", "fix.iot.alert"), ("source_res_id", "=", alerts.id)]
        )
        == 1
    )


# ================================================================== M48-13
def test_m48_13_health_degraded_raises_an_inspection_once(c):  # noqa: F811
    env = c.env
    device = env["fix.iot.device"].create(
        {"name": "E48 h", "device_id": "E48H-%s" % TAG, "site_id": c.site.id}
    )
    first = env["fix.iot.health"]._fix_score(device)
    device._fix_mark_offline()
    for n in range(4):
        env["fix.iot.alert"].create(
            {"device_id": device.id, "severity": "minor", "message": "m%d" % n}
        )
    second = env["fix.iot.health"]._fix_score(device)
    assert second.band in ("degraded", "critical") and second.band != first.band
    _deliver_one(c, "asset.health_degraded", second, "consume_asset_health_degraded")
    demand = env[DEMAND].search(
        [("source_model", "=", "fix.iot.health"), ("source_res_id", "=", second.id)]
    )
    assert demand.origin == "m48_health"


# ================================================================== LEAD-01
def test_lead_01_the_component_lot_picker_offers_m15_lots_of_the_part(c):  # noqa: F811
    env = c.env
    part = env["fix.spare.part"].create({"name": "E48 Fan", "part_number": "E48-FAN-%s" % TAG})
    other = env["fix.spare.part"].create({"name": "E48 Belt", "part_number": "E48-BLT-%s" % TAG})
    lot = env["fix.stock.lot"].create({"name": "LOT-E48-%s" % TAG, "part_id": part.id})
    wrong = env["fix.stock.lot"].create({"name": "LOT-E48W-%s" % TAG, "part_id": other.id})
    device = _device(c)
    comp = env["fix.device.component"].create(
        {"device_id": device.id, "part_number": part.part_number, "part_name": "Fan"}
    )
    assert env["fix.device.component"]._fields["stock_lot_ref_id"].comodel_name == "fix.stock.lot"
    comp.stock_lot_ref_id = lot
    assert (comp.lot_model, comp.lot_id) == ("fix.stock.lot", lot.id)
    comp.invalidate_recordset()
    assert comp.stock_lot_ref_id == lot
    with pytest.raises(REFUSED), env.cr.savepoint():
        comp.stock_lot_ref_id = wrong
        env.flush_all()
