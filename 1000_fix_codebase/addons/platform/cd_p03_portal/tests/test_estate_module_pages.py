# Every module's pages meet the M01 standard (12 Nov 2026).
#
# M01 was walked page by page (test_m01_submodule_pages.py). The same walk,
# run as an auditor over all 67 modules, found the same defects everywhere:
# 237 cross links answering "No module matches", 246 module reports and 56
# forms shown on no sub-module page, 187 screens badged with the wrong type,
# 20 order-slice pages offering the module's "+ New", 27 read-only forms
# opening blank, three modules offering "+ New Service Order" on their own
# page, report notes printing field names on the company PDF.
#
# One test per module and rule, evaluated as the browser evaluates the
# registry: node runs the engine's OWN methods (fregCreate, fregPanels,
# resolveCross) over the real fragments.
from __future__ import annotations

import ast
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "static" / "src"
CONTROLLERS = ROOT / "controllers"
IMPORT = re.compile(r'from\s+"(\./a\d\d/\w+)"')

# The deliberate in-workspace editors (not model_form screens): M19's journal
# editor (draft -> SoD review) and M20's manual-exception invoice editor.
EDITOR_CREATES = {"M19", "M20"}
# The form chips that openFormChip sends to those same editors, before any
# P03_FORM_CHIPS lookup - a plain form screen would bypass their controls.
EDITOR_CHIPS = {
    ("M19", "Journal Entry (manual/recurring)"),
    ("M20", "Invoice Request"),
}

PROBE = """
import * as M from './meta.mjs';
const { P03_MODULES, P03_MODULE_CREATE, P03_FORM_CHIPS, P03_DATA_SCREENS, P03_REPORT_ROUTES } = M;
function %(create)s
function %(panels)s
function %(cross)s
const kindLetter = { table_report: 'r', so_list: 'g', model_list: 'g', model_form: 'f' };
const out = {};
for (const [mid, mod] of Object.entries(P03_MODULES)) {
  const create = P03_MODULE_CREATE[mid] || null;
  const createCfg = create && create.screen ? P03_DATA_SCREENS[create.screen] : null;
  const moduleModel = create ? create.model : (mid === 'M01' ? 'fix.service.order' : null);
  const r = { mid, subs: [], reports: mod.reports || [], forms: mod.forms || [], cross: [],
    create: create ? { label: create.label, model: create.model, screen: create.screen || null,
      isForm: !!(createCfg && createCfg.kind === 'model_form' && createCfg.model === create.model) } : null,
    badges: [], readonlyForms: [], chips: [], routes: [] };
  for (const s of (mod.freg && mod.freg.sub) || []) {
    const map = s[3] || null;
    const p = fregPanels(mid, mod, map);
    r.subs.push({ no: s[0], title: s[1], model: (map && map.model) || null,
      explicitReports: !!(map && Array.isArray(map.reports)), explicitForms: !!(map && Array.isArray(map.forms)),
      reports: p.reports, forms: p.forms, create: fregCreate(mid, map),
      slice: !!(map && moduleModel && map.model === moduleModel && map.domain && map.domain.length),
      declaredCreate: map && Object.prototype.hasOwnProperty.call(map, 'create') ? map.create : null });
  }
  for (const rep of r.reports) r.routes.push({ rep, ok: !!P03_DATA_SCREENS[P03_REPORT_ROUTES[mid + ':' + rep]] });
  for (const f of r.forms) {
    const cfg = P03_DATA_SCREENS[P03_FORM_CHIPS[mid + ':' + f]];
    r.chips.push({ f, ok: !!cfg, kind: cfg ? cfg.kind : null });
  }
  for (const g of mod.groups) for (const s of g.screens) {
    const cfg = P03_DATA_SCREENS[s.id];
    const want = cfg && kindLetter[cfg.kind];
    if (want && s.t !== want && !(want === 'g' && s.t === 'd')) r.badges.push(s.id + ' is ' + cfg.kind + ', badged ' + s.t);
  }
  for (const [id, cfg] of Object.entries(P03_DATA_SCREENS)) {
    if (!id.startsWith(mid + '-') || cfg.kind !== 'model_form') continue;
    const fields = (cfg.sections || []).flatMap((x) => x.fields || []);
    const editable = fields.filter((f) => !f.readonly).length + (cfg.lines && !cfg.lines.readonlyGrid ? 1 : 0);
    if (fields.length && editable === 0 && !cfg.pickRecord) {
      const back = P03_DATA_SCREENS[cfg.back || ''];
      r.readonlyForms.push({ id, create: cfg.create === undefined ? null : cfg.create, pick: !!cfg.pick,
        backIsList: !!(back && back.kind !== 'model_form') });
    }
  }
  for (const c of mod.cross || []) {
    const to = resolveCross(c);
    const target = to && P03_MODULES[to.module];
    r.cross.push({ c, to, ok: !to || (!!target && (!to.screen || target.groups.some((g) => g.screens.some((s) => s.id === to.screen)))) });
  }
  out[mid] = r;
}
console.log(JSON.stringify(out));
"""


