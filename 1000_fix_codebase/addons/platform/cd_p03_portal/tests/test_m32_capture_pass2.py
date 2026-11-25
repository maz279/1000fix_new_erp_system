# M32 Conversational AI: capture audit pass 2 (19 Nov 2026).
#
# Pass 1 (14 Nov) gave every page a capture. Read against spec 10.1, 13 and
# 14, four pages still could not record what the spec gives a person there:
#   * 1 Intent Recognition: no intent category (FR-CAI-002) and no per-intent
#     confidence threshold (T-05); nothing ran a shadow evaluation before a
#     bundle replaced production (T-11, BRU-CAI-14). The playground ran a
#     fresh built-in engine, not the released bundle the bot uses.
#   * 6 Guard Rails: no stage or severity on a rule (fix.guardrail.rule), and
#     nobody could review a firing as a false positive (spec 14).
#   * 8 Agent Assistance: the AI answer could only be sent verbatim
#     (FR-CAI-038: "always editable").
#   * 9 Analytics: the unresolved queue and the knowledge-gap loop
#     (fix.unresolved.intent, AUT-CAI-06/08/10, KPI-184) did not exist.
#   * Access: every employee could create or edit intents and accept or reject
#     candidates, and could delete dialogue flows and RAG sources.
#
# Evaluated as the browser evaluates it, with the pass-1 guard's node fixture.
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("_m32_pass1", HERE / "test_m32_capture_buttons.py")
_p1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_p1)

m32 = _p1.m32  # the module-scoped node fixture
CC = _p1.CC
CONTROLLER = _p1.CONTROLLER


def _fields(cfg):
    return {f["name"]: f for f in cfg["fields"]}


def _chips(m32, no):
    return {f["id"] for f in _p1._sub(m32, no)["forms"] if f["opens"]}


def test_page_1_captures_taxonomy_threshold_and_shadow_run(m32):
    form = _fields(m32["screens"]["M32-form-intent"])
    for name in ("category", "confidence_threshold", "threshold_basis"):
        assert name in form and not form[name]["readonly"], name
    assert "M32-form-shadow" in _chips(m32, "1")
    shadow = m32["screens"]["M32-form-shadow"]
    assert shadow["save"]["method"] == "action_run_shadow"
    assert ["state", "=", "benchmarked"] in shadow["pick"]["domain"]
    typed = {n for n, f in _fields(shadow).items() if not f["readonly"]}
    assert not typed, "a shadow result is measured, never typed: %s" % sorted(typed)
    assert "action_run_shadow" in _p1._surfaces()["fix.assistant.dataset"]
    assert "shadow" in m32["screens"]["M32-form-dataset"]["tabs"]


def test_page_6_captures_stage_severity_and_reviews_firings(m32):
    rule = _fields(m32["screens"]["M32-form-guardrail"])
    for name in ("stage", "severity"):
        assert name in rule and rule[name]["required"], name
    assert "M32-form-guardrail-review" in _chips(m32, "6")
    review = m32["screens"]["M32-form-guardrail-review"]
    assert review["save"] == {
        "method": "action_review_guardrail",
        "kwargs": {"verdict": "review_verdict", "note": "review_note_input"},
    }
    assert ["guardrail_fired", "=", True] in review["pick"]["domain"]
    assert ["guardrail_review", "=", False] in review["pick"]["domain"]
    typed = {n for n, f in _fields(review).items() if not f["readonly"]}
    assert typed == {"review_verdict", "review_note_input"}, typed
    assert "action_review_guardrail" in _p1._surfaces()["fix.assistant.ask"]
    assert "M32-guardrail-firings" in _p1._sub(m32, "6")["screens"]


def test_page_8_reply_is_editable_before_it_is_sent(m32):
    send = m32["screens"]["M32-form-send-answer"]
    assert send["save"]["kwargs"] == {"reply": "draft_reply"}
    reply = _fields(send)["draft_reply"]
    assert not reply["readonly"] and reply["required"]


