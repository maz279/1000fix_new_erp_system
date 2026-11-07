"""A12 finish build, M67: findings F1-F20, lifecycle rows 10 and 11, BRU-PPM-07/-12/-20.

Source: working/A12_evidence/finish/m64_m67/FINDINGS.md. Every workflow is walked
as a NON-ADMIN role holder through the same controller the screen calls, with the
kwargs the screen sends. Finance tests run on the MD-035 chart linked as on live.
Hand-offs use the real publisher and cron_relay.
"""

from __future__ import annotations

import re
import sys
import types
from pathlib import Path

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
PM = "cd_ppm.group_ppm_project_manager"
SPONSOR = "cd_ppm.group_ppm_sponsor"
AGENT = "cd_itsm.group_itsm_agent"
T2 = "cd_entity_config.group_dofa_tier_2"
T3 = "cd_entity_config.group_dofa_tier_3"
T4 = "cd_entity_config.group_dofa_tier_4"
JUSTIFICATION = "FY27 programme, capex plan page 12"


class World:
    """The role holders of one test."""


def _user(env, login, *groups):
    gids = [env.ref("base.group_user").id] + [env.ref(x).id for x in groups]
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create({"name": login, "login": login + "@a12f.test", "group_ids": [(6, 0, gids)]})
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


def _screen_source():
    from odoo.addons.cd_p03_portal.controllers.a12 import m67

    return (Path(m67.__file__).parents[2] / "static" / "src" / "a12" / "m67.js").read_text(
        encoding="utf-8"
    )


def _button(source, method):
    """The screen's button for `method`, as text."""
    found = re.search(r"\{ m: '%s'.*" % method, source)
    assert found, "no button for %s" % method
    return found.group(0)


@pytest.fixture
def w(odoo_env):
    world = World()
    env = odoo_env
    world.env = env
    world.pm, world.pm_emp = _user(env, "a12f.pm", PM)
    world.pm2, world.pm2_emp = _user(env, "a12f.pm2", PM)
    world.sponsor, world.sponsor_emp = _user(env, "a12f.sponsor", SPONSOR)
    world.reviewer, world.reviewer_emp = _user(env, "a12f.reviewer")
    world.plain, world.plain_emp = _user(env, "a12f.plain")
    world.agent, world.agent_emp = _user(env, "a12f.agent", AGENT)
    world.t2, _e = _user(env, "a12f.t2", T2)
    world.t3, _e = _user(env, "a12f.t3", T3)
    world.t4, _e = _user(env, "a12f.t4", T4)
    world.accountant, _e = _user(env, "a12f.accountant", "account.group_account_user")
    world.billing, _e = _user(env, "a12f.billing", "account.group_account_invoice")
    world.customer = env["res.partner"].create({"name": "A12F Customer"})
    return world


@pytest.fixture
def linked(w):
    """The company on the MD-035 chart, as live is."""
    env = w.env
    env.company.partner_id.vat = "1234567890123"
    harness = next(
        module
        for name, module in sys.modules.items()
        if name.endswith("conftest") and hasattr(module, "link_statutory_chart")
    )
    harness.link_statutory_chart(env)
    harness._head_office_branch(env, env.company)
    return w


def _project(w, budget=200000.0, contract=500000.0, manager=True, user=None, **extra):
    vals = {
        "name": "A12F Project",
        "project_type": "client",
        "budget": budget,
        "contract_value": contract,
        "manager_id": w.pm_emp.id if manager else False,
    }
    vals.update(extra)
    return w.env["fix.project"].with_user(user or w.pm).create(vals)


def _task_of(project, user):
    return project.sudo().approval_request_id.task_ids.filtered(
        lambda t: t.state == "pending" and t.assigned_user_id == user
    )


def _approve(w, project, approver=None):
    project.with_user(w.pm).action_request_approval(justification=JUSTIFICATION)
    approver = approver or w.t2
    task = _task_of(project, approver)
    assert task, "setup: no task for %s" % approver.login
    task.with_user(approver).action_approve(comment="ok")
    assert project.dofa_approved, "setup: not approved"
    return project


def _gate(w, project, kind="g1_initiation", reviewer=None):
    return w.env["fix.project.gate"].create(
        {"project_id": project.id, "gate": kind, "reviewer_id": reviewer.id if reviewer else False}
    )


def _decided(w, project, decision="pass", kind="g1_initiation"):
    gate = _gate(w, project, kind=kind)
    gate.with_user(w.sponsor).action_record_decision(
        decision=decision, checklist_passed=True, findings="reviewed"
    )
    gate.with_user(w.sponsor).action_hold()
    gate.with_user(w.sponsor).action_close()
    return gate


def _gates_passed(w, project):
    _decided(w, project, kind="g1_initiation")
    _decided(w, project, kind="g2_planning")
    return project


def _active(w, **kw):
    project = _project(w, **kw)
    if project.budget:
        _approve(w, project)
    _gates_passed(w, project)
    project.with_user(w.pm).action_activate()
    assert project.state == "active"
    return project


def _accepted_milestone(w, project, name="A12F MS"):
    milestone = (
        w.env["fix.project.milestone"]
        .with_user(w.pm)
        .create({"name": name, "project_id": project.id})
    )
    milestone.with_user(w.sponsor).action_accept(acceptance_note="client sign-off 12")
    milestone.with_user(w.pm).action_complete()
    return milestone


def _bill(w, project, milestone=None, amount=100000.0, **extra):
    vals = {
        "project_id": project.id,
        "amount": amount,
        "customer_id": w.customer.id,
        "billing_type": "milestone" if milestone else "time_material",
        "milestone_id": milestone.id if milestone else False,
    }
    vals.update(extra)
    return w.env["fix.project.billing"].with_user(w.pm).create(vals)


def _invoiced(w, project=None, **extra):
    project = project or _active(w)
    line = _bill(w, project, _accepted_milestone(w, project), **extra)
    line.with_user(w.pm).action_mark_ready()
    result = Api(w.env, w.billing).action("fix.project.billing", line, "action_mark_invoiced")
    assert result["success"], result
    return line


def _refused(env, fn):
    try:
        with env.cr.savepoint():
            fn()
    except REFUSED as exc:
        return str(exc) or type(exc).__name__
    return None


def _risk(w, project=None, user=None, **extra):
    vals = {
        "project_id": (project or _project(w)).id,
        "title": "A12F risk",
        "probability": "high",
        "impact": "high",
    }
    vals.update(extra)
    return w.env["fix.project.risk"].with_user(user or w.pm).create(vals)


# =================== F1: budget approval from the workspace ===================


def test_a12f_f1_the_button_asks_for_the_justification():
    button = _button(_screen_source(), "action_request_approval")
    assert "ask:" in button and "kwarg: 'justification'" in button


def test_a12f_f1_budget_approved_from_the_workspace_with_the_kwarg_the_button_sends(w):
    project = _project(w)
    pm_api = Api(w.env, w.pm)
    result = pm_api.action(
        "fix.project", project, "action_request_approval", justification=JUSTIFICATION
    )
    assert result["success"], result
    task = _task_of(project, w.t2)
    result = Api(w.env, w.t2).action("fix.workflow.task", task, "action_approve", comment="ok")
    assert result["success"], result
    assert project.dofa_approved and project.dofa_justification == JUSTIFICATION


def test_a12f_f1_blank_justification_is_refused_at_the_request_with_a_plain_message(w):
    project = _project(w)
    result = Api(w.env, w.pm).action(
        "fix.project", project, "action_request_approval", justification=""
    )
    assert not result["success"] and "justification" in result["error"]
    assert project.approval_state == "none"


