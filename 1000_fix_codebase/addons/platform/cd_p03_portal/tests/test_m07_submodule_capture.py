# M07 CRM & Sales Pipeline: every Function Register sub-module page captures
# what its function records, and the capture saves the right record.
#
# Reported 2026-11-13: "not all the sub-modules have a relevant data capture
# button". Measured against the M07 spec (FR-CRM-001..046) and the code:
#   - 3 of 10 pages had no button: Activities, Cross-Sell / Upsell,
#     Competitor Intelligence;
#   - 3 of the 7 that had one saved the wrong thing:
#       "+ New Lead" saved an OPPORTUNITY (no user holds crm.group_use_lead,
#         the form's `type: lead` was read-only so it was never sent);
#       "+ New Forecast Snapshot" froze a snapshot of zeros and its unique
#         key then kept the scheduler's real snapshot out;
#       the Activity form edited a lead's computed next-activity fields
#         (every due date refused) and, opened blank, created a lead;
#   - the key-account master and its stakeholder map (FR-CRM-028/029) were
#     built but served by no screen; a lead could not become an opportunity.
#
# The page rule is JavaScript (p03_workspace.js fregCreate), so it is
# EXECUTED in node over the real registry; the saves run through the same
# endpoint the forms use, as a salesperson (not the superuser).
from __future__ import annotations

import datetime
import json
import re
import shutil
import subprocess
from pathlib import Path
from unittest import mock

import pytest
from odoo.addons.cd_p03_portal.controllers import form_fields
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api

SRC = Path(__file__).resolve().parents[1] / "static" / "src"
IMPORT = re.compile(r'from\s+"(\./a\d\d/\w+)"')
FREG_CREATE = re.compile(r"^    (fregCreate\(mid, map\) \{\n.*?\n    \})\n", re.S | re.M)

PROBE = """
import * as M from './meta.mjs';
const { P03_MODULES, P03_MODULE_CREATE, P03_FORM_CHIPS, P03_DATA_SCREENS } = M;
function %s
const subs = P03_MODULES.M07.freg.sub.map((s) => ({ no: s[0], title: s[1], map: s[3] || null,
  create: fregCreate('M07', s[3] || null) }));
console.log(JSON.stringify({ subs, create: P03_MODULE_CREATE.M07 || null,
  chips: Object.fromEntries(Object.entries(P03_FORM_CHIPS).filter(([k]) => k.startsWith('M07:'))),
  moduleForms: P03_MODULES.M07.forms,
  nav: P03_MODULES.M07.groups.flatMap((g) => g.screens.map((s) => s.id)),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([k]) => k.startsWith('M07-'))) }));
"""


@pytest.fixture(scope="module")
def m07(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m07_capture")
    for area in sorted(d for d in SRC.iterdir() if re.fullmatch(r"a\d\d", d.name)):
        (tmp / area.name).mkdir()
        for js in area.glob("*.js"):
            (tmp / area.name / (js.stem + ".mjs")).write_text(
                js.read_text(encoding="utf-8"), "utf-8"
            )
    meta = (SRC / "p03_modules_meta.js").read_text(encoding="utf-8")
    (tmp / "meta.mjs").write_text(IMPORT.sub(r'from "\1.mjs"', meta), "utf-8")
    method = FREG_CREATE.search(
        (SRC / "p03_workspace.js").read_text(encoding="utf-8").replace("\r\n", "\n")
    )
    assert method, "p03_workspace.js no longer defines fregCreate(mid, map)"
    probe = tmp / "probe.mjs"
    probe.write_text(PROBE % method.group(1), "utf-8")
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our own probe file
        [node, str(probe)], capture_output=True, encoding="utf-8", check=True, timeout=60
    )
    return json.loads(out.stdout)


def _sub(m07, no):
    return next(s for s in m07["subs"] if s["no"] == no)


# --- what each page offers -----------------------------------------------------

