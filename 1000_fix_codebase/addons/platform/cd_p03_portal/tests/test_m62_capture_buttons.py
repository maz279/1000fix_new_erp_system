# M62 Data Platform & Governance: every sub-module page captures each record
# it covers (capture audit 2026-11-18).
#
# Before (HEAD 32e24dc9), evaluated with the engine's own fregCreate/fregPanels:
#   * page 7 (Security & Cost) offered NO "+ New" and NO chip: its mapped
#     model is M29's sensitive-field list (create: false), so the retention
#     policy form that existed was reachable from no page; declassification
#     authorisations (the only way to lower a classification, BRU-DAT-11)
#     were served by the API but had no screen and no form; there was no
#     erasure propagation at all (FR-DAT-036 P0, BRU-DAT-15);
#   * page 4 (Semantic Layer) captured definitions only: metric VERSIONS -
#     the one path to publication - and the consumer register had no screen
#     and no form, and the whitelist for versions was empty, so no metric
#     could ever be published from the workspace; no glossary (FR-DAT-022);
#   * pages 1, 2, 3 and 6 had no chip; page 1 had no data source register
#     (spec 10.1), page 3 no conformed dimension (FR-DAT-010/011);
#   * the entity form had no Odoo model or layer and the rule form no check
#     field, so no rule created in the workspace could ever be measured.
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
CONTROLLER = HERE.parent / "controllers" / "a11" / "m62.py"
ADDONS = HERE.parents[2]
REG = ADDONS / "domain" / "j_data_analytics" / "cd_metric_registry"
MODEL_FILES = [
    *(REG / "models").glob("*.py"),
    ADDONS / "platform" / "cd_rbac_ext" / "models" / "fix_access_ops.py",
]

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
const mod = P03_MODULES.M62;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M62', map);
  const panels = fregPanels('M62', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M62:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M62.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: own || null, forms,
    reports: panels.reports.map((r) => ({ r, route: P03_REPORT_ROUTES['M62:' + r] || null })) };
});
const screen = (c) => ({
    kind: c.kind, model: c.model || null, create: c.create, report: c.report || null,
    tabIds: (c.tabs || []).map((t) => t.id),
    sectionTabs: (c.sections || []).map((s) => s.tab || null),
    actions: (c.actions || []).map((a) => ({ m: a.m, kwargs: (a.asks || []).map((q) => q.kwarg) })),
    cols: c.cols || [],
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({
      name: f.name, readonly: !!f.readonly, required: !!f.required })) });
console.log(JSON.stringify({ subs, forms: mod.forms,
  labelled: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => id.startsWith('M62-')).map(([id, c]) => [id, screen(c)])) }));
"""


@pytest.fixture(scope="module")
def m62(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m62_capture")
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
    value = _assigned(CONTROLLER, "WRITABLE")
    for key, val in zip(value.keys, value.values, strict=True):
        names = set()
        if isinstance(val, ast.Call) and val.args:
            names = set(ast.literal_eval(val.args[0]))
        out[ast.literal_eval(key)] = names
    return out


# what every model here also has, from the mail and approval mixins
MIXIN_FIELDS = {"name", "display_name", "approval_state", "approval_request_id", "active"}


def _model_classes():
    """{model: ({fields}, {methods})} defined or extended in the M62 module
    (and M29's sensitive field, which page 7 lists)."""
    out = {}
    for path in MODEL_FILES:
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
    "1": ["M62-form-pipeline", "M62-form-source", "M62-form-run"],
    "2": ["M62-form-run"],
    "3": ["M62-form-entity", "M62-form-dimension"],
    "4": [
        "M62-form-metric",
        "M62-form-version",
        "M62-form-consumer",
        "M62-form-glossary",
        "M62-form-contract",
    ],
    "5": ["M62-form-qrule", "M62-form-quality", "M62-form-incident"],
    "6": ["M62-form-data-lineage", "M62-form-entity", "M62-form-glossary"],
    "7": ["M62-form-retention", "M62-form-declass", "M62-form-erasure", "M29-form-sensitive"],
}

NEW_MODELS = ("fix.data.source", "fix.data.dimension", "fix.glossary.term", "fix.data.erasure")

