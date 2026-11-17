# M58 capture audit (2026-11-17): the records the M58 pages now capture, and
# the controls they carry, exercised as non-admin users on the ORM and
# through the real /p03 controller (fix_talent_capture.py).
import base64
import hashlib
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta
from odoo import fields
from odoo.addons.cd_talent.tests.test_a09_talent_controls import (
    _SEQ,
    EVIDENCE,
    _accept,
    _attest,
    _candidate,
    _finish_tasks,
    _hired_plan,
    _offer,
    _ready_to_hire,
    _requisition,
    _rpc_write,
    _user,
    _verify_documents,
    make_x,
)
from odoo.exceptions import AccessError, UserError, ValidationError


@pytest.fixture
def x(odoo_env):
    c = make_x(odoo_env)
    odoo_env["ir.config_parameter"].sudo().set_param("cd_talent.internal_consideration_days", "7")
    return c


def _channel(x, **vals):
    base = {"name": "A09 Portal %d" % next(_SEQ), "channel_type": "job_portal"}
    base.update(vals)
    return x.env(user=x.recruiter.id)["fix.recruitment.channel"].create(base)


def _posting(x, req, audience="internal", **vals):
    base = {"title": "Technician %d" % next(_SEQ), "requisition_id": req.id, "audience": audience}
    base.update(vals)
    return x.env(user=x.recruiter.id)["fix.job.posting"].create(base)


def _ready_plan(x):
    """A started plan with the letter attested, tasks done, bank and code set."""
    plan = _hired_plan(x)
    _attest(x, plan)
    _finish_tasks(x, plan)
    plan.employee_id.sudo().write(
        {
            "bank_account_number": "1234567890123",
            "routing_number": "123456789",
            "employee_code": "E-M58-%d" % next(_SEQ),
        }
    )
    return plan


# ===================================================================== postings
def test_no_posting_before_the_requisition_is_approved(x):
    req = _requisition(x, approve=False)
    post = _posting(x, req)
    with pytest.raises(UserError, match="BRU-TAO-02"):
        post.with_user(x.recruiter).action_publish()
    assert post.state == "draft"


def test_external_posting_waits_for_the_internal_window(x):
    req = _requisition(x)
    channel = _channel(x)
    ext = _posting(x, req, audience="external", channel_id=channel.id)
    with pytest.raises(UserError, match="posted internally first"):
        ext.with_user(x.recruiter).action_publish()
    internal = _posting(x, req)
    internal.with_user(x.recruiter).action_publish()
    assert internal.internal_only_until == fields.Date.today() + timedelta(days=7)
    with pytest.raises(UserError, match="internal only until"):
        ext.with_user(x.recruiter).action_publish()
    # the window elapsed
    internal.sudo()._guarded().write({"internal_only_until": fields.Date.today()})
    ext.with_user(x.recruiter).action_publish()
    assert ext.state == "published" and ext.published_by_id == x.recruiter


def test_published_posting_does_not_change_and_state_is_not_typed(x):
    req = _requisition(x)
    post = _posting(x, req)
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, x.recruiter, post, {"state": "published"})
    post.with_user(x.recruiter).action_publish()
    with pytest.raises(UserError, match="does not change"):
        _rpc_write(x.env, x.recruiter, post, {"title": "Something else"})


def test_a_hiring_manager_cannot_publish(x):
    hm = _user(x.env, "cd_talent.group_hiring_manager")
    req = _requisition(x)
    post = _posting(x, req)
    with pytest.raises(AccessError):
        post.with_user(hm).action_publish()


def test_candidate_posting_must_be_the_requisitions_and_published(x):
    req, other = _requisition(x), _requisition(x)
    post = _posting(x, req)
    with pytest.raises(ValidationError, match="never published"), x.env.cr.savepoint():
        _candidate(x, req, posting_id=post.id)
    post.with_user(x.recruiter).action_publish()
    with pytest.raises(ValidationError, match="not the candidate"), x.env.cr.savepoint():
        _candidate(x, other, posting_id=post.id)
    cand = _candidate(x, None, posting_id=post.id)
    assert cand.requisition_id == req
    assert post.candidate_count == 1


# ============================================================ channels and cost
def test_channel_cost_rules(x):
    with pytest.raises(ValidationError, match="names the agency"):
        _channel(x, channel_type="agency")
    with pytest.raises(ValidationError, match="agreed fee"):
        _channel(x, cost_model="per_hire")
    with pytest.raises(AccessError):
        x.env(user=x.plain.id)["fix.recruitment.channel"].create({"name": "X"})


