# M58 candidate biodata standard (18 Nov 2026): the full candidate record —
# education, training, employment, skills, languages, referees, family and
# documents as add-more-lines registers with a scan per row — exercised as
# non-admin users on the ORM and through the real /p03 form controller.
import base64
import hashlib
from unittest import mock

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_talent.tests.test_a09_talent_controls import (
    FakeRequest,
    _accept,
    _candidate,
    _interviewed,
    _ready_to_hire,
    _requisition,
    make_x,
)
from odoo.exceptions import AccessError, UserError, ValidationError

PDF = base64.b64encode(b"%PDF-1.4 candidate certificate").decode()
PDF2 = base64.b64encode(b"%PDF-1.4 a different certificate").decode()


@pytest.fixture
def x(odoo_env):
    return make_x(odoo_env)


@pytest.fixture
def call():
    """The real /p03 controller, as the given user (the M58 suite's harness)."""
    patchers = []

    def _call(env, route, **kw):
        p = mock.patch.object(api, "request", FakeRequest(env))
        p.start()
        patchers.append(p)
        return getattr(api.P03GenericApiController(), route)(**kw)

    yield _call
    for p in patchers:
        p.stop()


def _edu(**vals):
    base = {
        "level": "hsc",
        "exam_title": "HSC",
        "major": "Science",
        "board": "dhaka",
        "institute": "Dhaka College",
        "passing_year": 2016,
        "result_type": "gpa5",
        "result": 4.5,
        "certificate_file": PDF,
        "certificate_filename": "hsc.pdf",
    }
    base.update(vals)
    return base


def _form_fields(call, env, model, names, record_id=None, grids=None):
    return call(
        env,
        "model_form",
        model=model,
        fields=[{"name": n} for n in names],
        record_id=record_id,
        grids=grids or [],
    )


# ============================================================== the registers
def test_every_register_takes_many_lines_with_their_files(x):
    cand = _candidate(x, _requisition(x))
    rec = cand.with_user(x.recruiter)
    rec.write(
        {
            "education_ids": [
                (0, 0, _edu(level="ssc", exam_title="SSC", passing_year=2014, result=5.0)),
                (0, 0, _edu()),
                (
                    0,
                    0,
                    _edu(
                        level="bachelor_hons",
                        exam_title="B.Sc. in EEE",
                        board="university",
                        institute="BUET",
                        passing_year=2021,
                        result_type="cgpa4",
                        result=3.4,
                        transcript_file=PDF2,
                        transcript_filename="t.pdf",
                    ),
                ),
            ],
            "training_ids": [
                (0, 0, {"title": "Samsung Mobile L2", "institute": "Samsung", "kind": "oem"}),
                (0, 0, {"title": "RAC Servicing", "institute": "BTEB", "kind": "vocational"}),
            ],
            "experience_ids": [
                (
                    0,
                    0,
                    {
                        "employer": "Walton",
                        "designation": "Technician",
                        "start_date": "2021-03-01",
                        "end_date": "2023-02-28",
                    },
                ),
                (
                    0,
                    0,
                    {
                        "employer": "Rangs",
                        "designation": "Senior Technician",
                        "start_date": "2023-03-01",
                        "currently_working": True,
                    },
                ),
            ],
            "language_ids": [(0, 0, {"language": "bangla", "speaking": "native"})],
            "skill_ids": [(0, 0, {"category": "mobile", "skill": "BGA rework"})],
            "reference_ids": [
                (0, 0, {"name": "Mr. Karim", "relation": "supervisor", "phone": "01711000000"})
            ],
            "document_ids": [
                (
                    0,
                    0,
                    {"document_type": "cv", "document_file": PDF, "document_filename": "cv.pdf"},
                ),
                (0, 0, {"document_type": "testimonial", "document_file": PDF2}),
            ],
        }
    )
    assert len(cand.education_ids) == 3
    assert cand.highest_education_level == "bachelor_hons"
    assert cand.total_experience_years >= 3.5
    assert len(cand.training_ids) == 2 and len(cand.document_ids) == 2
    # each scan is hashed and stamped with its uploader, and awaits verification
    edu = cand.education_ids.filtered(lambda e: e.exam_title == "B.Sc. in EEE")
    digests = edu.evidence_sha256.split(",")
    assert hashlib.sha256(base64.b64decode(PDF)).hexdigest() in digests
    assert hashlib.sha256(base64.b64decode(PDF2)).hexdigest() in digests
    assert edu.uploaded_by_id == x.recruiter
    assert set(cand.document_ids.mapped("verification_state")) == {"pending"}
    assert cand.evidence_pending == 3 + 0 + 0 + 2  # files on 3 education rows + 2 documents


