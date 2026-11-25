"""M31 Function Register: every sub-module page captures its own data.

Reported 2026-11-12 from the M31 workspace: of the nine sub-module pages only
"Testing & Burn-In" had a capture button. Eight offered nothing. The
workshop and bench lists refused "+ New", so neither master could be added
from the workspace. Bench findings, repair actions and
part lines had no input anywhere in the workspace.

The button rule is JavaScript (p03_workspace.js fregCreate). It is executed
here over the real registry, by the cd_p03_portal `registry` fixture. Each
form is then saved through the real controller as a workshop user, never as
the superuser.

``odoo_env`` (addons/conftest.py): fix_test, rolled back after every test.
"""

from __future__ import annotations

import types

import odoo.addons.cd_p03_portal.controllers.p03_generic_api as api
import pytest
from odoo.addons.cd_p03_portal.tests.test_submodule_create_button import (  # noqa: F401 - fixture
    registry,
)

from . import test_a02_p0_m31 as a02

m31 = a02.m31

# sub-module -> (the form its button opens, the button's words)
EXPECTED = {
    "1": ("M31-form-receive", "Receive Device into Workshop"),
    "2": ("M31-form-workshop", "Workshop Facility"),
    # 14 Nov audit: 3 created a new BENCH and 7 filed a generic attachment
    "3": ("M31-form-allocate", "Allocate a Job to a Bench"),
    "4": ("M31-form-routing", "Route or Re-route a Job"),
    "5": ("M31-form-diagnosis", "Record Bench Diagnosis"),
    "6": ("M31-form-part", "Part Fitment"),
    "7": ("M31-form-testresult", "Record a Test Result"),
    # 19 Nov pass 2: page 8 captures the transfer itself (BRU-WSR-14)
    "8": ("M31-form-transfer", "Request a Workshop Transfer"),
    "9": ("M31-form-labour", "Record Labour & Cost"),
}


def _rows(reg):
    return {r["no"]: r for r in reg["rows"] if r["mid"] == "M31"}


def _screens():
    """The fragment's own screens, read by node like the registry fixture."""
    import json
    import shutil
    import subprocess
    from pathlib import Path

    import odoo.addons.cd_p03_portal as portal

    src = Path(portal.__file__).parent / "static" / "src" / "a02" / "m31.js"
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the M31 fragment")
    probe = (
        "import { pathToFileURL } from 'node:url';\n"
        "import { readFileSync, writeFileSync, mkdtempSync } from 'node:fs';\n"
        "import { tmpdir } from 'node:os';\n"
        "import { join } from 'node:path';\n"
        "const dir = mkdtempSync(join(tmpdir(), 'm31cap'));\n"
        "const file = join(dir, 'm31.mjs');\n"
        "writeFileSync(file, readFileSync(process.argv[1], 'utf-8'));\n"
        "const M = await import(pathToFileURL(file).href);\n"
        "console.log(JSON.stringify(M.SCREENS));\n"
    )
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary, inline probe, our file
        [node, "--input-type=module", "-e", probe, str(src)],
        capture_output=True,
        encoding="utf-8",
        check=True,
        timeout=60,
    )
    return json.loads(out.stdout)


@pytest.fixture(scope="module")
def screens():
    return _screens()


@pytest.fixture
def ui(m31, monkeypatch):
    cls = api.P03GenericApiController
    ctl = cls()

    def call(name, user, **kw):
        monkeypatch.setattr(
            api, "request", types.SimpleNamespace(env=m31.env(user=user.id, su=False))
        )
        fn = getattr(cls, name)
        return getattr(fn, "original_endpoint", fn)(ctl, **kw)

    return types.SimpleNamespace(
        records=lambda user, **kw: call("model_records", user, **kw),
        write=lambda user, **kw: call("model_write", user, **kw),
        action=lambda user, **kw: call("model_action", user, **kw),
    )


# --- every page offers its capture -------------------------------------------


def test_every_m31_submodule_offers_its_capture(registry):  # noqa: F811 - the imported fixture
    rows = _rows(registry)
    assert sorted(rows) == sorted(EXPECTED)
    got = {
        no: ((r["create"] or {}).get("screen"), (r["create"] or {}).get("label"))
        for no, r in rows.items()
    }
    assert got == EXPECTED
    assert all(r["formKind"] == "model_form" for r in rows.values())


def test_every_capture_form_shows_fields_of_its_model(screens, odoo_env):
    """A form field the model lacks renders empty and can never be saved."""
    bad = []
    for sid, cfg in screens.items():
        if cfg.get("kind") != "model_form":
            continue
        model_fields = odoo_env[cfg["model"]]._fields
        for section in cfg["sections"]:
            bad += [
                "%s.%s" % (sid, f["name"])
                for f in section["fields"]
                if f["name"] not in model_fields
            ]
        for clause in (cfg.get("pickRecord") or {}).get("domain", []):
            if clause[0] not in model_fields:
                bad.append("%s pick domain %s" % (sid, clause[0]))
    assert not bad, "\n  ".join(bad)


def test_the_repair_order_form_shows_what_the_bench_records(screens):
    names = {f["name"] for s in screens["M31-form-job"]["sections"] for f in s["fields"]}
    assert {"fault_description", "diagnostic_findings", "repair_action_summary"} <= names
    # a blank repair order could not be saved (no reported fault): it is opened, never typed
    assert screens["M31-form-job"]["create"] is False


# --- each capture saves through the workspace, as a workshop user ------------


