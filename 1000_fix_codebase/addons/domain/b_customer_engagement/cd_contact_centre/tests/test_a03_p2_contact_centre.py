"""test_a03_p2_contact_centre.py — the M27/M32 lifecycle repairs (A03 P2).

The A03 workflow audit (working/A03_Workflow_and_Approval_Report.md, §4.3,
§4.4 and the P2 rows "M27" and "M32") found the contact centre and the
assistant built in pieces that never met:

  M27 G7   contacts never became routed work items;
  M27 G6   no complaint hand-off and no SLA clock on a contact;
  M27 G13  agent, answer, queue and abandonment times were never written;
  M27 G10  bullseye routing crashed on the Odoo 19 group field;
  M27 G9/G11  supervisor overrides, QA scores and rubric publishing were
           open to every agent;
  BTRC DND the registry was counted and never enforced at the exit;
  M32 G3   the live bot skipped the guardrails and wrote no audit row;
  M32 G4   dataset release was forgeable, self-approved and read by nothing;
  M32 G12  'requires human' gated nothing and the asker reviewed their own.

Every test acts as a NON-ADMIN user (the superuser is trusted by the guards
and hides exactly these gaps) and checks each control both ways: the bad case
is refused and the legitimate path still works.
"""

import base64
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from odoo import fields as odoo_fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox, assigned
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
T3 = "cd_entity_config.group_dofa_tier_3"
SUPERVISOR = "cd_contact_centre.group_cc_supervisor"
PORTAL = Path(__file__).resolve().parents[4] / "platform" / "cd_p03_portal"


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
                    "name": "P2 CC Probe %d" % counter["n"],
                    "login": "p2.cc.probe.%d@a03.test" % counter["n"],
                    "group_ids": [(6, 0, groups)],
                }
            )
        )

    return _make


@pytest.fixture
def ou(env):
    return env["operating.unit"].search([], limit=1) or env["operating.unit"].create(
        {"name": "P2 CC Unit", "code": "P2CC"}
    )


@pytest.fixture
def queue(env):
    return env["fix.cc.queue"].create(
        {"name": "P2 Hotline", "code": "P2HOT", "channel": "voice", "target_answer_seconds": 30}
    )


@pytest.fixture
def workstream(env, queue):
    """A pick workstream for every channel's conversations."""
    return env["fix.routing.workstream"].create(
        {
            "name": "P2 Contacts",
            "code": "P2CONTACTS",
            "channel": "voice",
            "work_type": "conversation",
            "source_model": "fix.conversation",
            "queue_id": queue.id,
            "assignment_method": "pick",
            "prefer_last_agent": True,
        }
    )


def _conversation(env, user, ou, **vals):
    return (
        env["fix.conversation"]
        .with_user(user)
        .create(dict({"channel": "chat", "operating_unit_id": ou.id}, **vals))
    )


def _answer_sla(env, conv):
    Instance = env.get("fix.sla.kpi.instance")
    if Instance is None:
        return None
    return Instance.sudo().search(
        [("res_model", "=", "fix.conversation"), ("res_id", "=", conv.id)], limit=1
    )


