# M24 capture audit (2026-11-13) - the captures the sub-module pages now
# offer, driven through the workspace endpoints (/p03/model/write and
# /p03/model/action) as a NON-ADMIN user: the superuser is trusted by the
# model guards and would hide a gap.
#
#   * Document Template: a bilingual template saves with its Bengali name and
#     is refused without it - the old form showed no Bengali name, so no
#     template could ever be saved from the workspace.
#   * Signature Envelope: the signers travel with the envelope in the same
#     write, and only then can it be sent; with no signer Send is refused.
#   * Controlled Document: starts as a draft controlled document.
#   * Place Legal Hold: Records Officer only; the hold writes the register
#     row. Disposal (pass 2, 19 Nov) is refused outside an approved batch,
#     and a held document is excluded from the batch.
import base64
import itertools
from unittest import mock

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api

_SEQ = itertools.count(1)
FILE = base64.b64encode(b"M24 capture audit evidence bytes").decode()


class FakeRequest:
    def __init__(self, env):
        self.env = env


@pytest.fixture
def call():
    patchers = []

    def _call(env, route, **kw):
        p = mock.patch.object(api, "request", FakeRequest(env))
        p.start()
        patchers.append(p)
        return getattr(api.P03GenericApiController(), route)(**kw)

    yield _call
    for p in patchers:
        p.stop()


@pytest.fixture
def ou(odoo_env):
    return odoo_env["operating.unit"].search([], limit=1)


def _user(env, ou, *xmlids):
    n = next(_SEQ)
    groups = [env.ref("base.group_user").id] + [env.ref(x).id for x in xmlids]
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "M24 Capture User %d" % n,
                "login": "m24.capture.%d@a10.test" % n,
                "group_ids": [(6, 0, groups)],
                "operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )
    return env(user=user.id)


@pytest.fixture
def clerk(odoo_env, ou):
    return _user(odoo_env, ou)


@pytest.fixture
def records_officer(odoo_env, ou):
    return _user(odoo_env, ou, "cd_document_core.group_document_records")


def _upload(call, env, ou, **extra):
    values = {
        "upload_file": FILE,
        "upload_filename": "m24-capture.pdf",
        "name": "M24 Capture %d" % next(_SEQ),
        "document_type": "contract",
    }
    values.update(extra)
    res = call(env, "model_write", model="fix.document", values=values)
    assert "id" in res, res
    doc = env["fix.document"].browse(res["id"])
    if ou and not doc.operating_unit_id:
        doc.sudo()._guarded().write({"operating_unit_id": ou.id})
    return doc


def test_template_saves_with_its_bengali_name(call, clerk):
    code = "M24CAP%d" % next(_SEQ)
    refused = call(
        clerk,
        "model_write",
        model="fix.document.template",
        values={"code": code, "name": "Capture Notice", "document_type": "notice"},
    )
    assert "error" in refused and "Bengali" in refused["error"], refused
    ok = call(
        clerk,
        "model_write",
        model="fix.document.template",
        values={
            "code": code,
            "name": "Capture Notice",
            "name_bn": "ক্যাপচার নোটিশ",
            "document_type": "notice",
            "bilingual": True,
            "requires_approval": True,
        },
    )
    assert "id" in ok, ok
    tpl = clerk["fix.document.template"].browse(ok["id"])
    assert tpl.name_bn == "ক্যাপচার নোটিশ" and tpl.requires_approval


def test_envelope_carries_its_signers_and_can_be_sent(call, clerk, ou):
    doc = _upload(call, clerk, ou)
    signer = clerk["res.partner"].sudo().create({"name": "M24 Capture Signer"})
    # no signer: the envelope saves but cannot be sent (the old form's only outcome)
    bare = call(
        clerk,
        "model_write",
        model="fix.esignature.envelope",
        values={"name": "Bare envelope", "document_id": doc.id, "operating_unit_id": ou.id},
    )
    assert "id" in bare, bare
    sent = call(
        clerk,
        "model_action",
        model="fix.esignature.envelope",
        ids=[bare["id"]],
        method="action_send",
    )
    assert not sent.get("success") and "signer" in (sent.get("error") or ""), sent

    res = call(
        clerk,
        "model_write",
        model="fix.esignature.envelope",
        values={"name": "Capture envelope", "document_id": doc.id, "operating_unit_id": ou.id},
        lines={
            "field": "signer_ids",
            "rows": [
                {"values": {"sequence": 10, "partner_id": signer.id, "role_label": "Customer"}},
            ],
        },
    )
    assert "id" in res, res
    env_rec = clerk["fix.esignature.envelope"].browse(res["id"])
    assert env_rec.signer_ids.partner_id == signer
    out = call(
        clerk,
        "model_action",
        model="fix.esignature.envelope",
        ids=[env_rec.id],
        method="action_send",
    )
    assert out.get("success"), out
    env_rec.invalidate_recordset()
    assert env_rec.state == "sent" and env_rec.evidence_hash and env_rec.deadline


