# A05 workflow audit (2026-11-03), M14 Trade-in & Refurbishment: E3-E12 + P2.
#
# Every control the A05 probes (working/A05_evidence/probes/m14/probe_m14.py)
# found open is tested as NON-ADMIN users created here, each holding only the
# role groups its step needs (the superuser is trusted by the field guard and
# would hide a gap). Each control is attacked three ways where it applies:
# the wrong transition, a plain write() (the JSON-RPC path) and the real
# /p03/model/write endpoint. The legitimate path is run end to end through
# the real actions. The odoo_env fixture rolls everything back.
import itertools
import json
import re
import types
from datetime import timedelta
from pathlib import Path

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as g
from odoo.addons.cd_p03_portal.controllers.a05 import m14 as surface
from odoo.addons.cd_workflow_engine.tests.approval_helpers import assigned, inbox_task
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
GUARD = "changes only through its workflow"
ROUTED = "approver's inbox"
TRD = "fix.tradein.request"
M14_JS = Path(__file__).resolve().parents[4] / ("platform/cd_p03_portal/static/src/a05/m14.js")
_SEQ = itertools.count(1)
_MW = getattr(g.P03GenericApiController.model_write, "original_endpoint", None) or (
    g.P03GenericApiController.model_write
)
_MA = getattr(g.P03GenericApiController.model_action, "original_endpoint", None) or (
    g.P03GenericApiController.model_action
)


# --------------------------------------------------------------------------- fixtures
def _user(env, login, groups=(), ou=None):
    n = next(_SEQ)
    vals = {
        "name": "A05 M14 %s %d" % (login, n),
        "login": "a05m14.%s.%d@a05.test" % (login, n),
        "group_ids": [(6, 0, [env.ref("base.group_user").id] + [env.ref(x).id for x in groups])],
    }
    if ou:
        vals.update(operating_unit_ids=[(6, 0, ou.ids)], default_operating_unit_id=ou.id)
    user = env["res.users"].with_context(no_reset_password=True).create(vals)
    assert not user.has_group("base.group_system")
    return user


@pytest.fixture
def m(odoo_env):
    env = odoo_env
    params = env["ir.config_parameter"].sudo()
    # Journeys run with the hold period at 0 days and NEIR-unchecked devices
    # allowed; the tests of those two policies set them explicitly.
    params.set_param("cd_tradein.hold_days", "0")
    params.set_param("cd_tradein.allow_neir_unchecked", "1")
    ou = env["operating.unit"].search([], limit=1)
    x = types.SimpleNamespace(env=env, ou=ou)
    x.clerk = _user(env, "clerk", ["cd_workshop.group_fix_workshop_user"], ou)
    x.clerk2 = _user(env, "clerk2", [], ou)
    approver_groups = [
        "cd_entity_config.group_dofa_tier_1",
        "cd_tradein.group_tradein_payout_approver",
    ]
    x.approver = _user(env, "approver", approver_groups, ou)
    x.tier1 = _user(env, "tier1", ["cd_entity_config.group_dofa_tier_1"], ou)
    x.officer = _user(env, "officer", ["cd_tradein.group_tradein_provenance_officer"], ou)
    x.qa = _user(env, "qa", ["cd_tradein.group_tradein_qa_inspector"], ou)
    x.valmgr = _user(env, "valmgr", ["cd_tradein.group_tradein_valuation_manager"], ou)
    x.tech = _user(env, "tech", [], ou)
    env["hr.employee"].create({"name": "A05 M14 Technician", "user_id": x.tech.id})
    x.wofficer = _user(env, "wofficer", ["cd_device_registry.group_warranty_officer"], ou)
    brand = env["fix.brand"].create({"name": "A05 M14 Brand", "code": "A5M14C"})
    x.model = env["fix.device.model"].create({"name": "A05 M14 Phone", "brand_id": brand.id})
    grid = (
        env["fix.tradein.price.grid"]
        .with_user(x.clerk)
        .create({"device_model_id": x.model.id, "market_ref_price": 20000})
    )
    grid.with_user(x.valmgr).action_approve()
    x.grid = grid
    saved = getattr(g, "request", None)
    _CR.append(env.cr)
    yield x
    _CR.pop()
    g.request = saved


def p03_write(x, model, rec_id, values, user=None):
    g.request = types.SimpleNamespace(env=x.env(user=(user or x.clerk).id))
    return _MW(g.P03GenericApiController(), model=model, record_id=rec_id, values=values)


def p03_action(x, model, rec, method, user=None, **kwargs):
    g.request = types.SimpleNamespace(env=x.env(user=(user or x.clerk).id))
    return _MA(
        g.P03GenericApiController(), model=model, ids=rec.ids, method=method, kwargs=kwargs or None
    )


def device(x):
    n = next(_SEQ)
    return x.env["fix.device"].create(
        {
            "device_model_id": x.model.id,
            "serial_number": "A05M14-SN-%04d" % n,
            "imei_1": "35%013d" % (4400000 + n),
        }
    )


def cert(x, dev, verified=True):
    vals = {"method": "nist_800_88", "serial_number": dev.serial_number}
    if verified:
        log = x.env["ir.attachment"].create({"name": "wipe.log", "raw": b"nwipe: PASS"})
        vals.update(sector_count=1000, wipe_log_attachment_id=log.id)
    c = x.env["fix.data.wipe.certificate"].create(vals)
    if verified:
        c.action_verify()
    return c


def nid():
    return "47%08d" % (next(_SEQ) * 6113)


def request(x, user=None, **vals):
    vals.setdefault("customer_id", x.env["res.partner"].create({"name": "A05 M14 Seller"}).id)
    vals.setdefault("customer_nid", nid())
    vals.setdefault("operating_unit_id", x.ou.id)
    if "device_id" not in vals:
        vals["device_id"] = device(x).id
    return x.env[TRD].with_user(user or x.clerk).create(vals).with_user(x.clerk)


