"""test_event_relay.py — the in-process event relay (A03 audit R8).

The outbox was written and never read. These tests drive the relay against
throw-away consumers patched onto res.partner, so they prove the delivery
contract itself: once per consumer, retried, dead-lettered, never blocking a
healthy consumer, and never replaying history unless asked.
"""

from datetime import timedelta
from unittest import mock

import pytest
from odoo import fields
from odoo.exceptions import ValidationError

from libs.py.fix_events import publish


@pytest.fixture
def env(odoo_env):
    return odoo_env


@pytest.fixture
def consumer(env):
    """Patch consume_* methods onto res.partner; returns the call log."""
    calls = {"ok": [], "bad": []}
    cls = type(env["res.partner"])

    def ok(self, event):
        calls["ok"].append(event)

    def bad(self, event):
        calls["bad"].append(event)
        raise RuntimeError("consumer exploded")

    with (
        mock.patch.object(cls, "consume_probe_ok", ok, create=True),
        mock.patch.object(cls, "consume_probe_bad", bad, create=True),
    ):
        yield calls


def _sub(env, event_type, method, **vals):
    return env["fix.event.consumer"].create(
        {
            "name": "probe %s" % method,
            "event_type": event_type,
            "model": "res.partner",
            "method": method,
            "active_from": fields.Datetime.now() - timedelta(seconds=5),
            **vals,
        }
    )


def _emit(env, event_type="relay.probe", **payload):
    publish(env, event_type, "res.partner", env.user.partner_id.id, payload or {"n": 1})
    env.flush_all()
    return env["fix.event.outbox"].search(
        [("event_type", "=", event_type)], order="id desc", limit=1
    )


def test_an_event_reaches_its_consumer_exactly_once(env, consumer):
    _sub(env, "relay.probe", "consume_probe_ok")
    event = _emit(env, n=7)
    Outbox = env["fix.event.outbox"]
    Outbox.cron_relay()
    assert [c["payload"] for c in consumer["ok"]] == [{"n": 7}]
    assert consumer["ok"][0]["event_id"] == event.event_id
    assert event.relayed_at
    Outbox.cron_relay()
    event.write({"relayed_at": False})  # a redelivery
    Outbox.cron_relay()
    assert len(consumer["ok"]) == 1, "delivery is recorded per consumer, so a redelivery is a no-op"
    assert event.status == "pending", "bus publication is separate from in-process delivery"


def test_a_failing_consumer_retries_dead_letters_and_blocks_nobody(env, consumer):
    good = _sub(env, "relay.probe", "consume_probe_ok")
    bad = _sub(env, "relay.probe", "consume_probe_bad")
    event = _emit(env)
    Outbox = env["fix.event.outbox"]
    Outbox.cron_relay()
    assert len(consumer["ok"]) == 1
    delivery = env["fix.event.consumer.delivery"].search([("subscription_id", "=", bad.id)])
    assert delivery.state == "failed" and "consumer exploded" in delivery.last_error
    assert not event.relayed_at, "a failed consumer keeps the event open for retry"
    Outbox.cron_relay()
    Outbox.cron_relay()
    assert delivery.state == "dead" and delivery.attempts == 3
    assert event.relayed_at
    assert len(consumer["ok"]) == 1 and len(consumer["bad"]) == 3
    assert (
        env["fix.event.consumer.delivery"].search([("subscription_id", "=", good.id)]).state
        == "done"
    )
    assert Outbox.relay_health()["dead_letters"] >= 1


def test_history_is_not_replayed_unless_asked(env, consumer):
    event = _emit(env)
    env.cr.execute(
        "UPDATE fix_event_outbox SET create_date = %s WHERE id = %s",
        (fields.Datetime.now() - timedelta(days=3), event.id),
    )
    env.invalidate_all()
    sub = _sub(env, "relay.probe", "consume_probe_ok")
    env["fix.event.outbox"].cron_relay()
    assert not consumer["ok"], "an event older than the subscription is not delivered"
    sub.action_backfill()
    env["fix.event.outbox"].cron_relay()
    assert [c["event_id"] for c in consumer["ok"]] == [event.event_id]


def test_a_prefix_subscription_matches_the_family(env, consumer):
    _sub(env, "relay.family.*", "consume_probe_ok")
    _emit(env, "relay.family.one")
    _emit(env, "relay.other")
    env["fix.event.outbox"].cron_relay()
    assert [c["event_type"] for c in consumer["ok"]] == ["relay.family.one"]


def test_a_subscription_cannot_point_at_an_arbitrary_method(env):
    with pytest.raises(ValidationError, match="consume_"):
        _sub(env, "relay.probe", "unlink")


def test_an_unhealthy_relay_raises_its_alert(env, consumer):
    _sub(env, "relay.probe", "consume_probe_bad")
    event = _emit(env)
    env.cr.execute(
        "UPDATE fix_event_outbox SET create_date = %s WHERE id = %s",
        (fields.Datetime.now() - timedelta(hours=2), event.id),
    )
    env.invalidate_all()
    env["fix.event.consumer"].search([("method", "=", "consume_probe_bad")]).write(
        {"active_from": fields.Datetime.now() - timedelta(hours=3)}
    )
    env["fix.event.outbox"].cron_relay()
    health = env["fix.event.outbox"].cron_relay_age_alert()
    assert health["oldest_unrelayed_minutes"] > 30
    assert env["fix.event.outbox"].search_count([("event_type", "=", "outbox.relay_unhealthy")])
