# ruff: noqa: F811  (the imported m5 fixture is used as a parameter)
"""A04 ERP audit M39-F18 (20 Nov 2026): an MSP device uplift relayed after the
count changed again was refused for ever (the event's count no longer equals
the contract's). Each event bills its own step when a later change of the same
contract exists. Rolled back (``odoo_env``).

Since A02 pass 2 (M05-S06/D8) the consumer bills the contract's recorded
commercial amendments (fix.msp.terms.history), not the event's count: the
first event relayed bills every unbilled amendment of the contract, and a
payload's device count is never trusted. The two protections still hold and
are asserted on the price the subscription is asked to move to."""

import pytest

pytest.importorskip("odoo.addons.cd_msp_contract")

from odoo.addons.cd_msp_contract.tests.test_a02_erp_msp_uplift_billing import (
    _requested_amount,
    _subscription,
    _uplift_event,
)
from odoo.addons.cd_msp_contract.tests.test_a02_p1p2_cd_msp_contract import m5  # noqa: F401


def test_f18_an_uplift_overtaken_by_a_later_change_still_bills_its_step(m5):
    sub = _subscription(m5)
    rate = m5.msp.per_device_monthly
    assert rate > 0
    base = m5.msp.device_count or 0
    first = _uplift_event(m5, base + 10)
    second = _uplift_event(m5, base + 20)
    Consumer = m5.env["fix.subscription.msp.uplift"]
    assert Consumer.consume_msp_device_uplift(first).get("created") is True
    Consumer.consume_msp_device_uplift(second)  # already billed by the first
    # both steps (+10, then +10 more) reach the subscription: nothing is lost
    assert _requested_amount(sub) == pytest.approx(10000.0 + 20 * rate)


def test_f18_a_forged_count_bills_nothing_beyond_the_recorded_amendment(m5):
    sub = _subscription(m5)
    rate = m5.msp.per_device_monthly
    event = _uplift_event(m5, (m5.msp.device_count or 0) + 10)
    forged = dict(event, payload=dict(event["payload"], new_device_count=999))
    m5.env["fix.subscription.msp.uplift"].consume_msp_device_uplift(forged)
    # the forged count bills nothing: only the recorded +10 amendment does
    assert _requested_amount(sub) == pytest.approx(10000.0 + 10 * rate)
