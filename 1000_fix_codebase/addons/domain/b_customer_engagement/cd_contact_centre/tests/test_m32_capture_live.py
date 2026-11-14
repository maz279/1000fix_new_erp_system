"""M32 capture audit (2026-11-14): the captures the nine sub-module pages now
offer, driven through /p03/model/form, /p03/model/write and /p03/model/action
as NON-ADMIN users with the fields m32.js posts. The superuser is trusted by
the model guards and would hide a gap.

  * Every capture of every page opens for its actor (a Contact Centre
    Supervisor for the registers, an agent for the pick forms).
  * A plain agent reads the registers but cannot change them, nor any guard rail.
  * 2 Entity Extraction: a definition is proved against its examples; Bengali
    digits count; the IMEI check digit is applied; a catastrophic pattern is
    refused; the extraction report runs the registered definitions.
  * 5 Authenticated Actions: BRU-CAI-03/04/05 refuse a bad rule; a rule
    changes what the live assistant does (identity first, withdrawn action),
    and a withheld action is never answered by generation instead.
  * 6 Guard Rails: SOD-20, the author cannot switch their own rule off.
  * 7 Handoff Decision: the category follows the signal; distress and an
    explicit request cannot be weakened; a handoff is stamped with its
    category and priority, and the queue item is raised to that priority.
  * 8 Agent Assistance: review by another person, then send, through the pick
    forms' actions.
  * 9 Analytics: a candidate's mined evidence and state cannot be typed;
    Accept and Reject carry the reviewer's note.
"""

from __future__ import annotations

import re
import types
from pathlib import Path

import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

JS = (
    Path(__file__).resolve().parents[4]
    / "platform"
    / "cd_p03_portal"
    / "static"
    / "src"
    / "a03"
    / "m32.js"
)
SUP = "cd_contact_centre.group_cc_supervisor"
REFUSED = (UserError, ValidationError, AccessError)

# a valid IMEI (Luhn) and one with a wrong check digit
IMEI_OK = "490154203237518"
IMEI_BAD = "490154203237519"


def _user(env, login, groups=()):
    gids = [env.ref("base.group_user").id] + [env.ref(x).id for x in groups]
    ou = env["operating.unit"].search([], limit=1)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "email": "%s@m32cap.test" % login,
                "group_ids": [(6, 0, gids)],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.agent = _user(env, "m32cap_agent")
    x.agent2 = _user(env, "m32cap_agent2")
    x.sup1 = _user(env, "m32cap_sup1", [SUP])
    x.sup2 = _user(env, "m32cap_sup2", [SUP])
    assert not x.sup1.has_group("base.group_system")
    x.ou = env["operating.unit"].search([], limit=1)
    return x


@pytest.fixture
def p03(odoo_env):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g

    ctl = g.P03GenericApiController()

    def ep(name):
        f = getattr(g.P03GenericApiController, name)
        return getattr(f, "original_endpoint", f)

    old = getattr(g, "request", None)

    def call(user, name, **kw):
        g.request = types.SimpleNamespace(env=odoo_env(user=user.id))
        return ep(name)(ctl, **kw)

    try:
        yield types.SimpleNamespace(
            write=lambda user, **kw: call(user, "model_write", **kw),
            action=lambda user, record_id=None, **kw: call(
                user, "model_action", ids=[record_id], **kw
            ),
            records=lambda user, **kw: call(user, "model_records", **kw),
            form=lambda user, **kw: call(user, "model_form", **kw),
        )
    finally:
        g.request = old


def _form_fields(screen):
    """The field list one m32.js form posts (its block, up to the next screen)."""
    js = JS.read_text(encoding="utf-8")
    start = js.index("'%s': {" % screen)
    nxt = re.compile(r"^  '(M32[-:][\w-]+)': \{", re.M).search(js, start + 10)
    block = js[start : nxt.start() if nxt else len(js)]
    return [{"name": n} for n in re.findall(r"name: '(\w+)'", block)]


def _err(res):
    return res.get("error") or (res.get("success") is False and "failed")


def _conversation(c, user=None, **vals):
    return (
        c.env["fix.conversation"]
        .with_user(user or c.agent)
        .create(dict({"channel": "chat", "operating_unit_id": c.ou.id}, **vals))
    )


