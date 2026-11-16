"""M46 capture audit (2026-11-17): the registers the sub-module pages could not
capture, attacked as NON-ADMIN users holding the role they would really hold.
Each refusal is paired with the proper path. ``odoo_env`` rolls back.

- document renewal (FR-FLT-013/014, §13 SoD on a lapse penalty);
- defect, safety-critical or deferrable (FR-FLT-025, BRU-FLT-04);
- service execution and the next service (FR-FLT-026/027);
- telematics device register (FR-FLT-035/036);
- traffic fine with a recover-or-absorb decision (FR-FLT-043, BRU-FLT-16);
- ownership basis, and M49 capitalising only an owned vehicle (FR-FLT-003).
"""

import base64
import types
from datetime import timedelta

import pytest
from odoo.addons.cd_p03_portal.controllers.a07 import m46 as m46_surface
from odoo.addons.cd_vehicle_ext.models.fix_vehicle_ops import dhaka_today
from odoo.exceptions import AccessError, UserError, ValidationError
from psycopg2 import Error as PgError

REFUSED = (UserError, ValidationError, AccessError, PgError)
OFFICER = "fleet.fleet_group_user"
LM = "cd_vehicle_ext.group_logistics_manager"
SCAN = base64.b64encode(b"%PDF-1.4 scanned certificate").decode()


def refused(env, fn):
    try:
        with env.cr.savepoint():
            fn()
            env.flush_all()
    except REFUSED as exc:
        return str(exc) or exc.__class__.__name__
    return None


@pytest.fixture
def f(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([], limit=1)

    def user(login, groups=()):
        u = (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": login,
                    "login": login,
                    "group_ids": [
                        (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                    ],
                    "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                    "default_operating_unit_id": ou.id,
                }
            )
        )
        return u

    x = types.SimpleNamespace(env=env)
    x.today = dhaka_today(env["fix.vehicle.check"])
    x.clerk = user("m46cap_clerk")
    x.officer, x.officer2 = user("m46cap_off", [OFFICER]), user("m46cap_off2", [OFFICER])
    x.lm, x.lm2 = user("m46cap_lm", [LM]), user("m46cap_lm2", [LM])
    brand = env["fleet.vehicle.model.brand"].create({"name": "M46CAP Brand"})
    x.model = env["fleet.vehicle.model"].create(
        {"name": "M46CAP Van", "brand_id": brand.id, "vehicle_type": "car"}
    )
    x.garage = env["res.partner"].create({"name": "M46CAP Garage", "is_company": True})

    def doc(v, doc_type, valid_to, user=None, scan=True):
        vals = {
            "vehicle_id": v.id,
            "doc_type": doc_type,
            "number": "N-%s-%s" % (doc_type, valid_to),
        }
        vals["valid_to"] = valid_to
        if scan:
            vals["evidence_file"] = SCAN
        return env["fix.vehicle.document"].with_user(user or x.officer).create(vals)

    def vehicle(plate, **kw):
        v = env["fleet.vehicle"].create({"model_id": x.model.id, "license_plate": plate, **kw})
        for doc_type in ("fitness", "insurance", "tax"):
            doc(v, doc_type, x.today + timedelta(days=200))
        return v

    def driver(name, **kw):
        emp = env["hr.employee"].create({"name": name})
        vals = {
            "name": name,
            "employee_id": emp.id,
            "license_no": "DL-" + name,
            "license_class": "Light",
            "license_expiry": x.today + timedelta(days=400),
            **kw,
        }
        return env["fix.driver"].with_user(x.officer).create(vals)

    def check(v, user=None, ok=True):
        vals = {"vehicle_id": v.id}
        vals.update({k: ok for k in ("tyres_ok", "lights_ok", "fluids_ok", "brakes_ok")})
        return env["fix.vehicle.check"].with_user(user or x.officer2).create(vals)

    x.doc, x.vehicle, x.driver, x.check = doc, vehicle, driver, check
    x.van = vehicle("M46CAP-11-0001")
    # the person responsible for renewals is the first officer
    x.runner = env["hr.employee"].create({"name": "M46CAP Runner", "user_id": x.officer.id})
    return x


