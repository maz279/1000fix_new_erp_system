# M48 IoT Telemetry & Predictive Maintenance: every sub-module page captures
# each record it covers (capture audit 2026-11-17).
#
# Before (HEAD 3efdab37), evaluated with the engine's own fregCreate/fregPanels:
#   * page 3 (Ingestion & Storage) offered "+ New Iot Device" and page 5
#     (Health Scoring) "+ New Failure Prediction": neither is what the page does;
#   * pages 2, 5, 6 and 7 had no chip at all; the device and consent lists sat
#     on page 1 with no capture for either;
#   * six working lists sat on NO page: downsampling policies, retention
#     changes, gaps, readings, aggregates and the M48 alerts;
#   * the spec's signal definition (FR-IOT-004), criticality assessment
#     (FR-IOT-007), file batch channel (FR-IOT-012), maintenance window
#     (FR-IOT-032), health index history (FR-IOT-037/038) had no record; a
#     prediction no action acted on could never get its outcome (FR-IOT-044);
#     nothing decommissioned a stream or device (FR-IOT-008); an intervention
#     named no parts and no skill (FR-IOT-042).
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
CONTROLLER = HERE.parent / "controllers" / "a07" / "m48.py"
M26_CONTROLLER = HERE.parent / "controllers" / "a11" / "m26.py"
WRITABLE_FILE = HERE.parent / "controllers" / "a07" / "writable.py"
IOT = HERE.parents[2] / "domain" / "j_data_analytics" / "cd_stream_registry"

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
const mod = P03_MODULES.M48;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M48', map);
  const panels = fregPanels('M48', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M48:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M48.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: own || null, forms,
    reports: panels.reports.map((r) => ({ r, route: P03_REPORT_ROUTES['M48:' + r] || null })) };
});
console.log(JSON.stringify({ subs, forms: mod.forms,
  labelled: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => id.startsWith('M48-')).map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create, report: c.report || null,
    tabs: (c.tabs || []).map((t) => t.id),
    sectionTabs: (c.sections || []).map((s) => s.tab || null),
    saveAction: c.saveAction || null,
    pickDomain: (c.pickRecord && c.pickRecord.domain) || null,
    lines: c.lines ? { field: c.lines.field, fields: c.lines.fields.map((f) => f.name) } : null,
    actions: (c.actions || []).map((a) => ({ m: a.m, kwargs: (a.asks || []).map((q) => q.kwarg).concat(a.kwarg ? [a.kwarg] : []) })),
    cols: c.cols || [],
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({
      name: f.name, readonly: !!f.readonly, required: !!f.required })) }])) }));
"""


@pytest.fixture(scope="module")
def m48(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m48_capture")
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


def _surface_actions(path):
    out = {}
    value = _assigned(path, "SURFACES")
    for key, conf in zip(value.keys, value.values, strict=True):
        acts = set()
        for k, v in zip(conf.keys, conf.values, strict=True):
            if ast.literal_eval(k) == "actions" and isinstance(v, ast.Set):
                acts = {ast.literal_eval(e) for e in v.elts}
        out[ast.literal_eval(key)] = acts
    return out


def _surfaces():
    """M48's surfaces, plus the prediction surface the M26 controller serves."""
    out = _surface_actions(CONTROLLER)
    out["fix.predictive.maintenance"] = _surface_actions(M26_CONTROLLER)[
        "fix.predictive.maintenance"
    ]
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


def _model_methods():
    """{model: {method names}} defined in cd_stream_registry's model files."""
    out = {}
    for path in (IOT / "models").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for cls in (n for n in tree.body if isinstance(n, ast.ClassDef)):
            names = set()
            for stmt in cls.body:
                if (
                    isinstance(stmt, ast.Assign)
                    and isinstance(stmt.targets[0], ast.Name)
                    and stmt.targets[0].id in ("_name", "_inherit")
                    and isinstance(stmt.value, ast.Constant)
                ):
                    names.add(stmt.value.value)
            methods = {f.name for f in cls.body if isinstance(f, ast.FunctionDef)}
            for name in names:
                out.setdefault(name, set()).update(methods)
    return out


# What each page lets a person capture: its own "+ New" first, then every
# other record the page covers, by form screen.
CAPTURES = {
    "1": [
        "M48-form-stream",
        "M48-form-iot-device",
        "M48-form-signal",
        "M48-form-consent",
        "M48-form-scope",
    ],
    "2": ["M48-form-adapter", "M48-form-file-batch"],
    "3": ["M48-form-downsample", "M48-form-retention"],
    "4": ["M48-form-rule", "M48-form-window"],
    "5": ["M48-form-scope"],
    "6": ["M48-form-prediction", "M48-form-outcome"],
    "7": ["M48-form-action"],
}

RECORDS = {
    "1": "fix.iot.stream",
    "2": "fix.iot.adapter",
    "3": "fix.iot.downsample",
    "4": "fix.iot.rule",
    "5": "fix.iot.health",
    "6": "fix.predictive.maintenance",
    "7": "fix.iot.action",
}

