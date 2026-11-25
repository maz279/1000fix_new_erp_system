"""M28 capture pass 2 (2026-11-19): the records the sub-module pages could not
capture, driven as NON-ADMIN users through /p03/model/write and
/p03/model/action with the kwargs m28.js sends. The superuser is trusted by the
model guards and would hide a gap, so it only seeds.

  * Versioning & Portals - API credential per environment (FR-IPF-016)
  * Subscriptions & DLQ - consumer replay (FR-IPF-031)
  * Webhooks - inbound webhook source and receiver (FR-IPF-037/038)
  * Connector Framework - pattern/priority, tested fallback (BRU-IPF-12/13),
    batch file exchange (FR-IPF-045)
"""

from __future__ import annotations

import base64
import hashlib
import json
import time
import types
from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
IADMIN = "cd_itsm.group_integration_admin"
ALLOW_KEY = "fix.integration.webhook_allowlist"
HOST = "hooks.m28p2.test"


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
    env["ir.config_parameter"].sudo().set_param(ALLOW_KEY, HOST)
    return types.SimpleNamespace(
        env=env,
        plain=_user(env, "m28p2_plain"),
        admin1=_user(env, "m28p2_admin1", [IADMIN]),
        admin2=_user(env, "m28p2_admin2", [IADMIN]),
    )


@pytest.fixture
def p03(c):
    import odoo.addons.cd_p03_portal.controllers.a12 as a12mod
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g
    import odoo.addons.cd_p03_portal.controllers.p03_service_order_api as s

    ctl = g.P03GenericApiController()
    C = g.P03GenericApiController
    saved = (g.request, s.request, a12mod.request)

    def _o(fn):
        return getattr(fn, "original_endpoint", fn)

    def as_user(user):
        req = types.SimpleNamespace(env=c.env(user=user.id))
        g.request = req
        s.request = req
        a12mod.request = req

    try:
        yield types.SimpleNamespace(
            write=lambda **k: _o(C.model_write)(ctl, **k),
            action=lambda **k: _o(C.model_action)(ctl, **k),
            as_user=as_user,
        )
    finally:
        g.request, s.request, a12mod.request = saved


def made(out):
    assert "error" not in out and out.get("id"), out
    return out["id"]


def act_ok(p03, model, rec, method, **kwargs):
    out = p03.action(model=model, ids=[rec.id], method=method, kwargs=kwargs)
    assert out.get("success"), out
    return out


def act_refused(p03, model, rec, method, **kwargs):
    out = p03.action(model=model, ids=[rec.id], method=method, kwargs=kwargs)
    assert not out.get("success"), "%s was accepted" % method
    return out["error"]


def audits(c, event):
    return c.env["fix.security.audit"].sudo().search_count([("event", "=", event)])


def decide(c, record, user):
    tasks = (
        c.env["fix.workflow.task"]
        .sudo()
        .search([("request_id", "=", record.approval_request_id.id), ("state", "!=", "done")])
    )
    mine = tasks.filtered(lambda t: t.assigned_user_id == user)
    assert mine, "no task for %s; routed to %s" % (
        user.login,
        tasks.assigned_user_id.mapped("login"),
    )
    mine.with_user(user).action_approve(comment="checked")


# ============================================================ Connector register
def _connector(p03, c, **extra):
    p03.as_user(c.admin1)
    vals = {"name": "P2 Gateway", "connector_type": "payment", "endpoint": "https://%s/c" % HOST}
    vals.update(extra)
    return c.env["fix.connector"].browse(made(p03.write(model="fix.connector", values=vals)))


def _fallback(p03, c, connector, **extra):
    p03.as_user(c.admin1)
    vals = {
        "connector_id": connector.id,
        "fallback_type": "manual",
        "procedure": "Counter staff take cash; payments are keyed in on recovery.",
        "user_message": "Online payment is down; pay at the counter.",
        "user_message_bn": "অনলাইন পেমেন্ট বন্ধ; কাউন্টারে পরিশোধ করুন।",
    }
    vals.update(extra)
    return c.env["fix.integration.fallback"].browse(
        made(p03.write(model="fix.integration.fallback", values=vals))
    )


def _test(p03, c, fallback, result):
    p03.as_user(c.admin1)
    return c.env["fix.integration.fallback.test"].browse(
        made(
            p03.write(
                model="fix.integration.fallback.test",
                values={
                    "fallback_id": fallback.id,
                    "tested_at": fields.Datetime.to_string(fields.Datetime.now()),
                    "result": result,
                    "engage_seconds": 40,
                    "evidence": "Gateway blocked at the firewall; counter flow ran end to end.",
                },
            )
        )
    )


