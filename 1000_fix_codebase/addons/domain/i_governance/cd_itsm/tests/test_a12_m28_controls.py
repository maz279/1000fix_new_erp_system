"""test_a12_m28_controls.py — the A12 remediation of M28 (Integration, API &
Events), probed as NON-ADMIN users where the attack was non-admin.

Source: working/A12_Workflow_and_Approval_Report.md §6 (X4, P1-6, R4) and
working/A12_evidence/module_findings/M28.md (M28-1..M28-13). Every control is
checked both ways: the bypass is refused, the legitimate role still works.
The superuser fixture only builds the world; the attacks run as a plain
employee and as a member of cd_itsm.group_integration_admin.
"""

from __future__ import annotations

import json
import re
from datetime import timedelta
from pathlib import Path

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
IADMIN = "cd_itsm.group_integration_admin"
ALLOWLIST_KEY = "fix.integration.webhook_allowlist"

SCHEMA_OK = json.dumps({"type": "object", "properties": {"sn": {"type": "string"}}})


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
                    "name": "M28 A12 Probe %d" % counter["n"],
                    "login": "m28.a12.probe.%d@a12.test" % counter["n"],
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
def endpoint(env):
    return env["fix.api.endpoint"].create(
        {"code": "PROBE-API", "name": "Probe API", "path": "/api/v1/probe", "auth_type": "oauth2"}
    )


@pytest.fixture
def consumer(env):
    return env["fix.api.consumer"].create(
        {"name": "Probe Consumer", "key_ref": "vault://keys/probe-consumer/v2"}
    )


@pytest.fixture
def quota(env, consumer, endpoint):
    return env["fix.api.quota"].create(
        {"consumer_id": consumer.id, "endpoint_id": endpoint.id, "requests_per_min": 60}
    )


@pytest.fixture
def topic(env):
    return env["fix.event.topic"].create({"code": "probe.topic", "name": "Probe Topic"})


@pytest.fixture
def allowlist(env):
    env["ir.config_parameter"].sudo().set_param(ALLOWLIST_KEY, "hooks.probe.internal")
    return "hooks.probe.internal"


def _subscription(env, consumer, topic, url="https://hooks.probe.internal/hook"):
    return env["fix.event.subscription"].create(
        {
            "consumer_id": consumer.id,
            "topic_id": topic.id,
            "endpoint_url": url,
            "secret_ref": "vault://secrets/probe-hmac",
        }
    )


def _dead_delivery(env):
    """A real dead letter of the in-process relay: outbox event + consumer
    subscription + a delivery the relay gave up on."""
    event = env["fix.event.outbox"].create(
        {
            "event_type": "probe.dead",
            "aggregate": "res.partner",
            "aggregate_id": 1,
            "payload": json.dumps({"sn": "P-1"}),
        }
    )
    sub = env["fix.event.consumer"].create(
        {
            "name": "probe relay consumer",
            "event_type": "probe.dead",
            "model": "res.partner",
            "method": "consume_probe_never",
        }
    )
    delivery = env["fix.event.consumer.delivery"].create(
        {
            "subscription_id": sub.id,
            "event_id": event.id,
            "state": "dead",
            "attempts": 3,
            "last_error": "probe: consumer exploded",
        }
    )
    return event, sub, delivery


# --------------------------------------------------------------------------
# M28-2 / X4 — API governance is admin-only (probe A01-A04)


def test_m28_2_non_admin_cannot_create_or_lift_api_masters(env, plain, endpoint, quota):
    Endpoint = env["fix.api.endpoint"].with_user(plain)
    with pytest.raises(AccessError):
        Endpoint.create(
            {"code": "EVIL", "name": "evil", "path": "/api/v1/evil", "auth_type": "none"}
        )
    with pytest.raises(AccessError):
        env["fix.api.endpoint"].with_user(plain).browse(endpoint.id).write({"auth_type": "none"})
    with pytest.raises(AccessError):
        env["fix.api.quota"].with_user(plain).browse(quota.id).write(
            {"requests_per_min": 1000000, "state": "active"}
        )
    with pytest.raises(AccessError):
        env["fix.api.consumer"].with_user(plain).create({"name": "attacker consumer"})


def test_m28_2_integration_admin_still_configures_and_quota_takes_effect_directly(
    env, iadmin, endpoint, quota
):
    # the legitimate role can register and re-limit; the new limit applies
    # without any pause/resume state dance
    env["fix.api.endpoint"].with_user(iadmin).create(
        {"code": "GOOD", "name": "good", "path": "/api/v1/good", "auth_type": "api_key"}
    )
    env["fix.api.quota"].with_user(iadmin).browse(quota.id).write({"requests_per_min": 120})
    assert quota.requests_per_min == 120 and quota.state == "active"


