# cd_demand_plan live-ORM tests — M43 demand planning on M15's reorder seam.
#
# Rewritten in the A06 remediation (M43-3/M43-4): the previous tests typed the
# forecast, stock and ROP onto the plan and asserted the defective formula
# (order only when forecast - stock > ROP; e.g. 40 / 30 / 20 -> 0). The plan's
# figures are now computed from the approved forecast, M15 on-hand and the
# active policy, and the order is "at or below ROP -> up to the target".
import json

import pytest
from odoo.exceptions import UserError


# A06 ERP audit M43-06: the INVENTORY POSITION (stock + on order) is compared
# with the ROP, which already holds the lead-time demand; the period forecast
# is no longer subtracted a second time (that ordered ~1 extra period).
@pytest.mark.parametrize(
    ("forecast", "stock", "avg", "lead", "expected"),
    [
        (10.0, 5.0, 2.0, 10, 75.0),  # ROP 20, target 80, position 5
        (100.0, 0.0, 5.0, 10, 200.0),  # ROP 50, target 200, position 0
        (40.0, 30.0, 2.0, 10, 0.0),  # position 30 > ROP 20 (forecast not subtracted)
        (10.0, 100.0, 2.0, 10, 0.0),  # position 100 > ROP 20
    ],
)
def test_recommended_order(m43, forecast, stock, avg, lead, expected):
    plan = m43.ready_plan(forecast=forecast, stock=stock, avg=avg, std=0, lead=lead)
    assert plan.recommended_order == pytest.approx(expected)


def test_recommendation_follows_the_inventory_position(m43):
    plan = m43.ready_plan(forecast=10.0, stock=100.0)
    assert plan.recommended_order == 0.0
    forecast = m43.env["fix.demand.forecast"].search(
        [("part_id", "=", m43.part.id), ("period", "=", m43.period)]
    )
    forecast.sudo().write({"override_qty": 90.0})  # a re-forecast (superuser maintenance)
    plan.invalidate_recordset()
    # the forecast is shown, not ordered on: position 100 still above ROP 20
    assert plan.projected_stock == pytest.approx(10.0)
    assert plan.recommended_order == 0.0
    m43.env["fix.stock.onhand"].search([("part_id", "=", m43.part.id)]).sudo().write({"qty": 10})
    plan.invalidate_recordset()
    # position 10 <= ROP 20 -> up to 80
    assert plan.recommended_order == pytest.approx(70.0)


def test_approval_publishes_the_replenishment(m43):
    plan = m43.ready_plan()
    plan.with_user(m43.approver).action_approve()
    assert plan.state == "approved"
    rows = m43.env["fix.event.outbox"].search(
        [("event_type", "=", "demand_plan.approved"), ("aggregate_id", "=", plan.id)]
    )
    assert [json.loads(r.payload) for r in rows] == [{"product": m43.tmpl.name, "quantity": 75.0}]


def test_nothing_to_replenish_is_refused(m43):
    plan = m43.ready_plan(forecast=10.0, stock=100.0)
    with pytest.raises(UserError, match="Nothing to replenish"), m43.env.cr.savepoint():
        plan.with_user(m43.approver).action_approve()
    assert plan.state == "draft"


def test_plan_without_policy_is_refused(m43):
    m43.forecast(10)
    plan = m43.plan()
    with pytest.raises(UserError, match="no active replenishment policy"), m43.env.cr.savepoint():
        plan.with_user(m43.approver).action_approve()
