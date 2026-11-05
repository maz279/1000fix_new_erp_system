# A09 M58 round-2 acceptance suite: interview panel independence
# (BRU-TAO-07), the M22 competency baseline (BRU-TAO-12), the headcount
# budget (BRU-TAO-01) and position seats (BRU-HCM-10), the generated
# appointment letter (M24, BLA 2006 s.5), onboarding tasks (FR-TAO-027) and
# hiring-manager scoping (M58-F7).
#
# Same standard as test_a09_talent_controls.py, whose fixtures and helpers
# this file reuses: every attack runs as a freshly created NON-admin user,
# writes go through call_kw and the real /p03 controller.
import base64
import contextlib
from datetime import timedelta
from unittest import mock

import pytest
from odoo import fields
from odoo.addons.cd_hr_core.tests.residency_memory import install
from odoo.addons.cd_p03_portal.controllers import a09
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_talent.tests.test_a09_talent_controls import (
    _SEQ,
    EVIDENCE,
    REFUSED,
    FakeRequest,
    _accept,
    _attest,
    _candidate,
    _cleared_check,
    _decide,
    _evaluate,
    _finish_tasks,
    _hired_plan,
    _interviewed,
    _offer,
    _ready_to_hire,
    _requisition,
    _rpc_write,
    _user,
    make_x,
)
from odoo.exceptions import AccessError, UserError, ValidationError


@pytest.fixture
def x(odoo_env):
    return make_x(odoo_env)


@pytest.fixture
def call():
    patchers = []

    def _call(env, route, **kw):
        p = mock.patch.object(api, "request", FakeRequest(env))
        p.start()
        patchers.append(p)
        return getattr(api.P03GenericApiController(), route)(**kw)

    yield _call
    for p in patchers:
        p.stop()


def _shortlisted(x):
    req = _requisition(x)
    cand = _candidate(x, req)
    cand.with_user(x.recruiter).action_screen()
    cand.with_user(x.recruiter).action_interview()
    return cand


def _panel(x, cand, *panelists):
    """A scheduled round with the lead interviewer plus `panelists` (users)."""
    iv = x.env(user=x.recruiter.id)["fix.talent.interview"].create(
        {
            "candidate_id": cand.id,
            "scheduled_on": fields.Datetime.now(),
            "interviewer_id": x.interviewer.id,
        }
    )
    for user in panelists:
        emp = x.env["hr.employee"].create({"name": user.name, "user_id": user.id})
        iv.with_user(x.recruiter).action_add_panelist(panelist=str(emp.id))
    return iv


# ============================================ panel independence (BRU-TAO-07)
def test_a_panelist_reads_and_writes_only_their_own_evaluation(x):
    cand = _shortlisted(x)
    second = _user(x.env)
    iv = _panel(x, cand, second)
    assert iv.panel_size == 2
    Ev = x.env["fix.talent.evaluation"]
    mine = Ev.with_user(x.panel_user).search([("interview_id", "=", iv.id)])
    theirs = Ev.sudo().search([("interview_id", "=", iv.id)]) - mine
    assert len(mine) == 1 and len(theirs) == 1
    with pytest.raises(AccessError):
        theirs.with_user(x.panel_user).read(["score"])
    with pytest.raises(AccessError):
        _rpc_write(x.env, x.panel_user, theirs, {"score": 1.0})
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, x.panel_user, mine, {"state": "submitted"})
    with pytest.raises(AccessError):
        x.env(user=x.panel_user.id)["fix.talent.evaluation"].create(
            {"interview_id": iv.id, "panelist_id": x.interviewer.id}
        )
    # an employee off the panel reads nothing
    assert not Ev.with_user(x.plain).search([("interview_id", "=", iv.id)])


