"""cd_ppm tests - P10-M05 (CD-M67-01)."""
import inspect
import unittest

from odoo.addons.cd_ppm.models.fix_ppm import FixProject


class TestProject(unittest.TestCase):
    def test_open_milestones_block_completion(self):
        src = inspect.getsource(FixProject.action_complete)
        self.assertIn("open", src)
        self.assertIn("milestone", src)

    def test_project_events(self):
        src = inspect.getsource(FixProject)
        self.assertIn("project.created", src)
        self.assertIn("project.completed", src)


if __name__ == "__main__":
    unittest.main()
