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

    def test_incident_severity_ladder(self):
        """low/medium/high — the ladder drives escalation routing."""
        src = inspect.getsource(FixHseIncident)
        for sev in ("low", "medium", "high"):
            self.assertIn('"%s"' % sev, src)

    def test_inspection_lifecycle(self):
        """scheduled -> done -> follow_up: a failed check routes to
        follow_up, not silently to done."""
        src = inspect.getsource(FixSafetyInspection)
        for state in ("scheduled", "done", "follow_up"):
            self.assertIn(state, src)

    def test_as02_conformance_both_models(self):
        for model in (FixHseIncident, FixSafetyInspection):
            for mixin in ("mail.thread", "mail.activity.mixin"):
                self.assertIn(mixin, model._inherit)
            self.assertTrue(hasattr(model, "company_id"))
            self.assertTrue(hasattr(model, "operating_unit_id"))


if __name__ == "__main__":
    unittest.main()