# Forms that existed with no screen and no form at HEAD, served by the API.
UNSERVED_AT_HEAD = ("fix.metric.version", "fix.metric.consumer", "fix.data.declassification.auth")

# What a form must never let a person type: the state, every decision stamp
# and every measured figure.
NEVER_TYPED = {
    "fix.data.source": {"state", "activated_by", "activated_at", "pipeline_count"},
    "fix.data.pipeline": {"state", "last_run_at", "last_success_at"},
    "fix.data.run": {"state", "finished_at", "duration_minutes", "failure_reason"},
    "fix.data.entity": {"degraded"},
    "fix.data.contract": {
        "state",
        "version",
        "predecessor_id",
        "producer_signed_by",
        "producer_signed_at",
        "approval_state",
    },
    "fix.metric.definition": {"state", "current_version_id"},
    "fix.metric.version": {
        "state",
        "version",
        "steward_reviewed_by",
        "steward_reviewed_at",
        "published_by",
        "published_at",
        "impact_snapshot",
        "approval_state",
    },
    "fix.data.quality.rule": {"state", "last_result", "last_checked", "last_measured"},
    "fix.data.quality.test": {"threshold", "passed", "measured"},
    "fix.data.incident": {"state", "resolved_at", "due_at", "source_event_id"},
    "fix.data.retention.policy": {"pending_months", "monthly_cost"},
    "fix.data.declassification.auth": {"state", "approved_by", "approved_at", "approval_state"},
    "fix.data.erasure": {"state", "completed_by", "completed_at", "partner_id"},
}


def _sub(m62, no):
    return next(s for s in m62["subs"] if s["no"] == no)


