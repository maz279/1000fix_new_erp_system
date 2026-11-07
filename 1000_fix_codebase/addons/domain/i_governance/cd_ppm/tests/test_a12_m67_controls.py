"""test_a12_m67_controls.py — the A12 remediation of M67 (Projects) and
P1-3 (budget approval), probed as NON-ADMIN users where the attack was.

Source: working/A12_Workflow_and_Approval_Report.md and
working/A12_evidence/module_findings/M67.md (P1-3, M67-1..M67-11, R3, R4,
X5). Approvals are decided from the approver's inbox (approve_via_inbox);
the superuser fixture only builds the world.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from odoo.addons.cd_workflow_engine.tests.approval_helpers import (
    approve_via_inbox,
    inbox_task,
)
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
PM_GROUP = "cd_ppm.group_ppm_project_manager"
SPONSOR_GROUP = "cd_ppm.group_ppm_sponsor"
TIER2 = "cd_entity_config.group_dofa_tier_2"
TIER3 = "cd_entity_config.group_dofa_tier_3"


@pytest.fixture
def env(odoo_env):
    return odoo_env


@pytest.fixture
def make_user(env):
    counter = {"n": 0}

    def _make(*xmlids):
        counter["n"] += 1
        groups = [env.ref("base.group_user").id] + [env.ref(x).id for x in xmlids]
        return (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "M67 A12 Probe %d" % counter["n"],
                    "login": "m67.a12.probe.%d@a12.test" % counter["n"],
                    "group_ids": [(6, 0, groups)],
                }
            )
        )

    return _make


@pytest.fixture
def plain(env, make_user):
    return make_user()


@pytest.fixture
def pm_user(env, make_user):
    return make_user(PM_GROUP)


@pytest.fixture
def sponsor(env, make_user):
    return make_user(SPONSOR_GROUP)


@pytest.fixture
def tier2(env, make_user):
    return make_user(TIER2)


def _employee(env, name, user=None):
    vals = {"name": name}
    if user:
        vals["user_id"] = user.id
    return env["hr.employee"].create(vals)


def _project(env, **extra):
    vals = {
        "name": "Sylhet hub fit-out",
        "project_type": "client",
        "contract_value": 500000.0,
    }
    vals.update(extra)
    return env["fix.project"].create(vals)


def _ready_for_activation(env, project):
    """The entry conditions of F12 and F17, as the superuser builds the world."""
    if not project.manager_id:
        project.manager_id = _employee(env, "Controls Test Manager")
    for key in ("g1_initiation", "g2_planning"):
        gate = env["fix.project.gate"].create({"project_id": project.id, "gate": key})
        gate.action_record_decision("pass", checklist_passed=True)
        gate.action_hold()
        gate.action_close()
    return project


# ---------------------------------------------------------------------------
# P1-3 — the budget goes through DOFA before delivery starts
# ---------------------------------------------------------------------------


def test_p1_3_budgeted_activation_refused_without_dofa(env):
    project = _project(env, budget=250000.0)  # exactly the tier-2 band
    with pytest.raises(ValidationError, match="sign-off"):
        project.action_activate()
    assert project.state == "draft"


def test_p1_3_approved_budget_activates_and_freezes_the_baseline(env, tier2, pm_user):
    project = _project(env, budget=250000.0)
    project.action_request_approval(justification="FY27 hub expansion programme")
    assert project.approval_state == "pending"
    task = inbox_task(project, tier2)
    assert task, "the tier-2 authority received no inbox task"
    task.with_user(tier2).action_approve(comment="Capex plan page 12.")
    assert project.dofa_approved is True
    assert project.dofa_approved_tier == "tier_2"
    _ready_for_activation(env, project).action_activate()
    assert project.state == "active"
    assert project.baseline_budget == 250000.0
    # Raising the budget above the baseline is an overrun, not a field edit.
    # (The refusal fires on a USER's write; superuser code is trusted.)
    with pytest.raises(UserError, match="baselined"):
        project.with_user(pm_user).write({"budget": 400000.0})
    project.with_user(pm_user).write({"budget": 200000.0})  # lowering is fine
    assert project.budget == 200000.0


def test_p1_3_the_manager_never_approves_the_budget_they_spend(env, make_user):
    pm = make_user(PM_GROUP, TIER2)  # holds the authority AND manages it
    # The independent holder must exist BEFORE the request: approvers are
    # resolved when the request is raised, not when the inbox is read.
    outsider = make_user(TIER2)
    project = _project(env, budget=250000.0, manager_id=_employee(env, "PM Probe", pm).id)
    project.action_request_approval(justification="FY27 hub expansion programme")
    tasks = project.approval_request_id.task_ids.filtered(lambda t: t.state == "pending")
    assert pm not in tasks.mapped("assigned_user_id")
    assert outsider in tasks.mapped("assigned_user_id")
    task = inbox_task(project, outsider)
    task.with_user(outsider).action_approve(comment="Independently reviewed.")
    assert project.dofa_approved_by == outsider


def test_p1_3_editing_the_budget_after_approval_needs_a_new_round(env, make_user, tier2):
    tier3 = make_user(TIER3)  # 300,000 sits in the "up to 1M" tier-3 band
    project = _project(env, budget=250000.0)
    project.action_request_approval(justification="FY27 hub expansion programme")
    approve_via_inbox(project, tier2)
    assert project.dofa_approved is True
    # A user raising the budget voids the granted approval (amount pinned);
    # superuser writes are trusted bookkeeping and void nothing.
    project.with_user(tier2).write({"budget": 300000.0})
    assert project.approval_state != "approved"
    assert project.dofa_approved is False
    with pytest.raises(ValidationError, match="sign-off"):
        project.action_activate()
    project.action_request_approval(justification="Revised scope: two floors")
    # The tier-2 holder re-pointed the amount: whoever edited the terms never
    # signs them off (W3), and 300k is tier-3 anyway — the decision moves up.
    assert not inbox_task(project, tier2)
    approve_via_inbox(project, tier3)
    _ready_for_activation(env, project).action_activate()
    assert project.baseline_budget == 300000.0


def test_p1_3_unbudgeted_project_needs_no_dofa_approval(env):
    project = _project(env)  # no budget: Tier 0, though F12's gates still apply
    _ready_for_activation(env, project).action_activate()
    assert project.state == "active"
    assert project.baseline_budget == 0.0


# ---------------------------------------------------------------------------
# M67-6 — gate review is independent and a failed gate blocks
# ---------------------------------------------------------------------------


def test_m67_6_the_manager_never_reviews_his_own_gate(env, pm_user):
    manager = _employee(env, "PM Gate Probe", pm_user)
    project = _project(env, manager_id=manager.id)
    with pytest.raises(ValidationError, match="independent"):
        env["fix.project.gate"].create(
            {"project_id": project.id, "gate": "g2_planning", "reviewer_id": manager.id}
        )


def test_m67_6_gate_decision_is_the_reviewers_not_the_managers(env, pm_user, sponsor):
    manager = _employee(env, "PM Decision Probe", pm_user)
    reviewer_user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "Gate Reviewer",
                "login": "m67.reviewer@a12.test",
                # The gate register is writable by the sponsor group only (lead's
                # CSV): an independent reviewer records his verdict holding it.
                "group_ids": [
                    (
                        6,
                        0,
                        [env.ref("base.group_user").id, env.ref(SPONSOR_GROUP).id],
                    )
                ],
            }
        )
    )
    reviewer = _employee(env, "Reviewer Probe", reviewer_user)
    project = _project(env, manager_id=manager.id)
    _ready_for_activation(env, project).action_activate()
    gate = env["fix.project.gate"].create(
        {"project_id": project.id, "gate": "g2_planning", "reviewer_id": reviewer.id}
    )
    Gate = env["fix.project.gate"].with_user(pm_user)
    with pytest.raises(UserError, match="reviewer or a project sponsor"):
        Gate.browse(gate.id).action_record_decision("pass", checklist_passed=True)
    # The reviewer records a fail without findings: refused.
    ReviewerGate = env["fix.project.gate"].with_user(reviewer_user)
    with pytest.raises(UserError, match="findings"):
        ReviewerGate.browse(gate.id).action_record_decision("fail")
    ReviewerGate.browse(gate.id).action_record_decision(
        "fail", findings="Capacity plan missing the generator load."
    )
    assert gate.decision == "fail"
    # The decision and state are not forgeable by write, even by the sponsor.
    with pytest.raises(REFUSED):
        env["fix.project.gate"].with_user(sponsor).browse(gate.id).write(
            {"decision": "pass", "state": "closed"}
        )
    # A passing gate needs its checklist before the review is held.
    gate2 = env["fix.project.gate"].create(
        {"project_id": project.id, "gate": "g3_execution", "reviewer_id": reviewer.id}
    )
    ReviewerGate2 = env["fix.project.gate"].with_user(reviewer_user)
    ReviewerGate2.browse(gate2.id).action_record_decision("pass")
    with pytest.raises(UserError, match="checklist"):
        ReviewerGate2.browse(gate2.id).action_hold()
    # The lifecycle is scheduled -> held -> closed: a review that was never
    # held cannot close.
    with pytest.raises(UserError, match="held"):
        ReviewerGate2.browse(gate2.id).action_close()
    ReviewerGate2.browse(gate2.id).action_record_decision("pass", checklist_passed=True)
    ReviewerGate2.browse(gate2.id).action_hold()
    assert gate2.state == "held"
    ReviewerGate2.browse(gate2.id).action_close()
    assert gate2.state == "closed"


def test_m67_6_a_failed_gate_blocks_activation(env, sponsor):
    project = _project(env)
    gate = env["fix.project.gate"].create(
        {
            "project_id": project.id,
            "gate": "g1_initiation",
            "reviewer_id": _employee(env, "Independent reviewer").id,
        }
    )
    env["fix.project.gate"].with_user(sponsor).browse(gate.id).action_record_decision(
        "fail", findings="No signed charter."
    )
    project.manager_id = _employee(env, "Failed Gate Manager")
    with pytest.raises(UserError, match="closed as FAIL"):
        project.action_activate()
    # And a recorded G1 that has not CLOSED with pass/conditional does not
    # clear the entry gate either. (The decision reset is superuser code; the
    # guard trusts env.su.)
    gate.decision = False
    with pytest.raises(UserError, match="G1"):
        project.action_activate()


def test_m67_6_sponsor_records_the_decision_when_no_reviewer_is_named(env, sponsor):
    project = _project(env)
    _ready_for_activation(env, project).action_activate()
    gate = env["fix.project.gate"].create({"project_id": project.id, "gate": "g4_uat"})
    env["fix.project.gate"].with_user(sponsor).browse(gate.id).action_record_decision(
        "conditional", checklist_passed=True, findings="UAT report pending signature."
    )
    assert gate.decision == "conditional"


# ---------------------------------------------------------------------------
# BRU-PPM-11 — the manager cannot accept his own milestone
# ---------------------------------------------------------------------------


def test_bru_ppm_11_manager_cannot_accept_own_milestone(env, pm_user, sponsor):
    manager = _employee(env, "PM Acceptance Probe", pm_user)
    project = _project(env, manager_id=manager.id)
    _ready_for_activation(env, project).action_activate()
    milestone = env["fix.project.milestone"].create({"project_id": project.id, "name": "Go-live"})
    Milestone = env["fix.project.milestone"].with_user(pm_user)
    with pytest.raises(UserError, match="cannot accept"):
        Milestone.browse(milestone.id).action_accept("PM sign-off SO-1")
    env["fix.project.milestone"].with_user(sponsor).browse(milestone.id).action_accept(
        "Client sign-off SO-4471"
    )
    assert milestone.accepted_by_id == sponsor
    assert milestone.acceptance_note == "Client sign-off SO-4471"


# ---------------------------------------------------------------------------
# R3 / FF-48 — the crons and consumers the module ships exist
# ---------------------------------------------------------------------------


def test_r3_cron_records_exist(env):
    Cron = env["ir.cron"].sudo()
    for code, model in (
        ("model.cron_flag_overdue_milestones()", "fix.project.milestone"),
        ("model.cron_escalate_overdue_risks()", "fix.project.risk"),
    ):
        rows = Cron.search([("code", "=", code), ("model_id.model", "=", model)])
        assert rows, "no ir.cron record for %s on %s (FF-48)" % (code, model)
        assert rows.filtered("active")


def test_r3_consumers_exist_for_every_cd_ppm_event(env):
    Consumer = env["fix.event.consumer"].sudo()
    expected = {
        "project.created": ("fix.project", "consume_project_created"),
        "project.milestone_completed": (
            "fix.project.milestone",
            "consume_project_milestone_completed",
        ),
        "project.completed": ("fix.project", "consume_project_completed"),
        "project.risk_escalated": ("fix.project.risk", "consume_project_risk_escalated"),
    }
    for event_type, (model, method) in expected.items():
        rows = Consumer.search([("event_type", "=", event_type), ("model", "=", model)])
        assert rows, "no fix.event.consumer for %s" % event_type
        assert method in rows.mapped("method")
    for row in Consumer.search([("module", "=", "cd_ppm")]):
        assert callable(getattr(env[row.model], row.method, None)), row.method


# ---------------------------------------------------------------------------
# R4 / X5 — surface whitelists, buttons and caller-scope reads
# ---------------------------------------------------------------------------


def test_r4_every_surface_declares_its_writable_whitelist():
    from odoo.addons.cd_p03_portal.controllers.a12 import m67 as m67_ctrl

    assert set(m67_ctrl.WRITABLE) == set(m67_ctrl.SURFACES)
    for model, writable in m67_ctrl.WRITABLE.items():
        forbidden = {
            "state",
            "decision",
            "baseline_budget",
            "accepted_by_id",
            "accepted_on",
            "invoice_id",
            "invoiced_on",
            "invoice_ref",
            "escalated",
            "closed_on",
            "approval_state",
            "progress_pct",  # M67-7: computed by the consumer, never typed
        }
        assert not (forbidden & set(writable)), model
    # the gate's reviewer evidence is writable; the verdict is action-only
    assert "checklist_passed" in m67_ctrl.WRITABLE["fix.project.gate"]
    assert "decision" not in m67_ctrl.WRITABLE["fix.project.gate"]


def test_r4_every_js_button_is_whitelisted():
    from odoo.addons.cd_p03_portal.controllers.a12 import m67 as m67_ctrl

    js = (Path(m67_ctrl.__file__).parents[2] / "static" / "src" / "a12" / "m67.js").read_text(
        encoding="utf-8"
    )
    used = set(re.findall(r"m:\s*'(action_[a-z_]+)'", js))
    declared = set()
    for conf in m67_ctrl.SURFACES.values():
        declared |= set(conf["actions"])
    assert used <= declared, "buttons without a surface action whitelist: %s" % sorted(
        used - declared
    )


def test_x5_m67_kpis_count_real_invoices(env, plain):
    from odoo.addons.cd_p03_portal.controllers.a12 import m67 as m67_ctrl

    env.company.partner_id.vat = "1234567890123"
    project = _project(env)
    _ready_for_activation(env, project).action_activate()
    milestone = env["fix.project.milestone"].create({"project_id": project.id, "name": "Delivery"})
    milestone.action_accept("Client sign-off SO-9001")
    milestone.action_complete()
    customer = env["res.partner"].create({"name": "Meghna Retail"})
    line = env["fix.project.billing"].create(
        {
            "project_id": project.id,
            "milestone_id": milestone.id,
            "customer_id": customer.id,
            "amount": 1500.0,
        }
    )
    line.action_mark_ready()
    journals = (
        env["account.journal"]
        .sudo()
        .search([("type", "=", "sale"), ("company_id", "=", line.company_id.id)])
    )
    if not journals:
        pytest.skip("no sale journal configured on the company")
    line.action_mark_invoiced()
    caller = env(user=plain)  # Environment.__call__: the portal's caller env
    kpis = m67_ctrl.kpis(caller)
    invoiced = caller["fix.project.billing"].search_count([("invoice_id", "!=", False)])
    assert kpis["billings_invoiced"] == invoiced
    assert line.invoice_id.move_type == "out_invoice"
    # the invoices KPI is caller-scope readable too
    report = m67_ctrl.billing_status(caller)
    mine = [r for r in report["rows"] if r.get("billing") == line.name]
    assert mine and mine[0].get("invoice"), "the real invoice name is on the row"


# ---------------------------------------------------------------------------
# M67-5 — plain staff read the registers but cannot forge them
# ---------------------------------------------------------------------------


def test_m67_5_registers_read_only_for_staff(env, plain):
    for model, vals in (
        ("fix.project", {"name": "Forged project"}),
        ("fix.project.milestone", {"name": "Forged milestone", "project_id": _project(env).id}),
        ("fix.project.billing", {"project_id": _project(env).id, "amount": 1.0}),
        ("fix.project.risk", {"project_id": _project(env).id, "title": "Forged risk"}),
    ):
        with pytest.raises(AccessError):
            env[model].with_user(plain).create(vals)
    project = _project(env)
    # state is a guarded field: the guard refuses it BEFORE the ACL raises.
    with pytest.raises(REFUSED, match="cannot be set directly"):
        env["fix.project"].with_user(plain).browse(project.id).write({"state": "active"})
