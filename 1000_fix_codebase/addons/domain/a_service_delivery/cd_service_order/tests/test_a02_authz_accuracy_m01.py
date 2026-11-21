# A02 authorization / accuracy pass for M01 (cd_service_order).
#
# Each control is tested both ways as NON-ADMIN users holding only the groups
# a front-desk clerk, cashier or approver really holds (the superuser is
# trusted by the guards and would hide a gap):
#   1. a recycling / refurbishment category is not a zero-charge pass;
#   2. one M20 receipt settles one order, whichever of its keys names it;
#   3. an estimate is not approved on its preparer's word alone, is revised
#      only where a new version makes sense, and no line is priced below zero;
#   7. the estimate's VAT rate is the statutory rate, not a typed one.
# ruff: noqa: F811 - `w` / `p03_write` are the shared M01 fixtures of
# test_a02_p0_m01, imported so pytest registers them here.
from decimal import Decimal
from types import SimpleNamespace
from unittest import mock

import pytest
from odoo import Command
from odoo.addons.cd_service_order.tests.test_a02_p0_m01 import (  # noqa: F401 (fixtures)
    _user,
    attempt,
    estimate,
    handover_evidence,
    order,
    p03_write,
    so_request,
    to_estimating,
    to_ready,
    w,
)
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox

INTERNAL = ["recycling", "refurbishment"]


def _standard_vat(env) -> float:
    """The standard VAT rate in force (Tax Rate Master when M51 is installed)."""
    Rate = env.get("fix.tax.rate")
    return float(Rate._fix_vat_rates().standard) if Rate is not None else 15.0


# =========================================================================== 1. category
@pytest.mark.parametrize("category", INTERNAL)
def test_internal_intake_category_alone_approves_nothing(w, category):
    """Born in the category, no estimate: the category is not an entitlement."""
    o = to_estimating(order(w, order_category=category))
    assert "no estimate to send" in (
        attempt(w, lambda: o.with_user(w.clerk).action_send_estimate()) or ""
    )
    assert o.state == "estimate_pending"


@pytest.mark.parametrize("category", INTERNAL)
def test_internal_intake_category_does_not_release_an_unpaid_device(w, category):
    o = to_ready(w, order(w, order_category=category), 10000)  # BDT 11,500 due
    handover_evidence(w, o)
    assert "Settlement Gate" in (attempt(w, lambda: o.with_user(w.clerk).action_deliver()) or "")
    assert (o.state, o.payment_settlement_state) == ("ready", "unpaid")


def test_reclassifying_to_an_internal_intake_does_not_waive_the_charge(w):
    """The audit path: set the category, skip the estimate, release unpaid."""
    o = to_estimating(order(w))
    o.with_user(w.clerk).action_change_category("recycling", "customer wants it scrapped")
    assert o.order_category == "recycling"
    assert attempt(w, lambda: o.with_user(w.clerk).action_send_estimate())
    assert attempt(w, lambda: o.with_user(w.clerk).action_await_approval())
    assert o.state == "estimate_pending"


def test_internal_intake_is_free_once_a_commercial_approver_confirms(w):
    # priced job: the approver's stamp opens the delivery gate
    o = to_ready(w, order(w, order_category="refurbishment"), 10000)
    handover_evidence(w, o)
    o.with_user(w.clerk).action_request_goodwill("Trade-in unit: company-owned stock")
    approve_via_inbox(so_request(w, "goodwill", o), w.approver, requester=w.clerk)
    o.with_user(w.clerk).action_deliver()
    assert (o.state, o.payment_settlement_state) == ("delivered", "covered_zero_charge")
    # unpriced intake: the same stamp lets it through with no estimate
    bare = to_estimating(order(w, order_category="recycling"))
    bare.with_user(w.clerk).action_request_goodwill("E-waste intake, nothing to charge")
    approve_via_inbox(so_request(w, "goodwill", bare), w.approver, requester=w.clerk)
    bare.with_user(w.clerk).action_send_estimate()
    bare.with_user(w.clerk).action_await_approval()
    bare.with_user(w.clerk).action_approve()
    assert bare.state == "approved"


# =========================================================================== 2. receipt
def _receipt(w, reference, amount=11500.0):
    return w.env["fix.ar.receipt"].create(
        {
            "customer_id": w.customer.id,
            "amount": amount,
            "reference": reference,
            "state": "confirmed",
        }
    )


