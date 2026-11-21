"""A07 P1 bridge (builder S): the one work-order spine and its event consumers.

Live ORM, rolled back. Events are produced by the source modules' own code
(crons, dispatch, the preventive-WO action) and handed to this module's
subscription through the relay's own delivery path. Attacks run as NON-ADMIN
users with the role they would really hold (Facility Manager, Fleet Officer)
and without it.
"""

from __future__ import annotations

import types
from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError
from psycopg2 import Error as PgError

REFUSED = (UserError, ValidationError, AccessError, PgError)
FM = "cd_facility.group_facility_manager"
DIRECTOR = "cd_facility.group_operations_director"
OFFICER = "fleet.fleet_group_user"
WO = "fix.facility.work.order"
DEMAND = "fix.maintenance.demand"
MODULE = "cd_asset_workorder_spine"
CONSUMED = {
    "equipment.calibration_due": "consume_equipment_calibration_due",
    "vehicle.service_due": "consume_vehicle_service_due",
    "iot.action_dispatched": "consume_iot_action_dispatched",
    "predictive_maintenance.wo_created": "consume_predictive_wo_created",
    "device.maintenance_due": "consume_device_maintenance_due",
    "vehicle.assigned": "consume_vehicle_assigned",
}


def _refused(env, fn, *args, match=None, **kw):
    with pytest.raises(REFUSED, match=match), env.cr.savepoint():
        fn(*args, **kw)
        env.flush_all()


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.today = fields.Date.context_today(env["fix.site"])
    x.ou = env["operating.unit"].search([], limit=1)
    x.co = env.company
    # one legal entity per company (fix_entity_company_unique): reuse it
    entity = env["fix.entity"].search([("company_id", "=", x.co.id)], limit=1) or env[
        "fix.entity"
    ].create({"code": "A7SPN", "legal_name": "A07 spine entity", "company_id": x.co.id})

    def branch(code):
        return env["fix.branch"].create(
            {
                "name": "A07 Spine %s" % code,
                "code": code,
                "entity_id": entity.id,
                "operating_unit_id": x.ou.id,
            }
        )

    x.br, x.br_twin, x.br_bare = branch("A7SP1"), branch("A7SP2"), branch("A7SP3")
    x.site = env["fix.site"].create(
        {
            "name": "A07 Spine Branch Site",
            "company_id": x.co.id,
            "state": "active",
            "branch_id": x.br.id,
            "operating_unit_id": x.ou.id,
        }
    )
    for n in (1, 2):
        env["fix.site"].create(
            {
                "name": "A07 Spine Twin %d" % n,
                "company_id": x.co.id,
                "state": "active",
                "branch_id": x.br_twin.id,
            }
        )

    def user(login, *groups):
        ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
        return (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": login,
                    "login": login,
                    "group_ids": [(6, 0, ids)],
                    "company_ids": [(6, 0, x.co.ids)],
                    "company_id": x.co.id,
                    "assigned_operating_unit_ids": [(6, 0, x.ou.ids)],
                    "default_operating_unit_id": x.ou.id,
                }
            )
        )

    x.clerk = user("a07spine_clerk")
    x.fm, x.fm2 = user("a07spine_fm", FM), user("a07spine_fm2", FM)
    x.officer = user("a07spine_officer", OFFICER)
    x.tech = env["hr.employee"].create({"name": "A07 Spine Engineer", "user_id": x.clerk.id})
    return x


def _deliver(c, event_type, record):
    """Hand the latest `event_type` outbox row of `record` to this module's
    subscription, through the relay's delivery (savepoint, superuser)."""
    Outbox = c.env["fix.event.outbox"]
    row = Outbox.search(
        [("event_type", "=", event_type), ("aggregate_id", "=", record.id)],
        order="id desc",
        limit=1,
    )
    assert row, "%s published no %s" % (record.display_name, event_type)
    sub = c.env["fix.event.consumer"].search(
        [("event_type", "=", event_type), ("module", "=", MODULE)]
    )
    if len(sub) > 1:  # A07 ERP: iot.rule_alert_raised also reaches the asset alert
        sub = sub.filtered(lambda s: s.model == DEMAND)
    assert len(sub) == 1 and sub.active
    assert Outbox._relay_deliver(sub, row) == ""
    return row


def _demands(c, record):
    return c.env[DEMAND].search(
        [("source_model", "=", record._name), ("source_res_id", "=", record.id)]
    )


