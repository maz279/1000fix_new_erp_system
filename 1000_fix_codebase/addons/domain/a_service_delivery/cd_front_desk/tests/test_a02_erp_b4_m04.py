# A02 ERP audit, stream B4 (20 Nov 2026): M04 Branch & Front Desk.
#
#   M04-F5   the BRU-FRD-11 cash-handler set holds everyone who confirmed a
#            sale into the drawer, approved a refund paid from it or recorded a
#            movement on it; branch / operator / date are frozen at opening
#   M04-F6   a below-list sale's price approval is obtainable before confirm
#   M04-F9   operator scope: the acting cashier's own open shift is preferred
#   M04-F12  call-next by lane then issue time, daily per-branch numbering
#            (unique), one recall then no-show by default
#   M04-F16  BRU-FRD-03: no close with an unapproved variance; BRU-FRD-10
#            terms acceptance for flagged counter products
#   X-04     the internal counter reference is not presented as the NBR number
#
# Every test runs against the ORM in a rolled-back transaction.
from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_front_desk.tests.test_a02_p0_m04 import (  # noqa: F401
    GUARD,
    _refused,
    m04,
)
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox, assigned
from odoo.exceptions import UserError, ValidationError

SCOPE = "cd_front_desk.open_shift_scope"


@pytest.fixture
def b4(m04):  # noqa: F811
    params = m04.env["ir.config_parameter"]
    # the settings these tests depend on, stated (the copies carry real ones)
    params.set_param(SCOPE, "branch")
    params.set_param("cd_front_desk.variance_tolerance_bdt", "100")
    params.set_param("cd_front_desk.price_override_tolerance_pct", "0")
    params.set_param("cd_front_desk.counter_tender_required", "0")
    params.set_param("cd_front_desk.token_recall_limit", False)
    params.set_param("cd_front_desk.token_auto_no_show", False)
    return m04


def _counter(m, number=1, **vals):
    return m.env["fix.queue.counter"].create(
        {"branch_id": m.branch.id, "operating_unit_id": m.ou.id, "number": number, **vals}
    )


def _token(m, **vals):
    return m.token(**vals)


# =================================================================== M04-F5