def test_a12f_f1_justification_is_on_the_form_and_pinned_while_the_approval_stands(w):
    project = _project(w)
    api = Api(w.env, w.pm)
    form = api.form("fix.project", ["dofa_justification"], project.id)
    assert not form["fields"][0]["readonly"]
    assert not api.write("fix.project", {"dofa_justification": JUSTIFICATION}, project.id).get(
        "error"
    )
    # Typed on the form and not at the prompt: it still travels with the request.
    project.with_user(w.pm).action_request_approval()
    assert _task_of(project, w.t2)
    assert project.sudo().approval_request_id.justification == JUSTIFICATION
    assert api.write("fix.project", {"dofa_justification": "rewritten"}, project.id).get("error")
    assert _refused(w.env, lambda: project.with_user(w.pm).write({"dofa_justification": "x"}))


def test_a12f_f1_holds_when_the_engine_itself_refuses_a_blank_request(w, monkeypatch):
    """A cd_workflow_engine change on its way refuses a Tier 2+ request with no
    justification at request time. Stated at the prompt or on the form, the project's
    request carries one to the engine, and the approver's decision still works."""
    from odoo.addons.cd_workflow_engine.models.fix_approval_engine import FixApprovableMixin

    original = FixApprovableMixin.action_request_approval

    def strict(self, justification=None):
        if not (justification or "").strip():
            raise UserError("The engine refuses a Tier 2+ request with no justification.")
        return original(self, justification=justification)

    monkeypatch.setattr(FixApprovableMixin, "action_request_approval", strict)
    api = Api(w.env, w.pm)
    at_the_prompt = _project(w)
    result = api.action(
        "fix.project", at_the_prompt, "action_request_approval", justification=JUSTIFICATION
    )
    assert result["success"], result
    on_the_form = _project(w)
    api.write("fix.project", {"dofa_justification": JUSTIFICATION}, on_the_form.id)
    result = api.action("fix.project", on_the_form, "action_request_approval", justification="")
    assert result["success"], result
    for project in (at_the_prompt, on_the_form):
        task = _task_of(project, w.t2)
        result = Api(w.env, w.t2).action("fix.workflow.task", task, "action_approve", comment="ok")
        assert result["success"], result
        assert project.dofa_approved
    blank = _project(w)
    result = api.action("fix.project", blank, "action_request_approval", justification=" ")
    assert not result["success"] and "justification" in result["error"]


# =================== F2: zero or missing baseline ===================


def test_a12f_f2_zero_baseline_does_not_open_the_budget(w):
    project = _active(w, budget=0.0)
    assert project.state == "active"
    err = _refused(w.env, lambda: project.with_user(w.pm).write({"budget": 50000000.0}))
    assert "baselined" in err
    assert project.budget == 0.0


def test_a12f_f2_legacy_active_project_with_null_baseline_takes_no_raise(w):
    project = _project(w, budget=1000000.0)
    w.env.cr.execute(
        "UPDATE fix_project SET state='active', baseline_budget=NULL WHERE id=%s", (project.id,)
    )
    project.invalidate_recordset()
    assert _refused(w.env, lambda: project.with_user(w.pm).write({"budget": 10000000.0}))
    assert project.budget == 1000000.0
    # The form posts every field it shows: the unchanged value still saves, and
    # lowering stays open.
    assert not Api(w.env, w.pm).write("fix.project", {"budget": 1000000.0}, project.id).get("error")
    project.with_user(w.pm).write({"budget": 900000.0})


def test_a12f_f2_lowered_budget_can_return_to_its_baseline_but_not_above(w):
    project = _active(w)
    project.with_user(w.pm).write({"budget": 100000.0})
    project.with_user(w.pm).write({"budget": 200000.0})
    assert _refused(w.env, lambda: project.with_user(w.pm).write({"budget": 200001.0}))


# =================== F3 / BRU-PPM-07: overrun ===================


def test_a12f_f3_overrun_routes_at_its_own_tier_and_rebaselines(w):
    project = _active(w)
    assert project.baseline_budget == 200000.0
    api = Api(w.env, w.pm)
    # The direct raise still refuses, and says where to go.
    assert "Requested Budget" in api.write("fix.project", {"budget": 300000.0}, project.id).get(
        "error", ""
    ) or _refused(w.env, lambda: project.with_user(w.pm).write({"budget": 300000.0}))
    assert not api.write("fix.project", {"budget_requested": 400000.0}, project.id).get("error")
    assert project.budget == 200000.0
    result = api.action(
        "fix.project", project, "action_request_approval", justification="Scope grew by two floors"
    )
    assert result["success"], result
    assert not _task_of(project, w.t2), "400k is tier 3: the tier-2 holder is not asked"
    task = _task_of(project, w.t3)
    assert task
    # Still the old baseline while it is only requested.
    assert project.baseline_budget == 200000.0 and project.state == "active"
    result = Api(w.env, w.t3).action("fix.workflow.task", task, "action_approve", comment="ok")
    assert result["success"], result
    assert project.baseline_budget == 400000.0
    assert project.budget == 400000.0 and not project.budget_requested
    assert project.approval_state == "approved" and project.dofa_approved_tier == "tier_3"


def test_a12f_f3_rejected_overrun_leaves_the_baseline(w):
    project = _active(w)
    project.with_user(w.pm).write({"budget_requested": 400000.0})
    project.with_user(w.pm).action_request_approval(justification="More scope")
    _task_of(project, w.t3).with_user(w.t3).action_reject(comment="Not this year")
    assert project.approval_state == "rejected"
    assert project.baseline_budget == 200000.0 and project.budget == 200000.0


def test_a12f_f3_request_on_a_running_project_needs_a_new_figure(w):
    project = _active(w)
    err = _refused(
        w.env, lambda: project.with_user(w.pm).action_request_approval(justification="x")
    )
    assert "Requested Budget" in err


def test_a12f_f3_requested_figures_are_for_running_projects(w):
    project = _project(w)
    assert _refused(w.env, lambda: project.with_user(w.pm).write({"budget_requested": 1.0}))
    assert Api(w.env, w.pm).form("fix.project", ["budget_requested"])["fields"][0]["readonly"]


def test_a12f_f3_contract_variation_goes_through_the_same_approval(w):
    project = _active(w)
    project.with_user(w.pm).write({"contract_value_requested": 900000.0})
    project.with_user(w.pm).action_request_approval(justification="Contract addendum 2")
    task = _task_of(project, w.t3)
    assert task, "900k is tier 3"
    assert project.contract_value == 500000.0
    task.with_user(w.t3).action_approve(comment="ok")
    assert project.contract_value == 900000.0 and not project.contract_value_requested
    assert project.approval_state == "approved", "granting a variation does not void itself"


def test_a12f_f3_regularising_a_legacy_project_sets_the_baseline(w):
    project = _project(w, budget=200000.0)
    w.env.cr.execute("UPDATE fix_project SET state='on_hold' WHERE id=%s", (project.id,))
    project.invalidate_recordset()
    err = _refused(w.env, lambda: project.with_user(w.pm).action_resume())
    assert "baseline" in err
    project.with_user(w.pm).action_request_approval(justification="Regularising")
    _task_of(project, w.t2).with_user(w.t2).action_approve(comment="ok")
    assert project.baseline_budget == 200000.0


# =================== F4: risk mitigate and close ===================


def test_a12f_f4_mitigate_button_stores_what_it_asks_for(w):
    button = _button(_screen_source(), "action_mitigate")
    assert "kwarg: 'mitigation'" in button
    risk = _risk(w, probability="medium", impact="medium")
    api = Api(w.env, w.pm)
    result = api.action("fix.project.risk", risk, "action_mitigate", mitigation="Vendor cover")
    assert result["success"], result
    assert risk.state == "mitigating" and risk.mitigation == "Vendor cover"
    result = api.action("fix.project.risk", risk, "action_close")
    assert result["success"], result
    assert risk.state == "closed" and risk.closed_on


def test_a12f_f4_blank_mitigation_refused_with_a_message_not_a_crash(w):
    risk = _risk(w, probability="medium", impact="medium")
    result = Api(w.env, w.pm).action("fix.project.risk", risk, "action_mitigate", mitigation="  ")
    assert not result["success"] and "mitigation" in result["error"]


