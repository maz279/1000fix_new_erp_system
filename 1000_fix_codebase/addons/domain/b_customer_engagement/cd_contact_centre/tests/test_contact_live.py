"""Behavioural tests for M27/M32 conversations and the P10 agent console API.

Live ORM (``odoo_env`` on fix_test, rolled back per test). The console API runs
with ``odoo.http.request`` replaced by a stand-in carrying the agent's ``env``.
"""

from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from odoo.addons.cd_contact_centre.controllers import contact_api
from odoo.addons.cd_contact_centre.controllers.contact_api import ContactApiController
from odoo.addons.cd_contact_centre.models import assistant_engine
from odoo.exceptions import AccessError, UserError

ORDER_STATUS_BN = "আমার সার্ভিস অর্ডারের বর্তমান অবস্থা কী?"
AGENT_REQUEST_EN = "I want to speak with a human agent"


@pytest.fixture
def env(odoo_env):
    return odoo_env


@pytest.fixture
def agent(env):
    """An internal console agent."""
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "Agent CC",
                "login": "agent@cc.test",
                "group_ids": [(4, env.ref("base.group_user").id)],
            }
        )
    )


@contextmanager
def _console(env, user):
    with patch.object(contact_api, "request", SimpleNamespace(env=env(user=user.id))):
        yield ContactApiController()


def _conv(env, **vals):
    vals.setdefault("operating_unit_id", env["operating.unit"].search([], limit=1).id)
    return env["fix.conversation"].create(vals)


def _customer_with_order(env, phone="01811222333"):
    """A real customer with a real service order at a real branch."""
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].create(
        {"code": "CCENT", "legal_name": "CC Entity", "company_id": env.company.id}
    )
    address = env["fix.bd.address"].create(
        {"division": "Dhaka", "district": "Dhaka", "upazila": "Zindabahar", "house": "12"}
    )
    branch = env["fix.branch"].create(
        {
            "name": "Zindabahar Branch",
            "code": "ZDB1",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
            "address_id": address.id,
            "phone": "01700999888",
        }
    )
    customer = env["res.partner"].create({"name": "CC Order Customer", "phone": phone})
    brand = env["fix.brand"].create({"name": "CCOBrand", "code": "CCOBR"})
    model = env["fix.device.model"].create({"name": "CCO Phone", "brand_id": brand.id})
    device = env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": customer.id, "serial_number": "SN-CCO-1"}
    )
    order = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "fault_description": "No power",
        }
    )
    order.write({"state": "intake"})
    return SimpleNamespace(customer=customer, order=order, branch=branch)


def _events(env, event_type, conv):
    return env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate_id", "=", conv.id)]
    )


# --- the conversation model -----------------------------------------------------------


def test_order_status_is_answered_from_the_customers_real_order(env):
    data = _customer_with_order(env)
    conv = _conv(env, state="with_ai", channel="chat", customer_id=data.customer.id)
    conv.intake_message(ORDER_STATUS_BN, lang="bn")
    turns = conv.turn_ids.sorted("sequence")
    assert [(t.sequence, t.speaker) for t in turns] == [(10, "customer"), (20, "ai")]
    # the order's REAL state (intake), never a canned "completed / in QC"
    assert data.order.name in turns[-1].text
    assert "ডিভাইসটি গ্রহণ করা হয়েছে" in turns[-1].text
    assert "কোয়ালিটি" not in turns[-1].text
    assert (conv.state, conv.ai_resolved, conv.intent) == ("resolved_ai", True, "order.status")
    assert conv.ended_at
    assert _events(env, "conversation.resolved", conv)


def test_order_status_for_an_unidentified_contact_hands_off(env):
    conv = _conv(env, state="with_ai", channel="chat")
    conv.intake_message("What is the status of my service order?", lang="en")
    reply = conv.turn_ids.sorted("sequence")[-1].text
    assert "order reference" in reply
    assert (conv.state, conv.ai_resolved) == ("with_agent", False)
    assert conv.handoff_reason == "order_reference_required"


def test_order_status_without_any_order_hands_off(env):
    customer = env["res.partner"].create({"name": "CC No Orders"})
    conv = _conv(env, state="with_ai", customer_id=customer.id)
    conv.intake_message("What is the status of my service order?", lang="en")
    assert (conv.state, conv.handoff_reason) == ("with_agent", "no_order_found")


