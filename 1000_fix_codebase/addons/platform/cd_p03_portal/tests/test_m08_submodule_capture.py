# M08 Contract Lifecycle (AMC): every Function Register sub-module page
# captures what its function records.
#
# Reported 2026-11-13: "not all the sub-modules have a relevant data capture
# button". Measured over the real registry and the page rule: pages 2 (Parties
# & Approval), 5 (SLA & Service Credits), 10 (Pricing & Profitability) and 11
# (Documents & Signature) offered nothing; pages 3 (Coverage Scope) and 4
# (Entitlement Engine) offered the same form, titled "Asset Attach / Detach",
# which captured an ENTITLEMENT; page 9 (Churn & Win-Back) offered a form no
# chip named. No form anywhere set a contract's covered assets or its SLAs,
# while activation generates preventive visits only for covered assets and an
# AMC order is accepted only for a covered device. Two reports (SLA Credit
# Register, Contract P&L) read a field the SLA credit does not have and raised
# on the first credit. fix_real held 0 records in every M08 table.
#
# The page rule is JavaScript (p03_workspace.js fregCreate), so it is
# EXECUTED in node over the real registry; the saves run through the same
# endpoints the forms use, as non-admin users holding only the M08 roles.
from __future__ import annotations

import json
import re
import shutil
import subprocess
from datetime import timedelta
from pathlib import Path
from unittest import mock

import pytest
from odoo.addons.cd_contract_core.tests.test_a04_c2_c13_contracts import (  # noqa: F401
    _active,
    _contract,
    _device,
    c,
    p03,
)
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_p03_portal.controllers.a04 import m08 as m08_reports
from odoo.addons.cd_p03_portal.controllers.a04.writable import WRITABLE

SRC = Path(__file__).resolve().parents[1] / "static" / "src"
IMPORT = re.compile(r'from\s+"(\./a\d\d/\w+)"')
FREG_CREATE = re.compile(r"^    (fregCreate\(mid, map\) \{\n.*?\n    \})\n", re.S | re.M)

PROBE = """
import * as M from './meta.mjs';
const { P03_MODULES, P03_MODULE_CREATE, P03_FORM_CHIPS, P03_DATA_SCREENS } = M;
function %s
const subs = P03_MODULES.M08.freg.sub.map((s) => ({ no: s[0], title: s[1], map: s[3] || null,
  create: fregCreate('M08', s[3] || null) }));
const chips = Object.fromEntries(Object.entries(P03_FORM_CHIPS).filter(([k]) => k.startsWith('M08:')));
const forms = {};
for (const [id, cfg] of Object.entries(P03_DATA_SCREENS)) {
  if (cfg.kind === 'model_form' && (id.startsWith('M08-') || Object.values(chips).includes(id))) forms[id] = cfg;
}
console.log(JSON.stringify({ subs, forms, create: P03_MODULE_CREATE.M08 || null, chips,
  moduleForms: P03_MODULES.M08.forms, screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS)
    .filter(([k]) => k.startsWith('M08-'))) }));
"""