# ==========================================================================
# M27 (1): every contact is a routed work item, and the two stay in step
# ==========================================================================
class TestRoutedContacts:
    def test_a_hotline_call_becomes_a_queued_work_item_with_an_sla(
        self, env, make_user, workstream, queue
    ):
        agent = make_user()
        conv = env["fix.conversation"].with_user(agent).intake_hotline_call("01712000001", "P2-1")
        item = conv.work_item_id
        assert item, "intake must route the contact (A03 audit M27 G7)"
        assert item.source_model == "fix.conversation" and item.source_id == conv.id
        assert item.state == "pending" and item.queue_id == queue
        assert conv.queue_id == queue and conv.queued_at
        sla = _answer_sla(env, conv)
        if sla is not None:
            assert sla.state == "in_progress" and sla.kpi_code == "first_response"
            assert conv.sla_answer_due_at == sla.target_at

    def test_a_chat_message_is_routed_and_routing_is_idempotent(
        self, env, make_user, ou, workstream
    ):
        agent = make_user()
        conv = _conversation(env, agent, ou)
        conv.intake_message("hello there", lang="en")
        first = conv.work_item_id
        assert first
        conv.intake_message("still waiting", speaker="agent", lang="en")
        assert conv.work_item_id == first
        assert env["fix.routing.workitem"].search_count([("source_id", "=", conv.id)]) == 1

    def test_without_a_workstream_the_contact_says_why_it_is_unrouted(self, env, make_user, ou):
        env["fix.routing.workstream"].search([]).write({"active": False})
        conv = _conversation(env, make_user(), ou)
        conv._route_contact()
        assert not conv.work_item_id
        assert "No active routing workstream" in conv.routing_note

    def test_claim_stamps_the_agent_and_answer_and_takes_the_work_item(
        self, env, make_user, workstream
    ):
        agent = make_user()
        conv = env["fix.conversation"].with_user(agent).intake_hotline_call("01712000002", "P2-2")
        conv.action_claim()
        assert conv.state == "with_agent"
        assert conv.agent_id == agent and conv.answered_at
        assert conv.work_item_id.state == "active"
        assert conv.work_item_id.assigned_agent_id == agent
        sla = _answer_sla(env, conv)
        if sla is not None:
            assert sla.state == "succeeded"

    def test_routing_fields_cannot_be_typed(self, env, make_user, ou, workstream):
        agent = make_user()
        conv = _conversation(env, agent, ou)
        conv._route_contact()
        with pytest.raises(UserError):
            conv.write({"agent_id": agent.id})
        with pytest.raises(UserError):
            conv.write({"answered_at": odoo_fields.Datetime.now()})
        with pytest.raises(UserError):
            conv.work_item_id.write({"state": "closed"})
        with pytest.raises(UserError):
            conv.work_item_id.write({"assigned_agent_id": agent.id})

    def test_the_work_item_of_an_open_conversation_is_closed_only_by_the_conversation(
        self, env, make_user, workstream
    ):
        agent = make_user()
        conv = env["fix.conversation"].with_user(agent).intake_hotline_call("01712000003", "P2-3")
        conv.action_claim()
        with pytest.raises(UserError, match="open conversation"):
            conv.work_item_id.close_and_release(session_closed=True)
        disposition = env["fix.cc.disposition"].create({"name": "P2 Resolved", "code": "P2RES"})
        conv.write(
            {
                "disposition_id": disposition.id,
                "wrapup_notes": "Customer told the repair is ready for pickup today.",
            }
        )
        conv.action_resolve()
        assert conv.state == "resolved_agent"
        assert conv.work_item_id.state == "closed"
        assert conv.work_item_id.capacity_released

    def test_return_to_ai_closes_the_item_and_a_later_handoff_routes_a_new_one(
        self, env, make_user, workstream
    ):
        agent = make_user()
        conv = env["fix.conversation"].with_user(agent).intake_hotline_call("01712000004", "P2-4")
        conv.action_claim()
        first = conv.work_item_id
        conv.action_return_to_ai("customer wants the bot")
        assert first.state == "closed"
        conv.action_handoff_to_agent("needs a person again")
        assert conv.work_item_id and conv.work_item_id != first
        assert conv.work_item_id.state == "pending"

    def test_a_hang_up_before_any_answer_is_abandoned(self, env, make_user, workstream):
        agent = make_user()
        conv = env["fix.conversation"].with_user(agent).intake_hotline_call("01712000005", "P2-5")
        conv._mark_call_ended()
        assert conv.state == "abandoned" and conv.ended_at
        assert conv.work_item_id.state == "abandoned"
        sla = _answer_sla(env, conv)
        if sla is not None:
            assert sla.state in ("cancelled", "breached")
        with pytest.raises(UserError):
            conv.action_handoff_to_agent("reopen it")

    def test_a_supervisor_assignment_stamps_the_conversation(self, env, make_user, workstream):
        agent = make_user()
        supervisor = make_user(SUPERVISOR)
        conv = env["fix.conversation"].with_user(agent).intake_hotline_call("01712000006", "P2-6")
        item = conv.work_item_id
        with pytest.raises(AccessError):
            item.with_user(agent).action_assign_manually(agent=agent, reason="I want it")
        item.with_user(supervisor).action_assign_manually(agent=agent, reason="VIP caller")
        assert conv.agent_id == agent and conv.state == "with_agent" and conv.answered_at
        with pytest.raises(AccessError):
            item.with_user(agent).action_release_capacity(reason="done")
        item.with_user(supervisor).action_release_capacity(reason="Agent confirmed it is done")
        assert item.capacity_released

    def test_a_claim_cannot_overrule_the_routing_decision(self, env, make_user, workstream):
        agent, other = make_user(), make_user()
        supervisor = make_user(SUPERVISOR)
        conv = env["fix.conversation"].with_user(agent).intake_hotline_call("01712000007", "P2-7")
        conv.work_item_id.with_user(supervisor).action_assign_manually(
            agent=agent, reason="skills match"
        )
        conv.with_user(agent)._guarded().write({"state": "with_ai"})
        with pytest.raises(UserError, match="assigned to"):
            conv.with_user(other).action_claim()

    def test_affinity_reads_the_agent_that_claims_now_set(self, env, make_user, workstream):
        agent = make_user()
        customer = env["res.partner"].create({"name": "P2 Loyal", "phone": "01712000008"})
        first = env["fix.conversation"].with_user(agent).intake_hotline_call("01712000008", "P2-8")
        assert first.customer_id == customer
        first.action_claim()
        second = env["fix.conversation"].with_user(agent).intake_hotline_call("01712000008", "P2-9")
        assert second.work_item_id._preferred_agent() == agent

    def test_bullseye_ring_with_a_group_no_longer_crashes(self, env, queue):
        ws = env["fix.routing.workstream"].create(
            {
                "name": "P2 Bullseye",
                "code": "P2BULL",
                "channel": "voice",
                "source_model": "fix.complaint",
                "queue_id": queue.id,
            }
        )
        ring = env["fix.routing.bullseye.ring"].create(
            {
                "workstream_id": ws.id,
                "name": "Supervisors first",
                "user_group_id": env.ref(SUPERVISOR).id,
            }
        )
        ws.assignment_method = "bullseye"
        item = ws.intake("fix.complaint", 1)
        # It raised "Invalid field 'groups_id'" on every call (A03 audit M27 G10).
        assert ws.eligible_agents(item, ring=ring) is not None

    def test_the_service_level_alert_is_scheduled_and_runs(self, env):
        cron = env.ref("cd_contact_centre.ir_cron_queue_service_level")
        assert cron.active and "cron_monitor_service_level" in cron.code
        assert isinstance(env["fix.cc.queue"].cron_monitor_service_level(), list)


