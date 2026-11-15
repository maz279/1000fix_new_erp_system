# M42 Supplier Relationship & Performance: every sub-module page captures the
# record it names (capture audit 2026-11-15).
#
# Before (HEAD 75711b30), evaluated with the engine's own fregCreate/fregPanels:
#   * 2 Segmentation had no "+ New" and no chip (create: false): the segment
#     was typed on the profile by anyone with write rights, although it sets
#     the review cadence and the authority a qualification needs;
#   * 5 Contracts & Price Lists "captured" a supplier DOCUMENT of type
#     contract: no agreement, agreed price, price change or consignment terms
#     existed (FR-SRM2-021..024, BRU-SRM2-14/15);
#   * 3, 4, 6 and 9 had a "+ New" but no chip for the other records they list
#     (activation gate, re-qualification, document, bank change, review,
#     screening); 4/6/9 named no form at all; the bank-change list sat on no
#     page;
#   * the profile had no classification (FR-SRM2-002) or risk tier
#     (FR-SRM2-004), there were no role-based contacts and no questionnaire
#     template (FR-SRM2-008, §10.1).
#
# Evaluated as the browser evaluates it: node runs the engine's own fregCreate
# and fregPanels over the real registry fragments (the M36/M41 fixture).
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
CONTROLLER = HERE.parent / "controllers" / "a06" / "m42.py"
WRITABLE_FILE = HERE.parent / "controllers" / "a06" / "writable.py"
VENDOR = HERE.parents[2] / "domain" / "e_supply_chain" / "cd_vendor_portal"

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
const mod = P03_MODULES.M42;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M42', map);
  const panels = fregPanels('M42', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M42:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M42.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: own || null, forms,
    reports: panels.reports.map((r) => ({ r, route: P03_REPORT_ROUTES['M42:' + r] || null })) };
});
console.log(JSON.stringify({ subs, forms: mod.forms,
  labelled: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => id.startsWith('M42-')).map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create, tabs: (c.tabs || []).map((t) => t.id),
    actions: (c.actions || []).map((a) => ({ m: a.m, kwarg: a.kwarg || null })),
    fields: (c.sections || []).flatMap((s) => (s.fields || []).map((f) => ({
      name: f.name, readonly: !!f.readonly, required: !!f.required, tab: s.tab || null }))) }])) }));
"""

# What each page lets a person capture: its own "+ New" first, then every
# other record the page covers, by form screen.
CAPTURES = {
    "1": ["M42-form-supplier", "M42-form-contact"],
    "2": ["M42-form-segment-review"],
    "3": [
        "M42-form-qualification",
        "M42-form-questionnaire",
        "M42-form-activation",
        "M42-form-requalification",
    ],
    "4": ["M42-form-document", "M42-form-bank-change"],
    "5": ["M42-form-agreement", "M42-form-price", "M42-form-price-change"],
    "6": ["M42-form-scorecard", "M42-form-review"],
    "7": ["M42-form-car"],
    "8": ["M42-form-risk"],
    "9": ["M42-form-screening"],
}

RECORDS = {
    "1": "fix.supplier",
    "2": "fix.supplier",
    "3": "fix.supplier.qualification",
    "4": "fix.supplier.document",
    "5": "fix.supplier.agreement",
    "6": "fix.supplier.performance",
    "7": "fix.supplier.car",
    "8": "fix.supplier.risk",
    "9": "fix.supplier.screening",
}

NEW_MODELS = (
    "fix.supplier.contact",
    "fix.supplier.segment.review",
    "fix.qualification.questionnaire",
    "fix.supplier.agreement",
    "fix.supplier.price.list",
    "fix.supplier.price.change",
)
# models whose rows carry a company (agreement terms and prices are commercial)
COMPANY_RULED = ("fix.supplier.agreement", "fix.supplier.price.list")


@pytest.fixture(scope="module")
def m42(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m42_capture")
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


def _model_methods():
    """{model: {method names}} defined in cd_vendor_portal's model files."""
    out = {}
    for path in (VENDOR / "models").glob("*.py"):
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


def _sub(m42, no):
    return next(s for s in m42["subs"] if s["no"] == no)