def test_m28_2_quota_state_is_measured_not_typed(env, iadmin, quota):
    with pytest.raises(REFUSED):
        env["fix.api.quota"].with_user(iadmin).browse(quota.id).write({"state": "throttled"})
    # server code (the gateway) records the verdict through sudo
    quota.sudo().write({"state": "throttled"})
    assert quota.state == "throttled"


# --------------------------------------------------------------------------
# M28-2 / A05 — key rotation


def test_m28_2_rotate_key_bumps_vault_version_and_audits(env, plain, iadmin, consumer):
    with pytest.raises(AccessError):
        env["fix.api.consumer"].with_user(plain).browse(consumer.id).action_rotate_key()
    env["fix.api.consumer"].with_user(iadmin).browse(consumer.id).action_rotate_key()
    assert consumer.key_ref == "vault://keys/probe-consumer/v3"
    assert "#rotated" not in (consumer.key_ref or "")
    audit = (
        env["fix.security.audit"].sudo().search([("detail", "ilike", "%integration.key_rotated%")])
    )
    assert audit, "rotation left no security-audit row"


def test_m28_2_rotate_key_refuses_plain_key_references(env, iadmin):
    rec = env["fix.api.consumer"].create({"name": "keyless consumer"})
    with pytest.raises(REFUSED):
        env["fix.api.consumer"].with_user(iadmin).browse(rec.id).action_rotate_key()


def test_m28_2_consumer_key_ref_must_be_vault(env):
    # the value is deliberately NOT key-shaped (gitleaks generic-api-key):
    # the constraint refuses any plain reference, whatever it looks like
    with pytest.raises(ValidationError):
        env["fix.api.consumer"].create({"name": "raw key", "key_ref": "plain-text-refusal"})


# --------------------------------------------------------------------------
# M28-1 / X4 — webhook endpoints: https + allow-list + vault secret


def test_m28_1_http_webhook_url_refused(env, iadmin, consumer, topic):
    Sub = env["fix.event.subscription"].with_user(iadmin)
    with pytest.raises(ValidationError):
        Sub.create(
            {
                "consumer_id": consumer.id,
                "topic_id": topic.id,
                "endpoint_url": "http://hooks.probe.internal/collect",
                "secret_ref": "vault://secrets/hmac",
            }
        )


def test_m28_1_https_host_must_be_allowlisted(env, iadmin, consumer, topic, allowlist):
    Sub = env["fix.event.subscription"].with_user(iadmin)
    # empty-ish default is tested by the previous fixtures: not on the list
    with pytest.raises(ValidationError):
        Sub.create(
            {
                "consumer_id": consumer.id,
                "topic_id": topic.id,
                "endpoint_url": "https://attacker.example.net/collect",
                "secret_ref": "vault://secrets/hmac",
            }
        )
    with pytest.raises(ValidationError):
        Sub.create(
            {
                "consumer_id": consumer.id,
                "topic_id": topic.id,
                "endpoint_url": "https://localhost/collect",
                "secret_ref": "vault://secrets/hmac",
            }
        )
    # an allow-listed host is accepted
    sub = Sub.create(
        {
            "consumer_id": consumer.id,
            "topic_id": topic.id,
            "endpoint_url": "https://hooks.probe.internal/hook",
            "secret_ref": "vault://secrets/hmac",
        }
    )
    assert sub.state == "active"


def test_m28_1_webhook_secret_required_and_vault_prefixed(env, iadmin, consumer, topic, allowlist):
    Sub = env["fix.event.subscription"].with_user(iadmin)
    with pytest.raises(ValidationError):
        Sub.create(
            {
                "consumer_id": consumer.id,
                "topic_id": topic.id,
                "endpoint_url": "https://hooks.probe.internal/hook",
                "secret_ref": False,
            }
        )
    with pytest.raises(ValidationError):
        Sub.create(
            {
                "consumer_id": consumer.id,
                "topic_id": topic.id,
                "endpoint_url": "https://hooks.probe.internal/hook",
                "secret_ref": "super-secret-hmac-value",
            }
        )


