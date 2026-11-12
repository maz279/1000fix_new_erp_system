# A Function Register sub-module page offers the data capture of ITS OWN
# record.
#
# Reported 2026-11-12 from M01 "Estimate & Customer Approval Loop": the page
# lists fix.estimate records and its green button read "+ New Service Order".
# The page carried the module's one create button whatever the sub-module
# was - 358 of the 603 sub-module pages had a form of their own and showed
# the module's instead. And the form the button should have opened, M01's
# estimate form, showed the estimate's totals without its lines, so an
# estimate raised there could never be sent.
#
# The rule is JavaScript (p03_workspace.js fregCreate), so it is EXECUTED
# here: node runs the method's own source over the real registry, for every
# sub-module of every module. The lines grid is proved through the endpoint
# the form saves with.
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from unittest import mock

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.exceptions import UserError

SRC = Path(__file__).resolve().parents[1] / "static" / "src"
IMPORT = re.compile(r'from\s+"(\./a\d\d/\w+)"')
# the method as written in the component: `    fregCreate(mid, map) { ... }`
FREG_CREATE = re.compile(r"^    (fregCreate\(mid, map\) \{\n.*?\n    \})\n", re.S | re.M)

PROBE = """
import * as M from './meta.mjs';
const { P03_MODULES, P03_MODULE_CREATE, P03_FORM_CHIPS, P03_DATA_SCREENS } = M;
function %s
const rows = [];
for (const [mid, mod] of Object.entries(P03_MODULES)) {
  const moduleCreate = P03_MODULE_CREATE[mid];
  for (const sub of (mod.freg && mod.freg.sub) || []) {
    const map = sub[3] || null;
    const create = fregCreate(mid, map);
    const form = create && create.screen ? P03_DATA_SCREENS[create.screen] : null;
    rows.push({ mid, no: sub[0], title: sub[1], model: map && map.model,
      moduleModel: moduleCreate ? moduleCreate.model : 'fix.service.order',
      create, formKind: form && form.kind, formModel: form && form.model,
      declared: !!(map && typeof map.create === 'string'),
      forms: (map && map.forms) || [], reports: (map && map.reports) || [] });
  }
}
console.log(JSON.stringify({ rows,
  estimateForm: P03_DATA_SCREENS['M01-form-estimate'],
  chips: P03_FORM_CHIPS, routes: M.P03_REPORT_ROUTES }));
"""


@pytest.fixture(scope="module")
def registry(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_registry_freg_create")
    for area in sorted(d for d in SRC.iterdir() if re.fullmatch(r"a\d\d", d.name)):
        (tmp / area.name).mkdir()
        for js in area.glob("*.js"):
            (tmp / area.name / (js.stem + ".mjs")).write_text(
                js.read_text(encoding="utf-8"), "utf-8"
            )
    meta = (SRC / "p03_modules_meta.js").read_text(encoding="utf-8")
    (tmp / "meta.mjs").write_text(IMPORT.sub(r'from "\1.mjs"', meta), "utf-8")
    method = FREG_CREATE.search((SRC / "p03_workspace.js").read_text(encoding="utf-8"))
    assert method, "p03_workspace.js no longer defines fregCreate(mid, map)"
    probe = tmp / "probe.mjs"
    probe.write_text(PROBE % method.group(1), "utf-8")
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our own probe file
        [node, str(probe)],
        capture_output=True,
        encoding="utf-8",  # Bengali labels: never the Windows ANSI codepage
        check=True,
        timeout=60,
    )
    return json.loads(out.stdout)


def _row(registry, mid, no):
    return next(r for r in registry["rows"] if r["mid"] == mid and r["no"] == no)


def _tag(row):
    return "%s/%s '%s' (%s)" % (row["mid"], row["no"], row["title"], row["model"])


def test_the_scan_finds_every_submodule(registry):
    """A guard on the guard - an empty scan would pass everything below."""
    rows = registry["rows"]
    assert len({r["mid"] for r in rows}) == 67
    assert len(rows) >= 590


# --- the reported page -------------------------------------------------------


def test_the_estimate_submodule_captures_an_estimate(registry):
    row = _row(registry, "M01", "6")
    assert row["title"] == "Estimate & Customer Approval Loop"
    assert row["model"] == "fix.estimate"
    assert row["create"] == {
        "screen": "M01-form-estimate",
        "label": "Diagnostic Estimate Request",
    }


def test_the_estimate_submodule_names_its_form_and_its_report(registry):
    """'Forms Capturing It' and 'Reports Measuring It' were empty on a page
    whose module declares both - and each chip must open something."""
    row = _row(registry, "M01", "6")
    assert row["forms"] == ["Diagnostic Estimate Request"]
    assert row["reports"] == ["Estimate Conversion Funnel"]
    assert registry["chips"]["M01:" + row["forms"][0]] == "M01-form-estimate"
    assert registry["routes"]["M01:" + row["reports"][0]] == "M01-rpt-estfunnel"


def test_a_submodule_on_the_modules_own_record_keeps_the_module_button(registry):
    assert _row(registry, "M01", "1")["create"] == {"module": True}


def test_a_submodule_whose_lists_refuse_new_offers_no_button(registry):
    """M01-fault is `create: false`: fault codes are not made in M01, so the
    page must not offer to make anything - least of all a service order."""
    row = _row(registry, "M01", "4")
    assert row["model"] == "fix.fault.code"
    assert row["create"] is None


# --- the rule, for every sub-module of every module --------------------------


