# M06 capture audit, second pass (2026-11-18): the records five pages could
# not capture because they did not exist, the case-intake facts, and the
# destruction form that could not attach the evidence its verification needs.
#
# Reported again: "not all the sub-modules have a relevant data capture
# button". After the 13 Nov pass every page had A button; measured against
# the M06 specification, these pages still captured nothing the spec says a
# person records there:
#   10  staff confidentiality undertakings (FR-DTS-010 P0, BRU-DTS-12 H) - no
#       record; any operator could be named on a case and open its data
#    7  retention hold override (FR-DTS-008b P0, BRU-DTS-06 H) - no record;
#       the retention job flagged every case for purge regardless
#    6  inventory by file type and size (FR-DTS-006) - totals only
#    9  wipe request + failed-erasure fallback (FR-DTS-019/024, BRU-DTS-10) -
#       no request record; and the certificate form had no evidence upload,
#       so a certificate made on the page could NEVER be verified
#    8  backup job runs (FR-DTS-012, AUT-DTS-11) - no record; restore tests
#       had no form, no scope and no evidence (FR-DTS-013)
#    1  failure symptoms, criticality, target data, declarations (FR-DTS-001)
#
# Every save below runs through the endpoints the forms use, as non-admin
# users holding only the M06 roles.
from __future__ import annotations

import base64
from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_data_case.tests.test_a02_p1p2_cd_data_case import (  # noqa: F401
    _cert,
    _FakeRequest,
    m6,
)
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_p03_portal.controllers.a02.writable import WRITABLE
from odoo.addons.cd_p03_portal.tests.test_m06_submodule_capture import reg  # noqa: F401
from odoo.exceptions import AccessError, UserError

CASE = "fix.data.recovery.case"
UND = "fix.data.confidentiality.undertaking"
HOLD = "fix.data.retention.hold"
INV = "fix.data.recovered.inventory"
WRQ = "fix.data.wipe.request"
CERT = "fix.data.wipe.certificate"
RUN = "fix.data.backup.run"
TEST = "fix.data.backup.test"
PDF = base64.b64encode(b"%PDF-1.4 evidence").decode()

NEW_FORMS = {
    "Staff Confidentiality Undertaking": ("10", "M06-form-undertaking", UND),
    "Retention Hold": ("7", "M06-form-retention-hold", HOLD),
    "Recovered Data by File Type": ("6", "M06-form-inventory-line", INV),
    "Wipe Request": ("9", "M06-form-wipe-request", WRQ),
    "Restore Test": ("8", "M06-form-restore-test", TEST),
    "Backup Job Run": ("8", "M06-form-backup-run", RUN),
}


def _write(m6, who, model, values, record=None):  # noqa: F811
    from unittest import mock

    with mock.patch.object(api, "request", _FakeRequest(m6.env(user=who.id))):
        return api.P03GenericApiController().model_write(
            model=model, record_id=record.id if record else None, values=values
        )


def _act(m6, who, model, rec, method, kwargs=None):  # noqa: F811
    return m6.p03_action(who, model, rec, method, kwargs)


# --- the pages -------------------------------------------------------------------


@pytest.mark.parametrize("chip", sorted(NEW_FORMS))
def test_each_new_record_is_captured_on_its_page(reg, chip):  # noqa: F811
    page, screen, model = NEW_FORMS[chip]
    sub = next(s for s in reg["subs"] if s["no"] == page)
    assert chip in sub["map"]["forms"], "%s is not on page %s" % (chip, page)
    assert reg["chips"]["M06:" + chip] == screen
    assert reg["forms"][screen]["model"] == model
    assert model in api.SURFACES, "%s is not served" % model
    assert WRITABLE.get(model), "%s accepts no field from its form" % model


def test_the_page_buttons_open_the_record_the_page_is_about(reg):  # noqa: F811
    want = {
        "6": "M06-form-inventory-line",
        "9": "M06-form-wipe-request",
        "10": "M06-form-undertaking",
    }
    for no, screen in want.items():
        sub = next(s for s in reg["subs"] if s["no"] == no)
        assert (sub["create"] or {}).get("screen") == screen, sub


