# cd_cash_position — A08 fix-wave B4 regressions for the M50 audit findings:
#   M50-F2  a statement import lost legitimate identical rows (within-file
#           dedup) and re-imported every row of a re-downloaded file (file
#           hash only, no per-line content dedup);
#   M50-F3  MT940 validation was missing: no opening/closing capture, no
#           sequence continuity, no arithmetic check, no quarantine state;
#   M50-F4  a facility instalment paid bank money on ONE person's click with
#           no bank evidence at all.
# The controls (T-03 / BRU-TRE-18 / FR-TRE-006 / FR-TRE-010) are asserted on
# the live ORM inside a rolled-back transaction (odoo_env).
from __future__ import annotations

import base64
from datetime import date

import pytest
from odoo.addons.cd_cash_position.tests.test_treasury_a08 import _SEQ, Kit, _balance
from odoo.exceptions import UserError

pytestmark = [pytest.mark.financial]


@pytest.fixture
def kit(odoo_env):
    return Kit(odoo_env)


def _import(kit, content, fmt="csv", journal=None, filename="b4.csv"):
    """Import a statement file through the import record (the user path)."""
    imp = kit.env["fix.bank.statement.import"].create(
        {
            "journal_id": (journal or kit.bank).id,
            "file": base64.b64encode(content.encode()),
            "filename": filename,
            "format_type": fmt,
        }
    )
    imp.action_import()
    return imp


def _mt940(stmt_no, opening, entries, closing):
    """A well-formed MT940: entries are (C|D, '500,00', ref, narration)."""
    day = "261102"
    text = ":20:B4STMT-%s\n:25:BD1000FIX\n:28C:%s\n" % (stmt_no, stmt_no)
    text += ":60F:C%sBDT%s\n" % (day, opening)
    for mark, amount, ref, narration in entries:
        text += ":61:%s%s%sNTRF%s\n" % (day, mark, amount, ref)
        if narration:
            text += ":86:%s\n" % narration
    text += ":62F:C%sBDT%s\n" % (day, closing)
    return text


# --------------------------------------------------------------- M50-F2 (a)


def test_m50_f2a_two_identical_csv_rows_both_import(kit):
    """Two legitimate identical transactions in one bank file are two lines
    of real money: both import (the parser's within-file dedup is defeated)."""
    day = "2026-11-02"
    dup_csv = (
        "Date,Reference,Description,Credit,Debit\r\n"
        "%s,DUP-1,Coffee shop POS,,50.00\r\n"
        "%s,DUP-1,Coffee shop POS,,50.00\r\n" % (day, day)
    )
    imp = _import(kit, dup_csv, filename="dup.csv")
    assert (imp.state, imp.imported_count) == ("imported", 2)
    assert len(imp.line_ids) == 2
    assert all(ln.amount == -50.0 for ln in imp.line_ids)


def test_m50_f2a_two_identical_mt940_entries_both_import(kit):
    dup_mt = _mt940(
        1,
        "1000,00",
        [("D", "50,00", "DUP-1", "POS CHARGE"), ("D", "50,00", "DUP-1", "POS CHARGE")],
        "900,00",
    )
    imp = _import(kit, dup_mt, fmt="mt940", filename="dup.mt940")
    assert (imp.state, imp.imported_count) == ("imported", 2)
    assert len(imp.line_ids) == 2
    assert all(ln.amount == -50.0 for ln in imp.line_ids)
    # the balances the bank stated are captured on the import (M50-F3 capture)
    assert (imp.has_balances, imp.opening_balance, imp.closing_balance) == (True, 1000.0, 900.0)


# --------------------------------------------------------------- M50-F2 (b)


