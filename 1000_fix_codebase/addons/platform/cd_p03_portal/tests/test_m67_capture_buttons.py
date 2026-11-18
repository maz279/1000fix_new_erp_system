# M67 Projects & Portfolio: every sub-module page captures the records it
# covers (capture audit 2026-11-18).
#
# Before (HEAD 097904f0), evaluated with the engine's own fregCreate/fregPanels:
#   * page 5 (Financials) and page 6 ("Audit") had a "+ New" but no form chip;
#   * page 2 (Project Setup) opened + New Project Template with no Template chip;
#   * five records the specification makes M67 own existed nowhere, so no page
#     could capture them: the deliverable register (FR-PPM-004 P0), scope change
#     control (FR-PPM-013 P0, BRU-PPM-06 H), the budget by cost category
#     (FR-PPM-024 P0), lessons learned (FR-PPM-032 P0, BRU-PPM-14 H) and benefit
#     realisation (FR-PPM-032 P0, BRU-PPM-15 H) - the Benefits Realisation report
#     printed "not recorded" on every row because nothing could record one;
#   * the Resource Utilisation and Benefits Realisation reports sat on no page.
#
# Evaluated as the browser evaluates it: node runs the engine's own fregCreate
# and fregPanels over the real registry fragments (the M65 guard's fixture).
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
CONTROLLER = HERE.parent / "controllers" / "a12" / "m67.py"
PPM = HERE.parents[2] / "domain" / "i_governance" / "cd_ppm"
ITSM_CONTROLLER = HERE.parent / "controllers" / "a12" / "m66.py"

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
const mod = P03_MODULES.M67;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M67', map);
  const panels = fregPanels('M67', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M67:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M67.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: own || null, label: create ? create.label : null, forms,
    reports: panels.reports.map((r) => ({ r, route: P03_REPORT_ROUTES['M67:' + r] || null })) };
});
const shown = (c) => ({
  kind: c.kind, model: c.model || null, create: c.create, report: c.report || null,
  tabs: (c.tabs || []).map((t) => t.id),
  actions: (c.actions || []).map((a) => ({ m: a.m,
    kwargs: (a.asks || []).map((q) => q.kwarg).concat(a.kwarg ? [a.kwarg] : []) })),
  cols: c.cols || [],
  fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({
    name: f.name, readonly: !!f.readonly, required: !!f.required })) });
console.log(JSON.stringify({ subs,
  kpis: mod.kpis.map((k) => k.m),
  reports: mod.reports, forms: mod.forms,
  nav: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS)
    .filter(([id]) => id.startsWith('M67-')).map(([id, c]) => [id, shown(c)])),
  by_screen: P03_FORM_CHIPS['M67:__by_screen__'] }));
"""

# What each page must let a person capture: the page's own "+ New" first,
# then every other record the page covers, by its form screen.
CAPTURES = {
    "1": ["M67-form-project"],
    "2": ["M67-form-template", "M67-form-project"],
    "3": ["M67-form-task", "M67-form-milestone", "M67-form-deliverable"],
    "4": ["M67-form-gate", "M67-form-change"],
    "5": ["M67-form-billing", "M67-form-budget-line"],
    "6": ["M67-form-risk", "M67-form-lesson", "M67-form-benefit"],
}

# The models the capture audit built (cd_ppm/models/fix_ppm_capture.py).
NEW_MODELS = (
    "fix.project.deliverable",
    "fix.project.change",
    "fix.project.budget.line",
    "fix.project.lesson",
    "fix.project.benefit",
)

# What a form must never let a person type: the state, the decision and every stamp.
NEVER_TYPED = {
    "fix.project.deliverable": {
        "name",
        "state",
        "submitted_by_id",
        "submitted_on",
        "decided_by_id",
        "decided_on",
        "rejection_reason",
    },
    "fix.project.change": {
        "name",
        "state",
        "requested_by_id",
        "submitted_on",
        "decided_by_id",
        "decided_on",
        "decision_note",
    },
    "fix.project.lesson": {"name", "state", "recorded_by_id", "shared_by_id", "shared_on"},
    "fix.project.benefit": {
        "state",
        "measured_value",
        "measured_on",
        "measured_by_id",
        "measurement_evidence",
        "realised_pct",
    },
}


@pytest.fixture(scope="module")
def m67(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m67_capture")
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


def _literal_names(node):
    if isinstance(node, ast.Set | ast.Tuple | ast.List):
        return {ast.literal_eval(e) for e in node.elts}
    if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "set":
        return set()
    return set()


def _controller(path):
    """SURFACES (actions) / WRITABLE / REPORTS of a controller module, read without Odoo."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out = {"REPORTS": set(), "SURFACES": {}, "WRITABLE": {}}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name == "WRITABLE" and isinstance(node.value, ast.Dict):
                out[name] = {
                    ast.literal_eval(k): _literal_names(v)
                    for k, v in zip(node.value.keys, node.value.values, strict=True)
                }
            elif name == "SURFACES" and isinstance(node.value, ast.Dict):
                for key, conf in zip(node.value.keys, node.value.values, strict=True):
                    acts = set()
                    for k, v in zip(conf.keys, conf.values, strict=True):
                        if ast.literal_eval(k) == "actions":
                            acts = _literal_names(v)
                    out[name][ast.literal_eval(key)] = acts
            elif name == "REPORTS" and isinstance(node.value, ast.Dict):
                out["REPORTS"] |= {ast.literal_eval(k) for k in node.value.keys}
        if (
            isinstance(node, ast.Assign)
            and isinstance(node.targets[0], ast.Subscript)
            and isinstance(node.targets[0].value, ast.Name)
            and node.targets[0].value.id == "REPORTS"
        ):
            out["REPORTS"].add(ast.literal_eval(node.targets[0].slice))
    return out


