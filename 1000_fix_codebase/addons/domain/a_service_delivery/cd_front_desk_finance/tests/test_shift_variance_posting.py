"""cd_front_desk_finance — the drawer's counted variance reaches the GL.

E2E2 flow 2 (11 Nov 2026, copy of fix_real): the blind count found the drawer
BDT 350 short, a branch manager approved the -350 from the M63 inbox and a
second manager reconciled the shift to "discrepancy" — and nothing posted.
The drawer cash account (100108) went on carrying 350 the drawer did not
hold, and 500902 Cash Shortage stayed at zero.

A reconciled shift with a variance now posts, through M19 as the counter
bridge does: a shortage Dr cash shortage / Cr drawer cash, an overage Dr
drawer cash / Cr cash overage. An account that does not resolve never blocks
the reconcile: the shift is left pending with the reason and the retry (or
the hourly job) posts it once; nothing posts twice. The cashier and the
manager hold no accounting role.
"""

# ruff: noqa: F811  (the bridge's and the P0 suite's fixtures are used as parameters)
import pytest
from odoo.addons.cd_front_desk.tests.test_a02_p0_m04 import _refused, m04  # noqa: F401
from odoo.addons.cd_front_desk_finance.tests.test_counter_sale_posting import (  # noqa: F401
    _balance,
    _lines,
    fin,
)
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox
from odoo.exceptions import AccessError, UserError, ValidationError

pytestmark = [pytest.mark.financial]

SHORT_PARAM = "cd_cash_position.account_code.cash_shortage"
OVER_PARAM = "cd_front_desk_finance.account_code.cash_overage"
REFUSED = (UserError, ValidationError, AccessError)


@pytest.fixture
def var(fin):
    m = fin
    env = m.env

    def account(key, kind, name):
        return env["account.account"].create(
            {
                "code": "CSV%s%s" % (m.acc.drawer.code[-6:], key),
                "name": "Shift %s %s" % (name, m.acc.drawer.code),
                "account_type": kind,
            }
        )

    m.acc.shortage = account("SHT", "expense", "cash shortage")
    m.acc.overage = account("OVR", "income_other", "excess in till")
    m.params.set_param(SHORT_PARAM, m.acc.shortage.code)
    m.params.set_param(OVER_PARAM, m.acc.overage.code)

    def counted(denoms, approve=True):
        """Open a BDT 5,000 float, count it, confirm, approve (if beyond
        tolerance) from the inbox and reconcile as the branch manager."""
        s = m.shift()
        m.count(s, **denoms)
        s.action_confirm_closed()
        if approve and abs(s.sudo().variance) > 100.0:
            approve_via_inbox(s, m.manager, requester=m.cashier)
        m.as_(m.manager, s).action_reconcile()
        s.invalidate_recordset()
        return s

    m.counted = counted
    return m


def test_the_e2e2_shortage_posts_dr_cash_shortage_cr_drawer(var):
    """-350: counted 4,650 of 5,000, approved from the inbox, reconciled."""
    m = var
    assert not m.manager.has_group("account.group_account_user")
    s = m.counted({"d1000": 4, "d500": 1, "d100": 1, "d50": 1})
    shift = s.sudo()
    assert (shift.state, shift.variance) == ("discrepancy", -350.0)
    move = shift.variance_move_id
    assert move and move.state == "posted", "the approved shortage never reached the GL"
    assert _lines(move) == {
        m.acc.shortage.code: (350.0, 0.0),
        m.acc.drawer.code: (0.0, 350.0),
    }
    assert shift.variance_posting_state == "posted"
    assert _balance(m.env, m.acc.drawer) == -350.0
    assert _balance(m.env, m.acc.shortage) == 350.0
    # through M19, on behalf of the reconciling manager
    log = m.env["fix.journal.posting.log"].sudo().search([("move_id", "=", move.id)])
    assert log.source == "cash_shift" and log.requested_by == m.manager


