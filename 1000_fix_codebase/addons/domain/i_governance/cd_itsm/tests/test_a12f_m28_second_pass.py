"""A12 finish, M28 second pass: Y01, Y02, Y04, Y05, Y06.

Walked as real Integration Admins through the controllers the screen calls, with the
kwargs m28.js sends. A decision goes through the M63 inbox task, as it does on the screen.
"""

from __future__ import annotations

import contextlib
import json
import types
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta
from odoo import fields
from odoo.addons.cd_itsm.models.fix_integration import _contract_narrowed
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py import fix_api_edge as edge

REFUSED = (UserError, ValidationError, AccessError)
IADMIN = "cd_itsm.group_integration_admin"
ALLOW_KEY = "fix.integration.webhook_allowlist"
HOST = "hooks.y28.test"
URL = "https://hooks.y28.test/in"
SECRET = "vault://webhooks/y28/v1"


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
        plain=_user(env, "y28_plain"),
        admin1=_user(env, "y28_admin1", [IADMIN]),
        admin2=_user(env, "y28_admin2", [IADMIN]),
        admin3=_user(env, "y28_admin3", [IADMIN]),
    )


@pytest.fixture
def p03(c):
    import odoo.addons.cd_p03_portal.controllers.a12 as a12mod
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g
    import odoo.addons.cd_p03_portal.controllers.p03_service_order_api as s

    ctl = g.P03GenericApiController()

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
            as_user=as_user,
        )
    finally:
        g.request, s.request, a12mod.request = saved


def attempt(env, fn):
    try:
        with env.cr.savepoint():
            fn()
        return None
    except REFUSED as exc:
        return str(exc)


def audits(c, event):
    return c.env["fix.security.audit"].sudo().search_count([("event", "=", event)])


def task_of(c, record):
    return (
        c.env["fix.workflow.task"]
        .sudo()
        .search([("request_id", "=", record.approval_request_id.id), ("state", "!=", "done")])
    )


def decide(c, record, user):
    tasks = task_of(c, record)
    mine = tasks.filtered(lambda t: t.assigned_user_id == user)
    assert mine, "no task for %s; routed to %s" % (
        user.login,
        tasks.assigned_user_id.mapped("login"),
    )
    mine.with_user(user).action_approve(comment="checked")


def request_ok(p03, model, record, method, kwarg, text="needed for the partner launch"):
    out = p03.action(model=model, ids=[record.id], method=method, kwargs={kwarg: text})
    assert out.get("success"), out
    return out


def refused(p03, model, record, method, kwargs=None):
    out = p03.action(model=model, ids=[record.id], method=method, kwargs=kwargs or {})
    assert not out.get("success"), "%s was accepted" % method
    return out["error"]


# ==================================================== Y01 endpoint lifecycle
def _endpoint(p03, c, code="Y1", path="/y28/route"):
    p03.as_user(c.admin1)
    made = p03.write(
        model="fix.api.endpoint",
        values={
            "code": code,
            "name": code,
            "version": "v1",
            "path": path,
            "method": "GET",
            "auth_type": "api_key",
        },
    )
    assert "error" not in made, made
    return c.env["fix.api.endpoint"].browse(made["id"])


def test_a12f_y01_lifecycle_walk_through_the_screen(c, p03):
    endpoint = _endpoint(p03, c)
    assert endpoint.lifecycle == "designed"
    model = "fix.api.endpoint"
    assert "published" in refused(p03, model, endpoint, "action_deprecate")
    assert "deprecated" in refused(p03, model, endpoint, "action_sunset", {"reason": "x"})
    assert p03.action(model=model, ids=[endpoint.id], method="action_publish_endpoint")["success"]
    assert endpoint.lifecycle == "published"
    too_soon = str(fields.Date.today() + timedelta(days=30))
    assert "earliest" in refused(p03, model, endpoint, "action_deprecate", {"sunset_on": too_soon})
    assert "YYYY" in refused(p03, model, endpoint, "action_deprecate", {"sunset_on": "soon"})
    # the empty prompt takes exactly six months
    out = p03.action(
        model=model, ids=[endpoint.id], method="action_deprecate", kwargs={"sunset_on": ""}
    )
    assert out.get("success"), out
    today = fields.Date.context_today(endpoint)
    assert endpoint.lifecycle == "deprecated" and endpoint.deprecated_on == today
    assert endpoint.sunset_on == today + relativedelta(months=6)
    # inside the notice
    assert "notice" in refused(p03, model, endpoint, "action_sunset", {"reason": "done"})
    endpoint.sudo().write({"sunset_on": today - timedelta(days=1)})
    # a registered consumer still calling blocks it (AUT-IPF-09)
    consumer = c.env["fix.api.consumer"].sudo().create({"name": "Y1 Caller"})
    row = (
        c.env["fix.integration.log"]
        .sudo()
        ._log_request("api", consumer=consumer, endpoint=endpoint)
    )
    assert "call(s)" in refused(p03, model, endpoint, "action_sunset", {"reason": "done"})
    c.env.flush_all()
    c.env.cr.execute(
        "UPDATE fix_integration_log SET created_at = created_at - interval '60 days' WHERE id=%s",
        (row.id,),
    )
    c.env.invalidate_all()
    assert "State why" in refused(p03, model, endpoint, "action_sunset")
    before = audits(c, "integration.endpoint_sunset")
    out = p03.action(
        model=model, ids=[endpoint.id], method="action_sunset", kwargs={"reason": "done"}
    )
    assert out.get("success"), out
    assert endpoint.lifecycle == "sunset" and not endpoint.active
    assert audits(c, "integration.endpoint_sunset") == before + 1


