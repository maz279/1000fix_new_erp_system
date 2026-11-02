"""cd_data_case behaviour (live ORM, rolled back): Journey 11 data recovery.

Every test drives the real models on the `fix_test` database through the
`odoo_env` fixture and asserts results, state, raised errors and the
domain events written to the transactional outbox.
"""

from __future__ import annotations

import base64
import datetime
import json
import os
import time
from types import SimpleNamespace

import pytest
from odoo.addons.auth_totp.models import res_users as auth_totp_users
from odoo.addons.auth_totp.models.totp import TIMESTEP, hotp
from odoo.addons.cd_data_case.models import fix_data_case
from odoo.exceptions import UserError

CASE = "fix.data.recovery.case"
AUDIT = "fix.z4.access.audit"
CERT = "fix.data.wipe.certificate"


@pytest.fixture
def step_up(odoo_env, monkeypatch):
    """A cleanroom technician enrolled in auth_totp, acting inside an
    interactive request; `code(offset)` is their authenticator's current code
    (offset in 30 s time steps)."""
    fake_request = SimpleNamespace(
        httprequest=SimpleNamespace(environ={"REMOTE_ADDR": "10.9.8.7"}), session={}
    )
    monkeypatch.setattr(fix_data_case, "request", fake_request)
    monkeypatch.setattr(auth_totp_users, "request", fake_request)
    secret = base64.b32encode(os.urandom(20)).decode()
    user = odoo_env["res.users"].create(
        {
            "name": "Z4 Cleanroom Lead",
            "login": "z4-step-up-behaviour",
            "group_ids": [(6, 0, [odoo_env.ref("base.group_user").id])],
        }
    )
    user.sudo().write({"totp_secret": secret})
    key = base64.b32decode(secret)

    def code(offset=0):
        return f"{hotp(key, int(time.time() / TIMESTEP) + offset):06d}"

    def wrong_code():
        valid = {code(offset) for offset in (-1, 0, 1)}
        return next(c for c in ("000000", "111111", "222222", "333333") if c not in valid)

    def as_user(record):
        # the accessor's own environment (sudo only bypasses ACLs, uid stays)
        return record.with_user(user).sudo()

    return SimpleNamespace(user=user, code=code, wrong_code=wrong_code, as_user=as_user)


def _events(env, event_type, aggregate, res_id):
    rows = env["fix.event.outbox"].search(
        [
            ("event_type", "=", event_type),
            ("aggregate", "=", aggregate),
            ("aggregate_id", "=", res_id),
        ],
        order="id",
    )
    return [json.loads(r.payload) for r in rows]


def _customer(env, name="Data Case Customer"):
    return env["res.partner"].create({"name": name})


def _case(env, **vals):
    vals.setdefault("customer_id", _customer(env).id)
    return env[CASE].create(vals)


def _case_in(env, state, zone="z4"):
    case = _case(env)
    case.write({"state": state, "residency_zone": zone})
    return case


# --------------------------------------------------------------------------
# fix.data.recovery.case — creation and counters
# --------------------------------------------------------------------------


def test_case_name_uses_default_sequence(odoo_env):
    # iteration 2: data/ir_sequence_data.xml ships DRC/ and DWC/ sequences —
    # the old "DRC/New" fallback only applies when they are deleted.
    case = _case(odoo_env)
    assert case.name.startswith("DRC/")
    assert case.state == "new"
    assert case.residency_zone == "pending"


def test_case_names_are_sequential(odoo_env):
    first, second = odoo_env[CASE].create(
        [{"customer_id": _customer(odoo_env).id}, {"customer_id": _customer(odoo_env).id}]
    )
    assert first.name.startswith("DRC/")
    assert second.name.startswith("DRC/")
    assert first.name != second.name


def test_audit_count_counts_access_reads(odoo_env, step_up):
    case = step_up.as_user(_case_in(odoo_env, "recovered"))
    assert case.audit_count == 0
    case.action_access_recovered_data(step_up.code())
    case.action_access_recovered_data(step_up.code(1), access_type="export")
    assert case.audit_count == 2
    assert sorted(case.audit_ids.mapped("access_type")) == ["export", "file_list_read"]


# --------------------------------------------------------------------------
# Chain of custody
# --------------------------------------------------------------------------


def test_take_custody_logs_handler_and_publishes(odoo_env):
    case = _case(odoo_env)
    case.action_take_custody("Rafiq (front desk)")
    assert case.state == "custody"
    assert "custody taken by Rafiq (front desk)" in case.custody_chain
    assert _events(odoo_env, "data_case.custody_taken", CASE, case.id) == [
        {"case": case.name, "handler": "Rafiq (front desk)"}
    ]


