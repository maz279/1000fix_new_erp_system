# M27 capture audit (2026-11-14) - the captures the sub-module pages now
# offer, driven through the workspace endpoints (/p03/model/write and
# /p03/model/action) as NON-ADMIN users: the superuser is trusted by the
# model guards and would hide a gap.
#
#   * Wrap Up a Conversation (Agent Desktop): disposition + notes close the
#     agent's own conversation through action_resolve's gates; another agent
#     is refused.
#   * Set My Presence (Agent Desktop): the signed-in agent's presence changes
#     and the change is LOGGED as self-set; typing presence over the record is
#     refused by the whitelist.
#   * Log a Digital Contact (Digital Channels): an e-mail contact is saved
#     with its messages, and does not need a telephony SID or a wrap-up.
#   * DND Registry Entry (Consent Enforcement): a listed number is then
#     suppressed at send for promotional traffic.
#   * Notification Template: the Bengali body is saved from the workspace.
import itertools
from unittest import mock

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api

_SEQ = itertools.count(1)


class FakeRequest:
    def __init__(self, env):
        self.env = env


@pytest.fixture
def call():
    patchers = []

    def _call(env, route, **kw):
        p = mock.patch.object(api, "request", FakeRequest(env))
        p.start()
        patchers.append(p)
        return getattr(api.P03GenericApiController(), route)(**kw)

    yield _call
    for p in patchers:
        p.stop()


@pytest.fixture
def ou(odoo_env):
    return odoo_env["operating.unit"].search([], limit=1)


def _user(env, ou, *xmlids):
    n = next(_SEQ)
    groups = [env.ref("base.group_user").id] + [env.ref(x).id for x in xmlids]
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "M27 Capture User %d" % n,
                "login": "m27.capture.%d@a03.test" % n,
                "group_ids": [(6, 0, groups)],
                "operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )
    return env(user=user.id)


@pytest.fixture
def agent(odoo_env, ou):
    return _user(odoo_env, ou)


@pytest.fixture
def other_agent(odoo_env, ou):
    return _user(odoo_env, ou)


@pytest.fixture
def disposition(odoo_env):
    return odoo_env["fix.cc.disposition"].create(
        {"code": "M27CAP%d" % next(_SEQ), "name": "Status given", "category": "resolved"}
    )


def _handled_by(env, user_env, ou):
    """A conversation an agent is handling (claimed): state and agent are
    guarded, so they are set the way intake and claim set them."""
    conv = (
        env["fix.conversation"]
        .sudo()
        ._guarded()
        .create(
            {
                "channel": "chat",
                "contact_identity": "01711000%03d" % next(_SEQ),
                "operating_unit_id": ou.id,
                "state": "with_agent",
                "agent_id": user_env.uid,
            }
        )
    )
    return env["fix.conversation"].browse(conv.id)


NOTES = "Customer asked for the repair status; ETA given and confirmed."


def test_agent_wraps_up_their_conversation(call, odoo_env, agent, ou, disposition):
    conv = _handled_by(odoo_env, agent, ou)
    out = call(
        agent,
        "model_action",
        model="fix.conversation",
        ids=[conv.id],
        method="action_wrap_up",
        kwargs={"disposition_id": disposition.id, "wrapup_notes": NOTES, "fcr": True},
    )
    assert out.get("success"), out
    conv.invalidate_recordset()
    assert conv.state == "resolved_agent"
    assert conv.disposition_id == disposition and conv.fcr and conv.ended_at


def test_wrap_up_keeps_the_resolve_gates(call, odoo_env, agent, ou, disposition):
    conv = _handled_by(odoo_env, agent, ou)
    short = call(
        agent,
        "model_action",
        model="fix.conversation",
        ids=[conv.id],
        method="action_wrap_up",
        kwargs={"disposition_id": disposition.id, "wrapup_notes": "ok"},
    )
    assert not short.get("success") and "too short" in short["error"], short
    none = call(
        agent,
        "model_action",
        model="fix.conversation",
        ids=[conv.id],
        method="action_wrap_up",
        kwargs={"wrapup_notes": NOTES},
    )
    assert not none.get("success") and "disposition" in none["error"], none
    conv.invalidate_recordset()
    # the refused attempts left nothing behind (savepoint)
    assert conv.state == "with_agent" and not conv.disposition_id


def test_another_agent_cannot_close_my_conversation(
    call, odoo_env, agent, other_agent, ou, disposition
):
    conv = _handled_by(odoo_env, agent, ou)
    out = call(
        other_agent,
        "model_action",
        model="fix.conversation",
        ids=[conv.id],
        method="action_wrap_up",
        kwargs={"disposition_id": disposition.id, "wrapup_notes": NOTES},
    )
    assert not out.get("success") and "only that agent" in out["error"], out


