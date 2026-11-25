# ruff: noqa: F811 (the m6 fixture is imported, and named as test parameters)
"""A02 ERP audit pass 2 (20 Nov 2026) - M06 Data Services, findings
M06-01..M06-07, M06-09, M06-11 and M06-12.

Every control runs as non-admin users holding only the M06 roles they need
(the ``m6`` fixture of the P1/P2 suite). ``odoo_env`` rolls back.
"""

from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_data_case.tests.test_a02_p1p2_cd_data_case import (  # noqa: F401
    CASE,
    m6,
)
from odoo.exceptions import AccessError, UserError

from .test_a02_erp_b1_m06 import _cert, _request

CERT = "fix.data.wipe.certificate"


def _ready_for_handover(m6):
    case = m6.recovered(m6.new_case())
    target = "TGT-R2-%d" % case.id
    case.write({"handover_recipient_id": m6.contact.id, "encrypted_target_serial": target})
    case.action_confirm_target_serial(target)
    m6.receipt(case)
    return case


# ===================================================== M06-01 the customer
def test_m06_01_the_customer_is_frozen_after_custody(m6):
    case = m6.new_case()
    other = m6.env["res.partner"].create({"name": "R2 Other %d" % case.id})
    case.write({"customer_id": other.id})  # before custody: a typo is fixed
    case.write({"customer_id": m6.customer.id})
    m6.custody(case)
    with pytest.raises(UserError, match="Correct Customer"):
        case.write({"customer_id": other.id})
    res = m6.p03_write(m6.tech, CASE, case, {"customer_id": other.id})
    assert "error" in res
    assert case.customer_id == m6.customer


def test_m06_01_a_lab_manager_corrects_it_on_the_ledger(m6):
    case = m6.new_case()
    m6.custody(case)
    other = m6.env["res.partner"].create({"name": "R2 Right Owner %d" % case.id})
    with pytest.raises(AccessError):
        case.action_correct_customer(other.id, "the desk typed the wrong customer")
    with pytest.raises(UserError, match="why"):
        case.with_user(m6.manager2).action_correct_customer(other.id, "typo")
    case.with_user(m6.manager2).action_correct_customer(
        other.id, "the desk typed the wrong customer"
    )
    assert case.customer_id == other
    event = case.sudo().custody_event_ids.filtered(lambda e: e.action == "customer_corrected")
    assert event.actor_id == m6.manager2 and "wrong customer" in event.description


def test_m06_01_data_goes_only_to_the_customer_of_the_accepted_quote(m6):
    case = _ready_for_handover(m6)
    stranger = m6.env["res.partner"].create({"name": "R2 Stranger %d" % case.id})
    courier = m6.env["res.partner"].create({"name": "courier", "parent_id": stranger.id})
    # the customer swapped behind the lab's back (a forged write)
    case.sudo()._guarded().write({"customer_id": stranger.id, "handover_recipient_id": courier.id})
    with pytest.raises(UserError, match="accepted quotation"):
        case._handover_recipient_check()
    m6.settle(case)
    with pytest.raises(UserError, match="accepted quotation"):
        case.action_handover(verification="00000000")
    assert case.state == "recovered"


# ===================================================== M06-02 scope + read log
def test_m06_02_an_operator_sees_only_his_cases_and_reads_are_logged(m6):
    staffed = m6.new_case()
    queue = m6.new_case(serial="WD-Q-%d" % m6.n, staffed=False)
    Case = m6.env[CASE].with_user(m6.tech2)
    visible = Case.search([("id", "in", (staffed | queue).ids)])
    assert visible == queue.with_user(m6.tech2)
    with pytest.raises(AccessError):
        staffed.with_user(m6.tech2).read(["customer_id"])
    # the lab manager sees every case
    assert m6.env[CASE].with_user(m6.manager).search_count([("id", "=", staffed.id)]) == 1
    staffed.with_user(m6.tech).read(["customer_id"])
    staffed.with_user(m6.tech).read(["name"])  # within ten minutes: one row
    logs = m6.env["fix.data.case.read.log"].sudo().search([("case_id", "=", staffed.id)])
    assert logs.mapped("user_id") == m6.tech and len(logs) == 1
    with pytest.raises(UserError):
        logs.write({"user_id": m6.tech2.id})


