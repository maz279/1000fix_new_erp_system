"""M67 capture audit (2026-11-18): the records no page could capture, walked live.

Every step runs as a NON-ADMIN role holder (project manager, sponsor, a plain
reviewer) through the P03 controller the workspace calls, with the kwargs its
buttons send. Constraint refusals run in a savepoint so the test can go on.
"""

from __future__ import annotations

import base64
import datetime
import types

import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
PM = "cd_ppm.group_ppm_project_manager"
SPONSOR = "cd_ppm.group_ppm_sponsor"
T2 = "cd_entity_config.group_dofa_tier_2"
EVIDENCE = base64.b64encode(b"%PDF-1.4 UAT sign-off").decode()


class World:
    """The role holders of one test."""


def _user(env, login, *groups):
    gids = [env.ref("base.group_user").id] + [env.ref(x).id for x in groups]
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create({"name": login, "login": login + "@m67c.test", "group_ids": [(6, 0, gids)]})
    )
    return user, env["hr.employee"].create({"name": login, "user_id": user.id})


class Api:
    """The screen's own controller, as one user."""

    def __init__(self, env, user):
        self.env = env(user=user.id)

    def _call(self, name, **kw):
        import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g

        saved = getattr(g, "request", None)
        g.request = types.SimpleNamespace(env=self.env)
        try:
            ctl = g.P03GenericApiController()
            return getattr(g.P03GenericApiController, name).original_endpoint(ctl, **kw)
        finally:
            g.request = saved

    def write(self, model, values, record_id=None):
        return self._call("model_write", model=model, record_id=record_id, values=values)

    def action(self, model, rec, method, **kwargs):
        return self._call("model_action", model=model, ids=[rec.id], method=method, kwargs=kwargs)

    def form(self, model, names, record_id=None):
        specs = [{"name": n} for n in names]
        return self._call("model_form", model=model, fields=specs, record_id=record_id)

    def records(self, model, cols):
        return self._call("model_records", model=model, cols=cols)


@pytest.fixture
def w(odoo_env):
    world = World()
    env = odoo_env
    world.env = env
    world.pm, world.pm_emp = _user(env, "m67c.pm", PM)
    world.pm2, _e = _user(env, "m67c.pm2", PM)
    world.sponsor, _e = _user(env, "m67c.sponsor", SPONSOR)
    world.sponsor2, _e = _user(env, "m67c.sponsor2", SPONSOR)
    world.reviewer, _e = _user(env, "m67c.reviewer")
    world.plain, _e = _user(env, "m67c.plain")
    world.t2, _e = _user(env, "m67c.t2", T2)
    world.pm_api = Api(env, world.pm)
    world.sponsor_api = Api(env, world.sponsor)
    return world


def _refused(env, fn):
    try:
        with env.cr.savepoint():
            fn()
    except REFUSED as exc:
        return str(exc) or type(exc).__name__
    return None


def _created(result, env, model):
    assert result.get("id"), result
    return env[model].browse(result["id"])


def _project(w, project_type="client", budget=200000.0, **extra):
    vals = {
        "name": "M67C %s" % project_type,
        "project_type": project_type,
        "budget": budget,
        "contract_value": 500000.0 if project_type == "client" else 0.0,
        "manager_id": w.pm_emp.id,
        "date_end": datetime.date(2027, 6, 30),
    }
    vals.update(extra)
    return w.env["fix.project"].with_user(w.pm).create(vals)


def _decided(w, project, kind):
    gate = w.env["fix.project.gate"].create({"project_id": project.id, "gate": kind})
    gate.with_user(w.sponsor).action_record_decision(
        decision="pass", checklist_passed=True, findings="reviewed"
    )
    gate.with_user(w.sponsor).action_hold()
    gate.with_user(w.sponsor).action_close()


def _activate(w, project):
    project.with_user(w.pm).action_request_approval(justification="FY27 plan p.4")
    task = project.sudo().approval_request_id.task_ids.filtered(
        lambda t: t.state == "pending" and t.assigned_user_id == w.t2
    )
    task.with_user(w.t2).action_approve(comment="ok")
    _decided(w, project, "g1_initiation")
    _decided(w, project, "g2_planning")
    project.with_user(w.pm).action_activate()
    assert project.state == "active"
    return project


def _milestone(w, project, accepted=True):
    ms = _created(
        w.pm_api.write("fix.project.milestone", {"name": "Go-live", "project_id": project.id}),
        w.env,
        "fix.project.milestone",
    )
    if accepted:
        result = w.sponsor_api.action(
            "fix.project.milestone", ms, "action_accept", acceptance_note="UAT sign-off 7"
        )
        assert result["success"], result
    return ms


