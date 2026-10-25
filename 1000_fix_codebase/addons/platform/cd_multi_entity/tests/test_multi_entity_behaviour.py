# Behavioural tests for cd_multi_entity (M65) on the live ORM (`odoo_env`,
# rolled back after every test): consolidation + eliminations, inter-company
# and inter-branch mirroring against the real ledger, the Bangladesh
# statutory calendar, nil returns and the BD pack.
import contextlib
import itertools
import json
from datetime import date, timedelta

import pytest
from odoo import fields
from odoo.addons.cd_multi_entity.models.fix_bd_country_pack_data import (
    BANGLADESH_DISTRICTS,
    BANGLADESH_DIVISIONS,
    STATUTORY_HOLIDAYS_2026,
)
from odoo.exceptions import UserError, ValidationError

_SEQ = itertools.count(1)


@contextlib.contextmanager
def _rejects(env, exc, match):
    with pytest.raises(exc, match=match) as info, env.cr.savepoint():
        yield info


def _entity(env, code=None, **vals):
    """A legal entity on its own fresh company (one fix.entity per company)."""
    n = next(_SEQ)
    company = env["res.company"].create({"name": f"M65 Test Co {n}"})
    return env["fix.entity"].create(
        {
            "code": code or f"ME{n}",
            "legal_name": f"M65 Test Entity {n}",
            "company_id": company.id,
            **vals,
        }
    )


def _book(env, entities, **vals):
    return env["fix.consolidation.book"].create(
        {
            "name": "Group Consolidation",
            "code": vals.pop("code", f"CONS-{next(_SEQ)}"),
            "parent_entity_id": entities[0].id,
            "entity_ids": [(6, 0, [e.id for e in entities])],
            # Pinned so the year-to-date P&L window (fiscal year containing
            # this date) does not drift with the wall clock.
            "consolidation_date": vals.pop("consolidation_date", "2026-06-30"),
            **vals,
        }
    )


def _usd_to_bdt(env, rate=120.0):
    """BDT quoted against the (USD) test company: 1 USD = `rate` BDT."""
    bdt, usd = env.ref("base.BDT"), env.ref("base.USD")
    env["res.currency.rate"].create(
        {"currency_id": bdt.id, "rate": rate, "name": "2000-01-01", "company_id": env.company.id}
    )
    return bdt, usd


def _journal(env, company):
    n = next(_SEQ)
    return env["account.journal"].create(
        {"name": f"M65 J{n}", "code": f"M{n:04d}", "type": "general", "company_id": company.id}
    )


def _acc(env, company, account_type, reconcile=False):
    """Odoo 19: accounts are multi-company (company_ids), not per-company."""
    n = next(_SEQ)
    return env["account.account"].create(
        {
            "code": f"9{n:05d}",
            "name": f"M65 {account_type} {n}",
            "account_type": account_type,
            "reconcile": reconcile,
            "company_ids": [(6, 0, [company.id])],
        }
    )


def _move(env, journal, day, legs):
    """Post a balanced entry: legs = [(account, signed amount: + debit)]."""
    move = env["account.move"].create(
        {
            "journal_id": journal.id,
            "company_id": journal.company_id.id,
            "date": day,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "name": "leg",
                        "account_id": account.id,
                        "debit": amount if amount > 0 else 0.0,
                        "credit": -amount if amount < 0 else 0.0,
                    },
                )
                for account, amount in legs
            ],
        }
    )
    move.action_post()
    return move


def _post_ledger(env, entity, revenue=1_000_000.0, expense=650_000.0, date="2026-01-15"):
    """Post a real balanced journal entry on the entity's company so the
    consolidation aggregates actual ledger balances (R01 re-audit: the old
    tests relied on the module writing constant amounts)."""
    company = entity.company_id
    return _move(
        env,
        _journal(env, company),
        date,
        [
            (_acc(env, company, "income"), -revenue),
            (_acc(env, company, "expense"), expense),
            (_acc(env, company, "equity"), revenue - expense),
        ],
    )


def _rule(env, src, tgt, **vals):
    """A fully configured inter-company rule (journals + four accounts)."""
    sc, tc = src.company_id, tgt.company_id
    return env["fix.intercompany.rule"].create(
        {
            "name": "IT recharge",
            "code": f"ICR-{next(_SEQ)}",
            "source_entity_id": src.id,
            "target_entity_id": tgt.id,
            "source_journal_id": _journal(env, sc).id,
            "source_receivable_account_id": _acc(env, sc, "asset_current", True).id,
            "source_income_account_id": _acc(env, sc, "income").id,
            "target_journal_id": _journal(env, tc).id,
            "target_expense_account_id": _acc(env, tc, "expense").id,
            "target_payable_account_id": _acc(env, tc, "liability_current", True).id,
            **vals,
        }
    )


def _branches(env, entity):
    company = entity.company_id
    n = next(_SEQ)
    ou = env["operating.unit"].create(
        {
            "name": f"M65 OU {n}",
            "code": f"OU{n}",
            "partner_id": company.partner_id.id,
            "company_id": company.id,
        }
    )
    return [
        env["fix.branch"].create(
            {
                "code": f"B{n}{s}",
                "name": f"Branch {n}{s}",
                "entity_id": entity.id,
                "operating_unit_id": ou.id,
            }
        )
        for s in ("A", "B")
    ]


