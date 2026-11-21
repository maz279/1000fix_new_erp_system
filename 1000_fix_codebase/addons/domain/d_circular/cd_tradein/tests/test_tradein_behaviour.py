"""cd_tradein behaviour (live ORM, rolled back): Journey 9 trade-in
offer -> collection (M03) -> data wipe (M06 gate) -> refurbishment (M31)
-> grading (M37) -> graded stock (M15) -> payout (M50)."""

from __future__ import annotations

import itertools
import json
from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox, inbox_task
from odoo.exceptions import UserError, ValidationError

TRD = "fix.tradein.request"
_SEQ = itertools.count(1)
_ORDER = [
    "draft",
    "offered",
    "accepted",
    "collected",
    "wiped",
    "refurbished",
    "graded",
    "resale_ready",
    "closed",
]


@pytest.fixture(autouse=True)
def _policy(odoo_env):
    """The lifecycle suite runs under an explicit trade-in policy. The two
    switches below are business decisions (report §7.4 / P2 grid) whose
    fail-closed defaults are tested in test_a05_m14_controls.py: here an
    NEIR-unchecked device may be traded (no NEIR exists until 2027) and an
    offer may be typed in draft."""
    params = odoo_env["ir.config_parameter"].sudo()
    params.set_param("cd_tradein.allow_neir_unchecked", "1")
    params.set_param("cd_tradein.offer_requires_valuation", "0")


def _events(env, event_type, res_id):
    rows = env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate", "=", TRD), ("aggregate_id", "=", res_id)],
        order="id",
    )
    return [json.loads(r.payload) for r in rows]


def _device(env):
    brand = env["fix.brand"].create({"name": "Trade-in Brand (behaviour)", "code": "TRDB"})
    model = env["fix.device.model"].create({"name": "Pixel 7", "brand_id": brand.id})
    # A02 audit M06-1: the wipe certificate binds to the device's media serial
    return env["fix.device"].create({"device_model_id": model.id, "serial_number": WIPE_SN})


WIPE_SN = "TRD-WIPE-SN"


def _grade(env, code):
    return env["fix.refurb.grade"].search([("code", "=", code)], limit=1)


def _nid():
    """A distinct, realistic 10-digit Smart NID per seller (A05 audit M14-7:
    a placeholder such as 1990123456 is refused, and one NID is one seller)."""
    return "58%08d" % (next(_SEQ) * 7919)


def _request(env, **vals):
    vals.setdefault("customer_id", env["res.partner"].create({"name": "Trade-in Customer"}).id)
    # An identified seller: payout refuses without a Smart NID (AML gate).
    vals.setdefault("customer_nid", _nid())
    if vals.get("wipe_certificate_id") and "device_id" not in vals:
        vals["device_id"] = _device(env).id  # the device the certificate certifies
    return env[TRD].create(vals)


def _screen(env, rec):
    """A provenance screen cleared on its evidence (A05 audit M14-5/6: the
    trade-in is accepted, collected and paid only on a current one)."""
    prov = env["fix.tradein.provenance"].create(
        {
            "tradein_id": rec.id,
            "imei": "35%013d" % next(_SEQ),
            "evidence_ref": "GSMA/BTRC lookup %s" % rec.name,
            "lock_status": "off",
            "customer_nid_no": rec.customer_nid or False,
        }
    )
    prov.action_clear()
    return prov


def _finish_refurbishment(env, rec):
    """Every refurbishment step done and a measured QA pass (M14-12)."""
    steps = rec.refurbishment_ids
    if not steps:
        steps = env["fix.refurbishment"].create(
            {"name": "%s · Repair" % rec.name, "tradein_id": rec.id, "step": "repair"}
        )
    steps.filtered(lambda s: s.state != "done").write({"state": "done"})
    env["fix.refurb.qa"].create(
        {"tradein_id": rec.id, "tests_total": 12, "tests_passed": 12, "qa_state": "pass"}
    )


