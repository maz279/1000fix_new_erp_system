# The workspace FactBox must not carry static filler (user directive
# 2026-11-07): the old "Screen Overview" block restated what the command bar
# already offered and did nothing. It was removed; these tests pin that it
# STAYS removed, and keep the behavioural half of the original audit — the
# claims its wording leaned on must still be true of the controls that
# remain.
from __future__ import annotations

import re
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "static" / "src"
XML = SRC / "p03_workspace.xml"
JS = SRC / "p03_workspace.js"


def _xml():
    return XML.read_text(encoding="utf-8")


def _strip_comments(text):
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def test_the_static_overview_block_stays_removed():
    """Dead help text must not come back. Comments stripped so a comment
    recording the old wording cannot mask a regression."""
    xml = _strip_comments(_xml())
    assert 't("Screen Overview")' not in xml, (
        "the static Screen Overview block returned - it described controls "
        "the command bar already names and did nothing (user directive "
        "2026-11-07)"
    )
    assert "Live records from Odoo." not in xml, "the old filler copy returned"
    assert "Click a column header to sort" not in xml, "the old filler copy returned"


def test_the_pill_strip_still_renders_on_ml_states():
    """The state pill strip itself stays, keyed on mlStates.length — screens
    without a stateField simply render no strip."""
    xml = _strip_comments(_xml())
    assert 't-if="mlStates.length"' in xml


def test_a_row_click_really_does_open_the_record_pane():
    """A row click runs mlSelect -> openRecordTab (the record pane); the D365
    form opens via the separate Open Full Form button."""
    js = JS.read_text(encoding="utf-8")
    i = js.index("    mlSelect(row) {")
    nxt = re.search(r"\n    (?:async )?[a-zA-Z_]\w*\(", js[i + 20 :])
    body = js[i : i + 20 + nxt.start()] if nxt else js[i:]
    assert "openRecordTab" in body, (
        "mlSelect no longer opens the record pane - update the FactBox "
        "wording contract if the interaction changed"
    )


def test_the_controls_the_factbox_named_still_exist():
    """Sorting and Quick Find stay backed by real handlers — the FactBox no
    longer promises them, but removing the text must not coexist with
    removing the features."""
    xml = _strip_comments(_xml())
    assert "mlToggleSort" in xml, "column-header sorting disappeared"
    assert "mlOnSearchInput" in xml, "Quick Find disappeared"
    assert (
        "mlExportCsv" in xml and "mlRefresh" in xml
    ), "Export CSV and Refresh must stay on the command bar"
