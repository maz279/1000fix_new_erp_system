"""A05 cross-area follow-up (2026-11-06): an approved e-waste settlement
reaches its money document.

The A05 report recorded `ewaste.settlement_approved` as the one A05 event
waiting on a finance consumer (FF-48). This suite drives the real settlement
approval chain where it can, then delivers the event the way production
delivers it: ``cron_relay()`` as the superuser with this module's consumer
isolated on. Incentives and recycler fees raise a PENDING M50 payout
instruction; material-recovery income raises a draft M20 invoice; both are
idempotent per settlement. ``odoo_env`` rolls back after each test.
"""

import itertools
import json
from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
EVENT = "ewaste.settlement_approved"
_N = itertools.count(1)


@pytest.fixture
def w(odoo_env):
    """The A05 ERP (S3) M18 world: non-admin floor users, the D1 account
    parameters pointed at the test chart, an operating unit and a branch.
    Settlements are raised by the e-waste dispatcher on a basis that carries
    its operating unit, with the branch, payment method and payee account the
    approval pins."""
    from odoo.addons.cd_ewaste.tests.test_a05_s3_build import build

    x = build(odoo_env)
    try:
        yield x
    finally:
        x.close()


def _bank(w, partner):
    return w.env["res.partner.bank"].create(
        {"acc_number": "A5C7-%s-%d" % (partner.id, next(_N)), "partner_id": partner.id}
    )


def _settlement(w, kind="incentive", amount=5000.0):
    """A settlement on its proper basis, as the floor raises it: an incentive
    on one triaged collection of an operating unit (paid to the collection's
    customer); a recycler fee on one received batch (paid to the recycler's
    business contact); recovery income raised from the batch's recovery
    lines (action_raise_income: its amount is the lines' total, never typed)."""
    from odoo.addons.cd_ewaste.tests.test_a05_s3_build import (
        _incentive,
        _income,
        _received_batch,
    )

    if kind == "incentive":
        return _incentive(w, amount=amount)
    if kind == "recovery_income":
        _batch, _lines, rec = _income(w)
        rec.with_user(w.dispatcher).write({"branch_id": w.branch.id})
        return rec
    batch = _received_batch(w)
    contact = batch.partner_id.partner_id
    return (
        w.env["fix.ewaste.settlement"]
        .with_user(w.dispatcher)
        .create(
            {
                "kind": kind,
                "batch_id": batch.id,
                "partner_id": contact.id,
                "amount": amount,
                "branch_id": w.branch.id,
                "payment_method": "bank_transfer",
                "partner_bank_id": _bank(w, contact).id,
            }
        )
    )


def _approved(w, settlement):
    """Trusted staging of the routed M63 decision's result: the settlement is
    approved and its event sits in the outbox (the guards pin the terms; the
    consumer re-reads the record, never the payload)."""
    settlement.sudo()._guarded().write(
        {"state": "approved", "approved_by_id": w.env.uid, "approved_on": fields.Datetime.now()}
    )
    w.env["fix.event.outbox"].sudo().create(
        {
            "event_type": EVENT,
            "aggregate": "fix.ewaste.settlement",
            "aggregate_id": settlement.id,
            "payload": json.dumps({"kind": settlement.kind, "amount": settlement.amount}),
        }
    )
    return settlement


def _relay(w):
    Consumer = w.env["fix.event.consumer"].sudo()
    mine = Consumer.search([("event_type", "=", EVENT)])
    assert len(mine) == 1 and mine.model == "fix.a05.settlement.consumers"
    (Consumer.search([]) - mine).write({"active": False})
    mine.write({"active": True, "active_from": w.env.cr.now() - timedelta(minutes=1)})
    w.env["fix.event.outbox"].cron_relay()
    w.env.invalidate_all()


