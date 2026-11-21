# A05 ERP remediation, stream S6 (integration wiring), M13 side, 21 Nov 2026.
#
#   1a  The deposit refund instruction (M50) carries the booking branch and
#       its unit; a card deposit refunds to the card (method "card", the
#       collection's card reference); the journal is M50's to pre-fill.
#   1b  A rental invoice defers its hire over the service period
#       (_fix_defer_revenue + service_period_start/_end) and releases it
#       straight-line by day.
#   1c  Retirement opens the M49 disposal of the route's kind through S4's
#       _fix_open_disposal (transfer_resale / recycle, ewaste_route False);
#       the M14 intake's carrying value is exactly what M49 debits to
#       refurbished stock; a disposal that would post another value is
#       refused; a unit with no M49 asset keeps the old path, with a note.
#   1d  The fleet unit's book value is M49's _fix_book_value() when linked.
# Live ORM as non-admin users, rolled back by odoo_env.
import json
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta
from odoo.addons.cd_fixed_asset_ext.models.fix_asset_common import PARAM_RESALE_STOCK
from odoo.addons.cd_fixed_asset_ext.tests.test_a08_m49_controls import (
    Ctx,
    _approve,
    balance,
    dep_run,
    seam_asset,
)
from odoo.addons.cd_rental_asset.tests import test_a05_m13_controls as ctl
from odoo.addons.cd_rental_asset.tests.conftest import TEST_ACCOUNTS
from odoo.addons.cd_rental_asset.tests.test_a05_m13_controls import (
    REFUSED,
    close,
    inbox_approve,
    ledger,
    report,
    res,
    sign,
)
from odoo.exceptions import UserError

c = ctl.c

pytestmark = [pytest.mark.financial]

CARD_REF = "RRN-A05S6-000123"


# ------------------------------------------------------------------ helpers
def _walk_card(c, r, reference=CARD_REF):
    sign(c, r)
    r.action_reserve(method="card", reference=reference)
    report(c, r, "pre_delivery", r.env.user)
    r.action_deliver()
    r.action_activate()
    r.action_return()
    report(c, r, "post_return", r.env.user)
    r.action_assess_damage()
    return r


def _m49(c):
    """An M49 world in the rental fixture's company: a category with its
    accounts and journal, the refurbished-stock account parameter, and the
    accountant / approver roles the disposal workflow needs."""
    env = c.env
    m = Ctx(env=env, co=env.company, ou=c.ou, today=c.today)
    m.cenv = env(context=dict(env.context, allowed_company_ids=env.company.ids))
    Account = m.cenv["account.account"]

    def acc(code, name, kind):
        return Account.create(
            {
                "code": "A5S6%s" % code,
                "name": "A05S6 %s" % name,
                "account_type": kind,
                "company_ids": [(6, 0, env.company.ids)],
            }
        )

    m.a = {
        "asset": acc("01", "Rental fleet cost", "asset_fixed"),
        "accum": acc("02", "Rental fleet accumulated depreciation", "asset_fixed"),
        "expense": acc("03", "Depreciation", "expense_depreciation"),
        "gain": acc("07", "Gain on disposal", "income_other"),
        "loss": acc("08", "Loss on disposal", "expense"),
        "payable": acc("13", "Trade payables", "liability_current"),
        "stock": acc("20", "Stock of Inventory - Refurbished", "asset_current"),
    }
    env["ir.config_parameter"].sudo().set_param(PARAM_RESALE_STOCK, m.a["stock"].code)
    m.journal = m.cenv["account.journal"].create(
        {"name": "A05S6 Assets", "code": "A5S6", "type": "general", "company_id": env.company.id}
    )
    m.cat = m.cenv["fix.asset.category"].create(
        {
            "company_id": env.company.id,
            "journal_id": m.journal.id,
            "asset_account_id": m.a["asset"].id,
            "accumulated_account_id": m.a["accum"].id,
            "expense_account_id": m.a["expense"].id,
            "gain_account_id": m.a["gain"].id,
            "loss_account_id": m.a["loss"].id,
            "code": "A5S6RF",
            "name": "A05S6 Rental fleet",
            "useful_life_months": 36,
        }
    )

    def user(login, *groups):
        gids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
        return (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": login,
                    "login": "a05s6.%s@a05.test" % login,
                    "group_ids": [(6, 0, gids)],
                    "assigned_operating_unit_ids": [(6, 0, c.ou.ids)],
                    "default_operating_unit_id": c.ou.id,
                }
            )
        )

    acc_user, mgr = "account.group_account_user", "account.group_account_manager"
    m.acc1 = user("acc1", acc_user)
    m.acc2 = user("acc2", acc_user)
    tier = "cd_entity_config.group_dofa_tier_%d"
    m.tiers = {"tier_%d" % n: user("t%d" % n, mgr, tier % n) for n in (2, 3, 4, 5)}
    return m


