"""cd_vehicle_ext behaviour (live ORM, rolled back): fleet compliance and
dispatch vehicle assignment (one van, one place, one day)."""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from odoo.exceptions import ValidationError

# the gate decides on the Dhaka date (A07 audit M46-2)
TODAY = datetime.now(ZoneInfo("Asia/Dhaka")).date()


def _vehicle(env, fitness=None, insurance=None, plate="DHAKA-METRO-GA-11-2233"):
    """A vehicle whose fitness and insurance are recorded in the document
    register (A07 audit M46-2/3: the register, not the header dates, decides
    compliance), with a valid token tax. None = no such document."""
    brand = env["fleet.vehicle.model.brand"].create({"name": "Toyota (behaviour)"})
    model = env["fleet.vehicle.model"].create({"name": "HiAce", "brand_id": brand.id})
    vehicle = env["fleet.vehicle"].create(
        {
            "model_id": model.id,
            "license_plate": plate,
            "fitness_expiry": fitness,
            "insurance_expiry": insurance,
        }
    )
    for doc_type, valid_to in (
        ("fitness", fitness),
        ("insurance", insurance),
        ("tax", TODAY + timedelta(days=90)),
    ):
        if valid_to:
            env["fix.vehicle.document"].create(
                {"vehicle_id": vehicle.id, "doc_type": doc_type, "valid_to": valid_to}
            )
    return vehicle


def _compliant(env, **kw):
    return _vehicle(env, TODAY + timedelta(days=30), TODAY + timedelta(days=60), **kw)


@pytest.mark.parametrize(
    ("fitness", "insurance", "ok"),
    [
        (30, 60, True),
        (0, 0, True),  # expiring today is still valid
        (-1, 60, False),
        (30, -1, False),
        (None, 60, False),
        (30, None, False),
        (None, None, False),
    ],
)
def test_compliance_requires_valid_fitness_and_insurance(odoo_env, fitness, insurance, ok):
    def offset(days):
        return None if days is None else TODAY + timedelta(days=days)

    vehicle = _vehicle(odoo_env, offset(fitness), offset(insurance))
    assert vehicle.compliance_ok is ok


def test_dispatchable_vehicle_passes_gate(odoo_env):
    assert _compliant(odoo_env).action_assert_dispatchable() is True


def test_non_compliant_vehicle_is_not_dispatchable(odoo_env):
    vehicle = _vehicle(odoo_env, TODAY - timedelta(days=1), TODAY + timedelta(days=60))
    with pytest.raises(ValidationError, match="is not dispatchable"):
        vehicle.action_assert_dispatchable()


def test_gate_checks_every_vehicle(odoo_env):
    good = _compliant(odoo_env, plate="GOOD-1")
    bad = _vehicle(odoo_env, None, None, plate="BAD-1")
    with pytest.raises(ValidationError, match="BAD-1"):
        (good | bad).action_assert_dispatchable()


def test_assignment_publishes_event(odoo_env):
    vehicle = _compliant(odoo_env)
    day = date(2026, 11, 3)
    assignment = odoo_env["fix.vehicle.assignment"].create({"vehicle_id": vehicle.id, "date": day})
    rows = odoo_env["fix.event.outbox"].search(
        [
            ("event_type", "=", "vehicle.assigned"),
            ("aggregate", "=", "fix.vehicle.assignment"),
            ("aggregate_id", "=", assignment.id),
        ]
    )
    assert [json.loads(r.payload) for r in rows] == [
        {"vehicle": vehicle.name, "date": "2026-11-03"}
    ]


def test_assignment_refused_for_non_compliant_vehicle(odoo_env):
    vehicle = _vehicle(odoo_env, TODAY + timedelta(days=5), TODAY - timedelta(days=5))
    with pytest.raises(ValidationError, match="not dispatchable"), odoo_env.cr.savepoint():
        odoo_env["fix.vehicle.assignment"].create({"vehicle_id": vehicle.id, "date": TODAY})


def test_same_day_double_booking_refused(odoo_env):
    vehicle = _compliant(odoo_env)
    model = odoo_env["fix.vehicle.assignment"]
    model.create({"vehicle_id": vehicle.id, "date": date(2026, 11, 4)})
    # a different day is fine
    model.create({"vehicle_id": vehicle.id, "date": date(2026, 11, 5)})
    with (
        pytest.raises(ValidationError, match="already assigned on 2026-11-04"),
        odoo_env.cr.savepoint(),
    ):
        model.create({"vehicle_id": vehicle.id, "date": date(2026, 11, 4)})
    assert model.search_count([("vehicle_id", "=", vehicle.id)]) == 2
