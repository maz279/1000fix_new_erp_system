"""cd_vendor_portal supplier-register behaviour (live ORM, rolled back): the M42
workspace records — documents validity, qualification, the activation gate,
performance scorecards, CARs, reviews, risk and compliance screening."""

from __future__ import annotations

import uuid
from datetime import date, timedelta

import pytest
from odoo.exceptions import UserError
from psycopg2 import IntegrityError

TAG = uuid.uuid4().hex[:6].upper()


@pytest.fixture
def ctx(odoo_env):
    env = odoo_env
    partner = env["res.partner"].create({"name": f"Supplier Partner {TAG}", "is_company": True})
    supplier = env["fix.supplier"].create({"name": f"Supplier {TAG}", "partner_id": partner.id})
    return {"env": env, "partner": partner, "supplier": supplier}


def _doc(ctx, doc_type, valid_to):
    return ctx["env"]["fix.supplier.document"].create(
        {
            "supplier_id": ctx["supplier"].id,
            "doc_type": doc_type,
            "number": f"{doc_type}-{TAG}",
            "valid_from": date(2026, 1, 1),
            "valid_to": valid_to,
            "state": "valid",
        }
    )


def test_supplier_code_and_unique_partner(ctx):
    supplier = ctx["supplier"]
    assert supplier.supplier_code.startswith("SUP/")
    with pytest.raises(IntegrityError), ctx["env"].cr.savepoint():
        ctx["env"]["fix.supplier"].create({"name": "Duplicate", "partner_id": ctx["partner"].id})


def test_document_validity_uses_the_end_date(ctx):
    expired = _doc(ctx, "trade_licence", date(2020, 1, 1))
    valid = _doc(ctx, "tin", date.today() + timedelta(days=30))
    assert expired.is_valid is False
    assert valid.is_valid is True


def test_qualification_approval_moves_supplier_to_qualified(ctx):
    env, supplier = ctx["env"], ctx["supplier"]
    qual = env["fix.supplier.qualification"].create(
        {"supplier_id": supplier.id, "submitted_on": date(2026, 10, 28), "score": 80}
    )
    assert supplier.status == "prospect"
    with pytest.raises(UserError, match="in review"), env.cr.savepoint():
        qual.action_approve()
    qual.action_start()
    qual.action_approve()
    assert qual.state == "approved"
    assert supplier.status == "qualified"


def test_activation_gate_blocks_then_passes(ctx):
    env, supplier = ctx["env"], ctx["supplier"]
    qual = env["fix.supplier.qualification"].create(
        {"supplier_id": supplier.id, "submitted_on": date(2026, 10, 28), "score": 80}
    )
    qual.action_start()
    qual.action_approve()
    activation = env["fix.supplier.activation"].create(
        {"supplier_id": supplier.id, "qualification_id": qual.id}
    )
    with pytest.raises(UserError, match="Activation blocked"), env.cr.savepoint():
        activation.action_activate()
    for doc_type in ("trade_licence", "tin", "vat"):
        _doc(ctx, doc_type, date.today() + timedelta(days=200))
    activation.action_activate()
    assert activation.state == "activated"
    assert supplier.status == "active"


def test_requalification_needs_outcome(ctx):
    env, supplier = ctx["env"], ctx["supplier"]
    requal = env["fix.supplier.requalification"].create(
        {"supplier_id": supplier.id, "due_on": date(2026, 12, 31)}
    )
    assert requal.name.startswith("SREQ/")
    with pytest.raises(UserError, match="outcome"), env.cr.savepoint():
        requal.action_complete()
    requal.outcome = "pass"
    requal.action_complete()
    assert requal.state == "done"


def test_performance_score_compute_and_grade(ctx):
    env, supplier = ctx["env"], ctx["supplier"]
    card = env["fix.supplier.performance"].create(
        {
            "supplier_id": supplier.id,
            "period": "2026-10",
            "quality_score": 90,
            "delivery_score": 85,
            "cost_score": 80,
            "responsiveness_score": 88,
        }
    )
    assert card.name.startswith("SPERF/")
    assert card.total_score == pytest.approx(86.2)
    assert card.grade == "a"


def test_car_lifecycle_and_overdue(ctx):
    env, supplier = ctx["env"], ctx["supplier"]
    car = env["fix.supplier.car"].create(
        {
            "supplier_id": supplier.id,
            "issue": "Late delivery",
            "severity": "major",
            "raised_on": date(2026, 10, 1),
            "due_date": date(2026, 10, 10),
        }
    )
    assert car.is_overdue is True
    with pytest.raises(UserError, match="action plan"), env.cr.savepoint():
        car.action_action()
    car.action_plan = "Supplier to re-plan dispatch"
    car.action_action()
    car.action_close()
    assert car.state == "closed"
    assert car.is_overdue is False


def test_risk_band(ctx):
    env, supplier = ctx["env"], ctx["supplier"]
    risk = env["fix.supplier.risk"].create(
        {"supplier_id": supplier.id, "risk_type": "financial", "likelihood": 4, "impact": 5}
    )
    assert risk.risk_score == 20
    assert risk.band == "critical"
    with pytest.raises(UserError, match="mitigation"), env.cr.savepoint():
        risk.action_mitigate()
    risk.mitigation = "Dual source"
    risk.action_mitigate()
    assert risk.state == "mitigated"


def test_screening_hit_cannot_clear(ctx):
    env, supplier = ctx["env"], ctx["supplier"]
    hit = env["fix.supplier.screening"].create(
        {
            "supplier_id": supplier.id,
            "screening_type": "sanctions",
            "result": "hit",
        }
    )
    with pytest.raises(UserError, match="cannot be cleared"), env.cr.savepoint():
        hit.action_clear()
    clear = env["fix.supplier.screening"].create(
        {"supplier_id": supplier.id, "screening_type": "coi", "result": "clear"}
    )
    clear.action_clear()
    assert clear.state == "cleared"