def test_no_spend_on_an_unapproved_requisition_and_cost_per_hire(x):
    from odoo.addons.cd_p03_portal.controllers.a09 import m58

    draft = _requisition(x, approve=False)
    Cost = x.env(user=x.recruiter.id)["fix.recruitment.cost"]
    with pytest.raises(ValidationError, match="BRU-TAO-02"):
        Cost.create({"requisition_id": draft.id, "amount": 5000})
    cand, offer = _ready_to_hire(x)
    req = cand.requisition_id
    with pytest.raises(ValidationError, match="positive"):
        Cost.create({"requisition_id": req.id, "amount": 0})
    Cost.create({"requisition_id": req.id, "amount": 12000, "cost_type": "advertising"})
    _accept(x, offer)
    pack = m58.cost_per_hire(x.env)
    row = next(r for r in pack["rows"] if r["requisition"] == req.name)
    assert row["hires"] == 1 and row["cost_per_hire"] == 12000.0


# ===================================================================== referral
def test_referral_reward_is_approved_after_hire_by_another_hr_manager(x):
    referrer_user = _user(x.env)
    referrer = x.env["hr.employee"].create(
        {"name": "A09 Referrer", "user_id": referrer_user.id, "work_email": "ref@a09.test"}
    )
    cand, offer = _ready_to_hire(x)
    Ref = x.env(user=x.hrmgr.id)["fix.talent.referral"]
    ref = Ref.create(
        {"candidate_id": cand.id, "referring_employee_id": referrer.id, "reward_amount": 5000}
    )
    assert cand.source == "referral"
    with pytest.raises(UserError, match="already has a referral"):
        Ref.create({"candidate_id": cand.id, "referring_employee_id": referrer.id})
    other_hr = _user(x.env, "hr.group_hr_manager")
    with pytest.raises(UserError, match="not hired"):
        ref.with_user(other_hr).action_approve_reward()
    _accept(x, offer)
    with pytest.raises(UserError, match="another HR manager"):
        ref.with_user(x.hrmgr).action_approve_reward()
    with pytest.raises(AccessError):
        ref.with_user(x.recruiter).action_approve_reward()
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, x.hrmgr, ref, {"reward_state": "approved"})
    ref.with_user(other_hr).action_approve_reward()
    assert ref.reward_state == "approved" and ref.decided_by_id == other_hr
    with pytest.raises(UserError, match="decided"):
        _rpc_write(x.env, x.hrmgr, ref, {"reward_amount": 9000})


def test_self_referral_is_refused(x):
    emp = x.env["hr.employee"].create({"name": "A09 Self", "work_email": "self@a09.test"})
    cand = _candidate(x, _requisition(x), email="self@a09.test")
    with pytest.raises(ValidationError, match="self-referral"):
        x.env(user=x.recruiter.id)["fix.talent.referral"].create(
            {"candidate_id": cand.id, "referring_employee_id": emp.id}
        )


# ======================================================== pre-boarding documents
def test_the_hire_issues_the_document_checklist(x):
    plan = _hired_plan(x)
    kinds = set(plan.document_ids.mapped("document_type"))
    assert kinds == {"nid", "photo", "academic", "experience", "bank"}
    assert all(d.mandatory and d.state == "requested" for d in plan.document_ids)
    assert plan.documents_required == 5 and plan.documents_verified == 0


def test_document_is_verified_by_someone_other_than_its_uploader(x):
    plan = _hired_plan(x)
    doc = plan.document_ids.filtered(lambda d: d.document_type == "nid")
    with pytest.raises(UserError, match="no submitted document"):
        doc.with_user(x.verifier).action_verify()
    _rpc_write(x.env, x.recruiter, doc, {"document_file": EVIDENCE})
    assert doc.state == "submitted" and doc.uploaded_by_id == x.recruiter
    assert doc.file_sha256 == hashlib.sha256(base64.b64decode(EVIDENCE)).hexdigest()
    with pytest.raises(AccessError):
        doc.with_user(x.recruiter).action_verify()
    both = _user(x.env, "cd_talent.group_talent", "cd_talent.group_background_verifier")
    _rpc_write(x.env, both, doc, {"document_file": base64.b64encode(b"rescan").decode()})
    with pytest.raises(UserError, match="another verifier"):
        doc.with_user(both).action_verify()
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, x.recruiter, doc, {"state": "verified"})
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, x.recruiter, doc, {"mandatory": False})
    doc.with_user(x.verifier).action_verify()
    assert doc.state == "verified" and doc.verified_by_id == x.verifier
    with pytest.raises(UserError, match="verified"):
        _rpc_write(x.env, x.recruiter, doc, {"document_file": EVIDENCE[::-1] + "=="})


