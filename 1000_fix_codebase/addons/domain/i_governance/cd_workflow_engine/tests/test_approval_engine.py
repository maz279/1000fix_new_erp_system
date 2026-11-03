"""test_approval_engine.py — M63 as the single approval workflow (A03 audit R7).

Drives the engine on real A03 records (a complaint concession and an estimate
discount request) as NON-ADMIN users, because the superuser is trusted by the
guards and would hide a gap. Each control is checked both ways: the bypass is
refused and the routed path works.
"""

from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
T2 = "cd_entity_config.group_dofa_tier_2"
T3 = "cd_entity_config.group_dofa_tier_3"


@pytest.fixture
def env(odoo_env):
    if "fix.complaint" not in odoo_env:
        pytest.skip("cd_cx_feedback is not installed")
    return odoo_env


@pytest.fixture
def make_user(env):
    counter = {"n": 0}

    def _make(*xmlids, employee=False):
        counter["n"] += 1
        groups = [env.ref("base.group_user").id] + [env.ref(x).id for x in xmlids]
        user = (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Engine Probe %d" % counter["n"],
                    "login": "engine.probe.%d@m63.test" % counter["n"],
                    "group_ids": [(6, 0, groups)],
                }
            )
        )
        if employee:
            env["hr.employee"].create({"name": user.name, "user_id": user.id})
        return user

    return _make


@pytest.fixture
def ou(env):
    return env["operating.unit"].search([], limit=1)


@pytest.fixture
def complaint(env, make_user, ou):
    """A BDT 3,000 refund concession (Tier 2) raised by a plain user."""

    def _make(raiser=None, amount=3000.0):
        raiser = raiser or make_user()
        return (
            env["fix.complaint"]
            .with_user(raiser)
            .create(
                {
                    "name": "ENG-%s" % raiser.login,
                    "customer_id": env["res.partner"].create({"name": "Engine Customer"}).id,
                    "operating_unit_id": ou.id,
                    "description": "engine probe",
                    "severity": "minor",
                    "concession_amount": amount,
                    "concession_type": "refund",
                    "dofa_justification": "Repeat failure on the same repair.",
                }
            )
        )

    return _make


def _task_of(record, user):
    return record.approval_request_id.task_ids.filtered(
        lambda t: t.assigned_user_id == user and t.state == "pending"
    )


def _events(record):
    return record.approval_request_id.history_ids.sorted("id").mapped("event")


