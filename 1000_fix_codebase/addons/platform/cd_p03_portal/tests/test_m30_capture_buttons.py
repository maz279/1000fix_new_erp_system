# M30 Platform Administration: every sub-module page captures the records it
# covers (capture audit 2026-11-14).
#
# Before:
#   * Branch Master listed dispatch zones but offered no Zone capture.
#   * Entity Structure showed no form chip at all, and listed environments it
#     could not capture.
#   * Config & Flags offered only "+ New Feature Flag". Its "Parameter Registry"
#     and "Scheduled Job Registry" were read-only views of Odoo's own tables:
#     no configuration change record (FR-ADM-015/018, BRU-ADM-02) and no job
#     registry (FR-ADM-031, BRU-ADM-11) existed.
#   * Calendars had no chip, and Calendar Holidays was on no page.
#   * Announcements could not capture a notification configuration.
#   * Audit could not capture a release or a ladder band, and "Backup & DR"
#     listed CUSTOMER backup plans (M06's record). Restore tests and DR drills
#     (BRU-ADM-17/18) had no record anywhere.
#   * Nine screens (holidays, ladder bands, health console, backup, five report
#     screens) sat on no page.
#
# Second pass (2026-11-19), read against FR-ADM-001..040 and §10.1:
#   * Branch Master had no capability profile (FR-ADM-004, P0) and no zone
#     boundary (FR-ADM-005).
#   * Entity Structure captured only the legal entity: no cost centre
#     (FR-ADM-006, P0), business line (FR-ADM-007, P0) or effective-dated
#     organisation change (FR-ADM-010/011, BRU-ADM-08).
#   * Config & Flags had no change freeze (FR-ADM-028, BRU-ADM-22), no
#     emergency path (FR-ADM-017, BRU-ADM-04) and no licence register (FR-ADM-021).
#   * Calendars had no shift pattern (FR-ADM-008).
#   * Announcements had no maintenance window (FR-ADM-039, BRU-ADM-19).
#   * Audit had no runbook, alert or capacity review (FR-ADM-036..038).
#
# Evaluated as the browser evaluates it: node runs the engine's own fregCreate
# and fregPanels over the real registry fragments (the M29 guard's fixture).
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
CONTROLLER = HERE.parent / "controllers" / "a12" / "m30.py"

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
const mod = P03_MODULES.M30;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M30', map);
  const panels = fregPanels('M30', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M30:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M30.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: own || null, label: create ? create.label : null, forms,
    reports: panels.reports.map((r) => ({ r, route: P03_REPORT_ROUTES['M30:' + r] || null })) };
});
console.log(JSON.stringify({ subs,
  kpis: mod.kpis.map((k) => k.m),
  nav: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => id.startsWith('M30-')).map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create, report: c.report || null,
    tabs: (c.tabs || []).map((t) => t.id),
    actions: (c.actions || []).map((a) => ({ m: a.m, kwarg: a.kwarg || null })),
    sections: (c.sections || []).map((s) => ({ tab: s.tab || null, n: (s.fields || []).length })),
    cols: c.cols || [],
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({
      name: f.name, readonly: !!f.readonly, required: !!f.required })) }])),
  by_screen: P03_FORM_CHIPS['M30:__by_screen__'] }));
