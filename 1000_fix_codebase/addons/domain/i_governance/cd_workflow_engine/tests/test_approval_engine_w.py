"""test_approval_engine_w.py — the last R7 items of the A03 audit.

W2: approval SLAs count WORKING hours on fix.working.calendar (Dhaka local
time, holidays closed), chosen rule -> branch -> company default -> wall clock.
W3: whoever last changed the amount at risk is never routed the approval,
neither as an approver nor as a delegate.

Records are driven as NON-ADMIN users: the superuser is trusted by the guards
and would hide a gap.
"""

from datetime import datetime, timedelta

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

from .test_approval_engine import _estimate

REFUSED = (UserError, ValidationError, AccessError)
T2 = "cd_entity_config.group_dofa_tier_2"
T3 = "cd_entity_config.group_dofa_tier_3"
PARAM = "cd_workflow_engine.approval_calendar_id"

# November 2026: Thu 5, Fri 6 and Sat 7 (the Bangladesh weekend), Sun 8.
# Dhaka is UTC+6, so 09:00-17:00 Dhaka is 03:00-11:00 UTC.
THU_16_DHAKA = datetime(2026, 11, 5, 10, 0)


@pytest.fixture
def env(odoo_env):
    if "fix.complaint" not in odoo_env:
        pytest.skip("cd_cx_feedback is not installed")
    # A company default on this database would change every expectation.
    odoo_env["ir.config_parameter"].sudo().set_param(PARAM, False)
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
                    "name": "W Probe %d" % counter["n"],
                    "login": "w.probe.%d@m63.test" % counter["n"],
                    "group_ids": [(6, 0, groups)],
                }
            )
        )
        if employee:
            env["hr.employee"].create({"name": user.name, "user_id": user.id})
        return user

    return _make


@pytest.fixture
def complaint(env, make_user):
    """A BDT 3,000 refund concession (Tier 2) raised by a plain user."""
    ou = env["operating.unit"].search([], limit=1)

    def _make(raiser=None, amount=3000.0):
        raiser = raiser or make_user()
        return (
            env["fix.complaint"]
            .with_user(raiser)
            .create(
                {
                    "name": "W-%s" % raiser.login,
                    "customer_id": env["res.partner"].create({"name": "W Customer"}).id,
                    "operating_unit_id": ou.id,
                    "description": "W probe",
                    "severity": "minor",
                    "concession_amount": amount,
                    "concession_type": "refund",
                    "dofa_justification": "Repeat failure on the same repair.",
                }
            )
        )

    return _make


@pytest.fixture
def calendar(env):
    """Sunday-Thursday 09:00-17:00 Dhaka, optionally with holidays."""

    def _make(name="W Calendar", holidays=(), days=("sun", "mon", "tue", "wed", "thu")):
        return env["fix.working.calendar"].create(
            {
                "name": name,
                "line_ids": [
                    (0, 0, {"weekday": d, "hour_from": 9.0, "hour_to": 17.0}) for d in days
                ],
                "holiday_ids": [
                    (0, 0, {"name": "Closed", "date_from": d_from, "date_to": d_to})
                    for d_from, d_to in holidays
                ],
            }
        )

    return _make


@pytest.fixture
def clock(monkeypatch):
    """Pin the engine's clock; returns a setter. Unset, it is the real clock."""
    real_now = fields.Datetime.now
    state = {"now": None}
    monkeypatch.setattr(
        fields.Datetime, "now", staticmethod(lambda *a, **k: state["now"] or real_now())
    )

    def _set(value):
        state["now"] = value

    return _set


def _add(env, start, hours, cal):
    return env["fix.approval.request"]._approval_add_business_hours(start, hours, cal)


def _task_of(record, user):
    return record.approval_request_id.task_ids.filtered(
        lambda t: t.assigned_user_id == user and t.state == "pending"
    )


