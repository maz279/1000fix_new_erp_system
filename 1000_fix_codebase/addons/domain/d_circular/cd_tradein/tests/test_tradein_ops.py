"""cd_tradein_ops behaviour (live ORM, rolled back): the M14 workspace records —
valuation engine, provenance screen, grading result, QA, harvest and warranty."""

from __future__ import annotations

from datetime import date

import pytest
from odoo.exceptions import UserError, ValidationError
from psycopg2 import IntegrityError


def _customer(env):
    return env["res.partner"].create({"name": "M14 Ops Customer"})


def _request(env, **vals):
    vals.setdefault("customer_id", _customer(env).id)
    vals.setdefault("offered_value", 30000)
    return env["fix.tradein.request"].create(vals)


def test_valuation_computes_and_applies(odoo_env):
    env = odoo_env
    request = _request(env)
    val = env["fix.tradein.valuation"].create(
        {
            "tradein_id": request.id,
            "market_ref_price": 60000,
            "age_months": 24,
            "age_factor_pct": 70,
            "condition_factor_pct": 75,
        }
    )
    assert val.computed_offer == pytest.approx(31500.0)
    assert val.name.startswith("TVAL/")
    val.action_apply_to_tradein()
    assert request.offered_value == pytest.approx(31500.0)
    assert val.state == "applied"
    with pytest.raises(UserError, match="already been applied"), env.cr.savepoint():
        val.action_apply_to_tradein()


def test_valuation_manual_override_needs_reason(odoo_env):
    env = odoo_env
    request = _request(env)
    val = env["fix.tradein.valuation"].create(
        {
            "tradein_id": request.id,
            "market_ref_price": 50000,
            "age_factor_pct": 80,
            "condition_factor_pct": 80,
            "final_offer": 28000,
            "method": "manual",
        }
    )
    with pytest.raises(UserError, match="state its reason"), env.cr.savepoint():
        val.action_apply_to_tradein()
    val.override_reason = "Cracked frame disclosed at intake"
    val.action_apply_to_tradein()
    assert request.offered_value == pytest.approx(28000.0)


def test_valuation_refuses_after_acceptance(odoo_env):
    env = odoo_env
    request = _request(env, state="accepted")
    val = env["fix.tradein.valuation"].create(
        {
            "tradein_id": request.id,
            "market_ref_price": 10000,
            "age_factor_pct": 100,
            "condition_factor_pct": 100,
        }
    )
    with pytest.raises(UserError, match="before the offer is accepted"), env.cr.savepoint():
        val.action_apply_to_tradein()


def test_provenance_clear_rules(odoo_env):
    env = odoo_env
    request = _request(env)
    prov = env["fix.tradein.provenance"].create(
        {"tradein_id": request.id, "imei": "356789012345671"}
    )
    with pytest.raises(UserError, match="before clearing"), env.cr.savepoint():
        prov.action_clear()
    prov.write({"blacklist_checked": True, "stolen_checked": True, "stolen_hit": True})
    with pytest.raises(UserError, match="cannot be cleared"), env.cr.savepoint():
        prov.action_clear()
    prov.stolen_hit = False
    prov.action_clear()
    assert prov.state == "cleared"


def test_provenance_imei_is_15_digits(odoo_env):
    env = odoo_env
    request = _request(env)
    with pytest.raises(ValidationError, match="15 digits"), env.cr.savepoint():
        env["fix.tradein.provenance"].create({"tradein_id": request.id, "imei": "12345"})


def test_grading_aligns_the_request(odoo_env):
    env = odoo_env
    request = _request(env, state="refurbished")
    grade = env["fix.tradein.grade"].create(
        {
            "tradein_id": request.id,
            "grade": "c",
            "battery_health_pct": 72,
            "graded_on": date(2026, 10, 28),
        }
    )
    assert grade.name.startswith("TGRD/")
    assert request.grade == "c"
    assert request.battery_health_pct == 72


def test_qa_pass_percentage(odoo_env):
    env = odoo_env
    request = _request(env, state="refurbished")
    qa = env["fix.refurb.qa"].create(
        {
            "tradein_id": request.id,
            "tests_total": 12,
            "tests_passed": 9,
            "qa_state": "fail",
        }
    )
    assert qa.pass_pct == pytest.approx(75.0)
    assert qa.name.startswith("RQA/")
    with pytest.raises(IntegrityError), env.cr.savepoint():
        qa.tests_passed = 13


def test_harvest_total_and_quantity(odoo_env):
    env = odoo_env
    request = _request(env)
    line = env["fix.tradein.harvest"].create(
        {
            "tradein_id": request.id,
            "component": "screen",
            "quantity": 2,
            "unit_value": 1500,
            "target": "spare_stock",
        }
    )
    assert line.total_value == pytest.approx(3000.0)
    assert line.name.startswith("HARV/")
    with pytest.raises(IntegrityError), env.cr.savepoint():
        line.quantity = 0


def test_warranty_end_date(odoo_env):
    env = odoo_env
    request = _request(env)
    warranty = env["fix.tradein.warranty"].create(
        {"tradein_id": request.id, "months": 6, "start_date": date(2026, 10, 28)}
    )
    assert warranty.end_date == date(2027, 4, 28)
    assert warranty.name.startswith("TWAR/")
