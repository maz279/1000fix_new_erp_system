# M27 Contact Centre (16743): every sub-module page offers the button that
# captures ITS record, as spec section 5 (FR-CCE-001..058) describes it
# (audit 2026-11-14).
#
# Before:
#   * Consent Enforcement listed and captured OUTBOUND DIAL LISTS, which
#     enforce nothing; the BTRC DND registry the delivery service reads at
#     send (spec 10.1: owned by M27) was on no screen at all.
#   * Agent Desktop listed and captured disposition CODES (configuration):
#     no page let an agent wrap up the contact they had handled
#     (FR-CCE-033), and no code path let an agent set their own presence
#     (FR-CCE-032) - every set_presence() caller is system-forced.
#   * Digital Channels had no button: e-mail and social contacts have no
#     adapter, so they could not be recorded at all.
#   * The conversation form demanded a telephony SID, a disposition and
#     wrap-up notes at CAPTURE, and let a recording URL be typed - after which
#     Resolve refused the call for ever (no digest of the audio).
#   * The template form had no Bengali body (the field DE-17 calls the one
#     that matters); the QA form had no rubric; the presence form let anyone
#     overwrite presence, its source and its time with no history row.
#
# Evaluated as the browser evaluates it: node runs the engine's own
# fregCreate and fregPanels over the real registry fragments.
from __future__ import annotations

import ast
import importlib.util
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "static" / "src"
CONTROLLER = HERE.parent / "controllers" / "a03" / "m27.py"
WRITABLE = HERE.parent / "controllers" / "a03" / "writable.py"
ADDONS = HERE.parents[2]

_spec = importlib.util.spec_from_file_location(
    "_estate_pages", HERE / "test_estate_module_pages.py"
)
_estate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_estate)

PROBE = """
import * as M from './meta.mjs';
const { P03_MODULES, P03_MODULE_CREATE, P03_FORM_CHIPS, P03_DATA_SCREENS } = M;
function %(create)s
function %(panels)s
const mod = P03_MODULES.M27;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M27', map);
  const forms = fregPanels('M27', mod, map).forms.map((f) => {
    const id = P03_FORM_CHIPS['M27:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  return { no: s[0], title: s[1], model: map.model || null, domain: map.domain || [],
    screens: map.screens || [],
    create: create && (create.screen || (create.module ? 'module' : null)),
    label: create ? (create.label || null) : null, forms };
});
const S = P03_DATA_SCREENS;
console.log(JSON.stringify({ subs,
  module_create: P03_MODULE_CREATE.M27,
  nav: mod.groups.flatMap((g) => g.screens.map((s) => s.id)),
  screens: Object.fromEntries(Object.entries(S).filter(([id]) => id.startsWith('M27-')).map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create, back: c.back || null, empty: !!c.empty,
    domain: c.domain || [], newLabel: c.newLabel || null,
    pick: c.pickRecord ? { domain: c.pickRecord.domain || [] } : null,
    saveAction: c.saveAction || null,
    actions: (c.actions || []).map((a) => a.m),
    lines: c.lines ? { field: c.lines.field, readonlyGrid: !!c.lines.readonlyGrid } : null,
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({ name: f.name,
      readonly: !!f.readonly, required: !!f.required, choices: f.choices || null,
      domain: f.domain || null })) }])),
  by_screen: P03_FORM_CHIPS['M27:__by_screen__'] }));
"""

# What each page captures (the form its "+ New" opens) - spec section 5.
CAPTURE = {
    "1": "M27-form-ivr",  # FR-CCE-002: the bilingual IVR menu
    "2": "M27-form-digital",  # FR-CCE-011/013: a contact with no adapter
    "3": "module",  # FR-CCE-017: the unified conversation
    "4": "M27-form-queue",  # FR-CCE-019: a queue
    "5": "M27-form-wrapup",  # FR-CCE-033: the agent's wrap-up
    "6": "M27-form-wfm",  # FR-CCE-051: a roster shift
    "7": "M27-form-qa",  # FR-CCE-054: a QA evaluation
    "8": "M27-form-template",  # FR-CCE-036: a notification template
    "9": "M27-form-dnd",  # FR-CCE-039: a DND registry entry
}


