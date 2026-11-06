"""A04 §6 C7 (2026-11-04): the money events reach finance (probe K13 closed).

working/A04_Workflow_and_Approval_Report.md: commission.earned (a
commissioned marketplace order M12, a commissioned referral M40) and
partner.rebate_approved were published and consumed by nobody - the M53
ledger row and the payout existed only if finance noticed by hand.

The source events are produced by the real transitions (each source module's
own A04 suite proves the role gates; that is not re-proved here), then
delivered the way production delivers them: ``cron_relay()`` as the
superuser with this module's consumers isolated on. Each leg shows the
legitimate document, the replay idempotent, the forged event refused and a
non-relay caller refused. ``odoo_env`` rolls back after each test.
"""

import itertools
import types
from datetime import timedelta

import pytest
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
A04_EVENTS = ("commission.earned", "partner.rebate_approved")
PA = "cd_partner.group_fix_channel_"
TIER = "cd_entity_config.group_dofa_tier_%d"
OPERATOR = "cd_marketplace.group_marketplace_operator"
_SEQ = itertools.count(1)


def _mk(env, login, *xmlids):
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": "a4c7.%s.%d@a04.test" % (login, next(_SEQ)),
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(x).id for x in xmlids])
                ],
            }
        )
    )


@pytest.fixture
def w(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.plain = _mk(env, "plain")
    x.operator = _mk(env, "marketplace_operator", OPERATOR)
    x.officer = _mk(env, "channel_officer", PA + "officer")
    x.manager = _mk(env, "channel_manager", PA + "manager")
    x.approver = _mk(env, "rebate_approver", "cd_partner.group_fix_rebate_approver", TIER % 2)
    return x


def _relay(env):
    """Deliver this suite's events through the production relay, with only
    THIS suite's consumer active (the A08 B4 build adds its own
    fix.commission.ledger consumer for the same events — it is deactivated
    here so the A04 consumer's exclusivity assertions still measure this
    consumer alone)."""
    Consumer = env["fix.event.consumer"].sudo()
    mine = Consumer.search(
        [("event_type", "in", A04_EVENTS), ("model", "=", "fix.a04.finance.consumers")]
    )
    assert set(mine.mapped("model")) == {"fix.a04.finance.consumers"}
    (Consumer.search([]) - mine).write({"active": False})
    mine.write({"active": True, "active_from": env.cr.now() - timedelta(minutes=1)})
    env["fix.event.outbox"].cron_relay()
    env.invalidate_all()


def _deliveries(env, event_type, aggregate_id):
    events = (
        env["fix.event.outbox"]
        .sudo()
        .search([("event_type", "=", event_type), ("aggregate_id", "=", aggregate_id)])
    )
    return env["fix.event.consumer.delivery"].sudo().search([("event_id", "in", events.ids)])


def _event_dict(env, event_type, aggregate_id):
    row = (
        env["fix.event.outbox"]
        .sudo()
        .search(
            [("event_type", "=", event_type), ("aggregate_id", "=", aggregate_id)],
            order="id desc",
            limit=1,
        )
    )
    assert row, "the source transition never published %s for #%s" % (event_type, aggregate_id)
    return row._relay_event_dict()


def _attempt(env, fn):
    try:
        with env.cr.savepoint():
            fn()
    except REFUSED as exc:
        return str(exc) or type(exc).__name__
    return None


def _commissioned_order(w):
    """A marketplace order carried to 'commissioned' through M12's own chain."""
    env = w.env
    env["ir.config_parameter"].sudo().set_param("cd_marketplace.platform_commission_rate", "0.10")
    customer = env["res.partner"].create({"name": "A4 C7 Customer"})
    partner = env["res.partner"].create({"name": "A4 C7 Seller Co"})
    seller = env["fix.marketplace.seller"].create(
        {"name": "A4 C7 Seller", "partner_id": partner.id}
    )
    seller.write({"kyc_status": "verified", "cfo_approved": True})  # seed-style, superuser
    order = (
        env["fix.marketplace.order"]
        .with_user(w.operator)
        .create({"customer_id": customer.id, "description": "Cracked screen"})
    )
    quote = env["fix.seller.quote"].create(
        {"marketplace_order_id": order.id, "seller_id": seller.id, "quoted_price": 8000.0}
    )
    quote.with_user(w.operator).action_select()
    as_op = order.with_user(w.operator)
    as_op.action_start_job()
    as_op.action_complete()
    as_op.action_review(rating=5)
    as_op.action_earn_commission()
    order.invalidate_recordset()
    assert order.state == "commissioned"
    return order


def _commissioned_referral(w):
    """A referral carried to 'commissioned' (M40's in-house chain)."""
    env = w.env
    party = env["res.partner"].create({"name": "A4 C7 Channel Partner"})
    partner = env["fix.partner"].create(
        {
            "name": "A4 C7 Partner",
            "partner_id": party.id,
            "partner_type": "reseller",
            "tin_number": "123456789012",
            "trade_license_no": "TL-C7",
            "commission_rate": 0.05,
        }
    )
    partner.with_user(w.manager).action_onboard()
    ref = env["fix.referral"].create(
        {"name": "A4 C7 Referral", "partner_id": partner.id, "base_amount": 40000.0}
    )
    ref.action_convert()
    ref.action_earn_commission()
    ref.invalidate_recordset()
    assert ref.state == "commissioned" and ref.commission_amount > 0
    return ref


def _approved_rebate(w):
    """An approved rebate: the officer's request, decided from the inbox."""
    env = w.env
    party = env["res.partner"].create({"name": "A4 C7 Rebate Co"})
    partner = env["fix.partner"].create(
        {
            "name": "A4 C7 Rebate Partner",
            "partner_id": party.id,
            "partner_type": "reseller",
            "tin_number": "123456789013",
            "trade_license_no": "TL-C7R",
        }
    )
    partner.with_user(w.manager).action_onboard()
    audit = (
        env["fix.partner.audit"]
        .with_user(w.officer)
        .create({"partner_id": partner.id, "score": 88.0})
    )
    doc = (
        env["ir.attachment"]
        .with_user(w.officer)
        .create(
            {
                "name": "audit.pdf",
                "res_model": audit._name,
                "res_id": audit.id,
                "datas": "QVAtNCBhdWRpdA==",
            }
        )
    )
    audit.with_user(w.officer).write({"evidence_attachment_id": doc.id})
    audit.with_user(w.officer).action_submit()
    audit.with_user(w.manager).action_approve()
    rebate = (
        env["fix.partner.rebate"]
        .with_user(w.officer)
        .create(
            {
                "name": "A4 C7 rebate",
                "partner_id": partner.id,
                "period": "2026-Q4",
                "basis": 100000.0,
                "rate": 0.03,
            }
        )
    )
    rebate.with_user(w.officer).action_accrue()
    rebate.with_user(w.officer).action_request_approval(justification="Q4 volume met")
    approve_via_inbox(rebate, w.approver, requester=w.officer, justification="Q4 volume met")
    rebate.invalidate_recordset()
    assert (rebate.state, rebate.amount) == ("approved", 3000.0)
    return rebate


# ---------------------------------------------------------------- wiring


def test_the_consumer_rows_are_wired(w):
    rows = w.env["fix.event.consumer"].sudo().search([("event_type", "in", A04_EVENTS)])
    ours = rows.filtered(lambda r: r.model == "fix.a04.finance.consumers")
    by_type = {r.event_type: r for r in ours}
    assert set(by_type) == set(A04_EVENTS)
    for row in by_type.values():
        assert row.method.startswith("consume_")
        assert row.module == "cd_settlement_ext"
    # the A08 B4 build registers its own commission.earned consumer (the
    # ledger writer on fix.commission.ledger); both coexist, each delivering
    # the event once to its own model


# ---------------------------------------------------------------- commission.earned


def test_a_commissioned_marketplace_order_lands_in_the_m53_ledger(w):
    order = _commissioned_order(w)
    _relay(w.env)
    Ledger = w.env["fix.commission.ledger"].sudo()
    (row,) = Ledger.search([("source_ref", "=", "fix.marketplace.order/%s" % order.id)])
    assert (row.source_type, row.gross_amount, row.commission_rate) == ("marketplace", 8000.0, 0.10)
    assert row.seller_partner_id == order.selected_quote_id.seller_id.partner_id
    assert row.company_id == order.company_id
    (delivery,) = _deliveries(w.env, "commission.earned", order.id)
    assert delivery.state == "done"
    # a replay raises nothing more
    result = w.env["fix.a04.finance.consumers"].consume_commission_earned(
        _event_dict(w.env, "commission.earned", order.id)
    )
    assert result == {"model": "fix.commission.ledger", "id": row.id, "created": False}
    assert len(Ledger.search([("source_ref", "=", "fix.marketplace.order/%s" % order.id)])) == 1


def test_a_commissioned_referral_lands_in_the_m53_ledger(w):
    ref = _commissioned_referral(w)
    _relay(w.env)
    Ledger = w.env["fix.commission.ledger"].sudo()
    (row,) = Ledger.search([("source_ref", "=", "fix.referral/%s" % ref.id)])
    assert row.source_type == "partner_referral" and row.referral_id == ref
    assert (row.gross_amount, row.commission_rate) == (40000.0, 0.05)
    assert row.seller_partner_id == ref.partner_id.partner_id
    result = w.env["fix.a04.finance.consumers"].consume_commission_earned(
        _event_dict(w.env, "commission.earned", ref.id)
    )
    assert result == {"model": "fix.commission.ledger", "id": row.id, "created": False}


# ---------------------------------------------------------------- partner.rebate_approved


def test_an_approved_rebate_raises_its_pending_payout(w):
    rebate = _approved_rebate(w)
    _relay(w.env)
    Execution = w.env["fix.payment.execution"].sudo()
    (pay,) = Execution.search(
        [("source_model", "=", "fix.partner.rebate"), ("source_id", "=", rebate.id)]
    )
    assert (pay.state, pay.amount) == ("pending", 3000.0)
    assert pay.partner_id == rebate.partner_id.partner_id
    result = w.env["fix.a04.finance.consumers"].consume_partner_rebate_approved(
        _event_dict(w.env, "partner.rebate_approved", rebate.id)
    )
    assert result == {"model": "fix.payment.execution", "id": pay.id, "created": True}
    assert (
        len(
            Execution.search(
                [("source_model", "=", "fix.partner.rebate"), ("source_id", "=", rebate.id)]
            )
        )
        == 1
    )


# ---------------------------------------------------------------- forgery and access


def test_a_forged_amount_is_refused_and_dead_letters(w):
    order = _commissioned_order(w)
    event = _event_dict(w.env, "commission.earned", order.id)
    forged = dict(event, payload=dict(event["payload"], commission=999999.0))
    assert "999999" in _attempt(
        w.env, lambda: w.env["fix.a04.finance.consumers"].consume_commission_earned(forged)
    )
    assert (
        not w.env["fix.commission.ledger"]
        .sudo()
        .search([("source_ref", "=", "fix.marketplace.order/%s" % order.id)])
    )


def test_an_unknown_aggregate_and_a_wrong_state_are_refused(w):
    event = _event_dict(w.env, "commission.earned", _commissioned_order(w).id)
    err = _attempt(
        w.env,
        lambda: w.env["fix.a04.finance.consumers"].consume_commission_earned(
            dict(event, aggregate="fix.nonsense.model")
        ),
    )
    assert "aggregate" in err
    # a submitted (not commissioned) referral is not money yet
    partner = w.env["fix.partner"].create(
        {
            "name": "A4 C7 Early Partner",
            "partner_id": w.env["res.partner"].create({"name": "A4 C7 Early Co"}).id,
            "partner_type": "reseller",
            "commission_rate": 0.05,
        }
    )
    ref = w.env["fix.referral"].create(
        {"name": "A4 C7 early", "partner_id": partner.id, "base_amount": 100.0}
    )
    err = _attempt(
        w.env,
        lambda: w.env["fix.a04.finance.consumers"].consume_commission_earned(
            dict(event, aggregate="fix.referral", aggregate_id=ref.id)
        ),
    )
    assert "commissioned" in err


def test_only_the_relay_may_run_the_consumers(w):
    order = _commissioned_order(w)
    event = _event_dict(w.env, "commission.earned", order.id)
    consumers = w.env["fix.a04.finance.consumers"].with_user(w.plain)
    with pytest.raises(AccessError, match="event relay"):
        consumers.consume_commission_earned(event)
    with pytest.raises(AccessError, match="event relay"):
        consumers.consume_partner_rebate_approved(event)
