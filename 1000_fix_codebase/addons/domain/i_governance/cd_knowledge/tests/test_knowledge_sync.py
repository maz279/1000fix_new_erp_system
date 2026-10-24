"""test_knowledge_sync - R07-M05-T03: P02 Technician offline manual sync & delta hashing."""

import hashlib
import unittest
from unittest.mock import MagicMock

from odoo.addons.cd_knowledge.models.fix_knowledge import FixKnowledgeArticle


class TestKnowledgeOfflineSync(unittest.TestCase):
    def test_sha256_hash_computation(self):
        """Content SHA-256 hash must be deterministic for mobile client delta caching."""
        name = "HP ProBook 450 G8 No Power Diagnostic"
        category = "troubleshooting"
        content_en = "<p>Step 1: Inspect 19V DC-in rail</p>"
        content_bn = "<p>ধাপ ১: ১৯ ভোল্ট ডিসি-ইন পরীক্ষা করুন</p>"

        expected_hash = hashlib.sha256(
            f"{name}|{category}|{content_en}|{content_bn}".encode()
        ).hexdigest()

        rec = MagicMock()
        rec.name = name
        rec.category = category
        rec.content = content_en
        rec.content_bn = content_bn

        # Run compute logic
        FixKnowledgeArticle._compute_content_hash([rec])
        self.assertEqual(rec.content_hash, expected_hash)

    def test_offline_sync_payload_schema(self):
        """get_offline_manuals must return all fields required by P02 technician app."""
        mock_article = MagicMock()
        mock_article.id = 42
        mock_article.article_code = "KB-HW-0042"
        mock_article.name = "Dell Latitude 5420 Charging Fault"
        mock_article.title_bn = "ডেল ল্যাটিটিউড ৫৪২০ চার্জিং ত্রুটি"
        mock_article.category = "repair_procedure"
        mock_article.device_brand = "Dell"
        mock_article.device_model = "Latitude 5420"
        mock_article.fault_symptom = "Battery Not Charging"
        mock_article.rework_level = "L3"
        mock_article.content = "<p>Check ISL9538H charging IC</p>"
        mock_article.content_bn = "<p>আইএসএল৯৫৩৮এইচ চার্জিং আইসি পরীক্ষা করুন</p>"
        mock_article.content_hash = "abcdef1234567890"
        mock_article.version = 3

        mock_self = MagicMock()
        mock_self.search.return_value = [mock_article]

        payload = FixKnowledgeArticle.get_offline_manuals(
            mock_self, brand="Dell", model="Latitude 5420"
        )
        self.assertEqual(len(payload), 1)
        item = payload[0]
        self.assertEqual(item["id"], 42)
        self.assertEqual(item["code"], "KB-HW-0042")
        self.assertEqual(item["brand"], "Dell")
        self.assertEqual(item["rework_level"], "L3")
        self.assertEqual(item["version"], 3)
        self.assertEqual(item["content_hash"], "abcdef1234567890")
        self.assertIn("ISL9538H", item["content_en"])


if __name__ == "__main__":
    unittest.main()