def valued(x, rec):
    """The offer from an applied valuation on the governed grid (20,000)."""
    val = x.env["fix.tradein.valuation"].with_user(x.clerk).create({"tradein_id": rec.id})
    val.action_apply_to_tradein()
    return rec


def screen(x, rec, with_nid=True, imei=None):
    prov = (
        x.env["fix.tradein.provenance"]
        .with_user(x.clerk)
        .create(
            {
                "tradein_id": rec.id,
                "imei": imei or rec.device_id.imei_1,
                "evidence_ref": "GSMA + *16061# lookup %s" % rec.name,
                "lock_status": "off",
                "customer_nid_no": rec.customer_nid if with_nid else False,
            }
        )
    )
    prov.with_user(x.officer).action_clear()
    return prov


def accepted(x, rec=None, **screen_kw):
    rec = rec or request(x)
    valued(x, rec)
    rec.action_send_offer()
    screen(x, rec, **screen_kw)
    rec.action_accept()
    return rec


def refurbishing(x, rec=None, **kw):
    rec = accepted(x, rec, **kw)
    rec.action_collect()
    rec.write({"wipe_certificate_id": cert(x, rec.device_id).id})
    rec.action_wipe()
    rec.action_refurbish()
    return rec


def finish_steps(x, rec, parts=0.0, labour=0.0):
    for step in rec.refurbishment_ids.filtered(lambda s: s.state == "pending"):
        step.with_user(x.tech).write({"parts_cost": parts, "labor_cost": labour})
        step.with_user(x.tech).action_start()
        step.with_user(x.tech).action_complete_repair()


def qa(x, rec, passed=12, total=12):
    row = (
        x.env["fix.refurb.qa"]
        .with_user(x.clerk)
        .create({"tradein_id": rec.id, "tests_total": total, "tests_passed": passed})
    )
    row.with_user(x.qa).action_submit_result()
    return row


def graded(x, rec=None, grade="b", **kw):
    rec = refurbishing(x, rec, **kw)
    finish_steps(x, rec)
    qa(x, rec)
    rec.write({"grade": grade})
    rec.action_grade()
    return rec


def resale(x, rec=None, **kw):
    rec = graded(x, rec, **kw)
    rec.action_resale_ready()
    return rec


def approved(x, rec, value=20000.0, approver=None):
    rec.write({"graded_value": value})
    if rec.revision_state == "pending":
        rec.action_accept_revision()
    rec.action_request_payout_approval()
    approver = approver or x.approver
    task = inbox_task(rec, approver)
    assert task, "routed to %s" % assigned(rec).mapped("login")
    task.with_user(approver).action_approve(comment="ok")
    assert rec.payout_approval_state == "approved"
    return rec


_CR = []


def refused(fn, match=None):
    """fn() is refused (inside a savepoint, so the test goes on)."""
    with pytest.raises(REFUSED) as exc, _CR[-1].savepoint():
        fn()
    if match:
        assert re.search(match, str(exc.value)), str(exc.value)
    return exc.value


# =============================================================== E3: the field guard
GUARDED = {
    "state": "closed",
    "payout_approval_state": "approved",
    "payout_amount": 1.0,
    "psr_verified": True,
    "tds_certificate_no": "TDS-A05-0001",
    "accepted_offer_value": 1.0,
    "hold_released": True,
    "parts_cost": 10.0,
    "labour_cost": 10.0,
}


@pytest.mark.parametrize(("field", "value"), sorted(GUARDED.items()))
def test_request_workflow_fields_refuse_write_and_p03(m, field, value):
    """M14-1/2/10/11: state, payout approval, PSR, certificate and money fields."""
    rec = request(m)
    before = rec[field]
    with pytest.raises(UserError, match=GUARD), m.env.cr.savepoint():
        rec.write({field: value})
    res = p03_write(m, TRD, rec.id, {field: value})
    assert res.get("error"), res
    rec.invalidate_recordset()
    assert rec[field] == before


def test_request_approver_stamp_and_forged_birth_are_refused(m):
    rec = request(m)
    with pytest.raises(UserError, match=GUARD), m.env.cr.savepoint():
        rec.write({"payout_approved_by_id": m.clerk2.id})
    with pytest.raises(UserError, match=GUARD), m.env.cr.savepoint():
        request(m, state="graded")
    with pytest.raises(UserError, match=GUARD), m.env.cr.savepoint():
        rec.write({"dofa_approved": True, "dofa_approved_tier": "tier_4"})
    assert rec.state == "draft" and not rec.payout_approved_by_id


def test_forged_approval_never_pays(m):
    """M14-2: an 'approved' nobody gave (no approver stamp, no routed
    decision) is refused at the payout, even if the superuser forged it."""
    rec = resale(m)
    rec.write({"graded_value": 20000})
    rec.sudo().write({"payout_approval_state": "approved"})
    refused(rec.action_pay, "no recorded approver")
    assert rec.state == "resale_ready" and not rec.payout_execution_id


# =============================================== wrong transitions (M14-13, M14-19)
def test_send_offer_never_reopens_a_trade_in(m):
    rec = accepted(m)
    refused(rec.action_send_offer, "from draft only")
    rec.sudo().write({"state": "closed"})
    refused(rec.action_send_offer, "from draft only")
    res = p03_action(m, TRD, rec, "action_send_offer")
    assert not res["success"]
    assert rec.state == "closed"


def test_pay_and_grade_refuse_the_wrong_state(m):
    rec = request(m)
    refused(rec.action_pay, "Payout from graded")
    refused(rec.action_grade, "Grade from refurbished")
    refused(rec.action_resale_ready, "Resale from graded")


