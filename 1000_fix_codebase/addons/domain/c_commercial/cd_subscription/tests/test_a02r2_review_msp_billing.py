# ruff: noqa: F811  (the imported m5 fixture is used as a parameter)
"""A02 pass-2 independent review (2026-11-21), M39 side of M05 (P2 items).

  * an MSP fee change to BDT 0 became an M39 'cancel' proration, and an
    approved cancel changes no price: the fee kept billing. It is flagged for
    finance (who ends the subscription) instead;
  * a pre-pass-2 msp.device_uplift event has no terms history row, so the
    consumer found "nothing new to bill" and the uplift was dropped. Its row
    is recorded from the event (once per event), then billed.

The M05 fixture comes from cd_msp_contract's tests. ``odoo_env`` rolls back.
"""

from odoo import fields
from odoo.addons.cd_msp_contract.tests.test_a02_p1p2_cd_msp_contract import (  # noqa: F401
    m5,
)
from odoo.addons.cd_subscription.tests.test_a02r2_msp_billing import (
    _amend,
    _consume,
    _pending,
    _subscription,
)


def test_a_fee_falling_to_zero_is_flagged_not_a_silent_cancel(m5):
    sub = _subscription(m5, amount=10000.0)  # 4 devices x 2500
    out = _consume(m5, _amend(m5, per_device_monthly="0"))
    assert out.get("skipped") == "fee falls to 0"
    assert not _pending(sub)
    row = m5.msp.terms_amendment_ids.filtered(lambda r: r.kind == "amendment")
    assert row.billing_state == "flagged" and "cancels" in row.billing_note
    assert sub.recurring_amount == 10000.0  # finance decides the cancellation in M39


def _legacy_event(m5, event_id, old=4, new=6, rate=2500.0):
    return {
        "event_id": event_id,
        "aggregate_id": m5.msp.id,
        "payload": {
            "msp_contract_id": m5.msp.id,
            "old_device_count": old,
            "new_device_count": new,
            "added_devices": new - old,
            "per_device_monthly": rate,
            "monthly_increase": (new - old) * rate,
            "effective_date": fields.Date.to_string(fields.Date.today()),
            "reason": "two more workstations",
        },
    }


def test_a_legacy_device_uplift_event_is_billed_once(m5):
    sub = _subscription(m5, amount=10000.0)
    Uplift = m5.env["fix.subscription.msp.uplift"].sudo()
    out = Uplift.consume_msp_device_uplift(_legacy_event(m5, 9101))
    assert out.get("created") and out["new_amount"] == 15000.0
    row = m5.msp.terms_amendment_ids.filtered(lambda r: r.kind == "amendment")
    assert row.monthly_delta == 5000.0 and row.billing_state == "requested"
    # the SLA terms of the history are the ones in force, not blanks
    assert row.sla_target_pct == m5.msp.sla_target_pct
    assert row.coverage_window == m5.msp.coverage_window
    # redelivered: nothing billed twice
    again = Uplift.consume_msp_device_uplift(_legacy_event(m5, 9101))
    assert again.get("created") is False
    assert len(_pending(sub)) == 1
    assert len(m5.msp.terms_amendment_ids.filtered(lambda r: r.kind == "amendment")) == 1


def test_a_malformed_legacy_event_records_nothing(m5):
    _subscription(m5, amount=10000.0)
    Uplift = m5.env["fix.subscription.msp.uplift"].sudo()
    bad = _legacy_event(m5, 9102)
    bad["payload"]["new_device_count"] = 9  # 4 + 2 is not 9
    out = Uplift.consume_msp_device_uplift(bad)
    assert out.get("created") is False
    assert not m5.msp.terms_amendment_ids
