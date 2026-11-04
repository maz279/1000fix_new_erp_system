# Behavioural tests for the M24 e-signature envelope on the live ORM
# (`odoo_env`, rolled back after every test).
import base64
import contextlib
import hashlib
import json

import pytest
from odoo import fields
from odoo.exceptions import UserError


@contextlib.contextmanager
def _rejects(env, exc, match):
    with pytest.raises(exc, match=match) as info, env.cr.savepoint():
        yield info


def _envelope(env, signers=()):
    doc = env["fix.document"].attach(
        name="Repair Contract", datas=base64.b64encode(b"contract"), document_type="contract"
    )
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    partners = {name: env["res.partner"].create({"name": name}) for name, _seq in signers}
    return env["fix.esignature.envelope"].create(
        {
            "name": "Contract signing",
            "document_id": doc.id,
            "operating_unit_id": ou.id,
            "signer_ids": [
                (0, 0, {"partner_id": partners[name].id, "sequence": seq}) for name, seq in signers
            ],
        }
    )


def _events(env, event_type, envelope):
    return env["fix.event.outbox"].search(
        [
            ("event_type", "=", event_type),
            ("aggregate", "=", "fix.esignature.envelope"),
            ("aggregate_id", "=", envelope.id),
        ]
    )


def test_send_without_signers_is_refused(odoo_env):
    envelope = _envelope(odoo_env)
    with _rejects(odoo_env, UserError, match="at least one signer"):
        envelope.action_send()
    assert envelope.state == "draft"
    assert not _events(odoo_env, "envelope.sent", envelope)


def test_send_seals_evidence_hash_over_document_and_signing_order(odoo_env):
    envelope = _envelope(odoo_env, signers=[("Branch Manager", 20), ("Customer", 10)])
    envelope.action_send()

    expected = hashlib.sha256(
        json.dumps(
            {"document": "Repair Contract", "signers": [["Customer", 10], ["Branch Manager", 20]]},
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()
    assert envelope.state == "sent"
    assert envelope.evidence_hash == expected
    events = _events(odoo_env, "envelope.sent", envelope)
    assert json.loads(events.payload) == {"subject": "Contract signing"}


def test_evidence_hash_changes_when_signing_order_changes(odoo_env):
    a = _envelope(odoo_env, signers=[("Customer", 10), ("Branch Manager", 20)])
    b = _envelope(odoo_env, signers=[("Customer", 20), ("Branch Manager", 10)])
    assert a._compute_evidence() != b._compute_evidence()


def test_envelope_completes_only_when_every_signer_has_signed(odoo_env):
    envelope = _envelope(odoo_env, signers=[("Customer", 10), ("Branch Manager", 20)])
    envelope.action_send()
    first, second = envelope.signer_ids.sorted("sequence")

    first.signed_at = fields.Datetime.now()
    envelope.action_check_complete()
    assert envelope.state == "sent"
    assert not envelope.completed_at

    second.signed_at = fields.Datetime.now()
    envelope.action_check_complete()
    assert envelope.state == "completed"
    assert envelope.completed_at
    events = _events(odoo_env, "envelope.completed", envelope)
    assert json.loads(events.payload) == {"evidence_hash": envelope.evidence_hash}


def test_signing_order_sequences_must_be_unique(odoo_env):
    with _rejects(odoo_env, UserError, match="sequences must be unique"):
        _envelope(odoo_env, signers=[("Customer", 10), ("Witness", 10)])
    envelope = _envelope(odoo_env, signers=[("Customer", 10)])
    other = odoo_env["res.partner"].create({"name": "Second"})
    with _rejects(odoo_env, UserError, match="sequences must be unique"):
        odoo_env["fix.esignature.signer"].create(
            {"envelope_id": envelope.id, "partner_id": other.id, "sequence": 10}
        )
    assert len(envelope.signer_ids) == 1


# --- A04 integration (2026-11-04): a completed signature cannot be typed ------
def _clerk(env):
    return env["res.users"].create(
        {
            "name": "M24 Clerk",
            "login": "m24_guard_clerk",
            "group_ids": [(6, 0, [env.ref("base.group_user").id])],
        }
    )


def test_a_user_cannot_type_a_completed_envelope_or_a_signature(odoo_env):
    clerk = _clerk(odoo_env)
    envelope = _envelope(odoo_env, signers=[("Customer", 10)])
    as_clerk = envelope.with_user(clerk)
    with _rejects(odoo_env, UserError, match="cannot be set directly"):
        as_clerk.write({"state": "completed"})
    with _rejects(odoo_env, UserError, match="cannot be set directly"):
        as_clerk.write({"evidence_hash": "forged", "completed_at": fields.Datetime.now()})
    with _rejects(odoo_env, UserError, match="cannot be set directly"):
        odoo_env["fix.esignature.envelope"].with_user(clerk).create(
            {
                "name": "Forged",
                "document_id": envelope.document_id.id,
                "operating_unit_id": envelope.operating_unit_id.id,
                "state": "completed",
            }
        )
    as_clerk.action_send()  # the transition itself works for a plain user
    signer = envelope.signer_ids.with_user(clerk)
    with _rejects(odoo_env, UserError, match="cannot be set directly"):
        signer.write({"signed_at": fields.Datetime.now(), "signature_provider": "TYPED"})
    with _rejects(odoo_env, UserError, match="provider only"):
        signer._esign_provider_record_signature("TYPED")
    assert envelope.state == "sent" and not envelope.signer_ids.signed_at


def test_a_sent_envelope_is_sealed(odoo_env):
    clerk = _clerk(odoo_env)
    envelope = _envelope(odoo_env, signers=[("Customer", 10)])
    envelope.with_user(clerk).action_send()
    other = odoo_env["res.partner"].create({"name": "Late Signer"})
    with _rejects(odoo_env, UserError, match="while the envelope is a draft"):
        odoo_env["fix.esignature.signer"].with_user(clerk).create(
            {"envelope_id": envelope.id, "partner_id": other.id, "sequence": 20}
        )
    with _rejects(odoo_env, UserError, match="while the envelope is a draft"):
        envelope.signer_ids.with_user(clerk).unlink()
    with _rejects(odoo_env, UserError, match="cannot be set directly"):
        envelope.signer_ids.with_user(clerk).write({"partner_id": other.id})
    with _rejects(odoo_env, UserError, match="Only a draft envelope"):
        envelope.with_user(clerk).action_send()


def test_the_provider_records_the_signature_and_completes(odoo_env):
    envelope = _envelope(odoo_env, signers=[("Customer", 10)])
    envelope.action_send()
    envelope.signer_ids.sudo()._esign_provider_record_signature("L6-SIG-1")
    assert envelope.state == "completed" and envelope.completed_at
    assert envelope.signer_ids.signature_provider == "L6-SIG-1"
    with _rejects(odoo_env, UserError, match="not out for signature"):
        envelope.signer_ids.sudo()._esign_provider_record_signature("L6-SIG-2")
