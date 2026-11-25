"""A02 ERP pass 2, X5-14: M27 notices for A02 events the specs route to M27
and nobody consumed (M01 sla.warning, M05 AUT-RMS-10, M06 AUT-DTS-03).

Consumers are called the way the relay calls them (superuser); a plain
internal user is refused. ``odoo_env`` rolls back after each test.
"""

# ruff: noqa: F811  (fixtures are imported and used as parameters)

import pytest
from odoo.addons.cd_contact_centre.tests.test_a02_p1p2_cd_contact_centre import (  # noqa: F401
    so,
)
from odoo.exceptions import AccessError

SUPERVISOR = "cd_service_order.group_so_supervisor"
EVENTS = {
    "sla.instance_near_breach": "consume_sla_near_breach",
    "sla.escalated": "consume_sla_escalated",
    "msp.service_report_published": "consume_msp_service_report_published",
    "data_case.evaluated": "consume_data_case_evaluated",
    "data_case.quote_sent": "consume_data_case_quote_sent",
}


def _user(env, login, *groups):
    ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": "%s@a02r2.test" % login,
                "email": "%s@a02r2.test" % login,
                "group_ids": [(6, 0, ids)],
            }
        )
    )


def _emails(env, partner, order):
    return (
        env["fix.notif.delivery"]
        .sudo()
        .search(
            [
                ("partner_id", "=", partner.id),
                ("channel", "=", "email"),
                ("source_model", "=", order._name),
                ("source_id", "=", order.id),
            ]
        )
    )


def test_the_consumers_are_wired(odoo_env):
    rows = odoo_env["fix.event.consumer"].sudo().search([("model", "=", "fix.notif.delivery")])
    wired = {(r.event_type, r.method) for r in rows}
    assert set(EVENTS.items()) <= wired


def test_a_near_breach_emails_the_branch_supervisor_once(odoo_env, so):
    env = odoo_env
    supervisor = _user(env, "a02r2.sla.sup", SUPERVISOR)
    event = {
        "event_id": "a02r2-near-1",
        "payload": {
            "res_model": "fix.service.order",
            "res_id": so.id,
            "kpi": "resolution",
            "target_at": "2026-11-21 10:00:00",
        },
    }
    Delivery = env["fix.notif.delivery"].sudo()
    res = Delivery.consume_sla_near_breach(event)
    assert res["queued"] >= 1, res
    (row,) = _emails(env, supervisor.partner_id, so)
    assert so.name in row.body and row.lawful_basis == "contract"
    Delivery.consume_sla_near_breach(event)  # the relay redelivers
    assert len(_emails(env, supervisor.partner_id, so)) == 1


def test_a_clock_on_a_finished_order_notifies_nobody(odoo_env, so):
    env = odoo_env
    _user(env, "a02r2.sla.sup2", SUPERVISOR)
    so.action_cancel(reason_code="customer_declined")
    res = (
        env["fix.notif.delivery"]
        .sudo()
        .consume_sla_near_breach(
            {
                "event_id": "a02r2-near-2",
                "payload": {"res_model": "fix.service.order", "res_id": so.id},
            }
        )
    )
    assert res == {"queued": 0, "reason": "no open service order"}


def test_the_new_consumers_run_only_from_the_relay(odoo_env, so):
    clerk = _user(odoo_env, "a02r2.notify.clerk")
    Delivery = odoo_env["fix.notif.delivery"].with_user(clerk)
    for method in EVENTS.values():
        with pytest.raises(AccessError):
            getattr(Delivery, method)({"aggregate_id": so.id, "payload": {}})
