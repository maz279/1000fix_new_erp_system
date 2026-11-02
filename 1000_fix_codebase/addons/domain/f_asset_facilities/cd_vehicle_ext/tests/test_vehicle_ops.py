"""cd_vehicle_ext ops behaviour (live ORM, rolled back): drivers, documents,
off-road records, pre-use checks, PM, fuel, telemetry and accidents."""

from __future__ import annotations

import uuid
from datetime import date, timedelta

import pytest
from odoo.exceptions import UserError
from psycopg2 import IntegrityError

TAG = uuid.uuid4().hex[:4].upper()


@pytest.fixture
def ctx(odoo_env):
    env = odoo_env
    brand = env["fleet.vehicle.model.brand"].create({"name": f"Fleet Brand {TAG}"})
    model = env["fleet.vehicle.model"].create({"name": f"Fleet Model {TAG}", "brand_id": brand.id})
    vehicle = env["fleet.vehicle"].create(
        {
            "model_id": model.id,
            "license_plate": f"E2E-{TAG}",
            "fitness_expiry": date(2027, 1, 1),
            "insurance_expiry": date(2027, 1, 1),
        }
    )
    employee = env["hr.employee"].create({"name": f"Driver {TAG}"})
    driver = env["fix.driver"].create(
        {"name": f"Driver {TAG}", "employee_id": employee.id, "license_no": f"DL-{TAG}"}
    )
    return {"env": env, "vehicle": vehicle, "driver": driver}


def test_driver_unique_employee(ctx):
    env, driver = ctx["env"], ctx["driver"]
    with pytest.raises(IntegrityError), env.cr.savepoint():
        env["fix.driver"].create(
            {"name": "dup", "employee_id": driver.employee_id.id, "license_no": f"DL2-{TAG}"}
        )


def test_vehicle_document_validity_uses_end_date(ctx):
    env, vehicle = ctx["env"], ctx["vehicle"]
    expired = env["fix.vehicle.document"].create(
        {"vehicle_id": vehicle.id, "valid_to": date(2020, 1, 1), "state": "valid"}
    )
    valid = env["fix.vehicle.document"].create(
        {
            "vehicle_id": vehicle.id,
            "doc_type": "tax",
            "valid_to": date.today() + timedelta(days=30),
            "state": "valid",
        }
    )
    assert expired.is_valid is False
    assert valid.is_valid is True


def test_offroad_and_return(ctx):
    env, vehicle = ctx["env"], ctx["vehicle"]
    record = env["fix.vehicle.offroad"].create({"vehicle_id": vehicle.id, "reason": "service"})
    assert record.name.startswith("VOFF/")
    record.action_return()
    assert record.state == "returned"
    assert record.ended_on
    with pytest.raises(UserError, match="off-road"), env.cr.savepoint():
        record.action_return()


def test_pre_use_check_pass_compute(ctx):
    env, vehicle, driver = ctx["env"], ctx["vehicle"], ctx["driver"]
    check = env["fix.vehicle.check"].create(
        {"vehicle_id": vehicle.id, "driver_id": driver.id, "brakes_ok": False}
    )
    assert check.name.startswith("VCHK/")
    assert check.passed is False
    check.brakes_ok = True
    assert check.passed is True


def test_pm_done_and_fuel_positive(ctx):
    env, vehicle = ctx["env"], ctx["vehicle"]
    job = env["fix.vehicle.pm"].create({"vehicle_id": vehicle.id, "cost": 5000})
    assert job.name.startswith("VPM/")
    job.action_done()
    assert job.done_on
    with pytest.raises(IntegrityError), env.cr.savepoint():
        env["fix.vehicle.fuel"].create({"vehicle_id": vehicle.id, "litres": 0, "odometer": 1000})


def test_telemetry_fuel_range(ctx):
    env, vehicle = ctx["env"], ctx["vehicle"]
    snap = env["fix.vehicle.telemetry"].create({"vehicle_id": vehicle.id, "fuel_level_pct": 50})
    assert snap.name.startswith("VTEL/")
    with pytest.raises(IntegrityError), env.cr.savepoint():
        snap.fuel_level_pct = 101


def test_accident_claim_then_close(ctx):
    env, vehicle = ctx["env"], ctx["vehicle"]
    accident = env["fix.vehicle.accident"].create(
        {"vehicle_id": vehicle.id, "description": "bumper", "damage_cost": 1000}
    )
    assert accident.name.startswith("VACC/")
    with pytest.raises(UserError, match="claimed"), env.cr.savepoint():
        accident.action_close()
    accident.action_claim()
    accident.action_close()
    assert accident.state == "closed"


def test_dispatch_gate_requires_compliance(ctx):
    env, vehicle = ctx["env"], ctx["vehicle"]
    vehicle.write({"insurance_expiry": date(2020, 1, 1)})
    with pytest.raises(Exception, match="not dispatchable"), env.cr.savepoint():
        vehicle.action_assert_dispatchable()