def test_a12f_y01_lifecycle_cannot_be_typed(c, p03):
    endpoint = _endpoint(p03, c)
    out = p03.write(model="fix.api.endpoint", record_id=endpoint.id, values={"lifecycle": "sunset"})
    assert "error" in out, out
    assert attempt(c.env, lambda: endpoint.with_user(c.admin1).write({"lifecycle": "published"}))
    assert attempt(c.env, lambda: endpoint.with_user(c.plain).action_publish_endpoint())


def test_a12f_y01_rows_from_before_read_as_published(c):
    assert (
        c.env["fix.api.endpoint"]
        .sudo()
        .create({"code": "OLD", "name": "OLD", "path": "/old"})
        .lifecycle
        == "published"
    )


@pytest.fixture
def edge_env(c, monkeypatch):
    @contextlib.contextmanager
    def same_env():
        yield c.env

    monkeypatch.setattr(edge, "_log_environment", same_env)
    box = types.SimpleNamespace(headers={})

    def bind(user):
        monkeypatch.setattr(
            edge,
            "request",
            types.SimpleNamespace(
                env=c.env(user=user.id),
                future_response=types.SimpleNamespace(headers=box.headers),
                make_json_response=lambda body, status=200: types.SimpleNamespace(
                    status_code=status, body=body
                ),
            ),
        )

    box.bind = bind
    return box


def test_a12f_y01_edge_signals_deprecation_and_refuses_a_sunset_route(c, edge_env):
    edge_env.bind(c.plain)
    endpoint = (
        c.env["fix.api.endpoint"].sudo().create({"code": "E", "name": "E", "path": "/y28/edge"})
    )
    served = edge.api_edge("/y28/edge")(lambda: {"ok": 1})
    assert served() == {"ok": 1} and not edge_env.headers
    endpoint.action_deprecate()
    assert served() == {"ok": 1}
    assert edge_env.headers["Deprecation"] == "true" and "GMT" in edge_env.headers["Sunset"]
    endpoint._guarded().write({"lifecycle": "sunset", "active": False})
    assert served()["error"]["code"] == "gone"
    http_route = edge.api_edge("/y28/edge", http_route=True)(lambda: {"ok": 1})
    assert http_route().status_code == 410


# ==================================================== Y02 BRU-IPF-05
def test_a12f_y02_an_endpoint_in_use_cannot_be_removed(c, p03):
    endpoint = _endpoint(p03, c)
    consumer = c.env["fix.api.consumer"].sudo().create({"name": "Y2"})
    c.env["fix.api.quota"].sudo().create({"consumer_id": consumer.id, "endpoint_id": endpoint.id})
    out = p03.write(model="fix.api.endpoint", record_id=endpoint.id, values={"active": False})
    assert "error" in out and "BRU-IPF-05" in out["error"], out
    assert attempt(c.env, lambda: endpoint.with_user(c.admin1).unlink())
    assert endpoint.active


def test_a12f_y02_traffic_alone_blocks_it(c, p03):
    endpoint = _endpoint(p03, c)
    consumer = c.env["fix.api.consumer"].sudo().create({"name": "Y2b"})
    c.env["fix.integration.log"].sudo()._log_request("api", consumer=consumer, endpoint=endpoint)
    assert attempt(c.env, lambda: endpoint.with_user(c.admin1).write({"active": False}))


def test_a12f_y02_a_published_version_goes_only_through_the_notice(c, p03):
    endpoint = _endpoint(p03, c)
    endpoint.with_user(c.admin1).action_publish_endpoint()
    message = attempt(c.env, lambda: endpoint.with_user(c.admin1).write({"active": False}))
    assert message and "Deprecate" in message
    assert attempt(c.env, lambda: endpoint.with_user(c.admin1).unlink())