def test_an_overage_posts_dr_drawer_cr_cash_overage(var):
    m = var
    s = m.counted({"d1000": 5, "d200": 1})  # 5,200: +200
    move = s.sudo().variance_move_id
    assert _lines(move) == {
        m.acc.drawer.code: (200.0, 0.0),
        m.acc.overage.code: (0.0, 200.0),
    }


def test_an_overage_without_its_own_account_uses_the_shortage_over_account(var):
    """The estate books every cash over to its "Cash shortage / over" account
    (cd_cash_position's cash_shortage role, as the M50 deposit over-credit
    does) until a separate overage account is named."""
    m = var
    m.params.set_param(OVER_PARAM, False)
    s = m.counted({"d1000": 5, "d200": 1})
    assert _lines(s.sudo().variance_move_id) == {
        m.acc.drawer.code: (200.0, 0.0),
        m.acc.shortage.code: (0.0, 200.0),
    }


def test_a_variance_within_tolerance_posts_too(var):
    """-50 needs no approval, but the drawer still holds 50 less."""
    m = var
    s = m.counted({"d1000": 4, "d500": 1, "d200": 2, "d50": 1})  # 4,950
    assert s.sudo().state == "discrepancy"
    assert _lines(s.sudo().variance_move_id) == {
        m.acc.shortage.code: (50.0, 0.0),
        m.acc.drawer.code: (0.0, 50.0),
    }


def test_a_balanced_drawer_posts_nothing(var):
    m = var
    s = m.counted({"d1000": 5})
    shift = s.sudo()
    assert shift.state == "reconciled"
    assert not shift.variance_move_id and shift.variance_posting_state == "none"


def test_a_missing_account_leaves_the_shift_pending_never_blocked(var):
    m = var
    m.params.set_param(SHORT_PARAM, False)
    s = m.counted({"d1000": 4, "d500": 1, "d100": 1, "d50": 1})
    shift = s.sudo()
    assert shift.state == "discrepancy", "a missing account must not block the reconcile"
    assert shift.variance_posting_state == "pending" and not shift.variance_move_id
    assert SHORT_PARAM in (shift.variance_posting_note or "")
    # retry before the account is set: still pending, nothing posted
    m.as_(m.manager, s).action_retry_variance_posting()
    assert s.sudo().variance_posting_state == "pending"
    # configured: the retry posts once; again posts nothing
    m.params.set_param(SHORT_PARAM, m.acc.shortage.code)
    m.as_(m.manager, s).action_retry_variance_posting()
    m.as_(m.manager, s).action_retry_variance_posting()
    s.invalidate_recordset()
    assert s.sudo().variance_posting_state == "posted"
    assert _balance(m.env, m.acc.shortage) == 350.0
    assert _balance(m.env, m.acc.drawer) == -350.0


def test_the_hourly_job_posts_a_pending_shift_once(var):
    m = var
    m.params.set_param(SHORT_PARAM, False)
    s = m.counted({"d1000": 4, "d500": 1, "d100": 1, "d50": 1})
    m.params.set_param(SHORT_PARAM, m.acc.shortage.code)
    Shift = m.env["fix.cash.shift"]
    Shift._cron_retry_variance_postings()
    Shift._cron_retry_variance_postings()
    s.invalidate_recordset()
    assert s.sudo().variance_posting_state == "posted"
    assert _balance(m.env, m.acc.shortage) == 350.0


def test_the_posting_outcome_cannot_be_typed(var):
    m = var
    s = m.counted({"d1000": 4, "d500": 1, "d100": 1, "d50": 1})
    for vals in ({"variance_posting_state": "none"}, {"variance_move_id": False}):
        with pytest.raises(REFUSED), m.env.cr.savepoint():
            m.as_(m.manager, s).write(vals)
    # nobody outside the front desk / finance retries
    with pytest.raises(REFUSED), m.env.cr.savepoint():
        m.as_(m.plain, s).action_retry_variance_posting()
    assert s.sudo().variance_posting_state == "posted"
