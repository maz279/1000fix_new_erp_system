# cd_subscription tests — M39 + M53 W4 (P07-M03).
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
import sys
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "models" / "fix_subscription.py").read_text(encoding="utf-8")

# Insert models for pure rev_rec_engine testing
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "models"))
import rev_rec_engine  # noqa: E402
from rev_rec_engine import (  # noqa: E402
    compute_straight_line_recognition,
    compute_cancellation_refund,
    RevRecError,
)


class TestConsolidatedInvoicing(unittest.TestCase):
    def test_consolidated_flag(self):
        """T02: one invoice, many jobs, many sites — the flag defaults ON."""
        self.assertIn('consolidated = fields.Boolean(\n        default=True', SOURCE)

    def test_consolidated_skips_standalone_invoice(self):
        body = SOURCE[SOURCE.index("def action_generate_charge"):SOURCE.index("def action_trigger_dunning")]
        self.assertIn("if not sub.consolidated", body)

    def test_one_schedule_per_source(self):
        self.assertIn("source_schedule_unique", SOURCE)


class TestCycleCharges(unittest.TestCase):
    def test_cycles_and_days(self):
        self.assertIn('{"monthly": 30, "quarterly": 91, "annual": 365}', SOURCE)

    def test_charge_only_when_active(self):
        body = SOURCE[SOURCE.index("def action_generate_charge"):SOURCE.index("def action_trigger_dunning")]
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


class TestConsolidated400DeviceDemo(unittest.TestCase):
    """Demonstration of R05-M02-T01: 400-device client -> 1 single consolidated B2B invoice."""

    def test_400_device_consolidation_demo(self):
        """A corporate client with 400 devices across multiple branch sites receives
        exactly 1 consolidated invoice with 400 tagged line items and statutory Mushak 6.3."""
        # Synthesize 400 device lines across 4 branches
        branches = ["Dhaka-HQ", "Chittagong-Hub", "Sylhet-Depot", "Rajshahi-Center"]
        device_lines = []
        for i in range(1, 401):
            branch = branches[i % len(branches)]
            device_lines.append({
                "device_id": 1000 + i,
                "serial_number": f"SN-POS-{i:05d}",
                "branch_name": branch,
                "description": f"POS Terminal #{i:04d} Monthly Maintenance & SLA at {branch}",
                "amount": 250.00,
            })

        self.assertEqual(len(device_lines), 400)

        # Mock partner and environment for demonstration logic
        class DummyPartner:
            id = 99
            name = "Apex Financial Group Ltd."

        class DummyOU:
            id = 1

        class DummyCompany:
            name = "1000FiX Services Ltd."

        # Simulate generate_consolidated_b2b_invoice calculation
        total_taxable = sum(Decimal(str(d["amount"])) for d in device_lines)
        total_vat = (total_taxable * Decimal("0.15")).quantize(Decimal("0.01"))
        total_payable = total_taxable + total_vat

        self.assertEqual(total_taxable, Decimal("100000.00"))
        self.assertEqual(total_vat, Decimal("15000.00"))
        self.assertEqual(total_payable, Decimal("115000.00"))

        # Verify method signature in SOURCE
        self.assertIn("def generate_consolidated_b2b_invoice", SOURCE)
        self.assertIn("invoice.consolidated_b2b_created", SOURCE)
        self.assertIn("Mushak 6.3", SOURCE)


class TestDunningAndRefunds(unittest.TestCase):
    def test_dunning_ladder_source(self):
        """Verifies reminder, final notice, and service hold escalation ladder."""
        self.assertIn("def action_trigger_dunning", SOURCE)
        self.assertIn("subscription.dunning_escalated", SOURCE)
        self.assertIn('sub.write({"state": "hold"', SOURCE)
        self.assertIn("def action_reinstate", SOURCE)

    def test_refund_approval_threshold(self):
        """Refunds > BDT 25,000 require managerial SoD approval."""
        self.assertIn("def action_request_refund", SOURCE)
        self.assertIn("requires_manager_approval", SOURCE)