def test_m50_f2b_reimported_changed_file_imports_nothing_new(kit):
    feed = "Date,Reference,Description,Credit,Debit\n2026-11-02,DUP-1,POS,,50.00\n"
    imp = _import(kit, feed, filename="first.csv")
    assert (imp.state, imp.imported_count) == ("imported", 1)
    total = kit.env["fix.bank.statement.line"].search_count([("journal_id", "=", kit.bank.id)])
    # the same statement re-downloaded with any byte change: a different file
    # hash, so the file-level dedup misses it — the per-line content hash
    # must skip the row it already knows
    again = _import(kit, feed + "\r\n", filename="again.csv")
    assert again.state == "imported"  # not a duplicate FILE — a changed one
    assert (again.imported_count, again.skipped_count) == (0, 1)
    assert not again.line_ids
    assert (
        kit.env["fix.bank.statement.line"].search_count([("journal_id", "=", kit.bank.id)]) == total
    )


def test_m50_f2_parser_warnings_and_counts_surface_on_the_import(kit):
    feed = (
        "Date,Amount,Reference,Description\n"
        "2026-11-02,-75.00,CHG-9,Charge\n"
        "not-a-date,-1.00,BAD,Row\n"
    )
    imp = _import(kit, feed, filename="warn.csv")
    assert (imp.imported_count, imp.skipped_count) == (1, 0)
    assert "invalid date" in (imp.parser_warnings or "")


# --------------------------------------------------------------- M50-F3 (c)


def test_m50_f3_wrong_closing_balance_quarantines_with_zero_lines(kit):
    broken = _mt940(1, "1000,00", [("D", "500,00", "LOAN-1", "INSTALMENT")], "400,00")
    imp = _import(kit, broken, fmt="mt940", filename="bad-closing.mt940")
    assert imp.state == "quarantined"
    assert imp.imported_count == 0 and not imp.line_ids
    assert "FR-TRE-006" in imp.quarantine_reason and "T-03" in imp.quarantine_reason
    # nothing partially processed: no line carries this file's hash
    assert not kit.env["fix.bank.statement.line"].search(
        [("statement_file_hash", "=", imp.file_hash)]
    )
    # the corrected statement imports on a new record
    fixed = _import(
        kit, broken.replace("BDT400,00", "BDT500,00"), fmt="mt940", filename="fixed.mt940"
    )
    assert (fixed.state, fixed.imported_count) == ("imported", 1)


# --------------------------------------------------------------- M50-F3 (d)


def test_m50_f3_sequence_break_quarantines(kit):
    first = _import(
        kit,
        _mt940(1, "1000,00", [("D", "500,00", "LOAN-1", "INSTALMENT")], "500,00"),
        fmt="mt940",
        filename="s1.mt940",
    )
    assert (first.state, first.imported_count) == ("imported", 1)
    # the next statement does not continue the account's closing balance
    gap = _import(
        kit,
        _mt940(2, "400,00", [("D", "100,00", "CHG-2", "FEE")], "300,00"),
        fmt="mt940",
        filename="s2.mt940",
    )
    assert gap.state == "quarantined"
    assert gap.imported_count == 0 and not gap.line_ids
    assert "FR-TRE-006" in gap.quarantine_reason and "sequence" in gap.quarantine_reason
    # a statement that DOES continue the last closing balance imports
    cont = _import(
        kit,
        _mt940(3, "500,00", [("D", "100,00", "CHG-3", "FEE")], "400,00"),
        fmt="mt940",
        filename="s3.mt940",
    )
    assert (cont.state, cont.imported_count) == ("imported", 1)


def test_m50_f3_continuity_is_per_bank_account(kit):
    """A statement of ANOTHER account is not chained against this one."""
    other = kit.env["account.journal"].create(
        {"name": "B4 Other Bank", "type": "bank", "code": "B4OB"}
    )
    _import(
        kit,
        _mt940(1, "1000,00", [("D", "500,00", "LOAN-1", "INSTALMENT")], "500,00"),
        fmt="mt940",
        filename="s1.mt940",
    )
    imp = _import(
        kit,
        _mt940(2, "9000,00", [("D", "100,00", "CHG-9", "FEE")], "8900,00"),
        fmt="mt940",
        journal=other,
        filename="other.mt940",
    )
    assert (imp.state, imp.imported_count) == ("imported", 1)


# --------------------------------------------------------------- M50-F4 (e)


