"""A04 §6 C7 (2026-11-04): an approved storefront refund moves money.

working/A04_Workflow_and_Approval_Report.md (M38): the return window,
inspection grade and DOFA approval decided the refund - and the event was
consumed by nobody, so the customer's money moved only if finance noticed.

The source event is produced by the real storefront chain (cd_storefront's
own A04 suite proves the role gates), then delivered the way production
delivers it: ``cron_relay()`` as the superuser with this module's consumer
isolated on. The refund goes back the way it came (a PENDING M50
instruction on the order's rail), or a draft M20 credit note against the
order's invoice when one is left to credit (Mushak 6.7). ``odoo_env`` rolls
back after each test.
"""

import types
from datetime import timedelta

import pytest
from odoo import Command, fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
EVENT = "storefront.refund_approved"


@pytest.fixture
def w(odoo_env):
    env = odoo_env
    sf = "cd_storefront.group_fix_storefront_"

    def mk(login, *xmlids):
        return (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": login,
                    "login": "a4c7sf.%s@a04.test" % login,
                    "group_ids": [
                        (6, 0, [env.ref("base.group_user").id] + [env.ref(x).id for x in xmlids])
                    ],
                }
            )
        )

    x = types.SimpleNamespace(env=env)
    x.clerk = mk("clerk")
    x.operator = mk("operator", sf + "operator")
    x.cashier = mk("cashier", sf + "payment_officer")
    x.approver = mk(
        "approver",
        sf + "refund_approver",
        "cd_entity_config.group_dofa_tier_1",
        "cd_entity_config.group_dofa_tier_2",
        "cd_entity_config.group_dofa_tier_3",
    )
    x.customer = env["res.partner"].create(
        {"name": "A4 C7 SF Customer", "street": "House 1", "city": "Dhaka"}
    )
    x.product = env["product.template"].create(
        {"name": "A4 C7 Charger", "list_price": 2500.0, "sale_ok": True}
    )
    x.ou = env["operating.unit"].search([], limit=1)
    return x


def _relay(env):
    Consumer = env["fix.event.consumer"].sudo()
    mine = Consumer.search([("event_type", "=", EVENT)])
    assert len(mine) == 1 and mine.model == "fix.a04.storefront.consumers"
    (Consumer.search([]) - mine).write({"active": False})
    mine.write({"active": True, "active_from": env.cr.now() - timedelta(minutes=1)})
    env["fix.event.outbox"].cron_relay()
    env.invalidate_all()


def _attempt(env, fn):
    try:
        with env.cr.savepoint():
            fn()
    except REFUSED as exc:
        return str(exc) or type(exc).__name__
    return None


def _placed(w, rail="bkash"):
    cart = w.env["fix.storefront.cart"].with_user(w.clerk).create({"customer_id": w.customer.id})
    w.env["fix.storefront.cart.line"].with_user(w.clerk).create(
        {"cart_id": cart.id, "product_id": w.product.id, "quantity": 1}
    )
    return cart.action_place_order(shipping_method="standard_delivery", payment_rail=rail)


def _paid(w, order):
    ref = "TRX-C7-%s" % order.id
    w.env["fix.ar.receipt"].create(
        {
            "customer_id": w.customer.id,
            "amount": order.sudo().total_amount,
            "method": "bkash",
            "reference": ref,
            "state": "confirmed",
        }
    )
    order.with_user(w.cashier).action_confirm_payment(payment_ref=ref)
    return order


def _delivered(w):
    order = _paid(w, _placed(w))
    cons = w.env["fix.consignment"].create(
        {
            "operating_unit_id": w.ou.id,
            "consignment_type": "delivery",
            "scheduled_date": fields.Datetime.now(),
        }
    )
    cons.write({"state": "delivered"})  # setup by the superuser (M03's own suite)
    order.with_user(w.operator).action_dispatch(carrier_consignment_id=cons.id)
    order.with_user(w.operator).action_deliver()
    return order


def _refund_approved(w, order=None):
    """A return inspected grade A and approved from the DOFA inbox."""
    order = order or _delivered(w)
    ret = (
        w.env["fix.storefront.return"]
        .with_user(w.operator)
        .create(
            {
                "order_id": order.id,
                "customer_id": order.customer_id.id,
                "reason": "defective",
                "refund_amount": order.sudo().total_amount,
            }
        )
    )
    ret.with_user(w.operator).action_approve()
    ret.with_user(w.operator).action_receive_and_inspect(condition="grade_a")
    approve_via_inbox(ret, w.approver, requester=w.operator, justification="Defective")
    ret.invalidate_recordset()
    assert ret.state == "refund_approved"
    return ret


def _event_dict(env, ret):
    row = (
        env["fix.event.outbox"]
        .sudo()
        .search(
            [("event_type", "=", EVENT), ("aggregate_id", "=", ret.id)],
            order="id desc",
            limit=1,
        )
    )
    assert row, "the refund approval never published its event"
    return row._relay_event_dict()


