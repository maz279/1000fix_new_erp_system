"""M02 extension tests: journey stamps + travel/on-time computation, the
dispatch suggestion engine (roster / certification / zone / load), and the
service-order → field-order bridge.

``odoo_env`` (addons/conftest.py): superuser environment on fix_test, rolled
back after every test. Expected values are computed by hand in the comments.
"""

from datetime import date, timedelta

import pytest
from odoo import fields
from odoo.exceptions import UserError


@pytest.fixture
def fx(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].create(
        {"code": "FXEXT", "legal_name": "Field Ext Entity", "company_id": env.company.id}
    )
    branch = env["fix.branch"].create(
        {
            "name": "FX Ext Branch",
            "code": "FXEB",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    zone = env["fix.zone"].create({"name": "FX Zone", "code": "FXZ"})
    branch.write({"zone_id": zone.id})
    brand = env["fix.brand"].create({"name": "FxExtBrand", "code": "FXEB"})
    device_model = env["fix.device.model"].create({"name": "FxExt Phone", "brand_id": brand.id})
    customer = env["res.partner"].create({"name": "FX Customer", "phone": "01711000702"})
    device = env["fix.device"].create(
        {"device_model_id": device_model.id, "owner_id": customer.id, "serial_number": "SN-FXE-1"}
    )
    order = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "fault_description": "Onsite screen replacement",
            "service_type": "onsite",
        }
    )
    tech = env["hr.employee"].create({"name": "FX Technician"})
    return type(
        "FX", (), {"env": env, "branch": branch, "zone": zone, "order": order, "tech": tech}
    )()


def _shift(env):
    """A shift template for roster slots (fix_test ships none)."""
    shift = env["fix.shift.template"].search([], limit=1)
    if not shift:
        shift = env["fix.shift.template"].create(
            {"name": "FX Day Shift", "start_hour": 9.0, "end_hour": 18.0}
        )
    return shift


def _certify(env, employee):
    """Give an employee an ACTIVE certification in a dispatch-gating
    competency — the M22 work-order gate (FR-LMS-039) refuses technicians
    without one, so every technician referenced by a work order needs it."""
    Competency = env["fix.competency"]
    comp = Competency.search([("required_for_dispatch", "=", True)], limit=1)
    if not comp:
        comp = Competency.create(
            {"name": "FX Gating Competency", "code": "FXG", "required_for_dispatch": True}
        )
    existing = env["fix.certification"].search(
        [("employee_id", "=", employee.id), ("competency_id", "=", comp.id)], limit=1
    )
    if existing:
        return existing
    return env["fix.certification"].create(
        {
            "employee_id": employee.id,
            "competency_id": comp.id,
            "issued_on": date.today() - timedelta(days=30),
            "expires_on": date.today() + timedelta(days=365),
        }
    )


def _field_order(fx, **vals):
    return fx.env["fix.field.order"].create(
        {
            "order_id": fx.order.id,
            "zone_id": fx.zone.id,
            "operating_unit_id": fx.order.operating_unit_id.id or fx.branch.operating_unit_id.id,
            **vals,
        }
    )


# --- journey stamps ------------------------------------------------------


def test_journey_stamps_and_actual_travel_minutes(fx):
    fo = _field_order(fx, scheduled_start=fields.Datetime.now() + timedelta(hours=2))
    fo.action_request_dispatch()
    fo.action_dispatch(technician_id=fx.tech.id)
    assert fo.dispatched_at
    fo.action_accept()
    assert fo.accepted_at
    fo.action_start_travel()
    assert fo.en_route_at
    fo.action_arrive()
    assert fo.arrived_at
    # same-transaction travel: ~0 minutes, rounded — the FIELD is now written
    assert fo.actual_travel_minutes is not None and fo.actual_travel_minutes >= 0.0
    assert fo.on_time_arrival is True  # arrival before the +2h scheduled start
    fo.action_start_work()
    assert fo.started_work_at
    fo.action_complete()
    assert fo.completed_at


def test_late_arrival_flags_on_time_false(fx):
    fo = _field_order(fx, scheduled_start=fields.Datetime.now() - timedelta(hours=1))
    fo.action_request_dispatch()
    fo.action_dispatch(technician_id=fx.tech.id)
    fo.action_accept()
    fo.action_start_travel()
    fo.action_arrive()
    assert fo.on_time_arrival is False  # scheduled start already passed


