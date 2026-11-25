# M34 CX, Feedback & Complaints: every sub-module page offers the button that
# captures ITS record (audit 2026-11-13).
#
# Before: Survey Design & Distribution offered "+ New Survey" - a response row
# the service_order.closed consumer raises, one per order - while the
# instrument designer, its 3 instruments and the throttle rules sat on no page
# and the "Survey Designer" screen said no question model existed. CSAT / NPS
# / CES hand-created surveys with a typed state ("Sent" with nothing sent).
# Multi-Parameter Ratings offered "+ New Customer Review" (an external Google
# review); the per-question answers sat on no page and their grid keyed a
# related code, so no answer could be saved. Categorisation & SLA offered
# "+ New Complaint"; the complaint SLA binding had no screen at all. VoC
# Analytics captured nothing although reviews (FR-CXM-040) are entered there.
#
# Second pass (2026-11-14): Categorisation & SLA still showed no + button
# (the bindings were administrator-only and the category was a fixed list,
# although FR-CXM-030 asks for a maintained taxonomy the Customer Service
# Manager owns). A loop closed as "Recovered" with no word from the customer
# and "Not Recovered" with no contact (BRU-CXM-03/04), and a review could be
# typed "Published" with no consent (BRU-CXM-13).
#
# Evaluated as the browser evaluates it: node runs the engine's own fregCreate
# and fregPanels over the real registry fragments (the M02 guard's fixture).
from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "static" / "src"

_spec = importlib.util.spec_from_file_location(
    "_estate_pages", HERE / "test_estate_module_pages.py"
)
_estate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_estate)

PROBE = """
import * as M from './meta.mjs';
const { P03_MODULES, P03_MODULE_CREATE, P03_FORM_CHIPS, P03_DATA_SCREENS } = M;
function %(create)s
function %(panels)s
const mod = P03_MODULES.M34;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M34', map);
  const forms = fregPanels('M34', mod, map).forms.map((f) => {
    const id = P03_FORM_CHIPS['M34:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const lists = (map.screens || []).map((id) => ({ id, cfg: P03_DATA_SCREENS[id] || {} }))
    .filter((x) => x.cfg.kind === 'model_list')
    .map((x) => ({ id: x.id, model: x.cfg.model, create: x.cfg.create !== false, empty: !!x.cfg.empty,
      actions: (x.cfg.actions || []).map((a) => a.m) }));
  return { no: s[0], model: map.model || null, screens: map.screens || [],
    create: create && (create.screen || (create.module ? 'module' : null)), forms, lists };
});
const S = P03_DATA_SCREENS;
console.log(JSON.stringify({ subs,
  nav: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  screens: Object.fromEntries(Object.entries(S).filter(([id]) => id.startsWith('M34-')).map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create, back: c.back || null, empty: !!c.empty,
    pick: !!c.pickRecord, actions: (c.actions || []).map((a) => a.m),
    lines: c.lines ? c.lines.fields.map((f) => ({ name: f.name, readonly: !!f.readonly, required: !!f.required })) : null,
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({ name: f.name, value: f.value, readonly: !!f.readonly })) }])) }));
"""


# How each page's record is captured. 'form': a "+ New" or a chip opening an
# in-workspace form. 'system': calculated, so the page offers nothing.
CAPTURE = {
    "1": "form",  # survey instrument (questions, branching) + throttle rule
    "2": "form",  # a response recorded on the survey the closed order raised
    "3": "form",  # per-parameter answers, recorded on that response
    "4": "form",  # detractor follow-up (auto-raised; by hand for a call-back)
    "5": "form",  # complaint
    "6": "form",  # complaint category (maintained taxonomy) + SLA binding
    "7": "form",  # goodwill credit note
    "8": "form",  # review / testimonial (FR-CXM-040); the analytics are calculated
}


@pytest.fixture(scope="module")
def m34(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m34_capture")
    for area in sorted(d for d in SRC.iterdir() if re.fullmatch(r"a\d\d", d.name)):
        (tmp / area.name).mkdir()
        for js in area.glob("*.js"):
            (tmp / area.name / (js.stem + ".mjs")).write_text(
                js.read_text(encoding="utf-8"), "utf-8"
            )
    meta = (SRC / "p03_modules_meta.js").read_text(encoding="utf-8")
    (tmp / "meta.mjs").write_text(_estate.IMPORT.sub(r'from "\1.mjs"', meta), "utf-8")
    engine = (SRC / "p03_workspace.js").read_text(encoding="utf-8").replace("\r\n", "\n")
    probe = tmp / "probe.mjs"
    probe.write_text(
        PROBE
        % {
            "create": _estate._method(engine, "fregCreate(mid, map)"),
            "panels": _estate._method(engine, "fregPanels(mid, mod, map)"),
        },
        "utf-8",
    )
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our own probe file
        [node, str(probe)], capture_output=True, encoding="utf-8", check=True, timeout=120
    )
    return json.loads(out.stdout)


