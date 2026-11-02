# A03 - every sub-module panel must describe ITSELF, with real screens and
# real columns.
#
# Raised by a user opening M33 sub-module 6, "Kits & Bundles", and finding it
# empty. Two causes, both confirmed in the browser:
#
#   1. `openFreg` listed `mod.groups.flatMap(g => g.screens).slice(0, 6)` -
#      which does not depend on fnIndex. All 13 of M33's sub-modules showed
#      the SAME six screens (Brand, Refurb Grade, Unified Item Master, Item
#      Record, Typed Taxonomy, Product Hierarchy), none of them about kits.
#
#   2. The records table rendered `generateGridData()`, whose five return
#      paths all end `rows: []`. It chose column headers by keyword and never
#      carried data, in any module. It was headed "Sample & Live Database
#      Records" with a chip reading "records wire with each porting phase".
#
# A sub-module now declares { model, cols, screens, reports, forms } and the
# panel loads that model's real rows. This file checks those declarations
# against the ORM, because /p03/model/records DROPS unknown columns silently -
# a typo there does not raise, it just makes a column disappear, which looks
# exactly like the emptiness this was meant to fix. (I introduced precisely
# that bug while writing the mapping: `cols: ['name', ...]` on
# fix.catalogue.item, which had no `name` field at the time.)
from __future__ import annotations

import re
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "static" / "src" / "a03"

# ['6', 'Kits & Bundles', 4, { ... }]   - the 4th element is optional
SUB = re.compile(r"\['(\d+)',\s*'((?:[^'\\]|\\.)*)',\s*(\d+)\s*(?:,\s*(\{.*?\}))?\]", re.S)


def _subs():
    """[(module, no, title, count, mapping_src_or_None)]"""
    out = []
    for js in sorted(SRC.glob("m*.js")):
        text = js.read_text(encoding="utf-8")
        m = re.search(r"freg:\s*\{(.*?)\n\s*\};", text, re.S)
        chunk = m.group(1) if m else text
        for s in SUB.finditer(chunk):
            out.append((js.stem.upper(), s.group(1), s.group(2), int(s.group(3)), s.group(4)))
    return out


def _field(mapping, key):
    m = re.search(r"%s:\s*'([a-z0-9_.]+)'" % key, mapping or "")
    return m.group(1) if m else None


def _list(mapping, key):
    m = re.search(r"%s:\s*\[(.*?)\]" % key, mapping or "", re.S)
    return re.findall(r"'([^']+)'", m.group(1)) if m else []


def _declared_screens():
    ids = set()
    for js in SRC.glob("m*.js"):
        ids |= set(
            re.findall(
                r"^[ \t]{2,6}'([A-Za-z0-9:_-]+)':\s*\{", js.read_text(encoding="utf-8"), re.M
            )
        )
    return ids


def test_the_scan_finds_submodules():
    """A guard on the guard - an empty list would pass everything below."""
    subs = _subs()
    assert len(subs) >= 60, "only %d A03 sub-modules found - the scan broke" % len(subs)


def test_every_a03_submodule_is_mapped():
    """All 64, every module.

    Without a mapping the panel borrows the MODULE's first six screens -
    identical for every sub-module, so it describes none of them. That is
    the defect that made M37 "Kits & Bundles" look empty in A04.
    """
    unmapped = ["%s/%s %s" % (mod, n, t) for mod, n, t, _c, mp in _subs() if not mp]
    assert not unmapped, (
        "%d A03 sub-module(s) with no mapping:" % len(unmapped) + "\n  " + "\n  ".join(unmapped)
    )


def test_mapped_models_exist_in_the_orm(odoo_env):
    bad = [
        "%s/%s '%s' -> model %s is not in the registry" % (mod, no, title, model)
        for mod, no, title, _c, mp in _subs()
        if mp and (model := _field(mp, "model")) and model not in odoo_env
    ]
    assert not bad, "\n  ".join(bad)