def test_customer_rejection_needs_a_reason_and_freezes(m):
    rec = valued(m, request(m))
    rec.action_send_offer()
    refused(lambda: rec.action_reject(), "why")
    res = p03_action(m, TRD, rec, "action_reject", reason="Customer kept the phone")
    assert res["success"], res
    assert rec.state == "rejected" and rec.rejected_reason
    refused(lambda: rec.write({"offered_value": 1.0}), "closed record")
    assert not p03_write(m, TRD, rec.id, {"resale_value": 5.0}).get("success")


# ===================================== M14-14 / P2: frozen offer and governed grid
def test_accepted_offer_and_payee_are_frozen(m):
    rec = accepted(m)
    assert rec.accepted_offer_value == 20000 and rec.accepted_by_id == m.clerk
    refused(lambda: rec.write({"offered_value": 2000.0}), "frozen")
    res = p03_write(m, TRD, rec.id, {"offered_value": 2000.0})
    assert res.get("error"), res
    mule = m.env["res.partner"].create({"name": "A05 Accomplice"})
    refused(lambda: rec.write({"customer_id": mule.id}), "frozen")
    rec.invalidate_recordset()
    assert rec.offered_value == 20000 and rec.customer_id != mule


def test_offer_must_come_from_the_governed_grid(m):
    rec = request(m, offered_value=50000)
    refused(rec.action_send_offer, "applied valuation")
    val = (
        m.env["fix.tradein.valuation"]
        .with_user(m.clerk)
        .create({"tradein_id": rec.id, "market_ref_price": 60000})
    )
    assert val.is_override
    refused(val.action_apply_to_tradein, "state its reason")
    val.write({"override_reason": "Sealed box, two weeks old"})
    refused(val.action_apply_to_tradein, "approves it before it is applied")
    with pytest.raises(UserError, match=GUARD), m.env.cr.savepoint():
        val.write({"override_state": "approved"})
    assert p03_write(m, "fix.tradein.valuation", val.id, {"override_state": "approved"}).get(
        "error"
    )
    val.action_request_override_approval()
    refused(lambda: val.with_user(m.clerk2).action_approve_override(), "role")
    refused(lambda: val.write({"market_ref_price": 90000}), "frozen")
    val.with_user(m.valmgr).action_approve_override()
    val.action_apply_to_tradein()
    assert rec.offered_value == 60000
    rec.action_send_offer()
    assert rec.state == "offered"


def test_grid_price_approval_is_segregated(m):
    row = (
        m.env["fix.tradein.price.grid"]
        .with_user(m.valmgr)
        .create({"device_model_id": m.model.id, "market_ref_price": 25000})
    )
    refused(lambda: row.with_user(m.clerk).action_approve(), "role")
    refused(lambda: row.with_user(m.valmgr).action_approve(), "Segregation")
    with pytest.raises(UserError, match=GUARD), m.env.cr.savepoint():
        row.with_user(m.valmgr).write({"state": "approved"})
    refused(lambda: m.grid.with_user(m.valmgr).write({"market_ref_price": 1.0}), "not edited")


# ================================================= E7: provenance and KYC (M14-5/6/7)
def test_provenance_defaults_assert_nothing(m):
    rec = request(m)
    prov = m.env["fix.tradein.provenance"].with_user(m.clerk).create({"tradein_id": rec.id})
    assert not prov.customer_nid_verified
    assert not prov.btrc_neir_checked
    assert prov.btrc_neir_status == "unchecked"
    assert not prov.customer_nid_no
    assert not (prov.stolen_checked or prov.blacklist_checked)
    assert prov.state == "pending"


def test_neir_check_never_claims_a_check(m):
    rec = request(m)
    prov = (
        m.env["fix.tradein.provenance"]
        .with_user(m.clerk)
        .create({"tradein_id": rec.id, "imei": "999999999999999"})
    )
    res = p03_action(m, "fix.tradein.provenance", prov, "action_run_neir_check")
    assert res["success"], res
    assert prov.state == "pending"
    assert prov.btrc_neir_status == "unchecked" and not prov.btrc_neir_checked
    assert not (prov.stolen_checked or prov.blacklist_checked)


def test_provenance_verdict_and_hits_are_guarded(m):
    rec = request(m)
    Prov = m.env["fix.tradein.provenance"].with_user(m.clerk)
    ok = Prov.create({"tradein_id": rec.id, "imei": "356789012345671"})
    for field, value in (
        ("state", "cleared"),
        ("stolen_checked", True),
        ("customer_nid_verified", True),
        ("btrc_neir_status", "valid"),
        ("warranty_checked", True),
    ):
        with pytest.raises(UserError, match=GUARD), m.env.cr.savepoint():
            ok.write({field: value})
        assert p03_write(m, "fix.tradein.provenance", ok.id, {field: value}).get("error")
    # anyone may RAISE a hit (it flags the screen); nobody lowers it
    hit = Prov.create({"tradein_id": rec.id, "imei": "356789012345672", "stolen_hit": True})
    assert hit.state == "flagged"
    refused(lambda: hit.write({"stolen_hit": False}), "hard stop")
    assert p03_write(m, "fix.tradein.provenance", hit.id, {"stolen_hit": False}).get("error")
    hit.invalidate_recordset()
    assert hit.stolen_hit and hit.state == "flagged"
    refused(lambda: hit.with_user(m.officer).action_clear(), "cannot be cleared")


