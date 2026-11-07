# cd_vehicle_ext — can a person do the M46 job on the P03 workspace?
#
# The A07 build proved its fleet controls by calling methods directly. Each test
# here drives the endpoints the workspace calls (model_form, model_write,
# model_action, model_records, model_lookup) as a NON-ADMIN user with the real
# role; the screens are read by evaluating static/src/a07/m46.js with node.
from __future__ import annotations

import base64
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
from odoo.addons.cd_p03_portal.controllers.a07 import m46 as m46_surface
from odoo.addons.cd_vehicle_ext.tests.test_a07_p1_fleet_controls import (
    LM,
    OFFICER,
    SCAN,
    f,  # noqa: F401 - the fixture
    refused,
)
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox

SRC = Path(portal.__file__).parent / "static" / "src" / "a07"
TIER_2 = "cd_entity_config.group_dofa_tier_2"
REQUIRE_VEHICLE = "cd_vehicle_dispatch.dispatch_requires_vehicle"
PDF = base64.b64encode(b"%PDF-1.4 the certificate itself").decode()


@pytest.fixture(scope="module")
def m46_js(tmp_path_factory):
    node = shutil.which("node")
    assert node, "node evaluates the screens: without it these tests prove nothing"
    tmp = tmp_path_factory.mktemp("m46js")
    (tmp / "m46.mjs").write_text((SRC / "m46.js").read_text(encoding="utf-8"), "utf-8")
    (tmp / "run.mjs").write_text(
        "import * as M from './m46.mjs';\n"
        "console.log(JSON.stringify({module: M.MODULE, screens: M.SCREENS, "
        "chips: M.FORM_CHIPS}));\n",
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


def buttons(js, screen):
    return {a["m"]: a for a in js["screens"][screen].get("actions", [])}


@pytest.fixture
def ui(f, monkeypatch):  # noqa: F811
    cls = api.P03GenericApiController
    ctl = cls()

    def call(name, user, **kw):
        env = f.env(user=user.id, su=False)
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
        lookup=lambda user, **kw: call("model_lookup", user, **kw),
    )


def as_user(f, user):  # noqa: F811
    return f.env(user=user.id, su=False)


def deliver(f, event_type, record, consumer_xmlid):  # noqa: F811
    Outbox = f.env["fix.event.outbox"].sudo()
    row = Outbox.search(
        [
            ("event_type", "=", event_type),
            ("aggregate", "=", record._name),
            ("aggregate_id", "=", record.id),
        ],
        order="id desc",
        limit=1,
    )
    assert row, "%s was not published for %s" % (event_type, record.display_name)
    assert Outbox._relay_deliver(f.env.ref(consumer_xmlid).sudo(), row) == ""


def insurer(f, name="A7M46 Green Delta"):  # noqa: F811
    return f.env["res.partner"].create({"name": name, "is_company": True, "is_insurer": True})


def accident(f, user=None, **kw):  # noqa: F811
    vals = {"vehicle_id": f.van.id, "description": "Side collision", "damage_cost": 50000}
    vals.update(kw)
    return f.env["fix.vehicle.accident"].with_user(user or f.clerk).create(vals)


# =========================================================== 2: assignments
def test_2_fleet_officer_books_on_the_form_and_the_gate_applies(f, ui, m46_js):  # noqa: F811
    assert m46_js["screens"]["M46-assign"].get("create") is not False
    assert m46_js["chips"]["M46:__by_screen__"]["M46-assign"] == "M46-form-assignment"
    form = offered(m46_js, "M46-form-assignment")
    for name in ("vehicle_id", "date", "driver_id", "technician_id"):
        assert not form[name].get("readonly")
    assert {"action_release", "action_reassign"} <= set(buttons(m46_js, "M46-assign"))

    good = {"vehicle_id": f.van.id, "date": str(f.today), "driver_id": f.driver.id}
    # a plain employee does not book
    assert "error" in ui.write(f.clerk, model="fix.vehicle.assignment", values=good)
    res = ui.write(f.officer, model="fix.vehicle.assignment", values=good)
    assert "error" not in res, res
    booking = f.env["fix.vehicle.assignment"].browse(res["id"])
    assert (booking.vehicle_id, booking.driver_id, booking.date) == (f.van, f.driver, f.today)
    # the same van, the same day
    again = ui.write(f.officer, model="fix.vehicle.assignment", values=good)
    assert "overlaps are refused" in again["error"]

    # an uninsured van is refused on create and when an edit points at it
    bad = f.env["fleet.vehicle"].create(
        {"model_id": f.van_model.id, "license_plate": "A7M46-UNINS"}
    )
    out = ui.write(
        f.officer,
        model="fix.vehicle.assignment",
        values={"vehicle_id": bad.id, "date": str(f.today), "driver_id": f.driver.id},
    )
    assert "not dispatchable" in out["error"] and "Insurance" in out["error"]
    out = ui.write(
        f.officer,
        model="fix.vehicle.assignment",
        record_id=booking.id,
        values={"vehicle_id": bad.id},
    )
    assert "not dispatchable" in out["error"]
    booking.invalidate_recordset()
    assert booking.vehicle_id == f.van


def test_2_release_frees_the_day_and_keeps_the_trail(f, ui):  # noqa: F811
    booking = f.assign(f.van, user=f.officer, driver_id=f.driver.id)
    args = {"model": booking._name, "ids": booking.ids, "method": "action_release"}
    assert "reason" in ui.action(f.officer, **args)["error"].lower()
    assert not ui.action(f.clerk, **args, kwargs={"reason": "x"})["success"]
    res = ui.action(f.officer, **args, kwargs={"reason": "Customer postponed"})
    assert res["success"], res
    booking.invalidate_recordset()
    assert booking.state == "released" and not booking.active
    assert booking.released_by_id == f.officer and booking.release_reason == "Customer postponed"
    # the day is free again, and the released booking stays readable on the screen
    fresh = f.assign(f.van, user=f.officer)
    rows = ui.records(
        f.officer,
        model=booking._name,
        cols=["name", "state", "vehicle_id"],
        domain=[["active", "in", [True, False]], ["vehicle_id", "=", f.van.id]],
    )["rows"]
    assert {r["id"] for r in rows} == {booking.id, fresh.id}
    # a released booking is not edited or released again
    out = ui.write(
        f.officer, model=booking._name, record_id=booking.id, values={"driver_id": False}
    )
    assert "error" in out
    assert not ui.action(f.officer, **args, kwargs={"reason": "again"})["success"]


