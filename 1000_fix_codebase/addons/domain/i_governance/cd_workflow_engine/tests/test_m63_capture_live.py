"""M63 capture audit (2026-11-18): the three new records, live, as non-admin users.

Every test runs in the rolled-back test transaction, with users created for
it: a plain employee (the attacker), two DoA Administrators, a Platform Admin
and a complaint clerk.

  * fix.rule.simulation - a DoA matrix rule run over a past period, with no
    side effect, kept as evidence (FR-BPA-007, BRU-BPA-04/22);
  * fix.automation.register - the routine-work register, the denominator of
    the automation rate (AUT-BPA-21, AC-25);
  * fix.workflow.intervention - every Complete / Mark Failed / Escalate /
    Terminate on an instance is recorded with its reason (FR-BPA-008,
    BRU-BPA-15/23).
"""

import types
from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError
from psycopg2 import IntegrityError

REFUSED = (UserError, ValidationError, AccessError)
DOA = "cd_workflow_engine.group_doa_administrator"
PLATFORM = "cd_entity_config.group_platform_admin"


def _user(env, login, groups=()):
    gids = [env.ref("base.group_user").id] + [env.ref(x).id for x in groups]
    ou = env["operating.unit"].search([], limit=1)
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [(6, 0, gids)],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )
    env["hr.employee"].create({"name": login, "user_id": user.id})
    return user


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.ou = env["operating.unit"].search([], limit=1)
    x.p = _user(env, "m63c_plain")
    x.clerk = _user(env, "m63c_clerk")
    x.doa = _user(env, "m63c_doa", [DOA])
    x.doa2 = _user(env, "m63c_doa2", [DOA])
    x.ops = _user(env, "m63c_platform", [PLATFORM])
    return x


def _automation(env, code="AUT-963", **kw):
    # 19.0.1.2.0 (A11 fix B1): engine values are the honest taxonomy and an
    # active row's reference must resolve — this helper needs a LIVE
    # automation for the routine-work register, so it names a real method.
    vals = {
        "code": code,
        "trigger": "Nightly",
        "action": "Reconcile the day",
        "engine": "odoo_method",
        "engine_ref": "method:fix.service.order._flag_rework",
        "implementation": "partial",
    }
    vals.update(kw)
    return env["fix.automation"].create(vals)


# ============================================================ simulation
def _complaints(c):
    if "fix.complaint" not in c.env:
        pytest.skip("cd_cx_feedback is not installed")
    customer = c.env["res.partner"].create({"name": "M63C Customer"})
    out = c.env["fix.complaint"]
    for severity in ("minor", "minor", "critical"):
        out |= (
            c.env["fix.complaint"]
            .with_user(c.clerk)
            .create(
                {
                    "name": "M63C-%s" % severity,
                    "customer_id": customer.id,
                    "operating_unit_id": c.ou.id,
                    "description": "m63 capture",
                    "severity": severity,
                    "concession_amount": 500.0,
                    "concession_type": "refund",
                    "dofa_justification": "Repeat failure.",
                }
            )
        )
    return out


def _candidate(c, **kw):
    """A new rule version not yet in force (from tomorrow)."""
    vals = {
        "name": "M63C critical complaints",
        "decision_domain": "concession",
        "res_model": "fix.complaint",
        "condition": "[('severity', '=', 'critical')]",
        "approval_policy": "all",
        "sla_hours": 8,
        "max_escalations": 2,
        "final_action": "keep",
        "date_from": fields.Date.context_today(c.env["fix.approval.matrix"]) + timedelta(days=1),
    }
    vals.update(kw)
    return c.env["fix.approval.matrix"].with_user(c.doa).create(vals)


def _simulate(c, rule, user=None):
    today = fields.Date.context_today(c.env["fix.rule.simulation"])
    return (
        c.env["fix.rule.simulation"]
        .with_user(user or c.doa)
        .create({"matrix_id": rule.id, "date_from": today, "date_to": today})
    )


