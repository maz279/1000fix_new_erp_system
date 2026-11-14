# M32 Conversational AI: every sub-module page captures the records it covers
# (capture audit 2026-11-14).
#
# Before (HEAD 4a4842b9), five of the nine pages had no capture at all:
#   * 2 Entity Extraction listed AI answers and a hard-coded regex report. The
#     spec's entity definitions (fix.entity.definition, FR-CAI-003) had no
#     record, so nobody could say which entities the assistant extracts.
#   * 5 Authenticated Actions listed conversations. The authority matrix the
#     Customer Service Manager owns (FR-CAI-029, BRU-CAI-04, spec section 13)
#     did not exist.
#   * 7 Handoff Decision listed conversations. The handoff triggers
#     ("each independently tunable", FR-CAI-036) did not exist.
#   * 8 Agent Assistance listed AI answers that need a person, with no way to
#     review or send one from the page (FR-CAI-038: never auto-sent).
#   * 9 Analytics had no capture, and the improvement queue (Candidate
#     Intents, AUT-CAI-08/10) sat on no page.
#   * The playground, the model providers, the NLU release bundles and the
#     candidate intents were on no page.
#   * The candidate form let anyone type the mined evidence and the review
#     state, which bypassed Accept/Reject.
#
# Evaluated as the browser evaluates it: node runs the engine's own fregCreate
# and fregPanels over the real registry fragments (the M30 guard's fixture).
from __future__ import annotations

import ast
import importlib.util
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "static" / "src"
CONTROLLER = HERE.parent / "controllers" / "a03" / "m32.py"
WRITABLE_FILE = HERE.parent / "controllers" / "a03" / "writable.py"
CC = HERE.parents[2] / "domain" / "b_customer_engagement" / "cd_contact_centre"

_spec = importlib.util.spec_from_file_location(
    "_estate_pages", HERE / "test_estate_module_pages.py"
)
_estate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_estate)

PROBE = """
import * as M from './meta.mjs';
const { P03_MODULES, P03_MODULE_CREATE, P03_FORM_CHIPS, P03_DATA_SCREENS, P03_REPORT_ROUTES } = M;
function %(create)s
function %(panels)s
const mod = P03_MODULES.M32;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M32', map);
  const panels = fregPanels('M32', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M32:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M32.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: own || null, label: create ? create.label : null, forms,
    reports: panels.reports.map((r) => ({ r, route: P03_REPORT_ROUTES['M32:' + r] || null })) };
});
console.log(JSON.stringify({ subs,
  nav: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => id.startsWith('M32-')).map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create, report: c.report || null,
    tabs: (c.tabs || []).map((t) => t.id),
    pick: c.pickRecord ? { cols: c.pickRecord.cols || [], domain: c.pickRecord.domain || [] } : null,
    save: c.saveAction ? { method: c.saveAction.method, kwargs: c.saveAction.kwargs || {} } : null,
    actions: (c.actions || []).map((a) => ({ m: a.m, kwarg: a.kwarg || null })),
    sections: (c.sections || []).map((s) => ({ tab: s.tab || null, n: (s.fields || []).length })),
    cols: c.cols || [],
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({
      name: f.name, readonly: !!f.readonly, required: !!f.required })) }])),
  by_screen: P03_FORM_CHIPS['M32:__by_screen__'] }));
"""

# What each page must let a person capture: the page's own "+ New" first,
# then every other record the page covers, by its form screen.
CAPTURES = {
    "1": ["M32-form-intent", "M32-form-dataset"],
    "2": ["M32-form-entity"],
    "3": ["M32-form-dialogue"],
    "4": ["M32-form-rag", "M32-form-llm-provider"],
    "5": ["M32-form-authority"],
    "6": ["M32-form-guardrail"],
    "7": ["M32-form-handoff-trigger"],
    "8": ["M32-form-review-answer", "M32-form-send-answer"],
    "9": ["M32-form-candidate-accept", "M32-form-candidate-reject"],
}

# The record each page lists (its grid).
RECORDS = {
    "1": "fix.assistant.intent",
    "2": "fix.assistant.entity",
    "3": "fix.assistant.dialogue",
    "4": "fix.assistant.rag.source",
    "5": "fix.assistant.action.authority",
    "6": "fix.assistant.guardrail",
    "7": "fix.assistant.handoff.trigger",
    "8": "fix.assistant.ask",
    "9": "fix.conversation",
}

# Forms that act on an EXISTING record (step 1 picks it) and run one workflow
# method: the method each must call, which the surface must serve.
PICK_FORMS = {
    "M32-form-review-answer": "action_mark_reviewed",
    "M32-form-send-answer": "action_send_to_customer",
    "M32-form-candidate-accept": "action_accept",
    "M32-form-candidate-reject": "action_reject",
}

