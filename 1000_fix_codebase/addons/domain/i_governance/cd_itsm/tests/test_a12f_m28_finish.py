"""A12 finish build: M28 controls and workflows, walked as real non-admin users.

Each test names its finding. The walks go through the same controllers the screen
calls (/p03/model/write, action, form, records, report), with the kwargs m28.js
sends. No test reaches a network: the HTTP call is replaced at its one seam.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
import types
from datetime import timedelta
from pathlib import Path

import pytest
from odoo import fields
from odoo.addons.cd_itsm.models import fix_integration as integration
from odoo.addons.cd_itsm.models import fix_integration_dispatch as dispatch
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py import fix_api_edge as edge

REFUSED = (UserError, ValidationError, AccessError)
IADMIN = "cd_itsm.group_integration_admin"
ALLOW_KEY = "fix.integration.webhook_allowlist"
DISPATCH_KEY = "fix.integration.dispatch_enabled"
HOST = "hooks.f28.test"
URL = "https://hooks.f28.test/in"
LOCAL_URL = "https://localhost:9443/in"
SECRET_REF = "vault://webhooks/f28/v1"
SECRET_ENV = "FIX_VAULT_WEBHOOKS_F28_V1"
SECRET_VALUE = "local-test-signing-value"


class Ctx:
    pass


def _user(env, login, groups=()):
    gids = [env.ref("base.group_user").id] + [env.ref(x).id for x in groups]
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create({"name": login, "login": login, "group_ids": [(6, 0, gids)]})
    )
    env["hr.employee"].create({"name": login, "user_id": user.id})
    return user


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    env["ir.config_parameter"].sudo().search([("key", "=", ALLOW_KEY)]).unlink()
    env["ir.config_parameter"].sudo().search([("key", "=", DISPATCH_KEY)]).unlink()
    x = Ctx()
    x.env = env
    x.plain = _user(env, "f28f_plain")
    x.admin1 = _user(env, "f28f_admin1", [IADMIN])
    x.admin2 = _user(env, "f28f_admin2", [IADMIN])
    x.admin3 = _user(env, "f28f_admin3", [IADMIN])
    return x


@pytest.fixture
def p03(c):
    import odoo.addons.cd_p03_portal.controllers.a12 as a12mod
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g
    import odoo.addons.cd_p03_portal.controllers.p03_service_order_api as s

    ctl = g.P03GenericApiController()
    plat = a12mod.P03PlatformApi()

    def _o(fn):
        return getattr(fn, "original_endpoint", fn)

    C = g.P03GenericApiController
    saved = (g.request, s.request, a12mod.request)

    def as_user(user):
        req = types.SimpleNamespace(env=c.env(user=user.id))
        g.request = req
        s.request = req
        a12mod.request = req

    try:
        yield types.SimpleNamespace(
            write=lambda **k: _o(C.model_write)(ctl, **k),
            action=lambda **k: _o(C.model_action)(ctl, **k),
            records=lambda **k: _o(C.model_records)(ctl, **k),
            form=lambda **k: _o(C.model_form)(ctl, **k),
            report=lambda **k: _o(C.model_report)(ctl, **k),
            kpis=lambda **k: _o(a12mod.P03PlatformApi.platform_kpis)(plat, **k),
            as_user=as_user,
        )
    finally:
        g.request, s.request, a12mod.request = saved


@pytest.fixture
def http(monkeypatch):
    """The dispatcher's only way out. Answers `code`, records what it was sent."""
    box = types.SimpleNamespace(calls=[], code=200, error=None)

    def fake(url, body, headers, timeout):
        box.calls.append(types.SimpleNamespace(url=url, body=body, headers=headers))
        if box.error:
            raise box.error
        return box.code

    monkeypatch.setattr(dispatch, "_http_post", fake)
    monkeypatch.setenv(SECRET_ENV, SECRET_VALUE)
    monkeypatch.setenv("FIX_ENV", "local")
    return box


def attempt(env, fn):
    try:
        with env.cr.savepoint():
            fn()
        return None
    except REFUSED as exc:
        return str(exc)


def allow(c, hosts=HOST):
    c.env["ir.config_parameter"].sudo().set_param(ALLOW_KEY, hosts)


def enable_dispatch(c):
    c.env["ir.config_parameter"].sudo().set_param(DISPATCH_KEY, "1")


def consumer(c, **kw):
    vals = {"name": "F28 Consumer", "key_ref": "vault://keys/f28/v1"}
    vals.update(kw)
    return c.env["fix.api.consumer"].sudo().create(vals)


def topic(c, code="f28.topic", **kw):
    vals = {"code": code, "name": code}
    vals.update(kw)
    return c.env["fix.event.topic"].sudo().create(vals)


def subscription(c, code="f28.topic", url=URL, **kw):
    allow(c, kw.pop("hosts", HOST))
    vals = {
        "consumer_id": consumer(c).id,
        "topic_id": topic(c, code).id,
        "endpoint_url": url,
        "secret_ref": SECRET_REF,
    }
    vals.update(kw)
    sub = c.env["fix.event.subscription"].sudo().create(vals)
    # Already past go-live: test_a12f_m28_second_pass walks that decision.
    sub._guarded().write({"approval_state": "approved"})
    return sub


def emit(c, code="f28.topic", payload=None):
    return c.env["fix.event.outbox"].sudo().emit(code, "x", 1, payload or {"a": 1})


def audits(c, event):
    return c.env["fix.security.audit"].sudo().search_count([("event", "=", event)])


def decide(c, record, user):
    """Approve through the M63 inbox task, as the screen does."""
    task = (
        c.env["fix.workflow.task"]
        .sudo()
        .search([("request_id", "=", record.approval_request_id.id), ("state", "!=", "done")])
    )
    assert task, "no open task on %s" % record.display_name
    target = task.filtered(lambda t: t.assigned_user_id == user)
    assert target, "the task did not route to %s" % user.login
    target.with_user(user).action_approve(comment="checked")


# ==================================================== N-M28-1 sync resolution
def _conflict(c, **kw):
    partner = c.env["res.partner"].sudo().create({"name": "F28", "phone": "+880-server"})
    vals = {
        "device_ref": "DEV-1",
        "res_model": "res.partner",
        "res_id": partner.id,
        "field_name": "phone",
        "local_value": "+880-device",
        "remote_value": "+880-server",
    }
    vals.update(kw)
    return c.env["fix.sync.conflict"].sudo().create(vals), partner


def test_a12f_n_m28_1_conflict_cannot_be_repointed_at_a_config_parameter(c, p03):
    conflict, _partner = _conflict(c)
    param = c.env["ir.config_parameter"].sudo().create({"key": "f28.safe", "value": "original"})
    p03.as_user(c.admin1)
    out = p03.write(
        model="fix.sync.conflict",
        record_id=conflict.id,
        values={"res_model": "ir.config_parameter", "res_id": param.id, "field_name": "value"},
    )
    assert "error" in out, out
    assert conflict.res_model == "res.partner"
    assert attempt(
        c.env,
        lambda: conflict.with_user(c.admin1).write({"res_model": "ir.config_parameter"}),
    )


@pytest.mark.parametrize(
    "model,field",
    [
        ("ir.config_parameter", "value"),
        ("res.users", "login"),
        ("res.groups", "name"),
        ("ir.cron", "code"),
        ("product.product", "standard_price"),
    ],
)
def test_a12f_n_m28_1_resolution_never_reaches_a_target_off_the_list(c, model, field):
    # A row that got there by any path, as if raised by the engine.
    param = c.env["ir.config_parameter"].sudo().create({"key": "f28.safe", "value": "original"})
    conflict, _partner = _conflict(
        c, res_model=model, res_id=param.id, field_name=field, local_value="pwned"
    )
    assert conflict.policy_class == "denied"
    for action in ("action_local_wins", "action_remote_wins"):
        assert attempt(c.env, lambda a=action: getattr(conflict.with_user(c.admin1), a)())
    assert attempt(c.env, lambda: conflict.with_user(c.admin1).action_merged(note="done"))
    assert conflict.resolution == "pending"
    param.invalidate_recordset()
    assert param.value == "original"
    # It can only be closed, with nothing applied.
    conflict.with_user(c.admin1).action_dismiss(note="off the sync allow-list")
    assert conflict.resolution == "dismissed"
    param.invalidate_recordset()
    assert param.value == "original"


def test_a12f_n_m28_2_conflict_is_not_typed_on_the_screen(c, p03):
    p03.as_user(c.admin1)
    out = p03.write(
        model="fix.sync.conflict",
        values={"device_ref": "X", "res_model": "res.partner", "res_id": 1, "field_name": "phone"},
    )
    assert "error" in out, out
    assert attempt(
        c.env,
        lambda: c.env["fix.sync.conflict"]
        .with_user(c.admin1)
        .create(
            {"device_ref": "X", "res_model": "res.partner", "res_id": 1, "field_name": "phone"}
        ),
    )


def test_a12f_n_m28_2_local_wins_refuses_to_blank_the_target(c):
    conflict, partner = _conflict(c, local_value=False)
    assert attempt(c.env, lambda: conflict.with_user(c.admin1).action_local_wins())
    partner.invalidate_recordset()
    assert partner.phone == "+880-server"
    assert conflict.resolution == "pending"


def test_a12f_m28_7_partner_with_a_login_is_not_a_sync_target(c):
    partner = c.plain.partner_id
    conflict, _partner = _conflict(c, res_id=partner.id)
    assert attempt(c.env, lambda: conflict.with_user(c.admin1).action_local_wins())


