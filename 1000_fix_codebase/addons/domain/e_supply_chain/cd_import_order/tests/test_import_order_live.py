# cd_import_order live-ORM tests — M44 landed cost + the M41 event break.
import json


def test_landed_cost_is_fob_plus_freight_insurance_duty(odoo_env):
    order = odoo_env["fix.import.order"].create(
        {
            "name": "IMP-2026-001",
            "fob_value": 1000.0,
            "freight_cost": 150.0,
            "insurance_cost": 25.0,
            "customs_duty": 300.0,
        }
    )
    # 1000 + 150 + 25 + 300 = 1475.00
    assert order.landed_cost == 1475.0
    assert order.currency_id == odoo_env.ref("base.USD")
    assert order.state == "draft"
    order.customs_duty = 0.0
    assert order.landed_cost == 1175.0


def test_receipt_publishes_goods_received(odoo_env):
    supplier = odoo_env["res.partner"].create({"name": "Shenzhen Parts Co."})
    order = odoo_env["fix.import.order"].create(
        {"name": "IMP-2026-002", "supplier_id": supplier.id, "fob_value": 2500.5}
    )
    order.action_receive()
    assert order.state == "received"
    rows = odoo_env["fix.event.outbox"].search(
        [
            ("event_type", "=", "goods.received"),
            ("aggregate", "=", "fix.import.order"),
            ("aggregate_id", "=", order.id),
        ]
    )
    assert [json.loads(r.payload) for r in rows] == [{"order": "IMP-2026-002", "value": 2500.5}]