def test_recruiter_sees_no_evaluation_until_every_panelist_submitted(x):
    cand = _shortlisted(x)
    second = _user(x.env)
    iv = _panel(x, cand, second)
    Ev = x.env["fix.talent.evaluation"]
    _evaluate(x, iv, x.panel_user, score=5.0, recommendation="strong_yes")
    iv.invalidate_recordset()
    # one of two submitted: nothing is visible, not even a partial result
    assert not Ev.with_user(x.recruiter).search([("interview_id", "=", iv.id)])
    assert not Ev.with_user(x.hrmgr).search([("interview_id", "=", iv.id)])
    assert iv.panel_submitted == 1 and not iv.panel_complete
    assert not iv.recommendation and not iv.score
    with pytest.raises(UserError, match="1 of 2 panelists"):
        iv.with_user(x.recruiter).action_done()
    # nor does the second panelist see the first one's evaluation
    assert len(Ev.with_user(second).search([("interview_id", "=", iv.id)])) == 1
    _evaluate(x, iv, second, score=3.0, recommendation="yes")
    iv.invalidate_recordset()
    assert iv.panel_complete and iv.recommendation == "yes" and iv.score == 4.0
    assert len(Ev.with_user(x.recruiter).search([("interview_id", "=", iv.id)])) == 2
    iv.with_user(x.recruiter).action_done()
    assert iv.state == "done"


def test_a_submitted_evaluation_is_final_and_a_strong_no_vetoes(x):
    cand = _shortlisted(x)
    second = _user(x.env)
    iv = _panel(x, cand, second)
    mine = _evaluate(x, iv, x.panel_user, recommendation="strong_yes")
    with pytest.raises(REFUSED):
        _rpc_write(x.env, x.panel_user, mine, {"recommendation": "no"})
    with pytest.raises(UserError, match="already submitted"):
        mine.with_user(x.panel_user).action_submit()
    _evaluate(x, iv, second, score=1.0, recommendation="strong_no")
    iv.invalidate_recordset()
    assert iv.recommendation == "strong_no"
    iv.with_user(x.recruiter).action_done()
    with pytest.raises(UserError, match="Strong No"):
        cand.with_user(x.recruiter).action_offer()


def test_the_recruiter_cannot_type_the_panel_result(x):
    cand = _shortlisted(x)
    iv = _panel(x, cand)
    with contextlib.suppress(*REFUSED):
        _rpc_write(x.env, x.recruiter, iv, {"recommendation": "strong_yes", "score": 5})
    iv.invalidate_recordset()
    assert not iv.recommendation and not iv.score
    with pytest.raises(UserError, match="0 of 1 panelists"):
        iv.with_user(x.recruiter).action_done()


def test_a_panelist_who_submitted_stays_on_the_panel(x):
    cand = _shortlisted(x)
    second = _user(x.env)
    iv = _panel(x, cand, second)
    _evaluate(x, iv, second)
    emp = second.employee_ids[:1]
    with pytest.raises(UserError, match="stays on its panel"):
        iv.with_user(x.recruiter).action_remove_panelist(panelist=str(emp.id))


# ============================================ M22 baseline (BRU-TAO-12)
def _competency(x, code="A09-SMT"):
    return x.env["fix.competency"].sudo().create({"code": code, "name": "A09 Smartphone board"})


def _field_hire_with_assessment(x, competency=None):
    req = _requisition(x, field_role=True)
    cand = _candidate(x, req)
    _interviewed(x, cand)
    vals = {"candidate_id": cand.id, "score": 82.0, "level": "l3", "assessor_id": x.interviewer.id}
    if competency:
        vals["competency_id"] = competency.id
    asmt = x.env(user=x.recruiter.id)["fix.talent.assessment"].create(vals)
    cand.with_user(x.recruiter).action_offer()
    for kind in ("nid", "reference", "police"):
        _cleared_check(x, cand, kind)
    offer = _offer(x, cand)
    _decide(offer, x.hrmgr, x.offer_approver)
    return cand, offer, asmt


def test_the_passed_assessment_becomes_the_m22_baseline_at_hire(x):
    comp = _competency(x)
    cand, offer, asmt = _field_hire_with_assessment(x, comp)
    assert asmt.passed and asmt.competency_code == comp.code
    _accept(x, offer)
    emp = cand.employee_id
    baseline = x.env["fix.competency.assessment"].sudo().search([("employee_id", "=", emp.id)])
    assert len(baseline) == 1 and asmt.baseline_id == baseline
    assert baseline.competency_id == comp and baseline.score == 82.0
    assert baseline.level == "l3" and baseline.assessor_id == x.interviewer
    # the baseline is the record: neither side is edited afterwards
    with pytest.raises(UserError, match="baseline"):
        _rpc_write(x.env, x.recruiter, asmt, {"score": 99.0})
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, x.recruiter, asmt, {"baseline_id": False})


