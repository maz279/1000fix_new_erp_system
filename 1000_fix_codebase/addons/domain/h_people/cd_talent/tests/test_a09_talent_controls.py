# A09 M58 acceptance suite (A09 workflow audit B1-B6, C5, I6, I7; findings
# M58-F1..F14, working/A09_evidence/module_findings/M58.md).
#
# Every attack runs as a freshly created NON-admin user and asserts the
# refusal; then the proper path is walked by the right roles: the recruiter
# raises, a Requisition Approver opens, a Background Verifier clears, an HR
# manager drafts the offer, an Offer Approver (or the CFO tier out of band)
# issues it, and the hire creates the employee and a DRAFT contract from the
# offer. Writes go through call_kw with the client-controlled
# `tracking_disable` key and through the real /p03 controller.
import base64
import contextlib
import itertools
import json
from datetime import timedelta
from types import SimpleNamespace
from unittest import mock

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers import a09
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_p03_portal.controllers.a09 import m58
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.service.model import call_kw

REFUSED = (AccessError, UserError, ValidationError)
EVIDENCE = base64.b64encode(b"%PDF-1.4 verification evidence").decode()
_SEQ = itertools.count(1)


class FakeRequest:
    def __init__(self, env):
        self.env = env


def _user(env, *groups):
    n = next(_SEQ)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A09 M58 User %d" % n,
                "login": "a09-m58-%d@a09.test" % n,
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
            }
        )
    )


def _rpc_write(env, user, rec, vals):
    return call_kw(
        env(user=user.id, context={"tracking_disable": True})[rec._name],
        "write",
        [[rec.id], vals],
        {},
    )


def _decide(rec, requester, approver):
    """Request as `requester`, decide as `approver` from the M63 inbox."""
    rec.with_user(requester).action_request_approval()
    rec.invalidate_recordset()
    task = rec.approval_request_id.task_ids.filtered(
        lambda t: t.state == "pending" and t.assigned_user_id == approver
    )
    assert task, "no inbox task for %s; routed to %s" % (
        approver.name,
        rec.approval_request_id.task_ids.mapped("assigned_user_id.name"),
    )
    task.with_user(approver).action_approve()
    rec.invalidate_recordset()
    return task


def _events(env, event_type, aggregate, aggregate_id):
    return (
        env["fix.event.outbox"]
        .sudo()
        .search(
            [
                ("event_type", "=", event_type),
                ("aggregate", "=", aggregate),
                ("aggregate_id", "=", aggregate_id),
            ]
        )
    )


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


@pytest.fixture
def x(odoo_env):
    return make_x(odoo_env)


def make_x(env):
    """The cast of the M58 suites (also used by test_a09_talent_r2.py)."""
    c = SimpleNamespace(env=env)
    c.plain = _user(env)
    c.recruiter = _user(env, "cd_talent.group_talent")
    c.approver = _user(env, "cd_talent.group_requisition_approver")
    c.verifier = _user(env, "cd_talent.group_background_verifier")
    c.hrmgr = _user(env, "hr.group_hr_manager")
    c.offer_approver = _user(env, "cd_talent.group_offer_approver")
    c.cfo = _user(env, "cd_entity_config.group_dofa_tier_4")
    # a position with room: round 2 enforces its sanctioned headcount (BRU-HCM-10)
    c.position = env["fix.org.position"].create(
        {"name": "A09 M58 Technician", "grade": "A09T1", "headcount": 50}
    )
    env["fix.compensation.band"].sudo().create(
        {
            "name": "A09 T1",
            "grade": "A09T1",
            "range_min": 20000,
            "range_mid": 30000,
            "range_max": 50000,
        }
    )
    c.dept = env["hr.department"].create({"name": "A09 M58 Field Service"})
    c.panel_user = _user(env)
    c.interviewer = env["hr.employee"].create(
        {"name": "A09 M58 Panel Lead", "user_id": c.panel_user.id}
    )
    c.verifier2 = _user(env, "cd_talent.group_background_verifier")
    c.today = fields.Date.today()
    return c


def _requisition(x, openings=1, field_role=False, approve=True):
    vals = {
        "name": "A09 REQ %d" % next(_SEQ),
        "position_id": x.position.id,
        "department_id": x.dept.id,
        "openings": openings,
        "is_field_role": field_role,
    }
    if field_role:
        vals["assessment_pass_mark"] = 60
    req = x.env(user=x.recruiter.id)["fix.job.requisition"].create(vals)
    if approve:
        _decide(req, x.recruiter, x.approver)
        assert req.state == "open"
    return req


def _candidate(x, req, **vals):
    n = next(_SEQ)
    base = {
        "name": "A09 Candidate %d" % n,
        "email": "cand%d@a09.test" % n,
        "phone": "0171%07d" % n,
        "requisition_id": req.id if req else False,
        "consent_given": True,
        "declaration_accepted": True,
        "date_of_birth": "1998-03-01",
    }
    base.update(vals)
    return x.env(user=x.recruiter.id)["fix.candidate"].create(base)


