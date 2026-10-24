# cd_talent live-ORM tests — P09-M08 (CD-M58-01): requisition -> candidate ->
# onboarding plan -> the authoritative employee.joined event.
import json
from types import SimpleNamespace

import pytest
from odoo import fields
from odoo.exceptions import UserError


def _events(env, event_type, aggregate_id):
    rows = env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate_id", "=", aggregate_id)], order="id"
    )
    return [json.loads(r.payload) for r in rows]


@pytest.fixture
def ctx(odoo_env):
    env = odoo_env
    position = env["fix.org.position"].create({"name": "Field Technician L1"})
    department = env["hr.department"].create({"name": "Field Service"})
    requisition = env["fix.job.requisition"].create(
        {
            "name": "REQ-2026-014",
            "position_id": position.id,
            "department_id": department.id,
            "openings": 2,
        }
    )
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    return SimpleNamespace(
        env=env, position=position, department=department, requisition=requisition, ou=ou
    )


def test_requisition_lifecycle(ctx):
    req = ctx.requisition
    assert req.state == "draft"
    req.action_open()
    assert req.state == "open"
    req.action_hired()
    assert req.state == "hired"
    assert _events(ctx.env, "employee.hired", req.id) == [{"position": "Field Technician L1"}]
    no_position = ctx.env["fix.job.requisition"].create({"name": "REQ-ADHOC"})
    no_position.action_hired()
    assert _events(ctx.env, "employee.hired", no_position.id) == [{"position": "REQ-ADHOC"}]


def test_candidate_pipeline_and_hire_opens_onboarding(ctx):
    candidate = ctx.env["fix.candidate"].create(
        {
            "name": "Sabbir Ahmed",
            "requisition_id": ctx.requisition.id,
            "operating_unit_id": ctx.ou.id,
        }
    )
    for action, state in (
        ("action_screen", "screening"),
        ("action_interview", "interview"),
        ("action_offer", "offered"),
    ):
        getattr(candidate, action)()
        assert candidate.state == state
    candidate.action_hire()
    assert candidate.state == "hired"
    plan = ctx.env["fix.onboarding.plan"].search([("candidate_id", "=", candidate.id)])
    assert plan.name == "Onboarding: Sabbir Ahmed"
    assert (plan.requisition_id, plan.position_id, plan.department_id) == (
        ctx.requisition,
        ctx.position,
        ctx.department,
    )
    assert (plan.company_id, plan.operating_unit_id) == (candidate.company_id, ctx.ou)
    assert (plan.state, plan.joined_date) == ("draft", fields.Date.today())
    assert _events(ctx.env, "candidate.hired", candidate.id) == [
        {"candidate": "Sabbir Ahmed", "onboarding_plan_id": plan.id}
    ]


def test_walk_in_hire_without_requisition(ctx):
    candidate = ctx.env["fix.candidate"].create({"name": "Walk-in Candidate"})
    candidate.action_hire()
    plan = ctx.env["fix.onboarding.plan"].search([("candidate_id", "=", candidate.id)])
    assert not (plan.requisition_id or plan.position_id or plan.department_id)
    assert not plan.operating_unit_id


def _plan(ctx, **vals):
    candidate = ctx.env["fix.candidate"].create({"name": "Nadia Rahman"})
    return ctx.env["fix.onboarding.plan"].create(
        {"name": "Onboarding: Nadia", "candidate_id": candidate.id, **vals}
    )


PREREQUISITES = ("nid_verified", "contract_signed", "keycloak_provisioned", "bank_details_captured")


@pytest.mark.parametrize("missing", PREREQUISITES)
def test_onboarding_cannot_complete_without_statutory_prerequisites(ctx, missing):
    plan = _plan(ctx, **{flag: flag != missing for flag in PREREQUISITES})
    plan.action_start()
    assert plan.state == "in_progress"
    with pytest.raises(UserError, match="statutory prerequisites"), ctx.env.cr.savepoint():
        plan.action_complete()
    assert plan.state == "in_progress"
    assert _events(ctx.env, "employee.joined", plan.id) == []


def test_onboarding_completion_emits_employee_joined(ctx):
    plan = _plan(
        ctx,
        position_id=ctx.position.id,
        department_id=ctx.department.id,
        **dict.fromkeys(PREREQUISITES, True),
    )
    plan.action_complete()
    assert plan.state == "completed"
    assert _events(ctx.env, "employee.joined", plan.id) == [
        {
            "onboarding_id": plan.id,
            "candidate_name": "Nadia Rahman",
            "position": "Field Technician L1",
            "department": "Field Service",
            "joined_date": str(fields.Date.today()),
        }
    ]
    bare = _plan(ctx, **dict.fromkeys(PREREQUISITES, True))
    bare.action_complete()
    payload = _events(ctx.env, "employee.joined", bare.id)[0]
    assert (payload["position"], payload["department"]) == ("", "")
