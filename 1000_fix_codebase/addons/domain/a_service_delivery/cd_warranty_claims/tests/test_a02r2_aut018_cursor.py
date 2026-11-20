"""A02 ERP pass 2, X5-22: the AUT-018 backup intake reads on from a cursor.

The intake searched the OLDEST 500 service_order.closed events every hour,
so once 500 had been seen it re-read the same rows and never reached a newer
close. The batch is shrunk to 2 here so the stall shows with three events.
``odoo_env`` rolls back after each test.
"""

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


def test_the_intake_reaches_events_past_its_first_batch(wc, monkeypatch):
    env = wc.env
    monkeypatch.setattr(fwc, "AUT018_BATCH", 2)
    Outbox = env["fix.event.outbox"].sudo()
    last = Outbox.search([], order="id desc", limit=1)
    env["ir.config_parameter"].sudo().set_param(fwc.AUT018_CURSOR_PARAM, str(last.id or 0))
    standard = wc.closed_order(category="standard")
    _closed_event(env, standard, "std-1")
    _closed_event(env, standard, "std-2")
    warranty = wc.closed_order()
    assert warranty.order_category == "warranty"
    _closed_event(env, warranty, "wty")
    Claim = env["fix.warranty.claim"]
    assert Claim._cron_aut018_intake() == 0  # the two standard closes
    assert Claim._cron_aut018_intake() == 1  # the next run reads on
    assert Claim.search_count([("service_order_id", "=", warranty.id)]) == 1
    assert Claim._cron_aut018_intake() == 0  # nothing new: nothing re-read
