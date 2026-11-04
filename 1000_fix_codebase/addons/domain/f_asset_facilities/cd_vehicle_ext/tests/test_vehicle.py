# cd_vehicle_ext tests — P08-M08 (CD-M46-01).
#
# A07 P1 (2026-11-04) M46-19 / D10: these four tests grepped the source text
# (inspect.getsource) for "overlaps are refused", "_fix_check_dispatchable",
# "_fix_missing_documents" and "vehicle.assigned", which certified the
# narrow header-date gate as "dispatch gate covered". They now exercise the
# same four claims on the live ORM (odoo_env: rolled back), as a NON-ADMIN
# employee, so re-introducing a defect turns them red.
import base64
from datetime import timedelta

import pytest
from odoo.addons.cd_vehicle_ext.models.fix_vehicle_ops import dhaka_today
from odoo.exceptions import ValidationError

SCAN = base64.b64encode(b"%PDF-1.4 scan").decode()


@pytest.fixture
def v(odoo_env):
    env = odoo_env
    today = dhaka_today(env["fix.vehicle.check"])
    clerk = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "a7p1tv_clerk",
                "login": "a7p1tv_clerk",
                "group_ids": [(6, 0, [env.ref("base.group_user").id])],
            }
        )
    )
    brand = env["fleet.vehicle.model.brand"].create({"name": "A7P1TV Brand"})
    model = env["fleet.vehicle.model"].create({"name": "A7P1TV Van", "brand_id": brand.id})

    def vehicle(plate, docs=("fitness", "insurance", "tax")):
        rec = env["fleet.vehicle"].create({"model_id": model.id, "license_plate": plate})
        for doc_type in docs:
            env["fix.vehicle.document"].create(
                {
                    "vehicle_id": rec.id,
                    "doc_type": doc_type,
                    "valid_to": today + timedelta(days=100),
                    "evidence_file": SCAN,
                }
            )
        return rec

    def assign(rec, day=None):
        return (
            env["fix.vehicle.assignment"]
            .with_user(clerk)
            .create({"vehicle_id": rec.id, "date": day or today})
        )

    return env, today, clerk, vehicle, assign


def test_overlap_refused(v):
    env, today, _clerk, vehicle, assign = v
    van = vehicle("A7P1TV-1")
    assign(van)
    with pytest.raises(ValidationError, match="overlaps are refused"), env.cr.savepoint():
        assign(van)
    assert assign(van, day=today + timedelta(days=1))


def test_compliance_gates_dispatch(v):
    """create AND write run the gate (A07 audit M46-4)."""
    env, _today, clerk, vehicle, assign = v
    good, bad = vehicle("A7P1TV-GOOD"), vehicle("A7P1TV-BAD", docs=("fitness", "tax"))
    with pytest.raises(ValidationError, match="not dispatchable"), env.cr.savepoint():
        assign(bad)
    a = assign(good)
    with pytest.raises(ValidationError, match="not dispatchable"), env.cr.savepoint():
        a.with_user(clerk).write({"vehicle_id": bad.id})
    assert a.vehicle_id == good


def test_compliance_compute(v):
    """A07 audit M46-3: compliance comes from the document register, not the
    header date (which is read from it, A07 P1)."""
    env, today, _clerk, vehicle, _assign = v
    van = vehicle("A7P1TV-REG", docs=("fitness", "tax"))
    assert not van.compliance_ok and not van.insurance_expiry
    env["fix.vehicle.document"].create(
        {
            "vehicle_id": van.id,
            "doc_type": "insurance",
            "valid_to": today + timedelta(days=30),
            "evidence_file": SCAN,
        }
    )
    van.invalidate_recordset()
    assert van.compliance_ok and van.insurance_expiry == today + timedelta(days=30)


def test_assignment_event(v):
    env, _today, _clerk, vehicle, assign = v
    a = assign(vehicle("A7P1TV-EVT"))
    rows = (
        env["fix.event.outbox"]
        .sudo()
        .search(
            [
                ("event_type", "=", "vehicle.assigned"),
                ("aggregate", "=", "fix.vehicle.assignment"),
                ("aggregate_id", "=", a.id),
            ]
        )
    )
    assert len(rows) == 1