# ============================== forms ==============================

FORMS = {
    "fix.project.deliverable": [
        "title",
        "project_id",
        "milestone_id",
        "acceptance_criteria",
        "evidence_requirement",
        "reviewer_id",
        "evidence_file",
        "state",
    ],
    "fix.project.change": [
        "project_id",
        "title",
        "description",
        "justification",
        "cost_impact",
        "schedule_impact_days",
        "resource_impact",
        "state",
    ],
    "fix.project.budget.line": ["project_id", "category", "amount", "note"],
    "fix.project.lesson": ["project_id", "category", "observation", "recommendation", "state"],
    "fix.project.benefit": [
        "name",
        "project_id",
        "business_case_target",
        "unit",
        "measurement_method",
        "owner_id",
        "measured_value",
        "state",
    ],
}


@pytest.mark.parametrize("model", sorted(FORMS))
def test_every_new_form_opens_for_a_project_manager(w, model):
    result = w.pm_api.form(model, FORMS[model])
    assert result.get("success", True) and not result.get("error"), result


def test_a_plain_user_reads_but_captures_nothing(w):
    project = _project(w)
    api = Api(w.env, w.plain)
    result = api.write(
        "fix.project.lesson",
        {"project_id": project.id, "observation": "x", "recommendation": "y"},
    )
    assert not result.get("id"), result
    assert api.records("fix.project.lesson", ["name"]) is not None


# ============================== deliverables ==============================


def test_a_deliverable_is_submitted_with_evidence_and_accepted_by_its_reviewer(w):
    project = _active(w)
    ms = _milestone(w, project)
    dlv = _created(
        w.pm_api.write(
            "fix.project.deliverable",
            {
                "title": "Site survey report",
                "project_id": project.id,
                "milestone_id": ms.id,
                "acceptance_criteria": "Covers all 12 branches",
                "reviewer_id": w.reviewer.id,
            },
        ),
        w.env,
        "fix.project.deliverable",
    )
    assert dlv.name.startswith("DLV/")
    # no evidence: refused
    result = w.pm_api.action("fix.project.deliverable", dlv, "action_submit")
    assert not result["success"] and "evidence" in str(result).lower(), result
    dlv.with_user(w.pm).write({"evidence_file": EVIDENCE, "evidence_filename": "uat.pdf"})
    # the milestone cannot complete while its deliverable is not accepted
    err = _refused(w.env, lambda: ms.with_user(w.pm).action_complete())
    assert "not accepted" in err
    assert w.pm_api.action("fix.project.deliverable", dlv, "action_submit")["success"]
    assert dlv.state == "submitted" and dlv.submitted_by_id == w.pm
    # what the reviewer judges cannot change once submitted
    assert _refused(w.env, lambda: dlv.with_user(w.pm).write({"acceptance_criteria": "less"}))
    # the submitter does not accept his own deliverable
    assert not w.pm_api.action("fix.project.deliverable", dlv, "action_accept")["success"]
    # a send-back needs its reason
    reviewer = Api(w.env, w.reviewer)
    result = reviewer.action("fix.project.deliverable", dlv, "action_send_back")
    assert not result["success"] and "State why" in str(result), result
    assert reviewer.action(
        "fix.project.deliverable", dlv, "action_send_back", reason="Branch 9 missing"
    )["success"]
    assert dlv.state == "rework" and dlv.rejection_reason == "Branch 9 missing"
    assert w.pm_api.action("fix.project.deliverable", dlv, "action_submit")["success"]
    assert reviewer.action("fix.project.deliverable", dlv, "action_accept")["success"]
    assert dlv.state == "accepted" and dlv.decided_by_id == w.reviewer
    ms.with_user(w.pm).action_complete()
    assert ms.state == "done"


def test_a_sponsor_who_submits_does_not_accept_his_own_deliverable(w):
    project = _project(w)
    # the project manager registers it; a sponsor submits it
    dlv = (
        w.env["fix.project.deliverable"]
        .with_user(w.pm)
        .create(
            {
                "title": "Handover pack",
                "project_id": project.id,
                "acceptance_criteria": "Signed",
                "reviewer_id": w.reviewer.id,
                "evidence_file": EVIDENCE,
            }
        )
    )
    dlv.with_user(w.sponsor2).action_submit()
    assert dlv.submitted_by_id == w.sponsor2
    result = Api(w.env, w.sponsor2).action("fix.project.deliverable", dlv, "action_accept")
    assert not result["success"] and "submitted by you" in str(result), result
    assert w.sponsor_api.action("fix.project.deliverable", dlv, "action_accept")["success"]


