"""A06 ERP audit (20 Nov 2026) - M43 findings M43-01..21 and owner decision D7.

Each test drives the ORM inside the rolled-back odoo_env transaction and was
written to fail on the code before the fix (the defect reproduced), then pass
on the fixed code. Fixtures: conftest.M43.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from math import sqrt
from statistics import NormalDist

import pytest
from odoo.addons.cd_demand_plan.models import fix_demand_common as common
from odoo.exceptions import UserError, ValidationError


def _z(level):
    return NormalDist().inv_cdf(level / 100.0)


def _approve(m43, plan):
    plan.with_user(m43.approver).action_approve()
    return plan


# ------------------------------------------------------------- M43-01 / M43-08
def test_erp_m43_01_safety_stock_carries_lead_time_variability(m43):
    """SS = z x sqrt(L sd^2 + d^2 sL^2): a supplier whose lead time varies by
    3 days needs more buffer than the demand deviation alone gives."""
    pol = m43.policy(2.0, 1.0, 9, lead_time_stddev_days=3.0)
    expected = round(_z(95) * sqrt(9 * 1.0**2 + 2.0**2 * 3.0**2), 2)
    assert pol.safety_stock == pytest.approx(expected, abs=0.01)
    # the old z*sd*sqrt(L) = 4.95 is well below
    assert pol.safety_stock > 10.0
    assert pol.reorder_point == pytest.approx(round(2.0 * 9 + expected, 2), abs=0.01)


def test_erp_m43_08_any_service_level_by_inverse_normal(m43):
    """85% (owner item 9) is honoured with its own z, not silently 95%."""
    pol = m43.policy(2.0, 2.0, 4, service=85.0)
    assert pol.safety_stock == pytest.approx(round(_z(85) * 2.0 * 2.0, 2), abs=0.01)
    pol97 = m43.policy(2.0, 2.0, 4, service=97.5, loc=m43.loc2)
    assert pol97.safety_stock == pytest.approx(round(_z(97.5) * 2.0 * 2.0, 2), abs=0.01)
    with pytest.raises(ValidationError), m43.env.cr.savepoint():
        m43.policy(2.0, 2.0, 4, service=100.0, loc=m43.location("C"))
    assert common.z_for(95) == pytest.approx(1.6449, abs=1e-4)


# ------------------------------------------------------------- M43-14
def test_erp_m43_14_policy_uses_the_supplier_lead_time_model(m43):
    """The policy's supplier has a measured lead-time model (mean 20, sd 4):
    the refresh takes both from it instead of pooling every supplier."""
    model = m43.env["fix.demand.lead.time"].create(
        {
            "product_id": m43.prod.id,
            "vendor_id": m43.vendor.id,
            "quoted_days": 14,
            "state": "measured",
            "sample_count": 6,
            "mean_days": 20.0,
            "std_dev_days": 4.0,
        }
    )
    pol = m43.env["fix.demand.policy"].create(
        {
            "product_id": m43.prod.id,
            "part_id": m43.part.id,
            "location_id": m43.loc.id,
            "vendor_id": m43.vendor.id,
            "lead_time_days": 7,
        }
    )
    pol.with_user(m43.planner).action_refresh_from_history()
    assert pol.lead_time_model_id == model
    assert pol.lead_time_days == 20
    assert pol.lead_time_stddev_days == pytest.approx(4.0)
    assert pol.lead_time_source == "supplier"


# ------------------------------------------------------------- M43-07
def test_erp_m43_07_position_counts_unrestricted_stock_only(m43):
    m43.stock(5.0)
    m43.stock(40.0, ownership="owned").sudo().write({"stock_status": "quarantine"})
    assert common.on_hand(m43.env, m43.company, m43.part, m43.loc) == pytest.approx(5.0)


# ------------------------------------------------------------- M43-05
def test_erp_m43_05_on_order_is_netted_per_location(m43):
    """Another branch's requisition is not this location's stock on order; a
    transfer dispatched to it and an import receiving at it are."""
    other_branch = m43.env["fix.branch"].create(
        {
            "code": ("O%s" % m43.tag)[:10],
            "name": "M43 other branch %s" % m43.tag,
            "entity_id": m43.branch.entity_id.id,
            "operating_unit_id": m43.ou.id,
        }
    )
    emp = m43.env["hr.employee"].search([("user_id", "=", m43.planner.id)], limit=1)
    m43.env["fix.requisition"].create(
        {
            "description": "elsewhere",
            "product_id": m43.prod.id,
            "qty": 50,
            "estimate_amount": 100,
            "requested_by": emp.id,
            "operating_unit_id": m43.ou.id,
            "branch_id": other_branch.id,
        }
    )
    products = m43.prod
    assert common.on_order(m43.env, m43.company, products, m43.loc, m43.part) == 0.0
    # company-wide (no location) it is on order
    assert common.on_order(m43.env, m43.company, products) == pytest.approx(50.0)
    m43.env["fix.requisition"].create(
        {
            "description": "here",
            "product_id": m43.prod.id,
            "qty": 7,
            "estimate_amount": 100,
            "requested_by": emp.id,
            "operating_unit_id": m43.ou.id,
            "branch_id": m43.branch.id,
        }
    )
    assert common.on_order(m43.env, m43.company, products, m43.loc, m43.part) == pytest.approx(7.0)
    if "fix.import.order" in m43.env:
        m43.env["fix.import.order"].create(
            {
                "name": "M43-IMP-%s" % m43.tag,
                "operating_unit_id": m43.ou.id,
                "location_id": m43.loc.id,
                "currency_id": m43.env.ref("base.BDT").id,
                "line_ids": [(0, 0, {"part_id": m43.part.id, "quantity": 12, "unit_price": 10})],
            }
        )
        assert common.on_order(m43.env, m43.company, products, m43.loc, m43.part) == pytest.approx(
            19.0
        )


# ------------------------------------------------------------- M43-06
def test_erp_m43_06_order_compares_inventory_position_with_rop(m43):
    """ROP 20 (2/day x 10 days), target 80. Stock 25 is above the ROP: no
    order, although the month's forecast is 30 (the ROP already holds the
    lead-time demand; subtracting the forecast ordered ~1 extra period)."""
    plan = m43.ready_plan(forecast=30.0, stock=25.0, avg=2.0, lead=10)
    assert plan.reorder_point == pytest.approx(20.0)
    assert plan.inventory_position == pytest.approx(25.0)
    assert plan.recommended_order == 0.0
    with pytest.raises(UserError, match="inventory position"):
        plan.with_user(m43.approver).action_approve()
    m43.env["fix.stock.onhand"].search([("part_id", "=", m43.part.id)]).sudo().write({"qty": 15})
    plan.invalidate_recordset()
    assert plan.recommended_order == pytest.approx(80.0 - 15.0)


# ------------------------------------------------------------- M43-02 / D7
def test_erp_m43_02_release_publishes_min_max_and_m15_raises_the_document(m43):
    """One engine: the plan raises no requisition of its own. Release
    publishes the approved ROP/target to the M15 rule and M15's sweep raises
    the (single) requisition, linked back to the plan."""
    plan = m43.ready_plan(forecast=10.0, stock=5.0, avg=2.0, lead=10)
    _approve(m43, plan)
    before = m43.env["fix.requisition"].sudo().search_count([("product_id", "=", m43.prod.id)])
    plan.with_user(m43.planner).action_generate_pr()
    rule = (
        m43.env["fix.reorder.rule"]
        .sudo()
        .search([("spare_part_id", "=", m43.part.id), ("location_id", "=", m43.loc.id)])
    )
    assert len(rule) == 1
    assert rule.min_qty == pytest.approx(plan.approved_reorder_point)
    assert rule.max_qty == pytest.approx(plan.approved_target_level)
    assert rule.plan_source_ref == plan.name
    reqs = m43.env["fix.requisition"].sudo().search([("product_id", "=", m43.prod.id)])
    assert len(reqs) - before == 1, "exactly one replenishment document"
    req = reqs.sorted("id")[-1]
    assert req == rule.requisition_id, "raised by M15's rule, not by M43"
    assert not (req.description or "").startswith("Planned order")
    assert plan.state == "released" and plan.sudo().pr_requisition_id == req
    assert req.demand_plan_id == plan


# ------------------------------------------------------------- M43-04 / M43-15
def test_erp_m43_04_last_po_price_is_converted_to_bdt(m43):
    usd = m43.env.ref("base.USD")
    usd.sudo().active = True
    po = m43.env["fix.purchase.order"].create(
        {
            "operating_unit_id": m43.ou.id,
            "vendor_id": m43.vendor.id,
            "currency_id": usd.id,
            "line_ids": [(0, 0, {"product_id": m43.prod.id, "qty_ordered": 1, "unit_price": 10})],
        }
    )
    m43.env["res.currency.rate"].create(
        {
            "currency_id": usd.id,
            "name": po.date_order.date() - timedelta(days=1),
            "company_id": m43.company.id,
            "inverse_company_rate": 120.0,
        }
    )
    plan = m43.ready_plan()
    price, _vendor = plan._pr_price_and_vendor(m43.prod)
    if m43.company.currency_id == m43.env.ref("base.BDT"):
        assert price == pytest.approx(1200.0)
    else:  # the test company is not BDT: still never the raw USD figure
        assert price != pytest.approx(10.0)


# ------------------------------------------------------------- M43-10
def test_erp_m43_10_excluded_month_leaves_the_average(m43):
    m43.consume(10, m43.month(-3))
    m43.consume(40, m43.month(-2))
    m43.consume(10, m43.month(-1))
    m43.env["fix.demand.adjustment"].create(
        {
            "product_id": m43.prod.id,
            "part_id": m43.part.id,
            "location_id": m43.loc.id,
            "period": "%04d-%02d" % (m43.month(-2).year, m43.month(-2).month),
            "adjustment_type": "outlier_exclude",
            "reason": "one-off campaign",
        }
    ).with_user(m43.planner).action_apply()
    fc = m43.env["fix.demand.forecast"].create(
        {
            "product_id": m43.prod.id,
            "part_id": m43.part.id,
            "location_id": m43.loc.id,
            "period": m43.period,
            "window_months": 3,
        }
    )
    m43.env["ir.config_parameter"].sudo().set_param(common.CFG_FORECAST_MIN_HISTORY, "2")
    fc.with_user(m43.planner).action_compute_forecast()
    # (10 + 10) / 2, not (10 + 0 + 10) / 3
    assert fc.statistical_qty == pytest.approx(10.0)


# ------------------------------------------------------------- M43-12
def test_erp_m43_12_error_against_actuals_wape_and_bias(m43):
    from odoo.addons.cd_p03_portal.controllers.a06 import m43 as ctl

    fc = m43.forecast(10.0, period=m43.last_period)
    assert fc.actual_qty == 0.0
    # a zero-actual month has no % error of its own (was 100% of the forecast)
    assert fc.abs_error_pct == 0.0
    m43.consume(20, m43.month(-1), loc=m43.loc)
    fc.invalidate_recordset()
    assert fc.abs_error_pct == pytest.approx(50.0)
    measures = ctl.accuracy_measures(fc)
    assert measures["wape_pct"] == pytest.approx(50.0)
    assert measures["bias_pct"] == pytest.approx(-50.0)  # under-forecast


# ------------------------------------------------------------- M43-13
def test_erp_m43_13_kpi_is_the_achieved_fill_rate(m43):
    from odoo.addons.cd_p03_portal.controllers.a06 import m43 as ctl

    pol = m43.policy(2.0, 0.0, 10, service=99.0)
    m43.consume(9, datetime.utcnow() - timedelta(days=3))
    m43.env["fix.stock.backorder"].create(
        {"part_id": m43.part.id, "location_id": m43.loc.id, "qty": 1.0}
    )
    fill = ctl.achieved_fill_rate(m43.env, pol)
    assert fill["fill_rate_pct"] == pytest.approx(90.0)
    # the KPI is what happened, not the 99% target
    assert ctl.kpis(m43.env)["service_level_avg"] != pytest.approx(99.0)


# ------------------------------------------------------------- M43-21
def test_erp_m43_21_months_are_dhaka_months(m43):
    first = m43.month(-2, day=1)
    last_day = m43.month(-1, day=1) - timedelta(days=1)
    # 20:00 UTC on the month's last day is 02:00 next day in Dhaka
    m43.consume(4, datetime(last_day.year, last_day.month, last_day.day, 20, 0))
    buckets = common.consumed_by_month(m43.env, m43.company, m43.part, m43.loc, first, 2)
    assert buckets == [0.0, 4.0]
    assert common.dhaka_date(datetime(2026, 1, 31, 19, 0)) == date(2026, 2, 1)


# ------------------------------------------------------------- owner item 9
def test_erp_m43_forecast_window_defaults_12_and_6(m43):
    icp = m43.env["ir.config_parameter"].sudo()
    icp.search(
        [("key", "in", (common.CFG_FORECAST_WINDOW, common.CFG_FORECAST_MIN_HISTORY))]
    ).unlink()
    assert (
        common.param(m43.env, common.CFG_FORECAST_WINDOW, common.DEFAULT_FORECAST_WINDOW, int) == 12
    )
    fc = m43.env["fix.demand.forecast"].create(
        {"product_id": m43.prod.id, "part_id": m43.part.id, "period": m43.period}
    )
    assert fc.window_months == 12
    assert common.DEFAULT_FORECAST_MIN_HISTORY == 6
