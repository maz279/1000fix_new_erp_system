"""INT-006 bank feed parser — MT940 / CSV edge cases and regressions.

Malformed tags, debit/credit marks (incl. SWIFT reversals), optional :86:
narration, multi-line narration, multiple statements, BOM, separators,
short rows, and the IN-004 §9 sequence audit.
"""

from __future__ import annotations

import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

pytestmark = [pytest.mark.financial]

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bank_feed_parser import parse_bank_feed, parse_csv, parse_mt940

D = Decimal
BOM = chr(0xFEFF)


def mt940(*body: str, seq: str = "00045/001") -> str:
    return "\n".join(
        [
            ":20:STMT-1",
            ":25:012345678901",
            f":28C:{seq}",
            ":60F:C261001BDT50000,00",
            *body,
            ":62F:C261015BDT53450,00",
        ]
    )


# ------------------------------------------------------------------ MT940


class TestMt940DebitCreditMarks:
    @pytest.mark.parametrize(
        ("mark", "expected"),
        [("C", D("500.00")), ("D", D("-500.00")), ("RC", D("-500.00")), ("RD", D("500.00"))],
    )
    def test_regression_reversal_marks_carry_the_swift_sign(self, mark, expected):
        """Regression: RC (reversal of credit) is a DEBIT entry and RD
        (reversal of debit) a CREDIT entry (SWIFT field 61 subfield 3).
        The parser negated RD and kept RC positive — every reversal was
        imported with the wrong sign."""
        parsed = parse_mt940(mt940(f":61:2610151015{mark}500,00NTRFNONREF//REV/1", ":86:REV"))
        assert [line.amount for line in parsed.lines] == [expected]

    def test_funds_code_after_mark_is_not_a_sign(self):
        parsed = parse_mt940(mt940(":61:261015DR75,50NTRFNONREF//CHG/1", ":86:CHARGE"))
        assert parsed.lines[0].amount == D("-75.50")
        assert parsed.lines[0].date == date(2026, 10, 15)

    def test_regression_owner_reference_keeps_its_slash(self):
        """Regression: the owner-reference group stopped at the FIRST "/"
        ([^/]+), so an invoice reference such as AR/555 was imported as
        "AR" and could never match its invoice."""
        parsed = parse_mt940(mt940(":61:261015C100,00NTRFAR/555", ":86:X"))
        assert parsed.lines[0].reference == "AR/555"

    def test_regression_swift_numeric_transaction_type(self):
        """Regression: S103-style transaction types (S + 3 digits) were not
        recognised, so the type code was glued onto the reference."""
        parsed = parse_mt940(mt940(":61:261015C100,00S103AR/556", ":86:X"))
        assert parsed.lines[0].reference == "AR/556"

    def test_bank_reference_after_double_slash_wins(self):
        parsed = parse_mt940(mt940(":61:261015C100,00NTRFAR/557//BANK-REF-1", ":86:X"))
        assert parsed.lines[0].reference == "BANK-REF-1"

    def test_entry_without_reference_has_blank_reference(self):
        parsed = parse_mt940(mt940(":61:261015C100,00", ":86:CASH"))
        assert parsed.lines[0].reference == ""


class TestMt940OptionalNarration:
    def test_regression_consecutive_entries_without_86_are_all_kept(self):
        """Regression: an entry was only committed by a following :86: or
        :62F:, so consecutive :61: lines without narration silently dropped
        every entry but the last (bank money vanished from the import)."""
        parsed = parse_mt940(
            mt940(
                ":61:261015C1150,00NTRFNONREF//AR/101",
                ":61:261015C2300,00NTRFNONREF//AR/102",
                ":61:261015D99,00NCHGNONREF//FEE/1",
                ":86:SMS ALERT CHARGE",
            )
        )
        assert [(ln.reference, ln.amount, ln.narration) for ln in parsed.lines] == [
            ("AR/101", D("1150.00"), ""),
            ("AR/102", D("2300.00"), ""),
            ("FEE/1", D("-99.00"), "SMS ALERT CHARGE"),
        ]
        assert len(parsed.line_hashes) == 3

    def test_regression_truncated_statement_keeps_last_entry(self):
        """Regression: an entry still pending at end of input (no :86:, no
        :62F: — a truncated or page-split file) was discarded."""
        parsed = parse_mt940(":20:STMT-T\n:61:261015C10,00NTRFNONREF//AR/7")
        assert [(ln.reference, ln.amount) for ln in parsed.lines] == [("AR/7", D("10.00"))]
        assert parsed.closing_balance is None


