# cd_inventory tests — Replenishment Engine & M43 Seam (CD-M15-02).
#
# A06 audit M15-17: the source-grep checks that used to live here
# (inspect.getsource(...) contains "reorder.triggered") are replaced by
# executed behaviour of the same promises.
import json

import pytest
from odoo.exceptions import ValidationError


def _rule(inv, location=None, **kw):
    vals = {
        "spare_part_id": inv.part.id,
        "location_id": (location or inv.hub).id,
        "branch_id": inv.branch().id,
        "operating_unit_id": inv.ou.id,
    }
    vals.update(kw)
    return inv.env["fix.reorder.rule"].create(vals)


def test_m43_seam_reorder_point(inv):
    rule = _rule(inv)
    assert rule.m43_model_version == "m43_seam_v1.0"
    assert rule.compute_dynamic_reorder_point() == 7.0  # min 5 + safety 2
    rule.write({"m43_ai_override": True, "m43_predicted_demand": 14.0})
    assert rule.compute_dynamic_reorder_point() == 8.0  # 2/day x 3 days + 2


def test_trigger_publishes_reorder_triggered_with_the_seam(inv):
    rule = _rule(inv)  # the hub holds none of the part
    out = rule.action_trigger_reorder()
    assert (out["status"], out["order_qty"]) == ("alert_triggered", 20.0)
    rows = (
        inv.env["fix.event.outbox"]
        .sudo()
        .search([("event_type", "=", "reorder.triggered"), ("aggregate_id", "=", rule.id)])
    )
    (event,) = [json.loads(r.payload) for r in rows]
    assert (
        event["current_stock"],
        event["suggested_order_qty"],
        event["m43_dynamic_reorder_point"],
    ) == (
        0.0,
        20.0,
        7.0,
    )


def test_sweep_alerts_and_clears(inv):
    rule = _rule(inv)
    Rule = inv.env["fix.reorder.rule"]
    Rule.check_replenishment_alerts()
    assert rule.state in ("alert", "ordered")
    inv.stock(inv.part, inv.hub, 8.0, 500.0)
    Rule.check_replenishment_alerts()
    assert rule.state == "active"


@pytest.mark.parametrize(
    ("min_qty", "max_qty", "message"),
    [
        (-1.0, 10.0, "Minimum quantity cannot be negative"),
        (10.0, 10.0, "Maximum stock level must strictly exceed minimum reorder point"),
    ],
)
def test_quantity_constraints(inv, min_qty, max_qty, message):
    inv.branch()
    with pytest.raises(ValidationError, match=message), inv.env.cr.savepoint():
        _rule(inv, min_qty=min_qty, max_qty=max_qty)
