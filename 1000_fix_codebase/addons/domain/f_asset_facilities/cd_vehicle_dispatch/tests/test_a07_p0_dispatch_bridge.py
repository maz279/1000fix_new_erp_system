"""A07 audit P0 (E3), M46-1: M02 dispatch is gated by M46.

The audit found fix.field.order had no vehicle and action_dispatch never
consulted M46: an M02 dispatcher sent out an uninsured or unfit van, and
nothing ever created a fix.vehicle.assignment. cd_vehicle_dispatch bridges
the two. Tested as NON-ADMIN users created here (dispatcher, technicians);
``odoo_env`` rolls back after every test.
"""

import types
from datetime import timedelta

import pytest
from odoo.addons.cd_vehicle_dispatch.models.fix_field_order_vehicle import REQUIRE_VEHICLE_PARAM
from odoo.addons.cd_vehicle_ext.models.fix_vehicle_ops import dhaka_today
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)


def refused(env, fn):
    try:
        with env.cr.savepoint():
            fn()
            env.flush_all()
    except REFUSED as exc:
        return str(exc)
    return None


@pytest.fixture
def w(odoo_env):
    env = odoo_env
    # The bridge ships uninstalled (a new dependency in cd_vehicle_ext would
    # break an un-upgraded server on plain restart); `-u all` leaves it out.
    if "vehicle_assignment_id" not in env["fix.field.order"]._fields:
        pytest.skip("cd_vehicle_dispatch not installed")
    ou = env["operating.unit"].search([], limit=1)
    co = env.company
    x = types.SimpleNamespace(env=env, ou=ou)
    x.today = dhaka_today(env["fix.vehicle.check"])
    entity = env["fix.entity"].create(
        {"code": "A7P0D", "legal_name": "A07 P0 dispatch entity", "company_id": co.id}
    )
    zone = env["fix.zone"].create({"name": "A07P0 Zone", "code": "A7PZ"})
    branch = env["fix.branch"].create(
        {
            "name": "A07P0 Branch",
            "code": "A7P0D",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
            "zone_id": zone.id,
        }
    )
    brand = env["fix.brand"].create({"name": "A7P0Brand", "code": "A7PB"})
    dmodel = env["fix.device.model"].create({"name": "A7P0 Phone", "brand_id": brand.id})
    customer = env["res.partner"].create({"name": "A07P0 Customer", "phone": "01711000997"})
    device = env["fix.device"].create(
        {"device_model_id": dmodel.id, "owner_id": customer.id, "serial_number": "SN-A7P0-1"}
    )
    order = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "fault_description": "onsite A07 P0",
            "service_type": "onsite",
        }
    )

    def mk(login, groups):
        user = (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": login,
                    "login": login,
                    "group_ids": [(6, 0, [env.ref("base.group_user").id] + [g.id for g in groups])],
                    "company_id": co.id,
                    "company_ids": [(6, 0, [co.id])],
                    "operating_unit_ids": [(6, 0, ou.ids)],
                    "default_operating_unit_id": ou.id,
                }
            )
        )
        return user, env["hr.employee"].create({"name": login, "user_id": user.id})

    g_tech = env.ref("cd_field_service.group_fix_field_service_user")
    x.ua, x.ea = mk("a07p0d_tech_a", [g_tech])
    x.ub, x.eb = mk("a07p0d_tech_b", [g_tech])
    x.ud, x.ed = mk("a07p0d_disp", [env.ref("cd_field_service.group_fix_field_service_manager")])

    brand_v = env["fleet.vehicle.model.brand"].create({"name": "A07P0D Brand"})
    vmodel = env["fleet.vehicle.model"].create({"name": "A07P0D Van", "brand_id": brand_v.id})

    def vehicle(plate, docs=("fitness", "insurance", "tax")):
        v = env["fleet.vehicle"].create({"model_id": vmodel.id, "license_plate": plate})
        for doc_type in docs:
            env["fix.vehicle.document"].create(
                {
                    "vehicle_id": v.id,
                    "doc_type": doc_type,
                    "valid_to": x.today + timedelta(days=200),
                }
            )
        return v

    def fo(**kw):
        rec = env["fix.field.order"].create(
            {"order_id": order.id, "zone_id": zone.id, "operating_unit_id": ou.id, **kw}
        )
        rec.write({"state": "pending_dispatch"})  # setup: the superuser places it
        return rec

    x.vehicle, x.fo = vehicle, fo
    x.good = vehicle("A07P0D-GOOD")
    x.bad = vehicle("A07P0D-UNINSURED", docs=("fitness", "tax"))
    emp = env["hr.employee"].create({"name": "A07P0D Driver"})
    x.driver = env["fix.driver"].create(
        {
            "name": "A07P0D Driver",
            "employee_id": emp.id,
            "license_no": "DL-A7P0D",
            "license_expiry": x.today + timedelta(days=300),
        }
    )
    return x


