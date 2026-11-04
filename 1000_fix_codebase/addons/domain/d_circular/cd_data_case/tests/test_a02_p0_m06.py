"""A02 workflow audit, P0 for M06 Data Services & Recovery (M06-1..M06-11).

Every GAP probe of working/A02_evidence/probes/m05_m06/probe_m06.py is a
control here, tested both ways: the bypass is refused and the legitimate
path still works. Everyone acts as a NON-ADMIN user created in the test,
because the superuser is trusted by the guards and would hide a gap. The
key forgeries also go through the P03 endpoints (/p03/model/write, /action,
/records, /report), the path the audit used.
"""

from __future__ import annotations

import itertools
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest import mock

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.exceptions import AccessError, UserError, ValidationError
from psycopg2 import IntegrityError

REFUSALS = (UserError, AccessError, ValidationError)
GUARD = "changes only through its workflow"
CASE = "fix.data.recovery.case"
CERT = "fix.data.wipe.certificate"
_SEQ = itertools.count(1)


class _FakeRequest:
    def __init__(self, env):
        self.env = env


@pytest.fixture
def m6(odoo_env):
    env = odoo_env
    n = next(_SEQ)
    group = env.ref
    base = group("base.group_user")
    operator = group("cd_data_case.group_data_recovery_operator")
    verifier_group = group("cd_data_case.group_wipe_verifier")
    custodian = group("cd_data_case.group_z4_custodian")
    Users = env["res.users"].with_context(no_reset_password=True)

    def user(name, *groups):
        return Users.create(
            {
                "name": "A02 M06 %s %d" % (name, n),
                "login": "a02.p0.m06.%s.%d@a02.test" % (name.lower().replace(" ", "."), n),
                "group_ids": [(6, 0, [base.id, *[g.id for g in groups]])],
            }
        )

    tech = user("Tech", operator)
    tech2 = user("Second Tech", operator)
    verifier = user("Verifier", verifier_group)
    clerk = user("Front Desk")
    custodian_user = user("Custodian", custodian)
    assert not tech.has_group("base.group_system")
    customer = env["res.partner"].create(
        {"name": "A02 M06 Customer %d" % n, "phone": "01711000333"}
    )
    image_hash = "%064x" % (0xA02 * n)

    patchers = []

    def call(user, route, **kw):
        p = mock.patch.object(api, "request", _FakeRequest(env(user=user.id)))
        p.start()
        patchers.append(p)
        try:
            return getattr(api.P03GenericApiController(), route)(**kw)
        finally:
            p.stop()
            patchers.remove(p)

    def p03_write(user, model, rec, values):
        return call(user, "model_write", model=model, record_id=rec.id, values=values)

    def p03_action(user, model, rec, method, kwargs=None):
        return call(user, "model_action", model=model, ids=rec.ids, method=method, kwargs=kwargs)

    def evaluate(case, verdict="recoverable"):
        env["fix.data.evaluation"].with_user(tech).create(
            {"case_id": case.id, "verdict": verdict}
        ).action_complete()

    def new_case(serial="WD-CASE-%d" % n, staffed=True, evaluated=False, **vals):
        vals = {
            "customer_id": customer.id,
            "media_type": "hdd",
            "media_serial_number": serial,
            **vals,
        }
        case = env[CASE].with_user(tech).create(vals)
        if staffed:
            # A02 audit M06-P2: Z4 work is for the case's named staff
            case.action_assign_staff(technician=tech, custodian=custodian_user)
        if evaluated:
            evaluate(case)
        return case

    def accept_quote(case, amount=15000):
        if not case.evaluation_ids.filtered("evaluated_at"):
            evaluate(case)
        quote = env["fix.data.quote"].with_user(tech).create({"case_id": case.id, "amount": amount})
        quote.action_send()
        quote.action_accept(acceptance_reference="OTP-%06d" % (n * 7))
        return quote

    def to_recovering(case):
        case = case.with_user(tech)
        case.action_take_custody("tech")
        case.action_route_to_z4()
        evaluate(case)
        accept_quote(case)
        case.action_start_recovery()
        return case

    def image(case, by=None, verifier=None):
        case.with_user(by or tech).action_record_image(
            source_hash=image_hash, image_hash=image_hash
        )
        case.with_user(verifier or tech2).action_verify_image(recomputed_hash=image_hash)

    def handover_code(case):
        """Send the recipient the handover code; return what they received."""
        sent = {}

        def _send(self, recipient, phone, code):
            sent.update(recipient=recipient, code=code)
            return {"destination": "017*****333"}

        with mock.patch.object(type(case), "_handover_send_code", _send):
            case.action_request_handover_otp()
        return sent["code"]

    def ready_for_handover(case, target="TGT-%d" % n):
        case.write({"handover_recipient_id": customer.id, "encrypted_target_serial": target})
        case.action_confirm_target_serial(target)
        env["ir.attachment"].with_user(tech).create(
            {"name": "receipt.pdf", "raw": b"%PDF receipt", "res_model": CASE, "res_id": case.id}
        )

    def to_handover(case):
        case = to_recovering(case)
        env["fix.data.recovery.attempt"].with_user(tech).create(
            {"case_id": case.id, "method": "software_scan"}
        ).action_finish(outcome="success")
        image(case)
        case.action_recovered()
        ready_for_handover(case)
        case.action_handover("tech", verification=handover_code(case))
        return case

    def new_cert(serial, log=b"nwipe: 1953525168 sectors overwritten, PASS", by=None):
        by = by or tech
        att = env["ir.attachment"].with_user(by).create({"name": "wipe.log", "raw": log})
        cert = (
            env[CERT]
            .with_user(by)
            .create(
                {
                    "method": "nist_800_88",
                    "sector_count": 1000,
                    "serial_number": serial,
                    "wipe_log_attachment_id": att.id,
                }
            )
        )
        return cert, att

    def verified_cert(serial, **kw):
        cert, att = new_cert(serial, **kw)
        cert.with_user(verifier).action_verify()
        return cert, att

    def slot(case=None, particles=45):
        return (
            env["fix.data.cleanroom.slot"]
            .with_user(tech)
            .create(
                {
                    "case_id": case.id if case else False,
                    "purpose": "head_swap",
                    "start_at": datetime.now(),
                    "end_at": datetime.now() + timedelta(hours=2),
                    "particle_count_per_ft3": particles,
                }
            )
        )

    yield SimpleNamespace(
        env=env,
        tech=tech,
        tech2=tech2,
        verifier=verifier,
        clerk=clerk,
        custodian=custodian_user,
        customer=customer,
        n=n,
        user=user,
        call=call,
        p03_write=p03_write,
        p03_action=p03_action,
        new_case=new_case,
        evaluate=evaluate,
        image=image,
        image_hash=image_hash,
        handover_code=handover_code,
        ready_for_handover=ready_for_handover,
        accept_quote=accept_quote,
        to_recovering=to_recovering,
        to_handover=to_handover,
        new_cert=new_cert,
        verified_cert=verified_cert,
        slot=slot,
    )
    for p in patchers:
        p.stop()


