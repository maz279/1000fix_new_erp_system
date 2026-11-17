"""A11 audit E1-E4: the M63 rule book, delegation and engine semantics.

Every attack the A11 probes (working/A11_evidence/probes/m63/probe_m63.py)
found open is replayed here as a NON-ADMIN user created in the rolled-back
transaction, and must now be refused; next to it, the legitimate role does
the same job through the proper path, so no control blocks everyone. Test
names carry the probe / finding id (M63 E19 = probe test 19).

  E1 rule book locked to the DoA Administrator; task, instance and rule
     fields guarded; matrix condition and approver group validated on save;
     P03 write whitelists on the M63 surfaces          (M63-2, -7, -10, -12)
  E2 delegation is the delegator's act, re-checked at decision, expired by
     cron                                               (M63-1, -5)
  E3 the authority group is coded; a matrix group only narrows (M63-2)
  E4 quorum, stamp clearing, escalation exclusions, pinned terms, KPI
                                                        (M63-3, -4, -6, -11)
"""

import types
from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
T1 = "cd_entity_config.group_dofa_tier_1"
T2 = "cd_entity_config.group_dofa_tier_2"
T3 = "cd_entity_config.group_dofa_tier_3"
DOA = "cd_workflow_engine.group_doa_administrator"
HR_MANAGER = "hr.group_hr_manager"
SALES = "sales_team.group_sale_salesman"
SALES_ALL = "sales_team.group_sale_salesman_all_leads"
SALES_MGR = "sales_team.group_sale_manager"
POLICY_PARAM = "cd_workflow_engine.substitution_authority_groups"
M63_MODELS = (
    "fix.automation",
    "fix.workflow.instance",
    "fix.workflow.task",
    "fix.approval.matrix",
    "fix.approval.request",
    "fix.approval.history",
    "fix.approval.substitution",
    "fix.business.rule",
    # M63 capture audit (2026-11-18)
    "fix.rule.simulation",
    "fix.automation.register",
    "fix.workflow.intervention",
)


def _user(env, login, groups=(), manager=None):
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
    env["hr.employee"].create(
        {
            "name": login,
            "user_id": user.id,
            "parent_id": manager.employee_ids[:1].id if manager else False,
        }
    )
    return user


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    if "fix.complaint" not in env:
        pytest.skip("cd_cx_feedback is not installed")
    x = types.SimpleNamespace(env=env)
    x.ou = env["operating.unit"].search([], limit=1)
    x.clerk = _user(env, "a11e_clerk")
    x.p = _user(env, "a11e_plain")  # the attacker: base.group_user + OU only
    x.mgr = _user(env, "a11e_t1_manager")
    x.t1 = _user(env, "a11e_t1", [T1], manager=x.mgr)
    x.t1b = _user(env, "a11e_t1b", [T1])
    x.t2 = _user(env, "a11e_t2", [T2])
    x.doa = _user(env, "a11e_doa_admin", [DOA])
    x.hr = _user(env, "a11e_hr_manager", [HR_MANAGER])
    x.customer = env["res.partner"].create({"name": "A11E Customer"})
    x.accomplice = env["res.partner"].create({"name": "A11E Accomplice"})
    return x


def complaint(c, user=None, amount=800.0, **kw):
    """A service-recovery concession: <=1,000 Tier 1, <=5,000 Tier 2."""
    vals = {
        "name": "A11E-%s" % (user or c.clerk).login,
        "customer_id": c.customer.id,
        "operating_unit_id": c.ou.id,
        "description": "a11 e1-e4",
        "severity": "minor",
        "concession_amount": amount,
        "concession_type": "refund",
        "dofa_justification": "Repeat failure on the same repair.",
    }
    vals.update(kw)
    return c.env["fix.complaint"].with_user(user or c.clerk).create(vals)


def task_of(rec, user):
    return rec.approval_request_id.task_ids.filtered(
        lambda t: t.state == "pending" and t.assigned_user_id == user
    )


def assignees(rec):
    return rec.approval_request_id.task_ids.filtered(lambda t: t.state == "pending").mapped(
        "assigned_user_id"
    )


def gate_passes(rec):
    try:
        rec._concession_denial()
    except REFUSED:
        return False
    return True


def matrix_row(env, user=None, **kw):
    vals = {
        "name": "A11E rule",
        "decision_domain": "concession",
        "res_model": "fix.complaint",
        "approval_policy": "any",
        "sla_hours": 24,
        "max_escalations": 1,
        "final_action": "keep",
    }
    vals.update(kw)
    Model = env["fix.approval.matrix"]
    return (Model.with_user(user) if user else Model).create(vals)


