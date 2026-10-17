"""reconciliation tests — P06-M05-T07 (G3-02: >=90% auto-match)."""
from __future__ import annotations

import sys
import unittest
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
import pytest

pytestmark = [pytest.mark.financial]

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bank_feed_parser import (  # noqa: E402
    parse_bank_feed,
    parse_csv,
    parse_mt940,
)
from reconciliation import (  # noqa: E402
    OpenItem,
    ReconResult,
    StatementLine,
    reconcile,
)

D = Decimal
TODAY = date(2026, 10, 2)


def item(ref, amount, customer="Rahim Uddin", days_ago=1):
    return OpenItem(ref, customer, D(amount), TODAY - timedelta(days=days_ago))


class TestRules(unittest.TestCase):
    def test_r1_exact_reference(self):
        result = reconcile(
            [StatementLine(TODAY, D("1150.00"), reference="AR/101 CREDIT")],
            [item("AR/101", "1150.00")])
        self.assertEqual(result.matches[0].rule, "R1")
        self.assertTrue(result.meets_gate)

    def test_r1_reference_in_narration(self):
        result = reconcile(
            [StatementLine(TODAY, D("1150.00"), narration="TRANSFER FOR AR/101")],
            [item("AR/101", "1150.00")])
        self.assertEqual(result.matches[0].rule, "R1")

    def test_r2_amount_and_window_unique(self):
        result = reconcile(
            [StatementLine(TODAY, D("500.00"))],
            [item("AR/1", "500.00"), item("AR/2", "900.00")])
        self.assertEqual(result.matches[0].rule, "R2")

    def test_r2_ambiguous_goes_to_manual(self):
        """Two identical amounts in the window — guessing is forbidden."""
        result = reconcile(
            [StatementLine(TODAY, D("500.00"))],
            [item("AR/1", "500.00", days_ago=1), item("AR/2", "500.00", days_ago=2)])
        self.assertEqual(result.manual, [0])
        self.assertEqual(result.match_rate, 0.0)

    def test_r3_customer_token_loose_window(self):
        result = reconcile(
            [StatementLine(TODAY, D("500.00"), narration="NEFT RAHIM TRADERS")],
            [item("AR/1", "500.00", customer="Rahim Traders Ltd", days_ago=20)])
        self.assertEqual(result.matches[0].rule, "R3")

    def test_r4_gateway_batch(self):
        result = reconcile(
            [StatementLine(TODAY, D("1650.00"), reference="BKASH BATCH 88")],
            [item("AR/1", "1150.00"), item("AR/2", "500.00")])
        self.assertEqual(result.matches[0].rule, "R4")

    def test_r4_rocket_gateway_batch(self):
        result = reconcile(
            [StatementLine(TODAY, D("1650.00"), reference="ROCKET SETTLEMENT BATCH 01")],
            [item("AR/1", "1150.00"), item("AR/2", "500.00")])
        self.assertEqual(result.matches[0].rule, "R4")

    def test_outside_loose_window_manual(self):
        result = reconcile(
            [StatementLine(TODAY, D("500.00"))],
            [item("AR/1", "500.00", days_ago=60)])
        self.assertEqual(result.manual, [0])

    def test_each_item_matches_once(self):
        result = reconcile(
            [StatementLine(TODAY, D("500.00"), reference="AR/1"),
             StatementLine(TODAY, D("500.00"), reference="AR/1")],
            [item("AR/1", "500.00")])
        self.assertEqual(len(result.matches), 1)
        self.assertEqual(result.manual, [1])


class TestGate(unittest.TestCase):
    def test_ninety_percent_scenario_meets_gate(self):
        items = [item(f"AR/{i}", f"{100 + i}.00") for i in range(10)]
        lines = [StatementLine(TODAY, D(f"{100 + i}.00"), reference=f"AR/{i}")
                 for i in range(9)] + [StatementLine(TODAY, D("9.99"), narration="BANK CHARGE")]
        result = reconcile(lines, items)
        self.assertEqual(len(result.matches), 9)
        self.assertGreaterEqual(result.match_rate, 90.0)
        self.assertTrue(result.meets_gate)

    def test_poor_match_fails_gate(self):
        result = reconcile(
            [StatementLine(TODAY, D("1.00")), StatementLine(TODAY, D("2.00"))],
            [item("AR/1", "500.00")])
        self.assertEqual(result.match_rate, 0.0)
        self.assertFalse(result.meets_gate)

    def test_empty_statement_is_full_match(self):
        result = reconcile([], [item("AR/1", "10.00")])
        self.assertTrue(result.meets_gate)

    def test_logic_has_no_odoo_imports(self):
        import inspect
        import reconciliation
        source = inspect.getsource(reconciliation)
        self.assertNotIn("from odoo", source)


