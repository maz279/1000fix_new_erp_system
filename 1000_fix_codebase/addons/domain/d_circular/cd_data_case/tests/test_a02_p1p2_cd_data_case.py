"""A02 audit P1/P2 for M06 Data Services & Recovery (B1 routing, B4 crons, P2).

Both ways for every control, acting as freshly created NON-ADMIN users with
only the M06 roles they need (the superuser is trusted by the guards).

  B1  a re-quote that raises the price (or drops no-data-no-fee) is an M63
      routed approval for the lab manager; it cannot be sent before that.
  B4  retention purge (only on a verified wipe certificate, behind a switch)
      and the restore-test due job.
  P2  named Z4 staff; imaging as a verified step with a frozen hash; the
      quote needs a completed, recoverable evaluation; handover to a verified
      recipient with a receipt and the confirmed target drive.

``odoo_env`` (addons/conftest.py): rolled back after every test.
"""

import itertools
from datetime import timedelta
from types import SimpleNamespace
from unittest import mock

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_workflow_engine.tests.approval_helpers import (
    approve_via_inbox,
    assigned,
)
from odoo.exceptions import AccessError, UserError

CASE = "fix.data.recovery.case"
QUOTE = "fix.data.quote"
ROUTED = "approver's inbox"
GUARD = "changes only through its workflow"
AUTO_PURGE = "cd_data_case.retention_auto_purge"
_SEQ = itertools.count(1)


class _FakeRequest:
    def __init__(self, env):
        self.env = env


