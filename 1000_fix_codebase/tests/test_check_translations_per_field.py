"""R01-AUDIT: FF-25 (tooling/fitness/check_translations.py) checks every
user-facing field for a Bengali rendering - per field, not per file."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "fitness" / "check_translations.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_translations_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses resolve annotations via sys.modules
    spec.loader.exec_module(module)
    return module


MODEL = textwrap.dedent(
    """
    from odoo import fields, models


    class FixWidget(models.Model):
        _name = "fix.widget"

        name = fields.Char(string="Widget Name")
        name_bn = fields.Char(string="Widget Name (Bengali)")
        colour = fields.Selection([("r", "Red")], string="Colour")
        size = fields.Integer(string="Size")
        company_id = fields.Many2one("res.company", string="Company")
        internal = fields.Char()


    class FixWidgetExempt(models.Model):
        _name = "fix.feature.flag"

        code = fields.Char(string="Code")


    class PartnerExt(models.Model):
        _inherit = "res.partner"

        extra = fields.Char(string="Extra")
    """
)

PO = textwrap.dedent(
    """
    msgid ""
    msgstr ""

    msgid "Colour"
    msgstr "রং"

    msgid "Size"
    msgstr ""
    """
)


class TestPerFieldBengaliCheck(unittest.TestCase):
    def setUp(self):
        self.ct = _load()
        self.tmp = tempfile.TemporaryDirectory()
        self.addons = Path(self.tmp.name) / "addons"
        module = self.addons / "domain" / "cd_widget"
        (module / "models").mkdir(parents=True)
        (module / "i18n").mkdir()
        (module / "__manifest__.py").write_text("{'name': 'w'}", encoding="utf-8")
        (module / "models" / "widget.py").write_text(MODEL, encoding="utf-8")
        (module / "i18n" / "bn_BD.po").write_text(PO, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_each_labelled_field_is_checked(self):
        checked, models_with_bn, violations = self.ct.check_field_bengali(self.addons)
        # name, name_bn, colour, size - company_id is technical, internal has
        # no label, the exempt model and the pure extension are out of scope
        self.assertEqual(checked, 4)
        self.assertEqual(models_with_bn, 1)
        self.assertEqual([v.field for v in violations], ["size"])
        self.assertEqual(violations[0].model, "fix.widget")
        self.assertEqual(violations[0].label, "Size")

    def test_counterpart_field_satisfies_the_check(self):
        _, _, violations = self.ct.check_field_bengali(self.addons)
        self.assertNotIn("name", [v.field for v in violations])

    def test_missing_po_fails_every_untranslated_label(self):
        (self.addons / "domain" / "cd_widget" / "i18n" / "bn_BD.po").unlink()
        _, _, violations = self.ct.check_field_bengali(self.addons)
        self.assertEqual(sorted(v.field for v in violations), ["colour", "size"])

    def test_fully_translated_module_passes(self):
        po = self.addons / "domain" / "cd_widget" / "i18n" / "bn_BD.po"
        po.write_text(
            PO.replace('msgid "Size"\nmsgstr ""', 'msgid "Size"\nmsgstr "আকার"'), encoding="utf-8"
        )
        _, _, violations = self.ct.check_field_bengali(self.addons)
        self.assertEqual(violations, [])


if __name__ == "__main__":
    unittest.main()