def _run_wo(c, wo, notes="Done, job sheet JS-1"):
    wo.with_user(c.fm).action_schedule()
    wo.with_user(c.fm).action_start()
    wo.with_user(c.fm).action_complete(notes=notes)


# ------------------------------------------------------------ wiring
def test_each_consumed_event_has_an_active_subscription_and_the_cron_runs(c):
    for event_type, method in CONSUMED.items():
        sub = c.env["fix.event.consumer"].search(
            [("event_type", "=", event_type), ("module", "=", MODULE)]
        )
        assert sub.active and sub.model == DEMAND and sub.method == method
        assert callable(getattr(c.env[DEMAND], method))
    cron = c.env.ref("%s.ir_cron_spine_maintenance_due" % MODULE)
    assert cron.active and cron.model_id.model == DEMAND
    assert cron.code.strip() == "model.cron_maintenance_due()"
    assert cron.interval_type == "days" and cron.interval_number == 1


# ------------------------------------------------------------ M46
def _vehicle(c, plate="A7SPN-1", **kw):
    brand = c.env["fleet.vehicle.model.brand"].create({"name": "A7SPN Brand"})
    model = c.env["fleet.vehicle.model"].create(
        {"name": "A7SPN Van", "brand_id": brand.id, "vehicle_type": "car"}
    )
    vals = {"model_id": model.id, "license_plate": plate, "branch_id": c.br.id}
    vals.update(kw)
    return c.env["fleet.vehicle"].create(vals)


def _vehicle_pm(c, vehicle, **kw):
    vals = {
        "vehicle_id": vehicle.id,
        "pm_type": "service",
        "due_date": c.today - timedelta(days=2),
        "scheduled_on": c.today - timedelta(days=2),
    }
    vals.update(kw)
    return c.env["fix.vehicle.pm"].create(vals)


def test_m46_service_due_becomes_one_spine_work_order_completed_by_its_verification(c):
    vehicle = _vehicle(c)
    pm = _vehicle_pm(c, vehicle)
    c.env["fix.vehicle.pm"].cron_pm_due()
    _deliver(c, "vehicle.service_due", pm)
    demand = _demands(c, pm)
    wo = demand.work_order_id
    assert demand.state == "routed" and demand.origin == "m46_service"
    assert (wo.vehicle_id, wo.vehicle_pm_id, wo.site_id) == (vehicle, pm, c.site)
    assert (wo.spine_origin, wo.spine_asset_kind, wo.state) == ("m46_service", "vehicle", "draft")
    # redelivery and a second route attempt raise nothing new
    _deliver(c, "vehicle.service_due", pm)
    c.env[DEMAND].cron_maintenance_due()
    assert len(_demands(c, pm)) == 1
    assert c.env[WO].search_count([("vehicle_pm_id", "=", pm.id)]) == 1
    # M47's lifecycle is the spine's: a plain user does not verify
    _run_wo(c, wo)
    _refused(c.env, wo.with_user(c.clerk).action_verify, match="Facility Manager")
    # the source refuses completion without its odometer: so does the verification
    _refused(c.env, wo.with_user(c.fm2).action_verify, match="odometer")
    assert wo.state == "completed" and pm.state == "open"
    pm.with_user(c.officer).write({"odometer": 41200})
    wo.with_user(c.fm2).action_verify(notes="Checked")
    assert wo.state == "verified"
    assert (pm.state, pm.done_by_id) == ("done", c.fm2)
    assert demand.state == "done"
    done = c.env["fix.event.outbox"].search(
        [("event_type", "=", "vehicle.service_completed"), ("aggregate_id", "=", pm.id)]
    )
    assert len(done) == 1


def test_the_relay_cron_delivers_a_due_service_to_the_spine(c):
    pm = _vehicle_pm(c, _vehicle(c, plate="A7SPN-R"))
    c.env["fix.vehicle.pm"].cron_pm_due()
    row = c.env["fix.event.outbox"].search(
        [("event_type", "=", "vehicle.service_due"), ("aggregate_id", "=", pm.id)]
    )
    assert row and not c.env[WO].search_count([("vehicle_pm_id", "=", pm.id)])
    c.env["fix.event.outbox"].cron_relay(limit=5000)
    sub = c.env.ref("%s.consumer_vehicle_service_due" % MODULE)
    delivery = c.env["fix.event.consumer.delivery"].search(
        [("subscription_id", "=", sub.id), ("event_id", "=", row.id)]
    )
    assert delivery.state == "done", delivery.last_error
    assert c.env[WO].search_count([("vehicle_pm_id", "=", pm.id)]) == 1


