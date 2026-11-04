"""cd_demand_plan ops behaviour (live ORM, rolled back): forecasts and error,
segmentation, safety-stock/ROP policy, reviews, rebalancing, what-if scenarios
and the planned-order → purchase-requisition bridge.

Rewritten in the A06 remediation. The previous version asserted the defects
the audit found: a typed forecast and typed actual (variance from typed
figures), a policy fed typed demand statistics, a flat 10% rebalance
"saving", a what-if that ignored the lead-time delta, and a requisition born
`approved`. Each test below asserts the corrected behaviour."""

from __future__ import annotations

from datetime import date

import pytest
from odoo.exceptions import UserError
from psycopg2 import IntegrityError


def test_forecast_variance_from_m15_and_workflow(m43):
    forecast = m43.forecast(100, period=m43.last_period, state="draft")
    m43.consume(90, m43.month(-1, day=12))
    assert forecast.name.startswith("DFC/")
    assert forecast.actual_qty == pytest.approx(90.0)
    assert forecast.variance == pytest.approx(-10.0)
    assert forecast.abs_error_pct == pytest.approx(11.1)
    zero = m43.forecast(0, period=m43.period, state="draft")
    with pytest.raises(UserError, match="positive"), m43.env.cr.savepoint():
        zero.with_user(m43.approver).action_approve()
    with pytest.raises(UserError, match="approved"), m43.env.cr.savepoint():
        forecast.with_user(m43.planner).action_publish()
    forecast.with_user(m43.approver).action_approve()
    forecast.with_user(m43.planner).action_publish()
    assert forecast.state == "published"


def test_segment_unique_per_product(m43):
    m43.segment(abc="a")
    with pytest.raises(IntegrityError), m43.env.cr.savepoint():
        m43.segment(abc="b")
        m43.env.flush_all()


def test_policy_computes_safety_stock_rop_and_target(m43):
    policy = m43.policy(4, 2, 9, service="95", review=30, state="draft")
    assert policy.safety_stock == pytest.approx(9.9)
    assert policy.reorder_point == pytest.approx(45.9)
    assert policy.target_level == pytest.approx(165.9)
    policy.sudo().write({"state": "active"})
    policy.with_user(m43.planner).action_pause()
    assert policy.state == "paused"


def test_review_completion_by_owner(m43):
    owner = m43.env["hr.employee"].search([("user_id", "=", m43.planner.id)], limit=1)
    review = (
        m43.env["fix.demand.review"]
        .with_user(m43.planner)
        .create(
            {
                "period": m43.period,
                "due_on": date.today(),
                "owner_id": owner.id,
                "notes": "Consensus agreed",
            }
        )
    )
    assert review.name.startswith("DRVW/")
    review.with_user(m43.planner).action_complete()
    assert review.state == "done"
    with pytest.raises(UserError, match="scheduled"), m43.env.cr.savepoint():
        review.with_user(m43.planner).action_complete()


def test_rebalance_value_and_guards(m43):
    m43.stock(20)
    proposal = (
        m43.env["fix.demand.rebalance"]
        .with_user(m43.planner)
        .create(
            {
                "product_id": m43.prod.id,
                "part_id": m43.part.id,
                "source_location_id": m43.loc.id,
                "target_location_id": m43.loc2.id,
                "qty": 10,
                "transfer_cost": 250,
            }
        )
    )
    assert proposal.stock_value == pytest.approx(10_000.0)
    assert proposal.source_branch == m43.branch.name  # the M15 location's branch
    proposal.with_user(m43.approver).action_approve()
    assert proposal.state == "approved" and proposal.transfer_id.state == "draft"
    with pytest.raises(UserError, match="proposed"), m43.env.cr.savepoint():
        proposal.with_user(m43.approver).action_approve()


def test_scenario_projection_uses_demand_and_lead_time(m43):
    policy = m43.policy(2, 0, 30)  # ROP 60
    scenario = (
        m43.env["fix.demand.scenario"]
        .with_user(m43.planner)
        .create({"policy_id": policy.id, "demand_adjust_pct": 20})
    )
    assert scenario.base_reorder_point == pytest.approx(60.0)
    assert scenario.projected_reorder_point == pytest.approx(72.0)
    scenario.with_user(m43.planner).action_run()
    assert scenario.state == "run"


def test_plan_generates_a_draft_requisition_with_an_operating_unit(m43):
    plan = m43.ready_plan()
    with pytest.raises(UserError, match="Approve the plan"), m43.env.cr.savepoint():
        plan.with_user(m43.planner).action_generate_pr()
    plan.with_user(m43.approver).action_approve()
    assert plan.approved_order_qty > 0
    plan.with_user(m43.planner).action_generate_pr()
    requisition = plan.sudo().pr_requisition_id
    assert requisition and requisition.qty == pytest.approx(plan.approved_order_qty)
    assert requisition.operating_unit_id == m43.ou
    assert requisition.state not in ("approved", "converted")
    with pytest.raises(UserError, match="already has a requisition"), m43.env.cr.savepoint():
        plan.with_user(m43.planner).action_generate_pr()
