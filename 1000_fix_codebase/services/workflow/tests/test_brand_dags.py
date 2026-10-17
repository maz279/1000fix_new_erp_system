import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from services.workflow.brand_submission_engine import (
    BrandTemplateRegistry,
    BrandSubmissionWorkflow,
    CompletenessViolationError,
)


class TestBrandSubmissionWorkflows(unittest.TestCase):
    """R05-M01-T03: Verifies 18 Airflow brand workflows and blocking completeness check."""

    def setUp(self):
        config_path = Path(__file__).resolve().parents[1] / "brand_templates.json"
        self.registry = BrandTemplateRegistry(config_path)
        self.templates = self.registry.list_all_templates()

    def test_eighteen_brand_templates_loaded(self):
        """Verify exactly 18 brand templates are configured (H2-12 resolution)."""
        self.assertEqual(len(self.templates), 18)
        codes = [t["brand_code"] for t in self.templates]
        self.assertEqual(len(set(codes)), 18)
        self.assertEqual(codes[0], "BRD-001")
        self.assertEqual(codes[-1], "BRD-018")

    def test_brand_names_conformance(self):
        expected_brands = [
            "Samsung", "Walton", "Dell", "HP", "Lenovo", "LG", "Singer", "Haier",
            "Gree", "Sony", "Xiaomi", "Asus", "Acer", "Apple", "Canon", "Philips",
            "Panasonic", "Whirlpool"
        ]
        loaded_names = [t["brand_name"] for t in self.templates]
        for name in expected_brands:
            self.assertIn(name, loaded_names, f"Missing brand template: {name}")

    def test_blocking_completeness_check_all_eighteen_brands(self):
        """T03: Incomplete evidence pack strictly raises CompletenessViolationError on all 18 brands."""
        incomplete_claim = {
            "claim_no": "CLM-INCOMPLETE-001",
            "device_serial": "SN-INC-001",
            "evidence_keys": ["photo_before", "diagnostic", "parts_issued"],  # missing 4 mandatory items
        }

        for tmpl in self.templates:
            workflow = BrandSubmissionWorkflow(tmpl)
            with self.assertRaises(CompletenessViolationError) as ctx:
                workflow.check_completeness(incomplete_claim)
            self.assertIn(tmpl["brand_name"], str(ctx.exception))
            self.assertTrue(len(ctx.exception.missing_items) > 0)

    def test_complete_pack_submits_green_all_eighteen_brands(self):
        """T03: Complete evidence pack transforms and submits successfully for all 18 brands."""
        complete_claim = {
            "claim_no": "CLM-VALID-2026",
            "device_serial": "SN-VALID-7890",
            "fault_code": "FLT-PWR-001",
            "diagnostic_summary": "Power supply unit capacitor replaced",
            "parts_list": [{"part_no": "CAP-100UF", "qty": 2, "cost": 450.0}],
            "labor_amount": 1200.0,
            "parts_amount": 900.0,
            "total_amount": 2100.0,
            "evidence_keys": [
                "photo_before", "photo_after", "diagnostic", "parts_issued",
                "device_serial", "technician_cert", "purchase_proof"
            ],
        }

        for tmpl in self.templates:
            workflow = BrandSubmissionWorkflow(tmpl)
            # 1. Check passes
            self.assertTrue(workflow.check_completeness(complete_claim))

            # 2. Execution succeeds
            ack = workflow.execute_submission(complete_claim)
            self.assertEqual(ack["status"], "submitted")
            self.assertEqual(ack["brand_code"], tmpl["brand_code"])
            self.assertIn("data", ack["payload"])
            self.assertTrue(len(ack["payload"]["data"]) > 0)

    def test_airflow_dags_generation(self):
        """Verify Airflow DAG file dynamically imports and registers 18 DAGs."""
        import dags.brand_warranty_submission_dag as dag_module
        dags_dict = dag_module.generated_dags
        self.assertEqual(len(dags_dict), 18)

        # Check sample DAG properties
        samsung_dag = dags_dict.get("warranty_submission_samsung")
        self.assertIsNotNone(samsung_dag)
        self.assertEqual(samsung_dag.dag_id, "warranty_submission_samsung")
        self.assertEqual(len(samsung_dag.tasks), 3)

        walton_dag = dags_dict.get("warranty_submission_walton")
        self.assertIsNotNone(walton_dag)
        self.assertEqual(walton_dag.dag_id, "warranty_submission_walton")
        self.assertEqual(len(walton_dag.tasks), 3)


if __name__ == "__main__":
    unittest.main()
