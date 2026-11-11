"""A02 audit P1 (B2): the money hand-backs reach finance.

working/A02_Workflow_and_Approval_Report.md: a cancelled paid order
(service_order.refund_requested), a settled damage claim
(damage.claim.settled) and an applied MSP SLA credit (msp.sla_credit_applied)
were published and consumed by nobody, so no refund, payable, recovery or
credit note was ever raised.

The source events are produced by the real transitions, acted by NON-ADMIN
users holding only their role groups. The consumers run the way production
runs them: `cron_relay()` delivers the outbox, as the superuser, with this
module's subscriptions starting just before the test transaction. Each test
shows the legitimate path, a forged event refused, the replay idempotent and
the finance-side bypasses refused. ``odoo_env`` rolls back after each test.
"""

import itertools
import json
import types
from datetime import timedelta

import pytest
from odoo import Command, fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

REFUSED = (UserError, ValidationError, AccessError)
HANDBACK_EVENTS = (
    "service_order.refund_requested",
    "damage.claim.settled",
    "msp.sla_credit_applied",
)
ACCOUNTANT = "account.group_account_user"
_SEQ = itertools.count(1)


# --------------------------------------------------------------------------- helpers
def _user(env, key, *groups):
    n = next(_SEQ)
    ous = env["operating.unit"].search([("company_id", "=", env.company.id)])
    ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A02 HB %s %d" % (key, n),
                "login": "a02.hb.%s.%d@a02.test" % (key, n),
                "group_ids": [(6, 0, ids)],
                "company_id": env.company.id,
                "company_ids": [(6, 0, env.company.ids)],
                "operating_unit_ids": [(6, 0, ous.ids)],
                "default_operating_unit_id": ous[:1].id,
            }
        )
    )


