# M19 Financial Accounting & GL: every sub-module page offers the button that
# captures its record (audit 2026-11-13).
#
# Four of the twelve M19 pages had no "+ New": Journals (its grid is the
# journal register, so the journal-entry editor was never offered there),
# Subledger Posting Engine, Audit & Retention and Controls & SoD. Six more
# named no form although the module had one for their work: Control Account
# Change, Period Reopen Request, Intercompany Rule and Transfer-Pricing Rate
# were reachable only from a list, the Chart Loader and the FX revaluation from
# no chip at all.
#
# Evaluated as the browser evaluates it: node runs the engine's own fregCreate
# and fregPanels over the real registry fragments.
from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = ROOT / "static" / "src"

_spec = importlib.util.spec_from_file_location(
    "_estate_pages", HERE / "test_estate_module_pages.py"
)
_estate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_estate)

PROBE = """
import * as M from './meta.mjs';
const { P03_MODULES, P03_MODULE_CREATE, P03_FORM_CHIPS, P03_FORM_MODELS, P03_DATA_SCREENS } = M;
function %(create)s
function %(panels)s
const mod = P03_MODULES.M19;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M19', map);
  const createModel = create && create.screen ? (P03_DATA_SCREENS[create.screen] || {}).model || null : null;
  const forms = fregPanels('M19', mod, map).forms.map((f) => {
    const id = P03_FORM_CHIPS['M19:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      declared: P03_FORM_MODELS['M19:' + f] || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const lists = (map.screens || []).map((id) => ({ id, cfg: P03_DATA_SCREENS[id] || {} }))
    .filter((x) => x.cfg.kind === 'model_list')
    .map((x) => ({ id: x.id, model: x.cfg.model, create: x.cfg.create !== false, empty: !!x.cfg.empty }));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create, createModel, forms, lists };
});
const byScreen = P03_FORM_CHIPS['M19:__by_screen__'] || {};
const ownForms = Object.entries(P03_DATA_SCREENS)
  .filter(([id, c]) => id.startsWith('M19-form-') && c.kind === 'model_form' && c.create !== false)
  .map(([id]) => id);
console.log(JSON.stringify({ subs, ownForms, byScreen, moduleCreate: P03_MODULE_CREATE.M19 }));
"""

# How each page's record is captured. 'form': a "+ New" and the chips of the
# forms its work needs (for Journals, the journal-entry editor). 'chip': no
# "+ New" - the record a finance user could type has no model yet, and the
# chip opens a master only a system administrator may create (the button
# would be refused on Save). 'system': written by posting - typing it in
# would fabricate a posting.
CAPTURE = {
    "1": "form",  # account + control-account change + chart loader
    "2": "form",  # journal entry (editor) + partner-ledger take-on
    "3": "system",  # dimension lines are written when an entry posts
    "4": "form",  # period close + reopen request
    "5": "form",  # consolidation book, IC charge, IC rule, TP rate
    "6": "form",  # FX revaluation run
    "7": "form",  # report bridge + nil return
    "8": "chip",  # retention policy (M24 master, administrators)
    "9": "form",  # recurring template + allocation rule
    "10": "form",  # control-account change; SoD exception / control (M29)
    "11": "form",  # legacy GL control-ledger import
    "12": "form",  # legacy bank-ledger take-on
}

# Masters another module owns that only base.group_system may create
# (ir.model.access): never a page's "+ New" in M19.
ADMIN_ONLY = {"fix.retention.class", "fix.sod.control"}


@pytest.fixture(scope="module")
def m19(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m19_capture")
    for area in sorted(d for d in SRC.iterdir() if re.fullmatch(r"a\d\d", d.name)):
        (tmp / area.name).mkdir()
        for js in area.glob("*.js"):
            (tmp / area.name / (js.stem + ".mjs")).write_text(
                js.read_text(encoding="utf-8"), "utf-8"
            )
    meta = (SRC / "p03_modules_meta.js").read_text(encoding="utf-8")
    (tmp / "meta.mjs").write_text(_estate.IMPORT.sub(r'from "\1.mjs"', meta), "utf-8")
    engine = (SRC / "p03_workspace.js").read_text(encoding="utf-8").replace("\r\n", "\n")
    probe = tmp / "probe.mjs"
    probe.write_text(
        PROBE
        % {
            "create": _estate._method(engine, "fregCreate(mid, map)"),
            "panels": _estate._method(engine, "fregPanels(mid, mod, map)"),
        },
        "utf-8",
    )
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our own probe file
        [node, str(probe)], capture_output=True, encoding="utf-8", check=True, timeout=120
    )
    return json.loads(out.stdout)


def _sub(m19, no):
    return next(s for s in m19["subs"] if s["no"] == no)


def test_every_page_is_classified(m19):
    assert sorted(s["no"] for s in m19["subs"]) == sorted(CAPTURE)


