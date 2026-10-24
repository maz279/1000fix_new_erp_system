"""M51-core tax tests — P06-M02-T07 (DoD-03: 100% of tax calculation paths).

Every branch of determine_tax/determine_tds is exercised: all five
treatments, rate overrides valid and invalid, rounding half-up per line,
negative/discount-overflow rejection, the Mushak-threshold rule, TDS
categories incl. exempt certificates and unknown categories.
The pure logic imports WITHOUT Odoo (L5-pure), so these run anywhere.
"""

from __future__ import annotations

import sys
import unittest
from decimal import Decimal
from pathlib import Path

import pytest

pytestmark = [pytest.mark.tax, pytest.mark.financial]

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "models"))

from tax_logic import (
    DeterminationError,
    TaxLine,
    determine_tax,
    determine_tds,
)

D = Decimal


class TestDetermineTaxStandard(unittest.TestCase):
    def test_standard_15_single_line(self):
        result = determine_tax([TaxLine("SRV-01", D("1"), D("1000"))])
        self.assertEqual(result.total_taxable, D("1000.00"))
        self.assertEqual(result.total_vat, D("150.00"))
        self.assertEqual(result.total_payable, D("1150.00"))
        self.assertEqual(result.lines[0].treatment, "standard_15")

    def test_standard_15_multi_line_sums(self):
        result = determine_tax(
            [
                TaxLine("A", D("2"), D("150.50")),
                TaxLine("B", D("1"), D("99.99")),
            ]
        )
        self.assertEqual(result.total_taxable, D("400.99"))
        self.assertEqual(result.total_vat, D("60.15"))
        self.assertEqual(result.lines[0].vat_amount, D("45.15"))
        self.assertEqual(result.lines[1].vat_amount, D("15.00"))

    def test_rounding_half_up_per_line(self):
        # 0.05 x 15% = 0.0075 -> 0.01 (half-up, per line, never on total)
        result = determine_tax([TaxLine("X", D("1"), D("0.05"))])
        self.assertEqual(result.lines[0].vat_amount, D("0.01"))

    def test_discount_reduces_taxable(self):
        result = determine_tax([TaxLine("A", D("1"), D("200"), discount=D("50"))])
        self.assertEqual(result.total_taxable, D("150.00"))
        self.assertEqual(result.total_vat, D("22.50"))

    def test_qty_multiplies_before_tax(self):
        result = determine_tax([TaxLine("A", D("3"), D("33.33"))])
        self.assertEqual(result.total_taxable, D("99.99"))
        self.assertEqual(result.total_vat, D("15.00"))


class TestDetermineTaxTreatments(unittest.TestCase):
    def test_zero_rated(self):
        result = determine_tax([TaxLine("EXP", D("1"), D("500"), treatment="zero_rated")])
        self.assertEqual(result.total_vat, D("0.00"))
        self.assertEqual(result.total_payable, D("500.00"))
        self.assertEqual(result.lines[0].treatment, "zero_rated")

    def test_exempt(self):
        result = determine_tax([TaxLine("EXM", D("1"), D("500"), treatment="exempt")])
        self.assertEqual(result.total_vat, D("0.00"))
        self.assertEqual(result.requires_mushak, False)

    def test_reduced_default_rate_is_5(self):
        result = determine_tax([TaxLine("R", D("1"), D("200"), treatment="reduced")])
        self.assertEqual(result.lines[0].rate, D("5"))
        self.assertEqual(result.total_vat, D("10.00"))

    def test_reduced_override_7_5(self):
        result = determine_tax(
            [TaxLine("R", D("1"), D("200"), treatment="reduced", rate_override=D("7.5"))]
        )
        self.assertEqual(result.total_vat, D("15.00"))

    def test_reduced_override_10(self):
        result = determine_tax(
            [TaxLine("R", D("1"), D("100"), treatment="reduced", rate_override=D("10"))]
        )
        self.assertEqual(result.total_vat, D("10.00"))

    def test_truncated_flags_register(self):
        result = determine_tax([TaxLine("TRU", D("1"), D("500"), treatment="truncated")])
        self.assertTrue(result.has_truncated)
        self.assertEqual(result.total_vat, D("0.00"))  # fixed base, not ad-valorem