def _ask(c, asker, **vals):
    base = {
        "consumer": "m27_agent_assist",
        "question": "Where is my phone?",
        "language": "en",
        "engine": "llm",
        "guardrail_verdict": "pass",
        "grounded": True,
        "requires_human": True,
        "answer_en": "Your phone is in repair.",
        "citations": "[]",
    }
    base.update(vals)
    return c.env["fix.assistant.ask"].with_user(asker).sudo().create(base).with_user(asker)


# ---------------------------------------------------------------- every capture opens
CREATE_FORMS = {
    "M32-form-intent": "fix.assistant.intent",
    "M32-form-entity": "fix.assistant.entity",
    "M32-form-dialogue": "fix.assistant.dialogue",
    "M32-form-rag": "fix.assistant.rag.source",
    "M32-form-authority": "fix.assistant.action.authority",
    "M32-form-guardrail": "fix.assistant.guardrail",
    "M32-form-handoff-trigger": "fix.assistant.handoff.trigger",
}


@pytest.mark.parametrize("screen", sorted(CREATE_FORMS))
def test_every_register_capture_opens_blank_for_a_supervisor(c, p03, screen):
    got = p03.form(c.sup1, model=CREATE_FORMS[screen], fields=_form_fields(screen))
    assert not got.get("error"), (screen, got)


def test_the_pick_forms_open_their_record_for_an_agent(c, p03):
    ask = _ask(c, c.agent)
    cand = (
        c.env["fix.assistant.intent.candidate"]
        .sudo()
        .create({"phrase": "m32cap phone khub gorom", "normalised": "m32cap phone khub gorom"})
    )
    for screen, rec in (
        ("M32-form-review-answer", ask),
        ("M32-form-send-answer", ask),
        ("M32-form-candidate-accept", cand),
        ("M32-form-candidate-reject", cand),
    ):
        got = p03.form(c.agent2, model=rec._name, record_id=rec.id, fields=_form_fields(screen))
        assert not got.get("error"), (screen, got)


@pytest.mark.parametrize(
    "model,values",
    [
        ("fix.assistant.entity", {"code": "x", "name": "x", "pattern": "x", "examples": "x"}),
        ("fix.assistant.action.authority", {"action_type": "price_quote"}),
        ("fix.assistant.handoff.trigger", {"signal": "frustration"}),
        ("fix.assistant.guardrail", {"name": "x", "rule": "legal liability", "action": "block"}),
    ],
)
def test_a_plain_agent_reads_but_cannot_change_the_registers(c, p03, model, values):
    got = p03.records(c.agent, model=model, cols=["id"])
    assert not got.get("error"), (model, got)
    res = p03.write(c.agent, model=model, values=values)
    assert _err(res), (model, res)
    assert not c.env[model].with_user(c.agent).has_access("create")


# ---------------------------------------------------------------- 2 Entity Extraction
def _imei_vals(**extra):
    vals = {
        "code": "imei",
        "name": "IMEI",
        "entity_type": "imei",
        "pattern": r"\b[0-9]{15}\b",
        "validation": "luhn",
        "examples": "my imei is %s\nআমার আইএমইআই ৪৯০১৫৪২০৩২৩৭৫১৮" % IMEI_OK,
        "counter_examples": "my imei is %s\ncall 01711000000" % IMEI_BAD,
    }
    vals.update(extra)
    return vals


def test_an_entity_definition_is_proved_and_extracts(c, p03):
    res = p03.write(c.sup1, model="fix.assistant.entity", values=_imei_vals())
    assert not _err(res), res
    rec = c.env["fix.assistant.entity"].browse(res["id"])
    # Bengali digits are digits (FR-CAI-003); the check digit is applied
    assert rec.extract("আমার আইএমইআই ৪৯০১৫৪২০৩২৩৭৫১৮") == [IMEI_OK]
    assert rec.extract("imei %s" % IMEI_BAD) == []
    assert rec.example_check.startswith("2 of 2 examples extract; 0 of 2")


@pytest.mark.parametrize(
    "extra,needle",
    [
        ({"examples": "my imei is %s" % IMEI_BAD}, "extract nothing"),
        ({"counter_examples": "my imei is %s" % IMEI_OK}, "counter-examples"),
        ({"pattern": r"(\d+)+"}, "repeats a group"),
        ({"pattern": r"[0-9]*"}, "empty message"),
        ({"pattern": r"([0-9]{15}"}, "not a valid"),
    ],
)
def test_a_definition_that_does_not_do_what_it_says_is_refused(c, p03, extra, needle):
    res = p03.write(c.sup1, model="fix.assistant.entity", values=_imei_vals(**extra))
    assert _err(res) and needle in str(res), res


