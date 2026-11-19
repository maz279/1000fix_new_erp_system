# A07 M45-1 (live blocker): cd_workshop.qc_requires_instrument is on, and a QC pass needs
# an instrument. Can a QC Inspector name one on the M31 screen? Driven through the same
# endpoints the workspace calls, with the form schema read from static/src/a02/m31.js.
from __future__ import annotations

import json
import shutil
import subprocess
import types
from datetime import timedelta
from pathlib import Path

import odoo.addons.cd_p03_portal as portal
import odoo.addons.cd_p03_portal.controllers.p03_generic_api as api
import pytest
from odoo import fields

from . import test_a02_p0_m31 as a02
from ._m45_decided import calibrations_decided  # noqa: F401 - autouse fixture
from .test_a07_p0_m45_qc import PARAM, _meter

m31 = a02.m31
_qc_ready = a02._qc_ready
SRC = Path(portal.__file__).parent / "static" / "src" / "a02" / "m31.js"


@pytest.fixture(scope="module")
def form():
    node = shutil.which("node")
    assert node, "node evaluates the screens: without it these tests prove nothing"
    probe = (
        "import { pathToFileURL } from 'node:url';\n"
        "import { readFileSync, writeFileSync, mkdtempSync } from 'node:fs';\n"
        "import { tmpdir } from 'node:os';\n"
        "import { join } from 'node:path';\n"
        "const dir = mkdtempSync(join(tmpdir(), 'm31js'));\n"
        "const file = join(dir, 'm31.mjs');\n"
        "writeFileSync(file, readFileSync(process.argv[1], 'utf-8'));\n"
        "const M = await import(pathToFileURL(file).href);\n"
        "console.log(JSON.stringify(M.SCREENS['M31-form-job']));\n"
    )
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary, inline probe, our file
        [node, "--input-type=module", "-e", probe, str(SRC)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=60,
    )
    return json.loads(out.stdout)


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
        form=lambda user, **kw: call("model_form", user, **kw),
        write=lambda user, **kw: call("model_write", user, **kw),
        action=lambda user, **kw: call("model_action", user, **kw),
        lookup=lambda user, **kw: call("model_lookup", user, **kw),
    )


def _fields(form):
    return [f for section in form["sections"] for f in section["fields"]]


def _save(ui, user, form, job, **changes):
    """What the browser's formSave posts: every field the form holds."""
    out = ui.form(user, model=form["model"], fields=_fields(form), record_id=job.id)
    assert "error" not in out, out
    held = {**out["record"], **changes}
    values = {
        f["name"]: held[f["name"]]
        for f in _fields(form)
        if held.get(f["name"]) is not None and held.get(f["name"]) != ""
    }
    return ui.write(user, model=form["model"], record_id=job.id, values=values)


def test_a_qc_inspector_names_the_instrument_on_the_form_and_passes(m31, ui, form):
    """The whole path, as the QC Inspector, with the live switch on."""
    m31.env["ir.config_parameter"].sudo().set_param(PARAM, "True")
    meter = _meter(m31, "A7QCF-OK")
    job = m31.job()
    _qc_ready(m31, job)
    assert job.state == "qc_pending" and not job.equipment_id

    # the field sits on a tab that exists, and is editable by the inspector
    field = next(f for f in _fields(form) if f["name"] == "equipment_id")
    assert not field.get("readonly")
    section = next(s for s in form["sections"] if field in s["fields"])
    assert section["tab"] in {t["id"] for t in form["tabs"]}
    out = ui.form(m31.qc, model=form["model"], fields=_fields(form), record_id=job.id)
    meta = next(f for f in out["fields"] if f["name"] == "equipment_id")
    assert meta["readonly"] is False

    # the switch refuses a pass with no instrument, and says what to do
    refused = ui.action(
        m31.qc,
        model=job._name,
        ids=job.ids,
        method="action_pass_qc",
        kwargs={"notes": "Rails nominal"},
    )
    assert refused["success"] is False and "instrument" in refused["error"]
    assert job.state == "qc_pending"

    # he names it through the form save, then passes
    res = _save(ui, m31.qc, form, job, equipment_id=meter.id)
    assert "error" not in res, res
    assert job.equipment_id == meter
    done = ui.action(
        m31.qc,
        model=job._name,
        ids=job.ids,
        method="action_pass_qc",
        kwargs={"notes": "Rails nominal"},
    )
    assert done["success"] is True, done
    assert (job.state, job.qc_passed) == ("ready", True)
    use = m31.env["fix.equipment.usage"].search(
        [("equipment_id", "=", meter.id), ("source_res_id", "=", job.id)]
    )
    assert len(use) == 1 and use.qc_result == "pass"

    # the instrument is measurement evidence now: the form cannot swap it
    other = _meter(m31, "A7QCF-OTHER")
    swapped = _save(ui, m31.supv, form, job, equipment_id=other.id)
    assert "error" in swapped
    assert job.equipment_id == meter


def test_the_picker_offers_instruments_in_use_not_retired_or_out_of_service(m31, ui, form):
    today = fields.Date.today()
    fit = _meter(m31, "A7QCF-FIT")
    oos = _meter(m31, "A7QCF-OOS")
    m31.env["fix.equipment.oos"].create({"equipment_id": oos.id, "reason": "fault"})
    retired = _meter(m31, "A7QCF-RET")
    retired.sudo()._guarded().write({"operational_status": "retired"})
    out = ui.form(m31.qc, model=form["model"], fields=_fields(form))
    meta = next(f for f in out["fields"] if f["name"] == "equipment_id")
    assert meta["remote"] is False
    offered = {c["id"] for c in meta["choices"]}
    assert fit.id in offered
    assert oos.id not in offered and retired.id not in offered
    found = ui.lookup(m31.qc, model=form["model"], field="equipment_id", term="A7QCF")
    assert "error" not in found, found
    # a lapsed one still reaches the gate, which refuses it and says why
    lapsed = _meter(
        m31, "A7QCF-LATE", on=today - timedelta(days=400), due=today - timedelta(days=1)
    )
    job = m31.job()
    _qc_ready(m31, job)
    assert "error" not in _save(ui, m31.qc, form, job, equipment_id=lapsed.id)
    refused = ui.action(m31.qc, model=job._name, ids=job.ids, method="action_pass_qc")
    assert refused["success"] is False and "overdue" in refused["error"]
    assert job.state == "qc_pending"