def test_receive_hands_the_order_over(m31, ui, screens):
    """Sub-module 1: the order is picked from the form's own list, and the
    button runs the M01 hand-over (its rules included)."""
    cfg = screens["M31-form-receive"]
    so = m31.order(state="intake")
    draft = m31.order(state="draft")
    listed = ui.records(
        m31.tech,
        model="fix.service.order",
        cols=cfg["pickRecord"]["cols"],
        domain=cfg["pickRecord"]["domain"],
    )
    ids = {r["id"] for r in listed["rows"]}
    assert so.id in ids and draft.id not in ids

    act = cfg["saveAction"]
    res = ui.action(m31.tech, model="fix.service.order", ids=[so.id], method=act["method"])
    assert res["success"], res
    job = so.workshop_job_ids
    assert len(job) == 1 and job.state == "draft"
    assert (job.device_id, job.customer_id) == (so.device_id, so.customer_id)

    # received once: it no longer waits, and a second hand-over is refused
    again = ui.records(
        m31.tech, model="fix.service.order", cols=["name"], domain=cfg["pickRecord"]["domain"]
    )
    assert so.id not in {r["id"] for r in again["rows"]}
    res = ui.action(m31.tech, model="fix.service.order", ids=[so.id], method=act["method"])
    assert not res["success"]


def test_masters_are_created_by_a_workshop_manager(m31, ui):
    """Sub-modules 2 and 3: the workshop and bench masters (manager-only by ACL)."""
    ws = ui.write(
        m31.supv,
        model="fix.workshop",
        values={
            "code": "WS-CAP-1",
            "name": "Capture Depot",
            "name_bn": "ডিপো",
            "workshop_type": "central",
        },
    )
    assert "error" not in ws, ws
    bench = ui.write(
        m31.supv,
        model="fix.workshop.bench",
        values={
            "workshop_id": ws["id"],
            "code": "B-CAP-1",
            "name": "Capture Bench",
            "repair_level": "l2",
        },
    )
    # the Bengali name is NOT NULL: the form marks it required, the save names it
    assert "নাম" in bench.get("error", ""), bench
    bench = ui.write(
        m31.supv,
        model="fix.workshop.bench",
        values={
            "workshop_id": ws["id"],
            "code": "B-CAP-1",
            "name": "Capture Bench",
            "name_bn": "বেঞ্চ",
            "repair_level": "l2",
        },
    )
    assert "error" not in bench, bench
    refused = ui.write(
        m31.tech,
        model="fix.workshop",
        values={"code": "WS-CAP-2", "name": "x", "name_bn": "x", "workshop_type": "central"},
    )
    assert "error" in refused


def test_routing_diagnosis_and_labour_save_on_the_picked_job(m31, ui):
    """Sub-modules 4, 5, 8 and 9: fields of an existing job, each through
    the write whitelist the forms generate."""
    job = m31.job()
    for values in (
        {"repair_level": "l2", "workshop_id": m31.workshop.id, "bench_id": m31.l2.id},
        {
            "diagnostic_findings": "U7000 PMIC short to ground on PP_VDD_MAIN",
            "repair_action_summary": "Replaced U7000, reflowed, rail checked",
        },
        {"sam_standard_minutes": 90, "actual_logged_minutes": 75},
    ):
        res = ui.write(m31.tech, model="fix.workshop.job", record_id=job.id, values=values)
        assert "error" not in res, (values, res)
    # A02 ERP audit M31-F14: the labour figure is not typed on the form; a
    # supervisor records it (only where the workshop has no labour rate)
    res = ui.write(m31.tech, model="fix.workshop.job", record_id=job.id, values={"labour_total": 1})
    assert "error" in res, res
    res = ui.action(
        m31.supv,
        model="fix.workshop.job",
        ids=[job.id],
        method="action_record_labour",
        kwargs={"amount": 800},
    )
    assert res.get("success"), res
    job.invalidate_recordset()
    assert job.repair_level == "l2" and job.bench_id == m31.l2
    assert job.diagnostic_findings.startswith("U7000")
    assert job.labour_total == 800


def test_a_guarded_job_field_is_still_refused(m31, ui):
    job = m31.job()
    res = ui.write(m31.tech, model="fix.workshop.job", record_id=job.id, values={"qc_passed": True})
    assert "error" in res


def test_a_part_fitted_from_the_form_carries_its_standard_cost(m31, ui):
    """Sub-module 6: the line is created, its cost is the part's standard
    cost - a typed cost is not taken."""
    job = m31.job()
    res = ui.write(
        m31.tech,
        model="fix.workshop.part.line",
        values={
            "job_id": job.id,
            "product_id": m31.product.id,
            "quantity": 2,
            "source_origin": "central_warehouse",
            "lot_serial_number": "SN-PART-1",
            "circuit_designator": "U7000",
            "unit_cost": 1,
        },
    )
    assert "error" not in res, res
    line = m31.env["fix.workshop.part.line"].browse(res["id"])
    assert (line.job_id, line.reservation_state) == (job, "draft")
    assert (line.unit_cost, line.subtotal) == (500.0, 1000.0)


def test_the_part_form_offers_open_jobs_only():
    from odoo.addons.cd_p03_portal.controllers.a02 import m31 as surface

    picker = surface.SURFACES["fix.workshop.part.line"]["pickers"]["job_id"]
    assert picker == [("state", "not in", ("delivered", "unrepairable", "cancelled"))]