def test_branch_locator_reads_the_branch_record(env):
    data = _customer_with_order(env)
    conv = _conv(env, state="with_ai")
    conv.intake_message(
        "Where is your Zindabahar service center and what are the hours?", lang="en"
    )
    reply = conv.turn_ids.sorted("sequence")[-1].text
    assert reply.startswith(data.branch.name)
    assert "Zindabahar" in reply and "01700999888" in reply
    assert "House 42" not in reply  # the old hard-coded Dhanmondi address
    assert (conv.state, conv.ai_resolved) == ("resolved_ai", True)
    unknown = _conv(env, state="with_ai")
    unknown.intake_message("Where is the nearest 1000FiX service outlet?", lang="en")
    assert (unknown.state, unknown.handoff_reason) == ("with_agent", "branch_not_identified")


def test_price_estimate_quotes_only_a_real_rate_card_line(env):
    conv = _conv(env, state="with_ai")
    conv.intake_message("How much does it cost to replace a screen?", lang="en")
    assert (conv.state, conv.handoff_reason) == ("with_agent", "price_requires_agent")
    assert "BDT 500" not in conv.turn_ids.sorted("sequence")[-1].text
    if "fix.rate.card" not in env:
        return
    env["product.product"].create({"name": "Zqx Screen", "default_code": "CC-ZQX-SCR"})
    env["fix.rate.card"].create({"product_code": "CC-ZQX-SCR", "unit_price": 2450.0})
    priced = _conv(env, state="with_ai")
    priced.intake_message("How much does it cost to replace a zqx screen?", lang="en")
    reply = priced.turn_ids.sorted("sequence")[-1].text
    assert "Zqx Screen" in reply and "2450.00" in reply
    assert (priced.state, priced.ai_resolved) == ("resolved_ai", True)


def test_booking_and_invoice_requests_never_claim_the_action(env):
    booking = _conv(env, state="with_ai")
    booking.intake_message("Book a home service visit for my TV", lang="en")
    reply = booking.turn_ids.sorted("sequence")[-1].text
    assert "has been booked" not in reply
    assert (booking.state, booking.ai_resolved) == ("with_agent", False)
    assert booking.handoff_reason == "appointment_requires_agent"
    invoice = _conv(env, state="with_ai")
    invoice.intake_message("Send me the invoice for my last repair", lang="en")
    reply = invoice.turn_ids.sorted("sequence")[-1].text
    assert "dispatched" not in reply
    assert (invoice.state, invoice.handoff_reason) == ("with_agent", "invoice_requires_agent")


def test_grounding_access_errors_hand_off(env):
    conv = _conv(env, state="with_ai")
    with patch.object(
        type(conv), "_ground_order_status", side_effect=AccessError("no read access")
    ):
        answer = conv._ground_intent_response("order.status", "status?")
    assert (answer["grounded"], answer["reason"]) == (False, "grounding_access_denied")
    unknown = conv._ground_intent_response("loyalty.balance", "points?")
    assert (unknown["grounded"], unknown["reason"]) == (False, "no_grounding_source")


def test_unresolvable_turn_hands_off_with_full_context(env):
    conv = _conv(env, state="with_ai", channel="whatsapp")
    env["fix.conversation.turn"].create(
        [
            {"conversation_id": conv.id, "sequence": 10, "speaker": "customer", "text": "Hi"},
            {"conversation_id": conv.id, "sequence": 20, "speaker": "ai", "text": "Hello!"},
        ]
    )
    conv.intake_message(AGENT_REQUEST_EN, lang="en")
    assert conv.state == "with_agent"
    assert conv.handoff_reason == "customer_requested_agent"
    assert [t.sequence for t in conv.turn_ids.sorted("sequence")][-2:] == [30, 40]
    [event] = _events(env, "conversation.handed_off", conv)
    assert '"turns": 4' in event.payload
    assert '"channel": "whatsapp"' in event.payload


def test_agent_turns_and_human_owned_conversations_bypass_the_assistant(env):
    conv = _conv(env, state="with_agent")
    conv.intake_message("Let me check that for you", speaker="agent", lang="en")
    conv.intake_message(ORDER_STATUS_BN, speaker="customer", lang="bn")
    assert conv.turn_ids.mapped("speaker") == ["agent", "customer"]
    assert (conv.state, conv.intent) == ("with_agent", False)