# ------------------------------------------------------------------ renewal
def _renewal(f, user=None, **kw):
    fitness = f.van.document_ids.filtered(lambda d: d.doc_type == "fitness")[:1]
    vals = {"document_id": fitness.id, "responsible_employee_id": f.runner.id, **kw}
    return f.env["fix.vehicle.document.renewal"].with_user(user or f.officer).create(vals)


def test_a_renewal_completes_only_on_the_new_scanned_certificate(f):
    assert refused(f.env, lambda: _renewal(f, user=f.clerk)), "a plain employee opened a renewal"
    ren = _renewal(f, government_fee=1200.0, agent_fee=300.0)
    assert ren.vehicle_id == f.van and ren.doc_type == "fitness" and ren.total_cost == 1500.0
    assert "already has a renewal" in refused(f.env, lambda: _renewal(f))
    assert refused(f.env, lambda: ren.action_complete()), "completed before submission"
    ren.action_submit()
    assert ren.state == "submitted" and ren.submitted_on == f.today
    assert "Renewed Document" in refused(f.env, lambda: ren.action_complete())
    # the wrong type, then a new one with no scan, are refused
    tax = f.van.document_ids.filtered(lambda d: d.doc_type == "tax")[:1]
    ren.write({"new_document_id": tax.id})
    assert "must be a new fitness" in refused(f.env, lambda: ren.action_complete())
    unscanned = f.doc(f.van, "fitness", f.today + timedelta(days=500), scan=False)
    ren.write({"new_document_id": unscanned.id})
    assert "no evidence scan" in refused(f.env, lambda: ren.action_complete())
    new = f.doc(f.van, "fitness", f.today + timedelta(days=565))
    ren.write({"new_document_id": new.id})
    ren.action_complete()
    assert ren.state == "completed" and ren.completed_by_id == f.officer
    # a completed renewal is history: its fees are frozen, it is never deleted
    assert refused(f.env, lambda: ren.write({"agent_fee": 0.0}))
    assert refused(f.env, lambda: ren.unlink())


def test_a_lapse_penalty_needs_its_reason_and_a_second_officer(f):
    ren = _renewal(f, government_fee=1200.0, penalty=500.0)
    ren.action_submit()
    ren.write({"new_document_id": f.doc(f.van, "fitness", f.today + timedelta(days=565)).id})
    assert "why a late penalty" in refused(f.env, lambda: ren.action_complete()).lower()
    ren.write({"penalty_reason": "renewed 9 days late"})
    # the responsible person (the officer's employee) may not approve the penalty
    assert "Segregation of duties" in refused(f.env, lambda: ren.action_complete())
    ren.with_user(f.officer2).action_complete()
    assert ren.state == "completed" and ren.completed_by_id == f.officer2


def test_renewal_fees_are_running_cost(f):
    ren = _renewal(f, government_fee=1200.0, agent_fee=300.0)
    ren.action_submit()
    ren.write({"new_document_id": f.doc(f.van, "fitness", f.today + timedelta(days=565)).id})
    ren.action_complete()
    row = next(r for r in m46_surface.cost_per_km(f.env)["rows"] if r["plate"] == "M46CAP-11-0001")
    assert row["document_cost"] == 1500.0 and row["total_cost"] == 1500.0


# ------------------------------------------------------------------ defect
def test_a_deferrable_defect_leaves_the_vehicle_on_the_road(f):
    Defect = f.env["fix.vehicle.defect"].with_user(f.clerk)
    d = Defect.create({"vehicle_id": f.van.id, "category": "body", "description": "mirror cracked"})
    assert d.raised_by_id == f.clerk and not d.offroad_id
    assert not f.van._fix_dispatch_blockers().get(f.van.id)
    assert "Fleet Officer" in refused(f.env, lambda: d.with_user(f.clerk).action_clear("fixed"))
    d.with_user(f.officer).action_clear("mirror replaced")
    assert d.state == "cleared" and d.cleared_by_id == f.officer
    # the officer who reports a defect does not clear it
    own = (
        f.env["fix.vehicle.defect"]
        .with_user(f.officer)
        .create({"vehicle_id": f.van.id, "category": "lights", "description": "indicator slow"})
    )
    assert "Segregation" in refused(f.env, lambda: own.with_user(f.officer).action_clear("ok"))
    own.with_user(f.officer2).action_clear("bulb replaced")


