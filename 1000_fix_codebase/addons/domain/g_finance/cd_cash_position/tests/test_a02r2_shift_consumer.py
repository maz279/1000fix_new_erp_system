"""A02 ERP pass 2, X5-14: M04 shift.closed reaches M50 (FR-TRE-016,
BRU-TRE-03).

A variance above the first threshold already needs the Branch Manager in
M04; above the second, M50 now escalates it to finance (the treasury alert:
a note and a to-do for each Accounting Administrator of the company), once
per shift. Delivered by cron_relay as the superuser.
``odoo_env`` rolls back after each test.
"""

from datetime import timedelta

import pytest
from odoo.exceptions import AccessError

from libs.py.fix_events import publish

PARAM = "cd_cash_position.shift_variance_escalation_threshold"
ADMIN = "account.group_account_manager"


@pytest.fixture
def world(odoo_env):
    env = odoo_env
    company = env.company
    ou = env["operating.unit"].search([("company_id", "=", company.id)], limit=1)
    entity = env["fix.entity"].search([("company_id", "=", company.id)], limit=1) or env[
        "fix.entity"
    ].create({"code": "A2R2E", "legal_name": company.name, "company_id": company.id})
    branch = env["fix.branch"].create(
        {
            "code": "A2R2SH",
            "name": "A02R2 Shift Branch",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    operator = env["hr.employee"].create({"name": "A02R2 Cashier"})
    finance = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A02R2 Finance",
                "login": "a02r2.finance@x514.test",
                "group_ids": [(6, 0, [env.ref("base.group_user").id, env.ref(ADMIN).id])],
                "company_ids": [(6, 0, company.ids)],
                "company_id": company.id,
            }
        )
    )
    env["ir.config_parameter"].sudo().set_param(PARAM, "1000")

    def shift(opening, counted):
        return env["fix.cash.shift"].create(
            {
                "company_id": company.id,
                "operating_unit_id": ou.id,
                "branch_id": branch.id,
                "operator_id": operator.id,
                "opening_float": opening,
                "closing_counted": counted,
                "state": "closed",
            }
        )

    return env, shift, finance


def _relay(env):
    Consumer = env["fix.event.consumer"].sudo()
    mine = Consumer.search([("event_type", "=", "shift.closed")])
    assert len(mine) == 1 and mine.method == "consume_shift_closed"
    (Consumer.search([]) - mine).write({"active": False})
    mine.write({"active": True, "active_from": env.cr.now() - timedelta(minutes=1)})
    env["fix.event.outbox"].sudo().cron_relay()


def _close(env, shift):
    publish(env, "shift.closed", "fix.cash.shift", shift.id, {"shift_id": shift.id})


def _todos(env, shift, user):
    return (
        env["mail.activity"]
        .sudo()
        .search(
            [
                ("res_model", "=", "fix.cash.shift"),
                ("res_id", "=", shift.id),
                ("user_id", "=", user.id),
            ]
        )
    )


def test_a_large_variance_reaches_finance_once(world):
    env, shift, finance = world
    short = shift(5000.0, 2000.0)  # BDT 3,000 short
    assert abs(short.variance) > 1000
    _close(env, short)
    _close(env, short)  # re-published
    _relay(env)
    (todo,) = _todos(env, short, finance)
    assert "Finance Manager threshold" in todo.summary


def test_a_variance_within_the_second_threshold_stays_with_the_branch(world):
    env, shift, finance = world
    small = shift(5000.0, 4500.0)  # BDT 500 short
    _close(env, small)
    _relay(env)
    assert not _todos(env, small, finance)


def test_the_consumer_runs_only_from_the_relay(world):
    env, shift, finance = world
    short = shift(5000.0, 2000.0)
    with pytest.raises(AccessError):
        env["fix.a02r2.treasury.consumers"].with_user(finance).consume_shift_closed(
            {"aggregate_id": short.id, "payload": {"shift_id": short.id}}
        )