def test_provenance_clearance_needs_an_officer_evidence_and_no_lock(m):
    rec = request(m)
    prov = (
        m.env["fix.tradein.provenance"]
        .with_user(m.clerk)
        .create({"tradein_id": rec.id, "imei": rec.device_id.imei_1})
    )
    refused(lambda: prov.with_user(m.clerk).action_clear(), "role")
    refused(lambda: prov.with_user(m.officer).action_clear(), "evidence")
    prov.write({"evidence_ref": "GSMA lookup 77"})
    refused(lambda: prov.with_user(m.officer).action_clear(), "Find My")
    prov.write({"lock_status": "on"})
    refused(lambda: prov.with_user(m.officer).action_clear(), "Find My")
    prov.write({"lock_status": "off", "customer_nid_no": "4700000000"})
    refused(lambda: prov.with_user(m.officer).action_clear(), "not the seller")
    prov.write({"customer_nid_no": rec.customer_nid})
    # an officer never clears a trade-in they raised
    own = request(m, user=m.officer)
    own_prov = (
        m.env["fix.tradein.provenance"]
        .with_user(m.officer)
        .create(
            {
                "tradein_id": own.id,
                "imei": own.device_id.imei_1,
                "evidence_ref": "x",
                "lock_status": "off",
            }
        )
    )
    refused(lambda: own_prov.with_user(m.officer).action_clear(), "Segregation")
    prov.with_user(m.officer).action_clear()
    assert prov.state == "cleared" and prov.customer_nid_verified
    assert prov.cleared_by_id == m.officer
    refused(lambda: prov.write({"imei": "356789012345679"}), "frozen")


def test_stolen_hit_is_a_hard_stop_a_newer_clean_row_does_not_mask(m):
    """M14-6 (P_05, P_06): a stolen device is not accepted, collected,
    refurbished or paid, whatever screen comes after the hit."""
    rec = valued(m, request(m))
    rec.action_send_offer()
    m.env["fix.tradein.provenance"].with_user(m.clerk).create(
        {"tradein_id": rec.id, "imei": rec.device_id.imei_1, "stolen_hit": True}
    )
    screen(m, rec)  # a newer, clean, cleared screen
    refused(rec.action_accept, "hard stop")
    assert rec.state == "offered"
    # a hit arriving after acceptance stops the collection
    rec2 = accepted(m)
    m.env["fix.tradein.provenance"].with_user(m.clerk2).create(
        {"tradein_id": rec2.id, "imei": rec2.device_id.imei_1, "blacklist_hit": True}
    )
    refused(rec2.action_collect, "hard stop")


def test_unchecked_neir_devices_are_refused_by_default(m):
    """§7.4 provenance policy: NEIR cannot be queried until 1 Jan 2027, so
    every screen reads 'unchecked'; the shipped switch refuses such devices."""
    # with no parameter at all the code refuses (the shipped data says "0" too)
    m.env["ir.config_parameter"].sudo().set_param("cd_tradein.allow_neir_unchecked", False)
    rec = valued(m, request(m))
    rec.action_send_offer()
    screen(m, rec)
    refused(rec.action_accept, "unchecked")
    m.env["ir.config_parameter"].sudo().set_param("cd_tradein.allow_neir_unchecked", "1")
    rec.action_accept()
    assert rec.state == "accepted"


def test_accept_needs_a_current_screen_of_this_device(m):
    rec = valued(m, request(m))
    rec.action_send_offer()
    refused(rec.action_accept, "no current, cleared provenance")
    screen(m, rec, imei="356789012345600")  # another device's IMEI
    refused(rec.action_accept, "not this device")


@pytest.mark.parametrize(
    "bad",
    ["0000000000", "1111111111", "1234567890", "1990123456", "19901234567890", "1234512"],
)
def test_placeholder_or_malformed_nid_is_refused(m, bad):
    rec = request(m)
    with pytest.raises(ValidationError), m.env.cr.savepoint():
        rec.write({"customer_nid": bad})
    assert p03_write(m, TRD, rec.id, {"customer_nid": bad}).get("error")


def test_nid_is_bound_to_one_seller(m):
    rec = request(m)
    with pytest.raises(ValidationError, match="another customer"), m.env.cr.savepoint():
        request(m, customer_nid=rec.customer_nid)
    # the same seller may trade again under the same NID
    request(m, customer_id=rec.customer_id.id, customer_nid=rec.customer_nid)


def test_payout_needs_an_officer_verified_nid_and_a_current_screen(m):
    rec = resale(m, with_nid=False)
    approved(m, rec)
    refused(rec.action_pay, "has not been verified")
    screen(m, rec)  # the officer now sights the NID card
    old = m.env["fix.tradein.provenance"].sudo().search([("tradein_id", "=", rec.id)])
    old.write({"checked_on": fields.Date.today() - timedelta(days=45)})
    refused(rec.action_pay, "no current")
    assert not rec.payout_execution_id


def test_kyc_cap_per_nid(m):
    m.env["ir.config_parameter"].sudo().set_param("cd_tradein.kyc_payout_cap_per_nid_30d", "15000")
    rec = resale(m)
    approved(m, rec)
    refused(rec.action_pay, "KYC cap")


# ============================================================= E4: the wipe gate (M14-9)
def test_wipe_gate_is_rechecked_on_every_later_move(m):
    rec = request(m)
    # the superuser forges the state; no certificate was ever attached
    rec.sudo().write({"state": "refurbished", "grade": "a"})
    m.env["fix.refurbishment"].sudo().create(
        {"name": "s", "tradein_id": rec.id, "step": "repair", "state": "done"}
    )
    m.env["fix.refurb.qa"].sudo().create(
        {"tradein_id": rec.id, "tests_total": 1, "tests_passed": 1, "qa_state": "pass"}
    )
    refused(rec.action_grade, "wipe gate")
    rec.sudo().write(
        {"state": "graded", "refurb_grade_id": m.env["fix.refurb.grade"].search([], limit=1).id}
    )
    refused(rec.action_resale_ready, "wipe gate")
    other = device(m)
    rec.sudo().write({"wipe_certificate_id": cert(m, other).id})  # another serial
    refused(rec.action_resale_ready, "wipe gate")
    assert rec.state == "graded" and not rec.graded_stock_id


