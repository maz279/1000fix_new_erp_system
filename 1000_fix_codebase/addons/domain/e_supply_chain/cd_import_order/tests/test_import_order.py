"""cd_import_order structural behaviour - P09-M07 (CD-M44-01).

A06 audit (2026-11-03) P3: this file used to grep the source
(inspect.getsource) for words like "fob_value" and "goods.received". It now
checks the behaviour those words stood for, on the live registry.
"""


def test_landed_cost_computed_from_fob_freight_insurance_duty(odoo_env):
    order = odoo_env["fix.import.order"].create(
        {"name": "IMP-STRUCT-1", "fob_value": 100.0, "freight_cost": 10.0, "insurance_cost": 5.0}
    )
    assert order.landed_cost == 115.0
    order.write({"freight_cost": 20.0})
    assert order.landed_cost == 125.0
    field = order._fields["landed_cost"]
    assert field.compute and field.store


def test_import_lifecycle_states(odoo_env):
    """draft -> shipped -> customs -> cleared -> received -> landed."""
    states = [k for k, _v in odoo_env["fix.import.order"]._fields["state"].selection]
    assert states == ["draft", "shipped", "customs", "cleared", "received", "landed"]


def test_order_state_is_guarded(odoo_env):
    order = odoo_env["fix.import.order"].browse()
    assert "state" in order._fix_guarded_fields()
    assert "receipt_id" in order._fix_guarded_fields()


def test_as02_conformance(odoo_env):
    Order = odoo_env["fix.import.order"]
    for mixin in ("mail.thread", "mail.activity.mixin", "fix.guarded.mixin"):
        assert mixin in Order._inherit
    assert "company_id" in Order._fields
    assert "operating_unit_id" in Order._fields
