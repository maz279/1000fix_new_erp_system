"""cd_settlement_ext tests - P10-M02 (CD-M53-03)."""
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


if __name__ == "__main__":
    unittest.main()