def _branch_rule(env, entity):
    company = entity.company_id
    b1, b2 = _branches(env, entity)
    current = _acc(env, company, "asset_current", True)  # inter-branch current account
    return env["fix.intercompany.rule"].create(
        {
            "name": "Parts transfer",
            "code": f"IBR-{next(_SEQ)}",
            "scope": "interbranch",
            "source_entity_id": entity.id,
            "target_entity_id": entity.id,
            "source_branch_id": b1.id,
            "target_branch_id": b2.id,
            "source_journal_id": _journal(env, company).id,
            "source_receivable_account_id": current.id,
            "source_income_account_id": _acc(env, company, "income").id,
            "target_expense_account_id": _acc(env, company, "expense").id,
            "target_payable_account_id": current.id,
        }
    )


def _txn(env, source, target, state="matched", amount=75_000.0, **vals):
    return env["fix.intercompany.transaction"].create(
        {
            "name": "Shared IT recharge",
            "reference": f"IC-T-{next(_SEQ)}",
            "source_entity_id": source.id,
            "target_entity_id": target.id,
            "amount": amount,
            "currency_id": source.company_id.currency_id.id,
            "transaction_date": vals.pop("transaction_date", "2026-03-01"),
            "state": state,
            **vals,
        }
    )


def _mirrored(env, rule, amount, match, day="2026-03-01"):
    """A transaction taken through the real mirror (and match) flow."""
    txn = _txn(
        env,
        rule.source_entity_id,
        rule.target_entity_id,
        state="draft",
        amount=amount,
        rule_id=rule.id,
        transaction_date=day,
    )
    txn.action_generate_mirror()
    if match:
        assert txn.action_match() is True
    return txn


def _user(env, entity, *groups):
    n = next(_SEQ)
    company = entity.company_id
    return env["res.users"].create(
        {
            "name": f"M65 User {n}",
            "login": f"m65-user-{n}@test.local",
            "company_id": company.id,
            "company_ids": [(6, 0, company.ids)],
            "group_ids": [(6, 0, [env.ref(g).id for g in ("base.group_user", *groups)])],
        }
    )


# --- fix.consolidation.book -------------------------------------------------------------


def test_consolidation_code_must_be_uppercase(odoo_env):
    entity = _entity(odoo_env)
    with _rejects(odoo_env, ValidationError, match="must be uppercase"):
        _book(odoo_env, [entity], code="cons-lower")


def test_book_period_is_derived_from_the_consolidation_date(odoo_env):
    book = _book(odoo_env, [_entity(odoo_env)], consolidation_date="2026-03-31")
    assert (book.fiscal_year, book.period_month) == ("2025-2026", 3)
    book.consolidation_date = "2026-07-31"
    assert (book.fiscal_year, book.period_month) == ("2026-2027", 7)


def test_run_consolidation_requires_participating_entities(odoo_env):
    book = _book(odoo_env, [_entity(odoo_env)])
    book.entity_ids = [(5, 0, 0)]
    with _rejects(odoo_env, ValidationError, match="at least one participating entity"):
        book.action_run_consolidation()
    assert book.state == "draft"


def test_run_consolidation_refuses_without_any_ledger(odoo_env):
    book = _book(odoo_env, [_entity(odoo_env)])
    with _rejects(odoo_env, ValidationError, match="would be fabricated"):
        book.action_run_consolidation()
    assert not book.line_ids and book.state == "draft"


def test_run_consolidation_builds_lines_per_entity_and_totals(odoo_env):
    parent, sub = _entity(odoo_env), _entity(odoo_env)
    _post_ledger(odoo_env, parent)
    _post_ledger(odoo_env, sub)
    book = _book(odoo_env, [parent, sub])
    assert book.action_run_consolidation() is True

    assert book.state == "consolidated"
    assert book.run_by_id == odoo_env.user and book.run_at
    assert len(book.line_ids) == 6  # revenue, expense, equity per entity
    for entity in (parent, sub):
        lines = book.line_ids.filtered(lambda line, e=entity: line.entity_id == e)
        assert sorted(lines.mapped("account_type")) == ["equity", "expense", "revenue"]
        assert all(line.exchange_rate == 1.0 for line in lines)
        assert all(line.original_currency_id == odoo_env.ref("base.BDT") for line in lines)
        equity = lines.filtered(lambda line: line.account_type == "equity")
        assert equity.consolidated_amount == -350_000.0  # a debit on equity, natural sign
    assert book.total_subsidiary_revenue == 2_000_000.0
    assert book.total_subsidiary_expense == 1_300_000.0
    assert book.net_consolidated_profit == 700_000.0


def test_cost_of_revenue_and_depreciation_are_expenses(odoo_env):
    """Regression: the expense filter named account types that do not exist
    in Odoo 19 (cost_of_revenue, depreciation) and dropped COGS lines."""
    entity = _entity(odoo_env)
    company = entity.company_id
    journal = _journal(odoo_env, company)
    cogs = _acc(odoo_env, company, "expense_direct_cost")
    dep = _acc(odoo_env, company, "expense_depreciation")
    cash = _acc(odoo_env, company, "asset_cash")
    _move(odoo_env, journal, "2026-02-01", [(cogs, 300.0), (dep, 200.0), (cash, -500.0)])
    book = _book(odoo_env, [entity])
    book.action_run_consolidation()
    assert book.total_subsidiary_expense == 500.0
    assert book.total_assets == -500.0