def sub_vals(env, absent, delegate, **kw):
    today = fields.Date.context_today(env["fix.approval.substitution"])
    vals = {
        "absent_approver_id": absent.employee_ids[:1].id,
        "delegate_id": delegate.employee_ids[:1].id,
        "start_date": today,
        "end_date": today + timedelta(days=5),
        "reason": "annual leave",
    }
    vals.update(kw)
    return vals


def overdue(req):
    req.task_ids.filtered(lambda t: t.state == "pending")._guarded().write(
        {"due_at": fields.Datetime.now() - timedelta(hours=2)}
    )


def run_cron(env, xmlid="cd_workflow_engine.ir_cron_approval_escalate_overdue"):
    """The real ir.cron record's server action, not a direct method call."""
    env.ref(xmlid).sudo().ir_actions_server_id.run()


@pytest.fixture
def p03(c):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g
    import odoo.addons.cd_p03_portal.controllers.p03_service_order_api as s

    ctl = g.P03GenericApiController()
    mw = getattr(g.P03GenericApiController.model_write, "original_endpoint", None)
    ma = getattr(g.P03GenericApiController.model_action, "original_endpoint", None)
    mw = mw or g.P03GenericApiController.model_write
    ma = ma or g.P03GenericApiController.model_action
    old_g, old_s = getattr(g, "request", None), getattr(s, "request", None)

    def as_user(user):
        req = types.SimpleNamespace(env=c.env(user=user.id))
        g.request = req
        s.request = req

    as_user(c.p)
    try:
        yield types.SimpleNamespace(
            write=lambda **kw: mw(ctl, **kw), action=lambda **kw: ma(ctl, **kw), as_user=as_user
        )
    finally:
        g.request, s.request = old_g, old_s