def test_a12f_y02_a_design_nobody_uses_can_go_and_a_sunset_does_not_return(c, p03):
    endpoint = _endpoint(p03, c)
    endpoint.with_user(c.admin1).write({"active": False})
    assert not endpoint.active
    endpoint.with_user(c.admin1).write({"active": True})
    endpoint.with_user(c.admin1).unlink()
    gone = _endpoint(p03, c, code="Y3", path="/y28/three")
    gone.sudo()._guarded().write({"lifecycle": "sunset", "active": False})
    assert attempt(c.env, lambda: gone.with_user(c.admin1).write({"active": True}))


# ==================================================== Y04 reconciliation suppression
def _inject_divergence(c):
    """AC-15: a relay dead letter that never reached the DLQ, past the settling time."""
    Out = c.env["fix.event.outbox"].sudo()
    event = Out.emit("y28.dead", "x", 1, {"a": 1})
    consumer = (
        c.env["fix.event.consumer"]
        .sudo()
        .create(
            {
                "name": "Y4",
                "event_type": "y28.dead",
                "model": "fix.itsm.ticket",
                "method": "consume_y",
            }
        )
    )
    return (
        c.env["fix.event.consumer.delivery"]
        .sudo()
        .create(
            {
                "subscription_id": consumer.id,
                "event_id": event.id,
                "state": "dead",
                "delivered_at": fields.Datetime.now() - timedelta(hours=3),
            }
        )
    )


def _run(c):
    Run = c.env["fix.integration.reconciliation.run"].sudo()
    assert Run.cron_reconcile() > 0
    return Run.search(
        [("check_code", "=", "dead_letters"), ("company_id", "=", c.env.company.id)],
        order="id desc",
        limit=1,
    )


def _suppression(p03, c, hours=24, check="dead_letters"):
    p03.as_user(c.admin1)
    made = p03.write(
        model="fix.integration.reconciliation.suppression",
        values={
            "check_code": check,
            "reason": "known provider outage",
            "valid_until": str(fields.Datetime.now() + timedelta(hours=hours)),
        },
    )
    assert "error" not in made, made
    return c.env["fix.integration.reconciliation.suppression"].browse(made["id"])


def test_a12f_y04_divergence_raises_an_alert_and_a_person_records_the_investigation(c, p03):
    _inject_divergence(c)
    row = _run(c)
    assert row.state == "divergent" and row.divergences_found >= 1 and row.alerted
    assert c.admin1 in row.activity_ids.mapped("user_id")
    assert audits(c, "integration.reconciliation_divergence") >= 1
    p03.as_user(c.admin1)
    listed = p03.records(
        model="fix.integration.reconciliation.run",
        cols=["run_at", "check_code", "divergences_found", "state", "alerted"],
    )
    assert "error" not in listed, listed
    model = "fix.integration.reconciliation.run"
    assert "State what" in refused(p03, model, row, "action_resolve")
    out = p03.action(
        model=model, ids=[row.id], method="action_resolve", kwargs={"note": "mirror lag"}
    )
    assert out.get("success"), out
    assert row.resolved_by_id == c.admin1
    assert refused(p03, model, row, "action_resolve", {"note": "twice"})


def test_a12f_y04_suppression_needs_a_second_person_and_holds_back_only_the_alert(c, p03):
    _inject_divergence(c)
    suppression = _suppression(p03, c)
    model = "fix.integration.reconciliation.suppression"
    # not in force on the requester's say-so
    assert suppression.status == "requested"
    assert _run(c).state == "divergent"
    assert "State why" in refused(p03, model, suppression, "action_request_suppression")
    request_ok(p03, model, suppression, "action_request_suppression", "justification")
    assert suppression.approval_state == "pending" and suppression.status == "requested"
    assert _run(c).state == "divergent", "in force before anyone approved it"
    tasks = task_of(c, suppression)
    assert c.admin1 not in tasks.mapped("assigned_user_id"), "the requester decides his own"
    assert attempt(c.env, lambda: tasks.with_user(c.admin1).action_approve(comment="me"))
    # the direct path is shut as well
    assert attempt(c.env, lambda: suppression.with_user(c.admin1)._fix_apply_suppression())
    before = audits(c, "integration.reconciliation_suppressed")
    decide(c, suppression, c.admin2)
    assert suppression.status == "in_force" and suppression.approval_state == "approved"
    assert audits(c, "integration.reconciliation_suppressed") == before + 1
    # the check still runs and still records; only the alert is held back
    row = _run(c)
    assert row.state == "suppressed" and row.divergences_found >= 1
    assert not row.alerted and row.suppression_id == suppression
    # a decided suppression is not stretched by one person
    out = p03.write(
        model=model,
        record_id=suppression.id,
        values={"valid_until": str(fields.Datetime.now() + timedelta(days=2))},
    )
    assert "error" in out, out
    # ending it restores the alert
    assert p03.action(model=model, ids=[suppression.id], method="action_end")["success"]
    assert suppression.status == "ended"
    assert _run(c).state == "divergent"


