# Every screen, chip, route and button in the workspace lands somewhere real.
#
# The 2026-11-10 screens sweep (2,177 screens, driven over the wire) found a
# class of defects no test could see, because each one is a mismatch BETWEEN
# two declarations that are each valid on their own:
#
#   - a list row that opened another model's form with this row's id
#     (FORM_CHIPS.__by_screen__ mapped a line list to its batch's form);
#   - journey chips and links in the engine that named screen ids no fragment
#     declares, so openScreen() fell back to the module's first screen;
#   - seven report routes written inside SCREENS (M11 exported no
#     REPORT_ROUTES at all), so every M11 report chip answered with a toast;
#   - buttons whose method the backend surface refuses on purpose;
#   - a form field declared twice - the engine keys field metadata by NAME
#     and the last declaration wins, so a read-only echo on a later tab
#     silently locked the editable input on the first one.
#
# The registry is evaluated as the browser evaluates it: the fragments are
# loaded as ES modules through p03_modules_meta.js (the real merge), never
# pattern-matched. Same harness as test_a08_m19_registry.py.
from __future__ import annotations

import inspect
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api

SRC = Path(__file__).resolve().parents[1] / "static" / "src"
IMPORT = re.compile(r'from\s+"(\./a\d\d/\w+)"')
SCREEN_ID = re.compile(r"""['"](M\d\d-[a-z0-9][a-z0-9-]*)['"]""")
# The engine itself. p03_modules_meta.js is the merge (its inline module
# stubs are superseded by the fragments) and p03_i18n.js is a text catalogue.
ENGINE_SKIP = {"p03_modules_meta.js", "p03_i18n.js"}


@pytest.fixture(scope="module")
def registry(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_screens_wiring")
    for area in sorted(d for d in SRC.iterdir() if re.fullmatch(r"a\d\d", d.name)):
        (tmp / area.name).mkdir()
        for js in area.glob("*.js"):
            (tmp / area.name / (js.stem + ".mjs")).write_text(
                js.read_text(encoding="utf-8"), "utf-8"
            )
    meta = (SRC / "p03_modules_meta.js").read_text(encoding="utf-8")
    (tmp / "meta.mjs").write_text(IMPORT.sub(r'from "\1.mjs"', meta), "utf-8")
    probe = tmp / "probe.mjs"
    probe.write_text(
        "import * as M from './meta.mjs';\n"
        "console.log(JSON.stringify({modules: M.P03_MODULES,\n"
        "  screens: M.P03_DATA_SCREENS, live: Object.keys(M.P03_LIVE_SCREENS),\n"
        "  routes: M.P03_REPORT_ROUTES, chips: M.P03_FORM_CHIPS,\n"
        "  form_models: M.P03_FORM_MODELS, create: M.P03_MODULE_CREATE}));\n",
        "utf-8",
    )
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our own probe file
        [node, str(probe)],
        capture_output=True,
        encoding="utf-8",  # Bengali labels: never the Windows ANSI codepage
        check=True,
        timeout=120,
    )
    return json.loads(out.stdout)


def _configs(registry):
    return {sid: cfg for sid, cfg in registry["screens"].items() if isinstance(cfg, dict)}


def _nav(registry):
    for code, module in registry["modules"].items():
        for group in module.get("groups") or []:
            for screen in group.get("screens") or []:
                yield code, screen


def test_the_scan_sees_the_whole_estate(registry):
    """A guard on the guard - an empty registry would pass everything below."""
    assert len(registry["modules"]) == 67, len(registry["modules"])
    assert len(_configs(registry)) > 2000, len(_configs(registry))
    assert len(registry["routes"]) > 400 and len(registry["chips"]) > 300


def test_screens_holds_only_screen_configs(registry):
    """A route string inside SCREENS is a REPORT_ROUTES entry in the wrong
    export: the merge never sees it and its report chip is dead (M11)."""
    strays = {sid: cfg for sid, cfg in registry["screens"].items() if not isinstance(cfg, dict)}
    assert not strays, "non-config entries in SCREENS: %s" % strays


