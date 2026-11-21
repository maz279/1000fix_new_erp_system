# M03 Service Logistics: every Function Register sub-module page captures
# what its function records.
#
# Reported 2026-11-12: "not all the sub-modules have a relevant data capture
# button". Measured: 2 of 12 M03 pages had one (courier booking, damage
# claim). The module had no "+ New" at all, its Consignments list refused
# one, and the consignment form could not have saved a new record anyway
# (operating unit required, never on the form) - fix_real held 0
# consignments with no way to make one. Seal, hub intake, POD and rider
# pages offered nothing although each is a step a person performs.
#
# The page rule is JavaScript (p03_workspace.js fregCreate), so it is
# EXECUTED in node over the real registry; the saves run through the same
# endpoints the forms use.
from __future__ import annotations

import json
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from unittest import mock

import pytest
from odoo.addons.cd_p03_portal.controllers import form_fields
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api

SRC = Path(__file__).resolve().parents[1] / "static" / "src"
IMPORT = re.compile(r'from\s+"(\./a\d\d/\w+)"')
FREG_CREATE = re.compile(r"^    (fregCreate\(mid, map\) \{\n.*?\n    \})\n", re.S | re.M)

PROBE = """
import * as M from './meta.mjs';
const { P03_MODULES, P03_MODULE_CREATE, P03_FORM_CHIPS, P03_DATA_SCREENS } = M;
function %s
const subs = P03_MODULES.M03.freg.sub.map((s) => ({ no: s[0], title: s[1], map: s[3] || null,
  create: fregCreate('M03', s[3] || null) }));
const forms = {};
for (const [id, cfg] of Object.entries(P03_DATA_SCREENS)) {
  if (cfg.kind === 'model_form' && (id.startsWith('M03-') || id === 'M50-form-cod')) forms[id] = cfg;
}
console.log(JSON.stringify({ subs, forms, create: P03_MODULE_CREATE.M03 || null,
  chips: Object.fromEntries(Object.entries(P03_FORM_CHIPS).filter(([k]) => k.startsWith('M03:'))),
  moduleForms: P03_MODULES.M03.forms, screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS)
    .filter(([k]) => k.startsWith('M03-'))) }));
"""


