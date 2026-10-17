"""settlement-engine tests — P07-M03-T10 (DoD-03: 100% of calculation paths)."""
from __future__ import annotations

import sys
import unittest
from decimal import Decimal
from pathlib import Path
import pytest

pytestmark = [pytest.mark.financial]

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from settlement_engine import (  # noqa: E402
    EarningEvent,
    SettlementError,
    SoDViolationError,
    commission_for,
    settle_period,
    create_payout_batch,
    validate_payout_sod,
    approve_payout_batch,
    execute_payout_batch,
)

D = Decimal


class TestCommission(unittest.TestCase):
    def test_service_labour_10_pct(self):
        line = commission_for(EarningEvent("S1", D("1000.00"), "service_labour", "2026-10-01"))
        self.assertEqual(line.commission, D("100.00"))
        self.assertEqual(line.rate, D("10"))

    def test_part_margin_8_pct(self):
        line = commission_for(EarningEvent("S1", D("500.00"), "part_margin", "2026-10-01"))
        self.assertEqual(line.commission, D("40.00"))

    def test_subscription_reseller_15_pct(self):
        line = commission_for(EarningEvent("S2", D("200.00"), "subscription_reseller", "2026-10-01"))
        self.assertEqual(line.commission, D("30.00"))

    def test_marketplace_kicker_below_threshold(self):
        line = commission_for(EarningEvent("S3", D("100000.00"), "marketplace_gmv", "2026-10-01"))
        self.assertEqual(line.commission, D("5000.00"))  # 5% only

    def test_marketplace_kicker_above_threshold(self):
        line = commission_for(EarningEvent("S3", D("100000.01"), "marketplace_gmv", "2026-10-01"))
        # 5% + 2% kicker
        self.assertEqual(line.rate, D("7"))
        self.assertEqual(line.commission, D("7000.00"))

    def test_unknown_scheme_refused(self):
        with self.assertRaises(SettlementError):
            commission_for(EarningEvent("S1", D("100"), "nope", "2026-10-01"))

    def test_negative_basis_refused(self):
        with self.assertRaises(SettlementError):
            commission_for(EarningEvent("S1", D("-1"), "service_labour", "2026-10-01"))

    def test_rounding_half_up(self):
        line = commission_for(EarningEvent("S1", D("0.05"), "service_labour", "2026-10-01"))
        self.assertEqual(line.commission, D("0.01"))


class TestPayout(unittest.TestCase):
    def test_deduction_order_tds_then_fee(self):
        """gross -> TDS 10% -> fee 3% of after-TDS -> net."""
        payouts = settle_period(
            [EarningEvent("S1", D("1000.00"), "service_labour", "2026-10-15")],
            "2026-10")
        self.assertEqual(len(payouts), 1)
        p = payouts[0]
        self.assertEqual(p.gross_commission, D("100.00"))
        self.assertEqual(p.tds, D("10.00"))            # 10% of 100
        self.assertEqual(p.platform_fee, D("2.70"))    # 3% of 90
        self.assertEqual(p.net_payable, D("87.30"))

    def test_period_filtering(self):
        """Events outside the period are excluded from the payout."""
        payouts = settle_period([
            EarningEvent("S1", D("1000.00"), "service_labour", "2026-09-30"),
            EarningEvent("S1", D("1000.00"), "service_labour", "2026-10-01"),
        ], "2026-10")
        self.assertEqual(len(payouts), 1)
        self.assertEqual(payouts[0].gross_commission, D("100.00"))

    def test_multi_seller_aggregation(self):
        payouts = settle_period([
            EarningEvent("A", D("1000.00"), "service_labour", "2026-10-01"),
            EarningEvent("A", D("1000.00"), "service_labour", "2026-10-02"),
            EarningEvent("B", D("500.00"), "part_margin", "2026-10-03"),
        ], "2026-10")
        self.assertEqual(len(payouts), 2)
        a = next(p for p in payouts if p.seller_ref == "A")
        self.assertEqual(a.gross_commission, D("200.00"))
        self.assertEqual(a.tds, D("20.00"))

    def test_empty_period_empty_payouts(self):
        self.assertEqual(settle_period([], "2026-10"), [])

    def test_pure_no_odoo_imports(self):
        import inspect
        import settlement_engine
        source = inspect.getsource(settlement_engine)
        self.assertNotIn("from odoo", source)
        self.assertNotIn("import sqlite", source)


