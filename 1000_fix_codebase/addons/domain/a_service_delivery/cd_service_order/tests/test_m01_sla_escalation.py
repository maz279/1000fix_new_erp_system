"""M01 capture audit (2026-11-17): the SLA escalation matrix (FR-SRM-049).

Before: the "Escalation Rules" page listed SLA policies; no escalation rule
existed, so the page could capture nothing and an SLA clock escalated only
once, at breach, to the branch's Service Supervisors, with nothing to
acknowledge. Now a rule escalates a clock to a role at a share of its target
(50/75/90/100), once per clock series, and the escalation stays open until a
notified person acknowledges it.

``odoo_env``: superuser environment on fix_test, rolled back after every test.
"""

import itertools
from datetime import timedelta
from types import SimpleNamespace

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

SUPERVISOR = "cd_service_order.group_so_supervisor"
QC = "cd_service_order.group_so_qc_inspector"
_SEQ = itertools.count(1)


def _user(env, login, groups=()):
    n = next(_SEQ)
    ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "%s %d" % (login, n),
                "login": "m01esc.%s.%d@m01.test" % (login, n),
                "group_ids": [(6, 0, ids)],
            }
        )
    )


@pytest.fixture
def w(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].create(
        {"code": "M01ESC", "legal_name": "M01 Escalation Entity", "company_id": env.company.id}
    )
    branch = env["fix.branch"].create(
        {
            "name": "M01 Esc Branch",
            "code": "M01EB",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    brand = env["fix.brand"].create({"name": "M01EscBrand", "code": "M01EBR"})
    model = env["fix.device.model"].create({"name": "EscPhone", "brand_id": brand.id})
    customer = env["res.partner"].create({"name": "M01 Esc Customer", "phone": "01711999555"})
    device = env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": customer.id, "serial_number": "SN-M01ESC-1"}
    )
    policy = env["fix.sla.policy"].create(
        {
            "code": "M01ESC",
            "name": "Escalation test policy",
            "service_type": "walk_in",
            "priority": "normal",
            "response_hours": 2,
            "resolution_hours": 10,
        }
    )
    order = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "fault_description": "Screen flickers",
        }
    )
    sup = _user(env, "sup", [SUPERVISOR])
    inspector = _user(env, "qc", [QC])
    clerk = _user(env, "clerk")
    Inst = env["fix.sla.kpi.instance"]
    # a 10-hour resolution clock that started 6 hours ago, around the clock
    started = fields.Datetime.now() - timedelta(hours=6)
    clock = Inst.start_for(order, policy, "resolution", started_at=started)
    return SimpleNamespace(
        env=env, order=order, policy=policy, clock=clock, sup=sup, inspector=inspector, clerk=clerk
    )


def _rule(w, pct, group=SUPERVISOR, **extra):
    vals = {"policy_id": w.policy.id, "threshold_pct": pct, "group_id": w.env.ref(group).id}
    vals.update(extra)
    return w.env["fix.escalation.rule"].create(vals)


def _events(w):
    return w.env["fix.escalation.event"].search(
        [("res_model", "=", "fix.service.order"), ("res_id", "=", w.order.id)]
    )


# --- the rule ----------------------------------------------------------------


def test_a_level_is_a_share_of_the_target(w):
    for pct in (0, 101, -5):
        with pytest.raises(ValidationError), w.env.cr.savepoint():
            _rule(w, pct)
    assert _rule(w, 50).threshold_pct == 50


def test_one_role_is_told_once_per_level(w):
    _rule(w, 75)
    with pytest.raises(ValidationError), w.env.cr.savepoint():
        _rule(w, 75)
    # another role at the same level is a different escalation
    assert _rule(w, 75, group=QC)


def test_only_a_service_supervisor_keeps_the_rule_book(w):
    Rule = w.env["fix.escalation.rule"]
    vals = {"policy_id": w.policy.id, "threshold_pct": 50, "group_id": w.env.ref(QC).id}
    with pytest.raises(AccessError), w.env.cr.savepoint():
        Rule.with_user(w.clerk).create(vals)
    rule = Rule.with_user(w.sup).create(vals)
    assert rule.policy_id == w.policy
    # everyone may read it
    assert Rule.with_user(w.clerk).browse(rule.id).threshold_pct == 50


# --- the engine --------------------------------------------------------------


def test_the_clock_escalates_each_level_it_has_reached(w):
    _rule(w, 50)
    _rule(w, 75, group=QC)
    fired = w.env["fix.sla.kpi.instance"]._fire_escalation_rules()
    assert fired == 1
    ev = _events(w)
    assert len(ev) == 1 and ev.threshold_pct == 50
    assert 55 <= ev.elapsed_pct <= 65
    assert w.sup in ev.notified_user_ids and ev.state == "open"
    todo = w.env["mail.activity"].search(
        [
            ("res_model", "=", "fix.service.order"),
            ("res_id", "=", w.order.id),
            ("user_id", "=", w.sup.id),
            ("summary", "like", "SLA escalation 50%"),
        ]
    )
    assert todo
    # the next run does not escalate the same level again
    assert w.env["fix.sla.kpi.instance"]._fire_escalation_rules() == 0
    # 8 hours in, the 75% level goes to the QC role
    later = fields.Datetime.now() + timedelta(hours=2)
    assert w.env["fix.sla.kpi.instance"]._fire_escalation_rules(now=later) == 1
    assert sorted(_events(w).mapped("threshold_pct")) == [50, 75]
    assert w.inspector in _events(w).filtered(lambda e: e.threshold_pct == 75).notified_user_ids