@pytest.fixture(scope="module")
def m03(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m03_capture")
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


def _sub(m03, no):
    return next(s for s in m03["subs"] if s["no"] == no)


# --- what each page offers -----------------------------------------------------

EXPECTED = {
    "1": {"module": True},  # + New Consignment
    "2": "M03-form-next-leg",  # the next leg of an order's journey (2026-11-18)
    "3": "M03-form-hub-intake",
    "4": "M03-form-pod",
    "5": "M03-form-seal",
    "6": "M03-form-rider",
    "7": "M03-form-rider",
    "8": None,  # written by the rider app on sync
    "9": "M03-form-booking",
    "10": "M50-form-cod",
    "11": "M03-form-damage-claim",
    "12": "M03-form-courier",
}


def test_the_scan_sees_twelve_submodules(m03):
    assert [s["no"] for s in m03["subs"]] == [str(n) for n in range(1, 13)]


@pytest.mark.parametrize("no", sorted(EXPECTED, key=int))
def test_each_submodule_page_offers_its_capture(m03, no):
    sub = _sub(m03, no)
    want = EXPECTED[no]
    got = sub["create"]
    if want is None:
        assert got is None, "%s/%s offers %s" % (no, sub["title"], got)
    elif isinstance(want, dict):
        assert got == want, "%s/%s offers %s" % (no, sub["title"], got)
    else:
        assert got and got.get("screen") == want, "%s/%s offers %s" % (no, sub["title"], got)
        assert got.get("label")


def test_the_module_button_raises_a_consignment(m03):
    assert m03["create"] == {
        "screen": "M03-form-consignment",
        "model": "fix.consignment",
        "label": "Consignment",
    }
    assert m03["screens"]["M03-cons"].get("create") is not False


def test_every_capture_form_is_on_its_page_and_chip(m03):
    """'Forms Capturing It' lists the form the button opens, and the chip
    opens that same form."""
    for sub in m03["subs"]:
        screen = sub["create"] and sub["create"].get("screen")
        if not screen:
            continue
        names = [n for n in sub["map"]["forms"] if m03["chips"].get("M03:" + n) == screen]
        assert names, "%s/%s: no chip opens %s" % (sub["no"], sub["title"], screen)
    assert set(m03["moduleForms"]) == {k[4:] for k in m03["chips"] if "__" not in k}


def test_the_capture_forms_bind_real_fields(m03, odoo_env):
    """A form field or a pick column the model lacks is dropped silently by
    /p03/model/form and /p03/model/records - it would just not appear."""
    bad = []
    for sid, cfg in m03["forms"].items():
        fields = odoo_env[cfg["model"]]._fields
        names = [f["name"] for s in cfg["sections"] for f in s["fields"]]
        pick = cfg.get("pickRecord") or {}
        names += pick.get("cols", []) + [
            c[0] for c in pick.get("domain", []) if isinstance(c, list)
        ]
        bad += ["%s.%s" % (sid, n) for n in names if n not in fields]
    assert not bad, bad


def test_the_workflow_captures_call_whitelisted_methods(m03):
    for sid, cfg in m03["forms"].items():
        act = cfg.get("saveAction")
        if act:
            assert act["method"] in api.SURFACES[cfg["model"]]["actions"], sid


def test_the_hub_intake_is_blind(m03):
    """The hub reads its own seal and weight: showing the dispatch values
    would let it copy them."""
    cfg = m03["forms"]["M03-form-hub-intake"]
    shown = {f["name"] for s in cfg["sections"] for f in s["fields"]}
    assert not shown & {"outbound_seal_number", "dispatch_weight_g", "weight_variance_g"}
    assert cfg["pickRecord"]["domain"] == [["state", "=", "in_transit"]]


def test_the_whitelist_takes_every_consignment_form_field():
    """controllers/a02/writable.py is generated from the forms: a field a form
    offers but the whitelist lacks is DROPPED on create (the operating unit
    then fails NOT NULL)."""
    offered = set()
    for _area, _sid, model, editable in form_fields.forms():
        if model == "fix.consignment":
            offered |= set(editable)
    assert offered <= set(api.SURFACES["fix.consignment"]["writable"])
    assert {"operating_unit_id", "declared_value_bdt", "purchase_order_id"} <= offered


# --- the saves, through the endpoints the forms use ----------------------------


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


@pytest.fixture
def lg(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].create(
        {"code": "M3CAP", "legal_name": "M03 Capture Entity", "company_id": env.company.id}
    )
    branches = env["fix.branch"].create(
        [
            {
                "name": "M03 Cap A",
                "code": "M3CA",
                "entity_id": entity.id,
                "operating_unit_id": ou.id,
            },
            {
                "name": "M03 Cap B",
                "code": "M3CB",
                "entity_id": entity.id,
                "operating_unit_id": ou.id,
            },
        ]
    )
    return env, ou, branches


def test_a_branch_transfer_saves_from_the_workspace_form(lg, call):
    """Exactly what the form posts when the user leaves the operating unit
    blank: it was a NOT NULL failure; the unit now follows the branch."""
    env, ou, (a, b) = lg
    res = call(
        env,
        "model_write",
        model="fix.consignment",
        record_id=False,
        values={
            "consignment_type": "branch_transfer",
            "scheduled_date": "2026-11-13 10:00",
            "origin_branch_id": a.id,
            "dest_branch_id": b.id,
            "declared_value_bdt": 25000,
            "packaging_type": "bubble_carton",
            "vehicle_registration": "DHAKA-METRO-LA-11-2233",
        },
    )
    assert "error" not in res, res
    rec = env["fix.consignment"].browse(res["id"])
    assert rec.operating_unit_id == ou
    assert rec.state == "draft" and rec.name
    assert rec.declared_value_bdt == 25000 and rec.insurance_fee_bdt == 250.0
    assert rec.vehicle_registration == "DHAKA-METRO-LA-11-2233"


def test_the_users_unit_is_the_last_resort(lg):
    env, ou, _branches = lg
    env.user.default_operating_unit_id = ou
    rec = env["fix.consignment"].create(
        {"consignment_type": "return_to_vendor", "scheduled_date": datetime.now()}
    )
    assert rec.operating_unit_id == ou


def _in_transit(env, branches, **vals):
    a, b = branches
    rec = env["fix.consignment"].create(
        {
            "consignment_type": "branch_transfer",
            "scheduled_date": datetime.now(),
            "origin_branch_id": a.id,
            "dest_branch_id": b.id,
            "outbound_seal_number": "SEAL-001",
            "dispatch_weight_g": 1200,
            "declared_value_bdt": 15000.0,
            **vals,
        }
    )
    rec.action_confirm()
    rec.action_start_transit()
    assert rec.state == "in_transit"
    return rec


def _hub_intake_kwargs(m03, values):
    """The kwargs formSaveAction builds: server argument <- form field."""
    act = m03["forms"]["M03-form-hub-intake"]["saveAction"]
    return {k: values[f] for k, f in act["kwargs"].items() if values.get(f) not in (None, "")}


def test_the_hub_intake_form_completes_a_matching_intake(m03, lg, call):
    env, _ou, branches = lg
    rec = _in_transit(env, branches)
    act = m03["forms"]["M03-form-hub-intake"]["saveAction"]
    res = call(
        env,
        "model_action",
        model="fix.consignment",
        ids=[rec.id],
        method=act["method"],
        kwargs=_hub_intake_kwargs(
            m03, {"inbound_seal_number": "SEAL-001", "receive_weight_g": 1210}
        ),
    )
    assert res["success"], res
    assert not res["result"].get("warning")
    assert rec.seal_status == "verified"
    assert "hub_scan" in rec.custody_ids.mapped("step")


def test_the_hub_intake_form_reports_a_seal_mismatch(m03, lg, call):
    """The method succeeds with a warning and holds the leg; the engine now
    shows the warning instead of a '✓' (it was dropped)."""
    env, _ou, branches = lg
    rec = _in_transit(env, branches)
    res = call(
        env,
        "model_action",
        model="fix.consignment",
        ids=[rec.id],
        method="action_verify_hub_intake",
        kwargs=_hub_intake_kwargs(
            m03, {"inbound_seal_number": "SEAL-999", "receive_weight_g": 1200}
        ),
    )
    assert res["success"], res
    assert "Tamper Alert" in res["result"]["warning"]
    assert rec.state == "held" and rec.seal_status == "tampered_mismatch"
    engine = (SRC / "p03_workspace.js").read_text(encoding="utf-8")
    assert "res.result && res.result.warning" in engine
    assert "else if (r.warning)" in engine


def test_the_seal_form_cannot_rewrite_a_leg_in_transit(lg, call):
    env, _ou, branches = lg
    rec = _in_transit(env, branches)
    res = call(
        env,
        "model_write",
        model="fix.consignment",
        record_id=rec.id,
        values={"outbound_seal_number": "SEAL-REPLACED"},
    )
    assert "error" in res
    assert rec.outbound_seal_number == "SEAL-001"


# --- M03 capture audit 2026-11-18: page 2 plans the next leg of a journey ------


def test_page_two_plans_the_next_leg_not_a_blank_consignment(m03):
    """It offered the same blank consignment as page 1."""
    cfg = m03["forms"]["M03-form-next-leg"]
    assert cfg["model"] == "fix.service.order"
    assert cfg["saveAction"]["method"] == "action_create_consignment"
    assert not [f for s in cfg["sections"] for f in s["fields"] if not f.get("readonly")]
    assert m03["chips"]["M03:Next Journey Leg"] == "M03-form-next-leg"
    assert "Next Journey Leg" in _sub(m03, "2")["map"]["forms"]


def test_the_journeys_screen_lists_legs_not_custody_scans(m03):
    """'Multi-Leg Journeys' listed custody scans: page 3's records."""
    cfg = m03["screens"]["M03-journeys"]
    assert cfg["model"] == "fix.consignment"
    assert cfg["cols"][0] == "service_order_id"
    assert _sub(m03, "2")["map"]["screens"][0] == "M03-journeys"


def test_no_form_claims_five_consignment_types(m03, odoo_env):
    kinds = odoo_env["fix.consignment"]._fields["consignment_type"].selection
    assert len(kinds) == 4
    assert m03["forms"]["M03-form-consignment"]["title"] == "Consignment"
    assert not [n for n in m03["moduleForms"] if "5 types" in n]


@pytest.fixture
def journey(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].create(
        {"code": "M3NL", "legal_name": "M03 Next Leg Entity", "company_id": env.company.id}
    )
    branch = env["fix.branch"].create(
        {
            "name": "M03 NL Branch",
            "code": "M3NL",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    brand = env["fix.brand"].create({"name": "M3NLBrand", "code": "M3N"})
    model = env["fix.device.model"].create({"name": "M3NL Phone", "brand_id": brand.id})
    customer = env["res.partner"].create({"name": "M03 NL Customer", "phone": "01711000404"})
    device = env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": customer.id, "serial_number": "SN-M3NL-1"}
    )
    order = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "fault_description": "M03 next-leg journey",
            "service_type": "collection",
        }
    )
    return env, order