def test_a_document_line_needs_its_file(x):
    cand = _candidate(x, _requisition(x))
    with pytest.raises(UserError, match="Attach"), x.env.cr.savepoint():
        cand.with_user(x.recruiter).write({"document_ids": [(0, 0, {"document_type": "cv"})]})


@pytest.mark.parametrize(
    "vals,message",
    [
        ({"result_type": "gpa5", "result": 5.5}, "at most 5"),
        ({"result_type": "cgpa4", "result": 4.2}, "at most 4"),
        ({"passing_year": 1890}, "not plausible"),
    ],
)
def test_an_implausible_result_is_refused(x, vals, message):
    cand = _candidate(x, _requisition(x))
    with pytest.raises(ValidationError, match=message), x.env.cr.savepoint():
        cand.with_user(x.recruiter).write({"education_ids": [(0, 0, _edu(**vals))]})


def test_a_current_job_has_no_end_date(x):
    cand = _candidate(x, _requisition(x))
    with pytest.raises(ValidationError, match="current"), x.env.cr.savepoint():
        cand.with_user(x.recruiter).write(
            {
                "experience_ids": [
                    (
                        0,
                        0,
                        {
                            "employer": "X",
                            "designation": "Y",
                            "start_date": "2022-01-01",
                            "end_date": "2023-01-01",
                            "currently_working": True,
                        },
                    )
                ]
            }
        )


def test_a_plain_user_cannot_add_biodata_lines(x):
    cand = _candidate(x, _requisition(x))
    with pytest.raises(AccessError), x.env.cr.savepoint():
        x.env(user=x.plain.id)["fix.candidate.education"].create(dict(_edu(), candidate_id=cand.id))


# ================================================= data minimisation (PDPO 2025)
def test_sensitive_particulars_wait_for_the_offer_stage(x):
    cand = _candidate(x, _requisition(x))
    with pytest.raises(UserError, match="offer stage"), x.env.cr.savepoint():
        cand.with_user(x.recruiter).write({"religion": "islam"})
    with pytest.raises(UserError, match="offer stage"), x.env.cr.savepoint():
        _candidate(x, _requisition(x), blood_group="o_pos")
    with pytest.raises(UserError, match="offer stage"), x.env.cr.savepoint():
        cand.with_user(x.recruiter).write(
            {"family_ids": [(0, 0, {"name": "Spouse", "relation": "spouse"})]}
        )
    with pytest.raises(UserError, match="offer stage"), x.env.cr.savepoint():
        cand.with_user(x.recruiter).write(
            {"document_ids": [(0, 0, {"document_type": "bank_proof", "document_file": PDF})]}
        )
    # the form shows them locked until then
    assert {"religion", "blood_group", "marital_status", "spouse_name"} <= set(
        cand._fix_form_locked_fields()
    )


def test_at_the_offer_stage_the_joining_particulars_are_taken(x):
    cand, _offer = _ready_to_hire(x)
    assert cand.state == "offered"
    cand.with_user(x.recruiter).write(
        {
            "religion": "islam",
            "blood_group": "b_pos",
            "marital_status": "married",
            "spouse_name": "Ayesha",
            "family_ids": [
                (
                    0,
                    0,
                    {
                        "name": "Ayesha",
                        "relation": "spouse",
                        "phone": "01700000001",
                        "is_emergency_contact": True,
                        "is_nominee": True,
                        "nominee_pct": 60,
                    },
                ),
                (0, 0, {"name": "Rahim", "relation": "son", "is_nominee": True, "nominee_pct": 40}),
            ],
        }
    )
    assert len(cand.family_ids) == 2
    with pytest.raises(ValidationError, match="100"), x.env.cr.savepoint():
        cand.with_user(x.recruiter).write(
            {
                "family_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Extra",
                            "relation": "father",
                            "is_nominee": True,
                            "nominee_pct": 10,
                        },
                    )
                ]
            }
        )
    with pytest.raises(ValidationError, match="phone"), x.env.cr.savepoint():
        cand.with_user(x.recruiter).write(
            {
                "family_ids": [
                    (0, 0, {"name": "Sis", "relation": "sister", "is_emergency_contact": True})
                ]
            }
        )