def test_the_extraction_report_runs_the_registered_definitions(c, p03):
    from odoo.addons.cd_p03_portal.controllers.a03 import m32

    before = m32.entity_catalog(c.env)
    assert any(r["basis"] == "built-in pattern" for r in before["rows"])
    # A phone number survives the transcript's PII scrubbing. An IMEI does not:
    # the card mask (13-16 digits, REQ-32.3) masks it before it is stored.
    res = p03.write(
        c.sup1,
        model="fix.assistant.entity",
        values={
            "code": "bd_phone",
            "name": "Callback number",
            "entity_type": "phone",
            "pattern": r"(?:\+?880|0)1[0-9]{9}",
            "validation": "bd_mobile",
            "examples": "call me on 01711000000\nআমার নম্বর ০১৮১২৩৪৫৬৭৮",
            "counter_examples": "order 12345",
        },
    )
    assert not _err(res), res
    conv = _conversation(c)
    turn = c.env["fix.conversation.turn"].create(
        {
            "conversation_id": conv.id,
            "sequence": 10,
            "speaker": "customer",
            "text": "call me on ০১৭১১০০০০০০ or imei %s" % IMEI_OK,
            "lang": "en",
        }
    )
    assert IMEI_OK not in turn.text, "the IMEI is masked before the turn is stored"
    after = m32.entity_catalog(c.env)
    phone = next(r for r in after["rows"] if r["entity"] == "Callback number")
    assert phone["turns_with_match"] >= 1 and "bd_mobile" in phone["basis"]
    assert not any(r["basis"] == "built-in pattern" for r in after["rows"])


# ---------------------------------------------------------------- 5 Authenticated Actions
@pytest.mark.parametrize(
    "values,needle",
    [
        ({"action_type": "refund", "assistant_may_perform": True}, "BRU-CAI-04"),
        ({"action_type": "goodwill_credit", "assistant_may_perform": True}, "BRU-CAI-04"),
        (
            {
                "action_type": "status_enquiry",
                "assistant_may_perform": True,
                "requires_identity": False,
            },
            "BRU-CAI-03",
        ),
        (
            {
                "action_type": "service_booking",
                "assistant_may_perform": True,
                "requires_confirmation": False,
            },
            "BRU-CAI-05",
        ),
        ({"action_type": "repair_approval", "assistant_may_perform": True}, "needs a limit"),
    ],
)
def test_the_hard_rules_refuse_a_bad_authority_rule(c, p03, values, needle):
    res = p03.write(c.sup1, model="fix.assistant.action.authority", values=values)
    assert _err(res) and needle in str(res), res


def test_typed_kind_flags_are_not_saved(c, p03):
    res = p03.write(
        c.sup1,
        model="fix.assistant.action.authority",
        values={"action_type": "refund", "never_delegable": False, "commitment": True},
    )
    if not _err(res):
        rec = c.env["fix.assistant.action.authority"].browse(res["id"])
        assert rec.never_delegable and not rec.commitment


def _status_turn(c, conv):
    from odoo.addons.cd_contact_centre.models.assistant_engine import INTENT_REGISTRY

    conv.intake_message(INTENT_REGISTRY["order.status"].sample_en[0], lang="en")
    return conv


def test_identity_first_sends_an_unverified_customer_to_a_person(c, p03):
    res = p03.write(
        c.sup1,
        model="fix.assistant.action.authority",
        values={"action_type": "status_enquiry", "assistant_may_perform": True},
    )
    assert not _err(res), res
    conv = _status_turn(c, _conversation(c))
    assert conv.intent == "order.status", "the sample no longer classifies as order.status"
    assert conv.state == "with_agent" and conv.handoff_reason == "identity_not_verified"
    assert conv.handoff_signal == "identity" and conv.handoff_category == "technical"


def test_a_withdrawn_action_is_handed_off_not_answered(c, p03):
    res = p03.write(
        c.sup1,
        model="fix.assistant.action.authority",
        values={"action_type": "status_enquiry", "assistant_may_perform": False},
    )
    assert not _err(res), res
    partner = c.env["res.partner"].create({"name": "M32 cap customer"})
    conv = _status_turn(c, _conversation(c, customer_id=partner.id))
    assert conv.state == "with_agent" and conv.handoff_reason == "action_beyond_authority"
    assert conv.handoff_signal == "beyond_authority"