def test_a_passed_assessment_with_no_m22_competency_blocks_the_hire(x):
    _cand, offer, _asmt = _field_hire_with_assessment(x)
    with pytest.raises(UserError, match="names no M22 competency"):
        _accept(x, offer)


# ============================================ headcount budget (BRU-TAO-01)
def _budget(x, headcount, position=None, approve=True):
    budget = x.env(user=x.recruiter.id)["fix.headcount.budget"].create(
        {
            "position_id": (position or x.position).id,
            "approved_headcount": headcount,
            "basis": "FY plan line 12",
        }
    )
    if approve:
        _decide(budget, x.recruiter, x.cfo)
        assert budget.state == "approved" and budget.approved_by_id == x.cfo
    return budget


def test_the_headcount_budget_is_approved_by_the_cfo_tier_not_its_requester(x):
    both = _user(x.env, "cd_talent.group_talent", "cd_entity_config.group_dofa_tier_4")
    budget = x.env(user=both.id)["fix.headcount.budget"].create(
        {"position_id": x.position.id, "approved_headcount": 3, "basis": "plan"}
    )
    with pytest.raises(REFUSED):
        budget.with_user(both).action_approve()
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, both, budget, {"state": "approved"})
    budget.with_user(both).action_request_approval()
    assigned = budget.approval_request_id.task_ids.mapped("assigned_user_id")
    assert both not in assigned and x.cfo in assigned and x.approver not in assigned


def test_an_approved_budget_figure_is_frozen(x):
    budget = _budget(x, 4)
    with pytest.raises(UserError, match="a new figure is a new budget"):
        _rpc_write(x.env, x.recruiter, budget, {"approved_headcount": 40})


def test_a_requisition_beyond_the_budget_is_refused_unless_routed_to_the_cfo(x):
    _budget(x, 1)
    req = _requisition(x, openings=2, approve=False)
    with pytest.raises(UserError, match="over-budget justification"):
        req.with_user(x.recruiter).action_request_approval()
    assert req.approval_state == "none"
    req.with_user(x.recruiter).write({"over_budget_reason": "Eid surge, two extra technicians"})
    req.with_user(x.recruiter).action_request_approval()
    assert req.over_budget and req.budget_id
    assigned = req.approval_request_id.task_ids.mapped("assigned_user_id")
    assert x.cfo in assigned and x.approver not in assigned
    task = req.approval_request_id.task_ids.filtered(lambda t: t.assigned_user_id == x.cfo)
    task.with_user(x.cfo).action_approve()
    assert req.state == "open" and req.approved_by_id == x.cfo


def test_a_requisition_within_the_budget_goes_to_the_requisition_approver(x):
    _budget(x, 5)
    req = _requisition(x, openings=2)  # decided by x.approver inside the helper
    assert not req.over_budget and req.budget_id and req.approved_by_id == x.approver
    # the next one would take the position to 6 of 5
    nxt = _requisition(x, openings=4, approve=False)
    with pytest.raises(UserError, match="headcount budget of 5"):
        nxt.with_user(x.recruiter).action_request_approval()


def test_the_budget_is_read_again_at_the_decision(x):
    _budget(x, 2)
    first = _requisition(x, openings=2, approve=False)
    first.with_user(x.recruiter).action_request_approval()
    second = _requisition(x, openings=1, approve=False)
    with pytest.raises(UserError, match="headcount budget of 2"):
        second.with_user(x.recruiter).action_request_approval()


def test_no_budget_blocks_only_when_the_setting_requires_one(x):
    req = _requisition(x, approve=False)
    x.env["ir.config_parameter"].sudo().set_param("cd_talent.require_headcount_budget", "1")
    with pytest.raises(UserError, match="no approved headcount budget"):
        req.with_user(x.recruiter).action_request_approval()
    x.env["ir.config_parameter"].sudo().set_param("cd_talent.require_headcount_budget", "0")
    req.with_user(x.recruiter).action_request_approval()
    assert req.approval_state == "pending"


def test_a_requisition_cannot_ask_for_seats_the_position_does_not_have(x):
    small = x.env["fix.org.position"].create(
        {"name": "A09 M58 Bench Lead", "grade": "A09T1", "headcount": 1}
    )
    req = x.env(user=x.recruiter.id)["fix.job.requisition"].create(
        {"name": "A09 seats", "position_id": small.id, "openings": 2}
    )
    with pytest.raises(UserError, match="free seat"):
        req.with_user(x.recruiter).action_request_approval()