def test_no_submodule_page_offers_another_records_button(registry):
    """The module's button appears only where the sub-module's record IS the
    module's; everywhere else the page offers its own form or nothing."""
    wrong = [
        _tag(r) + " shows the %s button" % r["moduleModel"]
        for r in registry["rows"]
        if r["create"] and r["create"].get("module") and r["model"] != r["moduleModel"]
    ]
    assert not wrong, "\n  ".join(wrong)


def test_an_offered_form_is_a_form_of_the_submodules_own_record(registry):
    """A DERIVED "+ New" is a form of the page's own record. A page may name
    its form itself (`create: '<form screen>'`) when what it captures is a
    related record - a test result on a job in testing (M31/7), an appeal on
    a claim decision (M09/9), a hold on an order (M01/9): that is a choice
    written in the mapping, still a real in-workspace form."""
    offered = [r for r in registry["rows"] if r["create"] and r["create"].get("screen")]
    assert len(offered) >= 300, "only %d sub-modules resolve a form of their own" % len(offered)
    bad = [
        "%s -> %s is a %s on %s" % (_tag(r), r["create"]["screen"], r["formKind"], r["formModel"])
        for r in offered
        if r["formKind"] != "model_form" or (r["formModel"] != r["model"] and not r["declared"])
    ]
    assert not bad, "\n  ".join(bad)
    unlabelled = [_tag(r) for r in offered if not r["create"].get("label")]
    assert not unlabelled, "\n  ".join(unlabelled)


def test_an_offered_form_saves_through_a_served_model(registry):
    """The form saves with /p03/model/write, which serves SURFACES only: a
    button onto an unserved model would open a form that cannot load."""
    bad = sorted(
        {
            "%s -> %s not served by /p03/model/*" % (_tag(r), r["model"])
            for r in registry["rows"]
            if r["create"] and r["create"].get("screen") and r["model"] not in api.SURFACES
        }
    )
    assert not bad, "\n  ".join(bad)


def test_the_page_renders_the_submodule_button():
    """Wiring guard only (the rule itself is executed above): the Function
    Register header must render fregNewLabel / onFregNew, not the module's."""
    xml = (SRC / "p03_workspace.xml").read_text(encoding="utf-8")
    head = xml[xml.index("VIEW C: SUB-MODULE CAPABILITY VIEW") :]
    head = head[: head.index("Screens Executing this Sub-Module")]
    assert 't-on-click="onFregNew"' in head
    assert "onModuleNew" not in head


# --- the form the button opens captures the estimate's lines -----------------


class FakeRequest:
    def __init__(self, env):
        self.env = env


@pytest.fixture
def call():
    patchers = []

    def _call(env, route, **kw):
        p = mock.patch.object(api, "request", FakeRequest(env))
        p.start()
        patchers.append(p)
        return getattr(api.P03GenericApiController(), route)(**kw)

    yield _call
    for p in patchers:
        p.stop()


def test_the_m01_estimate_form_declares_its_lines(registry, odoo_env):
    grid = registry["estimateForm"].get("lines")
    assert grid and grid["field"] == "line_ids", "M01-form-estimate shows no estimate lines"
    assert not grid.get("readonlyGrid")
    line_fields = odoo_env["fix.estimate.line"]._fields
    names = [f["name"] for f in grid["fields"]]
    assert [n for n in names if n not in line_fields] == []
    # what a line cannot be saved without
    assert {"line_type", "description", "quantity", "unit_price"} <= set(names)
    assert "line_ids" in api.SURFACES["fix.estimate"]["writable"]


def test_an_estimate_saved_from_the_m01_form_carries_its_lines(registry, odoo_env, call):
    """The whole point: without lines the model refuses to send the estimate.
    Loads and saves exactly as the form does - its own declared grid."""
    env = odoo_env
    grid = registry["estimateForm"]["lines"]
    lead = env["crm.lead"].create({"name": "M01 estimate lines", "type": "opportunity"})
    est = env["fix.estimate"].create({"lead_id": lead.id})
    with pytest.raises(UserError, match="no parts, labour or diagnostic lines"):
        est._check_has_lines("sent")

    shown = call(
        env,
        "model_form",
        model="fix.estimate",
        fields=[{"name": "discount"}],
        record_id=est.id,
        lines={"field": grid["field"], "fields": grid["fields"]},
    )
    assert "error" not in shown, shown
    assert [f["name"] for f in shown["lines"]["fields"]] == [f["name"] for f in grid["fields"]]
    assert shown["lines"]["rows"] == []

    rows = [
        {"line_type": "part", "description": "Display assembly", "quantity": 1, "unit_price": 4200},
        {"line_type": "labour", "description": "Bench labour", "quantity": 2, "unit_price": 500},
        {
            "line_type": "diagnostic",
            "description": "Diagnostic fee",
            "quantity": 1,
            "unit_price": 300,
        },
    ]
    assert all(set(r) <= {f["name"] for f in grid["fields"]} for r in rows)
    saved = call(
        env,
        "model_write",
        model="fix.estimate",
        record_id=est.id,
        values={},
        lines={"field": grid["field"], "rows": [{"values": r} for r in rows], "removed": []},
    )
    assert "error" not in saved, saved
    est.invalidate_recordset()
    assert len(est.line_ids) == 3
    assert (est.parts_total, est.labour_total, est.diagnostic_total) == (4200.0, 1000.0, 300.0)
    est._check_has_lines("sent")  # no longer refused