def _statuses(env):
    Status = env["fix.cc.presence.status"].sudo()
    available = Status.search([("is_available_class", "=", True)], limit=1) or Status.create(
        {"name": "Available", "code": "m27cap_avail", "is_available_class": True}
    )
    offline = Status.search(
        [("is_available_class", "=", False), ("is_system_dnd", "=", False)], limit=1
    ) or Status.create({"name": "Offline", "code": "m27cap_off"})
    return available, offline


def test_agent_sets_their_own_presence_and_it_is_logged(call, odoo_env, agent):
    available, _offline = _statuses(odoo_env)
    out = call(
        agent,
        "model_action",
        model="fix.cc.presence.status",
        ids=[available.id],
        method="action_set_my_presence",
    )
    assert out.get("success"), out
    state = odoo_env["fix.cc.agent.state"].search([("agent_id", "=", agent.uid)])
    assert state.presence_status_id == available and state.presence_source == "manual"
    log = odoo_env["fix.cc.agent.state.log"].search(
        [("agent_id", "=", agent.uid), ("presence_status_id", "=", available.id)]
    )
    assert log and log[0].presence_source == "manual" and log[0].create_uid.id == agent.uid


def test_presence_cannot_be_typed_over(call, odoo_env, agent, other_agent):
    available, offline = _statuses(odoo_env)
    state = odoo_env["fix.cc.agent.state"].state_for(agent.uid)
    res = call(
        other_agent,
        "model_write",
        model="fix.cc.agent.state",
        record_id=state.id,
        values={"presence_status_id": available.id, "presence_source": "manual"},
    )
    state.invalidate_recordset()
    assert "error" in res or state.presence_status_id == offline, res
    assert state.presence_status_id != available


def test_an_email_contact_is_logged_with_its_messages(call, agent, ou):
    res = call(
        agent,
        "model_write",
        model="fix.conversation",
        values={
            "channel": "email",
            "contact_identity": "customer.m27@example.test",
            "operating_unit_id": ou.id,
            "started_at": "2026-11-14 04:00:00",
            "intent": "repair status",
        },
        lines={
            "field": "turn_ids",
            "rows": [
                {"values": {"sequence": 10, "speaker": "customer", "text": "Where is my laptop?"}},
                {"values": {"sequence": 20, "speaker": "agent", "text": "It is ready today."}},
            ],
        },
    )
    assert "id" in res, res
    conv = agent["fix.conversation"].browse(res["id"])
    assert conv.channel == "email" and conv.state == "new"
    assert len(conv.turn_ids) == 2 and not conv.call_sid


def test_a_typed_recording_url_is_refused(call, odoo_env, agent, ou):
    conv = _handled_by(odoo_env, agent, ou)
    res = call(
        agent,
        "model_write",
        model="fix.conversation",
        record_id=conv.id,
        values={"recording_url": "https://example.test/fake.wav"},
    )
    conv.invalidate_recordset()
    assert "error" in res or not conv.recording_url, res


def test_a_dnd_entry_suppresses_promotional_sends(call, odoo_env, ou):
    manager = _user(odoo_env, ou, "cd_entity_config.group_dofa_tier_2")
    number = "0171%07d" % (5000000 + next(_SEQ))
    res = call(
        manager,
        "model_write",
        model="fix.dnd.registry",
        values={"msisdn": number, "source": "customer_request", "registered_on": "2026-11-14"},
    )
    assert "id" in res, res
    Delivery = odoo_env["fix.notif.delivery"]
    reason = Delivery._dnd_reason("marketing", "sms", number)
    assert "Do-Not-Disturb" in reason
    assert Delivery._dnd_reason("service_updates", "sms", number) == ""


def test_a_clerk_cannot_list_a_number(call, agent):
    res = call(
        agent,
        "model_write",
        model="fix.dnd.registry",
        values={"msisdn": "01719999999", "source": "customer_request"},
    )
    assert "error" in res, res


def test_template_saves_its_bengali_body(call, agent):
    res = call(
        agent,
        "model_write",
        model="fix.cc.notif.template",
        values={
            "name": "M27 ready notice %d" % next(_SEQ),
            "channel": "sms",
            "consent_class": "marketing",
            "body": "Your device is ready.",
            "body_bn": "আপনার ডিভাইস প্রস্তুত।",
            "subject_bn": "প্রস্তুত",
        },
    )
    assert "id" in res, res
    tpl = agent["fix.cc.notif.template"].browse(res["id"])
    assert tpl.body_bn == "আপনার ডিভাইস প্রস্তুত।"