def test_a12f_f4_mitigation_is_on_the_form_and_frozen_when_closed(w):
    risk = _risk(w, probability="medium", impact="medium")
    api = Api(w.env, w.pm)
    assert "name: 'mitigation'" in _screen_source()
    assert not api.form("fix.project.risk", ["mitigation"], risk.id)["fields"][0]["readonly"]
    assert not api.write("fix.project.risk", {"mitigation": "Plan"}, risk.id).get("error")
    risk.with_user(w.pm).action_close()
    assert api.form("fix.project.risk", ["mitigation"], risk.id)["fields"][0]["readonly"]
    assert _refused(w.env, lambda: risk.with_user(w.pm).write({"mitigation": "rewritten"}))


# =================== F5 / BRU-PPM-20: the M60 hand-off ===================


def test_a12f_f5_severity_9_lands_in_m60_through_the_real_publisher_and_relay(w):
    env = w.env
    Register = env["fix.risk.register"].sudo()
    before = Register.search_count([])
    risk = _risk(w, title="Sev9 hand-off", mitigation="Generator on standby")
    assert risk.severity_score == 9 and risk.escalated
    env["fix.event.outbox"].sudo().cron_relay(limit=10000)
    assert Register.search_count([]) == before + 1
    entry = Register.search([("name", "like", risk.name)])
    assert entry.risk_score == 25 and entry.state == "open"
    assert "Generator on standby" in entry.mitigation
    event = (
        env["fix.event.outbox"]
        .sudo()
        .search(
            [("event_type", "=", "project.risk_escalated"), ("aggregate_id", "=", risk.id)],
            limit=1,
        )
    )
    deliveries = env["fix.event.consumer.delivery"].sudo().search([("event_id", "=", event.id)])
    assert deliveries, "the relay handed the event to nobody"
    assert set(deliveries.mapped("state")) == {"done"}, deliveries.mapped("last_error")
    assert "cd_grc" in deliveries.mapped("subscription_id.module")


def test_a12f_f5_the_echo_no_longer_claims_delivery(w):
    risk = _risk(w, title="Echo text")
    w.env["fix.event.outbox"].sudo().cron_relay(limit=10000)
    bodies = " ".join(risk.sudo().message_ids.mapped("body"))
    assert "delivered" not in bodies
    assert "Entered on the enterprise risk register" in bodies


def test_a12f_f5_relay_twice_makes_one_entry(w):
    risk = _risk(w, title="Twice")
    Outbox = w.env["fix.event.outbox"].sudo()
    Outbox.cron_relay(limit=10000)
    Outbox.search([("aggregate_id", "=", risk.id), ("event_type", "like", "project.risk")]).write(
        {"relayed_at": False}
    )
    Outbox.cron_relay(limit=10000)
    assert w.env["fix.risk.register"].sudo().search_count([("name", "like", risk.name)]) == 1


# =================== F6 / F14: Finance invoices and posts ===================


def test_a12f_f6_invoiced_means_posted_through_m19_on_the_linked_chart(linked):
    w = linked
    project = _active(w)
    line = _bill(w, project, _accepted_milestone(w, project))
    line.with_user(w.pm).action_mark_ready()
    result = Api(w.env, w.billing).action("fix.project.billing", line, "action_mark_invoiced")
    assert result["success"], result
    assert line.state == "invoiced"
    move = line.sudo().invoice_id
    assert move.state == "posted" and move.move_type == "out_invoice"
    assert move.partner_id == w.customer and move.amount_total == 100000.0
    assert line.invoice_ref == move.name
    # M19's marks: dimensions on every line, the project among them, and the log.
    dims = w.env["fix.journal.dimension"].sudo().search([("move_line_id", "in", move.line_ids.ids)])
    assert set(dims.mapped("project_ref")) == {project.code}
    # The live chart's income account requires these three (COA-03).
    income = dims.filtered(lambda d: d.move_line_id.account_id.account_type == "income")
    assert income and all(d.branch_id and d.cost_centre and d.business_line for d in income)
    log = w.env["fix.journal.posting.log"].sudo().search([("move_id", "=", move.id)])
    assert log.source == "ar" and log.source_ref == line.name
    assert log.posted_by == w.billing
    assert (
        w.env["fix.event.outbox"]
        .sudo()
        .search_count([("event_type", "=", "journal.posted"), ("aggregate_id", "=", move.id)])
    )


def test_a12f_f6_accountant_role_invoices_too(linked):
    w = linked
    project = _active(w)
    line = _bill(w, project, _accepted_milestone(w, project))
    line.with_user(w.pm).action_mark_ready()
    result = Api(w.env, w.accountant).action("fix.project.billing", line, "action_mark_invoiced")
    assert result["success"], result
    assert line.sudo().invoice_id.state == "posted"


def test_a12f_f14_the_pm_stops_at_ready(linked):
    w = linked
    project = _active(w)
    line = _bill(w, project, _accepted_milestone(w, project))
    line.with_user(w.pm).action_mark_ready()
    result = Api(w.env, w.pm).action("fix.project.billing", line, "action_mark_invoiced")
    assert not result["success"] and "Finance" in result["error"]
    assert line.state == "ready" and not line.invoice_id
    for user in (w.sponsor, w.plain):
        assert _refused(w.env, lambda u=user: line.with_user(u).action_mark_invoiced())


def test_a12f_f14_a_finance_user_running_the_project_does_not_invoice_it(linked):
    w = linked
    both, emp = _user(w.env, "a12f.pm.finance", PM, "account.group_account_invoice")
    project = _active(w, manager_id=emp.id)
    line = _bill(w, project, _accepted_milestone(w, project))
    line.with_user(w.pm).action_mark_ready()
    err = _refused(w.env, lambda: line.with_user(both).action_mark_invoiced())
    assert "Segregation of duties" in err


def test_a12f_f6_a_posting_refused_leaves_nothing_behind(linked):
    w = linked
    project = _active(w)
    line = _bill(w, project, _accepted_milestone(w, project))
    line.with_user(w.pm).action_mark_ready()
    moves = w.env["account.move"].sudo().search_count([])
    # With no default dimension, COA-03 refuses the income line.
    params = w.env["ir.config_parameter"].sudo()
    params.set_param("cd_gl_ext.default_cost_centre", False)
    result = Api(w.env, w.billing).action("fix.project.billing", line, "action_mark_invoiced")
    assert not result["success"] and "Posting refused" in result["error"]
    assert line.state == "ready" and not line.invoice_id
    assert w.env["account.move"].sudo().search_count([]) == moves


# =================== F7: Billing Status ===================


def test_a12f_f7_billing_status_works_for_roles_without_account_access(linked):
    from odoo.addons.cd_p03_portal.controllers.a12 import m67

    w = linked
    line = _invoiced(w)
    w.env.flush_all()
    w.env.invalidate_all()
    for user in (w.pm, w.sponsor, w.plain):
        out = m67.billing_status(w.env(user=user.id))
        row = next(r for r in out["rows"] if r["billing"] == line.name)
        assert row["real_invoice"] == "Yes"
        assert line.sudo().invoice_id.name in row["invoice"]
    for user in (w.pm, w.sponsor, w.plain):
        records = Api(w.env, user).records("fix.project.billing", ["name", "invoice_id", "state"])
        assert not records.get("error"), records


# =================== F8: the ceiling ===================


def test_a12f_f8_client_project_needs_a_contract_value_to_activate(w):
    project = _project(w, contract=False)
    _approve(w, project)
    _gates_passed(w, project)
    err = _refused(w.env, lambda: project.with_user(w.pm).action_activate())
    assert "contract value" in err
    # The contract is pinned: recording it voided the approval, which has to come back.
    project.with_user(w.pm).write({"contract_value": 500000.0})
    assert project.approval_state == "none" and not project.dofa_approved
    assert _refused(w.env, lambda: project.with_user(w.pm).action_activate())
    _approve(w, project)
    project.with_user(w.pm).action_activate()
    assert project.state == "active" and project.contract_value == 500000.0