def test_custody_chain_is_append_only_across_handoffs(odoo_env):
    case = _case(odoo_env)
    case.action_take_custody("Desk")
    case.action_log_custody_transfer(
        "Nadia", role="Cleanroom Lead", location="Z4 Vault", notes="sealed bag #7"
    )
    case.action_log_custody_transfer("Karim")
    lines = [line for line in case.custody_chain.split("\n") if line]
    assert len(lines) == 3
    assert "custody taken by Desk" in lines[0]
    assert lines[1].endswith(
        "[Custody Transfer] Handed to Nadia (Cleanroom Lead) at Z4 Vault - sealed bag #7"
    )
    # defaults applied, no notes suffix
    assert lines[2].endswith("[Custody Transfer] Handed to Karim (Technician) at Z4 Lab")
    assert _events(odoo_env, "data_case.custody_transferred", CASE, case.id) == [
        {"case": case.name, "handler": "Nadia", "location": "Z4 Vault"},
        {"case": case.name, "handler": "Karim", "location": "Z4 Lab"},
    ]
    # a custody transfer does not move the lifecycle state
    assert case.state == "custody"


# --------------------------------------------------------------------------
# Recovery gates (SC-007)
# --------------------------------------------------------------------------


def test_start_recovery_requires_custody(odoo_env):
    case = _case(odoo_env, residency_zone="z4")
    with pytest.raises(UserError, match="Recovery starts from custody"):
        case.action_start_recovery()
    assert case.state == "new"


def test_start_recovery_blocked_until_routed_to_z4(odoo_env):
    case = _case_in(odoo_env, "custody", zone="pending")
    with pytest.raises(UserError, match="SC-007"):
        case.action_start_recovery()
    assert case.state == "custody"


def test_start_recovery_from_custody_in_z4(odoo_env):
    case = _case_in(odoo_env, "custody")
    case.action_start_recovery()
    assert case.state == "recovering"


def test_recovered_publishes_event(odoo_env):
    case = _case_in(odoo_env, "recovering")
    case.action_recovered()
    assert case.state == "recovered"
    assert _events(odoo_env, "data_case.recovered", CASE, case.id) == [{"case": case.name}]


# --------------------------------------------------------------------------
# Step-up access + per-read audit (SC-002)
# --------------------------------------------------------------------------


def test_access_refused_outside_z4(odoo_env, step_up):
    case = step_up.as_user(_case_in(odoo_env, "recovered", zone="pending"))
    with pytest.raises(UserError, match="SC-007"):
        case.action_access_recovered_data(step_up.code())
    assert not case.audit_ids


@pytest.mark.parametrize("state", ["new", "custody", "purged", "closed", "unrecoverable"])
def test_access_refused_in_non_readable_state(odoo_env, step_up, state):
    case = step_up.as_user(_case_in(odoo_env, state))
    with pytest.raises(UserError, match=f"'{state}' state"):
        case.action_access_recovered_data(step_up.code())
    assert not case.audit_ids


def _assert_denied(odoo_env, case, token, reason):
    with pytest.raises(UserError, match="Access Denied") as err:
        case.action_access_recovered_data(token)
    assert reason in str(err.value)
    assert not case.audit_ids
    assert _events(odoo_env, "data_case.z4_accessed", CASE, case.id) == []


@pytest.mark.parametrize("token", [None, "", "12345", "1234567", "abcdef", "12 456"])
def test_malformed_step_up_code_is_refused(odoo_env, step_up, token):
    case = step_up.as_user(_case_in(odoo_env, "recovering"))
    _assert_denied(odoo_env, case, token, "a 6-digit authenticator code is required")


@pytest.mark.parametrize("token", ["100024", "MFA-Z4-AUTH", "PASS"])
def test_former_bypass_tokens_are_refused(odoo_env, step_up, token):
    """Regression: the step-up stub accepted the fixed tokens "100024",
    "MFA-Z4-AUTH" and "PASS" (and any 6-digit string) without verification."""
    case = step_up.as_user(_case_in(odoo_env, "recovered"))
    with pytest.raises(UserError, match="Access Denied"):
        case.action_access_recovered_data(token)
    assert not case.audit_ids


def test_unverified_six_digit_code_is_refused(odoo_env, step_up):
    """Regression: any 6-digit string used to pass the step-up check."""
    case = step_up.as_user(_case_in(odoo_env, "recovered"))
    _assert_denied(odoo_env, case, step_up.wrong_code(), "Verification failed")


