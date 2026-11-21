# ruff: noqa: F811  (the imported m5 fixture is used as a parameter)
"""A02 ERP pass-2 audit (2026-11-20), stream S4: M39 side of M05.

  M05-S03  the SLA credit base prorates each subscription charge by the days
           of its cycle inside the Dhaka month.
  M05-S05  MSP fee changes are billed from the terms history, whatever order
           the events arrive in; a proration computed from an amount the
           subscription no longer has is not applied.
  M05-S06  every commercial amendment (devices up or down, price) reaches
           M39; go-live needs exactly one live subscription; the
           reconciliation report flags differences.
  M05-S07  an offboarded MSP client's subscription churns.

The M05 fixture and helpers come from cd_msp_contract's tests (this database
has both modules). ``odoo_env`` rolls back after each test.
"""

import json
from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_msp_contract.tests.test_a02_erp_msp_uplift_billing import _approver
from odoo.addons.cd_msp_contract.tests.test_a02_p1p2_cd_msp_contract import (  # noqa: F401
    _as,
    m5,
)
from odoo.exceptions import AccessError, UserError

REASON = "Client signed amendment 9 on the 20th"


def _subscription(m5, amount=10000.0, cycle="monthly"):
    """An M39 subscription on the MSP's M08 contract; the first one of a test
    also appoints the DOFA approvers its price changes route to."""
    Sub = m5.env["fix.subscription"].sudo()
    if not Sub.search_count([("contract_id", "=", m5.msp.contract_id.id)]):
        _approver(m5)
    return Sub.create(
        {
            "name": "MSP subscription %d/%d" % (m5.n, Sub.search_count([]) + 1),
            "operating_unit_id": m5.ou.id,
            "customer_id": m5.msp.contract_id.customer_id.id,
            "contract_id": m5.msp.contract_id.id,
            "billing_cycle": cycle,
            "recurring_amount": amount,
        }
    )


def _amend(m5, **terms):
    _as(m5.msp, m5.fin).action_amend_terms(reason=REASON, **terms)
    row = (
        m5.env["fix.event.outbox"]
        .sudo()
        .search(
            [
                ("event_type", "=", "msp.commercial_terms_amended"),
                ("aggregate_id", "=", m5.msp.id),
            ],
            order="id desc",
            limit=1,
        )
    )
    assert row, "no fee-change event"
    return row._relay_event_dict()


def _consume(m5, event):
    return m5.env["fix.subscription.msp.uplift"].sudo().consume_msp_commercial_terms_amended(event)


def _pending(sub):
    return (
        sub.env["fix.subscription.proration"]
        .sudo()
        .search([("subscription_id", "=", sub.id), ("state", "in", ("draft", "pending"))])
    )


# ================================================================ M05-S05


def test_s05_fee_changes_delivered_out_of_order_are_all_billed(m5):
    sub = _subscription(m5, amount=10000.0)
    rate = m5.msp.per_device_monthly
    first = _amend(m5, device_count="6")  # +2 devices
    second = _amend(m5, device_count="9")  # +3 devices
    # the relay delivers the second event first: the first is not lost
    out = _consume(m5, second)
    assert out["created"] and out["new_amount"] == round(10000.0 + 5 * rate, 2)
    again = _consume(m5, first)
    assert again["created"] is False
    assert len(_pending(sub)) == 1
    rows = m5.msp.terms_amendment_ids.filtered(lambda r: r.kind == "amendment")
    assert set(rows.mapped("billing_state")) == {"requested"}
    assert json.loads(json.dumps(second["payload"]))["monthly_delta"] == 3 * rate


def test_s05_a_later_change_supersedes_the_one_still_waiting(m5):
    sub = _subscription(m5, amount=10000.0)
    rate = m5.msp.per_device_monthly
    _consume(m5, _amend(m5, device_count="6"))
    waiting = _pending(sub)
    out = _consume(m5, _amend(m5, device_count="7"))
    assert waiting.state == "void"
    assert out["new_amount"] == round(10000.0 + 3 * rate, 2)
    assert len(_pending(sub)) == 1


def test_s05_a_stale_proration_never_overwrites_a_newer_price(m5):
    sub = _subscription(m5, amount=10000.0)
    P = m5.env["fix.subscription.proration"].sudo()
    stale = P.create_for_plan_change(sub, 10500.0)
    sub.sudo()._guarded().write({"recurring_amount": 11000.0})  # another change applied
    with pytest.raises(UserError, match="computed from a recurring amount"):
        stale._proration_apply_to_subscription()
    assert sub.recurring_amount == 11000.0


def test_s05_an_approved_change_marks_its_amendments_billed(m5):
    sub = _subscription(m5, amount=10000.0)
    out = _consume(m5, _amend(m5, device_count="6"))
    pro = m5.env["fix.subscription.proration"].browse(out["proration_id"])
    pro._proration_apply_to_subscription()
    row = m5.msp.terms_amendment_ids.filtered(lambda r: r.kind == "amendment")
    assert row.billing_state == "billed"
    assert sub.recurring_amount == out["new_amount"]