def test_2_reassign_names_people_and_runs_the_gate(f, ui, m46_js):  # noqa: F811
    assert {a["kwarg"] for a in buttons(m46_js, "M46-assign")["action_reassign"]["asks"]} == {
        "vehicle",
        "driver",
        "technician",
        "reason",
    }
    booking = f.assign(f.van, user=f.officer, driver_id=f.driver.id)
    other = f.driver_f("A7M46 Other Driver")
    args = {"model": booking._name, "ids": booking.ids, "method": "action_reassign"}

    def go(user=f.officer, **kw):
        return ui.action(user, **args, kwargs=kw)

    assert not go(user=f.clerk, driver=other.name, reason="Leaver")["success"]
    assert "reason" in go(driver=other.name)["error"].lower()
    assert "Name" in go(reason="nothing changes")["error"]
    assert "A7M46 Nobody" in go(driver="A7M46 Nobody", reason="x")["error"]
    res = go(driver=other.name.lower(), reason="Leaver handed over")
    assert res["success"], res
    booking.invalidate_recordset()
    assert booking.driver_id == other
    assert "Leaver handed over" in booking.message_ids[0].body

    tech = f.env["hr.employee"].create({"name": "A7M46 Technician"})
    # the M59 licence rule still reads the technician a booking is moved to
    assert "BRU-HSE-07" in go(technician=tech.name, reason="Crew change")["error"]
    f.driver_f("A7M46 Tech Licence", employee_id=tech.id)
    res = go(technician=tech.name, reason="Crew change")
    assert res["success"], res
    booking.invalidate_recordset()
    assert booking.technician_id == tech

    # the gate reads the new van: uninsured refused, and the booking stays
    bad = f.env["fleet.vehicle"].create(
        {"model_id": f.van_model.id, "license_plate": "A7M46-UNINS2"}
    )
    out = go(vehicle="a7m46 unins2", reason="Swap")
    assert not out["success"] and "not dispatchable" in out["error"]
    booking.invalidate_recordset()
    assert booking.vehicle_id == f.van
    good = f.vehicle("A7M46-GOOD2")
    assert go(vehicle="A7M46-GOOD2", reason="Swap")["success"]
    booking.invalidate_recordset()
    assert booking.vehicle_id == good and bad.exists()
    # a van already booked that day is an overlap
    third = f.vehicle("A7M46-GOOD3")
    f.assign(third, user=f.officer)
    assert "overlaps are refused" in go(vehicle="A7M46-GOOD3", reason="Swap")["error"]


def test_2_exit_clearance_advice_can_be_followed_on_screen(f, ui):  # noqa: F811
    if "_spine_assets_held" not in dir(f.env["fix.hr.exit"]):
        pytest.skip("cd_asset_workorder_spine not installed")
    leaver = f.driver_f("A7M46 Leaver")
    keep = f.assign(f.van, user=f.officer, driver_id=leaver.id)
    other_van = f.vehicle("A7M46-EXIT")
    drop = f.assign(other_van, user=f.officer, driver_id=leaver.id)
    exit_rec = f.env["fix.hr.exit"].new({"employee_id": leaver.employee_id.id})
    assert len(exit_rec._spine_assets_held()) == 2
    assert ui.action(
        f.officer,
        model=keep._name,
        ids=keep.ids,
        method="action_reassign",
        kwargs={"driver": f.driver.name, "reason": "Leaving"},
    )["success"]
    assert ui.action(
        f.officer,
        model=drop._name,
        ids=drop.ids,
        method="action_release",
        kwargs={"reason": "Leaving"},
    )["success"]
    f.env.invalidate_all()
    assert exit_rec._spine_assets_held() == []


# =========================================================== 4: saved evidence
def test_4_a_frozen_documents_scan_can_be_downloaded(f, ui, m46_js):  # noqa: F811
    res = ui.write(
        f.officer,
        model="fix.vehicle.document",
        values={
            "vehicle_id": f.van.id,
            "doc_type": "route_permit",
            "valid_to": str(f.today + timedelta(days=90)),
            "evidence_file": PDF,
            "evidence_filename": "route-permit-2026.pdf",
        },
    )
    assert "error" not in res, res
    doc = f.env["fix.vehicle.document"].browse(res["id"])
    specs = [{"name": n, "type": "file"} for n in ("evidence_file",)] + [
        {"name": "evidence_filename"}
    ]
    out = ui.form(f.clerk, model=doc._name, record_id=doc.id, fields=specs)
    entry = {e["name"]: e for e in out["fields"]}
    assert entry["evidence_file"]["readonly"] is True, "frozen: the screen shows Download"
    value = out["record"]["evidence_file"]
    value = value.decode() if isinstance(value, bytes) else value
    assert base64.b64decode(value) == base64.b64decode(PDF)
    assert out["record"]["evidence_filename"] == "route-permit-2026.pdf"
    # and frozen means frozen: neither the file nor its name changes
    assert "error" in ui.write(
        f.officer, model=doc._name, record_id=doc.id, values={"evidence_filename": "other.pdf"}
    )