# lists a page must show although nobody captures them there
LISTED = {
    "3": {"M48-gaps", "M48-telemetry", "M48-rollups", "M48-health"},
    "4": {"M48-lifecycle", "M48-asset-alerts"},
    "5": {"M48-health-history", "M48-scores"},
}

NEW_MODELS = (
    "fix.iot.signal",
    "fix.iot.monitoring.scope",
    "fix.iot.file.batch",
    "fix.iot.maintenance.window",
)

# What a form must never let a person type: states, stamps and derived figures.
NEVER_TYPED = {
    "fix.iot.signal": {"stream_count"},
    "fix.iot.monitoring.scope": {"assessed_by_id", "device_count", "last_scored_on", "worst_band"},
    "fix.iot.file.batch": {
        "state",
        "processed_by",
        "processed_on",
        "rows_total",
        "rows_accepted",
        "rows_rejected",
        "alerts_raised",
        "report",
    },
    "fix.iot.maintenance.window": {
        "state",
        "requested_by",
        "approved_by",
        "approved_on",
        "cancel_reason",
        "suppressed_count",
    },
    "fix.iot.device": {
        "status",
        "last_telemetry",
        "decommissioned",
        "decommissioned_on",
        "decommissioned_by",
        "decommission_reason",
    },
    "fix.iot.stream": {
        "state",
        "activated_on",
        "decommissioned_on",
        "decommissioned_by",
        "decommission_reason",
    },
    "fix.iot.action": {"state", "approved_by", "outcome", "skill_name", "parts_state"},
    "fix.iot.health": {
        "index_value",
        "band",
        "trend",
        "previous_index",
        "computed_at",
        "factors",
    },
}


def _sub(m48, no):
    return next(s for s in m48["subs"] if s["no"] == no)


