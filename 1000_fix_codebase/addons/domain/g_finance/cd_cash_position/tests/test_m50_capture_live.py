# cd_cash_position: M50 capture audit (2026-11-17), the five new records on a
# real database. Every decision runs as a NON-ADMIN user holding the real
# finance role (the users of test_a08_m50_controls' fixture): acct and acct2
# are Accountants, mgr and mgr2 Accounting Administrators. Arrangement that
# is not under test (accounts, a foreign-currency journal, a past week) is
# done as superuser and says so. Everything rolls back (odoo_env).
from __future__ import annotations

from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

from . import test_a08_m50_controls as _base

# the shared fixture and helpers of the M50 control tests (same users and
# roles, same statement / gateway import paths)
c = _base.c
stmt = _base.stmt
_gw = _base._gw
_SEQ = _base._SEQ

pytestmark = [pytest.mark.financial]

REFUSED = (UserError, ValidationError, AccessError)


# ------------------------------------------------------------------ mandates
def _mandate(c, user, **kw):
    vals = {
        "journal_id": c.bank.id,
        "signatory_id": c.custodian.id,
        "signing_class": "sole",
        "limit_amount": 500000.0,
        "authority_ref": "Board resolution BR-%s" % next(_SEQ),
    }
    vals.update(kw)
    return c.env["fix.bank.mandate"].with_user(user).create(vals)


def test_mandate_is_approved_by_a_second_administrator_and_then_frozen(c):
    m = _mandate(c, c.mgr)
    m.with_user(c.mgr).action_submit()
    with pytest.raises(UserError):
        m.with_user(c.acct).action_approve()  # an accountant does not approve
    with pytest.raises(UserError):
        m.with_user(c.mgr).action_approve()  # nor the requester
    m.with_user(c.mgr2).action_approve()
    assert m.state == "active" and m.approved_by_id == c.mgr2
    with pytest.raises(UserError):
        m.with_user(c.mgr2).write({"limit_amount": 9_000_000.0})
    with pytest.raises(UserError):
        m.with_user(c.mgr2).unlink()
    assert c.custodian.name in c.bank.fix_active_signatories


def test_a_change_is_a_new_mandate_that_supersedes_and_keeps_history(c):
    old = _mandate(c, c.acct)
    old.with_user(c.acct).action_submit()
    old.with_user(c.mgr).action_approve()
    new = _mandate(c, c.acct, limit_amount=750000.0, supersedes_id=old.id)
    new.with_user(c.acct).action_submit()
    new.with_user(c.mgr).action_approve()
    assert old.state == "superseded" and old.ended_by_id == c.mgr
    assert new.state == "active"
    assert "750000.00" in c.bank.fix_active_signatories
    assert "500000.00" not in c.bank.fix_active_signatories


def test_mandate_rules_are_validated(c):
    with pytest.raises(ValidationError):
        _mandate(c, c.acct, limit_amount=0.0)
    with pytest.raises(ValidationError):
        _mandate(c, c.acct, signing_class="joint_with")
    with pytest.raises(ValidationError):
        _mandate(c, c.acct, valid_from=c.today, valid_to=c.today - timedelta(days=1))
    assert _mandate(c, c.acct, limit_amount=0.0, unlimited=True).state == "draft"


def test_mandate_state_and_stamps_cannot_be_typed(c):
    m = _mandate(c, c.acct)
    with pytest.raises(UserError):
        m.with_user(c.acct).write({"state": "active"})
    with pytest.raises(UserError):
        m.with_user(c.acct).write({"approved_by_id": c.mgr.id})
    with pytest.raises(UserError):
        m.with_user(c.mgr).action_revoke(reason="")


# ------------------------------------------------------------------ matching rules
def _rule(c, user, **kw):
    vals = {
        "name": "SMS charge %s" % next(_SEQ),
        "classification": "bank_charge",
        "direction": "debit",
        "keywords": "SMS CHG, SMS ALERT",
        "amount_max": 500.0,
        "effective_from": c.today - timedelta(days=30),
    }
    vals.update(kw)
    return c.env["fix.bank.matching.rule"].with_user(user).create(vals)


