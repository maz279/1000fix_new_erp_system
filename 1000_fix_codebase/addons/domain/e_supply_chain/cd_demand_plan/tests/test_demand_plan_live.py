# cd_demand_plan live-ORM tests — M43 demand planning on M15's reorder seam.
import json
from datetime import date

import pytest
from odoo.exceptions import UserError


@pytest.fixture
def product(odoo_env):
    return odoo_env["product.template"].create({"name": "AC Compressor 1.5T"})


def _plan(env, product, **vals):
    base = {
        "name": "FY26-Q3 compressors",
        "period_start": date(2026, 7, 1),
        "period_end": date(2026, 9, 30),
        "product_id": product.id,
    }
    base.update(vals)
    return env["fix.demand.plan"].create(base)


@pytest.mark.parametrize(
    ("forecast", "stock", "reorder", "expected"),
    [
        (100.0, 30.0, 20.0, 70.0),  # gap 70 > reorder point 20: order the gap
        (40.0, 30.0, 20.0, 0.0),  # gap 10 <= 20: within the buffer
        (50.0, 30.0, 20.0, 0.0),  # gap 20 == 20: not strictly above
        (10.0, 30.0, -50.0, 0.0),  # negative gap never orders
    ],
)
def test_recommended_order(odoo_env, product, forecast, stock, reorder, expected):
    plan = _plan(
        odoo_env,
        product,
        forecast_quantity=forecast,
        current_stock=stock,
        reorder_point=reorder,
    )
    assert plan.recommended_order == expected


def test_recommendation_follows_a_new_forecast(odoo_env, product):
    plan = _plan(odoo_env, product, forecast_quantity=40.0, current_stock=30.0, reorder_point=20.0)
    plan.forecast_quantity = 90.0  # gap 60 > 20
    assert plan.recommended_order == 60.0


def test_approval_publishes_the_replenishment(odoo_env, product):
    plan = _plan(odoo_env, product, forecast_quantity=100.0, current_stock=30.0, reorder_point=20.0)
    plan.action_approve()
    assert plan.state == "approved"
    rows = odoo_env["fix.event.outbox"].search(
        [("event_type", "=", "demand_plan.approved"), ("aggregate_id", "=", plan.id)]
    )
    assert [json.loads(r.payload) for r in rows] == [
        {"product": "AC Compressor 1.5T", "quantity": 70.0}
    ]


def test_nothing_to_replenish_is_refused(odoo_env, product):
    plan = _plan(odoo_env, product, forecast_quantity=10.0, current_stock=30.0)
    with pytest.raises(UserError, match="Nothing to replenish"), odoo_env.cr.savepoint():
        plan.action_approve()
    assert plan.state == "draft"
