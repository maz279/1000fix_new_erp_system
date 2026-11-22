# A08 M20-F5/F6: the dunning ladder's SEND half (FR-ARB-032/033,
# AUT-ARB-10). The A08 audit found the ladder advanced and escalated but
# never sent a reminder and kept no delivery evidence. These tests hold the
# four promises of the fix:
#   (a) a step transition sends exactly one reminder and writes one evidence
#       row carrying the amount and days overdue it stated;
#   (b) a failed send is recorded as failed and the retry (cron or person)
#       succeeds once — a sent step is never re-sent;
#   (c) a phone-call level raises the M27 handoff queue row, not a message;
#   (d) the evidence cannot be edited or deleted once it reached a delivery
#       state;
#   (e) disputed invoices still skip exactly as before.
from datetime import timedelta
from unittest import mock

import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

from . import test_a08_m20_controls as _controls
from .test_a08_m20_controls import as_
from .test_m20_capture_pass2 import TODAY, overdue
from .test_m20_capture_pass2 import policy as make_policy

c_raw = _controls.c_raw
c = _controls.c
REFUSED = (UserError, ValidationError, AccessError)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def provider(c, channel="email", transport="int_gateway"):
    """A configured M27 provider, so queue() attaches one and action_send()
    reaches the (patched) transport instead of stopping at 'no carrier'."""
    return (
        c.env["fix.notif.provider"]
        .sudo()
        .create(
            {
                "name": "Dunning %s %s" % (channel, c.tag),
                "code": "dun-%s-%s" % (channel, c.tag.lower()),
                "channel": channel,
                "transport": transport,
                "company_id": c.company.id,
            }
        )
    )


def _delivered(self, provider):
    return {"ok": True, "provider_ref": "dun-test-%s" % self.id}


def _failing(self, provider):
    return {"ok": False, "error": "gateway unreachable (test)", "permanent": False}


def _delivery_model(c):
    return type(c.env["fix.notif.delivery"])


def actions_for(c, invoice):
    return c.env["fix.ar.dunning.action"].search([("invoice_id", "=", invoice.id)], order="id")


def deliveries_for(c, action):
    return c.env["fix.notif.delivery"].search(
        [("source_model", "=", "fix.ar.dunning.action"), ("source_id", "=", action.id)]
    )


def active_policy(c, **vals):
    pol = make_policy(c, **vals)
    pol.with_user(c.mgr2).action_activate()
    return pol


# ================================================= (a) the step sends once
def test_a_ladder_step_sends_one_reminder_and_one_evidence_row(c):
    provider(c)
    c.customer.write({"email": "dun-%s@example.com" % c.tag})
    active_policy(
        c,
        first_offset_days=1,
        l1_channel="email",
        l2_days=7,
        l2_channel="email",
    )
    i = overdue(c, days=40)  # net-30 terms: 10 days past due
    Delivery = _delivery_model(c)
    with mock.patch.object(Delivery, "_dispatch_via_provider", _delivered):
        result = c.env["fix.dunning"].action_run_dunning()
        assert result["reminders_dispatched"]["sent"] == 1
        first = actions_for(c, i)
        assert len(first) == 1
        action = first
        assert (action.step, action.level, action.channel) == ("reminder", "l1", "email")
        assert action.state == "sent" and action.sent_at
        # the evidence carries what the customer was told
        assert action.amount == pytest.approx(11500.0)
        assert action.days_overdue == 10
        assert i.name in action.subject
        assert "11,500.00" in action.body and "10 days overdue" in action.body
        assert action.template_name == "ar_dunning.reminder.friendly.v1"
        assert action.recipient_masked == "d***@example.com"
        assert action.notif_delivery_ref.startswith("fix.notif.delivery:")
        delivery = deliveries_for(c, action)
        assert len(delivery) == 1
        assert delivery.state == "sent" and delivery.purpose == "collections"
        assert delivery.to_address == "dun-%s@example.com" % c.tag

        # advance the ladder one level: exactly ONE new reminder
        run = c.env["fix.dunning"].search([("invoice_id", "=", i.id)])
        run._guarded().write({"step_date": TODAY - timedelta(days=8)})
        result = c.env["fix.dunning"].action_run_dunning()
        assert result["reminders_dispatched"]["sent"] == 1

    actions = actions_for(c, i)
    assert [a.step for a in actions] == ["reminder", "final"]
    assert len(deliveries_for(c, actions[1])) == 1
    assert actions[1].amount == pytest.approx(11500.0)
    assert actions[1].days_overdue == 10
    assert actions[1].state == "sent"
    assert "FINAL REMINDER" in actions[1].body


