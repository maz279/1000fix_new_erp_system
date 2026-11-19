# A02 workflow audit, P0 for M01 (cd_service_order + cd_device_registry).
#
# Each control the A02 probes (working/A02_evidence/probes/m01/probe_m01.py)
# found open is tested BOTH ways: the bypass is refused, and the legitimate
# path still works. Everything acts as NON-ADMIN users created here, with only
# the role groups the step needs: the superuser is trusted by the field guard
# and would hide a gap. The odoo_env fixture rolls the transaction back.
import base64
import itertools
import types
from datetime import timedelta
from unittest import mock

import pytest
from odoo import Command, fields
from odoo.addons.cd_service_order.models import fix_otp_util
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
# a 1x1 PNG: a beyond-economic-repair proposal needs an IMAGE (BRU-SRM-12)
_PNG_B64 = b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
GUARD = "changes only through its workflow"
_SEQ = itertools.count(1)


# --------------------------------------------------------------------------- fixtures
def _user(env, login, groups=()):
    n = next(_SEQ)
    ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "%s %d" % (login, n),
                "login": "a02p0m01.%s.%d@a02.test" % (login, n),
                "group_ids": [(6, 0, ids)],
            }
        )
    )


@pytest.fixture
def w(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env, n=0, codes=[])
    x.clerk = _user(env, "clerk")
    x.clerk2 = _user(env, "clerk2")
    x.cashier = _user(env, "cashier", ["cd_service_order.group_so_cashier"])
    x.cashier2 = _user(env, "cashier2", ["cd_service_order.group_so_cashier"])
    x.inspector = _user(env, "inspector", ["cd_service_order.group_so_qc_inspector"])
    x.approver = _user(env, "approver", ["cd_service_order.group_so_commercial_approver"])
    x.officer = _user(env, "officer", ["cd_device_registry.group_warranty_officer"])
    x.bm = _user(env, "bm", ["cd_entity_config.group_dofa_tier_2"])
    branch = env["fix.branch"].search([("operating_unit_id", "!=", False)], limit=1)
    if not branch:
        ou = env["operating.unit"].search([], limit=1) or env["operating.unit"].create(
            {"name": "A02 P0 OU", "code": "A2P0", "company_id": env.company.id}
        )
        entity = env["fix.entity"].search([], limit=1) or env["fix.entity"].create(
            {"legal_name": "A02 P0 Entity", "code": "A2P0E", "company_id": env.company.id}
        )
        branch = env["fix.branch"].create(
            {
                "name": "A02 P0 Branch",
                "code": "A2P0-BR",
                "entity_id": entity.id,
                "operating_unit_id": ou.id,
            }
        )
    x.branch = branch
    x.customer = env["res.partner"].create({"name": "A02 P0 Customer", "phone": "01711000777"})
    brand = env["fix.brand"].create({"name": "A02P0Brand", "code": "A2P0B"})
    x.model = env["fix.device.model"].create({"name": "A02P0 Model", "brand_id": brand.id})
    # M04's rule that counter cash needs an open cash shift (cd_front_desk, when
    # installed; on by default) is tested there. These M01 tests open no drawer.
    env["ir.config_parameter"].set_param("cd_front_desk.order_cash_requires_open_shift", "0")

    def fake_dispatch(phone, code, ttl, language="bn"):
        x.codes.append((phone, code))

    with mock.patch.object(fix_otp_util, "dispatch_otp", fake_dispatch):
        yield x


def device(w, warranty=None):
    w.n += 1
    dev = w.env["fix.device"].create(
        {
            "device_model_id": w.model.id,
            "owner_id": w.customer.id,
            "serial_number": "A02P0-SN-%03d" % w.n,
        }
    )
    if warranty:
        today = fields.Date.context_today(dev)
        w.env["fix.warranty"].create(
            {
                "device_id": dev.id,
                "start_date": today - timedelta(days=30),
                "end_date": today + timedelta(days=300),
                "status": warranty,  # superuser data load
            }
        )
    return dev


def order(w, user=None, dev=None, **kw):
    vals = {
        "device_id": (dev or device(w)).id,
        "customer_id": w.customer.id,
        "branch_id": w.branch.id,
        "service_type": "walk_in",
        "order_category": "standard",
        "fault_description": "A02 P0 fault",
    }
    vals.update(kw)
    return w.env["fix.service.order"].with_user(user or w.clerk).create(vals)


def estimate(w, o, amount, user=None, **kw):
    vals = {
        "order_id": o.id,
        "line_ids": [
            Command.create(
                {
                    "line_type": "labour",
                    "description": "labour",
                    "quantity": 1,
                    "unit_price": amount,
                }
            )
        ],
    }
    vals.update(kw)
    return w.env["fix.estimate"].with_user(user or w.clerk).create(vals)


def to_estimating(o):
    o.action_intake()
    o.action_start_diagnostic()
    o.action_request_estimate()
    return o