def _certify(env, rec, axis):
    """The grading certificate measuring `axis` (M14 capture pass 2: the grade
    and its master come from the certificate, never from a typed grade)."""
    return env["fix.tradein.grade"].create(
        {"tradein_id": rec.id, "cosmetic_grade": axis, "battery_health_pct": 100}
    )


def _in(env, state, evidence=True, **vals):
    """A request set to `state` by the superuser, with the evidence that state
    implies (A05 audit E4: the gates of the later steps re-check it). Before
    the remediation this helper forged the state with no evidence at all."""
    rec = _request(env, **vals)
    rank = _ORDER.index(state) if state in _ORDER else 0
    if evidence:
        if rank >= _ORDER.index("accepted"):
            _screen(env, rec)
        if rank >= _ORDER.index("collected"):
            rec.write({"hold_until": fields.Date.today() - timedelta(days=1)})
        if rank >= _ORDER.index("refurbished"):
            if not rec.wipe_certificate_id:
                device = rec.device_id or _device(env)
                rec.write({"device_id": device.id, "wipe_certificate_id": _cert(env).id})
            rec.write({"state": "refurbished"})
            _finish_refurbishment(env, rec)
    rec.write({"state": state})
    return rec


def _cert(env, verified=True, **vals):
    """The wipe operator's M06 certificate, with real evidence when verified."""
    # A02 pass 2 review (D16): Purge passes the matrix at release for any media
    vals.setdefault("method", "nist_800_88_purge")
    vals.setdefault("serial_number", WIPE_SN)
    if verified:
        log = env["ir.attachment"].create({"name": "wipe.log", "raw": b"nwipe: PASS"})
        vals.setdefault("sector_count", 1000)
        vals.setdefault("wipe_log_attachment_id", log.id)
    cert = env["fix.data.wipe.certificate"].create(vals)
    if verified:
        cert.action_verify()
    return cert


def _approver(env):
    """The payout approver: the trade-in payout role AND the DOFA tier the
    amount needs (A05 audit M14-3: the four-eyes had no authority group)."""
    login = "tradein-payout-approver"
    return env["res.users"].search([("login", "=", login)], limit=1) or env["res.users"].create(
        {
            "name": "Trade-in Payout Approver",
            "login": login,
            "group_ids": [
                (
                    6,
                    0,
                    [
                        env.ref("base.group_user").id,
                        env.ref("cd_entity_config.group_dofa_tier_1").id,
                        env.ref("cd_tradein.group_tradein_payout_approver").id,
                    ],
                )
            ],
        }
    )


def _approved(env, rec, value):
    """Graded value entered (and, below the offer, re-accepted by the
    customer), then ONE routed approval decided from the approver's M63
    inbox: four-eyes, the payout role and the DOFA tier together."""
    approver = _approver(env)
    rec.write({"graded_value": value})
    if rec.revision_state == "pending":
        rec.action_accept_revision()
    approve_via_inbox(rec, approver, justification="Trade-in payout")
    return rec


# --------------------------------------------------------------------------
# Valuation & bounds
# --------------------------------------------------------------------------


def test_refurbishment_cost_and_inventory_valuation(odoo_env):
    rec = _request(odoo_env, offered_value=40000, parts_cost=4500, labour_cost=1500)
    assert rec.refurbishment_cost == 6000
    assert rec.inventory_valuation == 46000
    rec.write({"labour_cost": 500})
    assert rec.refurbishment_cost == 5000
    assert rec.inventory_valuation == 45000


@pytest.mark.parametrize(
    ("field", "message"),
    [
        ("offered_value", "Offered value"),
        ("resale_value", "Resale value"),
        ("parts_cost", "Parts cost"),
        ("labour_cost", "Labour cost"),
    ],
)
def test_money_fields_cannot_be_negative(odoo_env, field, message):
    with (
        pytest.raises(ValidationError, match=f"{message} cannot be negative"),
        odoo_env.cr.savepoint(),
    ):
        _request(odoo_env, **{field: -1})