@pytest.fixture(scope="module")
def reg(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m08_capture")
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


def _fields(cfg):
    return [f for s in cfg["sections"] for f in s["fields"]]


# --- what each page offers -----------------------------------------------------

EXPECTED = {
    "1": {"module": True},  # + New Contract
    "2": "M08-form-submit",  # Legal review is the second chip
    "3": "M08-form-coverage",  # the covered assets and SLAs, not an entitlement
    "4": "M08-form-entitlement",
    "5": "M05-form-credit",  # M05 masters the SLA credit
    "6": "M08-form-pm",
    "7": "M08-form-amendment",
    "8": "M08-form-renewal",
    "9": "M08-form-termination",
    "10": "M08-form-price",
    "11": "M08-form-signature",
    "12": "M08-form-pm",
}


def test_the_scan_sees_twelve_submodules(reg):
    assert [s["no"] for s in reg["subs"]] == [str(n) for n in range(1, 13)]


@pytest.mark.parametrize("no", sorted(EXPECTED, key=int))
def test_each_submodule_page_offers_its_capture(reg, no):
    sub = _sub(reg, no)
    want, got = EXPECTED[no], sub["create"]
    if isinstance(want, dict):
        assert got == want, "%s/%s offers %s" % (no, sub["title"], got)
    else:
        assert got and got.get("screen") == want, "%s/%s offers %s" % (no, sub["title"], got)
        assert got.get("label")


def test_coverage_and_entitlement_pages_no_longer_share_a_button(reg):
    assert _sub(reg, "3")["create"]["screen"] != _sub(reg, "4")["create"]["screen"]


def test_every_capture_form_is_on_its_page_and_chip(reg):
    """'Forms Capturing It' lists the form the button opens, and every chip
    on a page opens a declared form."""
    chips = reg["chips"]
    for sub in reg["subs"]:
        names = sub["map"]["forms"]
        for name in names:
            assert chips.get("M08:" + name) in reg["forms"], "%s: chip %s" % (sub["no"], name)
        screen = sub["create"] and sub["create"].get("screen")
        if screen:
            assert any(chips.get("M08:" + n) == screen for n in names), sub["title"]
    assert set(reg["moduleForms"]) == {k[4:] for k in chips if "__" not in k}


def test_the_registry_attach_detach_form_sets_the_contract_cover(reg):
    """'Asset Attach/Detach' opened the entitlement form: no form set the
    covered assets, so an activated contract generated no PM visit."""
    cover = reg["forms"][reg["chips"]["M08:Asset Attach/Detach"]]
    assert cover["model"] == "fix.contract"
    editable = {f["name"] for f in _fields(cover) if not f.get("readonly")}
    assert {"covered_device_ids", "sla_policy_ids"} <= editable
    record = {f["name"] for f in _fields(reg["forms"]["M08-record"])}
    assert {"covered_device_ids", "sla_policy_ids"} <= record
    assert {"covered_device_ids", "sla_policy_ids"} <= WRITABLE["fix.contract"]
    assert reg["forms"][reg["chips"]["M08:Entitlement"]]["model"] == "fix.contract.entitlement"


def test_the_price_revision_opens_as_a_pricing_amendment(reg):
    cfg = reg["forms"]["M08-form-price"]
    assert cfg["model"] == "fix.contract.amendment"
    assert cfg["presets"] == {"kind": "pricing"}
    kind = next(f for f in _fields(cfg) if f["name"] == "kind")
    assert not kind.get(
        "readonly"
    ), "a readonly field is dropped on create: the preset would be lost"


def test_the_capture_forms_bind_real_fields(reg, odoo_env):
    """A form field, a pick column or a filter field the model lacks is
    dropped silently by /p03/model/form and /p03/model/records."""
    bad = []
    for sid, cfg in reg["forms"].items():
        model = odoo_env[cfg["model"]]
        names = [f["name"] for f in _fields(cfg)]
        pick = cfg.get("pickRecord") or {}
        names += pick.get("cols", []) + [leaf[0] for leaf in pick.get("domain", [])]
        names += list(cfg.get("presets") or {})
        bad += ["%s.%s" % (sid, n) for n in names if n not in model._fields]
        for f in _fields(cfg):
            if f.get("domain") and f["name"] in model._fields:
                comodel = odoo_env[model._fields[f["name"]].comodel_name]
                bad += [
                    "%s.%s -> %s" % (sid, f["name"], leaf[0])
                    for leaf in f["domain"]
                    if leaf[0] not in comodel._fields
                ]
    assert not bad, bad


def test_the_workflow_captures_call_whitelisted_methods_with_their_fields(reg):
    for sid, cfg in reg["forms"].items():
        act = cfg.get("saveAction")
        if not act:
            continue
        assert act["method"] in api.SURFACES[cfg["model"]]["actions"], sid
        shown = {f["name"] for f in _fields(cfg)}
        assert set(act["kwargs"].values()) <= shown, sid
        assert cfg.get("pickRecord"), "%s acts on an existing record: it picks one" % sid


def test_the_pickers_and_pick_lists_are_served(reg, odoo_env):
    """Each form loads with its declared picker filters, and each pick list
    loads through the reader the lists use."""
    ctrl = api.P03GenericApiController()
    with mock.patch.object(api, "request", mock.Mock(env=odoo_env)):
        for sid, cfg in reg["forms"].items():
            out = ctrl.model_form(model=cfg["model"], fields=_fields(cfg))
            assert "error" not in out, (sid, out)
            pick = cfg.get("pickRecord")
            if pick:
                rows = ctrl.model_records(
                    model=cfg["model"], cols=pick["cols"], domain=pick["domain"]
                )
                assert "error" not in rows, (sid, rows)


# --- the saves, through the endpoints the forms use, as a Contract Officer ------


def test_a_draft_contract_takes_its_cover_and_activation_schedules_its_visits(c, p03):  # noqa: F811 - the imported fixture
    k = _contract(c)
    dev = _device(c)
    out = p03(c.officer).write(
        model="fix.contract", record_id=k.id, values={"covered_device_ids": [dev.id]}
    )
    assert "error" not in out, out
    k.invalidate_recordset()
    assert k.covered_device_ids == dev
    k.sudo().write({"has_signed_contract_doc": True})
    k.sudo().action_activate()
    visits = c.env["fix.contract.pm.visit"].search([("contract_id", "=", k.id)])
    assert visits and set(visits.mapped("device_id").ids) == {dev.id}


def test_the_cover_of_a_contract_in_force_is_fixed(c, p03):  # noqa: F811 - the imported fixture
    """Once submitted, the cover is a frozen term: the form shows it read-only
    and a write leaves it as it was.

    KNOWN ENGINE GAP (reported 2026-11-13, not fixed here): for a locked
    many2many, /p03/model/write drops the change and still answers success
    (_readonly_changed returns False for every many2many), so a crafted call
    is told "saved". The form cannot send it - the field is read-only."""
    k = _active(c, devices=_device(c))
    ctrl = api.P03GenericApiController()
    with mock.patch.object(api, "request", mock.Mock(env=c.env(user=c.officer.id))):
        form = ctrl.model_form(
            model="fix.contract",
            record_id=k.id,
            fields=[{"name": "covered_device_ids"}, {"name": "sla_policy_ids"}],
        )
    shown = {f["name"]: f for f in form["fields"]}
    assert shown["covered_device_ids"]["readonly"] and shown["sla_policy_ids"]["readonly"]
    p03(c.officer).write(
        model="fix.contract", record_id=k.id, values={"covered_device_ids": [_device(c).id]}
    )
    k.invalidate_recordset()
    assert len(k.covered_device_ids) == 1


def test_the_submit_capture_routes_the_contract_for_approval(c, p03):  # noqa: F811 - the imported fixture
    k = _contract(c)
    out = p03(c.officer).action(
        model="fix.contract",
        ids=[k.id],
        method="action_request_approval",
        kwargs={"justification": "Bank AMC at the list price"},
    )
    assert out.get("success"), out
    k.invalidate_recordset()
    assert k.state == "pending_approval"


def test_the_legal_review_capture_records_the_reviewer(c, p03):  # noqa: F811 - the imported fixture
    k = _contract(c, value=1500000.0)
    assert k.legal_review_required
    k.with_user(c.officer).action_request_approval(justification="Hospital AMC, 1.5M")
    out = p03(c.legal).action(
        model="fix.contract",
        ids=[k.id],
        method="action_legal_review",
        kwargs={"note": "Liability cap and SLA credits reviewed"},
    )
    assert out.get("success"), out
    k.invalidate_recordset()
    assert k.legal_reviewed_by == c.legal
    assert k.legal_review_note == "Liability cap and SLA credits reviewed"


def test_the_price_revision_capture_raises_a_pricing_amendment(c, p03):  # noqa: F811 - the imported fixture
    k = _active(c, value=120000.0)
    out = p03(c.officer).write(
        model="fix.contract.amendment",
        values={
            "name": "Escalation 5%",
            "contract_id": k.id,
            "kind": "pricing",
            "delta_value": 6000.0,
            "effective_from": str(c.today + timedelta(days=1)),
            "note": "Annual escalation clause",
        },
    )
    assert "error" not in out, out
    amendment = c.env["fix.contract.amendment"].search([("contract_id", "=", k.id)])
    assert amendment.kind == "pricing" and amendment.state == "draft"
    k.invalidate_recordset()
    assert k.annual_value == 120000.0, "the price changes only once the amendment is approved"


def test_the_signature_capture_records_stamp_duty_on_a_draft(c, p03):  # noqa: F811 - the imported fixture
    k = _contract(c, stamp_duty_cert_no=False, stamp_duty_amount=0.0)
    out = p03(c.officer).write(
        model="fix.contract",
        record_id=k.id,
        values={"stamp_duty_cert_no": "SD-2026-0042", "stamp_duty_amount": 450.0},
    )
    assert "error" not in out, out
    k.invalidate_recordset()
    assert k.stamp_duty_cert_no == "SD-2026-0042"


# --- the reports page 5 and page 10 show ----------------------------------------


def test_the_sla_credit_reports_name_the_amc_behind_each_credit(c):  # noqa: F811 - the imported fixture
    k = _active(c, value=240000.0, name="M08 capture AMC %s" % c.customer.id)
    msp = c.env["fix.msp.contract"].create(
        {
            "name": "M08 capture MSP",
            "contract_id": k.id,
            "operating_unit_id": c.ou.id,
            "device_count": 4,
            "per_device_monthly": 2500.0,
            "sla_target_pct": 95.0,
        }
    )
    c.env["fix.msp.sla.credit"].sudo().create(
        {
            "msp_contract_id": msp.id,
            "period_label": "M08-2026-10",
            "manual_amount": 100.0,
            "dofa_justification": "Missed response target twice",
        }
    )
    register = m08_reports.sla_credit_register(c.env)
    assert k.name in [r["contract"] for r in register["rows"]]
    pnl = m08_reports.contract_pnl(c.env)
    row = next(r for r in pnl["rows"] if r["contract"] == k.name)
    assert row["sla_credits"] == 100.0