@pytest.fixture(scope="module")
def m27(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m27_capture")
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


def _sub(m27, no):
    return next(s for s in m27["subs"] if s["no"] == no)


def _fields(m27, sid):
    return {f["name"]: f for f in m27["screens"][sid]["fields"]}


def _literal(path, name):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == name:
            return ast.literal_eval(node.value)
    raise AssertionError("%s no longer declares %s" % (path.name, name))


def _writable():
    """The generated a03 write whitelist (frozensets, so imported, not parsed)."""
    spec = importlib.util.spec_from_file_location("_a03_writable", WRITABLE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.WRITABLE


def _served_actions():
    surfaces = _literal(CONTROLLER, "SURFACES")
    return {m: set(cfg.get("actions") or ()) for m, cfg in surfaces.items()}


def _model_source(model):
    for py in ADDONS.rglob("models/*.py"):
        text = py.read_text(encoding="utf-8", errors="ignore")
        if re.search(r'_name = ["\']%s["\']' % re.escape(model), text):
            return text
    raise AssertionError("no source declares %s" % model)


@pytest.mark.parametrize("no", sorted(CAPTURE, key=int))
def test_every_page_captures_its_own_record(m27, no):
    sub = _sub(m27, no)
    assert sub["create"] == CAPTURE[no], "%s %s offers %s" % (no, sub["title"], sub["create"])


@pytest.mark.parametrize("no", sorted(CAPTURE, key=int))
def test_every_chip_opens_a_form(m27, no):
    sub = _sub(m27, no)
    assert sub["forms"], "%s %s shows no form chip" % (no, sub["title"])
    for f in sub["forms"]:
        assert f["opens"], "%s chip %s opens %s" % (no, f["f"], f["id"])


def test_consent_enforcement_is_about_consent_not_dial_lists(m27):
    """FR-CCE-038/039: the page shows the DND registry and what was
    suppressed at send, captures a DND entry, and reaches M33's consent form
    (M33 owns consent; M27 enforces it)."""
    sub = _sub(m27, "9")
    assert sub["model"] == "fix.dnd.registry"
    assert "M27-outbound" not in sub["screens"]
    assert {"M27-dnd", "M27-suppressed"} <= set(sub["screens"])
    chips = {f["f"]: f for f in sub["forms"]}
    assert "Outbound List" not in chips
    assert chips["Consent Record"]["id"] == "M33-form-consent"
    assert chips["Consent Record"]["model"] == "fix.consent"
    assert ["state", "=", "suppressed"] in m27["screens"]["M27-suppressed"]["domain"]
    assert m27["screens"]["M27-suppressed"]["create"] is False


def test_the_dnd_registry_is_the_one_the_delivery_service_reads(m27):
    """The registry is honoured at the point of send, so an entry made here
    changes what is sent - not a record for its own sake."""
    assert 'Registry = self.env.get("fix.dnd.registry")' in _model_source("fix.notif.delivery")
    form = _fields(m27, "M27-form-dnd")
    for name in ("msisdn", "source", "registered_on"):
        assert form[name]["required"] and not form[name]["readonly"]
    assert "fix.dnd.registry" in _served_actions()
    assert "fix.dnd.registry" in _writable()
    assert {"M27-dnd", "M27-suppressed", "M27-form-dnd"} <= set(m27["nav"])


def test_outbound_dial_lists_moved_to_voice(m27):
    """Outbound voice (FR-CCE-004) is a Voice & IVR matter."""
    sub = _sub(m27, "1")
    assert "M27-outbound" in sub["screens"]
    # pass 2 (2026-11-19) added Callback Request, Voicemail and On-Call Slot
    # between them: see test_m27_capture_pass2.py
    chips = [f["f"] for f in sub["forms"]]
    assert chips[0] == "IVR Flow" and "Outbound List" in chips


def test_agent_desktop_wraps_up_the_agents_conversations(m27):
    sub = _sub(m27, "5")
    assert sub["model"] == "fix.conversation"
    assert ["state", "=", "with_agent"] in sub["domain"]
    assert [f["f"] for f in sub["forms"]][:2] == ["Wrap-Up & Disposition", "Set My Presence"]
    form = m27["screens"]["M27-form-wrapup"]
    assert form["pick"] and ["state", "=", "with_agent"] in form["pick"]["domain"]
    act = form["saveAction"]
    assert act["method"] == "action_wrap_up"
    assert act["kwargs"] == {
        "disposition_id": "disposition_id",
        "wrapup_notes": "wrapup_notes",
        "fcr": "fcr",
    }
    assert "action_wrap_up" in _served_actions()["fix.conversation"]
    src = _model_source("fix.conversation")
    assert "def action_wrap_up(self, disposition_id=None, wrapup_notes=" in src
    # it closes through action_resolve, so the existing gates still decide
    body = src.split("def action_wrap_up", 1)[1].split("\n    def ", 1)[0]
    assert "self.action_resolve()" in body
    fields = _fields(m27, "M27-form-wrapup")
    assert fields["disposition_id"]["required"] and fields["wrapup_notes"]["required"]


def test_an_agent_can_set_their_own_presence(m27):
    form = m27["screens"]["M27-form-set-presence"]
    assert form["model"] == "fix.cc.presence.status"
    assert form["pick"] and ["active", "=", True] in form["pick"]["domain"]
    assert form["saveAction"]["method"] == "action_set_my_presence"
    assert "action_set_my_presence" in _served_actions()["fix.cc.presence.status"]
    src = _model_source("fix.cc.presence.status")
    body = src.split("def action_set_my_presence", 1)[1].split("\n    def ", 1)[0]
    assert "state_for(self.env.user)" in body and 'source="manual"' in body


def test_presence_is_never_typed_over(m27):
    """set_presence() writes the log adherence is measured from; a plain
    write skipped it and let anyone choose the "Set By"."""
    form = _fields(m27, "M27-form-presence")
    for name in (
        "agent_id",
        "presence_status_id",
        "presence_source",
        "changed_at",
        "missed_offers",
    ):
        assert form[name]["readonly"], name
    assert m27["screens"]["M27-form-presence"]["lines"]["readonlyGrid"]
    allowed = _writable()["fix.cc.agent.state"]
    assert allowed == frozenset({"is_bookable"})


def test_digital_contact_offers_only_digital_channels(m27):
    sub = _sub(m27, "2")
    assert sub["forms"] == [
        {
            "f": "Digital Contact",
            "id": "M27-form-digital",
            "kind": "model_form",
            "model": "fix.conversation",
            "opens": True,
        }
    ]
    fields = _fields(m27, "M27-form-digital")
    keys = [c[0] for c in fields["channel"]["choices"]]
    # digital channels only - never voice; pass 2 (2026-11-19) added inbound
    # SMS (FR-CCE-012) and social messaging (FR-CCE-013)
    assert sorted(keys) == ["chat", "email", "in_app", "sms", "social", "whatsapp"]
    # operating_unit_id is required on the model with no default
    assert fields["operating_unit_id"]["required"]
    assert fields["contact_identity"]["required"]
    assert m27["screens"]["M27-form-digital"]["lines"]["field"] == "turn_ids"


def test_a_conversation_is_captured_before_its_outcome_is_known(m27):
    """Disposition and notes are demanded at CLOSE (action_resolve), not at
    capture; a typed recording URL could never be closed (no audio digest)."""
    fields = _fields(m27, "M27-form-call")
    assert not fields["call_sid"]["required"]
    assert not fields["disposition_id"]["required"]
    assert not fields["wrapup_notes"]["required"]
    assert fields["recording_url"]["readonly"]
    src = _model_source("fix.conversation")
    assert "Mandatory wrap-up required" in src
    assert "recording_url" not in _writable()["fix.conversation"]


def test_template_form_carries_the_bengali_body(m27):
    fields = _fields(m27, "M27-form-template")
    for name in ("name_bn", "subject_bn", "body_bn"):
        assert name in fields and not fields[name]["readonly"]
    assert fields["body"]["required"]
    assert "body_bn = fields.Text(" in _model_source("fix.cc.notif.template")


def test_qa_evaluation_names_its_published_rubric(m27):
    fields = _fields(m27, "M27-form-qa")
    assert fields["rubric_id"]["domain"] == [["state", "=", "published"]]
    assert not fields["rubric_id"]["readonly"]
    for derived in ("handled_by", "auto_score", "coverage_pct", "manual_criteria_pending"):
        assert fields[derived]["readonly"]


def test_routing_rule_form_is_reachable_from_its_page(m27):
    chips = {f["f"]: f["id"] for f in _sub(m27, "4")["forms"]}
    assert chips["Routing Rule"] == "M27-form-routing"


def test_every_list_action_is_served(m27):
    served = _served_actions()
    bad = [
        "%s %s" % (sid, m)
        for sid, cfg in m27["screens"].items()
        for m in cfg["actions"]
        if m not in served.get(cfg["model"], set())
    ]
    for sid, cfg in m27["screens"].items():
        if cfg["saveAction"] and cfg["saveAction"]["method"] not in served.get(cfg["model"], set()):
            bad.append("%s saveAction %s" % (sid, cfg["saveAction"]["method"]))
    assert not bad, bad


@pytest.mark.parametrize("sid", ["M27-dnd", "M27-suppressed"])
def test_new_lists_explain_their_empty_state(m27, sid):
    assert m27["screens"][sid]["empty"]