@pytest.fixture
def m6(odoo_env):
    env = odoo_env
    n = next(_SEQ)
    ref = env.ref
    Users = env["res.users"].with_context(no_reset_password=True)

    def user(key, *groups):
        return Users.create(
            {
                "name": "A02 P1 M06 %s %d" % (key, n),
                "login": "a02.p1.m06.%s.%d@a02.test" % (key, n),
                "group_ids": [(6, 0, [ref("base.group_user").id] + [ref(g).id for g in groups])],
            }
        )

    op = "cd_data_case.group_data_recovery_operator"
    tech = user("tech", op)
    tech2 = user("tech2", op)
    custodian = user("custodian", "cd_data_case.group_z4_custodian")
    manager = user("manager", "cd_data_case.group_data_lab_manager")
    manager2 = user("manager2", "cd_data_case.group_data_lab_manager")
    verifier = user("verifier", "cd_data_case.group_wipe_verifier")
    customer = env["res.partner"].create(
        {"name": "A02 P1 M06 Customer %d" % n, "is_company": True, "phone": "01711000666"}
    )
    contact = env["res.partner"].create(
        {"name": "Customer's courier", "parent_id": customer.id, "phone": "01711000777"}
    )
    digest = "%064x" % (0xD06 * n)

    def undertake(case, *people):
        """M06 capture pass 2 (BRU-DTS-12): each person accepts the case's
        confidentiality undertaking themself before they are named on it."""
        for person in people:
            env["fix.data.confidentiality.undertaking"].with_user(person).create(
                {
                    "case_id": case.id,
                    "undertaking_type": "staff",
                    "user_id": person.id,
                    "acknowledged": True,
                }
            )

    def new_case(serial="WD-P1-%d" % n, staffed=True):
        case = (
            env[CASE]
            .with_user(tech)
            .create(
                {"customer_id": customer.id, "media_type": "hdd", "media_serial_number": serial}
            )
        )
        undertake(case, tech, custodian)
        if staffed:
            case.action_assign_staff(technician=tech, custodian=custodian)
        return case

    def custody(case, giver=None, receiver=None):
        """A02 pass 2 M06-03: the media is sealed, then one person hands the
        case over and the receiver confirms it in their own session."""
        giver, receiver = giver or custodian, receiver or tech
        if not case.sudo().media_unit_ids:
            env["fix.data.media.unit"].sudo().create(
                {"case_id": case.id, "seal_number": "SEAL-P1-%d-%d" % (n, case.id)}
            )
        case.with_user(giver).action_take_custody(receiver.login)
        case.with_user(receiver).action_confirm_custody()
        return case

    def purge_cert(case, ref=None, verify=True):
        """A02 pass 2 M06-04 (D15): the lab's purge certificate of the case."""
        log = (
            env["ir.attachment"]
            .with_user(tech)
            .create({"name": "purge.log", "raw": b"lab copy %d destroyed" % case.id})
        )
        cert = (
            env["fix.data.wipe.certificate"]
            .with_user(tech)
            .create(
                {
                    "purpose": "case_purge",
                    "case_id": case.id,
                    "lab_storage_ref": ref or "Z4-VOL-%d" % case.id,
                    "method": "cryptographic_erase",
                    "sector_count": 1000,
                    "wipe_log_attachment_id": log.id,
                }
            )
        )
        if verify:
            cert.with_user(verifier).action_verify()
        return cert

    def evaluate(case, verdict="recoverable"):
        env["fix.data.evaluation"].with_user(tech).create(
            {"case_id": case.id, "verdict": verdict}
        ).action_complete()

    def quote(case, amount=15000, **vals):
        return env[QUOTE].with_user(tech).create({"case_id": case.id, "amount": amount, **vals})

    def recovering(case):
        custody(case)
        case.action_route_to_z4()
        evaluate(case)
        q = quote(case)
        q.action_send()
        q.action_accept(acceptance_reference="OTP-%06d" % n)
        case.action_start_recovery()
        env["fix.data.recovery.attempt"].with_user(tech).create(
            {"case_id": case.id, "method": "software_scan"}
        ).action_finish(outcome="success")
        return case

    def image(case):
        case.action_record_image(source_hash=digest, image_hash=digest)
        # the second person is the case's custodian (A02 pass 2 M06-02: an
        # operator not named on a case does not see it)
        case.with_user(custodian).action_verify_image(recomputed_hash=digest)

    def recovered(case):
        recovering(case)
        image(case)
        case.action_recovered()
        return case

    def code_for(case):
        sent = {}

        def _send(self, recipient, phone, code):
            sent.update(recipient=recipient, phone=phone, code=code)
            return {"destination": "017*****777"}

        with mock.patch.object(type(case), "_handover_send_code", _send):
            case.action_request_handover_otp()
        return sent

    def receipt(case, name="receipt-signed.pdf"):
        return (
            env["ir.attachment"]
            .with_user(tech)
            .create({"name": name, "raw": b"%PDF signed", "res_model": CASE, "res_id": case.id})
        )

    def settle(case):
        """A02 ERP audit M06-F1: a billable case goes out on its paid M20
        invoice, a credit approval or a waiver (the lab manager's here)."""
        case.with_user(manager2).action_waive_charge(note="goodwill: test of the hand-over path")

    def handed_over(case, target="TGT-P1-%d" % n):
        recovered(case)
        settle(case)
        case.write({"handover_recipient_id": contact.id, "encrypted_target_serial": target})
        case.action_confirm_target_serial(target)
        receipt(case)
        case.action_handover(verification=code_for(case)["code"])
        return case

    def p03_action(who, model, rec, method, kwargs=None):
        with mock.patch.object(api, "request", _FakeRequest(env(user=who.id))):
            return api.P03GenericApiController().model_action(
                model=model, ids=rec.ids, method=method, kwargs=kwargs
            )

    def p03_write(who, model, rec, values):
        with mock.patch.object(api, "request", _FakeRequest(env(user=who.id))):
            return api.P03GenericApiController().model_write(
                model=model, record_id=rec.id, values=values
            )

    return SimpleNamespace(**locals())


# =========================================================== B1 · re-quote


def _sent_and_requoted(m6):
    case = m6.new_case()
    m6.custody(case)
    m6.evaluate(case)
    first = m6.quote(case, amount=15000)
    first.action_send()
    out = first.action_requote()
    return case, first, m6.env[QUOTE].browse(out["quote_ids"]).with_user(m6.tech)


