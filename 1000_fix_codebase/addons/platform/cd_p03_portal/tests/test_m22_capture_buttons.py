# M22 Learning & Certification: every sub-module page captures the records it
# covers (capture audit 2026-11-13).
#
# Before: every page had a "+ New", but several records the pages list or the
# spec assigns them had no capture there. Device categories sat on Competency
# Framework with no chip; the role requirement (FR-LMS-002) had no capture on
# it; the over-budget request and the training budget sat on Training Delivery
# with no chip; the certification waivers (override log, FR-LMS-040) were on
# no page at all. "Schedule & Attendance" captured an enrolment with no
# session, date, trainer, venue or attendance - there was no session record
# (FR-LMS-020/021/023). Forms could not capture what the page is about: a
# learning path with no competencies or courses, OJT with no end date or
# observations, evidence naming no technician or brand, an assessment with
# no method or evidence.
#
# Evaluated as the browser evaluates it: node runs the engine's own fregCreate
# and fregPanels over the real registry fragments (the M37 guard's fixture).
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
ROOT = HERE.parents[2]

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
const mod = P03_MODULES.M22;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M22', map);
  const forms = fregPanels('M22', mod, map).forms.map((f) => {
    const id = P03_FORM_CHIPS['M22:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: create && (create.screen || (create.module ? 'module' : null)), forms };
});
console.log(JSON.stringify({ subs,
  nav: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => id.startsWith('M22-')).map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create, cols: c.cols || [],
    actions: (c.actions || []).map((a) => a.m),
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({ name: f.name, readonly: !!f.readonly })) }])),
  by_screen: P03_FORM_CHIPS['M22:__by_screen__'] }));
"""

# What each page must let a person capture: the page's own "+ New" record
# first, then every other record the page covers, by its form screen.
CAPTURES = {
    "1": ["M22-form-competency", "M22-form-device", "M22-form-path"],
    "2": ["M22-form-assessment"],
    "3": ["M22-form-certification"],
    "4": [
        "M22-form-enrollment",
        "M22-form-course",
        "M22-form-path",
        "M22-form-session",
        "M22-form-budget",
        "M22-form-budget-exception",
    ],
    "5": ["M22-form-ojt"],
    "6": ["M22-form-evidence"],
}


@pytest.fixture(scope="module")
def m22(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m22_capture")
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


def _sub(m22, no):
    return next(s for s in m22["subs"] if s["no"] == no)


def _fields(m22, screen):
    return {f["name"] for f in m22["screens"][screen]["fields"]}


def test_every_page_is_classified(m22):
    assert sorted(s["no"] for s in m22["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m22, no):
    sub = _sub(m22, no)
    own, *others = CAPTURES[no]
    if sub["create"] == "module":
        assert own == "M22-form-certification"
    else:
        assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]}
    missing = [form for form in others if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)
    for f in sub["forms"]:
        assert f["kind"] == "model_form", "chip %s opens %s" % (f["f"], f["kind"])


def test_every_working_screen_sits_on_a_page(m22):
    placed = {sid for s in m22["subs"] for sid in s["screens"]}
    orphans = [
        sid
        for sid, cfg in m22["screens"].items()
        if cfg["kind"] == "model_list" and sid not in placed
    ]
    assert not orphans, orphans


def test_every_list_is_in_the_navigation(m22):
    lists = [sid for sid, cfg in m22["screens"].items() if cfg["kind"] == "model_list"]
    assert set(lists) <= set(m22["nav"])


def test_a_list_offering_new_opens_a_form_of_its_own_model(m22):
    for sid, cfg in m22["screens"].items():
        if cfg["kind"] != "model_list" or cfg.get("create") is False:
            continue
        form = m22["by_screen"].get(sid)
        assert form, "%s offers + New but opens no form" % sid
        assert m22["screens"][form]["model"] == cfg["model"], sid


def test_the_waiver_log_is_on_the_register_page_and_never_created_there(m22):
    assert "M22-waivers" in _sub(m22, "3")["screens"]
    assert m22["screens"]["M22-waivers"]["create"] is False


@pytest.mark.parametrize(
    "form,needed",
    [
        ("M22-form-path", {"target_role", "competency_ids", "course_ids", "min_level"}),
        ("M22-form-ojt", {"date_from", "date_to", "hours", "notes", "mentor_id"}),
        ("M22-form-evidence", {"employee_id", "brand_id", "evidence_file", "attachment_note"}),
        ("M22-form-assessment", {"assessor_id", "score", "notes"}),
        ("M22-form-device", {"parent_id", "repair_tier_floor"}),
        ("M22-form-enrollment", {"session_id", "attendance"}),
        (
            "M22-form-session",
            {"course_id", "trainer_id", "vendor_id", "venue", "date_start", "date_end", "capacity"},
        ),
    ],
)
def test_forms_capture_what_the_page_is_about(m22, form, needed):
    missing = needed - _fields(m22, form)
    assert not missing, "%s cannot capture %s" % (form, sorted(missing))


def test_attendance_is_recorded_by_action_never_typed(m22):
    enr = {f["name"]: f for f in m22["screens"]["M22-form-enrollment"]["fields"]}
    assert enr["attendance"]["readonly"]
    sched = m22["screens"]["M22-schedule"]
    assert {"session_id", "attendance"} <= set(sched["cols"])
    assert {"action_mark_attended", "action_mark_absent"} <= set(sched["actions"])
    sess = m22["screens"]["M22-sessions"]
    assert {"action_schedule", "action_mark_held", "action_cancel"} <= set(sess["actions"])


def test_the_server_serves_every_list_model_and_action():
    text = (HERE.parent / "controllers" / "a09" / "m22.py").read_text(encoding="utf-8")
    assert '"fix.training.session"' in text
    for action in (
        "action_mark_attended",
        "action_mark_absent",
        "action_schedule",
        "action_mark_held",
    ):
        assert '"%s"' % action in text, action


def test_the_whitelist_lets_the_new_fields_save():
    text = (HERE.parent / "controllers" / "a09" / "writable.py").read_text(encoding="utf-8")
    block = text[text.index('"fix.training.session": frozenset(') :]
    block = block[: block.index("),")]
    for name in ("course_id", "trainer_id", "venue", "date_start", "date_end", "capacity"):
        assert '"%s"' % name in block, name
    assert '"state"' not in block, "the session state moves by its actions only"


def test_only_training_managers_create_sessions():
    acl = (ROOT / "domain/h_people/cd_competency/security/ir.model.access.csv").read_text(
        encoding="utf-8"
    )
    rows = {
        r.split(",")[3]: r.split(",")[4:8]
        for r in acl.splitlines()
        if "model_fix_training_session," in r
    }
    assert rows["base.group_user"] == ["1", "0", "0", "0"]
    assert rows["cd_competency.group_training"] == ["1", "1", "1", "0"]
