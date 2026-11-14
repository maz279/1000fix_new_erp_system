"""M36 capture audit (2026-11-14): what the sub-module pages now capture,
driven as NON-ADMIN role holders through the workspace endpoints (the
superuser is trusted by the model guards and would hide a gap).

  * 5 Customer Approval Loop: an approved quotation is issued on a channel and
    the delivery is recorded (recipient defaulted from the customer); what was
    sent is fixed, delivery and views are tracked; "Quote Conversion by
    Channel" groups by the first delivery channel. A wrong acceptance code
    comes back as a warning, not as "Saved".
  * 6 Partial Accept & Counter: the customer's counter-offer or line-level
    partial acceptance is a record; whoever took it down does not decide it;
    "revise" derives the next draft version (declined lines out, the proposed
    price as an overall discount), "reject" needs a reason; a decided counter
    is frozen.
  * 7 e-Signature: the signed copy is uploaded with the request and accepts
    the quotation, by someone other than its author.
  * 8 Declined Handling: a governed reason; the service order gets the return
    / collection task with the diagnostic fee owed (BRU-QTE-12).
  * 3 Versioning and 4 Approval Routing run the workflow methods.
"""

import base64
import itertools
import types
from contextlib import contextmanager
from datetime import timedelta
from unittest import mock

import pytest
from odoo import Command, fields
from odoo.addons.cd_quotation.models.fix_quote_ops import estimate_untaxed
from odoo.addons.cd_service_order.models import fix_otp_util
from odoo.addons.cd_workflow_engine.tests.approval_helpers import inbox_task
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
AUTHOR = "cd_quotation.group_quotation_user"
_SEQ = itertools.count(1)


class FakeRequest:
    def __init__(self, env):
        self.env = env


def _ok(res):
    """The write endpoint answers {id, display_name}; the action one {success}."""
    return bool(res) and not res.get("error") and bool(res.get("success") or res.get("id"))


@contextmanager
def _refused(env, match=None):
    with pytest.raises(REFUSED, match=match), env.cr.savepoint():
        yield


def _user(env, login, *xmlids):
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": "%s.%d@m36cap.test" % (login, next(_SEQ)),
                "group_ids": [
                    Command.set([env.ref("base.group_user").id] + [env.ref(x).id for x in xmlids])
                ],
            }
        )
    )


@pytest.fixture
def api():
    from odoo.addons.cd_p03_portal.controllers import p03_generic_api as generic

    patchers = []

    def _call(user_env, route, **kw):
        p = mock.patch.object(generic, "request", FakeRequest(user_env))
        p.start()
        patchers.append(p)
        return getattr(generic.P03GenericApiController(), route)(**kw)

    yield _call
    for p in patchers:
        p.stop()