# ================================================================ M05-S06


def test_s06_a_device_reduction_and_a_price_change_reach_m39(m5):
    sub = _subscription(m5, amount=10000.0)
    _amend(m5, device_count="6")
    # covered devices can drop to the enrolled estate (1 asset)
    out = _consume(m5, _amend(m5, device_count="2"))
    assert out["new_amount"] == round(10000.0 - 2 * m5.msp.per_device_monthly, 2)
    out = _consume(m5, _amend(m5, per_device_monthly="3000"))
    assert out["new_amount"] == round(10000.0 - 2 * 2500.0 + 2 * 500.0, 2)
    assert len(_pending(sub)) == 1


def test_s06_two_subscriptions_flag_the_change_instead_of_guessing(m5):
    _subscription(m5, amount=10000.0)
    _subscription(m5, amount=5000.0)
    out = _consume(m5, _amend(m5, device_count="6"))
    assert out.get("skipped") == "2 subscriptions"
    row = m5.msp.terms_amendment_ids.filtered(lambda r: r.kind == "amendment")
    assert row.billing_state == "flagged"


def test_s06_go_live_needs_exactly_one_live_subscription(m5):
    project = _as(m5.env["fix.msp.onboarding"], m5.eng).create({"msp_contract_id": m5.msp.id})
    with pytest.raises(UserError, match="0 live M39 subscriptions"):
        _as(project, m5.eng).action_go_live()
    _subscription(m5)
    with pytest.raises(UserError) as err:
        _as(project, m5.eng).action_go_live()
    assert "live M39 subscriptions" not in str(err.value)  # now the checklist decides


def test_s06_the_reconciliation_report_flags_differences(m5):
    from odoo.addons.cd_p03_portal.controllers.a02.m05 import REPORTS

    _subscription(m5, amount=10000.0)  # the terms say 4 x 2500 = 10000
    rows = {r["contract"]: r for r in REPORTS["msp_billing_reconciliation"](m5.env)["rows"]}
    assert rows[m5.msp.name]["flag"] == "OK"
    _amend(m5, device_count="6")
    rows = {r["contract"]: r for r in REPORTS["msp_billing_reconciliation"](m5.env)["rows"]}
    row = rows[m5.msp.name]
    assert row["difference"] == -5000.0 and "difference" in row["flag"]
    assert "not billed" in row["flag"]


# ================================================================ M05-S03


def _charge(m5, sub, start, days, amount):
    Charge = m5.env["fix.subscription.charge"].sudo()
    charge = Charge.create(
        {
            "company_id": sub.company_id.id,
            "operating_unit_id": sub.operating_unit_id.id,
            "subscription_id": sub.id,
            "period_start": start,
            "period_end": start + timedelta(days=days - 1),
            "amount": amount,
        }
    )
    charge._create_invoice()
    charge.invoice_id.sudo().write({"state": "issued"})
    return charge


def test_s03_a_quarterly_charge_counts_a_third_in_each_month(m5):
    sub = _subscription(m5, amount=30000.0, cycle="quarterly")
    start = fields.Date.to_date("2026-04-01")
    _charge(m5, sub, start, 91, 30000.0)  # 1 Apr - 30 Jun
    april = m5.msp._msp_invoiced_value("2026-04")
    assert april == round(30000.0 * 30 / 91, 2)  # not the whole 30,000
    may = m5.msp._msp_invoiced_value("2026-05")
    assert may == round(30000.0 * 31 / 91, 2)  # a cycle started in April still counts


def test_s03_a_thirty_day_cycle_is_split_between_its_two_months(m5):
    sub = _subscription(m5, amount=10000.0)
    _charge(m5, sub, fields.Date.to_date("2026-03-16"), 30, 10000.0)  # 16 Mar - 14 Apr
    assert m5.msp._msp_invoiced_value("2026-03") == round(10000.0 * 16 / 30, 2)
    assert m5.msp._msp_invoiced_value("2026-04") == round(10000.0 * 14 / 30, 2)


# ================================================================ M05-S07


def test_s07_an_offboarded_client_churns_its_subscription(m5):
    sub = _subscription(m5)
    Uplift = m5.env["fix.subscription.msp.uplift"]
    event = {"aggregate_id": m5.msp.id, "payload": {"msp_contract_id": m5.msp.id}}
    with pytest.raises(UserError, match="not offboarded"):
        Uplift.sudo().consume_msp_client_offboarded(event)
    m5.msp.sudo()._guarded().write(
        {"lifecycle": "offboarded", "offboarded_at": fields.Datetime.now()}
    )
    with pytest.raises(AccessError):
        Uplift.with_user(m5.fin).consume_msp_client_offboarded(event)
    out = Uplift.sudo().consume_msp_client_offboarded(event)
    assert out["churned"] == 1 and sub.state == "churned"
    assert Uplift.sudo().consume_msp_client_offboarded(event)["churned"] == 0
    wired = (
        m5.env["fix.event.consumer"]
        .sudo()
        .search([("event_type", "=", "msp.client_offboarded"), ("model", "=", Uplift._name)])
    )
    assert wired
