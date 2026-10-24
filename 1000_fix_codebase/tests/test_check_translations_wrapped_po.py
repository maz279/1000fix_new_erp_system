"""FF-24/FF-25 (tooling/fitness/check_translations.py) read gettext-wrapped
entries: a long msgid/msgstr split over continuation lines - the form Odoo's
own `odoo-bin i18n export` writes - counts as the joined string."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "fitness" / "check_translations.py"

LONG = (
    "Affected Body Part (e.g. Eye, Hand, Respiratory) recorded on the statutory accident register"
)
LONG_BN = "আক্রান্ত শরীরের অংশ (যেমন চোখ, হাত, শ্বাসতন্ত্র) সংবিধিবদ্ধ দুর্ঘটনা রেজিস্টারে লিপিবদ্ধ"

WRAPPED_PO = textwrap.dedent(
    """\
    msgid ""
    msgstr ""
    "Language: bn_BD\\n"
    "Plural-Forms: nplurals=2; plural=(n != 1);\\n"

    #. module: cd_widget
    #: model:ir.model.fields,field_description:cd_widget.field_fix_widget__body_part
    msgid ""
    "Affected Body Part (e.g. Eye, Hand, Respiratory) recorded on the "
    "statutory accident register"
    msgstr ""
    "আক্রান্ত শরীরের অংশ (যেমন চোখ, হাত, শ্বাসতন্ত্র) সংবিধিবদ্ধ দুর্ঘটনা "
    "রেজিস্টারে লিপিবদ্ধ"

    #. module: cd_widget
    #: model:ir.model.fields,field_description:cd_widget.field_fix_widget__quote
    msgid "Say \\"hello\\""
    msgstr "\\"হ্যালো\\" বলুন"

    #. module: cd_widget
    #, fuzzy
    msgid "Size"
    msgstr "আকার"

    #~ msgid "Retired Label"
    #~ msgstr "পুরনো"
    """
)

WRAPPED_POT = textwrap.dedent(
    """\
    msgid ""
    msgstr ""

    #. module: cd_widget
    msgid ""
    "Affected Body Part (e.g. Eye, Hand, Respiratory) recorded on the "
    "statutory accident register"
    msgstr ""

    #. module: cd_widget
    msgid "Say \\"hello\\""
    msgstr ""
    """
)

MODEL = textwrap.dedent(
    f"""
    from odoo import fields, models


    class FixWidget(models.Model):
        _name = "fix.widget"

        body_part = fields.Char(string="{LONG}")
        quote = fields.Char(string='Say "hello"')
    """
)


def _load():
    spec = importlib.util.spec_from_file_location("check_translations_wrapped_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TestWrappedPoEntries(unittest.TestCase):
    def setUp(self):
        self.ct = _load()
        self.tmp = tempfile.TemporaryDirectory()
        self.addons = Path(self.tmp.name) / "addons"
        self.module = self.addons / "domain" / "cd_widget"
        (self.module / "models").mkdir(parents=True)
        (self.module / "i18n").mkdir()
        (self.module / "__manifest__.py").write_text("{'name': 'w'}", encoding="utf-8")
        (self.module / "models" / "widget.py").write_text(MODEL, encoding="utf-8")
        (self.module / "i18n" / "bn_BD.po").write_text(WRAPPED_PO, encoding="utf-8")
        (self.module / "i18n" / "cd_widget.pot").write_text(WRAPPED_POT, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_continuation_lines_are_joined(self):
        pairs = self.ct.parse_po_msgstr(WRAPPED_PO)
        self.assertEqual(pairs[LONG], LONG_BN)

    def test_escapes_are_decoded(self):
        pairs = self.ct.parse_po_msgstr(WRAPPED_PO)
        self.assertEqual(pairs['Say "hello"'], '"হ্যালো" বলুন')

    def test_fuzzy_counts_as_untranslated_and_obsolete_is_ignored(self):
        pairs = self.ct.parse_po_msgstr(WRAPPED_PO)
        self.assertEqual(pairs["Size"], "")
        self.assertNotIn("Retired Label", pairs)

    def test_template_msgids_are_joined(self):
        self.assertEqual(self.ct.parse_pot_msgids(WRAPPED_POT), ["", LONG, 'Say "hello"'])

    def test_wrapped_translation_satisfies_the_field_check(self):
        checked, _, violations = self.ct.check_field_bengali(self.addons)
        self.assertEqual(checked, 2)
        self.assertEqual(violations, [])

    def test_wrapped_translation_satisfies_ff24(self):
        original = self.ct.ADDONS
        self.ct.ADDONS = self.addons
        try:
            self.assertEqual(self.ct.check_po_completeness(), [])
        finally:
            self.ct.ADDONS = original

    def test_wrapped_label_with_empty_translation_still_fails(self):
        continuation = (
            '"আক্রান্ত শরীরের অংশ (যেমন চোখ, হাত, শ্বাসতন্ত্র) সংবিধিবদ্ধ দুর্ঘটনা "\n"রেজিস্টারে লিপিবদ্ধ"\n'
        )
        self.assertIn(continuation, WRAPPED_PO)
        po = self.module / "i18n" / "bn_BD.po"
        po.write_text(WRAPPED_PO.replace(continuation, ""), encoding="utf-8")  # msgstr "" only
        _, _, violations = self.ct.check_field_bengali(self.addons)
        self.assertEqual([v.field for v in violations], ["body_part"])
        self.ct.ADDONS, original = self.addons, self.ct.ADDONS
        try:
            self.assertEqual(len(self.ct.check_po_completeness()), 1)
        finally:
            self.ct.ADDONS = original


if __name__ == "__main__":
    unittest.main()
