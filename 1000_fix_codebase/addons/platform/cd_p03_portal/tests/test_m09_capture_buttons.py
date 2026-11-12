# M09 Warranty & Claims: every sub-module page offers the button that
# captures its record (audit 2026-11-13).
#
# Protection Products, Evidence Assembly and Recalls listed records the models
# let a person create, behind lists marked create:false - no "+ New". The
# Reconciliation page listed M53's computed provisions, and no page could
# record a brand's remittance, so an approved claim could never become
# remitted or closed. Repair Warranty offered "+ New Brand Claim", though
# 1000FiX's own repair warranty is never claimed from a brand. The "Protection
# Policy" chip opened the IAS 37 provision policy.
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
ROOT = HERE.parent
SRC = ROOT / "static" / "src"
CONTROLLER = ROOT / "controllers" / "a04" / "m09.py"

_spec = importlib.util.spec_from_file_location(
    "_estate_pages", HERE / "test_estate_module_pages.py"
)
_estate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_estate)

LISTS = ("model_list", "so_list")

PROBE = """
import * as M from './meta.mjs';
const { P03_MODULES, P03_MODULE_CREATE, P03_FORM_CHIPS, P03_FORM_MODELS, P03_DATA_SCREENS } = M;
function %(create)s
function %(panels)s
const mod = P03_MODULES.M09;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M09', map);
  const forms = fregPanels('M09', mod, map).forms.map((f) => {
    const id = P03_FORM_CHIPS['M09:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const lists = (map.screens || []).map((id) => ({ id, cfg: P03_DATA_SCREENS[id] || {} }))
    .filter((x) => %(lists)s.includes(x.cfg.kind))
    .map((x) => ({ id: x.id, kind: x.cfg.kind, model: x.cfg.model || null,
      create: x.cfg.kind === 'model_list' && x.cfg.create !== false, empty: !!x.cfg.empty,
      actions: (x.cfg.actions || []).map((a) => a.m) }));
  return { no: s[0], model: map.model || null, create, forms, lists };
});
const S = P03_DATA_SCREENS;
console.log(JSON.stringify({ subs, formModels: Object.fromEntries(
  Object.entries(P03_FORM_MODELS).filter(([k]) => k.startsWith('M09:'))),
  screens: Object.fromEntries(
  Object.entries(S).filter(([id]) => id.startsWith('M09-')).map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create, title: c.title || null,
    back: c.back || null, empty: !!c.empty, actions: (c.actions || []).map((a) => a.m),
    asks: (c.actions || []).map((a) => (a.asks || []).map((q) => q.kwarg)) }])) }));
"""

# How each page's record is captured. 'form': a "+ New" or a chip that opens
# an in-workspace form. 'actions': buttons on one of its lists write it.
# 'none': nothing is typed in - the verdict or score is computed.
CAPTURE = {
    "1": "form",  # Warranty Register Entry (+ Warranty Transfer)
    "2": "actions",  # Request Verification on the register
    "3": "actions",  # Open Comeback / Request Zero-Charge Rework (M01 order)
    "4": "none",  # the entitlement verdict is computed at intake
    "5": "form",  # Protection Product (+ Protection Policy = extended cover)
    "6": "actions",  # Assemble Evidence, Key OEM decision ...
    "7": "form",  # Claim Evidence Item
    "8": "form",  # Brand Claim
    "9": "form",  # Claim Appeal
    "10": "actions",  # Record Bank Receipt / Note Brand Remittance Advice
    "11": "form",  # Recall Campaign
    "12": "none",  # fraud signals are computed from claims
}


@pytest.fixture(scope="module")
def m09(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m09_capture")
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
            "lists": json.dumps(list(LISTS)),
        },
        "utf-8",
    )
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our own probe file
        [node, str(probe)], capture_output=True, encoding="utf-8", check=True, timeout=120
    )
    return json.loads(out.stdout)


def _sub(m09, no):
    return next(s for s in m09["subs"] if s["no"] == no)


def _surfaces():
    tree = ast.parse(CONTROLLER.read_text(encoding="utf-8"))
    node = next(
        n.value
        for n in tree.body
        if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "SURFACES"
    )
    return ast.literal_eval(node)


def test_every_page_is_classified(m09):
    assert sorted(s["no"] for s in m09["subs"]) == sorted(CAPTURE)


@pytest.mark.parametrize("no", sorted(CAPTURE, key=int))
def test_each_page_offers_its_capture(m09, no):
    sub = _sub(m09, no)
    opening = [f for f in sub["forms"] if f["opens"]]
    kind = CAPTURE[no]
    for f in sub["forms"]:
        assert f["kind"] == "model_form", "chip %s opens %s" % (f["f"], f["kind"])
    if kind == "form":
        assert sub["create"] or opening, "page %s has no + New and no form chip" % no
    elif kind == "actions":
        assert any(lst["actions"] for lst in sub["lists"]), "page %s: no list writes it" % no
    else:
        assert not sub["create"] and not opening, "page %s would let a person type in %s" % (
            no,
            sub["model"],
        )


@pytest.mark.parametrize(
    "screen", ["M09-brandrules", "M09-evidence", "M09-recalls", "M09-appeals", "M09-register"]
)
def test_lists_of_person_entered_records_offer_new(m09, screen):
    # each model's create() takes a clerk's or officer's entry
    # an unset `create` (absent from the JSON) means the list offers + New
    assert m09["screens"][screen].get("create") is not False


def test_repair_warranty_is_never_a_brand_claim(m09):
    sub = _sub(m09, "3")
    assert sub["model"] == "fix.service.order"
    assert not sub["create"], "a repair warranty comeback is opened on the delivered order"
    assert not any(f["model"] == "fix.warranty.claim" for f in sub["forms"])
    actions = {a for lst in sub["lists"] for a in lst["actions"]}
    assert "action_reopen_comeback" in actions


def test_repair_warranty_report_reads_service_orders():
    tree = ast.parse(CONTROLLER.read_text(encoding="utf-8"))
    fn = next(
        n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "warranty_repairs"
    )
    src = ast.unparse(fn)
    assert "fix.service.order" in src and "_claims(" not in src


def test_reconciliation_records_the_brands_money(m09):
    sub = _sub(m09, "10")
    assert sub["model"] == "fix.warranty.claim"
    remit = m09["screens"]["M09-remit"]
    assert {"action_record_remittance", "action_record_remittance_advice"} <= set(remit["actions"])
    # both server methods take (amount, bank_ref)
    for asks in remit["asks"][:2]:
        assert asks == ["amount", "bank_ref"]
    allowed = _surfaces()["fix.warranty.claim"]["actions"]
    assert {"action_record_remittance", "action_record_remittance_advice"} <= allowed


def test_protection_policy_chip_is_the_cover_not_the_reserve_basis(m09):
    assert m09["formModels"]["M09:Protection Policy"] == "fix.warranty"
    assert m09["formModels"]["M09:Provision Policy"] == "fix.warranty.provision.policy"
    assert m09["screens"]["M09-form-policy"]["title"] != "Protection Policy"


def test_product_form_returns_to_the_product_list(m09):
    assert m09["screens"]["M09-form-wproduct"]["back"] == "M09-brandrules"


def test_every_chip_names_its_model(m09):
    """FORM_MODELS and FORM_CHIPS agree, so a chip never opens another record."""
    screens = m09["screens"]
    for sub in m09["subs"]:
        for f in sub["forms"]:
            assert m09["formModels"].get("M09:" + f["f"]) == f["model"], f
            assert screens[f["id"]]["kind"] == "model_form"
