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
    # A05 ERP M14-23: a trade-in is taken in at an operating unit
    vals.setdefault(
        "operating_unit_id",
        env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1).id,
    )
    return env["fix.tradein.request"].create(vals)


def _model(env):
    brand = env["fix.brand"].create({"name": "M14 Ops Brand", "code": "M14OPS"})
    return env["fix.device.model"].create({"name": "M14 Ops Phone", "brand_id": brand.id})


def _valued_request(env, price):
    """A request on a device model with an approved grid price (P2: the
    valuation prices from the governed grid, not a typed market price)."""
    model = _model(env)
    device = env["fix.device"].create({"device_model_id": model.id, "serial_number": "M14-OPS-1"})
    grid = env["fix.tradein.price.grid"].create(
        {"device_model_id": model.id, "market_ref_price": price}
    )
    grid.action_approve()
    return _request(env, device_id=device.id)


def test_valuation_computes_and_applies(odoo_env):
    env = odoo_env
    request = _valued_request(env, 60000)
    val = env["fix.tradein.valuation"].create(
        {
            "tradein_id": request.id,
            "market_ref_price": 60000,
            "resale_estimate": 70000,
            "age_months": 24,
            "age_factor_pct": 70,
            "condition_factor_pct": 75,
        }
    )
    assert val.computed_offer == pytest.approx(31500.0)
    assert val.name.startswith("TVAL/")
    assert not val.is_override
    val.action_apply_to_tradein()
    assert request.offered_value == pytest.approx(31500.0)
    assert val.state == "applied"
    with pytest.raises(UserError, match="already been applied"), env.cr.savepoint():
        val.action_apply_to_tradein()


def test_valuation_manual_override_needs_reason_and_approval(odoo_env):
    env = odoo_env
    request = _request(env)
    val = env["fix.tradein.valuation"].create(
        {
            "tradein_id": request.id,
            "market_ref_price": 50000,
            "age_factor_pct": 80,
            "condition_factor_pct": 80,
            "final_offer": 28000,
            "resale_estimate": 56000,
            "method": "manual",
        }
    )
    with pytest.raises(UserError, match="state its reason"), env.cr.savepoint():
        val.action_apply_to_tradein()
    val.override_reason = "Cracked frame disclosed at intake"
    # P2: an override is approved by a valuation manager before it applies
    with pytest.raises(UserError, match="approves it before it is applied"), env.cr.savepoint():
        val.action_apply_to_tradein()
    val.action_request_override_approval()
    val.action_approve_override()
    val.action_apply_to_tradein()
    assert request.offered_value == pytest.approx(28000.0)


def test_valuation_refuses_after_acceptance(odoo_env):
    env = odoo_env
    request = _request(env, state="accepted")
    val = env["fix.tradein.valuation"].create(
        {
            "tradein_id": request.id,
            "market_ref_price": 10000,
            "resale_estimate": 20000,
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
    prov.write({"evidence_ref": "GSMA lookup 1", "lock_status": "off"})
    # A05 audit M14-5/6: a stolen hit flags the screen, and a flagged screen
    # is a hard stop that is never cleared (lowering the hit does not undo it)
    prov.write({"stolen_hit": True})
    assert prov.state == "flagged"
    with pytest.raises(UserError, match="cannot be cleared"), env.cr.savepoint():
        prov.action_clear()
    prov.stolen_hit = False
    with pytest.raises(UserError, match="flagged"), env.cr.savepoint():
        prov.action_clear()
    clean = env["fix.tradein.provenance"].create(
        {
            "tradein_id": _request(env).id,
            "imei": "356789012345672",
            "evidence_ref": "GSMA lookup 2",
            "lock_status": "off",
        }
    )
    clean.action_clear()
    assert clean.state == "cleared"
    assert (clean.blacklist_checked, clean.stolen_checked) == (True, True)
    assert clean.btrc_neir_status == "unchecked"  # no NEIR lookup exists


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