def test_spine_links_are_set_only_by_routing(c):
    vehicle = _vehicle(c, plate="A7SPN-2")
    pm = _vehicle_pm(c, vehicle)
    wo = (
        c.env[WO]
        .with_user(c.clerk)
        .create({"site_id": c.site.id, "work_type": "repair", "description": "Hand-raised job"})
    )
    assert wo.spine_origin == "request" and not wo.spine_source_ref
    for vals in ({"vehicle_id": vehicle.id}, {"vehicle_pm_id": pm.id}):
        _refused(c.env, wo.with_user(c.clerk).write, vals, match="cannot be set directly")
    _refused(
        c.env,
        c.env[WO].with_user(c.clerk).create,
        {"site_id": c.site.id, "description": "x", "vehicle_pm_id": pm.id},
        match="cannot be set directly",
    )
    c.env["fix.vehicle.pm"].cron_pm_due()
    _deliver(c, "vehicle.service_due", pm)
    demand = _demands(c, pm)
    # the ledger is the system's: no hand create, state change or delete
    _refused(
        c.env,
        c.env[DEMAND].with_user(c.fm).create,
        {
            "name": "x",
            "origin": "m45_pm",
            "target": "work_order",
            "source_model": "x",
            "source_res_id": 1,
            "description": "x",
        },
    )
    _refused(
        c.env, demand.with_user(c.fm).write, {"state": "pending"}, match="cannot be set directly"
    )
    _refused(c.env, demand.with_user(c.fm).unlink, match="dismiss")
    # one source item, one OPEN work order, whatever path tries a second
    _refused(
        c.env,
        c.env[WO]._guarded().create,
        {"site_id": c.site.id, "description": "dup", "spine_demand_id": demand.id},
    )
    # once the first is cancelled, the demand returns to the queue and is routed again
    demand.work_order_id.with_user(c.fm).action_cancel(reason="duplicate booking")
    assert demand.state == "pending" and "cancelled" in demand.blocker
    demand.with_user(c.fm).action_route()
    assert demand.state == "routed" and demand.work_order_id.state == "draft"
    assert c.env[WO].search_count([("vehicle_pm_id", "=", pm.id)]) == 2


# ------------------------------------------------------------ M45
def _equipment(c, code, **kw):
    vals = {
        "code": code,
        "name": "A07 Spine meter %s" % code,
        "category": "Electrical",
        "branch_id": c.br.id,
    }
    vals.update(kw)
    return c.env["fix.equipment"].create(vals)


def _calibration(c, e, on, due):
    return c.env["fix.calibration"].create(
        {
            "equipment_id": e.id,
            "calibrated_on": on,
            "next_due": due,
            "standard_ref": "STD-A7",
            "result": "pass",
            "certificate_ref": "CERT-A7",
            "performed_by": "A7 Lab",
        }
    )


def test_m45_pm_due_raises_its_work_order_and_verification_marks_it_done(c):
    e = _equipment(c, "A7SPN-EQ1")
    pm = c.env["fix.equipment.pm"].create(
        {"equipment_id": e.id, "pm_type": "preventive", "scheduled_on": c.today}
    )
    later = c.env["fix.equipment.pm"].create(
        {"equipment_id": e.id, "scheduled_on": c.today + timedelta(days=30)}
    )
    c.env[DEMAND].cron_maintenance_due()
    c.env[DEMAND].cron_maintenance_due()
    wo = c.env[WO].search([("equipment_pm_id", "=", pm.id)])
    assert len(wo) == 1 and not _demands(c, later)
    assert (wo.spine_origin, wo.spine_asset_kind, wo.equipment_id) == ("m45_pm", "equipment", e)
    _run_wo(c, wo, notes="Bearings replaced, JS-9")
    # the M45 job records who did it: the verification asks for the engineer
    _refused(c.env, wo.with_user(c.fm2).action_verify, match="engineer")
    wo.with_user(c.fm).write({"assigned_to": c.tech.id})
    wo.with_user(c.fm2).action_verify()
    assert (pm.state, pm.technician_id) == ("done", c.tech)
    assert wo.name in pm.notes and "JS-9" in pm.notes


