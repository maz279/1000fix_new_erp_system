# M11 Pricing & Rate Cards: every sub-module page offers the button that
# captures its record (audit 2026-11-13).
#
# Pages 1 (Pricing Engine) and 6 (Brand Reimbursement) offered nothing, 9 and
# 11 no form chip. Customer/Contract Pricing listed price books, and the Rate
# Card form had no contract number, so a contract rate (the engine's tier-99
# lane, BRU-PRC-11) could not be recorded anywhere. Rate Cards and Parts
# Pricing each listed every card. Brand Reimbursement listed M09's warranty
# claims under "rates": the brand rate card the spec gives M11 (FR-PRC-015)
# did not exist. Floors, rate/floor changes and the discount ladder sat on no
# page.
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
CONTROLLER = ROOT / "controllers" / "a04" / "m11.py"
WRITABLE = ROOT / "controllers" / "a04" / "writable.py"

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
const mod = P03_MODULES.M11;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M11', map);
  const forms = fregPanels('M11', mod, map).forms.map((f) => {
    const id = P03_FORM_CHIPS['M11:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const lists = (map.screens || []).map((id) => ({ id, cfg: P03_DATA_SCREENS[id] || {} }))
    .filter((x) => x.cfg.kind === 'model_list')
    .map((x) => ({ id: x.id, model: x.cfg.model, create: x.cfg.create !== false, empty: !!x.cfg.empty,
      domain: x.cfg.domain || [], actions: (x.cfg.actions || []).map((a) => a.m) }));
  return { no: s[0], model: map.model || null, domain: map.domain || [], create, forms, lists };
});
const S = P03_DATA_SCREENS;
const cfgOf = (id) => S[id] || {};
const fields = (id) => (cfgOf(id).sections || []).flatMap((sec) => (sec.fields || []).map((f) => f.name));
const emptyTabs = (id) => (cfgOf(id).tabs || []).map((t) => t.id).filter((tab) =>
  !(cfgOf(id).sections || []).some((sec) => sec.tab === tab && (sec.fields || []).length));
const navIds = mod.groups.flatMap((g) => g.screens.map((s) => s.id));
const mapped = new Set(mod.freg.sub.flatMap((s) => s[3].screens || []));
console.log(JSON.stringify({
  subs,
  cardFields: fields('M11-form-card'),
  cardEmptyTabs: emptyTabs('M11-form-card'),
  brandFormFields: fields('M11-form-brand-rate'),
  brandScreen: { kind: cfgOf('M11-brand').kind || null, model: cfgOf('M11-brand').model || null },
  unmappedLists: navIds.filter((id) => S[id] && S[id].kind === 'model_list' && !mapped.has(id)),
  kpis: mod.kpis,
}));
"""

# How each page's record is captured. 'form': a "+ New" or a chip that opens
# an in-workspace form for a record a person legitimately records.
CAPTURE = {
    "1": "form",  # explanation is engine-written; the what-if simulation is the input
    "2": "form",  # Price Book + Price Book Version
    "3": "form",  # labour / service rate card
    "4": "form",  # parts rate card + price floor
    "5": "form",  # contract rate card (tier 99)
    "6": "form",  # brand reimbursement rate
    "7": "form",  # discount approval request + ladder band + floor
    "8": "form",  # promotion
    "9": "form",  # dynamic price rule
    "10": "form",  # simulation request
    "11": "form",  # version + price change request
}


@pytest.fixture(scope="module")
def m11(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m11_capture")
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


def _sub(m11, no):
    return next(s for s in m11["subs"] if s["no"] == no)


def test_every_page_is_classified(m11):
    assert sorted(s["no"] for s in m11["subs"]) == sorted(CAPTURE)


@pytest.mark.parametrize("no", sorted(CAPTURE, key=int))
def test_each_page_offers_its_capture(m11, no):
    sub = _sub(m11, no)
    opening = [f for f in sub["forms"] if f["opens"]]
    assert sub["create"] or opening, "page %s has no + New and no form chip" % no
    for f in sub["forms"]:
        assert f["kind"] == "model_form", "chip %s opens %s" % (f["f"], f["kind"])


def test_pricing_engine_never_offers_typing_an_explanation(m11):
    """BRU-PRC-02: the trace is the engine's; the page offers the what-if."""
    sub = _sub(m11, "1")
    assert sub["create"] is None
    assert [f["model"] for f in sub["forms"]] == ["fix.price.simulation"]
    explanation = next(lst for lst in sub["lists"] if lst["model"] == "fix.price.explanation")
    assert not explanation["create"] and explanation["empty"]


def test_rate_card_pages_are_sliced_and_preset(m11):
    labour, parts, contract = (_sub(m11, n) for n in ("3", "4", "5"))
    assert ["line_type", "!=", "part"] in labour["domain"]
    assert parts["create"]["presets"] == {"line_type": "part"}
    assert contract["model"] == "fix.rate.card"
    assert contract["create"]["presets"] == {"min_tier": 99}


def test_a_contract_rate_can_be_recorded(m11):
    assert "contract_no" in m11["cardFields"]
    assert "min_tier" in m11["cardFields"]
    assert "contract_no" in ast.literal_eval(_writable("fix.rate.card"))


def test_rate_card_form_has_no_empty_tabs(m11):
    assert m11["cardEmptyTabs"] == []


def test_brand_reimbursement_records_the_brand_rate(m11):
    sub = _sub(m11, "6")
    assert sub["model"] == "fix.brand.reimbursement.rate"
    assert sub["create"]["screen"] == "M11-form-brand-rate"
    assert m11["brandScreen"] == {"kind": "model_list", "model": "fix.brand.reimbursement.rate"}
    for name in ("brand_id", "repair_level", "labour_rate", "parts_markup_pct", "valid_from"):
        assert name in m11["brandFormFields"]


def test_every_list_screen_sits_on_a_page(m11):
    assert m11["unmappedLists"] == []


def test_brand_kpi_has_a_source(m11):
    tile = next(k for k in m11["kpis"] if k["m"] == "brand_reimb_rates")
    assert tile.get("src", True) is not False


def _surfaces():
    tree = ast.parse(CONTROLLER.read_text(encoding="utf-8"))
    node = next(
        n.value
        for n in tree.body
        if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "SURFACES"
    )
    return ast.literal_eval(node)


def _writable(model):
    tree = ast.parse(WRITABLE.read_text(encoding="utf-8"))
    table = next(
        n.value
        for n in tree.body
        if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "WRITABLE"
    )
    for key, value in zip(table.keys, table.values, strict=True):
        if ast.literal_eval(key) == model:
            return ast.unparse(value.args[0])
    raise AssertionError("%s has no write whitelist" % model)


def test_brand_rate_lifecycle_is_whitelisted():
    actions = _surfaces()["fix.brand.reimbursement.rate"]["actions"]
    assert actions == {"action_submit", "action_recall_approval", "action_retire"}
    # the state, version and release stamps are never typed
    allowed = ast.literal_eval(_writable("fix.brand.reimbursement.rate"))
    assert not allowed & {"state", "version", "valid_to", "approved_by", "approved_at"}