def test_names(odoo_env):
    # the module ships the trade-in sequence (data/ir_sequence.xml): a new
    # request is numbered, not left as the "TRD/New" placeholder
    first = _request(odoo_env)
    assert first.name.startswith("TRD/")
    assert first.name != "TRD/New"
    assert _request(odoo_env, name="TRD/LEGACY/9").name == "TRD/LEGACY/9"
    # one sequence per code: retarget the module's own sequence rather than
    # creating a second row for the same code (next_by_code would be ambiguous)
    seq = odoo_env["ir.sequence"].search([("code", "=", TRD)], limit=1)
    seq.prefix = "TRD/T/"
    assert _request(odoo_env).name.startswith("TRD/T/")


def test_device_model_follows_device(odoo_env):
    device = _device(odoo_env)
    assert _request(odoo_env, device_id=device.id).device_model_id == device.device_model_id


# --------------------------------------------------------------------------
# Offer, acceptance, collection
# --------------------------------------------------------------------------


def test_offer_requires_positive_valuation(odoo_env):
    rec = _request(odoo_env)
    with pytest.raises(UserError, match="positive valuation"):
        rec.action_send_offer()
    assert rec.state == "draft"


def test_offer_publishes_value(odoo_env):
    rec = _request(odoo_env, offered_value=12000)
    rec.action_send_offer()
    assert rec.state == "offered"
    assert _events(odoo_env, "tradein.offered", rec.id) == [
        {"customer": "Trade-in Customer", "value": 12000.0}
    ]


def test_accept_only_from_offered(odoo_env):
    rec = _request(odoo_env, offered_value=100)
    with pytest.raises(UserError, match="Accept from offered"):
        rec.action_accept()
    rec.action_send_offer()
    _screen(odoo_env, rec)
    rec.action_accept()
    assert rec.state == "accepted"


def test_collect_only_from_accepted(odoo_env):
    rec = _in(odoo_env, "offered")
    with pytest.raises(UserError, match="Collect from accepted"):
        rec.action_collect()
    assert not rec.consignment_id


def test_collect_creates_pickup_consignment(odoo_env):
    """Regression: the pickup consignment was created without its REQUIRED
    operating unit, so every collection failed in the database."""
    device = _device(odoo_env)
    rec = _in(odoo_env, "accepted", device_id=device.id)
    rec.action_collect()
    assert rec.state == "collected"
    assert rec.consignment_id.consignment_type == "pickup"
    assert rec.consignment_id.operating_unit_id == odoo_env.user.default_operating_unit_id
    assert _events(odoo_env, "tradein.collected", rec.id) == [
        {"device": device.name, "consignment": rec.consignment_id.name}
    ]


def test_collect_uses_request_ou_and_existing_consignment(odoo_env):
    ou = odoo_env["operating.unit"].create(
        {
            "name": "Trade-in OU (behaviour)",
            "code": "TRD-OU",
            "partner_id": odoo_env.company.partner_id.id,
        }
    )
    rec = _in(odoo_env, "accepted", operating_unit_id=ou.id)
    assert rec._operating_unit() == ou
    existing = odoo_env["fix.consignment"].create(
        {"operating_unit_id": ou.id, "scheduled_date": "2026-11-01 10:00:00"}
    )
    rec.write({"consignment_id": existing.id})
    rec.action_collect()
    assert rec.consignment_id == existing
    assert _events(odoo_env, "tradein.collected", rec.id) == [
        {"device": "", "consignment": existing.name}
    ]


def test_collect_without_any_operating_unit_is_refused(odoo_env):
    odoo_env.user.write({"default_operating_unit_id": False})
    rec = _in(odoo_env, "accepted")
    with pytest.raises(UserError, match="has no operating unit"):
        rec.action_collect()
    assert rec.state == "accepted"