# =========================================================================== E1
class TestE1RuleBookLocked:
    def test_m63_24_plain_user_cannot_change_the_matrix(self, c, p03):
        row = matrix_row(c.env, user=c.doa, name="DoA-owned rule")
        with pytest.raises(AccessError):
            matrix_row(c.env, user=c.p, decision_domain="campaign_budget", res_model=False)
        with pytest.raises(AccessError):
            row.with_user(c.p).write({"sla_hours": 1, "max_escalations": 0})
        with pytest.raises(AccessError):
            row.with_user(c.p).write({"active": False})
        with pytest.raises(AccessError):
            row.with_user(c.p).unlink()
        res = p03.write(
            model="fix.approval.matrix",
            values={"decision_domain": "kyc", "approval_policy": "any", "final_action": "reject"},
        )
        assert res.get("error"), res
        res = p03.write(model="fix.approval.matrix", record_id=row.id, values={"sla_hours": 1})
        assert res.get("error"), res
        assert row.sla_hours == 24 and row.active
        # Everyone keeps read access (the simulation screen, the engine).
        assert row.with_user(c.p).read(["name"])[0]["name"] == "DoA-owned rule"

    def test_m63_24_doa_administrator_keeps_the_rule_book(self, c, p03):
        row = matrix_row(c.env, user=c.doa, name="Concession SLA")
        row.with_user(c.doa).write({"sla_hours": 8})
        assert row.sla_hours == 8
        p03.as_user(c.doa)
        res = p03.write(model="fix.approval.matrix", record_id=row.id, values={"sla_hours": 12})
        assert not res.get("error"), res
        assert row.sla_hours == 12

    def test_m63_25_rule_cannot_point_a_tier_at_an_empty_group(self, c):
        empty = c.env["res.groups"].create({"name": "A11E nobody"})
        with pytest.raises(AccessError):
            matrix_row(c.env, user=c.p, approver_group_id=empty.id)
        with pytest.raises(ValidationError, match="nobody"), c.env.cr.savepoint():
            matrix_row(c.env, user=c.doa, approver_group_id=empty.id)
        # Proper path: a group with holders is accepted.
        held = c.env["res.groups"].create(
            {"name": "A11E branch T1", "implied_ids": [(4, c.env.ref(T1).id)]}
        )
        c.t1b.write({"group_ids": [(4, held.id)]})
        assert matrix_row(c.env, user=c.doa, approver_group_id=held.id)
        # The real Tier-1 holders still get a concession with no row naming a group.

    def test_m63_28_plain_user_cannot_plant_an_auto_reject(self, c):
        with pytest.raises(AccessError):
            matrix_row(c.env, user=c.p, sla_hours=1, max_escalations=0, final_action="reject")
        rec = complaint(c)
        rec.with_user(c.clerk).action_request_approval()
        req = rec.approval_request_id
        for _ in range(2):
            overdue(req)
            run_cron(c.env)
        assert req.state == "pending"

    def test_m63_30_malformed_condition_refused_on_save(self, c):
        with pytest.raises(ValidationError, match="condition"), c.env.cr.savepoint():
            matrix_row(c.env, user=c.doa, condition="[('x', '=', ")
        with pytest.raises(ValidationError, match="condition"), c.env.cr.savepoint():
            matrix_row(c.env, user=c.doa, condition="[('no_such_field', '=', 1)]")
        with pytest.raises(ValidationError, match="condition"), c.env.cr.savepoint():
            matrix_row(c.env, user=c.doa, condition="'severity'")
        # A decision-domain row (no model) is dry-run on the domain's models.
        with pytest.raises(ValidationError, match="condition"), c.env.cr.savepoint():
            matrix_row(c.env, user=c.doa, res_model=False, condition="[('bogus', '=', 1)]")
        ok = matrix_row(c.env, user=c.doa, condition="[('concession_amount', '>', 500)]")
        rec = complaint(c)
        assert c.env["fix.approval.matrix"]._match(rec) == ok

    def test_m63_30_legacy_bad_condition_refuses_clearly(self, c):
        """A row saved before validation (written by SQL) no longer crashes a
        request with a SyntaxError: the request is refused, naming the rule."""
        row = matrix_row(c.env, user=c.doa, name="Legacy rule")
        c.env.cr.execute(
            "UPDATE fix_approval_matrix SET condition = %s WHERE id = %s", ("[('x', '=', ", row.id)
        )
        row.invalidate_recordset()
        rec = complaint(c)
        with pytest.raises(UserError, match="invalid condition"):
            rec.with_user(c.clerk).action_request_approval()

    def test_m63_34_task_fields_are_engine_set(self, c, p03):
        rec = complaint(c)
        rec.with_user(c.clerk).action_request_approval()
        task = task_of(rec, c.t1)
        inst = c.env["fix.workflow.instance"].create({"res_model": "fix.complaint"})
        employee = c.p.employee_ids[:1]
        for user in (c.p, c.t1):
            for vals in (
                {"task_type": "review"},
                {"name": "nothing to see"},
                {"created_at": fields.Datetime.now() - timedelta(days=30)},
                {"instance_id": inst.id},
                {"assigned_to_id": employee.id},
                {"comment": "typed"},
            ):
                with pytest.raises(REFUSED):
                    task.with_user(user).write(vals)
        with pytest.raises(REFUSED):  # the guard (name) or the ACL (no create)
            c.env["fix.workflow.task"].with_user(c.p).create({"name": "forged"})
        with pytest.raises(AccessError):
            c.env["fix.workflow.task"].with_user(c.p).check_access("create")
        res = p03.write(
            model="fix.workflow.task", record_id=task.id, values={"task_type": "review"}
        )
        assert res.get("error"), res
        assert task.task_type == "approval"
        assert (
            c.env["fix.workflow.task"]
            .with_user(c.t1)
            .search_count([("id", "=", task.id), ("task_type", "=", "approval")])
        )
        # Proper path: the assignee decides; the comment is the decision's.
        task.with_user(c.t1).action_approve(comment="ok")
        assert task.comment == "ok" and rec.approval_state == "approved"

    def test_m63_37_business_rules_owned_and_stamped(self, c):
        rule = c.env["fix.business.rule"].create(
            {"code": "BRU-A11E-1", "name": "Discount cap", "expression": "discount <= 0.15"}
        )
        with pytest.raises(AccessError):
            c.env["fix.business.rule"].with_user(c.p).create(
                {"code": "BRU-A11E-X", "name": "x", "expression": "__import__('os')"}
            )
        with pytest.raises(AccessError):
            rule.with_user(c.p).write({"expression": "True"})
        # The DoA administrator edits; the stamp is set, never typed.
        with pytest.raises(UserError):
            rule.with_user(c.doa).write({"last_changed_by": c.t2.id})
        with pytest.raises(UserError):
            rule.with_user(c.doa).write({"version": 7})
        rule.with_user(c.doa).write({"expression": "discount <= 0.10"})
        assert rule.version == 2 and rule.last_changed_by == c.doa
        rule.with_user(c.doa).write({"error_message": "Cap exceeded"})
        assert rule.version == 2  # wording only: stamped, same version
        rule.with_user(c.doa).action_new_version()
        assert rule.version == 3
        with pytest.raises(AccessError):
            rule.with_user(c.p).action_new_version()

    def test_m63_38_automation_register_owned(self, c):
        aut = c.env["fix.automation"].create(
            {"code": "AUT-951", "trigger": "x", "action": "y", "engine": "airflow"}
        )
        with pytest.raises(AccessError):
            c.env["fix.automation"].with_user(c.p).create(
                {"code": "AUT-952", "trigger": "t", "action": "a", "engine": "airflow"}
            )
        with pytest.raises(AccessError):
            aut.with_user(c.p).write({"active": False, "engine_ref": "dag: none"})
        aut.with_user(c.doa).write({"engine_ref": "dag: fix_aut_951"})
        assert aut.engine_ref == "dag: fix_aut_951" and aut.active

    def test_m63_39_workflow_instance_state_not_typed(self, c):
        inst = c.env["fix.workflow.instance"].create({"res_model": "fix.complaint", "res_id": 1})
        with pytest.raises(REFUSED):  # the guard refuses before the ACL is asked
            inst.with_user(c.p).write({"state": "completed"})
        with pytest.raises(REFUSED):
            c.env["fix.workflow.instance"].with_user(c.p).create({"state": "completed"})
        with pytest.raises(AccessError):
            inst.with_user(c.p).write({"res_id": 2})
        with pytest.raises(AccessError):
            c.env["fix.workflow.instance"].with_user(c.p).create({"res_model": "x"})
        with pytest.raises(AccessError):
            inst.with_user(c.p).action_complete()
        # Even the register's owner cannot type the outcome; the action sets it.
        with pytest.raises(UserError):
            inst.with_user(c.doa).write({"state": "completed"})
        with pytest.raises(UserError):
            c.env["fix.workflow.instance"].with_user(c.doa).create({"state": "completed"})
        own = c.env["fix.workflow.instance"].create({"res_model": "x"})
        # Since the M63 capture audit an operator's completion is a recorded
        # intervention: it needs a reason, and nobody completes an instance
        # they started themself.
        with pytest.raises(UserError, match="State why"):
            own.with_user(c.doa).action_complete()
        own.with_user(c.doa).action_complete(reason="Engine lost the callback; done by hand.")
        assert own.state == "completed" and own.finished_at
        assert own.intervention_ids.operator_id == c.doa

    def test_m63_writable_whitelists_match_the_forms(self, c):
        from odoo.addons.cd_p03_portal.controllers import form_fields
        from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
        from odoo.addons.cd_p03_portal.controllers.a11 import m63

        editable = form_fields.editable_by_model()
        for model in M63_MODELS:
            assert m63.SURFACES[model]["writable"] == frozenset(editable.get(model, ())), model
            assert api.SURFACES[model]["writable"] == m63.WRITABLE[model], model
        assert set(m63.SURFACES) == set(M63_MODELS)
        guarded = {
            "fix.workflow.task": {"task_type", "created_at", "state", "assigned_to_id"},
            "fix.workflow.instance": {"state", "started_at", "finished_at", "escalated"},
            "fix.approval.substitution": {"state", "activated_by_id"},
            "fix.business.rule": {"version", "last_changed_by", "last_changed_on"},
        }
        for model, names in guarded.items():
            assert not (names & m63.WRITABLE[model]), (model, names & m63.WRITABLE[model])

    def test_doa_administrator_group_ships_with_the_dev_admin_only(self, c):
        group = c.env.ref(DOA)
        members = group.user_ids - c.doa
        assert members <= c.env.ref("base.user_admin"), members.mapped("login")