def test_replayed_code_is_refused(odoo_env, step_up):
    case = step_up.as_user(_case_in(odoo_env, "recovered"))
    code = step_up.code()
    case.action_access_recovered_data(code)
    with pytest.raises(UserError, match="use the latest 6-digit code"):
        case.action_access_recovered_data(code)
    assert len(case.audit_ids) == 1


class _ServerClock(datetime.datetime):
    """odoo-bin runs with TZ=UTC, so auth_totp's naive `datetime.now()` is UTC
    and comparable to `create_date`; this test process keeps the workstation's
    zone, so the rate-limit window is evaluated on the server's (UTC) clock."""

    @classmethod
    def now(cls, tz=None):
        if tz is None:
            return datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
        return super().now(tz)


def test_step_up_attempts_are_rate_limited(odoo_env, step_up, monkeypatch):
    monkeypatch.setattr(auth_totp_users, "datetime", _ServerClock)
    case = step_up.as_user(_case_in(odoo_env, "recovered"))
    for _attempt in range(5):
        with pytest.raises(UserError, match="Verification failed"):
            case.action_access_recovered_data(step_up.wrong_code())
    # even the correct code is refused once the limit is reached
    _assert_denied(odoo_env, case, step_up.code(), "limit of code verifications")


def test_accessor_without_totp_enrolment_is_refused(odoo_env, step_up):
    case = _case_in(odoo_env, "recovered")  # OdooBot: no authenticator enrolled
    _assert_denied(odoo_env, case, step_up.code(), "no authenticator (TOTP) enrolled")


def test_step_up_outside_an_interactive_request_is_refused(odoo_env, step_up, monkeypatch):
    monkeypatch.setattr(fix_data_case, "request", None)
    case = step_up.as_user(_case_in(odoo_env, "recovered"))
    _assert_denied(odoo_env, case, step_up.code(), "requires an interactive session")


def test_step_up_fails_closed_without_auth_totp(odoo_env, step_up, monkeypatch):
    users_cls = type(odoo_env["res.users"])
    without_totp = {k: v for k, v in users_cls._fields.items() if k != "totp_enabled"}
    case = step_up.as_user(_case_in(odoo_env, "recovered"))
    with monkeypatch.context() as patched:
        patched.setattr(users_cls, "_fields", without_totp)
        with pytest.raises(UserError, match=r"auth_totp\) is not available"):
            case.action_access_recovered_data(step_up.code())
    assert not case.audit_ids


@pytest.mark.parametrize("state", ["recovering", "recovered", "handover"])
def test_access_granted_with_verified_totp_writes_audit(odoo_env, step_up, state):
    case = step_up.as_user(_case_in(odoo_env, state))
    result = case.action_access_recovered_data(
        step_up.code(),
        access_type="file_download",
        purpose="Customer handover",
        ip_address="10.0.0.9",
    )
    audit = case.audit_ids
    assert len(audit) == 1
    assert audit.access_type == "file_download"
    assert audit.purpose == "Customer handover"
    assert audit.ip_address == "10.0.0.9"
    assert audit.step_up_verified is True
    assert audit.user_id == step_up.user
    assert audit.user_name == "Z4 Cleanroom Lead"
    assert result["status"] == "granted"
    assert result["audit_hash"] == audit.sha256_audit_hash
    assert result["case"] == case.name
    assert result["access_type"] == "file_download"
    # nothing stored on the case: nothing listed (never invented file names)
    assert result["files"] == []
    assert _events(odoo_env, "data_case.z4_accessed", CASE, case.id) == [
        {"case": case.name, "audit_id": audit.id, "access_type": "file_download"}
    ]


def test_access_lists_the_cases_real_attachments(odoo_env, step_up):
    case = _case_in(odoo_env, "recovered")
    odoo_env["ir.attachment"].create(
        {"name": "recovered.tar.enc", "raw": b"12345", "res_model": CASE, "res_id": case.id}
    )
    result = step_up.as_user(case).action_access_recovered_data(step_up.code())
    assert result["files"] == [{"filename": "recovered.tar.enc", "size_bytes": 5, "zone": "z4"}]


def test_access_requires_a_single_case(odoo_env, step_up):
    cases = _case_in(odoo_env, "recovered") | _case_in(odoo_env, "recovered")
    with pytest.raises(ValueError):
        step_up.as_user(cases).action_access_recovered_data(step_up.code())


