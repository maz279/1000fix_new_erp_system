# M23 Quality Management (ISO): every sub-module page captures each record
# it covers (capture audit 2026-11-19).
#
# Before (HEAD a6ca660a), evaluated with the engine's own fregCreate/fregPanels:
#   * page 1 (Policy & Objectives) offered no chip: objectives could not be
#     cascaded to a branch, process or role (FR-QMS-002);
#   * page 2 (Process Register) offered no chip, the process form hid the
#     outputs and KPI the model holds, and no change could be assessed for
#     its QMS impact before release (FR-QMS-010, BRU-QMS-10);
#   * page 3 (Checklists & Gates) had no gate chip, and a checklist template
#     had no items at all - only a typed count (FR-QMS-011, BRU-QMS-03);
#   * page 5 (RCA & CAPA): the "RCA" list was the NCR list with a typed
#     root cause - no 5-Why / Ishikawa / 8D record (FR-QMS-026/027,
#     BRU-QMS-04/14) - and a CAPA had no action plan (FR-QMS-033);
#   * page 6 (Audit Programme): "+ New Audit Finding" opened an internal
#     AUDIT; findings could not be recorded at all (FR-QMS-043), nor the
#     annual programme, the auditor register or an evidence release
#     (FR-QMS-040/041/046), and the certification form had no chip;
#   * page 8 (Statistics & CoPQ): "+ New Qms Copq", a triage placeholder,
#     and a CoPQ entry named no non-conformance or cause (FR-QMS-029/030).
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
CONTROLLER = HERE.parent / "controllers" / "a10" / "m23.py"
WRITABLE_FILE = HERE.parent / "controllers" / "a10" / "writable.py"
QMS = HERE.parents[2] / "domain" / "i_governance" / "cd_qms_process"

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
const mod = P03_MODULES.M23;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M23', map);
  const panels = fregPanels('M23', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M23:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M23.screen : null));
  const label = create ? (create.label || null) : null;
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: own || null, label, forms };
});
const screen = (c) => ({
    kind: c.kind, model: c.model || null, create: c.create, title: c.title || null,
    tabs: (c.tabs || []).map((t) => t.id),
    sectionTabs: (c.sections || []).map((s) => s.tab || null),
    lines: c.lines ? c.lines.field : null,
    grids: (c.grids || []).map((g) => g.field),
    actions: (c.actions || []).map((a) => a.m),
    cols: c.cols || [],
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({
      name: f.name, readonly: !!f.readonly, required: !!f.required })),
    lineFields: c.lines ? c.lines.fields.map((f) => f.name) : [] });
console.log(JSON.stringify({ subs, forms: mod.forms,
  labelled: mod.groups.flatMap((g) => g.screens.map((x) => ({ id: x.id, en: x.en, bn: x.bn }))),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => id.startsWith('M23-')).map(([id, c]) => [id, screen(c)])) }));