def test_salary_is_hidden_from_a_hiring_manager(x):
    fields_hm = x.env(user=x.plain.id)["fix.candidate"].fields_get(["expected_salary"])
    assert "expected_salary" not in fields_hm
    assert "expected_salary" in x.env(user=x.recruiter.id)["fix.candidate"].fields_get(
        ["expected_salary"]
    )


def test_permanent_address_can_copy_the_present_one(x):
    cand = _candidate(
        x,
        _requisition(x),
        present_address="House 5, Road 2",
        present_district="Gazipur",
        present_division="dhaka",
        permanent_same_as_present=True,
    )
    assert cand.permanent_address == "House 5, Road 2"
    assert cand.permanent_division == "dhaka"
    cand.with_user(x.recruiter).write({"present_district": "Narsingdi"})
    assert cand.permanent_district == "Narsingdi"


def test_declaration_is_stamped_by_the_system(x):
    cand = _candidate(x, _requisition(x), declaration_accepted=False)
    assert not cand.declaration_on
    cand.with_user(x.recruiter).write({"declaration_accepted": True})
    assert cand.declaration_on
    with pytest.raises(UserError, match="workflow"), x.env.cr.savepoint():
        cand.with_user(x.recruiter).write({"declaration_on": "2020-01-01 00:00:00"})


# ============================================================== verification
def test_evidence_is_verified_by_someone_who_did_not_upload_it(x):
    cand = _candidate(x, _requisition(x))
    cand.with_user(x.recruiter).write({"education_ids": [(0, 0, _edu())]})
    edu = cand.education_ids
    # the recruiter cannot verify, nor write the verdict directly
    with pytest.raises(AccessError), x.env.cr.savepoint():
        edu.with_user(x.recruiter).action_verify()
    with pytest.raises(UserError, match="workflow"), x.env.cr.savepoint():
        edu.with_user(x.recruiter).write({"verification_state": "verified"})
    both = x.env["res.users"].browse(x.recruiter.id)
    both.sudo().write({"group_ids": [(4, x.env.ref("cd_talent.group_background_verifier").id)]})
    with pytest.raises(UserError, match="another verifier"), x.env.cr.savepoint():
        edu.with_user(both).action_verify()
    edu.with_user(x.verifier).action_verify()
    assert edu.verification_state == "verified" and edu.verified_by_id == x.verifier
    # a verified record is kept as it is
    with pytest.raises(UserError, match="verified"), x.env.cr.savepoint():
        edu.with_user(x.recruiter).write({"certificate_file": PDF2})
    with pytest.raises(UserError, match="verified"), x.env.cr.savepoint():
        edu.with_user(x.recruiter).unlink()


def test_a_replaced_file_is_decided_again(x):
    cand = _candidate(x, _requisition(x))
    cand.with_user(x.recruiter).write(
        {"document_ids": [(0, 0, {"document_type": "nid", "document_file": PDF})]}
    )
    doc = cand.document_ids
    doc.with_user(x.verifier).action_flag_discrepancy(reason="Photo does not match")
    assert doc.verification_state == "discrepancy"
    doc.with_user(x.recruiter).write({"document_file": PDF2})
    assert doc.verification_state == "pending" and not doc.verified_by_id


def test_a_discrepancy_stops_the_offer_stage(x):
    cand = _candidate(x, _requisition(x))
    cand.with_user(x.recruiter).write({"education_ids": [(0, 0, _edu())]})
    cand.education_ids.with_user(x.verifier).action_flag_discrepancy(reason="Board says GPA 3.2")
    _interviewed(x, cand)
    with pytest.raises(UserError, match="discrepancy"), x.env.cr.savepoint():
        cand.with_user(x.recruiter).action_offer()


def test_the_hire_needs_the_declaration(x):
    _cand, offer = _ready_to_hire(x, declaration_accepted=False)
    with pytest.raises(UserError, match="declaration"), x.env.cr.savepoint():
        _accept(x, offer)


