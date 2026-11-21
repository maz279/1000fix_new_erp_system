# A06 ERP audit (20 Nov 2026), stream P2P: the M16 / M42 report basis.
#
# P25 / X31: spend, maverick and price reports added drafts, cancellations and
# superseded originals, mixed USD with BDT and ignored the period. P26: the
# "match exceptions" KPI counted order lines awaiting delivery. P34: contract
# coverage counted suppliers, not spend. Rolled back.
from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers.a06 import m16, m42


def _rate(env, currency, day, bdt_per_unit):
    Rate = env["res.currency.rate"]
    Rate.search(
        [("currency_id", "=", currency.id), ("name", "=", day), ("company_id", "=", env.company.id)]
    ).unlink()
    Rate.create(
        {
            "currency_id": currency.id,
            "name": day,
            "company_id": env.company.id,
            "rate": 1.0 / bdt_per_unit,
        }
    )


@pytest.fixture
def r(odoo_env):
    env = odoo_env
    today = fields.Date.context_today(env.user)
    usd = (
        env.ref("base.BDT")
        if env.company.currency_id == env.ref("base.USD")
        else env.ref("base.USD")
    )
    usd.active = True
    _rate(env, usd, today, 120.0)
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    categ = env["product.category"].create({"name": "P2P RPT Category"})
    product = env["product.product"].create({"name": "P2P RPT Part", "categ_id": categ.id})
    vendor = env["res.partner"].create({"name": "P2P RPT Vendor", "is_company": True})
    sup = env["fix.supplier"].create(
        {"name": vendor.name, "partner_id": vendor.id, "status": "active"}
    )
    Order = env["fix.purchase.order"]

    def order(state, price, currency=None, rate=0.0, **kw):
        po = Order.create(
            {
                "operating_unit_id": ou.id,
                "vendor_id": vendor.id,
                "currency_id": (currency or env.company.currency_id).id,
                "line_ids": [
                    (0, 0, {"product_id": product.id, "qty_ordered": 1, "unit_price": price})
                ],
                **kw,
            }
        )
        po._guarded().write({"state": state, "fx_rate": rate})
        return po

    return {
        "env": env,
        "today": today,
        "usd": usd,
        "categ": categ,
        "vendor": vendor,
        "sup": sup,
        "order": order,
    }


def _spend(pack, vendor):
    return sum(row["amount"] for row in pack["rows"] if row["vendor"] == vendor.name)


def test_p25_spend_is_issued_orders_in_bdt_within_the_period(r):
    """Mutations: state != cancelled only -> drafts and superseded counted;
    line_total raw -> USD 100 counted as 100; no period -> last year's order."""
    env, order = r["env"], r["order"]
    order("sent", 1000.0)
    order("sent", 100.0, currency=r["usd"], rate=110.0)  # stamped at 110: BDT 11,000
    order("draft", 5000.0)
    order("cancelled", 7000.0)
    order("superseded", 9000.0)
    old = order("closed", 3000.0)
    old._guarded().write({"date_order": fields.Datetime.now() - timedelta(days=400)})
    since = r["today"] - timedelta(days=30)
    pack = m16.spend_by_category(env, date_from=str(since), date_to=str(r["today"]))
    assert _spend(pack, r["vendor"]) == 12000.0
    assert _spend(m16.spend_by_category(env), r["vendor"]) == 15000.0
    mav = m16.maverick_spend(env, date_from=str(since), date_to=str(r["today"]))
    assert sum(row["amount"] for row in mav["rows"] if row["vendor"] == r["vendor"].name) == 12000.0


def test_p26_match_exceptions_are_blocked_bills(r):
    """Mutation: the KPI counts undelivered order lines -> 1 for the sent order
    that awaits delivery and no bill at all."""
    env, order = r["env"], r["order"]
    before = m16.kpis(env)["match_exceptions"]
    po = order("sent", 1000.0)
    assert m16.kpis(env)["match_exceptions"] == before
    env["fix.vendor.invoice"].create(
        {
            "vendor_id": r["vendor"].id,
            "invoice_ref": "P2P-RPT-1",
            "requisition_id": po.id,
            "operating_unit_id": po.operating_unit_id.id,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": po.line_ids.product_id.id,
                        "description": "Part",
                        "quantity": 1,
                        "unit_price": 1000.0,
                        "tds_category": "supply_of_goods",
                    },
                )
            ],
        }
    )
    assert m16.kpis(env)["match_exceptions"] == before + 1
    rows = m16.match_exception(env)["rows"]
    assert any(row["bill"] == "P2P-RPT-1" for row in rows)


def test_p34_contract_coverage_is_measured_by_spend(r):
    env, order = r["env"], r["order"]
    order("sent", 100.0, currency=r["usd"], rate=120.0)
    pack = m42.contract_coverage(env)
    row = next(row for row in pack["rows"] if row["supplier"] == r["sup"].name)
    assert (row["contract"], row["spend"]) == ("no", 12000.0)
    assert "Coverage by spend" in pack["notes"][0]
