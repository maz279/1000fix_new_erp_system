# M57 Performance, Incentives & Compensation: every sub-module page captures
# each record it covers (capture audit 2026-11-17).
#
# Before (HEAD c5feece6), evaluated with the engine's own fregCreate/fregPanels:
#   * page 1 (Goals & KPIs) captured goals only: its "KPI Definitions" list
#     showed technician scorecards (create: false) and no scorecard could be
#     started anywhere in the workspace, so no incentive run could compute;
#     there was no KPI definition at all (FR-PIC-006 P0);
#   * page 2 (Review Cycles) offered a single review: no review cycle with a
#     population and deadlines (FR-PIC-016), and the PIP list had no chip;
#   * page 3 (Multi-Source Feedback) offered "+ New 360 Review" - page 2's
#     record; there was no feedback record (FR-PIC-020);
#   * page 4 (Rating & Calibration) captured nothing (create: false): no
#     calibration session (FR-PIC-021, BRU-PIC-13), and calibration could not
#     move a rating (the calibrated rating was the manager's, always);
#   * page 5 (Incentive Design & Calculation) had no "+ New"; its one chip,
#     "Incentive Scheme", opened an incentive RUN; the scheme and version
#     forms were on no chip; no incentive adjustment (FR-PIC-033 P1,
#     BRU-PIC-10 H);
#   * page 7 (Compensation Review) had no chip; succession plans no capture;
#     no compensation cycle with a budget (FR-PIC-038, BRU-PIC-17 H).
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
CONTROLLER = HERE.parent / "controllers" / "a09" / "m57.py"
WRITABLE_FILE = HERE.parent / "controllers" / "a09" / "writable.py"
PERF = HERE.parents[2] / "domain" / "h_people" / "cd_performance"

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
const mod = P03_MODULES.M57;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M57', map);
  const panels = fregPanels('M57', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M57:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M57.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: own || null, forms,
    reports: panels.reports.map((r) => ({ r, route: P03_REPORT_ROUTES['M57:' + r] || null })) };
});
const screen = (c) => ({
    kind: c.kind, model: c.model || null, create: c.create, report: c.report || null,
    tabs: (c.tabs || []).length, lines: c.lines ? c.lines.field : null,
    actions: (c.actions || []).map((a) => ({ m: a.m, kwargs: (a.asks || []).map((q) => q.kwarg).concat(a.kwarg ? [a.kwarg] : []) })),
    cols: c.cols || [],
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({
      name: f.name, readonly: !!f.readonly, required: !!f.required })) });
console.log(JSON.stringify({ subs, forms: mod.forms,
  labelled: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => id.startsWith('M57-')).map(([id, c]) => [id, screen(c)])) }));