# ------------------------------------------------------------------ groups


def test_groups_ship_as_decided(m6):
    """A3: the operational role keeps the admin working; the decision roles
    (wipe verifier, Z4 custodian) ship with no holder."""
    env = m6.env
    assert (
        env.ref("base.user_admin") in env.ref("cd_data_case.group_data_recovery_operator").user_ids
    )
    for xmlid in ("cd_data_case.group_wipe_verifier", "cd_data_case.group_z4_custodian"):
        holders = env.ref(xmlid).user_ids - m6.verifier - m6.custodian
        assert not holders, (xmlid, holders.mapped("login"))


def test_a_plain_user_has_no_case_access(m6):
    """Z4 / BRU-DTS-02: case PII is for the data-recovery role (M06-3)."""
    with pytest.raises(AccessError):
        m6.env[CASE].with_user(m6.clerk).create({"customer_id": m6.customer.id})
    case = m6.new_case(nda_reference="NDA-77")
    cols = ["name", "customer_id", "media_serial_number", "image_sha256_hash", "custody_chain"]
    out = m6.call(m6.clerk, "model_records", model=CASE, cols=cols, domain=[("id", "=", case.id)])
    assert out.get("error") and not out.get("rows")
    # the role still reads its cases
    out = m6.call(m6.tech, "model_records", model=CASE, cols=cols, domain=[("id", "=", case.id)])
    assert [r["id"] for r in out["rows"]] == [case.id]


