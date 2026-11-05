# A10 remediation (2026-11-05), D1: a real e-signature — the signature is
# the signer's own act, in sequence, over sealed file bytes.
#
# Every control is exercised as NON-ADMIN users (the superuser is trusted by
# the field guard and would hide a gap). Each control is attacked three ways
# where it applies: the wrong login, a plain write() (the JSON-RPC path) and
# the real P03 endpoints (/p03/model/write, /p03/model/action). The
# legitimate signing journey runs end to end. The odoo_env fixture rolls back.
import base64
import itertools
import json
import types
from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as g
from odoo.exceptions import UserError

RECORDS = "cd_document_core.group_document_records"
GUARD = "changes only through its workflow"

_MW = getattr(g.P03GenericApiController.model_write, "original_endpoint", None) or (
    g.P03GenericApiController.model_write
)
_MA = getattr(g.P03GenericApiController.model_action, "original_endpoint", None) or (
    g.P03GenericApiController.model_action
)

_SEQ = itertools.count(1)


def _user(env, login, groups=()):
    n = next(_SEQ)
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A10 D1 %s %d" % (login, n),
                "login": "a10d1.%s.%d@a10.test" % (login, n),
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(x).id for x in groups])
                ],
            }
        )
    )
    assert not user.has_group("base.group_system")
    return user


