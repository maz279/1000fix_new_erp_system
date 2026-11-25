# ruff: noqa: F811 (the m6 fixture is imported, and named as test parameters)
"""A02 ERP audit (2026-11-19), builder stream B1, M06 Data Services.

Each finding is tested both ways (the bypass is refused, the legitimate path
works), as non-admin users holding only the M06 roles they need. The M20
billing consumer itself is tested in cd_settlement_ext
(test_a02_erp_b1_data_billing.py).

``odoo_env`` (addons/conftest.py): rolled back after every test.
"""

import pytest
from odoo.addons.cd_data_case.tests.test_a02_p1p2_cd_data_case import (  # noqa: F401
    CASE,
    QUOTE,
    m6,
)
from odoo.addons.cd_p03_portal.controllers.a02 import m06 as m06_ctrl
from odoo.exceptions import AccessError, UserError

CERT = "fix.data.wipe.certificate"


def _log(m6, text):
    return m6.env["ir.attachment"].with_user(m6.tech).create({"name": "wipe.log", "raw": text})


def _cert(m6, serial, method="nist_800_88", request=None, verify=True):
    cert = (
        m6.env[CERT]
        .with_user(m6.tech)
        .create(
            {
                "method": method,
                "sector_count": 0 if method == "physical_destruction" else 1000,
                "serial_number": serial,
                "wipe_log_attachment_id": _log(
                    m6, b"evidence %s %s" % (serial.encode(), method.encode())
                ).id,
                "wipe_request_id": request.id if request else False,
            }
        )
    )
    if method == "physical_destruction":
        # A02 pass 2 M06-09 (D16): a destruction is photographed and witnessed
        photo = (
            m6.env["ir.attachment"]
            .with_user(m6.tech)
            .create({"name": "shredded.jpg", "raw": b"photo of the shredded platters"})
        )
        cert.with_user(m6.tech).write({"destruction_photo_attachment_id": photo.id})
        cert.with_user(m6.tech2).action_witness_destruction()
    if verify:
        cert.with_user(m6.verifier).action_verify()
    return cert


def _request(m6, serial, source="customer"):
    return (
        m6.env["fix.data.wipe.request"]
        .with_user(m6.tech)
        .create(
            {
                "source": source,
                "serial_number": serial,
                "confidentiality_level": "high",
                "disposition": "recycling",
                "customer_id": m6.customer.id,
            }
        )
    )


def _waive(m6, case):
    case.with_user(m6.manager2).action_waive_charge(note="goodwill: lab re-work of our own failure")


# ===================================================== M06-F1 settlement gate


def _ready_for_handover(m6):
    case = m6.recovered(m6.new_case())
    target = "TGT-B1-%d" % case.id
    case.write({"handover_recipient_id": m6.contact.id, "encrypted_target_serial": target})
    case.action_confirm_target_serial(target)
    m6.receipt(case)
    return case


def test_f1_recovered_data_is_not_handed_over_unpaid(m6):
    case = _ready_for_handover(m6)
    code = m6.code_for(case)["code"]
    with pytest.raises(UserError, match="cannot be handed over: BDT 15000.00 is billable"):
        case.action_handover(verification=code)
    assert case.state == "recovered"
    # the case's own staff cannot waive it, nor approve credit
    with pytest.raises(AccessError):
        case.action_waive_charge(note="goodwill: lab re-work of our own failure")
    with pytest.raises(AccessError, match="finance decision"):
        case.with_user(m6.manager2).action_approve_credit(note="customer pays on account")
    with pytest.raises(UserError, match="reason"):
        case.with_user(m6.manager2).action_waive_charge(note="ok")
    _waive(m6, case)
    assert case.settlement_exception == "charge_waived"
    assert case.settlement_exception_by_id == m6.manager2
    case.action_handover(verification=code)
    assert case.state == "handover"


def test_f1_an_assigned_lab_manager_cannot_waive_their_own_case(m6):
    case = _ready_for_handover(m6)
    m6.undertake(case, m6.manager)
    case._guarded().write({"z4_custodian_id": m6.manager.id})
    with pytest.raises(UserError, match="Segregation of duties"):
        case.with_user(m6.manager).action_waive_charge(note="goodwill for a long-standing client")


