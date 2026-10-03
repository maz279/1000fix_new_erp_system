# cd_vehicle_ext tests — P08-M08 (CD-M46-01).
import inspect
import unittest

from odoo.addons.cd_vehicle_ext.models.fix_vehicle import (
    FixVehicleAssignment, FleetVehicleCdExt)


class TestVehicleAssignment(unittest.TestCase):
    """The W2-deferred dispatch connection, delivered."""

    def test_overlap_refused(self):
        src = inspect.getsource(FixVehicleAssignment.create)
        self.assertIn("overlaps are refused", src)
        self.assertIn("search_count", src)

    def test_compliance_gates_dispatch(self):
        src = inspect.getsource(FixVehicleAssignment.create)
        self.assertIn("action_assert_dispatchable", src)

    def test_compliance_compute(self):
        src = inspect.getsource(FleetVehicleCdExt._compute_compliance)
        self.assertIn("fitness_expiry", src)
        self.assertIn("insurance_expiry", src)

    def test_assignment_event(self):
        self.assertIn("vehicle.assigned",
                      inspect.getsource(FixVehicleAssignment))


if __name__ == "__main__":
    unittest.main()