def test_a12f_f8_required_types_are_a_parameter(w):
    w.env["ir.config_parameter"].sudo().set_param(
        "fix_ppm.contract_value_required_types", "internal"
    )
    client = _active(w, contract=False)
    assert client.state == "active"
    internal = _project(w, budget=0.0, contract=False, project_type="internal")
    _gates_passed(w, internal)
    assert _refused(w.env, lambda: internal.with_user(w.pm).action_activate())


def test_a12f_f8_ceiling_falls_back_to_the_baseline(w):
    project = _active(w, contract=False, project_type="internal")
    err = _refused(w.env, lambda: _bill(w, project, amount=3000000.0))
    assert "exceed" in err
    _bill(w, project, amount=200000.0)
    assert _refused(w.env, lambda: _bill(w, project, amount=1.0))


def test_a12f_f8_contract_is_frozen_on_a_running_project(w):
    project = _active(w)
    result = Api(w.env, w.pm).write("fix.project", {"contract_value": 99000000.0}, project.id)
    assert result.get("error")
    assert _refused(w.env, lambda: project.with_user(w.pm).write({"contract_value": 99000000.0}))
    assert project.contract_value == 500000.0
    for name in ("project_type", "currency_id"):
        value = "internal" if name == "project_type" else w.env.ref("base.USD").id
        assert _refused(w.env, lambda n=name, v=value: project.with_user(w.pm).write({n: v}))


# =================== F9: cancelling a line ===================


def test_a12f_f9_a_mistaken_line_cancels_and_leaves_the_ceiling_and_the_closure(w):
    project = _active(w, contract=300000.0)
    line = _bill(w, project, amount=250000.0)
    assert _refused(w.env, lambda: _bill(w, project, amount=100000.0))
    button = _button(_screen_source(), "action_cancel', l: 'Cancel Line")
    assert "kwarg: 'reason'" in button
    api = Api(w.env, w.pm)
    assert not api.action("fix.project.billing", line, "action_cancel", reason=" ")["success"]
    result = api.action("fix.project.billing", line, "action_cancel", reason="Raised twice")
    assert result["success"], result
    assert line.state == "cancelled" and line.cancel_reason == "Raised twice"
    _bill(w, project, amount=100000.0)  # the room came back


def test_a12f_f9_invoiced_line_is_reversed_not_cancelled(linked):
    w = linked
    line = _invoiced(w)
    err = _refused(w.env, lambda: line.with_user(w.pm).action_cancel(reason="oops"))
    assert "reverses" in err


def test_a12f_f9_legacy_ready_line_without_customer_is_not_stranded(linked):
    w = linked
    project = _active(w)
    line = _bill(w, project, customer_id=False, amount=900.0)
    w.env.cr.execute("UPDATE fix_project_billing SET state='ready' WHERE id=%s", (line.id,))
    line.invalidate_recordset()
    assert _refused(w.env, lambda: line.with_user(w.billing).action_mark_invoiced())
    line.with_user(w.pm).write({"customer_id": w.customer.id})
    line.with_user(w.billing).action_mark_invoiced()
    assert line.state == "invoiced"


# =================== F10: gates ===================


def test_a12f_f10_failed_gate_cannot_be_moved_off_its_project(w):
    project = _project(w)
    other = _project(w)
    _approve(w, project)
    gate = _decided(w, project, decision="fail")
    assert _refused(w.env, lambda: gate.with_user(w.sponsor).write({"project_id": other.id}))
    assert _refused(w.env, lambda: gate.with_user(w.agent).write({"project_id": other.id}))
    assert gate.project_id == project


def test_a12f_f10_a_decided_gate_cannot_change_subject_before_closure(w):
    project = _project(w)
    other = _project(w)
    gate = _gate(w, project)
    gate.with_user(w.sponsor).action_record_decision(decision="fail", findings="No charter")
    assert gate.state == "scheduled"
    for vals in ({"project_id": other.id}, {"gate": "g5_closure"}):
        assert _refused(w.env, lambda v=vals: gate.with_user(w.sponsor).write(v))


def test_a12f_f10_closed_gate_is_immutable_at_the_orm(w):
    project = _project(w)
    gate = _decided(w, project)
    for vals in (
        {"reviewer_id": w.reviewer_emp.id},
        {"findings": "rewritten"},
        {"gate": "g5_closure"},
        {"checklist_passed": False},
        {"review_on": "2030-01-01"},
    ):
        assert _refused(w.env, lambda v=vals: gate.with_user(w.sponsor).write(v)), vals


def test_a12f_f10_manager_holding_the_sponsor_role_cannot_pass_his_own_gate(w):
    both, emp = _user(w.env, "a12f.pm.sponsor", PM, SPONSOR)
    project = _project(w, budget=0.0, contract=False, manager_id=emp.id, user=both)
    gate = _gate(w, project)
    for fn in (
        lambda: gate.with_user(both).action_record_decision(decision="pass", checklist_passed=True),
        lambda: gate.with_user(both).action_hold(),
        lambda: gate.with_user(both).write({"checklist_passed": True}),
    ):
        assert _refused(w.env, fn)


def test_a12f_f10_pm_and_sponsor_schedule_gates_from_the_workspace(w):
    project = _project(w)
    for user in (w.pm, w.sponsor):
        result = Api(w.env, user).write(
            "fix.project.gate",
            {"project_id": project.id, "gate": "g1_initiation", "review_on": "2030-01-01"},
        )
        assert result.get("id"), result


def test_a12f_f10_the_manager_does_not_write_the_reviewers_evidence(w):
    project = _project(w)
    gate = _gate(w, project, reviewer=w.reviewer_emp)
    api = Api(w.env, w.pm)
    # Rescheduling works and an unchanged echo of the evidence passes...
    result = api.write(
        "fix.project.gate", {"review_on": "2030-02-01", "checklist_passed": False}, gate.id
    )
    assert not result.get("error"), result
    # ...and the evidence itself is refused.
    assert api.write("fix.project.gate", {"checklist_passed": True}, gate.id).get("error")
    assert api.write("fix.project.gate", {"findings": "All good"}, gate.id).get("error")


def test_a12f_f10_named_reviewer_works_the_gate_from_the_workspace(w):
    button = _button(_screen_source(), "action_record_decision")
    project = _project(w)
    gate = _gate(w, project, reviewer=w.reviewer_emp)
    api = Api(w.env, w.reviewer)
    # What the three prompts of the button send: typed text.
    assert "asks:" in button
    result = api.action(
        "fix.project.gate",
        gate,
        "action_record_decision",
        decision=" Pass ",
        checklist_passed="yes",
        findings="Charter signed",
    )
    assert result["success"], result
    assert gate.decision == "pass" and gate.checklist_passed and gate.findings == "Charter signed"
    assert api.action("fix.project.gate", gate, "action_hold")["success"]
    assert api.action("fix.project.gate", gate, "action_close")["success"]
    assert gate.state == "closed"
    stranger = _gate(w, project)
    assert not api.action("fix.project.gate", stranger, "action_hold")["success"]


def test_a12f_f10_template_with_a_gate_plan_instantiates_for_a_pm(w):
    template = (
        w.env["fix.project.template"]
        .with_user(w.pm)
        .create(
            {
                "name": "A12F T",
                "gate_plan": "g1_initiation,g2_planning",
                "milestone_plan": "M1\nM2",
                "wbs_plan": "M1: analyse\nM2: build",
            }
        )
    )
    result = Api(w.env, w.pm).action("fix.project.template", template, "action_instantiate")
    assert result["success"], result
    project = w.env["fix.project"].search([("template_id", "=", template.id)])
    assert len(project.gate_ids) == 2 and len(project.milestone_ids) == 2


# =================== F11 / F12 ===================


