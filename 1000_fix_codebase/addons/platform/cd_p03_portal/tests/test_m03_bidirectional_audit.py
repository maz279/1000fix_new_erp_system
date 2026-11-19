# M03 bidirectional audit (13 Nov 2026): what the workspace shows on 8069
# against what the backend does, both ways.
#
# Found and fixed (each test below goes red on the old code):
# - every M03 screen, form, report and button resolves to a real field,
#   method and report (the static cross-check, kept as a guard);
# - a courier booking could never be delivered: its POD was a guarded field
#   with no served method and no upload anywhere;
# - an evidence field (waybill, POD, damage photo) offered a dropdown of every
#   attachment name in the company, read as superuser, and could not upload;
# - a damage claim could not be saved (operating unit required, on no form);
# - BRU-LOG-12 (declared value before dispatch) was not enforced;
# - the M01 hand-over had no button, and a second press made a second leg;
# - the Damage & Insurance Claims report ignored the claims; the Custody
#   Exception Register missed tamper holds and listed a lost, broken leg
#   twice; Reverse Logistics missed returns to vendor; Courier Performance
#   ignored the courier's SLA; the KPIs double-counted and called a count of
#   sheets "COD Today";
# - Return to Origin never set the RTO flag.
from __future__ import annotations

import base64
import inspect
import json
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from unittest import mock

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_p03_portal.controllers.a02 import m03 as ctl
from odoo.exceptions import UserError

SRC = Path(__file__).resolve().parents[1] / "static" / "src"
IMPORT = re.compile(r'from\s+"(\./a\d\d/\w+)"')
PROBE = """
import * as M from './meta.mjs';
const S = M.P03_DATA_SCREENS;
const screens = Object.fromEntries(Object.entries(S).filter(([k]) => k.startsWith('M03-')));
console.log(JSON.stringify({ module: M.P03_MODULES.M03, screens, cod: S['M50-form-cod'],
  chips: Object.fromEntries(Object.entries(M.P03_FORM_CHIPS).filter(([k]) => k.startsWith('M03:'))),
  routes: Object.fromEntries(Object.entries(M.P03_REPORT_ROUTES).filter(([k]) => k.startsWith('M03:'))),
  m01: S['M01-all'] }));
"""
PDF = base64.b64encode(b"%PDF-1.4 courier pod scan").decode()


@pytest.fixture(scope="module")
def reg(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m03_audit")
    for area in sorted(d for d in SRC.iterdir() if re.fullmatch(r"a\d\d", d.name)):
        (tmp / area.name).mkdir()
        for js in area.glob("*.js"):
            (tmp / area.name / (js.stem + ".mjs")).write_text(
                js.read_text(encoding="utf-8"), "utf-8"
            )
    meta = (SRC / "p03_modules_meta.js").read_text(encoding="utf-8")
    (tmp / "meta.mjs").write_text(IMPORT.sub(r'from "\1.mjs"', meta), "utf-8")
    probe = tmp / "probe.mjs"
    probe.write_text(PROBE, "utf-8")
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our own probe file
        [node, str(probe)], capture_output=True, encoding="utf-8", check=True, timeout=60
    )
    return json.loads(out.stdout)


# --- frontend -> backend: every M03 surface resolves --------------------------


