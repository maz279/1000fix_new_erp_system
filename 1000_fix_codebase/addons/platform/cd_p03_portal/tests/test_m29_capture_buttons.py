# M29 Identity, Access & Security: every sub-module page captures the records
# it covers (capture audit 2026-11-14).
#
# Before:
#   * Identity & MFA had no capture: its user list refuses "+ New" (logins come
#     from onboarding: employee.joined -> Keycloak SSO), yet its one chip, User,
#     opened a BLANK login form - an admin could create a login outside the
#     joiner path, its SoD gate and its audit. The identity-lifecycle record,
#     the joiner / mover / leaver event (FR-SEC-027..029), sat on another page.
#   * Monitoring & Audit had no capture: its grid is the append-only audit
#     trail, and nobody could report a security incident or request break-glass
#     access from it although both lists were on the page. The vulnerability
#     register (spec §10.1, BRU-SEC-21, AC-23) did not exist at all.
#   * SoD Testing and Data Protection showed no form chip beyond "+ New": SoD
#     controls and exceptions, and encryption keys, could not be captured there.
#   * Role & Group Model and Record & Field Rules offered no chip for Model
#     Access, Field Rule or Isolation Tier, although their lists were on the page.
#   * Certification Campaigns, Role Assignments and SoD Exceptions were on no
#     sub-module page.
#
# Second pass (2026-11-19), spec §5/§8/§10/§11 against what each page offered:
#   * Identity & MFA could not suspend or reinstate an identity (§8.1), register a
#     service account with an accountable owner (FR-SEC-012) or a device
#     (FR-SEC-010). Its JML form could not record a mover or a leaver at all: the
#     surface fenced the employee picker to people with NO login.
#   * Role & Group Model had no delegation of authority (FR-SEC-019).
#   * Data Protection had no cross-border transfer (FR-SEC-049) or data-subject
#     request (FR-SEC-051), and no residency class on a classification (FR-SEC-047).
#   * Monitoring & Audit had no penetration test (AUT-SEC-16, AC-26), no breach
#     decision on an incident (AUT-SEC-13) and no emergency break-glass path,
#     post-hoc justification or session review (FR-SEC-034/035, BRU-SEC-20).
#
# Evaluated as the browser evaluates it: node runs the engine's own fregCreate
# and fregPanels over the real registry fragments (the M28 guard's fixture).
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

_spec = importlib.util.spec_from_file_location(
    "_estate_pages", HERE / "test_estate_module_pages.py"
)
_estate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_estate)

PROBE = """
import * as M from './meta.mjs';
const { P03_MODULES, P03_MODULE_CREATE, P03_FORM_CHIPS, P03_DATA_SCREENS, P03_REPORT_ROUTES } = M;
function %(create)s
function %(panels)s
const mod = P03_MODULES.M29;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M29', map);
  const panels = fregPanels('M29', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M29:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M29.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: own || null, label: create ? create.label : null, forms,
    reports: panels.reports.map((r) => ({ r, route: P03_REPORT_ROUTES['M29:' + r] || null })) };
});
console.log(JSON.stringify({ subs,
  kpis: mod.kpis.map((k) => k.m),
  nav: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => id.startsWith('M29-')).map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create, report: c.report || null,
    newForm: c.newForm || null, newLabel: c.newLabel || null, cols: c.cols || [],
    tabs: (c.tabs || []).map((x) => x.id),
    lines: c.lines ? { field: c.lines.field, tab: c.lines.tab || null, fixed: !!c.lines.fixedRows,
      cols: c.lines.fields.map((f) => ({ name: f.name, type: f.type || null, readonly: !!f.readonly })) } : null,
    actions: (c.actions || []).map((a) => ({ m: a.m, kwarg: a.kwarg || null })),
    fields: (c.sections || []).flatMap((s) => (s.fields || []).map((f) => ({ ...f, tab: s.tab || null }))).map((f) => ({
      name: f.name, readonly: !!f.readonly, required: !!f.required, tab: f.tab,
      value: f.value === undefined ? null : f.value, domain: f.domain || null })) }])),
  by_screen: P03_FORM_CHIPS['M29:__by_screen__'] }));
"""

