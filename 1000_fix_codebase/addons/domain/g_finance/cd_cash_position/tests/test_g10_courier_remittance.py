# cd_cash_position — G10 (owner decision 12 Nov 2026): the courier remittance.
#
# Cash a third-party courier (Pathao, RedX, Steadfast) collects on delivered
# COD orders sits in COD clearing (the storefront bridge's cod receipt, Dr COD
# clearing / Cr AR). M50 settled only in-house riders, so nothing cleared it.
# The courier pays out in batches, net of its delivery and COD charges: a
# remittance names the courier's batch, the delivered COD orders it covers,
# the charges deducted and the net the bank received, and posts
#   Dr bank (net) + Dr courier charges / Cr COD clearing (gross)
# once one accountant has prepared it and a different Accounting
# Administrator settles it. Orders already settled (by a remittance or a
# rider settlement), prepaid or paid elsewhere are refused.
#
# The arrangement (accounts, a delivered consignment) is done as superuser;
# every workflow step runs as a non-admin user holding the real role.
# ruff: noqa: F811  (the M50 fixture is imported and used as a parameter)
from __future__ import annotations

import itertools

import pytest
from odoo import fields
from odoo.addons.cd_cash_position.tests.test_a08_m50_controls import (  # noqa: F401
    REFUSED,
    _cod,
    _cod_orders,
    bal,
    c,
)
from odoo.exceptions import UserError

pytestmark = [pytest.mark.financial]

_SEQ = itertools.count(1)
CHARGES_PARAM = "cd_cash_position.account_code.courier_charges"


@pytest.fixture
def cr(c):
    env = c.env
    n = next(_SEQ)
    c.charges = env["account.account"].create(
        {
            "code": "G10CC%02d" % (c.n % 100),
            "name": "G10 courier charges",
            "account_type": "expense",
        }
    )
    env["ir.config_parameter"].sudo().set_param(CHARGES_PARAM, c.charges.code)
    Courier = env["fix.courier.partner"]
    # A02 ERP audit pass 2 M03-06 (D22): deducted delivery charges are checked
    # against the courier's rate card, so each courier has one
    rates = {"base_rate": 200.0, "per_kg_rate": 0.0}
    c.pathao = Courier.create({"name": "G10 Pathao %s" % n, "code": "G10P%s%s" % (c.n, n), **rates})
    c.redx = Courier.create({"name": "G10 RedX %s" % n, "code": "G10R%s%s" % (c.n, n), **rates})
    return c


def _courier_orders(c, courier, amounts, rail="cod", **order_vals):
    """Delivered COD orders on one consignment the courier carried."""
    cons = (
        c.env["fix.consignment"]
        .sudo()
        .create(
            {
                "operating_unit_id": c.ou.id,
                "consignment_type": "delivery",
                "scheduled_date": fields.Datetime.now(),
                "courier_partner_id": courier.id,
            }
        )
    )
    c.env.cr.execute("update fix_consignment set state='delivered' where id=%s", (cons.id,))
    cons.invalidate_recordset()
    cust = c.env["res.partner"].create({"name": "G10 COD customer"})
    orders = c.env["fix.storefront.order"]
    for amount in amounts:
        orders |= (
            c.env["fix.storefront.order"]
            .sudo()
            .create(
                {
                    "customer_id": cust.id,
                    "total_amount": amount,
                    "shipping_address": "Dhaka",
                    "payment_rail": rail,
                    "state": "delivered",
                    "carrier_consignment_id": cons.id,
                    "operating_unit_id": c.ou.id,
                    **order_vals,
                }
            )
        )
    return orders


def _remittance(c, courier=None, user=None, **vals):
    values = {
        "operating_unit_id": c.ou.id,
        "courier_id": (courier or c.pathao).id,
        "batch_ref": "G10-PAY-%s" % next(_SEQ),
        "journal_id": c.bank.id,
        "bank_ref": "G10-BANK-%s" % next(_SEQ),
    }
    values.update(vals)
    return c.env["fix.courier.remittance"].with_user(user or c.acct).create(values)