def _branch(env):
    b = env["fix.branch"].search([("operating_unit_id", "!=", False)], limit=1)
    if b:
        return b
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].search([], limit=1) or env["fix.entity"].create(
        {"legal_name": "M36C Test Entity", "code": "M36C", "company_id": env.company.id}
    )
    return env["fix.branch"].create(
        {
            "name": "M36C Branch",
            "code": "M36C-BR",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env, n=0)
    x.today = fields.Date.context_today(env.user)
    x.clerk = _user(env, "m36c_clerk")
    x.author = _user(env, "m36c_author", AUTHOR)
    x.agent = _user(env, "m36c_agent", AUTHOR)
    x.t1 = _user(env, "m36c_t1", "cd_entity_config.group_dofa_tier_1")
    x.t2 = _user(env, "m36c_t2", "cd_entity_config.group_dofa_tier_2")
    x.t3 = _user(env, "m36c_t3", "cd_entity_config.group_dofa_tier_3")
    x.branch = _branch(env)
    x.ou = x.branch.operating_unit_id or env["operating.unit"].search([], limit=1)
    x.customer = env["res.partner"].create(
        {"name": "M36C Customer", "phone": "01711000362", "email": "m36c@example.test"}
    )
    brand = env["fix.brand"].create({"name": "M36CBrand", "code": "M36C"})
    x.model = env["fix.device.model"].create({"name": "M36C Model", "brand_id": brand.id})
    x.env_of = lambda user: env(user=user.id)
    return x


def _quote(c, lines=((15000.0, "AMC service"),), user=None, **kw):
    vals = {
        "customer_id": c.customer.id,
        "cost_amount": 9000.0,
        "valid_until": c.today + timedelta(days=15),
        "quote_type": "contract",
        "operating_unit_id": c.ou.id,
        "payment_term_id": c.env.ref("account.account_payment_term_immediate").id,
    }
    if "estimate_id" not in kw:
        vals["line_ids"] = [
            (
                0,
                0,
                {
                    "description": desc,
                    "line_type": "recurring",
                    "unit_price": price,
                    "sequence": 10 * (i + 1),
                },
            )
            for i, (price, desc) in enumerate(lines)
        ]
    vals.update(kw)
    return c.env["fix.quotation"].with_user(user or c.author).create(vals)


def _approve(c, q):
    q.with_user(c.author).action_submit(justification="test")
    task = inbox_task(q, c.t1) or inbox_task(q, c.t2) or inbox_task(q, c.t3)
    task.with_user(task.assigned_user_id).action_approve(comment="ok")
    assert q.state == "approved", q.state
    return q


def _sent(c, **kw):
    q = _approve(c, _quote(c, **kw))
    q.with_user(c.author).action_send()
    assert q.state == "sent"
    return q


def _service_quote(c):
    c.n += 1
    env = c.env
    dev = env["fix.device"].create(
        {
            "device_model_id": c.model.id,
            "owner_id": c.customer.id,
            "serial_number": "M36C-%03d" % c.n,
        }
    )
    order = env["fix.service.order"].create(
        {
            "device_id": dev.id,
            "customer_id": c.customer.id,
            "branch_id": c.branch.id,
            "service_type": "walk_in",
            "order_category": "standard",
            "fault_description": "M36 capture test",
        }
    )
    est = env["fix.estimate"].create(
        {
            "order_id": order.id,
            "operating_unit_id": c.ou.id,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "line_type": "diagnostic",
                        "description": "diagnosis",
                        "quantity": 1,
                        "unit_price": 500.0,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "line_type": "labour",
                        "description": "labour",
                        "quantity": 1,
                        "unit_price": 2500.0,
                    },
                ),
            ],
        }
    )
    est.action_send()
    est.action_approve()
    q = _approve(
        c,
        c.env["fix.quotation"]
        .with_user(c.author)
        .create(
            {
                "estimate_id": est.id,
                "quote_type": "service",
                "cost_amount": 1000.0,
                "valid_until": c.today + timedelta(days=10),
                "payment_term_id": c.env.ref("account.account_payment_term_immediate").id,
            }
        ),
    )
    q.with_user(c.author).action_send()
    return q, order, est


# --- 5 Customer Approval Loop --------------------------------------------------------


def test_issue_on_a_channel_records_the_delivery_and_the_report_groups_by_it(c, api):
    q = _approve(c, _quote(c))
    res = api(
        c.env_of(c.author),
        "model_action",
        model="fix.quotation",
        ids=[q.id],
        method="action_issue_on_channel",
        kwargs={"channel": "whatsapp", "delivery_ref": "WA-778"},
    )
    assert _ok(res), res
    q.invalidate_recordset()
    assert q.state == "sent"
    d = q.delivery_ids
    assert len(d) == 1 and d.channel == "whatsapp" and d.delivery_ref == "WA-778"
    assert d.recipient == "01711000362"  # the customer's mobile, not typed
    assert d.version == q.version and d.recorded_by_id == c.author
    assert q.delivery_channel == "whatsapp" and q.delivery_count == 1

    from odoo.addons.cd_p03_portal.controllers.a04 import m36

    pack = m36.quote_conversion(c.env)
    row = next(r for r in pack["rows"] if r["channel"] == "WhatsApp")
    assert row["issued"] >= 1 and row["open"] >= 1
    assert "state" not in pack["cols"]


def test_issue_refuses_an_unknown_channel_and_a_clerk(c, api):
    q = _approve(c, _quote(c))
    with _refused(c.env, match="channel"):
        q.with_user(c.author).action_issue_on_channel(channel="pigeon")
    res = api(
        c.env_of(c.clerk),
        "model_action",
        model="fix.quotation",
        ids=[q.id],
        method="action_issue_on_channel",
        kwargs={"channel": "sms"},
    )
    assert not _ok(res)
    q.invalidate_recordset()
    assert q.state == "approved" and not q.delivery_ids