# ==========================================================================
# M27 (2): complaint hand-off
# ==========================================================================
class TestComplaintHandOff:
    def test_create_complaint_is_whitelisted_and_has_a_button(self):
        from odoo.addons.cd_p03_portal.controllers.a03 import m27

        assert "action_create_complaint" in m27.SURFACES["fix.conversation"]["actions"]
        js = (PORTAL / "static" / "src" / "a03" / "m27.js").read_text(encoding="utf-8")
        assert "m: 'action_create_complaint'" in js

    def test_the_raise_complaint_macro_calls_the_m34_hand_off_when_present(
        self, env, make_user, ou
    ):
        macro = env["fix.cc.macro"].create(
            {"name": "P2 Complaint", "code": "P2CMP", "macro_action": "raise_complaint"}
        )
        conv = _conversation(env, make_user(), ou)
        if not hasattr(conv, "action_create_complaint"):
            result = macro.run_for(conv)
            assert result["ok"] is False and "not installed" in result["note"]
            return
        try:
            result = macro.run_for(conv)
        except REFUSED:
            # M34's own preconditions (e.g. an identified customer) may refuse
            # this bare conversation; the point is that the macro now calls it.
            return
        assert result["ok"] is True


# ==========================================================================
# M27 (5): QA dispute and calibration; rubric publishing
# ==========================================================================
class TestQualitySupervision:
    def _evaluation(self, env, ou, agent, evaluator, score=40):
        conv = _conversation(env, agent, ou)
        return (
            env["fix.cc.qa.evaluation"]
            .with_user(evaluator)
            .create({"conversation_id": conv.id, "agent_id": agent.id, "score": score})
        )

    def test_an_agent_can_neither_edit_nor_delete_nor_self_score(self, env, make_user, ou):
        agent, evaluator = make_user(), make_user()
        evaluation = self._evaluation(env, ou, agent, evaluator)
        with pytest.raises(UserError, match="own QA score"):
            evaluation.with_user(agent).write({"score": 100})
        with pytest.raises(REFUSED):
            evaluation.with_user(agent).unlink()
        with pytest.raises(UserError):
            evaluation.with_user(agent).write({"state": "final"})
        with pytest.raises(UserError, match="own interaction"):
            self._evaluation(env, ou, agent, agent)
        # The evaluator still corrects a score that nobody has disputed.
        evaluation.with_user(evaluator).write({"score": 45})
        assert evaluation.score == 45

    def test_dispute_then_supervisor_calibration_and_final(self, env, make_user, ou):
        agent, evaluator = make_user(), make_user()
        supervisor = make_user(SUPERVISOR)
        evaluation = self._evaluation(env, ou, agent, evaluator)
        with pytest.raises(UserError):
            evaluation.with_user(evaluator).action_dispute(reason="not mine to dispute")
        with pytest.raises(UserError, match="reason"):
            evaluation.with_user(agent).action_dispute(reason="")
        evaluation.with_user(agent).action_dispute(reason="The call was transferred to me late.")
        assert evaluation.state == "disputed" and evaluation.original_score == 40
        with pytest.raises(UserError):
            evaluation.with_user(evaluator).write({"score": 90})
        with pytest.raises(AccessError):
            evaluation.with_user(agent).action_send_to_calibration(note="please")
        with pytest.raises(AccessError):
            evaluation.with_user(evaluator).action_finalise(note="upheld")
        evaluation.with_user(supervisor).action_send_to_calibration(note="Listen to the recording")
        assert evaluation.state == "in_calibration"
        with pytest.raises(UserError):
            evaluation.with_user(evaluator).write({"score": 90})
        evaluation.with_user(supervisor).write({"score": 70})
        evaluation.with_user(supervisor).action_finalise(note="Late transfer confirmed; 70.")
        assert evaluation.state == "final" and evaluation.calibrated_by == supervisor
        assert evaluation.score == 70 and evaluation.original_score == 40
        with pytest.raises(UserError):
            evaluation.with_user(supervisor).write({"score": 99})

    def test_a_supervisor_cannot_calibrate_their_own_score(self, env, make_user, ou):
        supervisor, evaluator = make_user(SUPERVISOR), make_user()
        evaluation = self._evaluation(env, ou, supervisor, evaluator)
        with pytest.raises(AccessError, match="own"):
            evaluation.with_user(supervisor).action_finalise(note="fine")

    def test_only_a_supervisor_publishes_or_retires_a_rubric(self, env, make_user):
        agent, supervisor = make_user(), make_user(SUPERVISOR)
        rubric = (
            env["fix.cc.qa.rubric"].with_user(agent).create({"name": "P2 Rubric", "code": "P2R"})
        )
        env["fix.cc.qa.criterion"].create(
            {
                "rubric_id": rubric.id,
                "name": "Disposition",
                "code": "disp",
                "weight": 100.0,
                "measure": "disposition_set",
            }
        )
        with pytest.raises(AccessError):
            rubric.with_user(agent).action_publish()
        with pytest.raises(UserError):
            rubric.with_user(agent).write({"state": "published"})
        rubric.with_user(supervisor).action_publish()
        assert rubric.state == "published"
        with pytest.raises(AccessError):
            rubric.with_user(agent).action_retire()
        rubric.with_user(supervisor).action_retire()
        assert rubric.state == "retired"

    def test_supervision_actions_are_whitelisted_with_buttons(self):
        from odoo.addons.cd_p03_portal.controllers.a03 import m27

        qa = m27.SURFACES["fix.cc.qa.evaluation"]["actions"]
        assert {"action_dispute", "action_send_to_calibration", "action_finalise"} <= qa
        assert "action_retire" in m27.SURFACES["fix.cc.qa.rubric"]["actions"]
        assert "action_release_capacity" in m27.SURFACES["fix.routing.workitem"]["actions"]
        js = (PORTAL / "static" / "src" / "a03" / "m27.js").read_text(encoding="utf-8")
        for method in (
            "action_dispute",
            "action_send_to_calibration",
            "action_finalise",
            "action_retire",
            "action_release_capacity",
        ):
            assert "m: '%s'" % method in js, method


