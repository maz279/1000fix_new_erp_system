"""A02 ERP pass 2, X5-05 (owner decision D24): a warranty-claim write-off
reaches AR.

M09 wrote off what the brand would never pay and published
warranty_claim.written_off; nothing consumed it, so the brand's M20 invoice
stayed open on AR for money already forgone. The M09 Finance Manager approval
is the M20 approval: the consumer writes the amount off the OEM invoice
(Dr bad debts / Cr AR), once per write-off. The claim write-off is raised and
decided by NON-admin users with the real M09 roles; the event is delivered the
way production delivers it (cron_relay as the superuser).
``odoo_env`` rolls back after each test.
"""

from datetime import timedelta

import pytest
from odoo.addons.cd_billing_engine.tests.test_a04_c7_claim_consumer import (
    _invoices,
    _relay,
    _submitted,
)
from odoo.exceptions import AccessError, UserError

BILLING = "cd_billing_engine.account_code."
FINANCE = "account.group_account_manager"
EVENT = "warranty_claim.written_off"


def _relay_writeoffs(env):
    # the decision relay (fixture) deactivates every other consumer, this one too
    Consumer = env["fix.event.consumer"].sudo().with_context(active_test=False)
    mine = Consumer.search([("event_type", "=", EVENT)])
    assert len(mine) == 1 and mine.method == "consume_warranty_claim_written_off"
    (Consumer.search([("active", "=", True)]) - mine).write({"active": False})
    mine.write({"active": True, "active_from": env.cr.now() - timedelta(minutes=1)})
    env["fix.event.outbox"].cron_relay()
    env.invalidate_all()


@pytest.fixture
def wo(w):
    env = w.env
    params = env["ir.config_parameter"].sudo()

    def account(key, kind):
        return env["account.account"].create(
            {"code": "WOA%s%d" % (key, w.brand.id), "name": "WO %s" % key, "account_type": kind}
        )

    w.ar = account("AR", "asset_receivable")
    w.bank = account("BNK", "asset_cash")
    w.bad_debts = account("BAD", "expense")
    params.set_param(BILLING + "ar", w.ar.code)
    params.set_param(BILLING + "bank", w.bank.code)
    params.set_param(BILLING + "writeoff_expense", w.bad_debts.code)
    params.set_param(BILLING + "ecl_provision", "")
    w.oem = env["res.partner"].create({"name": "OEM %s" % w.brand.name, "ref": w.brand.code})
    claim = _submitted(w)
    claim.action_decide(approved=True)
    _relay(env)
    (w.invoice,) = _invoices(env, claim)
    w.claim = claim
    w.finance = w.user("a02r2_wo_finance", FINANCE)

    def write_off(amount, reason="Brand capped labour"):
        rec = (
            env["fix.claim.writeoff"]
            .with_user(w.clerk)
            .create({"claim_id": claim.id, "amount": amount, "reason": reason})
        )
        rec.with_user(w.finance).action_approve()
        return rec.sudo()  # the clerk does not read AR; the assertions do

    w.write_off = write_off
    return w


def _lines(move, account):
    return move.line_ids.filtered(lambda line: line.account_id == account)


def test_the_consumer_row_is_wired(wo):
    Consumer = wo.env["fix.event.consumer"].sudo().with_context(active_test=False)
    (row,) = Consumer.search([("event_type", "=", EVENT)])
    assert (row.model, row.method, row.module) == (
        "fix.a04.claim.consumers",
        "consume_warranty_claim_written_off",
        "cd_billing_engine",
    )


def test_a_claim_write_off_closes_the_oem_invoice_on_bad_debts(wo):
    w = wo
    w.invoice.sudo().action_issue()
    w.claim.with_user(w.officer).action_record_remittance(10000.0, "BANK-SHORT")
    w.invoice.invalidate_recordset()
    assert round(w.invoice.amount_residual, 2) == 2500.0
    rec = w.write_off(2500.0)
    assert w.claim.state == "written_off"
    _relay_writeoffs(w.env)
    ar = rec.ar_writeoff_id
    assert ar and ar.state == "posted" and ar.amount == 2500.0
    assert ar.fin_approved_by_id == w.finance  # the M09 decider is the M20 approver
    assert _lines(ar.move_id, w.bad_debts).debit == 2500.0
    (credit,) = _lines(ar.move_id, w.ar)
    assert credit.credit == 2500.0 and credit.partner_id == w.oem
    w.invoice.invalidate_recordset()
    assert w.invoice.state == "written_off" and w.invoice.amount_residual == 0.0