# --------------------------------------------------------------- case state


def test_D1_case_state_cannot_be_forged_to_purged(m6):
    case = m6.new_case()
    case.action_take_custody("tech")
    res = m6.p03_write(m6.tech, CASE, case, {"state": "purged"})
    assert "error" in res
    with pytest.raises(UserError, match=GUARD):
        case.write({"state": "purged"})
    case.invalidate_recordset()
    assert case.state == "custody" and not case.purge_certificate_id


def test_D2_custody_is_taken_once_and_never_after_purge(m6):
    case = m6.to_handover(m6.new_case(serial="WD-D2"))
    cert, _ = m6.verified_cert("WD-D2")
    case.action_purge(certificate=cert)
    assert case.state == "purged"
    with pytest.raises(UserError, match="taken once"):
        case.action_take_custody("someone")
    assert case.state == "purged"
    fresh = m6.new_case(serial="WD-D2-B")
    fresh.action_take_custody("desk")  # legitimate: from new
    assert fresh.state == "custody"


def test_D3_recovered_only_from_recovery_with_a_successful_attempt(m6):
    case = m6.new_case()
    out = m6.p03_action(m6.tech, CASE, case, "action_recovered")
    assert not out["success"] and case.state == "new"
    case = m6.to_recovering(case)
    with pytest.raises(UserError, match="no finished recovery attempt"):
        case.action_recovered()
    attempt = (
        m6.env["fix.data.recovery.attempt"]
        .with_user(m6.tech)
        .create({"case_id": case.id, "method": "software_scan"})
    )
    attempt.action_finish(outcome="partial")
    # A02 audit M06-P2: and from a verified forensic image
    with pytest.raises(UserError, match="verified forensic image"):
        case.action_recovered()
    m6.image(case)
    case.action_recovered()
    assert case.state == "recovered"


def test_D4_recovery_needs_z4_routing_evaluation_and_accepted_quote(m6):
    case = m6.new_case()
    case.action_take_custody("tech")
    # M06-9: the zone is not a label a user types
    res = m6.p03_write(m6.tech, CASE, case, {"residency_zone": "z4"})
    assert "error" in res
    with pytest.raises(UserError, match=GUARD):
        case.write({"residency_zone": "z4"})
    case.action_route_to_z4()
    assert case.residency_zone == "z4"
    out = m6.p03_action(m6.tech, CASE, case, "action_start_recovery")
    assert not out["success"] and "evaluation" in out["error"]
    m6.env["fix.data.evaluation"].with_user(m6.tech).create(
        {"case_id": case.id, "verdict": "partial"}
    ).action_complete()
    with pytest.raises(UserError, match="accepted the quotation"):
        case.action_start_recovery()
    m6.accept_quote(case)
    case.action_start_recovery()
    assert case.state == "recovering"


