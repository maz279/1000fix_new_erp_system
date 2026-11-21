"""A02 pass 2: the drawer's differences reach the GL when they are known.

M04-04 (P2): the variance posted only at the optional reconcile, so a shift
confirmed closed and never reconciled kept its shortage out of the GL while
M50 banked from it. It now posts when the count is confirmed.
M04-03 (P2): an opening float other than what the last close left is a cash
difference: once a Branch Manager accepts it, it posts like a variance.
"""

# ruff: noqa: F811  (the bridge's fixtures are used as parameters)
import pytest
from odoo.addons.cd_front_desk.tests.test_a02_p0_m04 import m04  # noqa: F401
from odoo.addons.cd_front_desk_finance.tests.test_counter_sale_posting import (  # noqa: F401
    _balance,
    _lines,
    fin,
)
from odoo.addons.cd_front_desk_finance.tests.test_shift_variance_posting import var  # noqa: F401
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox

pytestmark = [pytest.mark.financial]


def test_the_variance_posts_when_the_count_is_confirmed(var):
    m = var
    s = m.shift()
    m.count(s, d1000=4, d500=1, d100=1, d50=1)  # 4,650: -350
    approve_via_inbox(s, m.manager, requester=m.cashier)
    s.action_confirm_closed()
    shift = s.sudo()
    shift.invalidate_recordset()
    assert shift.state == "closed", "nobody has reconciled it"
    assert shift.variance_posting_state == "posted"
    assert _lines(shift.variance_move_id) == {
        m.acc.shortage.code: (350.0, 0.0),
        m.acc.drawer.code: (0.0, 350.0),
    }
    # the later reconcile posts nothing more
    m.as_(m.manager, s).action_reconcile()
    assert _balance(m.env, m.acc.shortage) == 350.0


def test_an_accepted_float_difference_posts_as_a_cash_variance(var):
    m = var
    s1 = m.shift()
    m.count(s1, d1000=5)
    s1.action_confirm_closed()
    s2 = m.shift(opening=4800.0)  # the last close left 5,000
    assert s2.sudo().float_variance == -200.0
    s2.with_user(m.manager).action_approve_opening_float()
    shift = s2.sudo()
    shift.invalidate_recordset()
    assert shift.float_posting_state == "posted"
    assert _lines(shift.float_move_id) == {
        m.acc.shortage.code: (200.0, 0.0),
        m.acc.drawer.code: (0.0, 200.0),
    }
    # retried: nothing posts twice
    s2.with_user(m.manager).action_retry_variance_posting()
    m.env["fix.cash.shift"]._cron_retry_float_postings()
    assert _balance(m.env, m.acc.shortage) == 200.0


def test_a_float_surplus_pending_until_its_account_exists(var):
    m = var
    s1 = m.shift()
    m.count(s1, d1000=5)
    s1.action_confirm_closed()
    m.params.set_param("cd_front_desk_finance.account_code.cash_overage", False)
    m.params.set_param("cd_cash_position.account_code.cash_shortage", False)
    s2 = m.shift(opening=5100.0)
    s2.with_user(m.manager).action_approve_opening_float()
    assert s2.sudo().float_posting_state == "pending"
    m.params.set_param("cd_front_desk_finance.account_code.cash_overage", m.acc.overage.code)
    m.env["fix.cash.shift"]._cron_retry_float_postings()
    s2.invalidate_recordset()
    assert s2.sudo().float_posting_state == "posted"
    assert _lines(s2.sudo().float_move_id) == {
        m.acc.drawer.code: (100.0, 0.0),
        m.acc.overage.code: (0.0, 100.0),
    }