# ===================================================== M06-03 custody
def test_m06_03_custody_starts_on_sealed_media_and_two_people(m6):
    case = m6.new_case()
    with pytest.raises(UserError, match="sealed evidence bag"):
        case.with_user(m6.custodian).action_take_custody(m6.tech.login)
    m6.env["fix.data.media.unit"].with_user(m6.tech).create(
        {"case_id": case.id, "seal_number": "R2-SEAL-%d" % case.id}
    )
    with pytest.raises(UserError, match="receives it"):
        case.with_user(m6.custodian).action_take_custody("")
    with pytest.raises(UserError, match="another person"):
        case.with_user(m6.custodian).action_take_custody(m6.custodian.login)
    case.with_user(m6.custodian).action_take_custody(m6.tech.login)
    assert case.state == "new" and case.custody_request_to_id == m6.tech
    with pytest.raises(AccessError, match="named receiver"):
        case.with_user(m6.custodian).action_confirm_custody()
    case.with_user(m6.tech).action_confirm_custody()
    assert case.state == "custody" and not case.custody_request_kind
    taken = case.sudo().custody_event_ids.filtered(lambda e: e.action == "custody_taken")
    assert (taken.actor_id, taken.witness_id) == (m6.tech, m6.custodian)


def test_m06_03_a_secure_area_move_is_confirmed_by_the_receiver(m6):
    case = m6.custody(m6.new_case())
    unit = case.media_unit_ids.with_user(m6.tech)
    unit.action_transfer("vault", handler=m6.custodian.login)
    assert unit.location == "reception" and unit.pending_location == "vault"
    with pytest.raises(AccessError, match="named receiver"):
        unit.action_confirm_move()
    unit.with_user(m6.custodian).action_confirm_move()
    assert unit.location == "vault" and not unit.pending_kind
    moved = case.sudo().custody_event_ids.filtered(lambda e: e.action == "media_moved")
    assert (moved.actor_id, moved.witness_id) == (m6.custodian, m6.tech)


# ===================================================== M06-04 purge after hand-over
def test_m06_04_a_purge_certificate_from_before_the_hand_over_proves_nothing(m6):
    case = _ready_for_handover(m6)
    early = m6.purge_cert(case)
    m6.settle(case)
    case.action_handover(verification=m6.code_for(case)["code"])
    case.sudo()._guarded().write({"handover_at": fields.Datetime.now() + timedelta(seconds=5)})
    with pytest.raises(UserError, match="before the hand-over"):
        case.action_purge(early)
    assert case.state == "handover"


# ===================================================== M06-05 consumer binding
def test_m06_05_a_certificate_is_tied_to_the_record_that_consumes_it(m6):
    consumer = m6.new_case(serial="WD-CONS-%d" % m6.n)
    serial = "SN-R2-%d" % m6.n
    req = _request(m6, serial)
    req.sudo().write({"source_ref": consumer.name})
    # A02 pass 2 review (D16): at release the matrix judges the method (a
    # Clear of high-confidentiality media is refused); Purge passes it
    cert = _cert(m6, serial, method="nist_800_88_purge", request=req)
    assert cert._fix_certify_denial(serial) == ""  # the old call still works
    later = cert.verified_at + timedelta(days=1)
    assert "earlier cycle" in cert._fix_certify_denial(serial, consumer=consumer, since=later)
    other = m6.new_case(serial="WD-OTH-%d" % m6.n)
    assert "no wipe request raised for" in cert._fix_certify_denial(
        serial, consumer=other, since=cert.verified_at - timedelta(days=1)
    )
    assert (
        cert._fix_certify_denial(
            serial, consumer=consumer, since=cert.verified_at - timedelta(days=1)
        )
        == ""
    )


