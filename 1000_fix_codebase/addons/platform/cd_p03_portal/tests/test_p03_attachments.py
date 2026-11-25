# Workspace record documents: list a record's attachments and upload one
# (controllers/p03_attachments.py).
#
# Found 2026-11-13 (M06 audit): the service-order record view's "Upload
# Attachment" button only showed "Select image or PDF to upload...", its
# empty-state line could never render (it sat inside the block shown only
# when there ARE attachments), and the in-workspace forms had no document
# panel - signed receipts and consents could be attached only in the Odoo
# back office.
from __future__ import annotations

import base64
from pathlib import Path
from unittest import mock

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_attachments as pa
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.exceptions import AccessError

SRC = Path(__file__).resolve().parents[1] / "static" / "src"
PDF = b"%PDF-1.4\n% signed delivery receipt\n%%EOF"
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32


class FakeRequest:
    def __init__(self, env):
        self.env = env


def _b64(raw):
    return base64.b64encode(raw).decode()


@pytest.fixture
def ws(odoo_env):
    env = odoo_env
    Users = env["res.users"].with_context(no_reset_password=True)
    ref = env.ref

    def user(key, *groups):
        return Users.create(
            {
                "name": "P03 Docs %s" % key,
                "login": "p03.docs.%s@docs.test" % key,
                "group_ids": [(6, 0, [ref("base.group_user").id] + [ref(g).id for g in groups])],
            }
        )

    clerk = user("clerk")
    customer = env["res.partner"].create({"name": "P03 Docs Customer", "is_company": True})
    plan = env["fix.data.backup.plan"].create({"name": "Docs NAS plan", "customer_id": customer.id})
    ctrl = pa.P03AttachmentsController()

    def call(who, route, **kw):
        with mock.patch.object(pa, "request", FakeRequest(env(user=who.id))):
            return getattr(ctrl, route)(**kw)

    return env, clerk, plan, call, user, customer


def _read_only_record(env, who):
    """Any served record this user may read but not change."""
    for model in sorted(api.SURFACES):
        if model not in env or env[model]._abstract or env[model]._transient:
            continue
        Model = env[model].with_user(who)
        if Model.has_access("read") and not Model.has_access("write"):
            rec = env[model].search([], limit=1)
            if rec and rec.with_user(who).has_access("read"):
                return rec
    pytest.skip("no served record is read-only for a basic internal user here")


def test_a_writer_uploads_and_the_list_shows_it(ws):
    env, clerk, plan, call, *_ = ws
    out = call(
        clerk,
        "model_attachment_upload",
        model=plan._name,
        record_id=plan.id,
        name="C:\\scans\\restore-test.pdf",
        data=_b64(PDF),
    )
    assert out["success"], out
    att = env["ir.attachment"].browse(out["id"])
    assert (att.res_model, att.res_id, att.name) == (plan._name, plan.id, "restore-test.pdf")
    assert att.raw == PDF and att.mimetype == "application/pdf"
    assert att.create_uid == clerk  # created as the user, not sudo
    assert "restore-test.pdf" in plan.message_ids[:1].body

    listed = call(clerk, "model_attachments", model=plan._name, record_id=plan.id)
    assert listed["can_upload"] and not listed["names_hidden"]
    row = listed["rows"][0]
    assert row["name"] == "restore-test.pdf" and row["type"] == "PDF"
    assert row["url"] == "/web/content/%d?download=true" % att.id
    # shown in Dhaka time (UTC+6), not the stored UTC
    clerk.tz = False
    local = call(clerk, "model_attachments", model=plan._name, record_id=plan.id)["rows"][0]
    utc = att.create_date.strftime("%Y-%m-%d %H:%M")
    assert local["date"] != utc and local["date"] > utc


@pytest.mark.parametrize(
    "name, raw, why",
    [
        ("tool.exe", b"MZ\x90\x00", "PDF, JPG, PNG or DOCX"),
        ("receipt.pdf", PNG, "not a real PDF"),
        ("photo.jpg", PDF, "not a real JPG"),
        ("receipt.pdf", b"", "Choose a file"),
        ("noext", PDF, "PDF, JPG, PNG or DOCX"),
    ],
)
def test_only_real_documents_are_accepted(ws, name, raw, why):
    env, clerk, plan, call, *_ = ws
    out = call(
        clerk,
        "model_attachment_upload",
        model=plan._name,
        record_id=plan.id,
        name=name,
        data=_b64(raw) if raw else "",
    )
    assert not out["success"] and why in out["error"], out
    assert not env["ir.attachment"].search(
        [("res_model", "=", plan._name), ("res_id", "=", plan.id)]
    )


