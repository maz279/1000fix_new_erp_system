"""cd_front_desk_finance — the counter sale reaches the books (E2E2 flow 2).

On a copy of fix_real (11 Nov 2026) three counter sales produced no GL entry,
no stock movement and no Mushak register row; the M50 deposit then credited
the drawer cash account for takings never debited to it. These tests drive
the front desk exactly as the counter does (a cashier, a branch manager
deciding refunds from the M63 inbox) and read what reached the ledger, the
VAT register and the M15 stock ledger.

The cashier holds no accounting role throughout: the posting runs as the
system on her behalf. ``odoo_env`` rolls every test back.
"""

# ruff: noqa: F811  (the P0 suite's fixtures are imported and used as parameters)
import itertools
from decimal import ROUND_HALF_UP, Decimal
from types import SimpleNamespace

import pytest
from odoo import fields
from odoo.addons.cd_front_desk.tests.test_a02_p0_m04 import (  # noqa: F401
    GUARD,
    _refused,
    m04,
)
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox
from odoo.exceptions import UserError

pytestmark = [pytest.mark.financial, pytest.mark.tax]

_SEQ = itertools.count(1)
PARAM = "cd_front_desk_finance.account_code."
CENT = Decimal("0.01")


def _balance(env, account):
    env.flush_all()
    lines = env["account.move.line"].search(
        [("account_id", "=", account.id), ("parent_state", "=", "posted")]
    )
    return round(sum(lines.mapped("balance")), 2)


def _lines(move):
    """{account code: (debit, credit)} of a move."""
    out = {}
    for line in move.line_ids:
        dr, cr = out.get(line.account_id.code, (0.0, 0.0))
        out[line.account_id.code] = (round(dr + line.debit, 2), round(cr + line.credit, 2))
    return out


def _moves_on(env, *accounts):
    env.flush_all()
    return (
        env["account.move.line"]
        .search([("account_id", "in", [a.id for a in accounts]), ("parent_state", "=", "posted")])
        .move_id
    )


def _register(env, sale, row_type="invoice"):
    return (
        env["fix.mushak.register"]
        .sudo()
        .search([("invoice_ref", "like", sale.name), ("row_type", "=", row_type)])
    )


def _suspense(env, sale):
    return (
        env["fix.inventory.valuation.suspense"]
        .sudo()
        .search([("source_ref", "like", sale.name)], order="id")
    )


