"""A05 ERP audit (20 Nov 2026): the M14 trade-in report packs and KPIs.

XC-12 / M14-24 every pack honours the period (a sale is the stock unit SOLD,
on the day it was sold); XC-13 gross margin on the resale price; XC-14 stock
value = in stock + reserved, ageing = in stock only; XC-25 the markdown ladder
is configuration shown in force; XC-18 the zero-target gate compliance.
"""

from datetime import timedelta
from types import SimpleNamespace

import pytest
from odoo.addons.cd_p03_portal.controllers.a05 import m13, m14
from odoo.addons.cd_p03_portal.tests.a05erp_helpers import SEQ, branch, row_of, set_cols, track


@pytest.fixture
def t(odoo_env):
    env = odoo_env
    if "fix.tradein.request" not in env or "fix.graded.stock" not in env:
        pytest.skip("cd_tradein / cd_inventory not installed")
    x = SimpleNamespace(env=env)
    x.today = m13.dhaka_today(env)
    i = next(SEQ)
    brand = env["fix.brand"].create({"name": "A05ERP Brand %d" % i, "code": "A5EB%d" % i})
    x.model = env["fix.device.model"].create({"name": "A05ERP Phone %d" % i, "brand_id": brand.id})
    x.customer = env["res.partner"].create({"name": "A05ERP Seller %d" % i})
    x.ou = branch(env).operating_unit_id
    x.grade = env["fix.refurb.grade"].search([], limit=1)
    assert x.grade, "the refurb grade master is seeded"

    def tradein(**cols):
        req = env["fix.tradein.request"].create(
            {
                "customer_id": x.customer.id,
                "device_id": env["fix.device"].create({"device_model_id": x.model.id}).id,
                "device_model_id": x.model.id,
                "offered_value": 5000,
                "operating_unit_id": x.ou.id,
            }
        )
        if cols:
            set_cols(req, **cols)
        return req

    def unit(req, cost, price, state="in_stock", since=None):
        device = env["fix.device"].create({"device_model_id": x.model.id})
        stock = env["fix.graded.stock"].create(
            {
                "device_id": device.id,
                "grade_id": x.grade.id,
                "tradein_id": req.id if req else 0,
                "acquisition_cost": cost,
                "refurbishment_cost": 0.0,
                "resale_price": price,
            }
        )
        set_cols(stock, state=state, inventory_valuation=cost)
        if since:
            track(stock, "in_stock", since)
        return stock

    x.tradein, x.unit = tradein, unit
    return x


def _sell(t, req, cost, price, day):
    stock = t.unit(req, cost, price, state="sold")
    track(stock, "sold", day)
    set_cols(
        req, state="closed", graded_stock_id=stock.id, resale_value=price, inventory_valuation=cost
    )
    return stock


def test_margin_is_on_the_resale_price_for_units_sold_in_the_period(t):
    start, end = t.today - timedelta(days=29), t.today
    req = t.tradein()
    _sell(t, req, 8000, 10000, t.today - timedelta(days=3))
    old = t.tradein()
    _sell(t, old, 1000, 9000, t.today - timedelta(days=60))  # outside the period
    pack = m14.tradein_margin(t.env, str(start), str(end))
    row = row_of(pack, "model", t.model.name)
    assert row["units"] == 1
    assert row["margin"] == 2000.0
    assert row["margin_pct"] == 20.0  # on the price, not 25% mark-up on cost
    econ = {r["tradein"] for r in m14.unit_economics(t.env, str(start), str(end))["rows"]}
    assert req.name in econ and old.name not in econ


def test_stock_value_counts_units_held_and_ageing_units_in_stock(t):
    env = t.env
    before = m14.kpis(env)["graded_stock_value"]
    in_stock = t.unit(t.tradein(), 1000, 1500, "in_stock", since=t.today - timedelta(days=40))
    t.unit(t.tradein(), 2000, 2500, "reserved")
    sold = t.unit(t.tradein(), 4000, 4500, "sold")
    scrapped = t.unit(t.tradein(), 8000, 8500, "scrapped")
    assert round(m14.kpis(env)["graded_stock_value"] - before, 2) == 3000.0
    names = {r["stock"] for r in m14.ageing_markdown(env)["rows"]}
    assert in_stock.name in names
    assert sold.name not in names and scrapped.name not in names
    row = row_of(m14.ageing_markdown(env), "stock", in_stock.name)
    assert row["age_days"] == 40


def test_markdown_ladder_is_the_configured_parameter(t):
    params = t.env["ir.config_parameter"].sudo()
    params.set_param("cd_tradein.markdown_after_days_1", "30")
    params.set_param("cd_tradein.markdown_pct_1", "5")
    unit = t.unit(t.tradein(), 1000, 1000, "in_stock", since=t.today - timedelta(days=40))
    pack = m14.ageing_markdown(t.env)
    row = row_of(pack, "stock", unit.name)
    assert row["suggested_markdown_pct"] == 5.0
    assert row["nrv"] == 950.0 and row["nrv_test"].startswith("BELOW COST")
    assert any("after 30 days 5%" in note for note in pack["notes"]), pack["notes"]


def test_gate_compliance_flags_a_unit_processed_without_a_certificate(t):
    req = t.tradein(state="refurbished")
    pack = m14.gate_compliance(t.env)
    row = row_of(pack, "control", "Units processed without a destruction / wipe certificate")
    assert row["status"] == "BREACH" and req.name in row["examples"]


def test_valuation_queue_honours_the_period(t):
    if "fix.tradein.valuation" not in t.env:
        pytest.skip("valuation not installed")
    req = t.tradein()
    old = t.env["fix.tradein.valuation"].create(
        {"tradein_id": req.id, "device_model_id": t.model.id, "market_ref_price": 1000}
    )
    set_cols(old, valuated_on=t.today - timedelta(days=200))
    pack = m14.valuation_queue(t.env, str(t.today - timedelta(days=30)), str(t.today))
    assert req.name not in {r["tradein"] for r in pack["rows"]}
    recent = m14.valuation_queue(t.env, str(t.today - timedelta(days=210)), str(t.today))
    assert req.name in {r["tradein"] for r in recent["rows"]}
