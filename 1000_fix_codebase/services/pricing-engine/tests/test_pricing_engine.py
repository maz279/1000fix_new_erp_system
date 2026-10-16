"""pricing-engine tests — P06-M06-T02/T10 (DoD-03: 100% of price paths)."""
from __future__ import annotations

import sys
import unittest
from decimal import Decimal
from pathlib import Path
import pytest

pytestmark = [pytest.mark.financial]

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pricing_engine import (  # noqa: E402
    PriceRequest,
    PriceRequestLine,
    PricingError,
    RateCardLine,
    price,
)

D = Decimal

CARDS = [
    RateCardLine("SRV-AC-CLEAN", "labour", D("500.00"), min_tier=1),
    RateCardLine("SRV-AC-CLEAN", "labour", D("450.00"), min_tier=3),
    RateCardLine("SRV-AC-CLEAN", "labour", D("400.00"), min_tier=99),
    RateCardLine("PART-COMP", "part", D("2000.00"), min_tier=1),
]
CATALOGUE = {"SRV-AC-CLEAN": D("600.00"), "PART-FAN": D("800.00"),
             "CONS-CLEANER": D("150.00"), "TRP-PICKUP": D("300.00")}


class TestRateResolution(unittest.TestCase):
    def test_catalogue_when_no_card(self):
        result = price(
            PriceRequest(lines=(PriceRequestLine("SRV-AC-CLEAN", D("1"), "labour"),)),
            CARDS, CATALOGUE)
        self.assertEqual(result.lines[0].basis, "catalogue")
        self.assertEqual(result.lines[0].unit_price, D("600.00"))

    def test_tier_rate_wins_over_catalogue(self):
        result = price(
            PriceRequest(customer_tier=1,
                         lines=(PriceRequestLine("SRV-AC-CLEAN", D("1"), "labour"),)),
            CARDS, CATALOGUE)
        self.assertEqual(result.lines[0].unit_price, D("500.00"))
        self.assertEqual(result.lines[0].basis, "tier")

    def test_highest_eligible_tier_rate(self):
        result = price(
            PriceRequest(customer_tier=4,
                         lines=(PriceRequestLine("SRV-AC-CLEAN", D("1"), "labour"),)),
            CARDS, CATALOGUE)
        self.assertEqual(result.lines[0].unit_price, D("450.00"))

    def test_contract_rate_beats_tier(self):
        result = price(
            PriceRequest(customer_tier=2, contract_no="CTR-77",
                         lines=(PriceRequestLine("SRV-AC-CLEAN", D("1"), "labour"),)),
            CARDS, CATALOGUE)
        self.assertEqual(result.lines[0].unit_price, D("400.00"))
        self.assertEqual(result.lines[0].basis, "contract")

    def test_contract_line_ignored_without_contract(self):
        """A contract rate exists, but this customer has no contract — the
        tier rate applies (a card is not a promise to everyone)."""
        result = price(
            PriceRequest(customer_tier=5,
                         lines=(PriceRequestLine("SRV-AC-CLEAN", D("1"), "labour"),)),
            CARDS, CATALOGUE)
        self.assertEqual(result.lines[0].unit_price, D("450.00"))

    def test_unknown_product_refused(self):
        with self.assertRaises(PricingError):
            price(PriceRequest(lines=(PriceRequestLine("NOPE", D("1"), "part"),)),
                  CARDS, CATALOGUE)


