# Behavioural tests for cd_multi_entity (M65) on the live ORM (`odoo_env`,
# rolled back after every test): consolidation + eliminations, inter-company
# mirroring, the Bangladesh statutory calendar, nil returns and the BD pack.
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


def _post_ledger(env, entity, revenue=1_000_000.0, expense=650_000.0, date="2026-01-15"):
    """Post a real balanced journal entry on the entity's company so the
    consolidation aggregates actual ledger balances (R01 re-audit: the old
    tests relied on the module writing constant amounts)."""
    n = next(_SEQ)
    company = entity.company_id
    journal = env["account.journal"].create(
        {"name": f"M65 J{n}", "code": f"M{n:04d}", "type": "general", "company_id": company.id}
    )
    # Odoo 19: accounts are multi-company (company_ids), not per-company.
    income = env["account.account"].create(
        {
            "code": f"4{n:04d}",
            "name": "Consolidation test income",
            "account_type": "income",
            "company_ids": [(6, 0, [company.id])],
        }
    )
    expense_acc = env["account.account"].create(
        {
            "code": f"5{n:04d}",
            "name": "Consolidation test expense",
            "account_type": "expense",
            "company_ids": [(6, 0, [company.id])],
        }
    )
    equity = env["account.account"].create(
        {
            "code": f"3{n:04d}",
            "name": "Consolidation test equity",
            "account_type": "equity",
            "company_ids": [(6, 0, [company.id])],
        }
    )
    move = env["account.move"].create(
        {
            "journal_id": journal.id,
            "company_id": company.id,
            "date": date,
            "line_ids": [
                (0, 0, {"name": "revenue", "account_id": income.id, "credit": revenue}),
                (0, 0, {"name": "expense", "account_id": expense_acc.id, "debit": expense}),
                (0, 0, {"name": "balance", "account_id": equity.id, "debit": revenue - expense}),
            ],
        }
    )
    move.action_post()
    return move


# --- fix.consolidation.book -------------------------------------------------------------


def test_consolidation_code_must_be_uppercase(odoo_env):
    entity = _entity(odoo_env)
    with _rejects(odoo_env, ValidationError, match="must be uppercase"):
        _book(odoo_env, [entity], code="cons-lower")


def test_run_consolidation_requires_participating_entities(odoo_env):
    book = _book(odoo_env, [_entity(odoo_env)])
    book.entity_ids = [(5, 0, 0)]
    with _rejects(odoo_env, ValidationError, match="at least one participating entity"):
        book.action_run_consolidation()
    assert book.state == "draft"


def test_run_consolidation_builds_lines_per_entity_and_totals(odoo_env):
    parent, sub = _entity(odoo_env), _entity(odoo_env)
    _post_ledger(odoo_env, parent)
    _post_ledger(odoo_env, sub)
    book = _book(odoo_env, [parent, sub])
    assert book.action_run_consolidation() is True

    assert book.state == "consolidated"
    assert len(book.line_ids) == 4
    for entity in (parent, sub):
        lines = book.line_ids.filtered(lambda line, e=entity: line.entity_id == e)
        assert sorted(lines.mapped("account_type")) == ["expense", "revenue"]
        assert all(line.exchange_rate == 1.0 for line in lines)
        assert all(line.original_currency_id == odoo_env.ref("base.BDT") for line in lines)
    assert book.total_subsidiary_revenue == 2_000_000.0
    assert book.total_subsidiary_expense == 1_300_000.0
    assert book.net_consolidated_profit == 700_000.0


def test_rerun_replaces_previous_lines(odoo_env):
    entity = _entity(odoo_env)
    _post_ledger(odoo_env, entity)
    book = _book(odoo_env, [entity])
    book.action_run_consolidation()
    first_lines = book.line_ids
    book.action_run_consolidation()
    assert len(book.line_ids) == 2
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