def test_page_9_reviews_the_unresolved_queue_and_closes_gaps(m32):
    sub = _p1._sub(m32, "9")
    assert sub["create"] == "M32-form-unresolved-review"
    assert {"M32-form-unresolved-review", "M32-form-gap-close"} <= _chips(m32, "9")
    assert "M32-unresolved" in sub["screens"]
    review = m32["screens"]["M32-form-unresolved-review"]
    assert review["save"]["method"] == "action_review"
    assert ["state", "=", "open"] in review["pick"]["domain"]
    close = m32["screens"]["M32-form-gap-close"]
    assert close["save"] == {"method": "action_close_gap", "kwargs": {"gap_ref": "gap_ref_input"}}
    assert ["disposition", "=", "knowledge_gap"] in close["pick"]["domain"]
    assert _fields(close)["gap_ref_input"]["required"]
    assert review["save"]["kwargs"] == {
        "disposition": "disposition_input",
        "note": "note_input",
        "gap_ref": "gap_ref_input",
    }
    # the assistant's log is shown, never retyped
    logged = {"question", "best_guess_intent", "confidence", "handoff_reason"}
    for sid in ("M32-form-unresolved-review", "M32-form-gap-close", "M32-form-unresolved"):
        for name, f in _fields(m32["screens"][sid]).items():
            if name in logged:
                assert f["readonly"], "%s lets %s be typed" % (sid, name)
    surf = _p1._surfaces()["fix.assistant.unresolved"]
    assert {"action_review", "action_close_gap"} <= surf
    reports = {r["r"]: r["route"] for r in sub["reports"]}
    assert reports.get("Knowledge Gap Report") == "M32-rpt-gaps"
    assert "knowledge_gap_report" in _p1._reports()


def test_review_outcomes_are_not_writable_through_the_endpoint():
    """The pick forms post unstored inputs to their action; the outcome they
    record is guarded and never on the write whitelist (R9 c)."""
    writable = _p1._writable()
    assert not writable["fix.assistant.unresolved"] & {
        "question",
        "best_guess_intent",
        "confidence",
        "state",
        "disposition",
        "knowledge_gap_ref",
        "review_note",
        "reviewed_by",
        "gap_closed_at",
    }
    assert not writable["fix.assistant.ask"] & {
        "guardrail_review",
        "guardrail_review_note",
        "sent_text",
        "edited_by_agent",
    }
    src = (CC / "models" / "fix_assistant_capture2.py").read_text(encoding="utf-8")
    for name in (
        "review_verdict",
        "review_note_input",
        "disposition_input",
        "gap_ref_input",
        "note_input",
    ):
        # the field's own definition: up to the next attribute or method
        m = re.search(r"^    %s = fields\..*?(?=^    \S)" % name, src, re.M | re.S)
        assert m, name
        assert "compute=" in m.group(0) and "store=True" not in m.group(0), name


def _acl():
    rows = (CC / "security" / "ir.model.access.csv").read_text(encoding="utf-8").splitlines()[1:]
    return [r.split(",") for r in rows if r.strip()]


def test_configuration_is_written_by_supervisors_not_every_employee():
    """Spec 13: the Customer Service Manager owns the taxonomy, the unresolved
    queue and the configuration. Every employee only reads them."""
    rows = _acl()
    for model in (
        "fix.assistant.intent",
        "fix.assistant.intent.candidate",
        "fix.assistant.dialogue",
        "fix.assistant.rag.source",
        "fix.assistant.unresolved",
    ):
        ref = "model_" + model.replace(".", "_")
        mine = [r for r in rows if r[2] == ref]
        user = [r for r in mine if r[3] == "base.group_user"]
        assert user and all(r[4:8] == ["1", "0", "0", "0"] for r in user), model
        assert any(
            r[3] == "cd_contact_centre.group_cc_supervisor" and r[5] == "1" for r in mine
        ), model
    rules = (CC / "security" / "fix_isolation_rules.xml").read_text(encoding="utf-8")
    assert 'ref="model_fix_assistant_unresolved"' in rules


def test_playground_runs_the_released_engine_at_its_thresholds():
    src = CONTROLLER.read_text(encoding="utf-8")
    assert "runtime_engine()" in src and "confidence_thresholds()" in src
    assert "AssistantEngine()" not in src, "the playground built a fresh built-in engine"


def test_live_bot_and_benchmark_apply_the_per_intent_threshold():
    bot = (CC / "models" / "fix_contact_centre.py").read_text(encoding="utf-8")
    ops = (CC / "models" / "fix_assistant_ops.py").read_text(encoding="utf-8")
    assert "confidence_thresholds()" in bot
    assert "confidence_thresholds()" in ops
    assert "result.confidence >= 0.75" not in ops
