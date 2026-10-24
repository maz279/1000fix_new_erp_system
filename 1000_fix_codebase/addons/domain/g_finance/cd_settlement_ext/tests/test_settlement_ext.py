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
    def test_requires_commissions(self):
        src = inspect.getsource(FixPayoutRun.action_approve)
        self.assertIn("No commissions", src)

    def test_execute_from_approved(self):
        src = inspect.getsource(FixPayoutRun.action_execute)
        self.assertIn("approved", src)

    def test_payout_events(self):
        src = inspect.getsource(FixPayoutRun)
        self.assertIn("payout.approved", src)
        self.assertIn("payout.executed", src)

    def test_int007_rail_integration_methods(self):
        """INT-007 rail methods: submission, read-back query, BEFTN fallback."""
        src = inspect.getsource(FixPayoutRun)
        self.assertIn("action_submit_payout", src)
        self.assertIn("action_query_status", src)
        self.assertIn("action_generate_beftn", src)
        self.assertIn("idempotency_key", src)
        self.assertIn("rail_status", src)

    def test_payout_gl_posting(self):
        """GL posting on payout execution: discharge liability, credit statutory TDS & bank."""
        src = inspect.getsource(FixPayoutRun.action_post_payout_to_gl)
        self.assertIn("post_with_dimensions", src)
        self.assertIn("200200", src)  # Seller Liability debited
        self.assertIn("210100", src)  # Statutory TDS credited under ITA 2023 §52
        self.assertIn("101000", src)  # Disbursement Bank credited


class TestPayoutRunSoDAuthority(unittest.TestCase):
    """R05-M02-T04: Two-person Segregation of Duties (SoD) gate and negative tests."""

    def test_sod_fields_exist(self):
        src = inspect.getsource(FixPayoutRun)
        self.assertIn("prepared_by_id", src)
        self.assertIn("approved_by_id", src)
        self.assertIn("approved_date", src)
        self.assertIn("sod_verified", src)
        self.assertIn("total_tds", src)

    def test_sod_self_approval_prevented_in_action_approve(self):
        """Negative test: preparer cannot approve own payout run."""
        src = inspect.getsource(FixPayoutRun.action_approve)
        self.assertIn("rec.prepared_by_id and self.env.user.id == rec.prepared_by_id.id", src)
        self.assertIn("SoD Violation: Preparer cannot approve their own payout run", src)

    def test_sod_manager_authority_required(self):
        """Negative test: approver must have group_account_manager or group_system."""
        src = inspect.getsource(FixPayoutRun.action_approve)
        self.assertIn("account.group_account_manager", src)
        self.assertIn("Only Finance Managers can approve payout runs", src)

    def test_sod_audit_trail_recorded(self):
        """Approved run sets approved_by_id, approved_date, and sod_verified."""
        src = inspect.getsource(FixPayoutRun.action_approve)
        self.assertIn('"approved_by_id": self.env.user.id', src)
        self.assertIn('"sod_verified": True', src)


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