@pytest.fixture
def fin(m04):
    """The M04 world plus the books: accounts named by the bridge's parameters,
    a spare part sold over the counter with stock at the branch."""
    m = m04
    env = m.env
    n = next(_SEQ)
    params = env["ir.config_parameter"].sudo()

    def account(key, kind, name):
        return env["account.account"].create(
            {
                "code": "CFD%d%s" % (n, key),
                "name": "Counter %s %d" % (name, n),
                "account_type": kind,
            }
        )

    acc = SimpleNamespace(
        drawer=account("CSH", "asset_cash", "drawer cash"),
        mfs=account("MFS", "asset_current", "MFS clearing"),
        card=account("CRD", "asset_current", "card clearing"),
        parts=account("PRT", "income", "parts revenue"),
        labour=account("LAB", "income", "labour revenue"),
        vat=account("VAT", "liability_current", "VAT output"),
        cit=account("CIT", "asset_current", "cash in transit"),
        equity=account("EQT", "equity", "opening float"),
    )
    # the drawer's account is the one the M50 deposit credits (branch_cash)
    params.set_param("cd_cash_position.account_code.branch_cash", acc.drawer.code)
    params.set_param("cd_cash_position.account_code.cash_in_transit", acc.cit.code)
    params.set_param(PARAM + "parts_revenue", acc.parts.code)
    params.set_param(PARAM + "labour_revenue", acc.labour.code)
    params.set_param(PARAM + "mfs_clearing", acc.mfs.code)
    params.set_param(PARAM + "card_clearing", acc.card.code)
    # output VAT is the account the AR invoice path credits
    params.set_param("cd_billing_engine.account_code.vat_output", acc.vat.code)

    loc = env["fix.stock.location"].create(
        {
            "name": "Counter stock %d" % n,
            "code": "CFDL%d" % n,
            "location_type": "branch",
            "branch_id": m.branch.id,
            "operating_unit_id": m.ou.id,
        }
    )
    part = env["fix.spare.part"].create(
        {
            "name": "Counter RAM %d" % n,
            "part_number": "CFDP-%d" % n,
            "unit_cost": 600.0,
            "product_id": m.product.id,
        }
    )
    env["fix.stock.onhand"]._apply(part, loc, "owned", 10.0, 600.0)
    service = env["product.product"].create(
        {"name": "Counter screen fitting %d" % n, "list_price": 500.0, "type": "service"}
    )

    def onhand(location=None, status="unrestricted"):
        env.invalidate_all()
        row = env["fix.stock.onhand"]._bucket(part, location or loc, "owned", status)
        return row.qty if row else 0.0

    def confirmed(price=1150.0, method="cash", shift=None, product=None, trx=None, **kw):
        sale = m.sale(shift, price=price, method=method)
        vals = dict(kw)
        if product:
            vals["product_id"] = product.id
        if trx:
            vals["transaction_ref"] = trx
        if vals:
            sale.write(vals)
        sale.action_confirm()
        sale.invalidate_recordset()
        return sale

    def refund(sale, reason="customer_cancelled"):
        sale.with_user(m.cashier).action_request_refund(reason=reason)
        approve_via_inbox(sale, m.manager)
        sale.invalidate_recordset()
        return sale

    m.acc, m.loc, m.part, m.service = acc, loc, part, service
    m.onhand, m.confirmed, m.refund, m.params = onhand, confirmed, refund, params
    return m


# ===================================================================== sale
def test_a_cash_sale_posts_revenue_vat_drawer_and_stock(fin):
    """The E2E2 sale: RAM 1,150.00 cash. Dr drawer / Cr parts revenue / Cr VAT,
    the 6.3 in the statutory register, one unit out of the branch stock."""
    m = fin
    assert not m.cashier.has_group("account.group_account_user")
    assert not m.cashier.has_group("account.group_account_manager")
    s = m.shift()
    sale = m.confirmed(1150.0, "cash", shift=s)
    env = m.env

    rows = _register(env, sale)
    assert len(rows) == 1, "no Mushak 6.3 register row for the counter sale"
    row = rows
    assert (row.taxable_amount, row.vat_amount, row.total_payable) == (1000.0, 150.0, 1150.0)
    assert row.supplier_bin and row.mushak_no and "-" in row.mushak_no
    assert "standard_15 @ 15%" in (row.treatment_summary or "")
    assert row.vat_line == "standard_15"

    moves = _moves_on(env, m.acc.drawer, m.acc.parts, m.acc.vat)
    assert len(moves) == 1, "the sale did not reach the GL exactly once"
    move = moves
    assert _lines(move) == {
        m.acc.drawer.code: (1150.0, 0.0),
        m.acc.parts.code: (0.0, 1000.0),
        m.acc.vat.code: (0.0, 150.0),
    }
    assert row.posted and row.move_id == move
    assert move.date == row.invoice_date

    # posted through M19 as the system, on behalf of the cashier
    log = env["fix.journal.posting.log"].sudo().search([("move_id", "=", move.id)])
    assert log.source == "counter_sale" and log.source_ref == sale.name
    assert log.requested_by == m.cashier

    # the part left the branch ledger and wrote its valuation suspense row
    assert m.onhand() == 9.0
    susp = _suspense(env, sale)
    assert len(susp) == 1
    assert (susp.entry_type, susp.quantity, susp.total_valuation, susp.status) == (
        "counter_sale",
        -1.0,
        -600.0,
        "pending_gl_cutover",
    )
    assert susp._fix_stock_effect_total() == -600.0

    sale = sale.sudo()
    assert sale.posting_state == "posted" and not sale.posting_note
    assert (sale.mushak_id, sale.gl_move_id) == (row, move)
    assert sale.mushak_no == row.mushak_no
    assert (sale.stock_state, sale.stock_location_id) == ("issued", m.loc)
    # the drawer controls are unchanged: the cash is in the shift's takings
    assert s.sudo().cash_payments == 1150.0


