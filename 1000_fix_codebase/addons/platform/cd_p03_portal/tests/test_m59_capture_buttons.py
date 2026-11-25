# M59 Health, Safety & Wellbeing: every sub-module page captures each record
# it covers (capture audit 2026-11-18).
#
# Before (HEAD 32e24dc9), evaluated with the engine's own fregCreate/fregPanels:
#   * page 1 (Hazard Register & Risk) listed safety inspections with no chip;
#   * page 2 (Procedures & Permits) held only the JSA: there was no safe work
#     procedure (FR-HSE-006) and no permit to work (FR-HSE-007);
#   * page 3 (Incident Management) had the incident only: the investigation
#     team, root cause and CAPA lists and forms sat on NO page, and there was
#     no witness statement (FR-HSE-012);
#   * page 5 (PPE) offered no chip for the PPE item;
#   * page 6 (Field & Road Safety) had no chip at all: the lone-worker and
#     hazardous-substance lists could not be captured there, no road check
#     could pass without a driving licence record that no M59 page reached,
#     and there was no right-to-stop-work refusal (FR-HSE-026, BRU-HSE-10 H)
#     and no customer-premises hazard (FR-HSE-025);
#   * page 7 (Training & Drills) had no chip: the committee list had no
#     capture, committee members and meetings sat on no page, and there was no
#     site emergency plan (FR-HSE-035);
#   * page 8 (Health & Wellbeing): "Return-to-Work" opened the periodic
#     medical form; the fitness status and lapsed-certification follow-ups
#     sat on no page.
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
CONTROLLER = HERE.parent / "controllers" / "a09" / "m59.py"
WRITABLE_FILE = HERE.parent / "controllers" / "a09" / "writable.py"
HSE = HERE.parents[2] / "domain" / "h_people" / "cd_hse"

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
const mod = P03_MODULES.M59;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M59', map);
  const forms = fregPanels('M59', mod, map).forms.map((f) => {
    const id = P03_FORM_CHIPS['M59:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: create && (create.screen || (create.module ? P03_MODULE_CREATE.M59.screen : null)), forms };
});
console.log(JSON.stringify({ subs,
  nav: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => id.startsWith('M59-')).map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create, cols: c.cols || [],
    actions: (c.actions || []).map((a) => ({ m: a.m, kwarg: a.kwarg || null })),
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({
      name: f.name, readonly: !!f.readonly, value: f.value === undefined ? null : f.value })),
    tabs: (c.tabs || []).map((t) => t.id) }])) }));
