"""A12 finish, M67: db/seeds/a12_finish_m67.py against rows shaped like fix_dev's.

The legacy rows below reproduce working/A12_evidence/finish/m64_m67/live_queries*.out.txt
with raw SQL, since no current code path could create them. The seed then has to leave
each one honest, redeliver the real dead hand-off, and walk a project to a posted invoice.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


def _seed_module():
    root = Path(__file__).resolve().parents[5]
    spec = importlib.util.spec_from_file_location(
        "a12_finish_m67_seed", root / "db" / "seeds" / "a12_finish_m67.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _seed_user(env, login, *groups):
    gids = [env.ref("base.group_user").id] + [env.ref(x).id for x in groups]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [(6, 0, gids)],
                "company_ids": [(6, 0, env["res.company"].search([]).ids)],
            }
        )
    )


def _typed_cost_column_exists(env):
    """The column of the old typed field. Upgraded databases keep it; a fresh one
    never had it."""
    env.cr.execute(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_name = 'fix_project' AND column_name = 'actual_cost'"
    )
    return bool(env.cr.fetchone())


def _sql_project(env, name, state, budget, project_type="internal", manager=None, actual=None):
    project = env["fix.project"].create({"name": name, "project_type": project_type})
    env.cr.execute(
        "UPDATE fix_project SET code='PRJ/New', state=%s, budget=%s, manager_id=%s, "
        "baseline_budget=NULL WHERE id=%s",
        (state, budget, manager.id if manager else None, project.id),
    )
    if actual and _typed_cost_column_exists(env):
        env.cr.execute("UPDATE fix_project SET actual_cost=%s WHERE id=%s", (actual, project.id))
    return project


def _sql_billing(env, project, amount, state, ref=None):
    line = env["fix.project.billing"].create({"project_id": project.id, "amount": 0.0})
    env.cr.execute(
        "UPDATE fix_project_billing SET amount=%s, state=%s, invoice_ref=%s, "
        "invoiced_on=%s WHERE id=%s",
        (amount, state, ref, "2026-10-28" if ref else None, line.id),
    )
    return line


@pytest.fixture
def world(odoo_env):
    env = odoo_env
    env.company.partner_id.vat = "1234567890123"
    harness = next(
        module
        for name, module in sys.modules.items()
        if name.endswith("conftest") and hasattr(module, "link_statutory_chart")
    )
    harness.link_statutory_chart(env)
    harness._head_office_branch(env, env.company)
    for login, group in (
        ("seed.dofa.t2@1000fix.local", "cd_entity_config.group_dofa_tier_2"),
        ("seed.dofa.t3@1000fix.local", "cd_entity_config.group_dofa_tier_3"),
        ("seed.dofa.t4@1000fix.local", "cd_entity_config.group_dofa_tier_4"),
        ("seed.fin.billing@1000fix.local", "account.group_account_invoice"),
    ):
        if not env["res.users"].search_count([("login", "=", login)]):
            _seed_user(env, login, group)
    manager = env["hr.employee"].create({"name": "Live Manager 6"})
    data = {"env": env, "manager": manager}
    data["p1"] = _sql_project(env, "Seed Project 1", "active", 100000.0)
    data["p2"] = _sql_project(env, "Seed Project 2", "active", 1000000.0, "client")
    data["p3"] = _sql_project(env, "Seed Project 3", "active", 500000.0)
    data["p4"] = _sql_project(
        env, "ERP Phase 2", "active", 4500000.0, manager=manager, actual=1850000.0
    )
    data["p5"] = _sql_project(
        env, "Chattogram Rollout", "active", 2800000.0, "infrastructure", manager
    )
    data["p6"] = _sql_project(env, "Portal Revamp", "draft", 1600000.0, "client", manager)
    env.invalidate_all()
    data["line4"] = _sql_billing(env, data["p2"], 900000.0, "ready")
    data["line5"] = _sql_billing(env, data["p2"], 650000.0, "planned")
    data["line6"] = _sql_billing(env, data["p3"], 1200000.0, "invoiced", "INV/2026/00031")
    Milestone = env["fix.project.milestone"]
    data["ms_foreign"] = Milestone.create({"name": "Seed Milestone 1", "project_id": data["p1"].id})
    data["ms_done"] = Milestone.create({"name": "Seed Milestone 2", "project_id": data["p2"].id})
    env.cr.execute(
        "UPDATE fix_project_milestone SET state='done' WHERE id=%s", (data["ms_done"].id,)
    )
    task = env["fix.project.task"].create({"name": "Seed task", "project_id": data["p4"].id})
    env.cr.execute(
        "UPDATE fix_project_task SET milestone_id=%s WHERE id=%s", (data["ms_foreign"].id, task.id)
    )
    data["task"] = task
    gate_rows = [("g3_execution", "conditional", "held", data["p4"])]
    gate_rows += [("g2_planning", "pass", "closed", data["p5"])]
    gate_rows += [("g1_initiation", None, "scheduled", data["p6"])]
    data["gates"] = []
    for kind, decision, state, project in gate_rows:
        gate = env["fix.project.gate"].create({"project_id": project.id, "gate": kind})
        env.cr.execute(
            "UPDATE fix_project_gate SET reviewer_id=%s, decision=%s, state=%s, "
            "checklist_passed=true WHERE id=%s",
            (manager.id, decision, state, gate.id),
        )
        data["gates"].append(gate)
    env.flush_all()
    env.invalidate_all()
    # A real risk, escalated by the real publisher, in the payload live holds (no
    # probability or impact), dead on the consumer exactly as live shows it.
    risk = env["fix.project.risk"].create(
        {
            "project_id": data["p3"].id,
            "title": "Network not ready",
            "probability": "high",
            "impact": "high",
        }
    )
    event = env["fix.event.outbox"].search(
        [("event_type", "=", "project.risk_escalated"), ("aggregate_id", "=", risk.id)]
    )
    payload = json.loads(event.payload)
    payload.pop("probability")
    payload.pop("impact")
    event.write({"payload": json.dumps(payload)})
    consumer = env.ref("cd_grc.consumer_project_risk_escalated")
    env["fix.event.consumer.delivery"].create(
        {
            "subscription_id": consumer.id,
            "event_id": event.id,
            "state": "dead",
            "attempts": 3,
            "last_error": "AttributeError: 'str' object has no attribute 'get'",
        }
    )
    data["risk"] = risk
    data["event"] = event
    return data


def test_a12f_seed_leaves_every_contradicting_row_honest(world):
    env = world["env"]
    out = _seed_module().run(env)
    env.flush_all()
    env.invalidate_all()
    for key in ("p1", "p2", "p3", "p4", "p5"):
        project = world[key]
        assert project.state == "on_hold", key
        assert project.code != "PRJ/New" and project.code.startswith("PRJ/")
        assert project.approval_state == "approved", key
        assert project.dofa_approved and project.baseline_budget == project.budget
        assert project.manager_id
    assert world["p6"].state == "draft" and world["p6"].code.startswith("PRJ/")
    # Approvals went through the engine, to a synthetic holder.
    request = world["p4"].approval_request_id
    assert request.state == "approved" and request.tier == "tier_4"
    assert request.decided_by_id.login.startswith("seed.dofa.")

    line6 = world["line6"]
    assert line6.state == "planned" and not line6.invoice_ref and not line6.invoice_id
    assert env["account.move"].search_count([("name", "=", "INV/2026/00031")]) == 0
    assert "INV/2026/00031" in " ".join(line6.message_ids.mapped("body"))
    assert world["line4"].state == "planned"
    assert world["line5"].state == "planned"
    above = " ".join(out["for_a_person"])
    assert world["p2"].code in above and world["p3"].code in above

    assert not world["task"].milestone_id
    assert world["ms_done"].state == "pending"
    for gate in world["gates"]:
        assert gate.reviewer_id != gate.project_id.manager_id
        assert gate.state == "scheduled" and not gate.decision and not gate.checklist_passed
    # Held projects cannot resume on their own: their gates need a real sponsor.
    with pytest.raises(Exception, match="not closed with a pass"):
        world["p4"].action_resume()
    if _typed_cost_column_exists(env):
        assert "1850000.00" in " ".join(world["p4"].message_ids.mapped("body"))


def test_a12f_seed_redelivers_the_dead_handoff_through_the_real_relay(world):
    env = world["env"]
    risk = world["risk"]
    out = _seed_module().run(env)
    assert out["handoffs_redelivered"]["dead_found"] == 1
    assert out["handoffs_redelivered"]["now_done"] == 1
    assert out["handoffs_redelivered"]["still_not_done"] == []
    entry = env["fix.risk.register"].search([("name", "like", risk.name)])
    assert len(entry) == 1 and entry.risk_score == 25
    delivery = env["fix.event.consumer.delivery"].search(
        [
            ("subscription_id", "=", env.ref("cd_grc.consumer_project_risk_escalated").id),
            ("event_id", "=", world["event"].id),
        ]
    )
    assert delivery.state == "done"


def test_a12f_seed_walks_a_project_to_a_real_posted_invoice(world):
    env = world["env"]
    out = _seed_module().run(env)
    walk = out["walk_closed"]
    assert walk["state"] == "completed", out
    assert walk["invoice_state"] == "posted" and walk["invoice_total"] == 135000.0
    assert walk["billing_state"] in ("paid", "invoiced")
    assert walk["risk_on_register"] == 1
    move = env["account.move"].search([("name", "=", walk["invoice"])])
    log = env["fix.journal.posting.log"].search([("move_id", "=", move.id)])
    assert log.source == "ar" and log.posted_by.login == "seed.fin.billing@1000fix.local"
    running = out["walk_running"]
    assert running["state"] == "active"
    line = env["fix.project.billing"].search([("name", "=", running["billing_ready_for_finance"])])
    assert line.state == "ready" and not line.invoice_id


def test_a12f_seed_runs_twice_without_changing_anything_more(world):
    env = world["env"]
    seed = _seed_module()
    seed.run(env)
    # The relay posts the hand-off trail of what the walk published: that is the
    # relay's work, not a second run of the seed.
    env["fix.event.outbox"].sudo().cron_relay(limit=10000)
    env.flush_all()
    counts = {
        model: env[model].search_count([])
        for model in (
            "fix.project",
            "fix.project.gate",
            "fix.project.billing",
            "fix.approval.request",
            "fix.risk.register",
            "account.move",
            "res.users",
        )
    }
    messages = env["mail.message"].search_count([("model", "=", "fix.project")])
    second = seed.run(env)
    env.flush_all()
    assert second["codes"] == [] and second["held"] == [] and second["gates_reset"] == []
    assert second["billing_moved_back"] == [] and second["tasks_unlinked"] == []
    assert second["walk_closed"] == "already walked"
    assert second["walk_running"] == "already walked"
    assert second["handoffs_redelivered"]["dead_found"] == 0
    for model, count in counts.items():
        assert env[model].search_count([]) == count, model
    assert env["mail.message"].search_count([("model", "=", "fix.project")]) == messages
