"""TR-07 / DoD-08: tooling/scripts/extract-translations.py writes i18n files
that Odoo 19's own reader (odoo.tools.translate.PoFileReader) loads.

Before 2026-10-22 the extractor (and the one-shot PO generators) wrote entries
with no `#. module:` comment and no `#:` references; PoFileReader raised
AttributeError on the first entry and the whole bn_BD load aborted.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "scripts" / "extract-translations.py"
sys.path.insert(0, str(REPO_ROOT / "vendor" / "odoo"))

try:
    from odoo.tools.translate import PoFileReader
except ImportError as exc:  # pragma: no cover - Odoo is vendored; deps come from the dev env
    PoFileReader = None
    _IMPORT_ERROR = exc


def _load_extractor():
    spec = importlib.util.spec_from_file_location("extract_translations_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODEL = textwrap.dedent(
    """
    from odoo import _, fields, models

    STATES = [("draft", "Draft"), ("done", "Done")]


    class FixWidget(models.Model):
        _name = "fix.widget"
        _description = "Widget"

        name = fields.Char(string="Widget Name")
        state = fields.Selection(STATES, string="Status")
        partner_id = fields.Many2one("res.partner", "Customer")
        quantity = fields.Integer()

        def action_done(self):
            raise ValueError(_("Widget already done"))
    """
)

VIEWS = textwrap.dedent(
    """\
    <?xml version="1.0" encoding="utf-8"?>
    <odoo>
        <record id="view_fix_widget_form" model="ir.ui.view">
            <field name="name">fix.widget.form</field>
            <field name="model">fix.widget</field>
            <field name="arch" type="xml">
                <form string="Widget">
                    <button name="action_done" string="Mark Done" type="object"/>
                    <field name="name"/>
                </form>
            </field>
        </record>
        <record id="action_fix_widget" model="ir.actions.act_window">
            <field name="name">Widgets</field>
            <field name="res_model">fix.widget</field>
        </record>
        <menuitem id="menu_fix_widget" name="Widgets" action="action_fix_widget"/>
    </odoo>
    """
)

# the pre-2026-10-22 form: plain msgid/msgstr pairs, no comments, no references
LEGACY_PO = textwrap.dedent(
    """\
    # Bengali translations for cd_widget.
    msgid ""
    msgstr ""
    "Language: bn_BD\\n"
    "Content-Type: text/plain; charset=UTF-8\\n"

    msgid "Widget Name"
    msgstr "উইজেটের নাম"

    msgid "Status"
    msgstr "অবস্থা"

    msgid "Draft"
    msgstr "খসড়া"

    msgid "Widgets"
    msgstr "উইজেটসমূহ"

    msgid "Customer"
    msgstr "গ্রাহক"

    msgid "Quantity"
    msgstr "পরিমাণ"
    """
)


@unittest.skipIf(PoFileReader is None, "odoo.tools.translate not importable")
class TestExtractorWritesOdooLoadablePo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.module = Path(self.tmp.name) / "addons" / "domain" / "cd_widget"
        (self.module / "models").mkdir(parents=True)
        (self.module / "views").mkdir()
        (self.module / "i18n").mkdir()
        (self.module / "__manifest__.py").write_text("{'name': 'w'}", encoding="utf-8")
        (self.module / "models" / "widget.py").write_text(MODEL, encoding="utf-8")
        (self.module / "views" / "widget_views.xml").write_text(VIEWS, encoding="utf-8")
        self.po = self.module / "i18n" / "bn_BD.po"
        self.pot = self.module / "i18n" / "cd_widget.pot"
        self.po.write_text(LEGACY_PO, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def _extract(self) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(self.module)],
            capture_output=True,
            text=True,
            check=False,
        )

    def _odoo_rows(self) -> list[dict]:
        # a file object named *.po: PoFileReader merges the sibling <module>.pot
        with self.po.open("rb") as fh:
            return list(PoFileReader(fh))

    def test_legacy_form_is_rejected_by_odoo(self):
        with self.assertRaises(AttributeError):
            self._odoo_rows()

    def test_extracted_files_load_with_field_description_rows(self):
        proc = self._extract()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertTrue(self.pot.is_file())
        rows = self._odoo_rows()
        fields = {
            r["imd_name"]: r["value"]
            for r in rows
            if r["type"] == "model" and r["name"] == "ir.model.fields,field_description"
        }
        self.assertEqual(fields["field_fix_widget__name"], "উইজেটের নাম")
        self.assertEqual(fields["field_fix_widget__state"], "অবস্থা")
        self.assertEqual(fields["field_fix_widget__partner_id"], "গ্রাহক")  # positional string
        self.assertEqual(fields["field_fix_widget__quantity"], "পরিমাণ")  # Odoo's default label
        self.assertTrue(all(r["module"] == "cd_widget" for r in rows))
        refs = {(r["name"], r["imd_name"], r["value"]) for r in rows if r["type"] == "model"}
        self.assertIn(
            ("ir.model.fields.selection,name", "selection__fix_widget__state__draft", "খসড়া"), refs
        )
        self.assertIn(("ir.ui.menu,name", "menu_fix_widget", "উইজেটসমূহ"), refs)
        self.assertIn(("ir.actions.act_window,name", "action_fix_widget", "উইজেটসমূহ"), refs)

    def test_template_carries_new_strings_but_po_gains_no_empty_msgstr(self):
        self._extract()
        pot = self.pot.read_text(encoding="utf-8")
        for msgid in ("Mark Done", "Done", "Widget already done"):  # untranslated template strings
            self.assertIn(f'msgid "{msgid}"', pot)
        po = self.po.read_text(encoding="utf-8")
        self.assertEqual(po.count('msgstr ""\n'), 1)  # the header only
        self.assertNotIn('msgid "Mark Done"', po)
        self.assertIn("#: code:addons/cd_widget/models/widget.py:0", pot)
        self.assertIn("#: model_terms:ir.ui.view,arch_db:cd_widget.view_fix_widget_form", pot)

    def test_rerun_is_idempotent(self):
        self._extract()
        first = (self.pot.read_text(encoding="utf-8"), self.po.read_text(encoding="utf-8"))
        self._extract()
        self.assertEqual(
            first, (self.pot.read_text(encoding="utf-8"), self.po.read_text(encoding="utf-8"))
        )

    def test_wrapped_and_fuzzy_entries_are_read(self):
        ext = _load_extractor()
        header, translated, fuzzy = ext.read_po(
            'msgid ""\nmsgstr ""\n"Language: bn_BD\\n"\n\n'
            '#, fuzzy\nmsgid "Status"\nmsgstr "অবস্থা"\n\n'
            'msgid ""\n"Widget "\n"Name"\nmsgstr ""\n"উইজেটের "\n"নাম"\n'
        )
        self.assertTrue(header.startswith('msgid ""'))
        self.assertEqual(translated["Widget Name"], "উইজেটের নাম")
        self.assertEqual(fuzzy, {"Status"})


if __name__ == "__main__":
    unittest.main()