def approved(w, o, amount=3000):
    """Diagnosis -> estimate sent -> approved; approving drives the order."""
    if o.state in ("draft", "intake"):
        if o.state == "draft":
            o.action_intake()
        o.action_start_diagnostic()
        o.action_request_estimate()
    est = estimate(w, o, amount)
    est.action_send()
    if est.grand_total > 5000:  # BRU-SRM-07: the customer's code
        est.action_send_customer_otp()
        assert est.action_verify_customer_otp(otp=w.codes[-1][1])["verified"]
        est.action_approve()
    else:
        # no documented approval is asked this low, so a second member of staff
        # records it: the preparer does not approve on his own word
        est.with_user(w.clerk2).action_approve()
    return est


def to_ready(w, o, amount=3000):
    approved(w, o, amount)
    assert o.state == "approved"
    o.action_start_repair()
    o.action_submit_qc()  # the clerk completed the repair
    qc = (
        w.env["fix.qc.checklist"]
        .with_user(w.clerk)
        .create(
            {"order_id": o.id, "item_ids": [Command.create({"name": "power on", "passed": True})]}
        )
    )
    qc.with_user(w.inspector).action_complete()
    o.action_ready()
    return o


def otp_verify(w, o):
    o.with_user(w.clerk).action_send_delivery_otp()
    code = w.codes[-1][1]
    assert o.with_user(w.clerk).action_verify_delivery_otp(otp=code)["verified"]


def handover_evidence(w, o):
    att = w.env["ir.attachment"].create(
        {"name": "signed-report.pdf", "datas": base64.b64encode(b"%PDF-1.4 signed")}
    )
    o.with_user(w.clerk).write({"recipient_name": "Rahim", "recipient_nid_phone": "01711000777"})
    o.with_user(w.clerk).write({"service_report_attachment_id": att.id})
    otp_verify(w, o)


def so_request(w, kind, target):
    """The live fix.so.approval request (A02 audit B1) for a target."""
    field = "estimate_id" if kind == "manager_key" else "order_id"
    return w.env["fix.so.approval"].search(
        [("kind", "=", kind), (field, "=", target.id)], order="id desc", limit=1
    )


def attempt(w, fn):
    try:
        with w.env.cr.savepoint():
            fn()
    except REFUSED as exc:
        return str(exc) or type(exc).__name__
    return None


# =========================================================================== A1: create
def test_create_refuses_a_late_state_and_accepts_intake(w):
    assert "starts as Draft or Intake" in attempt(w, lambda: order(w, state="closed"))
    assert attempt(w, lambda: order(w, state="ready"))
    born = order(w, state="intake")  # the M04 front desk path
    assert born.state == "intake" and born.intake_completed_at


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("state", "approved"),
        ("payment_settlement_state", "settled"),
        ("amount_settled_bdt", 99999.0),
        ("invoice_ref", "INV/FAKE"),
        ("is_goodwill", True),
        ("is_rework", True),
        ("delivery_otp_verified", True),
        ("sla_clock_paused", True),
        ("priority_override_reason", "because"),
        ("settlement_verified", True),
    ],
)
def test_guarded_order_field_refuses_a_direct_write(w, field, value):
    o = order(w)
    assert GUARD in attempt(w, lambda: o.with_user(w.clerk).write({field: value}))


def test_category_and_priority_change_only_through_their_actions(w):
    o = order(w)
    assert "set at intake" in attempt(
        w, lambda: o.with_user(w.clerk).write({"order_category": "warranty"})
    )
    # M01-1: the re-classification re-runs the warranty gate
    assert "BRU-SRM-02" in attempt(
        w, lambda: o.with_user(w.clerk).action_change_category("warranty", "customer says")
    )
    covered = order(w, dev=device(w, warranty="active"))
    covered.with_user(w.clerk).action_change_category("warranty", "proof shown")
    assert covered.order_category == "warranty"
    # FR-SRM-080
    assert "set at intake" in attempt(w, lambda: o.with_user(w.clerk).write({"priority": "urgent"}))
    assert attempt(w, lambda: o.with_user(w.clerk).action_override_priority("urgent", ""))
    # A02 ERP audit M01-F19: FR-SRM-080 "authorised roles" - a Service Supervisor
    assert "Supervisor" in attempt(
        w, lambda: o.with_user(w.clerk).action_override_priority("urgent", "VIP escalation")
    )
    sup = _user(w.env, "supervisor", ["cd_service_order.group_so_supervisor"])
    o.with_user(sup).action_override_priority("urgent", "VIP escalation")
    assert (o.priority, o.priority_override_user_id) == ("urgent", sup)


