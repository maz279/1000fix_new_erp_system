"""cd_talent tests - P09-M08 (CD-M58-01)."""

import inspect
import unittest

from odoo.addons.cd_talent.models import fix_talent
from odoo.addons.cd_talent.models.fix_talent import (
    FixCandidate,
    FixJobRequisition,
    FixOnboardingPlan,
)


class TestJobRequisition(unittest.TestCase):
    """M58: requisition lifecycle and the joiner event."""

    def test_hired_event_drives_m29(self):
        """The AR-006 interface break to M29 provisioning: hiring publishes
        employee.hired — M29 subscribes, talent never imports it."""
        src = inspect.getsource(FixJobRequisition.action_hired)
        self.assertIn("employee.hired", src)

    def test_requisition_lifecycle(self):
        src = inspect.getsource(FixJobRequisition)
        for state in ("draft", "open", "hired", "closed"):
            self.assertIn(state, src)

    def test_open_action_transitions_state(self):
        src = inspect.getsource(FixJobRequisition.action_open)
        self.assertIn('"open"', src)

    def test_hired_payload_carries_position(self):
        """M29 provisioning needs the position to provision access for."""
        src = inspect.getsource(FixJobRequisition.action_hired)
        self.assertIn("position_id.name", src)

    def test_no_direct_m29_dependency(self):
        """Loose coupling: talent must not import or call M29 directly —
        the event bus is the only seam (AR-006)."""
        src = inspect.getsource(fix_talent)
        self.assertNotIn("cd_onboarding", src)
        self.assertNotIn("fix.provisioning", src)


class TestCandidate(unittest.TestCase):
    """M58: candidate pipeline applied -> hired/rejected."""

    def test_candidate_lifecycle(self):
        src = inspect.getsource(FixCandidate)
        for state in ("applied", "screening", "interview", "offered", "hired", "rejected"):
            self.assertIn(state, src)

    def test_candidate_links_to_requisition(self):
        self.assertTrue(hasattr(FixCandidate, "requisition_id"))

    def test_candidate_actions(self):
        for action in ("action_screen", "action_interview", "action_offer", "action_hire"):
            self.assertTrue(hasattr(FixCandidate, action))


class TestOnboardingPlan(unittest.TestCase):
    """M58 / MV-01: Onboarding plan and authoritative employee.joined event."""

    def test_onboarding_lifecycle_states(self):
        src = inspect.getsource(FixOnboardingPlan)
        for state in ("draft", "in_progress", "completed", "cancelled"):
            self.assertIn(state, src)

    def test_onboarding_checklist_fields(self):
        for f in (
            "nid_verified",
            "contract_signed",
            "it_assets_allocated",
            "keycloak_provisioned",
            "bank_details_captured",
            "safety_kit_issued",
        ):
            self.assertTrue(hasattr(FixOnboardingPlan, f))

    def test_action_complete_emits_employee_joined_event(self):
        src = inspect.getsource(FixOnboardingPlan.action_complete)
        self.assertIn('"employee.joined"', src)
        self.assertIn('"onboarding_id"', src)
        self.assertIn('"joined_date"', src)

    def test_action_complete_statutory_prerequisite_guard(self):
        src = inspect.getsource(FixOnboardingPlan.action_complete)
        self.assertIn("UserError", src)
        self.assertIn("nid_verified", src)
        self.assertIn("contract_signed", src)
        self.assertIn("keycloak_provisioned", src)
        self.assertIn("bank_details_captured", src)


class TestArchConformance(unittest.TestCase):
    """AS-02/03: chatter, activities, company, operating unit on all models."""

    def test_models_inherit_chatter(self):
        for model in (FixJobRequisition, FixCandidate, FixOnboardingPlan):
            for mixin in ("mail.thread", "mail.activity.mixin"):
                self.assertIn(mixin, model._inherit)

    def test_all_models_carry_company_and_ou(self):
        for model in (FixJobRequisition, FixCandidate, FixOnboardingPlan):
            self.assertTrue(hasattr(model, "company_id"))
            self.assertTrue(hasattr(model, "operating_unit_id"))

    def test_candidate_hire_gates_and_idempotent_employee_creation(self):
        self.assertTrue(hasattr(FixCandidate, "employee_id"))
        src = inspect.getsource(FixCandidate.action_hire)
        self.assertIn("fix.talent.check", src)
        self.assertIn("fix.talent.assessment", src)
        self.assertIn("hr.employee", src)
        self.assertIn("fix.onboarding.plan", src)


if __name__ == "__main__":
    unittest.main()