# ===================================================== M14-12: costed steps and QA
def test_refurb_step_state_is_guarded_and_ordered(m):
    rec = refurbishing(m)
    step = rec.refurbishment_ids.filtered(lambda s: s.state == "pending")[:1]
    with pytest.raises(UserError, match=GUARD), m.env.cr.savepoint():
        step.write({"state": "done"})
    assert p03_write(m, "fix.refurbishment", step.id, {"state": "done"}).get("error")
    refused(step.action_complete_repair, "start it")
    res = p03_action(m, "fix.refurbishment", step, "action_start", user=m.tech)
    assert res["success"], res
    step.with_user(m.tech).action_complete_repair()
    assert step.state == "done" and step.completed_by_id == m.tech
    refused(lambda: step.write({"parts_cost": 99.0}), "can no longer change")


def test_grade_needs_every_step_done_and_a_measured_qa_pass(m):
    rec = refurbishing(m)
    rec.write({"grade": "b"})
    refused(rec.action_grade, "not done")
    finish_steps(m, rec)
    refused(rec.action_grade, "no passed QA")
    failed = qa(m, rec, passed=0, total=12)
    assert failed.qa_state == "fail"
    refused(rec.action_grade, "no passed QA")
    qa(m, rec, passed=12, total=12)
    rec.action_grade()
    assert rec.state == "graded"


def test_qa_verdict_is_derived_guarded_and_independent(m):
    rec = refurbishing(m)
    QA = m.env["fix.refurb.qa"].with_user(m.clerk)
    with pytest.raises(UserError, match=GUARD), m.env.cr.savepoint():
        QA.create({"tradein_id": rec.id, "tests_total": 12, "tests_passed": 0, "qa_state": "pass"})
    row = QA.create({"tradein_id": rec.id, "tests_total": 12, "tests_passed": 3})
    assert row.qa_state == "pending"
    assert p03_write(m, "fix.refurb.qa", row.id, {"qa_state": "pass"}).get("error")
    refused(lambda: row.with_user(m.clerk).action_submit_result(), "role")
    row.with_user(m.qa).action_submit_result()
    assert row.qa_state == "fail"
    refused(lambda: row.write({"tests_passed": 12}), "frozen")
    # QA independence: a technician who repaired the unit does not pass it
    finish_steps(m, rec)
    m.tech.write({"group_ids": [(4, m.env.ref("cd_tradein.group_tradein_qa_inspector").id)]})
    own = QA.create({"tradein_id": rec.id, "tests_total": 5, "tests_passed": 5})
    refused(lambda: own.with_user(m.tech).action_submit_result(), "independence")


def test_step_costs_roll_up_into_the_request_and_the_stock(m):
    rec = refurbishing(m)
    finish_steps(m, rec, parts=1000.0, labour=500.0)
    steps_total = sum(rec.refurbishment_ids.mapped("total_cost"))
    assert steps_total == 4 * 1500.0
    assert rec.refurbishment_cost == steps_total
    qa(m, rec)
    rec.write({"grade": "b"})
    rec.action_grade()
    rec.action_resale_ready()
    assert rec.graded_stock_id.refurbishment_cost == steps_total


def test_grade_rows_only_while_refurbishing(m):
    """M14-18: a grade row after resale-ready rewrote the request's grade."""
    rec = resale(m)
    Grade = m.env["fix.tradein.grade"].with_user(m.clerk)
    refused(lambda: Grade.create({"tradein_id": rec.id, "grade": "e"}), "in refurbishment")
    assert rec.grade == "b"


# ============================================== E5 / E11: the routed payout approval
def test_payout_is_routed_to_an_authorised_approver_only(m):
    rec = resale(m)
    rec.write({"graded_value": 20000})
    res = p03_action(m, TRD, rec, "action_request_approval")
    assert res["success"], res
    assert rec.payout_approval_state == "pending" and rec.approval_state == "pending"
    who = assigned(rec)
    assert m.approver in who
    assert not ({m.tier1, m.clerk, m.clerk2} & set(who))
    # pressed directly, the decisions refuse: they come from the inbox
    refused(lambda: rec.with_user(m.approver).action_approve_payout(), ROUTED)
    refused(lambda: rec.with_user(m.approver).action_dofa_approve(), ROUTED)
    refused(lambda: rec.with_user(m.clerk2).action_approve_payout(), ROUTED)
    refused(lambda: rec.with_user(m.clerk).action_reject_payout(reason="x"), ROUTED)
    res = p03_action(m, TRD, rec, "action_approve_payout", user=m.approver)
    assert res == {"success": False, "error": "Action not available for this surface"}
    inbox_task(rec, m.approver).with_user(m.approver).action_approve(comment="ok")
    assert rec.payout_approval_state == "approved"
    assert rec.payout_approved_by_id == m.approver and rec.dofa_approved
    assert rec.payout_approved_partner_id == rec.customer_id


def test_the_requester_never_decides_and_reject_needs_a_reason(m):
    approver2 = _user(
        m.env,
        "approver2",
        ["cd_entity_config.group_dofa_tier_1", "cd_tradein.group_tradein_payout_approver"],
        m.ou,
    )
    rec = resale(m)
    rec.write({"graded_value": 20000})
    rec.with_user(m.approver).action_request_payout_approval()
    assert m.approver not in assigned(rec) and approver2 in assigned(rec)
    task = inbox_task(rec, approver2)
    refused(lambda: task.with_user(approver2).action_reject(comment=""), "why")
    task.with_user(approver2).action_reject(comment="Grade disputed")
    assert rec.payout_approval_state == "rejected" and not rec.dofa_approved
    refused(rec.action_pay, "must be approved")