def test_rerun_replaces_previous_lines(odoo_env):
    entity = _entity(odoo_env)
    _post_ledger(odoo_env, entity)
    book = _book(odoo_env, [entity])
    book.action_run_consolidation()
    first_lines = book.line_ids
    book.action_run_consolidation()
    assert len(book.line_ids) == 3
    assert not first_lines.exists()


def test_foreign_currency_subsidiary_is_translated_at_the_real_rate(odoo_env):
    """Regression: the rate lookup was a 1.0 placeholder, consolidating a
    USD subsidiary as if 1 USD were 1 BDT."""
    bdt, usd = _usd_to_bdt(odoo_env, rate=120.0)
    local, foreign = _entity(odoo_env), _entity(odoo_env, currency_id=usd.id)
    _post_ledger(odoo_env, local)
    _post_ledger(odoo_env, foreign)
    book = _book(odoo_env, [local, foreign], currency_id=bdt.id)

    book.action_run_consolidation()

    usd_lines = book.line_ids.filtered(lambda line: line.entity_id == foreign)
    assert all(line.original_currency_id == usd for line in usd_lines)
    assert all(line.exchange_rate == pytest.approx(120.0) for line in usd_lines)
    revenue = usd_lines.filtered(lambda line: line.account_type == "revenue")
    assert revenue.consolidated_amount == pytest.approx(120_000_000.0)
    assert book.total_subsidiary_revenue == pytest.approx(1_000_000.0 + 120_000_000.0)


def test_entity_without_currency_books_in_the_consolidation_currency(odoo_env):
    entity = _entity(odoo_env, currency_id=False)
    _post_ledger(odoo_env, entity)
    book = _book(odoo_env, [entity])
    book.action_run_consolidation()
    assert book.line_ids.mapped("original_currency_id") == book.currency_id
    assert set(book.line_ids.mapped("exchange_rate")) == {1.0}


def test_line_amount_defaults_a_missing_rate_to_one(odoo_env):
    entity = _entity(odoo_env)
    book = _book(odoo_env, [entity])
    line = odoo_env["fix.consolidation.line"].create(
        {
            "book_id": book.id,
            "entity_id": entity.id,
            "account_code": "400100",
            "account_name": "Other income",
            "account_type": "revenue",
            "original_amount": 250.0,
            "exchange_rate": 0.0,
        }
    )
    assert line.consolidated_amount == 250.0
    line.exchange_rate = 2.0
    assert line.consolidated_amount == 500.0


def test_pl_balances_are_year_to_date_not_since_inception(odoo_env):
    """Regression: revenue/expense were summed with no period start, so every
    prior year's P&L leaked into the consolidation."""
    entity = _entity(odoo_env)
    _post_ledger(odoo_env, entity, revenue=500_000.0, expense=100_000.0, date="2025-03-10")
    _post_ledger(odoo_env, entity, revenue=1_000_000.0, expense=650_000.0, date="2026-01-15")
    book = _book(odoo_env, [entity], consolidation_date="2026-06-30")
    book.action_run_consolidation()
    assert book.total_subsidiary_revenue == 1_000_000.0
    assert book.total_subsidiary_expense == 650_000.0


# --- eliminations -------------------------------------------------------------------------


def test_eliminations_need_a_consolidation_run(odoo_env):
    book = _book(odoo_env, [_entity(odoo_env), _entity(odoo_env)])
    with _rejects(odoo_env, UserError, match="Run the consolidation"):
        book.action_generate_eliminations()
    assert book.state == "draft"


def test_eliminations_come_from_mirrored_matched_transactions_only(odoo_env):
    parent, sub, outsider = _entity(odoo_env), _entity(odoo_env), _entity(odoo_env)
    _post_ledger(odoo_env, parent)
    _post_ledger(odoo_env, sub)
    rule = _rule(odoo_env, parent, sub)
    matched = _mirrored(odoo_env, rule, amount=75_000.0, match=True)
    _mirrored(odoo_env, rule, amount=10_000.0, match=False)  # pending: not eliminated
    _txn(odoo_env, parent, sub, state="matched")  # typed state, no postings: ignored
    _mirrored(odoo_env, _rule(odoo_env, parent, outsider), amount=5_000.0, match=True)
    book = _book(odoo_env, [parent, sub])
    book.action_run_consolidation()

    assert book.action_generate_eliminations() is True

    assert book.state == "eliminated"
    pl = book.elimination_ids.filtered(lambda e: e.elimination_type == "revenue_expense")
    bs = book.elimination_ids.filtered(lambda e: e.elimination_type == "receivable_payable")
    assert len(pl) == 1 and len(bs) == 1
    assert pl.transaction_id == matched and pl.reference == matched.reference
    assert pl.name == f"Eliminate IC Txn {matched.reference}"
    assert (pl.from_entity_id, pl.to_entity_id) == (parent, sub)
    assert pl.amount == 75_000.0 and bs.amount == 75_000.0
    # the mirror postings are in the ledger: both entities carry the IC
    # revenue/expense (the 5,000 charged to the outsider is real group
    # revenue: its expense sits outside the book), and the P&L elimination
    # removes the matched 75,000 from both sides
    assert book.total_subsidiary_revenue == 2_000_000.0 + 75_000.0 + 10_000.0 + 5_000.0
    assert book.total_subsidiary_expense == 1_300_000.0 + 75_000.0 + 10_000.0
    assert book.consolidated_revenue == 2_000_000.0 + 10_000.0 + 5_000.0
    assert book.consolidated_expense == 1_300_000.0 + 10_000.0
    assert book.net_consolidated_profit == 705_000.0
    # the open due-from / due-to pair is removed from assets and liabilities
    assert book.consolidated_assets == book.total_assets - 75_000.0
    assert book.consolidated_liabilities == book.total_liabilities - 75_000.0


