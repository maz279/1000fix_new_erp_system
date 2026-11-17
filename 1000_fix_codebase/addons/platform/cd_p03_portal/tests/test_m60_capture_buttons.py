# M60 Governance, Risk & Compliance: every sub-module page captures each
# record it covers (capture audit 2026-11-18).
#
# Before (HEAD 32e24dc9), evaluated with the engine's own fregCreate/fregPanels:
#   * page 1 (Risk Register) captured the risk and the appetite only: no
#     dated assessment (FR-GRC-003/005, BRU-GRC-03 - a rescore overwrote the
#     last one), no treatment action with an owner and a date (FR-GRC-004),
#     no realised risk event (FR-GRC-007);
#   * page 2 (Control Framework & Testing) had no "Internal Control" chip and
#     the control had no objective, nature or key-control flag
#     (FR-GRC-011/012);
#   * page 3 (SoD & Authority) offered NO form chip: SoD tests (FR-GRC-019)
#     and time-boxed exceptions (FR-GRC-020) were capturable only in M29, and
#     the M60 rule named no control that enforces it;
#   * page 4 (Compliance Obligations) had no occurrence to discharge with
#     evidence (FR-GRC-024/025, BRU-GRC-12/13), no regulatory change
#     (FR-GRC-026), no framework chip, and the obligation had no owner;
#   * page 5 (Policy Governance) recorded no acknowledgement (FR-GRC-030: the
#     Attestation Status report said so itself), no exception (FR-GRC-031),
#     and no retention policy chip (FR-GRC-032);
#   * page 6 (Legal & IP) offered NO form chip: no legal hold (FR-GRC-039),
#     no IP register (FR-GRC-028);
#   * page 7 (PDPA Governance) offered NO form chip: no record of processing
#     (FR-GRC-033), cross-border transfer (FR-GRC-034), breach register
#     (FR-GRC-036) or privacy impact assessment (FR-GRC-037); its one form,
#     "PDPA Register Entry", described a processing record but captured a
#     data-subject request.
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
CONTROLLER = HERE.parent / "controllers" / "a10" / "m60.py"
WRITABLE_FILE = HERE.parent / "controllers" / "a10" / "writable.py"
GRC = HERE.parents[2] / "domain" / "i_governance" / "cd_grc"
# The asset/HSE bridge adds the "Reported by the Source Modules" fields to the
# risk; the field scan reads it too.
BRIDGE = HERE.parents[2] / "domain" / "f_asset_facilities" / "cd_asset_finance_hse_bridge"

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
const mod = P03_MODULES.M60;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M60', map);
  const panels = fregPanels('M60', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M60:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M60.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: own || null, forms,
    reports: panels.reports.map((r) => ({ r, route: P03_REPORT_ROUTES['M60:' + r] || null })) };
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
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => id.startsWith('M60-') || Object.entries(P03_FORM_CHIPS).some(([k, v]) => k.startsWith('M60:') && (v === id || (typeof v === 'object' && Object.values(v).includes(id))))).map(([id, c]) => [id, screen(c)])) }));
"""


@pytest.fixture(scope="module")
def m60(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m60_capture")
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
    """{model: ({fields}, {methods})} defined or extended in cd_grc."""
    out = {}
    for path in [*(GRC / "models").glob("*.py"), *(BRIDGE / "models").glob("*.py")]:
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
# other record the page covers, by form screen. M29's SoD test and exception
# and M24's legal hold and retention policy are reused, not duplicated.
CAPTURES = {
    "1": [
        "M60-form-risk",
        "M60-form-appetite",
        "M60-form-assessment",
        "M60-form-treatment",
        "M60-form-event",
    ],
    "2": ["M60-form-control", "M60-form-test"],
    "3": ["M60-form-sod", "M29-form-sodtest", "M29-form-sodexception"],
    "4": [
        "M60-form-obligation",
        "M60-form-compliance-framework",
        "M60-form-occurrence",
        "M60-form-licence",
        "M60-form-regchange",
    ],
    "5": [
        "M60-form-policy",
        "M60-form-attestation",
        "M60-form-policy-exception",
        "M24-form-retention",
    ],
    "6": ["M60-form-legal", "M24-form-hold", "M60-form-ip"],
    "7": [
        "M60-form-pdpa",
        "M60-form-ropa",
        "M60-form-transfer",
        "M60-form-breach",
        "M60-form-pia",
    ],
    "8": ["M60-form-whistle"],
}

NEW_MODELS = (
    "fix.risk.assessment",
    "fix.risk.treatment",
    "fix.risk.event",
    "fix.compliance.obligation.occurrence",
    "fix.grc.regulatory.change",
    "fix.grc.policy.attestation",
    "fix.grc.policy.exception",
    "fix.grc.ip.asset",
    "fix.grc.processing.activity",
    "fix.grc.data.transfer",
    "fix.grc.data.breach",
    "fix.grc.privacy.impact",
)

# What a form must never let a person type: the state, every decision stamp
# and every derived figure.
NEVER_TYPED = {
    "fix.risk.assessment": {
        "assessed_on",
        "assessed_by_id",
        "inherent_score",
        "residual_score",
        "previous_residual",
        "controls_relied_on",
    },
    "fix.risk.treatment": {"state", "completion_note", "completed_on", "completed_by_id"},
    "fix.risk.event": {"reported_by_id", "reassessment_due"},
    "fix.compliance.obligation.occurrence": {
        "state",
        "discharged_on",
        "discharged_by_id",
        "verified_by_id",
        "verified_on",
        "decision_note",
        "owner_id",
    },
    "fix.grc.regulatory.change": {"state", "impact_assessment", "assessed_by_id"},
    "fix.grc.policy.attestation": {"version", "employee_id", "acknowledged_at", "recorded_by_id"},
    "fix.grc.policy.exception": {
        "state",
        "requested_by_id",
        "decided_by_id",
        "decided_on",
        "decision_note",
    },
    "fix.grc.processing.activity": {"state", "activated_by_id", "activated_on"},
    "fix.grc.data.transfer": {"state", "requested_by_id", "approved_by_id"},
    "fix.grc.data.breach": {"state", "reported_by_id", "closed_by_id", "closed_on"},
    "fix.grc.privacy.impact": {"state", "author_id", "approved_by_id", "approved_on"},
    "fix.grc.pdpa": {"name", "outcome", "due_on"},
    "fix.grc.sod.rule": {"state", "waived_by_id", "waived_on", "last_test_result"},
    "fix.grc.policy": {"state", "approved_on", "attested_count"},
    "fix.control": {"state", "last_tested", "test_result"},
}


def _sub(m60, no):
    return next(s for s in m60["subs"] if s["no"] == no)


def test_every_page_is_classified(m60):
    assert sorted(s["no"] for s in m60["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m60, no):
    sub = _sub(m60, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]} | {sub["create"]}
    missing = [form for form in [own, *others] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)


@pytest.mark.parametrize("no", ("3", "6", "7"))
def test_the_pages_that_had_no_chip_now_have_them(m60, no):
    assert len(_sub(m60, no)["forms"]) >= 3


def test_the_pdpa_form_says_what_it_captures(m60):
    form = m60["screens"]["M60-form-pdpa"]
    assert form["model"] == "fix.grc.pdpa"
    chip = next(f for f in _sub(m60, "7")["forms"] if f["id"] == "M60-form-pdpa")
    assert chip["f"] == "Data Subject Request"
    assert "PDPA Register Entry" not in m60["forms"]
    # the reference is numbered on save; the outcome and deadline are decided
    typed = {f["name"] for f in form["fields"] if not f["readonly"]}
    assert not typed & {"name", "outcome", "due_on"}, sorted(typed)


def test_each_captured_record_is_listed_on_its_page(m60):
    for sub in m60["subs"]:
        listed = {m60["screens"][s]["model"] for s in sub["screens"] if s in m60["screens"]}
        listed.add(sub["model"])
        captures = list(sub["forms"])
        if sub["create"]:
            captures.append({"model": m60["screens"][sub["create"]]["model"]})
        for f in captures:
            if f["model"] == "fix.document":
                continue  # a legal hold is placed on a document; the page lists the holds
            assert f["model"] in listed, "page %s captures %s but lists none" % (
                sub["no"],
                f["model"],
            )


def test_every_creatable_list_on_a_page_has_its_capture(m60):
    for sub in m60["subs"]:
        captured = {f["model"] for f in sub["forms"] if f["opens"]}
        if sub["create"]:
            captured.add(m60["screens"][sub["create"]]["model"])
        for sid in sub["screens"]:
            cfg = m60["screens"].get(sid, {})
            if cfg.get("kind") == "model_list" and cfg.get("create") is not False:
                assert cfg["model"] in captured, "page %s lists %s (%s) with no capture" % (
                    sub["no"],
                    cfg["model"],
                    sid,
                )


def test_every_working_screen_sits_on_a_page(m60):
    placed = {sid for s in m60["subs"] for sid in s["screens"]}
    placed |= {r["route"] for s in m60["subs"] for r in s["reports"]}
    orphans = [
        sid
        for sid, cfg in m60["screens"].items()
        if sid.startswith("M60-")
        and cfg["kind"] in ("model_list", "table_report")
        and sid not in placed
    ]
    assert not orphans, orphans


def test_every_screen_on_a_page_has_a_navigation_label(m60):
    labelled = set(m60["labelled"])
    unlabelled = sorted(
        sid
        for sub in m60["subs"]
        for sid in sub["screens"]
        if sid in m60["screens"] and sid not in labelled
    )
    assert not unlabelled, unlabelled


def test_every_served_action_exists_on_its_model():
    classes = _model_classes()
    generic = {"action_request_approval", "action_recall_approval"}  # the M63 mixin's verbs
    for model, acts in _surfaces().items():
        methods = classes.get(model, (set(), set()))[1]
        missing = acts - methods - generic
        assert not missing, "%s serves %s, which the model lacks" % (model, sorted(missing))


def test_every_list_action_is_served(m60):
    surfaces = _surfaces()
    for sid, cfg in m60["screens"].items():
        if cfg["kind"] != "model_list" or not cfg["actions"] or cfg["model"] not in surfaces:
            continue
        served = surfaces[cfg["model"]]
        for act in cfg["actions"]:
            assert act["m"] in served, "%s offers %s, not served" % (sid, act["m"])


def test_every_list_column_exists_on_its_model(m60):
    """A column the model lacks is dropped silently by the endpoint."""
    classes = _model_classes()
    for sid, cfg in m60["screens"].items():
        if cfg["kind"] != "model_list" or cfg["model"] not in classes:
            continue
        known = classes[cfg["model"]][0] | {"name", "state", "approval_state", "display_name"}
        unknown = [c for c in cfg["cols"] if c not in known]
        assert not unknown, "%s lists %s, not fields of %s" % (sid, unknown, cfg["model"])


def test_every_form_field_exists_on_its_model(m60):
    classes = _model_classes()
    for sid, cfg in m60["screens"].items():
        if cfg["kind"] != "model_form" or cfg["model"] not in classes:
            continue
        known = classes[cfg["model"]][0] | {"name", "state", "active", "approval_state"}
        unknown = [f["name"] for f in cfg["fields"] if f["name"] not in known]
        assert not unknown, "%s shows %s, not fields of %s" % (sid, unknown, cfg["model"])


@pytest.mark.parametrize("model", NEW_MODELS)
def test_new_registers_are_served_and_whitelisted(m60, model):
    assert model in _surfaces()
    forms = [
        c for c in m60["screens"].values() if c["kind"] == "model_form" and c["model"] == model
    ]
    assert forms, "%s has no workspace form" % model
    typed = {f["name"] for c in forms for f in c["fields"] if not f["readonly"]}
    assert _writable()[model] == typed


@pytest.mark.parametrize("model", sorted(NEVER_TYPED))
def test_stamps_and_derived_figures_are_never_typed(model):
    leaked = _writable().get(model, set()) & NEVER_TYPED[model]
    assert not leaked, (model, sorted(leaked))


def test_new_forms_are_tabbed(m60):
    """AGENTS.md: forms are split into Dynamics-style tabs."""
    for model in NEW_MODELS:
        forms = [
            c for c in m60["screens"].values() if c["kind"] == "model_form" and c["model"] == model
        ]
        assert all(c["tabs"] >= 2 for c in forms), model


def test_decisions_ask_for_their_reason(m60):
    for sid, method, kwarg in (
        ("M60-treatments", "action_complete", "note"),
        ("M60-treatments", "action_cancel", "reason"),
        ("M60-occurrences", "action_record_breach", "reason"),
        ("M60-occurrences", "action_not_applicable", "reason"),
        ("M60-reg-changes", "action_assess", "impact"),
        ("M60-policy-exceptions", "action_reject", "reason"),
        ("M60-transfers", "action_suspend", "reason"),
        ("M60-pias", "action_reject", "reason"),
    ):
        acts = {a["m"]: a for a in m60["screens"][sid]["actions"]}
        assert acts[method]["kwargs"] == [kwarg], sid


def test_new_models_are_secured():
    acl = (GRC / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    rules = (GRC / "security" / "fix_isolation_rules.xml").read_text(encoding="utf-8")
    for model in NEW_MODELS:
        xmlid = "model_" + model.replace(".", "_")
        rows = [r.split(",") for r in acl.splitlines() if (",%s," % xmlid) in r]
        assert rows, model
        assert all(r[-1].strip() == "0" for r in rows), "%s: nobody deletes" % model
        assert 'ref="%s"' % xmlid in rules, "%s has no company rule" % model
    # BRU-GRC-20: the breach register is T5 - no plain internal user row
    breach = [r for r in acl.splitlines() if ",model_fix_grc_data_breach," in r]
    assert breach and not any(",base.group_user," in r for r in breach)
    # registers kept by an officer: a plain user reads only
    for model in (
        "fix_grc_processing_activity",
        "fix_grc_data_transfer",
        "fix_grc_privacy_impact",
        "fix_grc_regulatory_change",
        "fix_risk_assessment",
    ):
        for r in (r.split(",") for r in acl.splitlines() if ",model_%s," % model in r):
            if r[3] == "base.group_user":
                assert r[5:8] == ["0", "0", "0"], r


def test_the_new_file_loads_after_the_models_it_extends():
    init = (GRC / "models" / "__init__.py").read_text(encoding="utf-8")
    assert init.rstrip().endswith("from . import fix_m60_capture")
    assert "ruff: noqa: I001" in init