# ===================================================================== hire
def test_a_discrepancy_found_after_the_offer_stage_blocks_the_hire(x):
    cand, offer = _ready_to_hire(x)
    cand.with_user(x.recruiter).write(
        {"document_ids": [(0, 0, {"document_type": "release_letter", "document_file": PDF})]}
    )
    cand.document_ids.with_user(x.verifier).action_flag_discrepancy(reason="Forged letter")
    with pytest.raises(UserError, match="discrepancy"), x.env.cr.savepoint():
        _accept(x, offer)
    assert cand.state == "offered"


def test_the_hire_carries_the_biodata_to_the_employee(x):
    req = _requisition(x)
    cand, offer = _ready_to_hire(
        x,
        req,
        father_name="Abdul Karim",
        mother_name="Rahima Begum",
        passport_number="BR0934567",
        present_address="House 5",
        present_district="Gazipur",
    )
    rec = cand.with_user(x.recruiter)
    rec.write(
        {
            "sex": "male",
            "blood_group": "a_pos",
            "education_ids": [(0, 0, _edu())],
            "experience_ids": [
                (
                    0,
                    0,
                    {
                        "employer": "Walton",
                        "designation": "Technician",
                        "start_date": "2021-03-01",
                        "currently_working": True,
                        "experience_letter_file": PDF,
                    },
                )
            ],
            "document_ids": [
                (
                    0,
                    0,
                    {"document_type": "nid", "document_file": PDF, "document_filename": "n.pdf"},
                ),
                (0, 0, {"document_type": "cv", "document_file": PDF2}),
            ],
            "family_ids": [
                (
                    0,
                    0,
                    {
                        "name": "Ayesha",
                        "relation": "spouse",
                        "phone": "01700000002",
                        "is_emergency_contact": True,
                        "is_nominee": True,
                        "nominee_pct": 100,
                    },
                )
            ],
        }
    )
    cand.education_ids.with_user(x.verifier).action_verify()
    nid_doc = cand.document_ids.filtered(lambda d: d.document_type == "nid")
    nid_doc.with_user(x.verifier).action_verify()
    _accept(x, offer)
    assert cand.state == "hired"
    emp = cand.employee_id.sudo()
    assert emp.father_name == "Abdul Karim" and emp.mother_name == "Rahima Begum"
    assert emp.blood_group == "a_pos" and emp.sex == "male"
    assert emp.emergency_contact == "Ayesha"
    edu = emp.education_line_ids
    assert len(edu) == 1 and edu.is_verified == "verified_physical"
    assert len(emp.experience_line_ids) == 1
    assert emp.experience_line_ids.end_date  # a current job ends at the hire
    assert set(emp.document_ids.mapped("doc_type")) >= {"nid_smart", "cv"}
    assert emp.dependant_ids.filtered("is_nominee").nominee_pct == 100
    # M58-F4: nothing clear of the passport is left in the candidate's row (the
    # copy to the employee is exercised in test_m58_identity_residency.py, with
    # a store that serves the value back)
    cand.env.cr.execute("SELECT passport_number FROM fix_candidate WHERE id = %s", (cand.id,))
    assert not cand.env.cr.fetchone()[0]
    # the pre-boarding NID arrives verified by its own verifier
    plan = x.env["fix.onboarding.plan"].search([("candidate_id", "=", cand.id)])
    nid_item = plan.document_ids.filtered(lambda d: d.document_type == "nid")
    assert nid_item.state == "verified" and nid_item.verified_by_id == x.verifier
    # a hired candidate's biodata is frozen: it lives on the employee now
    with pytest.raises(UserError, match="hired"), x.env.cr.savepoint():
        cand.with_user(x.recruiter).write(
            {"skill_ids": [(0, 0, {"category": "other", "skill": "x"})]}
        )


# =============================================================== retention
def test_erasure_removes_every_line_and_file(x):
    cand = _candidate(x, _requisition(x), father_name="F", cv_file=PDF, cv_filename="cv.pdf")
    cand.with_user(x.recruiter).write(
        {
            "education_ids": [(0, 0, _edu())],
            "document_ids": [(0, 0, {"document_type": "cv", "document_file": PDF})],
            "reference_ids": [(0, 0, {"name": "R", "relation": "colleague", "phone": "017"})],
        }
    )
    cand.with_user(x.recruiter).action_reject(reason="Not shortlisted")
    cand.sudo()._guarded().write({"retention_until": "2000-01-01"})
    x.env["fix.candidate"].cron_erase_expired_candidates()
    cand.invalidate_recordset()
    assert cand.erased
    assert not cand.education_ids and not cand.document_ids and not cand.reference_ids
    assert not cand.father_name and not cand.cv_file


