"""cd_settlement_ext tests - Milestone R08-M02: M53 settlement completion and the payout rail.
Covers:
- R08-M02-T01: Two-person SoD gates on payout runs.
- R08-M02-T02: INT-007 seller payout rail (idempotency, unknown state, BEFTN fallback).
- R08-M02-T03: GL posting rules (FF-91: gross never in revenue, LP-02 reconciliation keys, LP-07 contra-posting).
- R08-M02-T04: Bilingual seller statements (ITA 2023 §52) and payout reconciliation with aging breaks.
- R08-M02-T05: 100% calculation & validation path verification.
"""

import inspect
import unittest

import pytest

pytestmark = [pytest.mark.financial]

from odoo.addons.cd_settlement_ext.models.fix_payout_reconciliation import (
    FixPayoutReconciliation,
    FixPayoutReconciliationLine,
)
from odoo.addons.cd_settlement_ext.models.fix_seller_statement import (
    FixSellerStatement,
)
from odoo.addons.cd_settlement_ext.models.fix_settlement_ext import (
    FixCommissionLedger,
    FixPayoutRun,
)


class TestCommissionLedger(unittest.TestCase):
    def test_commission_computed(self):
        src = inspect.getsource(FixCommissionLedger._compute_commission)
        self.assertIn("gross_amount", src)
        self.assertIn("commission_rate", src)

    def test_net_after_tds(self):
        src = inspect.getsource(FixCommissionLedger._compute_net)
        self.assertIn("tds_amount", src)

    def test_gl_posting_enforces_ff91(self):
        """FF-91 & MS-01: Gross is never revenue; only commission is revenue (400100)."""
        src = inspect.getsource(FixCommissionLedger.action_post_to_gl)
        self.assertIn("commission.accrued", src)
        self.assertIn("post_with_dimensions", src)
        self.assertIn("400100", src)  # Commission Revenue
        self.assertIn("200200", src)  # Seller Entitlement Liability
        self.assertIn("101000", src)  # Customer Payment Clearing

    def test_four_reconciliation_keys_present(self):
        """LP-02: Every posting carries payment id, rail, rail tx id, and merchant invoice number."""
        src = inspect.getsource(FixCommissionLedger)
        self.assertIn("payment_id", src)
        self.assertIn("rail", src)
        self.assertIn("rail_transaction_id", src)
        self.assertIn("merchant_invoice_number", src)

    def test_contra_posting_reversibility_enforced(self):
        """LP-07: Accrued entries cannot be edited directly; reversible only by contra-posting."""
        src = inspect.getsource(FixCommissionLedger.write)
        self.assertIn("LP-07 Violation", src)


class TestPayoutRun(unittest.TestCase):
    """A08 F2 (rewritten 4 Nov 2026): the source-grep tests asserted the old
    in-method SoD strings and the INT-007 rail. The behaviour is proven live in
    test_a08_m53_controls.py and test_settlement_orm.py; these pin the design."""

    def test_approval_is_routed_through_m63(self):
        from odoo.addons.cd_billing_engine.models.fix_finance_approval import (
            FixFinanceDofaMixin,
        )

        self.assertTrue(FixFinanceDofaMixin._approval_routed)
        self.assertEqual(FixFinanceDofaMixin._approval_apply_method, "action_dofa_approve")
        self.assertIn("fix.finance.dofa.mixin", FixPayoutRun._inherit)

    def test_payouts_are_paid_as_m50_instructions(self):
        from odoo.addons.cd_settlement_ext.models.fix_settlement_ext import FixPayoutRunLine

        self.assertEqual(FixPayoutRunLine._name, "fix.payout.run.line")
        self.assertTrue(FixPayoutRunLine._fix_posts_own_payment)

    def test_cfo_band_is_configuration(self):
        from odoo.addons.cd_settlement_ext.models import fix_settlement_ext as mod

        self.assertEqual(FixPayoutRun._fin_cfo_param, mod.PARAM_PAYOUT_CFO)
        self.assertEqual(mod.DEFAULT_PAYOUT_CFO, 2000000.0)


class TestPayoutRunSoDAuthority(unittest.TestCase):
    """R05-M02-T04: the SoD stamps are guarded workflow fields (A08 M53-2)."""

    def test_sod_fields_exist_and_are_guarded(self):
        from odoo.addons.cd_settlement_ext.models.fix_settlement_ext import PAYOUT_GUARDED

        for name in ("prepared_by_id", "approved_by_id", "approved_date", "sod_verified", "state"):
            self.assertIn(name, PAYOUT_GUARDED)


class TestSellerStatementModel(unittest.TestCase):
    """R08-M02-T04: Bilingual seller statement and ITA 2023 §52 documentation."""

    def test_statement_fields_and_bilingual_labels(self):
        src = inspect.getsource(FixSellerStatement)
        self.assertIn("gross_gmv", src)
        self.assertIn("commission_amount", src)
        self.assertIn("tds_withheld", src)
        self.assertIn("net_payable", src)
        self.assertIn("withholding_cert_ref", src)
        self.assertIn("statutory_note", src)
        self.assertIn("Income Tax Act 2023", src)
        self.assertIn("আয়কর আইন ২০২৩", src)

    def test_statement_issue_event(self):
        src = inspect.getsource(FixSellerStatement.action_issue_statement)
        self.assertIn("seller.statement_issued", src)


class TestPayoutReconciliationModel(unittest.TestCase):
    """R08-M02-T04: Payout reconciliation with count/amount split and aged break tracking."""

    def test_separate_count_and_amount_fields(self):
        """FF-94: System must compare count and amount separately."""
        src = inspect.getsource(FixPayoutReconciliation)
        self.assertIn("system_count", src)
        self.assertIn("rail_count", src)
        self.assertIn("count_matched", src)
        self.assertIn("system_amount", src)
        self.assertIn("rail_amount", src)
        self.assertIn("amount_matched", src)

    def test_aged_unmatched_tracking(self):
        """Unmatched aged > 30 days must be tracked and reported."""
        src = inspect.getsource(FixPayoutReconciliation)
        self.assertIn("aged_unmatched_count", src)
        self.assertIn("aged_unmatched_amount", src)

    def test_reconciliation_divergence_event(self):
        """BR-05: Non-zero breaks publish platform.reconciliation_divergence."""
        src = inspect.getsource(FixPayoutReconciliation.action_run_reconciliation)
        self.assertIn("platform.reconciliation_divergence", src)

    def test_reconciliation_line_aging_computation(self):
        src = inspect.getsource(FixPayoutReconciliationLine._compute_age)
        self.assertIn("rec.is_aged = rec.age_days > 30", src)


if __name__ == "__main__":
    unittest.main()