def test_connector_without_pattern_or_priority_cannot_go_live(c, p03):
    conn = _connector(p03, c)
    assert "pattern" in act_refused(
        p03, "fix.connector", conn, "action_request_go_live", justification="go"
    )
    conn.sudo().write({"pattern": "sync_request"})
    assert "priority" in act_refused(
        p03, "fix.connector", conn, "action_request_go_live", justification="go"
    )


def test_p0_connector_needs_a_fallback_whose_latest_test_passed(c, p03):
    conn = _connector(p03, c, pattern="sync_request", priority="p0")
    assert "BRU-IPF-12" in act_refused(
        p03, "fix.connector", conn, "action_request_go_live", justification="go"
    )
    fallback = _fallback(p03, c, conn)
    assert "BRU-IPF-12" in act_refused(
        p03, "fix.connector", conn, "action_request_go_live", justification="go"
    )
    _test(p03, c, fallback, "failed")
    assert not conn.fallback_ready
    assert "BRU-IPF-12" in act_refused(
        p03, "fix.connector", conn, "action_request_go_live", justification="go"
    )
    _test(p03, c, fallback, "passed")
    assert conn.fallback_ready
    act_ok(p03, "fix.connector", conn, "action_request_go_live", justification="bKash launch")
    decide(c, conn, c.admin2)
    assert conn.state == "live"


def test_a_failed_test_after_the_request_stops_the_go_live(c, p03):
    conn = _connector(p03, c, pattern="sync_request", priority="p0")
    fallback = _fallback(p03, c, conn)
    _test(p03, c, fallback, "passed")
    act_ok(p03, "fix.connector", conn, "action_request_go_live", justification="bKash launch")
    _test(p03, c, fallback, "failed")
    with pytest.raises(REFUSED), c.env.cr.savepoint():
        decide(c, conn, c.admin2)
    assert conn.state != "live"


def test_p1_connector_goes_live_without_a_fallback(c, p03):
    conn = _connector(p03, c, pattern="async_command", priority="p1")
    act_ok(p03, "fix.connector", conn, "action_request_go_live", justification="SMS")
    decide(c, conn, c.admin2)
    assert conn.state == "live"


def test_lowering_an_approved_p0_reopens_the_go_live(c, p03):
    conn = _connector(p03, c, pattern="sync_request", priority="p0")
    _test(p03, c, _fallback(p03, c, conn), "passed")
    act_ok(p03, "fix.connector", conn, "action_request_go_live", justification="launch")
    decide(c, conn, c.admin2)
    p03.as_user(c.admin1)
    made(p03.write(model="fix.connector", record_id=conn.id, values={"priority": "p2"}))
    assert conn.state == "registered" and conn.awaiting_go_live


def test_alternate_fallback_names_a_connector_of_the_same_type(c, p03):
    conn = _connector(p03, c, pattern="sync_request", priority="p0")
    p03.as_user(c.admin1)
    out = p03.write(
        model="fix.integration.fallback",
        values={
            "connector_id": conn.id,
            "fallback_type": "alternate",
            "procedure": "Route to the other gateway.",
            "user_message": "x",
            "user_message_bn": "x",
        },
    )
    assert out.get("error"), out
    sms = c.env["fix.connector"].sudo().create({"name": "SMS", "connector_type": "messaging"})
    out = p03.write(
        model="fix.integration.fallback",
        values={
            "connector_id": conn.id,
            "fallback_type": "alternate",
            "fallback_connector_id": sms.id,
            "procedure": "Route to the other gateway.",
            "user_message": "x",
            "user_message_bn": "x",
        },
    )
    assert out.get("error"), out


def test_a_tested_fallback_and_its_tests_do_not_change(c, p03):
    conn = _connector(p03, c, pattern="sync_request", priority="p0")
    fallback = _fallback(p03, c, conn)
    test = _test(p03, c, fallback, "passed")
    assert test.tested_by_id == c.admin1
    p03.as_user(c.admin1)
    out = p03.write(
        model="fix.integration.fallback",
        record_id=fallback.id,
        values={"procedure": "something else"},
    )
    assert out.get("error"), out
    out = p03.write(
        model="fix.integration.fallback.test", record_id=test.id, values={"result": "failed"}
    )
    assert out.get("error"), out
    with pytest.raises(REFUSED), c.env.cr.savepoint():
        test.with_user(c.admin1).unlink()
    # the model refuses too, not only the form's field lock (an admin may write fallbacks)
    with pytest.raises(REFUSED), c.env.cr.savepoint():
        fallback.with_user(c.admin1).write({"procedure": "something else"})