def _sub(m34, no):
    return next(s for s in m34["subs"] if s["no"] == no)


def _field(m34, screen, name):
    return next(f for f in m34["screens"][screen]["fields"] if f["name"] == name)


def test_every_page_is_classified(m34):
    assert sorted(s["no"] for s in m34["subs"]) == sorted(CAPTURE)


@pytest.mark.parametrize("no", sorted(CAPTURE, key=int))
def test_each_page_offers_its_capture(m34, no):
    sub = _sub(m34, no)
    opening = [f for f in sub["forms"] if f["opens"]]
    if CAPTURE[no] == "form":
        assert sub["create"] or opening, "page %s has no + New and no form chip" % no
        for f in sub["forms"]:
            assert f["kind"] == "model_form", "chip %s opens %s" % (f["f"], f["kind"])
    else:
        assert not sub["create"] and not opening
        assert all(lst["empty"] for lst in sub["lists"])


def test_every_working_screen_sits_on_a_page(m34):
    """A list or report on no page cannot be reached from the register."""
    placed = {sid for s in m34["subs"] for sid in s["screens"]}
    orphans = [
        sid
        for sid, cfg in m34["screens"].items()
        if cfg["kind"] != "model_form" and sid not in placed
    ]
    assert not orphans, orphans


def test_survey_design_captures_the_instrument_not_a_response(m34):
    sub = _sub(m34, "1")
    assert sub["model"] == "fix.survey.template"
    assert sub["create"] == "M34-form-survey-template"
    assert {"M34-survey-templates", "M34-design", "M34-throttle"} <= set(sub["screens"])
    chips = {f["f"]: f for f in sub["forms"]}
    assert chips["Distribution Throttle"]["model"] == "fix.cx.throttle"
    design = m34["screens"]["M34-design"]
    assert design["kind"] == "model_list" and design["model"] == "fix.survey.question"
    # Publish / Retire are the instrument's workflow; a typed state skipped
    # the Bengali-text check and the freeze.
    assert _field(m34, "M34-form-survey-template", "state")["readonly"]


@pytest.mark.parametrize("no", ["2"])
def test_response_is_recorded_on_the_raised_survey(m34, no):
    """A survey is raised by its closed order (one per order): the capture
    picks it and records the response; nothing types a new survey or its
    state."""
    sub = _sub(m34, no)
    assert sub["create"] == "M34-form-survey"
    form = m34["screens"]["M34-form-survey"]
    assert form["pick"], "the response form must pick the raised survey first"
    for name in ("state", "service_order_id", "operating_unit_id", "customer_id"):
        assert _field(m34, "M34-form-survey", name)["readonly"], name
    assert not _field(m34, "M34-form-survey", "rating")["readonly"]
    lines = {f["name"]: f for f in form["lines"]}
    assert lines["question_id"]["required"] and not lines["question_id"]["readonly"]
    assert "question_code" not in lines, "a related code cannot create an answer"


def test_multi_parameter_page_lists_the_answers(m34):
    sub = _sub(m34, "3")
    assert sub["model"] == "fix.survey.answer"
    assert "M34-survey-answers" in sub["screens"]
    assert "fix.cx.review" not in {f["model"] for f in sub["forms"]}
    # Third pass: the survey response is still a chip here (service ratings
    # are its answers); the page's own + is the conversation rating.
    chips = {f["f"]: f for f in sub["forms"]}
    assert chips["Survey"]["opens"]


def test_detractor_states_move_by_actions(m34):
    assert _field(m34, "M34-form-followup", "state")["readonly"]
    actions = set(m34["screens"]["M34-detractor"]["actions"])
    assert {
        "action_mark_contacted",
        "action_close_recovered",
        "action_close_unrecovered",
    } <= actions


def test_categorisation_page_captures_a_complaint_category(m34):
    """FR-CXM-030: the page's + button captures a node of the maintained
    taxonomy; the SLA binding is its second capture (chip and list)."""
    sub = _sub(m34, "6")
    assert sub["model"] == "fix.complaint.taxonomy"
    assert sub["create"] == "M34-form-complaint-taxonomy"
    assert {"M34-taxonomy", "M34-sla-rules"} <= set(sub["screens"])
    chips = {f["f"]: f for f in sub["forms"]}
    for chip, model in (
        ("Complaint Category", "fix.complaint.taxonomy"),
        ("Complaint SLA Binding", "fix.complaint.sla.rule"),
    ):
        assert chips[chip]["model"] == model and chips[chip]["opens"], chip
    assert m34["screens"]["M34-sla-rules"]["create"] is True
    assert m34["screens"]["M34-taxonomy"]["create"] is True
    assert "M34-taxonomy" in m34["nav"]
    form = {f["name"]: f for f in m34["screens"]["M34-form-complaint-taxonomy"]["fields"]}
    assert {"code", "name", "name_bn", "parent_id", "category", "default_severity"} <= set(form)
    assert form["complaint_count"]["readonly"]