def test_D5_destructive_attempt_needs_consent_and_a_passing_cleanroom_slot(m6):
    Attempt = m6.env["fix.data.recovery.attempt"].with_user(m6.tech)
    new = m6.new_case()
    with pytest.raises(UserError, match="in recovery"):
        Attempt.create({"case_id": new.id, "method": "chip_off"})  # the probe's NEW case
    case = m6.to_recovering(m6.new_case(serial="WD-D5"))
    savepoint = m6.env.cr.savepoint
    with pytest.raises(UserError, match="consent"), savepoint():
        Attempt.create({"case_id": case.id, "method": "chip_off"})
    # consent needs the customer's artefact
    with pytest.raises(UserError, match="artefact"):
        case.action_record_destructive_consent(reference="ok")
    with pytest.raises(UserError, match=GUARD):
        case.write({"destructive_consent_at": datetime.now()})
    out = m6.p03_action(
        m6.tech, CASE, case, "action_record_destructive_consent", {"reference": "OTP-CONSENT-91"}
    )
    assert out["success"], out
    assert case.destructive_consent_by_id == m6.tech
    with pytest.raises(UserError, match="cleanroom slot"), savepoint():
        Attempt.create({"case_id": case.id, "method": "chip_off"})
    unbooked = m6.slot()
    with pytest.raises(UserError, match="not booked for case"), savepoint():
        Attempt.create({"case_id": case.id, "method": "chip_off", "cleanroom_slot_id": unbooked.id})
    failing = m6.slot(case, particles=5000)
    with pytest.raises(UserError, match="FLAW-06.2 Cleanroom Environmental Interlock"), savepoint():
        Attempt.create(
            {
                "case_id": case.id,
                "method": "chip_off",
                "cleanroom_slot_id": failing.id,
            }
        )
    attempt = Attempt.create(
        {"case_id": case.id, "method": "chip_off", "cleanroom_slot_id": m6.slot(case).id}
    )
    assert attempt.destructive
    attempt.action_finish(outcome="media_damaged")
    assert attempt.outcome == "media_damaged" and attempt.finished_at


def test_D6_custody_chain_is_an_append_only_ledger(m6):
    case = m6.new_case(serial="WD-D6", staffed=False)
    case.action_take_custody("Desk")
    case.action_log_custody_transfer("Nadia", location="Z4 Vault")
    res = m6.p03_write(m6.tech, CASE, case, {"custody_chain": "nothing happened"})
    assert "error" in res
    with pytest.raises(UserError, match=GUARD):
        case.write({"custody_chain": "erased"})
    events = case.custody_event_ids
    assert events.mapped("action") == ["custody_taken", "custody_transfer"]
    assert set(events.mapped("actor_id")) == {m6.tech}
    assert set(events.mapped("media_serial")) == {"WD-D6"}
    assert events[1].prev_hash == events[0].entry_hash
    assert "custody taken by Desk" in case.custody_chain
    with pytest.raises(UserError, match="append-only"):
        events[0].write({"description": "rewritten"})
    with pytest.raises(UserError, match="append-only"):
        events[0].unlink()
    # a row is written only by a custody action, never by hand
    with pytest.raises(UserError, match="only by the custody actions"):
        m6.env["fix.data.custody.event"].with_user(m6.tech).create(
            {"case_id": case.id, "action": "handover", "description": "fake"}
        )
    # the serial the certificate binds to is frozen once custody is taken
    with pytest.raises(UserError, match="media serial"):
        case.write({"media_serial_number": "WD-OTHER"})


def test_H1_unrecoverable_and_closed_are_reachable(m6):
    case = m6.new_case()
    case.action_take_custody("tech")
    with pytest.raises(UserError, match="unrecoverable verdict needs"):
        case.action_mark_unrecoverable()
    with pytest.raises(UserError, match="closes after"):
        case.action_close()
    m6.env["fix.data.evaluation"].with_user(m6.tech).create(
        {"case_id": case.id, "verdict": "unrecoverable"}
    ).action_complete()
    case.action_route_to_z4()
    with pytest.raises(UserError, match="evaluated unrecoverable"):
        case.action_start_recovery()
    out = m6.p03_action(m6.tech, CASE, case, "action_mark_unrecoverable", {"reason": "PCB burnt"})
    assert out["success"], out
    unit = (
        m6.env["fix.data.media.unit"]
        .with_user(m6.tech)
        .create({"case_id": case.id, "seal_number": "SEAL-H1-%d" % m6.n})
    )
    with pytest.raises(UserError, match="return the customer's media"):
        case.action_close()
    unit.action_return()
    case.action_close()
    assert case.state == "closed"