def test_rejected_document_goes_back_to_submitted_on_reupload(x):
    plan = _hired_plan(x)
    doc = plan.document_ids[:1]
    _rpc_write(x.env, x.recruiter, doc, {"document_file": EVIDENCE})
    with pytest.raises(UserError, match="what is wrong"):
        doc.with_user(x.verifier).action_reject(reason=" ")
    doc.with_user(x.verifier).action_reject(reason="Blurred scan")
    assert doc.state == "rejected" and doc.rejection_reason == "Blurred scan"
    _rpc_write(x.env, x.recruiter, doc, {"document_file": base64.b64encode(b"clear").decode()})
    assert doc.state == "submitted" and not doc.rejection_reason


def test_onboarding_waits_for_every_mandatory_document(x):
    plan = _ready_plan(x)
    with pytest.raises(UserError, match="5 mandatory pre-boarding document"):
        plan.with_user(x.recruiter).action_complete()
    _verify_documents(x, plan)
    plan.with_user(x.recruiter).action_complete()
    assert plan.state == "completed"


# ===================================================================== induction
def test_induction_is_recorded_by_its_conductor_after_it_starts(x):
    plan = _ready_plan(x)
    _verify_documents(x, plan)
    conductor = _user(x.env)
    Ind = x.env(user=x.recruiter.id)["fix.onboarding.induction"]
    later = Ind.create(
        {
            "plan_id": plan.id,
            "session_type": "safety",
            "scheduled_at": fields.Datetime.now() + timedelta(days=2),
            "conductor_id": conductor.id,
        }
    )
    with pytest.raises(AccessError):
        x.env(user=conductor.id)["fix.onboarding.induction"].create(
            {
                "plan_id": plan.id,
                "scheduled_at": fields.Datetime.now(),
                "conductor_id": conductor.id,
            }
        )
    with pytest.raises(UserError, match="not started yet"):
        later.with_user(conductor).action_mark_attended()
    with pytest.raises(UserError, match="induction session"):
        plan.with_user(x.recruiter).action_complete()
    later.sudo().write({"scheduled_at": fields.Datetime.now() - timedelta(hours=1)})
    with pytest.raises(AccessError):
        later.with_user(x.recruiter).action_mark_attended()
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, conductor, later, {"state": "attended"})
    later.with_user(conductor).action_mark_attended()
    assert later.state == "attended" and later.recorded_by_id == conductor
    plan.with_user(x.recruiter).action_complete()


def test_field_hire_who_missed_the_safety_induction_does_not_complete(x):
    req = _requisition(x, field_role=True)
    plan = _ready_plan_for(x, req)
    _verify_documents(x, plan)
    conductor = _user(x.env)
    ind = x.env(user=x.recruiter.id)["fix.onboarding.induction"].create(
        {
            "plan_id": plan.id,
            "session_type": "safety",
            "scheduled_at": fields.Datetime.now() - timedelta(hours=2),
            "conductor_id": conductor.id,
        }
    )
    ind.with_user(conductor).action_mark_missed(reason="Did not turn up")
    problems = plan.sudo()._fix_completion_problems()
    assert any("safety induction" in p for p in problems)


def _ready_plan_for(x, req):
    from odoo.addons.cd_talent.tests.test_a09_talent_controls import _cleared_check

    cand, offer = _ready_to_hire_on(x, req, _cleared_check)
    _accept(x, offer)
    plan = x.env["fix.onboarding.plan"].search([("candidate_id", "=", cand.id)])
    plan.with_user(x.recruiter).action_start()
    return plan


def _ready_to_hire_on(x, req, _cleared_check):
    from odoo.addons.cd_talent.tests.test_a09_talent_controls import _decide, _interviewed

    cand = _candidate(x, req)
    _interviewed(x, cand)
    x.env(user=x.recruiter.id)["fix.talent.assessment"].create(
        {"candidate_id": cand.id, "score": 80, "competency_id": _competency(x).id}
    )
    cand.with_user(x.recruiter).action_offer()
    for kind in ("nid", "reference", "police"):
        _cleared_check(x, cand, kind)
    offer = _offer(x, cand)
    _decide(offer, x.hrmgr, x.offer_approver)
    return cand, offer


def _competency(x):
    Comp = x.env["fix.competency"].sudo()
    return Comp.search([], limit=1) or Comp.create(
        {"name": "A09 Bench", "code": "A09B%d" % next(_SEQ)}
    )


