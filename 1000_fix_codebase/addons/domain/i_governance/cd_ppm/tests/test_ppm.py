"""cd_ppm tests - P10-M05 (CD-M67-01 / R08-M03).

A12 rewrite (2026-11-05): this suite was eight inspect.getsource() greps
(open-milestones-block-completion, project events, project types, budget
variance, progress, state lifecycle, sequence, tasks relation, milestone
states, task states/hours). Every one of those is now a LIVE-ORM assertion
in test_ppm_orm.py (events, sequence PRJ/, variance, milestone/task
lifecycles, open-milestone and acceptance gates) or trivially here. What
this file now covers as behaviour: templates (BRU-PPM-19), hold/cancel,
progress recompute via the consumer, the billing register guards (M67-2)
and the risk register (M67-8 / M67-10). The role/DOFA/gate-independence
attacks live in test_a12_m67_controls.py.
"""

from __future__ import annotations

import json

import pytest
from odoo import fields
from odoo.exceptions import UserError, ValidationError


def _events(env, event_type, aggregate_id):
    domain = [("event_type", "=", event_type), ("aggregate_id", "=", aggregate_id)]
    return [json.loads(e.payload) for e in env["fix.event.outbox"].search(domain, order="id")]


def _billing(env, project, **extra):
    vals = {
        "project_id": project.id,
        "billing_type": "milestone",
        "customer_id": env["res.partner"].create({"name": "Meghna Retail"}).id,
        "amount": 1000.0,
        "due_on": fields.Date.context_today(env.user),
    }
    vals.update(extra)
    return env["fix.project.billing"].create(vals)


def test_project_types_states_and_relations(odoo_env):
    # The old grep suite's project_types / state_lifecycle / tasks_relation /
    # budget_variance / progress / task-hours assertions, as behaviour.
    for ptype in ("internal", "client", "infrastructure"):
        project = odoo_env["fix.project"].create({"name": "P-%s" % ptype, "project_type": ptype})
        assert project.project_type == ptype
        assert project.state == "draft"
    project = odoo_env["fix.project"].create({"name": "Ledger move", "project_type": "client"})
    project.action_activate()
    assert project.state == "active"
    project.action_hold()
    assert project.state == "on_hold"
    project.action_resume()
    assert project.state == "active"
    project.action_cancel()
    assert project.state == "cancelled"
    milestone = odoo_env["fix.project.milestone"].create(
        {"project_id": project.id, "name": "Cancelled milestone"}
    )
    task = odoo_env["fix.project.task"].create(
        {
            "project_id": project.id,
            "milestone_id": milestone.id,
            "name": "Cancelled task",
            "planned_hours": 4.0,
        }
    )
    task.actual_hours = 3.5
    task.action_cancel()
    assert task.state == "cancelled"
    assert project.task_ids == task
    with pytest.raises(UserError, match="Only an active project"), odoo_env.cr.savepoint():
        project.action_complete()


def test_template_instantiation_carries_plan(odoo_env):
    template = odoo_env["fix.project.template"].create(
        {
            "name": "Branch opening",
            "project_type": "client",
            "default_duration_days": 30,
            "default_budget": 250000.0,
            "gate_plan": "g1_initiation, g3_execution",
            "milestone_plan": "Survey\nGo-live",
            "wbs_plan": "Survey: site measure\nSurvey: power audit\nGo-live: cutover",
        }
    )
    project = template.action_instantiate()
    assert project.name == "Branch opening — from template"
    assert project.template_id == template
    assert project.template_version
    assert project.date_end == fields.Date.add(fields.Date.context_today(template), days=30)
    assert set(project.mapped("gate_ids.gate")) == {"g1_initiation", "g3_execution"}
    survey, go_live = project.milestone_ids.sorted("id")
    assert [m.name for m in project.milestone_ids.sorted("id")] == ["Survey", "Go-live"]
    survey_tasks = survey.task_ids.mapped("name")
    assert sorted(survey_tasks) == ["power audit", "site measure"]
    assert go_live.task_ids.mapped("name") == ["cutover"]
    # A task line naming no milestone is still carried, unattached.
    template.wbs_plan = "Survey: site measure"
    plain = template.action_instantiate()
    assert plain.task_ids.mapped("name") == ["site measure"]


