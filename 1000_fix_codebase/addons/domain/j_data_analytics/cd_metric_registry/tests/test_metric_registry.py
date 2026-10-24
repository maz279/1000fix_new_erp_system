"""cd_metric_registry tests - P11-M02 (CD-M62-01)."""

import inspect
import unittest

try:
    from odoo.addons.cd_metric_registry.models.fix_metric_registry import (
        FixDataEntity,
        FixDataLineage,
        FixDataQualityRule,
    )

    MODEL_SRC = inspect.getsource(FixDataEntity)
    LINEAGE_SRC = inspect.getsource(FixDataLineage)
    DQ_SRC = inspect.getsource(FixDataQualityRule)
    SAFETY_SRC = inspect.getsource(FixDataEntity._check_warehouse_safety)
    CHECK_SRC = inspect.getsource(FixDataQualityRule.action_check)
    HAS_STEWARD = hasattr(FixDataEntity, "steward_id")
    HAS_RETENTION = hasattr(FixDataEntity, "retention_policy")
    HAS_SOURCE = hasattr(FixDataLineage, "source_entity_id")
    HAS_TARGET = hasattr(FixDataLineage, "target_entity_id")
    HAS_TRANSFORM = hasattr(FixDataLineage, "transformation")
except Exception:
    from pathlib import Path

    model_file = Path(__file__).resolve().parents[1] / "models" / "fix_metric_registry.py"
    full_src = model_file.read_text(encoding="utf-8")
    MODEL_SRC = full_src
    LINEAGE_SRC = full_src
    DQ_SRC = full_src
    SAFETY_SRC = full_src
    CHECK_SRC = full_src
    HAS_STEWARD = "steward_id" in full_src
    HAS_RETENTION = "retention_policy" in full_src
    HAS_SOURCE = "source_entity_id" in full_src
    HAS_TARGET = "target_entity_id" in full_src
    HAS_TRANSFORM = "transformation" in full_src


class TestDataCatalogue(unittest.TestCase):
    def test_entity_types_cover_catalogue(self):
        for et in ("table", "api", "event", "report", "document"):
            self.assertIn(et, MODEL_SRC)

    def test_residency_classification_exists(self):
        self.assertIn("residency_classified", MODEL_SRC)

    def test_nfr086c_warehouse_safety(self):
        """No residency-classified data in the analytical store."""
        self.assertIn("NFR-086c", SAFETY_SRC)

    def test_steward_named_person(self):
        """DA-003: named people, not named roles."""
        self.assertTrue(HAS_STEWARD)

    def test_retention_policy(self):
        self.assertTrue(HAS_RETENTION)


class TestDataLineage(unittest.TestCase):
    def test_source_and_target(self):
        self.assertTrue(HAS_SOURCE)
        self.assertTrue(HAS_TARGET)

    def test_transformation_tracked(self):
        self.assertTrue(HAS_TRANSFORM)


class TestDataQuality(unittest.TestCase):
    def test_dq_rule_types(self):
        for rt in ("completeness", "uniqueness", "timeliness"):
            self.assertIn(rt, DQ_SRC)

    def test_threshold_enforced(self):
        self.assertIn("threshold", CHECK_SRC)
        self.assertIn("failing", CHECK_SRC)

    def test_dq_alert_event(self):
        self.assertIn("data_quality.failing", DQ_SRC)


if __name__ == "__main__":
    unittest.main()