def test_a_rule_for_another_kpi_does_not_fire(w):
    _rule(w, 50, kpi_code="first_response")
    assert w.env["fix.sla.kpi.instance"]._fire_escalation_rules() == 0
    _rule(w, 50, group=QC, kpi_code="resolution")
    assert w.env["fix.sla.kpi.instance"]._fire_escalation_rules() == 1


def test_a_pause_and_resume_does_not_escalate_the_level_again(w):
    _rule(w, 50)
    Inst = w.env["fix.sla.kpi.instance"]
    assert Inst._fire_escalation_rules() == 1
    w.clock.pause("parts")
    successor = w.clock.resume()
    assert successor != w.clock and successor.supersedes_id == w.clock
    # the successor keeps the series' used share (about 60%) ...
    assert 55 <= successor._fix_elapsed_pct(fields.Datetime.now()) <= 65
    # ... and the 50% level was already raised for this series
    assert Inst._fire_escalation_rules() == 0
    assert len(_events(w)) == 1


def test_a_paused_clock_does_not_escalate(w):
    _rule(w, 50)
    w.clock.pause("customer away")
    assert w.env["fix.sla.kpi.instance"]._fire_escalation_rules() == 0


def test_a_breach_reaches_the_100_percent_level_from_the_cron(w):
    _rule(w, 100)
    later = fields.Datetime.now() + timedelta(hours=5)
    Inst = w.env["fix.sla.kpi.instance"]
    # the clock breaches; the same cron run escalates it
    w.env.flush_all()
    w.env.cr.execute(
        "UPDATE fix_sla_kpi_instance SET target_at = %s WHERE id = %s",
        (fields.Datetime.now() - timedelta(minutes=1), w.clock.id),
    )
    w.env.invalidate_all()
    result = Inst.cron_flag_breaches()
    assert result["breached"] >= 1 and result["escalated"] >= 1
    ev = _events(w)
    assert ev.threshold_pct == 100 and ev.elapsed_pct == 100.0
    assert Inst._fire_escalation_rules(now=later) == 0


def test_a_finished_order_is_not_escalated(w):
    _rule(w, 50)
    w.env.flush_all()
    w.env.cr.execute(
        "UPDATE fix_service_order SET state = 'delivered' WHERE id = %s", (w.order.id,)
    )
    w.env.invalidate_all()
    assert w.env["fix.sla.kpi.instance"]._fire_escalation_rules() == 0


def test_no_role_holder_in_the_branch_is_recorded_not_lost(w):
    empty = w.env["res.groups"].create({"name": "M01 Esc Empty Role"})
    w.env["fix.escalation.rule"].create(
        {"policy_id": w.policy.id, "threshold_pct": 50, "group_id": empty.id}
    )
    assert w.env["fix.sla.kpi.instance"]._fire_escalation_rules() == 1
    ev = _events(w)
    assert ev.state == "no_owner" and not ev.notified_user_ids


def test_an_information_level_needs_no_acknowledgement(w):
    _rule(w, 50, requires_ack=False)
    w.env["fix.sla.kpi.instance"]._fire_escalation_rules()
    assert _events(w).state == "info"


# --- acknowledgement ---------------------------------------------------------


def test_a_notified_person_acknowledges_and_the_todo_closes(w):
    _rule(w, 50)
    w.env["fix.sla.kpi.instance"]._fire_escalation_rules()
    ev = _events(w)
    ev.with_user(w.sup).action_acknowledge(note="Calling the technician")
    assert ev.state == "acknowledged" and ev.acknowledged_by == w.sup
    assert ev.ack_note == "Calling the technician" and ev.acknowledged_at
    open_todo = w.env["mail.activity"].search(
        [
            ("res_model", "=", "fix.service.order"),
            ("res_id", "=", w.order.id),
            ("summary", "like", "SLA escalation 50%"),
        ]
    )
    assert not open_todo
    with pytest.raises(UserError):
        ev.with_user(w.sup).action_acknowledge()


def test_someone_not_told_cannot_acknowledge(w):
    _rule(w, 50, group=QC)
    w.env["fix.sla.kpi.instance"]._fire_escalation_rules()
    ev = _events(w)
    with pytest.raises(AccessError):
        ev.with_user(w.clerk).action_acknowledge()
    assert ev.state == "open"
    # a Service Supervisor may take any escalation
    ev.with_user(w.sup).action_acknowledge()
    assert ev.state == "acknowledged"


def test_an_escalation_is_never_typed_or_edited(w):
    rule = _rule(w, 50)
    w.env["fix.sla.kpi.instance"]._fire_escalation_rules()
    ev = _events(w)
    Event = w.env["fix.escalation.event"]
    with pytest.raises(UserError), w.env.cr.savepoint():
        Event.with_user(w.sup).create(
            {
                "rule_id": rule.id,
                "instance_id": w.clock.id,
                "series_root_id": w.clock.id,
                "res_model": "fix.service.order",
                "res_id": w.order.id,
                "fired_at": fields.Datetime.now(),
            }
        )
    with pytest.raises(UserError), w.env.cr.savepoint():
        ev.with_user(w.sup).write({"state": "acknowledged"})
    assert ev.state == "open"


# --- wiring ------------------------------------------------------------------


def test_the_escalation_runs_in_the_deployed_cron(w):
    cron = w.env.ref("cd_service_order.ir_cron_sla_breaches")
    assert cron.active and "cron_flag_breaches" in cron.code
    assert "escalated" in w.env["fix.sla.kpi.instance"].cron_flag_breaches()


def test_the_policy_shows_its_matrix(w):
    rule = _rule(w, 90)
    assert rule in w.policy.escalation_rule_ids
    assert "90%" in rule.display_name