class TestRequestAndDecide:
    def test_a_request_goes_only_to_holders_of_the_tier(self, env, make_user, complaint):
        raiser, approver = make_user(), make_user(T2)
        c = complaint(raiser)
        c.with_user(raiser).action_request_approval()
        req = c.approval_request_id
        assert c.approval_state == "pending" and req.state == "pending"
        assert req.tier == "tier_2" and req.amount == 3000.0
        assignees = req.task_ids.mapped("assigned_user_id")
        assert approver in assignees and raiser not in assignees
        assert all(u.has_group(T2) for u in assignees)
        assert _task_of(c, approver).activity_id, "the approver gets a to-do"
        assert env["fix.event.outbox"].search_count(
            [("event_type", "=", "approval.requested"), ("aggregate_id", "=", c.id)]
        )

    def test_pressing_approve_directly_is_refused(self, env, make_user, complaint):
        approver = make_user(T2)
        c = complaint().with_user(approver)
        with pytest.raises(UserError, match="approver's inbox"):
            c.action_approve_concession()
        assert not c.dofa_approved

    def test_the_approver_decides_from_the_inbox(self, env, make_user, complaint):
        raiser, approver = make_user(), make_user(T2)
        c = complaint(raiser)
        c.with_user(raiser).action_request_approval()
        _task_of(c, approver).with_user(approver).action_approve(comment="ok")
        assert c.approval_state == "approved" and c.approval_request_id.state == "approved"
        assert c.dofa_approved and c.concession_approved and c.dofa_approved_by == approver
        assert _events(c) == ["requested", "task_approved", "approved"]
        assert c.approval_request_id.cycle_hours >= 0.0
        others = c.approval_request_id.task_ids.filtered(lambda t: t.assigned_user_id != approver)
        assert all(t.state == "cancelled" for t in others)

    def test_only_the_assignee_decides_a_task(self, env, make_user, complaint):
        raiser, approver, other = make_user(), make_user(T2), make_user(T2)
        c = complaint(raiser)
        c.with_user(raiser).action_request_approval()
        with pytest.raises(UserError, match="Only the assignee"):
            _task_of(c, approver).with_user(other).action_approve()
        with pytest.raises(UserError, match="Only the assignee"):
            _task_of(c, approver).with_user(raiser).action_approve()

    def test_one_task_cannot_carry_a_second_record_through(self, env, make_user, complaint):
        raiser, approver = make_user(), make_user(T2)
        c1, c2 = complaint(raiser), complaint(raiser)
        c1.with_user(raiser).action_request_approval()
        task = _task_of(c1, approver)
        both = (c1 | c2).with_user(approver).with_context(fix_approval_task=task)
        with pytest.raises(UserError, match="approver's inbox"):
            both.action_approve_concession()
        assert not c2.dofa_approved

    def test_inbox_tasks_cannot_be_forged(self, env, make_user, complaint):
        raiser, approver = make_user(), make_user(T2)
        c = complaint(raiser)
        c.with_user(raiser).action_request_approval()
        task = _task_of(c, approver)
        with pytest.raises(REFUSED):
            task.with_user(raiser).write({"assigned_user_id": raiser.id})
        with pytest.raises(REFUSED):
            task.with_user(approver).write({"state": "done", "decision": "approved"})
        with pytest.raises(REFUSED):
            env["fix.workflow.task"].with_user(raiser).create(
                {"request_id": c.approval_request_id.id, "assigned_user_id": raiser.id}
            )
        with pytest.raises(REFUSED):
            c.approval_request_id.with_user(raiser).write({"state": "approved"})
        with pytest.raises(REFUSED):
            c.with_user(raiser).write({"approval_state": "approved"})

    def test_history_is_append_only(self, env, make_user, complaint):
        raiser = make_user()
        make_user(T2)
        c = complaint(raiser)
        c.with_user(raiser).action_request_approval()
        row = c.approval_request_id.history_ids[:1]
        with pytest.raises(UserError):
            row.sudo().write({"comment": "rewritten"})
        with pytest.raises(UserError):
            row.sudo().unlink()

    def test_no_holder_means_a_clear_refusal(self, env, make_user, complaint):
        raiser = make_user()
        c = complaint(raiser, amount=900000.0)  # Tier 5: nobody holds it here
        if env.ref("cd_entity_config.group_dofa_tier_5").all_user_ids - raiser:
            pytest.skip("this database has Tier 5 holders")
        with pytest.raises(UserError, match="Appoint an approver"):
            c.with_user(raiser).action_request_approval()
        assert c.approval_state == "none"


class TestRejectReturnRecallVoid:
    def test_a_rejection_needs_its_reason(self, env, make_user, complaint):
        raiser, approver = make_user(), make_user(T2)
        c = complaint(raiser)
        c.with_user(raiser).action_request_approval()
        with pytest.raises(UserError, match="State why"):
            _task_of(c, approver).with_user(approver).action_reject()
        _task_of(c, approver).with_user(approver).action_reject(comment="no evidence")
        assert c.approval_state == "rejected" and not c.dofa_approved
        c.with_user(raiser).action_request_approval()  # may ask again
        assert c.approval_state == "pending"

    def test_return_for_information(self, env, make_user, complaint):
        raiser, approver = make_user(), make_user(T2)
        c = complaint(raiser)
        c.with_user(raiser).action_request_approval()
        _task_of(c, approver).with_user(approver).action_return(comment="attach the job card")
        assert c.approval_state == "returned"
        assert c.approval_request_id.state == "returned"

    def test_only_the_requester_recalls(self, env, make_user, complaint):
        raiser, approver = make_user(), make_user(T2)
        c = complaint(raiser)
        c.with_user(raiser).action_request_approval()
        with pytest.raises(UserError, match="Only the person who requested"):
            c.with_user(approver).action_recall_approval()
        c.with_user(raiser).action_recall_approval()
        assert c.approval_state == "none" and c.approval_request_id.state == "recalled"

    def test_changing_the_amount_while_pending_voids_the_request(self, env, make_user, complaint):
        raiser, approver = make_user(), make_user(T2)
        c = complaint(raiser)
        c.with_user(raiser).action_request_approval()
        req = c.approval_request_id
        c.with_user(raiser).write({"concession_amount": 4500.0})
        assert req.state == "voided" and c.approval_state == "none"
        assert not _task_of(c, approver)

    def test_raising_an_approved_amount_voids_the_approval(self, env, make_user, complaint):
        raiser, approver = make_user(), make_user(T2)
        c = complaint(raiser)
        c.with_user(raiser).action_request_approval()
        _task_of(c, approver).with_user(approver).action_approve()
        c.with_user(raiser).write({"concession_amount": 4500.0})
        assert c.approval_state == "none" and not c.dofa_approved
        assert "voided" in _events(c)