# ============================================ appointment letter (M24, BLA s.5)
def test_the_appointment_letter_is_generated_at_hire_from_the_offer(x):
    plan = _hired_plan(x)
    letter = plan.appointment_letter_id.sudo()
    assert letter and letter.doc_type == "appointment" and letter.generated
    assert letter.employee_id == plan.employee_id and not letter.acknowledged
    text = base64.b64decode(letter.file_data).decode()
    assert "30,000.00" in text and "18,000.00" in text and plan.offer_id.name in text
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, x.recruiter, plan, {"appointment_ack_method": "employee"})


def test_nobody_acknowledges_the_letter_for_the_employee(x):
    plan = _hired_plan(x)
    with pytest.raises(AccessError):
        plan.with_user(x.recruiter).action_acknowledge_appointment()
    with pytest.raises(UserError, match="Attach the appointment letter signed"):
        plan.with_user(x.verifier).action_attest_signed_appointment()
    with pytest.raises(AccessError):  # the recruiter is no verifier
        plan.with_user(x.recruiter).action_attest_signed_appointment()
    # a verifier who uploads the signed copy does not attest it
    plan.with_user(x.recruiter).write({"signed_contract_file": EVIDENCE})
    plan.sudo()._guarded().write({"signed_contract_uploaded_by_id": x.verifier.id})
    with pytest.raises(UserError, match="another verifier"):
        plan.with_user(x.verifier).action_attest_signed_appointment()
    plan.with_user(x.verifier2).action_attest_signed_appointment()
    letter = plan.appointment_letter_id.sudo()
    assert letter.acknowledged and letter.verified and not letter.generated
    assert plan.appointment_ack_method == "signed_counterpart" and plan.contract_signed
    assert plan.appointment_ack_attested_by_id == x.verifier2
    with pytest.raises(UserError, match="is a record"):
        plan.with_user(x.recruiter).write(
            {"signed_contract_file": base64.b64encode(b"another scan").decode()}
        )


def test_the_uploader_is_stamped_from_the_session_not_typed(x):
    plan = _hired_plan(x)
    _rpc_write(x.env, x.recruiter, plan, {"signed_contract_file": EVIDENCE})
    assert plan.signed_contract_uploaded_by_id == x.recruiter
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, x.recruiter, plan, {"signed_contract_uploaded_by_id": x.plain.id})


def test_an_employee_with_a_login_acknowledges_their_own_letter(x):
    plan = _hired_plan(x)
    joiner = _user(x.env)
    plan.employee_id.sudo().write({"user_id": joiner.id})
    plan.with_user(joiner).action_acknowledge_appointment()
    assert plan.appointment_ack_method == "employee" and plan.contract_signed
    assert plan.appointment_letter_id.sudo().acknowledged


# ============================================ onboarding tasks (FR-TAO-027)
def test_hire_generates_the_template_tasks_with_owners_and_due_dates(x):
    hm = _user(x.env, "cd_talent.group_hiring_manager")
    req = _requisition(x, approve=False)
    req.with_user(x.recruiter).write({"hiring_manager_id": hm.id})
    _decide(req, x.recruiter, x.approver)
    cand, offer = _ready_to_hire(x, req)
    _accept(x, offer)
    plan = x.env["fix.onboarding.plan"].search([("candidate_id", "=", cand.id)])
    tasks = plan.task_ids
    # the default template: 3 mandatory + 2 optional (the safety induction is field-role only)
    assert len(tasks) == 5 and len(tasks.filtered("mandatory")) == 3
    assert set(tasks.mapped("owner_id")) == {hm}
    assert set(tasks.mapped("due_date")) == {plan.joined_date}
    plan._fix_generate_tasks()  # idempotent
    assert len(plan.task_ids) == 5


def test_only_the_owner_completes_a_task_on_its_evidence(x):
    plan = _hired_plan(x)
    task = plan.task_ids.filtered("mandatory")[:1]
    owner = task.owner_id
    assert owner == x.hrmgr  # no hiring manager: whoever made the hire
    other = _user(x.env, "cd_talent.group_talent")
    with pytest.raises(AccessError):
        task.with_user(other).action_done()
    with pytest.raises(UserError, match="completion evidence"):
        task.with_user(owner).action_done()
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, owner, task, {"state": "done"})
    with pytest.raises(UserError, match="never cancelled"):
        task.with_user(x.recruiter).action_cancel(reason="not needed")
    _rpc_write(x.env, owner, task, {"evidence_note": "Account created, login tested"})
    task.with_user(owner).action_done()
    assert task.state == "done" and task.completed_by_id == owner
    with pytest.raises(UserError, match="is a record"):
        _rpc_write(x.env, owner, task, {"evidence_note": "edited"})