def test_a_row_opens_a_form_of_its_own_model(registry):
    """'Open full record' passes the ROW's id to the mapped form: a form bound
    to another model then loads an unrelated record with that id, or none."""
    screens = _configs(registry)
    wrong, checked = [], 0
    for key, mapping in registry["chips"].items():
        if not isinstance(mapping, dict):
            continue
        for source, form in mapping.items():
            target = screens.get(form)
            assert target, "%s[%s] -> undeclared screen %s" % (key, source, form)
            if key.endswith(":__by_screen__"):
                assert source in screens, "%s names undeclared screen %s" % (key, source)
                model = screens[source].get("model")
                if not model:
                    # a report / bespoke screen has no rows of its own to open
                    continue
            else:
                model = source
            checked += 1
            if target.get("model") != model:
                wrong.append(
                    "%s[%s] (%s) -> %s (%s)" % (key, source, model, form, target.get("model"))
                )
    assert checked > 800, "only %d row->form mappings were checked" % checked
    assert not wrong, "rows open another model's form:\n  " + "\n  ".join(wrong)


def test_engine_links_name_declared_screens(registry):
    """Every screen id hard-coded in the engine (openScreen('M15-onhand'), a
    Tell-Me entry, a journey chip) must be a declared screen: an undeclared
    one silently opens the active module's first screen instead."""
    declared = set(_configs(registry)) | set(registry["live"])
    files = sorted(
        p for p in SRC.glob("p03_*") if p.suffix in (".js", ".xml") and p.name not in ENGINE_SKIP
    )
    assert any(p.name == "p03_workspace.js" for p in files)
    assert any(p.name == "p03_workspace.xml" for p in files)
    found, missing = 0, []
    for path in files:
        for no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for sid in SCREEN_ID.findall(line):
                found += 1
                if sid not in declared:
                    missing.append("%s:%d %s" % (path.name, no, sid))
    assert found >= 20, "the engine scan found only %d screen ids" % found
    assert not missing, "engine links to undeclared screens:\n  " + "\n  ".join(missing)


def test_every_report_chip_routes_to_a_declared_screen(registry):
    screens = set(_configs(registry)) | set(registry["live"])
    codes = set(registry["modules"])
    bad_keys = [k for k in registry["routes"] if k.split(":", 1)[0] not in codes or ":" not in k]
    assert not bad_keys, "REPORT_ROUTES keys without a module prefix: %s" % bad_keys
    dangling = {k: v for k, v in registry["routes"].items() if v not in screens}
    assert not dangling, "REPORT_ROUTES to undeclared screens: %s" % dangling
    dead = [
        "%s:%s" % (code, name)
        for code, module in registry["modules"].items()
        for name in module.get("reports") or []
        if "%s:%s" % (code, name) not in registry["routes"]
    ]
    assert not dead, "report chips with no route (toast only):\n  " + "\n  ".join(dead)


def test_every_form_chip_opens_its_own_form(registry):
    """A chip whose label matches no FORM_CHIPS / FORM_MODELS key falls back
    to the module's create surface - the Journal Entry editor for a take-on
    chip, the service-order intake for a rider shift."""
    screens = _configs(registry)
    lost = []
    for code, module in registry["modules"].items():
        for label in module.get("forms") or []:
            key = "%s:%s" % (code, label)
            # openFormChip() routes these two itself (p03_workspace.js)
            if code == "M19" and re.search("journal entry", label, re.I):
                continue
            if code == "M20" and re.search("invoice request", label, re.I):
                continue
            target = registry["chips"].get(key)
            if target:
                assert target in screens, "%s -> undeclared screen %s" % (key, target)
            elif key not in registry["form_models"]:
                lost.append(key)
    assert not lost, "form chips with no form of their own:\n  " + "\n  ".join(lost)


def test_every_list_and_form_model_is_served(registry):
    unserved = sorted(
        "%s (%s)" % (sid, cfg.get("model"))
        for sid, cfg in _configs(registry).items()
        if cfg.get("kind") in ("model_list", "model_form") and cfg.get("model") not in api.SURFACES
    )
    assert not unserved, "screens bind models no SURFACES serves:\n  " + "\n  ".join(unserved)


