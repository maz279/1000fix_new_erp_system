"""A12 workflow audit R4: every A12 surface declares a write whitelist.

Before this suite, no A12 surface declared what /p03/model/write may set,
so the form endpoint wrote any non-readonly field it was sent. The
per-module WRITABLE dicts in controllers/a12/mNN.py whitelist exactly the
fields a user may legitimately type; this test refuses to let a surface
ship without one (fail loudly - A09's silent-drop lesson).
"""

from __future__ import annotations

from ..controllers import a12


def test_every_a12_surface_declares_a_writable_whitelist():
    missing = sorted(m for m, conf in a12.SURFACES.items() if "writable" not in conf)
    assert not missing, "A12 surfaces without a writable whitelist: %s" % ", ".join(missing)


def test_state_and_approval_fields_are_never_writable():
    locked = ("state", "decision", "resolution", "in_force", "ruled_by", "ruled_on")
    offenders = []
    for model, conf in a12.SURFACES.items():
        writable = conf.get("writable")
        if not writable:
            continue
        hits = sorted(set(locked) & set(writable))
        if hits:
            offenders.append("%s: %s" % (model, ", ".join(hits)))
    assert not offenders, "workflow fields left writable: %s" % "; ".join(offenders)
