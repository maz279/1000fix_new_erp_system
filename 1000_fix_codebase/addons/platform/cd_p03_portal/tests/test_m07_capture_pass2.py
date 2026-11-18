# M07 CRM & Sales Pipeline, capture audit second pass (2026-11-18).
#
# The user again saw M07 pages without a relevant capture. The 13 Nov pass
# (test_m07_submodule_capture.py) gave all ten pages a "+ New", but read
# against the spec five pages still had nowhere to record what a person
# decides, and one "+ New" could never save:
#
#   page 1  the lead qualification assessment (FR-CRM-002, P1): a lead was
#           converted straight from capture; the form's qualification tab
#           held no field at all
#   page 2  the opportunity team (FR-CRM-013, spec entity): not built
#   page 3  the sales quota (FR-CRM-023, spec entity fix.quota): not built
#   page 5  the dedicated-manager criteria (FR-CRM-027 P1, BRU-CRM-09): anyone
#           could pick "Dedicated Manager", with no criteria and no approval
#   page 6  the QBR agreed actions (FR-CRM-037/038): only lines inside each
#           QBR; nothing raised an accepted recommendation as an opportunity
#   page 8  "+ New Contract Renewal Pursuit": the form never sent the
#           required source type, so every save was refused
#
# The page rule is JavaScript (p03_workspace.js fregCreate / fregPanels), so it
# is EXECUTED in node over the real registry; the saves run through the same
# endpoint the forms use, as salespeople and a sales manager, not superuser.
from __future__ import annotations

import datetime
import json
import re
import shutil
import subprocess
from pathlib import Path
from unittest import mock

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api

SRC = Path(__file__).resolve().parents[1] / "static" / "src"
IMPORT = re.compile(r'from\s+"(\./a\d\d/\w+)"')


def _method(name):
    return re.compile(r"^    (" + name + r"\(mid, (?:mod, )?map\) \{\n.*?\n    \})\n", re.S | re.M)


PROBE = """
import * as M from './meta.mjs';
const { P03_MODULES, P03_MODULE_CREATE, P03_FORM_CHIPS, P03_DATA_SCREENS, P03_REPORT_ROUTES } = M;
function %s
function %s
const mod = P03_MODULES.M07;
const subs = mod.freg.sub.map((s) => ({ no: s[0], title: s[1], map: s[3] || null,
  create: fregCreate('M07', s[3] || null), panels: fregPanels('M07', mod, s[3] || null) }));
console.log(JSON.stringify({ subs,
  chips: Object.fromEntries(Object.entries(P03_FORM_CHIPS).filter(([k]) => k.startsWith('M07:'))),
  nav: mod.groups.flatMap((g) => g.screens.map((s) => s.id)),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([k]) => k.startsWith('M07-'))) }));
"""