class TestPayoutRunSoD(unittest.TestCase):
    """R05-M02-T04: Settlement payout-run readiness with two-person Segregation of Duties (SoD)."""

    def setUp(self):
        self.events = [
            EarningEvent("Seller-101", D("5000.00"), "service_labour", "2026-10-05"),
            EarningEvent("Seller-102", D("12000.00"), "part_margin", "2026-10-12"),
        ]

    def test_payout_batch_creation(self):
        batch = create_payout_batch(self.events, "2026-10", prepared_by="acc_clerk_01")
        self.assertEqual(batch.period, "2026-10")
        self.assertEqual(batch.seller_count, 2)
        self.assertEqual(batch.prepared_by, "acc_clerk_01")
        self.assertIsNone(batch.approved_by)
        self.assertEqual(batch.state, "draft")
        self.assertTrue(batch.total_net_payable > D("0.00"))

    def test_payout_batch_missing_preparer(self):
        with self.assertRaises(SettlementError):
            create_payout_batch(self.events, "2026-10", prepared_by="")

    def test_sod_valid_approval(self):
        """Two-person rule: preparer 'acc_clerk_01' is distinct from approver 'cfo_01'."""
        batch = create_payout_batch(self.events, "2026-10", prepared_by="acc_clerk_01")
        approved = approve_payout_batch(batch, approver_id="cfo_01", approver_role="cfo")
        self.assertEqual(approved.state, "approved")
        self.assertEqual(approved.approved_by, "cfo_01")

    def test_sod_negative_self_approval_blocked(self):
        """SoD negative test: preparer attempting to self-approve MUST raise SoDViolationError."""
        batch = create_payout_batch(self.events, "2026-10", prepared_by="acc_clerk_01")
        with self.assertRaises(SoDViolationError) as ctx:
            approve_payout_batch(batch, approver_id="acc_clerk_01", approver_role="cfo")
        self.assertIn("Preparer cannot approve their own payout run", str(ctx.exception))

    def test_sod_negative_unauthorized_role_blocked(self):
        """SoD negative test: unauthorized role (e.g. junior clerk or technician) is blocked."""
        batch = create_payout_batch(self.events, "2026-10", prepared_by="acc_clerk_01")
        with self.assertRaises(SoDViolationError) as ctx:
            approve_payout_batch(batch, approver_id="mgr_02", approver_role="junior_clerk")
        self.assertIn("does not possess payout approval authority", str(ctx.exception))

    def test_sod_negative_empty_approver_blocked(self):
        with self.assertRaises(SoDViolationError):
            validate_payout_sod("user_a", "", "finance_manager")

    def test_empty_payout_batch_approval_blocked(self):
        batch = create_payout_batch([], "2026-10", prepared_by="acc_clerk_01")
        with self.assertRaises(SettlementError) as ctx:
            approve_payout_batch(batch, approver_id="cfo_01", approver_role="cfo")
        self.assertIn("zero commission lines", str(ctx.exception))

    def test_execution_requires_prior_approval(self):
        batch = create_payout_batch(self.events, "2026-10", prepared_by="acc_clerk_01")
        with self.assertRaises(SettlementError):
            execute_payout_batch(batch)  # in draft

        approved = approve_payout_batch(batch, approver_id="cfo_01", approver_role="cfo")
        executed = execute_payout_batch(approved)
        self.assertEqual(executed.state, "executed")


if __name__ == "__main__":
    unittest.main()