def test_complaint_intake_names_the_maintained_category(m34):
    field = _field(m34, "M34-record", "taxonomy_id")
    assert not field["readonly"]


@pytest.mark.parametrize("model", ["fix_complaint_sla_rule", "fix_complaint_taxonomy"])
def test_csm_registers_are_written_by_supervisors_only(model):
    """Spec section 13: the Customer Service Manager's registers. Every
    internal user reads them; the supervisor group and the administrator
    write them."""
    acl = (
        HERE.parents[2] / "domain/b_customer_engagement/cd_cx_feedback/security/ir.model.access.csv"
    ).read_text(encoding="utf-8")
    rows = [r.split(",") for r in acl.splitlines() if ",model_%s," % model in r]
    creators = {r[3] for r in rows if r[6] == "1"}
    writers = {r[3] for r in rows if r[5] == "1"}
    readers = {r[3] for r in rows if r[4] == "1"}
    expected = {"base.group_system", "cd_contact_centre.group_cc_supervisor"}
    assert creators == expected and writers == expected, (creators, writers)
    assert "base.group_user" in readers


def test_voc_page_captures_a_review(m34):
    sub = _sub(m34, "8")
    assert sub["create"] == "M34-form-review"
    assert "M34-reviews" in sub["screens"]


def test_review_publishes_by_actions_not_a_typed_state(m34):
    """BRU-CXM-13: the publishing state moves by Record Consent / Publish;
    a typed "Published" skipped the customer's consent."""
    for name in ("state", "publication_consent", "consent_evidence", "reply_text"):
        assert _field(m34, "M34-form-review", name)["readonly"], name
    actions = set(m34["screens"]["M34-reviews"]["actions"])
    assert {
        "action_record_consent",
        "action_publish",
        "action_flag",
        "action_reply",
        "action_withdraw_consent",
    } <= actions


def test_recovery_asks_for_the_customers_confirmation():
    """BRU-CXM-04: Mark Recovered asks what the customer said."""
    js = (SRC / "a03" / "m34.js").read_text(encoding="utf-8")
    line = next(ln for ln in js.splitlines() if "m: 'action_close_recovered'" in ln)
    assert "kwarg: 'confirmation'" in line and "ask:" in line


def test_server_serves_and_whitelists_what_the_pages_use():
    m34py = (HERE.parent / "controllers" / "a03" / "m34.py").read_text(encoding="utf-8")
    assert '"fix.complaint.sla.rule": {' in m34py
    assert '"fix.complaint.taxonomy": {' in m34py
    for action in (
        "action_mark_contacted",
        "action_close_unrecovered",
        "action_record_consent",
        "action_publish",
        "action_withdraw_consent",
    ):
        assert '"%s"' % action in m34py, action


# ---------------------------------------------------------------------------
# Third pass (2026-11-19). The user still saw pages without a relevant
# capture. Read against spec sections 5, 9, 10.1 and 11, these spec records
# had no page that could capture them: survey triggers and sampling
# (FR-002..004), response provenance (BRU-CXM-15) and attribution
# (BRU-CXM-10), response anomalies (FR-019, BRU-CXM-11), the conversation
# rating (FR-015), customer updates on a complaint (FR-033, BRU-CXM-07), the
# staff-keyed intake channel (FR-028/038), the SLA by customer tier (FR-031),
# journeys (FR-039) and coded VoC themes (FR-041).
# ---------------------------------------------------------------------------
PASS3_CHIPS = {
    "1": {"Survey Trigger": "fix.survey.trigger"},
    "2": {"Response Anomaly": "fix.cx.response.anomaly"},
    "3": {"Conversation Rating": "fix.cx.rating"},
    "5": {"Customer Update": "fix.complaint.update"},
    "8": {"Customer Journey": "fix.journey.definition", "VoC Theme": "fix.voc.theme"},
}
PASS3_LISTS = {
    "1": ("M34-survey-triggers", "fix.survey.trigger"),
    "2": ("M34-anomalies", "fix.cx.response.anomaly"),
    "3": ("M34-conv-ratings", "fix.cx.rating"),
    "5": ("M34-complaint-updates", "fix.complaint.update"),
}