# --------------------------------------------------------------------------
# M06 data wipe gate
# --------------------------------------------------------------------------


def test_wipe_only_from_collected(odoo_env):
    rec = _in(odoo_env, "accepted")
    with pytest.raises(UserError, match="Wipe from collected"):
        rec.action_wipe()


def test_wipe_never_fabricates_a_certificate(odoo_env):
    rec = _in(odoo_env, "collected", device_id=_device(odoo_env).id)
    before = odoo_env["fix.data.wipe.certificate"].search_count([])
    with pytest.raises(UserError, match="no M06 data wipe certificate"):
        rec.action_wipe()
    assert odoo_env["fix.data.wipe.certificate"].search_count([]) == before
    assert (rec.state, rec.wipe_certificate_id.id) == ("collected", False)


def test_wipe_refuses_an_unverified_certificate(odoo_env):
    pending = _cert(odoo_env, verified=False)
    rec = _in(odoo_env, "collected", wipe_certificate_id=pending.id)
    with pytest.raises(UserError, match="pending_verification"):
        rec.action_wipe()
    assert rec.state == "collected"


def test_wipe_passes_on_the_operators_verified_certificate(odoo_env):
    cert = _cert(odoo_env, method="cryptographic_erase")
    rec = _in(odoo_env, "collected", wipe_certificate_id=cert.id)
    rec.action_wipe()
    assert rec.state == "wiped"
    assert rec.wipe_certificate_id == cert
    assert _events(odoo_env, "tradein.wiped", rec.id) == [
        {
            "certificate": cert.name,
            "method": "cryptographic_erase",
            "verification_hash": cert.verification_hash,
        }
    ]


# --------------------------------------------------------------------------
# M31 refurbishment
# --------------------------------------------------------------------------


def test_refurbish_only_after_wipe(odoo_env):
    rec = _in(odoo_env, "collected")
    with pytest.raises(UserError, match="the wipe gate"):
        rec.action_refurbish()


def test_refurbish_blocked_without_wipe_certificate(odoo_env):
    rec = _in(odoo_env, "wiped")
    with pytest.raises(UserError, match="verified M06 data wipe certificate"):
        rec.action_refurbish()
    assert not rec.workshop_job_id
    assert rec.state == "wiped"
    rec.wipe_certificate_id = _cert(odoo_env, verified=False)
    with pytest.raises(UserError, match="not verified"):
        rec.action_refurbish()


def test_refurbish_opens_job_at_central_depot(odoo_env):
    """Regression: the workshop job was created with a non-existent
    `problem_description` field and without its required workshop and
    fault description, so refurbishment always crashed."""
    device = _device(odoo_env)
    rec = _in(
        odoo_env,
        "collected",
        device_id=device.id,
        parts_cost=800,
        labour_cost=400,
        wipe_certificate_id=_cert(odoo_env).id,
    )
    rec.action_wipe()
    rec.action_refurbish()
    job = rec.workshop_job_id
    assert rec.state == "refurbished"
    assert job.workshop_id.workshop_type == "central"
    assert job.device_id == device
    assert job.customer_id == rec.customer_id
    assert rec.name in job.fault_description
    assert _events(odoo_env, "tradein.refurbished", rec.id) == [
        {"workshop_job": job.name, "refurb_cost": 1200.0}
    ]


def test_refurbish_falls_back_to_any_company_workshop(odoo_env):
    workshops = odoo_env["fix.workshop"].search([])
    workshops.filtered(lambda w: w.workshop_type == "central").write({"workshop_type": "regional"})
    rec = _in(odoo_env, "collected", wipe_certificate_id=_cert(odoo_env).id)
    rec.action_wipe()
    rec.action_refurbish()
    assert rec.workshop_job_id.workshop_id in workshops