def test_m45_calibration_due_raises_one_work_order_that_needs_the_calibration(c):
    e = _equipment(c, "A7SPN-EQ2")
    _calibration(c, e, c.today - timedelta(days=340), c.today + timedelta(days=20))
    c.env["fix.equipment"].cron_calibration_status()
    _deliver(c, "equipment.calibration_due", e)
    demand = _demands(c, e)
    wo = demand.work_order_id
    assert demand.source_key == str(c.today + timedelta(days=20))
    assert (wo.spine_origin, wo.work_type, wo.spine_calibration_due) == (
        "m45_calibration",
        "inspection",
        c.today + timedelta(days=20),
    )
    # a later alert of the same due date (reset to the 60-day stamp so the
    # 30-day alert goes out again) raises nothing new
    e.sudo()._guarded().write({"calibration_alert_days": 60})
    c.env["fix.equipment"].cron_calibration_status()
    _deliver(c, "equipment.calibration_due", e)
    assert len(_demands(c, e)) == 1
    _run_wo(c, wo, notes="Sent to the lab")
    _refused(c.env, wo.with_user(c.fm2).action_verify, match="record the calibration")
    cal = _calibration(c, e, c.today, c.today + timedelta(days=365))
    wo.with_user(c.fm2).action_verify()
    assert wo.state == "verified" and wo.spine_calibration_id == cal


def test_an_unroutable_demand_waits_with_what_it_needs_and_a_facility_manager_routes_it(c):
    bare = _equipment(c, "A7SPN-EQ3", branch_id=c.br_bare.id)
    twin = _equipment(c, "A7SPN-EQ4", branch_id=c.br_twin.id)
    for e in (bare, twin):
        c.env["fix.equipment.pm"].create({"equipment_id": e.id, "scheduled_on": c.today})
    c.env[DEMAND].cron_maintenance_due()
    d_bare = c.env[DEMAND].search([("equipment_id", "=", bare.id)])
    d_twin = c.env[DEMAND].search([("equipment_id", "=", twin.id)])
    assert d_bare.state == "pending" and "has no M47 site" in d_bare.blocker
    assert d_twin.state == "pending" and "2 M47 sites" in d_twin.blocker
    assert not d_bare.work_order_id
    # a plain user neither routes nor dismisses
    _refused(c.env, d_bare.with_user(c.clerk).action_route, match="Facility Manager")
    _refused(c.env, d_bare.with_user(c.clerk).action_dismiss, "no", match="Facility Manager")
    _refused(c.env, d_bare.with_user(c.fm).action_route, match="choose the site")
    d_bare.with_user(c.fm).write({"site_id": c.site.id})
    d_bare.with_user(c.fm).action_route()
    wo = d_bare.work_order_id
    assert d_bare.state == "routed" and d_bare.routed_by_id == c.fm and wo.create_uid == c.fm
    # routed: the routing facts are frozen
    _refused(
        c.env, d_bare.with_user(c.fm).write, {"site_id": False}, match="cannot be set directly"
    )
    # the router does not verify the work order raised in their name (M47 SoD)
    wo.with_user(c.fm).write({"assigned_to": c.tech.id})
    _run_wo(c, wo)
    _refused(c.env, wo.with_user(c.fm).action_verify, match="Segregation")
    _refused(c.env, d_twin.with_user(c.fm).action_dismiss, "", match="why")
    d_twin.with_user(c.fm).action_dismiss("asset retired, job raised by hand")
    assert d_twin.state == "dismissed" and d_twin.dismissed_by_id == c.fm


# ------------------------------------------------------------ M48
def _govern(env, code="m26.predictive.maintenance"):
    """A07 ERP audit (2026-11-20) M48-02: only a score of a governed model version
    (deployed, accuracy gate passed) drives work. Give the serving version its gate."""
    version = env["fix.ml.model"].search([("code", "=", code)], limit=1)._serving_version()
    if not version.gate_ids.filtered(lambda g: g.gate == "accuracy" and g.result == "passed"):
        env["fix.ml.evaluation.gate"].create(
            {"version_id": version.id, "gate": "accuracy", "result": "passed"}
        )
    return version


def _director(c):
    """Someone the M63 engine can route an M48 approval to."""
    Users = c.env["res.users"].with_context(active_test=False)
    found = Users.search([("login", "=", "a07spine_director")], limit=1)
    return found or Users.with_context(no_reset_password=True).create(
        {
            "name": "a07spine_director",
            "login": "a07spine_director",
            "group_ids": [(6, 0, [c.env.ref("base.group_user").id, c.env.ref(DIRECTOR).id])],
            "company_ids": [(6, 0, c.co.ids)],
            "company_id": c.co.id,
        }
    )