class TestDelegationAndEscalation:
    def test_an_absent_approvers_delegate_decides_on_their_behalf(self, env, make_user, complaint):
        raiser = make_user()
        absent = make_user(T2, employee=True)
        delegate = make_user(employee=True)  # holds no tier of their own
        env["fix.approval.substitution"].create(
            {
                "absent_approver_id": absent.employee_ids[0].id,
                "delegate_id": delegate.employee_ids[0].id,
                "start_date": fields.Date.today() - timedelta(days=1),
                "end_date": fields.Date.today() + timedelta(days=5),
                "state": "active",
            }
        )
        c = complaint(raiser)
        c.with_user(raiser).action_request_approval()
        assert not _task_of(c, absent)
        task = _task_of(c, delegate)
        assert task.on_behalf_of_id == absent
        task.with_user(delegate).action_approve()
        assert c.dofa_approved and c.approval_request_id.on_behalf_of_id == absent
        approved = c.approval_request_id.history_ids.filtered(lambda h: h.event == "approved")
        assert approved.user_id == delegate and approved.on_behalf_of_id == absent

    def test_a_delegate_cannot_approve_what_they_raised(self, env, make_user, complaint):
        absent = make_user(T2, employee=True)
        delegate = make_user(employee=True)
        env["fix.approval.substitution"].create(
            {
                "absent_approver_id": absent.employee_ids[0].id,
                "delegate_id": delegate.employee_ids[0].id,
                "start_date": fields.Date.today(),
                "end_date": fields.Date.today(),
                "state": "active",
            }
        )
        c = complaint(delegate)
        c.with_user(delegate).action_request_approval()
        # The delegate raised it, so the absent approver keeps the task.
        assert _task_of(c, absent) and not _task_of(c, delegate)

    def test_overdue_reminds_then_escalates_then_applies_the_final_action(
        self, env, make_user, complaint
    ):
        env["fix.approval.matrix"].create(
            {
                "decision_domain": "concession",
                "res_model": "fix.complaint",
                "name": "Concession: auto-reject after one escalation",
                "approval_policy": "any",
                "sla_hours": 4,
                "max_escalations": 1,
                "final_action": "reject",
                "date_from": fields.Date.today(),
            }
        )
        raiser, _approver, director = make_user(), make_user(T2), make_user(T3)
        c = complaint(raiser)
        c.with_user(raiser).action_request_approval()
        req = c.approval_request_id
        Request = env["fix.approval.request"]

        def expire():
            req.task_ids.filtered(lambda t: t.state == "pending")._guarded().write(
                {"due_at": fields.Datetime.now() - timedelta(hours=1)}
            )

        expire()
        Request.cron_escalate_overdue()
        assert req.reminded_at and "reminded" in _events(c)
        expire()
        Request.cron_escalate_overdue()
        assert req.escalation_level == 1 and _task_of(c, director)
        assert "escalated" in _events(c)
        expire()
        Request.cron_escalate_overdue()
        assert req.state == "rejected" and c.approval_state == "rejected"
        assert "expired" in _events(c)


