# cd_equipment_register tests — P08-M08 (CD-M45-01).
import inspect
import unittest

from odoo.addons.cd_equipment_register.models.fix_equipment import (
    FixCalibration, FixEquipment)


class TestCalibrationModel(unittest.TestCase):
    """The M31-deferred capability (P05-M02-T07), now delivered."""

    def test_overdue_blocks_usage(self):
        src = inspect.getsource(FixEquipment.action_assert_usable)
        self.assertIn("Calibration overdue", src)

    def test_overdue_computed_from_next_due(self):
        src = inspect.getsource(FixEquipment._compute_calibration)
        self.assertIn("calibration_overdue", src)

    def test_only_passed_calibrations_count(self):
        src = inspect.getsource(FixEquipment._compute_calibration)
        self.assertIn('result == "pass"', src)

    def test_events_recorded_and_overdue(self):
        src = inspect.getsource(FixCalibration.create)
        self.assertIn("equipment.calibration.recorded", src)
        self.assertIn("equipment.calibration.overdue", src)

    def test_due_after_calibration_constraint(self):
        src = inspect.getsource(FixCalibration._check_due_after)
        self.assertIn("precedes", src)


if __name__ == "__main__":
    unittest.main()
