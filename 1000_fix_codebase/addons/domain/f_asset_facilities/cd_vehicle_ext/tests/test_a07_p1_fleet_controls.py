"""A07 P1/P2 (M46 Fleet & Vehicles): roles, scheduler, isolation and lifecycle
depth, attacked as NON-ADMIN users holding the role they would really hold
(and without it, where the role is the control). ``odoo_env`` rolls back.

Audit: working/A07_evidence/module_findings/M46.md and the still-failing
probes of probe_m46_docfixture.py (06/07, 10, 16, 17, 21, 23, 24, 29, 36,
38-40, 45, 49, 51, 56, 60, 61). Each refusal is paired with the proper path.

Users:
- ``clerk`` / ``clerk2``: any employee (driver, technician): base.group_user;
- ``officer`` / ``officer2``: Fleet Officer = fleet.fleet_group_user;
- ``lm`` / ``lm2``: Logistics Manager (cd_vehicle_ext.group_logistics_manager).
"""

import base64
import json
import types
from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_vehicle_ext.models.fix_vehicle import MANDATORY_DOCS_PARAM
from odoo.addons.cd_vehicle_ext.models.fix_vehicle_ops import (
    LEGACY_EVIDENCE_PARAM,
    LICENCE_CLASS_PARAM,
    PM_OFFROAD_PARAM,
    TELEMATICS_SILENCE_PARAM,
    dhaka_today,
)
from odoo.exceptions import AccessError, UserError, ValidationError
from psycopg2 import Error as PgError

REFUSED = (UserError, ValidationError, AccessError, PgError)
OFFICER = "fleet.fleet_group_user"
LM = "cd_vehicle_ext.group_logistics_manager"
SCAN = base64.b64encode(b"%PDF-1.4 scanned certificate").decode()


