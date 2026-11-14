"""M31 audit, 14 Nov 2026: every sub-module page captures the RELEVANT record.

The 12 Nov pass gave all nine pages a button, but two buttons captured the
wrong thing:

- 3 "Bench Allocation & Queue" offered "+ New Bench Allocation", which made
  a new bench (master data). A repair job could not be allocated to a bench
  and a technician from the page (FR-WSR-011/015, BRU-WSR-02/06).
- 7 "Testing & Burn-In" offered "Test Protocol Result", which filed an
  attachment. No protocol, no limits, no measured value (FR-WSR-031/032).

The Job Routing form also wrote the bench directly, past every rule of the
bench's own assignment (maintenance, closed, full, level).

Each capture is saved through the real controller as a workshop user, never as
the superuser. ``odoo_env`` (addons/conftest.py): fix_test, rolled back
after every test.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from .test_m31_submodule_capture import m31, screens, ui  # noqa: F401 - fixtures


def _fragment_subs():
    """The fragment's sub-module mappings, read by node."""
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
        "const dir = mkdtempSync(join(tmpdir(), 'm31sub'));\n"
        "const file = join(dir, 'm31.mjs');\n"
        "writeFileSync(file, readFileSync(process.argv[1], 'utf-8'));\n"
        "const M = await import(pathToFileURL(file).href);\n"
        "console.log(JSON.stringify({ sub: M.MODULE.freg.sub, chips: M.FORM_CHIPS }));\n"
    )
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary, inline probe, our file
        [node, "--input-type=module", "-e", probe, str(src)],
        capture_output=True,
        encoding="utf-8",
        check=True,
        timeout=60,
    )
    return json.loads(out.stdout)


def test_the_registry_forms_capture_what_they_name(screens):  # noqa: F811
    assert screens["M31-form-allocate"]["saveAction"]["method"] == "action_allocate_bench"
    assert screens["M31-form-testresult"]["model"] == "fix.workshop.test.result"
    assert screens["M31-form-bench"]["title"] == "Bench Master"
    assert screens["M31-form-evidence"]["title"] == "Test Evidence"
    data = _fragment_subs()
    subs = {s[0]: s[3] for s in data["sub"]}
    # the bench master moved to the masters page; the evidence upload stays on 7
    assert "Bench Master" in subs["2"]["forms"]
    assert {"Test Protocol", "Test Evidence"} <= set(subs["7"]["forms"])
    chips = data["chips"]
    assert chips["M31:Bench Allocation"] == "M31-form-allocate"
    assert chips["M31:Test Protocol Result"] == "M31-form-testresult"


# --- 3 Bench Allocation & Queue ------------------------------------------------


def _allocate(ui, user, job, bench, technician=None, note=None):  # noqa: F811
    kwargs = {"bench_id": bench.id}
    if technician:
        kwargs["technician_id"] = technician.id
    if note:
        kwargs["note"] = note
    return ui.action(
        user, model="fix.workshop.job", ids=[job.id], method="action_allocate_bench", kwargs=kwargs
    )


def _chatter(job, text):
    return any(text in (m.body or "") for m in job.message_ids)


def test_allocation_puts_a_waiting_job_on_a_bench(m31, ui, screens):  # noqa: F811
    cfg = screens["M31-form-allocate"]
    job = m31.job()
    listed = ui.records(
        m31.tech, model="fix.workshop.job", cols=["name"], domain=cfg["pickRecord"]["domain"]
    )
    assert job.id in {r["id"] for r in listed["rows"]}

    res = _allocate(ui, m31.tech, job, m31.l1, m31.tech2_emp, "Taken from the express queue")
    assert res["success"], res
    job.invalidate_recordset()
    assert (job.bench_id, job.technician_id) == (m31.l1, m31.tech2_emp)
    assert job.bench_handover_note == "Taken from the express queue"
    assert _chatter(job, "Allocated to bench %s" % m31.l1.code)


def test_reallocation_hands_the_job_over_and_frees_the_old_bench(m31, ui):  # noqa: F811
    job = m31.job()
    job.sudo().write({"state": "intake"})  # an active job counts on its bench
    assert _allocate(ui, m31.tech, job, m31.l1)["success"]
    m31.l1.invalidate_recordset()
    before = m31.l1.current_job_count
    assert before >= 1
    res = _allocate(ui, m31.tech, job, m31.l2, note="L1 bench needed for the express queue")
    assert res["success"], res
    for rec in (job, m31.l1, m31.l2):
        rec.invalidate_recordset()
    assert job.bench_id == m31.l2
    assert m31.l1.current_job_count == before - 1
    assert _chatter(job, "(from %s)" % m31.l1.code)