@pytest.mark.parametrize("no", sorted(PASS3_CHIPS, key=int))
def test_pass3_each_page_captures_its_missing_spec_record(m34, no):
    sub = _sub(m34, no)
    chips = {f["f"]: f for f in sub["forms"]}
    for chip, model in PASS3_CHIPS[no].items():
        assert chip in chips, "page %s has no %s chip" % (no, chip)
        assert chips[chip]["model"] == model, (chip, chips[chip])
        assert chips[chip]["opens"], "chip %s does not open a creatable form" % chip


@pytest.mark.parametrize("no", sorted(PASS3_LISTS, key=int))
def test_pass3_lists_sit_on_their_page_with_a_plus(m34, no):
    screen, model = PASS3_LISTS[no]
    assert screen in _sub(m34, no)["screens"]
    assert screen in m34["nav"]
    cfg = m34["screens"][screen]
    assert cfg["kind"] == "model_list" and cfg["model"] == model
    assert cfg["create"] is True and cfg["empty"]


def test_pass3_page3_plus_records_a_conversation_rating(m34):
    sub = _sub(m34, "3")
    assert sub["create"] == "M34-form-conv-rating"
    form = {f["name"]: f for f in m34["screens"]["M34-form-conv-rating"]["fields"]}
    for name in ("conversation_id", "overall", "timeliness", "professionalism", "behaviour"):
        assert not form[name]["readonly"], name
    # attribution is taken from the conversation, never typed (BRU-CXM-10)
    for name in ("agent_id", "customer_id", "channel"):
        assert form[name]["readonly"], name


def test_pass3_response_records_its_provenance_and_frozen_attribution(m34):
    """BRU-CXM-15: how the response arrived is entered with it; BRU-CXM-10:
    branch and technician are frozen at capture and shown read-only."""
    assert not _field(m34, "M34-form-survey", "response_channel")["readonly"]
    for name in (
        "branch_id",
        "technician_id",
        "responded_at",
        "response_recorded_by_id",
        "incentive_excluded",
    ):
        assert _field(m34, "M34-form-survey", name)["readonly"], name


def test_pass3_anomaly_moves_by_actions(m34):
    """SOD-21 lives in the actions: a typed state would skip it."""
    for name in ("state", "investigator_id", "outcome", "decided_by_id"):
        assert _field(m34, "M34-form-anomaly", name)["readonly"], name
    actions = set(m34["screens"]["M34-anomalies"]["actions"])
    assert {"action_start_investigation", "action_clear", "action_uphold"} <= actions


def test_pass3_loop_case_shows_its_contact_deadline_and_escalation(m34):
    for name in ("contact_due", "escalation_level", "escalated_to_id"):
        assert _field(m34, "M34-form-followup", name)["readonly"], name


def test_pass3_complaint_takes_its_intake_channel_and_referral(m34):
    assert not _field(m34, "M34-record", "received_via")["readonly"]
    for name in ("external_body", "external_reference", "external_response_due"):
        assert not _field(m34, "M34-record", name)["readonly"], name
    assert _field(m34, "M34-record", "intake_channel")["readonly"]


def test_pass3_sla_binding_takes_a_customer_tier(m34):
    assert not _field(m34, "M34-form-sla-rule", "loyalty_tier_id")["readonly"]


def test_pass3_theme_frequency_is_counted_not_typed(m34):
    assert _field(m34, "M34-form-voc-theme", "frequency")["readonly"]
    assert not _field(m34, "M34-form-voc-theme", "survey_ids")["readonly"]


@pytest.mark.parametrize(
    "model",
    ["fix_survey_trigger", "fix_journey_definition", "fix_journey_stage", "fix_voc_theme"],
)
def test_pass3_csm_registers_are_written_by_supervisors_only(model):
    test_csm_registers_are_written_by_supervisors_only(model)


def test_pass3_anomaly_is_raised_by_supervisors_and_never_deleted():
    acl = (
        HERE.parents[2] / "domain/b_customer_engagement/cd_cx_feedback/security/ir.model.access.csv"
    ).read_text(encoding="utf-8")
    rows = [r.split(",") for r in acl.splitlines() if ",model_fix_cx_response_anomaly," in r]
    creators = {r[3] for r in rows if r[6] == "1"}
    assert creators == {"base.group_system", "cd_contact_centre.group_cc_supervisor"}
    assert not any(r[7].strip() == "1" for r in rows), "an anomaly record is evidence"


def test_pass3_server_serves_the_new_records():
    m34py = (HERE.parent / "controllers" / "a03" / "m34.py").read_text(encoding="utf-8")
    for model in (
        "fix.survey.trigger",
        "fix.cx.response.anomaly",
        "fix.cx.rating",
        "fix.complaint.update",
        "fix.journey.definition",
        "fix.journey.stage",
        "fix.voc.theme",
    ):
        assert '"%s": {' % model in m34py, model
    for action in ("action_start_investigation", "action_clear", "action_uphold"):
        assert '"%s"' % action in m34py, action