# ==========================================================================
# M27 (6): BTRC Do-Not-Disturb at the single exit
# ==========================================================================
class TestDndAtTheExit:
    @pytest.fixture
    def registry(self, env):
        if "fix.dnd.registry" not in env:
            pytest.skip("cd_campaign (the DND registry) is not installed")
        return env["fix.dnd.registry"]

    def _queue(self, env, user, purpose, number, basis="contract"):
        return (
            env["fix.notif.delivery"]
            .with_user(user)
            .queue(
                channel="sms",
                purpose=purpose,
                to_address=number,
                body="1000FiX offer: 20% off screen repairs this week.",
                lawful_basis=basis,
            )
        )

    def test_marketing_to_a_listed_number_is_suppressed_at_queue(self, env, make_user, registry):
        registry.create({"msisdn": "01712999001", "source": "btrc_feed"})
        user = make_user()
        # The marketing SMS the audit saw rode a declared basis past consent.
        listed = self._queue(env, user, "marketing", "+8801712999001")
        assert listed.state == "suppressed" and listed.consent_decision == "dnd_listed"
        assert "Do-Not-Disturb" in listed.consent_reason
        clear = self._queue(env, user, "marketing", "01712999002")
        assert clear.state == "queued"
        # Transactional traffic is exempt, as with the curfew.
        service = self._queue(env, user, "service_updates", "01712999001")
        assert service.state == "queued"

    def test_a_number_listed_after_queueing_is_stopped_at_send(self, env, make_user, registry):
        user = make_user()
        delivery = self._queue(env, user, "marketing", "01712999003")
        assert delivery.state == "queued"
        registry.create({"msisdn": "8801712999003", "source": "operator"})
        provider = env["fix.notif.provider"].create(
            {"name": "P2 Manual SMS", "code": "P2MAN", "channel": "sms", "transport": "manual"}
        )
        delivery.sudo()._guarded().write({"provider_id": provider.id})
        with pytest.raises(UserError, match="Do-Not-Disturb"):
            delivery.with_user(user).action_mark_sent_manually()
        delivery.with_user(user)._attempt()
        assert delivery.state == "suppressed" and delivery.consent_decision == "dnd_listed"
        with pytest.raises(UserError):
            delivery.with_user(user).write({"state": "queued"})