def test_a12f_m28_7_client_field_takes_the_device_value_and_audits(c, p03):
    conflict, partner = _conflict(c)
    assert conflict.policy_class == "client"
    before = audits(c, "integration.sync_conflict_resolved")
    p03.as_user(c.admin1)
    out = p03.action(model="fix.sync.conflict", ids=[conflict.id], method="action_local_wins")
    assert out.get("success"), out
    partner.invalidate_recordset()
    assert partner.phone == "+880-device"
    assert conflict.resolved_by_id == c.admin1
    assert audits(c, "integration.sync_conflict_resolved") == before + 1


def test_a12f_m28_7_server_field_keeps_the_server_value(c):
    order_like = c.env["res.partner"].sudo().create({"name": "F28", "ref": "server-ref"})
    conflict, _partner = _conflict(
        c, res_id=order_like.id, field_name="ref", local_value="device-ref", remote_value="server"
    )
    assert conflict.policy_class == "server"
    assert attempt(c.env, lambda: conflict.with_user(c.admin1).action_local_wins())
    assert attempt(c.env, lambda: conflict.with_user(c.admin1).action_merged(note="by hand"))
    conflict.with_user(c.admin1).action_remote_wins()
    order_like.invalidate_recordset()
    # The server's value already stands: a state changes through its own workflow.
    assert order_like.ref == "server-ref"
    assert conflict.resolution == "remote_wins"


def test_a12f_m28_7_merged_needs_a_stated_reconciliation(c):
    conflict, partner = _conflict(c)
    assert attempt(c.env, lambda: conflict.with_user(c.admin1).action_merged())
    conflict.with_user(c.admin1).action_merged(note="agreed with the customer")
    partner.invalidate_recordset()
    assert partner.phone == "+880-server"
    assert conflict.resolution_note == "agreed with the customer"


def test_a12f_m28_7_the_offline_engine_feeds_the_register(c):
    """Through the method offline_sync_api calls when it records a conflict_applied."""
    if "fix.offline.idempotency.ledger" not in c.env:
        pytest.skip("cd_field_service not installed")
    c.env["fix.offline.idempotency.ledger"].sudo().record_execution(
        command_id="f28-cmd-1",
        technician_id=False,
        device_id="DEV-9",
        model="fix.field.order",
        record_id=12,
        operation="start_order",
        payload_hash="x",
        status="conflict_applied",
        response_dict={"order_id": 12, "state": "in_progress"},
        conflict_reason="Order was already marked in_progress on server",
    )
    Conflict = c.env["fix.sync.conflict"].sudo()
    assert Conflict.cron_ingest_ledger_conflicts() >= 1
    row = Conflict.search([("source_command_id", "=", "f28-cmd-1")])
    assert row.res_model == "fix.field.order" and row.res_id == 12
    assert row.device_ref == "DEV-9" and row.field_name == "state"
    assert row.remote_value == "in_progress" and row.policy_class == "server"
    assert Conflict.cron_ingest_ledger_conflicts() == 0, "raised twice"
    cron = c.env.ref("cd_itsm.ir_cron_sync_conflict_ingest")
    assert cron.active and "cron_ingest_ledger_conflicts" in cron.code


# ==================================================== M28-1 connector endpoint
def test_a12f_m28_1_connector_endpoint_obeys_the_host_rule(c):
    allow(c, "tokenized.pay.bka.sh")
    Connector = c.env["fix.connector"].with_user(c.admin1)
    assert attempt(c.env, lambda: Connector.create({"name": "x", "endpoint": "http://x.test"}))
    assert attempt(c.env, lambda: Connector.create({"name": "x", "endpoint": "https://x.test"}))
    assert attempt(
        c.env,
        lambda: Connector.create(
            {"name": "x", "endpoint": "https://user:pw@tokenized.pay.bka.sh/a"}
        ),
    )
    cred = (
        c.env["fix.connector.credential"]
        .with_user(c.admin1)
        .create({"name": "bKash", "secret_ref": "vault://x/1"})
    )
    conn = Connector.create(
        {
            "name": "bKash",
            "connector_type": "payment",
            "endpoint": "https://tokenized.pay.bka.sh",
            "credential_id": cred.id,
        }
    )
    assert attempt(c.env, lambda: conn.write({"endpoint": "http://attacker.example.net"}))
    assert attempt(c.env, lambda: conn.write({"endpoint": "https://attacker.example.net"}))
    assert conn.endpoint == "https://tokenized.pay.bka.sh"


def test_a12f_m28_1_connector_repoint_is_audited(c):
    allow(c, "a.test b.test")
    conn = (
        c.env["fix.connector"]
        .with_user(c.admin1)
        .create({"name": "C", "endpoint": "https://a.test"})
    )
    before = audits(c, "integration.connector_repointed")
    conn.write({"endpoint": "https://b.test"})
    assert audits(c, "integration.connector_repointed") == before + 1


def test_a12f_m28_1_a_connector_registered_earlier_can_still_be_renamed(c, p03):
    conn = c.env["fix.connector"].sudo().create({"name": "Old", "endpoint": "https://off.list"})
    p03.as_user(c.admin1)
    out = p03.write(
        model="fix.connector",
        record_id=conn.id,
        values={"name": "New", "endpoint": "https://off.list"},
    )
    assert "error" not in out, out
    assert conn.name == "New"


def test_a12f_m28_1_off_list_subscription_is_paused_by_the_cron(c):
    sub = subscription(c)
    c.env["ir.config_parameter"].sudo().search([("key", "=", ALLOW_KEY)]).unlink()
    Sub = c.env["fix.event.subscription"].sudo()
    assert Sub.cron_revalidate_subscriptions() >= 1
    assert sub.state == "paused"
    assert "allow-list" in sub.pause_reason
    assert c.env.ref("cd_itsm.ir_cron_webhook_revalidate").active


# ==================================================== M28-2 API governance
def test_a12f_m28_2_quota_increase_takes_a_second_admin(c, p03):
    cons = consumer(c)
    p03.as_user(c.admin1)
    made = p03.write(
        model="fix.api.quota",
        values={"consumer_id": cons.id, "requests_per_min": 30, "daily_quota": 100},
    )
    assert "error" not in made, made
    quota = c.env["fix.api.quota"].browse(made["id"])
    # the screen's plain save refuses a raise, and the row is untouched
    out = p03.write(model="fix.api.quota", record_id=quota.id, values={"requests_per_min": 1000000})
    assert "error" in out, out
    assert quota.requests_per_min == 30
    # the button, with the kwargs m28.js sends
    out = p03.action(
        model="fix.api.quota",
        ids=[quota.id],
        method="action_request_increase",
        kwargs={"requests_per_min": 90, "daily_quota": 500, "justification": "partner launch"},
    )
    assert out.get("success"), out
    assert quota.approval_state == "pending" and quota.requests_per_min == 30
    # the requester cannot decide his own; a colleague does
    tasks = (
        c.env["fix.workflow.task"]
        .sudo()
        .search([("request_id", "=", quota.approval_request_id.id)])
    )
    assert c.admin1 not in tasks.mapped("assigned_user_id")
    decide(c, quota, c.admin2)
    assert quota.requests_per_min == 90 and quota.daily_quota == 500
    assert quota.approval_state == "approved"
    assert audits(c, "integration.quota_changed") >= 1


def test_a12f_m28_2_quota_can_go_down_directly_with_an_audit_row(c):
    quota = (
        c.env["fix.api.quota"]
        .with_user(c.admin1)
        .create({"consumer_id": consumer(c).id, "requests_per_min": 30})
    )
    before = audits(c, "integration.quota_changed")
    quota.write({"requests_per_min": 10})
    assert quota.requests_per_min == 10
    assert audits(c, "integration.quota_changed") == before + 1


def test_a12f_m28_2_no_quota_is_born_above_the_ceiling_or_deleted_by_hand(c):
    Quota = c.env["fix.api.quota"].with_user(c.admin1)
    cons = consumer(c)
    assert attempt(
        c.env, lambda: Quota.create({"consumer_id": cons.id, "requests_per_min": 999999})
    )
    quota = Quota.create({"consumer_id": cons.id})
    assert attempt(c.env, lambda: quota.unlink())


def test_a12f_m28_2_endpoint_goes_public_only_through_a_second_admin(c, p03):
    p03.as_user(c.admin1)
    made = p03.write(
        model="fix.api.endpoint",
        values={
            "code": "WC",
            "name": "WC",
            "version": "v1",
            "path": "/wc",
            "method": "GET",
            "auth_type": "api_key",
        },
    )
    assert "error" not in made, made
    endpoint = c.env["fix.api.endpoint"].browse(made["id"])
    out = p03.write(model="fix.api.endpoint", record_id=endpoint.id, values={"auth_type": "none"})
    assert "error" in out, out
    assert endpoint.auth_type == "api_key"
    born_public = p03.write(
        model="fix.api.endpoint",
        values={
            "code": "WD",
            "name": "WD",
            "version": "v1",
            "path": "/wd",
            "method": "GET",
            "auth_type": "none",
        },
    )
    assert "error" in born_public, born_public
    out = p03.action(
        model="fix.api.endpoint",
        ids=[endpoint.id],
        method="action_request_public",
        kwargs={"justification": "warranty lookup is public by design"},
    )
    assert out.get("success"), out
    assert endpoint.auth_type == "api_key"
    before = audits(c, "integration.endpoint_auth_changed")
    decide(c, endpoint, c.admin2)
    assert endpoint.auth_type == "none"
    assert audits(c, "integration.endpoint_auth_changed") == before + 1