def test_without_a_rule_the_assistant_behaves_as_before(c):
    conv = _status_turn(c, _conversation(c))
    assert conv.handoff_reason not in ("identity_not_verified", "action_beyond_authority")


def test_a_withheld_action_is_never_generated_instead(c):
    Intent = c.env["fix.assistant.intent"]
    out = Intent._generate(False, "q", {"reason": "action_beyond_authority"}, "en")
    assert out["ok"] is False and "authority" in out["reason"]


def test_refund_cancellation_and_goodwill_are_never_delegated_even_without_rows(c):
    Authority = c.env["fix.assistant.action.authority"]
    for action in ("refund", "contract_cancellation", "goodwill_credit"):
        assert Authority.check(action, identity_verified=True)["allowed"] is False


# ---------------------------------------------------------------- 6 Guard Rails (SOD-20)
def test_the_author_cannot_switch_their_own_guard_rail_off(c, p03):
    res = p03.write(
        c.sup1,
        model="fix.assistant.guardrail",
        values={"name": "M32cap legal", "rule": "advice on legal liability", "action": "block"},
    )
    assert not _err(res), res
    rid = res["id"]
    own = p03.write(
        c.sup1, model="fix.assistant.guardrail", record_id=rid, values={"active": False}
    )
    assert _err(own) and "SOD-20" in str(own), own
    rail = c.env["fix.assistant.guardrail"].with_context(active_test=False).browse(rid)
    assert rail.active
    other = p03.write(
        c.sup2, model="fix.assistant.guardrail", record_id=rid, values={"active": False}
    )
    assert not _err(other), other
    assert not rail.active
    with pytest.raises(REFUSED):
        rail.with_user(c.sup1).unlink()


# ---------------------------------------------------------------- 7 Handoff Decision
def test_the_category_follows_the_signal_and_cannot_be_typed(c, p03):
    res = p03.write(
        c.sup1,
        model="fix.assistant.handoff.trigger",
        values={"signal": "sla_risk", "priority": "high", "category": "technical"},
    )
    assert not _err(res), res
    rec = c.env["fix.assistant.handoff.trigger"].browse(res["id"])
    assert rec.category == "operational"


@pytest.mark.parametrize(
    "values,needle",
    [
        (
            {"signal": "explicit_request", "priority": "high", "active": False},
            "cannot be switched off",
        ),
        ({"signal": "explicit_request", "priority": "normal"}, "at least"),
        ({"signal": "distress", "priority": "high", "notify_supervisor": True}, "at least"),
        ({"signal": "distress", "priority": "urgent", "notify_supervisor": False}, "AUT-CAI-04"),
    ],
)
def test_distress_and_an_explicit_request_cannot_be_weakened(c, p03, values, needle):
    res = p03.write(c.sup1, model="fix.assistant.handoff.trigger", values=values)
    assert _err(res) and needle in str(res), res


def test_a_mandatory_trigger_cannot_be_deleted(c, p03):
    res = p03.write(
        c.sup1,
        model="fix.assistant.handoff.trigger",
        values={"signal": "explicit_request", "priority": "urgent"},
    )
    assert not _err(res), res
    with pytest.raises(REFUSED):
        c.env["fix.assistant.handoff.trigger"].browse(res["id"]).with_user(c.sup1).unlink()


@pytest.fixture
def routed(c):
    """A pick workstream for chat conversations, so a handoff is a work item."""
    queue = c.env["fix.cc.queue"].create(
        {"name": "M32cap chat", "code": "M32CAPQ", "channel": "chat", "target_answer_seconds": 30}
    )
    return c.env["fix.routing.workstream"].create(
        {
            "name": "M32cap contacts",
            "code": "M32CAPWS",
            "channel": "chat",
            "work_type": "conversation",
            "source_model": "fix.conversation",
            "queue_id": queue.id,
            "assignment_method": "pick",
        }
    )


def test_a_handoff_is_stamped_and_queued_at_the_trigger_priority(c, p03, routed):
    # spec default with no row: an explicit request is at least High
    conv = _conversation(c)
    conv.action_handoff_to_agent(reason="customer_requested_agent")
    assert conv.handoff_signal == "explicit_request"
    assert conv.handoff_category == "emotional" and conv.handoff_priority == "high"
    assert conv.work_item_id, "the handoff was not routed to a work item"
    assert conv.work_item_id.priority >= 50

    # a supervisor makes low confidence urgent: the next such handoff is urgent
    res = p03.write(
        c.sup1,
        model="fix.assistant.handoff.trigger",
        values={"signal": "low_confidence", "priority": "urgent"},
    )
    assert not _err(res), res
    conv2 = _conversation(c)
    conv2.action_handoff_to_agent(reason="low_intent_confidence")
    assert conv2.handoff_category == "technical" and conv2.handoff_priority == "urgent"
    assert conv2.work_item_id, "the handoff was not routed to a work item"
    assert conv2.work_item_id.priority >= 100


