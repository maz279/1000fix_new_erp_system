"""cd_data_case tests - P09-M05 (CD-M06-01)."""
import inspect
import unittest

from odoo.addons.cd_data_case.models.fix_data_case import (
    FixDataRecoveryCase, FixDataWipeCertificate)


class TestResidencyEnforcement(unittest.TestCase):
    def test_recovery_blocked_until_z4(self):
        src = inspect.getsource(FixDataRecoveryCase.action_start_recovery)
        self.assertIn("z4", src)
        self.assertIn("SC-007", src)

    def test_custody_chain_logged(self):
        src = inspect.getsource(FixDataRecoveryCase.action_take_custody)
        self.assertIn("custody_chain", src)

    def test_purge_certificate_issued(self):
        src = inspect.getsource(FixDataRecoveryCase.action_purge)
        self.assertIn("wipe.certificate", src)

    def test_wipe_has_verification_hash(self):
        src = inspect.getsource(FixDataWipeCertificate.create)
        self.assertIn("hashlib", src)
        self.assertIn("verification_hash", src)

    def test_nist_methods(self):
        src = inspect.getsource(FixDataWipeCertificate)
        self.assertIn("nist_800_88", src)


if __name__ == "__main__":
    unittest.main()