# =========================================================================== A4: order <-> estimate
def test_order_approval_needs_an_approved_estimate(w):
    o = to_estimating(order(w))
    # A02 audit M01-P2: no estimate, nothing to send or to await
    assert "no estimate to send" in attempt(w, lambda: o.with_user(w.clerk).action_send_estimate())
    est = estimate(w, o, 3000)
    o.with_user(w.clerk).action_send_estimate()
    assert est.state == "sent"
    o.with_user(w.clerk).action_await_approval()
    est.action_reject()
    assert "no approved estimate" in attempt(w, lambda: o.with_user(w.clerk).action_approve())
    assert o.state == "awaiting_approval"


def test_estimate_approval_drives_the_order(w):
    o = to_estimating(order(w))
    est = estimate(w, o, 3000)
    est.action_send()
    assert o.state == "estimate_sent"
    est.with_user(w.clerk2).action_approve()  # not its preparer (segregation of duties)
    assert (est.state, o.state) == ("approved", "approved")
    assert est.approved_total == est.grand_total and est.approved_by == w.customer


def test_warranty_entitlement_approves_without_an_estimate(w):
    o = to_estimating(order(w, dev=device(w, warranty="active"), order_category="warranty"))
    o.with_user(w.clerk).action_send_estimate()
    o.with_user(w.clerk).action_await_approval()
    o.with_user(w.clerk).action_approve()
    assert o.state == "approved"


@pytest.mark.parametrize("when", ["draft", "rejected", "expired"])
def test_estimate_approves_only_from_sent_and_before_expiry(w, when):
    o = order(w)
    kw = {"expiry_date": fields.Date.today() - timedelta(days=5)} if when == "expired" else {}
    est = estimate(w, o, 3000, **kw)
    if when != "draft":
        est.action_send()
    if when == "rejected":
        est.action_reject()
    assert attempt(w, lambda: est.with_user(w.clerk).action_approve())
    assert est.state != "approved"


def test_expiry_cron_expires_sent_estimates(w):
    est = estimate(w, order(w), 3000, expiry_date=fields.Date.today() - timedelta(days=1))
    est.action_send()
    w.env["fix.estimate"]._cron_expire_estimates()
    assert est.state == "expired"


def test_estimate_state_and_approval_stamps_are_guarded(w):
    est = estimate(w, order(w), 30000)
    for vals in (
        {"state": "approved"},
        {"approved_at": fields.Datetime.now()},
        {"approved_by": w.customer.id},
        {"customer_approval_ref": "trust me"},
    ):
        assert GUARD in attempt(w, lambda v=vals: est.with_user(w.clerk).write(v))


def test_customer_approval_is_a_verified_code(w):
    """M01-9: the documented approval above BDT 5,000 is the code the customer
    read back, not typed text."""
    est = estimate(w, order(w), 10000)
    est.action_send()
    assert "BRU-SRM-07" in attempt(w, lambda: est.action_approve())
    est.action_send_customer_otp()
    assert w.codes[-1][0] == "01711000777"
    bad = est.action_verify_customer_otp(otp="000000" if w.codes[-1][1] != "000000" else "111111")
    assert bad["verified"] is False and est.customer_otp_attempts == 1
    assert est.action_verify_customer_otp(otp=w.codes[-1][1])["verified"]
    assert est.customer_approval_method == "otp"
    est.action_approve()
    assert est.state == "approved"


def test_signed_approval_needs_the_pdf_and_another_person(w):
    est = estimate(w, order(w), 10000)
    est.action_send()
    assert "Attach" in attempt(w, lambda: est.with_user(w.clerk2).action_record_signed_approval())
    att = w.env["ir.attachment"].create(
        {
            "name": "signed-estimate.pdf",
            "datas": b"JVBERg==",
            "res_model": "fix.estimate",
            "res_id": est.id,
        }
    )
    est.with_user(w.clerk).write({"signed_estimate_attachment_id": att.id})
    assert "Segregation" in attempt(
        w, lambda: est.with_user(w.clerk).action_record_signed_approval()
    )
    est.with_user(w.clerk2).action_record_signed_approval()
    assert est.customer_approval_method == "signed_form"


def test_approved_estimate_lines_are_frozen(w):
    o = order(w)
    est = approved(w, o, 4000)
    line = {"line_type": "part", "description": "board", "quantity": 1, "unit_price": 50000}
    assert "frozen" in attempt(
        w, lambda: est.with_user(w.clerk).write({"line_ids": [Command.create(line)]})
    )
    assert "frozen" in attempt(
        w,
        lambda: w.env["fix.estimate.line"]
        .with_user(w.clerk)
        .create(dict(line, estimate_id=est.id)),
    )
    assert "frozen" in attempt(w, lambda: est.line_ids.with_user(w.clerk).unlink())
    # the legitimate path: revise, which is a new draft with the lines
    new = w.env["fix.estimate"].browse(est.with_user(w.clerk).action_revise()["res_id"])
    new.with_user(w.clerk).write({"line_ids": [Command.create(line)]})
    assert new.state == "draft" and est.state == "approved"