# =========================================================== 5: insurers
def test_5_the_picker_offers_insurers_only(f, ui):  # noqa: F811
    f.env["res.partner"].create({"name": "A7M46 Ordinary Customer"})
    company = insurer(f)
    acc = accident(f)
    out = ui.form(f.clerk, model=acc._name, record_id=acc.id, fields=[{"name": "insurer_id"}])
    field = out["fields"][0]
    labels = {c["label"] for c in field["choices"]}
    assert company.display_name in labels and "A7M46 Ordinary Customer" not in labels
    assert ui.lookup(f.clerk, model=acc._name, field="insurer_id", term="Ordinary") == {"rows": []}
    # the server holds the same line for a hand-made call
    plain = f.env["res.partner"].create({"name": "A7M46 Not An Insurer"})
    res = ui.write(f.clerk, model=acc._name, record_id=acc.id, values={"insurer_id": plain.id})
    assert "insurer" in res["error"].lower()
    res = ui.write(f.clerk, model=acc._name, record_id=acc.id, values={"insurer_id": company.id})
    assert "error" not in res, res


def test_5_a_fleet_officer_adds_an_insurer_from_the_accident_screen(f, ui, m46_js):  # noqa: F811
    assert buttons(m46_js, "M46-accidents")["action_add_insurer"]["kwarg"] == "insurer"
    acc = accident(f)
    args = {"model": acc._name, "ids": acc.ids, "method": "action_add_insurer"}
    assert not ui.action(f.clerk, **args, kwargs={"insurer": "A7M46 New Insurer"})["success"]
    assert not ui.action(f.officer, **args, kwargs={"insurer": "  "})["success"]
    assert ui.action(f.officer, **args, kwargs={"insurer": "A7M46 New Insurer"})["success"]
    acc.invalidate_recordset()
    assert acc.insurer_id.name == "A7M46 New Insurer" and acc.insurer_id.is_insurer
    assert acc.insurer_id.is_company
    # an existing partner is marked, not duplicated
    known = f.env["res.partner"].create({"name": "A7M46 Known Partner Ltd", "is_company": True})
    other = accident(f, vehicle_id=f.vehicle("A7M46-INS2").id)
    res = ui.action(
        f.officer,
        model=other._name,
        ids=other.ids,
        method="action_add_insurer",
        kwargs={"insurer": "a7m46 known partner ltd"},
    )
    assert res["success"], res
    other.invalidate_recordset()
    assert other.insurer_id == known and known.is_insurer
    # the insurers report lists them, with their claims
    pack = m46_surface.REPORTS["insurers"](as_user(f, f.officer))
    names = {row["insurer"] for row in pack["rows"]}
    assert {"A7M46 New Insurer", "A7M46 Known Partner Ltd"} <= names


# =========================================================== 6: no claim
def test_6_an_accident_with_no_claim_closes_and_the_van_returns(f, ui, m46_js):  # noqa: F811
    assert buttons(m46_js, "M46-accidents")["action_close_no_claim"]["kwarg"] == "reason"
    acc = accident(f)
    args = {"model": acc._name, "ids": acc.ids, "method": "action_close_no_claim"}
    why = {"reason": "Own-damage below the excess; workshop repaired it"}
    # the role, the reporter, the reason
    assert not ui.action(f.officer, **args, kwargs=why)["success"]
    reported_by_lm = accident(f, user=f.lm, vehicle_id=f.vehicle("A7M46-OWN").id)
    res = ui.action(
        f.lm,
        model=acc._name,
        ids=reported_by_lm.ids,
        method="action_close_no_claim",
        kwargs=why,
    )
    assert "Segregation of duties" in res["error"]
    assert "reason" in ui.action(f.lm, **args)["error"].lower()

    # before closing, the van is gated; after closing and a re-check it runs
    assert "open accident" in refused(f.env, lambda: f.assign(f.van, user=f.officer))
    res = ui.action(f.lm, **args, kwargs=why)
    assert res["success"], res
    acc.invalidate_recordset()
    assert acc.state == "closed" and acc.closed_by_id == f.lm
    assert acc.no_claim_reason == why["reason"] and not acc.claim_ref and not acc.settlement_amount
    assert "off-road" in refused(f.env, lambda: f.assign(f.van, user=f.officer))
    f.check(f.van, user=f.clerk2)
    off = f.open_offroad(f.van, "accident")
    assert ui.action(f.officer, model=off._name, ids=off.ids, method="action_return")["success"]
    assert f.assign(f.van, user=f.officer)
    # closed is closed
    assert not ui.action(f.lm, **args, kwargs=why)["success"]


def test_6_a_claim_or_a_settlement_goes_the_claim_route(f, ui):  # noqa: F811
    filed = accident(f, claim_ref="INS-1")
    filed.with_user(f.clerk).action_claim()
    res = ui.action(
        f.lm,
        model=filed._name,
        ids=filed.ids,
        method="action_close_no_claim",
        kwargs={"reason": "x"},
    )
    assert not res["success"]
    filed.invalidate_recordset()
    assert filed.state == "claimed"
    settled = accident(f, settlement_amount=1000, vehicle_id=f.vehicle("A7M46-SET").id)
    res = ui.action(
        f.lm,
        model=settled._name,
        ids=settled.ids,
        method="action_close_no_claim",
        kwargs={"reason": "x"},
    )
    assert "settlement" in res["error"].lower()


# =========================================================== 8: capitalise, dispose, retire
def test_8_vehicle_value_and_disposal_on_the_form_with_role_checks(f, ui, m46_js):  # noqa: F811
    form = offered(m46_js, "M46-form-vehicle")
    for name in ("net_car_value", "acquisition_date", "write_off_date"):
        assert not form[name].get("readonly"), name
        assert name in api.SURFACES["fleet.vehicle"]["writable"], name
    assert form["active"]["readonly"] and form["fix_retire_reason"]["readonly"]

    van = f.van
    # the Fleet Officer keeps the register, not the money or the disposal
    for values in ({"net_car_value": 2500000}, {"write_off_date": str(f.today)}):
        res = ui.write(f.officer, model=van._name, record_id=van.id, values=values)
        assert "Logistics Manager" in res["error"], values
    assert "error" not in ui.write(
        f.officer, model=van._name, record_id=van.id, values={"fix_tank_capacity_l": 70}
    )
    res = ui.write(f.lm, model=van._name, record_id=van.id, values={"net_car_value": 2500000})
    assert "error" not in res, res
    if "fix.asset.finance.request" in f.env:
        Req = f.env["fix.asset.finance.request"]
        cap = Req.search([("source_model", "=", van._name), ("source_res_id", "=", van.id)])
        assert len(cap) == 1 and cap.kind == "capitalise" and cap.source_amount == 2500000
    # an unchanged echo of the form is not a change
    van.invalidate_recordset()
    res = ui.write(
        f.officer,
        model=van._name,
        record_id=van.id,
        values={"net_car_value": 2500000, "write_off_date": ""},
    )
    assert "error" not in res, res
    # a new vehicle typed with a value by an officer is the same decision
    res = ui.write(
        f.officer,
        model=van._name,
        values={"model_id": f.van_model.id, "license_plate": "A7M46-V", "net_car_value": 9},
    )
    assert "Logistics Manager" in res["error"]