"""

# What each page must let a person capture: the page's own "+ New" first,
# then every other record the page covers, by its form screen.
CAPTURES = {
    "1": ["M30-form-branch", "M30-form-zone", "M30-form-capability", "M02-form-zone"],
    "2": ["M30-form-entity", "M30-form-org-change", "M54-form-centre", "M54-form-bline"],
    "3": [
        "M30-form-flag",
        "M30-form-config-change",
        "M30-form-freeze",
        "M30-form-param",
        "M30-form-job",
        "M30-form-env",
        "M30-form-licence",
    ],
    "4": ["M30-form-calendar", "M30-form-holiday", "M55-form-shift"],
    "5": ["M30-form-announcement", "M30-form-maintenance", "M30-form-notif"],
    "6": [
        "M30-form-dofa-ladder",
        "M30-form-dofa-band",
        "M30-form-release",
        "M30-form-backup",
        "M30-form-drill",
        "M30-form-runbook",
        "M30-form-alert",
        "M30-form-capacity",
    ],
}

# Records the spec gives M30 but another module masters and serves: the chip
# opens that module's form, an M30 list shows them read-only, and a Platform
# Admin may write them (an ACL row in the owning module).
FOREIGN = {
    "fix.geofence": "cd_entity_config",
    "fix.cost.centre": "cd_fpa",
    "fix.business.line": "cd_fpa",
    "fix.shift.template": "cd_attendance",
}

# The record each page lists (its grid).
RECORDS = {
    "1": "fix.branch",
    "2": "fix.entity",
    "3": "fix.feature.flag",
    "4": "fix.working.calendar",
    "5": "fix.platform.announcement",
    "6": "fix.dofa.ladder",
}

# Odoo's own tables, shown as inventories: a person never types one here.
SYSTEM_WRITTEN = ("M30-config", "M30-crons")

# The models the capture audits built (cd_entity_config/models/fix_platform_ops3/4.py).
NEW_MODELS = (
    "fix.scheduled.job",
    "fix.config.parameter",
    "fix.config.change",
    "fix.backup.verification",
    "fix.dr.drill",
    "fix.org.change",
    "fix.component.licence",
    "fix.platform.alert",
    "fix.capacity.metric",
)
# Operational information every internal user may read (a maintenance window,
# a freeze, a runbook, what a branch can do); only a Platform Admin writes them.
NEW_PUBLIC_MODELS = (
    "fix.branch.capability",
    "fix.change.freeze",
    "fix.maintenance.window",
    "fix.runbook",
)


@pytest.fixture(scope="module")
def m30(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m30_capture")
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
    """SURFACES / WRITABLE / REPORTS of controllers/a12/m30.py, read without Odoo."""
    tree = ast.parse(CONTROLLER.read_text(encoding="utf-8"))
    out = {"REPORTS": set()}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
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
                out["REPORTS"] |= {ast.literal_eval(k) for k in node.value.keys}
        # REPORTS["x"] = fn
        if (
            isinstance(node, ast.Assign)
            and isinstance(node.targets[0], ast.Subscript)
            and isinstance(node.targets[0].value, ast.Name)
            and node.targets[0].value.id == "REPORTS"
        ):
            out["REPORTS"].add(ast.literal_eval(node.targets[0].slice))
    return out


def _sub(m30, no):
    return next(s for s in m30["subs"] if s["no"] == no)


def test_every_page_is_classified(m30):
    assert sorted(s["no"] for s in m30["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m30, no):
    sub = _sub(m30, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]}
    missing = [form for form in [own, *others] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)
    for f in sub["forms"]:
        assert f["kind"] == "model_form", "chip %s opens %s" % (f["f"], f["kind"])


@pytest.mark.parametrize("no", sorted(RECORDS, key=int))
def test_each_page_lists_its_own_record(m30, no):
    assert _sub(m30, no)["model"] == RECORDS[no]


def test_each_captured_record_is_listed_on_its_page(m30):
    """A capture lands on a list of the page it was made from."""
    for sub in m30["subs"]:
        listed = {m30["screens"][s]["model"] for s in sub["screens"] if s in m30["screens"]}
        for f in sub["forms"]:
            assert f["model"] in listed, "page %s captures %s but lists no such record" % (
                sub["no"],
                f["model"],
            )


def test_every_working_screen_sits_on_a_page(m30):
    """Every list, and every report screen the module's nav or report chips
    reach, is on some sub-module page."""
    placed = {sid for s in m30["subs"] for sid in s["screens"]}
    placed |= {r["route"] for s in m30["subs"] for r in s["reports"]}
    orphans = [
        sid
        for sid, cfg in m30["screens"].items()
        if cfg["kind"] in ("model_list", "table_report") and sid not in placed
    ]
    assert not orphans, orphans


def test_backup_screen_is_the_platform_register_not_customer_plans(m30):
    assert m30["screens"]["M30-backup"]["model"] == "fix.backup.verification"
    assert "fix.data.backup.plan" not in {c["model"] for c in m30["screens"].values()}


def test_registry_screens_are_the_registers(m30):
    assert m30["screens"]["M30-params"]["model"] == "fix.config.parameter"
    assert m30["screens"]["M30-jobs"]["model"] == "fix.scheduled.job"
    # Odoo's own tables stay visible as read-only inventories
    for sid in SYSTEM_WRITTEN:
        assert m30["screens"][sid]["create"] is False, sid


def test_every_page_report_opens_its_pack(m30):
    reports = _controller()["REPORTS"]
    for sub in m30["subs"]:
        for r in sub["reports"]:
            assert r["route"], "page %s report %s has no route" % (sub["no"], r["r"])
            assert m30["screens"][r["route"]]["report"] in reports, r


def test_a_list_offering_new_opens_a_form_of_its_own_model(m30):
    for sid, cfg in m30["screens"].items():
        if cfg["kind"] != "model_list" or cfg.get("create") is False:
            continue
        form = m30["by_screen"].get(sid)
        assert form, "%s offers + New but opens no form" % sid
        assert m30["screens"][form]["model"] == cfg["model"], sid


def test_every_row_action_is_served(m30):
    surfaces = _controller()["SURFACES"]
    for sid, cfg in m30["screens"].items():
        for act in cfg["actions"]:
            assert act["m"] in surfaces[cfg["model"]], "%s %s is not served" % (sid, act["m"])


def _served_elsewhere(model):
    """A surface may be declared by ONE area only; a foreign record is served by
    the controller of the module that masters it."""
    pattern = re.compile(r'^\s*"%s":\s*\{' % re.escape(model), re.M)
    for path in (HERE.parent / "controllers").rglob("*.py"):
        if path != CONTROLLER and pattern.search(path.read_text(encoding="utf-8")):
            return True
    return False


def test_every_listed_model_is_served(m30):
    surfaces = _controller()["SURFACES"]
    for sid, cfg in m30["screens"].items():
        if cfg["kind"] in ("model_list", "model_form"):
            if cfg["model"] in FOREIGN:
                assert cfg["model"] not in surfaces, "M30 would declare %s twice" % cfg["model"]
                assert cfg["kind"] == "model_list" and cfg["create"] is False, sid
                assert _served_elsewhere(cfg["model"]), cfg["model"]
                continue
            assert cfg["model"] in surfaces, "%s reads %s, which M30 does not serve" % (
                sid,
                cfg["model"],
            )


def test_foreign_chips_are_writable_by_a_platform_admin():
    addons = HERE.parents[2]
    for model, module in FOREIGN.items():
        acl = next(addons.rglob("%s/security/ir.model.access.csv" % module)).read_text(
            encoding="utf-8"
        )
        ref = "model_" + model.replace(".", "_")
        row = [
            line
            for line in acl.splitlines()
            if ",%s,cd_entity_config.group_platform_admin," % ref in line
        ]
        assert row and row[0].strip().split(",")[-3:-1] == ["1", "1"], model


def test_every_editable_form_field_is_writable(m30):
    """A field a form lets the user type saves through the write whitelist."""
    writable = _controller()["WRITABLE"]
    for sid, cfg in m30["screens"].items():
        if cfg["kind"] != "model_form":
            continue
        editable = {f["name"] for f in cfg["fields"] if not f["readonly"]}
        lost = editable - set(writable[cfg["model"]])
        assert not lost, "%s cannot save %s" % (sid, sorted(lost))


def test_workflow_stamps_are_never_typed(m30):
    """State, previous value and sign-off stamps move only through the actions."""
    writable = _controller()["WRITABLE"]
    stamps = {
        "fix.config.change": {
            "state",
            "previous_value",
            "proposed_by_id",
            "applied_by_id",
            "applied_on",
            "closed_by_id",
            "closed_on",
            "close_reason",
        },
        "fix.dr.drill": {"state", "signed_off_by_id", "signed_off_on", "rpo_met", "rto_met"},
        "fix.backup.verification": {"tested_by_id"},
        "fix.scheduled.job": {"cron_active", "last_run", "next_run", "run_state", "schedule"},
        "fix.config.parameter": {"current_value"},
        "fix.org.change": {
            "state",
            "previous_state",
            "proposed_by_id",
            "approved_by_id",
            "approved_on",
            "applied_on",
            "reject_reason",
        },
        "fix.change.freeze": {"declared_by_id", "lifted_by_id", "lift_reason", "status"},
        "fix.maintenance.window": {
            "state",
            "announcement_id",
            "actual_from",
            "actual_to",
            "overran",
            "planned_minutes",
        },
        "fix.capacity.metric": {"reviewed_by_id", "headroom_pct", "projected_exhaustion"},
        "fix.runbook": {"next_review_due"},
    }
    stamps["fix.config.change"] |= {"regularise_by", "regularised_on"}
    for model, names in stamps.items():
        assert not names & set(writable[model]), model
    for sid, cfg in m30["screens"].items():
        if cfg["kind"] == "model_form" and cfg["model"] in stamps:
            shown = {f["name"]: f for f in cfg["fields"]}
            for name in stamps[cfg["model"]] & set(shown):
                assert shown[name]["readonly"], "%s lets %s be typed" % (sid, name)


def test_odoo_tables_stay_unwritable():
    writable = _controller()["WRITABLE"]
    assert writable["ir.config_parameter"] == ()
    assert writable["ir.cron"] == ()


def test_long_forms_are_tabbed(m30):
    """Workspace standard: a form with more than 15 fields is split into tabs,
    and every section names a declared tab (an undeclared tab is invisible)."""
    for sid, cfg in m30["screens"].items():
        if cfg["kind"] != "model_form" or sid not in {c for v in CAPTURES.values() for c in v}:
            continue
        if len(cfg["fields"]) > 15:
            assert cfg["tabs"], "%s has %d fields and no tabs" % (sid, len(cfg["fields"]))
        for section in cfg["sections"]:
            if cfg["tabs"]:
                assert section["tab"] in cfg["tabs"], sid


def test_new_models_have_access_rows_and_company_rules():
    root = HERE.parents[1] / "cd_entity_config"
    acl = (root / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    rules = (root / "security" / "fix_isolation_rules.xml").read_text(encoding="utf-8")
    for model in NEW_MODELS + NEW_PUBLIC_MODELS:
        ref = "model_" + model.replace(".", "_")
        assert ",%s,cd_entity_config.group_platform_admin," % ref in acl, model
        assert 'ref="%s"' % ref in rules, model
        users = [line for line in acl.splitlines() if ",%s,base.group_user," % ref in line]
        if model in NEW_MODELS:
            assert not users, "%s is readable by every user" % model
        else:
            assert users and users[0].strip().endswith(",1,0,0,0"), model


def test_the_new_kpis_are_served(m30):
    assert {"config_changes_pending", "jobs_missed"} <= set(m30["kpis"])
    text = CONTROLLER.read_text(encoding="utf-8")
    assert 'out["config_changes_pending"]' in text
    assert 'out["jobs_missed"]' in text
    assert {"emergency_open", "maintenance_upcoming"} <= set(m30["kpis"])
    assert 'out["emergency_open"]' in text
    assert 'out["maintenance_upcoming"]' in text