# ------------------------------------------------------------ certificates


def test_W1_W2_certificate_status_cannot_be_forged(m6):
    cert = m6.env[CERT].with_user(m6.tech).create({"method": "nist_800_88"})
    for user in (m6.tech, m6.verifier):
        with pytest.raises(UserError, match=GUARD):
            cert.with_user(user).write({"sanitization_status": "verified"})
        with pytest.raises(UserError, match=GUARD):
            cert.with_user(user).write({"verified_by_id": m6.verifier.id})
    res = m6.p03_write(m6.tech, CERT, cert, {"sanitization_status": "verified"})
    assert "error" in res
    cert.invalidate_recordset()
    assert cert.sanitization_status == "pending_verification"
    # a status forged around the model (the 40 live certificates) certifies nothing
    cert.sudo()._guarded().write({"sanitization_status": "verified"})
    assert "never verified" in cert._fix_certify_denial(cert.serial_number)


def test_W3_the_operator_cannot_verify_his_own_certificate(m6):
    cert, _ = m6.new_cert("WD-W3", log=b"7 bytes")
    out = m6.p03_action(m6.tech, CERT, cert, "action_verify")
    assert not out["success"] and "Wipe Certificate Verifier" in out["error"]
    # holding the verifier role does not let the technician verify his own
    both = m6.user(
        "Tech Verifier",
        m6.env.ref("cd_data_case.group_data_recovery_operator"),
        m6.env.ref("cd_data_case.group_wipe_verifier"),
    )
    own, _ = m6.new_cert("WD-W3-B", by=both)
    with pytest.raises(UserError, match="Segregation of duties"):
        own.with_user(both).action_verify()
    # the legitimate path: a second identity holding the role
    cert.with_user(m6.verifier).action_verify()
    assert (cert.sanitization_status, cert.verified_by_id) == ("verified", m6.verifier)
    assert cert.verified_hash == cert.verification_hash and cert.evidence_intact


def test_W3_verification_without_a_holder_says_so(m6):
    m6.env.ref("cd_data_case.group_wipe_verifier").sudo().write({"user_ids": [(5, 0, 0)]})
    cert, _ = m6.new_cert("WD-W3-C")
    with pytest.raises(AccessError, match="no one holds it yet"):
        cert.with_user(m6.tech2).action_verify()


def test_W4_certificate_binds_one_serial_and_purges_one_case(m6):
    c1 = m6.to_handover(m6.new_case(serial="WD-A-%d" % m6.n))
    c2 = m6.to_handover(m6.new_case(serial="WD-B-%d" % m6.n))
    other, _ = m6.verified_cert("WD-OTHER-9")
    for case in (c1, c2):
        with pytest.raises(UserError, match="certifies media WD-OTHER-9"):
            case.action_purge(certificate=other)
    assert (c1.state, c2.state) == ("handover", "handover")
    # the legitimate UI path: the button passes the reference, or nothing
    own, _ = m6.verified_cert("wd-a-%d" % m6.n)  # labels vary in case
    out = m6.p03_action(m6.tech, CASE, c1, "action_purge", {"certificate": ""})
    assert out["success"], out
    assert (c1.state, c1.purge_certificate_id) == ("purged", own)
    # one certificate purges one case, even of the same serial
    c3 = m6.to_handover(m6.new_case(serial="WD-B-%d" % m6.n))
    for case in (c2, c3):
        with pytest.raises(UserError, match="certifies media|already closed another case"):
            case.action_purge(certificate=own.name)
    b_cert, _ = m6.verified_cert("WD-B-%d" % m6.n)
    out = m6.p03_action(m6.tech, CASE, c2, "action_purge", {"certificate": b_cert.name})
    assert out["success"], out
    with pytest.raises(UserError, match="already closed another case"):
        c3.action_purge(certificate=b_cert)