def _branch(env):
    """A branch with an operating unit: fix_test's own, else one made here."""
    branch = env["fix.branch"].search([("operating_unit_id", "!=", False)], limit=1)
    if branch:
        return branch
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    entity = env["fix.entity"].search([], limit=1) or env["fix.entity"].create(
        {"legal_name": "A02 HB Entity", "code": "A2HBE", "company_id": env.company.id}
    )
    return env["fix.branch"].create(
        {
            "name": "A02 HB Branch",
            "code": "A2HB-BR",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )


def _relay(env):
    """Deliver this test's hand-back events through the production relay."""
    Consumer = env["fix.event.consumer"].sudo()
    mine = Consumer.search([("event_type", "in", HANDBACK_EVENTS)])
    assert len(mine) == 3 and set(mine.mapped("model")) == {"fix.finance.handback"}
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


def _attempt(env, fn):
    try:
        with env.cr.savepoint():
            fn()
    except REFUSED as exc:
        return str(exc) or type(exc).__name__
    return None


def _account(env, code):
    return env["account.account"].search(
        [("code", "=", code), ("company_ids", "in", env.company.id)], limit=1
    )


def _notes(record, marker):
    return (
        record.env["mail.message"]
        .sudo()
        .search_count(
            [("model", "=", record._name), ("res_id", "=", record.id), ("body", "ilike", marker)]
        )
    )


def _executions(env, record):
    return (
        env["fix.payment.execution"]
        .sudo()
        .search([("source_model", "=", record._name), ("source_id", "=", record.id)])
    )


def _credit_notes(env, record):
    return (
        env["fix.credit.note"]
        .sudo()
        .search([("source_model", "=", record._name), ("source_id", "=", record.id)])
    )


# =========================================================================== M01 refund
@pytest.fixture
def so(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.clerk = _user(env, "clerk")
    x.clerk2 = _user(env, "clerk2")  # approves what the clerk prepared
    x.cashier = _user(env, "cashier", "cd_service_order.group_so_cashier")
    # M04, when installed (this module does not depend on it): the Front Desk
    # Cashier who opens the branch's cash drawer
    x.drawer_cashier = (
        _user(env, "drawer", "cd_front_desk.group_fd_cashier") if "fix.cash.shift" in env else None
    )
    x.accountant = _user(env, "acct", ACCOUNTANT)
    x.branch = _branch(env)
    x.customer = env["res.partner"].create({"name": "A02 HB Customer", "phone": "01711000444"})
    brand = env["fix.brand"].create({"name": "A02HBBrand", "code": "A2HB"})
    x.model = env["fix.device.model"].create({"name": "A02HB Model", "brand_id": brand.id})
    return x


def _open_drawer(so):
    """The branch's open cash shift (M04): counter cash is refused without one.
    Opened the way the counter opens it, by a Front Desk Cashier on a float.
    None when cd_front_desk is not installed and the order takes the cash alone."""
    if so.drawer_cashier is None:
        return None
    Shift = so.env["fix.cash.shift"]
    shift = Shift._fd_open_shift_for(so.branch)
    if not shift:
        operator = so.env["hr.employee"].create(
            {"name": "A02 HB Drawer Cashier", "user_id": so.drawer_cashier.id}
        )
        shift = Shift.with_user(so.drawer_cashier).create(
            {
                "branch_id": so.branch.id,
                "operating_unit_id": so.branch.operating_unit_id.id,
                "operator_id": operator.id,
                "opening_float": 1000.0,
            }
        )
    return shift


def _paid_order(so, amount=3000.0, settle=3450.0):
    """An order with an approved estimate, settled at the counter."""
    n = next(_SEQ)
    dev = so.env["fix.device"].create(
        {"device_model_id": so.model.id, "owner_id": so.customer.id, "serial_number": "A2HB-%d" % n}
    )
    o = (
        so.env["fix.service.order"]
        .with_user(so.clerk)
        .create(
            {
                "device_id": dev.id,
                "customer_id": so.customer.id,
                "branch_id": so.branch.id,
                "service_type": "walk_in",
                "order_category": "standard",
                "fault_description": "A02 hand-back fault",
            }
        )
    )
    o.action_intake()
    o.action_start_diagnostic()
    o.action_request_estimate()
    est = (
        so.env["fix.estimate"]
        .with_user(so.clerk)
        .create(
            {
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
        )
    )
    est.action_send()
    # not its preparer (segregation of duties): at this amount no customer
    # code is asked, so a second member of staff records the approval
    est.with_user(so.clerk2).action_approve()
    shift = _open_drawer(so)
    taken = shift.cash_payments if shift else 0.0
    o.with_user(so.cashier).action_mark_settled("POS-HB-%d" % n, settle)
    assert o.payment_settlement_state == "settled" and o.amount_settled_bdt == settle
    if shift:  # the counter cash is in the drawer, not only on the order
        assert o.counter_shift_id == shift and shift.cash_payments == taken + settle
    return o


def _invoice(env, o, total):
    """An issued M20 invoice of the order (fixture written by the superuser)."""
    return env["fix.ar.invoice"].create(
        {
            "operating_unit_id": o.branch_id.operating_unit_id.id,
            "branch_id": o.branch_id.id,
            "customer_id": o.customer_id.id,
            "source_model": "fix.service.order",
            "source_id": o.id,
            "state": "issued",
            "name": "INV/A02HB/%d" % o.id,
            "line_ids": [
                Command.create(
                    {
                        "description": "repair",
                        "taxable_amount": round(total / 1.15, 2),
                        "vat_amount": round(total - total / 1.15, 2),
                        "line_total": total,
                    }
                )
            ],
        }
    )


def test_a_cancelled_paid_order_raises_a_pending_treasury_refund(so):
    o = _paid_order(so)
    o.with_user(so.clerk).action_cancel(reason_code="customer_declined")
    assert o.payment_settlement_state == "refund_due"
    assert not _executions(so.env, o)  # the cancel itself pays nothing
    _relay(so.env)
    (pay,) = _executions(so.env, o)
    assert (pay.state, pay.amount, pay.partner_id, pay.method) == (
        "pending",
        3450.0,
        so.customer,
        "cash",  # settled at the counter: refunded at the counter
    )
    # the customer's money sits on AR control (M20's role), so the refund clears it
    assert pay.debit_account_id == _account(so.env, "121000")
    assert not _credit_notes(so.env, o)  # no invoice: nothing to credit
    assert _notes(o, "Finance hand-back (refund):") == 1
    (delivery,) = _deliveries(so.env, "service_order.refund_requested", o.id)
    assert delivery.state == "done"

    # a replay of the event raises nothing more
    event = so.env["fix.event.outbox"].search(
        [("event_type", "=", "service_order.refund_requested"), ("aggregate_id", "=", o.id)]
    )
    result = so.env["fix.finance.handback"].consume_service_order_refund_requested(
        event._relay_event_dict()
    )
    assert result == {"model": "fix.payment.execution", "id": pay.id, "created": False}
    assert len(_executions(so.env, o)) == 1 and _notes(o, "Finance hand-back (refund):") == 1


def test_a_refund_instruction_is_pinned_to_its_source(so):
    o = _paid_order(so)
    o.with_user(so.clerk).action_cancel(reason_code="customer_declined")
    _relay(so.env)
    (pay,) = _executions(so.env, o)
    acct = so.accountant
    # the payee, the source and the amount ceiling are the relay's
    assert "event relay" in _attempt(
        so.env, lambda: pay.with_user(acct).write({"payee": "Mallory"})
    )
    thief = so.env["res.partner"].create({"name": "A02 HB Mallory"})
    err = _attempt(so.env, lambda: pay.with_user(acct).write({"partner_id": thief.id}))
    assert "event relay" in err
    err = _attempt(so.env, lambda: pay.with_user(acct).write({"amount": 99999.0}))
    assert "cannot exceed" in err
    # the money goes to the payee's own account only
    bank = so.env["res.partner.bank"].create({"acc_number": "A2HB-THIEF-1", "partner_id": thief.id})
    err = _attempt(so.env, lambda: pay.with_user(acct).write({"partner_bank_id": bank.id}))
    # (M50's own payee-account check, B1, may answer first: either way refused)
    assert "payee's own" in err or "belongs to" in err
    own = so.env["res.partner.bank"].create(
        {"acc_number": "A2HB-OWN-1", "partner_id": so.customer.id}
    )
    pay.with_user(acct).write({"partner_bank_id": own.id, "amount": 3000.0})
    assert pay.partner_bank_id == own and pay.amount == 3000.0
    # a plain user (who may request payments) cannot squat a refund key
    other = _paid_order(so)
    err = _attempt(
        so.env,
        lambda: so.env["fix.payment.execution"]
        .with_user(so.clerk)
        .create(
            {
                "source_model": "fix.service.order",
                "source_id": other.id,
                "payee": "Mallory",
                "amount": 1.0,
                "operating_unit_id": pay.operating_unit_id.id,
            }
        ),
    )
    assert "event relay" in err


def test_a_refund_with_an_invoice_raises_a_draft_credit_note(so):
    o = _paid_order(so)
    invoice = _invoice(so.env, o, 3000.0)
    o.with_user(so.clerk).action_cancel(reason_code="customer_declined")
    _relay(so.env)
    (note,) = _credit_notes(so.env, o)
    # the invoice can credit 3,000 of the 3,450 settled
    assert (note.state, note.invoice_id, note.amount, note.reason_code, note.customer_id) == (
        "draft",
        invoice,
        3000.0,
        "order_cancelled",
        so.customer,
    )
    assert note.source_amount == 3000.0 and note.source_event_id
    assert not _executions(so.env, o)
    acct = so.accountant
    err = _attempt(so.env, lambda: note.with_user(acct).write({"amount": 3001.0}))
    assert "cannot exceed" in err
    err = _attempt(so.env, lambda: note.with_user(acct).write({"source_amount": 9e6}))
    assert "event relay" in err
    other = so.env["res.partner"].create({"name": "A02 HB Other Customer"})
    other_invoice = _invoice(so.env, _paid_order(so), 3000.0)
    other_invoice.customer_id = other
    err = _attempt(so.env, lambda: note.with_user(acct).write({"invoice_id": other_invoice.id}))
    assert "cannot credit an invoice of" in err
    note.with_user(acct).write({"amount": 2500.0})
    note.with_user(acct).action_submit()
    # A08 S3: submitting approves nothing; the submitter never approves it
    assert note.state == "pending_approval" and not note.approved_by
    assert "Segregation of duties" in _attempt(
        so.env, lambda: note.with_user(acct).action_approve()
    )


def test_a_forged_refund_event_is_refused(so):
    live = _paid_order(so)  # settled, not cancelled
    publish(
        so.env,
        "service_order.refund_requested",
        "fix.service.order",
        live.id,
        {"order_id": live.id, "amount_bdt": 3450.0},
    )
    cancelled = _paid_order(so)
    cancelled.with_user(so.clerk).action_cancel(reason_code="customer_declined")
    # a second event for the real refund, with an inflated amount
    publish(
        so.env,
        "service_order.refund_requested",
        "fix.service.order",
        cancelled.id,
        {"order_id": cancelled.id, "amount_bdt": 345000.0},
    )
    _relay(so.env)
    (forged,) = _deliveries(so.env, "service_order.refund_requested", live.id)
    assert forged.state == "failed" and "not a cancelled order" in forged.last_error
    assert not _executions(so.env, live) and not _credit_notes(so.env, live)
    deliveries = _deliveries(so.env, "service_order.refund_requested", cancelled.id)
    # the genuine event raised the refund at the record's amount; the inflated
    # copy is refused, even though a refund for the order already exists
    assert sorted(deliveries.mapped("state")) == ["done", "failed"]
    assert (
        "record says BDT 3450.00" in deliveries.filtered(lambda d: d.state == "failed").last_error
    )
    (pay,) = _executions(so.env, cancelled)
    assert pay.amount == 3450.0


def test_the_consumers_refuse_a_non_superuser(so):
    o = _paid_order(so)
    o.with_user(so.clerk).action_cancel(reason_code="customer_declined")
    event = (
        so.env["fix.event.outbox"]
        .search(
            [("event_type", "=", "service_order.refund_requested"), ("aggregate_id", "=", o.id)]
        )
        ._relay_event_dict()
    )
    Handback = so.env["fix.finance.handback"]
    for user in (so.accountant, so.clerk):
        for method in (
            "consume_service_order_refund_requested",
            "consume_damage_claim_settled",
            "consume_msp_sla_credit_applied",
        ):
            with pytest.raises(AccessError, match="only from the event relay"):
                getattr(Handback.with_user(user), method)(event)
    assert not _executions(so.env, o)
    # a hand-back credit note cannot be made by hand either
    invoice = _invoice(so.env, _paid_order(so), 1000.0)
    err = _attempt(
        so.env,
        lambda: so.env["fix.credit.note"]
        .with_user(so.accountant)
        .create(
            {
                "operating_unit_id": invoice.operating_unit_id.id,
                "invoice_id": invoice.id,
                "amount": 100.0,
                "reason_code": "order_cancelled",
                "source_model": "fix.service.order",
                "source_id": o.id,
            }
        ),
    )
    assert "event relay" in err


# =========================================================================== M03 damage claim
@pytest.fixture
def dc(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.branch = _branch(env)
    x.ou = x.branch.operating_unit_id
    x.clerk = _user(env, "dcclerk")
    x.manager = _user(env, "dcmgr", "cd_consignment.group_fix_logistics_manager")
    x.approver = _user(
        env,
        "dcappr",
        "cd_consignment.group_fix_damage_claim_approver",
        "cd_entity_config.group_dofa_tier_2",
        "cd_entity_config.group_dofa_tier_3",
        "cd_entity_config.group_dofa_tier_4",
    )
    x.accountant = _user(env, "dcacct", ACCOUNTANT)
    x.customer = env["res.partner"].create({"name": "A02 HB DC Customer", "phone": "01711000555"})
    brand = env["fix.brand"].create({"name": "A02HBDC", "code": "A2HBD"})
    model = env["fix.device.model"].create({"name": "A02HBDC Phone", "brand_id": brand.id})
    device = env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": x.customer.id, "serial_number": "A2HB-DC-1"}
    )
    x.order = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": x.customer.id,
            "branch_id": x.branch.id,
            "fault_description": "pick & drop",
            "service_type": "collection",
        }
    )
    x.courier = env["fix.courier.partner"].create({"name": "A02 HB Courier", "code": "A2HBCOUR"})
    # the courier's finance partner: a contact whose Reference is the code
    x.courier_partner = env["res.partner"].create(
        {"name": "A02 HB Courier Ltd", "ref": "A2HBCOUR", "is_company": True}
    )
    return x


def _settled_claim(dc, amount=3500.0, settle=None, **claim_vals):
    cons = dc.env["fix.consignment"].create(
        {
            "consignment_type": "delivery",
            "scheduled_date": fields.Datetime.now(),
            "operating_unit_id": dc.ou.id,
            "dest_branch_id": dc.branch.id,
            "service_order_id": dc.order.id,
            "courier_partner_id": dc.courier.id,
            "declared_value_bdt": 5000.0,
        }
    )
    cons.write({"state": "delivered"})  # setup by the superuser
    claim = (
        dc.env["fix.damage.claim"]
        .with_user(dc.clerk)
        .create(
            {
                "consignment_id": cons.id,
                "operating_unit_id": dc.ou.id,
                "description": "screen cracked in transit",
                "claimed_amount": amount,
                "dofa_justification": "Photos and the hub report agree.",
                **claim_vals,
            }
        )
    )
    approve_via_inbox(claim, dc.approver, requester=dc.clerk)  # M63 (A02 audit B1)
    claim.with_user(dc.manager).action_settle(settled_amount=settle or amount)
    assert claim.state == "settled"
    return claim


def test_a_settled_claim_raises_the_payout_and_the_courier_recovery(dc):
    dc.env["ir.config_parameter"].set_param(
        "cd_settlement_ext.account_code.damage_claim_expense", "600000"
    )
    claim = _settled_claim(dc, 4000.0, settle=3500.0, liability="carrier")
    _relay(dc.env)
    (pay,) = _executions(dc.env, claim)
    assert (pay.state, pay.amount, pay.partner_id, pay.payee) == (
        "pending",
        3500.0,  # the settled amount, not the claim
        dc.customer,
        dc.customer.name,
    )
    assert pay.debit_account_id == _account(dc.env, "600000")
    recovery = dc.env["fix.ar.invoice"].search(
        [("source_model", "=", "fix.damage.claim"), ("source_id", "=", claim.id)]
    )
    assert (recovery.state, recovery.customer_id, recovery.total_payable, recovery.vat_amount) == (
        "draft",
        dc.courier_partner,
        3500.0,
        0.0,
    )
    # issued, it credits recovery income (450000), not service revenue
    assert recovery._revenue_role() == "claim_recovery"
    assert _notes(claim, "Finance hand-back (damage claim):") == 1
    # replayed: nothing new
    event = (
        dc.env["fix.event.outbox"]
        .search([("event_type", "=", "damage.claim.settled"), ("aggregate_id", "=", claim.id)])
        ._relay_event_dict()
    )
    result = dc.env["fix.finance.handback"].consume_damage_claim_settled(event)
    assert result == {"payable": pay.id, "recovery": recovery.id}
    assert len(_executions(dc.env, claim)) == 1
    assert _notes(claim, "Finance hand-back (damage claim):") == 1
    # the payout cannot be raised above the settlement, nor squatted
    err = _attempt(dc.env, lambda: pay.with_user(dc.accountant).write({"amount": 4000.0}))
    assert "cannot exceed" in err
    err = _attempt(
        dc.env,
        lambda: dc.env["fix.ar.invoice"]
        .with_user(dc.accountant)
        .create(
            {
                "operating_unit_id": dc.ou.id,
                "customer_id": dc.courier_partner.id,
                "source_model": "fix.damage.claim",
                "source_id": claim.id + 1,
            }
        ),
    )
    assert "event relay" in err


def test_a_branch_claim_raises_no_payout_and_an_unknown_courier_no_recovery(dc):
    dc.courier_partner.ref = False  # the courier has no finance partner now
    claim = _settled_claim(dc, 2000.0, claimant="branch", liability="carrier")
    _relay(dc.env)
    assert not _executions(dc.env, claim)
    assert not dc.env["fix.ar.invoice"].search(
        [("source_model", "=", "fix.damage.claim"), ("source_id", "=", claim.id)]
    )
    body = (
        dc.env["mail.message"]
        .search(
            [
                ("model", "=", claim._name),
                ("res_id", "=", claim.id),
                ("body", "ilike", "Finance hand-back (damage claim):"),
            ]
        )
        .body
    )
    assert "claimant is the branch" in body and "no finance partner" in body
    (delivery,) = _deliveries(dc.env, "damage.claim.settled", claim.id)
    assert delivery.state == "done"


def test_a_forged_claim_event_is_refused(dc):
    cons = dc.env["fix.consignment"].create(
        {
            "consignment_type": "delivery",
            "scheduled_date": fields.Datetime.now(),
            "operating_unit_id": dc.ou.id,
            "service_order_id": dc.order.id,
        }
    )
    open_claim = (
        dc.env["fix.damage.claim"]
        .with_user(dc.clerk)
        .create(
            {
                "consignment_id": cons.id,
                "operating_unit_id": dc.ou.id,
                "description": "forged",
                "claimed_amount": 900000.0,
            }
        )
    )
    publish(
        dc.env,
        "damage.claim.settled",
        "fix.damage.claim",
        open_claim.id,
        {"claim": open_claim.name, "amount": 900000.0, "claimant": "customer"},
    )
    settled = _settled_claim(dc, 1000.0)
    # a forged copy for a settled claim that inflates the amount
    publish(
        dc.env,
        "damage.claim.settled",
        "fix.damage.claim",
        settled.id,
        {"claim": settled.name, "amount": 100000.0},
    )
    _relay(dc.env)
    (forged,) = _deliveries(dc.env, "damage.claim.settled", open_claim.id)
    assert forged.state == "failed" and "not settled" in forged.last_error
    assert not _executions(dc.env, open_claim)
    deliveries = _deliveries(dc.env, "damage.claim.settled", settled.id)
    assert sorted(deliveries.mapped("state")) == ["done", "failed"]
    assert (
        "record says BDT 1000.00" in deliveries.filtered(lambda d: d.state == "failed").last_error
    )
    (pay,) = _executions(dc.env, settled)
    assert pay.amount == 1000.0


# =========================================================================== M05 SLA credit
@pytest.fixture
def sla(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    x.eng = _user(env, "eng", "cd_msp_contract.group_msp_engineer")
    x.fin = _user(env, "fin", "cd_msp_contract.group_msp_credit_approver")
    x.accountant = _user(env, "slaacct", ACCOUNTANT)
    n = next(_SEQ)
    x.customer = env["res.partner"].create(
        {"name": "A02 HB MSP Client %d" % n, "is_company": True, "phone": "01711000666"}
    )
    x.contract = env["fix.contract"].create(
        {
            "name": "A02 HB MSP Contract %d" % n,
            "customer_id": x.customer.id,
            "family": "managed",
            "operating_unit_id": x.ou.id,
            "date_start": fields.Date.today(),
            "date_end": fields.Date.today() + timedelta(days=365),
            "annual_value": 240000.0,
        }
    )
    # the M08 term is in force (a draft term owes no credit, A02 audit M05-P2)
    x.contract.write({"state": "active"})  # setup by the superuser
    x.msp = env["fix.msp.contract"].create(
        {
            "name": "A02 HB MSP %d" % n,
            "contract_id": x.contract.id,
            "operating_unit_id": x.ou.id,
            "device_count": 4,
            "per_device_monthly": 2500.0,
            "sla_target_pct": 95.0,
        }
    )
    return x


def _applied_credit(sla, period):
    """A computed credit (45% shortfall of 4 x 2,500), approved and applied
    by the finance approver."""
    sla.env["fix.msp.service.report"].create(
        {
            "msp_contract_id": sla.msp.id,
            "period_label": period,
            "alert_count": 10,
            "resolved_count": 5,
            "sla_attainment": 0.5,
            "operating_unit_id": sla.ou.id,
        }
    )
    sla.msp.with_user(sla.eng).action_compute_sla_credits()
    credit = sla.env["fix.msp.sla.credit"].search(
        [("msp_contract_id", "=", sla.msp.id), ("period_label", "=", period)]
    )
    # A02 audit B1: decided from the approver's inbox (M63), not directly
    approve_via_inbox(credit, sla.fin, requester=sla.eng)
    credit.with_user(sla.fin).action_apply()
    assert credit.state == "applied" and credit.approved_amount == 4500.0
    return credit


def test_an_applied_sla_credit_raises_a_draft_credit_note(sla):
    credit = _applied_credit(sla, "2026-09")
    _relay(sla.env)
    (note,) = _credit_notes(sla.env, credit)
    assert (note.state, note.amount, note.reason_code, note.customer_id, note.invoice_id) == (
        "draft",
        4500.0,
        "sla_credit",
        sla.customer,
        sla.env["fix.ar.invoice"],  # the contract has no invoice yet
    )
    assert _notes(credit, "Finance hand-back (SLA credit):") == 1
    acct = sla.accountant
    # it waits for the invoice it credits, and its amount is pinned
    err = _attempt(sla.env, lambda: note.with_user(acct).action_submit())
    assert "link the invoice" in err
    err = _attempt(sla.env, lambda: note.with_user(acct).write({"amount": 45000.0}))
    assert "cannot exceed" in err
    err = _attempt(sla.env, lambda: note.with_user(acct).write({"customer_id": acct.partner_id.id}))
    assert "event relay" in err
    # finance links the customer's invoice, and the note goes on its way
    invoice = sla.env["fix.ar.invoice"].create(
        {
            "operating_unit_id": sla.ou.id,
            "customer_id": sla.customer.id,
            "source_model": "manual",
            "source_id": -987654,
            "state": "issued",
            "name": "INV/A02HB/SLA",
            "line_ids": [
                Command.create(
                    {"description": "MSP", "taxable_amount": 10000.0, "line_total": 10000.0}
                )
            ],
        }
    )
    note.with_user(acct).write({"invoice_id": invoice.id})
    note.with_user(acct).action_submit()
    # A08 S3: submitting approves nothing (the old auto-approval was the defect)
    assert note.state == "pending_approval" and not note.approved_by
    # a replay returns the same note
    event = (
        sla.env["fix.event.outbox"]
        .search([("event_type", "=", "msp.sla_credit_applied"), ("aggregate_id", "=", credit.id)])
        ._relay_event_dict()
    )
    result = sla.env["fix.finance.handback"].consume_msp_sla_credit_applied(event)
    assert result == {"model": "fix.credit.note", "id": note.id, "created": False}


def test_an_sla_credit_goes_against_the_contract_invoice(sla):
    if "fix.subscription.charge" not in sla.env:
        pytest.skip("cd_subscription not installed")
    sub = sla.env["fix.subscription"].create(
        {
            "name": "A02 HB MSP billing",
            "operating_unit_id": sla.ou.id,
            "customer_id": sla.customer.id,
            "contract_id": sla.contract.id,
            "recurring_amount": 10000.0,
        }
    )
    invoice = sla.env["fix.ar.invoice"].create(
        {
            "operating_unit_id": sla.ou.id,
            "customer_id": sla.customer.id,
            "source_model": "fix.subscription.charge",
            "source_id": -987655,
            "state": "issued",
            "name": "INV/A02HB/MSP",
            "line_ids": [
                Command.create(
                    {"description": "MSP", "taxable_amount": 10000.0, "line_total": 10000.0}
                )
            ],
        }
    )
    sla.env["fix.subscription.charge"].create(
        {
            "operating_unit_id": sla.ou.id,
            "subscription_id": sub.id,
            "period_start": fields.Date.today().replace(day=1),
            "period_end": fields.Date.today(),
            "amount": 10000.0,
            "invoice_id": invoice.id,
        }
    )
    credit = _applied_credit(sla, "2026-08")
    _relay(sla.env)
    (note,) = _credit_notes(sla.env, credit)
    assert note.invoice_id == invoice and note.amount == 4500.0 and note.state == "draft"


def test_a_forged_sla_event_is_refused(sla):
    draft = (
        sla.env["fix.msp.sla.credit"]
        .with_user(sla.eng)
        .create(
            {"msp_contract_id": sla.msp.id, "period_label": "A02-HB-draft", "manual_amount": 500.0}
        )
    )
    publish(
        sla.env,
        "msp.sla_credit_applied",
        "fix.msp.sla.credit",
        draft.id,
        {"contract": sla.msp.name, "period": "A02-HB-draft"},
    )
    _relay(sla.env)
    (forged,) = _deliveries(sla.env, "msp.sla_credit_applied", draft.id)
    assert forged.state == "failed" and "not applied" in forged.last_error
    assert not _credit_notes(sla.env, draft)
    # an applied credit whose event inflates the amount is refused as well
    credit = _applied_credit(sla, "2026-07")
    publish(
        sla.env,
        "msp.sla_credit_applied",
        "fix.msp.sla.credit",
        credit.id,
        {"contract": sla.msp.name, "period": "2026-07", "amount": 450000.0},
    )
    _relay(sla.env)
    deliveries = _deliveries(sla.env, "msp.sla_credit_applied", credit.id)
    assert sorted(deliveries.mapped("state")) == ["done", "failed"]
    failed = deliveries.filtered(lambda d: d.state == "failed")
    assert "record says BDT 4500.00" in failed.last_error
    assert json.loads(failed.event_id.payload)["amount"] == 450000.0
    (note,) = _credit_notes(sla.env, credit)
    assert note.amount == 4500.0
