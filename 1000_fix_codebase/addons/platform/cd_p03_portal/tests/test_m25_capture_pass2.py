# M25 second capture pass (2026-11-19): each sub-module page captures the
# record the spec names for it (M25 spec §5 / §10), not just "a" record.
#
# Before (14 Nov state):
#   p1 Role Dashboards    no annotation (FR-BID-009); the dashboard had no
#                         business owner (BRU-BID-07) and nothing recorded the
#                         steward's verification (§8.1, BRU-BID-10)
#   p2 Report Library     "+ New Distribution Schedule": no library entry with
#                         owner/definition/certification (FR-BID-011), no run
#                         stamp or restatement flag (FR-BID-017)
#   p3 Self-Service       "+ Dashboard": no saved exploration (FR-BID-018/019)
#   p4 Distribution       an alert stamped a time; nothing was raised,
#                         acknowledged or escalated (FR-BID-025/026)
#   p5 Embedded           "+ New Sync Connection": no embedded chart
#                         placement or token (FR-BID-029, T-08)
#   p6 Mobile             "+ Dashboard": no low-bandwidth delivery (FR-BID-028)
#   p7 Lifecycle & Usage  no usage telemetry (FR-BID-033)
#
# The page rule is JavaScript (p03_workspace.js fregCreate / fregPanels), so it
# is EXECUTED in node over the real registry; the saves run through the same
# endpoints the forms use, as non-admin users.
from __future__ import annotations

import ast
import itertools
import json
import re
import shutil
import subprocess
from pathlib import Path
from unittest import mock

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_p03_portal.controllers.a11 import m25 as m25_ctl

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "static" / "src"
CONTROLLER = HERE.parent / "controllers" / "a11" / "m25.py"
IMPORT = re.compile(r'from\s+"(\./a\d\d/\w+)"')

AUTHOR = "cd_bi_reporting.group_bi_author"
CERTIFIER = "cd_bi_reporting.group_bi_certifier"

_SEQ = itertools.count(1)


def _method(name):
    return re.compile(r"^    (" + name + r"\(mid, (?:mod, )?map\) \{\n.*?\n    \})\n", re.S | re.M)


PROBE = """
import * as M from './meta.mjs';
const { P03_MODULES, P03_MODULE_CREATE, P03_FORM_CHIPS, P03_DATA_SCREENS } = M;
function %s
function %s
const mod = P03_MODULES.M25;
const subs = mod.freg.sub.map((s) => ({ no: s[0], title: s[1], map: s[3] || null,
  create: fregCreate('M25', s[3] || null), panels: fregPanels('M25', mod, s[3] || null) }));
console.log(JSON.stringify({ subs,
  chips: Object.fromEntries(Object.entries(P03_FORM_CHIPS).filter(([k]) => k.startsWith('M25:'))),
  nav: mod.groups.flatMap((g) => g.screens.map((s) => s.id)),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([k]) => k.startsWith('M25-'))) }));
"""


@pytest.fixture(scope="module")
def m25(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m25_pass2")
    for area in sorted(d for d in SRC.iterdir() if re.fullmatch(r"a\d\d", d.name)):
        (tmp / area.name).mkdir()
        for js in area.glob("*.js"):
            (tmp / area.name / (js.stem + ".mjs")).write_text(
                js.read_text(encoding="utf-8"), "utf-8"
            )
    meta = (SRC / "p03_modules_meta.js").read_text(encoding="utf-8")
    (tmp / "meta.mjs").write_text(IMPORT.sub(r'from "\1.mjs"', meta), "utf-8")
    ws = (SRC / "p03_workspace.js").read_text(encoding="utf-8").replace("\r\n", "\n")
    create, panels = _method("fregCreate").search(ws), _method("fregPanels").search(ws)
    assert create and panels, "p03_workspace.js no longer defines fregCreate / fregPanels"
    probe = tmp / "probe.mjs"
    probe.write_text(PROBE % (create.group(1), panels.group(1)), "utf-8")
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our own probe file
        [node, str(probe)], capture_output=True, encoding="utf-8", check=True, timeout=60
    )
    return json.loads(out.stdout)


def _sub(m25, no):
    return next(s for s in m25["subs"] if s["no"] == no)