def test_a_file_over_10_mb_is_refused(ws):
    env, clerk, plan, call, *_ = ws
    big = b"%PDF" + b"\x00" * pa.MAX_BYTES
    out = call(
        clerk,
        "model_attachment_upload",
        model=plan._name,
        record_id=plan.id,
        name="big.pdf",
        data=_b64(big),
    )
    assert not out["success"] and "10 MB" in out["error"]


def test_a_reader_lists_but_cannot_upload(ws):
    env, clerk, _plan, call, *_ = ws
    rec = _read_only_record(env, clerk)
    listed = call(clerk, "model_attachments", model=rec._name, record_id=rec.id)
    assert "error" not in listed and listed["can_upload"] is False
    before = env["ir.attachment"].search_count(
        [("res_model", "=", rec._name), ("res_id", "=", rec.id)]
    )
    out = call(
        clerk,
        "model_attachment_upload",
        model=rec._name,
        record_id=rec.id,
        name="x.pdf",
        data=_b64(PDF),
    )
    assert not out["success"], out
    after = env["ir.attachment"].search_count(
        [("res_model", "=", rec._name), ("res_id", "=", rec.id)]
    )
    assert after == before


def test_unserved_models_and_unknown_records_are_refused(ws):
    env, clerk, plan, call, *_ = ws
    lang = env.ref("base.lang_en")
    assert lang._name not in api.SURFACES
    out = call(
        clerk,
        "model_attachment_upload",
        model=lang._name,
        record_id=lang.id,
        name="x.pdf",
        data=_b64(PDF),
    )
    assert not out["success"] and "not available" in out["error"]
    out = call(clerk, "model_attachments", model=plan._name, record_id=10**9)
    assert out["rows"] == [] and "not found" in out["error"]


def test_no_access_to_the_record_means_no_documents(ws):
    """A recovery case is for the data-recovery role: a basic user can
    neither list nor add its documents."""
    env, clerk, _plan, call, user, customer = ws
    tech = user("tech", "cd_data_case.group_data_recovery_operator")
    case = (
        env["fix.data.recovery.case"]
        .with_user(tech)
        .create({"customer_id": customer.id, "media_type": "hdd"})
    )
    listed = call(clerk, "model_attachments", model=case._name, record_id=case.id)
    assert listed["rows"] == [] and listed.get("error")
    out = call(
        clerk,
        "model_attachment_upload",
        model=case._name,
        record_id=case.id,
        name="nda.pdf",
        data=_b64(PDF),
    )
    assert not out["success"]
    with pytest.raises(AccessError):
        pa.upload_attachment(env(user=clerk.id), case._name, case.id, "nda.pdf", _b64(PDF))


def test_recovery_case_documents_are_listed_without_names(ws):
    env, _clerk, _plan, call, user, customer = ws
    tech = user("tech2", "cd_data_case.group_data_recovery_operator")
    case = (
        env["fix.data.recovery.case"]
        .with_user(tech)
        .create({"customer_id": customer.id, "media_type": "ssd"})
    )
    out = call(
        tech,
        "model_attachment_upload",
        model=case._name,
        record_id=case.id,
        name="Rahim-NDA-signed.pdf",
        data=_b64(PDF),
    )
    assert out["success"], out
    listed = call(tech, "model_attachments", model=case._name, record_id=case.id)
    assert listed["names_hidden"] and listed["can_upload"]
    row = listed["rows"][0]
    assert row["name"] == "Document 1" and row["url"] is False
    assert "Rahim" not in (case.message_ids[:1].body or "")


def test_no_message_calls_an_undefined_t():
    """`t` is a method of the workspace component, not a module function: 37
    `showToast(t('...'))` calls threw ReferenceError, so a failed order load or
    a validation message ("Please select an active order") became Odoo's
    "Oops! Something went wrong" (found 2026-11-13 opening an order)."""
    import re

    bare = re.compile(r"(?<![\w.$])t\((['\"`])")
    found = [
        "%s:%d" % (js.name, n)
        for js in sorted(SRC.glob("*.js"))
        for n, line in enumerate(js.read_text(encoding="utf-8").splitlines(), 1)
        if bare.search(line)
    ]
    assert not found, found


def test_the_workspace_wires_the_upload():
    xml = (SRC / "p03_workspace.xml").read_text(encoding="utf-8")
    js = (SRC / "p03_workspace.js").read_text(encoding="utf-8")
    assert "Select image or PDF to upload" not in xml
    assert "this.recordAttachmentUpload(ev)" in xml and "this.formAttachmentUpload(ev)" in xml
    assert "d365-attachments-card" in xml
    for method in (
        "formAttachmentsLoad()",
        "recordAttachmentsLoad(orderId)",
        "uploadRecordFile(model, recordId, ev, done)",
    ):
        assert method in js, method
    assert '"/p03/model/attachment/upload"' in js and '"/p03/model/attachments"' in js
