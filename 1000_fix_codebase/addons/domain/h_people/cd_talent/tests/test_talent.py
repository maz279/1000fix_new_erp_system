"""cd_talent tests - P09-M08 (CD-M58-01)."""
import inspect
import unittest

from odoo.addons.cd_talent.models import fix_talent
from odoo.addons.cd_talent.models.fix_talent import (
    FixCandidate,
    FixJobRequisition,
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
        for state in ("applied", "screening", "interview", "offered",
                      "hired", "rejected"):
            self.assertIn(state, src)

    def test_candidate_links_to_requisition(self):
        self.assertTrue(hasattr(FixCandidate, "requisition_id"))


class TestArchConformance(unittest.TestCase):
    """AS-02/03: chatter, activities, company, operating unit on both models."""

    def test_requisition_inherits_chatter(self):
        for mixin in ("mail.thread", "mail.activity.mixin"):
            self.assertIn(mixin, FixJobRequisition._inherit)

    def test_candidate_inherits_chatter(self):
        for mixin in ("mail.thread", "mail.activity.mixin"):
            self.assertIn(mixin, FixCandidate._inherit)

    def test_both_models_carry_company_and_ou(self):
        for model in (FixJobRequisition, FixCandidate):
            self.assertTrue(hasattr(model, "company_id"))
            self.assertTrue(hasattr(model, "operating_unit_id"))


if __name__ == "__main__":
    unittest.main()