class TestRuleSimulation:
    def test_doa_admin_simulates_a_new_rule_over_history(self, c):
        complaints = _complaints(c)
        rule = _candidate(c)
        sim = _simulate(c, rule)
        assert sim.run_by_id == c.doa and sim.run_at
        assert sim.target_models == "fix.complaint"
        assert sim.evaluated_count >= len(complaints)
        assert sim.matched_count >= 1  # the critical one
        # It would run "all approve, 8 h" instead of the default "any, 24 h".
        assert sim.changed_count >= 1
        assert "would route differently" in sim.summary
        assert "M63C-critical" in (sim.sample_differences or "")
        assert "M63C-minor" not in (sim.sample_differences or "")
        assert rule.simulation_count == 1 and rule.last_simulated_at

    def test_a_simulation_has_no_side_effect(self, c):
        complaints = _complaints(c)
        rule = _candidate(c)
        counts = {
            m: c.env[m].sudo().search_count([])
            for m in ("fix.approval.request", "fix.workflow.task", "mail.activity")
        }
        messages = c.env["mail.message"].sudo().search_count([])
        _simulate(c, rule)
        assert counts == {m: c.env[m].sudo().search_count([]) for m in counts}
        assert c.env["mail.message"].sudo().search_count([]) == messages
        assert set(complaints.mapped("approval_state")) <= {"none", False}

    def test_identical_terms_change_nothing(self, c):
        _complaints(c)
        # The default rule is any / 24 h / 1 escalation / keep: a candidate
        # saying the same routes every record the same way.
        rule = _candidate(c, approval_policy="any", sla_hours=24, max_escalations=1)
        sim = _simulate(c, rule)
        assert sim.matched_count >= 1 and sim.changed_count == 0
        assert "No approval in the period would have run differently." in sim.summary

    def test_plain_user_cannot_simulate(self, c):
        rule = _candidate(c)
        with pytest.raises(AccessError):
            _simulate(c, rule, user=c.p)

    def test_a_simulation_is_evidence(self, c):
        _complaints(c)
        sim = _simulate(c, _candidate(c))
        for user in (c.doa, c.doa2):
            with pytest.raises(REFUSED):
                sim.with_user(user).write({"date_to": sim.date_from})
            with pytest.raises(REFUSED):
                sim.with_user(user).unlink()
        with pytest.raises(UserError):
            sim.sudo().unlink()

    def test_results_cannot_be_typed(self, c):
        rule = _candidate(c)
        today = fields.Date.context_today(rule)
        with pytest.raises(UserError):
            c.env["fix.rule.simulation"].with_user(c.doa).create(
                {
                    "matrix_id": rule.id,
                    "date_from": today,
                    "date_to": today,
                    "changed_count": 0,
                    "summary": "nothing changes, trust me",
                    "evaluated_count": 9999,
                }
            )

    def test_never_simulated_rules_are_counted(self, c):
        from odoo.addons.cd_p03_portal.controllers.a11 import m63

        Matrix = c.env["fix.approval.matrix"]
        in_force = Matrix.with_user(c.doa).create(
            {
                "name": "M63C in force",
                "decision_domain": "concession",
                "res_model": "fix.complaint",
                "condition": "[('severity', '=', 'critical')]",
                "approval_policy": "all",
                "sla_hours": 4,
                "max_escalations": 1,
                "final_action": "keep",
            }
        )
        before = m63.kpis(c.env)["rules_unsimulated"]
        assert in_force in Matrix._rules_in_force_never_simulated()
        _complaints(c)
        _simulate(c, in_force)
        assert in_force not in Matrix._rules_in_force_never_simulated()
        assert m63.kpis(c.env)["rules_unsimulated"] == before - 1

    def test_period_must_be_ordered(self, c):
        rule = _candidate(c)
        today = fields.Date.context_today(rule)
        with pytest.raises(IntegrityError), c.env.cr.savepoint():
            c.env["fix.rule.simulation"].with_user(c.doa).create(
                {"matrix_id": rule.id, "date_from": today, "date_to": today - timedelta(1)}
            )

    def test_unnamed_rows_read_as_their_domain(self, c):
        row = c.env["fix.approval.matrix"].create(
            {"decision_domain": "write_off", "approval_policy": "any", "sla_hours": 24}
        )
        assert row.display_name == "Write-Off"
        aut = _automation(c.env)
        assert aut.display_name == "AUT-963 · Nightly"


