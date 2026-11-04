# cd_import_order live-ORM tests — M44 landed cost + the receipt gate.
#
# A06 audit (2026-11-03): the first test used to TYPE customs_duty = 300 and
# assert landed_cost = 1475; customs duty is now computed from the paid Bills
# of Entry (o06), so the test asserts that a typed duty is refused. The second
# test used to receive a DRAFT order and assert the goods.received event; a
# receipt now runs only from Cleared (M44-13), so it asserts the refusal. The
# proper receipt path is covered in test_a06_m44_controls.py (o02/o03).
import pytest
from odoo.exceptions import UserError


def test_landed_cost_is_fob_plus_freight_insurance_duty(odoo_env):
    order = odoo_env["fix.import.order"].create(
        {
            "name": "IMP-2026-001",
            "fob_value": 1000.0,
            "freight_cost": 150.0,
            "insurance_cost": 25.0,
        }
    )
    # 1000 + 150 + 25 + 0 duty (no paid Bill of Entry) = 1175.00
    assert order.landed_cost == 1175.0
    assert order.customs_duty == 0.0
    assert order.currency_id == odoo_env.ref("base.USD")
    assert order.state == "draft"
    officer = (
        odoo_env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "m44 live officer",
                "login": "m44.live.officer@test",
                "group_ids": [
                    (6, 0, [odoo_env.ref("cd_import_order.group_fix_import_officer").id])
                ],
            }
        )
    )
    with pytest.raises(UserError, match="workflow"), odoo_env.cr.savepoint():
        order.with_user(officer).write({"customs_duty": 300.0})


def test_receipt_refused_before_clearance(odoo_env):
    supplier = odoo_env["res.partner"].create({"name": "Shenzhen Parts Co."})
    order = odoo_env["fix.import.order"].create(
        {"name": "IMP-2026-002", "supplier_id": supplier.id, "fob_value": 2500.5}
    )
    with pytest.raises(UserError, match="cleared"), odoo_env.cr.savepoint():
        order.action_receive()
    assert order.state == "draft"
    assert not odoo_env["fix.event.outbox"].search(
        [
            ("event_type", "=", "goods.received"),
            ("aggregate", "=", "fix.import.order"),
            ("aggregate_id", "=", order.id),
        ]
    )
