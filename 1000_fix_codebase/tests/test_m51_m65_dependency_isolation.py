#!/usr/bin/env python3
"""test_m51_m65_dependency_isolation.py — Milestone R10-M01-T02.

Verifies Appendix E architectural isolation rule:
"M51 (cd_tax_engine_bd) depends on M30's cd_country_pack interface, never on M65 (cd_multi_entity) directly."
"""

import ast
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
for p in (str(REPO_ROOT), str(REPO_ROOT / "vendor" / "odoo")):
    if p not in sys.path:
        sys.path.insert(0, p)

M51_MANIFEST = (
    REPO_ROOT / "addons" / "domain" / "g_finance" / "cd_tax_engine_bd" / "__manifest__.py"
)
M51_DIR = REPO_ROOT / "addons" / "domain" / "g_finance" / "cd_tax_engine_bd"
M65_MANIFEST = REPO_ROOT / "addons" / "platform" / "cd_multi_entity" / "__manifest__.py"


class TestM51M65DependencyIsolation(unittest.TestCase):
    """Rigorous negative dependency test for M51 vs M65 decoupling."""

    def test_m51_manifest_depends_on_m30_not_m65(self):
        """Verify M51 declares cd_entity_config (M30) in depends, never cd_multi_entity (M65)."""
        self.assertTrue(M51_MANIFEST.exists(), "M51 manifest must exist")
        content = M51_MANIFEST.read_text(encoding="utf-8")
        manifest_dict = ast.literal_eval(content)

        deps = manifest_dict.get("depends", [])
        self.assertIn("cd_entity_config", deps, "M51 must depend on M30 (cd_entity_config)")
        self.assertNotIn(
            "cd_multi_entity", deps, "M51 must NEVER depend directly on M65 (cd_multi_entity)"
        )

    def test_m51_source_code_has_no_imports_of_cd_multi_entity(self):
        """Scan all Python files in cd_tax_engine_bd to prove 0 direct imports of cd_multi_entity."""
        py_files = list(M51_DIR.glob("**/*.py"))
        self.assertTrue(len(py_files) > 0, "M51 must contain python files")

        for py_path in py_files:
            source = py_path.read_text(encoding="utf-8", errors="replace")
            self.assertNotIn(
                "cd_multi_entity",
                source,
                f"Violation in {py_path.name}: M51 must not import cd_multi_entity",
            )
            self.assertNotIn(
                "fix.consolidation",
                source,
                f"Violation in {py_path.name}: M51 must not reference consolidation models",
            )
            self.assertNotIn(
                "fix.intercompany",
                source,
                f"Violation in {py_path.name}: M51 must not reference intercompany models",
            )

    def test_m65_manifest_declares_cd_entity_config(self):
        """Verify M65 properly depends on cd_entity_config for base legal entity models."""
        self.assertTrue(M65_MANIFEST.exists(), "M65 manifest must exist")
        content = M65_MANIFEST.read_text(encoding="utf-8")
        manifest_dict = ast.literal_eval(content)
        deps = manifest_dict.get("depends", [])
        self.assertIn("cd_entity_config", deps)
        self.assertEqual(manifest_dict.get("x_module_id"), "M65")
        self.assertEqual(manifest_dict.get("x_cd_id"), "CD-M65-03")

    def test_country_pack_data_loader_satisfies_interface(self):
        """Verify Bangladesh country pack loader populates M30's fix.country.pack."""
        pack_file = (
            REPO_ROOT
            / "addons"
            / "platform"
            / "cd_multi_entity"
            / "models"
            / "fix_bd_country_pack_data.py"
        )
        self.assertTrue(pack_file.exists(), "fix_bd_country_pack_data.py must exist")

        tree = ast.parse(pack_file.read_text(encoding="utf-8"))
        divisions = None
        districts = None
        holidays = None
        has_loader_method = False

        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if target.id == "BANGLADESH_DIVISIONS":
                            divisions = ast.literal_eval(node.value)
                        elif target.id == "BANGLADESH_DISTRICTS":
                            districts = ast.literal_eval(node.value)
                        elif target.id == "STATUTORY_HOLIDAYS_2026":
                            holidays = ast.literal_eval(node.value)
            elif isinstance(node, ast.ClassDef) and node.name == "FixCountryPackDataLoader":
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "load_bangladesh_pack":
                        has_loader_method = True

        self.assertIsNotNone(divisions, "BANGLADESH_DIVISIONS must be defined")
        self.assertEqual(len(divisions), 8, "Must define exactly 8 divisions")
        self.assertIsNotNone(districts, "BANGLADESH_DISTRICTS must be defined")
        self.assertEqual(len(districts), 64, "Must define 64 districts")
        self.assertIsNotNone(holidays, "STATUTORY_HOLIDAYS_2026 must be defined")
        self.assertTrue(len(holidays) >= 10, "Must define at least 10 gazetted holidays")
        self.assertTrue(
            has_loader_method, "FixCountryPackDataLoader must implement load_bangladesh_pack"
        )


if __name__ == "__main__":
    unittest.main()
