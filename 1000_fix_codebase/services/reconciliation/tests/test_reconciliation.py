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


if __name__ == "__main__":
    unittest.main()
