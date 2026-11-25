"""A02 ERP pass 2, X5-22: the AUT-018 backup intake reads on from a cursor.

The intake searched the OLDEST 500 service_order.closed events every hour,
so once 500 had been seen it re-read the same rows and never reached a newer
close. The batch is shrunk to 2 here so the stall shows with three events.

Independent review of the first fix (P2 16/17): the cursor is a low-water
mark - it never passes an event younger than the lag (an outbox id is taken
before its transaction commits, so a lower id can appear after a higher one)
nor an event that failed and is still being retried.
``odoo_env`` rolls back after each test.
"""

import json
from datetime import timedelta

from odoo import fields
from odoo.addons.cd_warranty_claims.models import fix_warranty_claims as fwc


def _closed_event(env, order, tag):
    return env["fix.event.outbox"].create(
        {
            "event_id": "evt-a02r2-x522-%s" % tag,
            "event_type": "service_order.closed",
            "aggregate": "fix.service.order",
            "aggregate_id": order.id,
            "payload": "{}",
        }
    )


def _age(env, events, minutes=60):
    """Back-date outbox rows past the cursor lag (their commit is long done)."""
    env.flush_all()
    env.cr.execute(
        "UPDATE fix_event_outbox SET create_date = %s WHERE id IN %s",
        (fields.Datetime.now() - timedelta(minutes=minutes), tuple(events.ids)),
    )
    events.invalidate_recordset(["create_date"])


def _start(env):
    params = env["ir.config_parameter"].sudo()
    last = env["fix.event.outbox"].sudo().search([], order="id desc", limit=1)
    params.set_param(fwc.AUT018_CURSOR_PARAM, str(last.id or 0))
    params.set_param(fwc.AUT018_FAILURES_PARAM, "{}")
    return params


def _cursor(params):
    return int(params.get_param(fwc.AUT018_CURSOR_PARAM))


def test_the_intake_reaches_events_past_its_first_batch(wc, monkeypatch):
    env = wc.env
    monkeypatch.setattr(fwc, "AUT018_BATCH", 2)
    _start(env)
    standard = wc.closed_order(category="standard")
    old = _closed_event(env, standard, "std-1") | _closed_event(env, standard, "std-2")
    warranty = wc.closed_order()
    assert warranty.order_category == "warranty"
    old |= _closed_event(env, warranty, "wty")
    _age(env, old)
    Claim = env["fix.warranty.claim"]
    assert Claim._cron_aut018_intake() == 0  # the two standard closes
    assert Claim._cron_aut018_intake() == 1  # the next run reads on
    assert Claim.search_count([("service_order_id", "=", warranty.id)]) == 1
    assert Claim._cron_aut018_intake() == 0  # nothing new: nothing re-read


def test_the_cursor_never_passes_an_event_younger_than_the_lag(wc):
    env = wc.env
    params = _start(env)
    start = _cursor(params)
    warranty = wc.closed_order()
    young = _closed_event(env, warranty, "young")
    Claim = env["fix.warranty.claim"]
    assert Claim._cron_aut018_intake() == 1  # processed at once...
    assert _cursor(params) == start  # ...but the mark waits for the lag
    _age(env, young)
    assert Claim._cron_aut018_intake() == 0  # re-read is free
    assert _cursor(params) == young.id


def test_a_failed_event_is_retried_then_given_up(wc, monkeypatch):
    env = wc.env
    params = _start(env)
    start = _cursor(params)
    warranty = wc.closed_order()
    event = _closed_event(env, warranty, "fails")
    _age(env, event)
    Claim = type(env["fix.warranty.claim"])
    real = Claim.consume_order_completed

    def broken(self, payload):
        raise ValueError("brand master unavailable")

    monkeypatch.setattr(Claim, "consume_order_completed", broken)
    assert env["fix.warranty.claim"]._cron_aut018_intake() == 0
    assert _cursor(params) == start  # not dropped: retried next run
    assert json.loads(params.get_param(fwc.AUT018_FAILURES_PARAM)) == {str(event.id): 1}
    monkeypatch.setattr(Claim, "consume_order_completed", real)
    assert env["fix.warranty.claim"]._cron_aut018_intake() == 1  # the retry succeeds
    assert _cursor(params) == event.id
    assert json.loads(params.get_param(fwc.AUT018_FAILURES_PARAM)) == {}


def test_an_event_that_keeps_failing_stops_holding_the_cursor(wc, monkeypatch):
    env = wc.env
    params = _start(env)
    monkeypatch.setattr(fwc, "AUT018_MAX_ATTEMPTS", 2)
    warranty = wc.closed_order()
    event = _closed_event(env, warranty, "poison")
    _age(env, event)
    Claim = type(env["fix.warranty.claim"])

    def broken(self, payload):
        raise ValueError("permanently malformed")

    monkeypatch.setattr(Claim, "consume_order_completed", broken)
    env["fix.warranty.claim"]._cron_aut018_intake()
    assert _cursor(params) < event.id
    env["fix.warranty.claim"]._cron_aut018_intake()  # second and last attempt
    assert _cursor(params) == event.id