def test_an_unclassified_failure_still_hands_off(env):
    """T07: an unresolved turn never dead-ends, whatever the engine answers."""
    conv = _conv(env, state="with_ai")
    verdict = SimpleNamespace(
        matched_intent=None,
        resolvable=False,
        requires_handoff=False,
        handoff_reason="",
        response_text_bn="…",
        response_text_en="…",
    )
    with patch.object(
        assistant_engine.default_assistant_engine, "classify_intent", return_value=verdict
    ):
        conv.intake_message("???", lang="en")
    assert (conv.state, conv.handoff_reason) == ("with_agent", "escalation")


def test_resolution_rate_is_ai_over_ai_plus_handoffs(env):
    conversations = env["fix.conversation"]
    conversations.search([]).write({"ai_resolved": False, "handoff_reason": False})
    assert conversations.resolution_rate() == 0.0
    a, b, c = (_conv(env) for _ in range(3))
    a.action_resolve(by_ai=True)
    b.action_resolve(by_ai=True)
    c.action_handoff_to_agent(reason="complaint_escalation")
    assert conversations.resolution_rate() == 66.67
    agent_closed = _conv(env)
    agent_closed.action_resolve(by_ai=False)
    assert agent_closed.state == "resolved_agent"
    assert conversations.resolution_rate() == 66.67  # an agent close is no AI resolution


def test_hotline_call_is_captured_in_the_record(env):
    caller = env["res.partner"].create({"name": "Hotline Caller", "phone": "01911000111"})
    conv = env["fix.conversation"].intake_hotline_call(
        "01911000111", call_sid="CA-CC-1", initial_utterance=AGENT_REQUEST_EN, lang="en"
    )
    greeting = conv.turn_ids.sorted("sequence")[0]
    assert (conv.channel, conv.customer_id, conv.call_sid) == ("voice", caller, "CA-CC-1")
    assert greeting.text.startswith("Welcome to 1000FiX")
    assert conv.state == "with_agent"
    assert _events(env, "conversation.hotline_captured", conv)
    unknown = env["fix.conversation"].intake_hotline_call("01911999999")
    assert not unknown.customer_id
    assert unknown.turn_ids.text.startswith("১০০০ফিক্স")
    assert unknown.state == "with_ai"


def test_pii_is_masked_before_mining(env):
    conv = _conv(env)
    env["fix.conversation.turn"].create(
        {
            "conversation_id": conv.id,
            "speaker": "customer",
            "text": "Call +8801712345678 or mail rahim.k@example.com, NID 1234567890",
        }
    )
    assert conv.mask_pii_for_mining() is True
    assert conv.turn_ids.text == "Call [PHONE_MASKED] or mail [EMAIL_MASKED], NID [NID_MASKED]"
    assert conv.pii_masked is True


# --- the assistant engine -------------------------------------------------------------


def test_containment_bonus_lifts_a_longer_utterance():
    res = assistant_engine.AssistantEngine().classify_intent("Track my repair order please")
    assert res.matched_intent == "order.status"
    assert res.confidence >= 0.85


def test_samples_that_normalise_to_nothing_never_match():
    """Regression: an empty normalised sample is a substring of every utterance,
    so it took the 0.85 containment bonus for ANY input."""
    custom = {
        "noise": assistant_engine.IntentDefinition(
            code="noise",
            name="Noise",
            name_bn="শব্দ",
            description="",
            sample_bn=["???"],
            sample_en=["!!!"],
            grounding_source="none",
        ),
        "greeting": assistant_engine.IntentDefinition(
            code="greeting",
            name="Greeting",
            name_bn="শুভেচ্ছা",
            description="",
            sample_bn=["হ্যালো"],
            sample_en=["hello there"],
            grounding_source="none",
            auto_handoff=True,
        ),
    }
    engine = assistant_engine.AssistantEngine(intents=custom)
    assert [code for code, _norm, _lang in engine.sample_map] == ["greeting", "greeting"]
    weather = engine.classify_intent("what is the weather")
    assert weather.matched_intent is None
    assert weather.handoff_reason == "low_intent_confidence"
    greet = engine.classify_intent("hello there")
    assert (greet.matched_intent, greet.handoff_reason) == ("greeting", "auto_handoff_intent")