class TestMt940Narration:
    def test_multi_line_narration_is_joined(self):
        parsed = parse_mt940(
            mt940(
                ":61:261015C1150,00NTRFNONREF//AR/101",
                ":86:CREDIT TRANSFER FROM",
                "RAHIM UDDIN",
                "  MIRPUR BRANCH  ",
            )
        )
        assert parsed.lines[0].narration == "CREDIT TRANSFER FROM RAHIM UDDIN MIRPUR BRANCH"

    def test_regression_continuation_never_lands_on_another_entry(self):
        """Regression: narration continuation lines were appended to the
        LAST COMMITTED line. When the :86: belonged to an entry skipped as a
        duplicate (its hash ignored the continuation), the text corrupted
        the previous entry and the distinct second entry was dropped."""
        parsed = parse_mt940(
            mt940(
                ":61:261015C100,00NTRFNONREF//R1",
                ":86:PAYMENT",
                ":61:261015C100,00NTRFNONREF//R1",
                ":86:PAYMENT",
                "SECOND INSTALMENT",
            )
        )
        assert [ln.narration for ln in parsed.lines] == ["PAYMENT", "PAYMENT SECOND INSTALMENT"]
        assert parsed.duplicate_lines_skipped == 0

    def test_regression_statement_level_86_does_not_touch_entries(self):
        """Regression: a statement-level :86: (after :62F:) and its
        continuation lines were glued onto the last transaction's narration."""
        content = mt940(":61:261015C100,00NTRFNONREF//R1", ":86:PAYMENT")
        content += "\n:64:C261015BDT53450,00\n:86:STATEMENT INFORMATION\nFOR OWNER\n-}"
        parsed = parse_mt940(content)
        assert [ln.narration for ln in parsed.lines] == ["PAYMENT"]

    def test_unknown_tag_ends_narration(self):
        parsed = parse_mt940(
            mt940(":61:261015C100,00NTRFNONREF//R1", ":86:PAYMENT", ":65:C261016BDT1,00")
        )
        assert parsed.lines[0].narration == "PAYMENT"

    def test_orphan_and_second_86_are_ignored(self):
        parsed = parse_mt940(
            ":20:S\n:86:ORPHAN BEFORE ANY ENTRY\n"
            ":61:261015C5,00NTRFNONREF//R9\n:86:FIRST\n:86:SECOND\n:62F:C261015BDT5,00"
        )
        assert [(ln.reference, ln.narration) for ln in parsed.lines] == [("R9", "FIRST")]

    def test_swift_block_wrappers_are_ignored(self):
        content = "{1:F01CIBLBDDHAXXX0000000000}{2:I940XXXXXXXXXXXXN}{4:\n" + mt940(
            ":61:261015C100,00NTRFNONREF//R1", ":86:PAYMENT"
        )
        parsed = parse_bank_feed(content + "\n-}")
        assert parsed.statement_id == "STMT-1"
        assert [ln.reference for ln in parsed.lines] == ["R1"]