def _method(engine, sig):
    m = re.search(r"^    (%s \{\n.*?\n    \})\n" % re.escape(sig), engine, re.S | re.M)
    assert m, "p03_workspace.js no longer defines %s" % sig
    return m.group(1)


@pytest.fixture(scope="module")
def estate(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_estate_pages")
    for area in sorted(d for d in SRC.iterdir() if re.fullmatch(r"a\d\d", d.name)):
        (tmp / area.name).mkdir()
        for js in area.glob("*.js"):
            (tmp / area.name / (js.stem + ".mjs")).write_text(
                js.read_text(encoding="utf-8"), "utf-8"
            )
    meta = (SRC / "p03_modules_meta.js").read_text(encoding="utf-8")
    (tmp / "meta.mjs").write_text(IMPORT.sub(r'from "\1.mjs"', meta), "utf-8")
    engine = (SRC / "p03_workspace.js").read_text(encoding="utf-8").replace("\r\n", "\n")
    probe = tmp / "probe.mjs"
    probe.write_text(
        PROBE
        % {
            "create": _method(engine, "fregCreate(mid, map)"),
            "panels": _method(engine, "fregPanels(mid, mod, map)"),
            "cross": _method(engine, "resolveCross(term)"),
        },
        "utf-8",
    )
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our own probe file
        [node, str(probe)], capture_output=True, encoding="utf-8", check=True, timeout=120
    )
    return json.loads(out.stdout)


MODULES = ["M%02d" % n for n in range(1, 68)]


def test_the_estate_has_67_modules(estate):
    assert sorted(estate) == MODULES


@pytest.mark.parametrize("mid", MODULES)
def test_every_page_names_both_panels(estate, mid):
    """A mapping states its reports AND its forms (an empty list included):
    nothing on a page is left to be guessed."""
    loose = [
        "%s/%s %s" % (mid, s["no"], s["title"])
        for s in estate[mid]["subs"]
        if not (s["explicitReports"] and s["explicitForms"])
    ]
    assert not loose, "\n  ".join(loose)


@pytest.mark.parametrize("mid", MODULES)
def test_every_module_report_and_form_is_on_a_page(estate, mid):
    r = estate[mid]
    on_r = {x for s in r["subs"] for x in s["reports"]}
    on_f = {x for s in r["subs"] for x in s["forms"]}
    missing = ["report: %s" % x for x in r["reports"] if x not in on_r]
    missing += ["form: %s" % x for x in r["forms"] if x not in on_f]
    assert not missing, "\n  ".join(missing)


@pytest.mark.parametrize("mid", MODULES)
def test_every_chip_opens_a_declared_screen(estate, mid):
    r = estate[mid]
    bad = ["report %s" % x["rep"] for x in r["routes"] if not x["ok"]]
    bad += [
        "form %s" % x["f"]
        for x in r["chips"]
        if x["kind"] != "model_form" and (mid, x["f"]) not in EDITOR_CHIPS
    ]
    assert not bad, "\n  ".join(bad)