def test_W5_a_log_changed_after_verification_voids_it(m6):
    case = m6.to_handover(m6.new_case(serial="WD-S-%d" % m6.n))
    cert, att = m6.verified_cert("WD-S-%d" % m6.n)
    assert cert._fix_certifies("WD-S-%d" % m6.n)
    att.with_user(m6.tech).write({"raw": b"wipe FAILED - 12 bad sectors"})
    cert.invalidate_recordset()
    assert not cert.evidence_intact
    with pytest.raises(UserError, match="verification is void"):
        case.action_purge(certificate=cert)
    assert case.state == "handover"


def test_W_external_gates_use_the_serial_binding(m6):
    """M14 trade-in, M18 e-waste and rental call _fix_certifies: a verified
    certificate of another serial releases nothing."""
    env = m6.env
    cert, _ = m6.verified_cert("SN-GATE-%d" % m6.n)
    brand = env["fix.brand"].create({"name": "A02 M06 Brand %d" % m6.n, "code": "A2M6%d" % m6.n})
    model = env["fix.device.model"].create({"name": "Drive", "brand_id": brand.id})
    mine = env["fix.device"].create(
        {"device_model_id": model.id, "serial_number": "SN-GATE-%d" % m6.n}
    )
    theirs = env["fix.device"].create(
        {"device_model_id": model.id, "serial_number": "SN-ELSE-%d" % m6.n}
    )
    gate = env["fix.tradein.request"]._wipe_gate_denial
    assert gate(cert, mine) == ""
    assert "certifies media" in gate(cert, theirs)
    assert "no M06 data wipe certificate" in gate(env[CERT], mine)
    assert not env[CERT]._fix_certifies("SN-GATE-%d" % m6.n)  # no certificate at all


# ------------------------------------------------------------- Z4 controls


def test_Z1_audit_rows_are_written_only_by_the_access_action(m6):
    case = m6.new_case()
    for user in (m6.tech, m6.clerk, m6.custodian):
        with pytest.raises(AccessError):
            m6.env["fix.z4.access.audit"].with_user(user).create(
                {
                    "case_id": case.id,
                    "user_id": m6.clerk.id,
                    "access_type": "file_download",
                    "purpose": "routine",
                    "step_up_verified": True,
                }
            )
    assert not case.audit_ids
    # a row no action wrote never claims a step-up
    row = m6.env["fix.z4.access.audit"].create(
        {"case_id": case.id, "access_type": "metadata_read", "purpose": "QA"}
    )
    assert row.step_up_verified is False


def test_Z2_inventory_report_lists_no_file_names(m6):
    case = m6.to_recovering(m6.new_case())
    m6.env["ir.attachment"].create(
        {"name": "Payroll_2026_salaries.xlsx", "res_model": CASE, "res_id": case.id, "raw": b"x"}
    )
    out = m6.call(m6.clerk, "model_report", module="M06", report="recovered_inventory", params={})
    assert out.get("error") and not out.get("rows")
    out = m6.call(m6.tech, "model_report", module="M06", report="recovered_inventory", params={})
    rows = [r for r in out["rows"] if r["case"] == case.name]
    assert rows and rows[0]["files"] == 1
    assert "Payroll_2026_salaries.xlsx" not in repr(out)
    for report in ("destruction_purge_audit", "data_service_revenue"):
        out = m6.call(m6.clerk, "model_report", module="M06", report=report, params={})
        assert out.get("error"), report


def test_Z3_access_needs_the_custodian_role_then_the_totp(m6):
    case = m6.to_recovering(m6.new_case())
    out = m6.p03_action(
        m6.tech, CASE, case, "action_access_recovered_data", {"step_up_token": "123456"}
    )
    assert not out["success"] and "Z4 Custodian" in out["error"]
    out = m6.p03_action(
        m6.custodian, CASE, case, "action_access_recovered_data", {"step_up_token": "123456"}
    )
    assert not out["success"] and "Access Denied" in out["error"]
    assert not case.audit_ids


# ------------------------------------------------------------------ quotes