def test_every_page_is_classified(m48):
    assert sorted(s["no"] for s in m48["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m48, no):
    sub = _sub(m48, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]}
    missing = [form for form in [own, *others] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)


@pytest.mark.parametrize("no", sorted(RECORDS, key=int))
def test_each_page_lists_its_own_record(m48, no):
    assert _sub(m48, no)["model"] == RECORDS[no]


@pytest.mark.parametrize("no", sorted(LISTED, key=int))
def test_system_raised_lists_sit_on_their_page(m48, no):
    assert LISTED[no] <= set(_sub(m48, no)["screens"])


def test_each_captured_record_is_listed_on_its_page(m48):
    for sub in m48["subs"]:
        listed = {m48["screens"][s]["model"] for s in sub["screens"] if s in m48["screens"]}
        for f in sub["forms"]:
            assert f["model"] in listed, "page %s captures %s but lists none" % (
                sub["no"],
                f["model"],
            )


def test_every_working_screen_sits_on_a_page(m48):
    placed = {sid for s in m48["subs"] for sid in s["screens"]}
    placed |= {r["route"] for s in m48["subs"] for r in s["reports"]}
    orphans = [
        sid
        for sid, cfg in m48["screens"].items()
        if cfg["kind"] in ("model_list", "table_report")
        and sid not in placed
        and not sid.startswith("M48-rpt-")
    ]
    assert not orphans, orphans


def test_every_report_chip_routes(m48):
    for sub in m48["subs"]:
        for r in sub["reports"]:
            assert r["route"] in m48["screens"], (sub["no"], r)


def test_every_screen_on_a_page_has_a_navigation_label(m48):
    """A list on a page but in no navigation group shows as its raw id."""
    labelled = set(m48["labelled"])
    unlabelled = sorted(
        sid
        for sub in m48["subs"]
        for sid in sub["screens"]
        if sid in m48["screens"]
        and m48["screens"][sid]["kind"] == "model_list"
        and sid not in labelled
    )
    assert not unlabelled, unlabelled


def test_every_served_action_exists_on_its_model():
    methods = _model_methods()
    for model, acts in _surfaces().items():
        missing = acts - methods.get(model, set())
        # the approval actions come from cd_workflow_engine's mixin
        missing -= {"action_request_approval", "action_recall_approval"}
        assert not missing, "%s serves %s, which the model lacks" % (model, sorted(missing))


def test_every_list_action_is_served(m48):
    surfaces = _surfaces()
    for sid, cfg in m48["screens"].items():
        if cfg["kind"] != "model_list" or not cfg["actions"]:
            continue
        if cfg["model"] not in surfaces:
            continue  # served by its owner's controller (fix.asset.alert: the spine)
        served = surfaces[cfg["model"]]
        for act in cfg["actions"]:
            assert act["m"] in served, "%s offers %s, not served" % (sid, act["m"])


def test_every_save_action_is_served(m48):
    surfaces = _surfaces()
    for sid, cfg in m48["screens"].items():
        act = cfg["saveAction"]
        if act:
            assert act["method"] in surfaces.get(cfg["model"], set()), (sid, act["method"])


@pytest.mark.parametrize("model", NEW_MODELS)
def test_new_registers_are_served_and_whitelisted(m48, model):
    assert model in _surfaces()
    forms = [
        c for c in m48["screens"].values() if c["kind"] == "model_form" and c["model"] == model
    ]
    assert forms, "%s has no workspace form" % model
    typed = {f["name"] for c in forms for f in c["fields"] if not f["readonly"]}
    assert _writable()[model] == typed


def test_the_health_history_is_never_typed(m48):
    assert "fix.iot.health" in _surfaces()
    form = m48["screens"]["M48-form-health"]
    assert form["create"] is False
    assert all(f["readonly"] for f in form["fields"])
    assert m48["screens"]["M48-health-history"]["create"] is False


@pytest.mark.parametrize("model", sorted(NEVER_TYPED))
def test_stamps_and_derived_figures_are_never_typed(model):
    leaked = _writable().get(model, set()) & NEVER_TYPED[model]
    assert not leaked, (model, sorted(leaked))


def test_long_forms_are_tabbed(m48):
    """Project standard: a form over 15 fields is partitioned into tabs."""
    long_forms = {
        sid: cfg
        for sid, cfg in m48["screens"].items()
        if cfg["kind"] == "model_form" and len(cfg["fields"]) > 15
    }
    assert {"M48-form-rule", "M48-form-consent", "M48-form-action", "M48-form-prediction"} <= set(
        long_forms
    )
    for sid, cfg in long_forms.items():
        assert cfg["tabs"], "%s has %d fields and no tabs" % (sid, len(cfg["fields"]))
        assert all(t in cfg["tabs"] for t in cfg["sectionTabs"]), sid


def test_the_device_form_captures_identity(m48):
    names = {f["name"] for f in m48["screens"]["M48-form-iot-device"]["fields"]}
    wanted = {"firmware", "connectivity", "gateway_id", "serial_no", "installed_on"}
    assert wanted <= names
    assert wanted <= _writable()["fix.iot.device"]


def test_the_stream_form_binds_a_signal_and_source(m48):
    names = {f["name"] for f in m48["screens"]["M48-form-stream"]["fields"]}
    assert {"signal_id", "source_address"} <= names
    assert {"signal_id", "source_address"} <= _writable()["fix.iot.stream"]


def test_streams_and_devices_are_decommissioned_from_their_lists(m48):
    for sid in ("M48-streams", "M48-iot-device"):
        acts = {a["m"]: a["kwargs"] for a in m48["screens"][sid]["actions"]}
        assert acts.get("action_decommission") == ["reason"], sid


def test_the_outcome_form_picks_a_pending_prediction(m48):
    form = m48["screens"]["M48-form-outcome"]
    assert form["saveAction"]["method"] == "action_record_outcome"
    assert form["saveAction"]["kwargs"] == {
        "outcome": "outcome",
        "note": "outcome_note",
        "evidence_ref": "outcome_evidence_ref",
    }
    assert ["outcome", "=", "pending"] in form["pickDomain"]


def test_the_action_form_names_parts_and_skill(m48):
    form = m48["screens"]["M48-form-action"]
    assert form["lines"] == {
        "field": "part_ids",
        "fields": ["product_id", "quantity", "on_hand", "availability"],
    }
    names = {f["name"] for f in form["fields"]}
    assert {"skill_code", "recommended_action"} <= names
    assert {"part_ids", "skill_code", "recommended_action"} <= _writable()["fix.iot.action"]


def test_the_prediction_form_records_mode_and_rul_interval(m48):
    names = {f["name"] for f in m48["screens"]["M48-form-prediction"]["fields"]}
    assert {"failure_mode", "rul_low_days", "rul_high_days"} <= names


def test_new_models_are_secured():
    acl = (IOT / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    rules = (IOT / "security" / "fix_iot_scope_rules.xml").read_text(encoding="utf-8")
    for model in (*NEW_MODELS, "fix.iot.health", "fix.iot.action.part"):
        xmlid = "model_" + model.replace(".", "_")
        rows = [r.split(",") for r in acl.splitlines() if (",%s," % xmlid) in r]
        assert rows, model
        assert 'ref="%s"' % xmlid in rules, "%s has no company rule" % model
        if model in (
            "fix.iot.signal",
            "fix.iot.monitoring.scope",
            "fix.iot.health",
            "fix.iot.maintenance.window",
        ):
            # nobody deletes a register row: archive or cancel instead
            assert all(r[-1].strip() == "0" for r in rows), model


def test_the_new_file_loads_after_the_models_it_extends():
    init = (IOT / "models" / "__init__.py").read_text(encoding="utf-8")
    for base in ("fix_iot_ops", "fix_stream_registry"):
        assert init.index(base) < init.index("fix_iot_capture"), base