def _evaluate(x, iv, user, score=4.0, recommendation="yes"):
    """The panelist writes and submits their own evaluation (BRU-TAO-07)."""
    ev = x.env(user=user.id)["fix.talent.evaluation"].search([("interview_id", "=", iv.id)])
    assert len(ev) == 1, "a panelist sees exactly their own evaluation"
    _rpc_write(x.env, user, ev, {"score": score, "recommendation": recommendation})
    ev.with_user(user).action_submit()
    return ev


def _interviewed(x, cand, recommendation="yes"):
    cand.with_user(x.recruiter).action_screen()
    cand.with_user(x.recruiter).action_interview()
    iv = x.env(user=x.recruiter.id)["fix.talent.interview"].create(
        {
            "candidate_id": cand.id,
            "scheduled_on": fields.Datetime.now(),
            "interviewer_id": x.interviewer.id,
        }
    )
    _evaluate(x, iv, x.panel_user, recommendation=recommendation)
    iv.with_user(x.recruiter).action_done()
    return iv


def _cleared_check(x, cand, kind):
    chk = x.env(user=x.recruiter.id)["fix.talent.check"].create(
        {"candidate_id": cand.id, "check_type": kind, "evidence_file": EVIDENCE}
    )
    _decide(chk, x.recruiter, x.verifier)
    assert chk.result == "clear"
    return chk


_UNDATED = object()


def _offer(x, cand, gross=30000.0, basic=18000.0, joining=None, valid_until=_UNDATED):
    """An offer with its acceptance deadline (M58-F15 makes the deadline a
    term of the offer). `valid_until=None` asks for a deliberately undated
    offer, which cannot be issued."""
    vals = {
        "candidate_id": cand.id,
        "gross_salary": gross,
        "basic_salary": basic,
        "joining_date": joining or (x.today + timedelta(days=30)),
        "valid_until": x.today + timedelta(days=21) if valid_until is _UNDATED else valid_until,
    }
    return x.env(user=x.hrmgr.id)["fix.talent.offer"].create(vals)


def _ready_to_hire(x, req=None, **cand_vals):
    """A candidate on the proper path up to an issued offer."""
    req = req or _requisition(x)
    cand = _candidate(x, req, **cand_vals)
    _interviewed(x, cand)
    cand.with_user(x.recruiter).action_offer()
    for kind in ("nid", "reference") + (("police",) if req.is_field_role else ()):
        _cleared_check(x, cand, kind)
    offer = _offer(x, cand)
    _decide(offer, x.hrmgr, x.offer_approver)
    assert offer.state == "issued"
    return cand, offer


def _accept(x, offer):
    offer.with_user(x.hrmgr).write({"acceptance_file": EVIDENCE, "acceptance_ref": "SIGNED-1"})
    offer.with_user(x.hrmgr).action_accept()


# =================================================================== requisition
def test_requisition_is_approved_by_someone_else_not_its_requester(x):
    both = _user(x.env, "cd_talent.group_talent", "cd_talent.group_requisition_approver")
    req = x.env(user=both.id)["fix.job.requisition"].create(
        {"name": "A09 self", "position_id": x.position.id, "openings": 1}
    )
    with pytest.raises(REFUSED):
        req.with_user(both).action_approve()  # the apply method is inbox-only
    req.with_user(both).action_request_approval()
    assigned = req.approval_request_id.task_ids.mapped("assigned_user_id")
    assert both not in assigned and x.approver in assigned
    task = req.approval_request_id.task_ids.filtered(lambda t: t.assigned_user_id == x.approver)
    task.with_user(x.approver).action_approve()
    assert req.state == "open" and req.approved_by_id == x.approver
    assert req.approved_openings == 1


def test_requisition_state_is_not_writable_by_orm_or_workspace(x, call):
    req = _requisition(x, approve=False)
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, x.recruiter, req, {"state": "open"})
    res = call(
        x.env(user=x.recruiter.id),
        "model_write",
        model="fix.job.requisition",
        record_id=req.id,
        values={"state": "open"},
    )
    req.invalidate_recordset()
    assert "error" in res and req.state == "draft"


def test_requisition_needs_a_position_and_positive_openings(x):
    Req = x.env(user=x.recruiter.id)["fix.job.requisition"]
    with pytest.raises(ValidationError), x.env.cr.savepoint():
        Req.create({"name": "A09 neg", "position_id": x.position.id, "openings": -3})
    no_position = Req.create({"name": "A09 nopos", "openings": 1})
    with pytest.raises(UserError, match="names no position"):
        no_position.action_request_approval()
    field_role = Req.create(
        {"name": "A09 fr", "position_id": x.position.id, "openings": 1, "is_field_role": True}
    )
    with pytest.raises(UserError, match="pass mark"):
        field_role.action_request_approval()


def test_approved_requisition_terms_are_frozen(x):
    req = _requisition(x, field_role=True)
    for vals in ({"openings": 5}, {"is_field_role": False}, {"assessment_pass_mark": 1}):
        with pytest.raises(UserError, match="approved"), x.env.cr.savepoint():
            _rpc_write(x.env, x.recruiter, req, vals)
    assert req.is_field_role and req.openings == 1


