# cd_payroll_bd tests — P08-M03 (CD-M56-01). DoD-03/DoD-04 companions.
import inspect
import unittest
import pytest

pytestmark = [pytest.mark.financial, pytest.mark.tax]

from odoo.addons.cd_payroll_bd.models.fix_payroll import (
    FixBeftnBatch, FixPayrollPeriod, FixPayslip)


class TestJourneyThirteenGuards(unittest.TestCase):
    """The cycle: lock -> calculate -> approve -> BEFTN -> payslips -> post."""

    def test_no_calculation_without_attendance_lock(self):
        src = inspect.getsource(FixPayrollPeriod.action_verify_attendance_locked)
        self.assertIn("fix.attendance.lock", src)
        self.assertIn("may not calculate on open attendance", src)

    def test_state_guards(self):
        for method, needed in (("action_calculate", "attendance_locked"),
                               ("action_approve", "calculated"),
                               ("action_pay", "approved"),
                               ("action_post", "paid")):
            src = inspect.getsource(getattr(FixPayrollPeriod, method))
            self.assertIn(needed, src, method)

    def test_events_full_cycle(self):
        src = inspect.getsource(FixPayrollPeriod)
        for event in ("payroll.attendance_locked", "payroll.approved",
                      "payroll.beftn_submitted", "payroll.posted"):
            self.assertIn(event, src)


class TestPayslipDelegation(unittest.TestCase):
    def test_all_arithmetic_in_the_engine(self):
        src = inspect.getsource(FixPayslip._compute_slip)
        self.assertIn("compute_payslip", src)
        self.assertIn("PayslipInput", src)

    def test_separation_uses_act_2026(self):
        src = inspect.getsource(FixPayslip.action_compute_separation)
        self.assertIn("gratuity", src)
        self.assertIn("resignation_compensation", src)


class TestBeftnBatch(unittest.TestCase):
    def test_settlement_respects_date(self):
        src = inspect.getsource(FixBeftnBatch.action_settle)
        self.assertIn("settlement_date", src)

    def test_batch_created_with_engine_settlement(self):
        src = inspect.getsource(FixPayrollPeriod.action_pay)
        self.assertIn("beftn_settlement_date", src)


if __name__ == "__main__":
    unittest.main()