def test_every_page_is_classified(m62):
    assert sorted(s["no"] for s in m62["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m62, no):
    sub = _sub(m62, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]} | {sub["create"]}
    missing = [form for form in [own, *others] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)


def test_page_7_captures_although_its_list_is_m29s(m62):
    sub = _sub(m62, "7")
    assert sub["model"] == "fix.sensitive.field"
    assert m62["screens"]["M62-masking"]["create"] is False
    assert sub["create"] == "M62-form-retention"


def test_each_captured_record_is_listed_on_its_page(m62):
    for sub in m62["subs"]:
        listed = {m62["screens"][s]["model"] for s in sub["screens"] if s in m62["screens"]}
        listed.add(sub["model"])
        captures = [f for f in sub["forms"] if f["id"] and f["id"].startswith("M62-")]
        if sub["create"]:
            captures.append({"model": m62["screens"][sub["create"]]["model"]})
        for f in captures:
            assert f["model"] in listed, "page %s captures %s but lists none" % (
                sub["no"],
                f["model"],
            )


def test_every_creatable_list_on_a_page_has_its_capture(m62):
    for sub in m62["subs"]:
        captured = {f["model"] for f in sub["forms"] if f["opens"]}
        if sub["create"]:
            captured.add(m62["screens"][sub["create"]]["model"])
        for sid in sub["screens"]:
            cfg = m62["screens"].get(sid, {})
            if cfg.get("kind") == "model_list" and cfg.get("create") is not False:
                assert cfg["model"] in captured, "page %s lists %s (%s) with no capture" % (
                    sub["no"],
                    cfg["model"],
                    sid,
                )


def test_every_served_model_has_a_screen_on_a_page(m62):
    """A model the API serves but no page lists is a register nobody can
    reach (versions, consumers and declassifications at HEAD)."""
    placed = {
        m62["screens"][sid]["model"]
        for s in m62["subs"]
        for sid in s["screens"]
        if sid in m62["screens"]
    }
    unplaced = sorted(set(_surfaces()) - placed)
    assert not unplaced, unplaced


@pytest.mark.parametrize("model", UNSERVED_AT_HEAD + NEW_MODELS)
def test_each_register_has_a_form_and_a_list(m62, model):
    kinds = {c["kind"] for c in m62["screens"].values() if c["model"] == model}
    assert {"model_list", "model_form"} <= kinds, (model, kinds)


def test_every_working_screen_sits_on_a_page(m62):
    placed = {sid for s in m62["subs"] for sid in s["screens"]}
    placed |= {r["route"] for s in m62["subs"] for r in s["reports"]}
    orphans = [
        sid
        for sid, cfg in m62["screens"].items()
        if cfg["kind"] in ("model_list", "table_report") and sid not in placed
    ]
    assert not orphans, orphans


def test_every_screen_on_a_page_has_a_navigation_label(m62):
    labelled = set(m62["labelled"])
    unlabelled = sorted(
        sid
        for sub in m62["subs"]
        for sid in sub["screens"]
        if sid in m62["screens"] and sid not in labelled
    )
    assert not unlabelled, unlabelled


def test_every_served_action_exists_on_its_model():
    classes = _model_classes()
    generic = {"action_request_approval", "action_recall_approval"}  # the M63 mixin's verbs
    for model, acts in _surfaces().items():
        methods = classes.get(model, (set(), set()))[1]
        missing = acts - methods - generic
        assert not missing, "%s serves %s, which the model lacks" % (model, sorted(missing))


def test_every_list_action_is_served(m62):
    surfaces = _surfaces()
    for sid, cfg in m62["screens"].items():
        if cfg["kind"] != "model_list" or not cfg["actions"]:
            continue
        served = surfaces[cfg["model"]]
        for act in cfg["actions"]:
            assert act["m"] in served, "%s offers %s, not served" % (sid, act["m"])


def test_the_governed_steps_are_buttons(m62):
    """A captured record that cannot take its next governed step is a dead
    capture: the contract co-signature, the version's review and request, the
    rule's measurement, the shortening request and the erasure completion
    were served by the API at HEAD but offered on no list."""
    want = {
        "M62-contracts": {"action_producer_sign", "action_request_approval", "action_new_version"},
        "M62-metric-versions": {"action_steward_review", "action_request_approval"},
        "M62-metrics": {"action_retire"},
        "M62-rules": {"action_measure"},
        "M62-retention": {"action_request_shorten", "action_purge"},
        "M62-declass": {"action_request_approval"},
        "M62-erasure": {"action_complete"},
        "M62-sources": {"action_activate", "action_retire"},
    }
    for sid, acts in want.items():
        offered = {a["m"] for a in m62["screens"][sid]["actions"]}
        assert acts <= offered, (sid, sorted(acts - offered))
    shorten = next(
        a for a in m62["screens"]["M62-retention"]["actions"] if a["m"] == "action_request_shorten"
    )
    assert shorten["kwargs"] == ["new_months"]


def test_every_list_column_exists_on_its_model(m62):
    """A column the model lacks is dropped silently by the endpoint."""
    classes = _model_classes()
    for sid, cfg in m62["screens"].items():
        if cfg["kind"] != "model_list" or cfg["model"] not in classes:
            continue
        known = classes[cfg["model"]][0] | MIXIN_FIELDS
        unknown = [c for c in cfg["cols"] if c not in known]
        assert not unknown, "%s lists %s, not fields of %s" % (sid, unknown, cfg["model"])


def test_every_form_field_exists_on_its_model(m62):
    classes = _model_classes()
    for sid, cfg in m62["screens"].items():
        if cfg["kind"] != "model_form" or cfg["model"] not in classes:
            continue
        known = classes[cfg["model"]][0] | MIXIN_FIELDS
        unknown = [f["name"] for f in cfg["fields"] if f["name"] not in known]
        assert not unknown, "%s shows %s, not fields of %s" % (sid, unknown, cfg["model"])


def test_every_form_tab_is_declared(m62):
    """A section naming an undeclared tab renders as an invisible panel."""
    for sid, cfg in m62["screens"].items():
        if cfg["kind"] != "model_form":
            continue
        if cfg["tabIds"]:
            stray = [t for t in cfg["sectionTabs"] if t not in cfg["tabIds"]]
            assert not stray, (sid, stray)
        else:
            assert not any(cfg["sectionTabs"]), sid


def test_each_form_types_exactly_its_whitelist(m62):
    """What a form lets a person type is exactly what the surface accepts;
    the rest is display. With an empty version whitelist no version could be
    drafted at all."""
    writable = _writable()
    forms = {}
    for cfg in m62["screens"].values():
        if cfg["kind"] == "model_form" and cfg["model"] in writable:
            forms.setdefault(cfg["model"], set()).update(
                f["name"] for f in cfg["fields"] if not f["readonly"]
            )
    for model, typed in forms.items():
        assert writable[model] == typed, (model, sorted(writable[model] ^ typed))


def test_state_is_never_typed_on_a_form(m62):
    for sid, cfg in m62["screens"].items():
        if cfg["kind"] != "model_form":
            continue
        for f in cfg["fields"]:
            if f["name"] == "state":
                assert f["readonly"], "%s lets a person type the state" % sid


@pytest.mark.parametrize("model", sorted(NEVER_TYPED))
def test_stamps_and_measured_figures_are_never_typed(model):
    leaked = _writable().get(model, set()) & NEVER_TYPED[model]
    assert not leaked, (model, sorted(leaked))


def test_capture_forms_carry_the_fields_that_make_the_record_work(m62):
    """An entity without an Odoo model can never be measured or purged; a rule
    without a check field never measured; a contract without its signatory
    never signed by its producer."""

    def typed(sid):
        return {f["name"] for f in m62["screens"][sid]["fields"] if not f["readonly"]}

    assert {"res_model", "warehouse_layer", "model_kind", "grain_declaration"} <= typed(
        "M62-form-entity"
    )
    assert {"check_field", "freshness_window_hours", "severity"} <= typed("M62-form-qrule")
    assert "producer_signatory_id" in typed("M62-form-contract")
    assert "transformation" in typed("M62-form-data-lineage")
    assert {"period_from", "period_to", "replay_of_run_id", "reason"} <= typed("M62-form-run")
    assert {"data_source_id", "layer", "upstream_ids"} <= typed("M62-form-pipeline")


def test_new_forms_are_tabbed(m62):
    """AGENTS.md: forms are split into Dynamics-style tabs."""
    for model in (*NEW_MODELS, "fix.metric.version"):
        forms = [
            c for c in m62["screens"].values() if c["kind"] == "model_form" and c["model"] == model
        ]
        assert forms and all(len(c["tabIds"]) >= 2 for c in forms), model


def test_new_models_are_secured():
    acl = (REG / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    rules = (REG / "security" / "fix_isolation_rules.xml").read_text(encoding="utf-8")
    rows = [r.split(",") for r in acl.splitlines()[1:] if r.strip()]
    for model in NEW_MODELS:
        xmlid = "model_" + model.replace(".", "_")
        mine = [r for r in rows if r[2] == xmlid]
        assert mine, model
        assert 'ref="%s"' % xmlid in rules, "%s has no company rule" % model
        # the governance rule book: plain users never write it
        for r in mine:
            if r[3] == "base.group_user":
                assert r[5:8] == ["0", "0", "0"], r
    # an erasure carries a person: no plain-user row at all; nobody deletes it
    erasure = [r for r in rows if r[2] == "model_fix_data_erasure"]
    assert all(r[3] != "base.group_user" for r in erasure)
    assert all(r[7].strip() == "0" for r in erasure)


def test_the_new_file_loads_after_the_models_it_extends():
    """Every extender is imported after the file that defines what it extends.

    A11 deep audit A3-F04 moved the seed-integrity repair into
    fix_data_platform (it extends fix.data.entity), so the two base files are
    imported model-definition-first; fix_m62_capture still comes last."""
    init = (REG / "models" / "__init__.py").read_text(encoding="utf-8")
    imports = [line for line in init.splitlines() if line.startswith("from . import")]
    assert len(imports) == 2, imports
    base, last = imports
    assert "fix_metric_registry" in base and "fix_data_platform" in base
    assert "fix_m62_capture" in last
    # fix.data.entity is defined before anything extends it, and the capture
    # file (which extends models from both) is imported after both
    assert init.index("from . import fix_m62_capture") > init.index("fix_data_platform")
    assert init.index("fix_metric_registry") < init.index("from . import fix_m62_capture")
    manifest = (REG / "__manifest__.py").read_text(encoding="utf-8")
    assert '"cd_party_master"' in manifest, "the erasure extends M33's rights request"