def test_Q1_quote_state_cannot_be_forged(m6):
    case = m6.new_case(evaluated=True)
    quote = (
        m6.env["fix.data.quote"].with_user(m6.tech).create({"case_id": case.id, "amount": 15000})
    )
    assert "error" in m6.p03_write(m6.tech, "fix.data.quote", quote, {"state": "accepted"})
    with pytest.raises(UserError, match=GUARD):
        quote.write({"state": "accepted"})
    with pytest.raises(UserError, match=GUARD):
        quote.write({"signed_quote_attachment_id": m6.env["ir.attachment"].search([], limit=1).id})
    assert quote.state == "draft"


def test_Q2_acceptance_needs_the_customers_artefact(m6):
    case = m6.new_case(evaluated=True)
    Quote = m6.env["fix.data.quote"].with_user(m6.tech)
    quote = Quote.create({"case_id": case.id, "amount": 15000})
    quote.action_send()
    out = m6.p03_action(m6.tech, "fix.data.quote", quote, "action_accept")
    assert not out["success"] and "customer" in out["error"]
    with pytest.raises(UserError, match="at least 6"):
        quote.action_accept(acceptance_reference="ok")
    # a customer-signed quotation uploaded to the quote
    m6.env["ir.attachment"].with_user(m6.tech).create(
        {
            "name": "signed.pdf",
            "raw": b"%PDF signed",
            "res_model": "fix.data.quote",
            "res_id": quote.id,
        }
    )
    out = m6.p03_action(
        m6.tech, "fix.data.quote", quote, "action_accept", {"acceptance_reference": ""}
    )
    assert out["success"], out
    assert (quote.state, quote.acceptance_channel) == ("accepted", "signed_document")
    assert quote.signed_quote_attachment_id and quote.accepted_by_id == m6.tech
    # an OTP / portal reference
    otp = Quote.create({"case_id": case.id, "amount": 100})
    otp.action_send()
    otp.action_accept(acceptance_reference="PORTAL-77812")
    assert otp.acceptance_channel == "otp_portal"
    # the business switch: staff may record acceptance when turned off
    m6.env["ir.config_parameter"].sudo().set_param(
        "cd_data_case.quote_acceptance_requires_customer_artefact", "0"
    )
    staff = Quote.create({"case_id": case.id, "amount": 100})
    staff.action_send()
    staff.action_accept()
    assert staff.acceptance_channel == "staff_recorded"


def test_Q3_price_and_terms_freeze_once_sent(m6):
    case = m6.new_case()
    case.action_take_custody("tech")
    quote = m6.accept_quote(case, amount=15000)
    res = m6.p03_write(
        m6.tech, "fix.data.quote", quote, {"amount": 95000, "no_data_no_fee_applies": False}
    )
    assert "error" in res
    with pytest.raises(UserError, match="frozen"):
        quote.write({"amount": 95000})
    assert quote.amount == 15000 and quote.no_data_no_fee_applies
    assert "amount" in quote._fix_form_locked_fields()
    # the legitimate change: a new version the customer accepts again
    out = m6.p03_action(m6.tech, "fix.data.quote", quote, "action_requote")
    assert out["success"], out
    new = m6.env["fix.data.quote"].browse(out["result"]["quote_ids"])
    assert quote.state == "superseded" and quote.superseded_by_id == new
    assert new.state == "draft"
    new.write({"amount": 95000})
    assert new.amount == 95000


def test_Q4_negative_amount_is_refused(m6):
    case = m6.new_case(evaluated=True)
    with pytest.raises(IntegrityError), m6.env.cr.savepoint():
        m6.env["fix.data.quote"].with_user(m6.tech).create({"case_id": case.id, "amount": -5000})
    res = m6.call(
        m6.tech,
        "model_write",
        model="fix.data.quote",
        record_id=None,
        values={"case_id": case.id, "amount": -5000},
    )
    assert "error" in res


# ---------------------------------------------------- media and cleanroom


def _unit(m6, case, suffix):
    return (
        m6.env["fix.data.media.unit"]
        .with_user(m6.tech)
        .create({"case_id": case.id, "seal_number": "SEAL-A2-%s-%d" % (suffix, m6.n)})
    )


