# cd_vehicle_dispatch — the dispatch gate as a dispatcher meets it on screen.
#
# The gate reads vehicle_id / vehicle_driver_id on the field order, and neither
# was on any screen, so on screen it never ran. Each test drives the endpoints
# the workspace calls as a NON-ADMIN dispatcher; M02's screens are read by
# evaluating static/src/a02/m02.js with node.
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
from odoo.addons.cd_vehicle_dispatch.models.fix_field_order_vehicle import REQUIRE_VEHICLE_PARAM
from odoo.addons.cd_vehicle_dispatch.tests.test_a07_p0_dispatch_bridge import (
    refused,
    w,  # noqa: F401 - the fixture
)

SRC = Path(portal.__file__).parent / "static" / "src" / "a02"
OFFICER = "fleet.fleet_group_user"


@pytest.fixture(scope="module")
def m02_js(tmp_path_factory):
    node = shutil.which("node")
    assert node, "node evaluates the screens: without it these tests prove nothing"
    tmp = tmp_path_factory.mktemp("m02js")
    (tmp / "m02.mjs").write_text((SRC / "m02.js").read_text(encoding="utf-8"), "utf-8")
    (tmp / "run.mjs").write_text(
        "import * as M from './m02.mjs';\n"
        "console.log(JSON.stringify({module: M.MODULE, screens: M.SCREENS}));\n",
        "utf-8",
    )
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our probe file
        [node, str(tmp / "run.mjs")],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=60,
    )
    return json.loads(out.stdout)


def offered(js, screen):
    return {fld["name"]: fld for sec in js["screens"][screen]["sections"] for fld in sec["fields"]}


@pytest.fixture
def ui(w, monkeypatch):  # noqa: F811
    cls = api.P03GenericApiController
    ctl = cls()

    def call(name, user, **kw):
        env = w.env(user=user.id, su=False)
        # Each request starts on a cold cache: what the superuser fixture left
        # there would hide an access refusal the real user would meet.
        env.invalidate_all()
        monkeypatch.setattr(api, "request", types.SimpleNamespace(env=env))
        fn = getattr(cls, name)
        return getattr(fn, "original_endpoint", fn)(ctl, **kw)

    return types.SimpleNamespace(
        records=lambda user, **kw: call("model_records", user, **kw),
        form=lambda user, **kw: call("model_form", user, **kw),
        write=lambda user, **kw: call("model_write", user, **kw),
        action=lambda user, **kw: call("model_action", user, **kw),
    )


def dispatch(ui, w, rec, emp=None):  # noqa: F811
    """The workspace dispatches by saving a fix.dispatch.decision (M02 capture
    audit 18 Nov: a bare action_dispatch skipped the engine's first choice and
    the override reason, BRU-FSM-04). The decision runs action_dispatch, so the
    M46 fleet gate is met here exactly as on the board."""
    res = ui.write(
        w.ud,
        model="fix.dispatch.decision",
        values={
            "field_order_id": rec.id,
            "technician_id": (emp or w.ea).id,
            # kept only when the engine ranked someone else first
            "override_reason": "other",
            "override_notes": "M46 operability test",
        },
    )
    return dict(res, success="error" not in res)


# =========================================================== 1: the gate on screen
def test_1_the_order_form_offers_the_vehicle_and_the_driver(w, ui, m02_js):  # noqa: F811
    form = offered(m02_js, "M02-form-wo")
    for name in ("vehicle_id", "vehicle_driver_id"):
        assert not form[name].get("readonly"), name
        assert name in api.SURFACES["fix.field.order"]["writable"], name
    rec = w.fo()
    out = ui.form(
        w.ud,
        model=rec._name,
        record_id=rec.id,
        fields=[{"name": "vehicle_id"}, {"name": "vehicle_driver_id"}],
    )
    choices = {f["name"]: {c["id"] for c in f["choices"]} for f in out["fields"]}
    assert w.good.id in choices["vehicle_id"] and w.driver.id in choices["vehicle_driver_id"]