EXPECTED = {
    "1": ("M07-form-lead", "Lead"),
    "2": {"module": True},  # + New Opportunity
    "3": ("M07-form-forecast", "Take a Forecast Snapshot"),
    "4": ("M07-form-plan", "Account Plan"),
    "5": ("M07-form-assignment", "Account Assignment"),
    "6": ("M07-form-qbr", "Quarterly Business Review (QBR)"),
    "7": ("M07-form-activity", "Log a Call, Visit or Meeting"),
    "8": ("M07-form-renewal", "Contract Renewal Pursuit"),
    "9": ("M07-form-opp", "Commercial Opportunity & B2B KAM"),
    "10": ("M07-form-competitor", "Record Competitor Intelligence"),
}


def test_the_scan_sees_ten_submodules(m07):
    assert [s["no"] for s in m07["subs"]] == [str(n) for n in range(1, 11)]


@pytest.mark.parametrize("no", sorted(EXPECTED, key=int))
def test_each_submodule_page_offers_its_capture(m07, no):
    sub = _sub(m07, no)
    want = EXPECTED[no]
    got = sub["create"]
    if isinstance(want, dict):
        assert got == want, "%s/%s offers %s" % (no, sub["title"], got)
        return
    assert got, "%s/%s offers no capture button" % (no, sub["title"])
    assert (got.get("screen"), got.get("label")) == want, "%s/%s offers %s" % (
        no,
        sub["title"],
        got,
    )


def test_the_module_button_raises_an_opportunity(m07):
    assert m07["create"] == {"screen": "M07-form-opp", "model": "crm.lead", "label": "Opportunity"}


def test_a_cross_sell_starts_ticked(m07):
    """The page lists cross-sell opportunities only, and the record made from
    it starts with the flag (and the opportunity type) filled in."""
    sub = _sub(m07, "9")
    assert ["is_cross_sell", "=", True] in sub["map"]["domain"]
    assert sub["create"]["presets"] == {"type": "opportunity", "is_cross_sell": True}


def test_every_capture_form_is_on_its_page_and_chip(m07):
    """'Forms Capturing It' lists the form the button opens, and the chip
    opens that same form; every module form has a chip."""
    for sub in m07["subs"]:
        screen = sub["create"] and sub["create"].get("screen")
        if not screen:
            continue
        names = [n for n in sub["map"]["forms"] if m07["chips"].get("M07:" + n) == screen]
        assert names, "%s/%s: no chip opens %s" % (sub["no"], sub["title"], screen)
    assert set(m07["moduleForms"]) == {k[4:] for k in m07["chips"] if "__" not in k}


def test_the_new_surfaces_are_on_the_navigation(m07):
    assert {"M07-key-accounts", "M07-form-account", "M07-form-competitor"} <= set(m07["nav"])


def test_the_activity_form_logs_an_activity_not_a_lead(m07):
    cfg = m07["screens"]["M07-form-activity"]
    assert cfg["model"] == "fix.sales.activity"
    assert m07["screens"]["M07-activities"]["model"] == "fix.sales.activity"
    assert m07["screens"]["M07-activities"].get("create") is not False


def test_the_lead_form_posts_its_type(m07):
    """A fixed value the server accepts: not read-only, so it is sent."""
    fields = [f for s in m07["screens"]["M07-form-lead"]["sections"] for f in s["fields"]]
    field = next(f for f in fields if f["name"] == "type")
    assert field.get("value") == "lead" and not field.get("readonly")
    assert "type" in api.SURFACES["crm.lead"]["writable"]