def _approved(c, **kw):
    rule = _rule(c, c.acct, **kw)
    rule.with_user(c.acct).action_submit()
    with pytest.raises(UserError):
        rule.with_user(c.acct).action_approve()
    rule.with_user(c.mgr).action_approve()
    return rule


def _set_role(c, role, account_type="income"):
    """Arrangement (superuser): a GL account for a treasury role."""
    acc = c.env["account.account"].create(
        {"code": "M50R%s" % next(_SEQ), "name": "M50 %s" % role, "account_type": account_type}
    )
    c.env["ir.config_parameter"].sudo().set_param(
        "cd_cash_position.account_code.%s" % role, acc.code
    )
    return acc


def test_an_approved_rule_books_a_bank_charge_in_auto_match(c):
    rule = _approved(c)
    lines = stmt(c, [(-115.0, "BK%s" % next(_SEQ), "SMS CHG Q3")])
    matched = c.env["fix.bank.statement.line"].with_user(c.acct2).auto_match()
    line = lines[0]
    assert matched >= 1
    assert line.match_state == "auto" and line.matched_kind == "external"
    assert line.matching_rule_id == rule and line.external_class == "bank_charge"
    move = line.external_move_id
    assert move.state == "posted"
    charge = move.line_ids.filtered(lambda ml: ml.account_id == c.acc["bank_charges"])
    assert round(charge.debit, 2) == 115.0
    assert rule.line_count == 1


def test_interest_received_and_unadvised_debits(c):
    income = _set_role(c, "interest_income")
    _approved(
        c, classification="interest_income", direction="credit", keywords="INT CR", amount_max=0.0
    )
    _approved(c, classification="unadvised", direction="debit", keywords="MISC DR", amount_max=0.0)
    interest, unknown = stmt(
        c,
        [(820.0, "IN%s" % next(_SEQ), "INT CR SAVINGS"), (-2500.0, "UN%s" % next(_SEQ), "MISC DR")],
    )
    c.env["fix.bank.statement.line"].with_user(c.acct2).auto_match()
    assert interest.matched_kind == "external" and interest.external_class == "interest_income"
    credit = interest.external_move_id.line_ids.filtered(lambda ml: ml.account_id == income)
    assert round(credit.credit, 2) == 820.0
    # an unadvised debit is flagged for the bank's advice, never booked
    assert unknown.match_state == "unmatched" and unknown.external_class == "unadvised"
    assert not unknown.external_move_id


def test_a_rule_out_of_its_band_or_direction_does_not_book(c):
    _approved(c)
    big, credit = stmt(
        c,
        [
            (-900.0, "BG%s" % next(_SEQ), "SMS CHG BULK"),
            (115.0, "CR%s" % next(_SEQ), "SMS CHG REV"),
        ],
    )
    c.env["fix.bank.statement.line"].with_user(c.acct2).auto_match()
    assert big.match_state == "unmatched" and not big.external_class
    assert credit.match_state == "unmatched" and not credit.external_class


def test_a_rule_is_frozen_once_submitted_and_changes_by_version(c):
    with pytest.raises(ValidationError):
        _rule(c, c.acct, direction="credit")  # a charge is money out
    rule = _approved(c)
    with pytest.raises(UserError):
        rule.with_user(c.mgr).write({"keywords": "ANYTHING"})
    rule.with_user(c.acct).action_new_version()
    draft = c.env["fix.bank.matching.rule"].search([("previous_id", "=", rule.id)])
    assert draft.state == "draft" and draft.version == 2
    draft.with_user(c.acct).write({"keywords": "SMS CHG, SMS FEE"})
    draft.with_user(c.acct).action_submit()
    draft.with_user(c.mgr2).action_approve()
    assert rule.state == "retired" and draft.state == "approved"
    with pytest.raises(UserError):
        rule.with_user(c.acct).write({"state": "approved"})


def test_rule_test_reports_without_booking(c):
    rule = _approved(c)
    lines = stmt(c, [(-50.0, "TS%s" % next(_SEQ), "SMS ALERT FEE")])
    rule.with_user(c.acct).action_test()
    assert rule.last_test.startswith("1 of ")
    assert lines.match_state == "unmatched"