def test_mark_hired_is_gone_and_the_requisition_fills_itself(x):
    assert not hasattr(x.env["fix.job.requisition"], "action_hired")
    req = _requisition(x)
    cand, offer = _ready_to_hire(x, req)
    _accept(x, offer)
    assert cand.state == "hired" and req.state == "hired" and req.openings_left == 0


# =================================================================== hire gates
def test_walk_in_hire_is_refused(x):
    walk_in = x.env(user=x.recruiter.id)["fix.candidate"].create({"name": "A09 Walk-in"})
    with pytest.raises(UserError, match="no requisition"):
        walk_in.action_hire()
    assert walk_in.state == "applied" and not walk_in.employee_id


def test_rejected_candidate_is_not_hired(x):
    req = _requisition(x)
    cand = _candidate(x, req)
    with pytest.raises(UserError, match="outcome"):
        cand.with_user(x.recruiter).action_reject()
    cand.with_user(x.recruiter).action_reject(reason="Not shortlisted; emailed 4 Nov")
    assert cand.state == "rejected" and cand.rejection_reason
    with pytest.raises(UserError, match="rejected"):
        cand.with_user(x.hrmgr).action_hire()


@pytest.mark.parametrize("req_state", ["draft", "closed"])
def test_hire_against_a_draft_or_closed_requisition_is_refused(x, req_state):
    req = _requisition(x)
    cand, offer = _ready_to_hire(x, req)
    if req_state == "closed":
        req.with_user(x.recruiter).action_close()
    else:
        req.sudo()._guarded().write({"state": "draft"})
    with pytest.raises(UserError, match="not open"), x.env.cr.savepoint():
        _accept(x, offer)  # the workspace runs every action in a savepoint
    offer.invalidate_recordset()
    assert offer.state == "issued" and cand.state == "offered"  # accept rolled back


def test_no_hire_beyond_the_approved_openings(x):
    req = _requisition(x, openings=1)
    _first, offer1 = _ready_to_hire(x, req)
    _second, offer2 = _ready_to_hire(x, req)
    _accept(x, offer1)
    with pytest.raises(UserError, match=r"not open|no openings"):
        _accept(x, offer2)
    assert (
        x.env["fix.candidate"].search_count(
            [("requisition_id", "=", req.id), ("state", "=", "hired")]
        )
        == 1
    )


def test_a_strong_no_interview_stops_the_offer_stage(x):
    req = _requisition(x)
    cand = _candidate(x, req)
    _interviewed(x, cand, recommendation="strong_no")
    with pytest.raises(UserError, match=r"Strong No|recommends"):
        cand.with_user(x.recruiter).action_offer()


def test_candidate_state_hired_is_not_writable(x, call):
    req = _requisition(x)
    cand = _candidate(x, req)
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, x.recruiter, cand, {"state": "hired"})
    res = call(
        x.env(user=x.recruiter.id),
        "model_write",
        model="fix.candidate",
        record_id=cand.id,
        values={"state": "hired"},
    )
    cand.invalidate_recordset()
    assert "error" in res and cand.state == "applied"


def test_hire_requires_the_accepted_offer(x):
    cand, _offer = _ready_to_hire(x)
    with pytest.raises(UserError, match="no accepted offer"):
        cand.with_user(x.recruiter).action_hire()


def test_screening_needs_consent_and_duplicates_are_refused(x):
    req = _requisition(x, openings=3)
    no_consent = _candidate(x, req, consent_given=False)
    with pytest.raises(UserError, match="consent"):
        no_consent.with_user(x.recruiter).action_screen()
    with pytest.raises(ValidationError, match="already applied"), x.env.cr.savepoint():
        _candidate(x, req, email=no_consent.email)
    with pytest.raises(ValidationError, match="10, 13 or 17"), x.env.cr.savepoint():
        _candidate(x, req, nid_number="12345")


def test_the_same_person_is_not_hired_twice(x):
    req_a, req_b = _requisition(x), _requisition(x)
    _first, offer_a = _ready_to_hire(x, req_a, nid_number="1234567890")
    _accept(x, offer_a)
    _second, offer_b = _ready_to_hire(x, req_b, nid_number="1234567890")
    with pytest.raises(UserError, match="already hired"):
        _accept(x, offer_b)


def test_minimum_age_is_checked_before_the_offer(x):
    req = _requisition(x)
    # a 12-year-old who aced the interview: the OFFER STAGE itself refuses
    # (M58-F20: the gate ran only at issue and hire, so a minor reached
    # "offered")
    cand = _candidate(x, req, date_of_birth=str(x.today - timedelta(days=365 * 12)))
    _interviewed(x, cand)
    with pytest.raises(UserError, match="minimum hiring age"):
        cand.with_user(x.recruiter).action_offer()
    cand.invalidate_recordset()
    assert cand.state == "interview"
    # a verified date of birth is required at the same gate (BRU-TAO-17)
    cand.sudo().write({"date_of_birth": False})
    with pytest.raises(UserError, match="no verified date of birth"):
        cand.with_user(x.recruiter).action_offer()
    # of age: the stage opens, and the same candidate could not be issued an
    # offer while under age
    cand.sudo().write({"date_of_birth": "1998-03-01"})
    cand.with_user(x.recruiter).action_offer()
    assert cand.state == "offered"
    cand.sudo().write({"date_of_birth": str(x.today - timedelta(days=365 * 12))})
    offer = _offer(x, cand)
    with pytest.raises(UserError, match="minimum hiring age"):
        offer.with_user(x.hrmgr).action_request_approval()