def test_mapped_columns_exist_on_their_model(odoo_env):
    """The silent-drop bug: /p03/model/records filters unknown columns out."""
    bad = []
    for mod, no, title, _c, mp in _subs():
        if not mp:
            continue
        model = _field(mp, "model")
        if not model or model not in odoo_env:
            continue
        fields = odoo_env[model]._fields
        for col in _list(mp, "cols"):
            if col not in fields:
                bad.append("%s/%s '%s': col '%s' not on %s" % (mod, no, title, col, model))
    assert not bad, "\n  ".join(bad)


def test_mapped_models_are_served_by_the_endpoint():
    """A mapping pointing at an unserved model renders an error, not rows."""
    import importlib

    surfaces = importlib.import_module(
        "odoo.addons.cd_p03_portal.controllers.p03_generic_api"
    ).SURFACES
    bad = [
        "%s/%s '%s' -> %s not served by /p03/model/*" % (mod, no, title, model)
        for mod, no, title, _c, mp in _subs()
        if mp and (model := _field(mp, "model")) and model not in surfaces
    ]
    assert not bad, "\n  ".join(bad)


def test_mapped_screens_are_declared():
    declared = _declared_screens()
    bad = []
    for mod, no, title, _c, mp in _subs():
        if not mp:
            continue
        for sid in _list(mp, "screens"):
            if sid not in declared:
                bad.append("%s/%s '%s' -> screen %s is not declared" % (mod, no, title, sid))
    assert not bad, "\n  ".join(bad)


def test_a_mapped_submodule_names_at_least_one_screen():
    """A mapping with no screens leaves the panel as empty as before."""
    bad = [
        "%s/%s '%s' maps nothing" % (mod, no, title)
        for mod, no, title, _c, mp in _subs()
        if mp and not _list(mp, "screens")
    ]
    assert not bad, "\n  ".join(bad)


def _strip_xml_comments(text):
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def _strip_js_comments(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"^\s*//.*$", "", text, flags=re.M)


def test_the_panel_no_longer_advertises_sample_data():
    """'Sample & Live Database Records' over a table that could not have
    rows, and a chip reading 'records wire with each porting phase'.

    Comments are stripped first. The first version of this test failed on the
    comment that RECORDS what was removed - the same mistake as grepping for
    a string that also lives in a docstring, which this audit had already
    hit once and written down.
    """
    xml = _strip_xml_comments((SRC.parents[0] / "p03_workspace.xml").read_text(encoding="utf-8"))
    assert "Sample &amp; Live Database Records" not in xml
    assert "records wire with each porting phase" not in xml
    assert "Live Database Records" in xml


def test_the_panel_loads_records_rather_than_generating_them():
    """Bounded at the NEXT method, not by a fixed character window - an
    unbounded window spilled into the following method and matched the
    comment there."""
    js = _strip_js_comments((SRC.parents[0] / "p03_workspace.js").read_text(encoding="utf-8"))
    i = js.index("openFreg(mid, fnIndex)")
    nxt = re.search(r"\n    (?:async )?[a-zA-Z_]\w*\(", js[i + 30 :])
    body = js[i : i + 30 + nxt.start()] if nxt else js[i:]
    assert "generateGridData" not in body, (
        "openFreg still builds its grid from generateGridData, whose every "
        "return path ends rows: []"
    )
    assert "loadFregRecords" in body
    assert "/p03/model/records" in js


@pytest.mark.parametrize(
    "mod,no,model,screen",
    [
        ("M10", "3", "fix.loyalty.ledger", "M10-ledger"),
        ("M27", "4", "fix.cc.queue", "M27-queues"),
        ("M32", "1", "fix.assistant.intent", "M32-intents"),
        ("M33", "10", "fix.segment", "M33-segments"),
        ("M34", "5", "fix.complaint", "M34-complaints"),
        ("M35", "3", "fix.campaign.journey", "M35-journeys"),
    ],
)
def test_named_a03_submodules_point_at_their_own_surface(mod, no, model, screen):
    """One per module: each panel must describe ITSELF, not the module."""
    mp = next((m for md, n, _t, _c, m in _subs() if md == mod and n == no), None)
    assert mp, "%s sub-module %s has no mapping" % (mod, no)
    assert _field(mp, "model") == model
    assert screen in _list(mp, "screens")