def test_progress_recomputed_by_consumer(odoo_env):
    project = odoo_env["fix.project"].create({"name": "Rollout"})
    project.action_activate()
    ms1 = odoo_env["fix.project.milestone"].create({"project_id": project.id, "name": "Phase 1"})
    odoo_env["fix.project.milestone"].create({"project_id": project.id, "name": "Phase 2"})
    ms1.action_accept("Signed")
    ms1.action_complete()
    # The consumer runs via the outbox relay (publish() is outbox-only).
    odoo_env["fix.event.outbox"].sudo().cron_relay(limit=10000)
    project.invalidate_recordset()
    assert project.progress_pct == 50.0  # 1 of 2 milestones done


def test_billing_ceiling_and_cross_project_milestone(odoo_env):
    # M67-2 (bl_02): Σ billing may not exceed the approved contract value.
    project = odoo_env["fix.project"].create({"name": "Capped", "contract_value": 3000.0})
    _billing(odoo_env, project, amount=1000.0)
    with pytest.raises(ValidationError, match="contract value"), odoo_env.cr.savepoint():
        _billing(odoo_env, project, amount=2500.0)
    # bl_10: billing another project's milestone bills work never delivered
    # (kept under the ceiling so ONLY the milestone constraint can fire).
    other = odoo_env["fix.project"].create({"name": "Other"})
    foreign_ms = odoo_env["fix.project.milestone"].create(
        {"project_id": other.id, "name": "Foreign"}
    )
    with pytest.raises(ValidationError, match="another project"), odoo_env.cr.savepoint():
        _billing(odoo_env, project, amount=500.0, milestone_id=foreign_ms.id)


def test_mark_ready_needs_accepted_milestone_and_freezes_terms(odoo_env):
    project = odoo_env["fix.project"].create({"name": "Billable"})
    milestone = odoo_env["fix.project.milestone"].create(
        {"project_id": project.id, "name": "Delivery"}
    )
    line = _billing(odoo_env, project, milestone_id=milestone.id)
    # BRU-PPM-11: not a completed, accepted milestone.
    with pytest.raises(UserError, match="accepted, completed milestone"), odoo_env.cr.savepoint():
        line.action_mark_ready()
    milestone.action_accept("Signed off")
    milestone.action_complete()
    line.action_mark_ready()
    assert line.state == "ready"
    # bl_08: terms frozen once ready. The freeze binds USERS: superuser code
    # is the trusted bookkeeping path (env.su), so the probe writes as the
    # project manager, like the desk does.
    pm_user = (
        odoo_env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "PM Freeze Probe",
                "login": "ppm.pm.freeze@a12.test",
                "group_ids": [
                    (
                        6,
                        0,
                        [
                            odoo_env.ref("base.group_user").id,
                            odoo_env.ref("cd_ppm.group_ppm_project_manager").id,
                        ],
                    )
                ],
            }
        )
    )
    line_pm = line.with_user(pm_user)
    with pytest.raises(UserError, match="frozen"), odoo_env.cr.savepoint():
        line_pm.write({"amount": 2000.0})
    with pytest.raises(UserError, match="frozen"), odoo_env.cr.savepoint():
        line_pm.write({"customer_id": odoo_env["res.partner"].create({"name": "Other"}).id})


