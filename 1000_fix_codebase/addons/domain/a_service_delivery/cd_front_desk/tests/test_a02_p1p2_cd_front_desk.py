"""A02 audit P1/P2 for M04 Branch & Front-Desk (cd_front_desk).

B1: the cash variance, counter refund and price below list are routed M63
    approvals: a direct press is refused, the approver's inbox works, and the
    segregation of duties and the amount pins still hold.
B2: the M04 events are published by literal publish() calls.
P2: token recall / no-show and queue roles; counter-sale tender, VAT split and
    Mushak-6.3 number; M01 counter cash and diagnostic fees in the drawer; a
    waived fee needs approval; the device is required at intake.

Non-admin users created in the test act throughout (the fixture is the P0
suite's); ``odoo_env`` rolls back after every test.
"""

# ruff: noqa: F811  (the P0 suite's fixtures are imported and used as parameters)
import pytest
from odoo.addons.cd_front_desk.tests.test_a02_p0_m04 import (  # noqa: F401
    GUARD,
    _refused,
    call,
    m04,
)
from odoo.addons.cd_workflow_engine.tests.approval_helpers import (
    approve_via_inbox,
    assigned,
    inbox_task,
)
from odoo.exceptions import UserError

ROUTED = "approver's inbox"


def _user(m, login, *groups):
    vals = {
        "name": login,
        "login": "a02.p1.m04.%s.%d@p1.test" % (login, m.branch.id),
        "group_ids": [
            (6, 0, [m.env.ref("base.group_user").id] + [m.env.ref(g).id for g in groups])
        ],
        "operating_unit_ids": [(6, 0, m.ou.ids)],
    }
    user = m.env["res.users"].with_context(no_reset_password=True).create(vals)
    m.env["hr.employee"].create({"name": login, "user_id": user.id})
    return user


def _outbox(env, etype, model, rec_id):
    return env["fix.event.outbox"].search(
        [("event_type", "=", etype), ("aggregate", "=", model), ("aggregate_id", "=", rec_id)]
    )


# ============================================================ B1 routing
def test_every_m04_approval_refuses_a_direct_press(m04):
    """Even the competent manager cannot press Approve on the record."""
    m = m04
    s = m.shift()
    m.count(s, d1000=4)  # -1,000
    with _refused(m.env, UserError, ROUTED):
        m.as_(m.manager, s).action_approve_variance()
    cheap = m.sale(s, price=500.0)
    with _refused(m.env, UserError, ROUTED):
        m.as_(m.manager, cheap).action_approve_price_override()
    it = m.intake(device_id=m.device.id, payment_channel="waived", diagnostic_fee_bdt=300.0)
    with _refused(m.env, UserError, ROUTED):
        m.as_(m.manager, it).action_approve_fee_waiver()
    assert not s.sudo().supervisor_variance_approved_by
    assert not cheap.sudo().price_override_approved_by
    assert not it.sudo().fee_waiver_approved_by_id


def test_variance_is_requested_in_the_workspace_and_approved_in_the_inbox(m04, call):
    m = m04
    s = m.shift()
    m.count(s, d1000=4)  # -1,000
    res = call(
        m.env(user=m.cashier.id),
        "model_action",
        model="fix.cash.shift",
        ids=[s.id],
        method="action_request_approval",
        kwargs={"justification": "Change given twice to one customer"},
    )
    assert res["success"], res
    s.invalidate_recordset()
    assert s.approval_state == "pending" and m.manager in assigned(s)
    assert not assigned(s) & (m.cashier | m.cashier2 | m.approver)
    # the cashier (requester and handler) holds no task; a cashier cannot decide
    assert not inbox_task(s, m.cashier)
    approve_via_inbox(s, m.manager)
    s.invalidate_recordset()
    assert (s.supervisor_variance_approved_by, s.variance_approved_amount) == (
        m.manager,
        -1000.0,
    )
    assert s.approval_state == "approved"
    s.action_confirm_closed()
    m.as_(m.manager, s).action_reconcile()
    assert s.sudo().state == "discrepancy"
    # B2: shift.closed is published by a literal publish()
    assert _outbox(m.env, "shift.closed", "fix.cash.shift", s.id)