class TestBusinessHours:
    def test_a_deadline_skips_the_weekend(self, env, calendar):
        # Thu 16:00 Dhaka + 4h: one hour on Thursday, none on Fri/Sat, three
        # on Sunday -> Sun 12:00 Dhaka. Wall clock would say Thu 20:00.
        assert _add(env, THU_16_DHAKA, 4, calendar()) == datetime(2026, 11, 8, 6, 0)

    def test_a_deadline_skips_a_holiday(self, env, calendar):
        sunday = datetime(2026, 11, 8).date()
        cal = calendar(holidays=[(sunday, sunday)])
        assert _add(env, THU_16_DHAKA, 4, cal) == datetime(2026, 11, 9, 6, 0)

    def test_a_deadline_carries_over_the_end_of_the_working_day(self, env, calendar):
        cal = calendar()
        # Tue 15:00 Dhaka + 4h: two hours Tuesday, two Wednesday -> Wed 11:00.
        assert _add(env, datetime(2026, 11, 3, 9, 0), 4, cal) == datetime(2026, 11, 4, 5, 0)
        # Before opening: Tue 07:00 Dhaka + 2h -> Tue 11:00 Dhaka.
        assert _add(env, datetime(2026, 11, 3, 1, 0), 2, cal) == datetime(2026, 11, 3, 5, 0)
        # Tue 20:00 UTC is already Wed 02:00 in Dhaka: + 1h -> Wed 10:00 Dhaka.
        assert _add(env, datetime(2026, 11, 3, 20, 0), 1, cal) == datetime(2026, 11, 4, 4, 0)
        # Exactly a working day lands on closing time.
        assert _add(env, datetime(2026, 11, 3, 3, 0), 8, cal) == datetime(2026, 11, 3, 11, 0)

    def test_a_calendar_inherits_its_templates_hours(self, env, calendar):
        template = calendar("W National")
        branch = env["fix.working.calendar"].create(
            {"name": "W Branch", "template_id": template.id}
        )
        assert _add(env, THU_16_DHAKA, 4, branch) == datetime(2026, 11, 8, 6, 0)

    def test_no_calendar_or_no_lines_is_wall_clock(self, env):
        Calendar = env["fix.working.calendar"]
        assert _add(env, THU_16_DHAKA, 4, Calendar) == THU_16_DHAKA + timedelta(hours=4)
        assert _add(env, THU_16_DHAKA, 4, None) == THU_16_DHAKA + timedelta(hours=4)
        empty = Calendar.create({"name": "W No Hours"})
        assert _add(env, THU_16_DHAKA, 4, empty) == THU_16_DHAKA + timedelta(hours=4)

    def test_a_calendar_with_no_working_time_does_not_hang(self, env, calendar):
        closed = calendar(holidays=[(datetime(2026, 1, 1).date(), datetime(2030, 12, 31).date())])
        assert _add(env, THU_16_DHAKA, 4, closed) == THU_16_DHAKA + timedelta(hours=4)


class TestCalendarChoice:
    def test_rule_then_branch_then_company_default_then_none(self, env, calendar):
        Request = env["fix.approval.request"].sudo()
        if "fix.service.order" not in env:
            pytest.skip("cd_service_order is not installed")
        order = (
            env["fix.service.order"].search([("branch_id", "!=", False)], limit=1)
            or _estimate(env).order_id
        )
        rule_cal, branch_cal, default_cal = calendar("W Rule"), calendar("W Br"), calendar("W Co")
        rule = env["fix.approval.matrix"].create(
            {
                "decision_domain": "other",
                "res_model": "fix.service.order",
                "name": "W calendar rule",
                "calendar_id": rule_cal.id,
                "date_from": fields.Date.today(),
            }
        )
        req = Request.create(
            {
                "res_model": order._name,
                "res_id": order.id,
                "requested_by_id": env.uid,
                "matrix_id": rule.id,
            }
        )
        order.branch_id.sudo().calendar_id = branch_cal
        env["ir.config_parameter"].sudo().set_param(PARAM, str(default_cal.id))
        assert req._approval_calendar() == rule_cal
        rule.calendar_id = False
        assert req._approval_calendar() == branch_cal
        order.branch_id.sudo().calendar_id = False
        assert req._approval_calendar() == default_cal
        env["ir.config_parameter"].sudo().set_param(PARAM, "not-an-id")
        assert not req._approval_calendar()
        env["ir.config_parameter"].sudo().set_param(PARAM, False)
        assert not req._approval_calendar()

    def test_a_request_without_a_calendar_keeps_wall_clock(self, env, make_user, complaint):
        raiser, approver = make_user(), make_user(T2)
        c = complaint(raiser)
        c.with_user(raiser).action_request_approval()
        task = _task_of(c, approver)
        req = c.approval_request_id
        assert not req._approval_calendar()
        assert abs((task.due_at - req.requested_at).total_seconds() - 24 * 3600) < 120


