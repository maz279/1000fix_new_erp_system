# M64 Master Data Management: every sub-module page captures each record it
# covers (capture audit 2026-11-18).
#
# Before (HEAD 00326139), evaluated with the engine's own fregCreate/fregPanels:
#   * page 1 (Stewardship) listed the domain register (fix.mdm.stewardship)
#     with no chip, so no domain could be set up from the page; the register
#     had no deputy steward, technical custodian or criticality (FR-MDM-001/004);
#   * page 2 (Data Quality) captured rules only: the evaluator counted failures
#     and no remediation worklist existed anywhere (FR-MDM-021 P0);
#   * page 3 (Code Lists) listed cross-references with no chip (FR-MDM-032);
#   * page 4 (Golden Records) had NO chip at all: match rules and governed
#     attributes were listed, uncapturable, and no governed hierarchy existed
#     (FR-MDM-028/029, BRU-MDM-18);
#   * page 5 (Workflows) offered single change requests only: no bulk change
#     set (FR-MDM-013 P0, BRU-MDM-08);
#   * no page held business parameters at all (FR-MDM-033 P0, BRU-MDM-16/17).
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
CONTROLLER = HERE.parent / "controllers" / "a12" / "m64.py"
ADDONS = HERE.parents[2]
MODEL_DIRS = (
    ADDONS / "platform" / "cd_mdm_core" / "models",
    ADDONS / "platform" / "cd_entity_config" / "models",
)

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
const mod = P03_MODULES.M64;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M64', map);
  const panels = fregPanels('M64', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M64:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M64.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: own || null, forms,
    reports: panels.reports.map((r) => ({ r, route: P03_REPORT_ROUTES['M64:' + r] || null })) };
});
const screen = (c) => ({
    kind: c.kind, model: c.model || null, create: c.create,
    lines: c.lines ? { field: c.lines.field, fields: c.lines.fields.map((f) => ({ name: f.name, readonly: !!f.readonly })) } : null,
    actions: (c.actions || []).map((a) => ({ m: a.m, kwargs: (a.asks || []).map((q) => q.kwarg).concat(a.kwarg ? [a.kwarg] : []) })),
    cols: c.cols || [],
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({
      name: f.name, readonly: !!f.readonly, required: !!f.required })) });
console.log(JSON.stringify({ subs, forms: mod.forms,
  labelled: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => id.startsWith('M64-')).map(([id, c]) => [id, screen(c)])) }));