def test_every_m03_screen_binds_real_fields_methods_and_reports(reg, odoo_env):
    bad = []
    for sid, cfg in reg["screens"].items():
        kind, model = cfg.get("kind"), cfg.get("model")
        if kind in ("model_list", "model_form"):
            if model not in api.SURFACES:
                bad.append("%s: %s not served" % (sid, model))
                continue
            fields = odoo_env[model]._fields
            served = api.SURFACES[model].get("actions", set())
            names = list(cfg.get("cols", []))
            names += [f["name"] for s in cfg.get("sections", []) for f in s["fields"]]
            pick = cfg.get("pickRecord") or {}
            names += pick.get("cols", []) + [
                c[0] for c in pick.get("domain", []) if isinstance(c, list)
            ]
            names += [c[0] for c in cfg.get("domain", []) if isinstance(c, list)]
            bad += ["%s: no field %s" % (sid, n) for n in names if n not in fields]
            # a `print` action is client-side (/p03/doc/print_url): no server method
            methods = [a["m"] for a in cfg.get("actions", []) if not a.get("print")]
            if cfg.get("saveAction"):
                methods.append(cfg["saveAction"]["method"])
            for m in methods:
                if m not in served or not hasattr(odoo_env[model], m):
                    bad.append("%s: %s not served or missing" % (sid, m))
            for a in cfg.get("actions", []):
                if a.get("kwarg"):
                    sig = inspect.signature(getattr(type(odoo_env[model]), a["m"]))
                    if a["kwarg"] not in sig.parameters:
                        bad.append("%s: %s takes no %s" % (sid, a["m"], a["kwarg"]))
            tabs = {t["id"] for t in cfg.get("tabs", [])}
            bad += [
                "%s: section on undeclared tab %s" % (sid, s.get("tab"))
                for s in cfg.get("sections", [])
                if tabs and s.get("tab") not in tabs
            ]
        elif kind == "table_report" and cfg.get("module") == "M03":
            if cfg["report"] not in ctl.REPORTS:
                bad.append("%s: report %s missing" % (sid, cfg["report"]))
    assert not bad, "\n".join(bad)


def test_every_m03_report_and_form_chip_lands(reg):
    for name in reg["module"]["reports"]:
        assert reg["routes"]["M03:" + name] in reg["screens"], name
    for name in reg["module"]["forms"]:
        target = reg["chips"]["M03:" + name]
        assert target in reg["screens"] or target == "M50-form-cod", name


def test_every_backend_report_has_a_screen(reg):
    used = {c["report"] for c in reg["screens"].values() if c.get("kind") == "table_report"}
    assert set(ctl.REPORTS) <= used


def test_every_served_m03_action_has_a_button(reg):
    """backend -> frontend: a whitelisted method nobody can press is dead."""
    pressed = {}
    for cfg in reg["screens"].values():
        model = cfg.get("model")
        for a in cfg.get("actions", []):
            pressed.setdefault(model, set()).add(a["m"])
        if cfg.get("saveAction"):
            pressed.setdefault(model, set()).add(cfg["saveAction"]["method"])
    for model in ("fix.consignment", "fix.courier.booking", "fix.damage.claim"):
        missing = api.SURFACES[model]["actions"] - pressed.get(model, set())
        assert not missing, (model, missing)


def test_the_m01_order_hands_over_to_logistics(reg):
    methods = [a["m"] for a in reg["m01"]["actions"]]
    assert "action_create_consignment" in methods
    assert "action_create_consignment" in api.SURFACES["fix.service.order"]["actions"]


def test_route_manifests_is_its_own_report(reg, odoo_env):
    assert reg["screens"]["M03-routes"]["report"] == "route_manifest"
    assert ctl.REPORTS["route_manifest"](odoo_env)["title"] == "Route Manifests"


# --- the saves and the rules ---------------------------------------------------


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
        {"code": "M3AUD", "legal_name": "M03 Audit Entity", "company_id": env.company.id}
    )
    a, b = env["fix.branch"].create(
        [
            {
                "name": "M03 Aud A",
                "code": "M3AA",
                "entity_id": entity.id,
                "operating_unit_id": ou.id,
            },
            {
                "name": "M03 Aud B",
                "code": "M3AB",
                "entity_id": entity.id,
                "operating_unit_id": ou.id,
            },
        ]
    )

    def leg(**kw):
        vals = {
            "consignment_type": "branch_transfer",
            "scheduled_date": datetime.now(),
            "origin_branch_id": a.id,
            "dest_branch_id": b.id,
            "outbound_seal_number": "SEAL-A1",
            "dispatch_weight_g": 900,
            "declared_value_bdt": 12000.0,
        }
        vals.update(kw)
        return env["fix.consignment"].create(vals)

    return env, ou, leg


