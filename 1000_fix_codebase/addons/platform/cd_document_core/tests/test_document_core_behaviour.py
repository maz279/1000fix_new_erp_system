# Behavioural tests for the M24-core document kernel on the live ORM
# (`odoo_env`, rolled back after every test).
import base64
import contextlib
import hashlib
import json
from datetime import date, timedelta
from unittest import mock

import pytest
from odoo.exceptions import UserError, ValidationError


@contextlib.contextmanager
def _rejects(env, exc, match):
    """pytest.raises inside a savepoint: an expected failure never leaves a
    half-applied write in the shared test transaction."""
    with pytest.raises(exc, match=match) as info, env.cr.savepoint():
        yield info


def _retention(env, years=7, code="TST-7Y"):
    return env["fix.retention.class"].create(
        {"code": code, "name": f"Test {years}y", "retention_years": years}
    )


def _attach(env, raw=b"service report bytes", **kw):
    return env["fix.document"].attach(
        name=kw.pop("name", "Report.pdf"),
        datas=base64.b64encode(raw),
        document_type=kw.pop("document_type", "service_report"),
        **kw,
    )


def _events(env, event_type, doc):
    return env["fix.event.outbox"].search(
        [
            ("event_type", "=", event_type),
            ("aggregate", "=", "fix.document"),
            ("aggregate_id", "=", doc.id),
        ]
    )


# --- attachment API + events --------------------------------------------------


def test_attach_creates_attachment_and_governed_document(odoo_env):
    retention = _retention(odoo_env)
    doc = _attach(
        odoo_env,
        res_model="res.partner",
        res_id=3,
        retention_class_id=retention.id,
        isolation_tier="T2",
    )
    assert doc.attachment_id.res_model == "fix.document"
    assert base64.b64decode(doc.attachment_id.datas) == b"service report bytes"
    assert (doc.res_model, doc.res_id, doc.isolation_tier) == ("res.partner", 3, "T2")
    assert doc.state == "active" and doc.mayan_sync_status == "not_synced"

    events = _events(odoo_env, "document.attached", doc)
    assert len(events) == 1
    assert json.loads(events.payload) == {
        "name": "Report.pdf",
        "document_type": "service_report",
        "is_residency_classified": False,
    }


def test_retention_change_emits_retention_applied_only_when_class_written(odoo_env):
    doc = _attach(odoo_env)
    doc.write({"description": "no retention change"})
    assert not _events(odoo_env, "document.retention_applied", doc)
    doc.write({"retention_class_id": _retention(odoo_env).id})
    assert len(_events(odoo_env, "document.retention_applied", doc)) == 1


# --- retention clock ------------------------------------------------------------


def test_retention_expiry_counts_years_from_creation(odoo_env):
    doc = _attach(odoo_env, retention_class_id=_retention(odoo_env, years=5).id)
    assert doc.retention_expires == doc.create_date.date() + timedelta(days=365 * 5)


def test_retention_expiry_of_an_unsaved_document_counts_from_today(odoo_env):
    retention = _retention(odoo_env, years=2)
    draft = odoo_env["fix.document"].new({"name": "Draft", "retention_class_id": retention.id})
    assert draft.retention_expires == date.today() + timedelta(days=365 * 2)


def test_no_retention_class_or_zero_years_never_expires(odoo_env):
    assert not _attach(odoo_env).retention_expires
    zero = _attach(odoo_env, retention_class_id=_retention(odoo_env, years=0, code="ZERO").id)
    assert not zero.retention_expires


def test_legal_hold_freezes_and_release_restores_the_clock(odoo_env):
    doc = _attach(odoo_env, retention_class_id=_retention(odoo_env, years=3).id)
    expiry = doc.retention_expires
    assert expiry

    doc.action_legal_hold("Court order 12/2026")
    assert doc.legal_hold and doc.legal_hold_reason == "Court order 12/2026"
    assert not doc.retention_expires

    doc.action_release_hold()
    assert not doc.legal_hold and not doc.legal_hold_reason
    assert doc.retention_expires == expiry


def test_legal_hold_without_reason_records_the_default(odoo_env):
    doc = _attach(odoo_env)
    doc.action_legal_hold()
    assert doc.legal_hold_reason == "Active Legal Inquiry"


def test_release_of_a_document_not_on_hold_is_a_no_op(odoo_env):
    held, free = _attach(odoo_env, name="held"), _attach(odoo_env, name="free")
    held.action_legal_hold("probe")
    with mock.patch.object(type(free), "write", autospec=True, wraps=type(free).write) as spy:
        (held | free).action_release_hold()
    written = [call.args[0] for call in spy.call_args_list]
    assert written == [held]
    assert not held.legal_hold