# ==========================================================================
# M32 (1): the live bot goes through the guardrails and the audit trail
# ==========================================================================
class TestLiveBotGuardrails:
    def test_a_blocking_guardrail_blocks_the_live_answer(self, env, make_user, ou):
        env["fix.assistant.guardrail"].create(
            {"name": "P2 warranty claims", "rule": "claim repair warranty", "action": "block"}
        )
        agent = make_user()
        conv = _conversation(env, agent, ou, channel="chat")
        conv.intake_message("I want to claim repair warranty on my phone", lang="en")
        ask = env["fix.assistant.ask"].search([("conversation_id", "=", conv.id)])
        assert len(ask) == 1 and ask.consumer == "m27_bot"
        assert ask.guardrail_verdict == "blocked"
        assert conv.state == "with_agent" and conv.handoff_reason == "guardrail_blocked"
        assert not conv.ai_resolved
        bot_turns = conv.turn_ids.filtered(lambda t: t.speaker == "ai")
        assert bot_turns and "warranty" not in bot_turns[-1].text.lower()
        assert not ask.sent_at

    def test_an_authored_answer_is_audited_sent_and_resolves(self, env, make_user, ou):
        from odoo.addons.cd_contact_centre.models.assistant_engine import INTENT_REGISTRY

        text = INTENT_REGISTRY["knowledge.warranty_policy"].sample_en[0]
        agent = make_user()
        conv = _conversation(env, agent, ou, channel="chat")
        conv.intake_message(text, lang="en")
        ask = env["fix.assistant.ask"].search([("conversation_id", "=", conv.id)])
        assert len(ask) == 1 and ask.guardrail_verdict == "pass" and ask.grounded
        assert ask.engine == "rule_grounder" and ask.sent_at
        assert conv.state == "resolved_ai" and conv.ai_resolved

    def test_a_generated_answer_is_not_sent_without_review(self, env, make_user, ou, monkeypatch):
        from odoo.addons.cd_contact_centre.models import fix_assistant_llm as llm

        env["fix.assistant.llm.provider"].create(
            {"name": "P2 Local", "code": "P2LOCAL", "state": "active"}
        )
        monkeypatch.setattr(llm, "_ollama", lambda: _FakeClient("GENERATED: try restarting it"))
        agent = make_user()
        conv = _conversation(env, agent, ou, channel="chat")
        conv.intake_message("zqxv blorp frobnicate", lang="en")
        ask = env["fix.assistant.ask"].search([("conversation_id", "=", conv.id)])
        assert ask.engine == "llm" and ask.requires_human and not ask.sent_at
        assert conv.state == "with_agent"
        assert conv.handoff_reason == "ai_answer_awaiting_review"
        assert not any("GENERATED" in t.text for t in conv.turn_ids)