def test_an_outsider_does_not_decide_a_deliverable(w):
    project = _project(w)
    dlv = (
        w.env["fix.project.deliverable"]
        .with_user(w.pm)
        .create(
            {
                "title": "Design pack",
                "project_id": project.id,
                "acceptance_criteria": "Signed by the client",
                "reviewer_id": w.reviewer.id,
                "evidence_file": EVIDENCE,
            }
        )
    )
    dlv.with_user(w.pm).action_submit()
    assert not Api(w.env, w.plain).action("fix.project.deliverable", dlv, "action_accept")[
        "success"
    ]
    assert dlv.state == "submitted"


# ============================== scope changes ==============================


def test_an_approved_change_requests_the_budget_and_moves_the_end(w):
    project = _active(w)
    change = _created(
        w.pm_api.write(
            "fix.project.change",
            {
                "project_id": project.id,
                "title": "Add 3 branches",
                "description": "Extend the rollout to Sylhet",
                "justification": "Client order variation 2",
                "cost_impact": 40000.0,
                "schedule_impact_days": 14,
            },
        ),
        w.env,
        "fix.project.change",
    )
    assert change.name.startswith("PCR/") and change.requested_by_id == w.pm
    assert w.pm_api.action("fix.project.change", change, "action_submit")["success"]
    # the priced change is not rewritten once submitted
    assert _refused(w.env, lambda: change.with_user(w.pm).write({"cost_impact": 1.0}))
    # the project manager does not decide his own scope change
    assert not w.pm_api.action("fix.project.change", change, "action_approve")["success"]
    # nor does another project manager who did not raise it: deciding is a sponsor's
    assert not Api(w.env, w.pm2).action("fix.project.change", change, "action_approve")["success"]
    assert change.state == "submitted"
    budget = project.budget
    result = w.sponsor_api.action("fix.project.change", change, "action_approve")
    assert result["success"], result
    assert change.state == "approved" and change.decided_by_id == w.sponsor
    assert project.budget == budget, "the change never edits the baselined budget"
    assert project.budget_requested == budget + 40000.0
    assert project.date_end == datetime.date(2027, 7, 14)


def test_a_rejection_states_why_and_a_pending_change_blocks_closure(w):
    project = _active(w, project_type="client")
    change = (
        w.env["fix.project.change"]
        .with_user(w.pm)
        .create(
            {
                "project_id": project.id,
                "title": "Swap vendor",
                "description": "d",
                "justification": "j",
            }
        )
    )
    change.with_user(w.pm).action_submit()
    result = w.sponsor_api.action("fix.project.change", change, "action_reject")
    assert not result["success"] and "State why" in str(result), result
    _ready_for_closure(w, project)
    err = _refused(w.env, lambda: project.with_user(w.sponsor).action_complete())
    assert "wait for a decision" in err
    assert w.sponsor_api.action(
        "fix.project.change", change, "action_reject", note="No budget left"
    )["success"]
    assert change.state == "rejected" and change.decision_note == "No budget left"
    lesson = (
        w.env["fix.project.lesson"]
        .with_user(w.pm)
        .create({"project_id": project.id, "observation": "o", "recommendation": "r"})
    )
    lesson.with_user(w.pm).action_share()
    project.with_user(w.sponsor).action_complete()
    assert project.state == "completed"


# ============================== budget by category ==============================


def test_budget_lines_stay_within_the_budget_and_freeze_at_activation(w):
    project = _project(w, budget=200000.0)
    line = _created(
        w.pm_api.write(
            "fix.project.budget.line",
            {"project_id": project.id, "category": "labour", "amount": 120000.0},
        ),
        w.env,
        "fix.project.budget.line",
    )
    result = w.pm_api.write(
        "fix.project.budget.line",
        {"project_id": project.id, "category": "parts", "amount": 90000.0},
    )
    assert not result.get("id"), result
    assert w.pm_api.write(
        "fix.project.budget.line",
        {"project_id": project.id, "category": "parts", "amount": 50000.0},
    ).get("id")
    from odoo.addons.cd_p03_portal.controllers.a12 import m67

    row = next(
        r for r in m67.budget_vs_actual(w.env(user=w.pm.id))["rows"] if r["project"] == project.name
    )
    assert row["split"] == "Labour 120000.00, Parts 50000.00, unallocated 30000.00"
    _activate(w, project)
    err = _refused(w.env, lambda: line.with_user(w.pm).write({"amount": 100000.0}))
    assert "baselined" in err


# ============================== closure: lessons and benefits ==============================


def _active(w, project_type="client", **extra):
    return _activate(w, _project(w, project_type=project_type, **extra))


def _ready_for_closure(w, project):
    ms = _milestone(w, project)
    ms.with_user(w.pm).action_complete()
    return ms