# --------------------------------------------------------------------------
# fix.z4.access.audit — immutable statutory log
# --------------------------------------------------------------------------


def test_audit_hash_is_sha256_and_unique_per_entry(odoo_env):
    case = _case(odoo_env)
    vals = {"case_id": case.id, "access_type": "metadata_read", "purpose": "QA"}
    first = odoo_env[AUDIT].create(dict(vals))
    second = odoo_env[AUDIT].create(dict(vals))
    for audit in (first, second):
        assert len(audit.sha256_audit_hash) == 64
        int(audit.sha256_audit_hash, 16)  # hex digest
    assert first.sha256_audit_hash != second.sha256_audit_hash


def test_audit_user_name_defaults_from_accessor(odoo_env):
    user = odoo_env["res.users"].create({"name": "Z4 Auditor", "login": "z4-auditor-behaviour"})
    case = _case(odoo_env)
    audit = odoo_env[AUDIT].create(
        {"case_id": case.id, "user_id": user.id, "access_type": "preview_read", "purpose": "QA"}
    )
    assert audit.user_name == "Z4 Auditor"
    # the environment user is the accessor when none is given
    implicit = odoo_env[AUDIT].create(
        {"case_id": case.id, "access_type": "preview_read", "purpose": "QA"}
    )
    assert implicit.user_id == odoo_env.user
    assert implicit.user_name == odoo_env.user.name


def test_audit_explicit_user_name_is_kept(odoo_env):
    case = _case(odoo_env)
    audit = odoo_env[AUDIT].create(
        {
            "case_id": case.id,
            "access_type": "export",
            "purpose": "QA",
            "user_name": "Badge #42",
        }
    )
    assert audit.user_name == "Badge #42"


def test_audit_inherits_case_company(odoo_env):
    case = _case(odoo_env)
    audit = odoo_env[AUDIT].create({"case_id": case.id, "access_type": "export", "purpose": "QA"})
    assert audit.company_id == case.company_id


def test_audit_cannot_be_modified_or_deleted(odoo_env):
    case = _case(odoo_env)
    audit = odoo_env[AUDIT].create({"case_id": case.id, "access_type": "export", "purpose": "QA"})
    with (
        pytest.raises(UserError, match="Modifications are strictly prohibited"),
        odoo_env.cr.savepoint(),
    ):
        audit.write({"purpose": "tampered"})
    with pytest.raises(UserError, match="Deletion is strictly prohibited"), odoo_env.cr.savepoint():
        audit.unlink()
    assert audit.exists()
    assert audit.purpose == "QA"


# --------------------------------------------------------------------------
# Handover & purge certificate (NFR-095)
# --------------------------------------------------------------------------


def test_handover_requires_recovered(odoo_env):
    case = _case_in(odoo_env, "recovering")
    with pytest.raises(UserError, match="Handover from recovered"):
        case.action_handover("Courier")
    assert case.state == "recovering"


def test_handover_logs_custody(odoo_env):
    case = _case_in(odoo_env, "recovered")
    case.action_handover("Customer counter")
    assert case.state == "handover"
    assert case.custody_chain.strip().endswith("handed over by Customer counter")


def test_purge_requires_handover(odoo_env):
    case = _case_in(odoo_env, "recovered")
    with pytest.raises(UserError, match="Purge from handover"):
        case.action_purge()
    assert not case.purge_certificate_id


def _wipe_log(env, content=b"nwipe 0.34: 1953525168 sectors overwritten, PASS"):
    return env["ir.attachment"].create({"name": "wipe.log", "raw": content})


def _cert(env, **vals):
    vals.setdefault("method", "nist_800_88_purge")
    return env[CERT].create(vals)


def _verified_cert(env, **vals):
    vals.setdefault("sector_count", 1000)
    vals.setdefault("wipe_log_attachment_id", _wipe_log(env).id)
    cert = _cert(env, **vals)
    cert.action_verify()
    return cert


def test_purge_closes_on_the_operators_verified_certificate(odoo_env):
    case = _case_in(odoo_env, "handover")
    cert = _verified_cert(odoo_env, serial_number="WD-123")
    case.action_purge(certificate=cert)
    assert case.state == "purged"
    assert case.purge_certificate_id == cert
    assert cert.statutory_record_retained is True
    assert _events(odoo_env, "data_case.purged", CASE, case.id) == [
        {"certificate": cert.name, "verification_hash": cert.verification_hash}
    ]