def test_a_write_off_is_booked_once(wo):
    w = wo
    w.invoice.sudo().action_issue()
    w.claim.with_user(w.officer).action_record_remittance(10000.0, "BANK-SHORT")
    rec = w.write_off(2500.0)
    _relay_writeoffs(w.env)
    first = rec.ar_writeoff_id
    # a redelivered event (the relay retries) books nothing more
    row = (
        w.env["fix.event.outbox"]
        .sudo()
        .search([("event_type", "=", EVENT), ("aggregate_id", "=", w.claim.id)], limit=1)
    )
    w.env["fix.a04.claim.consumers"].sudo().consume_warranty_claim_written_off(
        row._relay_event_dict()
    )
    assert w.env["fix.ar.writeoff"].search_count([("claim_writeoff_id", "=", rec.id)]) == 1
    assert rec.ar_writeoff_id == first


def test_a_partial_write_off_leaves_the_rest_owing(wo):
    w = wo
    w.invoice.sudo().action_issue()
    rec = w.write_off(2000.0)
    _relay_writeoffs(w.env)
    assert rec.ar_writeoff_id.amount == 2000.0
    w.invoice.invalidate_recordset()
    assert w.invoice.state == "issued"
    assert round(w.invoice.amount_residual, 2) == round(w.invoice.total_payable - 2000.0, 2)


def test_a_write_off_waits_for_the_issued_invoice_then_books_once(wo):
    """Nothing is on AR before finance issues the brand's invoice. Pass 2
    deferred the booking to the issue; A04 refuses the approval instead (the
    two were built in parallel and merged as ONE routine): a write-off is not
    approved against a receivable that does not exist yet, and once the
    invoice is issued the same approval books it, with the M09 decider."""
    w = wo
    assert w.invoice.state == "draft"
    pending = (
        w.env["fix.claim.writeoff"]
        .with_user(w.clerk)
        .create({"claim_id": w.claim.id, "amount": 12500.0, "reason": "Brand capped labour"})
    )
    with pytest.raises(UserError, match="issued first"), w.env.cr.savepoint():
        pending.with_user(w.finance).action_approve()
    assert pending.state == "requested" and not pending.sudo().ar_writeoff_id
    w.invoice.sudo().action_issue()
    pending.with_user(w.finance).action_approve()
    _relay_writeoffs(w.env)  # the consumer finds it booked: still one
    rec = pending.sudo()
    assert rec.ar_writeoff_id.state == "posted"
    assert rec.ar_writeoff_id.fin_approved_by_id == w.finance
    assert w.env["fix.ar.writeoff"].sudo().search_count([("claim_writeoff_id", "=", rec.id)]) == 1
    w.invoice.invalidate_recordset()
    assert w.invoice.state == "written_off"


def test_the_consumer_is_relay_only_and_refuses_an_undecided_write_off(wo):
    w = wo
    w.invoice.sudo().action_issue()
    pending = (
        w.env["fix.claim.writeoff"]
        .with_user(w.clerk)
        .create({"claim_id": w.claim.id, "amount": 1000.0, "reason": "requested only"})
    )
    event = {
        "aggregate": "fix.warranty.claim",
        "aggregate_id": w.claim.id,
        "payload": {"writeoff_no": pending.name, "amount": 1000.0},
    }
    Consumers = w.env["fix.a04.claim.consumers"]
    with pytest.raises(AccessError):
        Consumers.with_user(w.finance).consume_warranty_claim_written_off(event)
    with pytest.raises(UserError, match="not approved"):
        Consumers.sudo().consume_warranty_claim_written_off(event)
    assert not w.env["fix.ar.writeoff"].sudo().search([("claim_writeoff_id", "=", pending.id)])