def test_a12f_y04_suppression_is_time_boxed_and_expires(c, p03):
    p03.as_user(c.admin1)
    model = "fix.integration.reconciliation.suppression"
    for days in (30, -1):
        out = p03.write(
            model=model,
            values={
                "check_code": "dead_letters",
                "reason": "x",
                "valid_until": str(fields.Datetime.now() + timedelta(days=days)),
            },
        )
        assert "error" in out and "time-boxed" in out["error"], out
    _inject_divergence(c)
    suppression = _suppression(p03, c)
    request_ok(p03, model, suppression, "action_request_suppression", "justification")
    decide(c, suppression, c.admin2)
    c.env.flush_all()
    c.env.cr.execute(
        "UPDATE fix_integration_reconciliation_suppression SET valid_until = now() "
        "AT TIME ZONE 'UTC' - interval '1 minute' WHERE id=%s",
        (suppression.id,),
    )
    c.env.invalidate_all()
    assert suppression.status == "ended"
    assert _run(c).state == "divergent", "an expired suppression still held the alert"


def test_a12f_y04_suppression_covers_only_its_own_check_and_external_says_not_run(c, p03):
    _inject_divergence(c)
    model = "fix.integration.reconciliation.suppression"
    other = _suppression(p03, c, check="relay_lag")
    request_ok(p03, model, other, "action_request_suppression", "justification")
    decide(c, other, c.admin2)
    assert _run(c).state == "divergent"
    external = (
        c.env["fix.integration.reconciliation.run"]
        .sudo()
        .search([("check_code", "=", "external"), ("company_id", "=", c.env.company.id)], limit=1)
    )
    assert external.state == "not_run" and "Not reconciled" in external.detail


def test_a12f_y04_no_one_switches_the_job_off_or_edits_a_run(c, p03):
    cron = c.env.ref("cd_itsm.ir_cron_integration_reconcile")
    assert cron.active and "cron_reconcile" in cron.code
    Run = c.env["fix.integration.reconciliation.run"]
    assert attempt(c.env, lambda: Run.with_user(c.admin1).cron_reconcile())
    assert "external" not in dict(
        c.env["fix.integration.reconciliation.suppression"]._fields["check_code"].selection
    )
    row = _run(c)
    assert attempt(c.env, lambda: row.with_user(c.admin1).write({"state": "clean"}))
    p03.as_user(c.plain)
    assert "error" in p03.records(
        model="fix.integration.reconciliation.run", cols=["check_code", "state"]
    )
    assert attempt(
        c.env,
        lambda: c.env["fix.integration.reconciliation.suppression"]
        .with_user(c.plain)
        .create(
            {
                "check_code": "dead_letters",
                "reason": "x",
                "valid_until": str(fields.Datetime.now() + timedelta(days=1)),
            }
        ),
    )


# ==================================================== Y05 consumer registration
def test_a12f_y05_consumer_registration_walk(c, p03, edge_env):
    p03.as_user(c.admin1)
    made = p03.write(
        model="fix.api.consumer", values={"name": "Y5", "partner_id": c.plain.partner_id.id}
    )
    assert "error" not in made, made
    consumer = c.env["fix.api.consumer"].browse(made["id"])
    model = "fix.api.consumer"
    assert consumer.registration_state == "draft"
    assert "not registered" in refused(p03, model, consumer, "action_issue_key")
    # the edge does not recognise it, so its calls are not attributed to it
    edge_env.bind(c.plain)
    edge.api_edge("/y28/c")(lambda: {"ok": 1})()
    Log = c.env["fix.integration.log"].sudo()
    assert not Log.search_count([("consumer_id", "=", consumer.id)])
    assert "State why" in refused(p03, model, consumer, "action_request_registration")
    request_ok(p03, model, consumer, "action_request_registration", "justification")
    assert consumer.approval_state == "pending"
    tasks = task_of(c, consumer)
    assert c.admin1 not in tasks.mapped("assigned_user_id")
    assert attempt(c.env, lambda: tasks.with_user(c.admin1).action_approve(comment="me"))
    assert attempt(c.env, lambda: consumer.with_user(c.admin1)._fix_apply_registration())
    before = audits(c, "integration.consumer_registered")
    decide(c, consumer, c.admin2)
    assert consumer.registration_state == "registered" and consumer.approval_state == "approved"
    assert audits(c, "integration.consumer_registered") == before + 1
    assert p03.action(model=model, ids=[consumer.id], method="action_issue_key")["success"]
    edge.api_edge("/y28/c")(lambda: {"ok": 1})()
    assert Log.search_count([("consumer_id", "=", consumer.id)]) == 1
    # a different partner is a different registration
    other = c.env["res.partner"].sudo().create({"name": "Y5 Other"})
    p03.as_user(c.admin1)
    out = p03.write(model=model, record_id=consumer.id, values={"partner_id": other.id})
    assert "error" not in out, out
    assert consumer.registration_state == "draft" and consumer.approval_state == "none"