"""


@pytest.fixture(scope="module")
def m64(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m64_capture")
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
    value = _assigned(CONTROLLER, "WRITABLE")
    return {
        ast.literal_eval(k): set(ast.literal_eval(v))
        for k, v in zip(value.keys, value.values, strict=True)
    }


def _model_classes():
    """{model: ({fields}, {methods})} defined or extended in the MDM modules."""
    out = {}
    for folder in MODEL_DIRS:
        for path in folder.glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for cls in (n for n in tree.body if isinstance(n, ast.ClassDef)):
                names, flds = set(), set()
                for stmt in cls.body:
                    if not (isinstance(stmt, ast.Assign) and isinstance(stmt.targets[0], ast.Name)):
                        continue
                    target = stmt.targets[0].id
                    if (target == "_name" and isinstance(stmt.value, ast.Constant)) or (
                        target == "_inherit"
                        and isinstance(stmt.value, ast.Constant)
                        and not any(
                            isinstance(s, ast.Assign) and getattr(s.targets[0], "id", "") == "_name"
                            for s in cls.body
                        )
                    ):
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
    "1": ["M64-form-steward", "M64-form-mdm-stewardship"],
    "2": ["M64-form-dq", "M64-form-remediation"],
    "3": ["M64-form-list", "M64-form-entry", "M64-form-xref"],
    "4": [
        "M64-form-goldenrule",
        "M64-form-matchrule",
        "M64-form-governed",
        "M64-form-hierarchy",
    ],
    "5": ["M64-form-mdm-change-request", "M64-form-bulk"],
    "6": ["M64-form-dup"],
    "7": ["M64-form-parameter", "M64-form-param-change"],
}

NEW_MODELS = (
    "fix.mdm.dq.remediation",
    "fix.mdm.business.parameter",
    "fix.mdm.parameter.change",
    "fix.mdm.hierarchy",
    "fix.mdm.hierarchy.node",
    "fix.mdm.change.batch",
    "fix.mdm.change.batch.line",
)

# What a form must never let a person type: the state, decision stamps and
# measured values. Each changes only through its workflow action.
NEVER_TYPED = {
    "fix.mdm.dq.remediation": {
        "state",
        "resolution",
        "record_name",
        "raised_by_id",
        "resolved_by_id",
        "resolved_at",
    },
    "fix.mdm.business.parameter": {
        "state",
        "activated_on",
        "activated_by_id",
        "version",
        "current_value",
    },
    "fix.mdm.parameter.change": {
        "state",
        "previous_value",
        "submitted_by_id",
        "decided_by_id",
        "published_at",
        "decision_note",
        "approval_state",
    },
    "fix.mdm.hierarchy": {"state", "version", "published_by_id", "published_at"},
    "fix.mdm.change.batch": {
        "state",
        "name",
        "preview",
        "submitted_by_id",
        "reviewed_by_id",
        "applied_by_id",
        "applied_at",
        "approval_state",
    },
}


def test_every_page_offers_a_capture(m64):
    for sub in m64["subs"]:
        assert sub["create"] or any(f["opens"] for f in sub["forms"]), (
            "page %s %s captures nothing" % (sub["no"], sub["title"])
        )


@pytest.mark.parametrize("no", sorted(CAPTURES))
def test_each_page_captures_what_it_covers(m64, no):
    sub = next(s for s in m64["subs"] if s["no"] == no)
    offered = [sub["create"]] + [f["id"] for f in sub["forms"] if f["opens"]]
    want = CAPTURES[no]
    assert sub["create"] == want[0], "page %s + New is %s" % (no, sub["create"])
    missing = [screen for screen in want if screen not in offered]
    assert not missing, "page %s %s cannot capture %s" % (no, sub["title"], missing)


def test_a_page_captures_only_its_own_records(m64):
    """A chip opens a form whose model the page lists (no foreign capture)."""
    for sub in m64["subs"]:
        listed = {sub["model"]} | {
            m64["screens"][sid]["model"] for sid in sub["screens"] if sid in m64["screens"]
        }
        for form in sub["forms"]:
            assert form["model"] in listed, (
                "page %s chip %s opens %s, which the page does not list"
                % (sub["no"], form["f"], form["model"])
            )


def test_every_listed_record_has_a_capture_on_its_page(m64):
    """Each model a page lists as a register has a form on that page."""
    for sub in m64["subs"]:
        captured = {sub["model"]} | {f["model"] for f in sub["forms"] if f["opens"]}
        for sid in sub["screens"]:
            cfg = m64["screens"].get(sid)
            if not cfg or cfg["kind"] != "model_list":
                continue
            if cfg["model"] == "fix.mdm.duplicate":
                continue  # the page's own + New
            assert cfg["model"] in captured, "page %s lists %s and cannot capture it" % (
                sub["no"],
                cfg["model"],
            )


def test_every_new_list_and_form_is_labelled_on_the_module(m64):
    for sid in (
        "M64-remediation",
        "M64-hierarchies",
        "M64-bulk",
        "M64-parameters",
        "M64-param-changes",
    ):
        assert sid in m64["labelled"], "%s is on no module group" % sid


def test_the_new_records_exist():
    classes = _model_classes()
    missing = [m for m in NEW_MODELS if m not in classes]
    assert not missing, "no model defines %s" % missing


def test_every_surface_action_is_a_method():
    classes = _model_classes()
    for model, actions in _surfaces().items():
        methods = classes.get(model, (set(), set()))[1]
        if model in (
            "fix.mdm.steward",
            "fix.mdm.change.request",
            "fix.mdm.parameter.change",
            "fix.mdm.change.batch",
        ):
            # request/recall approval come from fix.approvable.mixin (M63)
            methods = methods | {"action_request_approval", "action_recall_approval"}
        missing = sorted(actions - methods)
        assert not missing, "%s serves %s but defines no such method" % (model, missing)


def test_every_list_button_is_served(m64):
    surfaces = _surfaces()
    for sid, cfg in m64["screens"].items():
        for act in cfg["actions"]:
            assert act["m"] in surfaces.get(cfg["model"], set()), (
                "%s offers %s, which the server refuses" % (sid, act["m"])
            )


def test_form_fields_are_writable_and_never_typed_fields_are_not(m64):
    writable = _writable()
    for sid, cfg in m64["screens"].items():
        if cfg["kind"] != "model_form" or cfg["model"] not in NEVER_TYPED:
            continue
        allowed = writable[cfg["model"]]
        for field in cfg["fields"]:
            if field["readonly"]:
                continue
            assert field["name"] in allowed, "%s offers %s but the server refuses it" % (
                sid,
                field["name"],
            )
        assert not (allowed & NEVER_TYPED[cfg["model"]]), "%s lets the form type %s" % (
            cfg["model"],
            allowed & NEVER_TYPED[cfg["model"]],
        )
        for field in cfg["fields"]:
            if field["name"] in NEVER_TYPED[cfg["model"]]:
                assert field["readonly"], "%s shows %s as an input" % (sid, field["name"])


def test_child_grids_are_writable_and_measured_cells_read_only(m64):
    writable = _writable()
    for sid, field, measured in (
        ("M64-form-hierarchy", "node_ids", {"level"}),
        ("M64-form-bulk", "line_ids", {"target_name", "current_values"}),
    ):
        cfg = m64["screens"][sid]
        assert cfg["lines"] and cfg["lines"]["field"] == field
        assert field in writable[cfg["model"]]
        cells = {c["name"]: c["readonly"] for c in cfg["lines"]["fields"]}
        for name in measured:
            assert cells.get(name) is True, "%s grid lets a person type %s" % (sid, name)


def test_the_domain_register_records_a_deputy_and_custodian(m64):
    names = {f["name"] for f in m64["screens"]["M64-form-mdm-stewardship"]["fields"]}
    assert {"deputy_steward_id", "technical_custodian_id", "criticality"} <= names
    assert {"deputy_steward_id", "technical_custodian_id", "criticality"} <= _writable()[
        "fix.mdm.stewardship"
    ]


def test_the_rule_list_raises_the_worklist(m64):
    acts = {a["m"] for a in m64["screens"]["M64-rules"]["actions"]}
    assert "action_raise_worklist" in acts


def test_a_closing_decision_asks_for_its_reason(m64):
    acts = {a["m"]: a["kwargs"] for a in m64["screens"]["M64-remediation"]["actions"]}
    assert acts["action_waive"] == ["note"]
    assert acts["action_resolve"] == ["note"]