def test_b1_a_requote_at_the_same_price_needs_no_approval(m6):
    _case, first, new = _sent_and_requoted(m6)
    assert new.supersedes_id == first and not new._approval_needed()
    new.action_send()
    assert new.state == "sent"


def test_b1_a_raised_requote_is_decided_by_the_lab_manager_in_the_inbox(m6):
    _case, _first, new = _sent_and_requoted(m6)
    new.write({"amount": 95000})
    with pytest.raises(UserError, match="lab manager"):
        new.action_send()
    with pytest.raises(UserError, match=ROUTED):
        new.with_user(m6.manager).action_approve_requote()
    new.action_request_approval(justification="second platter damaged")
    assert new.approval_state == "pending"
    assert assigned(new) == m6.manager | m6.manager2 and m6.tech not in assigned(new)
    approve_via_inbox(new, m6.manager)
    assert new.requote_approved_by_id == m6.manager and new.requote_approved_total == 95000
    new.action_send()
    assert new.state == "sent"


def test_b1_the_approval_covers_the_price_it_was_given_for(m6):
    _case, _first, new = _sent_and_requoted(m6)
    new.write({"amount": 30000})
    approve_via_inbox(new, m6.manager, requester=m6.tech)
    new.write({"amount": 95000})  # raised again after approval
    assert new.approval_state == "none"
    with pytest.raises(UserError, match="lab manager"):
        new.action_send()


def test_b1_dropping_no_data_no_fee_needs_the_approval_too(m6):
    _case, _first, new = _sent_and_requoted(m6)
    new.write({"no_data_no_fee_applies": False})
    with pytest.raises(UserError, match="no-data-no-fee"):
        new.action_send()


def test_b1_the_person_who_raised_the_price_is_never_routed_it(m6):
    _case, _first, new = _sent_and_requoted(m6)
    new.with_user(m6.manager).write({"amount": 50000})  # the manager raised it
    new.action_request_approval(justification="extra donor")
    assert m6.manager not in assigned(new) and assigned(new) == m6.manager2


# =========================================================== P2 · evaluation


def test_p2_a_quote_needs_a_completed_recoverable_evaluation(m6):
    case = m6.new_case()
    with pytest.raises(UserError, match="complete the free evaluation"):
        m6.quote(case)
    draft_eval = m6.env["fix.data.evaluation"].with_user(m6.tech).create({"case_id": case.id})
    with pytest.raises(UserError, match="complete the free evaluation"):
        m6.quote(case)
    draft_eval.write({"verdict": "unrecoverable"})
    draft_eval.action_complete()
    with pytest.raises(UserError, match="evaluated unrecoverable"):
        m6.quote(case)
    other = m6.new_case(serial="WD-P1-OK-%d" % m6.n)
    m6.evaluate(other, verdict="partial")
    assert m6.quote(other).state == "draft"


# ============================================================== P2 · Z4 staff


def test_p2_z4_work_is_for_the_named_staff_only(m6):
    case = m6.new_case(staffed=False)
    m6.custody(case)
    case.action_route_to_z4()
    m6.evaluate(case)
    q = m6.quote(case)
    q.action_send()
    q.action_accept(acceptance_reference="OTP-777123")
    with pytest.raises(AccessError, match="needs named Z4 staff"):
        case.action_start_recovery()
    with pytest.raises(UserError, match="Z4 Custodian role"):
        case.action_assign_staff(custodian=m6.tech2)
    with pytest.raises(UserError, match="Data Recovery Operator role"):
        case.action_assign_staff(technician=m6.verifier)
    case.action_assign_staff(technician=m6.tech, custodian=m6.custodian)
    with pytest.raises(UserError, match=GUARD):
        case.with_user(m6.tech2).write({"assigned_technician_id": m6.tech2.id})
    with pytest.raises(AccessError, match="assigned staff"):
        case.with_user(m6.tech2).action_start_recovery()
    case.action_start_recovery()
    with pytest.raises(AccessError, match="assigned staff"):
        m6.env["fix.data.recovery.attempt"].with_user(m6.tech2).create(
            {"case_id": case.id, "method": "software_scan"}
        )
    # once recovery started only a Z4 custodian re-assigns
    m6.undertake(case, m6.tech2)
    with pytest.raises(AccessError, match="Z4 Custodian"):
        case.action_assign_staff(technician=m6.tech2)
    case.with_user(m6.custodian).action_assign_staff(technician=m6.tech2)
    assert case.assigned_technician_id == m6.tech2
    assert "z4_assigned" in case.custody_event_ids.mapped("action")


