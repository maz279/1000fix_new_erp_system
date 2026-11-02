# A08 · M52 — the workspace registry (static/src/a08/m52.js, merged by
# p03_modules_meta.js) agrees with the backend surface (controllers/a08/m52.py)
# and the live models: every registry screen has a SCREENS entry with a
# Bengali label, every model_list model is served by a SURFACES entry with real
# columns and argument-free actions, every table_report names a REPORTS
# function, every report / form chip routes to a real screen / model, and the
# KPI tiles name metrics the backend returns.
from __future__ import annotations

import inspect
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest
from odoo.addons.cd_p03_portal.controllers import a08
from odoo.addons.cd_p03_portal.controllers.a08 import m52 as mod

CODE = "M52"
SRC = Path(__file__).resolve().parents[1] / "static" / "src"
IMPORT = re.compile(r'from\s+"(\./a\d\d/\w+)"')
# metrics served by the shared /p03/finance/kpis endpoint for this module
SHARED = {"match_exceptions", "expense_claims_pending"}


@pytest.fixture(scope="module")
def registry(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_registry_m52")
    # every area folder the registry imports (a02, a08, ...)
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
        "const C = '%s';\n"
        "const pick = (o) => Object.fromEntries(Object.entries(o).filter(([k]) => k.startsWith(C)));\n"
        "console.log(JSON.stringify({module: M.P03_MODULES[C],\n"
        "  screens: pick(M.P03_DATA_SCREENS), routes: pick(M.P03_REPORT_ROUTES),\n"
        "  forms: pick(M.P03_FORM_MODELS), create: M.P03_MODULE_CREATE[C]}));\n" % CODE,
        "utf-8",
    )
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our probe file
        [node, str(probe)], capture_output=True, text=True, encoding="utf-8", check=True, timeout=60
    )
    return json.loads(out.stdout)


def test_every_registry_screen_has_a_real_screen(registry):
    ids = [s["id"] for g in registry["module"]["groups"] for s in g["screens"]]
    assert len(ids) == len(set(ids))
    # Every nav screen renders (no dead nav entries)…
    assert set(ids) <= set(registry["screens"]), "screens without an in-workspace entry"
    # …and every non-nav SCREENS entry is a reachable D365 surface: a
    # model_form with a back-target grid, or a pack routed from a report
    # chip (the A08 form/report sweeps added these deliberately).
    routed = set(registry["routes"].values())
    orphans = [
        sid
        for sid, cfg in registry["screens"].items()
        if sid not in set(ids)
        and not (cfg.get("kind") == "model_form" and cfg.get("back"))
        and sid not in routed
    ]
    assert not orphans, f"orphan screens unreachable from nav or chips: {orphans}"
    for group in registry["module"]["groups"]:
        for s in group["screens"]:
            assert s.get("bn"), s["id"]


def test_model_list_screens_match_surfaces_and_fields(registry, odoo_env):
    for sid, cfg in registry["screens"].items():
        if cfg["kind"] != "model_list":
            continue
        model = cfg["model"]
        assert model in a08.SURFACES, f"{sid}: {model} not served"
        fields_ = odoo_env[model]._fields
        for col in cfg["cols"]:
            assert col in fields_, f"{sid}: {model}.{col} is not a field"
        if cfg.get("stateField"):
            assert cfg["stateField"] in fields_
        for act in cfg.get("actions", []):
            assert act["m"] in a08.SURFACES[model]["actions"], f"{sid}: {act['m']}"
            method = getattr(odoo_env[model], act["m"], None)
            assert callable(method), f"{sid}: {act['m']}"
            # the workspace calls actions WITHOUT arguments
            params = list(inspect.signature(method).parameters.values())
            assert all(p.default is not p.empty for p in params), f"{sid}: {act['m']} needs args"
        for leaf in cfg.get("domain", []):
            assert leaf[0] in fields_


def test_every_declared_action_is_argument_free(odoo_env):
    for model, conf in mod.SURFACES.items():
        for name in conf["actions"]:
            method = getattr(odoo_env[model], name)
            params = list(inspect.signature(method).parameters.values())
            assert all(p.default is not p.empty for p in params), f"{model}.{name}"


def test_table_reports_name_real_report_functions(registry):
    reports = [c for c in registry["screens"].values() if c["kind"] == "table_report"]
    assert reports
    for cfg in reports:
        assert cfg["module"] == CODE
        assert cfg["report"] in mod.REPORTS
    assert {c["report"] for c in reports} == set(mod.REPORTS)


def test_report_and_form_chips_route_to_real_targets(registry, odoo_env):
    module = registry["module"]
    for chip in module["reports"]:
        target = registry["routes"].get(f"{CODE}:{chip}")
        assert target in registry["screens"], f"report chip {chip!r} unrouted"
    for chip in module["forms"]:
        model = registry["forms"].get(f"{CODE}:{chip}")
        assert model and model in a08.SURFACES, f"form chip {chip!r} unmapped"
    assert registry["create"]["model"] in a08.SURFACES


def test_kpi_tiles_name_real_metrics(registry, odoo_env):
    keys = set(mod.kpis(odoo_env)) | SHARED
    for kpi in registry["module"]["kpis"]:
        assert kpi.get("m") in keys, f"KPI tile {kpi['l']!r} has no metric"
    assert all(v is not None for v in mod.kpis(odoo_env).values())
