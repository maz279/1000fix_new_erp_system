# M32 Conversational AI: capture audit pass 3 (19 Nov 2026).
#
# Pass 2 left two capture-shaped gaps open:
#   * 7 Handoff Decision: the emotional triggers were tunable but nothing could
#     record what a customer says that means distress, abuse, an explicit
#     request or frustration (FR-CAI-034/036, BRU-CAI-06/07), so they were
#     never raised.
#   * 9 Analytics: an abandoned session never reached the unresolved queue
#     (AUT-CAI-08).
from __future__ import annotations

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location(
    "_m32_pass1_p3", HERE / "test_m32_capture_buttons.py"
)
_p1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_p1)

m32 = _p1.m32
CC = _p1.CC
MODEL = "fix.assistant.signal.phrase"


def test_page_7_captures_signal_phrases(m32):
    sub = _p1._sub(m32, "7")
    chips = {f["id"] for f in sub["forms"] if f["opens"]}
    assert "M32-form-signal-phrase" in chips
    assert "M32-signal-phrases" in sub["screens"]
    form = m32["screens"]["M32-form-signal-phrase"]
    assert form["model"] == MODEL
    names = {f["name"]: f for f in form["fields"]}
    for name in ("signal", "phrase", "language"):
        assert names[name]["required"], name
    assert "normalised" not in names, "the normalised phrase is computed, never typed"
    assert m32["by_screen"]["M32-signal-phrases"] == "M32-form-signal-phrase"


def test_phrases_are_served_and_written_only_by_supervisors():
    assert MODEL in _p1._surfaces()
    writable = _p1._writable()[MODEL]
    assert "normalised" not in writable and "create_uid" not in writable
    rows = [
        r.split(",")
        for r in (CC / "security" / "ir.model.access.csv")
        .read_text(encoding="utf-8")
        .splitlines()[1:]
        if r.strip()
    ]
    mine = [r for r in rows if r[2] == "model_fix_assistant_signal_phrase"]
    assert all(r[4:8] == ["1", "0", "0", "0"] for r in mine if r[3] == "base.group_user")
    assert any(r[3] == "cd_contact_centre.group_cc_supervisor" and r[5] == "1" for r in mine)
    rules = (CC / "security" / "fix_isolation_rules.xml").read_text(encoding="utf-8")
    assert 'ref="model_fix_assistant_signal_phrase"' in rules


def test_the_bot_checks_signals_before_it_classifies_and_logs_abandonment():
    src = (CC / "models" / "fix_assistant_signals.py").read_text(encoding="utf-8")
    assert "def intake_message" in src and "def _mark_abandoned" in src
    init = (CC / "models" / "__init__.py").read_text(encoding="utf-8")
    assert init.index("fix_assistant_capture2") < init.index("fix_assistant_signals")
    manifest = (CC / "__manifest__.py").read_text(encoding="utf-8")
    assert "data/fix_assistant_signal_data.xml" in manifest
