"""A05 ERP audit (20 Nov 2026): the M13 rental report packs and KPIs.

XC-11 Dhaka 'today'; XC-16 utilisation from hand-over to actual return over
days available (retired / lost units are not capacity); XC-17 Rental P&L by
category from invoices, recovered damage added, depreciation subtracted;
XC-23 the caller's OU fence and the gated KPI route; XC-25/27 the late-fee
policy shown as the parameter in force, deposits held per the GL (a queued
refund is still held); XC-18 the spec reports (overdue, zero-target controls).
"""

import datetime
from datetime import timedelta
from types import SimpleNamespace

import pytest
from freezegun import freeze_time
from odoo.addons.cd_p03_portal.controllers import a05
from odoo.addons.cd_p03_portal.controllers.a05 import m13
from odoo.addons.cd_p03_portal.tests.a05erp_helpers import (
    SEQ,
    branch,
    dhaka_noon_utc,
    other_ou,
    row_of,
    set_cols,
    track,
    user,
)


@pytest.fixture
def r(odoo_env):
    env = odoo_env
    if "fix.rental.reservation" not in env:
        pytest.skip("cd_rental_asset not installed")
    x = SimpleNamespace(env=env)
    x.today = m13.dhaka_today(env)
    x.branch = branch(env)
    x.ou = x.branch.operating_unit_id
    x.ou2 = other_ou(env, x.ou)
    i = next(SEQ)
    x.customer = env["res.partner"].create(
        {"name": "A05ERP M13 Customer %d" % i, "phone": "0171300%04d" % i}
    )
    tmpl = env["product.template"].create({"name": "A05ERP M13 Medical %d" % i})
    item = env["fix.catalogue.item"].create({"product_tmpl_id": tmpl.id})
    x.sku = env["fix.rental.sku"].create(
        {"catalogue_item_id": item.id, "daily_rate": 1000, "security_deposit": 5000}
    )

    def asset(category="medical", ou=None, **kw):
        vals = {
            "name": "A05ERP-U-%d" % next(SEQ),
            "rental_sku_id": x.sku.id,
            "serial_no": "A05ERP-SN-%d" % next(SEQ),
            "category": category,
            "purchase_cost": 365000,
            "acquisition_date": x.today - timedelta(days=400),
            "operating_unit_id": (ou or x.ou).id,
        }
        vals.update(kw)
        return env["fix.rental.asset"].create(vals)

    def res(unit, d_from, d_to, ou=None, state=None, **cols):
        rec = env["fix.rental.reservation"].create(
            {
                "customer_id": x.customer.id,
                "rental_sku_id": x.sku.id,
                "rental_asset_id": unit.id if unit else False,
                "operating_unit_id": (ou or x.ou).id,
                "branch_id": x.branch.id if not ou or ou == x.ou else False,
                "date_from": d_from,
                "date_to": d_to,
            }
        )
        if state:
            cols["state"] = state
        if cols:
            set_cols(rec, **cols)
        return rec

    x.asset, x.res = asset, res
    return x


def _medical(pack):
    """The Medical Device row of a pack, or zeros (the category had no row)."""
    row = row_of(pack, "category", "Medical Device")
    if row:
        return row
    return dict.fromkeys(
        (
            "available_days",
            "rented_days",
            "assets",
            "revenue",
            "recovered",
            "damage",
            "depreciation",
            "loss",
            "gross_margin",
        ),
        0,
    )


def test_today_is_the_dhaka_business_day(odoo_env):
    # 20:00 UTC on 20 Nov is 02:00 on 21 Nov in Dhaka
    with freeze_time("2026-11-20 20:00:00"):
        assert m13.dhaka_today(odoo_env) == datetime.date(2026, 11, 21)
        start, end = m13.window(odoo_env)
        assert end == datetime.date(2026, 11, 21) and start == datetime.date(2026, 10, 23)


def test_utilisation_is_handover_to_return_over_days_available(r):
    start, end = r.today - timedelta(days=29), r.today
    before = _medical(m13.utilisation_by_category(r.env, str(start), str(end)))
    live = r.asset()
    retired = r.asset(retired_on=r.today - timedelta(days=60))
    set_cols(retired, status="retired")
    # booked from day -25, handed over on day -20, returned on day -11: 10 days on rent
    out = r.res(live, r.today - timedelta(days=25), r.today - timedelta(days=11))
    set_cols(out, state="returned", actual_return_date=r.today - timedelta(days=11))
    track(out, "delivered", r.today - timedelta(days=20))
    # a reservation never handed over earns no rent-day
    r.res(live, r.today - timedelta(days=5), r.today + timedelta(days=2), state="reserved")
    after = _medical(m13.utilisation_by_category(r.env, str(start), str(end)))
    assert after["available_days"] - before["available_days"] == 30  # the retired unit adds none
    assert after["rented_days"] - before["rented_days"] == 10
    assert after["assets"] - before["assets"] == 1


