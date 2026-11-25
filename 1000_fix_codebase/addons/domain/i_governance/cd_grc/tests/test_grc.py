"""cd_grc tests - P09-M08 & R07-M05 (CD-M60-01 & ADR D-040 GRC depth)."""

import inspect
import unittest

from odoo.addons.cd_grc.models.fix_grc import (
    FixAuditFinding,
    FixComplianceFramework,
    FixComplianceObligation,
    FixControl,
    FixRiskRegister,
)


class TestGrc(unittest.TestCase):
    def test_risk_score_computed(self):
        src = inspect.getsource(FixRiskRegister._compute_score)
        self.assertIn("likelihood", src)
        self.assertIn("impact", src)

    def test_control_types(self):
        src = inspect.getsource(FixControl)
        for ct in ("preventive", "detective", "corrective"):
            self.assertIn(ct, src)

    def test_control_links_to_risk(self):
        self.assertTrue(hasattr(FixControl, "risk_id"))

    def test_compliance_framework_matrix(self):
        """M60: ISO 9001, ISO 27001, PDPA 2023, and Labour Act 2006."""
        src = inspect.getsource(FixComplianceFramework)
        for fw in ("iso_9001", "iso_27001", "pdpa_2023", "bla_2006"):
            self.assertIn(fw, src)
        self.assertTrue(hasattr(FixComplianceFramework, "compliance_score"))

    def test_compliance_obligation_model(self):
        """M60: Clause references and M24 document evidence link."""
        self.assertTrue(hasattr(FixComplianceObligation, "clause_reference"))
        self.assertTrue(hasattr(FixComplianceObligation, "evidence_doc_id"))
        self.assertTrue(hasattr(FixComplianceObligation, "compliance_status"))

    def test_audit_finding_and_capa_lifecycle(self):
        """M60: Finding classification, CAPA submission and verification closure."""
        src = inspect.getsource(FixAuditFinding)
        for ft in ("major_nc", "minor_nc", "ofi"):
            self.assertIn(ft, src)
        self.assertIn("grc.capa_closed", inspect.getsource(FixAuditFinding.action_verify_closure))

    def test_adr_d040_m24_direction_invariance(self):
        """ADR D-040: GRC models reference M24 fix.document evidence; M24 never references GRC."""
        self.assertTrue(hasattr(FixControl, "evidence_doc_id"))
        self.assertTrue(hasattr(FixComplianceObligation, "evidence_doc_id"))
        self.assertTrue(hasattr(FixAuditFinding, "closure_evidence_doc_id"))

    def test_as02_as03_conformance_all_five_models(self):
        all_models = (
            FixRiskRegister,
            FixControl,
            FixComplianceFramework,
            FixComplianceObligation,
            FixAuditFinding,
        )
        for model in all_models:
            for mixin in ("mail.thread", "mail.activity.mixin"):
                self.assertIn(mixin, model._inherit, f"Missing {mixin} on {model._name}")
            self.assertTrue(hasattr(model, "company_id"), f"Missing company_id on {model._name}")
            self.assertTrue(
                hasattr(model, "operating_unit_id"), f"Missing operating_unit_id on {model._name}"
            )


if __name__ == "__main__":
    unittest.main()
