"""cd_knowledge tests - P09-M08 (CD-M61-01)."""
import inspect
import unittest

from odoo.addons.cd_knowledge.models.fix_knowledge import FixKnowledgeArticle


class TestKnowledge(unittest.TestCase):
    def test_categories_cover_m22_rescope(self):
        src = inspect.getsource(FixKnowledgeArticle)
        for cat in ("troubleshooting", "repair_procedure", "device_guide"):
            self.assertIn(cat, src)

    def test_bengali_title_field(self):
        self.assertTrue(hasattr(FixKnowledgeArticle, "title_bn"))

    def test_publish_event(self):
        self.assertIn("knowledge.published",
                      inspect.getsource(FixKnowledgeArticle))


if __name__ == "__main__":
    unittest.main()