def test_management_fee_rule_eliminates_as_management_fee(odoo_env):
    parent, sub = _entity(odoo_env), _entity(odoo_env)
    rule = _rule(odoo_env, parent, sub, transaction_type="management_fee")
    _mirrored(odoo_env, rule, amount=1_000.0, match=True)
    book = _book(odoo_env, [parent, sub])
    book.action_run_consolidation()
    book.action_generate_eliminations()
    assert set(book.elimination_ids.mapped("elimination_type")) == {
        "management_fee",
        "receivable_payable",
    }


def test_prior_year_transaction_eliminates_only_its_open_balance(odoo_env):
    parent, sub = _entity(odoo_env), _entity(odoo_env)
    rule = _rule(odoo_env, parent, sub)
    _mirrored(odoo_env, rule, amount=2_000.0, match=True, day="2025-11-20")
    book = _book(odoo_env, [parent, sub], consolidation_date="2026-06-30")
    book.action_run_consolidation()
    book.action_generate_eliminations()
    assert book.elimination_ids.mapped("elimination_type") == ["receivable_payable"]


def test_inter_branch_transactions_are_never_eliminated(odoo_env):
    entity, other = _entity(odoo_env), _entity(odoo_env)
    _post_ledger(odoo_env, other)
    rule = _branch_rule(odoo_env, entity)
    _mirrored(odoo_env, rule, amount=900.0, match=True)
    book = _book(odoo_env, [entity, other])
    book.action_run_consolidation()
    book.action_generate_eliminations()
    assert not book.elimination_ids


def test_without_matched_transactions_no_elimination_is_invented(odoo_env):
    """Regression: a hard-coded 50,000 'shared management fee' elimination
    used to be posted whenever no matched IC transaction existed."""
    parent, sub = _entity(odoo_env, code="PARENTX"), _entity(odoo_env, code="SUBX")
    _post_ledger(odoo_env, parent)
    book = _book(odoo_env, [parent, sub])
    book.action_run_consolidation()
    book.action_generate_eliminations()
    assert not book.elimination_ids
    assert book.total_eliminations == 0.0
    assert book.state == "eliminated"


def test_close_is_a_manager_approval_with_segregation_of_duties(odoo_env):
    entity = _entity(odoo_env)
    _post_ledger(odoo_env, entity)
    preparer = _user(odoo_env, entity, "account.group_account_manager")
    approver = _user(odoo_env, entity, "account.group_account_manager")
    clerk = _user(odoo_env, entity, "account.group_account_user")
    book = _book(odoo_env, [entity], company_id=entity.company_id.id).with_user(preparer)
    book.action_run_consolidation()
    with _rejects(odoo_env, UserError, match="Generate"):
        book.action_close()
    book.action_generate_eliminations()
    with _rejects(odoo_env, UserError, match="Only an accounting manager"):
        book.with_user(clerk).action_close()
    with _rejects(odoo_env, UserError, match="Segregation of duties"):
        book.action_close()
    assert book.with_user(approver).action_close() is True
    assert book.state == "closed" and book.closed_by_id == approver
    with _rejects(odoo_env, UserError, match="closed consolidation book"):
        book.action_run_consolidation()


# --- fix.intercompany ---------------------------------------------------------------------


def test_intercompany_rule_needs_distinct_entities(odoo_env):
    entity, other = _entity(odoo_env), _entity(odoo_env)
    Rule = odoo_env["fix.intercompany.rule"]
    with _rejects(odoo_env, ValidationError, match="must be distinct"):
        Rule.create(
            {
                "name": "Self",
                "code": "ICR-SELF",
                "source_entity_id": entity.id,
                "target_entity_id": entity.id,
            }
        )
    rule = Rule.create(
        {
            "name": "IT",
            "code": "ICR-IT",
            "source_entity_id": entity.id,
            "target_entity_id": other.id,
        }
    )
    # no transfer-pricing markup or compliance is assumed (adviser data)
    assert rule.markup_percent == 0.0 and not rule.transfer_pricing_compliant
    assert not rule.documentation_ref