def test_f1_finance_approves_a_handover_on_credit(m6):
    case = _ready_for_handover(m6)
    finance = (
        m6.env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "B1 Finance %d" % case.id,
                "login": "b1.fin.%d@a02.test" % case.id,
                "group_ids": [
                    (
                        6,
                        0,
                        [
                            m6.env.ref("base.group_user").id,
                            m6.env.ref("account.group_account_manager").id,
                        ],
                    )
                ],
            }
        )
    )
    case.with_user(finance).action_approve_credit(note="corporate client, net-30 account")
    assert case.settlement_exception == "credit_approved"
    case.action_handover(verification=m6.code_for(case)["code"])
    assert case.state == "handover"


def test_f1_nothing_billable_hands_over_and_unrecoverable_is_published(m6):
    case = m6.new_case()
    m6.custody(case)
    case.action_route_to_z4()
    m6.evaluate(case)
    q = m6.quote(case, amount=0)
    q.action_send()
    q.action_accept(acceptance_reference="OTP-000777")
    assert case._data_billable()[1] == []  # undecided: nothing billed yet
    case.action_start_recovery()
    m6.env["fix.data.recovery.attempt"].with_user(m6.tech).create(
        {"case_id": case.id, "method": "software_scan"}
    ).action_finish(outcome="failed")
    case.action_mark_unrecoverable(reason="platters scored")
    events = m6.env["fix.event.outbox"].search(
        [("event_type", "=", "data_case.unrecoverable"), ("aggregate_id", "=", case.id)]
    )
    assert len(events) == 1


def test_f1_billable_follows_outcome_and_no_data_no_fee(m6):
    case = m6.recovered(m6.new_case())
    quote, lines, outcome = case._data_billable()
    assert outcome == "recovered" and [a for _d, a in lines] == [15000.0]
    quote._guarded().write({"donor_fee_bdt": 4000.0})
    assert [a for _d, a in case._data_billable()[1]] == [15000.0, 4000.0]
    case._guarded().write({"state": "unrecoverable"})
    # unrecoverable under no-data-no-fee: only the non-refundable donor fee
    assert [a for _d, a in case._data_billable()[1]] == [4000.0]
    quote._guarded().write({"no_data_no_fee_applies": False})
    assert [a for _d, a in case._data_billable()[1]] == [15000.0, 4000.0]


# ===================================================== M06-F5 one live quote


def test_f5_a_fresh_quote_cannot_bypass_the_requote(m6):
    case = m6.new_case()
    m6.custody(case)
    m6.evaluate(case)
    first = m6.quote(case, amount=15000)
    first.action_send()
    with pytest.raises(UserError, match="already has a live quotation"):
        m6.quote(case, amount=95000, no_data_no_fee_applies=False)
    out = first.action_requote()
    new = m6.env[QUOTE].browse(out["quote_ids"])
    assert new.supersedes_id == first and first.state == "superseded"
    # declined: a new quote may follow
    new.with_user(m6.tech).action_decline()
    fresh = m6.quote(case, amount=12000)
    assert fresh.state == "draft"


def test_f5_no_quote_past_custody(m6):
    case = m6.recovering(m6.new_case())
    case.quote_ids._guarded().write({"state": "declined"})
    with pytest.raises(UserError, match="past quotation"):
        m6.quote(case, amount=1000)


# ===================================================== M06-F6 / F7 certificates


def test_f6_after_a_failed_erasure_only_physical_destruction_certifies(m6):
    serial = "SN-F6-%d" % m6.n
    req = _request(m6, serial)
    failed = _cert(m6, serial, request=req, verify=False)
    failed.with_user(m6.verifier).action_mark_failed()
    assert req.state == "physical_required"
    # the bypass: a fresh request-less erasure certificate
    with pytest.raises(UserError, match="BRU-DTS-10"):
        _cert(m6, serial, verify=False)
    destroyed = _cert(m6, serial, method="physical_destruction")
    assert destroyed._fix_certifies(serial)


def test_f6_an_erasure_recorded_before_the_failure_no_longer_certifies(m6):
    serial = "SN-F6B-%d" % m6.n
    first = _cert(m6, serial, verify=False)
    second = _cert(m6, serial, verify=False)
    first.with_user(m6.verifier).action_mark_failed()
    second.with_user(m6.verifier).action_verify()
    assert "BRU-DTS-10" in second._fix_certify_denial(serial)


def test_f7_a_linked_certificate_serial_cannot_be_retyped(m6):
    serial = "SN-F7-%d" % m6.n
    req = _request(m6, serial)
    cert = _cert(m6, serial, request=req, verify=False)
    with pytest.raises(UserError, match="answers request"):
        cert.with_user(m6.tech).write({"serial_number": "OTHER-%d" % m6.n})
    cert.with_user(m6.tech).write({"serial_number": " %s " % serial.lower()})  # same media


