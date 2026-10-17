"""document-generation tests — P06-M03-T07 (TR-07, BN-007)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from document_generation import (  # noqa: E402
    DOCUMENT_TEMPLATES,
    RenderJob,
    format_amount,
    render,
)


class TestTemplates(unittest.TestCase):
    def test_w3_document_set_present(self):
        self.assertIn("mushak_6_3", DOCUMENT_TEMPLATES)
        self.assertTrue(DOCUMENT_TEMPLATES["mushak_6_3"]["statutory"])
        self.assertIn("mushak_6_6", DOCUMENT_TEMPLATES)
        self.assertTrue(DOCUMENT_TEMPLATES["mushak_6_6"]["statutory"])
        self.assertIn("withholding_certificate", DOCUMENT_TEMPLATES)
        self.assertTrue(DOCUMENT_TEMPLATES["withholding_certificate"]["statutory"])


    def test_statutory_templates_carry_reference_images(self):
        for name, tpl in DOCUMENT_TEMPLATES.items():
            if tpl["statutory"]:
                self.assertTrue(tpl["reference"], f"{name} lacks a TR-07 reference")


class TestRender(unittest.TestCase):
    def test_unknown_template_refused(self):
        result = render(RenderJob("nope"))
        self.assertEqual(result.status, "unknown-template")

    def test_dry_run_without_runtime(self):
        result = render(RenderJob("mushak_6_3", payload={"amount": 100.0}))
        self.assertEqual(result.status, "dry-run")
        self.assertEqual(result.qweb_ref, "cd_tax_engine_bd.report_mushak63")

    def test_checks_carry_tr07_contract(self):
        result = render(RenderJob("mushak_6_3", locale="bn", payload={"amount": 1.0}))
        self.assertIn("Noto Sans Bengali", result.checks["bengali_font"])
        self.assertTrue(result.checks["identifiers_ascii"])


class TestBn007Amounts(unittest.TestCase):
    def test_bn_locale_uses_taka_sign_and_bengali_numerals(self):
        out = format_amount(1500.00, "bn")
        self.assertTrue(out.startswith("৳"))
        self.assertIn("১,৫০০.০০", out)

    def test_lakh_crory_grouping(self):
        out = format_amount(150000.00, "en")
        self.assertIn("1,50,000.00", out)

    def test_en_locale_ascii(self):
        out = format_amount(1500.00, "en")
        self.assertTrue(out.startswith("BDT"))
        self.assertIn("1,500.00", out)

    def test_negative_sign_preserved(self):
        self.assertTrue(format_amount(-50.0, "en").startswith("-"))

    def test_small_amount_no_grouping(self):
        self.assertIn("999.99", format_amount(999.99, "en"))


if __name__ == "__main__":
    unittest.main()