# ======================================================== the /p03 form engine
def test_the_form_saves_several_grids_in_one_write(x, call):
    cand = _candidate(x, _requisition(x))
    env = x.env(user=x.recruiter.id)
    res = call(
        env,
        "model_write",
        model="fix.candidate",
        record_id=cand.id,
        values={"name": cand.name, "name_bn": "প্রার্থী"},
        grids=[
            {"field": "education_ids", "rows": [{"id": None, "values": _edu()}], "removed": []},
            {
                "field": "language_ids",
                "rows": [{"id": None, "values": {"language": "english", "reading": "fluent"}}],
                "removed": [],
            },
        ],
    )
    assert res.get("id") == cand.id, res
    assert cand.name_bn == "প্রার্থী"
    assert len(cand.education_ids) == 1 and len(cand.language_ids) == 1


def test_a_grid_refusal_leaves_nothing_behind(x, call):
    cand = _candidate(x, _requisition(x))
    env = x.env(user=x.recruiter.id)
    res = call(
        env,
        "model_write",
        model="fix.candidate",
        record_id=cand.id,
        values={"name_bn": "নাম"},
        grids=[
            {"field": "education_ids", "rows": [{"values": _edu(result=9.9)}], "removed": []},
        ],
    )
    assert res.get("error"), res
    cand.invalidate_recordset()
    assert not cand.name_bn and not cand.education_ids


def test_a_stored_file_is_served_as_a_link_and_kept_on_resave(x, call):
    cand = _candidate(x, _requisition(x))
    cand.with_user(x.recruiter).write({"education_ids": [(0, 0, _edu())]})
    env = x.env(user=x.recruiter.id)
    grid = {
        "field": "education_ids",
        "fields": [
            {"name": n}
            for n in (
                "exam_title",
                "certificate_file",
                "certificate_filename",
                "verification_state",
            )
        ],
    }
    res = _form_fields(call, env, "fix.candidate", ["name"], cand.id, [grid])
    row = res["grids"]["education_ids"]["rows"][0]
    cell = row["certificate_file"]
    assert cell["stored"] and cell["filename"] == "hsc.pdf"
    assert "/web/content/fix.candidate.education/" in cell["url"]
    meta = {m["name"]: m for m in res["grids"]["education_ids"]["fields"]}
    assert meta["verification_state"]["readonly"]
    sha = cand.education_ids.evidence_sha256
    # the echo of the link (and an unchanged title) rewrites nothing
    res = call(
        env,
        "model_write",
        model="fix.candidate",
        record_id=cand.id,
        values={},
        grids=[
            {"field": "education_ids", "rows": [{"id": row["id"], "values": row}], "removed": []}
        ],
    )
    assert res.get("id"), res
    assert cand.education_ids.evidence_sha256 == sha


def test_a_grid_the_screen_does_not_offer_is_refused(x, call):
    cand = _candidate(x, _requisition(x))
    res = call(
        x.env(user=x.recruiter.id),
        "model_write",
        model="fix.candidate",
        record_id=cand.id,
        values={},
        grids=[{"field": "message_ids", "rows": [], "removed": []}],
    )
    assert "does not edit" in (res.get("error") or ""), res


def test_a_separated_candidate_stays_separated_on_the_employee(x):
    """M58-F18: the hire coerced "Separated" to "Single" because hr.version had
    no such value, silently changing a status the service book records. The
    employee master holds the value the candidate declared."""
    req = _requisition(x)
    cand, offer = _ready_to_hire(x, req)
    # marital status is collected from the offer stage (data minimisation)
    cand.with_user(x.recruiter).write({"marital_status": "separated"})
    _accept(x, offer)
    assert cand.state == "hired"
    emp = cand.employee_id.sudo()
    assert emp.marital == "separated"
    choices = dict(emp._fields["marital"]._description_selection(x.env))
    assert choices["separated"] == "Separated"
    # a married candidate is untouched by the change
    req2 = _requisition(x)
    cand2, offer2 = _ready_to_hire(x, req2)
    cand2.with_user(x.recruiter).write({"marital_status": "married"})
    _accept(x, offer2)
    assert cand2.employee_id.sudo().marital == "married"