def test_8_retire_takes_a_reason_a_role_and_reaches_m49(f, ui, m46_js):  # noqa: F811
    assert buttons(m46_js, "M46-vehicles")["action_retire"]["kwarg"] == "reason"
    van = f.vehicle("A7M46-RETIRE")
    van.sudo().write({"net_car_value": 1800000})
    args = {"model": van._name, "ids": van.ids, "method": "action_retire"}
    assert not ui.action(f.officer, **args, kwargs={"reason": "Sold"})["success"]
    assert "reason" in ui.action(f.lm, **args)["error"].lower()
    # direct archiving is not a way round the reason
    res = ui.write(f.lm, model=van._name, record_id=van.id, values={"active": False})
    assert "error" in res
    assert refused(f.env, lambda: van.with_user(f.lm).write({"active": False}))

    tomorrow = f.today + timedelta(days=1)
    booking = f.assign(van, user=f.officer, date=tomorrow)
    res = ui.action(f.lm, **args, kwargs={"reason": "Sold at auction"})
    assert "booked" in res["error"]
    booking.with_user(f.officer).action_release(reason="Van is being sold")

    res = ui.action(f.lm, **args, kwargs={"reason": "Sold at auction"})
    assert res["success"], res
    van.invalidate_recordset()
    assert not van.active and van.fix_retire_reason == "Sold at auction"
    assert van.fix_retired_by_id == f.lm and van.fix_retired_on == f.today
    if "fix.asset.finance.request" in f.env:
        disp = f.env["fix.asset.finance.request"].search(
            [
                ("source_model", "=", van._name),
                ("source_res_id", "=", van.id),
                ("kind", "=", "dispose"),
            ]
        )
        assert len(disp) == 1
    # the gate refuses it by name, and the list still shows it
    blockers = van._fix_dispatch_blockers()[van.id]
    assert any("retired" in b for b in blockers)
    assert "retired" in refused(
        f.env, lambda: f.assign(van, user=f.officer, date=f.today, driver_id=f.driver.id)
    )
    cfg = m46_js["screens"]["M46-vehicles"]
    rows = ui.records(
        f.officer, model=van._name, cols=cfg["cols"], domain=cfg["domain"], search="A7M46-RETIRE"
    )["rows"]
    assert [r["id"] for r in rows] == van.ids and rows[0]["active"] is False


def test_8_a_cancelled_plate_stops_the_van(f):  # noqa: F811
    van = f.vehicle("A7M46-WOFF")
    van.with_user(f.lm).write({"write_off_date": f.today})
    assert "cancelled" in refused(f.env, lambda: f.assign(van, user=f.officer))


# =========================================================== 10, 11: fuel
def test_10_fuel_list_filters_on_review_state(f, ui, m46_js):  # noqa: F811
    cfg = m46_js["screens"]["M46-fuel"]
    assert cfg["stateField"] == "review_state"
    van = f.vehicle("A7M46-FF")
    ok = f.fill(van, 10000)
    held = f.fill(van, 999999)
    assert held.review_state == "held"
    out = ui.records(
        f.lm,
        model="fix.vehicle.fuel",
        cols=cfg["cols"],
        domain=[["vehicle_id", "=", van.id]],
        state_field=cfg["stateField"],
        state_filter="held",
    )
    assert [r["id"] for r in out["rows"]] == held.ids and ok.id not in {
        r["id"] for r in out["rows"]
    }


def test_11_a_hard_exception_says_what_to_do_and_can_be_held(f, ui, m46_js):  # noqa: F811
    form = offered(m46_js, "M46-form-fuel")
    assert not form["exception_reason"].get("readonly")
    van = f.vehicle("A7M46-HARD")
    f.fill(van, 10000)
    typed = {
        "vehicle_id": van.id,
        "driver_id": f.driver.id,
        "odometer": 9000,
        "litres": 35,
        "amount": 4000,
        "filled_on": str(f.today),
    }
    res = ui.write(f.clerk, model="fix.vehicle.fuel", values=typed)
    msg = res["error"]
    assert "odometer below" in msg
    assert "import" not in msg, "there is no fuel-card import to send anyone to"
    assert "Reason" in msg
    assert not f.env["fix.vehicle.fuel"].search_count(
        [("vehicle_id", "=", van.id), ("odometer", "=", 9000)]
    )
    # a blank reason is no reason
    res = ui.write(f.clerk, model="fix.vehicle.fuel", values={**typed, "exception_reason": "  "})
    assert "error" in res
    res = ui.write(
        f.clerk,
        model="fix.vehicle.fuel",
        values={**typed, "exception_reason": "Odometer replaced at last service"},
    )
    assert "error" not in res, res
    fill = f.env["fix.vehicle.fuel"].browse(res["id"])
    assert fill.review_state == "held" and "odometer_back" in fill.exception_flags
    assert f.events("vehicle.fuel_exception", fill)
    assert not f.events("vehicle.fuel_recorded", fill), "held: nothing reaches M52 yet"
    # it is out of the figures until a second person reviews it
    pack = m46_surface.fuel_efficiency(as_user(f, f.officer))
    row = next(r for r in pack["rows"] if r["vehicle"] == van.name)
    assert row["records"] == 1 and "provisional" in row["basis"]
    res = ui.action(
        f.clerk,
        model=fill._name,
        ids=fill.ids,
        method="action_clear_exception",
        kwargs={"note": "self"},
    )
    assert not res["success"]
    assert ui.action(
        f.lm,
        model=fill._name,
        ids=fill.ids,
        method="action_clear_exception",
        kwargs={"note": "Service invoice seen"},
    )["success"]
    assert f.events("vehicle.fuel_recorded", fill)


