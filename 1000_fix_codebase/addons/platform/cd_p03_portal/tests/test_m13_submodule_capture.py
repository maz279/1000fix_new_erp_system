# ruff: noqa: F811 - the controls suite's pytest fixtures (c, p03) are imported
# M13 Rental & EaaS: every Function Register sub-module page captures what
# its function records.
#
# Reported 2026-11-13: "not all the sub-modules have a relevant data capture
# button". Measured over the real registry with the engine's own page rule
# (p03_workspace.js fregCreate), before the fix:
#   4 Deposits & Waivers, 7 In-Rental Support  -> no button at all;
#   3 Agreements -> "+ New Reservation" again (the module button), and its
#     agreement chip made a second, empty booking;
#   8 Turnaround & PM -> "+ New Turnaround", which the server REFUSES (a
#     turnaround is opened by the return, never typed): a dead button;
#   6 Returns & Recovery -> page 5's damage form; nothing recorded the return;
#   5/6 condition and damage pickers listed every rental, most of which the
#     server refuses (wrong stage).
# Found on the way: every deposit was booked as CASH (action_reserve passed no
# tender), so a bKash deposit hit the cash account and was refunded as cash.
# fix_real held 0 rows in every M13 table and 0 rental SKUs.
#
# The page rule is JavaScript, so it is EXECUTED in node over the real
# registry; the steps run through the endpoints the forms use, as a non-admin
# user with no rental group (the rental desk holds base.group_user only).
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_rental_asset.tests.test_a05_m13_controls import (  # noqa: F401
    REFUSED,
    c,
    damage,
    ledger,
    p03,
    res,
    walk,
)
from odoo.exceptions import UserError

SRC = Path(__file__).resolve().parents[1] / "static" / "src"
IMPORT = re.compile(r'from\s+"(\./a\d\d/\w+)"')
FREG_CREATE = re.compile(r"^    (fregCreate\(mid, map\) \{\n.*?\n    \})\n", re.S | re.M)
RES = "fix.rental.reservation"

PROBE = """
import * as M from './meta.mjs';
const { P03_MODULES, P03_MODULE_CREATE, P03_FORM_CHIPS, P03_DATA_SCREENS } = M;
function %s
const subs = P03_MODULES.M13.freg.sub.map((s) => ({ no: s[0], title: s[1], map: s[3] || null,
  create: fregCreate('M13', s[3] || null) }));
const forms = {};
for (const [id, cfg] of Object.entries(P03_DATA_SCREENS)) {
  if (cfg.kind === 'model_form') forms[id] = cfg;
}
console.log(JSON.stringify({ subs, forms,
  chips: Object.fromEntries(Object.entries(P03_FORM_CHIPS).filter(([k]) => k.startsWith('M13:'))),
  moduleForms: P03_MODULES.M13.forms, screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS)
    .filter(([k]) => k.startsWith('M13-'))) }));
"""


@pytest.fixture(scope="module")
def reg(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m13_capture")
    for area in sorted(d for d in SRC.iterdir() if re.fullmatch(r"a\d\d", d.name)):
        (tmp / area.name).mkdir()
        for js in area.glob("*.js"):
            (tmp / area.name / (js.stem + ".mjs")).write_text(
                js.read_text(encoding="utf-8"), "utf-8"
            )
    meta = (SRC / "p03_modules_meta.js").read_text(encoding="utf-8")
    (tmp / "meta.mjs").write_text(IMPORT.sub(r'from "\1.mjs"', meta), "utf-8")
    method = FREG_CREATE.search(
        (SRC / "p03_workspace.js").read_text(encoding="utf-8").replace("\r\n", "\n")
    )
    assert method, "p03_workspace.js no longer defines fregCreate(mid, map)"
    probe = tmp / "probe.mjs"
    probe.write_text(PROBE % method.group(1), "utf-8")
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our own probe file
        [node, str(probe)], capture_output=True, encoding="utf-8", check=True, timeout=60
    )
    return json.loads(out.stdout)


def _sub(reg, no):
    return next(s for s in reg["subs"] if s["no"] == no)


# --- what each page offers -----------------------------------------------------

EXPECTED = {
    "1": "M13-form-asset",  # + New fleet unit (kit and the M37 rental SKU are chips)
    "2": {"module": True},  # + New Reservation
    "3": "M13-form-agreement",  # prepare the booking's agreement
    "4": "M13-form-deposit-take",  # take the deposit in its tender
    "5": "M13-form-condition",
    "6": "M13-form-return",
    "7": "M13-form-fault",
    "8": "M13-form-turnaround",  # the checklist of an OPEN turnaround
    "9": None,  # computed analytics: nothing to type
}


