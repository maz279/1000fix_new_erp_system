"""GV-009: tooling/scripts/verify-stock-layer.py derives every component status from
parsed manifests (installable / depends / series) - a broken vendor tree is a FAIL,
never a hard-coded PASS."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "scripts" / "verify-stock-layer.py"


def _load():
    spec = importlib.util.spec_from_file_location("verify_stock_layer_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _manifest(path: Path, body: str) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / "__manifest__.py").write_text(body, encoding="utf-8")


def _oca(version="19.0.1.0.0", depends="['stock']", installable="True") -> str:
    return (
        f"{{'name': 'x', 'version': '{version}', 'depends': {depends}, "
        f"'installable': {installable}}}"
    )


class VerifyStockLayerTest(unittest.TestCase):
    def setUp(self):
        self.m = _load()
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.root = root
        odoo = root / "vendor" / "odoo"
        (odoo / "odoo").mkdir(parents=True)
        (odoo / "odoo" / "release.py").write_text(
            "version_info = (19, 0, 0, FINAL, 0, '')\n", encoding="utf-8"
        )
        _manifest(odoo / "odoo" / "addons" / "base", "{'name': 'base', 'depends': []}")
        _manifest(odoo / "addons" / "product", "{'name': 'product', 'depends': ['base']}")
        _manifest(odoo / "addons" / "stock", "{'name': 'Inventory', 'depends': ['product']}")
        oca = root / "vendor" / "oca"
        for repo, mod in self.m.KEY_OCA_MODULES:
            _manifest(oca / repo / mod, _oca())
        _manifest(oca / "stock-logistics-barcode" / "barcodes_generator_abstract", _oca())
        self.m.REPO_ROOT = root
        self.m.VENDOR_ODOO = odoo / "addons"
        self.m.VENDOR_ODOO_BASE = odoo / "odoo" / "addons"
        self.m.ODOO_RELEASE = odoo / "odoo" / "release.py"
        self.m.VENDOR_OCA = oca
        self.m.EVIDENCE_DIR = root / "evidence"

    def tearDown(self):
        self.tmp.cleanup()

    def _evidence(self) -> dict:
        return json.loads((self.m.EVIDENCE_DIR / self.m.EVIDENCE_NAME).read_text("utf-8"))

    def test_consistent_tree_is_measured_pass(self):
        self.assertEqual(self.m.main(), 0)
        ev = self._evidence()
        self.assertEqual(ev["verdict"], "PASS")
        self.assertEqual(ev["checks_passed"], ev["checks_total"])

    def test_off_series_key_module_fails(self):
        oca = self.m.VENDOR_OCA
        _manifest(
            oca / "stock-logistics-workflow" / "stock_no_negative", _oca(version="18.0.1.0.0")
        )
        self.assertEqual(self.m.main(), 1)
        ev = self._evidence()
        self.assertEqual(ev["verdict"], "FAIL")
        bad = [r for r in ev["results"] if r["status"] == "FAIL"]
        self.assertTrue(any("stock_no_negative" in r["component"] for r in bad))

    def test_unresolved_depends_and_not_installable_fail(self):
        oca = self.m.VENDOR_OCA
        _manifest(
            oca / "stock-logistics-warehouse" / "stock_inventory",
            _oca(depends="['stock', 'no_such_module']", installable="False"),
        )
        self.assertEqual(self.m.main(), 1)
        result = next(
            r for r in self._evidence()["results"] if r["component"].endswith("stock_inventory")
        )
        self.assertEqual(result["status"], "FAIL")
        joined = " ".join(result["problems"])
        self.assertIn("no_such_module", joined)
        self.assertIn("installable=False", joined)

    def test_missing_repo_and_unparseable_manifest_fail(self):
        import shutil

        shutil.rmtree(self.m.VENDOR_OCA / "stock-logistics-barcode")
        (self.m.VENDOR_ODOO / "stock" / "__manifest__.py").write_text("{not python", "utf-8")
        self.assertEqual(self.m.main(), 1)
        statuses = {r["component"]: r["status"] for r in self._evidence()["results"]}
        self.assertEqual(statuses["stock-logistics-barcode"], "FAIL")
        self.assertEqual(statuses["odoo_core_stock"], "FAIL")


if __name__ == "__main__":
    unittest.main()