# ===================================================== M06-06 media out, paid
def test_m06_06_media_goes_back_only_once_the_fee_is_settled(m6):
    case = m6.recovering(m6.new_case())
    case.quote_ids.filtered(lambda q: q.state == "accepted")._guarded().write(
        {"no_data_no_fee_applies": False}
    )
    case._guarded().write({"state": "unrecoverable"})
    unit = case.media_unit_ids.with_user(m6.tech)
    with pytest.raises(UserError, match="billable"):
        unit.action_return(handler=m6.custodian.login)
    with pytest.raises(UserError, match="billable"):
        case.action_close()
    case.with_user(m6.manager2).action_waive_charge(note="no data, goodwill waiver of the fee")
    unit.action_return(handler=m6.custodian.login)
    unit.with_user(m6.custodian).action_confirm_move()
    case.action_close()
    assert case.state == "closed"


# ===================================================== M06-07 waiver cancels
def test_m06_07_a_waiver_cancels_the_unpaid_invoice(m6):
    if "fix.data.case.billing" not in m6.env:
        pytest.skip("M20 billing (cd_settlement_ext) is not installed")
    case = m6.recovered(m6.new_case())
    m6.env["fix.data.case.billing"].sudo()._bill_case(
        {"aggregate_id": case.id, "payload": {"case": case.name}}, "recovered"
    )
    invoice = case._data_invoice()
    assert invoice and invoice.state == "draft"
    case.with_user(m6.manager2).action_waive_charge(note="lab error, goodwill waiver")
    assert invoice.state == "cancelled"


# ===================================================== M06-09 the matrix
def test_m06_09_the_matrix_refuses_a_clear_of_resale_media(m6):
    serial = "SN-MX-%d" % m6.n
    req = _request(m6, serial, source="m14_refurbishment")
    req.sudo().write({"disposition": "resale", "confidentiality_level": "moderate"})
    log = m6.env["ir.attachment"].with_user(m6.tech).create({"name": "w.log", "raw": b"x"})
    vals = {
        "serial_number": serial,
        "sector_count": 1000,
        "wipe_log_attachment_id": log.id,
        "wipe_request_id": req.id,
        "media_kind": "flash",
    }
    with pytest.raises(UserError, match="does not allow"), m6.env.cr.savepoint():
        m6.env[CERT].with_user(m6.tech).create(dict(vals, method="nist_800_88"))
    cert = m6.env[CERT].with_user(m6.tech).create(dict(vals, method="cryptographic_erase"))
    assert cert.standard_ref.startswith("NIST SP 800-88")
    rule = m6.env.ref("cd_data_case.sanitisation_flash_resale")
    with pytest.raises(AccessError, match="Quality Manager"):
        rule.with_user(m6.tech).write({"allow_clear": True})


def test_m06_09_a_destruction_is_witnessed(m6):
    serial = "SN-DW-%d" % m6.n
    cert = _cert(m6, serial, method="physical_destruction", verify=False)
    cert.sudo()._guarded().write({"destruction_witness_id": False})
    with pytest.raises(UserError, match="witnessed"):
        cert.with_user(m6.verifier).action_verify()
    with pytest.raises(UserError, match="not the person"):
        cert.with_user(m6.tech).action_witness_destruction()
    cert.with_user(m6.tech2).action_witness_destruction()
    cert.with_user(m6.verifier).action_verify()
    assert cert.sanitization_status == "verified"