def test_refurbish_without_any_workshop_is_refused(odoo_env):
    odoo_env["fix.workshop"].search([]).write({"active": False})
    rec = _in(odoo_env, "collected", wipe_certificate_id=_cert(odoo_env).id)
    rec.action_wipe()
    with pytest.raises(UserError, match="No active M31 workshop"):
        rec.action_refurbish()
    assert rec.state == "wiped"


def test_refurbish_reuses_existing_job(odoo_env):
    workshop = odoo_env["fix.workshop"].search([], limit=1)
    job = odoo_env["fix.workshop.job"].create(
        {"workshop_id": workshop.id, "fault_description": "Pre-booked refurb"}
    )
    rec = _in(odoo_env, "collected", workshop_job_id=job.id, wipe_certificate_id=_cert(odoo_env).id)
    rec.action_wipe()
    rec.action_refurbish()
    assert rec.workshop_job_id == job


# --------------------------------------------------------------------------
# M37 grading
# --------------------------------------------------------------------------


def test_grade_only_from_refurbished(odoo_env):
    rec = _in(odoo_env, "wiped", grade="a")
    with pytest.raises(UserError, match="Grade from refurbished"):
        rec.action_grade()


def test_grade_required(odoo_env):
    rec = _in(odoo_env, "refurbished")
    # M14 capture pass 2: the grade is the grading certificate's (BRU-TRF-12)
    with pytest.raises(UserError, match="no grading certificate"):
        rec.action_grade()


def test_grade_selection_derived_from_master_grade(odoo_env):
    master = _grade(odoo_env, "C")
    rec = _in(
        odoo_env, "refurbished", refurb_grade_id=_grade(odoo_env, "A").id, offered_value=10000
    )
    _certify(odoo_env, rec, "c")  # the measured grade, not the typed master, decides
    rec.action_grade()
    assert rec.refurb_grade_id == master
    assert rec.state == "graded"
    assert rec.grade == "c"
    assert rec.resale_value == pytest.approx(10000 * 1.6 * master.price_multiplier)
    assert _events(odoo_env, "tradein.graded", rec.id) == [
        {"grade": "c", "grade_master": master.name, "resale_value": rec.resale_value}
    ]


def test_master_grade_linked_from_selection(odoo_env):
    rec = _in(odoo_env, "refurbished", grade="a", offered_value=20000)
    _certify(odoo_env, rec, "a")
    rec.action_grade()
    assert rec.refurb_grade_id == _grade(odoo_env, "A")


def test_selection_without_master_grade_prices_at_benchmark(odoo_env):
    _grade(odoo_env, "D").write({"active": False})
    rec = _in(odoo_env, "refurbished", grade="d", offered_value=300)
    _certify(odoo_env, rec, "d")
    rec.action_grade()
    assert not rec.refurb_grade_id
    # floor benchmark of 1000 BDT, multiplier 1.0 without a master grade
    assert rec.resale_value == 1000.0
    (payload,) = _events(odoo_env, "tradein.graded", rec.id)
    assert payload["grade_master"] == ""


def test_both_grades_set_and_manual_resale_value_kept(odoo_env):
    master = _grade(odoo_env, "B")
    rec = _in(odoo_env, "refurbished", grade="a", refurb_grade_id=master.id, resale_value=55000)
    _certify(odoo_env, rec, "b")
    rec.action_grade()
    assert rec.grade == "b"  # the certificate's, not the typed "a"
    assert rec.refurb_grade_id == master
    assert rec.resale_value == 55000


# --------------------------------------------------------------------------
# M15 graded stock & M50 payout
# --------------------------------------------------------------------------


def test_resale_ready_only_from_graded(odoo_env):
    rec = _in(odoo_env, "refurbished")
    with pytest.raises(UserError, match="Resale from graded"):
        rec.action_resale_ready()