# =================================================================== checks
def test_recruiter_cannot_clear_a_check_himself(x):
    req = _requisition(x)
    cand = _candidate(x, req)
    chk = x.env(user=x.recruiter.id)["fix.talent.check"].create(
        {"candidate_id": cand.id, "check_type": "police"}
    )
    with pytest.raises(REFUSED):
        chk.with_user(x.recruiter).action_clear()
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, x.recruiter, chk, {"result": "clear"})
    with pytest.raises(UserError, match="evidence"):
        chk.with_user(x.recruiter).action_request_approval()
    chk.with_user(x.recruiter).write({"evidence_file": EVIDENCE})
    _decide(chk, x.recruiter, x.verifier)
    assert chk.result == "clear" and chk.verified_by_id == x.verifier


def test_a_recruiter_who_is_also_a_verifier_does_not_verify_his_own_check(x):
    both = _user(x.env, "cd_talent.group_talent", "cd_talent.group_background_verifier")
    req = _requisition(x)
    cand = _candidate(x, req)
    chk = x.env(user=both.id)["fix.talent.check"].create(
        {"candidate_id": cand.id, "check_type": "nid", "evidence_file": EVIDENCE}
    )
    chk.with_user(both).action_request_approval()
    assert both not in chk.approval_request_id.task_ids.mapped("assigned_user_id")


def test_a_failed_check_blocks_the_hire_and_cannot_be_rewritten(x):
    cand, offer = _ready_to_hire(x)
    chk = x.env(user=x.recruiter.id)["fix.talent.check"].create(
        {"candidate_id": cand.id, "check_type": "employment"}
    )
    chk.with_user(x.recruiter).action_mark_failed(reason="Previous employer denies tenure")
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, x.recruiter, chk, {"result": "clear"})
    with pytest.raises(UserError, match="pending, failed"):
        _accept(x, offer)


def test_every_hire_needs_verified_nid_and_reference_checks(x):
    req = _requisition(x)
    cand = _candidate(x, req)
    _interviewed(x, cand)
    cand.with_user(x.recruiter).action_offer()
    offer = _offer(x, cand)
    _decide(offer, x.hrmgr, x.offer_approver)
    with pytest.raises(UserError, match="no verified NID Verification check"):
        _accept(x, offer)


# =================================================================== assessment / field role
def test_assessment_pass_is_the_score_against_the_approved_pass_mark(x):
    req = _requisition(x, field_role=True)
    cand = _candidate(x, req)
    Asm = x.env(user=x.recruiter.id)["fix.talent.assessment"]
    low = Asm.create({"candidate_id": cand.id, "score": 4.0})
    assert not low.passed
    with pytest.raises(UserError, match="computed"):
        _rpc_write(x.env, x.recruiter, low, {"passed": True})
    assert Asm.create({"candidate_id": cand.id, "score": 75.0}).passed


def test_field_role_needs_police_clearance_and_a_passed_assessment(x):
    req = _requisition(x, field_role=True)
    cand = _candidate(x, req)
    _interviewed(x, cand)
    with pytest.raises(UserError, match="passed practical assessment"):
        cand.with_user(x.recruiter).action_offer()
    x.env(user=x.recruiter.id)["fix.talent.assessment"].create(
        {"candidate_id": cand.id, "score": 80.0}
    )
    cand.with_user(x.recruiter).action_offer()
    for kind in ("nid", "reference"):
        _cleared_check(x, cand, kind)
    offer = _offer(x, cand)
    _decide(offer, x.hrmgr, x.offer_approver)
    with pytest.raises(UserError, match="Police Clearance"):
        _accept(x, offer)


# =================================================================== offers (I7)
def test_offer_is_issued_only_by_an_approver_and_never_its_maker(x):
    req = _requisition(x)
    cand = _candidate(x, req)
    _interviewed(x, cand)
    cand.with_user(x.recruiter).action_offer()
    offer = _offer(x, cand)
    with pytest.raises(REFUSED):
        offer.with_user(x.hrmgr).action_issue()
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, x.hrmgr, offer, {"state": "accepted"})
    offer.with_user(x.hrmgr).action_request_approval()
    assigned = offer.approval_request_id.task_ids.mapped("assigned_user_id")
    assert x.hrmgr not in assigned and x.offer_approver in assigned and x.cfo not in assigned