def test_signature_stamps_cannot_be_typed_on_the_grid(call, clerk, ou):
    doc = _upload(call, clerk, ou)
    signer = clerk["res.partner"].sudo().create({"name": "M24 Forger"})
    res = call(
        clerk,
        "model_write",
        model="fix.esignature.envelope",
        values={"name": "Forged", "document_id": doc.id, "operating_unit_id": ou.id},
        lines={
            "field": "signer_ids",
            "rows": [
                {"values": {"partner_id": signer.id, "signed_at": "2026-11-13 10:00:00"}},
            ],
        },
    )
    created = res.get("id") and clerk["fix.esignature.envelope"].browse(res["id"])
    assert "error" in res or not created.signer_ids.signed_at, res


def test_controlled_document_starts_as_a_draft(call, clerk, ou):
    doc = _upload(call, clerk, ou, is_controlled=True)
    assert doc.is_controlled and doc.control_state == "draft" and doc.version == "1.0"


def test_only_a_records_officer_places_a_hold(call, clerk, records_officer, ou):
    doc = _upload(call, clerk, ou)
    refused = call(
        clerk,
        "model_action",
        model="fix.document",
        ids=[doc.id],
        method="action_legal_hold",
        kwargs={"matter_ref": "CASE-1"},
    )
    assert not refused.get("success"), refused
    ok = call(
        records_officer,
        "model_action",
        model="fix.document",
        ids=[doc.id],
        method="action_legal_hold",
        kwargs={"matter_ref": "BD-HC-2026/114"},
    )
    assert ok.get("success"), ok
    doc.invalidate_recordset()
    assert doc.legal_hold and doc.legal_hold_reason == "BD-HC-2026/114"
    hold = records_officer["fix.legal.hold"].search([("document_id", "=", doc.id)])
    assert hold.state == "held" and hold.placed_by_id == records_officer.user


def test_a_lone_disposal_is_refused_even_to_a_records_officer(call, clerk, records_officer, ou):
    """Pass 2 (19 Nov): disposal is an approved batch (FR-DMS-038, SOD-23);
    the 13 Nov direct disposal by one Records Officer is refused. The batch
    path is proven in cd_document_core/tests/test_m24_capture_pass2.py."""
    doc = _upload(call, clerk, ou)
    # what the daily retention sweep does when the class elapses
    doc.sudo()._guarded().write({"state": "expired"})
    for who in (clerk, records_officer):
        out = call(
            who,
            "model_action",
            model="fix.document",
            ids=[doc.id],
            method="action_dispose",
            kwargs={"method": "secure_wipe"},
        )
        assert not out.get("success") and "Disposal Batch" in (out.get("error") or ""), out
    doc.invalidate_recordset()
    assert doc.sudo().state == "expired"


def test_a_held_document_cannot_be_disposed(call, clerk, records_officer, ou):
    doc = _upload(call, clerk, ou)
    doc.sudo()._guarded().write({"state": "expired"})
    assert call(
        records_officer,
        "model_action",
        model="fix.document",
        ids=[doc.id],
        method="action_legal_hold",
        kwargs={"matter_ref": "AUDIT-7"},
    ).get("success")
    # the batch for its class leaves it out and lists it as held
    rc = (
        records_officer["fix.retention.class"]
        .sudo()
        .create({"code": "M24H%d" % next(_SEQ), "name": "Held test class", "retention_years": 1})
    )
    doc.sudo()._guarded().write({"retention_class_id": rc.id})
    doc.sudo().invalidate_recordset()
    res = call(
        records_officer,
        "model_write",
        model="fix.disposal.batch",
        values={"retention_class_id": rc.id, "cutoff_on": "2099-12-31", "method": "secure_wipe"},
    )
    assert "id" in res, res
    batch = records_officer["fix.disposal.batch"].browse(res["id"])
    assert doc not in batch.document_ids and doc in batch.excluded_held_ids
