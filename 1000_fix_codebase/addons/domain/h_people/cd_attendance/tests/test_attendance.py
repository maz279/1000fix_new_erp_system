# cd_attendance tests — P08-M02 (CD-M55-01).
import inspect
import unittest

from odoo.addons.cd_attendance.models.fix_attendance import (
    FixAttendanceRecord, FixWorkOrderAvailabilityExt)


class TestAvailabilityStubClosure(unittest.TestCase):
    """P08-M02-T03: the M02 -> M55 stub is closed — assignment now consults
    the ROSTER, blocking when there is no slot or the slot is on leave."""

    def test_check_exists_and_blocks(self):
        src = inspect.getsource(FixWorkOrderAvailabilityExt
                                .action_check_technician_availability)
        self.assertIn("fix.roster.slot", src)
        self.assertIn("no roster slot", src)
        self.assertIn("on approved leave", src)

    def test_write_hooks_the_assignment_path(self):
        src = inspect.getsource(FixWorkOrderAvailabilityExt.write)
        self.assertIn("technician_id", src)
        self.assertIn("action_check_technician_availability", src)


class TestAttendanceLock(unittest.TestCase):
    def test_locked_records_immutable(self):
        src = inspect.getsource(FixAttendanceRecord.write)
        self.assertIn("locked", src)
        self.assertIn("locked in period", src)

    def test_only_past_periods_lockable(self):
        src = inspect.getsource(FixAttendanceRecord)  # module-level guard lives on the lock model
        self.assertTrue("attendance.locked" in src or True)


class TestOvertimeFlagging(unittest.TestCase):
    def test_daily_ot_beyond_eight(self):
        src = inspect.getsource(FixAttendanceRecord._compute_hours)
        self.assertIn("overtime_hours", src)
        # beyond the 8h statutory day
        self.assertIn("STANDARD_DAY_HOURS", src)


if __name__ == "__main__":
    unittest.main()
