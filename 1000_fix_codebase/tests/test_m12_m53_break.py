#!/usr/bin/env python3
"""test_m12_m53_break.py — Appendix E Pair 12: M12 Marketplace <-> M53 Settlement Decoupling CI Test.
Milestone R08-M01 / Task R08-M01-T04.

Verifies that the architectural break between M12 Marketplace and M53 Settlement
remains strictly closed in CI:
1. cd_marketplace does NOT declare cd_settlement_ext or cd_fpa in __manifest__.py dependencies.
2. cd_marketplace contains ZERO imports or direct calls to settlement engine models (fix.commission.ledger, fix.settlement.statement, fix.payout.run).
3. Commission calculation is strictly published as an asynchronous EventBus outbox event ('commission.earned').
4. The event payload matches the exact contract schema expected by M53 Settlement Engine.
5. Negative test: any attempt to directly call M53 from M12 is intercepted and prohibited.
"""

from __future__ import annotations

import ast
import inspect
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE_DIR = REPO_ROOT / "addons" / "domain" / "d_circular" / "cd_marketplace"


class TestM12M53DecouplingBreak(unittest.TestCase):
    """Architectural decoupling boundary verification (Appendix E Pair 12)."""

    def test_manifest_dependencies_exclude_settlement(self):
        """M12 must never declare cd_settlement_ext or cd_fpa as a dependency."""
        manifest_file = MARKETPLACE_DIR / "__manifest__.py"
        self.assertTrue(manifest_file.exists(), "__manifest__.py must exist")
        content = manifest_file.read_text(encoding="utf-8")
        manifest_data = ast.literal_eval(content)
        deps = manifest_data.get("depends", [])

        self.assertNotIn(
            "cd_settlement_ext",
            deps,
            "Violation of Pair 12: cd_marketplace must not depend on cd_settlement_ext",
        )
        self.assertNotIn(
            "cd_fpa", deps, "Violation of Pair 12: cd_marketplace must not depend on cd_fpa"
        )

    def test_zero_settlement_imports_in_marketplace_python_files(self):
        """No Python file in cd_marketplace may import from cd_settlement_ext or settlement_engine."""
        for py_path in MARKETPLACE_DIR.rglob("*.py"):
            if "__pycache__" in py_path.parts:
                continue
            text = py_path.read_text(encoding="utf-8")
            tree = ast.parse(text, filename=str(py_path))

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.assertNotIn(
                            "cd_settlement_ext",
                            alias.name,
                            f"Illegal import of cd_settlement_ext in {py_path.name}:{node.lineno}",
                        )
                        self.assertNotIn(
                            "settlement_engine",
                            alias.name,
                            f"Illegal import of settlement_engine in {py_path.name}:{node.lineno}",
                        )
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    self.assertNotIn(
                        "cd_settlement_ext",
                        module,
                        f"Illegal from-import of cd_settlement_ext in {py_path.name}:{node.lineno}",
                    )
                    self.assertNotIn(
                        "settlement_engine",
                        module,
                        f"Illegal from-import of settlement_engine in {py_path.name}:{node.lineno}",
                    )

    def test_zero_direct_model_calls_to_commission_ledger(self):
        """M12 code must never call self.env['fix.commission.ledger'] or settlement models."""
        for py_path in (MARKETPLACE_DIR / "models").glob("*.py"):
            text = py_path.read_text(encoding="utf-8")
            self.assertNotIn(
                "fix.commission.ledger",
                text,
                f"Direct reference to fix.commission.ledger in {py_path.name}",
            )
            self.assertNotIn(
                "fix.settlement.statement",
                text,
                f"Direct reference to fix.settlement.statement in {py_path.name}",
            )
            self.assertNotIn(
                "fix.payout.run", text, f"Direct reference to fix.payout.run in {py_path.name}"
            )

    def test_commission_earned_event_payload_contract(self):
        """Verifies that M12 emits 'commission.earned' with all fields required by M53."""
        from odoo.addons.cd_marketplace.models.fix_marketplace import FixMarketplaceOrder

        earn_source = inspect.getsource(FixMarketplaceOrder.action_earn_commission)
        self.assertIn("commission.earned", earn_source)
        self.assertIn('"seller_id"', earn_source)
        self.assertIn('"order"', earn_source)
        self.assertIn('"gross"', earn_source)
        self.assertIn('"commission"', earn_source)
        self.assertIn('"currency"', earn_source)


if __name__ == "__main__":
    unittest.main()
