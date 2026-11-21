"""A02 pass 2 (M04-01 / X5-02, P0; owner decision D2): drawer cash-outs reach the GL.

A petty expense, a staff advance or a safe drop posted from the drawer lowered
the shift's expected cash and nothing else: the drawer account kept cash the
drawer no longer held, the expense never reached the P&L, the advance was owed
by nobody, the safe held nothing on the books. Posting a cash-out now posts
Dr expense-by-category / staff advance (employee partner) / Cash in Safe,
Cr drawer cash, through M19, idempotently, pending (never blocking) when an
account does not resolve. The M50 deposit can bank the safe. A technician's
field cash shortage (D20) books Dr payroll recovery / Cr drawer.

The cashier and the managers hold no accounting role; ``odoo_env`` rolls back.
"""

# ruff: noqa: F811  (the posting suite's fixtures are imported and used as parameters)
import pytest
from odoo.addons.cd_front_desk.tests.test_a02_p0_m04 import m04  # noqa: F401
from odoo.addons.cd_front_desk_finance.tests.test_counter_sale_posting import (  # noqa: F401
    _balance,
    _lines,
    fin,
)
from odoo.exceptions import AccessError, UserError, ValidationError

pytestmark = [pytest.mark.financial]

PARAM = "cd_front_desk_finance.account_code."
SAFE_PARAM = "cd_cash_position.account_code.branch_safe"
PAYROLL_PARAM = "cd_cash_position.account_code.rider_shortage_payroll"
REFUSED = (UserError, ValidationError, AccessError)


@pytest.fixture
def co(fin):
    m = fin
    env = m.env
    tag = m.acc.drawer.code[-8:]

    def account(key, kind, name):
        return env["account.account"].create(
            {
                "code": "CO%s%s" % (tag, key),
                "name": "Cash-out %s %s" % (name, tag),
                "account_type": kind,
            }
        )

    m.acc.misc = account("MSC", "expense", "miscellaneous expense")
    m.acc.conv = account("CNV", "expense", "conveyance")
    m.acc.ent = account("ENT", "expense", "entertainment")
    m.acc.adv = account("ADV", "asset_receivable", "advance loan office employee")
    m.acc.safe = account("SAF", "asset_cash", "cash in safe")
    m.acc.payroll = account("PAY", "liability_current", "salary payable")
    m.params.set_param(PARAM + "petty_expense", m.acc.misc.code)
    m.params.set_param(PARAM + "petty_conveyance", m.acc.conv.code)
    m.params.set_param(PARAM + "petty_entertainment", m.acc.ent.code)
    m.params.set_param(PARAM + "staff_advance", m.acc.adv.code)
    m.params.set_param(SAFE_PARAM, m.acc.safe.code)
    m.params.set_param(PAYROLL_PARAM, m.acc.payroll.code)

    def cash_out(shift, kind, amount, approve=False, **vals):
        mv = (
            env["fix.cash.movement"]
            .with_user(m.cashier)
            .create(
                {
                    "shift_id": shift.id,
                    "movement_type": kind,
                    "amount": amount,
                    "reason": vals.pop("reason", "test %s" % kind),
                    **vals,
                }
            )
        )
        if approve:
            mv.with_user(m.manager).action_approve()
        mv.with_user(m.cashier).action_post()
        mv.invalidate_recordset()
        return mv

    m.cash_out = cash_out
    return m


def test_a_petty_expense_posts_dr_miscellaneous_cr_drawer(co):
    m = co
    assert not m.cashier.has_group("account.group_account_user")
    s = m.shift()
    mv = m.cash_out(s, "petty_expense", 300.0, reason="Tea for customers")
    rec = mv.sudo()
    assert rec.state == "posted" and rec.posting_state == "posted"
    assert _lines(rec.move_id) == {m.acc.misc.code: (300.0, 0.0), m.acc.drawer.code: (0.0, 300.0)}
    assert _balance(m.env, m.acc.drawer) == -300.0
    assert s.sudo().expected_closing == 4700.0
    log = m.env["fix.journal.posting.log"].sudo().search([("move_id", "=", rec.move_id.id)])
    assert log.source == "cash_movement" and log.requested_by == m.cashier
    # the branch's dimensions (and so its operating unit) ride every line
    dims = (
        m.env["fix.journal.dimension"]
        .sudo()
        .search([("move_line_id", "in", rec.move_id.line_ids.ids)])
    )
    assert set(dims.mapped("branch_id")) == {m.branch}
    assert set(dims.mapped("operating_unit_id")) == {m.branch.operating_unit_id}
    assert rec.move_id.company_id == s.company_id