def test_handoff_stamps_are_never_typed(c, p03):
    conv = _conversation(c)
    with pytest.raises(REFUSED):
        conv.with_user(c.agent).write({"handoff_priority": "urgent"})


def test_distress_alerts_every_supervisor(c):
    conv = _conversation(c)
    before = (
        c.env["mail.activity"]
        .sudo()
        .search_count([("res_model", "=", "fix.conversation"), ("res_id", "=", conv.id)])
    )
    conv.action_handoff_to_agent(reason="distress")
    acts = (
        c.env["mail.activity"]
        .sudo()
        .search([("res_model", "=", "fix.conversation"), ("res_id", "=", conv.id)])
    )
    assert len(acts) > before
    assert {c.sup1.id, c.sup2.id} <= set(acts.mapped("user_id").ids)
    assert conv.handoff_priority == "urgent"


def test_the_handoff_report_groups_by_category(c):
    from odoo.addons.cd_p03_portal.controllers.a03 import m32

    conv = _conversation(c)
    conv.action_handoff_to_agent(reason="customer_requested_agent")
    pack = m32.handoff_reasons(c.env)
    row = next(r for r in pack["rows"] if r["reason"] == "customer_requested_agent")
    assert row["category"] == "emotional"


# ---------------------------------------------------------------- 8 Agent Assistance
def test_an_answer_is_reviewed_by_another_person_then_sent(c, p03):
    conv = _conversation(c)
    ask = _ask(c, c.agent, conversation_id=conv.id)
    own = p03.action(
        c.agent, model="fix.assistant.ask", record_id=ask.id, method="action_mark_reviewed"
    )
    assert _err(own), own
    early = p03.action(
        c.agent2, model="fix.assistant.ask", record_id=ask.id, method="action_send_to_customer"
    )
    assert _err(early), early
    ok = p03.action(
        c.agent2, model="fix.assistant.ask", record_id=ask.id, method="action_mark_reviewed"
    )
    assert not _err(ok), ok
    sent = p03.action(
        c.agent2, model="fix.assistant.ask", record_id=ask.id, method="action_send_to_customer"
    )
    assert not _err(sent), sent
    assert ask.sudo().sent_at and ask.sudo().human_reviewed_by == c.agent2
    assert any(t.text == "Your phone is in repair." for t in conv.turn_ids)


# ---------------------------------------------------------------- 9 Analytics
def test_candidate_evidence_and_state_cannot_be_typed(c, p03):
    cand = (
        c.env["fix.assistant.intent.candidate"]
        .sudo()
        .create(
            {
                "phrase": "m32cap screen kalo",
                "normalised": "m32cap screen kalo",
                "frequency": 7,
            }
        )
    )
    p03.write(
        c.agent,
        model="fix.assistant.intent.candidate",
        record_id=cand.id,
        values={"state": "accepted", "frequency": 9999, "phrase": "typed"},
    )
    cand.invalidate_recordset()
    assert cand.state == "proposed" and cand.frequency == 7 and cand.phrase == "m32cap screen kalo"


def test_accept_and_reject_carry_the_reviewer_note(c, p03):
    Cand = c.env["fix.assistant.intent.candidate"].sudo()
    a = Cand.create({"phrase": "m32cap a", "normalised": "m32cap a"})
    r = Cand.create({"phrase": "m32cap r", "normalised": "m32cap r"})
    got = p03.action(
        c.agent,
        model="fix.assistant.intent.candidate",
        record_id=a.id,
        method="action_accept",
        kwargs={"note": "common, author it"},
    )
    assert not _err(got), got
    got = p03.action(
        c.agent,
        model="fix.assistant.intent.candidate",
        record_id=r.id,
        method="action_reject",
        kwargs={"note": "noise"},
    )
    assert not _err(got), got
    assert (a.state, a.review_note) == ("accepted", "common, author it")
    assert (r.state, r.review_note) == ("rejected", "noise")
