"""audit-repo-formats PO validation reads gettext-wrapped entries whole: a
wrapped msgstr is not "empty", a wrapped msgid with an empty msgstr is, and a
plural entry's msgstr[0] keeps the file balanced."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "fitness" / "audit-repo-formats.py"

HEADER = 'msgid ""\nmsgstr ""\n"Language: bn_BD\\n"\n\n'

WRAPPED_OK = HEADER + textwrap.dedent(
    """\
    #. module: cd_widget
    msgid "Short label"
    msgstr ""
    "একটি দীর্ঘ "
    "বাংলা অনুবাদ"

    #. module: cd_widget
    msgid ""
    "A long label wrapped over "
    "two continuation lines"
    msgstr "দুই লাইনে ভাঙা একটি দীর্ঘ লেবেল"

    #. module: cd_widget
    msgid "One item"
    msgid_plural "%d items"
    msgstr[0] "একটি আইটেম"
    msgstr[1] "%d টি আইটেম"

    #~ msgid "Retired"
    #~ msgstr ""
    """
)

WRAPPED_EMPTY = HEADER + textwrap.dedent(
    """\
    #. module: cd_widget
    msgid ""
    "A long label wrapped over "
    "two continuation lines"
    msgstr ""
    """
)


def _load():
    spec = importlib.util.spec_from_file_location("audit_repo_formats_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TestPoValidation(unittest.TestCase):
    def setUp(self):
        self.audit = _load()
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.i18n = self.root / "addons" / "cd_widget" / "i18n"
        self.i18n.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def _issues(self, text: str) -> list[str]:
        (self.i18n / "bn_BD.po").write_text(text, encoding="utf-8")
        return self.audit.po_issues(self.root / "addons", rel_to=self.root)

    def test_wrapped_and_plural_entries_are_clean(self):
        self.assertEqual(self._issues(WRAPPED_OK), [])

    def test_wrapped_msgid_with_empty_msgstr_is_reported(self):
        self.assertEqual(
            self._issues(WRAPPED_EMPTY),
            [
                "PO empty msgstr: addons/cd_widget/i18n/bn_BD.po: 'A long label wrapped over two continuati'"
            ],
        )

    def test_missing_msgstr_is_unbalanced(self):
        issues = self._issues(HEADER + 'msgid "Orphan"\n\nmsgid "Pair"\nmsgstr "জোড়া"\n')
        self.assertIn("PO unbalanced: addons/cd_widget/i18n/bn_BD.po: 3 msgid vs 2 msgstr", issues)

    def test_repository_po_files_are_clean(self):
        self.assertEqual(self.audit.po_issues(REPO_ROOT / "addons", rel_to=REPO_ROOT), [])


if __name__ == "__main__":
    unittest.main()
