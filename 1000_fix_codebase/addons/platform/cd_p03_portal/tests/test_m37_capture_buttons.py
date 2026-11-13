# M37 Product & Service Catalogue: every sub-module page offers the button
# that captures ITS record (audit 2026-11-13).
#
# Before: Typed Taxonomy, Product Hierarchy, Tax & Rev-Rec and Lifecycle had no
# capture; rBOM & SRT and Fault Taxonomy offered only a chip because their
# lists refused + New although the forms worked; Repair Operations and Part
# Identity both captured rBOM lines; Service Definitions and the Protection
# Plan list showed every one of the 16,178 items on fix_real (all parts,
# accessories or finished goods) and their forms started with no type; Kits
# and Brands had no chip; rental SKUs and refurb grades sat on no page, and
# the refurb-grade list offered a + New no role may save.
#
# Evaluated as the browser evaluates it: node runs the engine's own fregCreate
# and fregPanels over the real registry fragments (the M02 guard's fixture).
from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "static" / "src"

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
const mod = P03_MODULES.M37;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M37', map);
  const forms = fregPanels('M37', mod, map).forms.map((f) => {
    const id = P03_FORM_CHIPS['M37:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const lists = (map.screens || []).map((id) => ({ id, cfg: P03_DATA_SCREENS[id] || {} }))
    .filter((x) => x.cfg.kind === 'model_list')
    .map((x) => ({ id: x.id, model: x.cfg.model, create: x.cfg.create !== false, empty: !!x.cfg.empty,
      actions: (x.cfg.actions || []).map((a) => a.m) }));
  return { no: s[0], model: map.model || null, screens: map.screens || [],
    create: create && (create.screen || (create.module ? 'module' : null)),
    presets: (create && create.presets) || null, forms, lists };
});
const S = P03_DATA_SCREENS;
console.log(JSON.stringify({ subs,
  nav: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  screens: Object.fromEntries(Object.entries(S).filter(([id]) => id.startsWith('M37-') || id === 'M51-form-treatment').map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create, back: c.back || null, empty: !!c.empty,
    domain: c.domain || [],
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({ name: f.name, value: f.value, readonly: !!f.readonly })) }])),
  by_screen: P03_FORM_CHIPS['M37:__by_screen__'] }));