# What each page must let a person capture: the page's own "+ New" first,
# then every other record the page covers, by its form screen.
CAPTURES = {
    "1": [
        "M29-form-provision",
        "M29-form-jml",
        "M29-form-suspend",
        "M29-form-service-account",
        "M02-form-device",
    ],
    "2": ["M29-form-role", "M29-form-acl", "M63-form-substitution"],
    "3": ["M29-form-rule", "M29-form-fieldrule", "M29-form-isolation-tier"],
    "4": ["M29-form-request", "M29-form-campaign", "M29-form-cert"],
    "5": ["M29-form-sodtest", "M29-form-sodcontrol", "M29-form-sodexception"],
    "6": ["M29-form-sensitive", "M29-form-key", "M60-form-transfer", "M33-form-dsr"],
    "7": [
        "M29-form-incident",
        "M29-form-session",
        "M29-form-vulnerability",
        "M29-form-pentest",
    ],
}

# The record each page lists (its grid).
RECORDS = {
    "1": "res.users",
    "2": "fix.role",
    "3": "ir.rule",
    "4": "fix.access.request",
    "5": "fix.sod.test",
    "6": "fix.sensitive.field",
    "7": "fix.security.audit",
}

# System-written registers: a person never types one.
SYSTEM_WRITTEN = (
    "M29-users",
    "M29-sessions",
    "M29-assignments",
    "M29-groups",
    "M29-audit",
    "M29-residency",
    # pass 2: other modules' records, captured through their owners' forms
    "M29-devices",
    "M29-delegations",
    "M29-transfers",
    "M29-rights",
)