# ------------------------------------------------------------------ settlement exceptions
def _exception_line(c):
    b = _gw(c, "TrxID,Amount,Fee,Net\nSX%s,1000.00,15.00,985.00\n" % next(_SEQ))
    b.with_user(c.acct).action_import_report()
    line = b.line_ids
    assert line.match_state == "missing_receipt"
    return line


def test_an_exception_case_has_a_named_owner_and_a_second_person_resolves_it(c):
    line = _exception_line(c)
    line.with_user(c.acct).action_open_case()
    case = line.open_case_id
    assert case.owner_id == c.acct
    assert case.exception_type == "settled_not_recorded" and case.amount == 1000.0
    assert case.name.startswith("SXC/")
    with pytest.raises(UserError):
        line.with_user(c.acct2).action_open_case()  # one open case per line
    with pytest.raises(UserError):
        case.with_user(c.acct).action_raise_with_provider()  # no provider ticket yet
    case.with_user(c.acct).write({"provider_case_ref": "BKASH-TKT-%s" % next(_SEQ)})
    case.with_user(c.acct).action_raise_with_provider()
    with pytest.raises(UserError):
        case.with_user(c.acct).action_propose(resolution="provider_corrected", note="")
    with pytest.raises(UserError):
        case.with_user(c.acct).action_propose(resolution="receipt_booked", note="TKT reply")
    case.with_user(c.mgr).action_propose(
        resolution="provider_corrected", note="Corrected report v2"
    )
    with pytest.raises(UserError):
        case.with_user(c.mgr).action_approve()  # not the proposer
    with pytest.raises(UserError):
        case.with_user(c.acct).write({"owner_id": c.acct2.id})  # frozen once proposed
    case.with_user(c.mgr2).action_approve()
    assert case.state == "resolved" and case.resolved_by_id == c.mgr2


def test_exception_stamps_cannot_be_typed(c):
    line = _exception_line(c)
    case = (
        c.env["fix.settlement.exception"]
        .with_user(c.acct)
        .create({"line_id": line.id, "owner_id": c.acct2.id})
    )
    for vals in ({"state": "resolved"}, {"resolution": "receipt_booked"}, {"amount": 1.0}):
        with pytest.raises(UserError):
            case.with_user(c.acct).write(vals)
    with pytest.raises(REFUSED):
        case.with_user(c.mgr).unlink()


# ------------------------------------------------------------------ forecast versions
def test_a_forecast_version_is_frozen_and_measured_against_actuals(c):
    v = (
        c.env["fix.cash.forecast.version"]
        .with_user(c.acct)
        .create({"scenario": "base", "assumptions": "Customers pay on terms; no new facility."})
    )
    assert v.name.startswith("CFV/") and v.generated_by_id == c.acct
    assert len(v.line_ids) == 13 and v.line_ids[0].horizon == 0
    with pytest.raises(UserError):
        v.with_user(c.acct).write({"assumptions": "rewritten after the fact"})
    with pytest.raises(UserError):
        v.line_ids[0].with_user(c.acct).write({"forecast_net": 1.0})
    with pytest.raises(REFUSED):
        v.with_user(c.mgr).unlink()
    # arrangement (superuser): make the first week one that has ended
    first = v.line_ids[0]
    first.sudo().write({"week_start": c.today - timedelta(days=14)})
    v.with_user(c.acct).action_measure()
    assert first.measured and 0.0 <= first.accuracy_pct <= 100.0
    assert v.measured_weeks == 1
    assert not v.line_ids[1].measured  # a week still running is not measured


# ------------------------------------------------------------------ FX conversions
def _usd_journal(c):
    """Arrangement (superuser): a USD account, a book rate and the exchange
    gain/loss accounts."""
    base = c.company.currency_id
    usd = c.env.ref("base.USD") if base != c.env.ref("base.USD") else c.env.ref("base.EUR")
    usd.sudo().active = True
    # 1 unit of company currency buys 1/118 of the foreign unit: 118 per unit
    c.env["res.currency.rate"].sudo().create(
        {"currency_id": usd.id, "name": c.today, "rate": 1 / 118.0, "company_id": c.company.id}
    )
    c.company.sudo().write(
        {
            "expense_currency_exchange_account_id": _set_role(c, "fx_loss_t", "expense").id,
            "income_currency_exchange_account_id": _set_role(c, "fx_gain_t", "income").id,
        }
    )
    return (
        c.env["account.journal"]
        .sudo()
        .create(
            {
                "name": "M50 USD %s" % next(_SEQ),
                "type": "bank",
                "code": "MU%s" % (next(_SEQ) % 1000),
                "currency_id": usd.id,
            }
        )
    )


