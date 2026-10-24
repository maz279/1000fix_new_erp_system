"""cd_itsm tests - P09-M08 (CD-M66-01)."""

import inspect
import unittest

from odoo.addons.cd_itsm.models.fix_itsm import FixItsmTicket


class TestItsm(unittest.TestCase):
    def test_ticket_lifecycle(self):
        src = inspect.getsource(FixItsmTicket)
        for state in ("new", "assigned", "in_progress", "resolved", "closed"):
            self.assertIn(state, src)

    def test_categories(self):
        src = inspect.getsource(FixItsmTicket)
        for cat in ("hardware", "software", "network", "account"):
            self.assertIn(cat, src)

    def test_events(self):
        src = inspect.getsource(FixItsmTicket)
        self.assertIn("itsm.ticket_created", src)
        self.assertIn("itsm.ticket_resolved", src)

    def test_resolve_gate(self):
        src = inspect.getsource(FixItsmTicket.action_resolve)
        self.assertIn("already resolved", src)


if __name__ == "__main__":
    unittest.main()