def test_a_task_owner_records_evidence_but_does_not_replan_the_task(x):
    plan = _hired_plan(x)
    it = _user(x.env)
    task = plan.task_ids.filtered("mandatory")[:1]
    task.with_user(x.recruiter).write({"owner_id": it.id})
    assert task.with_user(it).read(["name"])  # the owner reads their task
    with pytest.raises(AccessError):
        _rpc_write(x.env, it, task, {"due_date": str(x.today + timedelta(days=90))})
    _rpc_write(x.env, it, task, {"evidence_note": "Laptop FX-221 issued"})
    task.with_user(it).action_done()
    # someone else's task is not even visible to them
    others = plan.task_ids - task
    assert not x.env(user=it.id)["fix.onboarding.task"].search([("id", "in", others.ids)])


def test_onboarding_completes_once_letter_and_mandatory_tasks_are_done(x):
    plan = _hired_plan(x)
    _attest(x, plan)
    optional = plan.task_ids.filtered(lambda t: not t.mandatory)
    optional.with_user(x.recruiter).action_cancel(reason="Mentor programme paused")
    _finish_tasks(x, plan)
    emp = plan.employee_id.sudo()
    emp.write(
        {
            "bank_account_number": "1234567890123",
            "routing_number": "123456789",
            "employee_code": "E-A09-R2-%d" % next(_SEQ),
        }
    )
    plan.with_user(x.recruiter).action_complete()
    assert plan.state == "completed"
    # the M21 dossier now sees the verified, acknowledged letter
    emp.invalidate_recordset(["doc_appointment_signed"])
    assert emp.doc_appointment_signed


# ============================================ hiring-manager scoping (M58-F7)
def _hm_requisition(x, hm):
    req = x.env(user=hm.id)["fix.job.requisition"].create(
        {"name": "A09 HM REQ %d" % next(_SEQ), "position_id": x.position.id, "openings": 1}
    )
    assert req.hiring_manager_id == hm
    _decide(req, hm, x.approver)
    return req


def test_a_hiring_manager_sees_and_acts_only_on_their_own_requisitions(x, call):
    hm_a = _user(x.env, "cd_talent.group_hiring_manager")
    hm_b = _user(x.env, "cd_talent.group_hiring_manager")
    req_a, req_b = _hm_requisition(x, hm_a), _hm_requisition(x, hm_b)
    cand_a, cand_b = _candidate(x, req_a), _candidate(x, req_b)
    Req = x.env(user=hm_a.id)["fix.job.requisition"]
    assert Req.search([("id", "in", (req_a | req_b).ids)]).ids == req_a.ids
    Cand = x.env(user=hm_a.id)["fix.candidate"]
    assert Cand.search([("id", "in", (cand_a | cand_b).ids)]).ids == cand_a.ids
    with pytest.raises(AccessError):
        cand_b.with_user(hm_a).read(["email"])
    with pytest.raises(AccessError):
        cand_b.with_user(hm_a).action_screen()
    res = call(
        x.env(user=hm_a.id),
        "model_records",
        model="fix.job.requisition",
        cols=["name"],
        domain=[["id", "in", (req_a | req_b).ids]],
    )
    rows = res.get("records") or res.get("rows") or []
    assert [r["id"] for r in rows] == [req_a.id], res
    # their own candidate: screened and shortlisted by the hiring manager
    cand_a.with_user(hm_a).action_screen()
    cand_a.with_user(hm_a).action_interview()
    assert cand_a.state == "interview"
    # but never hired by them, and no requisition is raised for someone else
    with pytest.raises(AccessError):
        cand_a.with_user(hm_a).action_hire()
    with pytest.raises(AccessError):
        x.env(user=hm_a.id)["fix.job.requisition"].create(
            {"name": "A09 for B", "position_id": x.position.id, "hiring_manager_id": hm_b.id}
        )


def test_a_plain_employee_reads_no_requisition(x):
    req = _requisition(x)
    assert not x.env(user=x.plain.id)["fix.job.requisition"].search([("id", "=", req.id)])


