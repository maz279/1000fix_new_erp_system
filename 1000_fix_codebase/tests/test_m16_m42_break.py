"""tests/test_m16_m42_break.py — Appendix E Pair 10 Asymmetric Break Verification.

Enforces that M42 (Supplier Relationship & Performance) is an asynchronous
read-and-score consumer of M16 domain events, preventing bidirectional coupling:
1. M42 consumes M16 'goods.received' events via API/event bus.
2. M42 never performs direct SQL or ORM searches on M16 purchase tables.
3. M42 computes weighted supplier scorecards (0.6 on_time + 0.4 quality).
4. Scorecards are published as 'supplier.scorecard' events for Portal P05.
5. The manifest of cd_cx_feedback does not declare direct circular dependencies on M16.
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CX_FEEDBACK_DIR = REPO_ROOT / "addons" / "domain" / "b_customer_engagement" / "cd_cx_feedback"
CX_FEEDBACK_MODEL = CX_FEEDBACK_DIR / "models" / "fix_cx_feedback.py"
CX_FEEDBACK_MANIFEST = CX_FEEDBACK_DIR / "__manifest__.py"


class TestM16M42AsymmetricBreak(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model_code = CX_FEEDBACK_MODEL.read_text(encoding="utf-8")
        manifest_text = CX_FEEDBACK_MANIFEST.read_text(encoding="utf-8")
        cls.manifest = ast.literal_eval(manifest_text)

    def test_supplier_scorecard_model_defined(self):
        """M42 scorecard model fix.supplier.scorecard must exist."""
        self.assertIn('_name = "fix.supplier.scorecard"', self.model_code)

    def test_no_direct_m16_table_queries(self):
        """M42 must not query M16 purchase order tables directly (cycle break)."""
        forbidden_queries = [
            'self.env["fix.purchase.order"].search',
            'self.env["purchase.order"].search',
            'self.env["purchase.order.line"].search',
        ]
        for query in forbidden_queries:
            self.assertNotIn(query, self.model_code, f"Forbidden query found: {query}")

    def test_consumes_goods_received_event(self):
        """M42 must consume 'goods.received' events to evaluate performance."""
        self.assertIn("def consume_goods_received(self, event", self.model_code)
        self.assertIn("lines_on_time", self.model_code)
        self.assertIn("lines_late", self.model_code)

    def test_weighted_scoring_formula(self):
        """M42 must apply the canonical 0.6 on-time + 0.4 quality weighting."""
        self.assertIn("0.6 * on_time + 0.4 * quality", self.model_code)

    def test_publishes_scorecards_for_p05_portal(self):
        """M42 must publish scorecards via event bus for the P05 vendor portal.

        Asserted on the AST, not the source text: a formatter re-wrapping the
        call across lines must not change the verdict."""
        topics = {
            node.args[1].value
            for node in ast.walk(ast.parse(self.model_code))
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "publish"
            and len(node.args) >= 2
            and isinstance(node.args[1], ast.Constant)
        }
        self.assertIn("supplier.scorecard", topics)

    def test_vendor_period_unique_constraint(self):
        """Ensure period uniqueness constraint to prevent duplicate scorecards."""
        self.assertIn("vendor_period_unique", self.model_code)

    def test_manifest_avoids_circular_m16_dependency(self):
        """Manifest must not declare circular dependency on M16 purchase models."""
        depends = self.manifest.get("depends", [])
        self.assertNotIn("purchase", depends)
        self.assertNotIn("cd_purchase", depends)


if __name__ == "__main__":
    unittest.main()
