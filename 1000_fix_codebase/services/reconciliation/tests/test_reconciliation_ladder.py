"""Reconciliation ladder (R1..R4) — double-settlement guards, settlement
windows, reference boundaries, the smoke CLI, and the package entry point."""

from __future__ import annotations

import importlib.util
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

pytestmark = [pytest.mark.financial]

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

import reconciliation as recon
from reconciliation import OpenItem, StatementLine, reconcile

D = Decimal
TODAY = date(2026, 10, 2)


def item(ref: str, amount: str, customer: str = "Rahim Uddin", days_ago: int = 1) -> OpenItem:
    return OpenItem(ref, customer, D(amount), TODAY - timedelta(days=days_ago))


class TestGatewayBatchR4:
    def test_regression_batch_settles_every_invoice_it_covers(self):
        """Regression: an R4 batch line whose amount equalled the SUM of the
        open items marked only the FIRST item as taken. The other invoices
        in the batch stayed open, so a later line matched one of them again
        — the same money settled twice."""
        result = reconcile(
            [
                StatementLine(TODAY, D("1650.00"), reference="BKASH BATCH 88"),
                StatementLine(TODAY, D("500.00"), reference="AR/2"),
            ],
            [item("AR/1", "1150.00"), item("AR/2", "500.00")],
        )
        batch = result.matches[0]
        assert (batch.rule, batch.item_ref, batch.item_refs) == ("R4", "AR/1", ("AR/1", "AR/2"))
        assert batch.detail == "gateway settlement batch: AR/1, AR/2"
        assert len(result.matches) == 1
        assert result.manual == [1]  # never re-settles AR/2
        assert result.match_rate == 50.0

    def test_batch_sum_counts_only_items_inside_the_settlement_window(self):
        result = reconcile(
            [
                StatementLine(TODAY, D("1150.00"), narration="NAGAD SETTLEMENT 12"),
                StatementLine(TODAY, D("500.00"), reference="AR/9"),
            ],
            [item("AR/1", "1150.00"), item("AR/9", "500.00", days_ago=60)],
        )
        assert [(m.rule, m.item_refs or (m.item_ref,)) for m in result.matches] == [
            ("R4", ("AR/1",)),
            ("R1", ("AR/9",)),
        ]

    def test_batch_amount_mismatch_falls_through_the_ladder(self):
        result = reconcile(
            [StatementLine(TODAY, D("500.00"), reference="SSLC 2026-10-02")],
            [item("AR/1", "1150.00"), item("AR/2", "500.00")],
        )
        assert [(m.rule, m.item_ref) for m in result.matches] == [("R2", "AR/2")]

    def test_zero_gateway_line_with_nothing_in_window_goes_to_manual(self):
        result = reconcile(
            [StatementLine(TODAY, D("0.00"), reference="ROCKET NIL BATCH")],
            [item("AR/1", "0.00", days_ago=90)],
        )
        assert result.matches == []
        assert result.manual == [0]


class TestReferenceRuleR1:
    def test_regression_reference_must_match_as_a_whole_token(self):
        """Regression: R1 tested `ref in text`, so invoice AR/1 matched a
        payment referencing AR/10 (same amount) — customer A's invoice was
        marked paid by customer B's money."""
        result = reconcile(
            [
                StatementLine(TODAY, D("500.00"), reference="AR/10"),
                StatementLine(TODAY, D("500.00"), narration="PAYMENT FOR AR/1."),
            ],
            [item("AR/1", "500.00", "Customer A"), item("AR/10", "500.00", "Customer B")],
        )
        assert [(m.line_index, m.rule, m.item_ref) for m in result.matches] == [
            (0, "R1", "AR/10"),
            (1, "R1", "AR/1"),
        ]

    def test_reference_match_is_case_insensitive(self):
        result = reconcile(
            [StatementLine(TODAY, D("75.00"), reference="inv-ar/77 paid")],
            [item("AR/77", "75.00", days_ago=25)],
        )
        assert [(m.rule, m.item_ref) for m in result.matches] == [("R1", "AR/77")]

    def test_ref_helper_boundaries(self):
        assert recon._ref_in("AR/1", "AR/1")
        assert recon._ref_in("ar/1", "PAID AR/1/PART")
        assert not recon._ref_in("AR/1", "AR/10")
        assert not recon._ref_in("AR/1", "XAR/1")


class TestCustomerRuleR3:
    def test_no_customer_token_goes_to_manual(self):
        result = reconcile(
            [StatementLine(TODAY, D("500.00"), narration="NEFT XYZ")],
            [item("AR/1", "500.00", customer="Rahim Traders", days_ago=20)],
        )
        assert result.manual == [0]


class TestSmokeMain:
    def test_main_prints_the_day_summary(self, capsys):
        recon.main()
        assert capsys.readouterr().out == "matched=2 manual=[2, 3] rate=50.0% gate=FAIL\n"


def _load_package():
    name = "reconciliation_pkg"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(
        name, SRC / "__init__.py", submodule_search_locations=[str(SRC)]
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class TestPackageEntryPoint:
    def test_package_exports_and_relative_imports(self):
        pkg = _load_package()
        for symbol in pkg.__all__:
            assert getattr(pkg, symbol) is not None, symbol
        parser_mod = sys.modules["reconciliation_pkg.bank_feed_parser"]
        assert parser_mod.StatementLine is pkg.StatementLine
        assert pkg.TARGET_MATCH_RATE == 90

    def test_package_end_to_end_feed_to_match(self):
        pkg = _load_package()
        parsed = pkg.parse_bank_feed(
            ":20:S\n:61:261002C1150,00NTRFNONREF//AR/101\n:86:RAHIM\n:62F:C261002BDT1150,00"
        )
        result = pkg.reconcile(parsed.lines, [pkg.OpenItem("AR/101", "Rahim", D("1150.00"), TODAY)])
        assert [(m.rule, m.item_ref) for m in result.matches] == [("R1", "AR/101")]
        assert result.meets_gate