def test_a12f_m28_2_key_ref_is_set_at_registration_then_only_rotated(c, p03):
    p03.as_user(c.admin1)
    made = p03.write(
        model="fix.api.consumer", values={"name": "New", "key_ref": "vault://keys/new/v1"}
    )
    assert "error" not in made, made
    cons = c.env["fix.api.consumer"].browse(made["id"])
    assert cons.key_ref == "vault://keys/new/v1"
    out = p03.write(
        model="fix.api.consumer", record_id=cons.id, values={"key_ref": "vault://attacker/v9"}
    )
    assert "error" in out, out
    assert attempt(
        c.env, lambda: cons.with_user(c.admin1).write({"key_ref": "vault://attacker/v9"})
    )
    assert cons.key_ref == "vault://keys/new/v1"
    out = p03.action(model="fix.api.consumer", ids=[cons.id], method="action_rotate_key")
    assert out.get("success"), out
    assert cons.key_ref == "vault://keys/new/v2"


def test_a12f_n_m28_3_consumer_with_no_key_gets_one_from_the_screen(c, p03):
    p03.as_user(c.admin1)
    made = p03.write(model="fix.api.consumer", values={"name": "No Key"})
    cons = c.env["fix.api.consumer"].browse(made["id"])
    assert not cons.key_ref
    refused = p03.action(model="fix.api.consumer", ids=[cons.id], method="action_rotate_key")
    assert not refused.get("success") and "Issue Key" in refused["error"]
    # Y05: a key follows registration, which a second admin decides.
    out = p03.action(
        model="fix.api.consumer",
        ids=[cons.id],
        method="action_request_registration",
        kwargs={"justification": "partner launch"},
    )
    assert out.get("success"), out
    decide(c, cons, c.admin2)
    before = audits(c, "integration.key_issued")
    out = p03.action(model="fix.api.consumer", ids=[cons.id], method="action_issue_key")
    assert out.get("success"), out
    assert cons.key_ref == "vault://keys/consumer-%d/v1" % cons.id
    assert audits(c, "integration.key_issued") == before + 1
    again = p03.action(model="fix.api.consumer", ids=[cons.id], method="action_issue_key")
    assert not again.get("success")


def test_a12f_m28_2_vault_namespace_list_applies_when_set(c):
    Consumer = c.env["fix.api.consumer"].with_user(c.admin1)
    Consumer.create({"name": "any", "key_ref": "vault://anything/v1"})
    c.env["ir.config_parameter"].sudo().set_param(integration.VAULT_NAMESPACES_KEY, "keys, secrets")
    assert attempt(c.env, lambda: Consumer.create({"name": "x", "key_ref": "vault://other/v1"}))
    assert attempt(c.env, lambda: Consumer.create({"name": "x", "key_ref": "vault://keys/../v1"}))
    Consumer.create({"name": "ok", "key_ref": "vault://keys/ok/v1"})


# ==================================================== M28-3 webhook dispatcher
def run_dispatch(c):
    return c.env["fix.webhook.delivery"].sudo().cron_dispatch_webhooks()


def deliveries(c, sub):
    return c.env["fix.webhook.delivery"].sudo().search([("subscription_id", "=", sub.id)])


def weblogs(c, sub):
    return (
        c.env["fix.integration.log"]
        .sudo()
        .search([("kind", "=", "webhook"), ("subscription_id", "=", sub.id)])
    )


def test_a12f_m28_3_cron_record_exists_and_refuses_a_user(c):
    cron = c.env.ref("cd_itsm.ir_cron_webhook_dispatch")
    assert cron.active and "cron_dispatch_webhooks" in cron.code
    assert attempt(
        c.env, lambda: c.env["fix.webhook.delivery"].with_user(c.admin1).cron_dispatch_webhooks()
    )


def test_a12f_m28_3_dispatch_off_records_a_truthful_not_sent(c, http):
    sub = subscription(c)
    emit(c)
    run_dispatch(c)
    assert not http.calls, "HTTP left the system with dispatch off"
    row = deliveries(c, sub)
    assert row.state == "not_sent" and row.attempts == 0
    assert row.last_outcome == "not sent: dispatch disabled"
    log = weblogs(c, sub)
    assert len(log) == 1 and log.status == "not_sent" and log.measured
    assert log.outcome == "not sent: dispatch disabled"
    # one row, not one per minute
    run_dispatch(c)
    assert len(weblogs(c, sub)) == 1


def test_a12f_m28_3_de11_local_environment_never_reaches_a_non_local_host(c, http):
    sub = subscription(c)
    enable_dispatch(c)
    emit(c)
    run_dispatch(c)
    assert not http.calls
    assert deliveries(c, sub).last_outcome.startswith("not sent: DE-11")


def test_a12f_m28_3_signed_send_to_a_local_host_per_the_guide(c, http):
    sub = subscription(c, url=LOCAL_URL, hosts="localhost")
    enable_dispatch(c)
    event = emit(c, payload={"a": 1, "নাম": "গ্রাহক"})
    run_dispatch(c)
    assert len(http.calls) == 1
    call = http.calls[0]
    assert call.url == LOCAL_URL
    assert call.headers["webhook-id"] == event.event_id
    assert call.headers["content-type"] == "application/json; charset=utf-8"
    signed = ("%s.%s." % (event.event_id, call.headers["webhook-timestamp"])).encode() + call.body
    want = base64.b64encode(hmac.new(SECRET_VALUE.encode(), signed, hashlib.sha256).digest())
    assert call.headers["webhook-signature"] == "v1,%s" % want.decode()
    assert json.loads(call.body)["payload"]["নাম"] == "গ্রাহক"
    assert SECRET_VALUE not in json.dumps(dict(call.headers))
    row = deliveries(c, sub)
    assert row.state == "sent" and row.attempts == 1 and row.last_status_code == 200
    log = weblogs(c, sub)
    assert log.status == "success" and log.status_code == 200 and log.measured


def test_a12f_m28_3_a_secret_that_cannot_be_read_sends_nothing(c, http, monkeypatch):
    monkeypatch.delenv(SECRET_ENV)
    sub = subscription(c, url=LOCAL_URL, hosts="localhost")
    enable_dispatch(c)
    emit(c)
    run_dispatch(c)
    assert not http.calls
    assert "signing secret unavailable" in deliveries(c, sub).last_outcome


def test_a12f_m28_3_host_is_rechecked_at_send_time(c, http):
    sub = subscription(c, url=LOCAL_URL, hosts="localhost")
    enable_dispatch(c)
    emit(c)
    c.env["ir.config_parameter"].sudo().set_param(ALLOW_KEY, "elsewhere.test")
    run_dispatch(c)
    assert not http.calls
    assert sub.state == "paused"
    assert deliveries(c, sub).last_outcome == "not sent: host not on the allow-list"


def test_a12f_m28_3_retries_back_off_then_dead_letter_and_replay(c, http, p03):
    sub = subscription(c, url=LOCAL_URL, hosts="localhost")
    enable_dispatch(c)
    event = emit(c)
    http.code = 503
    run_dispatch(c)
    row = deliveries(c, sub)
    assert row.state == "retry" and row.attempts == 1 and sub.state == "failing"
    assert 25 <= (row.next_attempt_at - fields.Datetime.now()).total_seconds() <= 35
    # not due yet: no second request
    run_dispatch(c)
    assert len(http.calls) == 1
    row.write({"next_attempt_at": fields.Datetime.now() - timedelta(seconds=1)})
    run_dispatch(c)
    assert row.state == "retry" and row.attempts == 2
    assert (row.next_attempt_at - fields.Datetime.now()).total_seconds() > 200
    row.write({"next_attempt_at": fields.Datetime.now() - timedelta(seconds=1)})
    run_dispatch(c)
    assert row.state == "dead" and len(http.calls) == 3
    assert len(weblogs(c, sub).filtered(lambda r: r.status == "failed")) == 3
    # the same event id on every retry: the consumer's idempotency key
    assert {call.headers["webhook-id"] for call in http.calls} == {event.event_id}
    entry = c.env["fix.event.dlq"].sudo().search([("webhook_delivery_id", "=", row.id)])
    assert entry.state == "pending" and entry.origin == "webhook"
    # the DLQ screen replays it, and it really goes out
    http.code = 200
    p03.as_user(c.admin1)
    out = p03.action(
        model="fix.event.dlq",
        ids=[entry.id],
        method="action_replay",
        kwargs={"reason": "endpoint fixed", "otp": ""},
    )
    assert out.get("success"), out
    assert row.state == "pending" and row.attempts == 0
    run_dispatch(c)
    assert row.state == "sent" and sub.state == "active" and sub.consecutive_failures == 0


def test_a12f_m28_3_five_failures_disable_the_endpoint_and_tell_the_admins(c, http, p03):
    """BRU-IPF-18. Later events go to the DLQ, not a queue (AD-03)."""
    sub = subscription(c, url=LOCAL_URL, hosts="localhost")
    enable_dispatch(c)
    http.code = 500
    for _ in range(5):
        emit(c)
    run_dispatch(c)
    assert sub.state == "paused" and sub.auto_disabled and sub.consecutive_failures == 5
    assert audits(c, "integration.webhook_disabled") == 1
    todo = (
        c.env["mail.activity"]
        .sudo()
        .search([("res_model", "=", "fix.event.subscription"), ("res_id", "=", sub.id)])
    )
    assert c.admin1 in todo.mapped("user_id")
    sent = len(http.calls)
    emit(c)
    run_dispatch(c)
    assert len(http.calls) == sent
    assert (
        c.env["fix.event.dlq"]
        .sudo()
        .search_count([("webhook_delivery_id.subscription_id", "=", sub.id)])
    )
    p03.as_user(c.admin1)
    refused = p03.action(model="fix.event.subscription", ids=[sub.id], method="action_resume")
    assert not refused.get("success")
    out = p03.action(
        model="fix.event.subscription",
        ids=[sub.id],
        method="action_resume",
        kwargs={"reason": "their certificate was renewed"},
    )
    assert out.get("success"), out
    assert sub.state == "active" and not sub.auto_disabled and sub.consecutive_failures == 0