def test_fx_conversion_posts_the_realised_difference_after_a_second_approval(c):
    usd_bank = _usd_journal(c)
    conv = (
        c.env["fix.fx.conversion"]
        .with_user(c.acct)
        .create(
            {
                "deal_date": c.today,
                "bank_deal_ref": "DEAL-%s" % next(_SEQ),
                "from_journal_id": c.bank.id,
                "to_journal_id": usd_bank.id,
                "amount_from": 120000.0,
                "amount_to": 1000.0,
            }
        )
    )
    assert round(conv.rate_achieved, 2) == 120.0
    conv.with_user(c.acct).action_submit()
    with pytest.raises(UserError):
        conv.with_user(c.acct).write({"amount_to": 2000.0})
    with pytest.raises(UserError):
        conv.with_user(c.acct).action_approve()
    conv.with_user(c.mgr).action_approve()
    assert conv.state == "posted" and conv.move_id.state == "posted"
    assert round(conv.book_rate, 2) == 118.0
    assert round(conv.realised_difference, 2) == -2000.0  # paid 120,000 for 118,000 of USD
    loss = conv.move_id.line_ids.filtered(
        lambda ml: ml.account_id == c.company.expense_currency_exchange_account_id
    )
    assert round(loss.debit, 2) == 2000.0
    usd_leg = conv.move_id.line_ids.filtered(
        lambda ml: ml.account_id == usd_bank.default_account_id
    )
    assert usd_leg.amount_currency == 1000.0 and round(usd_leg.debit, 2) == 118000.0


def test_fx_conversion_needs_two_currencies_one_of_them_ours(c):
    other = (
        c.env["account.journal"]
        .sudo()
        .create(
            {
                "name": "M50 BDT2 %s" % next(_SEQ),
                "type": "bank",
                "code": "MB%s" % (next(_SEQ) % 1000),
            }
        )
    )
    with pytest.raises(ValidationError):
        c.env["fix.fx.conversion"].with_user(c.acct).create(
            {
                "deal_date": c.today,
                "bank_deal_ref": "X",
                "from_journal_id": c.bank.id,
                "to_journal_id": other.id,
                "amount_from": 10.0,
                "amount_to": 10.0,
            }
        )


def test_new_records_refuse_a_plain_user(c):
    with pytest.raises(REFUSED):
        _mandate(c, c.plain)
    with pytest.raises(REFUSED):
        _rule(c, c.plain)
    with pytest.raises(REFUSED):
        c.env["fix.cash.forecast.version"].with_user(c.plain).create(
            {"scenario": "base", "assumptions": "x"}
        )
    assert fields.Date.today()


def test_an_administrator_does_not_approve_their_own_rule(c):
    rule = _rule(c, c.mgr)
    rule.with_user(c.mgr).action_submit()
    with pytest.raises(UserError):
        rule.with_user(c.mgr).action_approve()
    rule.with_user(c.mgr2).action_approve()
    assert rule.state == "approved" and rule.approved_by_id == c.mgr2


def test_an_administrator_does_not_approve_their_own_conversion(c):
    usd_bank = _usd_journal(c)
    conv = (
        c.env["fix.fx.conversion"]
        .with_user(c.mgr)
        .create(
            {
                "deal_date": c.today,
                "bank_deal_ref": "DEAL-%s" % next(_SEQ),
                "from_journal_id": usd_bank.id,
                "to_journal_id": c.bank.id,
                "amount_from": 500.0,
                "amount_to": 60000.0,
            }
        )
    )
    conv.with_user(c.mgr).action_submit()
    with pytest.raises(UserError):
        conv.with_user(c.mgr).action_approve()
    conv.with_user(c.mgr2).action_approve()
    # sold 500 at 120 against a book rate of 118: a 1,000 gain
    assert round(conv.realised_difference, 2) == 1000.0
