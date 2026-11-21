"""Journey 11: M06 Data Services & Recovery, walked on the real models.

Milestone R07-M04 / Task R07-M04-T01. One damaged drive goes from intake to a
retained wipe certificate, every step by the person whose job it is, none of
them an administrator (the superuser is trusted by the guards and would hide
a gap):

1. Intake and initial custody: the chain of custody begins.
2. A structured custody hand-off is appended to the chain.
3. SC-007: recovery is refused until the case is routed to Z4.
4. SC-002: reading recovered data needs the accessor's own TOTP step-up.
5. SC-002: a verified read returns the case's files and writes one audit row;
   the same code cannot be replayed.
6. SC-002: the Z4 access audit is append-only.
7. Hand-over to the verified recipient, then purge on the wipe operator's
   verified NIST SP 800-88 certificate.
8. NFR-095: the certificate is a permanent statutory record.

This replaces the earlier unittest double of the case, which stopped matching
the model once custody moved to its own ledger and recovery gained its
evaluation, quote, named-staff and image checks. The same controls are tested
one by one in test_a02_p0_m06.py, test_a02_p1p2_cd_data_case.py and
test_data_case_behaviour.py; this file is the end-to-end walk Gate G6-4/G6-6
executes.
"""

from __future__ import annotations

import base64
import itertools
import os
import time
from types import SimpleNamespace
from unittest import mock

import pytest
from odoo.addons.auth_totp.models import res_users as auth_totp_users
from odoo.addons.auth_totp.models.totp import TIMESTEP, hotp
from odoo.addons.cd_data_case.models import fix_data_case
from odoo.exceptions import AccessError, UserError

CASE = "fix.data.recovery.case"
CERT = "fix.data.wipe.certificate"
AUDIT = "fix.z4.access.audit"
_SEQ = itertools.count(1)


