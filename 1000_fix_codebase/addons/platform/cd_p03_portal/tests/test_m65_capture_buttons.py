# M65 Multi-Entity & Localisation: every sub-module page captures the records
# it covers (capture audit 2026-11-18).
#
# Before:
#   * Entity Structure offered + New Legal Entity and no chip; an entity could
#     not be given a country pack anywhere (FR-GLO-001/010: no assignment
#     record existed).
#   * Country Packs listed pack lines and payment gateways but offered only a
#     Country Pack chip.
#   * Jurisdiction captured only the documentation register: no data residency
#     rule (FR-GLO-015) and no country onboarding record (FR-GLO-035) existed.
#   * Translation offered "+ New Locale Pack" - page 3's record - and nothing
#     to review: no translation review (FR-GLO-022/024, BRU-GLO-07) or
#     rendering verification (FR-GLO-025) record existed.
#   * "Audit" listed intercompany rules with create: false: no capture at all,
#     and the charges and transfer-pricing rates it governs were not shown.
#
# Evaluated as the browser evaluates it: node runs the engine's own fregCreate
# and fregPanels over the real registry fragments (the M30 guard's fixture).
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
CONTROLLER = HERE.parent / "controllers" / "a12" / "m65.py"
M19_CONTROLLER = HERE.parent / "controllers" / "a08" / "m19.py"
MULTI_ENTITY = HERE.parents[1] / "cd_multi_entity"

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
const mod = P03_MODULES.M65;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M65', map);
  const panels = fregPanels('M65', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M65:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M65.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: own || null, label: create ? create.label : null, forms,
    reports: panels.reports.map((r) => ({ r, route: P03_REPORT_ROUTES['M65:' + r] || null })) };
});
const shown = (c) => ({
  kind: c.kind, model: c.model || null, create: c.create, report: c.report || null,
  tabs: (c.tabs || []).map((t) => t.id),
  actions: (c.actions || []).map((a) => ({ m: a.m, kwarg: a.kwarg || null })),
  sections: (c.sections || []).map((s) => ({ tab: s.tab || null, n: (s.fields || []).length })),
  cols: c.cols || [],
  fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({
    name: f.name, readonly: !!f.readonly, required: !!f.required })) });
const chipped = new Set(Object.values(P03_FORM_CHIPS['M65:__by_screen__'] || {}));
console.log(JSON.stringify({ subs,
  kpis: mod.kpis.map((k) => k.m),
  reports: mod.reports, forms: mod.forms,
  nav: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS)
    .filter(([id]) => id.startsWith('M65-') || chipped.has(id)).map(([id, c]) => [id, shown(c)])),
  by_screen: P03_FORM_CHIPS['M65:__by_screen__'] }));
"""

# What each page must let a person capture: the page's own "+ New" first,
# then every other record the page covers, by its form screen.
CAPTURES = {
    "1": ["M65-form-entity", "M65-form-entity-pack"],
    "2": ["M65-form-country", "M65-form-packline", "M65-form-gateway"],
    "3": ["M65-form-locale"],
    "4": ["M65-form-jurisdiction", "M65-form-residency", "M65-form-onboarding"],
    "5": ["M65-form-translation", "M65-form-rendering"],
    "6": ["M19-form-icrule", "M19-form-ic", "M19-form-tp-rate"],
}

# The record each page lists (its grid).
RECORDS = {
    "1": "fix.entity",
    "2": "fix.country.pack",
    "3": "fix.locale.pack",
    "4": "fix.jurisdiction.rule",
    "5": "fix.translation.entry",
    "6": "fix.intercompany.rule",
}

# The models the capture audit built (cd_multi_entity/models/fix_m65_capture.py).
NEW_MODELS = (
    "fix.entity.jurisdiction",
    "fix.jurisdiction.residency.rule",
    "fix.country.onboarding",
    "fix.translation.entry",
    "fix.rendering.verification",
)

# Intercompany records are M19's (the accounting); M65 shows and captures them
# through M19's forms, and M19's controller serves them.
M19_MODELS = ("fix.intercompany.rule", "fix.intercompany.transaction", "fix.transfer.price.rate")


@pytest.fixture(scope="module")
def m65(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m65_capture")
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


def _controller(path):
    """SURFACES / WRITABLE / REPORTS of a controller module, read without Odoo."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out = {"REPORTS": set(), "SURFACES": {}, "WRITABLE": {}}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name == "WRITABLE" and isinstance(node.value, ast.Dict):
                out[name] = {
                    ast.literal_eval(k): tuple(ast.literal_eval(e) for e in v.elts)
                    if isinstance(v, ast.Tuple | ast.List)
                    else ()
                    for k, v in zip(node.value.keys, node.value.values, strict=True)
                }
            elif name == "SURFACES":
                actions = {}
                for key, conf in zip(node.value.keys, node.value.values, strict=True):
                    acts = set()
                    for k, v in zip(conf.keys, conf.values, strict=True):
                        if ast.literal_eval(k) == "actions" and isinstance(v, ast.Set):
                            acts = {ast.literal_eval(e) for e in v.elts}
                    actions[ast.literal_eval(key)] = acts
                out[name] = actions
            elif name == "REPORTS":
                out["REPORTS"] |= {ast.literal_eval(k) for k in node.value.keys}
        if (
            isinstance(node, ast.Assign)
            and isinstance(node.targets[0], ast.Subscript)
            and isinstance(node.targets[0].value, ast.Name)
            and node.targets[0].value.id == "REPORTS"
        ):
            out["REPORTS"].add(ast.literal_eval(node.targets[0].slice))
    return out