def test_11_a_reviewer_corrects_a_wrong_reading_so_later_fills_pass(f, ui, m46_js):  # noqa: F811
    asks = buttons(m46_js, "M46-fuel")["action_correct_odometer"]["asks"]
    assert {a["kwarg"] for a in asks} == {"odometer", "reason"}
    van = f.vehicle("A7M46-TYPO")
    f.fill(van, 10000)
    typo = f.fill(van, 15000)  # within a tank's range: accepted, and wrong
    assert typo.review_state == "none"
    # one typo blocks every honest fill after it
    assert "odometer below" in refused(f.env, lambda: f.fill(van, 10500, litres=30))
    args = {"model": typo._name, "ids": typo.ids, "method": "action_correct_odometer"}
    good = {"odometer": 10400, "reason": "Receipt reads 10,400"}
    # the Logistics Manager, not an officer, not the recorder
    assert not ui.action(f.officer, **args, kwargs=good)["success"]
    own = f.fill(f.vehicle("A7M46-OWNFILL"), 500, user=f.lm)
    res = ui.action(
        f.lm,
        model=own._name,
        ids=own.ids,
        method="action_correct_odometer",
        kwargs={"odometer": 400, "reason": "x"},
    )
    assert "Segregation of duties" in res["error"]
    assert "reason" in ui.action(f.lm, **args, kwargs={"odometer": 10400})["error"].lower()
    # the correction itself must fit between its neighbours
    res = ui.action(f.lm, **args, kwargs={"odometer": 9000, "reason": "x"})
    assert "previous" in res["error"]
    res = ui.action(f.lm, **args, kwargs=good)
    assert res["success"], res
    typo.invalidate_recordset()
    assert typo.odometer == 10400 and typo.review_state == "cleared"
    assert typo.reviewed_by_id == f.lm and "15000" in typo.review_note
    assert van._fix_last_odometer() == 10400
    # the fill after it now goes through
    assert f.fill(van, 10500, litres=30).review_state == "none"
    # corrected once: the reading is now reviewed, and locked
    assert not ui.action(f.lm, **args, kwargs={"odometer": 10450, "reason": "x"})["success"]


# =========================================================== 12: recall
def test_12_settlement_request_asks_and_can_be_recalled(f, ui, m46_js):  # noqa: F811
    btns = buttons(m46_js, "M46-accidents")
    assert btns["action_request_approval"]["kwarg"] == "justification"
    assert "action_recall_approval" in btns
    approver = (
        f.env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "a7m46_appr",
                "login": "a7m46_appr",
                "group_ids": [(6, 0, [f.env.ref("base.group_user").id, f.env.ref(TIER_2).id])],
            }
        )
    )
    company = insurer(f)
    acc = accident(f, claim_ref="INS-9", insurer_id=company.id, evidence_file=SCAN)
    acc.with_user(f.clerk).action_claim()
    acc.with_user(f.clerk).write({"settlement_amount": 40000})
    args = {"model": acc._name, "ids": acc.ids}
    res = ui.action(f.lm, **args, method="action_request_approval")
    assert "justification" in res["error"].lower()
    res = ui.action(
        f.lm,
        **args,
        method="action_request_approval",
        kwargs={"justification": "Assessor report"},
    )
    assert res["success"], res
    acc.invalidate_recordset()
    assert acc.approval_state == "pending"
    # only the requester withdraws it
    assert not ui.action(f.lm2, **args, method="action_recall_approval")["success"]
    assert ui.action(f.lm, **args, method="action_recall_approval")["success"]
    acc.invalidate_recordset()
    assert acc.approval_state == "none"
    # recalled, it can be asked again and decided
    approve_via_inbox(acc, approver, requester=f.lm, justification="Revised assessor report")
    assert acc.dofa_approved


# =========================================================== 13, 14: telemetry
def test_13_a_ping_typed_in_dhaka_time_does_not_read_online_for_hours(f, ui):  # noqa: F811
    env = as_user(f, f.officer)
    now_local = api._datetime_to_local(env, fields.Datetime.now())
    res = ui.write(
        f.officer,
        model="fix.vehicle.telemetry",
        values={"vehicle_id": f.van.id, "device_ref": "A7M46-T1", "last_ping": now_local},
    )
    assert "error" not in res, res
    fresh = f.env["fix.vehicle.telemetry"].browse(res["id"])
    gap = abs((fresh.last_ping - fields.Datetime.now()).total_seconds())
    assert gap < 120, "stored six hours ahead would be 21600s out, it was %s" % gap
    assert fresh.state == "online"
    # two hours ago on the wall clock is beyond the 60-minute silence, at once.
    # Stored without the zone it would sit 4h in the future and read online.
    two_hours = fields.Datetime.now() - timedelta(hours=2)
    res = ui.write(
        f.officer,
        model="fix.vehicle.telemetry",
        values={
            "vehicle_id": f.van.id,
            "device_ref": "A7M46-T2",
            "last_ping": api._datetime_to_local(env, two_hours),
        },
    )
    assert "error" not in res, res
    assert f.env["fix.vehicle.telemetry"].browse(res["id"]).state == "stale"
    # a ping from the future cannot be Online either
    res = ui.write(
        f.officer,
        model="fix.vehicle.telemetry",
        values={
            "vehicle_id": f.van.id,
            "device_ref": "A7M46-T3",
            "last_ping": api._datetime_to_local(env, fields.Datetime.now() + timedelta(hours=7)),
        },
    )
    assert "future" in res["error"]