# =========================================================================== E2
class TestE2Delegation:
    def test_m63_19_plain_user_cannot_appoint_himself_a_delegate(self, c):
        Sub = c.env["fix.approval.substitution"]
        with pytest.raises(UserError, match="Only the absent approver"):
            Sub.with_user(c.p).create(sub_vals(c.env, c.t1, c.p))
        own = Sub.with_user(c.t1).create(sub_vals(c.env, c.t1, c.t2))
        assert own.state == "draft"
        for intruder in (c.p, c.t2):  # a stranger, and the delegate himself
            with pytest.raises(UserError):
                own.with_user(intruder).action_activate()
        assert own.state == "draft"
        with pytest.raises(UserError):
            own.with_user(c.p).write({"delegate_id": c.p.employee_ids[:1].id})

    def test_m63_19_proper_path_delegate_decides_on_behalf(self, c):
        """The absent approver records and activates his own substitution; a
        delegate at a higher tier decides on his behalf."""
        sub = c.env["fix.approval.substitution"].with_user(c.t1).create(sub_vals(c.env, c.t1, c.t2))
        sub.with_user(c.t1).action_activate()
        assert sub.state == "active" and sub.activated_by_id == c.t1
        rec = complaint(c)
        rec.with_user(c.clerk).action_request_approval()
        task = task_of(rec, c.t2)
        assert task and task.on_behalf_of_id == c.t1
        task.with_user(c.t2).action_approve()
        assert rec.dofa_approved and rec.approval_request_id.on_behalf_of_id == c.t1

    def test_m63_19_manager_or_hr_may_record_and_activate(self, c):
        sub = c.env["fix.approval.substitution"].with_user(c.hr).create(sub_vals(c.env, c.t1, c.t2))
        with pytest.raises(UserError):
            sub.with_user(c.hr).action_activate()  # HR records; the line activates
        sub.with_user(c.mgr).action_activate()
        assert sub.state == "active" and sub.activated_by_id == c.mgr
        doa_sub = (
            c.env["fix.approval.substitution"].with_user(c.doa).create(sub_vals(c.env, c.t1b, c.t2))
        )
        assert doa_sub.state == "draft"

    def test_m63_20_substitution_not_born_active_nor_back_dated(self, c):
        Sub = c.env["fix.approval.substitution"]
        past = fields.Date.context_today(Sub) - timedelta(days=30)
        with pytest.raises(UserError):
            Sub.with_user(c.t2).create(sub_vals(c.env, c.t2, c.p, state="active"))
        with pytest.raises(UserError, match="back-dated"):
            Sub.with_user(c.t2).create(sub_vals(c.env, c.t2, c.p, start_date=past))
        draft = Sub.with_user(c.t1).create(sub_vals(c.env, c.t1, c.t2))
        with pytest.raises(UserError, match="back-dated"):
            draft.with_user(c.t1).write({"start_date": past})
        with pytest.raises(UserError):
            draft.with_user(c.t1).write({"state": "active"})
        draft.with_user(c.t1).action_activate()
        with pytest.raises(UserError, match="fixed"):
            draft.with_user(c.t1).write({"end_date": draft.end_date + timedelta(days=30)})
        draft.with_user(c.t1).write({"reason": "extended leave"})  # wording is free

    def test_m63_21_substitution_via_p03(self, c, p03):
        values = {
            "absent_approver_id": c.t1.employee_ids[:1].id,
            "delegate_id": c.p.employee_ids[:1].id,
            "start_date": str(fields.Date.context_today(c.env["fix.approval.substitution"])),
            "end_date": "2027-12-31",
            "state": "active",
        }
        res = p03.write(model="fix.approval.substitution", values=values)
        assert res.get("error"), res
        p03.as_user(c.t1)
        values["delegate_id"] = c.t2.employee_ids[:1].id
        res = p03.write(model="fix.approval.substitution", values=values)
        assert not res.get("error"), res
        assert c.env["fix.approval.substitution"].browse(res["id"]).state == "draft"
        res = p03.action(
            model="fix.approval.substitution", ids=[res["id"]], method="action_activate"
        )
        assert res.get("success"), res

    def test_m63_e2_delegate_must_hold_the_authority(self, c):
        Sub = c.env["fix.approval.substitution"]
        weak = Sub.with_user(c.t2).create(sub_vals(c.env, c.t2, c.t1))  # T1 cannot hold T2
        with pytest.raises(UserError, match="must hold the authority"):
            weak.with_user(c.t2).action_activate()
        with pytest.raises(ValidationError, match="must hold the authority"), c.env.cr.savepoint():
            Sub.create(sub_vals(c.env, c.t1, c.p, state="active"))  # even as superuser
        # The policy is configuration: with only Tier 5 listed, T1 authority
        # is not policed and a plain delegate is allowed.
        c.env["ir.config_parameter"].sudo().set_param(
            POLICY_PARAM, "cd_entity_config.group_dofa_tier_5"
        )
        free = Sub.with_user(c.t1).create(sub_vals(c.env, c.t1, c.p))
        free.with_user(c.t1).action_activate()
        assert free.state == "active"

    def test_m63_22_expired_delegation_hands_the_task_back(self, c):
        sub = c.env["fix.approval.substitution"].with_user(c.t1).create(sub_vals(c.env, c.t1, c.t2))
        sub.with_user(c.t1).action_activate()
        rec = complaint(c)
        rec.with_user(c.clerk).action_request_approval()
        task = task_of(rec, c.t2)
        assert task.on_behalf_of_id == c.t1
        sub.with_user(c.t1).action_expire()
        assert sub.state == "expired"
        assert task.assigned_user_id == c.t1 and not task.on_behalf_of_id
        assert "handed_back" in rec.approval_request_id.history_ids.mapped("event")
        with pytest.raises(UserError, match="assignee"):
            task.with_user(c.t2).action_approve()
        task.with_user(c.t1).action_approve()  # the principal decides himself
        assert rec.dofa_approved and rec.dofa_approved_by == c.t1

    def test_m63_22_lapsed_delegation_rechecked_at_decision(self, c):
        """The delegation ends (dates passed, nobody expired it): the delegate's
        decision is not taken; the task goes back to the absent approver."""
        sub = c.env["fix.approval.substitution"].with_user(c.t1).create(sub_vals(c.env, c.t1, c.t2))
        sub.with_user(c.t1).action_activate()
        rec = complaint(c)
        rec.with_user(c.clerk).action_request_approval()
        task = task_of(rec, c.t2)
        yesterday = fields.Date.context_today(sub) - timedelta(days=1)
        sub.sudo().write({"start_date": yesterday - timedelta(days=3), "end_date": yesterday})
        res = task.with_user(c.t2).action_approve()
        assert isinstance(res, dict) and res.get("handed_back") == task.ids
        assert not rec.dofa_approved and rec.approval_state == "pending"
        assert task.state == "pending" and task.assigned_user_id == c.t1
        # Also when the delegate no longer qualifies (loses the tier).
        sub2 = (
            c.env["fix.approval.substitution"].with_user(c.t1b).create(sub_vals(c.env, c.t1b, c.t2))
        )
        sub2.with_user(c.t1b).action_activate()
        rec2 = complaint(c)
        rec2.with_user(c.clerk).action_request_approval()
        task2 = task_of(rec2, c.t2).filtered(lambda t: t.on_behalf_of_id == c.t1b)
        assert task2
        c.t2.write({"group_ids": [(3, c.env.ref(T2).id)]})
        res = task2.with_user(c.t2).action_reject(comment="no")
        assert res.get("handed_back") == task2.ids and rec2.approval_state == "pending"
        assert task2.assigned_user_id == c.t1b and rec2.approval_request_id.state == "pending"

    def test_m63_e2_cron_expires_ended_substitutions(self, c):
        cron = c.env.ref("cd_workflow_engine.ir_cron_approval_substitution_expire")
        assert cron.active and cron.model_id.model == "fix.approval.substitution"
        assert "cron_expire_substitutions" in (cron.code or cron.ir_actions_server_id.code)
        assert cron.interval_type == "days" and cron.interval_number == 1
        sub = c.env["fix.approval.substitution"].with_user(c.t1).create(sub_vals(c.env, c.t1, c.t2))
        sub.with_user(c.t1).action_activate()
        rec = complaint(c)
        rec.with_user(c.clerk).action_request_approval()
        task = task_of(rec, c.t2)
        ended = fields.Date.context_today(sub) - timedelta(days=1)
        sub.sudo().write({"start_date": ended, "end_date": ended})
        current = (
            c.env["fix.approval.substitution"].with_user(c.t1b).create(sub_vals(c.env, c.t1b, c.t2))
        )
        current.with_user(c.t1b).action_activate()
        run_cron(c.env, "cd_workflow_engine.ir_cron_approval_substitution_expire")
        assert sub.state == "expired" and current.state == "active"
        assert task.assigned_user_id == c.t1 and not task.on_behalf_of_id