def test_every_new_list_binds_real_columns_and_whitelisted_actions(reg, odoo_env):  # noqa: F811
    ids = [
        "M06-custody-ledger",
        "M06-inventory-lines",
        "M06-retention-holds",
        "M06-restore-tests",
        "M06-backup-runs",
        "M06-wipe-requests",
        "M06-undertakings",
    ]
    for sid in ids:
        cfg = reg["screens"][sid]
        fields_ = odoo_env[cfg["model"]]._fields
        assert not [c for c in cfg["cols"] if c not in fields_], sid
        for act in cfg.get("actions", []):
            assert act["m"] in api.SURFACES[cfg["model"]]["actions"], (sid, act["m"])
        assert cfg.get("title"), "%s would show its raw id as title" % sid
    pages = {s for sub in reg["subs"] for s in sub["map"]["screens"]}
    assert set(ids) <= pages, set(ids) - pages


def test_the_destruction_form_takes_its_evidence_upload(reg, odoo_env):  # noqa: F811
    names = {f["name"] for s in reg["forms"]["M06-form-wipe"]["sections"] for f in s["fields"]}
    assert {"wipe_log_attachment_id", "wipe_request_id"} <= names
    assert "wipe_log_attachment_id" in WRITABLE["fix.data.wipe.certificate"]
    case_names = {f["name"] for s in reg["forms"]["M06-form-case"]["sections"] for f in s["fields"]}
    assert {
        "criticality",
        "failure_symptoms",
        "target_data_description",
        "customer_declarations",
        "prior_recovery_attempt",
    } <= case_names
    tabs = {t["id"] for t in reg["forms"]["M06-form-case"]["tabs"]}
    assert all(s["tab"] in tabs for s in reg["forms"]["M06-form-case"]["sections"])


# --- page 10: undertakings before access -------------------------------------------


def test_no_one_is_named_on_a_case_without_their_undertaking(m6):  # noqa: F811
    case = (
        m6.env[CASE]
        .with_user(m6.tech)
        .create(
            {
                "customer_id": m6.customer.id,
                "media_type": "hdd",
                "media_serial_number": "U-%d" % m6.n,
            }
        )
    )
    with pytest.raises(AccessError, match="confidentiality undertaking"):
        case.with_user(m6.tech).action_assign_staff(technician=m6.tech, custodian=m6.custodian)
    # the workspace form: the person accepts it themself
    out = _write(
        m6,
        m6.tech,
        UND,
        {
            "case_id": case.id,
            "undertaking_type": "staff",
            "user_id": m6.tech.id,
            "acknowledged": True,
        },
    )
    assert "id" in out, out
    und = m6.env[UND].browse(out["id"])
    assert und.signature_method == "e_ack" and und.recorded_by_id == m6.tech
    # nobody accepts on screen for someone else
    out = _write(
        m6,
        m6.tech,
        UND,
        {
            "case_id": case.id,
            "undertaking_type": "staff",
            "user_id": m6.custodian.id,
            "acknowledged": True,
        },
    )
    assert "error" in out and "Only" in out["error"]
    # ...but can record their signed form
    out = _write(
        m6,
        m6.tech,
        UND,
        {
            "case_id": case.id,
            "undertaking_type": "staff",
            "user_id": m6.custodian.id,
            "document_attachment_id": {"upload": PDF, "filename": "undertaking.pdf"},
        },
    )
    assert "id" in out, out
    signed = m6.env[UND].browse(out["id"])
    assert signed.signature_method == "signed_form"
    assert signed.document_attachment_id.res_model == UND
    case.with_user(m6.tech).action_assign_staff(technician=m6.tech, custodian=m6.custodian)
    assert case.z4_custodian_id == m6.custodian
    # a signed record does not change
    res = _write(m6, m6.tech, UND, {"valid_until": "2030-01-01"}, record=und)
    assert "error" in res
    with pytest.raises(UserError):
        und.with_user(m6.tech).write({"user_id": m6.tech2.id})
    # a second active undertaking for the same person is refused
    out = _write(
        m6,
        m6.tech,
        UND,
        {
            "case_id": case.id,
            "undertaking_type": "staff",
            "user_id": m6.tech.id,
            "acknowledged": True,
        },
    )
    assert "error" in out and "already" in out["error"]


