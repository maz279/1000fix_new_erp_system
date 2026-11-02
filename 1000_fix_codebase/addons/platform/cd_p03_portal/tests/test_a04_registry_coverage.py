# A04 - every model a workspace screen binds must be SERVED by the registry
# the generic endpoints consult.
#
# A08 has had this guard for a while (test_a08_m19_registry.py:
# `assert model in m19.SURFACES`). A04 never did, and that is precisely how
# `fix.contract.template` came to be bound by two M37 screens the backend
# would not serve: the drift was invisible to the entire test suite and was
# found only by driving a browser over all 245 surfaces, which is an expensive
# and very late way to learn it.
#
# Note on deployment, learned the hard way (A04 audit, 2026-11-01): passing
# here means the SOURCE TREE agrees. Odoo imports controller modules once, at
# process start, so a running server keeps serving whatever SURFACES looked
# like when it booted. A green run here plus a stale process is exactly the
# state that produced the two unservable surfaces - the remedy is a restart,
# and no assertion can substitute for one.
from __future__ import annotations

import importlib
import re
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "static" / "src" / "a04"

# every screen declaration:  'M37-form-ctpl': { ... }
SCREEN = re.compile(r"^[ \t]{2,6}'([A-Za-z0-9:_-]+)':\s*\{", re.M)
# the model a screen binds:  model: 'fix.contract.template'
MODEL = re.compile(r"model:\s*'([a-z0-9_.]+)'")
# the kinds that go through /p03/model/* and therefore need a surface
SERVED_KINDS = ("model_list", "model_form", "model_report")


def _modules():
    assert SRC.is_dir(), SRC
    return sorted(SRC.glob("m*.js"))


def _screens(js_path):
    """[(screen_id, body)] for one module fragment, bodies bounded correctly.

    Bounded at the NEXT screen declaration. An earlier scan of this same file
    shape used a fixed character window, spilled into the following screen and
    hid five defects - never use a fixed window here.
    """
    text = js_path.read_text(encoding="utf-8")
    starts = [(m.start(), m.group(1)) for m in SCREEN.finditer(text)]
    out = []
    for i, (pos, sid) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else len(text)
        out.append((sid, text[pos:end]))
    return out


def _a04_surfaces():
    """The MERGED A04 registry - what the endpoints actually consult.

    NOT the per-module dict. controllers/a04/__init__.py merges all nine
    fragments into one, so a screen declared in m09.js may legitimately be
    served by a surface declared in m08.py. The first version of this test
    asserted the per-module pairing and raised 20 false alarms against screens
    the live system serves perfectly well. Assert against the registry the
    runtime uses, never against a naming convention.

    That __init__ also raises when two modules declare the same model, so a
    duplicate surface cannot reach this point at all.
    """
    return importlib.import_module("odoo.addons.cd_p03_portal.controllers.a04").SURFACES


def _global_surfaces():
    """The registry /p03/model/* resolves against, across every area."""
    return importlib.import_module("odoo.addons.cd_p03_portal.controllers.p03_generic_api").SURFACES


def _bound_models():
    """[(js_name, screen_id, kind, model)] for every A04 screen that binds one."""
    rows = []
    for js in _modules():
        for sid, body in _screens(js):
            kind = next((k for k in SERVED_KINDS if "kind: '%s'" % k in body), None)
            if not kind:
                continue
            m = MODEL.search(body)
            if m:
                rows.append((js.name, sid, kind, m.group(1)))
    return rows


def test_the_scan_actually_finds_screens():
    """A guard on the guard. If the regex stops matching, every test below
    would pass vacuously over an empty list and certify nothing - which is the
    failure mode this whole audit kept running into."""
    rows = _bound_models()
    assert len(rows) >= 50, "only %d bound A04 screens found - the scan broke" % len(rows)


def test_every_bound_model_is_reachable_through_the_generic_endpoint():
    """The defect this file exists for.

    Asserted against the GLOBAL registry, deliberately. Two narrower versions
    of this test were wrong before this one:

    1. "m09.js screens are served by m09.py" - 20 false alarms. The nine A04
       fragments are merged by controllers/a04/__init__.py, so any of them may
       serve any A04 screen.
    2. "an A04 screen is served by the A04 registry" - 19 false alarms. A04
       screens legitimately bind models owned by other areas (fix.warranty,
       fix.estimate, fix.subscription and friends are served from A02/A03/A05
       controllers), and that is correct: the model belongs to the area that
       owns the domain, not to the area whose screen happens to show it.

    The only invariant that is actually true, and the only one that matters,
    is the one the endpoint itself applies: can /p03/model/* resolve this
    model at all.
    """
    surfaces = _global_surfaces()
    unreachable = [
        "%s binds %s" % (sid, model)
        for _js, sid, _kind, model in _bound_models()
        if model not in surfaces
    ]
    assert not unreachable, (
        "%d screen(s) bind a model /p03/model/* will refuse:" % len(unreachable)
        + "\n  "
        + "\n  ".join(unreachable)
    )


