"""A04 §6 C7 (2026-11-04): an approved warranty claim becomes a receivable.

working/A04_Workflow_and_Approval_Report.md (M09): the brand decision
provenance, amount pinning and remittance reconciliation landed with the
C2-C13 controls - and warranty_claim.decided was consumed by nobody, so the
OEM's debt existed only if finance noticed by hand.

The source event is produced by the real decision path (cd_warranty_claims'
own A04 suite proves the keying and inbox controls), then delivered the way
production delivers it: ``cron_relay()`` as the superuser with this module's
consumer isolated on. The invoice is DRAFT - finance reviews and issues it.
``odoo_env`` rolls back after each test.
"""

from datetime import timedelta

import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
EVENT = "warranty_claim.decided"


def _relay(env):
    Consumer = env["fix.event.consumer"].sudo()
    mine = Consumer.search([("event_type", "=", EVENT)])
    assert len(mine) == 1 and mine.model == "fix.a04.claim.consumers"
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


def _submitted(w, amount=12500.0):
    claim = w.full_pack(w.claim(amount=amount))
    claim.with_user(w.clerk).action_submit()
    return claim


def _event_dict(env, claim):
    row = (
        env["fix.event.outbox"]
        .sudo()
        .search(
            [("event_type", "=", EVENT), ("aggregate_id", "=", claim.id)],
            order="id desc",
            limit=1,
        )
    )
    assert row, "the decision never published its event"
    return row._relay_event_dict()


def _invoices(env, claim):
    return (
        env["fix.ar.invoice"]
        .sudo()
        .search([("source_model", "=", claim._name), ("source_id", "=", claim.id)])
    )


# ---------------------------------------------------------------- wiring


def test_the_consumer_row_is_wired(w):
    (row,) = w.env["fix.event.consumer"].sudo().search([("event_type", "=", EVENT)])
    assert (row.model, row.method, row.module) == (
        "fix.a04.claim.consumers",
        "consume_warranty_claim_decided",
        "cd_billing_engine",
    )


def test_an_approved_claim_raises_a_draft_invoice_on_the_oem(w):
    env = w.env
    oem = env["res.partner"].create({"name": "OEM %s" % w.brand.name, "ref": w.brand.code})
    claim = _submitted(w)
    claim.action_decide(approved=True)  # the brand-API path (superuser only)
    claim.invalidate_recordset()
    assert claim.state == "approved"
    _relay(env)
    (invoice,) = _invoices(env, claim)
    assert invoice.state == "draft"  # nothing is issued or collected by the relay
    assert invoice.customer_id == oem
    assert invoice.company_id == claim.company_id
    assert invoice.operating_unit_id == claim.operating_unit_id
    (line,) = invoice.line_ids
    assert (line.taxable_amount, line.vat_amount, line.line_total) == (
        claim.approved_amount,
        0.0,
        claim.approved_amount,
    )
    assert claim.claim_no in line.description
    # a replay raises nothing more
    result = env["fix.a04.claim.consumers"].consume_warranty_claim_decided(_event_dict(env, claim))
    assert result == {"model": "fix.ar.invoice", "id": invoice.id, "created": False}
    assert len(_invoices(env, claim)) == 1


def test_a_rejected_claim_has_no_money_leg(w):
    claim = _submitted(w)
    claim.action_decide(approved=False, reason="Liquid ingress")
    claim.invalidate_recordset()
    assert claim.state == "rejected"
    _relay(w.env)
    assert not _invoices(w.env, claim)  # acknowledged as a no-op, not dead-lettered


def test_an_oem_partner_that_is_not_unique_refuses(w):
    w.env["res.partner"].create({"name": "OEM twin A", "ref": w.brand.code})
    w.env["res.partner"].create({"name": "OEM twin B", "ref": w.brand.code})
    claim = _submitted(w)
    claim.action_decide(approved=True)
    claim.invalidate_recordset()
    _relay(w.env)
    assert not _invoices(w.env, claim)  # a guess would bill the wrong OEM


def test_a_forged_amount_is_refused(w):
    w.env["res.partner"].create({"name": "OEM %s" % w.brand.name, "ref": w.brand.code})
    claim = _submitted(w)
    claim.action_decide(approved=True)
    event = _event_dict(w.env, claim)
    forged = dict(event, payload=dict(event["payload"], approved_amount=999999.0))
    assert "999999" in _attempt(
        w.env, lambda: w.env["fix.a04.claim.consumers"].consume_warranty_claim_decided(forged)
    )
    assert not _invoices(w.env, claim)


def test_only_the_relay_may_run_the_consumer(w):
    w.env["res.partner"].create({"name": "OEM %s" % w.brand.name, "ref": w.brand.code})
    claim = _submitted(w)
    claim.action_decide(approved=True)
    event = _event_dict(w.env, claim)
    with pytest.raises(AccessError, match="event relay"):
        (w.env["fix.a04.claim.consumers"].with_user(w.plain).consume_warranty_claim_decided(event))