"""


# How each page's record is captured. 'form': a "+ New" or a chip opening an
# in-workspace form. 'workflow': existing records move by list actions only.
CAPTURE = {
    "1": "form",  # catalogue item (module button)
    "2": "form",  # category node (product-manager role) - chip
    "3": "form",  # service definition
    "4": "form",  # rBOM line
    "5": "form",  # repair operation = labour-only item with its SRT
    "6": "form",  # service kit
    "7": "form",  # category node - chip
    "8": "form",  # brand (+ its device models)
    "9": "form",  # fault code
    "10": "form",  # spare part item
    "11": "form",  # contract template, protection plan, rental SKU
    "12": "form",  # tariff code -> VAT treatment (M51's form) - chip
    "13": "workflow",  # submit / publish / restrict / discontinue / revise
}


@pytest.fixture(scope="module")
def m37(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m37_capture")
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


def _sub(m37, no):
    return next(s for s in m37["subs"] if s["no"] == no)


def _field(m37, screen, name):
    return next(f for f in m37["screens"][screen]["fields"] if f["name"] == name)


def _acl(path, model_xmlid):
    rows = [
        r.split(",")
        for r in (HERE.parents[2] / path).read_text(encoding="utf-8").splitlines()
        if model_xmlid in r
    ]
    return {r[3]: r[4:8] for r in rows}


def test_every_page_is_classified(m37):
    assert sorted(s["no"] for s in m37["subs"]) == sorted(CAPTURE)


@pytest.mark.parametrize("no", sorted(CAPTURE, key=int))
def test_each_page_offers_its_capture(m37, no):
    sub = _sub(m37, no)
    opening = [f for f in sub["forms"] if f["opens"]]
    if CAPTURE[no] == "form":
        assert sub["create"] or opening, "page %s has no + New and no form chip" % no
        for f in sub["forms"]:
            assert f["kind"] == "model_form", "chip %s opens %s" % (f["f"], f["kind"])
    else:
        assert not sub["create"] and not opening
        acting = [lst for lst in sub["lists"] if lst["actions"]]
        assert acting, "page %s: a workflow page needs a list that moves records" % no


def test_every_working_screen_sits_on_a_page(m37):
    """A list on no page cannot be reached from the register (report screens
    are reached by their report chips)."""
    placed = {sid for s in m37["subs"] for sid in s["screens"]}
    orphans = [
        sid
        for sid, cfg in m37["screens"].items()
        if cfg["kind"] == "model_list" and sid not in placed
    ]
    assert not orphans, orphans


def test_a_list_offering_new_opens_a_form_of_its_own_model(m37):
    by_screen = m37["by_screen"]
    for sid, cfg in m37["screens"].items():
        if cfg["kind"] != "model_list" or cfg.get("create") is False:
            continue
        form = by_screen.get(sid)
        assert form, "%s offers + New but opens no form" % sid
        assert m37["screens"][form]["model"] == cfg["model"], sid


@pytest.mark.parametrize(
    "screen,types",
    [
        ("M37-services", ["service", "inspection"]),
        ("M37-operations", ["labour"]),
        ("M37-parts-id", ["part"]),
        ("M37-protection", ["protection"]),
    ],
)
def test_typed_lists_show_only_their_type(m37, screen, types):
    cfg = m37["screens"][screen]
    assert cfg["model"] == "fix.catalogue.item"
    clause = next(c for c in cfg["domain"] if c[0] == "item_type")
    assert (clause[2] if isinstance(clause[2], list) else [clause[2]]) == types


def test_repair_operations_capture_a_labour_item_not_an_rbom_line(m37):
    sub = _sub(m37, "5")
    assert sub["model"] == "fix.catalogue.item"
    assert sub["create"] == "M37-form-service"
    assert sub["presets"] == {"item_type": "labour"}


def test_part_identity_captures_a_part_not_an_rbom_line(m37):
    sub = _sub(m37, "10")
    assert sub["model"] == "fix.catalogue.item"
    assert sub["create"] == "M37-item"
    assert sub["presets"] == {"item_type": "part"}


def test_new_typed_items_start_with_their_type(m37):
    assert _field(m37, "M37-form-service", "item_type")["value"] == "service"
    assert _field(m37, "M37-form-protection", "item_type")["value"] == "protection"


@pytest.mark.parametrize("no", ["4", "9"])
def test_rbom_and_fault_pages_have_a_new_button(m37, no):
    assert _sub(m37, no)["create"], "page %s offers only a chip" % no


def test_kits_brands_and_templates_have_chips(m37):
    assert "Service Kit" in [f["f"] for f in _sub(m37, "6")["forms"]]
    assert "Brand & Authorisation" in [f["f"] for f in _sub(m37, "8")["forms"]]
    chips = {f["f"] for f in _sub(m37, "11")["forms"]}
    assert {"Contract Template", "Protection Product Template", "Rental SKU"} <= chips
    assert {"M37-rental-sku", "M37-refurb-grade"} <= set(_sub(m37, "11")["screens"])


@pytest.mark.parametrize("no", ["2", "7"])
def test_category_pages_reach_the_category_form(m37, no):
    chip = next(f for f in _sub(m37, no)["forms"] if f["f"] == "Catalogue Category")
    assert chip["model"] == "product.category" and chip["opens"]
    # product.category is created by product managers only: a chip, no + New
    assert _sub(m37, no)["create"] is None


def test_tax_page_opens_m51_vat_treatment(m37):
    chip = next(f for f in _sub(m37, "12")["forms"] if f["f"] == "VAT Treatment")
    assert chip["id"] == "M51-form-treatment" and chip["model"] == "fix.vat.treatment"


def test_refurb_grades_offer_no_new_nobody_may_save():
    acl = _acl("platform/cd_catalogue/security/ir.model.access.csv", "model_fix_refurb_grade,")
    assert all(perms[2] == "0" for perms in acl.values()), acl


def test_refurb_grade_list_offers_no_new(m37):
    assert m37["screens"]["M37-refurb-grade"].get("create") is False


def test_category_form_fields_are_whitelisted():
    from importlib import util

    spec = util.spec_from_file_location(
        "_a04w", HERE.parent / "controllers" / "a04" / "writable.py"
    )
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert {"name", "parent_id"} <= set(mod.WRITABLE["product.category"])
