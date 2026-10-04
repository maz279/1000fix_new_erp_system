"""cd_hse tests - P09-M08 (CD-M59-01)."""
import inspect
import unittest

from odoo.addons.cd_hse.models.fix_hse import (
    FixHseIncident, FixSafetyInspection)


class TestHse(unittest.TestCase):
    def test_incident_types(self):
        src = inspect.getsource(FixHseIncident)
        for it in ("injury", "near_miss", "fire", "environmental"):
            self.assertIn(it, src)

    def test_safety_inspection_checks(self):
        src = inspect.getsource(FixSafetyInspection)
        for check in ("fire_extinguisher_ok", "emergency_exit_ok",
                      "first_aid_ok", "electrical_ok"):
            self.assertIn(check, src)

    def test_incident_event(self):
        self.assertIn("hse.incident_reported",
                      inspect.getsource(FixHseIncident))


if __name__ == "__main__":
    unittest.main()
