"""test_a12_p16_completion.py — the P1-6 remainder closed on 2026-11-05.

The A12 audit (working/A12_Workflow_and_Approval_Report.md §6 P1-6) said:
"either build the dispatcher, quota enforcement, connector probe and sync
apply, or remove the screens that imply them". The A12 build guarded all
three registers but left them read-by-nothing. These tests pin the three
completions:

1. quota enforcement  — check_request_allowed refuses on MEASURED counts,
   cron_enforce_quotas flips state both ways, audited;
2. connector probe    — cron_probe_connectors degrades on an expired
   credential / failing traffic, recovers on success traffic, never
   touches 'disabled', derives latency from the log;
3. sync apply         — local_wins/remote_wins WRITE the chosen value to
   the collided record; gone targets / non-text fields refuse; 'merged'
   applies nothing.
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
IADMIN = "cd_itsm.group_integration_admin"


@pytest.fixture
def env(odoo_env):
    return odoo_env


@pytest.fixture
def make_user(env):
    counter = {"n": 0}

    def _make(*xmlids):
        counter["n"] += 1
        groups = [env.ref("base.group_user").id] + [env.ref(x).id for x in xmlids]
        return (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "P16 Probe %d" % counter["n"],
                    "login": "p16.probe.%d@a12.test" % counter["n"],
                    "group_ids": [(6, 0, groups)],
                }
            )
        )

    return _make


@pytest.fixture
def plain(env, make_user):
    return make_user()


@pytest.fixture
def iadmin(env, make_user):
    return make_user(IADMIN)


@pytest.fixture
def consumer(env):
    return env["fix.api.consumer"].create(
        {"name": "P16 Consumer", "key_ref": "vault://keys/p16/v1"}
    )


@pytest.fixture
def quota(env, consumer):
    return env["fix.api.quota"].create(
        {"consumer_id": consumer.id, "requests_per_min": 3, "daily_quota": 5}
    )


def _log_api(env, consumer, n, status="success", minutes_ago=0):
    Log = env["fix.integration.log"].sudo()
    at = fields.Datetime.now() - timedelta(minutes=minutes_ago)
    for _ in range(n):
        Log._log_request("api", status=status, consumer=consumer.id, created_at=at)


# ---------------------------------------------------------------- quota


def test_p16_quota_gate_refuses_on_measured_rate(env, consumer, quota):
    _log_api(env, consumer, 3)
    verdict = env["fix.api.quota"].check_request_allowed(consumer.id)
    assert verdict["allowed"] is False
    assert "rate" in verdict["reason"]


def test_p16_quota_gate_refuses_on_measured_daily(env, consumer, quota):
    # old requests exhaust the daily quota but leave the per-minute empty. Pinned to
    # noon: "two hours ago" is yesterday's date in the first two hours of a UTC day
    noon = fields.Datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
    Log = env["fix.integration.log"].sudo()
    for _ in range(5):
        Log._log_request(
            "api", status="success", consumer=consumer.id, created_at=noon - timedelta(hours=2)
        )
    verdict = env["fix.api.quota"].check_request_allowed(consumer.id, at=noon)
    assert verdict["allowed"] is False
    assert "quota" in verdict["reason"]


def test_p16_quota_gate_allows_under_the_limits(env, consumer, quota):
    _log_api(env, consumer, 2)
    assert env["fix.api.quota"].check_request_allowed(consumer.id)["allowed"] is True


def test_p16_quota_gate_allows_consumer_without_quota(env, consumer):
    _log_api(env, consumer, 10)
    assert env["fix.api.quota"].check_request_allowed(consumer.id)["allowed"] is True


def test_p16_cron_throttles_and_releases_from_measured_counts(env, consumer, quota):
    _log_api(env, consumer, 3)
    env["fix.api.quota"].cron_enforce_quotas()
    assert quota.state == "throttled"
    # the append-only log cannot be aged by editing — assert release against
    # a second consumer whose traffic sits outside the live window
    consumer2 = env["fix.api.consumer"].create(
        {"name": "P16 Consumer 2", "key_ref": "vault://keys/p16b/v1"}
    )
    _log_api(env, consumer2, 3, minutes_ago=120)  # yesterday's traffic only
    quota2 = env["fix.api.quota"].create(
        {"consumer_id": consumer2.id, "requests_per_min": 3, "daily_quota": 5}
    )
    quota2._guarded().write({"state": "throttled"})
    env["fix.api.quota"].cron_enforce_quotas()
    assert quota2.state == "active"
    audits = (
        env["fix.security.audit"].sudo().search([("detail", "like", "quota_throttled")], limit=1)
    )
    assert audits, "the throttle decision was not audited"


def test_p16_quota_state_still_not_typable(env, plain, iadmin, quota):
    with pytest.raises(REFUSED):
        quota.with_user(plain).write({"state": "throttled"})
    with pytest.raises(REFUSED):
        quota.with_user(iadmin).write({"state": "throttled"})


# ------------------------------------------------------------- connector


def _connector(env, **kw):
    vals = {"name": "P16 Connector", "connector_type": "payment", "state": "live"}
    vals.update(kw)
    return env["fix.connector"].create(vals)


def test_p16_probe_degrades_on_expired_credential(env):
    cred = env["fix.connector.credential"].create(
        {
            "name": "P16 Cred",
            "secret_ref": "vault://secrets/p16",
            "expires_on": fields.Date.today() - timedelta(days=1),
        }
    )
    conn = _connector(env, credential_id=cred.id)
    conn.cron_probe_connectors()
    assert conn.state == "degraded"


def test_p16_probe_recovers_on_success_traffic_and_derives_latency(env):
    conn = _connector(env, state="degraded")
    Log = env["fix.integration.log"].sudo()
    for _ in range(3):
        Log._log_request(
            "api",
            status="success",
            connector=conn.id,
            consumer=None,
            latency_ms=120,
        )
    conn.cron_probe_connectors()
    assert conn.state == "live"
    assert conn.last_latency_ms == 120
    assert conn.last_success_at


def test_p16_probe_degrades_on_only_failing_traffic(env):
    conn = _connector(env)
    Log = env["fix.integration.log"].sudo()
    Log._log_request("api", status="failed", connector=conn.id)
    conn.cron_probe_connectors()
    assert conn.state == "degraded"


def test_p16_probe_never_touches_disabled(env):
    conn = _connector(env, state="disabled")
    Log = env["fix.integration.log"].sudo()
    Log._log_request("api", status="success", connector=conn.id, latency_ms=50)
    conn.cron_probe_connectors()
    assert conn.state == "disabled"


def test_p16_probe_leaves_silent_valid_connector_alone(env):
    conn = _connector(env, state="live")
    conn.cron_probe_connectors()
    assert conn.state == "live"
    assert not conn.last_success_at


def test_p16_action_probe_requires_integration_admin(env, plain, iadmin):
    conn = _connector(env)
    with pytest.raises(REFUSED):
        conn.with_user(plain).action_probe()
    conn.with_user(iadmin).action_probe()  # works for the admin role


# ------------------------------------------------------------ sync apply


def _conflict(env, partner, field_name="street", **kw):
    vals = {
        "device_ref": "P16-DEVICE",
        "res_model": "res.partner",
        "res_id": partner.id,
        "field_name": field_name,
        "local_value": "12 Gulshan Ave",
        "remote_value": "45 Banani Rd",
    }
    vals.update(kw)
    return env["fix.sync.conflict"].create(vals)


def test_p16_local_wins_applies_the_value(env, iadmin):
    partner = env["res.partner"].create({"name": "P16 Partner"})
    conflict = _conflict(env, partner)
    conflict.with_user(iadmin).action_local_wins()
    partner.invalidate_recordset()
    assert partner.street == "12 Gulshan Ave"
    assert conflict.resolution == "local_wins"


def test_p16_remote_wins_applies_the_value(env, iadmin):
    partner = env["res.partner"].create({"name": "P16 Partner R"})
    conflict = _conflict(env, partner)
    conflict.with_user(iadmin).action_remote_wins()
    partner.invalidate_recordset()
    assert partner.street == "45 Banani Rd"
    assert conflict.resolution == "remote_wins"


def test_p16_merged_applies_nothing(env, iadmin):
    partner = env["res.partner"].create({"name": "P16 Partner M", "street": "original"})
    conflict = _conflict(env, partner)
    conflict.with_user(iadmin).action_merged()
    partner.invalidate_recordset()
    assert partner.street == "original"
    assert conflict.resolution == "merged"


def test_p16_resolve_refuses_when_target_gone(env, iadmin):
    partner = env["res.partner"].create({"name": "P16 Gone"})
    conflict = _conflict(env, partner)
    partner.unlink()
    with pytest.raises(REFUSED):
        conflict.with_user(iadmin).action_local_wins()
    assert conflict.resolution == "pending"  # nothing half-resolved


def test_p16_resolve_refuses_non_text_field(env, iadmin):
    partner = env["res.partner"].create({"name": "P16 Numeric"})
    conflict = _conflict(env, partner, field_name="is_company")
    with pytest.raises(REFUSED):
        conflict.with_user(iadmin).action_local_wins()
    assert conflict.resolution == "pending"


def test_p16_resolve_still_requires_integration_admin(env, plain):
    partner = env["res.partner"].create({"name": "P16 Plain"})
    conflict = _conflict(env, partner)
    with pytest.raises(REFUSED):
        conflict.with_user(plain).action_local_wins()


def test_p16_resolution_is_audited(env, iadmin):
    partner = env["res.partner"].create({"name": "P16 Audit"})
    conflict = _conflict(env, partner)
    conflict.with_user(iadmin).action_local_wins()
    audits = (
        env["fix.security.audit"]
        .sudo()
        .search(
            [
                ("detail", "like", "sync_conflict_resolved"),
                ("detail", "like", "value applied to res.partner#%d" % partner.id),
            ],
            limit=1,
        )
    )
    assert audits, "the applied resolution was not audited"