def _request(c, p, user=None):
    """M48-03: request the preventive work order and approve it (the M63 routing
    of the approval is proven in cd_stream_registry's suite)."""
    _director(c)
    p.with_user(user or c.env.user).action_create_preventive_wo("bearing failing")
    p.preventive_action_id.sudo().action_approve()
    return p.preventive_action_id


def _m48(c, partner=None, site=None):
    _govern(c.env)
    e = _equipment(c, "A7SPN-IOT-%s" % ("C" if partner else "I"))
    c.env["fix.iot.device"].create(
        {
            "name": "A7SPN sensor",
            "device_id": "A7SPN-DEV-%s" % e.id,
            "equipment_id": e.id,
            "partner_id": partner.id if partner else False,
            "site_id": (site or c.site).id if not partner else False,
        }
    )
    p = c.env["fix.predictive.maintenance"].create(
        {
            "name": "A7SPN-PDM",
            "equipment_id": e.id,
            "prediction": "failure_predicted",
            "confidence": 0.8,
            "estimated_days_to_failure": 9,
            "model_name": "m26.predictive.maintenance",
        }
    )
    return e, p


def _dispatch(c, p):
    a = c.env["fix.iot.action"].create(
        {"prediction_id": p.id, "action_type": "replace", "technician_id": c.tech.id}
    )
    # approval is M48's (routed through M63, tested there); here it is given
    a._guarded().write({"state": "approved"})
    a.action_dispatch()
    return a


def test_m48_dispatch_on_an_internal_asset_raises_the_spine_work_order(c):
    e, p = _m48(c)
    a = _dispatch(c, p)
    _deliver(c, "iot.action_dispatched", a)
    wo = c.env[WO].search([("iot_action_id", "=", a.id)])
    assert len(wo) == 1 and wo.prediction_id == p and wo.equipment_id == e
    assert (wo.spine_origin, wo.spine_asset_kind) == ("m48_action", "iot")
    assert (wo.site_id, wo.assigned_to) == (c.site, c.tech)
    assert a.spine_work_order_id == wo and not a.spine_service_order_id
    # A07 ERP audit (2026-11-20) M48-03: with an action under way, a preventive
    # request is refused (the action's order is the work)
    _refused(c.env, p.action_create_preventive_wo, "bearing failing")
    _deliver(c, "iot.action_dispatched", a)
    assert c.env[WO].search_count([("prediction_id", "=", p.id)]) == 1
    # verification gives the action its evidence; the outcome stays M48's step
    _run_wo(c, wo, notes="Bearing replaced")
    wo.with_user(c.fm2).action_verify()
    assert a.state == "dispatched" and not a.outcome
    assert wo.name in a.outcome_evidence_ref
    assert p.outcome == "pending"


def test_m48_predicted_failure_first_then_the_action_joins_the_same_work_order(c):
    _e, p = _m48(c)
    request = _request(c, p)
    _deliver(c, "predictive_maintenance.wo_created", p)
    wo = c.env[WO].search([("prediction_id", "=", p.id)])
    assert len(wo) == 1 and wo.spine_origin == "m48_prediction" and not wo.iot_action_id
    # the approved request itself is dispatched and joins its own order
    request.write({"technician_id": c.tech.id})
    request.action_dispatch()
    a = request
    _deliver(c, "iot.action_dispatched", a)
    assert c.env[WO].search([("prediction_id", "=", p.id)]) == wo
    assert wo.iot_action_id == a and wo.assigned_to == c.tech


def test_m48_on_customer_premises_raises_a_draft_m01_order_on_the_customers_device(c):
    customer = c.env["res.partner"].create({"name": "A7SPN Hospital", "phone": "01711000771"})
    _e, p = _m48(c, partner=customer)
    a = _dispatch(c, p)
    _deliver(c, "iot.action_dispatched", a)
    demand = _demands(c, a)
    assert demand.target == "service_order" and demand.partner_id == customer
    assert demand.state == "pending" and demand.commercial_route == "opportunity"  # A07 ERP M48-04
    assert not c.env[WO].search_count([("iot_action_id", "=", a.id)])
    brand = c.env["fix.brand"].create({"name": "A7SPNBrand", "code": "A7SB"})
    model = c.env["fix.device.model"].create({"name": "A7SPN Chiller", "brand_id": brand.id})
    stranger = c.env["res.partner"].create({"name": "A7SPN Someone Else"})
    wrong = c.env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": stranger.id, "serial_number": "A7SPN-W"}
    )
    mine = c.env["fix.device"].create(
        {
            "device_model_id": model.id,
            "owner_id": customer.id,
            "serial_number": "A7SPN-M",
            "branch_id": c.br.id,
        }
    )
    demand.with_user(c.clerk).write({"device_id": wrong.id})
    _refused(c.env, demand.with_user(c.clerk).action_route, match="belongs to")
    demand.with_user(c.clerk).write({"device_id": mine.id})
    demand.with_user(c.clerk).action_route()
    so = demand.service_order_id
    assert (so.state, so.service_type, so.customer_id, so.device_id) == (
        "draft",
        "onsite",
        customer,
        mine,
    )
    assert so.branch_id == c.br and a.name in so.fault_description
    a.invalidate_recordset()
    assert a.spine_service_order_id == so and not a.spine_work_order_id