def _payout(w, settlement):
    return (
        w.env["fix.payment.execution"]
        .sudo()
        .search(
            [("source_model", "=", "fix.ewaste.settlement"), ("source_id", "=", settlement.id)],
            limit=1,
        )
    )


def _invoice(w, settlement):
    return (
        w.env["fix.ar.invoice"]
        .sudo()
        .search(
            [("source_model", "=", "fix.ewaste.settlement"), ("source_id", "=", settlement.id)],
            limit=1,
        )
    )


def test_an_incentive_raises_a_pending_m50_payout(w):
    s = _approved(w, _settlement(w, kind="incentive", amount=5000.0))
    _relay(w)
    pay = _payout(w, s)
    assert pay and pay.state == "pending", "the M50 instruction exists and is pending"
    assert pay.partner_id == s.collection_id.customer_id and pay.amount == 5000.0
    assert not _invoice(w, s)


def test_a_recycler_fee_also_goes_through_m50(w):
    s = _approved(w, _settlement(w, kind="recycler_fee", amount=12000.0))
    _relay(w)
    pay = _payout(w, s)
    assert pay and pay.amount == 12000.0
    assert pay.partner_id == s.batch_id.partner_id.partner_id  # the recycler's contact


def test_recovery_income_raises_a_draft_m20_invoice(w):
    s = _approved(w, _settlement(w, kind="recovery_income"))
    _relay(w)
    inv = _invoice(w, s)
    assert inv and inv.state == "draft"
    # the basis rule ties income to the batch's recycler contact; the
    # recovered-material lines' total is the taxable value (VAT is M51's, D2)
    assert inv.customer_id == s.batch_id.partner_id.partner_id
    assert sum(inv.line_ids.mapped("taxable_amount")) == pytest.approx(s.amount)
    assert inv.manual_reason and "material-recovery" in inv.manual_reason.lower()
    assert not _payout(w, s)


def test_relaying_twice_raises_one_document(w):
    s = _approved(w, _settlement(w, kind="incentive", amount=3000.0))
    _relay(w)
    _relay(w)
    payouts = (
        w.env["fix.payment.execution"]
        .sudo()
        .search([("source_model", "=", "fix.ewaste.settlement"), ("source_id", "=", s.id)])
    )
    assert len(payouts) == 1


def test_a_forged_payload_amount_is_refused(w):
    s = _approved(w, _settlement(w, kind="incentive", amount=5000.0))
    row = (
        w.env["fix.event.outbox"]
        .sudo()
        .search([("event_type", "=", EVENT), ("aggregate_id", "=", s.id)], limit=1)
    )
    payload = json.loads(row.payload)
    payload["amount"] = 999999.0
    row.payload = json.dumps(payload)
    _relay(w)
    assert not _payout(w, s)


def test_a_settlement_that_is_not_approved_is_refused(w):
    s = _settlement(w, kind="incentive", amount=5000.0)  # still draft
    w.env["fix.event.outbox"].sudo().create(
        {
            "event_type": EVENT,
            "aggregate": "fix.ewaste.settlement",
            "aggregate_id": s.id,
            "payload": json.dumps({"kind": "incentive", "amount": 5000.0}),
        }
    )
    _relay(w)
    assert not _payout(w, s) and not _invoice(w, s)


def test_the_consumer_runs_only_from_the_relay(w):
    s = _approved(w, _settlement(w, kind="incentive", amount=5000.0))
    clerk = (
        w.env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A5C7 clerk",
                "login": "a5c7.clerk@a05.test",
                "group_ids": [(6, 0, [w.env.ref("base.group_user").id])],
            }
        )
    )
    event = {
        "aggregate": "fix.ewaste.settlement",
        "aggregate_id": s.id,
        "payload": '{"amount": 5000.0}',
    }
    with pytest.raises(AccessError, match="relay"), w.env.cr.savepoint():
        w.env["fix.a05.settlement.consumers"].with_user(clerk).consume_ewaste_settlement_approved(
            event
        )