def test_f22_failing_a_certificate_needs_the_role(m6):
    cert = _cert(m6, "SN-F22-%d" % m6.n, verify=False)
    with pytest.raises(AccessError, match="Verifier"):
        cert.with_user(m6.tech2).action_mark_failed()
    cert.with_user(m6.tech).action_mark_failed()  # the operator who recorded it
    assert cert.sanitization_status == "failed"
    with pytest.raises(UserError, match="awaiting verification"):
        cert.with_user(m6.verifier).action_mark_failed()


# ===================================================== M06-F9 / F10 media


def _unit(m6, case, seal=None):
    return (
        m6.env["fix.data.media.unit"]
        .with_user(m6.tech)
        .create({"case_id": case.id, "seal_number": seal or "BAG-%d-%d" % (m6.n, case.id)})
    )


def test_f10_media_is_returned_only_at_the_end_and_to_the_customer(m6):
    case = m6.recovering(m6.new_case())
    unit = _unit(m6, case)
    with pytest.raises(UserError, match="stays in custody"):
        unit.with_user(m6.tech).action_return(handler=m6.tech2.login)
    case._guarded().write({"state": "unrecoverable"})
    stranger = m6.env["res.partner"].create({"name": "Not the customer %d" % m6.n})
    with pytest.raises(UserError, match="not the customer"):
        unit.with_user(m6.tech).action_return(handler=m6.tech2.login, recipient=stranger.id)
    with pytest.raises(AccessError):
        unit.with_user(m6.verifier).action_return(handler=m6.tech2.login)
    # A02 pass 2 M06-03: requested by one, confirmed by the second person
    unit.with_user(m6.tech).action_return(handler=m6.tech2.login, recipient=m6.contact.id)
    unit.with_user(m6.tech2).action_confirm_move()
    assert unit.location == "returned_to_customer" and unit.returned_to_id == m6.contact


def test_f9_a_purged_case_closes_only_once_its_media_left_the_lab(m6):
    case = _ready_for_handover(m6)
    _waive(m6, case)
    case.action_handover(verification=m6.code_for(case)["code"])
    unit = case.media_unit_ids[:1]  # the sealed bag custody was taken on (A02 pass 2)
    serial = case.media_serial_number
    req = _request(m6, serial)
    cert = _cert(m6, serial, method="physical_destruction", request=req)
    # A02 pass 2 M06-04: the purge is the lab's own purge certificate
    case.action_purge(m6.purge_cert(case))
    with pytest.raises(UserError, match="return the customer's media first"):
        case.action_close()
    # an erasure certificate does not destroy the drive
    other = _unit(m6, case, seal="BAG-ERASE-%d" % m6.n)
    with pytest.raises(UserError):
        other.with_user(m6.tech).action_destroy(_cert(m6, serial + "-X"))
    unit.with_user(m6.tech).action_destroy(cert.name)
    assert unit.location == "destroyed" and unit.destruction_certificate_id == cert
    with pytest.raises(UserError, match="already destroyed another unit"):
        other.with_user(m6.tech).action_destroy(cert.id)
    other.with_user(m6.tech).action_return(handler=m6.tech2.login)
    other.with_user(m6.tech2).action_confirm_move()
    case.action_close()
    assert case.state == "closed"


def test_f9_destruction_needs_the_customers_request(m6):
    case = _ready_for_handover(m6)
    _waive(m6, case)
    case.action_handover(verification=m6.code_for(case)["code"])
    unit = _unit(m6, case)
    cert = _cert(m6, case.media_serial_number, method="physical_destruction")
    with pytest.raises(UserError, match="no destruction request from the customer"):
        unit.with_user(m6.tech).action_destroy(cert.id)


# ===================================================== M06-F11 witness


def test_f11_the_witness_confirms_the_seal_break_in_their_own_session(m6):
    case = m6.new_case()
    unit = _unit(m6, case)
    unit.with_user(m6.tech).action_break_seal_with_witness(witness_user_id=m6.tech2.id)
    assert unit.seal_state == "sealed" and unit.seal_break_witness_id == m6.tech2
    with pytest.raises(AccessError, match="named witness"):
        unit.with_user(m6.tech).action_confirm_seal_break()
    with pytest.raises(AccessError, match="named witness"):
        unit.with_user(m6.custodian).action_confirm_seal_break()
    unit.with_user(m6.tech2).action_confirm_seal_break()
    assert unit.seal_state == "opened_in_lab" and unit.witness_user_id == m6.tech2
    event = case.custody_event_ids.filtered(lambda e: e.action == "seal_broken")
    assert event.actor_id == m6.tech2 and event.witness_id == m6.tech2
    assert not unit.seal_break_witness_id