@pytest.fixture(scope="module")
def m07(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m07_pass2")
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


def _sub(m07, no):
    return next(s for s in m07["subs"] if s["no"] == no)


# --- what each page offers -----------------------------------------------------

# page -> (list screen, chip name, form screen, model)
NEW_CAPTURES = {
    "1": (
        "M07-qualifications",
        "Lead Qualification",
        "M07-form-qualification",
        "fix.lead.qualification",
    ),
    "2": ("M07-opp-team", "Opportunity Team", "M07-form-opp-team", "fix.opportunity.team"),
    "3": ("M07-quotas", "Sales Quota", "M07-form-quota", "fix.sales.quota"),
    "5": (
        "M07-eligibility",
        "Dedicated-Manager Eligibility Criteria",
        "M07-form-eligibility",
        "fix.account.eligibility",
    ),
}


@pytest.mark.parametrize("no", sorted(NEW_CAPTURES, key=int))
def test_the_page_offers_its_new_capture(m07, no):
    """The page lists the record, names its form, and the chip opens the form
    of that record; the list's own + New opens the same form."""
    list_id, chip, form_id, model = NEW_CAPTURES[no]
    sub = _sub(m07, no)
    assert list_id in sub["map"]["screens"], sub["title"]
    assert chip in sub["panels"]["forms"], sub["title"]
    assert m07["chips"]["M07:" + chip] == form_id
    assert m07["chips"]["M07:__by_screen__"][list_id] == form_id
    assert m07["chips"]["M07:__by_model__"][model] == form_id
    form, lst = m07["screens"][form_id], m07["screens"][list_id]
    assert form["kind"] == "model_form" and form["model"] == model
    assert lst["kind"] == "model_list" and lst["model"] == model and lst.get("create") is True
    assert {list_id, form_id} <= set(m07["nav"])
    assert model in api.SURFACES


def test_every_page_still_has_its_own_button(m07):
    assert all(s["create"] for s in m07["subs"]), [
        s["title"] for s in m07["subs"] if not s["create"]
    ]


def test_the_opportunity_form_carries_its_team(m07):
    grids = m07["screens"]["M07-form-opp"].get("grids") or []
    team = next(g for g in grids if g["field"] == "team_member_ids")
    assert {f["name"] for f in team["fields"]} >= {"user_id", "role"}
    assert "team_member_ids" in api.SURFACES["crm.lead"]["writable"]


def test_qbr_actions_are_tracked_on_page_6(m07):
    sub = _sub(m07, "6")
    assert "M07-qbr-actions" in sub["map"]["screens"]
    cfg = m07["screens"]["M07-qbr-actions"]
    assert cfg["model"] == "fix.qbr.action" and cfg.get("create") is False
    methods = {a["m"] for a in cfg["actions"]}
    assert "action_raise_opportunity" in methods
    assert methods <= api.SURFACES["fix.qbr.action"]["actions"]


def test_no_m07_form_leaves_out_a_field_its_model_requires(m07, odoo_env):
    """A required field with no default that the form does not show can
    never be sent: every save of that form is refused. The renewal form
    left out source_type."""
    missing = []
    for sid, cfg in m07["screens"].items():
        if cfg.get("kind") != "model_form" or cfg.get("pickRecord"):
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
                and name not in ("id",)
                and field.type not in ("one2many", "many2many")
            ):
                missing.append("%s.%s" % (sid, name))
    assert not missing, missing


def test_the_renewal_form_offers_source_and_play(m07):
    fields = {
        f["name"]: f for s in m07["screens"]["M07-form-renewal"]["sections"] for f in s["fields"]
    }
    assert fields["source_type"].get("required") and not fields["source_type"].get("readonly")
    assert "play" in fields and not fields["play"].get("readonly")
    assert {"source_type", "play"} <= set(api.SURFACES["fix.renewal"]["writable"])


def test_the_lead_form_shows_its_qualification(m07):
    fields = [f["name"] for s in m07["screens"]["M07-form-lead"]["sections"] for f in s["fields"]]
    assert "qualification_state" in fields
    assert "qualification_state" not in api.SURFACES["crm.lead"]["writable"]


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


def _user(env, login, *groups):
    ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    return (
        env["res.users"]
        .with_context(no_reset_password=True, mail_create_nosubscribe=True)
        .create(
            {
                "name": login,
                "login": "%s@example.invalid" % login,
                "email": "%s@example.invalid" % login,
                "group_ids": [(6, 0, ids)],
            }
        )
    )


@pytest.fixture
def crm(odoo_env):
    env = odoo_env
    seller = _user(env, "m07p2.seller", "sales_team.group_sale_salesman")
    other = _user(env, "m07p2.other", "sales_team.group_sale_salesman")
    manager = _user(env, "m07p2.manager", "sales_team.group_sale_manager")
    partner = env["res.partner"].create({"name": "M07P2 Bank Ltd", "is_company": True})
    return {
        "env": env,
        "seller": seller,
        "other": other,
        "manager": manager,
        "partner": partner,
        "pipeline": env.ref("cd_crm_ext.pipeline_standard"),
    }


