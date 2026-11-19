"""M32 capture audit pass 2 (2026-11-19), live: the new captures driven as
NON-ADMIN users through /p03/model/form|write|action and the live bot.

  * 1 Intent Recognition: category and a calibrated per-intent threshold are
    captured by a supervisor (not an agent); the live bot honours the
    threshold; a bundle that replaces production needs a passing shadow run.
  * 6 Guard Rails: a rule runs at its stage only; a supervisor reviews a
    firing (a false positive needs a note); the log measures precision.
  * 8 Agent Assistance: the agent edits the AI answer before sending it.
  * 9 Analytics: a no-answer handoff is logged to the unresolved queue once;
    a supervisor gives it a disposition; a knowledge gap closes against its
    M61 reference; the knowledge gap report counts it (KPI-184).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

HERE = Path(__file__).resolve().parent


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_p1 = _load("_m32_live_p1", "test_m32_capture_live.py")
_rel = _load("_m32_live_rel", "test_a03_p2_contact_centre.py")

# fixtures reused from the pass-1 suite and the release suite
c = _p1.c
p03 = _p1.p03
env = _rel.env
make_user = _rel.make_user
release_parties = _rel.release_parties
golden = _rel.golden
bundle = _rel.bundle

_form_fields = _p1._form_fields
_err = _p1._err
_conversation = _p1._conversation
_ask = _p1._ask
REFUSED = (UserError, ValidationError, AccessError)
TROUBLESHOOT = "My laptop is not turning on what should I do?"


def _events(env, kind, res_id):
    Outbox = env["fix.event.outbox"].sudo()
    field = "aggregate_id" if "aggregate_id" in Outbox._fields else "res_id"
    return Outbox.search([("event_type", "=", kind), (field, "=", res_id)])


def _intent(c, code):
    Intent = c.env["fix.assistant.intent"].sudo()
    row = Intent.with_context(active_test=False).search([("code", "=", code)], limit=1)
    return row or Intent.create({"code": code, "name": code, "name_bn": code, "sample_bn": "x"})


# ---------------------------------------------------------------- every capture opens
def test_the_pass2_captures_open_for_their_actor(c, p03):
    got = p03.form(c.sup1, model="fix.assistant.intent", fields=_form_fields("M32-form-intent"))
    assert not got.get("error"), got
    ask = _ask(c, c.agent, guardrail_verdict="blocked", guardrail_reason="Guardrail 'x' matched")
    conv = _conversation(c)
    row = (
        c.env["fix.assistant.unresolved"]
        .sudo()
        .create({"conversation_id": conv.id, "question": "m32c2 what is this"})
    )
    for screen, rec in (
        ("M32-form-guardrail-review", ask),
        ("M32-form-send-answer", ask),
        ("M32-form-unresolved-review", row),
        ("M32-form-gap-close", row),
        ("M32-form-unresolved", row),
    ):
        got = p03.form(c.sup2, model=rec._name, record_id=rec.id, fields=_form_fields(screen))
        assert not got.get("error"), (screen, got)
    got = p03.records(c.agent, model="fix.assistant.unresolved", cols=["question", "state"])
    assert not got.get("error"), got


# ---------------------------------------------------------------- 1 intent taxonomy
def test_a_supervisor_calibrates_an_intent_and_an_agent_cannot(c, p03):
    vals = {
        "code": "m32c2.probe",
        "name": "Probe",
        "name_bn": "প্রোব",
        "sample_bn": "প্রোব",
        "sample_en": "probe",
        "grounding": "none",
        "category": "status",
        "confidence_threshold": 0.9,
        "threshold_basis": "golden v3: precision 0.98 at 0.90",
    }
    assert _err(p03.write(c.agent, model="fix.assistant.intent", values=vals))
    got = p03.write(c.sup1, model="fix.assistant.intent", values=vals)
    assert not _err(got), got
    rec = c.env["fix.assistant.intent"].sudo().search([("code", "=", "m32c2.probe")])
    assert (rec.category, rec.confidence_threshold) == ("status", 0.9)
    with pytest.raises(ValidationError):
        rec.write({"confidence_threshold": 0.55})
    with pytest.raises(ValidationError):
        rec.write({"threshold_basis": False})
    for model in ("fix.assistant.dialogue", "fix.assistant.rag.source"):
        assert not c.env[model].with_user(c.agent).has_access("create"), model
        assert c.env[model].with_user(c.sup1).has_access("create"), model


def test_the_live_bot_honours_the_intents_own_threshold(c):
    """T-05: the same message is answered at the global 0.75 and handed off,
    then logged as unresolved, once the intent's threshold is above it."""
    engine, _rel_ = c.env["fix.assistant.dataset"].runtime_engine()
    text = TROUBLESHOOT + " please today"
    base = engine.classify_intent(text)
    assert base.matched_intent == "knowledge.troubleshooting" and 0.75 <= base.confidence < 0.99
    conv = _conversation(c)
    conv.intake_message(text, speaker="customer", lang="en")
    assert conv.state == "resolved_ai", conv.state

    intent = _intent(c, "knowledge.troubleshooting")
    intent.write(
        {"confidence_threshold": min(0.99, base.confidence + 0.01), "threshold_basis": "probe"}
    )
    assert c.env["fix.assistant.intent"].confidence_thresholds()["knowledge.troubleshooting"]
    conv2 = _conversation(c)
    conv2.intake_message(text, speaker="customer", lang="en")
    assert conv2.state != "resolved_ai"
    assert conv2.handoff_signal == "low_confidence"
    logged = c.env["fix.assistant.unresolved"].sudo().search([("conversation_id", "=", conv2.id)])
    assert len(logged) == 1
    assert logged.best_guess_intent == "knowledge.troubleshooting"
    assert _events(c.env, "assistant.unresolved", logged.id)