def _fleet_asset(c, m, gross=36000.0):
    """The rental fixture's unit, put on the M49 register (a posted
    acquisition on the asset account, activated by an accountant)."""
    purchase = (c.today - relativedelta(months=2)).replace(day=1)
    fa = seam_asset(m, gross=gross, purchase=purchase, cat=m.cat, life=36, name="A05S6 camera")
    c.asset.write({"fixed_asset_id": fa.id, "category": "tool"})
    return fa


def _retire(c, route="resale", weight=0.0):
    vals = {"asset_id": c.asset.id, "route": route, "reason": "end of life: sensor failure"}
    if weight:
        vals["weight_kg"] = weight
    ret = c.env["fix.rental.retirement"].with_user(c.clerk).create(vals)
    ret.action_request_approval(justification="end of life: sensor failure")
    inbox_approve(ret, c.csh)
    inbox_approve(ret, c.cfo)
    ret.action_retire()
    return ret


def _post_disposal(m, disposal):
    disposal.with_user(m.acc1).action_submit()
    if disposal.state == "submitted":
        _approve(disposal, m.tiers[disposal.dofa_tier_required])
    disposal.with_user(m.acc2).action_post()
    return disposal


def _retired_event(c, asset):
    out = (
        c.env["fix.event.outbox"]
        .sudo()
        .search(
            [("event_type", "=", "rental.asset_retired"), ("aggregate_id", "=", asset.id)],
            order="id desc",
            limit=1,
        )
    )
    assert out, "rental.asset_retired was not published"
    return {
        "aggregate": "fix.rental.asset",
        "aggregate_id": asset.id,
        "payload": json.loads(out.payload),
    }


# ============================================================ 1a deposit refund
def test_card_deposit_refunds_to_the_card_on_the_booking_branch(c):
    r = _walk_card(c, res(c))
    collect = ledger(c, r).filtered(lambda d: d.kind == "collect")
    assert collect.method == "card" and collect.reference == CARD_REF
    assert collect.gl_state == "posted", collect.gl_note
    close(c, r)
    refund = ledger(c, r).filtered(lambda d: d.kind == "refund")
    assert refund.method == "card" and refund.amount == 5000
    pay = refund.payment_execution_id.sudo()
    assert pay.method == "card" and pay.original_payment_ref == CARD_REF
    assert pay.branch_id == c.branch and pay.operating_unit_id == c.branch.operating_unit_id
    # the journal is M50's pre-fill by method (I3), never the first bank journal
    Exec = c.env["fix.payment.execution"].sudo()
    assert not pay.journal_id or Exec._fix_journal_fits(pay.journal_id, "card")


def test_card_refund_without_a_card_reference_is_refused(c):
    r = res(c)
    sign(c, r)
    r.action_reserve(method="card", reference=CARD_REF)
    collect = ledger(c, r).filtered(lambda d: d.kind == "collect")
    # a legacy card collection that never carried its reference
    collect.sudo()._guarded().write({"reference": False})
    with pytest.raises(UserError, match="card payment reference"):
        r.with_user(c.clerk2).action_cancel()
    assert not ledger(c, r).filtered(lambda d: d.kind == "refund").payment_execution_id


