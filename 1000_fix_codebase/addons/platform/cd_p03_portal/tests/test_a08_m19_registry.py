# A08 · M19 — the workspace registry (static/src/a08/m19.js, merged by
# p03_modules_meta.js) agrees with the backend: the 14 original screens keep
# their bespoke p03_gl_api kinds, every added model_list model is served by
# controllers/a08/m19.py SURFACES with real columns and real actions, every
# table_report names a REPORTS function, every report / form chip routes to
# a real screen / model, and every KPI tile names a metric that is served.
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from unittest import mock

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_finance_api
from odoo.addons.cd_p03_portal.controllers.a08 import m19

SRC = Path(__file__).resolve().parents[1] / "static" / "src"
IMPORT = re.compile(r'from\s+"(\./a\d\d/\w+)"')

# The original screens, served by the bespoke /p03/gl/* endpoints.
BESPOKE = {
    "M19-coa": "coa",
    "M19-journals": "journals",
    "M19-je": "je_editor",
    "M19-tb": "statement",
    "M19-dimensions": "dimensions",
    "M19-close": "close",
    "M19-periods": "periods",
    "M19-bs": "statement",
    "M19-pl": "statement",
    "M19-cf": "statement",
    "M19-consol": "statement",
    "M19-suspense": "suspense",
    "M19-recon": "recon",
    "M19-audit": "audit",
}


@pytest.fixture(scope="module")
def registry(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_registry_m19")
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
        "const pick = (o) => Object.fromEntries(Object.entries(o).filter(([k]) => k.startsWith('M19')));\n"
        "console.log(JSON.stringify({module: M.P03_MODULES.M19,\n"
        "  screens: pick(M.P03_DATA_SCREENS), routes: pick(M.P03_REPORT_ROUTES),\n"
        "  forms: pick(M.P03_FORM_MODELS), create: M.P03_MODULE_CREATE.M19}));\n",
        "utf-8",
    )
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our own probe file
        [node, str(probe)],
        capture_output=True,
        encoding="utf-8",  # Bengali labels: never the Windows ANSI codepage
        check=True,
        timeout=60,
    )
    return json.loads(out.stdout)


def test_every_registry_screen_has_a_real_screen(registry):
    ids = [s["id"] for g in registry["module"]["groups"] for s in g["screens"]]
    assert len(ids) == len(set(ids))
    # Every nav screen renders (no dead nav entries)…
    assert set(ids) <= set(registry["screens"]), "screens without an in-workspace entry"
    # …and every non-nav SCREENS entry is a reachable D365 surface: a
    # model_form with a back-target grid, or a pack routed from a report
    # chip (the finance form/report sweeps added these deliberately).
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


def test_the_original_fourteen_screens_keep_their_bespoke_kinds(registry):
    for sid, kind in BESPOKE.items():
        assert registry["screens"][sid]["kind"] == kind, sid


def test_spec_additions_are_present(registry):
    groups = {g["en"]: [s["id"] for s in g["screens"]] for g in registry["module"]["groups"]}
    assert {"M19-coa-loader", "M19-recurring"} <= set(groups["Ledger"])
    assert {"M19-report-bridge", "M19-nil-returns", "M19-close-sla"} <= set(groups["Close"])
    assert groups["Group & Inter-Branch"] == [
        "M19-consol-books",
        "M19-eliminations",
        "M19-ic-txns",
        "M19-ic-balances",
        "M19-ic-rules",
    ]


def test_model_list_screens_match_surfaces_and_fields(registry, odoo_env):
    served = set()
    for sid, cfg in registry["screens"].items():
        if cfg["kind"] != "model_list":
            continue
        model = cfg["model"]
        served.add(model)
        assert model in m19.SURFACES, f"{sid}: {model} not served"
        fields_ = odoo_env[model]._fields
        for col in cfg["cols"]:
            assert col in fields_, f"{sid}: {model}.{col} is not a field"
        if cfg.get("stateField"):
            assert cfg["stateField"] in fields_
        for act in cfg.get("actions", []):
            assert act["m"] in m19.SURFACES[model]["actions"], f"{sid}: {act['m']}"
            assert callable(getattr(odoo_env[model], act["m"], None))
        for leaf in cfg.get("domain", []):
            assert leaf[0] in fields_
    assert served == set(m19.SURFACES), "a surface without a screen"
    for model, conf in m19.SURFACES.items():
        for method in conf["actions"]:
            assert callable(getattr(odoo_env[model], method, None)), f"{model}.{method}"


def test_table_reports_name_real_report_functions(registry):
    reports = [c for c in registry["screens"].values() if c["kind"] == "table_report"]
    assert reports
    for cfg in reports:
        assert cfg["module"] == "M19"
        assert cfg["report"] in m19.REPORTS
    assert {c["report"] for c in reports} == set(m19.REPORTS)


def test_report_and_form_chips_route_to_real_targets(registry, odoo_env):
    module = registry["module"]
    for chip in module["reports"]:
        target = registry["routes"].get(f"M19:{chip}")
        assert target in registry["screens"], f"report chip {chip!r} unrouted"
    for chip in module["forms"]:
        model = registry["forms"].get(f"M19:{chip}")
        assert model and model in odoo_env, f"form chip {chip!r} unmapped"
    assert registry["create"]["model"] in odoo_env


class _FakeRequest:
    def __init__(self, env):
        self.env = env


def test_kpi_tiles_name_served_metrics(registry, odoo_env):
    with mock.patch.object(p03_finance_api, "request", _FakeRequest(odoo_env)):
        served = p03_finance_api.P03FinanceApiController().finance_kpis(module="M19")["M19"]
    for kpi in registry["module"]["kpis"]:
        assert kpi.get("m") in served, f"KPI tile {kpi['l']!r} has no metric"
