# services/bi-warehouse/tests/test_catalogue_engine.py
# Unit tests for catalogue_engine.py (Milestone R09-M02).
import sys
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from catalogue_engine import DATA_DOMAINS, WAREHOUSE_FEEDS, DataGovernanceEngine


class TestCatalogueEngine(unittest.TestCase):
    """Rigorous tests for the bi-warehouse Data Governance Engine."""

    def setUp(self):
        self.engine = DataGovernanceEngine()

    def test_domains_and_stewards_specification(self):
        """Verifies exactly 12 domains and named stewards per DA-003 §3.2."""
        self.assertEqual(len(DATA_DOMAINS), 12)
        steward_names = {d["steward"] for d in DATA_DOMAINS}
        self.assertEqual(len(steward_names), 12, "Every domain must have a distinct named steward")
        for d in DATA_DOMAINS:
            self.assertTrue(d["id"].startswith("DD-"))
            self.assertTrue(
                len(d["steward"].split()) >= 2, f"Steward must be a named person: {d['steward']}"
            )
            self.assertTrue(d["retention"], f"Domain {d['id']} missing retention policy")

    def test_full_catalogue_generation(self):
        """R09-M02-T01: the catalogue reports the REAL entity count (31 known
        entities) against the DA-002 target (1,335) - 2.32% coverage, FAIL.
        No entities are synthesised to pad the count."""
        report = self.engine.build_full_catalogue()
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["total_entities_catalogued"], 31)
        self.assertEqual(report["target_entity_count"], 1335)
        self.assertEqual(report["completeness_pct"], 2.32)
        self.assertEqual(len(self.engine.entities), 31)
        # Every catalogued entity is a REAL named entity, no fix_cd_* filler.
        for e in self.engine.entities:
            self.assertRegex(e["name"], r"^(fix_|fact_|dim_|res_|account_|stock_|hr_|mail_)")
        # Coverage fields describe the catalogued entities only.
        self.assertEqual(report["owner_module_coverage_pct"], 100.0)
        self.assertEqual(report["named_steward_coverage_pct"], 100.0)
        self.assertEqual(report["classification_coverage_pct"], 100.0)
        self.assertEqual(report["retention_policy_coverage_pct"], 100.0)
        self.assertIn("FAILs until the remaining estate is genuinely catalogued", report["finding"])

    def test_warehouse_feed_lineage(self):
        """R09-M02-T02: Lineage across all 10 warehouse feeds with transformations."""
        self.assertEqual(len(WAREHOUSE_FEEDS), 10)
        report = self.engine.build_warehouse_lineage()
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["total_warehouse_feeds"], 10)
        self.assertEqual(report["lineage_coverage_pct"], 100.0)
        for feed in report["feeds"]:
            self.assertTrue(feed["transformation"])
            self.assertTrue(feed["grain"])
            self.assertTrue(feed["pii_masked"])

    def test_dq_monitoring_with_seeded_alert(self):
        """R09-M02-T03: DQ monitoring with thresholds and alert wire verification."""
        report = self.engine.run_dq_monitoring_with_seeded_failure()
        self.assertEqual(report["status"], "PASS")
        self.assertTrue(report["seeded_failure_tested"])
        self.assertTrue(report["seeded_failure_alert_dispatched"])
        self.assertEqual(report["rules_evaluated"], 5)
        self.assertEqual(report["failing_rules_count"], 1)

    def test_nfr086c_residency_scan(self):
        """R09-M02-T04: NFR-086c zero residency data in analytical warehouse."""
        report = self.engine.audit_warehouse_residency_scan()
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["violations_count"], 0)
        self.assertEqual(len(report["violations"]), 0)
        self.assertGreaterEqual(report["scanned_files_count"], 10)

    def test_full_governance_suite(self):
        """The suite is honest: the incomplete catalogue (31/1335 real entities)
        fails R09-M02-T01 even though lineage, DQ and residency tasks pass."""
        res = self.engine.run_full_governance_suite()
        self.assertEqual(res["status"], "FAIL")
        self.assertEqual(res["tasks"]["R09-M02-T01"], "FAIL")
        self.assertEqual(res["tasks"]["R09-M02-T02"], "PASS")
        self.assertEqual(res["tasks"]["R09-M02-T03"], "PASS")
        self.assertEqual(res["tasks"]["R09-M02-T04"], "PASS")


if __name__ == "__main__":
    unittest.main()
