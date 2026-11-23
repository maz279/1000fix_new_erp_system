# A10 deep audit (2026-11-23, D-A10-4): the M36 quotation e-signature runs
# through the M24 envelope — sealed bytes, the customer's own signature, the
# completion certificate — and completion accepts the quotation.
#
# ruff: noqa: F401, F811  (fixtures are imported and used as parameters)
from datetime import timedelta

import pytest
from odoo.addons.cd_quotation.tests.test_a04_m36_controls import _sent_quote, c
from odoo.exceptions import UserError


def _only_my_consumer(env):
    Consumer = env["fix.event.consumer"].sudo()
    mine = Consumer.search([("event_type", "=", "envelope.completed")])
    assert mine, "the envelope completion consumer is not registered"
    (Consumer.search([]) - mine).write({"active": False})
    mine.write({"active": True, "active_from": env.cr.now() - timedelta(minutes=1)})
    return mine


def _relay(env):
    _only_my_consumer(env)
    return env["fix.event.outbox"].sudo().cron_relay()


def test_an_issued_quotation_is_sent_for_signature_through_m24(c):
    env = c.env
    quote = _sent_quote(c)
    assert quote.esign_state == "sent"  # issuing marks the signature requested
    quote.with_user(c.author).action_request_esignature()
    quote.invalidate_recordset()
    envelope = quote.esign_envelope_id
    assert envelope and envelope.state == "sent"
    assert envelope.evidence_hash  # the bytes and signers were sealed
    assert envelope.document_id.res_model == "fix.quotation"
    assert envelope.document_id.res_id == quote.id
    assert quote.esign_state == "sent"
    assert envelope.signer_ids.partner_id == c.customer
    # a second request is refused (one envelope per quotation)
    with pytest.raises(UserError, match="already has envelope"), env.cr.savepoint():
        quote.with_user(c.author).action_request_esignature()


def test_the_customers_signature_accepts_the_quotation(c):
    env = c.env
    quote = _sent_quote(c)
    quote.with_user(c.author).action_request_esignature()
    envelope = quote.esign_envelope_id
    signer = envelope.signer_ids
    signer.sudo().action_sign(provider="internal-test")
    envelope.sudo().action_check_complete()
    envelope.invalidate_recordset()
    assert envelope.state == "completed"
    assert envelope.completion_certificate_id  # M24's own certificate
    _relay(env)
    quote.invalidate_recordset()
    assert quote.state == "accepted"
    assert quote.acceptance_method == "esign"
    assert "M24 envelope" in (quote.acceptance_ref or "")
    assert quote.esign_state == "signed"
    # a replayed event never accepts twice
    _relay(env)
    quote.invalidate_recordset()
    assert quote.state == "accepted"
