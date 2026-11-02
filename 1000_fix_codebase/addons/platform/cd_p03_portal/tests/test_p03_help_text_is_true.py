# The workspace's help text must describe what the screen actually offers.
#
# The "Screen Overview" FactBox block is rendered on every model_list, and two
# of its four claims were false:
#
#   "Click any column header to sort"       true  - th carries mlToggleSort
#   "Use Quick Find for real-time search"   true  - mlOnSearchInput
#   "or filter by state pills"              FALSE on 234 of 660 list screens
#                                           (35%) - the pill strip renders
#                                           `t-if="mlStates.length"`, empty
#                                           whenever the screen declares no
#                                           stateField, but the sentence was
#                                           unconditional
#   "Click any row to open the D365         FALSE everywhere - a row click runs
#    in-workspace form"                     mlSelect -> openRecordTab, the
#                                           record PANE. The form is the
#                                           separate "Open Full Form" button.
#
# Help text that tells a user to press something that is not there reads as a
# broken feature. These tests pin the two properties that keep it honest:
# the pill sentence is keyed on the same expression as the pill strip, and the
# row-click sentence matches what mlSelect does.
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


def _overview():
    """The Screen Overview block, comments stripped.

    Stripped because the block carries a comment recording the old wording,
    and asserting over raw text would match the thing being forbidden - a
    mistake this audit has already made twice.
    """
    xml = _strip_comments(_xml())
    i = xml.index('t("Screen Overview")')
    return xml[i : i + 1800]


def test_the_block_still_exists():
    """A guard on the guard: if the heading moved, everything below would
    pass vacuously over the wrong slice."""
    assert 't("Screen Overview")' in _strip_comments(_xml())


def test_the_state_pill_sentence_is_conditional():
    """234 of 660 list screens have no pills. The sentence must not appear
    on them."""
    body = _overview()
    assert "pills above the table" in body, "the pill sentence is gone entirely"
    m = re.search(
        r'<t t-if="([^"]+)"><t t-esc=\'t\("The pills above the table[^)]*\)\'/></t>', body
    )
    assert m, "the pill sentence is not wrapped in a t-if"
    assert "mlStates.length" in m.group(1), (
        "the pill sentence must be keyed on mlStates.length - the SAME "
        "expression the pill strip uses - so the two cannot drift apart; "
        "it is keyed on %r" % m.group(1)
    )


def test_the_pill_strip_uses_the_same_expression():
    """If the strip's condition ever changes, this test fails and the
    sentence has to follow it."""
    xml = _strip_comments(_xml())
    assert 't-if="mlStates.length"' in xml, (
        "the pill strip no longer renders on mlStates.length; the help text "
        "is now keyed on something the UI does not use"
    )


def test_no_claim_that_a_row_click_opens_the_form():
    """A row click runs mlSelect -> openRecordTab (the record pane). The
    D365 form is the Open Full Form button."""
    body = _overview()
    assert "open the D365 in-workspace form" not in body
    assert "Open Full Form" in body, "the help text should name the control that does open the form"


def test_a_row_click_really_does_open_the_record_pane():
    """The behavioural half: the text is only right while mlSelect behaves
    this way."""
    js = JS.read_text(encoding="utf-8")
    i = js.index("    mlSelect(row) {")
    nxt = re.search(r"\n    (?:async )?[a-zA-Z_]\w*\(", js[i + 20 :])
    body = js[i : i + 20 + nxt.start()] if nxt else js[i:]
    assert "openRecordTab" in body, (
        "mlSelect no longer opens the record pane - the Screen Overview "
        "text describes behaviour that has changed"
    )
    assert "mlOpenForm" not in body, "mlSelect now opens the form; the help text should say so"


def test_the_claims_that_remain_are_backed_by_controls():
    """Sorting and Quick Find are promised, so they must exist."""
    xml = _strip_comments(_xml())
    assert "mlToggleSort" in xml, "sorting is promised but no header sorts"
    assert "mlOnSearchInput" in xml, "Quick Find is promised but has no input"
    assert (
        "mlExportCsv" in xml and "mlRefresh" in xml
    ), "Export CSV and Refresh are named in the help text"


def test_the_help_text_uses_javascript_operators():
    """OWL compiles t-expressions as JavaScript; cd_p03_portal has its own
    test for the whole file, and this keeps the block honest locally."""
    body = _overview()
    for m in re.finditer(r't-if="([^"]+)"', body):
        assert not re.search(r"\b(and|or|not)\b", m.group(1)), (
            "Python operator in an OWL expression: %r" % m.group(1)
        )
