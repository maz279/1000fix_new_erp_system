# Behavioural tests for the M24 document kernel on the live ORM
# (`odoo_env`, rolled back after every test).
#
# A10 D2/P1-1 (2026-11-05): the kernel now has a records register, a
# controlled-document workflow, retention enforcement and an honest Mayan
# sync — these journeys run at superuser level (the guard opens for su);
# the non-admin three-way attacks live in test_a10_d2_p11_controls.py.
import base64
import contextlib
import hashlib
import json
from datetime import date, timedelta
from unittest import mock

import pytest
from odoo.exceptions import UserError, ValidationError

MAYAN_KEYS = ("mayan_edms.base_url", "mayan_edms.token")


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


def _mayan_off(env):
    env["ir.config_parameter"].search([("key", "in", MAYAN_KEYS)]).unlink()


def _mayan_on(env, url="http://mayan.test"):
    _mayan_off(env)
    env["ir.config_parameter"].create(
        [
            {"key": "mayan_edms.base_url", "value": url},
            {"key": "mayan_edms.token", "value": "test-token"},
        ]
    )


def _mayan_ack(remote_id=7):
    """A requests.post double that acknowledges (or not) the upload."""
    response = mock.Mock()
    response.headers = {"content-type": "application/json"}
    response.json = lambda: ({"id": remote_id} if remote_id else {"detail": "denied"})
    return mock.patch("requests.post", return_value=response)


def _backdate(env, model, table, column, value, rec_id):
    # flush the ORM queue FIRST: a raw UPDATE racing pending creates/computes
    # would hit a half-written row (or none), and the flush that follows the
    # SQL would overwrite the backdate with the in-memory value
    env.flush_all()
    env.cr.execute(f"UPDATE {table} SET {column} = %s WHERE id = %s", [value, rec_id])
    env[model].browse(rec_id).invalidate_recordset()


# --- attachment API + events --------------------------------------------------


def test_attach_creates_attachment_and_governed_document(odoo_env):
    retention = _retention(odoo_env)
    raw = b"service report bytes"
    doc = _attach(
        odoo_env,
        raw=raw,
        res_model="res.partner",
        res_id=3,
        retention_class_id=retention.id,
        isolation_tier="T2",
    )
    assert doc.attachment_id.res_model == "fix.document"
    assert base64.b64decode(doc.attachment_id.datas) == raw
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


# --- integrity fingerprint (server-computed, M24-8) -----------------------------


def test_checksum_is_computed_over_the_decoded_bytes(odoo_env):
    raw = b"%PDF-1.7 evidence pack"
    doc = _attach(odoo_env, raw=raw)
    assert doc.checksum_sha256 == hashlib.sha256(raw).hexdigest()
    assert doc.payload_size_bytes == len(raw)
    # a caller-typed fingerprint never reaches the record
    other = odoo_env["fix.document"].create(
        {
            "name": "Typed checksum",
            "attachment_id": doc.attachment_id.id,
            "checksum_sha256": "0" * 64,
            "payload_size_bytes": 1,
        }
    )
    assert other.checksum_sha256 == hashlib.sha256(raw).hexdigest()
    assert other.payload_size_bytes == len(raw)


def test_same_name_different_bytes_seal_differently(odoo_env):
    # the audit probe: 'Pay 5,000' vs 'Pay 500,000' under one name
    small = _attach(odoo_env, raw=b"Pay BDT 5,000 only", name="Settlement.pdf")
    large = _attach(odoo_env, raw=b"Pay BDT 500,000 only", name="Settlement.pdf")
    assert small.checksum_sha256 != large.checksum_sha256


def test_checksum_follows_the_file_and_empty_is_false(odoo_env):
    doc = _attach(odoo_env, raw=b"before")
    doc.attachment_id.write({"datas": base64.b64encode(b"after")})
    assert doc.checksum_sha256 == hashlib.sha256(b"after").hexdigest()
    bare = odoo_env["fix.document"].create(
        {
            "name": "Bare",
            "attachment_id": odoo_env["ir.attachment"].create({"name": "empty"}).id,
        }
    )
    assert not bare.checksum_sha256 and bare.payload_size_bytes == 0


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


# --- retention enforcement cron (M24-7) -----------------------------------------


def test_retention_cron_expires_only_eligible_documents(odoo_env):
    seven_years = _retention(odoo_env)
    eligible = _attach(odoo_env, name="due", retention_class_id=seven_years.id)
    held = _attach(odoo_env, name="held", retention_class_id=seven_years.id)
    unclassified = _attach(odoo_env, name="fresh")
    yesterday = date.today() - timedelta(days=1)
    for doc in (eligible, held):
        _backdate(odoo_env, "fix.document", "fix_document", "retention_expires", yesterday, doc.id)
    held.action_legal_hold("Court order 12/2026")

    expired = odoo_env["fix.document"].cron_retention_enforcement()

    assert expired == 1
    assert eligible.state == "expired"
    assert held.state == "active"  # the hold overrides disposal
    assert unclassified.state == "active"
    payload = json.loads(_events(odoo_env, "document.retention_due", eligible).payload)
    assert payload["name"] == "due"
    assert not _events(odoo_env, "document.retention_due", held)


def test_retention_consumer_runs_from_the_relay_only(odoo_env):
    doc = _attach(odoo_env, retention_class_id=_retention(odoo_env).id)
    with _rejects(odoo_env, UserError, match="event relay only"):
        doc.with_user(odoo_env.ref("base.user_admin")).consume_document_retention_due(
            {"aggregate_id": str(doc.id)}
        )
    assert doc.consume_document_retention_due({"aggregate_id": str(doc.id)}) is True
    assert any("retention sweep" in (m.body or "") for m in doc.message_ids)


# --- legal hold ------------------------------------------------------------------