class TestMt940Malformed:
    def test_unparseable_entry_warns_and_is_skipped(self):
        parsed = parse_mt940(mt940(":61:GARBAGE", ":86:NOTHING TO ATTACH TO"))
        assert parsed.lines == []
        assert parsed.warnings == ["Failed to parse MT940 line: :61:GARBAGE"]

    @pytest.mark.parametrize(
        "bad_entry",
        [":61:261345C100,00NTRFNONREF//R1", ":61:261015C1,2,3NTRFNONREF//R1"],
        ids=["month-13", "amount-with-two-decimal-marks"],
    )
    def test_regression_invalid_date_or_amount_warns_instead_of_crashing(self, bad_entry):
        """Regression: an impossible value date (ValueError) or a malformed
        amount (decimal.InvalidOperation) aborted the WHOLE statement import."""
        parsed = parse_mt940(mt940(":61:261015C1,00NTRFNONREF//OK", bad_entry, ":86:X"))
        assert [ln.reference for ln in parsed.lines] == ["OK"]
        assert parsed.warnings == [f"Failed to parse MT940 line: {bad_entry}"]

    def test_regression_malformed_balance_warns_instead_of_crashing(self):
        parsed = parse_mt940(":20:S\n:60F:C261001BDT1.000,00\n:62F:XX\n")
        assert parsed.opening_balance is None and parsed.closing_balance is None
        assert parsed.warnings == [
            "Failed to parse MT940 balance line: :60F:C261001BDT1.000,00",
            "Failed to parse MT940 balance line: :62F:XX",
        ]

    def test_debit_balances_and_intermediate_tags(self):
        parsed = parse_mt940(
            ":20:S\n:28:7\n:60M:D261001BDT250,00\n:61:261015C300,00NTRFNONREF//R1\n"
            ":62M:C261015BDT50,00"
        )
        assert parsed.sequence_number == "7"
        assert parsed.opening_balance == D("-250.00")
        assert parsed.closing_balance == D("50.00")
        assert parsed.lines[0].amount == D("300.00")
        parsed = parse_mt940(":20:S\n:62F:D261015BDT12,34")
        assert parsed.closing_balance == D("-12.34")


class TestMt940Statements:
    def test_multiple_statements_in_one_file(self):
        content = (
            ":20:STMT-A\n:28C:00045/001\n:60F:C261001BDT0,00\n"
            ":61:261014C10,00NTRFNONREF//A1\n"  # pending when the next :20: arrives
            ":20:STMT-B\n:28C:00046/001\n:60F:C261002BDT10,00\n"
            ":61:261015C20,00NTRFNONREF//B1\n:86:SECOND\n:62F:C261015BDT30,00"
        )
        parsed = parse_mt940(content)
        assert parsed.statement_id == "STMT-B"
        assert parsed.sequence_number == "00046/001"
        assert [(ln.reference, ln.amount) for ln in parsed.lines] == [
            ("A1", D("10.00")),
            ("B1", D("20.00")),
        ]
        assert (parsed.opening_balance, parsed.closing_balance) == (D("10.00"), D("30.00"))

    def test_reimport_with_seen_hashes_skips_every_line(self):
        content = mt940(
            ":61:261015C1150,00NTRFNONREF//AR/101",
            ":86:LINE ONE",
            "CONTINUED",
            ":61:261015C2300,00NTRFNONREF//AR/102",
        )
        first = parse_mt940(content)
        again = parse_mt940(content, seen_hashes=set(first.line_hashes))
        assert len(first.lines) == 2
        assert again.lines == []
        assert again.duplicate_lines_skipped == 2
        assert again.file_hash == first.file_hash

    def test_regression_bom_does_not_hide_the_statement_header(self):
        """Regression: a UTF-8 BOM (Excel / bank portal export) hid the first
        tag — the statement id came back UNKNOWN."""
        content = BOM + mt940(":61:261015C1,00NTRFNONREF//R1", ":86:X")
        assert parse_mt940(content).statement_id == "STMT-1"
        via_entry_point = parse_bank_feed(content)
        assert via_entry_point.statement_id == "STMT-1"
        assert via_entry_point.file_hash == parse_mt940(content).file_hash


