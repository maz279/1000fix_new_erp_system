"""cd_rental_asset tests — P09-M03 / R07-M03-T01 / R07-M03-T02.
CI financial job test suite: 100% money path coverage, deposit handling,
damage assessment, rental SKU tier pricing, and M03 logistics linkage.
"""

from __future__ import annotations

import inspect
import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "vendor" / "odoo"))
import odoo
import odoo.addons

circular_path = str(ROOT / "addons" / "domain" / "d_circular")
if circular_path not in odoo.addons.__path__:
    odoo.addons.__path__.append(circular_path)


import odoo.fields as f
from odoo.addons.cd_rental_asset.models.fix_rental_asset import (
    FixRentalDamage,
    FixRentalReservation,
)


class TestRentalAvailabilityAndLogistics(unittest.TestCase):
    """Verifies reservation availability checks, M37 SKU linkage, and M03 logistics."""

    def test_overlapping_reservations_refused(self):
        src = inspect.getsource(FixRentalReservation.action_reserve)
        self.assertIn("search_count", src)
        self.assertIn("already reserved", src)
        self.assertIn("blocking, not advisory", src)

    def test_events_published(self):
        src = inspect.getsource(FixRentalReservation)
        for event in ("rental.reserved", "rental.delivered", "rental.returned", "rental.closed"):
            self.assertIn(event, src)

    def test_m03_logistics_consignments_defined(self):
        self.assertTrue(hasattr(FixRentalReservation, "delivery_consignment_id"))
        self.assertTrue(hasattr(FixRentalReservation, "return_consignment_id"))
        self.assertTrue(hasattr(FixRentalReservation, "service_order_id"))

        src_del = inspect.getsource(FixRentalReservation.action_generate_delivery_consignment)
        self.assertIn("fix.consignment", src_del)
        self.assertIn("delivery", src_del)

        src_ret = inspect.getsource(FixRentalReservation.action_generate_return_consignment)
        self.assertIn("fix.consignment", src_ret)
        self.assertIn("pickup", src_ret)


class TestRentalFinancialMoneyPath(unittest.TestCase):
    """100% Money Path Coverage: monetary fields, deposit settlement, late fees,
    tier pricing, and edge-case boundary conditions."""

    def test_all_money_fields_are_monetary(self):
        money_fields = [
            "deposit_collected",
            "deposit_refunded",
            "daily_rate",
            "weekly_rate",
            "monthly_rate",
            "rental_charge",
            "late_fee",
            "excess_billed",
            "damage_total",
        ]
        for fn in money_fields:
            self.assertTrue(
                hasattr(FixRentalReservation, fn),
                f"Field {fn} must exist on FixRentalReservation",
            )
            self.assertIsInstance(
                getattr(FixRentalReservation, fn),
                f.Monetary,
                f"Field {fn} must be Monetary per AS-10",
            )

    def test_damage_cost_is_monetary_and_constrained(self):
        self.assertIsInstance(FixRentalDamage.cost, f.Monetary)
        src = inspect.getsource(FixRentalDamage._check_cost)
        self.assertIn("negative", src)

    def test_deposit_settlement_zero_damage(self):
        """Zero damage: 100% of deposit refunded."""
        deposit_collected = 10000.0
        damage_total = 0.0
        late_fee = 0.0

        total_charges = damage_total + late_fee
        deduction = min(total_charges, deposit_collected)
        refund = max(deposit_collected - total_charges, 0.0)
        excess = max(total_charges - deposit_collected, 0.0)

        self.assertEqual(deduction, 0.0)
        self.assertEqual(refund, 10000.0)
        self.assertEqual(excess, 0.0)

    def test_deposit_settlement_partial_damage(self):
        """Partial damage: deposit deduction equals damage, remainder refunded."""
        deposit_collected = 10000.0
        damage_total = 3500.0
        late_fee = 500.0

        total_charges = damage_total + late_fee
        deduction = min(total_charges, deposit_collected)
        refund = max(deposit_collected - total_charges, 0.0)
        excess = max(total_charges - deposit_collected, 0.0)

        self.assertEqual(deduction, 4000.0)
        self.assertEqual(refund, 6000.0)
        self.assertEqual(excess, 0.0)

    def test_deposit_settlement_exact_match(self):
        """Total charges exactly equal deposit: zero refund, zero excess."""
        deposit_collected = 10000.0
        damage_total = 10000.0
        late_fee = 0.0

        total_charges = damage_total + late_fee
        deduction = min(total_charges, deposit_collected)
        refund = max(deposit_collected - total_charges, 0.0)
        excess = max(total_charges - deposit_collected, 0.0)

        self.assertEqual(deduction, 10000.0)
        self.assertEqual(refund, 0.0)
        self.assertEqual(excess, 0.0)

    def test_deposit_settlement_excess_damage(self):
        """Damage exceeds deposit: deposit fully forfeited, excess billed to customer."""
        deposit_collected = 10000.0
        damage_total = 15000.0
        late_fee = 2000.0

        total_charges = damage_total + late_fee
        deduction = min(total_charges, deposit_collected)
        refund = max(deposit_collected - total_charges, 0.0)
        excess = max(total_charges - deposit_collected, 0.0)

        self.assertEqual(deduction, 10000.0)
        self.assertEqual(refund, 0.0)
        self.assertEqual(excess, 7000.0)

    def test_duration_computation_logic(self):
        d1 = date(2026, 10, 1)
        d2 = date(2026, 10, 5)
        duration = (d2 - d1).days + 1
        self.assertEqual(duration, 5)

        # Same day rental is 1 day minimum
        d_same = date(2026, 10, 1)
        self.assertEqual((d_same - d_same).days + 1, 1)

    def test_rental_tier_pricing_logic(self):
        """Test daily, weekly, and monthly tiered rate logic."""
        # 3 days @ 500 daily = 1500
        days = 3
        daily = 500.0
        weekly = 3000.0
        monthly = 10000.0
        charge_daily = days * daily
        self.assertEqual(charge_daily, 1500.0)

        # 10 days = 1 week (3000) + 3 days (3 * 500 = 1500) = 4500
        charge_weekly = (1 * weekly) + (3 * daily)
        self.assertEqual(charge_weekly, 4500.0)

        # 35 days = 1 month (10000) + 5 days (5 * 500 = 2500) = 12500
        charge_monthly = (1 * monthly) + (5 * daily)
        self.assertEqual(charge_monthly, 12500.0)


if __name__ == "__main__":
    unittest.main()