def test_one_m20_receipt_settles_one_order_whichever_key_names_it(w):
    if "fix.ar.receipt" not in w.env:
        pytest.skip("cd_billing_engine not installed")
    # settled by the receipt NUMBER, then claimed again by its bank REFERENCE
    rcpt = _receipt(w, "BK-G3-77")
    assert rcpt.name and rcpt.name != rcpt.reference
    first, second = to_ready(w, order(w), 10000), to_ready(w, order(w), 10000)
    first.with_user(w.clerk).action_mark_settled(rcpt.name, source="m20_receipt")
    assert first.settlement_verified
    assert attempt(
        w, lambda: second.with_user(w.clerk).action_mark_settled("BK-G3-77", source="m20_receipt")
    )
    assert (second.payment_settlement_state, second.settlement_verified) == ("unpaid", False)
    # and the other way round
    rcpt2 = _receipt(w, "BK-G3-78")
    third, fourth = to_ready(w, order(w), 10000), to_ready(w, order(w), 10000)
    third.with_user(w.clerk).action_mark_settled("BK-G3-78", source="m20_receipt")
    assert third.settlement_verified
    assert attempt(
        w, lambda: fourth.with_user(w.clerk).action_mark_settled(rcpt2.name, source="m20_receipt")
    )
    assert fourth.payment_settlement_state == "unpaid"


def test_a_used_receipt_does_not_verify_a_field_collection(w):
    """The receipt already released one device: it cannot verify a typed TrxID."""
    if "fix.ar.receipt" not in w.env:
        pytest.skip("cd_billing_engine not installed")
    rcpt = _receipt(w, "BK-G3-88")
    tech = _user(w.env, "fieldtech")
    held = to_ready(w, order(w), 10000)
    held.with_user(tech)._fix_record_settlement(11500, "BK-G3-88", "field_collection")
    released = to_ready(w, order(w), 10000)
    released.with_user(w.clerk).action_mark_settled(rcpt.name, source="m20_receipt")
    assert released.settlement_verified
    assert attempt(w, lambda: held.with_user(w.clerk).action_verify_settlement())
    assert not held.settlement_verified


# =========================================================================== 3a. approval
def test_preparer_cannot_approve_his_own_estimate_on_his_own_word(w):
    o = to_estimating(order(w))
    est = estimate(w, o, 3000)  # BDT 3,450: under the documented-approval threshold
    est.with_user(w.clerk).action_send()
    assert "Segregation" in (attempt(w, lambda: est.with_user(w.clerk).action_approve()) or "")
    assert (est.state, o.state) == ("sent", "estimate_sent")
    # another member of staff records the customer's verbal approval
    est.with_user(w.clerk2).action_approve()
    assert (est.state, o.state) == ("approved", "approved")


def test_preparer_may_approve_on_the_customers_verified_code(w):
    """The customer's own OTP is the second party: no staff sign-off on top."""
    o = to_estimating(order(w))
    est = estimate(w, o, 3000)
    est.with_user(w.clerk).action_send()
    est.with_user(w.clerk).action_send_customer_otp()
    assert est.with_user(w.clerk).action_verify_customer_otp(otp=w.codes[-1][1])["verified"]
    est.with_user(w.clerk).action_approve()
    assert (est.state, o.state) == ("approved", "approved")


# =========================================================================== 3b. revision
def test_a_draft_or_superseded_estimate_is_not_revised(w):
    o = to_estimating(order(w))
    v1 = estimate(w, o, 3000)
    assert attempt(w, lambda: v1.with_user(w.clerk).action_revise())  # a draft is edited
    assert len(o.estimate_ids) == 1
    v1.with_user(w.clerk).action_send()
    v2 = w.env["fix.estimate"].browse(v1.with_user(w.clerk).action_revise()["res_id"])
    assert (v2.version, v2.state, len(v2.line_ids)) == (2, "draft", 1)
    # v1 is superseded: revising it again would fork a second "version 2"
    assert attempt(w, lambda: v1.with_user(w.clerk).action_revise())
    assert sorted(o.estimate_ids.mapped("version")) == [1, 2]


def test_a_finished_orders_estimate_is_not_revised(w):
    o = to_ready(w, order(w), 3000)
    est = o.estimate_ids
    # still open: an approved estimate is revised (extra fault found on the bench)
    v2 = w.env["fix.estimate"].browse(est.with_user(w.clerk).action_revise()["res_id"])
    assert v2.state == "draft"
    v2.unlink()  # superuser clean-up, so v1 is the latest version again
    o.with_user(w.cashier).action_mark_settled("POS-G3-1", 3450.0, tender="cash")
    handover_evidence(w, o)
    o.with_user(w.clerk).action_deliver()
    assert "delivered" in (attempt(w, lambda: est.with_user(w.clerk).action_revise()) or "")
    o.with_user(w.clerk).action_close()
    assert "closed" in (attempt(w, lambda: est.with_user(w.clerk).action_revise()) or "")
    gone = to_estimating(order(w))
    quote = estimate(w, gone, 3000)
    quote.with_user(w.clerk).action_send()
    gone.with_user(w.clerk).action_cancel(reason_code="customer_declined")
    assert attempt(w, lambda: quote.with_user(w.clerk).action_revise())