def test_mfs_and_card_sales_debit_their_clearing_accounts(fin):
    m = fin
    s = m.shift()
    bkash = m.confirmed(2500.0, "bkash", trx="BKX9K2L7QP")
    nagad = m.confirmed(1150.0, "nagad", trx="NGD-0001")
    card = m.confirmed(1150.0, "card", trx="POS-SLIP-77")
    env = m.env
    assert _balance(env, m.acc.mfs) == 3650.0
    assert _balance(env, m.acc.card) == 1150.0
    # none of it is drawer cash, in the shift or in the GL
    assert _balance(env, m.acc.drawer) == 0.0
    assert s.sudo().cash_payments == 0.0
    assert _balance(env, m.acc.parts) == -4173.91  # 2,173.91 + 1,000 + 1,000
    assert _balance(env, m.acc.vat) == -626.09  # 326.09 + 150 + 150
    for sale in (bkash, nagad, card):
        assert sale.sudo().posting_state == "posted"
    # the bKash TrxID control still holds, and nothing posts for a refused confirm
    blank = m.sale(None, price=1150.0, method="bkash")
    with _refused(env, UserError, "transaction reference"):
        blank.action_confirm()
    assert not _register(env, blank) and blank.sudo().posting_state == "none"


def test_a_service_line_credits_labour_revenue_and_moves_no_stock(fin):
    m = fin
    m.shift()
    sale = m.confirmed(575.0, "cash", product=m.service)
    env = m.env
    assert _balance(env, m.acc.labour) == -500.0
    assert _balance(env, m.acc.parts) == 0.0
    assert _balance(env, m.acc.vat) == -75.0
    assert sale.sudo().stock_state == "not_required"
    assert sale.sudo().posting_state == "posted"
    assert m.onhand() == 10.0


def _gap_total():
    """A VAT-inclusive total no taxable value reaches exactly at 15%."""
    for cents in range(100000, 120000):
        total = Decimal(cents) / 100
        net = (total / Decimal("1.15")).quantize(CENT, ROUND_HALF_UP)
        if not any(
            n + (n * Decimal("0.15")).quantize(CENT, ROUND_HALF_UP) == total
            for n in (net - CENT, net, net + CENT)
        ):
            return float(total)
    raise AssertionError("no gap total found")


@pytest.mark.parametrize("price", [2500.0, 1150.0, "gap"])
def test_the_inclusive_price_splits_by_the_m51_rate_and_ties_to_the_cash(fin, price):
    m = fin
    m.shift()
    total = _gap_total() if price == "gap" else price
    sale = m.confirmed(total, "cash").sudo()
    row = _register(m.env, sale)
    assert len(row) == 1
    assert round(row.taxable_amount + row.vat_amount, 2) == total == row.total_payable
    # the VAT is the 15% the Tax Rate Master holds, to the paisa
    assert abs(row.vat_amount - round(row.taxable_amount * 0.15, 2)) <= 0.011
    if price == 2500.0:
        assert (row.taxable_amount, row.vat_amount) == (2173.91, 326.09)
    assert (sale.vat_taxable_amount, sale.vat_output_amount) == (
        row.taxable_amount,
        row.vat_amount,
    )
    assert _lines(sale.gl_move_id)[m.acc.drawer.code] == (total, 0.0)


