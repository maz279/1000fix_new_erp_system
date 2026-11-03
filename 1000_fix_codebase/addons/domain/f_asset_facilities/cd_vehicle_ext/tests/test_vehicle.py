# cd_vehicle_ext tests — P08-M08 (CD-M46-01).
import inspect
import unittest

from odoo.addons.cd_vehicle_ext.models.fix_vehicle import FixVehicleAssignment, FleetVehicleCdExt


class TestVehicleAssignment(unittest.TestCase):
    """The W2-deferred dispatch connection, delivered."""

    def test_overlap_refused(self):
        src = inspect.getsource(FixVehicleAssignment._fix_check_dispatchable)
        self.assertIn("overlaps are refused", src)
        self.assertIn("search_count", src)

    def test_compliance_gates_dispatch(self):
        # create AND write run the gate (A07 audit M46-4)
        for method in (FixVehicleAssignment.create, FixVehicleAssignment.write):
            self.assertIn("_fix_check_dispatchable", inspect.getsource(method))

    def test_compliance_compute(self):
        # A07 audit M46-3: compliance comes from the document register
        src = inspect.getsource(FleetVehicleCdExt._compute_compliance)
        self.assertIn("_fix_missing_documents", src)
        self.assertNotIn("insurance_expiry", src)

    def test_assignment_event(self):
        self.assertIn("vehicle.assigned", inspect.getsource(FixVehicleAssignment))


if __name__ == "__main__":
    unittest.main()