def _ic_txn(env, source, target, state="matched", amount=75_000.0):
    return env["fix.intercompany.transaction"].create(
        {
            "name": "Shared IT recharge",
            "reference": f"IC-T-{next(_SEQ)}",
            "source_entity_id": source.id,
            "target_entity_id": target.id,
            "amount": amount,
            "state": state,
        }
    )


def test_eliminations_offset_matched_intercompany_transactions(odoo_env):
    parent, sub, outsider = _entity(odoo_env), _entity(odoo_env), _entity(odoo_env)
    _post_ledger(odoo_env, parent)
    _post_ledger(odoo_env, sub)
    matched = _ic_txn(odoo_env, parent, sub)
    _ic_txn(odoo_env, parent, sub, state="draft")  # not matched: not eliminated
    _ic_txn(odoo_env, parent, outsider)  # counterparty outside the book
    book = _book(odoo_env, [parent, sub])
    book.action_run_consolidation()

    assert book.action_generate_eliminations() is True

    assert book.state == "eliminated"
    assert len(book.elimination_ids) == 1
    elim = book.elimination_ids
    assert elim.reference == matched.reference
    assert elim.name == f"Eliminate IC Txn {matched.reference}"
    assert (elim.from_entity_id, elim.to_entity_id) == (parent, sub)
    assert elim.amount == 75_000.0 and elim.elimination_type == "revenue_expense"
    assert book.total_eliminations == 75_000.0
    # IC revenue is eliminated against the counterparty's IC expense: both
    # sides shrink by the same amount and group profit is unchanged.
    assert book.consolidated_revenue == 2_000_000.0 - 75_000.0
    assert book.consolidated_expense == 1_300_000.0 - 75_000.0
    assert book.net_consolidated_profit == 700_000.0


def test_without_matched_transactions_no_elimination_is_invented(odoo_env):
    """Regression: a hard-coded 50,000 'shared management fee' elimination
    used to be posted whenever no matched IC transaction existed."""
    parent, sub = _entity(odoo_env, code="PARENTX"), _entity(odoo_env, code="SUBX")
    book = _book(odoo_env, [parent, sub])
    book.action_generate_eliminations()
    assert not book.elimination_ids
    assert book.total_eliminations == 0.0
    assert book.state == "eliminated"


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


def test_single_entity_book_has_no_eliminations_and_closes(odoo_env):
    book = _book(odoo_env, [_entity(odoo_env)])
    book.action_generate_eliminations()
    assert not book.elimination_ids
    assert book.state == "eliminated"
    assert book.action_close() is True
    assert book.state == "closed"


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
    assert rule.markup_percent == 5.0 and rule.transfer_pricing_compliant


def test_mirror_is_generated_once_then_matched(odoo_env):
    txn = _ic_txn(odoo_env, _entity(odoo_env), _entity(odoo_env), state="draft")
    assert txn.action_generate_mirror() is True
    assert txn.mirror_invoice_ref == f"MIRROR-AP-{txn.reference}"
    assert txn.state == "pending_matching"

    txn.write({"state": "disputed"})
    txn.action_generate_mirror()  # already mirrored: nothing is regenerated
    assert txn.state == "disputed"
    assert txn.mirror_invoice_ref == f"MIRROR-AP-{txn.reference}"

    assert txn.action_match() is True
    assert txn.state == "matched" and txn.matched_date


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


def test_new_entity_without_transactions_is_eligible(odoo_env):
    entity = _entity(odoo_env, incorporation_date=date(2026, 9, 1))
    nil = _nil(odoo_env, entity, period_year=2026, period_month=10)
    assert nil.is_newly_registered is True
    assert nil.eligible_for_nil_return is True
    assert nil.due_date == date(2026, 11, 15)  # a Sunday: a working day in Bangladesh
    nil.period_month = 7
    assert nil.due_date == date(2026, 8, 16)  # Saturday 15 Aug rolls to Sunday


