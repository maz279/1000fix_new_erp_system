# M58 Talent Acquisition: every sub-module page captures the records it covers
# (capture audit 2026-11-17).
#
# Before: the headcount budget and job profiles sat on no page; "Job Postings"
# listed requisitions (there was no posting record, FR-TAO-005/006); referral,
# channel and recruitment cost (FR-TAO-007/008/034) did not exist; practical
# assessments and background checks were listed on their pages with no
# capture; "My Panel Evaluations" sat on no page and its "+ New" was always
# refused by the server; Pre-Boarding offered a hand-made onboarding plan (the
# hire makes it) and had no document checklist (FR-TAO-023/024); Onboarding
# Orchestration captured only first-90 reviews while its tasks, templates and
# induction sessions (FR-TAO-027/029) were on no page or did not exist.
#
# Evaluated as the browser evaluates it: node runs the engine's own fregCreate
# and fregPanels over the real registry fragments (the M22 guard's fixture).
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
TALENT = ROOT / "domain" / "h_people" / "cd_talent"

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
const mod = P03_MODULES.M58;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M58', map);
  const forms = fregPanels('M58', mod, map).forms.map((f) => {
    const id = P03_FORM_CHIPS['M58:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: create && (create.screen || (create.module ? P03_MODULE_CREATE.M58.screen : null)), forms };
});
console.log(JSON.stringify({ subs,
  nav: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => id.startsWith('M58-')).map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create, pick: c.pick || null, cols: c.cols || [],
    report: c.report || null, empty: c.empty || null,
    actions: (c.actions || []).map((a) => a.m),
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({ name: f.name, readonly: !!f.readonly })) }])),
  by_screen: P03_FORM_CHIPS['M58:__by_screen__'] }));
"""

# What each page must let a person capture: the page's own "+ New" record
# first (None: the page only works existing records), then every other record
# the page covers, by its form screen.
CAPTURES = {
    "1": ["M58-form-req", "M58-form-budget", "M58-form-job-profile"],
    "2": [
        "M58-form-candidate",
        "M58-form-posting",
        "M58-form-referral",
        "M58-form-channel",
        "M58-form-cost",
    ],
    "3": [None],
    "4": ["M58-form-interview", "M58-form-assessment"],
    "5": ["M58-form-offer", "M58-form-check"],
    "6": ["M58-form-document"],
    "7": [
        "M58-form-task",
        "M58-form-induction",
        "M58-form-first90",
        "M58-form-template",
        "M58-form-template-line",
    ],
}

# Lists whose records the system makes: never "+ New", always an empty text.
SYSTEM_WRITTEN = {"M58-evaluations", "M58-preboard"}


@pytest.fixture(scope="module")
def m58(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m58_capture")
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


def _sub(m58, no):
    return next(s for s in m58["subs"] if s["no"] == no)


def _fields(m58, screen):
    return {f["name"] for f in m58["screens"][screen]["fields"]}


def test_every_page_is_classified(m58):
    assert sorted(s["no"] for s in m58["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m58, no):
    sub = _sub(m58, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]}
    missing = [form for form in others if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)
    for f in sub["forms"]:
        assert f["kind"] == "model_form", "chip %s opens %s" % (f["f"], f["kind"])


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_every_list_on_a_page_can_be_captured_there(m58, no):
    """A list on a page either refuses "+ New" (system-written) or has its
    form among the page's own "+ New" and chips."""
    sub = _sub(m58, no)
    if CAPTURES[no] == [None]:
        # Screening works the applications captured on Sourcing: its actions
        # (Screen, Invite, Reject with the outcome) are the capture.
        assert {"action_screen", "action_reject"} <= set(
            m58["screens"]["M58-candidates"]["actions"]
        )
        return
    offered = {sub["create"]} | {f["id"] for f in sub["forms"] if f["opens"]}
    for sid in sub["screens"]:
        cfg = m58["screens"][sid]
        if cfg["kind"] != "model_list" or cfg.get("create") is False:
            continue
        form = m58["by_screen"].get(sid)
        assert form in offered, "page %s lists %s but cannot capture it" % (no, sid)


def test_every_working_screen_sits_on_a_page(m58):
    placed = {sid for s in m58["subs"] for sid in s["screens"]}
    orphans = [
        sid
        for sid, cfg in m58["screens"].items()
        if cfg["kind"] == "model_list" and sid not in placed
    ]
    assert not orphans, orphans


def test_every_list_is_in_the_navigation(m58):
    lists = [sid for sid, cfg in m58["screens"].items() if cfg["kind"] == "model_list"]
    assert set(lists) <= set(m58["nav"])


def test_a_list_offering_new_opens_a_form_of_its_own_model(m58):
    for sid, cfg in m58["screens"].items():
        if cfg["kind"] != "model_list" or cfg.get("create") is False:
            continue
        form = m58["by_screen"].get(sid)
        assert form, "%s offers + New but opens no form" % sid
        assert m58["screens"][form]["model"] == cfg["model"], sid


def test_system_written_records_are_never_typed(m58):
    for sid in SYSTEM_WRITTEN:
        cfg = m58["screens"][sid]
        assert cfg.get("create") is False, sid
        assert cfg["empty"], sid
        form = m58["screens"][m58["by_screen"][sid]]
        assert form.get("create") is False and form["pick"], sid