@pytest.fixture
def w(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.clerk = _user(env, "clerk")  # the sender
    x.sig1 = _user(env, "signer1")
    x.sig2 = _user(env, "signer2")
    x.records = _user(env, "records", [RECORDS])
    x.ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    saved = getattr(g, "request", None)
    yield x
    g.request = saved


def p03(x, endpoint, user=None, **kw):
    g.request = types.SimpleNamespace(env=x.env(user=(user or x.clerk).id))
    return endpoint(g.P03GenericApiController(), **kw)


def _doc(x, raw=b"contract terms", **vals):
    attachment = x.env["ir.attachment"].create(
        {"name": "file", "datas": base64.b64encode(raw)}
    )
    return x.env["fix.document"].create(
        {"name": vals.pop("name", "Contract %d" % next(_SEQ)),
         "attachment_id": attachment.id, **vals}
    )


def _envelope(x, doc, signers, user=None, name="Signing"):
    """An envelope created by the sender over `doc` with (user, seq) signers."""
    return (
        x.env["fix.esignature.envelope"]
        .with_user(user or x.clerk)
        .create(
            {
                "name": name,
                "document_id": doc.id,
                "operating_unit_id": x.ou.id,
                "signer_ids": [
                    (0, 0, {"partner_id": (u.partner_id).id, "sequence": seq})
                    for u, seq in signers
                ],
            }
        )
    )


def _events(x, event_type, envelope):
    rows = x.env["fix.event.outbox"].search(
        [
            ("event_type", "=", event_type),
            ("aggregate_id", "=", envelope.id),
        ]
    )
    return [json.loads(r.payload) for r in rows]


# ------------------------------------------------- the signature is an act
def test_nobody_signs_for_somebody_else(w):
    env = _envelope(w, _doc(w), [(w.sig1, 10), (w.sig2, 20)])
    env.with_user(w.clerk).action_send()
    first, _second = env.signer_ids.sorted("sequence")

    with pytest.raises(UserError, match="signs for themself"):
        first.with_user(w.clerk).action_sign()
    with pytest.raises(UserError, match="signs for themself"):
        first.with_user(w.sig2).action_sign()
    assert not first.signed_at and env.state == "sent"

    # the evidence fields are stamped by the server, never typed
    for vals in (
        {"signed_at": fields.Datetime.now()},
        {"signature_provider": "typed-provider"},
        {"auth_method": "typed-auth"},
    ):
        with pytest.raises(UserError, match=GUARD):
            first.with_user(w.sig1).write(vals)
    out = p03(w, _MW, user=w.sig1, model="fix.esignature.signer", record_id=first.id,
              values={"signed_at": fields.Datetime.now().isoformat()})
    assert "error" in out and GUARD in out["error"]


def test_signing_is_sequential_within_the_window(w):
    env = _envelope(w, _doc(w), [(w.sig1, 10), (w.sig2, 20)])
    env.with_user(w.clerk).action_send()
    first, second = env.signer_ids.sorted("sequence")

    with pytest.raises(UserError, match="signing order is sequential"):
        second.with_user(w.sig2).action_sign()

    first.with_user(w.sig1).action_sign()
    assert first.signed_at and first.signature_provider == "internal"
    assert first.auth_method == "session"  # their own logged-in session
    assert env.state == "partially_signed"
    with pytest.raises(UserError, match="already signed"):
        first.with_user(w.sig1).action_sign()

    second.with_user(w.sig2).action_sign("otp-verified")
    assert second.signature_provider == "otp-verified"
    # all signed, but completion stays its own explicit, hash-checked step
    assert env.state == "partially_signed"

    # the signer list is sealed with the evidence: nobody joins or leaves
    with pytest.raises(UserError, match="while it is a DRAFT"):
        w.env["fix.esignature.signer"].with_user(w.clerk).create(
            {"envelope_id": env.id, "partner_id": w.clerk.partner_id.id, "sequence": 30}
        )
    with pytest.raises(UserError, match="only while the envelope is a DRAFT"):
        env.signer_ids.with_user(w.clerk).unlink()


def test_completion_is_checked_by_the_sender_over_the_same_bytes(w):
    doc = _doc(w)
    env = _envelope(w, doc, [(w.sig1, 10), (w.sig2, 20)])
    env.with_user(w.clerk).action_send()
    sealed = env.evidence_hash
    first, second = env.signer_ids.sorted("sequence")

    with pytest.raises(UserError, match="Completion is checked on a SENT envelope"):
        _envelope(w, doc, [(w.sig1, 10)]).with_user(w.clerk).action_check_complete()
    with pytest.raises(UserError, match="Every signer must sign"):
        env.with_user(w.clerk).action_check_complete()

    first.with_user(w.sig1).action_sign()
    second.with_user(w.sig2).action_sign()
    # the audit's file swap: a plain user writing the attachment directly
    with pytest.raises(UserError, match="e-signature seal"):
        doc.attachment_id.with_user(w.clerk).write(
            {"datas": base64.b64encode(b"Pay BDT 500,000 instead")}
        )
    assert w.env["fix.document"].search_count(
        [("attachment_id", "=", doc.attachment_id.id), ("signature_locked", "=", True)]
    )

    env.with_user(w.clerk).action_check_complete()
    assert env.state == "completed" and env.completed_at and env.evidence_hash == sealed
    certificate = env.completion_certificate_id
    assert certificate.document_type == "signature_certificate"
    assert certificate.res_model == "fix.esignature.envelope" and certificate.res_id == env.id
    evidence = json.loads(base64.b64decode(certificate.attachment_id.datas))
    assert evidence["evidence_hash"] == sealed
    assert [s["auth_method"] for s in evidence["signers"]] == ["session", "session"]
    assert _events(w, "envelope.completed", env) == [
        {"evidence_hash": sealed, "certificate": certificate.name}
    ]

    # a completed envelope is frozen
    with pytest.raises(UserError, match=GUARD):
        env.with_user(w.clerk).write({"state": "sent"})
    with pytest.raises(UserError, match=GUARD):
        env.with_user(w.clerk).write({"name": "renamed after send"})


def test_envelope_lifecycle_fields_are_never_typed(w):
    doc = _doc(w)
    with pytest.raises(UserError, match=GUARD):
        w.env["fix.esignature.envelope"].with_user(w.clerk).create(
            {
                "name": "Born completed",
                "document_id": doc.id,
                "operating_unit_id": w.ou.id,
                "state": "completed",
            }
        )
    env = _envelope(w, doc, [(w.sig1, 10)])
    out = p03(w, _MW, user=w.clerk, model="fix.esignature.envelope", record_id=env.id,
              values={"state": "completed"})
    assert "error" in out and GUARD in out["error"]
    # sending works through the endpoint, and seals the document
    out = p03(w, _MA, user=w.clerk, model="fix.esignature.envelope", ids=env.ids,
              method="action_send")
    assert out.get("success") is True and env.state == "sent"
    assert env.document_id.signature_locked
    out = p03(w, _MA, user=w.sig1, model="fix.esignature.signer", ids=env.signer_ids.ids,
              method="action_sign", kwargs={"provider": "p03-session"})
    assert out.get("success") is True
    env.invalidate_recordset()
    assert [s.signature_provider for s in env.signer_ids] == ["p03-session"]


def test_documents_that_may_not_be_signed_are_refused_at_send(w):
    held = _doc(w, name="Held contract")
    held.with_user(w.records).action_legal_hold("Court order 12/2026")

    superseded = _doc(w, name="Superseded SOP")
    superseded.sudo().write({"is_current": False})
    controlled = _doc(w, name="Controlled SOP", is_controlled=True)
    bare = _doc(w, name="No file")
    bare.attachment_id.sudo().write({"datas": False})

    for doc, refused in (
        (held, "legal hold"),
        (superseded, "superseded version"),
        (controlled, "controlled document in state 'draft'"),
        (bare, "no file to sign"),
    ):
        env = _envelope(w, doc, [(w.sig1, 10)])
        with pytest.raises(UserError, match=refused):
            env.with_user(w.clerk).action_send()
        assert env.state == "draft" and not env.document_id.signature_locked


def test_decline_and_void_unseal_and_record_their_reasons(w):
    doc = _doc(w)
    env = _envelope(w, doc, [(w.sig1, 10)])
    env.with_user(w.clerk).action_send()
    assert doc.signature_locked

    (signer,) = env.signer_ids
    with pytest.raises(UserError, match=r"Only .* declines their own signature"):
        signer.with_user(w.sig2).action_decline("no")
    with pytest.raises(UserError, match="State the reason"):
        signer.with_user(w.sig1).action_decline(" ")
    signer.with_user(w.sig1).action_decline("Terms changed overnight")
    assert (env.state, env.decline_reason) == ("declined", "Terms changed overnight")
    assert not doc.signature_locked

    second = _envelope(w, doc, [(w.sig1, 10)])
    second.with_user(w.clerk).action_send()
    with pytest.raises(UserError, match="State why the envelope is voided"):
        second.with_user(w.clerk).action_void("")
    second.with_user(w.clerk).action_void("Wrong attachment")
    assert (second.state, second.void_reason) == ("voided", "Wrong attachment")
    assert not doc.signature_locked

    with pytest.raises(UserError, match="Only a draft or in-flight envelope"):
        second.with_user(w.clerk).action_void("once more")


def test_the_signing_window_closes(w):
    env = _envelope(w, _doc(w), [(w.sig1, 10)])
    env.with_user(w.clerk).action_send()
    assert env.deadline == fields.Datetime.add(env.sent_at, days=3)

    stale = fields.Datetime.now() - timedelta(hours=1)
    w.env.flush_all()  # the send's writes land before the raw SQL backdate
    w.env.cr.execute(
        "UPDATE fix_esignature_envelope SET deadline = %s WHERE id = %s",
        [stale, env.id],
    )
    env.invalidate_recordset()

    with pytest.raises(UserError, match="signing window"):
        env.signer_ids.with_user(w.sig1).action_sign()
    assert w.env["fix.esignature.envelope"].cron_expire_envelopes() >= 1
    env.invalidate_recordset()
    assert env.state == "expired" and not env.document_id.signature_locked


def test_the_sealed_evidence_is_never_typed(w):
    env = _envelope(w, _doc(w), [(w.sig1, 10)])
    env.with_user(w.clerk).action_send()
    with pytest.raises(UserError, match=GUARD):
        env.with_user(w.clerk).write({"evidence_hash": "0" * 64})
    with pytest.raises(UserError, match=GUARD):
        env.with_user(w.clerk).write({"completion_certificate_id": 1})
    # re-pointing a signer at another envelope would move sealed evidence
    other = _envelope(w, _doc(w, raw=b"another contract"), [(w.sig1, 10)])
    with pytest.raises(UserError, match=GUARD):
        env.signer_ids.with_user(w.sig1).write({"envelope_id": other.id})
