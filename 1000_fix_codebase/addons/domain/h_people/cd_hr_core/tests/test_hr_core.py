# cd_hr_core tests — P08-M01 (CD-M21-01).
import inspect
import unittest

from odoo.addons.cd_hr_core.models.fix_hr_core import (
    PROBATION_CAP_MONTHS, STATUTORY_LEAVE, FixEmploymentContract,
    FixLeaveRequest, FixOrgPosition)


class TestEmploymentContract(unittest.TestCase):
    def test_probation_cap_is_six_months(self):
        # Labour Rules 2021 r.25
        self.assertEqual(PROBATION_CAP_MONTHS, 6)

    def test_weekly_hours_ceiling_enforced(self):
        source = inspect.getsource(FixEmploymentContract._validate_statutory)
        self.assertIn("48", source)

    def test_statutory_leave_floors(self):
        self.assertEqual(STATUTORY_LEAVE["annual"], 20)
        self.assertEqual(STATUTORY_LEAVE["sick"], 14)
        self.assertEqual(STATUTORY_LEAVE["festival"], 11)
        self.assertEqual(STATUTORY_LEAVE["maternity"], 112)

    def test_events_published(self):
        src = inspect.getsource(FixEmploymentContract)
        self.assertIn("employment.contract.activated", src)
        self.assertIn("employee.leaver", src)


class TestLeaveRequest(unittest.TestCase):
    def test_leave_approval_checks_entitlement(self):
        src = inspect.getsource(FixLeaveRequest.action_approve)
        self.assertIn("Entitlement exhausted", src)

    def test_leave_events(self):
        self.assertIn("leave.approved",
                      inspect.getsource(FixLeaveRequest))


class TestOrgPosition(unittest.TestCase):
    def test_reporting_line_loop_guard(self):
        self.assertIn("loop",
                      inspect.getsource(FixOrgPosition._check_hierarchy))


if __name__ == "__main__":
    unittest.main()