class TestRulesAndSimulation:
    def test_a_unanimous_rule_waits_for_every_approver(self, env, make_user, complaint):
        env["fix.approval.matrix"].create(
            {
                "decision_domain": "concession",
                "res_model": "fix.complaint",
                "name": "Concession: four eyes",
                "approval_policy": "all",
                "date_from": fields.Date.today(),
            }
        )
        raiser, a1, _a2 = make_user(), make_user(T2), make_user(T2)
        c = complaint(raiser)
        c.with_user(raiser).action_request_approval()
        holders = c.approval_request_id.task_ids
        _task_of(c, a1).with_user(a1).action_approve()
        if len(holders) > 1:
            assert c.approval_state == "pending"
        for task in c.approval_request_id.task_ids.filtered(lambda t: t.state == "pending"):
            task.with_user(task.assigned_user_id).action_approve()
        assert c.approval_state == "approved"

    def test_a_condition_selects_the_rule(self, env, make_user, complaint):
        rule = env["fix.approval.matrix"].create(
            {
                "decision_domain": "concession",
                "res_model": "fix.complaint",
                "name": "Large refunds",
                "condition": "[('concession_amount', '>', 4000)]",
                "approval_policy": "all",
                "date_from": fields.Date.today(),
            }
        )
        small, large = complaint(amount=3000.0), complaint(amount=4500.0)
        assert not env["fix.approval.matrix"]._match(small)
        assert env["fix.approval.matrix"]._match(large) == rule

    def test_simulation_creates_nothing(self, env, make_user, complaint):
        approver = make_user(T2)
        c = complaint()
        before = env["fix.approval.request"].search_count([])
        sim = c.approval_simulate()
        assert sim["tier"] == "tier_2" and approver.name in sim["approvers"]
        assert env["fix.approval.request"].search_count([]) == before
        assert c.approval_state == "none"

    def test_kpis_count_what_happened(self, env, make_user, complaint):
        raiser, approver = make_user(), make_user(T2)
        c = complaint(raiser)
        c.with_user(raiser).action_request_approval()
        _task_of(c, approver).with_user(approver).action_approve()
        kpis = env["fix.approval.request"].approval_kpis()
        assert kpis["approver_is_creator"] == 0
        assert kpis["approved_by_tier"].get("tier_2", 0) >= 1


def _estimate(env):
    """A bare estimate on a walk-in order, for a discount request to sit on."""
    branch = env["fix.branch"].search([], limit=1)
    if not branch:
        unit = env["operating.unit"].search([], limit=1)
        entity = env["fix.entity"].search([], limit=1) or env["fix.entity"].create(
            {
                "legal_name": "1000FiX Engine Probe Ltd",
                "code": "ENGENT",
                "company_id": env.company.id,
                "operating_unit_id": unit.id,
            }
        )
        branch = env["fix.branch"].create(
            {
                "name": "Engine Branch",
                "code": "ENG-BR",
                "entity_id": entity.id,
                "operating_unit_id": unit.id,
            }
        )
    customer = env["res.partner"].create({"name": "Discount Customer"})
    brand = env["fix.brand"].create({"name": "ENG Brand", "code": "ENGBR"})
    model = env["fix.device.model"].create({"name": "ENG Model", "brand_id": brand.id})
    device = env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": customer.id, "serial_number": "SN-ENG-1"}
    )
    order = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "service_type": "walk_in",
            "order_category": "standard",
            "fault_description": "engine probe",
        }
    )
    return env["fix.estimate"].create({"order_id": order.id})


class TestDiscountRouting:
    @pytest.fixture
    def discount(self, env, make_user):
        if "fix.discount.approval" not in env:
            pytest.skip("cd_quotation is not installed")
        estimate = env["fix.estimate"].search([], limit=1) or _estimate(env)

        def _make(seller, pct):
            return (
                env["fix.discount.approval"]
                .with_user(seller)
                .create(
                    {
                        "operating_unit_id": estimate.operating_unit_id.id
                        or env["operating.unit"].search([], limit=1).id,
                        "quotation_id": estimate.id,
                        "discount_pct": pct,
                        "justification": "Competitor match",
                    }
                )
            )

        return _make

    def test_a_discount_is_approved_from_the_inbox(self, env, make_user, discount):
        seller, manager = make_user(), make_user(T2)
        req = discount(seller, 8.0)
        with pytest.raises(UserError, match="approver's inbox"):
            req.with_user(manager).action_approve()
        req.with_user(seller).action_request_approval()
        _task_of(req, manager).with_user(manager).action_approve()
        assert req.state == "approved" and req.approved_by == manager

    def test_a_rejected_discount_records_the_reason(self, env, make_user, discount):
        seller, director = make_user(), make_user(T3)
        req = discount(seller, 20.0)
        req.with_user(seller).action_request_approval()
        assert all(t.assigned_user_id.has_group(T3) for t in req.approval_request_id.task_ids)
        _task_of(req, director).with_user(director).action_reject(comment="margin too thin")
        assert req.state == "rejected" and req.rejection_reason == "margin too thin"

    def test_an_agent_discount_needs_no_request(self, env, make_user, discount):
        req = discount(make_user(), 4.0)
        assert req.state == "approved"
        with pytest.raises(UserError, match="Nothing to approve"):
            req.action_request_approval()