def test_a_plain_user_cannot_register_a_fallback(c, p03):
    conn = _connector(p03, c, pattern="sync_request", priority="p0")
    with pytest.raises(REFUSED), c.env.cr.savepoint():
        c.env["fix.integration.fallback"].with_user(c.plain).create(
            {
                "connector_id": conn.id,
                "fallback_type": "manual",
                "procedure": "x",
                "user_message": "x",
                "user_message_bn": "x",
            }
        )


# ============================================================ Batch file exchange
FILE = b"HDR|PAYROLL-2026-11\nD|1|1000.00\nD|2|2500.50\nTRL|2|3500.50\n"


def _batch(p03, c, connector, **extra):
    p03.as_user(c.admin1)
    vals = {
        "connector_id": connector.id,
        "direction": "outbound",
        "purpose": "beftn_payroll",
        "reference": "PAYROLL-2026-11",
        "file": base64.b64encode(FILE).decode(),
        "file_name": "payroll.txt",
        "declared_records": 2,
        "declared_total": 3500.50,
    }
    vals.update(extra)
    return p03.write(model="fix.integration.batch.run", values=vals)


def test_batch_run_needs_a_batch_file_integration(c, p03):
    conn = _connector(p03, c, pattern="sync_request", priority="p1")
    assert _batch(p03, c, conn).get("error")


def test_batch_run_is_verified_by_a_second_admin_counting_the_file(c, p03):
    conn = _connector(p03, c, pattern="batch_file", priority="p0")
    run = c.env["fix.integration.batch.run"].browse(made(_batch(p03, c, conn)))
    assert run.name.startswith("BFX/")
    assert run.file_sha256 == hashlib.sha256(FILE).hexdigest()
    p03.as_user(c.admin1)
    assert "second" in act_refused(
        p03,
        "fix.integration.batch.run",
        run,
        "action_verify",
        counted_records=2,
        counted_total=3500.50,
    )
    p03.as_user(c.admin2)
    assert "does not reconcile" in act_refused(
        p03,
        "fix.integration.batch.run",
        run,
        "action_verify",
        counted_records=2,
        counted_total=3500,
    )
    before = audits(c, "integration.batch_verified")
    act_ok(
        p03,
        "fix.integration.batch.run",
        run,
        "action_verify",
        counted_records=2,
        counted_total=3500.50,
    )
    assert run.state == "verified" and run.verified_by_id == c.admin2
    assert audits(c, "integration.batch_verified") == before + 1


def test_a_recorded_batch_never_changes_and_rejecting_needs_a_reason(c, p03):
    conn = _connector(p03, c, pattern="batch_file", priority="p1")
    run = c.env["fix.integration.batch.run"].browse(made(_batch(p03, c, conn)))
    p03.as_user(c.admin1)
    out = p03.write(
        model="fix.integration.batch.run", record_id=run.id, values={"declared_total": 1.0}
    )
    assert out.get("error"), out
    # the model refuses too, not only the form's field lock
    with pytest.raises(REFUSED), c.env.cr.savepoint():
        run.with_user(c.admin1).write({"declared_total": 1.0})
    out = p03.write(
        model="fix.integration.batch.run", record_id=run.id, values={"state": "verified"}
    )
    assert out.get("error") or run.state == "recorded"
    p03.as_user(c.admin2)
    assert act_refused(p03, "fix.integration.batch.run", run, "action_reject")
    act_ok(p03, "fix.integration.batch.run", run, "action_reject", reason="trailer total wrong")
    assert run.state == "rejected"


# ============================================================ API credentials
def _consumer(c, registered):
    # A person's new consumer awaits approval; seed both states explicitly.
    consumer = c.env["fix.api.consumer"].sudo().create({"name": "Partner App"})
    consumer._guarded().write({"registration_state": "registered" if registered else "draft"})
    return consumer


def _credential(p03, c, consumer, env_name, ref="vault://keys/partner-app/v1"):
    p03.as_user(c.admin1)
    return p03.write(
        model="fix.api.credential",
        values={"consumer_id": consumer.id, "environment": env_name, "secret_ref": ref},
    )