def test_a_sale_posts_once_however_often_it_is_retried(fin):
    m = fin
    m.shift()
    sale = m.confirmed(1150.0, "cash")
    env = m.env
    sale.with_user(m.cashier).action_retry_posting()
    sale.sudo().action_retry_posting()
    env["fix.counter.sale"]._cron_retry_counter_postings()
    assert len(_moves_on(env, m.acc.drawer)) == 1
    assert len(_register(env, sale)) == 1
    assert len(_suspense(env, sale)) == 1
    assert m.onhand() == 9.0
    # the posting outcome is the system's: nobody types it
    for vals in ({"posting_state": "pending"}, {"gl_move_id": False}, {"stock_state": "pending"}):
        with _refused(env, UserError, GUARD):
            sale.with_user(m.cashier).write(vals)
    # a user without a front-desk or finance role cannot drive the posting
    with _refused(env, UserError, "retry"):
        sale.with_user(m.plain).action_retry_posting()


# ======================================================== fail closed, not blocking
def test_an_unresolved_account_leaves_the_sale_pending_until_configured(fin):
    m = fin
    m.params.set_param(PARAM + "mfs_clearing", "NOSUCH9")
    sale = m.confirmed(1150.0, "bkash", trx="BKX-PENDING-1")
    env = m.env
    sale = sale.sudo()
    # the counter is not blocked: the sale is confirmed and its 6.3 issued
    assert sale.state == "confirmed"
    assert sale.posting_state == "pending"
    assert PARAM + "mfs_clearing" in (sale.posting_note or "")
    assert len(_register(env, sale)) == 1 and not _register(env, sale).posted
    assert not sale.gl_move_id
    assert _balance(env, m.acc.mfs) == 0.0 and _balance(env, m.acc.parts) == 0.0
    # the stock leg does not wait for the GL
    assert sale.stock_state == "issued" and m.onhand() == 9.0

    # still unconfigured: the hourly job changes nothing and posts nothing
    env["fix.counter.sale"]._cron_retry_counter_postings()
    sale.invalidate_recordset()
    assert sale.posting_state == "pending" and not sale.gl_move_id

    # configured: the job posts it, once, and marks the 6.3 posted with it
    m.params.set_param(PARAM + "mfs_clearing", m.acc.mfs.code)
    env["fix.counter.sale"]._cron_retry_counter_postings()
    env["fix.counter.sale"]._cron_retry_counter_postings()
    sale.invalidate_recordset()
    assert sale.posting_state == "posted" and not sale.posting_note
    assert len(_moves_on(env, m.acc.mfs)) == 1
    assert _balance(env, m.acc.mfs) == 1150.0
    assert _register(env, sale).posted and _register(env, sale).move_id == sale.gl_move_id
    assert m.onhand() == 9.0 and len(_suspense(env, sale)) == 1


def test_an_unknown_issue_location_keeps_the_stock_leg_pending(fin):
    """Two branch locations hold the part: the bridge does not guess."""
    m = fin
    env = m.env
    other = env["fix.stock.location"].create(
        {
            "name": "Counter warranty stock",
            "code": "CFDW%d" % m.loc.id,
            "location_type": "branch",
            "branch_id": m.branch.id,
            "operating_unit_id": m.ou.id,
        }
    )
    env["fix.stock.onhand"]._apply(m.part, other, "owned", 5.0, 600.0)
    m.shift()
    sale = m.confirmed(1150.0, "cash").sudo()
    assert sale.posting_state == "pending" and sale.stock_state == "pending"
    assert "Issue From Location" in (sale.posting_note or "")
    assert sale.gl_move_id and sale.mushak_id  # money and VAT are not held up
    assert m.onhand() == 10.0 and m.onhand(other) == 5.0
    # the cashier names the location and retries
    sale.with_user(m.cashier).write({"stock_location_id": other.id})
    sale.with_user(m.cashier).action_retry_posting()
    sale.invalidate_recordset()
    assert sale.posting_state == "posted" and sale.stock_state == "issued"
    assert m.onhand(other) == 4.0 and m.onhand() == 10.0
    # once issued, where it came from is history
    with _refused(env, UserError, "issued"):
        sale.with_user(m.cashier).write({"stock_location_id": m.loc.id})


