"""test_a12_reaudit_fixes.py — A12 re-audit fixes in cd_itsm (2026-11-22).

M66-1: an SLA escalation that finds nobody (empty agent group, no escalation
manager) must still tell a human — the admin last resort — instead of posting
a note that says "nobody" and creating no activity.
M66-2: one employee cannot hold two active seats on one licence.
M28-D2: a webhook delivery parked 'not sent' because its signing secret was
unavailable is retried when the secret appears, and graduates to the DLQ
after the grace window instead of waiting forever.
"""

import json
from unittest import mock

import pytest
from odoo.exceptions import UserError


@pytest.fixture
def env(odoo_env):
    return odoo_env


# ---- M66-1: the escalation sink -------------------------------------------


def test_escalation_with_empty_queue_tells_the_admin(env):
    Ticket = env["fix.itsm.ticket"]
    ticket = Ticket.create(
        {
            "title": "nobody holds the queue",
            "description": "probe: the desk is empty",
            "category": "hardware",
            "priority": "low",
        }
    )
    # sla_deadline is computed: flush the create's pending compute FIRST, or
    # the ORM overwrites the raw SQL below when it flushes later; then force
    # it far into the past at the storage level.
    env.flush_all()
    env.cr.execute(
        "UPDATE fix_itsm_ticket SET sla_deadline = %s, sla_target_hours = 1 WHERE id = %s",
        ("2020-01-01 00:00:00", ticket.id),
    )
    # Drop the cached computed deadline, or the cron's tier math reads the
    # stale in-memory value instead of the row the search matched.
    ticket.invalidate_recordset()
    params = env["ir.config_parameter"].sudo()
    params.set_param("cd_itsm.sla_escalation_manager", "")
    admin = env.ref("base.user_admin")
    with mock.patch.object(type(Ticket), "_queue_agents", return_value=env["res.users"]):
        Ticket.cron_escalate_sla()
    ticket.invalidate_recordset()
    assert ticket.escalated and ticket.escalation_level >= 1
    told = ticket.sudo().activity_ids.filtered(
        lambda a: a.user_id == admin and "SLA breach" in (a.summary or "")
    )
    assert told, "the admin last resort must carry an activity when the queue is empty"


# ---- M66-2: one active seat per employee per licence ----------------------


def test_second_active_seat_on_a_licence_is_refused(env):
    employee = env["hr.employee"].create({"name": "Seat Holder"})
    licence = env["fix.itsm.licence"].create(
        {"name": "Office Suite", "vendor": "Vendor", "seats_owned": 5}
    )
    licence.action_assign_seat(employee=employee.id)
    assert licence.seats_assigned == 1
    with pytest.raises(UserError, match="already holds an active seat"):
        licence.action_assign_seat(employee=employee.id)
    assert licence.seats_assigned == 1


# ---- M28-D2: not-sent webhook rows recover or dead-letter -----------------


def _subscription_row(env, consumer, topic):
    sub = env["fix.event.subscription"].create(
        {
            "consumer_id": consumer.id,
            "topic_id": topic.id,
            "endpoint_url": "https://hooks.probe.internal/hook",
            "secret_ref": "vault://secrets/reaudit-hmac",
        }
    )
    sub._guarded().write({"approval_state": "approved"})
    return sub


@pytest.fixture
def delivery_row(env):
    env["ir.config_parameter"].sudo().set_param(
        "fix.integration.webhook_allowlist", "hooks.probe.internal"
    )
    consumer = env["fix.api.consumer"].create(
        {"name": "Reaudit Consumer", "key_ref": "vault://keys/reaudit/v1"}
    )
    topic = env["fix.event.topic"].create({"code": "reaudit.topic", "name": "Reaudit"})
    sub = _subscription_row(env, consumer, topic)
    event = env["fix.event.outbox"].create(
        {
            "event_type": "reaudit.topic",
            "aggregate": "res.partner",
            "aggregate_id": 1,
            "payload": json.dumps({"n": 1}),
        }
    )
    return env["fix.webhook.delivery"].create(
        {
            "subscription_id": sub.id,
            "event_id": event.id,
            "company_id": env.company.id,
            "state": "not_sent",
            "last_outcome": "not sent: signing secret unavailable (vault://secrets/reaudit-hmac)",
        }
    )


def test_not_sent_row_requeues_when_secret_returns(env, delivery_row, monkeypatch):
    env["ir.config_parameter"].sudo().set_param("fix.integration.dispatch_enabled", "1")
    monkeypatch.setenv("FIX_VAULT_SECRETS_REAUDIT_HMAC", "s3cret")
    env["fix.webhook.delivery"]._fix_due()
    delivery_row.invalidate_recordset()
    assert delivery_row.state == "pending"


def test_not_sent_row_dead_letters_after_grace(env, delivery_row):
    env["ir.config_parameter"].sudo().set_param("fix.integration.dispatch_enabled", "1")
    # secret never appears; the row is far older than the grace window
    env.flush_all()
    env.cr.execute(
        "UPDATE fix_webhook_delivery SET create_date = %s WHERE id = %s",
        ("2020-01-01 00:00:00", delivery_row.id),
    )
    env["fix.webhook.delivery"]._fix_due()
    delivery_row.invalidate_recordset()
    assert delivery_row.state == "dead"
    dlq = (
        env["fix.event.dlq"].sudo().search([("webhook_delivery_id", "=", delivery_row.id)], limit=1)
    )
    assert dlq and "not sent for over" in dlq.reason.lower()
