"""A02 ERP review (20 Nov 2026): the customer hears of every A02 milestone the
specs name, not only "estimate sent" and "ready" (NT-001 event matrix,
AUT-FSM-04, FR-FSM-037, AUT-LOG-03/05/06).

The M01 events come from the real transitions through the R8 relay; the
M02 / M03 payloads are the ones their publishers send.
"""

# ruff: noqa: F811  (fixtures are imported and used as parameters)

from datetime import timedelta

import pytest
from odoo.addons.cd_contact_centre.tests.test_a02_p1p2_cd_contact_centre import (  # noqa: F401
    _rows,
    so,
)
from odoo.exceptions import AccessError

A02_EVENTS = (
    "service_order.intake",
    "service_order.cancelled",
    "field.order.en_route",
    "visit.failed",
    "consignment.delivered",
    "consignment.returned",
)


def _relay(env):
    Consumer = env["fix.event.consumer"].sudo()
    mine = Consumer.search([("event_type", "in", A02_EVENTS), ("model", "=", "fix.notif.delivery")])
    assert len(mine) == len(A02_EVENTS), mine.mapped("event_type")
    (Consumer.search([]) - mine).write({"active": False})
    mine.write({"active": True, "active_from": env.cr.now() - timedelta(minutes=1)})
    return env["fix.event.outbox"].sudo().cron_relay()


def test_a_booked_order_and_its_cancellation_reach_the_customer(odoo_env, so):
    env = odoo_env
    _relay(env)  # the fixture's intake
    received = _rows(env, so)
    assert len(received) == 1 and so.name in received.body
    assert (received.purpose, received.lawful_basis) == ("service_updates", "contract")
    _relay(env)
    assert len(_rows(env, so)) == 1  # one event, one message
    so.action_cancel(reason_code="customer_declined")
    _relay(env)
    rows = _rows(env, so)
    assert len(rows) == 2
    assert any("cancelled" in r.body or "বাতিল" in r.body for r in rows)


def test_the_technician_on_the_way_and_the_logistics_legs_reach_the_customer(odoo_env, so):
    env = odoo_env
    Delivery = env["fix.notif.delivery"]
    before = len(_rows(env, so))
    res = Delivery.consume_field_order_en_route(
        {
            "event_id": "rv-enroute-1",
            "payload": {"service_order_id": so.id, "technician_name": "Rahim"},
        }
    )
    assert res.get("delivery_id"), res
    for leg, event_id in (("pickup", "rv-leg-1"), ("delivery", "rv-leg-2")):
        res = Delivery.consume_consignment_delivered(
            {
                "event_id": event_id,
                "payload": {"consignment_type": leg, "service_order_id": so.id},
            }
        )
        assert res.get("delivery_id"), res
    res = Delivery.consume_consignment_returned(
        {
            "event_id": "rv-rto-1",
            "payload": {"consignment_type": "delivery", "service_order_id": so.id},
        }
    )
    assert res.get("delivery_id"), res
    # a branch transfer is internal: nobody is texted
    res = Delivery.consume_consignment_delivered(
        {
            "event_id": "rv-leg-3",
            "payload": {"consignment_type": "branch_transfer", "service_order_id": so.id},
        }
    )
    assert res == {"queued": False, "reason": "not a customer leg"}
    bodies = _rows(env, so).mapped("body")
    assert len(bodies) == before + 4
    assert any("Rahim" in b for b in bodies)


def test_the_new_consumers_run_only_from_the_relay(odoo_env, so):
    clerk = odoo_env["res.users"].create(
        {
            "name": "A02 review notify clerk",
            "login": "a02.review.notify.clerk@a02.test",
            "group_ids": [(6, 0, [odoo_env.ref("base.group_user").id])],
        }
    )
    Delivery = odoo_env["fix.notif.delivery"].with_user(clerk)
    for method in (
        "consume_service_order_intake",
        "consume_service_order_cancelled",
        "consume_field_order_en_route",
        "consume_visit_failed",
        "consume_consignment_delivered",
        "consume_consignment_returned",
    ):
        with pytest.raises(AccessError):
            getattr(Delivery, method)({"aggregate_id": so.id, "payload": {}})