def test_inter_branch_rule_needs_one_entity_and_two_of_its_branches(odoo_env):
    entity, other = _entity(odoo_env), _entity(odoo_env)
    b1, _b2 = _branches(odoo_env, entity)
    Rule = odoo_env["fix.intercompany.rule"]
    base = {"name": "IB", "scope": "interbranch", "source_entity_id": entity.id}
    with _rejects(odoo_env, ValidationError, match="must be the same"):
        Rule.create({**base, "code": "IB-1", "target_entity_id": other.id})
    with _rejects(odoo_env, ValidationError, match="needs a supplying and a receiving"):
        Rule.create({**base, "code": "IB-2", "target_entity_id": entity.id})
    with _rejects(odoo_env, ValidationError, match="must differ"):
        Rule.create(
            {
                **base,
                "code": "IB-3",
                "target_entity_id": entity.id,
                "source_branch_id": b1.id,
                "target_branch_id": b1.id,
            }
        )
    (foreign_branch,) = _branches(odoo_env, other)[:1]
    with _rejects(odoo_env, ValidationError, match="does not belong to entity"):
        Rule.create(
            {
                **base,
                "code": "IB-4",
                "target_entity_id": entity.id,
                "source_branch_id": b1.id,
                "target_branch_id": foreign_branch.id,
            }
        )


def test_mirror_refuses_without_rule_or_posting_configuration(odoo_env):
    src, tgt = _entity(odoo_env), _entity(odoo_env)
    txn = _txn(odoo_env, src, tgt, state="draft")
    with _rejects(odoo_env, UserError, match="Select the inter-company rule"):
        txn.action_generate_mirror()
    bare = odoo_env["fix.intercompany.rule"].create(
        {
            "name": "Bare",
            "code": f"BARE-{next(_SEQ)}",
            "source_entity_id": src.id,
            "target_entity_id": tgt.id,
        }
    )
    txn.rule_id = bare
    with _rejects(odoo_env, UserError, match="Due-From Account is not configured"):
        txn.action_generate_mirror()
    assert txn.state == "draft" and not txn.source_move_id


def test_mirror_refuses_accounts_of_the_wrong_company(odoo_env):
    src, tgt = _entity(odoo_env), _entity(odoo_env)
    rule = _rule(odoo_env, src, tgt)
    rule.target_payable_account_id = rule.source_receivable_account_id
    txn = _txn(odoo_env, src, tgt, state="draft", rule_id=rule.id)
    with _rejects(odoo_env, UserError, match="Due-To Account must be an account of"):
        txn.action_generate_mirror()


def test_mirror_posts_both_sides_then_matches(odoo_env):
    src, tgt = _entity(odoo_env), _entity(odoo_env)
    rule = _rule(odoo_env, src, tgt)
    txn = _txn(odoo_env, src, tgt, state="draft", rule_id=rule.id, amount=12_500.0)

    assert txn.action_generate_mirror() is True

    assert txn.state == "pending_matching"
    assert txn.source_move_id.company_id == src.company_id
    assert txn.target_move_id.company_id == tgt.company_id
    assert txn.source_move_id.state == txn.target_move_id.state == "posted"
    assert txn.mirror_invoice_ref == txn.target_move_id.name
    assert txn.source_due_line_id.account_id == rule.source_receivable_account_id
    assert txn.source_due_line_id.balance == 12_500.0
    assert txn.target_due_line_id.account_id == rule.target_payable_account_id
    assert txn.target_due_line_id.balance == -12_500.0
    income = txn.source_move_id.line_ids.filtered(
        lambda line: line.account_id == rule.source_income_account_id
    )
    assert income.balance == -12_500.0
    log = odoo_env["fix.journal.posting.log"].search([("move_id", "=", txn.target_move_id.id)])
    assert log.source == "intercompany"

    moves = txn.source_move_id | txn.target_move_id
    assert txn.action_generate_mirror() is True  # idempotent: nothing reposted
    assert txn.source_move_id | txn.target_move_id == moves

    assert txn.action_match() is True
    assert txn.state == "matched" and txn.matched_date and txn.match_difference == 0.0


def test_match_disputes_a_mirror_reset_to_draft(odoo_env):
    src, tgt = _entity(odoo_env), _entity(odoo_env)
    txn = _mirrored(odoo_env, _rule(odoo_env, src, tgt), amount=4_000.0, match=False)
    txn.target_move_id.button_draft()
    result = txn.action_match()
    assert result["status"] == "disputed"
    assert "not posted" in result["reason"]
    assert txn.state == "disputed"


def test_match_requires_the_mirror_first(odoo_env):
    txn = _txn(odoo_env, _entity(odoo_env), _entity(odoo_env), state="draft")
    with _rejects(odoo_env, UserError, match="Generate the mirror"):
        txn.action_match()


def test_inter_branch_mirror_is_one_entry_tagged_per_branch(odoo_env):
    entity = _entity(odoo_env)
    rule = _branch_rule(odoo_env, entity)
    txn = _txn(odoo_env, entity, entity, state="draft", rule_id=rule.id, amount=3_000.0)
    assert txn.scope == "interbranch"
    assert (txn.source_branch_id, txn.target_branch_id) == (
        rule.source_branch_id,
        rule.target_branch_id,
    )
    txn.action_generate_mirror()
    assert txn.source_move_id == txn.target_move_id
    move = txn.source_move_id
    assert len(move.line_ids) == 4 and move.state == "posted"
    dims = odoo_env["fix.journal.dimension"].search([("move_line_id", "in", move.line_ids.ids)])
    by_line = {d.move_line_id: d.branch_id for d in dims}
    assert by_line[txn.source_due_line_id] == rule.source_branch_id
    assert by_line[txn.target_due_line_id] == rule.target_branch_id
    assert txn.action_match() is True