def test_14_a_snapshot_typed_already_stale_raises_the_event_and_the_inspection(f, ui):  # noqa: F811
    old = fields.Datetime.now() - timedelta(days=2)
    env = as_user(f, f.officer)
    res = ui.write(
        f.officer,
        model="fix.vehicle.telemetry",
        values={
            "vehicle_id": f.van.id,
            "device_ref": "A7M46-SILENT",
            "last_ping": api._datetime_to_local(env, old),
        },
    )
    assert "error" not in res, res
    snap = f.env["fix.vehicle.telemetry"].browse(res["id"])
    assert snap.state == "stale" and len(f.events("vehicle.telematics_silent", snap)) == 1
    if "fix.maintenance.demand" in f.env:
        deliver(
            f,
            "vehicle.telematics_silent",
            snap,
            "cd_asset_workorder_spine.consumer_vehicle_telematics_silent",
        )
        demand = f.env["fix.maintenance.demand"].search(
            [("vehicle_id", "=", f.van.id), ("origin", "=", "m46_telematics")]
        )
        assert len(demand) == 1
    # an older snapshot typed in afterwards is history, not a new silence
    history = (
        f.env["fix.vehicle.telemetry"]
        .with_user(f.officer)
        .create(
            {
                "vehicle_id": f.van.id,
                "device_ref": "A7M46-SILENT",
                "last_ping": old - timedelta(days=5),
            }
        )
    )
    assert history.state == "stale" and not f.events("vehicle.telematics_silent", history)
    # a device that never reported is offline, and no event claims it went silent
    never = (
        f.env["fix.vehicle.telemetry"]
        .with_user(f.officer)
        .create({"vehicle_id": f.van.id, "device_ref": "A7M46-NEVER"})
    )
    assert never.state == "offline" and not f.events("vehicle.telematics_silent", never)


# =========================================================== 15-17: the figures
def test_15_docs_expiring_counts_only_current_valid_documents(f):  # noqa: F811
    env = as_user(f, f.officer)
    before = m46_surface.kpis(env)["docs_expiring_90d"]
    van = f.vehicle("A7M46-KPI1", days=400)
    soon = f.today + timedelta(days=30)
    old = f.doc(van, "route_permit", soon)
    f.env.invalidate_all()
    assert m46_surface.kpis(env)["docs_expiring_90d"] == before + 1
    # a renewal supersedes it: the old one no longer "expires"
    f.doc(van, "route_permit", f.today + timedelta(days=400))
    f.env.invalidate_all()
    assert m46_surface.kpis(env)["docs_expiring_90d"] == before
    assert not old.is_current
    # marked expired does not count either
    marked = f.doc(van, "other", soon)
    marked.with_user(f.officer).action_expire()
    f.env.invalidate_all()
    assert m46_surface.kpis(env)["docs_expiring_90d"] == before
    pack = m46_surface.statutory_compliance(env)
    row = next(r for r in pack["rows"] if r["plate"] == "A7M46-KPI1")
    assert row["expiring_90d"] == 0


def test_16_fuel_mtd_leaves_out_held_and_rejected_fills(f):  # noqa: F811
    env = as_user(f, f.officer)
    before = m46_surface.kpis(env)["fuel_mtd"]
    van = f.vehicle("A7M46-KPI2")
    f.fill(van, 10000, amount=1000)
    held = f.fill(van, 999999, amount=99999)
    rejected = f.fill(van, 899999, amount=88888)
    assert held.review_state == "held" and rejected.review_state == "held"
    rejected.with_user(f.lm).action_reject_fill(reason="Typo")
    assert m46_surface.kpis(env)["fuel_mtd"] == round(before + 1000, 2)
    held.with_user(f.lm).action_clear_exception(note="Long trip with logs")
    assert m46_surface.kpis(env)["fuel_mtd"] == round(before + 1000 + 99999, 2)


def test_17_open_jobs_are_not_maintenance_cost(f):  # noqa: F811
    env = as_user(f, f.officer)
    van = f.vehicle("A7M46-KPI3")
    PM = f.env["fix.vehicle.pm"].with_user(f.officer)
    PM.create({"vehicle_id": van.id, "cost": 7000, "odometer": 100})  # an estimate, still open
    done = PM.create({"vehicle_id": van.id, "cost": 500, "odometer": 100})
    done.action_done()
    f.fill(van, 1000, amount=100)
    f.fill(van, 1200, amount=100)
    row = next(r for r in m46_surface.maintenance_cost(env)["rows"] if r["vehicle"] == van.name)
    assert (row["jobs"], row["done"], row["cost"]) == (2, 1, 500)
    row = next(r for r in m46_surface.cost_per_km(env)["rows"] if r["plate"] == "A7M46-KPI3")
    assert row["pm_cost"] == 500
    assert row["cost_per_km"] == round((100 + 500) / 200, 2)


# =========================================================== 18: models
def test_18_a_new_model_can_be_made_on_screen(f, ui, m46_js):  # noqa: F811
    assert m46_js["chips"]["M46:__by_screen__"]["M46-models"] == "M46-form-model"
    assert m46_js["chips"]["M46:__by_screen__"]["M46-brands"] == "M46-form-brand"
    assert "error" in ui.write(
        f.clerk, model="fleet.vehicle.model.brand", values={"name": "A7M46 Clerk Brand"}
    )
    res = ui.write(f.officer, model="fleet.vehicle.model.brand", values={"name": "A7M46 Toyota"})
    assert "error" not in res, res
    brand = res["id"]
    model_vals = {"brand_id": brand, "name": "A7M46 Hiace", "vehicle_type": "car"}
    assert "error" in ui.write(f.clerk, model="fleet.vehicle.model", values=model_vals)
    res = ui.write(f.officer, model="fleet.vehicle.model", values=model_vals)
    assert "error" not in res, res
    res = ui.write(
        f.officer,
        model="fleet.vehicle",
        values={"model_id": res["id"], "license_plate": "A7M46-NEWMODEL"},
    )
    assert "error" not in res, res
    assert f.env["fleet.vehicle"].browse(res["id"]).model_id.name == "A7M46 Hiace"