class TestReductions(unittest.TestCase):
    def test_labour_privilege_by_tier(self):
        result = price(
            PriceRequest(customer_tier=2,
                         lines=(PriceRequestLine("SRV-AC-CLEAN", D("1"), "labour"),)),
            CARDS, CATALOGUE)
        # tier 2 -> 5% privilege on the tier rate 500
        self.assertEqual(result.lines[0].privilege_amount, D("25.00"))

    def test_privilege_never_on_parts(self):
        """BRU-LOY-01: privilege discounts apply to labour only."""
        result = price(
            PriceRequest(customer_tier=6,
                         lines=(PriceRequestLine("PART-FAN", D("1"), "part"),)),
            CARDS, CATALOGUE)
        self.assertEqual(result.lines[0].privilege_amount, D("0.00"))

    def test_privilege_never_on_consumables_or_transport(self):
        for line_type in ("consumable", "transport"):
            result = price(
                PriceRequest(customer_tier=6,
                             lines=(PriceRequestLine("CONS-CLEANER" if line_type == "consumable" else "TRP-PICKUP",
                                                     D("1"), line_type),)),
                CARDS, CATALOGUE)
            self.assertEqual(result.lines[0].privilege_amount, D("0.00"), line_type)

    def test_privilege_caps_at_15_percent(self):
        result = price(
            PriceRequest(customer_tier=9,
                         lines=(PriceRequestLine("SRV-AC-CLEAN", D("1"), "labour"),)),
            CARDS, CATALOGUE)
        self.assertEqual(result.lines[0].privilege_amount, D("67.50"))  # 15% of 450

    def test_agent_discount_applies_with_cap_check(self):
        result = price(
            PriceRequest(customer_tier=0, line_discount_pct=D("10"),
                         lines=(PriceRequestLine("PART-FAN", D("1"), "part"),)),
            CARDS, CATALOGUE)
        self.assertEqual(result.lines[0].discount_amount, D("80.00"))

    def test_loyalty_credit_reduces_total(self):
        result = price(
            PriceRequest(loyalty_points_to_redeem=100, point_value=D("1"),
                         lines=(PriceRequestLine("PART-FAN", D("1"), "part"),)),
            CARDS, CATALOGUE)
        self.assertEqual(result.loyalty_credit, D("100.00"))
        self.assertEqual(result.total, D("700.00"))

    def test_loyalty_credit_never_negative_total(self):
        result = price(
            PriceRequest(loyalty_points_to_redeem=100000, point_value=D("1"),
                         lines=(PriceRequestLine("PART-FAN", D("1"), "part"),)),
            CARDS, CATALOGUE)
        self.assertEqual(result.total, D("0.00"))

    def test_stack_cap_enforced(self):
        """BRU-LOY-09: aggregate stacked discount above the cap refuses."""
        with self.assertRaises(PricingError):
            price(PriceRequest(customer_tier=6, line_discount_pct=D("20"),
                               loyalty_points_to_redeem=100, point_value=D("2"),
                               lines=(PriceRequestLine("SRV-AC-CLEAN", D("1"), "labour"),)),
                  CARDS, CATALOGUE)

    def test_stack_cap_passes_below(self):
        result = price(
            PriceRequest(customer_tier=2, line_discount_pct=D("5"),
                         lines=(PriceRequestLine("SRV-AC-CLEAN", D("1"), "labour"),)),
            CARDS, CATALOGUE)
        self.assertEqual(result.total, D("450.00"))


class TestTotals(unittest.TestCase):
    def test_multi_line_sums(self):
        result = price(
            PriceRequest(customer_tier=1,
                         lines=(PriceRequestLine("SRV-AC-CLEAN", D("2"), "labour"),
                                PriceRequestLine("PART-COMP", D("1"), "part"))),
            CARDS, CATALOGUE)
        # labour 2x500=1000 -2.5% priv(25) = 975; part 2000; total 2975
        self.assertEqual(result.subtotal, D("3000.00"))
        self.assertEqual(result.total, D("2975.00"))

    def test_audit_trail_complete(self):
        result = price(
            PriceRequest(customer_tier=1,
                         lines=(PriceRequestLine("SRV-AC-CLEAN", D("1"), "labour"),)),
            CARDS, CATALOGUE)
        self.assertTrue(any("SRV-AC-CLEAN" in entry for entry in result.audit))
        self.assertTrue(any("total" in entry for entry in result.audit))

    def test_pure_no_odoo_imports(self):
        import inspect
        import pricing_engine
        source = inspect.getsource(pricing_engine)
        self.assertNotIn("from odoo", source)
        self.assertNotIn("import sqlite", source)


if __name__ == "__main__":
    unittest.main()
