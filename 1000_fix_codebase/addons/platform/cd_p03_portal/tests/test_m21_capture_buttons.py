# M21 Core HR & Lifecycle: every sub-module page captures each record it
# covers (capture audit 2026-11-17).
#
# Before (HEAD 42d00bb2), evaluated with the engine's own fregCreate/fregPanels:
#   * page 7 (ESS / MSS) listed employees and captured nothing, and no
#     employment privacy-notice acknowledgement existed anywhere (FR-HCM-044
#     P0, BRU-HCM-12 H); employee rights requests (FR-HCM-045) were on no page;
#   * page 3 (Org Structure) captured positions only: the 23 departments and
#     61 job profiles every fix_real employee belongs to were on no screen
#     (FR-HCM-020/022), and a position named no job, department or freeze;
#   * page 8 (Exit Process) listed absence cases with no chip and had no exit
#     interview (FR-HCM-038): attrition could not be read by reason;
#   * page 4 listed master changes and disciplinary cases with no chip, and
#     its Promotion chip opened the dossier with "Transfer" selected;
#   * pages 1, 2, 5 and 6 listed education, experience, contracts, service
#     book entries and dependants with no chip.
#
# Evaluated as the browser evaluates it: node runs the engine's own fregCreate
# and fregPanels over the real registry fragments.
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
CONTROLLER = HERE.parent / "controllers" / "a09" / "m21.py"
WRITABLE_FILE = HERE.parent / "controllers" / "a09" / "writable.py"
HRCORE = HERE.parents[2] / "domain" / "h_people" / "cd_hr_core"

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
const mod = P03_MODULES.M21;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M21', map);
  const panels = fregPanels('M21', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M21:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M21.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: own || null, forms,
    reports: panels.reports.map((r) => ({ r, route: P03_REPORT_ROUTES['M21:' + r] || null })) };
});
const screen = (c) => ({
    kind: c.kind, model: c.model || null, create: c.create, report: c.report || null,
    tabs: (c.tabs || []).length, presets: c.presets || null, domain: c.domain || null,
    actions: (c.actions || []).map((a) => ({ m: a.m, kwargs: (a.asks || []).map((q) => q.kwarg).concat(a.kwarg ? [a.kwarg] : []) })),
    cols: c.cols || [],
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({
      name: f.name, readonly: !!f.readonly, required: !!f.required })) });
console.log(JSON.stringify({ subs, forms: mod.forms,
  labelled: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  foreign: Object.fromEntries(Object.values(P03_FORM_CHIPS).filter((id) => typeof id === 'string' && !id.startsWith('M21-') && P03_DATA_SCREENS[id]).map((id) => [id, screen(P03_DATA_SCREENS[id])])),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => id.startsWith('M21-')).map(([id, c]) => [id, screen(c)])) }));
