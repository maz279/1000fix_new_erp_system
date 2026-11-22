"""test_a12_reaudit_drain.py — the no-publisher bus drain (A12 re-audit 2026-11-22).

The live estate carried 19k+ outbox rows at status='pending' forever: the
external bus publisher does not run here, `status` is the publisher's ledger,
and nothing drained, alerted on, or purged it. These tests prove the drain
cron bounds it: relayed events become 'published', unrelayed ones wait, and
the bus_publisher flag stands the drain down.
"""

from datetime import timedelta

import pytest
from odoo import fields

from libs.py.fix_events import publish


@pytest.fixture
def env(odoo_env):
    return odoo_env


def _pending_relayed(env, event_type="drain.probe"):
    publish(env, event_type, "res.partner", env.user.partner_id.id, {"n": 1})
    env.flush_all()
    row = env["fix.event.outbox"].search([("event_type", "=", event_type)], limit=1)
    row.write({"status": "pending", "relayed_at": fields.Datetime.now()})
    return row


def test_drain_marks_relayed_pending_published(env):
    row = _pending_relayed(env)
    drained = env["fix.event.outbox"].cron_mark_relayed_published(limit=10**6)
    assert drained >= 1
    row.invalidate_recordset()
    assert row.status == "published" and row.published_at


def test_drain_leaves_unrelayed_rows_alone(env):
    publish(env, "drain.unrelayed", "res.partner", env.user.partner_id.id, {"n": 2})
    env.flush_all()
    row = env["fix.event.outbox"].search([("event_type", "=", "drain.unrelayed")], limit=1)
    row.write({"status": "pending"})
    env["fix.event.outbox"].cron_mark_relayed_published(limit=10**6)
    row.invalidate_recordset()
    assert row.status == "pending"


def test_drain_stands_down_when_publisher_runs(env):
    row = _pending_relayed(env, "drain.flagged")
    params = env["ir.config_parameter"].sudo()
    params.set_param("fix_event_outbox.bus_publisher", "true")
    try:
        assert env["fix.event.outbox"].cron_mark_relayed_published() == 0
        row.invalidate_recordset()
        assert row.status == "pending"
    finally:
        params.set_param("fix_event_outbox.bus_publisher", "false")


def test_relay_health_reports_bus_backlog(env):
    row = _pending_relayed(env, "drain.health")
    health = env["fix.event.outbox"].relay_health()
    assert health["bus_pending"] >= 1
    assert health["oldest_bus_pending_hours"] >= 0.0
    row.write({"create_date": fields.Datetime.now() - timedelta(hours=30)})
    health = env["fix.event.outbox"].relay_health()
    assert health["oldest_bus_pending_hours"] >= 30.0


def test_backfill_refuses_non_admins_and_audits(env):
    from odoo.exceptions import AccessError

    sub = env["fix.event.consumer"].create(
        {
            "name": "drain backfill probe",
            "event_type": "drain.probe",
            "model": "res.partner",
            "method": "consume_probe_ok",
            "active_from": fields.Datetime.now(),
        }
    )
    admin_group = env.ref("cd_itsm.group_integration_admin", raise_if_not_found=False)
    mortal_domain = [("active", "=", True), ("id", "!=", 1)]
    if admin_group:
        mortal_domain.append(("group_ids", "not in", [admin_group.id]))
    mortal = env["res.users"].sudo().search(mortal_domain, limit=1)
    if mortal:
        with pytest.raises(AccessError):
            env["fix.event.consumer"].with_user(mortal).action_backfill()
    # As the server (su) it runs and leaves the audit event behind.
    assert sub.action_backfill()
    audit = env["fix.event.outbox"].search(
        [("event_type", "=", "integration.consumer_backfilled")], limit=1
    )
    assert audit and audit.payload