# ---------------------------------------------------------------- 1 shadow evaluation
def test_replacing_production_needs_a_passing_shadow_run(env, bundle, release_parties):
    from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox

    author, director = release_parties.author, release_parties.director
    Dataset = env["fix.assistant.dataset"]
    # the first release has nothing to shadow: the benchmark alone gates it
    bundle.action_run_benchmark()
    approve_via_inbox(bundle, director, requester=author)
    assert Dataset.runtime_release() == bundle

    att = _rel._attachment(
        env,
        author,
        "corpus2.json",
        {
            "intents": {
                "order.status": {"sample_en": [_rel.CORPUS_ONLY_UTTERANCE, "parcel where now"]}
            }
        },
    )
    v2 = Dataset.with_user(author).create(
        {
            "name": "P2 bundle v2",
            "language": "en",
            "attachment_id": att.id,
            "benchmark_dataset_id": bundle.benchmark_dataset_id.id,
        }
    )
    v2.action_compute_digest()
    with pytest.raises(UserError):
        v2.action_run_shadow()  # not benchmarked yet
    v2.action_run_benchmark()
    assert v2.state == "benchmarked"
    with pytest.raises(ValidationError, match="BRU-CAI-14"):
        v2.action_request_approval(justification="v2")
    with pytest.raises(UserError):
        v2.write({"shadow_state": "passed"})  # measured, never typed

    # live, PII-scrubbed traffic the shadow run replays
    ou = env["operating.unit"].search([], limit=1)
    conv = (
        env["fix.conversation"]
        .sudo()
        .create({"channel": "chat", "operating_unit_id": ou.id, "pii_masked": True})
    )
    Turn = env["fix.conversation.turn"].sudo()
    for i, text in enumerate(
        [TROUBLESHOOT, "WiFi not connecting to my device", _rel.CORPUS_ONLY_UTTERANCE, "hello"]
    ):
        Turn.create(
            {
                "conversation_id": conv.id,
                "sequence": 10 * (i + 1),
                "speaker": "customer",
                "text": text,
            }
        )
    v2.with_user(author).action_run_shadow()
    assert v2.shadow_turns >= 4
    assert v2.shadow_baseline_id == bundle
    assert v2.shadow_state == "passed", (
        v2.shadow_baseline_confident,
        v2.shadow_candidate_confident,
        v2.shadow_regressions,
    )
    assert v2.shadow_sha256 == v2.sha256_checksum
    assert _events(env, "model.evaluation_completed", v2.id)
    v2.action_request_approval(justification="v2 passes golden and shadow")
    assert v2.approval_state == "pending"