def test_a_delivery_is_fixed_once_recorded_and_its_views_only_grow(c, api):
    q = _sent(c)
    res = api(
        c.env_of(c.agent),
        "model_write",
        model="fix.quotation.delivery",
        values={"quotation_id": q.id, "channel": "email"},
    )
    assert _ok(res), res
    d = c.env["fix.quotation.delivery"].browse(res["id"])
    assert d.recipient == "m36c@example.test" and d.recorded_by_id == c.agent
    with _refused(c.env, match="fixed once recorded"):
        d.with_user(c.agent).write({"channel": "sms"})
    # the workspace sends what the user types: Dhaka wall-clock time
    seen = fields.Datetime.now() + timedelta(hours=6, minutes=1)
    res = api(
        c.env_of(c.agent),
        "model_write",
        model="fix.quotation.delivery",
        record_id=d.id,
        values={
            "delivered_at": fields.Datetime.to_string(seen),
            "first_viewed_at": fields.Datetime.to_string(seen),
            "view_count": 2,
        },
    )
    assert _ok(res), res
    assert d.view_count == 2
    with _refused(c.env, match="never goes down"):
        d.with_user(c.agent).write({"view_count": 1})
    with _refused(c.env):
        d.with_user(c.agent).unlink()
    draft = _quote(c)
    with _refused(c.env, match="issue it first"):
        c.env["fix.quotation.delivery"].with_user(c.agent).create(
            {"quotation_id": draft.id, "channel": "sms"}
        )
    with _refused(c.env):
        c.env["fix.quotation.delivery"].with_user(c.clerk).create(
            {"quotation_id": q.id, "channel": "sms"}
        )


def test_a_wrong_acceptance_code_is_a_warning_not_saved(c, api, monkeypatch):
    sent = []
    monkeypatch.setattr(
        fix_otp_util, "dispatch_otp", lambda phone, code, ttl, language="bn": sent.append(code)
    )
    q = _sent(c)
    q.with_user(c.author).action_send_acceptance_otp()
    wrong = "000000" if sent[-1] != "000000" else "111111"
    res = api(
        c.env_of(c.agent),
        "model_action",
        model="fix.quotation",
        ids=[q.id],
        method="action_verify_acceptance_otp",
        kwargs={"otp": wrong},
    )
    assert res.get("success") and "not correct" in (res["result"].get("warning") or "")
    q.invalidate_recordset()
    assert q.state == "sent"
    res = api(
        c.env_of(c.agent),
        "model_action",
        model="fix.quotation",
        ids=[q.id],
        method="action_verify_acceptance_otp",
        kwargs={"otp": sent[-1]},
    )
    assert _ok(res) and not res["result"].get("warning"), res
    q.invalidate_recordset()
    assert q.state == "accepted" and q.acceptance_method == "otp"


# --- 6 Partial Accept & Counter ---------------------------------------------------------


def test_a_counter_offer_is_decided_by_someone_else_and_revises_the_quotation(c, api):
    q = _sent(c)
    res = api(
        c.env_of(c.agent),
        "model_write",
        model="fix.quotation.counter",
        values={
            "quotation_id": q.id,
            "kind": "counter",
            "channel": "phone",
            "customer_request": "Will sign today at BDT 12,000.",
            "requested_value": 12000.0,
            "evidence_ref": "CALL-2026-11-14-031",
        },
    )
    assert _ok(res), res
    co = c.env["fix.quotation.counter"].browse(res["id"])
    assert co.state == "requested" and co.recorded_by_id == c.agent and co.version == 1
    # the person who took it down does not decide it
    res = api(
        c.env_of(c.agent),
        "model_action",
        model="fix.quotation.counter",
        ids=[co.id],
        method="action_decide",
        kwargs={"decision": "revise"},
    )
    assert not _ok(res) and "Segregation" in res.get("error", "")
    res = api(
        c.env_of(c.author),
        "model_action",
        model="fix.quotation.counter",
        ids=[co.id],
        method="action_decide",
        kwargs={"decision": "revise", "note": "Within the discount ladder."},
    )
    assert _ok(res), res
    co.invalidate_recordset()
    q.invalidate_recordset()
    new = co.revised_quotation_id
    assert co.state == "revised" and co.decided_by_id == c.author
    assert q.state == "superseded"
    assert new.version == 2 and new.state == "draft" and new.parent_version_id == q
    assert new.discount_amount == pytest.approx(3000.0) and new.value == pytest.approx(12000.0)
    # a decided counter is a record
    with _refused(c.env, match="not edited"):
        co.with_user(c.author).write({"customer_request": "changed"})