@pytest.fixture
def j11(odoo_env, monkeypatch):
    env = odoo_env
    n = next(_SEQ)
    base = env.ref("base.group_user")
    Users = env["res.users"].with_context(no_reset_password=True)

    def user(name, *groups):
        return Users.create(
            {
                "name": "J11 %s %d" % (name, n),
                "login": "j11.%s.%d@journey11.test" % (name.lower().replace(" ", "."), n),
                "group_ids": [(6, 0, [base.id, *[env.ref(g).id for g in groups]])],
            }
        )

    tech = user("Lab Engineer", "cd_data_case.group_data_recovery_operator")
    tech2 = user("Second Engineer", "cd_data_case.group_data_recovery_operator")
    verifier = user("Wipe Verifier", "cd_data_case.group_wipe_verifier")
    custodian = user("Cleanroom Lead", "cd_data_case.group_z4_custodian")
    assert not any(u.has_group("base.group_system") for u in (tech, verifier, custodian))
    customer = env["res.partner"].create({"name": "J11 Customer %d" % n, "phone": "01711000555"})

    # the custodian is enrolled in auth_totp and acts inside an interactive request
    secret = base64.b32encode(os.urandom(20)).decode()
    custodian.sudo().write({"totp_secret": secret})
    key = base64.b32decode(secret)
    fake_request = SimpleNamespace(
        httprequest=SimpleNamespace(environ={"REMOTE_ADDR": "192.168.10.45"}), session={}
    )
    monkeypatch.setattr(fix_data_case, "request", fake_request)
    monkeypatch.setattr(auth_totp_users, "request", fake_request)

    def code(offset=0):
        return f"{hotp(key, int(time.time() / TIMESTEP) + offset):06d}"

    serial = "WD-J11-%d" % n
    image_hash = "%064x" % (0xD11 * n)

    def intake():
        case = (
            env[CASE]
            .with_user(tech)
            .create(
                {"customer_id": customer.id, "media_type": "hdd", "media_serial_number": serial}
            )
        )
        # M06 capture pass 2 (BRU-DTS-12): undertakings before access
        for person in (tech, custodian):
            env["fix.data.confidentiality.undertaking"].with_user(person).create(
                {
                    "case_id": case.id,
                    "undertaking_type": "staff",
                    "user_id": person.id,
                    "acknowledged": True,
                }
            )
        case.action_assign_staff(technician=tech, custodian=custodian)
        return case

    def custody(case, giver=None, receiver=None):
        """A02 pass 2 M06-03: sealed media, then the receiver confirms."""
        giver, receiver = giver or custodian, receiver or tech
        if not case.sudo().media_unit_ids:
            env["fix.data.media.unit"].sudo().create(
                {"case_id": case.id, "seal_number": "J11-SEAL-%d-%d" % (n, case.id)}
            )
        case.with_user(giver).action_take_custody(receiver.login)
        case.with_user(receiver).action_confirm_custody()
        return case

    def purge_cert(case):
        """A02 pass 2 M06-04 (D15): the lab's purge certificate of the case."""
        log = (
            env["ir.attachment"]
            .with_user(tech)
            .create({"name": "purge.log", "raw": b"Z4 working copy and key destroyed"})
        )
        cert = (
            env[CERT]
            .with_user(tech)
            .create(
                {
                    "purpose": "case_purge",
                    "case_id": case.id,
                    "lab_storage_ref": "Z4-VOL-J11-%d" % case.id,
                    "method": "cryptographic_erase",
                    "sector_count": 1000,
                    "wipe_log_attachment_id": log.id,
                }
            )
        )
        cert.with_user(verifier).action_verify()
        return cert

    def evaluated_and_quoted(case):
        env["fix.data.evaluation"].with_user(tech).create(
            {"case_id": case.id, "verdict": "recoverable"}
        ).action_complete()
        quote = env["fix.data.quote"].with_user(tech).create({"case_id": case.id, "amount": 15000})
        quote.action_send()
        quote.action_accept(acceptance_reference="OTP-%06d" % (n * 11))

    def recovered():
        case = intake()
        custody(case)
        case.action_route_to_z4()
        evaluated_and_quoted(case)
        case.action_start_recovery()
        env["fix.data.recovery.attempt"].with_user(tech).create(
            {"case_id": case.id, "method": "software_scan"}
        ).action_finish(outcome="success")
        case.action_record_image(source_hash=image_hash, image_hash=image_hash)
        # the case's custodian is its second person (A02 pass 2 M06-02)
        case.with_user(custodian).action_verify_image(recomputed_hash=image_hash)
        case.action_recovered()
        return case

    def handed_over(case, handler="Customer Rep Farzana"):
        target = "TGT-J11-%d" % n
        case.write({"handover_recipient_id": customer.id, "encrypted_target_serial": target})
        case.action_confirm_target_serial(target)
        env["ir.attachment"].with_user(tech).create(
            {"name": "receipt.pdf", "raw": b"%PDF receipt", "res_model": CASE, "res_id": case.id}
        )
        sent = {}

        def _send(self, recipient, phone, code):
            sent["code"] = code
            return {"destination": "017*****555"}

        with mock.patch.object(type(case), "_handover_send_code", _send):
            case.action_request_handover_otp()
        # A02 ERP audit M06-F1: a billable case goes out paid, on credit or waived
        case.sudo().action_waive_charge(note="test: the hand-over path, charge waived")
        case.action_handover(handler, verification=sent["code"])
        return case

    def verified_cert():
        log = (
            env["ir.attachment"]
            .with_user(tech)
            .create({"name": "wipe.log", "raw": b"nwipe: 1953525168 sectors overwritten, PASS"})
        )
        cert = (
            env[CERT]
            .with_user(tech)
            .create(
                {
                    "method": "nist_800_88",
                    "sector_count": 1000,
                    "serial_number": serial,
                    "wipe_log_attachment_id": log.id,
                }
            )
        )
        cert.with_user(verifier).action_verify()
        return cert

    return SimpleNamespace(
        env=env,
        tech=tech,
        custodian=custodian,
        code=code,
        intake=intake,
        evaluated_and_quoted=evaluated_and_quoted,
        recovered=recovered,
        handed_over=handed_over,
        verified_cert=verified_cert,
        custody=custody,
        purge_cert=purge_cert,
        tech2=tech2,
    )


def test_01_intake_and_custody_logging(j11):
    case = j11.intake()
    assert (case.state, case.residency_zone) == ("new", "pending")
    j11.custody(case)
    assert case.state == "custody"
    assert "custody taken by" in case.custody_chain
    # naming the case's Z4 staff at intake is itself the first ledger entry;
    # A02 pass 2 M06-03: the hand-off is requested by one, taken by the other
    assert case.custody_event_ids.mapped("action") == [
        "z4_assigned",
        "custody_requested",
        "custody_taken",
    ]
    taken = case.custody_event_ids[-1]
    assert (taken.actor_id, taken.witness_id) == (j11.tech, j11.custodian)


def test_02_custody_transfer_preserves_audit_trail(j11):
    case = j11.intake()
    j11.custody(case)
    case.action_log_custody_transfer(
        handler=j11.custodian.login,
        role="Z4 Cleanroom Lead",
        location="Sovereign Cleanroom Vault 1",
        notes="Sealed electrostatic carrier transfer",
    )
    case.with_user(j11.custodian).action_confirm_custody()
    assert "Z4 Cleanroom Lead at Sovereign Cleanroom Vault 1" in case.custody_chain
    assert "Sealed electrostatic carrier transfer" in case.custody_chain
    events = case.custody_event_ids
    assert events.mapped("action") == [
        "z4_assigned",
        "custody_requested",
        "custody_taken",
        "custody_requested",
        "custody_transfer",
    ]
    assert events[4].prev_hash == events[3].entry_hash  # chained, append-only
    assert (events[4].actor_id, events[4].witness_id) == (j11.custodian, j11.tech)