@pytest.mark.parametrize("mid", MODULES)
def test_a_slice_of_the_modules_record_offers_no_module_button(estate, mid):
    """Hold management, delivered jobs, a dispatch board: pages that work on
    EXISTING records of the module's own model declare what they capture."""
    bad = [
        "%s/%s %s" % (mid, s["no"], s["title"])
        for s in estate[mid]["subs"]
        if s["slice"] and s["declaredCreate"] is None
    ]
    assert not bad, "\n  ".join(bad)


@pytest.mark.parametrize("mid", MODULES)
def test_the_module_button_opens_a_workspace_form(estate, mid):
    create = estate[mid]["create"]
    if not create or mid in EDITOR_CREATES:
        return
    assert create["isForm"], "%s '+ %s' leaves the workspace" % (mid, create["label"])


@pytest.mark.parametrize("mid", MODULES)
def test_screen_links_are_badged_with_what_they_are(estate, mid):
    assert not estate[mid]["badges"], "\n  ".join(estate[mid]["badges"])


@pytest.mark.parametrize("mid", MODULES)
def test_a_read_only_form_never_opens_blank(estate, mid):
    bad = [
        "%s create=%s pick=%s backIsList=%s" % (f["id"], f["create"], f["pick"], f["backIsList"])
        for f in estate[mid]["readonlyForms"]
        if not (f["create"] is False and f["pick"] and f["backIsList"])
    ]
    assert not bad, "\n  ".join(bad)


@pytest.mark.parametrize("mid", MODULES)
def test_cross_links_land_on_their_module(estate, mid):
    bad = ["%s -> %s" % (x["c"], x["to"]) for x in estate[mid]["cross"] if not x["ok"]]
    assert not bad, "\n  ".join(bad)


# --- what the company PDF prints ---------------------------------------------

TECH = re.compile(
    r"\b(fix|res|account|stock|hr|mail|ir|sale|purchase|product)\.[a-z_]+(\.[a-z_]+)*\b"
    r"|\b[a-z]+_[a-z0-9_]+\b"
)


def _notes_by_module():
    found = {}
    for f in sorted(CONTROLLERS.glob("a[0-9][0-9]/m[0-9][0-9]*.py")):
        mid = "M" + re.match(r"m(\d\d)", f.stem).group(1)
        tree = ast.parse(f.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Dict):
                continue
            for k, v in zip(node.keys, node.values, strict=False):
                if isinstance(k, ast.Constant) and k.value == "notes":
                    for n in ast.walk(v):
                        text = None
                        if isinstance(n, ast.Constant) and isinstance(n.value, str):
                            text = n.value
                        elif isinstance(n, ast.JoinedStr):
                            text = "".join(p.value for p in n.values if isinstance(p, ast.Constant))
                        if text and TECH.search(text):
                            found.setdefault(mid, []).append("%s:%s %s" % (f.name, n.lineno, text))
    return found


NOTES = _notes_by_module()


@pytest.mark.parametrize("mid", MODULES)
def test_report_notes_are_written_for_the_reader(mid):
    """Notes print on the company PDF: no field or model names."""
    assert not NOTES.get(mid), "\n  ".join(NOTES.get(mid, []))


def test_a_record_made_on_a_filtered_page_lands_on_that_page(estate):
    """M63 "Scheduled & Event Jobs" lists automations whose engine is Airflow:
    a job created there starts with that engine, or it would vanish from the
    page it was made on. Only plain `field = value` clauses on fields the form
    lets the user type are carried."""
    sub = next(s for s in estate["M63"]["subs"] if s["no"] == "5")
    # the workflow-definition form, opened as "Scheduled Workflow" (M63 capture audit)
    assert sub["create"]["screen"] == "M63-form-scheduled"
    assert sub["create"]["presets"] == {"engine": "odoo_cron"}
    carried = [
        (m, s["no"])
        for m in MODULES
        for s in estate[m]["subs"]
        if (s["create"] or {}).get("presets")
    ]
    assert ("M63", "5") in carried