def test_cash_refund_carries_the_branch_and_a_cash_journal_or_none(c):
    r = ctl.walk(c, res(c), "action_assess_damage")
    close(c, r)
    pay = ledger(c, r).filtered(lambda d: d.kind == "refund").payment_execution_id.sudo()
    assert pay.method == "cash" and pay.branch_id == c.branch
    assert not pay.journal_id or pay.journal_id.type == "cash"


def test_a_paid_refund_is_posted_not_left_queued(c):
    """A05 e2e walk defect 2: treasury paid the refund (payment.executed) but
    the row stayed refund_queued and the reports kept the deposit as held."""
    r = ctl.walk(c, res(c), "action_assess_damage")
    close(c, r)
    refund = ledger(c, r).filtered(lambda d: d.kind == "refund")
    pay = refund.payment_execution_id.sudo()
    assert refund.gl_state == "refund_queued"
    Deposit = c.env["fix.rental.deposit"].sudo()
    event = {"aggregate_id": pay.id}
    # not executed yet: nothing moves
    assert Deposit.consume_payment_executed(event) is False
    pay.write({"state": "executed", "confirmation_source": "cash_voucher"})
    assert Deposit.consume_payment_executed(event) is True
    refund.invalidate_recordset()
    assert refund.gl_state == "posted"
    # a replay moves nothing; only the relay may call it
    assert Deposit.consume_payment_executed(event) is False
    with pytest.raises(REFUSED):
        c.env["fix.rental.deposit"].with_user(c.clerk).consume_payment_executed(event)


def _m13_deposit_row(c, r):
    from odoo.addons.cd_p03_portal.controllers.a05 import m13

    pack = m13.deposit_reconciliation(c.env(user=c.clerk.id))
    rows = [row for row in pack["rows"] if row["rental"] == r.name]
    assert len(rows) == 1, pack["rows"]
    return rows[0], m13._held(ledger(c, r))


def test_a_refund_paid_on_a_cash_voucher_reaches_the_ledger_and_the_m13_reports(c):
    """A05 e2e walk defect 2, the production path: treasury prepares and
    releases the cash refund, a cashier who is not the requester pays it out
    on a cash voucher (Dr deposits held / Cr cash on the booking branch), the
    relay delivers payment.executed through the registered consumer, and the
    M13 deposit reconciliation shows the deposit refunded, not queued/held."""
    env = c.env
    params = env["ir.config_parameter"].sudo()
    params.set_param("cd_cash_position.release_single_ceiling", "1000000000")
    # the one cash journal of the company (rolled back): the refund pre-fills it
    env["account.journal"].search(
        [("company_id", "=", env.company.id), ("type", "=", "cash")]
    ).write({"active": False})
    cash = env["account.journal"].create(
        {"name": "A05 S7 Counter Cash", "type": "cash", "code": "A5S7C"}
    )
    maker = ctl._user(env, "s7maker", ["account.group_account_manager"])
    checker = ctl._user(env, "s7checker", ["account.group_account_manager"])
    cashier = ctl._user(env, "s7cashier", ["cd_front_desk.group_fd_cashier"])
    r = ctl.walk(c, res(c), "action_assess_damage")
    close(c, r)
    refund = ledger(c, r).filtered(lambda d: d.kind == "refund")
    pay = refund.payment_execution_id.sudo()
    assert refund.gl_state == "refund_queued" and pay.method == "cash"
    if pay.journal_id != cash:
        pay.write({"journal_id": cash.id})
    row, held = _m13_deposit_row(c, r)
    assert (row["refunded"], row["refund_queued"], row["outstanding"]) == (0.0, 5000.0, 5000.0)
    assert held == 5000.0
    pay.with_user(maker).action_prepare()
    pay.with_user(checker).action_release()
    assert pay.state == "sent"
    pay.with_user(cashier).action_pay_cash_voucher(received_by=c.customer.name)
    assert (pay.state, pay.confirmation_source) == ("executed", "cash_voucher")
    assert pay.move_id and pay.move_id.state == "posted"
    # the relay as production runs it, through the registered consumer
    consumer = env.ref("cd_rental_asset.consumer_payment_executed_rental_deposit")
    assert consumer.event_type == "payment.executed" and consumer.active
    env["fix.event.outbox"].sudo().cron_relay()
    refund.invalidate_recordset()
    assert refund.gl_state == "posted", refund.gl_note
    assert refund.journal_entry_id == pay.move_id
    liability = pay.move_id.line_ids.filtered(lambda ln: ln.debit)
    assert liability.account_id.code == TEST_ACCOUNTS["deposit_liability"]
    assert liability.debit == 5000.0
    row, held = _m13_deposit_row(c, r)
    assert (row["refunded"], row["refund_queued"], row["outstanding"]) == (5000.0, 0.0, 0.0)
    assert held == 0.0