@pytest.mark.parametrize("category,attr", [("conveyance", "conv"), ("entertainment", "ent")])
def test_the_expense_category_picks_its_account(co, category, attr):
    m = co
    mv = m.cash_out(m.shift(), "petty_expense", 120.0, expense_category=category)
    assert _lines(mv.sudo().move_id) == {
        getattr(m.acc, attr).code: (120.0, 0.0),
        m.acc.drawer.code: (0.0, 120.0),
    }


def test_a_staff_advance_is_owed_by_the_employee(co):
    m = co
    s = m.shift()
    emp = m.cashier2_emp
    # an advance names who received it
    with pytest.raises(REFUSED), m.env.cr.savepoint():
        m.env["fix.cash.movement"].with_user(m.cashier).create(
            {"shift_id": s.id, "movement_type": "staff_advance", "amount": 1000.0, "reason": "x"}
        )
    mv = m.cash_out(s, "staff_advance", 1000.0, approve=True, employee_id=emp.id)
    move = mv.sudo().move_id
    assert _lines(move) == {m.acc.adv.code: (1000.0, 0.0), m.acc.drawer.code: (0.0, 1000.0)}
    adv_line = move.line_ids.filtered(lambda ln: ln.account_id == m.acc.adv)
    assert adv_line.partner_id == emp.work_contact_id and adv_line.partner_id


def test_a_safe_drop_goes_to_cash_in_safe_and_is_refused_without_a_safe(co):
    m = co
    s = m.shift()
    mv = m.cash_out(s, "safe_drop", 2000.0, reason="Mid-day safe drop")
    assert _lines(mv.sudo().move_id) == {
        m.acc.safe.code: (2000.0, 0.0),
        m.acc.drawer.code: (0.0, 2000.0),
    }
    # no safe account on the chart: the cash does not leave the drawer
    m.params.set_param(SAFE_PARAM, "NOSUCH-100112")
    drop = (
        m.env["fix.cash.movement"]
        .with_user(m.cashier)
        .create({"shift_id": s.id, "movement_type": "safe_drop", "amount": 500.0, "reason": "drop"})
    )
    with pytest.raises(UserError, match="branch safe"), m.env.cr.savepoint():
        drop.with_user(m.cashier).action_post()
    drop.invalidate_recordset()
    s.invalidate_recordset()
    assert drop.state == "draft" and s.cash_advances == 2000.0


def test_a_missing_account_leaves_the_cash_out_pending_and_the_retry_posts_once(co):
    m = co
    m.params.set_param(PARAM + "petty_expense", False)
    s = m.shift()
    mv = m.cash_out(s, "petty_expense", 250.0)
    rec = mv.sudo()
    assert rec.state == "posted", "a missing account must not block the cash-out"
    assert rec.posting_state == "pending" and not rec.move_id
    assert PARAM + "petty_expense" in (rec.posting_note or "")
    m.params.set_param(PARAM + "petty_expense", m.acc.misc.code)
    mv.with_user(m.cashier).action_retry_posting()
    mv.with_user(m.cashier).action_retry_posting()
    m.env["fix.cash.movement"]._cron_retry_movement_postings()
    mv.invalidate_recordset()
    assert mv.sudo().posting_state == "posted"
    assert _balance(m.env, m.acc.misc) == 250.0
    assert _balance(m.env, m.acc.drawer) == -250.0


def test_the_hourly_job_posts_a_pending_cash_out_once(co):
    m = co
    m.params.set_param(PARAM + "staff_advance", False)
    mv = m.cash_out(m.shift(), "staff_advance", 400.0, approve=True, employee_id=m.cashier2_emp.id)
    assert mv.sudo().posting_state == "pending"
    m.params.set_param(PARAM + "staff_advance", m.acc.adv.code)
    Movement = m.env["fix.cash.movement"]
    Movement._cron_retry_movement_postings()
    Movement._cron_retry_movement_postings()
    assert _balance(m.env, m.acc.adv) == 400.0


