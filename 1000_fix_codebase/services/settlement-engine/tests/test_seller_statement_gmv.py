"""Seller statement gross sales value (ITA 2023 §52 statement, DE-17).

The statement's "Gross Sales Value" must be the seller's GMV - the commission
basis - never the commission itself."""

from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

import pytest

pytestmark = [pytest.mark.financial]

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from settlement_engine import (
    EarningEvent,
    PayoutLine,
    SettlementError,
    create_payout_batch,
    generate_seller_statement,
    settle_period,
)

D = Decimal


def test_regression_statement_gmv_is_the_sales_value_not_the_commission():
    """Regression: generate_seller_statement filled gross_gmv with
    payout_line.gross_commission, so a seller with 50,000 BDT of sales was
    certified as having 2,500 BDT gross sales (the 5% commission)."""
    (line,) = settle_period(
        [EarningEvent("SELLER-1", D("50000.00"), "marketplace_gmv", "2026-10-18")], "2026-10"
    )
    assert line.gross_commission == D("2500.00")
    assert line.gross_basis == D("50000.00")
    statement = generate_seller_statement(line)
    assert statement.gross_gmv == D("50000.00")
    assert statement.commission_amount == D("2500.00")
    assert statement.net_payable == D("2182.50")


def test_gross_basis_aggregates_per_seller_within_the_period_only():
    events = [
        EarningEvent("S1", D("1000.10"), "service_labour", "2026-10-01"),
        EarningEvent("S1", D("200000.00"), "marketplace_gmv", "2026-10-20"),
        EarningEvent("S1", D("999.00"), "service_labour", "2026-09-30"),  # other period
        EarningEvent("S2", D("400.00"), "part_margin", "2026-10-05"),
    ]
    batch = create_payout_batch(events, "2026-10", prepared_by="accountant")
    by_seller = {line.seller_ref: line for line in batch.payout_lines}
    assert by_seller["S1"].gross_basis == D("201000.10")
    assert by_seller["S2"].gross_basis == D("400.00")
    assert generate_seller_statement(by_seller["S2"]).gross_gmv == D("400.00")


def test_explicit_gross_gmv_is_used_when_the_line_carries_none():
    line = PayoutLine("S9", "2026-10", D("100.00"), D("10.00"), D("2.70"), D("87.30"))
    assert line.gross_basis is None
    statement = generate_seller_statement(line, gross_gmv=D("2000.00"))
    assert statement.gross_gmv == D("2000.00")


def test_explicit_gross_gmv_overrides_the_line_value():
    line = PayoutLine("S9", "2026-10", D("100.00"), D("10.00"), D("2.70"), D("87.30"), D("1000.00"))
    assert generate_seller_statement(line, gross_gmv=D("1500.00")).gross_gmv == D("1500.00")


def test_statement_refuses_when_gmv_is_unavailable():
    line = PayoutLine("S9", "2026-10", D("100.00"), D("10.00"), D("2.70"), D("87.30"))
    with pytest.raises(SettlementError, match="gross sales value unavailable for seller 'S9'"):
        generate_seller_statement(line)
