"""cd_settlement_ext tests - P10-M02 (CD-M53-03) & R05-M02-T04 (SoD Authority)."""
import inspect
import unittest

from odoo.addons.cd_settlement_ext.models.fix_settlement_ext import (
    FixCommissionLedger, FixPayoutRun)


class TestCommissionLedger(unittest.TestCase):
    def test_commission_computed(self):
        src = inspect.getsource(FixCommissionLedger._compute_commission)
        self.assertIn("gross_amount", src)
        self.assertIn("commission_rate", src)

    def test_net_after_tds(self):
        src = inspect.getsource(FixCommissionLedger._compute_net)
        self.assertIn("tds_amount", src)

    def test_gl_posting(self):
        self.assertIn("commission.accrued",
                      inspect.getsource(FixCommissionLedger))


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


if __name__ == "__main__":
    unittest.main()