def test_settlement_needs_reconciled_due_lines(odoo_env):
    src, tgt = _entity(odoo_env), _entity(odoo_env)
    rule = _rule(odoo_env, src, tgt)
    txn = _mirrored(odoo_env, rule, amount=6_000.0, match=True)
    with _rejects(odoo_env, UserError, match="Not settled in the ledger"):
        txn.action_mark_settled()

    # the receiving company pays, the supplying company receives: both due
    # lines are reconciled against the bank legs
    src_bank = _acc(odoo_env, src.company_id, "asset_cash")
    tgt_bank = _acc(odoo_env, tgt.company_id, "asset_cash")
    pay_in = _move(
        odoo_env,
        _journal(odoo_env, src.company_id),
        "2026-03-20",
        [(src_bank, 6_000.0), (rule.source_receivable_account_id, -6_000.0)],
    )
    pay_out = _move(
        odoo_env,
        _journal(odoo_env, tgt.company_id),
        "2026-03-20",
        [(rule.target_payable_account_id, 6_000.0), (tgt_bank, -6_000.0)],
    )
    (
        txn.source_due_line_id
        | pay_in.line_ids.filtered(
            lambda line: line.account_id == rule.source_receivable_account_id
        )
    ).reconcile()
    (
        txn.target_due_line_id
        | pay_out.line_ids.filtered(lambda line: line.account_id == rule.target_payable_account_id)
    ).reconcile()
    assert txn.action_mark_settled() is True
    assert txn.state == "settled"


def test_transaction_references_come_from_the_sequence(odoo_env):
    src, tgt = _entity(odoo_env), _entity(odoo_env)
    Txn = odoo_env["fix.intercompany.transaction"]
    vals = {"name": "x", "source_entity_id": src.id, "target_entity_id": tgt.id, "amount": 1.0}
    first, second = Txn.create(vals), Txn.create(vals)
    assert first.reference != second.reference
    assert first.reference.startswith("IC/")


def test_transaction_amount_must_be_positive(odoo_env):
    src, tgt = _entity(odoo_env), _entity(odoo_env)
    with _rejects(odoo_env, Exception, match="positive|amount_positive"):
        _txn(odoo_env, src, tgt, state="draft", amount=-5.0)
        odoo_env.flush_all()


# --- statutory calendar (fix.entity localisation) ---------------------------------------------


def _holiday(env, day):
    pack = env["fix.country.pack"].search([("code", "=", "TST-HOL")], limit=1) or env[
        "fix.country.pack"
    ].create({"name": "Test holidays", "code": "TST-HOL", "kind": "holidays"})
    env["fix.country.pack.line"].create(
        {
            "pack_id": pack.id,
            "code": str(day),
            "name": "Holiday",
            "name_bn": "ছুটি",
            "date_value": day,
        }
    )


def test_december_return_is_due_in_january_of_the_next_year(odoo_env):
    entity = _entity(odoo_env)
    # 15 Jan 2027 is a Friday -> rolls to Sunday 17 Jan
    assert entity.get_vat_return_due_date(2026, 12) == date(2027, 1, 17)


def test_strict_calendar_rule_never_rolls_over(odoo_env):
    entity = _entity(odoo_env, statutory_calendar_rule="strict_calendar_day")
    assert entity.get_vat_return_due_date(2026, 7) == date(2026, 8, 15)  # a Saturday


def test_due_date_skips_gazetted_holidays_and_the_weekend_after_them(odoo_env):
    entity = _entity(odoo_env)
    _holiday(odoo_env, date(2026, 1, 15))  # Thursday holiday
    # Thu 15 (holiday) -> Fri 16 / Sat 17 (weekend) -> Sun 18
    assert entity.get_vat_return_due_date(2025, 12) == date(2026, 1, 18)
    _holiday(odoo_env, date(2026, 11, 15))  # Sunday holiday
    _holiday(odoo_env, date(2026, 11, 16))
    assert entity.get_vat_return_due_date(2026, 10) == date(2026, 11, 17)


def test_unset_statutory_day_defaults_to_the_fifteenth(odoo_env):
    entity = _entity(odoo_env, vat_statutory_day=0, statutory_calendar_rule="strict_calendar_day")
    assert entity.get_vat_return_due_date(2026, 3) == date(2026, 4, 15)


@pytest.mark.parametrize(
    ("quarter", "expected"),
    [
        (1, date(2026, 10, 15)),
        (2, date(2027, 1, 17)),
        (3, date(2027, 4, 15)),
        (4, date(2027, 7, 15)),
    ],
)
def test_tds_quarter_due_dates(odoo_env, quarter, expected):
    assert _entity(odoo_env).get_tds_quarter_due_date(quarter, 2027) == expected


def test_tds_quarter_must_exist(odoo_env):
    with _rejects(odoo_env, ValidationError, match="Invalid TDS quarter 5"):
        _entity(odoo_env).get_tds_quarter_due_date(5, 2027)