def test_the_branch_counter_location_is_the_default_issue_location(fin):
    m = fin
    env = m.env
    other = env["fix.stock.location"].create(
        {
            "name": "Counter shelf",
            "code": "CFDS%d" % m.loc.id,
            "location_type": "branch",
            "branch_id": m.branch.id,
            "operating_unit_id": m.ou.id,
        }
    )
    env["fix.stock.onhand"]._apply(m.part, other, "owned", 3.0, 600.0)
    m.branch.write({"counter_stock_location_id": other.id})
    m.shift()
    sale = m.confirmed(1150.0, "cash").sudo()
    assert sale.posting_state == "posted" and sale.stock_location_id == other
    assert m.onhand(other) == 2.0 and m.onhand() == 10.0


# ================================================================== refunds
def test_a_refund_reverses_the_gl_the_vat_and_the_stock(fin):
    m = fin
    s = m.shift()
    sale = m.confirmed(1150.0, "cash", shift=s)
    env = m.env
    m.refund(sale)
    sale = sale.sudo()
    assert sale.state == "refunded" and sale.posting_state == "reversed"
    assert not sale.posting_note

    note = _register(env, sale, "credit_note")
    assert len(note) == 1
    assert note.original_id == sale.mushak_id and note == sale.mushak_note_id
    assert (note.taxable_amount, note.vat_amount, note.total_payable) == (-1000.0, -150.0, -1150.0)
    assert note.posted and note.move_id == sale.gl_reversal_move_id

    assert _lines(sale.gl_reversal_move_id) == {
        m.acc.drawer.code: (0.0, 1150.0),
        m.acc.parts.code: (1000.0, 0.0),
        m.acc.vat.code: (150.0, 0.0),
    }
    for account in (m.acc.drawer, m.acc.parts, m.acc.vat):
        assert _balance(env, account) == 0.0
    # the drawer paid the refund, as before
    assert s.sudo().cash_refunds == 1150.0

    assert m.onhand() == 10.0 and sale.stock_state == "returned"
    susp = _suspense(env, sale)
    assert [(r.quantity, r.total_valuation) for r in susp] == [(-1.0, -600.0), (1.0, 600.0)]
    assert susp._fix_stock_effect_total() == 0.0
    # a reversed sale is final: a retry posts nothing more
    sale.action_retry_posting()
    assert len(_moves_on(env, m.acc.drawer)) == 2
    assert len(_register(env, sale, "credit_note")) == 1


def test_a_defective_return_goes_to_quarantine(fin):
    m = fin
    m.shift()
    sale = m.confirmed(1150.0, "cash")
    m.refund(sale, reason="defective: port loose")
    assert m.onhand() == 9.0
    assert m.onhand(status="quarantine") == 1.0
    assert sale.sudo().posting_state == "reversed"


def test_a_refund_of_a_pending_sale_reverses_only_what_was_posted(fin):
    m = fin
    m.params.set_param(PARAM + "parts_revenue", "NOSUCH9")
    m.shift()
    sale = m.confirmed(1150.0, "cash").sudo()
    assert sale.posting_state == "pending" and sale.mushak_id and not sale.gl_move_id
    m.refund(sale)
    env = m.env
    assert sale.posting_state == "reversed"
    # the 6.3 was issued, so it is credited; the GL never moved, so nothing mirrors
    assert len(_register(env, sale, "credit_note")) == 1
    assert not sale.gl_move_id and not sale.gl_reversal_move_id
    assert _balance(env, m.acc.drawer) == 0.0
    assert m.onhand() == 10.0
    # configuring the account later does not post a sale that was refunded
    m.params.set_param(PARAM + "parts_revenue", m.acc.parts.code)
    env["fix.counter.sale"]._cron_retry_counter_postings()
    sale.invalidate_recordset()
    assert not sale.gl_move_id and _balance(env, m.acc.drawer) == 0.0


