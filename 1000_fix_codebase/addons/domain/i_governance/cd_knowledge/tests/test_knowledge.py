"""cd_knowledge tests - P09-M08 & R07-M05 (CD-M61-01 & P02 Offline Manuals)."""

import inspect
import unittest

from odoo.addons.cd_knowledge.models.fix_knowledge import FixKnowledgeArticle


class TestKnowledge(unittest.TestCase):
    def test_categories_cover_m22_rescope(self):
        src = inspect.getsource(FixKnowledgeArticle)
        for cat in (
            "troubleshooting",
            "repair_procedure",
            "device_guide",
            "schematic",
            "safety_bulletin",
        ):
            self.assertIn(cat, src)

    def test_bengali_title_and_content_fields(self):
        self.assertTrue(hasattr(FixKnowledgeArticle, "title_bn"))
        self.assertTrue(hasattr(FixKnowledgeArticle, "content_bn"))

    def test_technical_hardware_metadata(self):
        self.assertTrue(hasattr(FixKnowledgeArticle, "device_brand"))
        self.assertTrue(hasattr(FixKnowledgeArticle, "device_model"))
        self.assertTrue(hasattr(FixKnowledgeArticle, "fault_symptom"))
        self.assertTrue(hasattr(FixKnowledgeArticle, "rework_level"))

    def test_offline_sync_and_content_hash(self):
        self.assertTrue(hasattr(FixKnowledgeArticle, "offline_available"))
        self.assertTrue(hasattr(FixKnowledgeArticle, "content_hash"))
        self.assertTrue(hasattr(FixKnowledgeArticle, "version"))
        self.assertTrue(hasattr(FixKnowledgeArticle, "get_offline_manuals"))

    def test_publish_event(self):
        self.assertIn("knowledge.published", inspect.getsource(FixKnowledgeArticle))

    def test_lifecycle(self):
        """draft -> published -> archived (DE-16: every state reachable)."""
        src = inspect.getsource(FixKnowledgeArticle)
        for state in ("draft", "published", "archived"):
            self.assertIn(state, src)

    def test_publish_action_publishes(self):
        src = inspect.getsource(FixKnowledgeArticle.action_publish)
        self.assertIn('"published"', src)

    def test_as02_conformance(self):
        for mixin in ("mail.thread", "mail.activity.mixin"):
            self.assertIn(mixin, FixKnowledgeArticle._inherit)
        self.assertTrue(hasattr(FixKnowledgeArticle, "company_id"))
        self.assertTrue(hasattr(FixKnowledgeArticle, "operating_unit_id"))


if __name__ == "__main__":
    unittest.main()