def test_m28_1_redirecting_an_existing_webhook_is_rechecked(
    env, iadmin, consumer, topic, allowlist
):
    sub = _subscription(env, consumer, topic)
    with pytest.raises(ValidationError):
        env["fix.event.subscription"].with_user(iadmin).browse(sub.id).write(
            {"endpoint_url": "http://attacker.example.net/collect"}
        )
    with pytest.raises(ValidationError):
        env["fix.event.subscription"].with_user(iadmin).browse(sub.id).write({"secret_ref": False})


def test_m28_1_subscription_state_changes_only_through_actions(
    env, iadmin, consumer, topic, allowlist
):
    sub = _subscription(env, consumer, topic)
    with pytest.raises(REFUSED):
        env["fix.event.subscription"].with_user(iadmin).browse(sub.id).write({"state": "paused"})
    env["fix.event.subscription"].with_user(iadmin).browse(sub.id).action_pause()
    assert sub.state == "paused"
    env["fix.event.subscription"].with_user(iadmin).browse(sub.id).action_resume()
    assert sub.state == "active"


# --------------------------------------------------------------------------
# M28-4 / M28-6 / P1-6 — one DLQ, fed by the relay; privileged replay


def _mirror_one(env):
    event, sub, delivery = _dead_delivery(env)
    env["fix.event.dlq"].cron_sync_dead_letters()
    return event, sub, delivery


def test_m28_4_cron_mirrors_real_dead_letters_idempotently(env):
    event, sub, delivery = _dead_delivery(env)
    # a failing (retryable) delivery is NOT a dead letter
    retryable_event = env["fix.event.outbox"].create(
        {
            "event_type": "probe.dead",
            "aggregate": "res.partner",
            "aggregate_id": 2,
            "payload": json.dumps({"sn": "P-2"}),
        }
    )
    failing = env["fix.event.consumer.delivery"].create(
        {"subscription_id": sub.id, "event_id": retryable_event.id, "state": "failed"}
    )
    created = env["fix.event.dlq"].cron_sync_dead_letters()
    assert created >= 1  # at least OUR dead letter was mirrored
    entry = env["fix.event.dlq"].search([("delivery_id", "=", delivery.id)])
    assert len(entry) == 1
    assert entry.topic_code == "probe.dead"
    assert "probe: consumer exploded" in entry.reason
    assert entry.state == "pending"
    # second run mirrors nothing new (unique on the delivery link)
    assert env["fix.event.dlq"].cron_sync_dead_letters() == 0
    assert env["fix.event.dlq"].search_count([("delivery_id", "=", failing.id)]) == 0


def test_m28_6_replay_privileged_audited_idempotent(env, plain, iadmin):
    event, sub, delivery = _mirror_one(env)
    entry = env["fix.event.dlq"].search([("delivery_id", "=", delivery.id)])
    # a plain employee may not even read the DLQ, let alone replay it
    with pytest.raises(AccessError):
        env["fix.event.dlq"].with_user(plain).browse(entry.ids).action_replay()
    # the integration admin replays: the delivery is re-enqueued for the relay
    env["fix.event.dlq"].with_user(iadmin).browse(entry.ids).action_replay()
    assert entry.state == "replayed"
    assert entry.replayed_by == iadmin
    assert delivery.state == "failed" and delivery.attempts == 0
    assert not event.relayed_at  # the relay cron will retry the event
    audit = (
        env["fix.security.audit"].sudo().search([("detail", "ilike", "%integration.dlq_replayed%")])
    )
    assert audit, "replay left no security-audit row"
    # idempotent: replaying a replayed entry is refused, nothing re-enqueued
    with pytest.raises(REFUSED):
        env["fix.event.dlq"].with_user(iadmin).browse(entry.ids).action_replay()
    # a replay that dead-letters AGAIN resurfaces as pending (BRU-IPF-14)
    delivery.sudo().write(
        {"state": "dead", "delivered_at": fields.Datetime.now() + timedelta(minutes=1)}
    )
    env["fix.event.dlq"].cron_sync_dead_letters()
    assert entry.state == "pending" and not entry.replayed_at


def test_m28_6_replay_refuses_rows_with_no_delivery_and_discard_is_privileged(env, iadmin):
    orphan = (
        env["fix.event.dlq"]
        .sudo()
        .create(
            {"topic_code": "seed.legacy", "payload": "{}", "reason": "seeded before the mirror"}
        )
    )
    with pytest.raises(REFUSED):
        env["fix.event.dlq"].with_user(iadmin).browse(orphan.id).action_replay()
    env["fix.event.dlq"].with_user(iadmin).browse(orphan.id).action_discard()
    assert orphan.state == "discarded"
    audit = (
        env["fix.security.audit"]
        .sudo()
        .search([("detail", "ilike", "%integration.dlq_discarded%")])
    )
    assert audit