def test_bru_log_12_a_leg_needs_a_declared_value_to_dispatch(lg):
    env, _ou, leg = lg
    rec = leg(declared_value_bdt=0)
    with pytest.raises(UserError, match="BRU-LOG-12"):
        rec.action_confirm()
    rec.declared_value_bdt = 5000
    rec.action_confirm()
    assert rec.state == "confirmed"


def test_a_damage_claim_saves_from_the_workspace_form(lg, call):
    env, ou, leg = lg
    rec = leg()
    res = call(
        env,
        "model_write",
        model="fix.damage.claim",
        record_id=False,
        values={
            "consignment_id": rec.id,
            "claimed_on": "2026-11-13",
            "claimant": "customer",
            "damage_kind": "physical",
            "liability": "pending",
            "description": "Screen cracked in transit",
            "claimed_amount": 3000,
        },
    )
    assert "error" not in res, res
    assert env["fix.damage.claim"].browse(res["id"]).operating_unit_id == ou


def test_the_m01_hand_over_makes_one_live_leg(lg):
    env, _ou, _leg = lg
    branch = env["fix.branch"].search([("code", "=", "M3AA")])
    brand = env["fix.brand"].create({"name": "M03AudBrand", "code": "M3AUD"})
    model = env["fix.device.model"].create({"name": "M03Aud Phone", "brand_id": brand.id})
    customer = env["res.partner"].create({"name": "M03 Aud Customer", "phone": "01711000404"})
    device = env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": customer.id, "serial_number": "SN-M3AUD-1"}
    )
    order = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "fault_description": "Collection pickup, M03 audit",
            "service_type": "collection",
        }
    )
    leg = order.action_create_consignment()
    assert leg.consignment_type == "pickup" and leg.service_order_id == order
    with pytest.raises(UserError, match="already has a live"):
        order.action_create_consignment()


def test_return_to_origin_sets_the_rto_flag(lg):
    env, _ou, leg = lg
    rec = leg()
    rec.action_confirm()
    rec.action_return(reason="Customer refused")
    assert rec.state == "returned" and rec.rto_flag
    assert "rto_flag" in rec._fix_guarded_fields()


# --- evidence uploads ----------------------------------------------------------


def test_an_evidence_field_is_an_upload_not_a_list_of_files(lg, call):
    env, _ou, _leg = lg
    form = call(
        env,
        "model_form",
        model="fix.consignment",
        fields=[{"name": "waybill_attachment_id"}],
        record_id=False,
    )
    entry = next(f for f in form["fields"] if f["name"] == "waybill_attachment_id")
    assert entry["type"] == "attachment"
    assert not entry.get("choices")
    found = call(
        env, "model_lookup", model="fix.consignment", field="waybill_attachment_id", term="a"
    )
    assert "error" in found
    plain = env(user=env.ref("base.user_admin").id, su=False)
    assert api._picker_source(plain, "ir.attachment").env.su is False
    assert api._picker_source(plain, "res.partner").env.su is True  # others unchanged


def test_a_waybill_upload_is_stored_on_its_consignment(lg, call):
    env, _ou, leg = lg
    rec = leg()
    res = call(
        env,
        "model_write",
        model="fix.consignment",
        record_id=rec.id,
        values={"waybill_attachment_id": {"upload": PDF, "filename": "waybill.pdf"}},
    )
    assert "error" not in res, res
    att = rec.waybill_attachment_id
    assert att.name == "waybill.pdf"
    assert (att.res_model, att.res_id) == ("fix.consignment", rec.id)


