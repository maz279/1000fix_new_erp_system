"""A02 P1 (B2): the customer is told when an M01 estimate is sent and when the
device is ready, through the one exit (fix.notif.delivery.queue): consent,
curfew and evidence apply, transactional purpose on a contract basis.

The events are published by the real M01 transitions and delivered by the
R8 relay; the consumers refuse a direct (non-relay) call.
"""

from datetime import timedelta

import pytest
from odoo import Command
from odoo.exceptions import AccessError

NOTIFY_EVENTS = ("estimate.sent", "service_order.ready")


def _relay(env):
    Consumer = env["fix.event.consumer"].sudo()
    mine = Consumer.search(
        [("event_type", "in", NOTIFY_EVENTS), ("model", "=", "fix.notif.delivery")]
    )
    (Consumer.search([]) - mine).write({"active": False})
    mine.write({"active": True, "active_from": env.cr.now() - timedelta(minutes=1)})
    return env["fix.event.outbox"].sudo().cron_relay()


@pytest.fixture
def so(odoo_env):
    env = odoo_env
    if "fix.service.order" not in env:
        pytest.skip("cd_service_order not installed")
    branch = env["fix.branch"].search([("operating_unit_id", "!=", False)], limit=1)
    if not branch:
        ou = env["operating.unit"].search([], limit=1) or env["operating.unit"].create(
            {"name": "A2P1N OU", "code": "A2P1N", "company_id": env.company.id}
        )
        entity = env["fix.entity"].search([], limit=1) or env["fix.entity"].create(
            {"legal_name": "A2P1N Entity", "code": "A2P1NE", "company_id": env.company.id}
        )
        branch = env["fix.branch"].create(
            {
                "name": "A2P1N Branch",
                "code": "A2P1N-BR",
                "entity_id": entity.id,
                "operating_unit_id": ou.id,
            }
        )
    customer = env["res.partner"].create({"name": "A2P1 Notify Customer", "phone": "01711000888"})
    brand = env["fix.brand"].create({"name": "A2P1N Brand", "code": "A2P1N"})
    model = env["fix.device.model"].create({"name": "A2P1N Phone", "brand_id": brand.id})
    dev = env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": customer.id, "serial_number": "A2P1N-SN-1"}
    )
    order = env["fix.service.order"].create(
        {
            "device_id": dev.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "service_type": "walk_in",
            "fault_description": "No power",
        }
    )
    order.action_intake()
    order.action_start_diagnostic()
    order.action_request_estimate()
    return order


def _rows(env, order):
    return (
        env["fix.notif.delivery"]
        .sudo()
        .search([("source_model", "=", "fix.service.order"), ("source_id", "=", order.id)])
    )


def test_sent_estimate_and_ready_device_notify_the_customer_once(odoo_env, so):
    env = odoo_env
    est = env["fix.estimate"].create(
        {
            "order_id": so.id,
            "line_ids": [
                Command.create(
                    {"line_type": "labour", "description": "fix", "quantity": 1, "unit_price": 900}
                )
            ],
        }
    )
    est.action_send()
    _relay(env)
    rows = _rows(env, so)
    assert len(rows) == 1
    assert (rows.purpose, rows.lawful_basis, rows.channel) == ("service_updates", "contract", "sms")
    assert so.name in rows.body
    _relay(env)  # a redelivery is a no-op (dedup key per event)
    assert len(_rows(env, so)) == 1
    # the device is ready
    est.action_approve()
    so.action_start_repair()
    so.action_submit_qc()
    env["fix.qc.checklist"].create(
        {
            "order_id": so.id,
            "qc_round": so.qc_round,
            "state": "passed",
            "item_ids": [Command.create({"name": "Boot"})],
        }
    )
    so.action_ready()
    _relay(env)
    assert len(_rows(env, so)) == 2


def test_notification_consumers_run_only_from_the_relay(odoo_env, so):
    clerk = odoo_env["res.users"].create(
        {
            "name": "A2P1 Notify Clerk",
            "login": "a2p1.notify.clerk@a02.test",
            "group_ids": [(6, 0, [odoo_env.ref("base.group_user").id])],
        }
    )
    Delivery = odoo_env["fix.notif.delivery"].with_user(clerk)
    for method in ("consume_estimate_sent", "consume_service_order_ready"):
        with pytest.raises(AccessError):
            getattr(Delivery, method)({"aggregate_id": so.id, "payload": {}})