def test_a_partial_acceptance_drops_the_declined_lines(c, api):
    q = _sent(c, lines=((10000.0, "Server AMC"), (5000.0, "UPS AMC")))
    res = api(
        c.env_of(c.agent),
        "model_write",
        model="fix.quotation.counter",
        values={
            "quotation_id": q.id,
            "kind": "partial",
            "channel": "email",
            "customer_request": "Only the server AMC.",
        },
    )
    assert _ok(res), res
    co = c.env["fix.quotation.counter"].browse(res["id"])
    assert len(co.line_ids) == 2 and set(co.line_ids.mapped("decision")) == {"accept"}
    ups = co.line_ids.filtered(lambda r: r.description == "UPS AMC")
    # nothing declined yet: not a partial acceptance
    with _refused(c.env, match="declined"):
        co.with_user(c.author).action_decide(decision="revise")
    res = api(
        c.env_of(c.agent),
        "model_write",
        model="fix.quotation.counter",
        record_id=co.id,
        values={},
        lines={
            "field": "line_ids",
            "rows": [{"id": ups.id, "values": {"decision": "decline"}}],
            "removed": [],
        },
    )
    assert _ok(res), res
    assert ups.decision == "decline" and co.accepted_value == pytest.approx(10000.0)
    with _refused(c.env, match="Only the customer's decision"):
        ups.with_user(c.agent).write({"quotation_line_id": co.line_ids[0].quotation_line_id.id})
    co.with_user(c.author).action_decide(decision="revise")
    new = co.revised_quotation_id
    assert new.line_ids.mapped("description") == ["Server AMC"]
    assert new.value == pytest.approx(10000.0)


def test_counter_rules(c):
    q = _sent(c, lines=((10000.0, "A"), (5000.0, "B")))
    Counter = c.env["fix.quotation.counter"].with_user(c.agent)
    with _refused(c.env, match="above the quoted lines"):
        Counter.create(
            {
                "quotation_id": q.id,
                "channel": "sms",
                "customer_request": "x",
                "requested_value": 99999.0,
            }
        )
    co = Counter.create(
        {
            "quotation_id": q.id,
            "kind": "partial",
            "channel": "sms",
            "customer_request": "none of it",
        }
    )
    with _refused(c.env, match="awaiting its decision"):
        Counter.create({"quotation_id": q.id, "channel": "sms", "customer_request": "again"})
    co.line_ids.with_user(c.agent).write({"decision": "decline"})
    with _refused(c.env, match="declined every line"):
        co.with_user(c.author).action_decide(decision="revise")
    with _refused(c.env, match="why"):
        co.with_user(c.author).action_decide(decision="reject")
    co.with_user(c.author).action_decide(decision="reject", note="The price is the floor.")
    assert co.state == "rejected" and q.state == "sent"
    draft = _quote(c)
    with _refused(c.env, match="with the customer"):
        Counter.create({"quotation_id": draft.id, "channel": "sms", "customer_request": "x"})
    with _refused(c.env):
        c.env["fix.quotation.counter"].with_user(c.clerk).create(
            {"quotation_id": q.id, "channel": "sms", "customer_request": "x"}
        )
    sq, _order, _est = _service_quote(c)
    with _refused(c.env, match="estimate"):
        Counter.create({"quotation_id": sq.id, "channel": "sms", "customer_request": "cheaper"})


# --- 7 e-Signature -------------------------------------------------------------------------


def test_the_signed_copy_is_uploaded_with_the_acceptance(c, api):
    q = _sent(c)
    upload = {
        "upload": base64.b64encode(b"%PDF-1.4 signed by the customer").decode(),
        "filename": "signed.pdf",
    }
    res = api(
        c.env_of(c.author),
        "model_action",
        model="fix.quotation",
        ids=[q.id],
        method="action_record_signed_acceptance",
        kwargs={"attachment_id": dict(upload)},
    )
    assert not _ok(res) and "Segregation" in res.get("error", "")
    q.invalidate_recordset()
    assert q.state == "sent"
    res = api(
        c.env_of(c.agent),
        "model_action",
        model="fix.quotation",
        ids=[q.id],
        method="action_record_signed_acceptance",
        kwargs={"attachment_id": dict(upload)},
    )
    assert _ok(res), res
    q.invalidate_recordset()
    assert q.state == "accepted" and q.acceptance_method == "signed_form"
    assert q.signed_attachment_id.name == "signed.pdf" and q.evidence_hash


def test_someone_elses_upload_is_not_a_signed_copy(c):
    q = _sent(c)
    other = (
        c.env["ir.attachment"]
        .with_user(c.author)
        .create(
            {"name": "x.pdf", "raw": b"%PDF-1.4 x", "res_model": "fix.quotation", "res_id": q.id}
        )
    )
    with _refused(c.env, match="uploaded yourself"):
        q.with_user(c.agent).action_record_signed_acceptance(attachment_id=other.id)


# --- 8 Declined Handling ---------------------------------------------------------------------