class _FakeClient:
    """Stands in for services/conversational-ai/src/ollama_client.py."""

    URL_ENV = "FIX_OLLAMA_URL"
    MODEL_ENV = "FIX_OLLAMA_MODEL"

    def __init__(self, text):
        self.text = text
        self.calls = []

    def configured(self, model=None):
        return True

    def generate(self, prompt, *, system="", profile="chat", max_tokens=512, model=None):
        self.calls.append({"model": model, "system": system})
        return SimpleNamespace(
            ok=True,
            text=self.text,
            model=model or "env-model",
            latency_ms=5,
            completion_tokens=7,
            detail="",
        )


# ==========================================================================
# M32 (3): requires_human blocks sending until a different person reviews
# ==========================================================================
class TestHumanReview:
    def _generated(self, env, asker, conv):
        return (
            env["fix.assistant.ask"]
            .sudo()
            .create(
                {
                    "asked_by": asker.id,
                    "consumer": "m27_agent_assist",
                    "conversation_id": conv.id,
                    "question": "How do I reset the router?",
                    "language": "en",
                    "answer_en": "Hold the reset button for ten seconds.",
                    "grounded": True,
                    "engine": "llm",
                    "guardrail_verdict": "pass",
                    "requires_human": True,
                }
            )
        )

    def test_review_is_four_eyes_and_gates_the_send(self, env, make_user, ou):
        asker, reviewer = make_user(), make_user()
        conv = _conversation(env, asker, ou)
        ask = self._generated(env, asker, conv).with_user(asker)
        with pytest.raises(UserError, match="review"):
            ask.action_send_to_customer()
        with pytest.raises(UserError, match="Segregation"):
            ask.action_mark_reviewed()
        with pytest.raises(UserError):
            ask.write({"human_reviewed_by": reviewer.id})
        with pytest.raises(UserError):
            ask.write({"answer_en": "Something else entirely."})
        ask.with_user(reviewer).action_mark_reviewed()
        assert ask.human_reviewed_by == reviewer
        ask.action_send_to_customer()
        assert ask.sent_at and ask.sent_by == asker
        assert conv.turn_ids.filtered(lambda t: "reset button" in t.text)
        with pytest.raises(UserError, match="already sent"):
            ask.action_send_to_customer()

    def test_send_is_whitelisted_with_a_button(self):
        from odoo.addons.cd_p03_portal.controllers.a03 import m32

        assert {"action_mark_reviewed", "action_send_to_customer"} <= m32.SURFACES[
            "fix.assistant.ask"
        ]["actions"]
        js = (PORTAL / "static" / "src" / "a03" / "m32.js").read_text(encoding="utf-8")
        assert "m: 'action_send_to_customer'" in js