def test_out_of_band_offer_goes_to_the_cfo_tier(x):
    req = _requisition(x)
    cand = _candidate(x, req)
    _interviewed(x, cand)
    cand.with_user(x.recruiter).action_offer()
    offer = _offer(x, cand, gross=9999999.0, basic=5000000.0)
    assert not offer.in_band
    _decide(offer, x.hrmgr, x.cfo)
    assert offer.state == "issued" and offer.approved_by_id == x.cfo
    assert not offer.approved_in_band


def test_offer_against_an_unapproved_requisition_is_refused(x):
    req = _requisition(x, approve=False)
    cand = _candidate(x, req)
    offer = _offer(x, cand)
    with pytest.raises(UserError, match=r"offer stage|not open"):
        offer.with_user(x.hrmgr).action_request_approval()


def test_issued_offer_terms_are_frozen_and_a_pending_change_voids(x):
    _cand, offer = _ready_to_hire(x)
    with pytest.raises(UserError, match="terms were approved"):
        _rpc_write(x.env, x.hrmgr, offer, {"gross_salary": 90000})
    # a change while the approval is pending withdraws it
    req = _requisition(x)
    cand2 = _candidate(x, req)
    _interviewed(x, cand2)
    cand2.with_user(x.recruiter).action_offer()
    pending = _offer(x, cand2)
    pending.with_user(x.hrmgr).action_request_approval()
    pending.with_user(x.hrmgr).write({"basic_salary": 19000})
    pending.invalidate_recordset()
    assert pending.approval_state == "none"


def test_acceptance_is_the_candidates_signed_act(x):
    _cand, offer = _ready_to_hire(x)
    with pytest.raises(UserError, match="signed acceptance"):
        offer.with_user(x.hrmgr).action_accept()
    _accept(x, offer)
    assert offer.state == "accepted" and offer.responded_on


# =================================================================== I6 hand-off
def test_hire_creates_employee_and_draft_contract_from_the_offer(x):
    joining = x.today + timedelta(days=45)
    req = _requisition(x)
    cand = _candidate(x, req)
    _interviewed(x, cand)
    cand.with_user(x.recruiter).action_offer()
    for kind in ("nid", "reference"):
        _cleared_check(x, cand, kind)
    offer = _offer(x, cand, gross=32000.0, basic=20000.0, joining=joining)
    _decide(offer, x.hrmgr, x.offer_approver)
    _accept(x, offer)
    emp = cand.employee_id.sudo()
    assert emp.joining_date == joining and emp.joined_date == joining
    plan = x.env["fix.onboarding.plan"].search([("candidate_id", "=", cand.id)])
    contract = plan.contract_id.sudo()
    assert contract.state == "draft" and contract.employee_id == emp
    assert contract.basic_monthly == 20000.0 and contract.other_allowance == 12000.0
    assert contract.joining_date == joining
    # M58-F6: no identity provisioning while onboarding is still open
    assert not _events(x.env, "employee.joined", "hr.employee", emp.id)


def test_recruiter_without_employee_rights_completes_the_hire(x):
    """The P0 A2 control on the proper path: the Recruitment Officer holds no
    hr.employee create, and the hire still creates the employee."""
    cand, offer = _ready_to_hire(x)
    offer.sudo()._guarded().write({"state": "accepted", "acceptance_file": EVIDENCE})
    assert not x.env(user=x.recruiter.id)["hr.employee"].has_access("create")
    cand.with_user(x.recruiter).action_hire()
    assert cand.state == "hired" and cand.employee_id


# =================================================================== onboarding
def _hired_plan(x):
    cand, offer = _ready_to_hire(x)
    _accept(x, offer)
    plan = x.env["fix.onboarding.plan"].search([("candidate_id", "=", cand.id)])
    plan.with_user(x.recruiter).action_start()
    return plan


def _attest(x, plan):
    """The employee-signed letter, uploaded by the recruiter, attested by a
    verifier who did not upload it."""
    plan.with_user(x.recruiter).write({"signed_contract_file": EVIDENCE})
    plan.with_user(x.verifier).action_attest_signed_appointment()


def _finish_tasks(x, plan):
    for task in plan.sudo().task_ids.filtered(lambda t: t.mandatory and t.state == "open"):
        owner = task.owner_id
        _rpc_write(x.env, owner, task, {"evidence_note": "Done on day one"})
        task.with_user(owner).action_done()


def _verify_documents(x, plan):
    """FR-TAO-023/024 (capture audit 2026-11-17): the recruiter uploads each
    checklist document, a verifier who did not upload it verifies it."""
    for doc in plan.sudo().document_ids.filtered(lambda d: d.state != "verified"):
        _rpc_write(x.env, x.recruiter, doc, {"document_file": EVIDENCE})
        doc.with_user(x.verifier).action_verify()


