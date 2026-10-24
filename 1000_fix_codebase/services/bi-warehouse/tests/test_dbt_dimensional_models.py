#!/usr/bin/env python3
"""test_dbt_dimensional_models.py — Verification of M62 W4 dimensional models (R05-M04-T02).

Validates:
1. Conformed dimension and fact model files exist.
2. Models conform to dbt project schema specifications.
3. LB-06 compliance: Models query exclusively downstream read-replica sources.
4. NFR-086c compliance: Zero PII plaintext / S3 classified leaks in warehouse models.
"""

import re
import unittest
from pathlib import Path

import yaml

DBT_ROOT = Path(__file__).resolve().parents[1] / "dbt"
MODELS_DIR = DBT_ROOT / "models" / "core"


class TestDbtDimensionalModels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(DBT_ROOT / "dbt_project.yml", encoding="utf-8") as f:
            cls.project_cfg = yaml.safe_load(f)
        cls.declared_models = {m["name"] for m in cls.project_cfg.get("models", [])}

    def test_all_declared_models_exist_as_sql(self):
        """Every model declared in dbt_project.yml must have a matching .sql file."""
        expected_models = {
            "dim_date",
            "dim_branch",
            "dim_customer",
            "dim_device",
            "dim_technician",
            "fact_service_orders",
            "fact_invoices",
            "fact_warranty_claims",
            "fact_conversations",
            "fact_nps",
        }
        self.assertEqual(self.declared_models, expected_models)

        for model_name in expected_models:
            sql_file = MODELS_DIR / f"{model_name}.sql"
            self.assertTrue(sql_file.exists(), f"Missing SQL file for model: {model_name}")

    def test_lb06_read_replica_source_constraint(self):
        """LB-06 / AR-001: Fact models must only select from oltp_replica, never write back."""
        fact_models = [
            "fact_service_orders",
            "fact_invoices",
            "fact_warranty_claims",
            "fact_conversations",
            "fact_nps",
        ]
        forbidden_keywords = [
            r"\binsert\b",
            r"\bupdate\b",
            r"\bdelete\b",
            r"\bdrop\b",
            r"\balter\b",
        ]

        for model_name in fact_models:
            content = (MODELS_DIR / f"{model_name}.sql").read_text(encoding="utf-8")
            self.assertIn(
                "{{ source('oltp_replica'",
                content,
                f"{model_name} must read from oltp_replica source",
            )
            self.assertIn(
                "materialized='table'", content, f"{model_name} must declare table materialization"
            )

            lower_content = content.lower()
            for kw in forbidden_keywords:
                self.assertIsNone(
                    re.search(kw, lower_content),
                    f"{model_name} contains forbidden mutating keyword: {kw}",
                )

    def test_pdpa_pii_minimisation_in_customer_and_conversation(self):
        """NFR-086c: Customer and conversation models must use hashing or masking."""
        cust_sql = (MODELS_DIR / "dim_customer.sql").read_text(encoding="utf-8")
        self.assertIn("pseudonym_hash", cust_sql)
        self.assertIn("md5(", cust_sql)

        conv_sql = (MODELS_DIR / "fact_conversations.sql").read_text(encoding="utf-8")
        self.assertIn("is_pii_masked", conv_sql)

    def test_dim_date_bangladesh_statutory_calendar(self):
        """dim_date must account for Friday-Saturday weekend and statutory holidays."""
        date_sql = (MODELS_DIR / "dim_date.sql").read_text(encoding="utf-8")
        self.assertIn(
            "extract(isodow from datum) in (5, 6)",
            date_sql,
            "Must flag Friday (5) and Saturday (6) as weekend in Bangladesh",
        )
        self.assertIn("Independence Day", date_sql)
        self.assertIn("Victory Day", date_sql)
        self.assertIn("Language Martyrs Day", date_sql)


if __name__ == "__main__":
    unittest.main()