def test_f5_whoever_confirmed_a_sale_into_the_drawer_cannot_reconcile_it(b4):
    m = b4
    s = m.shift()
    # a manager who also works the till rings a sale into the cashier's drawer
    sale = m.sale(s, as_user=m.manager_cashier)
    sale.with_user(m.manager_cashier).action_confirm()
    assert m.manager_cashier in s.sudo()._fd_cash_handlers()
    total = int(s.sudo().expected_closing)
    m.count(s, d1000=total // 1000)
    s.action_confirm_closed()
    with _refused(m.env, UserError, "BRU-FRD-11"):
        m.as_(m.manager_cashier, s).action_reconcile()
    m.as_(m.manager, s).action_reconcile()
    assert s.sudo().reconciled_by == m.manager


def test_f5_a_refund_approver_and_a_movement_recorder_handled_the_drawer(b4):
    m = b4
    s = m.shift()
    sale = m.sale(s)
    sale.action_confirm()
    sale.action_request_refund(reason="defective: screen flickers")
    approve_via_inbox(sale, m.manager_cashier, requester=m.cashier)
    assert sale.sudo().refund_shift_id == s
    handlers = s.sudo()._fd_cash_handlers()
    assert m.manager_cashier in handlers
    # a cash-out recorded on the drawer by the other manager
    m.env["fix.cash.movement"].with_user(m.manager).create(
        {
            "shift_id": s.id,
            "movement_type": "safe_drop",
            "amount": 100.0,
            "reason": "safe drop to the branch safe",
        }
    )
    assert m.manager in s.sudo()._fd_cash_handlers()
    # the variance routing now excludes both of them
    assert {m.manager, m.manager_cashier} <= set(s.sudo()._approval_excluded())


def test_f5_branch_operator_and_date_are_frozen_once_opened(b4):
    m = b4
    s = m.shift()
    for vals in (
        {"operator_id": m.cashier2_emp.id},
        {"branch_id": m.branch2.id},
        {"shift_date": fields.Date.today() - timedelta(days=3)},
    ):
        with _refused(m.env, UserError, "can no longer be changed"):
            s.write(vals)
    assert {"operator_id", "branch_id", "shift_date"} <= s._fix_form_locked_fields()
    # a new shift still takes them at creation
    s2 = m.shift(branch=m.branch2, as_user=m.cashier2, operator=m.cashier2_emp)
    assert (s2.branch_id, s2.operator_id) == (m.branch2, m.cashier2_emp)


# =================================================================== M04-F9


def test_f9_operator_scope_takes_the_confirming_cashiers_own_drawer(b4):
    m = b4
    m.env["ir.config_parameter"].set_param(SCOPE, "operator")
    own = m.shift()  # the cashier's drawer, opened first
    newer = m.shift(as_user=m.cashier2, operator=m.cashier2_emp)  # the newest of the branch
    Shift = m.env["fix.cash.shift"]
    # the legacy two-argument call still answers (the branch's newest)
    assert Shift._fd_open_shift_for(m.branch, m.env.company) == newer
    assert Shift.with_user(m.cashier)._fd_open_shift_for(m.branch, m.env.company) == own
    assert Shift._fd_open_shift_for(m.branch, m.env.company, m.cashier2) == newer
    sale = m.sale(None)
    sale.action_confirm()
    assert sale.shift_id == own and own.sudo().cash_payments == 1000.0
    assert newer.sudo().cash_payments == 0.0
    # someone with no drawer of their own falls back to the branch's newest
    assert Shift._fd_open_shift_for(m.branch, m.env.company, m.manager) == newer
    # branch scope: unchanged (one drawer per branch)
    m.env["ir.config_parameter"].set_param(SCOPE, "branch")
    assert Shift.with_user(m.cashier)._fd_open_shift_for(m.branch, m.env.company) == newer


# =================================================================== M04-F12


def test_f12_tokens_number_per_dhaka_day_and_never_twice(b4):
    m = b4
    Token = m.env["fix.token.queue"].sudo()._guarded()
    yesterday = fields.Datetime.now() - timedelta(days=1)
    old = Token.create(
        [
            {"branch_id": m.branch.id, "operating_unit_id": m.ou.id, "issued_at": yesterday},
            {"branch_id": m.branch.id, "operating_unit_id": m.ou.id, "issued_at": yesterday},
        ]
    )
    assert old.mapped("token_number") == [1, 2]
    today = _token(m)
    assert today.token_number == 1, "the number restarts every business day"
    assert today.queue_date != old[0].queue_date
    assert _token(m).token_number == 2
    # a number is issued once a day per branch
    with _refused(m.env, Exception):
        Token.create({"branch_id": m.branch.id, "operating_unit_id": m.ou.id, "token_number": 2})
        m.env.flush_all()


def test_f12_queue_day_is_the_dhaka_day(b4):
    m = b4
    # 19:00 UTC on the 1st is 01:00 on the 2nd in Dhaka
    stamp = fields.Datetime.to_datetime("2026-11-01 19:00:00")
    tok = (
        m.env["fix.token.queue"]
        .sudo()
        ._guarded()
        .create({"branch_id": m.branch.id, "operating_unit_id": m.ou.id, "issued_at": stamp})
    )
    assert str(tok.queue_date) == "2026-11-02"


def test_f12_the_counter_calls_the_highest_lane_then_the_first_issued(b4):
    m = b4
    counter = _counter(m)
    normal = _token(m)
    senior = _token(m, priority_level="senior_citizen")
    vip = _token(m, priority_level="vip_corporate")
    senior2 = _token(m, priority_level="senior_citizen")
    called = []
    for _i in range(4):
        res = counter.with_user(m.cashier).action_call_next()
        called.append(m.env["fix.token.queue"].browse(res["token_id"]))
    assert called == [vip, senior, senior2, normal]
    assert all(t.state == "called" and t.counter_id == counter for t in called)
    with _refused(m.env, ValidationError, "is waiting"):
        counter.with_user(m.cashier).action_call_next()


def test_f12_a_counter_calls_only_what_it_serves(b4):
    m = b4
    pay_only = _counter(m, number=2, can_intake=False, can_collect=False, can_enquiry=False)
    drop = _token(m, priority_level="vip_corporate")  # drop-off: not served there
    pay = _token(m, service_type="payment")
    res = pay_only.with_user(m.cashier).action_call_next()
    assert res["token_id"] == pay.id and drop.state == "waiting"
    # a plain user does not run the queue
    _token(m, service_type="payment")
    with _refused(m.env, UserError, "Queue Agent"):
        pay_only.with_user(m.plain).action_call_next()


def test_f12_call_next_from_the_queue_screen_follows_the_lanes(b4):
    m = b4
    first = _token(m)
    vip = _token(m, priority_level="vip_corporate")
    res = first.with_user(m.cashier).action_call_next()
    assert res["token_id"] == vip.id and vip.state == "called" and first.state == "waiting"


def test_f12_one_recall_then_no_show_by_default(b4):
    """BRU-FRD-08: a customer is re-called once; the next re-call is a no-show."""
    m = b4
    t = _token(m)
    t.with_user(m.cashier).action_call()
    t.with_user(m.cashier).action_call()  # the one recall
    assert (t.state, t.recall_count) == ("called", 1)
    res = t.with_user(m.cashier).action_call()
    assert t.state == "no_show" and "no-show" in res["warning"]


def test_f12_the_list_reads_in_calling_order(b4):
    m = b4
    normal = _token(m)
    vip = _token(m, priority_level="vip_corporate")
    rows = m.env["fix.token.queue"].search([("id", "in", (normal | vip).ids)])
    assert list(rows) == [vip, normal]
    assert (vip.priority_rank, normal.priority_rank) == (3, 0)


# =================================================================== M04-F16


def test_f16_an_unapproved_variance_does_not_close_the_shift(b4):
    m = b4
    s = m.shift()
    m.count(s, d1000=4)  # 4,000 of 5,000: BDT 1,000 short
    with _refused(m.env, UserError, "BRU-FRD-03"):
        s.action_confirm_closed()
    assert s.sudo().state == "counting"
    approve_via_inbox(s, m.manager, requester=m.cashier)
    s.action_confirm_closed()
    assert s.sudo().state == "closed"
    # within tolerance: closes with no approval
    s2 = m.shift(branch=m.branch2)
    m.count(s2, d1000=4, d500=1, d100=4, d50=1)  # -50
    s2.action_confirm_closed()
    assert s2.sudo().state == "closed"


def test_bru_frd_10_a_protection_plan_is_sold_once_its_terms_are_accepted(b4):
    m = b4
    plan = m.env["product.product"].create(
        {"name": "B4 screen protection plan", "list_price": 1000.0, "type": "service"}
    )
    plan.product_tmpl_id.fd_counter_terms_required = True
    s = m.shift()
    sale = m.sale(s)
    sale.write({"product_id": plan.id})
    assert sale.terms_required
    with _refused(m.env, UserError, "BRU-FRD-10"):
        sale.action_confirm()
    with _refused(m.env, UserError, "choose the customer"):
        sale.action_accept_terms()
    with _refused(m.env, UserError, GUARD):
        sale.write({"terms_accepted_at": fields.Datetime.now()})
    sale.write({"customer_id": m.customer.id})
    with _refused(m.env, UserError, "Front Desk Cashier"):
        sale.with_user(m.plain).action_accept_terms()
    sale.action_accept_terms()
    assert (sale.terms_accepted_by, sale.terms_accepted_partner_id) == (m.cashier, m.customer)
    # another customer did not accept them
    other = m.env["res.partner"].create({"name": "B4 someone else"})
    sale.write({"customer_id": other.id})
    with _refused(m.env, UserError, "BRU-FRD-10"):
        sale.action_confirm()
    sale.write({"customer_id": m.customer.id})
    sale.action_confirm()
    assert sale.state == "confirmed"
    # an unflagged product sells as before
    plain_sale = m.sale(s)
    plain_sale.action_confirm()
    assert plain_sale.state == "confirmed"


# =================================================================== M04-F6


def test_f6_a_below_list_price_is_approved_before_anything_confirms(b4):
    m = b4
    s = m.shift()
    cheap = m.sale(s, price=800.0)
    full = m.sale(s)
    sales = cheap | full
    assert sales._fd_price_blocked() == cheap
    waiting = sales.action_request_price_approvals()
    assert waiting == cheap and cheap.approval_state == "pending"
    assert m.manager in assigned(cheap) and m.cashier not in assigned(cheap)
    # asking again does not raise a second request
    assert sales.action_request_price_approvals() == cheap
    approve_via_inbox(cheap, m.manager)
    assert not sales._fd_price_blocked()
    sales.action_confirm()
    assert set(sales.mapped("state")) == {"confirmed"}
    with _refused(m.env, UserError, "Front Desk Cashier"):
        m.sale(s, price=700.0).with_user(m.plain).action_request_price_approvals()


# =================================================================== X-04


def test_x04_the_internal_reference_is_not_labelled_the_nbr_number(b4):
    m = b4
    Sale = m.env["fix.counter.sale"]
    ref = Sale._fields["mushak_63_ref"]
    assert "NBR" not in ref.string and "internal" in ref.string.lower()
    assert "estimate" in Sale._fields["vat_amount"].string.lower()
    s = m.shift()
    sale = m.sale(s)
    sale.action_confirm()
    # the internal reference is still issued, the statutory one is the bridge's
    assert sale.mushak_63_ref
    if "mushak_id" in Sale._fields:
        assert sale.mushak_63_ref != (sale.mushak_id.mushak_no or "")


# ===================================================== lead request: _hv_is_open


def test_the_id_check_target_open_hook(b4):
    m = b4
    Check = m.env["fix.cash.id.check"]
    s = m.shift()
    sale = m.sale(s)
    assert Check._hv_is_open(sale)
    sale.action_confirm()
    assert not Check._hv_is_open(sale)