def test_a12f_f11_manager_frozen_at_the_orm_after_activation(w):
    project = _active(w)
    assert (
        Api(w.env, w.pm).write("fix.project", {"manager_id": w.pm2_emp.id}, project.id).get("error")
    )
    assert _refused(w.env, lambda: project.with_user(w.pm).write({"manager_id": w.pm2_emp.id}))
    assert project.manager_id == w.pm_emp


def test_a12f_f11_a_legacy_blank_manager_can_be_named_once(w):
    project = _project(w, budget=0.0, contract=False, manager=False)
    w.env.cr.execute("UPDATE fix_project SET state='active' WHERE id=%s", (project.id,))
    project.invalidate_recordset()
    project.with_user(w.pm).write({"manager_id": w.pm_emp.id})
    assert _refused(w.env, lambda: project.with_user(w.pm).write({"manager_id": w.pm2_emp.id}))


def test_a12f_f12_activation_needs_g1_and_g2_passed(w):
    project = _project(w)
    _approve(w, project)
    err = _refused(w.env, lambda: project.with_user(w.pm).action_activate())
    assert "G1" in err, "zero gates no longer activate"
    _decided(w, project, kind="g1_initiation")
    _gate(w, project, kind="g2_planning")
    err = _refused(w.env, lambda: project.with_user(w.pm).action_activate())
    assert "G2" in err, "an undecided G2 is not a passed one"
    _decided(w, project, kind="g2_planning")
    project.with_user(w.pm).action_activate()
    assert project.state == "active"


def test_a12f_f12_required_gates_are_a_parameter(w):
    w.env["ir.config_parameter"].sudo().set_param(
        "fix_ppm.activation_required_gates", "g3_execution"
    )
    project = _project(w)
    _approve(w, project)
    err = _refused(w.env, lambda: project.with_user(w.pm).action_activate())
    assert "G3" in err
    _decided(w, project, kind="g3_execution")
    project.with_user(w.pm).action_activate()


def test_a12f_f12_latest_decision_wins_so_a_failed_gate_can_be_re_reviewed(w):
    project = _project(w)
    _approve(w, project)
    _decided(w, project, decision="fail")
    _decided(w, project, kind="g2_planning")
    err = _refused(w.env, lambda: project.with_user(w.pm).action_activate())
    assert "closed as FAIL" in err
    # A re-review only scheduled has decided nothing: the failure stands.
    _gate(w, project, kind="g1_initiation")
    assert _refused(w.env, lambda: project.with_user(w.pm).action_activate())
    _decided(w, project, decision="pass")
    project.with_user(w.pm).action_activate()
    assert project.state == "active"


def test_a12f_f12_failed_gate_blocks_completion_until_re_reviewed(w):
    project = _active(w)
    _accepted_milestone(w, project)
    _decided(w, project, decision="fail", kind="g5_closure")
    err = _refused(w.env, lambda: project.with_user(w.sponsor).action_complete())
    assert "closed as FAIL" in err
    _decided(w, project, decision="pass", kind="g5_closure")
    project.with_user(w.sponsor).action_complete()
    assert project.state == "completed"


def test_a12f_f12_reviewer_cannot_become_the_manager_afterwards(w):
    project = _project(w)
    _gate(w, project, reviewer=w.reviewer_emp)
    err = _refused(w.env, lambda: project.with_user(w.pm).write({"manager_id": w.reviewer_emp.id}))
    assert "independent" in err


# =================== F13 / BRU-PPM-12 / lifecycle row 11: cost ===================


def test_a12f_f13_cost_is_not_typed(w):
    project = _active(w)
    api = Api(w.env, w.pm)
    assert api.write("fix.project", {"actual_cost": 1.0}, project.id).get("error")
    from odoo.addons.cd_p03_portal.controllers.a12 import m67

    assert "actual_cost" not in m67.WRITABLE["fix.project"]


def test_a12f_f13_with_nothing_real_the_cost_says_not_measured(w):
    from odoo.addons.cd_p03_portal.controllers.a12 import m67

    project = _active(w, name="A12F Unmeasured")
    w.env["fix.project.task"].with_user(w.pm).create(
        {"name": "T", "project_id": project.id, "actual_hours": 500.0}
    )
    project.invalidate_recordset()
    assert not project.cost_measured and project.cost_basis == "Not measured"
    env = w.env(user=w.pm.id)
    for report in (m67.portfolio_status, m67.budget_vs_actual, m67.project_pnl):
        row = next(r for r in report(env)["rows"] if r["project"] == project.name)
        assert row["actual"] == m67.NOT_MEASURED, report.__name__
    row = next(r for r in m67.project_pnl(env)["rows"] if r["project"] == project.name)
    assert row["margin"] == m67.NOT_MEASURED
    row = next(r for r in m67.earned_value(env)["rows"] if r["project"] == project.name)
    assert row["ac"] == m67.NOT_MEASURED and row["cpi"] is None
    row = next(r for r in m67.benefits_realisation(env)["rows"] if r["project"] == project.name)
    assert row["saved"] == m67.NOT_MEASURED


def test_a12f_f13_hours_at_the_rate_parameter_feed_the_cost(w):
    w.env["ir.config_parameter"].sudo().set_param("fix_ppm.cost_rate_per_hour", "200")
    project = _active(w)
    w.env["fix.project.task"].with_user(w.pm).create(
        {"name": "T", "project_id": project.id, "actual_hours": 500.0}
    )
    project.invalidate_recordset()
    assert project.actual_cost == 100000.0 and project.cost_measured
    assert project.budget_variance == 100000.0
    assert "500.0 task hours x 200.00" in project.cost_basis


def test_a12f_f13_project_tagged_ledger_postings_feed_the_cost(w):
    from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

    env = w.env
    env.company.partner_id.vat = "1234567890123"
    unit = env["operating.unit"].sudo().search([("company_id", "=", env.company.id)], limit=1)
    if not unit:
        pytest.skip("this company has no operating unit to carry a dimension")
    project = _active(w)
    journal = env["account.journal"].sudo().search([("type", "=", "general")], limit=1)
    expense = (
        env["account.account"]
        .sudo()
        .search([("account_type", "=", "expense"), ("company_ids", "in", env.company.id)], limit=1)
    )
    bank = (
        env["account.account"]
        .sudo()
        .search(
            [("account_type", "=", "asset_current"), ("company_ids", "in", env.company.id)], limit=1
        )
    )
    move, _dims = post_with_dimensions(
        env(su=True),
        {
            "journal_id": journal.id,
            "company_id": env.company.id,
            "date": fields.Date.context_today(project),
            "line_ids": [
                (
                    0,
                    0,
                    {"account_id": expense.id, "name": "Cabling", "debit": 750.0, "credit": 0.0},
                ),
                (0, 0, {"account_id": bank.id, "name": "Cabling", "debit": 0.0, "credit": 750.0}),
            ],
        },
        {0: {"project_ref": project.code}},
        source="api",
    )
    assert move.state == "posted"
    project.invalidate_recordset()
    expected = env.company.currency_id._convert(
        750.0, project.currency_id, env.company, fields.Date.context_today(project)
    )
    if project.currency_id != env.company.currency_id and not env[
        "res.currency.rate"
    ].sudo().search_count([("currency_id", "=", project.currency_id.id)]):
        # No rate on this database: unknown, not zero and not a raw figure.
        assert not project.cost_measured
        return
    assert project.cost_measured and abs(project.actual_cost - expected) < 0.01
    assert project.code in project.cost_basis


def test_a12f_f13_pnl_shows_billed_revenue_and_margin(linked):
    from odoo.addons.cd_p03_portal.controllers.a12 import m67

    w = linked
    w.env["ir.config_parameter"].sudo().set_param("fix_ppm.cost_rate_per_hour", "100")
    project = _active(w, name="A12F PnL")
    w.env["fix.project.task"].with_user(w.pm).create(
        {"name": "T", "project_id": project.id, "actual_hours": 300.0}
    )
    _invoiced(w, project, retention_pct=10.0)
    project.invalidate_recordset()
    out = m67.project_pnl(w.env(user=w.pm.id))
    assert {"billed", "margin", "retention"} <= set(out["cols"])
    row = next(r for r in out["rows"] if r["project"] == project.name)
    assert (row["billed"], row["retention"], row["actual"], row["margin"]) == (
        90000.0,
        10000.0,
        30000.0,
        60000.0,
    )