def test_purge_never_fabricates_a_certificate(odoo_env):
    case = _case_in(odoo_env, "handover")
    before = odoo_env[CERT].search_count([])
    with pytest.raises(UserError, match="wipe operator"):
        case.action_purge()
    assert odoo_env[CERT].search_count([]) == before
    pending = _cert(odoo_env)
    case.purge_certificate_id = pending
    with pytest.raises(UserError, match="pending_verification"):
        case.action_purge()
    assert case.state == "handover"


# --------------------------------------------------------------------------
# fix.data.wipe.certificate
# --------------------------------------------------------------------------


def test_certificate_starts_pending_with_no_invented_evidence(odoo_env):
    cert = _cert(odoo_env, sanitization_status="verified")
    assert cert.name.startswith("DWC/")
    assert cert.sanitization_status == "pending_verification"  # never born verified
    assert (cert.sector_count, cert.duration_seconds) == (0, 0)
    assert not cert.verification_hash
    assert cert.certified_by == odoo_env.user.name
    assert cert.technician_id == odoo_env.user


def test_certificate_method_is_an_operator_input(odoo_env):
    from psycopg2 import IntegrityError

    with pytest.raises(IntegrityError), odoo_env.cr.savepoint():
        odoo_env[CERT].create({})


def test_verification_requires_the_operators_evidence(odoo_env):
    cert = _cert(odoo_env)
    with pytest.raises(UserError, match=r"sector count.*log attachment"):
        cert.action_verify()
    cert.write({"sector_count": 10, "wipe_log_attachment_id": _wipe_log(odoo_env, b"").id})
    with pytest.raises(UserError, match="non-empty wipe tool log"):
        cert.action_verify()
    assert cert.sanitization_status == "pending_verification"
    destroyed = _cert(
        odoo_env, method="physical_destruction", wipe_log_attachment_id=_wipe_log(odoo_env).id
    )
    destroyed.action_verify()  # no sectors for a shredded platter
    assert destroyed.sanitization_status == "verified"


def test_hash_is_sha256_over_the_evidence_content(odoo_env):
    import hashlib

    log = b"blancco: 500 sectors, PASS"
    cert = _verified_cert(
        odoo_env,
        sector_count=500,
        serial_number="SN-9",
        wipe_log_attachment_id=_wipe_log(odoo_env, log).id,
    )
    expected = hashlib.sha256(log + b"|nist_800_88_purge|500|SN-9").hexdigest()
    assert cert.verification_hash == expected
    assert (cert.sanitization_status, cert.verified_by_id) == ("verified", odoo_env.user)
    assert cert.verified_at
    twin = _verified_cert(
        odoo_env,
        sector_count=500,
        serial_number="SN-9",
        wipe_log_attachment_id=_wipe_log(odoo_env, log).id,
    )
    assert twin.verification_hash == expected  # re-derivable: same evidence, same hash


def test_verified_evidence_is_frozen_and_tampering_is_refused(odoo_env):
    cert = _verified_cert(odoo_env)
    with pytest.raises(UserError, match="frozen"):
        cert.write({"sector_count": 2})
    with pytest.raises(UserError, match="Only a pending"):
        cert.action_verify()
    with pytest.raises(UserError, match="cannot be failed"):
        cert.action_mark_failed()
    tampered = _cert(odoo_env, sector_count=5, wipe_log_attachment_id=_wipe_log(odoo_env).id)
    tampered.wipe_log_attachment_id.raw = b"edited after the fact"
    with pytest.raises(UserError, match="hash mismatch"):
        tampered.action_verify()
    tampered.action_mark_failed()
    assert tampered.sanitization_status == "failed"


def test_certificate_keeps_explicit_certifier_and_uses_sequence(odoo_env):
    cert = odoo_env[CERT].create({"certified_by": "Ext. Auditor", "method": "cryptographic_erase"})
    assert cert.certified_by == "Ext. Auditor"
    assert cert.name.startswith("DWC/")


def test_retained_certificate_cannot_be_deleted(odoo_env):
    kept = _cert(odoo_env)
    disposable = _cert(odoo_env)
    disposable.write({"statutory_record_retained": False})
    with pytest.raises(UserError, match="NFR-095"), odoo_env.cr.savepoint():
        (disposable | kept).unlink()
    assert kept.exists() and disposable.exists()


def test_non_retained_certificates_can_be_deleted(odoo_env):
    certs = _cert(odoo_env) | _cert(odoo_env)
    certs.write({"statutory_record_retained": False})
    certs.unlink()
    assert not certs.exists()