def test_onboarding_completes_only_on_evidence(x, call):
    plan = _hired_plan(x)
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, x.recruiter, plan, {"state": "completed"})
    with pytest.raises(UserError, match="appointment letter is not acknowledged"):
        plan.with_user(x.recruiter).action_complete()
    _attest(x, plan)
    with pytest.raises(UserError, match="mandatory onboarding task"):
        plan.with_user(x.recruiter).action_complete()
    _finish_tasks(x, plan)
    with pytest.raises(UserError, match="bank account"):
        plan.with_user(x.recruiter).action_complete()
    emp = plan.employee_id.sudo()
    emp.write({"bank_account_number": "1234567890123", "routing_number": "123456789"})
    # M58-F1: a create mints the employee code, so the code gate is met; the
    # evidence gates below still refuse
    assert emp.employee_code
    with pytest.raises(UserError, match="pre-boarding document"):
        plan.with_user(x.recruiter).action_complete()
    _verify_documents(x, plan)
    plan.with_user(x.recruiter).action_complete()
    assert plan.state == "completed" and plan.completed_by_id == x.recruiter
    joined = _events(x.env, "employee.joined", "hr.employee", emp.id)
    assert len(joined) == 1
    payload = json.loads(joined.payload)
    assert payload["employee_id"] == emp.id and payload["employee_code"] == emp.employee_code
    assert not _events(x.env, "employee.joined", "fix.onboarding.plan", plan.id)


def test_onboarding_flags_cannot_be_ticked(x):
    """The flags are read from evidence: a typed tick does not stick."""
    plan = _hired_plan(x)
    for flag in ("nid_verified", "contract_signed", "bank_details_captured"):
        with x.env.cr.savepoint(), contextlib.suppress(REFUSED):
            _rpc_write(x.env, x.recruiter, plan, {flag: True})
        plan.invalidate_recordset()
        if flag != "nid_verified":  # the NID check was cleared on this path
            assert not plan[flag], flag
    with pytest.raises(UserError, match="appointment letter is not acknowledged"):
        plan.with_user(x.recruiter).action_complete()


# =================================================================== reads, KPIs
def test_plain_employee_reads_no_candidate_or_report(x, call):
    req = _requisition(x)
    cand = _candidate(x, req)
    x.env["fix.talent.assessment"].create({"candidate_id": cand.id, "score": 41})
    with pytest.raises(AccessError):
        cand.with_user(x.plain).read(["email"])
    res = call(x.env(user=x.plain.id), "model_report", module="M58", report="practical_results")
    assert "error" in res or not res.get("rows")


def test_kpis_do_not_count_another_companys_candidates(x):
    other = x.env["res.company"].create({"name": "A09 M58 Other Co"})
    before = m58.kpis(x.env(user=x.recruiter.id))["pipeline"]
    x.env["fix.candidate"].create({"name": "A09 Foreign", "company_id": other.id})
    assert m58.kpis(x.env(user=x.recruiter.id))["pipeline"] == before


# =================================================================== automation
def test_expired_offers_expire_and_erasure_follows_the_retention_setting(x):
    _cand, offer = _ready_to_hire(x)
    offer.sudo()._guarded().write({"valid_until": x.today - timedelta(days=1)})
    x.env["fix.talent.offer"].cron_expire_offers()
    assert offer.state == "expired"
    req = _requisition(x)
    gone = _candidate(x, req, nid_number="12345678901234567")
    gone.with_user(x.recruiter).action_reject(reason="Not selected")
    Cand = x.env["fix.candidate"]
    assert not gone.retention_until  # 0 days: no automatic erasure (decision)
    x.env["ir.config_parameter"].sudo().set_param("cd_talent.candidate_retention_days", "30")
    late = _candidate(x, req)
    late.with_user(x.recruiter).action_reject(reason="Not selected")
    assert late.retention_until == fields.Date.context_today(late) + timedelta(days=30)
    late.sudo()._guarded().write({"retention_until": x.today - timedelta(days=1)})
    assert Cand.cron_erase_expired_candidates() == 1
    assert late.erased and not late.email and not late.phone
    assert Cand.cron_erase_expired_candidates() == 0  # idempotent


def test_day_one_readiness_escalates_once(x):
    plan = _hired_plan(x)
    plan.sudo().write({"joined_date": x.today + timedelta(days=3)})
    Plan = x.env["fix.onboarding.plan"]
    assert Plan.cron_escalate_day_one_readiness() >= 1
    assert plan.readiness_escalated_on
    assert plan.id not in Plan.search([("readiness_escalated_on", "=", False)]).ids


# =================================================================== deployment
@pytest.mark.parametrize(
    "xmlid",
    [
        "cd_talent.cron_talent_day_one_readiness",
        "cd_talent.cron_talent_expire_offers",
        "cd_talent.cron_talent_erase_candidates",
    ],
)
def test_crons_are_deployed_and_active(odoo_env, xmlid):
    cron = odoo_env.ref(xmlid)
    assert cron.active and cron.user_id == odoo_env.ref("base.user_root")


@pytest.mark.parametrize(
    "group",
    [
        "cd_talent.group_requisition_approver",
        "cd_talent.group_offer_approver",
        "cd_talent.group_background_verifier",
    ],
)
def test_approver_roles_exist_and_hold_admin_only(odoo_env, group):
    holders = odoo_env.ref(group).user_ids
    assert holders <= (odoo_env.ref("base.user_root") | odoo_env.ref("base.user_admin"))


