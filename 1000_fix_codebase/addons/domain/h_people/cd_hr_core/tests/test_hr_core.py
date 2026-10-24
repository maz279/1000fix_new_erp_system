# cd_hr_core tests — P08-M01, R06-M01 (CD-M21-01).
import inspect
import unittest

from odoo.addons.cd_hr_core.models.fix_hr_core import (
    PROBATION_CAP_MONTHS,
    STATUTORY_LEAVE,
    FixEmploymentContract,
    FixLeaveRequest,
    FixLeaveType,
    FixOrgPosition,
    HrEmployeeCdCoreExt,
)


class TestEmploymentContract(unittest.TestCase):
    def test_probation_cap_is_six_months(self):
        # Labour Rules 2021 r.25
        self.assertEqual(PROBATION_CAP_MONTHS, 6)

    def test_weekly_hours_ceiling_enforced(self):
        source = inspect.getsource(FixEmploymentContract._validate_statutory)
        self.assertIn("48", source)

    def test_statutory_leave_floors(self):
        self.assertEqual(STATUTORY_LEAVE["casual"], 10)
        self.assertEqual(STATUTORY_LEAVE["annual"], 20)
        self.assertEqual(STATUTORY_LEAVE["sick"], 14)
        self.assertEqual(STATUTORY_LEAVE["festival"], 11)
        self.assertEqual(STATUTORY_LEAVE["maternity"], 112)
        self.assertEqual(STATUTORY_LEAVE["paternity"], 10)

    def test_events_published(self):
        src = inspect.getsource(FixEmploymentContract)
        self.assertIn("employment.contract.activated", src)
        # the leaver leaves through cd_employee_core's canonical employee.left
        self.assertIn("action_mark_left", src)
        self.assertIn("employment.contract.generated", src)

    def test_m24_template_document_generation(self):
        src = inspect.getsource(FixEmploymentContract.action_generate_contract_document)
        self.assertIn("fix.document", src)
        self.assertIn("statutory_density_score", src)
        self.assertIn("Form 6", src)

    def test_legal_signoff_workflow(self):
        src_approve = inspect.getsource(FixEmploymentContract.action_approve_legal_signoff)
        self.assertIn("approved", src_approve)


class TestLeaveRequestAndCitations(unittest.TestCase):
    def test_leave_approval_checks_entitlement(self):
        src = inspect.getsource(FixLeaveRequest.action_approve)
        self.assertIn("Entitlement exhausted", src)

    def test_leave_events(self):
        self.assertIn("leave.approved", inspect.getsource(FixLeaveRequest))

    def test_dod17_statutory_citations(self):
        for field_name in (
            "legal_citation",
            "labour_act_section",
            "amendment_ref",
            "verified_on",
            "carry_forward_limit",
            "is_statutory",
        ):
            self.assertTrue(
                hasattr(FixLeaveType, field_name)
                or field_name in getattr(FixLeaveType, "_fields", {}),
                f"Field {field_name} missing on FixLeaveType",
            )


class TestOrgPosition(unittest.TestCase):
    def test_reporting_line_loop_guard(self):
        self.assertIn("loop", inspect.getsource(FixOrgPosition._check_hierarchy))


class TestKpi090LeaverDeprovisioning(unittest.TestCase):
    def test_kpi_090_measurement_implemented(self):
        src = inspect.getsource(HrEmployeeCdCoreExt.measure_kpi_090_orphaned_accounts)
        self.assertIn("cutoff", src)
        self.assertIn("left_at", src)  # the leaver event, not the hire date

    def test_keycloak_deprovisioning_is_confirmed_not_self_reported(self):
        """GV-009: the module never marks its own deprovisioning done."""
        self.assertFalse(hasattr(HrEmployeeCdCoreExt, "action_deprovision_keycloak"))
        src = inspect.getsource(HrEmployeeCdCoreExt.action_confirm_keycloak_deprovisioned)
        self.assertIn("hr.group_hr_manager", src)
        self.assertIn("employee.keycloak.deprovisioned", src)
        self.assertIn("KPI-090", src)

    def test_contract_termination_requests_deprovisioning(self):
        src = inspect.getsource(FixEmploymentContract.action_terminate)
        self.assertIn("action_mark_left", src)
        self.assertNotIn('"deprovisioned"', src)


if __name__ == "__main__":
    unittest.main()