def test_03_strict_z4_residency_gate_enforced(j11):
    case = j11.intake()
    j11.custody(case)
    j11.evaluated_and_quoted(case)
    with pytest.raises(UserError, match="SC-007"):
        case.action_start_recovery()
    assert case.state == "custody"
    # the zone is never typed: only the routing action sets it
    with pytest.raises(UserError):
        case.write({"residency_zone": "z4"})
    case.action_route_to_z4()
    case.action_start_recovery()
    assert case.state == "recovering"


def test_04_step_up_refused_without_the_accessors_own_code(j11):
    case = j11.recovered()
    assert case.state == "recovered"
    # the lab engineer is not a Z4 custodian
    with pytest.raises(AccessError, match="Z4 Custodian"):
        case.action_access_recovered_data(step_up_token=j11.code())
    as_custodian = case.with_user(j11.custodian)
    with pytest.raises(UserError, match="Access Denied"):
        as_custodian.action_access_recovered_data(step_up_token="")
    with pytest.raises(UserError, match="Access Denied"):
        as_custodian.action_access_recovered_data(step_up_token="BAD-TOKEN")
    wrong = next(
        c for c in ("000000", "111111", "222222") if c not in {j11.code(o) for o in (-1, 0, 1)}
    )
    with pytest.raises(UserError, match="Access Denied"):
        as_custodian.action_access_recovered_data(step_up_token=wrong)
    assert not case.audit_ids, "a refused step-up writes no audit row"


def test_05_verified_read_lists_the_files_and_audits_each_read(j11):
    case = j11.recovered()
    for name, raw in (("IMG_0001.jpg", b"x" * 2048), ("contacts.vcf", b"y" * 512)):
        j11.env["ir.attachment"].create(
            {"name": name, "raw": raw, "res_model": CASE, "res_id": case.id}
        )
    as_custodian = case.with_user(j11.custodian)
    code = j11.code()
    result = as_custodian.action_access_recovered_data(
        step_up_token=code,
        access_type="file_list_read",
        purpose="Statutory Legal Hold Inspection",
        ip_address="192.168.10.45",
    )
    assert result["status"] == "granted" and result["audit_hash"]
    assert sorted((f["filename"], f["size_bytes"]) for f in result["files"]) == [
        ("IMG_0001.jpg", 2048),
        ("contacts.vcf", 512),
    ]
    audit = case.audit_ids
    assert len(audit) == 1
    assert (audit.access_type, audit.purpose, audit.ip_address) == (
        "file_list_read",
        "Statutory Legal Hold Inspection",
        "192.168.10.45",
    )
    assert audit.step_up_verified and audit.user_id == j11.custodian
    assert result["audit_hash"] == audit.sha256_audit_hash
    # the same code cannot be replayed; the next one is audited separately
    with pytest.raises(UserError, match="use the latest 6-digit code"):
        as_custodian.action_access_recovered_data(step_up_token=code)
    assert len(case.audit_ids) == 1
    as_custodian.action_access_recovered_data(step_up_token=j11.code(1))
    assert len(case.audit_ids) == 2


def test_06_z4_audit_log_immutability(j11):
    case = j11.recovered()
    case.with_user(j11.custodian).action_access_recovered_data(step_up_token=j11.code())
    audit = case.audit_ids
    with pytest.raises(UserError, match="Modifications are strictly prohibited"):
        audit.write({"purpose": "Altered Purpose"})
    with pytest.raises(UserError, match="Deletion is strictly prohibited"):
        audit.unlink()
    # and no one writes an audit row by hand
    with pytest.raises(AccessError):
        j11.env[AUDIT].with_user(j11.tech).create(
            {"case_id": case.id, "access_type": "file_download", "purpose": "forged"}
        )
    assert audit.exists() and audit.purpose != "Altered Purpose"


def test_07_handover_then_purge_on_the_verified_certificate(j11):
    case = j11.handed_over(j11.recovered())
    assert case.state == "handover"
    assert "handed over by Customer Rep Farzana" in case.custody_chain
    # a purge never fabricates a certificate
    with pytest.raises(UserError, match="wipe operator"):
        case.action_purge()
    # A02 pass 2 M06-04: a certificate of the customer's drive proves no purge
    with pytest.raises(UserError, match="never proves a purge"):
        case.action_purge(certificate=j11.verified_cert())
    cert = j11.purge_cert(case)
    case.action_purge(certificate=cert)
    assert case.state == "purged"
    assert case.purge_certificate_id == cert
    assert cert.sanitization_status == "verified"
    assert cert.statutory_record_retained is True
    assert cert.verification_hash


def test_08_wipe_certificate_permanent_statutory_retention(j11):
    case = j11.handed_over(j11.recovered())
    cert = j11.purge_cert(case)
    case.action_purge(certificate=cert)
    with pytest.raises(UserError, match="NFR-095"):
        cert.unlink()
    assert cert.exists()