@pytest.mark.parametrize("missing", ["division", "district", "postcode"])
def test_bd_address_validation_requires_each_tier(odoo_env, missing):
    address = {"division": "Dhaka", "district": "Dhaka", "postcode": "1212"}
    address.pop(missing)
    with _rejects(
        odoo_env, ValidationError, match=f"Missing mandatory address component: {missing}"
    ):
        _entity(odoo_env).validate_bd_address(address)


def test_bd_address_validation_accepts_numeric_postcodes(odoo_env):
    assert _entity(odoo_env).validate_bd_address(
        {"division": "Dhaka", "district": "Dhaka", "postcode": 1212}
    )


# --- fix.nil.return.generator ------------------------------------------------------------------


def _nil(env, entity, **vals):
    today = fields.Date.context_today(entity)
    vals = {"entity_id": entity.id, "period_year": today.year, "period_month": today.month, **vals}
    return env["fix.nil.return.generator"].create(vals)


def _verified(env, entity, **vals):
    nil = _nil(env, entity, **vals)
    assert nil.action_verify_eligibility() is True
    return nil


def test_default_period_is_the_previous_month(odoo_env):
    nil = odoo_env["fix.nil.return.generator"].create({"entity_id": _entity(odoo_env).id})
    today = fields.Date.context_today(nil)
    expected = (today.year - 1, 12) if today.month == 1 else (today.year, today.month - 1)
    assert (nil.period_year, nil.period_month) == expected
    assert nil.name.startswith("NIL/")


def test_period_month_must_be_a_month(odoo_env):
    with _rejects(odoo_env, ValidationError, match="between 1 and 12"):
        _nil(odoo_env, _entity(odoo_env), period_month=13)


def test_eligibility_is_only_known_after_counting(odoo_env):
    entity = _entity(odoo_env, incorporation_date=date(2026, 9, 1))
    nil = _nil(odoo_env, entity, period_year=2026, period_month=10)
    assert nil.is_newly_registered is True
    # nothing counted yet: never eligible by default
    assert nil.eligible_for_nil_return is False
    assert nil.due_date == date(2026, 11, 15)  # a Sunday: a working day in Bangladesh
    nil.action_verify_eligibility()
    assert nil.eligible_for_nil_return is True
    assert nil.transaction_count == 0 and nil.transactions_counted_at
    assert nil.state == "verified"
    nil.period_month = 7
    assert nil.due_date == date(2026, 8, 16)  # Saturday 15 Aug rolls to Sunday


def test_registration_month_counts_as_newly_registered(odoo_env):
    entity = _entity(odoo_env, incorporation_date=date(2026, 10, 20))
    assert _nil(odoo_env, entity, period_year=2026, period_month=10).is_newly_registered is True


def test_old_future_or_unknown_incorporation_is_not_newly_registered(odoo_env):
    old = _entity(odoo_env, incorporation_date=date(2020, 1, 1))
    assert _nil(odoo_env, old, period_year=2026, period_month=6).is_newly_registered is False
    future = _entity(odoo_env, incorporation_date=date(2026, 12, 1))
    assert _nil(odoo_env, future, period_year=2026, period_month=6).is_newly_registered is False
    unknown = _entity(odoo_env)
    assert not unknown.incorporation_date  # no assumed default
    assert _nil(odoo_env, unknown, period_year=2026, period_month=6).is_newly_registered is False


def test_unsaved_return_without_entity_has_no_due_date_or_eligibility(odoo_env):
    draft = odoo_env["fix.nil.return.generator"].new({"period_year": 2026, "period_month": 6})
    assert not draft.due_date
    assert draft.is_newly_registered is False
    assert draft.eligible_for_nil_return is False


def test_verify_counts_the_period_ledger(odoo_env):
    entity = _entity(odoo_env, code="NILBUSY")
    _post_ledger(odoo_env, entity, date="2026-05-10")
    _post_ledger(odoo_env, entity, date="2026-06-02")  # outside May: not counted
    busy = _nil(odoo_env, entity, period_year=2026, period_month=5)
    with _rejects(odoo_env, ValidationError, match="NILBUSY has 1 recorded transactions"):
        busy.action_verify_eligibility()
    assert busy.state == "draft" and busy.eligible_for_nil_return is False

    quiet = _nil(odoo_env, entity, period_year=2026, period_month=4)
    assert quiet.action_verify_eligibility() is True
    assert quiet.state == "verified"


def test_draft_entries_do_not_count(odoo_env):
    entity = _entity(odoo_env)
    move = _post_ledger(odoo_env, entity, date="2026-05-10")
    move.button_draft()
    assert _nil(odoo_env, entity, period_year=2026, period_month=5).action_verify_eligibility()


def test_generate_nil_packs_builds_mushak_and_tds_payloads(odoo_env):
    entity = _entity(
        odoo_env, code="NILPACK", bin_number="1882991029102", tin_number="881920391029"
    )
    nil = _verified(odoo_env, entity, period_year=2026, period_month=3)
    assert nil.action_generate_nil_packs() is True
    assert nil.state == "generated"
    mushak = json.loads(nil.mushak_9_1_nil_payload)
    assert mushak["bin"] == "1882991029102"
    assert mushak["tax_period"] == "2026-03"
    assert mushak["entity_code"] == "NILPACK"
    assert mushak["declaration"]["timestamp_utc"]
    tds = json.loads(nil.tds_nil_payload)
    assert tds["tin"] == "881920391029"
    assert tds["withholding_count"] == 0