def test_the_posting_outcome_cannot_be_typed(co):
    m = co
    mv = m.cash_out(m.shift(), "petty_expense", 50.0)
    for vals in ({"posting_state": "pending"}, {"move_id": False}, {"debit_account_id": False}):
        with pytest.raises(REFUSED), m.env.cr.savepoint():
            mv.with_user(m.manager).write(vals)
    with pytest.raises(REFUSED), m.env.cr.savepoint():
        mv.with_user(m.plain).action_retry_posting()
    assert mv.sudo().posting_state == "posted"


def test_a_field_cash_shortage_books_payroll_recovery_once(co):
    """D20: the technician handed in less than the drawer took on his
    declaration: the shortfall leaves the drawer as a payroll recovery."""
    m = co
    s = m.shift()
    tech = m.cashier2_emp
    mv = s.with_user(m.cashier)._fix_book_field_cash_shortage(tech, 150.0, "FCR/T-1")
    again = s.with_user(m.cashier)._fix_book_field_cash_shortage(tech, 150.0, "FCR/T-1")
    assert again == mv
    rec = mv.sudo()
    assert (rec.movement_type, rec.state, rec.employee_id) == ("field_shortage", "posted", tech)
    move = rec.move_id
    assert _lines(move) == {m.acc.payroll.code: (150.0, 0.0), m.acc.drawer.code: (0.0, 150.0)}
    payroll_line = move.line_ids.filtered(lambda ln: ln.account_id == m.acc.payroll)
    assert payroll_line.partner_id == tech.work_contact_id
    s.invalidate_recordset()
    assert s.sudo().cash_advances == 150.0 and s.sudo().expected_closing == 4850.0
    # a field shortage is never typed as a cash-out
    with pytest.raises(REFUSED), m.env.cr.savepoint():
        m.env["fix.cash.movement"].with_user(m.cashier).create(
            {"shift_id": s.id, "movement_type": "field_shortage", "amount": 10.0, "reason": "x"}
        )


def test_the_deposit_banks_the_safe(co):
    """D2: the M50 deposit may take cash from the safe: Dr cash-in-transit /
    Cr Cash in Safe, never more than the safe holds."""
    m = co
    env = m.env
    if "fix.cash.deposit" not in env:
        pytest.skip("cd_cash_position is not installed")
    s = m.shift()
    m.cash_out(s, "safe_drop", 3000.0, reason="safe drop")
    bank = env["account.account"].create(
        {
            "code": "CO%sBNK" % m.acc.drawer.code[-8:],
            "name": "Deposit bank",
            "account_type": "asset_cash",
        }
    )
    journal = env["account.journal"].create(
        {
            "name": "Deposit bank %s" % bank.code,
            "code": "D%s" % bank.code[-4:],
            "type": "bank",
            "default_account_id": bank.id,
        }
    )
    accountant = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "cash-out accountant",
                "login": "a02r2.co.acct.%s@test" % bank.code,
                "group_ids": [
                    (
                        6,
                        0,
                        [env.ref("base.group_user").id, env.ref("account.group_account_user").id],
                    )
                ],
            }
        )
    )
    Deposit = env["fix.cash.deposit"].with_user(accountant)
    too_much = Deposit.create(
        {
            "branch_id": m.branch.id,
            "journal_id": journal.id,
            "amount": 3500.0,
            "cash_source": "safe",
        }
    )
    with pytest.raises(UserError, match="safe"), env.cr.savepoint():
        too_much.action_dispatch()
    dep = Deposit.create(
        {
            "branch_id": m.branch.id,
            "journal_id": journal.id,
            "amount": 3000.0,
            "cash_source": "safe",
        }
    )
    dep.action_dispatch()
    dep.invalidate_recordset()
    assert dep.state == "in_transit"
    assert _lines(dep.sudo().dispatch_move_id) == {
        m.acc.cit.code: (3000.0, 0.0),
        m.acc.safe.code: (0.0, 3000.0),
    }
    assert _balance(env, m.acc.safe) == 0.0
    # the safe is empty now
    more = Deposit.create(
        {"branch_id": m.branch.id, "journal_id": journal.id, "amount": 1.0, "cash_source": "safe"}
    )
    with pytest.raises(UserError), env.cr.savepoint():
        more.action_dispatch()
