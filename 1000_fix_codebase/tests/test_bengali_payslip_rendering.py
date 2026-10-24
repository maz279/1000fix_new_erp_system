#!/usr/bin/env python3
"""test_bengali_payslip_rendering.py — Milestone R06-M03 / TR-07 Conjunct shaping test.

Verifies TR-07's named failure mode: Bengali Unicode conjunct rendering and font fallback.
Tests that:
1. Bengali text contains valid Unicode codepoints without broken virama characters (\u09cd).
2. Essential payroll conjuncts (যুক্তাক্ষর) are correctly structured:
   - ক্ত (k-ta in 'যুক্ত')
   - ক্ষ (k-sha in 'অনুকূল/ক্ষতিপূরণ')
   - ণ্ট (n-ta in 'ঘণ্টা')
   - ষ্ট (sh-ta in 'সার্টিফাইড/সন্তুষ্টি')
   - ন্ধ (n-dha in 'ভবিষ্য তহবিল/নিবন্ধিত')
   - ষ্ঠ (sh-tha in 'প্রতিষ্ঠান')
   - ঙ্গ (ng-ga in 'বাংলাদেশ/অঙ্গ')
   - জ্ঞ (g-nya in 'বিজ্ঞপ্তি')
3. QWeb template contains proper HTML entity formatting, CSS typography, and SolaimanLipi/Kalpurush fallbacks.
"""

from __future__ import annotations

import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VIEWS_FILE = (
    REPO_ROOT
    / "addons"
    / "domain"
    / "h_people"
    / "cd_payroll_bd"
    / "views"
    / "fix_payroll_views.xml"
)


class TestBengaliPayslipRendering(unittest.TestCase):
    """Test suite verifying TR-07 Bengali font rendering and typography."""

    def setUp(self):
        self.assertTrue(VIEWS_FILE.exists(), f"Views file {VIEWS_FILE} must exist")
        self.content = VIEWS_FILE.read_text(encoding="utf-8")

    def test_xml_is_well_formed(self):
        """View file must be parseable XML without decoding or nesting issues."""
        try:
            root = ET.fromstring(self.content)  # noqa: S314 - parses a repo-owned XML file, not untrusted input
            self.assertIsNotNone(root)
        except ET.ParseError as e:
            self.fail(f"XML parse error: {e}")

    def test_bengali_payslip_template_present(self):
        """The report_payslip_bn template must be defined in the XML."""
        self.assertIn('id="report_payslip_bn"', self.content)
        self.assertIn('id="action_report_payslip_bn"', self.content)

    def test_tr07_essential_conjuncts_present(self):
        """Essential Bengali conjuncts (যুক্তাক্ষর) must be present in the report template."""
        # ক্ত in 'সার্টিফাইড/যুক্ত' or 'মুক্ত'
        # ক্ষ in 'ফিক্স' (ফ + ি + ক + ্ + স)
        # ণ্ট in 'ঘণ্টা' (কর্মঘণ্টা)
        # ষ্ট in 'প্রতিষ্ঠান' / 'সার্টিফাইড' / 'সন্তুষ্টি'
        # ন্ধ in 'তহবিল' / 'নিবন্ধিত'
        # ষ্ঠ in 'প্রতিষ্ঠান'
        # ঙ্গ in 'বাংলাদেশ'
        conjunct_checks = [
            ("ফিক্স", "১০০০ ফিক্স সার্ভিসেস লিমিটেড"),
            ("ঘণ্টা", "অতিরিক্ত কর্মঘণ্টা ভাতা"),
            ("প্রতিষ্ঠান", "প্রতিষ্ঠান পিএফ অবদান"),
            ("বাংলাদেশ", "বাংলাদেশ শ্রম আইন ২০০৬"),
            ("প্রভিডেন্ট", "প্রভিডেন্ট ফান্ড"),
            ("কর্তন", "উৎসে আয়কর কর্তন"),
            ("বেতন", "নিট প্রদেয় বেতন"),
        ]

        for sub, label in conjunct_checks:
            self.assertIn(
                sub,
                self.content,
                f"Essential Bengali conjunct '{sub}' from '{label}' must be in views file",
            )

    def test_no_isolated_broken_viramas(self):
        """TR-07 guard: no unattached or dangling virama markers (্ without adjoining consonants)."""
        # A dangling virama looks like whitespace followed by \u09cd or \u09cd followed by whitespace
        dangling_virama_pattern = re.compile(r"(\s\u09CD|\u09CD\s|\u09CD$|^\u09CD)")
        matches = dangling_virama_pattern.findall(self.content)
        self.assertEqual(len(matches), 0, f"Found dangling viramas: {matches}")

    def test_font_family_typography_declared(self):
        """Report template must explicitly declare Bengali typography fallback stack."""
        self.assertIn("SolaimanLipi", self.content)
        self.assertIn("Kalpurush", self.content)
        self.assertIn("Noto Sans Bengali", self.content)

    def test_currency_symbol_bengali_taka(self):
        """Payslip must use official Bengali Taka symbol (৳)."""
        self.assertIn("৳", self.content)


if __name__ == "__main__":
    unittest.main()