# =================== F15 ===================


def test_a12f_f15_retyping_a_milestone_line_does_not_skip_acceptance(w):
    project = _active(w)
    milestone = (
        w.env["fix.project.milestone"]
        .with_user(w.pm)
        .create({"name": "M", "project_id": project.id})
    )
    line = _bill(w, project, milestone)
    result = Api(w.env, w.pm).write(
        "fix.project.billing",
        {"billing_type": "time_material", "milestone_id": False},
        record_id=line.id,
    )
    assert result.get("error") and "acceptance" in result["error"]
    assert _refused(w.env, lambda: line.with_user(w.pm).action_mark_ready())


def test_a12f_f15_currency_and_type_freeze_at_ready(w):
    project = _active(w)
    line = _bill(w, project, _accepted_milestone(w, project))
    line.with_user(w.pm).action_mark_ready()
    usd = w.env.ref("base.USD")
    api = Api(w.env, w.pm)
    assert api.write("fix.project.billing", {"currency_id": usd.id}, line.id).get("error")
    assert _refused(w.env, lambda: line.with_user(w.pm).write({"currency_id": usd.id}))


def test_a12f_f15_ceiling_refuses_a_foreign_amount_with_no_rate(w):
    project = _active(w, contract=300000.0)
    w.env["res.currency.rate"].sudo().search(
        [("currency_id", "=", project.currency_id.id)]
    ).unlink()
    if project.currency_id == w.env.company.currency_id:
        pytest.skip("the company runs in the project's currency")
    usd = w.env.ref("base.USD")
    err = _refused(w.env, lambda: _bill(w, project, amount=250000.0, currency_id=usd.id))
    assert "exchange rate" in err


def test_a12f_f15_ceiling_converts_through_the_company_rate(w):
    env = w.env
    company = env.company
    foreign = env.ref("base.EUR")
    foreign.sudo().active = True
    project = _active(w, contract=300000.0, currency_id=company.currency_id.id)
    today = fields.Date.context_today(project)
    # 1 company unit = 0.01 EUR, so 1 EUR = 100 company units.
    env["res.currency.rate"].sudo().create(
        {"currency_id": foreign.id, "rate": 0.01, "name": today, "company_id": company.id}
    )
    assert _refused(w.env, lambda: _bill(w, project, amount=3001.0, currency_id=foreign.id))
    _bill(w, project, amount=2999.0, currency_id=foreign.id)


def test_a12f_f15_contract_cannot_drop_below_what_is_billed(w):
    project = _project(w, contract=300000.0)
    _bill(w, project, amount=200000.0)
    err = _refused(w.env, lambda: project.with_user(w.pm).write({"contract_value": 100000.0}))
    assert "ceiling" in err
    project.with_user(w.pm).write({"contract_value": 250000.0})


def test_a12f_f15_a_project_already_over_its_ceiling_still_saves_its_other_fields(w):
    project = _project(w, budget=100.0, contract=False)
    w.env.cr.execute(
        "INSERT INTO fix_project_billing (name, company_id, project_id, billing_type, amount, "
        "currency_id, due_on, state) VALUES ('LEG', %s, %s, 'milestone', 500, %s, now(), 'planned')",
        (project.company_id.id, project.id, project.currency_id.id),
    )
    w.env.invalidate_all()
    result = Api(w.env, w.pm).write("fix.project", {"name": "Renamed", "budget": 100.0}, project.id)
    assert not result.get("error"), result


# =================== F16 / lifecycle row 10: the line follows its move ===================


def test_a12f_f16_retention_is_deducted_on_the_invoice(linked):
    w = linked
    line = _invoiced(w, retention_pct=10.0)
    move = line.sudo().invoice_id
    assert move.state == "posted" and move.amount_total == 90000.0
    assert line.net_amount == 90000.0 and line.retention_amount == 10000.0
    assert any("Retention held" in item.name for item in move.invoice_line_ids)


def test_a12f_f16_ceiling_counts_what_is_invoiced_so_a_release_line_fits(w):
    project = _active(w, contract=100000.0)
    _bill(w, project, amount=100000.0, retention_pct=10.0)
    _bill(w, project, amount=10000.0)  # the retention, released
    assert _refused(w.env, lambda: _bill(w, project, amount=1.0))


def test_a12f_f16_a_reset_invoice_reopens_the_line_and_posts_again_without_a_duplicate(linked):
    w = linked
    line = _invoiced(w)
    move = line.sudo().invoice_id
    moves = w.env["account.move"].sudo().search_count([("move_type", "=", "out_invoice")])
    move.button_draft()
    w.env.flush_all()
    line.invalidate_recordset()
    assert line.state == "ready" and not line.invoice_ref
    line.with_user(w.billing).action_mark_invoiced()
    assert line.state == "invoiced" and line.sudo().invoice_id == move
    assert w.env["account.move"].sudo().search_count([("move_type", "=", "out_invoice")]) == moves


def test_a12f_f16_cancelled_invoice_reopens_the_line(linked):
    w = linked
    line = _invoiced(w)
    move = line.sudo().invoice_id
    move.button_draft()
    move.button_cancel()
    w.env.flush_all()
    line.invalidate_recordset()
    assert line.state == "ready"
    line.with_user(w.billing).action_mark_invoiced()
    assert line.sudo().invoice_id != move and line.sudo().invoice_id.state == "posted"


def test_a12f_f16_deleted_invoice_leaves_no_fiction(linked):
    # A move M19 posted cannot be deleted at all: its posting log refers to it. What
    # can be deleted is a draft the earlier build left behind, reading "invoiced".
    w = linked
    project = _active(w)
    line = _bill(w, project, _accepted_milestone(w, project))
    line.with_user(w.pm).action_mark_ready()
    move = line.sudo()._invoice_draft()
    line.sudo()._guarded().write({"invoice_id": move.id, "state": "invoiced"})
    move.sudo().with_context(force_delete=True).unlink()
    w.env.flush_all()
    line.invalidate_recordset()
    assert line.state == "ready" and not line.invoice_id and not line.invoice_ref


def test_a12f_f16_a_draft_left_by_the_earlier_build_is_posted_not_duplicated(linked):
    w = linked
    project = _active(w)
    line = _bill(w, project, _accepted_milestone(w, project))
    line.with_user(w.pm).action_mark_ready()
    move = line.sudo()._invoice_draft()
    line.sudo()._guarded().write({"invoice_id": move.id})
    assert line.state == "ready", "a draft is not an invoice"
    line.with_user(w.billing).action_mark_invoiced()
    assert line.sudo().invoice_id == move and move.state == "posted"
    assert line.state == "invoiced"


def test_a12f_f16_reversed_invoice_reopens_the_line(linked):
    w = linked
    line = _invoiced(w)
    move = line.sudo().invoice_id
    wizard = (
        w.env["account.move.reversal"]
        .sudo()
        .with_context(active_model="account.move", active_ids=move.ids)
        .create(
            {
                "journal_id": move.journal_id.id,
                "date": fields.Date.context_today(move),
                "reason": "Billing error",
            }
        )
    )
    wizard.refund_moves()
    credit = w.env["account.move"].sudo().search([("reversed_entry_id", "=", move.id)])
    credit.with_context(fix_test=True)._fix_m19_post(source="ar")
    w.env.flush_all()
    line.invalidate_recordset()
    assert move.payment_state == "reversed", move.payment_state
    assert line.state == "ready"