def test_p2_z4_read_needs_the_assigned_custodian(m6):
    case = m6.recovering(m6.new_case())
    stranger = m6.user("othercust", "cd_data_case.group_z4_custodian")
    # an unassigned custodian does not even see the case (the M06-02 rule)
    with pytest.raises(AccessError, match="doesn't have 'read' access"):
        case.with_user(stranger).action_access_recovered_data(step_up_token="123456")
    # one who sees every case (a lab manager) is still not its Z4 staff
    overseer = m6.user(
        "overseer", "cd_data_case.group_z4_custodian", "cd_data_case.group_data_lab_manager"
    )
    with pytest.raises(AccessError, match="assigned staff"):
        case.with_user(overseer).action_access_recovered_data(step_up_token="123456")
    with pytest.raises(UserError, match="Access Denied"):  # assigned: on to the TOTP step
        case.with_user(m6.custodian).action_access_recovered_data(step_up_token="123456")


# ============================================================== P2 · imaging


def test_p2_imaging_is_a_verified_step_and_the_hash_freezes(m6):
    case = m6.recovering(m6.new_case())
    with pytest.raises(UserError, match=GUARD):
        case.write({"image_sha256_hash": m6.digest})
    res = m6.p03_write(m6.tech, CASE, case, {"image_sha256_hash": m6.digest})
    assert "error" in res
    with pytest.raises(UserError, match="64 hex digits"):
        case.action_record_image(source_hash="abc", image_hash="def")
    # the Z4 staff check refuses an operator not named on the case
    with pytest.raises(AccessError, match="assigned staff"):
        case.with_user(m6.tech2).action_record_image(hashes="%s %s" % (m6.digest, m6.digest))
    # a lab manager sees it but is not its Z4 staff
    with pytest.raises(AccessError, match="assigned staff"):
        case.with_user(m6.manager).action_record_image(hashes="%s %s" % (m6.digest, m6.digest))
    out = m6.p03_action(
        m6.tech, CASE, case, "action_record_image", {"hashes": "%s %s" % (m6.digest, m6.digest)}
    )
    assert out["success"], out
    # A02 ERP audit M06-F12: the hash is withheld until a second person verifies it
    assert not case.image_sha256_hash and case.imaged_by_id == m6.tech
    with pytest.raises(UserError, match="verified forensic image"):
        case.action_recovered()
    with pytest.raises(UserError, match="Segregation of duties"):
        case.action_verify_image(recomputed_hash=m6.digest)
    # the second person is the case's custodian (an unassigned operator does
    # not see the case: M06-02)
    with pytest.raises(UserError, match="does not match"):
        case.with_user(m6.custodian).action_verify_image(recomputed_hash="f" * 64)
    case.with_user(m6.custodian).action_verify_image(recomputed_hash=m6.digest.upper())
    assert case.image_verify_method == "second_person" and case.image_matches_source
    assert case.image_sha256_hash == m6.digest
    with pytest.raises(UserError, match="frozen"):
        case.action_record_image(source_hash=m6.digest, image_hash="e" * 64)
    case.action_recovered()
    assert case.state == "recovered"


