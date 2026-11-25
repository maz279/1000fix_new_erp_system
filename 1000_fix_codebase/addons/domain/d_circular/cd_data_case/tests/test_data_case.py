from __future__ import annotations

import inspect
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "vendor" / "odoo"))
import odoo
import odoo.addons

circular_path = str(ROOT / "addons" / "domain" / "d_circular")
if circular_path not in odoo.addons.__path__:
    odoo.addons.__path__.append(circular_path)

from odoo.addons.cd_data_case.models.fix_data_case import (
    FixDataRecoveryCase,
    FixDataWipeCertificate,
    FixZ4AccessAudit,
)


class TestResidencyEnforcement(unittest.TestCase):
    def test_recovery_blocked_until_z4(self):
        src = inspect.getsource(FixDataRecoveryCase.action_start_recovery)
        self.assertIn("z4", src)
        self.assertIn("SC-007", src)

    # A02 audit M06-6: the chain is an append-only ledger written by _custody_log
    def test_custody_chain_logged(self):
        src = inspect.getsource(FixDataRecoveryCase.action_take_custody)
        self.assertIn("_custody_log", src)

    def test_custody_transfer_logged(self):
        src = inspect.getsource(FixDataRecoveryCase.action_log_custody_transfer)
        self.assertIn("_custody_log", src)
        self.assertIn("custody_transferred", src)

    def test_step_up_auth_enforced(self):
        src = inspect.getsource(FixDataRecoveryCase.action_access_recovered_data)
        self.assertIn("step_up_token", src)
        self.assertIn("SC-002", src)
        self.assertIn("Access Denied", src)

    def test_per_read_access_logged(self):
        src = inspect.getsource(FixDataRecoveryCase.action_access_recovered_data)
        self.assertIn("fix.z4.access.audit", src)
        self.assertIn("step_up_verified", src)

    def test_z4_audit_immutability(self):
        write_src = inspect.getsource(FixZ4AccessAudit.write)
        unlink_src = inspect.getsource(FixZ4AccessAudit.unlink)
        self.assertIn("immutable", write_src)
        self.assertIn("immutable", unlink_src)

    def test_purge_certificate_issued(self):
        src = inspect.getsource(FixDataRecoveryCase.action_purge)
        self.assertIn("wipe.certificate", src)
        self.assertIn("statutory_record_retained", src)

    def test_wipe_has_verification_hash(self):
        # the hash is derived from the wipe EVIDENCE (log content), not a clock
        src = inspect.getsource(FixDataWipeCertificate._evidence_digest)
        self.assertIn("hashlib", src)
        self.assertIn("wipe_log_attachment_id", src)
        self.assertNotIn("time.time", inspect.getsource(FixDataWipeCertificate))

    def test_wipe_certificate_permanent(self):
        unlink_src = inspect.getsource(FixDataWipeCertificate.unlink)
        self.assertIn("NFR-095", unlink_src)
        self.assertIn("statutory_record_retained", unlink_src)

    def test_nist_methods(self):
        from odoo.addons.cd_data_case.models.fix_data_case import WIPE_METHODS

        methods = dict(WIPE_METHODS)
        self.assertIn("nist_800_88", methods)
        self.assertIn("nist_800_88_purge", methods)
        # the method is the operator's input: no default
        self.assertNotIn(
            "default=",
            inspect.getsource(FixDataWipeCertificate).split("method = ")[1].split(")")[0],
        )


if __name__ == "__main__":
    unittest.main()