def test_production_credential_needs_a_registered_consumer(c, p03):
    consumer = _consumer(c, registered=False)
    assert "not registered" in _credential(p03, c, consumer, "production")["error"]
    sandbox = c.env["fix.api.credential"].browse(made(_credential(p03, c, consumer, "sandbox")))
    assert sandbox.client_id.startswith("cid-sand-") and sandbox.issued_by_id == c.admin1
    consumer._guarded().write({"registration_state": "registered"})
    made(_credential(p03, c, consumer, "production", "vault://keys/partner-app/prod/v1"))


def test_one_live_credential_per_environment_rotate_and_revoke(c, p03):
    consumer = _consumer(c, registered=True)
    cred = c.env["fix.api.credential"].browse(made(_credential(p03, c, consumer, "production")))
    assert (
        "already holds" in _credential(p03, c, consumer, "production", "vault://keys/x/v9")["error"]
    )
    act_ok(p03, "fix.api.credential", cred, "action_rotate")
    assert cred.revoked_at and cred.revoked_reason == "rotated"
    new = cred.replaced_by_id
    assert new.secret_ref == "vault://keys/partner-app/v2" and new.state == "active"
    assert new.client_id != cred.client_id
    assert act_refused(p03, "fix.api.credential", new, "action_revoke")
    before = audits(c, "integration.api_credential_revoked")
    act_ok(p03, "fix.api.credential", new, "action_revoke", reason="partner offboarded")
    assert new.state == "revoked"
    assert audits(c, "integration.api_credential_revoked") == before + 1


def test_issued_credential_stamps_cannot_be_typed(c, p03):
    consumer = _consumer(c, registered=True)
    cred = c.env["fix.api.credential"].browse(made(_credential(p03, c, consumer, "staging")))
    with pytest.raises(REFUSED), c.env.cr.savepoint():
        cred.with_user(c.admin1).write({"client_id": "cid-forged"})
    with pytest.raises(REFUSED), c.env.cr.savepoint():
        cred.with_user(c.admin1).write({"secret_ref": "vault://keys/other/v1"})
    with pytest.raises(REFUSED), c.env.cr.savepoint():
        c.env["fix.api.credential"].with_user(c.plain).create(
            {"consumer_id": consumer.id, "environment": "sandbox", "secret_ref": "vault://k/v1"}
        )


# ============================================================ Consumer replay
EVENT = "m28probe.thing_recorded"


@pytest.fixture
def consumers(c, monkeypatch):
    calls = {"a": [], "b": []}
    Ticket = type(c.env["fix.itsm.ticket"])
    monkeypatch.setattr(
        Ticket,
        "consume_m28probe_a",
        lambda self, e: calls["a"].append(e["event_id"]),
        raising=False,
    )
    monkeypatch.setattr(
        Ticket,
        "consume_m28probe_b",
        lambda self, e: calls["b"].append(e["event_id"]),
        raising=False,
    )
    Consumer = c.env["fix.event.consumer"].sudo()
    start = fields.Datetime.now() - timedelta(hours=2)
    a = Consumer.create(
        {
            "name": "probe A",
            "event_type": EVENT,
            "model": "fix.itsm.ticket",
            "method": "consume_m28probe_a",
            "active_from": start,
        }
    )
    b = Consumer.create(
        {
            "name": "probe B",
            "event_type": EVENT,
            "model": "fix.itsm.ticket",
            "method": "consume_m28probe_b",
            "active_from": start,
        }
    )
    Outbox = c.env["fix.event.outbox"].sudo()
    events = Outbox.browse()
    for i in range(3):
        events |= Outbox.emit(EVENT, "fix.itsm.ticket", i + 1, {"n": i})
    return types.SimpleNamespace(a=a, b=b, calls=calls, events=events)


def _replay(p03, c, consumer, since):
    p03.as_user(c.admin1)
    return p03.write(
        model="fix.event.consumer.replay",
        values={
            "consumer_id": consumer.id,
            "replay_from": fields.Datetime.to_string(since),
            "reason": "consumer bug fixed in release 4.2; reprocess",
        },
    )