# =========================================================================== 3c. floor
def test_list_price_floor_applies_to_a_labour_line_with_a_product(w):
    """The price floor reads the line's product, whatever the line type.

    A04 ERP audit (M11-F1/F6): the floor is the M11 price floor (or the M15
    cost margin floor), never the list_price placeholder (1.00 on fix_real)."""
    service = w.env["product.product"].create(
        {
            "name": "G3 board-level labour",
            "default_code": "A02-G3-LABOUR",
            "list_price": 4000.0,
            "type": "service",
        }
    )
    w.env["fix.price.floor"].create(
        {"name": "G3 labour floor", "product_code": "A02-G3-LABOUR", "floor_price": 4000.0}
    )
    o = order(w)
    line = {"line_type": "labour", "product_id": service.id, "description": "x", "quantity": 1}
    assert "floor is BDT 4000.00" in (
        attempt(
            w,
            lambda: w.env["fix.estimate"]
            .with_user(w.clerk)
            .create({"order_id": o.id, "line_ids": [Command.create(dict(line, unit_price=10.0))]}),
        )
        or ""
    )


def test_no_estimate_line_is_priced_or_counted_below_zero(w):
    """A negative line is an unapproved discount that skips the DOFA route."""
    o = order(w)
    est = estimate(w, o, 5000)
    credit = {"line_type": "labour", "description": "adjustment", "quantity": 1}
    assert attempt(
        w,
        lambda: est.with_user(w.clerk).write(
            {"line_ids": [Command.create(dict(credit, unit_price=-5000.0))]}
        ),
    )
    assert attempt(w, lambda: est.line_ids.with_user(w.clerk).write({"unit_price": -1.0}))
    assert attempt(w, lambda: est.line_ids.with_user(w.clerk).write({"quantity": -1.0}))
    assert est.grand_total == 5750.0
    # a free courtesy line is still a line
    est.with_user(w.clerk).write({"line_ids": [Command.create(dict(credit, unit_price=0.0))]})
    assert est.grand_total == 5750.0


# =========================================================================== 7. VAT rate
def test_estimate_vat_rate_is_the_statutory_rate_not_a_typed_one(w, p03_write):
    std = _standard_vat(w.env)
    o = order(w)
    est = estimate(w, o, 1000)
    assert est.vat_rate == std
    assert "VAT" in (attempt(w, lambda: est.with_user(w.clerk).write({"vat_rate": 0.0})) or "")
    assert attempt(w, lambda: estimate(w, o, 1000, vat_rate=1.0))
    # the workspace save endpoint (vat_rate is on its whitelist) is refused too
    res = p03_write(w.clerk, model="fix.estimate", record_id=est.id, values={"vat_rate": 0.0})
    est.invalidate_recordset()
    assert res.get("error") and est.vat_rate == std
    assert est.grand_total == pytest.approx(1000 * (1 + std / 100))
    # the form posts the rate it shows: writing the value it has is no change
    est.with_user(w.clerk).write({"vat_rate": std, "diagnostic_notes": "saved from the form"})
    # A02 pass 2 (X5-03, D23): nobody types a rate, a commercial approver
    # included: a zero-rated or reduced item is set up on its M51 tariff
    assert attempt(w, lambda: est.with_user(w.approver).write({"vat_rate": 3.33}))
    assert "M51" in attempt(w, lambda: est.with_user(w.approver).write({"vat_rate": 0.0}))


def test_estimate_vat_rate_follows_the_tax_rate_master(w):
    Rate = w.env.get("fix.tax.rate")
    if Rate is None:
        pytest.skip("cd_tax_engine_bd not installed")
    # D23: the estimate asks M51 per line, which also reports the rates' source
    in_force = SimpleNamespace(
        standard=Decimal("17.5"), reduced=frozenset({Decimal("5")}), source="master"
    )
    with mock.patch.object(type(Rate), "_fix_vat_rates", lambda self, *a, **k: in_force):
        est = estimate(w, order(w), 1000)
        assert est.vat_rate == 17.5
        assert attempt(w, lambda: est.with_user(w.clerk).write({"vat_rate": 15.0}))
        assert attempt(w, lambda: est.with_user(w.clerk).write({"vat_rate": 5.0}))
        # A02 pass 2 (D23): a scheduled reduced rate is M51's tariff, not typed
        assert attempt(w, lambda: est.with_user(w.approver).write({"vat_rate": 5.0}))


def test_a_revision_keeps_the_rate_the_estimate_already_carries(w):
    o = to_estimating(order(w))
    est = estimate(w, o, 1000)
    est._guarded().write({"vat_rate": 0.0})  # a rate carried from before D23
    est.with_user(w.clerk).action_send()
    v2 = w.env["fix.estimate"].browse(est.with_user(w.clerk).action_revise()["res_id"])
    assert v2.vat_rate == 0.0  # carried, not re-typed: the clerk changed nothing