def test_rental_pl_is_by_category_from_invoices_with_recovery_and_depreciation(r):
    env = r.env
    start, end = r.today - timedelta(days=29), r.today
    before = _medical(m13.rental_pl(env, str(start), str(end)))
    unit = r.asset(useful_life_days=3650, residual_value=0)
    res = r.res(unit, r.today - timedelta(days=20), r.today - timedelta(days=6), daily_rate=1000)
    set_cols(
        res, state="closed", actual_return_date=r.today - timedelta(days=6), rental_charge=15000
    )
    invoice = env["fix.ar.invoice"].create(
        {
            "company_id": env.company.id,
            "customer_id": r.customer.id,
            "operating_unit_id": r.ou.id,
            "source_model": "fix.rental.reservation",
            "source_id": res.id,
            "invoice_date": r.today - timedelta(days=5),
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "description": "Rental",
                        "quantity": 1,
                        "unit_price": 10000,
                        "taxable_amount": 10000,
                        "vat_amount": 1500,
                        "line_total": 11500,
                    },
                )
            ],
        }
    )
    set_cols(invoice, state="issued", taxable_amount=10000, vat_amount=1500, total_payable=11500)
    env.cr.execute(
        """INSERT INTO fix_rental_deposit (name, company_id, reservation_id, customer_id, kind,
               amount, currency_id, method, date, gl_state)
           VALUES ('A05ERP-DED', %s, %s, %s, 'deduction', 2000, %s, 'cash', %s, 'posted')""",
        [
            env.company.id,
            res.id,
            r.customer.id,
            env.ref("base.BDT").id,
            r.today - timedelta(days=4),
        ],
    )
    env["fix.rental.damage"].create(
        {
            "reservation_id": res.id,
            "description": "Cracked probe",
            "cost": 3000,
            "incident_date": r.today - timedelta(days=6),
        }
    )
    env.invalidate_all()
    after = _medical(m13.rental_pl(env, str(start), str(end)))
    assert (
        round(after["revenue"] - before["revenue"], 2) == 10000.0
    )  # invoiced, not the 15,000 contracted
    assert round(after["recovered"] - before["recovered"], 2) == 2000.0
    assert round(after["damage"] - before["damage"], 2) == 3000.0
    dep = round(unit.daily_depreciation * 30, 2)
    assert dep > 0
    assert round(after["depreciation"] - before["depreciation"], 2) == dep
    gross = round(after["gross_margin"] - before["gross_margin"], 2)
    assert gross == round(10000 + 2000 - 3000 - dep, 2)


def test_deposits_held_count_a_queued_refund_as_still_held(r):
    env = r.env
    held_before = m13.kpis(env)["deposits_held"]
    res = r.res(
        r.asset(), r.today - timedelta(days=10), r.today - timedelta(days=3), state="closed"
    )
    for kind, state in (("collect", "posted"), ("refund", "refund_queued")):
        env.cr.execute(
            """INSERT INTO fix_rental_deposit (name, company_id, reservation_id, customer_id,
                   kind, amount, currency_id, method, date, gl_state)
               VALUES (%s, %s, %s, %s, %s, 5000, %s, 'cash', %s, %s)""",
            [
                "A05ERP-%s" % kind,
                env.company.id,
                res.id,
                r.customer.id,
                kind,
                env.ref("base.BDT").id,
                r.today - timedelta(days=3),
                state,
            ],
        )
    env.invalidate_all()
    assert round(m13.kpis(env)["deposits_held"] - held_before, 2) == 5000.0


def test_late_return_note_shows_the_policy_parameter_in_force(r):
    r.env["ir.config_parameter"].sudo().set_param("cd_rental_asset.late_fee_multiplier", "2.25")
    pack = m13.late_return(r.env)
    assert any("late_fee_multiplier = 2.25 x" in note for note in pack["notes"]), pack["notes"]
    assert not any("1.5×" in note for note in pack["notes"])


def test_reports_read_only_the_callers_operating_unit(r):
    env = r.env
    mine = r.res(r.asset(), r.today - timedelta(days=12), r.today - timedelta(days=8))
    set_cols(mine, state="closed", actual_return_date=r.today - timedelta(days=5))
    theirs = r.res(
        r.asset(ou=r.ou2), r.today - timedelta(days=12), r.today - timedelta(days=8), ou=r.ou2
    )
    set_cols(theirs, state="closed", actual_return_date=r.today - timedelta(days=5))
    clerk = user(env, "m13clerk", ou=r.ou, modules=("cd_rental_asset",))
    names = {row["rental"] for row in m13.late_return(env(user=clerk.id))["rows"]}
    assert mine.name in names
    assert theirs.name not in names


def test_overdue_report_bands_units_still_out(r):
    out = r.res(
        r.asset(), r.today - timedelta(days=10), r.today - timedelta(days=3), state="active"
    )
    row = row_of(m13.overdue_recovery(r.env), "rental", out.name)
    assert row and row["days_overdue"] == 3 and row["age_band"] == "1–3 days"


def test_zero_target_control_flags_a_dispatch_without_a_condition_report(r):
    out = r.res(r.asset(), r.today - timedelta(days=4), r.today + timedelta(days=3), state="active")
    track(out, "delivered", r.today - timedelta(days=4))
    pack = m13.zero_target_controls(r.env)
    row = row_of(pack, "control", "Dispatches without a complete condition report")
    assert row["status"] == "BREACH" and out.name in row["examples"]


def test_circular_kpis_are_gated_by_the_module_permission(r):
    env = r.env
    clerk = user(env, "m13kpi", ou=r.ou, modules=("cd_rental_asset",))
    payload = a05.gated_kpis(env(user=clerk.id), "M13")
    assert "M13" in payload and "error" not in payload
    env["fix.module.permission"].sudo().create(
        {"user_id": clerk.id, "module_code": "M13", "module_name": "M13 Rental", "level": "none"}
    )
    refused = a05.gated_kpis(env(user=clerk.id), "M13")
    assert "error" in refused and "M13" not in refused


def test_dhaka_noon_helper_is_midday_dhaka():
    assert dhaka_noon_utc(datetime.date(2026, 11, 20)) == datetime.datetime(2026, 11, 20, 6, 0)