def test_list_buttons_are_actions_the_surface_allows(registry):
    """/p03/model/action refuses a method that is not in the surface's
    `actions`; a button for one can only ever answer 'Action not available'."""
    refused = []
    for sid, cfg in _configs(registry).items():
        if cfg.get("kind") != "model_list":
            continue
        allowed = (api.SURFACES.get(cfg.get("model")) or {}).get("actions", set())
        for action in cfg.get("actions") or []:
            # `print`: the record's document through /p03/doc/print_url - no
            # server method; the model must be one that route can print
            if action.get("print"):
                from odoo.addons.cd_p03_portal.controllers import p03_commercial_docs as docs

                source = inspect.getsource(docs)
                if '"%s":' % cfg.get("model") not in source:
                    refused.append(
                        "%s %s print (no document for the model)" % (sid, cfg.get("model"))
                    )
                continue
            # `form`: opens a NEW record of another form for the row (Record
            # Proforma) - no server call; that form must exist and take the row
            if action.get("form"):
                target = _configs(registry).get(action["form"]) or {}
                names = {
                    f.get("name")
                    for s in target.get("sections") or []
                    for f in s.get("fields") or []
                }
                if target.get("kind") != "model_form" or (
                    action.get("prefill") and action["prefill"] not in names
                ):
                    refused.append("%s %s opens no form for it" % (sid, action.get("m")))
                continue
            if action.get("m") not in allowed:
                refused.append("%s %s.%s" % (sid, cfg.get("model"), action.get("m")))
    assert not refused, "buttons the backend refuses:\n  " + "\n  ".join(refused)


def test_no_list_shows_a_column_the_endpoint_blocks(registry):
    blocked = sorted(
        "%s %s" % (sid, col)
        for sid, cfg in _configs(registry).items()
        if cfg.get("kind") == "model_list"
        for col in cfg.get("cols") or []
        if col in api._BLOCKED_FIELDS
    )
    assert not blocked, "columns /p03/model/records never returns:\n  " + "\n  ".join(blocked)


def test_no_form_declares_a_field_twice(registry):
    """Field metadata is keyed by field name and the LAST declaration wins: a
    read-only echo on a later tab locks the editable input on an earlier one
    (a new loyalty account could not pick its programme)."""
    twice = []
    for sid, cfg in _configs(registry).items():
        if cfg.get("kind") != "model_form":
            continue
        names = [f.get("name") for s in cfg.get("sections") or [] for f in s.get("fields") or []]
        dup = sorted({n for n in names if names.count(n) > 1})
        if dup:
            twice.append("%s %s" % (sid, dup))
    assert not twice, "fields declared more than once:\n  " + "\n  ".join(twice)


def test_nav_entries_are_declared_and_typed_as_what_they_are(registry):
    screens = _configs(registry)
    undeclared, mistyped = [], []
    for code, entry in _nav(registry):
        cfg = screens.get(entry["id"])
        if cfg is None:
            if entry["id"] not in registry["live"]:
                undeclared.append("%s %s" % (code, entry["id"]))
            continue
        kind, t = cfg.get("kind"), entry.get("t")
        if (t == "f" and kind in ("model_list", "table_report")) or (
            t in ("g", "r") and kind == "model_form"
        ):
            mistyped.append("%s t:'%s' is a %s" % (entry["id"], t, kind))
    assert not undeclared, "nav screens with no SCREENS entry:\n  " + "\n  ".join(undeclared)
    assert not mistyped, "nav type contradicts the screen kind:\n  " + "\n  ".join(mistyped)


def test_a_form_status_pill_reads_a_field_it_can_print(registry, odoo_env):
    """/p03/model/form serves a status value only for a selection, char or
    boolean field; a many2one there rendered a blank pill or '[object Object]'
    (M07-form-activity pointed its pill at activity_type_id)."""
    unprintable, checked = [], 0
    for sid, cfg in _configs(registry).items():
        field = (cfg.get("status") or {}).get("field")
        if cfg.get("kind") != "model_form" or not field or cfg.get("model") not in odoo_env:
            continue
        spec = odoo_env[cfg["model"]]._fields.get(field)
        checked += 1
        if spec is None or spec.type not in ("selection", "char", "boolean"):
            unprintable.append("%s %s.%s (%s)" % (sid, cfg["model"], field, spec and spec.type))
    assert checked > 200, "only %d status pills were checked" % checked
    assert not unprintable, "status pills on unprintable fields:\n  " + "\n  ".join(unprintable)
