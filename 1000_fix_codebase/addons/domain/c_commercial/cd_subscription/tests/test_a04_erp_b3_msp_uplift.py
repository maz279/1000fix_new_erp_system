# ruff: noqa: F811  (the imported m5 fixture is used as a parameter)
"""A04 ERP audit M39-F18 (20 Nov 2026): an MSP device uplift relayed after the
count changed again was refused for ever (the event's count no longer equals
the contract's). Each event bills its own step when a later change of the same
contract exists. Rolled back (``odoo_env``)."""

import pytest

pytest.importorskip("odoo.addons.cd_msp_contract")

from odoo.addons.cd_msp_contract.tests.test_a02_erp_msp_uplift_billing import (
    _subscription,
    _uplift_event,
)
from odoo.addons.cd_msp_contract.tests.test_a02_p1p2_cd_msp_contract import m5  # noqa: F401
from odoo.exceptions import UserError


def test_f18_an_uplift_overtaken_by_a_later_change_still_bills_its_step(m5):
    _subscription(m5)
    base = m5.msp.device_count or 0
    first = _uplift_event(m5, base + 10)
    second = _uplift_event(m5, base + 20)
    Consumer = m5.env["fix.subscription.msp.uplift"]
    out = Consumer.consume_msp_device_uplift(first)
    assert out.get("created") is True
    assert Consumer.consume_msp_device_uplift(second).get("created") is True


def test_f18_a_forged_count_with_no_later_change_is_still_refused(m5):
    _subscription(m5)
    event = _uplift_event(m5, (m5.msp.device_count or 0) + 10)
    forged = dict(event, payload=dict(event["payload"], new_device_count=999))
    with pytest.raises(UserError, match="999"), m5.env.cr.savepoint():
        m5.env["fix.subscription.msp.uplift"].consume_msp_device_uplift(forged)