def test_manager_key_is_voided_when_the_total_rises(w):
    est = estimate(w, order(w), 30000)
    est.action_send()
    w.env["fix.estimate"].browse(est.id).write({"customer_approval_ref": "portal-OTP"})  # su
    est.with_user(w.clerk).action_request_manager_key("34.5k board repair")
    approve_via_inbox(so_request(w, "manager_key", est), w.bm, requester=w.clerk)
    assert est.manager_approval_uid == w.bm
    est.with_user(w.clerk).write(
        {
            "line_ids": [
                Command.create(
                    {"line_type": "part", "description": "x", "quantity": 1, "unit_price": 170000}
                )
            ]
        }
    )
    assert not est.manager_approval_uid and not est.customer_approval_ref
    assert "BRU-SRM-07" in attempt(w, lambda: est.with_user(w.clerk).action_approve())


def test_superuser_raise_voids_an_approval(w):
    est = approved(w, order(w), 4000)
    w.env["fix.estimate.line"].create(
        {"estimate_id": est.id, "description": "x", "quantity": 1, "unit_price": 50000}
    )
    assert est.state == "sent" and not est.approved_at


def test_price_below_list_needs_the_discount_route(w):
    prod = w.env["product.product"].create({"name": "A02 P0 LCD", "list_price": 5000.0})
    o = order(w)
    part = {"line_type": "part", "product_id": prod.id, "description": "LCD", "quantity": 1}
    assert "listed at BDT 5000" in attempt(
        w,
        lambda: w.env["fix.estimate"]
        .with_user(w.clerk)
        .create({"order_id": o.id, "line_ids": [Command.create(dict(part, unit_price=1.0))]}),
    )
    est = (
        w.env["fix.estimate"]
        .with_user(w.clerk)
        .create({"order_id": o.id, "line_ids": [Command.create(dict(part, unit_price=5000.0))]})
    )
    assert est.parts_total == 5000.0


# =========================================================================== QC (M01-6)
def test_qc_state_is_guarded_and_needs_items(w):
    o = order(w)
    assert GUARD in attempt(
        w,
        lambda: w.env["fix.qc.checklist"]
        .with_user(w.clerk)
        .create({"order_id": o.id, "state": "passed"}),
    )
    empty = w.env["fix.qc.checklist"].with_user(w.clerk).create({"order_id": o.id})
    assert GUARD in attempt(w, lambda: empty.with_user(w.clerk).write({"state": "passed"}))
    assert "at least one item" in attempt(w, lambda: empty.with_user(w.inspector).action_complete())


def test_qc_inspector_is_independent(w):
    tech_user = _user(w.env, "tech", ["cd_service_order.group_so_qc_inspector"])
    tech = w.env["hr.employee"].create({"name": "A02 P0 Tech", "user_id": tech_user.id})
    o = order(w, technician_id=tech.id)
    approved(w, o)
    o.action_start_repair()
    o.with_user(w.inspector).action_submit_qc()  # the inspector completed the repair
    qc = (
        w.env["fix.qc.checklist"]
        .with_user(w.clerk)
        .create({"order_id": o.id, "item_ids": [Command.create({"name": "x", "passed": True})]})
    )
    assert "Only a QC Inspector" in attempt(w, lambda: qc.with_user(w.clerk).action_complete())
    assert "technician who repaired" in attempt(
        w, lambda: qc.with_user(tech_user).action_complete()
    )
    assert "completed the repair" in attempt(w, lambda: qc.with_user(w.inspector).action_complete())
    other = _user(w.env, "inspector2", ["cd_service_order.group_so_qc_inspector"])
    qc.with_user(other).action_complete()
    assert (qc.state, qc.inspected_by) == ("passed", other)
    o.action_ready()
    assert o.state == "ready"


def test_failed_qc_sends_the_order_to_rework(w):
    o = order(w)
    approved(w, o)
    o.action_start_repair()
    o.action_submit_qc()
    qc = (
        w.env["fix.qc.checklist"]
        .with_user(w.clerk)
        .create({"order_id": o.id, "item_ids": [Command.create({"name": "x", "passed": False})]})
    )
    qc.with_user(w.inspector).action_complete()
    assert (qc.state, o.state) == ("failed", "qc_failed")
    o.action_start_repair()
    o.action_submit_qc()
    o.with_user(w.clerk).action_fail_qc()  # the M31 workshop sync's entry point
    assert o.state == "qc_failed"
    assert "already failed" in attempt(
        w, lambda: qc.item_ids.with_user(w.clerk).write({"passed": True})
    )