"""


@pytest.fixture(scope="module")
def m57(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m57_capture")
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
    """{model: ({fields}, {methods})} defined or extended in cd_performance."""
    out = {}
    for path in (PERF / "models").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for cls in (n for n in tree.body if isinstance(n, ast.ClassDef)):
            names, flds = set(), set()
            for stmt in cls.body:
                if not (isinstance(stmt, ast.Assign) and isinstance(stmt.targets[0], ast.Name)):
                    continue
                target = stmt.targets[0].id
                if target in ("_name", "_inherit") and isinstance(stmt.value, ast.Constant):
                    names.add(stmt.value.value)
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
    return out


# What each page lets a person capture: its own "+ New" first, then every
# other record the page covers, by form screen.
CAPTURES = {
    "1": ["M57-form-goal", "M57-form-kpi", "M57-form-scorecard"],
    "2": ["M57-form-review-cycle", "M57-form-review", "M57-form-pip"],
    "3": ["M57-form-feedback"],
    "4": ["M57-form-calibration"],
    "5": [
        "M57-form-scheme-def",
        "M57-form-scheme-version",
        "M57-form-scheme",
        "M57-form-adjustment",
    ],
    "6": ["M57-form-recognition"],
    "7": ["M57-form-comp-cycle", "M57-form-comp", "M57-form-succession"],
}

NEW_MODELS = (
    "fix.kpi.definition",
    "fix.performance.review.cycle",
    "fix.performance.feedback",
    "fix.performance.calibration.session",
    "fix.incentive.adjustment",
    "fix.compensation.cycle",
)

# What a form must never let a person type: the state, every decision stamp
# and every measured or answered figure.
NEVER_TYPED = {
    "fix.kpi.definition": {
        "state",
        "version_no",
        "date_to",
        "submitted_by_id",
        "approved_by_id",
        "approved_at",
        "rejection_reason",
        "kind",
        "unit",
        "direction",
        "source_module",
    },
    "fix.performance.review.cycle": {
        "state",
        "skipped_note",
        "opened_by_id",
        "closed_by_id",
        "review_count",
        "closed_count",
        "overdue_count",
    },
    "fix.performance.feedback": {
        "name",
        "state",
        "rating",
        "strengths",
        "improvements",
        "decline_reason",
        "requested_by_id",
        "submitted_at",
    },
    "fix.performance.calibration.session": {
        "name",
        "state",
        "distribution_before",
        "distribution_after",
        "pending_count",
        "concluded_by_id",
    },
    "fix.incentive.adjustment": {
        "name",
        "state",
        "approval_state",
        "approved_by_id",
        "approved_at",
        "applied_run_id",
        "applied_line_id",
    },
    "fix.compensation.cycle": {
        "state",
        "committed_amount",
        "pending_amount",
        "remaining_amount",
        "opened_by_id",
    },
    "fix.performance.scorecard": {"kpi_attainment", "kpi_breaches", "first_time_fix", "score"},
    "fix.performance.review": {"cycle_id", "feedback_count", "feedback_avg", "calibrated_rating"},
    "fix.compensation.proposal": {"cycle_id", "over_budget"},
}


def _sub(m57, no):
    return next(s for s in m57["subs"] if s["no"] == no)


def test_every_page_is_classified(m57):
    assert sorted(s["no"] for s in m57["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m57, no):
    sub = _sub(m57, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]} | {sub["create"]}
    missing = [form for form in [own, *others] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)


def test_the_feedback_page_no_longer_offers_a_review(m57):
    assert _sub(m57, "3")["create"] != "M57-form-review"
    assert _sub(m57, "3")["model"] == "fix.performance.feedback"


def test_the_incentive_scheme_chip_opens_a_scheme_not_a_run(m57):
    chip = next(f for f in _sub(m57, "5")["forms"] if f["f"] == "Incentive Scheme")
    assert chip["model"] == "fix.incentive.scheme", chip


def test_each_captured_record_is_listed_on_its_page(m57):
    for sub in m57["subs"]:
        listed = {m57["screens"][s]["model"] for s in sub["screens"] if s in m57["screens"]}
        listed.add(sub["model"])
        captures = list(sub["forms"])
        if sub["create"]:
            captures.append({"model": m57["screens"][sub["create"]]["model"]})
        for f in captures:
            assert f["model"] in listed, "page %s captures %s but lists none" % (
                sub["no"],
                f["model"],
            )


def test_every_creatable_list_on_a_page_has_its_capture(m57):
    for sub in m57["subs"]:
        captured = {f["model"] for f in sub["forms"] if f["opens"]}
        if sub["create"]:
            captured.add(m57["screens"][sub["create"]]["model"])
        for sid in sub["screens"]:
            cfg = m57["screens"].get(sid, {})
            if cfg.get("kind") == "model_list" and cfg.get("create") is not False:
                assert cfg["model"] in captured, "page %s lists %s (%s) with no capture" % (
                    sub["no"],
                    cfg["model"],
                    sid,
                )


def test_every_working_screen_sits_on_a_page(m57):
    placed = {sid for s in m57["subs"] for sid in s["screens"]}
    placed |= {r["route"] for s in m57["subs"] for r in s["reports"]}
    orphans = [
        sid
        for sid, cfg in m57["screens"].items()
        if cfg["kind"] in ("model_list", "table_report") and sid not in placed
    ]
    assert not orphans, orphans


def test_every_screen_on_a_page_has_a_navigation_label(m57):
    labelled = set(m57["labelled"])
    unlabelled = sorted(
        sid
        for sub in m57["subs"]
        for sid in sub["screens"]
        if sid in m57["screens"] and sid not in labelled
    )
    assert not unlabelled, unlabelled


def test_every_served_action_exists_on_its_model():
    classes = _model_classes()
    generic = {"action_request_approval", "action_recall_approval"}  # the M63 mixin's verbs
    for model, acts in _surfaces().items():
        methods = classes.get(model, (set(), set()))[1]
        missing = acts - methods - generic
        assert not missing, "%s serves %s, which the model lacks" % (model, sorted(missing))


def test_every_list_action_is_served(m57):
    surfaces = _surfaces()
    for sid, cfg in m57["screens"].items():
        if cfg["kind"] != "model_list" or not cfg["actions"]:
            continue
        served = surfaces[cfg["model"]]
        for act in cfg["actions"]:
            assert act["m"] in served, "%s offers %s, not served" % (sid, act["m"])


def test_every_list_column_exists_on_its_model(m57):
    """A column the model lacks is dropped silently by the endpoint."""
    classes = _model_classes()
    for sid, cfg in m57["screens"].items():
        if cfg["kind"] != "model_list" or cfg["model"] not in classes:
            continue
        known = classes[cfg["model"]][0] | {"name", "state", "approval_state", "display_name"}
        unknown = [c for c in cfg["cols"] if c not in known]
        assert not unknown, "%s lists %s, not fields of %s" % (sid, unknown, cfg["model"])


def test_every_form_field_exists_on_its_model(m57):
    classes = _model_classes()
    for sid, cfg in m57["screens"].items():
        if cfg["kind"] != "model_form" or cfg["model"] not in classes:
            continue
        known = classes[cfg["model"]][0] | {"name", "state", "active", "approval_state"}
        unknown = [f["name"] for f in cfg["fields"] if f["name"] not in known]
        assert not unknown, "%s shows %s, not fields of %s" % (sid, unknown, cfg["model"])


@pytest.mark.parametrize("model", NEW_MODELS)
def test_new_registers_are_served_and_whitelisted(m57, model):
    assert model in _surfaces()
    forms = [
        c for c in m57["screens"].values() if c["kind"] == "model_form" and c["model"] == model
    ]
    assert forms, "%s has no workspace form" % model
    typed = {f["name"] for c in forms for f in c["fields"] if not f["readonly"]}
    typed |= {c["lines"] for c in forms if c["lines"]}
    assert _writable()[model] == typed


@pytest.mark.parametrize("model", sorted(NEVER_TYPED))
def test_stamps_and_measured_figures_are_never_typed(model):
    leaked = _writable().get(model, set()) & NEVER_TYPED[model]
    assert not leaked, (model, sorted(leaked))


def test_new_forms_are_tabbed(m57):
    """AGENTS.md: forms are split into Dynamics-style tabs."""
    for model in NEW_MODELS:
        forms = [
            c for c in m57["screens"].values() if c["kind"] == "model_form" and c["model"] == model
        ]
        assert all(c["tabs"] >= 2 for c in forms), model


def test_decisions_ask_for_their_reason_or_answer(m57):
    for sid, method, kwarg in (
        ("M57-kpi-defs", "action_reject", "reason"),
        ("M57-feedback", "action_submit_feedback", "feedback"),
        ("M57-feedback", "action_decline", "reason"),
    ):
        acts = {a["m"]: a for a in m57["screens"][sid]["actions"]}
        assert acts[method]["kwargs"] == [kwarg], sid


def test_new_models_are_secured():
    acl = (PERF / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    rules = (PERF / "security" / "fix_isolation_rules.xml").read_text(encoding="utf-8")
    privacy = (PERF / "security" / "fix_a09_privacy_rules.xml").read_text(encoding="utf-8")
    for model in (*NEW_MODELS, "fix.performance.calibration.line"):
        xmlid = "model_" + model.replace(".", "_")
        rows = [r.split(",") for r in acl.splitlines() if (",%s," % xmlid) in r]
        assert rows, model
        assert 'ref="%s"' % xmlid in rules, "%s has no company rule" % model
    for model in ("fix_performance_feedback", "fix_incentive_adjustment"):
        assert 'ref="model_%s"' % model in privacy, "%s has no privacy rule" % model
    # nobody deletes an adjustment (evidence); no plain user writes pay records
    for model in ("fix_incentive_adjustment",):
        rows = [r.split(",") for r in acl.splitlines() if ",model_%s," % model in r]
        assert all(r[-1].strip() == "0" for r in rows), "%s: nobody deletes" % model
    for r in (r.split(",") for r in acl.splitlines()):
        if (
            len(r) > 7
            and r[3] == "base.group_user"
            and r[2].endswith(("adjustment", "feedback", "kpi_definition"))
        ):
            assert r[5:8] == ["0", "0", "0"], r


def test_the_new_file_loads_after_the_models_it_extends():
    init = (PERF / "models" / "__init__.py").read_text(encoding="utf-8")
    body = init[init.index("from . import (") :]
    assert body.rstrip().endswith("fix_m57_capture,\n)") or body.rstrip().endswith(
        "fix_m57_capture,\n)".rstrip()
    ), body
    assert body.index("fix_m57_capture") > body.index("fix_compensation_proposal")
    assert "ruff: noqa: I001" in init
