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
# Second pass (2026-11-14): Typed Taxonomy and Product Hierarchy still had
# only a chip; Tax & Rev-Rec opened M51's tariff master because the item had
# no tax, HS or revenue class; Lifecycle captured nothing although FR-CAT-044
# publishes channel projections; SRT baselines, part cross-references and
# brand claim codes had no record at all.
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
  screens: Object.fromEntries(Object.entries(S).filter(([id]) => id.startsWith('M37-') || id === 'M51-form-treatment' || id === 'M09-form-wproduct').map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create, back: c.back || null, empty: !!c.empty,
    pick: !!c.pickRecord, lines: (c.lines && c.lines.field) || null,
    grids: (c.grids || []).map((g) => g.field),
    domain: c.domain || [],
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({ name: f.name, value: f.value, readonly: !!f.readonly })) }])),
  by_screen: P03_FORM_CHIPS['M37:__by_screen__'] }));
"""


# How each page's record is captured. 'form': a "+ New" or a chip opening an
# in-workspace form. 'workflow': existing records move by list actions only.
CAPTURE = {
    "1": "form",  # catalogue item (module button)
    "2": "form",  # category node (product-manager role)
    "3": "form",  # service definition
    "4": "form",  # rBOM line
    "5": "form",  # repair operation = labour-only item with its SRT
    "6": "form",  # service kit
    "7": "form",  # variant attribute + its values; category chip
    "8": "form",  # brand (+ its device models)
    "9": "form",  # fault code
    "10": "form",  # spare part item
    "11": "form",  # contract template, protection plan, rental SKU
    "12": "form",  # the item's VAT / SD / HS / revenue class (pick the item)
    "13": "form",  # a versioned channel publication; lifecycle by list actions
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


# --- second pass (2026-11-14): every page has a + New of its own -------------
OWN_NEW = {
    "2": ("M37-form-category", "product.category"),
    "4": ("M37-form-rbom", "fix.rbom.line"),
    "7": ("M37-form-attribute", "product.attribute"),
    "12": ("M37-form-taxclass", "fix.catalogue.item"),
    "13": ("M37-form-publication", "fix.catalogue.publication"),
}


@pytest.mark.parametrize("no", sorted(CAPTURE, key=int))
def test_every_page_has_a_new_button(m37, no):
    assert _sub(m37, no)["create"], "page %s offers only chips" % no


@pytest.mark.parametrize("no", sorted(OWN_NEW, key=int))
def test_second_pass_pages_capture_their_own_record(m37, no):
    form, model = OWN_NEW[no]
    assert _sub(m37, no)["create"] == form
    assert m37["screens"][form]["model"] == model


def test_tax_page_classifies_the_item_and_keeps_m51_chip(m37):
    sub = _sub(m37, "12")
    assert "M37-taxclass" in sub["screens"]
    chip = next(f for f in sub["forms"] if f["f"] == "VAT Treatment")
    assert chip["id"] == "M51-form-treatment" and chip["model"] == "fix.vat.treatment"
    names = {f["name"] for f in m37["screens"]["M37-form-taxclass"]["fields"]}
    assert {"hs_code", "vat_class", "sd_applicable", "revenue_recognition"} <= names
    assert m37["screens"]["M37-form-taxclass"]["pick"], "the form must first pick the item"


@pytest.mark.parametrize(
    "no,chip,screen",
    [
        ("4", "SRT Baseline", "M37-srt-baselines"),
        ("5", "SRT Baseline", "M37-srt-baselines"),
        ("10", "Part Cross-Reference", "M37-part-xref"),
        ("13", "Channel Publication", "M37-publications"),
    ],
)
def test_spec_records_are_on_their_pages(m37, no, chip, screen):
    sub = _sub(m37, no)
    assert screen in sub["screens"]
    f = next(f for f in sub["forms"] if f["f"] == chip)
    assert f["opens"] and f["kind"] == "model_form"


def test_srt_list_moves_baselines_by_actions(m37):
    lst = next(x for x in _sub(m37, "4")["lists"] if x["id"] == "M37-srt-baselines")
    assert {"action_propose", "action_approve", "action_reject"} <= set(lst["actions"])


def test_item_forms_carry_the_classification(m37):
    for form in ("M37-item", "M37-form-service", "M37-form-protection"):
        names = {f["name"] for f in m37["screens"][form]["fields"]}
        assert {"hs_code", "vat_class", "revenue_recognition"} <= names, form
    item = {f["name"] for f in m37["screens"]["M37-item"]["fields"]}
    assert {"repair_level", "provenance_grade", "hazard_class", "hazard_handling"} <= item


def test_fault_form_maps_brand_claim_codes(m37):
    assert m37["screens"]["M37-form-fault"]["lines"] == "brand_code_ids"


def test_new_forms_are_whitelisted():
    from importlib import util

    for area, model, needed in (
        (
            "a04",
            "fix.catalogue.item",
            {
                "hs_code",
                "vat_class",
                "sd_applicable",
                "revenue_recognition",
                "repair_level",
                "provenance_grade",
                "hazard_class",
                "hazard_handling",
            },
        ),
        ("a04", "fix.srt.baseline", {"item_id", "minutes", "repair_level", "reason"}),
        (
            "a04",
            "fix.part.crossref",
            {"part_item_id", "alt_item_id", "relation_type", "quality_note"},
        ),
        ("a04", "fix.catalogue.publication", {"channel", "note"}),
        ("a04", "product.attribute", {"name", "value_ids"}),
        ("a02", "fix.fault.code", {"brand_code_ids"}),
    ):
        spec = util.spec_from_file_location(
            "_w_" + area, HERE.parent / "controllers" / area / "writable.py"
        )
        mod = util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert needed <= set(mod.WRITABLE[model]), (area, model)


def test_publication_snapshot_fields_are_not_writable():
    from importlib import util

    spec = util.spec_from_file_location(
        "_a04w2", HERE.parent / "controllers" / "a04" / "writable.py"
    )
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert not {"version", "item_count", "content_hash", "published_at"} & set(
        mod.WRITABLE["fix.catalogue.publication"]
    )


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


# --- third pass (2026-11-19): the forms behind the buttons hold the spec record ---


def _editable(m37, screen):
    return {f["name"] for f in m37["screens"][screen]["fields"] if not f["readonly"]}


def _writable(area="a04"):
    from importlib import util

    spec = util.spec_from_file_location(
        "_%sw3" % area, HERE.parent / "controllers" / area / "writable.py"
    )
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.WRITABLE


SERVICE_DEFINITION = {
    # FR-CAT-013
    "scope_of_work",
    "inclusions",
    "exclusions",
    "prerequisites",
    "deliverables",
    # FR-CAT-015/018/019/020/025/026
    "required_competency_id",
    "requires_certification",
    "repair_warranty_days",
    "requires_customer_consent",
    "requires_data_declaration",
    "requires_regulatory_cert",
    "default_sla_policy_id",
    "fault_code_ids",
    "tooling_required",
    "workstation_class",
}


def test_service_definition_form_holds_the_service_definition(m37):
    """Pages 3 and 5: the button opened a form with a name, a type and a
    labour time - none of FR-CAT-013..020."""
    assert _editable(m37, "M37-form-service") >= SERVICE_DEFINITION
    # FR-CAT-014/016: delivery modes with their standard durations
    assert "mode_duration_ids" in m37["screens"]["M37-form-service"]["grids"]
    assert SERVICE_DEFINITION | {"mode_duration_ids"} <= set(_writable()["fix.catalogue.item"])
    for no in ("3", "5"):
        assert _sub(m37, no)["create"] == "M37-form-service"


def test_protection_template_shows_cover_not_labour_time(m37):
    fields_ = {f["name"] for f in m37["screens"]["M37-form-protection"]["fields"]}
    assert not fields_ & {"standard_labour_time", "srt_observed_minutes"}
    chip = next(f for f in _sub(m37, "11")["forms"] if f["f"] == "Protection Product (Cover Terms)")
    assert chip["id"] == "M09-form-wproduct" and chip["opens"]
    assert {"coverage_scope", "exclusions", "duration_months", "claim_limit"} <= _editable(
        m37, "M09-form-wproduct"
    )


@pytest.mark.parametrize(
    "no,form,screen,model",
    [
        ("7", "Attribute Set", "M37-attribute-sets", "fix.catalogue.attribute.set"),
        ("8", "Model Compatibility", "M37-model-compat", "fix.model.compatibility"),
        ("9", "Fault Symptom", "M37-symptoms", "fix.fault.symptom"),
        ("11", "Subscription Plan", "M37-plan-defs", "fix.subscription.plan.def"),
    ],
)
def test_new_spec_records_are_captured_on_their_page(m37, no, form, screen, model):
    sub = _sub(m37, no)
    chip = next(f for f in sub["forms"] if f["f"] == form)
    assert chip["opens"] and chip["model"] == model
    assert any(lst["id"] == screen and lst["create"] for lst in sub["lists"])
    assert screen in m37["nav"]
    assert _editable(m37, chip["id"]) <= set(_writable()[model])


def test_rbom_line_is_per_model_with_criticality_and_alternates(m37):
    assert {"device_model_id", "criticality", "alternate_group"} <= _editable(m37, "M37-form-rbom")


def test_fault_code_form_holds_the_taxonomy(m37):
    screen = m37["screens"]["M37-form-fault"]
    assert {"name_bn", "symptom_ids", "operation_ids"} <= _editable(m37, "M37-form-fault")
    assert "root_cause_ids" in screen["grids"] and screen["lines"] == "brand_code_ids"
    assert {"symptom_ids", "operation_ids", "root_cause_ids", "name_bn"} <= set(
        _writable("a02")["fix.fault.code"]
    )


def test_part_form_shows_its_identity_and_model_fit(m37):
    assert {"manufacturer_part_number", "oem_reference"} <= _editable(m37, "M37-item")
    assert "compatibility_ids" in m37["screens"]["M37-item"]["grids"]


def test_refurb_grade_criteria_are_editable_by_the_officer_only(m37):
    editable = _editable(m37, "M37-form-refurb-grade")
    assert {"cosmetic_criteria", "functional_criteria", "sell_online", "warranty_days"} <= editable
    assert not editable & {"code", "price_multiplier", "currency_id"}
    acl = _acl("platform/cd_catalogue/security/ir.model.access.csv", "model_fix_refurb_grade,")
    assert acl["group_catalogue_officer"] == ["1", "1", "0", "0"], acl


def test_category_node_is_bilingual_coded_and_in_a_tree(m37):
    assert {"name_bn", "code", "tree_type"} <= _editable(m37, "M37-form-category")


def test_kit_and_rental_sku_carry_their_definition(m37):
    assert "explode_at" in _editable(m37, "M37-form-kit")
    assert {"min_hire_days", "deposit_basis", "condition_standard", "return_criteria"} <= _editable(
        m37, "M37-form-rentalsku"
    )