# =========================================================== 19: the role's name
def test_19_the_role_has_a_name_of_its_own(f, ui):  # noqa: F811
    group = f.env.ref(LM)
    assert group.name == "Fleet Logistics Manager"
    assert group.with_context(lang="bn_BD").name != "Fleet Logistics Manager" or not f.env[
        "res.lang"
    ].search_count([("code", "=", "bn_BD")])
    fill = f.fill(f.van, 999999)
    res = ui.action(
        f.officer,
        model=fill._name,
        ids=fill.ids,
        method="action_clear_exception",
        kwargs={"note": "x"},
    )
    assert "Fleet Logistics Manager" in res["error"]


# =========================================================== 20, 21: what the form shows
def test_20_accident_form_shows_the_hse_case(f, ui, m46_js):  # noqa: F811
    form = offered(m46_js, "M46-form-accident")
    assert form["hse_case_ref"]["readonly"]
    assert "hse_case_ref" not in api.SURFACES["fix.vehicle.accident"]["writable"]
    acc = accident(f)
    acc.sudo().write({"hse_case_ref": "HSE/0042"})
    out = ui.form(f.clerk, model=acc._name, record_id=acc.id, fields=[{"name": "hse_case_ref"}])
    assert out["record"]["hse_case_ref"] == "HSE/0042"


@pytest.mark.parametrize(
    "screen,model,file_field,name_field",
    [
        ("M46-form-document", "fix.vehicle.document", "evidence_file", "evidence_filename"),
        ("M46-form-accident", "fix.vehicle.accident", "evidence_file", "evidence_filename"),
        ("M46-form-fuel", "fix.vehicle.fuel", "receipt_file", "receipt_filename"),
    ],
)
def test_21_evidence_keeps_its_own_file_name(f, ui, m46_js, screen, model, file_field, name_field):  # noqa: F811
    form = offered(m46_js, screen)
    assert form[file_field]["type"] == "file" and not form[name_field].get("readonly")
    assert name_field in api.SURFACES[model]["writable"]
    base = {
        "fix.vehicle.document": {
            "vehicle_id": f.van.id,
            "doc_type": "other",
            "valid_to": str(f.today + timedelta(days=9)),
        },
        "fix.vehicle.accident": {"vehicle_id": f.van.id, "description": "Scrape"},
        "fix.vehicle.fuel": {
            "vehicle_id": f.van.id,
            "driver_id": f.driver.id,
            "odometer": 100,
            "litres": 5,
            "amount": 500,
        },
    }[model]
    res = ui.write(
        f.officer, model=model, values={**base, file_field: PDF, name_field: "scan-77.pdf"}
    )
    assert "error" not in res, res
    assert f.env[model].browse(res["id"])[name_field] == "scan-77.pdf"


# =========================================================== 22, 23: the screens say the truth
def test_22_the_off_road_screen_is_named_for_what_it_lists(f, m46_js):  # noqa: F811
    screens = {s["id"]: s for g in m46_js["module"]["groups"] for s in g["screens"]}
    assert screens["M46-renewal"]["en"] == "Off-Road Records"
    assert m46_js["screens"]["M46-renewal"]["model"] == "fix.vehicle.offroad"


def test_23_new_is_offered_only_where_some_role_can_create(f, m46_js):  # noqa: F811
    roles = (f.clerk, f.officer, f.lm)
    for sid, cfg in m46_js["screens"].items():
        if cfg.get("kind") != "model_list":
            continue
        can = (
            any(f.env[cfg["model"]].with_user(u).has_access("create") for u in roles)
            and sid in m46_js["chips"]["M46:__by_screen__"]
        )
        if cfg.get("create") is False:
            continue
        assert can, "%s offers + New that nobody can use" % sid


def test_every_m46_column_and_form_field_exists(f, m46_js):  # noqa: F811
    """/p03/model/records drops an unknown column silently."""
    for sid, cfg in m46_js["screens"].items():
        if cfg.get("kind") == "model_list":
            missing = set(cfg["cols"]) - set(f.env[cfg["model"]]._fields)
            assert not missing, (sid, missing)
        if cfg.get("kind") == "model_form":
            missing = set(offered(m46_js, sid)) - set(f.env[cfg["model"]]._fields)
            assert not missing, (sid, missing)
            # a section naming an undeclared tab renders invisible; a long form has tabs
            tabs = {t["id"]: t for t in cfg.get("tabs", [])}
            assert tabs or len(offered(m46_js, sid)) <= 15, sid
            for tab_id, tab in tabs.items():
                count = sum(len(s["fields"]) for s in cfg["sections"] if s.get("tab") == tab_id)
                assert tab["badge"] == str(count), (sid, tab_id, count)
            if tabs:
                assert all(s.get("tab") in tabs for s in cfg["sections"]), sid


# =========================================================== logic bugs
def test_gate_needs_a_driver_when_the_switch_requires_one(f, ui):  # noqa: F811
    van = f.vehicle("A7M46-NODRV")
    assert not van.fix_driver_id
    f.env["ir.config_parameter"].sudo().set_param(REQUIRE_VEHICLE, "True")
    res = ui.write(
        f.officer,
        model="fix.vehicle.assignment",
        values={"vehicle_id": van.id, "date": str(f.today)},
    )
    assert "no driver" in res["error"]
    assert "no driver" in refused(
        f.env, lambda: van.with_user(f.officer).action_assert_dispatchable()
    )
    # a driver named, or the van's own, passes
    res = ui.write(
        f.officer,
        model="fix.vehicle.assignment",
        values={"vehicle_id": van.id, "date": str(f.today), "driver_id": f.driver.id},
    )
    assert "error" not in res, res
    other = f.vehicle("A7M46-OWNDRV", fix_driver_id=f.driver.id)
    assert f.assign(other, user=f.officer).driver_id == f.driver
    # with the switch off a van with nobody named still books (the deploy default)
    f.env["ir.config_parameter"].sudo().set_param(REQUIRE_VEHICLE, "False")
    third = f.vehicle("A7M46-OFFDRV")
    assert f.assign(third, user=f.officer)


