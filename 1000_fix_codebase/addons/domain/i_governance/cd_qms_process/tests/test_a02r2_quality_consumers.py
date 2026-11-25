"""A02 ERP pass 2, X5-14: M01 quality events reach M23.

service_order.qc_failed and rework.detected are routed to M23 by both the
M01 and the M23 specs; nothing consumed them, so a failed final QC or a
comeback under the repair warranty left no nonconformity. The QC failure is
produced by the real M01 transition and delivered by cron_relay as the
superuser. ``odoo_env`` rolls back after each test.
"""

# ruff: noqa: F811  (fixtures are imported and used as parameters)

from datetime import timedelta

import pytest
from odoo import Command
from odoo.addons.cd_contact_centre.tests.test_a02_p1p2_cd_contact_centre import (  # noqa: F401
    so,
)
from odoo.exceptions import AccessError

from libs.py.fix_events import publish

EVENTS = ("service_order.qc_failed", "rework.detected")


def _relay(env):
    Consumer = env["fix.event.consumer"].sudo()
    mine = Consumer.search([("event_type", "in", EVENTS), ("model", "=", "fix.ncr")])
    assert len(mine) == 2, mine.mapped("event_type")
    (Consumer.search([]) - mine).write({"active": False})
    mine.write({"active": True, "active_from": env.cr.now() - timedelta(minutes=1)})
    return env["fix.event.outbox"].sudo().cron_relay()


def _ncrs(env, order):
    return env["fix.ncr"].sudo().search([("order_id", "=", order.id)])


def _to_qc(env, order):
    est = env["fix.estimate"].create(
        {
            "order_id": order.id,
            "line_ids": [
                Command.create(
                    {"line_type": "labour", "description": "fix", "quantity": 1, "unit_price": 900}
                )
            ],
        }
    )
    est.action_send()
    est.action_approve()
    order.action_start_repair()
    order.action_submit_qc()


def test_a_failed_final_qc_raises_one_ncr(odoo_env, so):
    env = odoo_env
    _to_qc(env, so)
    so.action_qc_fail()
    _relay(env)
    (ncr,) = _ncrs(env, so)
    assert (ncr.source, ncr.severity, ncr.state) == ("service_order", "minor", "new")
    assert ncr.relay_key.startswith("service_order.qc_failed:")
    _relay(env)  # nothing new to deliver, nothing new raised
    assert len(_ncrs(env, so)) == 1
    # a second failure adds to the open NCR instead of stacking another
    so.action_start_repair()
    so.action_submit_qc()
    so.action_qc_fail()
    _relay(env)
    assert len(_ncrs(env, so)) == 1


def test_a_rework_raises_one_major_ncr(odoo_env, so):
    env = odoo_env
    payload = {"original_order_id": so.id, "rework_order_id": so.id, "fault": "F-12"}
    publish(env, "rework.detected", "fix.service.order", so.id, payload)
    publish(env, "rework.detected", "fix.service.order", so.id, payload)  # re-published
    _relay(env)
    (ncr,) = _ncrs(env, so)
    assert ncr.severity == "major" and "F-12" in ncr.description


def test_the_consumers_run_only_from_the_relay(odoo_env, so):
    clerk = odoo_env["res.users"].create(
        {
            "name": "A02R2 QMS clerk",
            "login": "a02r2.qms.clerk@a02r2.test",
            "group_ids": [(6, 0, [odoo_env.ref("base.group_user").id])],
        }
    )
    Ncr = odoo_env["fix.ncr"].with_user(clerk)
    for method in ("consume_service_order_qc_failed", "consume_rework_detected"):
        with pytest.raises(AccessError):
            getattr(Ncr, method)({"aggregate_id": so.id, "payload": {"order_id": so.id}})