# =========================================================================== E3
class TestE3CodedAuthority:
    def test_m63_27_matrix_group_cannot_authorise_a_contract(self, c):
        if "contract_verified" not in c.env["crm.lead"]._fields:
            pytest.skip("cd_crm_ext is not installed")
        seller = _user(c.env, "a11e_seller", [SALES])
        attacker = _user(c.env, "a11e_sales_all", [SALES_ALL])
        manager = _user(c.env, "a11e_sales_mgr", [SALES_MGR])
        lead = (
            c.env["crm.lead"]
            .with_user(seller)
            .create(
                {
                    "name": "A11E deal",
                    "type": "opportunity",
                    "user_id": seller.id,
                    "contract_ref": "PO-A11E-1",
                }
            )
        )
        with pytest.raises(AccessError):
            matrix_row(
                c.env,
                user=attacker,
                decision_domain="contract_verification",
                res_model="crm.lead",
                approver_group_id=c.env.ref(SALES_ALL).id,
            )
        # Even a row the DoA administrator saves cannot widen the authority:
        # All-Leads salespeople do not hold Sales Manager, so it is ignored.
        matrix_row(
            c.env,
            user=c.doa,
            decision_domain="contract_verification",
            res_model="crm.lead",
            approver_group_id=c.env.ref(SALES_ALL).id,
        )
        assert lead._approval_group_for(lead._approval_rule(), False) != c.env.ref(SALES_ALL)
        lead.with_user(seller).action_request_approval()
        routed = lead.approval_request_id.task_ids.mapped("assigned_user_id")
        assert attacker not in routed and manager in routed
        task = lead.approval_request_id.task_ids.filtered(lambda t: t.assigned_user_id == manager)
        task.with_user(manager).action_approve()
        assert lead.contract_verified and lead.contract_verified_by == manager

    def test_m63_e3_a_matrix_group_may_only_narrow(self, c):
        narrow = c.env["res.groups"].create(
            {"name": "A11E Dhaka T1", "implied_ids": [(4, c.env.ref(T1).id)]}
        )
        c.t1b.write({"group_ids": [(4, narrow.id)]})
        matrix_row(c.env, user=c.doa, approver_group_id=narrow.id)
        rec = complaint(c)
        rec.with_user(c.clerk).action_request_approval()
        assert assignees(rec) == c.t1b
        task_of(rec, c.t1b).with_user(c.t1b).action_approve()
        assert rec.dofa_approved
        # A wider group (every internal user) is ignored: the tier decides.
        c.env["fix.approval.matrix"].search([("name", "=", "A11E rule")]).with_user(c.doa).write(
            {"approver_group_id": c.env.ref("base.group_user").id}
        )
        rec2 = complaint(c)
        rec2.with_user(c.clerk).action_request_approval()
        assert set(assignees(rec2)) == {c.t1, c.t1b}
        assert c.p not in assignees(rec2)