def _ok(res):
    assert "error" not in res, res
    return res["id"]


def _refused(res, *words):
    assert "error" in res or res.get("success") is False, res
    text = json.dumps(res)
    for word in words:
        assert word in text, (word, res)


def _write(call, env, model, values, record_id=False):
    return call(env, "model_write", model=model, record_id=record_id, values=values)


BANT_OK = {"need": "confirmed", "authority": "partial", "budget": "partial", "timing": "confirmed"}


# page 1 ------------------------------------------------------------------------
def test_a_lead_is_qualified_then_converted(crm, call):
    env = crm["env"](user=crm["seller"])
    lead = env["crm.lead"].create(
        {"name": "ATM fleet AMC", "type": "lead", "partner_id": crm["partner"].id}
    )
    res = call(
        env, "model_action", model="crm.lead", ids=[lead.id], method="action_convert_to_opportunity"
    )
    _refused(res, "Qualify")
    assert lead.type == "lead"
    rid = _ok(
        _write(
            call, env, "fix.lead.qualification", dict(BANT_OK, lead_id=lead.id, outcome="qualified")
        )
    )
    rec = env["fix.lead.qualification"].browse(rid)
    assert lead.qualification_state == "qualified" and rec.assessed_by == crm["seller"]
    res = call(
        env, "model_action", model="crm.lead", ids=[lead.id], method="action_convert_to_opportunity"
    )
    assert res.get("success"), res
    assert lead.type == "opportunity"


def test_qualified_needs_a_confirmed_need_and_no_unknowns(crm, call):
    env = crm["env"](user=crm["seller"])
    lead = env["crm.lead"].create({"name": "Vague enquiry", "type": "lead"})
    weak = dict(BANT_OK, need="partial", lead_id=lead.id, outcome="qualified")
    _refused(_write(call, env, "fix.lead.qualification", weak), "confirmed need")
    weak = dict(BANT_OK, budget="unknown", lead_id=lead.id, outcome="qualified")
    _refused(_write(call, env, "fix.lead.qualification", weak), "budget")
    assert lead.qualification_state == "captured"


def test_disqualified_needs_a_reason_and_closes_the_lead(crm, call):
    env = crm["env"](user=crm["seller"])
    lead = env["crm.lead"].create({"name": "No budget walk-in", "type": "lead"})
    vals = dict(BANT_OK, budget="unknown", lead_id=lead.id, outcome="disqualified")
    _refused(_write(call, env, "fix.lead.qualification", vals), "why")
    _refused(
        _write(call, env, "fix.lead.qualification", dict(vals, disqualify_reason="other")),
        "Other",
    )
    _ok(_write(call, env, "fix.lead.qualification", dict(vals, disqualify_reason="no_budget")))
    assert lead.qualification_state == "disqualified" and not lead.active
    # a closed lead is not assessed again
    _refused(
        _write(
            call, env, "fix.lead.qualification", dict(BANT_OK, lead_id=lead.id, outcome="qualified")
        )
    )


def test_not_ready_returns_the_lead_to_nurture(crm, call):
    env = crm["env"](user=crm["seller"])
    lead = env["crm.lead"].create({"name": "Next year's refresh", "type": "lead"})
    vals = dict(
        BANT_OK, timing="unknown", lead_id=lead.id, outcome="nurture", notes="Budget cycle in July"
    )
    _ok(_write(call, env, "fix.lead.qualification", vals))
    assert lead.qualification_state == "recycled" and not lead.active