def test_an_intent_without_an_authored_answer_hands_off():
    custom = {
        "loyalty.balance": assistant_engine.IntentDefinition(
            code="loyalty.balance",
            name="Points balance",
            name_bn="পয়েন্ট ব্যালেন্স",
            description="",
            sample_bn=["আমার পয়েন্ট কত"],
            sample_en=["my points balance"],
            grounding_source="fix.loyalty.account",
        )
    }
    res = assistant_engine.AssistantEngine(intents=custom).classify_intent("my points balance")
    # never a generic "request accepted" claim for an action nobody performed
    assert (res.resolvable, res.requires_handoff) == (False, True)
    assert res.handoff_reason == "no_authored_answer"
    assert "accepted" not in res.response_text_en


# --- the agent console API ------------------------------------------------------------


def test_queue_lists_live_conversations_only(env, agent):
    live = _conv(env, state="with_ai", contact_identity="01700000001")
    done = _conv(env, state="resolved_ai")
    with _console(env, agent) as ctrl:
        res = ctrl.conversations()
    ids = [c["id"] for c in res["conversations"]]
    assert live.id in ids
    assert done.id not in ids
    row = next(c for c in res["conversations"] if c["id"] == live.id)
    assert (row["contact_identity"], row["turns"], row["intent"]) == ("01700000001", 0, "")


def test_detail_bundles_transcript_and_customer_360(env, agent):
    customer = env["res.partner"].create({"name": "CC 360 Customer"})
    anonymous = _conv(env)
    conv = _conv(env, customer_id=customer.id, intent="order.status")
    env["fix.conversation.turn"].create(
        [
            {"conversation_id": conv.id, "sequence": 20, "speaker": "ai", "text": "second"},
            {"conversation_id": conv.id, "sequence": 10, "speaker": "customer", "text": "first"},
        ]
    )
    brand = env["fix.brand"].create({"name": "CCBrand", "code": "CCBR"})
    model = env["fix.device.model"].create({"name": "CC Phone", "brand_id": brand.id})
    env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": customer.id, "serial_number": "SN-CC-360"}
    )
    with _console(env, env.ref("base.user_admin")) as ctrl:
        missing = ctrl.conversation_detail()
        unknown = ctrl.conversation_detail(conversation_id=999999999)
        bare = ctrl.conversation_detail(conversation_id=anonymous.id)
        full = ctrl.conversation_detail(conversation_id=conv.id)["conversation"]
    assert missing["error"]["code"] == "missing_conversation"
    assert unknown["error"]["code"] == "no_conversation"
    assert bare["conversation"]["customer_360"] == {
        "open_orders": [],
        "devices": [],
        "recent_conversations": [],
    }
    assert [t["text"] for t in full["transcript"]] == ["first", "second"]
    assert full["customer_360"]["devices"] == [
        {"model": "CC Phone", "identifier": "SN-CC-…", "warranty_status": "unknown"}
    ]
    assert [c["id"] for c in full["customer_360"]["recent_conversations"]] == [conv.id]
    assert full["customer_360"]["open_orders"] == []


def test_call_control_transitions(env, agent):
    conv = _conv(env, state="new")
    with _console(env, agent) as ctrl:
        invalid = ctrl.handoff(conversation_id=conv.id, action="transfer")
        unknown = ctrl.handoff(conversation_id=999999999, action="claim")
        claimed = ctrl.handoff(conversation_id=conv.id, action="claim")
        not_again = ctrl.handoff(conversation_id=conv.id, action="claim")
        back = ctrl.handoff(conversation_id=conv.id, action="handoff", reason="after hours")
        ended = ctrl.handoff(conversation_id=conv.id, action="end")
    assert invalid["error"]["code"] == "invalid_action"
    assert unknown["error"]["code"] == "no_conversation"
    assert claimed["conversation"]["state"] == "with_agent"
    assert not_again["error"]["code"] == "not_claimable"
    assert back["conversation"]["state"] == "with_ai"
    assert ended["conversation"]["state"] == "resolved_agent"
    assert conv.handoff_reason == "after hours"
    assert conv.ended_at


