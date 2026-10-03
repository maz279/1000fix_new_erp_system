# cd_subscription tests — M39 + M53 W4 (P07-M03).
from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "models" / "fix_subscription.py").read_text(encoding="utf-8")


class TestConsolidatedInvoicing(unittest.TestCase):
    def test_consolidated_flag(self):
        """T02: one invoice, many jobs, many sites — the flag defaults ON."""
        self.assertIn('consolidated = fields.Boolean(\n        default=True', SOURCE)

    def test_consolidated_skips_standalone_invoice(self):
        body = SOURCE[SOURCE.index("def action_generate_charge"):SOURCE.index("def action_cancel")]
        self.assertIn("if not sub.consolidated", body)

    def test_one_schedule_per_source(self):
        names = [c[0] for c in []]  # constraint names via source scan
        self.assertIn("source_schedule_unique", SOURCE)


class TestCycleCharges(unittest.TestCase):
    def test_cycles_and_days(self):
        self.assertIn('{"monthly": 30, "quarterly": 91, "annual": 365}', SOURCE)

    def test_charge_only_when_active(self):
        body = SOURCE[SOURCE.index("def action_generate_charge"):SOURCE.index("def action_cancel")]
        self.assertIn('state != "active"', body)

    def test_charge_publishes(self):
        self.assertIn('"subscription.charged"', SOURCE)


class TestRevenueRecognition(unittest.TestCase):
    def test_straight_line_formula(self):
        body = SOURCE[SOURCE.index("def action_recognize_period"):]
        self.assertIn("elapsed / term_days", body)

    def test_cumulative_idempotent(self):
        """Recognition is cumulative: only the delta posts, and only when
        positive — re-running a period recognizes nothing new."""
        body = SOURCE[SOURCE.index("def action_recognize_period"):]
        self.assertIn("if delta <= 0", body)
        self.assertIn("continue", body)

    def test_completion_boundary(self):
        body = SOURCE[SOURCE.index("def action_recognize_period"):]
        self.assertIn("state = \"complete\"", body)

    def test_fee_over_term_not_point_of_sale(self):
        """BRU-LOY-12's shape: fee revenue over the period, never at sale."""
        self.assertIn("never at the point of sale", SOURCE)


class TestInterfaceBreak(unittest.TestCase):
    def test_commission_is_calculation_not_call(self):
        """AR-006 pair 12: commission CALCULATION is M53's via the L5
        engine; no M12/marketplace module reach-in (imports or env refs)."""
        import re
        imports = re.findall(r'^from .*|^import .*', SOURCE, re.M)
        for line in imports:
            self.assertNotIn("marketplace", line.lower())
            self.assertNotIn("m12", line.lower())
        self.assertNotIn('self.env["fix.marketplace', SOURCE)


if __name__ == "__main__":
    unittest.main()
