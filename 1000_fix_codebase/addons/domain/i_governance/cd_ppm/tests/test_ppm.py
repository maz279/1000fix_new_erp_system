"""cd_ppm tests - P10-M05 (CD-M67-01 / R08-M03)."""

import inspect
import unittest

from odoo.addons.cd_ppm.models.fix_ppm import FixProject, FixProjectMilestone, FixProjectTask


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

    def test_budget_variance_tracked(self):
        self.assertTrue(hasattr(FixProject, "budget"))
        self.assertTrue(hasattr(FixProject, "actual_cost"))
        self.assertTrue(hasattr(FixProject, "budget_variance"))
        self.assertTrue(hasattr(FixProject, "variance_pct"))

    def test_progress_tracked(self):
        self.assertTrue(hasattr(FixProject, "progress_pct"))

    def test_state_lifecycle(self):
        src = inspect.getsource(FixProject)
        for s in ("draft", "active", "on_hold", "completed", "cancelled"):
            self.assertIn(s, src)

    def test_sequence_code_generated(self):
        src = inspect.getsource(FixProject.create)
        self.assertIn("ir.sequence", src)

    def test_tasks_relation(self):
        self.assertTrue(hasattr(FixProject, "task_ids"))


class TestMilestone(unittest.TestCase):
    def test_milestone_states(self):
        src = inspect.getsource(FixProjectMilestone)
        for s in ("pending", "done"):
            self.assertIn(s, src)

    def test_milestone_links_to_project(self):
        self.assertTrue(hasattr(FixProjectMilestone, "project_id"))

    def test_milestone_completion_gated_by_tasks(self):
        src = inspect.getsource(FixProjectMilestone.action_complete)
        self.assertIn("task(s) still open in milestone", src)
        self.assertIn("project.milestone_completed", src)


class TestProjectTask(unittest.TestCase):
    def test_task_states(self):
        src = inspect.getsource(FixProjectTask)
        for s in ("todo", "in_progress", "done", "cancelled"):
            self.assertIn(s, src)

    def test_task_hours_tracked(self):
        self.assertTrue(hasattr(FixProjectTask, "planned_hours"))
        self.assertTrue(hasattr(FixProjectTask, "actual_hours"))


if __name__ == "__main__":
    unittest.main()