def _surfaces():
    tree = ast.parse(CONTROLLER.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "SURFACES":
            return ast.literal_eval(node.value)
    raise AssertionError("m25.py no longer declares SURFACES")


# --- what each page offers ------------------------------------------------------

# page -> (list screen on the page, form its + New / chip opens, model)
NEW = {
    "1": ("M25-annotations", "M25-form-annotation", "fix.bi.annotation"),
    "2": ("M25-reportdefs", "M25-form-reportdef", "fix.bi.report.definition"),
    "3": ("M25-explorations", "M25-form-exploration", "fix.bi.exploration"),
    "4": ("M25-alert-raised", None, "fix.bi.alert.instance"),
    "5": ("M25-embedded", "M25-form-embedded", "fix.bi.embedded.surface"),
    "7": ("M25-usage", None, "fix.bi.content.usage"),
}


@pytest.mark.parametrize("no", sorted(NEW))
def test_each_page_shows_its_new_register(m25, no):
    screen, form, model = NEW[no]
    sub = _sub(m25, no)
    assert screen in sub["map"]["screens"], (no, sub["map"]["screens"])
    assert screen in m25["nav"], "%s is reachable from no navigation group" % screen
    assert m25["screens"][screen]["model"] == model
    if form:
        assert m25["chips"]["M25:__by_screen__"][screen] == form
        assert m25["screens"][form]["model"] == model


@pytest.mark.parametrize(
    ("no", "form"),
    [
        ("2", "M25-form-reportdef"),
        ("3", "M25-form-exploration"),
        ("5", "M25-form-embedded"),
    ],
)
def test_the_primary_button_opens_the_spec_record(m25, no, form):
    assert _sub(m25, no)["create"]["screen"] == form


def test_the_mobile_page_captures_a_low_bandwidth_summary(m25):
    sub = _sub(m25, "6")
    assert sub["map"]["domain"] == [["channel", "=", "low_bandwidth"]]
    create = sub["create"]
    assert create["screen"] == "M25-form-schedule"
    assert create["label"] == "New Low-Bandwidth Summary" and create["verbatim"]
    # the new summary starts with the page's own filter filled in
    assert create["presets"] == {"channel": "low_bandwidth"}


def test_system_written_registers_offer_no_new(m25):
    for screen in ("M25-runs", "M25-alert-raised", "M25-usage"):
        assert m25["screens"][screen]["create"] is False, screen


def test_every_new_action_is_served_with_its_asks(m25):
    served = {m: set(c.get("actions") or ()) for m, c in _surfaces().items()}
    for sid, cfg in m25["screens"].items():
        for act in cfg.get("actions") or []:
            assert act["m"] in served.get(cfg["model"], set()), (sid, act["m"])
    asks = {
        ("M25-builder", "action_steward_verify"): "note",
        ("M25-runs", "action_flag_restatement"): "reference",
        ("M25-alert-raised", "action_acknowledge"): "note",
        ("M25-alert-raised", "action_close"): "note",
    }
    for (sid, method), kwarg in asks.items():
        act = next(a for a in m25["screens"][sid]["actions"] if a["m"] == method)
        assert kwarg in [a["kwarg"] for a in act["asks"]], (sid, method)


def test_metric_and_role_choices_are_the_servers(m25, odoo_env):
    bank = set(m25_ctl._metrics(odoo_env(su=True)))
    roles = {k for k, _ in odoo_env["fix.bi.dashboard"]._fields["role"].selection}
    for form, names in {
        "M25-form-annotation": ("metric_key",),
        "M25-form-exploration": ("metric_key", "metric_key_2", "metric_key_3"),
        "M25-form-embedded": ("metric_key", "metric_key_2"),
    }.items():
        fields = {f["name"]: f for s in m25["screens"][form]["sections"] for f in s["fields"]}
        for name in names:
            assert {k for k, _ in fields[name]["choices"]} == bank, (form, name)
    for form, name in (("M25-form-annotation", "role"), ("M25-form-exploration", "target_role")):
        fields = {f["name"]: f for s in m25["screens"][form]["sections"] for f in s["fields"]}
        assert {k for k, _ in fields[name]["choices"]} == roles, (form, name)


def test_a_form_over_fifteen_fields_is_tabbed(m25):
    for sid, cfg in m25["screens"].items():
        if cfg.get("kind") != "model_form":
            continue
        count = sum(len(s["fields"]) for s in cfg["sections"])
        if count > 15:
            tabs = {t["id"] for t in cfg.get("tabs") or []}
            assert tabs, "%s has %d fields on one scroll" % (sid, count)
            assert all(s.get("tab") in tabs for s in cfg["sections"]), sid


def test_no_m25_form_leaves_out_a_field_its_model_requires(m25, odoo_env):
    """A required field with no default that the form does not show can never
    be sent: every save of that form is refused."""
    missing = []
    for sid, cfg in m25["screens"].items():
        if cfg.get("kind") != "model_form":
            continue
        model = odoo_env[cfg["model"]]
        shown = {f["name"] for s in cfg["sections"] for f in s["fields"]}
        defaults = model.default_get(list(model._fields))
        for name, field in model._fields.items():
            if (
                field.required
                and not field.compute
                and not field.related
                and name not in defaults
                and name not in shown
                and field.type not in ("one2many", "many2many")
            ):
                missing.append("%s.%s" % (sid, name))
    assert not missing, missing


# --- the saves, through the endpoints the forms use -------------------------------


class FakeHttpRequest:
    headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 13) Mobile Safari/537.36"}


