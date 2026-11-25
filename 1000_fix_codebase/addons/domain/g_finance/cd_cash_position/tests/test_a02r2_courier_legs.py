# A02 ERP audit pass 2 (20 Nov 2026), the courier remittance side of M03.
#
#   M03-02 (D1)  a courier's service-order cash-on-delivery legs are cleared by
#                its remittance like its storefront COD orders, once, and the
#                legs are marked handed in
#   M03-06 (D22) the delivery charges a courier deducts are checked against its
#                rate card (5% tolerance); no rate card, no deduction accepted
#
# Arrangement as superuser; every workflow step as the non-admin accountant /
# Accounting Administrator of the M50 fixture.
# ruff: noqa: F811  (fixtures are imported and used as parameters)
from __future__ import annotations

import pytest
from odoo import fields
from odoo.addons.cd_cash_position.tests.test_a08_m50_controls import c  # noqa: F401
from odoo.addons.cd_cash_position.tests.test_g10_courier_remittance import (  # noqa: F401
    _courier_orders,
    _remittance,
    cr,
)
from odoo.exceptions import UserError

pytestmark = [pytest.mark.financial]


def _cod_leg(c, courier, amount):
    """A delivered service-order delivery leg whose COD the courier collected."""
    brand = c.env["fix.brand"].create({"name": "R2 Brand %s" % amount, "code": "R2B%d" % amount})
    model = c.env["fix.device.model"].create({"name": "R2 Phone", "brand_id": brand.id})
    cust = c.env["res.partner"].create({"name": "R2 COD customer"})
    device = c.env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": cust.id, "serial_number": "R2-SN-%d" % amount}
    )
    branch = c.env["fix.branch"].search([], limit=1)
    order = c.env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": cust.id,
            "branch_id": branch.id,
            "fault_description": "r2 cod",
        }
    )
    leg = (
        c.env["fix.consignment"]
        .sudo()
        .create(
            {
                "operating_unit_id": c.ou.id,
                "consignment_type": "delivery",
                "scheduled_date": fields.Datetime.now(),
                "courier_partner_id": courier.id,
                "service_order_id": order.id,
            }
        )
    )
    c.env.cr.execute("update fix_consignment set state='delivered' where id=%s", (leg.id,))
    leg.invalidate_recordset()
    leg._guarded().write(
        {
            "cod_amount": amount,
            "cod_collected_at": fields.Datetime.now(),
            "cod_reference": "COD/%s" % leg.name,
        }
    )
    return leg


def test_m03_02_service_order_cod_legs_are_remitted_once(cr):
    c = cr
    orders = _courier_orders(c, c.pathao, [1000.0])
    leg = _cod_leg(c, c.pathao, 2500.0)
    _cod_leg(c, c.redx, 900.0)  # another courier's
    r = _remittance(c, net_amount=3500.0)
    r.with_user(c.acct).action_load_orders()
    assert r.order_ids == orders and r.consignment_ids == leg
    assert (r.order_count, r.gross_amount, r.difference) == (2, 3500.0, 0.0)
    r.with_user(c.acct).action_submit()
    r.with_user(c.mgr).action_settle()
    credit = sum(
        r.move_id.line_ids.filtered(lambda ln: ln.account_id == c.acc["cod_clearing"]).mapped(
            "credit"
        )
    )
    assert credit == 3500.0
    assert leg.cod_remitted_at
    # once: a second remittance finds it handed in, and naming it is refused
    again = _remittance(c, net_amount=0.0)
    again.with_user(c.acct).action_load_orders()
    assert not again.consignment_ids
    with pytest.raises(UserError, match="handed in"), c.env.cr.savepoint():
        again.with_user(c.acct).action_load_orders(references=leg.name)


def test_d1_the_courier_remittance_confirms_the_orders_cod(cr):
    """A02 pass 2 review (D1): the COD receipt booked at the door verified the
    order's COD on the spot (it found its own receipt), while the courier
    still held the cash; and the courier remittance never confirmed it. The
    order's COD is verified when the remittance that hands the cash in is
    settled, not before."""
    c = cr
    params = c.env["ir.config_parameter"].sudo()
    ar = c.env["account.account"].create(
        {"code": "R2CRAR%d" % c.n, "name": "R2 courier AR", "account_type": "asset_receivable"}
    )
    params.set_param("cd_billing_engine.account_code.ar", ar.code)
    params.set_param("cd_billing_engine.account_code.cod_clearing", c.acc["cod_clearing"].code)
    leg = _cod_leg(c, c.pathao, 1.0)
    order = leg.service_order_id
    c.env["fix.estimate"].create(
        {
            "order_id": order.id,
            "state": "approved",
            "line_ids": [
                (
                    0,
                    0,
                    {"description": "Repair", "quantity": 1, "unit_price": 2000.0,
                     "line_type": "labour"},
                )
            ],
        }
    )  # fmt: skip
    due = order._fix_amount_due()
    leg._guarded().write({"cod_amount": due})
    order.with_context(fd_settlement_tender="cod")._fix_record_settlement(
        due, leg.cod_reference, source="cod"
    )
    receipt = c.env["fix.ar.receipt"].search([("source_order_id", "=", order.id)])
    assert receipt.method == "cod" and receipt.amount == due
    # the courier still holds the cash: its own receipt does not verify it
    assert not order._fix_try_verify_from_receipt()
    assert order.settlement_source == "cod" and not order.settlement_verified
    r = _remittance(c, net_amount=due)
    r.with_user(c.acct).action_load_orders()
    assert leg in r.consignment_ids
    r.with_user(c.acct).action_submit()
    r.with_user(c.mgr).action_settle()
    order.invalidate_recordset()
    assert leg.cod_remitted_at and order.settlement_verified
    assert order.amount_verified_bdt == due


def test_m03_06_deducted_charges_are_checked_against_the_rate_card(cr):
    c = cr
    _courier_orders(c, c.pathao, [3000.0])  # one consignment: rate card BDT 200
    r = _remittance(c, delivery_charges=260.0, net_amount=2740.0)
    r.with_user(c.acct).action_load_orders()
    with pytest.raises(UserError, match="rate card"), c.env.cr.savepoint():
        r.with_user(c.acct).action_submit()
    r.with_user(c.acct).write({"delivery_charges": 210.0, "net_amount": 2790.0})  # within 5%
    r.with_user(c.acct).action_submit()
    assert r.state == "submitted"
    # a courier with no rate card cannot have its charges accepted
    c.redx.sudo().write({"base_rate": 0.0, "per_kg_rate": 0.0})
    _courier_orders(c, c.redx, [1000.0])
    r2 = _remittance(c, courier=c.redx, delivery_charges=50.0, net_amount=950.0)
    r2.with_user(c.acct).action_load_orders()
    with pytest.raises(UserError, match="no rate card"), c.env.cr.savepoint():
        r2.with_user(c.acct).action_submit()
