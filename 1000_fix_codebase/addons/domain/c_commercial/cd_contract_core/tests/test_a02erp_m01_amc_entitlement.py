# A02 ERP audit (2026-11-19) M01-F13, builder stream B5: the AMC entitlement
# is drawn when the order is approved by ANY path - the estimate's approval
# drives the order to approved without calling the order's Approve button,
# which was the only place the draw lived - and is given back on cancel.
# ruff: noqa: F811 - `c` is the contract fixture, imported so pytest registers it.
from odoo import Command
from odoo.addons.cd_contract_core.tests.test_a04_c2_c13_contracts import (  # noqa: F401
    _active,
    _amc_order,
    _device,
    _user,
    c,
)


def test_amc_entitlement_is_drawn_when_the_estimate_approves_the_order(c):
    dev = _device(c)
    k = _active(
        c, devices=dev, entitlements=[{"entitlement_type": "incidents", "quantity_included": 2}]
    )
    order = _amc_order(c, k, dev)
    order.action_intake()
    order.action_start_diagnostic()
    order.action_request_estimate()
    est = (
        c.env["fix.estimate"]
        .with_user(c.clerk)
        .create(
            {
                "order_id": order.id,
                "line_ids": [
                    Command.create(
                        {
                            "line_type": "labour",
                            "description": "AMC visit labour",
                            "quantity": 1,
                            "unit_price": 1000,
                        }
                    )
                ],
            }
        )
    )
    est.action_send()
    est.with_user(_user(c.env, "a02erp_b5_staff")).action_approve()
    assert order.state == "approved"
    ent = k.entitlement_ids
    ent.invalidate_recordset()
    assert ent.quantity_consumed == 1.0 and order.contract_entitlement_id == ent
    # the cancelled order gives its unit back
    order.with_user(c.clerk).action_cancel(reason_code="customer_declined")
    ent.invalidate_recordset()
    assert ent.quantity_consumed == 0.0 and order.contract_entitlement_restored