def test_a_revoked_undertaking_stops_the_person_working_the_case(m6):  # noqa: F811
    case = m6.recovering(m6.new_case())
    und = case.undertaking_ids.filtered(lambda u: u.user_id == m6.tech)
    out = _act(m6, m6.tech, UND, und, "action_revoke", {"reason": "left the lab"})
    assert not out["success"] and "lab manager" in out["error"]
    out = _act(m6, m6.custodian, UND, und, "action_revoke", {"reason": "left the lab"})
    assert out["success"], out
    assert und.state == "revoked"
    with pytest.raises(AccessError, match="confidentiality undertaking"):
        m6.env["fix.data.recovery.attempt"].with_user(m6.tech).create(
            {"case_id": case.id, "method": "software_scan"}
        )


def test_a_customer_nda_needs_the_signed_document(m6):  # noqa: F811
    case = m6.new_case()
    out = _write(
        m6,
        m6.tech,
        UND,
        {"case_id": case.id, "undertaking_type": "customer_nda", "partner_id": m6.customer.id},
    )
    assert "error" in out and "Attach" in out["error"]
    out = _write(
        m6,
        m6.tech,
        UND,
        {
            "case_id": case.id,
            "undertaking_type": "customer_nda",
            "partner_id": m6.customer.id,
            "document_attachment_id": {"upload": PDF, "filename": "nda.pdf"},
        },
    )
    assert "id" in out, out


# --- page 7: retention hold --------------------------------------------------------


def test_a_retention_hold_keeps_the_data_only_once_another_manager_approves(m6):  # noqa: F811
    case = m6.handed_over(m6.new_case(serial="WD-HOLD-%d" % m6.n), target="T-HOLD")
    cert = _cert(m6, case.media_serial_number)
    end = case.retention_until
    vals = {
        "case_id": case.id,
        "reason_type": "legal_hold",
        "reason": "Court order 77/2026 in the customer's dispute",
        "hold_until": fields.Date.to_string(end + timedelta(days=30)),
    }
    # must outlast the retention, and is time-limited
    out = _write(m6, m6.manager, HOLD, dict(vals, hold_until=fields.Date.to_string(end)))
    assert "error" in out and "after that" in out["error"]
    out = _write(
        m6,
        m6.manager,
        HOLD,
        dict(vals, hold_until=fields.Date.to_string(fields.Date.today() + timedelta(days=400))),
    )
    assert "error" in out and "at most" in out["error"]
    out = _write(m6, m6.manager, HOLD, vals)
    assert "id" in out, out
    hold = m6.env[HOLD].browse(out["id"])
    assert hold.state == "requested" and hold.requested_by_id == m6.manager
    # a request alone holds nothing; the requester cannot approve it
    out = _act(m6, m6.manager, HOLD, hold, "action_approve")
    assert not out["success"] and "Segregation" in out["error"]
    out = _act(m6, m6.tech, HOLD, hold, "action_approve")
    assert not out["success"]
    out = _act(m6, m6.manager2, HOLD, hold, "action_approve")
    assert out["success"], out
    assert hold.state == "approved" and hold.decided_by_id == m6.manager2
    # while it runs: no purge by hand, and the retention job skips the case
    with pytest.raises(UserError, match="retention hold"):
        case.with_user(m6.tech).action_purge(cert)
    case._guarded().write({"retention_until": fields.Date.today() - timedelta(days=1)})
    # with automatic purge off the job would flag the case for purging
    m6.env["ir.config_parameter"].sudo().set_param("cd_data_case.retention_auto_purge", "0")
    assert m6.env[CASE].cron_retention_purge() == 0
    assert not case.retention_flagged_at and not case.activity_ids.filtered(
        lambda a: "Retention ended" in (a.summary or "")
    )
    m6.env["ir.config_parameter"].sudo().set_param("cd_data_case.retention_auto_purge", "1")
    assert m6.env[CASE].cron_retention_purge() == 0
    assert case.state == "handover" and not case.retention_flagged_at
    # released: the case is due again and purged on its certificate
    out = _act(m6, m6.manager, HOLD, hold, "action_release")
    assert out["success"], out
    assert m6.env[CASE].cron_retention_purge() == 1 and case.state == "purged"


