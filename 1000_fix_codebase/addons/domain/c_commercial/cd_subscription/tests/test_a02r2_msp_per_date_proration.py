# ruff: noqa: F811  (the imported m5 fixture is used as a parameter)
"""MSP fee changes: ONE PRORATION PER EFFECTIVE DATE (owner decision, 21 Nov 2026).

Amendments billed in one run were batched into one M39 proration dated at the
earliest amendment, so a later uplift was charged from the earlier date too.
Each date's amendments are now one proration, prorated from that date, and the
next date's proration is raised (from the amount the previous one left) when
the previous one is decided. Nothing is billed twice; a change still waiting is
superseded only when the earliest unbilled date changes.

The cycle used throughout: billed 30 days, from 20 days ago to 9 days ahead,
BDT 10,000 a month (4 devices x 2,500). ``odoo_env`` rolls back.
"""

from datetime import timedelta

from odoo import fields
from odoo.addons.cd_msp_contract.tests.test_a02_p1p2_cd_msp_contract import (  # noqa: F401
    _as,
    m5,
)
from odoo.addons.cd_subscription.tests.test_a02r2_msp_billing import (
    _charge,
    _consume,
    _pending,
    _subscription,
)

REASON = "Client signed amendment 12 on the 21st"


def _cycle(m5):
    sub = _subscription(m5, amount=10000.0)
    start = fields.Date.today() - timedelta(days=20)
    sub.sudo()._guarded().write({"start_date": start})
    _charge(m5, sub, start, 30, 10000.0)
    return sub


def _amend(m5, days_ago, **terms):
    when = fields.Date.today() - timedelta(days=days_ago)
    _as(m5.msp, m5.fin).action_amend_terms(reason=REASON, effective_date=str(when), **terms)
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
    return row._relay_event_dict()


def _decide(pro):
    """What an approval in M39 does to an MSP change (action_dofa_approve)."""
    pro = pro.sudo()
    pro._guarded().write({"state": "approved"})
    pro._proration_refresh_approved()
    pro._proration_apply_to_subscription()


def _rows(m5):
    return m5.msp.terms_amendment_ids.filtered(lambda r: r.kind == "amendment").sorted(
        "effective_date"
    )


def _all_prorations(sub):
    return (
        sub.env["fix.subscription.proration"]
        .sudo()
        .search([("subscription_id", "=", sub.id)], order="id")
    )


def test_two_dates_in_one_run_are_prorated_each_from_its_own_date(m5):
    sub = _cycle(m5)
    first = _amend(m5, 10, device_count="6")  # +5,000 a month from 10 days ago
    second = _amend(m5, 4, device_count="7")  # +2,500 a month from 4 days ago
    _consume(m5, second)
    _consume(m5, first)  # one run, both unbilled
    pro1 = _pending(sub)
    assert len(pro1) == 1
    assert pro1.effective_date == fields.Date.today() - timedelta(days=10)
    assert (pro1.old_amount, pro1.new_amount) == (10000.0, 15000.0)
    assert pro1.amount == round(5000.0 * 20 / 30, 2)  # 20 of 30 days left
    early, late = _rows(m5)
    assert early.billing_state == "requested" and late.billing_state == "pending"
    # deciding the first raises the second, from the amount the first left
    _decide(pro1)
    pro2 = _pending(sub)
    assert len(pro2) == 1 and pro2 != pro1
    assert pro2.effective_date == fields.Date.today() - timedelta(days=4)
    assert (pro2.old_amount, pro2.new_amount) == (15000.0, 17500.0)
    assert pro2.amount == round(2500.0 * 14 / 30, 2)  # 14 of 30 days left
    _decide(pro2)
    assert sub.recurring_amount == 17500.0
    assert set(_rows(m5).mapped("billing_state")) == {"billed"}
    # exact: 3,333.33 + 1,166.67, not 7,500 x 20/30 = 5,000 from the first date
    assert round(pro1.amount + pro2.amount, 2) == 4500.0


def test_a_replayed_run_bills_nothing_twice(m5):
    sub = _cycle(m5)
    first = _amend(m5, 10, device_count="6")
    second = _amend(m5, 4, device_count="7")
    _consume(m5, first)
    _consume(m5, second)
    waiting = _pending(sub)
    # replays while the first date's change waits: it is not superseded
    for event in (first, second, first):
        out = _consume(m5, event)
        assert out["created"] is False
    assert _pending(sub) == waiting and waiting.new_amount == 15000.0
    _decide(waiting)
    _decide(_pending(sub))
    before = _all_prorations(sub)
    for event in (first, second):
        assert _consume(m5, event)["created"] is False
    assert _all_prorations(sub) == before and not _pending(sub)
    assert sub.recurring_amount == 17500.0


def test_reductions_are_credited_each_from_its_own_date(m5):
    sub = _cycle(m5)
    price = _amend(m5, 10, per_device_monthly="2000")  # 4 x 2,000: -2,000
    devices = _amend(m5, 4, device_count="3")  # 3 x 2,000: -2,000
    _consume(m5, devices)
    _consume(m5, price)
    pro1 = _pending(sub)
    assert (pro1.old_amount, pro1.new_amount, pro1.change_type) == (10000.0, 8000.0, "downgrade")
    assert pro1.amount == round(-2000.0 * 20 / 30, 2)
    _decide(pro1)
    pro2 = _pending(sub)
    assert (pro2.old_amount, pro2.new_amount) == (8000.0, 6000.0)
    assert pro2.amount == round(-2000.0 * 14 / 30, 2)
    _decide(pro2)
    assert sub.recurring_amount == 6000.0


def test_an_amendment_dated_before_the_waiting_change_supersedes_it(m5):
    sub = _cycle(m5)
    _consume(m5, _amend(m5, 4, device_count="6"))  # +5,000 from 4 days ago
    waiting = _pending(sub)
    assert waiting.new_amount == 15000.0
    # an earlier-dated amendment arrives: the earliest date is now 10 days ago
    out = _consume(m5, _amend(m5, 10, device_count="7"))
    assert out["created"] and waiting.state == "void"
    pro1 = _pending(sub)
    assert pro1.effective_date == fields.Date.today() - timedelta(days=10)
    assert (pro1.old_amount, pro1.new_amount) == (10000.0, 12500.0)
    late = _rows(m5).filtered(lambda r: r.effective_date == waiting.effective_date)
    assert late.billing_state == "pending" and not late.billing_ref
    _decide(pro1)
    pro2 = _pending(sub)
    assert (pro2.old_amount, pro2.new_amount) == (12500.0, 17500.0)
    _decide(pro2)
    assert set(_rows(m5).mapped("billing_state")) == {"billed"}


def test_a_rejected_change_lets_the_next_date_bill_from_the_unchanged_price(m5):
    sub = _cycle(m5)
    _consume(m5, _amend(m5, 10, device_count="6"))
    _consume(m5, _amend(m5, 4, device_count="7"))
    pro1 = _pending(sub)
    pro1.sudo()._approval_on_rejected("client disputes the first uplift")
    assert pro1.state == "void"
    early, late = _rows(m5)
    assert early.billing_state == "flagged"
    pro2 = _pending(sub)
    assert (pro2.old_amount, pro2.new_amount) == (10000.0, 12500.0)
    assert late.billing_state == "requested"