def test_recall_by_the_requester(m):
    rec = resale(m)
    rec.write({"graded_value": 20000})
    rec.action_request_payout_approval()
    res = p03_action(m, TRD, rec, "action_recall_approval")
    assert res["success"], res
    assert rec.payout_approval_state == "none" and rec.approval_state == "none"


def test_approval_pins_payee_net_tds_and_nid(m):
    """M14-4 (A_06, A_07): after approval the payee is frozen and a change of
    the TDS, the NID or the graded value voids the approval."""
    rec = resale(m)
    approved(m, rec)
    mule = m.env["res.partner"].create({"name": "A05 Accomplice"})
    refused(lambda: rec.write({"customer_id": mule.id}), "frozen")
    rec.write({"tds_applicable": True})  # the net drops: the approval goes
    assert rec.payout_approval_state == "none" and not rec.dofa_approved
    refused(rec.action_pay, "must be approved")
    approved(m, rec, value=20000)
    rec.write({"tds_applicable": False})
    assert rec.payout_approval_state == "none"
    approved(m, rec, value=20000)
    rec.write({"graded_value": 19000})
    assert rec.payout_approval_state == "none" and not rec.dofa_approved


def test_revised_offer_needs_the_customers_reacceptance(m):
    rec = resale(m)
    rec.write({"graded_value": 15000})
    assert rec.revision_state == "pending"
    refused(rec.action_request_payout_approval, "revised value")
    res = p03_action(m, TRD, rec, "action_accept_revision")
    assert res["success"], res
    assert rec.revision_state == "accepted"
    rec.action_request_payout_approval()
    assert rec.payout_approval_state == "pending"


# ============================================================= PSR (M14-10)
def test_psr_needs_a_tin_a_document_and_another_person(m):
    rec = request(m)
    rec.write({"graded_value": 10000, "tds_applicable": True, "tds_rate_pct": 5.0})
    # no PSR and no e-TIN are two defaults: 5% x 1.5 x 1.5 (the M51-7 floor)
    assert rec.tds_amount == 1125.0
    assert p03_write(m, TRD, rec.id, {"psr_verified": True}).get("error")
    rec.invalidate_recordset()
    assert not rec.psr_verified and rec.tds_amount == 1125.0
    refused(lambda: rec.with_user(m.clerk2).action_verify_psr(), "e-TIN")
    rec.write({"taxpayer_tin": "583920174635"})
    assert rec.tds_amount == 750.0  # the e-TIN clears one default; no PSR is still one
    refused(lambda: rec.with_user(m.clerk2).action_verify_psr(), "Attach the PSR")
    doc = m.env["ir.attachment"].create({"name": "psr.pdf", "raw": b"PSR"})
    rec.write({"psr_attachment_id": doc.id})
    refused(rec.action_verify_psr, "Segregation")
    rec.with_user(m.clerk2).action_verify_psr()
    assert rec.psr_verified and rec.psr_verified_by_id == m.clerk2
    assert rec.tds_amount == 500.0  # no default left: the statutory rate
    rec.write({"taxpayer_tin": "583920174699"})
    assert not rec.psr_verified  # a PSR is verified against one e-TIN


def test_tds_rate_never_below_the_statutory_rate(m):
    rec = request(m)
    with pytest.raises(ValidationError, match="statutory"), m.env.cr.savepoint():
        rec.write({"tds_applicable": True, "tds_rate_pct": 1.0})


# ================================================================ P03 surface
def _js_actions():
    text = M14_JS.read_text(encoding="utf-8")
    body = text[text.index("export const SCREENS") : text.index("/* Report chips")]
    out = {}
    for chunk in re.split(r"\n  '(?=M14-)", body)[1:]:
        model = re.search(r"model: '([a-z0-9_.]+)'", chunk)
        if model:
            out.setdefault(model.group(1), set()).update(re.findall(r"\bm: '(\w+)'", chunk))
    return out


def test_surface_whitelists_follow_the_routing(m):
    acts = surface.SURFACES[TRD]["actions"]
    assert {"action_request_approval", "action_recall_approval"} <= acts
    assert not {"action_approve_payout", "action_reject_payout", "action_dofa_approve"} & acts
    for model, methods in _js_actions().items():
        if model not in surface.SURFACES:
            continue  # graded stock is M38's surface
        allowed = surface.SURFACES[model]["actions"]
        assert methods <= allowed, (model, sorted(methods - allowed))
        for method in methods:
            assert hasattr(m.env[model], method), (model, method)
    for model, conf in surface.SURFACES.items():
        guarded = (
            m.env[model]._fix_guarded_fields()
            if hasattr(m.env[model], "_fix_guarded_fields")
            else set()
        )
        assert not (set(conf["writable"]) & guarded), (model, set(conf["writable"]) & guarded)


def test_kpis_and_packs_stay_in_the_users_companies(m):
    """E2 / M18-11 for M14: a second company's trade-in is not counted."""
    clerk_env = m.env(user=m.clerk.id)
    before = surface.kpis(clerk_env)
    other = m.env["res.company"].create({"name": "A05 M14 Other Company"})
    partner = m.env["res.partner"].create({"name": "Other Co Seller", "company_id": other.id})
    m.env[TRD].create({"customer_id": partner.id, "company_id": other.id, "offered_value": 999})
    after = surface.kpis(clerk_env)
    assert after["open_tradeins"] == before["open_tradeins"]
    request(m)
    assert surface.kpis(clerk_env)["open_tradeins"] == before["open_tradeins"] + 1
    for name, pack in surface.REPORTS.items():
        assert isinstance(pack(clerk_env), dict), name