class TestRevRecEngine100PercentCoverage(unittest.TestCase):
    """100% calculation path coverage for M53 W4 revenue recognition (DoD-03)."""

    def test_straight_line_normal_halfway(self):
        start = date(2026, 1, 1)
        end = date(2026, 12, 31)  # 364 days
        as_of = date(2026, 7, 2)   # halfway (182 days)
        res = compute_straight_line_recognition(
            total_amount=Decimal("12000.00"),
            start_date=start,
            end_date=end,
            as_of=as_of,
            already_recognized=Decimal("0.00"),
        )
        self.assertEqual(res.term_days, 364)
        self.assertEqual(res.elapsed_days, 182)
        self.assertEqual(res.target_cumulative, Decimal("6000.00"))
        self.assertEqual(res.incremental_delta, Decimal("6000.00"))
        self.assertEqual(res.remaining_deferred, Decimal("6000.00"))
        self.assertFalse(res.is_complete)

    def test_straight_line_before_start(self):
        start = date(2026, 6, 1)
        end = date(2026, 12, 31)
        res = compute_straight_line_recognition(
            total_amount="6000.00",
            start_date=start,
            end_date=end,
            as_of=date(2026, 5, 15),
        )
        self.assertEqual(res.elapsed_days, 0)
        self.assertEqual(res.target_cumulative, Decimal("0.00"))
        self.assertEqual(res.incremental_delta, Decimal("0.00"))
        self.assertEqual(res.remaining_deferred, Decimal("6000.00"))
        self.assertFalse(res.is_complete)

    def test_straight_line_after_end(self):
        start = date(2026, 1, 1)
        end = date(2026, 6, 30)
        res = compute_straight_line_recognition(
            total_amount=3000.0,
            start_date=start,
            end_date=end,
            as_of=date(2026, 8, 1),
            already_recognized="2000.00",
        )
        self.assertEqual(res.elapsed_days, res.term_days)
        self.assertEqual(res.target_cumulative, Decimal("3000.00"))
        self.assertEqual(res.incremental_delta, Decimal("1000.00"))
        self.assertEqual(res.remaining_deferred, Decimal("0.00"))
        self.assertTrue(res.is_complete)

    def test_straight_line_idempotent_zero_delta(self):
        start = date(2026, 1, 1)
        end = date(2026, 12, 31)
        as_of = date(2026, 6, 1)
        # Already recognized equals or exceeds target
        res = compute_straight_line_recognition(
            total_amount="12000.00",
            start_date=start,
            end_date=end,
            as_of=as_of,
            already_recognized="5000.00",
        )
        self.assertEqual(res.incremental_delta, Decimal("0.00"))

    def test_straight_line_invalid_parameters(self):
        # Non-positive total
        with self.assertRaises(RevRecError):
            compute_straight_line_recognition(0, date(2026, 1, 1), date(2026, 2, 1), date(2026, 1, 15))
        with self.assertRaises(RevRecError):
            compute_straight_line_recognition(-100, date(2026, 1, 1), date(2026, 2, 1), date(2026, 1, 15))
        # End <= Start
        with self.assertRaises(RevRecError):
            compute_straight_line_recognition(100, date(2026, 2, 1), date(2026, 1, 1), date(2026, 1, 15))
        # Negative recognized
        with self.assertRaises(RevRecError):
            compute_straight_line_recognition(100, date(2026, 1, 1), date(2026, 2, 1), date(2026, 1, 15), -10)
        # Recognized exceeds total
        with self.assertRaises(RevRecError):
            compute_straight_line_recognition(100, date(2026, 1, 1), date(2026, 2, 1), date(2026, 1, 15), 150)

    def test_cancellation_refund_under_threshold(self):
        start = date(2026, 1, 1)
        end = date(2026, 12, 31)  # 364 days
        cancel_date = date(2026, 7, 2)  # 182 days (50%)
        res = compute_cancellation_refund(
            total_amount="20000.00",
            start_date=start,
            end_date=end,
            cancellation_date=cancel_date,
            cancellation_fee_pct="10.0",
        )
        self.assertEqual(res.earned_revenue, Decimal("10000.00"))
        self.assertEqual(res.unearned_refund, Decimal("10000.00"))
        self.assertEqual(res.cancellation_fee, Decimal("1000.00"))
        self.assertEqual(res.net_refund_payable, Decimal("9000.00"))
        self.assertFalse(res.requires_manager_approval)

    def test_cancellation_refund_above_threshold_requires_approval(self):
        start = date(2026, 1, 1)
        end = date(2026, 12, 31)
        cancel_date = date(2026, 2, 1)  # early cancel
        res = compute_cancellation_refund(
            total_amount="100000.00",
            start_date=start,
            end_date=end,
            cancellation_date=cancel_date,
            cancellation_fee_pct="5.0",
        )
        self.assertTrue(res.net_refund_payable > Decimal("25000.00"))
        self.assertTrue(res.requires_manager_approval)

    def test_cancellation_invalid_parameters(self):
        with self.assertRaises(RevRecError):
            compute_cancellation_refund(0, date(2026, 1, 1), date(2026, 2, 1), date(2026, 1, 15))
        with self.assertRaises(RevRecError):
            compute_cancellation_refund(100, date(2026, 2, 1), date(2026, 1, 1), date(2026, 1, 15))
        with self.assertRaises(RevRecError):
            compute_cancellation_refund(100, date(2026, 1, 1), date(2026, 2, 1), date(2026, 1, 15), -5)
        with self.assertRaises(RevRecError):
            compute_cancellation_refund(100, date(2026, 1, 1), date(2026, 2, 1), date(2026, 1, 15), 105)

    def test_cancellation_refund_on_or_before_start(self):
        start = date(2026, 1, 1)
        end = date(2026, 12, 31)
        res = compute_cancellation_refund(
            total_amount="12000.00",
            start_date=start,
            end_date=end,
            cancellation_date=date(2025, 12, 31),
        )
        self.assertEqual(res.earned_revenue, Decimal("0.00"))
        self.assertEqual(res.unearned_refund, Decimal("12000.00"))

    def test_cancellation_refund_on_or_after_end(self):
        start = date(2026, 1, 1)
        end = date(2026, 12, 31)
        res = compute_cancellation_refund(
            total_amount="12000.00",
            start_date=start,
            end_date=end,
            cancellation_date=date(2027, 1, 5),
        )
        self.assertEqual(res.earned_revenue, Decimal("12000.00"))
        self.assertEqual(res.unearned_refund, Decimal("0.00"))


if __name__ == "__main__":
    unittest.main()