def test_an_assessment_is_never_edited_and_the_state_never_typed(crm, call):
    env = crm["env"](user=crm["seller"])
    lead = env["crm.lead"].create({"name": "Typed state", "type": "lead"})
    rid = _ok(
        _write(
            call, env, "fix.lead.qualification", dict(BANT_OK, lead_id=lead.id, outcome="qualified")
        )
    )
    _refused(
        _write(call, env, "fix.lead.qualification", {"outcome": "disqualified"}, record_id=rid)
    )
    other = env["crm.lead"].create({"name": "Self-qualified", "type": "lead"})
    with pytest.raises(Exception, match="cannot be set directly"):
        other.write({"qualification_state": "qualified"})
    with pytest.raises(Exception, match="cannot be set directly"):
        env["crm.lead"].create(
            {"name": "Born qualified", "type": "lead", "qualification_state": "qualified"}
        )


def test_an_opportunity_is_not_qualified_as_a_lead(crm, call):
    env = crm["env"](user=crm["seller"])
    opp = env["crm.lead"].create(
        {"name": "Already an opp", "type": "opportunity", "partner_id": crm["partner"].id}
    )
    _refused(
        _write(
            call, env, "fix.lead.qualification", dict(BANT_OK, lead_id=opp.id, outcome="qualified")
        ),
        "already an opportunity",
    )


# page 2 ------------------------------------------------------------------------
def _opp(crm, owner):
    return crm["env"](user=owner)["crm.lead"].create(
        {
            "name": "Managed print, 40 sites",
            "type": "opportunity",
            "partner_id": crm["partner"].id,
            "user_id": owner.id,
            "pipeline_id": crm["pipeline"].id,
        }
    )


def test_the_owner_builds_the_opportunity_team(crm, call):
    opp = _opp(crm, crm["seller"])
    env = crm["env"](user=crm["seller"])
    rid = _ok(
        _write(
            call,
            env,
            "fix.opportunity.team",
            {"lead_id": opp.id, "user_id": crm["other"].id, "role": "technical"},
        )
    )
    assert opp.team_member_ids.ids == [rid]
    # the owner is not their own team member; one person once
    _refused(
        _write(
            call,
            env,
            "fix.opportunity.team",
            {"lead_id": opp.id, "user_id": crm["seller"].id, "role": "commercial"},
        ),
        "already owns",
    )
    # the unique constraint, raised by the database
    with pytest.raises(Exception), env.cr.savepoint():  # noqa: B017
        env["fix.opportunity.team"].create(
            {"lead_id": opp.id, "user_id": crm["other"].id, "role": "presales"}
        )


def test_only_the_owner_or_a_manager_changes_the_team(crm, call):
    opp = _opp(crm, crm["seller"])
    intruder = crm["env"](user=crm["other"])
    _refused(
        _write(
            call,
            intruder,
            "fix.opportunity.team",
            {"lead_id": opp.id, "user_id": crm["other"].id, "role": "presales"},
        ),
        "owner",
    )
    boss = crm["env"](user=crm["manager"])
    _ok(
        _write(
            call,
            boss,
            "fix.opportunity.team",
            {"lead_id": opp.id, "user_id": crm["other"].id, "role": "executive_sponsor"},
        )
    )
    _refused(
        _write(
            call,
            boss,
            "fix.opportunity.team",
            {"lead_id": opp.id, "user_id": crm["manager"].id, "role": "executive_sponsor"},
        ),
        "one executive sponsor",
    )


def test_a_lead_has_no_pursuit_team(crm, call):
    env = crm["env"](user=crm["seller"])
    lead = env["crm.lead"].create(
        {"name": "Still a lead", "type": "lead", "user_id": crm["seller"].id}
    )
    _refused(
        _write(
            call,
            env,
            "fix.opportunity.team",
            {"lead_id": lead.id, "user_id": crm["other"].id, "role": "technical"},
        ),
        "is a lead",
    )


# page 3 ------------------------------------------------------------------------
def _won_stage(env):
    stage = env["crm.stage"].search([("is_won", "=", True)], limit=1)
    return stage or env["crm.stage"].create({"name": "Won (test)", "is_won": True})