def test_a_safety_critical_defect_stops_the_vehicle_until_rechecked(f):
    d = (
        f.env["fix.vehicle.defect"]
        .with_user(f.clerk)
        .create(
            {
                "vehicle_id": f.van.id,
                "category": "brakes",
                "safety_critical": True,
                "description": "brakes pull left",
            }
        )
    )
    assert d.offroad_id and d.offroad_id.cause == "defect" and d.offroad_id.state == "offroad"
    assert any("off-road" in b for b in f.van._fix_dispatch_blockers()[f.van.id])
    # never downgraded to put the vehicle back on the road
    assert refused(f.env, lambda: d.with_user(f.clerk).write({"safety_critical": False}))
    assert "passed pre-use check" in refused(
        f.env, lambda: d.with_user(f.officer).action_clear("pads replaced")
    )
    f.check(f.van)
    d.with_user(f.officer).action_clear("pads replaced")
    assert d.state == "cleared" and d.clear_check_id


# ------------------------------------------------------------------ service
def test_a_garage_service_names_its_invoice_and_opens_the_next(f):
    pm = (
        f.env["fix.vehicle.pm"]
        .with_user(f.clerk)
        .create(
            {
                "vehicle_id": f.van.id,
                "odometer": 12000,
                "cost": 3500.0,
                "provider_id": f.garage.id,
                "work_performed": "oil and filter",
                "next_due_odometer": 17000,
                "next_due_date": f.today + timedelta(days=90),
            }
        )
    )
    assert "invoice reference" in refused(f.env, lambda: pm.with_user(f.officer).action_done())
    pm.write({"invoice_ref": "GAR-881"})
    pm.with_user(f.officer).action_done()
    nxt = pm.next_pm_id
    assert nxt and nxt.state == "open" and nxt.due_odometer == 17000
    assert nxt.due_date == f.today + timedelta(days=90)
    assert refused(f.env, lambda: pm.with_user(f.officer).write({"invoice_ref": "X"}))
    assert refused(f.env, lambda: pm.with_user(f.clerk).write({"next_due_odometer": 11000}))


# ------------------------------------------------------------------ telematics
def test_the_device_register_holds_one_device_per_vehicle(f):
    Device = f.env["fix.telematics.device"]
    assert refused(f.env, lambda: Device.with_user(f.clerk).create({"name": "IMEI-1"}))
    dev = Device.with_user(f.officer).create(
        {"name": " IMEI-1 ", "sim_number": "01700000000", "vehicle_id": f.van.id}
    )
    assert dev.name == "IMEI-1" and dev.state == "fitted" and dev.fitted_on
    assert dev.health_state == "offline"
    assert "already registered" in refused(
        f.env, lambda: Device.with_user(f.officer).create({"name": "imei-1"})
    )
    assert "already carries" in refused(
        f.env,
        lambda: Device.with_user(f.officer).create({"name": "IMEI-2", "vehicle_id": f.van.id}),
    )
    other = f.vehicle("M46CAP-11-0002")
    assert refused(f.env, lambda: dev.with_user(f.officer).write({"vehicle_id": other.id}))
    assert "removing the device" in refused(f.env, lambda: dev.with_user(f.officer).action_remove())
    dev.with_user(f.officer).action_remove("moved to another van")
    assert dev.state == "stock" and dev.removed_on == f.today
    # a device in stock has no vehicle: the record rules still show it
    assert f.env["fix.telematics.device"].with_user(f.clerk).search([("id", "=", dev.id)])
    dev.with_user(f.officer).write({"vehicle_id": other.id})
    assert dev.vehicle_id == other and dev.state == "fitted"