def _raise_next_leg(m03, env, order, call):
    act = m03["forms"]["M03-form-next-leg"]["saveAction"]
    res = call(
        env,
        "model_action",
        model="fix.service.order",
        ids=[order.id],
        method=act["method"],
        kwargs=act["kwargs"],
    )
    return res


# a 1x1 PNG, base64 (pickup evidence must be an image)
_PNG_B64 = b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="


def _door_proof(env, leg):
    """A02 pass 2 M03-04: what a service order's pickup records at the
    customer's door before it leaves - the customer's signature, a package
    photo, the device serial, and the outbound seal and weight (as the
    cd_consignment fixture's door_proof does, with a signature for the code)."""
    for kind in ("signature", "photo"):
        image = env["ir.attachment"].create(
            {
                "name": "%s.png" % kind,
                "datas": _PNG_B64,
                "mimetype": "image/png",
                "res_model": leg._name,
                "res_id": leg.id,
            }
        )
        leg.action_attach_pickup_evidence(attachment_id=image.id, kind=kind)
    serial = leg.service_order_id.device_serial
    if serial:
        leg.action_scan_pickup_serial(serial=serial)
    door = {}
    if not leg.outbound_seal_number:
        door["outbound_seal_number"] = "SEAL-DOOR-%s" % leg.id
    if not leg.dispatch_weight_g:
        door["dispatch_weight_g"] = 500.0
    if door:
        leg.write(door)
    assert not leg._m03_pickup_proof_missing()


