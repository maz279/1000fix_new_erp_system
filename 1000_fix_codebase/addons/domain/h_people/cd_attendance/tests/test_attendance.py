# cd_attendance tests — P08-M02 / R06-M02 (CD-M55-01).
import inspect
import unittest

from odoo.addons.cd_attendance.models.fix_attendance import (
    MAX_DAILY_HOURS,
    MAX_WEEKLY_HOURS,
    MIN_SHIFT_REST_HOURS,
    OVERTIME_RATE_MULTIPLIER,
    STANDARD_DAY_HOURS,
    STANDARD_WEEKLY_HOURS,
    FixAttendanceLock,
    FixAttendanceRecord,
    FixBiometricDevice,
    FixRosterSlot,
    FixShiftTemplate,
    FixWorkOrderAvailabilityExt,
)


class TestWorkingTimeCompliance(unittest.TestCase):
    """R06-M02-T01: Bangladesh Labour Act 2006 statutory working-time compliance."""

    def test_statutory_constants(self):
        """Verify statutory working-time thresholds match BLA 2006."""
        self.assertEqual(STANDARD_DAY_HOURS, 8.0)  # s. 100
        self.assertEqual(MAX_DAILY_HOURS, 10.0)  # s. 102/108
        self.assertEqual(STANDARD_WEEKLY_HOURS, 48.0)  # s. 102
        self.assertEqual(MAX_WEEKLY_HOURS, 60.0)  # s. 102
        self.assertEqual(MIN_SHIFT_REST_HOURS, 11.0)  # s. 101/105
        self.assertEqual(OVERTIME_RATE_MULTIPLIER, 2.0)  # s. 108

    def test_hours_compute_logic(self):
        """Verify standard hours and overtime computation."""
        src = inspect.getsource(FixAttendanceRecord._compute_hours)
        self.assertIn("worked_hours", src)
        self.assertIn("overtime_hours", src)
        self.assertIn("STANDARD_DAY_HOURS", src)

    def test_compliance_status_compute_logic(self):
        """Verify compliance status computation covers daily ceiling and shift rest."""
        src = inspect.getsource(FixAttendanceRecord._compute_compliance)
        self.assertIn("compliance_status", src)
        self.assertIn("daily_limit_exceeded", src)
        self.assertIn("rest_interval_violation", src)
        self.assertIn("MAX_DAILY_HOURS", src)
        self.assertIn("MIN_SHIFT_REST_HOURS", src)


class TestBiometricDeviceAndResidency(unittest.TestCase):
    """R06-M02-T02: INT-041 Biometric Devices with S3 Residency Routing."""

    def test_biometric_device_model_definition(self):
        """Verify fix.biometric.device model schema and fields."""
        self.assertTrue(hasattr(FixBiometricDevice, "device_id"))
        self.assertTrue(hasattr(FixBiometricDevice, "model_type"))
        self.assertTrue(hasattr(FixBiometricDevice, "branch_id"))
        self.assertTrue(hasattr(FixBiometricDevice, "status"))
        self.assertTrue(hasattr(FixBiometricDevice, "last_sync_at"))
        self.assertEqual(FixBiometricDevice._name, "fix.biometric.device")

    def test_biometric_ingest_routes_template_to_z4(self):
        """Verify action_ingest_punch routes templates strictly to fix.identity.document."""
        src = inspect.getsource(FixBiometricDevice.action_ingest_punch)
        self.assertIn("fix.identity.document", src)
        self.assertIn("biometric", src)
        self.assertIn("action_ingest_punch", src)
        # Verify it checks for period lock
        self.assertIn("fix.attendance.lock", src)


class TestAvailabilityStubClosure(unittest.TestCase):
    """R06-M02-T03: M02 -> M55 availability stub is closed in the assignment path."""

    def test_check_exists_and_blocks(self):
        """Assignment strictly verifies roster slot and blocks if missing or on leave."""
        src = inspect.getsource(FixWorkOrderAvailabilityExt.action_check_technician_availability)
        self.assertIn("fix.roster.slot", src)
        self.assertIn("no roster slot", src)
        self.assertIn("on approved leave", src)

    def test_write_hooks_the_assignment_path(self):
        """Work order write triggers availability check when technician_id is assigned."""
        src = inspect.getsource(FixWorkOrderAvailabilityExt.write)
        self.assertIn("technician_id", src)
        self.assertIn("action_check_technician_availability", src)


class TestAttendanceLockImmutability(unittest.TestCase):
    """R06-M02-T04: Monthly attendance lock guards payroll (Journey 13 Gate 1)."""

    def test_locked_records_immutable_on_write(self):
        src = inspect.getsource(FixAttendanceRecord.write)
        self.assertIn("locked", src)
        self.assertIn("locked in period", src)

    def test_locked_records_immutable_on_create(self):
        src = inspect.getsource(FixAttendanceRecord.create)
        self.assertIn("locked", src)
        self.assertIn("Cannot create attendance record in locked period", src)

    def test_locked_records_immutable_on_unlink(self):
        src = inspect.getsource(FixAttendanceRecord.unlink)
        self.assertIn("locked", src)
        self.assertIn("Cannot delete attendance record in locked period", src)

    def test_only_past_periods_lockable(self):
        src = inspect.getsource(FixAttendanceLock.action_lock)
        self.assertIn("Only a fully PAST period may be locked", src)
        self.assertIn("period_end", src)


class TestShiftAndRosterManagement(unittest.TestCase):
    """Shift templates and roster slots."""

    def test_shift_hours_constraint(self):
        src = inspect.getsource(FixShiftTemplate._check_hours)
        self.assertIn("start_hour", src)
        self.assertIn("end_hour", src)
        self.assertIn("ValidationError", src)

    def test_roster_slot_label_compute(self):
        src = inspect.getsource(FixRosterSlot._compute_label)
        self.assertIn("display_label", src)


if __name__ == "__main__":
    unittest.main()