def test_a_snapshot_belongs_to_the_fitted_device(f):
    dev = (
        f.env["fix.telematics.device"]
        .with_user(f.officer)
        .create({"name": "IMEI-9", "vehicle_id": f.van.id})
    )
    Tel = f.env["fix.vehicle.telemetry"].with_user(f.officer)
    snap = Tel.create({"vehicle_id": f.van.id, "last_ping": f.env.cr.now()})
    assert snap.device_id == dev and snap.device_ref == "IMEI-9"
    assert dev.health_state == "online" and dev.last_report_at
    assert "not in the device register" in refused(
        f.env, lambda: Tel.create({"vehicle_id": f.van.id, "device_ref": "GHOST-1"})
    )


# ------------------------------------------------------------------ penalty
def test_a_fine_is_the_driver_on_duty_and_decided_by_another_manager(f):
    drv = f.driver("M46CAP Driver")
    Pen = f.env["fix.vehicle.penalty"]
    vals = {"vehicle_id": f.van.id, "offence": "wrong-way driving", "amount": 2000.0}
    assert refused(f.env, lambda: Pen.with_user(f.clerk).create(vals)), "a clerk recorded a fine"
    assert "driver on duty" in refused(f.env, lambda: Pen.with_user(f.lm).create(vals))
    f.env["fix.vehicle.assignment"].with_user(f.officer).create(
        {"vehicle_id": f.van.id, "date": f.today, "driver_id": drv.id}
    )
    pen = Pen.with_user(f.lm).create(vals)
    assert pen.driver_id == drv and pen.recorded_by_id == f.lm
    assert refused(f.env, lambda: Pen.with_user(f.lm).create({**vals, "amount": 0.0}))
    assert "Segregation" in refused(f.env, lambda: pen.with_user(f.lm).action_recover("x"))
    assert refused(f.env, lambda: pen.with_user(f.officer).action_absorb("x")), "officer decided"
    pen.with_user(f.lm2).action_absorb("signal fault confirmed by police")
    assert pen.state == "decided" and pen.recovery_decision == "absorb"
    assert refused(f.env, lambda: pen.with_user(f.lm2).write({"amount": 1.0}))


# ------------------------------------------------------------------ ownership
def test_only_an_owned_vehicle_is_capitalised(f):
    V = f.env["fleet.vehicle"]
    assert "names its contract" in refused(
        f.env,
        lambda: V.with_user(f.lm).create(
            {"model_id": f.model.id, "license_plate": "M46CAP-L1", "fix_ownership_basis": "leased"}
        ),
    )
    assert refused(
        f.env,
        lambda: V.with_user(f.officer).create(
            {
                "model_id": f.model.id,
                "license_plate": "M46CAP-L2",
                "fix_ownership_basis": "leased",
                "fix_contract_ref": "LEASE-1",
                "fix_contract_end": f.today + timedelta(days=700),
            }
        ),
    ), "a Fleet Officer registered a leased vehicle"
    leased = V.with_user(f.lm).create(
        {
            "model_id": f.model.id,
            "license_plate": "M46CAP-L3",
            "fix_ownership_basis": "leased",
            "fix_contract_ref": "LEASE-1",
            "fix_contract_end": f.today + timedelta(days=700),
            "net_car_value": 2500000.0,
        }
    )
    owned = V.with_user(f.lm).create(
        {"model_id": f.model.id, "license_plate": "M46CAP-O1", "net_car_value": 2500000.0}
    )
    Req = f.env["fix.asset.finance.request"].sudo()

    def caps(v):
        return Req.search(
            [
                ("source_model", "=", "fleet.vehicle"),
                ("source_res_id", "=", v.id),
                ("kind", "=", "capitalise"),
            ]
        )

    assert not caps(leased), "a leased vehicle was capitalised"
    assert len(caps(owned)) == 1
    # bought out at the end of the lease: it becomes the company's asset
    assert refused(
        f.env, lambda: leased.with_user(f.officer).write({"fix_ownership_basis": "owned"})
    )
    leased.with_user(f.lm).write({"fix_ownership_basis": "owned"})
    assert len(caps(leased)) == 1