def dispatch(w, rec, emp, user=None):
    rec.with_user(user or w.ud).action_dispatch(technician_id=emp.id)


def test_dispatch_books_the_days_assignment(w):
    rec = w.fo(vehicle_id=w.good.id, vehicle_driver_id=w.driver.id)
    dispatch(w, rec, w.ea)
    a = rec.vehicle_assignment_id
    assert rec.state == "dispatched"
    assert (a.vehicle_id, a.date, a.driver_id, a.technician_id) == (
        w.good,
        w.today,
        w.driver,
        w.ea,
    )
    assert a.field_order_ids == rec and a.dispatch_created


def test_uninsured_van_is_not_dispatched(w):
    rec = w.fo(vehicle_id=w.bad.id)
    msg = refused(w.env, lambda: dispatch(w, rec, w.ea))
    assert "not dispatchable" in msg and "Insurance" in msg
    assert rec.state == "pending_dispatch" and not rec.vehicle_assignment_id
    assert not w.env["fix.vehicle.assignment"].search([("vehicle_id", "=", w.bad.id)])


def test_offroad_van_and_expired_driver_are_not_dispatched(w):
    w.env["fix.vehicle.offroad"].create({"vehicle_id": w.good.id, "reason": "Clutch"})
    assert "off-road" in refused(w.env, lambda: dispatch(w, w.fo(vehicle_id=w.good.id), w.ea))
    van = w.vehicle("A07P0D-DRV")
    w.driver.license_expiry = w.today - timedelta(days=1)
    rec = w.fo(vehicle_id=van.id, vehicle_driver_id=w.driver.id)
    assert "licence expired" in refused(w.env, lambda: dispatch(w, rec, w.ea))


def test_vehicle_requirement_is_a_switch(w):
    rec = w.fo()
    dispatch(w, rec, w.ea)  # default off: a job without a van still dispatches
    assert rec.state == "dispatched" and not rec.vehicle_assignment_id
    w.env["ir.config_parameter"].sudo().set_param(REQUIRE_VEHICLE_PARAM, "True")
    assert "Name the vehicle" in refused(w.env, lambda: dispatch(w, w.fo(), w.ea))
    rec2 = w.fo(vehicle_id=w.good.id)
    dispatch(w, rec2, w.ea)
    assert rec2.vehicle_assignment_id


def test_one_van_one_crew_per_day(w):
    first = w.fo(vehicle_id=w.good.id)
    dispatch(w, first, w.ea)
    second = w.fo(vehicle_id=w.good.id)
    dispatch(w, second, w.ea)  # same technician: the day's assignment is shared
    assert second.vehicle_assignment_id == first.vehicle_assignment_id
    assert len(first.vehicle_assignment_id.field_order_ids) == 2
    third = w.fo(vehicle_id=w.good.id)
    assert "cannot be in two places" in refused(w.env, lambda: dispatch(w, third, w.eb))


def test_changing_the_van_after_dispatch_is_gated(w):
    rec = w.fo(vehicle_id=w.good.id)
    dispatch(w, rec, w.ea)
    # the technician (or anyone) re-points the live order to the uninsured van
    assert refused(w.env, lambda: rec.with_user(w.ua).write({"vehicle_id": w.bad.id}))
    # an unforgeable token: a context key from RPC does not skip the gate
    assert refused(
        w.env,
        lambda: rec.with_user(w.ua)
        .with_context(fix_vehicle_sync_deferred=True)
        .write({"vehicle_id": w.bad.id}),
    )
    other = w.vehicle("A07P0D-OTHER")
    rec.with_user(w.ud).write({"vehicle_id": other.id})
    assert rec.vehicle_assignment_id.vehicle_id == other
    assert not w.env["fix.vehicle.assignment"].search([("vehicle_id", "=", w.good.id)])


def test_assignment_link_cannot_be_typed(w):
    rec = w.fo(vehicle_id=w.good.id)
    dispatch(w, rec, w.ea)
    stray = w.env["fix.vehicle.assignment"].create(
        {"vehicle_id": w.vehicle("A07P0D-STRAY").id, "date": w.today}
    )
    assert refused(w.env, lambda: rec.with_user(w.ud).write({"vehicle_assignment_id": stray.id}))


def test_decline_frees_the_van(w):
    rec = w.fo(vehicle_id=w.good.id)
    dispatch(w, rec, w.ea)
    rec.with_user(w.ua).action_decline(reason="other", notes="sick")
    assert not rec.vehicle_assignment_id
    assert not w.env["fix.vehicle.assignment"].search([("vehicle_id", "=", w.good.id)])
    # another technician can now take the van that day
    dispatch(w, w.fo(vehicle_id=w.good.id), w.eb)


def test_non_dispatcher_still_cannot_dispatch(w):
    rec = w.fo(vehicle_id=w.good.id)
    assert refused(w.env, lambda: dispatch(w, rec, w.ea, user=w.ua))
    assert not rec.vehicle_assignment_id
