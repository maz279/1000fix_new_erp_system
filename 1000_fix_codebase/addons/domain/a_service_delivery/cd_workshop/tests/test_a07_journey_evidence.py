# Running M31 as real users on a copy of live data: evidence filed on screen never
# counted for the release gate, and the M01 checklist could not be completed, so no
# order could reach Ready through the workspace.
from __future__ import annotations

import base64

import pytest
from odoo.exceptions import UserError, ValidationError

from . import test_a02_p0_m31 as a02

m31 = a02.m31


def _upload(m, job, evidence_type, name="photo.png"):
    return (
        m.env["fix.workshop.evidence"]
        .with_user(m.tech)
        .create(
            {
                "job_id": job.id,
                "name": name,
                "evidence_type": evidence_type,
                "upload_file": base64.b64encode(b"\x89PNG evidence"),
                "upload_filename": name,
            }
        )
    )


def test_an_upload_on_the_evidence_form_satisfies_the_release_gate(m31):
    job = m31.job()
    with pytest.raises(UserError, match="evidence pack"), m31.env.cr.savepoint():
        job._m31_check_release_evidence()
    first = _upload(m31, job, "post_repair_photo")
    _upload(m31, job, "test_log", "log.txt")
    job.invalidate_recordset()
    job._m31_check_release_evidence()
    assert (first.document_id.res_model, first.document_id.res_id) == (job._name, job.id)
    assert first.document_id.attachment_id.name == "photo.png"
    assert base64.b64decode(first.document_id.attachment_id.datas) == b"\x89PNG evidence"


def test_an_unfiled_document_picked_as_evidence_is_filed_against_the_job(m31):
    job = m31.job()
    document = m31.env["fix.document"].attach(
        name="A07 loose", datas=base64.b64encode(b"x"), document_type="evidence_pack"
    )
    m31.env["fix.workshop.evidence"].with_user(m31.tech).create(
        {"job_id": job.id, "name": "A07", "evidence_type": "test_log", "document_id": document.id}
    )
    assert (document.res_model, document.res_id) == (job._name, job.id)


def test_a_document_filed_elsewhere_cannot_be_this_jobs_evidence(m31):
    job = m31.job()
    document = m31.env["fix.document"].attach(
        name="A07 elsewhere",
        datas=base64.b64encode(b"x"),
        document_type="evidence_pack",
        res_model="res.partner",
        res_id=1,
    )
    with pytest.raises(UserError, match="another record"), m31.env.cr.savepoint():
        m31.env["fix.workshop.evidence"].with_user(m31.tech).create(
            {
                "job_id": job.id,
                "name": "A07",
                "evidence_type": "test_log",
                "document_id": document.id,
            }
        )


# ------------------------------------------------------------ the M01 QC checklist
def _checklist(m, **stages):
    order = m.order()
    return m.env["fix.qc.checklist"].create({"order_id": order.id, **stages})


ALL_STAGES = {
    "visual_inspection_passed": True,
    "functional_test_passed": True,
    "safety_electrical_passed": True,
    "cleaning_sanitization_passed": True,
}


def test_qc_stages_are_not_born_passed(m31):
    checklist = _checklist(m31)
    assert not any(checklist[name] for name in ALL_STAGES)


def test_a_checklist_with_no_stage_inspected_is_refused(m31):
    checklist = _checklist(m31)
    with pytest.raises(ValidationError, match="at least one item"), m31.env.cr.savepoint():
        checklist.action_complete()


def test_the_stages_a_person_ticks_become_the_checklist(m31):
    checklist = _checklist(m31, **ALL_STAGES)
    checklist.action_complete()
    assert len(checklist.item_ids) == 4 and checklist.state == "passed"


def test_a_stage_left_unticked_fails_the_checklist(m31):
    checklist = _checklist(m31, visual_inspection_passed=True)
    checklist.action_complete()
    assert len(checklist.item_ids) == 4 and checklist.state == "failed"