# ============================================================ 1b revenue deferral
def test_three_month_rental_invoice_defers_the_hire_and_releases_it_by_day(c):
    start = c.today
    end = start + timedelta(days=89)  # 90 days, both inclusive
    r = res(c, date_from=start, date_to=end)
    ctl.walk(c, r, "action_activate")
    r.action_issue_rental_invoice()
    row = r.billing_ids.filtered(lambda b: b.kind == "rental")
    assert (row.service_date_from, row.service_date_to) == (start, end)
    inv = row.invoice_id.sudo()
    hire = inv.line_ids.filtered(lambda ln: ln.service_period_start)
    assert (hire.service_period_start, hire.service_period_end) == (start, end)
    inv.action_issue()
    assert inv.state == "issued" and inv.posted_move_id, inv.gl_note
    deferral = inv.revenue_deferral_ids
    assert len(deferral) == 1 and deferral.invoice_line_id == hire
    assert deferral.amount == pytest.approx(hire.taxable_amount, abs=0.01)
    amount = deferral.amount
    # day 1 of 90 is earned at issue; the rest is a contract liability
    assert deferral.released_amount == pytest.approx(round(amount / 90, 2), abs=0.01)
    deferral._fix_release(as_of=start + timedelta(days=29))
    assert deferral.released_amount == pytest.approx(round(amount * 30 / 90, 2), abs=0.01)
    deferral._fix_release(as_of=start + timedelta(days=59))
    assert deferral.released_amount == pytest.approx(round(amount * 60 / 90, 2), abs=0.01)
    deferral._fix_release(as_of=end)
    assert deferral.released_amount == pytest.approx(amount, abs=0.01)
    assert deferral.state == "done" and deferral.balance == 0.0
    # the releases credit the invoice's revenue account: rental income
    assert deferral.revenue_account_id.code == TEST_ACCOUNTS["rental_income"]
    released = deferral.log_ids.filtered(lambda lg: lg.kind == "release")
    assert round(sum(released.mapped("amount")), 2) == pytest.approx(amount, abs=0.01)


# ============================================================ 1c / 1d retirement
def test_book_value_is_m49s_when_the_unit_is_capitalised(c):
    m = _m49(c)
    fa = _fleet_asset(c, m)
    straight = c.asset.sudo().net_book_value
    assert c.asset.sudo()._book_value() == fa._fix_book_value() == 36000.0
    dep_run(m, fa, c.today.month, year=c.today.year)
    fa.invalidate_recordset()
    assert c.asset.sudo()._book_value() == fa._fix_book_value() < 36000.0
    assert straight  # the memo straight-line figure is not what is used


def test_resale_retirement_opens_a_transfer_to_resale_stock(c):
    m = _m49(c)
    fa = _fleet_asset(c, m)
    ret = _retire(c, "resale")
    disposal = ret.disposal_id.sudo()
    assert disposal.asset_id == fa and disposal.state == "draft"
    assert disposal.kind == "transfer_resale" and not disposal.ewaste_route
    assert (disposal.source_model, disposal.source_res_id) == ("fix.rental.asset", c.asset.id)
    assert disposal.date == ret.retired_on and c.asset.disposal_id == disposal