def test_M1_media_cannot_be_forged_destroyed(m6):
    unit = _unit(m6, m6.new_case(), "M1")
    assert "error" in m6.p03_write(m6.tech, "fix.data.media.unit", unit, {"location": "destroyed"})
    with pytest.raises(UserError, match=GUARD):
        unit.write({"location": "destroyed"})
    unit.action_transfer(location="z4_lab", handler="Nadia")
    assert unit.location == "z4_lab"
    assert unit.case_id.custody_event_ids[-1].media_unit_id == unit


def test_M2_M3_seal_break_needs_a_distinct_witness(m6):
    unit = _unit(m6, m6.new_case(), "M2")
    out = m6.p03_action(m6.tech, "fix.data.media.unit", unit, "action_break_seal")
    assert not out["success"]  # the lax action is no longer offered
    with pytest.raises(UserError, match="second witness"):
        unit.action_break_seal()
    with pytest.raises(UserError, match="different person"):
        unit.action_break_seal_with_witness(witness_user_id=m6.tech.id)
    res = m6.p03_write(
        m6.tech,
        "fix.data.media.unit",
        unit,
        {"seal_state": "opened_in_lab", "witness_user_id": m6.tech.id},
    )
    assert "error" in res
    with pytest.raises(UserError, match=GUARD):
        unit.write({"seal_state": "opened_in_lab"})
    assert unit.seal_state == "sealed"
    out = m6.p03_action(
        m6.tech,
        "fix.data.media.unit",
        unit,
        "action_break_seal_with_witness",
        {"witness_user_id": m6.tech2.login},
    )
    assert out["success"], out
    assert (unit.seal_state, unit.witness_user_id) == ("opened_in_lab", m6.tech2)
    event = unit.case_id.custody_event_ids.filtered(lambda e: e.action == "seal_broken")
    assert (event.actor_id, event.witness_id) == (m6.tech, m6.tech2)


def test_M4_failed_interlock_slot_cannot_be_forged_used(m6):
    bad = m6.slot(particles=5000)
    assert not m6.p03_action(m6.tech, "fix.data.cleanroom.slot", bad, "action_use")["success"]
    assert "error" in m6.p03_write(m6.tech, "fix.data.cleanroom.slot", bad, {"state": "used"})
    with pytest.raises(UserError, match=GUARD):
        bad.write({"state": "used"})
    assert bad.state == "planned"
    good = m6.slot()
    good.action_use()
    assert good.state == "used"
    with pytest.raises(UserError, match="can no longer change"):
        good.write({"particle_count_per_ft3": 9000})


def test_M5_attempt_outcome_cannot_be_forged(m6):
    case = m6.to_recovering(m6.new_case())
    attempt = (
        m6.env["fix.data.recovery.attempt"]
        .with_user(m6.tech)
        .create({"case_id": case.id, "method": "software_scan"})
    )
    res = m6.p03_write(m6.tech, "fix.data.recovery.attempt", attempt, {"outcome": "success"})
    assert "error" in res
    with pytest.raises(UserError, match=GUARD):
        attempt.write({"outcome": "success"})
    assert attempt.outcome == "in_progress"
    out = m6.p03_action(
        m6.tech, "fix.data.recovery.attempt", attempt, "action_finish", {"outcome": "success"}
    )
    assert out["success"], out
    assert attempt.outcome == "success" and attempt.finished_at
    with pytest.raises(UserError, match="evidence"):
        attempt.write({"method": "chip_off"})


def test_evaluation_verdict_freezes_once_complete(m6):
    case = m6.new_case()
    ev = (
        m6.env["fix.data.evaluation"]
        .with_user(m6.tech)
        .create({"case_id": case.id, "verdict": "recoverable"})
    )
    with pytest.raises(UserError, match=GUARD):
        ev.write({"evaluated_at": datetime.now()})
    ev.action_complete()
    with pytest.raises(UserError, match="frozen"):
        ev.write({"verdict": "unrecoverable"})
