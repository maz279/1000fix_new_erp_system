"""M51-core tax tests — P06-M02-T07 (DoD-03: 100% of tax calculation paths).

Every branch of determine_tax is exercised: all five treatments, rate
overrides valid and invalid, rounding half-up per line, negative/discount-
overflow rejection, the Mushak-threshold rule, and (A08 M51-5) the rates
passed in from the effective-dated master. The in-code TDS schedule
(determine_tds) is gone: withholding is determined from fix.tax.rate only.
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

import tax_logic
from tax_logic import (
    DeterminationError,
    TaxLine,
    VatRates,
    determine_tax,
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

    def test_reduced_without_a_scheduled_rate_is_refused(self):
        # A08 M51-5: a reduced supply used to be guessed at 5%; the tariff row
        # names its scheduled rate, the engine never guesses one.
        with self.assertRaises(DeterminationError):
            determine_tax([TaxLine("R", D("1"), D("200"), treatment="reduced")])

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


class TestRatesFromTheMaster(unittest.TestCase):
    """A08 M51-5: the caller passes the master's rates; nothing is hard-coded."""

    def test_standard_rate_comes_from_the_master(self):
        rates = VatRates(standard=D("10"), reduced=frozenset({D("5")}))
        result = determine_tax([TaxLine("SVC", D("1"), D("1000"))], rates)
        self.assertEqual(result.total_vat, D("100.00"))
        self.assertEqual(result.rates_source, "master")

    def test_reduced_rates_come_from_the_master(self):
        rates = VatRates(standard=D("15"), reduced=frozenset({D("6")}))
        ok = determine_tax(
            [TaxLine("R", D("1"), D("100"), treatment="reduced", rate_override=D("6"))], rates
        )
        self.assertEqual(ok.total_vat, D("6.00"))
        with self.assertRaises(DeterminationError):
            determine_tax(
                [TaxLine("R", D("1"), D("100"), treatment="reduced", rate_override=D("5"))],
                rates,
            )

    def test_no_standard_rate_fails_closed(self):
        with self.assertRaises(DeterminationError):
            determine_tax([TaxLine("SVC", D("1"), D("1"))], VatRates(standard=D("0")))

    def test_legacy_fallback_is_marked(self):
        result = determine_tax([TaxLine("SVC", D("1"), D("100"))])
        self.assertEqual(result.rates_source, "legacy")


class TestNoSecondTdsSchedule(unittest.TestCase):
    def test_in_code_tds_schedule_is_gone(self):
        # M51-5 (T06): the in-code schedule disagreed with the master on rent,
        # contractor and professional fees; it no longer exists.
        self.assertFalse(hasattr(tax_logic, "TDS_DEFAULT_RATES"))
        self.assertFalse(hasattr(tax_logic, "determine_tds"))


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