def test_a12f_y05_state_cannot_be_typed_and_plain_is_refused(c):
    consumer = c.env["fix.api.consumer"].with_user(c.admin1).create({"name": "Y5b"})
    assert attempt(c.env, lambda: consumer.write({"registration_state": "registered"}))
    assert attempt(c.env, lambda: consumer.write({"approval_state": "approved"}))
    assert attempt(
        c.env, lambda: consumer.with_user(c.plain).action_request_registration(justification="x")
    )


# ==================================================== Y05 webhook go-live
def _registered_consumer(c):
    return c.env["fix.api.consumer"].sudo().create({"name": "Y5 Registered"})


def _topic(c, code="y28.topic"):
    return c.env["fix.event.topic"].sudo().create({"code": code, "name": code})


def _new_webhook(p03, c, consumer=None, code="y28.topic"):
    p03.as_user(c.admin1)
    made = p03.write(
        model="fix.event.subscription",
        values={
            "consumer_id": (consumer or _registered_consumer(c)).id,
            "topic_id": _topic(c, code).id,
            "endpoint_url": URL,
            "secret_ref": SECRET,
        },
    )
    assert "error" not in made, made
    return c.env["fix.event.subscription"].browse(made["id"])


def _dispatch_rows(c, sub):
    c.env["fix.webhook.delivery"].sudo().cron_dispatch_webhooks()
    return c.env["fix.webhook.delivery"].sudo().search([("subscription_id", "=", sub.id)])


def test_a12f_y05_webhook_sends_nothing_until_a_second_admin_approves(c, p03):
    sub = _new_webhook(p03, c)
    model = "fix.event.subscription"
    assert sub.state == "draft"
    c.env["fix.event.outbox"].sudo().emit("y28.topic", "x", 1, {"a": 1})
    assert not _dispatch_rows(c, sub), "a webhook nobody approved was queued"
    assert "go-live approval" in refused(p03, model, sub, "action_resume", {"reason": "go"})
    assert "State why" in refused(p03, model, sub, "action_request_go_live")
    request_ok(p03, model, sub, "action_request_go_live", "justification")
    assert sub.approval_state == "pending" and sub.state == "draft"
    assert not _dispatch_rows(c, sub)
    tasks = task_of(c, sub)
    assert c.admin1 not in tasks.mapped("assigned_user_id")
    assert attempt(c.env, lambda: tasks.with_user(c.admin1).action_approve(comment="me"))
    before = audits(c, "integration.webhook_live")
    decide(c, sub, c.admin2)
    assert sub.state == "active" and sub.approval_state == "approved"
    assert audits(c, "integration.webhook_live") == before + 1
    assert _dispatch_rows(c, sub), "the approved webhook was not queued"
    # pause and resume stay with one person once it is approved
    assert p03.action(
        model=model, ids=[sub.id], method="action_pause", kwargs={"reason": "maintenance"}
    )["success"]
    assert p03.action(model=model, ids=[sub.id], method="action_resume", kwargs={"reason": "back"})[
        "success"
    ]
    assert sub.state == "active"


def test_a12f_y05_moving_an_approved_webhook_takes_it_out_of_service(c, p03):
    c.env["ir.config_parameter"].sudo().set_param(ALLOW_KEY, "%s other.y28.test" % HOST)
    sub = _new_webhook(p03, c)
    model = "fix.event.subscription"
    request_ok(p03, model, sub, "action_request_go_live", "justification")
    decide(c, sub, c.admin2)
    p03.as_user(c.admin1)
    out = p03.write(
        model=model, record_id=sub.id, values={"endpoint_url": "https://other.y28.test/in"}
    )
    assert "error" not in out, out
    assert sub.state == "draft" and sub.approval_state == "none"
    assert refused(p03, model, sub, "action_resume", {"reason": "go"})