def test_every_served_surface_is_reachable_from_a_screen(odoo_env):
    """A surface nothing opens is dead weight.

    A child model reached through a parent form's `lines:` grid counts as
    reachable: it is served so the grid can read it, and is edited inside its
    parent rather than from a screen of its own. Without this, adding grids
    makes legitimate surfaces look orphaned - fix.campaign.response,
    fix.qbr.action and fix.segment.membership all did
    (A03/A04 audit, 2026-11-01).

    Parsed per screen body, not with a regex across the whole file: the grid
    is inserted before `model:`, and a whole-file regex both missed it and
    could pair a grid with the wrong screen's model.
    """
    bound = {m for _js, _sid, _kind, m in _bound_models()}
    for js in _modules():
        for _sid, body in _screens(js):
            mm = MODEL.search(body)
            gm = re.search(r"lines:\s*\{[^}]*?field:\s*'([a-z0-9_]+)'", body, re.S)
            if not (mm and gm):
                continue
            owner, field = mm.group(1), gm.group(1)
            if owner not in odoo_env:
                continue
            fl = odoo_env[owner]._fields.get(field)
            if fl is not None and fl.type == "one2many":
                bound.add(fl.comodel_name)
    orphans = sorted(m for m in _a04_surfaces() if m not in bound)
    assert not orphans, (
        "%d surface(s) that no screen opens and no grid reaches:" % len(orphans)
        + "\n  "
        + "\n  ".join(orphans)
    )


def test_no_model_is_served_by_two_a04_modules():
    """Duplication between modules is explicitly out of scope for this estate.
    The merge raises on it, so importing the package is the assertion."""
    assert _a04_surfaces(), "the merged A04 registry is empty"


def test_every_bound_model_exists_in_the_orm(odoo_env):
    """A surface can be registered for a model that was never installed."""
    missing = [
        "%s binds %s, which is not in the registry" % (sid, model)
        for _js, sid, _kind, model in _bound_models()
        if model not in odoo_env
    ]
    assert not missing, "\n  ".join(missing)


@pytest.mark.parametrize("js_name", [p.name for p in _modules()])
def test_each_module_fragment_declares_at_least_one_screen(js_name):
    assert _screens(SRC / js_name), "%s declares no screens" % js_name


COLS = re.compile(r"cols:\s*\[([^\]]*)\]")


def _list_screens():
    """[(js, screen_id, model, cols)] for every A04 model_list."""
    out = []
    for js in _modules():
        for sid, body in _screens(js):
            if "kind: 'model_list'" not in body:
                continue
            m = MODEL.search(body)
            c = COLS.search(body)
            if m and c:
                out.append((js.name, sid, m.group(1), re.findall(r"'([a-z0-9_.]+)'", c.group(1))))
    return out


def test_the_list_scan_finds_screens():
    """A guard on the guard: an empty list passes everything below."""
    assert len(_list_screens()) >= 30, "the list-screen scan broke"


def test_every_list_column_exists_on_its_model(odoo_env):
    """/p03/model/records DROPS unknown columns silently.

    Nothing is raised and nothing is logged - the column simply does not
    appear. Two M37 lists bound to fix.catalogue.item asked for a `name`
    column that model has never had, so they rendered without their primary
    identifying column and there was no error to chase. The same silent drop
    made a sub-module mapping written during this audit look correct
    (A04 audit, 2026-11-01).
    """
    bad = []
    for js, sid, model, cols in _list_screens():
        if model not in odoo_env:
            continue
        fields = odoo_env[model]._fields
        for col in cols:
            if col not in fields:
                bad.append("%s/%s: column '%s' not on %s" % (js, sid, col, model))
    assert not bad, (
        "%d list column(s) would be silently dropped:" % len(bad) + "\n  " + "\n  ".join(bad)
    )