# ============================================ deployment
def test_round_two_rules_acl_and_data_are_deployed(odoo_env):
    for xmlid in (
        "cd_talent.rule_job_requisition_scope",
        "cd_talent.rule_candidate_scope",
        "cd_talent.rule_talent_interview_scope",
        "cd_talent.rule_onboarding_plan_scope",
        "cd_talent.rule_talent_evaluation_read",
        "cd_talent.rule_talent_evaluation_write",
        "cd_talent.rule_onboarding_task_read",
        "cd_talent.rule_onboarding_task_write",
    ):
        rule = odoo_env.ref(xmlid)
        assert rule.active and rule["global"], xmlid
    for xmlid in (
        "cd_talent.access_fix_talent_evaluation_user",
        "cd_talent.access_fix_headcount_budget_role",
        "cd_talent.access_fix_headcount_budget_cfo",
        "cd_talent.access_fix_onboarding_task_user",
        "cd_talent.access_fix_onboarding_task_role",
        "cd_talent.access_fix_job_requisition_hm",
        "cd_talent.access_fix_candidate_hm",
    ):
        assert odoo_env.ref(xmlid).perm_read, xmlid
    holders = odoo_env.ref("cd_talent.group_hiring_manager").user_ids
    assert holders <= (odoo_env.ref("base.user_root") | odoo_env.ref("base.user_admin"))
    tpl = odoo_env.ref("cd_talent.onboarding_template_default")
    assert tpl.is_default and len(tpl.line_ids.filtered("mandatory")) == 4
    assert odoo_env.ref("cd_talent.param_require_headcount_budget").value == "0"
    for model in ("fix.talent.evaluation", "fix.headcount.budget", "fix.onboarding.task"):
        assert model in a09.SURFACES and a09.SURFACES[model]["rules"]
        for method in a09.SURFACES[model]["actions"]:
            assert callable(getattr(odoo_env[model], method, None)), (model, method)
    assert "action_approve" not in a09.SURFACES["fix.headcount.budget"]["actions"]
    assert "action_submit" in a09.SURFACES["fix.talent.evaluation"]["actions"]


# ============================================ candidate NID (M21 residency move)
def _clear_nid(x, cand):
    x.env.flush_all()
    x.env.cr.execute("SELECT nid_number, nid_hash FROM fix_candidate WHERE id = %s", (cand.id,))
    return x.env.cr.fetchone()


def test_the_hire_leaves_no_clear_candidate_nid_and_duplicates_are_still_found(x, monkeypatch):
    # the employee NID now lives in the residency store (A09 M21-A6); the
    # local store answers synthetic values only, so the test stands in the
    # in-memory store to read the copied value back
    install(monkeypatch)
    nid = "1990123456789"
    req = _requisition(x, openings=2)
    cand, offer = _ready_to_hire(x, req, nid_number=nid)
    clear, digest = _clear_nid(x, cand)
    assert clear == nid and digest and nid not in digest
    _accept(x, offer)
    clear, digest_after = _clear_nid(x, cand)
    assert clear is None and digest_after == digest
    assert cand.employee_id.sudo().nid_number == nid
    # a second application with the same NID is still recognised (by its hash)
    with pytest.raises(ValidationError, match="already applied"):
        _candidate(x, req, nid_number=nid)
    # and the hired candidate's NID is never typed back in
    with pytest.raises(UserError, match="employee master"):
        _rpc_write(x.env, x.recruiter, cand, {"nid_number": nid})


def test_erasure_leaves_no_candidate_nid_or_hash(x):
    x.env["ir.config_parameter"].sudo().set_param("cd_talent.candidate_retention_days", "30")
    req = _requisition(x)
    cand = _candidate(x, req, nid_number="19901234567890123")
    cand.with_user(x.recruiter).action_reject(reason="Not selected")
    cand.sudo()._guarded().write({"retention_until": x.today - timedelta(days=1)})
    x.env["fix.candidate"].cron_erase_expired_candidates()
    assert _clear_nid(x, cand) == (None, None)


def test_the_nid_hash_is_the_m21_keyed_hash_and_never_typed(x):
    import hashlib
    import hmac

    req = _requisition(x)
    cand = _candidate(x, req, nid_number="1234567890")
    key = x.env["ir.config_parameter"].sudo().get_param("cd_hr_core.identity_hash_key")
    assert key
    expected = hmac.new(key.encode(), b"nid:1234567890", hashlib.sha256).hexdigest()
    assert cand.sudo().nid_hash == expected
    with pytest.raises(REFUSED):
        _rpc_write(x.env, x.recruiter, cand, {"nid_hash": "forged"})