def test_a12f_row10_paid_follows_the_payment_state_and_back(linked):
    w = linked
    line = _invoiced(w)
    move = line.sudo().invoice_id
    assert line.state == "invoiced"
    register = (
        w.env["account.payment.register"]
        .sudo()
        .with_context(active_model="account.move", active_ids=move.ids)
        .create({})
    )
    payments = register._create_payments()
    w.env.flush_all()
    line.invalidate_recordset()
    assert move.payment_state in ("paid", "in_payment"), move.payment_state
    assert line.state == "paid"
    assert payments
    # The payment unreconciled: the line is owed again.
    move.line_ids.remove_move_reconcile()
    w.env.flush_all()
    line.invalidate_recordset()
    assert move.payment_state == "not_paid"
    assert line.state == "invoiced"


def test_a12f_row10_paid_cannot_be_typed(linked):
    w = linked
    line = _invoiced(w)
    assert _refused(w.env, lambda: line.with_user(w.billing).write({"state": "paid"}))
    assert Api(w.env, w.pm).write("fix.project.billing", {"state": "paid"}, line.id).get("error")


# =================== F17 ===================


def test_a12f_f17_acceptance_is_a_sponsor_act(w):
    project = _active(w)
    milestone = (
        w.env["fix.project.milestone"]
        .with_user(w.pm)
        .create({"name": "M", "project_id": project.id})
    )
    assert _refused(w.env, lambda: milestone.with_user(w.pm).action_accept("self"))
    assert _refused(w.env, lambda: milestone.with_user(w.pm2).action_accept("colleague"))
    assert _refused(w.env, lambda: milestone.with_user(w.plain).action_accept("x"))
    result = Api(w.env, w.sponsor).action(
        "fix.project.milestone", milestone, "action_accept", acceptance_note="Client SO-1"
    )
    assert result["success"], result
    assert milestone.accepted_by_id == w.sponsor


def test_a12f_f17_no_acceptance_while_the_project_names_no_manager(w):
    project = _project(w, budget=0.0, contract=False, manager=False)
    milestone = (
        w.env["fix.project.milestone"]
        .with_user(w.pm)
        .create({"name": "M", "project_id": project.id})
    )
    err = _refused(w.env, lambda: milestone.with_user(w.sponsor).action_accept("x"))
    assert "names no manager" in err
    err = _refused(w.env, lambda: project.with_user(w.pm).action_activate())
    assert "project manager" in err


def test_a12f_f17_a_manager_holding_the_sponsor_role_does_not_accept_his_own(w):
    both, emp = _user(w.env, "a12f.pm.sponsor2", PM, SPONSOR)
    project = _project(w, budget=0.0, contract=False, manager_id=emp.id, user=both)
    milestone = (
        w.env["fix.project.milestone"]
        .with_user(both)
        .create({"name": "M", "project_id": project.id})
    )
    assert _refused(w.env, lambda: milestone.with_user(both).action_accept("self"))


def test_a12f_f17_acceptance_evidence_is_immutable(w):
    project = _active(w)
    milestone = _accepted_milestone(w, project)
    assert _refused(
        w.env, lambda: milestone.with_user(w.pm).write({"acceptance_note": "rewritten"})
    )
    assert _refused(w.env, lambda: milestone.with_user(w.sponsor).write({"acceptance_note": "x"}))


# =================== F18 ===================


def test_a12f_f18_the_pm_does_not_close_his_project(w):
    project = _active(w)
    _accepted_milestone(w, project)
    result = Api(w.env, w.pm).action("fix.project", project, "action_complete")
    assert not result["success"]
    both, emp = _user(w.env, "a12f.pm.sponsor3", PM, SPONSOR)
    own = _active(w, manager_id=emp.id)
    _accepted_milestone(w, own)
    assert _refused(w.env, lambda: own.with_user(both).action_complete())


def test_a12f_f18_no_milestones_no_completion(w):
    project = _active(w)
    err = _refused(w.env, lambda: project.with_user(w.sponsor).action_complete())
    assert "no milestones" in err


def test_a12f_f18_closure_needs_finance_to_confirm_the_billing(linked):
    w = linked
    project = _active(w)
    line = _invoiced(w, project)
    err = _refused(w.env, lambda: project.with_user(w.sponsor).action_complete())
    assert "Finance" in err
    assert not Api(w.env, w.pm).action("fix.project", project, "action_confirm_billing")["success"]
    result = Api(w.env, w.billing).action("fix.project", project, "action_confirm_billing")
    assert result["success"], result
    assert project.billing_confirmed_by_id == w.billing
    # Billing that moves afterwards needs a new confirmation.
    line.sudo().invoice_id.button_draft()
    w.env.flush_all()
    project.invalidate_recordset()
    err = _refused(w.env, lambda: project.with_user(w.sponsor).action_complete())
    assert "not invoiced" in err
    line.with_user(w.billing).action_mark_invoiced()
    extra = _bill(w, project, amount=5000.0)
    extra.with_user(w.pm).action_mark_ready()
    extra.with_user(w.accountant).action_mark_invoiced()
    err = _refused(w.env, lambda: project.with_user(w.sponsor).action_complete())
    assert "moved" in err
    project.with_user(w.billing).action_confirm_billing()
    result = Api(w.env, w.sponsor).action("fix.project", project, "action_complete")
    assert result["success"], result
    assert project.state == "completed" and project.closed_by_id == w.sponsor


def test_a12f_f18_unbilled_line_blocks_finance_and_the_sponsor(w):
    project = _active(w)
    _accepted_milestone(w, project)
    _bill(w, project)
    assert _refused(w.env, lambda: project.with_user(w.billing).action_confirm_billing())
    assert _refused(w.env, lambda: project.with_user(w.sponsor).action_complete())


# =================== F19 ===================


def test_a12f_f19_assignee_works_and_logs_his_own_task_from_the_workspace(w):
    project = _project(w)
    task = (
        w.env["fix.project.task"]
        .with_user(w.pm)
        .create({"name": "T", "project_id": project.id, "assigned_to": w.plain_emp.id})
    )
    api = Api(w.env, w.plain)
    assert api.action("fix.project.task", task, "action_start")["success"]
    result = api.action("fix.project.task", task, "action_log_hours", hours=3.5)
    assert result["success"], result
    assert task.actual_hours == 3.5
    assert not api.action("fix.project.task", task, "action_log_hours", hours=-1)["success"]
    assert api.action("fix.project.task", task, "action_done")["success"]
    assert task.state == "done"


def test_a12f_f19_someone_elses_task_is_refused(w):
    project = _project(w)
    task = (
        w.env["fix.project.task"]
        .with_user(w.pm)
        .create({"name": "T", "project_id": project.id, "assigned_to": w.reviewer_emp.id})
    )
    for method in ("action_start", "action_done", "action_cancel"):
        assert not Api(w.env, w.plain).action("fix.project.task", task, method)["success"], method
    assert not Api(w.env, w.plain).action("fix.project.task", task, "action_log_hours", hours=1)[
        "success"
    ]
    assert _refused(w.env, lambda: task.with_user(w.plain).write({"state": "done"}))


def test_a12f_f19_owner_and_sponsor_work_a_risk_a_bystander_does_not(w):
    risk = _risk(w, probability="medium", impact="medium", owner_id=w.plain.id)
    api = Api(w.env, w.plain)
    result = api.action("fix.project.risk", risk, "action_mitigate", mitigation="Vendor cover")
    assert result["success"], result
    assert api.action("fix.project.risk", risk, "action_close")["success"]
    assert risk.state == "closed"
    other = _risk(w, probability="medium", impact="medium", mitigation="m")
    assert not Api(w.env, w.reviewer).action("fix.project.risk", other, "action_close")["success"]
    assert Api(w.env, w.sponsor).action("fix.project.risk", other, "action_close")["success"]