# =========================================================================== settlement + delivery
def test_settlement_api_refuses_bad_inputs(w):
    o = to_ready(w, order(w), 10000)  # BDT 11,500 due
    S = o.with_user(w.cashier)
    assert "reference" in attempt(w, lambda: S._fix_record_settlement(11500, "", "counter"))
    assert "does not settle" in attempt(w, lambda: S._fix_record_settlement(1, "R1", "counter"))
    assert "Unknown settlement source" in attempt(
        w, lambda: S._fix_record_settlement(11500, "R1", "cash")
    )
    assert "Only a Service Order Cashier" in attempt(
        w, lambda: o.with_user(w.clerk)._fix_record_settlement(11500, "R1", "counter")
    )
    assert "M20 receipt" in attempt(
        w, lambda: S._fix_record_settlement(11500, "NO-SUCH", "m20_receipt")
    )
    # action_mark_settled: no default reference and no arbitrary amount (M01-15)
    assert attempt(w, lambda: o.with_user(w.cashier).action_mark_settled())
    assert attempt(w, lambda: o.with_user(w.cashier).action_mark_settled("X", 1.0))


def test_counter_settlement_opens_the_delivery_gate(w):
    o = to_ready(w, order(w), 10000)
    handover_evidence(w, o)
    assert "Settlement Gate" in attempt(w, lambda: o.with_user(w.clerk).action_deliver())
    o.with_user(w.cashier).action_mark_settled("POS-123", 11500.0)
    assert (o.settlement_source, o.settlement_verified) == ("counter", True)
    o.with_user(w.clerk).action_deliver()
    assert o.state == "delivered" and o.delivered_at
    o.with_user(w.clerk).action_close()
    assert o.state == "closed"


def test_field_collection_holds_the_device_until_verified(w):
    """A typed bKash TrxID is a claim: it settles, but releases nothing."""
    tech_user = _user(w.env, "fieldtech")
    o = to_ready(w, order(w), 10000)
    handover_evidence(w, o)
    o.with_user(tech_user)._fix_record_settlement(11500, "BKASH-TRX-1", "field_collection")
    assert o.payment_settlement_state == "settled" and not o.settlement_verified
    assert "verified settlement" in attempt(w, lambda: o.with_user(w.clerk).action_deliver())
    assert "Only a Service Order Cashier" in attempt(
        w, lambda: o.with_user(w.clerk).action_verify_settlement()
    )
    o.with_user(w.cashier).action_verify_settlement()
    assert o.settlement_verified_by == w.cashier
    o.with_user(w.clerk).action_deliver()
    assert o.state == "delivered"


def test_the_collector_cannot_verify_his_own_collection(w):
    o = to_ready(w, order(w), 10000)
    o.with_user(w.cashier)._fix_record_settlement(11500, "BKASH-TRX-2", "field_collection")
    assert "Segregation" in attempt(w, lambda: o.with_user(w.cashier).action_verify_settlement())
    o.with_user(w.cashier2).action_verify_settlement()
    assert o.settlement_verified


def test_m20_receipt_settles_verified(w):
    if "fix.ar.receipt" not in w.env:
        pytest.skip("cd_billing_engine not installed")
    o = to_ready(w, order(w), 10000)
    rcpt = w.env["fix.ar.receipt"].create(
        {
            "customer_id": w.customer.id,
            "amount": 11500.0,
            "reference": "BK-77",
            "state": "confirmed",
        }
    )
    o.with_user(w.clerk).action_mark_settled(rcpt.name, source="m20_receipt")
    assert (o.amount_settled_bdt, o.settlement_verified) == (11500.0, True)
    other = to_ready(w, order(w), 10000)
    assert "M20 receipt" in attempt(
        w, lambda: other.with_user(w.clerk).action_mark_settled(rcpt.name, source="m20_receipt")
    )


def test_delivery_needs_verified_otp_recipient_and_report(w):
    o = to_ready(w, order(w), 3000)
    o.with_user(w.cashier).action_mark_settled("POS-9", 3450.0)
    msg = attempt(w, lambda: o.with_user(w.clerk).action_deliver())
    assert "handover OTP" in msg and "recipient" in msg and "signed service" in msg
    o.with_user(w.clerk).action_send_delivery_otp()
    wrong = "123456" if w.codes[-1][1] != "123456" else "654321"
    assert o.with_user(w.clerk).action_verify_delivery_otp(otp=wrong)["verified"] is False
    assert not o.delivery_otp_verified and o.delivery_otp_attempts == 1
    handover_evidence(w, o)
    assert o.delivery_otp_verified_by == w.clerk
    o.with_user(w.clerk).action_deliver()
    assert o.state == "delivered"
    # the handover record is frozen
    assert attempt(w, lambda: o.with_user(w.clerk).write({"recipient_name": "Someone else"}))


def test_five_wrong_codes_burn_the_otp(w):
    o = to_ready(w, order(w))
    o.with_user(w.clerk).action_send_delivery_otp()
    right = w.codes[-1][1]
    wrong = "123456" if right != "123456" else "654321"
    for _ in range(fix_otp_util.OTP_MAX_ATTEMPTS):
        o.with_user(w.clerk).action_verify_delivery_otp(otp=wrong)
    assert "Send the handover code" in attempt(
        w, lambda: o.with_user(w.clerk).action_verify_delivery_otp(otp=right)
    )