def test_p2_the_second_person_rule_is_a_switch(m6):
    m6.env["ir.config_parameter"].set_param("cd_data_case.image_verification_second_person", "0")
    case = m6.recovering(m6.new_case())
    case.action_record_image(source_hash="1" * 64, image_hash=m6.digest)
    case.action_verify_image(recomputed_hash=m6.digest)
    assert case.image_verify_method == "recomputed" and not case.image_matches_source


# ============================================================== P2 · handover


def test_p2_handover_needs_a_verified_recipient_receipt_and_target(m6):
    case = m6.recovered(m6.new_case())
    m6.settle(case)
    stranger = m6.env["res.partner"].create({"name": "Walk-in stranger", "phone": "01711000888"})
    with pytest.raises(UserError, match="name the handover recipient"):
        case.action_handover(verification="123456")
    case.write({"handover_recipient_id": stranger.id, "encrypted_target_serial": "TGT-X1"})
    with pytest.raises(UserError, match="not the customer"):
        case.action_request_handover_otp()
    case.write({"handover_recipient_id": m6.contact.id})
    with pytest.raises(UserError, match="confirm the target drive"):
        case.action_handover(verification="123456")
    with pytest.raises(UserError, match="not the recorded target drive"):
        case.action_confirm_target_serial("TGT-X2")
    case.action_confirm_target_serial("tgt-x1")
    with pytest.raises(UserError, match="fixed once the target serial"):
        case.write({"encrypted_target_serial": "TGT-OTHER"})
    sent = m6.code_for(case)
    assert sent["recipient"] == m6.contact and sent["phone"] == "01711000777"
    bad = "000000" if sent["code"] != "000000" else "111111"
    with pytest.raises(UserError, match="does not match"):
        case.action_handover(verification=bad)
    assert case.handover_code_attempts == 1
    with pytest.raises(UserError, match="handover receipt"):
        case.action_handover(verification=sent["code"])
    m6.receipt(case, name="Receipt.pdf")
    with pytest.raises(AccessError, match="assigned staff"):
        case.with_user(m6.tech2).action_handover(verification=sent["code"])
    out = m6.p03_action(m6.tech, CASE, case, "action_handover", {"verification": sent["code"]})
    assert out["success"], out
    assert case.state == "handover" and case.handover_verification_method == "otp"
    assert case.handover_receipt_attachment_id.name == "Receipt.pdf"
    assert case.retention_until == fields.Date.context_today(case) + timedelta(days=30)
    assert "to %s" % m6.contact.display_name in case.custody_chain


def test_p2_handover_by_a_verified_id_document(m6):
    case = m6.recovered(m6.new_case())
    m6.settle(case)
    case.write({"handover_recipient_id": m6.customer.id, "encrypted_target_serial": "TGT-ID"})
    case.action_confirm_target_serial("TGT-ID")
    m6.receipt(case)
    with pytest.raises(UserError, match="none is on file"):
        case.action_handover(verification="1234567890")
    doc = m6.env["fix.identity.document"].create(
        {"partner_id": m6.customer.id, "document_type": "nid_10", "document_number": "1987654321"}
    )
    doc.write({"verification_status": "verified"})
    if doc.read(["document_number"])[0]["document_number"] != "1987654321":
        # the local residency service answers with synthetic values (DE-12)
        pytest.skip("the Z4 residency store does not return stored values here")
    with pytest.raises(UserError, match="does not match"):
        case.action_handover(verification="1234567890")
    case.action_handover(verification="1987 654 321")
    assert case.handover_verification_ref == "ID ****4321"


# ============================================================ B4 · retention


def _cert(m6, serial):
    att = (
        m6.env["ir.attachment"]
        .with_user(m6.tech)
        .create({"name": "wipe.log", "raw": b"nwipe PASS %s" % serial.encode()})
    )
    cert = (
        m6.env["fix.data.wipe.certificate"]
        .with_user(m6.tech)
        .create(
            {
                "method": "nist_800_88",
                "sector_count": 1000,
                "serial_number": serial,
                "wipe_log_attachment_id": att.id,
            }
        )
    )
    cert.with_user(m6.verifier).action_verify()
    return cert