def test_the_scan_sees_nine_submodules(reg):
    assert [s["no"] for s in reg["subs"]] == [str(n) for n in range(1, 10)]


@pytest.mark.parametrize("no", sorted(EXPECTED, key=int))
def test_each_submodule_page_offers_its_capture(reg, no):
    sub = _sub(reg, no)
    want, got = EXPECTED[no], sub["create"]
    if want is None or isinstance(want, dict):
        assert got == want, "%s/%s offers %s" % (no, sub["title"], got)
    else:
        assert got and got.get("screen") == want, "%s/%s offers %s" % (no, sub["title"], got)
        assert got.get("label")


def test_every_capture_form_is_on_its_page_and_chip(reg):
    chips = reg["chips"]
    for sub in reg["subs"]:
        names = sub["map"]["forms"]
        for name in names:
            assert chips.get("M13:" + name) in reg["forms"], "%s: chip %s" % (sub["no"], name)
        screen = sub["create"] and sub["create"].get("screen")
        if screen:
            assert any(chips.get("M13:" + n) == screen for n in names), sub["title"]
    assert set(reg["moduleForms"]) == {k[4:] for k in chips if "__" not in k}


def test_no_page_offers_a_create_the_server_refuses(reg):
    """A turnaround and a deposit movement are made by the workflow: their
    lists offer no + New, and their forms only act on an existing record."""
    screens, forms = reg["screens"], reg["forms"]
    assert screens["M13-turnaround"].get("create") is False and screens["M13-turnaround"]["empty"]
    assert screens["M13-deposits"].get("create") is False
    assert forms["M13-form-turnaround"].get("pickRecord")
    assert forms["M13-form-deposit"].get("create") is False
    # the agreement form prepares an existing booking; it never makes one
    assert forms["M13-form-agreement"].get("pickRecord")


def test_every_form_field_and_filter_exists(reg, odoo_env):
    """No phantom field on any M13 form (a missing one is dropped silently),
    and every picker/step filter is one the server accepts."""
    m13 = {k: v for k, v in reg["forms"].items() if k.startswith("M13-")}
    for fid, cfg in m13.items():
        model = odoo_env[cfg["model"]]
        for sec in cfg["sections"]:
            for f in sec["fields"]:
                assert f["name"] in model._fields, "%s: %s" % (fid, f["name"])
                if f.get("domain"):
                    comodel = model._fields[f["name"]].comodel_name
                    assert api._choice_domain(odoo_env, comodel, f["domain"]) == f["domain"]
        pick = cfg.get("pickRecord")
        if pick:
            for col in pick["cols"]:
                assert col in model._fields, "%s pick col %s" % (fid, col)
            for leaf in pick["domain"]:
                assert leaf[0] in model._fields, "%s pick filter %s" % (fid, leaf)
            model.search(pick["domain"], limit=1)  # well-formed
        act = cfg.get("saveAction")
        if act:
            surface = api.SURFACES[cfg["model"]]
            assert act["method"] in surface["actions"], "%s: %s" % (fid, act["method"])
            for name in (act.get("kwargs") or {}).values():
                assert name in model._fields, "%s kwarg field %s" % (fid, name)


# --- each step, done the legitimate way through the endpoints -----------------


def _act(p03, model, rec, action, **kwargs):
    out = p03.action(model=model, ids=[rec.id], method=action, kwargs=kwargs)
    assert out.get("success"), out
    rec.invalidate_recordset()
    return out


def test_page4_deposit_is_taken_in_its_tender_and_refunded_the_same_way(c, p03):
    r = res(c)
    out = p03.action(model=RES, ids=[r.id], method="action_reserve", kwargs={"method": "bkash"})
    assert not out.get("success") and "reference" in out["error"]
    out = p03.action(model=RES, ids=[r.id], method="action_reserve", kwargs={"method": "gold"})
    assert not out.get("success") and "tender" in out["error"]
    r.invalidate_recordset()
    assert r.state == "draft" and not ledger(c, r)
    _act(p03, RES, r, "action_reserve", method="bkash", reference=" BK8XJ2Q1 ")
    collect = ledger(c, r)
    assert r.state == "reserved"
    assert (collect.kind, collect.method, collect.reference, collect.amount) == (
        "collect",
        "bkash",
        "BK8XJ2Q1",
        5000,
    )
    if collect.gl_state == "posted":
        r.with_user(c.clerk).action_cancel()
        refund = ledger(c, r).filtered(lambda d: d.kind == "refund")
        assert refund.method == "bkash", "a bKash deposit is refunded by bKash"