def test_g10_remittance_posts_net_bank_and_charges_against_gross_cod(cr):
    c = cr
    mine = _courier_orders(c, c.pathao, [3000.0, 2000.0])
    _courier_orders(c, c.redx, [7000.0])  # another courier's cash
    _courier_orders(c, c.pathao, [9000.0], rail="bkash")  # not cash on delivery
    _cod_orders(c, [4000.0])  # an in-house rider's cash
    r = _remittance(c, delivery_charges=120.0, cod_charges=50.0, net_amount=4830.0)
    r.with_user(c.acct).action_load_orders()
    assert r.order_ids == mine
    assert (r.order_count, r.gross_amount, r.total_charges, r.difference) == (
        2,
        5000.0,
        170.0,
        0.0,
    )
    r.with_user(c.acct).action_submit()
    assert r.state == "submitted" and r.submitted_by_id == c.acct
    r.with_user(c.mgr).action_settle()
    assert r.state == "settled" and r.settled_by_id == c.mgr
    move = r.move_id
    assert move.state == "posted"
    by_account = {(ln.account_id, ln.debit, ln.credit) for ln in move.line_ids}
    assert by_account == {
        (c.bank_acc, 4830.0, 0.0),
        (c.charges, 170.0, 0.0),
        (c.acc["cod_clearing"], 0.0, 5000.0),
    }
    assert bal(c, c.acc["cod_clearing"]) == -5000.0  # the receipts' debit is not in this test


def test_g10_the_preparer_cannot_settle_and_an_accountant_cannot_settle(cr):
    c = cr
    _courier_orders(c, c.pathao, [3000.0])
    r = _remittance(c, user=c.mgr, net_amount=3000.0)
    r.with_user(c.mgr).action_load_orders()
    r.with_user(c.mgr).action_submit()
    with pytest.raises(UserError, match="Segregation"), c.env.cr.savepoint():
        r.with_user(c.mgr).action_settle()
    with pytest.raises(UserError), c.env.cr.savepoint():
        r.with_user(c.acct).action_settle()  # not an Accounting Administrator
    assert r.state == "submitted" and not r.move_id
    r.with_user(c.mgr2).action_settle()
    assert r.state == "settled"


def test_g10_the_courier_statement_must_add_up(cr):
    c = cr
    _courier_orders(c, c.pathao, [3000.0, 2000.0])
    r = _remittance(c, delivery_charges=100.0, net_amount=4950.0)  # 50 unexplained
    r.with_user(c.acct).action_load_orders()
    with pytest.raises(UserError, match="add up"), c.env.cr.savepoint():
        r.with_user(c.acct).action_submit()
    r.with_user(c.acct).write({"net_amount": 4900.0})
    r.with_user(c.acct).action_submit()
    assert r.state == "submitted"


def test_g10_a_bank_remittance_names_its_bank_credit_and_batch(cr):
    c = cr
    _courier_orders(c, c.pathao, [3000.0])
    r = _remittance(c, bank_ref=False, net_amount=3000.0)
    r.with_user(c.acct).action_load_orders()
    with pytest.raises(UserError, match="bank"), c.env.cr.savepoint():
        r.with_user(c.acct).action_submit()
    r.with_user(c.acct).write({"bank_ref": "G10-SLIP-1"})
    r.with_user(c.acct).action_submit()
    # the courier's batch is settled once
    _courier_orders(c, c.pathao, [1000.0])
    again = _remittance(c, batch_ref=r.batch_ref, net_amount=1000.0)
    again.with_user(c.acct).action_load_orders()
    with pytest.raises(UserError, match=r.batch_ref), c.env.cr.savepoint():
        again.with_user(c.acct).action_submit()