# ===================================================== M06-11 auto purge
def test_m06_11_automatic_purge_is_on_and_overdue_cases_escalate(m6):
    m6.env["ir.config_parameter"].sudo().search(
        [("key", "=", "cd_data_case.retention_auto_purge")]
    ).unlink()
    case = m6.handed_over(m6.new_case())
    m6.purge_cert(case)
    case._guarded().write({"retention_until": fields.Date.today() - timedelta(days=1)})
    m6.env[CASE].cron_retention_purge()
    assert case.state == "purged"
    # without a purge certificate: flagged, then escalated to the lab managers
    late = m6.handed_over(m6.new_case(serial="WD-LATE-%d" % m6.n))
    late._guarded().write(
        {
            "retention_until": fields.Date.today() - timedelta(days=10),
            "retention_flagged_at": fields.Datetime.now() - timedelta(days=5),
        }
    )
    m6.env[CASE].cron_retention_purge()
    assert late.state == "handover" and late.purge_escalated_at
    assert m6.manager in late.sudo().activity_ids.mapped("user_id")


# ===================================================== M06-12 the certificate
def test_m06_12_certificate_stamps_and_frozen_device(m6):
    plain = (
        m6.env["res.users"]
        .with_context(no_reset_password=True)
        .create({"name": "R2 plain %d" % m6.n, "login": "r2.plain.%d@a02.test" % m6.n})
    )
    with pytest.raises(AccessError):
        m6.env[CERT].with_user(plain).create({"method": "nist_800_88", "serial_number": "X"})
    log = m6.env["ir.attachment"].with_user(m6.tech).create({"name": "w.log", "raw": b"y"})
    cert = (
        m6.env[CERT]
        .with_user(m6.tech)
        .create(
            {
                "method": "nist_800_88",
                "serial_number": "SN-CB-%d" % m6.n,
                "sector_count": 10,
                "wipe_log_attachment_id": log.id,
                "certified_by": "Somebody Else",
            }
        )
    )
    assert cert.certified_by == m6.tech.name
    with pytest.raises(UserError):
        cert.with_user(m6.tech).write({"certified_by": "Somebody Else"})
    cert.with_user(m6.verifier).action_verify()
    device = m6.env["fix.device"].search([], limit=1)
    if device:
        with pytest.raises(UserError, match="decided"):
            cert.with_user(m6.tech).write({"device_id": device.id})


# ===================================================== M06-08 report fences
def test_m06_08_report_packs_are_fenced_to_the_company_and_role(m6):
    from odoo.addons.cd_p03_portal.controllers.a02 import m06 as ctrl

    case = m6.handed_over(m6.new_case())
    case.action_purge(m6.purge_cert(case))
    other = m6.env["res.company"].create({"name": "R2 Other Co %d" % m6.n})
    foreign = m6.handed_over(m6.new_case(serial="WD-FOR-%d" % m6.n))
    foreign.action_purge(m6.purge_cert(foreign))
    foreign.sudo().write({"company_id": other.id})
    reader = m6.env(user=m6.tech.id)
    names = [r["case"] for r in ctrl._destruction_audit(reader)["rows"]]
    assert case.name in names and foreign.name not in names
    plain = (
        m6.env["res.users"]
        .with_context(no_reset_password=True)
        .create({"name": "R2 plain rpt %d" % m6.n, "login": "r2.plainrpt.%d@a02.test" % m6.n})
    )
    for report in (ctrl._case_cycle_time, ctrl._backup_compliance, ctrl._destruction_audit):
        with pytest.raises(AccessError):
            report(m6.env(user=plain.id))


# ===================================================== M06-10 printables
def test_m06_10_the_case_file_and_quotation_print(m6):
    case = m6.custody(m6.new_case())
    m6.evaluate(case)
    quote = m6.quote(case)
    report = m6.env["report.cd_p03_portal.report_a02_data_case"]
    payload = report._payload(case.sudo())
    custody = payload["tables"][0]
    assert custody["title"] == "Chain of custody"
    assert [r[2] for r in custody["rows"]][-1] == "Custody Taken"
    assert {b["title"] for b in payload["blocks"]} == {"Intake receipt", "Hand-over receipt"}
    qp = m6.env["report.cd_p03_portal.report_a02_data_quote"]._payload(quote.sudo())
    assert qp["bill_to"]["name"] == m6.customer.name
