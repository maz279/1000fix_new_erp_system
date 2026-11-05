# Behavioural tests for the M24 e-signature envelope on the live ORM
# (`odoo_env`, rolled back after every test).
#
# A10 D1 (2026-11-05): a signature is an act of the signer's own login in
# sequence, over sealed file bytes; completion re-hashes the bytes and files
# a certificate. These journeys run at superuser level; the non-admin
# three-way attacks live in test_a10_d1_controls.py.
import base64
import contextlib
import hashlib
import json
from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import UserError

SEND_SECONDS = 3 * 24 * 3600


@contextlib.contextmanager
def _rejects(env, exc, match):
    with pytest.raises(exc, match=match) as info, env.cr.savepoint():
        yield info


def _envelope(env, signers=(), raw=b"contract", name="Repair Contract"):
    doc = env["fix.document"].attach(
        name=name, datas=base64.b64encode(raw), document_type="contract"
    )
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    partners = {n: env["res.partner"].create({"name": n}) for n, _seq in signers}
    return env["fix.esignature.envelope"].create(
        {
            "name": "Contract signing",
            "document_id": doc.id,
            "operating_unit_id": ou.id,
            "signer_ids": [
                (0, 0, {"partner_id": partners[n].id, "sequence": seq}) for n, seq in signers
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


def _expected_evidence(envelope):
    doc = envelope.document_id
    payload = json.dumps(
        {
            "document": doc.name or "",
            "bytes_sha256": hashlib.sha256(base64.b64decode(doc.attachment_id.datas)).hexdigest(),
            "signers": [
                (s.partner_id.name or "", s.sequence)
                for s in envelope.signer_ids.sorted("sequence")
            ],
        },
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def test_send_without_signers_is_refused(odoo_env):
    envelope = _envelope(odoo_env)
    with _rejects(odoo_env, UserError, match="at least one signer"):
        envelope.action_send()
    assert envelope.state == "draft"
    assert not _events(odoo_env, "envelope.sent", envelope)


def test_send_seals_evidence_over_bytes_and_order_and_locks_the_file(odoo_env):
    envelope = _envelope(odoo_env, signers=[("Branch Manager", 20), ("Customer", 10)])
    envelope.action_send()

    assert envelope.state == "sent"
    assert envelope.evidence_hash == _expected_evidence(envelope)
    assert envelope.deadline == fields.Datetime.add(envelope.sent_at, seconds=SEND_SECONDS)
    assert envelope.document_id.signature_locked  # the file is sealed
    events = _events(odoo_env, "envelope.sent", envelope)
    assert json.loads(events.payload) == {
        "subject": "Contract signing",
        "document": "Repair Contract",
        "evidence_hash": envelope.evidence_hash,
    }


def test_same_name_different_bytes_seal_differently(odoo_env):
    # the audit probe: 'Pay 5,000' and 'Pay 500,000' under one name
    small = _envelope(odoo_env, signers=[("Customer", 10)], raw=b"Pay BDT 5,000 only")
    large = _envelope(odoo_env, signers=[("Customer", 10)], raw=b"Pay BDT 500,000 only")
    small.action_send()
    large.action_send()
    assert small.evidence_hash != large.evidence_hash


def test_evidence_hash_changes_when_signing_order_changes(odoo_env):
    a = _envelope(odoo_env, signers=[("Customer", 10), ("Branch Manager", 20)])
    b = _envelope(odoo_env, signers=[("Customer", 20), ("Branch Manager", 10)])
    assert a._compute_evidence() != b._compute_evidence()


def test_envelope_completes_only_when_every_signer_has_signed(odoo_env):
    envelope = _envelope(odoo_env, signers=[("Customer", 10), ("Branch Manager", 20)])
    envelope.action_send()
    first, second = envelope.signer_ids.sorted("sequence")

    first.action_sign()  # superuser session: a provider-callback signature
    assert envelope.state == "partially_signed"
    assert first.signature_provider == "internal" and first.auth_method == "provider-callback"
    with _rejects(odoo_env, UserError, match="Every signer must sign"):
        envelope.action_check_complete()
    assert envelope.state == "partially_signed" and not envelope.completed_at

    second.action_sign()
    # all signed, but completion is its own explicit, hash-checked step
    assert envelope.state == "partially_signed"
    envelope.action_check_complete()
    assert envelope.state == "completed" and envelope.completed_at

    certificate = envelope.completion_certificate_id
    assert certificate.document_type == "signature_certificate"
    evidence = json.loads(base64.b64decode(certificate.attachment_id.datas))
    assert evidence["evidence_hash"] == envelope.evidence_hash
    assert [s["signer"] for s in evidence["signers"]] == ["Customer", "Branch Manager"]

    events = _events(odoo_env, "envelope.completed", envelope)
    assert json.loads(events.payload) == {
        "evidence_hash": envelope.evidence_hash,
        "certificate": certificate.name,
    }


def test_completion_refuses_a_swapped_file(odoo_env):
    envelope = _envelope(odoo_env, signers=[("Customer", 10)], raw=b"original terms")
    envelope.action_send()
    sealed = envelope.evidence_hash
    envelope.signer_ids.action_sign()
    # the only signer signed — completion stays its own explicit step
    assert envelope.state == "sent"

    # even the superuser may swap the file — completion still catches it
    envelope.document_id.attachment_id.write({"datas": base64.b64encode(b"tampered terms")})
    with _rejects(odoo_env, UserError, match="sealed evidence no longer matches"):
        envelope.action_check_complete()
    assert envelope.state == "sent"

    envelope.document_id.attachment_id.write({"datas": base64.b64encode(b"original terms")})
    envelope.action_check_complete()
    assert envelope.state == "completed" and envelope.evidence_hash == sealed


def test_signers_join_and_leave_only_in_draft(odoo_env):
    envelope = _envelope(odoo_env, signers=[("Customer", 10)])
    envelope.action_send()
    # su is trusted code — the draft-only rule is attacked as a plain user
    clerk = (
        odoo_env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A10 D1 clerk",
                "login": "a10d1.clerk@behaviour.test",
                "group_ids": [(6, 0, [odoo_env.ref("base.group_user").id])],
            }
        )
    )
    late = odoo_env["res.partner"].create({"name": "Late"})
    with _rejects(odoo_env, UserError, match="while it is a DRAFT"):
        odoo_env["fix.esignature.signer"].with_user(clerk).create(
            {"envelope_id": envelope.id, "partner_id": late.id, "sequence": 20}
        )
    with _rejects(odoo_env, UserError, match="removed only while the envelope is a DRAFT"):
        envelope.signer_ids.with_user(clerk).unlink()
    assert len(envelope.signer_ids) == 1


def test_decline_and_void_unseal_the_document(odoo_env):
    envelope = _envelope(odoo_env, signers=[("Customer", 10)])
    envelope.action_send()
    with _rejects(odoo_env, UserError, match="State the reason"):
        envelope.signer_ids.action_decline("   ")
    envelope.signer_ids.action_decline("Terms changed")
    assert (envelope.state, envelope.decline_reason) == ("declined", "Terms changed")
    assert not envelope.document_id.signature_locked

    second = _envelope(odoo_env, signers=[("Customer", 10)])
    second.action_send()
    with _rejects(odoo_env, UserError, match="State why the envelope is voided"):
        second.action_void("")
    second.action_void("Wrong document")
    assert (second.state, second.void_reason) == ("voided", "Wrong document")
    assert not second.document_id.signature_locked


def test_expired_windows_refuse_signatures_and_the_cron_expires_them(odoo_env):
    envelope = _envelope(odoo_env, signers=[("Customer", 10)])
    envelope.action_send()
    stale = fields.Datetime.now() - timedelta(days=4)
    odoo_env.flush_all()  # the send's writes land before the raw SQL backdate
    odoo_env.cr.execute(
        "UPDATE fix_esignature_envelope SET deadline = %s WHERE id = %s",
        [stale, envelope.id],
    )
    envelope.invalidate_recordset()

    with _rejects(odoo_env, UserError, match="signing window"):
        envelope.signer_ids.action_sign()
    with _rejects(odoo_env, UserError, match="signing window"):
        envelope.action_check_complete()
    # the refusal's expiry write rolls back with its savepoint — the cron makes it stick
    odoo_env["fix.esignature.envelope"].cron_expire_envelopes()
    envelope.invalidate_recordset()
    assert envelope.state == "expired"
    assert not envelope.document_id.signature_locked

    # and the daily cron sweeps the same state without the failed attempts
    other = _envelope(odoo_env, signers=[("Customer", 10)])
    other.action_send()
    odoo_env.flush_all()
    odoo_env.cr.execute(
        "UPDATE fix_esignature_envelope SET deadline = %s WHERE id = %s",
        [stale, other.id],
    )
    other.invalidate_recordset()
    assert odoo_env["fix.esignature.envelope"].cron_expire_envelopes() >= 1
    assert other.state == "expired" and not other.document_id.signature_locked


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