"""


@pytest.fixture(scope="module")
def m21(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m21_capture")
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
    """{model: ({fields}, {methods})} defined or extended in cd_hr_core."""
    out = {}
    for path in (HRCORE / "models").glob("*.py"):
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
    "1": ["M21-employee", "M21-form-education", "M21-form-experience"],
    "2": ["M21-form-contract"],
    "3": ["M21-form-position", "M21-form-department", "M21-form-job"],
    "4": [
        "M21-form-transfer",
        "M21-form-promotion",
        "M21-form-master-change",
        "M21-form-disciplinary",
    ],
    "5": ["M21-form-document", "M21-form-servicebook"],
    "6": ["M21-form-dependant"],
    "7": ["M21-form-notice-ack", "M21-form-rights", "M21-form-master-change"],
    "8": ["M21-form-exit", "M21-form-exit-interview", "M21-form-abandonment"],
}

NEW_MODELS = ("fix.hr.notice.ack", "fix.hr.exit.interview")
# the Odoo models the Org Structure page now captures
STRUCTURE_MODELS = ("hr.department", "hr.job")

# What a form must never let a person type: the state and every stamp.
NEVER_TYPED = {
    "fix.hr.notice.ack": {
        "name",
        "state",
        "recorded_by_id",
        "withdrawn_on",
        "withdrawn_by_id",
        "withdrawal_reason",
        "purposes",
    },
    "fix.hr.exit.interview": {"name", "state", "recorded_on", "employee_id", "exit_type"},
    "hr.department": {"total_employee", "complete_name"},
    "hr.job": {"no_of_employee"},
}


def _sub(m21, no):
    return next(s for s in m21["subs"] if s["no"] == no)


def test_every_page_is_classified(m21):
    assert sorted(s["no"] for s in m21["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m21, no):
    sub = _sub(m21, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]} | {sub["create"]}
    missing = [form for form in [own, *others] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)


def test_the_self_service_page_captures_instead_of_listing_employees(m21):
    sub = _sub(m21, "7")
    assert sub["model"] == "fix.hr.notice.ack"
    assert sub["create"] == "M21-form-notice-ack"


def test_the_promotion_chip_starts_a_promotion(m21):
    form = m21["screens"]["M21-form-promotion"]
    assert form["model"] == "fix.hr.transfer"
    assert form["presets"] == {"movement_type": "promotion"}
    # the preset is posted: the field is on the form and typed, not read-only
    field = next(f for f in form["fields"] if f["name"] == "movement_type")
    assert not field["readonly"]
    assert "movement_type" in _writable()["fix.hr.transfer"]
    chip = next(f for f in _sub(m21, "4")["forms"] if f["f"] == "Promotion")
    assert chip["id"] == "M21-form-promotion"


def test_each_captured_record_is_listed_on_its_page(m21):
    for sub in m21["subs"]:
        listed = {m21["screens"][s]["model"] for s in sub["screens"] if s in m21["screens"]}
        listed.add(sub["model"])
        captures = list(sub["forms"])
        if sub["create"]:
            captures.append({"model": m21["screens"][sub["create"]]["model"]})
        for f in captures:
            assert f["model"] in listed, "page %s captures %s but lists none" % (
                sub["no"],
                f["model"],
            )


def test_every_creatable_list_on_a_page_has_its_capture(m21):
    for sub in m21["subs"]:
        captured = {f["model"] for f in sub["forms"] if f["opens"]}
        if sub["create"]:
            captured.add(m21["screens"][sub["create"]]["model"])
        for sid in sub["screens"]:
            cfg = m21["screens"].get(sid, {})
            if cfg.get("kind") == "model_list" and cfg.get("create") is not False:
                assert cfg["model"] in captured, "page %s lists %s (%s) with no capture" % (
                    sub["no"],
                    cfg["model"],
                    sid,
                )


def test_every_module_form_chip_opens_a_form(m21):
    """mod.forms is what the module page shows as chips: each opens a form."""
    pages = {f["f"]: f for s in m21["subs"] for f in s["forms"]}
    for name in m21["forms"]:
        assert name in pages, "form chip %s sits on no sub-module page" % name
        assert pages[name]["opens"], "form chip %s opens no form" % name


def test_every_screen_on_a_page_has_a_navigation_label(m21):
    labelled = set(m21["labelled"])
    unlabelled = sorted(
        sid
        for sub in m21["subs"]
        for sid in sub["screens"]
        if sid in m21["screens"] and sid not in labelled
    )
    assert not unlabelled, unlabelled


def test_every_served_action_exists_on_its_model():
    classes = _model_classes()
    for model, acts in _surfaces().items():
        if model not in NEW_MODELS:
            continue
        methods = classes.get(model, (set(), set()))[1]
        missing = acts - methods
        assert not missing, "%s serves %s, which the model lacks" % (model, sorted(missing))


def test_every_list_action_is_served(m21):
    surfaces = _surfaces()
    for sid, cfg in m21["screens"].items():
        if cfg["kind"] != "model_list" or not cfg["actions"] or cfg["model"] not in surfaces:
            continue
        served = surfaces[cfg["model"]]
        for act in cfg["actions"]:
            assert act["m"] in served, "%s offers %s, not served" % (sid, act["m"])


def test_the_new_lists_are_served_by_m21():
    surfaces = _surfaces()
    for model in NEW_MODELS + STRUCTURE_MODELS:
        assert model in surfaces, model


def test_every_form_field_exists_on_its_model(m21):
    classes = _model_classes()
    for sid, cfg in m21["screens"].items():
        if cfg["kind"] != "model_form" or cfg["model"] not in NEW_MODELS:
            continue
        known = classes[cfg["model"]][0] | {"name", "state", "active"}
        unknown = [f["name"] for f in cfg["fields"] if f["name"] not in known]
        assert not unknown, "%s shows %s, not fields of %s" % (sid, unknown, cfg["model"])


@pytest.mark.parametrize("model", NEW_MODELS + STRUCTURE_MODELS)
def test_new_captures_are_whitelisted_exactly_as_the_forms_type(m21, model):
    forms = [
        c for c in m21["screens"].values() if c["kind"] == "model_form" and c["model"] == model
    ]
    assert forms, "%s has no workspace form" % model
    typed = {f["name"] for c in forms for f in c["fields"] if not f["readonly"]}
    assert _writable()[model] == typed


@pytest.mark.parametrize("model", sorted(NEVER_TYPED))
def test_stamps_and_counts_are_never_typed(model):
    leaked = _writable().get(model, set()) & NEVER_TYPED[model]
    assert not leaked, (model, sorted(leaked))


def test_long_forms_are_tabbed(m21):
    """AGENTS.md: a form of more than 15 fields is split into tabs."""
    long_flat = [
        sid
        for sid, c in m21["screens"].items()
        if c["kind"] == "model_form" and len(c["fields"]) > 15 and not c["tabs"]
    ]
    assert not long_flat, long_flat


def test_a_withdrawal_asks_what_was_withdrawn(m21):
    acts = {a["m"]: a for a in m21["screens"]["M21-notice-acks"]["actions"]}
    assert acts["action_withdraw"]["kwargs"] == ["reason"]


def test_the_rights_list_is_scoped_to_employees(m21):
    cfg = m21["screens"]["M21-rights"]
    assert cfg["model"] == "fix.rights.request"
    assert cfg["domain"] == [["partner_id.employee_ids", "!=", False]]


def test_new_models_are_secured():
    acl = (HRCORE / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    rules = (HRCORE / "security" / "fix_a09_m21_capture_rules.xml").read_text(encoding="utf-8")
    manifest = (HRCORE / "__manifest__.py").read_text(encoding="utf-8")
    assert "security/fix_a09_m21_capture_rules.xml" in manifest
    for model in NEW_MODELS:
        xmlid = "model_" + model.replace(".", "_")
        rows = [r.split(",") for r in acl.splitlines() if (",%s," % xmlid) in r]
        assert rows, model
        # HR only: no row for every internal user
        assert not [r for r in rows if r[3] == "base.group_user"], model
        officer = [r for r in rows if r[3] == "cd_hr_core.group_hr_officer"]
        assert officer and officer[0][4:8] == ["1", "1", "1", "0"], model
        assert 'ref="%s"' % xmlid in rules, "%s has no company rule" % model


def test_the_new_file_loads_after_the_models_it_extends():
    """It extends hr.employee, fix.org.position and reads fix.hr.exit: an
    _inherit before its _name fails to load."""
    init = (HRCORE / "models" / "__init__.py").read_text(encoding="utf-8")
    # pass 2 (2026-11-19) loads fix_hr_capture2 last; it extends this file's
    # models, so this file is the one just before it
    assert init.rstrip().endswith("from . import fix_hr_capture2"), init
    imports = [ln for ln in init.splitlines() if ln.startswith("from . import")]
    assert imports[-2:] == ["from . import fix_hr_capture", "from . import fix_hr_capture2"], init
    assert "ruff: noqa: I001" in init