@pytest.fixture(scope="module")
def m29(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m29_capture")
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


def _controller():
    """SURFACES / WRITABLE / REPORTS of controllers/a12/m29.py, read without Odoo:
    the per-model action names, the write whitelist and the report keys."""
    tree = ast.parse((HERE.parent / "controllers" / "a12" / "m29.py").read_text(encoding="utf-8"))
    out = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or not isinstance(node.targets[0], ast.Name):
            continue
        name = node.targets[0].id
        if name == "WRITABLE":
            out[name] = ast.literal_eval(node.value)
        elif name == "SURFACES":
            actions = {}
            for key, conf in zip(node.value.keys, node.value.values, strict=True):
                acts = set()
                for k, v in zip(conf.keys, conf.values, strict=True):
                    if ast.literal_eval(k) == "actions" and isinstance(v, ast.Set):
                        acts = {ast.literal_eval(e) for e in v.elts}
                actions[ast.literal_eval(key)] = acts
            out[name] = actions
        elif name == "REPORTS":
            out[name] = {ast.literal_eval(k) for k in node.value.keys}
    return out


def _sub(m29, no):
    return next(s for s in m29["subs"] if s["no"] == no)


def test_every_page_is_classified(m29):
    assert sorted(s["no"] for s in m29["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m29, no):
    sub = _sub(m29, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]}
    missing = [form for form in [own, *others] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)
    for f in sub["forms"]:
        assert f["kind"] == "model_form", "chip %s opens %s" % (f["f"], f["kind"])


@pytest.mark.parametrize("no", sorted(RECORDS, key=int))
def test_each_page_lists_its_own_record(m29, no):
    assert _sub(m29, no)["model"] == RECORDS[no]


def test_each_captured_record_is_listed_on_its_page(m29):
    """A capture lands on a list of the page it was made from."""
    for sub in m29["subs"]:
        listed = {m29["screens"][s]["model"] for s in sub["screens"] if s in m29["screens"]}
        for f in sub["forms"]:
            assert f["model"] in listed, "page %s captures %s but lists no such record" % (
                sub["no"],
                f["model"],
            )


def test_identity_page_never_offers_a_blank_login(m29):
    """A login is provisioned by a joiner event a second person applies (it
    creates the login, grants the roles through the SoD gate and sets the data
    scope); never typed into a blank user form."""
    assert m29["screens"]["M29-form-user"]["create"] is False
    sub = _sub(m29, "1")
    assert "M29-jml" in sub["screens"]
    assert sub["label"] == "Provision a New Login"
    # the User chip stays (estate standard: every module form sits on a page), but
    # it opens an existing user only - never a blank login
    user_chip = next(f for f in sub["forms"] if f["id"] == "M29-form-user")
    assert user_chip["opens"] is False


def test_the_users_list_offers_provisioning_not_a_blank_login(m29):
    """The user's report (14 Nov): the Users screen had no way to enter anyone."""
    users = m29["screens"]["M29-users"]
    assert users["create"] is False
    assert users["newForm"] == "M29-form-provision"
    form = m29["screens"]["M29-form-provision"]
    assert form["model"] == "fix.jml.event" and form.get("create") is not False
    assert form["newLabel"] == "Provision a New Login"


def test_provisioning_states_what_the_person_may_access(m29):
    fields = {f["name"]: f for f in m29["screens"]["M29-form-provision"]["fields"]}
    assert fields["employee_id"]["required"] and fields["role_id"]["required"]
    for name in ("extra_role_ids", "operating_unit_ids", "default_operating_unit_id"):
        assert not fields[name]["readonly"], name
    for name in ("proposed_login", "permission_preview", "applied_on", "result_note"):
        assert fields[name]["readonly"], name
    assert "event_type" not in fields, "a provisioning event is always a joiner"
    for name in ("reason", "lang", "tz", "valid_until"):
        assert name in fields, name
    assert "user_id" not in fields, "the login is created, never picked"


def test_engine_offers_the_named_form_on_a_list_that_refuses_new():
    engine = (SRC / "p03_workspace.js").read_text(encoding="utf-8")
    view = (SRC / "p03_workspace.xml").read_text(encoding="utf-8")
    assert "mlNewVia()" in engine and "get mlNewViaLabel()" in engine
    assert "state.gl.modelCfg.create === false &amp;&amp; mlNewViaLabel" in view


def test_monitoring_page_reports_an_incident(m29):
    sub = _sub(m29, "7")
    assert sub["label"] == "Report a Security Incident"
    assert {"M29-incidents", "M29-privileged", "M29-vulnerabilities"} <= set(sub["screens"])


def test_every_working_screen_sits_on_a_page(m29):
    placed = {sid for s in m29["subs"] for sid in s["screens"]}
    orphans = [
        sid
        for sid, cfg in m29["screens"].items()
        if cfg["kind"] == "model_list" and sid not in placed
    ]
    assert not orphans, orphans


def test_every_page_report_opens_its_pack(m29):
    reports = _controller()["REPORTS"]
    for sub in m29["subs"]:
        for r in sub["reports"]:
            assert r["route"], "page %s report %s has no route" % (sub["no"], r["r"])
            assert m29["screens"][r["route"]]["report"] in reports, r


def test_a_list_offering_new_opens_a_form_of_its_own_model(m29):
    for sid, cfg in m29["screens"].items():
        if cfg["kind"] != "model_list" or cfg.get("create") is False:
            continue
        form = m29["by_screen"].get(sid)
        assert form, "%s offers + New but opens no form" % sid
        assert m29["screens"][form]["model"] == cfg["model"], sid


def test_system_written_registers_still_create_nothing(m29):
    for sid in SYSTEM_WRITTEN:
        assert m29["screens"][sid]["create"] is False, sid


def test_every_row_action_is_served(m29):
    surfaces = _controller()["SURFACES"]
    for sid, cfg in m29["screens"].items():
        for act in cfg["actions"]:
            assert act["m"] in surfaces[cfg["model"]], "%s %s is not served" % (sid, act["m"])


def test_every_editable_form_field_is_writable(m29):
    """A field a form lets the user type saves through the write whitelist."""
    writable = _controller()["WRITABLE"]
    for sid, cfg in m29["screens"].items():
        if cfg["kind"] != "model_form":
            continue
        editable = {f["name"] for f in cfg["fields"] if not f["readonly"]}
        lost = editable - set(writable[cfg["model"]])
        assert not lost, "%s cannot save %s" % (sid, sorted(lost))


def test_vulnerability_lifecycle_is_never_typed(m29):
    fields = {f["name"]: f for f in m29["screens"]["M29-form-vulnerability"]["fields"]}
    stamps = {
        "sla_due",
        "reported_by_id",
        "remediation_note",
        "remediated_by_id",
        "remediated_on",
        "verified_by_id",
        "verified_on",
        "acceptance_reason",
        "accepted_by_id",
        "accepted_until",
        "escalated_on",
    }
    assert all(fields[n]["readonly"] for n in stamps)
    writable = set(_controller()["WRITABLE"]["fix.vulnerability"])
    assert not (stamps | {"state"}) & writable


def test_the_vulnerability_kpi_is_served(m29):
    assert "critical_vulns_overdue" in m29["kpis"]
    text = (HERE.parent / "controllers" / "a12" / "m29.py").read_text(encoding="utf-8")
    assert '"critical_vulns_overdue":' in text


def test_the_new_user_form_is_a_six_step_wizard_with_a_permission_checklist(m29):
    """User feedback (14 Nov): the first form was not professional. Modelled on
    D365 (review effective access), NetSuite (None / View / Create / Edit
    levels; print and export as their own switches) and SAP (restrictions
    narrow what roles grant)."""
    form = m29["screens"]["M29-form-provision"]
    assert form["tabs"] == ["person", "roles", "scope", "perms", "validity", "review"]
    grid = form["lines"]
    assert grid["field"] == "permission_line_ids" and grid["tab"] == "perms" and grid["fixed"]
    cols = {c["name"]: c for c in grid["cols"]}
    assert cols["level"]["type"] == "selection" and not cols["level"]["readonly"]
    for switch in ("can_approve", "can_print", "can_export", "can_email"):
        assert cols[switch]["type"] == "boolean" and not cols[switch]["readonly"], switch
    for shown in ("area", "module_name", "allowed_label"):
        assert cols[shown]["readonly"], shown
    writable = set(_controller()["WRITABLE"]["fix.jml.event"])
    assert "permission_line_ids" in writable


def test_narrowed_permissions_are_listed_on_the_identity_page(m29):
    assert "M29-module-permissions" in _sub(m29, "1")["screens"]
    assert m29["screens"]["M29-module-permissions"]["create"] is False


def test_every_workspace_endpoint_checks_the_module_permission():
    text = (HERE.parent / "controllers" / "p03_generic_api.py").read_text(encoding="utf-8")
    for need in ("view", "create", "edit", "approve", "print", "export", "email"):
        assert '"%s"' % need in text, need
    assert text.count("_gate(") >= 10, "records, form, write, action, report x3, list x2"


# ---------------------------------------------------------------- second pass (2026-11-19)
def _fields(m29, form):
    return {f["name"]: f for f in m29["screens"][form]["fields"]}


def test_the_jml_picker_is_not_fenced_to_people_without_a_login():
    """The surface-wide fence made every JML form offer only login-less employees,
    so a mover, a leaver or a suspension could pick nobody."""
    text = (HERE.parent / "controllers" / "a12" / "m29.py").read_text(encoding="utf-8")
    block = text[text.index('"fix.jml.event": {') : text.index('"fix.access.certification": {')]
    assert '"pickers"' not in block, "the surface fences every JML form's employee picker"
    assert '"picker_names": ("employee_id",)' in block


def test_each_jml_form_states_its_own_employee_filter(m29):
    assert _fields(m29, "M29-form-provision")["employee_id"]["domain"] == [["user_id", "=", False]]
    assert _fields(m29, "M29-form-suspend")["employee_id"]["domain"] == [["user_id", "!=", False]]
    assert _fields(m29, "M29-form-jml")["employee_id"]["domain"] is None


def test_the_suspension_form_files_a_suspension(m29):
    form = m29["screens"]["M29-form-suspend"]
    fields = _fields(m29, "M29-form-suspend")
    assert form["model"] == "fix.jml.event" and form["newLabel"]
    assert fields["event_type"]["value"] == "suspend"
    assert fields["reason"]["required"]
    for stamp in ("applied_on", "result_note", "permission_preview"):
        assert fields[stamp]["readonly"], stamp
    assert "suspend_reason" in _fields(m29, "M29-form-jml")
    assert "suspend_reason" in _controller()["WRITABLE"]["fix.jml.event"]


STAMPS = {
    "M29-form-service-account": {
        "code",
        "is_orphaned",
        "orphan_flagged_on",
        "state_note",
        "state_changed_by_id",
    },
    "M29-form-incident": {
        "breach_decision",
        "breach_assessed_by_id",
        "breach_assessed_on",
        "breach_confirmed_by_id",
        "breach_confirmed_on",
        "statutory_clock_start",
        "m60_notification_ref",
        "breach_assessment_due",
    },
    "M29-form-session": {
        "justification",
        "justification_due_at",
        "justification_escalated_on",
        "reviewed_by_id",
        "reviewed_on",
        "review_outcome",
        "review_note",
    },
    "M29-form-pentest": {"finding_count", "open_count", "closed_on", "closed_by_id"},
    "M29-form-sensitive": {"classified_by_id", "classified_on"},
}


@pytest.mark.parametrize("form", sorted(STAMPS))
def test_pass2_decisions_and_stamps_are_never_typed(m29, form):
    fields = _fields(m29, form)
    model = m29["screens"][form]["model"]
    writable = set(_controller()["WRITABLE"][model])
    for name in STAMPS[form]:
        assert name in fields, "%s does not show %s" % (form, name)
        assert fields[name]["readonly"], "%s lets %s be typed" % (form, name)
        assert name not in writable, "%s.%s is writable" % (model, name)
    assert "state" not in writable


def test_the_session_form_offers_break_glass_and_the_record_of_actions(m29):
    fields = _fields(m29, "M29-form-session")
    assert not fields["break_glass"]["readonly"] and not fields["actions_summary"]["readonly"]
    actions = {a["m"]: a["kwarg"] for a in m29["screens"]["M29-privileged"]["actions"]}
    assert actions["action_close"] == "summary", "closing asks what was done (FR-SEC-034)"
    assert actions["action_justify"] == "justification"
    assert actions["action_review_misuse"] == "note"
    for act in ("action_break_glass", "action_review_ok"):
        assert act in actions, act


def test_the_incident_form_records_the_breach_facts(m29):
    fields = _fields(m29, "M29-form-incident")
    assert fields["personal_data_involved"]["required"]
    for name in ("significant_damage_likely", "data_subjects_estimate", "owner_id"):
        assert not fields[name]["readonly"], name
    actions = {a["m"]: a["kwarg"] for a in m29["screens"]["M29-incidents"]["actions"]}
    assert actions["action_assess_breach"] == "decision"
    assert "action_confirm_not_notifiable" in actions


def test_the_classification_carries_the_residency_class(m29):
    fields = _fields(m29, "M29-form-sensitive")
    assert fields["residency_class"]["required"] and not fields["residency_class"]["readonly"]
    assert "residency_class" in m29["screens"]["M29-classification"]["cols"]


def test_a_pentest_finding_names_its_test(m29):
    assert "pentest_id" in _fields(m29, "M29-form-vulnerability")
    assert "pentest_id" in _controller()["WRITABLE"]["fix.vulnerability"]


@pytest.mark.parametrize(
    "form",
    ["M29-form-session", "M29-form-service-account", "M29-form-incident", "M29-form-pentest"],
)
def test_long_pass2_forms_are_tabbed(m29, form):
    """AGENTS.md: a form of more than 15 fields is a multi-tab form, and every
    section of a tabbed form sits on one of its tabs."""
    cfg = m29["screens"][form]
    assert cfg["tabs"], form
    assert all(f["tab"] in cfg["tabs"] for f in cfg["fields"]), form


def test_the_pass2_kpis_are_served(m29):
    text = (HERE.parent / "controllers" / "a12" / "m29.py").read_text(encoding="utf-8")
    for kpi in (
        "breach_assessments_overdue",
        "break_glass_unreviewed",
        "service_accounts_orphaned",
    ):
        assert kpi in m29["kpis"], kpi
        assert '"%s":' % kpi in text, kpi


def test_other_modules_records_open_their_owners_forms(m29):
    by_screen = m29["by_screen"]
    owners = {
        "M29-devices": ("fix.technician.device", "M02-form-device"),
        "M29-delegations": ("fix.approval.substitution", "M63-form-substitution"),
        "M29-transfers": ("fix.grc.data.transfer", "M60-form-transfer"),
        "M29-rights": ("fix.rights.request", "M33-form-dsr"),
    }
    for sid, (model, form) in owners.items():
        assert m29["screens"][sid]["model"] == model, sid
        assert by_screen[sid] == form, sid
