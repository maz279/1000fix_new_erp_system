"""AUT-018 wiring tests: the outbox intake that was previously missing.

``consume_order_completed`` existed but NOTHING called it, and its documented
event (service_order.completed) is emitted by no producer — the live outbox
holds service_order.closed rows only. The cron intake now drains closed
events; idempotent per order.

``odoo_env`` (addons/conftest.py): fix_test, rolled back after every test.
"""


def test_cron_intake_creates_claim_from_closed_event(wc):
    env = wc.env
    order = wc.order
    assert order.order_category == "warranty"  # the fixture builds a warranty job
    env["fix.event.outbox"].create(
        {
            "event_id": "evt-aut018-test-1",
            "event_type": "service_order.closed",
            "aggregate": "fix.service.order",
            "aggregate_id": order.id,
            "payload": '{"order_id": %d, "state": "closed"}' % order.id,
        }
    )
    created = env["fix.warranty.claim"]._cron_aut018_intake()
    assert created == 1
    claims = env["fix.warranty.claim"].search([("service_order_id", "=", order.id)])
    assert len(claims) == 1
    assert claims.brand_id == order.device_id.brand_id


def test_cron_intake_is_idempotent_across_runs(wc):
    env = wc.env
    order = wc.order
    for i in (1, 2):
        env["fix.event.outbox"].create(
            {
                "event_id": "evt-aut018-replay-%d" % i,
                "event_type": "service_order.closed",
                "aggregate": "fix.service.order",
                "aggregate_id": order.id,
                "payload": "{}",
            }
        )
    assert env["fix.warranty.claim"]._cron_aut018_intake() == 1
    # second run over the same outbox rows: no duplicate claim
    assert env["fix.warranty.claim"]._cron_aut018_intake() == 0
    assert env["fix.warranty.claim"].search_count([("service_order_id", "=", order.id)]) == 1


def test_cron_intake_skips_non_warranty_orders(wc):
    env = wc.env
    standard = env["fix.service.order"].create(
        {
            "device_id": wc.order.device_id.id,
            "customer_id": wc.order.customer_id.id,
            "branch_id": wc.order.branch_id.id,
            "fault_description": "Paid repair",
            "order_category": "standard",
        }
    )
    env["fix.event.outbox"].create(
        {
            "event_id": "evt-aut018-std-1",
            "event_type": "service_order.closed",
            "aggregate": "fix.service.order",
            "aggregate_id": standard.id,
            "payload": "{}",
        }
    )
    assert env["fix.warranty.claim"]._cron_aut018_intake() == 0
    assert not env["fix.warranty.claim"].search([("service_order_id", "=", standard.id)])