def test_generate_nil_packs_needs_verification_first(odoo_env):
    """Regression: packs could be generated straight from draft, skipping
    the eligibility check."""
    entity = _entity(odoo_env, bin_number="1882991029102", tin_number="881920391029")
    nil = _nil(odoo_env, entity, period_year=2026, period_month=3)
    with _rejects(odoo_env, ValidationError, match="must be verified prior to generation"):
        nil.action_generate_nil_packs()
    assert not nil.mushak_9_1_nil_payload


def test_generate_nil_packs_refuses_without_real_bin_tin(odoo_env):
    """Regression: placeholder BIN/TIN (1000000000001 / 100000000001) were
    written into statutory payloads when the entity had none."""
    nil = _verified(odoo_env, _entity(odoo_env, code="NILNOID"), period_year=2026, period_month=3)
    with _rejects(odoo_env, UserError, match="no registered BIN / TIN"):
        nil.action_generate_nil_packs()
    assert not nil.mushak_9_1_nil_payload


def test_generate_nil_packs_refused_after_submission(odoo_env):
    nil = _nil(odoo_env, _entity(odoo_env))
    nil.state = "submitted"
    with _rejects(odoo_env, ValidationError, match="must be verified prior to generation"):
        nil.action_generate_nil_packs()
    with _rejects(odoo_env, UserError, match="re-verified before the packs"):
        nil.action_verify_eligibility()


def _generated(env, code):
    entity = _entity(env, code=code, bin_number="1882991029102", tin_number="881920391029")
    nil = _verified(env, entity, period_year=2026, period_month=4)
    nil.action_generate_nil_packs()
    return nil


def test_submit_refuses_without_a_real_nbr_acknowledgement(odoo_env):
    """Regression: the action minted NBR-ACK-<entity>-<period>-NIL itself and
    marked the return acknowledged although nothing was filed with NBR."""
    nil = _generated(odoo_env, "NILREF")
    with _rejects(odoo_env, UserError, match="acknowledgement slip number"):
        nil.action_submit_to_nbr()
    assert nil.state == "generated"
    assert not nil.filing_reference


def test_submit_needs_generated_packs(odoo_env):
    nil = _nil(odoo_env, _entity(odoo_env, code="NILNOPK"))
    nil.filing_reference = "EVAT-ACK-1"
    with _rejects(odoo_env, UserError, match="Generate the nil-return packs"):
        nil.action_submit_to_nbr()
    assert nil.state == "draft"


def test_submit_records_the_acknowledgement(odoo_env):
    nil = _generated(odoo_env, "NILSUB")
    nil.filing_reference = "  EVAT-ACK-778812  "  # slip number keyed in from the NBR portal
    assert nil.action_submit_to_nbr() is True
    assert nil.state == "acknowledged"
    assert nil.filing_reference == "EVAT-ACK-778812"
    assert json.loads(nil.tds_nil_payload)["tin"] == "881920391029"
    assert json.loads(nil.mushak_9_1_nil_payload)["bin"] == "1882991029102"


# --- Bangladesh country pack loader ----------------------------------------------------------------


def test_bangladesh_pack_loads_divisions_districts_and_holidays_once(odoo_env):
    Pack = odoo_env["fix.country.pack"]
    Loader = odoo_env["fix.country_pack.loader"]

    result = Loader.load_bangladesh_pack()

    assert result == {
        "divisions_count": 8,
        "districts_count": 64,
        "holidays_count": len(STATUTORY_HOLIDAYS_2026),
        "status": "LOADED",
    }
    div_pack = Pack.search([("code", "=", "BD-DIV-DIST-2026")])
    hol_pack = Pack.search([("code", "=", "BD-HOL-2026")])
    assert div_pack.loaded_at and hol_pack.loaded_at
    assert len(div_pack.line_ids) == len(BANGLADESH_DIVISIONS) + len(BANGLADESH_DISTRICTS)
    gazipur = div_pack.line_ids.filtered(lambda line: line.code == "BD-14")
    assert (gazipur.parent_code, gazipur.name_bn) == ("BD-30", "গাজীপুর")
    victory = hol_pack.line_ids.filtered(lambda line: line.code == "HOL-2026-12-16")
    assert victory.date_value == date(2026, 12, 16)

    Loader.load_bangladesh_pack()  # idempotent: no duplicate packs or lines
    assert Pack.search_count([("code", "in", ["BD-DIV-DIST-2026", "BD-HOL-2026"])]) == 2
    assert len(div_pack.line_ids) == 72

    # the loaded holidays drive the statutory calendar: 16 Dec 2026 is a
    # Wednesday holiday, so a due date landing on it moves to Thursday
    entity = _entity(odoo_env, vat_statutory_day=16)
    assert entity.get_vat_return_due_date(2026, 11) == date(2026, 12, 16) + timedelta(days=1)