def test_a_project_closes_only_with_a_lesson_passed_to_quality(w):
    project = _active(w)
    _ready_for_closure(w, project)
    err = _refused(w.env, lambda: project.with_user(w.sponsor).action_complete())
    assert "BRU-PPM-14" in err
    lesson = _created(
        w.pm_api.write(
            "fix.project.lesson",
            {
                "project_id": project.id,
                "category": "vendor",
                "observation": "Courier missed two slots",
                "recommendation": "Book a second courier for rollouts",
            },
        ),
        w.env,
        "fix.project.lesson",
    )
    assert lesson.name.startswith("LSN/") and lesson.recorded_by_id == w.pm
    # recorded but not passed to Quality: still refused
    assert _refused(w.env, lambda: project.with_user(w.sponsor).action_complete())
    assert w.pm_api.action("fix.project.lesson", lesson, "action_share")["success"]
    assert lesson.state == "shared" and lesson.shared_by_id == w.pm
    events = (
        w.env["fix.event.outbox"]
        .sudo()
        .search([("event_type", "=", "project.lesson_recorded"), ("aggregate_id", "=", lesson.id)])
    )
    assert len(events) == 1
    assert _refused(w.env, lambda: lesson.with_user(w.pm).write({"observation": "rewritten"}))
    assert _refused(w.env, lambda: lesson.with_user(w.pm).unlink())
    result = w.sponsor_api.action("fix.project", project, "action_complete")
    assert result["success"], result
    assert project.state == "completed"


def test_an_internal_initiative_closes_only_with_a_measured_benefit(w):
    project = _active(w, project_type="internal")
    _ready_for_closure(w, project)
    lesson = (
        w.env["fix.project.lesson"]
        .with_user(w.pm)
        .create({"project_id": project.id, "observation": "o", "recommendation": "r"})
    )
    lesson.with_user(w.pm).action_share()
    err = _refused(w.env, lambda: project.with_user(w.sponsor).action_complete())
    assert "BRU-PPM-15" in err
    benefit = _created(
        w.pm_api.write(
            "fix.project.benefit",
            {
                "name": "Faster intake",
                "project_id": project.id,
                "business_case_target": 400.0,
                "unit": "hours saved per month",
                "measurement_method": "Intake log, Oct vs Dec",
            },
        ),
        w.env,
        "fix.project.benefit",
    )
    # the manager does not measure his own initiative's benefit
    assert not w.pm_api.action(
        "fix.project.benefit",
        benefit,
        "action_record_measurement",
        measured_value=380,
        evidence="intake log",
    )["success"]
    # a measurement needs its evidence
    assert not w.sponsor_api.action(
        "fix.project.benefit", benefit, "action_record_measurement", measured_value=380
    )["success"]
    result = w.sponsor_api.action(
        "fix.project.benefit",
        benefit,
        "action_record_measurement",
        measured_value=300,
        evidence="Intake log Dec 2026",
    )
    assert result["success"], result
    assert benefit.state == "measured" and benefit.realised_pct == 75.0
    assert benefit.measured_by_id == w.sponsor
    assert _refused(w.env, lambda: benefit.with_user(w.pm).write({"business_case_target": 300.0}))
    from odoo.addons.cd_p03_portal.controllers.a12 import m67

    row = next(
        r
        for r in m67.benefits_realisation(w.env(user=w.pm.id))["rows"]
        if r["project"] == project.name
    )
    assert row["benefit_baseline"] == "Faster intake: 300 of 400 hours saved per month"
    assert row["benefit_realised_pct"] == 75.0
    assert w.sponsor_api.action("fix.project", project, "action_complete")["success"]
    assert project.state == "completed"


def test_a_benefit_belongs_to_an_internal_initiative(w):
    project = _project(w, project_type="client")
    result = w.pm_api.write(
        "fix.project.benefit",
        {
            "name": "x",
            "project_id": project.id,
            "business_case_target": 1.0,
            "unit": "u",
            "measurement_method": "m",
        },
    )
    assert not result.get("id"), result


def test_the_kpis_count_the_decisions_waiting(w):
    from odoo.addons.cd_p03_portal.controllers.a12 import m67

    project = _project(w)
    before = m67.kpis(w.env(user=w.pm.id))
    change = (
        w.env["fix.project.change"]
        .with_user(w.pm)
        .create({"project_id": project.id, "title": "t", "description": "d", "justification": "j"})
    )
    change.with_user(w.pm).action_submit()
    after = m67.kpis(w.env(user=w.pm.id))
    assert after["changes_pending"] == before["changes_pending"] + 1
    assert "deliverables_awaiting" in after