def test_a12f_m28_3_no_cross_company_and_no_backfill(c, http):
    old = emit(c, "f28.old")
    sub = subscription(c, code="f28.old", url=LOCAL_URL, hosts="localhost")
    enable_dispatch(c)
    other = c.env["res.company"].sudo().create({"name": "F28 Other"})
    foreign = c.env["fix.event.outbox"].sudo().with_company(other).emit("f28.old", "x", 1, {"b": 2})
    assert foreign.company_id == other
    # Same transaction, so `old` and the subscription share a create date: age it.
    c.env.flush_all()
    c.env.cr.execute(
        "UPDATE fix_event_outbox SET create_date = create_date - interval '1 day' WHERE id=%s",
        (old.id,),
    )
    c.env.invalidate_all()
    run_dispatch(c)
    assert not deliveries(c, sub), "a foreign or older event was queued"


def test_a12f_m28_3_paused_subscription_holds_its_events(c, http):
    sub = subscription(c, url=LOCAL_URL, hosts="localhost")
    enable_dispatch(c)
    sub.with_user(c.admin1).action_pause(reason="their maintenance")
    emit(c)
    run_dispatch(c)
    assert not http.calls and not deliveries(c, sub)
    sub.with_user(c.admin1).action_resume()
    run_dispatch(c)
    assert len(http.calls) == 1


def test_a12f_m28_3_paused_topic_stops_relay_and_webhook_then_resume_delivers(c, http):
    Consumer = c.env["fix.event.consumer"].sudo()
    relay_consumer = Consumer.create(
        {
            "name": "F28 hold",
            "event_type": "f28.topic",
            "model": "fix.itsm.ticket",
            "method": "consume_ticket_created",
            "active_from": fields.Datetime.now() - timedelta(days=1),
        }
    )
    sub = subscription(c, url=LOCAL_URL, hosts="localhost")
    enable_dispatch(c)
    the_topic = sub.topic_id
    the_topic.with_user(c.admin1).action_pause(reason="migration")
    assert the_topic.state == "paused" and the_topic.pause_reason == "migration"
    emit(c)
    Out = c.env["fix.event.outbox"].sudo()
    Out.cron_relay()
    run_dispatch(c)
    Delivery = c.env["fix.event.consumer.delivery"].sudo()
    assert not Delivery.search_count([("subscription_id", "=", relay_consumer.id)])
    assert not http.calls
    the_topic.with_user(c.admin1).action_resume()
    Out.cron_relay()
    run_dispatch(c)
    assert Delivery.search_count([("subscription_id", "=", relay_consumer.id)]) == 1
    assert len(http.calls) == 1


# ==================================================== M28-3 / M28-5 API edge
@pytest.fixture
def edge_env(c, monkeypatch):
    """Serve a decorated route with a real request environment, logging into the test
    transaction instead of a cursor of its own."""
    import contextlib

    @contextlib.contextmanager
    def same_env():
        yield c.env

    monkeypatch.setattr(edge, "_log_environment", same_env)

    def bind(user):
        monkeypatch.setattr(
            edge,
            "request",
            types.SimpleNamespace(
                env=c.env(user=user.id),
                make_json_response=lambda body, status=200: types.SimpleNamespace(
                    status_code=status, body=body
                ),
            ),
        )

    return bind


def _partner_consumer(c, user, **kw):
    return consumer(c, partner_id=user.partner_id.id, **kw)


def test_a12f_m28_3_edge_logs_a_real_request_against_its_consumer(c, edge_env):
    edge_env(c.plain)
    cons = _partner_consumer(c, c.plain)
    endpoint = (
        c.env["fix.api.endpoint"].sudo().create({"code": "E", "name": "E", "path": "/f28/route"})
    )
    route = edge.api_edge("/f28/route")(lambda *a, **k: {"ok": True})
    assert route() == {"ok": True}
    log = c.env["fix.integration.log"].sudo().search([("consumer_id", "=", cons.id)])
    assert len(log) == 1 and log.measured and log.status == "success"
    assert log.endpoint_id == endpoint and log.route == "/f28/route"
    assert log.latency_ms is not False


def test_a12f_m28_3_edge_throttles_on_the_measured_quota(c, edge_env):
    edge_env(c.plain)
    cons = _partner_consumer(c, c.plain)
    c.env["fix.api.quota"].sudo().create(
        {"consumer_id": cons.id, "requests_per_min": 2, "daily_quota": 100}
    )
    served = []
    route = edge.api_edge("/f28/route")(lambda *a, **k: served.append(1) or {"ok": True})
    route()
    route()
    third = route()
    assert third["error"]["code"] == "rate_limited" and len(served) == 2
    rows = c.env["fix.integration.log"].sudo().search([("consumer_id", "=", cons.id)])
    assert sorted(rows.mapped("status")) == ["success", "success", "throttled"]
    # the quota screen's cron reads the same measured rows
    c.env["fix.api.quota"].sudo().cron_enforce_quotas()
    assert (
        c.env["fix.api.quota"].sudo().search([("consumer_id", "=", cons.id)]).state == "throttled"
    )


def test_a12f_m28_3_edge_answers_an_http_route_with_a_real_429(c, edge_env):
    edge_env(c.plain)
    cons = _partner_consumer(c, c.plain)
    c.env["fix.api.quota"].sudo().create({"consumer_id": cons.id, "requests_per_min": 1})
    route = edge.api_edge("/f28/http", http_route=True)(
        lambda *a, **k: types.SimpleNamespace(status_code=200)
    )
    assert route().status_code == 200
    assert route().status_code == 429


def test_a12f_m28_3_edge_logs_a_failure_and_lets_it_raise(c, edge_env):
    edge_env(c.plain)
    cons = _partner_consumer(c, c.plain)

    def boom(*a, **k):
        raise UserError("no")

    with pytest.raises(UserError):
        edge.api_edge("/f28/route")(boom)()
    assert (
        c.env["fix.integration.log"].sudo().search([("consumer_id", "=", cons.id)]).status
        == "failed"
    )
    refused = edge.api_edge("/f28/route")(lambda: {"error": {"code": "forbidden"}})
    assert refused()["error"]["code"] == "forbidden"
    rows = c.env["fix.integration.log"].sudo().search([("consumer_id", "=", cons.id)])
    assert rows.mapped("status") == ["failed", "failed"]


def test_a12f_m28_3_edge_never_takes_a_route_down(c, edge_env, monkeypatch):
    edge_env(c.plain)

    def broken(*a, **k):
        raise RuntimeError("gate down")

    monkeypatch.setattr(edge, "_resolve", broken)
    assert edge.api_edge("/f28/route")(lambda: {"ok": 1})() == {"ok": 1}


def test_a12f_m28_3_edge_with_no_request_just_serves(c, monkeypatch):
    monkeypatch.setattr(edge, "request", None)
    assert edge.api_edge("/f28/route")(lambda: {"ok": 1})() == {"ok": 1}


@pytest.mark.parametrize(
    "module,routes",
    [
        (
            "odoo.addons.cd_warranty_claims.controllers.brand_api",
            {"claims", "claim_status", "claim_webhook", "reconciliation"},
        ),
        (
            "odoo.addons.cd_storefront.controllers.storefront_api",
            {"catalogue", "get_or_update_cart", "checkout", "track_order", "payment_callback"},
        ),
        ("odoo.addons.cd_field_service.controllers.offline_sync_api", {"offline_sync"}),
    ],
)
def test_a12f_m28_3_external_routes_carry_the_edge(module, routes):
    import importlib
    import inspect

    mod = importlib.import_module(module)
    source = inspect.getsource(mod)
    assert "api_edge(" in source
    for name in routes:
        found = re.search(r"@api_edge\([^\n]*\)\n    def %s\(" % name, source)
        assert found, "%s has no api_edge" % name


# ==================================================== M28-5 honest reports
def _seed_row(c, **kw):
    vals = {"kind": "api", "status": "success", "latency_ms": 5}
    vals.update(kw)
    return c.env["fix.integration.log"].sudo().create(vals)


def test_a12f_m28_5_seed_rows_are_not_traffic(c, p03):
    Log = c.env["fix.integration.log"]
    before = Log.sudo().search_count([("measured", "=", True), ("kind", "=", "api")])
    _seed_row(c)
    assert not _seed_row(c).measured
    p03.as_user(c.admin1)
    out = p03.report(module="M28", report="api_usage")
    assert sum(r["requests"] for r in out["rows"]) == before
    assert any("seed row(s)" in n for n in out["notes"])
    if not before:
        assert out["rows"] == [] and "No measured traffic" in out["empty"]
    # a measured row counts
    cons = consumer(c)
    Log.sudo()._log_request("api", consumer=cons, latency_ms=7)
    out = p03.report(module="M28", report="api_usage")
    assert cons.name in [r["consumer"] for r in out["rows"]]


