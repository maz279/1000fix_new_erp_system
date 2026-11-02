"""cd_hse tests - P09-M08 & R07-M05 (CD-M59-01 statutory HSE depth)."""

import inspect
import unittest

from odoo.addons.cd_hse.models.fix_hse import (
    FixHazardousSubstanceRegister,
    FixHseIncident,
    FixPpeRegister,
    FixSafetyCommittee,
    FixSafetyInspection,
    FixStatutoryAccidentRegister,
)


class TestHse(unittest.TestCase):
    def test_incident_types(self):
        src = inspect.getsource(FixHseIncident)
        for it in ("injury", "near_miss", "fire", "environmental", "battery_thermal"):
            self.assertIn(it, src)

    def test_safety_inspection_checks(self):
        src = inspect.getsource(FixSafetyInspection)
        for check in (
            "fire_extinguisher_ok",
            "esd_grounding_ok",
            "first_aid_ok",
            "electrical_ok",
            "fume_extraction_ok",
        ):
            self.assertIn(check, src)

    def test_incident_event(self):
        self.assertIn("hse.incident_reported", inspect.getsource(FixHseIncident))

    def test_incident_severity_ladder(self):
        """low/medium/high — drives DIFE escalation."""
        src = inspect.getsource(FixHseIncident)
        for sev in ("low", "medium", "high"):
            self.assertIn('"%s"' % sev, src)

    def test_inspection_lifecycle(self):
        src = inspect.getsource(FixSafetyInspection)
        for state in ("scheduled", "done", "follow_up"):
            self.assertIn(state, src)

    def test_safety_committee_bla_conformance(self):
        """M59: Bangladesh Labour Act 2006 §90A and Labour Rules 2015 Rule 81."""
        src = inspect.getsource(FixSafetyCommittee)
        self.assertIn("§90A", src)
        self.assertIn("dife_registered", src)
        self.assertIn("hse.safety_committee_meeting", src)

    def test_statutory_accident_register(self):
        """M59: Form 33/34 statutory register with 48h DIFE notification."""
        src = inspect.getsource(FixStatutoryAccidentRegister)
        self.assertIn("Form 33/34", src)
        self.assertIn("dife_notified", src)
        self.assertIn("statutory_compensation_bdt", src)
        self.assertIn("hse.dife_accident_reported", src)

    def test_ppe_equipment_register(self):
        """M59: ANSI/ESD S20.20 and workshop protective equipment."""
        src = inspect.getsource(FixPpeRegister)
        self.assertIn("esd_wristband", src)
        self.assertIn("thermal_gloves", src)
        self.assertIn("fume_mask", src)
        self.assertIn("check_replenishment", src)

    def test_hazardous_substance_register(self):
        """M59: Chemical solvent & Lithium-ion battery containment register."""
        src = inspect.getsource(FixHazardousSubstanceRegister)
        self.assertIn("un_number", src)
        self.assertIn("msds_on_file", src)
        self.assertIn("fire_suppression_type", src)

    def test_as02_conformance_all_six_models(self):
        all_models = (
            FixHseIncident,
            FixSafetyInspection,
            FixSafetyCommittee,
            FixStatutoryAccidentRegister,
            FixPpeRegister,
            FixHazardousSubstanceRegister,
        )
        for model in all_models:
            for mixin in ("mail.thread", "mail.activity.mixin"):
                self.assertIn(mixin, model._inherit, f"Missing {mixin} on {model._name}")
            self.assertTrue(hasattr(model, "company_id"), f"Missing company_id on {model._name}")
            self.assertTrue(
                hasattr(model, "operating_unit_id"), f"Missing operating_unit_id on {model._name}"
            )

    def test_bla_s80_two_working_day_clock_and_s90_append_only_register(self):
        from odoo.addons.cd_hse.models.fix_hse_ops import FixHseLoneWorker

        for f in ("accident_datetime", "notice_due", "notice_form", "dife_notice_ref"):
            self.assertTrue(hasattr(FixHseIncident, f))
        src_close = inspect.getsource(FixHseIncident.action_close)
        self.assertIn("dife_notice_ref", src_close)
        src_write = inspect.getsource(FixStatutoryAccidentRegister.write)
        self.assertIn("append-only", src_write)
        src_lw = inspect.getsource(FixHseLoneWorker.action_escalate)
        self.assertIn("hse.loneworker.escalated", src_lw)


if __name__ == "__main__":
    unittest.main()