# ===================================================== M06-F12 image hash


def test_f12_the_verifier_does_not_see_the_hash_they_must_recompute(m6):
    case = m6.recovering(m6.new_case())
    case.action_record_image(source_hash=m6.digest, image_hash=m6.digest)
    seen = case.with_user(m6.custodian).read(
        ["image_sha256_hash", "image_source_sha256", "custody_chain"]
    )[0]
    assert not seen["image_sha256_hash"] and not seen["image_source_sha256"]
    assert m6.digest not in (seen["custody_chain"] or "")
    with pytest.raises(UserError, match="does not match"):
        case.with_user(m6.custodian).action_verify_image(recomputed_hash="e" * 64)
    case.with_user(m6.custodian).action_verify_image(recomputed_hash=m6.digest)
    assert case.image_sha256_hash == m6.digest and case.image_source_sha256 == m6.digest
    assert case.image_matches_source


# ===================================================== M06-F13 undertaking file


def test_f13_the_undertaking_file_is_a_signed_upload_for_it(m6):
    case = m6.new_case(staffed=False)
    Undertaking = m6.env["fix.data.confidentiality.undertaking"].with_user(m6.tech)
    Att = m6.env["ir.attachment"].with_user(m6.tech)
    other_doc = Att.create(
        {"name": "nda.pdf", "raw": b"%PDF", "res_model": CASE, "res_id": case.id}
    )
    empty = Att.create({"name": "blank.pdf", "raw": b""})
    base = {"case_id": case.id, "undertaking_type": "staff", "user_id": m6.tech2.id}
    with pytest.raises(UserError, match="another record"):
        Undertaking.create(dict(base, document_attachment_id=other_doc.id))
    with pytest.raises(UserError, match="empty"):
        Undertaking.create(dict(base, document_attachment_id=empty.id))
    upload = Att.create({"name": "undertaking-signed.pdf", "raw": b"%PDF signed"})
    rec = Undertaking.create(dict(base, document_attachment_id=upload.id))
    assert (upload.res_model, upload.res_id) == (rec._name, rec.id)
    assert rec.signature_method == "signed_form"


# ===================================================== M06-F16/F17/F20 KPIs


def test_f16_f17_kpis_count_outcomes_and_bill_what_is_owed(m6):
    env = m6.env
    won = _ready_for_handover(m6)
    _waive(m6, won)
    won.action_handover(verification=m6.code_for(won)["code"])  # moved on from 'recovered'
    lost = m6.recovering(m6.new_case(serial="WD-LOST-%d" % m6.n))
    lost.quote_ids.filtered(lambda q: q.state == "accepted")._guarded().write(
        {"donor_fee_bdt": 2500.0}
    )
    lost._guarded().write({"state": "unrecoverable"})
    k = m06_ctrl.kpis(env)
    counted = m06_ctrl._outcomes(env[CASE].search([("id", "in", (won | lost).ids)]))
    assert counted == {"recovered": 1, "unrecoverable": 1}
    assert k["recovery_success"] is not None
    report = m06_ctrl._service_revenue(env)
    rows = {r["case"]: r for r in report["rows"]}
    assert rows[won.name]["billable_bdt"] == 15000.0
    # unrecoverable under no-data-no-fee bills only the donor fee
    assert rows[lost.name]["billable_bdt"] == 2500.0
    assert rows[lost.name]["quoted_bdt"] == 17500.0


def test_f20_destruction_kpi_counts_this_companys_verified_certificates(m6):
    env = m6.env
    reader = env(user=m6.verifier.id)
    before = m06_ctrl.kpis(reader)["destruction_certs_mtd"]
    _cert(m6, "SN-F20A-%d" % m6.n, verify=False)  # pending: not a certificate yet
    _cert(m6, "SN-F20B-%d" % m6.n)
    other = env["res.company"].create({"name": "B1 Other Co %d" % m6.n})
    foreign = _cert(m6, "SN-F20C-%d" % m6.n)
    foreign.sudo().write({"company_id": other.id})
    assert m06_ctrl.kpis(reader)["destruction_certs_mtd"] == before + 1