def test_the_capture_forms_bind_real_fields(m07, odoo_env):
    """A form field or a pick column the model lacks is dropped silently by
    /p03/model/form and /p03/model/records - it would just not appear."""
    bad = []
    for sid, cfg in m07["screens"].items():
        model = cfg.get("model")
        if not model or model not in odoo_env:
            continue
        fields = odoo_env[model]._fields
        names = list(cfg.get("cols", []))
        names += [f["name"] for s in cfg.get("sections", []) for f in s["fields"]]
        pick = cfg.get("pickRecord") or {}
        names += pick.get("cols", []) + [c[0] for c in pick.get("domain", [])]
        lines = cfg.get("lines")
        if lines:
            names.append(lines["field"])
            child = odoo_env[fields[lines["field"]].comodel_name]._fields
            bad += [
                "%s.%s.%s" % (sid, lines["field"], f["name"])
                for f in lines["fields"]
                if f["name"] not in child
            ]
        bad += ["%s.%s" % (sid, n) for n in names if n not in fields]
    for sub in m07["subs"]:
        fields = odoo_env[sub["map"]["model"]]._fields
        bad += ["sub %s.%s" % (sub["no"], c) for c in sub["map"]["cols"] if c not in fields]
    assert not bad, bad


def test_the_list_actions_are_served(m07):
    for sid, cfg in m07["screens"].items():
        for act in cfg.get("actions", []):
            assert act["m"] in api.SURFACES[cfg["model"]]["actions"], (sid, act["m"])


def test_the_whitelist_matches_the_forms():
    offered = {}
    for area, _sid, model, editable in form_fields.forms():
        if area == "a03":
            offered.setdefault(model, set()).update(editable)
    for model in ("crm.lead", "fix.sales.activity", "fix.account"):
        assert offered[model] == set(api.SURFACES[model]["writable"]), model
    # the lead's computed next-activity fields are no longer offered
    assert not {"activity_date_deadline", "activity_summary"} & offered["crm.lead"]


# --- the saves, through the endpoint the forms use -----------------------------


class FakeRequest:
    def __init__(self, env):
        self.env = env


@pytest.fixture
def call():
    patchers = []

    def _call(env, route, **kw):
        p = mock.patch.object(api, "request", FakeRequest(env))
        p.start()
        patchers.append(p)
        return getattr(api.P03GenericApiController(), route)(**kw)

    yield _call
    for p in patchers:
        p.stop()


@pytest.fixture
def crm(odoo_env):
    """A salesperson, a customer and the standard pipeline."""
    env = odoo_env
    groups = [env.ref("base.group_user").id, env.ref("sales_team.group_sale_salesman").id]
    user = (
        env["res.users"]
        .with_context(no_reset_password=True, mail_create_nosubscribe=True)
        .create(
            {
                "name": "M07 Capture Seller",
                "login": "m07.capture.seller@example.invalid",
                "email": "m07.capture.seller@example.invalid",
                "group_ids": [(6, 0, groups)],
            }
        )
    )
    partner = env["res.partner"].create({"name": "M07 Capture Bank Ltd", "is_company": True})
    pipeline = env.ref("cd_crm_ext.pipeline_standard")
    return env(user=user), partner, pipeline


def _form_values(m07, sid, **typed):
    """What the form posts on create: its fixed values, then what was typed."""
    values = {}
    for section in m07["screens"][sid]["sections"]:
        for field in section["fields"]:
            if "value" in field:
                values[field["name"]] = field["value"]
    values.update(typed)
    return values


def _ok(res):
    assert "error" not in res, res
    return res["id"]


def test_new_lead_saves_a_lead_on_the_leads_list(m07, crm, call):
    env, partner, _pipeline = crm
    rid = _ok(
        call(
            env,
            "model_write",
            model="crm.lead",
            record_id=False,
            values=_form_values(m07, "M07-form-lead", name="ATM fleet AMC", partner_id=partner.id),
        )
    )
    lead = env["crm.lead"].browse(rid)
    assert lead.type == "lead"
    assert lead in env["crm.lead"].search(m07["screens"]["M07-leads"]["domain"])


def test_a_saved_lead_changes_type_only_by_conversion(crm, call):
    env, _partner, _pipeline = crm
    lead = env["crm.lead"].create({"name": "Lead to lock", "type": "lead"})
    res = call(
        env,
        "model_write",
        model="crm.lead",
        record_id=lead.id,
        values={"name": lead.name, "type": "opportunity"},
    )
    assert "error" in res and lead.type == "lead"


