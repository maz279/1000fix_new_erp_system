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
    "2": {"module": True},  # the next leg of a journey is a consignment
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
        names += pick.get("cols", []) + [c[0] for c in pick.get("domain", [])]
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
