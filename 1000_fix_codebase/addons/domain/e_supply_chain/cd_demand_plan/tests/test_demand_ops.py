"""cd_demand_plan ops behaviour (live ORM, rolled back): forecasts and error,
segmentation, safety-stock/ROP policy, reviews, rebalancing, what-if scenarios
and the planned-order → purchase-requisition bridge."""

from __future__ import annotations

import uuid
from datetime import date

import pytest
from odoo.exceptions import UserError
from psycopg2 import IntegrityError

TAG = uuid.uuid4().hex[:6].upper()


@pytest.fixture
def ctx(odoo_env):
    env = odoo_env
    product = env["product.product"].create({"name": f"Demand Product {TAG}"})
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    return {"env": env, "product": product, "ou": ou}


def test_forecast_variance_and_guards(ctx):
    env, product = ctx["env"], ctx["product"]
    forecast = env["fix.demand.forecast"].create(
        {"product_id": product.id, "period": "2026-10", "forecast_qty": 100, "actual_qty": 90}
    )
    assert forecast.name.startswith("DFC/")
    assert forecast.variance == pytest.approx(-10.0)
    assert forecast.abs_error_pct == pytest.approx(11.1)
    with pytest.raises(UserError, match="positive"), env.cr.savepoint():
        env["fix.demand.forecast"].create(
            {"product_id": product.id, "period": "2026-11", "forecast_qty": 0}
        ).action_approve()
    with pytest.raises(UserError, match="approved"), env.cr.savepoint():
        forecast.action_publish()
    forecast.action_approve()
    forecast.action_publish()
    assert forecast.state == "published"


def test_segment_unique_per_product(ctx):
    env, product = ctx["env"], ctx["product"]
    env["fix.demand.segment"].create({"product_id": product.id, "abc_class": "a"})
    with pytest.raises(IntegrityError), env.cr.savepoint():
        env["fix.demand.segment"].create({"product_id": product.id, "abc_class": "b"})


def test_policy_computes_safety_stock_and_rop(ctx):
    env, product = ctx["env"], ctx["product"]
    policy = env["fix.demand.policy"].create(
        {
            "product_id": product.id,
            "avg_daily_demand": 4,
            "demand_stddev": 2,
            "lead_time_days": 9,
            "service_level_pct": "95",
        }
    )
    assert policy.safety_stock == pytest.approx(9.9)
    assert policy.reorder_point == pytest.approx(45.9)
    policy.action_pause()
    assert policy.state == "paused"


def test_review_completion(ctx):
    env = ctx["env"]
    review = env["fix.demand.review"].create({"period": "2026-10", "due_on": date(2026, 10, 31)})
    assert review.name.startswith("DRVW/")
    review.action_complete()
    assert review.state == "done"
    with pytest.raises(UserError, match="scheduled"), env.cr.savepoint():
        review.action_complete()


def test_rebalance_savings_and_guards(ctx):
    env, product = ctx["env"], ctx["product"]
    proposal = env["fix.demand.rebalance"].create(
        {
            "product_id": product.id,
            "source_branch": "A",
            "target_branch": "B",
            "qty": 10,
            "unit_cost": 500,
        }
    )
    assert proposal.savings == pytest.approx(500.0)
    proposal.action_approve()
    assert proposal.state == "approved"
    with pytest.raises(UserError, match="proposed"), env.cr.savepoint():
        proposal.action_approve()


def test_scenario_projection(ctx):
    env, product = ctx["env"], ctx["product"]
    scenario = env["fix.demand.scenario"].create(
        {
            "product_id": product.id,
            "demand_adjust_pct": 20,
            "base_reorder_point": 60,
        }
    )
    assert scenario.projected_reorder_point == pytest.approx(72.0)
    scenario.action_run()
    assert scenario.state == "run"


def test_plan_generates_a_requisition_with_an_operating_unit(ctx):
    env, product, ou = ctx["env"], ctx["product"], ctx["ou"]
    plan = env["fix.demand.plan"].create(
        {
            "name": f"PLAN-{TAG}",
            "period_start": date(2026, 10, 1),
            "period_end": date(2026, 10, 31),
            "product_id": product.product_tmpl_id.id,
            "forecast_quantity": 120,
            "current_stock": 20,
            "reorder_point": 30,
            "operating_unit_id": ou.id,
        }
    )
    with pytest.raises(UserError, match="Approve the plan"), env.cr.savepoint():
        plan.action_generate_pr()
    plan.action_approve()
    assert plan.recommended_order > 0
    plan.action_generate_pr()
    requisition = plan.pr_requisition_id
    assert requisition and requisition.qty == pytest.approx(plan.recommended_order)
    assert requisition.operating_unit_id == ou
    assert requisition.state == "approved"
    with pytest.raises(UserError, match="already has a requisition"), env.cr.savepoint():
        plan.action_generate_pr()