# ------------------------------------------------------------ M17 -> M01
def test_device_maintenance_due_raises_the_owners_draft_preventive_order_once(c):
    brand = c.env["fix.brand"].create({"name": "A7SPNB2", "code": "A7S2"})
    model = c.env["fix.device.model"].create({"name": "A7SPN Laptop", "brand_id": brand.id})
    owner = c.env["res.partner"].create({"name": "A7SPN Owner", "phone": "01711000772"})
    device = c.env["fix.device"].create(
        {
            "device_model_id": model.id,
            "owner_id": owner.id,
            "serial_number": "A7SPN-L1",
            "branch_id": c.br.id,
        }
    )
    plan = c.env["fix.device.pm"].create(
        {"device_id": device.id, "plan_type": "annual", "next_due": c.today - timedelta(days=1)}
    )
    c.env["fix.device.pm"].cron_pm_due()
    _deliver(c, "device.maintenance_due", device)
    demand = c.env[DEMAND].search([("device_pm_id", "=", plan.id)])
    so = demand.service_order_id
    assert demand.state == "routed" and demand.origin == "m17_device_pm"
    assert (so.state, so.service_type, so.order_category) == ("draft", "pm_schedule", "standard")
    assert (so.customer_id, so.device_id, so.branch_id) == (owner, device, c.br)
    _deliver(c, "device.maintenance_due", device)
    # the plan falls due again while that order is open: no second order
    plan.sudo()._guarded().write({"next_due": c.today, "due_notified_for": False})
    c.env["fix.device.pm"].cron_pm_due()
    _deliver(c, "device.maintenance_due", device)
    assert c.env[DEMAND].search_count([("device_pm_id", "=", plan.id)]) == 1
    assert c.env["fix.service.order"].search_count([("device_id", "=", device.id)]) == 1


# ------------------------------------------------------------ M46 booking
def test_a_vehicle_booked_on_its_maintenance_day_is_flagged_once(c):
    c.env["ir.config_parameter"].sudo().set_param(
        "cd_vehicle_ext.mandatory_document_types", "fitness"
    )
    vehicle = _vehicle(c, plate="A7SPN-3")
    c.env["fix.vehicle.document"].create(
        {
            "vehicle_id": vehicle.id,
            "doc_type": "fitness",
            "number": "F-1",
            "valid_to": c.today + timedelta(days=200),
            "evidence_file": "JVBERi0xLjQgc2Nhbg==",
        }
    )
    pm = _vehicle_pm(c, vehicle)
    c.env["fix.vehicle.pm"].cron_pm_due()
    _deliver(c, "vehicle.service_due", pm)
    wo = c.env[WO].search([("vehicle_pm_id", "=", pm.id)])
    day = c.today + timedelta(days=3)
    wo.with_user(c.fm).write({"scheduled_date": day})
    # M46: a duty booking is made by a fleet officer
    c.clerk.group_ids = [(4, c.env.ref("fleet.fleet_group_user").id)]
    booking = (
        c.env["fix.vehicle.assignment"]
        .with_user(c.clerk)
        .create({"vehicle_id": vehicle.id, "date": day})
    )
    _deliver(c, "vehicle.assigned", booking)
    _deliver(c, "vehicle.assigned", booking)
    assert wo.spine_conflict_assignment_ids == booking
    acts = booking.activity_ids.filtered(lambda a: "maintenance" in (a.summary or ""))
    assert len(acts) == 1 and acts.user_id == c.clerk
    other = (
        c.env["fix.vehicle.assignment"]
        .with_user(c.clerk)
        .create({"vehicle_id": vehicle.id, "date": day + timedelta(days=1)})
    )
    _deliver(c, "vehicle.assigned", other)
    assert wo.spine_conflict_assignment_ids == booking and not other.activity_ids