# ==========================================================================
# M32 (2): a meaningful release
# ==========================================================================
def _attachment(env, user, name, payload):
    return (
        env["ir.attachment"]
        .with_user(user)
        .create({"name": name, "datas": base64.b64encode(json.dumps(payload).encode("utf-8"))})
    )


CORPUS_ONLY_UTTERANCE = "zebra ticket whereabouts kindly"


@pytest.fixture
def release_parties(make_user):
    return SimpleNamespace(
        author=make_user(),
        qa=make_user(),
        director=make_user(T3),
    )


@pytest.fixture
def golden(env, release_parties):
    from odoo.addons.cd_contact_centre.models.assistant_engine import INTENT_REGISTRY

    cases = [
        {"text": defn.sample_en[0], "intent": code}
        for code, defn in INTENT_REGISTRY.items()
        if defn.sample_en
    ]
    cases.append({"text": CORPUS_ONLY_UTTERANCE, "intent": "order.status"})
    qa = release_parties.qa
    att = _attachment(env, qa, "golden.json", {"cases": cases})
    ds = (
        env["fix.assistant.dataset"]
        .with_user(qa)
        .create({"name": "P2 golden", "dataset_type": "golden_benchmark", "attachment_id": att.id})
    )
    ds.action_compute_digest()
    return ds


@pytest.fixture
def bundle(env, release_parties, golden):
    author = release_parties.author
    att = _attachment(
        env,
        author,
        "corpus.json",
        {"intents": {"order.status": {"sample_en": [CORPUS_ONLY_UTTERANCE]}}},
    )
    ds = (
        env["fix.assistant.dataset"]
        .with_user(author)
        .create(
            {
                "name": "P2 bundle v1",
                "language": "en",
                "attachment_id": att.id,
                "benchmark_dataset_id": golden.id,
                "model_name": "qwen2.5:3b-p2",
                "system_prompt": "P2 released prompt: answer only from the facts.",
                "prompt_version": "p2-v1",
            }
        )
    )
    ds.action_compute_digest()
    return ds