def test_every_page_is_classified(m42):
    assert sorted(s["no"] for s in m42["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m42, no):
    sub = _sub(m42, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]}
    missing = [form for form in [own, *others] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)


@pytest.mark.parametrize("no", sorted(RECORDS, key=int))
def test_each_page_lists_its_own_record(m42, no):
    assert _sub(m42, no)["model"] == RECORDS[no]


def test_contracts_page_captures_agreements_not_documents(m42):
    sub = _sub(m42, "5")
    models = {f["model"] for f in sub["forms"]}
    assert "fix.supplier.document" not in models
    assert {"fix.supplier.agreement", "fix.supplier.price.list"} <= models


def test_each_captured_record_is_listed_on_its_page(m42):
    for sub in m42["subs"]:
        listed = {m42["screens"][s]["model"] for s in sub["screens"] if s in m42["screens"]}
        for f in sub["forms"]:
            assert f["model"] in listed, "page %s captures %s but lists none" % (
                sub["no"],
                f["model"],
            )


def test_every_working_screen_sits_on_a_page(m42):
    placed = {sid for s in m42["subs"] for sid in s["screens"]}
    orphans = [
        sid
        for sid, cfg in m42["screens"].items()
        if cfg["kind"] == "model_list" and sid not in placed
    ]
    assert not orphans, orphans


def test_every_form_chip_resolves(m42):
    for sub in m42["subs"]:
        for f in sub["forms"]:
            assert f["id"] and f["kind"] == "model_form", (sub["no"], f)


def test_every_served_action_exists_on_its_model():
    methods = _model_methods()
    for model, acts in _surfaces().items():
        missing = acts - methods.get(model, set())
        assert not missing, "%s serves %s, which the model lacks" % (model, sorted(missing))


def test_every_list_action_is_served(m42):
    surfaces = _surfaces()
    for sid, cfg in m42["screens"].items():
        if cfg["kind"] != "model_list" or not cfg["actions"]:
            continue
        served = surfaces.get(cfg["model"], set())
        for act in cfg["actions"]:
            assert act["m"] in served, "%s offers %s, not served" % (sid, act["m"])


@pytest.mark.parametrize("model", NEW_MODELS)
def test_new_registers_are_served_and_whitelisted(m42, model):
    assert model in _surfaces()
    forms = [
        c for c in m42["screens"].values() if c["kind"] == "model_form" and c["model"] == model
    ]
    assert forms, "%s has no form" % model
    typed = {f["name"] for c in forms for f in c["fields"] if not f["readonly"]}
    assert _writable()[model] == typed


def test_decisions_and_evidence_are_never_typed():
    """States, approvers and snapshots move only through their actions."""
    never = {
        "fix.supplier.segment.review": {"state", "from_segment", "proposed_by_id", "decided_by_id"},
        "fix.supplier.agreement": {"state", "approved_by_id", "approved_on", "terminated_reason"},
        "fix.supplier.price.list": {"state", "approved_by_id", "approved_on", "source_change_id"},
        "fix.supplier.price.change": {
            "state",
            "old_price",
            "requested_by_id",
            "decided_by_id",
            "new_price_id",
        },
        "fix.supplier": {"status", "payment_block", "bank_account_id"},
    }
    writable = _writable()
    for model, names in never.items():
        assert not (writable.get(model, set()) & names), (model, writable[model] & names)


def test_profile_captures_classification_and_risk_tier(m42):
    fields = {f["name"]: f for f in m42["screens"]["M42-form-supplier"]["fields"]}
    assert fields["classification"]["required"]
    assert "risk_tier" in fields
    assert "questionnaire_id" in {
        f["name"] for f in m42["screens"]["M42-form-qualification"]["fields"]
    }


def test_the_agreement_form_is_tabbed(m42):
    """More than 15 fields: Dynamics-style tabs, every section on a tab."""
    cfg = m42["screens"]["M42-form-agreement"]
    assert len(cfg["fields"]) > 15
    assert cfg["tabs"] == ["agreement", "commercial", "consignment"]
    assert all(f["tab"] in cfg["tabs"] for f in cfg["fields"])


def test_reject_actions_ask_for_the_reason(m42):
    for sid in ("M42-segment-reviews", "M42-price-changes", "M42-agreements"):
        acts = {a["m"]: a for a in m42["screens"][sid]["actions"]}
        rejecting = acts.get("action_reject") or acts.get("action_terminate")
        assert rejecting and rejecting["kwarg"] == "reason", sid


def test_new_models_are_secured():
    acl = (VENDOR / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    rules = (VENDOR / "security" / "fix_isolation_rules.xml").read_text(encoding="utf-8")
    for model in NEW_MODELS:
        xmlid = "model_" + model.replace(".", "_")
        rows = [r.split(",") for r in acl.splitlines() if (",%s," % xmlid) in r]
        assert rows, model
        # nobody may delete; a plain employee only reads
        assert all(r[-1].strip() == "0" for r in rows), model
        plain = [r for r in rows if r[3] == "base.group_user"]
        assert plain and plain[0][4:8] == ["1", "0", "0", "0"], model
    for model in COMPANY_RULED:
        assert 'ref="model_%s"' % model.replace(".", "_") in rules, "%s has no company rule" % model


def test_the_new_file_loads_after_the_models_it_extends():
    init = (VENDOR / "models" / "__init__.py").read_text(encoding="utf-8")
    assert init.index("fix_supplier_controls") < init.index("fix_supplier_terms")


def test_every_screen_on_a_page_has_a_navigation_label(m42):
    labelled = set(m42["labelled"])
    unlabelled = sorted(
        sid
        for sub in m42["subs"]
        for sid in sub["screens"]
        if sid in m42["screens"]
        and m42["screens"][sid]["kind"] == "model_list"
        and sid not in labelled
    )
    assert not unlabelled, unlabelled