# ============================================================ task dependency
def test_a_dependent_task_waits_for_its_prerequisite(x):
    plan = _hired_plan(x)
    owner = x.recruiter
    Task = x.env(user=x.recruiter.id)["fix.onboarding.task"]
    first = Task.create(
        {
            "plan_id": plan.id,
            "name": "Issue laptop",
            "owner_id": owner.id,
            "due_date": fields.Date.today(),
        }
    )
    second = Task.create(
        {
            "plan_id": plan.id,
            "name": "Install apps",
            "owner_id": owner.id,
            "due_date": fields.Date.today(),
            "depends_on_id": first.id,
        }
    )
    assert not first.mandatory and not second.mandatory
    _rpc_write(x.env, owner, second, {"evidence_note": "done"})
    with pytest.raises(UserError, match="waits for"):
        second.with_user(owner).action_done()
    _rpc_write(x.env, owner, first, {"evidence_note": "done"})
    first.with_user(owner).action_done()
    second.with_user(owner).action_done()
    with pytest.raises(ValidationError, match="loop"):
        first.sudo().write({"depends_on_id": second.id})
    other = _hired_plan(x)
    with pytest.raises(UserError, match="does not move"):
        _rpc_write(x.env, x.recruiter, second, {"plan_id": other.id})


# ==================================================== assessment, offer, profile
def test_assessment_evidence_freezes_with_the_baseline(x):
    cand = _candidate(x, _requisition(x))
    asmt = x.env(user=x.recruiter.id)["fix.talent.assessment"].create(
        {
            "candidate_id": cand.id,
            "score": 70,
            "competency_id": _competency(x).id,
            "tasks_performed": "Replaced a charging port",
            "evidence_file": EVIDENCE,
        }
    )
    assert asmt.tasks_performed and asmt.evidence_file
    baseline = (
        x.env["fix.competency.assessment"]
        .sudo()
        .create({"employee_id": x.interviewer.id, "competency_id": _competency(x).id})
    )
    asmt.sudo()._guarded().write({"baseline_id": baseline.id})
    with pytest.raises(UserError, match="baseline"):
        _rpc_write(x.env, x.recruiter, asmt, {"tasks_performed": "Other"})


def test_offer_probation_is_capped_and_reaches_the_contract_and_letter(x):
    cand, offer = _ready_to_hire(x)
    with pytest.raises(ValidationError, match="at most 3 months"):
        _offer(x, cand).write({"probation_class": "skilled", "probation_months": 6})
    assert offer.probation_months == 6
    _accept(x, offer)
    plan = x.env["fix.onboarding.plan"].search([("candidate_id", "=", cand.id)])
    contract = plan.contract_id.sudo()
    assert contract.probation_end == offer.joining_date + relativedelta(months=6, days=-1)
    letter = base64.b64decode(plan.appointment_letter_id.sudo().file_data).decode()
    assert "Probation period: 6 month(s)" in letter


def test_probation_offer_without_a_period_is_not_issued(x):
    cand, _offer_issued = _ready_to_hire(x)
    draft = _offer(x, cand)
    draft.write({"probation_months": 0})
    assert any("probation period" in p for p in draft._fix_issue_problems())


def test_job_profile_is_the_requisitions_position(x):
    other = x.env["fix.org.position"].create({"name": "A09 Other", "headcount": 5})
    prof = x.env(user=x.recruiter.id)["fix.job.profile"].create(
        {"name": "Bench Tech", "position_id": other.id, "responsibilities": "Repairs"}
    )
    with pytest.raises(ValidationError, match="is for position"):
        x.env(user=x.recruiter.id)["fix.job.requisition"].create(
            {"name": "REQ P", "position_id": x.position.id, "job_profile_id": prof.id}
        )
    with pytest.raises(AccessError):
        x.env(user=x.plain.id)["fix.job.profile"].create({"name": "X", "responsibilities": "Y"})


# =============================================================== workspace path
def test_workspace_writes_through_the_whitelist(x):
    """The page's forms save through /p03/model/write as the recruiter."""
    from unittest import mock

    from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
    from odoo.addons.cd_talent.tests.test_a09_talent_controls import FakeRequest

    req = _requisition(x)
    with mock.patch.object(api, "request", FakeRequest(x.env(user=x.recruiter.id))):
        res = api.P03GenericApiController().model_write(
            model="fix.job.posting",
            record_id=None,
            values={"title": "Field Tech", "requisition_id": req.id, "audience": "internal"},
        )
    assert res.get("id"), res
    post = x.env["fix.job.posting"].browse(res["id"])
    assert post.title == "Field Tech" and post.state == "draft"


def test_day_one_readiness_lists_what_is_missing(x):
    from odoo.addons.cd_p03_portal.controllers.a09 import m58

    plan = _hired_plan(x)
    pack = m58.day_one_readiness(x.env)
    row = next(r for r in pack["rows"] if r["plan"] == plan.name)
    assert "pre-boarding document" in row["missing"] and row["outstanding"] >= 1


def test_evaluations_are_never_created_by_hand(x):
    with pytest.raises(AccessError, match="naming the panelist"):
        x.env(user=x.recruiter.id)["fix.talent.evaluation"].create({})