# ============================================================ the M50 deposit
def test_the_drawer_cash_account_nets_to_float_plus_takings_less_deposit(fin):
    """E2E2 c28: the deposit's Cr drawer is now matched by the sales' Dr."""
    from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

    m = fin
    env = m.env
    float_ = 5000.0
    # the float is cash already in the drawer account (the opening balance)
    post_with_dimensions(
        env,
        {
            "journal_id": env["account.journal"]
            .search([("type", "=", "general"), ("company_id", "=", env.company.id)], limit=1)
            .id,
            "date": fields.Date.today(),
            "ref": "Counter float",
            "line_ids": [
                (0, 0, {"account_id": m.acc.drawer.id, "debit": float_, "credit": 0.0}),
                (0, 0, {"account_id": m.acc.equity.id, "debit": 0.0, "credit": float_}),
            ],
        },
        {},
        source="api",
    )
    s = m.shift(opening=float_)
    m.confirmed(2500.0, "cash", shift=s)
    m.confirmed(2500.0, "bkash", trx="BKX9K2L7QP")
    pen = m.confirmed(1150.0, "cash", shift=s)
    m.refund(pen)
    shift = s.sudo()
    takings = shift.cash_payments - shift.cash_refunds
    assert takings == 2500.0
    assert _balance(env, m.acc.drawer) == float_ + takings

    s.action_close_shift()
    m.count(s, d1000=7, d500=1)  # 7,500.00 = float + takings, no variance
    s.action_confirm_closed()
    assert shift.closing_counted == float_ + takings

    bank = env["account.journal"].create(
        {"name": "Counter deposit bank %d" % s.id, "type": "bank", "code": "CFB%d" % (s.id % 1000)}
    )
    Deposit = env["fix.cash.deposit"]
    deposit = Deposit.create(
        {
            "operating_unit_id": m.ou.id,
            "branch_id": m.branch.id,
            "journal_id": bank.id,
            "business_date": shift.shift_date,
            "amount": shift.closing_counted - shift.opening_float,
            "carrier": Deposit._fields["carrier"].selection[0][0],
            "slip_no": "CFD-SLIP-%d" % s.id,
        }
    )
    deposit.action_dispatch()
    assert _lines(deposit.dispatch_move_id)[m.acc.drawer.code] == (0.0, 2500.0)
    # float + takings - deposit: the drawer account is back at its float
    assert _balance(env, m.acc.drawer) == float_ + takings - deposit.amount == float_
    assert _balance(env, m.acc.cit) == 2500.0


# ================================================ fallback to the estate's accounts
def test_without_parameters_the_estate_accounts_are_used(fin):
    """No cd_front_desk_finance key: revenue and VAT are the AR invoice's
    accounts, the drawer is the billing engine's cash account — on the
    statutory chart, so the MD-035 dimension rules apply."""
    m = fin
    env = m.env
    for key in (
        "cd_cash_position.account_code.branch_cash",
        "cd_billing_engine.account_code.vat_output",
        PARAM + "parts_revenue",
    ):
        m.params.set_param(key, False)  # unset
    m.shift()
    sale = m.confirmed(1150.0, "cash").sudo()
    assert sale.posting_state == "posted", sale.posting_note
    from odoo.addons.cd_billing_engine.models.fix_ar_engine import _ar_account

    company = env.company
    lines = _lines(sale.gl_move_id)
    assert lines[_ar_account(env, company, "cash").code] == (1150.0, 0.0)
    assert lines[_ar_account(env, company, "revenue").code] == (0.0, 1000.0)
    assert lines[_ar_account(env, company, "vat_output").code] == (0.0, 150.0)
    # every line carries the branch (COA-03)
    assert sale.revenue_account_id == _ar_account(env, company, "revenue")