"""

# What each page lets a person capture: its own "+ New" first, then every
# other record the page covers, by form screen.
CAPTURES = {
    "1": ["M59-form-hazard", "M59-form-inspection"],
    "2": ["M59-form-jsa", "M59-form-procedure", "M59-form-permit"],
    "3": [
        "M59-form-incident",
        "M59-form-anonymous",
        "M59-form-investigation-member",
        "M59-form-witness",
        "M59-form-root-cause",
        "M59-form-capa",
    ],
    "4": ["M59-form-statutory-register"],
    "5": ["M59-form-ppe", "M59-form-ppe-issue"],
    "6": [
        "M59-form-roadcheck",
        "M46-form-driver",
        "M59-form-loneworker",
        "M59-form-work-refusal",
        "M59-form-site-hazard",
        "M59-form-substance",
    ],
    "7": [
        "M59-form-drill",
        "M59-form-emergency-plan",
        "M59-form-committee",
        "M59-form-committee-member",
    ],
    "8": ["M59-form-health", "M59-form-rtw"],
}

# A chip may open another module's form for a record that module masters
# (the M02 rule); its list then lives on that module's page.
CROSS_MODULE = {"M46-form-driver": "fix.driver"}

NEW_MODELS = (
    "fix.hse.procedure",
    "fix.hse.permit",
    "fix.hse.witness.statement",
    "fix.hse.work.refusal",
    "fix.hse.location.hazard",
    "fix.hse.emergency.plan",
)

# What a form must never let a person type: the state and every decision
# stamp, measured figure or system-written trace.
NEVER_TYPED = {
    "fix.hse.procedure": {
        "state",
        "version",
        "previous_id",
        "prepared_by_id",
        "submitted_by_id",
        "submitted_on",
        "approved_by_id",
        "approved_on",
        "review_due_on",
        "rejection_reason",
    },
    "fix.hse.permit": {
        "name",
        "state",
        "requested_by_id",
        "requested_on",
        "authorised_by_id",
        "authorised_on",
        "authorisation_note",
        "closed_by_id",
        "closed_on",
        "closure_note",
        "cancel_reason",
    },
    "fix.hse.witness.statement": {"name", "taken_by_id", "taken_on"},
    "fix.hse.work.refusal": {
        "name",
        "state",
        "recorded_by_id",
        "recorded_at",
        "reviewed_by_id",
        "reviewed_on",
        "outcome",
        "review_note",
    },
    "fix.hse.location.hazard": {
        "name",
        "state",
        "reported_by_id",
        "reported_on",
        "confirmed_by_id",
        "confirmed_on",
        "retired_by_id",
        "retire_reason",
    },
    "fix.hse.emergency.plan": {
        "state",
        "version",
        "previous_id",
        "prepared_by_id",
        "approved_by_id",
        "approved_on",
        "last_reviewed_on",
        "next_review_date",
        "review_due",
    },
    "fix.hse.health": {"state", "fitness_status_id"},
}


@pytest.fixture(scope="module")
def m59(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m59_capture")
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


def _assigned(path, name):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == name
        ):
            return node.value
    raise AssertionError("%s defines no %s" % (path.name, name))


def _surfaces():
    out = {}
    value = _assigned(CONTROLLER, "SURFACES")
    for key, conf in zip(value.keys, value.values, strict=True):
        acts = set()
        for k, v in zip(conf.keys, conf.values, strict=True):
            if ast.literal_eval(k) == "actions" and isinstance(v, ast.Set):
                acts = {ast.literal_eval(e) for e in v.elts}
        out[ast.literal_eval(key)] = acts
    return out


def _writable():
    out = {}
    value = _assigned(WRITABLE_FILE, "WRITABLE")
    for key, val in zip(value.keys, value.values, strict=True):
        names = set()
        if isinstance(val, ast.Call) and val.args:
            names = set(ast.literal_eval(val.args[0]))
        out[ast.literal_eval(key)] = names
    return out


def _model_classes():
    """{model: ({fields}, {methods})} defined or extended in cd_hse."""
    out = {}
    for path in (HSE / "models").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for cls in (n for n in tree.body if isinstance(n, ast.ClassDef)):
            names, flds = set(), set()
            for stmt in cls.body:
                if not (isinstance(stmt, ast.Assign) and isinstance(stmt.targets[0], ast.Name)):
                    continue
                target = stmt.targets[0].id
                if target in ("_name", "_inherit") and isinstance(stmt.value, ast.Constant):
                    names.add(stmt.value.value)
                elif target == "_inherit" and isinstance(stmt.value, ast.List):
                    names.update(e.value for e in stmt.value.elts if isinstance(e, ast.Constant))
                elif (
                    isinstance(stmt.value, ast.Call)
                    and isinstance(stmt.value.func, ast.Attribute)
                    and getattr(stmt.value.func.value, "id", "") == "fields"
                ):
                    flds.add(target)
            methods = {f.name for f in cls.body if isinstance(f, ast.FunctionDef)}
            for name in names:
                entry = out.setdefault(name, (set(), set()))
                entry[0].update(flds)
                entry[1].update(methods)
    # the incident-child base gives its children incident_id and company_id
    base = out.get("fix.hse.incident.child", (set(), set()))
    for child in ("fix.hse.witness.statement", "fix.hse.root.cause", "fix.hse.capa"):
        if child in out:
            out[child][0].update(base[0])
            out[child][1].update(base[1])
    return out


def _sub(m59, no):
    return next(s for s in m59["subs"] if s["no"] == no)


def test_every_page_is_classified(m59):
    assert sorted(s["no"] for s in m59["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m59, no):
    sub = _sub(m59, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]} | {sub["create"]}
    missing = [form for form in [own, *others] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)


def test_each_captured_record_is_listed_on_its_page(m59):
    for sub in m59["subs"]:
        listed = {m59["screens"][s]["model"] for s in sub["screens"] if s in m59["screens"]}
        listed.add(sub["model"])
        for f in sub["forms"]:
            if f["id"] in CROSS_MODULE:
                assert f["model"] == CROSS_MODULE[f["id"]], f
                continue
            assert f["model"] in listed, "page %s captures %s but lists none" % (
                sub["no"],
                f["model"],
            )


def test_every_creatable_list_on_a_page_has_its_capture(m59):
    for sub in m59["subs"]:
        captured = {f["model"] for f in sub["forms"] if f["opens"]}
        if sub["create"]:
            captured.add(m59["screens"][sub["create"]]["model"])
        for sid in sub["screens"]:
            cfg = m59["screens"].get(sid, {})
            if cfg.get("kind") == "model_list" and cfg.get("create") is not False:
                assert cfg["model"] in captured, "page %s lists %s (%s) with no capture" % (
                    sub["no"],
                    cfg["model"],
                    sid,
                )


def test_every_working_screen_sits_on_a_page(m59):
    """CAPA, root causes, the investigation team, committee members and
    meetings, fitness and follow-ups were on no page before the audit."""
    placed = {sid for s in m59["subs"] for sid in s["screens"]}
    orphans = sorted(
        sid
        for sid, cfg in m59["screens"].items()
        if cfg["kind"] == "model_list" and sid not in placed
    )
    assert not orphans, orphans


def test_every_screen_on_a_page_is_in_the_navigation(m59):
    nav = set(m59["nav"])
    missing = sorted(
        sid
        for sub in m59["subs"]
        for sid in sub["screens"]
        if sid in m59["screens"] and sid not in nav
    )
    assert not missing, missing


def test_return_to_work_starts_a_return_to_work_record(m59):
    chip = next(f for f in _sub(m59, "8")["forms"] if f["f"] == "Return-to-Work")
    assert chip["id"] == "M59-form-rtw"
    rtype = next(f for f in m59["screens"]["M59-form-rtw"]["fields"] if f["name"] == "record_type")
    assert rtype["value"] == "return_to_work"


def test_every_served_action_exists_on_its_model():
    classes = _model_classes()
    generic = {"action_request_approval", "action_recall_approval"}  # the M63 mixin's verbs
    for model, acts in _surfaces().items():
        methods = classes.get(model, (set(), set()))[1]
        missing = acts - methods - generic
        assert not missing, "%s serves %s, which the model lacks" % (model, sorted(missing))


def test_every_list_action_is_served(m59):
    surfaces = _surfaces()
    for sid, cfg in m59["screens"].items():
        if cfg["kind"] != "model_list" or not cfg["actions"]:
            continue
        served = surfaces[cfg["model"]]
        for act in cfg["actions"]:
            assert act["m"] in served, "%s offers %s, not served" % (sid, act["m"])


def test_every_list_column_exists_on_its_model(m59):
    """A column the model lacks is dropped silently by the endpoint."""
    classes = _model_classes()
    for sid, cfg in m59["screens"].items():
        if cfg["kind"] != "model_list" or cfg["model"] not in NEW_MODELS:
            continue
        known = classes[cfg["model"]][0] | {"display_name"}
        unknown = [c for c in cfg["cols"] if c not in known]
        assert not unknown, "%s lists %s, not fields of %s" % (sid, unknown, cfg["model"])


def test_every_new_form_field_exists_on_its_model(m59):
    classes = _model_classes()
    for sid, cfg in m59["screens"].items():
        if cfg["kind"] != "model_form" or cfg["model"] not in NEW_MODELS:
            continue
        known = classes[cfg["model"]][0]
        unknown = [f["name"] for f in cfg["fields"] if f["name"] not in known]
        assert not unknown, "%s shows %s, not fields of %s" % (sid, unknown, cfg["model"])


@pytest.mark.parametrize("model", NEW_MODELS)
def test_new_registers_are_served_and_whitelisted(m59, model):
    assert model in _surfaces()
    forms = [
        c for c in m59["screens"].values() if c["kind"] == "model_form" and c["model"] == model
    ]
    assert forms, "%s has no workspace form" % model
    typed = {f["name"] for c in forms for f in c["fields"] if not f["readonly"]}
    assert _writable()[model] == typed


@pytest.mark.parametrize("model", sorted(NEVER_TYPED))
def test_stamps_and_decisions_are_never_typed(model):
    leaked = _writable().get(model, set()) & NEVER_TYPED[model]
    assert not leaked, (model, sorted(leaked))


def test_new_forms_are_tabbed(m59):
    """AGENTS.md: forms are split into Dynamics-style tabs."""
    for sid, cfg in m59["screens"].items():
        if cfg["kind"] == "model_form" and cfg["model"] in NEW_MODELS:
            assert len(cfg["tabs"]) >= 2, sid


@pytest.mark.parametrize(
    ("sid", "method", "kwarg"),
    [
        ("M59-procedures", "action_reject", "reason"),
        ("M59-permits", "action_close", "note"),
        ("M59-permits", "action_cancel", "reason"),
        ("M59-work-refusals", "action_uphold", "note"),
        ("M59-work-refusals", "action_made_safe", "note"),
        ("M59-work-refusals", "action_not_substantiated", "note"),
        ("M59-site-hazards", "action_retire", "reason"),
    ],
)
def test_decisions_ask_for_their_reason(m59, sid, method, kwarg):
    acts = {a["m"]: a for a in m59["screens"][sid]["actions"]}
    assert acts[method]["kwarg"] == kwarg


def test_new_models_are_secured():
    acl = (HSE / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    rules = (HSE / "security" / "fix_hse_capture_rules.xml").read_text(encoding="utf-8")
    for model in NEW_MODELS:
        xmlid = "model_" + model.replace(".", "_")
        rows = [r.split(",") for r in acl.splitlines() if (",%s," % xmlid) in r]
        assert rows, model
        assert 'ref="%s"' % xmlid in rules, "%s has no company rule" % model
    # evidence is never deleted; a plain user never writes a published procedure
    # or an emergency plan, and never reads a witness statement
    for model in ("fix_hse_witness_statement", "fix_hse_work_refusal", "fix_hse_location_hazard"):
        rows = [r.split(",") for r in acl.splitlines() if ",model_%s," % model in r]
        assert all(r[-1].strip() == "0" for r in rows), "%s: nobody deletes" % model
    for r in (r.split(",") for r in acl.splitlines()):
        if len(r) > 7 and r[3] == "base.group_user":
            if r[2] in ("model_fix_hse_procedure", "model_fix_hse_emergency_plan"):
                assert r[5:8] == ["0", "0", "0"], r
            assert r[2] != "model_fix_hse_witness_statement", r
    for model in ("fix_hse_procedure", "fix_hse_permit", "fix_hse_work_refusal"):
        assert 'ref="model_%s"' % model in rules


def test_the_new_file_loads_last():
    init = (HSE / "models" / "__init__.py").read_text(encoding="utf-8")
    body = init[init.index("from . import (") :]
    assert body.index("fix_hse_capture") > body.index("fix_hse_followup")
    assert "ruff: noqa: I001" in init