def _facility(kit):
    env = kit.env
    loan_acc = env["account.account"].create(
        {
            "code": "B4LN%04d" % (next(_SEQ) % 10000),
            "name": "B4 term loan",
            "account_type": "liability_non_current",
        }
    )
    fac = env["fix.bank.facility"].create(
        {
            "name": "BRAC B4 TL",
            "lender_id": kit.vendor.id,
            "facility_type": "term_loan",
            "limit_amount": 1200000.0,
            "principal": 1200000.0,
            "interest_rate": 12.0,
            "tenor_months": 12,
            "start_date": date(2026, 11, 1),
            "liability_account_id": loan_acc.id,
            "journal_id": kit.bank.id,
        }
    )
    fac.action_generate_schedule()
    fac.action_activate()
    return fac, loan_acc


def test_m50_f4_instalment_refuses_one_person_and_confirms_via_statement_debit(kit):
    env = kit.env
    fac, loan_acc = _facility(kit)
    first = fac.repayment_ids[0]
    # the maker marks the instalment: NO GL, no bank movement
    first.with_user(kit.maker).action_pay()
    assert first.state == "awaiting_bank"
    assert (first.paid_by_id, first.move_id) == (kit.maker, env["account.move"])
    assert _balance(env, kit.bank_acc) == 0.0
    assert _balance(env, loan_acc) == 0.0
    # nothing but the bank's own record confirms it (FR-TRE-010): without an
    # imported debit there is nothing to confirm from
    with (
        pytest.raises(UserError, match="No single imported bank statement debit"),
        env.cr.savepoint(),
    ):
        first.with_user(kit.checker).action_confirm_bank()
    # the bank's debit arrives on an imported statement
    debit = kit.line(-first.total, narration="%s instalment #%s" % (fac.name, first.sequence))
    # the maker cannot confirm their own instruction (BRU-TRE-18)
    with pytest.raises(UserError, match="Segregation"), env.cr.savepoint():
        first.with_user(kit.maker).action_confirm_bank()
    assert first.state == "awaiting_bank"
    assert _balance(env, kit.bank_acc) == 0.0
    # a second person confirms: GL posts from the debit's value date
    first.with_user(kit.checker).action_confirm_bank()
    assert first.state == "paid"
    assert first.statement_line_id == debit
    assert debit.match_state == "manual" and debit.matched_kind == "instalment"
    env.invalidate_all()
    # Dr loan liability (the principal falls) + Dr interest / Cr bank
    assert _balance(env, loan_acc) == first.principal
    assert _balance(env, kit.accounts["interest_expense"]) == first.interest
    assert _balance(env, kit.bank_acc) == -first.total
    # paid in full only once: re-paying is refused, and a second debit of the
    # same total cannot confirm the instalment again
    with pytest.raises(UserError, match="only a planned"), env.cr.savepoint():
        first.with_user(kit.maker).action_pay()
    repeat = kit.line(
        -first.total, narration="%s instalment #%s repeat" % (fac.name, first.sequence)
    )
    repeat.with_user(kit.checker).write({"matched_instalment_id": first.id})
    with pytest.raises(UserError, match="not awaiting"), env.cr.savepoint():
        repeat.with_user(kit.checker).action_confirm_manual_match()


def test_m50_f4_marked_instalment_can_be_withdrawn_and_automatches(kit):
    env = kit.env
    fac, loan_acc = _facility(kit)
    first = fac.repayment_ids[0]
    first.with_user(kit.maker).action_pay()
    first.with_user(kit.maker).action_withdraw_payment()
    assert (first.state, first.paid_by_id) == ("planned", env["res.users"])
    # mark again, then the cron auto-match confirms it from the debit
    first.with_user(kit.maker).action_pay()
    kit.line(-first.total, narration="%s instalment #%s" % (fac.name, first.sequence))
    matched = env["fix.bank.statement.line"].with_user(kit.checker).auto_match()
    assert matched == 1
    assert first.state == "paid" and first.statement_line_id
    assert first.statement_line_id.matched_kind == "instalment"
