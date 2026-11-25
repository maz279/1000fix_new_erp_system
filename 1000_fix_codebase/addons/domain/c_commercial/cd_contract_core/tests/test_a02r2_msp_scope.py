# ruff: noqa: F811  (the imported m5 fixture is used as a parameter)
"""A02 ERP pass-2 audit (2026-11-20), stream S4: M05-S09 (owner decision D10).

The MSP per-device fee covers labour and remote support only. An MSP ticket is
an order of service type "MSP Alert"; it is zero-charge under the MSP while
its work is labour, but parts and out-of-scope work are an overage the client
approves on the estimate, unless the MSP contract has a parts entitlement.
Every MSP ticket used to be a zero-charge AMC order, so parts left free.

The M05 fixture comes from cd_msp_contract's tests (this database has both).
``odoo_env`` rolls back after each test.
"""

from odoo.addons.cd_msp_contract.tests.test_a02_p1p2_cd_msp_contract import (  # noqa: F401
    _as,
    m5,
)

REASON = "Client signed amendment 3 on the 20th"


def _ticket(m5):
    alert = _as(m5.env["fix.msp.alert"], m5.eng).create(
        {
            "msp_contract_id": m5.msp.id,
            "asset_id": m5.asset.id,
            "severity": "major",
            "message": "server will not boot",
        }
    )
    _as(alert, m5.eng).action_to_ticket()
    return alert.order_id


def _estimate(m5, order, line_type):
    return m5.env["fix.estimate"].create(
        {
            "order_id": order.id,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "line_type": line_type,
                        "description": "Mainboard" if line_type == "part" else "Bench labour",
                        "quantity": 1,
                        "unit_price": 20000.0 if line_type == "part" else 3000.0,
                    },
                )
            ],
        }
    )


def test_s09_an_msp_ticket_is_an_msp_alert_order_covered_for_labour(m5):
    order = _ticket(m5)
    assert order.service_type == "msp_alert"
    assert order._fix_msp_covers()
    _estimate(m5, order, "labour")
    assert order._fix_msp_covers()
    assert "managed asset under MSP" in order._fix_zero_charge_basis()


def test_s09_parts_are_an_overage_unless_the_contract_includes_them(m5):
    order = _ticket(m5)
    _estimate(m5, order, "part")
    assert not order._fix_msp_covers()
    assert order._fix_zero_charge_basis() == ""  # the client approves the estimate
    _as(m5.msp, m5.fin).action_amend_terms(term="parts_included", value="1", reason=REASON)
    order.invalidate_recordset()
    assert order._fix_msp_covers()


def test_s09_an_offboarding_contract_no_longer_covers(m5):
    order = _ticket(m5)
    _as(m5.msp, m5.eng).action_start_offboarding()
    assert not order._fix_msp_covers()
