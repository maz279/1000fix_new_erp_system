"""test_m12_m53_dependency_break — Appendix E Pair 12 Verification.

R05-M02-T03: Commission engine fed by events only (M12 earning is an event;
M53 never called by M12 — verify by dependency negative test).

Audits:
1. M12 (addons/domain/d_circular/cd_marketplace) AST has zero imports of M53
   (cd_settlement_ext, services/settlement-engine).
2. M12 production models and controllers have zero direct calls or lookups into
   fix.commission.ledger or fix.payout.run.
3. M12 communicates commission exclusively by publishing 'commission.earned'
   through fix_events.
4. M53 (cd_settlement_ext) production AST has zero imports or dependencies on
   cd_marketplace.
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MARKETPLACE_DIR = REPO_ROOT / "addons" / "domain" / "d_circular" / "cd_marketplace"
SETTLEMENT_DIR = REPO_ROOT / "addons" / "domain" / "g_finance" / "cd_settlement_ext"
SERVICES_SETTLEMENT = REPO_ROOT / "services" / "settlement-engine"


class TestM12M53DependencyBreak(unittest.TestCase):
    """Architectural decoupling negative test suite."""

    def test_m12_zero_m53_imports(self):
        """M12 must never import M53 modules or settlement engine."""
        forbidden_import_tokens = (
            "cd_settlement_ext",
            "settlement_engine",
            "fix.commission.ledger",
            "fix.payout.run",
        )
        for py_file in MARKETPLACE_DIR.rglob("*.py"):
            text = py_file.read_text(encoding="utf-8")
            tree = ast.parse(text, filename=str(py_file))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        name_lower = alias.name.lower()
                        for forbidden in forbidden_import_tokens:
                            self.assertNotIn(
                                forbidden,
                                name_lower,
                                f"Forbidden import '{alias.name}' in {py_file.name}",
                            )
                elif isinstance(node, ast.ImportFrom):
                    mod = (node.module or "").lower()
                    for forbidden in forbidden_import_tokens:
                        self.assertNotIn(
                            forbidden,
                            mod,
                            f"Forbidden from-import '{node.module}' in {py_file.name}",
                        )

    def test_m12_zero_direct_model_lookups_into_m53(self):
        """M12 production models/controllers must never query or access M53 models directly via env['fix.commission.ledger'] etc."""
        forbidden_models = (
            "fix.commission.ledger",
            "fix.payout.run",
        )
        for py_dir in (MARKETPLACE_DIR / "models", MARKETPLACE_DIR / "controllers"):
            for py_file in py_dir.glob("*.py"):
                text = py_file.read_text(encoding="utf-8")
                for model in forbidden_models:
                    self.assertNotIn(
                        f'"{model}"',
                        text,
                        f"Direct reference to M53 model '{model}' found in {py_file.name}",
                    )
                    self.assertNotIn(
                        f"'{model}'",
                        text,
                        f"Direct reference to M53 model '{model}' found in {py_file.name}",
                    )

    def test_m12_publishes_commission_earned_event(self):
        """M12 communicates commission earnings strictly via event publishing."""
        # Structural, not textual (R01 re-audit: the docstring-phrase match
        # broke on whitespace while the contract was intact): the method
        # exists and itself calls publish(env, "commission.earned", ...).
        mkt_file = MARKETPLACE_DIR / "models" / "fix_marketplace.py"
        tree = ast.parse(mkt_file.read_text(encoding="utf-8"))
        method = next(
            (
                n
                for n in ast.walk(tree)
                if isinstance(n, ast.FunctionDef) and n.name == "action_earn_commission"
            ),
            None,
        )
        self.assertIsNotNone(method, "action_earn_commission is missing")
        published = [
            call.args[1].value
            for call in ast.walk(method)
            if isinstance(call, ast.Call)
            and getattr(call.func, "id", getattr(call.func, "attr", None)) == "publish"
            and len(call.args) > 1
            and isinstance(call.args[1], ast.Constant)
        ]
        self.assertIn("commission.earned", published)

    def test_m53_zero_m12_imports(self):
        """M53 production code must not import from cd_marketplace."""
        for py_file in list(SETTLEMENT_DIR.rglob("*.py")) + list(SERVICES_SETTLEMENT.rglob("*.py")):
            if "test" in py_file.name.lower():
                continue
            text = py_file.read_text(encoding="utf-8")
            tree = ast.parse(text, filename=str(py_file))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.assertNotIn("cd_marketplace", alias.name.lower())
                elif isinstance(node, ast.ImportFrom):
                    mod = (node.module or "").lower()
                    self.assertNotIn("cd_marketplace", mod)


if __name__ == "__main__":
    unittest.main()