def test_page4_list_reserve_without_a_tender_is_still_cash(c, p03):
    r = res(c)
    _act(p03, RES, r, "action_reserve")
    assert ledger(c, r).method == "cash"


def test_page4_loss_waiver_is_requested_with_its_justification(c, p03):
    r = walk(c, res(c), "action_assess_damage")
    dmg = damage(c, r, cost=9000)  # above the 5,000 deposit
    assert dmg.unrecovered_loss_amount == 9000
    out = p03.action(
        model="fix.rental.damage",
        ids=[dmg.id],
        method="action_request_approval",
        kwargs={"justification": "Long-standing corporate customer; goodwill"},
    )
    dmg.invalidate_recordset()
    if out.get("success"):
        assert dmg.approval_state == "pending"
        assert dmg.dofa_justification == "Long-standing corporate customer; goodwill"
    else:  # no approver appointed in this database: refused with the reason
        assert "approve" in out["error"]


def test_page6_return_is_recorded_and_opens_the_turnaround(c, p03):
    r = walk(c, res(c), "action_activate")
    _act(p03, RES, r, "action_return")
    assert r.state == "returned" and r.actual_return_date
    turn = c.env["fix.rental.turnaround"].search([("reservation_id", "=", r.id)])
    assert turn.state == "pending" and c.asset.status == "maintenance"


def test_page7_fault_is_recorded_with_a_support_todo(c, p03):
    r = walk(c, res(c), "action_activate")
    out = p03.action(model=RES, ids=[r.id], method="action_report_fault", kwargs={"fault": " "})
    assert not out.get("success")
    before = len(r.message_ids)
    _act(p03, RES, r, "action_report_fault", fault="Projector lamp flickers, then dies")
    assert len(r.message_ids) == before + 1
    assert "Projector lamp flickers" in r.message_ids[0].body
    todo = r.activity_ids.filtered(lambda a: "In-rental fault" in (a.summary or ""))
    assert todo and todo.date_deadline >= c.today
    draft = res(c, rental_asset_id=False, device_id=c.device.id)
    with pytest.raises(UserError, match="out on rent"):
        draft.with_user(c.clerk).action_report_fault(fault="x")


def test_page7_return_collection_is_booked_in_m03(c, p03):
    r = walk(c, res(c), "action_activate")
    _act(p03, RES, r, "action_generate_return_consignment")
    assert r.return_consignment_id.consignment_type == "pickup"


def test_page8_turnaround_checklist_is_saved_from_the_form_then_released(c, p03):
    c.asset.write({"category": "tool"})  # not data-bearing: the checklist alone releases it
    r = walk(c, res(c), "action_return")
    t = c.env["fix.rental.turnaround"].search([("reservation_id", "=", r.id)])
    out = p03.write(
        model="fix.rental.turnaround",
        record_id=t.id,
        values={
            "cleaning_done": True,
            "sensor_cleaned": True,
            "connectors_inspected": True,
            "firmware_updated": True,
            "inspection_done": True,
            "functional_score_pct": 96,
            "battery_health_after_pm": 91,
            "regrade": "b",
            "technician_id": c.tech.id,
        },
    )
    assert not out.get("error"), out
    t.invalidate_recordset()
    assert t.sensor_cleaned and t.functional_score_pct == 96
    _act(p03, "fix.rental.turnaround", t, "action_ready")
    assert t.state == "ready" and c.asset.status == "available"
    # and a turnaround is still never typed
    with pytest.raises(REFUSED, match="not typed"):
        c.env["fix.rental.turnaround"].with_user(c.clerk).create({"rental_asset_id": c.asset.id})


def test_page8_preventive_maintenance_takes_the_unit_out_of_availability(c, p03):
    _act(p03, "fix.rental.asset", c.asset, "action_send_to_maintenance")
    assert c.asset.status == "maintenance"
    assert c.asset.turnaround_ids.filtered(lambda t: t.state == "pending")


def test_page5_condition_report_records_the_extra_checks(c, p03):
    r = res(c)
    out = p03.write(
        model="fix.rental.condition",
        record_id=None,
        values={
            "reservation_id": r.id,
            "report_type": "pre_delivery",
            "grade": "a",
            "reported_on": str(c.today),
            "body_condition_rating": "good",
            "charge_cycles": 212,
            "maintenance_required": True,
        },
    )
    assert not out.get("error"), out
    cond = c.env["fix.rental.condition"].search([("reservation_id", "=", r.id)])
    assert (cond.body_condition_rating, cond.charge_cycles, cond.maintenance_required) == (
        "good",
        212,
        True,
    )