def test_a12f_m28_5_seed_rows_do_not_move_a_quota_or_a_consumer_count(c):
    cons = consumer(c)
    quota = c.env["fix.api.quota"].sudo().create({"consumer_id": cons.id, "requests_per_min": 1})
    _seed_row(c, consumer_id=cons.id)
    assert c.env["fix.api.quota"].sudo().check_request_allowed(cons)["allowed"]
    c.env["fix.api.quota"].sudo().cron_enforce_quotas()
    assert quota.state == "active"
    cons.invalidate_recordset()
    assert cons.request_count == 0


def test_a12f_m28_5_context_key_no_longer_opens_the_log(c):
    Log = c.env["fix.integration.log"].with_user(c.admin1)
    assert attempt(
        c.env,
        lambda: Log.with_context(fix_integration_log_service=True).create({"kind": "api"}),
    )


def test_a12f_m28_5_delivery_slo_counts_real_relay_deliveries(c, p03):
    Consumer = c.env["fix.event.consumer"].sudo()
    Consumer.create(
        {
            "name": "F28 slo",
            "event_type": "f28.slo",
            "model": "fix.itsm.ticket",
            "method": "consume_ticket_created",
            "active_from": fields.Datetime.now() - timedelta(days=1),
        }
    )
    emit(c, "f28.slo")
    c.env["fix.event.outbox"].sudo().cron_relay()
    p03.as_user(c.admin1)
    out = p03.report(module="M28", report="event_delivery_slo")
    assert "f28.slo" in [r["topic"] for r in out["rows"]]


def test_a12f_m28_5_webhook_report_says_dispatch_is_off(c, http, p03):
    sub = subscription(c)
    emit(c)
    run_dispatch(c)
    p03.as_user(c.admin1)
    out = p03.report(module="M28", report="webhook_success")
    row = next(r for r in out["rows"] if r["subscription"] == sub.name)
    assert row["attempts"] == 0 and row["not_sent"] == 1 and row["rate"] is None
    assert any("Dispatch is off" in n for n in out["notes"])


def test_a12f_n_m28_9_offline_screen_is_its_own_report(c, p03):
    if "fix.offline.idempotency.ledger" not in c.env:
        pytest.skip("cd_field_service not installed")
    c.env["fix.offline.idempotency.ledger"].sudo().record_execution(
        command_id="f28-cmd-2",
        technician_id=False,
        device_id="D",
        model="fix.field.order",
        record_id=1,
        operation="f28_op",
        payload_hash="x",
        status="applied",
        response_dict={},
    )
    p03.as_user(c.admin1)
    out = p03.report(module="M28", report="offline_sync")
    assert "error" not in out, out
    assert next(r for r in out["rows"] if r["operation"] == "f28_op")["applied"] == 1
    js = _m28_js()
    assert re.search(r"'M28-offline':[^\n]*report: 'offline_sync'", js)


# ==================================================== M28-13 report access
@pytest.mark.parametrize(
    "report",
    [
        "api_usage",
        "event_delivery_slo",
        "connector_latency",
        "dlq_analysis",
        "webhook_success",
        "offline_sync",
    ],
)
def test_a12f_m28_13_plain_user_gets_no_report(c, p03, report):
    subscription(c)
    c.env["fix.connector"].sudo().create({"name": "Secret Conn", "endpoint": "https://x.test"})
    c.env["fix.integration.log"].sudo()._log_request("api", latency_ms=9)
    p03.as_user(c.plain)
    out = p03.report(module="M28", report=report)
    assert "error" in out, "%s leaked %s" % (report, out.get("rows"))


def test_a12f_m28_13_plain_user_gets_no_kpis_and_other_modules_still_load(c, p03):
    c.env["fix.connector"].sudo().create({"name": "K"})
    p03.as_user(c.plain)
    assert p03.kpis(module="M28")["M28"] == {}


def test_a12f_m28_13_integration_admin_gets_kpis(c, p03):
    c.env["fix.connector"].sudo().create({"name": "K"})
    p03.as_user(c.admin1)
    out = p03.kpis(module="M28")["M28"]
    assert out["connectors_total"] >= 1
    assert "api_p95" in out and "event_delivery" in out


def test_a12f_m28_13_report_stays_in_the_callers_company(c, p03):
    other = c.env["res.company"].sudo().create({"name": "F28 Other"})
    c.env["fix.connector"].sudo().create({"name": "Other Conn", "company_id": other.id})
    p03.as_user(c.admin1)
    out = p03.report(module="M28", report="connector_latency")
    assert "Other Conn" not in [r["connector"] for r in out["rows"]]


def test_a12f_m28_13_plain_user_reads_no_conflict_values(c, p03):
    _conflict(c)
    p03.as_user(c.plain)
    assert "error" in p03.records(model="fix.sync.conflict", cols=["local_value"])


# ==================================================== M28-6 DLQ
def _dead_row(c):
    Out = c.env["fix.event.outbox"].sudo()
    consumer_row = (
        c.env["fix.event.consumer"]
        .sudo()
        .create(
            {
                "name": "F28 failing",
                "event_type": "f28.dl",
                "model": "fix.itsm.ticket",
                "method": "consume_does_not_exist",
                "active_from": fields.Datetime.now() - timedelta(days=1),
            }
        )
    )
    emit(c, "f28.dl")
    for _ in range(3):
        Out.cron_relay()
    delivery = (
        c.env["fix.event.consumer.delivery"]
        .sudo()
        .search([("subscription_id", "=", consumer_row.id)])
    )
    assert delivery.state == "dead"
    c.env["fix.event.dlq"].sudo().cron_sync_dead_letters()
    return c.env["fix.event.dlq"].sudo().search([("delivery_id", "=", delivery.id)]), consumer_row


def test_a12f_m28_6_replay_needs_a_reason_and_records_it(c, p03):
    entry, consumer_row = _dead_row(c)
    p03.as_user(c.admin1)
    refused = p03.action(model="fix.event.dlq", ids=[entry.id], method="action_replay")
    assert not refused.get("success") and "State why" in refused["error"]
    assert entry.state == "pending"
    consumer_row.write({"method": "consume_ticket_created"})
    before = audits(c, "integration.dlq_replayed")
    out = p03.action(
        model="fix.event.dlq",
        ids=[entry.id],
        method="action_replay",
        kwargs={"reason": "consumer fixed", "otp": ""},
    )
    assert out.get("success"), out
    assert entry.decision_reason == "consumer fixed" and entry.replayed_by == c.admin1
    assert audits(c, "integration.dlq_replayed") == before + 1
    c.env["fix.event.outbox"].sudo().cron_relay()
    assert entry.delivery_id.state == "done"


def test_a12f_m28_6_enrolled_user_must_pass_step_up(c, monkeypatch):
    entry, _consumer_row = _dead_row(c)
    # The acting user has an authenticator: no code, or a code with no session, refuses.
    monkeypatch.setattr(type(c.admin1), "totp_enabled", property(lambda self: True), raising=False)
    Dlq = entry.with_user(c.admin1)
    message = attempt(c.env, lambda: Dlq.action_replay(reason="why"))
    assert message and "6-digit" in message
    assert attempt(c.env, lambda: Dlq.action_replay(reason="why", otp="123456"))
    assert entry.state == "pending"


def test_a12f_m28_6_required_mode_refuses_a_user_with_no_authenticator(c):
    entry, _consumer_row = _dead_row(c)
    c.env["ir.config_parameter"].sudo().set_param(integration.REPLAY_STEP_UP_KEY, "required")
    message = attempt(c.env, lambda: entry.with_user(c.admin1).action_replay(reason="why"))
    assert message and "no authenticator" in message


def test_a12f_m28_6_no_one_types_a_dead_letter(c, p03):
    Dlq = c.env["fix.event.dlq"].with_user(c.admin1)
    assert attempt(c.env, lambda: Dlq.create({"topic_code": "x", "payload": "{}", "reason": "r"}))
    p03.as_user(c.admin1)
    assert "error" in p03.write(
        model="fix.event.dlq", values={"topic_code": "x", "payload": "{}", "reason": "r"}
    )


def test_a12f_m28_6_discard_needs_a_reason(c):
    entry, _consumer_row = _dead_row(c)
    assert attempt(c.env, lambda: entry.with_user(c.admin1).action_discard())
    entry.with_user(c.admin1).action_discard(reason="superseded by a compensating event")
    # Y05: the reason is on the request; a second admin decides.
    assert entry.state == "pending" and entry.approval_state == "pending"
    decide(c, entry, c.admin2)
    assert entry.state == "discarded"


def test_a12f_m28_6_stale_dead_letter_opens_one_incident_through_the_real_relay(c):
    entry, _consumer_row = _dead_row(c)
    c.env.flush_all()
    c.env.cr.execute(
        "UPDATE fix_event_dlq SET created_at = created_at - interval '3 hours' WHERE id=%s",
        (entry.id,),
    )
    c.env.invalidate_all()
    # The incident itself is M66's (fix.itsm.ticket.cron_dead_letter_incidents). This
    # proves the row M28 mirrors reaches it through the real relay, once.
    Ticket = c.env["fix.itsm.ticket"].sudo()
    ref = "fix.event.dlq,%d" % entry.id
    Out = c.env["fix.event.outbox"].sudo()
    Out.search([("event_type", "=", "outbox.relay_unhealthy")]).unlink()
    Out.cron_relay_age_alert()
    Out.cron_relay()
    assert Ticket.search_count([("source_ref", "=", ref)]) == 1
    c.env["fix.event.dlq"].sudo().cron_sync_dead_letters()
    Out.search([("event_type", "=", "outbox.relay_unhealthy")]).unlink()
    Out.cron_relay_age_alert()
    Out.cron_relay()
    assert Ticket.search_count([("source_ref", "=", ref)]) == 1, "raised twice"