def test_a_price_below_list_is_approved_from_the_inbox(m04, call):
    m = m04
    s = m.shift()
    sale = m.sale(s, price=850.0)
    with _refused(m.env, UserError, "below the list price"):
        sale.action_confirm()
    res = call(
        m.env(user=m.cashier.id),
        "model_action",
        model="fix.counter.sale",
        ids=[sale.id],
        method="action_request_approval",
        kwargs={"justification": "Loyal walk-in, manager agreed by phone"},
    )
    assert res["success"], res
    sale.invalidate_recordset()
    # managers only (the refund approver is not one), never the seller
    assert m.manager in assigned(sale) and not assigned(sale) & (m.approver | m.cashier)
    assert sale.approval_request_id.decision_domain == "price_override"
    approve_via_inbox(sale, m.manager)
    sale.action_confirm()
    assert sale.state == "confirmed" and s.sudo().cash_payments == 850.0


def test_a_rejected_refund_leaves_the_sale_confirmed(m04):
    m = m04
    s = m.shift()
    sale = m.sale(s)
    sale.action_confirm()
    sale.action_request_refund(reason="customer_cancelled")
    sale.invalidate_recordset()
    assert sale.approval_request_id.decision_domain == "counter_refund"
    task = inbox_task(sale, m.approver)
    task.with_user(m.approver).action_reject(comment="Item opened and used")
    sale.invalidate_recordset()
    assert (sale.state, sale.refund_state, sale.approval_state) == (
        "confirmed",
        "none",
        "rejected",
    )
    assert s.sudo().cash_refunds == 0.0
    # it can be asked again, and approved by the manager instead
    sale.action_request_refund(reason="defective: screen flickers")
    approve_via_inbox(sale, m.manager)
    assert sale.sudo().refund_state == "refunded" and s.sudo().cash_refunds == 1000.0


def test_a_refund_request_with_no_approver_is_refused_whole(m04):
    """With nobody to decide, nothing is recorded (no orphan 'requested')."""
    m = m04
    s = m.shift()
    sale = m.sale(s)
    sale.action_confirm()
    for xmlid in (
        "cd_front_desk.group_fd_refund_approver",
        "cd_front_desk.group_fd_branch_manager",
    ):
        m.env.ref(xmlid).write({"user_ids": [(5, 0, 0)]})
    with _refused(m.env, UserError, "No one can approve"):
        sale.action_request_refund(reason="duplicate")
    assert sale.refund_state == "none"


# ============================================================ P2 token queue
def test_queue_actions_need_a_front_desk_role(m04, call):
    m = m04
    t = m.token()
    with _refused(m.env, UserError, "Queue Agent"):
        m.as_(m.plain, t).action_call()
    agent = _user(m, "agent", "cd_front_desk.group_fd_queue_agent")
    m.as_(agent, t).action_call()
    assert t.state == "called"
    # the whitelisted cancel now has a button; it checks the role too
    res = call(
        m.env(user=m.plain.id),
        "model_action",
        model="fix.token.queue",
        ids=[t.id],
        method="action_cancel",
    )
    assert res["success"] is False, res
    res = call(
        m.env(user=m.cashier.id),
        "model_action",
        model="fix.token.queue",
        ids=[t.id],
        method="action_cancel",
    )
    assert res["success"], res
    t.invalidate_recordset()
    assert t.state == "cancelled"


def test_recall_is_counted_and_auto_no_show_is_a_switch(m04):
    m = m04
    # A02 ERP audit M04-F12: the switch is ON by default now (BRU-FRD-08);
    # this test turns it off explicitly to show the counting alone
    m.env["ir.config_parameter"].set_param("cd_front_desk.token_auto_no_show", "0")
    t = m.token()
    t.action_call()
    first_call = t.called_at
    t.action_call()  # re-call: the customer did not come up
    t.action_call()
    assert (t.state, t.recall_count) == ("called", 2) and t.last_recalled_at
    assert t.called_at == first_call  # the wait ended at the first call
    with _refused(m.env, UserError, GUARD):
        t.write({"recall_count": 0})
    # switch off: no limit is applied
    for _i in range(3):
        t.action_call()
    assert (t.state, t.recall_count) == ("called", 5)
    m.env["ir.config_parameter"].set_param("cd_front_desk.token_auto_no_show", "1")
    m.env["ir.config_parameter"].set_param("cd_front_desk.token_recall_limit", "2")
    t2 = m.token()
    t2.action_call()
    t2.action_call()
    t2.action_call()
    res = t2.action_call()  # third re-call is past the limit of 2
    assert t2.state == "no_show" and "no-show" in res["warning"]
    assert t2.recall_count == 2