"""


@pytest.fixture(scope="module")
def m23(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m23_capture")
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
    """{model: ({fields}, {methods})} defined or extended in cd_qms_process."""
    out = {}
    for path in (QMS / "models").glob("*.py"):
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
    # mixins the models inherit
    for name in out:
        out[name][0].update({"id", "display_name", "create_date", "write_date"})
    return out


# What each page lets a person capture: its own "+ New" first, then every
# other record the page covers, by form screen.
CAPTURES = {
    "1": ["M23-form-policy", "M23-form-objective"],
    "2": ["M23-form-process", "M23-form-change"],
    "3": ["M23-form-checklist", "M23-form-gate"],
    "4": ["M23-form-ncr"],
    "5": ["M23-form-capa", "M23-form-rca"],
    "6": [
        "M23-form-audit",
        "M23-form-finding",
        "M23-form-programme",
        "M23-form-auditor",
        "M23-form-certification",
        "M23-form-evidence",
    ],
    "7": ["M23-form-review", "M23-form-review-action"],
    "8": ["M23-form-qms-copq"],
}

NEW_MODELS = (
    "fix.qms.objective",
    "fix.qms.change.assessment",
    "fix.qms.checklist.item",
    "fix.qms.rca",
    "fix.capa.action",
    "fix.qms.audit.programme",
    "fix.qms.auditor",
    "fix.qms.audit.finding",
    "fix.qms.evidence.release",
)

# What a form must never let a person type: the state, every decision stamp
# and every derived figure.
NEVER_TYPED = {
    "fix.ncr": {"state", "disposition", "root_cause", "containment_done_on", "finding_id"},
    "fix.capa": {"state", "effectiveness_result", "implemented_by_id", "verification_due_on"},
    "fix.qms.checklist": {"state", "item_count", "previous_version_id"},
    "fix.qms.change.assessment": {
        "name",
        "state",
        "assessed_by_id",
        "released_by_id",
        "released_on",
    },
    "fix.qms.rca": {"name", "state", "completed_by_id", "completed_on"},
    "fix.capa.action": {"state", "done_on", "done_by_id", "evidence_note"},
    "fix.qms.audit.programme": {"state", "approved_by_id", "approved_on", "planned_count"},
    "fix.internal.audit": {"name", "state", "auditee_acknowledged_on"},
    "fix.qms.audit.finding": {"name", "state", "ncr_id", "closed_on"},
    "fix.qms.evidence.release": {"name", "state", "approved_by_id", "released_on"},
    "fix.qms.objective": {"attainment"},
}


def _sub(m23, no):
    return next(s for s in m23["subs"] if s["no"] == no)


def test_every_page_is_classified(m23):
    assert sorted(s["no"] for s in m23["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m23, no):
    sub = _sub(m23, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]} | {sub["create"]}
    missing = [form for form in [own, *others] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)


def test_the_audit_page_button_says_what_it_captures(m23):
    """'+ New Audit Finding' opened an internal audit; the chip of that name
    opened the same audit form."""
    sub = _sub(m23, "6")
    assert sub["label"] == "Internal Audit"
    finding = next(f for f in sub["forms"] if f["f"] == "Audit Finding")
    assert finding["model"] == "fix.qms.audit.finding"
    assert m23["screens"]["M23-form-audit"]["title"] == "Internal Audit"


def test_no_placeholder_wording_left(m23):
    assert _sub(m23, "8")["label"] == "CoPQ Entry"
    for screen in m23["labelled"]:
        assert "Qms Copq" not in (screen["en"], screen["bn"]), screen
    for sid, cfg in m23["screens"].items():
        assert (cfg["title"] or "") != "Qms Copq", sid


def test_each_captured_record_is_listed_on_its_page(m23):
    for sub in m23["subs"]:
        listed = {m23["screens"][s]["model"] for s in sub["screens"] if s in m23["screens"]}
        listed.add(sub["model"])
        captures = list(sub["forms"])
        if sub["create"]:
            captures.append({"model": m23["screens"][sub["create"]]["model"]})
        for f in captures:
            assert f["model"] in listed, "page %s captures %s but lists none" % (
                sub["no"],
                f["model"],
            )


def test_every_creatable_list_on_a_page_has_its_capture(m23):
    for sub in m23["subs"]:
        captured = {f["model"] for f in sub["forms"] if f["opens"]}
        if sub["create"]:
            captured.add(m23["screens"][sub["create"]]["model"])
        for sid in sub["screens"]:
            cfg = m23["screens"].get(sid)
            if not cfg or cfg["kind"] != "model_list" or cfg.get("create") is False:
                continue
            if cfg["model"] == "fix.capa.action":
                continue  # planned on the CAPA form's Action Plan grid
            if cfg["model"] == "fix.qms.review.input":
                continue  # pulled, never typed
            assert cfg["model"] in captured, "page %s lists %s with no capture" % (
                sub["no"],
                cfg["model"],
            )


def test_the_rca_list_is_the_analysis_not_the_ncr(m23):
    assert m23["screens"]["M23-rca"]["model"] == "fix.qms.rca"
    assert "action_complete" in m23["screens"]["M23-rca"]["actions"]


def test_the_typed_root_cause_left_the_workspace(m23):
    assert "action_set_root_cause" not in m23["screens"]["M23-ncr"]["actions"]
    assert "action_set_root_cause" not in _surfaces()["fix.ncr"]
    assert "root_cause" not in _writable()["fix.ncr"]


def test_the_templates_and_capas_show_their_children(m23):
    assert m23["screens"]["M23-form-checklist"]["lines"] == "item_ids"
    assert m23["screens"]["M23-form-capa"]["lines"] == "action_ids"
    assert "finding_ids" in m23["screens"]["M23-form-audit"]["grids"]
    # findings are recorded on their own form while the audit is executed
    assert "finding_ids" not in _writable()["fix.internal.audit"]


def test_every_form_field_column_and_line_exists_on_its_model(m23):
    models = _model_classes()
    for sid, cfg in m23["screens"].items():
        model = cfg["model"]
        if not model or model not in models:
            continue
        flds = models[model][0]
        names = [f["name"] for f in cfg["fields"]] + cfg["cols"]
        missing = [
            n
            for n in names
            if n not in flds and n not in ("company_id", "currency_id", "name", "approval_state")
        ]
        assert not missing, "%s names %s missing on %s" % (sid, missing, model)
        if cfg["lines"]:
            child = {
                "item_ids": "fix.qms.checklist.item",
                "action_ids": "fix.capa.action",
            }[cfg["lines"]]
            gone = [n for n in cfg["lineFields"] if n not in models[child][0]]
            assert not gone, "%s grid names %s missing on %s" % (sid, gone, child)


def test_every_section_tab_is_declared(m23):
    for sid, cfg in m23["screens"].items():
        for tab in cfg["sectionTabs"]:
            if tab:
                assert tab in cfg["tabs"], "%s section names undeclared tab %s" % (sid, tab)


def test_every_list_action_is_served_and_exists(m23):
    surfaces = _surfaces()
    models = _model_classes()
    for sid, cfg in m23["screens"].items():
        if cfg["kind"] != "model_list":
            continue
        for action in cfg["actions"]:
            assert action in surfaces.get(cfg["model"], set()), (sid, action)
            assert action in models[cfg["model"]][1], (sid, action)


def test_every_new_model_is_served_and_writable_only_where_a_form_offers(m23):
    surfaces = _surfaces()
    writable = _writable()
    for model in NEW_MODELS:
        assert model in surfaces, model
        assert model in writable, model


@pytest.mark.parametrize("model", sorted(NEVER_TYPED))
def test_no_form_lets_a_decision_be_typed(m23, model):
    typed = set()
    for cfg in m23["screens"].values():
        if cfg["model"] == model and cfg["kind"] == "model_form":
            typed |= {f["name"] for f in cfg["fields"] if not f["readonly"]}
    assert not typed & NEVER_TYPED[model], sorted(typed & NEVER_TYPED[model])
    assert not writable_overlap(model), model


def writable_overlap(model):
    return _writable().get(model, set()) & NEVER_TYPED[model]


def test_the_new_models_have_access_and_isolation():
    acl = (QMS / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    rules = (QMS / "security" / "fix_isolation_rules.xml").read_text(encoding="utf-8")
    for model in NEW_MODELS:
        xml_id = "model_" + model.replace(".", "_")
        assert "," + xml_id + "," in acl, model
        assert 'ref="%s"' % xml_id in rules, model