# --- suggestion engine ----------------------------------------------------


def test_suggestions_rank_rostered_certified_zone_technician_first(fx):
    env = fx.env
    # a technician with everything: rostered today in the order's zone branch,
    # plus an active certification in a dispatch-gating competency
    star = env["hr.employee"].create({"name": "FX Star Tech"})
    idle = env["hr.employee"].create({"name": "FX Idle Tech"})
    _certify(env, star)
    _certify(env, idle)  # both ride work orders as technician references
    env["fix.roster.slot"].create(
        {
            "employee_id": star.id,
            "date": date.today(),
            "shift_id": _shift(env).id,
            "branch_id": fx.branch.id,  # branch carries the order's zone
        }
    )
    # reference both as technicians so they are candidates (work order name
    # is computed — never passed explicitly)
    env["fix.work.order"].create({"order_id": fx.order.id, "technician_id": star.id})
    env["fix.work.order"].create({"order_id": fx.order.id, "technician_id": idle.id})

    fo = _field_order(fx)
    suggestions = fo.action_suggest_technicians()
    assert suggestions, "expected at least the two referenced technicians"
    names = [s["name"] for s in suggestions]
    assert "FX Star Tech" in names and "FX Idle Tech" in names
    # star: roster(+30) + home zone(+20) [+25 if a gating competency exists]
    # idle: 0 unless certifiable — star must outrank idle in every case
    star_s = next(s for s in suggestions if s["name"] == "FX Star Tech")
    idle_s = next(s for s in suggestions if s["name"] == "FX Idle Tech")
    assert star_s["score"] > idle_s["score"]
    assert star_s["rostered"] is True and star_s["zone_match"] is True
    assert idle_s["rostered"] is False


def test_suggestions_penalise_active_load(fx):
    env = fx.env
    busy = env["hr.employee"].create({"name": "FX Busy Tech"})
    _certify(env, busy)
    _certify(env, fx.tech)
    env["fix.work.order"].create({"order_id": fx.order.id, "technician_id": busy.id})
    env["fix.work.order"].create({"order_id": fx.order.id, "technician_id": fx.tech.id})
    # busy carries two active field orders; fx.tech carries none
    for _i in (1, 2):
        fo = _field_order(fx)
        fo.action_request_dispatch()
        fo.action_dispatch(technician_id=busy.id)
    new = _field_order(fx)
    suggestions = new.action_suggest_technicians()
    busy_s = next(s for s in suggestions if s["name"] == "FX Busy Tech")
    tech_s = next(s for s in suggestions if s["name"] == "FX Technician")
    assert busy_s["open_jobs"] == 2
    # both certified (+25); the load penalty (-5/job) must rank the loaded
    # technician BELOW the unloaded one
    assert tech_s["score"] > busy_s["score"]
    assert tech_s["open_jobs"] == 0


# --- service order bridge -------------------------------------------------


def test_bridge_creates_draft_field_order_from_onsite(fx):
    created = fx.order.action_create_field_order()
    assert len(created) == 1
    fo = created[0]
    assert fo.state == "draft"
    assert fo.zone_id == fx.branch.zone_id
    assert fo.order_id == fx.order
    assert fx.order.field_order_count == 1
    # idempotent per order is NOT enforced (multiple visits are legal), but a
    # second creation must still link the same service order
    second = fx.order.action_create_field_order()
    assert second[0].order_id == fx.order
    assert fx.order.field_order_count == 2


def test_bridge_refuses_non_onsite(fx):
    fx.order.service_type = "walk_in"
    with pytest.raises(UserError, match="on-site"):
        fx.order.action_create_field_order()


def test_bridge_refuses_closed(fx):
    fx.order.state = "intake"
    fx.order.state = "diagnostic"
    fx.order.state = "estimate_pending"
    fx.order.state = "estimate_sent"
    fx.order.state = "awaiting_approval"
    fx.order.state = "approved"
    fx.order.state = "in_repair"
    fx.order.state = "qc_pending"
    env = fx.env
    env["fix.qc.checklist"].create({"order_id": fx.order.id, "state": "passed"})
    fx.order.state = "ready"
    fx.order.state = "delivered"
    fx.order.state = "closed"
    with pytest.raises(UserError, match="can no longer be dispatched"):
        fx.order.action_create_field_order()