def test_legal_hold_needs_the_matter_reference(odoo_env):
    doc = _attach(odoo_env)
    with _rejects(odoo_env, UserError, match="matter reference"):
        doc.action_legal_hold("   ")
    assert not doc.legal_hold


def test_legal_hold_freezes_and_release_restores_the_clock(odoo_env):
    doc = _attach(odoo_env, retention_class_id=_retention(odoo_env, years=3).id)
    expiry = doc.retention_expires
    assert expiry

    doc.action_legal_hold("Court order 12/2026")
    assert doc.legal_hold and doc.legal_hold_reason == "Court order 12/2026"
    assert not doc.retention_expires
    (hold,) = odoo_env["fix.legal.hold"].search([("document_id", "=", doc.id)])
    assert (hold.state, hold.matter_ref, hold.placed_by_id) == (
        "held",
        "Court order 12/2026",
        odoo_env.user,
    )

    with _rejects(odoo_env, UserError, match="State why the hold is released"):
        doc.action_release_hold()
    doc.action_release_hold("Matter closed")
    assert not doc.legal_hold and not doc.legal_hold_reason
    assert doc.retention_expires == expiry
    hold.invalidate_recordset()
    assert (hold.state, hold.release_reason) == ("released", "Matter closed")


def test_release_of_a_document_not_on_hold_is_a_no_op(odoo_env):
    held, free = _attach(odoo_env, name="held"), _attach(odoo_env, name="free")
    held.action_legal_hold("probe")
    with mock.patch.object(type(free), "write", autospec=True, wraps=type(free).write) as spy:
        (held | free).action_release_hold("nothing to release for one of them")
    written = [call.args[0] for call in spy.call_args_list]
    assert written == [held]
    assert not held.legal_hold


# --- Mayan EDMS honesty (M24-8) ---------------------------------------------------


def test_sync_refuses_without_a_configured_endpoint(odoo_env):
    _mayan_off(odoo_env)
    doc = _attach(odoo_env)
    with _rejects(odoo_env, UserError, match="Mayan EDMS is not configured"):
        doc.action_sync_to_mayan()
    assert doc.mayan_sync_status == "not_synced"
    assert not doc.mayan_document_id


def test_sync_marks_synced_only_on_a_remote_acknowledgement(odoo_env):
    _mayan_on(odoo_env)
    doc = _attach(odoo_env)
    with _mayan_ack(7):
        assert doc.action_sync_to_mayan() is True
    assert doc.mayan_sync_status == "synced"
    assert doc.mayan_document_id == "7"
    assert len(_events(odoo_env, "document.mayan_synced", doc)) == 1

    denied = _attach(odoo_env, name="Denied.pdf")
    with _mayan_ack(None), _rejects(odoo_env, UserError, match="did not acknowledge"):
        denied.action_sync_to_mayan()
    assert denied.mayan_sync_status != "synced"
    assert not denied.mayan_document_id


def test_batch_migration_reports_honest_control_totals(odoo_env):
    _mayan_on(odoo_env)
    Doc = odoo_env["fix.document"]
    mine = _attach(odoo_env, name="a") | _attach(odoo_env, name="b")
    Doc.create(
        {
            "name": "no file",
            "attachment_id": odoo_env["ir.attachment"].create({"name": "empty"}).id,
        }
    )
    pending_before = Doc.search_count([("mayan_sync_status", "!=", "synced")])

    with _mayan_ack(41):
        result = Doc.migrate_documents_to_mayan(limit=pending_before)

    assert result["batch_processed"] == pending_before
    assert all(d.mayan_sync_status == "synced" for d in mine)
    assert result["failed_this_batch"] >= 1  # the file-less document
    assert result["synced_this_batch"] + result["failed_this_batch"] == result["batch_processed"]
    assert result["total_synced"] == Doc.search_count([("mayan_sync_status", "=", "synced")])
    assert result["total_records"] == Doc.search_count([])
    assert result["control_totals_match"] is True


# --- destruction guard + disposal register (M24-7) --------------------------------


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


def test_a_bare_delete_never_leaves_a_register_entry(odoo_env):
    doc = _attach(odoo_env)
    doc.write({"state": "expired"})
    with _rejects(odoo_env, UserError, match="only through a recorded disposal"):
        doc.unlink()
    assert doc.exists()


@pytest.mark.parametrize("method", ["secure_wipe", "physical_shredding", "degaussing"])
def test_disposal_records_the_destruction_and_wipes_the_file(odoo_env, method):
    doc = _attach(odoo_env, name="Expired batch %s" % method, raw=b"shred me")
    doc.write({"state": "expired"})
    assert doc.action_dispose(method) is True

    (register,) = odoo_env["fix.disposal.record"].search([("document_id", "=", doc.id)])
    assert register.name == "DISPOSAL/Expired batch %s" % method
    assert register.method == method
    assert register.performed_by_id == odoo_env.user
    certificate = register.certificate_doc_id
    assert certificate.document_type == "destruction_certificate"
    assert certificate.res_model == "fix.document" and certificate.res_id == doc.id
    assert not doc.attachment_id.datas  # the file is gone
    assert (doc.state, doc.active) == ("destroyed", False)
    # the destroyed row anchors its register entry forever
    with _rejects(odoo_env, UserError, match="anchors the permanent disposal register"):
        doc.unlink()
    assert doc.exists()


def test_disposal_register_is_permanent(odoo_env):
    doc = _attach(odoo_env)
    doc.write({"state": "expired"})
    doc.action_dispose()
    (register,) = odoo_env["fix.disposal.record"].search([("document_id", "=", doc.id)])
    with _rejects(odoo_env, UserError, match="permanent"):
        register.with_user(odoo_env.ref("base.user_admin")).unlink()
    assert register.exists()


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