class TestMt940SequenceAudit:
    def test_regression_sequence_gap_is_reported(self):
        """Regression: the MT940 gap audit tested `"last_sequence" in
        warnings`, which can never be true — gaps were never reported."""
        parsed = parse_mt940(mt940(seq="00047/001"), expected_sequence=46)
        assert parsed.warnings == ["Sequence mismatch: expected 46, got 00047/001"]

    def test_expected_sequence_matches(self):
        assert parse_mt940(mt940(), expected_sequence=45).warnings == []

    def test_no_audit_without_expectation(self):
        assert parse_mt940(mt940(seq="ABC/1")).warnings == []

    def test_unparseable_sequence_is_flagged_not_silently_passed(self):
        parsed = parse_mt940(mt940(seq="ABC/1"), expected_sequence=1)
        assert parsed.warnings == ["Sequence check skipped: unparseable sequence 'ABC/1'"]

    def test_entry_point_passes_expectation_through(self):
        parsed = parse_bank_feed(mt940(), format_type="mt940", expected_sequence=44)
        assert parsed.warnings == ["Sequence mismatch: expected 44, got 00045/001"]


# ------------------------------------------------------------------ CSV


class TestCsvSeparatorsAndEncoding:
    def test_regression_tab_feed_with_comma_thousands(self):
        """Regression: the delimiter was "tab only if NO comma anywhere in
        the first 1 KB", so a tab-separated feed with 1,150.00-style amounts
        was parsed as comma-separated and every row was lost."""
        content = "Date\tReference\tAmount\n2026-10-15\tAR/1\t1,15,000.50\n"
        parsed = parse_csv(content)
        assert [(ln.reference, ln.amount) for ln in parsed.lines] == [("AR/1", D("115000.50"))]
        assert parsed.warnings == []

    def test_semicolon_separated_feed(self):
        content = "Date;Ref;Particulars;Cr;Dr\n15/10/2026;AR/2;NPSB;2500.00;\n"
        parsed = parse_csv(content)
        assert [(ln.reference, ln.amount, ln.narration) for ln in parsed.lines] == [
            ("AR/2", D("2500.00"), "NPSB")
        ]

    def test_regression_bom_keeps_first_column_mapping(self):
        """Regression: with a BOM the first header became "\\ufeffReference",
        which matched no column name, so every line lost its reference."""
        content = BOM + "Reference,Date,Amount\nAR/3,2026-10-15,100.00\n"
        parsed = parse_bank_feed(content)
        assert parsed.statement_id == "CSV-IMPORT"
        assert parsed.lines[0].reference == "AR/3"

    def test_empty_feed(self):
        parsed = parse_csv("")
        assert (parsed.statement_id, parsed.sequence_number, parsed.lines) == ("EMPTY", "0", [])
        assert parsed.warnings == ["Empty CSV"]