def test_allocation_refuses_a_bench_that_cannot_take_the_job(m31, ui):  # noqa: F811
    env = m31.env
    job = m31.job(level="l2")
    # below the job's level
    res = _allocate(ui, m31.tech, job, m31.l1)
    assert not res["success"] and "L2 capability" in res["error"], res
    # another workshop's bench
    other = env["fix.workshop"].create(
        {"code": "WS-CAP-O", "name": "Other Depot", "name_bn": "ডিপো"}
    )
    foreign = env["fix.workshop.bench"].create(
        {
            "workshop_id": other.id,
            "code": "B-CAP-O",
            "name": "O",
            "name_bn": "ও",
            "repair_level": "l3",
        }
    )
    res = _allocate(ui, m31.tech, job, foreign)
    assert not res["success"] and "belongs to" in res["error"], res
    # full: one place, held by an active job
    small = env["fix.workshop.bench"].create(
        {
            "workshop_id": m31.workshop.id,
            "code": "B-CAP-S",
            "name": "S",
            "name_bn": "এস",
            "repair_level": "l3",
            "max_concurrent_jobs": 1,
        }
    )
    first = m31.job(level="l2")
    first.sudo().write({"state": "intake"})
    assert _allocate(ui, m31.tech, first, small)["success"]
    res = _allocate(ui, m31.tech, job, small)
    assert not res["success"] and "full" in res["error"], res
    # under maintenance
    m31.l2.action_set_maintenance(reason="tip replacement")
    res = _allocate(ui, m31.tech, job, m31.l2)
    assert not res["success"] and "Maintenance" in res["error"], res
    job.invalidate_recordset()
    assert not job.bench_id


def test_job_routing_can_no_longer_bypass_the_bench_rules(m31, ui):  # noqa: F811
    """The routing form writes the bench: the same rules apply to it."""
    job = m31.job(level="l2")
    res = ui.write(
        m31.tech, model="fix.workshop.job", record_id=job.id, values={"bench_id": m31.l1.id}
    )
    assert "error" in res and "L2 capability" in res["error"], res
    m31.l2.action_set_maintenance(reason="calibration")
    res = ui.write(
        m31.tech, model="fix.workshop.job", record_id=job.id, values={"bench_id": m31.l2.id}
    )
    assert "error" in res, res
    job.invalidate_recordset()
    assert not job.bench_id


def test_the_bench_picker_hides_benches_out_of_service():
    from odoo.addons.cd_p03_portal.controllers.a02 import m31 as surface

    picker = surface.SURFACES["fix.workshop.job"]["pickers"]["bench_id"]
    assert picker == [("state", "in", ("available", "occupied"))]


# --- 7 Testing & Burn-In ------------------------------------------------------


def _protocol(m31):  # noqa: F811
    vbus = {
        "code": "V1",
        "name": "VBUS",
        "unit": "V",
        "has_limits": True,
        "lower_limit": 4.75,
        "upper_limit": 5.25,
    }
    icon = {"code": "C1", "name": "Charge icon shows", "has_limits": False, "sequence": 20}
    return (
        m31.env["fix.workshop.test.protocol"]
        .with_user(m31.supv)
        .create(
            {
                "code": "TP-CAP-1",
                "name": "Smartphone charging",
                "device_type": "smartphone",
                "repair_level": "l2",
                "burn_in_minutes": 240,
                "step_ids": [(0, 0, vbus), (0, 0, icon)],
            }
        )
    )


def test_a_protocol_is_kept_by_a_workshop_manager(m31, ui):  # noqa: F811
    step = {
        "name": "Rail PP3V3",
        "unit": "V",
        "has_limits": True,
        "lower_limit": 3.2,
        "upper_limit": 3.4,
    }
    res = ui.write(
        m31.supv,
        model="fix.workshop.test.protocol",
        values={"code": "TP-CAP-UI", "name": "Laptop no power"},
        lines={"field": "step_ids", "rows": [{"values": step}], "removed": []},
    )
    assert "error" not in res, res
    proto = m31.env["fix.workshop.test.protocol"].browse(res["id"])
    assert proto.step_ids.mapped("name") == ["Rail PP3V3"]
    refused = ui.write(
        m31.tech, model="fix.workshop.test.protocol", values={"code": "TP-X", "name": "x"}
    )
    assert "error" in refused


def test_a_test_result_is_judged_by_the_protocol_limits(m31, ui):  # noqa: F811
    proto = _protocol(m31)
    vbus, icon = proto.step_ids.sorted("sequence")
    job = m31.job(level="l2")

    def record(step, **vals):
        res = ui.write(
            m31.tech,
            model="fix.workshop.test.result",
            values={"job_id": job.id, "step_id": step.id, **vals},
        )
        assert "error" not in res, res
        return m31.env["fix.workshop.test.result"].browse(res["id"])

    inside = record(vbus, measured_value=5.02)
    # a tick does not pass a reading outside the limits
    outside = record(vbus, measured_value=5.6, observed_pass=True)
    check = record(icon, observed_pass=True)
    assert (inside.passed, outside.passed, check.passed) == (True, False, True)
    assert inside.tested_by_id == m31.tech and inside.protocol_id == proto
    job.invalidate_recordset()
    assert (job.test_result_count, job.test_failed_count) == (3, 1)


def test_results_are_fixed_once_the_job_passed_qc(m31, ui):  # noqa: F811
    proto = _protocol(m31)
    job = m31.job(level="l2")
    step = proto.step_ids.sorted("sequence")[0]
    res = ui.write(
        m31.tech,
        model="fix.workshop.test.result",
        values={"job_id": job.id, "step_id": step.id, "measured_value": 5.0},
    )
    assert "error" not in res, res
    m31.env.cr.execute("UPDATE fix_workshop_job SET qc_passed = true WHERE id = %s", (job.id,))
    job.invalidate_recordset()
    res = ui.write(
        m31.tech,
        model="fix.workshop.test.result",
        record_id=res["id"],
        values={"measured_value": 4.0},
    )
    assert "error" in res and "passed QC" in res["error"], res
    res = ui.write(
        m31.tech,
        model="fix.workshop.test.result",
        values={"job_id": job.id, "step_id": step.id, "measured_value": 5.0},
    )
    assert "error" in res, res