def test_new_acl_rows_are_deployed(odoo_env):
    for xmlid in (
        "cd_talent.access_fix_job_requisition_approver",
        "cd_talent.access_fix_talent_offer_approver",
        "cd_talent.access_fix_talent_offer_cfo",
        "cd_talent.access_fix_talent_check_verifier",
    ):
        assert odoo_env.ref(xmlid).perm_read


def test_workspace_offers_requests_never_the_apply_methods(odoo_env):
    for model, conf in m58.SURFACES.items():
        for method in conf["actions"]:
            assert callable(getattr(odoo_env[model], method, None)), (model, method)
    assert "action_approve" not in a09.SURFACES["fix.job.requisition"]["actions"]
    assert "action_clear" not in a09.SURFACES["fix.talent.check"]["actions"]
    assert "action_issue" not in a09.SURFACES["fix.talent.offer"]["actions"]
    assert "action_request_approval" in a09.SURFACES["fix.talent.offer"]["actions"]


# ============================================================ wave 2 (A09 ERP audit)
def _requisition_for(x, hiring_manager):
    """A requisition the recruiter raises for `hiring_manager`'s team and a
    different approver opens."""
    req = x.env(user=x.recruiter.id)["fix.job.requisition"].create(
        {
            "name": "A09 REQ %d" % next(_SEQ),
            "position_id": x.position.id,
            "department_id": x.dept.id,
            "openings": 1,
            "hiring_manager_id": hiring_manager.id,
        }
    )
    return req


def test_a_hiring_manager_never_approves_their_own_requisition(x):
    """M58-F12: the conflict set held the requester and the creator only, so a
    Requisition Approver who is the requisition's hiring manager could open
    the requisition that hires for their own team."""
    both = _user(x.env, "cd_talent.group_hiring_manager", "cd_talent.group_requisition_approver")
    req = _requisition_for(x, both)
    req.with_user(x.recruiter).action_request_approval()
    req.invalidate_recordset()
    tasks = req.approval_request_id.task_ids
    mine = tasks.filtered(lambda t: t.state == "pending" and t.assigned_user_id == both)
    assert mine, "the request is routed to the approver who is the hiring manager"
    with pytest.raises(UserError, match="subject of it"):
        mine.with_user(both).action_approve()
    req.invalidate_recordset()
    assert req.state == "draft" and req.approval_state == "pending"
    # an approver with no stake in the requisition opens it
    other = tasks.filtered(lambda t: t.state == "pending" and t.assigned_user_id == x.approver)
    other.with_user(x.approver).action_approve()
    req.invalidate_recordset()
    assert req.state == "open" and req.approved_by_id == x.approver


def test_the_hiring_manager_and_the_approver_never_judge_their_own_candidates(x):
    """M58-F12: the panel check excluded only the candidate, so the hiring
    manager could sit on - or lead - the panel that judges their own
    candidates (BRU-TAO-07 independence)."""
    hm = _user(x.env, "cd_talent.group_hiring_manager")
    hm_emp = x.env["hr.employee"].create({"name": "A09 HM on panel", "user_id": hm.id})
    approver_emp = x.env["hr.employee"].create(
        {"name": "A09 approver on panel", "user_id": x.approver.id}
    )
    req = _requisition_for(x, hm)
    _decide(req, x.recruiter, x.approver)
    cand = _candidate(x, req)
    cand.with_user(x.recruiter).action_screen()
    cand.with_user(x.recruiter).action_interview()
    Interview = x.env(user=x.recruiter.id)["fix.talent.interview"]
    now = fields.Datetime.now()
    # each refusal rolls back what it had written, as a real request would
    with pytest.raises(ValidationError, match="cannot judge its candidates"), x.env.cr.savepoint():
        Interview.create(
            {"candidate_id": cand.id, "scheduled_on": now, "interviewer_id": hm_emp.id}
        )
    with pytest.raises(ValidationError, match="cannot judge its candidates"), x.env.cr.savepoint():
        Interview.create(
            {"candidate_id": cand.id, "scheduled_on": now, "interviewer_id": approver_emp.id}
        )
    iv = Interview.create(
        {"candidate_id": cand.id, "scheduled_on": now, "interviewer_id": x.interviewer.id}
    )
    with pytest.raises(ValidationError, match="cannot judge its candidates"), x.env.cr.savepoint():
        iv.with_user(x.recruiter).action_add_panelist(hm_emp.id)
    with pytest.raises(ValidationError, match="cannot judge its candidates"), x.env.cr.savepoint():
        iv.with_user(x.recruiter).action_add_panelist(approver_emp.id)
    iv.invalidate_recordset()
    # the round keeps its own panel (the lead interviewer); the refused two never join
    assert iv.sudo().panelist_ids == x.interviewer
    # an independent panelist is still added
    independent = x.env["hr.employee"].create({"name": "A09 independent panelist"})
    iv.with_user(x.recruiter).action_add_panelist(independent.id)
    iv.invalidate_recordset()
    assert iv.sudo().panelist_ids == x.interviewer | independent