def test_a12f_y05_a_webhook_from_before_the_route_also_stops_when_moved(c):
    c.env["ir.config_parameter"].sudo().set_param(ALLOW_KEY, "%s other.y28.test" % HOST)
    sub = (
        c.env["fix.event.subscription"]
        .sudo()
        .create(
            {
                "consumer_id": _registered_consumer(c).id,
                "topic_id": _topic(c).id,
                "endpoint_url": URL,
                "secret_ref": SECRET,
            }
        )
    )
    assert sub.state == "active"
    sub.with_user(c.admin1).write({"endpoint_url": "https://other.y28.test/in"})
    assert sub.state == "draft"


def test_a12f_y05_a_rejected_webhook_stays_out_and_a_recall_withdraws_it(c, p03):
    sub = _new_webhook(p03, c)
    model = "fix.event.subscription"
    request_ok(p03, model, sub, "action_request_go_live", "justification")
    out = p03.action(model=model, ids=[sub.id], method="action_recall_approval")
    assert out.get("success"), out
    assert sub.state == "draft" and sub.approval_state == "none"
    request_ok(p03, model, sub, "action_request_go_live", "justification")
    task_of(c, sub).filtered(lambda t: t.assigned_user_id == c.admin2).with_user(
        c.admin2
    ).action_reject(comment="no owner named")
    assert sub.state == "draft" and sub.approval_state == "rejected"


def test_a12f_y05_webhook_of_an_unregistered_consumer_cannot_go_live(c, p03):
    p03.as_user(c.admin1)
    made = p03.write(model="fix.api.consumer", values={"name": "Y5 Draft"})
    consumer = c.env["fix.api.consumer"].browse(made["id"])
    sub = _new_webhook(p03, c, consumer=consumer)
    message = refused(
        p03, "fix.event.subscription", sub, "action_request_go_live", {"justification": "x"}
    )
    assert "not registered" in message


# ==================================================== Y05 connector go-live
def _new_connector(p03, c, name="Y5 Conn"):
    p03.as_user(c.admin1)
    made = p03.write(
        model="fix.connector",
        # capture pass 2: BRU-IPF-13 / -12 - a connector declares its pattern and
        # priority before it can go live (P1: no fallback test needed).
        values={
            "name": name,
            "connector_type": "other",
            "endpoint": "https://hooks.y28.test/c",
            "pattern": "sync_request",
            "priority": "p1",
        },
    )
    assert "error" not in made, made
    return c.env["fix.connector"].browse(made["id"])


def _success_traffic(c, connector):
    c.env["fix.integration.log"].sudo()._log_request(
        "api", connector=connector, status="success", latency_ms=20
    )


def test_a12f_y05_connector_go_live_walk(c, p03):
    connector = _new_connector(p03, c)
    model = "fix.connector"
    assert connector.state == "registered" and connector.awaiting_go_live
    # neither a button nor good evidence puts it in service
    assert "go-live" in refused(p03, model, connector, "action_mark_live", {"reason": "seen ok"})
    _success_traffic(c, connector)
    assert p03.action(model=model, ids=[connector.id], method="action_probe")["success"]
    assert connector.state == "registered" and connector.last_success_at
    assert "State why" in refused(p03, model, connector, "action_request_go_live")
    request_ok(p03, model, connector, "action_request_go_live", "justification")
    tasks = task_of(c, connector)
    assert c.admin1 not in tasks.mapped("assigned_user_id")
    assert attempt(c.env, lambda: tasks.with_user(c.admin1).action_approve(comment="me"))
    before = audits(c, "integration.connector_live")
    decide(c, connector, c.admin2)
    assert connector.state == "live" and not connector.awaiting_go_live
    assert audits(c, "integration.connector_live") == before + 1
    assert refused(p03, model, connector, "action_request_go_live", {"justification": "again"})


def test_a12f_y05_repointing_a_live_connector_needs_go_live_again(c, p03):
    c.env["ir.config_parameter"].sudo().set_param(ALLOW_KEY, "%s other.y28.test" % HOST)
    connector = _new_connector(p03, c)
    model = "fix.connector"
    request_ok(p03, model, connector, "action_request_go_live", "justification")
    decide(c, connector, c.admin2)
    p03.as_user(c.admin1)
    # an unchanged echo and a rename leave it live
    out = p03.write(
        model=model,
        record_id=connector.id,
        values={"name": "Y5 New", "endpoint": connector.endpoint},
    )
    assert "error" not in out, out
    assert connector.state == "live"
    out = p03.write(
        model=model, record_id=connector.id, values={"endpoint": "https://other.y28.test/c"}
    )
    assert "error" not in out, out
    assert connector.state == "registered" and connector.awaiting_go_live
    assert connector.approval_state == "none"