def test_resale_ready_books_graded_stock(odoo_env):
    device = _device(odoo_env)
    master = _grade(odoo_env, "A")
    rec = _in(
        odoo_env,
        "graded",
        device_id=device.id,
        refurb_grade_id=master.id,
        grade="a",
        offered_value=40000,
        parts_cost=4500,
        labour_cost=1500,
        resale_value=58000,
    )
    rec.action_resale_ready()
    stock = rec.graded_stock_id
    assert rec.state == "resale_ready"
    assert stock.device_id == device
    assert stock.grade_id == master
    assert stock.tradein_id == rec.id
    assert stock.acquisition_cost == 40000
    assert stock.refurbishment_cost == 6000
    assert stock.resale_price == 58000
    assert stock.projected_margin == 12000
    assert stock.state == "in_stock"
    assert _events(odoo_env, "tradein.resale_ready", rec.id) == [
        {
            "grade": "a",
            "resale_value": 58000.0,
            "inventory_valuation": 46000.0,
            "graded_stock": stock.name,
        }
    ]


def test_resale_ready_refuses_a_unit_without_device(odoo_env):
    """A05 audit M14-15: a unit with no registered device was put on resale
    with no stock row. It is now refused (the wipe gate binds to a device)."""
    rec = _in(odoo_env, "graded", grade="b", refurb_grade_id=_grade(odoo_env, "B").id)
    rec.write({"device_id": False})
    with pytest.raises(UserError, match="cannot move to resale_ready"):
        rec.action_resale_ready()
    assert rec.state == "graded"
    assert not rec.graded_stock_id


def test_pay_only_from_graded_or_resale_ready(odoo_env):
    rec = _in(odoo_env, "refurbished", offered_value=100)
    with pytest.raises(UserError, match="Payout from graded or resale-ready"):
        rec.action_pay()


def test_pay_refuses_an_unidentified_seller(odoo_env):
    """AML / ITA 2023: no trade-in money leaves without the seller's Smart NID."""
    rec = _in(odoo_env, "graded", offered_value=15000, customer_nid=False)
    _approved(odoo_env, rec, 12500)
    with pytest.raises(UserError, match="Smart NID is required"):
        rec.action_pay()
    assert rec.state == "graded" and not rec.payout_execution_id


@pytest.mark.parametrize("state", ["graded", "resale_ready"])
def test_pay_executes_treasury_payout(odoo_env, state):
    """Regression: the M50 payment execution was created without its
    REQUIRED operating unit, so no trade-in could ever be paid out."""
    rec = _in(odoo_env, state, offered_value=15000)
    _approved(odoo_env, rec, 12500)  # graded below the offer
    rec.action_pay()
    payment = rec.payout_execution_id
    assert rec.state == "closed"
    assert rec.payout_amount == 12500  # the APPROVED graded value, not the offer
    # queued with treasury; only bank/MFS evidence marks it executed
    assert payment.state == "pending"
    assert payment.amount == 12500
    assert payment.method == "mobile_fs"
    assert payment.payee == "Trade-in Customer"
    assert (payment.source_model, payment.source_id) == (TRD, rec.id)
    assert payment.operating_unit_id == odoo_env.user.default_operating_unit_id
    assert payment.display_name.startswith("PEX/")
    assert _events(odoo_env, "tradein.paid", rec.id) == [
        {"payout": 12500.0, "payment_ref": payment.display_name}
    ]


def test_pay_requires_graded_value_and_approval(odoo_env):
    _approver(odoo_env)  # someone the routed request can go to
    rec = _in(odoo_env, "graded", offered_value=15000)
    with pytest.raises(UserError, match="graded payout value"):
        rec.action_pay()
    with pytest.raises(UserError, match="graded payout value"):
        rec.action_request_payout_approval()
    rec.write({"graded_value": 9000})
    rec.action_accept_revision()
    with pytest.raises(UserError, match="'none': it must be approved"):
        rec.action_pay()
    rec.action_request_payout_approval()
    assert (rec.payout_approval_state, rec.payout_requested_by_id) == ("pending", odoo_env.user)
    with pytest.raises(UserError, match="must be approved"):
        rec.action_pay()
    with pytest.raises(UserError, match="Four-eyes"):
        rec.action_approve_payout()
    assert not rec.payout_execution_id and rec.state == "graded"