def test_talent_kpis_are_honest_when_nothing_was_measured(x):
    """M58-F13: `first90_retention` printed 0.0% with no review (unknown is
    not 0), and the funnel share was over whoever still sat in the "Applied"
    stage, so two of three candidates in interview read 200%."""
    req = _requisition(x)
    moved = [_candidate(x, req), _candidate(x, req)]
    _candidate(x, req)  # still at "Applied"
    for cand in moved:
        _interviewed(x, cand)
    out = m58.kpis(x.env)
    assert out["first90_retention"] is None  # no first-90 review exists
    assert out["offer_accept_rate"] is None  # no offer was ever issued
    assert out["referral_share"] == 0.0  # a measured 0 of 3
    shares = {r["stage"]: r["share"] for r in m58.funnel_conversion(x.env)["rows"]}
    assert shares["Applied"] == 33.3, shares
    assert shares["Interview"] == 66.7, shares
    assert shares["Hired"] == 0.0


def test_an_offer_without_a_validity_date_cannot_be_issued(x):
    """M58-F15: `valid_until` was optional, and the expiry cron only sees a
    dated offer - an undated one stayed live for ever and blocked the
    candidate's other offers. No default figure is ours to pick: the date is
    entered (or defaults from the business's own setting)."""
    req = _requisition(x)
    cand = _candidate(x, req)
    _interviewed(x, cand)
    cand.with_user(x.recruiter).action_offer()
    offer = _offer(x, cand, valid_until=None)
    assert not offer.valid_until  # cd_talent.offer_validity_days is not ruled
    with pytest.raises(UserError, match="no validity date"):
        offer.with_user(x.hrmgr).action_request_approval()
    offer.with_user(x.hrmgr).write({"valid_until": x.today + timedelta(days=7)})
    _decide(offer, x.hrmgr, x.offer_approver)
    offer.invalidate_recordset()
    assert offer.state == "issued"
    # once the business rules a figure, a NEW offer (no date passed) defaults to it
    Param = x.env["ir.config_parameter"].sudo()
    Param.set_param("cd_talent.offer_validity_days", "10")
    try:
        dated = x.env(user=x.hrmgr.id)["fix.talent.offer"].create(
            {
                "candidate_id": cand.id,
                "gross_salary": 30000.0,
                "basic_salary": 18000.0,
                "joining_date": x.today + timedelta(days=30),
            }
        )
        assert dated.valid_until == x.today + timedelta(days=10)
    finally:
        Param.set_param("cd_talent.offer_validity_days", "0")


def test_a_hiring_manager_records_the_first_90_reviews_of_their_own_hires(x):
    """M58-F17: fix.talent.first90 had no access row for a Hiring Manager, so
    the manager who runs the 30/60/90 conversation could neither see nor
    record it. They reach their own requisitions' plans and the reviews they
    conduct - never another manager's."""
    hm = _user(x.env, "cd_talent.group_hiring_manager")
    hm_emp = x.env["hr.employee"].create({"name": "A09 HM reviewer", "user_id": hm.id})
    mine = _requisition_for(x, hm)
    _decide(mine, x.recruiter, x.approver)
    theirs = _requisition(x)
    Plan = x.env["fix.onboarding.plan"]
    cand_mine, cand_theirs = _candidate(x, mine), _candidate(x, theirs)
    plan_mine = Plan.create(
        {
            "name": "A09 plan mine",
            "candidate_id": cand_mine.id,
            "requisition_id": mine.id,
            "joined_date": x.today,
        }
    )
    plan_theirs = Plan.create(
        {
            "name": "A09 plan theirs",
            "candidate_id": cand_theirs.id,
            "requisition_id": theirs.id,
            "joined_date": x.today,
        }
    )
    hire_mine = x.env["hr.employee"].create({"name": "A09 hire mine"})
    hire_theirs = x.env["hr.employee"].create({"name": "A09 hire theirs"})
    plan_mine.sudo().write({"employee_id": hire_mine.id})
    plan_theirs.sudo().write({"employee_id": hire_theirs.id})
    First90 = x.env["fix.talent.first90"]
    own = First90.with_user(hm).create(
        {
            "employee_id": hire_mine.id,
            "plan_id": plan_mine.id,
            "reviewer_id": hm_emp.id,
            "milestone": "day_30",
        }
    )
    foreign = First90.create(
        {
            "employee_id": hire_theirs.id,
            "plan_id": plan_theirs.id,
            "milestone": "day_30",
        }
    )
    x.env.invalidate_all()
    assert own.with_user(hm).milestone == "day_30"
    own.with_user(hm).write({"rating": 4.0})
    assert own.sudo().rating == 4.0
    assert First90.with_user(hm).search([]) == own
    with pytest.raises(AccessError), x.env.cr.savepoint():
        foreign.with_user(hm).write({"rating": 1.0})
    # a review the manager conducts for another team is theirs to record too
    conducted = First90.with_user(hm).create(
        {
            "employee_id": hire_theirs.id,
            "plan_id": plan_theirs.id,
            "reviewer_id": hm_emp.id,
            "milestone": "day_60",
        }
    )
    x.env.invalidate_all()
    assert conducted in First90.with_user(hm).search([])