def test_a12f_f19_severity_9_needs_a_sponsor_who_does_not_manage_the_project(w):
    project = _project(w)
    risk = _risk(w, project=project, owner_id=w.plain.id, mitigation="x")
    assert risk.severity_score == 9
    assert _refused(w.env, lambda: risk.with_user(w.pm).action_close())
    assert _refused(w.env, lambda: risk.with_user(w.plain).action_close())
    both, emp = _user(w.env, "a12f.pm.sponsor4", PM, SPONSOR)
    own = _project(w, manager_id=emp.id)
    own_risk = _risk(w, project=own, mitigation="x")
    assert _refused(w.env, lambda: own_risk.with_user(both).action_close())
    assert Api(w.env, w.sponsor).action("fix.project.risk", risk, "action_close")["success"]
    assert risk.state == "closed"


def test_a12f_f19_the_closure_threshold_is_a_parameter(w):
    w.env["ir.config_parameter"].sudo().set_param("fix_ppm.risk_sponsor_close_threshold", "4")
    risk = _risk(w, probability="medium", impact="medium", mitigation="x")
    assert _refused(w.env, lambda: risk.with_user(w.pm).action_close())


# =================== F20 ===================


def test_a12f_f20_requester_recalls_from_the_workspace(w):
    assert _button(_screen_source(), "action_recall_approval")
    project = _project(w)
    project.with_user(w.pm).action_request_approval(justification=JUSTIFICATION)
    result = Api(w.env, w.pm).action("fix.project", project, "action_recall_approval")
    assert result["success"], result
    assert project.approval_state == "none"


# =================== every button is whitelisted, every field real ===================


def test_a12f_list_columns_are_real_fields(w):
    source = _screen_source()
    for model, cols in re.findall(
        r"kind: 'model_list', model: '(fix\.project[a-z.]*)'.*?cols: \[(.*?)\]", source, re.S
    ):
        for col in re.findall(r"'([a-z_0-9]+)'", cols):
            assert col in w.env[model]._fields, "%s.%s" % (model, col)


def test_a12f_form_fields_are_real_and_writable_where_offered(w):
    from odoo.addons.cd_p03_portal.controllers.a12 import m67

    source = _screen_source()
    forms = re.findall(
        r"kind: 'model_form',\s*model: '(fix\.project[a-z.]*)'(.*?)\n  \}", source, re.S
    )
    assert len(forms) >= 6
    for model, body in forms:
        for line in re.findall(r"\{ name: '([a-z_0-9]+)'([^}]*)\}", body):
            name, attrs = line
            assert name in w.env[model]._fields, "%s.%s" % (model, name)
            if "readonly: true" not in attrs:
                assert name in m67.WRITABLE[model], "%s.%s is offered and not writable" % (
                    model,
                    name,
                )


# =================== the whole path, as the real roles ===================


def test_a12f_full_walk_by_the_real_roles_through_the_screen(linked):
    """Project to paid and closed. No step is done by a superuser."""
    from odoo.addons.cd_p03_portal.controllers.a12 import m67

    w = linked
    w.env["ir.config_parameter"].sudo().set_param("fix_ppm.cost_rate_per_hour", "500")
    pm, sponsor, t2, finance = (
        Api(w.env, w.pm),
        Api(w.env, w.sponsor),
        Api(w.env, w.t2),
        Api(w.env, w.billing),
    )
    # PM raises the project and asks for the budget.
    result = pm.write(
        "fix.project",
        {
            "name": "A12F Walk",
            "project_type": "client",
            "manager_id": w.pm_emp.id,
            "budget": 200000.0,
            "contract_value": 500000.0,
        },
    )
    assert result.get("id"), result
    project = w.env["fix.project"].browse(result["id"])
    assert project.code.startswith("PRJ/")
    result = pm.action(
        "fix.project", project, "action_request_approval", justification=JUSTIFICATION
    )
    assert result["success"], result
    # The tier holder approves from the inbox.
    result = t2.action(
        "fix.workflow.task", _task_of(project, w.t2), "action_approve", comment="Plan page 12"
    )
    assert result["success"], result
    # The PM schedules G1 and G2; the sponsor decides them.
    for kind in ("g1_initiation", "g2_planning"):
        result = pm.write(
            "fix.project.gate", {"project_id": project.id, "gate": kind, "review_on": "2030-01-01"}
        )
        assert result.get("id"), result
        gate = w.env["fix.project.gate"].browse(result["id"])
        result = sponsor.action(
            "fix.project.gate",
            gate,
            "action_record_decision",
            decision="pass",
            checklist_passed="yes",
            findings="Reviewed",
        )
        assert result["success"], result
        assert sponsor.action("fix.project.gate", gate, "action_hold")["success"]
        assert sponsor.action("fix.project.gate", gate, "action_close")["success"]
    result = pm.action("fix.project", project, "action_activate")
    assert result["success"], result
    assert project.baseline_budget == 200000.0
    # Delivery: the assignee works the task, the sponsor accepts.
    result = pm.write("fix.project.milestone", {"name": "Go-live", "project_id": project.id})
    milestone = w.env["fix.project.milestone"].browse(result["id"])
    result = pm.write(
        "fix.project.task",
        {
            "name": "Build",
            "project_id": project.id,
            "milestone_id": milestone.id,
            "assigned_to": w.plain_emp.id,
        },
    )
    task = w.env["fix.project.task"].browse(result["id"])
    worker = Api(w.env, w.plain)
    assert worker.action("fix.project.task", task, "action_start")["success"]
    assert worker.action("fix.project.task", task, "action_log_hours", hours=40)["success"]
    assert worker.action("fix.project.task", task, "action_done")["success"]
    result = sponsor.action(
        "fix.project.milestone", milestone, "action_accept", acceptance_note="Client SO-4471"
    )
    assert result["success"], result
    assert pm.action("fix.project.milestone", milestone, "action_complete")["success"]
    # A risk reaches the enterprise register and is closed by the sponsor.
    result = pm.write(
        "fix.project.risk",
        {
            "project_id": project.id,
            "title": "Cutover window",
            "kind": "risk",
            "probability": "high",
            "impact": "high",
            "opened_on": "2026-11-01",
        },
    )
    risk = w.env["fix.project.risk"].browse(result["id"])
    w.env["fix.event.outbox"].sudo().cron_relay(limit=10000)
    assert w.env["fix.risk.register"].sudo().search_count([("name", "like", risk.name)]) == 1
    result = pm.action("fix.project.risk", risk, "action_mitigate", mitigation="Night cutover")
    assert result["success"], result
    assert sponsor.action("fix.project.risk", risk, "action_close")["success"]
    # Billing: PM to ready, Finance posts, the customer pays.
    result = pm.write(
        "fix.project.billing",
        {
            "project_id": project.id,
            "milestone_id": milestone.id,
            "customer_id": w.customer.id,
            "billing_type": "milestone",
            "amount": 100000.0,
            "retention_pct": 5.0,
            "due_on": "2026-12-01",
        },
    )
    assert result.get("id"), result
    line = w.env["fix.project.billing"].browse(result["id"])
    assert pm.action("fix.project.billing", line, "action_mark_ready")["success"]
    result = finance.action("fix.project.billing", line, "action_mark_invoiced")
    assert result["success"], result
    move = line.sudo().invoice_id
    assert move.state == "posted" and move.amount_total == 95000.0
    (
        w.env["account.payment.register"]
        .sudo()
        .with_context(active_model="account.move", active_ids=move.ids)
        .create({})
        ._create_payments()
    )
    w.env.flush_all()
    line.invalidate_recordset()
    assert line.state == "paid"
    # Closure: Finance confirms, the sponsor closes.
    assert finance.action("fix.project", project, "action_confirm_billing")["success"]
    result = sponsor.action("fix.project", project, "action_complete")
    assert result["success"], result
    assert project.state == "completed"
    # What the screens now show.
    env = w.env(user=w.pm.id)
    row = next(r for r in m67.project_pnl(env)["rows"] if r["project"] == "A12F Walk")
    assert (row["billed"], row["retention"], row["actual"], row["margin"]) == (
        95000.0,
        5000.0,
        20000.0,
        75000.0,
    )
    row = next(r for r in m67.billing_status(env)["rows"] if r["billing"] == line.name)
    assert row["real_invoice"] == "Yes" and row["state"] == "Paid"