def test_m28_6_dlq_state_not_forgeable(env, iadmin):
    with pytest.raises(REFUSED):
        env["fix.event.dlq"].with_user(iadmin).create(
            {
                "topic_code": "forged",
                "payload": "{}",
                "reason": "born replayed",
                "state": "replayed",
            }
        )


# --------------------------------------------------------------------------
# M28-8 / P1-6 — schema registry: valid JSON, frozen once published


def test_m28_8_non_json_schema_refused(env, iadmin):
    with pytest.raises(ValidationError):
        env["fix.event.schema"].with_user(iadmin).create(
            {"code": "probe.schema", "schema_text": "not json {{{"}
        )


def test_m28_8_publish_freezes_the_contract(env, iadmin):
    Schema = env["fix.event.schema"].with_user(iadmin)
    schema = Schema.create({"code": "probe.schema", "schema_text": SCHEMA_OK})
    schema.action_publish()
    assert schema.state == "published"
    for frozen, value in (
        ("schema_text", '{"type": "array"}'),
        ("code", "probe.schema.renamed"),
        ("version", 2),
    ):
        with pytest.raises(REFUSED):
            schema.write({frozen: value})
    # the form locks the same fields for this record
    locks = schema._fix_form_locked_fields()
    assert {"schema_text", "code", "version"} <= locks
    # the legitimate correction path: a NEW version record
    v2 = Schema.create({"code": "probe.schema", "version": 2, "schema_text": SCHEMA_OK})
    assert v2.state == "draft"


def test_m28_8_publish_is_privileged(env, plain):
    schema = (
        env["fix.event.schema"].sudo().create({"code": "probe.schema2", "schema_text": SCHEMA_OK})
    )
    with pytest.raises(AccessError):
        env["fix.event.schema"].with_user(plain).browse(schema.id).action_publish()


def test_m28_8_topic_retention_must_be_meaningful(env, iadmin):
    Topic = env["fix.event.topic"].with_user(iadmin)
    with pytest.raises(ValidationError):
        Topic.create({"code": "probe.neg", "name": "negative", "retention_days": -5})
    topic = Topic.create({"code": "probe.pos", "name": "positive"})
    with pytest.raises(REFUSED):
        topic.write({"state": "paused"})
    topic.action_pause()
    assert topic.state == "paused"


# --------------------------------------------------------------------------
# M28-5 / P1-6 — the measured log is system-written only


def test_m28_5_users_cannot_forge_the_integration_log(env, plain, iadmin):
    Log = env["fix.integration.log"]
    for user in (plain, iadmin):
        with pytest.raises(AccessError):
            Log.with_user(user).create({"kind": "api", "status": "success", "latency_ms": 5})
    seeded = env["fix.integration.log"].sudo().search([], limit=1)
    if seeded:
        with pytest.raises(AccessError):
            env["fix.integration.log"].with_user(iadmin).browse(seeded.id).write(
                {"status": "success"}
            )


def test_m28_5_server_path_logs_and_links_the_subscription(env, consumer, topic, allowlist):
    sub = _subscription(env, consumer, topic)
    row = env["fix.integration.log"]._log_request(
        kind="webhook",
        status="success",
        consumer=consumer,
        topic_code=topic.code,
        subscription=sub,
        latency_ms=120,
        status_code=200,
    )
    assert row.subscription_id == sub and row.status == "success"


def test_m28_12_webhook_report_matches_attempts_on_the_subscription(
    env, consumer, topic, allowlist
):
    other_topic = env["fix.event.topic"].create({"code": "probe.other", "name": "Other"})
    sub_a = _subscription(env, consumer, topic)
    sub_b = _subscription(env, consumer, other_topic)
    Log = env["fix.integration.log"]
    for _ in range(3):
        Log._log_request(kind="webhook", status="success", subscription=sub_b)
    Log._log_request(kind="webhook", status="failed", subscription=sub_b)
    from odoo.addons.cd_p03_portal.controllers.a12 import m28 as m28_ctrl

    pack = m28_ctrl.webhook_success(env)
    by_name = {r["subscription"]: r for r in pack["rows"]}
    # consumer_id is the SAME for both subscriptions: the old consumer match
    # would have counted 4 attempts on each. The subscription link does not.
    assert by_name[sub_a.name]["attempts"] == 0
    assert by_name[sub_b.name]["attempts"] == 4
    assert by_name[sub_b.name]["success"] == 3