# ================================================================= the full journey
def test_full_journey_as_the_real_roles(m):
    rec = resale(m)
    approved(m, rec)
    rec.action_pay()
    pex = rec.payout_execution_id
    assert rec.state == "closed" and pex.state == "pending"
    assert (pex.source_model, pex.source_id, pex.amount) == (TRD, rec.id, 20000.0)
    assert pex.partner_id == rec.customer_id
    assert (
        json.loads(
            m.env["fix.event.outbox"]
            .search([("event_type", "=", "tradein.paid"), ("aggregate_id", "=", rec.id)])
            .payload
        )["payout"]
        == 20000.0
    )
    # a closed trade-in is frozen and never reopened
    refused(lambda: rec.write({"resale_value": 1.0}), "closed record")
    refused(rec.action_send_offer, "from draft only")


# ======================================================= E6 / E10 / E12 hand-offs
def test_stock_is_capitalised_at_the_payout_not_the_offer(m):
    """M14-15 (R_07): offer 20,000, graded and paid 15,000."""
    rec = resale(m)
    assert rec.graded_stock_id.acquisition_cost == 20000.0  # before grading's value is known
    approved(m, rec, value=15000.0)
    rec.action_pay()
    assert rec.payout_amount == 15000.0
    assert rec.graded_stock_id.acquisition_cost == 15000.0
    assert rec.inventory_valuation == 15000.0 + rec.refurbishment_cost


def test_tds_is_registered_with_m51_for_nbr_remittance(m):
    """M14-11 (A_08, A_09): the withheld tax becomes an M51 register line."""
    rec = resale(m)
    rec.write({"tds_applicable": True, "tds_rate_pct": 5.0, "taxpayer_tin": "583920174635"})
    approved(m, rec, value=10000.0)
    rec.action_pay()
    line = rec.withholding_line_id
    assert line and line.state == "withheld" and line.tax_kind == "tds"
    # e-TIN but no sighted PSR: one default, x1.5, which the M51 row's floor requires
    assert (line.base_amount, line.amount, line.partner_id) == (10000.0, 750.0, rec.customer_id)
    assert line.multiplier == 1.5
    assert line.source_ref == rec.name
    assert rec.payout_execution_id.amount == 9250.0
    with pytest.raises(UserError, match=GUARD), m.env.cr.savepoint():
        rec.write({"withholding_line_id": False})
    other = request(m)
    with pytest.raises(UserError, match=GUARD), m.env.cr.savepoint():
        other.write({"tds_certificate_no": "TDS-DUP-1"})


def test_hold_period_blocks_resale_until_the_cron_releases_it(m):
    m.env["ir.config_parameter"].sudo().set_param("cd_tradein.hold_days", "7")
    rec = graded(m)
    # the hold counts from the local day, not UTC
    assert rec.hold_until == fields.Date.context_today(rec) + timedelta(days=7)
    refused(rec.action_resale_ready, "hold period")
    Request = m.env[TRD]
    assert rec.id not in Request.search([("hold_released", "=", True)]).ids
    rec.sudo().write({"hold_until": fields.Date.context_today(rec) - timedelta(days=1)})
    assert Request.cron_tradein_hold_period() >= 1
    assert rec.hold_released
    assert Request.cron_tradein_hold_period() == 0  # safe to re-run
    rec.action_resale_ready()
    assert rec.state == "resale_ready"
    cron = m.env.ref("cd_tradein.ir_cron_tradein_hold_period")
    assert cron.active and "cron_tradein_hold_period" in cron.code


def _part(x):
    Part = x.env["fix.spare.part"]
    part = Part.search([("company_id", "=", x.env.company.id)], limit=1)
    if part:
        return part
    category = Part._fields["part_category"].selection
    category = category(Part) if callable(category) else category
    return Part.create(
        {"name": "A05 Harvest Screen", "part_number": "A05-HV-SCR", "part_category": category[0][0]}
    )


def _location(x):
    Loc = x.env["fix.stock.location"]
    loc = Loc.search([("company_id", "=", x.env.company.id)], limit=1)
    if loc:
        return loc
    kind = Loc._fields["location_type"].selection
    kind = kind(Loc) if callable(kind) else kind
    return Loc.create({"name": "A05 Harvest Bin", "code": "A05HV", "location_type": kind[0][0]})


def test_harvest_workflow_hands_parts_to_m15_stock(m):
    """M14-16 (H_01): harvest ran from a free state write and reached no
    inventory. It now runs from a graded parts-only unit into an M15 receipt."""
    unit = graded(m, grade="e")
    Harvest = m.env["fix.tradein.harvest"].with_user(m.clerk)
    line = Harvest.create(
        {
            "tradein_id": unit.id,
            "component": "screen",
            "part_id": _part(m).id,
            "quantity": 2,
            "unit_value": 1500,
            "target": "spare_stock",
        }
    )
    with pytest.raises(UserError, match=GUARD), m.env.cr.savepoint():
        line.write({"state": "harvested"})
    assert p03_write(m, "fix.tradein.harvest", line.id, {"state": "harvested"}).get("error")
    refused(line.action_harvest, "receiving location")
    m.env["ir.config_parameter"].sudo().set_param(
        "cd_tradein.harvest_location_id", str(_location(m).id)
    )
    res = p03_action(m, "fix.tradein.harvest", line, "action_harvest")
    assert res["success"], res
    receipt = line.receipt_id
    assert line.state == "harvested" and receipt.state == "draft"
    assert (receipt.source_model, receipt.source_res_id) == ("fix.tradein.harvest", line.id)
    assert receipt.line_ids.qty_accepted == 2 and receipt.line_ids.unit_cost == 1500
    event = m.env["fix.event.outbox"].search(
        [("event_type", "=", "tradein.harvested"), ("aggregate_id", "=", line.id)]
    )
    assert json.loads(event.payload)["target"] == "spare_stock"
    refused(lambda: line.write({"quantity": 5}), "final")
    # a resaleable (grade B) unit is not broken up
    resaleable = graded(m)
    other = Harvest.create(
        {"tradein_id": resaleable.id, "component": "battery", "target": "recycle"}
    )
    refused(other.action_harvest, "grade E")


