# cd_payroll_bd tests — P08-M03 (CD-M56-01). DoD-03/DoD-04 companions.
import inspect
import unittest

import pytest

pytestmark = [pytest.mark.financial, pytest.mark.tax]

from odoo.addons.cd_payroll_bd.models.fix_payroll import FixBeftnBatch, FixPayrollPeriod, FixPayslip


class TestJourneyThirteenGuards(unittest.TestCase):
    """The cycle: lock -> calculate -> approve -> BEFTN -> payslips -> post."""

    def test_no_calculation_without_attendance_lock(self):
        src = inspect.getsource(FixPayrollPeriod.action_verify_attendance_locked)
        self.assertIn("fix.attendance.lock", src)
        self.assertIn("may not calculate on open attendance", src)

    def test_state_guards(self):
        for method, needed in (
            ("action_calculate", "attendance_locked"),
            ("action_approve", "calculated"),
            ("action_pay", "approved"),
            ("action_post", "paid"),
        ):
            src = inspect.getsource(getattr(FixPayrollPeriod, method))
            self.assertIn(needed, src, method)

    def test_events_full_cycle(self):
        src = inspect.getsource(FixPayrollPeriod)
        for event in (
            "payroll.attendance_locked",
            "payroll.approved",
            "payroll.beftn_submitted",
            "payroll.posted",
        ):
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

    def test_beftn_generation_invokes_engine(self):
        src = inspect.getsource(FixBeftnBatch.action_generate_beftn_file)
        self.assertIn("generate_beftn_batch_file", src)
        self.assertIn("validate_routing_number", src)
        self.assertIn("BeftnEntry", src)
        self.assertIn("BeftnBatchHeader", src)


class TestMakerCheckerSoD(unittest.TestCase):
    def test_approval_enforces_maker_checker_sod(self):
        src = inspect.getsource(FixPayrollPeriod.action_approve)
        self.assertIn("calculator_id", src)
        self.assertIn("Maker-Checker SoD violation", src)

    # test_calculator_recorded_on_calculate (a source-text assertion) was
    # retired in the A09 P0 fix: calculate now stamps the calculator through
    # the guard. The behaviour is asserted live, as a non-admin officer, in
    # test_a09_p0_payroll_controls.py::test_calculate_stamps_the_officer and
    # test_payroll_orm.py::test_full_cycle_lock_calculate_approve_pay_post.


class TestDoubleEntryGLPosting(unittest.TestCase):
    def test_post_checks_debit_credit_balance(self):
        src = inspect.getsource(FixPayrollPeriod.action_post)
        self.assertIn("total_debit", src)
        self.assertIn("total_credit", src)
        self.assertIn("GL Unbalanced", src)


class TestSeparationAndRetrenchment(unittest.TestCase):
    def test_retrenchment_uses_act_2006(self):
        src = inspect.getsource(FixPayslip.action_compute_retrenchment)
        self.assertIn("retrenchment_compensation", src)


class TestWave2And4PayrollStatutory(unittest.TestCase):
    def test_contract_allowances_on_payslip(self):
        for f in (
            "house_rent",
            "medical_allowance",
            "conveyance_allowance",
            "technical_allowance",
            "other_allowance",
            "dearness_allowance",
            "adhoc_allowance",
        ):
            self.assertTrue(hasattr(FixPayslip, f))

    def test_wppf_allocation_80_10_10_split(self):
        from odoo.addons.cd_payroll_bd.models.fix_payroll_ops import FixWppfAllocation

        src = inspect.getsource(FixWppfAllocation._compute_wppf_split)
        self.assertIn("0.05", src)
        self.assertIn("0.80", src)
        self.assertIn("0.10", src)
        self.assertIn("2.0 / 3.0", src)

    def test_certificate_and_withholding_return_reconciliation(self):
        from odoo.addons.cd_payroll_bd.models.fix_payroll_ops import (
            FixPayrollCertificate,
            FixWithholdingReturn,
        )

        self.assertTrue(hasattr(FixPayrollCertificate, "action_compute_from_payslips"))
        self.assertTrue(hasattr(FixWithholdingReturn, "action_reconcile_payslips"))


if __name__ == "__main__":
    unittest.main()
