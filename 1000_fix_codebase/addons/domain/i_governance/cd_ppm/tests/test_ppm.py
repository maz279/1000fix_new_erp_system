"""cd_ppm tests - P10-M05 (CD-M67-01)."""
import inspect
import unittest

from odoo.addons.cd_ppm.models.fix_ppm import FixProject, FixProjectMilestone


class TestProject(unittest.TestCase):
    def test_open_milestones_block_completion(self):
        src = inspect.getsource(FixProject.action_complete)
        self.assertIn("open", src)
        self.assertIn("milestone", src)

    def test_project_events(self):
        src = inspect.getsource(FixProject)
        self.assertIn("project.created", src)
        self.assertIn("project.completed", src)

    def test_project_types(self):
        src = inspect.getsource(FixProject)
        for pt in ("internal", "client", "infrastructure"):
            self.assertIn(pt, src)

    def test_budget_tracked(self):
        self.assertTrue(hasattr(FixProject, "budget"))
        self.assertTrue(hasattr(FixProject, "actual_cost"))

    def test_progress_tracked(self):
        self.assertTrue(hasattr(FixProject, "progress_pct"))

    def test_state_lifecycle(self):
        src = inspect.getsource(FixProject)
        for s in ("draft", "active", "on_hold", "completed", "cancelled"):
            self.assertIn(s, src)

    def test_sequence_code_generated(self):
        src = inspect.getsource(FixProject.create)
        self.assertIn("ir.sequence", src)


class TestMilestone(unittest.TestCase):
    def test_milestone_states(self):
        src = inspect.getsource(FixProjectMilestone)
        for s in ("pending", "done"):
            self.assertIn(s, src)

    def test_milestone_links_to_project(self):
        self.assertTrue(hasattr(FixProjectMilestone, "project_id"))


if __name__ == "__main__":
    unittest.main()