def test_a12f_m28_4_dead_letter_closes_when_its_delivery_later_succeeds(c):
    """A12 finish rehearsal on a fix_dev copy: three real M60 dead letters were
    redelivered after the consumer fix, yet their DLQ rows stayed 'pending'. The
    mirror closes such a row truthfully, naming no one as the replayer."""
    entry, consumer_row = _dead_row(c)
    assert entry.state == "pending" and entry.delivery_id
    # a second dead letter on the same consumer stays dead
    Out = c.env["fix.event.outbox"].sudo()
    emit(c, "f28.dl")
    for _ in range(3):
        Out.cron_relay()
    Delivery = c.env["fix.event.consumer.delivery"].sudo()
    still_dead = Delivery.search(
        [("subscription_id", "=", consumer_row.id), ("id", "!=", entry.delivery_id.id)]
    )
    assert still_dead.state == "dead"
    entry.delivery_id.sudo().write({"state": "done", "delivered_at": fields.Datetime.now()})
    c.env["fix.event.dlq"].sudo().cron_sync_dead_letters()
    entry.invalidate_recordset()
    assert entry.state == "replayed"
    assert not entry.replayed_by
    assert "later relay attempt" in entry.decision_reason
    other = c.env["fix.event.dlq"].sudo().search([("delivery_id", "=", still_dead.id)])
    assert other.state == "pending"


# ==================================================== M28-8 schema and topic
def test_a12f_m28_8_schema_code_version_is_unique(c):
    Schema = c.env["fix.event.schema"].sudo()
    Schema.create({"code": "dup", "version": 1, "schema_text": "{}"})
    with pytest.raises(Exception, match="unique|duplicate"), c.env.cr.savepoint():
        Schema.create({"code": "dup", "version": 1, "schema_text": "{}"})


def test_a12f_m28_8_deprecate_through_the_screen(c, p03):
    p03.as_user(c.admin1)
    made = p03.write(
        model="fix.event.schema", values={"code": "d", "version": 1, "schema_text": "{}"}
    )
    schema = c.env["fix.event.schema"].browse(made["id"])
    refused = p03.action(model="fix.event.schema", ids=[schema.id], method="action_deprecate")
    assert not refused.get("success")
    assert p03.action(model="fix.event.schema", ids=[schema.id], method="action_publish")["success"]
    assert p03.action(model="fix.event.schema", ids=[schema.id], method="action_deprecate")[
        "success"
    ]
    assert schema.state == "deprecated"


def _published(c, code, contract):
    schema = (
        c.env["fix.event.schema"].sudo().create({"code": code, "schema_text": json.dumps(contract)})
    )
    schema.action_publish()
    return schema


def test_a12f_m28_8_payload_is_checked_at_emit_through_the_real_publisher(c):
    from libs.py.fix_events import publish

    contract = {
        "type": "object",
        "required": ["must"],
        "properties": {
            "must": {"type": "integer"},
            "kind": {"enum": ["a", "b"]},
            "rows": {"type": "array", "items": {"type": "string"}},
        },
        "additionalProperties": False,
    }
    topic(c, "f28.v", schema_id=_published(c, "f28.v", contract).id)
    publish(c.env, "f28.v", "x", 1, {"must": 1, "kind": "a", "rows": ["x"]})
    for bad in (
        {"nope": 1},
        {"must": "text"},
        {"must": True},
        {"must": 1, "kind": "c"},
        {"must": 1, "rows": [1]},
        {"must": 1, "extra": 1},
    ):
        with pytest.raises(ValidationError), c.env.cr.savepoint():
            publish(c.env, "f28.v", "x", 1, bad)


def test_a12f_m28_8_warn_mode_rehearses_a_schema_without_blocking(c):
    topic(c, "f28.w", schema_id=_published(c, "f28.w", {"required": ["must"]}).id)
    c.env["ir.config_parameter"].sudo().set_param(dispatch.SCHEMA_ENFORCEMENT_KEY, "warn")
    assert emit(c, "f28.w", {"nope": 1})


def test_a12f_m28_8_draft_schema_and_other_company_do_not_gate(c):
    draft = (
        c.env["fix.event.schema"]
        .sudo()
        .create({"code": "f28.x", "schema_text": json.dumps({"required": ["must"]})})
    )
    topic(c, "f28.x", schema_id=draft.id)
    assert emit(c, "f28.x", {"nope": 1})


def test_a12f_m28_8_retention_purges_only_settled_events_past_it(c):
    the_topic = topic(c, "f28.r", retention_days=7)
    Out = c.env["fix.event.outbox"].sudo()
    old_done = emit(c, "f28.r")
    old_unrelayed = emit(c, "f28.r")
    old_dead = emit(c, "f28.r")
    old_pending = emit(c, "f28.r")
    young = emit(c, "f28.r")
    other_type = emit(c, "f28.no_topic")
    now = fields.Datetime.now()
    (old_done | old_dead | young | other_type).write({"relayed_at": now})
    # M28-D3: retention may only delete what the bus confirmed published —
    # old_pending is settled in-process but still pending for the bus, so it
    # must survive the cutoff.
    old_pending.write({"relayed_at": now})
    old_done.write({"status": "published"})
    consumer_row = (
        c.env["fix.event.consumer"]
        .sudo()
        .create(
            {
                "name": "F28 r",
                "event_type": "f28.r",
                "model": "fix.itsm.ticket",
                "method": "consume_x",
            }
        )
    )
    c.env["fix.event.consumer.delivery"].sudo().create(
        {"subscription_id": consumer_row.id, "event_id": old_dead.id, "state": "dead"}
    )
    c.env.flush_all()
    c.env.cr.execute(
        "UPDATE fix_event_outbox SET create_date = create_date - interval '30 days' WHERE id IN %s",
        ((old_done | old_unrelayed | old_dead | old_pending | other_type)._ids,),
    )
    c.env.invalidate_all()
    before = audits(c, "integration.events_purged")
    assert the_topic.cron_purge_retention() == 1
    assert not old_done.exists()
    assert (
        old_unrelayed.exists() and old_dead.exists() and young.exists()
    ), "unrelayed/dead/young survive"
    assert old_pending.exists(), "M28-D3: a bus-pending event survives its retention cutoff"
    assert other_type.exists(), "a type with no topic was purged"
    assert audits(c, "integration.events_purged") == before + 1
    assert c.env.ref("cd_itsm.ir_cron_event_retention_purge").active
    assert Out.browse(young.id).exists()


def test_a12f_m28_8_cron_bodies_refuse_a_json_rpc_caller(c):
    for model, method in (
        ("fix.event.topic", "cron_purge_retention"),
        ("fix.event.subscription", "cron_revalidate_subscriptions"),
        ("fix.sync.conflict", "cron_ingest_ledger_conflicts"),
        ("fix.connector.credential", "cron_alert_expiring"),
        ("fix.api.quota", "cron_enforce_quotas"),
        ("fix.connector", "cron_probe_connectors"),
        ("fix.event.dlq", "cron_sync_dead_letters"),
    ):
        Model = c.env[model].with_user(c.admin1)
        assert attempt(c.env, lambda m=Model, n=method: getattr(m, n)()), "%s.%s" % (model, method)


# ==================================================== M28-9 connector health
def test_a12f_m28_9_probe_is_on_the_screen_and_honest_when_silent(c, p03):
    conn = c.env["fix.connector"].sudo().create({"name": "P", "endpoint": "https://p.test"})
    p03.as_user(c.admin1)
    out = p03.action(model="fix.connector", ids=[conn.id], method="action_probe")
    assert out.get("success"), out
    assert conn.state == "live" and not conn.last_probe_at
    assert "No evidence" in conn.last_probe_note


def test_a12f_m28_9_active_probe_measures_when_the_gate_opens(c, monkeypatch):
    monkeypatch.setattr(integration, "_http_head", lambda url, timeout: 200)
    monkeypatch.setenv("FIX_ENV", "local")
    allow(c, "localhost")
    enable_dispatch(c)
    conn = c.env["fix.connector"].sudo().create({"name": "P", "endpoint": "https://localhost/x"})
    conn.with_user(c.admin1).action_probe()
    assert conn.last_probe_at and conn.last_success_at and conn.state == "live"
    log = c.env["fix.integration.log"].sudo().search([("connector_id", "=", conn.id)])
    assert log.kind == "probe" and log.measured


def test_a12f_m28_9_down_comes_back_only_on_measured_evidence(c, p03):
    conn = c.env["fix.connector"].sudo().create({"name": "D"})
    p03.as_user(c.admin1)
    out = p03.action(
        model="fix.connector",
        ids=[conn.id],
        method="action_mark_down",
        kwargs={"reason": "provider outage"},
    )
    assert out.get("success"), out
    assert conn.state == "down"
    refused = p03.action(model="fix.connector", ids=[conn.id], method="action_mark_live")
    assert not refused.get("success")
    refused = p03.action(
        model="fix.connector",
        ids=[conn.id],
        method="action_mark_live",
        kwargs={"reason": "trust me"},
    )
    assert not refused.get("success") and "Probe" in refused["error"]
    assert conn.state == "down"
    c.env["fix.integration.log"].sudo()._log_request(
        "api", connector=conn, status="success", latency_ms=20
    )
    assert p03.action(model="fix.connector", ids=[conn.id], method="action_probe")["success"]
    assert conn.state == "live" and conn.last_latency_ms == 20


