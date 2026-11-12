"""M02 bidirectional audit (2026-11-13): what the workspace shows and what the
backend does now agree. Each test pins one discrepancy that was found.

``odoo_env`` (addons/conftest.py): superuser environment, rolled back per test.
"""

from datetime import timedelta

import pytest
from odoo import Command, fields
from odoo.exceptions import UserError, ValidationError

from .test_field_dispatch_ext import (
    _certify,
    _field_order,
    _shift,
    fx,  # noqa: F401 - the shared fixture
)


def _leave(env, employee, day):
    """An approved leave request covering ``day`` (written as HR would)."""
    ltype = env["fix.leave.type"].search([], limit=1) or env["fix.leave.type"].create(
        {"name": "M02 Audit Leave", "code": "M02AL", "entitlement_days": 10}
    )
    leave = env["fix.leave.request"].create(
        {"employee_id": employee.id, "leave_type_id": ltype.id, "date_from": day, "date_to": day}
    )
    leave.write({"state": "approved"})  # superuser test env: HR's decision, recorded
    return leave


# --- BRU-FSM-01: a technician on leave is never offered nor sent -------------


def test_a_technician_on_approved_leave_is_neither_offered_nor_dispatched(fx):  # noqa: F811
    env = fx.env
    if "fix.leave.request" not in env:
        pytest.skip("cd_hr_core leave is not installed")
    away = env["hr.employee"].create({"name": "M02 Away Tech"})
    _certify(env, away)
    env["fix.work.order"].create({"order_id": fx.order.id, "technician_id": away.id})
    fo = _field_order(fx, scheduled_start=fields.Datetime.now() + timedelta(hours=1))
    assert "M02 Away Tech" in [s["name"] for s in fo.action_suggest_technicians(limit=50)]
    _leave(env, away, fo._fix_day())
    assert "M02 Away Tech" not in [s["name"] for s in fo.action_suggest_technicians(limit=50)]
    fo.action_request_dispatch()
    with pytest.raises(UserError, match="approved leave"):
        fo.action_dispatch(technician_id=away.id)


def test_a_roster_slot_marked_on_leave_rules_the_technician_out(fx):  # noqa: F811
    env = fx.env
    tech = env["hr.employee"].create({"name": "M02 Slot Leave Tech"})
    fo = _field_order(fx)
    slot = env["fix.roster.slot"].create(
        {"employee_id": tech.id, "date": fo._fix_day(), "shift_id": _shift(env).id}
    )
    slot._guarded().write({"on_leave": True})  # as the leave workflow marks it
    assert "M02 Slot Leave Tech" not in [s["name"] for s in fo.action_suggest_technicians(50)]


def test_an_unrostered_technician_is_offered_with_the_reason(fx):  # noqa: F811
    env = fx.env
    tech = env["hr.employee"].create({"name": "M02 Unrostered Tech"})
    _certify(env, tech)  # the M22 gate refuses an uncertified technician on a slot
    env["fix.work.order"].create({"order_id": fx.order.id, "technician_id": tech.id})
    fo = _field_order(fx)
    row = next(s for s in fo.action_suggest_technicians(50) if s["name"] == "M02 Unrostered Tech")
    assert "not on the day's roster" in row["reasons"]


def test_a_new_estate_offers_the_field_service_technicians(fx):  # noqa: F811
    """No work order, field order or roster names them yet: the Field Service
    Technician group still makes them candidates (fix_real offered nobody)."""
    env = fx.env
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "M02 Group Tech",
                "login": "m02.group.tech@audit.test",
                "group_ids": [
                    Command.link(env.ref("cd_field_service.group_fix_field_service_user").id)
                ],
            }
        )
    )
    env["hr.employee"].create({"name": "M02 Group Tech", "user_id": user.id})
    fo = _field_order(fx)
    assert "M02 Group Tech" in [s["name"] for s in fo.action_suggest_technicians(limit=500)]


# --- route plans: stops are the technician's own ------------------------------


def test_a_route_takes_only_its_technicians_orders(fx):  # noqa: F811
    env = fx.env
    other = env["hr.employee"].create({"name": "M02 Other Tech"})
    _certify(env, fx.tech)
    _certify(env, other)
    mine = _field_order(fx)
    mine.action_request_dispatch()
    mine.action_dispatch(technician_id=fx.tech.id)
    theirs = _field_order(fx)
    theirs.action_request_dispatch()
    theirs.action_dispatch(technician_id=other.id)
    Route = env["fix.field.route"]
    route = Route.create({"technician_id": fx.tech.id, "field_order_ids": [Command.set(mine.ids)]})
    assert route.order_count == 1 and route.name != "/"
    with pytest.raises(ValidationError, match="dispatched to someone else"):
        route.write({"field_order_ids": [Command.link(theirs.id)]})


# --- work orders: the Assign button's method ---------------------------------


def test_assign_technician_names_the_slot_and_assigns_it(fx):  # noqa: F811
    """The workspace Assign Technician button sends the employee id as text."""
    env = fx.env
    _certify(env, fx.tech)
    # M55: a slot is assigned from the roster, not the calendar
    # the LOCAL day the check reads (UTC is a day behind before 06:00 Dhaka)
    local_day = fields.Date.context_today(env["fix.work.order"])
    env["fix.roster.slot"].create(
        {"employee_id": fx.tech.id, "date": local_day, "shift_id": _shift(env).id}
    )
    slot = env["fix.work.order"].create({"order_id": fx.order.id})
    assert slot.state == "pending" and not slot.technician_id
    slot.action_assign(technician_id=str(fx.tech.id))
    assert (slot.state, slot.technician_id) == ("assigned", fx.tech)


def test_a_route_may_plan_an_order_not_yet_dispatched(fx):  # noqa: F811
    route = fx.env["fix.field.route"].create(
        {"technician_id": fx.tech.id, "field_order_ids": [Command.set(_field_order(fx).ids)]}
    )
    assert route.order_count == 1


# --- KPIs and safety reports say what is true --------------------------------


def test_automatic_assignment_rate_is_zero_not_one_hundred(fx):  # noqa: F811
    from odoo.addons.cd_p03_portal.controllers.a02 import m02

    env = fx.env
    _certify(env, fx.tech)
    fo = _field_order(fx)
    fo.action_request_dispatch()
    fo.action_dispatch(technician_id=fx.tech.id)
    # every dispatch is a dispatcher's pick: KPI-013 is 0 %, never 100 %
    assert m02.kpis(env)["auto_assignment"] == 0.0


def test_safety_reports_count_the_real_stores(fx):  # noqa: F811
    from odoo.addons.cd_p03_portal.controllers.a02 import m02

    env = fx.env
    lone = m02.REPORTS["lone_worker"](env)
    panic = m02.REPORTS["panic_alerts"](env)
    text = " ".join(lone["notes"] + panic["notes"]).lower()
    assert "no safety-event store" not in text
    assert any(r["event"].startswith("Sessions:") for r in lone["rows"])
    assert panic["rows"][0]["event"] == "Panic alerts received"
