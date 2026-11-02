"""cd_ewaste_ops behaviour (live ORM, rolled back): the M18 workspace records —
collection event, triage decision, batch dispatch, battery stream, certified
partner, disposal certificate and statutory return."""

from __future__ import annotations

from datetime import date

import pytest
from odoo.exceptions import UserError, ValidationError
from psycopg2 import IntegrityError


def _customer(env):
    return env["res.partner"].create({"name": "M18 Ops Donor"})


def _collection(env, **vals):
    vals.setdefault("customer_id", _customer(env).id)
    vals.setdefault("material_type", "laptop")
    vals.setdefault("weight_kg", 3.5)
    return env["fix.ewaste.collection"].create(vals)


def test_event_collected_weight_sums_collections(odoo_env):
    env = odoo_env
    event = env["fix.ewaste.event"].create({"event_date": date(2026, 10, 28), "venue": "Hall"})
    assert event.name.startswith("EWEV/")
    _collection(env, event_id=event.id, weight_kg=2.0)
    _collection(env, event_id=event.id, weight_kg=1.25)
    assert event.collected_kg == pytest.approx(3.25)


def test_triage_applies_grade_to_collected(odoo_env):
    env = odoo_env
    rec = _collection(env)
    triage = env["fix.ewaste.triage"].create(
        {"collection_id": rec.id, "decision": "refurbish", "decided_on": date(2026, 10, 28)}
    )
    assert triage.name.startswith("ETRI/")
    assert rec.state == "triaged"
    assert rec.triage_grade == "refurbish"


def test_batch_dispatch_requires_partner(odoo_env):
    env = odoo_env
    batch = env["fix.ewaste.batch"].create({"material_type": "laptop", "weight_kg": 5})
    assert batch.name.startswith("EBTY/")
    with pytest.raises(UserError, match="certified partner"), env.cr.savepoint():
        batch.action_dispatch()
    partner = env["fix.ewaste.partner"].create({"name": "Recycler A"})
    batch.partner_id = partner.id
    batch.action_dispatch()
    assert batch.state == "dispatched"
    assert batch.dispatched_on


def test_battery_negative_weight_refused(odoo_env):
    env = odoo_env
    with pytest.raises(IntegrityError), env.cr.savepoint():
        env["fix.ewaste.battery"].create(
            {"chemistry": "li_ion", "weight_kg": -1, "hazard_class": "class_9"}
        )


def test_certified_partner_cannot_be_active_when_expired(odoo_env):
    env = odoo_env
    with pytest.raises(ValidationError, match="cannot be active"), env.cr.savepoint():
        env["fix.ewaste.partner"].create(
            {
                "name": "Expired Recycler",
                "certification": "doe",
                "valid_from": date(2020, 1, 1),
                "valid_to": date(2021, 1, 1),
                "state": "active",
            }
        )


def test_return_overdue_flag(odoo_env):
    env = odoo_env
    overdue = env["fix.ewaste.return"].create(
        {"authority": "doe", "period": "2026-09", "due_date": date(2026, 9, 30)}
    )
    current = env["fix.ewaste.return"].create(
        {"authority": "btrc", "period": "2026-10", "due_date": date(2027, 11, 15)}
    )
    assert overdue.name.startswith("ERET/")
    assert overdue.is_overdue is True
    assert current.is_overdue is False
    overdue.state = "submitted"
    assert overdue.is_overdue is False


def test_disposal_certificate_names_partner(odoo_env):
    env = odoo_env
    partner = env["fix.ewaste.partner"].create({"name": "Recycler B"})
    rec = _collection(env, state="recycled")
    cert = env["fix.ewaste.certificate"].create(
        {
            "collection_id": rec.id,
            "partner_id": partner.id,
            "material_type": "laptop",
            "weight_kg": 3.5,
            "issued_on": date(2026, 10, 28),
        }
    )
    assert cert.name.startswith("ECER/")
    assert cert.state == "issued"