class FakeRequest:
    def __init__(self, env):
        self.env = env
        self.httprequest = FakeHttpRequest()


@pytest.fixture
def env(odoo_env):
    if "fix.bi.report.definition" not in odoo_env:
        pytest.skip("cd_bi_reporting 19.0.0.4.0 is not installed")
    return odoo_env


@pytest.fixture
def call():
    patchers = []

    def _call(env, route, **kw):
        for module in (api, m25_ctl):
            p = mock.patch.object(module, "request", FakeRequest(env))
            p.start()
            patchers.append(p)
        if route == "bi_role":
            return m25_ctl.P03BiApi().bi_role(**kw)
        if route == "bi_embed_token":
            return m25_ctl.P03BiApi().bi_embed_token(**kw)
        return getattr(api.P03GenericApiController(), route)(**kw)

    yield _call
    for p in patchers:
        p.stop()


def _user(env, *xmlids):
    n = next(_SEQ)
    groups = [env.ref("base.group_user").id] + [env.ref(x).id for x in xmlids]
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "M25 Pass2 User %d" % n,
                "login": "m25.pass2.%d@a11.test" % n,
                "email": "m25.pass2.%d@a11.test" % n,
                "group_ids": [(6, 0, groups)],
            }
        )
    )
    return env(user=user.id)


def _ok(res):
    assert "id" in res, res
    return res["id"]


def _act(call, who, model, rid, method, **kwargs):
    return call(who, "model_action", model=model, ids=[rid], method=method, kwargs=kwargs or None)


def test_p1_owner_steward_and_annotation_round_trip(call, env):
    author, steward, owner = _user(env, AUTHOR), _user(env, CERTIFIER), _user(env, AUTHOR)
    emp = env["hr.employee"].create({"name": "Pass2 Steward"})
    dash_id = _ok(
        call(
            author,
            "model_write",
            model="fix.bi.dashboard",
            values={
                "name": "Branch cockpit",
                "name_bn": "শাখা ককপিট",
                "role": "coo",
                "tier": "branch",
                "steward_id": emp.id,
                "business_owner_id": owner.uid,
                "decision_supported": "Supervisor visits",
                "review_cycle": "monthly",
            },
        )
    )
    model = "fix.bi.dashboard"
    assert _act(call, author, model, dash_id, "action_submit_review").get("success")
    early = _act(call, author, model, dash_id, "action_request_approval", justification="x")
    assert not early.get("success") and "BRU-BID-10" in early["error"], early
    assert _act(call, steward, model, dash_id, "action_steward_verify", note="Bengali ok").get(
        "success"
    )
    assert env[model].browse(dash_id).verified_by.id == steward.uid

    note_id = _ok(
        call(
            owner,
            "model_write",
            model="fix.bi.annotation",
            values={
                "name": "Eid closures",
                "role": "coo",
                "dashboard_id": dash_id,
                "metric_key": "delivered_mtd",
                "period": "2026-11",
                "text_en": "Branches closed for Eid",
            },
        )
    )
    assert env["fix.bi.annotation"].browse(note_id).author_id.id == owner.uid
    cockpit = call(author, "bi_role", role="coo")
    assert any("Eid closures" in n for n in cockpit["notes"]), cockpit["notes"]


def test_p2_library_entry_certified_run_and_restatement(call, env):
    # the registering author also holds the steward hat: still not the certifier
    author, steward, owner = _user(env, AUTHOR, CERTIFIER), _user(env, CERTIFIER), _user(env)
    rid = _ok(
        call(
            author,
            "model_write",
            model="fix.bi.report.definition",
            values={
                "report_key": "M25:service_kpi_pack",
                "name": "Service KPI Pack",
                "owning_module": "M25",
                "business_owner_id": owner.uid,
                "definition": "Service throughput and SLA for service heads",
                "layout_type": "analytical",
            },
        )
    )
    model = "fix.bi.report.definition"
    refused = _act(call, author, model, rid, "action_certify")
    assert not refused.get("success") and "independent" in refused["error"], refused
    assert _act(call, steward, model, rid, "action_certify").get("success")
    gen = _act(call, author, model, rid, "action_generate_run", date_from="2026-11-01")
    assert gen.get("success"), gen
    run = env["fix.bi.report.run"].search([("definition_id", "=", rid)])
    assert len(run) == 1 and run.definition_certified and run.requested_by.id == author.uid
    assert _act(
        call,
        steward,
        "fix.bi.report.run",
        run.id,
        "action_flag_restatement",
        reference="M62/RST/2026/7",
    ).get("success")
    assert run.restatement_flag
    lib = call(author, "model_report", module="M25", report="report_library")
    row = next(r for r in lib["rows"] if r["key"] == "M25:service_kpi_pack")
    assert row["owner"] == owner.user.name and row["certification"] == "Certified"
    assert "owner" in lib["cols"] and "certification" in lib["cols"]