class TestDetermineTaxValidation(unittest.TestCase):
    def test_unknown_treatment_rejected(self):
        with self.assertRaises(DeterminationError):
            determine_tax([TaxLine("A", D("1"), D("1"), treatment="magic")])

    def test_negative_qty_rejected(self):
        with self.assertRaises(DeterminationError):
            determine_tax([TaxLine("A", D("-1"), D("1"))])

    def test_negative_price_rejected(self):
        with self.assertRaises(DeterminationError):
            determine_tax([TaxLine("A", D("1"), D("-5"))])

    def test_negative_discount_rejected(self):
        with self.assertRaises(DeterminationError):
            determine_tax([TaxLine("A", D("1"), D("5"), discount=D("-1"))])

    def test_discount_above_line_rejected(self):
        with self.assertRaises(DeterminationError):
            determine_tax([TaxLine("A", D("1"), D("5"), discount=D("6"))])

    def test_standard_rate_override_rejected(self):
        with self.assertRaises(DeterminationError):
            determine_tax(
                [TaxLine("A", D("1"), D("100"), treatment="standard_15", rate_override=D("10"))]
            )

    def test_nonzero_exempt_rate_rejected(self):
        with self.assertRaises(DeterminationError):
            determine_tax(
                [TaxLine("A", D("1"), D("100"), treatment="exempt", rate_override=D("5"))]
            )

    def test_nonzero_zero_rated_rate_rejected(self):
        with self.assertRaises(DeterminationError):
            determine_tax(
                [TaxLine("A", D("1"), D("100"), treatment="zero_rated", rate_override=D("5"))]
            )

    def test_unscheduled_reduced_rate_rejected(self):
        with self.assertRaises(DeterminationError):
            determine_tax(
                [TaxLine("A", D("1"), D("100"), treatment="reduced", rate_override=D("12"))]
            )


class TestMushakThreshold(unittest.TestCase):
    def test_mushak_required_when_vat_applies(self):
        result = determine_tax([TaxLine("A", D("1"), D("10"))])
        self.assertTrue(result.requires_mushak)

    def test_mushak_required_above_25000_even_without_vat(self):
        result = determine_tax([TaxLine("EXM", D("1"), D("25000.01"), treatment="exempt")])
        self.assertTrue(result.requires_mushak)

    def test_no_mushak_below_threshold_without_vat(self):
        result = determine_tax([TaxLine("EXM", D("1"), D("25000.00"), treatment="exempt")])
        self.assertFalse(result.requires_mushak)


class TestDetermineTds(unittest.TestCase):
    def test_service_general_10(self):
        result = determine_tds("service_general", D("10000"))
        self.assertEqual(result.rate, D("10"))
        self.assertEqual(result.tds_amount, D("1000.00"))

    def test_supply_of_goods_5(self):
        result = determine_tds("supply_of_goods", D("10000"))
        self.assertEqual(result.tds_amount, D("500.00"))

    def test_transport_3(self):
        result = determine_tds("transport", D("10000"))
        self.assertEqual(result.tds_amount, D("300.00"))

    def test_rent_commercial_15(self):
        result = determine_tds("rent_commercial", D("10000"))
        self.assertEqual(result.tds_amount, D("1500.00"))

    def test_exempt_certificate_zero_deduction(self):
        result = determine_tds("service_general", D("10000"), exempt_certificate=True)
        self.assertEqual(result.tds_amount, D("0.00"))
        self.assertTrue(result.exempt)

    def test_rounding_half_up(self):
        result = determine_tds("service_general", D("333.33"))
        # 333.33 * 10% = 33.333 -> 33.33
        self.assertEqual(result.tds_amount, D("33.33"))

    def test_unknown_category_rejected(self):
        with self.assertRaises(DeterminationError):
            determine_tds("unknown_category", D("100"))

    def test_negative_base_rejected(self):
        with self.assertRaises(DeterminationError):
            determine_tds("service_general", D("-1"))


class TestCallDirectionContract(unittest.TestCase):
    def test_logic_has_no_odoo_imports(self):
        """AR-006: M20/M52 call M51 synchronously — the engine must be a
        pure computation importable by any layer (and by services/)."""
        import inspect

        import tax_logic

        source = inspect.getsource(tax_logic)
        self.assertNotIn("from odoo", source)
        self.assertNotIn("import odoo", source)


if __name__ == "__main__":
    unittest.main()