# ---------------------------------------------------------------- 6 guard rails
def test_a_rule_runs_at_its_own_stage(c):
    Rail = c.env["fix.assistant.guardrail"].sudo()
    Intent = c.env["fix.assistant.intent"]
    q = "m32c2 quantum warranty loophole please"
    rail = Rail.create(
        {
            "name": "m32c2 rail",
            "rule": "quantum warranty loophole",
            "action": "block",
            "stage": "output",
        }
    )
    assert not Intent._evaluate_guardrails(q, stage="input")["blocked"]
    assert Intent._evaluate_guardrails(q, stage="output")["blocked"]
    rail.stage = "input"
    assert Intent._evaluate_guardrails(q, stage="input")["blocked"]
    assert not Intent._evaluate_guardrails(q, stage="output")["blocked"]
    rail.stage = "both"
    assert Intent._evaluate_guardrails(q, stage="output")["blocked"]


def test_a_supervisor_reviews_a_firing_and_the_log_measures_it(c, p03):
    c.env["fix.assistant.guardrail"].sudo().create(
        {"name": "m32c2 review rail", "rule": "zircon refund loophole", "action": "block"}
    )
    res = (
        c.env["fix.assistant.intent"]
        .with_user(c.agent)
        .ask("m32c2 zircon refund loophole now", consumer="m27_agent_assist", language="en")
    )
    ask = c.env["fix.assistant.ask"].sudo().browse(res["ask_id"])
    assert ask.guardrail_verdict == "blocked" and ask.guardrail_fired

    def review(user, **kw):
        return p03.action(
            user,
            model="fix.assistant.ask",
            record_id=ask.id,
            method="action_review_guardrail",
            kwargs=kw,
        )

    assert _err(review(c.agent, verdict="confirmed"))
    assert _err(review(c.sup1, verdict="false_positive"))  # needs a note
    assert _err(review(c.sup1, verdict="maybe"))
    assert not ask.guardrail_review
    got = review(c.sup1, verdict="false_positive", note="customer quoted our own policy")
    assert not _err(got), got
    assert (ask.guardrail_review, ask.guardrail_reviewed_by) == ("false_positive", c.sup1)
    assert _err(review(c.sup2, verdict="confirmed"))  # reviewed once
    assert (
        _err(
            p03.write(
                c.sup1,
                model="fix.assistant.ask",
                record_id=ask.id,
                values={"guardrail_review": "confirmed"},
            )
        )
        or ask.guardrail_review == "false_positive"
    )

    from odoo.addons.cd_p03_portal.controllers.a03 import m32 as ctl

    pack = ctl.guardrail_status(c.env)
    row = next(r for r in pack["rows"] if r["name"] == "m32c2 review rail")
    assert (row["blocked"], row["reviewed"], row["false_positive"], row["precision"]) == (
        1,
        1,
        1,
        0.0,
    )


# ---------------------------------------------------------------- 8 agent assistance
def test_the_agent_edits_the_answer_before_sending_it(c, p03):
    conv = _conversation(c)
    ask = _ask(c, c.agent, conversation_id=conv.id)
    ask.with_user(c.agent2).action_mark_reviewed()
    form = p03.form(
        c.agent2,
        model="fix.assistant.ask",
        record_id=ask.id,
        fields=_form_fields("M32-form-send-answer"),
    )
    assert not form.get("error"), form
    edited = "Your phone is in repair; we will SMS you when it is ready."
    got = p03.action(
        c.agent2,
        model="fix.assistant.ask",
        record_id=ask.id,
        method="action_send_to_customer",
        kwargs={"reply": edited},
    )
    assert not _err(got), got
    turn = conv.turn_ids.sorted("sequence")[-1]
    assert (turn.speaker, turn.text) == ("agent", edited)
    assert ask.sent_text == edited and ask.edited_by_agent
    assert ask.answer_en == "Your phone is in repair."  # the AI draft stays on record
    assert _events(c.env, "assistant.answer_corrected", ask.id)

    conv2 = _conversation(c)
    ask2 = _ask(c, c.agent, conversation_id=conv2.id, requires_human=False)
    ask2.with_user(c.agent2).action_send_to_customer(reply=ask2.draft_reply)
    turn2 = conv2.turn_ids.sorted("sequence")[-1]
    assert (turn2.speaker, ask2.edited_by_agent) == ("ai", False)
    assert not _events(c.env, "assistant.answer_corrected", ask2.id)


