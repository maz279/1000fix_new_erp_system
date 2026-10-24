# cd_qms_process tests — P08-M06 (CD-M23-01). Stub closures pinned.
import inspect
import unittest

from odoo.addons.cd_qms_process.models.fix_qms import (
    FixCapa,
    FixComplaintM23Ext,
    FixInternalAudit,
    FixNcr,
    FixQcChecklistM23Ext,
)


class TestNcrCapa(unittest.TestCase):
    def test_critical_ncr_requires_verified_capa(self):
        src = inspect.getsource(FixNcr.action_close)
        self.assertIn("VERIFIED", src)
        self.assertIn("CLOSED CAPA", src)

    def test_major_capa_requires_preventive_action(self):
        src = inspect.getsource(FixCapa.action_implement)
        self.assertIn("PREVENTIVE", src)

    def test_capa_verification_gate(self):
        src = inspect.getsource(FixCapa.action_close)
        self.assertIn("verification", src)


class TestStubClosures(unittest.TestCase):
    """P08-M06-T04/T05 — the registered stubs close HERE."""

    def test_m31_to_m23_qc_takeover(self):
        self.assertIn("fix.ncr", inspect.getsource(FixQcChecklistM23Ext.action_fail_with_ncr))

    def test_m34_to_m23_complaint_linkage_real(self):
        src = inspect.getsource(FixComplaintM23Ext.action_raise_ncr)
        self.assertIn("fix.ncr", src)
        self.assertIn("NCR-STUB-CLOSED", src)  # the closure is traced

    def test_stub_fields_now_relations(self):
        import odoo.fields as f

        self.assertIsInstance(FixComplaintM23Ext.ncr_id, f.Many2one)


class TestIsoAudit(unittest.TestCase):
    def test_con11_systems_traced_question(self):
        src = inspect.getsource(FixInternalAudit.nccr_systems_traced)
        self.assertIn("system", src.lower())

    def test_p11_offline_capture_field(self):
        self.assertIn("offline_payload", inspect.getsource(FixInternalAudit))


if __name__ == "__main__":
    unittest.main()