def test_the_next_leg_form_runs_the_whole_collection_journey(m03, journey, call):
    """Pickup, then (after the device arrives and the repair is ready) the
    delivery back - through the same endpoint the form's save uses."""
    env, order = journey
    pick = m03["forms"]["M03-form-next-leg"]["pickRecord"]["domain"]
    assert order not in env["fix.service.order"].search(pick)  # a draft is not booked in
    order.state = "intake"
    assert order in env["fix.service.order"].search(pick)
    res = _raise_next_leg(m03, env, order, call)
    assert res["success"], res
    pickup = order.consignment_ids
    assert pickup.consignment_type == "pickup"
    pickup.declared_value_bdt = 5000
    pickup.action_confirm()
    _door_proof(env, pickup)  # A02 pass 2 (M03-04): proof at the customer's door
    pickup.action_start_transit()
    # the door fitted a seal and weighed the parcel: the hub checks both
    pickup.action_verify_hub_intake(
        inbound_seal=pickup.outbound_seal_number, receive_weight_g=pickup.dispatch_weight_g
    )
    pickup.action_confirm_receipt()
    order.state = "diagnostic"
    res = _raise_next_leg(m03, env, order, call)
    assert not res.get("success") and "already arrived" in str(res), res
    for state in (
        "estimate_pending",
        "estimate_sent",
        "awaiting_approval",
        "approved",
        "in_repair",
        "qc_pending",
    ):
        order.state = state
    # A02 pass 2 (M01-09): Ready reads the checklist of the current QC round
    env["fix.qc.checklist"].create(
        {"order_id": order.id, "state": "passed", "qc_round": order.qc_round}
    )
    order.state = "ready"
    assert order in env["fix.service.order"].search(pick)
    res = _raise_next_leg(m03, env, order, call)
    assert res["success"], res
    back = order.consignment_ids - pickup
    assert back.consignment_type == "delivery" and back.state == "draft"