def test_conversion_needs_the_party_match_and_keeps_the_source(crm, call):
    env, partner, _pipeline = crm
    lead = env["crm.lead"].create({"name": "Unmatched", "type": "lead", "lead_source": "referral"})
    res = call(
        env,
        "model_action",
        model="crm.lead",
        ids=[lead.id],
        method="action_convert_to_opportunity",
    )
    assert not res.get("success") and "BRU-CRM-02" in json.dumps(res)
    assert lead.type == "lead"
    lead.partner_id = partner
    res = call(
        env,
        "model_action",
        model="crm.lead",
        ids=[lead.id],
        method="action_convert_to_opportunity",
    )
    assert res.get("success"), res
    assert lead.type == "opportunity" and lead.partner_id == partner
    assert lead.lead_source == "referral"


def test_a_cross_sell_saves_as_a_flagged_opportunity(m07, crm, call):
    env, partner, pipeline = crm
    sub = _sub(m07, "9")
    values = _form_values(
        m07,
        "M07-form-opp",
        name="Add UPS AMC to the ATM contract",
        partner_id=partner.id,
        user_id=env.user.id,
        expected_revenue=450000,
        forecast_category="pipeline",
        pipeline_id=pipeline.id,
    )
    values.update(sub["create"]["presets"])
    lead = env["crm.lead"].browse(
        _ok(call(env, "model_write", model="crm.lead", record_id=False, values=values))
    )
    assert lead.type == "opportunity" and lead.is_cross_sell
    assert lead in env["crm.lead"].search(sub["map"]["domain"])


def test_an_activity_is_logged_with_its_reminder(m07, crm, call):
    env, partner, _pipeline = crm
    lead = env["crm.lead"].create({"name": "Visit lead", "type": "lead", "partner_id": partner.id})
    due = datetime.date.today() + datetime.timedelta(days=3)
    rid = _ok(
        call(
            env,
            "model_write",
            model="fix.sales.activity",
            record_id=False,
            values={
                "activity_type": "site_visit",
                "name": "Survey of the Motijheel branch ATMs",
                "occurred_at": "2026-11-13 11:00",
                "owner_id": env.user.id,
                "lead_id": lead.id,
                "outcome": "progressed",
                "next_action": "Send the AMC proposal",
                "next_action_date": str(due),
            },
        )
    )
    act = env["fix.sales.activity"].browse(rid)
    assert act.partner_id == partner and act.subject_type == "lead"
    todo = act.reminder_activity_id
    assert todo and todo.res_model == "crm.lead" and todo.res_id == lead.id
    assert todo.user_id == env.user and todo.date_deadline == due
    assert todo.summary == "Send the AMC proposal"
    # a moved due date replaces the pending reminder, it does not add one
    later = due + datetime.timedelta(days=2)
    _ok(
        call(
            env,
            "model_write",
            model="fix.sales.activity",
            record_id=act.id,
            values={"next_action_date": str(later)},
        )
    )
    assert not todo.exists()
    pending = env["mail.activity"].search(
        [("res_model", "=", "crm.lead"), ("res_id", "=", lead.id)]
    )
    assert pending == act.reminder_activity_id and pending.date_deadline == later


def test_an_activity_must_be_against_something(crm, call):
    env, _partner, _pipeline = crm
    res = call(
        env,
        "model_write",
        model="fix.sales.activity",
        record_id=False,
        values={"activity_type": "call", "name": "Cold call", "owner_id": env.user.id},
    )
    assert "FR-CRM-045" in res.get("error", "")