def test_an_ended_hold_expires_and_the_case_is_flagged(m6):  # noqa: F811
    case = m6.handed_over(m6.new_case(serial="WD-EXP-%d" % m6.n), target="T-EXP")
    hold = (
        m6.env[HOLD]
        .with_user(m6.manager)
        .create(
            {
                "case_id": case.id,
                "reason_type": "customer_request",
                "reason": "asked in writing",
                "hold_until": case.retention_until + timedelta(days=5),
            }
        )
    )
    hold.with_user(m6.manager2).action_approve()
    hold._guarded().write({"hold_until": fields.Date.today() - timedelta(days=1)})
    case._guarded().write({"retention_until": fields.Date.today() - timedelta(days=2)})
    m6.env[CASE].cron_retention_purge()
    assert hold.state == "expired" and case.retention_flagged_at


def test_a_hold_applies_only_to_handed_over_data(m6):  # noqa: F811
    case = m6.new_case()
    out = _write(
        m6,
        m6.manager,
        HOLD,
        {"case_id": case.id, "reason_type": "dispute", "reason": "x", "hold_until": "2030-01-01"},
    )
    assert "error" in out and "handed over" in out["error"]


# --- page 6: inventory by file type ------------------------------------------------


def test_the_inventory_is_recorded_per_file_type_and_sums_to_the_case(m6):  # noqa: F811
    case = m6.recovering(m6.new_case())
    out = _write(
        m6,
        m6.tech2,
        INV,
        {"case_id": case.id, "file_type": "images", "file_count": 10, "size_gb": 1},
    )
    assert "error" in out and "assigned staff" in out["error"]
    out = _write(
        m6,
        m6.tech,
        INV,
        {"case_id": case.id, "file_type": "images", "file_count": 12000, "size_gb": 48.5},
    )
    assert "id" in out, out
    line = m6.env[INV].browse(out["id"])
    out = _write(
        m6,
        m6.tech,
        INV,
        {"case_id": case.id, "file_type": "documents", "file_count": 3400, "size_gb": 2.25},
    )
    assert "id" in out, out
    assert case.recovered_files_count == 15400 and case.recovered_volume_gb == 50.75
    out = _write(
        m6,
        m6.tech,
        INV,
        {"case_id": case.id, "file_type": "images", "file_count": 1, "size_gb": 0.1},
    )
    assert "error" in out and "already" in out["error"]
    out = _write(
        m6, m6.tech, INV, {"case_id": case.id, "file_type": "video", "file_count": 0, "size_gb": 3}
    )
    assert "error" in out
    # the totals-only entry would contradict the lines
    with pytest.raises(UserError, match="by file type"):
        case.with_user(m6.tech).action_record_inventory(files_count=1, volume_gb=1)
    # a correction updates the totals
    res = _write(m6, m6.tech, INV, {"file_count": 12500}, record=line)
    assert "error" not in res, res
    assert case.recovered_files_count == 15900
    # frozen once handed over
    m6.image(case)
    case.action_recovered()
    case.write({"handover_recipient_id": m6.contact.id, "encrypted_target_serial": "T-INV2"})
    case.action_confirm_target_serial("T-INV2")
    m6.receipt(case)
    case.action_handover(verification=m6.code_for(case)["code"])
    res = _write(m6, m6.tech, INV, {"file_count": 1}, record=line)
    assert "error" in res and line.file_count == 12500
    with pytest.raises(UserError, match="before handover"):
        line.with_user(m6.tech).write({"file_count": 1})
    with pytest.raises(UserError):
        line.with_user(m6.tech).unlink()


# --- page 9: wipe requests, failed erasure, the evidence upload ---------------------