def test_settlement_cannot_be_reverted_and_close_needs_it(w):
    o = to_ready(w, order(w), 10000)
    handover_evidence(w, o)
    o.with_user(w.cashier).action_mark_settled("POS-1", 11500.0)
    o.with_user(w.clerk).action_deliver()
    assert GUARD in attempt(
        w, lambda: o.with_user(w.clerk).write({"payment_settlement_state": "unpaid"})
    )
    o.with_user(w.clerk).action_close()
    assert o.state == "closed" and o.closed_at


# =========================================================================== zero-charge approvals
def test_goodwill_needs_an_independent_approver(w):
    o = to_ready(w, order(w), 10000)
    handover_evidence(w, o)
    assert GUARD in attempt(
        w,
        lambda: o.with_user(w.clerk).write({"is_goodwill": True, "goodwill_approved_by": w.bm.id}),
    )
    # A02 audit B1: pressed directly, even by an approver, it is refused
    assert "approver's inbox" in attempt(
        w, lambda: o.with_user(w.approver).action_approve_goodwill("loyal customer")
    )
    assert attempt(w, lambda: o.with_user(w.clerk).action_request_goodwill(""))
    own = order(w, user=w.approver)
    # the only approver raised the order: nobody can be routed to
    assert "No one can approve" in attempt(
        w, lambda: own.with_user(w.approver).action_request_goodwill("my own")
    )
    o.with_user(w.clerk).action_request_goodwill("Service failure last visit")
    approve_via_inbox(so_request(w, "goodwill", o), w.approver, requester=w.clerk)
    assert (o.goodwill_approved_by, o.goodwill_cost_attribution_bdt) == (w.approver, 11500.0)
    o.with_user(w.clerk).action_deliver()
    assert (o.state, o.payment_settlement_state) == ("delivered", "covered_zero_charge")


def test_rework_needs_the_same_fault_and_an_approval(w):
    dev = device(w)
    fault = [Command.create({"fault_code": "DSP-01", "description": "No display"})]
    first = order(w, dev=dev, fault_line_ids=fault)
    # A02 ERP audit M01-F21: the window runs from the handover of the repair
    w.env.cr.execute(
        "UPDATE fix_service_order SET state = 'delivered', delivered_at = %s WHERE id = %s",
        (fields.Datetime.now(), first.id),
    )
    first.invalidate_recordset()
    unrelated = order(w, dev=dev, fault_description="Cracked back glass")
    assert not unrelated.is_rework  # same device, unrelated fault (A02 dlv_06)
    o = order(w, dev=dev, fault_line_ids=fault)
    assert o.is_rework and o.rework_of_id
    to_ready(w, o, 10000)
    handover_evidence(w, o)
    # flagged, but still charged until an approver confirms it
    assert "Settlement Gate" in attempt(w, lambda: o.with_user(w.clerk).action_deliver())
    assert attempt(w, lambda: unrelated.with_user(w.clerk).action_request_rework_approval("free"))
    assert "approver's inbox" in attempt(
        w, lambda: o.with_user(w.approver).action_approve_rework("free")
    )
    o.with_user(w.clerk).action_request_rework_approval("Same display fault in 30 days")
    approve_via_inbox(so_request(w, "rework", o), w.approver, requester=w.clerk)
    o.with_user(w.clerk).action_deliver()
    assert o.payment_settlement_state == "covered_zero_charge"


# =========================================================================== cancel / close / hand-offs
def test_cancel_needs_a_reason_and_cascades(w):
    o = to_estimating(order(w))
    est = estimate(w, o, 3000)
    est.action_send()
    assert "cancellation reason" in attempt(w, lambda: o.with_user(w.clerk).action_cancel())
    assert "Describe" in attempt(w, lambda: o.with_user(w.clerk).action_cancel(reason_code="other"))
    o.with_user(w.clerk).action_cancel(reason="estimate_declined: too expensive")
    assert (o.state, o.cancel_reason_code, est.state) == (
        "cancelled",
        "estimate_declined",
        "rejected",
    )


def test_cancelling_a_settled_order_raises_the_refund_hand_off(w):
    o = order(w)
    approved(w, o, 3000)
    o.with_user(w.cashier).action_mark_settled("POS-55", 3450.0)
    # A02 ERP audit X-05: a paid order is cancelled by a Service Supervisor
    assert "only a Service Supervisor" in attempt(
        w, lambda: o.with_user(w.clerk).action_cancel(reason_code="customer_declined")
    )
    from odoo.addons.cd_service_order.tests.test_a02_p1p2_cd_service_order import supervisor

    o.with_user(supervisor(w)).action_cancel(reason_code="customer_declined")
    assert o.payment_settlement_state == "refund_due"
    ev = w.env["fix.event.outbox"].search(
        [("event_type", "=", "service_order.refund_requested"), ("aggregate_id", "=", o.id)]
    )
    assert ev


