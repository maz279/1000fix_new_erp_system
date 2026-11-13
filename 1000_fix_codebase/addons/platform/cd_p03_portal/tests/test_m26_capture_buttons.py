# M26 AI/ML Services: every sub-module page captures the records it covers
# (capture audit 2026-11-14).
#
# Before:
#   * Training Pipelines and Explainability offered "+ New Model Version", a
#     form that could not save: it posted `state` (a selection with a
#     default) and the version's lifecycle guard refused every create and
#     every edit - no version could be registered and no model card written.
#   * Deployment & Monitoring had no capture at all (create:false): the
#     fallback test the spec makes a hard rule (BRU-AIM-06) and the drift
#     observations of the monitoring run had no record.
#   * Explainability offered a new version, not the card or the override.
#   * GenAI & RAG offered "+ New ML Model Catalogue Entry" - a deterministic
#     engine entry with no generative kind to choose.
#   * Bengali NLP & OCR offered the module's inference run with any model.
#   * The portfolio form had none of the spec's declarations (consumer,
#     target, fallback, risk class, owner, review date - FR-AIM-001).
#
# Evaluated as the browser evaluates it: node runs the engine's own fregCreate
# and fregPanels over the real registry fragments (the M22/M37 guards' fixture).
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
ROOT = HERE.parents[2]

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
const mod = P03_MODULES.M26;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M26', map);
  const forms = fregPanels('M26', mod, map).forms.map((f) => {
    const id = P03_FORM_CHIPS['M26:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    domain: map.domain || [], presets: (create && create.presets) || null,
    create: create && (create.screen || (create.module ? 'module' : null)), forms };
});
console.log(JSON.stringify({ subs,
  nav: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => id.startsWith('M26-')).map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create, cols: c.cols || [],
    pick: !!c.pickRecord, pickDomain: (c.pickRecord && c.pickRecord.domain) || null,
    actions: (c.actions || []).map((a) => a.m),
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({
      name: f.name, readonly: !!f.readonly, required: !!f.required, domain: f.domain || null })) }])),
  by_screen: P03_FORM_CHIPS['M26:__by_screen__'] }));