def test_job_postings_list_postings_not_requisitions(m58):
    cfg = m58["screens"]["M58-postings"]
    assert cfg["model"] == "fix.job.posting"
    assert {"action_publish", "action_close"} <= set(cfg["actions"])
    assert {"audience", "internal_only_until"} <= set(cfg["cols"])


@pytest.mark.parametrize(
    "form,needed",
    [
        ("M58-form-req", {"job_profile_id"}),
        ("M58-form-candidate", {"posting_id", "channel_id", "consent_given"}),
        ("M58-form-assessment", {"tasks_performed", "evidence_file", "assessor_id", "score"}),
        ("M58-form-check", {"reference_contact", "evidence_file", "check_type"}),
        ("M58-form-offer", {"probation_class", "probation_months", "benefits"}),
        ("M58-form-onboarding", {"mentor_id", "documents_required", "documents_verified"}),
        ("M58-form-task", {"plan_id", "owner_id", "due_date", "depends_on_id"}),
        ("M58-form-first90", {"plan_id", "milestone", "rating"}),
        (
            "M58-form-job-profile",
            {"position_id", "responsibilities", "competency_ids", "qualifications", "band_id"},
        ),
        ("M58-form-posting", {"requisition_id", "audience", "channel_id", "closes_on"}),
        ("M58-form-referral", {"candidate_id", "referring_employee_id", "reward_amount"}),
        ("M58-form-channel", {"channel_type", "partner_id", "cost_model", "fee"}),
        ("M58-form-cost", {"requisition_id", "cost_type", "amount", "incurred_on"}),
        ("M58-form-document", {"plan_id", "document_type", "document_file", "file_sha256"}),
        ("M58-form-induction", {"plan_id", "session_type", "scheduled_at", "conductor_id"}),
        ("M58-form-template-line", {"template_id", "function", "owner_user_id", "mandatory"}),
    ],
)
def test_forms_capture_what_the_page_is_about(m58, form, needed):
    missing = needed - _fields(m58, form)
    assert not missing, "%s cannot capture %s" % (form, sorted(missing))


def test_task_plan_is_editable_so_new_can_save(m58):
    task = {f["name"]: f for f in m58["screens"]["M58-form-task"]["fields"]}
    assert not task["plan_id"]["readonly"]


@pytest.mark.parametrize(
    "form,field",
    [
        ("M58-form-document", "file_sha256"),
        ("M58-form-document", "verified_by_id"),
        ("M58-form-document", "mandatory"),
        ("M58-form-posting", "internal_only_until"),
        ("M58-form-posting", "state"),
        ("M58-form-referral", "reward_state"),
        ("M58-form-induction", "recorded_by_id"),
    ],
)
def test_decisions_are_never_typed(m58, form, field):
    fields = {f["name"]: f for f in m58["screens"][form]["fields"]}
    assert fields[field]["readonly"], "%s.%s is typed" % (form, field)


def test_the_new_reports_are_served():
    import ast

    text = (HERE.parent / "controllers" / "a09" / "m58.py").read_text(encoding="utf-8")
    tree = ast.parse(text)
    names = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
    assert {"cost_per_hire", "day_one_readiness"} <= names
    for key in ('"cost_per_hire": cost_per_hire', '"day_one_readiness": day_one_readiness'):
        assert key in text


def test_the_server_serves_every_list_model_and_action(m58):
    from importlib import util

    spec = util.spec_from_file_location("_m58ctl", HERE.parent / "controllers" / "a09" / "m58.py")
    text = spec.loader.get_data(spec.origin).decode("utf-8")
    for cfg in m58["screens"].values():
        if cfg["kind"] != "model_list":
            continue
        assert '"%s"' % cfg["model"] in text, "%s is not served" % cfg["model"]
        for action in cfg["actions"]:
            assert '"%s"' % action in text, "%s.%s is not served" % (cfg["model"], action)


def test_the_whitelist_lets_the_new_fields_save():
    text = (HERE.parent / "controllers" / "a09" / "writable.py").read_text(encoding="utf-8")
    for model, names in {
        "fix.job.posting": ("title", "requisition_id", "audience", "channel_id"),
        "fix.preboarding.document": ("plan_id", "document_type", "document_file"),
        "fix.onboarding.induction": ("plan_id", "session_type", "scheduled_at", "conductor_id"),
        "fix.talent.referral": ("candidate_id", "referring_employee_id", "reward_amount"),
    }.items():
        block = text[text.index('"%s": frozenset(' % model) :]
        block = block[: block.index("),")]
        for name in names:
            assert '"%s"' % name in block, (model, name)
        for decided in ("state", "reward_state", "verified_by_id", "file_sha256"):
            assert '"%s"' % decided not in block, (model, decided)


def test_access_rows_keep_decisions_with_their_roles():
    acl = (TALENT / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    rows = {}
    for r in acl.splitlines()[1:]:
        parts = r.split(",")
        rows.setdefault(parts[2], {})[parts[3]] = parts[4:8]
    # plain users never create documents, postings, referrals or costs
    for model in (
        "model_fix_preboarding_document",
        "model_fix_job_posting",
        "model_fix_talent_referral",
        "model_fix_recruitment_cost",
    ):
        assert "base.group_user" not in rows[model], model
    assert rows["model_fix_preboarding_document"]["cd_talent.group_background_verifier"] == [
        "1",
        "1",
        "0",
        "0",
    ]
    # a conductor records an induction, never creates one
    assert rows["model_fix_onboarding_induction"]["base.group_user"] == ["1", "1", "0", "0"]