def test_field_hand_off_carries_priority_and_is_not_duplicated(w):
    if "field_order_ids" not in w.env["fix.service.order"]._fields:
        pytest.skip("cd_field_service not installed")
    if not w.branch.zone_id:
        w.branch.zone_id = w.env["fix.zone"].create({"name": "A02 P0 zone", "code": "A2PZ"})
    o = order(w, user=w.env.user, service_type="onsite", priority="emergency", state="intake")
    fo = o.action_create_field_order()
    assert fo.priority == "3"
    assert "already has a live field order" in attempt(w, lambda: o.action_create_field_order())
    o.action_cancel(reason_code="customer_declined")
    assert fo.state == "cancelled"


def test_workshop_hand_off_carries_priority_and_is_not_duplicated(w):
    if "workshop_job_ids" not in w.env["fix.service.order"]._fields:
        pytest.skip("cd_workshop not installed")
    if not w.env["fix.workshop"].search([("active", "=", True)], limit=1):
        w.env["fix.workshop"].create(
            {"name": "A02 P0 WS", "code": "A2PW", "branch_id": w.branch.id}
        )
    o = order(w, user=w.env.user, priority="urgent")
    o.action_intake()  # M31 receives only a booked-in device (S3, A02 M31 step 1)
    job = o.action_create_workshop_job()
    assert job.priority == "urgent"
    assert "already has a live workshop job" in attempt(w, lambda: o.action_create_workshop_job())


def test_warranty_job_is_not_invoiced_to_the_customer(w):
    if "fix.ar.invoice" not in w.env:
        pytest.skip("cd_billing_engine not installed")
    o = order(w, dev=device(w, warranty="active"), order_category="warranty")
    to_ready(w, o, 4000)
    handover_evidence(w, o)
    o.with_user(w.clerk).action_deliver()
    o.with_user(w.clerk).action_close()
    msg = attempt(
        w,
        lambda: w.env["fix.ar.invoice"].sudo().from_closed_service_order(o, fields.Datetime.now()),
    )
    assert msg and "not charged to the customer" in msg


# =========================================================================== warranty (M01-W1)
def _proof(w):
    att = w.env["ir.attachment"].create({"name": "receipt.pdf", "datas": b"JVBERg=="})
    return w.env["fix.document"].create(
        {"name": "Purchase receipt", "attachment_id": att.id, "document_type": "invoice"}
    )


def test_warranty_is_born_pending_and_gives_no_cover(w):
    dev = device(w)
    today = fields.Date.context_today(dev)
    vals = {"device_id": dev.id, "start_date": today, "end_date": today + timedelta(days=700)}
    assert GUARD in attempt(
        w, lambda: w.env["fix.warranty"].with_user(w.clerk).create(dict(vals, status="active"))
    )
    wty = w.env["fix.warranty"].with_user(w.clerk).create(vals)
    assert wty.status == "pending"
    assert "BRU-SRM-02" in attempt(w, lambda: order(w, dev=dev, order_category="warranty"))
    for forged in ({"status": "active"}, {"verified_at": fields.Datetime.now()}):
        assert GUARD in attempt(w, lambda f=forged: wty.with_user(w.clerk).write(f))


def test_warranty_officer_verifies_someone_elses_registration(w):
    dev = device(w)
    today = fields.Date.context_today(dev)
    wty = (
        w.env["fix.warranty"]
        .with_user(w.officer)
        .create(
            {
                "device_id": dev.id,
                "start_date": today,
                "end_date": today + timedelta(days=365),
                "proof_document_id": _proof(w).id,
            }
        )
    )
    # A02 audit B1: verified from a Warranty Officer's M63 inbox, never pressed
    officer2 = _user(w.env, "officer2", ["cd_device_registry.group_warranty_officer"])
    assert "approver's inbox" in attempt(w, lambda: wty.with_user(officer2).action_verify())
    approve_via_inbox(wty, officer2, requester=w.officer)
    assert w.officer not in wty.approval_request_id.task_ids.mapped("assigned_user_id")
    assert (wty.status, wty.verified_by) == ("active", officer2)
    assert "frozen" in attempt(
        w, lambda: wty.with_user(officer2).write({"end_date": today + timedelta(days=3000)})
    )
    assert order(w, dev=dev, order_category="warranty").id
    assert attempt(w, lambda: wty.with_user(officer2).action_void(""))
    if "fix.warranty.void" not in w.env:
        wty.with_user(officer2).action_void("fraudulent receipt")
        assert wty.status == "voided"
        return
    # M09 second pass (BRU-WTY-17): a typed reason no longer voids cover; the
    # condition is declared with its evidence and applied by another officer.
    assert "evidenced void condition" in attempt(
        w, lambda: wty.with_user(officer2).action_void("fraudulent receipt")
    )
    clerk = _user(w.env, "void_clerk", ["cd_warranty_claims.group_warranty_claims_clerk"])
    void = (
        w.env["fix.warranty.void"]
        .with_user(clerk)
        .create(
            {
                "warranty_id": wty.id,
                "condition": "other",
                "description": "fraudulent receipt",
                "evidence_document_id": _proof(w).id,
            }
        )
    )
    void.with_user(officer2).action_apply()
    assert wty.status == "voided" and "fraudulent receipt" in wty.void_reason