def test_payout_approval_lifecycle(odoo_env):
    rec = _in(odoo_env, "resale_ready", offered_value=5000)
    _approved(odoo_env, rec, 4000)
    assert rec.payout_approval_state == "approved"
    assert rec.payout_approved_by_id.login == "tradein-payout-approver"
    assert rec.payout_approved_at
    with pytest.raises(UserError, match="already approved"):
        rec.action_request_payout_approval()
    with pytest.raises(UserError, match="Only a pending payout can be approved"):
        rec.action_approve_payout()
    rec.write({"graded_value": 4500})  # a new amount voids the old approval
    assert rec.payout_approval_state == "none"
    rec.action_accept_revision()
    rec.action_request_payout_approval()
    # rejected from the approver's inbox, with a reason (M14-3)
    approver = _approver(odoo_env)
    inbox_task(rec, approver).with_user(approver).action_reject(comment="Grade disputed")
    assert rec.payout_approval_state == "rejected"
    with pytest.raises(UserError, match="Only a pending payout can be rejected"):
        rec.action_reject_payout()
    with pytest.raises(UserError, match="Payout approval from graded"):
        _in(odoo_env, "wiped", graded_value=10).action_request_payout_approval()
    with pytest.raises(ValidationError, match="Graded value cannot be negative"):
        rec.write({"graded_value": -1})


def test_graded_value_is_frozen_once_paid(odoo_env):
    rec = _in(odoo_env, "graded", offered_value=3000)
    _approved(odoo_env, rec, 3000)
    rec.action_pay()
    with pytest.raises(UserError, match="already been sent to treasury"):
        rec.write({"graded_value": 1})


def test_pay_reuses_existing_payout(odoo_env):
    rec = _in(odoo_env, "resale_ready", offered_value=900)
    payment = odoo_env["fix.payment.execution"].create(
        {
            "operating_unit_id": odoo_env.user.default_operating_unit_id.id,
            "source_model": TRD,
            "source_id": rec.id,
            "payee": "Pre-arranged",
            "amount": 900,
        }
    )
    rec.write({"payout_execution_id": payment.id})
    _approved(odoo_env, rec, 900)
    rec.action_pay()
    assert rec.state == "closed"
    assert rec.payout_execution_id == payment
    assert payment.state == "pending"  # not executed a second time by the trade-in


def test_full_journey(odoo_env):
    device = _device(odoo_env)
    rec = _request(odoo_env, device_id=device.id, offered_value=25000, parts_cost=2000)
    rec.action_send_offer()
    _screen(odoo_env, rec)
    rec.action_accept()
    rec.action_collect()
    rec.write({"wipe_certificate_id": _cert(odoo_env, device_id=device.id).id})
    rec.action_wipe()
    rec.action_refurbish()
    _finish_refurbishment(odoo_env, rec)
    _certify(odoo_env, rec, "b")
    rec.action_grade()
    rec.write({"hold_until": fields.Date.today()})  # the hold period has run
    rec.action_resale_ready()
    _approved(odoo_env, rec, 22000)
    rec.action_pay()
    assert rec.state == "closed"
    assert rec.graded_stock_id.grade_id == _grade(odoo_env, "B")
    assert rec.payout_execution_id.state == "pending"  # queued with treasury
    # M14-15: the stock is capitalised at what the seller is paid
    assert rec.graded_stock_id.acquisition_cost == 22000


def test_refurbishment_step_defaults(odoo_env):
    rec = _request(odoo_env)
    step = odoo_env["fix.refurbishment"].create({"name": "Intake", "tradein_id": rec.id})
    assert (step.step, step.state, step.parts_cost) == ("intake", "pending", 0.0)
    assert step.currency_id == odoo_env.ref("base.BDT")
    rec.unlink()
    assert not step.exists()
