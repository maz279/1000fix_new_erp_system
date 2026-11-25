# ruff: noqa: F811  (the imported m5 fixture is used as a parameter)
"""A02 ERP audit M05-F4 / owner item O14 (20 Nov 2026): an MSP device uplift
is billed. Raising the covered devices published msp.device_uplift, which
nothing consumed, so 50 -> 80 devices changed no bill. M39 now turns it into
the subscription's controlled price change (a second person approves).
``odoo_env`` rolls back after each test.
"""

import json

import pytest
from odoo.addons.cd_msp_contract.tests.test_a02_erp_b1_m05 import REASON
from odoo.addons.cd_msp_contract.tests.test_a02_p1p2_cd_msp_contract import _as, m5  # noqa: F401
from odoo.exceptions import AccessError, UserError


def _approver(m5):
    """The second person M39's price change needs (DOFA tiers, accountant):
    with nobody appointed the request refuses, and the uplift stays a failed,
    retried delivery until finance appoints one."""
    env = m5.env
    groups = ["base.group_user", "account.group_account_user", "account.group_account_manager"]
    groups += ["cd_entity_config.group_dofa_tier_%d" % i for i in range(1, 6)]
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "MSP uplift approver %d" % m5.n,
                "login": "a02.msp.uplift.approver.%d@test" % m5.n,
                "group_ids": [(6, 0, [env.ref(g).id for g in groups])],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )


def _subscription(m5, amount=10000.0, cycle="monthly"):
    _approver(m5)
    Sub = m5.env["fix.subscription"].sudo()
    plan = Sub._fields["plan"].selection
    plan = plan[0][0] if isinstance(plan, list) else "standard"
    return Sub.create(
        {
            "name": "MSP subscription %d" % m5.n,
            "operating_unit_id": m5.ou.id,
            "customer_id": m5.msp.contract_id.customer_id.id,
            "contract_id": m5.msp.contract_id.id,
            "plan": plan,
            "billing_cycle": cycle,
            "recurring_amount": amount,
        }
    )


def _uplift_event(m5, devices):
    _as(m5.msp, m5.fin).action_amend_terms(term="device_count", value=str(devices), reason=REASON)
    row = (
        m5.env["fix.event.outbox"]
        .sudo()
        .search(
            # A02 ERP pass 2 (M05-S06): every fee change, one event type
            [
                ("event_type", "=", "msp.commercial_terms_amended"),
                ("aggregate_id", "=", m5.msp.id),
            ],
            order="id desc",
            limit=1,
        )
    )
    assert row, "no uplift event"
    return row._relay_event_dict()


def _requested_amount(sub):
    """What the price change asks for: a pending amount, or the proration's."""
    sub.invalidate_recordset()
    if sub.pending_recurring_amount:
        return sub.pending_recurring_amount
    Proration = sub.env.get("fix.subscription.proration")
    if Proration is not None:
        pro = Proration.sudo().search([("subscription_id", "=", sub.id)], order="id desc", limit=1)
        for name in ("to_amount", "new_amount", "new_recurring_amount"):
            if pro and name in pro._fields:
                return pro[name]
    return None


def test_an_uplift_requests_the_subscription_price_change(m5):
    sub = _subscription(m5, amount=10000.0)
    old = m5.msp.device_count
    event = _uplift_event(m5, old + 2)
    payload = json.loads(json.dumps(event["payload"]))
    rate = m5.msp.per_device_monthly
    out = m5.env["fix.subscription.msp.uplift"].sudo().consume_msp_commercial_terms_amended(event)
    assert out["created"] and out["new_amount"] == round(10000.0 + 2 * rate, 2)
    assert payload["monthly_delta"] == 2 * rate
    asked = _requested_amount(sub)
    assert asked == out["new_amount"], asked
    # the recurring amount itself waits for the second person
    assert sub.recurring_amount == 10000.0
    # a replay requests nothing twice
    again = m5.env["fix.subscription.msp.uplift"].sudo().consume_msp_commercial_terms_amended(event)
    assert again["created"] is False


def test_a_quarterly_subscription_bills_three_months_of_devices(m5):
    _subscription(m5, amount=30000.0, cycle="quarterly")
    event = _uplift_event(m5, m5.msp.device_count + 1)
    out = m5.env["fix.subscription.msp.uplift"].sudo().consume_msp_commercial_terms_amended(event)
    assert out["new_amount"] == round(30000.0 + 3 * m5.msp.per_device_monthly, 2)


def test_a_forged_amendment_and_a_user_call_are_refused(m5):
    _subscription(m5)
    event = _uplift_event(m5, m5.msp.device_count + 1)
    # the amount comes from the terms history, never the payload (M05-S05)
    forged = dict(event, payload=dict(event["payload"], amendment_id=999999999))
    with pytest.raises(UserError, match="is not a terms change"):
        m5.env["fix.subscription.msp.uplift"].sudo().consume_msp_commercial_terms_amended(forged)
    with pytest.raises(AccessError):
        m5.env["fix.subscription.msp.uplift"].with_user(
            m5.fin
        ).consume_msp_commercial_terms_amended(event)


def test_the_consumer_is_wired(m5):
    for event_type in ("msp.device_uplift", "msp.commercial_terms_amended"):
        row = m5.env["fix.event.consumer"].sudo().search([("event_type", "=", event_type)])
        assert row and row.model == "fix.subscription.msp.uplift"