"""

# What each page must let a person capture: the page's own "+ New" first,
# then every other record the page covers, by its form screen.
CAPTURES = {
    "1": ["M26-form-model", "M26-form-risk", "M26-form-guardrail"],
    "2": ["M26-form-version"],
    "3": ["M26-form-gate"],
    "4": ["M26-form-drift", "M26-form-fallback"],
    "5": ["M26-form-card", "M26-form-decision"],
    "6": ["M26-form-risk"],
    "7": ["M26-form-nlp", "M26-form-inference"],
}


@pytest.fixture(scope="module")
def m26(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m26_capture")
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
    """controllers/a11/m26.py SURFACES, read without importing Odoo."""
    tree = ast.parse((HERE.parent / "controllers" / "a11" / "m26.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "SURFACES" for t in node.targets
        ):
            return ast.literal_eval(node.value)
    raise AssertionError("SURFACES not found")


def _sub(m26, no):
    return next(s for s in m26["subs"] if s["no"] == no)


def _fields(m26, screen):
    return {f["name"]: f for f in m26["screens"][screen]["fields"]}


def test_every_page_is_classified(m26):
    assert sorted(s["no"] for s in m26["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m26, no):
    sub = _sub(m26, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]}
    missing = [form for form in [own, *others] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)
    for f in sub["forms"]:
        assert f["kind"] == "model_form", "chip %s opens %s" % (f["f"], f["kind"])


def test_the_genai_page_records_generative_risks_not_a_fake_model(m26):
    sub = _sub(m26, "6")
    assert sub["model"] == "fix.ml.ai.risk"
    assert sub["presets"] == {"category": "generative"}, "a risk made there must land there"
    assert "M26-form-model" not in {f["id"] for f in sub["forms"]}


def test_the_nlp_page_classifies_with_the_fault_classifier_only(m26):
    sub = _sub(m26, "7")
    assert ["model_id.kind", "=", "fault_classifier"] in sub["domain"]
    model = _fields(m26, "M26-form-nlp")["model_id"]
    assert model["domain"] == [["kind", "=", "fault_classifier"]]
    assert _fields(m26, "M26-form-nlp")["input_text"]["required"]


def test_explainability_picks_an_existing_version_or_run(m26):
    card = m26["screens"]["M26-form-card"]
    assert card["pick"] and _fields(m26, "M26-form-card")["model_card"]["required"]
    decision = m26["screens"]["M26-form-decision"]
    assert decision["pick"] and decision["pickDomain"] == [["state", "=", "computed"]]
    editable = {n for n, f in _fields(m26, "M26-form-decision").items() if not f["readonly"]}
    assert editable == {"final_value", "override_reason"}


def test_every_working_screen_sits_on_a_page(m26):
    placed = {sid for s in m26["subs"] for sid in s["screens"]}
    orphans = [
        sid
        for sid, cfg in m26["screens"].items()
        if cfg["kind"] == "model_list" and sid not in placed and sid != "M26-ai"
    ]
    assert not orphans, orphans


def test_every_list_is_in_the_navigation(m26):
    lists = [sid for sid, cfg in m26["screens"].items() if cfg["kind"] == "model_list"]
    assert set(lists) <= set(m26["nav"])


def test_a_list_offering_new_opens_a_form_of_its_own_model(m26):
    for sid, cfg in m26["screens"].items():
        if cfg["kind"] != "model_list" or cfg.get("create") is False:
            continue
        form = m26["by_screen"].get(sid)
        assert form, "%s offers + New but opens no form" % sid
        assert m26["screens"][form]["model"] == cfg["model"], sid


def test_deployment_patterns_list_creates_nothing(m26):
    """A version is deployed by promotion, never typed in as 'deployed'."""
    assert m26["screens"]["M26-deploy"]["create"] is False


def test_the_registry_moves_versions_by_action(m26):
    actions = set(m26["screens"]["M26-registry"]["actions"])
    assert {"action_evaluate", "action_request_promotion", "action_retire"} <= actions


@pytest.mark.parametrize(
    "form,needed",
    [
        (
            "M26-form-model",
            {
                "purpose",
                "consumer_modules",
                "accuracy_target",
                "fallback_definition",
                "risk_class",
                "owner_id",
                "review_date",
            },
        ),
        ("M26-form-drift", {"version_id", "feature_name", "psi", "ks_statistic", "threshold"}),
        (
            "M26-form-fallback",
            {"model_id", "consumer_module", "method", "consumer_behaviour", "outcome"},
        ),
        (
            "M26-form-risk",
            {"name", "category", "likelihood", "impact", "treatment", "owner_id", "review_date"},
        ),
    ],
)
def test_forms_capture_what_the_page_is_about(m26, form, needed):
    missing = needed - set(_fields(m26, form))
    assert not missing, "%s cannot capture %s" % (form, sorted(missing))


def test_engine_owned_fields_are_never_typed(m26):
    """state / approver / deploy date / drift score and the run's machine half
    are read-only on every form that shows them."""
    owned = {
        "M26-form-version": {"state", "approved_by", "deployed_at", "drift_score"},
        "M26-form-inference": {"state", "suggested_value", "overridden", "output_json"},
        "M26-form-nlp": {"state", "suggested_value", "output_json"},
        "M26-form-gate": {"checked_by", "checked_at"},
        "M26-form-drift": {"breached", "recorded_by"},
        "M26-form-fallback": {"tested_by"},
    }
    for form, names in owned.items():
        fields = _fields(m26, form)
        typed = [n for n in names if n in fields and not fields[n]["readonly"]]
        assert not typed, "%s lets the user type %s" % (form, typed)


def test_every_form_surface_declares_what_it_may_write(m26):
    """The write whitelist (R3) is what drops the echoed engine fields on save:
    every editable field of every M26 form is in it, and nothing engine-owned."""
    surfaces = _surfaces()
    for sid, cfg in m26["screens"].items():
        if cfg["kind"] != "model_form":
            continue
        writable = surfaces[cfg["model"]].get("writable")
        assert writable is not None, "%s (%s) declares no whitelist" % (sid, cfg["model"])
        editable = {f["name"] for f in cfg["fields"] if not f["readonly"]}
        assert editable <= writable, "%s cannot save %s" % (sid, sorted(editable - writable))
    version = surfaces["fix.ml.model.version"]["writable"]
    assert not {"state", "approved_by", "deployed_at", "drift_score"} & version


def test_the_server_serves_every_new_list():
    surfaces = _surfaces()
    for model in ("fix.ml.ai.risk", "fix.ml.drift.observation", "fix.ml.fallback.test"):
        assert model in surfaces, model


def test_the_fallback_report_shows_the_last_test():
    text = (HERE.parent / "controllers" / "a11" / "m26.py").read_text(encoding="utf-8")
    body = text[text.index("def fallback_status") : text.index("def genai_catalog")]
    assert "fix.ml.fallback.test" in body and '"last_test"' in body


def test_who_may_capture_the_evidence():
    acl = (ROOT / "domain/j_data_analytics/cd_ml_services/security/ir.model.access.csv").read_text(
        encoding="utf-8"
    )

    def rows(model):
        return {
            r.split(",")[3]: r.split(",")[4:8]
            for r in acl.splitlines()
            if ",model_%s," % model.replace(".", "_") in r
        }

    for model in ("fix.ml.fallback.test", "fix.ml.drift.observation", "fix.ml.ai.risk"):
        assert rows(model)["base.group_user"] == ["1", "0", "0", "0"], model
    assert rows("fix.ml.fallback.test")["group_ml_model_owner"][2] == "1"
    assert rows("fix.ml.drift.observation")["group_ml_data_scientist"][2] == "1"
    assert rows("fix.ml.ai.risk")["group_ml_model_owner"][:3] == ["1", "1", "1"]
