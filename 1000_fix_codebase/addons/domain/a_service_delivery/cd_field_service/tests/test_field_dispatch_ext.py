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


def _certify(env, employee, device_type="smartphone"):
    """Give an employee an ACTIVE certification in a dispatch-gating
    competency scoped to the job's device type — the M22 gate (FR-LMS-039,
    A09 C4) refuses technicians without one and fails closed for a device type
    no gating competency covers. The fixture's device model is a smartphone."""
    Competency = env["fix.competency"]
    comp = Competency.search([("required_for_dispatch", "=", True)]).filtered(
        lambda c: device_type in (c.device_type or "").replace(" ", "").split(",")
    )[:1]
    if not comp:
        comp = Competency.create(
            {
                "name": "FX Gating Competency",
                "code": "FXG",
                "device_type": device_type,
                "required_for_dispatch": True,
            }
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


PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVR4nGNgAAIAAAUAAXpeqz8AAAAASUVORK5CYII="
)


def _give_completion_evidence(fo):
    """A02 audit M02-2: completion needs the customer's signature, a post-work
    photo and a work summary (the order must be in progress)."""
    import base64

    Att = fo.env["ir.attachment"]
    for media in ("signature", "photo"):
        att = Att.create(
            {
                "name": "%s.png" % media,
                "raw": base64.b64decode(PNG_B64),
                "mimetype": "image/png",
                "res_model": "fix.field.order",
                "res_id": fo.id,
            }
        )
        fo._fix_attach_field_evidence(att, media, signer="Test Customer")
    fo.work_summary = "Replaced the faulty part and tested."


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
    _certify(fx.env, fx.tech)  # A09 C4: dispatch needs a device-scoped certification
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
    _give_completion_evidence(fo)
    fo.action_complete()
    assert fo.completed_at


def test_late_arrival_flags_on_time_false(fx):
    _certify(fx.env, fx.tech)  # A09 C4: dispatch needs a device-scoped certification
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
    # multiple visits are legal, one at a time: A02 audit M01-13 refuses a
    # second LIVE field order, so the first visit ends before the next
    with pytest.raises(UserError, match="already has a live field order"):
        fx.order.action_create_field_order()
    fo.action_cancel(reason="revisit booked")
    second = fx.order.action_create_field_order()
    assert second[0].order_id == fx.order
    assert fx.order.field_order_count == 2


def test_bridge_refuses_non_onsite(fx):
    fx.order.service_type = "walk_in"
    with pytest.raises(UserError, match="on-site"):
        fx.order.action_create_field_order()


def test_bridge_refuses_closed(fx):
    # placed in its state directly: what this test checks is the bridge's
    # refusal, not the M01 path to closed (whose gates change independently)
    fx.env.flush_all()
    fx.env.cr.execute("UPDATE fix_service_order SET state = 'closed' WHERE id = %s", [fx.order.id])
    fx.env.invalidate_all()
    with pytest.raises(UserError, match="can no longer be dispatched"):
        fx.order.action_create_field_order()


def test_a_suggestion_says_what_the_gate_will_say_about_the_brand(fx):
    """On live data the board marked technicians certified, then dispatch refused all 21 tried:
    the board asked about the device type, the gate about the brand as well."""
    env = fx.env
    wrong_brand = env["hr.employee"].create({"name": "FX Other Brand Tech"})
    right_brand = env["hr.employee"].create({"name": "FX Same Brand Tech"})
    other = env["fix.brand"].create({"name": "FxOtherBrand", "code": "FXOB"})
    _certify(env, wrong_brand).write({"brand_id": other.id})
    _certify(env, right_brand).write({"brand_id": fx.order.device_id.device_model_id.brand_id.id})
    # the gate rightly refuses the wrong brand on a work order: the roster makes them candidates
    for tech in (wrong_brand, right_brand):
        env["fix.roster.slot"].create(
            {
                "employee_id": tech.id,
                "date": date.today(),
                "shift_id": _shift(env).id,
                "branch_id": fx.branch.id,
            }
        )

    fo = _field_order(fx)
    suggestions = {s["name"]: s for s in fo.action_suggest_technicians(limit=50)}
    assert fo._fix_certification_problem(wrong_brand)
    assert not fo._fix_certification_problem(right_brand)
    assert "certified" in suggestions["FX Same Brand Tech"]["reasons"]
    wrong = suggestions["FX Other Brand Tech"]["reasons"]
    assert "certified" not in wrong and any(r.startswith("cert:") for r in wrong)