def test_old_or_future_incorporation_is_not_newly_registered(odoo_env):
    old = _entity(odoo_env, incorporation_date=date(2020, 1, 1))
    assert _nil(odoo_env, old, period_year=2026, period_month=6).is_newly_registered is False
    future = _entity(odoo_env, incorporation_date=date(2026, 12, 1))
    assert _nil(odoo_env, future, period_year=2026, period_month=6).is_newly_registered is False


def test_unsaved_return_without_entity_has_no_due_date_or_eligibility(odoo_env):
    draft = odoo_env["fix.nil.return.generator"].new({"period_year": 2026, "period_month": 6})
    assert not draft.due_date
    assert draft.is_newly_registered is False
    assert draft.eligible_for_nil_return is False


def test_verify_eligibility(odoo_env):
    entity = _entity(odoo_env, code="NILOK")
    nil = _nil(odoo_env, entity)
    assert nil.action_verify_eligibility() is True
    assert nil.state == "verified"

    busy = _nil(odoo_env, entity, transaction_count=3)
    assert busy.eligible_for_nil_return is False
    with _rejects(odoo_env, ValidationError, match="NILOK has 3 recorded transactions"):
        busy.action_verify_eligibility()
    assert busy.state == "draft"


def test_generate_nil_packs_builds_mushak_and_tds_payloads(odoo_env):
    entity = _entity(
        odoo_env, code="NILPACK", bin_number="1882991029102", tin_number="881920391029"
    )
    nil = _nil(odoo_env, entity, period_year=2026, period_month=3)
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


def test_generate_nil_packs_refuses_without_real_bin_tin(odoo_env):
    """Regression: placeholder BIN/TIN (1000000000001 / 100000000001) were
    written into statutory payloads when the entity had none."""
    nil = _nil(odoo_env, _entity(odoo_env, code="NILNOID"))
    with _rejects(odoo_env, UserError, match="no registered BIN / TIN"):
        nil.action_generate_nil_packs()
    assert not nil.mushak_9_1_nil_payload


def test_generate_nil_packs_refused_after_submission(odoo_env):
    nil = _nil(odoo_env, _entity(odoo_env))
    nil.state = "submitted"
    with _rejects(odoo_env, ValidationError, match="must be verified prior to generation"):
        nil.action_generate_nil_packs()


def test_submit_refuses_without_a_real_nbr_acknowledgement(odoo_env):
    """Regression: the action minted NBR-ACK-<entity>-<period>-NIL itself and
    marked the return acknowledged although nothing was filed with NBR."""
    entity = _entity(odoo_env, code="NILREF", bin_number="1882991029102", tin_number="881920391029")
    nil = _nil(odoo_env, entity, period_year=2026, period_month=4)
    with _rejects(odoo_env, UserError, match="acknowledgement slip number"):
        nil.action_submit_to_nbr()
    assert nil.state == "draft"
    assert not nil.filing_reference


def test_submit_generates_missing_packs_and_records_acknowledgement(odoo_env):
    entity = _entity(odoo_env, code="NILSUB", bin_number="1882991029102", tin_number="881920391029")
    nil = _nil(odoo_env, entity, period_year=2026, period_month=4)
    nil.filing_reference = "  EVAT-ACK-778812  "  # slip number keyed in from the NBR portal
    assert nil.action_submit_to_nbr() is True
    assert nil.state == "acknowledged"
    assert nil.filing_reference == "EVAT-ACK-778812"
    assert json.loads(nil.tds_nil_payload)["tin"] == "881920391029"
    assert json.loads(nil.mushak_9_1_nil_payload)["bin"] == "1882991029102"


def test_submit_keeps_already_generated_packs(odoo_env):
    nil = _nil(odoo_env, _entity(odoo_env, code="NILKEEP"))
    nil.mushak_9_1_nil_payload = '{"prepared": "by compliance"}'
    nil.filing_reference = "EVAT-ACK-1"
    nil.action_submit_to_nbr()
    assert nil.mushak_9_1_nil_payload == '{"prepared": "by compliance"}'
    assert nil.state == "acknowledged"


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