# The registers the capture audit built (cd_contact_centre/models/fix_assistant_registers.py).
NEW_MODELS = (
    "fix.assistant.entity",
    "fix.assistant.action.authority",
    "fix.assistant.handoff.trigger",
)


@pytest.fixture(scope="module")
def m32(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m32_capture")
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


def _surfaces():
    """SURFACES of controllers/a03/m32.py (model -> served actions), read without Odoo."""
    tree = ast.parse(CONTROLLER.read_text(encoding="utf-8"))
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "SURFACES"
        ):
            out = {}
            for key, conf in zip(node.value.keys, node.value.values, strict=True):
                acts = set()
                for k, v in zip(conf.keys, conf.values, strict=True):
                    if ast.literal_eval(k) == "actions" and isinstance(v, ast.Set):
                        acts = {ast.literal_eval(e) for e in v.elts}
                out[ast.literal_eval(key)] = acts
            return out
    raise AssertionError("m32.py defines no SURFACES")


def _reports():
    tree = ast.parse(CONTROLLER.read_text(encoding="utf-8"))
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "REPORTS"
        ):
            return {ast.literal_eval(k) for k in node.value.keys}
    raise AssertionError("m32.py defines no REPORTS")


def _writable():
    tree = ast.parse(WRITABLE_FILE.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and node.targets[0].id == "WRITABLE":
            out = {}
            for key, val in zip(node.value.keys, node.value.values, strict=True):
                names = set()
                if isinstance(val, ast.Call) and val.args:
                    names = set(ast.literal_eval(val.args[0]))
                out[ast.literal_eval(key)] = names
            return out
    raise AssertionError("writable.py defines no WRITABLE")


def _sub(m32, no):
    return next(s for s in m32["subs"] if s["no"] == no)


def test_every_page_is_classified(m32):
    assert sorted(s["no"] for s in m32["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m32, no):
    sub = _sub(m32, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]}
    missing = [form for form in [own, *others] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)
    for f in sub["forms"]:
        assert f["kind"] == "model_form", "chip %s opens %s" % (f["f"], f["kind"])


@pytest.mark.parametrize("no", sorted(RECORDS, key=int))
def test_each_page_lists_its_own_record(m32, no):
    assert _sub(m32, no)["model"] == RECORDS[no]


def test_each_captured_record_is_listed_on_its_page(m32):
    """A capture lands on a list of the page it was made from."""
    for sub in m32["subs"]:
        listed = {m32["screens"][s]["model"] for s in sub["screens"] if s in m32["screens"]}
        for f in sub["forms"]:
            assert f["model"] in listed, "page %s captures %s but lists no such record" % (
                sub["no"],
                f["model"],
            )


def test_every_working_screen_sits_on_a_page(m32):
    """Every list, report and the playground is on some sub-module page."""
    placed = {sid for s in m32["subs"] for sid in s["screens"]}
    placed |= {r["route"] for s in m32["subs"] for r in s["reports"]}
    orphans = [
        sid
        for sid, cfg in m32["screens"].items()
        if cfg["kind"] in ("model_list", "table_report", "assistant_play") and sid not in placed
    ]
    assert not orphans, orphans


@pytest.mark.parametrize("sid", sorted(PICK_FORMS))
def test_pick_forms_act_on_an_existing_record_through_its_workflow(m32, sid):
    cfg = m32["screens"][sid]
    assert cfg["kind"] == "model_form" and cfg["pick"], "%s does not pick a record" % sid
    assert cfg["save"] and cfg["save"]["method"] == PICK_FORMS[sid], sid
    assert cfg["save"]["method"] in _surfaces()[cfg["model"]], "%s is not served" % sid
    # what the record says is shown, never retyped: only a reviewer's note
    typed = {f["name"] for f in cfg["fields"] if not f["readonly"]}
    assert typed <= {"review_note"}, "%s lets %s be typed" % (sid, sorted(typed))
    for kwarg_field in cfg["save"]["kwargs"].values():
        assert kwarg_field in typed, "%s passes %s, which the form does not offer" % (
            sid,
            kwarg_field,
        )


def test_review_and_send_pick_only_what_they_can_act_on(m32):
    review = m32["screens"]["M32-form-review-answer"]["pick"]["domain"]
    send = m32["screens"]["M32-form-send-answer"]["pick"]["domain"]
    assert ["requires_human", "=", True] in review
    assert ["human_reviewed_by", "=", False] in review
    assert ["sent_at", "=", False] in send
    assert ["grounded", "=", True] in send
    for sid in ("M32-form-candidate-accept", "M32-form-candidate-reject"):
        assert ["state", "=", "proposed"] in m32["screens"][sid]["pick"]["domain"], sid


def test_candidate_evidence_and_state_are_never_typed(m32):
    """Mined evidence and the review state move only through Accept/Reject."""
    mined = {
        "phrase",
        "language",
        "frequency",
        "distinct_conversations",
        "first_seen",
        "last_seen",
        "sample_utterances",
        "mined_at",
        "state",
    }
    for sid, cfg in m32["screens"].items():
        if cfg["kind"] == "model_form" and cfg["model"] == "fix.assistant.intent.candidate":
            for f in cfg["fields"]:
                if f["name"] in mined:
                    assert f["readonly"], "%s lets %s be typed" % (sid, f["name"])
    assert not mined & _writable()["fix.assistant.intent.candidate"]


def test_register_stamps_are_never_typed(m32):
    computed = {
        "fix.assistant.handoff.trigger": {"category", "mandatory"},
        "fix.assistant.action.authority": {"commitment", "never_delegable"},
        "fix.assistant.entity": {"example_check"},
        "fix.assistant.guardrail": {"create_uid"},
    }
    writable = _writable()
    for model, names in computed.items():
        assert not names & writable.get(model, set()), model
    for sid, cfg in m32["screens"].items():
        if cfg["kind"] == "model_form" and cfg["model"] in computed:
            for f in cfg["fields"]:
                if f["name"] in computed[cfg["model"]]:
                    assert f["readonly"], "%s lets %s be typed" % (sid, f["name"])


def test_every_page_report_opens_its_pack(m32):
    reports = _reports()
    for sub in m32["subs"]:
        for r in sub["reports"]:
            assert r["route"], "page %s report %s has no route" % (sub["no"], r["r"])
            assert m32["screens"][r["route"]]["report"] in reports, r


def test_a_list_offering_new_opens_a_form_of_its_own_model(m32):
    for sid, cfg in m32["screens"].items():
        if cfg["kind"] != "model_list" or cfg.get("create") is False:
            continue
        form = m32["by_screen"].get(sid)
        assert form, "%s offers + New but opens no form" % sid
        assert m32["screens"][form]["model"] == cfg["model"], sid


def test_every_row_action_is_served(m32):
    surfaces = _surfaces()
    for sid, cfg in m32["screens"].items():
        for act in cfg["actions"]:
            assert act["m"] in surfaces[cfg["model"]], "%s %s is not served" % (sid, act["m"])


def test_every_listed_model_is_served(m32):
    surfaces = _surfaces()
    for sid, cfg in m32["screens"].items():
        if cfg["kind"] in ("model_list", "model_form") and cfg["model"] != "fix.conversation":
            # fix.conversation is served by M27's surface (one declaration)
            assert cfg["model"] in surfaces, "%s reads %s, which M32 does not serve" % (
                sid,
                cfg["model"],
            )


def test_every_editable_form_field_is_writable(m32):
    """A field a form lets the user type saves through the write whitelist,
    unless the form runs a workflow method instead of a write."""
    writable = _writable()
    for sid, cfg in m32["screens"].items():
        if cfg["kind"] != "model_form" or cfg["save"]:
            continue
        editable = {f["name"] for f in cfg["fields"] if not f["readonly"]}
        lost = editable - writable.get(cfg["model"], set())
        assert not lost, "%s cannot save %s" % (sid, sorted(lost))


def test_long_forms_are_tabbed(m32):
    """Workspace standard: a form with more than 15 fields is split into tabs,
    and every section names a declared tab (an undeclared tab is invisible)."""
    for sid, cfg in m32["screens"].items():
        if cfg["kind"] != "model_form":
            continue
        if len(cfg["fields"]) > 15:
            assert cfg["tabs"], "%s has %d fields and no tabs" % (sid, len(cfg["fields"]))
        for section in cfg["sections"]:
            if cfg["tabs"]:
                assert section["tab"] in cfg["tabs"], sid


def test_new_registers_are_read_by_staff_and_written_by_supervisors():
    acl = (CC / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    rows = [line.split(",") for line in acl.splitlines()[1:] if line.strip()]
    for model in (*NEW_MODELS, "fix.assistant.guardrail"):
        ref = "model_" + model.replace(".", "_")
        mine = [r for r in rows if r[2] == ref]
        assert mine, model
        for r in mine:
            if r[3] == "base.group_user":
                assert r[4:8] == ["1", "0", "0", "0"], "%s: every user may write it" % model
        assert any(r[3] == "cd_contact_centre.group_cc_supervisor" and r[5] == "1" for r in mine), (
            "%s: no supervisor may write it" % model
        )
    rules = (CC / "security" / "fix_isolation_rules.xml").read_text(encoding="utf-8")
    for model in NEW_MODELS:
        assert 'ref="model_%s"' % model.replace(".", "_") in rules, model