def test_an_activity_with_an_account_only_reminds_on_the_account(crm, call):
    env, partner, _pipeline = crm
    act = env["fix.sales.activity"].browse(
        _ok(
            call(
                env,
                "model_write",
                model="fix.sales.activity",
                record_id=False,
                values={
                    "activity_type": "meeting",
                    "name": "Courtesy visit",
                    "owner_id": env.user.id,
                    "partner_id": partner.id,
                    "next_action_date": str(datetime.date.today()),
                },
            )
        )
    )
    assert act.subject_type == "account"
    assert act.reminder_activity_id.res_model == "res.partner"


def test_a_forecast_snapshot_is_rolled_up_not_typed(m07, crm, call):
    env, partner, pipeline = crm
    values = {"period": "2099-07", "owner_id": env.user.id, "pipeline_id": pipeline.id}
    refused = call(
        env, "model_write", model="fix.forecast.snapshot", record_id=False, values=values
    )
    assert "no forecast to snapshot" in refused.get("error", "")
    Lead = env["crm.lead"].with_context(default_type="opportunity")
    for name, value, category in (
        ("A", 100000, "commit"),
        ("B", 60000, "best_case"),
        ("C", 40000, "pipeline"),
    ):
        Lead.create(
            {
                "name": "Forecast %s" % name,
                "type": "opportunity",
                "partner_id": partner.id,
                "user_id": env.user.id,
                "pipeline_id": pipeline.id,
                "expected_revenue": value,
                "probability": 50,
                "forecast_category": category,
            }
        )
    # a figure sent by a caller is ignored: the snapshot is taken, never typed
    snap = env["fix.forecast.snapshot"].browse(
        _ok(
            call(
                env,
                "model_write",
                model="fix.forecast.snapshot",
                record_id=False,
                values={**values, "commit_value": 9999999},
            )
        )
    )
    assert (snap.commit_value, snap.best_case_value, snap.pipeline_value) == (
        100000,
        160000,
        200000,
    )
    assert snap.taken_at


def test_a_key_account_saves_with_its_stakeholders(crm, call):
    env, partner, _pipeline = crm
    rid = _ok(
        call(
            env,
            "model_write",
            model="fix.account",
            record_id=False,
            values={"partner_id": partner.id, "tier": "strategic", "industry_vertical": "banking"},
            lines={
                "field": "stakeholder_ids",
                "rows": [
                    {
                        "values": {
                            "name": "Head of ADC",
                            "buying_role": "economic_buyer",
                            "sentiment": "supportive",
                        }
                    },
                    {
                        "values": {
                            "name": "IT Infrastructure Lead",
                            "buying_role": "technical_evaluator",
                        }
                    },
                ],
                "removed": [],
            },
        )
    )
    account = env["fix.account"].browse(rid)
    assert account.tier == "strategic"
    assert set(account.stakeholder_ids.mapped("buying_role")) == {
        "economic_buyer",
        "technical_evaluator",
    }


def test_competitor_intelligence_is_recorded_on_the_picked_opportunity(m07, crm, call):
    env, partner, pipeline = crm
    cfg = m07["screens"]["M07-form-competitor"]
    opp = env["crm.lead"].create(
        {
            "name": "Bank ATM AMC tender",
            "type": "opportunity",
            "partner_id": partner.id,
            "pipeline_id": pipeline.id,
        }
    )
    picked = call(
        env,
        "model_records",
        model="crm.lead",
        cols=cfg["pickRecord"]["cols"],
        domain=cfg["pickRecord"]["domain"],
    )
    assert opp.id in [r["id"] for r in picked["rows"]]
    _ok(
        call(
            env,
            "model_write",
            model="crm.lead",
            record_id=opp.id,
            values={
                "name": opp.name,
                "competitor": "RivalFix BD",
                "competitor_price_bdt": 380000,
                "price_position": "premium",
            },
        )
    )
    assert (opp.competitor, opp.competitor_price_bdt, opp.price_position) == (
        "RivalFix BD",
        380000,
        "premium",
    )
    assert opp in env["crm.lead"].search(_sub(m07, "10")["map"]["domain"])