def _sub(m67, no):
    return next(s for s in m67["subs"] if s["no"] == no)


def _served():
    # the stage gate is cd_itsm's model, served by the M66 controller
    return {**_controller(ITSM_CONTROLLER)["SURFACES"], **_controller(CONTROLLER)["SURFACES"]}


def test_every_page_is_classified(m67):
    assert sorted(s["no"] for s in m67["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m67, no):
    sub = _sub(m67, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]}
    missing = [form for form in [own, *others] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)
    for f in sub["forms"]:
        assert f["kind"] == "model_form", "chip %s opens %s" % (f["f"], f["kind"])


def test_the_audit_page_is_named_for_what_it_holds(m67):
    assert _sub(m67, "6")["title"] == "Risks, Issues & Closure"


def test_each_captured_record_is_listed_on_its_page(m67):
    """A capture lands on a list of the page it was made from."""
    for sub in m67["subs"]:
        listed = {m67["screens"][s]["model"] for s in sub["screens"] if s in m67["screens"]}
        listed.add(sub["model"])
        for f in sub["forms"]:
            assert f["model"] in listed, "page %s captures %s but lists no such record" % (
                sub["no"],
                f["model"],
            )


def test_every_working_screen_sits_on_a_page_and_in_the_nav(m67):
    placed = {sid for s in m67["subs"] for sid in s["screens"]}
    placed |= {r["route"] for s in m67["subs"] for r in s["reports"]}
    lists = [
        sid for sid, cfg in m67["screens"].items() if cfg["kind"] in ("model_list", "table_report")
    ]
    assert not [sid for sid in lists if sid not in placed]
    assert not [sid for sid in lists if sid not in m67["nav"]]


def test_every_module_report_and_form_sits_on_a_page(m67):
    reports = {r["r"] for s in m67["subs"] for r in s["reports"]}
    forms = {f["f"] for s in m67["subs"] for f in s["forms"]}
    assert set(m67["reports"]) <= reports, set(m67["reports"]) - reports
    assert set(m67["forms"]) <= forms, set(m67["forms"]) - forms


def test_every_page_report_opens_its_pack(m67):
    reports = _controller(CONTROLLER)["REPORTS"]
    for sub in m67["subs"]:
        for r in sub["reports"]:
            assert r["route"], "page %s report %s has no route" % (sub["no"], r["r"])
            assert m67["screens"][r["route"]]["report"] in reports, r


def test_a_list_offering_new_opens_a_form_of_its_own_model(m67):
    for sid, cfg in m67["screens"].items():
        if cfg["kind"] != "model_list" or cfg.get("create") is False:
            continue
        form = m67["by_screen"].get(sid)
        assert form, "%s offers + New but opens no form" % sid
        assert m67["screens"][form]["model"] == cfg["model"], sid


def test_every_listed_model_and_row_action_is_served(m67):
    surfaces = _served()
    for sid, cfg in m67["screens"].items():
        if cfg["kind"] not in ("model_list", "model_form"):
            continue
        assert cfg["model"] in surfaces, "%s reads %s, which nobody serves" % (sid, cfg["model"])
        for act in cfg["actions"]:
            assert act["m"] in surfaces[cfg["model"]], "%s %s is not served" % (sid, act["m"])


def test_every_editable_field_of_a_new_form_is_writable(m67):
    writable = _controller(CONTROLLER)["WRITABLE"]
    for sid, cfg in m67["screens"].items():
        if cfg["kind"] != "model_form" or cfg["model"] not in NEW_MODELS:
            continue
        editable = {f["name"] for f in cfg["fields"] if not f["readonly"]}
        lost = editable - writable[cfg["model"]]
        assert not lost, "%s cannot save %s" % (sid, sorted(lost))


def test_workflow_stamps_are_never_typed(m67):
    writable = _controller(CONTROLLER)["WRITABLE"]
    for model, names in NEVER_TYPED.items():
        assert not names & writable[model], model
    for sid, cfg in m67["screens"].items():
        if cfg["kind"] == "model_form" and cfg["model"] in NEVER_TYPED:
            shown = {f["name"]: f for f in cfg["fields"]}
            for name in NEVER_TYPED[cfg["model"]] & set(shown):
                assert shown[name]["readonly"], "%s lets %s be typed" % (sid, name)


def test_the_prompts_send_what_the_methods_take(m67):
    """A button that asks sends the kwarg its method reads."""
    model_file = (PPM / "models" / "fix_ppm_capture.py").read_text(encoding="utf-8")
    expected = {
        ("M67-deliverables", "action_send_back"): ["reason"],
        ("M67-changes", "action_reject"): ["note"],
        ("M67-benefits", "action_record_measurement"): ["measured_value", "evidence"],
    }
    for (sid, method), kwargs in expected.items():
        act = next(a for a in m67["screens"][sid]["actions"] if a["m"] == method)
        assert act["kwargs"] == kwargs, (sid, method, act["kwargs"])
        signature = re.search(r"def %s\(self, ([^)]*)\)" % method, model_file).group(1)
        for kwarg in kwargs:
            assert kwarg + "=None" in signature, (method, kwarg)


def test_long_forms_are_tabbed(m67):
    """Workspace standard: a form with more than 15 fields is split into tabs."""
    for sid, cfg in m67["screens"].items():
        if cfg["kind"] == "model_form" and len(cfg["fields"]) > 15:
            assert cfg["tabs"], "%s has %d fields and no tabs" % (sid, len(cfg["fields"]))


def test_new_models_have_access_rows_and_company_rules():
    acl = (PPM / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    rules = (PPM / "security" / "fix_isolation_rules.xml").read_text(encoding="utf-8")
    for model in NEW_MODELS:
        ref = "model_" + model.replace(".", "_")
        assert ",%s,cd_ppm.group_ppm_project_manager,1,1,1," % ref in acl, model
        for line in acl.splitlines():
            if ",%s,base.group_user," % ref in line:
                assert line.endswith(",1,0,0,0"), line
        assert 'ref="%s"' % ref in rules, model


def test_the_capture_models_load_after_the_project_models():
    """fix_ppm_capture extends fix.project and fix.project.milestone (fix_ppm)."""
    init = (PPM / "models" / "__init__.py").read_text(encoding="utf-8")
    order = re.search(r"from \. import (.+)", init).group(1).split(", ")
    assert order.index("fix_ppm_capture") > order.index("fix_ppm")
    manifest = (PPM / "__manifest__.py").read_text(encoding="utf-8")
    assert "data/fix_ppm_capture_sequences.xml" in manifest


def test_the_new_kpis_are_served(m67):
    assert {"changes_pending", "deliverables_awaiting"} <= set(m67["kpis"])
    text = CONTROLLER.read_text(encoding="utf-8")
    assert '"changes_pending"' in text and '"deliverables_awaiting"' in text


def test_closure_checks_lessons_and_benefits():
    """BRU-PPM-14/15: project completion calls the closure-records check."""
    core = (PPM / "models" / "fix_ppm.py").read_text(encoding="utf-8")
    body = core[core.index('    def action_complete(self):\n        """F18') :]
    body = body[: body.index("    # ---- event consumers")]
    assert "rec._ppm_closure_records_ready()" in body
    capture = (PPM / "models" / "fix_ppm_capture.py").read_text(encoding="utf-8")
    assert "BRU-PPM-14" in capture and "BRU-PPM-15" in capture