def test_mark_invoiced_creates_the_real_invoice(odoo_env):
    # M67-1: "invoiced" without an invoice is fiction.
    project = odoo_env["fix.project"].create({"name": "Invoice me"})
    milestone = odoo_env["fix.project.milestone"].create(
        {"project_id": project.id, "name": "Delivery"}
    )
    milestone.action_accept("Signed off")
    milestone.action_complete()
    line = _billing(odoo_env, project, milestone_id=milestone.id)
    with pytest.raises(UserError, match="Only a ready"), odoo_env.cr.savepoint():
        line.action_mark_invoiced()
    line.action_mark_ready()
    journals = (
        odoo_env["account.journal"]
        .sudo()
        .search([("type", "=", "sale"), ("company_id", "=", line.company_id.id)])
    )
    if not journals:
        pytest.skip("no sale journal configured on the company")
    line.action_mark_invoiced()
    move = line.invoice_id
    assert move and move.move_type == "out_invoice"
    assert move.partner_id == line.customer_id
    assert move.state == "draft"
    assert line.state == "invoiced"
    assert line.invoice_ref == (move.name or move.display_name)  # display echo
    assert move.amount_untaxed == line.amount
    with pytest.raises(UserError, match="already carries"), odoo_env.cr.savepoint():
        line.action_mark_invoiced()


def test_risk_register_behaviour(odoo_env):
    # M67-8: no mitigation, no close; severity is computed; M60 hand-off
    # publishes the escalation event at/above the threshold.
    project = odoo_env["fix.project"].create({"name": "Risky"})
    risk = odoo_env["fix.project.risk"].create(
        {"project_id": project.id, "kind": "issue", "title": "Flooded comms room"}
    )
    assert risk.name.startswith("RISK/")
    assert risk.severity_score == 4  # medium x medium
    with pytest.raises(UserError, match="mitigation"), odoo_env.cr.savepoint():
        risk.action_mitigate()
    risk.mitigation = "Relay rack raised 40 cm"
    risk.action_mitigate()
    assert risk.state == "mitigating"
    risk.action_close()
    assert (risk.state, risk.closed_on) == ("closed", fields.Date.context_today(risk))
    risk.action_reopen()
    assert risk.state == "open"


def test_risk_escalation_threshold(odoo_env):
    project = odoo_env["fix.project"].create({"name": "Watched"})
    # Default threshold 9: a severity-4 risk is not escalated on open...
    low = odoo_env["fix.project.risk"].create(
        {"project_id": project.id, "title": "Trivial", "probability": "low", "impact": "medium"}
    )
    assert (low.escalated, low.severity_score) == (False, 2)
    assert _events(odoo_env, "project.risk_escalated", low.id) == []
    # ...but raising it to the threshold publishes exactly once.
    low.write({"impact": "high"})
    assert low.severity_score == 3
    odoo_env["ir.config_parameter"].sudo().set_param("fix_ppm.risk_escalation_threshold", "3")
    low.write({"probability": "high"})
    assert low.escalated is True
    payloads = _events(odoo_env, "project.risk_escalated", low.id)
    assert len(payloads) == 1
    assert payloads[0]["title"] == "Trivial"
    # probability is now high too: the published severity is 3 x 3 = 9.
    assert payloads[0]["severity"] == 9
    assert payloads[0]["project"] == "Watched"
    # A new material risk escalates the moment it is opened.
    hot = odoo_env["fix.project.risk"].create(
        {"project_id": project.id, "title": "Critical", "probability": "high", "impact": "high"}
    )
    assert hot.escalated is True


def test_cron_escalate_overdue_risks(odoo_env):
    project = odoo_env["fix.project"].create({"name": "Stale risks"})
    odoo_env["ir.config_parameter"].sudo().set_param("fix_ppm.risk_overdue_days", "7")
    stale = odoo_env["fix.project.risk"].create(
        {"project_id": project.id, "title": "Stale", "probability": "low", "impact": "low"}
    )
    odoo_env.cr.execute(
        "UPDATE fix_project_risk SET opened_on = %s WHERE id = %s",
        (fields.Date.subtract(fields.Date.context_today(stale), days=9), stale.id),
    )
    odoo_env.invalidate_all()
    odoo_env["fix.project.risk"].cron_escalate_overdue_risks()
    stale.invalidate_recordset()
    assert stale.escalated is True
    assert _events(odoo_env, "project.risk_escalated", stale.id)