def test_a_courier_booking_closes_on_its_uploaded_pod(reg, lg, call):
    env, _ou, leg = lg
    rec = leg(consignment_type="delivery")
    partner = env["fix.courier.partner"].create({"name": "M03 Aud Courier", "code": "M3AC"})
    booking = env["fix.courier.booking"].create(
        {"partner_id": partner.id, "consignment_id": rec.id}
    )
    rec.action_confirm()
    form = reg["screens"]["M03-form-courier-pod"]
    kwarg, field = next(iter(form["saveAction"]["kwargs"].items()))
    assert field == "pod_attachment_id"
    no_pod = call(
        env, "model_action", model="fix.courier.booking", ids=[booking.id], method="action_deliver"
    )
    assert not no_pod["success"]
    res = call(
        env,
        "model_action",
        model="fix.courier.booking",
        ids=[booking.id],
        method=form["saveAction"]["method"],
        kwargs={kwarg: {"upload": PDF, "filename": "pod.pdf"}},
    )
    assert res["success"], res
    assert booking.pod_attachment_id.name == "pod.pdf"
    assert booking.pod_attachment_id.res_id == booking.id
    call(
        env, "model_action", model="fix.courier.booking", ids=[booking.id], method="action_pick_up"
    )
    done = call(
        env, "model_action", model="fix.courier.booking", ids=[booking.id], method="action_deliver"
    )
    assert done["success"], done
    assert booking.state == "delivered"


def test_an_oversized_upload_is_refused():
    with pytest.raises(UserError, match="10 MB"):
        api._store_upload(None, {"upload": "A" * (14 * 1024 * 1024), "filename": "big.pdf"})


# --- reports and KPIs ----------------------------------------------------------


def test_every_m03_report_runs_with_labelled_columns(odoo_env):
    for key, fn in ctl.REPORTS.items():
        res = fn(odoo_env)
        assert set(res["cols"]) <= set(res["labels"]), key


def test_the_custody_register_lists_a_tamper_hold_once(lg):
    env, _ou, leg = lg
    rec = leg()
    rec.action_confirm()
    rec.action_start_transit()
    rec.action_verify_hub_intake(inbound_seal="SEAL-ZZ", receive_weight_g=900)
    assert rec.state == "held"
    rows = [
        r for r in ctl.REPORTS["custody_exceptions"](env)["rows"] if r["consignment"] == rec.name
    ]
    assert len(rows) == 1 and "Tamper" in rows[0]["issue"]
    before = ctl.kpis(env)["custody_exceptions"]
    rec.action_report_lost(reason="Bag never arrived")
    assert ctl.kpis(env)["custody_exceptions"] == before  # same leg, counted once


def test_the_claims_report_lists_the_claims(lg):
    env, _ou, leg = lg
    rec = leg()
    claim = env["fix.damage.claim"].create(
        {
            "consignment_id": rec.id,
            "claimant": "branch",
            "damage_kind": "water",
            "liability": "pending",
            "description": "Wet carton",
            "claimed_amount": 800,
        }
    )
    rows = ctl.REPORTS["damage_claims"](env)["rows"]
    assert any(r["ref"] == claim.name and r["consignment"] == rec.name for r in rows)


def test_reverse_logistics_counts_returns_to_vendor(lg):
    env, _ou, leg = lg
    rtv = leg(consignment_type="return_to_vendor")
    rows = ctl.REPORTS["reverse_volume"](env)["rows"]
    assert any(r["consignment"] == rtv.name and r["flow"] == "Return to vendor" for r in rows)


def test_courier_on_time_uses_the_couriers_sla(odoo_env):
    env = odoo_env
    partner = env["fix.courier.partner"].create(
        {"name": "M03 Aud SLA", "code": "M3AS", "sla_delivery_hours": 24}
    )
    rows = [
        r for r in ctl.REPORTS["courier_performance"](env)["rows"] if r["courier"] == partner.name
    ]
    assert rows and rows[0]["sla"] == "24h"