# ---------------------------------------------------------------- 9 unresolved queue
def test_a_no_answer_handoff_is_logged_once_and_reviewed(c, p03):
    conv = _conversation(c)
    conv.intake_message("m32c2 xylophone marmalade quorum", speaker="customer", lang="en")
    assert conv.handoff_signal == "low_confidence"
    Unresolved = c.env["fix.assistant.unresolved"].sudo()
    row = Unresolved.search([("conversation_id", "=", conv.id)])
    assert len(row) == 1 and row.state == "open"
    conv.action_handoff_to_agent(reason="low_intent_confidence")
    assert Unresolved.search_count([("conversation_id", "=", conv.id)]) == 1
    with pytest.raises(REFUSED):
        row.with_user(c.sup1).write({"question": "typed"})

    # a guard-rail handoff is not a knowledge question
    other = _conversation(c)
    other.turn_ids.create(
        {"conversation_id": other.id, "speaker": "customer", "text": "m32c2 abc", "sequence": 10}
    )
    other.action_handoff_to_agent(reason="guardrail_blocked")
    assert not Unresolved.search_count([("conversation_id", "=", other.id)])

    def act(user, method, **kw):
        return p03.action(
            user, model="fix.assistant.unresolved", record_id=row.id, method=method, kwargs=kw
        )

    assert _err(act(c.agent, "action_review", disposition="knowledge_gap"))
    assert _err(act(c.sup1, "action_review", disposition="no_action"))  # needs a reason
    assert _err(act(c.sup1, "action_close_gap", gap_ref="KB-1"))  # not reviewed yet
    got = act(c.sup1, "action_review", disposition="knowledge_gap", note="no article on this")
    assert not _err(got), got
    assert (row.state, row.disposition, row.reviewed_by) == ("reviewed", "knowledge_gap", c.sup1)
    assert _events(c.env, "assistant.knowledge_gap", row.id)
    assert _err(act(c.sup1, "action_review", disposition="no_action", note="again"))
    assert _err(act(c.sup2, "action_close_gap"))  # a gap closes against evidence
    got = act(c.sup2, "action_close_gap", gap_ref="KB-2026-0117")
    assert not _err(got), got
    assert (row.state, row.knowledge_gap_ref, row.gap_days) == ("closed", "KB-2026-0117", 0)

    from odoo.addons.cd_p03_portal.controllers.a03 import m32 as ctl

    pack = ctl.knowledge_gap_report(c.env)
    assert pack["totals"]["gaps_closed"] >= 1 and pack["totals"]["closed_in_30"] >= 1
    assert any("KPI-184" in n for n in pack["notes"])


def test_a_disambiguation_tier_guess_is_never_answered(c):
    """REQ-32.1: between 0.50 and the threshold the assistant asks, it does not
    answer. The bot wrote its guess on the conversation, and ask() grounded on
    it, so the authored answer went out and the conversation closed as
    resolved by AI (found by capture pass 2)."""
    engine, _r = c.env["fix.assistant.dataset"].runtime_engine()
    probes = [
        "laptop not turning",
        "phone heating what",
        "wifi device problem today again",
        "screen display no light phone",
        "laptop power problem kindly",
    ]
    text = next(
        (
            t
            for t in probes
            if (r := engine.classify_intent(t)).matched_intent
            and r.matched_intent.startswith("knowledge.")
            and 0.50 <= r.confidence < 0.75
        ),
        None,
    )
    if text is None:
        pytest.skip("no probe lands in the disambiguation band on this engine")
    conv = _conversation(c)
    conv.intake_message(text, speaker="customer", lang="en")
    assert conv.state != "resolved_ai", (text, conv.state)
    ask = c.env["fix.assistant.ask"].sudo().search([("conversation_id", "=", conv.id)], limit=1)
    assert not ask.sent_at
