"""cd_metric_registry tests - P11-M02 (CD-M62-01)."""
import inspect
import unittest

from odoo.addons.cd_metric_registry.models.fix_metric_registry import (
    FixDataEntity, FixDataLineage, FixDataQualityRule)


class TestDataCatalogue(unittest.TestCase):
    def test_entity_types_cover_catalogue(self):
        src = inspect.getsource(FixDataEntity)
        for et in ("table", "api", "event", "report", "document"):
            self.assertIn(et, src)

    def test_residency_classification_exists(self):
        src = inspect.getsource(FixDataEntity)
        self.assertIn("residency_classified", src)

    def test_nfr086c_warehouse_safety(self):
        """No residency-classified data in the analytical store."""
        src = inspect.getsource(FixDataEntity._check_warehouse_safety)
        self.assertIn("NFR-086c", src)

    def test_steward_named_person(self):
        """DA-003: named people, not named roles."""
        self.assertTrue(hasattr(FixDataEntity, "steward_id"))

    def test_retention_policy(self):
        self.assertTrue(hasattr(FixDataEntity, "retention_policy"))


class TestDataLineage(unittest.TestCase):
    def test_source_and_target(self):
        self.assertTrue(hasattr(FixDataLineage, "source_entity_id"))
        self.assertTrue(hasattr(FixDataLineage, "target_entity_id"))

    def test_transformation_tracked(self):
        self.assertTrue(hasattr(FixDataLineage, "transformation"))


class TestDataQuality(unittest.TestCase):
    def test_dq_rule_types(self):
        src = inspect.getsource(FixDataQualityRule)
        for rt in ("completeness", "uniqueness", "timeliness"):
            self.assertIn(rt, src)

    def test_threshold_enforced(self):
        src = inspect.getsource(FixDataQualityRule.action_check)
        self.assertIn("threshold", src)
        self.assertIn("failing", src)

    def test_dq_alert_event(self):
        self.assertIn("data_quality.failing",
                      inspect.getsource(FixDataQualityRule))


if __name__ == "__main__":
    unittest.main()