# =========================================================================== P03 endpoint
class _FakeRequest:
    def __init__(self, env):
        self.env = env


@pytest.fixture
def p03_write(w):
    from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api

    def _write(user, **kw):
        with mock.patch.object(api, "request", _FakeRequest(w.env(user=user.id))):
            return api.P03GenericApiController().model_write(**kw)

    return _write


def test_p03_refuses_forged_workflow_fields(w, p03_write):
    o = order(w)
    res = p03_write(
        w.clerk,
        model="fix.service.order",
        record_id=o.id,
        values={
            "payment_settlement_state": "settled",
            "amount_settled_bdt": 99999,
            "is_goodwill": True,
            "delivery_otp_verified": True,
            "sla_clock_paused": True,
        },
    )
    o.invalidate_recordset()
    assert res.get("error") and o.payment_settlement_state == "unpaid" and not o.is_goodwill
    assert p03_write(
        w.clerk, model="fix.service.order", record_id=o.id, values={"order_category": "warranty"}
    ).get("error")
    est = estimate(w, order(w), 30000)
    assert p03_write(
        w.clerk, model="fix.estimate", record_id=est.id, values={"state": "approved"}
    ).get("error")
    wty = (
        w.env["fix.warranty"]
        .with_user(w.clerk)
        .create(
            {
                "device_id": device(w).id,
                "start_date": fields.Date.today(),
                "end_date": fields.Date.today() + timedelta(days=10),
            }
        )
    )
    assert p03_write(
        w.clerk, model="fix.warranty", record_id=wty.id, values={"status": "active"}
    ).get("error")


def test_p03_create_in_ready_does_not_skip_the_workflow(w, p03_write):
    res = p03_write(
        w.clerk,
        model="fix.service.order",
        values={
            "device_id": device(w).id,
            "customer_id": w.customer.id,
            "branch_id": w.branch.id,
            "fault_description": "p03 create",
            "state": "ready",
        },
    )
    created = w.env["fix.service.order"].browse(res.get("id") or 0).exists()
    assert res.get("error") or (created and created.state == "draft")
    # the legitimate create still works
    ok = p03_write(
        w.clerk,
        model="fix.service.order",
        values={
            "device_id": device(w).id,
            "customer_id": w.customer.id,
            "branch_id": w.branch.id,
            "fault_description": "p03 create",
            "order_category": "standard",
            "priority": "high",
        },
    )
    assert ok.get("id"), ok


def test_p03_whitelists_the_new_actions(w):
    from odoo.addons.cd_p03_portal.controllers.a02 import m01

    for model, conf in m01.SURFACES.items():
        if model in w.env:
            for method in conf["actions"]:
                assert hasattr(w.env[model], method), "%s.%s" % (model, method)
    assert {"action_verify_delivery_otp", "action_request_goodwill"} <= m01.SURFACES[
        "fix.service.order"
    ]["actions"]


def test_mark_unrepairable_needs_a_reason_and_cancels(w):
    o = order(w)
    o.action_intake()
    assert "from diagnosis, repair or QC" in attempt(
        w, lambda: o.with_user(w.clerk).action_mark_unrepairable("board dead")
    )
    o.action_start_diagnostic()
    assert "repaired" in attempt(w, lambda: o.with_user(w.clerk).action_mark_unrepairable(""))
    # A02 ERP audit M01-F9 / BRU-SRM-12: photo evidence, then a second
    # technician (the full flow: test_a02erp_m01_b5.test_f9_*)
    techs = []
    for login in ("ber_a", "ber_b"):
        user = _user(w.env, login, ("cd_service_order.group_so_qc_inspector",))
        w.env["hr.employee"].create({"name": user.name, "user_id": user.id})
        techs.append(user)
    photo = w.env["ir.attachment"].create(
        {"name": "ber.png", "datas": _PNG_B64, "res_model": o._name, "res_id": o.id}
    )
    o.with_user(w.clerk).write({"ber_photo_attachment_id": photo.id})
    o.with_user(techs[0]).action_mark_unrepairable("Board corroded beyond repair")
    assert o.state == "diagnostic"
    o.with_user(techs[1]).action_mark_unrepairable("Confirmed")
    assert (o.state, o.cancel_reason_code) == ("cancelled", "unrepairable")