def test_a_refused_transition_is_reported(env, agent):
    conv = _conv(env, state="new")
    with (
        patch.object(type(conv), "write", side_effect=UserError("locked by supervisor")),
        _console(env, agent) as ctrl,
    ):
        res = ctrl.handoff(conversation_id=conv.id, action="end")
    assert res["error"] == {"code": "handoff_rejected", "message": "locked by supervisor"}


def test_softphone_seam_reads_system_parameters_only(env, agent):
    params = env["ir.config_parameter"].sudo()
    for key in ("fix_softphone_ws", "fix_softphone_sip_realm", "fix_softphone_vendor"):
        params.set_param(key, False)
    params.set_param("fix_softphone_dial_prefix", "+880")
    with _console(env, agent) as ctrl:
        res = ctrl.softphone()["softphone"]
    assert res == {
        "ws_url": None,
        "sip_realm": None,
        "click_to_call_prefix": "+880",
        "vendor": None,
    }


def test_telephony_webhook_captures_the_call_lifecycle(env, agent):
    _customer_with_order(env, phone="01811222333")
    with _console(env, agent) as ctrl:
        nothing = ctrl.telephony_webhook()
        started = ctrl.telephony_webhook(caller="01811222333", call_sid="CA-CC-9", lang="en")
        spoken = ctrl.telephony_webhook(
            call_sid="CA-CC-9", event="call.transcript", text="Track my repair order", lang="en"
        )
        quiet = ctrl.telephony_webhook(call_sid="CA-CC-9", event="call.dtmf")
        hung_up = ctrl.telephony_webhook(call_sid="CA-CC-9", event="call.hangup")
    assert nothing["error"]["code"] == "missing_telephony_data"
    conv_id = started["conversation"]["id"]
    assert spoken["conversation"]["id"] == conv_id
    assert spoken["conversation"]["state"] == "resolved_ai"  # answered from the real order
    assert quiet["conversation"]["turns"] == spoken["conversation"]["turns"] == 3
    assert hung_up["conversation"]["state"] == "resolved_ai"  # already closed: untouched


def test_telephony_hangup_closes_an_open_call(env, agent):
    with _console(env, agent) as ctrl:
        ctrl.telephony_webhook(**{"from": "01811222444", "session_id": "CA-CC-10"})
        ended = ctrl.telephony_webhook(call_sid="CA-CC-10", event="call.ended")
    assert ended["conversation"]["state"] == "resolved_agent"
    assert ended["conversation"]["ai_resolved"] is False


def test_a_call_without_a_session_id_opens_a_new_conversation(env, agent):
    with _console(env, agent) as ctrl:
        first = ctrl.telephony_webhook(caller="01811222555")
        second = ctrl.telephony_webhook(caller="01811222555")
    assert first["conversation"]["id"] != second["conversation"]["id"]
    assert not first["conversation"]["call_sid"]


def test_chat_message_intake(env, agent):
    known = env["res.partner"].create({"name": "Chat Known", "email": "known@cc.test"})
    with _console(env, agent) as ctrl:
        empty = ctrl.chat_message(message="")
        unknown = ctrl.chat_message(conversation_id=999999999, message="hi")
        opened = ctrl.chat_message(
            channel="whatsapp",
            contact_identity="known@cc.test",
            message=AGENT_REQUEST_EN,
            lang="en",
        )
        follow_up = ctrl.chat_message(
            conversation_id=opened["conversation"]["id"], text="Still there?", lang="en"
        )
        stranger = ctrl.chat_message(channel="pigeon", message=ORDER_STATUS_BN)
    assert empty["error"]["code"] == "empty_message"
    assert unknown["error"]["code"] == "not_found"
    conv = env["fix.conversation"].browse(opened["conversation"]["id"])
    assert (conv.channel, conv.customer_id) == ("whatsapp", known)
    assert opened["conversation"]["handoff_reason"] == "customer_requested_agent"
    assert opened["conversation"]["reply"].startswith("Transferring")
    assert follow_up["conversation"]["reply"] == ""  # an agent owns it now
    stranger_conv = env["fix.conversation"].browse(stranger["conversation"]["id"])
    assert (stranger_conv.channel, stranger_conv.customer_id.id) == ("chat", False)
    # an unidentified chatter is never told an order status: agent handoff
    assert stranger["conversation"]["ai_resolved"] is False
    assert stranger_conv.handoff_reason == "order_reference_required"