def test_a_declined_repair_gives_the_order_its_return_task_and_fee(c, api):
    q, order, est = _service_quote(c)
    res = api(
        c.env_of(c.agent),
        "model_action",
        model="fix.quotation",
        ids=[q.id],
        method="action_decline",
        kwargs={"code": "price", "reason": "Too dear for an old phone."},
    )
    assert _ok(res), res
    q.invalidate_recordset()
    assert q.state == "declined" and q.decline_reason_code == "price"
    assert q.diagnostic_fee_due == pytest.approx(est.diagnostic_total) and q.diagnostic_fee_due > 0
    acts = c.env["mail.activity"].search(
        [("res_model", "=", "fix.service.order"), ("res_id", "=", order.id)]
    )
    act = acts.filtered(lambda a: "return or collect" in (a.summary or ""))
    assert act and "Diagnostic fee owed" in (act.note or "")
    assert estimate_untaxed(est) == pytest.approx(q.value)


def test_a_decline_without_a_governed_reason_is_refused(c, api):
    q = _sent(c)
    res = api(
        c.env_of(c.agent),
        "model_action",
        model="fix.quotation",
        ids=[q.id],
        method="action_decline",
        kwargs={"reason": "no"},
    )
    assert not _ok(res)
    q.invalidate_recordset()
    assert q.state == "sent"


# --- 3 Versioning, 4 Approval Routing ----------------------------------------------------------


def test_revise_and_submit_run_their_workflow(c, api):
    q = _quote(c)
    res = api(
        c.env_of(c.author),
        "model_action",
        model="fix.quotation",
        ids=[q.id],
        method="action_submit",
        kwargs={"justification": "Framework customer"},
    )
    assert _ok(res), res
    q.invalidate_recordset()
    assert q.approval_state == "pending" and q.state == "draft"
    task = inbox_task(q, c.t1) or inbox_task(q, c.t2) or inbox_task(q, c.t3)
    task.with_user(task.assigned_user_id).action_approve(comment="ok")
    q.with_user(c.author).action_send()
    res = api(
        c.env_of(c.author),
        "model_action",
        model="fix.quotation",
        ids=[q.id],
        method="action_revise",
        kwargs={},
    )
    assert _ok(res), res
    q.invalidate_recordset()
    assert q.state == "superseded"
    nxt = c.env["fix.quotation"].search([("name", "=", q.name), ("version", "=", 2)])
    assert nxt.state == "draft" and nxt.parent_version_id == q


# --- the workspace form re-sends every field it shows -------------------------------------


def test_a_full_form_save_changes_only_what_changed(c, api):
    """The form posts every field on save: unchanged frozen fields are no edit
    (the UI check on 14 Nov: saving the line decisions was refused for
    "kind, quotation_id"), a changed one still is."""
    q = _sent(c, lines=((10000.0, "Server AMC"), (5000.0, "UPS AMC")))
    co = (
        c.env["fix.quotation.counter"]
        .with_user(c.agent)
        .create(
            {
                "quotation_id": q.id,
                "kind": "partial",
                "channel": "email",
                "customer_request": "Server only.",
            }
        )
    )
    ups = co.line_ids.filtered(lambda r: r.description == "UPS AMC")
    res = api(
        c.env_of(c.agent),
        "model_write",
        model="fix.quotation.counter",
        record_id=co.id,
        values={
            "quotation_id": q.id,
            "kind": "partial",
            "channel": "email",
            "customer_request": "Server only.",
        },
        lines={
            "field": "line_ids",
            "rows": [{"id": ups.id, "values": {"decision": "decline"}}],
            "removed": [],
        },
    )
    assert _ok(res), res
    assert ups.decision == "decline"
    res = api(
        c.env_of(c.agent),
        "model_write",
        model="fix.quotation.counter",
        record_id=co.id,
        values={"kind": "counter"},
    )
    assert not _ok(res) and "kind" in res.get("error", "")

    d = q.delivery_ids[:1] or c.env["fix.quotation.delivery"].with_user(c.agent).create(
        {"quotation_id": q.id, "channel": "sms"}
    )
    # the form shows Dhaka wall-clock time to the minute
    local = fields.Datetime.to_string(d.sent_at + timedelta(hours=6))[:16] + ":00"
    later = fields.Datetime.to_string(d.sent_at + timedelta(hours=6, minutes=5))
    res = api(
        c.env_of(c.agent),
        "model_write",
        model="fix.quotation.delivery",
        record_id=d.id,
        values={
            "quotation_id": q.id,
            "channel": d.channel,
            "sent_at": local,
            "delivered_at": later,
        },
    )
    assert _ok(res), res
    assert d.delivered_at
    res = api(
        c.env_of(c.agent),
        "model_write",
        model="fix.quotation.delivery",
        record_id=d.id,
        values={"channel": "portal" if d.channel != "portal" else "app"},
    )
    assert not _ok(res) and "fixed once recorded" in res.get("error", "")