def test_the_migration_hashes_candidate_nids_and_erases_hired_ones(x):
    import importlib.util
    from pathlib import Path

    req = _requisition(x)
    cand = _candidate(x, req)
    emp = x.env["hr.employee"].create({"name": "A09 migrated hire"})
    x.env.flush_all()
    x.env.cr.execute(
        "UPDATE fix_candidate SET nid_number = '1234509876', nid_hash = NULL, state = 'hired', "
        "employee_id = %s WHERE id = %s",
        (emp.id, cand.id),
    )
    x.env.invalidate_all()
    path = Path(__file__).resolve().parents[1] / "migrations" / "19.0.0.3.0" / "post-migrate.py"
    spec = importlib.util.spec_from_file_location("m", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.migrate(x.env.cr, "19.0.0.2.0")
    clear, digest = _clear_nid(x, cand)
    assert clear is None and digest


# ============================================ due and overdue tasks (AUT-TAO-13)
def _hm_plan(x):
    hm = _user(x.env, "cd_talent.group_hiring_manager")
    req = _requisition(x, approve=False)
    req.with_user(x.recruiter).write({"hiring_manager_id": hm.id})
    _decide(req, x.recruiter, x.approver)
    cand, offer = _ready_to_hire(x, req)
    _accept(x, offer)
    plan = x.env["fix.onboarding.plan"].search([("candidate_id", "=", cand.id)])
    return hm, plan


def test_a_due_task_tells_its_owner_then_escalates_once_overdue(x):
    hm, plan = _hm_plan(x)
    owner = _user(x.env)
    task = plan.task_ids.filtered("mandatory")[:1]
    # AUT-TAO-13 decides on the context date (env tz Asia/Dhaka); align with
    # it, or an 18:00-24:00 UTC run makes a due-today task already overdue.
    today = fields.Date.context_today(task)
    task.with_user(x.recruiter).write({"owner_id": owner.id, "due_date": str(today)})
    others = plan.task_ids - task
    others.sudo().write({"due_date": today + timedelta(days=30)})
    Task = x.env["fix.onboarding.task"]
    assert Task.cron_notify_due_tasks() >= 1
    assert task.alert_level == 1
    assert task.activity_ids.mapped("user_id") == owner
    count = len(task.activity_ids)
    Task.cron_notify_due_tasks()
    assert len(task.activity_ids) == count  # idempotent
    task.sudo().write({"due_date": today - timedelta(days=2)})
    Task.cron_notify_due_tasks()
    assert task.alert_level == 2 and hm in task.activity_ids.mapped("user_id")
    count = len(task.activity_ids)
    Task.cron_notify_due_tasks()
    assert len(task.activity_ids) == count
    assert all(t.alert_level == 0 for t in others)  # not yet due
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, x.recruiter, task, {"alert_level": 0})


def test_an_overdue_task_with_no_hiring_manager_goes_to_hr(x):
    plan = _hired_plan(x)
    task = plan.task_ids.filtered("mandatory")[:1]
    task.sudo().write({"due_date": x.today - timedelta(days=1)})
    x.env["fix.onboarding.task"].cron_notify_due_tasks()
    assert task.alert_level == 2
    assert x.hrmgr in task.activity_ids.mapped("user_id")


def test_a_done_task_is_never_chased(x):
    plan = _hired_plan(x)
    task = plan.task_ids.filtered("mandatory")[:1]
    owner = task.owner_id
    _rpc_write(x.env, owner, task, {"evidence_note": "Done early"})
    task.with_user(owner).action_done()
    task.sudo()._guarded().write({"due_date": x.today - timedelta(days=5)})
    x.env["fix.onboarding.task"].cron_notify_due_tasks()
    assert task.alert_level == 0 and not task.activity_ids


def test_the_onboarding_task_cron_is_deployed(odoo_env):
    cron = odoo_env.ref("cd_talent.cron_talent_onboarding_task_alerts")
    assert cron.active and cron.user_id == odoo_env.ref("base.user_root")
    assert cron.code.strip() == "model.cron_notify_due_tasks()"