def refused(env, fn):
    """The refusal text, or None when fn() went through (rolled back to a
    savepoint either way)."""
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
        return (
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

    x = types.SimpleNamespace(env=env, ou=ou)
    x.today = dhaka_today(env["fix.vehicle.check"])
    x.clerk, x.clerk2 = user("a7p1f_clerk"), user("a7p1f_clerk2")
    x.officer, x.officer2 = user("a7p1f_off", [OFFICER]), user("a7p1f_off2", [OFFICER])
    x.lm, x.lm2 = user("a7p1f_lm", [LM]), user("a7p1f_lm2", [LM])
    brand = env["fleet.vehicle.model.brand"].create({"name": "A7P1F Brand"})
    x.van_model = env["fleet.vehicle.model"].create(
        {"name": "A7P1F Van", "brand_id": brand.id, "vehicle_type": "car"}
    )
    x.bike_model = env["fleet.vehicle.model"].create(
        {"name": "A7P1F Bike", "brand_id": brand.id, "vehicle_type": "bike"}
    )
    x.insurer = env["res.partner"].create(
        {"name": "A7P1F Insurer", "is_company": True, "is_insurer": True}
    )

    def doc(v, doc_type, valid_to, user=None, scan=True, **kw):
        vals = {"vehicle_id": v.id, "doc_type": doc_type, "number": "N-" + doc_type}
        vals.update({"valid_to": valid_to, **kw})
        if scan:
            vals.setdefault("evidence_file", SCAN)
        return env["fix.vehicle.document"].with_user(user or x.officer).create(vals)

    def vehicle(plate, model=None, days=200, **kw):
        v = env["fleet.vehicle"].create(
            {"model_id": (model or x.van_model).id, "license_plate": plate, **kw}
        )
        for doc_type in ("fitness", "insurance", "tax"):
            doc(v, doc_type, x.today + timedelta(days=days))
        return v

    def driver(name, user=None, **kw):
        emp = env["hr.employee"].create({"name": name})
        vals = {
            "name": name,
            "employee_id": emp.id,
            "license_no": "DL-" + name,
            "license_class": "Light",
            "license_expiry": x.today + timedelta(days=400),
        }
        vals.update(kw)
        return env["fix.driver"].with_user(user or x.officer).create(vals)

    def assign(v, user=None, **kw):
        vals = {"vehicle_id": v.id, "date": x.today}
        vals.update(kw)
        # booking is the Fleet Officer's (the form and its ACL); M02 dispatch books as itself
        return env["fix.vehicle.assignment"].with_user(user or x.officer).create(vals)

    def check(v, user=None, ok=True, **kw):
        vals = {"vehicle_id": v.id}
        vals.update({k: ok for k in ("tyres_ok", "lights_ok", "fluids_ok", "brakes_ok")})
        vals.update(kw)
        return env["fix.vehicle.check"].with_user(user or x.clerk).create(vals)

    def fill(v, odometer, litres=40.0, amount=4500.0, user=None, **kw):
        vals = {
            "vehicle_id": v.id,
            "driver_id": x.driver.id,
            "odometer": odometer,
            "litres": litres,
            "amount": amount,
        }
        vals.update(kw)
        return env["fix.vehicle.fuel"].with_user(user or x.clerk).create(vals)

    def events(event_type, record):
        return (
            env["fix.event.outbox"]
            .sudo()
            .search(
                [
                    ("event_type", "=", event_type),
                    ("aggregate", "=", record._name),
                    ("aggregate_id", "=", record.id),
                ]
            )
        )

    def open_offroad(v, cause=None):
        dom = [("vehicle_id", "=", v.id), ("state", "=", "offroad")]
        if cause:
            dom.append(("cause", "=", cause))
        return env["fix.vehicle.offroad"].search(dom)

    x.doc, x.vehicle, x.driver_f, x.assign = doc, vehicle, driver, assign
    x.check, x.fill, x.events, x.open_offroad = check, fill, events, open_offroad
    x.driver = driver("A7P1F Driver")
    x.van = vehicle("A7P1F-VAN")
    # A07 decision B10 (8 Nov 2026): a van's pre-use check is its assigned
    # driver's. The clerk is that driver, holding the Driver role.
    x.clerk.write({"group_ids": [(4, env.ref("cd_vehicle_ext.group_fleet_driver").id)]})
    x.driver.sudo().employee_id.user_id = x.clerk
    x.van.fix_driver_id = x.driver
    return x


# =========================================================== roles (P1)
def test_logistics_manager_role_exists_implies_officer_and_admin_holds_it(f):
    group = f.env.ref(LM)
    assert f.env.ref(OFFICER) in group.all_implied_ids
    assert f.env.ref("base.user_admin") in group.user_ids
    assert group.privilege_id == f.env.ref("cd_vehicle_ext.privilege_fleet_operations")


def test_plain_employee_reads_but_does_not_keep_the_registers(f):
    """Documents, drivers and telemetry are the Fleet Officer's; any
    employee may still read them, and does the driver's own work."""
    emp = f.env["hr.employee"].create({"name": "A7P1F Clerk Driver"})
    attempts = [
        lambda: f.doc(f.van, "tax", f.today + timedelta(days=30), user=f.clerk),
        lambda: f.driver_f("A7P1F Self", user=f.clerk, employee_id=emp.id),
        lambda: f.env["fix.vehicle.telemetry"]
        .with_user(f.clerk)
        .create({"vehicle_id": f.van.id, "last_ping": fields.Datetime.now()}),
        lambda: f.driver.with_user(f.clerk).write(
            {"license_expiry": f.today + timedelta(days=900)}
        ),
    ]
    for fn in attempts:
        assert refused(f.env, fn)
    assert (
        f.env["fix.vehicle.document"]
        .with_user(f.clerk)
        .search_count([("vehicle_id", "=", f.van.id)])
        == 3
    )
    # the proper paths: the officer keeps the registers ...
    f.doc(f.van, "route_permit", f.today + timedelta(days=30))
    f.driver_f("A7P1F Second", employee_id=emp.id)
    # ... and the employee does a driver's own work
    f.check(f.van)
    f.fill(f.van, 10000)
    f.env["fix.vehicle.pm"].with_user(f.clerk).create({"vehicle_id": f.van.id})


def test_role_gated_actions_refuse_a_plain_employee(f):
    d = f.driver
    assert "Fleet Officer" in refused(
        f.env, lambda: d.with_user(f.clerk).action_suspend(reason="x")
    )
    pm = f.env["fix.vehicle.pm"].with_user(f.clerk).create({"vehicle_id": f.van.id, "odometer": 1})
    assert refused(f.env, lambda: pm.action_done())
    off = (
        f.env["fix.vehicle.offroad"]
        .with_user(f.clerk)
        .create({"vehicle_id": f.van.id, "reason": "Brakes"})
    )
    f.check(f.van)  # the driver's re-check
    assert refused(f.env, lambda: off.with_user(f.clerk2).action_return())
    # the officer does them
    d.with_user(f.officer).action_suspend(reason="Speeding")
    d.with_user(f.officer2).action_reinstate(reason="Coached")
    pm.with_user(f.officer).action_done()
    off.with_user(f.officer).action_return()
    assert pm.state == "done" and pm.done_by_id == f.officer
    assert off.state == "returned" and off.returned_by_id == f.officer


def test_insert_only_records_are_never_deleted_by_a_user(f):
    chk = f.check(f.van)
    fuel = f.fill(f.van, 10000)
    doc = f.van.document_ids[:1]
    for rec, user in ((chk, f.clerk), (fuel, f.clerk), (doc, f.lm), (chk, f.lm)):
        assert refused(f.env, lambda r=rec, u=user: r.with_user(u).unlink())
    pm = f.env["fix.vehicle.pm"].with_user(f.clerk).create({"vehicle_id": f.van.id})
    assert refused(f.env, lambda: pm.with_user(f.clerk).unlink())
    pm.with_user(f.lm).unlink()  # an open service entered in error


# =========================================================== crons (P1)
@pytest.mark.parametrize(
    "xmlid,model,method",
    [
        ("ir_cron_vehicle_document_expiry", "fix.vehicle.document", "cron_document_expiry"),
        ("ir_cron_driver_licence_expiry", "fix.driver", "cron_driver_licence_expiry"),
        ("ir_cron_vehicle_pm_due", "fix.vehicle.pm", "cron_pm_due"),
        ("ir_cron_vehicle_telemetry_silence", "fix.vehicle.telemetry", "cron_telemetry_silence"),
    ],
)
def test_each_job_is_a_scheduled_active_cron_calling_its_method(f, xmlid, model, method):
    cron = f.env.ref("cd_vehicle_ext.%s" % xmlid)
    assert cron.active and cron.model_id.model == model
    assert cron.code.strip() == "model.%s()" % method
    assert callable(getattr(f.env[model], method))


def test_document_expiry_job_expires_takes_offroad_and_is_idempotent(f):
    ins = f.van.document_ids.filtered(lambda d: d.doc_type == "insurance")
    f.env.flush_all()
    f.env.cr.execute(
        "UPDATE fix_vehicle_document SET valid_to = %s WHERE id = %s",
        (f.today - timedelta(days=1), ins.id),
    )
    f.env.invalidate_all()
    # M46-20: it reads expired from the date at once; the job records the lapse
    assert not ins.is_valid and ins.state == "expired" and ins.recorded_state == "valid"
    f.env["fix.vehicle.document"].cron_document_expiry()
    assert ins.state == "expired" and ins.recorded_state == "expired"
    off = f.open_offroad(f.van, "document")
    assert len(off) == 1 and "Insurance" in off.reason
    assert f.events("vehicle.document_expired", ins)
    assert f.events("vehicle.off_road", off)
    f.env["fix.vehicle.document"].cron_document_expiry()
    assert len(f.open_offroad(f.van, "document")) == 1
    assert len(f.events("vehicle.document_expired", ins)) == 1
    # return needs the renewal with its scan, not a re-check
    f.check(f.van)
    assert "Insurance" in refused(f.env, lambda: off.with_user(f.officer).action_return())
    f.doc(f.van, "insurance", f.today + timedelta(days=365), scan=False)
    assert "evidence" in refused(f.env, lambda: off.with_user(f.officer).action_return())
    f.doc(f.van, "insurance", f.today + timedelta(days=365))
    off.with_user(f.officer).action_return()
    assert off.state == "returned" and f.events("vehicle.available", off)


def test_document_alerts_fire_once_per_threshold(f):
    tax = f.van.document_ids.filtered(lambda d: d.doc_type == "tax")
    f.env.flush_all()
    f.env.cr.execute(
        "UPDATE fix_vehicle_document SET valid_to = %s WHERE id = %s",
        (f.today + timedelta(days=14), tax.id),
    )
    f.env.invalidate_all()
    Doc = f.env["fix.vehicle.document"]
    Doc.cron_document_expiry()
    Doc.cron_document_expiry()
    sent = f.events("vehicle.document_expiring", tax)
    assert len(sent) == 1 and tax.alert_days_sent == 15
    assert json.loads(sent.payload)["days_remaining"] == 14


def test_licence_job_suspends_lapsed_drivers_and_alerts_once(f):
    lapsed = f.driver_f("A7P1F Lapsing")
    soon = f.driver_f("A7P1F Soon", license_expiry=f.today + timedelta(days=10))
    f.env.flush_all()
    f.env.cr.execute(
        "UPDATE fix_driver SET license_expiry = %s WHERE id = %s",
        (f.today - timedelta(days=1), lapsed.id),
    )
    f.env.invalidate_all()
    Driver = f.env["fix.driver"]
    Driver.cron_driver_licence_expiry()
    Driver.cron_driver_licence_expiry()
    assert lapsed.state == "suspended" and not lapsed.suspended_by_id
    assert len(f.events("driver.licence_expired", lapsed)) == 1
    assert len(f.events("driver.licence_expiring", soon)) == 1 and soon.state == "active"
    # the system's suspension is lifted by an officer once the licence is renewed
    assert "licence" in refused(
        f.env, lambda: lapsed.with_user(f.officer).action_reinstate(reason="back")
    )
    lapsed.with_user(f.officer).write({"license_expiry": f.today + timedelta(days=700)})
    lapsed.with_user(f.officer).action_reinstate(reason="Licence renewed")
    assert lapsed.state == "active"


def test_driver_registered_with_an_expired_licence_is_born_suspended(f):
    d = f.driver_f("A7P1F Expired", license_expiry=f.today - timedelta(days=30))
    assert d.state == "suspended"
    assert refused(f.env, lambda: f.assign(f.van, driver_id=d.id))


def test_pm_due_by_date_or_odometer_and_job(f):
    PM = f.env["fix.vehicle.pm"].with_user(f.clerk)
    by_date = PM.create({"vehicle_id": f.van.id, "due_date": f.today - timedelta(days=1)})
    by_km = PM.create({"vehicle_id": f.van.id, "due_odometer": 10500})
    later = PM.create({"vehicle_id": f.van.id, "due_date": f.today + timedelta(days=30)})
    assert by_date.is_overdue and not by_km.is_overdue and not later.is_overdue
    f.fill(f.van, 10600)
    by_km.invalidate_recordset()
    assert by_km.is_overdue
    assert set(PM.search([("is_overdue", "=", True), ("vehicle_id", "=", f.van.id)]).ids) == {
        by_date.id,
        by_km.id,
    }
    f.env["fix.vehicle.pm"].cron_pm_due()
    assert by_date.due_notified and f.events("vehicle.service_due", by_date)
    assert not f.open_offroad(f.van, "service")  # off-road is a switch, off
    f.env["ir.config_parameter"].sudo().set_param(PM_OFFROAD_PARAM, "True")
    f.env["fix.vehicle.pm"].cron_pm_due()
    assert len(f.open_offroad(f.van, "service")) == 1
    assert len(f.events("vehicle.service_due", by_date)) == 1


def test_telemetry_state_follows_the_ping_and_silence_job(f):
    Tel = f.env["fix.vehicle.telemetry"].with_user(f.officer)
    old = Tel.create(
        {
            "vehicle_id": f.van.id,
            "device_ref": "T1",
            "last_ping": fields.Datetime.now() - timedelta(days=30),
        }
    )
    assert old.state == "stale"
    assert refused(f.env, lambda: old.write({"state": "online"}))
    fresh = Tel.create(
        {
            "vehicle_id": f.van.id,
            "device_ref": "T1",
            "last_ping": fields.Datetime.now() - timedelta(minutes=5),
        }
    )
    assert fresh.state == "online" and not f.van.fix_position_unknown
    f.env["ir.config_parameter"].sudo().set_param(TELEMATICS_SILENCE_PARAM, "1")
    f.env["fix.vehicle.telemetry"].cron_telemetry_silence()
    f.env["fix.vehicle.telemetry"].cron_telemetry_silence()
    f.van.invalidate_recordset()
    assert fresh.state == "stale" and f.van.fix_position_unknown
    assert len(f.events("vehicle.telematics_silent", fresh)) == 1


# =========================================================== the register (M46-3/5)
def test_document_needs_its_scan_to_count(f):
    v = f.env["fleet.vehicle"].create({"model_id": f.van_model.id, "license_plate": "A7P1F-SCAN"})
    for t in ("fitness", "insurance", "tax"):
        f.doc(v, t, f.today + timedelta(days=90), scan=False)
    assert not v.compliance_ok
    assert "evidence" in refused(f.env, lambda: f.assign(v))
    docs = v.document_ids
    assert set(docs.mapped("evidence_status")) == {"missing"} and not any(docs.mapped("is_valid"))
    for d in docs:
        d.with_user(f.officer).write({"evidence_file": SCAN})
    v.invalidate_recordset()
    assert v.compliance_ok and all(docs.mapped("is_valid"))
    f.assign(v)
    # a scanned document certifies its facts: no editing afterwards
    assert refused(
        f.env,
        lambda: docs[:1].with_user(f.officer).write({"valid_to": f.today + timedelta(days=900)}),
    )


def test_legacy_documents_count_until_switched_off(f):
    """Superuser data loading (the live register) is legacy: it counts while
    the switch is on, and is queued for its scan."""
    v = f.env["fleet.vehicle"].create({"model_id": f.van_model.id, "license_plate": "A7P1F-LEG"})
    for t in ("fitness", "insurance", "tax"):
        f.env["fix.vehicle.document"].create(
            {"vehicle_id": v.id, "doc_type": t, "valid_to": f.today + timedelta(days=90)}
        )
    assert set(v.document_ids.mapped("evidence_status")) == {"legacy"} and v.compliance_ok
    f.env["ir.config_parameter"].sudo().set_param(LEGACY_EVIDENCE_PARAM, "False")
    v.invalidate_recordset()
    assert not v.compliance_ok


def test_latest_recorded_document_is_the_current_one(f):
    old = f.van.document_ids.filtered(lambda d: d.doc_type == "fitness")
    lapse = f.doc(f.van, "fitness", f.today - timedelta(days=2), state="expired")
    assert lapse.is_current and not old.is_current
    assert not f.van.compliance_ok and f.van.fitness_expiry == lapse.valid_to
    # a renewal that starts next month does not supersede until it starts
    renewal = f.doc(
        f.van,
        "fitness",
        f.today + timedelta(days=400),
        valid_from=f.today + timedelta(days=30),
    )
    assert not renewal.is_current and lapse.is_current
    fix = f.doc(f.van, "fitness", f.today + timedelta(days=365))
    assert fix.is_current and f.van.compliance_ok


def test_header_dates_come_from_the_register_and_are_not_typed(f):
    ins = f.van.document_ids.filtered(lambda d: d.doc_type == "insurance")
    assert f.van.insurance_expiry == ins.valid_to
    future = f.today + timedelta(days=900)
    for user in (f.officer, f.lm):
        assert "register" in refused(
            f.env, lambda u=user: f.van.with_user(u).write({"insurance_expiry": future})
        )
    assert refused(
        f.env,
        lambda: f.env["fleet.vehicle"]
        .with_user(f.officer)
        .create(
            {"model_id": f.van_model.id, "license_plate": "A7P1F-TYPED", "fitness_expiry": future}
        ),
    )
    # the echo of the value it already has passes (the P03 form posts it)
    f.van.with_user(f.officer).write({"insurance_expiry": ins.valid_to, "branch_id": False})


def test_unknown_mandatory_type_fails_closed(f):
    f.env["ir.config_parameter"].sudo().set_param(MANDATORY_DOCS_PARAM, "fitness,insurence")
    f.van.invalidate_recordset()
    assert not f.van.compliance_ok and "insurence" in f.van.dispatch_blockers


def test_one_plate_one_active_vehicle(f):
    for plate in ("A7P1F-VAN", "a7p1f van", " A7P1F_VAN "):
        assert "already registered" in refused(
            f.env,
            lambda p=plate: f.env["fleet.vehicle"].create(
                {"model_id": f.van_model.id, "license_plate": p}
            ),
        )
    f.van.write({"active": False})
    f.env["fleet.vehicle"].create({"model_id": f.van_model.id, "license_plate": "A7P1F-VAN"})


# =========================================================== drivers (M46-6)
def test_licence_class_must_cover_the_vehicle(f):
    moto = f.driver_f("A7P1F Moto", license_class="Motorcycle")
    assert "does not cover" in refused(f.env, lambda: f.assign(f.van, driver_id=moto.id))
    bike = f.vehicle("A7P1F-BIKE", model=f.bike_model)
    assert bike.fix_licence_class_required == "motorcycle"
    assert "does not cover" in refused(f.env, lambda: f.assign(bike, driver_id=f.driver.id))
    f.assign(bike, driver_id=moto.id)
    f.assign(f.van, driver_id=f.driver.id)
    # a heavy vehicle needs a heavy licence; a heavy licence covers a van
    truck = f.vehicle("A7P1F-TRUCK")
    truck.write({"fix_licence_class_required": "heavy"})
    assert refused(f.env, lambda: f.assign(truck, driver_id=f.driver.id))
    heavy = f.driver_f("A7P1F Heavy", license_class="Heavy (professional)")
    f.assign(truck, driver_id=heavy.id)


def test_unrecorded_licence_class_blocks_only_when_switched_on(f):
    pro = f.driver_f("A7P1F Pro", license_class="professional")
    van2 = f.vehicle("A7P1F-VAN2")
    f.assign(van2, driver_id=pro.id)
    f.env["ir.config_parameter"].sudo().set_param(LICENCE_CLASS_PARAM, "True")
    van3 = f.vehicle("A7P1F-VAN3")
    assert "BRTA" in refused(f.env, lambda: f.assign(van3, driver_id=pro.id))


# =========================================================== off-road (M46-7/8/10)
def test_failed_check_takes_the_vehicle_offroad_until_someone_else_returns_it(f):
    chk = f.check(f.van, brakes_ok=False, defects="Brakes soft")
    off = f.open_offroad(f.van, "defect")
    assert off.check_id == chk and off.raised_by_id == f.clerk
    assert f.events("vehicle.defect_raised", chk) and f.events("vehicle.off_road", off)
    assert refused(f.env, lambda: f.assign(f.van))
    # the reporter, if an officer, still cannot return what they raised
    chk2 = f.check(f.van, user=f.officer, lights_ok=False)
    assert chk2 and len(f.open_offroad(f.van, "defect")) == 1
    f.check(f.van)  # the driver's re-check
    assert "Segregation" not in (
        refused(f.env, lambda: off.with_user(f.officer).action_return()) or ""
    )
    assert off.state == "returned"


def test_reporter_who_is_an_officer_cannot_return_their_own_offroad(f):
    f.check(f.van, user=f.officer, brakes_ok=False)
    off = f.open_offroad(f.van, "defect")
    f.check(f.van, user=f.clerk)
    assert "Segregation of duties" in refused(
        f.env, lambda: off.with_user(f.officer).action_return()
    )
    off.with_user(f.officer2).action_return()


def test_cause_and_raiser_cannot_be_typed(f):
    Off = f.env["fix.vehicle.offroad"].with_user(f.clerk)
    for vals in ({"cause": "document"}, {"raised_by_id": f.clerk2.id}):
        assert refused(
            f.env, lambda v=vals: Off.create({"vehicle_id": f.van.id, "reason": "x", **v})
        )
    off = Off.create({"vehicle_id": f.van.id, "reason": "Clutch"})
    assert off.cause == "defect" and off.raised_by_id == f.clerk
    assert refused(f.env, lambda: off.write({"cause": "document"}))


def test_reported_accident_takes_the_vehicle_offroad(f):
    acc = (
        f.env["fix.vehicle.accident"]
        .with_user(f.clerk)
        .create({"vehicle_id": f.van.id, "description": "Rear-ended", "injury": True})
    )
    off = f.open_offroad(f.van, "accident")
    assert off.accident_id == acc and off.raised_by_id == f.clerk
    payload = json.loads(f.events("vehicle.incident", acc).payload)
    assert payload["injuries"] is True and payload["vehicle_id"] == f.van.id


def test_claim_close_needs_a_logistics_manager_insurer_and_evidence(f):
    acc = (
        f.env["fix.vehicle.accident"]
        .with_user(f.clerk)
        .create({"vehicle_id": f.van.id, "description": "Side swipe", "damage_cost": 12000})
    )
    acc.with_user(f.clerk).action_claim(claim_ref="INS-9")
    assert "Logistics Manager" in refused(
        f.env, lambda: acc.with_user(f.officer).action_close(settlement="0")
    )
    assert "insurer" in refused(f.env, lambda: acc.with_user(f.lm).action_close(settlement="0"))
    acc.with_user(f.clerk).write({"insurer_id": f.insurer.id})
    assert "evidence" in refused(f.env, lambda: acc.with_user(f.lm).action_close(settlement="0"))
    acc.with_user(f.clerk).write({"evidence_file": SCAN})
    acc.with_user(f.lm).action_close(settlement="0")
    assert acc.state == "closed" and acc.closed_by_id == f.lm
    assert refused(f.env, lambda: acc.with_user(f.lm).write({"insurer_id": False}))


def test_only_the_reporter_or_an_officer_files_the_claim(f):
    acc = (
        f.env["fix.vehicle.accident"]
        .with_user(f.clerk)
        .create({"vehicle_id": f.van.id, "description": "x", "claim_ref": "INS-10"})
    )
    assert refused(f.env, lambda: acc.with_user(f.clerk2).action_claim())
    acc.with_user(f.officer).action_claim()
    assert acc.state == "claimed"


# =========================================================== fuel (M46-9)
@pytest.mark.parametrize("rule", ["odometer_back", "over_capacity", "duplicate", "offroad"])
def test_hard_fuel_rules_refuse_a_users_fill(f, rule):
    f.fill(f.van, 12000)
    if rule == "odometer_back":
        fn = lambda: f.fill(f.van, 9000, litres=35)  # noqa: E731
    elif rule == "over_capacity":
        fn = lambda: f.fill(f.van, 12400, litres=5000, amount=600000)  # noqa: E731
    elif rule == "duplicate":
        fn = lambda: f.fill(f.van, 12000, user=f.clerk2)  # noqa: E731
    else:
        f.env["fix.vehicle.offroad"].create({"vehicle_id": f.van.id, "reason": "Engine out"})
        fn = lambda: f.fill(f.van, 12400, litres=30)  # noqa: E731
    assert "refused" in refused(f.env, fn)


def test_superuser_loading_is_held_not_refused(f):
    """A fuel-card feed is never dropped: a breach holds it for review."""
    f.fill(f.van, 12000)
    held = f.env["fix.vehicle.fuel"].create(
        {"vehicle_id": f.van.id, "odometer": 9000, "litres": 35, "amount": 4000}
    )
    assert held.review_state == "held" and held.exception_flags == "odometer_back"
    assert f.events("vehicle.fuel_exception", held)
    assert not f.events("vehicle.fuel_recorded", held)


def test_same_receipt_at_the_same_station_is_a_duplicate(f):
    f.fill(f.van, 12000, receipt_no="R-77", station="Padma Oil")
    assert refused(
        f.env, lambda: f.fill(f.van, 12400, litres=30, receipt_no="r-77 ", station="padma oil")
    )
    f.fill(f.van, 12400, litres=30, receipt_no="R-77", station="Meghna")


def test_tank_capacity_of_the_vehicle_wins_over_the_fleet_ceiling(f):
    bike = f.vehicle("A7P1F-BK", model=f.bike_model)
    bike.write({"fix_tank_capacity_l": 12})
    assert refused(f.env, lambda: f.fill(bike, 5000, litres=15))
    f.fill(bike, 5000, litres=11)


def test_implausible_distance_is_held_and_reviewed_by_a_logistics_manager(f):
    f.fill(f.van, 10000)
    f.fill(f.van, 11000)  # 25 km/l
    typo = f.fill(f.van, 999999)  # one typo odometer
    assert typo.review_state == "held" and typo.exception_flags == "odometer_jump"
    assert not f.events("vehicle.fuel_recorded", typo)
    assert "Logistics Manager" in refused(
        f.env, lambda: typo.with_user(f.officer).action_reject_fill(reason="typo")
    )
    lm_fill = f.fill(f.van, 998000, user=f.lm)  # the manager's own held fill
    assert lm_fill.review_state == "held"
    assert "Segregation" in refused(
        f.env, lambda: lm_fill.with_user(f.lm).action_clear_exception(note="mine")
    )
    typo.with_user(f.lm).action_reject_fill(reason="Odometer typo")
    assert typo.review_state == "rejected" and typo.reviewed_by_id == f.lm
    # a cleared fill reaches M52 only once cleared
    lm_fill.with_user(f.lm2).action_clear_exception(note="Long trip, log attached")
    assert f.events("vehicle.fuel_recorded", lm_fill)


def test_cost_per_km_leaves_held_fills_out(f):
    import odoo.addons.cd_p03_portal.controllers.a07.m46 as m46

    v = f.vehicle("A7P1F-CPK")
    f.fill(v, 10000)
    f.fill(v, 11000)
    f.fill(v, 999999)
    row = next(r for r in m46.cost_per_km(f.env)["rows"] if r["plate"] == "A7P1F-CPK")
    assert row["km"] == 1000 and row["basis"].startswith("provisional")
    assert "implausible distance" in row["basis"]


# =========================================================== isolation (M46-15)
def test_ops_models_are_fenced_by_company(f):
    other = f.env["res.company"].create({"name": "A7P1F OtherCo"})
    v = f.env["fleet.vehicle"].create(
        {"model_id": f.van_model.id, "license_plate": "A7P1F-OTHER", "company_id": other.id}
    )
    f.env["fix.vehicle.document"].create(
        {"vehicle_id": v.id, "doc_type": "tax", "valid_to": f.today + timedelta(days=9)}
    )
    f.env["fix.vehicle.check"].create({"vehicle_id": v.id})
    for model in ("fix.vehicle.document", "fix.vehicle.check", "fix.vehicle.offroad"):
        assert not f.env[model].with_user(f.officer).search([("vehicle_id", "=", v.id)]), model
        assert f.env[model].search([("vehicle_id", "=", v.id)]), model