def _sub(m65, no):
    return next(s for s in m65["subs"] if s["no"] == no)


def test_every_page_is_classified(m65):
    assert sorted(s["no"] for s in m65["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m65, no):
    sub = _sub(m65, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]}
    missing = [form for form in [own, *others] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)
    for f in sub["forms"]:
        assert f["kind"] == "model_form", "chip %s opens %s" % (f["f"], f["kind"])


@pytest.mark.parametrize("no", sorted(RECORDS, key=int))
def test_each_page_lists_its_own_record(m65, no):
    assert _sub(m65, no)["model"] == RECORDS[no]


def test_translation_page_does_not_offer_a_locale_pack(m65):
    """The old page 5 "+ New" opened page 3's Locale Pack form."""
    sub = _sub(m65, "5")
    assert sub["create"] != "M65-form-locale"
    assert "M65-form-locale" not in {f["id"] for f in sub["forms"]}


def test_each_captured_record_is_listed_on_its_page(m65):
    """A capture lands on a list of the page it was made from."""
    for sub in m65["subs"]:
        listed = {m65["screens"][s]["model"] for s in sub["screens"] if s in m65["screens"]}
        for f in sub["forms"]:
            assert f["model"] in listed, "page %s captures %s but lists no such record" % (
                sub["no"],
                f["model"],
            )


def test_every_working_screen_sits_on_a_page_and_in_the_nav(m65):
    placed = {sid for s in m65["subs"] for sid in s["screens"]}
    placed |= {r["route"] for s in m65["subs"] for r in s["reports"]}
    lists = [
        sid
        for sid, cfg in m65["screens"].items()
        if sid.startswith("M65-") and cfg["kind"] in ("model_list", "table_report")
    ]
    assert not [sid for sid in lists if sid not in placed]
    assert not [sid for sid in lists if sid not in m65["nav"]]


def test_every_module_report_and_form_sits_on_a_page(m65):
    reports = {r["r"] for s in m65["subs"] for r in s["reports"]}
    forms = {f["f"] for s in m65["subs"] for f in s["forms"]}
    assert set(m65["reports"]) <= reports, set(m65["reports"]) - reports
    assert set(m65["forms"]) <= forms, set(m65["forms"]) - forms


def test_every_page_report_opens_its_pack(m65):
    reports = _controller(CONTROLLER)["REPORTS"]
    for sub in m65["subs"]:
        for r in sub["reports"]:
            assert r["route"], "page %s report %s has no route" % (sub["no"], r["r"])
            assert m65["screens"][r["route"]]["report"] in reports, r


def test_a_list_offering_new_opens_a_form_of_its_own_model(m65):
    for sid, cfg in m65["screens"].items():
        if not sid.startswith("M65-") or cfg["kind"] != "model_list" or cfg.get("create") is False:
            continue
        form = m65["by_screen"].get(sid)
        assert form, "%s offers + New but opens no form" % sid
        assert m65["screens"][form]["model"] == cfg["model"], sid


def _served():
    m65 = _controller(CONTROLLER)["SURFACES"]
    m19 = _controller(M19_CONTROLLER)["SURFACES"]
    # fix.entity is M30's surface (one controller per model in A12)
    m30 = _controller(HERE.parent / "controllers" / "a12" / "m30.py")["SURFACES"]
    return {**m19, **m30, **m65}


def test_every_row_action_is_served(m65):
    surfaces = _served()
    for sid, cfg in m65["screens"].items():
        if not sid.startswith("M65-"):
            continue
        for act in cfg["actions"]:
            assert act["m"] in surfaces[cfg["model"]], "%s %s is not served" % (sid, act["m"])


def test_every_listed_model_is_served(m65):
    surfaces = _served()
    for sid, cfg in m65["screens"].items():
        if cfg["kind"] in ("model_list", "model_form"):
            assert cfg["model"] in surfaces, "%s reads %s, which nobody serves" % (
                sid,
                cfg["model"],
            )
    for model in M19_MODELS:
        assert model in _controller(M19_CONTROLLER)["SURFACES"], model


def test_every_editable_m65_form_field_is_writable(m65):
    """A field an M65 form lets the user type saves through the write whitelist."""
    writable = _controller(CONTROLLER)["WRITABLE"]
    for sid, cfg in m65["screens"].items():
        if not sid.startswith("M65-form-") or cfg["model"] not in NEW_MODELS:
            continue
        editable = {f["name"] for f in cfg["fields"] if not f["readonly"]}
        lost = editable - set(writable[cfg["model"]])
        assert not lost, "%s cannot save %s" % (sid, sorted(lost))


def test_workflow_stamps_are_never_typed(m65):
    """State, sign-off and phase stamps move only through create and the actions."""
    writable = _controller(CONTROLLER)["WRITABLE"]
    stamps = {
        "fix.entity.jurisdiction": {
            "state",
            "pack_version",
            "assigned_by_id",
            "assigned_on",
            "superseded_by_id",
            "superseded_on",
        },
        "fix.jurisdiction.residency.rule": {
            "state",
            "verified_by_id",
            "verified_on",
            "verification_note",
        },
        "fix.country.onboarding": {
            "phase",
            "initiated_on",
            "piloted_on",
            "activated_on",
            "activated_by_id",
            "abandoned_reason",
            "gate_result",
        },
        "fix.translation.entry": {
            "state",
            "translated_by_id",
            "reviewed_by_id",
            "reviewed_on",
            "review_note",
            "applied",
        },
        "fix.rendering.verification": {"verified_by_id"},
    }
    for model, names in stamps.items():
        assert not names & set(writable[model]), model
    for sid, cfg in m65["screens"].items():
        if cfg["kind"] == "model_form" and cfg["model"] in stamps:
            shown = {f["name"]: f for f in cfg["fields"]}
            for name in stamps[cfg["model"]] & set(shown):
                assert shown[name]["readonly"], "%s lets %s be typed" % (sid, name)


def test_long_forms_are_tabbed(m65):
    """Workspace standard: a form with more than 15 fields is split into tabs,
    and every section names a declared tab (an undeclared tab is invisible)."""
    for sid, cfg in m65["screens"].items():
        if cfg["kind"] != "model_form" or not sid.startswith("M65-form-"):
            continue
        if len(cfg["fields"]) > 15:
            assert cfg["tabs"], "%s has %d fields and no tabs" % (sid, len(cfg["fields"]))
        for section in cfg["sections"]:
            if cfg["tabs"]:
                assert section["tab"] in cfg["tabs"], sid


def test_new_models_have_access_rows_and_company_rules():
    acl = (MULTI_ENTITY / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    rules = (MULTI_ENTITY / "security" / "fix_isolation_rules.xml").read_text(encoding="utf-8")
    for model in NEW_MODELS:
        ref = "model_" + model.replace(".", "_")
        assert ",%s,cd_entity_config.group_platform_admin,1,1,1," % ref in acl, model
        # internal users may read, never write
        for line in acl.splitlines():
            if ",%s,base.group_user," % ref in line:
                assert line.endswith(",1,0,0,0"), line
        assert 'ref="%s"' % ref in rules, model


def test_the_new_kpis_are_served(m65):
    assert {"translations_in_review", "onboardings_open"} <= set(m65["kpis"])
    text = CONTROLLER.read_text(encoding="utf-8")
    assert '"translations_in_review"' in text
    assert '"onboardings_open"' in text
