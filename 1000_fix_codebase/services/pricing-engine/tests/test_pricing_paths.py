"""pricing-engine — remaining price paths (DoD-03) and reduction guards."""

from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

import pytest

pytestmark = [pytest.mark.financial]

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pricing_engine import (
    PriceRequest,
    PriceRequestLine,
    PricingError,
    RateCardLine,
    price,
)

D = Decimal
CARDS = [
    RateCardLine("SRV-AC-CLEAN", "labour", D("500.00"), min_tier=1),
    RateCardLine("SRV-AC-CLEAN", "labour", D("400.00"), min_tier=99),
    RateCardLine("PART-COMP", "part", D("2000.00"), min_tier=1),
]
CATALOGUE = {"PART-FAN": D("800.00"), "FREE-CHECK": D("0.00")}


def _line(code: str, qty: str = "1", line_type: str = "part") -> PriceRequestLine:
    return PriceRequestLine(code, D(qty), line_type)


class TestRateResolutionFallthrough:
    def test_contract_customer_without_contract_line_gets_tier_rate(self):
        result = price(
            PriceRequest(customer_tier=2, contract_no="CTR-77", lines=(_line("PART-COMP"),)),
            CARDS,
            CATALOGUE,
        )
        assert (result.lines[0].unit_price, result.lines[0].basis) == (D("2000.00"), "tier")

    def test_contract_customer_falls_back_to_catalogue(self):
        result = price(
            PriceRequest(customer_tier=0, contract_no="CTR-77", lines=(_line("PART-FAN"),)),
            CARDS,
            CATALOGUE,
        )
        assert (result.lines[0].unit_price, result.lines[0].basis) == (D("800.00"), "catalogue")


class TestZeroSubtotal:
    def test_empty_request_prices_to_zero(self):
        result = price(PriceRequest(loyalty_points_to_redeem=50), CARDS, CATALOGUE)
        assert (result.subtotal, result.loyalty_credit, result.total) == (D("0"), D("0"), D("0"))
        assert result.audit == ["subtotal 0; discounts 0; privilege 0; loyalty 0; total 0.00"]

    def test_free_line_skips_the_cap_division(self):
        result = price(
            PriceRequest(line_discount_pct=D("25"), lines=(_line("FREE-CHECK"),)),
            CARDS,
            CATALOGUE,
        )
        assert result.total == D("0.00")
        assert result.lines[0].discount_amount == D("0.00")


class TestRounding:
    def test_half_up_on_gross_discount_and_privilege(self):
        result = price(
            PriceRequest(
                customer_tier=1,
                line_discount_pct=D("2.5"),
                lines=(_line("SRV-AC-CLEAN", qty="1.333", line_type="labour"),),
            ),
            CARDS,
            CATALOGUE,
        )
        line = result.lines[0]
        assert line.gross == D("666.50")  # 1.333 x 500
        assert line.discount_amount == D("16.66")  # 16.6625 -> 16.66
        assert line.privilege_amount == D("16.66")
        assert line.net == D("633.18")
        assert result.total == D("633.18")

    def test_fractional_point_value_credit_is_rounded(self):
        result = price(
            PriceRequest(
                loyalty_points_to_redeem=3, point_value=D("0.335"), lines=(_line("PART-FAN"),)
            ),
            CARDS,
            CATALOGUE,
        )
        assert result.loyalty_credit == D("1.01")  # 1.005 -> 1.01 (half-up)
        assert result.total == D("798.99")


class TestNegativeReductionsRefused:
    def test_regression_negative_loyalty_points_cannot_raise_the_total(self):
        """Regression: redeeming -100 points produced a -100.00 loyalty
        credit; min(credit, pre_total) kept it and the 800.00 part was
        billed at 900.00."""
        with pytest.raises(PricingError, match="can never increase the price"):
            price(
                PriceRequest(loyalty_points_to_redeem=-100, lines=(_line("PART-FAN"),)),
                CARDS,
                CATALOGUE,
            )

    def test_regression_negative_point_value_refused(self):
        with pytest.raises(PricingError):
            price(
                PriceRequest(
                    loyalty_points_to_redeem=10, point_value=D("-5"), lines=(_line("PART-FAN"),)
                ),
                CARDS,
                CATALOGUE,
            )

    def test_regression_negative_line_discount_cannot_bypass_the_cap(self):
        """Regression: a -50% "discount" passed the stacked-discount cap
        (the aggregate was negative) and surcharged the line by 50%."""
        with pytest.raises(PricingError, match="negative discount"):
            price(
                PriceRequest(line_discount_pct=D("-50"), lines=(_line("PART-FAN"),)),
                CARDS,
                CATALOGUE,
            )