def test_a12f_y05_connector_with_no_endpoint_or_off_list_cannot_go_live(c, p03):
    Connector = c.env["fix.connector"].with_user(c.admin1)
    bare = Connector.create({"name": "Bare", "pattern": "sync_request", "priority": "p1"})
    p03.as_user(c.admin1)
    assert "no endpoint" in refused(
        p03, "fix.connector", bare, "action_request_go_live", {"justification": "x"}
    )
    moved = _new_connector(p03, c)
    c.env["ir.config_parameter"].sudo().set_param(ALLOW_KEY, "elsewhere.test")
    assert "allow-list" in refused(
        p03, "fix.connector", moved, "action_request_go_live", {"justification": "x"}
    )


# ==================================================== Y05 DLQ discard
def _dlq_row(c):
    return (
        c.env["fix.event.dlq"]
        .sudo()
        .create({"topic_code": "y28.dl", "payload": "{}", "reason": "consumer exploded"})
    )


def test_a12f_y05_discard_takes_a_second_admin(c, p03):
    entry = _dlq_row(c)
    model = "fix.event.dlq"
    p03.as_user(c.admin1)
    assert "State why" in refused(p03, model, entry, "action_discard")
    request_ok(p03, model, entry, "action_discard", "reason", "superseded by a compensating event")
    assert entry.state == "pending" and entry.approval_state == "pending"
    assert entry.decision_reason == "superseded by a compensating event"
    # no replay around a discard waiting for a decision
    assert "awaiting approval" in refused(p03, model, entry, "action_replay", {"reason": "x"})
    tasks = task_of(c, entry)
    assert c.admin1 not in tasks.mapped("assigned_user_id")
    assert attempt(c.env, lambda: tasks.with_user(c.admin1).action_approve(comment="me"))
    assert attempt(c.env, lambda: entry.with_user(c.admin1)._fix_apply_discard())
    before = audits(c, "integration.dlq_discarded")
    decide(c, entry, c.admin2)
    assert entry.state == "discarded" and entry.approval_state == "approved"
    assert audits(c, "integration.dlq_discarded") == before + 1
    row = (
        c.env["fix.security.audit"]
        .sudo()
        .search([("event", "=", "integration.dlq_discarded")], order="id desc", limit=1)
    )
    assert "y28_admin1" in row.detail and "y28_admin2" in row.detail


def test_a12f_y05_recalled_discard_can_be_replayed_instead(c, p03):
    Out = c.env["fix.event.outbox"].sudo()
    consumer = (
        c.env["fix.event.consumer"]
        .sudo()
        .create(
            {
                "name": "Y5 dl",
                "event_type": "y28.dl2",
                "model": "fix.itsm.ticket",
                "method": "consume_missing",
                "active_from": fields.Datetime.now() - timedelta(days=1),
            }
        )
    )
    Out.emit("y28.dl2", "x", 1, {"a": 1})
    for _ in range(3):
        Out.cron_relay()
    delivery = (
        c.env["fix.event.consumer.delivery"].sudo().search([("subscription_id", "=", consumer.id)])
    )
    c.env["fix.event.dlq"].sudo().cron_sync_dead_letters()
    entry = c.env["fix.event.dlq"].sudo().search([("delivery_id", "=", delivery.id)])
    model = "fix.event.dlq"
    p03.as_user(c.admin1)
    request_ok(p03, model, entry, "action_discard", "reason", "looks stale")
    assert p03.action(model=model, ids=[entry.id], method="action_recall_approval")["success"]
    assert entry.approval_state == "none" and not entry.decision_reason
    out = p03.action(
        model=model,
        ids=[entry.id],
        method="action_replay",
        kwargs={"reason": "was not stale", "otp": ""},
    )
    assert out.get("success"), out
    assert entry.state == "replayed"


def test_a12f_y05_with_one_admin_the_engine_says_no_one_can_decide(c, p03):
    group = c.env.ref(IADMIN).sudo()
    others = group.user_ids - c.admin1
    group.write({"user_ids": [(3, u.id) for u in others]})
    entry = _dlq_row(c)
    p03.as_user(c.admin1)
    message = refused(p03, "fix.event.dlq", entry, "action_discard", {"reason": "stale"})
    assert "No one can approve" in message
    assert entry.state == "pending"


# ==================================================== Y06 breaking schema
def _schema(p03, c, user, version, contract, code="y28.s"):
    p03.as_user(user)
    made = p03.write(
        model="fix.event.schema",
        values={"code": code, "version": version, "schema_text": json.dumps(contract)},
    )
    assert "error" not in made, made
    return c.env["fix.event.schema"].browse(made["id"])