def test_recycle_retirement_opens_a_recycle_disposal_m18_does_not_get_twice(c):
    m = _m49(c)
    fa = _fleet_asset(c, m)
    ret = _retire(c, "recycle", weight=1.5)
    disposal = ret.disposal_id.sudo()
    assert disposal.asset_id == fa and disposal.kind == "recycle"
    # M18 receives the unit from rental.asset_retired (S3): the M49 posting
    # must not open a second collection
    assert not disposal.ewaste_route
    assert disposal.ewaste_weight_kg == 1.5


def test_retire_to_intake_carrying_value_equals_the_stock_debit(c):
    if "fix.tradein.request" not in c.env:
        pytest.skip("cd_tradein not installed")
    m = _m49(c)
    fa = _fleet_asset(c, m)
    c.asset.sudo()._guarded().write({"device_id": c.device.id})
    ret = _retire(c, "resale")
    book = ret.sudo().book_value
    assert book == fa._fix_book_value() == 36000.0
    event = _retired_event(c, c.asset)
    assert event["payload"]["book_value"] == book
    # M14's intake: the carrying value in the trade-in stock ledger, no GL
    out = c.env["fix.tradein.request"].sudo().consume_rental_asset_retired(event)
    intake = c.env["fix.tradein.request"].sudo().browse(out["id"])
    assert intake.carrying_cost == book
    transfer = intake.ledger_ids.filtered(lambda r: r.kind == "transfer_in")
    assert transfer.amount == book and not transfer.move_id
    # a replayed event (relay retry) opens no second intake, no second ledger row
    again = c.env["fix.tradein.request"].sudo().consume_rental_asset_retired(event)
    assert again["id"] == intake.id and again["created"] is False
    TI = c.env["fix.tradein.request"].sudo()
    assert TI.search_count([("rental_asset_id", "=", c.asset.id)]) == 1
    assert len(intake.ledger_ids.filtered(lambda r: r.kind == "transfer_in")) == 1
    stock = m.a["stock"]
    assert balance(m, stock) == 0.0
    # M49's posting: Dr refurbished stock at the same carrying amount
    _post_disposal(m, ret.disposal_id.sudo())
    assert ret.disposal_id.state == "posted" and ret.disposal_id.gain_loss == 0.0
    assert balance(m, stock) == intake.carrying_cost == book
    assert balance(m, m.a["asset"]) == 0.0 and balance(m, m.a["loss"]) == 0.0
    # the unit is off the register: its book value is nil, not a memo figure
    fa.invalidate_recordset()
    assert fa.state == "disposed" and c.asset.sudo()._book_value() == 0.0


def test_disposal_posting_another_value_than_the_intake_is_refused(c):
    m = _m49(c)
    fa = _fleet_asset(c, m)
    ret = _retire(c, "resale")
    disposal = ret.disposal_id.sudo()
    # finance re-dates the draft to the month end and the month's
    # depreciation posts: M49 would now debit stock with less than M14 holds
    month_end = c.today + relativedelta(day=31)
    disposal.write({"date": month_end})
    dep_run(m, fa, c.today.month, year=c.today.year)
    fa.invalidate_recordset()
    assert fa._fix_book_value() < ret.sudo().book_value
    disposal.with_user(m.acc1).action_submit()
    if disposal.state == "submitted":
        _approve(disposal, m.tiers[disposal.dofa_tier_required])
    with pytest.raises(UserError, match="handed it to M14 resale"):
        disposal.with_user(m.acc2).action_post()
    assert disposal.state == "approved" and balance(m, m.a["stock"]) == 0.0


def test_unit_off_the_register_keeps_the_old_path_with_a_note(c):
    assert not c.asset.fixed_asset_id
    c.asset.write({"category": "tool"})  # not data-bearing: no wipe gate here
    ret = _retire(c, "resale")
    assert ret.state == "retired" and not ret.disposal_id
    notes = " ".join(ret.message_ids.mapped("body"))
    assert "not on the fixed-asset register" in notes
    # owner decision D13: the books never held it, so it crosses at nil
    # (its memo value is shown, never carried into refurbished stock)
    assert ret.sudo().book_value > 0.0
    event = _retired_event(c, c.asset)
    assert event["payload"]["book_value"] == 0.0
    assert "at nil value" in notes