@pytest.mark.parametrize("no", sorted(CAPTURE, key=int))
def test_each_page_offers_its_capture(m19, no):
    sub = _sub(m19, no)
    if CAPTURE[no] == "form":
        assert sub["create"], "page %s '%s' has no + New" % (no, sub["title"])
        assert sub["forms"], "page %s '%s' names no form" % (no, sub["title"])
    elif CAPTURE[no] == "chip":
        assert not sub["create"], "page %s offers a + New finance cannot save" % no
        assert any(f["opens"] for f in sub["forms"]), "page %s names no form" % no
    else:
        opening = [f for f in sub["forms"] if f["opens"]]
        assert not sub["create"] and not opening, "page %s would let a person type in %s" % (
            no,
            sub["model"],
        )
        assert all(lst["empty"] for lst in sub["lists"]), "page %s: say where rows come from" % no


@pytest.mark.parametrize("no", sorted(CAPTURE, key=int))
def test_every_chip_opens_the_form_of_its_declared_record(m19, no):
    """A chip is either the journal-entry editor or an in-workspace form whose
    model is the one FORM_MODELS declares (the M19 registry test checks that
    model exists in the ORM)."""
    for f in _sub(m19, no)["forms"]:
        if f["f"] == "Journal Entry (manual/recurring)":
            assert f["declared"] == "account.move"
            continue
        assert f["kind"] == "model_form", "chip %s opens %s" % (f["f"], f["kind"])
        assert f["opens"], "chip %s opens a form that cannot create" % f["f"]
        assert f["model"] == f["declared"], "chip %s: form %s, declared %s" % (
            f["f"],
            f["model"],
            f["declared"],
        )


def test_journals_offers_the_journal_entry_editor(m19):
    sub = _sub(m19, "2")
    assert sub["create"] == {"module": True}
    assert m19["moduleCreate"]["model"] == "account.move"


def test_records_mastered_elsewhere_open_their_masters_form(m19):
    chips = {f["f"]: f["id"] for s in m19["subs"] for f in s["forms"]}
    assert chips["Retention Policy"] == "M24-form-retention"
    assert chips["SoD Control"] == "M29-form-sodcontrol"
    assert chips["SoD Exception"] == "M29-form-sodexception"


def test_admin_only_masters_are_admin_only_in_the_acl():
    """The reason they are chips and not buttons: only base.group_system may
    create them. If that ever changes, the classification above must too."""
    addons = ROOT.parents[1]
    creators = {}
    for csv in addons.glob("**/security/ir.model.access.csv"):
        for line in csv.read_text(encoding="utf-8").splitlines()[1:]:
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 8:
                continue
            model = parts[2].split(".")[-1].removeprefix("model_").replace("_", ".")
            if model in ADMIN_ONLY and parts[6] == "1":
                creators.setdefault(model, set()).add(parts[3])
    assert creators == {m: {"base.group_system"} for m in ADMIN_ONLY}, creators


def test_no_page_button_opens_an_admin_only_master(m19):
    bad = ["%s %s" % (s["no"], s["title"]) for s in m19["subs"] if s["createModel"] in ADMIN_ONLY]
    assert not bad, "\n  ".join(bad)


def test_controls_page_captures_the_control_account_change(m19):
    sod = _sub(m19, "10")
    assert sod["create"]["screen"] == "M19-form-control-change"
    assert "M19-control-changes" in sod["screens"]


def test_a_page_header_creates_its_own_record_when_it_has_a_form(m19):
    """The "+ New" of a page with its own form is that form - not a form of a
    neighbouring record (Controls & SoD declares its related record)."""
    bad = [
        "%s %s: + New makes %s" % (s["no"], s["title"], s["createModel"])
        for s in m19["subs"]
        if s["create"] and s["createModel"] and s["no"] != "10" and s["createModel"] != s["model"]
    ]
    assert not bad, "\n  ".join(bad)


def test_every_m19_form_is_offered_on_a_page(m19):
    """A form nobody can reach from a sub-module page is a capture the user
    cannot find: each M19 form is a chip or the + New of some page."""
    offered = {f["id"] for s in m19["subs"] for f in s["forms"]}
    offered |= {
        s["create"]["screen"] for s in m19["subs"] if s["create"] and "screen" in s["create"]
    }
    missing = sorted(set(m19["ownForms"]) - offered)
    assert not missing, "\n  ".join(missing)


def test_lists_on_a_page_open_their_form(m19):
    """Every list mapped on a page that can create has a row form."""
    bad = [
        "%s/%s" % (s["no"], lst["id"])
        for s in m19["subs"]
        for lst in s["lists"]
        if lst["create"] and lst["id"] not in m19["byScreen"]
    ]
    assert not bad, "\n  ".join(bad)