def test_replay_reaches_that_consumer_only_after_a_second_admin(c, p03, consumers):
    since = fields.Datetime.now() - timedelta(minutes=30)
    replay = c.env["fix.event.consumer.replay"].browse(made(_replay(p03, c, consumers.a, since)))
    assert replay.event_count == 3
    act_ok(
        p03, "fix.event.consumer.replay", replay, "action_request_replay", justification="bug fixed"
    )
    assert not consumers.calls["a"], "nothing runs before the decision"
    before = audits(c, "integration.consumer_replayed")
    decide(c, replay, c.admin2)
    assert sorted(consumers.calls["a"]) == sorted(consumers.events.mapped("event_id"))
    assert consumers.calls["b"] == [], "FR-IPF-031: no side effect on another consumer"
    assert replay.state == "replayed" and replay.delivered_count == 3 and replay.failed_count == 0
    rows = (
        c.env["fix.event.consumer.delivery"]
        .sudo()
        .search([("subscription_id", "=", consumers.a.id)])
    )
    assert len(rows) == 3 and set(rows.mapped("state")) == {"done"}
    assert (
        not c.env["fix.event.consumer.delivery"]
        .sudo()
        .search_count([("subscription_id", "=", consumers.b.id)])
    )
    assert audits(c, "integration.consumer_replayed") == before + 1


def test_replay_is_bounded_and_one_shot(c, p03, consumers):
    c.env["ir.config_parameter"].sudo().set_param("fix.integration.replay_max_events", "2")
    wide = c.env["fix.event.consumer.replay"].browse(
        made(_replay(p03, c, consumers.a, fields.Datetime.now() - timedelta(hours=1)))
    )
    assert "narrow" in act_refused(
        p03, "fix.event.consumer.replay", wide, "action_request_replay", justification="x"
    )
    c.env["ir.config_parameter"].sudo().set_param("fix.integration.replay_max_events", "100")
    act_ok(p03, "fix.event.consumer.replay", wide, "action_request_replay", justification="x")
    decide(c, wide, c.admin2)
    assert wide.state == "replayed"
    p03.as_user(c.admin1)
    out = p03.write(
        model="fix.event.consumer.replay",
        record_id=wide.id,
        values={
            "replay_from": fields.Datetime.to_string(fields.Datetime.now() - timedelta(hours=2))
        },
    )
    assert out.get("error"), "a replay that ran is not re-pointed"
    assert act_refused(
        p03, "fix.event.consumer.replay", wide, "action_request_replay", justification="again"
    )
    # the workspace reads a datetime in the user's time zone (UTC+6): go well past it
    future = _replay(p03, c, consumers.a, fields.Datetime.now() + timedelta(days=2))
    assert future.get("error"), future
    other = (
        c.env["fix.event.consumer"]
        .sudo()
        .create(
            {
                "name": "probe C",
                "event_type": "m28probe.never_emitted",
                "model": "fix.itsm.ticket",
                "method": "consume_m28probe_a",
            }
        )
    )
    empty = c.env["fix.event.consumer.replay"].browse(
        made(_replay(p03, c, other, fields.Datetime.now() - timedelta(hours=1)))
    )
    assert "No m28probe.never_emitted event" in act_refused(
        p03, "fix.event.consumer.replay", empty, "action_request_replay", justification="x"
    )


def test_a_plain_user_cannot_request_a_replay(c, consumers):
    with pytest.raises(REFUSED), c.env.cr.savepoint():
        c.env["fix.event.consumer.replay"].with_user(c.plain).create(
            {"consumer_id": consumers.a.id, "replay_from": fields.Datetime.now(), "reason": "x"}
        )


# ============================================================ Inbound webhooks
SECRET = "whsec-m28p2-test"


@pytest.fixture
def hook(c, p03, monkeypatch):
    import odoo.addons.cd_itsm.controllers.inbound_webhook as iw

    monkeypatch.setenv("FIX_VAULT_HOOKS_BKASH_V1", SECRET)
    monkeypatch.setattr(iw, "_reply", lambda http_status, **body: (http_status, body))
    p03.as_user(c.admin1)
    source = c.env["fix.webhook.inbound.source"].browse(
        made(
            p03.write(
                model="fix.webhook.inbound.source",
                values={
                    "name": "bKash payment notifications",
                    "code": "bkash-pay",
                    "owning_module": "M20",
                    "route_key": "bkash.payment_notified",
                    "secret_ref": "vault://hooks/bkash/v1",
                    "replay_window_seconds": 300,
                },
            )
        )
    )

    def post(body, message_id="msg-1", stamp=None, secret=SECRET, code="bkash-pay"):
        raw = json.dumps(body).encode() if not isinstance(body, bytes) else body
        stamp = str(int(stamp if stamp is not None else time.time()))
        headers = {
            "webhook-id": message_id,
            "webhook-timestamp": stamp,
            "webhook-signature": iw._sign(secret, message_id, stamp, raw),
        }
        return iw.receive(c.env(su=True), code, headers, raw)

    return types.SimpleNamespace(source=source, post=post)


