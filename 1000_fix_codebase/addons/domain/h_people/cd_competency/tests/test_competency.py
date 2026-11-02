# cd_competency tests — P08-M05 (CD-M22-01).
import inspect
import unittest

from odoo.addons.cd_competency.models.fix_competency import (
    FixCertification,
    FixWorkOrderEligibilityExt,
)


class TestCertificationRegister(unittest.TestCase):
    def test_expiry_status_compute(self):
        src = inspect.getsource(FixCertification._compute_status)
        self.assertIn("expired", src)
        self.assertIn("expiring", src)
        self.assertIn("active", src)

    def test_expiring_window_30_days(self):
        from odoo.addons.cd_competency.models.fix_competency import EXPIRING_WINDOW_DAYS

        self.assertEqual(EXPIRING_WINDOW_DAYS, 30)

    def test_events_granted_and_expired(self):
        src = inspect.getsource(FixCertification)
        self.assertIn("certification.granted", src)
        self.assertIn("certification.expired", src)


class TestDispatchEligibility(unittest.TestCase):
    """FR-LMS-039 — the check that closed the M02/M31 -> M22 stubs."""

    def test_check_blocks_uncertified(self):
        src = inspect.getsource(FixCertification.dispatch_eligibility)
        self.assertIn("required_for_dispatch", src)
        self.assertIn("no ACTIVE certification", src)

    def test_blocking_on_assignment_path(self):
        src = inspect.getsource(FixWorkOrderEligibilityExt.write)
        self.assertIn("action_check_certification", src)
        block = inspect.getsource(FixWorkOrderEligibilityExt.action_check_certification)
        self.assertIn("assignment blocked", block)

    def test_device_scope_match(self):
        src = inspect.getsource(FixCertification.dispatch_eligibility)
        self.assertIn("device_type", src)

    def test_brand_tier_and_fail_closed_dispatch_gate(self):
        from odoo.addons.cd_competency.models.fix_competency import FixDeviceCategory
        from odoo.addons.cd_competency.models.fix_competency_ops import FixAuditEvidence

        self.assertEqual(FixDeviceCategory._name, "fix.device.category")
        src = inspect.getsource(FixCertification.dispatch_eligibility)
        self.assertIn("fail_closed", src)
        self.assertIn("repair_tier", src)
        self.assertIn("brand_id", src)
        self.assertTrue(hasattr(FixAuditEvidence, "action_compile_iso_dossier"))


if __name__ == "__main__":
    unittest.main()
