"""M32 capture audit pass 3 (2026-11-19), live, as NON-ADMIN users.

* 7 Handoff Decision: a supervisor records a signal phrase (an agent cannot);
  a customer message carrying it hands off on the same turn, before any
  classification or generated answer, with the trigger's priority; distress
  beats a lesser signal; matching is by whole words; a distress phrase is
  removed only by another supervisor; the safety floor is installed.
* 9 Analytics: an abandoned session the assistant took part in reaches the
  unresolved queue; one it never spoke in does not.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("_m32_live_p1_p3", HERE / "test_m32_capture_live.py")
_p1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_p1)

c = _p1.c
p03 = _p1.p03
_form_fields = _p1._form_fields
_err = _p1._err
_conversation = _p1._conversation
REFUSED = (UserError, ValidationError, AccessError)
MODEL = "fix.assistant.signal.phrase"


def _phrase(c, user, signal, phrase):
    return c.env[MODEL].with_user(user).create({"signal": signal, "phrase": phrase})


def _events(env, kind, res_id):
    Outbox = env["fix.event.outbox"].sudo()
    field = "aggregate_id" if "aggregate_id" in Outbox._fields else "res_id"
    return Outbox.search([("event_type", "=", kind), (field, "=", res_id)])


def test_a_supervisor_records_a_phrase_and_an_agent_cannot(c, p03):
    got = p03.form(c.sup1, model=MODEL, fields=_form_fields("M32-form-signal-phrase"))
    assert not got.get("error"), got
    vals = {"signal": "frustration", "phrase": "m32p3 utterly useless bot", "language": "en"}
    assert _err(p03.write(c.agent, model=MODEL, values=vals))
    got = p03.write(c.sup1, model=MODEL, values=vals)
    assert not _err(got), got
    row = c.env[MODEL].sudo().search([("phrase", "=", vals["phrase"])])
    assert row.normalised == "m32p3 utterly useless bot"
    with pytest.raises(ValidationError):
        _phrase(c, c.sup1, "frustration", "ok")  # too short to mean anything
    assert c.env[MODEL].with_user(c.agent).search_count([]) >= 1  # agents read


def test_the_safety_floor_is_installed(c):
    gas = c.env.ref("cd_contact_centre.signal_phrase_distress_gas")
    assert gas.signal == "distress" and gas.normalised == "gas leak"


def test_a_distress_phrase_hands_off_before_the_assistant_answers(c):
    _phrase(c, c.sup1, "distress", "m32p3 flames everywhere")
    _phrase(c, c.sup1, "frustration", "m32p3 so annoyed")
    conv = _conversation(c)
    conv.intake_message(
        "I am so annoyed, m32p3 so annoyed, M32P3 flames everywhere!", speaker="customer", lang="en"
    )
    assert conv.handoff_signal == "distress", conv.handoff_signal  # the most serious wins
    assert conv.handoff_category == "emotional" and conv.handoff_priority == "urgent"
    assert conv.state not in ("new", "with_ai", "resolved_ai")
    assert (
        not c.env["fix.assistant.ask"].sudo().search_count([("conversation_id", "=", conv.id)])
    ), "the message reached the classifier / generator"
    speakers = conv.turn_ids.sorted("sequence").mapped("speaker")
    assert speakers[:2] == ["customer", "ai"]
    assert _events(c.env, "sentiment.detected", conv.id)
    # supervisors are alerted on distress (AUT-CAI-04)
    assert conv.sudo().activity_ids or conv.sudo().message_ids


def test_an_explicit_request_phrase_is_honoured_on_the_same_turn(c):
    _phrase(c, c.sup1, "explicit_request", "m32p3 let me talk to staff")
    conv = _conversation(c)
    conv.intake_message("please m32p3 let me talk to staff", speaker="customer", lang="en")
    assert (conv.handoff_signal, conv.handoff_priority) == ("explicit_request", "high")
    # the reason M27 and its reports already key on is kept
    assert conv.handoff_reason == "customer_requested_agent"


def test_phrases_match_whole_words_only(c):
    _phrase(c, c.sup1, "distress", "m32p3 on fire")
    Phrase = c.env[MODEL]
    assert Phrase.detect("my m32p3 on fire now")["signal"] == "distress"
    assert Phrase.detect("my m32p3 on fireplace manual") is None
    assert Phrase.detect("") is None


def test_a_distress_phrase_is_removed_only_by_another_supervisor(c):
    row = _phrase(c, c.sup1, "distress", "m32p3 help me i am trapped")
    with pytest.raises(ValidationError):
        row.with_user(c.sup1).write({"active": False})
    with pytest.raises(ValidationError):
        row.with_user(c.sup1).write({"signal": "frustration"})
    with pytest.raises(ValidationError):
        row.with_user(c.sup1).unlink()
    row.with_user(c.sup2).write({"active": False})
    assert not row.active
    own = _phrase(c, c.sup1, "frustration", "m32p3 waste of time")
    own.with_user(c.sup1).unlink()  # a lesser signal is the author's to remove


def test_an_abandoned_assistant_session_reaches_the_unresolved_queue(c):
    Turn = c.env["fix.conversation.turn"].sudo()
    Unresolved = c.env["fix.assistant.unresolved"].sudo()
    conv = _conversation(c)
    Turn.create(
        {
            "conversation_id": conv.id,
            "sequence": 10,
            "speaker": "customer",
            "text": "m32p3 where is it",
        }
    )
    Turn.create(
        {"conversation_id": conv.id, "sequence": 20, "speaker": "ai", "text": "Which order?"}
    )
    conv._mark_abandoned()
    assert conv.state == "abandoned"
    row = Unresolved.search([("conversation_id", "=", conv.id)])
    assert len(row) == 1
    assert (row.signal, row.handoff_reason, row.state) == ("abandoned", "session_abandoned", "open")

    silent = _conversation(c)  # the assistant never spoke: not an assistant session
    Turn.create(
        {"conversation_id": silent.id, "sequence": 10, "speaker": "customer", "text": "m32p3 hello"}
    )
    silent._mark_abandoned()
    assert not Unresolved.search_count([("conversation_id", "=", silent.id)])
