"""test_a12_m66_controls.py — the A12 remediation of M66 (ITSM) and P1-1
(change enablement), probed as NON-ADMIN users where the attack was.

Source: working/A12_Workflow_and_Approval_Report.md and
working/A12_evidence/module_findings/M66.md (M66-5/7/8/9/10/11/13, P1-1).
Every control is checked both ways: the bypass is refused, the legitimate
role still works. Approvals are decided from the approver's inbox
(approve_via_inbox), never by pressing Approve on the record.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from odoo import fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import (
    approve_via_inbox,
    inbox_task,
)
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
AGENT = "cd_itsm.group_itsm_agent"
CHANGE_MANAGER = "cd_itsm.group_itsm_change_manager"
CAB = "cd_itsm.group_itsm_cab_member"


@pytest.fixture
def env(odoo_env):
    return odoo_env


@pytest.fixture
def make_user(env):
    counter = {"n": 0}

    def _make(*xmlids):
        counter["n"] += 1
        groups = [env.ref("base.group_user").id] + [env.ref(x).id for x in xmlids]
        user = (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "M66 A12 Probe %d" % counter["n"],
                    "login": "m66.a12.probe.%d@a12.test" % counter["n"],
                    "group_ids": [(6, 0, groups)],
                }
            )
        )
        return user

    return _make


@pytest.fixture
def plain(env, make_user):
    return make_user()


@pytest.fixture
def agent(env, make_user):
    return make_user(AGENT)


@pytest.fixture
def change_mgr(env, make_user):
    return make_user(CHANGE_MANAGER)


@pytest.fixture
def cab_member(env, make_user):
    return make_user(CAB)


def _employee(env, name, user=None):
    vals = {"name": name}
    if user:
        vals["user_id"] = user.id
    return env["hr.employee"].create(vals)


def _ticket(env, **extra):
    vals = {
        "title": "POS printer offline",
        "requester_id": _employee(env, "Requester Rafiq").id,
        "category": "hardware",
        "priority": "high",
        "description": "Thermal printer not detected after update",
    }
    vals.update(extra)
    return env["fix.itsm.ticket"].create(vals)


def _change(env, **extra):
    vals = {
        "title": "Core switch firmware 9.2",
        "change_type": "normal",
        "risk": "medium",
        "risk_probability": "2",
        "risk_impact": "2",  # score 4: below the CAB threshold (6)
        "requested_by_id": _employee(env, "Change requester Ranjan").id,
        "implementation_plan": "Stage firmware, flash stack A then B, verify LLDP.",
        "test_plan": "Ping sweep, VLAN 20 throughput, failover drill.",
        "rollback_plan": "Boot previous image from the secondary partition.",
        "change_window_hours": 4,
        "planned_on": fields.Date.context_today(env.user),
    }
    vals.update(extra)
    return env["fix.itsm.change"].create(vals)


def _events(env, event_type, aggregate_id):
    domain = [("event_type", "=", event_type), ("aggregate_id", "=", aggregate_id)]
    return [json.loads(e.payload) for e in env["fix.event.outbox"].search(domain, order="id")]


# ---------------------------------------------------------------------------
# P1-1 — the change approval matrix
# ---------------------------------------------------------------------------


def _authorised_template(env, change_mgr, agent, code="A12-STD-1"):
    template = (
        env["fix.itsm.change.template"]
        .with_user(agent)
        .create(
            {
                "code": code,
                "name": "Firmware on a test switch",
                "implementation_plan": "Stage firmware, flash stack A then B, verify LLDP.",
                "test_plan": "Ping sweep, VLAN 20 throughput, failover drill.",
                "rollback_plan": "Boot previous image from the secondary partition.",
                "risk_probability": "1",
                "risk_impact": "2",
                "max_window_hours": 4,
            }
        )
    )
    template.with_user(change_mgr).action_authorise()
    return template


def test_p1_1_standard_change_from_a_template_is_pre_approved_by_policy(env, agent, change_mgr):
    template = _authorised_template(env, change_mgr, agent)
    change = _change(env, change_type="standard", template_id=template.id)
    # the desk submits; the authorised template — not a person — clears it
    change.with_user(agent).action_submit()
    assert change.state == "approved"
    assert change.approval_state == "approved"
    assert not change.approval_request_id  # nothing was routed
    assert not change.approved_by_id  # policy, not a person


def test_p1_1_a_standard_change_with_no_template_is_routed(env, agent, change_mgr):
    change = _change(env, change_type="standard")
    change.with_user(agent).action_submit()
    assert change.state == "draft"
    assert change.approval_state == "pending"


def test_p1_1_normal_change_routes_to_the_change_manager(env, change_mgr):
    assert change_mgr.has_group(CHANGE_MANAGER)
    change = _change(env)  # normal, score 4
    change.action_submit()
    assert change.approval_state == "pending"
    assert change._approval_group_xmlid() == CHANGE_MANAGER
    task = inbox_task(change, change_mgr)
    assert task, "the change manager received no inbox task"
    task.with_user(change_mgr).action_approve(comment="Window and rollback accepted.")
    assert change.state == "approved"
    assert change.approved_by_id == change_mgr


def test_p1_1_emergency_and_high_risk_route_to_the_cab(env, cab_member):
    assert cab_member.has_group(CAB)
    # An emergency change is the CAB's whatever its score...
    emergency = _change(env, change_type="emergency", title="Core switch RMA")
    assert emergency._approval_group_xmlid() == CAB
    emergency.action_submit()
    assert emergency.approval_state == "pending"
    # ...and a high score makes ANY change high-risk: standard included.
    hot = _change(
        env,
        change_type="standard",
        risk_probability="3",
        risk_impact="4",  # score 12 >= threshold 6
        rollback_plan=False,
    )
    assert hot.high_risk is True
    assert hot._approval_group_xmlid() == CAB
    with pytest.raises(UserError, match="high-risk change needs a rollback plan"):
        hot.action_submit()
    hot.rollback_plan = "Boot the previous image from the secondary partition."
    hot.action_submit()
    assert hot.approval_state == "pending"  # standard is NOT auto-approved when high-risk
    approve_via_inbox(emergency, cab_member)
    assert emergency.state == "approved"
    approve_via_inbox(hot, cab_member)
    assert hot.state == "approved"


def test_p1_1_cab_threshold_is_a_configurable_business_rule(env, cab_member):
    env["ir.config_parameter"].sudo().set_param("cd_itsm.change_cab_risk_score", "16")
    change = _change(env, risk_probability="3", risk_impact="4")  # score 12 < 16
    assert change.high_risk is False
    assert change._approval_group_xmlid() == CHANGE_MANAGER  # not the CAB at 12


def test_p1_1_requester_and_implementer_never_decide_their_own_change(env, make_user):
    requester_user = make_user(CAB)  # holds the authority AND is the requester
    requester_emp = _employee(env, "Requester-with-authority", requester_user)
    implementer_user = make_user(CAB)
    implementer_emp = _employee(env, "Implementer-with-authority", implementer_user)
    outsider = make_user(CAB)
    change = _change(
        env,
        change_type="emergency",
        requested_by_id=requester_emp.id,
        implementer_id=implementer_emp.id,
    )
    change.action_submit()
    tasks = change.approval_request_id.task_ids.filtered(lambda t: t.state == "pending")
    holders = {t.assigned_user_id for t in tasks}
    assert requester_user not in holders, "the requester was handed the decision"
    assert implementer_user not in holders, "the implementer was handed the decision"
    assert outsider in holders  # a genuinely independent CAB member decides


def test_p1_1_direct_approve_is_refused_it_decides_from_the_inbox(env, change_mgr, plain):
    change = _change(env)
    change.action_submit()
    assert change.approval_state == "pending"
    # The approver himself cannot short-circuit the inbox task...
    with pytest.raises(REFUSED, match="not directly"):
        change.with_user(change_mgr).action_approve()
    # ...and neither can a bystander.
    with pytest.raises(REFUSED):
        change.with_user(plain).action_approve()
    approve_via_inbox(change, change_mgr)
    assert change.state == "approved"


def test_p1_1_editing_the_approved_terms_voids_the_approval(env, make_user, change_mgr):
    change_mgr2 = make_user(CHANGE_MANAGER)
    change = _change(env)
    change.action_submit()
    approve_via_inbox(change, change_mgr)
    assert change.state == "approved"
    # A USER's edit of a pinned term voids the approval (superuser code does
    # not - server-side bookkeeping must not un-approve things), so edit as
    # the change manager.
    change.with_user(change_mgr).write({"title": "Core switch firmware 9.3 (updated)"})
    assert change.state == "draft", "the approval covered the old title only"
    assert not change.approved_by_id
    assert change.approval_state != "approved"
    # Same for the window and the plan. Whoever edited the terms is now the
    # record's amount-changer: the engine never hands him the decision again
    # (W3), so a SECOND change manager approves the re-request.
    change.action_submit()
    assert not inbox_task(change, change_mgr), "the editor was re-handed the decision"
    approve_via_inbox(change, change_mgr2)
    assert change.state == "approved"
    change.with_user(change_mgr).write({"change_window_hours": 8})
    assert change.state == "draft"
    change.action_submit()
    approve_via_inbox(change, change_mgr2)
    change.with_user(change_mgr).write({"rollback_plan": "Different plan: power down the stack."})
    assert change.state == "draft"


def test_p1_1_rejection_leaves_no_approved_change(env, change_mgr):
    change = _change(env)
    change.action_submit()
    task = inbox_task(change, change_mgr)
    task.with_user(change_mgr).action_reject(comment="No rollback test evidence.")
    assert change.state == "rejected"
    assert not change.approved_by_id


def test_p1_1_implement_needs_rollback_plans_and_segregation(env, change_mgr, plain):
    requester_user = plain
    requester_emp = _employee(env, "Requester Probe", requester_user)
    # No rollback plan, standard or not: not approvable at all (BRU-ITS-06).
    sloppy = _change(
        env,
        change_type="standard",
        requested_by_id=requester_emp.id,
        implementer_id=_employee(env, "Sloppy implementer").id,
        rollback_plan=False,
    )
    with pytest.raises(UserError, match="rollback plan"):
        sloppy.action_submit()
    assert sloppy.state == "draft"
    # Proper change: requester and implementer are different people.
    implementer_emp = _employee(env, "Implementer Probe")
    change = _change(env, requested_by_id=requester_emp.id, implementer_id=implementer_emp.id)
    change.action_submit()
    approve_via_inbox(change, change_mgr)
    assert change.approved_by_id == change_mgr
    with pytest.raises(UserError, match="approved change"):
        _change(env).action_implement()  # a draft change is not implementable
    # The implementer may not be the requester...
    same = _change(env, requested_by_id=requester_emp.id, implementer_id=requester_emp.id)
    same.action_submit()
    approve_via_inbox(same, change_mgr)
    with pytest.raises(UserError, match="not the requester"):
        same.action_implement()
    # ...nor the approver. The approver can never even be HANDED the decision
    # for a change he implements (_approval_excluded), so the attack names him
    # implementer AFTER the approval; the implement gate still refuses it.
    mgr_employee = _employee(env, "Change Manager Probe", change_mgr)
    by_approver = _change(env)
    by_approver.action_submit()
    approve_via_inbox(by_approver, change_mgr)
    by_approver.write({"implementer_id": mgr_employee.id})  # superuser bookkeeping
    with pytest.raises(UserError, match="not the approver"):
        by_approver.action_implement()
    change.action_implement()
    assert change.state == "implemented"
    assert change.implemented_on
    payloads = _events(env, "itsm.change_implemented", change.id)
    assert len(payloads) == 1
    assert payloads[0]["title"] == "Core switch firmware 9.2"
    assert payloads[0]["change_type"] == "normal"
    assert payloads[0]["risk_score"] == 4


def test_p1_1_emergency_change_rolls_back_and_records_its_pir(env, cab_member):
    implementer_emp = _employee(env, "Night engineer")
    change = _change(
        env,
        change_type="emergency",
        implementer_id=implementer_emp.id,
    )
    change.action_submit()
    approve_via_inbox(change, cab_member)
    change.action_implement()
    assert change.state == "implemented"
    # N-M66-2: a rollback no longer waits for a review, but it says why.
    with pytest.raises(UserError, match="rollback reason"):
        change.action_rollback()
    with pytest.raises(UserError, match="PIR notes are required"):
        change.action_record_pir("   ")
    change.action_record_pir("Root cause was a lacp flap; monitor for 48h.")
    assert change.state == "reviewed"
    assert change.pir_by_id
    assert change.pir_on
    change.action_rollback()  # the review is the reason
    assert change.state == "rolled_back"
    assert change.rollback_reason == "Root cause was a lacp flap; monitor for 48h."


# ---------------------------------------------------------------------------
# M66-5 / M66-8 — the ticket is worked by the service desk only
# ---------------------------------------------------------------------------


def test_m66_5_plain_user_cannot_work_or_forgive_a_ticket(env, plain, agent):
    ticket = _ticket(env)
    Ticket = env["fix.itsm.ticket"].with_user(plain)
    with pytest.raises(UserError, match="ITSM agent"):
        Ticket.browse(ticket.id).action_assign()
    with pytest.raises(UserError, match="ITSM agent"):
        Ticket.browse(ticket.id).action_resolve("Forgiven")
    # A direct state/resolution write is doubly blocked: the model's guard
    # refuses the workflow fields before the ACL is even reached.
    with pytest.raises(REFUSED, match="cannot be set directly"):
        Ticket.browse(ticket.id).write({"state": "resolved", "resolution": "Forgiven"})
    # The agent's path still works end to end.
    AgentTicket = env["fix.itsm.ticket"].with_user(agent)
    AgentTicket.browse(ticket.id).action_assign(assigned_to=_employee(env, "Agent Ali", agent))
    AgentTicket.browse(ticket.id).action_start()
    AgentTicket.browse(ticket.id).action_resolve("Driver reinstalled")
    assert ticket.state == "resolved"


def test_m66_5_close_belongs_to_the_requester_or_the_desk(env, make_user, agent):
    requester_user = make_user()
    requester_emp = _employee(env, "Requester Probe", requester_user)
    ticket = _ticket(env, requester_id=requester_emp.id)
    agent_ticket = env["fix.itsm.ticket"].with_user(agent)
    agent_ticket.browse(ticket.id).action_assign(assigned_to=_employee(env, "Agent Ali", agent))
    agent_ticket.browse(ticket.id).action_resolve("Driver reinstalled")
    stranger = make_user()  # an internal user who is neither
    with pytest.raises(REFUSED):
        env["fix.itsm.ticket"].with_user(stranger).browse(ticket.id).action_close()
    # N-M66-4: the requester is the rightful owner of the close. He holds no write
    # access, so the transition runs as sudo after that check.
    env["fix.itsm.ticket"].with_user(requester_user).browse(ticket.id).action_close()
    assert ticket.state == "closed"
    assert ticket.closed_on


def test_m66_5_the_desk_also_closes_a_resolved_ticket(env, make_user, agent):
    ticket = _ticket(env)
    agent_ticket = env["fix.itsm.ticket"].with_user(agent)
    agent_ticket.browse(ticket.id).action_assign(assigned_to=_employee(env, "Agent Ali", agent))
    agent_ticket.browse(ticket.id).action_resolve("Driver reinstalled")
    agent_ticket.browse(ticket.id).action_close()
    assert ticket.state == "closed"


# ---------------------------------------------------------------------------
# M66-7 — SLA escalation tells the NAMED manager
# ---------------------------------------------------------------------------


def test_m66_7_escalated_ticket_activities_go_to_the_configured_manager(env, make_user):
    manager = make_user()
    env["ir.config_parameter"].sudo().set_param("cd_itsm.sla_escalation_manager", manager.login)
    ticket = _ticket(env, priority="medium")
    # The deadline is the stored compute create_date + target hours; a raw
    # push of the column is clobbered by the pending compute and a Python
    # fields.Datetime.now() is local naive time before the process settles on
    # UTC here. Push create_date back on the DATABASE clock and rerun the
    # compute the ORM way (catalogue_id is a dependency).
    env.cr.execute(
        "UPDATE fix_itsm_ticket SET create_date = now() - interval '12 hours' WHERE id = %s",
        [ticket.id],
    )
    env.invalidate_all()
    catalogue = env["fix.itsm.catalogue"].create(
        {"code": "SLA-M66-7-%d" % ticket.id, "name": "Escalation probe", "target_hours": 4.0}
    )
    env["fix.itsm.ticket"].browse(ticket.id).write({"catalogue_id": catalogue.id})
    env.flush_all()
    assert env["fix.itsm.ticket"].browse(ticket.id).sla_deadline < fields.Datetime.now()
    env["fix.itsm.ticket"].cron_escalate_sla()
    ticket.invalidate_recordset()
    assert ticket.escalated is True
    assert ticket.priority == "high"
    activities = (
        env["mail.activity"]
        .sudo()
        .search([("res_model", "=", "fix.itsm.ticket"), ("res_id", "=", ticket.id)])
    )
    # The manager is told on top of the agent the queue rotates the ticket to.
    assert activities and manager in activities.mapped("user_id")


# ---------------------------------------------------------------------------
# M66-9 — asset retirement publishes the wipe-evidenced hand-off
# ---------------------------------------------------------------------------


def test_m66_9_retirement_needs_certificate_and_a_second_person_then_publishes(env):
    employee = _employee(env, "Holder Karim")
    asset = env["fix.itsm.asset"].create(
        {
            "name": "MacBook POS-7",
            "asset_tag": "A12-RET-1",
            "asset_kind": "laptop",
            "serial_no": "C02X1234",
            "state": "in_stock",
        }
    )
    with pytest.raises(UserError, match="data-wipe certificate"):
        asset.action_retire()
    asset.action_allocate(assigned_to=employee)
    with pytest.raises(UserError, match="still assigned"):
        asset.action_retire(wipe_certificate="WIPE-2026-101")
    asset.action_send_repair()
    asset.action_recover()  # back to stock, unassigned
    asset.action_retire(wipe_certificate="WIPE-2026-101")
    assert asset.state == "in_stock", "one person retired an asset"
    assert asset.writeoff_state == "requested"
    assert not _events(env, "itsm.asset_retired", asset.id)
    asset.action_approve_writeoff()
    assert asset.state == "retired"
    payloads = _events(env, "itsm.asset_retired", asset.id)
    assert payloads == [{"asset_tag": "A12-RET-1", "asset_kind": "laptop", "serial": "C02X1234"}]
    with pytest.raises(UserError, match="already retired"):
        asset.action_retire(wipe_certificate="WIPE-2026-102")


# ---------------------------------------------------------------------------
# M66-10 / 11 / 13 — the registers refuse fiction (role side)
# ---------------------------------------------------------------------------


def test_m66_10_11_13_registers_are_read_only_for_staff(env, plain):
    # base.group_user keeps READ on every register (B3/lead by design); the
    # write/create/unlink are the service desk's alone.
    for model, vals in (
        (
            "fix.itsm.change.template",
            {
                "code": "F",
                "name": "F",
                "implementation_plan": "i",
                "test_plan": "t",
                "rollback_plan": "r",
            },
        ),
        ("fix.itsm.problem", {"title": "Forged problem", "severity": "high"}),
        ("fix.itsm.licence", {"name": "Forged licence", "vendor": "X"}),
        ("fix.itsm.ci", {"name": "Forged CI", "ci_key": "forged-ci"}),
    ):
        with pytest.raises(AccessError):
            env[model].with_user(plain).create(vals)


# ---------------------------------------------------------------------------
# A12 P2 / FF-48 — the shipped consumers exist for every published event
# ---------------------------------------------------------------------------


def test_consumers_exist_for_every_cd_itsm_event(env):
    Consumer = env["fix.event.consumer"].sudo()
    expected = {
        "itsm.ticket_created": ("fix.itsm.ticket", "consume_ticket_created"),
        "itsm.ticket_resolved": ("fix.itsm.ticket", "consume_ticket_resolved"),
        "itsm.change_implemented": ("fix.itsm.change", "consume_change_implemented"),
        "itsm.asset_retired": ("fix.itsm.asset", "consume_asset_retired"),
    }
    for event_type, (model, method) in expected.items():
        rows = Consumer.search([("event_type", "=", event_type), ("model", "=", model)])
        assert rows, "no fix.event.consumer for %s" % event_type
        assert method in rows.mapped("method")
    # ...and every consume_* method the data file names actually exists.
    for row in Consumer.search([("module", "=", "cd_itsm")]):
        assert callable(getattr(env[row.model], row.method, None)), row.method


# ---------------------------------------------------------------------------
# R4 / X5 — surface whitelists, buttons and caller-scope reads
# ---------------------------------------------------------------------------


def test_r4_every_surface_declares_its_writable_whitelist():
    from odoo.addons.cd_p03_portal.controllers.a12 import m66 as m66_ctrl

    assert set(m66_ctrl.WRITABLE) == set(m66_ctrl.SURFACES)
    for model, writable in m66_ctrl.WRITABLE.items():
        forbidden = {
            "state",
            "resolution",
            "escalated",
            "resolved_on",
            "approved_by_id",
            "implemented_on",
            "pir_notes",
            "pir_by_id",
            "pir_on",
            "approval_state",
            "decision",
            "wipe_certificate",
        }
        assert not (forbidden & set(writable)), model
    assert m66_ctrl.SURFACES["fix.itsm.ticket"].get("rules") is True


def test_r4_every_js_button_is_whitelisted():
    from odoo.addons.cd_p03_portal.controllers.a12 import m66 as m66_ctrl

    js = (Path(m66_ctrl.__file__).parents[2] / "static" / "src" / "a12" / "m66.js").read_text(
        encoding="utf-8"
    )
    used = set(re.findall(r"m:\s*'(action_[a-z_]+)'", js))
    declared = set()
    for conf in m66_ctrl.SURFACES.values():
        declared |= set(conf["actions"])
    assert used <= declared, "buttons without a surface action whitelist: %s" % sorted(
        used - declared
    )
    assert {"action_resolve", "action_retire"} <= declared


def test_x5_kpis_and_reports_read_in_the_caller_scope(env, plain):
    from odoo.addons.cd_p03_portal.controllers.a12 import m66 as m66_ctrl

    # The caller is the requester: an employee reads his own tickets (spec s13).
    ticket = _ticket(env, requester_id=_employee(env, "Requester Plain", plain).id)
    ticket.sudo().action_assign(assigned_to=_employee(env, "Agent Ali"))
    caller = env(user=plain)  # Environment.__call__: the portal's caller env
    kpis = m66_ctrl.kpis(caller)
    expected_open = caller["fix.itsm.ticket"].search_count(
        [("state", "in", ("new", "assigned", "in_progress"))]
    )
    assert kpis["tickets_open"] == expected_open  # caller scope, no sudo inflation
    report = m66_ctrl.sla_report(caller)
    mine = [r for r in report["rows"] if r.get("ticket") == ticket.name]
    assert mine, "the caller cannot see the SLA report row"
    assert "escalated" in report["cols"] and "deadline" in report["cols"]