# --------------------------------------------------------------------------
# M28-7 / M28-9 — conflict resolution and connector health are privileged


def _conflict(env):
    # P1-6 completion: a resolution now APPLIES the chosen value, so the
    # target must exist (a dangling target refuses - see
    # test_a12_p16_completion.test_p16_resolve_refuses_when_target_gone).
    partner = env["res.partner"].create(
        {"name": "M28 Conflict Target", "phone": "+8801700000000"}
    )
    return env["fix.sync.conflict"].create(
        {
            "device_ref": "PROBE-DEV-1",
            "res_model": "res.partner",
            "res_id": partner.id,
            "field_name": "phone",
            "local_value": "+8801700000001",
            "remote_value": "+8801700000002",
        }
    )


def test_m28_7_conflict_resolution_privileged_and_frozen(env, plain, iadmin):
    conflict = _conflict(env)
    with pytest.raises(AccessError):
        env["fix.sync.conflict"].with_user(plain).browse(conflict.id).action_local_wins()
    env["fix.sync.conflict"].with_user(iadmin).browse(conflict.id).action_remote_wins()
    assert conflict.resolution == "remote_wins"
    # resolved is final: neither the action nor a direct write changes it
    # (the direct writes run as the integration admin, NOT the superuser -
    # the guard trusts server code by design)
    with pytest.raises(REFUSED):
        env["fix.sync.conflict"].with_user(iadmin).browse(conflict.id).action_local_wins()
    with pytest.raises(REFUSED):
        env["fix.sync.conflict"].with_user(iadmin).browse(conflict.id).write(
            {"resolution": "merged"}
        )
    with pytest.raises(REFUSED):
        env["fix.sync.conflict"].with_user(iadmin).browse(conflict.id).write(
            {"local_value": "+8801700000003"}
        )
    audit = (
        env["fix.security.audit"]
        .sudo()
        .search([("detail", "ilike", "%integration.sync_conflict_resolved%")])
    )
    assert audit


def test_m28_9_connector_health_is_measured_not_typed(env, plain, iadmin):
    connector = env["fix.connector"].create({"name": "bKash probe", "connector_type": "payment"})
    with pytest.raises(REFUSED):
        env["fix.connector"].with_user(iadmin).browse(connector.id).write(
            {"state": "live", "last_latency_ms": 12}
        )
    with pytest.raises(AccessError):
        env["fix.connector"].with_user(plain).browse(connector.id).action_mark_live()
    env["fix.connector"].with_user(iadmin).browse(connector.id).action_mark_live()
    assert connector.state == "live"


def test_m28_10_credential_secret_must_be_vault(env):
    with pytest.raises(ValidationError):
        env["fix.connector.credential"].create(
            {"name": "raw", "secret_ref": "bkash-live-secret-value"}
        )
    ok = env["fix.connector.credential"].create(
        {"name": "vaulted", "secret_ref": "vault://secrets/bkash"}
    )
    assert ok.secret_ref.startswith("vault://")


# --------------------------------------------------------------------------
# R4 / M28-11 — surface whitelists and buttons


def test_m28_11_every_surface_declares_its_writable_whitelist():
    from odoo.addons.cd_p03_portal.controllers.a12 import m28 as m28_ctrl

    assert set(m28_ctrl.WRITABLE) == set(m28_ctrl.SURFACES)
    for model, writable in m28_ctrl.WRITABLE.items():
        assert not ({"state", "resolution"} & set(writable)), model
    assert m28_ctrl.WRITABLE["fix.integration.log"] == ()
    assert m28_ctrl.WRITABLE["fix.event.dlq"] == ()


def test_m28_11_every_js_button_is_whitelisted():
    from odoo.addons.cd_p03_portal.controllers.a12 import m28 as m28_ctrl

    js = (Path(m28_ctrl.__file__).parents[2] / "static" / "src" / "a12" / "m28.js").read_text(
        encoding="utf-8"
    )
    used = set(re.findall(r"m:\s*'(action_[a-z_]+)'", js))
    declared = set()
    for conf in m28_ctrl.SURFACES.values():
        declared |= set(conf["actions"])
    assert used <= declared, "buttons without a surface action whitelist: %s" % (
        sorted(used - declared)
    )
    assert {"action_pause", "action_resume"} <= m28_ctrl.SURFACES["fix.event.topic"]["actions"]