V1 = {
    "type": "object",
    "required": ["a"],
    "properties": {"a": {"type": "integer"}, "kind": {"enum": ["x", "y"]}},
}


def test_a12f_y06_breaking_version_takes_a_second_person_who_did_not_register_it(c, p03):
    model = "fix.event.schema"
    v1 = _schema(p03, c, c.admin1, 1, V1)
    assert p03.action(model=model, ids=[v1.id], method="action_publish")["success"]
    v2 = _schema(p03, c, c.admin1, 2, {"type": "object", "required": ["a", "b"]})
    message = refused(p03, model, v2, "action_publish")
    assert "Breaking-Change Exception" in message and "b is now required" in message
    assert v2.state == "draft"
    assert "State why" in refused(p03, model, v2, "action_request_breaking_exception")
    request_ok(p03, model, v2, "action_request_breaking_exception", "justification")
    tasks = task_of(c, v2)
    assert c.admin1 not in tasks.mapped("assigned_user_id")
    assert attempt(c.env, lambda: tasks.with_user(c.admin1).action_approve(comment="me"))
    assert attempt(c.env, lambda: v2.with_user(c.admin1)._fix_apply_breaking_publish())
    before = audits(c, "integration.schema_breaking_approved")
    decide(c, v2, c.admin2)
    assert v2.state == "published" and v2.approval_state == "approved"
    assert audits(c, "integration.schema_breaking_approved") == before + 1
    # dual-publish: the old version stays in force
    assert v1.state == "published"


def test_a12f_y06_the_engineer_who_registered_it_cannot_approve_it(c, p03):
    """Spec s13: admin1 registers, admin2 requests. Neither decides."""
    model = "fix.event.schema"
    v1 = _schema(p03, c, c.admin1, 1, V1)
    v1.with_user(c.admin1).action_publish()
    v2 = _schema(p03, c, c.admin1, 2, {"type": "array"})
    p03.as_user(c.admin2)
    request_ok(p03, model, v2, "action_request_breaking_exception", "justification")
    assignees = task_of(c, v2).mapped("assigned_user_id")
    assert c.admin1 not in assignees and c.admin2 not in assignees and c.admin3 in assignees
    decide(c, v2, c.admin3)
    assert v2.state == "published"


def test_a12f_y06_additive_version_publishes_directly(c, p03):
    model = "fix.event.schema"
    v1 = _schema(p03, c, c.admin1, 1, V1)
    v1.with_user(c.admin1).action_publish()
    additive = json.loads(json.dumps(V1))
    additive["properties"]["note"] = {"type": "string"}
    v2 = _schema(p03, c, c.admin1, 2, additive)
    assert p03.action(model=model, ids=[v2.id], method="action_publish")["success"]
    assert v2.state == "published"
    assert refused(p03, model, v2, "action_request_breaking_exception", {"justification": "x"})


def test_a12f_y06_editing_the_contract_voids_a_pending_exception(c, p03):
    model = "fix.event.schema"
    v1 = _schema(p03, c, c.admin1, 1, V1)
    v1.with_user(c.admin1).action_publish()
    v2 = _schema(p03, c, c.admin1, 2, {"type": "array"})
    request_ok(p03, model, v2, "action_request_breaking_exception", "justification")
    v2.with_user(c.admin1).write({"schema_text": json.dumps({"type": "string"})})
    assert v2.approval_state == "none" and v2.state == "draft"


@pytest.mark.parametrize(
    "new,fragment",
    [
        ({"type": "array"}, "type"),
        ({**V1, "required": ["a", "b"]}, "b is now required"),
        (
            {"type": "object", "required": ["a"], "properties": {"a": {"type": "integer"}}},
            "kind was removed",
        ),
        (
            {**V1, "properties": {"a": {"type": "string"}, "kind": V1["properties"]["kind"]}},
            "a type",
        ),
        (
            {**V1, "properties": {"a": V1["properties"]["a"], "kind": {"enum": ["x"]}}},
            "enum narrowed",
        ),
        ({**V1, "additionalProperties": False}, "extra properties"),
    ],
)
def test_a12f_y06_what_counts_as_breaking(new, fragment):
    assert any(fragment in problem for problem in _contract_narrowed(V1, new))


def test_a12f_y06_additive_changes_do_not_count():
    assert _contract_narrowed(V1, V1) == []
    wider = {**V1, "properties": {**V1["properties"], "extra": {"type": "string"}}}
    assert _contract_narrowed(V1, wider) == []
    enum_added = {
        **V1,
        "properties": {"a": V1["properties"]["a"], "kind": {"enum": ["x", "y", "z"]}},
    }
    assert _contract_narrowed(V1, enum_added) == []