def _past_retention(case):
    case._guarded().write({"retention_until": fields.Date.today() - timedelta(days=1)})


def test_b4_retention_flags_and_never_purges_by_default(m6):
    case = m6.handed_over(m6.new_case())
    _cert(m6, case.media_serial_number)
    Case = m6.env[CASE]
    assert Case.cron_retention_purge() == 0  # not yet due
    _past_retention(case)
    assert Case.cron_retention_purge() == 0
    assert case.state == "handover" and case.retention_flagged_at
    activity = case.activity_ids.filtered(lambda a: "Retention ended" in (a.summary or ""))
    assert len(activity) == 1 and activity.user_id == m6.tech
    Case.cron_retention_purge()  # once
    assert len(case.activity_ids.filtered(lambda a: "Retention ended" in (a.summary or ""))) == 1


def test_b4_auto_purge_only_on_a_verified_certificate_for_the_media(m6):
    m6.env["ir.config_parameter"].set_param(AUTO_PURGE, "1")
    Case = m6.env[CASE]
    no_cert = m6.handed_over(m6.new_case(serial="WD-NOCERT-%d" % m6.n), target="T-A")
    _cert(m6, "SOME-OTHER-DRIVE-%d" % m6.n)  # binds another serial
    with_cert = m6.handed_over(m6.new_case(serial="WD-CERT-%d" % m6.n), target="T-B")
    # A02 pass 2 M06-04 (D15): the purge is proved by the lab's purge
    # certificate of the case, never by a drive certificate
    _cert(m6, with_cert.media_serial_number)
    cert = m6.purge_cert(with_cert)
    _past_retention(no_cert)
    _past_retention(with_cert)
    assert Case.cron_retention_purge() == 1
    assert with_cert.state == "purged" and with_cert.purge_certificate_id == cert
    assert no_cert.state == "handover" and no_cert.retention_flagged_at


def test_b4_m06_crons_are_scheduled(m6):
    for xmlid in (
        "cd_data_case.ir_cron_data_case_retention_purge",
        "cd_data_case.ir_cron_data_backup_restore_test_due",
    ):
        assert m6.env.ref(xmlid).active


# ======================================================== B4 · restore tests


def test_b4_restore_test_due_is_scheduled_and_reminded_once(m6):
    Plan = m6.env["fix.data.backup.plan"].with_user(m6.tech)
    plan = Plan.create(
        {"name": "NAS 3-2-1", "customer_id": m6.customer.id, "test_frequency_days": 30}
    )
    assert plan.next_test_due == fields.Date.context_today(plan) + timedelta(days=30)
    plan.write({"next_test_due": fields.Date.context_today(plan) - timedelta(days=2)})
    Plan = m6.env["fix.data.backup.plan"]
    assert Plan.cron_restore_test_due() >= 1
    todo = plan.activity_ids.filtered(lambda a: "Restore test overdue" in (a.summary or ""))
    assert len(todo) == 1 and todo.user_id == m6.tech
    Plan.cron_restore_test_due()
    assert (
        len(plan.activity_ids.filtered(lambda a: "Restore test overdue" in (a.summary or ""))) == 1
    )
    assert not plan.compliant
    evidence = (
        m6.env["ir.attachment"]
        .with_user(m6.tech)
        .create({"name": "restore-report.pdf", "raw": b"%PDF restore ok"})
    )
    plan.with_user(m6.tech).action_log_test(result="passed", evidence_attachment_id=evidence.id)
    assert plan.compliant and plan.next_test_due == fields.Date.context_today(plan) + timedelta(
        days=30
    )


def test_b4_a_case_handed_over_before_the_clock_gets_a_retention_date(m6):
    case = m6.handed_over(m6.new_case())
    case._guarded().write({"retention_until": False, "handover_at": False})
    m6.env[CASE].cron_retention_purge()
    assert case.retention_until and not case.retention_flagged_at