# ============================== (b) a failed send is recorded and retried once
def test_a_failed_reminder_is_recorded_and_the_retry_succeeds_once(c):
    provider(c)
    c.customer.write({"email": "retry-%s@example.com" % c.tag})
    active_policy(c, first_offset_days=1, l1_channel="email")
    i = overdue(c, days=40)
    Delivery = _delivery_model(c)
    with mock.patch.object(Delivery, "_dispatch_via_provider", _failing):
        c.env["fix.dunning"].action_run_dunning()
    action = actions_for(c, i)
    assert len(action) == 1
    assert action.state == "failed"
    assert "gateway unreachable" in (action.failure_reason or "")
    assert action.notif_delivery_ref.startswith("fix.notif.delivery:")
    assert len(deliveries_for(c, action)) == 1

    Action = c.env["fix.ar.dunning.action"]
    with mock.patch.object(Delivery, "_dispatch_via_provider", _delivered):
        result = Action._cron_retry_failed()
        assert result == {"failed": 1, "sent": 1}
    assert action.state == "sent" and action.retry_count == 1
    assert action.provider_ref and not action.failure_reason
    # the retry reused the transport row: one message, not two
    assert len(deliveries_for(c, action)) == 1
    assert len(actions_for(c, i)) == 1

    # nothing left to retry, and a sent reminder is never re-sent
    with mock.patch.object(Delivery, "_dispatch_via_provider", _delivered):
        assert Action._cron_retry_failed()["failed"] == 0
        action.action_retry()
    assert action.state == "sent" and action.retry_count == 1
    assert len(deliveries_for(c, action)) == 1


# ============================== (c) a call level is an M27 handoff, not a message
def test_a_call_step_raises_the_m27_handoff_instead_of_a_message(c):
    c.customer.write({"phone": "01712345678"})
    active_policy(c, first_offset_days=1, l1_channel="call", l1_tone="final")
    i = overdue(c, days=40)
    c.env["fix.dunning"].action_run_dunning()
    action = actions_for(c, i)
    assert len(action) == 1
    assert action.channel == "call" and action.state == "handoff"
    assert action.notif_delivery_ref in (False, "")
    assert not deliveries_for(c, action), "a call step must not queue a message"
    handoff = c.env["fix.ar.dunning.handoff"].search([("action_id", "=", action.id)])
    assert len(handoff) == 1
    assert handoff.state == "m27_follow_up"
    assert handoff.phone == "01712345678"
    assert handoff.amount == pytest.approx(11500.0) and handoff.days_overdue == 10
    # the queue has an exit: a collector picks it up and closes it
    handoff.action_pick_up()
    assert handoff.state == "picked_up" and handoff.picked_up_by_id
    handoff.action_done(note="customer promised to pay on Friday")
    assert handoff.state == "done" and handoff.closed_by_id


# ================================================ (d) evidence is immutable
def test_the_reminder_evidence_cannot_be_edited_or_deleted(c):
    provider(c)
    c.customer.write({"email": "frozen-%s@example.com" % c.tag})
    active_policy(c, first_offset_days=1, l1_channel="email")
    i = overdue(c, days=40)
    Delivery = _delivery_model(c)
    with mock.patch.object(Delivery, "_dispatch_via_provider", _delivered):
        c.env["fix.dunning"].action_run_dunning()
    action = actions_for(c, i)
    assert action.state == "sent"
    body = action.body

    with pytest.raises(REFUSED):
        action.with_user(c.acct).write({"body": "a different message"})
    with pytest.raises(REFUSED):
        action.with_user(c.acct).write({"state": "failed"})
    with pytest.raises(REFUSED):
        action.with_user(c.acct).unlink()
    # even a superuser cannot erase evidence (the estate's deletion rule)
    with pytest.raises(REFUSED):
        action.unlink()
    action.invalidate_recordset()
    assert action.body == body and action.state == "sent"


# ============================================ (e) disputes still suppress
def test_a_fully_disputed_invoice_still_skips_the_reminder(c):
    provider(c)
    c.customer.write({"email": "dispute-%s@example.com" % c.tag})
    active_policy(c, first_offset_days=1, l1_channel="email")
    i = overdue(c, days=40)
    as_(c, c.acct)["fix.ar.dispute"].create(
        {"invoice_id": i.id, "amount_disputed": 11500.0, "reason": "wrong part"}
    )
    c.env["fix.dunning"].action_run_dunning()
    assert not c.env["fix.dunning"].search([("invoice_id", "=", i.id)])
    assert not actions_for(c, i)
    assert not c.env["fix.notif.delivery"].search([("source_model", "=", "fix.ar.dunning.action")])