class TestEscalationOnBusinessHours:
    def test_due_dates_reminder_and_escalation_count_working_hours(
        self, env, make_user, complaint, calendar, clock
    ):
        cal = calendar()
        env["fix.approval.matrix"].create(
            {
                "decision_domain": "concession",
                "res_model": "fix.complaint",
                "name": "Concession: 4 working hours",
                "sla_hours": 4,
                "max_escalations": 1,
                "final_action": "reject",
                "calendar_id": cal.id,
                "date_from": fields.Date.today(),
            }
        )
        raiser, approver, director = make_user(), make_user(T2), make_user(T3)
        c = complaint(raiser)
        Request = env["fix.approval.request"]

        clock(THU_16_DHAKA)
        c.with_user(raiser).action_request_approval()
        req = c.approval_request_id
        # Requested Thursday 16:00 Dhaka: due Sunday 12:00, not Thursday 20:00.
        assert _task_of(c, approver).due_at == datetime(2026, 11, 8, 6, 0)

        clock(datetime(2026, 11, 8, 7, 0))  # Sun 13:00 Dhaka: overdue
        Request.cron_escalate_overdue()
        assert req.reminded_at and req.escalation_level == 0
        assert _task_of(c, approver).due_at == datetime(2026, 11, 8, 11, 0)  # Sun 17:00

        clock(datetime(2026, 11, 8, 10, 0))  # Sun 16:00 Dhaka: still in time
        Request.cron_escalate_overdue()
        assert req.escalation_level == 0 and not _task_of(c, director)

        clock(datetime(2026, 11, 8, 11, 30))  # Sun 17:30 Dhaka, after closing
        Request.cron_escalate_overdue()
        assert req.escalation_level == 1
        # Counted from Monday's opening: Mon 13:00 Dhaka.
        monday_13 = datetime(2026, 11, 9, 7, 0)
        assert _task_of(c, director).due_at == monday_13
        assert _task_of(c, approver).due_at == monday_13


class TestAmountChangerExcluded:
    def test_who_changes_the_amount_is_recorded_and_guarded(self, env, make_user, complaint):
        raiser, editor, other = make_user(), make_user(T2), make_user()
        c = complaint(raiser)
        assert not c.approval_amount_changed_by_id
        c.with_user(editor).write({"concession_amount": 4000.0})
        assert c.approval_amount_changed_by_id == editor
        c.with_user(other).write({"description": "no amount change"})
        assert c.approval_amount_changed_by_id == editor
        c.sudo().write({"concession_amount": 3500.0})  # trusted system code
        assert c.approval_amount_changed_by_id == editor
        c.with_user(other).write({"concession_amount": 3000.0})  # a decrease counts too
        assert c.approval_amount_changed_by_id == other
        with pytest.raises(REFUSED):
            c.with_user(raiser).write({"approval_amount_changed_by_id": raiser.id})
        with pytest.raises(REFUSED):
            c.with_user(other).write({"approval_amount_changed_by_id": False})
        assert c.approval_amount_changed_by_id == other

    def test_a_user_who_raised_the_amount_is_not_routed_to(self, env, make_user, complaint):
        raiser, editor, approver = make_user(), make_user(T2), make_user(T2)
        c = complaint(raiser)
        c.with_user(editor).write({"concession_amount": 4000.0})
        assert editor.name not in c.approval_simulate()["approvers"]
        c.with_user(raiser).action_request_approval()
        assigned = c.approval_request_id.task_ids.mapped("assigned_user_id")
        assert approver in assigned and editor not in assigned

    def test_a_delegate_who_changed_the_amount_is_not_routed_to(self, env, make_user, complaint):
        raiser = make_user()
        absent = make_user(T2, employee=True)
        delegate = make_user(employee=True)
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
        c.with_user(delegate).write({"concession_amount": 4200.0})
        c.with_user(raiser).action_request_approval()
        # The delegate set the figure, so the absent approver keeps the task.
        assert _task_of(c, absent) and not _task_of(c, delegate)

    def test_an_escalation_skips_the_amount_changer(self, env, make_user, complaint):
        raiser, _approver, director = make_user(), make_user(T2), make_user(T3)
        c = complaint(raiser)
        c.with_user(director).write({"concession_amount": 4100.0})
        c.with_user(raiser).action_request_approval()
        targets = c.approval_request_id._next_tier_holders(c.sudo())
        assert director not in [u for u, _b in targets]

    def test_a_pending_request_is_still_voided_by_an_amount_change(self, env, make_user, complaint):
        raiser, editor = make_user(), make_user(T2)
        make_user(T2)
        c = complaint(raiser)
        c.with_user(raiser).action_request_approval()
        req = c.approval_request_id
        c.with_user(editor).write({"concession_amount": 4500.0})
        assert req.state == "voided" and c.approval_state == "none"
        assert c.approval_amount_changed_by_id == editor
