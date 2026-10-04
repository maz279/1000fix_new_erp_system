"""cd_talent tests - P09-M08 (CD-M58-01)."""
import inspect
import unittest

from odoo.addons.cd_talent.models.fix_talent import FixJobRequisition


class TestTalent(unittest.TestCase):
    def test_hired_event_drives_m29(self):
        src = inspect.getsource(FixJobRequisition.action_hired)
        self.assertIn("employee.hired", src)

    def test_requisition_lifecycle(self):
        src = inspect.getsource(FixJobRequisition)
        for state in ("draft", "open", "hired", "closed"):
            self.assertIn(state, src)


if __name__ == "__main__":
    unittest.main()