def test_g10_orders_settled_prepaid_or_paid_elsewhere_are_refused(cr):
    c = cr
    first = _courier_orders(c, c.pathao, [3000.0])
    done = _remittance(c, net_amount=3000.0)
    done.with_user(c.acct).action_load_orders()
    done.with_user(c.acct).action_submit()
    done.with_user(c.mgr).action_settle()
    prepaid = _courier_orders(
        c, c.pathao, [2000.0], payment_date=fields.Datetime.now(), payment_ref="G10-PRE"
    )
    other = _courier_orders(c, c.redx, [1500.0])
    r = _remittance(c, net_amount=0.0)
    # loading finds nothing open: the settled order and the prepaid one are skipped
    r.with_user(c.acct).action_load_orders()
    assert not r.order_ids
    # naming them is refused, each with its reason
    with pytest.raises(UserError, match="already"), c.env.cr.savepoint():
        r.with_user(c.acct).action_load_orders(references=first.name)
    with pytest.raises(UserError, match="paid"), c.env.cr.savepoint():
        r.with_user(c.acct).action_load_orders(references=prepaid.name)
    with pytest.raises(UserError, match=c.pathao.name), c.env.cr.savepoint():
        r.with_user(c.acct).action_load_orders(references=other.name)
    assert not r.order_ids
    # the order set cannot be written by hand
    with pytest.raises(REFUSED), c.env.cr.savepoint():
        r.with_user(c.acct).write({"order_ids": [(6, 0, first.ids)]})


def test_g10_a_batch_covers_the_orders_the_courier_names(cr):
    c = cr
    a, b = _courier_orders(c, c.pathao, [3000.0, 2000.0])
    r = _remittance(c, net_amount=2000.0)
    r.with_user(c.acct).action_load_orders(references="%s" % b.name)
    assert r.order_ids == b
    r.with_user(c.acct).action_submit()
    r.with_user(c.mgr).action_settle()
    # the other order stays open for the courier's next batch
    nxt = _remittance(c, net_amount=3000.0)
    nxt.with_user(c.acct).action_load_orders()
    assert nxt.order_ids == a


def test_g10_rider_and_courier_settlements_never_count_one_order_twice(cr):
    c = cr
    orders = _cod_orders(c, [3000.0])
    cons = orders.carrier_consignment_id
    cons.sudo().write({"courier_partner_id": c.pathao.id})  # carried by both, on paper
    r = _remittance(c, net_amount=3000.0)
    r.with_user(c.acct).action_load_orders()
    assert r.order_ids == orders
    rider = _cod(c, c.acct)
    rider.with_user(c.acct).action_load_orders()
    assert not rider.order_ids  # in a live courier remittance
    r.with_user(c.acct).action_dispute(reason="Wrong courier batch")
    rider.with_user(c.acct).action_load_orders()
    assert rider.order_ids == orders
    r2 = _remittance(c, net_amount=3000.0)
    with pytest.raises(UserError, match="already"), c.env.cr.savepoint():
        r2.with_user(c.acct).action_load_orders(references=orders.name)


def test_g10_charges_need_their_account(cr):
    c = cr
    c.env["ir.config_parameter"].sudo().set_param(CHARGES_PARAM, False)
    _courier_orders(c, c.pathao, [3000.0])
    r = _remittance(c, delivery_charges=60.0, net_amount=2940.0)
    r.with_user(c.acct).action_load_orders()
    r.with_user(c.acct).action_submit()
    with pytest.raises(UserError, match=CHARGES_PARAM), c.env.cr.savepoint():
        r.with_user(c.mgr).action_settle()
    assert r.state == "submitted" and not r.move_id


def test_g10_state_stamps_and_terms_cannot_be_forged(cr):
    c = cr
    _courier_orders(c, c.pathao, [3000.0])
    r = _remittance(c, net_amount=3000.0)
    r.with_user(c.acct).action_load_orders()
    for vals in ({"state": "settled"}, {"submitted_by_id": c.mgr.id}):
        with pytest.raises(REFUSED), c.env.cr.savepoint():
            r.with_user(c.acct).write(vals)
    r.with_user(c.acct).action_submit()
    with pytest.raises(UserError, match="submitted"), c.env.cr.savepoint():
        r.with_user(c.acct).write({"net_amount": 1.0})
    assert r.state == "submitted" and r.net_amount == 3000.0
    # the workspace form offers no workflow field
    from odoo.addons.cd_p03_portal.controllers.a08 import m50
    from odoo.addons.cd_p03_portal.controllers.a08.writable import WRITABLE

    surface = WRITABLE["fix.courier.remittance"]
    assert not {"state", "order_ids", "submitted_by_id", "settled_by_id", "move_id"} & surface
    assert {"courier_id", "batch_ref", "net_amount"} <= surface
    assert {"action_load_orders", "action_submit", "action_settle"} <= m50.SURFACES[
        "fix.courier.remittance"
    ]["actions"]
