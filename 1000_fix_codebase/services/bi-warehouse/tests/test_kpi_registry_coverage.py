#!/usr/bin/env python3
"""test_kpi_registry_coverage.py — Verification of 95 registered KPIs and BM-002 reconciliation (R05-M04-T03).

Validates:
1. Exactly 95 registered KPIs exist in services/bi-warehouse/kpi-register.json.
2. Contiguous KPI-001 through KPI-095 numbering without gaps or duplicates.
3. Every delivered module has its KPIs visible in M25 (DoD-09).
4. BM-002 reconciliation arithmetic is verified.
5. Formal reconciliation document exists.
"""

import json
import unittest
from pathlib import Path

BI_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]


class TestKpiRegistryCoverage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        json_path = BI_ROOT / "kpi-register.json"
        with open(json_path, encoding="utf-8") as f:
            cls.data = json.load(f)
        cls.register = cls.data.get("register", [])

    def test_exact_95_registered_kpis(self):
        """The register must contain exactly 95 registered KPIs (06-02 section 2)."""
        self.assertEqual(len(self.register), 95, f"Expected 95 KPIs, got {len(self.register)}")
        self.assertEqual(self.data.get("total_registered"), 95)

    def test_contiguous_kpi_numbering(self):
        """KPI IDs must run contiguously from KPI-001 through KPI-095 without duplicates."""
        kpi_ids = [item["kpi"] for item in self.register]
        self.assertEqual(len(kpi_ids), len(set(kpi_ids)), "Duplicate KPI IDs found in register")

        expected_ids = [f"KPI-{i:03d}" for i in range(1, 96)]
        self.assertEqual(kpi_ids, expected_ids, "KPI sequence must match KPI-001..KPI-095 exactly")

    def test_required_metadata_fields(self):
        """Every KPI entry must declare ID, name, family, baseline, targets, source, owner, and formula."""
        required_fields = [
            "kpi",
            "name",
            "family",
            "baseline",
            "w4_target",
            "w8_target",
            "source",
            "owner",
            "formula",
        ]
        for item in self.register:
            for field in required_fields:
                self.assertIn(field, item, f"Missing field '{field}' in {item.get('kpi')}")
                self.assertTrue(
                    str(item[field]).strip(), f"Empty field '{field}' in {item.get('kpi')}"
                )

    def test_ten_kpi_families_represented(self):
        """All 10 families from 06-02 section 2 must be present."""
        expected_families = {
            "service",
            "field_ops",
            "customer",
            "commercial",
            "warranty",
            "supply_chain",
            "financial",
            "people_quality",
            "new_business",
            "platform",
        }
        actual_families = {item["family"] for item in self.register}
        self.assertEqual(actual_families, expected_families)

    def test_dod09_delivered_modules_visible(self):
        """DoD-09: Every delivered module (M01, M02, M08, M09, M19, M20, M27) must have visible KPIs."""
        delivered_owners = {"M01", "M02", "M08", "M09", "M19", "M20", "M27"}
        actual_owners = {item["owner"] for item in self.register}
        for owner in delivered_owners:
            self.assertIn(
                owner, actual_owners, f"Delivered module {owner} has no KPIs in M25 register"
            )

    def test_bm002_reconciliation_integrity(self):
        """BM-002 arithmetic must hold: 95 registered, 250 in specs, 196 operational, 41 unproduced, 54 both."""
        rec = self.data.get("reconciliation_bm002", {})
        self.assertEqual(rec.get("registered_count"), 95)
        self.assertEqual(rec.get("distinct_in_specifications"), 250)
        self.assertEqual(rec.get("used_but_unregistered"), 196)
        self.assertEqual(rec.get("registered_but_unproduced"), 41)
        self.assertEqual(rec.get("both_registered_and_used"), 54)
        self.assertEqual(rec.get("unallocated_gap"), 14)

        # Verification equations from BM-002 section 9.1
        self.assertEqual(rec["both_registered_and_used"] + rec["used_but_unregistered"], 250)
        self.assertEqual(rec["both_registered_and_used"] + rec["registered_but_unproduced"], 95)
        self.assertEqual(rec["registered_count"] + rec["used_but_unregistered"], 291)

    def test_reconciliation_document_exists(self):
        """The formal documentation BM-002-reconciliation-95-vs-250.md must exist."""
        doc_path = REPO_ROOT / "docs" / "analytics" / "BM-002-reconciliation-95-vs-250.md"
        self.assertTrue(doc_path.exists(), "Missing BM-002 reconciliation report")
        content = doc_path.read_text(encoding="utf-8")
        self.assertIn("95 Registered vs. 250 In-Use Metrics", content)
        self.assertIn("KPI-110", content)


if __name__ == "__main__":
    unittest.main()
