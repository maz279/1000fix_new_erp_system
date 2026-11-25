# What running the five modules as real users on a copy of live data found, after every
# module's own suite was green. Each test fails on the code those journeys ran against.
from __future__ import annotations

import itertools
import types

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.exceptions import UserError

_SEQ = itertools.count(1)


def _user(env, *groups):
    n = next(_SEQ)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A07 Journey %s" % n,
                "login": "a07-journey-%s" % n,
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
            }
        )
    )


@pytest.fixture
def ui(odoo_env):
    ctl = api.P03GenericApiController()
    cls = api.P03GenericApiController
    old = getattr(api, "request", None)

    def call(name, user, **kw):
        api.request = types.SimpleNamespace(env=odoo_env(user=user.id))
        fn = getattr(cls, name)
        return getattr(fn, "original_endpoint", fn)(ctl, **kw)

    try:
        yield types.SimpleNamespace(
            records=lambda user, **kw: call("model_records", user, **kw),
            action=lambda user, **kw: call("model_action", user, **kw),
        )
    finally:
        api.request = old


def _site(env):
    site = env["fix.site"].create({"name": "A07 Journey %s" % next(_SEQ)})
    site.sudo().write({"state": "active"})
    return site


def _work_order(env, user, **vals):
    return (
        env["fix.facility.work.order"]
        .with_user(user)
        .create(
            {"site_id": _site(env).id, "work_type": "repair", "description": "A07 fault", **vals}
        )
    )


# ------------------------------------------------------------ the approval inbox
INBOX = [["is_mine", "=", True], ["state", "=", "pending"]]


def _routed_task(env):
    """A real request routed to one approver, as the inbox would show it."""
    approver = _user(env, "cd_entity_config.group_dofa_tier_5")
    requester = _user(env, "cd_facility.group_facility_manager")
    # the other holders of the tier must not catch this request
    env.ref("cd_entity_config.group_dofa_tier_5").sudo().write({"user_ids": [(6, 0, approver.ids)]})
    order = _work_order(env, requester, estimated_cost=50000000.0)
    order.with_user(requester).action_triage(priority="normal")
    order.with_user(requester).action_request_approval(justification="A07 inbox")
    task = (
        env["fix.workflow.task"]
        .sudo()
        .search(
            [
                ("res_model", "=", order._name),
                ("res_id", "=", order.id),
                ("state", "=", "pending"),
                ("assigned_user_id", "=", approver.id),
            ]
        )
    )
    assert task, "the request reached no one"
    return approver, task


def test_my_inbox_lists_my_task(odoo_env, ui):
    approver, task = _routed_task(odoo_env)
    out = ui.records(approver, model="fix.workflow.task", cols=["state"], domain=INBOX)
    assert task.id in [row["id"] for row in out["rows"]]


def test_someone_elses_inbox_does_not_list_it(odoo_env, ui):
    _approver, task = _routed_task(odoo_env)
    stranger = _user(odoo_env)
    out = ui.records(stranger, model="fix.workflow.task", cols=["state"], domain=INBOX)
    assert task.id not in [row["id"] for row in out.get("rows") or []]


def test_every_form_of_the_filter_means_what_it_says(odoo_env):
    me = _user(odoo_env)
    Task = odoo_env["fix.workflow.task"].with_user(me)
    for operator, value in (("in", [True]), ("=", True), ("!=", False), ("not in", [False])):
        assert Task._search_is_mine(operator, value)[0] == "|", (operator, value)
    for operator, value in (("in", [False]), ("=", False), ("!=", True), ("not in", [True])):
        assert Task._search_is_mine(operator, value)[0] == "!", (operator, value)


# ------------------------------------------------------------ facility work order roles
def test_anyone_may_report_a_fault_but_not_run_the_job(odoo_env, ui):
    env = odoo_env
    plain = _user(env)
    manager = _user(env, "cd_facility.group_facility_manager")
    order = _work_order(env, plain)
    order.with_user(manager).action_triage(priority="normal")
    kw = {"model": order._name, "ids": order.ids}
    out = ui.action(plain, method="action_schedule", **kw)
    assert out["success"] is False and "Facility Manager" in out["error"]
    assert ui.action(manager, method="action_schedule", **kw)["success"]
    out = ui.action(plain, method="action_start", **kw)
    assert out["success"] is False and "assigned engineer" in out["error"]
    assert ui.action(manager, method="action_start", **kw)["success"]
    out = ui.action(plain, method="action_complete", kwargs={"notes": "x"}, **kw)
    assert out["success"] is False and "assigned engineer" in out["error"]
    assert order.state == "in_progress"


def test_a_plain_user_cannot_type_the_actual_cost(odoo_env):
    plain = _user(odoo_env)
    order = _work_order(odoo_env, plain)
    with pytest.raises(UserError, match="actual cost"), odoo_env.cr.savepoint():
        order.with_user(plain).write({"actual_cost": 1800000.0})
    assert not order.actual_cost


def test_the_assigned_engineer_may_do_the_work(odoo_env):
    env = odoo_env
    engineer = _user(env)
    manager = _user(env, "cd_facility.group_facility_manager")
    employee = env["hr.employee"].create({"name": "A07 Engineer", "user_id": engineer.id})
    order = _work_order(env, manager)
    order.with_user(manager).write({"assigned_to": employee.id})
    order.with_user(manager).action_triage(priority="normal")
    order.with_user(manager).action_schedule()
    order.with_user(engineer).action_start()
    order.with_user(engineer).write({"actual_cost": 100.0})
    assert order.state == "in_progress" and order.actual_cost == 100.0


# ------------------------------------------------------------ M60 consumer
def test_the_risk_register_takes_the_payload_m67_really_sends(odoo_env):
    entry = odoo_env["fix.risk.register"].consume_project_risk_escalated(
        {
            "event_id": "a07-e1",
            "payload": {"title": "A07 slip", "project": "Depot refit"},
            "company_id": odoo_env.company.id,
        }
    )
    assert entry and "Depot refit" in entry.name