# ============================================================ P2 counter sale
def test_tender_vat_split_and_mushak_number(m04):
    m = m04
    s = m.shift()
    sale = m.sale(s, price=1150.0)
    assert sale.vat_rate == 15.0
    assert (sale.amount_untaxed, sale.vat_amount, sale.total) == (1000.0, 150.0, 1150.0)
    sale.write({"tendered_amount": 500.0})
    with _refused(m.env, UserError, "does not cover"):
        sale.action_confirm()
    sale.write({"tendered_amount": 2000.0})
    assert sale.change_due == 850.0
    for vals in ({"mushak_63_ref": "TYPED"}, {"vat_rate": 0.0}, {"vat_amount": 0.0}):
        with _refused(m.env, UserError, GUARD):
            sale.write(vals)
    sale.action_confirm()
    assert sale.mushak_63_ref and sale.mushak_63_ref.startswith("M63/")
    with _refused(m.env, UserError, "can no longer be changed"):
        sale.write({"tendered_amount": 5000.0})
    # a required tender is a switch (off today)
    m.env["ir.config_parameter"].set_param("cd_front_desk.counter_tender_required", "1")
    other = m.sale(s, price=1150.0)
    with _refused(m.env, UserError, "cash tendered"):
        other.action_confirm()
    mfs = m.sale(s, price=1150.0, method="bkash")
    mfs.write({"transaction_ref": "TRX-P2-0001"})  # not cash: its TrxID, no tender
    mfs.action_confirm()


# ============================================================ P2 order cash
def _order(m):
    return m.env["fix.service.order"].create(
        {
            "device_id": m.device.id,
            "customer_id": m.customer.id,
            "branch_id": m.branch.id,
            "fault_description": "battery swollen",
            "service_type": "walk_in",
        }
    )


def test_m01_counter_settlement_lands_in_the_drawer(m04):
    m = m04
    so_cashier = _user(m, "socash", "cd_service_order.group_so_cashier")
    s = m.shift()
    order = _order(m)
    order.with_user(so_cashier)._fix_record_settlement(700.0, "CTR-0001", "counter")
    assert order.counter_shift_id == s and s.sudo().cash_payments == 700.0
    assert s.sudo().expected_closing == 5700.0
    with _refused(m.env, UserError, GUARD):
        order.with_user(so_cashier).write({"counter_shift_id": False})
    # other sources do not touch the drawer
    order2 = _order(m)
    order2.with_user(so_cashier)._fix_record_settlement(300.0, "TRX-FIELD", "field_collection")
    assert s.sudo().cash_payments == 700.0


def test_counter_cash_with_no_open_shift_is_a_switch(m04):
    m = m04
    so_cashier = _user(m, "socash2", "cd_service_order.group_so_cashier")
    # switched off by an explicit "0" (an absent parameter now means ON: see
    # test_a02_authz_accuracy_m04)
    m.env["ir.config_parameter"].set_param("cd_front_desk.order_cash_requires_open_shift", "0")
    order = _order(m)
    order.with_user(so_cashier)._fix_record_settlement(400.0, "CTR-0002", "counter")
    assert not order.counter_shift_id and order.payment_settlement_state == "settled"
    m.env["ir.config_parameter"].set_param("cd_front_desk.order_cash_requires_open_shift", "1")
    order2 = _order(m)
    with _refused(m.env, UserError, "no open cash shift"):
        order2.with_user(so_cashier)._fix_record_settlement(400.0, "CTR-0003", "counter")
    assert order2.payment_settlement_state != "settled"


# ============================================================ P2 diagnostic fee
def _ready(m, **vals):
    return m.intake(
        device_id=m.device.id,
        handover_method="signature",
        customer_signature_attachment_id=m.signature.id,
        **vals,
    )