def test_p3_exploration_saved_run_and_promoted(call, env):
    author, peer = _user(env, AUTHOR), _user(env, AUTHOR)
    eid = _ok(
        call(
            author,
            "model_write",
            model="fix.bi.exploration",
            values={
                "name": "QC failures by week",
                "question": "Are QC failures rising?",
                "metric_key": "qc_failed",
                "target_role": "quality",
            },
        )
    )
    model = "fix.bi.exploration"
    hijack = _act(call, peer, model, eid, "action_promote")
    assert not hijack.get("success"), hijack
    assert _act(call, author, model, eid, "action_run").get("success")
    assert _act(call, author, model, eid, "action_promote").get("success")
    exp = env[model].browse(eid)
    assert exp.state == "promoted" and exp.dashboard_id.state == "draft"


def test_p4_raised_alert_acknowledged_from_the_list(call, env, monkeypatch):
    owner, recipient = _user(env, AUTHOR), _user(env)
    alert = env["fix.bi.alert.subscription"].create(
        {
            "name": "QC failures",
            "metric_key": "qc_failed",
            "comparator": "gt",
            "threshold": 3,
            "recipients": recipient.user.login,
            "owner_id": owner.uid,
        }
    )
    monkeypatch.setattr(type(alert), "_current_value", lambda self: 9.0)
    alert._evaluate()
    inst = alert.instance_ids
    assert len(inst) == 1
    stranger = _user(env)
    assert not _act(
        call, stranger, "fix.bi.alert.instance", inst.id, "action_acknowledge", note="x"
    ).get("success")
    assert _act(
        call,
        recipient,
        "fix.bi.alert.instance",
        inst.id,
        "action_acknowledge",
        note="re-testing the failed units",
    ).get("success")
    assert inst.state == "acknowledged"


def test_p5_embedded_surface_saved_activated_and_tokened(call, env):
    author, steward, viewer = _user(env, AUTHOR), _user(env, CERTIFIER), _user(env)
    sid = _ok(
        call(
            author,
            "model_write",
            model="fix.bi.embedded.surface",
            values={
                "name": "Backlog on the WIP board",
                "host_module": "M02",
                "host_screen": "M02-wip",
                "metric_key": "in_repair",
                "audience": "internal",
                "context_binding": "scope",
                "token_ttl_seconds": 120,
            },
        )
    )
    early = call(viewer, "bi_embed_token", surface_id=sid)
    assert "error" in early, early
    assert _act(call, steward, "fix.bi.embedded.surface", sid, "action_activate").get("success")
    issued = call(viewer, "bi_embed_token", surface_id=sid)
    assert issued.get("token") and issued["expires_in"] == 120, issued
    payload = env["fix.bi.embedded.surface"].with_user(viewer.uid)._redeem_token(issued["token"])
    assert payload["u"] == viewer.uid


def test_p6_low_bandwidth_summary_saved_from_the_mobile_page(call, env):
    author = _user(env, AUTHOR)
    sid = _ok(
        call(
            author,
            "model_write",
            model="fix.bi.distribution.schedule",
            values={
                "name": "Rangpur branch summary",
                "report_key": "M25:branch_league",
                "cadence": "daily",
                "recipients": author.user.login,
                "channel": "low_bandwidth",
                "format": "csv",
            },
        )
    )
    assert env["fix.bi.distribution.schedule"].browse(sid).channel == "low_bandwidth"


def test_p7_a_cockpit_view_is_logged_with_its_device(call, env):
    viewer, steward = _user(env), _user(env, CERTIFIER)
    call(viewer, "bi_role", role="service")
    rows = call(
        steward,
        "model_records",
        model="fix.bi.content.usage",
        domain=[["user_id", "=", viewer.uid]],
        cols=["content_ref", "device_class"],
    )
    recs = rows.get("rows") or []
    assert recs and recs[0]["content_ref"] == "M25:service", rows
    device = recs[0]["device_class"]
    assert (device.get("key") if isinstance(device, dict) else device) == "mobile", recs[0]
    # a plain user does not read who viewed what
    assert "error" in call(
        viewer, "model_records", model="fix.bi.content.usage", cols=["content_ref"]
    )