def test_a_request_is_answered_by_a_certificate_verified_on_its_uploaded_evidence(m6):  # noqa: F811
    serial = "SN-WRQ-%d" % m6.n
    clerk = m6.user("clerk")  # an M14/M18 desk, no M06 role
    out = _write(
        m6,
        clerk,
        WRQ,
        {
            "source": "m14_refurbishment",
            "source_ref": "TI-0042",
            "serial_number": serial,
            "confidentiality_level": "moderate",
            "disposition": "resale",
        },
    )
    assert "id" in out, out
    req = m6.env[WRQ].browse(out["id"])
    assert req.state == "requested" and req.name.startswith("WRQ/")
    # the certificate form: the serial comes from the request; the evidence
    # is uploaded on the form (before this pass it could not be)
    out = _write(
        m6,
        m6.tech,
        CERT,
        {
            "wipe_request_id": req.id,
            "method": "nist_800_88",
            "sector_count": 976773168,
            "tool_name": "nwipe 0.35",
            "wipe_log_attachment_id": {
                "upload": base64.b64encode(b"nwipe PASS").decode(),
                "filename": "nwipe.log",
            },
        },
    )
    assert "id" in out, out
    cert = m6.env[CERT].browse(out["id"])
    assert cert.serial_number == serial and cert.wipe_log_attachment_id
    assert req.state == "in_progress"
    cert.with_user(m6.verifier).action_verify()
    assert cert.sanitization_status == "verified" and req.state == "certified"
    # what was asked is fixed once worked
    res = _write(m6, clerk, WRQ, {"serial_number": "OTHER"}, record=req)
    assert "error" in res


def test_a_failed_erasure_makes_physical_destruction_mandatory(m6):  # noqa: F811
    serial = "SN-FAIL-%d" % m6.n
    req = (
        m6.env[WRQ]
        .with_user(m6.tech)
        .create(
            {
                "source": "m18_recycling",
                "serial_number": serial,
                "confidentiality_level": "high",
                "disposition": "recycling",
            }
        )
    )
    with pytest.raises(UserError, match="is for media"):
        m6.env[CERT].with_user(m6.tech).create(
            {"wipe_request_id": req.id, "method": "nist_800_88", "serial_number": "WRONG"}
        )
    first = (
        m6.env[CERT]
        .with_user(m6.tech)
        .create({"wipe_request_id": req.id, "method": "nist_800_88_purge"})
    )
    first.with_user(m6.verifier).action_mark_failed()
    assert req.state == "physical_required"
    assert req.activity_ids.filtered(lambda a: a.user_id == m6.tech)
    with pytest.raises(UserError, match="BRU-DTS-10"):
        m6.env[CERT].with_user(m6.tech).create(
            {"wipe_request_id": req.id, "method": "cryptographic_erase"}
        )
    second = (
        m6.env[CERT]
        .with_user(m6.tech)
        .create({"wipe_request_id": req.id, "method": "physical_destruction"})
    )
    assert second.serial_number == serial and req.state == "in_progress"


def test_only_an_unworked_request_is_cancelled(m6):  # noqa: F811
    req = (
        m6.env[WRQ]
        .with_user(m6.tech)
        .create(
            {
                "source": "customer",
                "serial_number": "SN-C-%d" % m6.n,
                "confidentiality_level": "low",
                "disposition": "return_customer",
            }
        )
    )
    out = _act(m6, m6.tech, WRQ, req, "action_cancel", {"reason": "customer withdrew"})
    assert out["success"], out
    assert req.state == "cancelled"
    with pytest.raises(UserError, match="cancelled"):
        m6.env[CERT].with_user(m6.tech).create({"wipe_request_id": req.id, "method": "nist_800_88"})


# --- page 8: job runs and evidenced restore tests -------------------------------------


def _plan(m6):  # noqa: F811
    return (
        m6.env["fix.data.backup.plan"]
        .with_user(m6.tech)
        .create(
            {
                "name": "Office NAS %d" % m6.n,
                "customer_id": m6.customer.id,
                "test_frequency_days": 30,
            }
        )
    )