class TestCsvRows:
    def test_regression_short_rows_do_not_crash(self):
        """Regression: csv.DictReader fills missing trailing cells with None
        and `None.replace(...)` raised AttributeError for the whole feed."""
        content = (
            "Date,Reference,Description,Credit,Debit\n2026-10-15,AR/5,NEFT,500.00\n2026-10-16\n"
        )
        parsed = parse_csv(content)
        assert [(ln.date, ln.reference, ln.amount) for ln in parsed.lines] == [
            (date(2026, 10, 15), "AR/5", D("500.00")),
            (date(2026, 10, 16), "", D("0.00")),
        ]

    def test_regression_invalid_amount_warns_and_skips_row(self):
        """Regression: a non-numeric amount raised decimal.InvalidOperation
        and aborted the import (dates already warned-and-skipped)."""
        content = "Date,Reference,Amount\n2026-10-15,AR/6,N/A\n2026-10-15,AR/7,10.00\n"
        parsed = parse_csv(content)
        assert [ln.reference for ln in parsed.lines] == ["AR/7"]
        assert parsed.warnings == ["Row 1: invalid amount (amount='N/A', credit='', debit='')"]

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("2026-10-15", date(2026, 10, 15)),
            ("15-10-2026", date(2026, 10, 15)),
            ("2026/10/15", date(2026, 10, 15)),
            ("15/10/2026", date(2026, 10, 15)),
            ("20261015", date(2026, 10, 15)),
        ],
    )
    def test_supported_date_formats(self, raw, expected):
        parsed = parse_csv(f"Txn Date,Value Date,Amount\n{raw},2026-01-01,1.00\n")
        assert parsed.lines[0].date == expected

    @pytest.mark.parametrize("raw", ["2026-13-45", "15/10", "Oct 15 2026"])
    def test_invalid_dates_warn(self, raw):
        parsed = parse_csv(f"Date,Amount\n{raw},1.00\n")
        assert parsed.lines == []
        assert parsed.warnings == [f"Row 1: invalid date {raw!r}"]

    def test_amount_cell_symbols_sign_and_fallback(self):
        content = (
            "Date,Ref No.,Remarks,Net Amount,Inflow,Outflow\n"
            '2026-10-15,R1,TAKA,"৳1,150.00",,\n'
            "2026-10-15,R2,USD,$20,,\n"
            "2026-10-15,R3,REVERSAL,-500.00,,\n"
            "2026-10-15,R4,SPLIT,,300.00,100.00\n"
            ",,TOTAL ROW WITHOUT DATE,970.00,,\n"
        )
        parsed = parse_csv(content)
        assert [(ln.reference, ln.amount) for ln in parsed.lines] == [
            ("R1", D("1150.00")),
            ("R2", D("20")),
            ("R3", D("-500.00")),
            ("R4", D("200.00")),
        ]
        assert parsed.warnings == []

    def test_missing_date_column_is_reported(self):
        parsed = parse_csv("Reference,Amount\nAR/1,10.00\n")
        assert parsed.lines == []
        assert parsed.warnings == ["No date column in CSV header - no statement lines imported"]

    def test_reimport_dedup_with_seen_hashes(self):
        content = "Date,Trx ID,Narration,Deposit,Withdrawal\n2026-10-15,T1,BKASH,10.00,\n"
        first = parse_csv(content)
        again = parse_csv(content, seen_hashes=set(first.line_hashes))
        assert again.lines == [] and again.duplicate_lines_skipped == 1


class TestCsvSequence:
    CONTENT = "Date,Seq,Amount\n2026-10-15,7,1.00\n2026-10-16,,2.00\n"

    def test_sequence_column_is_tracked(self):
        parsed = parse_csv(self.CONTENT, expected_sequence=7)
        assert parsed.sequence_number == "7"
        assert parsed.warnings == []

    def test_sequence_mismatch(self):
        parsed = parse_bank_feed(self.CONTENT, expected_sequence=8)
        assert parsed.warnings == ["Sequence mismatch: expected 8, got 7"]

    def test_regression_unparseable_sequence_is_flagged(self):
        """Regression: an unparseable sequence silently skipped the audit
        the caller asked for (ValueError swallowed)."""
        parsed = parse_csv("Date,Statement No,Amount\n2026-10-15,A7,1.00\n", expected_sequence=7)
        assert parsed.warnings == ["Sequence check skipped: unparseable sequence 'A7'"]


class TestFeedRouting:
    def test_explicit_csv_format_overrides_detection(self):
        content = "Date,Description,Amount\n2026-10-15,see :61: tag,1.00\n"
        parsed = parse_bank_feed(content, format_type="csv")
        assert parsed.statement_id == "CSV-IMPORT"
        assert parsed.lines[0].narration == "see :61: tag"

    def test_auto_detects_mt940_without_leading_20(self):
        parsed = parse_bank_feed("  \n:25:ACC\n:61:261015C1,00NTRFNONREF//R1\n")
        assert parsed.statement_id == "UNKNOWN"
        assert [ln.reference for ln in parsed.lines] == ["R1"]