def test_resale_warranty_is_issued_by_the_sale(m):
    """M14-17 (H_02): the warranty was a manual row any clerk voided."""
    rec = resale(m)
    Warranty = m.env["fix.tradein.warranty"].with_user(m.clerk)
    refused(lambda: Warranty.create({"tradein_id": rec.id}), "issued by the resale")
    stock = rec.graded_stock_id
    stock.sudo().action_sell()
    event = {"aggregate": "fix.graded.stock", "aggregate_id": stock.id, "payload": {}}
    refused(lambda: m.env[TRD].with_user(m.clerk).consume_graded_stock_sold(event), "relay")
    out = m.env[TRD].sudo().consume_graded_stock_sold(event)
    assert out["created"]
    warranty = m.env["fix.tradein.warranty"].browse(out["id"])
    assert warranty.state == "active" and warranty.graded_stock_ref == stock.name
    assert warranty.end_date > warranty.start_date
    cover = warranty.device_warranty_id
    assert cover.device_id == stock.device_id and cover.status == "pending"
    assert cover.warranty_type == "extended"
    assert not m.env[TRD].sudo().consume_graded_stock_sold(event)["created"]  # idempotent
    consumer = m.env.ref("cd_tradein.consumer_graded_stock_sold_warranty")
    assert (consumer.event_type, consumer.method) == (
        "graded_stock.sold",
        "consume_graded_stock_sold",
    )
    with pytest.raises(UserError, match=GUARD), m.env.cr.savepoint():
        warranty.with_user(m.clerk).write({"state": "void"})
    refused(lambda: warranty.with_user(m.clerk).action_void(reason="x"), "role")
    refused(lambda: warranty.with_user(m.wofficer).action_void(reason=""), "why")
    warranty.with_user(m.wofficer).action_void(reason="Unit returned tampered")
    assert warranty.state == "void"


def test_marketplace_channel_is_listed_on_m12(m):
    """E10 / M14-17: a marketplace-channel unit is listed through M12's own
    listing path when cd_marketplace is installed."""
    if "fix.marketplace.order" not in m.env:
        pytest.skip("cd_marketplace is not installed in this database")
    rec = graded(m)
    rec.write({"resale_channel": "marketplace"})
    rec.action_resale_ready()
    order = m.env["fix.marketplace.order"].sudo().browse(rec.marketplace_order_id).exists()
    assert order, "no M12 listing was created"
    assert order.order_type == "refurb_resale" and order.graded_stock_id == rec.graded_stock_id
    assert order.tradein_request_id == rec


def test_ewaste_reuse_routing_opens_one_intake_and_keeps_the_wipe_gate(m):
    """A05 P2 (M18 -> M14): ewaste.reuse_routed opens a draft trade-in intake,
    once per collection; the payload's data_bearing=False skips nothing."""
    if "fix.ewaste.collection" not in m.env:
        pytest.skip("cd_ewaste is not installed in this database")
    dev = device(m)
    customer = m.env["res.partner"].create({"name": "A05 M18 Donor"})
    coll = m.env["fix.ewaste.collection"].create(
        {"customer_id": customer.id, "material_type": "phone", "device_id": dev.id}
    )
    coll.write({"state": "triaged", "triage_grade": "refurbish"})
    coll.write({"state": "routed"})
    event = {
        "aggregate": "fix.ewaste.collection",
        "aggregate_id": coll.id,
        # a forged claim: the consumer reads the collection, not this
        "payload": {"data_bearing": False, "wipe_certificate_id": None, "customer_id": 1},
    }
    Request = m.env[TRD]
    refused(lambda: Request.with_user(m.clerk).consume_ewaste_reuse_routed(event), "relay")
    out = Request.sudo().consume_ewaste_reuse_routed(event)
    assert out["created"]
    intake = Request.browse(out["id"])
    assert intake.state == "draft" and intake.ewaste_collection_id == coll.id
    assert (intake.customer_id, intake.device_id) == (customer, dev)
    again = Request.sudo().consume_ewaste_reuse_routed(event)
    assert (again["created"], again["id"]) == (False, intake.id)
    assert Request.sudo().search_count([("ewaste_collection_id", "=", coll.id)]) == 1
    with pytest.raises(UserError, match=GUARD), m.env.cr.savepoint():
        intake.with_user(m.clerk).write({"ewaste_collection_id": 0})
    # no certificate came with it, and the wipe gate holds downstream
    intake.sudo().write({"state": "wiped"})
    refused(intake.with_user(m.clerk).action_refurbish, "wipe certificate")
    consumer = m.env.ref("cd_tradein.consumer_ewaste_reuse_routed_intake")
    assert (consumer.event_type, consumer.method) == (
        "ewaste.reuse_routed",
        "consume_ewaste_reuse_routed",
    )
    other = m.env["fix.ewaste.collection"].create(
        {"customer_id": customer.id, "material_type": "phone"}
    )
    refused(
        lambda: Request.sudo().consume_ewaste_reuse_routed(
            {"aggregate": "fix.ewaste.collection", "aggregate_id": other.id}
        ),
        "not routed",
    )