def test_a12f_m28_9_marks_are_audited(c):
    conn = c.env["fix.connector"].sudo().create({"name": "M"})
    before = audits(c, "integration.connector_marked")
    conn.with_user(c.admin1).action_mark_degraded(reason="slow")
    conn.with_user(c.admin1).action_disable(reason="retired")
    assert audits(c, "integration.connector_marked") == before + 2
    assert conn.state == "disabled"


def test_a12f_m28_9_fallback_must_be_another_connector_of_the_same_type(c):
    Connector = c.env["fix.connector"].with_user(c.admin1)
    pay = Connector.create({"name": "bKash", "connector_type": "payment"})
    nagad = Connector.create({"name": "Nagad", "connector_type": "payment"})
    sms = Connector.create({"name": "SMS", "connector_type": "messaging"})
    pay.write({"fallback_connector_id": nagad.id})
    assert attempt(c.env, lambda: pay.write({"fallback_connector_id": sms.id}))
    assert attempt(c.env, lambda: pay.write({"fallback_connector_id": pay.id}))


# ==================================================== M28-10 credentials
def test_a12f_m28_10_rotation_versions_the_reference_and_audits(c, p03):
    p03.as_user(c.admin1)
    made = p03.write(
        model="fix.connector.credential",
        values={
            "name": "bKash",
            "auth_type": "api_key",
            "secret_ref": "vault://connectors/bkash/v1",
        },
    )
    assert "error" not in made, made
    cred = c.env["fix.connector.credential"].browse(made["id"])
    out = p03.write(
        model="fix.connector.credential",
        record_id=cred.id,
        values={"secret_ref": "vault://attacker/1"},
    )
    assert "error" in out, out
    assert attempt(
        c.env, lambda: cred.with_user(c.admin1).write({"secret_ref": "vault://attacker/1"})
    )
    before = audits(c, "integration.credential_rotated")
    out = p03.action(
        model="fix.connector.credential",
        ids=[cred.id],
        method="action_rotate",
        kwargs={"expires_on": "2030-01-31"},
    )
    assert out.get("success"), out
    assert cred.secret_ref == "vault://connectors/bkash/v2"
    assert str(cred.expires_on) == "2030-01-31"
    assert cred.rotated_by_id == c.admin1
    assert audits(c, "integration.credential_rotated") == before + 1
    bad = p03.action(
        model="fix.connector.credential",
        ids=[cred.id],
        method="action_rotate",
        kwargs={"expires_on": "next year"},
    )
    assert not bad.get("success") and "YYYY-MM-DD" in bad["error"]


def test_a12f_m28_10_expiry_alert_once_with_a_to_do(c):
    soon = fields.Date.context_today(c.env["res.users"]) + timedelta(days=10)
    cred = (
        c.env["fix.connector.credential"]
        .sudo()
        .create({"name": "Soon", "secret_ref": "vault://x/1", "expires_on": soon})
    )
    far = (
        c.env["fix.connector.credential"]
        .sudo()
        .create(
            {"name": "Far", "secret_ref": "vault://x/2", "expires_on": soon + timedelta(days=300)}
        )
    )
    Cred = c.env["fix.connector.credential"].sudo()
    assert Cred.cron_alert_expiring() >= 1
    assert cred.expiry_alerted_on and not far.expiry_alerted_on
    assert cred.activity_ids and c.admin1 in cred.activity_ids.mapped("user_id")
    assert Cred.cron_alert_expiring() == 0, "alerted twice"
    # a new date restarts the clock, and the change is audited
    before = audits(c, "integration.credential_expiry_changed")
    cred.with_user(c.admin1).write({"expires_on": soon + timedelta(days=5)})
    assert not cred.expiry_alerted_on
    assert audits(c, "integration.credential_expiry_changed") == before + 1
    assert c.env.ref("cd_itsm.ir_cron_credential_expiry_alert").active


# ==================================================== N-M28-5 allowed hosts
def test_a12f_n_m28_5_integration_admin_lists_a_host_from_the_screen(c, p03):
    Param = c.env["ir.config_parameter"].sudo()
    p03.as_user(c.admin1)
    made = p03.write(
        model="fix.integration.allowed.host",
        values={"host": "Hooks.Partner.test", "reason": "partner webhook, contract 12"},
    )
    assert "error" not in made, made
    row = c.env["fix.integration.allowed.host"].browse(made["id"])
    assert row.host == "hooks.partner.test" and row.listed_by_id == c.admin1
    assert Param.get_param(ALLOW_KEY) == "hooks.partner.test"
    assert audits(c, "integration.allowlist_added") >= 1
    # the point of the list: a subscription can now be registered
    cons = consumer(c)
    the_topic = topic(c)
    sub = p03.write(
        model="fix.event.subscription",
        values={
            "consumer_id": cons.id,
            "topic_id": the_topic.id,
            "endpoint_url": "https://hooks.partner.test/in",
            "secret_ref": SECRET_REF,
        },
    )
    assert "error" not in sub, sub
    live = c.env["fix.event.subscription"].browse(sub["id"])
    out = p03.action(
        model="fix.event.subscription",
        ids=[live.id],
        method="action_request_go_live",
        kwargs={"justification": "contract 12"},
    )
    assert out.get("success"), out
    decide(c, live, c.admin2)
    assert live.state == "active"
    # removal is audited, and what used the host pauses at once
    refused = p03.action(model="fix.integration.allowed.host", ids=[row.id], method="action_remove")
    assert not refused.get("success")
    out = p03.action(
        model="fix.integration.allowed.host",
        ids=[row.id],
        method="action_remove",
        kwargs={"reason": "contract ended"},
    )
    assert out.get("success"), out
    assert row.state == "removed" and row.removal_reason == "contract ended"
    assert not Param.get_param(ALLOW_KEY)
    assert c.env["fix.event.subscription"].browse(sub["id"]).state == "paused"


def test_a12f_n_m28_5_it_grants_no_access_to_config_parameters(c):
    Param = c.env["ir.config_parameter"].with_user(c.admin1)
    assert attempt(c.env, lambda: Param.set_param(ALLOW_KEY, "x.test"))
    assert attempt(c.env, lambda: Param.search([]))
    assert attempt(c.env, lambda: Param.create({"key": "f28.k", "value": "v"}))


def test_a12f_n_m28_5_plain_user_cannot_list_a_host(c, p03):
    Host = c.env["fix.integration.allowed.host"].with_user(c.plain)
    assert attempt(c.env, lambda: Host.create({"host": "x.test", "reason": "r"}))
    p03.as_user(c.plain)
    assert "error" in p03.write(
        model="fix.integration.allowed.host", values={"host": "x.test", "reason": "r"}
    )


@pytest.mark.parametrize(
    "bad",
    ["https://x.test", "x.test:443", "x.test/path", "*", "*.com", "", "a b.test", "*.*.test"],
)
def test_a12f_n_m28_5_a_host_must_be_a_host(c, bad):
    Host = c.env["fix.integration.allowed.host"].with_user(c.admin1)
    assert attempt(c.env, lambda: Host.create({"host": bad, "reason": "r"}))


def test_a12f_n_m28_5_host_needs_a_reason_and_cannot_be_edited(c):
    Host = c.env["fix.integration.allowed.host"].with_user(c.admin1)
    assert attempt(c.env, lambda: Host.create({"host": "x.test", "reason": " "}))
    row = Host.create({"host": "x.test", "reason": "ok"})
    assert attempt(c.env, lambda: row.write({"host": "attacker.test"}))
    assert attempt(c.env, lambda: Host.create({"host": "x.test", "reason": "twice"}))


def test_a12f_n_m28_5_screen_follows_a_host_set_directly_by_a_system_admin(c):
    allow(c, "direct.test")
    Sub = c.env["fix.event.subscription"].sudo()
    Sub.cron_revalidate_subscriptions()
    row = c.env["fix.integration.allowed.host"].sudo().search([("host", "=", "direct.test")])
    assert row.state == "listed" and "system admin" in row.reason
    c.env["ir.config_parameter"].sudo().search([("key", "=", ALLOW_KEY)]).unlink()
    Sub.cron_revalidate_subscriptions()
    assert row.state == "removed"


# ==================================================== N-M28-4, -7, -8, -10 screens
def _m28_js():
    from odoo.addons.cd_p03_portal.controllers.a12 import m28

    return (Path(m28.__file__).parents[2] / "static" / "src" / "a12" / "m28.js").read_text(
        encoding="utf-8"
    )


def test_a12f_n_m28_4_lists_exist_and_rows_open(c, p03):
    js = _m28_js()
    for screen, form in (
        ("M28-subscriptions", "M28-form-subscription"),
        ("M28-credentials", "M28-form-credential"),
        ("M28-allowlist", "M28-form-allowed-host"),
    ):
        assert "{ id: '%s'" % screen in js, screen
        assert "'%s': '%s'" % (screen, form) in js, screen
    sub = subscription(c)
    p03.as_user(c.admin1)
    rows = p03.records(
        model="fix.event.subscription",
        cols=[
            "name",
            "consumer_id",
            "topic_id",
            "endpoint_url",
            "secret_ref",
            "consecutive_failures",
            "pause_reason",
            "state",
        ],
    )
    assert "error" not in rows, rows
    assert sub.id in [r["id"] for r in rows["rows"]]
    assert p03.action(
        model="fix.event.subscription",
        ids=[sub.id],
        method="action_pause",
        kwargs={"reason": "maintenance"},
    )["success"]
    assert sub.pause_reason == "maintenance"
    assert p03.action(
        model="fix.event.subscription",
        ids=[sub.id],
        method="action_resume",
        kwargs={"reason": "back"},
    )["success"]
    before = sub.secret_ref
    assert p03.action(model="fix.event.subscription", ids=[sub.id], method="action_rotate_secret")[
        "success"
    ]
    assert sub.secret_ref != before