# =========================================================================== E4
class TestE4EngineSemantics:
    def test_m63_12_unanimous_waits_for_every_vote(self, c):
        matrix_row(c.env, user=c.doa, approval_policy="all")
        rec = complaint(c)
        rec.with_user(c.clerk).action_request_approval()
        task_of(rec, c.t1).with_user(c.t1).action_approve()
        assert rec.approval_state == "pending" and not rec.dofa_approved
        assert not rec.concession_approved and not gate_passes(rec)
        task_of(rec, c.t1b).with_user(c.t1b).action_approve()
        assert rec.approval_state == "approved" and rec.dofa_approved and gate_passes(rec)
        assert rec.dofa_approved_by == c.t1b

    def test_m63_12_an_early_vote_still_checks_the_voter(self, c):
        """The dry run applies the record's checks to a vote that does not yet
        complete the request: a voter who lost his tier is refused."""
        matrix_row(c.env, user=c.doa, approval_policy="all")
        rec = complaint(c)
        rec.with_user(c.clerk).action_request_approval()
        c.t1.write({"group_ids": [(3, c.env.ref(T1).id)]})
        with pytest.raises(UserError, match="DOFA authority"):
            task_of(rec, c.t1).with_user(c.t1).action_approve()
        assert task_of(rec, c.t1) and not rec.dofa_approved

    def test_m63_13_reject_after_a_vote_leaves_no_approval(self, c):
        matrix_row(c.env, user=c.doa, approval_policy="all")
        rec = complaint(c)
        rec.with_user(c.clerk).action_request_approval()
        task_of(rec, c.t1).with_user(c.t1).action_approve()
        task_of(rec, c.t1b).with_user(c.t1b).action_reject(comment="I do not agree")
        assert rec.approval_request_id.state == "rejected"
        assert not (rec.dofa_approved or rec.concession_approved) and not gate_passes(rec)

    def test_m63_e4_reject_and_recall_clear_an_existing_stamp(self, c):
        rec = complaint(c)
        rec.with_user(c.clerk).action_request_approval()
        task_of(rec, c.t1).with_user(c.t1).action_approve()
        assert rec.dofa_approved and rec.concession_approved
        rec.with_user(c.clerk).action_request_approval()  # asked again: e.g. new evidence
        task_of(rec, c.t1b).with_user(c.t1b).action_reject(comment="not upheld after all")
        assert not rec.dofa_approved and not rec.concession_approved
        rec2 = complaint(c)
        rec2.with_user(c.clerk).action_request_approval()
        task_of(rec2, c.t1).with_user(c.t1).action_approve()
        rec2.with_user(c.clerk).action_request_approval()
        rec2.with_user(c.clerk).action_recall_approval()
        assert not rec2.dofa_approved and rec2.approval_state == "none"

    def test_m63_14_escalation_never_reaches_the_requester(self, c):
        t2b = _user(c.env, "a11e_t2b", [T2])
        rec = complaint(c)
        rec.with_user(c.t2).action_request_approval()  # a Tier-2 manager requests
        req = rec.approval_request_id
        assert c.t2 not in assignees(rec)
        overdue(req)
        run_cron(c.env)  # reminder
        overdue(req)
        run_cron(c.env)  # escalation to Tier 2, as the superuser
        assert req.escalation_level == 1
        assert not task_of(rec, c.t2), "escalated to its own requester"
        assert task_of(rec, t2b)
        targets = [u for u, _b in req._next_tier_holders(rec.sudo())]
        assert c.t2 not in targets and t2b not in targets  # t2b already assigned
        # Defence in depth: a task that somehow reaches the requester is refused.
        forged = req.sudo()._open_tasks([(c.t2, None)], level=1)
        with pytest.raises(UserError, match="Segregation of duties"):
            forged.with_user(c.t2).action_approve()
        task_of(rec, t2b).with_user(t2b).action_approve()
        assert rec.dofa_approved_by == t2b

    def test_m63_14_delegate_of_the_requester_is_refused(self, c):
        sub = c.env["fix.approval.substitution"].with_user(c.t1).create(sub_vals(c.env, c.t1, c.t2))
        sub.with_user(c.t1).action_activate()
        rec = complaint(c)
        rec.with_user(c.t1).action_request_approval()  # the absent T1 requested it
        assert c.t2 not in assignees(rec)
        forged = rec.approval_request_id.sudo()._open_tasks([(c.t2, c.t1)])
        with pytest.raises(UserError, match="Segregation of duties"):
            forged.with_user(c.t2).action_approve()

    def test_m63_11_payee_and_type_are_pinned(self, c):
        rec = complaint(c)
        rec.with_user(c.clerk).action_request_approval()
        task_of(rec, c.t1).with_user(c.t1).action_approve()
        rec.with_user(c.clerk).write({"description": "customer called back"})
        assert rec.dofa_approved and rec.approval_state == "approved"  # not a term
        rec.with_user(c.clerk).write({"customer_id": c.accomplice.id})
        assert rec.approval_state == "none" and not rec.dofa_approved
        assert not rec.concession_approved and not gate_passes(rec)
        assert rec.approval_amount_changed_by_id == c.clerk
        assert "voided" in rec.approval_request_id.history_ids.mapped("event")

        rec2 = complaint(c)
        rec2.with_user(c.clerk).action_request_approval()
        task_of(rec2, c.t1).with_user(c.t1).action_approve()
        rec2.with_user(c.clerk).write({"concession_type": "discount"})
        assert not rec2.dofa_approved and not rec2.concession_approved

        rec3 = complaint(c)
        rec3.with_user(c.clerk).action_request_approval()
        req3 = rec3.approval_request_id
        rec3.with_user(c.t1b).write({"customer_id": c.accomplice.id})
        assert req3.state == "voided" and rec3.approval_state == "none"
        # Who re-pointed it is not routed the new request.
        rec3.with_user(c.clerk).action_request_approval()
        assert c.t1b not in assignees(rec3) and c.t1 in assignees(rec3)

    def test_m63_11_pinned_fields_declared(self, c):
        pinned = c.env["fix.complaint"]._approval_pinned_fields()
        assert {"customer_id", "concession_type"} <= pinned

    def test_m63_e4_kpi_counts_every_conflicted_decision(self, c):
        Req = c.env["fix.approval.request"].sudo()
        before = Req.approval_kpis()["approver_is_creator"]
        rec = complaint(c)
        base = {
            "res_model": "fix.complaint",
            "res_id": rec.id,
            "state": "approved",
            "record_creator_id": c.clerk.id,
        }
        Req.create(dict(base, requested_by_id=c.t1.id, decided_by_id=c.t1.id))  # requester
        Req.create(
            dict(base, requested_by_id=c.t1.id, decided_by_id=c.t2.id, on_behalf_of_id=c.t1.id)
        )  # delegate of the requester
        Req.create(
            dict(
                base,
                requested_by_id=c.clerk.id,
                decided_by_id=c.t1b.id,
                amount_changed_by_id=c.t1b.id,
            )
        )  # amount-changer
        Req.create(dict(base, requested_by_id=c.clerk.id, decided_by_id=c.clerk.id))  # creator
        Req.create(dict(base, requested_by_id=c.clerk.id, decided_by_id=c.t1.id))  # clean
        assert Req.approval_kpis()["approver_is_creator"] == before + 4