def test_a_manager_sets_a_quota_and_attainment_counts_won_deals(crm, call):
    env = crm["env"]
    opp = _opp(crm, crm["seller"])
    opp.sudo().write({"expected_revenue": 400000.0})
    stage = _won_stage(env)
    # flush first: a pending stage recompute would overwrite the raw update
    env.flush_all()
    env.cr.execute(
        "UPDATE crm_lead SET stage_id=%s, date_closed=%s, probability=100 WHERE id=%s",
        (stage.id, datetime.datetime(2026, 11, 10, 6, 0), opp.id),
    )
    env.invalidate_all()
    boss = env(user=crm["manager"])
    rid = _ok(
        _write(
            call,
            boss,
            "fix.sales.quota",
            {"owner_id": crm["seller"].id, "period": "2026-Q4", "target_value": 1000000.0},
        )
    )
    quota = boss["fix.sales.quota"].browse(rid)
    assert quota.won_count == 1 and quota.achieved_value == 400000.0
    assert quota.attainment_pct == 40.0 and quota.set_by == crm["manager"]
    # one quota per seller, period and pipeline
    _refused(
        _write(
            call,
            boss,
            "fix.sales.quota",
            {"owner_id": crm["seller"].id, "period": "2026-Q4", "target_value": 5.0},
        ),
        "already has a quota",
    )


def test_a_seller_never_sets_a_quota(crm, call):
    seller = crm["env"](user=crm["seller"])
    _refused(
        _write(
            call,
            seller,
            "fix.sales.quota",
            {"owner_id": crm["other"].id, "period": "2026", "target_value": 9.0},
        )
    )
    boss = crm["env"](user=crm["manager"])
    _refused(
        _write(
            call,
            boss,
            "fix.sales.quota",
            {"owner_id": crm["manager"].id, "period": "2026", "target_value": 9.0},
        ),
        "own quota",
    )
    _refused(
        _write(
            call,
            boss,
            "fix.sales.quota",
            {"owner_id": crm["seller"].id, "period": "Q4 2026", "target_value": 9.0},
        ),
        "2026-Q4",
    )
    _refused(
        _write(
            call,
            boss,
            "fix.sales.quota",
            {"owner_id": crm["seller"].id, "period": "2026-11", "target_value": 0.0},
        ),
        "above zero",
    )


# page 5 ------------------------------------------------------------------------
def _key_account(env, partner, tier):
    return env["fix.account"].create(
        {
            "partner_id": partner.id,
            "tier": tier,
            "industry_vertical": env["fix.account"]._fields["industry_vertical"].selection[0][0],
        }
    )


def test_only_a_manager_publishes_criteria_and_new_ones_supersede(crm, call):
    seller = crm["env"](user=crm["seller"])
    _refused(
        _write(
            call, seller, "fix.account.eligibility", {"name": "Mine", "strategic_qualifies": True}
        )
    )
    boss = crm["env"](user=crm["manager"])
    first = _ok(
        _write(call, boss, "fix.account.eligibility", {"name": "FY26", "strategic_qualifies": True})
    )
    second = _ok(
        _write(call, boss, "fix.account.eligibility", {"name": "FY27", "min_acv_bdt": 2000000.0})
    )
    Crit = boss["fix.account.eligibility"].with_context(active_test=False)
    assert not Crit.browse(first).active and Crit.browse(second).active
    _refused(
        _write(
            call, boss, "fix.account.eligibility", {"name": "Nothing", "strategic_qualifies": False}
        ),
        "at least one criterion",
    )