# ============================================================ register
class TestRoutineWorkRegister:
    def test_the_register_is_the_automation_rate(self, c):
        from odoo.addons.cd_p03_portal.controllers.a11 import m63

        Register = c.env["fix.automation.register"]
        before_rows = Register.sudo().search([])  # a clone may already hold rows
        aut = _automation(c.env)
        Register.with_user(c.doa).create(
            {
                "name": "Key in walk-in intakes",
                "process_area": "Front Desk",
                "volume_per_month": 100,
            }
        )
        Register.with_user(c.doa).create(
            {
                "name": "Reconcile bKash settlements",
                "process_area": "Treasury",
                "volume_per_month": 300,
                "automated": True,
                "automation_id": aut.id,
                "stp_rate": 50.0,
            }
        )
        rows = Register.sudo().search([])
        total = sum(rows.mapped("volume_per_month"))
        automated = sum(rows.mapped("automated_volume"))
        assert round(automated / total * 100.0, 1) == m63.kpis(c.env)["automation_rate"]
        if not before_rows:
            assert m63.kpis(c.env)["automation_rate"] == 37.5
        pack = m63.automation_rate(c.env)
        areas = {r["area"]: r for r in pack["rows"]}
        assert areas["Treasury"]["automated"] == 150.0 and areas["Treasury"]["rate"] == 50.0
        assert areas["Front Desk"]["rate"] == 0.0

    def test_automated_names_an_active_automation(self, c):
        Register = c.env["fix.automation.register"].with_user(c.doa)
        base = {
            "name": "Chase overdue AMC renewals",
            "process_area": "B2B",
            "volume_per_month": 40,
            "automated": True,
        }
        with pytest.raises(ValidationError, match="name the automation"), c.env.cr.savepoint():
            Register.create(dict(base))
        off = _automation(c.env, code="AUT-964", active=False)
        with pytest.raises(ValidationError, match="switched off"), c.env.cr.savepoint():
            Register.create(dict(base, automation_id=off.id))
        with pytest.raises(ValidationError, match="above zero"), c.env.cr.savepoint():
            Register.create(dict(base, automated=False, volume_per_month=0))

    def test_plain_user_reads_but_cannot_register_or_review(self, c):
        Register = c.env["fix.automation.register"]
        row = Register.with_user(c.doa).create(
            {"name": "Post daily cash", "process_area": "Finance", "volume_per_month": 30}
        )
        assert row.with_user(c.p).read(["name"])
        with pytest.raises(AccessError):
            Register.with_user(c.p).create(
                {"name": "x", "process_area": "x", "volume_per_month": 1}
            )
        with pytest.raises(AccessError):
            row.with_user(c.p).action_mark_reviewed()
        with pytest.raises(UserError):
            row.with_user(c.doa).write({"last_reviewed_on": fields.Date.today()})
        row.with_user(c.doa2).action_mark_reviewed()
        assert row.reviewed_by_id == c.doa2 and row.last_reviewed_on


# ============================================================ interventions
def _instance(env, user=None):
    Instance = env["fix.workflow.instance"]
    return (Instance.with_user(user) if user else Instance).create(
        {"res_model": "fix.complaint", "res_id": 1}
    )