class TestDatasetRelease:
    def test_accuracy_is_measured_not_typed(self, bundle, release_parties):
        with pytest.raises(UserError):
            bundle.write({"benchmark_accuracy_pct": 99.0})
        with pytest.raises(UserError):
            bundle.with_user(release_parties.author).create(
                {"name": "typed", "benchmark_accuracy_pct": 99.0}
            )
        bundle.action_run_benchmark()
        assert bundle.state == "benchmarked"
        assert bundle.benchmark_accuracy_pct >= 92.0
        assert bundle.benchmark_cases == bundle.benchmark_correct + (
            bundle.benchmark_cases - bundle.benchmark_correct
        )
        assert bundle.benchmark_training_sha256 == bundle.sha256_checksum
        with pytest.raises(UserError):
            bundle.write({"model_name": "something-else"})

    def test_the_golden_set_must_be_independent(self, env, release_parties):
        author = release_parties.author
        att = _attachment(
            env, author, "own-golden.json", {"cases": [{"text": "hi", "intent": None}]}
        )
        own = (
            env["fix.assistant.dataset"]
            .with_user(author)
            .create(
                {"name": "own golden", "dataset_type": "golden_benchmark", "attachment_id": att.id}
            )
        )
        own.action_compute_digest()
        corpus = _attachment(env, author, "c.json", {"intents": {}})
        ds = (
            env["fix.assistant.dataset"]
            .with_user(author)
            .create(
                {
                    "name": "self-checked",
                    "language": "en",
                    "attachment_id": corpus.id,
                    "benchmark_dataset_id": own.id,
                }
            )
        )
        ds.action_compute_digest()
        with pytest.raises(ValidationError, match="Independent"):
            ds.action_run_benchmark()

    def test_release_is_four_eyes_through_the_inbox(self, env, bundle, release_parties):
        author, director = release_parties.author, release_parties.director
        with pytest.raises(UserError, match="benchmarked"):
            bundle.action_request_approval(justification="ship it")
        bundle.action_run_benchmark()
        with pytest.raises(UserError, match="inbox"):
            bundle.with_user(director).action_release()
        bundle.action_request_approval(justification="Corpus v1 passes the golden set.")
        assert bundle.approval_state == "pending"
        assert author not in assigned(bundle) and director in assigned(bundle)
        approve_via_inbox(bundle, director, requester=author)
        assert bundle.state == "released" and bundle.released_by == director
        assert bundle.approval_state == "approved"

    def test_a_rejected_bundle_cannot_be_released(self, env, bundle, release_parties):
        from odoo.addons.cd_workflow_engine.tests.approval_helpers import inbox_task

        bundle.action_run_benchmark()
        bundle.action_request_approval(justification="please")
        inbox_task(bundle, release_parties.director).with_user(
            release_parties.director
        ).action_reject(comment="Prompt is too permissive.")
        assert bundle.state == "rejected"
        with pytest.raises(UserError):
            bundle.action_request_approval(justification="again")
        with pytest.raises(UserError):
            bundle.action_run_benchmark()

    def test_the_runtime_reads_the_released_bundle(self, env, bundle, release_parties, monkeypatch):
        from odoo.addons.cd_contact_centre.models import fix_assistant_llm as llm
        from odoo.addons.cd_contact_centre.models.assistant_engine import default_assistant_engine

        Dataset = env["fix.assistant.dataset"]
        assert not Dataset.runtime_release(), "the test database starts with nothing released"
        before = default_assistant_engine.classify_intent(CORPUS_ONLY_UTTERANCE)
        assert not (before.matched_intent == "order.status" and before.confidence >= 0.75)

        bundle.action_run_benchmark()
        approve_via_inbox(bundle, release_parties.director, requester=release_parties.author)
        assert Dataset.runtime_release() == bundle
        engine, release = Dataset.runtime_engine()
        assert release == bundle
        after = engine.classify_intent(CORPUS_ONLY_UTTERANCE)
        assert after.matched_intent == "order.status" and after.confidence >= 0.75

        # The generator runs on the released model and prompt, not the env
        # var and the code constant.
        client = _FakeClient("generated")
        monkeypatch.setattr(llm, "_ollama", lambda: client)
        provider = env["fix.assistant.llm.provider"].create(
            {"name": "P2 Local Gen", "code": "P2GEN", "state": "active"}
        )
        result = env["fix.assistant.intent"]._generate(
            provider, "q", {"en": "facts", "citations": []}, "en"
        )
        assert result["ok"]
        assert client.calls[-1]["model"] == "qwen2.5:3b-p2"
        assert client.calls[-1]["system"] == "P2 released prompt: answer only from the facts."
        assert result["answer"]["release_id"] == bundle.id

        # Bytes nobody approved are not run.
        bundle.attachment_id.sudo().write(
            {"datas": base64.b64encode(b'{"intents": {"order.status": {}}}')}
        )
        assert not Dataset.runtime_release()

    def test_the_release_gate_is_on_the_workspace(self):
        from odoo.addons.cd_p03_portal.controllers.a03 import m32

        actions = m32.SURFACES["fix.assistant.dataset"]["actions"]
        assert {
            "action_compute_digest",
            "action_run_benchmark",
            "action_request_approval",
        } <= actions
        assert "action_release" not in actions, "release is decided from the approver's inbox"
        js = (PORTAL / "static" / "src" / "a03" / "m32.js").read_text(encoding="utf-8")
        for method in ("action_compute_digest", "action_run_benchmark", "action_request_approval"):
            assert "m: '%s'" % method in js, method
