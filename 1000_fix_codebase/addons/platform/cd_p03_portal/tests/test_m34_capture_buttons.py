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
    "6": "form",  # complaint SLA binding (admin) chip; complaints reassessed on their list
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


@pytest.mark.parametrize("no", ["2", "3"])
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


def test_detractor_states_move_by_actions(m34):
    assert _field(m34, "M34-form-followup", "state")["readonly"]
    actions = set(m34["screens"]["M34-detractor"]["actions"])
    assert {
        "action_mark_contacted",
        "action_close_recovered",
        "action_close_unrecovered",
    } <= actions


def test_sla_page_reaches_the_binding(m34):
    sub = _sub(m34, "6")
    assert sub["model"] == "fix.complaint.sla.rule"
    assert "M34-sla-rules" in sub["screens"]
    chips = {f["f"]: f for f in sub["forms"]}
    assert chips["Complaint SLA Binding"]["model"] == "fix.complaint.sla.rule"
    assert chips["Complaint SLA Binding"]["opens"]
    # administrator-only create (model ACL): no "+ New" a user's save would hit
    assert sub["create"] is None
    assert m34["screens"]["M34-sla-rules"]["create"] is False


def test_sla_binding_is_admin_create_only():
    acl = (
        HERE.parents[2] / "domain/b_customer_engagement/cd_cx_feedback/security/ir.model.access.csv"
    ).read_text(encoding="utf-8")
    rows = [r.split(",") for r in acl.splitlines() if "model_fix_complaint_sla_rule" in r]
    creators = {r[3] for r in rows if r[6] == "1"}
    assert creators == {"base.group_system"}, creators


def test_voc_page_captures_a_review(m34):
    sub = _sub(m34, "8")
    assert sub["create"] == "M34-form-review"
    assert "M34-reviews" in sub["screens"]


def test_server_serves_and_whitelists_what_the_pages_use():
    m34py = (HERE.parent / "controllers" / "a03" / "m34.py").read_text(encoding="utf-8")
    assert '"fix.complaint.sla.rule": {' in m34py
    for action in ("action_mark_contacted", "action_close_unrecovered"):
        assert '"%s"' % action in m34py, action