def _receipts(c, source, outcome):
    return (
        c.env["fix.webhook.inbound.event"]
        .sudo()
        .search_count([("source_id", "=", source.id), ("outcome", "=", outcome)])
    )


def test_a_new_source_receives_nothing_until_a_second_admin_takes_it_live(c, p03, hook):
    assert hook.source.state == "draft"
    status, _body = hook.post({"amount": 500})
    assert status == 403
    act_ok(
        p03,
        "fix.webhook.inbound.source",
        hook.source,
        "action_request_go_live",
        justification="M20 bKash",
    )
    decide(c, hook.source, c.admin2)
    assert hook.source.state == "active"


def _live(c, p03, hook):
    act_ok(
        p03,
        "fix.webhook.inbound.source",
        hook.source,
        "action_request_go_live",
        justification="M20",
    )
    decide(c, hook.source, c.admin2)


def test_a_verified_post_is_routed_once_as_an_event(c, p03, hook):
    _live(c, p03, hook)
    status, body = hook.post({"trx": "BK123", "amount": 500}, message_id="msg-42")
    assert status == 200 and body["status"] == "accepted", body
    event = c.env["fix.event.outbox"].sudo().search([("event_id", "=", body["event_id"])])
    assert event.event_type == "integration.webhook_received"
    payload = json.loads(event.payload)
    assert payload["route_key"] == "bkash.payment_notified" and payload["owning_module"] == "M20"
    assert payload["body"] == {"trx": "BK123", "amount": 500}
    again_status, again = hook.post({"trx": "BK123", "amount": 500}, message_id="msg-42")
    assert again_status == 200 and again["status"] == "duplicate"
    assert again["event_id"] == body["event_id"], "IP-04: the repeat gets the first answer"
    assert (
        c.env["fix.event.outbox"]
        .sudo()
        .search_count(
            [
                ("event_type", "=", "integration.webhook_received"),
                ("aggregate_id", "=", body["receipt"]),
            ]
        )
        == 1
    )
    assert (
        _receipts(c, hook.source, "accepted") == 1 and _receipts(c, hook.source, "duplicate") == 1
    )


def test_bad_signature_stale_post_and_non_object_are_refused_and_recorded(c, p03, hook):
    _live(c, p03, hook)
    assert hook.post({"a": 1}, secret="wrong")[0] == 401
    assert hook.post({"a": 1}, message_id="m-old", stamp=time.time() - 3600)[0] == 401
    assert hook.post(b"[1, 2]", message_id="m-list")[0] == 400
    assert _receipts(c, hook.source, "rejected") == 3
    assert _receipts(c, hook.source, "accepted") == 0
    status, _ = hook.post({"a": 1}, code="no-such-source")
    assert status == 401


def test_a_source_without_its_secret_value_refuses_everything(c, p03, hook, monkeypatch):
    _live(c, p03, hook)
    monkeypatch.delenv("FIX_VAULT_HOOKS_BKASH_V1")
    assert hook.post({"a": 1})[0] == 503


def test_receipts_are_written_by_the_receiver_only(c, p03, hook):
    _live(c, p03, hook)
    hook.post({"a": 1}, message_id="m-1")
    receipt = c.env["fix.webhook.inbound.event"].sudo().search([("source_id", "=", hook.source.id)])
    with pytest.raises(REFUSED), c.env.cr.savepoint():
        receipt.with_user(c.admin1).write({"outcome": "rejected"})
    p03.as_user(c.admin1)
    out = p03.write(
        model="fix.webhook.inbound.event",
        values={"source_id": hook.source.id, "message_id": "forged", "outcome": "accepted"},
    )
    assert out.get("error"), out


def test_moving_a_live_source_takes_it_out(c, p03, hook):
    _live(c, p03, hook)
    p03.as_user(c.admin1)
    made(
        p03.write(
            model="fix.webhook.inbound.source",
            record_id=hook.source.id,
            values={"route_key": "bkash.refund_notified"},
        )
    )
    assert hook.source.state == "draft"