def test_two_failed_runs_in_a_row_raise_one_incident(m6):  # noqa: F811
    plan = _plan(m6)
    now = fields.Datetime.now()

    def run(outcome, hours_ago, **extra):
        out = _write(
            m6,
            m6.tech,
            RUN,
            {
                "plan_id": plan.id,
                "outcome": outcome,
                "started_at": fields.Datetime.to_string(now - timedelta(hours=hours_ago)),
                **extra,
            },
        )
        assert "id" in out, out
        return m6.env[RUN].browse(out["id"])

    out = _write(m6, m6.tech, RUN, {"plan_id": plan.id, "outcome": "failed"})
    assert "error" in out and "error reference" in out["error"]
    run("failed", 30, error_ref="VSS-0x80042306")
    run("success", 20, transferred_gb=12.5)
    second = run("missed", 10)
    assert not second.incident_raised  # the run before it succeeded
    third = run("failed", 1, error_ref="disk full")
    assert third.incident_raised
    assert plan.consecutive_failures == 2 and plan.last_run_outcome == "failed"
    todo = plan.activity_ids.filtered(lambda a: "Backup failing" in (a.summary or ""))
    assert todo and todo.user_id == m6.tech
    res = _write(m6, m6.tech, RUN, {"outcome": "success"}, record=third)
    assert "error" in res


def test_a_passed_restore_test_needs_its_evidence_and_rolls_the_due_date(m6):  # noqa: F811
    plan = _plan(m6)
    plan.sudo().write({"next_test_due": fields.Date.today() - timedelta(days=3)})
    vals = {
        "plan_id": plan.id,
        "result": "passed",
        "restored_gb": 40,
        "scope_tested": "Finance share, 3 folders, opened 20 files",
    }
    out = _write(m6, m6.tech, TEST, vals)
    assert "error" in out and "evidence" in out["error"]
    out = _write(
        m6,
        m6.tech,
        TEST,
        dict(vals, evidence_attachment_id={"upload": PDF, "filename": "restore-report.pdf"}),
    )
    assert "id" in out, out
    test = m6.env[TEST].browse(out["id"])
    assert test.tested_by == m6.tech and test.evidence_attachment_id.res_model == TEST
    assert plan.compliant and plan.next_test_due == fields.Date.today() + timedelta(days=30)
    res = _write(m6, m6.tech, TEST, {"result": "failed"}, record=test)
    assert "error" in res
    # a failed test needs no evidence, and is logged as such
    out = _write(
        m6, m6.tech, TEST, {"plan_id": plan.id, "result": "failed", "notes": "catalogue corrupt"}
    )
    assert "id" in out and not plan.compliant


# --- page 1: intake --------------------------------------------------------------------


def test_the_case_form_takes_the_intake_facts(m6):  # noqa: F811
    out = _write(
        m6,
        m6.tech,
        CASE,
        {
            "customer_id": m6.customer.id,
            "media_type": "ssd",
            "criticality": "business_critical",
            "failure_symptoms": "Not detected in BIOS after a power cut",
            "target_data_description": "Accounts folder and the Tally company data",
            "customer_declarations": "Owner of the data; no earlier recovery attempt",
            "prior_recovery_attempt": False,
        },
    )
    assert "id" in out, out
    case = m6.env[CASE].browse(out["id"])
    assert case.criticality == "business_critical"
    assert case.failure_symptoms.startswith("Not detected")


def test_the_inventory_report_shows_the_breakdown_by_type(m6):  # noqa: F811
    from unittest import mock

    case = m6.recovering(m6.new_case())
    m6.env[INV].with_user(m6.tech).create(
        {"case_id": case.id, "file_type": "email", "file_count": 4, "size_gb": 12.5}
    )
    with mock.patch.object(api, "request", mock.Mock(env=m6.env(user=m6.tech.id))):
        out = api.P03GenericApiController().model_report(
            module="M06", report="recovered_inventory", params={}
        )
    row = next(r for r in out["rows"] if r["case"] == case.name)
    assert row["recovered_files"] == 4 and "Email Stores 4 (12.50 GB)" in row["by_type"]
    assert out["labels"]["by_type"] == "By File Type"