def test_a_dedicated_manager_follows_the_criteria(crm, call):
    env = crm["env"]
    env["fix.account.eligibility"].with_user(crm["manager"]).create(
        {"name": "FY27", "strategic_qualifies": True}
    )
    strategic = env["res.partner"].create({"name": "Strategic Telco", "is_company": True})
    _key_account(env, strategic, "strategic")
    small = env["res.partner"].create({"name": "Small Shop", "is_company": True})
    _key_account(env, small, "growth")
    seller = env(user=crm["seller"])
    rid = _ok(
        _write(
            call,
            seller,
            "fix.account.assignment",
            {
                "partner_id": strategic.id,
                "owner_id": crm["seller"].id,
                "assignment_type": "dedicated",
                "effective_from": "2026-11-18",
            },
        )
    )
    asg = seller["fix.account.assignment"].browse(rid)
    assert (
        asg.eligibility_basis.startswith("Eligible on strategic tier")
        and not asg.exception_approved_by
    )
    # outside the criteria: a seller is refused, with or without a reason
    vals = {
        "partner_id": small.id,
        "owner_id": crm["seller"].id,
        "assignment_type": "dedicated",
        "effective_from": "2026-11-18",
    }
    _refused(_write(call, seller, "fix.account.assignment", vals), "exception reason")
    _refused(
        _write(call, seller, "fix.account.assignment", dict(vals, exception_reason="Board asked")),
        "BRU-CRM-09",
    )
    # a sales manager approves the exception, and it is stamped
    boss = env(user=crm["manager"])
    rid = _ok(
        _write(call, boss, "fix.account.assignment", dict(vals, exception_reason="Board asked"))
    )
    asg = boss["fix.account.assignment"].browse(rid)
    assert asg.exception_approved_by == crm["manager"] and asg.eligibility_basis.startswith("Below")
    # the stamps are never typed
    asg.with_user(crm["seller"]).write({"exception_approved_by": crm["seller"].id})
    assert asg.exception_approved_by == crm["manager"]


def test_a_named_account_needs_no_criteria(crm, call):
    seller = crm["env"](user=crm["seller"])
    _ok(
        _write(
            call,
            seller,
            "fix.account.assignment",
            {
                "partner_id": crm["partner"].id,
                "owner_id": crm["seller"].id,
                "assignment_type": "account",
                "effective_from": "2026-11-18",
            },
        )
    )


# page 6 ------------------------------------------------------------------------
def test_an_accepted_recommendation_becomes_an_opportunity_once(crm, call):
    env = crm["env"](user=crm["seller"])
    qbr = env["fix.qbr"].create(
        {
            "partner_id": crm["partner"].id,
            "period": "2026-Q4",
            "scheduled_for": "2026-11-15",
            "action_ids": [
                (
                    0,
                    0,
                    {
                        "description": "Add UPS AMC for 12 branches",
                        "owner_internal": crm["seller"].id,
                    },
                )
            ],
        }
    )
    action = qbr.action_ids
    res = call(
        env,
        "model_action",
        model="fix.qbr.action",
        ids=[action.id],
        method="action_raise_opportunity",
    )
    _refused(res, "held")
    qbr.write(
        {"attendees": "CFO, KAM", "decisions": "Extend to UPS", "document_ref": "QBR-2026-Q4.pdf"}
    )
    qbr.action_mark_held()
    res = call(
        env,
        "model_action",
        model="fix.qbr.action",
        ids=[action.id],
        method="action_raise_opportunity",
    )
    assert res.get("success"), res
    opp = action.opportunity_id
    assert opp.type == "opportunity" and opp.partner_id == crm["partner"]
    assert opp.lead_source == "qbr" and opp.is_cross_sell and opp.user_id == crm["seller"]
    res = call(
        env,
        "model_action",
        model="fix.qbr.action",
        ids=[action.id],
        method="action_raise_opportunity",
    )
    _refused(res, "already raised")


# page 8 ------------------------------------------------------------------------
def test_new_renewal_pursuit_saves(crm, call):
    env = crm["env"](user=crm["seller"])
    rid = _ok(
        _write(
            call,
            env,
            "fix.renewal",
            {
                "partner_id": crm["partner"].id,
                "source_type": "contract",
                "source_ref": "AMC-2025-114",
                "expiry_date": "2027-02-01",
                "value": 850000.0,
                "play": "executive",
            },
        )
    )
    renewal = env["fix.renewal"].browse(rid)
    assert renewal.state == "open" and renewal.play == "executive"