def test_a12f_every_screen_column_is_a_real_field(c):
    """/p03/model/records drops an unknown column silently."""
    js = _m28_js()
    for model, cols in re.findall(r"model: '(fix\.[a-z.]+)'[^\n]*\n\s*cols: \[([^\]]+)\]", js):
        names = re.findall(r"'([a-z_0-9]+)'", cols)
        for name in names:
            assert name in c.env[model]._fields, "%s has no %s" % (model, name)


def test_a12f_every_form_field_is_real_and_writable_or_readonly(c):
    from odoo.addons.cd_p03_portal.controllers.a12 import m28

    js = _m28_js()
    for form in re.findall(
        r"model: '(fix\.[a-z.]+)',\n\s*title:.*?(?=\n  '?M28-form|\nSCREENS|\Z)", js, re.S
    ):
        assert form in m28.WRITABLE
    blocks = re.split(r"\n  'M28-form-|\nSCREENS\['M28-form-", js)
    checked = 0
    for block in blocks[1:]:
        model = re.search(r"model: '(fix\.[a-z.]+)'", block).group(1)
        # a decision form (saveAction, capture audit 2026-11-14) carries its
        # inputs to a whitelisted workflow method, never to /p03/model/write
        carried = set()
        for kwargs in re.findall(r"saveAction: \{.*?kwargs: \{([^}]*)\}", block, re.S):
            carried |= set(re.findall(r":\s*'([a-z_0-9]+)'", kwargs))
        for line in re.findall(r"\{ name: '[a-z_0-9]+'[^\n]*", block.split("export const")[0]):
            name = re.search(r"name: '([a-z_0-9]+)'", line).group(1)
            assert name in c.env[model]._fields, "%s.%s" % (model, name)
            if "readonly: true" not in line:
                if name in carried:
                    assert name not in m28.WRITABLE[model], "%s.%s writable too" % (model, name)
                else:
                    assert name in m28.WRITABLE[model], "%s.%s not writable" % (model, name)
            checked += 1
    assert checked > 20


def test_a12f_every_button_is_whitelisted_and_its_argument_is_asked(c):
    """A button whose method needs an argument needs an ask, or it always refuses."""
    import inspect

    from odoo.addons.cd_p03_portal.controllers.a12 import m28

    js = _m28_js()
    declared = set()
    for conf in m28.SURFACES.values():
        declared |= set(conf["actions"])
    # row buttons (m:) and decision forms' buttons (saveAction method:)
    used = set(re.findall(r"\bm:\s*'(action_[a-z_]+)'", js))
    used |= set(re.findall(r"saveAction: \{\s*method:\s*'(action_[a-z_]+)'", js))
    assert used <= declared, sorted(used - declared)
    assert declared <= used, "whitelisted with no button: %s" % sorted(declared - used)
    for model, conf in m28.SURFACES.items():
        for method in conf["actions"]:
            assert hasattr(c.env[model], method), "%s.%s" % (model, method)
    assert (
        "kwarg: 'reason'" in js
        and inspect.signature(c.env["fix.event.dlq"].action_replay).parameters["reason"]
    )


def test_a12f_n_m28_7_probe_is_whitelisted():
    from odoo.addons.cd_p03_portal.controllers.a12 import m28

    assert "action_probe" in m28.SURFACES["fix.connector"]["actions"]
    assert "m: 'action_probe'" in _m28_js()


def test_a12f_n_m28_8_dropdowns_read_as_words(c):
    schema = c.env["fix.event.schema"].sudo().create({"code": "f28.n", "schema_text": "{}"})
    assert schema.display_name == "f28.n v1 (draft)"
    cons = consumer(c)
    quota = c.env["fix.api.quota"].sudo().create({"consumer_id": cons.id})
    assert quota.display_name == "F28 Consumer / all endpoints"


def test_a12f_n_m28_10_vault_screens_claim_only_what_rotate_does():
    js = _m28_js()
    assert "Rotate Key action" not in js
    assert js.count("No secrets manager is attached") >= 3


def test_a12f_workflow_webhook_from_nothing_as_a_real_admin(c, p03, http):
    """The whole path on the screen: list a host, register, publish, deliver."""
    enable_dispatch(c)
    p03.as_user(c.admin1)
    assert "error" not in p03.write(
        model="fix.integration.allowed.host", values={"host": "localhost", "reason": "local test"}
    )
    cons = p03.write(model="fix.api.consumer", values={"name": "Walk"})
    consumer_row = c.env["fix.api.consumer"].browse(cons["id"])
    assert p03.action(
        model="fix.api.consumer",
        ids=[cons["id"]],
        method="action_request_registration",
        kwargs={"justification": "walk"},
    )["success"]
    decide(c, consumer_row, c.admin2)
    assert p03.action(model="fix.api.consumer", ids=[cons["id"]], method="action_issue_key")[
        "success"
    ]
    schema = p03.write(
        model="fix.event.schema",
        values={"code": "f28.walk", "version": 1, "schema_text": '{"required": ["a"]}'},
    )
    assert p03.action(model="fix.event.schema", ids=[schema["id"]], method="action_publish")[
        "success"
    ]
    made_topic = p03.write(
        model="fix.event.topic",
        values={"code": "f28.walk", "name": "Walk", "schema_id": schema["id"], "retention_days": 7},
    )
    assert "error" not in made_topic, made_topic
    sub = p03.write(
        model="fix.event.subscription",
        values={
            "consumer_id": cons["id"],
            "topic_id": made_topic["id"],
            "endpoint_url": LOCAL_URL,
            "secret_ref": SECRET_REF,
        },
    )
    assert "error" not in sub, sub
    assert p03.action(
        model="fix.event.subscription",
        ids=[sub["id"]],
        method="action_request_go_live",
        kwargs={"justification": "walk"},
    )["success"]
    decide(c, c.env["fix.event.subscription"].browse(sub["id"]), c.admin2)
    emit(c, "f28.walk", {"a": 1})
    run_dispatch(c)
    assert len(http.calls) == 1
    out = p03.report(module="M28", report="webhook_success")
    row = next(r for r in out["rows"] if r["topic"] == "f28.walk")
    assert row["attempts"] == 1 and row["rate"] == 100.0


def _form_fields(out):
    assert "error" not in out, out
    return {f["name"]: f for f in out["fields"]}


def test_a12f_forms_offer_a_reference_on_a_new_record_and_lock_it_after(c, p03):
    cons = consumer(c)
    p03.as_user(c.admin1)
    spec = [{"name": "name"}, {"name": "key_ref"}]
    assert not _form_fields(p03.form(model="fix.api.consumer", fields=spec))["key_ref"]["readonly"]
    saved = _form_fields(p03.form(model="fix.api.consumer", fields=spec, record_id=cons.id))
    assert saved["key_ref"]["readonly"] and not saved["name"]["readonly"]
    spec = [{"name": "secret_ref"}, {"name": "expires_on"}]
    new = _form_fields(p03.form(model="fix.connector.credential", fields=spec))
    assert not new["secret_ref"]["readonly"]
    cred = (
        c.env["fix.connector.credential"].sudo().create({"name": "C", "secret_ref": "vault://c/1"})
    )
    old = _form_fields(p03.form(model="fix.connector.credential", fields=spec, record_id=cred.id))
    assert old["secret_ref"]["readonly"] and not old["expires_on"]["readonly"]


def test_a12f_conflict_form_opens_read_only_and_a_save_changes_nothing(c, p03):
    conflict, _partner = _conflict(c)
    p03.as_user(c.admin1)
    spec = [{"name": n} for n in ("device_ref", "res_model", "local_value", "policy_class")]
    fields_out = _form_fields(
        p03.form(model="fix.sync.conflict", fields=spec, record_id=conflict.id)
    )
    assert fields_out["res_model"]["readonly"] and fields_out["local_value"]["readonly"]
    # The form posts every field it shows: an unchanged echo is not an edit.
    out = p03.write(
        model="fix.sync.conflict",
        record_id=conflict.id,
        values={"device_ref": conflict.device_ref, "res_model": conflict.res_model},
    )
    assert "error" not in out, out


def test_a12f_schema_and_host_dropdowns_and_lists_load_for_the_role(c, p03):
    schema = c.env["fix.event.schema"].sudo().create({"code": "f28.dd", "schema_text": "{}"})
    p03.as_user(c.admin1)
    out = _form_fields(p03.form(model="fix.event.topic", fields=[{"name": "schema_id"}]))
    labels = {choice["label"] for choice in out["schema_id"]["choices"]}
    assert schema.display_name in labels
    for model, cols in (
        ("fix.webhook.delivery", ["event_type", "state", "last_outcome"]),
        ("fix.integration.allowed.host", ["host", "reason", "state"]),
        ("fix.integration.log", ["kind", "status", "measured", "outcome"]),
        ("fix.connector.credential", ["name", "secret_ref", "rotated_at"]),
    ):
        listed = p03.records(model=model, cols=cols)
        assert "error" not in listed, (model, listed)
