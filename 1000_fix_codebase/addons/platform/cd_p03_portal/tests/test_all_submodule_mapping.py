# Every area - every Function Register sub-module must describe ITSELF.
#
# test_a03/a04_submodule_mapping.py guarded two areas. The other nine were
# never mapped, so 435 of 598 sub-module panels (A02, A05-A12) opened on
# "No screens are mapped to this sub-module yet" and an empty records table
# - reported from M01 "Omni-Channel Intake (12 channels)". This guard covers
# all eleven areas so a new module cannot ship an empty panel again.
#
# Checks are against the ORM because /p03/model/records DROPS unknown
# columns silently: a typo looks exactly like the emptiness this fixes.
from __future__ import annotations

import importlib
import json
import re
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "static" / "src"

# ['6', 'Kits & Bundles', 4, { ... }]   - the 4th element is the mapping
SUB = re.compile(r"\['(\d+)',\s*'((?:[^'\\]|\\.)*)',\s*(\d+)\s*(?:,\s*(\{.*?\}))?\]", re.S)


def _modules():
    """{code: (text, [(no, title, mapping_src_or_None)])}"""
    out = {}
    for js in sorted(SRC.glob("a*/m*.js")):
        text = js.read_text(encoding="utf-8")
        code = re.search(r"code:\s*'(M\d+)'", text)
        block = re.search(r"freg:\s*\{.*?sub:\s*\[(.*?)\n\s*\]\s*\}", text, re.S)
        if not code or not block:
            continue
        subs = [(s.group(1), s.group(2), s.group(4)) for s in SUB.finditer(block.group(1))]
        out[code.group(1)] = (text, subs)
    return out


def _field(mapping, key):
    m = re.search(r"%s:\s*'([a-z0-9_.]+)'" % key, mapping or "")
    return m.group(1) if m else None


def _list(mapping, key):
    m = re.search(r"%s:\s*\[(.*?)\]" % key, mapping or "", re.S)
    return re.findall(r"'([^']+)'", m.group(1)) if m else []


def _domain_fields(mapping):
    """Field names of a mapping's domain, parsed - not pattern-matched, since
    a value list such as ['ready', 'delivered', 'closed'] looks like a term."""
    m = re.search(r"domain:\s*(\[.*\])\s*\}", mapping or "", re.S)
    if not m:
        return []
    terms = json.loads(m.group(1).replace("'", '"'))
    return [t[0] for t in terms if isinstance(t, list) and len(t) == 3]


def _mapped():
    for code, (_text, subs) in _modules().items():
        for no, title, mp in subs:
            if mp:
                yield code, no, title, mp


def test_the_scan_finds_every_area():
    """A guard on the guard - an empty scan would pass everything below."""
    mods = _modules()
    assert len(mods) == 67, "found %d modules with a Function Register" % len(mods)
    assert sum(len(s) for _t, s in mods.values()) >= 590


def test_every_submodule_in_every_area_is_mapped():
    unmapped = [
        "%s/%s %s" % (code, no, title)
        for code, (_t, subs) in _modules().items()
        for no, title, mp in subs
        if not mp
    ]
    assert not unmapped, "%d unmapped sub-module(s):\n  %s" % (len(unmapped), "\n  ".join(unmapped))


def test_mapped_screens_belong_to_their_own_module():
    """openFreg resolves a mapped screen from the module's nav groups, or -
    for report screens reached through report chips - from its SCREENS. A
    screen in neither is dropped silently and the panel looks empty again."""
    bad = []
    mods = _modules()
    for code, no, title, mp in _mapped():
        text = mods[code][0]
        nav = set(re.findall(r"\{\s*id:\s*'([A-Za-z0-9:_-]+)'", text))
        declared = set(re.findall(r"^[ \t]{2,6}'([A-Za-z0-9:_-]+)':\s*\{", text, re.M))
        screens = _list(mp, "screens")
        if not screens:
            bad.append("%s/%s '%s': no screens" % (code, no, title))
        bad += [
            "%s/%s '%s': screen %s is neither in %s's nav nor its SCREENS"
            % (code, no, title, s, code)
            for s in screens
            if s not in nav and s not in declared
        ]
    assert not bad, "\n  ".join(bad)


def test_mapped_models_and_columns_exist_in_the_orm(odoo_env):
    bad = []
    for code, no, title, mp in _mapped():
        model = _field(mp, "model")
        if not model or model not in odoo_env:
            bad.append("%s/%s '%s': model %s is not in the registry" % (code, no, title, model))
            continue
        fields = odoo_env[model]._fields
        for col in _list(mp, "cols"):
            if col not in fields:
                bad.append("%s/%s '%s': col '%s' not on %s" % (code, no, title, col, model))
        for fname in _domain_fields(mp):
            if fname.split(".")[0] not in fields:
                bad.append(
                    "%s/%s '%s': domain field '%s' not on %s" % (code, no, title, fname, model)
                )
    assert not bad, "\n  ".join(bad)


def test_mapped_models_are_served_by_the_endpoint():
    """A mapping pointing at an unserved model renders an error, not rows."""
    surfaces = importlib.import_module(
        "odoo.addons.cd_p03_portal.controllers.p03_generic_api"
    ).SURFACES
    bad = [
        "%s/%s '%s' -> %s not served by /p03/model/*" % (code, no, title, model)
        for code, no, title, mp in _mapped()
        if (model := _field(mp, "model")) and model not in surfaces
    ]
    assert not bad, "\n  ".join(bad)