def test_cash_diagnostic_fee_is_posted_at_handover(m04):
    m = m04
    s = m.shift()
    it = _ready(m, payment_channel="cash", diagnostic_fee_bdt=300.0)
    it.action_complete_handover()
    assert it.diagnostic_fee_shift_id == s and s.sudo().cash_payments == 300.0
    # MFS needs its TrxID
    it2 = _ready(m, payment_channel="bkash", diagnostic_fee_bdt=300.0)
    with _refused(m.env, UserError, "TrxID"):
        it2.action_complete_handover()
    it2.write({"payment_trx_ref": "BK123456"})
    it2.action_complete_handover()
    assert s.sudo().cash_payments == 300.0  # not cash


def test_a_waived_fee_needs_a_managers_approval(m04):
    m = m04
    it = _ready(m, payment_channel="waived", diagnostic_fee_bdt=300.0)
    with _refused(m.env, UserError, "approve the waiver"):
        it.action_complete_handover()
    it.action_submit_for_handover()  # routes the waiver
    it.invalidate_recordset()
    assert it.state == "handover_pending" and it.approval_state == "pending"
    assert m.manager in assigned(it) and m.cashier not in assigned(it)
    with _refused(m.env, UserError, GUARD):
        it.write({"fee_waiver_approved_by_id": m.cashier.id})
    approve_via_inbox(it, m.manager)
    it.invalidate_recordset()
    assert it.fee_waiver_approved_by_id == m.manager and it.fee_waiver_approved_amount == 300.0
    # the waiver is pinned: a higher fee needs a new one
    it.write({"diagnostic_fee_bdt": 500.0})
    with _refused(m.env, UserError, "approve the waiver"):
        it.action_complete_handover()
    it.write({"diagnostic_fee_bdt": 300.0})
    it.action_complete_handover()
    assert it.state == "completed"


def test_a_waiver_with_no_fee_follows_the_standard_fee_switch(m04):
    m = m04
    it = _ready(m, payment_channel="waived")
    it.action_complete_handover()  # today: a 0 fee waives nothing
    assert it.state == "completed"
    m.env["ir.config_parameter"].set_param("cd_front_desk.standard_diagnostic_fee_bdt", "250")
    it2 = _ready(m, payment_channel="waived")
    with _refused(m.env, UserError, "BDT 250.00"):
        it2.action_complete_handover()


# ============================================================ P2 device
def test_the_device_is_required_when_the_intake_is_created(m04, call):
    m = m04
    with _refused(m.env, UserError, "BRU-FRD-12"):
        m.intake()
    res = call(
        m.env(user=m.cashier.id),
        "model_write",
        model="fix.walkin.intake",
        values={
            "branch_id": m.branch.id,
            "operating_unit_id": m.ou.id,
            "customer_id": m.customer.id,
            "fault_description": "no device given",
        },
    )
    assert "error" in res, res
    # a scanned, registered serial links the device at once
    it = m.intake(device_serial_input=m.device.serial_number)
    assert it.device_id == m.device
    # and the device cannot be cleared afterwards
    with _refused(m.env, UserError, "BRU-FRD-12"):
        it.write({"device_id": False, "device_serial_input": False})
    it.write({"device_id": False})  # the serial still identifies it
    assert it.device_serial_input


# ============================================================ B2 events
def test_m04_events_are_published_literally(m04):
    m = m04
    t = m.token()
    assert _outbox(m.env, "token.issued", "fix.token.queue", t.id)
    it = _ready(m)
    it.action_complete_handover()
    assert _outbox(m.env, "handover.completed", "fix.walkin.intake", it.id)
    import inspect

    from odoo.addons.cd_front_desk.models import fix_cash_shift, fix_token_queue, fix_walkin_intake

    for module in (fix_cash_shift, fix_token_queue, fix_walkin_intake):
        assert "def _emit" not in inspect.getsource(module)


@pytest.mark.parametrize(
    "model,method",
    [
        ("fix.cash.shift", "action_approve_variance"),
        ("fix.counter.sale", "action_approve_refund"),
        ("fix.counter.sale", "action_approve_price_override"),
        ("fix.walkin.intake", "action_approve_fee_waiver"),
    ],
)
def test_the_approve_methods_are_not_on_the_workspace(m04, call, model, method):
    m = m04
    rec = m.env[model].search([], limit=1)
    res = call(
        m.env(user=m.manager.id),
        "model_action",
        model=model,
        ids=rec.ids or [0],
        method=method,
    )
    assert res.get("success") is not True, res