def _executions(env, ret):
    return (
        env["fix.payment.execution"]
        .sudo()
        .search([("source_model", "=", ret._name), ("source_id", "=", ret.id)])
    )


# ---------------------------------------------------------------- wiring


def test_the_consumer_row_is_wired(w):
    (row,) = w.env["fix.event.consumer"].sudo().search([("event_type", "=", EVENT)])
    assert (row.model, row.method, row.module) == (
        "fix.a04.storefront.consumers",
        "consume_storefront_refund_approved",
        "cd_cash_position",
    )


def _bridged(env):
    """cd_storefront_finance invoices every paid order, so its refund is a
    credit note against that invoice (raised by the bridge) instead of the
    direct instruction this consumer raises for an uninvoiced order."""
    return "ar_credit_note_id" in env["fix.storefront.return"]._fields


def test_the_refund_goes_back_over_the_rail_it_came_in_on(w):
    ret = _refund_approved(w)
    if _bridged(w.env):
        _relay(w.env)
        note = ret.sudo().ar_credit_note_id
        assert note and not _executions(w.env, ret)  # the credit note pays it
        assert note._fix_refund_method() == "mobile_fs"  # the order paid over bKash
        result = w.env["fix.a04.storefront.consumers"].consume_storefront_refund_approved(
            _event_dict(w.env, ret)
        )
        assert result == {"model": "fix.credit.note", "id": note.id, "created": False}
        return
    _relay(w.env)
    (pay,) = _executions(w.env, ret)
    assert (pay.state, pay.amount) == ("pending", ret.refund_amount)
    assert pay.partner_id == ret.customer_id
    assert pay.method == "mobile_fs"  # the order paid over bKash
    assert (
        not w.env["fix.credit.note"]
        .sudo()
        .search([("source_model", "=", ret._name), ("source_id", "=", ret.id)])
    )
    # a replay raises nothing more
    result = w.env["fix.a04.storefront.consumers"].consume_storefront_refund_approved(
        _event_dict(w.env, ret)
    )
    assert result == {"model": "fix.payment.execution", "id": pay.id, "created": False}
    assert len(_executions(w.env, ret)) == 1


def test_the_refund_credits_the_orders_invoice_when_one_is_left(w):
    ret = _refund_approved(w)
    order = ret.order_id
    if _bridged(w.env):
        # the bridge already invoiced the order and credited it on approval
        invoice = order.sudo().ar_invoice_id
        _relay(w.env)
        assert invoice and not _executions(w.env, ret)
        note = ret.sudo().ar_credit_note_id
        assert (note.invoice_id, note.reason_code) == (invoice, "return")
        assert note.amount == min(ret.refund_amount, invoice.total_payable)
        result = w.env["fix.a04.storefront.consumers"].consume_storefront_refund_approved(
            _event_dict(w.env, ret)
        )
        assert result == {"model": "fix.credit.note", "id": note.id, "created": False}
        return
    invoice = w.env["fix.ar.invoice"].create(
        {
            "operating_unit_id": w.ou.id,
            "customer_id": order.customer_id.id,
            "source_model": order._name,
            "source_id": order.id,
            "state": "issued",
            "name": "INV/A4C7/%s" % order.id,
            "line_ids": [
                Command.create(
                    {
                        "description": "sale",
                        "taxable_amount": 2173.91,
                        "vat_amount": 326.09,
                        "line_total": 2500.0,
                    }
                )
            ],
        }
    )
    _relay(w.env)
    assert not _executions(w.env, ret)  # the credit note pays this one
    (note,) = (
        w.env["fix.credit.note"]
        .sudo()
        .search([("source_model", "=", ret._name), ("source_id", "=", ret.id)])
    )
    assert (note.invoice_id, note.reason_code, note.state) == (invoice, "return", "draft")
    assert note.amount == min(ret.refund_amount, 2500.0)
    result = w.env["fix.a04.storefront.consumers"].consume_storefront_refund_approved(
        _event_dict(w.env, ret)
    )
    assert result == {"model": "fix.credit.note", "id": note.id, "created": False}


def test_a_forged_amount_and_a_wrong_state_are_refused(w):
    ret = _refund_approved(w)
    event = _event_dict(w.env, ret)
    forged = dict(event, payload=dict(event["payload"], refund_amount=999999.0))
    assert "999999" in _attempt(
        w.env,
        lambda: w.env["fix.a04.storefront.consumers"].consume_storefront_refund_approved(forged),
    )
    assert not _executions(w.env, ret)
    # an event naming a record that is not there is refused, not guessed at
    assert "no fix.storefront.return" in _attempt(
        w.env,
        lambda: w.env["fix.a04.storefront.consumers"].consume_storefront_refund_approved(
            dict(event, aggregate_id=0)
        ),
    )


def test_only_the_relay_may_run_the_consumer(w):
    ret = _refund_approved(w)
    event = _event_dict(w.env, ret)
    with pytest.raises(AccessError, match="event relay"):
        (
            w.env["fix.a04.storefront.consumers"]
            .with_user(w.clerk)
            .consume_storefront_refund_approved(event)
        )