def test_receipt_evidence_is_a_setting_default_off(f, ui):  # noqa: F811
    param = "cd_vehicle_ext.require_fuel_receipt"
    assert f.env["ir.config_parameter"].sudo().get_param(param) == "False"
    van = f.vehicle("A7M46-RCPT")
    typed = {
        "vehicle_id": van.id,
        "driver_id": f.driver.id,
        "odometer": 100,
        "litres": 5,
        "amount": 500,
    }
    assert "error" not in ui.write(f.clerk, model="fix.vehicle.fuel", values=typed)
    f.env["ir.config_parameter"].sudo().set_param(param, "True")
    res = ui.write(f.clerk, model="fix.vehicle.fuel", values={**typed, "odometer": 200})
    assert "receipt" in res["error"]
    res = ui.write(
        f.clerk,
        model="fix.vehicle.fuel",
        values={**typed, "odometer": 200, "receipt_file": PDF, "receipt_filename": "r.pdf"},
    )
    assert "error" not in res, res
    # and it cannot be taken off afterwards
    res2 = ui.write(
        f.clerk, model="fix.vehicle.fuel", record_id=res["id"], values={"receipt_file": False}
    )
    assert "receipt" in res2["error"]


def test_a_check_cannot_inflate_the_last_odometer(f, ui):  # noqa: F811
    van = f.vehicle("A7M46-CHK")
    f.fill(van, 10000)
    ok = {
        "vehicle_id": van.id,
        "tyres_ok": True,
        "lights_ok": True,
        "fluids_ok": True,
        "brakes_ok": True,
    }
    typo = ui.write(f.clerk, model="fix.vehicle.check", values={**ok, "odometer": 1000000})
    assert "beyond" in typo["error"] and "leave" in typo["error"].lower()
    assert van._fix_last_odometer() == 10000
    back = ui.write(f.clerk, model="fix.vehicle.check", values={**ok, "odometer": 9000})
    assert "below" in back["error"]
    # the check is never blocked: with no reading it still saves
    res = ui.write(f.clerk, model="fix.vehicle.check", values=ok)
    assert "error" not in res, res
    res = ui.write(f.clerk, model="fix.vehicle.check", values={**ok, "odometer": 10100})
    assert "error" not in res, res
    assert van._fix_last_odometer() == 10100
    # data loading stays trusted
    loaded = f.env["fix.vehicle.check"].create({**ok, "odometer": 5})
    assert loaded.odometer == 5


def test_only_the_recorder_corrects_a_fill_whatever_the_field(f, ui):  # noqa: F811
    van = f.vehicle("A7M46-LOCK")
    other_van = f.vehicle("A7M46-LOCK2")
    fuel = f.fill(van, 10000, station="Padma")
    other_driver = f.driver_f("A7M46 Lock Driver")
    for values in (
        {"vehicle_id": other_van.id},
        {"driver_id": other_driver.id},
        {"filled_on": str(f.today - timedelta(days=3))},
        {"station": "Meghna"},
    ):
        res = ui.write(f.clerk2, model=fuel._name, record_id=fuel.id, values=values)
        assert "error" in res, values
        assert refused(f.env, lambda v=values: fuel.with_user(f.clerk2).write(v)), values
    fuel.invalidate_recordset()
    assert fuel.vehicle_id == van and fuel.station == "Padma"
    # the recorder still can
    assert "error" not in ui.write(
        f.clerk, model=fuel._name, record_id=fuel.id, values={"station": "Meghna"}
    )


def test_a_corrected_amount_reaches_the_m52_cost_entry(f, ui):  # noqa: F811
    if "fix.asset.cost.entry" not in f.env:
        pytest.skip("cd_asset_finance_hse_bridge not installed")
    consumer = "cd_asset_finance_hse_bridge.consumer_vehicle_fuel_recorded"
    van = f.vehicle("A7M46-M52")
    fuel = f.fill(van, 10000, amount=4500)
    Entry = f.env["fix.asset.cost.entry"].sudo()

    def entry():
        return Entry.search([("source_model", "=", fuel._name), ("source_res_id", "=", fuel.id)])

    # corrected before the relay ran: the entry carries the corrected figure
    res = ui.write(f.clerk, model=fuel._name, record_id=fuel.id, values={"amount": 4600})
    assert "error" not in res, res
    deliver(f, "vehicle.fuel_recorded", fuel, consumer)
    assert entry().amount == 4600
    # corrected after it: a pending entry follows the fill
    res = ui.write(f.clerk, model=fuel._name, record_id=fuel.id, values={"amount": 4700})
    assert "error" not in res, res
    assert entry().amount == 4700
    # matched to a bill, AP has decided: the fill's figure no longer moves
    entry()._guarded().write({"state": "matched"})
    res = ui.write(f.clerk, model=fuel._name, record_id=fuel.id, values={"amount": 4800})
    assert "accounts payable" in res["error"].lower()
    fuel.invalidate_recordset()
    assert fuel.amount == 4700


def test_a_service_off_road_returns_only_when_the_service_is_done(f, ui):  # noqa: F811
    van = f.vehicle("A7M46-SVC")
    pm = (
        f.env["fix.vehicle.pm"]
        .with_user(f.officer)
        .create({"vehicle_id": van.id, "due_date": f.today - timedelta(days=9)})
    )
    off = van._fix_take_offroad("service", "Service overdue", pm_id=pm.id)
    f.check(van, user=f.clerk2)
    args = {"model": off._name, "ids": off.ids, "method": "action_return"}
    res = ui.action(f.officer, **args)
    assert pm.name in res["error"] and "service" in res["error"].lower()
    pm.with_user(f.officer).write({"odometer": 1000})
    pm.with_user(f.officer).action_done()
    # a check from before the service does not count? It still needs the re-check rule,
    # which the earlier check meets; now the job is done the van returns.
    res = ui.action(f.officer, **args)
    assert res["success"], res
    off.invalidate_recordset()
    assert off.state == "returned"


def test_role_constants_are_real_groups(f):  # noqa: F811
    assert f.env.ref(OFFICER) and f.env.ref(LM)