# --- Mayan EDMS sync ------------------------------------------------------------


def test_sync_to_mayan_hashes_the_decoded_attachment_bytes(odoo_env):
    raw = b"%PDF-1.7 evidence pack"
    doc = _attach(odoo_env, raw=raw)
    assert doc.action_sync_to_mayan() is True
    assert doc.checksum_sha256 == hashlib.sha256(raw).hexdigest()
    assert doc.payload_size_bytes == len(raw)
    assert doc.mayan_document_id == f"MAYAN-DOC-{doc.id:06d}"
    assert doc.mayan_sync_status == "synced"
    assert len(_events(odoo_env, "document.mayan_synced", doc)) == 1


def test_sync_to_mayan_falls_back_to_raw_datas_when_not_base64(odoo_env):
    doc = _attach(odoo_env, raw=b"abc")
    stored = doc.attachment_id.datas
    with mock.patch("base64.b64decode", side_effect=ValueError("bad padding")):
        doc.action_sync_to_mayan()
    expected = str(stored).encode("utf-8")
    assert doc.checksum_sha256 == hashlib.sha256(expected).hexdigest()
    assert doc.payload_size_bytes == len(expected)


@pytest.mark.parametrize(
    ("description", "expected"), [("signed custody note", b"signed custody note"), (False, b"Bare")]
)
def test_sync_to_mayan_without_file_hashes_description_or_name(odoo_env, description, expected):
    empty_file = odoo_env["ir.attachment"].create({"name": "empty"})
    doc = odoo_env["fix.document"].create(
        {"name": "Bare", "attachment_id": empty_file.id, "description": description}
    )
    doc.action_sync_to_mayan()
    assert doc.checksum_sha256 == hashlib.sha256(expected).hexdigest()
    assert doc.payload_size_bytes == len(expected)


def test_batch_migration_syncs_unsynced_documents_with_control_totals(odoo_env):
    Doc = odoo_env["fix.document"]
    mine = _attach(odoo_env, name="a") | _attach(odoo_env, name="b")
    pending_before = Doc.search_count([("mayan_sync_status", "!=", "synced")])

    result = Doc.migrate_documents_to_mayan(limit=pending_before)

    assert result["batch_processed"] == pending_before
    assert all(d.mayan_sync_status == "synced" for d in mine)
    assert result["total_synced"] == Doc.search_count([("mayan_sync_status", "=", "synced")])
    assert result["total_records"] == Doc.search_count([])
    assert result["control_totals_match"] is True


# --- destruction guard ------------------------------------------------------------


def test_destruction_blocked_under_legal_hold_with_reason(odoo_env):
    doc = _attach(odoo_env, name="Held Contract")
    doc.write({"state": "expired"})
    doc.action_legal_hold("Tax audit 2026")
    with _rejects(odoo_env, UserError, match=r"Held Contract.*'Tax audit 2026'.*strictly blocked"):
        doc.action_assert_can_destroy()


def test_destruction_blocked_under_legal_hold_without_reason(odoo_env):
    doc = _attach(odoo_env, name="Held")
    doc.write({"legal_hold": True})
    with _rejects(odoo_env, UserError, match="'Legal Notice'"):
        doc.unlink()
    assert doc.exists()


def test_destruction_blocked_before_retention_expiry(odoo_env):
    doc = _attach(odoo_env, name="Fresh")
    with _rejects(odoo_env, UserError, match="has not reached retention expiry"):
        doc.unlink()
    assert doc.exists()


@pytest.mark.parametrize("state", ["expired", "pending_destruction"])
def test_expired_documents_may_be_destroyed(odoo_env, state):
    doc = _attach(odoo_env)
    doc.write({"state": state})
    assert doc.action_assert_can_destroy() is True
    doc_id = doc.id
    doc.unlink()
    assert not odoo_env["fix.document"].browse(doc_id).exists()


# --- fix.document.template ------------------------------------------------------


def test_bilingual_template_requires_bengali_name(odoo_env):
    Template = odoo_env["fix.document.template"]
    with _rejects(odoo_env, ValidationError, match="Bengali name"):
        Template.create({"code": "SR-01", "name": "Service Report", "document_type": "invoice"})
    ok = Template.create(
        {
            "code": "SR-02",
            "name": "Service Report",
            "name_bn": "সার্ভিস রিপোর্ট",
            "document_type": "service_report",
        }
    )
    assert ok.bilingual
    mono = Template.create(
        {"code": "SR-03", "name": "EN only", "document_type": "notice", "bilingual": False}
    )
    assert not mono.name_bn