def test_1_an_expired_insurance_van_is_refused_once_the_order_names_it(w, ui):  # noqa: F811
    van = w.vehicle("A7M46D-INS")
    insurance = van.document_ids.filtered(lambda d: d.doc_type == "insurance")
    w.env.flush_all()
    w.env.cr.execute(
        "UPDATE fix_vehicle_document SET valid_to = %s WHERE id = %s",
        (w.today - timedelta(days=1), insurance.id),
    )
    w.env.invalidate_all()
    rec = w.fo()
    res = ui.write(w.ud, model=rec._name, record_id=rec.id, values={"vehicle_id": van.id})
    assert "error" not in res, res
    res = dispatch(ui, w, rec)
    assert res["success"] is False
    assert "not dispatchable" in res["error"] and "Insurance" in res["error"]
    rec.invalidate_recordset()
    assert rec.state == "pending_dispatch" and not rec.vehicle_assignment_id
    # another van on the same form, and the same button goes through
    res = ui.write(w.ud, model=rec._name, record_id=rec.id, values={"vehicle_id": w.good.id})
    assert "error" not in res, res
    res = dispatch(ui, w, rec)
    assert res["success"], res
    rec.invalidate_recordset()
    assert rec.state == "dispatched" and rec.vehicle_assignment_id.vehicle_id == w.good


def test_1_a_live_order_moved_onto_a_bad_van_is_refused_on_save(w, ui):  # noqa: F811
    rec = w.fo(vehicle_id=w.good.id)
    assert dispatch(ui, w, rec)["success"]
    res = ui.write(w.ud, model=rec._name, record_id=rec.id, values={"vehicle_id": w.bad.id})
    assert "not dispatchable" in res["error"]
    rec.invalidate_recordset()
    assert rec.vehicle_id == w.good


def test_1_switch_on_and_no_vehicle_says_what_to_do(w, ui):  # noqa: F811
    w.env["ir.config_parameter"].sudo().set_param(REQUIRE_VEHICLE_PARAM, "True")
    rec = w.fo()
    res = dispatch(ui, w, rec)
    assert res["success"] is False
    assert rec.name in res["error"] and "Vehicle" in res["error"] and "save" in res["error"]
    rec.invalidate_recordset()
    assert rec.state == "pending_dispatch"
    # a van with no driver is refused too, and the driver named on the form clears it
    van = w.vehicle("A7M46D-NODRV")
    res = ui.write(w.ud, model=rec._name, record_id=rec.id, values={"vehicle_id": van.id})
    assert "error" not in res, res
    res = dispatch(ui, w, rec)
    assert res["success"] is False and "no driver" in res["error"]
    res = ui.write(
        w.ud, model=rec._name, record_id=rec.id, values={"vehicle_driver_id": w.driver.id}
    )
    assert "error" not in res, res
    res = dispatch(ui, w, rec)
    assert res["success"], res
    rec.invalidate_recordset()
    assert rec.vehicle_assignment_id.driver_id == w.driver