class TestBankFeedParser(unittest.TestCase):
    """INT-006: Electronic bank statement import parser tests."""

    def test_parse_mt940_swift_format(self):
        raw_mt940 = """
:20:START20261015
:25:012345678901
:28C:00045/001
:60F:C261001BDT50000,00
:61:2610151015CR1150,00NTRFNONREF//AR/101
:86:CREDIT TRANSFER FROM RAHIM UDDIN
:61:2610151015CR2300,00NTRFNONREF//AR/102
:86:KARIM TRADERS SETTLEMENT
:62F:C261015BDT53450,00
"""
        parsed = parse_mt940(raw_mt940)
        self.assertEqual(parsed.statement_id, "START20261015")
        self.assertEqual(parsed.sequence_number, "00045/001")
        self.assertEqual(parsed.opening_balance, Decimal("50000.00"))
        self.assertEqual(parsed.closing_balance, Decimal("53450.00"))
        self.assertEqual(len(parsed.lines), 2)
        self.assertEqual(parsed.lines[0].reference, "AR/101")
        self.assertEqual(parsed.lines[0].amount, Decimal("1150.00"))
        self.assertEqual(parsed.lines[0].narration, "CREDIT TRANSFER FROM RAHIM UDDIN")

    def test_parse_csv_bangladeshi_commercial_format(self):
        raw_csv = """Date,Reference,Description,Withdrawal,Deposit,Balance
2026-10-15,AR/201,EBL INTERNET BANKING,,4500.00,104500.00
2026-10-15,AR/202,CITY BANK RTGS,,7200.00,111700.00
2026-10-15,CHG-99,EXCISE DUTY,500.00,,111200.00
"""
        parsed = parse_csv(raw_csv)
        self.assertEqual(len(parsed.lines), 3)
        self.assertEqual(parsed.lines[0].reference, "AR/201")
        self.assertEqual(parsed.lines[0].amount, Decimal("4500.00"))
        self.assertEqual(parsed.lines[1].reference, "AR/202")
        self.assertEqual(parsed.lines[1].amount, Decimal("7200.00"))
        self.assertEqual(parsed.lines[2].amount, Decimal("-500.00"))

    def test_deduplication_skips_duplicate_lines(self):
        raw_csv = """Date,Reference,Description,Withdrawal,Deposit,Balance
2026-10-15,AR/201,EBL INTERNET BANKING,,4500.00,104500.00
2026-10-15,AR/201,EBL INTERNET BANKING,,4500.00,104500.00
"""
        parsed = parse_csv(raw_csv)
        self.assertEqual(len(parsed.lines), 1)
        self.assertEqual(parsed.duplicate_lines_skipped, 1)

    def test_end_to_end_parsed_feed_meets_ninety_percent_gate(self):
        # 10 lines, 9 matching open items, 1 bank fee
        feed_content = """Date,Reference,Description,Credit,Debit
2026-10-02,AR/001,Rahim Uddin,1000.00,
2026-10-02,AR/002,Karim Traders,2000.00,
2026-10-02,AR/003,Customer Three,3000.00,
2026-10-02,AR/004,Customer Four,4000.00,
2026-10-02,AR/005,Customer Five,5000.00,
2026-10-02,AR/006,Customer Six,6000.00,
2026-10-02,AR/007,Customer Seven,7000.00,
2026-10-02,AR/008,Customer Eight,8000.00,
2026-10-02,AR/009,Customer Nine,9000.00,
2026-10-02,FEE-01,SMS Alert Charge,,50.00
"""
        parsed = parse_bank_feed(feed_content)
        self.assertEqual(len(parsed.lines), 10)

        open_items = [
            item("AR/001", "1000.00", "Rahim Uddin"),
            item("AR/002", "2000.00", "Karim Traders"),
            item("AR/003", "3000.00", "Customer Three"),
            item("AR/004", "4000.00", "Customer Four"),
            item("AR/005", "5000.00", "Customer Five"),
            item("AR/006", "6000.00", "Customer Six"),
            item("AR/007", "7000.00", "Customer Seven"),
            item("AR/008", "8000.00", "Customer Eight"),
            item("AR/009", "9000.00", "Customer Nine"),
        ]

        result = reconcile(parsed.lines, open_items)
        self.assertEqual(len(result.matches), 9)
        self.assertEqual(result.match_rate, 90.0)
        self.assertTrue(result.meets_gate)


if __name__ == "__main__":
    unittest.main()