class TestManualIntervention:
    def test_each_monitor_button_is_a_recorded_intervention(self, c):
        inst = _instance(c.env)
        inst.with_user(c.doa).action_escalate(reason="Customer waiting since Tuesday.")
        inst.with_user(c.doa).action_complete(reason="Engine lost the callback; done by hand.")
        assert inst.state == "completed" and inst.escalated and inst.finished_at
        done = inst.intervention_ids.sorted("id")
        assert done.mapped("action") == ["escalate", "complete"]
        assert set(done.mapped("operator_id")) == {c.doa}
        assert done[-1].state_before == "Running" and done[-1].state_after == "Completed"
        assert inst.intervention_count == 2

    def test_a_reason_is_required(self, c):
        inst = _instance(c.env)
        for reason in (None, "", "   ", "because"):
            with pytest.raises(UserError, match="State why"):
                inst.with_user(c.doa).action_fail(reason=reason)
        assert inst.state == "running" and not inst.intervention_ids

    def test_plain_user_cannot_intervene(self, c):
        inst = _instance(c.env)
        with pytest.raises(AccessError):
            inst.with_user(c.p).action_terminate(reason="I do not like this one.")
        with pytest.raises(AccessError):
            c.env["fix.workflow.intervention"].with_user(c.p).create(
                {"instance_id": inst.id, "action": "complete", "reason": "Forged completion."}
            )
        assert inst.state == "running"

    def test_platform_admin_may_terminate(self, c):
        inst = _instance(c.env)
        inst.with_user(c.ops).action_terminate(reason="Duplicate start after a restart.")
        assert inst.state == "cancelled"
        assert inst.intervention_ids.operator_id == c.ops

    def test_nobody_completes_an_instance_they_started(self, c):
        inst = _instance(c.env, user=c.doa)
        with pytest.raises(UserError, match="You started"):
            inst.with_user(c.doa).action_complete(reason="My own process, finished by me.")
        inst.with_user(c.doa2).action_complete(reason="Checked the ledger: posted already.")
        assert inst.state == "completed"

    def test_only_a_running_instance_is_completed_or_failed(self, c):
        inst = _instance(c.env)
        inst.with_user(c.doa).action_fail(reason="The DAG failed three retries.")
        with pytest.raises(UserError, match="only a running instance"):
            inst.with_user(c.doa).action_complete(reason="Try to rescue a failed one.")
        assert inst.state == "failed"

    def test_an_intervention_is_append_only(self, c):
        inst = _instance(c.env)
        inst.with_user(c.doa).action_escalate(reason="Waiting on the branch manager.")
        rec = inst.intervention_ids
        for env_rec in (rec.with_user(c.doa), rec.sudo()):
            with pytest.raises(UserError):
                env_rec.write({"reason": "rewritten"})
            with pytest.raises(UserError):
                env_rec.unlink()

    def test_the_stamps_cannot_be_typed(self, c):
        inst = _instance(c.env)
        rec = (
            c.env["fix.workflow.intervention"]
            .with_user(c.doa)
            .create(
                {
                    "instance_id": inst.id,
                    "action": "escalate",
                    "reason": "Stuck at the parts step.",
                    "operator_id": c.p.id,
                    "at": "2020-01-01 00:00:00",
                }
            )
        )
        assert rec.operator_id == c.doa and str(rec.at)[:4] != "2020"

    def test_the_workspace_cannot_type_an_instance(self, c):
        from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api

        assert api.SURFACES["fix.workflow.instance"]["writable"] == frozenset()
        assert "action_terminate" in api.SURFACES["fix.workflow.instance"]["actions"]
        assert api.SURFACES["fix.workflow.intervention"]["writable"] == frozenset(
            {"instance_id", "action", "reason"}
        )


def test_the_spec_failure_behaviours_can_be_declared(c):
    aut = _automation(c.env, code="AUT-965")
    for policy in ("block", "escalate", "compensate", "retry", "manual_fallback"):
        aut.with_user(c.doa).write({"failure_policy": policy})
        assert aut.failure_policy == policy