# =========================================================== 3: the re-dispatch flag
def test_3_the_flag_and_the_conflict_are_on_the_screens(w, ui, m02_js):  # noqa: F811
    screens = {s["id"] for g in m02_js["module"]["groups"] for s in g["screens"]}
    assert "M02-redispatch" in screens
    cfg = m02_js["screens"]["M02-redispatch"]
    assert cfg["domain"] == [["redispatch_required", "=", True]]
    for sid in ("M02-record", "M02-unassigned", "M02-redispatch"):
        cols = m02_js["screens"][sid]["cols"]
        assert {"vehicle_id", "redispatch_required"} <= set(cols), sid
        assert not set(cols) - set(w.env["fix.field.order"]._fields), sid
    form = offered(m02_js, "M02-form-wo")
    for name in ("redispatch_required", "redispatch_reason", "redispatch_offroad_id"):
        assert form[name]["readonly"], name
        assert name not in api.SURFACES["fix.field.order"]["writable"], name

    rec = w.fo(vehicle_id=w.good.id, vehicle_driver_id=w.driver.id)
    other = w.fo(vehicle_id=w.vehicle("A7M46D-OTHER").id)
    assert dispatch(ui, w, rec)["success"]
    off = w.env["fix.vehicle.offroad"].create({"vehicle_id": w.good.id, "reason": "Brakes failed"})
    w.env["fix.field.order"].consume_vehicle_off_road({"aggregate_id": off.id})

    out = ui.records(w.ud, model=rec._name, cols=cfg["cols"], domain=cfg["domain"])
    ids = {r["id"] for r in out["rows"]}
    assert rec.id in ids and other.id not in ids
    row = next(r for r in out["rows"] if r["id"] == rec.id)
    assert row["vehicle_id"]["id"] == w.good.id and row["redispatch_required"] is True
    assert "Brakes failed" in row["redispatch_reason"]

    # the conflict shows on the booking
    booking = rec.vehicle_assignment_id
    out = ui.records(
        w.ud,
        model=booking._name,
        cols=["offroad_conflict_id", "offroad_conflict_note"],
        domain=[["id", "=", booking.id]],
    )
    assert off.reason in out["rows"][0]["offroad_conflict_note"]

    # the dispatcher resolves it on the form, the flag clears, and it says who
    fresh = w.vehicle("A7M46D-FRESH")
    res = ui.write(w.ud, model=rec._name, record_id=rec.id, values={"vehicle_id": fresh.id})
    assert "error" not in res, res
    rec.invalidate_recordset()
    assert not rec.redispatch_required and rec.redispatch_cleared_by_id == w.ud
    assert ui.records(w.ud, model=rec._name, cols=cfg["cols"], domain=cfg["domain"])["count"] == 0


# =========================================================== 2: a booking an order holds
def test_2_a_booking_held_by_a_live_order_moves_on_the_order_not_here(w, ui):  # noqa: F811
    officer = (
        w.env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "a7m46d_off",
                "login": "a7m46d_off",
                "group_ids": [(6, 0, [w.env.ref("base.group_user").id, w.env.ref(OFFICER).id])],
                "operating_unit_ids": [(6, 0, w.ou.ids)],
                "default_operating_unit_id": w.ou.id,
            }
        )
    )
    rec = w.fo(vehicle_id=w.good.id, vehicle_driver_id=w.driver.id)
    assert dispatch(ui, w, rec)["success"]
    booking = rec.vehicle_assignment_id
    args = {"model": booking._name, "ids": booking.ids}
    res = ui.action(officer, **args, method="action_release", kwargs={"reason": "x"})
    assert not res["success"] and rec.name in res["error"]
    res = ui.action(
        officer,
        **args,
        method="action_reassign",
        kwargs={"vehicle": w.vehicle("A7M46D-SW").license_plate, "reason": "x"},
    )
    assert not res["success"] and rec.name in res["error"]
    other = w.vehicle("A7M46D-SW2")
    res = ui.write(
        officer, model=booking._name, record_id=booking.id, values={"vehicle_id": other.id}
    )
    assert rec.name in res["error"]
    booking.invalidate_recordset()
    assert booking.vehicle_id == w.good and booking.active
    # once the order lets go of the van the booking is the dispatcher's to drop
    rec.with_user(w.ud).action_cancel(reason="Customer cancelled")
    assert not w.env["fix.vehicle.assignment"].search_count([("id", "=", booking.id)])


def test_1_only_a_dispatcher_changes_the_vehicle(w, ui):  # noqa: F811
    rec = w.fo(vehicle_id=w.good.id)
    assert dispatch(ui, w, rec)["success"]
    other = w.vehicle("A7M46D-TECH")
    res = ui.write(w.ua, model=rec._name, record_id=rec.id, values={"vehicle_id": other.id})
    assert "dispatcher" in res["error"]
    assert refused(w.env, lambda: rec.with_user(w.ua).write({"vehicle_id": other.id}))
    # the technician's own edit, with the form echoing the vehicle, still saves
    res = ui.write(
        w.ua,
        model=rec._name,
        record_id=rec.id,
        values={"vehicle_id": w.good.id, "notes": "Gate code 1234"},
    )
    assert "error" not in res, res
